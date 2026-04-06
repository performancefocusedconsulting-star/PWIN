# PWIN Competitive Intelligence

Automated competitive intelligence database built on the UK
Find a Tender Service (FTS) OCDS open data API.

## What it does

- **Scheduled ingest agent** — pulls all UK public sector procurement notices
  nightly via the FTS OCDS API (Cabinet Office, Open Government Licence)
- **Structured database** — buyers, suppliers, awards, lots, CPV codes,
  planning notices with full relationship mapping
- **Intelligence queries** — buyer profiles, supplier win histories,
  expiry pipelines, forward pipeline, and PWIN competition signals

## Setup

```bash
# No external dependencies — uses Python stdlib only
python --version   # 3.9+ required

# Quick test (50 releases)
python agent/ingest.py --limit 50

# Ingest from a specific date
python agent/ingest.py --from 2026-01-01

# Full historical ingest from 2024
python agent/ingest.py --full
```

## Queries

```bash
# Database stats
python queries/queries.py summary

# Buyer profile
python queries/queries.py buyer "Ministry of Defence"
python queries/queries.py buyer "NHS"

# Supplier intelligence
python queries/queries.py supplier "Serco"
python queries/queries.py supplier "Capita"

# Expiry pipeline (core prospecting tool)
python queries/queries.py expiring --days 180
python queries/queries.py expiring --days 90 --value 500000
python queries/queries.py expiring --days 365 --buyer "Home Office"

# Forward pipeline (planning + market engagement)
python queries/queries.py pipeline
python queries/queries.py pipeline --buyer "Ministry of Justice"

# Awards above value threshold
python queries/queries.py awards --value 1000000
python queries/queries.py awards --supplier "Serco"

# PWIN signals (competition level by buyer/category)
python queries/queries.py pwin
python queries/queries.py pwin --buyer "Home Office"

# CPV code search
python queries/queries.py cpv 79410000
```

## Scheduling

### Cron (local / server)
```bash
0 2 * * * cd /path/to/pwin-competitive-intel && python agent/scheduler.py >> logs/ingest.log 2>&1
```

### GitHub Actions
See `.github/workflows/ingest.yml` — runs at 02:00 UTC nightly.
Database cached between runs for incremental pulls only.

## Database

SQLite at `db/bid_intel.db`. Schema:

| Table              | Contents                                                |
|--------------------|---------------------------------------------------------|
| `buyers`           | Contracting authorities — name, type, region, contact   |
| `suppliers`        | Companies — name, COH no., scale, VCSE flag             |
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

## Data source

**Find a Tender Service OCDS API** (Cabinet Office, Open Government Licence).

Covers all UK public sector contracts published via FTS since 2024:
- Planning notices and market engagement (future pipeline)
- Tender notices (live opportunities)
- Contract award notices (who won, at what value, how many bidders)
- Contract detail notices (signed contracts with dates)

**Not in this feed:** KPI data, delivery performance, contract modifications
post-award. Supplement with FOI requests for that layer.
