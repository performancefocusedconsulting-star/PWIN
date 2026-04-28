#!/usr/bin/env python3
"""
PWIN — Daily pipeline scan orchestrator
========================================
Invokes the platform `daily-pipeline-scan` skill (via the Node CLI),
parses the JSON output, and does the actual writes:

  1. Obsidian pursuit files (one per BOOK / QUALIFY item) — frontmatter
     matches the watcher.py schema so flipping `status: action_required`
     immediately triggers the action handlers.
  2. wiki/pursuits/_index.md — appends new pipeline rows.
  3. crm.db opportunities — upserts each BOOK/QUALIFY/INTEL row.
  4. ~/.pwin/digests/{date}.md — saves the digest text. Email send is
     a separate concern (Gmail token reconnect).

Idempotency: every step checks for existing rows / files by ref. Re-running
the same scan does not duplicate. The skill is also told the existing
pipeline so it doesn't re-action duplicates.

Usage:
    python agent/run-pipeline-scan.py                     # standard nightly
    python agent/run-pipeline-scan.py --hours 24
    python agent/run-pipeline-scan.py --dry-run           # no writes
    python agent/run-pipeline-scan.py --skip-skill --json result.json
        # parse a previously-saved skill result (debug)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import smtplib
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT      = Path(__file__).parent.parent.parent
PLATFORM_DIR   = REPO_ROOT / "pwin-platform"
RUN_SKILL_JS   = PLATFORM_DIR / "bin" / "run-skill.js"

PURSUITS_DIR   = Path("C:/Users/User/Documents/Obsidian Vault/wiki/pursuits")
PURSUITS_INDEX = PURSUITS_DIR / "_index.md"

CRM_DB         = Path.home() / ".pwin" / "crm.db"
DIGESTS_DIR    = Path.home() / ".pwin" / "digests"

log = logging.getLogger("pipeline-scan")


# ══════════════════════════════════════════════════════════════════════════════
# 1 — Skill invocation
# ══════════════════════════════════════════════════════════════════════════════

def run_skill(hours: int = 24, dry_run: bool = False) -> dict[str, Any]:
    """Call the Node CLI to execute the daily-pipeline-scan skill."""
    cmd = ["node", str(RUN_SKILL_JS), "daily-pipeline-scan",
           "--lookbackHours", str(hours)]
    if dry_run:
        cmd.append("--dry-run")
    log.info("invoking skill: %s", " ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    # Tolerate non-zero exit IF stdout is parseable JSON. On Windows we
    # sometimes see a libuv cleanup assertion fire AFTER the skill has
    # successfully written its result — the data is good, the exit code is not.
    try:
        parsed = json.loads(result.stdout)
        if result.returncode != 0:
            log.warning(
                "skill runner exit=%d but stdout parsed cleanly — proceeding "
                "(treating as a Node cleanup-time fault). stderr first line: %s",
                result.returncode,
                (result.stderr or "").splitlines()[0] if result.stderr else "",
            )
        # The skill-runner short-circuits to a `{dryRun: true, ...}` shape when
        # ANTHROPIC_API_KEY is missing. We did not ask for that here, so treat
        # it as a hard failure with a clear message rather than letting the
        # caller fall through to "could not extract triage JSON".
        if not dry_run and parsed.get("dryRun") is True:
            raise RuntimeError(
                "Skill returned dry-run shape (no `text` field) — "
                "ANTHROPIC_API_KEY is not visible to the Node child process. "
                "Set it for your user (setx ANTHROPIC_API_KEY ...) and reopen "
                "the shell, or export it in the calling environment."
            )
        return parsed
    except json.JSONDecodeError as e:
        if result.returncode != 0:
            log.error("skill runner failed (exit %d):\n%s", result.returncode, result.stderr)
            raise RuntimeError(f"Skill runner failed: {result.stderr}")
        log.error("could not parse skill stdout as JSON: %s", e)
        log.error("stdout (first 500 chars): %s", result.stdout[:500])
        raise


def extract_triage_json(skill_result: dict[str, Any]) -> dict[str, Any] | None:
    """The skill prompts Claude to produce a JSON object with `meta`, `triage`,
    `digest`. Claude's response comes back in the `text` field. Find and parse
    the JSON object embedded in the text. Returns None if no JSON found."""
    text = skill_result.get("text") or ""
    if not text:
        return None
    # Find the largest top-level JSON object that contains "triage"
    # We look for { ... "triage" ... } with balanced braces.
    candidates = []
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                candidates.append(text[start:i + 1])
                start = -1
    for cand in sorted(candidates, key=len, reverse=True):
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict) and "triage" in obj:
                return obj
        except json.JSONDecodeError:
            continue
    return None


# ══════════════════════════════════════════════════════════════════════════════
# 2 — Obsidian pursuit file writer
# ══════════════════════════════════════════════════════════════════════════════

PURSUIT_FRONTMATTER_KEYS = [
    "ref", "status", "action_type", "close_reason", "priority", "buyer",
    "value", "notice_type", "notice_url", "published",
    "registration_deadline", "session_date", "tender_expected",
    "submission_deadline", "contract_start", "contract_end", "processed_at",
]


def slugify(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80]


def fmt_yaml_value(v: Any) -> str:
    if v is None or v == "":
        return "~"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if re.search(r":\s", s) or s.startswith(("[", "{", "!", "&", "*", ">", "|", "%")):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def render_pursuit_file(item: dict[str, Any], notice_type_default: str) -> str:
    fm = {
        "ref":                   item.get("ref"),
        "status":                "new",
        "action_type":           None,
        "close_reason":          None,
        "priority":              item.get("priority", "medium"),
        "buyer":                 item.get("buyer"),
        "value":                 item.get("value"),
        "notice_type":           item.get("noticeType") or notice_type_default,
        "notice_url":            item.get("noticeUrl"),
        "published":             item.get("publishedDate"),
        "registration_deadline": item.get("registrationDeadline"),
        "session_date":          item.get("sessionDate"),
        "tender_expected":       item.get("tenderExpected"),
        "submission_deadline":   item.get("tenderDeadline") or item.get("submissionDeadline"),
        "contract_start":        item.get("contractStart"),
        "contract_end":          item.get("contractEnd"),
        "processed_at":          None,
    }

    lines = ["---"]
    for k in PURSUIT_FRONTMATTER_KEYS:
        lines.append(f"{k}: {fmt_yaml_value(fm.get(k))}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {item.get('ref')} — {item.get('title','')}")
    lines.append("")

    if item.get("scopeSummary"):
        lines.extend(["## What it is", "", item["scopeSummary"], ""])
    if item.get("scoringRationale"):
        lines.extend(["## Why it matters", "", item["scoringRationale"], ""])
    if item.get("competitiveField"):
        lines.append("## Competitive field (from FTS award history)")
        lines.append("")
        for s in item["competitiveField"]:
            lines.append(f"- {s}")
        lines.append("")

    lines.append("## Key dates")
    lines.append("")
    for label, key in [
        ("Published", "publishedDate"),
        ("Registration deadline", "registrationDeadline"),
        ("Engagement session", "sessionDate"),
        ("Tender expected", "tenderExpected"),
        ("Tender deadline", "tenderDeadline"),
        ("Contract start", "contractStart"),
        ("Contract end", "contractEnd"),
    ]:
        v = item.get(key)
        if v:
            lines.append(f"- **{label}:** {v}")
    lines.append("")

    lines.append("## Actions")
    lines.append("")
    lines.append(f"- [x] Logged in pursuits pipeline ({datetime.now().strftime('%Y-%m-%d')})")
    lines.append("- [ ] Read the brief, decide next step (set `status: action_required` + an `action_type`)")
    if item.get("contentAngle"):
        lines.append(f"- [ ] Content angle to consider: {item['contentAngle']}")
    lines.append("")

    lines.append("## Contact")
    lines.append("")
    lines.append(f"- **Notice URL:** {item.get('noticeUrl','—')}")
    lines.append("")
    return "\n".join(lines)


def write_pursuit_file(item: dict[str, Any], bucket: str, dry_run: bool) -> Path | None:
    ref = item.get("ref")
    if not ref:
        log.warning("item without ref skipped: %s", item.get("title"))
        return None
    title_slug = slugify(item.get("title") or "")
    fname = f"{ref}-{title_slug}.md" if title_slug else f"{ref}.md"
    path = PURSUITS_DIR / fname

    if path.exists():
        log.info("pursuit file exists, skipping: %s", path.name)
        return path

    notice_type_default = "UK2" if bucket == "BOOK" else "UK4"
    content = render_pursuit_file(item, notice_type_default)
    if dry_run:
        log.info("[dry-run] would write %s (%d chars)", path.name, len(content))
        return path
    path.write_text(content, encoding="utf-8")
    log.info("wrote pursuit file: %s", path.name)
    return path


# ══════════════════════════════════════════════════════════════════════════════
# 3 — Pursuits index updater
# ══════════════════════════════════════════════════════════════════════════════

def fmt_value_for_index(v: Any) -> str:
    if v is None:
        return "—"
    try:
        n = float(v)
    except (TypeError, ValueError):
        return str(v)
    if n >= 1_000_000:
        return f"£{n/1_000_000:.1f}m"
    if n >= 1_000:
        return f"£{n/1_000:.0f}k"
    return f"£{n:.0f}"


def update_pursuits_index(items: list[tuple[dict, str, Path | None]], dry_run: bool) -> None:
    """Append rows to the Pipeline table for any new items not already there."""
    if not PURSUITS_INDEX.exists():
        log.warning("pursuits index not found: %s", PURSUITS_INDEX)
        return
    text = PURSUITS_INDEX.read_text(encoding="utf-8")

    # Find the Pipeline section table; collect existing refs
    existing_refs = set(re.findall(r"\| \[([A-Z0-9]+)\]\(", text))

    new_rows = []
    for item, bucket, path in items:
        ref = item.get("ref")
        if not ref or ref in existing_refs:
            continue
        title = (item.get("title") or "").replace("|", "\\|")
        buyer = (item.get("buyer") or "").replace("|", "\\|")
        value = fmt_value_for_index(item.get("value"))
        ntype = item.get("noticeType") or ("UK2" if bucket == "BOOK" else "UK4")
        deadline = (
            item.get("registrationDeadline")
            or item.get("tenderDeadline")
            or item.get("submissionDeadline")
            or "—"
        )
        fname = path.name if path else f"{ref}.md"
        new_rows.append(
            f"| [{ref}]({fname}) | {title} | {buyer} | {value} | {ntype} | {deadline} | new |"
        )

    if not new_rows:
        log.info("pursuits index: no new rows")
        return

    if dry_run:
        log.info("[dry-run] would append %d rows to pursuits index", len(new_rows))
        for row in new_rows:
            log.info("  %s", row)
        return

    # Append rows just below the Pipeline table header. We look for the header
    # and insert before the next blank line / next H2.
    pattern = re.compile(
        r"(## Pipeline\s*\n\n\| Ref \| Title \| Buyer \| Value \| Type \| Deadline \| Status \|\n\|[^\n]+\n)((?:\|[^\n]*\n)*)",
        re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        log.warning("pursuits index: Pipeline table header not found; appending at end")
        text = text.rstrip() + "\n\n" + "\n".join(new_rows) + "\n"
    else:
        existing_block = m.group(2)
        text = text[:m.end(1)] + existing_block + "\n".join(new_rows) + "\n" + text[m.end(2):]

    PURSUITS_INDEX.write_text(text, encoding="utf-8")
    log.info("pursuits index: appended %d rows", len(new_rows))


# ══════════════════════════════════════════════════════════════════════════════
# 4 — CRM upsert
# ══════════════════════════════════════════════════════════════════════════════

def upsert_crm_opportunity(item: dict, bucket: str, pursuit_path: Path | None, dry_run: bool) -> None:
    if not CRM_DB.exists():
        log.warning("crm.db not found at %s — skipping CRM upsert", CRM_DB)
        return
    if dry_run:
        log.info("[dry-run] would upsert crm.opportunities for %s (bucket=%s)", item.get("ref"), bucket)
        return

    conn = sqlite3.connect(str(CRM_DB))
    try:
        # Initial status: 'new' for BOOK/QUALIFY, 'watching' for INTEL.
        # We don't write opportunities for WATCH items (audit only).
        status = "new" if bucket in ("BOOK", "QUALIFY") else "watching"
        conn.execute(
            """
            INSERT INTO opportunities (
                id, title, value, notice_type, priority, status,
                published_date, registration_deadline, session_date,
                tender_expected, submission_deadline,
                contract_start, contract_end, notice_url, pursuit_file,
                content_angle, updated_at
            ) VALUES (
                :id, :title, :value, :notice_type, :priority, :status,
                :published_date, :registration_deadline, :session_date,
                :tender_expected, :submission_deadline,
                :contract_start, :contract_end, :notice_url, :pursuit_file,
                :content_angle, datetime('now')
            )
            ON CONFLICT(id) DO UPDATE SET
                title          = excluded.title,
                priority       = excluded.priority,
                pursuit_file   = COALESCE(excluded.pursuit_file, pursuit_file),
                content_angle  = COALESCE(excluded.content_angle, content_angle),
                updated_at     = datetime('now')
            """,
            {
                "id":                    item.get("ref"),
                "title":                 item.get("title"),
                "value":                 item.get("value"),
                "notice_type":           item.get("noticeType") or ("UK2" if bucket == "BOOK" else "UK4" if bucket == "QUALIFY" else "UK5"),
                "priority":              item.get("priority", "medium"),
                "status":                status,
                "published_date":        item.get("publishedDate"),
                "registration_deadline": item.get("registrationDeadline"),
                "session_date":          item.get("sessionDate"),
                "tender_expected":       item.get("tenderExpected"),
                "submission_deadline":   item.get("tenderDeadline") or item.get("submissionDeadline"),
                "contract_start":        item.get("contractStart"),
                "contract_end":          item.get("contractEnd"),
                "notice_url":            item.get("noticeUrl"),
                "pursuit_file":          str(pursuit_path) if pursuit_path else None,
                "content_angle":         item.get("contentAngle"),
            },
        )
        conn.commit()
        log.debug("crm: upserted %s", item.get("ref"))
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# 5 — Digest writer
# ══════════════════════════════════════════════════════════════════════════════

def save_digest(triage: dict, dry_run: bool) -> Path | None:
    digest = triage.get("digest") or "(no digest produced)"
    today = datetime.now().strftime("%Y-%m-%d")
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    path = DIGESTS_DIR / f"{today}.md"
    if dry_run:
        log.info("[dry-run] would write digest to %s (%d chars)", path, len(digest))
        return path
    path.write_text(digest, encoding="utf-8")
    log.info("digest saved: %s", path)
    return path


# ══════════════════════════════════════════════════════════════════════════════
# 5b — Email sender (Gmail SMTP via app password)
# ══════════════════════════════════════════════════════════════════════════════
#
# Reads three env vars set by the user (Windows: setx ...):
#   GMAIL_APP_PASSWORD  — Google app password (16-char, generated at
#                          myaccount.google.com/apppasswords)
#   PWIN_DIGEST_FROM    — full Gmail / Workspace address used to send
#   PWIN_DIGEST_TO      — recipient (often same as FROM)
#
# Falls back to no-op + warning if any are missing — the pipeline must still
# succeed (the digest file has already been saved).

def send_email_digest(
    triage: dict,
    counts: dict[str, int],
    digest_path: Path | None,
    dry_run: bool,
) -> bool:
    pwd       = os.environ.get("GMAIL_APP_PASSWORD")
    sender    = os.environ.get("PWIN_DIGEST_FROM")
    recipient = os.environ.get("PWIN_DIGEST_TO")

    if not (pwd and sender and recipient):
        missing = [n for n, v in [
            ("GMAIL_APP_PASSWORD", pwd),
            ("PWIN_DIGEST_FROM",   sender),
            ("PWIN_DIGEST_TO",     recipient),
        ] if not v]
        log.warning("email not sent — missing env var(s): %s", ", ".join(missing))
        return False

    digest_text = (triage.get("digest") or "(no digest produced)").strip()
    today_human = datetime.now().strftime("%a %d %b %Y")

    booked   = counts.get("BOOK", 0)
    qualify  = counts.get("QUALIFY", 0)
    intel_n  = counts.get("INTEL", 0)
    actioned = booked + qualify
    summary  = (
        f"{actioned} need attention" if actioned
        else f"clean ({intel_n} intel)" if intel_n
        else "clean"
    )
    subject = f"[BidEquity Intel] Daily Pipeline {today_human} | {summary}"

    body = digest_text
    if digest_path:
        body += f"\n\n---\nSaved locally: {digest_path}"

    if dry_run:
        log.info("[dry-run] would email %s -> %s — subject: %s", sender, recipient, subject)
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = sender
    msg["To"]      = recipient
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, pwd)
            server.send_message(msg)
        log.info("digest emailed: %s -> %s (%d chars)", sender, recipient, len(body))
        return True
    except smtplib.SMTPAuthenticationError as e:
        log.error("SMTP auth failed — check GMAIL_APP_PASSWORD and PWIN_DIGEST_FROM. %s", e)
        return False
    except Exception as e:
        log.error("email send failed: %s", e)
        return False


# ══════════════════════════════════════════════════════════════════════════════
# 6 — Main
# ══════════════════════════════════════════════════════════════════════════════

def process(triage_obj: dict, dry_run: bool) -> dict[str, int]:
    triage = triage_obj.get("triage", {})
    counts = {"BOOK": 0, "QUALIFY": 0, "INTEL": 0, "WATCH": 0}

    items_for_index: list[tuple[dict, str, Path | None]] = []

    for bucket in ("BOOK", "QUALIFY"):
        for item in triage.get(bucket, []) or []:
            counts[bucket] += 1
            path = write_pursuit_file(item, bucket, dry_run)
            upsert_crm_opportunity(item, bucket, path, dry_run)
            items_for_index.append((item, bucket, path))

    for item in triage.get("INTEL", []) or []:
        counts["INTEL"] += 1
        upsert_crm_opportunity(item, "INTEL", None, dry_run)

    counts["WATCH"] = len(triage.get("WATCH", []) or [])

    update_pursuits_index(items_for_index, dry_run)
    digest_path = save_digest(triage_obj, dry_run)
    send_email_digest(triage_obj, counts, digest_path, dry_run)
    return counts


def main():
    p = argparse.ArgumentParser(description="Daily pipeline scan orchestrator")
    p.add_argument("--hours", type=int, default=24, help="lookback window hours (default 24)")
    p.add_argument("--dry-run", action="store_true", help="don't write anything")
    p.add_argument("--skip-skill", action="store_true",
                   help="skip the skill call; load result from --json instead")
    p.add_argument("--json", type=str, help="path to a saved skill result JSON (for debug)")
    p.add_argument("--save-result", type=str,
                   help="write the raw skill result JSON to this path (for debug)")
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    if args.skip_skill:
        if not args.json:
            log.error("--skip-skill requires --json <path>")
            sys.exit(2)
        skill_result = json.loads(Path(args.json).read_text(encoding="utf-8"))
    else:
        skill_result = run_skill(hours=args.hours, dry_run=False)

    if args.save_result:
        Path(args.save_result).write_text(json.dumps(skill_result, indent=2), encoding="utf-8")
        log.info("raw skill result saved to %s", args.save_result)

    triage = extract_triage_json(skill_result)
    if not triage:
        log.error("could not extract triage JSON from skill output")
        log.error("skill text (first 1500 chars): %s",
                  (skill_result.get("text") or "")[:1500])
        sys.exit(1)

    log.info("triage extracted: BOOK=%d QUALIFY=%d INTEL=%d WATCH=%d",
             len(triage.get("triage", {}).get("BOOK", []) or []),
             len(triage.get("triage", {}).get("QUALIFY", []) or []),
             len(triage.get("triage", {}).get("INTEL", []) or []),
             len(triage.get("triage", {}).get("WATCH", []) or []))

    counts = process(triage, args.dry_run)
    log.info("processing complete: %s", counts)


if __name__ == "__main__":
    main()
