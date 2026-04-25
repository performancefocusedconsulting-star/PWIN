#!/usr/bin/env python3
"""
Fuzzy-match unmatched buyer rows to the canonical buyer glossary.

Why this exists
---------------
The existing matcher (load-canonical-buyers.py) uses exact + normalised alias
matches and gets ~38% coverage on the older Find a Tender data and 0% on the
newly loaded Contracts Finder data. Many unmatched buyers ARE on the glossary,
just spelled differently:
  "DfE" / "Dept for Education"     → "Department for Education"
  "MFT"                            → "Manchester University NHS Foundation Trust"
  "London Borough Hillingdon"      → "London Borough of Hillingdon"

This script computes a fuzzy similarity score between each unmatched buyer
name and every canonical alias, and proposes matches above a threshold.

By default it ONLY runs in dry-run mode and writes nothing. The user reviews
the preview CSVs and decides whether to apply.

Run:
  .venv/Scripts/python.exe agent/fuzzy-match-buyers.py --threshold 90
  .venv/Scripts/python.exe agent/fuzzy-match-buyers.py --threshold 90 --apply
"""
from __future__ import annotations

import argparse
import csv
import re
import sqlite3
import sys
import time
from pathlib import Path

# Windows console defaults to cp1252 and chokes on Unicode chars in publisher
# data (e.g. narrow no-break space  ). Force UTF-8 stdout.
sys.stdout.reconfigure(encoding="utf-8")

from rapidfuzz import fuzz, process

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"
LOG_DIR = Path(__file__).parent.parent / "logs"

# ─────────────────────────────────────────────────────────────────────────────
# Normalisation — applied to both the unmatched name and each candidate alias.
# Same logic for both sides so they meet on equal ground.
# ─────────────────────────────────────────────────────────────────────────────

_PUNCT = re.compile(r"[^\w\s]")
_WS = re.compile(r"\s+")
_THE_OF = re.compile(r"\b(the|of|for|and)\b")

# Common org-type abbreviations to expand on the input side so they meet the
# canonical "long form" spelling on the alias side.
_ABBREV = {
    "dept": "department",
    "depts": "departments",
    "govt": "government",
    "co": "council",
    "cncl": "council",
    "uni": "university",
    "ft": "foundation trust",
    "nhs ft": "nhs foundation trust",
    "ltd": "limited",
    "plc": "public limited company",
}


