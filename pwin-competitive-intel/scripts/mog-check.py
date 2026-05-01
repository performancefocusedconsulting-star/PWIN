#!/usr/bin/env python3
"""
Monthly GOV.UK machinery-of-government (MoG) change detector.

Fetches the full GOV.UK organisations list, diffs against the stored snapshot,
files a GitHub issue for any changes, opens a PR with the updated snapshot,
and drafts/sends a summary email via the Gmail API.

Run from the repo root:
    python pwin-competitive-intel/scripts/mog-check.py

Requirements:
- Unrestricted outbound HTTPS to www.gov.uk
- gh CLI authenticated (for GitHub operations)
- Optional: GMAIL_TOKEN env var or gcloud ADC for email (falls back to draft)

Exit codes:
  0  success (seeded, changed, or unchanged)
  1  GOV.UK API fetch failed after retry
"""
import sys
import os
import json
import time
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_PATH = REPO_ROOT / "pwin-competitive-intel" / "snapshots" / "govuk-orgs.json"
GOVUK_API_BASE = "https://www.gov.uk/api/organisations"
NOTIFY_EMAIL = "pfenton@me.com"
GITHUB_REPO = "performancefocusedconsulting-star/PWIN"

# Change-signal priority (highest first) for email bullet ordering
PRIORITY = ["Closed", "Superseded", "Reparented", "Format changed", "Renamed", "Added"]


# ── GOV.UK fetch ─────────────────────────────────────────────────────────────
def fetch_page(url: str) -> dict:
    """Fetch one page; retry once on 5xx or timeout, abort on 4xx."""
    headers = {
        "Accept": "application/json",
        "User-Agent": "PWIN-MoG-Monitor/1.0 (+https://github.com/performancefocusedconsulting-star/PWIN)",
    }
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status >= 500:
                    raise Exception(f"Server error {resp.status}")
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt == 0:
                print(f"  5xx on attempt 1, retrying in 10s…", file=sys.stderr)
                time.sleep(10)
                continue
            sys.exit(f"ABORT: GOV.UK API returned HTTP {e.code} — {e.reason}")
        except Exception as e:
            if attempt == 0:
                print(f"  Error on attempt 1 ({e}), retrying in 10s…", file=sys.stderr)
                time.sleep(10)
                continue
            sys.exit(f"ABORT: GOV.UK API failed after retry — {e}")
    sys.exit("ABORT: GOV.UK API fetch failed after retry")


def fetch_all_orgs() -> list:
    url = f"{GOVUK_API_BASE}?page=1"
    all_orgs = []
    page_num = 0
    while url:
        page_num += 1
        print(f"  Page {page_num}: {url}", file=sys.stderr)
        data = fetch_page(url)
        all_orgs.extend(data.get("results", []))
        url = data.get("next_page_url") or data.get("links", {}).get("next")
        if url:
            time.sleep(0.5)
    print(f"  Total raw orgs: {len(all_orgs)}", file=sys.stderr)
    return all_orgs


def normalise(raw_orgs: list) -> list:
    def slug_from(org):
        s = org.get("details", {}).get("slug")
        if s:
            return s
        href = org.get("id", "")
        return href.rstrip("/").split("/")[-1]

    snapshot = []
    for org in raw_orgs:
        slug = slug_from(org)
        parents  = sorted(p.get("id","").rstrip("/").split("/")[-1] for p in org.get("parent_organisations", []))
        children = sorted(c.get("id","").rstrip("/").split("/")[-1] for c in org.get("child_organisations", []))
        superseded = sorted(s.get("id","").rstrip("/").split("/")[-1] for s in org.get("superseded_by", []))
        snapshot.append({
            "slug": slug,
            "title": org.get("title", ""),
            "format": org.get("format", ""),
            "govuk_status": org.get("details", {}).get("govuk_status", ""),
            "closed_at": org.get("details", {}).get("closed_at"),
            "parent_organisations": parents,
            "child_organisations": children,
            "superseded_by": superseded,
        })
    snapshot.sort(key=lambda x: x["slug"])
    return snapshot


# ── Diff ─────────────────────────────────────────────────────────────────────
def diff_snapshots(old: list, new: list) -> dict:
    """Return classified changes, excluding Sub organisation format entries."""
    old_by_slug = {e["slug"]: e for e in old}
    new_by_slug = {e["slug"]: e for e in new}

    changes = {k: [] for k in PRIORITY}

    for slug, new_e in new_by_slug.items():
        if new_e.get("format") == "Sub organisation":
            continue
        if slug not in old_by_slug:
            changes["Added"].append({"slug": slug, "title": new_e["title"],
                                     "format": new_e["format"], "status": new_e["govuk_status"]})
            continue
        old_e = old_by_slug[slug]
        if old_e.get("format") == "Sub organisation":
            continue
        if (new_e.get("govuk_status") == "closed" and old_e.get("govuk_status") != "closed") or \
           (new_e.get("closed_at") and not old_e.get("closed_at")):
            changes["Closed"].append({"slug": slug, "title": new_e["title"],
                                      "old_status": old_e["govuk_status"],
                                      "closed_at": new_e.get("closed_at")})
        if new_e.get("superseded_by") != old_e.get("superseded_by"):
            added_superseded = [s for s in new_e.get("superseded_by", [])
                                if s not in old_e.get("superseded_by", [])]
            if added_superseded:
                changes["Superseded"].append({"slug": slug, "title": new_e["title"],
                                              "superseded_by": added_superseded})
        if new_e["parent_organisations"] != old_e["parent_organisations"]:
            changes["Reparented"].append({"slug": slug, "title": new_e["title"],
                                          "old_parents": old_e["parent_organisations"],
                                          "new_parents": new_e["parent_organisations"]})
        if new_e["format"] != old_e["format"]:
            changes["Format changed"].append({"slug": slug, "title": new_e["title"],
                                              "old": old_e["format"], "new": new_e["format"]})
        if new_e["title"] != old_e["title"]:
            changes["Renamed"].append({"slug": slug,
                                       "old_title": old_e["title"], "new_title": new_e["title"]})

    return changes


