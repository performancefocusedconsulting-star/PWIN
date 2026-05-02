"""
Directional concentration analysis
==================================
One-off script that produces a directional-grade markdown report on UK
government procurement market concentration. Substitutes (canonical_buyer.type
→ sector) and (CPV leading-2-digits → opportunity bucket) for the polished
canonical taxonomies because the polished cube engine ships post-cloud-migration.

Read-only against bid_intel.db. Writes a markdown file under reports/.

Usage:
    python queries/directional_concentration_analysis.py
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

# Map canonical buyer 'type' values to one of the 9 platform sectors.
# Where the type is ambiguous (Defence is a Ministerial department, Justice
# Courts/Tribunals overlap with Central Government), we accept the limitation
# and note it in the report.
TYPE_TO_SECTOR = {
    # Central Government
    "Ministerial department": "Central Government",
    "Executive agency": "Central Government",
    "Executive non-departmental public body": "Central Government",
    "Advisory non-departmental public body": "Central Government",
    "Non-ministerial department": "Central Government",
    "Non-departmental public body": "Central Government",
    "Civil service": "Central Government",
    "Sub organisation": "Central Government",
    "Sub-organisation": "Central Government",
    "Executive office": "Central Government",
    "Independent monitoring body": "Central Government",
    "Ad-hoc advisory group": "Central Government",
    "Public corporation": "Central Government",
    "Tribunal": "Justice & Home Affairs",
    "Court": "Justice & Home Affairs",
    "central_government": "Central Government",
    "Other": "Central Government",  # heterogeneous fallback
    # Local Government
    "District council": "Local Government",
    "Unitary authority": "Local Government",
    "County council": "Local Government",
    "County borough": "Local Government",
    "Council area": "Local Government",
    "Combined authority": "Local Government",
    "London borough": "Local Government",
    "Metropolitan borough": "Local Government",
    "NI district": "Local Government",
    "Local authority company": "Local Government",
    # NHS & Health
    "NHS Foundation Trust": "NHS & Health",
    "NHS Trust": "NHS & Health",
    "Integrated Care Board": "NHS & Health",
    "NHS Commissioning Support Unit": "NHS & Health",
    "NHS Community Trust": "NHS & Health",
    "NHS Mental Health Trust": "NHS & Health",
    "NHS Ambulance Trust": "NHS & Health",
    "NHS Support Agency": "NHS & Health",
    "NHS Health Board": "NHS & Health",
    "Scottish NHS Board": "NHS & Health",
    "Special Health Authority": "NHS & Health",
    "Special health authority": "NHS & Health",
    "NI HSC Trust": "NHS & Health",
    "NHS Integrated Care Board": "NHS & Health",
    # Education
    "University": "Education",
    "Multi-academy trust": "Education",
    # Emergency Services
    "Police force": "Emergency Services",
    "Police & Crime Commissioner": "Emergency Services",
    "Fire and rescue authority": "Emergency Services",
    # Devolved Government
    "Devolved government": "Devolved Government",
    "Devolved agency": "Devolved Government",
    # Central buying agencies — heterogeneous; route to Central Gov for now
    "Central buying agency": "Central Government",
    # Housing
    "Registered provider": "Local Government",  # housing associations broadly serve local communities
}

# CPV major category mapping — leading 2 digits → directional opportunity bucket
# Coarser than the cube's 10-bucket taxonomy; sufficient for directional analysis.
CPV_TO_BUCKET = {
    "30": "IT Hardware & Equipment",
    "31": "IT Hardware & Equipment",
    "32": "IT Hardware & Equipment",
    "33": "Health & Medical Equipment",
    "34": "Transport Vehicles & Equipment",
    "35": "Security & Defence Equipment",
    "37": "Recreational Goods",
    "38": "Laboratory & Scientific",
    "39": "Furniture & General Goods",
    "44": "Construction Materials",
    "45": "Construction Works",
    "48": "Software & SaaS",
    "50": "Repair, Maintenance & Installation",
    "51": "Installation Services",
    "55": "Catering & Hospitality",
    "60": "Transport Services",
    "63": "Transport Support Services",
    "64": "Telecoms",
    "65": "Utilities",
    "66": "Financial & Insurance",
    "70": "Real Estate",
    "71": "Architecture, Engineering & Surveying",
    "72": "IT Services",
    "73": "Research & Development",
    "75": "Public Administration",
    "76": "Mining & Minerals",
    "77": "Agriculture & Forestry",
    "79": "Business & Consulting Services",
    "80": "Education & Training Services",
    "85": "Health & Social Care Services",
    "90": "Environmental, Cleaning & Waste",
    "92": "Recreational, Cultural & Sporting",
    "98": "Other Community & Personal Services",
}


def connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def fmt_value(v):
    if v is None or v == 0:
        return "—"
    if v >= 1e9:
        return f"£{v/1e9:.2f}bn"
    if v >= 1e6:
        return f"£{v/1e6:.0f}m"
    if v >= 1e3:
        return f"£{v/1e3:.0f}k"
    return f"£{v:.0f}"


def fmt_pct(p):
    return f"{p*100:.0f}%" if p is not None else "—"


def hhi(shares):
    """Herfindahl-Hirschman Index on fractional shares; returns effective n suppliers."""
    if not shares:
        return None
    h = sum(s * s for s in shares)
    return round(1.0 / h, 1) if h > 0 else None


def insight_1_total_universe(conn):
    """Headline figures for the analysis universe."""
    cutoff = (datetime.utcnow() - timedelta(days=365 * 5)).date().isoformat()
    rows = conn.execute("""
        SELECT
          COUNT(DISTINCT n.ocid) AS notices,
          COUNT(DISTINCT a.id) AS awards,
          COALESCE(SUM(a.value_amount), 0) AS total_value
        FROM notices n
        LEFT JOIN awards a ON a.ocid = n.ocid
        WHERE n.published_date >= ?
    """, (cutoff,)).fetchone()
    return dict(rows)


def insight_2_sector_concentration(conn):
    """Per-sector top-3 / top-5 / effective-n concentration."""
    cutoff = (datetime.utcnow() - timedelta(days=365 * 5)).date().isoformat()

    # Build the supplier-by-sector aggregate
    rows = conn.execute("""
        SELECT cb.type AS buyer_type,
               COALESCE(stc.canonical_id, sup.id) AS supplier_id,
               COALESCE(cs.canonical_name, sup.name) AS supplier_name,
               COUNT(DISTINCT a.id) AS wins,
               COALESCE(SUM(a.value_amount), 0) AS value
        FROM awards a
        JOIN notices n        ON n.ocid = a.ocid
        JOIN buyers b         ON b.id = n.buyer_id
        JOIN canonical_buyer_aliases al ON al.alias_lower = LOWER(TRIM(b.name))
        JOIN canonical_buyers cb        ON cb.canonical_id = al.canonical_id
        JOIN award_suppliers asu        ON asu.award_id = a.id
        JOIN suppliers sup              ON sup.id = asu.supplier_id
        LEFT JOIN supplier_to_canonical stc ON stc.supplier_id = sup.id
        LEFT JOIN canonical_suppliers cs    ON cs.canonical_id = stc.canonical_id
        WHERE n.published_date >= ?
          AND a.value_amount > 0
        GROUP BY cb.type, COALESCE(stc.canonical_id, sup.id)
    """, (cutoff,)).fetchall()

    # Aggregate to sector level
    sector_buckets = {}
    for r in rows:
        sector = TYPE_TO_SECTOR.get(r["buyer_type"], "Unmapped")
        if sector == "Unmapped":
            continue
        bucket = sector_buckets.setdefault(sector, {})
        bucket.setdefault(r["supplier_id"], {"name": r["supplier_name"], "wins": 0, "value": 0})
        bucket[r["supplier_id"]]["wins"] += r["wins"]
        bucket[r["supplier_id"]]["value"] += r["value"]

    sector_summaries = []
    for sector, suppliers in sector_buckets.items():
        ranked = sorted(suppliers.values(), key=lambda x: x["value"], reverse=True)
        total_value = sum(s["value"] for s in ranked)
        if total_value == 0:
            continue
        shares = [s["value"] / total_value for s in ranked]
        sector_summaries.append({
            "sector": sector,
            "total_contracts": sum(s["wins"] for s in ranked),
            "total_value": total_value,
            "supplier_count": len(ranked),
            "top_3_share": sum(shares[:3]),
            "top_5_share": sum(shares[:5]),
            "effective_n": hhi(shares),
            "top_5_named": [s["name"] for s in ranked[:5]],
        })
    sector_summaries.sort(key=lambda x: x["total_value"], reverse=True)
    return sector_summaries


def insight_3_sector_x_cpv(conn, top_buckets_per_sector=3):
    """Sector × CPV major-category concentration — directional cube."""
    cutoff = (datetime.utcnow() - timedelta(days=365 * 5)).date().isoformat()

    rows = conn.execute("""
        SELECT cb.type AS buyer_type,
               SUBSTR(c.code, 1, 2) AS cpv2,
               COALESCE(stc.canonical_id, sup.id) AS supplier_id,
               COALESCE(cs.canonical_name, sup.name) AS supplier_name,
               COUNT(DISTINCT a.id) AS wins,
               COALESCE(SUM(a.value_amount), 0) AS value
        FROM awards a
        JOIN notices n            ON n.ocid = a.ocid
        JOIN buyers b             ON b.id = n.buyer_id
        JOIN canonical_buyer_aliases al ON al.alias_lower = LOWER(TRIM(b.name))
        JOIN canonical_buyers cb        ON cb.canonical_id = al.canonical_id
        JOIN cpv_codes c                ON c.ocid = n.ocid
        JOIN award_suppliers asu        ON asu.award_id = a.id
        JOIN suppliers sup              ON sup.id = asu.supplier_id
        LEFT JOIN supplier_to_canonical stc ON stc.supplier_id = sup.id
        LEFT JOIN canonical_suppliers cs    ON cs.canonical_id = stc.canonical_id
        WHERE n.published_date >= ?
          AND a.value_amount > 0
          AND c.code IS NOT NULL
          AND LENGTH(c.code) >= 2
        GROUP BY cb.type, SUBSTR(c.code, 1, 2), COALESCE(stc.canonical_id, sup.id)
    """, (cutoff,)).fetchall()

    cells = {}
    for r in rows:
        sector = TYPE_TO_SECTOR.get(r["buyer_type"], None)
        bucket = CPV_TO_BUCKET.get(r["cpv2"], None)
        if not sector or not bucket:
            continue
        key = (sector, bucket)
        cell = cells.setdefault(key, {})
        cell.setdefault(r["supplier_id"], {"name": r["supplier_name"], "wins": 0, "value": 0})
        cell[r["supplier_id"]]["wins"] += r["wins"]
        cell[r["supplier_id"]]["value"] += r["value"]

    cell_summaries = []
    for (sector, bucket), suppliers in cells.items():
        ranked = sorted(suppliers.values(), key=lambda x: x["value"], reverse=True)
        total_value = sum(s["value"] for s in ranked)
        total_contracts = sum(s["wins"] for s in ranked)
        if total_value == 0 or total_contracts < 5:
            continue
        shares = [s["value"] / total_value for s in ranked]
        cell_summaries.append({
            "sector": sector,
            "bucket": bucket,
            "total_contracts": total_contracts,
            "total_value": total_value,
            "supplier_count": len(ranked),
            "top_3_share": sum(shares[:3]),
            "top_5_share": sum(shares[:5]),
            "effective_n": hhi(shares),
            "top_5_named": [s["name"] for s in ranked[:5]],
            "sufficiency": "reliable" if total_contracts >= 15 else "directional",
        })
    cell_summaries.sort(key=lambda x: x["total_value"], reverse=True)
    return cell_summaries


def insight_4_direct_award_reliance(conn):
    """Per-sector share of award value won via direct award (no competition)."""
    cutoff = (datetime.utcnow() - timedelta(days=365 * 5)).date().isoformat()
    rows = conn.execute("""
        SELECT cb.type AS buyer_type,
               n.procurement_method AS method,
               COALESCE(SUM(a.value_amount), 0) AS value
        FROM awards a
        JOIN notices n        ON n.ocid = a.ocid
        JOIN buyers b         ON b.id = n.buyer_id
        JOIN canonical_buyer_aliases al ON al.alias_lower = LOWER(TRIM(b.name))
        JOIN canonical_buyers cb        ON cb.canonical_id = al.canonical_id
        WHERE n.published_date >= ?
          AND a.value_amount > 0
        GROUP BY cb.type, n.procurement_method
    """, (cutoff,)).fetchall()

    sector_method = {}
    for r in rows:
        sector = TYPE_TO_SECTOR.get(r["buyer_type"], None)
        if not sector:
            continue
        d = sector_method.setdefault(sector, {"limited": 0, "open": 0, "selective": 0, "other": 0, "total": 0})
        method = (r["method"] or "other").lower()
        if method not in ("limited", "open", "selective"):
            method = "other"
        d[method] += r["value"]
        d["total"] += r["value"]

    out = []
    for sector, d in sector_method.items():
        if d["total"] == 0:
            continue
        out.append({
            "sector": sector,
            "total_value": d["total"],
            "direct_award_share": d["limited"] / d["total"],
            "open_share": d["open"] / d["total"],
            "selective_share": d["selective"] / d["total"],
        })
    out.sort(key=lambda x: x["direct_award_share"], reverse=True)
    return out


def insight_5_trend(conn):
    """Year-on-year trend on top-3 share per sector — recent year vs prior years."""
    cutoff_5y = (datetime.utcnow() - timedelta(days=365 * 5)).date().isoformat()
    cutoff_1y = (datetime.utcnow() - timedelta(days=365)).date().isoformat()

    def share_top3(date_floor, date_ceiling):
        rows = conn.execute("""
            SELECT cb.type AS buyer_type,
                   COALESCE(stc.canonical_id, sup.id) AS supplier_id,
                   COALESCE(SUM(a.value_amount), 0) AS value
            FROM awards a
            JOIN notices n        ON n.ocid = a.ocid
            JOIN buyers b         ON b.id = n.buyer_id
            JOIN canonical_buyer_aliases al ON al.alias_lower = LOWER(TRIM(b.name))
            JOIN canonical_buyers cb        ON cb.canonical_id = al.canonical_id
            JOIN award_suppliers asu        ON asu.award_id = a.id
            JOIN suppliers sup              ON sup.id = asu.supplier_id
            LEFT JOIN supplier_to_canonical stc ON stc.supplier_id = sup.id
            WHERE n.published_date >= ?
              AND n.published_date < ?
              AND a.value_amount > 0
            GROUP BY cb.type, COALESCE(stc.canonical_id, sup.id)
        """, (date_floor, date_ceiling)).fetchall()
        sector_buckets = {}
        for r in rows:
            sector = TYPE_TO_SECTOR.get(r["buyer_type"], None)
            if not sector:
                continue
            sector_buckets.setdefault(sector, {})
            sector_buckets[sector].setdefault(r["supplier_id"], 0)
            sector_buckets[sector][r["supplier_id"]] += r["value"]
        out = {}
        for sector, supplier_values in sector_buckets.items():
            total = sum(supplier_values.values())
            if total == 0:
                continue
            top3 = sum(sorted(supplier_values.values(), reverse=True)[:3])
            out[sector] = top3 / total
        return out

    recent = share_top3(cutoff_1y, "9999-99-99")
    prior  = share_top3(cutoff_5y, cutoff_1y)
    out = []
    for sector in set(recent.keys()) | set(prior.keys()):
        r = recent.get(sector)
        p = prior.get(sector)
        diff = (r - p) if (r is not None and p is not None) else None
        verdict = None
        if diff is not None:
            if diff >= 0.05:
                verdict = "consolidating"
            elif diff <= -0.05:
                verdict = "fragmenting"
            else:
                verdict = "stable"
        out.append({"sector": sector, "recent_top3": r, "prior_top3": p, "delta": diff, "trend": verdict})
    out.sort(key=lambda x: x["delta"] or 0, reverse=True)
    return out


def insight_6_pipeline_density(conn):
    """Forward pipeline density per sector — planning notices in next 24 months."""
    today = datetime.utcnow().date().isoformat()
    horizon = (datetime.utcnow() + timedelta(days=730)).date().isoformat()
    rows = conn.execute("""
        SELECT cb.type AS buyer_type, COUNT(*) AS pipeline_count, COALESCE(SUM(pn.estimated_value), 0) AS pipeline_value
        FROM planning_notices pn
        JOIN buyers b         ON b.id = pn.buyer_id
        JOIN canonical_buyer_aliases al ON al.alias_lower = LOWER(TRIM(b.name))
        JOIN canonical_buyers cb        ON cb.canonical_id = al.canonical_id
        WHERE pn.future_notice_date BETWEEN ? AND ?
        GROUP BY cb.type
    """, (today, horizon)).fetchall()
    sector_buckets = {}
    for r in rows:
        sector = TYPE_TO_SECTOR.get(r["buyer_type"], None)
        if not sector:
            continue
        sector_buckets.setdefault(sector, {"count": 0, "value": 0})
        sector_buckets[sector]["count"] += r["pipeline_count"]
        sector_buckets[sector]["value"] += r["pipeline_value"]
    out = [{"sector": s, **v} for s, v in sector_buckets.items()]
    out.sort(key=lambda x: x["value"], reverse=True)
    return out


def render_report(universe, sectors, cells, direct_award, trend, pipeline):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    L = []
    L.append("# UK Government Procurement — Directional Concentration Analysis")
    L.append("")
    L.append(f"**Generated:** {today}  ")
    L.append(f"**Status:** Directional only — substitutes coarse type→sector and CPV-2-digit→bucket mappings for the polished canonical taxonomies. The polished cube engine ships post-cloud-migration.  ")
    L.append(f"**Source:** Find a Tender Service + Contracts Finder, trailing 5 years, awards with value > £0  ")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Universe")
    L.append("")
    L.append(f"- **Total notices analysed:** {universe['notices']:,}")
    L.append(f"- **Total awards with value:** {universe['awards']:,}")
    L.append(f"- **Total contract value:** {fmt_value(universe['total_value'])}")
    L.append("")

    # Insight 1 + 2 — sector concentration
    L.append("## Insight 1 — Sector-level concentration")
    L.append("")
    L.append("How concentrated is each sector by total contract value? Lower effective-n means a more concentrated market.")
    L.append("")
    L.append("| Sector | Contracts | Total value | Top-3 share | Top-5 share | Effective n |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for s in sectors:
        L.append(
            f"| {s['sector']} | {s['total_contracts']:,} | {fmt_value(s['total_value'])} | "
            f"{fmt_pct(s['top_3_share'])} | {fmt_pct(s['top_5_share'])} | {s['effective_n'] or '—'} |"
        )
    L.append("")
    L.append("**Top 5 named suppliers by sector (by contract value):**")
    L.append("")
    for s in sectors:
        names = " · ".join(s["top_5_named"])
        L.append(f"- **{s['sector']}** — {names}")
    L.append("")

    # Insight 3 — sector × CPV
    L.append("## Insight 2 — Sector × CPV-bucket concentration (directional cube)")
    L.append("")
    L.append("The 90-cell cube approximated using CPV major-category buckets in place of the polished opportunity-type taxonomy. Filtered to cells with at least 5 awarded contracts. The 25 highest-value cells are shown.")
    L.append("")
    L.append("| # | Sector | CPV bucket | Contracts | Total value | Top-3 share | Effective n | Top 3 suppliers |")
    L.append("|---:|---|---|---:|---:|---:|---:|---|")
    for i, c in enumerate(cells[:25], 1):
        names = " · ".join(c["top_5_named"][:3])
        L.append(
            f"| {i} | {c['sector']} | {c['bucket']} | {c['total_contracts']:,} | "
            f"{fmt_value(c['total_value'])} | {fmt_pct(c['top_3_share'])} | {c['effective_n']} | {names} |"
        )
    L.append("")
    high_conc_count = sum(1 for c in cells if c["top_3_share"] >= 0.70)
    very_high_conc_count = sum(1 for c in cells if c["top_3_share"] >= 0.85)
    L.append(f"**Macro shape:** Of {len(cells)} populated cells (≥5 contracts), **{high_conc_count} have top-3 share ≥ 70%** "
             f"and **{very_high_conc_count} have top-3 share ≥ 85%**.")
    L.append("")

    # Insight 4 — direct-award reliance
    L.append("## Insight 3 — Direct-award reliance per sector")
    L.append("")
    L.append("Share of contract value won via direct award (no competitive process) versus open / selective procurement. High direct-award share signals structurally protected supplier positions.")
    L.append("")
    L.append("| Sector | Total value | Direct award % | Open % | Selective % |")
    L.append("|---|---:|---:|---:|---:|")
    for s in direct_award:
        L.append(
            f"| {s['sector']} | {fmt_value(s['total_value'])} | "
            f"{fmt_pct(s['direct_award_share'])} | {fmt_pct(s['open_share'])} | {fmt_pct(s['selective_share'])} |"
        )
    L.append("")

    # Insight 5 — trend
    L.append("## Insight 4 — Trajectory: consolidating versus fragmenting")
    L.append("")
    L.append("Compares top-3 share in the most recent 12 months to the prior 4 years. Positive delta = market is consolidating around incumbents. Negative delta = market is fragmenting.")
    L.append("")
    L.append("| Sector | Prior top-3 | Recent top-3 | Δ | Verdict |")
    L.append("|---|---:|---:|---:|---|")
    for t in trend:
        L.append(
            f"| {t['sector']} | {fmt_pct(t['prior_top3'])} | {fmt_pct(t['recent_top3'])} | "
            f"{('+' if t['delta'] and t['delta']>=0 else '') + (fmt_pct(t['delta']) if t['delta'] is not None else '—')} | "
            f"{t['trend'] or '—'} |"
        )
    L.append("")

    # Insight 6 — pipeline density
    L.append("## Insight 5 — Forward pipeline density per sector")
    L.append("")
    L.append("Planning notices in the next 24 months (forward pipeline of opportunities not yet competitively advertised).")
    L.append("")
    L.append("| Sector | Pipeline notices | Pipeline value (when stated) |")
    L.append("|---|---:|---:|")
    for p in pipeline:
        L.append(f"| {p['sector']} | {p['count']:,} | {fmt_value(p['value'])} |")
    L.append("")

    L.append("---")
    L.append("")
    L.append("## Caveats")
    L.append("")
    L.append("- **Sector mapping is coarse.** Defence (Ministry of Defence) sits inside Central Government in this analysis because the canonical buyer type is `Ministerial department`. The polished cube will isolate Defence properly; the directional analysis cannot.")
    L.append("- **Justice & Home Affairs** is approximated using only `Court` and `Tribunal` types. Home Office and Ministry of Justice as buyers sit in Central Government here. The polished cube will route by buyer name, not just type.")
    L.append("- **Transport** has no clean type signature. Excluded from the sector analysis. The polished cube will pick this up via name patterns (Transport for London, Network Rail, etc.).")
    L.append("- **CPV buckets are coarser than the cube's opportunity-type taxonomy.** The polished cube will use the 10-bucket taxonomy (BPO, IT Outsourcing, Managed Service, Facilities, Hybrid Transformation, Digital Outcomes, Consulting & Advisory, Infrastructure & Hardware, Software / SaaS, Framework / Panel Appointment) with title-keyword fallback for ambiguous CPVs. The directional CPV-2-digit buckets here are approximate.")
    L.append("- **Awards with NULL value are excluded** from concentration calculations because they cannot be fairly weighted. About 30% of awards in the database have unknown values, which biases concentration metrics toward larger named contracts. This is a known limitation noted in the methodology document.")
    L.append("- **Direct-award figures combine procurement methods.** `limited` is used as the direct-award proxy here, matching the existing methodology classification.")
    L.append("- **Supplier deduplication uses the canonical_supplier layer** (Splink-derived, 82,637 entities) where available, falling back to raw supplier rows otherwise. Concentration figures may be slightly understated where canonical mapping is incomplete.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## How to interpret this for launch positioning")
    L.append("")
    L.append("Each insight section above answers a specific commercial question:")
    L.append("")
    L.append("- **Insight 1 + 2 (concentration)** prove the structural claim that UK government procurement is highly concentrated when sliced narrowly. Use the *macro shape* line as the headline citation; use the named-supplier rosters as the proof that this is not theoretical.")
    L.append("- **Insight 3 (direct-award reliance)** is the politically pointed evidence — sectors where dominant suppliers are not just incumbent but structurally protected from competition.")
    L.append("- **Insight 4 (trajectory)** tells you whether the displacement opportunity is growing or shrinking. Sectors that are consolidating make the challenger story more urgent; sectors that are fragmenting confirm the breaking-in narrative is empirically possible.")
    L.append("- **Insight 5 (forward pipeline)** turns the structural claim into a pipeline. The number of planning notices per sector is the count of *near-term* opportunities the displacement intelligence can be applied to.")
    L.append("")
    L.append("**For positioning material, anchor on:** the macro shape line in Insight 2, the named suppliers in Insight 1, the direct-award percentages in Insight 3 for the politically pointed angle, and the pipeline density in Insight 5 to turn it from abstract concentration into concrete commercial opportunity.")
    L.append("")
    L.append("**The polished cube** (post-cloud-migration build) will harden every claim above by isolating Defence, Justice, and Transport sectors cleanly, replacing CPV buckets with the platform's 10-bucket opportunity taxonomy, and adding the named per-cell credible competitor lists with grip data and the per-cell forward pipeline.")
    return "\n".join(L)


def main():
    conn = connect()
    print("Running directional analysis...")
    print("  [1/6] Universe...")
    universe = insight_1_total_universe(conn)
    print(f"      {universe['notices']:,} notices, {universe['awards']:,} awards, {fmt_value(universe['total_value'])}")
    print("  [2/6] Sector concentration...")
    sectors = insight_2_sector_concentration(conn)
    print(f"      {len(sectors)} sectors")
    print("  [3/6] Sector x CPV cells...")
    cells = insight_3_sector_x_cpv(conn)
    print(f"      {len(cells)} populated cells")
    print("  [4/6] Direct-award reliance...")
    direct_award = insight_4_direct_award_reliance(conn)
    print(f"      {len(direct_award)} sectors")
    print("  [5/6] Trend...")
    trend = insight_5_trend(conn)
    print(f"      {len(trend)} sectors")
    print("  [6/6] Forward pipeline...")
    pipeline = insight_6_pipeline_density(conn)
    print(f"      {len(pipeline)} sectors")

    report = render_report(universe, sectors, cells, direct_award, trend, pipeline)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"directional-concentration-analysis-{datetime.utcnow().strftime('%Y-%m-%d')}.md"
    out.write_text(report, encoding="utf-8")
    print(f"\nWritten: {out}")
    print(f"Length: {len(report.splitlines())} lines")


if __name__ == "__main__":
    main()
