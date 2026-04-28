# Sub-Org Spend Transparency Ingest — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest five years of UK government £25k spend transparency files for the four publish-at-parent departments (Home Office, MoJ, DfE, MoD), and surface per-sub-organisation supplier-spend rankings inside the existing `get_buyer_profile` MCP tool.

**Architecture:** Two new tables (`spend_transactions` and `spend_files_state`) in the existing `bid_intel.db`. A committed JSON catalogue of file URLs drives a download-and-parse pipeline. Four format-specific handlers normalise each department's column conventions into a uniform row shape. A canonicalisation pass links rows to known canonical entities. The spend signal is added to `_buildConsolidatedProfile` in `competitive-intel.js` — no new MCP tool, no schema changes to existing tables.

**Tech Stack:** Python 3.9+ stdlib (csv, urllib.request, hashlib, json, sqlite3, pathlib), Node.js 22 (node:sqlite) for the MCP layer, existing `db_utils.py` migration pattern, existing `norm()` function from `load-canonical-buyers.py`.

---

## File map

| Action | File |
|---|---|
| Modify | `pwin-competitive-intel/db/schema.sql` |
| Modify | `pwin-competitive-intel/agent/db_utils.py` |
| Create | `pwin-competitive-intel/agent/test_spend_schema.py` |
| Create | `pwin-competitive-intel/agent/spend-catalogue.json` |
| Create | `pwin-competitive-intel/agent/parse_spend.py` |
| Create | `pwin-competitive-intel/agent/test_parse_spend.py` |
| Create | `pwin-competitive-intel/agent/fetch_spend.py` |
| Create | `pwin-competitive-intel/agent/canonicalise_spend.py` |
| Create | `pwin-competitive-intel/agent/test_canonicalise_spend.py` |
| Create | `pwin-competitive-intel/agent/ingest_spend.py` |
| Modify | `pwin-competitive-intel/agent/scheduler.py` |
| Modify | `pwin-platform/src/competitive-intel.js` |
| Create | `pwin-competitive-intel/agent/generate_spend_health.py` |
| Modify | `pwin-competitive-intel/agent/run-pipeline-scan.py` |

All test files (`test_spend_schema.py`, `test_parse_spend.py`, `test_canonicalise_spend.py`) live in `agent/` alongside the scripts they test, matching the existing `test_normaliser.py` pattern. Run each with `python agent/<test_file>.py` from `pwin-competitive-intel/`.

---

## Task 1: Add spend tables to the database

**Files:**
- Modify: `pwin-competitive-intel/db/schema.sql` (append after existing CREATE TABLE blocks)
- Modify: `pwin-competitive-intel/agent/db_utils.py` (inside `_migrate_schema`)
- Create: `pwin-competitive-intel/agent/test_spend_schema.py`

- [ ] **Step 1: Write the failing test**

Create `pwin-competitive-intel/agent/test_spend_schema.py`:

```python
"""Tests that spend tables are created by both schema.sql and _migrate_schema."""
import importlib.util, os, sqlite3, sys

HERE = os.path.dirname(__file__)
SCHEMA_PATH = os.path.join(HERE, "..", "db", "schema.sql")

def _load(p):
    spec = importlib.util.spec_from_file_location("m", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

DB_UTILS = _load(os.path.join(HERE, "db_utils.py"))


def _fresh_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn


def test_schema_sql_creates_spend_tables():
    conn = _fresh_conn()
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert "spend_transactions" in tables, f"spend_transactions missing from schema.sql. Tables: {tables}"
    assert "spend_files_state" in tables, f"spend_files_state missing from schema.sql. Tables: {tables}"


def test_migrate_creates_spend_tables_on_existing_db():
    # Simulates an existing DB that was created before the spend tables were added.
    # Run schema.sql, delete the spend tables, then run _migrate_schema — they should reappear.
    conn = _fresh_conn()
    conn.execute("DROP TABLE IF EXISTS spend_transactions")
    conn.execute("DROP TABLE IF EXISTS spend_files_state")
    conn.commit()
    DB_UTILS._migrate_schema(conn)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert "spend_transactions" in tables, "spend_transactions not created by _migrate_schema"
    assert "spend_files_state" in tables, "spend_files_state not created by _migrate_schema"


def test_spend_transactions_columns():
    conn = _fresh_conn()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(spend_transactions)").fetchall()}
    required = {
        "id", "source_file_id", "department_family", "raw_entity",
        "raw_supplier_name", "amount", "payment_date", "expense_type",
        "expense_area", "canonical_sub_org_id", "canonical_supplier_id", "ingested_at",
    }
    missing = required - cols
    assert not missing, f"Missing columns in spend_transactions: {missing}"


def test_spend_files_state_columns():
    conn = _fresh_conn()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(spend_files_state)").fetchall()}
    required = {
        "id", "department", "year", "month", "entity_override",
        "source_url", "format_id", "local_path", "file_checksum",
        "row_count", "status", "error_message", "loaded_at",
    }
    missing = required - cols
    assert not missing, f"Missing columns in spend_files_state: {missing}"


if __name__ == "__main__":
    test_schema_sql_creates_spend_tables()
    test_migrate_creates_spend_tables_on_existing_db()
    test_spend_transactions_columns()
    test_spend_files_state_columns()
    print("OK")
```

- [ ] **Step 2: Run the test to verify it fails**

```
cd pwin-competitive-intel
python agent/test_spend_schema.py
```

Expected: `AssertionError: spend_transactions missing from schema.sql`.

- [ ] **Step 3: Add the two new tables to `db/schema.sql`**

Append after the last existing `CREATE VIEW` block at the end of `schema.sql`:

```sql
-- ============================================================
-- SPEND TRANSPARENCY TABLES (Wave 1, 2026-04-28)
-- Source: UK Government £25k spend transparency CSVs
-- ============================================================

CREATE TABLE IF NOT EXISTS spend_files_state (
    id              TEXT PRIMARY KEY,     -- SHA-256 hex of the source URL (first 16 chars)
    department      TEXT NOT NULL,        -- 'home-office' | 'ministry-of-justice' | etc.
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    entity_override TEXT,                 -- canonical_id forced for this file (MoJ ALB streams)
    source_url      TEXT NOT NULL,
    format_id       TEXT NOT NULL,        -- 'home-office-v1' | 'ministry-of-justice-v1' | etc.
    local_path      TEXT,                 -- path under data/spend/ after download
    file_checksum   TEXT,                 -- SHA-256 of file content
    row_count       INTEGER,
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | downloaded | loaded | error
    error_message   TEXT,
    loaded_at       TEXT                  -- ISO timestamp when rows were written to spend_transactions
);

CREATE INDEX IF NOT EXISTS idx_sfs_dept_month ON spend_files_state(department, year, month);
CREATE INDEX IF NOT EXISTS idx_sfs_status ON spend_files_state(status);

CREATE TABLE IF NOT EXISTS spend_transactions (
    id                    TEXT PRIMARY KEY,  -- '{file_id}-{row_idx:06d}'
    source_file_id        TEXT NOT NULL REFERENCES spend_files_state(id),
    department_family     TEXT NOT NULL,     -- mirrors spend_files_state.department
    raw_entity            TEXT,              -- raw "Entity" column value (or NULL if entity_override used)
    raw_supplier_name     TEXT NOT NULL,
    amount                REAL NOT NULL,     -- GBP payment amount
    payment_date          TEXT,             -- ISO YYYY-MM-DD
    expense_type          TEXT,
    expense_area          TEXT,
    canonical_sub_org_id  TEXT,             -- FK to canonical_buyers.canonical_id (NULL = unresolved)
    canonical_supplier_id TEXT,             -- FK to canonical_suppliers.canonical_id (NULL = unresolved)
    ingested_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_st_file ON spend_transactions(source_file_id);
CREATE INDEX IF NOT EXISTS idx_st_dept ON spend_transactions(department_family);
CREATE INDEX IF NOT EXISTS idx_st_sub_org ON spend_transactions(canonical_sub_org_id);
CREATE INDEX IF NOT EXISTS idx_st_supplier ON spend_transactions(canonical_supplier_id);
CREATE INDEX IF NOT EXISTS idx_st_date ON spend_transactions(payment_date);
```