def total_changes(changes: dict) -> int:
    return sum(len(v) for v in changes.values())


# ── GitHub via gh CLI ─────────────────────────────────────────────────────────
def gh(args: list, input_text: str = None) -> str:
    """Run gh CLI, return stdout. Raises on non-zero."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True,
        input=input_text
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def create_pr_branch(branch: str) -> None:
    subprocess.run(["git", "checkout", "-b", branch], check=True)


def commit_snapshot(branch: str, message: str) -> None:
    subprocess.run(["git", "add", str(SNAPSHOT_PATH)], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "-u", "origin", branch], check=True)


def open_issue(title: str, body: str) -> str:
    """Open GitHub issue, return URL."""
    url = gh(["issue", "create",
               "--repo", GITHUB_REPO,
               "--title", title,
               "--body", body,
               "--assignee", "performancefocusedconsulting-star"])
    return url.strip()


def open_pr(branch: str, title: str, body: str) -> str:
    """Open PR, return URL."""
    url = gh(["pr", "create",
               "--repo", GITHUB_REPO,
               "--base", "main",
               "--head", branch,
               "--title", title,
               "--body", body])
    return url.strip()


# ── Issue / PR body builders ──────────────────────────────────────────────────
def build_issue_body(changes: dict) -> str:
    lines = [f"Detected on {TODAY}. Changes affecting non-Sub-organisation entities only.\n"]
    for cat in PRIORITY:
        entries = changes[cat]
        lines.append(f"## {cat} ({len(entries)})")
        if not entries:
            lines.append("_None_")
        elif cat == "Added":
            for e in entries:
                lines.append(f"- `{e['slug']}` — {e['title']} ({e['format']}, {e['status']})")
        elif cat == "Closed":
            for e in entries:
                lines.append(f"- `{e['slug']}` — {e['title']} (was `{e['old_status']}`, closed_at: {e.get('closed_at','?')})")
        elif cat == "Renamed":
            for e in entries:
                lines.append(f"- `{e['slug']}` — \"{e['old_title']}\" → \"{e['new_title']}\"")
        elif cat == "Reparented":
            for e in entries:
                old = ", ".join(e['old_parents']) or "_none_"
                new = ", ".join(e['new_parents']) or "_none_"
                lines.append(f"- `{e['slug']}` — {e['title']} | parents: `{old}` → `{new}`")
        elif cat == "Superseded":
            for e in entries:
                lines.append(f"- `{e['slug']}` — {e['title']}, superseded_by: {e['superseded_by']}")
        elif cat == "Format changed":
            for e in entries:
                lines.append(f"- `{e['slug']}` — {e['title']}: `{e['old']}` → `{e['new']}`")
        lines.append("")

    lines += [
        "## Next steps",
        "Re-run the local glossary build and wiki regeneration:",
        "```",
        "python pwin-platform/scripts/seed-canonical-buyers.py",
        "python pwin-competitive-intel/agent/generate-buyer-wiki.py",
        "```",
    ]
    return "\n".join(lines)


def build_seed_pr_body() -> str:
    return (
        f"## GOV.UK organisations baseline snapshot — {TODAY}\n\n"
        "This PR seeds the initial `pwin-competitive-intel/snapshots/govuk-orgs.json` file. "
        "Future monthly runs will diff against this baseline to detect machinery-of-government (MoG) changes — "
        "departments and arm's-length bodies being created, closed, renamed, reparented, or restructured.\n\n"
        "No issue is opened on a seed run; the first diff run will detect any changes from this point.\n\n"
        "Generated by `pwin-competitive-intel/scripts/mog-check.py`."
    )


def build_update_pr_body(n: int, issue_url: str = None) -> str:
    lines = [
        f"## GOV.UK organisations snapshot update — {TODAY}",
        "",
        f"Updates `pwin-competitive-intel/snapshots/govuk-orgs.json` with {n} classified change(s).",
        "",
    ]
    if issue_url:
        lines += [f"Linked issue: {issue_url}", ""]
    lines += [
        "Generated by `pwin-competitive-intel/scripts/mog-check.py`.",
    ]
    return "\n".join(lines)


# ── Email via Gmail MCP (subprocess shim — replace with direct MCP call) ──────
def build_email_body(changes: dict | None, pr_url: str, issue_url: str | None, is_seed: bool) -> str:
    footer = (
        "\n\nTo rebuild locally:\n"
        "  python pwin-platform/scripts/seed-canonical-buyers.py\n"
        "  python pwin-competitive-intel/agent/generate-buyer-wiki.py"
    )
    if is_seed:
        return (
            f"Initial GOV.UK organisations snapshot seeded on {TODAY}.\n\n"
            f"Snapshot PR: {pr_url}"
            + footer
        )
    counts = {k: len(v) for k, v in changes.items()}
    summary = ", ".join(f"{v} {k.lower()}" for k, v in counts.items())
    bullets = []
    for cat in PRIORITY:
        for e in changes[cat][:4]:
            if cat == "Added":
                bullets.append(f"• [Added] {e['title']} ({e['slug']})")
            elif cat == "Closed":
                bullets.append(f"• [Closed] {e['title']} ({e['slug']})")
            elif cat == "Renamed":
                bullets.append(f"• [Renamed] {e['old_title']} → {e['new_title']} ({e['slug']})")
            elif cat == "Reparented":
                bullets.append(f"• [Reparented] {e['title']} ({e['slug']})")
            elif cat == "Superseded":
                bullets.append(f"• [Superseded] {e['title']} ({e['slug']})")
            elif cat == "Format changed":
                bullets.append(f"• [Format] {e['title']}: {e['old']} → {e['new']} ({e['slug']})")
        if len(bullets) >= 20:
            break
    body_parts = [summary, ""]
    if bullets:
        body_parts += bullets + [""]
    if issue_url:
        body_parts.append(f"GitHub issue: {issue_url}")
    body_parts.append(f"Snapshot PR: {pr_url}")
    body_parts.append(footer)
    return "\n".join(body_parts)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print(f"=== PWIN MoG Check {TODAY} ===", file=sys.stderr)

    # 1. Fetch
    print("Fetching GOV.UK organisations…", file=sys.stderr)
    raw = fetch_all_orgs()
    new_snapshot = normalise(raw)
    print(f"Normalised: {len(new_snapshot)} entries", file=sys.stderr)

    is_seed = not SNAPSHOT_PATH.exists()
    changed = True  # assume changed; override below

    if is_seed:
        print("No existing snapshot — SEED run.", file=sys.stderr)
    else:
        old_snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        old_json = json.dumps(old_snapshot, sort_keys=True)
        new_json = json.dumps(new_snapshot, sort_keys=True)
        if old_json == new_json:
            print("Snapshot unchanged — nothing to do.", file=sys.stderr)
            print(f"unchanged")
            return
        changes = diff_snapshots(old_snapshot, new_snapshot)
        n = total_changes(changes)
        print(f"Changes detected: {n}", file=sys.stderr)

    # 2. Write snapshot
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(
        json.dumps(new_snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    # 3. Git branch + commit + push
    if is_seed:
        branch = f"chore/seed-govuk-snapshot-{TODAY}"
        pr_title = "Seed GOV.UK organisations snapshot for MoG-change detection"
        commit_msg = "chore: seed GOV.UK organisations snapshot"
    else:
        branch = f"chore/update-govuk-snapshot-{TODAY}"
        pr_title = f"MoG changes detected {TODAY} ({n} changes)"
        commit_msg = f"chore: update GOV.UK organisations snapshot {TODAY}"

    create_pr_branch(branch)
    commit_snapshot(branch, commit_msg)

    # 4. GitHub issue (non-seed only)
    issue_url = None
    if not is_seed and n > 0:
        issue_title = f"MoG changes detected {TODAY} ({n} changes)"
        issue_body = build_issue_body(changes)
        issue_url = open_issue(issue_title, issue_body)
        print(f"Issue: {issue_url}", file=sys.stderr)

    # 5. PR
    if is_seed:
        pr_body = build_seed_pr_body()
    else:
        pr_body = build_update_pr_body(n, issue_url)
    pr_url = open_pr(branch, pr_title, pr_body)
    print(f"PR: {pr_url}", file=sys.stderr)

    # 6. Summary line
    if is_seed:
        print(f"seeded | PR: {pr_url} | issue: none | email: see Gmail MCP call below")
    else:
        counts = {k: len(v) for k, v in changes.items()}
        counts_str = " ".join(f"{k.lower().replace(' ','_')}={v}" for k, v in counts.items())
        print(f"{n} changes ({counts_str}) | PR: {pr_url} | issue: {issue_url}")

    # Email is handled by the caller (Claude) via Gmail MCP tools
    print("EMAIL_SUBJECT:" + (
        f"GOV.UK organisations snapshot seeded {TODAY}" if is_seed
        else f"MoG changes detected {TODAY} ({n} changes)"
    ))
    print("EMAIL_BODY_START")
    if is_seed:
        print(build_email_body(None, pr_url, None, True))
    else:
        print(build_email_body(changes, pr_url, issue_url, False))
    print("EMAIL_BODY_END")


if __name__ == "__main__":
    main()
