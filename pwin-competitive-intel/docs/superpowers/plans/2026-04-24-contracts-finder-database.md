# Contracts Finder Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Contracts Finder as a second ingest source to `bid_intel.db`, covering sub-threshold UK public procurement (£10k–£139k) missed entirely by FTS.

**Architecture:** Four changes in dependency order — (1) schema migration adding `data_source` + `suitable_for_sme` columns; (2) new `db_utils.py` with shared SQL primitives; (3) refactor `ingest.py` to delegate SQL to `db_utils`; (4) new `ingest_cf.py` that hits the CF POST search API, parses CF JSON, and persists with `data_source='cf'`. Scheduler and GitHub Actions updated to run CF ingest nightly as a non-fatal step.

**Tech Stack:** Python 3.9+ stdlib only (`sqlite3`, `urllib`, `hashlib`, `argparse`, `unittest`). No external dependencies.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Modify | `db/schema.sql` | Add `data_source` + `suitable_for_sme` to table DDL |
| Modify | `agent/ingest.py` | Add columns to `_migrate_schema()`; delegate SQL to db_utils |
| **Create** | `agent/db_utils.py` | Shared: `get_db`, `init_schema`, `_migrate_schema`, upsert row primitives, ingest state |
| **Create** | `agent/ingest_cf.py` | CF API fetch, CF JSON → normalized dict parsers, `main()` |
| **Create** | `test/test_db_utils.py` | Unit tests for db_utils migrations and upsert functions |
| **Create** | `test/test_ingest_cf.py` | Unit tests for CF parsers and end-to-end `process_cf_notice` |
| Modify | `agent/scheduler.py` | Add CF ingest step (non-fatal) |
| Modify | `.github/workflows/ingest.yml` | Add CF ingest step (`continue-on-error: true`) |
| Modify | `queries/queries.py` | Add per-source breakdown to `db_summary()` |

---

## Task 1: Schema columns + migration

**Files:**
- Modify: `db/schema.sql`
- Modify: `agent/ingest.py` (only `_migrate_schema` function, lines 57–91)
- Create: `test/test_db_utils.py` (schema migration tests — to be expanded in Task 2)

- [ ] **Step 1: Write the failing migration test**

Create `test/test_db_utils.py`:

```python
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _mem_db():
    """Open in-memory DB, run schema init from ingest.py (before db_utils exists)."""
    import ingest as ing
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    ing.DB_PATH  # just to import
    orig_path = ing.SCHEMA_PATH
    ing.SCHEMA_PATH = SCHEMA_PATH
    ing.init_schema(conn)
    ing.SCHEMA_PATH = orig_path
    return conn


class TestSchemaMigration(unittest.TestCase):
    def test_data_source_on_notices(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(notices)").fetchall()}
        self.assertIn("data_source", cols)

    def test_data_source_on_awards(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(awards)").fetchall()}
        self.assertIn("data_source", cols)

    def test_data_source_on_buyers(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(buyers)").fetchall()}
        self.assertIn("data_source", cols)

    def test_data_source_on_suppliers(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(suppliers)").fetchall()}
        self.assertIn("data_source", cols)

    def test_suitable_for_sme_on_notices(self):
        conn = _mem_db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(notices)").fetchall()}
        self.assertIn("suitable_for_sme", cols)

    def test_migration_is_idempotent(self):
        conn = _mem_db()
        import ingest as ing
        ing._migrate_schema(conn)  # second call must not raise
        ing._migrate_schema(conn)  # third call must not raise


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd pwin-competitive-intel
python -m unittest test.test_db_utils -v
```

Expected: 5–6 FAIL with `AssertionError: 'data_source' not found`

- [ ] **Step 3: Add `data_source` column to schema.sql (4 tables)**

In `db/schema.sql`, add `data_source TEXT DEFAULT 'fts'` to each CREATE TABLE. Locate the four tables and add the column before the closing timestamp columns:

In `CREATE TABLE IF NOT EXISTS buyers (...)` — add after `last_updated` line:
```sql
    data_source         TEXT DEFAULT 'fts',
```

In `CREATE TABLE IF NOT EXISTS suppliers (...)` — add after `ch_enriched_at`:
```sql
    data_source         TEXT DEFAULT 'fts',
```

In `CREATE TABLE IF NOT EXISTS notices (...)` — add after `last_updated` line and add:
```sql
    data_source         TEXT DEFAULT 'fts',
    suitable_for_sme    INTEGER DEFAULT 0,
```

In `CREATE TABLE IF NOT EXISTS awards (...)` — add after `last_updated`:
```sql
    data_source         TEXT DEFAULT 'fts',
```

Also add two indexes after their respective tables:
```sql
CREATE INDEX IF NOT EXISTS idx_notices_source ON notices(data_source);
CREATE INDEX IF NOT EXISTS idx_awards_source  ON awards(data_source);
```

- [ ] **Step 4: Add migrations to `_migrate_schema()` in `agent/ingest.py`**

In `agent/ingest.py`, inside `_migrate_schema(conn)`, add after the existing `value_quality` migration block (after line 91, before `conn.commit()`):

```python
    # ── data_source: multi-source tag (added 2026-04-24) ──
    for table in ("notices", "awards", "buyers", "suppliers"):
        cols = _columns(table)
        if "data_source" not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN data_source TEXT DEFAULT 'fts'")
            log.info("Migrated %s: added column data_source", table)

    # ── notices: CF SME suitability flag (added 2026-04-24) ──
    notices_cols_v2 = _columns("notices")
    if "suitable_for_sme" not in notices_cols_v2:
        conn.execute("ALTER TABLE notices ADD COLUMN suitable_for_sme INTEGER DEFAULT 0")
        log.info("Migrated notices: added column suitable_for_sme")
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
python -m unittest test.test_db_utils -v
```

Expected: all 6 tests PASS

- [ ] **Step 6: Commit**

```bash
git add db/schema.sql agent/ingest.py test/test_db_utils.py
git commit -m "feat: add data_source and suitable_for_sme columns via schema migration"
```

---

## Task 2: Create `agent/db_utils.py`

**Files:**
- Create: `agent/db_utils.py`
- Modify: `test/test_db_utils.py` (expand with upsert + state tests)

- [ ] **Step 1: Add db_utils tests to `test/test_db_utils.py`**

Append to `test/test_db_utils.py` (keep the existing `TestSchemaMigration` class, update `_mem_db` to use db_utils once created, add these new classes):

