"""
PWIN Competitive Intelligence — Dashboard Data Server
=====================================================
Lightweight HTTP API serving SQLite query results to the dashboard.
No external dependencies — uses Python stdlib only.

Usage:
    python server.py              # starts on localhost:8765
    python server.py --port 9000  # custom port
"""

import argparse
import json
import sqlite3
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

DB_PATH = Path(__file__).parent / "db" / "bid_intel.db"

def get_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def dict_rows(rows):
    return [dict(r) for r in rows]

def fmt_methods(method_rows):
    """Convert list of {procurement_method, cnt} rows into {open, limited, direct, selective} dict."""
    result = {"open": 0, "limited": 0, "direct": 0, "selective": 0}
    for r in method_rows:
        m = r.get("procurement_method") or "unknown"
        if m in result:
            result[m] = r["cnt"]
    return result


# ── API handlers ──────────────────────────────────────────────────────────

def api_summary():
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        counts = {}
        for t in ["buyers", "suppliers", "notices", "lots", "awards", "award_suppliers", "cpv_codes", "planning_notices"]:
            counts[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]

        cursor = conn.execute("SELECT value FROM ingest_state WHERE key='last_cursor'").fetchone()
        val = conn.execute("SELECT SUM(value_amount_gross) as total, AVG(value_amount_gross) as avg, MAX(value_amount_gross) as mx FROM awards WHERE value_amount_gross IS NOT NULL").fetchone()

        top_cpv = [
            {"code": r["code"], "description": r["description"], "awards": r["cnt"]}
            for r in conn.execute("SELECT code, description, COUNT(*) AS cnt FROM cpv_codes GROUP BY code ORDER BY cnt DESC LIMIT 15").fetchall()
        ]

        method_rows = dict_rows(conn.execute("""
            SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
            FROM awards a JOIN notices n ON a.ocid = n.ocid
            WHERE a.status IN ('active', 'pending')
            GROUP BY n.procurement_method ORDER BY cnt DESC
        """).fetchall())

        # Coverage stats
        dates = conn.execute("SELECT MIN(published_date) as earliest, MAX(published_date) as latest FROM notices WHERE published_date IS NOT NULL").fetchone()
        cpv_count = conn.execute("SELECT COUNT(DISTINCT code) FROM cpv_codes").fetchone()[0]
        region_count = conn.execute("SELECT COUNT(DISTINCT region_code) FROM buyers WHERE region_code IS NOT NULL").fetchone()[0]

        return {
            "buyers": counts["buyers"],
            "suppliers": counts["suppliers"],
            "notices": counts["notices"],
            "awards": counts["awards"],
            "total_value": val[0],
            "avg_value": val[1],
            "max_value": val[2],
            "last_ingest": cursor[0] if cursor else None,
            "top_cpv": top_cpv,
            "methods": fmt_methods(method_rows),
            "coverage": {
                "earliest": dates[0],
                "latest": dates[1],
                "cpv_codes": cpv_count,
                "regions": region_count,
            },
        }
    finally:
        conn.close()


