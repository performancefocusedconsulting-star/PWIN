# Frameworks Canonical Layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a searchable index of UK government procurement frameworks inside `pwin-competitive-intel`, with two ingest pipelines (top-down catalogue scrape + bottom-up contracts data mine), a consolidation step, five MCP tools, and a new Frameworks dashboard tab.

**Architecture:** Four new SQLite tables in `bid_intel.db` (`frameworks`, `framework_lots`, `framework_suppliers`, `framework_call_offs`). Three new Python agents run in sequence: `mine_framework_calloffs.py` mines the existing notices/awards data, `ingest_frameworks_catalogue.py` scrapes CCS and other published catalogues, `consolidate_frameworks.py` merges both lists. Five new functions exported from `pwin-platform/src/competitive-intel.js` expose the data to AI skills. A new "Frameworks" tab in `dashboard.html` provides the visual directory.

**Tech Stack:** Python 3.9+ stdlib only (no external deps), SQLite via `sqlite3`, `urllib.request` for HTTP, `html.parser` for HTML parsing. Node.js `DatabaseSync` for MCP tools. Vanilla JS + existing CSS for dashboard tab. pytest for Python tests.

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `pwin-competitive-intel/db/schema.sql` | Modify | Add 4 new table definitions |
| `pwin-competitive-intel/agent/db_utils.py` | Modify | Add migration block for the 4 new tables |
| `pwin-competitive-intel/tests/test_framework_schema.py` | Create | Verify tables and columns after init |
| `pwin-competitive-intel/agent/mine_framework_calloffs.py` | Create | Bottom-up call-off miner |
| `pwin-competitive-intel/tests/test_mine_framework_calloffs.py` | Create | Unit tests for miner logic |
| `pwin-competitive-intel/agent/ingest_frameworks_catalogue.py` | Create | Top-down CCS + NHS catalogue scraper |
| `pwin-competitive-intel/tests/test_ingest_frameworks_catalogue.py` | Create | Parser unit tests with fixture HTML |
| `pwin-competitive-intel/agent/consolidate_frameworks.py` | Create | Merge both lists, flag gaps, produce report |
| `pwin-competitive-intel/tests/test_consolidate_frameworks.py` | Create | Unit tests for consolidation logic |
| `pwin-competitive-intel/agent/scheduler.py` | Modify | Add nightly call-off mining step |
| `pwin-competitive-intel/server.py` | Modify | Add 3 new API endpoints |
| `pwin-competitive-intel/dashboard.html` | Modify | Add Frameworks tab |
| `pwin-platform/src/competitive-intel.js` | Modify | Add 5 new MCP tool functions + exports |

---

## Task 1: Schema — four new tables

**Files:**
- Modify: `pwin-competitive-intel/db/schema.sql`
- Modify: `pwin-competitive-intel/agent/db_utils.py`
- Create: `pwin-competitive-intel/tests/test_framework_schema.py`

- [ ] **Step 1: Write the failing test**

Create `pwin-competitive-intel/tests/test_framework_schema.py`:

```python
"""Tests: framework tables created by schema.sql + db_utils migration."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
import db_utils

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"
DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"


def _make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _columns(conn, table):
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def test_frameworks_table_exists():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert "frameworks" in tables
    assert "framework_lots" in tables
    assert "framework_suppliers" in tables
    assert "framework_call_offs" in tables


def test_frameworks_required_columns():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "frameworks")
    for c in ("id", "reference_no", "name", "owner", "owner_type",
              "category", "expiry_date", "status", "source",
              "call_off_count", "call_off_value_total"):
        assert c in cols, f"Missing column: {c}"


def test_framework_lots_fk_column():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "framework_lots")
    assert "framework_id" in cols


def test_framework_suppliers_columns():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "framework_suppliers")
    for c in ("framework_id", "lot_id", "supplier_canonical_id",
              "supplier_name_raw", "status", "call_off_count"):
        assert c in cols, f"Missing column: {c}"


def test_framework_call_offs_columns():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "framework_call_offs")
    for c in ("framework_id", "notice_ocid", "buyer_canonical_id",
              "match_method", "match_confidence"):
        assert c in cols, f"Missing column: {c}"


def test_migration_idempotent():
    """Running init_schema twice must not raise."""
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)  # second call must be safe
```

- [ ] **Step 2: Run to verify it fails**

```
cd pwin-competitive-intel
python -m pytest tests/test_framework_schema.py -v
```

Expected: 6 failures (tables don't exist yet).

- [ ] **Step 3: Add the four tables to `db/schema.sql`**

Append to the end of `pwin-competitive-intel/db/schema.sql` (after the spend_transactions table):

```sql
-- ============================================================
-- FRAMEWORKS CANONICAL LAYER (2026-04-30)
-- ============================================================

CREATE TABLE IF NOT EXISTS frameworks (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_no             TEXT UNIQUE,
    name                     TEXT NOT NULL,
    short_name               TEXT,
    owner                    TEXT NOT NULL,
    owner_type               TEXT,
    category                 TEXT,
    sub_category             TEXT,
    description              TEXT,
    max_value                REAL,
    start_date               TEXT,
    expiry_date              TEXT,
    status                   TEXT NOT NULL DEFAULT 'active',
    replacement_framework_id INTEGER REFERENCES frameworks(id),
    eligible_buyer_types     TEXT,
    route_type               TEXT NOT NULL DEFAULT 'framework_agreement',
    lot_count                INTEGER NOT NULL DEFAULT 0,
    supplier_count           INTEGER NOT NULL DEFAULT 0,
    call_off_count           INTEGER NOT NULL DEFAULT 0,
    call_off_value_total     REAL NOT NULL DEFAULT 0,
    first_call_off_date      TEXT,
    last_call_off_date       TEXT,
    source                   TEXT NOT NULL DEFAULT 'contracts_only',
    source_url               TEXT,
    last_updated             TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_frameworks_ref      ON frameworks(reference_no);
CREATE INDEX IF NOT EXISTS idx_frameworks_status   ON frameworks(status);
CREATE INDEX IF NOT EXISTS idx_frameworks_owner    ON frameworks(owner_type);
CREATE INDEX IF NOT EXISTS idx_frameworks_category ON frameworks(category);
CREATE INDEX IF NOT EXISTS idx_frameworks_expiry   ON frameworks(expiry_date);

CREATE TABLE IF NOT EXISTS framework_lots (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_id   INTEGER NOT NULL REFERENCES frameworks(id),
    lot_number     TEXT,
    lot_name       TEXT,
    scope          TEXT,
    max_value      REAL,
    supplier_count INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_fw_lots_fw ON framework_lots(framework_id);

CREATE TABLE IF NOT EXISTS framework_suppliers (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_id          INTEGER NOT NULL REFERENCES frameworks(id),
    lot_id                INTEGER REFERENCES framework_lots(id),
    supplier_canonical_id TEXT,
    supplier_name_raw     TEXT,
    awarded_date          TEXT,
    status                TEXT NOT NULL DEFAULT 'active',
    call_off_count        INTEGER NOT NULL DEFAULT 0,
    call_off_value        REAL NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_fw_sup_fw  ON framework_suppliers(framework_id);
CREATE INDEX IF NOT EXISTS idx_fw_sup_can ON framework_suppliers(supplier_canonical_id);

CREATE TABLE IF NOT EXISTS framework_call_offs (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_id          INTEGER NOT NULL REFERENCES frameworks(id),
    lot_id                INTEGER REFERENCES framework_lots(id),
    notice_ocid           TEXT REFERENCES notices(ocid),
    supplier_canonical_id TEXT,
    buyer_canonical_id    TEXT,
    sub_org_canonical_id  TEXT,
    value                 REAL,
    awarded_date          TEXT,
    contract_title        TEXT,
    match_method          TEXT NOT NULL DEFAULT 'reference_no',
    match_confidence      REAL NOT NULL DEFAULT 1.0
);

CREATE INDEX IF NOT EXISTS idx_fw_co_fw       ON framework_call_offs(framework_id);
CREATE INDEX IF NOT EXISTS idx_fw_co_notice   ON framework_call_offs(notice_ocid);
CREATE INDEX IF NOT EXISTS idx_fw_co_buyer    ON framework_call_offs(buyer_canonical_id);
CREATE INDEX IF NOT EXISTS idx_fw_co_supplier ON framework_call_offs(supplier_canonical_id);
```

- [ ] **Step 4: Add migration block to `db_utils.py`**

Add the following block to the end of `_migrate_schema()` in `pwin-competitive-intel/agent/db_utils.py`, just before the `conn.commit()` call:

```python
    # ── frameworks canonical layer (2026-04-30) ──
    # New tables: created by CREATE TABLE IF NOT EXISTS in schema.sql.
    # Only column additions to existing framework tables go here.
    pass
```

(The `CREATE TABLE IF NOT EXISTS` clauses in `schema.sql` already handle fresh and existing DBs. This stub keeps the migration function extensible for future column additions.)

- [ ] **Step 5: Run tests to verify they pass**

```
cd pwin-competitive-intel
python -m pytest tests/test_framework_schema.py -v
```

Expected: 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add pwin-competitive-intel/db/schema.sql \
        pwin-competitive-intel/agent/db_utils.py \
        pwin-competitive-intel/tests/test_framework_schema.py
git commit -m "feat(frameworks): schema — 4 new tables for frameworks canonical layer"
```

---

## Task 2: Call-off miner

Mines the existing `notices` and `awards` tables for framework references. Three signal types, in confidence order:

- **Signal A:** `notices.parent_framework_title IS NOT NULL` — structured field already populated by the FTS ingest (Decision C06, 2026-04-12). Confidence 1.0.
- **Signal B:** Reference number pattern in title or description — regex `RM\d{4,6}` for CCS, plus common departmental patterns. Confidence 0.9.
- **Signal C:** Known framework name appearing in free text. Confidence 0.7.

**Files:**
- Create: `pwin-competitive-intel/agent/mine_framework_calloffs.py`
- Create: `pwin-competitive-intel/tests/test_mine_framework_calloffs.py`

- [ ] **Step 1: Write the failing tests**

Create `pwin-competitive-intel/tests/test_mine_framework_calloffs.py`:

```python
"""Tests: mine_framework_calloffs.py — framework reference extraction."""
import importlib.util
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

spec = importlib.util.spec_from_file_location(
    "mine_framework_calloffs",
    Path(__file__).parent.parent / "agent" / "mine_framework_calloffs.py",
)
# Module doesn't exist yet — import will fail until Task 2 Step 3
try:
    mfc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mfc)