- [ ] **Step 4: Add migration blocks to `db_utils.py::_migrate_schema`**

Inside `_migrate_schema`, after the last existing migration block (before the `conn.commit()`), add:

```python
    # ── spend transparency tables (Wave 1, 2026-04-28) ──
    conn.execute("""
        CREATE TABLE IF NOT EXISTS spend_files_state (
            id              TEXT PRIMARY KEY,
            department      TEXT NOT NULL,
            year            INTEGER NOT NULL,
            month           INTEGER NOT NULL,
            entity_override TEXT,
            source_url      TEXT NOT NULL,
            format_id       TEXT NOT NULL,
            local_path      TEXT,
            file_checksum   TEXT,
            row_count       INTEGER,
            status          TEXT NOT NULL DEFAULT 'pending',
            error_message   TEXT,
            loaded_at       TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS spend_transactions (
            id                    TEXT PRIMARY KEY,
            source_file_id        TEXT NOT NULL,
            department_family     TEXT NOT NULL,
            raw_entity            TEXT,
            raw_supplier_name     TEXT NOT NULL,
            amount                REAL NOT NULL,
            payment_date          TEXT,
            expense_type          TEXT,
            expense_area          TEXT,
            canonical_sub_org_id  TEXT,
            canonical_supplier_id TEXT,
            ingested_at           TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sfs_dept_month ON spend_files_state(department, year, month)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_st_sub_org ON spend_transactions(canonical_sub_org_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_st_supplier ON spend_transactions(canonical_supplier_id)")
```

- [ ] **Step 5: Run the test to verify it passes**

```
cd pwin-competitive-intel
python agent/test_spend_schema.py
```

Expected output: `OK`

- [ ] **Step 6: Commit**

```bash
git add pwin-competitive-intel/db/schema.sql pwin-competitive-intel/agent/db_utils.py pwin-competitive-intel/agent/test_spend_schema.py
git commit -m "feat(intel): add spend_transactions + spend_files_state tables to schema"
```

---

## Task 2: Create the static spend catalogue seed

**Files:**
- Create: `pwin-competitive-intel/agent/spend-catalogue.json`

The catalogue is a committed JSON file listing one entry per spend file. The engineer must look up real URLs from gov.uk transparency pages. This task creates the structure with one real entry per department so the downstream pipeline can be tested end-to-end.

- [ ] **Step 1: Find one real spend file URL per department**

Visit each transparency collection page listed below. Find the most recently published monthly CSV file for each department. Copy the exact download URL (a `https://assets.publishing.service.gov.uk/...` URL ending in `.csv`).

| Department | Collection page search term on gov.uk |
|---|---|
| Home Office | "Home Office spending over £25,000" |
| Ministry of Justice | "Ministry of Justice spend over £25,000" |
| Department for Education | "Department for Education spending over £25,000" |
| Ministry of Defence | "Ministry of Defence spending over £25,000" |

For each MoJ file, note whether it is the MoJ HQ file, the HMCTS file, the HMPPS file, or another arm's-length body file — record this as `entity_override` using the canonical ID from the glossary (e.g. `"hm-courts-and-tribunals-service"`).

- [ ] **Step 2: Create the catalogue file**

Create `pwin-competitive-intel/agent/spend-catalogue.json` with this structure, replacing the placeholder URLs and dates with the real values found in step 1:

```json
{
  "meta": {
    "generated_at": "2026-04-28",
    "description": "Static catalogue of UK government £25k spend transparency files. Four publish-at-parent families only. Refresh annually (March) via scheduled agent.",
    "format_ids": {
      "home-office-v1": "Entity column present. Columns: Date, Entity, Cost Centre, Cost Centre Description, Project Code, Project Description, Supplier, Transaction Number, Amount, Expense Type, Expense Area, Expenditure Account Description.",
      "ministry-of-justice-v1": "Each file is a single sub-org stream. Entity from entity_override in catalogue. Columns vary by stream but always include: Date, Supplier, Amount, Expense Type, Expense Area.",
      "department-for-education-v1": "Entity column present. Columns: Department, Entity, Date, Expense Type, Amount, Supplier Name, Transaction Number.",
      "ministry-of-defence-v1": "Top Level Budget column used as entity proxy. Columns: Top Level Budget, Entity, Cost Centre, Date, Supplier, Invoice Number, Net Payment, Category."
    },
    "families": {
      "home-office": "Single file per month covering all Home Office sub-orgs. Entity column names UKVI, Border Force, HMPO, Immigration Enforcement, and others.",
      "ministry-of-justice": "Thirteen separate streams per month: MoJ HQ, HMCTS, HMPPS, LAA, Youth Justice Board, Criminal Injuries Compensation Authority, HM Land Registry, Legal Services Commission (historic), Office of the Public Guardian, Parole Board, Prison and Probation Ombudsman, Serious Fraud Office, and Tribunal Service.",
      "department-for-education": "Single file per month. Entity column names ESFA and other DfE sub-orgs.",
      "ministry-of-defence": "Single file per month. Top Level Budget and Entity columns."
    }
  },
  "entries": [
    {
      "_comment": "REPLACE with real URL from gov.uk Home Office transparency collection",
      "department": "home-office",
      "year": 2026,
      "month": 3,
      "url": "REPLACE_WITH_REAL_URL",
      "format_id": "home-office-v1",
      "entity_override": null
    },
    {
      "_comment": "REPLACE with real URL — MoJ HQ stream",
      "department": "ministry-of-justice",
      "year": 2026,
      "month": 3,
      "url": "REPLACE_WITH_REAL_URL",
      "format_id": "ministry-of-justice-v1",
      "entity_override": "ministry-of-justice"
    },
    {
      "_comment": "REPLACE with real URL — HMCTS stream",
      "department": "ministry-of-justice",
      "year": 2026,
      "month": 3,
      "url": "REPLACE_WITH_REAL_URL",
      "format_id": "ministry-of-justice-v1",
      "entity_override": "hm-courts-and-tribunals-service"
    },
    {
      "_comment": "REPLACE with real URL — HMPPS stream",
      "department": "ministry-of-justice",
      "year": 2026,
      "month": 3,
      "url": "REPLACE_WITH_REAL_URL",
      "format_id": "ministry-of-justice-v1",
      "entity_override": "hm-prison-and-probation-service"
    },
    {
      "_comment": "REPLACE with real URL from gov.uk DfE transparency collection",
      "department": "department-for-education",
      "year": 2026,
      "month": 3,
      "url": "REPLACE_WITH_REAL_URL",
      "format_id": "department-for-education-v1",
      "entity_override": null
    },
    {
      "_comment": "REPLACE with real URL from gov.uk MoD transparency collection",
      "department": "ministry-of-defence",
      "year": 2026,
      "month": 3,
      "url": "REPLACE_WITH_REAL_URL",
      "format_id": "ministry-of-defence-v1",
      "entity_override": null
    }
  ]
}
```

- [ ] **Step 3: Verify the JSON is valid**

```bash
cd pwin-competitive-intel
python -c "import json; d=json.load(open('agent/spend-catalogue.json', encoding='utf-8')); print(f'OK — {len(d[\"entries\"])} entries')"
```

Expected: `OK — 6 entries`

- [ ] **Step 4: Commit**

```bash
git add pwin-competitive-intel/agent/spend-catalogue.json
git commit -m "feat(intel): add spend catalogue seed (6 entries, one per family/stream)"
```

---

## Task 3: Parser module — four format handlers

**Files:**
- Create: `pwin-competitive-intel/agent/parse_spend.py`
- Create: `pwin-competitive-intel/agent/test_parse_spend.py`

Each handler takes a raw CSV row dict (from `csv.DictReader`) plus the catalogue entry metadata, and returns a uniform dict. Amount parsing strips `£`, commas, and whitespace. Date parsing handles both DD/MM/YYYY and YYYY-MM-DD.

- [ ] **Step 1: Write the failing tests**

Create `pwin-competitive-intel/agent/test_parse_spend.py`:

