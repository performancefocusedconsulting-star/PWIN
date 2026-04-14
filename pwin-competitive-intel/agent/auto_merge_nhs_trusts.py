#!/usr/bin/env python3
"""Deterministic auto-merge: NHS trust no-CH FTS-synthetic variants.

Clears the large volume of NHS-trust publisher name variants from Morgan's
queue without cycling an AI call. Pattern noted in batch 002: 4 of 20
pairs were Manchester University NHS FT publisher variants, and the wider
queue has many more.

Rule (conservative by design):

  For any pair currently in adjudication_queue where:
    - left side is identifiably an NHS trust (name matches NHS-trust regex)
    - right side has id_kind='fts_synthetic' (GB-FTS-*) with no CH numbers
    - right's locality overlaps with a locality in left's postcodes+localities
    - right's canonical_name, as a normalised token set, is a subset of
      left's canonical_name token set OR left's name_variants contains the
      right's canonical_name verbatim (after whitespace normalisation)
  → auto-approve the merge and mark the queue row 'auto_approved'

Pairs that don't match this specific shape stay in the queue for Morgan.
Deliberately narrow — expanding the rule later is safer than widening it
now and sweeping in a wrong merge.

Run:
  .venv/bin/python agent/auto_merge_nhs_trusts.py                  # preview
  .venv/bin/python agent/auto_merge_nhs_trusts.py --apply          # execute
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "bid_intel.db"
LEDGER = REPO_ROOT / "adjudicator" / "adjudicator_decisions.jsonl"

NHS_TRUST_RE = re.compile(
    r"\bnhs\b.*\b(trust|foundation trust|nhsft|nhs ft|foundation)\b"
    r"|\b(university hospitals?|hospitals?)\b.*\bnhs\b",
    re.IGNORECASE,
)
_TOKEN_RE = re.compile(r"[a-z0-9]+")
# Tokens that carry no identifying signal — ignored when we check whether
# right's name is a subset of left's
_STOPWORDS = {
    "nhs", "foundation", "trust", "ft", "nhsft", "the", "of", "and",
    "for", "limited", "ltd", "plc", "hospital", "hospitals",
}


def _norm_tokens(s: str | None) -> set[str]:
    if not s:
        return set()
    toks = _TOKEN_RE.findall(s.lower())
    return {t for t in toks if t not in _STOPWORDS}


def _collapse_ws(s: str | None) -> str | None:
    if not s:
        return None
    return re.sub(r"\s+", " ", s).strip().lower()


def find_candidates(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    q = """
        SELECT queue_id, left_canonical_id, right_canonical_id,
               left_name, right_name,
               left_name_variants, right_name_variants,
               left_postcodes, right_postcodes,
               left_localities, right_localities,
               left_id_kind, right_id_kind,
               left_ch_numbers, right_ch_numbers,
               left_member_count, right_member_count,
               max_match_probability
        FROM adjudication_queue
        WHERE status = 'pending'
    """
    candidates = []
    for r in conn.execute(q):
        left_name = r["left_name"] or ""
        # NHS trust on the left side
        if not NHS_TRUST_RE.search(left_name):
            continue
        # Right must be a no-CH FTS synthetic
        if r["right_id_kind"] != "fts_synthetic":
            continue
        if r["right_ch_numbers"]:
            continue

        right_name = r["right_name"] or ""
        right_name_norm = _collapse_ws(right_name)

        # Left's name_variants contains right's name verbatim? → approve
        variants = json.loads(r["left_name_variants"] or "[]")
        variants_norm = {_collapse_ws(v) for v in variants if v}
        variant_hit = right_name_norm in variants_norm

        # OR right's signal tokens are a subset of left's signal tokens
        left_tokens = _norm_tokens(left_name)
        for v in variants:
            left_tokens |= _norm_tokens(v)
        right_tokens = _norm_tokens(right_name)
        token_subset = bool(right_tokens) and right_tokens.issubset(left_tokens)

        if not (variant_hit or token_subset):
            continue

        # Locality overlap guard: right's locality should appear in left's
        # localities (case-insensitive). Cheap safety net to avoid a
        # "Newcastle Hospitals NHS FT" being merged into a "Manchester
        # University NHS FT" on pure name-token subset.
        left_locs = {l.lower() for l in json.loads(r["left_localities"] or "[]")}
        right_locs = {l.lower() for l in json.loads(r["right_localities"] or "[]")}
        if right_locs and left_locs and not (right_locs & left_locs):
            # Try partial match — publisher localities are free-text
            overlap = any(
                any(rl in ll or ll in rl for ll in left_locs)
                for rl in right_locs
            )
            if not overlap:
                continue

        # Survivor = left (it's the NHS trust canonical)
        candidates.append({
            "queue_id": r["queue_id"],
            "survivor_canonical_id": r["left_canonical_id"],
            "absorbed_canonical_id": r["right_canonical_id"],
            "left_name": left_name,
            "right_name": right_name,
            "left_member_count": r["left_member_count"],
            "right_member_count": r["right_member_count"],
            "match_rule": "variant_verbatim_match" if variant_hit else "token_subset_match",
            "max_match_probability": r["max_match_probability"],
        })
    return candidates


def apply(conn: sqlite3.Connection, candidates: list[dict]) -> int:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("PRAGMA foreign_keys = ON")

    # Pre-resolve transitive survivors: if A→B and B→C both appear in the
    # candidate list, A's survivor resolves to C (and B is already absorbed
    # by the time we reach A). Without this, the second merge hits an FK
    # violation because B has been deleted.
    absorbed_to_survivor: dict[str, str] = {
        c["absorbed_canonical_id"]: c["survivor_canonical_id"] for c in candidates
    }

    def _resolve(cid: str, seen: set[str] | None = None) -> str:
        seen = seen or set()
        if cid in seen:  # cycle guard — should never happen
            return cid
        seen.add(cid)
        if cid in absorbed_to_survivor:
            return _resolve(absorbed_to_survivor[cid], seen)
        return cid

    applied = 0
    with LEDGER.open("a") as ledger:
        for c in candidates:
            # Guard against status drift since the preview read
            status_row = conn.execute(
                "SELECT status FROM adjudication_queue WHERE queue_id = ?",
                (c["queue_id"],),
            ).fetchone()
            if not status_row or status_row[0] != "pending":
                continue

            survivor = _resolve(c["survivor_canonical_id"])
            absorbed = c["absorbed_canonical_id"]
            if survivor == absorbed:
                # Chain collapsed to identity — nothing to do, mark resolved
                conn.execute(
                    "UPDATE adjudication_queue SET status = 'auto_approved', reviewed_at = ? "
                    "WHERE queue_id = ?",
                    (now, c["queue_id"]),
                )
                continue
            n_moved = conn.execute(
                "UPDATE supplier_to_canonical SET canonical_id = ? WHERE canonical_id = ?",
                (survivor, absorbed),
            ).rowcount
            conn.execute(
                "DELETE FROM canonical_suppliers WHERE canonical_id = ?",
                (absorbed,),
            )
            conn.execute(
                """UPDATE canonical_suppliers
                      SET member_count = (
                        SELECT COUNT(*) FROM supplier_to_canonical s2c
                        WHERE s2c.canonical_id = canonical_suppliers.canonical_id
                      )
                    WHERE canonical_id = ?""",
                (survivor,),
            )

            decision_record = {
                "queue_id": c["queue_id"],
                "decision_type": "supplier_merge",
                "recommendation": "approve_merge",
                "status": "auto_approved",
                "adjudicator": "auto_merge_nhs_trusts",
                "batch_id": "auto_nhs_trust_001",
                "match_rule": c["match_rule"],
                "survivor_canonical_id": survivor,
                "absorbed_canonical_id": absorbed,
                "left_name_snapshot": c["left_name"],
                "right_name_snapshot": c["right_name"],
                "members_moved": n_moved,
                "reviewed_at": now,
                "evidence": [
                    f"Left matches NHS-trust regex",
                    f"Right is no-CH FTS synthetic",
                    f"Right matched via {c['match_rule']}",
                    f"Locality overlap verified",
                ],
            }
            conn.execute(
                "UPDATE adjudication_queue SET status = ?, decision_json = ?, reviewed_at = ? WHERE queue_id = ?",
                ("auto_approved", json.dumps(decision_record), now, c["queue_id"]),
            )
            ledger.write(json.dumps(decision_record) + "\n")
            applied += 1
    conn.commit()
    return applied


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Execute merges (default is preview-only)")
    ap.add_argument("--limit", type=int, default=20,
                    help="Preview cap (default 20)")
    args = ap.parse_args()

    with sqlite3.connect(DB_PATH) as conn:
        candidates = find_candidates(conn)
        print(f"[auto-nhs] {len(candidates):,} pairs matched the NHS-trust auto-merge rule")
        if not candidates:
            return 0

        # Preview top-N for sanity
        print(f"[auto-nhs] Preview (first {min(args.limit, len(candidates))}):")
        for c in candidates[:args.limit]:
            print(f"  {c['match_rule']:25} "
                  f"{c['left_name'][:55]:55} ← {c['right_name'][:50]} "
                  f"[prob={c['max_match_probability']:.2f}, "
                  f"moving {c['right_member_count']} rows]")

        if not args.apply:
            print()
            print("[auto-nhs] Preview only. Re-run with --apply to execute.")
            return 0

        print()
        print(f"[auto-nhs] Applying {len(candidates):,} merges…")
        applied = apply(conn, candidates)
        print(f"[auto-nhs] Done. {applied:,} merges committed; ledger appended.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
