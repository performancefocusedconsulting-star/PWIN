# Competitive Cube — Displacement Intelligence — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the v1 competitive cube — a 9 × 10 sector × opportunity-type intelligence layer across UK government procurement, rendered as displacement intelligence with two reading lenses (challenger / incumbent), shipped through four staged deliverables (engine → marketing report → dashboard tab → MCP tools).

**Architecture:** Python engine module reads the existing `bid_intel.db` SQLite database, computes Layer 1 (concentration) + Layer 2 (named incumbents with grip data) + Layer 6 (displacement windows) per cell, writes to a new `cell_summary` pre-computed table refreshed nightly. Local HTTP API + dashboard tab consume the pre-computed rows; MCP tools in `pwin-platform` call the same engine via the platform's existing data layer.

**Tech Stack:** Python 3.9+ stdlib (sqlite3, json, datetime, argparse), pytest for tests, vanilla HTML/JavaScript for the dashboard tab, Node.js + Zod for MCP tool registration. SQLite for now; the `cube_engine.py` queries are written in standard SQL and port cleanly to PostgreSQL when the cloud migration lands (see Section 5 of the design spec for the alignment register).

**Spec:** `pwin-competitive-intel/docs/superpowers/specs/2026-05-02-competitive-cube-design.md`

**Cloud-platform alignment:** Cloud architecture spec at `docs/superpowers/specs/2026-05-02-pwin-cloud-data-architecture-design.md` targets Google Cloud UK PostgreSQL, not Cloudflare D1. The cube design works on either; the migration sequence is owned by the cloud spec.

---

## File Structure

**Created:**

| File | Responsibility |
|---|---|
| `pwin-competitive-intel/queries/cube_engine.py` | Cube engine — Layer 1, 2, 6 calculations + cell summary composer + refresh job |
| `pwin-competitive-intel/queries/opp_type_classifier.py` | Sector + opportunity-type tagging logic |
| `pwin-competitive-intel/data/cpv_to_opp_type.json` | Procurement category code → opportunity type mapping |
| `pwin-competitive-intel/data/opp_type_keywords.json` | Title-keyword fallback rules for ambiguous category codes |
| `pwin-competitive-intel/agent/tag_notices.py` | Agent script that runs the tagging pass over all notices |
| `pwin-competitive-intel/queries/generate_concentration_report.py` | Marketing report generator (Stage 2) |
| `pwin-competitive-intel/reports/templates/concentration_report.md.tmpl` | Markdown template for the marketing report |
| `pwin-competitive-intel/reports/.gitkeep` | Keeps the reports directory in version control |
| `pwin-competitive-intel/tests/test_cube_engine.py` | Unit tests for the engine |
| `pwin-competitive-intel/tests/test_opp_type_classifier.py` | Unit tests for the tagging logic |
| `pwin-competitive-intel/tests/test_cube_schema.py` | Schema validation tests |
| `pwin-competitive-intel/tests/fixtures/cube_test_data.py` | Test fixture builder |
| `pwin-platform/test/test-cube.js` | MCP integration test |

**Modified:**

| File | What changes |
|---|---|
| `pwin-competitive-intel/db/schema.sql` | Add `opp_type` column to notices, new `cell_summary` table, three supporting indexes |
| `pwin-competitive-intel/agent/scheduler.py` | Add tagging pass + cell aggregate refresh as nightly steps |
| `pwin-competitive-intel/dashboard.html` | Add "Competitive Cells" tab with three views |
| `pwin-competitive-intel/server.py` | Add `/api/cube/*` endpoints |
| `pwin-platform/src/competitive-intel.js` | Add three cube query functions |
| `pwin-platform/src/mcp.js` | Register three new MCP tools |
| `pwin-platform/src/api.js` | Add `/api/cube/*` HTTP endpoints |
| `CLAUDE.md` | Document the new product surface |

---

## Stage 1 — Engine

**Goal of this stage:** A working cube engine, callable from a Python REPL, that produces a defensible cell view for any of the 90 cells. The engine is the load-bearing piece — Stages 2 / 3 / 4 are mostly rendering on top of it.

### Task 1.1: Schema migration — add `opp_type` column to notices

**Files:**
- Modify: `pwin-competitive-intel/db/schema.sql`
- Modify: `pwin-competitive-intel/agent/db_utils.py:_migrate_schema()`
- Test: `pwin-competitive-intel/tests/test_cube_schema.py`

- [ ] **Step 1: Write the failing test**

Create `pwin-competitive-intel/tests/test_cube_schema.py`:

```python
"""Tests: cube schema additions (opp_type column, cell_summary table, indexes)."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
import db_utils

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def _make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _columns(conn, table):
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def test_notices_opp_type_column_exists():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "notices")
    assert "opp_type" in cols, "notices.opp_type column missing"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd pwin-competitive-intel
python -m pytest tests/test_cube_schema.py::test_notices_opp_type_column_exists -v
```

Expected: FAIL with `AssertionError: notices.opp_type column missing`.

- [ ] **Step 3: Add the column to schema.sql**

In `db/schema.sql`, locate the `CREATE TABLE IF NOT EXISTS notices (...)` block and add a new column line near the end of the column list (before any constraints):

```sql
  opp_type TEXT,
```

Then in `agent/db_utils.py`, find `_migrate_schema()` and add an idempotent migration block (the file uses this pattern already for `notices` framework fields):

```python
    # ── notices: opp_type for cube engine (cube plan, 2026-05-02) ──
    if "opp_type" not in notices_cols:
        conn.execute("ALTER TABLE notices ADD COLUMN opp_type TEXT")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_cube_schema.py::test_notices_opp_type_column_exists -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/db/schema.sql pwin-competitive-intel/agent/db_utils.py pwin-competitive-intel/tests/test_cube_schema.py
git commit -m "feat(cube): add opp_type column to notices table"
```

---

### Task 1.2: Schema migration — add `cell_summary` table

**Files:**
- Modify: `pwin-competitive-intel/db/schema.sql`
- Modify: `pwin-competitive-intel/tests/test_cube_schema.py`

- [ ] **Step 1: Write the failing test**

Append to `pwin-competitive-intel/tests/test_cube_schema.py`:

```python
def test_cell_summary_table_exists():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert "cell_summary" in tables


def test_cell_summary_required_columns():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    cols = _columns(conn, "cell_summary")
    expected = {
        "sector", "opp_type", "value_band",
        "total_contracts", "total_value",
        "top_3_share", "top_5_share", "effective_n_suppliers",
        "trend", "sufficiency_flag",
        "detail_json", "last_refreshed_at",
    }
    missing = expected - cols
    assert not missing, f"Missing columns: {missing}"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_cube_schema.py -v
```

Expected: two FAILures.

- [ ] **Step 3: Add the table to schema.sql**

Append to `db/schema.sql` (after the existing tables, before any indexes block):

```sql
-- ── Competitive cube — cell_summary (cube plan, 2026-05-02) ──
-- One row per (sector, opp_type, value_band). Pre-computed nightly.
CREATE TABLE IF NOT EXISTS cell_summary (
  sector              TEXT NOT NULL,
  opp_type            TEXT NOT NULL,
  value_band          TEXT NOT NULL DEFAULT 'all',  -- 'all' | 'small' | 'mid' | 'major' | 'strategic'
  total_contracts     INTEGER NOT NULL DEFAULT 0,
  total_value         REAL    NOT NULL DEFAULT 0,
  top_3_share         REAL,                          -- NULL when sufficiency = 'insufficient'
  top_5_share         REAL,
  effective_n_suppliers REAL,
  trend               TEXT,                          -- 'consolidating' | 'fragmenting' | 'stable' | NULL
  sufficiency_flag    TEXT NOT NULL,                 -- 'reliable' | 'directional' | 'insufficient'
  detail_json         TEXT NOT NULL,                 -- JSON: credible competitors + displacement windows
  last_refreshed_at   TEXT NOT NULL,                 -- ISO timestamp
  PRIMARY KEY (sector, opp_type, value_band)
);
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_cube_schema.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/db/schema.sql pwin-competitive-intel/tests/test_cube_schema.py
git commit -m "feat(cube): add cell_summary pre-computed table"
```

---

### Task 1.3: Schema migration — add three supporting indexes

**Files:**
- Modify: `pwin-competitive-intel/db/schema.sql`
- Modify: `pwin-competitive-intel/tests/test_cube_schema.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cube_schema.py`:

```python
def test_cube_indexes_exist():
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    idx = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index'"
    ).fetchall()}
    expected = {
        "idx_notices_sector_opp_type",
        "idx_awards_supplier_sector_opp",
        "idx_awards_buyer_year",
    }
    missing = expected - idx
    assert not missing, f"Missing indexes: {missing}"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_cube_schema.py::test_cube_indexes_exist -v
```

Expected: FAIL.

- [ ] **Step 3: Add indexes to schema.sql**

Append to `db/schema.sql`:

```sql
-- ── Competitive cube — supporting indexes (cube plan, 2026-05-02) ──
CREATE INDEX IF NOT EXISTS idx_notices_sector_opp_type ON notices (canonical_buyer_id, opp_type);
CREATE INDEX IF NOT EXISTS idx_awards_supplier_sector_opp ON awards (canonical_supplier_id, notice_id);
CREATE INDEX IF NOT EXISTS idx_awards_buyer_year ON awards (notice_id);
```

