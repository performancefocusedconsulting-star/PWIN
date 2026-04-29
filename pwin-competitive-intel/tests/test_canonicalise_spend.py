"""Tests: canonicalise_spend.py — buyer and supplier matching."""
import importlib.util
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

spec = importlib.util.spec_from_file_location(
    "canonicalise_spend",
    Path(__file__).parent.parent / "agent" / "canonicalise_spend.py",
)
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)


# ── Norm tests ───────────────────────────────────────────────────────────────

def test_norm_lowercases():
    assert cs._norm("BORDER FORCE") == "border force"


def test_norm_ampersand():
    assert cs._norm("HM Courts & Tribunals Service") == "hm courts and tribunals service"


def test_norm_ltd():
    assert cs._norm("Acme Ltd.") == "acme limited"


def test_norm_plc():
    assert cs._norm("Serco PLC") == "serco limited"


def test_norm_strips_punctuation():
    assert cs._norm("O'Brien, Smith") == "o brien smith"


# ── Integration: in-memory DB ────────────────────────────────────────────────

def _make_db() -> sqlite3.Connection:
    """Create minimal in-memory DB with canonical tables + spend tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE canonical_buyers (
            canonical_id TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL
        );
        CREATE TABLE canonical_buyer_aliases (
            alias_lower TEXT,
            alias_norm  TEXT,
            canonical_id TEXT
        );
        CREATE TABLE canonical_suppliers (
            canonical_id   TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL,
            member_count   INTEGER,
            ch_numbers     TEXT,
            distinct_ch_count INTEGER,
            source         TEXT,
            created_at     TEXT
        );
        CREATE TABLE spend_files_state (
            id TEXT PRIMARY KEY, department TEXT, year INTEGER, month INTEGER,
            entity_override TEXT, source_url TEXT, format_id TEXT,
            local_path TEXT, file_checksum TEXT, row_count INTEGER,
            status TEXT DEFAULT 'pending', error_message TEXT, loaded_at TEXT
        );
        CREATE TABLE spend_transactions (
            id TEXT PRIMARY KEY,
            source_file_id TEXT,
            department_family TEXT,
            raw_entity TEXT,
            raw_supplier_name TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT,
            expense_type TEXT,
            expense_area TEXT,
            canonical_sub_org_id TEXT,
            canonical_supplier_id TEXT,
            ingested_at TEXT DEFAULT (datetime('now'))
        );
    """)
    # Seed a canonical buyer and alias
    conn.execute("INSERT INTO canonical_buyers VALUES ('border-force', 'Border Force')")
    conn.execute("INSERT INTO canonical_buyer_aliases VALUES ('border force', 'border force', 'border-force')")
    # Seed a canonical supplier
    conn.execute("""INSERT INTO canonical_suppliers
        (canonical_id, canonical_name, member_count, ch_numbers, distinct_ch_count, source, created_at)
        VALUES ('GB-COH-12345678', 'serco limited', 5, '["12345678"]', 1, 'splink', '2026-01-01')""")
    conn.commit()
    return conn


def test_match_buyer_and_supplier():
    conn = _make_db()
    conn.execute("INSERT INTO spend_files_state (id, department, year, month, source_url, format_id) VALUES ('f1', 'home-office', 2025, 1, 'http://x', 'home-office-v1')")
    conn.execute("""INSERT INTO spend_transactions
        (id, source_file_id, department_family, raw_entity, raw_supplier_name, amount)
        VALUES ('t1', 'f1', 'home-office', 'Border Force', 'Serco PLC', 100000)""")
    conn.commit()

    cs.run(conn=conn, close_after=False)

    row = conn.execute("SELECT * FROM spend_transactions WHERE id='t1'").fetchone()
    assert row["canonical_sub_org_id"] == "border-force"
    assert row["canonical_supplier_id"] == "GB-COH-12345678"


def test_unmatched_stays_null():
    conn = _make_db()
    conn.execute("INSERT INTO spend_files_state (id, department, year, month, source_url, format_id) VALUES ('f2', 'home-office', 2025, 2, 'http://y', 'home-office-v1')")
    conn.execute("""INSERT INTO spend_transactions
        (id, source_file_id, department_family, raw_entity, raw_supplier_name, amount)
        VALUES ('t2', 'f2', 'home-office', 'Unknown Entity XYZ', 'NoName Corp', 50000)""")
    conn.commit()

    cs.run(conn=conn, close_after=False)

    row = conn.execute("SELECT * FROM spend_transactions WHERE id='t2'").fetchone()
    assert row["canonical_sub_org_id"] is None
    assert row["canonical_supplier_id"] is None


def test_idempotent():
    conn = _make_db()
    conn.execute("INSERT INTO spend_files_state (id, department, year, month, source_url, format_id) VALUES ('f3', 'home-office', 2025, 3, 'http://z', 'home-office-v1')")
    conn.execute("""INSERT INTO spend_transactions
        (id, source_file_id, department_family, raw_entity, raw_supplier_name, amount)
        VALUES ('t3', 'f3', 'home-office', 'Border Force', 'Serco PLC', 75000)""")
    conn.commit()

    cs.run(conn=conn, close_after=False)
    cs.run(conn=conn, close_after=False)   # second run — should be a no-op

    row = conn.execute("SELECT * FROM spend_transactions WHERE id='t3'").fetchone()
    assert row["canonical_sub_org_id"] == "border-force"


def test_entity_override_match():
    """entity_override values from the catalogue (e.g. 'hm-courts-and-tribunals-service')
    become raw_entity on MoJ rows — they should match by alias_norm lookup."""
    conn = _make_db()
    conn.execute("INSERT INTO canonical_buyers VALUES ('hm-courts-and-tribunals-service', 'HM Courts and Tribunals Service')")
    conn.execute("INSERT INTO canonical_buyer_aliases VALUES ('hm courts and tribunals service', 'hm courts and tribunals service', 'hm-courts-and-tribunals-service')")
    conn.commit()

    conn.execute("INSERT INTO spend_files_state (id, department, year, month, source_url, format_id) VALUES ('f4', 'ministry-of-justice', 2025, 1, 'http://a', 'ministry-of-justice-v1')")
    conn.execute("""INSERT INTO spend_transactions
        (id, source_file_id, department_family, raw_entity, raw_supplier_name, amount)
        VALUES ('t4', 'f4', 'ministry-of-justice', 'HM Courts & Tribunals Service', 'NoName', 30000)""")
    conn.commit()

    cs.run(conn=conn, close_after=False)

    row = conn.execute("SELECT canonical_sub_org_id FROM spend_transactions WHERE id='t4'").fetchone()
    assert row["canonical_sub_org_id"] == "hm-courts-and-tribunals-service"


if __name__ == "__main__":
    for fn_name in sorted(k for k in dir() if k.startswith("test_")):
        fn = globals()[fn_name]
        fn()
        print(f"  PASS  {fn_name}")
    print("OK")