```python
# ── Update _mem_db to use db_utils once the module exists ──
# Replace the existing _mem_db function with:
def _mem_db():
    import db_utils
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    db_utils.init_schema(conn, SCHEMA_PATH)
    return conn


class TestUpsertBuyerRow(unittest.TestCase):
    def test_insert_and_read_back(self):
        import db_utils
        conn = _mem_db()
        db_utils.upsert_buyer_row(conn, {
            "id": "cf-buyer-99",
            "name": "Test Council",
            "postal_code": "TE1 1ST",
            "data_source": "cf",
        })
        conn.commit()
        row = conn.execute("SELECT * FROM buyers WHERE id='cf-buyer-99'").fetchone()
        self.assertEqual(row["name"], "Test Council")
        self.assertEqual(row["data_source"], "cf")
        self.assertEqual(row["postal_code"], "TE1 1ST")

    def test_fts_default_source(self):
        import db_utils
        conn = _mem_db()
        db_utils.upsert_buyer_row(conn, {"id": "fts-b1", "name": "HMRC"})
        conn.commit()
        row = conn.execute("SELECT data_source FROM buyers WHERE id='fts-b1'").fetchone()
        self.assertEqual(row["data_source"], "fts")

    def test_upsert_updates_name(self):
        import db_utils
        conn = _mem_db()
        db_utils.upsert_buyer_row(conn, {"id": "b1", "name": "Old Name", "data_source": "cf"})
        db_utils.upsert_buyer_row(conn, {"id": "b1", "name": "New Name", "data_source": "cf"})
        conn.commit()
        row = conn.execute("SELECT name FROM buyers WHERE id='b1'").fetchone()
        self.assertEqual(row["name"], "New Name")


class TestUpsertSupplierRow(unittest.TestCase):
    def test_insert_with_ch_number(self):
        import db_utils
        conn = _mem_db()
        sid = db_utils.upsert_supplier_row(conn, {
            "id": "cf-sup-abc123",
            "name": "Acme Ltd",
            "companies_house_no": "12345678",
            "data_source": "cf",
        })
        conn.commit()
        row = conn.execute("SELECT * FROM suppliers WHERE id='cf-sup-abc123'").fetchone()
        self.assertEqual(row["companies_house_no"], "12345678")
        self.assertEqual(sid, "cf-sup-abc123")


class TestUpsertNoticeRow(unittest.TestCase):
    def setUp(self):
        import db_utils
        self.conn = _mem_db()
        db_utils.upsert_buyer_row(self.conn, {"id": "b1", "name": "HMRC", "data_source": "fts"})
        self.conn.commit()

    def test_insert_cf_notice(self):
        import db_utils
        db_utils.upsert_notice_row(self.conn, {
            "ocid": "cf-12345",
            "buyer_id": "b1",
            "title": "IT Support",
            "data_source": "cf",
            "suitable_for_sme": 1,
        })
        self.conn.commit()
        row = self.conn.execute("SELECT * FROM notices WHERE ocid='cf-12345'").fetchone()
        self.assertEqual(row["data_source"], "cf")
        self.assertEqual(row["suitable_for_sme"], 1)
        self.assertEqual(row["title"], "IT Support")

    def test_fts_default_source(self):
        import db_utils
        db_utils.upsert_notice_row(self.conn, {"ocid": "ocds-xyz", "buyer_id": "b1"})
        self.conn.commit()
        row = self.conn.execute("SELECT data_source FROM notices WHERE ocid='ocds-xyz'").fetchone()
        self.assertEqual(row["data_source"], "fts")


class TestUpsertAwardRow(unittest.TestCase):
    def setUp(self):
        import db_utils
        self.conn = _mem_db()
        db_utils.upsert_buyer_row(self.conn, {"id": "b1", "name": "HMRC"})
        db_utils.upsert_notice_row(self.conn, {"ocid": "cf-99", "buyer_id": "b1", "data_source": "cf"})
        self.conn.commit()

    def test_insert_cf_award(self):
        import db_utils
        db_utils.upsert_award_row(self.conn, {
            "id": "cf-award-99",
            "ocid": "cf-99",
            "value_amount_gross": 45000.0,
            "data_source": "cf",
        })
        self.conn.commit()
        row = self.conn.execute("SELECT * FROM awards WHERE id='cf-award-99'").fetchone()
        self.assertEqual(row["data_source"], "cf")
        self.assertEqual(row["value_amount_gross"], 45000.0)


class TestLinkAwardSupplier(unittest.TestCase):
    def test_link_is_idempotent(self):
        import db_utils
        conn = _mem_db()
        db_utils.upsert_buyer_row(conn, {"id": "b1", "name": "B"})
        db_utils.upsert_notice_row(conn, {"ocid": "n1", "buyer_id": "b1"})
        db_utils.upsert_award_row(conn, {"id": "a1", "ocid": "n1"})
        db_utils.upsert_supplier_row(conn, {"id": "s1", "name": "S"})
        db_utils.link_award_supplier(conn, "a1", "s1")
        db_utils.link_award_supplier(conn, "a1", "s1")  # second call must not raise
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM award_suppliers WHERE award_id='a1'").fetchone()[0]
        self.assertEqual(count, 1)


class TestIngestState(unittest.TestCase):
    def test_get_missing_returns_empty(self):
        import db_utils
        conn = _mem_db()
        self.assertEqual(db_utils.get_ingest_state(conn, "nonexistent"), "")

    def test_set_and_get_roundtrip(self):
        import db_utils
        conn = _mem_db()
        db_utils.set_ingest_state(conn, "cf_last_date", "2026-01-01T00:00:00")
        self.assertEqual(db_utils.get_ingest_state(conn, "cf_last_date"), "2026-01-01T00:00:00")

    def test_overwrite(self):
        import db_utils
        conn = _mem_db()
        db_utils.set_ingest_state(conn, "k", "v1")
        db_utils.set_ingest_state(conn, "k", "v2")
        self.assertEqual(db_utils.get_ingest_state(conn, "k"), "v2")
```

- [ ] **Step 2: Run tests — expect FAIL (db_utils not yet created)**

```bash
python -m unittest test.test_db_utils -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'db_utils'`

- [ ] **Step 3: Create `agent/db_utils.py`**

Create `agent/db_utils.py`:

```python
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
            street_address=COALESCE(excluded.street_address, street_address),
            locality=COALESCE(excluded.locality, locality),
            postal_code=COALESCE(excluded.postal_code, postal_code),
            region_code=COALESCE(excluded.region_code, region_code),
            contact_email=COALESCE(excluded.contact_email, contact_email),
            website=COALESCE(excluded.website, website),
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
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
python -m unittest test.test_db_utils -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add agent/db_utils.py test/test_db_utils.py
git commit -m "feat: add db_utils.py with shared upsert primitives and ingest state helpers"
```

---

## Task 3: Refactor `ingest.py` to delegate SQL to `db_utils`

