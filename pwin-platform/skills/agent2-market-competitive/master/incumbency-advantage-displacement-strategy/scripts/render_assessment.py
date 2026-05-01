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
