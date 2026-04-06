# PWIN Competitive Intelligence

Automated competitive intelligence database built on the UK
Find a Tender Service (FTS) OCDS open data API and Companies House.

## What it does

- **FTS ingest agent** — pulls all UK public sector procurement notices
  nightly via the FTS OCDS API (Cabinet Office, Open Government Licence)
- **Companies House enrichment** — enriches supplier records with company
  status, directors, SIC codes, parent company, accounts data
- **Structured database** — buyers, suppliers, awards, lots, CPV codes,
  planning notices with full relationship mapping
- **Dashboard** — 6-tab web interface for browsing buyer profiles, supplier
  intelligence, expiry pipeline, forward pipeline, and PWIN signals
- **Platform integration** — MCP tools and Data API endpoints feed intelligence
  into Qualify AI reviews and Win Strategy
- **Cloudflare deployment** — D1 serverless SQLite + Worker for live product access

## Setup

```bash
# No external dependencies — uses Python stdlib only
python --version   # 3.9+ required

# Quick test (50 releases)
python agent/ingest.py --limit 50

# Ingest from a specific date
python agent/ingest.py --from 2026-01-01T00:00:00

# Full historical ingest from 2024
python agent/ingest.py --full
```

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

One-time setup for live product access:

```bash
cd workers
npx wrangler d1 create pwin-competitive-intel
# Paste database_id into wrangler.toml

npx wrangler d1 execute pwin-competitive-intel --file=../db/schema.sql
python ../agent/sync-d1.py --apply
npx wrangler deploy
```

Worker URL: `https://pwin-competitive-intel.performancefocusedconsulting.workers.dev`

The live Qualify app auto-detects environment and calls the Worker
when running on production, localhost when in development.

## Database

SQLite at `db/bid_intel.db`. Schema:

| Table              | Contents                                                |
|--------------------|---------------------------------------------------------|
| `buyers`           | Contracting authorities — name, type, region, contact   |
| `suppliers`        | Companies — name, COH no., scale, VCSE + 13 CH fields  |
| `notices`          | Contracting processes (one per OCID) — tender details   |
| `lots`             | Individual lots within a notice                         |
| `awards`           | Awards — value, dates, status, linked to lots           |
| `award_suppliers`  | Many-to-many: which suppliers won which awards          |
| `cpv_codes`        | Normalised CPV codes per notice (indexed for search)    |
| `planning_notices` | Forward pipeline — market engagement, future tenders    |
| `ingest_state`     | Cursor for incremental ingestion                        |

Pre-built views:

| View                    | Purpose                                           |
|-------------------------|---------------------------------------------------|
| `v_expiring_contracts`  | Awards with contracts ending in next 365 days     |
| `v_supplier_wins`       | Supplier win history with buyer context            |
| `v_buyer_history`       | Buyer procurement history with suppliers           |
| `v_pwin_signals`        | Competition level and procurement method breakdown |

## Data sources

**Find a Tender Service OCDS API** (Cabinet Office, Open Government Licence).
Covers all UK public sector contracts published via FTS:
- Planning notices and market engagement (forward pipeline)
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
