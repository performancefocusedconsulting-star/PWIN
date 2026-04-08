# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PWIN is a monorepo containing multiple products, each in its own subfolder. It is in early development.

## Repository

- **Remote:** https://github.com/performancefocusedconsulting-star/PWIN
- **Main branch:** `main`
- **Structure:** Each product lives in its own subfolder (e.g. `pwin-bid-execution/`)

---

## pwin-bid-execution

A single self-contained HTML application for bid production control and assurance. Used by bid managers to track the full lifecycle of complex government bids.

### Reference Documents

- `pwin-bid-execution/docs/bid_execution_architecture_v6.html` — the WHAT (modules, data model, UX, activities)
- `pwin-bid-execution/docs/bid_execution_rules.html` — the HOW (algorithms, state transitions, formulae, thresholds)
- **Always read the relevant sections of these documents before implementing any feature.**

### Technical Constraints

- Single HTML file output. All CSS, JS, and template data in one file.
- Vanilla JavaScript only. No React, Vue, Angular, or any framework.
- No external JS dependencies beyond Google Fonts (Cormorant Garamond, DM Mono, DM Sans).
- `localStorage` for persistence. JSON import/export for portability.
- Must work in any modern browser without a server.

### Visual Identity

- Midnight Executive palette (see CSS variables in architecture document)
- Cormorant Garamond for display/numbers, DM Mono for labels/data/code, DM Sans for body text
- Deep navy backgrounds, gold accents, structured information hierarchy
- Match the visual style of the architecture document itself

### Code Organisation Within the Single File

- **CSS:** design tokens (variables), base styles, layout, component styles, print styles, animations
- **Data:** state management, mutation functions, computed properties, localStorage, template data
- **Components:** render functions per module, shared UI components (tables, forms, cards, badges, modals)
- **Controllers:** event handlers, routing, validation, calculations, alert logic

### Key Principles

- The bid manager is the sole operator. No multi-user, no login, no authentication.
- The methodology prescribes the activities. The bid manager executes, deactivates, or adjusts.
- Readiness is earned through evidence, not declared by ticking a box.
- Nudges are prompts, not autonomous updates. The system never changes status without human confirmation.
- Every state transition must follow the rules in `bid_execution_rules.html` — no invalid transitions.

---

## Session Protocol

- After every significant decision, update the relevant reference document (architecture or rules) before continuing.
- Never proceed to the next task without confirming the current decision is captured in writing.
- At the end of every session, add a **## Next Session** section to the architecture document summarising:
  - What was just decided
  - What was about to happen next
  - Any open questions or unresolved options

---

## pwin-qualify

An AI-assisted bid qualification and coaching application. Pursuit teams self-assess opportunity strength across 6 categories (24 questions), receive an AI assurance review that challenges over-scoring, and get a PWIN score with a pursue/condition/walk-away recommendation.

### Reference Documents

- `pwin-qualify/docs/PWIN-Qualify-Design v1.html` — functional design document (scoring model, PWIN formula, context engine, AI assurance layer, rejected decisions)
- `pwin-qualify/docs/PWIN_AI_Enrichment_Review.xlsx` — AI prompt enrichment spec (sector knowledge, opportunity types, few-shot examples, output schema, system prompt) — **review columns not yet completed**
- `pwin-qualify/docs/BWIN Qualify_AI Design_Proforma_v2.xlsx` — Phase 1 intelligence-gathering spec (51 data points, 20 reasoning rules, confidence model) — **not yet completed**
- `pwin-qualify/docs/PWIN_Architect_v1.html` — working prototype application

### Technical Constraints

- Same as pwin-bid-execution: single HTML file, vanilla JavaScript, no frameworks, no external dependencies beyond Google Fonts.
- JSON file export/import for persistence (not localStorage).
- No MCP integration yet — AI assurance review currently calls Claude API directly from the browser.

### Cross-Product Data

- PWIN Qualify shares pursuit-level data with Win Strategy and Bid Execution (see Session 15 memory for shared entity model).
- Sector and opportunity type knowledge is platform-level, not product-specific.

