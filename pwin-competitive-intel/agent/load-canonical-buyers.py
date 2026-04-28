#!/usr/bin/env python3
"""
Load the canonical buyer glossary into the FTS database.

Creates two new tables and adds a column to the existing buyers table:

  canonical_buyers       — one row per canonical entity (1,928+)
  canonical_buyer_aliases — one row per alias for fast lookup
  buyers.canonical_id    — FK mapping each raw buyer to its canonical entity

Matching logic:
  1. Exact alias match (lowercased buyer name → alias)
  2. Normalised alias match (collapse &/and, Ltd/Limited, punctuation)
  3. Prefix match for known patterns (NHS Supply Chain, HealthTrust Europe)
  4. Remaining buyers left as canonical_id = NULL (unmatched)

Hierarchy support:
  canonical_buyers.parent_canonical_id enables recursive CTE traversal.
  Example: "all MoD awards" traverses MoD → DE&S → DSTL → DIO → ...

Usage:
    python3 agent/load-canonical-buyers.py
    python3 agent/load-canonical-buyers.py --glossary /path/to/glossary.json
    python3 agent/load-canonical-buyers.py --dry-run   # report stats, don't write

Idempotent — safe to re-run after glossary updates.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

DEFAULT_GLOSSARY = os.path.join(os.path.expanduser("~"), ".pwin", "platform", "buyer-canonical-glossary.json")
DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "bid_intel.db")

# Known prefix-match patterns: any buyer name starting with these strings
# maps to the given canonical_id regardless of what follows.
PREFIX_RULES = [
    ("nhs supply chain", "nhs-supply-chain"),
    ("healthtrust europe llp (hte)", "healthtrust-europe"),
    ("healthtrust europe llp", "healthtrust-europe"),
    ("the minister for the cabinet office acting through crown commercial", "crown-commercial-service"),
    ("minister for the cabinet office acting through crown commercial", "crown-commercial-service"),
    ("the common services agency", "nhs-national-services-scotland"),
]


def norm(s: str) -> str:
    """Normalise a name for matching.

    Rules (all applied lowercased):
      1. Lower + strip
      2. & ↔ and
      3. Ltd / Ltd. / PLC / PLC. ↔ Limited
      4. Drop leading 'the '
      5. Drop trailing decorative suffixes (' company limited', ' (CCS)', etc.)
      6. Drop trailing portal/eTendering noise
      7. Strip punctuation, collapse whitespace
    """
    s = (s or "").lower().strip()
    s = re.sub(r"\s*[\&]\s*", " and ", s)
    s = re.sub(r"\bplc\b\.?", "limited", s)
    s = re.sub(r"\bltd\b\.?", "limited", s)
    s = re.sub(r"^the\s+", "", s)
    s = re.sub(r"\s+company\s+limited\s*$", "", s)
    s = re.sub(r"\s+[-–—]\s+(e[- ]?tendering(?:\s+system)?|tendering\s+system|portal|esourcing|procurement\s+department|procurement\s+services?).*$", "", s)
    s = re.sub(r"\s+e[- ]?tendering(?:\s+system|\s+portal)?\s*$", "", s)
    s = re.sub(r"\s+network\s+e[- ]?tendering(?:\s+portal)?\s*$", "", s)
    s = re.sub(r"[,\.\(\)\-\'\"]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def create_tables(conn: sqlite3.Connection):
    """Create the canonical tables (idempotent)."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS canonical_buyers (
            canonical_id            TEXT PRIMARY KEY,
            canonical_name          TEXT NOT NULL,
            abbreviation            TEXT,
            type                    TEXT,
            subtype                 TEXT,
            parent_canonical_id     TEXT REFERENCES canonical_buyers(canonical_id),
            source                  TEXT,
            status                  TEXT DEFAULT 'active',
            ons_code                TEXT,
            ods_id                  TEXT,
            gov_uk_url              TEXT,
            loaded_at               TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_cb_parent ON canonical_buyers(parent_canonical_id);
        CREATE INDEX IF NOT EXISTS idx_cb_type ON canonical_buyers(type);
        CREATE INDEX IF NOT EXISTS idx_cb_source ON canonical_buyers(source);

        CREATE TABLE IF NOT EXISTS canonical_buyer_aliases (
            alias_lower             TEXT NOT NULL,
            alias_norm              TEXT NOT NULL,
            canonical_id            TEXT NOT NULL REFERENCES canonical_buyers(canonical_id),
            PRIMARY KEY (alias_lower, canonical_id)
        );

        CREATE INDEX IF NOT EXISTS idx_cba_norm ON canonical_buyer_aliases(alias_norm);
        CREATE INDEX IF NOT EXISTS idx_cba_canonical ON canonical_buyer_aliases(canonical_id);
    """)

    # Add canonical_id column to buyers if not present
    cols = [r[1] for r in conn.execute("PRAGMA table_info(buyers)").fetchall()]
    if "canonical_id" not in cols:
        conn.execute("ALTER TABLE buyers ADD COLUMN canonical_id TEXT REFERENCES canonical_buyers(canonical_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_buyers_canonical ON buyers(canonical_id)")
        print("  Added canonical_id column to buyers table")
    else:
        print("  canonical_id column already exists on buyers table")


def load_glossary(conn: sqlite3.Connection, glossary_path: str) -> int:
    """Load canonical entities and aliases from the glossary JSON."""
    with open(glossary_path) as f:
        glossary = json.load(f)

    entities = glossary.get("entities", [])
    print(f"  Loading {len(entities)} canonical entities from {glossary_path}")

    # Clear and reload (idempotent)
    conn.execute("DELETE FROM canonical_buyer_aliases")
    conn.execute("DELETE FROM canonical_buyers")

    # First pass: insert all entities (parent_canonical_id may reference forward)
    for e in entities:
        parent = None
        if e.get("parent_ids"):
            parent = e["parent_ids"][0]  # Use first parent

        conn.execute("""
            INSERT OR REPLACE INTO canonical_buyers
            (canonical_id, canonical_name, abbreviation, type, subtype,
             parent_canonical_id, source, status, ons_code, ods_id, gov_uk_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e["canonical_id"],
            e.get("canonical_name", ""),
            e.get("abbreviation"),
            e.get("type"),
            e.get("subtype"),
            parent,
            e.get("source"),
            e.get("status", "active"),
            e.get("ons_code"),
            e.get("ods_id"),
            e.get("gov_uk_url"),
        ))

    # Second pass: insert aliases
    alias_count = 0
    for e in entities:
        cid = e["canonical_id"]
        seen = set()
        for alias in e.get("aliases", []):
            al = alias.lower().strip()
            an = norm(alias)
            if al in seen:
                continue
            seen.add(al)
            conn.execute("""
                INSERT OR IGNORE INTO canonical_buyer_aliases (alias_lower, alias_norm, canonical_id)
                VALUES (?, ?, ?)
            """, (al, an, cid))
            alias_count += 1

    conn.commit()
    print(f"  Loaded {len(entities)} entities, {alias_count} aliases")
    return len(entities)


