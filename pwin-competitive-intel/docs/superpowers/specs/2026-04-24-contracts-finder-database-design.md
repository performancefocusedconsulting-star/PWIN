# Contracts Finder Database — Design Spec
**Date:** 2026-04-24
**Product:** pwin-competitive-intel
**Status:** Approved, ready for implementation

---

## Overview

Extend the existing `bid_intel.db` SQLite database to ingest data from the UK Government's **Contracts Finder** portal, complementing the existing Find a Tender Service (FTS) OCDS dataset.

**Why:** FTS covers above-threshold contracts only (~£139k+ for central government). Contracts Finder covers £10k+ (central gov) and £25k+ (other public bodies), including contracts from buyers who never publish on FTS. This fills two gaps simultaneously: the sub-threshold value band and buyers with no FTS presence at all.

**Scope:** Full Contracts Finder ingest — both opportunity/tender notices and contract award notices — with historical backfill from 2021-01-01 to match FTS depth, plus nightly incremental updates.

---

## Approach

**Unified tables, source-tagged (Approach A).**

All existing tables (`notices`, `awards`, `buyers`, `suppliers`) gain a `data_source` column. FTS rows are `'fts'`; CF rows are `'cf'`. Existing views, MCP tools, and queries automatically span both sources with no changes to the query layer.

---

## Section 1: Schema Changes

### New column on four tables

Added via the existing `_migrate_schema()` migration pattern in `db_utils.py` (safe to re-run, guarded by `PRAGMA table_info`):

```sql
ALTER TABLE notices   ADD COLUMN data_source TEXT DEFAULT 'fts';
ALTER TABLE awards    ADD COLUMN data_source TEXT DEFAULT 'fts';
ALTER TABLE buyers    ADD COLUMN data_source TEXT DEFAULT 'fts';
ALTER TABLE suppliers ADD COLUMN data_source TEXT DEFAULT 'fts';
```

All 175k+ existing rows automatically get `data_source = 'fts'` via the DEFAULT. No data migration script needed.

### One new CF-specific column

```sql
ALTER TABLE notices ADD COLUMN suitable_for_sme INTEGER DEFAULT 0;
```

Contracts Finder publishes an explicit SME-suitability flag with no FTS equivalent. Useful PWIN signal: SME-friendly contracts typically have lower competition from large primes. FTS rows default to 0 (unknown).

### New indexes

```sql
CREATE INDEX IF NOT EXISTS idx_notices_source ON notices(data_source);
CREATE INDEX IF NOT EXISTS idx_awards_source  ON awards(data_source);
```

### Primary key conventions for CF rows

| Table | CF key pattern | Example |
|---|---|---|
| `notices` (`ocid`) | `cf-<systemId>` | `cf-12345678` |
| `buyers` (`id`) | `cf-buyer-<orgId>` | `cf-buyer-9001` |
| `suppliers` (`id`) | `cf-sup-<hash>` | `cf-sup-a3f9b2` |
| `awards` (`id`) | `cf-award-<noticeId>` | `cf-award-12345678` |

Hash for supplier ID is a short hex digest of `name + (postcode or '')`, avoiding collisions with FTS IDs while remaining deterministic (idempotent re-runs). Postcode may be absent in CF data; fall back to name-only hash in that case.

---

## Section 2: Shared DB Utilities (`agent/db_utils.py`)

Currently the upsert functions are inlined in `ingest.py`. Extract them into a new shared module so both `ingest.py` (FTS) and `ingest_cf.py` (CF) call the same code.

### Functions to extract

| Function | Notes |
|---|---|
| `get_db(path)` | Open connection, set WAL + FK |
| `init_schema(conn, schema_path)` | Run schema.sql + `_migrate_schema()` |
| `_migrate_schema(conn)` | All ALTER TABLE migrations live here |
| `upsert_buyer(conn, d)` | `d` must include `data_source` |
| `upsert_supplier(conn, d)` | `d` must include `data_source` |
| `upsert_notice(conn, d)` | `d` must include `ocid`, `data_source` |
| `upsert_lot(conn, d)` | Unchanged |
| `upsert_award(conn, d)` | `d` must include `data_source` |
| `link_award_supplier(conn, award_id, supplier_id)` | Unchanged |
| `upsert_cpv(conn, ocid, codes)` | Unchanged |

`ingest.py` becomes: `from db_utils import get_db, init_schema, upsert_buyer, ...` — its FTS-specific parse logic is untouched. `DB_PATH` and `SCHEMA_PATH` stay as constants in each agent so they can be overridden for testing.

---

## Section 3: CF Ingest Agent (`agent/ingest_cf.py`)

### API

Contracts Finder exposes a public POST-based search API (no API key required):

```
POST https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedSearchApi/Search
Content-Type: application/json

{
  "publishedFrom": "2026-04-01T00:00:00",
  "publishedTo":   "2026-04-24T23:59:59",
  "size": 100,
  "page": 1
}
```

Pagination is page-number-based (not cursor-based like FTS).

### Ingest state