def api_buyer(params):
    name = params.get("name", [""])[0]
    if not name: return {"error": "name parameter required"}
    limit = int(params.get("limit", ["20"])[0])
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        buyers = conn.execute("""
            SELECT id, name, org_type, region_code FROM buyers
            WHERE LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 10
        """, (f"%{name}%",)).fetchall()

        if not buyers: return {"buyers": [], "message": f"No buyers matching '{name}'"}

        results = []
        for buyer in buyers:
            stats = conn.execute("""
                SELECT COUNT(DISTINCT a.id) AS total_awards, COUNT(DISTINCT n.ocid) AS total_notices,
                       SUM(a.value_amount_gross) AS total_spend, AVG(a.value_amount_gross) AS avg_value,
                       MAX(a.value_amount_gross) AS max_value, AVG(n.total_bids) AS avg_bids
                FROM awards a JOIN notices n ON a.ocid = n.ocid
                WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
            """, (buyer["id"],)).fetchone()

            method_rows = dict_rows(conn.execute("""
                SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
                FROM awards a JOIN notices n ON a.ocid = n.ocid
                WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
                GROUP BY n.procurement_method ORDER BY cnt DESC
            """, (buyer["id"],)).fetchall())

            top_suppliers = [
                {"name": r["name"], "awards": r["wins"], "value": r["total_value"]}
                for r in conn.execute("""
                    SELECT canonical_name AS name,
                           COUNT(DISTINCT award_id) AS wins,
                           SUM(value_amount_gross) AS total_value
                    FROM v_canonical_supplier_wins
                    WHERE buyer_id = ? AND value_quality IS NULL
                    GROUP BY canonical_id
                    ORDER BY wins DESC, total_value DESC LIMIT 15
                """, (buyer["id"],)).fetchall()
            ]

            recent_awards = [
                {"title": r["title"], "value": r["value_amount_gross"],
                 "method": r["procurement_method"], "supplier": r["suppliers"],
                 "date": r["award_date"], "end_date": r["contract_end_date"]}
                for r in conn.execute("""
                    SELECT n.title, a.value_amount_gross, n.procurement_method,
                           GROUP_CONCAT(DISTINCT s.name) AS suppliers,
                           a.contract_end_date, a.award_date
                    FROM awards a
                    JOIN notices n ON a.ocid = n.ocid
                    LEFT JOIN award_suppliers asup ON a.id = asup.award_id
                    LEFT JOIN suppliers s ON asup.supplier_id = s.id
                    WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
                    GROUP BY a.id ORDER BY a.award_date DESC NULLS LAST LIMIT ?
                """, (buyer["id"], limit)).fetchall()
            ]

            results.append({
                "name": buyer["name"],
                "org_type": buyer["org_type"],
                "region_code": buyer["region_code"],
                "awards": stats["total_awards"],
                "total_spend": stats["total_spend"],
                "avg_value": stats["avg_value"],
                "max_value": stats["max_value"],
                "avg_bids": stats["avg_bids"],
                "methods": fmt_methods(method_rows),
                "top_suppliers": top_suppliers,
                "recent_awards": recent_awards,
            })

        return {"buyers": results}
    finally:
        conn.close()


