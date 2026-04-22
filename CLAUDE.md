# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Wiki Knowledge Base

Path: `C:/Users/User/Documents/Obsidian Vault`

When you need context not already in this project (prior decisions, research, session history):
1. Read `C:/Users/User/Documents/Obsidian Vault/wiki/hot.md` first (~500 words of recent context)
2. If not enough, read `wiki/index.md`
3. If you need domain specifics, read `wiki/<domain>/_index.md`
4. Only then read individual wiki pages

Use `/save` to file any valuable insight, decision, or answer into the wiki at the end of a session.
Do NOT read the wiki for general coding questions or things already in this project's CLAUDE.md.

## Project

PWIN is a monorepo containing multiple products, each in its own subfolder. It is in early development.

## Repository

- **Remote:** https://github.com/performancefocusedconsulting-star/PWIN
- **Main branch:** `main`
- **Structure:** Each product lives in its own subfolder (e.g. `pwin-bid-execution/`)

---

## Architecture Decisions

PWIN products historically used a "single HTML file, no server" architecture by default. That rule fit when products were prototypes shown on consultant laptops. **It is not a forever rule.** When the deployment context changes — public distribution, sensitive IP, integration requirements, scale — architecture should be reconsidered against the factors below, not blindly inherited.

### Factors to weigh on every architecture decision

| Factor | Questions to ask |
|---|---|
| **Effort** | How much work to build, test, and maintain? Does it require new tooling, hosting, or ongoing operational responsibility? |
| **Cost** | What does it cost to run at expected volume? Is a free tier sufficient? Does cost scale linearly with users or stay flat? |
| **Security & IP exposure** | What can a visitor copy from the running app? Are rubrics, prompts, persona, scoring logic visible in browser source? Is the threat model "trusted internal users" or "public adversary"? |
| **Extensibility** | Can features be added without rewrites? Does the architecture force every change into one file? |
| **Future-proofing** | Does the choice lock in a hard-to-reverse decision? Is there a clean migration path if context changes again? |
| **User experience** | Does it work offline? On slow networks? Does login or account creation get in the way? |
| **Distribution** | How does the product reach users — email attachment, public URL, app store, embedded? |

### The "single HTML file" default, in context

PWIN products started as single HTML files because:

- They were demonstrated on consultant laptops via email or USB
- The audience was small, trusted, and internal
- The AI layer didn't exist yet
- Hosting and servers were unwanted operational overhead
- IP exposure to "users" wasn't a concern because users were trusted

This is still the right default for **prototypes** and for **consultant standalone tools** that ship as files. It is the wrong default for:

- **Public-facing lead-gen pages**, where competitors can View Source and copy the entire scoring intelligence in seconds
- **Multi-user products**, where state must be shared across devices
- **Products with sensitive prompt engineering**, where the system prompt is the IP
- **Anything that needs server-side authentication, rate limiting, or audit logging**

**When a product moves from prototype to public deployment, re-read this section before continuing** and decide whether the original architecture still fits. Do not let "single HTML file" override security, IP protection, or fitness for purpose.

### Current architecture state of each product (2026-04-09)

| Product | Current architecture | Why | Re-evaluate when |
|---|---|---|---|
| pwin-bid-execution | Single HTML, localStorage | Internal bid manager tool, single user, sensitive bid data should not leave the user's machine | Multi-user collaboration is required |
| pwin-qualify (consulting standalone) | Single HTML, content inlined at build time | Ships to consultants on laptops, must work offline | The consultant deployment shifts to hosted SaaS with login |
| pwin-qualify (website MVP) | Single HTML on Cloudflare Pages, AI via Worker proxy | **Currently exposes the rubrics, persona, and trigger rules in public browser source — server-side migration in scope for v0.2 (Pursuit Viability) ship, agreed 2026-04-15** | Shipping with v0.2: rubrics, persona, calibration matrix, RAG logic, and challenger overlay output schema move into the Worker so the browser becomes a thin display layer. Rationale: v0.2 creates the IP that's worth protecting; deferral logic ("no real moat to protect yet") no longer holds. Consulting standalone stays client-side (must work offline). |
| pwin-strategy | Not yet built | — | At design time, not after |
| pwin-portfolio | Single HTML prototype | Internal leadership view, not public | If exposed externally |
| bidequity-verdict | Runs on the pwin-platform MCP server | Two-pass forensic review needs server-side execution and platform knowledge access | — |
| pwin-platform | Node.js + MCP server | Multi-product orchestration is inherently server-side | — |
| pwin-competitive-intel | Python pipeline + SQLite + Cloudflare D1 | Data ingestion and serverless query layer for an internal-only DB | — |

---

## pwin-bid-execution

A single self-contained HTML application for bid production control and assurance. Used by bid managers to track the full lifecycle of complex government bids.

