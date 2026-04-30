"""Tests: framework tables created by schema.sql + db_utils migration."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
import db_utils

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _columns(conn, table):
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def test_frameworks_table_exists():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert "frameworks" in tables
    assert "framework_lots" in tables
    assert "framework_suppliers" in tables
    assert "framework_call_offs" in tables


def test_frameworks_required_columns():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "frameworks")
    for c in ("id", "reference_no", "name", "owner", "owner_type",
              "category", "expiry_date", "status", "source",
              "call_off_count", "call_off_value_total"):
        assert c in cols, f"Missing column: {c}"


def test_framework_lots_fk_column():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "framework_lots")
    assert "framework_id" in cols


def test_framework_suppliers_columns():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "framework_suppliers")
    for c in ("framework_id", "lot_id", "supplier_canonical_id",
              "supplier_name_raw", "status", "call_off_count"):
        assert c in cols, f"Missing column: {c}"


def test_framework_call_offs_columns():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "framework_call_offs")
    for c in ("framework_id", "notice_ocid", "buyer_canonical_id",
              "match_method", "match_confidence"):
        assert c in cols, f"Missing column: {c}"


def test_migration_idempotent():
    """Running init_schema twice must not raise or drop tables."""
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)  # second call must be safe
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert "frameworks" in tables
    assert "framework_lots" in tables
    assert "framework_suppliers" in tables
    assert "framework_call_offs" in tables


if __name__ == "__main__":
    for fn_name in [k for k in dir() if k.startswith("test_")]:
        fn = globals()[fn_name]
        try:
            fn()
            print(f"  PASS  {fn_name}")
        except AssertionError as e:
            print(f"  FAIL  {fn_name}: {e}")
    print("OK")
