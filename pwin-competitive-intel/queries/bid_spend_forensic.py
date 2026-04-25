#!/usr/bin/env python3
"""
Forensic, line-by-line bid spend calculation.

Replaces tier-based blended assumptions with per-contract calculations:
  for each strategic-supplier-won contract:
    bid_cost = base_cost(actual_TCV) × bid_type_multiplier
  total = sum across all contracts

Plus a refined classification that distinguishes:
  - Framework AGREEMENTS (parent panels — heavy upfront process)
  - Framework CALL-OFFS (transactions under a framework — lighter process)
  - Several signals for the previously-unclassified bucket

Window: trailing 12 months from today.
"""
from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"

# Strategic supplier list (37 groups)
STRATEGIC_SUPPLIERS = [
    "accenture", "amazon web services", "aws emea", "amazon eu sarl",
    "atos it services", "atos uk", "atos services", "bae systems",
    "babcock international", "babcock training", "babcock rail",
    "babcock marine", "babcock vehicle", "altrad babcock", "balfour beatty",
    "bouygues", "british telecommunications", "bt plc", "capgemini",
    "capita business", "capita customer", "capita it", "capita resourcing",
    "capita pip", "capita plc", "capita health", "capita managed",
    "capita translation", "cgi it uk", "cgi group", "compass contract services",
    "compass group", "computacenter", "deloitte", "dxc technology",
    "dxc business", "ernst & young", "ernst and young", "fujitsu services",
    "fujitsu uk", "g4s secure", "g4s security", "g4s facility",
    "g4s facilities", "g4s health", "hewlett packard enterprise",
    "hewlett-packard enterprise", "hpe services", "ibm united kingdom",
    "iss facility", "iss mediclean", "kier construction", "kier highways",
    "kier services", "kier infrastructure", "kier limited", "kier business",
    "kpmg llp", "kpmg uk", "leidos innovations", "leidos europe",
    "leidos uk", "leidos supply", "lockheed martin", "microsoft limited",
    "microsoft ireland", "mitie property", "mitie security", "mitie limited",
    "mitie facilities", "mitie group", "mitie ic", "mitie tilley",
    "mitie nuclear", "oracle corporation uk", "oracle america",
    "pricewaterhousecoopers", "rolls-royce", "rolls royce", "serco limited",
    "serco group", "serco solutions", "sodexo limited", "sodexo motivation",
    "sodexo healthcare", "sodexo defence", "sopra steria", "telefónica",
    "telefonica", "telent technology", "vinci construction", "vinci facilities",
    "vinci building", "vinci uk", "wipro limited",
]


