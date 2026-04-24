"""
PWIN Competitive Intelligence — Shared database utilities
=========================================================
Common get_db / init_schema / upsert row primitives shared by
ingest.py (FTS) and ingest_cf.py (Contracts Finder).
"""

import logging
import sqlite3
from pathlib import Path

log = logging.getLogger(__name__)


def get_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _migrate_schema(conn: sqlite3.Connection):
    """Add columns appended to schema.sql after DB first created. Idempotent."""
    def _columns(table):
        return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}

    # ── notices: framework fields (Decision C06, 2026-04-12) ──
    notices_cols = _columns("notices")
    for col, typedef in [
        ("is_framework",           "INTEGER DEFAULT 0"),
        ("framework_method",       "TEXT"),
        ("framework_type",         "TEXT"),
        ("parent_framework_ocid",  "TEXT"),
        ("parent_framework_title", "TEXT"),
    ]:
        if col not in notices_cols:
            conn.execute(f"ALTER TABLE notices ADD COLUMN {col} {typedef}")
            log.info("Migrated notices: added column %s", col)

    # ── awards: value_quality flag (2026-04) ──
    awards_cols = _columns("awards")
    if awards_cols and "value_quality" not in awards_cols:
        conn.execute("ALTER TABLE awards ADD COLUMN value_quality TEXT")
        log.info("Migrated awards: added column value_quality")

    # ── data_source: multi-source tag (2026-04-24) ──
    for table in ("notices", "awards", "buyers", "suppliers"):
        cols = _columns(table)
        if "data_source" not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN data_source TEXT DEFAULT 'fts'")
            log.info("Migrated %s: added column data_source", table)

    # ── notices: CF SME suitability flag (2026-04-24) ──
    if "suitable_for_sme" not in _columns("notices"):
        conn.execute("ALTER TABLE notices ADD COLUMN suitable_for_sme INTEGER DEFAULT 0")
        log.info("Migrated notices: added column suitable_for_sme")

    conn.commit()


def init_schema(conn: sqlite3.Connection, schema_path: Path):
    try:
        _migrate_schema(conn)
    except Exception:
        pass  # tables don't exist yet — CREATE TABLE IF NOT EXISTS handles it
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    conn.commit()
    log.info("Schema initialised")


# ── Ingest state ─────────────────────────────────────────────────────────────

def get_ingest_state(conn: sqlite3.Connection, key: str) -> str:
    row = conn.execute(
        "SELECT value FROM ingest_state WHERE key=?", (key,)
    ).fetchone()
    return row["value"] if row and row["value"] else ""


def set_ingest_state(conn: sqlite3.Connection, key: str, value: str):
    conn.execute(
        "INSERT OR REPLACE INTO ingest_state (key, value, updated) VALUES (?, ?, datetime('now'))",
        (key, value),
    )
    conn.commit()


def clear_ingest_state(conn: sqlite3.Connection, key: str):
    conn.execute("DELETE FROM ingest_state WHERE key=?", (key,))
    conn.commit()


# ── Upsert row primitives ─────────────────────────────────────────────────────
# All functions accept a dict whose keys match column names.
# Missing keys default to None (or the column's SQL DEFAULT).

