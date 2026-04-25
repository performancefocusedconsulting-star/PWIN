#!/usr/bin/env python3
"""
Bid-type-aware industry pursuit spend model.

Why this exists
---------------
The earlier model (queries/bid_spend_recalc.py) tiered every competition by
contract value alone, then multiplied unique-competitions × ~7 bidders × full
bid cost. That overstates the true spend because it counts:

  - Direct awards (no competitive bid took place)
  - Contract extensions (negotiation, not a bid)
  - Renewal / recompete (cheaper than greenfield — incumbency, templates)
  - All multi-bidder competitions at the same per-bid cost

This model classifies every big contract into one of 8 bid types using the
structured fields in the database, then applies differentiated costs and win
rates per type. Every assumption is visible in this file so a CFO can audit
each lever.

Methodology
-----------
Step 1: Classify each unique competition by bid type
        (priority order: most-specific signal wins)
Step 2: Filter to competitions won by a strategic supplier
Step 3: For each (value tier × bid type), compute:
          bidders_count × bid_cost = pursuit spend per competition
Step 4: Sum across all classified competitions
Step 5: For unclassified competitions (mostly Contracts Finder data with no
        procurement_method field), apply the same mix as classified

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

# ─────────────────────────────────────────────────────────────────────────────
# 1. Strategic supplier list (37 Cabinet Office groups)
# ─────────────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# 2. Bid type definitions and classification logic
#
# Eight bid types, ordered from highest-effort to lowest-effort. Each
# contract is classified into ONE bid type via priority-ordered signals
# (the first matching rule wins).
#
# For each bid type:
#   bidders          = avg number of strategic-supplier-class bidders per comp.
#   cost_multiplier  = effort relative to baseline open-competition cost
#                       (1.0 = full bid; 0.0 = no bid took place)
#   win_rate         = the assumed win rate for the typical strategic bidder
#
# Sources for the multipliers and win rates are noted inline. Adjust here.
# ─────────────────────────────────────────────────────────────────────────────
BID_TYPES = {
    "competitive_dialogue": {
        "label":           "Competitive dialogue / negotiated with publication",
        "bidders":         4,    # smaller field — heavy upfront cost selects out
        "cost_multiplier": 1.30, # extra discovery / dialogue rounds
        "win_rate":        0.30,
    },
    "open_competition": {
        "label":           "Open competitive bid (greenfield)",
        "bidders":         7,    # original CFO model assumption
        "cost_multiplier": 1.00, # baseline
        "win_rate":        0.25, # largest field — typical industry win rate
    },
    "restricted_competition": {
        "label":           "Restricted (invitation-only after pre-qualification)",
        "bidders":         5,    # pre-qualified field is smaller
        "cost_multiplier": 0.90, # similar effort, slightly less wasted on losing PQQ
        "win_rate":        0.35, # smaller field, higher per-bidder odds
    },
    "framework_call_off": {
        "label":           "Framework call-off / mini-competition",
        "bidders":         4,    # framework limits the field
        "cost_multiplier": 1.00, # uses the £35k tier baseline (not relative to greenfield)
        "win_rate":        0.33,
        "fixed_cost":      35000,  # overrides the tier-based cost
    },
    "recompete_renewal": {
        "label":           "Renewal / recompete (defending or attacking a known scope)",
        "bidders":         3,    # incumbent + 2 challengers typical
        "cost_multiplier": 0.70, # templates, relationships, accumulated knowledge
        "win_rate":        0.50, # incumbent advantage averaged across both sides
    },
    "extension_modification": {
        "label":           "Extension / contract modification",
        "bidders":         1,    # only the incumbent is involved
        "cost_multiplier": 0.15, # negotiation effort only, no bid response
        "win_rate":        0.95, # incumbents almost always get the extension
    },
    "direct_award": {
        "label":           "Direct award (no competitive process)",
        "bidders":         1,    # the awarded supplier
        "cost_multiplier": 0.00, # no bid effort
        "win_rate":        1.00, # by definition
    },
    "unclassified": {
        "label":           "Unclassified (default mix applied)",
        "bidders":         5,    # blended
        "cost_multiplier": 0.75, # blended (calculated below from observed mix)
        "win_rate":        0.33,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. Value tiers (unchanged from earlier model — these are the per-tier
#    BASELINE bid costs at full-effort open competition. Bid-type multipliers
#    are then applied on top.)
# ─────────────────────────────────────────────────────────────────────────────
TIERS = [
    ("Sub-threshold (<£100k)",           0,            100_000,      15_000),
    ("Small call-off (£100k-1m)",        100_000,      1_000_000,    25_000),
    ("Framework call-off (£1-5m)",       1_000_000,    5_000_000,    50_000),
    ("Notified small (£5-25m)",          5_000_000,    25_000_000,   150_000),
    ("Notified mid (£25-100m)",          25_000_000,   100_000_000,  550_000),
    ("Major services (£100-500m)",       100_000_000,  500_000_000,  1_500_000),
    ("Strategic programme (£500m-5bn)",  500_000_000,  5_000_000_000, 14_000_000),
    ("Defence mega (£5bn+)",             5_000_000_000, 10**15,       25_000_000),
]


def supplier_clause() -> str:
    parts = []
    for _, patterns in STRATEGIC_SUPPLIERS:
        for p in patterns:
            parts.append(f"LOWER(s.name) LIKE '%{p}%'")
    return " OR ".join(parts)


def classify_bid_type(row: dict) -> str:
    """Apply priority-ordered classification rules to one contract row.

    Order matters — first matching rule wins. Most specific first.
    Inputs:
      row['title']                    str
      row['procurement_method']       str | None
      row['procurement_method_detail']str | None
      row['is_framework']             0/1
      row['parent_framework_ocid']    str | None
      row['has_renewal']              0/1
      row['notice_type']              str | None
    """
    title = (row.get("title") or "").lower()
    pmd   = (row.get("procurement_method_detail") or "").lower()
    pm    = (row.get("procurement_method") or "").lower()
    notice_type = (row.get("notice_type") or "").lower()

    # 1. Direct award — no competitive process at all
    direct_signals = [
        "award procedure without prior publication" in pmd,
        "negotiated without publication" in pmd,
        "direct award" in title,
        pm == "limited",  # OCDS "limited" = single supplier
    ]
    if any(direct_signals):
        return "direct_award"

    # 2. Extension / modification
    extension_signals = [
        "modification" in notice_type,
        "amendment" in notice_type,
        "extension" in title,
        "modification" in title,
        "modificat" in title,
        "extend " in title or title.startswith("extend"),
        " amend" in title and "amendment" not in title.split()[0:2],
    ]
    if any(extension_signals):
        return "extension_modification"

    # 3. Framework call-off
    framework_signals = [
        row.get("is_framework") == 1,
        row.get("parent_framework_ocid"),
        "call-off" in title,
        "call off" in title,
        "mini-competit" in title,
        "mini competit" in title,
        "further competition" in title,
    ]
    if any(framework_signals):
        return "framework_call_off"

    # 4. Renewal / recompete
    renewal_signals = [
        row.get("has_renewal") == 1,
        "renewal" in title,
        "recompet" in title,
        "follow-on" in title,
        "follow on" in title,
        "continuation" in title,
    ]
    if any(renewal_signals):
        return "recompete_renewal"

    # 5. Open competition
    if "open procedure" in pmd or pm == "open":
        return "open_competition"

    # 6. Restricted competition
    if "restricted" in pmd or pm == "selective":
        return "restricted_competition"

    # 7. Competitive dialogue / negotiated with publication
    if "competitive dialogue" in pmd or "negotiated" in pmd:
        return "competitive_dialogue"

    # 8. Anything else — unclassified (mostly CF data with no procurement_method)
    return "unclassified"


def value_tier(value: float) -> int | None:
    for i, (_, lo, hi, _) in enumerate(TIERS):
        if value is not None and lo <= value < hi:
            return i
    return None


def fetch_competitions(c, source_filter: str, since: str) -> list[dict]:
    """Return all big-contract competitions won by a strategic supplier."""
    where_source = ""
    if source_filter == "fts":
        where_source = "AND n.data_source = 'fts'"
    elif source_filter == "cf":
        where_source = "AND n.data_source = 'cf'"

    # Lowered floor to £25k — captures small framework call-offs.
    # Below £25k is mostly direct purchases / micro-procurement, irrelevant
    # to strategic-supplier pursuit cost analysis.
    q = f"""
    SELECT DISTINCT
      n.ocid, n.title, n.procurement_method, n.procurement_method_detail,
      n.is_framework, n.parent_framework_ocid, n.has_renewal, n.notice_type,
      a.value_amount_gross AS value, n.data_source
    FROM notices n
    JOIN awards a            ON a.ocid = n.ocid
    JOIN award_suppliers aws ON aws.award_id = a.id
    JOIN suppliers s         ON s.id = aws.supplier_id
    WHERE a.status = 'active'
      AND a.value_amount_gross >= 25000
      AND n.published_date >= ?
      AND ({supplier_clause()})
      {where_source}
    """
    rows = []
    for r in c.execute(q, (since,)).fetchall():
        rows.append({
            "ocid": r[0], "title": r[1], "procurement_method": r[2],
            "procurement_method_detail": r[3], "is_framework": r[4],
            "parent_framework_ocid": r[5], "has_renewal": r[6],
            "notice_type": r[7], "value": r[8], "data_source": r[9],
        })
    return rows


def compute_industry_spend(competitions: list[dict]) -> tuple[dict, float, int]:
    """Returns ((tier, bid_type) -> stats), total_spend, total_competitions.

    Stats per cell: dict with keys 'count' (unique comps), 'bids' (× bidders),
    'spend' (£), 'won_bids' (× win_rate)."""
    cells: dict[tuple, dict] = defaultdict(lambda: {"count": 0, "bids": 0, "spend": 0.0, "won_bids": 0.0})

    # First pass: everything except 'unclassified'.
    # Track classified mix PER TIER so we can distribute unclassified
    # competitions using same-tier observed proportions, not global ones.
    per_tier_mix: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    unclassified: list[dict] = []
    for comp in competitions:
        t = value_tier(comp["value"])
        if t is None:
            continue
        bt = classify_bid_type(comp)
        if bt == "unclassified":
            unclassified.append(comp)
        else:
            per_tier_mix[t][bt] += 1
            apply_to_cell(cells, t, bt, n=1)

    # Global fallback mix for tiers with no classified data
    global_mix: dict[str, int] = defaultdict(int)
    for tier_mix in per_tier_mix.values():
        for bt, n in tier_mix.items():
            global_mix[bt] += n
    global_total = sum(global_mix.values()) or 1

    # Second pass: distribute unclassified per same-tier mix
    for comp in unclassified:
        t = value_tier(comp["value"])
        if t is None:
            continue
        tier_mix = per_tier_mix.get(t)
        if tier_mix and sum(tier_mix.values()) >= 5:
            # Use this tier's observed mix (need >= 5 classified observations)
            mix = tier_mix
            mix_total = sum(mix.values())
        else:
            # Too few same-tier observations — fall back to global mix
            mix = global_mix
            mix_total = global_total
        for bt, n in mix.items():
            share = n / mix_total
            apply_to_cell(cells, t, bt, n=share)

    total_spend = sum(c["spend"] for c in cells.values())
    total_comps = len(competitions)
    return cells, total_spend, total_comps


def apply_to_cell(cells: dict, tier_idx: int, bid_type: str, n: float):
    bt = BID_TYPES[bid_type]
    if bid_type == "framework_call_off":
        cost_per_bid = bt["fixed_cost"]
    else:
        cost_per_bid = TIERS[tier_idx][3] * bt["cost_multiplier"]
    bids = n * bt["bidders"]
    spend = bids * cost_per_bid
    cell = cells[(tier_idx, bid_type)]
    cell["count"]    += n
    cell["bids"]     += bids
    cell["spend"]    += spend
    cell["won_bids"] += bids * bt["win_rate"]


def fmt_money(v: float) -> str:
    if v >= 1e9: return f"£{v/1e9:.2f}bn"
    if v >= 1e6: return f"£{v/1e6:,.0f}m"
    if v >= 1e3: return f"£{v/1e3:,.0f}k"
    return f"£{v:,.0f}"


def report(label: str, cells: dict, total_spend: float, total_comps: int):
    print(f"\n{'='*78}")
    print(f"  {label}")
    print(f"{'='*78}")
    print(f"  Total unique competitions won by strategic suppliers: {total_comps:,}")
    print(f"  Total industry pursuit spend:                          {fmt_money(total_spend)}")
    won = sum(c["won_bids"] for c in cells.values())
    bids = sum(c["bids"] for c in cells.values())
    lost = bids - won
    if bids > 0:
        avg_win = won / bids
        sunk_pct = (lost / bids)
        sunk_spend = sum(
            c["spend"] * (1 - BID_TYPES[bt]["win_rate"])
            for (t, bt), c in cells.items()
        )
        print(f"  Total bids generated (× bidder count):                {bids:,.0f}")
        print(f"  Effective blended win rate:                           {avg_win*100:.1f}%")
        print(f"  Sunk cost on losing bids:                             {fmt_money(sunk_spend)}")

    # Per bid-type summary
    print(f"\n  Per bid type:")
    print(f"  {'Bid type':<55}  {'Comps':>6}  {'Bids':>7}  {'Spend':>10}")
    by_type: dict = defaultdict(lambda: {"count":0,"bids":0,"spend":0.0})
    for (t, bt), c in cells.items():
        by_type[bt]["count"] += c["count"]
        by_type[bt]["bids"]  += c["bids"]
        by_type[bt]["spend"] += c["spend"]
    for bt, stats in sorted(by_type.items(), key=lambda kv: -kv[1]["spend"]):
        print(f"  {BID_TYPES[bt]['label']:<55}  {stats['count']:>6,.0f}  {stats['bids']:>7,.0f}  {fmt_money(stats['spend']):>10}")

    # Per tier summary
    print(f"\n  Per value tier:")
    print(f"  {'Tier':<35}  {'Comps':>6}  {'Bids':>7}  {'Spend':>10}")
    by_tier: dict = defaultdict(lambda: {"count":0,"bids":0,"spend":0.0})
    for (t, bt), c in cells.items():
        by_tier[t]["count"] += c["count"]
        by_tier[t]["bids"]  += c["bids"]
        by_tier[t]["spend"] += c["spend"]
    for t in sorted(by_tier.keys()):
        stats = by_tier[t]
        print(f"  {TIERS[t][0]:<35}  {stats['count']:>6,.0f}  {stats['bids']:>7,.0f}  {fmt_money(stats['spend']):>10}")


def main() -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    today = datetime.now().date()
    since = (today - timedelta(days=365)).isoformat()
    print(f"Bid-type-aware industry pursuit spend model")
    print(f"Window: {since} to {today}")
    print(f"Strategic supplier list: {len(STRATEGIC_SUPPLIERS)} groups")

    # Run on combined dataset
    print(f"\n[1/2] Loading competitions (Find a Tender + Contracts Finder)...")
    comps_both = fetch_competitions(c, "both", since)
    print(f"  Loaded {len(comps_both):,} unique competitions won by a strategic supplier")

    # Show classification breakdown
    classification_counts: dict[str, int] = defaultdict(int)
    for comp in comps_both:
        bt = classify_bid_type(comp)
        classification_counts[bt] += 1
    print(f"\nBid type classification (combined data):")
    for bt, n in sorted(classification_counts.items(), key=lambda kv: -kv[1]):
        pct = 100 * n / len(comps_both) if comps_both else 0
        print(f"  {n:>5,}  ({pct:>4.1f}%)  {BID_TYPES[bt]['label']}")

    # FTS-only run for comparison
    print(f"\n[2/2] Loading FTS-only competitions for comparison...")
    comps_fts = fetch_competitions(c, "fts", since)

    cells_fts, spend_fts, _ = compute_industry_spend(comps_fts)
    cells_both, spend_both, _ = compute_industry_spend(comps_both)

    report("FTS only — bid-type-aware", cells_fts, spend_fts, len(comps_fts))
    report("FTS + Contracts Finder COMBINED — bid-type-aware",
           cells_both, spend_both, len(comps_both))

    # Headline comparison vs original models
    print(f"\n{'='*78}")
    print("  HEADLINE COMPARISON ACROSS MODELS")
    print(f"{'='*78}")
    print(f"  {'Model':<60}  {'Spend':>10}  {'Sunk':>10}")
    print(f"  {'Original 2026-04-23 (FTS, value-tier-only)':<60}  {'£3.93bn':>10}  {'£2.00bn':>10}")
    print(f"  {'Today re-run (FTS, value-tier-only)':<60}  {'£3.57bn':>10}  {'£2.39bn':>10}")
    print(f"  {'Today re-run (FTS+CF, value-tier-only)':<60}  {'£4.96bn':>10}  {'£3.32bn':>10}")
    sunk_fts = sum(c['spend'] * (1 - BID_TYPES[bt]['win_rate']) for (t,bt),c in cells_fts.items())
    sunk_both = sum(c['spend'] * (1 - BID_TYPES[bt]['win_rate']) for (t,bt),c in cells_both.items())
    print(f"  {'NEW: Bid-type-aware (FTS only)':<60}  {fmt_money(spend_fts):>10}  {fmt_money(sunk_fts):>10}")
    print(f"  {'NEW: Bid-type-aware (FTS + CF combined)':<60}  {fmt_money(spend_both):>10}  {fmt_money(sunk_both):>10}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