# ─────────────────────────────────────────────────────────────────────────────
# Bid-type multipliers — agreed with user 2026-04-25
# ─────────────────────────────────────────────────────────────────────────────
BID_TYPES = {
    "framework_agreement": {
        "label": "Framework agreement (set up the panel)",
        "bidders": 6,
        "cost_multiplier": 1.20,   # heavier — sets up the rules of engagement
        "win_rate": 0.30,
        # Cap per-bidder cost: framework ceilings can be £100m+ but the
        # *effective* revenue per panel member is much smaller. A panel slot
        # is worth bidding ~£200k-£1.5m to win, regardless of nominal ceiling.
        "max_cost_per_bidder": 1_000_000,
    },
    "competitive_dialogue": {
        "label": "Competitive dialogue / negotiated with publication",
        "bidders": 4,
        "cost_multiplier": 1.30,
        "win_rate": 0.30,
    },
    "open_competition": {
        "label": "Open competitive bid (greenfield)",
        "bidders": 7,
        "cost_multiplier": 1.00,
        "win_rate": 0.25,
    },
    "restricted_competition": {
        "label": "Restricted (invitation-only after pre-qualification)",
        "bidders": 5,
        "cost_multiplier": 1.00,
        "win_rate": 0.35,
    },
    "framework_call_off": {
        "label": "Framework call-off / mini-competition",
        "bidders": 4,
        "cost_multiplier": 0.65,
        "win_rate": 0.30,
        "min_cost": 35_000,   # floor: even small call-offs cost ~£35k to bid
    },
    "recompete_renewal": {
        "label": "Renewal / recompete",
        "bidders": 3,
        "cost_multiplier": 0.90,   # incumbent 70% × 1 + challengers 100% × 2 / 3
        "win_rate": 0.33,
    },
    "extension_modification": {
        "label": "Extension / modification",
        "bidders": 1,
        "cost_multiplier": 0.35,   # AGREED 2026-04-25
        "win_rate": 0.95,
    },
    "direct_award": {
        "label": "Direct award (winning-supplier effort only)",
        "bidders": 1,
        "cost_multiplier": 0.35,   # AGREED 2026-04-25
        "win_rate": 1.00,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Per-contract bid-cost function (open-competition baseline).
# Anchored on cost-of-sale economics, validated against real bids:
#   Selborne £1.2bn / 2yr / £12m  → 1.0% at £1.2bn
#   £25m deal — user benchmark    → ~2.5%, i.e. £625k
#   £200k framework call-off       → £35k floor (~17% — fixed-cost zone)
# ─────────────────────────────────────────────────────────────────────────────
def base_cost_for_value(v: float) -> float:
    """Open-competition full-effort bid cost as a function of contract value."""
    if v < 100_000:
        return 15_000
    if v < 1_000_000:
        return max(35_000, v * 0.05)        # ~5% with floor
    if v < 5_000_000:
        return max(75_000, v * 0.035)       # ~3.5%
    if v < 25_000_000:
        return v * 0.025                    # ~2.5%
    if v < 100_000_000:
        return v * 0.020                    # ~2%
    if v < 500_000_000:
        return v * 0.013                    # ~1.3%
    if v < 5_000_000_000:
        return v * 0.008                    # ~0.8%
    return v * 0.004                        # ~0.4% (defence megas — ceiling)


def bid_cost_per_bidder(value: float, bid_type: str) -> float:
    bt = BID_TYPES[bid_type]
    raw = base_cost_for_value(value) * bt["cost_multiplier"]
    floor = bt.get("min_cost", 0)
    cap = bt.get("max_cost_per_bidder", float("inf"))
    return max(min(raw, cap), floor)


# ─────────────────────────────────────────────────────────────────────────────
# Refined classification — distinguishes framework agreements from call-offs
# and uses a wider set of signals to reduce the "unclassified" bucket.
# ─────────────────────────────────────────────────────────────────────────────
def classify(row: dict) -> str:
    """Classify a contract by bid type using all available signals.

    Priority-ordered: most specific signal wins. Last-resort rules use
    value bands and notice subtype to reduce the unclassified pile.
    """
    title = (row.get("title") or "").lower()
    pmd = (row.get("procurement_method_detail") or "").lower()
    pm = (row.get("procurement_method") or "").lower()
    notice_type = (row.get("notice_type") or "").lower()
    is_fw = row.get("is_framework") == 1
    parent_fw = row.get("parent_framework_ocid")
    value = row.get("value") or 0

    # 1. Direct award signals — explicit
    if any([
        "award procedure without prior publication" in pmd,
        "negotiated without publication" in pmd,
        "direct award" in title,
        pm == "limited",
    ]):
        return "direct_award"

    # NEW: UK Procurement Act 2023 transparency notice (UK4) = direct award
    if notice_type in ("uk4", "transparency notice"):
        return "direct_award"

    # 2. Extension / modification
    if any([
        "modification" in notice_type,
        "amendment" in notice_type,
        notice_type == "uk7",   # UK7 = Contract change notice
        "extension" in title,
        "modification" in title,
        "modificat" in title,
        title.startswith("extend"),
    ]):
        return "extension_modification"

    # 3. Framework call-off (transaction UNDER an existing framework)
    if any([
        parent_fw is not None,
        "call-off" in title,
        "call off" in title,
        "mini-competit" in title,
        "mini competit" in title,
        "further competition" in title,
    ]):
        return "framework_call_off"

    # 4. Framework agreement (the parent panel itself)
    if is_fw or "framework agreement" in title or "framework contract" in title:
        return "framework_agreement"

    # 5. Renewal / recompete
    if any([
        row.get("has_renewal") == 1,
        "renewal" in title,
        "recompet" in title,
        "follow-on" in title,
        "follow on" in title,
        "continuation" in title,
    ]):
        return "recompete_renewal"

    # 6. Open competition
    if "open procedure" in pmd or pm == "open":
        return "open_competition"

    # 7. Restricted
    if "restricted" in pmd or pm == "selective":
        return "restricted_competition"

    # 8. Competitive dialogue / negotiated with publication
    if "competitive dialogue" in pmd or "negotiated" in pmd:
        return "competitive_dialogue"

    # ─── Last-resort fallback rules ──────────────────────────────────────
    # By the time we get here we've seen no procurement_method (mostly
    # Contracts Finder data) and no obvious title keyword. Use value bands
    # and notice subtype to pick the most likely category.

    # Title-based hints
    if "tender" in title:
        return "open_competition"
    if any(k in title for k in ["supply of", "provision of", "lot ", " lot:"]):
        # Very common in framework call-offs
        return "framework_call_off"

    # UK Procurement Act notice subtype hints
    # UK6 = Contract details notice (a normal award publication — could be any type)
    # UK5 = Contract award notice (same)
    # UK12 = Contract performance notice (post-award, treat as part of life of an award)
    # We can't pin these down further, so fall through to the value-based default

    # Value-based default for everything else
    # Sub-£100k spend is almost always direct purchase / micro-procurement
    # £100k-£5m is most often a framework call-off in the public sector
    # £5m+ unclassified treated as restricted competition (cautious assumption)
    if value < 100_000:
        return "direct_award"
    if value < 5_000_000:
        return "framework_call_off"
    return "restricted_competition"


def fmt_money(v: float) -> str:
    if v >= 1e9:
        return f"£{v/1e9:.2f}bn"
    if v >= 1e6:
        return f"£{v/1e6:,.1f}m"
    if v >= 1e3:
        return f"£{v/1e3:,.0f}k"
    return f"£{v:,.0f}"


def main() -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.now().date()
    since = (today - timedelta(days=365)).isoformat()

    print("Forensic line-by-line bid spend calculation")
    print(f"Window: {since} to {today}")
    print(f"Method: per-contract base cost (function of TCV) × bid-type multiplier")
    print()

    sup_clause = " OR ".join(f"LOWER(s.name) LIKE '%{p}%'" for p in STRATEGIC_SUPPLIERS)

    q = f"""
    SELECT DISTINCT
      n.ocid, n.title, n.procurement_method, n.procurement_method_detail,
      n.is_framework, n.parent_framework_ocid, n.has_renewal, n.notice_type,
      a.value_amount_gross AS value, n.data_source
    FROM notices n
    JOIN awards a ON a.ocid = n.ocid
    JOIN award_suppliers aws ON aws.award_id = a.id
    JOIN suppliers s ON s.id = aws.supplier_id
    WHERE a.status = 'active'
      AND a.value_amount_gross >= 25000
      AND n.published_date >= ?
      AND ({sup_clause})
    """
    rows = c.execute(q, (since,)).fetchall()
    contracts = [dict(zip(["ocid","title","procurement_method","procurement_method_detail","is_framework","parent_framework_ocid","has_renewal","notice_type","value","data_source"], r)) for r in rows]
    print(f"Loaded {len(contracts):,} unique strategic-supplier-won contracts (≥£25k, last 12m)")

    # Classify each
    by_type: dict[str, list[dict]] = defaultdict(list)
    for ct in contracts:
        bt = classify(ct)
        ct["bid_type"] = bt
        by_type[bt].append(ct)

    print(f"\n=== Classification breakdown ===")
    print(f"{'Bid type':<55}  {'Count':>5}  {'%':>5}  {'Median TCV':>12}  {'Total TCV':>14}")
    for bt, cs in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        if not cs:
            continue
        vals = sorted([ct["value"] for ct in cs])
        median = vals[len(vals)//2]
        total = sum(vals)
        pct = 100 * len(cs) / len(contracts)
        label = BID_TYPES.get(bt, {"label": bt})["label"]
        print(f"  {label:<53}  {len(cs):>5}  {pct:>4.1f}%  {fmt_money(median):>12}  {fmt_money(total):>14}")

    # Compute bid spend line by line
    print(f"\n=== Industry pursuit spend — per-contract calculation ===")
    print(f"{'Bid type':<55}  {'Count':>5}  {'Bidders':>7}  {'Spend':>10}  {'Sunk':>10}")
    grand_spend = 0.0
    grand_sunk = 0.0
    grand_bids = 0
    for bt in BID_TYPES:
        if bt not in by_type:
            continue
        cs = by_type[bt]
        bidders = BID_TYPES[bt]["bidders"]
        win_rate = BID_TYPES[bt]["win_rate"]
        # For each contract: per-bidder cost × bidders = competition spend
        # × (1 - win_rate) = sunk
        spend = 0.0
        sunk = 0.0
        for ct in cs:
            per_bidder = bid_cost_per_bidder(ct["value"], bt)
            comp_spend = per_bidder * bidders
            spend += comp_spend
            sunk += comp_spend * (1 - win_rate)
        bids = len(cs) * bidders
        grand_spend += spend
        grand_sunk += sunk
        grand_bids += bids
        label = BID_TYPES[bt]["label"]
        print(f"  {label:<53}  {len(cs):>5}  {bidders:>7}  {fmt_money(spend):>10}  {fmt_money(sunk):>10}")

    # Unclassified — apply per-tier mix from classified
    if "unclassified" in by_type:
        un = by_type["unclassified"]
        # Build classified-only bid type weighting
        classified_total = sum(len(v) for k, v in by_type.items() if k != "unclassified")
        weights = {bt: len(v) / classified_total for bt, v in by_type.items() if bt != "unclassified"}
        spend = 0.0
        sunk = 0.0
        for ct in un:
            for bt, w in weights.items():
                per_bidder = bid_cost_per_bidder(ct["value"], bt)
                bidders = BID_TYPES[bt]["bidders"]
                win_rate = BID_TYPES[bt]["win_rate"]
                comp_spend = per_bidder * bidders * w
                spend += comp_spend
                sunk += comp_spend * (1 - win_rate)
        grand_spend += spend
        grand_sunk += sunk
        print(f"  {'(Unclassified — distributed using classified mix)':<53}  {len(un):>5}  {'~':>7}  {fmt_money(spend):>10}  {fmt_money(sunk):>10}")

    print(f"\n  {'TOTAL':<53}  {len(contracts):>5}  {grand_bids:>7,}  {fmt_money(grand_spend):>10}  {fmt_money(grand_sunk):>10}")

    # Sanity check vs the cost-of-sale benchmark
    total_tcv = sum(ct["value"] for ct in contracts)
    avg_pct = 100 * grand_spend / total_tcv if total_tcv > 0 else 0
    print(f"\n  Total contract value across all wins: {fmt_money(total_tcv)}")
    print(f"  Industry pursuit spend as % of total TCV: {avg_pct:.2f}%")
    print(f"  (Cost-of-sale benchmark: ~2-3% expected for typical mix)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