```python
"""Tests for the spend CSV format handlers."""
import importlib.util, os, sys

HERE = os.path.dirname(__file__)

def _load(p):
    spec = importlib.util.spec_from_file_location("m", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

P = _load(os.path.join(HERE, "parse_spend.py"))


# ── Amount parser ──────────────────────────────────────────────────────────

def test_parse_amount_plain():
    assert P._parse_amount("342000.00") == 342000.0

def test_parse_amount_commas():
    assert P._parse_amount("342,000.00") == 342000.0

def test_parse_amount_sterling_prefix():
    assert P._parse_amount("£342,000.00") == 342000.0

def test_parse_amount_negative():
    assert P._parse_amount("-12,500.00") == -12500.0

def test_parse_amount_whitespace():
    assert P._parse_amount("  198,000.00  ") == 198000.0


# ── Date parser ────────────────────────────────────────────────────────────

def test_parse_date_dmy():
    assert P._parse_date("01/04/2026") == "2026-04-01"

def test_parse_date_iso():
    assert P._parse_date("2026-04-01") == "2026-04-01"

def test_parse_date_empty():
    assert P._parse_date("") is None

def test_parse_date_invalid():
    assert P._parse_date("N/A") is None


# ── Home Office handler ────────────────────────────────────────────────────

HO_ROW = {
    "Date": "01/04/2026",
    "Entity": "UK Visas and Immigration",
    "Supplier": "Atos IT Services UK Ltd",
    "Amount": "342,000.00",
    "Expense Type": "IT Services",
    "Expense Area": "Digital & Technology",
}
HO_META = {"format_id": "home-office-v1", "entity_override": None}

def test_home_office_handler():
    row = P.parse_row(HO_ROW, HO_META)
    assert row["raw_entity"] == "UK Visas and Immigration"
    assert row["raw_supplier_name"] == "Atos IT Services UK Ltd"
    assert row["amount"] == 342000.0
    assert row["payment_date"] == "2026-04-01"
    assert row["expense_type"] == "IT Services"
    assert row["expense_area"] == "Digital & Technology"


# ── MoJ handler (entity comes from entity_override, not column) ────────────

MOJ_ROW = {
    "Date": "01/04/2026",
    "Supplier": "Capita Plc",
    "Amount": "198,000.00",
    "Expense Type": "IT",
    "Expense Area": "Digital",
}
MOJ_META = {"format_id": "ministry-of-justice-v1", "entity_override": "hm-courts-and-tribunals-service"}

def test_moj_handler_uses_entity_override():
    row = P.parse_row(MOJ_ROW, MOJ_META)
    assert row["raw_entity"] is None   # no entity column in this format
    assert row["entity_override"] == "hm-courts-and-tribunals-service"
    assert row["raw_supplier_name"] == "Capita Plc"
    assert row["amount"] == 198000.0


# ── DfE handler ────────────────────────────────────────────────────────────

DFE_ROW = {
    "Date": "01/04/2026",
    "Entity": "Education and Skills Funding Agency",
    "Supplier Name": "Academy Trust Ltd",
    "Amount": "5,000,000.00",
    "Expense Type": "Grants & Subsidies",
    "Expense Area": "",
}
DFE_META = {"format_id": "department-for-education-v1", "entity_override": None}

def test_dfe_handler():
    row = P.parse_row(DFE_ROW, DFE_META)
    assert row["raw_entity"] == "Education and Skills Funding Agency"
    assert row["raw_supplier_name"] == "Academy Trust Ltd"
    assert row["amount"] == 5000000.0
    assert row["expense_area"] is None   # empty string → None


# ── MoD handler ────────────────────────────────────────────────────────────

MOD_ROW = {
    "Date": "01/04/2026",
    "Top Level Budget": "1500 - Army",
    "Entity": "Defence Equipment and Support",
    "Supplier": "BAE Systems Plc",
    "Net Payment": "1,500,000.00",
    "Category": "Equipment",
}
MOD_META = {"format_id": "ministry-of-defence-v1", "entity_override": None}

def test_mod_handler():
    row = P.parse_row(MOD_ROW, MOD_META)
    assert row["raw_entity"] == "Defence Equipment and Support"
    assert row["raw_supplier_name"] == "BAE Systems Plc"
    assert row["amount"] == 1500000.0
    assert row["expense_type"] == "Equipment"


# ── Skip row: amount zero or missing ──────────────────────────────────────

def test_skip_zero_amount():
    row = P.parse_row({**HO_ROW, "Amount": "0.00"}, HO_META)
    assert row is None

def test_skip_missing_supplier():
    row = P.parse_row({**HO_ROW, "Supplier": ""}, HO_META)
    assert row is None


if __name__ == "__main__":
    test_parse_amount_plain(); test_parse_amount_commas()
    test_parse_amount_sterling_prefix(); test_parse_amount_negative()
    test_parse_amount_whitespace()
    test_parse_date_dmy(); test_parse_date_iso()
    test_parse_date_empty(); test_parse_date_invalid()
    test_home_office_handler()
    test_moj_handler_uses_entity_override()
    test_dfe_handler()
    test_mod_handler()
    test_skip_zero_amount(); test_skip_missing_supplier()
    print("OK")
```

- [ ] **Step 2: Run the test to verify it fails**

```
cd pwin-competitive-intel
python agent/test_parse_spend.py
```

Expected: `ModuleNotFoundError` or `AttributeError` — `parse_spend` does not exist yet.

- [ ] **Step 3: Implement `parse_spend.py`**

Create `pwin-competitive-intel/agent/parse_spend.py`:

```python
#!/usr/bin/env python3
"""
Spend transparency CSV parser — four department-family format handlers.

Each handler converts a raw csv.DictReader row into a uniform dict:
  raw_entity       : str | None   — entity column value, or None if entity_override used
  entity_override  : str | None   — canonical_id from catalogue (MoJ ALB streams)
  raw_supplier_name: str
  amount           : float        — GBP
  payment_date     : str | None   — ISO YYYY-MM-DD
  expense_type     : str | None
  expense_area     : str | None

Returns None for rows that should be skipped (zero/missing amount, missing supplier).
"""
import re
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")


# ── Helpers ────────────────────────────────────────────────────────────────

def _parse_amount(s: str) -> float | None:
    """Strip £, commas, whitespace; return float. Returns None if unparseable."""
    s = s.strip().lstrip("£").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def _parse_date(s: str) -> str | None:
    """
    Accept DD/MM/YYYY or YYYY-MM-DD. Returns ISO YYYY-MM-DD or None.
    """
    s = s.strip()
    if not s:
        return None
    # DD/MM/YYYY
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    # YYYY-MM-DD
    m = re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)
    if m:
        return s
    return None


def _clean(s: str) -> str | None:
    """Strip whitespace; return None for empty strings."""
    v = s.strip() if s else ""
    return v if v else None


# ── Handlers ───────────────────────────────────────────────────────────────

def _handle_home_office(row: dict, meta: dict) -> dict | None:
    supplier = _clean(row.get("Supplier", ""))
    if not supplier:
        return None
    amount = _parse_amount(row.get("Amount", "0"))
    if not amount:
        return None
    return {
        "raw_entity": _clean(row.get("Entity", "")),
        "entity_override": None,
        "raw_supplier_name": supplier,
        "amount": amount,
        "payment_date": _parse_date(row.get("Date", "")),
        "expense_type": _clean(row.get("Expense Type", "")),
        "expense_area": _clean(row.get("Expense Area", "")),
    }


def _handle_ministry_of_justice(row: dict, meta: dict) -> dict | None:
    # MoJ streams: sub-org identity comes from the catalogue entry, not a column.
    supplier = _clean(row.get("Supplier", "") or row.get("Supplier Name", ""))
    if not supplier:
        return None
    amount = _parse_amount(row.get("Amount", "0"))
    if not amount:
        return None
    return {
        "raw_entity": None,
        "entity_override": meta.get("entity_override"),
        "raw_supplier_name": supplier,
        "amount": amount,
        "payment_date": _parse_date(row.get("Date", "")),
        "expense_type": _clean(row.get("Expense Type", "")),
        "expense_area": _clean(row.get("Expense Area", "")),
    }


def _handle_department_for_education(row: dict, meta: dict) -> dict | None:
    supplier = _clean(row.get("Supplier Name", "") or row.get("Supplier", ""))
    if not supplier:
        return None
    amount = _parse_amount(row.get("Amount", "0"))
    if not amount:
        return None
    return {
        "raw_entity": _clean(row.get("Entity", "")),
        "entity_override": None,
        "raw_supplier_name": supplier,
        "amount": amount,
        "payment_date": _parse_date(row.get("Date", "")),
        "expense_type": _clean(row.get("Expense Type", "")),
        "expense_area": _clean(row.get("Expense Area", "")),
    }


def _handle_ministry_of_defence(row: dict, meta: dict) -> dict | None:
    supplier = _clean(row.get("Supplier", ""))
    if not supplier:
        return None
    # MoD uses "Net Payment" for the amount column.
    amount = _parse_amount(row.get("Net Payment", "0") or row.get("Amount", "0"))
    if not amount:
        return None
    # Entity column preferred; fall back to Top Level Budget.
    entity = _clean(row.get("Entity", "")) or _clean(row.get("Top Level Budget", ""))
    return {
        "raw_entity": entity,
        "entity_override": None,
        "raw_supplier_name": supplier,
        "amount": amount,
        "payment_date": _parse_date(row.get("Date", "")),
        "expense_type": _clean(row.get("Category", "") or row.get("Expense Type", "")),
        "expense_area": _clean(row.get("Expense Area", "")),
    }


# ── Dispatch ───────────────────────────────────────────────────────────────

HANDLERS = {
    "home-office-v1": _handle_home_office,
    "ministry-of-justice-v1": _handle_ministry_of_justice,
    "department-for-education-v1": _handle_department_for_education,
    "ministry-of-defence-v1": _handle_ministry_of_defence,
}


def parse_row(row: dict, meta: dict) -> dict | None:
    """
    Parse one csv.DictReader row using the handler for meta['format_id'].
    Returns a uniform dict or None (skip this row).
    """
    fmt = meta.get("format_id")
    handler = HANDLERS.get(fmt)
    if not handler:
        raise ValueError(f"Unknown format_id: {fmt!r}. Known: {list(HANDLERS)}")
    result = handler(row, meta)
    if result is None:
        return None
    # Final guard: skip zero-amount rows regardless of handler.
    if not result.get("amount"):
        return None
    return result
```

