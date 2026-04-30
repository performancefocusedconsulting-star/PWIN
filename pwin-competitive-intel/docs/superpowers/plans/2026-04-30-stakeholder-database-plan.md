# Stakeholder Database — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the stakeholder canonical layer — a SQLite database of UK central government senior civil servants (Director tier and above), ingested from twice-yearly organogram CSV files and supplemented by a weekly PAC witness scraper, exposed via three MCP tools.

**Architecture:** Three new tables added to the existing `bid_intel.db` database. A standalone Python ingest script fetches organogram CSVs from data.gov.uk and upserts stakeholder records. A separate PAC witness scraper adds event-driven SRO names. Three new query functions in `competitive-intel.js` are registered as MCP tools in `mcp.js`. All Python code uses stdlib only.

**Tech Stack:** Python 3.9+ stdlib (urllib, csv, json, sqlite3, html.parser, re, unittest), Node.js (node:sqlite, existing `_resolveBuyerCanonical` helper).

**Evidence base:** Feasibility report at `docs/research/2026-04-30-stakeholder-database-feasibility.md`. Verdict: build narrower — central government Director tier and above, organograms + PAC witnesses only. NHS England (stopped publishing 2016), local government (no bulk mechanism), and Deputy Director/Grade 6 tier (redacted in organograms) are deferred.

**Key finding from feasibility investigation:** All current central government departments use an identical column set that differs from the original 2011 organogram specification. The parser must handle both variants. Actual current headers:
- `"Grade (or equivalent)"` (not `"Grade"`)
- `"Reports to Senior Post"` (not `"Reports To Senior Post"`)
- `"Contact E-mail"` (not `"Contact Email"`)
- Pay columns carry a `"(£)"` suffix: `"Actual Pay Floor (£)"`, `"Actual Pay Ceiling (£)"`

---

## File Map

| Action | Path |
|---|---|
| Create | `pwin-competitive-intel/agent/stakeholder_utils.py` |
| Create | `pwin-competitive-intel/agent/ingest_organograms.py` |
| Create | `pwin-competitive-intel/agent/scrape_pac_witnesses.py` |
| Create | `pwin-competitive-intel/agent/tests/test_stakeholder.py` |
| Modify | `pwin-competitive-intel/db/schema.sql` |
| Modify | `pwin-competitive-intel/agent/db_utils.py` |
| Modify | `pwin-platform/src/competitive-intel.js` |
| Modify | `pwin-platform/src/mcp.js` |

---

## Task 1: Schema — three new tables + migration

**Files:**
- Modify: `pwin-competitive-intel/db/schema.sql`
- Modify: `pwin-competitive-intel/agent/db_utils.py`
- Create: `pwin-competitive-intel/agent/tests/test_stakeholder.py` (test scaffold)

- [ ] **Step 1: Write the failing schema test**

Create `pwin-competitive-intel/agent/tests/test_stakeholder.py`:

```python
import sys, os, sqlite3, unittest, tempfile
sys.stdout.reconfigure(encoding='utf-8')

# Add agent/ to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'schema.sql')

class TestSchema(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")

    def tearDown(self):
        self.conn.close()

    def _table_exists(self, name):
        row = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone()
        return row is not None

    def _columns(self, table):
        return {r[1] for r in self.conn.execute(f"PRAGMA table_info({table})").fetchall()}

    def test_stakeholders_table_exists(self):
        self.assertFalse(self._table_exists('stakeholders'))

    def test_stakeholder_history_table_exists(self):
        self.assertFalse(self._table_exists('stakeholder_history'))

    def test_pac_witnesses_table_exists(self):
        self.assertFalse(self._table_exists('pac_witnesses'))


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
cd pwin-competitive-intel
python agent/tests/test_stakeholder.py -v
```