def run_matching(conn: sqlite3.Connection) -> dict:
    """Match raw buyers to canonical entities. Returns stats dict."""
    # Reset all canonical_id assignments
    conn.execute("UPDATE buyers SET canonical_id = NULL")

    # Build lookup dicts from the alias table
    alias_exact = {}  # lower → canonical_id
    alias_norm = {}   # normalised → canonical_id
    for row in conn.execute("SELECT alias_lower, alias_norm, canonical_id FROM canonical_buyer_aliases"):
        alias_exact.setdefault(row[0], row[2])
        alias_norm.setdefault(row[1], row[2])

    buyers = conn.execute("SELECT id, name FROM buyers").fetchall()
    stats = {"total": len(buyers), "exact": 0, "normalised": 0, "prefix": 0, "unmatched": 0}

    for buyer_id, name in buyers:
        nl = (name or "").lower().strip()
        canonical_id = None
        method = None

        # 1. Exact alias match
        if nl in alias_exact:
            canonical_id = alias_exact[nl]
            method = "exact"
            stats["exact"] += 1

        # 2. Normalised alias match
        if not canonical_id:
            nn = norm(name)
            if nn in alias_norm:
                canonical_id = alias_norm[nn]
                method = "normalised"
                stats["normalised"] += 1

        # 3. Prefix match for known patterns
        if not canonical_id:
            for prefix, cid in PREFIX_RULES:
                if nl.startswith(prefix):
                    canonical_id = cid
                    method = "prefix"
                    stats["prefix"] += 1
                    break

        if canonical_id:
            conn.execute("UPDATE buyers SET canonical_id = ? WHERE id = ?", (canonical_id, buyer_id))
        else:
            stats["unmatched"] += 1

    conn.commit()
    return stats