def api_supplier(params):
    name = params.get("name", [""])[0]
    if not name: return {"error": "name parameter required"}
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        # Search canonical entities — matches canonical_name OR any raw
        # member name. Splink clustering has already collapsed variants
        # across normalised-name AND cross-name patterns (brand vs legal
        # entity, rebrands, subsidiaries).
        canonicals = conn.execute("""
            SELECT DISTINCT canonical_id, canonical_name,
                            canonical_ch_numbers, canonical_distinct_ch_count,
                            canonical_member_count
            FROM v_canonical_supplier_wins
            WHERE LOWER(canonical_name) LIKE LOWER(?)
               OR LOWER(raw_supplier_name) LIKE LOWER(?)
            ORDER BY canonical_member_count DESC NULLS LAST, canonical_name
            LIMIT 10
        """, (f"%{name}%", f"%{name}%")).fetchall()

        if not canonicals: return {"suppliers": [], "message": f"No suppliers matching '{name}'"}

        results = []
        for grp in canonicals:
            cid = grp["canonical_id"]

            stats = conn.execute("""
                SELECT COUNT(DISTINCT award_id) AS total_wins,
                       SUM(value_amount_gross) AS total_value,
                       AVG(value_amount_gross) AS avg_value,
                       MAX(value_amount_gross) AS max_value,
                       MIN(award_date) AS first_win,
                       MAX(award_date) AS last_win
                FROM v_canonical_supplier_wins
                WHERE canonical_id = ? AND value_quality IS NULL
            """, (cid,)).fetchone()

            buyer_rels = [
                {"name": r["name"], "awards": r["awards"], "value": r["total_value"]}
                for r in conn.execute("""
                    SELECT COALESCE(cb.canonical_name, v.buyer_name) AS name,
                           COUNT(DISTINCT v.award_id) AS awards,
                           SUM(v.value_amount_gross) AS total_value
                    FROM v_canonical_supplier_wins v
                    JOIN buyers b ON v.buyer_id = b.id
                    LEFT JOIN canonical_buyers cb ON b.canonical_id = cb.canonical_id
                    WHERE v.canonical_id = ? AND v.value_quality IS NULL
                    GROUP BY COALESCE(cb.canonical_id, b.id)
                    ORDER BY awards DESC LIMIT 15
                """, (cid,)).fetchall()
            ]

            # GROUP BY award_id collapses the N-rows-per-award that appear
            # when a canonical rolls up multiple raw suppliers on one award.
            awards_list = [
                {"title": r["title"], "buyer": r["buyer"], "value": r["value_amount_gross"],
                 "service": r["service_category"],
                 "end_date": r["contract_end_date"], "award_date": r["award_date"],
                 "method": r["procurement_method_detail"]}
                for r in conn.execute("""
                    SELECT v.title,
                           COALESCE(cb.canonical_name, v.buyer_name) AS buyer,
                           v.value_amount_gross,
                           n.service_category,
                           v.contract_end_date, v.award_date,
                           n.procurement_method_detail
                    FROM v_canonical_supplier_wins v
                    JOIN notices n ON v.ocid = n.ocid
                    JOIN buyers b ON v.buyer_id = b.id
                    LEFT JOIN canonical_buyers cb ON b.canonical_id = cb.canonical_id
                    WHERE v.canonical_id = ? AND v.award_status IN ('active', 'pending')
                    GROUP BY v.award_id
                    ORDER BY v.value_amount_gross DESC NULLS LAST LIMIT 50
                """, (cid,)).fetchall()
            ]

            # Companies House enrichment — pick the most-recently-enriched
            # raw member as the representative. A canonical may have multiple
            # CH numbers (group consolidation); we show one, not all.
            ch_row = conn.execute("""
                SELECT s.companies_house_no, s.scale, s.is_vcse,
                       s.ch_company_name, s.ch_status, s.ch_type, s.ch_incorporated,
                       s.ch_sic_codes, s.ch_address, s.ch_turnover, s.ch_net_assets,
                       s.ch_employees, s.ch_accounts_date, s.ch_directors, s.ch_parent,
                       s.ch_enriched_at, s.name AS display_name
                FROM suppliers s
                LEFT JOIN supplier_to_canonical s2c ON s.id = s2c.supplier_id
                WHERE COALESCE(s2c.canonical_id, 'RAW-' || s.id) = ?
                ORDER BY (s.ch_enriched_at IS NOT NULL) DESC,
                         s.ch_enriched_at DESC
                LIMIT 1
            """, (cid,)).fetchone()

            ch = None
            if ch_row and ch_row["ch_enriched_at"]:
                directors = []
                try: directors = json.loads(ch_row["ch_directors"] or "[]")
                except: pass
                sic = []
                try: sic = json.loads(ch_row["ch_sic_codes"] or "[]")
                except: pass
                ch = {
                    "company_name": ch_row["ch_company_name"],
                    "status": ch_row["ch_status"],
                    "type": ch_row["ch_type"],
                    "incorporated": ch_row["ch_incorporated"],
                    "sic_codes": sic,
                    "address": ch_row["ch_address"],
                    "turnover": ch_row["ch_turnover"],
                    "net_assets": ch_row["ch_net_assets"],
                    "employees": ch_row["ch_employees"],
                    "accounts_date": ch_row["ch_accounts_date"],
                    "directors": directors,
                    "parent": ch_row["ch_parent"],
                }

            results.append({
                "name": grp["canonical_name"],
                "canonical_id": cid,
                "canonical_ch_numbers": grp["canonical_ch_numbers"],
                "variant_count": grp["canonical_member_count"] or 1,
                "scale": ch_row["scale"] if ch_row else None,
                "is_vcse": bool(ch_row["is_vcse"]) if ch_row else False,
                "companies_house_no": ch_row["companies_house_no"] if ch_row else None,
                "wins": stats["total_wins"],
                "total_value": stats["total_value"],
                "avg_value": stats["avg_value"],
                "first_win": stats["first_win"],
                "last_win": stats["last_win"],
                "buyers": buyer_rels,
                "active_contracts": awards_list,
                "companies_house": ch,
            })

        # Sort by total wins descending so the most relevant result is first
        results.sort(key=lambda r: -(r["wins"] or 0))
        return {"suppliers": results}
    finally:
        conn.close()