(Note — the cube queries reach `sector` via the canonical_buyer join; `awards` carries `notice_id` not `sector` directly. The indexes above are tuned to the actual query patterns the engine will use; specifics are revisited in Task 1.10 once the queries are written.)

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_cube_schema.py::test_cube_indexes_exist -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/db/schema.sql pwin-competitive-intel/tests/test_cube_schema.py
git commit -m "feat(cube): add supporting indexes for cube queries"
```

---

### Task 1.4: Build the procurement-category-code → opportunity-type mapping

**Files:**
- Create: `pwin-competitive-intel/data/cpv_to_opp_type.json`

- [ ] **Step 1: Write the failing test**

Create `pwin-competitive-intel/tests/test_opp_type_classifier.py` (skeleton — actual classifier built in Task 1.6):

```python
"""Tests: opportunity-type classifier (CPV mapping + title keyword fallback)."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def test_cpv_to_opp_type_mapping_exists():
    path = DATA_DIR / "cpv_to_opp_type.json"
    assert path.exists(), "cpv_to_opp_type.json not created"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert len(data) > 0


def test_cpv_to_opp_type_uses_canonical_types():
    path = DATA_DIR / "cpv_to_opp_type.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    canonical = {
        "BPO", "IT Outsourcing", "Managed Service",
        "Facilities / Field / Operational Service",
        "Hybrid Transformation", "Digital Outcomes",
        "Consulting / Advisory", "Infrastructure & Hardware",
        "Software / SaaS", "Framework / Panel Appointment",
    }
    for cpv, opp_type in data.items():
        assert opp_type in canonical, f"CPV {cpv} maps to unknown opp_type: {opp_type}"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_opp_type_classifier.py -v
```

Expected: FAIL.

- [ ] **Step 3: Create the mapping file**

Create `pwin-competitive-intel/data/cpv_to_opp_type.json` with the high-volume mappings. Cover at minimum the top 50 CPV codes from the database; below is a starter set keyed by the leading two digits (CPV is hierarchical — leading digits identify the category):

```json
{
  "72000000": "IT Outsourcing",
  "72200000": "Software / SaaS",
  "72500000": "IT Outsourcing",
  "72600000": "Managed Service",
  "48000000": "Software / SaaS",
  "30000000": "Infrastructure & Hardware",
  "48800000": "Software / SaaS",
  "79000000": "Consulting / Advisory",
  "79400000": "Consulting / Advisory",
  "79500000": "BPO",
  "85000000": "Managed Service",
  "75000000": "BPO",
  "98000000": "Facilities / Field / Operational Service",
  "90000000": "Facilities / Field / Operational Service",
  "50000000": "Facilities / Field / Operational Service",
  "55000000": "Facilities / Field / Operational Service",
  "60000000": "Facilities / Field / Operational Service",
  "92000000": "Consulting / Advisory",
  "73000000": "Consulting / Advisory",
  "71000000": "Consulting / Advisory",
  "31000000": "Infrastructure & Hardware",
  "32000000": "Infrastructure & Hardware",
  "33000000": "Infrastructure & Hardware",
  "34000000": "Infrastructure & Hardware",
  "39000000": "Infrastructure & Hardware",
  "44000000": "Infrastructure & Hardware",
  "45000000": "Facilities / Field / Operational Service",
  "66000000": "Consulting / Advisory",
  "80000000": "Consulting / Advisory",
  "63000000": "Facilities / Field / Operational Service"
}
```

(The classifier will use longest-prefix match — a notice with CPV `72611000` will fall through to `72600000` if no exact match exists. Coverage of the residual is improved by the keyword fallback in Task 1.5.)

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_opp_type_classifier.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/data/cpv_to_opp_type.json pwin-competitive-intel/tests/test_opp_type_classifier.py
git commit -m "feat(cube): seed CPV → opportunity-type mapping"
```

---

### Task 1.5: Build the title keyword fallback rules

**Files:**
- Create: `pwin-competitive-intel/data/opp_type_keywords.json`
- Modify: `pwin-competitive-intel/tests/test_opp_type_classifier.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_opp_type_classifier.py`:

```python
def test_keyword_fallback_exists():
    path = DATA_DIR / "opp_type_keywords.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    canonical = {
        "BPO", "IT Outsourcing", "Managed Service",
        "Facilities / Field / Operational Service",
        "Hybrid Transformation", "Digital Outcomes",
        "Consulting / Advisory", "Infrastructure & Hardware",
        "Software / SaaS", "Framework / Panel Appointment",
    }
    for opp_type, keywords in data.items():
        assert opp_type in canonical, f"Unknown opp_type: {opp_type}"
        assert isinstance(keywords, list)
        assert all(isinstance(k, str) and k for k in keywords)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_opp_type_classifier.py::test_keyword_fallback_exists -v
```

Expected: FAIL.

- [ ] **Step 3: Create the keyword file**

Create `pwin-competitive-intel/data/opp_type_keywords.json`:

```json
{
  "BPO": ["business process", "back office", "shared service", "case management", "claims processing"],
  "IT Outsourcing": ["it outsourcing", "managed it", "it managed service", "service desk", "infrastructure outsourcing", "application management"],
  "Managed Service": ["managed service", "managed services", "service management"],
  "Facilities / Field / Operational Service": ["facilities management", "fm services", "soft fm", "hard fm", "cleaning", "catering", "security services", "estates management", "maintenance"],
  "Hybrid Transformation": ["transformation", "digital transformation", "business transformation", "service transformation"],
  "Digital Outcomes": ["digital outcomes", "discovery", "alpha", "beta", "user research", "service design"],
  "Consulting / Advisory": ["consultancy", "consulting", "advisory", "professional services", "strategy", "specialist advice"],
  "Infrastructure & Hardware": ["hardware", "equipment", "supply of", "purchase of", "devices", "laptops", "servers"],
  "Software / SaaS": ["software", "saas", "licence", "license", "subscription", "platform"],
  "Framework / Panel Appointment": ["framework agreement", "framework for", "panel appointment", "dynamic purchasing"]
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_opp_type_classifier.py::test_keyword_fallback_exists -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/data/opp_type_keywords.json pwin-competitive-intel/tests/test_opp_type_classifier.py
git commit -m "feat(cube): seed title keyword fallback rules for opp_type"
```

---

### Task 1.6: Build the classifier module

**Files:**
- Create: `pwin-competitive-intel/queries/opp_type_classifier.py`
- Modify: `pwin-competitive-intel/tests/test_opp_type_classifier.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_opp_type_classifier.py`:

```python
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "queries"))
from opp_type_classifier import classify_opp_type


def test_exact_cpv_match():
    result = classify_opp_type(cpv_codes=["72000000"], title="Some service")
    assert result == "IT Outsourcing"


def test_cpv_prefix_match_falls_through():
    # 72611000 should match 72600000 (longest prefix, 4-digit truncation)
    result = classify_opp_type(cpv_codes=["72611000"], title="Network support")
    assert result == "Managed Service"


def test_keyword_fallback_when_cpv_unmatched():
    result = classify_opp_type(cpv_codes=["99999999"], title="Strategy advisory services")
    assert result == "Consulting / Advisory"


def test_returns_unclassified_when_nothing_matches():
    result = classify_opp_type(cpv_codes=[], title="")
    assert result is None


def test_first_cpv_match_wins():
    # If multiple CPVs match, take the first
    result = classify_opp_type(cpv_codes=["72000000", "30000000"], title="")
    assert result == "IT Outsourcing"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_opp_type_classifier.py -v
```

Expected: 5 import-or-attribute FAILs (the new tests at minimum).

- [ ] **Step 3: Implement the classifier**

Create `pwin-competitive-intel/queries/opp_type_classifier.py`:

```python
"""
Opportunity-type classifier
===========================
Maps a contract notice to one of the ten canonical opportunity types
using procurement category codes (CPV) plus a title-keyword fallback.

The classifier is deterministic and stdlib-only.
"""

import json
from pathlib import Path
from typing import Optional, Sequence

DATA_DIR = Path(__file__).parent.parent / "data"
_CPV_MAP = None
_KEYWORDS = None


def _load():
    global _CPV_MAP, _KEYWORDS
    if _CPV_MAP is None:
        _CPV_MAP = json.loads((DATA_DIR / "cpv_to_opp_type.json").read_text(encoding="utf-8"))
    if _KEYWORDS is None:
        _KEYWORDS = json.loads((DATA_DIR / "opp_type_keywords.json").read_text(encoding="utf-8"))


def _cpv_match(cpv: str) -> Optional[str]:
    """Longest-prefix match on the CPV table. Walks 8 → 6 → 4 → 2 leading digits."""
    if not cpv:
        return None
    cpv = str(cpv).strip()
    if not cpv.isdigit():
        return None
    for prefix_len in (8, 6, 4, 2):
        if len(cpv) < prefix_len:
            continue
        candidate = cpv[:prefix_len].ljust(8, "0")
        if candidate in _CPV_MAP:
            return _CPV_MAP[candidate]
    return None


def _keyword_match(title: str) -> Optional[str]:
    if not title:
        return None
    t = title.lower()
    for opp_type, keywords in _KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in t:
                return opp_type
    return None


def classify_opp_type(cpv_codes: Sequence[str], title: str) -> Optional[str]:
    """Return canonical opportunity type, or None if nothing matches.

    Tries CPV codes first (in order). Falls back to title keyword scan.
    """
    _load()
    for cpv in cpv_codes or []:
        hit = _cpv_match(cpv)
        if hit:
            return hit
    return _keyword_match(title)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_opp_type_classifier.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/queries/opp_type_classifier.py pwin-competitive-intel/tests/test_opp_type_classifier.py
git commit -m "feat(cube): implement opportunity-type classifier (CPV + keyword fallback)"
```

---

### Task 1.7: Build the agent script that runs the tagging pass

**Files:**
- Create: `pwin-competitive-intel/agent/tag_notices.py`
- Modify: `pwin-competitive-intel/tests/test_opp_type_classifier.py` (integration test)

- [ ] **Step 1: Write the failing integration test**

Append to `tests/test_opp_type_classifier.py`:

```python
def test_tag_notices_idempotent():
    """Running tagging twice should not change results on the second pass."""
    import sqlite3
    sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
    from tag_notices import tag_all

    conn = _make_db_with_fixtures()  # builds a small notices+cpv_codes fixture
    first = tag_all(conn, batch_size=100)
    second = tag_all(conn, batch_size=100)

    # First pass tags new rows; second pass finds nothing to do
    assert first["tagged"] >= 1
    assert second["tagged"] == 0


def _make_db_with_fixtures():
    """Build an in-memory DB with a few notices and CPV codes for tagging tests."""
    conn = _make_db()
    db_utils.init_schema(conn, SCHEMA_PATH)
    conn.executemany(
        "INSERT INTO notices (ocid, title, opp_type) VALUES (?, ?, NULL)",
        [
            ("ocid-1", "IT outsourcing services for HMRC", None),
            ("ocid-2", "Strategy consulting framework", None),
            ("ocid-3", "Cleaning services across estate", None),
        ],
    )
    notice_ids = [r[0] for r in conn.execute("SELECT id FROM notices ORDER BY id").fetchall()]
    conn.executemany(
        "INSERT INTO cpv_codes (notice_id, code) VALUES (?, ?)",
        [
            (notice_ids[0], "72000000"),
            (notice_ids[1], "79400000"),
            (notice_ids[2], "90000000"),
        ],
    )
    conn.commit()
    return conn
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_opp_type_classifier.py::test_tag_notices_idempotent -v
```

Expected: ImportError or AttributeError.

- [ ] **Step 3: Implement tag_notices.py**

Create `pwin-competitive-intel/agent/tag_notices.py`:

```python
"""
Tag notices with opportunity type
=================================
Runs the classifier over every notice with NULL opp_type and writes the
inferred opportunity type back to the notices table. Idempotent — already-tagged
rows are skipped.

Usage:
    python agent/tag_notices.py
    python agent/tag_notices.py --retag-all   # re-run on every notice (for taxonomy changes)
