#!/usr/bin/env python3
"""
Re-run the strategic-supplier bid-spend model on the current database.

Compares:
  - Find a Tender data only (the original 2026-04-23 baseline of £3.9bn)
  - Find a Tender + Contracts Finder combined (current state)

Methodology comes from
  wiki/intel/Strategic Supplier Bid Spend Intelligence.md
  wiki/meta/2026-04-23-cfo-model.md
  pwin-competitive-intel/bidequity-cfo-model.html

Per tier:
  unique_competitions_won_by_strategic_suppliers × bidders_per_competition
   × bid_cost = annual_spend_per_tier

The smallest tier (<£5m / framework call-offs) was originally a bottom-up
estimate of 8,000 bids/year because Find a Tender captures <15% of small
contracts.

Window: trailing 12 months from today.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"

# 37 Cabinet Office strategic suppliers (2024-25 list).
# Each entry: (display name, list of LIKE patterns to match supplier name).
# Patterns are case-insensitive substring matches against suppliers.name.
STRATEGIC_SUPPLIERS = [
    ("Accenture",          ["accenture"]),
    ("Amazon Web Services",["amazon web services", "aws emea", "amazon eu sarl"]),
    ("Atos",               ["atos it services", "atos uk", "atos services"]),
    ("BAE Systems",        ["bae systems"]),
    ("Babcock",            ["babcock international", "babcock training", "babcock rail",
                            "babcock marine", "babcock vehicle", "altrad babcock"]),
    ("Balfour Beatty",     ["balfour beatty"]),
    ("Bouygues",           ["bouygues"]),
    ("BT",                 ["british telecommunications", "bt plc"]),
    ("CapGemini",          ["capgemini"]),
    ("Capita",             ["capita business", "capita customer", "capita it",
                            "capita resourcing", "capita pip", "capita plc",
                            "capita health", "capita managed", "capita translation"]),
    ("CGI",                ["cgi it uk", "cgi group"]),
    ("Compass",            ["compass contract services", "compass group"]),
    ("Computacenter",      ["computacenter"]),
    ("Deloitte",           ["deloitte"]),
    ("DXC",                ["dxc technology", "dxc business"]),
    ("EY",                 ["ernst & young", "ernst and young"]),
    ("Fujitsu",            ["fujitsu services", "fujitsu uk"]),
    ("G4S",                ["g4s secure", "g4s security", "g4s facility", "g4s facilities",
                            "g4s health"]),
    ("HPE",                ["hewlett packard enterprise", "hewlett-packard enterprise",
                            "hpe services"]),
    ("IBM",                ["ibm united kingdom"]),
    ("ISS",                ["iss facility", "iss mediclean"]),
    ("Kier",               ["kier construction", "kier highways", "kier services",
                            "kier infrastructure", "kier limited", "kier business"]),
    ("KPMG",               ["kpmg llp", "kpmg uk"]),
    ("Leidos",             ["leidos innovations", "leidos europe", "leidos uk", "leidos supply"]),
    ("Lockheed Martin",    ["lockheed martin"]),
    ("Microsoft",          ["microsoft limited", "microsoft ireland"]),
    ("Mitie",              ["mitie property", "mitie security", "mitie limited",
                            "mitie facilities", "mitie group", "mitie ic", "mitie tilley",
                            "mitie nuclear"]),
    ("Oracle",             ["oracle corporation uk", "oracle america"]),
    ("PwC",                ["pricewaterhousecoopers"]),
    ("Rolls-Royce",        ["rolls-royce", "rolls royce"]),
    ("Serco",              ["serco limited", "serco group", "serco solutions"]),
    ("Sodexo",             ["sodexo limited", "sodexo motivation", "sodexo healthcare",
                            "sodexo defence"]),
    ("Sopra Steria",       ["sopra steria"]),
    ("Telefonica",         ["telefónica", "telefonica"]),
    ("Telent",             ["telent technology"]),
    ("Vinci",              ["vinci construction", "vinci facilities", "vinci building",
                            "vinci uk"]),
    ("Wipro",              ["wipro limited"]),
]

# Tier definitions
TIERS = [
    ("Framework call-off (<£5m)",       0,            5_000_000,    None,    35_000),
    ("Notified small (£5-25m)",         5_000_000,    25_000_000,   8.2,     125_000),
    ("Notified mid (£25-100m)",         25_000_000,   100_000_000,  6.7,     550_000),
    ("Major services (£100-500m)",      100_000_000,  500_000_000,  7.3,     1_500_000),
    ("Strategic programme (£500m-5bn)", 500_000_000,  5_000_000_000, 5.6,    14_000_000),
    ("Defence mega (£5bn+)",            5_000_000_000, 10**15,      7.75,    25_000_000),
]

ORIGINAL_BIDS_PER_TIER = {
    "Framework call-off (<£5m)":        8000,
    "Notified small (£5-25m)":          515,
    "Notified mid (£25-100m)":          330,
    "Major services (£100-500m)":       350,
    "Strategic programme (£500m-5bn)":  150,
    "Defence mega (£5bn+)":             31,
}


def supplier_match_clause() -> str:
    """Build a (?,?,?,...) LIKE clause matching any strategic supplier pattern."""
    parts = []
    for _, patterns in STRATEGIC_SUPPLIERS:
        for p in patterns:
            parts.append(f"LOWER(s.name) LIKE '%{p}%'")
    return " OR ".join(parts)


def count_strategic_won_competitions(c, source_filter: str, since: str) -> dict:
    """Per tier, count unique competitions won by ANY strategic supplier."""
    where_source = ""
    if source_filter == "fts":
        where_source = "AND n.data_source = 'fts'"
    elif source_filter == "cf":
        where_source = "AND n.data_source = 'cf'"

    sup_clause = supplier_match_clause()

    out = {}
    for label, lo, hi, *_ in TIERS:
        q = f"""
        SELECT COUNT(DISTINCT n.ocid)
        FROM notices n
        JOIN awards a         ON a.ocid = n.ocid
        JOIN award_suppliers aws ON aws.award_id = a.id
        JOIN suppliers s      ON s.id = aws.supplier_id
        WHERE a.status = 'active'
          AND a.value_amount_gross >= ?
          AND a.value_amount_gross <  ?
          AND n.published_date >= ?
          AND ({sup_clause})
          {where_source}
        """
        out[label] = c.execute(q, (lo, hi, since)).fetchone()[0]
    return out


def total_strategic_wins(c, source_filter: str, since: str) -> int:
    """Total unique competitions won by any strategic supplier (any value)."""
    where_source = ""
    if source_filter == "fts":
        where_source = "AND n.data_source = 'fts'"
    elif source_filter == "cf":
        where_source = "AND n.data_source = 'cf'"
    sup_clause = supplier_match_clause()
    q = f"""
    SELECT COUNT(DISTINCT n.ocid)
    FROM notices n
    JOIN awards a         ON a.ocid = n.ocid
    JOIN award_suppliers aws ON aws.award_id = a.id
    JOIN suppliers s      ON s.id = aws.supplier_id
    WHERE a.status = 'active'
      AND n.published_date >= ?
      AND ({sup_clause})
      {where_source}
    """
    return c.execute(q, (since,)).fetchone()[0]


def model_total(unique_per_tier: dict) -> tuple[int, float, dict]:
    total_bids = 0
    total_spend = 0.0
    breakdown = {}
    for label, lo, hi, bidders, uc in TIERS:
        unique = unique_per_tier.get(label, 0)
        if bidders is None:
            bids = ORIGINAL_BIDS_PER_TIER[label]
            method = "bottom-up estimate"
        else:
            bids = round(unique * bidders)
            method = f"{unique} unique × {bidders}"
        spend = bids * uc
        breakdown[label] = (unique, bids, uc, spend, method)
        total_bids += bids
        total_spend += spend
    return total_bids, total_spend, breakdown


def fmt_money(v: float) -> str:
    if v >= 1e9:
        return f"£{v/1e9:.2f}bn"
    if v >= 1e6:
        return f"£{v/1e6:.0f}m"
    return f"£{v/1e3:.0f}k"


def print_breakdown(label: str, breakdown: dict, total_bids: int, total_spend: float):
    print(f"\n=== {label} ===")
    print(f"  {'Tier':<32}  {'Unique':>8}  {'Bids':>7}  {'Cost':>7}  {'Spend':>9}  Method")
    for tier_label, (unique, bids, uc, spend, method) in breakdown.items():
        print(f"  {tier_label:<32}  {unique:>8,}  {bids:>7,}  {fmt_money(uc):>7}  {fmt_money(spend):>9}  {method}")
    print(f"  {'TOTAL':<32}  {'':>8}  {total_bids:>7,}  {'':>7}  {fmt_money(total_spend):>9}")


def main() -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    today = datetime.now().date()
    since = (today - timedelta(days=365)).isoformat()
    print("Strategic supplier bid spend recalculation")
    print(f"Window: {since} to {today}")
    print(f"Strategic supplier list: {len(STRATEGIC_SUPPLIERS)} groups, "
          f"{sum(len(p) for _, p in STRATEGIC_SUPPLIERS)} name patterns")

    # Sanity: total wins by strategic suppliers in window
    print(f"\n--- Strategic-supplier wins in window (sanity check) ---")
    for src in ("fts", "cf", "both"):
        n = total_strategic_wins(c, src, since)
        print(f"  {src:<5}: {n:,} unique competitions won by a strategic supplier")
    print(f"  (original 2026-04-21 figure: 1,059 in FTS — same window)")

    # 1. FTS-only baseline
    fts_unique = count_strategic_won_competitions(c, "fts", since)
    fts_bids, fts_spend, fts_breakdown = model_total(fts_unique)
    print_breakdown("Find a Tender ONLY (recreates the original baseline)",
                    fts_breakdown, fts_bids, fts_spend)

    # 2. Combined
    both_unique = count_strategic_won_competitions(c, "both", since)
    both_bids, both_spend, both_breakdown = model_total(both_unique)
    print_breakdown("Find a Tender + Contracts Finder COMBINED",
                    both_breakdown, both_bids, both_spend)

    # 3. CF-only contribution
    cf_unique = count_strategic_won_competitions(c, "cf", since)
    print(f"\n=== Contracts Finder ONLY (the new contribution) ===")
    print(f"  {'Tier':<32}  {'Unique':>8}  Note")
    for tier_label, lo, hi, *_ in TIERS:
        u = cf_unique[tier_label]
        f = fts_unique[tier_label]
        if f > 0:
            ratio = f"{u/f:+.1f}× the FTS volume"
        else:
            ratio = "(FTS = 0)"
        print(f"  {tier_label:<32}  {u:>8,}  {ratio}")

    # 4. Headline comparison
    print()
    print("=" * 70)
    print("HEADLINE COMPARISON vs ORIGINAL BASELINE")
    print("=" * 70)
    print(f"  Original published figure (FTS only, April 2026):  £3.93bn / 9,376 bids")
    print(f"  This re-run (FTS only):                            {fmt_money(fts_spend)} / {fts_bids:,} bids")
    print(f"  This re-run (FTS + Contracts Finder combined):     {fmt_money(both_spend)} / {both_bids:,} bids")
    delta_pct = 100 * (both_spend - fts_spend) / max(fts_spend, 1)
    print(f"  Change vs FTS-only re-run:                         {delta_pct:+.1f}%")
    print()
    print(f"Sunk cost on losing bids (~67% loss rate at 33% baseline win rate):")
    print(f"  FTS only:   {fmt_money(fts_spend * 0.67)}")
    print(f"  Combined:   {fmt_money(both_spend * 0.67)}")
    print(f"  (original 'wasted £2bn' headline)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