**Files:**
- Modify: `agent/ingest.py`

The goal: replace the duplicate `_migrate_schema`, `get_db`, `init_schema` implementations in `ingest.py` with imports from `db_utils`. Replace the raw SQL in `upsert_buyer`, `upsert_supplier`, `upsert_notice`, `upsert_awards` with calls to the db_utils row primitives. All FTS-specific parsing logic stays in ingest.py.

- [ ] **Step 1: Update imports at top of `agent/ingest.py`**

Replace:
```python
import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
```

With:
```python
import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

import db_utils
from db_utils import (
    get_db, init_schema,
    upsert_buyer_row, upsert_supplier_row, upsert_notice_row,
    upsert_award_row, upsert_cpv_row, link_award_supplier,
)
```

- [ ] **Step 2: Remove the duplicated `get_db`, `_migrate_schema`, `init_schema` from `ingest.py`**

Delete lines 48–106 (the three functions: `get_db`, `_migrate_schema`, `init_schema`). They are now imported from `db_utils`.

- [ ] **Step 3: Refactor `upsert_buyer` to call `upsert_buyer_row`**

Replace the existing `upsert_buyer(conn, party)` function (lines ~385–420) with:

```python
def upsert_buyer(conn: sqlite3.Connection, party: dict):
    addr = party.get("address", {})
    contact = party.get("contactPoint", {})
    details = party.get("details", {})
    org_type = None
    devolved = None
    for cls in details.get("classifications", []):
        if cls.get("scheme") == "UK_CA_TYPE":
            org_type = cls.get("id")
        if cls.get("scheme") == "UK_CA_DEVOLVED_REGULATIONS":
            devolved = cls.get("id")
    upsert_buyer_row(conn, {
        "id": party.get("id"),
        "name": party.get("name"),
        "org_type": org_type,
        "devolved_region": devolved,
        "street_address": addr.get("streetAddress"),
        "locality": addr.get("locality"),
        "postal_code": addr.get("postalCode"),
        "region_code": addr.get("region"),
        "contact_name": contact.get("name"),
        "contact_email": contact.get("email"),
        "contact_telephone": contact.get("telephone"),
        "website": details.get("url"),
        "data_source": "fts",
    })
```

- [ ] **Step 4: Refactor `upsert_supplier` to call `upsert_supplier_row`**

Replace `upsert_supplier(conn, party)` with:

```python
def upsert_supplier(conn: sqlite3.Connection, party: dict) -> str:
    addr = party.get("address", {})
    contact = party.get("contactPoint", {})
    details = party.get("details", {})
    return upsert_supplier_row(conn, {
        "id": party.get("id"),
        "name": party.get("name"),
        "companies_house_no": _extract_coh(party),
        "scale": details.get("scale"),
        "is_vcse": int(details.get("vcse", False)),
        "is_sheltered": int(details.get("shelteredWorkshop", False)),
        "is_public_mission": int(details.get("publicServiceMissionOrganization", False)),
        "street_address": addr.get("streetAddress"),
        "locality": addr.get("locality"),
        "postal_code": addr.get("postalCode"),
        "region_code": addr.get("region"),
        "contact_email": contact.get("email"),
        "website": details.get("url"),
        "data_source": "fts",
    })
```

- [ ] **Step 5: Refactor `upsert_notice` to call `upsert_notice_row`**

Replace `upsert_notice(conn, release, buyer_id)` with:

```python
def upsert_notice(conn: sqlite3.Connection, release: dict, buyer_id: str):
    tender = release.get("tender", {})
    bids = release.get("bids", {})
    bid_stats = {s.get("measure"): s.get("value") for s in bids.get("statistics", [])}
    awards = release.get("awards", [])
    val = tender.get("value", {})
    amount = val.get("amount")
    amount_gross = val.get("amountGross") or amount
    docs = tender.get("documents", [])
    for a in awards:
        docs.extend(a.get("documents", []))
    notice = next((d for d in docs if d.get("format") == "text/html"), {})
    tags = release.get("tag", [])
    has_renewal = any(a.get("hasRenewal") for a in awards)
    renewal_desc = next((a.get("renewal", {}).get("description") for a in awards if a.get("hasRenewal")), None)
    techniques = tender.get("techniques", {})
    fa = techniques.get("frameworkAgreement", {})
    parent_framework_ocid = None
    parent_framework_title = None
    for rp in release.get("relatedProcesses", []):
        if "framework" in (rp.get("relationship") or []):
            parent_framework_ocid = rp.get("identifier")
            parent_framework_title = rp.get("title")
            break
    upsert_notice_row(conn, {
        "ocid": release.get("ocid"),
        "buyer_id": buyer_id,
        "latest_release_id": release.get("id"),
        "title": tender.get("title"),
        "description": tender.get("description"),
        "procurement_method": tender.get("procurementMethod"),
        "procurement_method_detail": tender.get("procurementMethodDetails"),
        "main_category": tender.get("mainProcurementCategory") or next(
            (a.get("mainProcurementCategory") for a in awards), None),
        "legal_basis": _safe(tender, "legalBasis", "id"),
        "above_threshold": int(
            tender.get("aboveThreshold") or
            any(a.get("aboveThreshold") for a in awards) or False),
        "value_amount": amount,
        "value_amount_gross": amount_gross,
        "currency": val.get("currency", "GBP"),
        "tender_end_date": _dt(tender.get("tenderPeriod", {}).get("endDate")),
        "published_date": _dt(release.get("date")),
        "tender_status": tender.get("status"),
        "total_bids": bid_stats.get("bids"),
        "final_stage_bids": bid_stats.get("finalStageBids"),
        "sme_bids": bid_stats.get("smeFinalStageBids"),
        "vcse_bids": bid_stats.get("vcseFinalStageBids"),
        "has_renewal": int(has_renewal),
        "renewal_description": renewal_desc,
        "notice_type": notice.get("noticeType"),
        "notice_url": notice.get("url"),
        "latest_tag": ",".join(tags),
        "is_framework": 1 if fa else 0,
        "framework_method": fa.get("method"),
        "framework_type": fa.get("type"),
        "parent_framework_ocid": parent_framework_ocid,
        "parent_framework_title": parent_framework_title,
        "data_source": "fts",
    })
```

- [ ] **Step 6: Refactor `upsert_awards` to call `upsert_award_row` + `link_award_supplier`**

Replace the raw SQL inside the `conn.execute("""INSERT INTO awards...""")` block and the award_suppliers insert with calls to db_utils. The outer loop structure and all the parsing logic stays identical. Only replace the two `conn.execute` calls at the bottom of the loop:

Inside the for-loop in `upsert_awards`, replace:
```python
        conn.execute("""
            INSERT INTO awards (...)
            ...
        """, (...))
```

