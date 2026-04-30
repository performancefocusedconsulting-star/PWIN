"""Tests: consolidate_frameworks.py — merge logic and gap report."""
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

spec = importlib.util.spec_from_file_location(
    "consolidate_frameworks",
    Path(__file__).parent.parent / "agent" / "consolidate_frameworks.py",
)
try:
    cf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cf)
except Exception:
    cf = None

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    # Remove UNIQUE constraint on reference_no to allow test duplicates
    schema_text = schema_text.replace("reference_no             TEXT UNIQUE,", "reference_no             TEXT,")
    conn.executescript(schema_text)
    conn.commit()
    return conn


def _insert_fw(conn, name, reference_no=None, source="contracts_only"):
    conn.execute("""
        INSERT INTO frameworks (name, owner, reference_no, source)
        VALUES (?, 'unknown', ?, ?)
    """, (name, reference_no, source))
    conn.commit()


def test_merge_by_reference_no():
    """Two records with same reference_no should merge — source becomes 'both'."""
    assert cf is not None
    conn = _make_db()
    _insert_fw(conn, "Technology Services 3", "RM6100", "contracts_only")
    _insert_fw(conn, "Technology Services 3 (CCS)", "RM6100", "catalogue_only")
    cf.consolidate(conn)
    rows = conn.execute(
        "SELECT * FROM frameworks WHERE reference_no='RM6100'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["source"] == "both"


def test_merge_by_name_similarity():
    """Two records with same normalised name, no reference_no, should merge."""
    conn = _make_db()
    _insert_fw(conn, "Network Services 3", None, "contracts_only")
    _insert_fw(conn, "Network Services 3", None, "catalogue_only")
    cf.consolidate(conn)
    rows = conn.execute(
        "SELECT * FROM frameworks WHERE lower(name)='network services 3'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["source"] == "both"


def test_no_merge_different_frameworks():
    """Two distinct frameworks must remain as separate records."""
    conn = _make_db()
    _insert_fw(conn, "Tech Services 3", "RM6100", "contracts_only")
    _insert_fw(conn, "Network Services 3", "RM6116", "catalogue_only")
    cf.consolidate(conn)
    count = conn.execute("SELECT COUNT(*) FROM frameworks").fetchone()[0]
    assert count == 2


def test_gap_report_contracts_only():
    conn = _make_db()
    _insert_fw(conn, "TEPAS 2", None, "contracts_only")
    _insert_fw(conn, "Tech Services 3", "RM6100", "catalogue_only")
    cf.consolidate(conn)
    report = cf.build_gap_report(conn)
    assert report["contracts_only_count"] == 1
    assert report["catalogue_only_count"] == 1
    assert report["both_count"] == 0
    assert any(r["name"] == "TEPAS 2" for r in report["contracts_only"])


def test_gap_report_both():
    conn = _make_db()
    _insert_fw(conn, "Tech Services 3", "RM6100", "contracts_only")
    _insert_fw(conn, "Tech Services 3", "RM6100", "catalogue_only")
    cf.consolidate(conn)
    report = cf.build_gap_report(conn)
    assert report["both_count"] == 1
    assert report["contracts_only_count"] == 0


def test_merge_three_records_same_source_keeps_source():
    """Three contracts_only records for same ref should merge to contracts_only, not 'both'."""
    conn = _make_db()
    for _ in range(3):
        _insert_fw(conn, "Tech Services 3", "RM6100", "contracts_only")
    cf.consolidate(conn)
    row = conn.execute("SELECT source FROM frameworks WHERE reference_no='RM6100'").fetchone()
    assert row is not None
    assert row["source"] == "contracts_only"
    count = conn.execute("SELECT COUNT(*) FROM frameworks").fetchone()[0]
    assert count == 1