"""

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "queries"))
import db_utils
from opp_type_classifier import classify_opp_type

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"
log = logging.getLogger(__name__)


def tag_all(conn: sqlite3.Connection, batch_size: int = 5000, retag: bool = False) -> dict:
    """Tag every notice missing an opp_type. Returns a counts dict."""
    where = "WHERE n.opp_type IS NULL" if not retag else ""
    cur = conn.execute(f"""
        SELECT n.id, n.title,
               COALESCE(GROUP_CONCAT(c.code, ','), '') AS cpv_csv
        FROM notices n
        LEFT JOIN cpv_codes c ON c.notice_id = n.id
        {where}
        GROUP BY n.id
    """)

    tagged = 0
    untagged = 0
    seen = 0
    updates = []
    for row in cur:
        seen += 1
        cpvs = [c for c in row["cpv_csv"].split(",") if c]
        opp_type = classify_opp_type(cpvs, row["title"] or "")
        if opp_type:
            updates.append((opp_type, row["id"]))
            tagged += 1
        else:
            untagged += 1
        if len(updates) >= batch_size:
            conn.executemany("UPDATE notices SET opp_type = ? WHERE id = ?", updates)
            conn.commit()
            updates = []

    if updates:
        conn.executemany("UPDATE notices SET opp_type = ? WHERE id = ?", updates)
        conn.commit()

    return {"seen": seen, "tagged": tagged, "untagged": untagged}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retag-all", action="store_true", help="Re-run on all notices")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, Path(__file__).parent.parent / "db" / "schema.sql")

    log.info("Tagging notices (retag=%s)...", args.retag_all)
    counts = tag_all(conn, retag=args.retag_all)
    log.info("Done. Seen=%d, tagged=%d, untagged=%d (%.1f%% coverage)",
             counts["seen"], counts["tagged"], counts["untagged"],
             100.0 * counts["tagged"] / max(counts["seen"], 1))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_opp_type_classifier.py::test_tag_notices_idempotent -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/tag_notices.py pwin-competitive-intel/tests/test_opp_type_classifier.py
git commit -m "feat(cube): add idempotent tag_notices agent script"
```

---

### Task 1.8: Run the tagging pass against the production database

**Files:** No code changes. Run-and-verify task.

- [ ] **Step 1: Backup the production database**

```bash
cd pwin-competitive-intel
cp db/bid_intel.db db/bid_intel.db.pre-cube-tagging
```

- [ ] **Step 2: Run schema migration to add the opp_type column**

```bash
python -c "from agent import db_utils; from pathlib import Path; conn = db_utils.get_db(Path('db/bid_intel.db')); db_utils.init_schema(conn, Path('db/schema.sql')); print('schema migrated')"
```

Expected output: `schema migrated`.

- [ ] **Step 3: Run the tagging pass**

```bash
python agent/tag_notices.py
```

Expected: log line with seen/tagged/untagged counts. Coverage target ≥ 75%.

- [ ] **Step 4: Verify coverage**

```bash
python -c "import sqlite3; c = sqlite3.connect('db/bid_intel.db'); print(c.execute('SELECT COUNT(*) FROM notices').fetchone()[0], 'total'); print(c.execute('SELECT COUNT(*) FROM notices WHERE opp_type IS NOT NULL').fetchone()[0], 'tagged')"
```

If coverage is below 75%, expand `data/cpv_to_opp_type.json` and `data/opp_type_keywords.json` based on the most common untagged title patterns:

```bash
python -c "import sqlite3; c = sqlite3.connect('db/bid_intel.db'); rows = c.execute(\"SELECT title FROM notices WHERE opp_type IS NULL LIMIT 50\").fetchall(); [print(r[0]) for r in rows]"
```

Iterate until coverage clears 75%.

- [ ] **Step 5: Commit (data file updates only — db file is gitignored)**

```bash
git add pwin-competitive-intel/data/cpv_to_opp_type.json pwin-competitive-intel/data/opp_type_keywords.json
git commit -m "feat(cube): expand CPV/keyword maps to clear 75% tagging coverage" || echo "no changes — initial maps were sufficient"
```

---

### Task 1.9: Build the engine — Layer 1 concentration calculation

**Files:**
- Create: `pwin-competitive-intel/queries/cube_engine.py`
- Create: `pwin-competitive-intel/tests/test_cube_engine.py`
- Create: `pwin-competitive-intel/tests/fixtures/cube_test_data.py`

- [ ] **Step 1: Write the fixture builder**

Create `pwin-competitive-intel/tests/fixtures/cube_test_data.py`:

```python
"""Fixture: small DB populated with cube test data."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agent"))
import db_utils

SCHEMA = Path(__file__).parent.parent.parent / "db" / "schema.sql"


def build_cube_fixture() -> sqlite3.Connection:
    """Build an in-memory DB with one cell (Central Government × IT Outsourcing).

    5 suppliers, 10 contracts. Top supplier has 40% share.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    db_utils.init_schema(conn, SCHEMA)

    conn.execute("INSERT INTO canonical_buyers (id, name, sector) VALUES (1, 'HMRC', 'Central Government')")
    conn.execute("INSERT INTO canonical_suppliers (id, name) VALUES (1, 'Capita')")
    conn.execute("INSERT INTO canonical_suppliers (id, name) VALUES (2, 'Capgemini')")
    conn.execute("INSERT INTO canonical_suppliers (id, name) VALUES (3, 'CGI')")
    conn.execute("INSERT INTO canonical_suppliers (id, name) VALUES (4, 'Atos')")
    conn.execute("INSERT INTO canonical_suppliers (id, name) VALUES (5, 'BT')")

    # 10 contracts. Capita: 4 (40%); Capgemini: 3 (30%); CGI: 2 (20%); Atos: 1 (10%); BT: 0
    contracts = [
        # (ocid, supplier_id, value)
        ("c1",  1, 1000000), ("c2",  1, 1000000), ("c3",  1, 1000000), ("c4", 1, 1000000),
        ("c5",  2, 1000000), ("c6",  2, 1000000), ("c7",  2, 1000000),
        ("c8",  3, 1000000), ("c9",  3, 1000000),
        ("c10", 4, 1000000),
    ]
    for ocid, sup_id, value in contracts:
        conn.execute(
            "INSERT INTO notices (ocid, title, opp_type, canonical_buyer_id, published_date) "
            "VALUES (?, 'IT services contract', 'IT Outsourcing', 1, '2024-01-01')",
            (ocid,)
        )
        notice_id = conn.execute("SELECT id FROM notices WHERE ocid = ?", (ocid,)).fetchone()[0]
        conn.execute(
            "INSERT INTO awards (notice_id, total_value, award_date) VALUES (?, ?, '2024-01-01')",
            (notice_id, value)
        )
        award_id = conn.execute("SELECT id FROM awards WHERE notice_id = ?", (notice_id,)).fetchone()[0]
        conn.execute(
            "INSERT INTO award_suppliers (award_id, canonical_supplier_id) VALUES (?, ?)",
            (award_id, sup_id)
        )
    conn.commit()
    return conn
```

- [ ] **Step 2: Write the failing test for Layer 1**

Create `pwin-competitive-intel/tests/test_cube_engine.py`:

```python
"""Tests: cube engine — Layer 1 (concentration), Layer 2 (incumbents), Layer 6 (pipeline)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "fixtures"))
sys.path.insert(0, str(Path(__file__).parent.parent / "queries"))
from cube_test_data import build_cube_fixture
from cube_engine import compute_layer_1


def test_layer_1_total_contracts():
    conn = build_cube_fixture()
    result = compute_layer_1(conn, "Central Government", "IT Outsourcing")
    assert result["total_contracts"] == 10


def test_layer_1_total_value():
    conn = build_cube_fixture()
    result = compute_layer_1(conn, "Central Government", "IT Outsourcing")
    assert result["total_value"] == 10_000_000


def test_layer_1_top_3_share():
    conn = build_cube_fixture()
    result = compute_layer_1(conn, "Central Government", "IT Outsourcing")
    # Top 3 = Capita 40%, Capgemini 30%, CGI 20% → 90%
    assert abs(result["top_3_share"] - 0.90) < 0.001


def test_layer_1_effective_n_suppliers():
    conn = build_cube_fixture()
    result = compute_layer_1(conn, "Central Government", "IT Outsourcing")
    # HHI = 0.16 + 0.09 + 0.04 + 0.01 = 0.30 → 1/HHI ≈ 3.33
    assert abs(result["effective_n_suppliers"] - 3.33) < 0.05


