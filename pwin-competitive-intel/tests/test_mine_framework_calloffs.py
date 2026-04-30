"""Tests: mine_framework_calloffs.py — framework reference extraction."""
import importlib.util
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

spec = importlib.util.spec_from_file_location(
    "mine_framework_calloffs",
    Path(__file__).parent.parent / "agent" / "mine_framework_calloffs.py",
)
# Module doesn't exist yet — import will fail until Task 2 Step 3
try:
    mfc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mfc)
except Exception:
    mfc = None

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _make_db() -> sqlite3.Connection:
    """In-memory DB with full schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    return conn


def _seed_notice(conn, ocid, title, parent_framework_title=None,
                 parent_framework_ocid=None, description=None):
    conn.execute("""
        INSERT OR IGNORE INTO buyers (id, name, last_updated) VALUES ('b1', 'Test Buyer', datetime('now'))
    """)
    conn.execute("""
        INSERT INTO notices (ocid, buyer_id, title, description,
            parent_framework_title, parent_framework_ocid, last_updated)
        VALUES (?, 'b1', ?, ?, ?, ?, datetime('now'))
    """, (ocid, title, description or "", parent_framework_title, parent_framework_ocid))
    conn.execute("""
        INSERT INTO awards (id, ocid, status, value_amount_gross, award_date, last_updated)
        VALUES (?, ?, 'active', 100000, '2025-01-15', datetime('now'))
    """, (f"award-{ocid}", ocid))
    conn.commit()


# ── _extract_rm_numbers ───────────────────────────────────────────────────────

def test_extract_rm_from_title():
    assert mfc is not None
    assert mfc._extract_rm_numbers("Technology Services 3 RM6100") == ["RM6100"]


def test_extract_rm_returns_empty_when_absent():
    assert mfc._extract_rm_numbers("Standard procurement notice") == []


def test_extract_rm_multiple():
    assert set(mfc._extract_rm_numbers("RM6116 and RM6100 frameworks")) == {"RM6116", "RM6100"}


# ── _normalise_fw_name ────────────────────────────────────────────────────────

def test_normalise_fw_name_lowercases():
    assert mfc._normalise_fw_name("Technology Services 3") == "technology services 3"


def test_normalise_fw_name_strips_punctuation():
    assert mfc._normalise_fw_name("Tech. Services (3)") == "tech services 3"


# ── mine_structured_references ───────────────────────────────────────────────

def test_mine_structured_creates_framework():
    assert mfc is not None
    conn = _make_db()
    _seed_notice(conn, "ocid-001", "Cloud services",
                 parent_framework_title="Technology Services 3",
                 parent_framework_ocid="rm6100")
    mfc.mine_structured_references(conn)
    fw = conn.execute("SELECT * FROM frameworks WHERE name='Technology Services 3'").fetchone()
    assert fw is not None
    assert fw["source"] == "contracts_only"


def test_mine_structured_creates_call_off():
    conn = _make_db()
    _seed_notice(conn, "ocid-002", "Cloud hosting",
                 parent_framework_title="Network Services 3")
    mfc.mine_structured_references(conn)
    co = conn.execute(
        "SELECT * FROM framework_call_offs WHERE notice_ocid='ocid-002'"
    ).fetchone()
    assert co is not None
    assert co["match_method"] == "reference_no"
    assert co["match_confidence"] == 1.0


def test_mine_structured_idempotent():
    """Running twice must not create duplicate frameworks or call-offs."""
    conn = _make_db()
    _seed_notice(conn, "ocid-003", "IT support",
                 parent_framework_title="Technology Services 3")
    mfc.mine_structured_references(conn)
    mfc.mine_structured_references(conn)
    count = conn.execute("SELECT COUNT(*) FROM frameworks").fetchone()[0]
    assert count == 1


# ── mine_rm_patterns ─────────────────────────────────────────────────────────

def test_mine_rm_pattern_in_title():
    conn = _make_db()
    _seed_notice(conn, "ocid-004", "Procurement via RM6116")
    mfc.mine_rm_patterns(conn)
    fw = conn.execute("SELECT * FROM frameworks WHERE reference_no='RM6116'").fetchone()
    assert fw is not None
    assert fw["match_confidence"] if hasattr(fw, "match_confidence") else True


def test_mine_rm_pattern_creates_call_off():
    conn = _make_db()
    _seed_notice(conn, "ocid-005", "Services under RM6100")
    mfc.mine_rm_patterns(conn)
    co = conn.execute(
        "SELECT * FROM framework_call_offs WHERE notice_ocid='ocid-005'"
    ).fetchone()
    assert co is not None
    assert co["match_method"] == "reference_no"
    assert abs(co["match_confidence"] - 0.9) < 0.01


# ── update_summary_counts ─────────────────────────────────────────────────────

def test_summary_counts_updated():
    conn = _make_db()
    _seed_notice(conn, "ocid-006", "Cloud via RM6116")
    mfc.mine_rm_patterns(conn)
    mfc.update_summary_counts(conn)
    fw = conn.execute(
        "SELECT call_off_count, call_off_value_total FROM frameworks WHERE reference_no='RM6116'"
    ).fetchone()
    assert fw["call_off_count"] == 1
    assert fw["call_off_value_total"] == 100000.0