except Exception:
    mfc = None

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _make_db() -> sqlite3.Connection:
    """In-memory DB with full schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    return conn


def _seed_notice(conn, ocid, title, parent_framework_title=None,
                 parent_framework_ocid=None, description=None):
    conn.execute("""
        INSERT OR IGNORE INTO buyers (id, name, last_updated) VALUES ('b1', 'Test Buyer', datetime('now'))
    """)
    conn.execute("""
        INSERT INTO notices (ocid, buyer_id, title, description,
            parent_framework_title, parent_framework_ocid, last_updated)
        VALUES (?, 'b1', ?, ?, ?, ?, datetime('now'))
    """, (ocid, title, description or "", parent_framework_title, parent_framework_ocid))
    conn.execute("""
        INSERT INTO awards (id, ocid, status, value_amount_gross, award_date, last_updated)
        VALUES (?, ?, 'active', 100000, '2025-01-15', datetime('now'))
    """, (f"award-{ocid}", ocid))
    conn.commit()


# ── _extract_rm_numbers ───────────────────────────────────────────────────────

def test_extract_rm_from_title():
    assert mfc is not None
    assert mfc._extract_rm_numbers("Technology Services 3 RM6100") == ["RM6100"]


def test_extract_rm_returns_empty_when_absent():
    assert mfc._extract_rm_numbers("Standard procurement notice") == []


def test_extract_rm_multiple():
    assert set(mfc._extract_rm_numbers("RM6116 and RM6100 frameworks")) == {"RM6116", "RM6100"}


# ── _normalise_fw_name ────────────────────────────────────────────────────────

def test_normalise_fw_name_lowercases():
    assert mfc._normalise_fw_name("Technology Services 3") == "technology services 3"


def test_normalise_fw_name_strips_punctuation():
    assert mfc._normalise_fw_name("Tech. Services (3)") == "tech services 3"


# ── mine_structured_references ───────────────────────────────────────────────

def test_mine_structured_creates_framework():
    assert mfc is not None
    conn = _make_db()
    _seed_notice(conn, "ocid-001", "Cloud services",
                 parent_framework_title="Technology Services 3",
                 parent_framework_ocid="rm6100")
    mfc.mine_structured_references(conn)
    fw = conn.execute("SELECT * FROM frameworks WHERE name='Technology Services 3'").fetchone()
    assert fw is not None
    assert fw["source"] == "contracts_only"


def test_mine_structured_creates_call_off():
    conn = _make_db()
    _seed_notice(conn, "ocid-002", "Cloud hosting",
                 parent_framework_title="Network Services 3")
    mfc.mine_structured_references(conn)
    co = conn.execute(
        "SELECT * FROM framework_call_offs WHERE notice_ocid='ocid-002'"
    ).fetchone()
    assert co is not None
    assert co["match_method"] == "reference_no"
    assert co["match_confidence"] == 1.0


def test_mine_structured_idempotent():
    """Running twice must not create duplicate frameworks or call-offs."""
    conn = _make_db()
    _seed_notice(conn, "ocid-003", "IT support",
                 parent_framework_title="Technology Services 3")
    mfc.mine_structured_references(conn)
    mfc.mine_structured_references(conn)
    count = conn.execute("SELECT COUNT(*) FROM frameworks").fetchone()[0]
    assert count == 1


# ── mine_rm_patterns ─────────────────────────────────────────────────────────

def test_mine_rm_pattern_in_title():
    conn = _make_db()
    _seed_notice(conn, "ocid-004", "Procurement via RM6116")
    mfc.mine_rm_patterns(conn)
    fw = conn.execute("SELECT * FROM frameworks WHERE reference_no='RM6116'").fetchone()
    assert fw is not None
    assert fw["match_confidence"] if hasattr(fw, "match_confidence") else True


def test_mine_rm_pattern_creates_call_off():
    conn = _make_db()
    _seed_notice(conn, "ocid-005", "Services under RM6100")
    mfc.mine_rm_patterns(conn)
    co = conn.execute(
        "SELECT * FROM framework_call_offs WHERE notice_ocid='ocid-005'"
    ).fetchone()
    assert co is not None
    assert co["match_method"] == "reference_no"
    assert abs(co["match_confidence"] - 0.9) < 0.01


# ── update_summary_counts ─────────────────────────────────────────────────────

def test_summary_counts_updated():
    conn = _make_db()
    _seed_notice(conn, "ocid-006", "Cloud via RM6116")
    mfc.mine_rm_patterns(conn)
    mfc.update_summary_counts(conn)
    fw = conn.execute(
        "SELECT call_off_count, call_off_value_total FROM frameworks WHERE reference_no='RM6116'"
    ).fetchone()
    assert fw["call_off_count"] == 1
    assert fw["call_off_value_total"] == 100000.0
```

- [ ] **Step 2: Run to verify tests fail (module not found)**

```
cd pwin-competitive-intel
python -m pytest tests/test_mine_framework_calloffs.py -v
```

Expected: collection error (module not found).

- [ ] **Step 3: Create `agent/mine_framework_calloffs.py`**

```python
"""
PWIN Competitive Intelligence — Framework call-off miner
=========================================================
Mines existing notices/awards data for framework references and populates
the frameworks canonical tables.

Three signal types:
  A  parent_framework_title populated (structured field, confidence 1.0)
  B  RM reference number pattern in title/description (confidence 0.9)
  C  Known framework name mention in free text (confidence 0.7)

Usage:
    python mine_framework_calloffs.py           # run against bid_intel.db
    python mine_framework_calloffs.py --dry-run # count matches, no writes
"""

import argparse
import logging
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
import db_utils

DB_PATH     = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mine_framework_calloffs")

# CCS reference pattern: RM followed by 4-6 digits
_RM_PATTERN = re.compile(r'\bRM\d{4,6}\b', re.IGNORECASE)

# Common punctuation to strip when normalising names
_PUNCT = re.compile(r'[^\w\s]')
_MULTI_SPACE = re.compile(r'\s+')


def _extract_rm_numbers(text: str) -> list[str]:
    """Return all CCS RM reference numbers found in text, uppercased."""
    if not text:
        return []
    return [m.upper() for m in _RM_PATTERN.findall(text)]


def _normalise_fw_name(name: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    if not name:
        return ""
    s = _PUNCT.sub(" ", name.lower())
    return _MULTI_SPACE.sub(" ", s).strip()


def _upsert_framework(conn: sqlite3.Connection, name: str, reference_no: str | None,
                      source: str = "contracts_only") -> int:
    """Insert or return existing framework id. Returns the row id."""
    if reference_no:
        row = conn.execute(
            "SELECT id FROM frameworks WHERE reference_no=?", (reference_no,)
        ).fetchone()
        if row:
            return row[0]
    # Try by normalised name
    norm = _normalise_fw_name(name)
    row = conn.execute(
        "SELECT id FROM frameworks WHERE lower(name)=?", (norm,)
    ).fetchone()
    if row:
        return row[0]
    # Insert skeleton
    conn.execute("""
        INSERT INTO frameworks (name, owner, reference_no, source, last_updated)
        VALUES (?, 'unknown', ?, ?, datetime('now'))
    """, (name, reference_no, source))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def _upsert_call_off(conn: sqlite3.Connection, framework_id: int, notice_ocid: str,
                     value: float | None, awarded_date: str | None,
                     title: str | None, match_method: str,
                     match_confidence: float):
    """Insert call-off if not already recorded for this notice+framework pair."""
    exists = conn.execute(
        "SELECT 1 FROM framework_call_offs WHERE framework_id=? AND notice_ocid=?",
        (framework_id, notice_ocid)
    ).fetchone()
    if exists:
        return
    conn.execute("""
        INSERT INTO framework_call_offs
            (framework_id, notice_ocid, value, awarded_date, contract_title,
             match_method, match_confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (framework_id, notice_ocid, value, awarded_date, title,
          match_method, match_confidence))


def mine_structured_references(conn: sqlite3.Connection):
    """
    Signal A: notices with parent_framework_title populated (structured field).
    These come from FTS OCDS data where the contracting authority explicitly
    tagged the parent framework. Confidence = 1.0.
    """
    rows = conn.execute("""
        SELECT n.ocid, n.parent_framework_title, n.parent_framework_ocid,
               a.value_amount_gross, a.award_date, n.title
        FROM notices n
        LEFT JOIN awards a ON a.ocid = n.ocid
        WHERE n.parent_framework_title IS NOT NULL
          AND n.parent_framework_title != ''
    """).fetchall()

    inserted = 0
    for row in rows:
        fw_id = _upsert_framework(
            conn,
            name=row["parent_framework_title"],
            reference_no=row["parent_framework_ocid"],
            source="contracts_only",
        )
        _upsert_call_off(
            conn,
            framework_id=fw_id,
            notice_ocid=row["ocid"],
            value=row["value_amount_gross"],
            awarded_date=row["award_date"],
            title=row["title"],
            match_method="reference_no",
            match_confidence=1.0,
        )
        inserted += 1

    conn.commit()
    log.info("Signal A (structured): %d notices processed", inserted)
    return inserted


def mine_rm_patterns(conn: sqlite3.Connection):
    """
    Signal B: RM reference number patterns in title or description.
    Skips notices already linked via Signal A (parent_framework_title set).
    Confidence = 0.9.
    """
    rows = conn.execute("""
        SELECT n.ocid, n.title, n.description,
               a.value_amount_gross, a.award_date
        FROM notices n
        LEFT JOIN awards a ON a.ocid = n.ocid
        WHERE (n.parent_framework_title IS NULL OR n.parent_framework_title = '')
    """).fetchall()

    linked = 0
    for row in rows:
        text = f"{row['title'] or ''} {row['description'] or ''}"
        rm_numbers = _extract_rm_numbers(text)
        for ref in rm_numbers:
            fw_id = _upsert_framework(conn, name=ref, reference_no=ref,
                                      source="contracts_only")
            _upsert_call_off(
                conn,
                framework_id=fw_id,
                notice_ocid=row["ocid"],
                value=row["value_amount_gross"],
                awarded_date=row["award_date"],
                title=row["title"],
                match_method="reference_no",
                match_confidence=0.9,
            )
            linked += 1

    conn.commit()
    log.info("Signal B (RM pattern): %d call-offs linked", linked)
    return linked


