# Intelligence Skills Platform Upgrade — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the gap between the buyer intelligence skill and the supplier, sector, and incumbency skills — fixing missing renderer sections, creating the incumbency HTML renderer, and wiring the new stakeholder and framework databases into buyer and incumbency skills as preferred MCP sources.

**Architecture:** All changes live under `pwin-platform/skills/agent2-market-competitive/master/`. Python renderer tasks follow a refactor-then-test pattern: extract `build_html(data: dict) -> str` from `render(slug)` so HTML logic is unit-testable without file I/O. SKILL.md tasks are markdown edits to prerequisite tables and Step 0 MCP call sequences — no changes to the platform itself.

**Tech Stack:** Python 3.9+ stdlib (renderers and tests), Markdown (SKILL.md edits), pytest.

**Out of scope for this plan:** Extraction templates for supplier/sector; mode workflow reference docs for supplier/sector. Both are separate bodies of work.

---

## File Map

**Modified:**
- `master/supplier-intelligence/scripts/render.py` — extract `build_html(data)`, add D3 and D4 section rendering
- `master/buyer-intelligence/SKILL.md` — add `get_senior_leadership`, `find_evaluators`, `get_buyer_framework_usage` to prerequisites and Step 0
- `master/incumbency-advantage-displacement-strategy/SKILL.md` — add `get_senior_leadership`, `find_evaluators` to preferred prerequisites and Step 0

**Created:**
- `master/supplier-intelligence/tests/__init__.py`
- `master/supplier-intelligence/tests/test_render.py`
- `master/incumbency-advantage-displacement-strategy/scripts/__init__.py`
- `master/incumbency-advantage-displacement-strategy/scripts/render_assessment.py`
- `master/incumbency-advantage-displacement-strategy/tests/__init__.py`
- `master/incumbency-advantage-displacement-strategy/tests/test_render_assessment.py`

---

## Task 1: Supplier renderer — add D3 and D4 sections

The supplier renderer shows D1, D2, D5–D9 but silently skips D3 (Framework & Contract Positions) and D4 (Contracts Expiring 24m). Both sections are in the output schema and populated by the skill but never appear in the HTML. This task also extracts `build_html(data)` from `render(slug)` so the rendering logic is testable without file I/O.

**Files:**
- Modify: `master/supplier-intelligence/scripts/render.py`
- Create: `master/supplier-intelligence/tests/__init__.py`
- Create: `master/supplier-intelligence/tests/test_render.py`

- [ ] **Step 1: Create test file with failing tests**

Create `master/supplier-intelligence/tests/__init__.py` (empty file).

Create `master/supplier-intelligence/tests/test_render.py`:

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

```
cd pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence
python -m pytest tests/test_render.py -v
```

Expected: `ImportError: cannot import name 'build_html' from 'render'`

- [ ] **Step 3: Rewrite `render.py` to extract `build_html` and add D3/D4**

Replace the contents of `master/supplier-intelligence/scripts/render.py` with:

```python
#!/usr/bin/env python3
"""Render a supplier dossier JSON to branded BidEquity HTML.

Usage: python render.py <slug>

Reads from C:\\Users\\User\\.pwin\\intel\\suppliers\\<slug>-dossier.json
and writes the rendered HTML to both the intel cache and the workspace folder.
"""
import json
import os
import re
import sys
from datetime import date

NAVY = "#021744"
SAND = "#F7F4EE"
AQUA = "#7ADDE2"
TEAL = "#5CA3B6"
PALE = "#E0F4F6"
TERRA = "#D17A74"

CITATION_RE = re.compile(r"\[(CLM-[0-9A-Z-]+|[A-Z]+-CLM-[0-9A-Z-]+)\]")


def _linkify_citations(text: str) -> str:
    if not isinstance(text, str):
        return text
    return CITATION_RE.sub(
        lambda m: f'<a class="claim-cite" href="#claim-{m.group(1)}">[{m.group(1)}]</a>',
        text,
    )


def _render_claims_block(claims: list) -> str:
    if not claims:
        return ""
    rows = []
    for c in claims:
        cid = c.get("claimId", "?")
        rows.append(
            f'<dt id="claim-{cid}">[{cid}] '
            f'(tier {c.get("sourceTier", "?")} '
            f'— {c.get("sourceDate") or "undated"})</dt>'
            f'<dd><p>{c.get("claimText", "")}</p>'
            f'<p class="claim-source"><strong>Source:</strong> '
            f'{c.get("source", "?")}</p>'
            f'<p class="claim-meta">Asserted '
            f'{c.get("claimDate", "?")}</p></dd>'
        )
    return (
        '<div class="card"><h2>Claims and evidence</h2>'
        '<dl class="claims">' + "".join(rows) + '</dl></div>'
    )


def ev(w, default="—"):
    if isinstance(w, dict):
        return _linkify_citations(str(w.get("value", default)))
    return _linkify_citations(str(w)) if w else default


def badge(w):
    if not isinstance(w, dict):
        return ""
    c = w.get("confidence", "")
    col = {"high": AQUA, "medium": TERRA, "low": SAND}.get(c, SAND)
    return (f'<span style="background:{col};color:{NAVY};padding:1px 6px;'
            f'border-radius:3px;font-size:0.75em;margin-left:6px">{c}</span>')


def bar(score, mx=10):
    pct = int((score / mx) * 100)
    return (f'<div style="background:{PALE};border-radius:4px;height:8px;'
            f'width:200px;display:inline-block;vertical-align:middle">'
            f'<div style="background:{TEAL};width:{pct}%;height:8px;'
            f'border-radius:4px"></div></div>')


def domain_table(domain_data, fields):
    rows = []
    for label, key in fields:
        val = domain_data.get(key)
        if isinstance(val, list):
            items = "".join(f"<li>{ev(i)}{badge(i)}</li>" for i in val)
            rows.append(
                f'<tr><td class="lbl">{label}</td>'
                f'<td><ul style="margin:0;padding-left:18px">{items}</ul></td></tr>'
            )
        elif val:
            rows.append(
                f'<tr><td class="lbl">{label}</td>'
                f'<td>{ev(val)}{badge(val)}</td></tr>'
            )
    if not rows:
        rows = ['<tr><td colspan="2" style="color:#999;font-size:0.85em">No data yet</td></tr>']
    return "".join(rows)


def build_html(d: dict) -> str:
    """Build the full HTML string from a dossier dict. Testable without file I/O."""
    meta = d.get("meta", {})
    sc = d.get("strategicScores", {})

    def score_row(label, s):
        sc_val = s.get("score", 0)
        rat = s.get("rationale", "")
        return (
            f'<tr><td style="padding:8px 12px;font-weight:600">{label}</td>'
            f'<td style="padding:8px 12px">{bar(sc_val)} '
            f'<span style="font-family:DM Mono,monospace;margin-left:8px">{sc_val}/10</span></td>'
            f'<td style="padding:8px 12px;font-size:0.88em;color:#444">{rat}</td></tr>'
        )

    def domain_card(code, title, fields):
        rows = domain_table(d.get(code, {}), fields)
        return (
            f'<div style="margin-bottom:24px">'
            f'<h3 style="font-family:Cormorant Garamond,serif;color:{NAVY};'
            f'font-size:1.1em;margin:0 0 8px 0;padding-bottom:4px;'
            f'border-bottom:1px solid {PALE}">{code} — {title}</h3>'
            f'<table style="width:100%;border-collapse:collapse">{rows}</table></div>'
        )

    # D3: Framework & Contract Positions
    d3 = d.get("D3", {})
    fp_rows = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px">{fp.get("framework", "")}</td>'
        f'<td style="padding:6px 12px">{fp.get("lot", "")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace">{fp.get("expiry", "")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace">'
        f'{"£{:,.0f}m".format(fp["valueCeilingGbpm"]) if fp.get("valueCeilingGbpm") else "—"}</td></tr>'
        for fp in d3.get("frameworkPositions", [])
    )
    tc_rows = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px">{tc.get("buyer", "")}</td>'
        f'<td style="padding:6px 12px">{tc.get("title", "")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace">'
        f'{"£{:,.0f}m".format(tc["valueGbpm"]) if tc.get("valueGbpm") else "—"}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace">{tc.get("expiry", "")}</td>'
        f'<td style="padding:6px 12px;font-size:0.8em;color:#666">{tc.get("cpv", "")}</td></tr>'
        for tc in d3.get("topContracts", [])
    )
    d3_html = ""
    if fp_rows or tc_rows:
        d3_html = (
            '<div style="margin-bottom:24px">'
            f'<h3 style="font-family:Cormorant Garamond,serif;color:{NAVY};font-size:1.1em;'
            f'margin:0 0 8px 0;padding-bottom:4px;border-bottom:1px solid {PALE}">'
            'D3 — Framework &amp; Contract Positions</h3>'
        )
        if fp_rows:
            d3_html += (
                '<p style="font-size:0.8em;color:#666;margin-bottom:4px">Framework positions</p>'
                f'<table style="width:100%;border-collapse:collapse;margin-bottom:12px">'
                f'<thead><tr style="background:{NAVY};color:{SAND}">'
                '<th style="padding:6px 12px;text-align:left">Framework</th>'
                '<th style="padding:6px 12px;text-align:left">Lot</th>'
                '<th style="padding:6px 12px;text-align:left">Expiry</th>'
                '<th style="padding:6px 12px;text-align:left">Ceiling</th></tr></thead>'
                f'<tbody>{fp_rows}</tbody></table>'
            )
        if tc_rows:
            d3_html += (
                '<p style="font-size:0.8em;color:#666;margin-bottom:4px">Top contracts</p>'
                f'<table style="width:100%;border-collapse:collapse">'
                f'<thead><tr style="background:{NAVY};color:{SAND}">'
                '<th style="padding:6px 12px;text-align:left">Buyer</th>'
                '<th style="padding:6px 12px;text-align:left">Title</th>'
                '<th style="padding:6px 12px;text-align:left">Value</th>'
                '<th style="padding:6px 12px;text-align:left">Expiry</th>'
                '<th style="padding:6px 12px;text-align:left">CPV</th></tr></thead>'
                f'<tbody>{tc_rows}</tbody></table>'
            )
        d3_html += '</div>'

    # D4: Contracts Expiring 24m
    d4 = d.get("D4", {})
    vuln_col = {"high": TERRA, "medium": AQUA, "low": PALE}
    exp_rows = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px">{c.get("buyer", "")}</td>'
        f'<td style="padding:6px 12px">{c.get("title", "")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace">'
        f'{"£{:,.0f}m".format(c["valueGbpm"]) if c.get("valueGbpm") else "—"}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace">{c.get("expiry", "")}</td>'
        f'<td style="padding:6px 12px">'
        f'<span style="background:{vuln_col.get(c.get("rebidVulnerability", ""), PALE)};'
        f'color:{NAVY};padding:2px 8px;border-radius:4px;font-size:0.8em;font-weight:600">'
        f'{c.get("rebidVulnerability", "").upper()}</span></td>'
        f'<td style="padding:6px 12px;font-size:0.82em;color:#444">'
        f'{c.get("vulnerabilityRationale", "")}</td></tr>'
        for c in d4.get("contractsExpiring24m", [])
    )
    pipeline_items = "".join(
        f'<li style="margin-bottom:4px">{ev(p)}</li>'
        for p in d4.get("knownPipelinePursuits", [])
    )
    d4_html = ""
    if exp_rows or pipeline_items:
        d4_html = (
            '<div style="margin-bottom:24px">'
            f'<h3 style="font-family:Cormorant Garamond,serif;color:{NAVY};font-size:1.1em;'
            f'margin:0 0 8px 0;padding-bottom:4px;border-bottom:1px solid {PALE}">'
            'D4 — Contracts Expiring 24m</h3>'
        )
        if exp_rows:
            d4_html += (
                f'<table style="width:100%;border-collapse:collapse;margin-bottom:12px">'
                f'<thead><tr style="background:{NAVY};color:{SAND}">'
                '<th style="padding:6px 12px;text-align:left">Buyer</th>'
                '<th style="padding:6px 12px;text-align:left">Contract</th>'
                '<th style="padding:6px 12px;text-align:left">Value</th>'
                '<th style="padding:6px 12px;text-align:left">Expiry</th>'
                '<th style="padding:6px 12px;text-align:left">Vulnerability</th>'
                '<th style="padding:6px 12px;text-align:left">Rationale</th></tr></thead>'
                f'<tbody>{exp_rows}</tbody></table>'
            )
        if pipeline_items:
            d4_html += (
                '<p style="font-size:0.8em;color:#666;margin:8px 0 4px">Known pipeline pursuits</p>'
                f'<ul style="margin:0;padding-left:18px">{pipeline_items}</ul>'
            )
        d4_html += '</div>'

    vmap_rows = "".join(
        f'<tr>'
        f'<td style="padding:8px 12px">{r.get("contract", "")}</td>'
        f'<td style="padding:8px 12px">{r.get("buyer", "")}</td>'
        f'<td style="padding:8px 12px;font-family:DM Mono,monospace">{r.get("expiry", "")}</td>'
        f'<td style="padding:8px 12px">{r.get("vulnerability", "")}</td>'
        f'<td style="padding:8px 12px;font-size:0.88em">{r.get("displacementRoute", "")}</td></tr>'
        for r in d.get("vulnerabilityMap", [])
    )

    amend_cards = "".join(
        f'<div style="background:#fff;border-radius:8px;padding:20px;margin-bottom:16px;'
        f'border-left:4px solid {TERRA}">'
        f'<strong>{a.get("sourceId")} — {a.get("type")}</strong>'
        f'<p style="margin:8px 0">{a.get("content")}</p>'
        f'<span style="font-size:0.8em;color:#666">{a.get("date")} | confidence: {a.get("confidence")}</span>'
        f'</div>'
        for a in d.get("amendments", [])
    )

    register = d.get("sourceRegister", {})
    sources = register.get("sources", [])
    src_rows = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{s.get("sourceId")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em">{s.get("tier")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em">{s.get("title")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">'
        f'{", ".join(s.get("sectionsSupported", []))}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{s.get("accessDate")}</td></tr>'
        for s in sources
    )

    version_log = meta.get("versionLog", [])
    version_rows = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{v.get("version")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{v.get("date")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em;text-transform:uppercase">{v.get("mode")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em">{v.get("summary")}</td></tr>'
        for v in version_log
    )

    html = (
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{meta.get("supplierName", "Supplier")} — Intelligence Dossier</title>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Cormorant+Garamond:wght@400;600;700&family=DM+Mono:wght@400;500'
        '&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">'
        '<style>'
        f'*{{box-sizing:border-box;margin:0;padding:0}} body{{background:{SAND};font-family:DM Sans,sans-serif;color:{NAVY}}}'
        f'.hdr{{background:{NAVY};color:{SAND};padding:32px 48px}}'
        '.hdr h1{font-family:Cormorant Garamond,serif;font-size:2.2em;font-weight:700}'
        f'.sub{{font-family:DM Mono,monospace;font-size:0.78em;color:{AQUA};margin-top:6px}}'
        '.body{max-width:1100px;margin:0 auto;padding:32px 24px}'
        f'.card{{background:#fff;border-radius:8px;padding:24px;margin-bottom:24px;box-shadow:0 1px 4px rgba(2,23,68,.07)}}'
        f'.card h2{{font-family:Cormorant Garamond,serif;color:{NAVY};font-size:1.4em;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid {PALE}}}'
        'table{width:100%;border-collapse:collapse} tr:nth-child(even){background:#F7F4EE}'
        f'.lbl{{padding:6px 12px;color:#666;font-size:0.85em;width:200px;font-family:DM Sans,sans-serif}}'
        f'td{{padding:6px 12px;font-family:DM Sans,sans-serif;color:{NAVY}}}'
        '.claims{list-style:none}'
        f'.claims dt{{font-family:DM Sans,sans-serif;font-weight:600;color:{NAVY};margin-top:14px;font-size:0.88em}}'
        f'.claims dd{{border-left:3px solid {TEAL};padding-left:14px;margin-left:0;margin-bottom:8px}}'
        '.claim-source,.claim-meta{font-size:0.78em;color:#94A3B8;margin:2px 0}'
        f'a.claim-cite{{color:{TEAL};text-decoration:none;font-size:0.85em;font-weight:600}}'
        'a.claim-cite:hover{text-decoration:underline}'
        '</style></head><body>'
        '<div class="hdr">'
        f'<h1>{meta.get("supplierName", "Supplier Intelligence Dossier")}</h1>'
        f'<div class="sub">v{meta.get("version", "1.0.0")} &nbsp;|&nbsp; '
        f'Built {meta.get("builtDate", "--")} &nbsp;|&nbsp; '
        f'{meta.get("sourceCount", 0)} sources &nbsp;|&nbsp; '
        f'<span style="text-transform:uppercase">{meta.get("mode", "build")}</span>'
        f'<span style="background:{TEAL};color:{SAND};padding:2px 10px;border-radius:12px;'
        f'font-family:DM Mono,monospace;font-size:0.75em;margin-left:10px">INTERNAL</span></div></div>'
        '<div class="body">'
        '<div class="card"><h2>Strategic Scores</h2><table>'
        + score_row("Sector Strength", sc.get("sectorStrength", {}))
        + score_row("Competitor Threat", sc.get("competitorThreat", {}))
        + score_row("Vulnerability", sc.get("vulnerability", {}))
        + '</table></div>'
        '<div class="card"><h2>Domain Intelligence</h2>'
        + domain_card("D1", "Identity & Structure", [
            ("Legal name", "legalName"),
            ("CH number", "companiesHouseNo"),
            ("Parent", "parentCompany"),
            ("SIC codes", "sicCodes"),
        ])
        + domain_card("D2", "UK Public Sector Footprint", [
            ("PS revenue", "totalUkPublicSectorRevenueGbpm"),
            ("% of group", "pctOfGroupRevenue"),
            ("Geography", "geographicSpread"),
        ])
        + d3_html
        + d4_html
        + domain_card("D5", "Capabilities & Service Lines", [
            ("Core capabilities", "coreCapabilities"),
            ("Tech stack", "technologyStack"),
            ("Accreditations", "accreditations"),
        ])
        + domain_card("D6", "Key People", [
            ("CEO", "ceo"),
            ("CFO", "cfo"),
            ("PS MD", "publicSectorMd"),
            ("BD Director", "bdDirector"),
            ("Recent changes", "recentLeadershipChanges"),
        ])
        + domain_card("D7", "Competitive Positioning", [
            ("Win rate signal", "ftsWinRateSignal"),
            ("Differentiation", "differentiationNarrative"),
            ("Weaknesses", "knownWeaknesses"),
            ("Pricing", "pricingPosture"),
        ])
        + domain_card("D8", "Recent Signals", [
            ("Recent wins", "recentWins"),
            ("Recent losses", "recentLosses"),
            ("Press (90d)", "pressSignals90d"),
            ("Regulatory", "regulatoryReputationalEvents"),
        ])
        + domain_card("D9", "Financial Health", [
            ("EBITDA margin", "ebitdaMarginPct"),
            ("Net debt", "netDebtGbpm"),
            ("PS revenue %", "publicSectorRevenuePct"),
            ("Credit risk", "creditRiskSummary"),
        ])
        + '</div>'
        + '<div class="card"><h2>Vulnerability Map</h2><table>'
        + f'<thead><tr style="background:{NAVY};color:{SAND}">'
        + '<th style="padding:8px 12px;text-align:left">Contract</th>'
        + '<th style="padding:8px 12px;text-align:left">Buyer</th>'
        + '<th style="padding:8px 12px;text-align:left">Expiry</th>'
        + '<th style="padding:8px 12px;text-align:left">Vulnerability</th>'
        + '<th style="padding:8px 12px;text-align:left">Displacement Route</th></tr></thead>'
        + f'<tbody>{vmap_rows}</tbody></table></div>'
        + (f'<div class="card"><h2>Internal Amendments</h2>{amend_cards}</div>' if amend_cards else "")
        + '<div class="card"><h2>Sources</h2><table>'
        + f'<thead><tr style="background:{NAVY};color:{SAND}">'
        + '<th style="padding:6px 12px;text-align:left">ID</th>'
        + '<th style="padding:6px 12px;text-align:left">Tier</th>'
        + '<th style="padding:6px 12px;text-align:left">Title</th>'
        + '<th style="padding:6px 12px;text-align:left">Sections</th>'
        + '<th style="padding:6px 12px;text-align:left">Accessed</th></tr></thead>'
        + f'<tbody>{src_rows}</tbody></table></div>'
        + (f'<div class="card"><h2>Version History</h2><table>'
           f'<thead><tr style="background:{NAVY};color:{SAND}">'
           f'<th style="padding:6px 12px;text-align:left">Version</th>'
           f'<th style="padding:6px 12px;text-align:left">Date</th>'
           f'<th style="padding:6px 12px;text-align:left">Mode</th>'
           f'<th style="padding:6px 12px;text-align:left">Summary</th></tr></thead>'
           f'<tbody>{version_rows}</tbody></table></div>' if version_rows else "")
        + f'<div style="text-align:center;padding:16px;font-family:DM Mono,monospace;font-size:0.72em;color:#999">'
        + f'BidEquity Intelligence Platform &nbsp;|&nbsp; INTERNAL USE ONLY &nbsp;|&nbsp; Generated {date.today().isoformat()}</div>'
    )
    html += _render_claims_block(d.get("claims", []))
    html += '</div></body></html>'
    return html


def render(slug):
    intel = fr"C:\Users\User\.pwin\intel\suppliers\{slug}-dossier.json"
    ws_dir = r"C:\Users\User\Documents\Claude\Projects\Bid Equity\suppliers"
    os.makedirs(ws_dir, exist_ok=True)
    os.makedirs(r"C:\Users\User\.pwin\intel\suppliers", exist_ok=True)

    with open(intel, encoding="utf-8") as f:
        d = json.load(f)

    html = build_html(d)
    out_paths = [
        fr"C:\Users\User\.pwin\intel\suppliers\{slug}-dossier.html",
        os.path.join(ws_dir, f"{slug}-dossier.html"),
    ]
    for p in out_paths:
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"Written: {p}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render.py <slug>")
        sys.exit(1)
    render(sys.argv[1])
```