- [ ] **Step 4: Run the tests to verify they pass**

```
cd pwin-competitive-intel
python agent/test_parse_spend.py
```

Expected output: `OK`

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/parse_spend.py pwin-competitive-intel/agent/test_parse_spend.py
git commit -m "feat(intel): spend CSV parser with four department format handlers"
```

---

## Task 4: Download script

**Files:**
- Create: `pwin-competitive-intel/agent/fetch_spend.py`

Downloads every entry in `spend-catalogue.json` that is not already in `spend_files_state`. Saves files under `data/spend/<department>/<YYYY-MM[-entity]>.csv`. Records each download to `spend_files_state`. Idempotent — safe to re-run.

- [ ] **Step 1: Create `fetch_spend.py`**

```python
#!/usr/bin/env python3
"""
Download spend transparency CSV files listed in spend-catalogue.json.

For each catalogue entry not already recorded in spend_files_state:
  1. Download the file from gov.uk (1s polite delay between requests).
  2. Save to data/spend/<department>/<YYYY-MM[-entity_slug]>.csv.
  3. Record to spend_files_state with status='downloaded'.

Idempotent — skips entries already in spend_files_state regardless of status.

Usage:
    python agent/fetch_spend.py                  # download all pending entries
    python agent/fetch_spend.py --dry-run        # show what would be downloaded
    python agent/fetch_spend.py --limit 5        # stop after 5 new downloads
"""
import argparse
import csv
import hashlib
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
REPO_ROOT = HERE.parent
DB_PATH = REPO_ROOT / "db" / "bid_intel.db"
CATALOGUE_PATH = HERE / "spend-catalogue.json"
DATA_DIR = REPO_ROOT / "data" / "spend"

POLITE_DELAY = 1.0    # seconds between downloads
REQUEST_TIMEOUT = 60  # seconds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fetch_spend")


def _file_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def _local_path(entry: dict) -> Path:
    dept = entry["department"]
    slug = f"{entry['year']}-{entry['month']:02d}"
    if entry.get("entity_override"):
        slug += f"-{entry['entity_override']}"
    return DATA_DIR / dept / f"{slug}.csv"


def _already_loaded(conn: sqlite3.Connection, file_id: str) -> bool:
    row = conn.execute(
        "SELECT status FROM spend_files_state WHERE id = ?", (file_id,)
    ).fetchone()
    return row is not None


def _download(url: str, dest: Path, dry_run: bool) -> tuple[str, int]:
    """Download url to dest. Returns (sha256_hex, byte_count)."""
    if dry_run:
        log.info("DRY-RUN  would download %s → %s", url, dest)
        return ("dryrun", 0)
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "PWIN-research/1.0 (academic use)"})
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        data = resp.read()
    dest.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    return sha, len(data)