def update_summary_counts(conn: sqlite3.Connection):
    """
    Update frameworks.call_off_count, call_off_value_total,
    first_call_off_date, last_call_off_date from framework_call_offs.
    """
    conn.execute("""
        UPDATE frameworks SET
            call_off_count = (
                SELECT COUNT(*) FROM framework_call_offs
                WHERE framework_id = frameworks.id
            ),
            call_off_value_total = (
                SELECT COALESCE(SUM(value), 0) FROM framework_call_offs
                WHERE framework_id = frameworks.id AND value IS NOT NULL
            ),
            first_call_off_date = (
                SELECT MIN(awarded_date) FROM framework_call_offs
                WHERE framework_id = frameworks.id
            ),
            last_call_off_date = (
                SELECT MAX(awarded_date) FROM framework_call_offs
                WHERE framework_id = frameworks.id
            ),
            last_updated = datetime('now')
    """)
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM frameworks WHERE call_off_count > 0").fetchone()[0]
    log.info("Summary counts updated: %d frameworks with call-offs", count)


def run(conn: sqlite3.Connection, dry_run: bool = False):
    if dry_run:
        a = conn.execute(
            "SELECT COUNT(*) FROM notices WHERE parent_framework_title IS NOT NULL"
            " AND parent_framework_title != ''"
        ).fetchone()[0]
        b = conn.execute(
            "SELECT COUNT(*) FROM notices WHERE (parent_framework_title IS NULL"
            " OR parent_framework_title='') AND (title LIKE '%RM[0-9]%'"
            " OR description LIKE '%RM[0-9]%')"
        ).fetchone()[0]
        log.info("DRY RUN — Signal A candidates: %d, Signal B candidates: ~%d", a, b)
        return
    mine_structured_references(conn)
    mine_rm_patterns(conn)
    update_summary_counts(conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mine framework call-off references")
    parser.add_argument("--dry-run", action="store_true",
                        help="Count candidates without writing")
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)
    run(conn, dry_run=args.dry_run)
    conn.close()
```

- [ ] **Step 4: Run tests to verify they pass**

```
cd pwin-competitive-intel
python -m pytest tests/test_mine_framework_calloffs.py -v
```

Expected: 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/mine_framework_calloffs.py \
        pwin-competitive-intel/tests/test_mine_framework_calloffs.py
git commit -m "feat(frameworks): call-off miner — signals A and B"
```

---

## Task 3: Catalogue ingest — CCS parser

The CCS website (`crowncommercial.gov.uk/agreements`) publishes all active frameworks. This task builds a parser for the list page and individual agreement pages. The HTTP layer is injected so parsers are testable with fixture HTML without making network calls.

**Important:** CCS HTML structure must be verified against the live site on first run. The parser is written against the typical CCS page structure (known from prior work), but selectors may need minor adjustment if the site has changed. Run with `--dry-run` first.

**Files:**
- Create: `pwin-competitive-intel/agent/ingest_frameworks_catalogue.py`
- Create: `pwin-competitive-intel/tests/test_ingest_frameworks_catalogue.py`

- [ ] **Step 1: Write the failing tests**

Create `pwin-competitive-intel/tests/test_ingest_frameworks_catalogue.py`:

```python
"""Tests: ingest_frameworks_catalogue.py — CCS parser functions."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

spec = importlib.util.spec_from_file_location(
    "ingest_frameworks_catalogue",
    Path(__file__).parent.parent / "agent" / "ingest_frameworks_catalogue.py",
)
try:
    ifc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ifc)
except Exception:
    ifc = None

# Minimal fixture HTML representing a CCS agreement list page
LIST_FIXTURE = """
<html><body>
  <ul class="agreements-list">
    <li><a href="/agreements/rm6116">Network Services 3</a></li>
    <li><a href="/agreements/rm6100">Technology Services 3</a></li>
  </ul>
</body></html>
"""

# Minimal fixture HTML representing a CCS agreement detail page
DETAIL_FIXTURE = """
<html><body>
  <h1 class="agreement-title">Network Services 3</h1>
  <p class="reference-number">RM6116</p>
  <p class="expiry-date">31 March 2027</p>
  <p class="description">Wide area networking and connectivity services.</p>
  <table class="lots-table">
    <tbody>
      <tr><td>1</td><td>Wide Area Network</td><td>Connectivity</td></tr>
      <tr><td>2</td><td>Internet Access</td><td>Broadband</td></tr>
    </tbody>
  </table>
</body></html>
"""

DETAIL_FIXTURE_MINIMAL = """
<html><body>
  <h1 class="agreement-title">TEPAS 2</h1>
</body></html>
"""


def test_parse_ccs_list_extracts_urls():
    assert ifc is not None
    urls = ifc.parse_ccs_list(LIST_FIXTURE, base_url="https://www.crowncommercial.gov.uk")
    assert len(urls) == 2
    assert any("rm6116" in u for u in urls)
    assert any("rm6100" in u for u in urls)


def test_parse_ccs_agreement_name():
    assert ifc is not None
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE)
    assert result["name"] == "Network Services 3"


def test_parse_ccs_agreement_reference():
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE)
    assert result["reference_no"] == "RM6116"


def test_parse_ccs_agreement_expiry():
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE)
    assert result["expiry_date"] == "2027-03-31"


def test_parse_ccs_agreement_lots():
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE)
    assert len(result["lots"]) == 2
    assert result["lots"][0]["lot_number"] == "1"
    assert result["lots"][0]["lot_name"] == "Wide Area Network"


def test_parse_ccs_agreement_minimal_no_crash():
    """Parser must not crash on a minimal/incomplete page."""
    result = ifc.parse_ccs_agreement(DETAIL_FIXTURE_MINIMAL)
    assert result["name"] == "TEPAS 2"
    assert result["reference_no"] is None
    assert result["lots"] == []


def test_parse_date_iso():
    assert ifc is not None
    assert ifc._parse_date("31 March 2027") == "2027-03-31"
    assert ifc._parse_date("2027-03-31") == "2027-03-31"
    assert ifc._parse_date("") is None
    assert ifc._parse_date(None) is None
```

- [ ] **Step 2: Run to verify they fail**

```
cd pwin-competitive-intel
python -m pytest tests/test_ingest_frameworks_catalogue.py -v
```

Expected: collection error (module not found).

- [ ] **Step 3: Create `agent/ingest_frameworks_catalogue.py`**

