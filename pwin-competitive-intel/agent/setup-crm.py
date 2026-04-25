#!/usr/bin/env python3
"""
Create ~/.pwin/crm.db from db/crm-schema.sql.

Usage:
    python agent/setup-crm.py           # create if not exists
    python agent/setup-crm.py --reset   # drop and recreate (prompts for confirmation)
    python agent/setup-crm.py --force   # drop and recreate without prompting
    python agent/setup-crm.py --status  # print DB stats without modifying
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH     = Path.home() / ".pwin" / "crm.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "crm-schema.sql"


def _stats(conn):
    tables = ["organisations", "contacts", "opportunities", "interactions", "actions"]
    for t in tables:
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t:<20} {n:>6} rows")
        except Exception:
            print(f"  {t:<20}  (missing)")


def main():
    args = sys.argv[1:]

    if "--status" in args:
        if not DB_PATH.exists():
            print(f"CRM DB not found at {DB_PATH}")
            return
        conn = sqlite3.connect(DB_PATH)
        print(f"CRM DB: {DB_PATH}")
        _stats(conn)
        conn.close()
        return

    if "--reset" in args or "--force" in args:
        if DB_PATH.exists():
            if "--force" not in args:
                confirm = input(f"DELETE {DB_PATH} and recreate? Type YES to confirm: ")
                if confirm.strip() != "YES":
                    print("Aborted.")
                    return
            DB_PATH.unlink()
            print(f"Deleted {DB_PATH}")

    if DB_PATH.exists():
        print(f"CRM DB already exists at {DB_PATH}")
        print("Use --reset to drop and recreate (WARNING: destroys all data)")
        print("Use --force to skip the confirmation prompt")
        print("Use --status to inspect row counts")
        return

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    conn.commit()
    print(f"CRM DB created at {DB_PATH}")
    _stats(conn)
    conn.close()


if __name__ == "__main__":
    main()