---

## pwin-platform

The PWIN Platform MCP server — a single Node.js process serving dual interfaces for all products.

### Architecture

- **Data API (HTTP, localhost:3456)** — replaces localStorage for HTML product apps. Pursuit CRUD, per-product load/save, shared entity access, import/export.
- **MCP Server (stdio)** — 94 typed tools for Claude (read + write). Field-level permission enforcement on all AI writes.
- **JSON file store** under `~/.pwin/` — per-pursuit directories with shared.json + product files.
- **Skill runner** — generic executor for declarative YAML skill configs. Assembles context from platform knowledge + pursuit data, calls Claude, executes write-backs via MCP tools.

### Reference Documents

- `pwin-bid-execution/docs/mcp_server_architecture.md` — authoritative architecture spec (v1.0)
- `pwin-bid-execution/docs/pwin_architect_plugin_architecture.md` — plugin architecture (v1.5), agent specs, skill definitions

### Technical Constraints

- Node.js (ES modules). Single dependency: `@modelcontextprotocol/sdk`.
- No database — JSON files on disk. Designed for SaaS migration (Supabase/Postgres).
- Skills are YAML config files, not code. The skill runner is the only executor.
- `ANTHROPIC_API_KEY` environment variable required for live skill execution. Without it, skills run in dry-run mode (prompt assembly only).

### Running

```bash
cd pwin-platform
npm install
node src/server.js              # Data API only (default)
node src/server.js --mcp        # MCP server only (stdio, for Claude)
node src/server.js --both       # Both interfaces
node test/test-skills.js        # Run test suite (68 tests)
```

### Platform Knowledge

11 JSON files seeded under `~/.pwin/platform/` from the two enrichment spreadsheets. Served via MCP tools (`get_sector_knowledge`, `get_reasoning_rules`, etc.). Must be seeded before skills can assemble context-rich prompts — run the extraction script or copy from a seeded environment.

---

## pwin-strategy

AI-driven capture-phase strategy development. The bridge between Qualify ("should we bid?") and Execution ("execute the bid"). Takes the qualification intelligence and transforms it into a locked win strategy, competitive positioning, and capture plan that Execution imports.

### Reference Documents

- No design documents yet — product folder created, awaiting design.

### Position in Product Lifecycle

```
Qualify → Strategy → Execution
  "Should we bid?"   "How do we win?"   "Execute the bid"
```

- **Receives from Qualify:** PWIN score, category assessments, buyer values, stakeholder maturity, competitive positioning maturity
- **Produces for Execution:** locked win themes, competitive strategy, stakeholder map, buyer values, client intelligence, capture plan (all written to `shared.json`)
- **Data file:** `win_strategy.json` per pursuit (designed in MCP architecture, not yet populated)

### Shared Entities Owned by Strategy

| Entity | Created by Strategy | Consumed by Execution |
|--------|--------------------|-----------------------|
| Win Themes | Defined and locked | Imported into SAL-04, threaded through responses |
| Competitive Positioning | Full competitor strategy | SAL-03 imports, battle cards feed response writing |
| Stakeholder Map | Enriched from Qualify maturity | SAL-10 imports, engagement tracked through bid |
| Buyer Values | Confirmed and prioritised | SAL-01.2 imports, shapes solution design |
| Client Intelligence | Built from capture engagement | SAL-01 imports |
| Capture Plan | Produced and locked | SAL-06.4 imports, governs bid strategy |

### Technical Constraints

- Same as other products: single HTML file, vanilla JavaScript, no frameworks
- Data persisted via PWIN Platform Data API (`win_strategy.json`)
- MCP server already has Win Strategy read/write endpoints and shared entity sync rules designed

---

## pwin-portfolio

Portfolio-level intelligence dashboard. Provides a senior leadership view across all active pursuits — aggregating PWIN scores, pipeline economics, resource allocation, and risk exposure into a single operational picture.

### Reference Documents