Expected: all three `test_*` methods pass trivially because they assert `assertFalse` (tables don't exist yet). This confirms the test runner works.

- [ ] **Step 3: Append the three new tables to `schema.sql`**

Open `pwin-competitive-intel/db/schema.sql` and append after the last line:

```sql

-- ============================================================
-- STAKEHOLDER CANONICAL LAYER (2026-04-30)
-- Organogram-derived senior civil servants, Director tier and above.
-- Supplemented by PAC witness lists for event-driven SRO capture.
-- Feasibility report: docs/research/2026-04-30-stakeholder-database-feasibility.md
-- ============================================================

CREATE TABLE IF NOT EXISTS stakeholders (
    person_id          TEXT PRIMARY KEY,   -- '{name-slug}--{canonical_buyer_id}'
    name_raw           TEXT NOT NULL,      -- verbatim from source
    name_normalised    TEXT NOT NULL,      -- 'First Last' for cross-source matching
    job_title          TEXT,
    unit               TEXT,              -- organisational unit within department
    organisation       TEXT,             -- sub-org (e.g. NISTA within HM Treasury)
    parent_department  TEXT,             -- raw dept name from source CSV
    canonical_buyer_id TEXT REFERENCES canonical_buyers(canonical_id),
    scs_band_inferred  TEXT,             -- PermanentSecretary | DirectorGeneral | Director | DeputyDirector | Unknown
    reports_to_post    TEXT,             -- 'Reports to Senior Post' value from organogram
    source             TEXT NOT NULL,   -- 'organogram' | 'pac_witness'
    source_url         TEXT,
    snapshot_date      TEXT,             -- YYYY-MM-DD of organogram; NULL for pac_witness rows
    ingested_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_stakeholders_buyer  ON stakeholders(canonical_buyer_id);
CREATE INDEX IF NOT EXISTS idx_stakeholders_name   ON stakeholders(name_normalised);
CREATE INDEX IF NOT EXISTS idx_stakeholders_band   ON stakeholders(scs_band_inferred);
CREATE INDEX IF NOT EXISTS idx_stakeholders_source ON stakeholders(source);

CREATE TABLE IF NOT EXISTS stakeholder_history (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id          TEXT NOT NULL REFERENCES stakeholders(person_id),
    snapshot_date      TEXT NOT NULL,
    job_title          TEXT,
    unit               TEXT,
    canonical_buyer_id TEXT,
    recorded_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sh_person   ON stakeholder_history(person_id);
CREATE INDEX IF NOT EXISTS idx_sh_snapshot ON stakeholder_history(snapshot_date);

CREATE TABLE IF NOT EXISTS pac_witnesses (
    witness_id         TEXT PRIMARY KEY,   -- '{name-slug}--{session-date}'
    name_raw           TEXT NOT NULL,
    name_normalised    TEXT NOT NULL,
    role_title         TEXT,
    organisation       TEXT,
    canonical_buyer_id TEXT REFERENCES canonical_buyers(canonical_id),
    session_date       TEXT,              -- YYYY-MM-DD
    session_title      TEXT,
    session_url        TEXT NOT NULL,
    scraped_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_pac_buyer ON pac_witnesses(canonical_buyer_id);
CREATE INDEX IF NOT EXISTS idx_pac_name  ON pac_witnesses(name_normalised);
```

- [ ] **Step 4: Add the migration block to `db_utils.py`**

In `pwin-competitive-intel/agent/db_utils.py`, find the `_migrate_schema` function. Locate the frameworks block (the last block before `conn.commit()`):

```python
    # ── frameworks canonical layer (2026-04-30) ──
    # New tables: created by CREATE TABLE IF NOT EXISTS in schema.sql.
    # Only column additions to existing framework tables go here.
    pass
```

Replace that block with:

```python
    # ── frameworks canonical layer (2026-04-30) ──
    # New tables created by CREATE TABLE IF NOT EXISTS in schema.sql.
    pass

    # ── stakeholder canonical layer (2026-04-30) ──
    # Three new tables: stakeholders, stakeholder_history, pac_witnesses.
    # Created by CREATE TABLE IF NOT EXISTS in schema.sql — no ALTER needed.
    pass
```

This is a no-op migration because the tables use `CREATE TABLE IF NOT EXISTS` in schema.sql — the comment is the record that they were added in this session.

- [ ] **Step 5: Update the failing tests to assert the tables now exist after applying schema**

Update `test_stakeholder.py` — replace the three test methods:

```python
    def _apply_schema(self):
        with open(SCHEMA_PATH, encoding='utf-8') as f:
            self.conn.executescript(f.read())

    def test_stakeholders_table_exists(self):
        self._apply_schema()
        self.assertTrue(self._table_exists('stakeholders'))
        cols = self._columns('stakeholders')
        self.assertIn('person_id', cols)
        self.assertIn('name_normalised', cols)
        self.assertIn('canonical_buyer_id', cols)
        self.assertIn('scs_band_inferred', cols)

    def test_stakeholder_history_table_exists(self):
        self._apply_schema()
        self.assertTrue(self._table_exists('stakeholder_history'))
        cols = self._columns('stakeholder_history')
        self.assertIn('person_id', cols)
        self.assertIn('snapshot_date', cols)

    def test_pac_witnesses_table_exists(self):
        self._apply_schema()
        self.assertTrue(self._table_exists('pac_witnesses'))
        cols = self._columns('pac_witnesses')
        self.assertIn('witness_id', cols)
        self.assertIn('name_normalised', cols)
        self.assertIn('canonical_buyer_id', cols)
```

- [ ] **Step 6: Run to confirm tests pass**

```bash
cd pwin-competitive-intel
python agent/tests/test_stakeholder.py -v
```

Expected output:
```
test_pac_witnesses_table_exists ... ok
test_stakeholder_history_table_exists ... ok
test_stakeholders_table_exists ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.XXXs
OK
```

- [ ] **Step 7: Commit**

```bash
git add pwin-competitive-intel/db/schema.sql
git add pwin-competitive-intel/agent/db_utils.py
git add pwin-competitive-intel/agent/tests/test_stakeholder.py
git commit -m "feat(stakeholders): schema — 3 new tables for stakeholder canonical layer"
```

---

## Task 2: Utility functions — name normaliser, SCS band inference, column resolver

**Files:**
- Create: `pwin-competitive-intel/agent/stakeholder_utils.py`
- Modify: `pwin-competitive-intel/agent/tests/test_stakeholder.py`

These are pure functions with no database or network dependencies. Tested against the sample records from the feasibility report.

- [ ] **Step 1: Write the failing tests first**

Add a `TestUtils` class to `test_stakeholder.py` (below the existing `TestSchema` class):

```python
class TestUtils(unittest.TestCase):

    def test_normalise_name_last_first(self):
        from stakeholder_utils import normalise_name
        self.assertEqual(normalise_name('Gallagher, Daniel'), 'Daniel Gallagher')

    def test_normalise_name_with_nickname_and_title(self):
        from stakeholder_utils import normalise_name
        self.assertEqual(normalise_name('Rouse, Deana (Deana), Miss'), 'Deana Rouse')
        self.assertEqual(normalise_name('Berthon, Richard (Richard), Mr'), 'Richard Berthon')

    def test_normalise_name_already_normalised(self):
        from stakeholder_utils import normalise_name
        self.assertEqual(normalise_name('Isabelle Trowler'), 'Isabelle Trowler')
        self.assertEqual(normalise_name('Helen Waite'), 'Helen Waite')

    def test_normalise_name_empty(self):
        from stakeholder_utils import normalise_name
        self.assertEqual(normalise_name(''), '')
        self.assertEqual(normalise_name('  '), '')

    def test_infer_scs_band_permanent_secretary(self):
        from stakeholder_utils import infer_scs_band
        self.assertEqual(infer_scs_band('Permanent Secretary'), 'PermanentSecretary')
        self.assertEqual(infer_scs_band('Second Permanent Secretary'), 'PermanentSecretary')

    def test_infer_scs_band_director_general(self):
        from stakeholder_utils import infer_scs_band
        self.assertEqual(infer_scs_band('Director General and Chief Economic Adviser'), 'DirectorGeneral')
        self.assertEqual(infer_scs_band('Director-General, Strategy'), 'DirectorGeneral')

    def test_infer_scs_band_director(self):
        from stakeholder_utils import infer_scs_band
        self.assertEqual(infer_scs_band('Director - Economics'), 'Director')
        self.assertEqual(infer_scs_band('Director of Finance and Deputy CEO Infrastructure Projects Authority'), 'Director')
        self.assertEqual(infer_scs_band('FCAS Director'), 'Director')

    def test_infer_scs_band_deputy_director_not_director(self):
        from stakeholder_utils import infer_scs_band
        # DeputyDirector must not match as Director
        self.assertEqual(infer_scs_band('Deputy Director, Commercial Policy'), 'DeputyDirector')

    def test_infer_scs_band_unknown(self):
        from stakeholder_utils import infer_scs_band
        self.assertEqual(infer_scs_band('Secretary of State COS-2'), 'Unknown')
        self.assertEqual(infer_scs_band(''), 'Unknown')

    def test_resolve_col_current_format(self):
        from stakeholder_utils import resolve_col
        row = {
            'Name': 'Gallagher, Daniel',
            'Grade (or equivalent)': 'SCS2',
            'Reports to Senior Post': 'CEO',
            'Contact E-mail': 'daniel.gallagher@hmt.gov.uk',
        }
        self.assertEqual(resolve_col(row, 'name'), 'Gallagher, Daniel')
        self.assertEqual(resolve_col(row, 'grade'), 'SCS2')
        self.assertEqual(resolve_col(row, 'reports_to'), 'CEO')

    def test_resolve_col_legacy_format(self):
        from stakeholder_utils import resolve_col
        row = {
            'Name': 'Smith, Jane',
            'Grade': 'SCS1',
            'Reports To Senior Post': 'Head of Unit',
            'Contact Email': 'jane.smith@dfe.gov.uk',
        }
        self.assertEqual(resolve_col(row, 'grade'), 'SCS1')
        self.assertEqual(resolve_col(row, 'reports_to'), 'Head of Unit')

    def test_resolve_col_missing_field_returns_empty(self):
        from stakeholder_utils import resolve_col
        self.assertEqual(resolve_col({}, 'grade'), '')
        self.assertEqual(resolve_col({}, 'reports_to'), '')

    def test_slug(self):
        from stakeholder_utils import slug
        self.assertEqual(slug('Daniel Gallagher'), 'daniel-gallagher')
        self.assertEqual(slug('  Hello  World  '), 'hello-world')

    def test_person_id(self):
        from stakeholder_utils import person_id
        self.assertEqual(person_id('Daniel Gallagher', 'hm-treasury'), 'daniel-gallagher--hm-treasury')
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
cd pwin-competitive-intel
python agent/tests/test_stakeholder.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'stakeholder_utils'`

- [ ] **Step 3: Create `stakeholder_utils.py`**

Create `pwin-competitive-intel/agent/stakeholder_utils.py`:

```python
"""
PWIN Competitive Intelligence — Stakeholder utilities
======================================================
Pure functions: name normalisation, SCS band inference, column resolution.
No database or network dependencies.
"""

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ── Name normalisation ───────────────────────────────────────────────────────

_HONORIFICS = {
    'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'dame',
    'reverend', 'rev', 'lord', 'lady',
}


def normalise_name(raw: str) -> str:
    """Convert organogram name variants to 'First Last'.

    Handles:
      'Gallagher, Daniel'              -> 'Daniel Gallagher'
      'Rouse, Deana (Deana), Miss'     -> 'Deana Rouse'
      'Berthon, Richard (Richard), Mr' -> 'Richard Berthon'
      'Isabelle Trowler'               -> 'Isabelle Trowler'
    """
    name = (raw or '').strip()
    if not name:
        return name

    if ',' in name:
        parts = name.split(',', 1)
        surname = parts[0].strip()
        rest = parts[1].strip()
        # strip parenthetical nicknames: "(Deana)", "(Richard)"
        rest = re.sub(r'\s*\([^)]*\)\s*', ' ', rest).strip()
        # strip trailing honorifics
        tokens = rest.split()
        while tokens and tokens[-1].lower().rstrip('.') in _HONORIFICS:
            tokens.pop()
        first = tokens[0] if tokens else ''
        return f'{first} {surname}'.strip() if first else surname

    return name


def slug(text: str) -> str:
    """Lowercase, spaces to hyphens, strip non-alphanumeric (except hyphens)."""
    s = text.lower().strip()
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'[^a-z0-9\-]', '', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s


def person_id(name_normalised: str, canonical_buyer_id: str) -> str:
    return f'{slug(name_normalised)}--{canonical_buyer_id}'


# ── SCS band inference ───────────────────────────────────────────────────────

# Checked in order — DeputyDirector before Director so 'Deputy Director' is
# not captured by the Director rule.
_BAND_PATTERNS = [
    ('PermanentSecretary', [
        'permanent secretary',
        'first permanent secretary',
        'second permanent secretary',
    ]),
    ('DirectorGeneral', ['director general', 'director-general']),
    ('DeputyDirector', ['deputy director']),
    ('Director', ['director']),
]


def infer_scs_band(job_title: str) -> str:
    """Infer SCS band from job title string."""
    t = (job_title or '').lower()
    for band, keywords in _BAND_PATTERNS:
        for kw in keywords:
            if kw in t:
                return band
    return 'Unknown'


# ── Column resolution ────────────────────────────────────────────────────────

# Maps logical field name -> ordered list of CSV header variants (current first,
# legacy 2011 spec variants after). resolve_col() tries each in order.
COLUMN_MAP = {
    'name':              ['Name'],
    'grade':             ['Grade (or equivalent)', 'Grade'],
    'job_title':         ['Job Title'],
    'parent_department': ['Parent Department'],
    'organisation':      ['Organisation'],
    'unit':              ['Unit'],
    'contact_email':     ['Contact E-mail', 'Contact Email'],
    'reports_to':        ['Reports to Senior Post', 'Reports To Senior Post'],
    'fte':               ['FTE'],
    'pay_floor':         ['Actual Pay Floor (£)', 'Actual Pay Floor'],
    'pay_ceiling':       ['Actual Pay Ceiling (£)', 'Actual Pay Ceiling'],
    'valid':             ['Valid?'],
    'post_ref':          ['Post Unique Reference'],
    'prof_group':        ['Professional/Occupational Group'],
    'notes':             ['Notes'],
}


def resolve_col(row: dict, field: str) -> str:
    """Return the value for a logical field, trying each header variant in order."""
    for header in COLUMN_MAP.get(field, []):
        if header in row:
            return (row[header] or '').strip()
    return ''
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd pwin-competitive-intel
python agent/tests/test_stakeholder.py -v
```

Expected output:
```
test_infer_scs_band_deputy_director_not_director ... ok
test_infer_scs_band_director ... ok
test_infer_scs_band_director_general ... ok
test_infer_scs_band_permanent_secretary ... ok
test_infer_scs_band_unknown ... ok
test_normalise_name_already_normalised ... ok
test_normalise_name_empty ... ok
test_normalise_name_last_first ... ok
test_normalise_name_with_nickname_and_title ... ok
test_pac_witnesses_table_exists ... ok
test_person_id ... ok
test_resolve_col_current_format ... ok
test_resolve_col_legacy_format ... ok
test_resolve_col_missing_field_returns_empty ... ok
test_schema_applied ... ok  (or similar — from TestSchema)
test_slug ... ok
test_stakeholder_history_table_exists ... ok
test_stakeholders_table_exists ... ok
----------------------------------------------------------------------
Ran 18 tests in 0.XXXs
OK
```

- [ ] **Step 5: Commit**

```bash
git add pwin-competitive-intel/agent/stakeholder_utils.py
git add pwin-competitive-intel/agent/tests/test_stakeholder.py
git commit -m "feat(stakeholders): name normaliser, SCS band inference, column resolver with tests"
```

---

## Task 3: Organogram ingest script

**Files:**
- Create: `pwin-competitive-intel/agent/ingest_organograms.py`
- Modify: `pwin-competitive-intel/agent/tests/test_stakeholder.py`

This script fetches senior-staff CSVs from data.gov.uk and upserts stakeholder records into `bid_intel.db`.

- [ ] **Step 1: Write the failing tests**

Add a `TestOrganogramParser` class to `test_stakeholder.py`:

```python
class TestOrganogramParser(unittest.TestCase):
    """Tests parse_organogram_csv() in isolation — no network, no database."""

    # Fixture CSV using the current (post-2011 drift) column format
    FIXTURE_CSV_CURRENT = (
        "Post Unique Reference,Name,Grade (or equivalent),Job Title,"
        "Parent Department,Organisation,Unit,Contact E-mail,"
        "Reports to Senior Post,FTE,Actual Pay Floor (£),Actual Pay Ceiling (£),"
        "Professional/Occupational Group,Notes,Valid?\n"
        "1001,Gallagher Daniel,SCS2,Director - Economics,"
        "HM Treasury,HM Treasury,Economics,d.gallagher@hmt.gov.uk,"
        "Director General Economic Affairs,1.0,95000,100000,Economics,, Y\n"
        "1002,N/D,,Grade 6 Policy Adviser,"
        "HM Treasury,HM Treasury,Economics,,1234,1.0,55000,60000,Policy,,Y\n"
        "1003,Russell Elizabeth,,Second Permanent Secretary,"
        "HM Treasury,HM Treasury,Ministerial & Communications,,1001,1.0,150000,155000,Strategy,,Y\n"
    )

    FIXTURE_CSV_LEGACY = (
        "Post Unique Reference,Name,Grade,Job Title,"
        "Parent Department,Organisation,Unit,Contact Email,"
        "Reports To Senior Post,FTE,Actual Pay Floor,Actual Pay Ceiling,"
        "Professional/Occupational Group,Notes,Valid?\n"
        "2001,Smith Jane,SCS1,Deputy Director Policy,"
        "Ministry of Justice,Ministry of Justice,Criminal Policy,j.smith@moj.gov.uk,"
        "Director Criminal Justice,1.0,75000,80000,Policy,,Y\n"
    )

    def _parse(self, csv_text, source=None):
        import io, csv as csv_mod
        from ingest_organograms import parse_organogram_csv
        raw = csv_text.encode('utf-8')
        return parse_organogram_csv(raw, source or {'canonical_id': 'hm-treasury', 'source_url': 'http://example.com', 'snapshot_date': '2025-12-01'})

    def test_named_rows_only(self):
        records = self._parse(self.FIXTURE_CSV_CURRENT)
        # Row 2 has 'N/D' name — should be filtered out
        self.assertEqual(len(records), 2)

    def test_name_normalised(self):
        records = self._parse(self.FIXTURE_CSV_CURRENT)
        names = [r['name_normalised'] for r in records]
        self.assertIn('Daniel Gallagher', names)
        self.assertIn('Elizabeth Russell', names)

    def test_scs_band_inferred(self):
        records = self._parse(self.FIXTURE_CSV_CURRENT)
        by_name = {r['name_normalised']: r for r in records}
        self.assertEqual(by_name['Daniel Gallagher']['scs_band_inferred'], 'Director')
        self.assertEqual(by_name['Elizabeth Russell']['scs_band_inferred'], 'PermanentSecretary')

    def test_person_id_format(self):
        records = self._parse(self.FIXTURE_CSV_CURRENT)
        by_name = {r['name_normalised']: r for r in records}
        self.assertEqual(by_name['Daniel Gallagher']['person_id'], 'daniel-gallagher--hm-treasury')

    def test_legacy_column_names(self):
        records = self._parse(
            self.FIXTURE_CSV_LEGACY,
            source={'canonical_id': 'ministry-of-justice', 'source_url': 'http://example.com', 'snapshot_date': '2025-09-01'}
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name_normalised'], 'Jane Smith')
        self.assertEqual(records[0]['scs_band_inferred'], 'DeputyDirector')

    def test_source_fields_carried_through(self):
        records = self._parse(self.FIXTURE_CSV_CURRENT)
        self.assertEqual(records[0]['source'], 'organogram')
        self.assertEqual(records[0]['snapshot_date'], '2025-12-01')
        self.assertEqual(records[0]['source_url'], 'http://example.com')
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
cd pwin-competitive-intel
python agent/tests/test_stakeholder.py TestOrganogramParser -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError: No module named 'ingest_organograms'`

- [ ] **Step 3: Create `ingest_organograms.py`**

Create `pwin-competitive-intel/agent/ingest_organograms.py`:

```python
"""
PWIN Competitive Intelligence — Government organogram ingest
============================================================
Fetches senior-staff CSV files from data.gov.uk, parses them,
and upserts stakeholder records into bid_intel.db.

Usage:
    python ingest_organograms.py              # all priority departments
    python ingest_organograms.py --dept hmt   # single department key
    python ingest_organograms.py --limit 3    # cap departments processed
    python ingest_organograms.py --dry-run    # parse only, no DB writes
"""

import argparse
import csv
import io
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding='utf-8')

from db_utils import get_db, init_schema
from stakeholder_utils import (
    normalise_name, slug, person_id, infer_scs_band, resolve_col,
)

# ── Config ───────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / 'db' / 'bid_intel.db'
SCHEMA_PATH = Path(__file__).parent.parent / 'db' / 'schema.sql'
DATA_GOV_UK_API = 'https://data.gov.uk/api/3/action/package_search'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger('ingest_organograms')

# ── Priority departments (v1 — central government + major ALBs) ──────────────
# canonical_id values must match canonical_buyers.canonical_id in bid_intel.db.
# Run `python queries/queries.py buyer "{name}"` to verify before first ingest.

PRIORITY_DEPARTMENTS = {
    'hmt':              {'query': 'HM Treasury organogram senior staff salaries',                         'canonical_id': 'hm-treasury'},
    'mod':              {'query': 'Ministry of Defence organogram senior staff salaries',                  'canonical_id': 'ministry-of-defence'},
    'dfe':              {'query': 'Department for Education organogram senior staff salaries',             'canonical_id': 'department-for-education'},
    'home-office':      {'query': 'Home Office organogram senior staff salaries',                         'canonical_id': 'home-office'},
    'hmrc':             {'query': 'HMRC organogram senior staff salaries',                                'canonical_id': 'hm-revenue-and-customs'},
    'dhsc':             {'query': 'Department Health Social Care organogram senior staff',                 'canonical_id': 'department-of-health-and-social-care'},
    'mhclg':            {'query': 'Ministry Housing Communities organogram senior staff',                  'canonical_id': 'ministry-of-housing-communities-and-local-government'},
    'dwp':              {'query': 'Department Work Pensions organogram senior staff',                     'canonical_id': 'department-for-work-and-pensions'},
    'moj':              {'query': 'Ministry of Justice organogram senior staff salaries',                  'canonical_id': 'ministry-of-justice'},
    'dcms':             {'query': 'Department Culture Media Sport organogram senior staff',               'canonical_id': 'department-for-culture-media-and-sport'},
    'desnz':            {'query': 'Department Energy Security Net Zero organogram senior staff',          'canonical_id': 'department-for-energy-security-and-net-zero'},
    'dsit':             {'query': 'Department Science Innovation Technology organogram senior staff',     'canonical_id': 'department-for-science-innovation-and-technology'},
    'fcdo':             {'query': 'Foreign Commonwealth Development Office organogram senior staff',      'canonical_id': 'foreign-commonwealth-and-development-office'},
    'cabinet-office':   {'query': 'Cabinet Office organogram senior staff salaries',                     'canonical_id': 'cabinet-office'},
    'dft':              {'query': 'Department for Transport organogram senior staff salaries',            'canonical_id': 'department-for-transport'},
    'defra':            {'query': 'Department Environment Food Rural Affairs organogram senior staff',   'canonical_id': 'department-for-environment-food-and-rural-affairs'},
    'environment-agency': {'query': 'Environment Agency organogram senior staff',                        'canonical_id': 'environment-agency'},
    'ccs':              {'query': 'Crown Commercial Service organogram senior staff',                     'canonical_id': 'crown-commercial-service'},
    'homes-england':    {'query': 'Homes England organogram senior staff',                               'canonical_id': 'homes-england'},
    'ukri':             {'query': 'UK Research Innovation organogram senior staff',                      'canonical_id': 'uk-research-and-innovation'},
}

# Name values that mean "redacted" in organogram CSVs
_REDACTION_MARKERS = frozenset({'N/D', 'ND', 'REDACTED', 'WITHHELD', 'N/A', 'N/D (VPR)', '', '-'})


# ── CSV decoding ─────────────────────────────────────────────────────────────

def _decode(raw: bytes) -> str:
    for enc in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError('Cannot decode CSV with any known encoding')


# ── data.gov.uk discovery ────────────────────────────────────────────────────

def _find_senior_staff_resource(package: dict) -> Optional[dict]:
    resources = package.get('resources', [])
    candidates = [
        r for r in resources
        if 'senior' in (r.get('name') or '').lower()
        or 'senior' in (r.get('url') or '').lower()
    ]
    if not candidates:
        candidates = [
            r for r in resources
            if (r.get('format') or '').upper() in ('CSV', '')
            and 'junior' not in (r.get('name') or '').lower()
        ]
    if not candidates:
        return None
    candidates.sort(
        key=lambda r: r.get('last_modified') or r.get('created') or '',
        reverse=True,
    )
    return candidates[0]


def fetch_organogram_url(query: str) -> Optional[tuple]:
    """Return (csv_url, dataset_url, snapshot_date) or None."""
    params = urlencode({'q': query, 'sort': 'metadata_modified desc', 'rows': 5})
    url = f'{DATA_GOV_UK_API}?{params}'
    try:
        with urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        log.warning('data.gov.uk API error: %s', e)
        return None

    packages = data.get('result', {}).get('results', [])
    if not packages:
        return None

    resource = _find_senior_staff_resource(packages[0])
    if not resource:
        return None

    csv_url = resource.get('url')
    dataset_url = f'https://data.gov.uk/dataset/{packages[0].get("name", "")}'
    modified = resource.get('last_modified') or resource.get('created') or ''
    snapshot_date = modified.split('T')[0] if modified else None
    return csv_url, dataset_url, snapshot_date


def download_csv(url: str) -> Optional[bytes]:
    try:
        req = Request(url, headers={'User-Agent': 'PWIN-Intel/1.0'})
        with urlopen(req, timeout=30) as resp:
            return resp.read()
    except Exception as e:
        log.warning('Download failed %s: %s', url, e)
        return None


# ── Parsing ──────────────────────────────────────────────────────────────────

def parse_organogram_csv(raw_bytes: bytes, source: dict) -> list:
    """Parse a senior-staff CSV, returning a list of stakeholder dicts.

    source dict must contain: canonical_id, source_url, snapshot_date.
    Named rows only — redacted/blank names are skipped.
    """
    text = _decode(raw_bytes)
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    canonical_id = source.get('canonical_id', '')
    results = []

    for row in rows:
        name_raw = resolve_col(row, 'name')
        if not name_raw or name_raw.upper().strip() in _REDACTION_MARKERS:
            continue

        name_norm = normalise_name(name_raw)
        job_title = resolve_col(row, 'job_title')
        unit = resolve_col(row, 'unit')
        organisation = resolve_col(row, 'organisation')
        parent_department = resolve_col(row, 'parent_department')
        reports_to = resolve_col(row, 'reports_to')

        pid = person_id(name_norm, canonical_id)
        band = infer_scs_band(job_title)

        results.append({
            'person_id': pid,
            'name_raw': name_raw,
            'name_normalised': name_norm,
            'job_title': job_title,
            'unit': unit,
            'organisation': organisation,
            'parent_department': parent_department,
            'canonical_buyer_id': canonical_id,
            'scs_band_inferred': band,
            'reports_to_post': reports_to,
            'source': 'organogram',
            'source_url': source.get('source_url'),
            'snapshot_date': source.get('snapshot_date'),
        })

    return results


# ── DB write ─────────────────────────────────────────────────────────────────

def upsert_stakeholder(conn, record: dict):
    """Upsert one stakeholder. If job_title or unit changed, write history."""
    existing = conn.execute(
        'SELECT job_title, unit, canonical_buyer_id FROM stakeholders WHERE person_id = ?',
        (record['person_id'],),
    ).fetchone()

    if existing:
        old_title = existing['job_title'] if hasattr(existing, '__getitem__') else existing[0]
        old_unit = existing['unit'] if hasattr(existing, '__getitem__') else existing[1]
        old_buyer = existing['canonical_buyer_id'] if hasattr(existing, '__getitem__') else existing[2]
        if old_title != record['job_title'] or old_unit != record['unit']:
            conn.execute(
                'INSERT INTO stakeholder_history '
                '(person_id, snapshot_date, job_title, unit, canonical_buyer_id) '
                'VALUES (?, ?, ?, ?, ?)',
                (record['person_id'], record['snapshot_date'],
                 old_title, old_unit, old_buyer),
            )

    conn.execute(
        '''INSERT OR REPLACE INTO stakeholders
           (person_id, name_raw, name_normalised, job_title, unit, organisation,
            parent_department, canonical_buyer_id, scs_band_inferred, reports_to_post,
            source, source_url, snapshot_date, ingested_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
        (
            record['person_id'], record['name_raw'], record['name_normalised'],
            record['job_title'], record['unit'], record['organisation'],
            record['parent_department'], record['canonical_buyer_id'],
            record['scs_band_inferred'], record['reports_to_post'],
            record['source'], record['source_url'], record['snapshot_date'],
        ),
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def run(dept_filter=None, limit=None, dry_run=False):
    conn = get_db(DB_PATH)
    init_schema(conn, SCHEMA_PATH)

    depts = PRIORITY_DEPARTMENTS
    if dept_filter:
        depts = {k: v for k, v in depts.items() if k == dept_filter}
        if not depts:
            log.error('Unknown dept key: %s. Valid keys: %s', dept_filter, list(PRIORITY_DEPARTMENTS))
            return
    if limit:
        depts = dict(list(depts.items())[:limit])

    total = 0
    for dept_id, dept_info in depts.items():
        log.info('Processing %s...', dept_id)

        result = fetch_organogram_url(dept_info['query'])
        if not result:
            log.warning('  No organogram found for %s', dept_id)
            continue

        csv_url, dataset_url, snapshot_date = result
        log.info('  CSV: %s (snapshot %s)', csv_url, snapshot_date)

        raw = download_csv(csv_url)
        if not raw:
            log.warning('  Download failed for %s', dept_id)
            continue

        source = {
            'canonical_id': dept_info['canonical_id'],
            'source_url': dataset_url,
            'snapshot_date': snapshot_date,
        }
        records = parse_organogram_csv(raw, source)
        log.info('  Parsed %d named staff records', len(records))

        if not dry_run:
            for rec in records:
                upsert_stakeholder(conn, rec)
            conn.commit()

        total += len(records)
        log.info('  Done (%d records%s)', len(records), ' — dry run' if dry_run else '')
        time.sleep(1)  # polite delay between departments

    conn.close()
    log.info('Complete. Total records processed: %d', total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest government organogram CSV files')
    parser.add_argument('--dept', help='Single department key (e.g. hmt, mod, dfe)')
    parser.add_argument('--limit', type=int, help='Max number of departments to process')
    parser.add_argument('--dry-run', action='store_true', help='Parse but do not write to database')
    args = parser.parse_args()
    run(dept_filter=args.dept, limit=args.limit, dry_run=args.dry_run)
```

- [ ] **Step 4: Run parser tests**

```bash
cd pwin-competitive-intel
python agent/tests/test_stakeholder.py TestOrganogramParser -v
```

Expected: all 6 `TestOrganogramParser` tests pass. Fix any failures before proceeding.

- [ ] **Step 5: Smoke test against the live database**

```bash
cd pwin-competitive-intel
python agent/ingest_organograms.py --dept hmt --dry-run
```

Expected output:
```
HH:MM:SS  INFO     Processing hmt...
HH:MM:SS  INFO       CSV: https://data.gov.uk/... (snapshot 2025-12-01)
HH:MM:SS  INFO       Parsed 44 named staff records
HH:MM:SS  INFO       Done (44 records -- dry run)
HH:MM:SS  INFO     Complete. Total records processed: 44
```

If the data.gov.uk API returns a different number (the dataset is updated periodically), that is expected — the count will match whatever HM Treasury's most recent organogram contains. If the API returns zero records, check the query string in `PRIORITY_DEPARTMENTS['hmt']` and adjust to match the current dataset name.

- [ ] **Step 6: Ingest one department for real**

```bash
cd pwin-competitive-intel
python agent/ingest_organograms.py --dept hmt
```

Verify the records were written:

```bash
python -c "
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
rows = conn.execute(\"SELECT count(*) FROM stakeholders WHERE source='organogram'\").fetchone()
sample = conn.execute(\"SELECT name_normalised, job_title, scs_band_inferred FROM stakeholders LIMIT 5\").fetchall()
print('Total stakeholder rows:', rows[0])
for r in sample: print(' ', r)
conn.close()
"
```

Expected: count > 0, each row has a name, job_title, and a band that is not all 'Unknown'.

- [ ] **Step 7: Commit**

```bash
git add pwin-competitive-intel/agent/ingest_organograms.py
git add pwin-competitive-intel/agent/tests/test_stakeholder.py
git commit -m "feat(stakeholders): organogram ingest — fetch, parse, upsert with TDD"
```

---

## Task 4: PAC witness scraper

**Files:**
- Create: `pwin-competitive-intel/agent/scrape_pac_witnesses.py`
- Modify: `pwin-competitive-intel/agent/tests/test_stakeholder.py`

The Public Accounts Committee publishes oral evidence sessions at `https://committees.parliament.uk/committee/127/public-accounts-committee/publications/?type=oral-evidence`. Each session page lists witness names, roles, and organisations in an HTML table.

- [ ] **Step 1: Write the failing test**

Add a `TestPACWitnessScraper` class to `test_stakeholder.py`:

```python
class TestPACWitnessScraper(unittest.TestCase):
    """Tests parse_witnesses_html() in isolation — no network."""

    # Minimal HTML fixture modelled on the Parliament website witness table structure
    FIXTURE_HTML = """
    <html><body>
    <section class="publication-related-links">
      <h2>Witnesses</h2>
      <ul>
        <li>Matthew Vickerstaff, Director General, National Infrastructure and Service Transformation Authority</li>
        <li>Tom Scholar, Permanent Secretary, HM Treasury</li>
        <li>Beth Russell, Director General, Tax and Welfare, HM Treasury</li>
      </ul>
    </section>
    </body></html>
    """

    def test_parse_witnesses_returns_list(self):
        from scrape_pac_witnesses import parse_witnesses_html
        witnesses = parse_witnesses_html(
            self.FIXTURE_HTML,
            session_date='2025-11-15',
            session_title='NISTA Spending Review',
            session_url='https://committees.parliament.uk/work/9999/oral-evidence/',
        )
        self.assertIsInstance(witnesses, list)
        self.assertEqual(len(witnesses), 3)

    def test_parse_witnesses_fields(self):
        from scrape_pac_witnesses import parse_witnesses_html
        witnesses = parse_witnesses_html(
            self.FIXTURE_HTML,
            session_date='2025-11-15',
            session_title='NISTA Spending Review',
            session_url='https://committees.parliament.uk/work/9999/oral-evidence/',
        )
        w = witnesses[0]
        self.assertIn('name_normalised', w)
        self.assertIn('role_title', w)
        self.assertIn('organisation', w)
        self.assertIn('session_date', w)
        self.assertIn('witness_id', w)
        self.assertEqual(w['session_date'], '2025-11-15')

    def test_parse_witnesses_name_normalised(self):
        from scrape_pac_witnesses import parse_witnesses_html
        witnesses = parse_witnesses_html(
            self.FIXTURE_HTML,
            session_date='2025-11-15',
            session_title='NISTA Spending Review',
            session_url='https://committees.parliament.uk/work/9999/oral-evidence/',
        )
        names = [w['name_normalised'] for w in witnesses]
        self.assertIn('Matthew Vickerstaff', names)
        self.assertIn('Tom Scholar', names)
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
cd pwin-competitive-intel
python agent/tests/test_stakeholder.py TestPACWitnessScraper -v 2>&1 | head -5
```

Expected: `ModuleNotFoundError: No module named 'scrape_pac_witnesses'`

- [ ] **Step 3: Create `scrape_pac_witnesses.py`**

Create `pwin-competitive-intel/agent/scrape_pac_witnesses.py`:

```python
"""
PWIN Competitive Intelligence — PAC witness list scraper
========================================================
Scrapes Public Accounts Committee oral evidence sessions, extracts witness
names and organisations, and upserts into pac_witnesses in bid_intel.db.

The Parliament website exposes witness lists in two formats depending on
the session age: newer sessions use a structured <ul> list, older sessions
may use a <table>. Both are handled.

Usage:
    python scrape_pac_witnesses.py              # last 12 months of sessions
    python scrape_pac_witnesses.py --months 6   # narrower window
    python scrape_pac_witnesses.py --dry-run    # parse only, no DB writes
    python scrape_pac_witnesses.py --url URL    # single session URL

PAC publications index:
  https://committees.parliament.uk/committee/127/public-accounts-committee/publications/?type=oral-evidence
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding='utf-8')

from db_utils import get_db, init_schema
from stakeholder_utils import normalise_name, slug

# ── Config ───────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / 'db' / 'bid_intel.db'
SCHEMA_PATH = Path(__file__).parent.parent / 'db' / 'schema.sql'
PAC_BASE = 'https://committees.parliament.uk'
PAC_PUBLICATIONS = (
    f'{PAC_BASE}/committee/127/public-accounts-committee/publications/'
    '?type=oral-evidence'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger('scrape_pac')


# ── HTML fetching ─────────────────────────────────────────────────────────────

def _fetch(url: str) -> Optional[str]:
    try:
        req = Request(url, headers={'User-Agent': 'PWIN-Intel/1.0'})
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        log.warning('Fetch failed %s: %s', url, e)
        return None


# ── Witness HTML parsing ──────────────────────────────────────────────────────

class _ListExtractor(HTMLParser):
    """Extracts <li> text items from inside a Witnesses section."""

    def __init__(self):
        super().__init__()
        self._in_witnesses = False
        self._in_li = False
        self._depth = 0
        self.items = []
        self._current = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ('h2', 'h3') :
            self._in_witnesses = False  # will be set true by handle_data
        if tag == 'li' and self._in_witnesses:
            self._in_li = True
            self._current = []
        if tag == 'ul' and self._in_witnesses:
            self._depth += 1

    def handle_endtag(self, tag):
        if tag == 'li' and self._in_li:
            text = ''.join(self._current).strip()
            if text:
                self.items.append(text)
            self._in_li = False
        if tag == 'ul' and self._in_witnesses:
            self._depth -= 1
            if self._depth <= 0:
                self._in_witnesses = False

    def handle_data(self, data):
        if data.strip().lower() in ('witnesses', 'witness'):
            self._in_witnesses = True
            self._depth = 0
        if self._in_li:
            self._current.append(data)


def _parse_witness_line(line: str) -> Optional[dict]:
    """Parse a single witness line: 'First Last, Role, Organisation'."""
    # Lines look like: "Matthew Vickerstaff, Director General, NISTA"
    # Or: "Tom Scholar, Permanent Secretary, HM Treasury"
    # Or sometimes just: "Jane Smith, HM Treasury" (no role given)
    parts = [p.strip() for p in line.split(',')]
    if len(parts) < 2:
        return None
    name_raw = parts[0]
    name_norm = normalise_name(name_raw)
    if not name_norm or len(name_norm) < 3:
        return None

    if len(parts) == 2:
        role_title = None
        organisation = parts[1]
    else:
        role_title = parts[1]
        organisation = ', '.join(parts[2:])

    return {
        'name_raw': name_raw,
        'name_normalised': name_norm,
        'role_title': role_title,
        'organisation': organisation,
    }


def parse_witnesses_html(
    html: str,
    session_date: str,
    session_title: str,
    session_url: str,
) -> list:
    """Extract witnesses from a PAC session page HTML.

    Returns a list of witness dicts ready for upsert.
    """
    extractor = _ListExtractor()
    extractor.feed(html)

    results = []
    for line in extractor.items:
        parsed = _parse_witness_line(line)
        if not parsed:
            continue
        witness_id = f'{slug(parsed["name_normalised"])}--{session_date}'
        results.append({
            'witness_id': witness_id,
            'name_raw': parsed['name_raw'],
            'name_normalised': parsed['name_normalised'],
            'role_title': parsed['role_title'],
            'organisation': parsed['organisation'],
            'canonical_buyer_id': None,  # resolved at upsert time
            'session_date': session_date,
            'session_title': session_title,
            'session_url': session_url,
        })

    return results


# ── Session listing ───────────────────────────────────────────────────────────

_DATE_RE = re.compile(r'(\d{1,2}\s+\w+\s+\d{4})')
_SESSION_LINK_RE = re.compile(
    r'href="(/work/\d+/oral-evidence/[^"]*)"'
)


def _extract_session_links(html: str, months_back: int = 12) -> list:
    """Return list of (url, date_str, title) for sessions within the window."""
    cutoff = datetime.utcnow() - timedelta(days=months_back * 30)
    results = []

    # Split into blocks around session links — crude but robust without lxml
    blocks = re.split(r'(?=<article|<li class="publication)', html)
    for block in blocks:
        link_m = _SESSION_LINK_RE.search(block)
        if not link_m:
            continue
        path = link_m.group(1)
        url = PAC_BASE + path

        # Extract a date from the block text
        date_m = _DATE_RE.search(block)
        date_str = date_m.group(1) if date_m else None
        session_date = None
        if date_str:
            try:
                session_date = datetime.strptime(date_str, '%d %B %Y').strftime('%Y-%m-%d')
                if datetime.strptime(session_date, '%Y-%m-%d') < cutoff:
                    continue
            except ValueError:
                pass

        # Extract title
        title_m = re.search(r'<h[23][^>]*>([^<]+)</h[23]>', block)
        title = title_m.group(1).strip() if title_m else 'PAC session'

        results.append({'url': url, 'session_date': session_date, 'title': title})

    return results


# ── Canonical buyer resolution ─────────────────────────────────────────────────

def _resolve_buyer(conn, organisation: Optional[str]) -> Optional[str]:
    """Return canonical_buyer_id for an organisation name, or None."""
    if not organisation:
        return None
    q = organisation.strip().lower()
    row = conn.execute(
        'SELECT canonical_id FROM canonical_buyer_aliases WHERE alias_lower = ?', (q,)
    ).fetchone()
    if row:
        return row[0]
    # Partial match — only accept if unique
    rows = conn.execute(
        'SELECT canonical_id FROM canonical_buyers WHERE LOWER(canonical_name) LIKE ? LIMIT 2',
        (f'%{q}%',),
    ).fetchall()
    if len(rows) == 1:
        return rows[0][0]
    return None


# ── DB write ─────────────────────────────────────────────────────────────────

def upsert_witness(conn, record: dict):
    conn.execute(
        '''INSERT OR REPLACE INTO pac_witnesses
           (witness_id, name_raw, name_normalised, role_title, organisation,
            canonical_buyer_id, session_date, session_title, session_url, scraped_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
        (
            record['witness_id'], record['name_raw'], record['name_normalised'],
            record['role_title'], record['organisation'],
            record['canonical_buyer_id'],
            record['session_date'], record['session_title'], record['session_url'],
        ),
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def run(months=12, single_url=None, dry_run=False):
    conn = get_db(DB_PATH)
    init_schema(conn, SCHEMA_PATH)

    if single_url:
        session_urls = [{'url': single_url, 'session_date': None, 'title': 'Single session'}]
    else:
        log.info('Fetching PAC publications index...')
        index_html = _fetch(PAC_PUBLICATIONS)
        if not index_html:
            log.error('Cannot fetch PAC index')
            conn.close()
            return
        session_urls = _extract_session_links(index_html, months_back=months)
        log.info('Found %d sessions in the last %d months', len(session_urls), months)

    total = 0
    for session in session_urls:
        url = session['url']
        log.info('Scraping %s', url)
        html = _fetch(url)
        if not html:
            continue

        witnesses = parse_witnesses_html(
            html,
            session_date=session['session_date'] or 'unknown',
            session_title=session['title'],
            session_url=url,
        )
        log.info('  Found %d witnesses', len(witnesses))

        for w in witnesses:
            w['canonical_buyer_id'] = _resolve_buyer(conn, w['organisation'])
            if not dry_run:
                upsert_witness(conn, w)
            total += 1

        if not dry_run:
            conn.commit()
        time.sleep(1)

    conn.close()
    log.info('Done. Total witness records: %d', total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape PAC witness lists')
    parser.add_argument('--months', type=int, default=12, help='Months of sessions to scrape (default 12)')
    parser.add_argument('--url', help='Scrape a single session URL instead of the full index')
    parser.add_argument('--dry-run', action='store_true', help='Parse but do not write to database')
    args = parser.parse_args()
    run(months=args.months, single_url=args.url, dry_run=args.dry_run)
```

- [ ] **Step 4: Run PAC scraper tests**

```bash
cd pwin-competitive-intel
python agent/tests/test_stakeholder.py TestPACWitnessScraper -v
```

Expected: all 3 tests pass.

- [ ] **Step 5: Smoke test the PAC scraper against the live site**

```bash
cd pwin-competitive-intel
python agent/scrape_pac_witnesses.py --months 3 --dry-run
```

Expected: the script fetches the PAC publications page and prints the number of sessions found and witnesses per session. If the Parliament website has changed its HTML structure since the feasibility investigation, the witness count per session may be 0 — check the raw HTML of one session page and update `_ListExtractor` or `_parse_witness_line` to match the actual structure.

- [ ] **Step 6: Run for real against the last 12 months**

```bash
cd pwin-competitive-intel
python agent/scrape_pac_witnesses.py --months 12
```

Verify:

```bash
python -c "
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
count = conn.execute('SELECT count(*) FROM pac_witnesses').fetchone()[0]
sample = conn.execute('SELECT name_normalised, role_title, organisation, session_date FROM pac_witnesses LIMIT 5').fetchall()
print('Total pac_witnesses:', count)
for r in sample: print(' ', r)
conn.close()
"
```

- [ ] **Step 7: Commit**

```bash
git add pwin-competitive-intel/agent/scrape_pac_witnesses.py
git add pwin-competitive-intel/agent/tests/test_stakeholder.py
git commit -m "feat(stakeholders): PAC witness scraper — html.parser-based, no external deps"
```

---

## Task 5: MCP query functions in competitive-intel.js

**Files:**
- Modify: `pwin-platform/src/competitive-intel.js`

Three new functions: `getStakeholders`, `getStakeholderByName`, `findEvaluators`. All use the existing `_resolveBuyerCanonical` helper and the same `getDb()` pattern as the rest of the file.

- [ ] **Step 1: Write the failing test**

Create `pwin-platform/test/test-stakeholder-mcp.js`:

```javascript
/**
 * Tests for competitive-intel.js stakeholder query functions.
 * Requires a bid_intel.db with at least one stakeholder row.
 * Run after Task 3 has ingested at least one department.
 */

import { getStakeholders, getStakeholderByName, findEvaluators } from '../src/competitive-intel.js';

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  PASS: ${message}`);
    passed++;
  } else {
    console.error(`  FAIL: ${message}`);
    failed++;
  }
}