- [ ] **Step 4: Run tests — confirm all pass**

```
cd pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence
python -m pytest tests/test_render.py -v
```

Expected:
```
test_d3_framework_positions_rendered PASSED
test_d3_top_contracts_rendered PASSED
test_d4_expiring_contracts_rendered PASSED
test_d4_pipeline_pursuits_rendered PASSED
test_no_d3_d4_renders_without_error PASSED
5 passed
```

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/scripts/render.py
git add pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/tests/
git commit -m "feat(supplier-intel): render D3 framework positions and D4 expiring contracts"
```

---

## Task 2: Wire `get_senior_leadership` and `find_evaluators` into buyer SKILL.md

The buyer output schema has `seniorLeadership` (array of `{name, role, since, background}`) and `decisionUnitAssumptions`. The organogram database is built and exposes `get_senior_leadership(name)` and `find_evaluators(name)` via MCP, but the buyer SKILL.md Step 0 doesn't fetch from them. Every buyer dossier currently builds the leadership section from web research when the database can supply it instantly.

**Files:**
- Modify: `master/buyer-intelligence/SKILL.md`

- [ ] **Step 1: Add both tools to the preferred prerequisites table**

Find the `## Prerequisites` section. In the preferred prerequisites table (after the `get_buyer_behaviour_profile` row), add:

```markdown
| Senior leadership (organogram DB) | `pwin-platform` (`get_senior_leadership`, `find_evaluators`) | `seniorLeadership`, `decisionUnitAssumptions` |
```

- [ ] **Step 2: Add the MCP calls to Step 0**

Find `## Step 0` (or the section describing the opening MCP fetch sequence). After the existing preferred prerequisite calls, add:

```markdown
**3a.** `get_senior_leadership(buyerName)` — preferred. Returns Director-tier and above civil servants from the organogram database. If successful, use as primary source for the `seniorLeadership` array. Set `meta.prerequisitesPresentAt.preferred.organogramData` to `true`. If the call returns an empty list or fails, fall back to web research and set to `false`.

**3b.** `find_evaluators(buyerName)` — preferred. Returns Director-level SROs who have appeared as PAC witnesses — the most likely evaluators and governance owners on major procurements. Use to populate `decisionUnitAssumptions.seniorResponsibleOwner` and `decisionUnitAssumptions.likelyEvaluators`. Set `meta.prerequisitesPresentAt.preferred.evaluatorData` to `true` if successful.
```

- [ ] **Step 3: Add the new flags to the `prerequisitesPresentAt` schema example**

Find the `prerequisitesPresentAt` example JSON block in the SKILL.md. Add two lines to the `preferred` object:

```json
"organogramData": true,
"evaluatorData": true
```

- [ ] **Step 4: Add MCP-priority note near the `seniorLeadership` field guidance**

Find the section describing how to populate `seniorLeadership` (in the BUILD mode workflow or section-by-section writing guidance). Add immediately before that guidance:

```markdown
> **MCP data takes priority.** If `get_senior_leadership` returned results, use those as the primary source. Do not re-research from web if MCP data is present. Web research only supplements gaps — e.g. very recent appointees not yet in the latest organogram release.
```

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/SKILL.md
git commit -m "feat(buyer-intel): wire get_senior_leadership and find_evaluators into Step 0"
```

---

## Task 3: Wire `get_buyer_framework_usage` into buyer SKILL.md

The buyer output schema has `procurementBehaviour.frameworkUsage` and `procurementBehaviour.preferredRoutes`. The framework database exposes `get_buyer_framework_usage(buyerName)` which returns the buyer's frameworks ranked by call-off value. This is more reliable than inferring framework usage from press coverage or procurement notices, but is not currently in the buyer skill's Step 0.

**Files:**
- Modify: `master/buyer-intelligence/SKILL.md`

- [ ] **Step 1: Add to the preferred prerequisites table**

In the same prerequisites table as Task 2, after the organogram row just added, add:

```markdown
| Framework usage (DB) | `pwin-platform` (`get_buyer_framework_usage`) | `procurementBehaviour.frameworkUsage`, `procurementBehaviour.preferredRoutes` |
```

- [ ] **Step 2: Add the MCP call to Step 0**

After the `find_evaluators` call added in Task 2, add:

```markdown
**3c.** `get_buyer_framework_usage(buyerName)` — preferred. Returns frameworks the buyer routes spend through, ranked by call-off value. Use to populate `procurementBehaviour.frameworkUsage` and `procurementBehaviour.preferredRoutes`. Set `meta.prerequisitesPresentAt.preferred.frameworkUsageData` to `true` if successful.
```

- [ ] **Step 3: Add flag to `prerequisitesPresentAt`**

In the same `preferred` block updated in Task 2 Step 3, add:

```json
"frameworkUsageData": true
```

- [ ] **Step 4: Add MCP-priority note near the `procurementBehaviour` field guidance**

Find the guidance for populating `procurementBehaviour`. Add:

```markdown
> **Framework data from DB.** If `get_buyer_framework_usage` returned data, use the top frameworks (by call-off value) as the primary `frameworkUsage` list. Include framework name, lot(s) used, and spend volume where available. DB data is sourced directly from FTS contract awards and is more reliable than press inference.
```

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/SKILL.md
git commit -m "feat(buyer-intel): wire get_buyer_framework_usage into Step 0"
```

---

## Task 4: Wire `get_senior_leadership` and `find_evaluators` into incumbency SKILL.md