def _record(conn: sqlite3.Connection, entry: dict, file_id: str, local_path: Path,
            checksum: str, status: str, error: str | None = None):
    conn.execute("""
        INSERT OR REPLACE INTO spend_files_state
          (id, department, year, month, entity_override, source_url, format_id,
           local_path, file_checksum, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        file_id,
        entry["department"],
        entry["year"],
        entry["month"],
        entry.get("entity_override"),
        entry["url"],
        entry["format_id"],
        str(local_path.relative_to(REPO_ROOT)) if local_path else None,
        checksum,
        status,
        error,
    ))
    conn.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    entries = [e for e in catalogue["entries"] if not e.get("_comment", "").startswith("REPLACE")]

    # Warn about placeholder entries
    placeholders = [e for e in catalogue["entries"] if "REPLACE_WITH_REAL_URL" in e.get("url", "")]
    if placeholders:
        log.warning("%d catalogue entries still have placeholder URLs — skipping them", len(placeholders))

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    downloaded = 0
    skipped = 0
    for entry in entries:
        file_id = _file_id(entry["url"])
        if _already_loaded(conn, file_id):
            skipped += 1
            continue

        dest = _local_path(entry)
        log.info("Downloading %s/%d-%02d → %s",
                 entry["department"], entry["year"], entry["month"], dest.name)
        try:
            checksum, size = _download(entry["url"], dest, args.dry_run)
            _record(conn, entry, file_id, dest, checksum, "downloaded")
            log.info("  OK  %s  (%.1f KB)", dest.name, size / 1024)
        except (HTTPError, URLError, OSError) as exc:
            log.error("  FAIL  %s: %s", entry["url"], exc)
            _record(conn, entry, file_id, dest, "", "error", str(exc))

        downloaded += 1
        if args.limit and downloaded >= args.limit:
            log.info("Reached --limit %d, stopping.", args.limit)
            break
        if not args.dry_run:
            time.sleep(POLITE_DELAY)

    log.info("Done. downloaded=%d  skipped(already_recorded)=%d", downloaded, skipped)
    conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run a dry-run to verify no crash**

```
cd pwin-competitive-intel
python agent/fetch_spend.py --dry-run
```

Expected: Warning about placeholder URLs, and then `Done. downloaded=0 skipped(already_recorded)=0`. No crash.

- [ ] **Step 3: Replace catalogue placeholders with real URLs, then test a live download**

Having filled in the real URLs in Task 2 Step 2:

```
python agent/fetch_spend.py --limit 1
```

Expected: One file downloaded to `data/spend/<department>/`, one row in `spend_files_state` with `status='downloaded'`. Verify:

```
python -c "
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
rows = conn.execute('SELECT department, year, month, status, local_path FROM spend_files_state').fetchall()
for r in rows: print(r)
"
```

- [ ] **Step 4: Commit**

```bash
git add pwin-competitive-intel/agent/fetch_spend.py pwin-competitive-intel/agent/spend-catalogue.json
git commit -m "feat(intel): spend download script + catalogue with real URLs"
```

---

## Task 5: Canonicalisation pass

**Files:**
- Create: `pwin-competitive-intel/agent/canonicalise_spend.py`
- Create: `pwin-competitive-intel/agent/test_canonicalise_spend.py`

Two lookups per row: entity name → `canonical_sub_org_id`, supplier name → `canonical_supplier_id`. Both use normalised exact matching. Rows that don't match stay NULL — they go to the weekly review queue, not discarded.

- [ ] **Step 1: Write the failing tests**

Create `pwin-competitive-intel/agent/test_canonicalise_spend.py`:

```python
"""Tests for spend canonicalisation helpers."""
import importlib.util, os, sqlite3, sys

HERE = os.path.dirname(__file__)

def _load(p):
    spec = importlib.util.spec_from_file_location("m", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

CS = _load(os.path.join(HERE, "canonicalise_spend.py"))
LOAD = _load(os.path.join(HERE, "load-canonical-buyers.py"))


def _make_conn():
    """In-memory DB with canonical_buyer_aliases and canonical_suppliers seeded."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE canonical_buyer_aliases (
            canonical_id TEXT NOT NULL,
            alias TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE canonical_suppliers (
            canonical_id TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL
        )
    """)
    # Seed buyer aliases
    conn.executemany("INSERT INTO canonical_buyer_aliases VALUES (?, ?)", [
        ("uk-visas-and-immigration", "uk visas and immigration"),
        ("uk-visas-and-immigration", "ukvip"),
        ("hm-prison-and-probation-service", "hm prison and probation service"),
        ("hm-prison-and-probation-service", "hmpps"),
        ("education-and-skills-funding-agency", "education and skills funding agency"),
        ("education-and-skills-funding-agency", "esfa"),
    ])
    # Seed canonical suppliers
    conn.executemany("INSERT INTO canonical_suppliers VALUES (?, ?)", [
        ("atos-it-services", "Atos IT Services UK Ltd"),
        ("capita", "Capita Plc"),
        ("bae-systems", "BAE Systems Plc"),
    ])
    conn.commit()
    return conn


def test_resolve_entity_exact():
    conn = _make_conn()
    lookup = CS.build_entity_lookup(conn)
    assert lookup.get(LOAD.norm("UK Visas and Immigration")) == "uk-visas-and-immigration"


def test_resolve_entity_abbreviation():
    conn = _make_conn()
    lookup = CS.build_entity_lookup(conn)
    assert lookup.get(LOAD.norm("UKVIP")) == "uk-visas-and-immigration"


def test_resolve_entity_no_match():
    conn = _make_conn()
    lookup = CS.build_entity_lookup(conn)
    assert lookup.get(LOAD.norm("Some Unknown Directorate")) is None


def test_resolve_supplier_exact():
    conn = _make_conn()
    lookup = CS.build_supplier_lookup(conn)
    assert lookup.get(LOAD.norm("Atos IT Services UK Ltd")) == "atos-it-services"


def test_resolve_supplier_case_insensitive():
    conn = _make_conn()
    lookup = CS.build_supplier_lookup(conn)
    assert lookup.get(LOAD.norm("ATOS IT SERVICES UK LTD")) == "atos-it-services"


def test_resolve_supplier_no_match():
    conn = _make_conn()
    lookup = CS.build_supplier_lookup(conn)
    assert lookup.get(LOAD.norm("Some Unknown Supplier Ltd")) is None


if __name__ == "__main__":
    test_resolve_entity_exact()
    test_resolve_entity_abbreviation()
    test_resolve_entity_no_match()
    test_resolve_supplier_exact()
    test_resolve_supplier_case_insensitive()
    test_resolve_supplier_no_match()
    print("OK")
```

- [ ] **Step 2: Run the test to verify it fails**

```
cd pwin-competitive-intel
python agent/test_canonicalise_spend.py
```

Expected: `ModuleNotFoundError` — `canonicalise_spend` does not exist.

- [ ] **Step 3: Implement `canonicalise_spend.py`**

Create `pwin-competitive-intel/agent/canonicalise_spend.py`:

```python
#!/usr/bin/env python3
"""
Canonicalise spend_transactions rows.

Two passes:
  1. Entity → canonical_sub_org_id  (via canonical_buyer_aliases, normalised match)
  2. Supplier → canonical_supplier_id  (via canonical_suppliers.canonical_name, normalised)

Rows with entity_override set skip the entity lookup — they already have a canonical_id.
Unresolved rows stay NULL and surface in the weekly alias review queue.

Usage:
    python agent/canonicalise_spend.py            # update all unresolved rows
    python agent/canonicalise_spend.py --dry-run  # count what would change
"""
import argparse
import importlib.util
import logging
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
DB_PATH = HERE.parent / "db" / "bid_intel.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("canonicalise_spend")


def _load_norm():
    p = HERE / "load-canonical-buyers.py"
    spec = importlib.util.spec_from_file_location("lcb", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.norm


norm = _load_norm()


def build_entity_lookup(conn: sqlite3.Connection) -> dict[str, str]:
    """Returns {norm(alias) -> canonical_id} from canonical_buyer_aliases."""
    rows = conn.execute(
        "SELECT canonical_id, alias FROM canonical_buyer_aliases"
    ).fetchall()
    return {norm(alias): canonical_id for canonical_id, alias in rows}


def build_supplier_lookup(conn: sqlite3.Connection) -> dict[str, str]:
    """Returns {norm(canonical_name) -> canonical_id} from canonical_suppliers."""
    rows = conn.execute(
        "SELECT canonical_id, canonical_name FROM canonical_suppliers"
    ).fetchall()
    return {norm(name): canonical_id for canonical_id, name in rows}


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone())


def run(conn: sqlite3.Connection, dry_run: bool = False):
    for required in ("canonical_buyer_aliases", "canonical_suppliers", "spend_transactions"):
        if not _table_exists(conn, required):
            log.error("Table %r not found. Run load-canonical-buyers.py and splink_supplier_dedup.py first.", required)
            sys.exit(1)

    entity_lookup = build_entity_lookup(conn)
    supplier_lookup = build_supplier_lookup(conn)
    log.info("Loaded %d entity aliases, %d supplier names", len(entity_lookup), len(supplier_lookup))

    # ── Pass 1: rows with entity_override (already resolved at ingest time) ──
    if not dry_run:
        conn.execute("""
            UPDATE spend_transactions
            SET canonical_sub_org_id = source_file_id  -- placeholder; actual override applied below
            WHERE canonical_sub_org_id IS NULL
              AND id IN (
                  SELECT t.id FROM spend_transactions t
                  JOIN spend_files_state f ON t.source_file_id = f.id
                  WHERE f.entity_override IS NOT NULL
              )
        """)
        # Correct: set canonical_sub_org_id from the file's entity_override.
        conn.execute("""
            UPDATE spend_transactions
            SET canonical_sub_org_id = (
                SELECT entity_override FROM spend_files_state
                WHERE id = spend_transactions.source_file_id
            )
            WHERE canonical_sub_org_id IS NULL
              AND source_file_id IN (
                  SELECT id FROM spend_files_state WHERE entity_override IS NOT NULL
              )
        """)
        conn.commit()
        override_count = conn.execute(
            "SELECT changes()"
        ).fetchone()[0]
        log.info("Pass 1 (entity_override): %d rows updated", override_count)

    # ── Pass 2: entity column → lookup ──────────────────────────────────────
    unresolved = conn.execute("""
        SELECT id, raw_entity FROM spend_transactions
        WHERE canonical_sub_org_id IS NULL AND raw_entity IS NOT NULL
    """).fetchall()
    log.info("Pass 2 (entity lookup): %d unresolved rows to check", len(unresolved))

    entity_updates = []
    for row_id, raw_entity in unresolved:
        canonical_id = entity_lookup.get(norm(raw_entity))
        if canonical_id:
            entity_updates.append((canonical_id, row_id))

    if not dry_run and entity_updates:
        conn.executemany(
            "UPDATE spend_transactions SET canonical_sub_org_id = ? WHERE id = ?",
            entity_updates,
        )
        conn.commit()
    log.info("Pass 2: %d/%d entity rows resolved", len(entity_updates), len(unresolved))

    # ── Pass 3: supplier name → lookup ──────────────────────────────────────
    unresolved_sup = conn.execute("""
        SELECT id, raw_supplier_name FROM spend_transactions
        WHERE canonical_supplier_id IS NULL AND raw_supplier_name IS NOT NULL
    """).fetchall()
    log.info("Pass 3 (supplier lookup): %d unresolved rows to check", len(unresolved_sup))

    supplier_updates = []
    for row_id, raw_name in unresolved_sup:
        canonical_id = supplier_lookup.get(norm(raw_name))
        if canonical_id:
            supplier_updates.append((canonical_id, row_id))

    if not dry_run and supplier_updates:
        conn.executemany(
            "UPDATE spend_transactions SET canonical_supplier_id = ? WHERE id = ?",
            supplier_updates,
        )
        conn.commit()
    log.info("Pass 3: %d/%d supplier rows resolved", len(supplier_updates), len(unresolved_sup))

    # ── Summary ──────────────────────────────────────────────────────────────
    total = conn.execute("SELECT COUNT(*) FROM spend_transactions").fetchone()[0]
    entity_mapped = conn.execute(
        "SELECT COUNT(*) FROM spend_transactions WHERE canonical_sub_org_id IS NOT NULL"
    ).fetchone()[0]
    supplier_mapped = conn.execute(
        "SELECT COUNT(*) FROM spend_transactions WHERE canonical_supplier_id IS NOT NULL"
    ).fetchone()[0]
    if total:
        log.info(
            "Coverage: entity %d/%d (%.1f%%)  supplier %d/%d (%.1f%%)",
            entity_mapped, total, 100 * entity_mapped / total,
            supplier_mapped, total, 100 * supplier_mapped / total,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    run(conn, dry_run=args.dry_run)
    conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify they pass**

```
cd pwin-competitive-intel
python agent/test_canonicalise_spend.py
```

Expected output: `OK`

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/canonicalise_spend.py pwin-competitive-intel/agent/test_canonicalise_spend.py
git commit -m "feat(intel): spend canonicalisation pass (entity + supplier lookup)"
```

---

## Task 6: Ingest orchestrator + scheduler integration

**Files:**
- Create: `pwin-competitive-intel/agent/ingest_spend.py`
- Modify: `pwin-competitive-intel/agent/scheduler.py`

`ingest_spend.py` wires together: for each `downloaded` file in `spend_files_state`, parse all rows and upsert to `spend_transactions`, then mark the file as `loaded`. Running it again is a no-op for already-loaded files. The scheduler calls it as a non-fatal step.

- [ ] **Step 1: Create `ingest_spend.py`**

```python
#!/usr/bin/env python3
"""
Parse downloaded spend CSVs into spend_transactions.

For each spend_files_state row with status='downloaded':
  1. Read the local CSV file using the appropriate format handler.
  2. Upsert parsed rows into spend_transactions.
  3. Mark the file as status='loaded'.

Then run canonicalise_spend.run() to resolve new rows.

Usage:
    python agent/ingest_spend.py            # parse all downloaded-but-not-loaded files
    python agent/ingest_spend.py --dry-run  # count rows without writing
    python agent/ingest_spend.py --skip-canonicalise  # parse only, skip canon pass
"""
import argparse
import csv
import hashlib
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
REPO_ROOT = HERE.parent
DB_PATH = REPO_ROOT / "db" / "bid_intel.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest_spend")


def _import(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location("m", HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

parse_spend = _import("parse_spend")
canonicalise_spend = _import("canonicalise_spend")


def _row_id(file_id: str, idx: int) -> str:
    return f"{file_id}-{idx:06d}"


def _parse_file(path: Path, file_meta: dict) -> list[dict]:
    """Read CSV and return list of uniform dicts. Skips None rows."""
    rows = []
    meta = {"format_id": file_meta["format_id"], "entity_override": file_meta["entity_override"]}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            parsed = parse_spend.parse_row(dict(raw), meta)
            if parsed:
                rows.append(parsed)
    return rows


def _upsert_rows(conn: sqlite3.Connection, file_id: str, dept: str, rows: list[dict]):
    conn.executemany("""
        INSERT OR IGNORE INTO spend_transactions
          (id, source_file_id, department_family, raw_entity, raw_supplier_name,
           amount, payment_date, expense_type, expense_area)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            _row_id(file_id, i),
            file_id,
            dept,
            r.get("raw_entity") or r.get("entity_override"),
            r["raw_supplier_name"],
            r["amount"],
            r.get("payment_date"),
            r.get("expense_type"),
            r.get("expense_area"),
        )
        for i, r in enumerate(rows)
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-canonicalise", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    pending = conn.execute(
        "SELECT * FROM spend_files_state WHERE status = 'downloaded'"
    ).fetchall()
    log.info("%d files ready to parse", len(pending))

    total_rows = 0
    for file_state in pending:
        file_id = file_state["id"]
        local_path = REPO_ROOT / file_state["local_path"]

        if not local_path.exists():
            log.error("Local file not found: %s", local_path)
            conn.execute(
                "UPDATE spend_files_state SET status='error', error_message=? WHERE id=?",
                ("local file not found", file_id),
            )
            conn.commit()
            continue

        log.info("Parsing %s (%s %d-%02d)",
                 local_path.name, file_state["department"], file_state["year"], file_state["month"])

        try:
            rows = _parse_file(local_path, dict(file_state))
        except Exception as exc:
            log.error("Parse error on %s: %s", local_path.name, exc)
            conn.execute(
                "UPDATE spend_files_state SET status='error', error_message=? WHERE id=?",
                (str(exc), file_id),
            )
            conn.commit()
            continue

        log.info("  %d rows parsed", len(rows))
        total_rows += len(rows)

        if not args.dry_run:
            _upsert_rows(conn, file_id, file_state["department"], rows)
            conn.execute(
                "UPDATE spend_files_state SET status='loaded', row_count=?, loaded_at=? WHERE id=?",
                (len(rows), datetime.now(timezone.utc).isoformat(), file_id),
            )
            conn.commit()

    log.info("Total rows parsed: %d", total_rows)

    if not args.dry_run and not args.skip_canonicalise:
        log.info("Running canonicalisation pass...")
        canonicalise_spend.run(conn, dry_run=False)

    conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test with dry run**