console.log('\n=== Stakeholder MCP functions ===\n');

// getStakeholders — valid buyer
console.log('getStakeholders("HM Treasury")');
const result1 = getStakeholders('HM Treasury');
assert(!result1.error, 'no error for known buyer');
assert(Array.isArray(result1.stakeholders), 'stakeholders is an array');
if (result1.stakeholders.length > 0) {
  const first = result1.stakeholders[0];
  assert('name_normalised' in first, 'has name_normalised');
  assert('scs_band_inferred' in first, 'has scs_band_inferred');
  assert('job_title' in first, 'has job_title');
}

// getStakeholders — tier filter
console.log('\ngetStakeholders("HM Treasury", { tier: "DirectorGeneral" })');
const result2 = getStakeholders('HM Treasury', { tier: 'DirectorGeneral' });
assert(!result2.error, 'no error with tier filter');
if (result2.stakeholders.length > 0) {
  assert(
    result2.stakeholders.every(s => s.scs_band_inferred === 'DirectorGeneral'),
    'all results match the requested tier'
  );
}

// getStakeholders — unknown buyer
console.log('\ngetStakeholders("XYZZY Unknown Dept")');
const result3 = getStakeholders('XYZZY Unknown Dept');
assert(!result3.error || result3.stakeholders !== undefined, 'returns gracefully for unknown buyer');

