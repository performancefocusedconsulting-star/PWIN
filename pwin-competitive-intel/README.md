# PWIN Competitive Intelligence

Internal-only intelligence database of UK public sector procurement,
built on the Find a Tender Service (FTS) OCDS open data and Companies House.

## Role within the platform

This is an **internal enrichment asset**, not a customer-facing product.
It exists to feed the other PWIN products with credible procurement
intelligence:

- **[[bidequity-verdict/docs/BidEquity-Verdict-PRD-v2|Verdict]]** — incumbent detection, supplier history, buyer relationships
  for post-loss forensics
- **Win Strategy** — competitor profiling, framework holders, parent groups
- **[[pwin-bid-execution/docs/methodology_gold_standard|Bid Execution]]** — incumbent flags, comparable awards, buyer patterns
  during bid production
- **[[pwin-qualify/content/README|Qualify]] (paid tier, future)** — buyer signals and competition intensity
  injected into AI assurance reviews

The **public Qualify lead-gen experience does NOT call this layer**.
A free public lookup tool was considered and consciously declined; the
data here is for internal product enrichment only.

## What's in the database

- **5+ years** of UK procurement data (Jan 2021 → present)
- ~175k contract notices, ~24k buyers, ~161k suppliers, ~186k awards
- Lots, CPV categorisation, supplier↔award many-to-many, planning notices
- Companies House enrichment available for suppliers with valid CH numbers

Data is loaded by two complementary mechanisms (see *Ingestion* below):

1. **OCP bulk file** — weekly-refreshed JSONL covering Jan 2021 → present.
   The canonical path for historical depth and weekly catch-up.
2. **Live FTS API** — incremental cursor-based pulls. Used to keep current
   between OCP refreshes and to capture forward-pipeline planning notices
   (which the OCP compiled-release file does not contain as standalone records).

## Setup

```bash
# No external dependencies — uses Python stdlib only
python --version   # 3.9+ required

# Quick smoke test (50 records via the live API)
python agent/ingest.py --limit 50
```

## Ingestion

There are two ingest paths and they complement each other.

### 1. OCP bulk import (canonical for historical depth)

The Open Contracting Partnership Data Registry publishes a weekly-refreshed
bulk file of every UK FTS release as OCDS *compiled* releases — one merged
current-state record per contract OCID. Coverage is January 2021 to present.

```bash
# One-off download (~200 MB gzipped, ~175k compiled releases)
mkdir -p data
curl -L -o data/ocp-uk-fts.jsonl.gz \
  "https://data.open-contracting.org/en/publication/41/download?name=full.jsonl.gz"

# Import into the local SQLite database
python agent/import_ocp.py                  # full import (~4 minutes)
python agent/import_ocp.py --limit 1000     # bounded (testing)
python agent/import_ocp.py --file <path>    # custom input file
```

The import is **idempotent** — every upsert is keyed on OCID / party ID,
so re-running after the OCP file refreshes is safe and just updates the
existing rows. Re-pull the JSONL whenever you want the latest snapshot.

The `data/` directory is gitignored — the bulk file stays local.

> **Note on planning notices:** OCP compiled releases do not represent
> pure forward-pipeline planning notices as standalone records (those
> only exist in the live release-package format). The OCP import never
> writes to the `planning_notices` table. Forward pipeline data flows
> exclusively from the live API path below.

### 2. Live FTS API (incremental keep-current)

Incremental cursor-based pulls from the FTS OCDS API. This is what the
nightly job runs to stay current between OCP refreshes and to capture
new forward-pipeline planning notices.

```bash
# Incremental from saved cursor (default — what the nightly cron runs)
python agent/ingest.py

# From a specific date
python agent/ingest.py --from 2026-01-01T00:00:00

# Bounded for testing
python agent/ingest.py --limit 50
```

The cursor advances only on the high-water mark of releases actually
processed. If a run dies mid-flight (network issue, container restart),
the cursor stays put and the next run picks up from where it stopped.
Read timeouts are caught and retried with exponential backoff.

#### Resumable backfill mode

For long backfills directly against the FTS API (rare — prefer the OCP
bulk path for history), there's a separate state machine that persists
the API's `links.next` cursor URL between runs:

```bash
python agent/ingest.py --backfill 2024-01-01T00:00:00 --max-pages 50
python agent/ingest.py --resume --max-pages 50
python agent/ingest.py --resume                            # run to completion
```

Backfill mode does NOT touch the incremental cursor — the two state
machines are fully independent.

## Dashboard

```bash
python server.py
# Open http://localhost:8765/dashboard.html
# In Codespace: use the Ports tab → port 8765
```

Six views: Summary, Buyer Intelligence, Supplier Intelligence,
Expiry Pipeline, Forward Pipeline, PWIN Signals.

Click any row in the pipeline views to expand full description and notice link.
Supplier profiles include Companies House panel when enriched.

## Companies House Enrichment

```bash
# Register free at: https://developer.company-information.service.gov.uk/
export COMPANIES_HOUSE_API_KEY=your_key_here

python agent/enrich-ch.py --limit 100   # test with 100
python agent/enrich-ch.py               # enrich all unenriched suppliers
python agent/enrich-ch.py --refresh     # re-enrich all
```

Adds to each supplier: company status, type, incorporation date, SIC codes,
registered address, directors (current), parent company (from PSC data),
and a link to the Companies House register.

## Queries

```bash
python queries/queries.py summary
python queries/queries.py buyer "Ministry of Defence"
python queries/queries.py supplier "Serco"
python queries/queries.py expiring --days 180 --value 500000
python queries/queries.py pipeline --buyer "Ministry of Justice"
python queries/queries.py awards --value 1000000
python queries/queries.py pwin --buyer "Home Office"
python queries/queries.py cpv 79410000
```