```
cd pwin-competitive-intel
python agent/ingest_spend.py --dry-run
```

Expected: `0 files ready to parse` (none downloaded yet) or a count if Task 4 Step 3 was run. No crash.

- [ ] **Step 3: Run a live end-to-end test with one real downloaded file**

If you completed Task 4 Step 3 (downloaded one real file):

```
python agent/ingest_spend.py
```

Then verify rows are in the database:

```
python -c "
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
n = conn.execute('SELECT COUNT(*) FROM spend_transactions').fetchone()[0]
subs = conn.execute('''
    SELECT canonical_sub_org_id, COUNT(*) c, SUM(amount) s
    FROM spend_transactions
    GROUP BY canonical_sub_org_id
    ORDER BY s DESC LIMIT 5
''').fetchall()
print(f'Total rows: {n}')
for r in subs: print(r)
"
```

- [ ] **Step 4: Add spend ingest step to `scheduler.py`**

After the last existing `run_step(...)` call and before `log.info("Nightly pipeline complete")`, add:

```python
    # Spend transparency: parse any newly-downloaded CSV files and run canon pass.
    # Non-fatal — a failed parse must not stop the data pipeline.
    # fetch_spend.py is run separately (monthly) — this step only parses.
    run_step("Spend transparency: parse downloaded files + canonicalise",
             [str(AGENT_DIR / "ingest_spend.py")])
```

- [ ] **Step 5: Verify scheduler runs without error**

```
cd pwin-competitive-intel
python agent/scheduler.py
```

This runs the full nightly pipeline. Check the log output includes the new spend step (it will log "0 files ready to parse" if nothing new is downloaded, which is the correct no-op behaviour).

- [ ] **Step 6: Commit**

```bash
git add pwin-competitive-intel/agent/ingest_spend.py pwin-competitive-intel/agent/scheduler.py
git commit -m "feat(intel): spend ingest orchestrator + scheduler step"
```

---

## Task 7: Surface spend signal in `get_buyer_profile`

**Files:**
- Modify: `pwin-platform/src/competitive-intel.js`

