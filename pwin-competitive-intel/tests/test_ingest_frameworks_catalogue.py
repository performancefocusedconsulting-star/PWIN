"""Tests: ingest_frameworks_catalogue.py — CCS parser functions."""
import importlib.util
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

SCHEMA_PATH_DB = Path(__file__).parent.parent / "db" / "schema.sql"

spec = importlib.util.spec_from_file_location(
    "ingest_frameworks_catalogue",
    Path(__file__).parent.parent / "agent" / "ingest_frameworks_catalogue.py",
)
try:
    ifc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ifc)
except Exception:
    ifc = None

# Minimal fixture HTML representing a CCS agreement list page
LIST_FIXTURE = """
<html><body>
  <ul class="agreements-list">
    <li><a href="/agreements/rm6116">Network Services 3</a></li>
    <li><a href="/agreements/rm6100">Technology Services 3</a></li>
  </ul>
</body></html>
"""

# Minimal fixture HTML representing a GCA (formerly CCS) agreement detail page
# Structure matches the actual GCA site as of 2026-04
DETAIL_FIXTURE = """
<html><body>
  <div class="govuk-grid-column-two-thirds">
    <h1 class="govuk-heading-xl page-title">Network Services 3</h1>
    <div class="govuk-body-l">Wide area networking and connectivity services.</div>
  </div>
  <div class="govuk-grid-column-one-third">
    <aside class="aside">
      <div class="apollo-enclosure">
        <h2 class="aside__heading">Key facts</h2>
        <dl class="govuk-list govuk-list--definition">
          <dt>Agreement ID</dt>
          <dd class="apollo-list--definition__value">RM6116</dd>
          <dt>End date</dt>
          <dd class="apollo-list--definition__value">31/03/2027</dd>
        </dl>
      </div>
    </aside>
  </div>
  <dl class="apollo-list apollo-list--definition">
    <dt class="apollo-list--definition__key">
      <span class="apollo-list--definition__key__inner">Lot 1: Wide Area Network</span>
    </dt>
    <dd class="apollo-list--definition__value"><p class>Expires: <time>31/03/2027</time></p></dd>
    <dt class="apollo-list--definition__key">
      <span class="apollo-list--definition__key__inner">Lot 2: Internet Access</span>
    </dt>
    <dd class="apollo-list--definition__value"><p class>Expires: <time>31/03/2027</time></p></dd>
  </dl>
</body></html>
"""

DETAIL_FIXTURE_MINIMAL = """
<html><body>
  <h1 class="govuk-heading-xl page-title">TEPAS 2</h1>
</body></html>
"""


def _make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_PATH_DB.read_text(encoding="utf-8"))
    conn.commit()
    return conn


def test_parse_ccs_list_extracts_urls():
    assert ifc is not None
    urls = ifc.parse_ccs_list(LIST_FIXTURE, base_url="https://www.crowncommercial.gov.uk")
    assert len(urls) == 2
    assert any("rm6116" in u for u in urls)
    assert any("rm6100" in u for u in urls)


def test_parse_ccs_agreement_name():
    assert ifc is not None
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE)
    assert result["name"] == "Network Services 3"


def test_parse_ccs_agreement_reference():
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE)
    assert result["reference_no"] == "RM6116"


def test_parse_ccs_agreement_expiry():
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE)
    assert result["expiry_date"] == "2027-03-31"


def test_parse_ccs_agreement_lots():
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE)
    assert len(result["lots"]) == 2
    assert result["lots"][0]["lot_number"] == "1"
    assert result["lots"][0]["lot_name"] == "Wide Area Network"


def test_parse_ccs_agreement_minimal_no_crash():
    """Parser must not crash on a minimal/incomplete page."""
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE_MINIMAL)
    assert result["name"] == "TEPAS 2"
    assert result["reference_no"] is None
    assert result["lots"] == []


def test_parse_date_iso():
    assert ifc is not None
    assert ifc._parse_date("31 March 2027") == "2027-03-31"
    assert ifc._parse_date("2027-03-31") == "2027-03-31"
    assert ifc._parse_date("") is None
    assert ifc._parse_date(None) is None


def test_upsert_catalogue_framework_inserts():
    assert ifc is not None
    conn = _make_db()
    data = {"name": "Network Services 3", "reference_no": "RM6116",
            "expiry_date": "2027-03-31", "description": "WAN services",
            "lots": [{"lot_number": "1", "lot_name": "WAN", "scope": None}]}
    fw_id = ifc._upsert_catalogue_framework(conn, data, source_url="https://example.com/rm6116")
    fw = conn.execute("SELECT * FROM frameworks WHERE id=?", (fw_id,)).fetchone()
    assert fw["name"] == "Network Services 3"
    assert fw["source"] == "catalogue_only"
    assert fw["lot_count"] == 1


def test_upsert_catalogue_framework_idempotent():
    conn = _make_db()
    data = {"name": "Tech Services 3", "reference_no": "RM6100",
            "expiry_date": None, "description": None, "lots": []}
    ifc._upsert_catalogue_framework(conn, data, source_url="https://example.com/rm6100")
    ifc._upsert_catalogue_framework(conn, data, source_url="https://example.com/rm6100")
    count = conn.execute("SELECT COUNT(*) FROM frameworks WHERE reference_no='RM6100'").fetchone()[0]
    assert count == 1


def test_upsert_preserves_both_source():
    """A 'contracts_only' record should become 'both'; 'both' should stay 'both'."""
    conn = _make_db()
    # Seed a contracts_only record
    conn.execute("""
        INSERT INTO frameworks (name, reference_no, owner, source, last_updated)
        VALUES ('Network Services 3', 'RM6116', 'unknown', 'contracts_only', datetime('now'))
    """)
    conn.commit()
    data = {"name": "Network Services 3", "reference_no": "RM6116",
            "expiry_date": "2027-03-31", "description": None, "lots": []}
    # First catalogue run: should promote to 'both'
    ifc._upsert_catalogue_framework(conn, data, source_url="https://example.com/rm6116")
    fw = conn.execute("SELECT source FROM frameworks WHERE reference_no='RM6116'").fetchone()
    assert fw["source"] == "both"
    # Second catalogue run: should preserve 'both', not downgrade to 'catalogue_only'
    ifc._upsert_catalogue_framework(conn, data, source_url="https://example.com/rm6116")
    fw = conn.execute("SELECT source FROM frameworks WHERE reference_no='RM6116'").fetchone()
    assert fw["source"] == "both"
