"""One-off harvest script for sector-margin defaults document (action A8).

Reads bid_intel.db and produces:
 1) coverage stats on Companies House enrichment
 2) top public-sector contractors per target sector, by total award value,
    rolled up via the canonical supplier layer

Sector buckets are defined by SIC-code prefix patterns and name keywords so
that we can flag the dominant set of contractors per sector even when
canonical names alone are ambiguous (e.g. Capita appears in multiple sectors).

Output: prints a markdown-friendly summary to stdout.
"""

import sqlite3
import json
import sys
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DB = r"c:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel\db\bid_intel.db"

# Sector definitions: (label, name keywords, SIC prefixes)
# SIC prefix list is illustrative — we use it to *boost* keyword-matched
# contractors that also have a matching SIC. Keyword match alone is fine.
SECTORS = {
    "BPO / outsourcing": {
        "name_keywords": [
            "capita", "serco", "mitie", "g4s", "sopra", "atos",
            "concentrix", "teleperformance", "arvato", "shared services",
            "outsourcing",
        ],
        "sic_prefixes": ["8211", "8219", "8220", "8299"],
    },
    "IT services": {
        "name_keywords": [
            "fujitsu", "accenture", "cgi", "cap gemini", "capgemini",
            "ibm", "dxc", "computacenter", "softcat", "bytes", "phoenix",
            "kainos", "bjss", "tcs", "tata consultancy", "infosys", "wipro",
            "hcl", "cognizant", "ncr", "civica", "leidos", "bae applied",
            "bae digital", "northgate public", "agilisys", "softwareone",
        ],
        "sic_prefixes": ["6201", "6202", "6203", "6209", "6311"],
    },
    "Facilities management": {
        "name_keywords": [
            "iss", "compass", "sodexo", "engie", "equans", "vinci facilities",
            "kier facilities", "interserve", "amey", "carillion", "bouygues",
            "cbre", "jll", "mitie", "serco", "skanska facilities",
        ],
        "sic_prefixes": ["8110", "8121", "8122", "8129", "8130", "8110"],
    },
    "Construction / civils": {
        "name_keywords": [
            "balfour beatty", "kier", "morgan sindall", "vinci", "skanska",
            "laing o'rourke", "costain", "galliford", "willmott dixon",
            "wates", "interserve construction", "bam", "mace", "bouygues uk",
            "henry boot", "graham construction", "robertson", "isg", "tilbury",
            "volkerwessels", "amey", "j murphy",
        ],
        "sic_prefixes": ["4110", "4120", "4211", "4212", "4213", "4221", "4222", "4291", "4299", "4321", "4322"],
    },
    "Defence": {
        "name_keywords": [
            "bae systems", "babcock", "qinetiq", "leonardo", "thales",
            "lockheed", "raytheon", "general dynamics", "northrop",
            "rolls-royce", "rolls royce", "marshall aerospace", "ultra electronics",
            "chemring", "cobham", "saab", "mbda", "elbit", "rheinmetall",
            "kbr", "leidos",
        ],
        "sic_prefixes": ["3030", "2540", "3040", "3315"],
    },
    "Consulting / advisory": {
        "name_keywords": [
            "deloitte", "pwc", "pricewaterhouse", "kpmg", "ey ", "ernst & young",
            "ernst and young", "mckinsey", "bain", "boston consulting",
            "accenture strategy", "oliver wyman", "roland berger", "ad littl",
            "pa consulting", "newton europe", "north highland", "credera",
            "baringa", "alixpartners", "ankura", "ftI consulting", "cratus",
            "atkins", "mott macdonald", "wsp", "arup", "ricardo",
        ],
        "sic_prefixes": ["7022", "7021", "7010", "7022", "7090"],
    },
}


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1) Coverage
    print("# Coverage stats\n")
    c.execute("SELECT COUNT(*) FROM suppliers")
    print("Total suppliers:", c.fetchone()[0])
    for q, label in [
        ("companies_house_no IS NOT NULL", "Has CH number"),
        ("ch_status IS NOT NULL", "CH-enriched (any field)"),
        ("ch_turnover IS NOT NULL", "Has turnover"),
        ("ch_net_assets IS NOT NULL", "Has net assets"),
        ("ch_employees IS NOT NULL", "Has employee count"),
    ]:
        c.execute(f"SELECT COUNT(*) FROM suppliers WHERE {q}")
        print(f"  {label}:", c.fetchone()[0])

    # Confirm there is no operating-profit field
    c.execute("PRAGMA table_info(suppliers)")
    cols = [r[1] for r in c.fetchall()]
    profit_cols = [c for c in cols if "profit" in c.lower() or "ebit" in c.lower() or "operating" in c.lower()]
    print("\nProfit-style columns in suppliers:", profit_cols or "(none)")

    # 2) Top contractors per sector via canonical layer
    # Roll up canonical_id, then join back to a representative supplier with CH data.
    print("\n# Top contractors per sector\n")

    for sector_label, defn in SECTORS.items():
        kw_clauses = " OR ".join(["LOWER(cs.canonical_name) LIKE ?" for _ in defn["name_keywords"]])
        params = [f"%{kw.lower()}%" for kw in defn["name_keywords"]]

        sql = f"""
        SELECT
            v.canonical_id,
            v.canonical_name,
            SUM(COALESCE(v.value_amount_gross, 0)) AS total_value,
            COUNT(DISTINCT v.award_id) AS award_count,
            -- pick MAX of CH fields across the cluster's members (best available)
            MAX(s.ch_status) AS ch_status,
            MAX(s.ch_turnover) AS ch_turnover,
            MAX(s.ch_net_assets) AS ch_net_assets,
            MAX(s.ch_employees) AS ch_employees,
            MAX(s.ch_parent) AS ch_parent
        FROM v_canonical_supplier_wins v
        JOIN canonical_suppliers cs ON v.canonical_id = cs.canonical_id
        LEFT JOIN suppliers s ON s.id = v.raw_supplier_id
        WHERE ({kw_clauses})
          AND COALESCE(v.value_quality, '') <> 'suspect_outlier'
        GROUP BY v.canonical_id, v.canonical_name
        ORDER BY total_value DESC
        LIMIT 12
        """
        try:
            c.execute(sql, params)
            rows = c.fetchall()
        except sqlite3.OperationalError as e:
            print(f"## {sector_label}\n  SQL error: {e}\n")
            continue

        print(f"## {sector_label}")
        if not rows:
            print("  (no matches)\n")
            continue
        print(f"  {'Canonical name':<45} {'Total £m':>10} {'Awards':>7}  {'CH status':<12} {'Turnover £m':>12} {'Net assets £m':>14}  Parent")
        for r in rows:
            tv = (r["total_value"] or 0) / 1e6
            to = (r["ch_turnover"] or 0) / 1e6 if r["ch_turnover"] else None
            na = (r["ch_net_assets"] or 0) / 1e6 if r["ch_net_assets"] else None
            print(
                f"  {(r['canonical_name'] or '')[:43]:<45}"
                f" {tv:>10,.0f}"
                f" {r['award_count']:>7}"
                f"  {(r['ch_status'] or '-'):<12}"
                f" {(f'{to:>12,.0f}' if to is not None else '          --')}"
                f" {(f'{na:>14,.0f}' if na is not None else '            --')}"
                f"  {(r['ch_parent'] or '')[:50]}"
            )
        print()

    conn.close()


if __name__ == "__main__":
    main()