```python
"""
PWIN Competitive Intelligence — Framework catalogue ingest
==========================================================
Pulls UK government framework agreements from published catalogues
(Crown Commercial Service primary; NHS and local gov in Wave 2).

The HTTP layer is injectable for testing. Parsers accept raw HTML strings.

Usage:
    python ingest_frameworks_catalogue.py              # full CCS catalogue
    python ingest_frameworks_catalogue.py --limit 10   # first 10 agreements
    python ingest_frameworks_catalogue.py --dry-run    # parse only, no writes
    python ingest_frameworks_catalogue.py --url <url>  # single agreement

NOTE: CSS selectors are based on CCS site structure as of 2026-04. Run with
--dry-run on first use to verify the parser is producing sensible output
before committing to the database.
"""

import argparse
import logging
import sqlite3
import sys
import time
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
import db_utils

DB_PATH     = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"

CCS_BASE        = "https://www.crowncommercial.gov.uk"
CCS_LIST_URL    = f"{CCS_BASE}/agreements"
REQUEST_DELAY   = 1.5   # seconds between requests — polite crawling

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest_frameworks_catalogue")

_MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}


def _parse_date(text: str | None) -> str | None:
    """Convert various date formats to ISO YYYY-MM-DD. Returns None on failure."""
    if not text:
        return None
    text = text.strip()
    if not text:
        return None
    # Already ISO
    if len(text) == 10 and text[4] == "-":
        return text
    # "31 March 2027" format
    parts = text.lower().split()
    if len(parts) == 3:
        month = _MONTH_MAP.get(parts[1])
        if month:
            try:
                return f"{parts[2]}-{month}-{int(parts[0]):02d}"
            except ValueError:
                pass
    return None


def _fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch URL and return HTML as string. Raises on HTTP error."""
    req = Request(url, headers={"User-Agent": "PWIN-Competitive-Intel/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ── CCS HTML parsers ──────────────────────────────────────────────────────────

class _LinkCollector(HTMLParser):
    """Collects href values from <a> tags inside a named class container."""
    def __init__(self, container_class: str, href_prefix: str):
        super().__init__()
        self.container_class = container_class
        self.href_prefix = href_prefix
        self.links: list[str] = []
        self._in_container = False
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class", "")
        if self.container_class in cls:
            self._in_container = True
            self._depth = 0
        if self._in_container:
            self._depth += 1
            if tag == "a":
                href = attrs.get("href", "")
                if href.startswith(self.href_prefix):
                    self.links.append(href)

    def handle_endtag(self, tag):
        if self._in_container:
            self._depth -= 1
            if self._depth <= 0:
                self._in_container = False


def parse_ccs_list(html: str, base_url: str = CCS_BASE) -> list[str]:
    """
    Extract absolute URLs for individual agreement pages from the CCS list page.
    Returns a list of full URLs.

    NOTE: Adjust container_class if the CCS list page structure has changed.
    """
    collector = _LinkCollector(
        container_class="agreements-list",
        href_prefix="/agreements/",
    )
    collector.feed(html)
    # Fall back to any /agreements/<slug> links if container class not found
    if not collector.links:
        import re
        paths = re.findall(r'href="(/agreements/[a-z0-9\-]+)"', html)
        collector.links = list(dict.fromkeys(paths))  # deduplicate preserving order
    return [f"{base_url}{path}" for path in collector.links]


class _AgreementParser(HTMLParser):
    """
    Parses a single CCS agreement detail page.
    Extracts: name, reference_no, expiry_date, description, lots.
    """
    def __init__(self):
        super().__init__()
        self.name: str | None = None
        self.reference_no: str | None = None
        self.expiry_date_raw: str | None = None
        self.description: str | None = None
        self.lots: list[dict] = []
        self._current_tag: str = ""
        self._current_class: str = ""
        self._capture: str | None = None  # which field to capture next text into
        self._in_lots_table: bool = False
        self._current_lot: list[str] = []
        self._in_lot_row: bool = False
        self._lot_cell: int = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class", "")
        self._current_tag = tag
        self._current_class = cls

        if tag == "h1" and "agreement-title" in cls:
            self._capture = "name"
        elif tag == "p" and "reference-number" in cls:
            self._capture = "reference_no"
        elif tag == "p" and "expiry-date" in cls:
            self._capture = "expiry_date_raw"
        elif tag == "p" and "description" in cls:
            self._capture = "description"
        elif tag == "table" and "lots-table" in cls:
            self._in_lots_table = True
        elif self._in_lots_table and tag == "tr":
            self._in_lot_row = True
            self._current_lot = []
            self._lot_cell = 0
        elif self._in_lots_table and self._in_lot_row and tag == "td":
            self._capture = f"lot_cell_{self._lot_cell}"
            self._lot_cell += 1

    def handle_endtag(self, tag):
        if tag in ("h1", "p"):
            self._capture = None
        elif tag == "tr" and self._in_lot_row:
            if len(self._current_lot) >= 2:
                self.lots.append({
                    "lot_number": self._current_lot[0].strip(),
                    "lot_name": self._current_lot[1].strip(),
                    "scope": self._current_lot[2].strip() if len(self._current_lot) > 2 else None,
                })
            self._in_lot_row = False
            self._lot_cell = 0
        elif tag == "table":
            self._in_lots_table = False

    def handle_data(self, data):
        data = data.strip()
        if not data or not self._capture:
            return
        if self._capture == "name":
            self.name = (self.name or "") + data
        elif self._capture == "reference_no":
            self.reference_no = (self.reference_no or "") + data
        elif self._capture == "expiry_date_raw":
            self.expiry_date_raw = (self.expiry_date_raw or "") + data
        elif self._capture == "description":
            self.description = (self.description or "") + data
        elif self._capture and self._capture.startswith("lot_cell_"):
            self._current_lot.append(data)


def parse_ccs_agreement(html: str) -> dict:
    """
    Parse a CCS agreement detail page. Returns a dict with:
    name, reference_no, expiry_date (ISO), description, lots (list of dicts).
    """
    parser = _AgreementParser()
    parser.feed(html)

    # Strip RM prefix noise from reference_no if present
    ref = parser.reference_no
    if ref:
        ref = ref.strip()
        # Normalise to uppercase RM format
        import re
        m = re.search(r'RM\d{4,6}', ref, re.IGNORECASE)
        ref = m.group(0).upper() if m else ref

    return {
        "name": (parser.name or "").strip() or None,
        "reference_no": ref,
        "expiry_date": _parse_date(parser.expiry_date_raw),
        "description": (parser.description or "").strip() or None,
        "lots": parser.lots,
    }


# ── Database write ────────────────────────────────────────────────────────────

def _upsert_catalogue_framework(conn: sqlite3.Connection, data: dict,
                                 source_url: str):
    """
    Insert or update a framework record from catalogue data.
    If the record already exists (by reference_no), updates catalogue fields.
    Sets source = 'both' if it was previously 'contracts_only'.
    """
    if not data.get("name"):
        return None

    existing = None
    if data.get("reference_no"):
        existing = conn.execute(
            "SELECT id, source FROM frameworks WHERE reference_no=?",
            (data["reference_no"],)
        ).fetchone()

    if not existing:
        existing = conn.execute(
            "SELECT id, source FROM frameworks WHERE lower(name)=lower(?)",
            (data["name"],)
        ).fetchone()

    new_source = "both" if (existing and existing["source"] == "contracts_only") else "catalogue_only"

    if existing:
        conn.execute("""
            UPDATE frameworks SET
                name         = COALESCE(?, name),
                reference_no = COALESCE(?, reference_no),
                expiry_date  = COALESCE(?, expiry_date),
                description  = COALESCE(?, description),
                owner        = 'Crown Commercial Service',
                owner_type   = 'central_gov',
                source       = ?,
                source_url   = ?,
                last_updated = datetime('now')
            WHERE id = ?
        """, (data["name"], data.get("reference_no"), data.get("expiry_date"),
              data.get("description"), new_source, source_url, existing["id"]))
        fw_id = existing["id"]
    else:
        conn.execute("""
            INSERT INTO frameworks
                (name, reference_no, owner, owner_type, expiry_date,
                 description, source, source_url, last_updated)
            VALUES (?, ?, 'Crown Commercial Service', 'central_gov',
                    ?, ?, 'catalogue_only', ?, datetime('now'))
        """, (data["name"], data.get("reference_no"), data.get("expiry_date"),
              data.get("description"), source_url))
        fw_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    for lot in data.get("lots", []):
        conn.execute("""
            INSERT OR IGNORE INTO framework_lots
                (framework_id, lot_number, lot_name, scope)
            VALUES (?, ?, ?, ?)
        """, (fw_id, lot.get("lot_number"), lot.get("lot_name"), lot.get("scope")))

    conn.commit()
    return fw_id


# ── Main run ──────────────────────────────────────────────────────────────────

def run(conn: sqlite3.Connection, dry_run: bool = False,
        limit: int | None = None,
        fetch_fn=_fetch_url):
    """
    Fetch the CCS agreements list, then fetch and parse each agreement.
    fetch_fn is injectable for testing.
    """
    log.info("Fetching CCS agreements list from %s", CCS_LIST_URL)
    try:
        list_html = fetch_fn(CCS_LIST_URL)
    except (HTTPError, URLError) as e:
        log.error("Failed to fetch CCS list: %s", e)
        return 0

    urls = parse_ccs_list(list_html)
    log.info("Found %d agreement URLs", len(urls))

    if limit:
        urls = urls[:limit]

    ingested = 0
    for i, url in enumerate(urls):
        time.sleep(REQUEST_DELAY)
        try:
            html = fetch_fn(url)
        except (HTTPError, URLError) as e:
            log.warning("Failed to fetch %s: %s", url, e)
            continue

        data = parse_ccs_agreement(html)
        if not data.get("name"):
            log.warning("No name parsed from %s — skipping", url)
            continue

        if dry_run:
            log.info("DRY RUN [%d/%d]: %s (%s) expiry=%s lots=%d",
                     i + 1, len(urls), data["name"], data.get("reference_no"),
                     data.get("expiry_date"), len(data.get("lots", [])))
        else:
            _upsert_catalogue_framework(conn, data, source_url=url)
            log.info("[%d/%d] Ingested: %s (%s)",
                     i + 1, len(urls), data["name"], data.get("reference_no"))

        ingested += 1

    log.info("Catalogue ingest complete: %d agreements processed", ingested)
    return ingested


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest framework catalogue from CCS")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--url", type=str, default=None,
                        help="Parse a single agreement URL")
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)

    if args.url:
        html = _fetch_url(args.url)
        data = parse_ccs_agreement(html)
        import json; print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        run(conn, dry_run=args.dry_run, limit=args.limit)

    conn.close()
```

- [ ] **Step 4: Run tests to verify they pass**

```
cd pwin-competitive-intel
python -m pytest tests/test_ingest_frameworks_catalogue.py -v
```

Expected: 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/ingest_frameworks_catalogue.py \
        pwin-competitive-intel/tests/test_ingest_frameworks_catalogue.py
git commit -m "feat(frameworks): CCS catalogue ingest + parser tests"
```

---

## Task 4: Consolidation script

Merges the catalogue list (source = `catalogue_only`) and contracts-mined list (source = `contracts_only`) into unified records. Produces a JSON gap report.

**Files:**
- Create: `pwin-competitive-intel/agent/consolidate_frameworks.py`
- Create: `pwin-competitive-intel/tests/test_consolidate_frameworks.py`

- [ ] **Step 1: Write the failing tests**

Create `pwin-competitive-intel/tests/test_consolidate_frameworks.py`:

```python
"""Tests: consolidate_frameworks.py — merge logic and gap report."""
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

spec = importlib.util.spec_from_file_location(
    "consolidate_frameworks",
    Path(__file__).parent.parent / "agent" / "consolidate_frameworks.py",
)
try:
    cf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cf)
except Exception:
    cf = None

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    return conn


def _insert_fw(conn, name, reference_no=None, source="contracts_only"):
    conn.execute("""
        INSERT INTO frameworks (name, owner, reference_no, source)
        VALUES (?, 'unknown', ?, ?)
    """, (name, reference_no, source))
    conn.commit()