### Reference Documents

- `pwin-bid-execution/docs/bid_execution_architecture_v6.html` — the WHAT (modules, data model, UX, activities)
- `pwin-bid-execution/docs/bid_execution_rules.html` — the HOW (algorithms, state transitions, formulae, thresholds)
- **Always read the relevant sections of these documents before implementing any feature.**

### Current Architecture

Single HTML file, vanilla JavaScript, `localStorage` for persistence, JSON import/export for portability, no external JS dependencies beyond Google Fonts (Cormorant Garamond, DM Mono, DM Sans). Must work in any modern browser without a server.

This is the right shape for now because the bid manager is the sole operator, the data is highly sensitive (bid pricing, win strategy, client intelligence, commercial position) and should not leave the user's machine, and a single user on their own laptop has no need for a server. See the [Architecture Decisions](#architecture-decisions) section above for the framework that drove this choice.

**Re-evaluate when:** multi-user collaboration becomes a requirement, or when the product needs to share state with the rest of the PWIN platform via the MCP server.

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
- `pwin-qualify/docs/PWIN_Rebid_Module_Review.xlsx` — design pack for the incumbent rebid modifier layer (12 questions, 11 trigger rules, 9 risk-assessment fields, 3 few-shots). The source of truth for the rebid layer; the JSON content file below is generated from it.
- `pwin-qualify/docs/PWIN_Architect_v1.html` — **the consulting standalone app, and the canonical product**. All future Qualify development centres on this file.
- `pwin-qualify/content/` — versioned content system (see below). Both Qualify apps load their scoring intelligence from here.
- `pwin-qualify/content/README.md` — operating manual for editing content and the publishing workflow.

### The two Qualify apps

There are two Qualify HTML apps that share the same scoring intelligence but diverge on UX, branding, and feature flags:

| App | Path | Purpose |
|---|---|---|
| **Consulting standalone (canon)** | `pwin-qualify/docs/PWIN_Architect_v1.html` | The main product going forward. Carries the full intelligence stack (intel injection, deeper context, eventually the rebid module enabled). |
| **Website MVP** | `bidequity-co/qualify-app.html` | Public lead-gen, deliberately under-enriched (no competitive intel injection per the public-launch decision). Stripped variant of the consulting app. |

**Both apps load the same `QUALIFY_CONTENT` JSON at build time** via `pwin-qualify/content/build-content.js`. The intelligence layer (questions, rubrics, persona, opportunity-type calibration, rebid modifier) is identical across both. Only the brand colours, runtime feature flags, and presentation HTML can drift.

### Content system

The product's scoring brain lives in `pwin-qualify/content/qualify-content-v0.1.json`. Editing this file and re-running the build script propagates changes to both apps. Never edit literals inside the HTML files by hand — they are sentinel-injected at build time.

**What's in the content file:**

- `questionPacks.standard` — the 24 standard questions (text, rubric, inflation signals, weight)
- `modifiers.incumbent` — the rebid modifier layer (12 R-questions, additional persona triggers, additional output schema, design principles, few-shot examples)
- `categories`, `weightProfiles`, `oppTypeProfile` — category definitions and the per-opportunity-type weight rebalancing
- `persona` — Alex Mercer's full persona object (identity, beliefs, traits, tone, language patterns, hard rules, workflow triggers, success criteria)
- `opportunityTypeCalibration` — the seven opportunity-type-specific calibration paragraphs injected into Alex's prompt
- `outputs` — output schema definitions referenced by the apps

**The four tunable areas** (per `feedback_qualify_finetune_scope` in auto-memory):

1. **Rubric bands** — inside each question's `rubric` field
2. **Inflation signals (per-question)** — each question's `inflationSignals` array
3. **Persona workflow triggers** — `persona.workflowTriggers.{autoChallenge, autoQuery, calibrationRules, inflationTriggers}` and the modifier's `addsPersonaTriggers`
4. **Opportunity-type calibration** — `opportunityTypeCalibration.{BPO, IT Outsourcing, ...}`

**What NOT to tune for now:** question weights (`qw`) and category weights (`weight`, `weightProfiles`). These are stable.

### Rebid modifier layer

The incumbent rebid layer is the proof case for the modifier mechanism. When `state.context.incumbent === "We are the incumbent defending this contract"`, the runtime calls `applyContentModifiers()` which:

1. Pushes a 7th category (`Incumbent Position`, weight 0.20) into `CATS`, rebalancing the standard six proportionally to 0.80 total
2. Appends 12 R-questions (R1–R12) to `QUESTIONS`, each with normalised within-category weights
3. Augments `ALEX_PERSONA.workflowTriggers` with 4 inflation triggers (RI-1..RI-4), 4 calibration rules (RC-1..RC-4), and 3 auto-verdict rules (RA-1..RA-3) — all with `[ref]` prefixes for traceability
4. Registers `CONTENT_OUTPUTS.rebidRiskAssessment` with the 9-field Rebid Risk Assessment schema

