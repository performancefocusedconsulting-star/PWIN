"""
PWIN Competitive Intelligence — Query Library
==============================================
Named queries for surfacing buyer profiles, supplier intelligence,
PWIN signals, and expiry pipelines.

Usage:
    python queries.py summary
    python queries.py buyer "Ministry of Defence"
    python queries.py supplier "Serco"
    python queries.py expiring --days 180 --value 500000
    python queries.py pipeline
    python queries.py awards --value 1000000
    python queries.py pwin --buyer "Home Office"
    python queries.py cpv 79410000
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Optional

# Windows cp1252 stdout chokes on the Unicode glyphs we use in the
# behaviour profile output. Force UTF-8 (no-op on POSIX systems).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"


def get_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Run agent/ingest.py first.")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def fmt_gbp(v) -> str:
    if v is None:
        return "—"
    if v >= 1_000_000:
        return f"£{v/1_000_000:.1f}m"
    if v >= 1_000:
        return f"£{v/1_000:.0f}k"
    return f"£{v:.0f}"


def print_table(rows, headers: list, col_widths: list):
    header_line = "  ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("—" * len(header_line))
    for row in rows:
        print("  ".join(str(v or "—")[:w].ljust(w) for v, w in zip(row, col_widths)))


# ──────────────────────────────────────────────────────────────────────────
# DATABASE SUMMARY
# ──────────────────────────────────────────────────────────────────────────

def db_summary():
    conn = get_db()
    print("\nDatabase summary")
    print("=" * 60)
    for table in ["buyers", "suppliers", "notices", "lots", "awards",
                  "award_suppliers", "cpv_codes", "planning_notices"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<25} {count:>10,}")

    # Per-source breakdown (present only once data_source column exists)
    try:
        print(f"\n  {'Source':<10}  {'Notices':>10}  {'Awards':>10}  "
              f"{'Buyers':>10}  {'Suppliers':>10}")
        print("  " + "-" * 56)
        for src in ("fts", "cf"):
            n = conn.execute(
                "SELECT COUNT(*) FROM notices WHERE COALESCE(data_source,'fts')=?", (src,)
            ).fetchone()[0]
            a = conn.execute(
                "SELECT COUNT(*) FROM awards WHERE COALESCE(data_source,'fts')=?", (src,)
            ).fetchone()[0]
            b = conn.execute(
                "SELECT COUNT(*) FROM buyers WHERE COALESCE(data_source,'fts')=?", (src,)
            ).fetchone()[0]
            s = conn.execute(
                "SELECT COUNT(*) FROM suppliers WHERE COALESCE(data_source,'fts')=?", (src,)
            ).fetchone()[0]
            print(f"  {src:<10}  {n:>10,}  {a:>10,}  {b:>10,}  {s:>10,}")
    except Exception:
        pass  # data_source column not yet present on older DBs

    cursor = conn.execute(
        "SELECT value FROM ingest_state WHERE key='last_cursor'"
    ).fetchone()
    cf_cur = conn.execute(
        "SELECT value FROM ingest_state WHERE key='cf_last_date'"
    ).fetchone()
    print(f"\n  FTS cursor  : {cursor['value'] if cursor and cursor['value'] else 'none'}")
    print(f"  CF cursor   : {cf_cur['value'] if cf_cur and cf_cur['value'] else 'none'}")

    # Value stats (exclude flagged outliers — see schema comment on awards.value_quality)
    val = conn.execute("""
        SELECT SUM(value_amount_gross), AVG(value_amount_gross), MAX(value_amount_gross)
        FROM awards WHERE value_amount_gross IS NOT NULL AND value_quality IS NULL
    """).fetchone()
    if val[0]:
        print(f"\n  Total award value indexed : {fmt_gbp(val[0])}")
        print(f"  Avg award value           : {fmt_gbp(val[1])}")
        print(f"  Largest single award      : {fmt_gbp(val[2])}")

    # Top CPV codes
    top_cpv = conn.execute("""
        SELECT code, description, COUNT(*) AS cnt
        FROM cpv_codes GROUP BY code ORDER BY cnt DESC LIMIT 10
    """).fetchall()
    if top_cpv:
        print(f"\n  Top CPV codes:")
        for r in top_cpv:
            print(f"    {r['code']}  {r['description'][:40]:<40}  ({r['cnt']} notices)")

    conn.close()


# ──────────────────────────────────────────────────────────────────────────
# BUYER PROFILE
# ──────────────────────────────────────────────────────────────────────────

def buyer_profile(name_query: str, limit: int = 50):
    conn = get_db()

    buyers = conn.execute("""
        SELECT id, name, org_type, region_code FROM buyers
        WHERE LOWER(name) LIKE LOWER(?)
        ORDER BY name LIMIT 10
    """, (f"%{name_query}%",)).fetchall()

    if not buyers:
        print(f"No buyers found matching '{name_query}'")
        return

    for buyer in buyers:
        print(f"\n{'='*70}")
        print(f"BUYER: {buyer['name']}")
        print(f"Type : {buyer['org_type'] or '—'}   Region: {buyer['region_code'] or '—'}")

        # Summary stats
        stats = conn.execute("""
            SELECT
                COUNT(DISTINCT a.id)        AS total_awards,
                COUNT(DISTINCT n.ocid)      AS total_notices,
                SUM(a.value_amount_gross)   AS total_spend,
                AVG(a.value_amount_gross)   AS avg_value,
                MAX(a.value_amount_gross)   AS max_value,
                AVG(n.total_bids)           AS avg_bids
            FROM awards a
            JOIN notices n ON a.ocid = n.ocid
            WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
              AND a.value_quality IS NULL
        """, (buyer["id"],)).fetchone()

        if stats["total_awards"]:
            print(f"\nSummary")
            print(f"  Notices        : {stats['total_notices']}")
            print(f"  Awards         : {stats['total_awards']}")
            print(f"  Total spend    : {fmt_gbp(stats['total_spend'])}")
            print(f"  Avg award      : {fmt_gbp(stats['avg_value'])}")
            print(f"  Largest award  : {fmt_gbp(stats['max_value'])}")
            print(f"  Avg bids/tender: {round(stats['avg_bids'], 1) if stats['avg_bids'] else '—'}")

        # Procurement method breakdown
        methods = conn.execute("""
            SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
            FROM awards a JOIN notices n ON a.ocid = n.ocid
            WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
            GROUP BY n.procurement_method ORDER BY cnt DESC
        """, (buyer["id"],)).fetchall()
        if methods:
            print(f"\n  Procurement methods:")
            for m in methods:
                print(f"    {m['procurement_method'] or 'unknown':<15} {m['cnt']}")

        # Top suppliers — rolled up by canonical entity
        top_suppliers = conn.execute("""
            SELECT canonical_name AS name,
                   COUNT(DISTINCT award_id) AS wins,
                   SUM(value_amount_gross)  AS total_value
            FROM v_canonical_supplier_wins
            WHERE buyer_id = ? AND value_quality IS NULL
            GROUP BY canonical_id
            ORDER BY wins DESC, total_value DESC LIMIT 15
        """, (buyer["id"],)).fetchall()

        if top_suppliers:
            print(f"\nTop suppliers")
            print_table(
                [(r["name"], r["wins"], fmt_gbp(r["total_value"])) for r in top_suppliers],
                ["Supplier", "Wins", "Total value"],
                [45, 6, 14],
            )

        # Recent awards
        recent = conn.execute("""
            SELECT n.title, a.value_amount_gross, n.procurement_method,
                   GROUP_CONCAT(DISTINCT s.name) AS suppliers,
                   a.contract_end_date, a.award_date
            FROM awards a
            JOIN notices n ON a.ocid = n.ocid
            LEFT JOIN award_suppliers asup ON a.id = asup.award_id
            LEFT JOIN suppliers s ON asup.supplier_id = s.id
            WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
            GROUP BY a.id
            ORDER BY a.award_date DESC NULLS LAST
            LIMIT ?
        """, (buyer["id"], limit)).fetchall()

        if recent:
            print(f"\nAward history (most recent {len(recent)})")
            print_table(
                [(r["title"], fmt_gbp(r["value_amount_gross"]),
                  r["procurement_method"] or "—",
                  (r["suppliers"] or "—")[:35],
                  (r["contract_end_date"] or "—")[:10])
                 for r in recent],
                ["Title", "Value", "Method", "Supplier(s)", "Expires"],
                [30, 10, 10, 35, 12],
            )

    conn.close()


# ──────────────────────────────────────────────────────────────────────────
# SUPPLIER INTELLIGENCE
# ──────────────────────────────────────────────────────────────────────────

def supplier_profile(name_query: str, limit: int = 50):
    """Supplier profile, aggregated by canonical entity.

    Matches canonical_name OR any raw member name, then rolls all awards
    belonging to the canonical entity into one profile. So a search for
    'Serco' returns one canonical Serco with every variant's awards
    combined, not a separate row per name variant.
    """
    conn = get_db()

    canonicals = conn.execute("""
        SELECT DISTINCT canonical_id, canonical_name, canonical_ch_numbers,
                        canonical_distinct_ch_count, canonical_member_count
        FROM v_canonical_supplier_wins
        WHERE LOWER(canonical_name) LIKE LOWER(?)
           OR LOWER(raw_supplier_name) LIKE LOWER(?)
        ORDER BY canonical_member_count DESC NULLS LAST, canonical_name
        LIMIT 10
    """, (f"%{name_query}%", f"%{name_query}%")).fetchall()

    if not canonicals:
        print(f"No suppliers found matching '{name_query}'")
        return

    for sup in canonicals:
        print(f"\n{'='*70}")
        print(f"CANONICAL SUPPLIER: {sup['canonical_name']}")
        ch_list = sup['canonical_ch_numbers'] or '—'
        member = sup['canonical_member_count']
        if member and member > 1:
            print(f"Rolls up {member} raw supplier rows  "
                  f"|  CH numbers: {ch_list}")
        else:
            print(f"CH numbers: {ch_list}")

        stats = conn.execute("""
            SELECT
                COUNT(DISTINCT award_id)      AS total_wins,
                SUM(value_amount_gross)       AS total_value,
                AVG(value_amount_gross)       AS avg_value,
                MAX(value_amount_gross)       AS max_value,
                MIN(award_date)               AS first_win,
                MAX(award_date)               AS last_win
            FROM v_canonical_supplier_wins
            WHERE canonical_id = ? AND value_quality IS NULL
        """, (sup["canonical_id"],)).fetchone()

        if stats["total_wins"]:
            print(f"\nSummary")
            print(f"  Total awards     : {stats['total_wins']}")
            print(f"  Total value      : {fmt_gbp(stats['total_value'])}")
            print(f"  Avg award        : {fmt_gbp(stats['avg_value'])}")
            print(f"  Largest award    : {fmt_gbp(stats['max_value'])}")
            print(f"  First win        : {(stats['first_win'] or '—')[:10]}")
            print(f"  Last win         : {(stats['last_win'] or '—')[:10]}")

        # Buyer relationships — canonical buyer side would be nice too but
        # for v1 we keep buyer as raw b.name; canonical_buyers join is a
        # follow-up once the buyer canonical layer is in the playbook.
        buyers = conn.execute("""
            SELECT buyer_name, COUNT(DISTINCT award_id) AS awards,
                   SUM(value_amount_gross) AS total_value,
                   MAX(contract_end_date) AS latest_expiry
            FROM v_canonical_supplier_wins
            WHERE canonical_id = ? AND value_quality IS NULL
            GROUP BY buyer_id
            ORDER BY awards DESC, total_value DESC LIMIT 15
        """, (sup["canonical_id"],)).fetchall()

        if buyers:
            print(f"\nBuyer relationships")
            print_table(
                [(r["buyer_name"], r["awards"], fmt_gbp(r["total_value"]),
                  (r["latest_expiry"] or "—")[:10])
                 for r in buyers],
                ["Buyer", "Awards", "Total value", "Latest expiry"],
                [40, 7, 14, 14],
            )

        # Active contracts (incumbencies) — dedupe: when a canonical rolls
        # up multiple raw rows all tied to the same award, the view returns
        # N rows for one award. GROUP BY award_id collapses them.
        active = conn.execute("""
            SELECT title, buyer_name, value_amount_gross,
                   contract_end_date, contract_max_extend
            FROM v_canonical_supplier_wins
            WHERE canonical_id = ?
              AND contract_end_date > datetime('now')
            GROUP BY award_id
            ORDER BY contract_end_date ASC LIMIT 20
        """, (sup["canonical_id"],)).fetchall()

        if active:
            print(f"\nActive contracts (incumbent positions)")
            print_table(
                [(r["title"], r["buyer_name"], fmt_gbp(r["value_amount_gross"]),
                  (r["contract_end_date"] or "—")[:10],
                  (r["contract_max_extend"] or "—")[:10])
                 for r in active],
                ["Title", "Buyer", "Value", "Expires", "Max extend"],
                [28, 28, 10, 12, 12],
            )

    conn.close()


# ──────────────────────────────────────────────────────────────────────────
# EXPIRY PIPELINE
# ──────────────────────────────────────────────────────────────────────────

def expiring_contracts(days: int = 365, min_value: Optional[float] = None,
                       buyer_query: Optional[str] = None, category: Optional[str] = None):
    conn = get_db()

    sql = "SELECT * FROM v_expiring_contracts WHERE days_to_expiry <= ?"
    params = [days]

    if min_value:
        sql += " AND value_amount_gross >= ?"
        params.append(min_value)
    if buyer_query:
        sql += " AND LOWER(buyer_name) LIKE LOWER(?)"
        params.append(f"%{buyer_query}%")
    if category:
        sql += " AND LOWER(main_category) LIKE LOWER(?)"
        params.append(f"%{category}%")

    sql += " ORDER BY days_to_expiry ASC LIMIT 100"
    rows = conn.execute(sql, params).fetchall()

    print(f"\nContracts expiring within {days} days")
    if min_value:
        print(f"Minimum value: {fmt_gbp(min_value)}")
    print(f"Results: {len(rows)}\n")

    print_table(
        [(r["buyer_name"], r["supplier_names"] or "Unknown",
          fmt_gbp(r["value_amount_gross"]), r["days_to_expiry"],
          r["procurement_method"] or "—",
          (r["contract_end_date"] or "—")[:10])
         for r in rows],
        ["Buyer", "Supplier(s)", "Value", "Days", "Method", "Expires"],
        [28, 30, 10, 5, 10, 12],
    )
    conn.close()


# ──────────────────────────────────────────────────────────────────────────
# FORWARD PIPELINE
# ──────────────────────────────────────────────────────────────────────────

def forward_pipeline(buyer_query: Optional[str] = None):
    conn = get_db()

    sql = """
        SELECT p.*, b.name AS buyer_name, b.org_type
        FROM planning_notices p
        JOIN buyers b ON p.buyer_id = b.id
        WHERE 1=1
    """
    params = []

    if buyer_query:
        sql += " AND LOWER(b.name) LIKE LOWER(?)"
        params.append(f"%{buyer_query}%")

    sql += """
        ORDER BY
            CASE WHEN p.future_notice_date IS NOT NULL
                 THEN p.future_notice_date
                 ELSE p.engagement_deadline END ASC
        LIMIT 100
    """
    rows = conn.execute(sql, params).fetchall()

    print(f"\nForward pipeline — planning and market engagement notices")
    print(f"Results: {len(rows)}\n")

    print_table(
        [(r["buyer_name"], (r["title"] or "—")[:40],
          fmt_gbp(r["estimated_value"]),
          (r["engagement_deadline"] or "—")[:10],
          (r["future_notice_date"] or "—")[:10])
         for r in rows],
        ["Buyer", "Title", "Est. value", "Engage by", "Tender due"],
        [28, 40, 12, 12, 12],
    )
    conn.close()


# ──────────────────────────────────────────────────────────────────────────
# AWARDS ABOVE THRESHOLD
# ──────────────────────────────────────────────────────────────────────────

def awards_above_value(min_value: float = 1_000_000, buyer_query: Optional[str] = None,
                       supplier_query: Optional[str] = None, limit: int = 100):
    conn = get_db()

    sql = """
        SELECT n.title, b.name AS buyer,
               GROUP_CONCAT(DISTINCT s.name) AS suppliers,
               a.value_amount_gross, n.procurement_method,
               a.contract_start_date, a.contract_end_date,
               n.total_bids, a.award_date
        FROM awards a
        JOIN notices n ON a.ocid = n.ocid
        JOIN buyers b ON n.buyer_id = b.id
        LEFT JOIN award_suppliers asup ON a.id = asup.award_id
        LEFT JOIN suppliers s ON asup.supplier_id = s.id
        WHERE a.value_amount_gross >= ?
    """
    params = [min_value]

    if buyer_query:
        sql += " AND LOWER(b.name) LIKE LOWER(?)"
        params.append(f"%{buyer_query}%")
    if supplier_query:
        sql += " AND LOWER(s.name) LIKE LOWER(?)"
        params.append(f"%{supplier_query}%")

    sql += " GROUP BY a.id ORDER BY a.value_amount_gross DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()

    print(f"\nAwards above {fmt_gbp(min_value)}")
    print(f"Results: {len(rows)}\n")

    print_table(
        [(r["title"], r["buyer"], (r["suppliers"] or "—")[:25],
          fmt_gbp(r["value_amount_gross"]),
          (r["contract_end_date"] or "—")[:10])
         for r in rows],
        ["Title", "Buyer", "Supplier(s)", "Value", "Expires"],
        [28, 25, 25, 10, 12],
    )
    conn.close()


# ──────────────────────────────────────────────────────────────────────────
# PWIN SIGNALS
# ──────────────────────────────────────────────────────────────────────────

def pwin_signals(buyer_query: Optional[str] = None, category: Optional[str] = None):
    conn = get_db()

    sql = "SELECT * FROM v_pwin_signals WHERE 1=1"
    params = []

    if buyer_query:
        sql += " AND LOWER(buyer_name) LIKE LOWER(?)"
        params.append(f"%{buyer_query}%")
    if category:
        sql += " AND LOWER(main_category) LIKE LOWER(?)"
        params.append(f"%{category}%")

    sql += " LIMIT 50"
    rows = conn.execute(sql, params).fetchall()

    print(f"\nPWIN signals — competition analysis")
    print(f"Results: {len(rows)}\n")

    print_table(
        [(r["buyer_name"], r["main_category"] or "—",
          r["awards_count"],
          round(r["avg_bids_per_tender"], 1) if r["avg_bids_per_tender"] else "—",
          fmt_gbp(r["avg_award_value"]),
          r["open_awards"], r["limited_awards"], r["direct_awards"])
         for r in rows],
        ["Buyer", "Category", "Awards", "Avg bids", "Avg value", "Open", "Limited", "Direct"],
        [30, 10, 7, 9, 11, 6, 8, 7],
    )
    conn.close()


# ──────────────────────────────────────────────────────────────────────────
# CPV CODE SEARCH
# ──────────────────────────────────────────────────────────────────────────

def cpv_search(code_query: str):
    conn = get_db()

    rows = conn.execute("""
        SELECT c.code, c.description, n.title, b.name AS buyer,
               n.procurement_method, n.tender_status,
               (SELECT SUM(a.value_amount_gross) FROM awards a WHERE a.ocid = n.ocid AND a.value_quality IS NULL) AS total_value
        FROM cpv_codes c
        JOIN notices n ON c.ocid = n.ocid
        JOIN buyers b ON n.buyer_id = b.id
        WHERE c.code LIKE ?
        ORDER BY n.published_date DESC
        LIMIT 50
    """, (f"{code_query}%",)).fetchall()

    print(f"\nNotices matching CPV {code_query}*")
    print(f"Results: {len(rows)}\n")

    print_table(
        [(r["code"], r["buyer"], r["title"],
          fmt_gbp(r["total_value"]),
          r["procurement_method"] or "—")
         for r in rows],
        ["CPV", "Buyer", "Title", "Value", "Method"],
        [10, 28, 30, 10, 10],
    )
    conn.close()


# ──────────────────────────────────────────────────────────────────────────
# BUYER BEHAVIOUR ANALYTICS (v1) — see docs/buyer-behaviour-analytics-v1.md
# ──────────────────────────────────────────────────────────────────────────
#
# A behavioural intelligence profile for one buyer. Powers the empirical
# Probability of Going Out (PGO) figure consumed by Win Strategy, Verdict,
# and the future paid Qualify tier.
#
# Pipeline:
#   1. resolve buyer name → canonical entity → set of raw buyers.id rows
#      (across both Find a Tender and Contracts Finder).
#   2. compute per-CPV-division dormant thresholds from the whole database.
#   3. classify each in-window notice into an outcome bucket.
#   4. emit ten sections plus a one-line PGO summary.
#
# Caveats baked in:
#   - Contracts Finder rows have no cancellation marker, so cancellation
#     metrics are FTS-only with the FTS share clearly disclosed.
#   - Procurement-method fields are essentially FTS-only — disclose the same.
#   - Amendment behaviour is not in v1 (data not captured in current schema).
#   - Incumbent-distress flag fires only on ch_status='dissolved' for now.
#   - Peer-buyer comparison uses canonical_buyers.type only (region is
#     unpopulated on most rows).

# CPV first-2-digit "division" labels — friendly names for the most-used
# divisions. Anything not in this map prints as "CPV 4X" with the digits.
CPV_DIVISION_LABELS = {
    "03": "Agriculture / forestry",
    "09": "Petroleum / fuels",
    "14": "Mining / minerals",
    "15": "Food / beverages",
    "16": "Agricultural machinery",
    "18": "Clothing / footwear",
    "19": "Leather / textiles",
    "22": "Printed matter",
    "24": "Chemicals",
    "30": "Office / IT equipment",
    "31": "Electrical / electronic",
    "32": "Radio / TV / comms equipment",
    "33": "Medical / pharma equipment",
    "34": "Transport equipment",
    "35": "Security / defence equipment",
    "37": "Sports / musical / arts goods",
    "38": "Laboratory / measuring",
    "39": "Furniture",
    "41": "Water utility",
    "42": "Industrial machinery",
    "43": "Mining / quarrying machinery",
    "44": "Construction materials",
    "45": "Construction works",
    "48": "Software packages",
    "50": "Repair / maintenance",
    "51": "Installation services",
    "55": "Hotel / catering",
    "60": "Transport services",
    "63": "Supporting transport / travel",
    "64": "Postal / telecoms services",
    "65": "Public utilities",
    "66": "Financial / insurance services",
    "70": "Real estate services",
    "71": "Architectural / engineering",
    "72": "IT services",
    "73": "Research / development",
    "75": "Public administration",
    "76": "Oil / gas services",
    "77": "Agricultural services",
    "79": "Business / consultancy services",
    "80": "Education / training",
    "85": "Health / social care",
    "90": "Sewage / waste / cleaning",
    "92": "Recreational / cultural / sport",
    "98": "Other community / social services",
}


def _cpv_division_label(div):
    if not div:
        return "Uncategorised"
    return f"CPV {div} — {CPV_DIVISION_LABELS.get(div, 'Other')}"


def _fmt_pct(num, denom, places=0):
    if not denom:
        return "—"
    return f"{(num * 100.0 / denom):.{places}f}%"


def _resolve_buyer_canonical(conn, name_query):
    """Resolve a free-text buyer name to a canonical buyer entity and the
    full set of raw buyers.id rows that map to it (across FTS and CF).

    Resolution waterfall:
      1. exact alias_lower match (e.g. "ministry of defence")
      2. abbreviation match in canonical_buyers.abbreviation
      3. LIKE match against canonical_name
      4. fragmented fallback — LIKE match against raw buyers.name with a warning

    Returns a dict with canonical_id, canonical_name, canonical_type,
    raw_buyer_ids (list of strings), and fragmented (bool).
    """
    q = name_query.strip()
    qlow = q.lower()

    # Path 1 — exact alias match
    row = conn.execute(
        "SELECT canonical_id FROM canonical_buyer_aliases WHERE alias_lower = ?",
        (qlow,),
    ).fetchone()

    canonical_id = row["canonical_id"] if row else None

    # Path 2 — abbreviation
    if not canonical_id:
        row = conn.execute(
            "SELECT canonical_id FROM canonical_buyers "
            "WHERE LOWER(abbreviation) = ? LIMIT 1",
            (qlow,),
        ).fetchone()
        canonical_id = row["canonical_id"] if row else None

    # Path 3 — canonical name LIKE
    if not canonical_id:
        rows = conn.execute(
            "SELECT canonical_id, canonical_name FROM canonical_buyers "
            "WHERE LOWER(canonical_name) LIKE ? "
            "ORDER BY LENGTH(canonical_name) ASC LIMIT 5",
            (f"%{qlow}%",),
        ).fetchall()
        if len(rows) == 1:
            canonical_id = rows[0]["canonical_id"]
        elif len(rows) > 1:
            print(f"\nMultiple canonical buyers match '{q}'. Be more specific:")
            for r in rows:
                print(f"  - {r['canonical_name']}")
            return None

    if canonical_id:
        canon = conn.execute(
            "SELECT canonical_id, canonical_name, type FROM canonical_buyers "
            "WHERE canonical_id = ?",
            (canonical_id,),
        ).fetchone()

        # All raw buyers.id whose name matches any alias for this canonical
        ids = [r["id"] for r in conn.execute("""
            SELECT DISTINCT b.id
            FROM buyers b
            JOIN canonical_buyer_aliases a
              ON LOWER(TRIM(b.name)) = a.alias_lower
            WHERE a.canonical_id = ?
        """, (canonical_id,))]

        return {
            "canonical_id":    canon["canonical_id"],
            "canonical_name":  canon["canonical_name"],
            "canonical_type":  canon["type"],
            "raw_buyer_ids":   ids,
            "fragmented":      False,
        }

    # Path 4 — fragmented fallback
    raw_rows = conn.execute(
        "SELECT id, name FROM buyers WHERE LOWER(name) LIKE ? ORDER BY name LIMIT 200",
        (f"%{qlow}%",),
    ).fetchall()
    if not raw_rows:
        return None

    return {
        "canonical_id":    None,
        "canonical_name":  raw_rows[0]["name"],
        "canonical_type":  None,
        "raw_buyer_ids":   [r["id"] for r in raw_rows],
        "fragmented":      True,
    }


def _stage_buyer_id_temp_table(conn, buyer_ids):
    """Drop the buyer_ids into a session-temp table so multi-section
    queries can JOIN against it instead of expanding a giant IN list
    every time. Returns the temp-table name."""
    conn.execute("DROP TABLE IF EXISTS _bb_ids")
    conn.execute("CREATE TEMP TABLE _bb_ids (id TEXT PRIMARY KEY)")
    conn.executemany("INSERT OR IGNORE INTO _bb_ids (id) VALUES (?)",
                     [(b,) for b in buyer_ids])
    return "_bb_ids"


CPV_P95_CACHE = Path(__file__).parent.parent / "db" / "_cpv_p95_cache.json"


def _compute_cpv_division_p95(conn, min_sample=50):
    """Return {cpv_division_2_digit: p95_days} for notice→first-award
    timelines, computed across the entire database. Used as the dormant
    threshold per category. Falls back to overall P95 for divisions
    with too few awards.

    Cached for one day to a JSON file beside the database, since the
    underlying distribution barely shifts day-to-day on 478k+ notices.
    """
    import time as _time
    if CPV_P95_CACHE.exists():
        age = _time.time() - CPV_P95_CACHE.stat().st_mtime
        if age < 86400:  # 24h
            try:
                return json.loads(CPV_P95_CACHE.read_text(encoding="utf-8"))
            except Exception:
                pass
    # First award per OCID (any source)
    rows = conn.execute("""
        WITH first_award AS (
            SELECT n.ocid,
                   n.published_date,
                   MIN(COALESCE(a.award_date, a.date_signed,
                                a.contract_start_date))         AS first_aw
            FROM notices n
            JOIN awards a ON a.ocid = n.ocid
            WHERE a.status IN ('active', 'pending')
              AND n.published_date IS NOT NULL
            GROUP BY n.ocid
        )
        SELECT SUBSTR(c.code, 1, 2)  AS div,
               CAST(julianday(fa.first_aw) - julianday(fa.published_date) AS INTEGER) AS days
        FROM first_award fa
        JOIN cpv_codes c ON c.ocid = fa.ocid
        WHERE fa.first_aw IS NOT NULL
          AND fa.first_aw > fa.published_date
    """).fetchall()

    # Group by division
    bucket = {}
    overall = []
    for r in rows:
        d = r["days"]
        if d is None or d < 0 or d > 2000:  # silly outliers
            continue
        bucket.setdefault(r["div"], []).append(d)
        overall.append(d)

    def p95(vals):
        if not vals:
            return None
        s = sorted(vals)
        idx = int(0.95 * (len(s) - 1))
        return s[idx]

    overall_p95 = p95(overall) or 365
    out = {}
    for div, vals in bucket.items():
        if len(vals) >= min_sample:
            out[div] = p95(vals)
        else:
            out[div] = overall_p95
    out["_overall"] = overall_p95
    try:
        CPV_P95_CACHE.write_text(json.dumps(out), encoding="utf-8")
    except Exception:
        pass
    return out


def _section_volume_trend(conn, years):
    """1. Volume and trend — published notices and awards per year by source."""
    print(f"\n1. Volume and trend (last {years} years)")
    print("-" * 60)

    rows = conn.execute(f"""
        SELECT CAST(STRFTIME('%Y', n.published_date) AS INTEGER)  AS yr,
               COALESCE(n.data_source, 'fts')                     AS src,
               COUNT(*)                                           AS notices
        FROM notices n
        JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE n.published_date >= datetime('now', '-{years} years')
        GROUP BY yr, src
        ORDER BY yr ASC, src ASC
    """).fetchall()

    if not rows:
        print("  No notices in window.")
        return {"total_notices": 0}

    by_year = {}
    by_year_src = {}
    for r in rows:
        by_year[r["yr"]] = by_year.get(r["yr"], 0) + r["notices"]
        by_year_src[(r["yr"], r["src"])] = r["notices"]

    award_rows = conn.execute(f"""
        SELECT CAST(STRFTIME('%Y', a.award_date) AS INTEGER) AS yr,
               COUNT(DISTINCT a.id)                          AS awards
        FROM awards a
        JOIN notices n ON a.ocid = n.ocid
        JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE a.award_date >= datetime('now', '-{years} years')
          AND a.status IN ('active', 'pending')
        GROUP BY yr ORDER BY yr ASC
    """).fetchall()
    awards_by_year = {r["yr"]: r["awards"] for r in award_rows if r["yr"]}

    print(f"  {'Year':<6} {'Notices':>10} {'(FTS)':>8} {'(CF)':>8} {'Awards':>9}")
    years_sorted = sorted(by_year.keys())
    total = total_fts = total_cf = total_aw = 0
    for y in years_sorted:
        if not y:
            continue
        n_total = by_year[y]
        n_fts   = by_year_src.get((y, "fts"), 0)
        n_cf    = by_year_src.get((y, "cf"),  0)
        n_aw    = awards_by_year.get(y, 0)
        total += n_total; total_fts += n_fts; total_cf += n_cf; total_aw += n_aw
        print(f"  {y:<6} {n_total:>10,} {n_fts:>8,} {n_cf:>8,} {n_aw:>9,}")

    print(f"  {'─'*6} {'─'*10} {'─'*8} {'─'*8} {'─'*9}")
    print(f"  {'Total':<6} {total:>10,} {total_fts:>8,} {total_cf:>8,} {total_aw:>9,}")

    # Year-on-year direction — last full year vs prior full year
    if len(years_sorted) >= 3:
        recent = by_year[years_sorted[-2]]
        prior  = by_year[years_sorted[-3]]
        if prior:
            delta = (recent - prior) * 100.0 / prior
            direction = "growing" if delta > 10 else "shrinking" if delta < -10 else "steady"
            print(f"\n  Trend: {direction} ({delta:+.0f}% YoY between "
                  f"{years_sorted[-3]} and {years_sorted[-2]})")

    return {"total_notices": total, "fts_notices": total_fts,
            "cf_notices": total_cf, "total_awards": total_aw}


def _section_method_mix(conn, years):
    """6. Procurement method mix — FTS-only because CF doesn't populate
    procurement_method or procurement_method_detail."""
    print(f"\n2. Procurement method mix (last {years} years, FTS only)")
    print("-" * 60)

    rows = conn.execute(f"""
        SELECT n.procurement_method               AS method,
               n.procurement_method_detail        AS detail,
               COUNT(*)                           AS notices
        FROM notices n
        JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE COALESCE(n.data_source, 'fts') = 'fts'
          AND n.published_date >= datetime('now', '-{years} years')
        GROUP BY method, detail
    """).fetchall()

    fts_total = sum(r["notices"] for r in rows)
    if not fts_total:
        print("  No FTS notices in window.")
        return

    # Roll up by top-level method
    by_method = {}
    framework_callcoff = 0
    for r in rows:
        m = r["method"] or "unknown"
        d = (r["detail"] or "").lower()
        if "framework" in d or "call-off" in d or "call off" in d:
            framework_callcoff += r["notices"]
            continue
        by_method[m] = by_method.get(m, 0) + r["notices"]

    if framework_callcoff:
        by_method["framework call-off"] = framework_callcoff

    method_label = {
        "open":              "Open competition",
        "limited":           "Limited (restricted / negotiated)",
        "selective":         "Selective",
        "direct":            "Direct award",
        "framework call-off":"Framework call-off",
        "unknown":           "Unknown / not stated",
    }

    print(f"  {'Method':<35} {'Count':>8} {'Share':>7}")
    for m, n in sorted(by_method.items(), key=lambda x: -x[1]):
        print(f"  {method_label.get(m, m):<35} {n:>8,} "
              f"{_fmt_pct(n, fts_total):>7}")

    cf_count = conn.execute(f"""
        SELECT COUNT(*) FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE n.data_source = 'cf'
          AND n.published_date >= datetime('now', '-{years} years')
    """).fetchone()[0]
    if cf_count:
        print(f"\n  ({cf_count:,} additional Contracts Finder notices "
              f"have no method recorded.)")


def _section_competition(conn, years):
    """7. Competition intensity — average bid count overall and trend."""
    print(f"\n3. Competition intensity (last {years} years)")
    print("-" * 60)

    overall = conn.execute(f"""
        SELECT AVG(n.total_bids)             AS avg_bids,
               COUNT(n.total_bids)           AS bid_n
        FROM notices n
        JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE n.published_date >= datetime('now', '-{years} years')
          AND n.total_bids IS NOT NULL
          AND n.total_bids > 0
    """).fetchone()

    if not overall["bid_n"]:
        print("  No bid-count data on this buyer's notices in window.")
        return

    print(f"  Average bidders per tender : {overall['avg_bids']:.1f}  "
          f"(n={overall['bid_n']:,} notices with bid count recorded)")

    # Yearly trend
    yearly = conn.execute(f"""
        SELECT CAST(STRFTIME('%Y', n.published_date) AS INTEGER) AS yr,
               AVG(n.total_bids) AS avg_bids,
               COUNT(*)          AS n
        FROM notices n
        JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE n.published_date >= datetime('now', '-{years} years')
          AND n.total_bids > 0
        GROUP BY yr ORDER BY yr ASC
    """).fetchall()

    if yearly:
        print(f"\n  {'Year':<6} {'Avg bidders':>12} {'Notices':>9}")
        for r in yearly:
            if not r["yr"]:
                continue
            print(f"  {r['yr']:<6} {r['avg_bids']:>12.1f} {r['n']:>9,}")

        # Trend direction (last vs first)
        if len(yearly) >= 3 and yearly[0]["avg_bids"] and yearly[-1]["avg_bids"]:
            first = yearly[0]["avg_bids"]
            last  = yearly[-1]["avg_bids"]
            delta = (last - first) / first
            direction = ("rising" if delta > 0.15 else
                         "falling" if delta < -0.15 else "flat")
            print(f"\n  Direction: {direction} "
                  f"({first:.1f} → {last:.1f} avg bidders)")

    low_comp = conn.execute(f"""
        SELECT COUNT(*) AS n
        FROM notices n
        JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE n.published_date >= datetime('now', '-{years} years')
          AND n.total_bids IS NOT NULL
          AND n.total_bids < 3
          AND n.total_bids > 0
    """).fetchone()
    if low_comp["n"]:
        share_low = low_comp["n"] * 100.0 / overall["bid_n"]
        print(f"\n  Notices attracting fewer than 3 bidders: "
              f"{low_comp['n']:,} ({share_low:.0f}% of bid-recorded notices)")
        if share_low > 25:
            print(f"    → elevated 'no compliant bid' risk")


def _classify_outcomes(conn, years, cat_p95):
    """Classify each in-window notice for the staged buyer set into one
    of five outcome buckets. Returns a list of dicts with ocid, source,
    bucket, published_date, days_since_publish, cpv_div.

    Bucket precedence:
      1. Awarded               — has any award status active|pending
      2. Cancelled / withdrawn — FTS only (CF has no signal)
      3. No compliant bid      — tender_status='unsuccessful' OR all
                                 awards 'unsuccessful'
      4. Dormant               — published > P95(CPV division) + 90 days,
                                 no award, no cancellation
      5. In flight             — everything else
    """
    rows = conn.execute(f"""
        WITH buyer_notices AS (
            SELECT n.ocid, n.published_date, n.tender_status, n.latest_tag,
                   COALESCE(n.data_source, 'fts') AS src,
                   CAST(julianday('now') - julianday(n.published_date)
                        AS INTEGER) AS age_days
            FROM notices n
            JOIN _bb_ids b ON n.buyer_id = b.id
            WHERE n.published_date >= datetime('now', '-{years} years')
              AND n.published_date IS NOT NULL
        ),
        award_agg AS (
            SELECT a.ocid,
                   SUM(CASE WHEN a.status IN ('active','pending')
                            THEN 1 ELSE 0 END) AS awarded_n,
                   SUM(CASE WHEN a.status = 'unsuccessful'
                            THEN 1 ELSE 0 END) AS unsucc_n,
                   COUNT(*) AS total_aw
            FROM awards a
            WHERE a.ocid IN (SELECT ocid FROM buyer_notices)
            GROUP BY a.ocid
        ),
        cpv_first AS (
            SELECT c.ocid, MIN(SUBSTR(c.code, 1, 2)) AS cpv_div
            FROM cpv_codes c
            WHERE c.ocid IN (SELECT ocid FROM buyer_notices)
            GROUP BY c.ocid
        )
        SELECT bn.ocid, bn.src, bn.published_date,
               bn.tender_status, bn.latest_tag, bn.age_days,
               cf.cpv_div,
               COALESCE(aa.awarded_n, 0) AS awarded_n,
               COALESCE(aa.unsucc_n, 0)  AS unsucc_n,
               COALESCE(aa.total_aw, 0)  AS total_aw
        FROM buyer_notices bn
        LEFT JOIN award_agg aa ON aa.ocid = bn.ocid
        LEFT JOIN cpv_first cf ON cf.ocid = bn.ocid
    """).fetchall()

    out = []
    overall = cat_p95.get("_overall", 365)
    for r in rows:
        bucket = None

        if r["awarded_n"] > 0:
            bucket = "awarded"
        elif r["src"] == "fts" and (
            r["tender_status"] in ("cancelled", "withdrawn")
            or (r["latest_tag"] or "") == "tenderCancellation"
        ):
            bucket = "cancelled"
        elif (r["tender_status"] == "unsuccessful"
              or (r["total_aw"] > 0 and r["unsucc_n"] == r["total_aw"])):
            bucket = "no_compliant_bid"
        else:
            threshold = cat_p95.get(r["cpv_div"], overall) + 90
            if r["age_days"] is not None and r["age_days"] > threshold:
                bucket = "dormant"
            else:
                bucket = "in_flight"

        out.append({
            "ocid":     r["ocid"],
            "src":      r["src"],
            "bucket":   bucket,
            "cpv_div":  r["cpv_div"],
            "age_days": r["age_days"],
            "published_date": r["published_date"],
        })

    return out


def _section_outcome_mix(conn, years, cat_p95):
    """2. Outcome mix — the headline PGO input."""
    print(f"\n4. Outcome mix (last {years} years)")
    print("-" * 60)

    classified = _classify_outcomes(conn, years, cat_p95)
    if not classified:
        print("  No notices in window.")
        return classified

    total = len(classified)
    fts_total = sum(1 for c in classified if c["src"] == "fts")

    bucket_label = {
        "awarded":          "Awarded",
        "cancelled":        "Cancelled / withdrawn",
        "no_compliant_bid": "No compliant bid",
        "dormant":          "Dormant (effectively dead)",
        "in_flight":        "In flight (live)",
    }
    order = ["awarded", "cancelled", "no_compliant_bid",
             "dormant", "in_flight"]

    counts = {k: 0 for k in order}
    for c in classified:
        counts[c["bucket"]] += 1

    sample_size = total
    print(f"  Sample size            : {sample_size:,} published notices")
    if sample_size < 10:
        print(f"  ⚠ Sample too small for percentages — counts only.")
        for k in order:
            if counts[k]:
                print(f"  {bucket_label[k]:<32} {counts[k]:>5}")
        return classified

    if sample_size < 25:
        print(f"  Indicative only (sample n={sample_size}).")

    print(f"  {'Bucket':<32} {'Count':>7} {'Share':>7}")
    for k in order:
        n = counts[k]
        if k == "cancelled":
            denom = fts_total
            share = _fmt_pct(n, denom)
            print(f"  {bucket_label[k]:<32} {n:>7,} {share:>7}  "
                  f"(of {fts_total:,} FTS-tracked)")
        else:
            denom = total
            print(f"  {bucket_label[k]:<32} {n:>7,} {_fmt_pct(n, denom):>7}")

    closed = counts["awarded"] + counts["cancelled"] + counts["no_compliant_bid"] + counts["dormant"]
    if closed >= 25:
        award_rate_of_closed = counts["awarded"] * 100.0 / closed
        print(f"\n  Of closed notices ({closed:,}): "
              f"{award_rate_of_closed:.0f}% reached award.")

    return classified


def _section_timeline(conn, years):
    """3. Notice-to-award timeline distribution."""
    print(f"\n5. Notice-to-award timeline (last {years} years)")
    print("-" * 60)

    rows = conn.execute(f"""
        WITH first_aw AS (
            SELECT n.ocid, n.published_date,
                   MIN(COALESCE(a.award_date, a.date_signed,
                                a.contract_start_date)) AS first_aw_date
            FROM notices n
            JOIN _bb_ids b  ON n.buyer_id = b.id
            JOIN awards a   ON a.ocid = n.ocid
            WHERE n.published_date >= datetime('now', '-{years} years')
              AND a.status IN ('active', 'pending')
            GROUP BY n.ocid
        )
        SELECT CAST(julianday(first_aw_date) - julianday(published_date)
                    AS INTEGER) AS days
        FROM first_aw
        WHERE first_aw_date IS NOT NULL
          AND first_aw_date > published_date
    """).fetchall()

    days = [r["days"] for r in rows if r["days"] is not None and r["days"] >= 0
            and r["days"] < 1500]
    n = len(days)

    if n < 25:
        print(f"  Sample too small for percentile analysis "
              f"(only {n} notices have paired publication and award dates "
              f"in window).")
        print(f"  Many Contracts Finder rows lack a structured award date — "
              f"this is the main coverage gap.")
        return

    days.sort()

    def pct(p):
        return days[max(0, min(n - 1, int(p * (n - 1))))]

    print(f"  Awarded notices in window with paired dates: {n:,}")
    print(f"  Median (P50)        : {pct(0.50):>4} days")
    print(f"  IQR (P25–P75)       : {pct(0.25):>4}–{pct(0.75)} days")
    print(f"  P90 (slowest 10%)   : {pct(0.90):>4} days")
    print(f"  P95                 : {pct(0.95):>4} days")
    print(f"  Caveat: multi-lot tenders use the FIRST award date per OCID.")


def _section_category_footprint(conn, years, classified, cat_p95):
    """4. Category footprint — top 10 CPV divisions by volume,
    each with outcome mix and median timeline."""
    print(f"\n6. Category footprint (last {years} years)")
    print("-" * 60)

    by_div = {}
    for c in classified:
        d = c["cpv_div"] or "??"
        by_div.setdefault(d, {"total": 0, "awarded": 0, "cancelled": 0,
                              "ncb": 0, "dormant": 0, "in_flight": 0})
        by_div[d]["total"] += 1
        if c["bucket"] == "awarded":
            by_div[d]["awarded"] += 1
        elif c["bucket"] == "cancelled":
            by_div[d]["cancelled"] += 1
        elif c["bucket"] == "no_compliant_bid":
            by_div[d]["ncb"] += 1
        elif c["bucket"] == "dormant":
            by_div[d]["dormant"] += 1
        else:
            by_div[d]["in_flight"] += 1

    top = sorted(by_div.items(), key=lambda x: -x[1]["total"])[:10]
    if not top:
        print("  No category data.")
        return

    print(f"  {'Category':<40} {'N':>5} {'Award':>6} {'Cancel':>7} "
          f"{'NCB':>5} {'Dorm':>5} {'Live':>5}")
    for div, c in top:
        if c["total"] < 5:
            continue
        label = _cpv_division_label(div)[:40]
        print(f"  {label:<40} {c['total']:>5} "
              f"{_fmt_pct(c['awarded'], c['total']):>6} "
              f"{_fmt_pct(c['cancelled'], c['total']):>7} "
              f"{_fmt_pct(c['ncb'], c['total']):>5} "
              f"{_fmt_pct(c['dormant'], c['total']):>5} "
              f"{_fmt_pct(c['in_flight'], c['total']):>5}")

    print(f"\n  NCB = no-compliant-bid. "
          f"Categories with <5 notices in window suppressed.")


def _section_cancellation(conn, years, classified, canonical_type):
    """5. Cancellation behaviour — rate, peer comparison, time-to-cancel.

    FTS only — Contracts Finder has no cancellation marker. Peer set is
    canonical_buyers with the same `type` (region not used because it's
    largely unpopulated)."""
    print(f"\n7. Cancellation behaviour (last {years} years, FTS only)")
    print("-" * 60)

    fts = [c for c in classified if c["src"] == "fts"]
    if not fts:
        print("  No FTS notices in window.")
        return

    fts_n      = len(fts)
    cancelled  = [c for c in fts if c["bucket"] == "cancelled"]
    cancel_pct = len(cancelled) * 100.0 / fts_n if fts_n else 0

    print(f"  This buyer       : {len(cancelled):,} of {fts_n:,} "
          f"FTS notices cancelled ({cancel_pct:.1f}%)")

    # Peer median — canonical buyers with same type
    if canonical_type:
        peer_rows = conn.execute(f"""
            SELECT cb.canonical_id,
                   COUNT(*) AS fts_n,
                   SUM(CASE WHEN n.tender_status IN ('cancelled','withdrawn')
                              OR n.latest_tag = 'tenderCancellation'
                            THEN 1 ELSE 0 END) AS cancelled_n
            FROM canonical_buyers cb
            JOIN canonical_buyer_aliases a ON a.canonical_id = cb.canonical_id
            JOIN buyers br ON LOWER(TRIM(br.name)) = a.alias_lower
            JOIN notices n ON n.buyer_id = br.id
            WHERE cb.type = ?
              AND COALESCE(n.data_source, 'fts') = 'fts'
              AND n.published_date >= datetime('now', '-{years} years')
            GROUP BY cb.canonical_id
            HAVING fts_n >= 25
        """, (canonical_type,)).fetchall()

        if peer_rows:
            peer_rates = sorted(r["cancelled_n"] * 100.0 / r["fts_n"]
                                for r in peer_rows)
            n = len(peer_rates)
            median = peer_rates[n // 2] if n else None
            p75    = peer_rates[min(n - 1, int(0.75 * (n - 1)))] if n else None
            print(f"  Peer median      : {median:.1f}%  "
                  f"(across {n} '{canonical_type}' buyers with ≥25 FTS notices)")
            print(f"  Peer P75         : {p75:.1f}%")
            if median is not None:
                if cancel_pct > p75:
                    flag = "above peer P75 — high canceller"
                elif cancel_pct < median:
                    flag = "below peer median — low canceller"
                else:
                    flag = "within peer range"
                print(f"  Position         : {flag}")
        else:
            print(f"  Peer median      : insufficient peer set (need ≥25 FTS "
                  f"notices each among '{canonical_type}' buyers)")

    if not cancelled:
        return

    # Top categories cancelled
    by_div = {}
    for c in cancelled:
        d = c["cpv_div"] or "??"
        by_div[d] = by_div.get(d, 0) + 1
    top_cancel = sorted(by_div.items(), key=lambda x: -x[1])[:3]
    if top_cancel:
        print(f"\n  Categories most often cancelled:")
        for div, n in top_cancel:
            print(f"    {n:>3}  {_cpv_division_label(div)}")

    # Time-to-cancellation distribution — proxy: notice last_updated minus
    # published_date, restricted to FTS cancelled notices in window
    cancel_ocids = tuple(c["ocid"] for c in cancelled)
    if cancel_ocids:
        placeholders = ",".join("?" * len(cancel_ocids))
        rows = conn.execute(f"""
            SELECT CAST(julianday(last_updated) - julianday(published_date)
                        AS INTEGER) AS d
            FROM notices
            WHERE ocid IN ({placeholders})
              AND last_updated > published_date
        """, cancel_ocids).fetchall()
        ttd = sorted(r["d"] for r in rows if r["d"] is not None and r["d"] >= 0)
        if ttd:
            n = len(ttd)
            def pct(p):
                return ttd[max(0, min(n - 1, int(p * (n - 1))))]
            print(f"\n  Time-to-cancellation (proxy: days from publish to "
                  f"last update on cancelled FTS notices):")
            print(f"    Median : {pct(0.5)} days     "
                  f"P75 : {pct(0.75)} days     P90 : {pct(0.9)} days")


def _section_distress(conn):
    """9. Incumbent-distress flag — currently-active contracts where the
    supplier's Companies House status indicates distress.

    Coverage caveat: ch_status enrichment only fires for suppliers with
    a CH number on file (~27% of all suppliers). Currently the only
    distress value present in the data is 'dissolved'."""
    print("\n8. Incumbent-distress flag (live contracts only)")
    print("-" * 60)

    rows = conn.execute("""
        SELECT n.title, b.name AS buyer_name,
               s.name AS supplier_name, s.ch_status,
               a.value_amount_gross, a.contract_end_date
        FROM awards a
        JOIN notices n        ON n.ocid = a.ocid
        JOIN _bb_ids bb       ON bb.id = n.buyer_id
        JOIN buyers b         ON b.id = n.buyer_id
        JOIN award_suppliers asup ON asup.award_id = a.id
        JOIN suppliers s      ON s.id = asup.supplier_id
        WHERE a.status IN ('active', 'pending')
          AND a.contract_end_date > datetime('now')
          AND s.ch_status IN ('dissolved', 'liquidation', 'administration',
                              'receivership', 'in-administration',
                              'voluntary-arrangement', 'compulsory-strike-off',
                              'cessation', 'closed')
        ORDER BY a.contract_end_date ASC
        LIMIT 20
    """).fetchall()

    if not rows:
        print("  No live contracts with a distressed-supplier flag in this "
              "buyer's portfolio.")
        print("  (Only ~27% of suppliers carry a Companies House number; "
              "this flag fires only on enriched suppliers.)")
        return

    print(f"  {len(rows)} contract(s) with a distressed incumbent:")
    for r in rows:
        print(f"    - {r['supplier_name']} ({r['ch_status']}): "
              f"{r['title'][:50]}")
        print(f"        Value {fmt_gbp(r['value_amount_gross'])}, "
              f"expires {(r['contract_end_date'] or '—')[:10]}")


def _section_pgo_summary(conn, classified, years, buyer_name, distress_n):
    """10. One-line summary suitable for lifting into a Win Strategy doc."""
    print("\n9. PGO summary line")
    print("-" * 60)

    if not classified:
        print("  No classifiable notices — summary not generated.")
        return

    total = len(classified)
    counts = {"awarded": 0, "cancelled": 0, "no_compliant_bid": 0,
              "dormant": 0, "in_flight": 0}
    for c in classified:
        counts[c["bucket"]] += 1
    closed = (counts["awarded"] + counts["cancelled"]
              + counts["no_compliant_bid"] + counts["dormant"])

    if closed < 25:
        print(f"  Sample of closed notices ({closed}) too small to quote a "
              f"PGO benchmark for {buyer_name}.")
        return

    award_rate = counts["awarded"] * 100.0 / closed
    cancel_rate = counts["cancelled"] * 100.0 / closed
    ncb_rate    = counts["no_compliant_bid"] * 100.0 / closed
    dormant_rate = counts["dormant"] * 100.0 / closed

    # Median timeline among awarded
    days_rows = conn.execute(f"""
        WITH first_aw AS (
            SELECT n.ocid, n.published_date,
                   MIN(COALESCE(a.award_date, a.date_signed,
                                a.contract_start_date)) AS first_aw_date
            FROM notices n
            JOIN _bb_ids b ON n.buyer_id = b.id
            JOIN awards a  ON a.ocid = n.ocid
            WHERE n.published_date >= datetime('now', '-{years} years')
              AND a.status IN ('active','pending')
            GROUP BY n.ocid
        )
        SELECT CAST(julianday(first_aw_date) - julianday(published_date)
                    AS INTEGER) AS d
        FROM first_aw
        WHERE first_aw_date IS NOT NULL AND first_aw_date > published_date
    """).fetchall()
    days = sorted(r["d"] for r in days_rows
                  if r["d"] is not None and 0 <= r["d"] < 1500)
    median = days[len(days)//2] if days else None
    p90    = days[int(0.9*(len(days)-1))] if days else None

    distress_clause = ""
    if distress_n:
        distress_clause = (f" {distress_n} live contract"
                           f"{'s' if distress_n != 1 else ''} "
                           f"in this buyer's portfolio currently has an "
                           f"incumbent in financial distress.")

    timeline_clause = ""
    if median is not None and len(days) >= 25:
        timeline_clause = (f" Median time from publication to award was "
                           f"{median} days, with the slowest 10% taking "
                           f"over {p90} days.")

    print(f"\n  > Over the last {years} years, {buyer_name} published "
          f"{total:,} tenders ({closed:,} now closed). "
          f"{award_rate:.0f}% reached award, {cancel_rate:.0f}% were "
          f"cancelled (FTS-tracked), {ncb_rate:.0f}% received no compliant "
          f"bid, {dormant_rate:.0f}% went dormant.{timeline_clause}"
          f"{distress_clause} PGO benchmark for tenders from this buyer: "
          f"{award_rate:.0f}% historical award rate.")


def buyer_behaviour_data(name_query, years=5):
    """JSON-emitting variant of buyer_behaviour. Returns a dict with the
    same shape as the JS module's buyerBehaviourProfile() so the dashboard
    HTTP endpoint and the platform Data API surface identical structures.

    Returns {} with an 'error' key on failure (no matching buyer, ambiguous
    name, etc.) so the caller can return JSON unconditionally."""
    from datetime import datetime, timezone

    conn = get_db()
    resolved = _resolve_buyer_canonical(conn, name_query)
    if resolved is None:
        conn.close()
        return {"error": f"No buyer found matching '{name_query}'."}
    if not resolved["raw_buyer_ids"]:
        conn.close()
        return {"error": f"Buyer '{resolved['canonical_name']}' has no rows in the database."}

    _stage_buyer_id_temp_table(conn, resolved["raw_buyer_ids"])
    cat_p95 = _compute_cpv_division_p95(conn)

    def _safe_pct(num, denom, places=1):
        if not denom:
            return None
        return round(num * 100.0 / denom, places)

    # ── Volume and trend ─────────────────────────────────────────────────
    vol_rows = conn.execute(f"""
        SELECT CAST(STRFTIME('%Y', n.published_date) AS INTEGER)  AS yr,
               COALESCE(n.data_source, 'fts')                     AS src,
               COUNT(*)                                           AS notices
        FROM notices n
        JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE n.published_date >= datetime('now', '-{years} years')
        GROUP BY yr, src ORDER BY yr ASC, src ASC
    """).fetchall()
    award_rows = conn.execute(f"""
        SELECT CAST(STRFTIME('%Y', a.award_date) AS INTEGER) AS yr,
               COUNT(DISTINCT a.id)                          AS awards
        FROM awards a
        JOIN notices n ON a.ocid = n.ocid
        JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE a.award_date >= datetime('now', '-{years} years')
          AND a.status IN ('active', 'pending')
        GROUP BY yr
    """).fetchall()
    awards_by_yr = {r["yr"]: r["awards"] for r in award_rows if r["yr"]}
    by_yr_src = {}
    by_yr = {}
    for r in vol_rows:
        if not r["yr"]:
            continue
        by_yr[r["yr"]] = by_yr.get(r["yr"], 0) + r["notices"]
        by_yr_src[(r["yr"], r["src"])] = r["notices"]
    yrs = sorted(by_yr.keys())
    by_year_list = []
    total_notices = total_fts = total_cf = total_aw = 0
    for y in yrs:
        f = by_yr_src.get((y, "fts"), 0)
        c = by_yr_src.get((y, "cf"),  0)
        a = awards_by_yr.get(y, 0)
        by_year_list.append({"year": y, "notices": by_yr[y],
                             "fts": f, "cf": c, "awards": a})
        total_notices += by_yr[y]; total_fts += f; total_cf += c; total_aw += a
    trend_dir = trend_pct = None
    if len(yrs) >= 3:
        recent = by_yr[yrs[-2]]; prior = by_yr[yrs[-3]]
        if prior:
            d = (recent - prior) * 100.0 / prior
            trend_pct = round(d, 0)
            trend_dir = "growing" if d > 10 else "shrinking" if d < -10 else "steady"
    volume = {
        "totalNotices": total_notices, "ftsNotices": total_fts,
        "cfNotices": total_cf, "totalAwards": total_aw,
        "byYear": by_year_list,
        "trendDirection": trend_dir, "trendDeltaPct": trend_pct,
    }

    # ── Method mix (FTS only) ────────────────────────────────────────────
    method_rows = conn.execute(f"""
        SELECT n.procurement_method  AS method,
               n.procurement_method_detail AS detail,
               COUNT(*)              AS n
        FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE COALESCE(n.data_source, 'fts') = 'fts'
          AND n.published_date >= datetime('now', '-{years} years')
        GROUP BY method, detail
    """).fetchall()
    fts_total = sum(r["n"] for r in method_rows)
    by_method = {}; framework = 0
    for r in method_rows:
        d = (r["detail"] or "").lower()
        if "framework" in d or "call-off" in d or "call off" in d:
            framework += r["n"]
        else:
            m = r["method"] or "unknown"
            by_method[m] = by_method.get(m, 0) + r["n"]
    if framework:
        by_method["framework_call_off"] = framework
    methods_list = sorted(
        [{"method": m, "count": n, "sharePct": _safe_pct(n, fts_total)}
         for m, n in by_method.items()],
        key=lambda x: -x["count"],
    )
    cf_no_method = conn.execute(f"""
        SELECT COUNT(*) FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE n.data_source = 'cf'
          AND n.published_date >= datetime('now', '-{years} years')
    """).fetchone()[0]
    method_mix = {"ftsTotal": fts_total, "cfNoMethodCount": cf_no_method,
                  "methods": methods_list}

    # ── Competition intensity ────────────────────────────────────────────
    overall = conn.execute(f"""
        SELECT AVG(n.total_bids) AS avg_bids, COUNT(n.total_bids) AS n
        FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
        WHERE n.published_date >= datetime('now', '-{years} years')
          AND n.total_bids IS NOT NULL AND n.total_bids > 0
    """).fetchone()
    competition = {"avgBidders": None, "bidRecordedN": 0, "byYear": []}
    if overall["n"]:
        yearly = [r for r in conn.execute(f"""
            SELECT CAST(STRFTIME('%Y', n.published_date) AS INTEGER) AS yr,
                   AVG(n.total_bids) AS avg_bids, COUNT(*) AS n
            FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
            WHERE n.published_date >= datetime('now', '-{years} years')
              AND n.total_bids > 0
            GROUP BY yr ORDER BY yr ASC
        """).fetchall() if r["yr"]]
        low = conn.execute(f"""
            SELECT COUNT(*) FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
            WHERE n.published_date >= datetime('now', '-{years} years')
              AND n.total_bids IS NOT NULL AND n.total_bids < 3 AND n.total_bids > 0
        """).fetchone()[0]
        trend = None
        if len(yearly) >= 3 and yearly[0]["avg_bids"]:
            d = (yearly[-1]["avg_bids"] - yearly[0]["avg_bids"]) / yearly[0]["avg_bids"]
            trend = "rising" if d > 0.15 else "falling" if d < -0.15 else "flat"
        competition = {
            "avgBidders": round(overall["avg_bids"], 2),
            "bidRecordedN": overall["n"],
            "byYear": [{"year": r["yr"],
                        "avgBidders": round(r["avg_bids"], 2),
                        "noticesWithBidCount": r["n"]} for r in yearly],
            "lowCompetitionCount": low,
            "lowCompetitionSharePct": _safe_pct(low, overall["n"]),
            "trendDirection": trend,
        }

    # ── Outcome classification ───────────────────────────────────────────
    classified = _classify_outcomes(conn, years, cat_p95)
    total = len(classified)
    fts_t = sum(1 for c in classified if c["src"] == "fts")
    counts = {"awarded": 0, "cancelled": 0, "no_compliant_bid": 0,
              "dormant": 0, "in_flight": 0}
    for c in classified:
        counts[c["bucket"]] += 1
    closed = counts["awarded"] + counts["cancelled"] + counts["no_compliant_bid"] + counts["dormant"]
    quality = "too_small" if total < 10 else "indicative" if total < 25 else "reliable"
    outcome_mix = {
        "sampleSize": total, "sampleQuality": quality, "ftsTotal": fts_t,
        "buckets": {
            "awarded":        counts["awarded"],
            "cancelled":      counts["cancelled"],
            "noCompliantBid": counts["no_compliant_bid"],
            "dormant":        counts["dormant"],
            "inFlight":       counts["in_flight"],
        },
        "sharesPct": {
            "awarded":        _safe_pct(counts["awarded"], total),
            "cancelled":      _safe_pct(counts["cancelled"], fts_t),
            "noCompliantBid": _safe_pct(counts["no_compliant_bid"], total),
            "dormant":        _safe_pct(counts["dormant"], total),
            "inFlight":       _safe_pct(counts["in_flight"], total),
        },
        "closedTotal": closed,
        "awardedOfClosedPct": _safe_pct(counts["awarded"], closed),
    }

    # ── Timeline ────────────────────────────────────────────────────────
    t_rows = conn.execute(f"""
        WITH first_aw AS (
            SELECT n.ocid, n.published_date,
                   MIN(COALESCE(a.award_date, a.date_signed,
                                a.contract_start_date)) AS first_aw_date
            FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
            JOIN awards a  ON a.ocid = n.ocid
            WHERE n.published_date >= datetime('now', '-{years} years')
              AND a.status IN ('active', 'pending')
            GROUP BY n.ocid
        )
        SELECT CAST(julianday(first_aw_date) - julianday(published_date)
                    AS INTEGER) AS days
        FROM first_aw
        WHERE first_aw_date IS NOT NULL AND first_aw_date > published_date
    """).fetchall()
    days = sorted(r["days"] for r in t_rows
                  if r["days"] is not None and 0 <= r["days"] < 1500)
    if len(days) < 25:
        timeline = {
            "pairedN": len(days),
            "suppressedReason": (
                "No paired publication and award dates in window."
                if not days
                else f"Only {len(days)} notices have paired dates — too few for percentile analysis."
            ),
        }
    else:
        n = len(days)
        def _p(p):
            return days[max(0, min(n - 1, int(p * (n - 1))))]
        timeline = {"pairedN": n, "medianDays": _p(0.5),
                    "p25Days": _p(0.25), "p75Days": _p(0.75),
                    "p90Days": _p(0.9),  "p95Days": _p(0.95)}

    # ── Category footprint ───────────────────────────────────────────────
    by_div = {}
    for c in classified:
        d = c["cpv_div"] or "??"
        by_div.setdefault(d, {"total": 0, "awarded": 0, "cancelled": 0,
                              "ncb": 0, "dormant": 0, "inFlight": 0})
        by_div[d]["total"] += 1
        k = ("ncb" if c["bucket"] == "no_compliant_bid"
             else "inFlight" if c["bucket"] == "in_flight"
             else c["bucket"])
        by_div[d][k] += 1
    cat_list = []
    for div, v in sorted(by_div.items(), key=lambda x: -x[1]["total"])[:10]:
        if v["total"] < 5:
            continue
        cat_list.append({
            "cpvDivision":  None if div == "??" else div,
            "label":        _cpv_division_label(None if div == "??" else div),
            "total":        v["total"],
            "awardedPct":   _safe_pct(v["awarded"],   v["total"]),
            "cancelledPct": _safe_pct(v["cancelled"], v["total"]),
            "ncbPct":       _safe_pct(v["ncb"],       v["total"]),
            "dormantPct":   _safe_pct(v["dormant"],   v["total"]),
            "inFlightPct":  _safe_pct(v["inFlight"],  v["total"]),
        })

    # ── Cancellation ─────────────────────────────────────────────────────
    fts_cls = [c for c in classified if c["src"] == "fts"]
    cancel = [c for c in fts_cls if c["bucket"] == "cancelled"]
    this_pct = _safe_pct(len(cancel), len(fts_cls)) if fts_cls else None
    peer = None
    if resolved["canonical_type"]:
        peer_rows = conn.execute(f"""
            SELECT cb.canonical_id,
                   COUNT(*) AS fts_n,
                   SUM(CASE WHEN n.tender_status IN ('cancelled','withdrawn')
                              OR n.latest_tag = 'tenderCancellation'
                            THEN 1 ELSE 0 END) AS cancelled_n
            FROM canonical_buyers cb
            JOIN canonical_buyer_aliases a ON a.canonical_id = cb.canonical_id
            JOIN buyers br ON LOWER(TRIM(br.name)) = a.alias_lower
            JOIN notices n ON n.buyer_id = br.id
            WHERE cb.type = ?
              AND COALESCE(n.data_source, 'fts') = 'fts'
              AND n.published_date >= datetime('now', '-{years} years')
            GROUP BY cb.canonical_id HAVING fts_n >= 25
        """, (resolved["canonical_type"],)).fetchall()
        if peer_rows:
            rates = sorted(r["cancelled_n"] * 100.0 / r["fts_n"] for r in peer_rows)
            n = len(rates)
            median = rates[n // 2]
            p75 = rates[min(n - 1, int(0.75 * (n - 1)))]
            label = ("above peer P75 — high canceller" if this_pct and this_pct > p75
                     else "below peer median — low canceller" if this_pct is not None and this_pct < median
                     else "within peer range")
            peer = {"peerType": resolved["canonical_type"], "peerCount": n,
                    "peerMedianPct": round(median, 1),
                    "peerP75Pct":    round(p75, 1),
                    "positionLabel": label}
        else:
            peer = {"peerType": resolved["canonical_type"], "peerCount": 0,
                    "note": f"No peer set with ≥25 FTS notices for type '{resolved['canonical_type']}'."}
    cancel_div = {}
    for c in cancel:
        d = c["cpv_div"] or "??"
        cancel_div[d] = cancel_div.get(d, 0) + 1
    top_cancel = [
        {"cpvDivision": None if d == "??" else d,
         "label":        _cpv_division_label(None if d == "??" else d),
         "n": n}
        for d, n in sorted(cancel_div.items(), key=lambda x: -x[1])[:3]
    ]
    ttd_obj = None
    if cancel:
        placeholders = ",".join("?" * len(cancel))
        rows = conn.execute(f"""
            SELECT CAST(julianday(last_updated) - julianday(published_date)
                        AS INTEGER) AS d
            FROM notices WHERE ocid IN ({placeholders})
              AND last_updated > published_date
        """, [c["ocid"] for c in cancel]).fetchall()
        ttd = sorted(r["d"] for r in rows if r["d"] is not None and r["d"] >= 0)
        if ttd:
            n = len(ttd)
            def _p(p):
                return ttd[max(0, min(n - 1, int(p * (n - 1))))]
            ttd_obj = {"n": n, "medianDays": _p(0.5),
                       "p75Days": _p(0.75), "p90Days": _p(0.9)}
    cancellation = {
        "ftsTotal": len(fts_cls), "cancelledN": len(cancel),
        "thisBuyerPct": this_pct, "peer": peer,
        "topCancelledCategories": top_cancel,
        "timeToCancel": ttd_obj,
    }

    # ── Distress ─────────────────────────────────────────────────────────
    drows = conn.execute("""
        SELECT n.title, b.name AS buyer_name,
               s.name AS supplier_name, s.ch_status,
               a.value_amount_gross, a.contract_end_date
        FROM awards a
        JOIN notices n        ON n.ocid = a.ocid
        JOIN _bb_ids bb       ON bb.id = n.buyer_id
        JOIN buyers b         ON b.id = n.buyer_id
        JOIN award_suppliers asup ON asup.award_id = a.id
        JOIN suppliers s      ON s.id = asup.supplier_id
        WHERE a.status IN ('active', 'pending')
          AND a.contract_end_date > datetime('now')
          AND s.ch_status IN ('dissolved', 'liquidation', 'administration',
                              'receivership', 'in-administration',
                              'voluntary-arrangement', 'compulsory-strike-off',
                              'cessation', 'closed')
        ORDER BY a.contract_end_date ASC LIMIT 20
    """).fetchall()
    distress = {
        "count": len(drows),
        "coverageNote": "Only ~27% of suppliers carry a Companies House number; this flag fires only on enriched suppliers. ch_status 'dissolved' is currently the only distress value populated in the data.",
        "contracts": [
            {"title": r["title"], "supplierName": r["supplier_name"],
             "chStatus": r["ch_status"], "contractValue": r["value_amount_gross"],
             "contractEndDate": r["contract_end_date"]}
            for r in drows
        ],
    }

    # ── Summary ─────────────────────────────────────────────────────────
    summary = None
    if closed >= 25:
        award = round(counts["awarded"] * 100 / closed)
        cancel_pct_c = round(counts["cancelled"] * 100 / closed)
        ncb_pct = round(counts["no_compliant_bid"] * 100 / closed)
        dorm_pct = round(counts["dormant"] * 100 / closed)
        timeline_clause = ""
        if isinstance(timeline.get("medianDays"), int) and timeline.get("pairedN", 0) >= 25:
            timeline_clause = (f" Median time from publication to award was "
                               f"{timeline['medianDays']} days, with the slowest "
                               f"10% taking over {timeline['p90Days']} days.")
        distress_clause = ""
        if distress["count"]:
            s = "" if distress["count"] == 1 else "s"
            distress_clause = (f" {distress['count']} live contract{s} in this "
                               f"buyer's portfolio currently has an incumbent "
                               f"in financial distress.")
        summary = (
            f"Over the last {years} years, {resolved['canonical_name']} "
            f"published {total:,} tenders ({closed:,} now closed). "
            f"{award}% reached award, {cancel_pct_c}% were cancelled "
            f"(FTS-tracked), {ncb_pct}% received no compliant bid, "
            f"{dorm_pct}% went dormant.{timeline_clause}{distress_clause} "
            f"PGO benchmark for tenders from this buyer: {award}% historical "
            f"award rate."
        )

    out = {
        "meta": {
            "canonicalId":     resolved["canonical_id"],
            "canonicalName":   resolved["canonical_name"],
            "canonicalType":   resolved["canonical_type"],
            "rawBuyerIdCount": len(resolved["raw_buyer_ids"]),
            "fragmented":      resolved["fragmented"],
            "yearsWindow":     years,
            "generatedAt":     datetime.now(timezone.utc).isoformat(),
        },
        "volume":            volume,
        "methodMix":         method_mix,
        "competition":       competition,
        "outcomeMix":        outcome_mix,
        "timeline":          timeline,
        "categoryFootprint": cat_list,
        "cancellation":      cancellation,
        "distress":          distress,
        "summary":           summary,
        "caveats": [
            "Cancellation analysis is FTS-only — Contracts Finder rows have no cancellation marker.",
            "Procurement-method mix is FTS-only — both method columns are unpopulated for Contracts Finder rows.",
            "Amendment behaviour deferred to Phase 2 (no usable amendment trail in current schema).",
            "Distress flag fires only on enriched suppliers (~27% coverage) and only on ch_status='dissolved'.",
            "Peer comparison uses canonical_buyers.type only (region is unpopulated for Contracts Finder).",
        ],
    }
    conn.close()
    return out


def buyer_behaviour(name_query, years=5):
    """Buyer behavioural intelligence profile (v1).

    See pwin-competitive-intel/docs/buyer-behaviour-analytics-v1.md
    for the full spec. Output is one-page-of-text per buyer.
    """
    conn = get_db()

    resolved = _resolve_buyer_canonical(conn, name_query)
    if resolved is None:
        print(f"No buyer found matching '{name_query}'.")
        conn.close()
        return

    print(f"\n{'='*72}")
    print(f"BUYER BEHAVIOUR PROFILE — {resolved['canonical_name']}")
    if resolved["canonical_id"]:
        print(f"Canonical ID  : {resolved['canonical_id']}")
        print(f"Type          : {resolved['canonical_type'] or '—'}")
    if resolved["fragmented"]:
        print(f"\n  ⚠ FRAGMENTED BUYER WARNING")
        print(f"  Name '{name_query}' did not resolve to a canonical entity.")
        print(f"  Falling back to raw name LIKE match across "
              f"{len(resolved['raw_buyer_ids'])} buyer rows.")
        print(f"  Aggregations may double-count or miss related entities.")
    print(f"Raw rows      : {len(resolved['raw_buyer_ids']):,} buyer IDs")
    print(f"Window        : last {years} years")

    if not resolved["raw_buyer_ids"]:
        print("\nNo buyer rows in database.")
        conn.close()
        return

    _stage_buyer_id_temp_table(conn, resolved["raw_buyer_ids"])

    cat_p95 = _compute_cpv_division_p95(conn)

    _section_volume_trend(conn, years)
    _section_method_mix(conn, years)
    _section_competition(conn, years)
    classified = _section_outcome_mix(conn, years, cat_p95)
    _section_timeline(conn, years)
    _section_category_footprint(conn, years, classified, cat_p95)
    _section_cancellation(conn, years, classified, resolved["canonical_type"])
    distress_n = _count_distress_for_summary(conn)
    _section_distress(conn)
    _section_pgo_summary(conn, classified, years,
                         resolved["canonical_name"], distress_n)

    conn.close()


def _count_distress_for_summary(conn):
    return conn.execute("""
        SELECT COUNT(DISTINCT a.id)
        FROM awards a
        JOIN notices n        ON n.ocid = a.ocid
        JOIN _bb_ids bb       ON bb.id = n.buyer_id
        JOIN award_suppliers asup ON asup.award_id = a.id
        JOIN suppliers s      ON s.id = asup.supplier_id
        WHERE a.status IN ('active', 'pending')
          AND a.contract_end_date > datetime('now')
          AND s.ch_status IN ('dissolved', 'liquidation', 'administration',
                              'receivership', 'in-administration',
                              'voluntary-arrangement', 'compulsory-strike-off',
                              'cessation', 'closed')
    """).fetchone()[0] or 0


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PWIN Competitive Intelligence queries")
    sub = parser.add_subparsers(dest="cmd")

    p_buyer = sub.add_parser("buyer", help="Buyer procurement profile")
    p_buyer.add_argument("name", help="Buyer name (partial match)")

    p_bb = sub.add_parser("buyer-behaviour",
                          help="Buyer behaviour analytics (v1) — PGO inputs")
    p_bb.add_argument("name", help="Buyer name (canonical / abbreviation / partial)")
    p_bb.add_argument("--years", type=int, default=5,
                      help="Time window in years (default 5)")

    p_sup = sub.add_parser("supplier", help="Supplier win history")
    p_sup.add_argument("name", help="Supplier name (partial match)")

    p_exp = sub.add_parser("expiring", help="Contracts expiring soon")
    p_exp.add_argument("--days",     type=int,   default=365)
    p_exp.add_argument("--value",    type=float, default=None, help="Min value £")
    p_exp.add_argument("--buyer",    default=None)
    p_exp.add_argument("--category", default=None)

    p_pip = sub.add_parser("pipeline", help="Forward planning / market engagement")
    p_pip.add_argument("--buyer", default=None)

    p_aw = sub.add_parser("awards", help="Awards above value threshold")
    p_aw.add_argument("--value",    type=float, default=1_000_000)
    p_aw.add_argument("--buyer",    default=None)
    p_aw.add_argument("--supplier", default=None)

    p_pw = sub.add_parser("pwin", help="PWIN signals — competition analysis")
    p_pw.add_argument("--buyer",    default=None)
    p_pw.add_argument("--category", default=None)

    p_cpv = sub.add_parser("cpv", help="Search by CPV code")
    p_cpv.add_argument("code", help="CPV code (prefix match)")

    sub.add_parser("summary", help="Database stats")

    args = parser.parse_args()

    commands = {
        "summary":  lambda: db_summary(),
        "buyer":            lambda: buyer_profile(args.name),
        "buyer-behaviour":  lambda: buyer_behaviour(args.name, args.years),
        "supplier":         lambda: supplier_profile(args.name),
        "expiring": lambda: expiring_contracts(args.days, args.value, args.buyer, args.category),
        "pipeline": lambda: forward_pipeline(args.buyer),
        "awards":   lambda: awards_above_value(args.value, args.buyer, args.supplier),
        "pwin":     lambda: pwin_signals(args.buyer, args.category),
        "cpv":      lambda: cpv_search(args.code),
    }

    if args.cmd in commands:
        commands[args.cmd]()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
