"""
Match spend_transactions rows to canonical buyers and canonical suppliers.

Updates canonical_sub_org_id and canonical_supplier_id in place.
Idempotent — already-matched rows are skipped.
Unmatched rows stay NULL; they are stored but excluded from rendered output.
"""
import logging
import re
import sqlite3
import sys
from pathlib import Path

log = logging.getLogger(__name__)

AGENT_DIR   = Path(__file__).parent
DB_PATH     = AGENT_DIR.parent / "db" / "bid_intel.db"
SCHEMA_PATH = AGENT_DIR.parent / "db" / "schema.sql"

# ── Normaliser (mirrors load-canonical-buyers.py::norm exactly) ──────────────

def _norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"\s*[\&]\s*", " and ", s)
    s = re.sub(r"\bplc\b\.?", "limited", s)
    s = re.sub(r"\bltd\b\.?", "limited", s)
    s = re.sub(r"^the\s+", "", s)
    s = re.sub(r"\s+company\s+limited\s*$", "", s)
    s = re.sub(r"\s+[-–—]\s+(e[- ]?tendering(?:\s+system)?|tendering\s+system|portal|esourcing|procurement\s+department|procurement\s+services?).*$", "", s)
    s = re.sub(r"\s+e[- ]?tendering(?:\s+system|\s+portal)?\s*$", "", s)
    s = re.sub(r"\s+network\s+e[- ]?tendering(?:\s+portal)?\s*$", "", s)
    s = re.sub(r"[,\.\(\)\-\'\"]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ── Lookup tables ────────────────────────────────────────────────────────────

def _build_buyer_index(conn: sqlite3.Connection) -> dict[str, str]:
    """Return {alias_norm → canonical_id} from canonical_buyer_aliases."""
    rows = conn.execute("SELECT alias_norm, canonical_id FROM canonical_buyer_aliases").fetchall()
    return {r[0]: r[1] for r in rows}


def _build_supplier_index(conn: sqlite3.Connection) -> dict[str, str]:
    """Return {norm(canonical_name) → canonical_id} from canonical_suppliers."""
    rows = conn.execute("SELECT canonical_id, canonical_name FROM canonical_suppliers").fetchall()
    return {_norm(r[1]): r[0] for r in rows}


# ── Matching ─────────────────────────────────────────────────────────────────

def _match_buyer(raw_entity: str, buyer_index: dict) -> str | None:
    if not raw_entity:
        return None
    return buyer_index.get(_norm(raw_entity))


def _match_supplier(raw_supplier: str, supplier_index: dict) -> str | None:
    if not raw_supplier:
        return None
    return supplier_index.get(_norm(raw_supplier))


# ── Main ─────────────────────────────────────────────────────────────────────

def run(conn: sqlite3.Connection | None = None, close_after: bool = True) -> None:
    if conn is None:
        import db_utils
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        db_utils.init_schema(conn, SCHEMA_PATH)

    buyer_index    = _build_buyer_index(conn)
    supplier_index = _build_supplier_index(conn)
    log.info("Buyer index: %d aliases | Supplier index: %d names",
             len(buyer_index), len(supplier_index))

    # Rows where at least one canonical column is still NULL
    rows = conn.execute(
        "SELECT id, raw_entity, raw_supplier_name "
        "FROM spend_transactions "
        "WHERE canonical_sub_org_id IS NULL OR canonical_supplier_id IS NULL"
    ).fetchall()

    log.info("%d spend_transactions rows to canonicalise", len(rows))

    buyer_hits = buyer_miss = sup_hits = sup_miss = 0

    for row in rows:
        sub_org_id  = _match_buyer(row["raw_entity"], buyer_index)
        supplier_id = _match_supplier(row["raw_supplier_name"], supplier_index)

        if sub_org_id:
            buyer_hits += 1
        else:
            buyer_miss += 1

        if supplier_id:
            sup_hits += 1
        else:
            sup_miss += 1

        conn.execute(
            "UPDATE spend_transactions "
            "SET canonical_sub_org_id=?, canonical_supplier_id=? WHERE id=?",
            (sub_org_id, supplier_id, row["id"])
        )

    conn.commit()

    log.info(
        "Sub-org: %d matched / %d unmatched | Supplier: %d matched / %d unmatched",
        buyer_hits, buyer_miss, sup_hits, sup_miss
    )

    if close_after:
        conn.close()


if __name__ == "__main__":
    sys.path.insert(0, str(AGENT_DIR))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
