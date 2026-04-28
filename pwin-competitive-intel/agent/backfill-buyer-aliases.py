#!/usr/bin/env python3
"""
backfill-buyer-aliases.py — register missing buyer aliases against the canonical layer.

The problem: many raw buyer rows fail to resolve to canonical because the
canonical_buyer_aliases table only registers 1-2 spellings per canonical entity
(canonical name + abbreviation). Real raw data carries many variants:
  - trailing punctuation ("Ministry of Justice.")
  - legal preambles ("The Secretary of State for Defence acting through DE&S")
  - prefix-then-dash ("DoJ - Ministry of Justice")
  - brand-in-parentheses ("Crown Commercial Service (CCS)")
  - HM/His Majesty's preambles

This script walks every raw buyer name in `buyers`, applies tidying rules,
and where a tidied name EXACTLY matches a canonical_name or abbreviation in
`canonical_buyers`, inserts a new row into `canonical_buyer_aliases`. It also
back-fills `buyers.canonical_id` for every newly resolved row so downstream
queries that use the back-reference column see the new matches without a
separate run of load-canonical-buyers.py.

Match policy:
  * Exact match only (after tidying). Never fuzzy.
  * Skip raw names that match more than one canonical entry (ambiguous).
  * Never overwrite or delete existing aliases.

Usage:
  python3 agent/backfill-buyer-aliases.py --dry-run   # report only, no writes
  python3 agent/backfill-buyer-aliases.py             # apply
  python3 agent/backfill-buyer-aliases.py --db /path/to/bid_intel.db --dry-run

Idempotent: safe to re-run; aliases already in the table are skipped.
"""
import argparse
import os
import re
import sqlite3
import sys
from collections import defaultdict

# Force UTF-8 stdout on Windows so pretty-printing doesn't crash on Unicode.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "bid_intel.db"
)