- `pwin-portfolio/docs/pwin-architect-portfolio-dashboard.html` — working prototype (early, uses illustrative Serco data)

### Purpose Within the Product Family

The Portfolio Dashboard sits **above** the individual pursuit products. While Qualify, Execution, and Verdict operate at the single-pursuit level, Portfolio aggregates across the entire pipeline:

- **Qualify** answers "should we bid this?" for one opportunity
- **Execution** answers "how is this bid progressing?" for one opportunity
- **Portfolio** answers "how is our bid operation performing across all opportunities?"

### Key Views (from prototype)

- **Portfolio Grid** — all active pursuits with PWIN scores, stages, trajectories, category breakdowns, risk flags
- **Priority Matrix** — bubble chart (TCV × PWIN, sized by bid cost, coloured by deal type) with raw and stage-adjusted modes
- **Pursuit Detail** — drill-down into individual pursuit with category-level evidence and vulnerability analysis
- **Portfolio Economics** — three-lever productivity framework (pursuit velocity, team efficiency, commercial yield) with ROI modelling
- **Settings** — configurable parameters (win rate benchmarks, cost assumptions, period selection)

### Platform Integration

- Reads shared pursuit data from `shared.json` across all pursuits (PWIN scores, stages, sectors, TCV)
- Consumes Qualify category scores (cp, pi, ss, oi, vp, pp) for the radar/category breakdown
- Consumes Bid Execution activity status for trajectory and progress tracking
- Consumes Verdict Pursuit Maturity Scores for historical portfolio benchmarking
- The Portfolio Economics view models the consulting ROI — this is the commercial justification layer for Core and Command engagements

### Technical Constraints

- Same as other products: single HTML file, vanilla JavaScript, no frameworks
- Prototype uses seed data (12 illustrative Serco pursuits). Production version reads from the PWIN Platform Data API
- Not yet wired to the MCP server — currently standalone

---

## bidequity-verdict

Forensic post-loss bid review product. Independently evaluates the entire pursuit lifecycle — not just the written submission, but every upstream activity that determined whether the submission could succeed.

### Reference Documents

- `bidequity-verdict/docs/BidEquity-Verdict-PRD-v2.md` — product requirements document (draft, v2.0)

### Architecture

- Runs on the same PWIN Platform MCP server as Qualify and Bid Execution — not a separate build.
- Two-pass execution model: Pass 1 (platform analysis with AI), Pass 2 (consultant investigation with AI-generated probe questions, then re-assessment).
- 7 evaluation domains, each scored on a 5-point maturity scale (Absent → Optimised). Weighted to produce a Pursuit Maturity Score.
- ~11 new YAML skill configs (7 forensic domain assessments + proposal parsing + independent scoring + traceability + report assembly). Independent scoring skill is shared with Bid Execution pre-review AI scoring.
- Product data stored as `verdict.json` per pursuit, alongside existing product files.

### Commercial Model

- Fixed-fee transactional: Verdict Single (£2,000 / 1 pursuit), Verdict Portfolio (£5,000 / 3 pursuits).
- Gateway product into Core and Command (outcome-aligned consulting engagements).
- API cost per engagement: <£1. Cost driver is consultant time, not platform.

---

## pwin-competitive-intel

Internal-only intelligence database of UK public sector procurement, built on the Find a Tender Service (FTS) OCDS open data and Companies House. Loaded primarily from the Open Contracting Partnership weekly bulk file (5+ years of history) and kept current via incremental FTS API pulls. Enriches supplier records with Companies House data (directors, parent companies, SIC codes) and feeds the other PWIN products (Verdict, Win Strategy, Bid Execution, future paid Qualify tier).

**This is NOT a customer-facing product.** A free public lookup tool was considered and consciously declined. The public Qualify lead-gen experience must not call this layer — see `feedback_qualify_lead_gen_scope.md` in auto-memory.

### Architecture

