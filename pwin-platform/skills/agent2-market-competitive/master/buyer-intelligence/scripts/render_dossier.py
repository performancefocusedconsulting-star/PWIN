#!/usr/bin/env python3
"""
BidEquity Buyer Intelligence Dossier Renderer v3.0

Reads a v3.0 JSON dossier and produces a BidEquity-branded standalone HTML report.

New in v3.0 (vs v2.3):
  - Renders procurementBehaviourSnapshot (analytics snapshot)
  - Renders decisionUnitAssumptions (roles, interests, tensions, dominant lens)
  - Renders pursuitImplications (7th intelligence lens)
  - Renders actionRegister (living gap/action tracker)
  - Missing fields within existing sections: regulatoryPressures,
    publicStatementsOfIntent, programme SRO/timeline/dependencies/targets,
    spendClassification, outcomesSought, consequencesOfInaction,
    commissioningCycleStage, approvalsPending, marketEngagementLikelihood,
    totalAwards/totalValue/dataWindow, sharedServiceArrangements,
    evidencePreferences, supplierInteractionStyle, presentationStyle,
    languageAndFraming, contractualCaution, preferredCommercialModels,
    paymentTermsNorms, barriersToEntry, vulnerabilitySignals per incumbent,
    priorContracts, activeProgrammes, pastBids, executiveRelationships,
    knownAdvocates, knownBlockers, positioningSensitivities

Brand system:
  - Midnight Navy #021744 (primary background)
  - Soft Sand #F7F4EE (page canvas, body text on dark)
  - Bright Aqua #7ADDE2 (headlines, key numbers, accents)
  - Calm Teal #5CA3B6 (secondary accent, evidence borders)
  - Pale Aqua #E0F4F6 (light backgrounds, tags)
  - Light Terracotta #D17A74 (risk indicators, warnings)
  - Descriptor Cyan #60F5F7 (subtitle descriptor text)

Usage:
  python3 render_dossier.py <input.json> <output.html>
"""

import json
import html
import sys
import os
from datetime import datetime
import re


def e(s):
    """HTML-escape a string, returning empty string for None."""
    return html.escape(str(s)) if s else ""


def badge(conf):
    """Render a confidence badge."""
    colors = {
        "high": "#2d7d46",
        "medium": "#b8860b",
        "low": "#D17A74",
        "none": "#94A3B8",
    }
    c = colors.get(conf, "#94A3B8")
    return (
        f'<span style="background:{c};color:#fff;padding:2px 10px;'
        f'border-radius:3px;font-size:0.7em;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.05em">{e(conf)}</span>'
    )


def priority_badge(priority):
    colors = {
        "critical": "#C0392B",
        "high": "#b8860b",
        "medium": "#5CA3B6",
        "low": "#94A3B8",
    }
    c = colors.get(priority, "#94A3B8")
    return (
        f'<span style="background:{c};color:#fff;padding:2px 8px;'
        f'border-radius:3px;font-size:0.7em;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.05em">{e(priority)}</span>'
    )


def category_badge(cat):
    colors = {
        "stance": "#021744",
        "language": "#5CA3B6",
        "evidence": "#2d7d46",
        "commercial": "#b8860b",
        "engagement": "#7ADDE2",
        "risk-management": "#D17A74",
        "timing": "#8e44ad",
        "structural": "#34495e",
    }
    text_colors = {
        "engagement": "#021744",
    }
    bg = colors.get(cat, "#94A3B8")
    fg = text_colors.get(cat, "#fff")
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border-radius:3px;font-size:0.72em;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.04em">{e(cat)}</span>'
    )


def ev(field, label=None):
    """Render an evidenced field or plain string."""
    if field is None:
        return ""
    if isinstance(field, str):
        return f"<p>{e(field)}</p>"
    if isinstance(field, dict) and "value" in field:
        v = field
        val = v["value"]
        # value may be a list (e.g. preferredCommercialModels)
        if isinstance(val, list):
            val_str = ", ".join(str(x) for x in val)
        else:
            val_str = str(val) if val is not None else ""
        refs = ", ".join(v.get("sourceRefs", [])) if v.get("sourceRefs") else ""
        typ = v.get("type", "")
        conf = v.get("confidence", "")
        rat = v.get("rationale", "")
        out = (
            '<div style="margin-bottom:14px;border-left:3px solid #5CA3B6;'
            'padding-left:14px">'
        )
        if label:
            out += f'<strong style="color:#021744;font-size:0.95em">{e(label)}</strong><br>'
        out += f'<p style="margin:4px 0;line-height:1.6">{_linkify_citations(e(val_str))}</p>'
        out += (
            f'<div style="font-size:0.78em;color:#94A3B8;margin-top:4px">'
            f"Type: {e(typ)} | Confidence: {badge(conf)} | Sources: {e(refs)}"
            f"</div>"
        )
        if rat:
            out += (
                f'<div style="font-size:0.78em;color:#94A3B8;margin-top:4px">'
                f"<em>Rationale: {e(rat)}</em></div>"
            )
        out += "</div>"
        return out
    return f"<p>{e(str(field))}</p>"


CITATION_RE = re.compile(r"\[(CLM-[0-9A-Z-]+|[A-Z]+-CLM-[0-9A-Z-]+)\]")


def _linkify_citations(text: str) -> str:
    """Replace [CLM-id] markers in narrative with anchor links."""
    if not isinstance(text, str):
        return text
    return CITATION_RE.sub(
        lambda m: (
            f'<a class="claim-cite" href="#claim-{m.group(1)}">'
            f'[{m.group(1)}]</a>'
        ),
        text,
    )


def _render_claims_block(claims: list) -> str:
    if not claims:
        return ""
    rows = []
    for c in claims:
        cid = c.get("claimId", "?")
        rows.append(
            f'<dt id="claim-{e(cid)}">[{e(cid)}] '
            f'(tier {c.get("sourceTier", "?")} '
            f'— {e(c.get("sourceDate") or "undated")})</dt>'
            f'<dd><p>{e(c.get("claimText", ""))}</p>'
            f'<p class="claim-source"><strong>Source:</strong> '
            f'{e(c.get("source", "?"))}</p>'
            f'<p class="claim-meta">Asserted '
            f'{e(c.get("claimDate", "?"))}.</p></dd>'
        )
    return (
        '<section class="claims-block"><h2>Claims and evidence</h2>'
        '<dl class="claims">' + "".join(rows) + '</dl></section>'
    )


def render(data):
    """Render complete HTML from dossier JSON."""
    meta = data["meta"]
    snap = data["buyerSnapshot"]
    org = data.get("organisationContext") or {}
    strat = data.get("strategicPriorities") or {}
    comm = data.get("commissioningContextHypotheses") or {}
    proc = data.get("procurementBehaviour") or {}
    proc_snap = data.get("procurementBehaviourSnapshot") or {}
    dec = data.get("decisionUnitAssumptions") or {}
    cult = data.get("cultureAndPreferences") or {}
    risk_p = data.get("commercialAndRiskPosture") or {}
    supp = data.get("supplierEcosystem") or {}
    rel = data.get("relationshipHistory") or {}
    risks = data.get("risksAndSensitivities") or {}
    pursuit_impl = data.get("pursuitImplications") or {}
    act_reg = data.get("actionRegister") or {}
    sreg = data.get("sourceRegister") or {}

    grid_mark = """<svg width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="10" height="10" rx="1" fill="#7ADDE2"/>
      <rect x="13" y="0" width="10" height="10" rx="1" fill="#5CA3B6"/>
      <rect x="26" y="0" width="10" height="10" rx="1" fill="#7ADDE2"/>
      <rect x="0" y="13" width="10" height="10" rx="1" fill="#5CA3B6"/>
      <rect x="13" y="13" width="10" height="10" rx="1" fill="#D17A74"/>
      <rect x="26" y="13" width="10" height="10" rx="1" fill="#5CA3B6"/>
      <rect x="0" y="26" width="10" height="10" rx="1" fill="#7ADDE2"/>
      <rect x="13" y="26" width="10" height="10" rx="1" fill="#5CA3B6"/>
      <rect x="26" y="26" width="10" height="10" rx="1" fill="#7ADDE2"/>
    </svg>"""

    depth_label = e(meta.get("depthMode", "standard")).upper()

    # Build action register summary for header
    act_summary = ""
    if act_reg.get("openCriticalCount") or act_reg.get("openHighCount"):
        crit = act_reg.get("openCriticalCount", 0)
        high = act_reg.get("openHighCount", 0)
        med = act_reg.get("openMediumCount", 0)
        act_summary = f'{crit} critical &bull; {high} high &bull; {med} medium open'

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Buyer Intelligence Dossier — {e(meta['buyerName'])}</title>
<link href="https://fonts.googleapis.com/css2?family=Spline+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1a1a2e;
  background: #F7F4EE;
  line-height: 1.65;
  font-size: 14px;
}}
.container {{ max-width: 960px; margin: 0 auto; padding: 24px; }}