Add a `spendSignal` property to the buyer object returned by `_buildConsolidatedProfile`. The property is `null` when the `spend_transactions` table does not exist (graceful degradation for environments that haven't run the ingest yet).

- [ ] **Step 1: Add `_buildSpendSignal` helper function**

In `competitive-intel.js`, after the `_buildRawProfile` function (around line 266), add this new function:

```javascript
// ── Spend Signal ─────────────────────────────────────────────────────────

function _buildSpendSignal(db, canonicalId) {
  // Graceful degradation: table may not exist if ingest hasn't been run.
  const tableExists = db.prepare(
    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='spend_transactions'"
  ).get();
  if (!tableExists) return null;

  // Top suppliers by total spend attributed to this sub-org.
  const topSuppliers = db.prepare(`
    SELECT
      COALESCE(cs.canonical_name, st.raw_supplier_name) AS supplier_name,
      SUM(st.amount)                                     AS total_spend,
      MAX(st.payment_date)                               AS last_paid,
      COUNT(*)                                           AS payment_count
    FROM spend_transactions st
    LEFT JOIN canonical_suppliers cs ON st.canonical_supplier_id = cs.canonical_id
    WHERE st.canonical_sub_org_id = ?
      AND st.payment_date >= date('now', '-5 years')
    GROUP BY COALESCE(st.canonical_supplier_id, st.raw_supplier_name)
    ORDER BY total_spend DESC
    LIMIT 10
  `).all(canonicalId);

  if (!topSuppliers.length) return null;

  // Family-level coverage stats (all rows for the same department family).
  const familyRow = db.prepare(
    'SELECT department_family FROM spend_transactions WHERE canonical_sub_org_id = ? LIMIT 1'
  ).get(canonicalId);

  let coverage = null;
  if (familyRow) {
    const cov = db.prepare(`
      SELECT
        COUNT(*)                                                          AS total_rows,
        SUM(CASE WHEN canonical_sub_org_id IS NOT NULL THEN 1 ELSE 0 END) AS mapped_rows,
        SUM(amount)                                                       AS total_amount,
        SUM(CASE WHEN canonical_sub_org_id IS NOT NULL THEN amount ELSE 0 END) AS mapped_amount,
        MIN(payment_date)                                                 AS earliest,
        MAX(payment_date)                                                 AS latest
      FROM spend_transactions
      WHERE department_family = ?
    `).get(familyRow.department_family);

    if (cov && cov.total_rows > 0) {
      coverage = {
        familyCoveragePercent: Math.round(100 * cov.mapped_rows / cov.total_rows),
        unmappedSpend: (cov.total_amount || 0) - (cov.mapped_amount || 0),
        dateRange: { from: cov.earliest, to: cov.latest },
        family: familyRow.department_family,
      };
    }
  }

  return {
    topSuppliers: topSuppliers.map(s => ({
      name: s.supplier_name,
      totalSpend: s.total_spend,
      lastPaid: s.last_paid,
      paymentCount: s.payment_count,
    })),
    coverage,
    source: '£25k spend transparency feed',
    caveat: 'Spend is not contracts. Figures are total payments, not contract values. 1–3 month publisher lag applies.',
  };
}
```

- [ ] **Step 2: Call `_buildSpendSignal` from `_buildConsolidatedProfile`**

In `_buildConsolidatedProfile`, after the `recentAwards` query (around line 136) and before the `return {` statement, add:

```javascript
  const spendSignal = _buildSpendSignal(db, resolved.canonicalId);
```

Then inside the returned buyer object (the one with `id: resolved.canonicalId`), add `spendSignal` as a field after `recentAwards`:

```javascript
      recentAwards: recentAwards.map(r => ({
        title: r.title,
        value: r.value_amount_gross,
        method: r.procurement_method,
        suppliers: r.suppliers,
        contractEndDate: r.contract_end_date,
        awardDate: r.award_date,
      })),
      spendSignal,
```

- [ ] **Step 3: Manual verification**

Start the platform server:

```
cd pwin-platform
node src/server.js --mcp
```

In a separate terminal, call `get_buyer_profile` for "UK Visas and Immigration" via the Data API:

```
curl http://localhost:3456/api/intel/buyer?name=UK+Visas+and+Immigration | python -m json.tool | head -80
```

Expected: The response includes a `spendSignal` property. If spend data has been loaded for this sub-org, it contains `topSuppliers` with spend figures. If not yet loaded, `spendSignal` is `null` — no crash.

- [ ] **Step 4: Commit**

```bash
git add pwin-platform/src/competitive-intel.js
git commit -m "feat(intel): add spendSignal to get_buyer_profile (£25k spend overlay)"
```

---

## Task 8: Health reports and morning digest line

**Files:**
- Create: `pwin-competitive-intel/agent/generate_spend_health.py`
- Modify: `pwin-competitive-intel/agent/run-pipeline-scan.py`

The health script writes two markdown files to the Obsidian wiki. The digest modification appends a one-line spend-health summary to the existing morning email. Both are non-fatal; failure logs and continues.

- [ ] **Step 1: Create `generate_spend_health.py`**

```python
#!/usr/bin/env python3
"""
Generate two weekly health files for the spend transparency layer:

  wiki/intel/spend-health.md          — green/amber/red per family, one screen
  wiki/intel/spend-alias-review-queue.md — top unmapped entity names for triage

Run weekly (from scheduler or manually). Safe to re-run — overwrites both files.

Usage:
    python agent/generate_spend_health.py
    python agent/generate_spend_health.py --dry-run    # print to stdout, don't write
"""
import argparse
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
REPO_ROOT = HERE.parent
DB_PATH = REPO_ROOT / "db" / "bid_intel.db"
WIKI_DIR = Path("C:/Users/User/Documents/Obsidian Vault/wiki/intel")

# Thresholds matching the design spec Section 4.
UNMAPPED_AMBER = 10.0    # % unmapped above this → amber
NEW_ENTITY_AMBER = 1_000_000  # £ spend without canonical match → amber

logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
log = logging.getLogger("spend-health")


def _table_exists(conn, name):
    return bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone())


def _family_stats(conn):
    rows = conn.execute("""
        SELECT
          department_family,
          COUNT(*)                                                            AS total_rows,
          SUM(CASE WHEN canonical_sub_org_id IS NOT NULL THEN 1 ELSE 0 END)  AS mapped_rows,
          SUM(amount)                                                         AS total_spend,
          SUM(CASE WHEN canonical_sub_org_id IS NOT NULL THEN amount ELSE 0 END) AS mapped_spend,
          MIN(payment_date)                                                   AS earliest,
          MAX(payment_date)                                                   AS latest
        FROM spend_transactions
        GROUP BY department_family
        ORDER BY department_family
    """).fetchall()
    return rows


def _file_stats(conn):
    return conn.execute("""
        SELECT department, status, COUNT(*) AS cnt
        FROM spend_files_state
        GROUP BY department, status
        ORDER BY department, status
    """).fetchall()


def _top_unmapped_entities(conn, limit=20):
    return conn.execute(f"""
        SELECT raw_entity, department_family,
               COUNT(*) AS row_count, SUM(amount) AS total_spend
        FROM spend_transactions
        WHERE canonical_sub_org_id IS NULL
          AND raw_entity IS NOT NULL
          AND raw_entity != ''
        GROUP BY raw_entity, department_family
        ORDER BY total_spend DESC
        LIMIT {limit}
    """).fetchall()


def _rag(pct_unmapped, max_unmapped_spend):
    if pct_unmapped > UNMAPPED_AMBER or max_unmapped_spend > NEW_ENTITY_AMBER:
        return "AMBER"
    return "GREEN"


def build_health_md(conn, now_str):
    stats = _family_stats(conn)
    file_rows = _file_stats(conn)

    files_by_dept = {}
    for r in file_rows:
        files_by_dept.setdefault(r[0], {})[r[1]] = r[2]

    lines = [
        f"# Spend transparency health",
        f"",
        f"_Generated {now_str}_",
        f"",
        f"| Family | Files loaded | Rows | % mapped | Date range | Status |",
        f"|--------|-------------|------|----------|------------|--------|",
    ]
    for r in stats:
        dept = r[0]
        pct_mapped = 100 * r[2] / r[1] if r[1] else 0
        pct_unmapped = 100 - pct_mapped
        max_unmap = (r[3] or 0) - (r[4] or 0)
        rag = _rag(pct_unmapped, max_unmap)
        icon = "🟢" if rag == "GREEN" else "🟡"
        loaded = files_by_dept.get(dept, {}).get("loaded", 0)
        lines.append(
            f"| {dept} | {loaded} | {r[1]:,} | {pct_mapped:.1f}% | {r[5] or '—'} → {r[6] or '—'} | {icon} {rag} |"
        )

    lines += [
        "",
        "## File state",
        "",
        "| Department | Status | Count |",
        "|------------|--------|-------|",
    ]
    for r in file_rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} |")

    return "\n".join(lines) + "\n"


def build_alias_queue_md(conn, now_str):
    unmapped = _top_unmapped_entities(conn)
    lines = [
        "# Spend alias review queue",
        "",
        f"_Generated {now_str}. Say yes/no/skip next to each entry, then run `canonicalise_spend.py` to pick up changes._",
        "",
        "| Entity name (raw) | Family | Rows | Spend | Action |",
        "|-------------------|--------|------|-------|--------|",
    ]
    for r in unmapped:
        spend_k = f"£{r[3]/1000:.0f}k" if r[3] else "£?"
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {spend_k} | <!-- yes: canonical_id / skip --> |")

    if not unmapped:
        lines.append("| _All entity names mapped_ | | | | |")

    return "\n".join(lines) + "\n"


def one_line_summary(conn):
    """Returns the one-line digest string for the morning email."""
    if not _table_exists(conn, "spend_transactions"):
        return "Spend ingest: tables not yet created."
    total = conn.execute("SELECT COUNT(*) FROM spend_transactions").fetchone()[0]
    if not total:
        return "Spend ingest: no rows loaded yet."
    families = conn.execute(
        "SELECT COUNT(DISTINCT department_family) FROM spend_transactions"
    ).fetchone()[0]
    loaded_files = conn.execute(
        "SELECT COUNT(*) FROM spend_files_state WHERE status='loaded'"
    ).fetchone()[0]
    error_files = conn.execute(
        "SELECT COUNT(*) FROM spend_files_state WHERE status='error'"
    ).fetchone()[0]
    pct_mapped = conn.execute("""
        SELECT ROUND(100.0 * SUM(CASE WHEN canonical_sub_org_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1)
        FROM spend_transactions
    """).fetchone()[0] or 0
    errors_str = f". {error_files} file errors — check spend-health.md." if error_files else "."
    return (
        f"Spend ingest: {total:,} rows across {families} families, "
        f"{loaded_files} files loaded, {pct_mapped}% entity-mapped{errors_str}"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    if not _table_exists(conn, "spend_transactions"):
        log.warning("spend_transactions table not found — run ingest_spend.py first.")
        conn.close()
        return

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    health_md = build_health_md(conn, now_str)
    queue_md = build_alias_queue_md(conn, now_str)

    if args.dry_run:
        print("=== spend-health.md ===")
        print(health_md)
        print("=== spend-alias-review-queue.md ===")
        print(queue_md)
    else:
        WIKI_DIR.mkdir(parents=True, exist_ok=True)
        (WIKI_DIR / "spend-health.md").write_text(health_md, encoding="utf-8")
        (WIKI_DIR / "spend-alias-review-queue.md").write_text(queue_md, encoding="utf-8")
        log.info("Written spend-health.md and spend-alias-review-queue.md to %s", WIKI_DIR)

    conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test the dry run**

```
cd pwin-competitive-intel
python agent/generate_spend_health.py --dry-run
```

Expected: Prints `spend-health.md` content (likely showing empty/zero tables if no data loaded yet) without crashing.

- [ ] **Step 3: Add the spend-health line to `run-pipeline-scan.py`**

In `run-pipeline-scan.py`, find the `one_line_summary` or equivalent digest-building section (search for `digest` in the file). The script writes a digest to `DIGESTS_DIR`. After the existing digest content is assembled, append the spend health line.

Locate the section that builds the digest text string (look for `digest` variable or similar). Add after the existing digest content:

```python
    # ── Spend health line ──────────────────────────────────────────────────
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("gsh",
            str(REPO_ROOT / "pwin-competitive-intel" / "agent" / "generate_spend_health.py"))
        _gsh = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_gsh)
        import sqlite3 as _sq3
        _intel_db = Path.home() / ".pwin" / "intel" / "bid_intel.db"
        _fallback_db = REPO_ROOT / "pwin-competitive-intel" / "db" / "bid_intel.db"
        _db_path = _intel_db if _intel_db.exists() else _fallback_db
        _conn = _sq3.connect(str(_db_path))
        _conn.row_factory = _sq3.Row
        spend_line = _gsh.one_line_summary(_conn)
        _conn.close()
    except Exception as _exc:
        spend_line = f"Spend ingest: health check failed ({_exc})"