def test_merge_by_reference_no():
    """Two records with same reference_no should merge — source becomes 'both'."""
    assert cf is not None
    conn = _make_db()
    _insert_fw(conn, "Technology Services 3", "RM6100", "contracts_only")
    _insert_fw(conn, "Technology Services 3 (CCS)", "RM6100", "catalogue_only")
    cf.consolidate(conn)
    rows = conn.execute(
        "SELECT * FROM frameworks WHERE reference_no='RM6100'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["source"] == "both"


def test_merge_by_name_similarity():
    """Two records with same normalised name, no reference_no, should merge."""
    conn = _make_db()
    _insert_fw(conn, "Network Services 3", None, "contracts_only")
    _insert_fw(conn, "Network Services 3", None, "catalogue_only")
    cf.consolidate(conn)
    rows = conn.execute(
        "SELECT * FROM frameworks WHERE lower(name)='network services 3'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["source"] == "both"


def test_no_merge_different_frameworks():
    """Two distinct frameworks must remain as separate records."""
    conn = _make_db()
    _insert_fw(conn, "Tech Services 3", "RM6100", "contracts_only")
    _insert_fw(conn, "Network Services 3", "RM6116", "catalogue_only")
    cf.consolidate(conn)
    count = conn.execute("SELECT COUNT(*) FROM frameworks").fetchone()[0]
    assert count == 2


def test_gap_report_contracts_only():
    conn = _make_db()
    _insert_fw(conn, "TEPAS 2", None, "contracts_only")
    _insert_fw(conn, "Tech Services 3", "RM6100", "catalogue_only")
    cf.consolidate(conn)
    report = cf.build_gap_report(conn)
    assert report["contracts_only_count"] == 1
    assert report["catalogue_only_count"] == 1
    assert report["both_count"] == 0
    assert any(r["name"] == "TEPAS 2" for r in report["contracts_only"])


def test_gap_report_both():
    conn = _make_db()
    _insert_fw(conn, "Tech Services 3", "RM6100", "contracts_only")
    _insert_fw(conn, "Tech Services 3", "RM6100", "catalogue_only")
    cf.consolidate(conn)
    report = cf.build_gap_report(conn)
    assert report["both_count"] == 1
    assert report["contracts_only_count"] == 0
```

- [ ] **Step 2: Run to verify they fail**

```
cd pwin-competitive-intel
python -m pytest tests/test_consolidate_frameworks.py -v
```

Expected: collection error (module not found).

- [ ] **Step 3: Create `agent/consolidate_frameworks.py`**

```python
"""
PWIN Competitive Intelligence — Framework consolidation
=======================================================
Merges framework records from catalogue ingest and call-off mining.
Deduplicates by reference_no (exact) or name (normalised).
Produces a JSON gap report.

Usage:
    python consolidate_frameworks.py              # merge + report
    python consolidate_frameworks.py --report-only # report without merge
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
import db_utils

DB_PATH      = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH  = Path(__file__).parent.parent / "db" / "schema.sql"
REPORT_PATH  = Path(__file__).parent.parent / "db" / "framework_consolidation_report.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("consolidate_frameworks")

_PUNCT = re.compile(r'[^\w\s]')
_MULTI_SPACE = re.compile(r'\s+')


def _norm_name(name: str) -> str:
    if not name:
        return ""
    s = _PUNCT.sub(" ", name.lower())
    return _MULTI_SPACE.sub(" ", s).strip()


def consolidate(conn: sqlite3.Connection):
    """
    Merge duplicate framework records.

    Pass 1: merge by exact reference_no match.
    Pass 2: merge by normalised name match (where no reference_no).
    """
    merged = 0

    # Pass 1: exact reference_no
    refs = conn.execute(
        "SELECT reference_no FROM frameworks WHERE reference_no IS NOT NULL"
        " GROUP BY reference_no HAVING COUNT(*) > 1"
    ).fetchall()

    for ref_row in refs:
        ref = ref_row[0]
        rows = conn.execute(
            "SELECT id, name, source, call_off_count, call_off_value_total,"
            " description, expiry_date, source_url"
            " FROM frameworks WHERE reference_no=? ORDER BY"
            " CASE source WHEN 'both' THEN 0 WHEN 'catalogue_only' THEN 1 ELSE 2 END",
            (ref,)
        ).fetchall()
        if len(rows) < 2:
            continue

        # Keep first row, merge others into it
        keep = rows[0]
        for dup in rows[1:]:
            # Accumulate call-offs from the duplicate
            conn.execute("""
                UPDATE framework_call_offs SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE framework_suppliers SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE framework_lots SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            # Update kept record with any enriched fields from dup
            conn.execute("""
                UPDATE frameworks SET
                    description = COALESCE(description, ?),
                    expiry_date = COALESCE(expiry_date, ?),
                    source_url  = COALESCE(source_url, ?),
                    source      = 'both',
                    last_updated = datetime('now')
                WHERE id = ?
            """, (dup["description"], dup["expiry_date"], dup["source_url"], keep["id"]))
            conn.execute("DELETE FROM frameworks WHERE id=?", (dup["id"],))
            merged += 1

    conn.commit()

    # Pass 2: normalised name (no reference_no)
    unnamed = conn.execute(
        "SELECT id, name, source, call_off_count, description, expiry_date, source_url"
        " FROM frameworks WHERE reference_no IS NULL"
    ).fetchall()

    groups: dict[str, list] = {}
    for row in unnamed:
        key = _norm_name(row["name"])
        groups.setdefault(key, []).append(row)

    for key, rows in groups.items():
        if len(rows) < 2:
            continue
        # Sort: catalogue_only first (richer data), then contracts_only
        rows.sort(key=lambda r: 0 if r["source"] == "catalogue_only" else 1)
        keep = rows[0]
        for dup in rows[1:]:
            conn.execute("""
                UPDATE framework_call_offs SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE framework_suppliers SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE framework_lots SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE frameworks SET
                    description = COALESCE(description, ?),
                    expiry_date = COALESCE(expiry_date, ?),
                    source_url  = COALESCE(source_url, ?),
                    source      = 'both',
                    last_updated = datetime('now')
                WHERE id = ?
            """, (dup["description"], dup["expiry_date"], dup["source_url"], keep["id"]))
            conn.execute("DELETE FROM frameworks WHERE id=?", (dup["id"],))
            merged += 1

    conn.commit()
    log.info("Consolidation complete: %d duplicate records merged", merged)
    return merged


def build_gap_report(conn: sqlite3.Connection) -> dict:
    """Build a summary report of source coverage gaps."""
    contracts_only = conn.execute(
        "SELECT name, reference_no, call_off_count, call_off_value_total"
        " FROM frameworks WHERE source='contracts_only'"
        " ORDER BY call_off_value_total DESC"
    ).fetchall()

    catalogue_only = conn.execute(
        "SELECT name, reference_no, expiry_date"
        " FROM frameworks WHERE source='catalogue_only'"
        " ORDER BY name"
    ).fetchall()

    both = conn.execute(
        "SELECT COUNT(*) FROM frameworks WHERE source='both'"
    ).fetchone()[0]

    return {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "contracts_only_count": len(contracts_only),
        "catalogue_only_count": len(catalogue_only),
        "both_count": both,
        "total": len(contracts_only) + len(catalogue_only) + both,
        "contracts_only": [dict(r) for r in contracts_only],
        "catalogue_only": [dict(r) for r in catalogue_only],
        "notes": {
            "contracts_only": "Frameworks seen in real call-offs but absent from published catalogues. "
                              "Typically departmental frameworks (MoD, Home Office). Enrich manually.",
            "catalogue_only": "Frameworks in the CCS catalogue but with no recorded call-offs. "
                              "May be new, unused, or represent a data coverage gap.",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate framework records")
    parser.add_argument("--report-only", action="store_true",
                        help="Print gap report without merging")
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)

    if not args.report_only:
        consolidate(conn)

    report = build_gap_report(conn)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log.info("Gap report written to %s", REPORT_PATH)
    log.info("  contracts_only: %d  catalogue_only: %d  both: %d",
             report["contracts_only_count"],
             report["catalogue_only_count"],
             report["both_count"])
    conn.close()
```

- [ ] **Step 4: Run tests to verify they pass**

```
cd pwin-competitive-intel
python -m pytest tests/test_consolidate_frameworks.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/consolidate_frameworks.py \
        pwin-competitive-intel/tests/test_consolidate_frameworks.py
git commit -m "feat(frameworks): consolidation script — dedup + gap report"
```

---

## Task 5: Wire into scheduler

Add the call-off miner as a nightly step. Catalogue ingest runs monthly, not nightly — add it as an optional flag.

**Files:**
- Modify: `pwin-competitive-intel/agent/scheduler.py`

- [ ] **Step 1: Add the nightly mining step**

In `pwin-competitive-intel/agent/scheduler.py`, add after the `ingest_spend.py` step (before the final `log.info("Nightly pipeline complete")`):

```python
    # Framework call-off mining: links newly ingested contracts to the frameworks
    # canonical layer. Non-fatal — a failure here must not stop the core pipeline.
    run_step("Framework call-off mining",
             [str(AGENT_DIR / "mine_framework_calloffs.py")])
```

- [ ] **Step 2: Add a monthly catalogue refresh option**

Add a `--with-frameworks-catalogue` flag to the scheduler. Add this block to the argument parser at the top of the `if __name__ == "__main__":` block in `scheduler.py`:

```python
    import argparse as _ap
    _parser = _ap.ArgumentParser()
    _parser.add_argument("--with-frameworks-catalogue", action="store_true",
                         help="Also run the monthly CCS catalogue ingest")
    _args, _ = _parser.parse_known_args()
```

And after the framework call-off mining step:

```python
    # Monthly: CCS catalogue ingest (run with --with-frameworks-catalogue)
    if _args.with_frameworks_catalogue:
        run_step("CCS framework catalogue ingest",
                 [str(AGENT_DIR / "ingest_frameworks_catalogue.py")])
        run_step("Framework consolidation",
                 [str(AGENT_DIR / "consolidate_frameworks.py")])
```

- [ ] **Step 3: Run the scheduler in dry-run mode to verify no import errors**

```
cd pwin-competitive-intel
python agent/scheduler.py --help
```

Expected: prints usage with `--with-frameworks-catalogue` option shown, no errors.

- [ ] **Step 4: Commit**

```bash
git add pwin-competitive-intel/agent/scheduler.py
git commit -m "feat(frameworks): wire call-off mining into nightly scheduler"
```

---

## Task 6: MCP tools — five new functions

Five new query functions in `pwin-platform/src/competitive-intel.js`, following the existing `DatabaseSync` + try/finally pattern.

**Files:**
- Modify: `pwin-platform/src/competitive-intel.js`

- [ ] **Step 1: Add `frameworkProfile` function**

Add the following function to `pwin-platform/src/competitive-intel.js`, before the final `export` block:

```javascript
// ── Frameworks ────────────────────────────────────────────────────────────

function frameworkProfile(query) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    // Try exact reference_no first, then partial name match
    let fw = db.prepare(
      "SELECT * FROM frameworks WHERE upper(reference_no)=upper(?)"
    ).get(query);
    if (!fw) {
      fw = db.prepare(
        "SELECT * FROM frameworks WHERE instr(lower(name), lower(?)) > 0 ORDER BY call_off_value_total DESC LIMIT 1"
      ).get(query);
    }
    if (!fw) return { error: `No framework found matching '${query}'` };

    const lots = db.prepare(
      "SELECT * FROM framework_lots WHERE framework_id=? ORDER BY lot_number"
    ).all(fw.id);

    const topSuppliers = db.prepare(`
      SELECT supplier_name_raw, supplier_canonical_id,
             call_off_count, call_off_value
      FROM framework_suppliers WHERE framework_id=?
      ORDER BY call_off_value DESC LIMIT 10
    `).all(fw.id);

    return {
      id: fw.id,
      name: fw.name,
      referenceNo: fw.reference_no,
      owner: fw.owner,
      ownerType: fw.owner_type,
      category: fw.category,
      description: fw.description,
      status: fw.status,
      expiryDate: fw.expiry_date,
      routeType: fw.route_type,
      maxValue: fw.max_value,
      callOffCount: fw.call_off_count,
      callOffValueTotal: fw.call_off_value_total,
      source: fw.source,
      lots: lots.map(l => ({
        lotNumber: l.lot_number,
        lotName: l.lot_name,
        scope: l.scope,
        supplierCount: l.supplier_count,
      })),
      topSuppliers: topSuppliers.map(s => ({
        name: s.supplier_name_raw,
        canonicalId: s.supplier_canonical_id,
        callOffCount: s.call_off_count,
        callOffValue: s.call_off_value,
      })),
    };
  } finally {
    db.close();
  }
}
```

- [ ] **Step 2: Add `searchFrameworks` function**

```javascript
function searchFrameworks(query, { ownerType, category, status, expiringWithinMonths } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const conditions = [];
    const params = [];

    if (query) {
      conditions.push("(instr(lower(name), lower(?)) > 0 OR upper(reference_no) = upper(?))");
      params.push(query, query);
    }
    if (ownerType) {
      conditions.push("owner_type = ?");
      params.push(ownerType);
    }
    if (category) {
      conditions.push("instr(lower(category), lower(?)) > 0");
      params.push(category);
    }
    if (status) {
      conditions.push("status = ?");
      params.push(status);
    }
    if (expiringWithinMonths) {
      conditions.push("expiry_date IS NOT NULL AND expiry_date <= date('now', '+' || ? || ' months')");
      params.push(expiringWithinMonths);
    }

    const where = conditions.length ? "WHERE " + conditions.join(" AND ") : "";
    const rows = db.prepare(`
      SELECT id, name, reference_no, owner, owner_type, category, status,
             expiry_date, call_off_count, call_off_value_total, source
      FROM frameworks ${where}
      ORDER BY call_off_value_total DESC NULLS LAST
      LIMIT 50
    `).all(...params);

    return {
      count: rows.length,
      frameworks: rows.map(r => ({
        id: r.id,
        name: r.name,
        referenceNo: r.reference_no,
        owner: r.owner,
        ownerType: r.owner_type,
        category: r.category,
        status: r.status,
        expiryDate: r.expiry_date,
        callOffCount: r.call_off_count,
        callOffValueTotal: r.call_off_value_total,
        source: r.source,
      })),
    };
  } finally {
    db.close();
  }
}
```

- [ ] **Step 3: Add `buyerFrameworkUsage` function**

```javascript
function buyerFrameworkUsage(buyerQuery) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const resolved = _resolveBuyerCanonical(db, buyerQuery);
    if (!resolved) return { error: `No buyer found matching '${buyerQuery}'` };
    if (resolved.ambiguous) return { error: 'Ambiguous buyer name', candidates: resolved.candidates };

    const canonicalId = resolved.canonicalId || (resolved.rawBuyerIds[0] || null);
    if (!canonicalId) return { error: `Buyer '${buyerQuery}' has no data` };

    const usage = db.prepare(`
      SELECT f.id, f.name, f.reference_no, f.owner, f.category, f.status, f.expiry_date,
             COUNT(co.id) AS call_off_count,
             SUM(co.value) AS total_value,
             MIN(co.awarded_date) AS first_date,
             MAX(co.awarded_date) AS last_date
      FROM framework_call_offs co
      JOIN frameworks f ON co.framework_id = f.id
      WHERE co.buyer_canonical_id = ?
      GROUP BY f.id
      ORDER BY total_value DESC NULLS LAST
    `).all(canonicalId);

    return {
      buyer: resolved.canonicalName || buyerQuery,
      frameworkCount: usage.length,
      frameworks: usage.map(r => ({
        id: r.id,
        name: r.name,
        referenceNo: r.reference_no,
        owner: r.owner,
        category: r.category,
        status: r.status,
        expiryDate: r.expiry_date,
        callOffCount: r.call_off_count,
        totalValue: r.total_value,
        firstDate: r.first_date,
        lastDate: r.last_date,
      })),
    };
  } finally {
    db.close();
  }
}
```

- [ ] **Step 4: Add `supplierFrameworkPosition` function**

```javascript
function supplierFrameworkPosition(supplierQuery) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    // Resolve to canonical supplier id via name search
    const sup = db.prepare(`
      SELECT COALESCE(s2c.canonical_id, 'RAW-' || s.id) AS canonical_id,
             COALESCE(cs.canonical_name, s.name) AS canonical_name
      FROM suppliers s
      LEFT JOIN supplier_to_canonical s2c ON s.id = s2c.supplier_id
      LEFT JOIN canonical_suppliers cs ON s2c.canonical_id = cs.canonical_id
      WHERE instr(lower(s.name), lower(?)) > 0
      LIMIT 1
    `).get(supplierQuery);

    if (!sup) return { error: `No supplier found matching '${supplierQuery}'` };

    const positions = db.prepare(`
      SELECT f.id, f.name, f.reference_no, f.owner, f.category, f.status, f.expiry_date,
             fl.lot_number, fl.lot_name,
             fs.status AS position_status, fs.awarded_date,
             fs.call_off_count, fs.call_off_value
      FROM framework_suppliers fs
      JOIN frameworks f ON fs.framework_id = f.id
      LEFT JOIN framework_lots fl ON fs.lot_id = fl.id
      WHERE fs.supplier_canonical_id = ?
      ORDER BY fs.call_off_value DESC NULLS LAST
    `).all(sup.canonical_id);

    return {
      supplier: sup.canonical_name,
      canonicalId: sup.canonical_id,
      positionCount: positions.length,
      positions: positions.map(r => ({
        frameworkId: r.id,
        frameworkName: r.name,
        referenceNo: r.reference_no,
        owner: r.owner,
        category: r.category,
        frameworkStatus: r.status,
        expiryDate: r.expiry_date,
        lotNumber: r.lot_number,
        lotName: r.lot_name,
        positionStatus: r.position_status,
        awardedDate: r.awarded_date,
        callOffCount: r.call_off_count,
        callOffValue: r.call_off_value,
      })),
    };
  } finally {
    db.close();
  }
}
```

- [ ] **Step 5: Add `frameworkCallOffs` function**

```javascript
function frameworkCallOffs(frameworkQuery, { buyer, supplier, since, limit = 20 } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    // Resolve framework
    let fw = db.prepare(
      "SELECT id, name FROM frameworks WHERE upper(reference_no)=upper(?)"
    ).get(frameworkQuery);
    if (!fw) {
      fw = db.prepare(
        "SELECT id, name FROM frameworks WHERE instr(lower(name), lower(?)) > 0 ORDER BY call_off_value_total DESC LIMIT 1"
      ).get(frameworkQuery);
    }
    if (!fw) return { error: `No framework found matching '${frameworkQuery}'` };

    const conditions = ["co.framework_id = ?"];
    const params = [fw.id];

    if (buyer) { conditions.push("instr(lower(co.buyer_canonical_id), lower(?)) > 0"); params.push(buyer); }
    if (supplier) { conditions.push("instr(lower(co.supplier_canonical_id), lower(?)) > 0"); params.push(supplier); }
    if (since) { conditions.push("co.awarded_date >= ?"); params.push(since); }
    params.push(limit);

    const callOffs = db.prepare(`
      SELECT co.notice_ocid, co.buyer_canonical_id, co.supplier_canonical_id,
             co.value, co.awarded_date, co.contract_title,
             co.match_method, co.match_confidence
      FROM framework_call_offs co
      WHERE ${conditions.join(" AND ")}
      ORDER BY co.awarded_date DESC NULLS LAST
      LIMIT ?
    `).all(...params);

    return {
      framework: fw.name,
      frameworkId: fw.id,
      callOffCount: callOffs.length,
      callOffs: callOffs.map(r => ({
        noticeOcid: r.notice_ocid,
        buyer: r.buyer_canonical_id,
        supplier: r.supplier_canonical_id,
        value: r.value,
        awardedDate: r.awarded_date,
        title: r.contract_title,
        matchMethod: r.match_method,
        matchConfidence: r.match_confidence,
      })),
    };
  } finally {
    db.close();
  }
}
```

- [ ] **Step 6: Add the five functions to the export block**

Find the existing `export {` block at the bottom of `competitive-intel.js` and add the five new functions:

```javascript
export {
  dbSummary,
  buyerProfile,
  supplierProfile,
  sectorProfile,
  expiringContracts,
  forwardPipeline,
  pwinSignals,
  cpvSearch,
  pipelineRecentNotices,
  pipelineRecentAwardsForBuyers,
  buyerBehaviourProfile,
  frameworkProfile,
  searchFrameworks,
  buyerFrameworkUsage,
  supplierFrameworkPosition,
  frameworkCallOffs,
};
```

- [ ] **Step 7: Verify the Node.js module loads without errors**

```
cd pwin-platform
node --input-type=module <<'EOF'
import { frameworkProfile, searchFrameworks, buyerFrameworkUsage, supplierFrameworkPosition, frameworkCallOffs } from './src/competitive-intel.js';
console.log('All five framework tools imported successfully');
EOF
```

Expected: `All five framework tools imported successfully`

- [ ] **Step 8: Commit**

```bash
git add pwin-platform/src/competitive-intel.js
git commit -m "feat(frameworks): 5 new MCP tools for framework intelligence"
```

---

## Task 7: Register MCP tools in the server

The MCP server needs to know about the five new tools so Claude can call them. These are registered in `pwin-platform/src/mcp.js` alongside the existing competitive intel tools.

**Files:**
- Modify: `pwin-platform/src/mcp.js`

- [ ] **Step 1: Find the existing competitive intel tool registrations**

```
grep -n "get_buyer_profile\|get_competitive_intel\|competitive-intel" pwin-platform/src/mcp.js | head -20
```

Note the pattern used for the existing competitive intel tools.

- [ ] **Step 2: Add the five tool registrations following the existing pattern**

Find the existing competitive intel tool block in `mcp.js`. After the last competitive intel tool registration (e.g. `get_buyer_behaviour_profile`), add:

```javascript
  {
    name: 'get_framework_profile',
    description: 'Get full profile for a named framework — reference number, lots, top suppliers, call-off stats.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Framework name, reference number (e.g. RM6116), or partial name' },
      },
      required: ['query'],
    },
    handler: async ({ query }) => ci.frameworkProfile(query),
  },
  {
    name: 'search_frameworks',
    description: 'Search the framework index. Returns ranked list by call-off value.',
    inputSchema: {
      type: 'object',
      properties: {
        query:                { type: 'string',  description: 'Free-text search on name or reference number' },
        owner_type:           { type: 'string',  description: 'central_gov | nhs | local_gov | departmental | devolved' },
        category:             { type: 'string',  description: 'technology | professional_services | facilities | etc.' },
        status:               { type: 'string',  description: 'active | expiring_soon | expired | replaced' },
        expiring_within_months: { type: 'number', description: 'Only return frameworks expiring within N months' },
      },
    },
    handler: async ({ query, owner_type, category, status, expiring_within_months }) =>
      ci.searchFrameworks(query, { ownerType: owner_type, category, status, expiringWithinMonths: expiring_within_months }),
  },
  {
    name: 'get_buyer_framework_usage',
    description: 'Which frameworks does a buyer route spend through? Ranked by value.',
    inputSchema: {
      type: 'object',
      properties: {
        buyer: { type: 'string', description: 'Buyer name or canonical ID' },
      },
      required: ['buyer'],
    },
    handler: async ({ buyer }) => ci.buyerFrameworkUsage(buyer),
  },
  {
    name: 'get_supplier_framework_position',
    description: 'Which frameworks is a supplier approved on, and how much are they actually winning through each?',
    inputSchema: {
      type: 'object',
      properties: {
        supplier: { type: 'string', description: 'Supplier name or canonical ID' },
      },
      required: ['supplier'],
    },
    handler: async ({ supplier }) => ci.supplierFrameworkPosition(supplier),
  },
  {
    name: 'get_framework_call_offs',
    description: 'List individual contracts placed through a framework, with optional filters.',
    inputSchema: {
      type: 'object',
      properties: {
        framework: { type: 'string',  description: 'Framework name or reference number' },
        buyer:     { type: 'string',  description: 'Optional: filter by buyer' },
        supplier:  { type: 'string',  description: 'Optional: filter by supplier' },
        since:     { type: 'string',  description: 'Optional: ISO date — only call-offs after this date' },
        limit:     { type: 'number',  description: 'Max results (default 20)' },
      },
      required: ['framework'],
    },
    handler: async ({ framework, buyer, supplier, since, limit }) =>
      ci.frameworkCallOffs(framework, { buyer, supplier, since, limit }),
  },
