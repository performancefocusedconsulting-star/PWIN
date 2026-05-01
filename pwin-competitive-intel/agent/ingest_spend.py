"""
Orchestrate the £25k spend transparency ingest pipeline.

Steps:
  1. Download any pending files from the catalogue (fetch_spend)
  2. Parse downloaded files and write rows to spend_transactions (this file)
  3. Canonicalise raw entity + supplier names (canonicalise_spend)

Idempotent — files with status='loaded' are skipped. Re-run after adding
new entries to spend-catalogue.json or after a download failure is resolved.
"""
import hashlib
import logging
import sqlite3
import sys
from pathlib import Path

log = logging.getLogger(__name__)

AGENT_DIR   = Path(__file__).parent
DB_PATH     = AGENT_DIR.parent / "db" / "bid_intel.db"
SCHEMA_PATH = AGENT_DIR.parent / "db" / "schema.sql"
CATALOGUE   = AGENT_DIR / "spend-catalogue.json"


def _open_db() -> sqlite3.Connection:
    sys.path.insert(0, str(AGENT_DIR))
    import db_utils
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    db_utils.init_schema(conn, SCHEMA_PATH)
    return conn


def _ingest_file(conn: sqlite3.Connection, file_row: sqlite3.Row) -> int:
    """
    Parse one downloaded spend file and upsert its rows into spend_transactions.
    Returns the number of rows written.
    """
    from parse_spend import parse_file

    local_path = Path(file_row["local_path"])
    format_id  = file_row["format_id"]
    file_id    = file_row["id"]
    dept       = file_row["department"]
    entity_override = file_row["entity_override"]

    rows_written = 0
    for idx, row in enumerate(parse_file(local_path, format_id)):
        # For MoJ streams the raw_entity comes from entity_override in the catalogue
        raw_entity = entity_override if entity_override else row.get("raw_entity", "")

        tx_id = f"{file_id}-{idx:06d}"
        try:
            amount = float(row["amount"].replace(",", ""))
        except (ValueError, AttributeError):
            log.debug("Skipping row %d in %s — unparseable amount: %r", idx, local_path, row.get("amount"))
            continue

        conn.execute(
            "INSERT OR IGNORE INTO spend_transactions "
            "(id, source_file_id, department_family, raw_entity, raw_supplier_name, "
            " amount, payment_date, expense_type, expense_area) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (tx_id, file_id, dept, raw_entity,
             row.get("raw_supplier_name", ""),
             amount,
             row.get("payment_date"),
             row.get("expense_type"),
             row.get("expense_area"))
        )
        rows_written += 1

    conn.commit()
    return rows_written


def run() -> None:
    sys.path.insert(0, str(AGENT_DIR))
    import fetch_spend
    import canonicalise_spend

    # Step 1 — download pending files
    log.info("Step 1: downloading pending spend files")
    fetch_spend.run()

    conn = _open_db()

    # Step 2 — parse downloaded files
    log.info("Step 2: parsing downloaded files into spend_transactions")
    downloaded = conn.execute(
        "SELECT * FROM spend_files_state WHERE status='downloaded'"
    ).fetchall()
    log.info("%d files ready to parse", len(downloaded))

    for file_row in downloaded:
        try:
            n = _ingest_file(conn, file_row)
            conn.execute(
                "UPDATE spend_files_state SET status='loaded', row_count=? WHERE id=?",
                (n, file_row["id"])
            )
            conn.commit()
            log.info("Parsed %s → %d rows", file_row["source_url"], n)
        except Exception as exc:
            conn.execute(
                "UPDATE spend_files_state SET status='error', error_message=? WHERE id=?",
                (str(exc), file_row["id"])
            )
            conn.commit()
            log.error("Failed to parse %s: %s", file_row["source_url"], exc)

    # Step 3 — canonicalise
    log.info("Step 3: canonicalising entity and supplier names")
    canonicalise_spend.run(conn=conn, close_after=True)

    log.info("Spend ingest complete")


if __name__ == "__main__":
    sys.path.insert(0, str(AGENT_DIR))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