Stored in the existing `ingest_state` table under key `cf_last_date`. Incremental runs query `cf_last_date → now`. On completion, `cf_last_date` advances to the last successfully processed notice's `publishedDate`.

The backfill (`--from 2021-01-01`) processes month-by-month windows to keep individual API responses manageable and allow resumption after failure.

### Parse → normalise → upsert flow

```
CF API response (page of notices)
  └─ notice['buyerOrganisation']     → upsert_buyer(conn, {..., data_source='cf'})
  └─ notice['suppliers']             → upsert_supplier(conn, {..., data_source='cf'})
  └─ notice (tender/opportunity)     → upsert_notice(conn, {
                                           ocid=f"cf-{notice['id']}",
                                           data_source='cf',
                                           suitable_for_sme=notice.get('suitableForSme', 0),
                                           ...
                                       })
  └─ if award notice:                → upsert_award(conn, {
                                           id=f"cf-award-{notice['id']}",
                                           ocid=f"cf-{notice['id']}",
                                           data_source='cf',
                                           ...
                                       })
                                       link_award_supplier(conn, award_id, supplier_id)
  └─ notice['cpvCodes']              → upsert_cpv(conn, f"cf-{notice['id']}", codes)
```

### CF → schema field mapping

| CF field | Schema column | Notes |
|---|---|---|
| `id` / `systemId` | `ocid` = `'cf-' + id` | |
| `title` | `title` | |
| `description` | `description` | |
| `publishedDate` | `published_date` | |
| `deadlineDate` | `tender_end_date` | |
| `value.amount` | `value_amount` | |
| `status` | `tender_status` | Normalise to FTS values where possible |
| `type` | `notice_type` | e.g. `ContractNotice`, `ContractAwardNotice` |
| `contractStart` | `contract_start_date` | |
| `contractEnd` | `contract_end_date` | |
| `awardedDate` | `award_date` on award row | |
| `awardedValue` | `value_amount` on award row | |
| `suitableForSme` | `suitable_for_sme` | CF-specific |
| `buyerOrganisation.id` | `buyer_id` = `'cf-buyer-' + org_id` | |
| `suppliers[].companiesHouseNumber` | `suppliers.companies_house_no` | Enables CH enrichment |
| `cpvCodes[]` | `cpv_codes` table | Same structure as FTS |

### Rate limiting and error handling

- 1 second between pages (same politeness as FTS)
- Exponential backoff on 429 / 5xx (same pattern as FTS)
- Page-level failure: log and skip; don't advance `cf_last_date` past a failed window
- No read timeout concern (POST responses are fast)

### CLI flags

```bash
python ingest_cf.py                    # incremental from cf_last_date
python ingest_cf.py --from 2021-01-01  # backfill from date
python ingest_cf.py --limit 500        # cap releases (testing)
```

---

## Section 4: Scheduler + GitHub Actions

### `scheduler.py` — updated run order

```
1. python ingest.py       (FTS incremental)   — non-negotiable, exit non-zero on failure
2. python ingest_cf.py    (CF incremental)    — log failure, continue (non-fatal for v1)
3. python enrich-ch.py    (CH enrichment)     — unchanged
```

CF failure is logged but does not cause the scheduler to return a non-zero exit code. This keeps the nightly run stable while CF is new and potentially flaky.

### `.github/workflows/ingest.yml` — new step

```yaml
- name: CF incremental ingest
  run: python pwin-competitive-intel/agent/ingest_cf.py
  continue-on-error: true
```

Placed between the existing FTS ingest step and the CH enrichment step. `continue-on-error: true` matches the non-fatal policy above.

No new secrets — Contracts Finder is a public API.

### `queries.py` — `summary` command update

The `summary` command gains a per-source breakdown row:

```
Source    Notices    Awards    Buyers    Suppliers
fts       174,823   186,241   24,103    161,119
cf         38,412    21,005    9,817     14,203
total     213,235   207,246   33,920    175,322
```

All other query commands (`buyer`, `supplier`, `expiring`, `pwin`, `awards`, `pipeline`, `cpv`) span both sources automatically — no changes needed because the views don't filter on `data_source`.

---

## What this unlocks

| Intelligence use case | Before | After |
|---|---|---|
| Sub-threshold contracts (£10k–£139k) | Blind | Full coverage |
| Buyers who only publish on CF | Missing entirely | Profiled |
| Supplier win history (small contracts) | Incomplete | Complete |
| SME-friendly contract signals | Not available | `suitable_for_sme` flag on notices |
| Expiry pipeline | Above-threshold only | Full value range |
| Buyer behaviour (procurement method, competition) | Above-threshold only | Full range |

---

## Out of scope for this iteration

- Resolving CF buyers against the canonical buyer layer (same playbook as FTS raw buyers — name-match pass deferred to canonical layer v2)
- CF supplier deduplication via Splink (extends naturally from existing supplier dedup pipeline)
- D1 sync of CF data (deferred alongside FTS D1 deploy)
- `suitable_for_sme` signal surfaced in MCP tools (deferred — add to `get_buyer_profile` / `get_supplier_profile` once data volume justifies it)