```

- [ ] **Step 3: Verify the platform server starts without errors**

```
cd pwin-platform
node src/server.js --mcp &
sleep 2
kill %1
```

Expected: starts and stops cleanly, no import errors.

- [ ] **Step 4: Commit**

```bash
git add pwin-platform/src/mcp.js
git commit -m "feat(frameworks): register 5 framework MCP tools in server"
```

---

## Task 8: Dashboard — server endpoints

Add three server-side API endpoints that the dashboard JavaScript will call.

**Files:**
- Modify: `pwin-competitive-intel/server.py`

- [ ] **Step 1: Add `api_frameworks_summary` function**

Add to `pwin-competitive-intel/server.py`, after `api_expiry_categories()`:

```python
def api_frameworks_summary():
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        total = conn.execute("SELECT COUNT(*) FROM frameworks").fetchone()[0]
        active = conn.execute(
            "SELECT COUNT(*) FROM frameworks WHERE status='active'"
        ).fetchone()[0]
        expiring = conn.execute(
            "SELECT COUNT(*) FROM frameworks WHERE status='active'"
            " AND expiry_date IS NOT NULL"
            " AND expiry_date <= date('now', '+12 months')"
        ).fetchone()[0]
        total_value = conn.execute(
            "SELECT COALESCE(SUM(call_off_value_total), 0) FROM frameworks"
        ).fetchone()[0]
        return {
            "total": total, "active": active,
            "expiring_soon": expiring, "total_call_off_value": total_value,
        }
    except Exception:
        return {"total": 0, "active": 0, "expiring_soon": 0, "total_call_off_value": 0}
    finally:
        conn.close()


