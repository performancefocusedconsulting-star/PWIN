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