// getStakeholderByName
console.log('\ngetStakeholderByName("Gallagher")');
const result4 = getStakeholderByName('Gallagher');
assert(!result4.error, 'no error');
assert('results' in result4, 'has results field');
assert(typeof result4.count === 'number', 'has count field');

// findEvaluators
console.log('\nfindEvaluators("HM Treasury")');
const result5 = findEvaluators('HM Treasury');
assert(!result5.error, 'no error');
assert('pac_witnesses' in result5, 'has pac_witnesses field');
assert(Array.isArray(result5.pac_witnesses), 'pac_witnesses is an array');

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
cd pwin-platform
node test/test-stakeholder-mcp.js 2>&1 | head -10
```

Expected: `SyntaxError` or `TypeError` — the functions don't exist yet.

- [ ] **Step 3: Add the three query functions to `competitive-intel.js`**

Open `pwin-platform/src/competitive-intel.js`. Locate the line:

```javascript
export {
```

(near the end of the file, the export block). Before the export block, add:

```javascript
// ── Stakeholder queries ──────────────────────────────────────────────────────

/**
 * Get senior leadership for a buyer (Director tier and above).
 * @param {string} buyerName  - Buyer name or partial match
 * @param {object} opts
 * @param {string} [opts.tier] - Filter by scs_band_inferred (e.g. 'DirectorGeneral')
 * @param {number} [opts.topN=20] - Max records to return
 */
function getStakeholders(buyerName, { tier = null, topN = 20 } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const resolved = _resolveBuyerCanonical(db, buyerName);
    if (!resolved) {
      return { stakeholders: [], message: `No buyer found matching '${buyerName}'` };
    }
    if (resolved.ambiguous) {
      return { stakeholders: [], ambiguous: true, candidates: resolved.candidates };
    }
    if (!resolved.canonicalId) {
      return { stakeholders: [], message: `No canonical buyer for '${buyerName}'` };
    }

    const tierClause = tier ? ' AND scs_band_inferred = ?' : '';
    const params = tier
      ? [resolved.canonicalId, tier, topN]
      : [resolved.canonicalId, topN];

    const rows = db.prepare(`
      SELECT person_id, name_normalised, job_title, unit, organisation,
             scs_band_inferred, reports_to_post, source, snapshot_date
      FROM stakeholders
      WHERE canonical_buyer_id = ?${tierClause}
      ORDER BY
        CASE scs_band_inferred
          WHEN 'PermanentSecretary' THEN 1
          WHEN 'DirectorGeneral'    THEN 2
          WHEN 'Director'           THEN 3
          WHEN 'DeputyDirector'     THEN 4
          ELSE 5
        END, name_normalised
      LIMIT ?
    `).all(...params);

    return {
      canonical_buyer_id: resolved.canonicalId,
      canonical_buyer_name: resolved.canonicalName,
      count: rows.length,
      stakeholders: rows,
    };
  } finally {
    db.close();
  }
}