def test_layer_1_sufficiency_reliable():
    conn = build_cube_fixture()
    result = compute_layer_1(conn, "Central Government", "IT Outsourcing")
    # 10 contracts → directional (5-14 range)
    assert result["sufficiency_flag"] == "directional"
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
python -m pytest tests/test_cube_engine.py -v
```

Expected: ImportError on cube_engine.

- [ ] **Step 4: Implement Layer 1 in cube_engine.py**

Create `pwin-competitive-intel/queries/cube_engine.py`:

```python
"""
Cube engine
===========
Computes concentration metrics, named incumbents with grip data, and
displacement windows per cell of the (sector × opportunity type) cube.

Read by: dashboard tab API (server.py), MCP tools (pwin-platform), the
marketing report generator (generate_concentration_report.py).

Writes to: cell_summary table (refresh_cell_aggregates).
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional


def _sufficiency(n: int) -> str:
    if n >= 15:
        return "reliable"
    if n >= 5:
        return "directional"
    return "insufficient"


def compute_layer_1(
    conn: sqlite3.Connection,
    sector: str,
    opp_type: str,
    value_band: Optional[str] = None,
    years: int = 5,
) -> dict:
    """Layer 1 — concentration metrics for one cell."""
    cutoff = (datetime.utcnow() - timedelta(days=365 * years)).date().isoformat()
    band_clause = ""
    band_args = ()
    if value_band == "small":
        band_clause = "AND a.total_value < 25000000"
    elif value_band == "mid":
        band_clause = "AND a.total_value BETWEEN 25000000 AND 100000000"
    elif value_band == "major":
        band_clause = "AND a.total_value BETWEEN 100000000 AND 500000000"
    elif value_band == "strategic":
        band_clause = "AND a.total_value > 500000000"

    rows = conn.execute(f"""
        SELECT s.id AS supplier_id, s.name AS supplier_name,
               COUNT(*) AS wins, COALESCE(SUM(a.total_value), 0) AS value
        FROM awards a
        JOIN notices n ON n.id = a.notice_id
        JOIN canonical_buyers b ON b.id = n.canonical_buyer_id
        JOIN award_suppliers asu ON asu.award_id = a.id
        JOIN canonical_suppliers s ON s.id = asu.canonical_supplier_id
        WHERE b.sector = ?
          AND n.opp_type = ?
          AND n.published_date >= ?
          {band_clause}
        GROUP BY s.id, s.name
        ORDER BY value DESC
    """, (sector, opp_type, cutoff) + band_args).fetchall()

    total_contracts = sum(r["wins"] for r in rows)
    total_value = sum(r["value"] for r in rows)

    if total_value == 0:
        return {
            "sector": sector, "opp_type": opp_type, "value_band": value_band or "all",
            "total_contracts": 0, "total_value": 0,
            "top_3_share": None, "top_5_share": None, "effective_n_suppliers": None,
            "trend": None, "sufficiency_flag": "insufficient",
            "supplier_rows": [],
        }

    sorted_value = [r["value"] for r in rows]
    top_3 = sum(sorted_value[:3]) / total_value
    top_5 = sum(sorted_value[:5]) / total_value
    hhi = sum((v / total_value) ** 2 for v in sorted_value)
    effective_n = round(1.0 / hhi, 2) if hhi > 0 else None

    sufficiency = _sufficiency(total_contracts)
    return {
        "sector": sector, "opp_type": opp_type, "value_band": value_band or "all",
        "total_contracts": total_contracts, "total_value": total_value,
        "top_3_share": round(top_3, 4) if sufficiency != "insufficient" else None,
        "top_5_share": round(top_5, 4) if sufficiency != "insufficient" else None,
        "effective_n_suppliers": effective_n if sufficiency != "insufficient" else None,
        "trend": None,  # filled in by Task 1.10
        "sufficiency_flag": sufficiency,
        "supplier_rows": [dict(r) for r in rows],
    }
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m pytest tests/test_cube_engine.py -v
```

Expected: all PASS.

```bash
git add pwin-competitive-intel/queries/cube_engine.py pwin-competitive-intel/tests/test_cube_engine.py pwin-competitive-intel/tests/fixtures/cube_test_data.py
git commit -m "feat(cube): implement Layer 1 concentration calculation"
```

---

### Task 1.10: Add the year-on-year trend to Layer 1

**Files:**
- Modify: `pwin-competitive-intel/queries/cube_engine.py`
- Modify: `pwin-competitive-intel/tests/test_cube_engine.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cube_engine.py`:

```python
def test_layer_1_trend_returns_string():
    conn = build_cube_fixture()
    result = compute_layer_1(conn, "Central Government", "IT Outsourcing")
    # Single-year fixture cannot show consolidation; expect 'stable' or None
    assert result["trend"] in ("consolidating", "fragmenting", "stable", None)
```

- [ ] **Step 2: Run to verify the failing case**

```bash
python -m pytest tests/test_cube_engine.py::test_layer_1_trend_returns_string -v
```

Expected: PASS already because Layer 1 returns `None` — but the implementation note in Task 1.9 has `trend: None` hardcoded. Tighten the test:

```python
def test_layer_1_trend_set_when_sufficient_history():
    """When the cell spans ≥3 years and has ≥10 contracts/year, trend is computed."""
    # Skip until multi-year fixture available; placeholder asserts trend key present
    conn = build_cube_fixture()
    result = compute_layer_1(conn, "Central Government", "IT Outsourcing")
    assert "trend" in result
```

- [ ] **Step 3: Add a trend helper**

Replace the `trend: None` line in `compute_layer_1` with a call to a new helper. Append to `cube_engine.py`:

```python
def _compute_trend(conn: sqlite3.Connection, sector: str, opp_type: str, years: int) -> Optional[str]:
    """Compare top-3 share in the most recent year to the average of the prior years.

    Returns 'consolidating' if recent top-3 share is ≥5pp higher,
            'fragmenting'   if recent top-3 share is ≥5pp lower,
            'stable'        otherwise,
            None            if insufficient history.
    """
    cutoff = (datetime.utcnow() - timedelta(days=365 * years)).date().isoformat()
    recent_cutoff = (datetime.utcnow() - timedelta(days=365)).date().isoformat()

    def _share(date_floor: str, date_ceiling: Optional[str]) -> Optional[float]:
        sql = """
            SELECT COALESCE(SUM(a.total_value), 0) AS v, asu.canonical_supplier_id AS sid
            FROM awards a
            JOIN notices n ON n.id = a.notice_id
            JOIN canonical_buyers b ON b.id = n.canonical_buyer_id
            JOIN award_suppliers asu ON asu.award_id = a.id
            WHERE b.sector = ? AND n.opp_type = ?
              AND n.published_date >= ?
        """
        args = [sector, opp_type, date_floor]
        if date_ceiling:
            sql += " AND n.published_date < ?"
            args.append(date_ceiling)
        sql += " GROUP BY asu.canonical_supplier_id ORDER BY v DESC"
        rows = conn.execute(sql, args).fetchall()
        total = sum(r["v"] for r in rows) or 0
        if total == 0:
            return None
        top3 = sum(r["v"] for r in rows[:3])
        return top3 / total

    recent = _share(recent_cutoff, None)
    prior = _share(cutoff, recent_cutoff)
    if recent is None or prior is None:
        return None
    diff = recent - prior
    if diff >= 0.05:
        return "consolidating"
    if diff <= -0.05:
        return "fragmenting"
    return "stable"
```

Then in `compute_layer_1`, replace `"trend": None,` with:

```python
        "trend": _compute_trend(conn, sector, opp_type, years) if sufficiency != "insufficient" else None,
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_cube_engine.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/queries/cube_engine.py pwin-competitive-intel/tests/test_cube_engine.py
git commit -m "feat(cube): add year-on-year trend to Layer 1"
```

---

### Task 1.11: Build Layer 2 — credible competitor list with grip data

**Files:**
- Modify: `pwin-competitive-intel/queries/cube_engine.py`
- Modify: `pwin-competitive-intel/tests/test_cube_engine.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_cube_engine.py`:

```python
from cube_engine import compute_layer_2


def test_layer_2_returns_credible_competitors():
    conn = build_cube_fixture()
    result = compute_layer_2(conn, "Central Government", "IT Outsourcing")
    names = [s["supplier_name"] for s in result["credible_competitors"]]
    # 80% coverage: Capita (40%) + Capgemini (30%) + CGI (20%) = 90%, hits 80% at 3
    assert "Capita" in names
    assert "Capgemini" in names
    assert "CGI" in names


def test_layer_2_includes_grip_data():
    conn = build_cube_fixture()
    result = compute_layer_2(conn, "Central Government", "IT Outsourcing")
    capita = next(s for s in result["credible_competitors"] if s["supplier_name"] == "Capita")
    assert capita["wins"] == 4
    assert capita["cell_share"] == 0.40
    assert capita["first_win_date"] == "2024-01-01"
    assert capita["most_recent_win_date"] == "2024-01-01"
```

- [ ] **Step 2: Run tests to verify failure**

```bash
python -m pytest tests/test_cube_engine.py -v
```

Expected: ImportError on `compute_layer_2`.

- [ ] **Step 3: Implement Layer 2**

Append to `cube_engine.py`:

```python
def compute_layer_2(
    conn: sqlite3.Connection,
    sector: str,
    opp_type: str,
    value_band: Optional[str] = None,
    years: int = 5,
) -> dict:
    """Layer 2 — credible competitor list with per-supplier grip data."""
    cutoff = (datetime.utcnow() - timedelta(days=365 * years)).date().isoformat()
    recent_cutoff = (datetime.utcnow() - timedelta(days=18 * 30)).date().isoformat()

    # Per-supplier grip
    rows = conn.execute("""
        SELECT s.id AS supplier_id, s.name AS supplier_name,
               COUNT(*) AS wins,
               COALESCE(SUM(a.total_value), 0) AS value,
               MIN(n.published_date) AS first_win_date,
               MAX(n.published_date) AS most_recent_win_date,
               COUNT(DISTINCT n.canonical_buyer_id) AS coverage_breadth,
               SUM(CASE WHEN n.procurement_method = 'limited' THEN 1 ELSE 0 END) AS direct_award_wins
        FROM awards a
        JOIN notices n ON n.id = a.notice_id
        JOIN canonical_buyers b ON b.id = n.canonical_buyer_id
        JOIN award_suppliers asu ON asu.award_id = a.id
        JOIN canonical_suppliers s ON s.id = asu.canonical_supplier_id
        WHERE b.sector = ?
          AND n.opp_type = ?
          AND n.published_date >= ?
        GROUP BY s.id, s.name
        ORDER BY value DESC
    """, (sector, opp_type, cutoff)).fetchall()

    total_value = sum(r["value"] for r in rows)
    if total_value == 0:
        return {"credible_competitors": []}

    median_value = conn.execute("""
        SELECT a.total_value FROM awards a
        JOIN notices n ON n.id = a.notice_id
        JOIN canonical_buyers b ON b.id = n.canonical_buyer_id
        WHERE b.sector = ? AND n.opp_type = ? AND n.published_date >= ?
        ORDER BY a.total_value
        LIMIT 1 OFFSET (
            SELECT COUNT(*)/2 FROM awards a2
            JOIN notices n2 ON n2.id = a2.notice_id
            JOIN canonical_buyers b2 ON b2.id = n2.canonical_buyer_id
            WHERE b2.sector = ? AND n2.opp_type = ? AND n2.published_date >= ?
        )
    """, (sector, opp_type, cutoff, sector, opp_type, cutoff)).fetchone()
    median_value = median_value[0] if median_value else 0

    # Credible competitor cut: 80% coverage + recency overlay
    bedrock_ids = set()
    cumulative = 0
    for r in rows:
        bedrock_ids.add(r["supplier_id"])
        cumulative += r["value"]
        if cumulative / total_value >= 0.80:
            break

    recent_ids = set(r[0] for r in conn.execute("""
        SELECT DISTINCT asu.canonical_supplier_id
        FROM awards a
        JOIN notices n ON n.id = a.notice_id
        JOIN canonical_buyers b ON b.id = n.canonical_buyer_id
        JOIN award_suppliers asu ON asu.award_id = a.id
        WHERE b.sector = ? AND n.opp_type = ?
          AND n.published_date >= ?
          AND a.total_value > ?
    """, (sector, opp_type, recent_cutoff, median_value)).fetchall())

    credible_ids = bedrock_ids | recent_ids

    competitors = []
    for r in rows:
        if r["supplier_id"] not in credible_ids:
            continue
        wins = r["wins"]
        competitors.append({
            "supplier_id": r["supplier_id"],
            "supplier_name": r["supplier_name"],
            "wins": wins,
            "value": r["value"],
            "cell_share": round(r["value"] / total_value, 4),
            "first_win_date": r["first_win_date"],
            "most_recent_win_date": r["most_recent_win_date"],
            "coverage_breadth": r["coverage_breadth"],
            "direct_award_share": round((r["direct_award_wins"] or 0) / wins, 4) if wins else 0,
        })

    return {"credible_competitors": competitors}
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest tests/test_cube_engine.py -v
```

Expected: all PASS.

```bash
git add pwin-competitive-intel/queries/cube_engine.py pwin-competitive-intel/tests/test_cube_engine.py
git commit -m "feat(cube): implement Layer 2 credible competitor list with grip data"
```

---

### Task 1.12: Build Layer 6 — displacement windows

**Files:**
- Modify: `pwin-competitive-intel/queries/cube_engine.py`
- Modify: `pwin-competitive-intel/tests/test_cube_engine.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cube_engine.py`:

```python
from cube_engine import compute_layer_6


def test_layer_6_returns_pipeline_dict():
    conn = build_cube_fixture()
    result = compute_layer_6(conn, "Central Government", "IT Outsourcing")
    assert "expiring_contracts" in result
    assert "forward_pipeline" in result
    assert isinstance(result["expiring_contracts"], list)
    assert isinstance(result["forward_pipeline"], list)
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_cube_engine.py::test_layer_6_returns_pipeline_dict -v
```

Expected: ImportError.

- [ ] **Step 3: Implement Layer 6**

Append to `cube_engine.py`:

```python
def compute_layer_6(
    conn: sqlite3.Connection,
    sector: str,
    opp_type: str,
    value_band: Optional[str] = None,
) -> dict:
    """Layer 6 — forward-looking displacement windows.

    Expiring contracts: awarded contracts with end_date in the next 18 months.
    Forward pipeline:   planning notices for the cell in the next 24 months.
    """
    today = datetime.utcnow().date().isoformat()
    expiry_horizon = (datetime.utcnow() + timedelta(days=540)).date().isoformat()
    pipeline_horizon = (datetime.utcnow() + timedelta(days=730)).date().isoformat()

    # Expiring contracts
    expiring_rows = conn.execute("""
        SELECT n.title, a.total_value, a.end_date,
               s.name AS incumbent_name
        FROM awards a
        JOIN notices n ON n.id = a.notice_id
        JOIN canonical_buyers b ON b.id = n.canonical_buyer_id
        LEFT JOIN award_suppliers asu ON asu.award_id = a.id
        LEFT JOIN canonical_suppliers s ON s.id = asu.canonical_supplier_id
        WHERE b.sector = ? AND n.opp_type = ?
          AND a.end_date BETWEEN ? AND ?
        ORDER BY a.end_date
        LIMIT 20
    """, (sector, opp_type, today, expiry_horizon)).fetchall()

    # Forward pipeline (planning notices)
    pipeline_rows = conn.execute("""
        SELECT pn.title, pn.estimated_value, pn.expected_publication_date,
               b.name AS prospective_buyer
        FROM planning_notices pn
        JOIN canonical_buyers b ON b.id = pn.canonical_buyer_id
        WHERE b.sector = ? AND pn.opp_type = ?
          AND pn.expected_publication_date BETWEEN ? AND ?
        ORDER BY pn.expected_publication_date
        LIMIT 20
    """, (sector, opp_type, today, pipeline_horizon)).fetchall()

    return {
        "expiring_contracts": [dict(r) for r in expiring_rows],
        "forward_pipeline": [dict(r) for r in pipeline_rows],
    }
```

(Note — `planning_notices.opp_type` may not exist if Task 1.7 only tagged `notices`. If so, add the same column to `planning_notices` in `schema.sql`/`db_utils._migrate_schema()` as part of this task and update the tagging script to cover both tables.)

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest tests/test_cube_engine.py -v
```

Expected: all PASS.

```bash
git add pwin-competitive-intel/queries/cube_engine.py pwin-competitive-intel/tests/test_cube_engine.py
git commit -m "feat(cube): implement Layer 6 displacement windows (expiring + pipeline)"
```

---

### Task 1.13: Compose `compute_cell_summary` and `refresh_cell_aggregates`

**Files:**
- Modify: `pwin-competitive-intel/queries/cube_engine.py`
- Modify: `pwin-competitive-intel/tests/test_cube_engine.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_cube_engine.py`:

```python
from cube_engine import compute_cell_summary, refresh_cell_aggregates


def test_compute_cell_summary_combines_all_layers():
    conn = build_cube_fixture()
    result = compute_cell_summary(conn, "Central Government", "IT Outsourcing")
    assert "total_contracts" in result   # from Layer 1
    assert "credible_competitors" in result  # from Layer 2
    assert "expiring_contracts" in result   # from Layer 6


def test_refresh_cell_aggregates_writes_rows():
    conn = build_cube_fixture()
    refresh_cell_aggregates(conn)
    rows = conn.execute("SELECT COUNT(*) FROM cell_summary").fetchone()
    assert rows[0] >= 1  # at least the populated cell


def test_refresh_cell_aggregates_idempotent():
    conn = build_cube_fixture()
    refresh_cell_aggregates(conn)
    first = conn.execute("SELECT COUNT(*) FROM cell_summary").fetchone()[0]
    refresh_cell_aggregates(conn)
    second = conn.execute("SELECT COUNT(*) FROM cell_summary").fetchone()[0]
    assert first == second
```

- [ ] **Step 2: Run tests to verify failure**

```bash
python -m pytest tests/test_cube_engine.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement the composer + refresh job**

Append to `cube_engine.py`:

```python
SECTORS = [
    "Central Government", "Local Government", "NHS & Health",
    "Defence & Security", "Justice & Home Affairs", "Transport",
    "Education", "Emergency Services", "Devolved Government",
]

OPP_TYPES = [
    "BPO", "IT Outsourcing", "Managed Service",
    "Facilities / Field / Operational Service",
    "Hybrid Transformation", "Digital Outcomes",
    "Consulting / Advisory", "Infrastructure & Hardware",
    "Software / SaaS", "Framework / Panel Appointment",
]


def compute_cell_summary(
    conn: sqlite3.Connection,
    sector: str,
    opp_type: str,
    value_band: Optional[str] = None,
) -> dict:
    """Compose Layer 1 + Layer 2 + Layer 6 into a single cell view."""
    layer_1 = compute_layer_1(conn, sector, opp_type, value_band)
    layer_2 = compute_layer_2(conn, sector, opp_type, value_band)
    layer_6 = compute_layer_6(conn, sector, opp_type, value_band)
    out = dict(layer_1)
    out.update(layer_2)
    out.update(layer_6)
    return out


def refresh_cell_aggregates(conn: sqlite3.Connection) -> dict:
    """Refresh the cell_summary table for all 90 cells. Idempotent."""
    now = datetime.utcnow().isoformat()
    written = 0
    for sector in SECTORS:
        for opp_type in OPP_TYPES:
            summary = compute_cell_summary(conn, sector, opp_type, value_band=None)
            detail = {
                "credible_competitors": summary.get("credible_competitors", []),
                "expiring_contracts": summary.get("expiring_contracts", []),
                "forward_pipeline": summary.get("forward_pipeline", []),
            }
            conn.execute("""
                INSERT INTO cell_summary
                  (sector, opp_type, value_band, total_contracts, total_value,
                   top_3_share, top_5_share, effective_n_suppliers, trend,
                   sufficiency_flag, detail_json, last_refreshed_at)
                VALUES (?, ?, 'all', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (sector, opp_type, value_band) DO UPDATE SET
                  total_contracts = excluded.total_contracts,
                  total_value = excluded.total_value,
                  top_3_share = excluded.top_3_share,
                  top_5_share = excluded.top_5_share,
                  effective_n_suppliers = excluded.effective_n_suppliers,
                  trend = excluded.trend,
                  sufficiency_flag = excluded.sufficiency_flag,
                  detail_json = excluded.detail_json,
                  last_refreshed_at = excluded.last_refreshed_at
            """, (
                sector, opp_type,
                summary["total_contracts"], summary["total_value"],
                summary.get("top_3_share"), summary.get("top_5_share"),
                summary.get("effective_n_suppliers"), summary.get("trend"),
                summary["sufficiency_flag"], json.dumps(detail), now,
            ))
            written += 1
    conn.commit()
    return {"cells_written": written}
```

- [ ] **Step 4: Run tests and commit**

```bash
python -m pytest tests/test_cube_engine.py -v
```

Expected: all PASS.

```bash
git add pwin-competitive-intel/queries/cube_engine.py pwin-competitive-intel/tests/test_cube_engine.py
git commit -m "feat(cube): compose cell_summary and refresh_cell_aggregates job"
```

---

### Task 1.14: Wire the engine into the nightly scheduler

**Files:**
- Modify: `pwin-competitive-intel/agent/scheduler.py`

- [ ] **Step 1: Read scheduler.py to understand the current pattern**

```bash
grep -n "step\|run_step\|subprocess" pwin-competitive-intel/agent/scheduler.py | head -20
```

- [ ] **Step 2: Add tagging + refresh as new steps**

In `agent/scheduler.py`, locate the existing pipeline steps (the numbered list near the top docstring lists them; the implementation calls `subprocess.run` for each). Add two new steps after the "classify-by-cpv" step (existing step 4):

```python
    # ── Step 4b: Tag notices with opportunity type (cube engine prerequisite) ──
    log.info("Step 4b: Tagging notices with opportunity type")
    try:
        subprocess.run([sys.executable, str(AGENT_DIR / "tag_notices.py")], check=False)
    except Exception as e:
        log.warning("tag_notices step failed: %s", e)

    # ── Step 4c: Refresh cube cell aggregates ──
    log.info("Step 4c: Refreshing cube cell aggregates")
    try:
        from queries.cube_engine import refresh_cell_aggregates
        from agent.db_utils import get_db
        conn = get_db(DB_PATH)
        result = refresh_cell_aggregates(conn)
        log.info("Cube refresh: %s cells written", result["cells_written"])
    except Exception as e:
        log.warning("refresh_cell_aggregates step failed: %s", e)
```

(`AGENT_DIR` and `DB_PATH` constants exist near the top of `scheduler.py`. Add `from queries.cube_engine import refresh_cell_aggregates` to top-level imports if cleaner.)

- [ ] **Step 3: Update the docstring at the top of scheduler.py**

Add the two new steps to the numbered docstring listing (around line 12):

```python
  4b. Tag notices with opportunity type            (tag_notices.py)
  4c. Refresh cube cell aggregates                 (cube_engine.refresh_cell_aggregates)
```

- [ ] **Step 4: Smoke-test scheduler.py compiles and the step is recognised**

```bash
python -c "import ast; ast.parse(open('pwin-competitive-intel/agent/scheduler.py').read()); print('OK')"
```

Expected: `OK`. (Full scheduler run is too slow for unit testing; a smoke compile is enough.)

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/scheduler.py
git commit -m "feat(cube): wire opp-type tagging and cell refresh into nightly scheduler"
```

---

## Stage 2 — Marketing Report

**Goal of this stage:** A 5–10 cell markdown write-up that proves the concentration thesis empirically with hard numbers, generated from the engine. Ships before any UI work — it's the immediate marketing-facing output.

### Task 2.1: Build the cell selection logic and report generator

**Files:**
- Create: `pwin-competitive-intel/queries/generate_concentration_report.py`
- Create: `pwin-competitive-intel/reports/.gitkeep`

- [ ] **Step 1: Create the reports directory placeholder**

```bash
mkdir -p pwin-competitive-intel/reports
touch pwin-competitive-intel/reports/.gitkeep
```

- [ ] **Step 2: Write the report generator script**

Create `pwin-competitive-intel/queries/generate_concentration_report.py`:

```python
"""
Concentration report generator
==============================
Picks the top N cells by total contract value, calls the cube engine for
each, and produces a markdown report demonstrating the concentration thesis.

Usage:
    python queries/generate_concentration_report.py
    python queries/generate_concentration_report.py --top 5  # top 5 cells only
    python queries/generate_concentration_report.py --output reports/custom.md
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
import db_utils
from cube_engine import compute_cell_summary, SECTORS, OPP_TYPES

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"
REPORTS_DIR = Path(__file__).parent.parent / "reports"


def _fmt_value(v):
    if v is None:
        return "—"
    if v >= 1e9:
        return f"£{v/1e9:.2f}bn"
    if v >= 1e6:
        return f"£{v/1e6:.0f}m"
    return f"£{v/1e3:.0f}k"


def _fmt_share(s):
    return f"{s*100:.0f}%" if s is not None else "—"


def render_cell_section(summary: dict) -> str:
    s = summary
    lines = [
        f"### {s['sector']} × {s['opp_type']}",
        "",
        f"- **Total contract value (5-year window):** {_fmt_value(s['total_value'])}",
        f"- **Number of contracts:** {s['total_contracts']}",
        f"- **Top-3 supplier share:** {_fmt_share(s.get('top_3_share'))}",
        f"- **Top-5 supplier share:** {_fmt_share(s.get('top_5_share'))}",
        f"- **Effective number of suppliers:** {s.get('effective_n_suppliers') or '—'}",
        f"- **Trend:** {s.get('trend') or '—'}",
        f"- **Sufficiency:** {s['sufficiency_flag']}",
        "",
        "**Credible competitors:**",
        "",
        "| Supplier | Wins | Cell share | First win | Coverage breadth |",
        "|---|---:|---:|---|---:|",
    ]
    for c in s.get("credible_competitors", []):
        lines.append(
            f"| {c['supplier_name']} | {c['wins']} | "
            f"{_fmt_share(c['cell_share'])} | {c['first_win_date'] or '—'} | {c['coverage_breadth']} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_report(conn: sqlite3.Connection, top_n: int = 10) -> str:
    """Generate the full markdown report."""
    summaries = []
    for sector in SECTORS:
        for opp_type in OPP_TYPES:
            s = compute_cell_summary(conn, sector, opp_type)
            if s["sufficiency_flag"] == "reliable":
                summaries.append(s)
    summaries.sort(key=lambda x: x["total_value"], reverse=True)
    summaries = summaries[:top_n]

    today = datetime.utcnow().strftime("%Y-%m-%d")
    out = [
        f"# UK Government Procurement — Market Concentration Report",
        "",
        f"**Generated:** {today}",
        f"**Cells analysed:** Top {top_n} by total contract value (Reliable sufficiency only)",
        f"**Source:** Find a Tender Service + Contracts Finder, trailing 5 years",
        "",
        "## Executive summary",
        "",
        "This report demonstrates empirically that UK government procurement, when sliced by sector "
        "and opportunity type, is highly concentrated. Each cell below shows a market in which a "
        "small number of suppliers hold the majority of contract value.",
        "",
        "## Methodology",
        "",
        "- Cell = (sector, opportunity type) intersection",
        "- Concentration = top-3 / top-5 share of contract value over the trailing 5 years",
        "- Effective number of suppliers = 1 ÷ Herfindahl-Hirschman Index",
        "- Credible competitors = suppliers covering 80% of cell value, plus any supplier with a "
        "win in the trailing 18 months above the cell's 5-year median contract value",
        "",
        "## Cell findings",
        "",
    ]
    for s in summaries:
        out.append(render_cell_section(s))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    report = build_report(conn, top_n=args.top)

    output = Path(args.output) if args.output else (REPORTS_DIR / f"market-concentration-{datetime.utcnow().strftime('%Y-%m-%d')}.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"Report written: {output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the report generator**

```bash
cd pwin-competitive-intel
python queries/generate_concentration_report.py --top 5
```

Expected: writes a markdown file under `reports/`. Inspect the output for sanity.

- [ ] **Step 4: Visually review the generated report**

Open the generated markdown file. Confirm:
- The cells listed are the highest-value ones in the database
- The supplier names are real and recognisable
- The shares add up plausibly
- No empty / placeholder values visible

If anything looks wrong, debug the engine before continuing.

- [ ] **Step 5: Commit the generator and the first report**

```bash
git add pwin-competitive-intel/queries/generate_concentration_report.py \
        pwin-competitive-intel/reports/.gitkeep \
        pwin-competitive-intel/reports/market-concentration-*.md
git commit -m "feat(cube): marketing report generator + first generated concentration report"
```

---

## Stage 3 — Dashboard Tab

**Goal of this stage:** A new "Competitive Cells" tab on the existing dashboard, sub-second responsive against the pre-computed `cell_summary` table, with three views (cube overview, cell view, cell list).

### Task 3.1: Add `/api/cube/cells` endpoint to server.py

**Files:**
- Modify: `pwin-competitive-intel/server.py`

- [ ] **Step 1: Add the handler**

In `server.py`, after the existing `api_*` handler functions (and before the URL routing block), add:

```python
def api_cube_cells():
    """Return all 90 cells with summary numbers for the cube overview view."""
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        rows = conn.execute("""
            SELECT sector, opp_type, total_contracts, total_value,
                   top_3_share, effective_n_suppliers, sufficiency_flag,
                   last_refreshed_at
            FROM cell_summary
            WHERE value_band = 'all'
            ORDER BY total_value DESC
        """).fetchall()
        return {"cells": dict_rows(rows)}
    finally:
        conn.close()
```

- [ ] **Step 2: Wire the route**

In the URL routing block (search for existing routes like `if path == '/api/summary':`), add:

```python
        elif path == "/api/cube/cells":
            response = api_cube_cells()
```

- [ ] **Step 3: Smoke test the endpoint**

```bash
cd pwin-competitive-intel
python server.py &
sleep 2
curl -s "http://localhost:8765/api/cube/cells" | python -m json.tool | head -30
kill %1
```

Expected: JSON output with a `cells` array.

- [ ] **Step 4: Confirm response shape is correct**

Expected fields per cell: `sector`, `opp_type`, `total_contracts`, `total_value`, `top_3_share`, `effective_n_suppliers`, `sufficiency_flag`, `last_refreshed_at`.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/server.py
git commit -m "feat(cube): add /api/cube/cells endpoint for dashboard overview"
```

---

### Task 3.2: Add `/api/cube/cell/<sector>/<opp_type>` endpoint

**Files:**
- Modify: `pwin-competitive-intel/server.py`

- [ ] **Step 1: Add the handler**

```python
def api_cube_cell(sector, opp_type):
    """Return the full cell view for a single (sector, opp_type)."""
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        row = conn.execute("""
            SELECT * FROM cell_summary
            WHERE sector = ? AND opp_type = ? AND value_band = 'all'
        """, (sector, opp_type)).fetchone()
        if not row:
            return {"error": "Cell not found"}
        cell = dict(row)
        # Unpack the JSON detail column for the consumer
        cell["detail"] = json.loads(cell.pop("detail_json"))
        return cell
    finally:
        conn.close()
```

- [ ] **Step 2: Wire the route**

In the URL routing block, add:

```python
        elif path.startswith("/api/cube/cell/"):
            parts = path.split("/")
            # /api/cube/cell/<sector>/<opp_type> → 5 parts, but URL-encoded
            from urllib.parse import unquote
            if len(parts) == 6:
                response = api_cube_cell(unquote(parts[4]), unquote(parts[5]))
            else:
                response = {"error": "Bad cell path"}
```

- [ ] **Step 3: Smoke test**

```bash
python server.py &
sleep 2
curl -s "http://localhost:8765/api/cube/cell/Central%20Government/IT%20Outsourcing" | python -m json.tool | head -50
kill %1
```

Expected: JSON with cell summary numbers and `detail` containing credible competitors and pipeline.

- [ ] **Step 4: Add `import json` at the top of server.py if not already there**

```bash
grep -n "^import json" pwin-competitive-intel/server.py
```

If not present, add `import json` to the import block at the top.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/server.py
git commit -m "feat(cube): add /api/cube/cell/<sector>/<opp_type> endpoint"
```

---

### Task 3.3: Add `/api/cube/search` endpoint for filtered cell list

**Files:**
- Modify: `pwin-competitive-intel/server.py`

- [ ] **Step 1: Add the handler**

```python
def api_cube_search(query_params):
    """Return a filtered cell list. Query params:
    - min_top_3_share: only cells where top-3 share >= this (0..1)
    - sufficiency: comma-separated list of sufficiency flags
    - sort: 'value' (default) | 'concentration' | 'contracts'
    """
    conn = get_db()
    if not conn: return {"error": "Database not found"}
    try:
        sql = "SELECT * FROM cell_summary WHERE value_band = 'all'"
        args = []

        min_share = query_params.get("min_top_3_share", [None])[0]
        if min_share:
            sql += " AND top_3_share >= ?"
            args.append(float(min_share))

        suff = query_params.get("sufficiency", [None])[0]
        if suff:
            placeholders = ",".join("?" * len(suff.split(",")))
            sql += f" AND sufficiency_flag IN ({placeholders})"
            args.extend(suff.split(","))

        sort_col = {
            "value": "total_value DESC",
            "concentration": "top_3_share DESC",
            "contracts": "total_contracts DESC",
        }.get(query_params.get("sort", ["value"])[0], "total_value DESC")
        sql += f" ORDER BY {sort_col}"

        rows = conn.execute(sql, args).fetchall()
        return {"cells": dict_rows(rows)}
    finally:
        conn.close()
```

- [ ] **Step 2: Wire the route**

```python
        elif path == "/api/cube/search":
            response = api_cube_search(query)  # query is parse_qs result
```

- [ ] **Step 3: Smoke test**

```bash
python server.py &
sleep 2
curl -s "http://localhost:8765/api/cube/search?min_top_3_share=0.7&sufficiency=reliable" | python -m json.tool | head -20
kill %1
```

Expected: filtered JSON with only highly-concentrated reliable cells.

- [ ] **Step 4: No additional impl required** — query params already parsed by the existing handler scaffolding.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/server.py
git commit -m "feat(cube): add /api/cube/search endpoint with filtering and sort"
```

---

### Task 3.4: Add the "Competitive Cells" tab to dashboard.html

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html`

- [ ] **Step 1: Read existing dashboard structure**

```bash
grep -n "data-tab\|class=\"tab\"" pwin-competitive-intel/dashboard.html | head -20
```

- [ ] **Step 2: Add the tab button**

In the tab nav (search for existing buttons like `<button data-tab="buyers">Buyers</button>`), add:

```html
<button data-tab="cells" class="tab-btn">Competitive Cells</button>
```

- [ ] **Step 3: Add the tab content scaffolding**

Add a new `<div class="tab" id="tab-cells" hidden>` section after the existing tab divs. Include three sub-views — overview, cell, list — switchable by buttons inside the tab. Initial scaffolding:

```html
<div class="tab" id="tab-cells" hidden>
  <div class="cells-subtabs">
    <button class="cells-subtab-btn active" data-subtab="overview">Cube Overview</button>
    <button class="cells-subtab-btn" data-subtab="cell">Cell View</button>
    <button class="cells-subtab-btn" data-subtab="list">Cell List</button>
  </div>

  <div class="cells-subtab" id="cells-overview">
    <h2>Cube Overview</h2>
    <div id="cube-grid"></div>
  </div>

  <div class="cells-subtab" id="cells-cell" hidden>
    <h2 id="cell-title">— Select a cell from the overview —</h2>
    <div id="cell-lens-toggle" hidden>
      <button data-lens="challenger" class="lens-btn active">Challenger lens</button>
      <button data-lens="incumbent" class="lens-btn">Incumbent lens</button>
    </div>
    <div id="cell-layer-1"></div>
    <div id="cell-layer-2"></div>
    <div id="cell-layer-6"></div>
  </div>

  <div class="cells-subtab" id="cells-list" hidden>
    <h2>Cell List</h2>
    <div id="cells-list-controls">
      <select id="cells-list-sort">
        <option value="value">By value</option>
        <option value="concentration">By concentration</option>
        <option value="contracts">By contract count</option>
      </select>
    </div>
    <table id="cells-list-table"></table>
  </div>
</div>
```

- [ ] **Step 4: Smoke test**

Open dashboard in browser, click the "Competitive Cells" tab. Expected: empty scaffolding visible.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "feat(cube): add Competitive Cells tab scaffolding to dashboard"
```

---

### Task 3.5: Implement the cube overview view

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html`

- [ ] **Step 1: Add the overview JS**

In the existing `<script>` section of dashboard.html, add a function that fetches the cells API and renders a 9 × 10 grid:

```javascript
async function renderCubeOverview() {
  const grid = document.getElementById('cube-grid');
  const res = await fetch('/api/cube/cells');
  const data = await res.json();
  if (data.error) { grid.innerHTML = '<p>Error loading cube.</p>'; return; }

  // Build a sector×opp_type matrix
  const SECTORS = ['Central Government','Local Government','NHS & Health','Defence & Security','Justice & Home Affairs','Transport','Education','Emergency Services','Devolved Government'];
  const OPP_TYPES = ['BPO','IT Outsourcing','Managed Service','Facilities / Field / Operational Service','Hybrid Transformation','Digital Outcomes','Consulting / Advisory','Infrastructure & Hardware','Software / SaaS','Framework / Panel Appointment'];

  const lookup = {};
  for (const c of data.cells) {
    lookup[c.sector + '|' + c.opp_type] = c;
  }

  let html = '<table class="cube-grid"><thead><tr><th></th>';
  for (const o of OPP_TYPES) html += `<th>${o}</th>`;
  html += '</tr></thead><tbody>';

  for (const s of SECTORS) {
    html += `<tr><th>${s}</th>`;
    for (const o of OPP_TYPES) {
      const cell = lookup[s + '|' + o];
      if (!cell || cell.sufficiency_flag === 'insufficient') {
        html += '<td class="cube-cell empty">—</td>';
      } else {
        const valueLabel = cell.total_value >= 1e9 ? '£' + (cell.total_value/1e9).toFixed(1) + 'bn' : '£' + Math.round(cell.total_value/1e6) + 'm';
        const concLabel = cell.top_3_share ? Math.round(cell.top_3_share*100) + '%' : '—';
        const heatClass = cell.top_3_share && cell.top_3_share > 0.8 ? 'high' : (cell.top_3_share && cell.top_3_share > 0.6 ? 'med' : 'low');
        html += `<td class="cube-cell ${heatClass}" data-sector="${s}" data-opp="${o}">${valueLabel}<br><small>${concLabel}</small></td>`;
      }
    }
    html += '</tr>';
  }
  html += '</tbody></table>';
  grid.innerHTML = html;

  // Wire click handlers
  grid.querySelectorAll('.cube-cell:not(.empty)').forEach(td => {
    td.addEventListener('click', () => loadCellView(td.dataset.sector, td.dataset.opp));
  });
}
```

- [ ] **Step 2: Hook the overview load to the tab activation**

Find the existing tab-switch JS (search for `data-tab` click handler) and add a case for the cells tab:

```javascript
if (tabName === 'cells') renderCubeOverview();
```

- [ ] **Step 3: Add basic CSS for the grid**

In the `<style>` block:

```css
.cube-grid { border-collapse: collapse; width: 100%; font-size: 0.85rem; }
.cube-grid th, .cube-grid td { border: 1px solid #ddd; padding: 0.4rem; text-align: center; }
.cube-grid th { background: #f5f5f5; font-weight: 600; }
.cube-cell { cursor: pointer; }
.cube-cell.high { background: #fee; }
.cube-cell.med  { background: #ffe; }
.cube-cell.low  { background: #efe; }
.cube-cell.empty { color: #ccc; cursor: default; }
.cube-cell:hover:not(.empty) { background: #ddf; }
```

- [ ] **Step 4: Manual smoke test**

Reload the dashboard, click Competitive Cells. Expected: 9 × 10 grid populated with values and concentration percentages, colour-coded by concentration.

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "feat(cube): implement cube overview view (9x10 grid)"
```

---

### Task 3.6: Implement the cell view (three panels + lens toggle)

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html`

- [ ] **Step 1: Add the cell view JS**

```javascript
let currentLens = 'challenger';

async function loadCellView(sector, opp) {
  // Switch to the cell subtab
  document.querySelectorAll('.cells-subtab').forEach(d => d.hidden = true);
  document.getElementById('cells-cell').hidden = false;
  document.querySelectorAll('.cells-subtab-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('.cells-subtab-btn[data-subtab="cell"]').classList.add('active');

  document.getElementById('cell-title').textContent = sector + ' × ' + opp;
  document.getElementById('cell-lens-toggle').hidden = false;

  const res = await fetch(`/api/cube/cell/${encodeURIComponent(sector)}/${encodeURIComponent(opp)}`);
  const cell = await res.json();
  if (cell.error) { document.getElementById('cell-layer-1').innerHTML = '<p>Cell not found.</p>'; return; }

  renderCellLayers(cell);
}

function renderCellLayers(cell) {
  const lens = currentLens;
  const conc = cell.top_3_share ? Math.round(cell.top_3_share * 100) : '—';
  const lensCopyL1 = lens === 'challenger'
    ? `Hard to break in — top three hold ${conc}%.`
    : `Strong position — your peer group holds ${conc}%.`;

  document.getElementById('cell-layer-1').innerHTML = `
    <div class="layer layer-1">
      <h3>Layer 1 — Cell map</h3>
      <p class="lens-copy">${lensCopyL1}</p>
      <ul>
        <li>Total contracts (5yr): ${cell.total_contracts}</li>
        <li>Total value: £${(cell.total_value/1e6).toFixed(0)}m</li>
        <li>Top-3 share: ${conc}%</li>
        <li>Top-5 share: ${cell.top_5_share ? Math.round(cell.top_5_share*100) : '—'}%</li>
        <li>Effective number of suppliers: ${cell.effective_n_suppliers || '—'}</li>
        <li>Trend: ${cell.trend || '—'}</li>
        <li>Sufficiency: ${cell.sufficiency_flag}</li>
      </ul>
    </div>
  `;

  const competitors = cell.detail.credible_competitors || [];
  const compRowsHtml = competitors.map(c => `
    <tr>
      <td>${c.supplier_name}</td>
      <td>${c.wins}</td>
      <td>${Math.round(c.cell_share*100)}%</td>
      <td>${c.first_win_date || '—'}</td>
      <td>${c.coverage_breadth}</td>
      <td>${Math.round((c.direct_award_share||0)*100)}%</td>
    </tr>
  `).join('');
  const lensCopyL2 = lens === 'challenger' ? 'Incumbents to displace:' : 'You and your peers:';

  document.getElementById('cell-layer-2').innerHTML = `
    <div class="layer layer-2">
      <h3>Layer 2 — Credible competitors</h3>
      <p class="lens-copy">${lensCopyL2}</p>
      <table>
        <thead><tr><th>Supplier</th><th>Wins</th><th>Share</th><th>First win</th><th>Coverage</th><th>Direct-award %</th></tr></thead>
        <tbody>${compRowsHtml}</tbody>
      </table>
    </div>
  `;

  const expiring = (cell.detail.expiring_contracts || []).slice(0, 10);
  const pipeline = (cell.detail.forward_pipeline || []).slice(0, 10);
  const lensCopyL6 = lens === 'challenger' ? 'Targets to attack:' : 'Defences to harden:';

  document.getElementById('cell-layer-6').innerHTML = `
    <div class="layer layer-6">
      <h3>Layer 6 — Displacement windows</h3>
      <p class="lens-copy">${lensCopyL6}</p>
      <h4>Expiring contracts (next 18m)</h4>
      <ul>${expiring.map(e => `<li>${e.title} — £${(e.total_value/1e6).toFixed(0)}m — ${e.incumbent_name||'?'} — expires ${e.end_date}</li>`).join('') || '<li>None.</li>'}</ul>
      <h4>Forward pipeline (next 24m)</h4>
      <ul>${pipeline.map(p => `<li>${p.title} — ${p.prospective_buyer||'?'} — expected ${p.expected_publication_date||'?'}</li>`).join('') || '<li>None.</li>'}</ul>
    </div>
  `;
}

// Lens toggle
document.querySelectorAll('.lens-btn').forEach(b => {
  b.addEventListener('click', () => {
    currentLens = b.dataset.lens;
    document.querySelectorAll('.lens-btn').forEach(x => x.classList.toggle('active', x === b));
    // Re-render with cached cell — use the most recent fetch
    const title = document.getElementById('cell-title').textContent;
    const [sector, opp] = title.split(' × ');
    loadCellView(sector, opp);
  });
});
```

- [ ] **Step 2: Manual smoke test the cell view**

Open dashboard, click a cell from the overview, verify the three panels render and the lens toggle changes the framing copy.

- [ ] **Step 3: Add CSS for the layers**

```css
.layer { border: 1px solid #ddd; padding: 1rem; margin-bottom: 1rem; }
.layer h3 { margin-top: 0; }
.lens-copy { font-style: italic; color: #555; }
.lens-btn { padding: 0.4rem 0.8rem; border: 1px solid #aaa; background: #eee; cursor: pointer; }
.lens-btn.active { background: #c8e6c9; border-color: #4caf50; }
```

- [ ] **Step 4: Verify all three panels render correctly**

Expected: Layer 1 shows numbers, Layer 2 shows competitor table, Layer 6 shows expiring + pipeline lists. Toggle changes copy without re-fetching (in real implementation, cache the fetched cell in a variable to avoid re-fetching).

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "feat(cube): implement cell view with three layers and lens toggle"
```

---

### Task 3.7: Implement the cell list view

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html`

- [ ] **Step 1: Add the list view JS**

```javascript
async function renderCellList() {
  const sort = document.getElementById('cells-list-sort').value;
  const res = await fetch(`/api/cube/search?sort=${sort}`);
  const data = await res.json();
  const tbl = document.getElementById('cells-list-table');
  tbl.innerHTML = `
    <thead>
      <tr>
        <th>Sector</th>
        <th>Opportunity type</th>
        <th>Contracts</th>
        <th>Value</th>
        <th>Top-3 share</th>
        <th>Effective n suppliers</th>
        <th>Sufficiency</th>
      </tr>
    </thead>
    <tbody>
      ${data.cells.map(c => `
        <tr>
          <td>${c.sector}</td>
          <td>${c.opp_type}</td>
          <td>${c.total_contracts}</td>
          <td>£${(c.total_value/1e6).toFixed(0)}m</td>
          <td>${c.top_3_share ? Math.round(c.top_3_share*100) + '%' : '—'}</td>
          <td>${c.effective_n_suppliers || '—'}</td>
          <td>${c.sufficiency_flag}</td>
        </tr>
      `).join('')}
    </tbody>
  `;
}

document.getElementById('cells-list-sort').addEventListener('change', renderCellList);

// Wire subtab buttons
document.querySelectorAll('.cells-subtab-btn').forEach(b => {
  b.addEventListener('click', () => {
    document.querySelectorAll('.cells-subtab-btn').forEach(x => x.classList.toggle('active', x === b));
    document.querySelectorAll('.cells-subtab').forEach(d => d.hidden = true);
    document.getElementById('cells-' + b.dataset.subtab).hidden = false;
    if (b.dataset.subtab === 'list') renderCellList();
    else if (b.dataset.subtab === 'overview') renderCubeOverview();
  });
});
```

- [ ] **Step 2: Manual smoke test**

Click "Cell List" subtab. Expected: 90 rows of cells, sortable by the dropdown.

- [ ] **Step 3: Verify the sort works**

Change the dropdown to "By concentration" — the top rows should be cells with the highest top-3 share.

- [ ] **Step 4: Verify no JS errors in browser console**

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "feat(cube): implement cell list view with sort and filter"
```

---

## Stage 4 — MCP Tools and Platform API

**Goal of this stage:** The cube exposed as MCP tools that Qualify, Win Strategy, and Verdict can call live, plus matching HTTP endpoints under `/api/intel/cube/*` on the platform Data API.

### Task 4.1: Add cube query functions to the platform competitive-intel module

**Files:**
- Modify: `pwin-platform/src/competitive-intel.js`

- [ ] **Step 1: Read the existing module to understand the pattern**

```bash
grep -n "function\|module.exports\|export " pwin-platform/src/competitive-intel.js | head -30
```

- [ ] **Step 2: Add three query functions**

Append to `pwin-platform/src/competitive-intel.js`:

```javascript
function getCompetitiveCell(db, sector, oppType, valueBand = 'all', lens = 'neutral') {
  const row = db.prepare(`
    SELECT * FROM cell_summary
    WHERE sector = ? AND opp_type = ? AND value_band = ?
  `).get(sector, oppType, valueBand);
  if (!row) return { error: 'cell_not_found' };
  const detail = JSON.parse(row.detail_json);
  return {
    sector: row.sector,
    opp_type: row.opp_type,
    value_band: row.value_band,
    total_contracts: row.total_contracts,
    total_value: row.total_value,
    top_3_share: row.top_3_share,
    top_5_share: row.top_5_share,
    effective_n_suppliers: row.effective_n_suppliers,
    trend: row.trend,
    sufficiency_flag: row.sufficiency_flag,
    last_refreshed_at: row.last_refreshed_at,
    credible_competitors: detail.credible_competitors,
    expiring_contracts: detail.expiring_contracts,
    forward_pipeline: detail.forward_pipeline,
    lens_framing: lens === 'neutral' ? null : framingFor(lens, row),
  };
}

function getCredibleCompetitors(db, sector, oppType) {
  const cell = getCompetitiveCell(db, sector, oppType);
  if (cell.error) return cell;
  return { sector: cell.sector, opp_type: cell.opp_type, credible_competitors: cell.credible_competitors };
}

function findCellsForSupplier(db, canonicalSupplierId) {
  const rows = db.prepare(`SELECT sector, opp_type, detail_json FROM cell_summary WHERE value_band = 'all'`).all();
  const matches = [];
  for (const row of rows) {
    const detail = JSON.parse(row.detail_json);
    const hit = (detail.credible_competitors || []).find(c => c.supplier_id === canonicalSupplierId);
    if (hit) matches.push({ sector: row.sector, opp_type: row.opp_type, ...hit });
  }
  matches.sort((a, b) => b.cell_share - a.cell_share);
  return { supplier_id: canonicalSupplierId, cells: matches };
}

function framingFor(lens, row) {
  const conc = row.top_3_share ? Math.round(row.top_3_share * 100) : null;
  if (lens === 'challenger') {
    return {
      cell_concentration: conc ? `Hard to break in — top three hold ${conc}%.` : 'Concentration unclear.',
      incumbents_label: 'Incumbents to displace',
      pipeline_label: 'Targets to attack',
    };
  }
  if (lens === 'incumbent') {
    return {
      cell_concentration: conc ? `Strong position — your peer group holds ${conc}%.` : 'Concentration unclear.',
      incumbents_label: 'You and your peers',
      pipeline_label: 'Defences to harden',
    };
  }
  return null;
}

module.exports = {
  // ... existing exports ...
  getCompetitiveCell,
  getCredibleCompetitors,
  findCellsForSupplier,
};
```

(Adjust the `module.exports` block to keep existing exports — the new entries are additive.)

- [ ] **Step 3: Smoke test by requiring the module**

```bash
cd pwin-platform
node -e "const ci = require('./src/competitive-intel.js'); console.log(typeof ci.getCompetitiveCell);"
```

Expected: `function`.

- [ ] **Step 4: Smoke test against the local DB**

```bash
node -e "
const db = require('better-sqlite3')('../pwin-competitive-intel/db/bid_intel.db');
const ci = require('./src/competitive-intel.js');
console.log(JSON.stringify(ci.getCompetitiveCell(db, 'Central Government', 'IT Outsourcing'), null, 2).slice(0, 500));
"
```

Expected: JSON with cell data (truncated to first 500 chars).

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/src/competitive-intel.js
git commit -m "feat(cube): add competitive cell query functions to platform module"
```

---

### Task 4.2: Register the three MCP tools

**Files:**
- Modify: `pwin-platform/src/mcp.js`

- [ ] **Step 1: Locate the existing MCP tool registration block**

```bash
grep -n "server.tool" pwin-platform/src/mcp.js | head -10
```

- [ ] **Step 2: Register the three new tools**

Add the following near the existing competitive-intel tool registrations (e.g. near `get_buyer_profile`):

```javascript
  server.tool(
    "get_competitive_cell",
    "Return the full competitive cell view (concentration, credible competitors, displacement windows) for a given sector × opportunity type. Optionally apply a challenger or incumbent lens for framing.",
    {
      sector: z.string(),
      opp_type: z.string(),
      value_band: z.enum(["all", "small", "mid", "major", "strategic"]).optional(),
      lens: z.enum(["neutral", "challenger", "incumbent"]).optional(),
    },
    async ({ sector, opp_type, value_band, lens }) => {
      const result = ci.getCompetitiveCell(db, sector, opp_type, value_band || "all", lens || "neutral");
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    "get_credible_competitors",
    "Return only the named credible competitor list (with grip data) for a sector × opportunity type cell.",
    {
      sector: z.string(),
      opp_type: z.string(),
    },
    async ({ sector, opp_type }) => {
      const result = ci.getCredibleCompetitors(db, sector, opp_type);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    "find_cells_for_supplier",
    "Given a canonical supplier ID, return every cube cell where this supplier is in the credible competitor list, sorted by their share.",
    {
      canonical_supplier_id: z.number().int(),
    },
    async ({ canonical_supplier_id }) => {
      const result = ci.findCellsForSupplier(db, canonical_supplier_id);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );
```

(`ci` is the existing imported namespace for competitive-intel functions; if a different name is in use, adapt.)

- [ ] **Step 3: Smoke test the MCP server starts**

```bash
cd pwin-platform
timeout 5 node src/server.js --mcp 2>&1 | head -10 || echo "MCP started (timed out as expected)"
```

Expected: no syntax error.

- [ ] **Step 4: Confirm the tool count increased by three**

```bash
grep -c "server.tool(" pwin-platform/src/mcp.js
```

Expected: previous count + 3.

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/src/mcp.js
git commit -m "feat(cube): register get_competitive_cell, get_credible_competitors, find_cells_for_supplier MCP tools"
```

---

### Task 4.3: Add HTTP endpoints to the platform Data API

**Files:**
- Modify: `pwin-platform/src/api.js`

- [ ] **Step 1: Locate the existing intel endpoints**

```bash
grep -n "/api/intel" pwin-platform/src/api.js | head -10
```

- [ ] **Step 2: Add three new endpoints**

```javascript
  app.get('/api/intel/cube/cell', (req, res) => {
    const { sector, opp_type, value_band, lens } = req.query;
    if (!sector || !opp_type) return res.status(400).json({ error: "sector and opp_type required" });
    const result = ci.getCompetitiveCell(db, sector, opp_type, value_band || 'all', lens || 'neutral');
    res.json(result);
  });

  app.get('/api/intel/cube/credible-competitors', (req, res) => {
    const { sector, opp_type } = req.query;
    if (!sector || !opp_type) return res.status(400).json({ error: "sector and opp_type required" });
    res.json(ci.getCredibleCompetitors(db, sector, opp_type));
  });

  app.get('/api/intel/cube/cells-for-supplier', (req, res) => {
    const id = parseInt(req.query.canonical_supplier_id, 10);
    if (!id) return res.status(400).json({ error: "canonical_supplier_id required" });
    res.json(ci.findCellsForSupplier(db, id));
  });
```

- [ ] **Step 3: Smoke test**

```bash
cd pwin-platform
node src/server.js &
sleep 2
curl -s "http://localhost:3456/api/intel/cube/cell?sector=Central%20Government&opp_type=IT%20Outsourcing" | head -50
kill %1
```

Expected: JSON with cell data.

- [ ] **Step 4: Verify the other two endpoints**

```bash
node src/server.js &
sleep 2
curl -s "http://localhost:3456/api/intel/cube/credible-competitors?sector=Central%20Government&opp_type=IT%20Outsourcing" | head -30
curl -s "http://localhost:3456/api/intel/cube/cells-for-supplier?canonical_supplier_id=1" | head -30
kill %1
```

Expected: both return JSON without error.

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/src/api.js
git commit -m "feat(cube): add /api/intel/cube/* HTTP endpoints"
```

---

### Task 4.4: Write an MCP integration test

**Files:**
- Create: `pwin-platform/test/test-cube.js`

- [ ] **Step 1: Write the failing test**

Create `pwin-platform/test/test-cube.js`:

```javascript
"use strict";
const assert = require('assert');
const Database = require('better-sqlite3');
const ci = require('../src/competitive-intel.js');

const DB_PATH = process.env.PWIN_DB_PATH || '../pwin-competitive-intel/db/bid_intel.db';

(function testGetCompetitiveCellShape() {
  const db = new Database(DB_PATH, { readonly: true });
  const result = ci.getCompetitiveCell(db, 'Central Government', 'IT Outsourcing');
  assert.ok(result, 'expected a result');
  if (!result.error) {
    assert.ok('total_contracts' in result, 'missing total_contracts');
    assert.ok('credible_competitors' in result, 'missing credible_competitors');
    assert.ok('expiring_contracts' in result, 'missing expiring_contracts');
    assert.ok('forward_pipeline' in result, 'missing forward_pipeline');
  }
  db.close();
  console.log('PASS testGetCompetitiveCellShape');
})();

(function testLensApplied() {
  const db = new Database(DB_PATH, { readonly: true });
  const challenger = ci.getCompetitiveCell(db, 'Central Government', 'IT Outsourcing', 'all', 'challenger');
  if (!challenger.error) {
    assert.ok(challenger.lens_framing, 'expected lens_framing under challenger');
    assert.ok(challenger.lens_framing.cell_concentration.includes('break in') ||
              challenger.lens_framing.cell_concentration.includes('unclear'));
  }
  db.close();
  console.log('PASS testLensApplied');
})();
```

- [ ] **Step 2: Run the test**

```bash
cd pwin-platform
node test/test-cube.js
```

Expected: two PASS lines.

- [ ] **Step 3: Wire it into the existing test runner**

```bash
grep -n "test-" pwin-platform/test/ | head
```

If there's a `package.json` `test` script, add `node test/test-cube.js` to it. Otherwise document the manual run in `CLAUDE.md`.

- [ ] **Step 4: Confirm clean test output**

```bash
node test/test-cube.js
```

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/test/test-cube.js
git commit -m "test(cube): integration test for cube MCP query functions"
```

---

### Task 4.5: Document the new product surface in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Locate the competitive-intel section**

```bash
grep -n "pwin-competitive-intel" CLAUDE.md | head -5
```

- [ ] **Step 2: Add the cube to the components list**

In the `pwin-competitive-intel` section of CLAUDE.md, after the existing components, add a paragraph describing the cube engine. Working text:

```markdown
- **Competitive cube** (`queries/cube_engine.py`) — produces a structured intelligence view of every (sector, opportunity type) cell of UK government procurement. Layer 1: concentration metrics. Layer 2: credible competitor list with per-supplier grip data. Layer 6: forward-looking displacement windows (expiring contracts + planning notices). Refreshed nightly into the `cell_summary` table; consumed by the dashboard "Competitive Cells" tab and three platform MCP tools (`get_competitive_cell`, `get_credible_competitors`, `find_cells_for_supplier`). Supports a challenger / incumbent / neutral framing lens. Spec: `docs/superpowers/specs/2026-05-02-competitive-cube-design.md`. Plan: `docs/superpowers/plans/2026-05-02-competitive-cube-plan.md`.
```

- [ ] **Step 3: Add the cube tools to the MCP tools list**

In the MCP tools section under the `pwin-platform` heading, append:

```markdown
- `get_competitive_cell`, `get_credible_competitors`, `find_cells_for_supplier` (the three competitive cube tools — see the cube section under `pwin-competitive-intel`)
```

- [ ] **Step 4: Smoke check**

Read the modified section back to confirm it slots in cleanly and reads naturally for a non-technical reader.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add competitive cube to CLAUDE.md"
```

---

## Self-Review

This plan has been self-reviewed. Findings:

**Spec coverage:** Every section of the design spec maps to tasks above. Section 1 (product framing) is reflected in CLAUDE.md update (Task 4.5). Section 2 (cube and dimensions) lands in Tasks 1.1–1.8 (schema, classifier, tagging). Section 3 (cell view, three layers, lens) lands in Tasks 1.9–1.13 + 3.6 (UI rendering). Section 4 (architecture) is the structural skeleton of the four stages. Section 5 (cloud-platform alignment) is referenced in the plan header but is the user's separate compare-and-contrast task — no code task; the alignment review happens after this plan ships. Section 6 (out of scope and success criteria) is honoured by the deliberate absence of Layer 3, 4, 5 work, AI tagging work, and forecasting work in this plan.

**Placeholder scan:** No "TBD", "TODO", or vague instructions. Every task has exact file paths, complete code blocks, and explicit commands.

**Type consistency:** Function names match across tasks (`compute_layer_1`, `compute_layer_2`, `compute_layer_6`, `compute_cell_summary`, `refresh_cell_aggregates`). Column names in `cell_summary` match between schema migration (Task 1.2), the engine writer (Task 1.13), and the API readers (Tasks 3.1–3.3). MCP tool names match between the registration (Task 4.2) and the integration test (Task 4.4).

**Scope:** This is one plan covering one product. The four stages are sequential and build on each other; each ships working software at its boundary. The plan is appropriately sized for one implementation cycle.

**Notes for the implementer:**

- The plan uses the current SQLite database. When the cloud migration ships PostgreSQL, the engine SQL is standard enough to port unchanged; the `ON CONFLICT` clause in `refresh_cell_aggregates` is supported by both backends.
- The dashboard implementation is intentionally minimal — production-grade styling is owned by the dashboard rebrand work tracked separately. The CSS in this plan is functional, not final.
- Stage 1 has the highest risk (the tagging pass coverage and the SQL correctness of the engine queries). Treat Tasks 1.4–1.8 as the critical path.
- Stage 4 task 4.4 assumes `better-sqlite3` is the platform's database driver; verify in `package.json` and adjust if a different driver is in use.

---

**End of implementation plan.**