def upsert_buyer_row(conn: sqlite3.Connection, row: dict):
    r = {"org_type": None, "devolved_region": None, "street_address": None,
         "locality": None, "postal_code": None, "region_code": None,
         "contact_name": None, "contact_email": None, "contact_telephone": None,
         "website": None, "data_source": "fts", **row}
    conn.execute("""
        INSERT INTO buyers (id, name, org_type, devolved_region, street_address, locality,
            postal_code, region_code, contact_name, contact_email, contact_telephone,
            website, data_source, last_updated)
        VALUES (:id, :name, :org_type, :devolved_region, :street_address, :locality,
            :postal_code, :region_code, :contact_name, :contact_email, :contact_telephone,
            :website, :data_source, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            org_type=COALESCE(excluded.org_type, org_type),
            devolved_region=COALESCE(excluded.devolved_region, devolved_region),
            street_address=COALESCE(excluded.street_address, street_address),
            locality=COALESCE(excluded.locality, locality),
            postal_code=COALESCE(excluded.postal_code, postal_code),
            region_code=COALESCE(excluded.region_code, region_code),
            contact_name=COALESCE(excluded.contact_name, contact_name),
            contact_email=COALESCE(excluded.contact_email, contact_email),
            contact_telephone=COALESCE(excluded.contact_telephone, contact_telephone),
            website=COALESCE(excluded.website, website),
            data_source=excluded.data_source,
            last_updated=datetime('now')
    """, r)


def upsert_supplier_row(conn: sqlite3.Connection, row: dict) -> str:
    r = {"companies_house_no": None, "scale": None, "is_vcse": 0,
         "is_sheltered": 0, "is_public_mission": 0, "street_address": None,
         "locality": None, "postal_code": None, "region_code": None,
         "contact_email": None, "website": None, "data_source": "fts", **row}
    conn.execute("""
        INSERT INTO suppliers (id, name, companies_house_no, scale, is_vcse, is_sheltered,
            is_public_mission, street_address, locality, postal_code, region_code,
            contact_email, website, data_source, last_updated)
        VALUES (:id, :name, :companies_house_no, :scale, :is_vcse, :is_sheltered,
            :is_public_mission, :street_address, :locality, :postal_code, :region_code,
            :contact_email, :website, :data_source, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            companies_house_no=COALESCE(excluded.companies_house_no, companies_house_no),
            scale=COALESCE(excluded.scale, scale),
            is_vcse=COALESCE(excluded.is_vcse, is_vcse),
            is_sheltered=COALESCE(excluded.is_sheltered, is_sheltered),
            is_public_mission=COALESCE(excluded.is_public_mission, is_public_mission),
            street_address=COALESCE(excluded.street_address, street_address),
            locality=COALESCE(excluded.locality, locality),
            postal_code=COALESCE(excluded.postal_code, postal_code),
            region_code=COALESCE(excluded.region_code, region_code),
            contact_email=COALESCE(excluded.contact_email, contact_email),
            website=COALESCE(excluded.website, website),
            data_source=excluded.data_source,
            last_updated=datetime('now')
    """, r)
    return row["id"]


