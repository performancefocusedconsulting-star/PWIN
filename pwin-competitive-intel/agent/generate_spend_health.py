"""
Generate a Markdown health summary for the £25k spend transparency ingest.

Returns a string ready to append to the nightly digest, or prints it when
run directly.
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

AGENT_DIR   = Path(__file__).parent
DB_PATH     = AGENT_DIR.parent / "db" / "bid_intel.db"


def generate(conn: sqlite3.Connection | None = None) -> str:
    """Return a Markdown section summarising spend ingest health."""
    close = False
    if conn is None:
        if not DB_PATH.exists():
            return ""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        close = True

    try:
        # Check tables exist
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        if "spend_files_state" not in tables or "spend_transactions" not in tables:
            return ""

        # File-level status summary
        file_stats = conn.execute("""
            SELECT status, COUNT(*) AS n
            FROM spend_files_state
            GROUP BY status
        """).fetchall()
        by_status = {r["status"]: r["n"] for r in file_stats}

        total_files   = sum(by_status.values())
        loaded_files  = by_status.get("loaded", 0)
        pending_files = by_status.get("pending", 0)
        error_files   = by_status.get("error", 0)

        # Transaction-level summary
        tx_stats = conn.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(canonical_sub_org_id) AS sub_org_matched,
                COUNT(canonical_supplier_id) AS supplier_matched,
                SUM(amount) AS total_amount,
                MIN(payment_date) AS earliest,
                MAX(payment_date) AS latest
            FROM spend_transactions
        """).fetchone()

        total_rows     = tx_stats["total_rows"] or 0
        sub_matched    = tx_stats["sub_org_matched"] or 0
        sup_matched    = tx_stats["supplier_matched"] or 0
        total_amount   = tx_stats["total_amount"] or 0
        earliest       = tx_stats["earliest"] or "—"
        latest         = tx_stats["latest"] or "—"

        sub_pct = round(100 * sub_matched / total_rows) if total_rows else 0
        sup_pct = round(100 * sup_matched / total_rows) if total_rows else 0

        # Errors
        errors = conn.execute("""
            SELECT source_url, error_message FROM spend_files_state
            WHERE status = 'error' LIMIT 5
        """).fetchall()

    finally:
        if close:
            conn.close()

    lines = [
        "",
        "## Spend transparency ingest health",
        f"_Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC_",
        "",
        f"**Files:** {loaded_files}/{total_files} loaded"
        + (f", {pending_files} pending" if pending_files else "")
        + (f", **{error_files} errors**" if error_files else ""),
        f"**Rows:** {total_rows:,} payment rows | "
        f"Total: £{total_amount:,.0f} | "
        f"Date range: {earliest} → {latest}",
        f"**Canonicalisation:** sub-org {sub_pct}% matched | "
        f"supplier {sup_pct}% matched",
    ]

    if errors:
        lines.append("")
        lines.append("**Download errors:**")
        for e in errors:
            lines.append(f"- `{e['source_url']}`: {e['error_message']}")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(generate())
