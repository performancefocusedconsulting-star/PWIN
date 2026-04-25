#!/usr/bin/env python3
"""
BidEquity Pursuit Watcher
=========================
Polls wiki/pursuits/*.md for pursuit files whose YAML frontmatter signals
that Paul wants autonomous action. When status == 'action_required' and
processed_at is null, dispatches to an action handler based on action_type,
writes the result back into the file, and syncs crm.db.

State machine (mirrors db/crm-schema.sql and daily-pipeline-scan.yaml):

    status: new | watching | action_required | researched |
            registered_pending | attending | active | draft_sent |
            no_bid | won | lost | withdrawn | superseded

    action_type: research | register | reach_out | campaign | no_action

Idempotency: the watcher fires only when processed_at is ~ (null). After a
successful action, it sets processed_at to the current ISO datetime and
advances status, so the same file is never processed twice.

Usage:
    python agent/watcher.py                 # run once, exit
    python agent/watcher.py --loop          # poll every 120s
    python agent/watcher.py --interval 300  # custom poll interval (seconds)
    python agent/watcher.py --dry-run       # log what would happen, don't write
    python agent/watcher.py --file <path>   # process a single file
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Paths ─────────────────────────────────────────────────────────────────────

PURSUITS_DIR = Path("C:/Users/User/Documents/Obsidian Vault/wiki/pursuits")
BID_INTEL_DB = Path(__file__).parent.parent / "db" / "bid_intel.db"
CRM_DB       = Path.home() / ".pwin" / "crm.db"

# ── Claude API ────────────────────────────────────────────────────────────────

ANTHROPIC_URL    = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL  = "claude-sonnet-4-6"
ANTHROPIC_MAX    = 2048

log = logging.getLogger("watcher")


# ══════════════════════════════════════════════════════════════════════════════
# 1 — Frontmatter parser / writer
# ══════════════════════════════════════════════════════════════════════════════
#
# We control the schema (flat key: value pairs, no nesting, no lists).
# A tiny hand-rolled parser avoids a PyYAML dependency.

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body_text). Empty dict if no frontmatter."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    fm_block = m.group(1)
    body = text[m.end():]

    fm: dict[str, Any] = {}
    for line in fm_block.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        val = raw.strip()
        if val == "~" or val == "null" or val == "":
            fm[key] = None
        elif val.lower() == "true":
            fm[key] = True
        elif val.lower() == "false":
            fm[key] = False
        elif val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
            fm[key] = int(val)
        else:
            # strip matching surrounding quotes only
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            fm[key] = val
    return fm, body


def _fmt_val(v: Any) -> str:
    if v is None:
        return "~"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    # quote only if the value contains a colon followed by a space or starts
    # with a character YAML would mis-parse
    if re.search(r":\s", s) or s.startswith(("[", "{", "!", "&", "*", ">", "|", "%")):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def render_frontmatter(fm: dict[str, Any], body: str, key_order: list[str]) -> str:
    """Render fm + body back to a full markdown document preserving key order."""
    lines = ["---"]
    seen = set()
    for k in key_order:
        if k in fm:
            lines.append(f"{k}: {_fmt_val(fm[k])}")
            seen.add(k)
    # any keys that were in the file but not in key_order go at the end,
    # in insertion order (dicts are ordered in py3.7+)
    for k, v in fm.items():
        if k not in seen:
            lines.append(f"{k}: {_fmt_val(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


# Canonical key order for pursuit frontmatter (matches daily-pipeline-scan.yaml)
PURSUIT_KEY_ORDER = [
    "ref", "status", "action_type", "close_reason", "priority", "buyer",
    "value", "notice_type", "notice_url", "published",
    "registration_deadline", "session_date", "tender_expected",
    "submission_deadline", "contract_start", "contract_end", "processed_at",
]


# ══════════════════════════════════════════════════════════════════════════════
# 2 — Body section injection
# ══════════════════════════════════════════════════════════════════════════════

def upsert_body_section(body: str, heading: str, content: str) -> str:
    """
    Insert or replace a `## {heading}` section in the body.

    If the heading exists, replace everything from that heading up to (but not
    including) the next H2 heading (or end-of-file). If it does not exist,
    append the section at the end.
    """
    pattern = re.compile(
        rf"(^##\s+{re.escape(heading)}\s*\n)(.*?)(?=^##\s+|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    new_block = f"## {heading}\n\n{content.rstrip()}\n\n"
    if pattern.search(body):
        return pattern.sub(new_block, body, count=1)
    # append
    if not body.endswith("\n"):
        body += "\n"
    return body + "\n" + new_block


# ══════════════════════════════════════════════════════════════════════════════
# 3 — bid_intel.db context queries
# ══════════════════════════════════════════════════════════════════════════════

def _get_intel_db() -> sqlite3.Connection | None:
    if not BID_INTEL_DB.exists():
        log.warning("bid_intel.db not found at %s — research will run without history", BID_INTEL_DB)
        return None
    conn = sqlite3.connect(str(BID_INTEL_DB))
    conn.row_factory = sqlite3.Row
    return conn


def gather_buyer_context(buyer_name: str, limit: int = 15) -> dict[str, Any]:
    """
    Fetch recent awards and top suppliers for a buyer, best-effort matching
    on name. Returns {} if the DB is missing or there's no match.
    """
    conn = _get_intel_db()
    if conn is None:
        return {}

    # Token search — buyer_name from notice may be multi-org ("BLC / NPCC / HO")
    tokens = [t.strip() for t in re.split(r"[/,]| and ", buyer_name) if t.strip()]
    if not tokens:
        tokens = [buyer_name]

    matched_buyers: list[sqlite3.Row] = []
    seen_ids: set = set()
    for tok in tokens:
        rows = conn.execute(
            "SELECT id, name FROM buyers WHERE name LIKE ? LIMIT 5",
            (f"%{tok}%",),
        ).fetchall()
        for r in rows:
            if r["id"] not in seen_ids:
                matched_buyers.append(r)
                seen_ids.add(r["id"])

    if not matched_buyers:
        conn.close()
        return {"matched_buyers": []}

    buyer_ids = tuple(b["id"] for b in matched_buyers)
    placeholders = ",".join("?" * len(buyer_ids))

    # Recent awards at these buyers
    awards = conn.execute(
        f"""
        SELECT a.id, a.title, a.award_date, a.value_amount,
               a.contract_end_date, n.ocid, b.name AS buyer_name,
               GROUP_CONCAT(s.name, ' | ') AS suppliers
        FROM awards a
        JOIN notices n       ON a.ocid = n.ocid
        JOIN buyers b        ON n.buyer_id = b.id
        LEFT JOIN award_suppliers asup ON a.id = asup.award_id
        LEFT JOIN suppliers s          ON asup.supplier_id = s.id
        WHERE n.buyer_id IN ({placeholders})
          AND a.award_date IS NOT NULL
        GROUP BY a.id
        ORDER BY a.award_date DESC
        LIMIT ?
        """,
        (*buyer_ids, limit),
    ).fetchall()

    # Top suppliers by award count
    top_suppliers = conn.execute(
        f"""
        SELECT s.name, COUNT(*) AS n_awards, SUM(a.value_amount) AS total_value
        FROM award_suppliers asup
        JOIN suppliers s ON asup.supplier_id = s.id
        JOIN awards a    ON asup.award_id   = a.id
        JOIN notices n   ON a.ocid          = n.ocid
        WHERE n.buyer_id IN ({placeholders})
        GROUP BY s.id
        ORDER BY n_awards DESC
        LIMIT 10
        """,
        buyer_ids,
    ).fetchall()

    conn.close()
    return {
        "matched_buyers":  [dict(r) for r in matched_buyers],
        "recent_awards":   [dict(r) for r in awards],
        "top_suppliers":   [dict(r) for r in top_suppliers],
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4 — Claude API call
# ══════════════════════════════════════════════════════════════════════════════

def call_claude(system: str, user: str, max_tokens: int = ANTHROPIC_MAX) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    payload = {
        "model":      ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "system":     system,
        "messages":   [{"role": "user", "content": user}],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=data,
        headers={
            "content-type":      "application/json",
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Claude API error {e.code}: {err}") from e

    parts = body.get("content", [])
    return "".join(p.get("text", "") for p in parts if p.get("type") == "text").strip()


# ══════════════════════════════════════════════════════════════════════════════
# 5 — Action handlers
# ══════════════════════════════════════════════════════════════════════════════
#
# Each handler receives (fm, body) and returns (new_fm, new_body, summary).
# The caller is responsible for persisting and for crm.db sync.

RESEARCH_SYSTEM = (
    "You are a senior public-sector bid intelligence analyst writing a concise "
    "research brief for Paul Fenton at BidEquity. Paul scans briefs in under 60 "
    "seconds. Write in clean markdown with short sections. Do not speculate — "
    "if a data point is missing, omit it rather than guess."
)


def _research_user_prompt(fm: dict, intel: dict) -> str:
    recent = intel.get("recent_awards") or []
    suppliers = intel.get("top_suppliers") or []

    lines = [
        f"## Pursuit",
        f"- Ref: {fm.get('ref')}",
        f"- Buyer: {fm.get('buyer')}",
        f"- Notice type: {fm.get('notice_type')}",
        f"- Value: £{fm.get('value'):,}" if fm.get("value") else "- Value: unstated",
        f"- Notice URL: {fm.get('notice_url')}",
        f"- Tender expected: {fm.get('tender_expected') or 'unknown'}",
        f"- Contract window: {fm.get('contract_start') or '?'} → {fm.get('contract_end') or '?'}",
        "",
        "## Buyer history from FTS (bid_intel.db)",
    ]

    if not intel.get("matched_buyers"):
        lines.append("No matching buyer record found — treat as greenfield.")
    else:
        matches = ", ".join(b["name"] for b in intel["matched_buyers"])
        lines.append(f"Matched buyers: {matches}")
        lines.append("")
        lines.append("### Recent awards")
        if not recent:
            lines.append("None in the window.")
        else:
            for a in recent[:12]:
                val = f"£{a['value_amount']:,.0f}" if a.get("value_amount") else "—"
                date = a.get("award_date") or "?"
                sup = a.get("suppliers") or "?"
                lines.append(f"- {date} · {a.get('title','')[:80]} · {val} · {sup}")
        lines.append("")
        lines.append("### Top suppliers at this buyer")
        if not suppliers:
            lines.append("None.")
        else:
            for s in suppliers[:10]:
                tv = f"£{s['total_value']:,.0f}" if s.get("total_value") else "—"
                lines.append(f"- {s['name']} — {s['n_awards']} awards, {tv}")

    lines.extend([
        "",
        "## Write a research brief with these sections",
        "",
        "### Buyer read",
        "Two or three sentences on the buyer's likely priorities and procurement pattern, drawn from the award history above.",
        "",
        "### Likely competitive field",
        "Bullet list of 5–8 suppliers likely to bid, with a one-line reason each. Draw primarily from the top suppliers list. Name specific firms only if they appear above; otherwise describe the archetype (e.g. 'large SI with policing delivery track record').",
        "",
        "### Angle for BidEquity",
        "Two or three sentences: what BidEquity's distinctive play is (intelligence support to a consortium, direct bid advisory, content/thought-leadership angle, or no-action and log).",
        "",
        "### Key risks or watch-outs",
        "Bullet list of 3–5 things to check before committing time. Be specific.",
        "",
        "### Recommendation",
        "One sentence. One of: REGISTER / PROBE / PASS / WATCH.",
    ])
    return "\n".join(lines)


def action_research(fm: dict, body: str, dry_run: bool = False) -> tuple[dict, str, str]:
    buyer = fm.get("buyer") or ""
    intel = gather_buyer_context(buyer) if buyer else {}

    if dry_run:
        brief = "_[dry-run: research brief would be generated here]_"
    else:
        prompt = _research_user_prompt(fm, intel)
        brief = call_claude(RESEARCH_SYSTEM, prompt)

    new_body = upsert_body_section(body, "Research Brief", brief)
    new_fm = dict(fm)
    new_fm["status"] = "researched"
    new_fm["processed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    summary = f"Generated research brief ({len(brief)} chars); {len(intel.get('recent_awards') or [])} recent awards in context"
    return new_fm, new_body, summary


def action_no_action(fm: dict, body: str, dry_run: bool = False) -> tuple[dict, str, str]:
    new_fm = dict(fm)
    new_fm["status"] = "watching"
    new_fm["processed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    return new_fm, body, "Marked watching (no_action)"


def action_stub(kind: str):
    def _stub(fm: dict, body: str, dry_run: bool = False) -> tuple[dict, str, str]:
        new_fm = dict(fm)
        # stash a note in the body so Paul sees it
        stub_note = (
            f"_Watcher: `{kind}` handler is not yet implemented. File left with "
            f"`status: action_required` for manual handling._"
        )
        new_body = upsert_body_section(body, f"Watcher note ({kind})", stub_note)
        # Do NOT set processed_at — keeps the file idempotent-eligible for when
        # the handler ships. But do flag that we've seen it.
        return new_fm, new_body, f"Stub handler for action_type={kind} (not implemented)"
    return _stub


ACTION_HANDLERS = {
    "research":  action_research,
    "no_action": action_no_action,
    "register":  action_stub("register"),
    "reach_out": action_stub("reach_out"),
    "campaign":  action_stub("campaign"),
}


# ══════════════════════════════════════════════════════════════════════════════
# 6 — CRM sync
# ══════════════════════════════════════════════════════════════════════════════

def sync_crm_opportunity(fm: dict, pursuit_file: Path) -> None:
    """Upsert crm.db opportunities row from frontmatter state."""
    if not CRM_DB.exists():
        log.warning("crm.db not found at %s — skipping CRM sync", CRM_DB)
        return

    conn = sqlite3.connect(str(CRM_DB))
    try:
        conn.execute(
            """
            INSERT INTO opportunities (
                id, title, value, notice_type, priority, status, action_type,
                published_date, registration_deadline, session_date,
                tender_expected, submission_deadline,
                contract_start, contract_end, notice_url, pursuit_file,
                processed_at, updated_at
            ) VALUES (
                :id, :title, :value, :notice_type, :priority, :status, :action_type,
                :published_date, :registration_deadline, :session_date,
                :tender_expected, :submission_deadline,
                :contract_start, :contract_end, :notice_url, :pursuit_file,
                :processed_at, datetime('now')
            )
            ON CONFLICT(id) DO UPDATE SET
                status         = excluded.status,
                action_type    = excluded.action_type,
                priority       = excluded.priority,
                processed_at   = excluded.processed_at,
                pursuit_file   = excluded.pursuit_file,
                updated_at     = datetime('now')
            """,
            {
                "id":                     fm.get("ref"),
                "title":                  _title_from_file(pursuit_file, fm),
                "value":                  fm.get("value"),
                "notice_type":            fm.get("notice_type"),
                "priority":               fm.get("priority") or "medium",
                "status":                 fm.get("status"),
                "action_type":            fm.get("action_type"),
                "published_date":         fm.get("published"),
                "registration_deadline":  fm.get("registration_deadline"),
                "session_date":           fm.get("session_date"),
                "tender_expected":        fm.get("tender_expected"),
                "submission_deadline":    fm.get("submission_deadline"),
                "contract_start":         fm.get("contract_start"),
                "contract_end":           fm.get("contract_end"),
                "notice_url":             fm.get("notice_url"),
                "pursuit_file":           str(pursuit_file),
                "processed_at":           fm.get("processed_at"),
            },
        )
        conn.commit()
    finally:
        conn.close()


def log_crm_interaction(ref: str, summary: str, outcome: str) -> None:
    if not CRM_DB.exists():
        return
    conn = sqlite3.connect(str(CRM_DB))
    try:
        conn.execute(
            """
            INSERT INTO interactions (date, type, opportunity_id, summary, outcome)
            VALUES (datetime('now'), 'watcher_action', ?, ?, ?)
            """,
            (ref, summary, outcome),
        )
        conn.commit()
    finally:
        conn.close()


def _title_from_file(path: Path, fm: dict) -> str:
    """Best-effort title: the first H1, or the slug after the ref."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return fm.get("ref") or path.stem
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if m:
        t = m.group(1)
        # strip "REF — " prefix if present
        return re.sub(r"^[A-Z0-9]+\s+[—-]\s+", "", t)
    return fm.get("ref") or path.stem