# Mirrors norm() in load-canonical-buyers.py so backfill aligns with the
# normalised-match path used by run_matching().
def _norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[\&]", " and ", s)
    s = re.sub(r"\bltd\b\.?", "limited", s)
    s = re.sub(r"[,\.\(\)\-\'\"]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ── Tidying rules ─────────────────────────────────────────────────────────
# Each rule takes a lowercased trimmed name and returns a list of candidate
# tidied names to try matching. Rules are conservative — exact match only,
# no fuzzy fallback.

DEPT_PREFIX_RE = re.compile(
    r"^(do[a-z]{1,4}|d[a-z]{1,3}|hm|moj|mod|dft|dwp|dhsc|fcdo|defra|beis|dcms|dluhc|nhs)\s*[-:–—]\s*",
    re.IGNORECASE,
)

# "The Secretary of State for X (acting|acting through Y)" → "Y" or "X"
SOS_ACTING_THROUGH_RE = re.compile(
    r"^(?:the\s+)?secretary of state for [^,]+?\s+acting\s+through\s+(.+?)$",
    re.IGNORECASE,
)
SOS_FOR_RE = re.compile(
    r"^(?:the\s+)?secretary of state for\s+(.+?)$",
    re.IGNORECASE,
)

# "The Common Services Agency (more commonly known as Z)" → "Z"
COMMON_KNOWN_AS_RE = re.compile(
    r"\(more commonly known as\s+([^)]+?)\)",
    re.IGNORECASE,
)

# "X (Y)" — pull both X and Y as candidates
PARENS_RE = re.compile(r"^([^(]+?)\s*\(([^)]+?)\)\s*$")

HM_PREAMBLE_RE = re.compile(
    r"^(his|her)\s+majesty'?s\s+",
    re.IGNORECASE,
)

# "On behalf of X" / "Acting on behalf of X" → "X"
ON_BEHALF_RE = re.compile(
    r"^(?:acting\s+)?on behalf of\s+(.+?)$",
    re.IGNORECASE,
)


def candidates_for(raw_name: str) -> list:
    """Generate the list of tidied-name candidates to test against canonicals."""
    out = []
    seen = set()

    def add(s: str):
        s = (s or "").strip()
        # Normalise internal whitespace and strip wrapping quotes
        s = re.sub(r"\s+", " ", s).strip(' "\'')
        # Strip trailing punctuation
        s = re.sub(r"[\.,;:]+$", "", s).strip()
        if not s:
            return
        if s.lower() in seen:
            return
        seen.add(s.lower())
        out.append(s)

    if not raw_name:
        return out

    base = raw_name.strip()
    add(base)

    # Strip trailing punctuation aggressively
    add(re.sub(r"[\.,;:]+$", "", base))

    # Strip wrapping quotes
    if (base.startswith('"') and base.endswith('"')) or (base.startswith("'") and base.endswith("'")):
        add(base[1:-1])

    lower = base.lower()

    # HM / His Majesty's / Her Majesty's preamble
    m = HM_PREAMBLE_RE.match(lower)
    if m:
        add(base[m.end():])

    # Department prefix-then-dash: "DoJ - Ministry of Justice" → "Ministry of Justice"
    m = DEPT_PREFIX_RE.match(base)
    if m:
        add(base[m.end():])
    m = DEPT_PREFIX_RE.match(lower)
    if m:
        add(base[m.end():])

    # Brand-in-parentheses: "Crown Commercial Service (CCS)" → both halves
    m = PARENS_RE.match(base)
    if m:
        add(m.group(1))
        add(m.group(2))

    # "more commonly known as Z" → "Z"
    m = COMMON_KNOWN_AS_RE.search(base)
    if m:
        add(m.group(1))

    # "Secretary of State for X acting through Y" → "Y"
    m = SOS_ACTING_THROUGH_RE.match(base)
    if m:
        add(m.group(1))
    # "Secretary of State for X" → "X"
    m = SOS_FOR_RE.match(base)
    if m:
        add(m.group(1))

    # "On behalf of X"
    m = ON_BEHALF_RE.match(base)
    if m:
        add(m.group(1))

    return out


def load_canonical_lookups(conn: sqlite3.Connection):
    """Build name+abbreviation → canonical_id lookup dicts."""
    name_to_ids = defaultdict(set)
    abbr_to_ids = defaultdict(set)
    norm_to_ids = defaultdict(set)
    canonical_names_by_id = {}

    for cid, cname, abbr in conn.execute(
        "SELECT canonical_id, canonical_name, abbreviation FROM canonical_buyers"
    ):
        canonical_names_by_id[cid] = cname
        if cname:
            name_to_ids[cname.lower().strip()].add(cid)
            norm_to_ids[_norm(cname)].add(cid)
        if abbr:
            abbr_to_ids[abbr.lower().strip()].add(cid)
            norm_to_ids[_norm(abbr)].add(cid)

    return name_to_ids, abbr_to_ids, norm_to_ids, canonical_names_by_id


def existing_aliases(conn: sqlite3.Connection):
    """Set of (alias_lower, canonical_id) tuples already in the alias table."""
    rows = conn.execute(
        "SELECT alias_lower, canonical_id FROM canonical_buyer_aliases"
    ).fetchall()
    return set((r[0], r[1]) for r in rows)


def main():
    p = argparse.ArgumentParser(description="Backfill buyer aliases against canonical entities")
    p.add_argument("--db", default=DEFAULT_DB, help="path to bid_intel.db")
    p.add_argument("--dry-run", action="store_true", help="report what would change without writing")
    p.add_argument("--sample", type=int, default=50, help="how many sample rows to show in reports")
    args = p.parse_args()

    if not os.path.exists(args.db):
        print(f"ERROR: database not found at {args.db}", file=sys.stderr)
        sys.exit(1)

    print(f"Database: {args.db}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'APPLY'}")

    conn = sqlite3.connect(args.db)
    try:
        name_to_ids, abbr_to_ids, norm_to_ids, canonical_names_by_id = load_canonical_lookups(conn)
        print(f"Canonical entities loaded: {len(canonical_names_by_id):,}")

        already = existing_aliases(conn)
        print(f"Existing alias rows: {len(already):,}")

        # Walk every raw buyer.
        # Includes buyers already mapped (their additional tidied variants may
        # still be useful as aliases). The (alias_lower, canonical_id) PK plus
        # `already` set guarantees no duplicates.
        rows = conn.execute("SELECT id, name, canonical_id FROM buyers").fetchall()
        print(f"Raw buyer rows: {len(rows):,}\n")

        new_aliases = []          # list of (alias_lower, alias_norm, canonical_id, raw_name, raw_id)
        ambiguous_rows = []       # raw names that match >1 canonical
        unmatched_rows = []       # raw names that didn't tidy into any canonical match
        backref_updates = []      # buyers.id → canonical_id (to set when canonical_id was NULL)

        for raw_id, raw_name, raw_canonical_id in rows:
            if not raw_name:
                continue

            cands = candidates_for(raw_name)
            matched_ids = set()
            matched_via = None

            for c in cands:
                cl = c.lower().strip()
                if cl in name_to_ids:
                    matched_ids |= name_to_ids[cl]
                    matched_via = matched_via or "name"
                if cl in abbr_to_ids:
                    matched_ids |= abbr_to_ids[cl]
                    matched_via = matched_via or "abbr"
                cn = _norm(c)
                if cn in norm_to_ids:
                    matched_ids |= norm_to_ids[cn]
                    matched_via = matched_via or "norm"

            if not matched_ids:
                unmatched_rows.append(raw_name)
                continue

            if len(matched_ids) > 1:
                names = sorted(canonical_names_by_id[i] for i in matched_ids)
                ambiguous_rows.append((raw_name, names))
                continue

            # Exactly one canonical match.
            cid = next(iter(matched_ids))

            # Register the raw name itself as an alias (lowercased + trimmed).
            alias_lower = raw_name.lower().strip()
            alias_norm = _norm(raw_name)
            key = (alias_lower, cid)
            if key not in already:
                new_aliases.append((alias_lower, alias_norm, cid, raw_name, raw_id))
                already.add(key)

            # Back-fill buyers.canonical_id if it was NULL or pointed elsewhere
            # at a previous (now superseded) match. We only set when NULL —
            # never overwrite an existing assignment, to preserve existing
            # work from load-canonical-buyers.py.
            if raw_canonical_id is None:
                backref_updates.append((raw_id, cid))

        # ── Report ───────────────────────────────────────────────────────
        print("=== REPORT ===")
        print(f"Raw names processed:       {len(rows):,}")
        print(f"New aliases to insert:     {len(new_aliases):,}")
        print(f"buyers.canonical_id back-fills: {len(backref_updates):,}")
        print(f"Ambiguous (>1 canonical):  {len(ambiguous_rows):,}")
        print(f"Still unmatched:           {len(unmatched_rows):,}")
        print()

        if new_aliases:
            print(f"--- Sample of new aliases (first {min(args.sample, len(new_aliases))}) ---")
            for alias_lower, _alias_norm, cid, raw_name, _raw_id in new_aliases[: args.sample]:
                cn = canonical_names_by_id.get(cid, "?")
                print(f"  '{raw_name[:60]}'  →  {cn[:50]}  [{cid}]")
            print()

        if ambiguous_rows:
            print(f"--- Sample of ambiguous matches (first {min(args.sample, len(ambiguous_rows))}) ---")
            for raw_name, names in ambiguous_rows[: args.sample]:
                shown = " | ".join(n[:30] for n in names[:4])
                more = f" + {len(names) - 4} more" if len(names) > 4 else ""
                print(f"  '{raw_name[:60]}'  →  {shown}{more}")
            print()

        if unmatched_rows:
            print(f"--- Sample of unmatched (first {min(args.sample, len(unmatched_rows))}) ---")
            for raw_name in unmatched_rows[: args.sample]:
                print(f"  '{raw_name[:80]}'")
            print()

        # ── Write ────────────────────────────────────────────────────────
        if args.dry_run:
            print("DRY-RUN: no changes written.")
            return

        if not new_aliases and not backref_updates:
            print("Nothing to write.")
            return

        ins_alias = conn.executemany(
            "INSERT OR IGNORE INTO canonical_buyer_aliases (alias_lower, alias_norm, canonical_id) VALUES (?, ?, ?)",
            [(a, n, c) for (a, n, c, _rn, _rid) in new_aliases],
        ).rowcount

        upd_buyers = 0
        for raw_id, cid in backref_updates:
            cur = conn.execute(
                "UPDATE buyers SET canonical_id = ? WHERE id = ? AND canonical_id IS NULL",
                (cid, raw_id),
            )
            upd_buyers += cur.rowcount

        conn.commit()
        print(f"Inserted aliases: {ins_alias:,}")
        print(f"Updated buyers.canonical_id rows: {upd_buyers:,}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
