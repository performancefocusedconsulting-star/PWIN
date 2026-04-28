#!/usr/bin/env python3
"""
BidEquity Buyer Intelligence Dossier Renderer v2.3

Reads a v2.2 JSON dossier and produces a BidEquity-branded standalone HTML report.

Brand system:
  - Midnight Navy #021744 (primary background)
  - Soft Sand #F7F4EE (page canvas, body text on dark)
  - Bright Aqua #7ADDE2 (headlines, key numbers, accents)
  - Calm Teal #5CA3B6 (secondary accent, evidence borders)
  - Pale Aqua #E0F4F6 (light backgrounds, tags)
  - Light Terracotta #D17A74 (risk indicators, warnings)
  - Descriptor Cyan #60F5F7 (subtitle descriptor text)

Typography: Spline Sans (headings), Inter (body)

Usage:
  python3 render_dossier.py <input.json> <output.html>
"""

import json
import html
import sys
import os
from datetime import datetime


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


def ev(field, label=None):
    """Render an evidenced field or plain string."""
    if field is None:
        return ""
    if isinstance(field, str):
        return f"<p>{e(field)}</p>"
    if isinstance(field, dict) and "value" in field:
        v = field
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
        out += f'<p style="margin:4px 0;line-height:1.6">{e(v["value"])}</p>'
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


def render(data):
    """Render complete HTML from dossier JSON."""
    meta = data["meta"]
    snap = data["buyerSnapshot"]
    org = data.get("organisationContext") or {}
    strat = data.get("strategicPriorities") or {}
    comm = data.get("commissioningContextHypotheses") or {}
    proc = data.get("procurementBehaviour") or {}
    dec = data.get("decisionUnitAssumptions") or {}
    cult = data.get("cultureAndPreferences") or {}
    risk_p = data.get("commercialAndRiskPosture") or {}
    supp = data.get("supplierEcosystem") or {}
    rel = data.get("relationshipHistory") or {}
    risks = data.get("risksAndSensitivities") or {}
    sreg = data.get("sourceRegister") or {}

    # Build the grid mark SVG (3x3 coloured grid)
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