def validate(conn: sqlite3.Connection):
    """Run validation queries and print results."""
    print("\n=== VALIDATION ===")

    # Coverage on £1m+ universe
    r = conn.execute("""
        SELECT
            COUNT(DISTINCT a.id) total_awards,
            COUNT(DISTINCT CASE WHEN b.canonical_id IS NOT NULL THEN a.id END) matched_awards
        FROM awards a JOIN notices n ON a.ocid = n.ocid JOIN buyers b ON n.buyer_id = b.id
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6
    """).fetchone()
    total, matched = r
    print(f"  £1m+ awards coverage: {matched:,} of {total:,} ({100*matched/total:.1f}%)")

    # MoD hierarchy test
    print(f"\n  MoD hierarchy traversal:")
    mod_rows = conn.execute("""
        WITH RECURSIVE descendants AS (
            SELECT canonical_id, canonical_name FROM canonical_buyers WHERE canonical_id = 'ministry-of-defence'
            UNION ALL
            SELECT cb.canonical_id, cb.canonical_name FROM canonical_buyers cb
            JOIN descendants d ON cb.parent_canonical_id = d.canonical_id
        )
        SELECT d.canonical_name, COUNT(DISTINCT a.id) awards, SUM(a.value_amount_gross) total_value
        FROM descendants d
        JOIN buyers b ON b.canonical_id = d.canonical_id
        JOIN notices n ON n.buyer_id = b.id
        JOIN awards a ON a.ocid = n.ocid
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6
        GROUP BY d.canonical_id
        ORDER BY total_value DESC
        LIMIT 10
    """).fetchall()
    for name, awards, val in mod_rows:
        print(f"    {awards:>5} awards  £{(val or 0)/1e6:>8,.0f}m  {name[:50]}")

    mod_total = conn.execute("""
        WITH RECURSIVE descendants AS (
            SELECT canonical_id FROM canonical_buyers WHERE canonical_id = 'ministry-of-defence'
            UNION ALL
            SELECT cb.canonical_id FROM canonical_buyers cb
            JOIN descendants d ON cb.parent_canonical_id = d.canonical_id
        )
        SELECT COUNT(DISTINCT a.id), SUM(a.value_amount_gross)
        FROM descendants d JOIN buyers b ON b.canonical_id = d.canonical_id
        JOIN notices n ON n.buyer_id = b.id JOIN awards a ON a.ocid = n.ocid
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6
    """).fetchone()
    print(f"    TOTAL: {mod_total[0]:,} awards, £{(mod_total[1] or 0)/1e6:,.0f}m")

    # Top 10 canonical buyers by award count
    print(f"\n  Top 10 canonical buyers by £1m+ award count:")
    for r in conn.execute("""
        SELECT cb.canonical_name, COUNT(DISTINCT a.id) awards
        FROM buyers b JOIN canonical_buyers cb ON b.canonical_id = cb.canonical_id
        JOIN notices n ON n.buyer_id = b.id JOIN awards a ON a.ocid = n.ocid
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6
        GROUP BY cb.canonical_id ORDER BY awards DESC LIMIT 10
    """):
        print(f"    {r[1]:>5}  {r[0][:60]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--glossary", default=DEFAULT_GLOSSARY)
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--dry-run", action="store_true", help="Report stats without writing to DB")
    args = parser.parse_args()

    if not os.path.exists(args.glossary):
        print(f"ERROR: glossary not found at {args.glossary}")
        print("Run: python3 pwin-platform/scripts/seed-canonical-buyers.py")
        sys.exit(1)

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys = OFF")  # Temporarily off for bulk load
    conn.execute("PRAGMA journal_mode = WAL")

    print("Step 1: Creating tables...")
    create_tables(conn)

    print("\nStep 2: Loading glossary...")
    load_glossary(conn, args.glossary)

    if args.dry_run:
        print("\n[DRY RUN] Skipping matching and validation")
        conn.close()
        return

    print("\nStep 3: Matching raw buyers to canonical entities...")
    stats = run_matching(conn)
    print(f"  Total buyers : {stats['total']:,}")
    print(f"  Exact match  : {stats['exact']:,} ({100*stats['exact']/stats['total']:.1f}%)")
    print(f"  Normalised   : {stats['normalised']:,} ({100*stats['normalised']/stats['total']:.1f}%)")
    print(f"  Prefix match : {stats['prefix']:,} ({100*stats['prefix']/stats['total']:.1f}%)")
    print(f"  Unmatched    : {stats['unmatched']:,} ({100*stats['unmatched']/stats['total']:.1f}%)")

    validate(conn)

    conn.execute("PRAGMA foreign_keys = ON")
    conn.close()
    print(f"\nDone. Database updated at {args.db}")


if __name__ == "__main__":
    main()
