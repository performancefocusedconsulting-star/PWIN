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
    """
    Return {norm(name) → canonical_id} covering every known supplier name variant.
    Joins the 287k raw supplier name records via supplier_to_canonical so all
    aliases (not just the chosen canonical name) resolve to the canonical entity.
    Falls back to canonical_suppliers.canonical_name to cover canonicals with
    no raw supplier rows.
    """
    index: dict[str, str] = {}
    # Raw name variants → canonical
    for name, canonical_id in conn.execute(
        "SELECT s.name, m.canonical_id "
        "FROM suppliers s "
        "JOIN supplier_to_canonical m ON m.supplier_id = s.id"
    ):
        key = _norm(name)
        if key and key not in index:
            index[key] = canonical_id
    # Add canonical names themselves (covers any canonicals with no raw rows)
    for canonical_id, canonical_name in conn.execute(
        "SELECT canonical_id, canonical_name FROM canonical_suppliers"
    ):
        key = _norm(canonical_name)
        if key and key not in index:
            index[key] = canonical_id
    return index


# ── Matching ─────────────────────────────────────────────────────────────────

def _match_buyer(raw_entity: str, buyer_index: dict) -> str | None:
    if not raw_entity:
        return None
    result = buyer_index.get(_norm(raw_entity))
    if result:
        return result
    # Strip leading internal code prefix e.g. "UKBF - UK Border Force" → "UK Border Force"
    stripped = re.sub(r"^[A-Z][A-Za-z0-9]+ - ", "", raw_entity)
    if stripped != raw_entity:
        result = buyer_index.get(_norm(stripped))
    return result


def _match_supplier(raw_supplier: str, supplier_index: dict) -> str | None:
    if not raw_supplier:
        return None
    return supplier_index.get(_norm(raw_supplier))


# Recipients that are not procurement suppliers — councils, agencies, foreign
# governments, public bodies receiving grants or transfer payments. These will
# never live in the canonical supplier table and shouldn't dilute match-rate
# diagnostics.
_PUBLIC_BODY_PATTERNS = re.compile(
    r"\b("
    r"council|borough|metro(politan)? (?:borough|council)|"
    r"county council|district council|city council|town council|parish council|"
    r"london borough|"
    r"government(?!\s+gateway)|"
    r"hm revenue|hmrc|hm treasury|"
    r"student loans company|"
    r"national health service|nhs (?:trust|england|scotland|wales)|"
    r"department for|department of|ministry of|"
    r"police (?:and crime commissioner|authority|force|service)|"
    r"fire (?:and rescue|authority)|"
    r"crown commercial service|"
    r"environment agency|"
    r"the (?:university|college) of|university of|"
    r"chief constable|"
    r"foreign(?:,| and) commonwealth"
    r")\b",
    re.IGNORECASE,
)


def _classify_recipient(raw_supplier: str) -> str:
    """Return 'public_body' for grants/transfers, else 'supplier'."""
    if raw_supplier and _PUBLIC_BODY_PATTERNS.search(raw_supplier):
        return "public_body"
    return "supplier"


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

    # Rows where canonicalisation is incomplete (recipient_type NULL means
    # the row hasn't been through this pipeline yet)
    rows = conn.execute(
        "SELECT id, raw_entity, raw_supplier_name "
        "FROM spend_transactions "
        "WHERE canonical_sub_org_id IS NULL OR canonical_supplier_id IS NULL "
        "OR recipient_type IS NULL"
    ).fetchall()

    log.info("%d spend_transactions rows to canonicalise", len(rows))

    buyer_hits = buyer_miss = sup_hits = sup_miss = 0
    public_body_count = procurement_count = 0

    for row in rows:
        sub_org_id     = _match_buyer(row["raw_entity"], buyer_index)
        supplier_id    = _match_supplier(row["raw_supplier_name"], supplier_index)
        recipient_type = _classify_recipient(row["raw_supplier_name"])

        if sub_org_id:
            buyer_hits += 1
        else:
            buyer_miss += 1

        if recipient_type == "public_body":
            public_body_count += 1
        else:
            procurement_count += 1
            if supplier_id:
                sup_hits += 1
            else:
                sup_miss += 1

        conn.execute(
            "UPDATE spend_transactions "
            "SET canonical_sub_org_id=?, canonical_supplier_id=?, recipient_type=? "
            "WHERE id=?",
            (sub_org_id, supplier_id, recipient_type, row["id"])
        )

    conn.commit()

    log.info(
        "Sub-org: %d matched / %d unmatched",
        buyer_hits, buyer_miss
    )
    log.info(
        "Recipient: %d procurement / %d public-body transfers",
        procurement_count, public_body_count
    )
    if procurement_count:
        pct = round(100 * sup_hits / procurement_count)
        log.info(
            "Supplier (procurement only): %d matched / %d unmatched (%d%%)",
            sup_hits, sup_miss, pct
        )

    if close_after:
        conn.close()


if __name__ == "__main__":
    sys.path.insert(0, str(AGENT_DIR))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