/* Header */
.header {{
  background: #021744;
  color: #F7F4EE;
  padding: 40px 36px 32px;
  border-radius: 6px;
  margin-bottom: 28px;
  position: relative;
}}
.lockup {{
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}}
.lockup-text {{ display: flex; flex-direction: column; gap: 2px; }}
.lockup-brand {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 14px; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase; color: #F7F4EE;
}}
.lockup-descriptor {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 10px; font-weight: 500;
  letter-spacing: 0.12em; text-transform: uppercase; color: #60F5F7;
}}
.header h1 {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 2em; font-weight: 700;
  margin-bottom: 6px; color: #7ADDE2; letter-spacing: -0.01em;
}}
.header .subtitle {{ color: #F7F4EE; font-size: 0.95em; opacity: 0.85; }}
.meta-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 10px; margin-top: 20px;
}}
.meta-item {{
  background: rgba(255,255,255,0.06);
  padding: 8px 12px; border-radius: 4px;
  font-size: 0.82em; color: #E0F4F6;
}}
.meta-label {{
  font-weight: 600; color: #7ADDE2;
  font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.04em;
}}
.act-alert {{
  margin-top: 14px;
  background: rgba(192,57,43,0.2);
  border: 1px solid rgba(192,57,43,0.5);
  border-radius: 4px; padding: 8px 14px;
  font-size: 0.82em; color: #F7F4EE;
}}
.act-alert strong {{ color: #ff8f87; }}

/* Sections */
section {{
  background: #fff; border-radius: 6px;
  padding: 28px 32px; margin-bottom: 18px;
  border: 1px solid rgba(2,23,68,0.06);
}}
section h2 {{
  font-family: 'Spline Sans', sans-serif;
  color: #021744; font-size: 1.2em; font-weight: 600;
  border-bottom: 2px solid #7ADDE2;
  padding-bottom: 8px; margin-bottom: 18px;
  display: flex; align-items: center; gap: 10px;
}}
section h3 {{
  font-family: 'Spline Sans', sans-serif;
  color: #021744; font-size: 1em; font-weight: 600;
  margin: 20px 0 10px;
}}
section h4 {{
  font-family: 'Spline Sans', sans-serif;
  color: #344;
  font-size: 0.92em; font-weight: 600; margin: 14px 0 6px;
}}

/* Stats row */
.stats-row {{
  display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 18px;
}}
.stat-cell {{
  background: #E0F4F6; border-radius: 6px;
  padding: 12px 18px; flex: 1; min-width: 120px;
}}
.stat-cell .stat-value {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 1.4em; font-weight: 700; color: #021744;
}}
.stat-cell .stat-label {{
  font-size: 0.75em; color: #5CA3B6;
  text-transform: uppercase; letter-spacing: 0.04em;
}}
.stat-cell.alert {{ background: rgba(209,122,116,0.12); }}
.stat-cell.alert .stat-value {{ color: #D17A74; }}

/* Risk items */
.risk-item {{
  background: rgba(209,122,116,0.08);
  border-left: 3px solid #D17A74;
  padding: 10px 14px; margin-bottom: 8px;
  border-radius: 0 4px 4px 0;
  font-size: 0.88em; line-height: 1.5;
}}

/* Programmes */
.programme {{
  border: 1px solid #E0F4F6; border-radius: 6px;
  padding: 14px 16px; margin-bottom: 10px;
}}
.programme-header {{
  display: flex; justify-content: space-between;
  align-items: flex-start; gap: 12px; margin-bottom: 8px;
}}
.programme-name {{
  font-family: 'Spline Sans', sans-serif;
  font-weight: 600; color: #021744; font-size: 0.95em;
}}
.programme-meta {{
  font-size: 0.8em; color: #94A3B8; margin-top: 4px;
}}
.programme-meta span {{ margin-right: 14px; }}
.programme-target {{
  font-size: 0.8em; margin-top: 6px;
  background: rgba(45,125,70,0.08);
  border-left: 3px solid #2d7d46;
  padding: 4px 10px;
}}

/* Suppliers */
.supplier {{
  border: 1px solid #E0F4F6; border-radius: 6px;
  padding: 16px 18px; margin-bottom: 12px;
  background: rgba(224,244,246,0.15);
}}
.supplier h4 {{
  font-family: 'Spline Sans', sans-serif;
  color: #021744; font-size: 0.95em; font-weight: 600; margin-bottom: 8px;
}}
.supplier-meta {{
  display: flex; gap: 8px; flex-wrap: wrap;
  font-size: 0.78em; margin-bottom: 8px;
}}
.supplier-meta span {{
  padding: 2px 8px; border-radius: 3px; font-weight: 500;
}}
.vulnerability-section {{
  margin-top: 10px; padding-top: 10px;
  border-top: 1px solid #f0ede6;
}}
.vuln-label {{
  font-size: 0.75em; text-transform: uppercase;
  letter-spacing: 0.04em; color: #94A3B8; margin-bottom: 6px;
}}
.vuln-item {{
  font-size: 0.82em; color: #555; margin-bottom: 3px;
  padding-left: 10px; border-left: 2px solid #D17A74;
}}

/* Decision unit */
.role-block {{
  border: 1px solid #E0F4F6; border-radius: 6px;
  padding: 14px 16px; margin-bottom: 10px;
}}
.role-title {{
  font-family: 'Spline Sans', sans-serif;
  font-weight: 600; color: #021744; font-size: 0.9em;
  text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px;
}}
.role-interest-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px; margin: 12px 0;
}}
.role-interest-card {{
  background: #F7F4EE; border-radius: 5px;
  padding: 12px 14px; border-left: 3px solid #7ADDE2;
}}
.role-interest-card .role-name {{
  font-family: 'Spline Sans', sans-serif;
  font-weight: 600; color: #021744; font-size: 0.82em;
  text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 6px;
}}
.role-interest-card .primary {{ color: #021744; font-size: 0.88em; line-height: 1.45; }}
.role-interest-card .secondary {{ color: #5CA3B6; font-size: 0.8em; margin-top: 4px; }}
.role-interest-card .evidence {{ color: #94A3B8; font-size: 0.75em; margin-top: 4px; font-style: italic; }}
.tension-item {{
  background: rgba(184,134,11,0.08);
  border-left: 3px solid #b8860b;
  padding: 10px 14px; margin-bottom: 8px;
  border-radius: 0 4px 4px 0; font-size: 0.88em;
}}
.tension-between {{
  font-size: 0.75em; color: #b8860b;
  text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px;
}}
.dominant-lens-box {{
  background: #E0F4F6; border: 1px solid #5CA3B6;
  border-radius: 6px; padding: 14px 18px; margin: 12px 0;
}}
.lens-value {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 1.1em; font-weight: 700; color: #021744; margin-bottom: 6px;
  text-transform: capitalize;
}}

/* Language and framing */
.lang-tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }}
.lang-tag {{
  background: #021744; color: #7ADDE2;
  padding: 3px 10px; border-radius: 3px;
  font-size: 0.78em; font-weight: 500;
}}
.lang-tag.avoid {{
  background: rgba(209,122,116,0.12); color: #D17A74;
  border: 1px solid rgba(209,122,116,0.4);
}}
.lang-tag.policy {{
  background: #E0F4F6; color: #5CA3B6;
}}

/* Pursuit implications */
.implication-card {{
  border: 1px solid #E0F4F6; border-radius: 6px;
  padding: 16px 18px; margin-bottom: 12px;
}}
.implication-header {{
  display: flex; align-items: flex-start;
  gap: 10px; margin-bottom: 10px; flex-wrap: wrap;
}}
.implication-text {{
  font-size: 0.95em; font-weight: 600; color: #021744;
  line-height: 1.5; margin-bottom: 8px;
}}
.implication-rationale {{
  font-size: 0.84em; color: #555; line-height: 1.5; margin-bottom: 8px;
}}
.implication-meta {{
  font-size: 0.75em; color: #94A3B8;
  display: flex; flex-wrap: wrap; gap: 12px;
}}
.implication-meta span {{ display: flex; align-items: center; gap: 4px; }}

/* Action register */
.action-count-row {{
  display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px;
}}
.action-count {{
  padding: 8px 16px; border-radius: 5px;
  font-family: 'Spline Sans', sans-serif;
  font-weight: 700; font-size: 0.9em; color: #fff;
}}
.action-card {{
  border: 1px solid #E0F4F6; border-radius: 6px;
  padding: 16px 18px; margin-bottom: 12px;
}}
.action-card.priority-critical {{ border-left: 4px solid #C0392B; }}
.action-card.priority-high {{ border-left: 4px solid #b8860b; }}
.action-card.priority-medium {{ border-left: 4px solid #5CA3B6; }}
.action-card.priority-low {{ border-left: 4px solid #94A3B8; }}
.action-header {{
  display: flex; justify-content: space-between;
  align-items: flex-start; flex-wrap: wrap; gap: 8px;
  margin-bottom: 10px;
}}
.action-id {{
  font-family: 'Spline Sans', sans-serif;
  font-weight: 700; color: #021744; font-size: 0.85em;
}}
.action-gap {{
  font-size: 0.9em; color: #1a1a2e; line-height: 1.5; margin-bottom: 8px;
}}
.action-next-step {{
  background: #F7F4EE; border-radius: 4px;
  padding: 10px 14px; font-size: 0.84em;
  margin-bottom: 8px; line-height: 1.5;
}}
.action-meta {{
  font-size: 0.75em; color: #94A3B8;
  display: flex; flex-wrap: wrap; gap: 12px;
}}
.action-blocks {{
  margin-top: 8px; font-size: 0.75em;
  color: #D17A74;
}}
.action-blocks strong {{ color: #b8860b; }}

/* Contracts table */
.contract-table {{
  width: 100%; border-collapse: collapse; font-size: 0.84em; margin: 10px 0;
}}
.contract-table th {{
  background: #021744; color: #F7F4EE;
  padding: 6px 10px; text-align: left;
  font-family: 'Spline Sans', sans-serif;
  font-weight: 500; letter-spacing: 0.03em;
}}
.contract-table td {{
  padding: 6px 10px; border-bottom: 1px solid #f0ede6; vertical-align: top;
}}
.contract-table tr:hover {{ background: #F7F4EE; }}

/* Pill lists */
.pill-list {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }}
.pill {{
  background: #E0F4F6; color: #021744;
  padding: 3px 10px; border-radius: 3px;
  font-size: 0.8em; font-weight: 500;
}}

/* Source table */
.source-table {{ width: 100%; border-collapse: collapse; font-size: 0.78em; }}
.source-table th {{
  text-align: left; background: #021744;
  color: #F7F4EE; padding: 8px 10px;
  font-family: 'Spline Sans', sans-serif;
  font-weight: 500; letter-spacing: 0.03em;
}}
.source-table td {{
  padding: 6px 10px; border-bottom: 1px solid #f0ede6; vertical-align: top;
}}
.source-table tr:hover {{ background: #F7F4EE; }}
.source-table a {{ color: #5CA3B6; text-decoration: none; }}
.source-table a:hover {{ text-decoration: underline; }}

/* Gap list */
.gap-list {{ list-style: none; }}
.gap-list li {{
  padding: 6px 0; border-bottom: 1px solid #f0ede6;
  font-size: 0.88em; color: #444;
}}
.gap-list li:before {{ content: "\\25B6  "; color: #D17A74; font-size: 0.7em; }}

/* Archetype box */
.archetype-box {{
  background: #E0F4F6; border: 1px solid #5CA3B6;
  border-radius: 6px; padding: 16px 18px; margin: 14px 0;
}}

/* Headline */
.headline {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 1.05em; font-weight: 600;
  color: #021744; margin-bottom: 14px; line-height: 1.45;
}}

/* Caveat */
.caveat {{
  background: rgba(209,122,116,0.06);
  border-left: 3px solid #D17A74;
  padding: 10px 14px; font-size: 0.82em;
  color: #94A3B8; margin-bottom: 16px;
  border-radius: 0 4px 4px 0; font-style: italic;
}}

/* Market refresh */
.refresh-item {{
  background: #E0F4F6; padding: 8px 14px;
  margin: 4px 0; border-radius: 4px;
  font-size: 0.88em; color: #021744;
}}

/* Footer */
.footer {{
  text-align: center; padding: 24px;
  font-size: 0.75em; color: #94A3B8; letter-spacing: 0.02em;
}}
.footer strong {{ color: #5CA3B6; }}

@media print {{
  body {{ background: #fff; }}
  .container {{ max-width: 100%; }}
  section {{ break-inside: avoid; }}
}}

/* Claims block */
.claims {{ list-style: none; }}
.claims dt {{
  font-family: 'Spline Sans', sans-serif;
  font-weight: 600; color: #021744;
  margin-top: 14px; font-size: 0.88em;
}}
.claims dd {{
  border-left: 3px solid #5CA3B6;
  padding-left: 14px; margin-left: 0; margin-bottom: 8px;
}}
.claim-source, .claim-meta {{ font-size: 0.78em; color: #94A3B8; margin: 2px 0; }}
a.claim-cite {{
  color: #5CA3B6; text-decoration: none;
  font-size: 0.85em; font-weight: 600;
}}
a.claim-cite:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="container">

<!-- MASTHEAD -->
<div class="header">
  <div class="lockup">
    {grid_mark}
    <div class="lockup-text">
      <span class="lockup-brand">BID EQUITY</span>
      <span class="lockup-descriptor">PURSUIT INTELLIGENCE</span>
    </div>
  </div>
  <h1>{e(meta['buyerName'])}</h1>
  <div class="subtitle">Buyer Intelligence Dossier v{e(meta['version'])} — {depth_label}</div>
  <div class="meta-grid">
    <div class="meta-item"><span class="meta-label">Sector</span><br>{e(meta.get('sector',''))}</div>
    <div class="meta-item"><span class="meta-label">Generated</span><br>{e(meta['generatedAt'][:10])}</div>
    <div class="meta-item"><span class="meta-label">Sources</span><br>{e(meta.get('sourcesSummary',''))}</div>
    <div class="meta-item"><span class="meta-label">Refresh due</span><br>{e(meta.get('refreshDue',''))}</div>
    <div class="meta-item"><span class="meta-label">Org type</span><br>{e(snap.get('organisationType',''))}</div>
    <div class="meta-item"><span class="meta-label">Budget</span><br>{e(snap.get('annualBudget',''))}</div>
    <div class="meta-item"><span class="meta-label">Headcount</span><br>{"~{:,}".format(snap['headcount']) if snap.get('headcount') else 'Unknown'}</div>
    <div class="meta-item"><span class="meta-label">Remit</span><br>{e(snap.get('geographicRemit',''))}</div>
  </div>
  {f'<div class="act-alert"><strong>Action register:</strong> {act_summary}</div>' if act_summary else ''}
</div>
"""

    # ── EXECUTIVE SUMMARY ──────────────────────────────────────────────────────
    exec_sum = snap.get("executiveSummary", {})
    html_out += f"""
<section>
  <h2>Executive summary</h2>
  <div class="headline">{e(exec_sum.get('headline',''))}</div>
  {"".join(f'<p style="margin-bottom:12px">{_linkify_citations(e(p))}</p>' for p in exec_sum.get('narrative','').split(chr(10)+chr(10)) if p.strip())}

  <h3>Organisational archetype</h3>
  <div class="archetype-box">
    {ev(snap.get('organisationalArchetype'))}
  </div>

  <h3>Key risks for any pursuit</h3>
  {"".join(f'<div class="risk-item">{e(r)}</div>' for r in snap.get('keyRisks',[]))}
</section>
"""

    # ── ORGANISATION CONTEXT ───────────────────────────────────────────────────
    if org:
        leaders = org.get("seniorLeadership", [])
        leader_html = ""
        for l in leaders:
            bg = f" <span style='font-size:0.8em;color:#94A3B8'>— {e(l.get('background',''))}</span>" if l.get('background') else ""
            leader_html += (
                f'<p style="margin-bottom:6px"><strong>{e(l.get("name",""))}</strong> — '
                f'{e(l.get("role",""))} '
                f'(since {e(l.get("since","unknown"))}){bg}</p>'
            )
        units = org.get("keyBusinessUnits", [])
        units_html = " &bull; ".join(e(u) for u in units) if units else ""

        html_out += f"""
<section>
  <h2>Organisation context {badge(org.get('sectionConfidence',''))}</h2>
  {ev(org.get('mandate'), 'Mandate')}
  {ev(org.get('operatingModel'), 'Operating model')}
  {ev(org.get('organisationStructure'), 'Structure')}
  <h3>Key business units</h3>
  <p>{units_html}</p>
  <h3>Senior leadership</h3>
  {leader_html}
  {ev(org.get('fundingModel'), 'Funding model')}
  {ev(org.get('recentChanges'), 'Recent changes')}
</section>
"""

    # ── STRATEGIC PRIORITIES ───────────────────────────────────────────────────
    if strat:
        themes_html = "".join(ev(t) for t in strat.get("publishedStrategyThemes", []))

        progs_html = ""
        for p in strat.get("majorProgrammes", []):
            targets = p.get("quantifiedTargets") or []
            targets_html = ""
            for qt in targets:
                targets_html += (
                    f'<div class="programme-target">'
                    f'<strong>{e(qt.get("metric",""))}:</strong> {e(qt.get("value",""))} '
                    f'{"by " + e(qt.get("byWhen","")) if qt.get("byWhen") else ""} '
                    f'<em style="color:#94A3B8">({e(qt.get("stretchOrCommitted",""))})</em>'
                    f'</div>'
                )
            deps = p.get("dependencies") or []
            deps_html = (
                f'<div style="font-size:0.78em;color:#94A3B8;margin-top:6px">'
                f'<strong>Dependencies:</strong> {e(", ".join(str(d) for d in deps))}</div>'
                if deps else ""
            )
            srefs = ", ".join(p.get("sourceRefs") or [])
            progs_html += f"""<div class="programme">
  <div class="programme-header">
    <div>
      <div class="programme-name">{e(p.get("name",""))}</div>
      <div class="programme-meta">
        <span>Status: <strong>{e(p.get("status",""))}</strong></span>
        {"<span>Value: <strong>" + e(p.get("value","")) + "</strong></span>" if p.get("value") else ""}
        {"<span>SRO: " + e(p.get("sro","")) + "</span>" if p.get("sro") else ""}
        {"<span>Timeline: " + e(p.get("timeline","")) + "</span>" if p.get("timeline") else ""}
      </div>
    </div>
    {"<span style='font-size:0.75em;color:#94A3B8'>" + e(srefs) + "</span>" if srefs else ""}
  </div>
  {targets_html}
  {deps_html}
</div>"""

        reg_html = "".join(ev(r) for r in strat.get("regulatoryPressures", []))
        pol_html = "".join(ev(p) for p in strat.get("politicalPressures", []))
        fisc_html = "".join(ev(p) for p in strat.get("fiscalPressures", []))
        perf_html = "".join(ev(p) for p in strat.get("servicePerformancePressures", []))
        stmt_html = "".join(ev(p) for p in strat.get("publicStatementsOfIntent", []))

        html_out += f"""
<section>
  <h2>Strategic priorities {badge(strat.get('sectionConfidence',''))}</h2>
  <p style="margin-bottom:16px">{_linkify_citations(e(strat.get('summaryNarrative','')))}</p>
  <h3>Published strategy themes</h3>
  {themes_html}
  <h3>Major programmes</h3>
  {progs_html}
  {"<h3>Regulatory pressures</h3>" + reg_html if reg_html else ""}
  <h3>Political pressures</h3>
  {pol_html}
  <h3>Fiscal pressures</h3>
  {fisc_html}
  <h3>Service performance pressures</h3>
  {perf_html}
  {"<h3>Public statements of intent</h3>" + stmt_html if stmt_html else ""}
</section>
"""

    # ── COMMISSIONING CONTEXT HYPOTHESES ───────────────────────────────────────
    if comm:
        spend_class = comm.get("spendClassification")
        spend_html = ev(spend_class, "Spend classification") if spend_class else ""

        html_out += f"""
<section>
  <h2>Commissioning context hypotheses {badge(comm.get('sectionConfidence',''))}</h2>
  <div class="caveat">{e(comm.get('sectionCaveat',''))}</div>
  {spend_html}
  <h3>Drivers of external buying</h3>
  {"".join(ev(d2) for d2 in comm.get('driversOfExternalBuying',[]))}
  <h3>Outcomes sought</h3>
  {"".join(ev(o) for o in comm.get('outcomesSought',[]))}
  <h3>Pressures shaping spend</h3>
  {"".join(ev(p) for p in comm.get('pressuresShapingSpend',[]))}
  <h3>Operational pain points</h3>
  {"".join(ev(p) for p in comm.get('operationalPainPoints',[]))}
  {"<h3>Consequences of inaction</h3>" + "".join(ev(c) for c in comm.get('consequencesOfInaction',[])) if comm.get('consequencesOfInaction') else ""}
  {ev(comm.get('commissioningCycleStage'), 'Commissioning cycle stage')}
  {ev(comm.get('approvalsPending'), 'Approvals pending')}
  {ev(comm.get('marketEngagementLikelihood'), 'Market engagement likelihood')}
  <h3>Buying readiness</h3>
  {ev(comm.get('buyingReadiness'))}
  <h3>Timeline risks</h3>
  {"".join(ev(t) for t in comm.get('timelineRisks',[]))}
</section>
"""

    # ── PROCUREMENT BEHAVIOUR ──────────────────────────────────────────────────
    if proc:
        routes = " &bull; ".join(e(r) for r in proc.get("preferredRoutes", []))
        frameworks = " &bull; ".join(e(f) for f in proc.get("frameworkUsage", []))

        # Data stats row
        total_awards = proc.get("totalAwards")
        total_value = proc.get("totalValue")
        data_window = proc.get("dataWindow")
        stats_row = ""
        if any([total_awards, total_value, data_window]):
            stats_row = '<div class="stats-row">'
            if total_awards is not None:
                stats_row += f'<div class="stat-cell"><div class="stat-value">{e(str(total_awards))}</div><div class="stat-label">Total awards</div></div>'
            if total_value:
                stats_row += f'<div class="stat-cell"><div class="stat-value">{e(total_value)}</div><div class="stat-label">Total value</div></div>'
            if data_window:
                stats_row += f'<div class="stat-cell"><div class="stat-value">{e(data_window)}</div><div class="stat-label">Data window</div></div>'
            stats_row += '</div>'

        shared = proc.get("sharedServiceArrangements")
        shared_html = f'<p style="font-size:0.88em;color:#555;margin-bottom:12px"><strong>Shared service arrangements:</strong> {e(shared)}</p>' if shared else ""

        html_out += f"""
<section>
  <h2>Procurement behaviour {badge(proc.get('sectionConfidence',''))}</h2>
  <p style="margin-bottom:16px">{_linkify_citations(e(proc.get('summaryNarrative','')))}</p>
  {stats_row}
  {shared_html}
  <h3>Preferred routes</h3>
  <p>{routes}</p>
  <h3>Framework usage</h3>
  <p>{frameworks}</p>
  <h3>Typical contract shape</h3>
  <p><strong>Length:</strong> {e(proc.get('typicalContractLength',''))} |
     <strong>Value range:</strong> {e(proc.get('typicalContractValue',''))}</p>
  {ev(proc.get('categoryConcentration'), 'Category concentration')}
  {ev(proc.get('innovationVsProven'), 'Innovation vs proven')}
  {ev(proc.get('priceVsQualityBias'), 'Price vs quality bias')}
  {ev(proc.get('renewalPatterns'), 'Renewal patterns')}
</section>
"""

    # ── PROCUREMENT BEHAVIOUR SNAPSHOT ─────────────────────────────────────────
    if proc_snap:
        om = proc_snap.get("outcomeMix") or {}
        n2a = proc_snap.get("noticeToAwardDays") or {}
        top_cats = proc_snap.get("topCategoriesByOutcome") or []

        def _snap_stat(val, label, alert=False):
            if val is None or val == "unknown":
                return ""
            cls = "stat-cell alert" if alert else "stat-cell"
            return (
                f'<div class="{cls}">'
                f'<div class="stat-value">{e(str(val))}</div>'
                f'<div class="stat-label">{e(label)}</div>'
                f'</div>'
            )

        snap_stats = '<div class="stats-row">'
        snap_stats += _snap_stat(proc_snap.get("averageBidsPerTender"), "Avg bids per tender",
                                  alert=(proc_snap.get("averageBidsPerTender") or 99) <= 1)
        snap_stats += _snap_stat(proc_snap.get("competitionIntensity"), "Competition intensity",
                                  alert=proc_snap.get("competitionIntensity") == "low")
        snap_stats += _snap_stat(proc_snap.get("cancellationRateVsPeers"), "Cancellation vs peers",
                                  alert=proc_snap.get("cancellationRateVsPeers") == "above-peer-average")
        if n2a.get("median"):
            snap_stats += _snap_stat(f'{n2a["median"]} days', "Notice-to-award median")
        snap_stats += _snap_stat(proc_snap.get("volumeTrend"), "Volume trend")
        snap_stats += '</div>'

        outcome_html = ""
        if om:
            parts = []
            for k, label in [("awarded","Awarded"),("cancelled","Cancelled"),("nonCompliant","Non-compliant"),("dormant","Dormant"),("live","Live")]:
                if om.get(k) is not None:
                    parts.append(f"<strong>{label}:</strong> {om[k]}")
            outcome_html = f'<p style="font-size:0.88em;margin-bottom:10px">{" &bull; ".join(parts)}</p>'

        top_cat_html = ""
        if top_cats:
            top_cat_html = '<h3>Top categories</h3>'
            for tc in top_cats:
                top_cat_html += (
                    f'<p style="font-size:0.84em">{e(tc.get("category",""))} — '
                    f'Awarded: <strong>{tc.get("awarded","—")}</strong>, '
                    f'Cancelled: <strong>{tc.get("cancelled","—")}</strong></p>'
                )

        distressed = proc_snap.get("distressedIncumbentFlag")
        distressed_html = ""
        if distressed is not None:
            flag_color = "#D17A74" if distressed else "#2d7d46"
            flag_text = "DISTRESSED INCUMBENT SIGNAL" if distressed else "No distressed incumbent signal"
            distressed_html = (
                f'<p style="font-size:0.82em;color:{flag_color};font-weight:600;margin:10px 0">'
                f'{flag_text}</p>'
            )
            if proc_snap.get("distressedIncumbentEvidence"):
                distressed_html += f'<p style="font-size:0.82em;color:#555">{e(proc_snap["distressedIncumbentEvidence"])}</p>'

        summary_sentence = proc_snap.get("consultantSummarySentence", "")
        snap_date = (proc_snap.get("snapshotTakenAt") or "")[:10]
        snap_source = proc_snap.get("snapshotSourcedFrom", "")

        html_out += f"""
<section>
  <h2>Procurement behaviour snapshot</h2>
  <div class="caveat">
    Analytics pinned {e(snap_date)} from {e(snap_source)}.
    {e(str(proc_snap.get("yearsCovered","")))} years covered.
    Re-run get_buyer_behaviour_profile on next dossier refresh.
  </div>
  {snap_stats}
  <h3>Outcome mix</h3>
  {outcome_html}
  {top_cat_html}
  {distressed_html}
  {"<div class='archetype-box'><strong>Consultant takeaway:</strong><br>" + e(summary_sentence) + "</div>" if summary_sentence else ""}
</section>
"""

    # ── DECISION UNIT ASSUMPTIONS ──────────────────────────────────────────────
    if dec:
        def _render_role_list(roles, title):
            if not roles:
                return ""
            out = f'<h3>{title}</h3>'
            for r in roles:
                out += f'<div class="role-block">{ev(r)}</div>'
            return out

        # Per-role interests grid
        pri = dec.get("perRoleInterests") or {}
        role_cards_html = ""
        if pri:
            role_cards_html = '<h3>What each role cares about</h3><div class="role-interest-grid">'
            for key, display in [
                ("businessOwner", "Business owner"),
                ("commercial", "Commercial"),
                ("technical", "Technical"),
                ("finance", "Finance"),
                ("evaluators", "Evaluators"),
            ]:
                ri = pri.get(key)
                if not ri:
                    continue
                sec = f'<div class="secondary">{e(ri.get("secondaryInterest",""))}</div>' if ri.get("secondaryInterest") else ""
                ev_basis = f'<div class="evidence">{e(ri.get("evidenceBasis",""))}</div>' if ri.get("evidenceBasis") else ""
                role_cards_html += (
                    f'<div class="role-interest-card">'
                    f'<div class="role-name">{display} {badge(ri.get("confidence",""))}</div>'
                    f'<div class="primary">{e(ri.get("primaryInterest",""))}</div>'
                    f'{sec}{ev_basis}'
                    f'</div>'
                )
            role_cards_html += '</div>'

        # Internal tensions
        tensions_html = ""
        tensions = dec.get("internalTensions") or []
        if tensions:
            tensions_html = '<h3>Internal tensions</h3>'
            for t in tensions:
                between = " vs ".join(t.get("between") or [])
                tensions_html += (
                    f'<div class="tension-item">'
                    f'<div class="tension-between">{e(between)}</div>'
                    f'<strong>{e(t.get("tension",""))}</strong>'
                    f'{ev({"value": t.get("evidenceBasis",""), "type": t.get("type",""), "confidence": t.get("confidence",""), "rationale": t.get("rationale",""), "sourceRefs": t.get("sourceRefs",[])} if t.get("evidenceBasis") else None)}'
                    f'</div>'
                )

        # Dominant lens
        lens = dec.get("dominantDecisionLens") or {}
        lens_html = ""
        if lens:
            lens_html = (
                f'<h3>Dominant decision lens</h3>'
                f'<div class="dominant-lens-box">'
                f'<div class="lens-value">{e(lens.get("value","unknown")).replace("-", " ")} {badge(lens.get("confidence",""))}</div>'
                f'<p style="font-size:0.88em;color:#555;margin-top:6px">{e(lens.get("rationale",""))}</p>'
                f'</div>'
            )

        intel_gaps = dec.get("intelligenceGaps") or []
        gaps_html = ""
        if intel_gaps:
            gaps_html = (
                '<h3>Intelligence gaps</h3>'
                '<ul class="gap-list">'
                + "".join(f"<li>{e(g)}</li>" for g in intel_gaps)
                + '</ul>'
            )

        html_out += f"""
<section>
  <h2>Decision unit assumptions {badge(dec.get('sectionConfidence',''))}</h2>
  <div class="caveat">{e(dec.get('sectionCaveat',''))}</div>
  {_render_role_list(dec.get('businessOwnerRoles',[]), 'Business owner roles')}
  {_render_role_list(dec.get('commercialRoles',[]), 'Commercial roles')}
  {_render_role_list(dec.get('technicalStakeholders',[]), 'Technical stakeholders')}
  {_render_role_list(dec.get('financeAssuranceRoles',[]), 'Finance and assurance roles')}
  {_render_role_list(dec.get('evaluatorGroups',[]), 'Evaluator groups')}
  {role_cards_html}
  {tensions_html}
  {lens_html}
  {gaps_html}
</section>
"""

    # ── CULTURE AND PREFERENCES ────────────────────────────────────────────────
    if cult:
        cm = cult.get("changeMaturity", {}) or {}
        cm_html = ""
        cm_labels = [
            ("deliveryMaturity", "Delivery"),
            ("digitalMaturity", "Digital"),
            ("governanceMaturity", "Governance"),
            ("supplierManagementMaturity", "Supplier management"),
            ("coCreationTolerance", "Co-creation tolerance"),
            ("phaseOrAgileCapability", "Phased/agile capability"),
        ]
        for k, label in cm_labels:
            if cm.get(k):
                cm_html += ev(cm[k], label)

        # Language and framing
        lang = cult.get("languageAndFraming") or {}
        lang_html = ""
        if lang:
            preferred = lang.get("preferredTerminology") or []
            policy = lang.get("policyFrames") or []
            avoid = lang.get("avoidLanguage") or []
            lang_html = '<h3>Language and framing</h3>'
            if preferred:
                lang_html += '<p style="font-size:0.82em;color:#94A3B8;margin-bottom:4px">Use these terms:</p>'
                lang_html += '<div class="lang-tags">' + "".join(f'<span class="lang-tag">{e(t)}</span>' for t in preferred) + '</div>'
            if policy:
                lang_html += '<p style="font-size:0.82em;color:#94A3B8;margin:8px 0 4px">Policy frames:</p>'
                lang_html += '<div class="lang-tags">' + "".join(f'<span class="lang-tag policy">{e(t)}</span>' for t in policy) + '</div>'
            if avoid:
                lang_html += '<p style="font-size:0.82em;color:#D17A74;margin:8px 0 4px">Avoid:</p>'
                lang_html += '<div class="lang-tags">' + "".join(f'<span class="lang-tag avoid">{e(t)}</span>' for t in avoid) + '</div>'
            if lang.get("evidenceBasis"):
                lang_html += f'<p style="font-size:0.78em;color:#94A3B8;margin-top:8px"><em>Basis: {e(lang["evidenceBasis"])}</em></p>'

        html_out += f"""
<section>
  <h2>Culture and preferences {badge(cult.get('sectionConfidence',''))}</h2>
  {ev(cult.get('decisionMakingFormality'), 'Decision-making formality')}
  {ev(cult.get('governanceIntensity'), 'Governance intensity')}
  {ev(cult.get('riskTolerance'), 'Risk tolerance')}
  {ev(cult.get('evidencePreferences'), 'Evidence preferences')}
  {ev(cult.get('supplierInteractionStyle'), 'Supplier interaction style')}
  {ev(cult.get('presentationStyle'), 'Presentation style')}
  {ev(cult.get('socialValueAndESG'), 'Social value and ESG')}
  <h3>Change maturity</h3>
  {cm_html}
  {lang_html}
</section>
"""

    # ── COMMERCIAL AND RISK POSTURE ────────────────────────────────────────────
    if risk_p:
        html_out += f"""
<section>
  <h2>Commercial and risk posture {badge(risk_p.get('sectionConfidence',''))}</h2>
  {ev(risk_p.get('affordabilitySensitivity'), 'Affordability sensitivity')}
  {ev(risk_p.get('riskTransferPosture'), 'Risk transfer posture')}
  {ev(risk_p.get('contractualCaution'), 'Contractual caution')}
  {ev(risk_p.get('preferredCommercialModels'), 'Preferred commercial models')}
  {ev(risk_p.get('paymentTermsNorms'), 'Payment terms norms')}
  {ev(risk_p.get('cyberDataSensitivity'), 'Cyber and data sensitivity')}
  {ev(risk_p.get('mobilisationSensitivity'), 'Mobilisation sensitivity')}
  {ev(risk_p.get('auditFoiExposure'), 'Audit and FOI exposure')}
  {ev(risk_p.get('securityClearanceRequirements'), 'Security clearance requirements')}
</section>
"""

    # ── SUPPLIER ECOSYSTEM ─────────────────────────────────────────────────────
    if supp and supp.get("incumbents"):
        suppliers_html = ""
        for s in supp["incumbents"]:
            imp = s.get("strategicImportance", "")
            act = s.get("recentActivity", "")
            imp_colors = {
                "critical": ("#D17A74", "#fff"),
                "major": ("#b8860b", "#fff"),
                "moderate": ("#5CA3B6", "#fff"),
                "minor": ("#94A3B8", "#fff"),
            }
            act_colors = {
                "growing": ("#2d7d46", "#fff"),
                "stable": ("#5CA3B6", "#fff"),
                "thinning": ("#D17A74", "#fff"),
            }
            ic, it = imp_colors.get(imp, ("#94A3B8", "#fff"))
            ac, at = act_colors.get(act, ("#94A3B8", "#fff"))

            slines = ", ".join(e(sl) for sl in s.get("serviceLines", []))
            ei = s.get("entrenchmentIndicators", {}) or {}
            indicators = [
                f"<strong>{ek}:</strong> {e(ev2)}"
                for ek, ev2 in ei.items()
                if ev2
            ]
            ind_html = (
                '<p style="font-size:0.82em;color:#94A3B8;margin-top:6px">'
                + " | ".join(indicators)
                + "</p>"
                if indicators
                else ""
            )

            # Vulnerability signals
            vs = s.get("vulnerabilitySignals") or {}
            vuln_html = ""
            if vs and vs.get("overallVulnerability"):
                vuln_lines = []
                for vk, vl in [
                    ("cancelledContracts", "Cancelled contracts"),
                    ("auditFindings", "Audit findings"),
                    ("performanceIssues", "Performance issues"),
                    ("publicComplaints", "Public complaints"),
                    ("earlyTerminations", "Early terminations"),
                    ("leadershipDeparturesAtSupplier", "Leadership departures"),
                ]:
                    items = vs.get(vk) or []
                    for item in items:
                        vuln_lines.append(f"<strong>{vl}:</strong> {e(item)}")
                ov = vs.get("overallVulnerability", "")
                ov_color = {"high":"#D17A74","medium":"#b8860b","low":"#2d7d46","none":"#94A3B8"}.get(ov, "#94A3B8")
                vuln_html = (
                    f'<div class="vulnerability-section">'
                    f'<div class="vuln-label">Vulnerability: '
                    f'<strong style="color:{ov_color}">{e(ov.upper())}</strong></div>'
                    + "".join(f'<div class="vuln-item">{v}</div>' for v in vuln_lines)
                    + (f'<p style="font-size:0.78em;color:#94A3B8;margin-top:6px">{e(vs.get("rationale",""))}</p>' if vs.get("rationale") else "")
                    + "</div>"
                )

            suppliers_html += f"""<div class="supplier">
  <h4>{e(s.get('supplierName',''))}</h4>
  <div class="supplier-meta">
    <span style="background:{ic};color:{it}">{e(imp)}</span>
    <span style="background:{ac};color:{at}">{e(act)}</span>
    <span style="background:#E0F4F6;color:#021744">Since: {e(s.get('longestRelationship',''))}</span>
    <span style="background:#E0F4F6;color:#021744">Value: {e(s.get('totalValue',''))}</span>
    {"<span style='background:#E0F4F6;color:#021744'>Contracts: " + str(s.get('contractCount','')) + "</span>" if s.get('contractCount') else ""}
  </div>
  <p style="font-size:0.88em"><strong>Service lines:</strong> {slines}</p>
  {ind_html}
  {vuln_html}
</div>"""

        adj = " &bull; ".join(e(a) for a in supp.get("adjacentSuppliers", []))
        refresh_html = "".join(
            f'<div class="refresh-item">{e(a)}</div>'
            for a in supp.get("marketRefreshAreas", [])
        )
        barriers = supp.get("barriersToEntry")

        html_out += f"""
<section>
  <h2>Supplier ecosystem {badge(supp.get('sectionConfidence',''))}</h2>
  <p style="margin-bottom:16px">{_linkify_citations(e(supp.get('summaryNarrative','')))}</p>
  {ev(barriers, 'Barriers to entry')}
  <h3>Incumbent suppliers</h3>
  {suppliers_html}
  <h3>Adjacent suppliers</h3>
  <p style="font-size:0.88em">{adj}</p>
  {ev(supp.get('supplierConcentration'), 'Supplier concentration')}
  {ev(supp.get('switchingEvidence'), 'Switching evidence')}
  <h3>Market refresh areas</h3>
  {refresh_html}
</section>
"""

    # ── RELATIONSHIP HISTORY ───────────────────────────────────────────────────
    if rel:
        prior = rel.get("priorContracts") or []
        prior_html = ""
        if prior:
            prior_html = (
                '<h3>Prior contracts</h3>'
                '<table class="contract-table">'
                '<tr><th>Contract</th><th>Value</th><th>Period</th><th>Status</th></tr>'
            )
            for c in prior:
                prior_html += (
                    f"<tr><td>{e(c.get('contractName',''))}</td>"
                    f"<td>{e(c.get('value',''))}</td>"
                    f"<td>{e(c.get('period',''))}</td>"
                    f"<td>{e(c.get('status',''))}</td></tr>"
                )
            prior_html += '</table>'

        active = rel.get("activeProgrammes") or []
        active_html = ""
        if active:
            active_html = '<h3>Active programmes</h3><div class="pill-list">' + "".join(f'<span class="pill">{e(p)}</span>' for p in active) + '</div>'

        past_bids = rel.get("pastBids") or []
        bids_html = ""
        if past_bids:
            bids_html = (
                '<h3>Past bids</h3>'
                '<table class="contract-table">'
                '<tr><th>Opportunity</th><th>Date</th><th>Outcome</th><th>Feedback</th></tr>'
            )
            for b in past_bids:
                outcome_color = {"win":"#2d7d46","loss":"#D17A74","no-bid":"#94A3B8"}.get(b.get("outcome",""), "#1a1a2e")
                bids_html += (
                    f"<tr><td>{e(b.get('opportunityName',''))}</td>"
                    f"<td>{e(b.get('date',''))}</td>"
                    f"<td style='color:{outcome_color};font-weight:600'>{e(b.get('outcome',''))}</td>"
                    f"<td>{e(b.get('feedbackReceived','') or '—')}</td></tr>"
                )
            bids_html += '</table>'

        exec_rels = rel.get("executiveRelationships") or []
        advocates = rel.get("knownAdvocates") or []
        blockers = rel.get("knownBlockers") or []

        exec_html = ""
        if exec_rels:
            exec_html = '<h3>Executive relationships</h3>' + "".join(f"<p style='font-size:0.88em'>{e(r)}</p>" for r in exec_rels)
        if advocates:
            exec_html += '<h3>Known advocates</h3><div class="pill-list">' + "".join(f'<span class="pill" style="background:#E8F5E9;color:#2d7d46">{e(a)}</span>' for a in advocates) + '</div>'
        if blockers:
            exec_html += '<h3>Known blockers</h3><div class="pill-list">' + "".join(f'<span class="pill" style="background:rgba(209,122,116,0.1);color:#D17A74">{e(b)}</span>' for b in blockers) + '</div>'

        html_out += f"""
<section>
  <h2>Relationship history {badge(rel.get('sectionConfidence',''))}</h2>
  <div class="caveat">{e(rel.get('tierNote',''))}</div>
  {prior_html}
  {active_html}
  {bids_html}
  {exec_html}
  <h3>Intelligence gaps</h3>
  <ul class="gap-list">
    {"".join(f'<li>{e(g)}</li>' for g in rel.get('intelGaps',[]))}
  </ul>
</section>
"""

    # ── RISKS AND SENSITIVITIES ────────────────────────────────────────────────
    if risks:
        pos_sens = risks.get("positioningSensitivities") or []
        html_out += f"""
<section>
  <h2>Risks and sensitivities {badge(risks.get('sectionConfidence',''))}</h2>
  <p style="margin-bottom:16px;font-weight:500">{_linkify_citations(e(risks.get('summaryNarrative','')))}</p>
  <h3>Procurement controversies</h3>
  {"".join(ev(c) for c in risks.get('procurementControversies',[]))}
  <h3>Programme failures</h3>
  {"".join(ev(f) for f in risks.get('programmeFailures',[]))}
  <h3>Audit findings</h3>
  {"".join(ev(a) for a in risks.get('auditFindings',[]))}
  <h3>Media scrutiny</h3>
  {"".join(ev(m) for m in risks.get('mediaScrutiny',[]))}
  <h3>Public sensitivities</h3>
  {"".join(ev(p) for p in risks.get('publicSensitivities',[]))}
  {"<h3>Positioning sensitivities</h3>" + "".join(ev(p) for p in pos_sens) if pos_sens else ""}
</section>
"""

    # ── PURSUIT IMPLICATIONS ───────────────────────────────────────────────────
    if pursuit_impl and pursuit_impl.get("implications"):
        impls_html = ""
        for impl in pursuit_impl["implications"]:
            fq = impl.get("linkedFrameworkQuestions") or []
            lenses = impl.get("derivedFromLenses") or []
            fq_html = " &bull; ".join(e(q) for q in fq) if fq else ""
            lens_html = " &bull; ".join(e(l) for l in lenses) if lenses else ""
            srefs = ", ".join(impl.get("sourceRefs") or [])
            impls_html += f"""<div class="implication-card">
  <div class="implication-header">
    {category_badge(impl.get('category',''))}
    {badge(impl.get('confidence',''))}
  </div>
  <div class="implication-text">{e(impl.get('implication',''))}</div>
  <div class="implication-rationale">{e(impl.get('rationale',''))}</div>
  <div class="implication-meta">
    {"<span>Framework: " + fq_html + "</span>" if fq_html else ""}
    {"<span>Lenses: " + lens_html + "</span>" if lens_html else ""}
    {"<span>Sources: " + e(srefs) + "</span>" if srefs else ""}
  </div>
</div>"""

        html_out += f"""
<section>
  <h2>Pursuit implications {badge(pursuit_impl.get('sectionConfidence',''))}</h2>
  <div class="caveat">{e(pursuit_impl.get('sectionCaveat',''))}</div>
  <p style="margin-bottom:16px;font-weight:500">{e(pursuit_impl.get('summaryNarrative',''))}</p>
  {impls_html}
</section>
"""

    # ── ACTION REGISTER ────────────────────────────────────────────────────────
    if act_reg and act_reg.get("actions"):
        crit_c = act_reg.get("openCriticalCount", 0)
        high_c = act_reg.get("openHighCount", 0)
        med_c = act_reg.get("openMediumCount", 0)
        low_c = act_reg.get("openLowCount", 0)

        count_row = (
            '<div class="action-count-row">'
            + (f'<div class="action-count" style="background:#C0392B">{crit_c} Critical</div>' if crit_c else '')
            + (f'<div class="action-count" style="background:#b8860b">{high_c} High</div>' if high_c else '')
            + (f'<div class="action-count" style="background:#5CA3B6">{med_c} Medium</div>' if med_c else '')
            + (f'<div class="action-count" style="background:#94A3B8">{low_c} Low</div>' if low_c else '')
            + '</div>'
        )

        actions_html = ""
        for a in act_reg["actions"]:
            if a.get("status") == "closed":
                continue
            gap = a.get("gap") or {}
            nxt = a.get("recommendedNextStep") or {}
            owner = a.get("owner") or {}
            blocks = a.get("blocksDownstreamDecision") or []
            fqs = gap.get("frameworkQuestionsBlocked") or []
            priority = a.get("priority", "medium")

            blocks_html = ""
            if blocks:
                blocks_html = (
                    '<div class="action-blocks"><strong>Blocks:</strong> '
                    + " &bull; ".join(e(b.replace("-", " ")) for b in blocks)
                    + '</div>'
                )

            nxt_html = ""
            if nxt.get("specificTarget"):
                nxt_html = (
                    f'<div class="action-next-step">'
                    f'<strong>Next step ({e(nxt.get("method",""))}):</strong> '
                    f'{e(nxt.get("specificTarget",""))}'
                    + (f'<br><em style="color:#94A3B8">Where: {e(nxt.get("expectedSourceLocation",""))}</em>' if nxt.get("expectedSourceLocation") else "")
                    + f'</div>'
                )

            actions_html += f"""<div class="action-card priority-{priority}">
  <div class="action-header">
    <div>
      <span class="action-id">{e(a.get('actionId',''))}</span>
      <span style="font-size:0.78em;color:#94A3B8;margin-left:8px">{e(a.get('type',''))}</span>
    </div>
    <div>{priority_badge(priority)}</div>
  </div>
  <div class="action-gap">{e(gap.get('description',''))}</div>
  <div style="font-size:0.78em;color:#94A3B8;margin-bottom:8px">
    Section: {e(gap.get('section',''))}
    {" &bull; Blocks: " + " | ".join(e(q) for q in fqs) if fqs else ""}
  </div>
  {nxt_html}
  <div class="action-meta">
    <span>Owner: {e(owner.get('namedPerson') or owner.get('role','unassigned'))}</span>
    <span>Effort: {e(nxt.get('estimatedEffort',''))}</span>
    <span>Confidence uplift: {e(nxt.get('estimatedConfidenceUplift',''))}</span>
  </div>
  <p style="font-size:0.78em;color:#94A3B8;margin-top:6px"><em>{e(a.get('priorityRationale',''))}</em></p>
  {blocks_html}
</div>"""

        html_out += f"""
<section>
  <h2>Action register</h2>
  <p style="font-size:0.88em;color:#555;margin-bottom:14px">{e(act_reg.get('summary',''))}</p>
  {count_row}
  {actions_html}
</section>
"""

    # ── SOURCE REGISTER ────────────────────────────────────────────────────────
    if sreg and sreg.get("sources"):
        rows = ""
        for s in sreg["sources"]:
            url = s.get("url")
            name = (
                f'<a href="{e(url)}" target="_blank">{e(s["sourceName"])}</a>'
                if url
                else e(s.get("sourceName", ""))
            )
            sects = ", ".join(s.get("sectionsSupported", []))
            tmpl = e(s.get("extractionTemplateApplied") or "")
            rows += (
                f"<tr><td>{e(s['sourceId'])}</td><td>{name}</td>"
                f"<td>{e(s.get('sourceType',''))}</td>"
                f"<td>{e(s.get('reliability',''))}</td>"
                f"<td>{e(s.get('publicationDate','—'))}</td>"
                f"<td>{sects}</td>"
                f"<td>{tmpl}</td></tr>"
            )

        gaps_html = "".join(f"<li>{e(g)}</li>" for g in sreg.get("gaps", []))
        stale_html = "".join(f"<li>{e(g)}</li>" for g in sreg.get("staleFields", []))
        low_conf = "".join(
            f"<li>{e(g)}</li>"
            for g in sreg.get("lowConfidenceInferences", [])
        )

        # Extraction templates applied
        etemplates = meta.get("extractionTemplatesApplied") or []
        et_html = ""
        if etemplates:
            et_html = '<h3>Extraction templates applied</h3><div class="pill-list">'
            for et in etemplates:
                et_html += (
                    f'<span class="pill" title="Source: {e(et.get("sourceId",""))} | '
                    f'Lenses: {e(", ".join(et.get("lensesContributed",[])))}">'
                    f'{e(et.get("documentType",""))}</span>'
                )
            et_html += '</div>'

        # Source inventory trace if present
        sit = meta.get("sourceInventoryTrace") or {}
        sit_html = ""
        if sit:
            sit_html = '<h3>Source inventory trace</h3>'
            for tier_key, tier_label in [
                ("tier1Checks", "Tier 1 (Primary HMG)"),
                ("tier2Checks", "Tier 2 (Parliamentary / assurance)"),
                ("tier3Checks", "Tier 3 (Industry / media)"),
                ("tier4Checks", "Tier 4 (Procurement data)"),
            ]:
                if sit.get(tier_key):
                    sit_html += (
                        f'<h4>{tier_label}</h4>'
                        f'<p style="font-size:0.82em;color:#555;line-height:1.6">{e(sit[tier_key])}</p>'
                    )
            if sit.get("documentsAttempted") is not None:
                sit_html += (
                    f'<p style="font-size:0.8em;color:#94A3B8;margin-top:8px">'
                    f'Documents attempted: {sit.get("documentsAttempted")} &bull; '
                    f'Retrieved: {sit.get("documentsRetrieved")} &bull; '
                    f'Named gaps: {sit.get("namedGapsRecorded")}</p>'
                )

        html_out += f"""
<section>
  <h2>Source register</h2>
  {et_html}
  {sit_html}
  <h3>Sources ({len(sreg.get("sources",[]))})</h3>
  <table class="source-table">
    <tr><th>ID</th><th>Source</th><th>Type</th><th>Tier</th><th>Date</th><th>Sections</th><th>Template</th></tr>
    {rows}
  </table>
  {"<h3>Intelligence gaps</h3><ul class='gap-list'>" + gaps_html + "</ul>" if gaps_html else ""}
  {"<h3>Stale fields</h3><ul class='gap-list'>" + stale_html + "</ul>" if stale_html else ""}
  {"<h3>Low confidence inferences</h3><ul class='gap-list'>" + low_conf + "</ul>" if low_conf else ""}
</section>
"""

    html_out += _render_claims_block(data.get("claims", []))

    # ── FOOTER ─────────────────────────────────────────────────────────────────
    html_out += f"""
<div class="footer">
  {grid_mark}
  <p style="margin-top:8px">
    <strong>BID EQUITY</strong> &mdash; PURSUIT INTELLIGENCE<br>
    Generated {e(meta['generatedAt'][:10])} &bull;
    Refresh due {e(meta.get('refreshDue',''))} &bull;
    v{e(meta['version'])}
  </p>
</div>

</div>
</body>
</html>"""

    return html_out


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) != 3:
        print("Usage: python3 render_dossier.py <input.json> <output.html>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    html_content = render(data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"BidEquity dossier rendered: {output_path}")
