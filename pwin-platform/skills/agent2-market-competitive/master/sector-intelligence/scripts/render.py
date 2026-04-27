#!/usr/bin/env python3
"""Render a sector brief JSON to branded BidEquity HTML.

Usage: python render.py <slug>

Reads from C:\\Users\\User\\.pwin\\intel\\sectors\\<slug>-brief.json
and writes the rendered HTML to both the intel cache and the workspace folder.
"""
import json
import os
import sys
from datetime import date

NAVY = "#021744"
SAND = "#F7F4EE"
AQUA = "#7ADDE2"
TEAL = "#5CA3B6"
PALE = "#E0F4F6"
TERRA = "#D17A74"


def ev(w, default="--"):
    if isinstance(w, dict):
        return str(w.get("value", default))
    return str(w) if w else default


def badge(w):
    if not isinstance(w, dict):
        return ""
    c = w.get("confidence", "")
    col = {"high": AQUA, "medium": TERRA, "low": SAND}.get(c, SAND)
    return (f'<span style="background:{col};color:{NAVY};padding:1px 6px;'
            f'border-radius:3px;font-size:0.75em;margin-left:6px">{c}</span>')


def section_card(code, title, data, fields):
    rows = []
    for label, key in fields:
        val = data.get(key)
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
    body = "".join(rows)
    return (f'<div style="margin-bottom:24px">'
            f'<h3 style="font-family:Cormorant Garamond,serif;color:{NAVY};'
            f'font-size:1.1em;margin:0 0 8px 0;padding-bottom:4px;'
            f'border-bottom:1px solid {PALE}">{code} -- {title}</h3>'
            f'<table style="width:100%;border-collapse:collapse">{body}</table></div>')


