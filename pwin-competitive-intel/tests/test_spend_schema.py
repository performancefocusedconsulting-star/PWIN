"""Tests: spend_files_state and spend_transactions tables created correctly."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
import db_utils

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _open():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    db_utils.init_schema(conn, SCHEMA_PATH)
    return conn


def test_spend_files_state_exists():
    conn = _open()
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "spend_files_state" in tables


def test_spend_transactions_exists():
    conn = _open()
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "spend_transactions" in tables


def test_spend_files_state_columns():
    conn = _open()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(spend_files_state)").fetchall()}
    for expected in ("id", "department", "year", "month", "entity_override",
                     "source_url", "format_id", "local_path", "file_checksum",
                     "row_count", "status", "error_message", "loaded_at"):
        assert expected in cols, f"Missing column: {expected}"


def test_spend_transactions_columns():
    conn = _open()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(spend_transactions)").fetchall()}
    for expected in ("id", "source_file_id", "department_family", "raw_entity",
                     "raw_supplier_name", "amount", "payment_date", "expense_type",
                     "expense_area", "canonical_sub_org_id", "canonical_supplier_id",
                     "ingested_at"):
        assert expected in cols, f"Missing column: {expected}"


def test_spend_files_state_default_status():
    conn = _open()
    conn.execute(
        "INSERT INTO spend_files_state (id, department, year, month, source_url, format_id) "
        "VALUES ('abc123', 'home-office', 2025, 1, 'https://example.com/file.csv', 'home-office-v1')"
    )
    row = conn.execute("SELECT status FROM spend_files_state WHERE id='abc123'").fetchone()
    assert row["status"] == "pending"


def test_migrate_schema_idempotent():
    conn = _open()
    db_utils._migrate_schema(conn)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "spend_files_state" in tables
    assert "spend_transactions" in tables


if __name__ == "__main__":
    for fn_name in [k for k in dir() if k.startswith("test_")]:
        fn = globals()[fn_name]
        fn()
        print(f"  PASS  {fn_name}")
    print("OK")