The incumbency skill assesses `incumbentAdvantage.relationshipEmbeddedness` and `buyerSwitchingPsychology` — both depend on knowing who the senior decision-makers are at the buyer. The organogram tools are not in the incumbency Step 0. Named relationships with Director-level contacts are a quantifiable incumbency advantage (or vulnerability when they've changed), and knowing the likely evaluators informs `procurementContext`.

**Files:**
- Modify: `master/incumbency-advantage-displacement-strategy/SKILL.md`

- [ ] **Step 1: Add to the preferred prerequisites table**

Find the `## Prerequisites` section. In the preferred prerequisites table, add:

```markdown
| Senior leadership (organogram DB) | `pwin-platform` (`get_senior_leadership`, `find_evaluators`) | `incumbentAdvantage.relationshipEmbeddedness`, `buyerSwitchingPsychology`, `procurementContext` |
```

- [ ] **Step 2: Add MCP calls to Step 0**

Find the "check preferred prerequisites" block in Step 0 (after the required prerequisite checks). Add after the last existing preferred call:

```markdown
**[N].** `get_senior_leadership(buyerName)` — preferred. Cross-reference with `incumbentProfile.accountTeam` — named relationships with current Director-level civil servants are a form of incumbency advantage. Set `prerequisitesPresentAt.preferred.organogramData` to `true` if successful.

**[N+1].** `find_evaluators(buyerName)` — preferred. Returns likely evaluators (PAC witnesses at Director level). Use to populate `procurementContext` (who will evaluate) and inform `buyerSwitchingPsychology` — evaluators who commissioned the incumbent carry relationship risk for a challenger. Set `prerequisitesPresentAt.preferred.evaluatorData` to `true` if successful.
```

Replace `[N]` and `[N+1]` with the next sequential numbers after the existing preferred calls.

- [ ] **Step 3: Add flags to the `prerequisitesPresentAt` schema block**

Find the `prerequisitesPresentAt` YAML block. Add to the `preferred` object:

```yaml
organogramData: boolean
evaluatorData: boolean
```

- [ ] **Step 4: Add guidance note to `relationshipEmbeddedness`**

Find the section of the skill describing how to assess `incumbentAdvantage.relationshipEmbeddedness`. Add:

```markdown
> **Cross-reference organogram data.** If `get_senior_leadership` returned results, check whether any named account-team members from the incumbent profile appear in the current Director-level leadership list. If the key relationship contacts have left or moved, that is a vulnerability not an advantage. Evaluators from `find_evaluators` who overlap with the original commissioning decision strengthen the embeddedness case.
```

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/SKILL.md
git commit -m "feat(incumbency): wire get_senior_leadership and find_evaluators into Step 0"
```

---

## Task 5: Create incumbency HTML renderer

The incumbency skill produces JSON and a markdown narrative but has no HTML renderer. This gaps the consultant experience — buyer and supplier dossiers both have branded HTML reports, but the incumbency assessment is only viewable as raw JSON or markdown. This task creates `render_assessment.py` following the same pattern as the other renderers.

**Files:**
- Create: `master/incumbency-advantage-displacement-strategy/scripts/__init__.py`
- Create: `master/incumbency-advantage-displacement-strategy/scripts/render_assessment.py`
- Create: `master/incumbency-advantage-displacement-strategy/tests/__init__.py`
- Create: `master/incumbency-advantage-displacement-strategy/tests/test_render_assessment.py`

- [ ] **Step 1: Write failing tests**

Create `master/incumbency-advantage-displacement-strategy/tests/__init__.py` (empty).

Create `master/incumbency-advantage-displacement-strategy/tests/test_render_assessment.py`:

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

```
cd pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy
python -m pytest tests/test_render_assessment.py -v
```

Expected: `ImportError: No module named 'render_assessment'`

- [ ] **Step 3: Create `scripts/__init__.py`** (empty file)

- [ ] **Step 4: Create `scripts/render_assessment.py`**

```python
#!/usr/bin/env python3
"""Render an incumbency assessment JSON to branded BidEquity HTML.

Usage: python render_assessment.py <slug>

Reads from C:\\Users\\User\\.pwin\\intel\\incumbency\\<slug>-assessment.json
and writes the rendered HTML to both the intel cache and the workspace folder.
"""
import json
import os
import re
import sys
from datetime import date

NAVY = "#021744"
SAND = "#F7F4EE"
AQUA = "#7ADDE2"
TEAL = "#5CA3B6"
PALE = "#E0F4F6"
TERRA = "#D17A74"
GOLD = "#C9A84C"

CITATION_RE = re.compile(r"\[(INC-CLM-[0-9A-Z-]+|CLM-[0-9A-Z-]+)\]")

VERDICT_COLOURS = {
    "high_risk": TERRA,
    "medium_risk": AQUA,
    "low_risk": PALE,
    "opportunity": GOLD,
}
VERDICT_LABELS = {
    "high_risk": "HIGH RISK",
    "medium_risk": "MEDIUM RISK",
    "low_risk": "LOW RISK",
    "opportunity": "OPPORTUNITY",
}


def _linkify_citations(text: str) -> str:
    if not isinstance(text, str):
        return text
    return CITATION_RE.sub(
        lambda m: f'<a class="claim-cite" href="#claim-{m.group(1)}">[{m.group(1)}]</a>',
        text,
    )


def _render_claims_block(claims: list) -> str:
    if not claims:
        return ""
    rows = []
    for c in claims:
        cid = c.get("claimId", "?")
        rows.append(
            f'<dt id="claim-{cid}">[{cid}] '
            f'(tier {c.get("sourceTier", "?")} — {c.get("sourceDate") or "undated"})</dt>'
            f'<dd><p>{c.get("claimText", "")}</p>'
            f'<p class="claim-source"><strong>Source:</strong> {c.get("source", "?")}</p>'
            f'<p class="claim-meta">Asserted {c.get("claimDate", "?")}</p></dd>'
        )
    return (
        '<div class="card"><h2>Claims and evidence</h2>'
        '<dl class="claims">' + "".join(rows) + '</dl></div>'
    )


def ev(w, default="—"):
    if isinstance(w, dict):
        return _linkify_citations(str(w.get("value", default)))
    return _linkify_citations(str(w)) if w else default


def score_bar(score, mx=10):
    pct = int((score / mx) * 100)
    col = TERRA if score >= 7 else (AQUA if score >= 4 else PALE)
    return (
        f'<div style="background:{PALE};border-radius:4px;height:10px;width:200px;'
        f'display:inline-block;vertical-align:middle">'
        f'<div style="background:{col};width:{pct}%;height:10px;border-radius:4px"></div></div>'
        f'<span style="font-family:DM Mono,monospace;margin-left:10px;font-size:0.9em">{score}/10</span>'
    )


def section_rows(section_data: dict, fields: list) -> str:
    rows = []
    for label, key in fields:
        val = section_data.get(key)
        if isinstance(val, list):
            items = "".join(f"<li>{ev(i)}</li>" for i in val)
            rows.append(
                f'<tr><td class="lbl">{label}</td>'
                f'<td><ul style="margin:0;padding-left:18px">{items}</ul></td></tr>'
            )
        elif val:
            rows.append(f'<tr><td class="lbl">{label}</td><td>{ev(val)}</td></tr>')
    return "".join(rows) or '<tr><td colspan="2" style="color:#999;font-size:0.85em">No data</td></tr>'


def build_html(d: dict) -> str:
    """Build the full HTML string from an assessment dict. Testable without file I/O."""
    meta = d.get("meta", {})
    judgement = d.get("executiveJudgement") or {}
    verdict_key = judgement.get("overallVerdict", "")
    verdict_col = VERDICT_COLOURS.get(verdict_key, PALE)
    verdict_label = VERDICT_LABELS.get(verdict_key, verdict_key.upper().replace("_", " "))
    verdict_rationale = ev(judgement.get("verdictRationale", ""))
    confidence = judgement.get("confidenceLevel", "")

    go = d.get("goNoGoImplications") or {}
    go_stance = ev(go.get("recommendedStance", ""))
    pwin_alignment = ev(go.get("pwinScoreAlignment", ""))

    adv = d.get("incumbentAdvantage") or {}
    adv_score = adv.get("totalAdvantageScore", 0)
    vuln = d.get("incumbentVulnerabilities") or {}
    vuln_score = vuln.get("totalVulnerabilityScore", 0)

    register = d.get("sourceRegister") or {}
    sources = register.get("sources", [])
    src_rows = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{s.get("sourceId")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em">{s.get("tier")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em">{s.get("title")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{s.get("accessDate")}</td></tr>'
        for s in sources
    )

    version_log = meta.get("versionLog", [])
    version_rows = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{v.get("version")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{v.get("date")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em;text-transform:uppercase">{v.get("mode")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em">{v.get("summary")}</td></tr>'
        for v in version_log
    )

    adv_rows = section_rows(adv, [
        ("Relationship embeddedness", "relationshipEmbeddedness"),
        ("Switching cost to buyer", "switchingCostTobuyer"),
        ("Knowledge asymmetry", "knowledgeAsymmetry"),
        ("Solution entrenchment", "solutionEntrenchment"),
        ("Political capital", "politicalCapital"),
    ])
    vuln_rows = section_rows(vuln, [
        ("Performance record", "performanceRecord"),
        ("Financial stress", "financialStressSignals"),
        ("Leadership instability", "leadershipInstability"),
        ("Reputational risk", "reputationalRisk"),
        ("Innovation deficit", "innovationDeficit"),
    ])
    strategy_rows = section_rows(d.get("strategy") or {}, [
        ("Displacement route", "displacementRoute"),
        ("Win theme anchors", "winThemeAnchors"),
        ("Proof requirements", "proofRequirements"),
        ("Risk mitigation", "riskMitigation"),
    ])
    challenger_rows = section_rows(d.get("challengerPosition") or {}, [
        ("Relative strength", "relativeStrength"),
        ("Credibility gaps", "credibilityGaps"),
        ("Framework access", "frameworkAccess"),
    ])

    bid_actions = d.get("bidExecutionActions") or {}
    action_items = bid_actions.get("actions", []) if isinstance(bid_actions, dict) else []
    action_list = "".join(f'<li style="margin-bottom:6px">{ev(a)}</li>' for a in action_items)

    html = (
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{meta.get("incumbentName", "Incumbency")} — Assessment</title>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Cormorant+Garamond:wght@400;600;700&family=DM+Mono:wght@400;500'
        '&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">'
        '<style>'
        f'*{{box-sizing:border-box;margin:0;padding:0}} body{{background:{SAND};font-family:DM Sans,sans-serif;color:{NAVY}}}'
        f'.hdr{{background:{NAVY};color:{SAND};padding:32px 48px}}'
        '.hdr h1{font-family:Cormorant Garamond,serif;font-size:2.2em;font-weight:700}'
        f'.sub{{font-family:DM Mono,monospace;font-size:0.78em;color:{AQUA};margin-top:6px}}'
        '.body{max-width:1100px;margin:0 auto;padding:32px 24px}'
        f'.card{{background:#fff;border-radius:8px;padding:24px;margin-bottom:24px;box-shadow:0 1px 4px rgba(2,23,68,.07)}}'
        f'.card h2{{font-family:Cormorant Garamond,serif;color:{NAVY};font-size:1.4em;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid {PALE}}}'
        'table{width:100%;border-collapse:collapse} tr:nth-child(even){background:#F7F4EE}'
        f'.lbl{{padding:6px 12px;color:#666;font-size:0.85em;width:220px}}'
        f'td{{padding:6px 12px;color:{NAVY}}}'
        '.claims{list-style:none}'
        f'.claims dt{{font-weight:600;color:{NAVY};margin-top:14px;font-size:0.88em}}'
        f'.claims dd{{border-left:3px solid {TEAL};padding-left:14px;margin-left:0;margin-bottom:8px}}'
        '.claim-source,.claim-meta{font-size:0.78em;color:#94A3B8;margin:2px 0}'
        f'a.claim-cite{{color:{TEAL};text-decoration:none;font-size:0.85em;font-weight:600}}'
        'a.claim-cite:hover{text-decoration:underline}'
        '</style></head><body>'
        '<div class="hdr">'
        f'<h1>Incumbency Assessment — {meta.get("incumbentName", "")}</h1>'
        f'<div class="sub">'
        f'{meta.get("buyerName", "")} &nbsp;|&nbsp; {meta.get("contractTitle", "")} &nbsp;|&nbsp; '
        f'v{meta.get("version", "1.0.0")} &nbsp;|&nbsp; Built {meta.get("builtDate", "--")} &nbsp;|&nbsp; '
        f'{meta.get("sourceCount", 0)} sources'
        f'<span style="background:{TEAL};color:{SAND};padding:2px 10px;border-radius:12px;'
        f'font-family:DM Mono,monospace;font-size:0.75em;margin-left:10px">INTERNAL</span></div></div>'
        '<div class="body">'
        f'<div class="card" style="border-left:6px solid {verdict_col}">'
        f'<h2>Executive Verdict</h2>'
        f'<div style="display:flex;align-items:flex-start;gap:24px">'
        f'<div style="background:{verdict_col};color:{NAVY};padding:12px 24px;border-radius:6px;'
        f'font-family:DM Mono,monospace;font-weight:700;font-size:1.1em;white-space:nowrap">{verdict_label}</div>'
        f'<div><p style="font-size:0.95em;line-height:1.6">{verdict_rationale}</p>'
        f'<p style="margin-top:8px;font-size:0.8em;color:#666">Confidence: <strong>{confidence}</strong></p>'
        f'</div></div>'
        f'<div style="margin-top:16px;padding:12px;background:{PALE};border-radius:4px">'
        f'<strong>Recommended stance:</strong> {go_stance}'
        f'<br><span style="font-size:0.85em;color:#666;margin-top:4px;display:block">PWIN alignment: {pwin_alignment}</span>'
        f'</div></div>'
        '<div class="card"><h2>Score Summary</h2>'
        f'<table><tr><td class="lbl">Incumbent advantage</td><td>{score_bar(adv_score)}</td></tr>'
        f'<tr><td class="lbl">Incumbent vulnerability</td><td>{score_bar(vuln_score)}</td></tr></table></div>'
        '<div class="card"><h2>Incumbent Advantage</h2>'
        f'<table>{adv_rows}</table></div>'
        '<div class="card"><h2>Incumbent Vulnerabilities</h2>'
        f'<table>{vuln_rows}</table></div>'
        '<div class="card"><h2>Challenger Position</h2>'
        f'<table>{challenger_rows}</table></div>'
        '<div class="card"><h2>Strategy</h2>'
        f'<table>{strategy_rows}</table></div>'
        + (f'<div class="card"><h2>Bid Execution Actions</h2>'
           f'<ul style="padding-left:18px;line-height:1.8">{action_list}</ul></div>'
           if action_list else "")
        + '<div class="card"><h2>Sources</h2><table>'
        + f'<thead><tr style="background:{NAVY};color:{SAND}">'
        + '<th style="padding:6px 12px;text-align:left">ID</th>'
        + '<th style="padding:6px 12px;text-align:left">Tier</th>'
        + '<th style="padding:6px 12px;text-align:left">Title</th>'
        + '<th style="padding:6px 12px;text-align:left">Accessed</th></tr></thead>'
        + f'<tbody>{src_rows}</tbody></table></div>'
        + (f'<div class="card"><h2>Version History</h2><table>'
           f'<thead><tr style="background:{NAVY};color:{SAND}">'
           f'<th style="padding:6px 12px;text-align:left">Version</th>'
           f'<th style="padding:6px 12px;text-align:left">Date</th>'
           f'<th style="padding:6px 12px;text-align:left">Mode</th>'
           f'<th style="padding:6px 12px;text-align:left">Summary</th></tr></thead>'
           f'<tbody>{version_rows}</tbody></table></div>' if version_rows else "")
        + f'<div style="text-align:center;padding:16px;font-family:DM Mono,monospace;font-size:0.72em;color:#999">'
        + f'BidEquity Intelligence Platform &nbsp;|&nbsp; INTERNAL USE ONLY &nbsp;|&nbsp; Generated {date.today().isoformat()}</div>'
    )
    html += _render_claims_block(d.get("claims", []))
    html += '</div></body></html>'
    return html


def render(slug):
    intel = fr"C:\Users\User\.pwin\intel\incumbency\{slug}-assessment.json"
    ws_dir = r"C:\Users\User\Documents\Claude\Projects\Bid Equity\incumbency"
    os.makedirs(ws_dir, exist_ok=True)
    os.makedirs(r"C:\Users\User\.pwin\intel\incumbency", exist_ok=True)

    with open(intel, encoding="utf-8") as f:
        d = json.load(f)

    html = build_html(d)
    out_paths = [
        fr"C:\Users\User\.pwin\intel\incumbency\{slug}-assessment.html",
        os.path.join(ws_dir, f"{slug}-assessment.html"),
    ]
    for p in out_paths:
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"Written: {p}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_assessment.py <slug>")
        sys.exit(1)
    render(sys.argv[1])
```

- [ ] **Step 5: Run tests — confirm all pass**

```
cd pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy
python -m pytest tests/test_render_assessment.py -v
```

Expected:
```
test_header_renders PASSED
test_executive_verdict_renders PASSED
test_advantage_score_renders PASSED
test_vulnerability_score_renders PASSED
test_go_no_go_renders PASSED
test_claims_block_renders PASSED
test_empty_claims_renders_without_error PASSED
7 passed
```

- [ ] **Step 6: Commit**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/scripts/
git add pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/tests/
git commit -m "feat(incumbency): HTML renderer with verdict, scores, strategy, and claims block"
```