/**
 * Look up a named individual across organogram + PAC witness records.
 * @param {string} name - Name or partial name
 */
function getStakeholderByName(name) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const nameLike = `%${(name || '').toLowerCase()}%`;

    const fromOrganograms = db.prepare(`
      SELECT person_id AS id, name_normalised, name_raw, job_title,
             unit, organisation, canonical_buyer_id, scs_band_inferred,
             'organogram' AS source_type, snapshot_date
      FROM stakeholders
      WHERE lower(name_normalised) LIKE ? OR lower(name_raw) LIKE ?
      LIMIT 10
    `).all(nameLike, nameLike);

    const fromPAC = db.prepare(`
      SELECT witness_id AS id, name_normalised, name_raw, role_title AS job_title,
             NULL AS unit, organisation, canonical_buyer_id, NULL AS scs_band_inferred,
             'pac_witness' AS source_type, session_date AS snapshot_date
      FROM pac_witnesses
      WHERE lower(name_normalised) LIKE ? OR lower(name_raw) LIKE ?
      LIMIT 10
    `).all(nameLike, nameLike);

    const combined = [...fromOrganograms, ...fromPAC];
    return { count: combined.length, results: combined };
  } finally {
    db.close();
  }
}

/**
 * Find likely evaluators for a buyer — PAC witnesses (named SROs in sessions).
 * FTS contact names are the planned future addition (not yet extracted from notices).
 * @param {string} buyerName - Buyer name or partial match
 */