## Scheduling

### GitHub Actions (recommended)
`.github/workflows/ingest.yml` runs nightly at 02:00 UTC:
1. FTS incremental ingest
2. Companies House enrichment (200 suppliers/night)
3. D1 sync to Cloudflare

Requires GitHub secrets:
- `COMPANIES_HOUSE_API_KEY` — free key from developer.company-information.service.gov.uk
- `CLOUDFLARE_API_TOKEN` — for D1 sync
- `CLOUDFLARE_ACCOUNT_ID` — for D1 sync

### Cron (local / server)
```bash
0 2 * * * cd /path/to/pwin-competitive-intel && python agent/scheduler.py >> logs/ingest.log 2>&1
```

## Cloudflare D1 Deployment

> **Status: descoped from immediate priority.** The D1 deploy was
> originally driven by production Qualify needing intel access.
> Public Qualify is shipping deliberately under-enriched (no intel
> injection), so D1 is no longer urgent. It will become relevant
> again when the paid Qualify tier or another internal product
> starts consuming intel from a production environment.
>
> Before deploying, two things need verification:
> 1. The current SQLite database is ~570 MB (14× the size when D1
>    was first specced). Confirm `wrangler d1 execute` can load a
>    DB of that size without hitting batch / execution-time limits.
>    The free tier permits 5 GB storage so the data fits, but the
>    *load mechanism* needs validation.
> 2. The free tier permits 5M reads/day. Model expected production
>    traffic before going live.

One-time setup, when ready:

```bash
cd workers
npx wrangler d1 create pwin-competitive-intel
# Paste database_id into wrangler.toml

npx wrangler d1 execute pwin-competitive-intel --file=../db/schema.sql
python ../agent/sync-d1.py --apply
npx wrangler deploy
```

## Database

SQLite at `db/bid_intel.db`. Schema:

| Table              | Contents                                                  |
|--------------------|-----------------------------------------------------------|
| `buyers`           | Contracting authorities — name, type, region, contact     |
| `suppliers`        | Companies — name, scale, VCSE + 13 Companies House fields |
| `notices`          | Contracting processes (one per OCID) — tender details     |
| `lots`             | Individual lots within a notice                           |
| `awards`           | Awards — value, dates, status, linked to lots             |
| `award_suppliers`  | Many-to-many: which suppliers won which awards            |
| `cpv_codes`        | Normalised CPV codes per notice (indexed for search)      |
| `planning_notices` | Forward pipeline — fed by live API only                   |
| `ingest_state`     | Incremental cursor + backfill resume URL                  |

The 13 Companies House columns on `suppliers` (`ch_status`, `ch_directors`,
`ch_sic_codes`, `ch_parent`, `ch_turnover`, etc.) are populated by
`agent/enrich-ch.py`. The structured CH number itself
(`companies_house_no`) is recovered at ingest time by `_extract_coh()`,
which handles three real-world cases: spec-compliant `GB-COH`-tagged
identifiers, schemeless identifiers whose value matches the CH number
format (a common publisher omission), and the same in `additionalIdentifiers`.
Values are validated in all paths to reject foreign registers
(e.g. German HRB numbers) that publishers sometimes mis-tag as `GB-COH`.

Pre-built views:

| View                    | Purpose                                           |
|-------------------------|---------------------------------------------------|
| `v_expiring_contracts`  | Awards with contracts ending in next 365 days     |
| `v_supplier_wins`       | Supplier win history with buyer context            |
| `v_buyer_history`       | Buyer procurement history with suppliers           |
| `v_pwin_signals`        | Competition level and procurement method breakdown |

## Data sources

**Open Contracting Partnership Data Registry — UK Find a Tender publication.**
Bulk JSONL of OCDS compiled releases, refreshed weekly, covering January
2021 to present. Free, no auth, Open Government Licence v3.0.
URL: <https://data.open-contracting.org/en/publication/41>

**Find a Tender Service OCDS API** (Cabinet Office, Open Government Licence).
Used for incremental keep-current and forward-pipeline planning notices:
- Planning notices and market engagement (forward pipeline) — exclusive to this path
- Tender notices (live opportunities)
- Contract award notices (who won, at what value, how many bidders)
- Contract detail notices (signed contracts with dates)

**Companies House API** (Companies House, Open Government Licence).
- Company status, type, incorporation date
- Directors (current), persons of significant control
- SIC codes, registered address
- Accounts filing dates

**Not yet integrated:** Contracts Finder (below-threshold contracts),
KPI data, delivery performance, contract modifications post-award.

## Known limitations

- **Buyer entity resolution.** Large public sector buyers often appear
  as many distinct rows in the database. Ministry of Defence currently
  fragments across ~1,272 buyer IDs (multiple PPON identifiers, legacy
  GB-FTS IDs, case variants, MoD subsidiaries like DE&S / DSTL / DIO).
  Aggregated queries for big buyers must currently use a name-based
  LIKE join across all variants. A canonical-buyer mapping layer is
  the next planned data-quality improvement.

- **Companies House coverage.** ~27% of suppliers in the database have
  a Companies House number on file. The remainder are split between
  publisher name-only entries (no structured ID), GB-PPON-only entries,
  non-UK entities, and public sector bodies acting as suppliers
  (NHS trusts, universities, etc.). Recovering the name-only suppliers
  requires fuzzy matching against the Companies House register —
  planned but not yet built.

- **Framework values.** OCDS records framework agreement *maximum*
  values, not realised spend. Total-value summaries reflect ceilings,
  not actual contract draw-down.