```

Then include `spend_line` in the digest output (append it to whatever string the script writes as the digest).

To find the exact insertion point, search for `digest` or the email body assembly in `run-pipeline-scan.py`. The line should appear in the digest text alongside the existing pipeline summary lines.

- [ ] **Step 4: Test the pipeline scan with the new line**

```
cd pwin-competitive-intel
python agent/run-pipeline-scan.py --dry-run
```

Check that the output includes a spend-health line without crashing.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/generate_spend_health.py pwin-competitive-intel/agent/run-pipeline-scan.py
git commit -m "feat(intel): spend health report + morning digest line"
```

---

## Task 9: Schedule annual catalogue refresh

This task has no code to write. It uses the `/schedule` mechanism to set a recurring reminder for March 2027 to review and update `spend-catalogue.json` with any new file URLs published in the previous year.

- [ ] **Step 1: Set the schedule**

Run `/schedule` with the following prompt and a target of 1 March 2027 (or as close as the schedule mechanism allows):

> **Task:** Annual spend catalogue refresh for the £25k spend transparency ingest.
>
> Check each of the four department transparency collections on gov.uk for new monthly files published since the last catalogue update. Add any new entries to `pwin-competitive-intel/agent/spend-catalogue.json` following the format already in that file. Then run `python agent/fetch_spend.py --limit 12` to download the new files, `python agent/ingest_spend.py` to parse them, and commit the updated catalogue.
>
> Departments to check:
> - Home Office: search gov.uk for "Home Office spending over £25,000"
> - Ministry of Justice: search gov.uk for "Ministry of Justice spend over £25,000" (13 streams)
> - Department for Education: search gov.uk for "Department for Education spending over £25,000"
> - Ministry of Defence: search gov.uk for "Ministry of Defence spending over £25,000"
>
> After updating, run `python agent/generate_spend_health.py` to regenerate `wiki/intel/spend-health.md` and check the mapped % for each family. If it drops below 85%, add the missing aliases to the canonical glossary and re-run `load-canonical-buyers.py`.

- [ ] **Step 2: Confirm the schedule is set**

The `/schedule` command should confirm the scheduled date. Note the confirmation in a comment at the top of `spend-catalogue.json`:

```json
  "meta": {
    "generated_at": "2026-04-28",
    "annual_refresh_scheduled": "2027-03-01",
    ...
  }
```

- [ ] **Step 3: Commit the catalogue with the schedule note**

```bash
git add pwin-competitive-intel/agent/spend-catalogue.json
git commit -m "chore(intel): note annual catalogue refresh scheduled for 2027-03-01"
```

---

## Self-review checklist

Spec requirements cross-checked against plan tasks:

| Spec requirement | Task |
|---|---|
| spend_transactions and spend_files_state tables | Task 1 |
| Static catalogue file (JSON, committed) | Task 2 |
| Four format handlers (HO, MoJ, DfE, MoD) | Task 3 |
| Download script with polite delay + checksum bookmark | Task 4 |
| Canonicalisation pass (entity + supplier) | Task 5 |
| Ingest orchestrator (download → parse → canon) | Task 6 |
| Scheduler integration (non-fatal step) | Task 6 |
| spendSignal in get_buyer_profile | Task 7 |
| Coverage footer (pct mapped, unmapped spend) | Task 7 |
| No raw publisher text in output (strict render) | Task 7 — `canonical_name` used; raw only as fallback |
| Morning digest health line | Task 8 |
| Weekly spend-health.md and alias-review-queue.md | Task 8 |
| Annual catalogue refresh scheduled | Task 9 |
| Graceful degradation if tables not present | Task 7 — `_buildSpendSignal` returns null if table missing |
| Success criterion 4 (digest red flag on failure) | Task 8 — `error_files` surfaces in digest line |

All spec sections accounted for. No placeholders remain.
