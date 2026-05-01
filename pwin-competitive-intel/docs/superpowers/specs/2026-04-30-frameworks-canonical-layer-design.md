# Frameworks Canonical Layer — Design Specification

**Date:** 2026-04-30
**Project:** pwin-competitive-intel
**Status:** Approved — ready for implementation planning

---

## Overview

A searchable index of UK government procurement frameworks, built into the existing competitive intelligence product. Frameworks are the pre-agreed routes that public sector buyers use to purchase services — Crown Commercial Service agreements, NHS procurement hub frameworks, local government buying organisation frameworks, and departmental frameworks. Today, no central searchable index exists. Buyer and supplier dossiers cannot reliably name the correct route to market; the Defence Digital v3.0 dossier missed every named framework it should have found.

This product closes that gap. It is three things sharing one data foundation:

1. **A directory** — visual, searchable, factual. A place to understand the whole framework landscape at a glance, with volume and value data showing which frameworks are most commercially significant.
2. **An intelligence layer** — factual data on which buyers route spend through which frameworks, and where suppliers hold approved positions. Feeds the buyer dossier, supplier dossier, and win strategy skills automatically.
3. **A platform asset** — AI tools that any downstream product or skill can reach into to enrich context.

---

## Architecture

Lives entirely within `pwin-competitive-intel/`. No new product, no new server, no new database file.

### Components

| Component | Location | Purpose |
|---|---|---|
| Schema migration | `db/schema.sql` | Four new tables added to `bid_intel.db` |
| Catalogue ingest | `agent/ingest_frameworks_catalogue.py` | Top-down pull from CCS and other published catalogues |
| Call-off mining | `agent/mine_framework_calloffs.py` | Bottom-up extraction from existing contracts data |
| Consolidation | `agent/consolidate_frameworks.py` | Merges both lists, flags gaps, produces report |
| Dashboard tab | `dashboard.html` | "Frameworks" tab, existing visual style |
| AI tools | `pwin-platform/src/competitive-intel.js` | Five new MCP tools |

### Two-pipeline ingest strategy