def upsert_notice_row(conn: sqlite3.Connection, row: dict):
    r = {"latest_release_id": None, "title": None, "description": None,
         "procurement_method": None, "procurement_method_detail": None,
         "main_category": None, "legal_basis": None, "above_threshold": 0,
         "value_amount": None, "value_amount_gross": None, "currency": "GBP",
         "tender_end_date": None, "published_date": None, "tender_status": None,
         "total_bids": None, "final_stage_bids": None, "sme_bids": None, "vcse_bids": None,
         "has_renewal": 0, "renewal_description": None,
         "notice_type": None, "notice_url": None, "latest_tag": None,
         "is_framework": 0, "framework_method": None, "framework_type": None,
         "parent_framework_ocid": None, "parent_framework_title": None,
         "data_source": "fts", "suitable_for_sme": 0, **row}
    conn.execute("""
        INSERT INTO notices (
            ocid, buyer_id, latest_release_id, title, description,
            procurement_method, procurement_method_detail, main_category,
            legal_basis, above_threshold, value_amount, value_amount_gross, currency,
            tender_end_date, published_date, tender_status,
            total_bids, final_stage_bids, sme_bids, vcse_bids,
            has_renewal, renewal_description, notice_type, notice_url, latest_tag,
            is_framework, framework_method, framework_type,
            parent_framework_ocid, parent_framework_title,
            data_source, suitable_for_sme, last_updated
        ) VALUES (
            :ocid, :buyer_id, :latest_release_id, :title, :description,
            :procurement_method, :procurement_method_detail, :main_category,
            :legal_basis, :above_threshold, :value_amount, :value_amount_gross, :currency,
            :tender_end_date, :published_date, :tender_status,
            :total_bids, :final_stage_bids, :sme_bids, :vcse_bids,
            :has_renewal, :renewal_description, :notice_type, :notice_url, :latest_tag,
            :is_framework, :framework_method, :framework_type,
            :parent_framework_ocid, :parent_framework_title,
            :data_source, :suitable_for_sme, datetime('now')
        )
        ON CONFLICT(ocid) DO UPDATE SET
            latest_release_id=excluded.latest_release_id,
            tender_status=COALESCE(excluded.tender_status, tender_status),
            total_bids=COALESCE(excluded.total_bids, total_bids),
            final_stage_bids=COALESCE(excluded.final_stage_bids, final_stage_bids),
            sme_bids=COALESCE(excluded.sme_bids, sme_bids),
            vcse_bids=COALESCE(excluded.vcse_bids, vcse_bids),
            has_renewal=COALESCE(excluded.has_renewal, has_renewal),
            renewal_description=COALESCE(excluded.renewal_description, renewal_description),
            notice_url=COALESCE(excluded.notice_url, notice_url),
            latest_tag=excluded.latest_tag,
            is_framework=COALESCE(excluded.is_framework, is_framework),
            suitable_for_sme=COALESCE(excluded.suitable_for_sme, suitable_for_sme),
            last_updated=datetime('now')
    """, r)


def upsert_award_row(conn: sqlite3.Connection, row: dict):
    r = {"lot_id": None, "title": None, "status": None, "award_date": None,
         "value_amount": None, "value_amount_gross": None, "currency": "GBP",
         "contract_start_date": None, "contract_end_date": None,
         "contract_max_extend": None, "date_signed": None, "contract_status": None,
         "award_criteria": None, "value_quality": None, "data_source": "fts", **row}
    conn.execute("""
        INSERT INTO awards (
            id, ocid, lot_id, title, status, award_date,
            value_amount, value_amount_gross, currency,
            contract_start_date, contract_end_date, contract_max_extend,
            date_signed, contract_status, award_criteria,
            value_quality, data_source, last_updated
        ) VALUES (
            :id, :ocid, :lot_id, :title, :status, :award_date,
            :value_amount, :value_amount_gross, :currency,
            :contract_start_date, :contract_end_date, :contract_max_extend,
            :date_signed, :contract_status, :award_criteria,
            :value_quality, :data_source, datetime('now')
        )
        ON CONFLICT(id) DO UPDATE SET
            status=COALESCE(excluded.status, status),
            value_amount=COALESCE(excluded.value_amount, value_amount),
            value_amount_gross=COALESCE(excluded.value_amount_gross, value_amount_gross),
            contract_start_date=COALESCE(excluded.contract_start_date, contract_start_date),
            contract_end_date=COALESCE(excluded.contract_end_date, contract_end_date),
            contract_max_extend=COALESCE(excluded.contract_max_extend, contract_max_extend),
            date_signed=COALESCE(excluded.date_signed, date_signed),
            contract_status=COALESCE(excluded.contract_status, contract_status),
            value_quality=excluded.value_quality,
            data_source=excluded.data_source,
            last_updated=datetime('now')
    """, r)


def upsert_cpv_row(conn: sqlite3.Connection, ocid: str, code: str, desc: str):
    conn.execute("""
        INSERT OR IGNORE INTO cpv_codes (ocid, code, description) VALUES (?, ?, ?)
    """, (ocid, code, desc))


def link_award_supplier(conn: sqlite3.Connection, award_id: str, supplier_id: str):
    conn.execute("""
        INSERT OR IGNORE INTO award_suppliers (award_id, supplier_id) VALUES (?, ?)
    """, (award_id, supplier_id))
