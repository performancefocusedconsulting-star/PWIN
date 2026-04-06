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
                    SELECT s.name, COUNT(DISTINCT a.id) AS wins, SUM(a.value_amount_gross) AS total_value
                    FROM award_suppliers asup
                    JOIN suppliers s ON asup.supplier_id = s.id
                    JOIN awards a ON asup.award_id = a.id
                    JOIN notices n ON a.ocid = n.ocid
                    WHERE n.buyer_id = ?
                    GROUP BY s.id ORDER BY wins DESC, total_value DESC LIMIT 15
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
        suppliers = conn.execute("""
            SELECT id, name, scale, is_vcse, companies_house_no FROM suppliers
            WHERE LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 10
        """, (f"%{name}%",)).fetchall()

        if not suppliers: return {"suppliers": [], "message": f"No suppliers matching '{name}'"}

        results = []
        for sup in suppliers:
            stats = conn.execute("""
                SELECT COUNT(DISTINCT a.id) AS total_wins, SUM(a.value_amount_gross) AS total_value,
                       AVG(a.value_amount_gross) AS avg_value, MAX(a.value_amount_gross) AS max_value,
                       MIN(a.award_date) AS first_win, MAX(a.award_date) AS last_win
                FROM award_suppliers asup JOIN awards a ON asup.award_id = a.id
                WHERE asup.supplier_id = ?
            """, (sup["id"],)).fetchone()

            buyer_rels = [
                {"name": r["name"], "awards": r["awards"], "value": r["total_value"]}
                for r in conn.execute("""
                    SELECT b.name, COUNT(DISTINCT a.id) AS awards,
                           SUM(a.value_amount_gross) AS total_value
                    FROM award_suppliers asup
                    JOIN awards a ON asup.award_id = a.id
                    JOIN notices n ON a.ocid = n.ocid
                    JOIN buyers b ON n.buyer_id = b.id
                    WHERE asup.supplier_id = ?
                    GROUP BY b.id ORDER BY awards DESC LIMIT 15
                """, (sup["id"],)).fetchall()
            ]

            active = [
                {"title": r["title"], "buyer": r["buyer"], "value": r["value_amount_gross"],
                 "end_date": r["contract_end_date"], "max_extend": r["contract_max_extend"]}
                for r in conn.execute("""
                    SELECT n.title, b.name AS buyer, a.value_amount_gross,
                           a.contract_end_date, a.contract_max_extend
                    FROM award_suppliers asup
                    JOIN awards a ON asup.award_id = a.id
                    JOIN notices n ON a.ocid = n.ocid
                    JOIN buyers b ON n.buyer_id = b.id
                    WHERE asup.supplier_id = ? AND a.contract_end_date > datetime('now')
                    ORDER BY a.contract_end_date ASC LIMIT 20
                """, (sup["id"],)).fetchall()
            ]

            results.append({
                "name": sup["name"],
                "scale": sup["scale"],
                "is_vcse": bool(sup["is_vcse"]),
                "companies_house_no": sup["companies_house_no"],
                "wins": stats["total_wins"],
                "total_value": stats["total_value"],
                "avg_value": stats["avg_value"],
                "first_win": stats["first_win"],
                "last_win": stats["last_win"],
                "buyers": buyer_rels,
                "active_contracts": active,
            })

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
        sql += " ORDER BY CASE WHEN p.future_notice_date IS NOT NULL THEN p.future_notice_date ELSE p.engagement_deadline END ASC LIMIT 200"
        rows = [
            {"buyer": r["buyer_name"], "title": r["title"],
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


# ── HTTP Server ───────────────────────────────────────────────────────────

ROUTES = {
    "/api/summary": lambda p: api_summary(),
    "/api/buyer": api_buyer,
    "/api/supplier": api_supplier,
    "/api/expiring": api_expiring,
    "/api/pipeline": api_pipeline,
    "/api/pwin": api_pwin,
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
