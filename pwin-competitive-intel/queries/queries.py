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
    print("=" * 50)
    for table in ["buyers", "suppliers", "notices", "lots", "awards", "award_suppliers",
                   "cpv_codes", "planning_notices"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<25} {count:>8,}")

    cursor = conn.execute(
        "SELECT value FROM ingest_state WHERE key='last_cursor'"
    ).fetchone()
    print(f"\n  Last ingest cursor: {cursor['value'] if cursor and cursor['value'] else 'none'}")

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
# CLI
# ──────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PWIN Competitive Intelligence queries")
    sub = parser.add_subparsers(dest="cmd")

    p_buyer = sub.add_parser("buyer", help="Buyer procurement profile")
    p_buyer.add_argument("name", help="Buyer name (partial match)")

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
        "buyer":    lambda: buyer_profile(args.name),
        "supplier": lambda: supplier_profile(args.name),
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
