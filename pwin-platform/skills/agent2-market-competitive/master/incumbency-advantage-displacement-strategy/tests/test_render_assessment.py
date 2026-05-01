import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from render_assessment import build_html

MINIMAL = {
    "meta": {
        "pursuitId": "PUR-2026-0001",
        "skillName": "incumbency-advantage-displacement-strategy",
        "version": "1.0.0",
        "mode": "build",
        "builtDate": "2026-05-01",
        "sourceCount": 4,
        "incumbentName": "Serco Group plc",
        "buyerName": "Ministry of Justice",
        "contractTitle": "Electronic Monitoring Services",
    },
    "incumbentScenario": "defending",
    "executiveJudgement": {
        "overallVerdict": "high_risk",
        "verdictRationale": "Incumbent has deep relationship embeddedness but faces performance scrutiny.",
        "confidenceLevel": "medium",
    },
    "incumbentAdvantage": {
        "totalAdvantageScore": 7,
        "relationshipEmbeddedness": {"value": "Strong — 8 years on contract, 3 Director-level relationships"},
        "switchingCostTobuyer": {"value": "High — estimated £15m transition cost"},
    },
    "incumbentVulnerabilities": {
        "totalVulnerabilityScore": 6,
        "performanceRecord": {"value": "2 amber KPIs in last 12 months"},
    },
    "goNoGoImplications": {
        "recommendedStance": "Pursue with displacement strategy",
        "pwinScoreAlignment": "Consistent with current 42% PWIN",
    },
    "claims": [
        {
            "claimId": "INC-CLM-001",
            "claimText": "Serco has held this contract since 2017.",
            "claimDate": "2026-05-01",
            "source": "SRC-001",
            "sourceDate": "2026-04-15",
            "sourceTier": 1,
        }
    ],
    "sourceRegister": {"sources": []},
}


def test_header_renders():
    html = build_html(MINIMAL)
    assert "Serco Group plc" in html
    assert "Ministry of Justice" in html


def test_executive_verdict_renders():
    html = build_html(MINIMAL)
    assert "HIGH RISK" in html


def test_advantage_score_renders():
    html = build_html(MINIMAL)
    assert ">7<" in html or "7/10" in html


def test_vulnerability_score_renders():
    html = build_html(MINIMAL)
    assert ">6<" in html or "6/10" in html


def test_go_no_go_renders():
    html = build_html(MINIMAL)
    assert "Pursue" in html


def test_claims_block_renders():
    html = build_html(MINIMAL)
    assert "INC-CLM-001" in html
    assert "Serco has held this contract since 2017" in html


def test_empty_claims_renders_without_error():
    data = {**MINIMAL, "claims": []}
    html = build_html(data)
    assert "Serco Group plc" in html