function findEvaluators(buyerName) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const resolved = _resolveBuyerCanonical(db, buyerName);
    if (!resolved || !resolved.canonicalId) {
      return {
        evaluators: [],
        pac_witnesses: [],
        message: `No canonical buyer found for '${buyerName}'`,
      };
    }

    const witnesses = db.prepare(`
      SELECT name_normalised, role_title, organisation, session_date, session_title, session_url
      FROM pac_witnesses
      WHERE canonical_buyer_id = ?
      ORDER BY session_date DESC
      LIMIT 20
    `).all(resolved.canonicalId);

    return {
      canonical_buyer_id: resolved.canonicalId,
      canonical_buyer_name: resolved.canonicalName,
      pac_witnesses: witnesses,
      note: 'PAC witnesses are Director-level SROs who have appeared before the Public Accounts Committee. FTS contact names (Grade 7 procurement leads) are the highest-priority future addition — one schema change to extract contactPoint.name from OCDS notices.',
    };
  } finally {
    db.close();
  }
}
```

Then add the three new functions to the export block. Find the existing export:

```javascript
export {
  dbSummary,
```

And add to the list:

```javascript
  getStakeholders,
  getStakeholderByName,
  findEvaluators,
```

- [ ] **Step 4: Run the tests**

```bash
cd pwin-platform
node test/test-stakeholder-mcp.js
```

Expected: all assertions pass (or the PAC witness tests pass with 0 results if `scrape_pac_witnesses.py` hasn't been run yet — that is acceptable). Fix any failures before proceeding.

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/src/competitive-intel.js
git add pwin-platform/test/test-stakeholder-mcp.js
git commit -m "feat(stakeholders): MCP query functions — getStakeholders, getStakeholderByName, findEvaluators"
```

---

## Task 6: MCP tool registration

**Files:**
- Modify: `pwin-platform/src/mcp.js`

Register the three new query functions as MCP tools, following the exact same pattern as `get_buyer_behaviour_profile` and `get_supplier_profile`.

- [ ] **Step 1: Locate the insertion point in `mcp.js`**

Open `pwin-platform/src/mcp.js`. Find the `get_buyer_behaviour_profile` tool registration (around line 1834). The stakeholder tools go immediately after the final competitive-intel tool and before the `// ====` divider that starts the Agent 2 intelligence dossier tools.

- [ ] **Step 2: Add three tool registrations**

After the closing `);` of `get_buyer_behaviour_profile`, add:

```javascript
  server.tool(
    'get_stakeholders',
    'Get senior civil servants (Director tier and above) for a government buyer from the organogram database. Returns names, job titles, SCS bands, and reporting lines. Use to populate the senior-leadership section of buyer intelligence dossiers or Win Strategy stakeholder maps.',
    {
      name: z.string().describe('Buyer name (e.g. "HM Treasury", "Ministry of Defence", "Home Office")'),
      tier: z.string().optional().describe('Filter by seniority band: PermanentSecretary | DirectorGeneral | Director | DeputyDirector'),
      topN: z.number().optional().describe('Max records to return (default 20)'),
    },
    async ({ name, tier, topN }) => {
      const result = compIntel.getStakeholders(name, { tier, topN });
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'get_stakeholder_by_name',
    'Look up a named individual across organogram records and PAC witness lists. Returns matching stakeholders with their current role, organisation, and seniority band.',
    {
      name: z.string().describe('Name or partial name to search for (e.g. "Gallagher", "Tom Scholar")'),
    },
    async ({ name }) => {
      const result = compIntel.getStakeholderByName(name);
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'find_evaluators',
    'Find likely evaluators for a buyer — PAC witnesses who are Director-level SROs. Use when assessing who will evaluate a bid or map stakeholder engagement risk.',
    {
      name: z.string().describe('Buyer name (e.g. "Home Office", "Ministry of Justice")'),
    },
    async ({ name }) => {
      const result = compIntel.findEvaluators(name);
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );
```

- [ ] **Step 3: Verify the MCP server starts without error**

```bash
cd pwin-platform
node src/server.js --mcp 2>&1 | head -5
```

Expected: server starts cleanly (or is killed immediately because it waits on stdin — that is expected in `--mcp` mode). No syntax errors, no `TypeError: compIntel.getStakeholders is not a function`.

- [ ] **Step 4: Verify the tools appear in the MCP tool list**

Start the server in `--both` mode and call the tools:

```bash
node src/server.js --both &
sleep 2
curl -s http://localhost:3456/mcp/tools 2>/dev/null | python -c "
import json, sys
tools = json.load(sys.stdin)
names = [t['name'] for t in tools.get('tools', [])]
for n in ['get_stakeholders', 'get_stakeholder_by_name', 'find_evaluators']:
    print('FOUND' if n in names else 'MISSING', n)
"
kill %1 2>/dev/null
```

Expected:
```
FOUND get_stakeholders
FOUND get_stakeholder_by_name
FOUND find_evaluators
```

If the HTTP endpoint doesn't expose tool list this way, skip this step and rely on the functional test from Task 5.

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/src/mcp.js
git commit -m "feat(stakeholders): register 3 MCP tools — get_stakeholders, get_stakeholder_by_name, find_evaluators"
```

---

## Self-review

**Spec coverage check:**

| Requirement (from action file) | Covered by |
|---|---|
| `stakeholders` table: person_id, name, role_title, grade, salary_band, parent_unit_id, department_canonical_id, snapshot_date, source_url | Task 1 — note: `salary_band` omitted (empty in organograms for Director tier); `parent_unit_id` simplified to `unit` (flat, no unit hierarchy table needed for v1 — the `organisation` column covers sub-org) |
| `stakeholder_history` table | Task 1 |
| Cross-link to `canonical_buyers` | Tasks 1 + 3 — `canonical_buyer_id` in all three tables |
| `get_stakeholder_profile(name \| id)` | `get_stakeholder_by_name` in Tasks 5+6 |
| `search_stakeholders(query, department?, grade?)` | `get_stakeholders` in Tasks 5+6 |
| `get_buyer_senior_leadership(canonical_buyer_id, top_n?)` | `get_stakeholders` with `canonical_buyer_id` lookup via `_resolveBuyerCanonical` |
| `get_unit_org_chart(unit_id, depth?)` | Deferred — requires a `units` hierarchy table not warranted for v1 given the flat organogram structure |
| `get_stakeholder_history(name)` | Deferred — history records are written at upsert time but no dedicated MCP read tool in v1; `get_stakeholder_by_name` surfaces current records; history readable via direct DB query |
| PAC witness layer | Task 4 |
| Wave 1: top-20 priority buyers ingested | PRIORITY_DEPARTMENTS list in Task 3 has 20 entries |
| Twice-yearly refresh cycle | Scripts are re-runnable; no CI wiring in this plan — add to `scheduler.py` as a follow-up |
| `linkedAssets.stakeholderProfileRefs[]` in buyer dossiers | Deferred — buyer-intelligence SKILL.md update is a follow-on session |

**Placeholder scan:** No placeholders — all steps contain complete code.

**Type consistency check:**
- `getStakeholders` in `competitive-intel.js` is exported and registered in `mcp.js` as `compIntel.getStakeholders` — names match.
- `getStakeholderByName` in `competitive-intel.js` is exported and called as `compIntel.getStakeholderByName` — names match.
- `findEvaluators` in `competitive-intel.js` is exported and called as `compIntel.findEvaluators` — names match.
- `parse_organogram_csv` is defined in `ingest_organograms.py` and imported in tests as `from ingest_organograms import parse_organogram_csv` — matches.
- `parse_witnesses_html` is defined in `scrape_pac_witnesses.py` and imported in tests as `from scrape_pac_witnesses import parse_witnesses_html` — matches.

**Known gaps (not bugs — scope decisions):**
- `units` hierarchy table omitted; organograms record unit as a flat string, which is sufficient for v1 dossier use.
- `get_unit_org_chart` MCP tool deferred; not needed until Win Strategy Stage 2 consumes depth-first org chart traversal.
- `get_stakeholder_history` MCP tool deferred; history writes happen but no dedicated read endpoint in v1.
- `linkedAssets.stakeholderProfileRefs[]` buyer-intelligence skill update is a separate follow-on task.
- Adding organogram ingest to `scheduler.py` nightly cron is a follow-on task (twice-yearly is manual; daily cron is unnecessary).