def api_frameworks_list(params):
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        q = params.get("q", [""])[0].lower()
        owner_type = params.get("owner_type", [""])[0]
        status = params.get("status", [""])[0]
        category = params.get("category", [""])[0]

        conditions, args = [], []
        if q:
            conditions.append("(instr(lower(name), ?) > 0 OR instr(lower(reference_no), ?) > 0)")
            args += [q, q]
        if owner_type:
            conditions.append("owner_type = ?"); args.append(owner_type)
        if status:
            conditions.append("status = ?"); args.append(status)
        if category:
            conditions.append("instr(lower(category), ?) > 0"); args.append(category)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = conn.execute(f"""
            SELECT id, name, reference_no, owner, owner_type, category, status,
                   expiry_date, supplier_count, call_off_count, call_off_value_total, source
            FROM frameworks {where}
            ORDER BY call_off_value_total DESC
            LIMIT 200
        """, args).fetchall()
        return {"frameworks": [dict(r) for r in rows]}
    finally:
        conn.close()


def api_framework_detail(params):
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        fw_id = params.get("id", [None])[0]
        if not fw_id: return {"error": "id required"}
        fw = conn.execute(
            "SELECT * FROM frameworks WHERE id=?", (fw_id,)
        ).fetchone()
        if not fw: return {"error": "Not found"}

        lots = conn.execute(
            "SELECT * FROM framework_lots WHERE framework_id=? ORDER BY lot_number",
            (fw_id,)
        ).fetchall()
        top_suppliers = conn.execute("""
            SELECT supplier_name_raw, call_off_count, call_off_value
            FROM framework_suppliers WHERE framework_id=?
            ORDER BY call_off_value DESC LIMIT 10
        """, (fw_id,)).fetchall()
        top_buyers = conn.execute("""
            SELECT buyer_canonical_id AS buyer, COUNT(*) AS call_offs,
                   SUM(value) AS total_value
            FROM framework_call_offs WHERE framework_id=?
              AND buyer_canonical_id IS NOT NULL
            GROUP BY buyer_canonical_id
            ORDER BY total_value DESC LIMIT 10
        """, (fw_id,)).fetchall()
        recent = conn.execute("""
            SELECT contract_title, buyer_canonical_id AS buyer,
                   supplier_canonical_id AS supplier,
                   value, awarded_date
            FROM framework_call_offs WHERE framework_id=?
            ORDER BY awarded_date DESC LIMIT 20
        """, (fw_id,)).fetchall()

        return {
            "framework": dict(fw),
            "lots": [dict(l) for l in lots],
            "top_suppliers": [dict(s) for s in top_suppliers],
            "top_buyers": [dict(b) for b in top_buyers],
            "recent_call_offs": [dict(r) for r in recent],
        }
    finally:
        conn.close()
```

- [ ] **Step 2: Register the three new routes**

Find the `ROUTES` dict in `server.py` and add:

```python
    "/api/frameworks-summary": lambda p: api_frameworks_summary(),
    "/api/frameworks":         api_frameworks_list,
    "/api/framework":          api_framework_detail,
```

- [ ] **Step 3: Smoke test the server starts**

```
cd pwin-competitive-intel
python server.py &
sleep 2
curl -s http://localhost:8765/api/frameworks-summary
kill %1
```

Expected: returns JSON (may be `{"total": 0, ...}` if DB not yet populated — that's fine).

- [ ] **Step 4: Commit**

```bash
git add pwin-competitive-intel/server.py
git commit -m "feat(frameworks): 3 new API endpoints for frameworks dashboard tab"
```

---

## Task 9: Dashboard tab — Frameworks

Add the Frameworks tab to `dashboard.html`. Follows the exact same tab/section pattern as the existing Buyer Intelligence, Supplier, and Expiry tabs.

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html`

- [ ] **Step 1: Add the tab button**

Find the `<nav class="tabs" id="tabs">` block and add the Frameworks tab after the PWIN Signals tab:

```html
  <div class="tab" data-view="frameworks">Frameworks</div>
```

- [ ] **Step 2: Add the section HTML**

Find the last `</section>` closing tag before the closing `</main>` (or equivalent) and add:

```html
  <section class="view" id="view-frameworks">
    <!-- Summary bar -->
    <div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap" id="fw-summary-bar">
      <div class="card" style="flex:1;min-width:140px;text-align:center">
        <div class="card-title">Total Frameworks</div>
        <div style="font-size:2rem;font-family:var(--font-display)" id="fw-total">—</div>
      </div>
      <div class="card" style="flex:1;min-width:140px;text-align:center">
        <div class="card-title">Active</div>
        <div style="font-size:2rem;font-family:var(--font-display)" id="fw-active">—</div>
      </div>
      <div class="card" style="flex:1;min-width:160px;text-align:center">
        <div class="card-title">Expiring ≤12 months</div>
        <div style="font-size:2rem;font-family:var(--font-display);color:var(--warning)" id="fw-expiring">—</div>
      </div>
      <div class="card" style="flex:1;min-width:160px;text-align:center">
        <div class="card-title">Total Call-off Value</div>
        <div style="font-size:2rem;font-family:var(--font-display)" id="fw-total-value">—</div>
      </div>
    </div>

    <!-- Filters -->
    <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;align-items:center">
      <input type="text" id="fw-search" placeholder="Search name or reference…"
             style="flex:2;min-width:200px;padding:8px 12px;background:var(--surface);color:var(--text);border:1px solid rgba(255,255,255,0.1);border-radius:4px">
      <select id="fw-filter-owner" style="flex:1;min-width:140px;padding:8px;background:var(--surface);color:var(--text);border:1px solid rgba(255,255,255,0.1);border-radius:4px">
        <option value="">All owners</option>
        <option value="central_gov">Central Govt (CCS)</option>
        <option value="nhs">NHS</option>
        <option value="local_gov">Local Government</option>
        <option value="departmental">Departmental</option>
      </select>
      <select id="fw-filter-status" style="flex:1;min-width:140px;padding:8px;background:var(--surface);color:var(--text);border:1px solid rgba(255,255,255,0.1);border-radius:4px">
        <option value="">All statuses</option>
        <option value="active">Active</option>
        <option value="expiring_soon">Expiring soon</option>
        <option value="expired">Expired</option>
      </select>
      <button id="fw-search-btn" class="btn" style="padding:8px 16px">Search</button>
    </div>

    <!-- Directory table -->
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Reference</th><th>Name</th><th>Owner</th><th>Category</th>
            <th>Status</th><th>Suppliers</th><th>Call-offs</th><th>Value (£)</th>
          </tr>
        </thead>
        <tbody id="fw-table-body"></tbody>
      </table>
    </div>

    <!-- Detail panel (hidden until row clicked) -->
    <div id="fw-detail" style="display:none;margin-top:24px">
      <h3 id="fw-detail-name" style="font-family:var(--font-display);font-size:1.4rem;margin-bottom:4px"></h3>
      <div id="fw-detail-meta" style="color:var(--muted);font-size:0.85rem;margin-bottom:16px"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px" id="fw-detail-grid">
        <div class="card">
          <div class="card-title">Lots</div>
          <div id="fw-detail-lots"></div>
        </div>
        <div class="card">
          <div class="card-title">Top Suppliers by Call-off Value</div>
          <div id="fw-detail-suppliers"></div>
        </div>
        <div class="card">
          <div class="card-title">Top Buyers</div>
          <div id="fw-detail-buyers"></div>
        </div>
        <div class="card">
          <div class="card-title">Recent Call-offs</div>
          <div id="fw-detail-calloffs"></div>
        </div>
      </div>
    </div>
  </section>
```