- **OCP bulk importer** (`agent/import_ocp.py`) — reads the Open Contracting Partnership weekly JSONL bulk file (5+ years of UK FTS data, ~175k compiled releases) and back-populates the database in ~4 minutes. Reuses `ingest.py`'s parse/upsert functions so there is one source of truth for parsing. Idempotent — safe to re-run after each weekly OCP refresh. The canonical path for historical depth.
- **FTS ingest agent** (`agent/ingest.py`) — incremental OCDS API pull with cursor-based pagination, multi-lot and multi-supplier support, 1s polite delay between pages. Cursor advances only on the high-water mark of releases actually processed (failures preserve state). Read timeouts caught with exponential backoff. Also supports a separate `--backfill`/`--resume`/`--max-pages` mode that persists the API's `links.next` URL between runs for chunked recovery.
- **Companies House enrichment** (`agent/enrich-ch.py`) — pulls company status, directors, SIC codes, parent company, accounts date for suppliers with CH numbers. Requires `COMPANIES_HOUSE_API_KEY` env var (free key from developer.company-information.service.gov.uk).
- **SQLite database** (`db/bid_intel.db`) — normalised schema: notices (OCID-keyed), lots, awards, award_suppliers (many-to-many), cpv_codes (indexed junction table), planning_notices, plus 13 Companies House columns on suppliers. The structured `companies_house_no` field is recovered at ingest time by `_extract_coh()`, which accepts spec-compliant `GB-COH`-tagged identifiers, schemeless identifiers whose value matches the CH number format (a common publisher omission), and the same in `additionalIdentifiers`. Values are validated to reject foreign registers (e.g. German HRB numbers) that publishers sometimes mis-tag.
- **Query library** (`queries/queries.py`) — CLI with 8 commands: summary, buyer, supplier, expiring, pipeline, awards, pwin, cpv
- **Dashboard** (`dashboard.html`) — 6-tab single HTML file with expandable detail rows, Companies House panel on supplier profiles, Midnight Executive palette
- **Data server** (`server.py`, port 8765) — Python HTTP API bridging SQLite to dashboard
- **Cloudflare Worker** (`workers/intel-api.js`) — serves `/api/intel/*` endpoints from D1 serverless SQLite. Currently stale (D1 deploy descoped — see below).
- **D1 sync** (`agent/sync-d1.py`) — exports local SQLite to SQL for `wrangler d1 execute`
- **GitHub Actions** (`.github/workflows/ingest.yml`, at repo root) — nightly at 02:00 UTC: FTS incremental ingest → CH enrichment (200/night) → D1 sync. The workflow file MUST live at the repo root, not nested under `pwin-competitive-intel/.github/`, or GitHub Actions will not pick it up.
- **Scheduler** (`agent/scheduler.py`) — cron wrapper for local nightly runs

### Platform Integration

- **MCP tools** — 7 read tools added to `pwin-platform/src/mcp.js` via `competitive-intel.js` module (uses node:sqlite): `get_competitive_intel_summary`, `get_buyer_profile`, `get_supplier_profile`, `get_expiring_contracts`, `get_forward_pipeline`, `get_pwin_signals`, `search_cpv_codes`
- **Platform Data API** — `/api/intel/*` endpoints added to `pwin-platform/src/api.js` (same queries, served via HTTP for HTML apps)
- **Qualify integration (current state)** — both `pwin-qualify/docs/PWIN_Architect_v1.html` and `bidequity-co/qualify-app.html` currently fetch buyer profile + PWIN signals before every AI review (auto-detects: localhost → platform API, production → Cloudflare Worker). **This is being suppressed for the public lead-gen release**: when public release is imminent, the intel calls will be feature-flagged off in the public versions of these apps. They stay available for internal Bid Execution / Win Strategy / Verdict consumption and for the future paid Qualify tier. Re-enabling on the paid tier is gated on data-quality work (entity resolution, CH name-matching) clearing the misleading-assertion risk.

### Technical Constraints