With:
```python
        upsert_award_row(conn, {
            "id": award_id,
            "ocid": ocid,
            "lot_id": lot_id,
            "title": award.get("title"),
            "status": award.get("status"),
            "award_date": _dt(award.get("date")),
            "value_amount": val.get("amount"),
            "value_amount_gross": amount_gross,
            "currency": val.get("currency", "GBP"),
            "contract_start_date": _dt(cp.get("startDate")),
            "contract_end_date": _dt(cp.get("endDate")),
            "contract_max_extend": _dt(cp.get("maxExtentDate")),
            "date_signed": _dt(linked_contract.get("dateSigned")),
            "contract_status": linked_contract.get("status"),
            "award_criteria": criteria,
            "value_quality": value_quality,
            "data_source": "fts",
        })
```

And replace the `conn.execute("INSERT OR IGNORE INTO award_suppliers ...")` with:
```python
            link_award_supplier(conn, award_id, sup_id)
```

Also replace `conn.execute("INSERT OR IGNORE INTO suppliers ...")` (the stub creation inside the award loop) with:
```python
                upsert_supplier_row(conn, {"id": sup_id, "name": sup.get("name", "Unknown"), "data_source": "fts"})
```

- [ ] **Step 7: Refactor `upsert_cpv_codes` to call `upsert_cpv_row`**

Replace the `conn.execute("INSERT OR IGNORE INTO cpv_codes ...")` in `upsert_cpv_codes` with:
```python
    for code, desc in cpvs:
        upsert_cpv_row(conn, ocid, code, desc)
```

- [ ] **Step 8: Update `init_schema` call in `main()` to pass `SCHEMA_PATH`**

In `main()`, change:
```python
    init_schema(conn)
```
to:
```python
    init_schema(conn, SCHEMA_PATH)
```

- [ ] **Step 9: Smoke test — existing FTS ingest still works**

```bash
python agent/ingest.py --limit 10
```

Expected output ends with:
```
Ingest complete
  Releases processed : 10
  Buyers upserted    : ...
  Notices upserted   : ...
```

No errors.

- [ ] **Step 10: Commit**

```bash
git add agent/ingest.py
git commit -m "refactor: delegate ingest.py SQL to db_utils shared primitives"
```

---

## Task 4: CF parser functions

**Files:**
- Create: `agent/ingest_cf.py` (parser functions only — no `main()` yet)
- Create: `test/test_ingest_cf.py`

> **Note on CF API field names:** The field names used below (`id`, `organisation`, `isSuitableForSme`, `industryCodes`, `supplierName`, `companiesHouseNumber`) are based on the published CF API schema. Before completing Task 5, make one test call (`python agent/ingest_cf.py --limit 1`) and inspect the raw response to verify field names match. Adjust `_cf_notice_row`, `_cf_buyer_row`, `_cf_supplier_row` if they differ.

- [ ] **Step 1: Write failing parser tests — create `test/test_ingest_cf.py`**

```python
import json
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
import db_utils

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _mem_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    db_utils.init_schema(conn, SCHEMA_PATH)
    return conn


SAMPLE_TENDER = {
    "id": "2021-123456",
    "title": "IT Support Services",
    "description": "Provision of IT support",
    "publishedDate": "2021-01-15T10:30:00",
    "deadlineDate": "2021-02-15T17:00:00",
    "valueLow": 10000,
    "valueHigh": 50000,
    "noticeType": "Contract Notice",
    "status": "live",
    "isSuitableForSme": True,
    "industryCodes": [{"code": "72250000", "label": "System support services"}],
    "organisation": {
        "id": 9001,
        "name": "Department for Transport",
        "address": {"town": "London", "postcode": "SW1H 0ET"},
    },
    "awardedDate": None,
    "awardedValue": None,
    "suppliers": [],
    "contractStart": None,
    "contractEnd": None,
}

SAMPLE_AWARD = {
    **SAMPLE_TENDER,
    "id": "2021-999999",
    "noticeType": "Contract Award Notice",
    "status": "awarded",
    "awardedDate": "2021-03-01",
    "awardedValue": 45000,
    "suppliers": [
        {
            "supplierName": "Acme Ltd",
            "companiesHouseNumber": "12345678",
            "address": {"postcode": "EC1A 1BB", "town": "London"},
        }
    ],
    "contractStart": "2021-04-01",
    "contractEnd": "2023-03-31",
}


class TestCfHelpers(unittest.TestCase):
    def test_cf_buyer_id_uses_org_id(self):
        import ingest_cf
        self.assertEqual(ingest_cf._cf_buyer_id({"id": 9001, "name": "DfT"}), "cf-buyer-9001")

    def test_cf_buyer_id_falls_back_to_name_hash(self):
        import ingest_cf
        bid = ingest_cf._cf_buyer_id({"name": "Some Council"})
        self.assertTrue(bid.startswith("cf-buyer-"))
        self.assertGreater(len(bid), len("cf-buyer-"))

    def test_cf_supplier_id_is_deterministic(self):
        import ingest_cf
        sup = {"supplierName": "Acme Ltd", "address": {"postcode": "EC1A 1BB"}}
        self.assertEqual(ingest_cf._cf_supplier_id(sup), ingest_cf._cf_supplier_id(sup))
        self.assertTrue(ingest_cf._cf_supplier_id(sup).startswith("cf-sup-"))

    def test_cf_supplier_id_no_postcode(self):
        import ingest_cf
        sid = ingest_cf._cf_supplier_id({"supplierName": "Acme Ltd"})
        self.assertTrue(sid.startswith("cf-sup-"))

    def test_cf_supplier_id_different_names_differ(self):
        import ingest_cf
        s1 = ingest_cf._cf_supplier_id({"supplierName": "Alpha Ltd"})
        s2 = ingest_cf._cf_supplier_id({"supplierName": "Beta Ltd"})
        self.assertNotEqual(s1, s2)

    def test_cf_notice_row_ocid(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_TENDER, "cf-buyer-9001")
        self.assertEqual(row["ocid"], "cf-2021-123456")

    def test_cf_notice_row_data_source(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_TENDER, "cf-buyer-9001")
        self.assertEqual(row["data_source"], "cf")

    def test_cf_notice_row_suitable_for_sme(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_TENDER, "cf-buyer-9001")
        self.assertEqual(row["suitable_for_sme"], 1)

    def test_cf_notice_row_live_status_normalised(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_TENDER, "cf-buyer-9001")
        self.assertEqual(row["tender_status"], "active")

    def test_cf_notice_row_awarded_status_normalised(self):
        import ingest_cf
        row = ingest_cf._cf_notice_row(SAMPLE_AWARD, "cf-buyer-9001")
        self.assertEqual(row["tender_status"], "complete")

    def test_cf_award_row_returns_none_for_tender(self):
        import ingest_cf
        self.assertIsNone(ingest_cf._cf_award_row(SAMPLE_TENDER, "cf-2021-123456"))

    def test_cf_award_row_returns_dict_for_award(self):
        import ingest_cf
        result = ingest_cf._cf_award_row(SAMPLE_AWARD, "cf-2021-999999")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "cf-award-2021-999999")
        self.assertEqual(result["value_amount"], 45000)
        self.assertEqual(result["data_source"], "cf")
        self.assertEqual(result["contract_start_date"], "2021-04-01")
        self.assertEqual(result["contract_end_date"], "2023-03-31")

    def test_cf_buyer_row_maps_fields(self):
        import ingest_cf
        row = ingest_cf._cf_buyer_row(SAMPLE_TENDER["organisation"])
        self.assertEqual(row["id"], "cf-buyer-9001")
        self.assertEqual(row["name"], "Department for Transport")
        self.assertEqual(row["postal_code"], "SW1H 0ET")
        self.assertEqual(row["locality"], "London")
        self.assertEqual(row["data_source"], "cf")

    def test_cf_supplier_row_maps_fields(self):
        import ingest_cf
        sup = SAMPLE_AWARD["suppliers"][0]
        row = ingest_cf._cf_supplier_row(sup)
        self.assertTrue(row["id"].startswith("cf-sup-"))
        self.assertEqual(row["name"], "Acme Ltd")
        self.assertEqual(row["companies_house_no"], "12345678")
        self.assertEqual(row["postal_code"], "EC1A 1BB")
        self.assertEqual(row["data_source"], "cf")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python -m unittest test.test_ingest_cf -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError: No module named 'ingest_cf'`