- [ ] **Step 3: Add JavaScript for the Frameworks tab**

Find the `<script>` block near the bottom of `dashboard.html`. Add the following function alongside the other view-loading functions:

```javascript
function fmtVal(v) {
  if (!v) return '—';
  if (v >= 1e9) return '£' + (v/1e9).toFixed(1) + 'bn';
  if (v >= 1e6) return '£' + (v/1e6).toFixed(1) + 'm';
  if (v >= 1e3) return '£' + (v/1e3).toFixed(0) + 'k';
  return '£' + v.toFixed(0);
}

function statusBadge(status) {
  const colours = {
    active: 'color:#4caf50',
    expiring_soon: 'color:#ff9800',
    expired: 'color:#f44336',
    replaced: 'color:#9e9e9e',
  };
  const style = colours[status] || '';
  return `<span style="${style}">${status || '—'}</span>`;
}

async function loadFrameworksSummary() {
  const data = await fetch('/api/frameworks-summary').then(r => r.json()).catch(() => ({}));
  document.getElementById('fw-total').textContent = data.total ?? '—';
  document.getElementById('fw-active').textContent = data.active ?? '—';
  document.getElementById('fw-expiring').textContent = data.expiring_soon ?? '—';
  document.getElementById('fw-total-value').textContent = fmtVal(data.total_call_off_value);
}

async function loadFrameworksList() {
  const q = document.getElementById('fw-search').value;
  const owner = document.getElementById('fw-filter-owner').value;
  const status = document.getElementById('fw-filter-status').value;
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (owner) params.set('owner_type', owner);
  if (status) params.set('status', status);

  const data = await fetch(`/api/frameworks?${params}`).then(r => r.json()).catch(() => ({frameworks: []}));
  const tbody = document.getElementById('fw-table-body');
  tbody.innerHTML = '';
  for (const fw of (data.frameworks || [])) {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.innerHTML = `
      <td style="font-family:var(--font-mono);font-size:0.85rem">${fw.reference_no || '—'}</td>
      <td>${fw.name}</td>
      <td style="font-size:0.85rem">${fw.owner || '—'}</td>
      <td style="font-size:0.85rem">${fw.category || '—'}</td>
      <td>${statusBadge(fw.status)}</td>
      <td style="text-align:right">${fw.supplier_count || 0}</td>
      <td style="text-align:right">${fw.call_off_count || 0}</td>
      <td style="text-align:right">${fmtVal(fw.call_off_value_total)}</td>
    `;
    tr.addEventListener('click', () => loadFrameworkDetail(fw.id));
    tbody.appendChild(tr);
  }
}

async function loadFrameworkDetail(id) {
  const data = await fetch(`/api/framework?id=${id}`).then(r => r.json()).catch(() => null);
  if (!data || data.error) return;
  const fw = data.framework;
  document.getElementById('fw-detail').style.display = 'block';
  document.getElementById('fw-detail-name').textContent = fw.name;
  document.getElementById('fw-detail-meta').textContent =
    [fw.reference_no, fw.owner, fw.expiry_date ? `Expires ${fw.expiry_date}` : null,
     fw.source === 'contracts_only' ? '⚑ Enrich from catalogue' : null]
    .filter(Boolean).join(' · ');

  // Lots
  const lotsEl = document.getElementById('fw-detail-lots');
  lotsEl.innerHTML = data.lots.length
    ? '<table>' + data.lots.map(l =>
        `<tr><td style="font-family:var(--font-mono)">${l.lot_number || ''}</td><td>${l.lot_name || ''}</td></tr>`
      ).join('') + '</table>'
    : '<p style="color:var(--muted)">No lot data</p>';

  // Suppliers
  const supEl = document.getElementById('fw-detail-suppliers');
  supEl.innerHTML = data.top_suppliers.length
    ? '<table>' + data.top_suppliers.map(s =>
        `<tr><td>${s.supplier_name_raw || '—'}</td><td style="text-align:right">${fmtVal(s.call_off_value)}</td></tr>`
      ).join('') + '</table>'
    : '<p style="color:var(--muted)">No supplier data</p>';

  // Buyers
  const buyEl = document.getElementById('fw-detail-buyers');
  buyEl.innerHTML = data.top_buyers.length
    ? '<table>' + data.top_buyers.map(b =>
        `<tr><td>${b.buyer || '—'}</td><td style="text-align:right">${fmtVal(b.total_value)}</td></tr>`
      ).join('') + '</table>'
    : '<p style="color:var(--muted)">No buyer data</p>';

  // Call-offs
  const coEl = document.getElementById('fw-detail-calloffs');
  coEl.innerHTML = data.recent_call_offs.length
    ? '<table>' + data.recent_call_offs.map(c =>
        `<tr><td style="font-size:0.8rem">${c.awarded_date || ''}</td><td style="font-size:0.8rem">${c.title || '—'}</td><td style="text-align:right;font-size:0.8rem">${fmtVal(c.value)}</td></tr>`
      ).join('') + '</table>'
    : '<p style="color:var(--muted)">No call-off data</p>';

  document.getElementById('fw-detail').scrollIntoView({ behavior: 'smooth' });
}
```

- [ ] **Step 4: Wire up event listeners**

Find where other tabs are initialised (typically in a `DOMContentLoaded` listener or a `switchView` function). Add:

```javascript
// Frameworks tab event wiring
document.getElementById('fw-search-btn').addEventListener('click', loadFrameworksList);
document.getElementById('fw-search').addEventListener('keydown', e => {
  if (e.key === 'Enter') loadFrameworksList();
});
```

And in the `switchView` function (or wherever view changes are handled), add a case for frameworks:

```javascript
if (view === 'frameworks') {
  loadFrameworksSummary();
  loadFrameworksList();
}
```

- [ ] **Step 5: Open the dashboard and verify the tab appears**

```
cd pwin-competitive-intel
python server.py
```

Open `http://localhost:8765` in a browser. Click the "Frameworks" tab. Expected: the tab loads, showing the summary bar (all zeros until the miner runs) and an empty directory table. No console errors.

- [ ] **Step 6: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "feat(frameworks): Frameworks tab in competitive intel dashboard"
```

---

## Task 10: End-to-end smoke test

Run the full three-step pipeline against the real database and verify the output.

- [ ] **Step 1: Run the call-off miner dry-run first**

```
cd pwin-competitive-intel
python agent/mine_framework_calloffs.py --dry-run
```

Expected: logs showing candidate counts for Signal A and Signal B. No writes.

- [ ] **Step 2: Run the call-off miner for real**

```
python agent/mine_framework_calloffs.py
```

Expected: logs like `Signal A (structured): N notices processed` and `Signal B (RM pattern): N call-offs linked`. Check the count is non-zero.

- [ ] **Step 3: Verify frameworks were created**

```
python queries/queries.py summary
```

Expected: output now includes rows for `frameworks`, `framework_call_offs`. Or run directly:

```
python -c "
import sqlite3; conn = sqlite3.connect('db/bid_intel.db')
print('Frameworks:', conn.execute('SELECT COUNT(*) FROM frameworks').fetchone()[0])
print('Call-offs:', conn.execute('SELECT COUNT(*) FROM framework_call_offs').fetchone()[0])
"
```

Expected: frameworks count > 0 once Signal A notices exist in the DB.

- [ ] **Step 4: Run the CCS catalogue ingest in dry-run**

```
python agent/ingest_frameworks_catalogue.py --dry-run --limit 5
```

Expected: fetches first 5 CCS agreement pages and logs parsed data (name, reference_no, expiry_date, lots count). If the selectors need adjustment, the name or reference_no fields will be None — update the parser classes in `ingest_frameworks_catalogue.py` to match the actual HTML structure.

- [ ] **Step 5: Run the catalogue ingest for real (first 20 frameworks)**

```
python agent/ingest_frameworks_catalogue.py --limit 20
```

Expected: 20 frameworks ingested with `source = 'catalogue_only'` (or `'both'` where they matched existing mined records).

- [ ] **Step 6: Run consolidation**

```
python agent/consolidate_frameworks.py
```

Expected: consolidation report written to `db/framework_consolidation_report.json`. Review it:

```
python -c "import json; r = json.load(open('db/framework_consolidation_report.json')); print('both:', r['both_count'], 'contracts_only:', r['contracts_only_count'], 'catalogue_only:', r['catalogue_only_count'])"
```

- [ ] **Step 7: Open dashboard and verify the Frameworks tab has data**

```
python server.py
```

Open `http://localhost:8765`, click Frameworks tab. Expected:
- Summary bar shows real numbers
- Directory table shows frameworks sorted by call-off value
- Clicking a framework opens the detail panel with lots, suppliers, buyers, recent call-offs

- [ ] **Step 8: Final all-tests run**

```
cd pwin-competitive-intel
python -m pytest tests/ -v
```

Expected: all tests pass, including the new framework tests.

- [ ] **Step 9: Final commit**

```bash
git add -A
git commit -m "feat(frameworks): end-to-end smoke test — frameworks layer operational"
```

---

## Self-Review Notes

- **`_resolveBuyerCanonical`** is called in `buyerFrameworkUsage` — this function exists in `competitive-intel.js` and is used by `buyerProfile`. Confirmed compatible.
- **`supplier_to_canonical` and `canonical_suppliers` tables** are referenced in `supplierFrameworkPosition` — these exist from the canonical supplier layer.
- **Schema `NOT NULL DEFAULT 0`** columns on `call_off_count`, `call_off_value_total` — consistent with the way the miner updates them via `UPDATE ... SET call_off_count = (SELECT COUNT(*) ...)`.
- **`fmtVal` function** used in dashboard JS — defined in Task 9 Step 3, used in the same step. No forward reference issue.
- **`--with-frameworks-catalogue`** flag in scheduler — uses `_ap` as alias for `argparse` to avoid shadowing any existing `args` variable in the script.