def api_expiring(params):
    days = int(params.get("days", ["365"])[0])
    min_value = float(params.get("minValue", ["0"])[0])
    buyer = params.get("buyer", [""])[0]
    category = params.get("category", [""])[0]
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        sql = "SELECT * FROM v_expiring_contracts WHERE days_to_expiry <= ?"
        p = [days]
        if min_value > 0: sql += " AND value_amount_gross >= ?"; p.append(min_value)
        if buyer: sql += " AND LOWER(buyer_name) LIKE LOWER(?)"; p.append(f"%{buyer}%")
        if category: sql += " AND LOWER(main_category) LIKE LOWER(?)"; p.append(f"%{category}%")
        sql += " ORDER BY days_to_expiry ASC LIMIT 200"
        rows = [
            {"buyer": r["buyer_name"], "supplier": r["supplier_names"],
             "title": r["title"], "value": r["value_amount_gross"],
             "days_to_expiry": r["days_to_expiry"], "method": r["procurement_method"],
             "end_date": r["contract_end_date"], "start_date": r["contract_start_date"],
             "max_extend": r["contract_max_extend"], "category": r["main_category"],
             "has_renewal": bool(r["has_renewal"]), "renewal_description": r["renewal_description"],
             "notice_url": r["notice_url"], "buyer_type": r["buyer_type"]}
            for r in conn.execute(sql, p).fetchall()
        ]
        return {"count": len(rows), "contracts": rows}
    finally:
        conn.close()


def api_pipeline(params):
    buyer = params.get("buyer", [""])[0]
    org_type = params.get("orgType", [""])[0]
    min_value = float(params.get("minValue", ["0"])[0])
    days = params.get("days", [""])[0]
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        sql = """
            SELECT p.ocid, p.title, p.description, p.engagement_deadline, p.future_notice_date,
                   p.estimated_value, p.notice_url, b.name AS buyer_name, b.org_type
            FROM planning_notices p JOIN buyers b ON p.buyer_id = b.id WHERE 1=1
        """
        p = []
        if buyer: sql += " AND LOWER(b.name) LIKE LOWER(?)"; p.append(f"%{buyer}%")
        if org_type: sql += " AND LOWER(b.org_type) LIKE LOWER(?)"; p.append(f"%{org_type}%")
        if min_value > 0: sql += " AND p.estimated_value >= ?"; p.append(min_value)
        if days: sql += " AND p.future_notice_date <= datetime('now', '+{} days')".format(int(days))
        sql += " ORDER BY CASE WHEN p.future_notice_date IS NOT NULL THEN p.future_notice_date ELSE p.engagement_deadline END ASC LIMIT 200"
        rows = [
            {"buyer": r["buyer_name"], "org_type": r["org_type"], "title": r["title"],
             "estimated_value": r["estimated_value"],
             "engagement_deadline": r["engagement_deadline"],
             "future_notice_date": r["future_notice_date"],
             "notice_url": r["notice_url"], "description": r["description"]}
            for r in conn.execute(sql, p).fetchall()
        ]
        return {"count": len(rows), "notices": rows}
    finally:
        conn.close()


def api_pwin(params):
    buyer = params.get("buyer", [""])[0]
    category = params.get("category", [""])[0]
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        sql = "SELECT * FROM v_pwin_signals WHERE 1=1"
        p = []
        if buyer: sql += " AND LOWER(buyer_name) LIKE LOWER(?)"; p.append(f"%{buyer}%")
        if category: sql += " AND LOWER(main_category) LIKE LOWER(?)"; p.append(f"%{category}%")
        sql += " LIMIT 100"
        rows = [
            {"buyer": r["buyer_name"], "category": r["main_category"],
             "awards": r["awards_count"],
             "avg_bids": r["avg_bids_per_tender"],
             "avg_value": r["avg_award_value"],
             "methods": {
                 "open": r["open_awards"] or 0,
                 "limited": r["limited_awards"] or 0,
                 "direct": r["direct_awards"] or 0,
                 "selective": r["selective_awards"] or 0,
             }}
            for r in conn.execute(sql, p).fetchall()
        ]
        return {"count": len(rows), "signals": rows}
    finally:
        conn.close()


def api_service_categories():
    """Return the list of service categories and their award counts."""
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        rows = conn.execute("""
            SELECT n.service_category, COUNT(DISTINCT a.id) AS awards,
                   SUM(a.value_amount_gross) AS total_value
            FROM notices n JOIN awards a ON a.ocid = n.ocid
            WHERE a.status IN ('active','pending') AND n.service_category IS NOT NULL
              AND a.value_amount_gross >= 1e6
            GROUP BY n.service_category ORDER BY awards DESC
        """).fetchall()
        return {"categories": [
            {"id": r["service_category"], "awards": r["awards"], "total_value": r["total_value"]}
            for r in rows
        ]}
    finally:
        conn.close()