def render(slug):
    intel = fr"C:\Users\User\.pwin\intel\sectors\{slug}-brief.json"
    ws_dir = r"C:\Users\User\Documents\Claude\Projects\Bid Equity\sectors"
    os.makedirs(ws_dir, exist_ok=True)
    os.makedirs(r"C:\Users\User\.pwin\intel\sectors", exist_ok=True)

    with open(intel, encoding="utf-8") as f:
        d = json.load(f)

    meta = d.get("meta", {})
    summ = d.get("sectorSummary", {})

    risk_col = {"high": TERRA, "medium": AQUA, "low": PALE}.get(
        summ.get("sectorRiskLevel", ""), PALE
    )

    summary_rows = (
        f'<tr><td class="lbl">Addressable spend</td><td>{ev(summ.get("addressableSpendGbpbn"))}{badge(summ.get("addressableSpendGbpbn"))}</td></tr>'
        + f'<tr><td class="lbl">Spend trajectory</td><td>{summ.get("spendTrajectory","--")}</td></tr>'
        + f'<tr><td class="lbl">Avg contract value</td><td>{ev(summ.get("avgContractValueGbpm"))}{badge(summ.get("avgContractValueGbpm"))}</td></tr>'
        + f'<tr><td class="lbl">Social value weight</td><td>{ev(summ.get("socialValueWeightTypicalPct"))}{badge(summ.get("socialValueWeightTypicalPct"))}</td></tr>'
        + f'<tr><td class="lbl">Quality/price split</td><td>{ev(summ.get("qualityPriceSplitTypical"))}{badge(summ.get("qualityPriceSplitTypical"))}</td></tr>'
        + f'<tr><td class="lbl">Sector risk</td>'
        + f'<td><span style="background:{risk_col};color:{NAVY};padding:2px 8px;border-radius:4px;font-weight:600">{summ.get("sectorRiskLevel","--").upper()}</span></td></tr>'
        + f'<tr><td class="lbl">Risk rationale</td><td style="font-size:0.88em">{summ.get("riskRationale","--")}</td></tr>'
    )

    top_frameworks = "".join(f"<li>{f}</li>" for f in summ.get("topFrameworks", []))
    key_buyers = "".join(f"<li>{b}</li>" for b in summ.get("keyBuyerOrganisations", []))
    recompetes = "".join(f"<li>{r}</li>" for r in summ.get("majorRecompetes24m", []))

    register = d.get("sourceRegister", {})
    sources = register.get("sources", [])
    src_rows = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{s.get("sourceId")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em">{s.get("tier")}</td>'
        f'<td style="padding:6px 12px;font-size:0.85em">{s.get("title")}</td>'
        f'<td style="padding:6px 12px;font-family:DM Mono,monospace;font-size:0.8em">{", ".join(s.get("sectionsSupported",[]))}</td>'
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
        f'<title>{meta.get("sectorName","Sector")} -- Intelligence Brief</title>'
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
        f'.lbl{{padding:6px 12px;color:#666;font-size:0.85em;width:220px;font-family:DM Sans,sans-serif}}'
        f'td{{padding:6px 12px;font-family:DM Sans,sans-serif;color:{NAVY}}}'
        '</style></head><body>'
        '<div class="hdr">'
        f'<h1>{meta.get("sectorName","Sector Intelligence Brief")}</h1>'
        f'<div class="sub">v{meta.get("version","1.0.0")} &nbsp;|&nbsp; '
        f'Built {meta.get("builtDate","--")} &nbsp;|&nbsp; '
        f'{meta.get("sourceCount",0)} sources &nbsp;|&nbsp; '
        f'<span style="text-transform:uppercase">{meta.get("mode","build")}</span>'
        f'<span style="background:{TEAL};color:{SAND};padding:2px 10px;border-radius:12px;'
        f'font-family:DM Mono,monospace;font-size:0.75em;margin-left:10px">INTERNAL</span></div></div>'
        '<div class="body">'
        '<div class="card"><h2>Sector Summary</h2>'
        '<table>'
        + summary_rows
        + f'<tr><td class="lbl">Top frameworks</td><td><ul style="margin:0;padding-left:18px">{top_frameworks}</ul></td></tr>'
        + f'<tr><td class="lbl">Key buyers</td><td><ul style="margin:0;padding-left:18px">{key_buyers}</ul></td></tr>'
        + f'<tr><td class="lbl">Major recompetes (24m)</td><td><ul style="margin:0;padding-left:18px">{recompetes}</ul></td></tr>'
        + '</table></div>'
        + '<div class="card"><h2>Section Intelligence</h2>'
        + section_card("S1", "Policy & Regulatory Environment", d.get("S1", {}), [
            ("Policy direction", "policyDirectionSummary"),
            ("Active legislation", "keyLegislationActive"),
            ("Pending legislation", "keyLegislationPending"),
            ("Scrutiny & oversight", "scrutinyAndOversight"),
            ("Policy risks", "policyRisks"),
            ("Key documents (12m)", "keyPolicyDocuments12m"),
        ])
        + section_card("S2", "Spending & Budget Landscape", d.get("S2", {}), [
            ("Total addressable spend", "totalAddressableSpendGbpbn"),
            ("Budget trajectory", "budgetTrajectory"),
            ("SR commitments", "srCommitments"),
            ("Top frameworks by value", "topFrameworksByValue"),
        ])
        + section_card("S3", "Market Trends & Dynamics", d.get("S3", {}), [
            ("Demand drivers", "demandDrivers"),
            ("Delivery model shifts", "serviceDeliveryModelShifts"),
            ("Technology adoption", "technologyAdoption"),
            ("Workforce context", "workforceContext"),
            ("ESG / social value", "esgSocialValueRequirements"),
        ])
        + section_card("S4", "Trade Press & Commentary", d.get("S4", {}), [
            ("Key publications", "keyPublications"),
            ("Commentary themes (90d)", "commentaryThemes90d"),
            ("Trade body positions", "tradeBodyPositions"),
            ("Analyst views", "analystViews"),
            ("Parliamentary activity (90d)", "parliamentaryActivity90d"),
        ])
        + section_card("S5", "Peer Comparisons & Benchmarks", d.get("S5", {}), [
            ("International comparisons", "internationalComparisons"),
            ("Performance benchmarks", "performanceBenchmarks"),
            ("Innovation cases", "deliveryInnovationCases"),
            ("Failure cases", "deliveryFailureCases"),
        ])
        + section_card("S6", "Implications for Pursuit & Positioning", d.get("S6", {}), [
            ("Buyer priorities", "buyerPrioritiesForSolutionDesign"),
            ("Evaluation criteria patterns", "evaluationCriteriaPatterns"),
            ("Differentiation angles", "differentiationAngles"),
            ("Qualification risk flags", "qualificationRiskFlags"),
        ])
        + '</div>'
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
        + '</div></body></html>'
    )

    out_paths = [
        fr"C:\Users\User\.pwin\intel\sectors\{slug}-brief.html",
        os.path.join(ws_dir, f"{slug}-brief.html"),
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