# ══════════════════════════════════════════════════════════════════════════════
# 7 — Processing loop
# ══════════════════════════════════════════════════════════════════════════════

def process_file(path: Path, dry_run: bool = False) -> str:
    """
    Process a single pursuit file. Returns a short status string for logs.
    Idempotent — files already processed (processed_at set) or not flagged
    (status != action_required) are skipped.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"read error: {e}"

    fm, body = parse_frontmatter(text)
    if not fm:
        return "skip (no frontmatter)"
    if fm.get("status") != "action_required":
        return f"skip (status={fm.get('status')!r})"
    if fm.get("processed_at"):
        return f"skip (already processed at {fm['processed_at']})"

    action_type = fm.get("action_type")
    handler = ACTION_HANDLERS.get(action_type)
    if handler is None:
        return f"skip (unknown action_type={action_type!r})"

    log.info("processing %s (action_type=%s)", path.name, action_type)
    try:
        new_fm, new_body, summary = handler(fm, body, dry_run=dry_run)
    except Exception as e:
        log.exception("handler failed for %s: %s", path.name, e)
        log_crm_interaction(fm.get("ref") or path.stem, f"handler error: {e}", "error")
        return f"error: {e}"

    if dry_run:
        return f"dry-run -> {summary}"

    rendered = render_frontmatter(new_fm, new_body, PURSUIT_KEY_ORDER)
    path.write_text(rendered, encoding="utf-8")

    try:
        sync_crm_opportunity(new_fm, path)
        log_crm_interaction(new_fm.get("ref") or path.stem, summary, "ok")
    except Exception as e:
        log.exception("crm sync failed for %s: %s", path.name, e)

    return f"processed -> status={new_fm.get('status')} - {summary}"


def scan_once(dry_run: bool = False) -> int:
    """Scan the pursuits dir once. Returns the number of files processed."""
    if not PURSUITS_DIR.exists():
        log.error("Pursuits dir not found: %s", PURSUITS_DIR)
        return 0

    count = 0
    for path in sorted(PURSUITS_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        result = process_file(path, dry_run=dry_run)
        if result.startswith("skip"):
            log.debug("%s: %s", path.name, result)
        else:
            log.info("%s: %s", path.name, result)
            count += 1
    return count


def scan_loop(interval: int, dry_run: bool = False) -> None:
    log.info("Watcher loop started — polling %s every %ds", PURSUITS_DIR, interval)
    while True:
        try:
            n = scan_once(dry_run=dry_run)
            if n:
                log.info("tick: %d file(s) processed", n)
        except KeyboardInterrupt:
            log.info("interrupt — exiting")
            return
        except Exception:
            log.exception("scan failed; continuing")
        time.sleep(interval)


# ══════════════════════════════════════════════════════════════════════════════
# 8 — CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description="BidEquity pursuit watcher")
    p.add_argument("--loop", action="store_true", help="run continuously")
    p.add_argument("--interval", type=int, default=120, help="poll seconds (loop mode)")
    p.add_argument("--dry-run", action="store_true", help="log but don't write")
    p.add_argument("--file", type=str, help="process a single file (absolute or relative to PURSUITS_DIR)")
    p.add_argument("--verbose", "-v", action="store_true", help="debug logging")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    if args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = PURSUITS_DIR / path
        if not path.exists():
            print(f"File not found: {path}")
            sys.exit(1)
        print(process_file(path, dry_run=args.dry_run))
        return

    if args.loop:
        scan_loop(args.interval, dry_run=args.dry_run)
    else:
        n = scan_once(dry_run=args.dry_run)
        print(f"Scan complete — {n} file(s) processed")


if __name__ == "__main__":
    main()
