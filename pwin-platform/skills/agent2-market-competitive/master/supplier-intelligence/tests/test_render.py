import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from render import build_html

MINIMAL = {
    "meta": {
        "supplierName": "TestCo Ltd",
        "version": "1.0.0",
        "builtDate": "2026-05-01",
        "mode": "build",
        "sourceCount": 2,
    },
    "strategicScores": {
        "sectorStrength": {"score": 5, "rationale": "ok"},
        "competitorThreat": {"score": 5, "rationale": "ok"},
        "vulnerability": {"score": 5, "rationale": "ok"},
    },
    "D3": {
        "frameworkPositions": [
            {"framework": "Tech Services 3", "lot": "Lot 1b", "expiry": "2027-03-31", "valueCeilingGbpm": 50}
        ],
        "topContracts": [
            {"buyer": "Home Office", "title": "IT Support", "valueGbpm": 10.5, "expiry": "2026-12-31", "cpv": "72000000"}
        ],
    },
    "D4": {
        "contractsExpiring24m": [
            {"buyer": "HMRC", "title": "Data Services", "valueGbpm": 8.0, "expiry": "2027-01-15",
             "rebidVulnerability": "high", "vulnerabilityRationale": "Performance concerns flagged in PAC 2025."}
        ],
        "knownPipelinePursuits": [{"value": "Pursuing DESNZ digital transformation, est. £30m"}],
    },
    "claims": [],
}


def test_d3_framework_positions_rendered():
    html = build_html(MINIMAL)
    assert "Tech Services 3" in html
    assert "Lot 1b" in html
    assert "2027-03-31" in html


def test_d3_top_contracts_rendered():
    html = build_html(MINIMAL)
    assert "Home Office" in html
    assert "IT Support" in html


def test_d4_expiring_contracts_rendered():
    html = build_html(MINIMAL)
    assert "HMRC" in html
    assert "Data Services" in html
    assert "high" in html.lower()


def test_d4_pipeline_pursuits_rendered():
    html = build_html(MINIMAL)
    assert "DESNZ" in html


def test_no_d3_d4_renders_without_error():
    data = {**MINIMAL, "D3": {}, "D4": {}}
    html = build_html(data)
    assert "TestCo Ltd" in html