The full-report function checks `ACTIVE_MODIFIERS.has('incumbent')` and, if true, merges the rebid risk-assessment fields into the AI request schema. The response is rendered as a separate "Rebid Risk Assessment" section below the standard report. **One AI call, combined schema** — not two calls.

`renderRebidRiskAssessment(rra)` exists in both apps (ES6 in consulting, ES5 in website) and renders the seven core fields plus the two PROPOSED-now-active fields (`performanceNarrativeGaps`, `switchingCostQuantification`).

Modifier deactivation is handled by re-running `applyContentModifiers()` whenever context changes — the function rebuilds from base before re-applying, so flipping the radio button cleanly resets back to 24 questions and the standard persona.

### Build, eval, publish workflow

```bash
# 1. Edit pwin-qualify/content/qualify-content-vX.Y.json
# 2. Bump version + add changelog entry
# 3. Run the eval harness (requires API key)
ANTHROPIC_API_KEY=sk-... node pwin-qualify/content/eval-harness.js

# 4. Build — inlines JSON into both HTML apps between sentinel markers
node pwin-qualify/content/build-content.js --version 0.2   # v0.2+
node pwin-qualify/content/build-content.js                  # targets v0.1 (legacy)

# 5. Verify both apps in sync without modifying them
node pwin-qualify/content/build-content.js --version 0.2 --check

# 6. Commit JSON + both HTML files together
```

**The build script is idempotent** — running it twice prints "unchanged" the second time. The HTML files MUST be committed alongside the JSON because they are derived but not auto-built (no CI step).

**`build_v02.py`** (`pwin-qualify/content/build_v02.py`) — generation script that rebuilds `qualify-content-v0.2.json` from `Winnability_Artifact_Judgment_Scorecard_v6.xlsx` and the v0.1 JSON. Run this when the Excel source changes or structural content needs regenerating. Do not hand-edit the JSON for bulk structural changes — edit the script and re-run.

**Eval harness** (`pwin-qualify/content/eval-harness.js`) reads fixtures from `pwin-qualify/content/eval-fixtures/`, builds the same prompt the app builds, calls Claude, and diffs against expected verdicts. Add a fixture for every meaningful tune so it doesn't regress. Seed fixtures from the workbook few-shots are flagged `isConstructed: true` and should be replaced with real BIP cases when available. Cost is roughly $0.01–$0.02 per fixture with Sonnet 4.6.

**Eval fixtures are versioned:** v0.1 fixtures in `eval-fixtures/` root are invalidated by the v0.2 question changes. v0.2 fixtures live in `eval-fixtures/v0.2/`.

**v0.2 calibration rules are objects:** `persona.workflowTriggers.calibrationRules` in `qualify-content-v0.2.json` are `{id, rule}` objects, not plain strings as in v0.1. Any code iterating them must handle both: `typeof r === 'object' ? r.rule : r`.

**Python Windows encoding gotcha:** `print()` with Unicode characters (e.g. `→`) crashes with `UnicodeEncodeError` on Windows cp1252. Fix: add `import sys; sys.stdout.reconfigure(encoding='utf-8')` at the top of any script, or replace Unicode arrows with `->` in print statements.

### Current Architecture

Two HTML apps share one scoring brain via build-time content injection:

- **Consulting standalone** (`pwin-qualify/docs/PWIN_Architect_v1.html`) — single HTML file, JSON content inlined at build time, vanilla JavaScript, runs offline. AI calls go directly to the Claude API. This is the right shape because it ships to consultants on laptops and must work without a server.
- **Website MVP** (`bidequity-co/qualify-app.html`) — single HTML file deployed to Cloudflare Pages, AI calls proxied through a Cloudflare Worker that holds the API key. **Currently exposes the rubrics, persona, opportunity-type calibration, and trigger rules in public browser source — anyone can View Source and copy the entire scoring intelligence.** This was acceptable for the prototype but is not acceptable for the public lead-gen deployment.

