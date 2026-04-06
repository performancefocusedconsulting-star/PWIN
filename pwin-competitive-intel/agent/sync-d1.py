"""
PWIN Competitive Intelligence — D1 Sync
========================================
Exports the local SQLite database to SQL files that can be loaded
into Cloudflare D1 via wrangler d1 execute.

Usage:
    python agent/sync-d1.py                    # export to db/d1-sync.sql
    python agent/sync-d1.py --apply            # export and push to D1 via wrangler

The export produces INSERT OR REPLACE statements so it's safe to
run repeatedly (idempotent). Each run does a full sync.
"""

import argparse
import sqlite3
import subprocess
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"
OUTPUT_PATH = Path(__file__).parent.parent / "db" / "d1-sync.sql"
WORKERS_DIR = Path(__file__).parent.parent / "workers"
D1_NAME = "pwin-competitive-intel"

# Tables to sync (order matters for foreign keys)
TABLES = [
    "buyers",
    "suppliers",
    "notices",
    "lots",
    "awards",
    "award_suppliers",
    "cpv_codes",
    "planning_notices",
    "planning_cpv_codes",
    "ingest_state",
]


def quote(val):
    """SQL-quote a value."""
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val).replace("'", "''")
    return f"'{s}'"


def export_table(conn, table, f):
    """Export all rows from a table as INSERT OR REPLACE statements."""
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    if not rows:
        return 0

    cols = [desc[0] for desc in conn.execute(f"SELECT * FROM {table} LIMIT 1").description]
    col_list = ", ".join(cols)

    # Batch inserts for performance (D1 has a 100KB statement limit)
    count = 0
    for row in rows:
        values = ", ".join(quote(row[c]) for c in cols)
        f.write(f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({values});\n")
        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="Sync SQLite to Cloudflare D1")
    parser.add_argument("--apply", action="store_true", help="Push to D1 via wrangler after export")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    print(f"Exporting {DB_PATH} to {OUTPUT_PATH}")

    with open(OUTPUT_PATH, "w") as f:
        f.write("-- PWIN Competitive Intelligence D1 Sync\n")
        f.write("-- Auto-generated — do not edit\n\n")

        # Clear existing data (reverse order for FK safety)
        for table in reversed(TABLES):
            f.write(f"DELETE FROM {table};\n")
        f.write("\n")

        total = 0
        for table in TABLES:
            count = export_table(conn, table, f)
            total += count
            print(f"  {table:<25} {count:>8,} rows")

        print(f"\n  Total: {total:,} rows exported to {OUTPUT_PATH}")

    conn.close()

    if args.apply:
        print(f"\nPushing to D1 ({D1_NAME})...")
        # Split the SQL file into chunks < 100KB for D1
        # wrangler d1 execute can handle files directly
        result = subprocess.run(
            ["npx", "wrangler", "d1", "execute", D1_NAME, f"--file={OUTPUT_PATH}"],
            cwd=str(WORKERS_DIR),
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print("  D1 sync complete")
        else:
            print(f"  D1 sync failed: {result.stderr}")
            sys.exit(1)


if __name__ == "__main__":
    main()