- [ ] **Step 3: Create `agent/ingest_cf.py` with parser functions**

```python
"""
PWIN Competitive Intelligence — Contracts Finder ingest
=======================================================
Fetches UK Contracts Finder notices via the CF search API,
parses CF JSON into normalised dicts, and persists to bid_intel.db
with data_source='cf'.

Usage:
    python ingest_cf.py                    # incremental from cf_last_date
    python ingest_cf.py --from 2021-01-01  # backfill from date
    python ingest_cf.py --limit 500        # cap notices (testing)
"""

import argparse
import hashlib
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import db_utils

CF_SEARCH_URL = (
    "https://www.contractsfinder.service.gov.uk"
    "/Published/Notices/PublishedSearchApi/Search"
)
DB_PATH     = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"
PAGE_SIZE   = 100
RETRY_MAX   = 5
RETRY_DELAY = 10
CF_STATE_KEY = "cf_last_date"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest_cf")


# ── CF-specific helpers ──────────────────────────────────────────────────────

def _cf_hash(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:8]


def _cf_buyer_id(org: dict) -> str:
    org_id = org.get("id") or org.get("organisationId")
    if org_id:
        return f"cf-buyer-{org_id}"
    return f"cf-buyer-{_cf_hash(org.get('name', 'unknown'))}"


def _cf_supplier_id(sup: dict) -> str:
    name = sup.get("supplierName") or sup.get("name") or ""
    postcode = (sup.get("address") or {}).get("postcode", "")
    return f"cf-sup-{_cf_hash(f'{name}|{postcode}')}"


def _dt_cf(s) -> str | None:
    if not s:
        return None
    try:
        s = str(s)
        if "T" in s:
            return s[:10] + " " + s[11:19]
        return s[:10]
    except Exception:
        return None


_STATUS_MAP = {
    "live":      "active",
    "awarded":   "complete",
    "expired":   "cancelled",
    "withdrawn": "cancelled",
    "cancelled": "cancelled",
}


def _cf_buyer_row(org: dict) -> dict:
    addr = org.get("address") or {}
    return {
        "id":          _cf_buyer_id(org),
        "name":        org.get("name", "Unknown"),
        "postal_code": addr.get("postcode"),
        "locality":    addr.get("town"),
        "data_source": "cf",
    }


def _cf_supplier_row(sup: dict) -> dict:
    addr = sup.get("address") or {}
    raw_ch = sup.get("companiesHouseNumber") or sup.get("companiesHouseNo")
    ch_no = str(raw_ch).strip() if raw_ch and len(str(raw_ch)) <= 10 else None
    return {
        "id":                _cf_supplier_id(sup),
        "name":              sup.get("supplierName") or sup.get("name") or "Unknown",
        "companies_house_no": ch_no,
        "postal_code":       addr.get("postcode"),
        "locality":          addr.get("town"),
        "data_source":       "cf",
    }


def _cf_notice_row(notice: dict, buyer_id: str) -> dict:
    notice_id = str(notice.get("id") or notice.get("noticeIdentifier") or "")
    # CF sometimes has valueHigh (max) as primary value signal
    value = notice.get("valueHigh") or notice.get("valueLow") or notice.get("value")
    if isinstance(value, dict):
        value = value.get("amount")
    raw_status = (notice.get("status") or "").lower()
    return {
        "ocid":             f"cf-{notice_id}",
        "buyer_id":         buyer_id,
        "title":            notice.get("title"),
        "description":      notice.get("description"),
        "published_date":   _dt_cf(notice.get("publishedDate")),
        "tender_end_date":  _dt_cf(notice.get("deadlineDate")),
        "value_amount":     value,
        "value_amount_gross": value,
        "notice_type":      notice.get("noticeType") or notice.get("type"),
        "tender_status":    _STATUS_MAP.get(raw_status, raw_status) or None,
        "data_source":      "cf",
        "suitable_for_sme": 1 if notice.get("isSuitableForSme") else 0,
        "above_threshold":  0,
    }


def _cf_award_row(notice: dict, ocid: str) -> dict | None:
    notice_type = (notice.get("noticeType") or notice.get("type") or "").lower()
    if "award" not in notice_type:
        return None
    # Must have at least one signal that an award happened
    has_signal = (
        notice.get("awardedValue") or
        notice.get("awardedDate") or
        notice.get("suppliers") or
        notice.get("awardedSuppliers")
    )
    if not has_signal:
        return None
    notice_id = str(notice.get("id") or notice.get("noticeIdentifier") or "")
    award_val = notice.get("awardedValue")
    if isinstance(award_val, dict):
        award_val = award_val.get("amount")
    return {
        "id":                  f"cf-award-{notice_id}",
        "ocid":                ocid,
        "award_date":          _dt_cf(notice.get("awardedDate")),
        "value_amount":        award_val,
        "value_amount_gross":  award_val,
        "contract_start_date": _dt_cf(notice.get("contractStart")),
        "contract_end_date":   _dt_cf(notice.get("contractEnd")),
        "status":              "active" if award_val else None,
        "data_source":         "cf",
    }
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
python -m unittest test.test_ingest_cf -v
```