def api_expiry_categories():
    """Return distinct main_category values present in the expiry pipeline."""
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        rows = conn.execute("""
            SELECT main_category, COUNT(*) AS awards
            FROM v_expiring_contracts
            WHERE main_category IS NOT NULL
            GROUP BY main_category
            ORDER BY awards DESC
        """).fetchall()
        return {"categories": [{"id": r["main_category"], "awards": r["awards"]} for r in rows]}
    finally:
        conn.close()


def api_search(params):
    """Three-dimension bid-director search: service × buyer × value."""
    service = params.get("service", [""])[0]
    buyer = params.get("buyer", [""])[0]
    min_value = float(params.get("minValue", ["1000000"])[0])
    limit = int(params.get("limit", ["100"])[0])
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        sql = """
            SELECT n.title, n.service_category,
                   COALESCE(cb.canonical_name, b.name) AS buyer_name,
                   cb.type AS buyer_type,
                   GROUP_CONCAT(DISTINCT s.name) AS suppliers,
                   a.value_amount_gross, a.award_date,
                   a.contract_start_date, a.contract_end_date,
                   n.procurement_method_detail, n.notice_url,
                   n.is_framework
            FROM notices n
            JOIN awards a ON a.ocid = n.ocid
            JOIN buyers b ON n.buyer_id = b.id
            LEFT JOIN canonical_buyers cb ON b.canonical_id = cb.canonical_id
            LEFT JOIN award_suppliers asup ON a.id = asup.award_id
            LEFT JOIN suppliers s ON asup.supplier_id = s.id
            WHERE a.status IN ('active','pending')
              AND a.value_amount_gross >= ?
        """
        p = [min_value]

        if service:
            sql += " AND n.service_category = ?"
            p.append(service)

        if buyer:
            # Search canonical name OR raw buyer name, with hierarchy traversal
            sql += """ AND (
                b.canonical_id IN (
                    WITH RECURSIVE descendants AS (
                        SELECT canonical_id FROM canonical_buyers
                        WHERE LOWER(canonical_name) LIKE LOWER(?)
                        UNION ALL
                        SELECT cb2.canonical_id FROM canonical_buyers cb2
                        JOIN descendants d ON cb2.parent_canonical_id = d.canonical_id
                    )
                    SELECT canonical_id FROM descendants
                )
                OR LOWER(b.name) LIKE LOWER(?)
            )"""
            p.extend([f"%{buyer}%", f"%{buyer}%"])

        sql += " GROUP BY a.id ORDER BY a.value_amount_gross DESC LIMIT ?"
        p.append(limit)

        rows = conn.execute(sql, p).fetchall()

        results = [{
            "title": r["title"],
            "service": r["service_category"],
            "buyer": r["buyer_name"],
            "buyer_type": r["buyer_type"],
            "suppliers": r["suppliers"],
            "value": r["value_amount_gross"],
            "award_date": r["award_date"],
            "start_date": r["contract_start_date"],
            "end_date": r["contract_end_date"],
            "method": r["procurement_method_detail"],
            "notice_url": r["notice_url"],
            "is_framework": bool(r["is_framework"]),
        } for r in rows]

        return {"count": len(results), "awards": results}
    finally:
        conn.close()


# ── HTTP Server ───────────────────────────────────────────────────────────

ROUTES = {
    "/api/summary": lambda p: api_summary(),
    "/api/buyer": api_buyer,
    "/api/supplier": api_supplier,
    "/api/expiring": api_expiring,
    "/api/pipeline": api_pipeline,
    "/api/pwin": api_pwin,
    "/api/categories": lambda p: api_service_categories(),
    "/api/expiry-categories": lambda p: api_expiry_categories(),
    "/api/search": api_search,
}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        handler = ROUTES.get(parsed.path)
        if handler:
            try:
                result = handler(params)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result, default=str).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            super().do_GET()

    def log_message(self, format, *args):
        if "/api/" in str(args[0]):
            sys.stderr.write(f"  API  {args[0]}\n")


def main():
    parser = argparse.ArgumentParser(description="PWIN Competitive Intelligence data server")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = HTTPServer(("0.0.0.0", args.port), Handler)
    print(f"\n  PWIN Competitive Intelligence")
    print(f"  Dashboard: http://localhost:{args.port}/dashboard.html")
    print(f"  API:       http://localhost:{args.port}/api/summary")
    print(f"  Database:  {DB_PATH}")
    print(f"  {'Database found' if DB_PATH.exists() else 'WARNING: Database not found — run agent/ingest.py first'}")
    print(f"\n  Press Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