def normalise(s: str) -> str:
    if not s:
        return ""
    out = s.lower().strip()
    # Expand whole-word abbreviations first
    for short, long in _ABBREV.items():
        out = re.sub(rf"\b{short}\b", long, out)
    out = _PUNCT.sub(" ", out)
    out = _THE_OF.sub(" ", out)
    out = _WS.sub(" ", out).strip()
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Match
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=int, default=90,
                    help="Minimum match score 0-100 (default 90)")
    ap.add_argument("--apply", action="store_true",
                    help="Write canonical_id back to the buyers table. Default is dry-run.")
    ap.add_argument("--source", default=None,
                    help="Limit to one data source: 'cf' or 'fts' (default: both)")
    args = ap.parse_args()

    LOG_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Load all canonical aliases into a list (alias_norm-side) and a parallel
    # list of (canonical_id, canonical_name, raw_alias) for context.
    print("Loading canonical aliases...")
    aliases = c.execute("""
        SELECT a.alias_norm, a.canonical_id, b.canonical_name, a.alias_lower
        FROM canonical_buyer_aliases a
        JOIN canonical_buyers b ON b.canonical_id = a.canonical_id
    """).fetchall()
    print(f"  {len(aliases):,} aliases across {len({a[1] for a in aliases}):,} canonical entities")

    # Pre-normalise alias side once, keep parallel context list
    alias_norms: list[str] = []
    alias_meta: list[tuple[str, str, str]] = []  # (canonical_id, canonical_name, raw_alias)
    seen = set()
    for raw_norm, cid, cname, raw_lower in aliases:
        n = normalise(raw_norm or raw_lower or "")
        if not n:
            continue
        # Keep only the first appearance of each (norm, canonical_id) pair —
        # the same alias may appear under multiple canonicals (rare).
        key = (n, cid)
        if key in seen:
            continue
        seen.add(key)
        alias_norms.append(n)
        alias_meta.append((cid, cname, raw_lower or raw_norm or ""))
    print(f"  {len(alias_norms):,} unique normalised aliases for scoring")

    # Load unmatched buyer rows
    where = "WHERE canonical_id IS NULL"
    if args.source:
        where += f" AND data_source = '{args.source}'"
    print(f"Loading unmatched buyers ({where})...")
    rows = c.execute(f"""
        SELECT id, name, data_source FROM buyers {where}
    """).fetchall()
    print(f"  {len(rows):,} unmatched buyer rows to score")

    # Match each unmatched name against all aliases
    print(f"\nScoring all unmatched buyers (one pass, reports at 95/90/85)...")
    t0 = time.time()
    # all_scored is the master list — one row per unmatched buyer
    all_scored = []  # (buyer_id, raw_name, source, score, canonical_id, canonical_name, matched_alias)
    for i, (buyer_id, raw_name, source) in enumerate(rows, 1):
        norm = normalise(raw_name or "")
        if not norm:
            continue
        best = process.extractOne(
            norm, alias_norms, scorer=fuzz.WRatio, score_cutoff=0
        )
        if best is None:
            continue
        matched_alias_norm, score, idx = best
        cid, cname, raw_alias = alias_meta[idx]
        all_scored.append((buyer_id, raw_name, source, score, cid, cname, raw_alias))
        if i % 5000 == 0:
            print(f"  scored {i:,} of {len(rows):,}  ({time.time()-t0:.1f}s)")

    print(f"  scoring complete in {time.time()-t0:.1f}s")
    print()

    # Sort once for reporting
    all_scored.sort(key=lambda r: (-r[3], r[1] or ""))

    def _safe(s: str) -> str:
        # belt + braces vs surprise unicode in publisher data
        return (s or "").encode("utf-8", "replace").decode("utf-8")

    for thr in (95, 90, 85):
        matches = [m for m in all_scored if m[3] >= thr]
        near_misses = [m for m in all_scored if thr - 5 <= m[3] < thr][:5]
        by_source = {}
        for m in matches:
            by_source[m[2]] = by_source.get(m[2], 0) + 1

        print(f"=== Threshold {thr} ===")
        print(f"  Would match : {len(matches):,} buyers ({100*len(matches)/max(len(rows),1):.1f}%)")
        for src, n in sorted(by_source.items()):
            total_src = sum(1 for r in rows if r[2] == src)
            print(f"    {src}: {n:,} of {total_src:,} ({100*n/max(total_src,1):.1f}%)")
        print(f"  Still unmatched: {len(rows) - len(matches):,}")

        print(f"  5 LOWEST-scoring matches still above threshold (these define the floor):")
        for m in matches[-5:]:
            print(f"    {m[3]:>5.1f}  '{_safe(m[1])[:55]}'  ->  '{_safe(m[5])[:55]}'")

        print(f"  5 NEAR-MISSES just below threshold (sanity check what we'd reject):")
        for m in near_misses:
            print(f"    {m[3]:>5.1f}  '{_safe(m[1])[:55]}'  ->  '{_safe(m[5])[:55]}'")

        # CSV preview per threshold
        csv_path = LOG_DIR / f"buyer-fuzzy-preview-{thr}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["buyer_id", "raw_name", "data_source", "score", "canonical_id", "canonical_name", "matched_alias"])
            for m in matches:
                w.writerow([_safe(str(x)) for x in m])
        print(f"  Preview written: {csv_path}")
        print()

    if args.apply:
        matches = [m for m in all_scored if m[3] >= args.threshold]
        print(f"\n--apply set: writing canonical_id to {len(matches):,} buyer rows at threshold {args.threshold}...")
        c.executemany(
            "UPDATE buyers SET canonical_id = ? WHERE id = ? AND canonical_id IS NULL",
            [(m[4], m[0]) for m in matches]
        )
        conn.commit()
        print("Written.")
    else:
        print(f"\n(dry-run; rerun with --apply --threshold N to write back at threshold N)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