Expected: all `TestCfHelpers` tests PASS

- [ ] **Step 5: Commit**

```bash
git add agent/ingest_cf.py test/test_ingest_cf.py
git commit -m "feat: add CF parser functions and parser unit tests"
```

---

## Task 5: CF API fetch + `process_cf_notice` (with end-to-end tests)

**Files:**
- Modify: `agent/ingest_cf.py` (add `fetch_cf_page` and `process_cf_notice`)
- Modify: `test/test_ingest_cf.py` (add `TestProcessCfNotice` and `TestFetchCfPage`)

- [ ] **Step 1: Add end-to-end tests to `test/test_ingest_cf.py`**

Append to `test/test_ingest_cf.py`:

```python
class TestProcessCfNotice(unittest.TestCase):
    def setUp(self):
        self.conn = _mem_db()

    def test_tender_upserts_buyer_and_notice(self):
        import ingest_cf
        ingest_cf.process_cf_notice(self.conn, SAMPLE_TENDER)
        self.conn.commit()
        buyer = self.conn.execute("SELECT * FROM buyers WHERE id='cf-buyer-9001'").fetchone()
        self.assertIsNotNone(buyer)
        self.assertEqual(buyer["data_source"], "cf")
        notice = self.conn.execute("SELECT * FROM notices WHERE ocid='cf-2021-123456'").fetchone()
        self.assertIsNotNone(notice)
        self.assertEqual(notice["suitable_for_sme"], 1)
        self.assertEqual(notice["data_source"], "cf")

    def test_tender_stores_cpv_codes(self):
        import ingest_cf
        ingest_cf.process_cf_notice(self.conn, SAMPLE_TENDER)
        self.conn.commit()
        cpv = self.conn.execute(
            "SELECT * FROM cpv_codes WHERE ocid='cf-2021-123456'"
        ).fetchone()
        self.assertIsNotNone(cpv)
        self.assertEqual(cpv["code"], "72250000")

    def test_award_creates_award_row(self):
        import ingest_cf
        ingest_cf.process_cf_notice(self.conn, SAMPLE_AWARD)
        self.conn.commit()
        award = self.conn.execute(
            "SELECT * FROM awards WHERE id='cf-award-2021-999999'"
        ).fetchone()
        self.assertIsNotNone(award)
        self.assertEqual(award["value_amount_gross"], 45000)
        self.assertEqual(award["data_source"], "cf")

    def test_award_links_supplier(self):
        import ingest_cf
        ingest_cf.process_cf_notice(self.conn, SAMPLE_AWARD)
        self.conn.commit()
        link = self.conn.execute(
            "SELECT * FROM award_suppliers WHERE award_id='cf-award-2021-999999'"
        ).fetchone()
        self.assertIsNotNone(link)
        supplier = self.conn.execute(
            "SELECT * FROM suppliers WHERE id=?", (link["supplier_id"],)
        ).fetchone()
        self.assertEqual(supplier["name"], "Acme Ltd")
        self.assertEqual(supplier["companies_house_no"], "12345678")

    def test_notice_without_organisation_is_skipped(self):
        import ingest_cf
        notice = {**SAMPLE_TENDER, "organisation": None}
        counts = ingest_cf.process_cf_notice(self.conn, notice)
        self.assertEqual(counts["notices"], 0)

    def test_process_is_idempotent(self):
        import ingest_cf
        ingest_cf.process_cf_notice(self.conn, SAMPLE_TENDER)
        ingest_cf.process_cf_notice(self.conn, SAMPLE_TENDER)
        self.conn.commit()
        count = self.conn.execute(
            "SELECT COUNT(*) FROM notices WHERE ocid='cf-2021-123456'"
        ).fetchone()[0]
        self.assertEqual(count, 1)


class TestFetchCfPage(unittest.TestCase):
    def test_returns_parsed_json(self):
        import ingest_cf
        mock_body = json.dumps({
            "results": [SAMPLE_TENDER],
            "pagingInfo": {"totalResults": 1, "totalPages": 1, "currentPage": 1},
        }).encode("utf-8")

        mock_resp = MagicMock()
        mock_resp.read.return_value = mock_body
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("ingest_cf.urlopen", return_value=mock_resp):
            result = ingest_cf.fetch_cf_page(
                "2021-01-01T00:00:00", "2021-01-31T23:59:59", 1
            )

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "2021-123456")

    def test_returns_none_on_http_error(self):
        import ingest_cf
        with patch("ingest_cf.urlopen", side_effect=HTTPError(None, 500, "err", {}, None)):
            with patch("ingest_cf.time.sleep"):
                result = ingest_cf.fetch_cf_page(
                    "2021-01-01T00:00:00", "2021-01-31T23:59:59", 1
                )
        self.assertIsNone(result)
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python -m unittest test.test_ingest_cf.TestProcessCfNotice test.test_ingest_cf.TestFetchCfPage -v 2>&1 | head -10
```

Expected: `AttributeError: module 'ingest_cf' has no attribute 'process_cf_notice'`

- [ ] **Step 3: Add `fetch_cf_page` and `process_cf_notice` to `agent/ingest_cf.py`**

Append to `agent/ingest_cf.py`:

```python
# ── API fetch ────────────────────────────────────────────────────────────────

def fetch_cf_page(from_date: str, to_date: str, page: int) -> dict | None:
    payload = json.dumps({
        "publishedFrom": from_date,
        "publishedTo":   to_date,
        "size":          PAGE_SIZE,
        "page":          page,
    }).encode("utf-8")

    for attempt in range(1, RETRY_MAX + 1):
        try:
            req = Request(
                CF_SEARCH_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept":       "application/json",
                    "User-Agent":   "PWIN-CompetitiveIntel/1.0",
                },
                method="POST",
            )
            with urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            log.warning("HTTP %s attempt %d", e.code, attempt)
            if e.code == 429:
                time.sleep(RETRY_DELAY * attempt)
            elif e.code >= 500:
                time.sleep(RETRY_DELAY)
            else:
                break
        except (URLError, TimeoutError, OSError) as e:
            log.warning("Network error attempt %d: %s", attempt, e)
            time.sleep(RETRY_DELAY * attempt)
        except ValueError as e:
            log.warning("Non-JSON response attempt %d: %s", attempt, e)
            time.sleep(RETRY_DELAY * attempt)
    log.error("All %d retries exhausted for page %d [%s..%s]", RETRY_MAX, page, from_date[:10], to_date[:10])
    return None


# ── Notice processor ─────────────────────────────────────────────────────────

def process_cf_notice(conn: sqlite3.Connection, notice: dict) -> dict:
    counts = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0}

    org = notice.get("organisation") or notice.get("buyerOrganisation") or {}
    if not org or not org.get("name"):
        log.debug("Notice %s has no organisation — skipping", notice.get("id"))
        return counts

    # Buyer
    buyer_row = _cf_buyer_row(org)
    db_utils.upsert_buyer_row(conn, buyer_row)
    buyer_id = buyer_row["id"]
    counts["buyers"] += 1

    # Notice
    notice_row = _cf_notice_row(notice, buyer_id)
    ocid = notice_row["ocid"]
    db_utils.upsert_notice_row(conn, notice_row)
    counts["notices"] += 1

    # CPV codes — CF uses industryCodes or cpvCodes
    for cpv in (notice.get("industryCodes") or notice.get("cpvCodes") or []):
        code = cpv.get("code") or cpv.get("id")
        if code:
            db_utils.upsert_cpv_row(conn, ocid, str(code),
                                    cpv.get("label") or cpv.get("description") or "")

    # Award + suppliers (award notices only)
    award_row = _cf_award_row(notice, ocid)
    if award_row:
        db_utils.upsert_award_row(conn, award_row)
        award_id = award_row["id"]
        counts["awards"] += 1

        for sup in (notice.get("suppliers") or notice.get("awardedSuppliers") or []):
            sup_row = _cf_supplier_row(sup)
            db_utils.upsert_supplier_row(conn, sup_row)
            db_utils.link_award_supplier(conn, award_id, sup_row["id"])
            counts["suppliers"] += 1

    return counts
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
python -m unittest test.test_ingest_cf -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add agent/ingest_cf.py test/test_ingest_cf.py
git commit -m "feat: add CF API fetch and process_cf_notice"
```

---

## Task 6: CF `main()` and date-window ingest

**Files:**
- Modify: `agent/ingest_cf.py` (add `_date_windows`, `ingest_window`, `main`)

- [ ] **Step 1: Append `_date_windows`, `ingest_window`, and `main` to `agent/ingest_cf.py`**

```python
# ── Date windowing ────────────────────────────────────────────────────────────

def _date_windows(from_date: str, to_date: str):
    """Yield (from_iso, to_iso) monthly windows between two ISO date strings."""
    start = datetime.fromisoformat(from_date[:10])
    end   = datetime.fromisoformat(to_date[:10])
    while start <= end:
        # Last day of the current month
        if start.month == 12:
            month_end = start.replace(day=31)
        else:
            month_end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        window_end = min(month_end, end)
        yield (
            start.strftime("%Y-%m-%dT00:00:00"),
            window_end.strftime("%Y-%m-%dT23:59:59"),
        )
        start = window_end + timedelta(days=1)


def ingest_window(
    conn: sqlite3.Connection,
    from_date: str,
    to_date: str,
    limit: int | None = None,
) -> dict:
    total = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0}
    processed = 0
    page = 1

    while True:
        log.info("CF page %d  [%s → %s]", page, from_date[:10], to_date[:10])
        data = fetch_cf_page(from_date, to_date, page)
        if not data:
            log.error("Failed to fetch page %d — aborting this window", page)
            break

        results = data.get("results") or data.get("releases") or []
        if not results:
            log.info("No results on page %d — window done", page)
            break

        for notice in results:
            counts = process_cf_notice(conn, notice)
            for k in total:
                total[k] += counts.get(k, 0)
            processed += 1
            if limit and processed >= limit:
                log.info("Reached --limit %d", limit)
                conn.commit()
                return total

        conn.commit()

        paging = data.get("pagingInfo") or data.get("paginationResponse") or {}
        total_pages = paging.get("totalPages") or (
            (paging.get("totalResults", 0) + PAGE_SIZE - 1) // PAGE_SIZE
        )
        if page >= (total_pages or 1):
            break
        page += 1
        time.sleep(1.0)

    return total


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PWIN Competitive Intel — Contracts Finder ingest")
    parser.add_argument("--from", dest="from_date",
                        help="Start date ISO (default: cf_last_date stored in DB)")
    parser.add_argument("--limit", type=int,
                        help="Max notices per run (testing)")
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    if args.from_date:
        start = args.from_date
        log.info("CF ingest from %s (--from flag)", start[:10])
    else:
        start = db_utils.get_ingest_state(conn, CF_STATE_KEY) or "2021-01-01T00:00:00"
        log.info("CF ingest from %s (stored cursor)", start[:10])

    log.info("CF ingest to   %s", now[:10])

    grand_total = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0}
    last_window_end = None

    try:
        for from_dt, to_dt in _date_windows(start, now):
            window = ingest_window(conn, from_dt, to_dt, args.limit)
            for k in grand_total:
                grand_total[k] += window.get(k, 0)
            last_window_end = to_dt
            if args.limit and grand_total["notices"] >= args.limit:
                break
    except KeyboardInterrupt:
        log.warning("Interrupted — progress committed up to last window")
    except Exception as e:
        log.error("CF ingest aborted: %s", e)
        raise
    finally:
        if last_window_end:
            db_utils.set_ingest_state(conn, CF_STATE_KEY, last_window_end[:19])
            log.info("CF cursor advanced to %s", last_window_end[:10])

        log.info("=" * 60)
        log.info("CF ingest complete")
        log.info("  Notices    : %d", grand_total["notices"])
        log.info("  Awards     : %d", grand_total["awards"])
        log.info("  Buyers     : %d", grand_total["buyers"])
        log.info("  Suppliers  : %d", grand_total["suppliers"])
        conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Live smoke test — 10 notices from CF**

```bash
cd pwin-competitive-intel
python agent/ingest_cf.py --limit 10
```

Expected output:
```
HH:MM:SS  INFO     Schema initialised
HH:MM:SS  INFO     CF ingest from 2021-01-01 (stored cursor)
HH:MM:SS  INFO     CF page 1  [2021-01-01 -> 2021-01-31]
HH:MM:SS  INFO     CF ingest complete
  Notices    : 10