Brand colours stay app-local (declared in each app's `CAT_BRAND` constant) — they are the only intentional drift between the two apps' scoring layers.

See the [Architecture Decisions](#architecture-decisions) section for the framework that drove these choices.

**Re-evaluate when:**
- For the **consulting standalone**: when the deployment shifts from laptop-distributed files to a hosted SaaS model with login.
- For the **website MVP**: **now.** A Phase 1 server-side migration was scoped on 2026-04-09 — move the content (rubrics, persona, trigger rules, calibration paragraphs) into the Cloudflare Worker so the browser becomes a thin display layer that only sees what the visitor types in and what Alex says back. The questions remain visible (visitors must see them to answer them) but the scoring intelligence stays server-side.

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

- `pwin-platform/docs/architecture/mcp_server_architecture.md` — authoritative architecture spec (v1.0)
- `pwin-platform/docs/architecture/pwin_architect_plugin_architecture.md` — plugin architecture (v1.5), agent specs, skill definitions

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

AI-driven capture-phase strategy development. The bridge between Qualify ("should we bid?") and Execution ("execute the bid"). Takes the qualification intelligence and transforms it into a locked win strategy, competitive positioning, and capture plan that **informs the bid manager** running Execution.

### Reference Documents

- No design documents yet — product folder created, awaiting design.

### Position in Product Lifecycle

```
Qualify → Strategy → Execution
  "Should we bid?"   "How do we win?"   "Execute the bid"
```

- **Receives from Qualify:** PWIN score, category assessments, buyer values, stakeholder maturity, competitive positioning maturity
- **Produces for Execution:** locked win themes, competitive strategy, stakeholder map, buyer values, client intelligence, capture plan
- **Data file:** `win_strategy.json` per pursuit (designed in MCP architecture, not yet populated)

> **v1 handoff model — process-level, not programmatic.** In v1, Execution is a standalone single-HTML, localStorage app. It does not read from `shared.json` or any other product's data store. The bid manager carries Strategy's outputs mentally and re-enters relevant context through the Execution Setup Wizard. The "Consumed by Execution" column below describes where in Execution each entity is applied — by the bid manager, not by the application. Programmatic data sharing between Strategy and Execution requires the unresolved localStorage↔MCP bridge (see `bid_execution_architecture_v6.html` Session 13 note). Do not treat this as a v1 integration requirement.

### Shared Entities Owned by Strategy

| Entity | Created by Strategy | Applied in Execution (by bid manager) |
|--------|--------------------|-----------------------|
| Win Themes | Defined and locked | Referenced when executing SAL-04; threaded through responses |
| Competitive Positioning | Full competitor strategy | Referenced in SAL-03; battle cards inform response writing |
| Stakeholder Map | Enriched from Qualify maturity | Referenced in SAL-10; engagement tracked through bid |
| Buyer Values | Confirmed and prioritised | Referenced in SAL-01.2; shapes solution design |
| Client Intelligence | Built from capture engagement | Referenced in SAL-01 |
| Capture Plan | Produced and locked | Referenced in SAL-06.4; governs bid strategy |

### Current Architecture

Not yet built. When designed, the architecture should be chosen using the [Architecture Decisions](#architecture-decisions) framework above — not inherited from prior products. Likely shape: a single HTML application backed by the PWIN Platform Data API for `win_strategy.json` persistence, with the MCP server providing read/write endpoints and shared entity sync to Bid Execution. Whether the AI prompt assembly should live in the browser or server-side is an open question and should be decided at design time using the same security/IP framework that flagged the Qualify website MVP.

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

### Current Architecture

Single HTML file prototype, vanilla JavaScript, currently uses 12 illustrative Serco pursuits as seed data. Not yet wired to the MCP server. Production version will read from the PWIN Platform Data API.

This is an internal leadership view, not a public product, so the single-file architecture is appropriate. See the [Architecture Decisions](#architecture-decisions) section above.

**Re-evaluate when:** the dashboard is exposed externally (e.g. shared with clients as part of a Core or Command engagement), or when it needs to display data from the live PWIN Platform Data API in real time for multiple concurrent leadership users.

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

- Python 3.9+ stdlib only for ingest, enrichment, dashboard, and query layer — zero external deps. The canonical layer (Splink supplier dedup) is scoped into `.venv/` with its own `requirements-splink.txt`; nightly cron unaffected.
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

- **Canonical entity layer.** Buyer canonical layer at 70.3% award-weighted coverage of the £1m+ universe (1,928 entities from GOV.UK + central buying agencies + NHS ODS + ONS LA codes + devolved, built 2026-04-11/12). Supplier canonical layer built 2026-04-14: 161,119 raw suppliers → **82,637 canonical** via Splink + deterministic name-merge post-pass. Downstream consumers should join through `canonical_suppliers` + `supplier_to_canonical` (or `canonical_buyers` + the buyer glossary) rather than aggregating raw IDs. See `CANONICAL-LAYER-DESIGN.md`, `DISCOVERY-REPORT.md`, and `CANONICAL-LAYER-PLAYBOOK.md` for decisions and lessons.
- **Companies House coverage.** ~27% of suppliers have a CH number on file. The rest are publisher name-only entries (no structured ID), GB-PPON-only, non-UK, or public sector bodies. Recovering name-only suppliers via Splink-against-CH-register is the next canonical-layer task, deferred until this v1 is validated against live dossier work.
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