- Python 3.9+ stdlib only — zero external dependencies for ingest and enrichment
- SQLite for local persistence — currently ~570 MB at 175k notices, scales comfortably
- Cloudflare D1 for production (serverless SQLite, free tier: 5GB, 5M reads/day) — **deploy descoped from immediate priority** since public Qualify is shipping intel-stripped; D1 becomes relevant again when paid Qualify or another internal product needs production access. The current 570 MB DB has not been validated against `wrangler d1 execute` load limits — verify before any deploy attempt.
- FTS API rate limits: 1s between pages, 429 retries with exponential backoff, 60s read timeout with retries
- Companies House API: 600ms between calls, free key required
- Database not committed to repo (`.gitignore`); the OCP bulk JSONL file (`data/`) is also gitignored — built from a single download, not from git

### Purpose Within the Product Family

Cross-cutting **internal** knowledge layer feeding the other pursuit products:

- **Feeds Verdict** — incumbent detection, supplier history, buyer relationships for post-loss forensics
- **Feeds Win Strategy** — competitor incumbencies, supplier win histories, buyer relationships, Companies House data (directors, parent companies)
- **Feeds Bid Execution** — incumbent flags, comparable awards, buyer patterns during bid production
- **Feeds future paid Qualify tier** — buyer signals, competition intensity, framework holders injected into AI assurance
- **Internal sales pipeline** — forward pipeline (planning notices = upcoming tenders), expiry pipeline (contracts ending soon), CPV-filtered prospecting

### Known Limitations

- **Buyer entity resolution.** Large buyers fragment across many distinct rows. Ministry of Defence currently has ~1,272 buyer IDs (PPON variants, legacy GB-FTS IDs, case variants, subsidiaries like DE&S / DSTL / DIO). Aggregated queries for big buyers must use name-based LIKE joins across all variants. A canonical-buyer mapping layer is the #1 planned data-quality improvement.
- **Companies House coverage.** ~27% of suppliers have a CH number on file. The rest are publisher name-only entries (no structured ID), GB-PPON-only, non-UK, or public sector bodies. Recovering name-only suppliers needs fuzzy matching against the Companies House register — planned but not yet built.
- **Framework values.** OCDS records framework *maximum* values, not realised spend. Total-value summaries reflect ceilings, not draw-down.

### Running

```bash
cd pwin-competitive-intel

# Dashboard (local development)
python server.py                                    # → port 8765, open /dashboard.html

# OCP bulk import (canonical path for historical depth)
mkdir -p data
curl -L -o data/ocp-uk-fts.jsonl.gz \
  "https://data.open-contracting.org/en/publication/41/download?name=full.jsonl.gz"
python agent/import_ocp.py                          # full import (~4 minutes)
python agent/import_ocp.py --limit 1000             # bounded (testing)

# Live FTS API (incremental keep-current — what the nightly cron runs)
python agent/ingest.py                              # incremental from saved cursor
python agent/ingest.py --from 2026-01-01T00:00:00   # custom start date
python agent/ingest.py --limit 50                   # quick test

# Resumable backfill (rare — prefer OCP for history)
python agent/ingest.py --backfill 2024-01-01T00:00:00 --max-pages 50
python agent/ingest.py --resume --max-pages 50
python agent/ingest.py --resume                     # run to completion

# Companies House enrichment
export COMPANIES_HOUSE_API_KEY=your_key_here
python agent/enrich-ch.py --limit 100               # enrich 100 suppliers
python agent/enrich-ch.py                           # enrich all unenriched

# Queries
python queries/queries.py summary
python queries/queries.py buyer "NHS"
python queries/queries.py supplier "Serco"
python queries/queries.py expiring --days 180 --value 500000
python queries/queries.py pwin --category services

# Deploy to Cloudflare D1 (descoped — verify load mechanism for ~570 MB DB first)
cd workers
npx wrangler d1 create pwin-competitive-intel       # paste ID into wrangler.toml
npx wrangler d1 execute pwin-competitive-intel --file=../db/schema.sql
python ../agent/sync-d1.py --apply
npx wrangler deploy
```

---

## Adding New Products

When a new product folder is added, create a new section in this file following the same structure as above.