/* Header / Masthead */
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
.lockup-text {{
  display: flex;
  flex-direction: column;
  gap: 2px;
}}
.lockup-brand {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #F7F4EE;
}}
.lockup-descriptor {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #60F5F7;
}}
.header h1 {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 2em;
  font-weight: 700;
  margin-bottom: 6px;
  color: #7ADDE2;
  letter-spacing: -0.01em;
}}
.header .subtitle {{
  color: #F7F4EE;
  font-size: 0.95em;
  opacity: 0.85;
}}
.meta-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 10px;
  margin-top: 20px;
}}
.meta-item {{
  background: rgba(255,255,255,0.06);
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.82em;
  color: #E0F4F6;
}}
.meta-label {{
  font-weight: 600;
  color: #7ADDE2;
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}

/* Sections */
section {{
  background: #fff;
  border-radius: 6px;
  padding: 28px 32px;
  margin-bottom: 18px;
  border: 1px solid rgba(2,23,68,0.06);
}}
section h2 {{
  font-family: 'Spline Sans', sans-serif;
  color: #021744;
  font-size: 1.2em;
  font-weight: 600;
  border-bottom: 2px solid #7ADDE2;
  padding-bottom: 8px;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
}}
section h3 {{
  font-family: 'Spline Sans', sans-serif;
  color: #021744;
  font-size: 1em;
  font-weight: 600;
  margin: 20px 0 10px;
}}

/* Risk items */
.risk-item {{
  background: rgba(209,122,116,0.08);
  border-left: 3px solid #D17A74;
  padding: 10px 14px;
  margin-bottom: 8px;
  border-radius: 0 4px 4px 0;
  font-size: 0.88em;
  line-height: 1.5;
}}

/* Programmes */
.programme {{
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 8px;
  padding: 10px 0;
  border-bottom: 1px solid #f0ede6;
  font-size: 0.88em;
  align-items: start;
}}
.programme:last-child {{ border: none; }}
.programme strong {{ color: #021744; }}

/* Suppliers */
.supplier {{
  border: 1px solid #E0F4F6;
  border-radius: 6px;
  padding: 16px 18px;
  margin-bottom: 12px;
  background: rgba(224,244,246,0.15);
}}
.supplier h4 {{
  font-family: 'Spline Sans', sans-serif;
  color: #021744;
  font-size: 0.95em;
  font-weight: 600;
  margin-bottom: 8px;
}}
.supplier-meta {{
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 0.78em;
  margin-bottom: 8px;
}}
.supplier-meta span {{
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 500;
}}

/* Source table */
.source-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78em;
}}
.source-table th {{
  text-align: left;
  background: #021744;
  color: #F7F4EE;
  padding: 8px 10px;
  font-family: 'Spline Sans', sans-serif;
  font-weight: 500;
  letter-spacing: 0.03em;
}}
.source-table td {{
  padding: 6px 10px;
  border-bottom: 1px solid #f0ede6;
  vertical-align: top;
}}
.source-table tr:hover {{ background: #F7F4EE; }}
.source-table a {{ color: #5CA3B6; text-decoration: none; }}
.source-table a:hover {{ text-decoration: underline; }}

/* Gap list */
.gap-list {{ list-style: none; }}
.gap-list li {{
  padding: 6px 0;
  border-bottom: 1px solid #f0ede6;
  font-size: 0.88em;
  color: #444;
}}
.gap-list li:before {{ content: "\\25B6  "; color: #D17A74; font-size: 0.7em; }}

/* Archetype box */
.archetype-box {{
  background: #E0F4F6;
  border: 1px solid #5CA3B6;
  border-radius: 6px;
  padding: 16px 18px;
  margin: 14px 0;
}}

/* Headline */
.headline {{
  font-family: 'Spline Sans', sans-serif;
  font-size: 1.05em;
  font-weight: 600;
  color: #021744;
  margin-bottom: 14px;
  line-height: 1.45;
}}

/* Caveat */
.caveat {{
  background: rgba(209,122,116,0.06);
  border-left: 3px solid #D17A74;
  padding: 10px 14px;
  font-size: 0.82em;
  color: #94A3B8;
  margin-bottom: 16px;
  border-radius: 0 4px 4px 0;
  font-style: italic;
}}

/* Market refresh */
.refresh-item {{
  background: #E0F4F6;
  padding: 8px 14px;
  margin: 4px 0;
  border-radius: 4px;
  font-size: 0.88em;
  color: #021744;
}}

/* Footer */
.footer {{
  text-align: center;
  padding: 24px;
  font-size: 0.75em;
  color: #94A3B8;
  letter-spacing: 0.02em;
}}
.footer strong {{ color: #5CA3B6; }}

@media print {{
  body {{ background: #fff; }}
  .container {{ max-width: 100%; }}
  section {{ break-inside: avoid; }}
}}
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
</div>
"""

    # EXECUTIVE SUMMARY
    exec_sum = snap.get("executiveSummary", {})
    html_out += f"""
<section>
  <h2>Executive summary</h2>
  <div class="headline">{e(exec_sum.get('headline',''))}</div>
  {"".join(f'<p style="margin-bottom:12px">{e(p)}</p>' for p in exec_sum.get('narrative','').split(chr(10)+chr(10)) if p.strip())}

  <h3>Organisational archetype</h3>
  <div class="archetype-box">
    {ev(snap.get('organisationalArchetype'))}
  </div>

  <h3>Key risks for any pursuit</h3>
  {"".join(f'<div class="risk-item">{e(r)}</div>' for r in snap.get('keyRisks',[]))}
</section>
"""

    # ORGANISATION CONTEXT
    if org:
        leaders = org.get("seniorLeadership", [])
        leader_html = "".join(
            f'<p><strong>{e(l.get("name",""))}</strong> — {e(l.get("role",""))} '
            f'(since {e(l.get("since","unknown"))})</p>'
            for l in leaders
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

    # STRATEGIC PRIORITIES
    if strat:
        themes_html = "".join(ev(t) for t in strat.get("publishedStrategyThemes", []))
        progs = strat.get("majorProgrammes", [])
        progs_html = "".join(
            f'<div class="programme"><strong>{e(p.get("name",""))}</strong>'
            f'<span>{e(p.get("status",""))}</span>'
            f'<span>{e(p.get("value","—"))}</span></div>'
            for p in progs
        )
        pol_html = "".join(ev(p) for p in strat.get("politicalPressures", []))
        fisc_html = "".join(ev(p) for p in strat.get("fiscalPressures", []))
        perf_html = "".join(ev(p) for p in strat.get("servicePerformancePressures", []))

        html_out += f"""
<section>
  <h2>Strategic priorities {badge(strat.get('sectionConfidence',''))}</h2>
  <p style="margin-bottom:16px">{e(strat.get('summaryNarrative',''))}</p>
  <h3>Published strategy themes</h3>
  {themes_html}
  <h3>Major programmes</h3>
  {progs_html}
  <h3>Political pressures</h3>
  {pol_html}
  <h3>Fiscal pressures</h3>
  {fisc_html}
  <h3>Service performance pressures</h3>
  {perf_html}
</section>
"""

    # COMMISSIONING CONTEXT
    if comm:
        html_out += f"""
<section>
  <h2>Commissioning context hypotheses {badge(comm.get('sectionConfidence',''))}</h2>
  <div class="caveat">{e(comm.get('sectionCaveat',''))}</div>
  <h3>Drivers of external buying</h3>
  {"".join(ev(d2) for d2 in comm.get('driversOfExternalBuying',[]))}
  <h3>Pressures shaping spend</h3>
  {"".join(ev(p) for p in comm.get('pressuresShapingSpend',[]))}
  <h3>Operational pain points</h3>
  {"".join(ev(p) for p in comm.get('operationalPainPoints',[]))}
  <h3>Buying readiness</h3>
  {ev(comm.get('buyingReadiness'))}
  <h3>Timeline risks</h3>
  {"".join(ev(t) for t in comm.get('timelineRisks',[]))}
</section>
"""

    # PROCUREMENT BEHAVIOUR
    if proc:
        routes = " &bull; ".join(e(r) for r in proc.get("preferredRoutes", []))
        frameworks = " &bull; ".join(e(f) for f in proc.get("frameworkUsage", []))

        html_out += f"""
<section>
  <h2>Procurement behaviour {badge(proc.get('sectionConfidence',''))}</h2>
  <p style="margin-bottom:16px">{e(proc.get('summaryNarrative',''))}</p>
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

    # CULTURE AND PREFERENCES
    if cult:
        cm = cult.get("changeMaturity", {})
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

        html_out += f"""
<section>
  <h2>Culture and preferences {badge(cult.get('sectionConfidence',''))}</h2>
  {ev(cult.get('decisionMakingFormality'), 'Decision-making formality')}
  {ev(cult.get('governanceIntensity'), 'Governance intensity')}
  {ev(cult.get('riskTolerance'), 'Risk tolerance')}
  {ev(cult.get('socialValueAndESG'), 'Social value and ESG')}
  <h3>Change maturity</h3>
  {cm_html}
</section>
"""

    # COMMERCIAL AND RISK POSTURE
    if risk_p:
        html_out += f"""
<section>
  <h2>Commercial and risk posture {badge(risk_p.get('sectionConfidence',''))}</h2>
  {ev(risk_p.get('affordabilitySensitivity'), 'Affordability sensitivity')}
  {ev(risk_p.get('riskTransferPosture'), 'Risk transfer posture')}
  {ev(risk_p.get('cyberDataSensitivity'), 'Cyber and data sensitivity')}
  {ev(risk_p.get('mobilisationSensitivity'), 'Mobilisation sensitivity')}
  {ev(risk_p.get('auditFoiExposure'), 'Audit and FOI exposure')}
  {ev(risk_p.get('securityClearanceRequirements'), 'Security clearance requirements')}
</section>
"""

    # SUPPLIER ECOSYSTEM
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

            suppliers_html += f"""<div class="supplier">
  <h4>{e(s.get('supplierName',''))}</h4>
  <div class="supplier-meta">
    <span style="background:{ic};color:{it}">{e(imp)}</span>
    <span style="background:{ac};color:{at}">{e(act)}</span>
    <span style="background:#E0F4F6;color:#021744">Since: {e(s.get('longestRelationship',''))}</span>
    <span style="background:#E0F4F6;color:#021744">Value: {e(s.get('totalValue',''))}</span>
  </div>
  <p style="font-size:0.88em"><strong>Service lines:</strong> {slines}</p>
  {ind_html}
</div>"""

        adj = " &bull; ".join(e(a) for a in supp.get("adjacentSuppliers", []))
        refresh_html = "".join(
            f'<div class="refresh-item">{e(a)}</div>'
            for a in supp.get("marketRefreshAreas", [])
        )

        html_out += f"""
<section>
  <h2>Supplier ecosystem {badge(supp.get('sectionConfidence',''))}</h2>
  <p style="margin-bottom:16px">{e(supp.get('summaryNarrative',''))}</p>
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

    # RISKS AND SENSITIVITIES
    if risks:
        html_out += f"""
<section>
  <h2>Risks and sensitivities {badge(risks.get('sectionConfidence',''))}</h2>
  <p style="margin-bottom:16px;font-weight:500">{e(risks.get('summaryNarrative',''))}</p>
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
</section>
"""

    # RELATIONSHIP HISTORY
    if rel:
        html_out += f"""
<section>
  <h2>Relationship history {badge(rel.get('sectionConfidence',''))}</h2>
  <div class="caveat">{e(rel.get('tierNote',''))}</div>
  <h3>Intelligence gaps</h3>
  <ul class="gap-list">
    {"".join(f'<li>{e(g)}</li>' for g in rel.get('intelGaps',[]))}
  </ul>
</section>
"""

    # SOURCE REGISTER
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
            rows += (
                f"<tr><td>{e(s['sourceId'])}</td><td>{name}</td>"
                f"<td>{e(s.get('sourceType',''))}</td>"
                f"<td>{e(s.get('reliability',''))}</td>"
                f"<td>{e(s.get('publicationDate','—'))}</td>"
                f"<td>{sects}</td></tr>"
            )

        gaps_html = "".join(
            f"<li>{e(g)}</li>" for g in sreg.get("gaps", [])
        )
        low_conf = "".join(
            f"<li>{e(g)}</li>"
            for g in sreg.get("lowConfidenceInferences", [])
        )

        html_out += f"""
<section>
  <h2>Source register</h2>
  <table class="source-table">
    <tr><th>ID</th><th>Source</th><th>Type</th><th>Tier</th><th>Date</th><th>Sections</th></tr>
    {rows}
  </table>
  <h3>Intelligence gaps</h3>
  <ul class="gap-list">{gaps_html}</ul>
  <h3>Low confidence inferences</h3>
  <ul class="gap-list">{low_conf}</ul>
</section>
"""

    # FOOTER
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
    # Force UTF-8 on stdout so any path containing non-ASCII characters
    # does not crash on Windows cp1252 consoles. Documented gotcha in
    # the project CLAUDE.md.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) != 3:
        print("Usage: python3 render_dossier.py <input.json> <output.html>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Explicit UTF-8 encoding on both ends — Python's default text-mode
    # encoding follows the system locale (cp1252 on Windows), which
    # silently mangles or crashes on UTF-8 dossiers containing curly
    # quotes (U+201D), em-dashes, or other characters whose UTF-8
    # continuation bytes fall in cp1252's undefined range (0x81, 0x8D,
    # 0x8F, 0x90, 0x9D).
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    html_content = render(data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"BidEquity dossier rendered: {output_path}")
