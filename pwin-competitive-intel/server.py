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


# ── API handlers ──────────────────────────────────────────────────────────

def api_summary():
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        tables = ["buyers", "suppliers", "notices", "lots", "awards", "award_suppliers", "cpv_codes", "planning_notices"]
        counts = {}
        for t in tables:
            counts[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]

        cursor = conn.execute("SELECT value FROM ingest_state WHERE key='last_cursor'").fetchone()
        val = conn.execute("SELECT SUM(value_amount_gross) as total, AVG(value_amount_gross) as avg, MAX(value_amount_gross) as mx FROM awards WHERE value_amount_gross IS NOT NULL").fetchone()

        top_cpv = dict_rows(conn.execute("""
            SELECT code, description, COUNT(*) AS cnt
            FROM cpv_codes GROUP BY code ORDER BY cnt DESC LIMIT 15
        """).fetchall())

        methods = dict_rows(conn.execute("""
            SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
            FROM awards a JOIN notices n ON a.ocid = n.ocid
            WHERE a.status IN ('active', 'pending')
            GROUP BY n.procurement_method ORDER BY cnt DESC
        """).fetchall())

        return {
            "tables": counts,
            "lastCursor": cursor[0] if cursor else None,
            "totalValue": val[0], "avgValue": val[1], "maxValue": val[2],
            "topCpv": top_cpv,
            "procurementMethods": methods,
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
        buyers = dict_rows(conn.execute("""
            SELECT id, name, org_type, region_code FROM buyers
            WHERE LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 10
        """, (f"%{name}%",)).fetchall())

        if not buyers: return {"buyers": [], "message": f"No buyers matching '{name}'"}

        results = []
        for buyer in buyers:
            stats = dict(conn.execute("""
                SELECT COUNT(DISTINCT a.id) AS total_awards, COUNT(DISTINCT n.ocid) AS total_notices,
                       SUM(a.value_amount_gross) AS total_spend, AVG(a.value_amount_gross) AS avg_value,
                       MAX(a.value_amount_gross) AS max_value, AVG(n.total_bids) AS avg_bids
                FROM awards a JOIN notices n ON a.ocid = n.ocid
                WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
            """, (buyer["id"],)).fetchone())

            methods = dict_rows(conn.execute("""
                SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
                FROM awards a JOIN notices n ON a.ocid = n.ocid
                WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
                GROUP BY n.procurement_method ORDER BY cnt DESC
            """, (buyer["id"],)).fetchall())

            top_suppliers = dict_rows(conn.execute("""
                SELECT s.name, COUNT(DISTINCT a.id) AS wins, SUM(a.value_amount_gross) AS total_value
                FROM award_suppliers asup
                JOIN suppliers s ON asup.supplier_id = s.id
                JOIN awards a ON asup.award_id = a.id
                JOIN notices n ON a.ocid = n.ocid
                WHERE n.buyer_id = ?
                GROUP BY s.id ORDER BY wins DESC, total_value DESC LIMIT 15
            """, (buyer["id"],)).fetchall())

            recent = dict_rows(conn.execute("""
                SELECT n.title, a.value_amount_gross, n.procurement_method,
                       GROUP_CONCAT(DISTINCT s.name) AS suppliers,
                       a.contract_end_date, a.award_date
                FROM awards a
                JOIN notices n ON a.ocid = n.ocid
                LEFT JOIN award_suppliers asup ON a.id = asup.award_id
                LEFT JOIN suppliers s ON asup.supplier_id = s.id
                WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
                GROUP BY a.id ORDER BY a.award_date DESC NULLS LAST LIMIT ?
            """, (buyer["id"], limit)).fetchall())

            results.append({
                **buyer, "stats": stats, "procurementMethods": methods,
                "topSuppliers": top_suppliers, "recentAwards": recent,
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
        suppliers = dict_rows(conn.execute("""
            SELECT id, name, scale, is_vcse, companies_house_no FROM suppliers
            WHERE LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 10
        """, (f"%{name}%",)).fetchall())

        if not suppliers: return {"suppliers": [], "message": f"No suppliers matching '{name}'"}

        results = []
        for sup in suppliers:
            stats = dict(conn.execute("""
                SELECT COUNT(DISTINCT a.id) AS total_wins, SUM(a.value_amount_gross) AS total_value,
                       AVG(a.value_amount_gross) AS avg_value, MAX(a.value_amount_gross) AS max_value,
                       MIN(a.award_date) AS first_win, MAX(a.award_date) AS last_win
                FROM award_suppliers asup JOIN awards a ON asup.award_id = a.id
                WHERE asup.supplier_id = ?
            """, (sup["id"],)).fetchone())

            buyer_rels = dict_rows(conn.execute("""
                SELECT b.name, COUNT(DISTINCT a.id) AS awards,
                       SUM(a.value_amount_gross) AS total_value,
                       MAX(a.contract_end_date) AS latest_expiry
                FROM award_suppliers asup
                JOIN awards a ON asup.award_id = a.id
                JOIN notices n ON a.ocid = n.ocid
                JOIN buyers b ON n.buyer_id = b.id
                WHERE asup.supplier_id = ?
                GROUP BY b.id ORDER BY awards DESC LIMIT 15
            """, (sup["id"],)).fetchall())

            active = dict_rows(conn.execute("""
                SELECT n.title, b.name AS buyer, a.value_amount_gross,
                       a.contract_end_date, a.contract_max_extend
                FROM award_suppliers asup
                JOIN awards a ON asup.award_id = a.id
                JOIN notices n ON a.ocid = n.ocid
                JOIN buyers b ON n.buyer_id = b.id
                WHERE asup.supplier_id = ? AND a.contract_end_date > datetime('now')
                ORDER BY a.contract_end_date ASC LIMIT 20
            """, (sup["id"],)).fetchall())

            results.append({**sup, "stats": stats, "buyerRelationships": buyer_rels, "activeContracts": active})

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
        rows = dict_rows(conn.execute(sql, p).fetchall())
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
        rows = dict_rows(conn.execute(sql, p).fetchall())
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
        rows = dict_rows(conn.execute(sql, p).fetchall())
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
                # Handlers that don't need params get called differently
                if parsed.path == "/api/summary":
                    result = handler(params)
                else:
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
            # Serve static files (dashboard.html etc.)
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