The design uses both a top-down catalogue pull and a bottom-up contracts data mine, then consolidates them. The comparison gap is itself intelligence: frameworks that appear in call-offs but not the catalogue are typically departmental frameworks (MoD's TEPAS 2, DIPS, MVDS) that no central catalogue publishes. Frameworks in the catalogue but with no call-offs in the database are either new, genuinely unused, or represent coverage gaps.

### Refresh cadence

- Catalogue ingest: monthly (new frameworks awarded, old ones expire) — wired into `agent/scheduler.py` as a monthly step alongside the existing nightly pipeline
- Call-off mining: nightly, wired into the existing ingest pipeline — new contracts land in the database and automatically link to frameworks

---

## Database Schema

Four new tables added to `bid_intel.db`.

### `frameworks`

One row per framework. The master record.

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `reference_no` | TEXT UNIQUE | e.g. RM6116 for CCS frameworks |
| `name` | TEXT NOT NULL | Full name |
| `short_name` | TEXT | Abbreviated name for display |
| `owner` | TEXT NOT NULL | e.g. "Crown Commercial Service", "NHS SBS", "ESPO" |
| `owner_type` | TEXT | `central_gov`, `nhs`, `local_gov`, `departmental`, `devolved` |
| `category` | TEXT | technology, professional_services, facilities, construction, etc. |
| `sub_category` | TEXT | |
| `description` | TEXT | |
| `max_value` | REAL | Ceiling, not realised spend — always displayed as ceiling |
| `start_date` | TEXT | ISO date |
| `expiry_date` | TEXT | ISO date |
| `status` | TEXT | `active`, `expiring_soon`, `expired`, `replaced` |
| `replacement_framework_id` | INTEGER FK | Pointer to successor framework |
| `eligible_buyer_types` | TEXT | JSON array: `["central_gov", "nhs", "local_gov"]` |
| `route_type` | TEXT | `framework_agreement`, `dps`, `approved_list` |
| `lot_count` | INTEGER | |
| `supplier_count` | INTEGER | |
| `call_off_count` | INTEGER | Populated from call-off mining |
| `call_off_value_total` | REAL | Populated from call-off mining |
| `first_call_off_date` | TEXT | |
| `last_call_off_date` | TEXT | |
| `source` | TEXT | `catalogue_only`, `contracts_only`, `both` — the gap-analysis field |
| `source_url` | TEXT | |
| `last_updated` | TEXT | |

`expiring_soon` = expiry within 12 months. Frameworks in this status are strategically important — a replacement competition is likely.

### `framework_lots`

One row per lot within a framework. Most frameworks are divided into lots representing distinct scopes or service areas.

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `framework_id` | INTEGER FK | |
| `lot_number` | TEXT | e.g. "1", "2a" |
| `lot_name` | TEXT | |
| `scope` | TEXT | |
| `max_value` | REAL | Lot-level ceiling |
| `supplier_count` | INTEGER | |

### `framework_suppliers`

One row per supplier per lot. Records who holds an approved position and whether they are actually winning work through it.

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `framework_id` | INTEGER FK | |
| `lot_id` | INTEGER FK | |
| `supplier_canonical_id` | INTEGER | Links to canonical suppliers table |
| `supplier_name_raw` | TEXT | Original name as published |
| `awarded_date` | TEXT | |
| `status` | TEXT | `active`, `suspended`, `withdrawn` |
| `call_off_count` | INTEGER | Actual call-offs, not just position |
| `call_off_value` | REAL | |

The gap between holding a position and having call-off activity is strategically significant. A supplier on a framework with no call-offs may be dormant or building quietly.

### `framework_call_offs`

One row per contract that routes through a framework. Bridges the existing contracts data to the frameworks layer.

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `framework_id` | INTEGER FK | |
| `lot_id` | INTEGER FK | NULL where lot not determinable |
| `notice_ocid` | TEXT | Links to `notices` table |
| `supplier_canonical_id` | INTEGER | |
| `buyer_canonical_id` | INTEGER | |
| `sub_org_canonical_id` | INTEGER | Where available — supports sub-org visibility |
| `value` | REAL | |
| `awarded_date` | TEXT | |
| `contract_title` | TEXT | |
| `match_method` | TEXT | `reference_no`, `name_fuzzy`, `inferred` |
| `match_confidence` | REAL | 0.0–1.0. Low-confidence links flagged for review |

The sub-organisation field makes this a third route into the sub-organisation visibility problem for MoD and other publish-at-parent departments, alongside the £25k spend transparency feed.

---

## Ingest Pipeline

### Step 1 — Catalogue ingest (`agent/ingest_frameworks_catalogue.py`)

Pulls from published catalogues, top-down. Sources in priority order:

**Crown Commercial Service** (`crowncommercial.gov.uk/agreements`)
The most structured source. Each CCS agreement page lists: reference number, name, lot breakdown, approved suppliers per lot, eligible buyer categories, and expiry date. Covers the majority of central government technology and professional services spend.

**NHS procurement hubs**
- NHS Shared Business Services
- NHS London Procurement Partnership
- NHS Supply Chain

Less structured than CCS but parseable. Each hub publishes a framework catalogue.

**Local government buying organisations**
- ESPO, YPO, NEPO, TPPL

Variable structure — some have well-maintained catalogues, others publish PDFs. Parser functions handle each source separately.

**Departmental frameworks**
MoD (TEPAS 2, DIPS, MVDS, MCF 4, DDAD), Home Office, HMRC, and others. These are the hardest to automate — often in procurement portals or published inconsistently. For Wave 1, these are populated primarily from Step 2 (call-off mining) rather than scraped directly. Skeleton records created; enriched manually where needed.

Each source has its own parser function within the script. The script is idempotent — re-running updates existing records rather than creating duplicates.

### Step 2 — Call-off mining (`agent/mine_framework_calloffs.py`)

Queries the existing `notices`, `awards`, and related tables for framework references:

**Signal 1 — Reference number patterns**
Strings matching known framework reference formats (RM-prefixed CCS references, departmental equivalents) in notice titles, descriptions, and structured fields. High confidence.

**Signal 2 — Framework name mentions**
Known framework names in free-text fields. Lower confidence, flagged as `name_fuzzy` in `match_method`.

For each match:
- Creates a `framework_call_offs` record linking the award to the framework
- If the framework is not yet in the `frameworks` table, creates a skeleton record with `source = 'contracts_only'`
- Updates summary counts (`call_off_count`, `call_off_value_total`, date range) on the framework record

### Step 3 — Consolidation (`agent/consolidate_frameworks.py`)

Merges the two lists:

1. **Exact reference number match** — highest confidence. Merges catalogue record with contracts-mined data.
2. **Name similarity match** — for frameworks without a reference number in both sources. Fuzzy matching with a confidence threshold; matches below the threshold are flagged for human review rather than auto-merged.
3. **No match** — record stays single-source, flagged.

Produces a consolidation report written to `db/framework_consolidation_report.json`:
- Count of catalogue-only, contracts-only, and matched records
- List of contracts-only frameworks (the departmental gap list)
- List of catalogue-only frameworks with zero call-offs (coverage or usage gaps)
- Low-confidence name matches requiring review

---

## Dashboard Tab

A "Frameworks" tab added to `dashboard.html`, consistent with the existing Midnight Executive visual style.

### Summary bar

Four headline numbers: total frameworks indexed, active frameworks, frameworks expiring within 12 months (amber flag — replacement competitions likely), total annual call-off value across all frameworks in the database.

### Main directory table

Searchable, filterable table of every framework. Columns: reference number, name, owner, category, status (amber badge for expiring soon), approved supplier count, call-off count, total call-off value. Default sort: call-off value descending — most commercially significant frameworks first.

Filters: owner type, category, status, free-text search on name or reference number.

### Framework detail panel

Clicking any framework opens a detail panel. Five sections:

**Overview**
Description, reference number, owner, eligible buyer types, route type, value ceiling (labelled as ceiling), start and expiry dates, replacement framework link if applicable. Source flag shown where `contracts_only` or `catalogue_only` — signals data completeness.

**Lots**
Table of lots: lot number, name, scope, value ceiling, supplier count.

**Suppliers on this framework**
Ranked by call-off value. Shows approved position holders and their actual call-off activity. Suppliers with a position but zero call-offs are flagged — approved but not active.

**Buyers using this framework**
Which organisations route spend through it, ranked by value. Lot-level breakdown where available.

**Recent call-offs**
Last 20 contracts placed through this framework: buyer, supplier, value, date.

### Gap flags

- `contracts_only` frameworks: small indicator prompting enrichment from catalogue sources
- `catalogue_only` frameworks with zero call-offs: flagged as either genuinely unused or a coverage gap

---

## AI Tools

Five new tools added to `pwin-platform/src/competitive-intel.js`, available to all intelligence skills via the MCP server.

### `get_framework_profile(framework_id | reference_no | name)`

Returns the full framework record for a named or referenced framework. Used by buyer and supplier dossiers when describing a specific framework in detail.

### `search_frameworks(query, owner_type?, category?, status?, expiry_window?)`

Finds frameworks matching a query. Parameters: free-text search, owner type, category, status, and expiry window (e.g. "expiring within 18 months"). Returns a ranked list. Used by win strategy to identify routes to market for a pursuit.

### `get_buyer_framework_usage(buyer_canonical_id)`

Returns which frameworks a buyer routes spend through, ranked by value, with call-off counts, value totals, and lot-level breakdown where available. Replaces narrative inference in the buyer dossier's `procurementBehaviour.frameworkUsage` field with factual data.

### `get_supplier_framework_position(supplier_canonical_id)`

Returns every framework a supplier holds a position on, which lots, their status, and their actual call-off volume through each. Surfaces the gap between approved position and active call-off activity.

### `get_framework_call_offs(framework_id, buyer?, supplier?, since?)`

Returns individual contracts placed through a framework, with optional filters. Used when a skill needs to cite specific evidence.

---

## Done When

- Top-50 frameworks ingested by call-off value (CCS technology and professional services + NHS hub frameworks + the major MoD-specific frameworks: DIPS, TEPAS 2, MVDS, MCF 4, DDAD)
- Framework reference numbers populated so call-off joins work cleanly
- All five MCP tools live and tested
- Buyer dossier produces `procurementBehaviour.frameworkUsage` from the layer rather than from narrative inference
- Defence Digital test dossier names TEPAS 2, Tech Services 3 (RM6100), Network Services 3 (RM6116), MVDS, DIPS, and MCF 4 with reference numbers and call-off counts
- Consolidation report produced and reviewed — departmental gap list understood
- Dashboard Frameworks tab live and usable

---

## Decisions Not Made Here

- **Whether to build scrapers for every catalogue source in Wave 1, or start with CCS only and add others incrementally.** Recommend CCS first given its structure; NHS and local gov buying organisations in Wave 2.
- **Threshold for auto-merging name-fuzzy matches during consolidation.** To be set empirically after the first consolidation run.
- **Whether departmental frameworks (MoD, Home Office) get their own dedicated scrapers or are populated exclusively from call-off mining.** Depends on how much structure their procurement portals expose. Treat as Wave 2 unless the portals are obviously parseable.
