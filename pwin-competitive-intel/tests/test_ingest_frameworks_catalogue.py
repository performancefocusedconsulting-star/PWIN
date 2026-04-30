"""Tests: ingest_frameworks_catalogue.py — CCS parser functions."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

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

# Minimal fixture HTML representing a CCS agreement detail page
DETAIL_FIXTURE = """
<html><body>
  <h1 class="agreement-title">Network Services 3</h1>
  <p class="reference-number">RM6116</p>
  <p class="expiry-date">31 March 2027</p>
  <p class="description">Wide area networking and connectivity services.</p>
  <table class="lots-table">
    <tbody>
      <tr><td>1</td><td>Wide Area Network</td><td>Connectivity</td></tr>
      <tr><td>2</td><td>Internet Access</td><td>Broadband</td></tr>
    </tbody>
  </table>
</body></html>
"""

DETAIL_FIXTURE_MINIMAL = """
<html><body>
  <h1 class="agreement-title">TEPAS 2</h1>
</body></html>
"""


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