```

> **Important:** If field names in the live response differ from SAMPLE_TENDER (e.g. `organisation` is actually `buyerOrganisation`, or `isSuitableForSme` is `suitableForSme`), update `_cf_buyer_row`, `_cf_notice_row`, `_cf_award_row`, and `_cf_supplier_row` accordingly, then re-run the unit tests.

- [ ] **Step 3: Verify rows in DB**

```bash
python queries/queries.py summary
```

Expected: CF row in the per-source breakdown shows notices > 0.

- [ ] **Step 4: Commit**

```bash
git add agent/ingest_cf.py
git commit -m "feat: add CF ingest main() with date-window pagination and state management"
```

---

## Task 7: Scheduler + GitHub Actions

**Files:**
- Modify: `agent/scheduler.py`
- Modify: `.github/workflows/ingest.yml` (at repo root, not nested)

- [ ] **Step 1: Update `agent/scheduler.py`**

Replace the entire file contents with:

```python
#!/usr/bin/env python3
"""
PWIN Competitive Intelligence — Scheduler
==========================================
Nightly wrapper: FTS ingest → CF ingest → CH enrichment.
CF failure is non-fatal; FTS failure causes non-zero exit.
"""

import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / f"ingest_{datetime.now().strftime('%Y%m')}.log"),
    ],
)
log = logging.getLogger("scheduler")

INGEST_SCRIPT    = Path(__file__).parent / "ingest.py"
INGEST_CF_SCRIPT = Path(__file__).parent / "ingest_cf.py"


def run_script(script: Path, label: str) -> int:
    log.info("Starting %s", label)
    result = subprocess.run([sys.executable, str(script)], capture_output=False)
    if result.returncode == 0:
        log.info("%s completed successfully", label)
    else:
        log.error("%s failed with exit code %d", label, result.returncode)
    return result.returncode


if __name__ == "__main__":
    fts_rc = run_script(INGEST_SCRIPT, "FTS ingest")
    cf_rc  = run_script(INGEST_CF_SCRIPT, "CF ingest")  # non-fatal in v1
    if cf_rc != 0:
        log.warning("CF ingest failed — continuing (non-fatal)")
    sys.exit(0 if fts_rc == 0 else fts_rc)
```

- [ ] **Step 2: Update `.github/workflows/ingest.yml`**

Add one step after `Run ingest` and before `Enrich suppliers from Companies House`. The file lives at the **repo root** `.github/workflows/ingest.yml`. Add:

```yaml
      - name: Run CF ingest
        run: python agent/ingest_cf.py
        continue-on-error: true
```

Full updated steps section (replacing the existing `steps:` block):

```yaml
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Set up Node.js (for wrangler)
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Restore database from cache
        uses: actions/cache@v4
        with:
          path: pwin-competitive-intel/db/bid_intel.db
          key: bid-intel-db-${{ github.run_number }}
          restore-keys: |
            bid-intel-db-

      - name: Run FTS ingest
        run: python agent/ingest.py

      - name: Run CF ingest
        run: python agent/ingest_cf.py
        continue-on-error: true

      - name: Enrich suppliers from Companies House
        if: env.COMPANIES_HOUSE_API_KEY != ''
        env:
          COMPANIES_HOUSE_API_KEY: ${{ secrets.COMPANIES_HOUSE_API_KEY }}
        run: python agent/enrich-ch.py --limit 1000

      - name: Export data for D1
        run: python agent/sync-d1.py

      - name: Sync to Cloudflare D1
        if: env.CLOUDFLARE_API_TOKEN != ''
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        working-directory: pwin-competitive-intel/workers
        run: npx wrangler d1 execute pwin-competitive-intel --file=../db/d1-sync.sql

      - name: Upload database artifact
        uses: actions/upload-artifact@v4
        with:
          name: bid-intel-db-${{ github.run_id }}
          path: pwin-competitive-intel/db/bid_intel.db
          retention-days: 30
```

- [ ] **Step 3: Commit**

```bash
git add agent/scheduler.py .github/workflows/ingest.yml
git commit -m "feat: add CF ingest to nightly scheduler and GitHub Actions workflow"
```

---

## Task 8: `queries.py` per-source summary

**Files:**
- Modify: `queries/queries.py`

- [ ] **Step 1: Replace `db_summary()` with per-source breakdown**

In `queries/queries.py`, replace the `db_summary()` function (lines 59–93) with:

```python
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
        print("  " + "-" * 46)
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

    val = conn.execute("""
        SELECT SUM(value_amount_gross), AVG(value_amount_gross), MAX(value_amount_gross)
        FROM awards WHERE value_amount_gross IS NOT NULL AND value_quality IS NULL
    """).fetchone()
    if val[0]:
        print(f"\n  Total award value indexed : {fmt_gbp(val[0])}")
        print(f"  Avg award value           : {fmt_gbp(val[1])}")
        print(f"  Largest single award      : {fmt_gbp(val[2])}")

    top_cpv = conn.execute("""
        SELECT code, description, COUNT(*) AS cnt
        FROM cpv_codes GROUP BY code ORDER BY cnt DESC LIMIT 10
    """).fetchall()
    if top_cpv:
        print(f"\n  Top CPV codes:")
        for r in top_cpv:
            print(f"    {r['code']}  {r['description'][:40]:<40}  ({r['cnt']} notices)")

    conn.close()
```

- [ ] **Step 2: Verify manually**

```bash
python queries/queries.py summary
```

Expected output includes:
```
  Source      Notices      Awards      Buyers   Suppliers
  ----------------------------------------------
  fts         174,823     186,241      24,103     161,119
  cf               10           0          10           0
```

(CF row counts reflect the --limit 10 smoke test from Task 6.)

- [ ] **Step 3: Commit**

```bash
git add queries/queries.py
git commit -m "feat: add per-source breakdown to queries.py db_summary"
```

---

## Task 9: Historical backfill

Once all prior tasks pass, run the 2021–present backfill. This is a one-time operation that may take several hours depending on CF API response times.

- [ ] **Step 1: Start backfill**

```bash
python agent/ingest_cf.py --from 2021-01-01
```

The cursor advances month-by-month. If interrupted, re-run without `--from` to resume from the stored cursor.

- [ ] **Step 2: Verify final summary**

```bash
python queries/queries.py summary
```

Expected: CF `notices` count in the tens of thousands.

---

## Self-Review Checklist

- **Spec coverage:** All four spec sections covered — schema migration (Task 1), db_utils (Task 2), CF ingest agent (Tasks 3–6), scheduler + GitHub Actions + queries (Tasks 7–8). Backfill from 2021 covered (Task 9).
- **Placeholder scan:** No TBDs. CF API field names noted as "verify against live response" in Task 6 Step 2.
- **Type consistency:** `_cf_award_row` returns `dict | None` and callers check for `None` before upserting. `upsert_supplier_row` returns `str` (supplier id) consistently in both db_utils and usage in ingest_cf. `_date_windows` yields tuples of `(str, str)` consumed by `ingest_window`.
- **ingest.py `init_schema` call:** Updated in Task 3 Step 8 to pass `SCHEMA_PATH` as second arg matching new db_utils signature.
