# Competitive Cube — Displacement Intelligence — Design Specification

**Date:** 2026-05-02
**Project:** pwin-competitive-intel (data layer, dashboard) + pwin-platform (MCP tools)
**Status:** Approved design — **build deferred until post-cloud-migration** (decision dated 2026-05-02 pm). Implementation plan committed at `pwin-competitive-intel/docs/superpowers/plans/2026-05-02-competitive-cube-plan.md` and held until the Wave 1 cloud migration completes. A directional analysis ships in advance to inform launch positioning — see Section 7.
**Related:**
- `pwin-platform/knowledge/sector_opp_matrix.json` (the 9×10 intersection grid that this spec reads from)
- `pwin-platform/knowledge/sector_knowledge.json` (the nine canonical sectors)
- `pwin-platform/knowledge/opportunity_types.json` (the ten canonical opportunity types)
- `wiki/meta/2026-05-02-cfo-model-margins-and-retainer.md` (the conversation that surfaced this product)
- `docs/superpowers/specs/2026-05-02-pwin-cloud-data-architecture-design.md` (the cloud architecture spec — Wave 1 PostgreSQL migration; cube ships against PostgreSQL after migration)
- `pwin-competitive-intel/queries/directional_concentration_analysis.py` (one-off script delivering directional findings ahead of the cube build)
- `pwin-competitive-intel/reports/directional-concentration-analysis-2026-05-02.md` (the directional report itself)

---

## Background — Why This Product Exists

This spec emerged from a marketing-claim audit on the BidEquity Chief Financial Officer business case model. While checking whether *"the average pursuit returns about 1:1 on bid spend"* held up across the actual client list, two related findings surfaced that this product addresses directly.

**Finding one — UK government procurement is highly concentrated when sliced narrowly.** When you cut the market by sector and by opportunity type, individual cells of that grid are dominated by a small number of incumbents — typically three to five suppliers holding 70–90% of contract value. This is hidden when the market is looked at in aggregate, because the aggregate view averages across many different sub-markets that don't actually compete with each other.

**Finding two — concentration plus high bid cost is a structural barrier to entry.** A challenger looking at a concentrated cell faces expected return well below break-even at population-average win rates, because the bid cost is fixed and the win probability is low. Rationally, challengers don't bid; rationally, incumbents do. The cells stay concentrated. The barrier compounds.

This product turns the structural barrier from a passive lock-out into an *informed* go/no-go. By rendering each cell of the market as a structured intelligence view, it tells challengers which cells are worth their bid cost (where the displacement window is genuinely open) and tells incumbents where their position is more eroded than they realised.

---

## Section 1 — What This Product Is

A **cube of UK government procurement** sliced by sector (9), opportunity type (10), and supplier (every canonical supplier on file). Each of the 90 sector-and-opportunity-type cells is rendered as a **displacement intelligence view** — a single page of structured information that tells the reader who currently holds the cell, how concentrated the cell is, what specific contracts are coming up, and how open the buyer behaviour in that cell looks to challenge.

The same view supports three reading lenses:

- **Challenger lens** — *"where is the wedge?"* — for outsiders trying to break in.
- **Incumbent lens** — *"where am I exposed?"* — for incumbents defending position.
- **Portfolio-strategic lens** — *"what's my multi-year capture programme?"* — for incumbents wanting to *grow* portfolio share, not just defend, over a 3–5 year horizon. (This lens emerged from a brainstorming follow-up on 2026-05-02; the rationale, implications, and conversation script are in Section 3 and in `wiki/meta/2026-05-02-competitive-cube-brainstorm.md`.)

All three lenses read off the same underlying data. The rendering changes the framing copy and the sort order; the numbers are identical.

The product addresses three engagement contexts:

- **Bid-team decision-making** at the moment of pursue / no-pursue (challenger and incumbent lenses, single-pursuit scope).
- **Strategic-portfolio planning** at the executive and chief-financial-officer level (portfolio-strategic lens, 3-year horizon, multi-cell supplier-level aggregation).
- **Commercial evidence** in BidEquity's external materials about why incumbency is sticky, where it isn't, and how a strategic supplier can target portfolio share over time.

**What this product is not:**

- A *"who showed up to the bid"* tool. The procurement data does not publish unsuccessful bidders.
- A per-named-pursuit capture aid. Win Strategy already does that.
- A forecasting model. The cube is descriptive intelligence about market structure, not a predictive engine.

---

## Section 2 — The Cube and Its Dimensions

### The fixed cube — 90 cells

Three dimensions, two are part of cell identity:

**Sector.** Nine canonical sectors from the platform taxonomy: Central Government, Local Government, NHS & Health, Defence & Security, Justice & Home Affairs, Transport, Education, Emergency Services, Devolved Government. Every contract notice in the database is mapped to a sector via the canonical buyer layer, which currently covers about 85% of all notices. The remaining 15% (procurement-platform intermediaries, private contractors publishing under their own name, one-off buyers) are excluded from cell aggregates by design — they are not public buyers and shouldn't influence concentration measures.

**Opportunity type.** Ten canonical opportunity types from the platform taxonomy: BPO, IT Outsourcing, Managed Service, Facilities/Field/Operational Service, Hybrid Transformation, Digital Outcomes, Consulting/Advisory, Infrastructure & Hardware, Software/SaaS, Framework/Panel Appointment.

**Supplier.** The canonical supplier layer (currently 82,637 entities). This is the third dimension but is not part of cell identity — it is what *populates* a cell. Each cell holds a ranked supplier list.

### Slicers on top of the cube

Two orthogonal filters that the user can apply to any cell view, but that aren't part of cell identity:

**Contract value band.** Default: all values. User can filter to small (under £25m), mid (£25–100m), major (£100–500m), or strategic (£500m+).

**Time window.** Default: trailing five years for concentration analysis. The recency overlay for the credible-competitor cut (Section 3) uses trailing 18 months. Forward-looking displacement windows use the next 18 months for expiring contracts and the next 24 months for the planning-notice pipeline.

### Cell sufficiency flags

Three states, applied to every cell:

- **Reliable** — 15 or more awarded contracts in the trailing five years. Concentration metrics shown without caveat.
- **Directional** — 5 to 14 contracts. Concentration metrics shown with a *"directional only"* caveat.
- **Insufficient** — fewer than 5 contracts. Supplier names shown but no concentration metrics.

The cube is sorted by total contract value descending so users naturally land on the rich cells first; thin-data cells fall to the bottom of the list.

### Implementation note — opportunity-type tagging

Sector tagging is mechanical (canonical buyer → sector — the work is already done). Opportunity-type tagging is harder. There is no clean field in the procurement data that says *"this is BPO"* versus *"this is IT Outsourcing."* It has to be inferred from the contract's procurement category codes plus title keywords. About 80% of contracts can be tagged unambiguously by category code alone; the remaining 20% need keyword fallback rules.

This is a real piece of v1 work — probably one to two weeks — and it is a hard prerequisite for the cube. The implementation plan owns the build sequence; the design notes it as part of the engine.

---

## Section 3 — What a Single Cell View Looks Like

A cell view is a single page of structured information about one (sector × opportunity type) intersection. Three layers, all visible at once on the same page rather than separate tabs.

### Layer 1 — Cell map (concentration)

The headline numbers about the cell:

- Total contracts awarded in the cell (trailing five years)
- Total contract value
- Top-3 share — what percentage of contract value the top three suppliers hold
- Top-5 share — same for top five
- Effective number of suppliers — a single number ("this cell behaves like a market with 3.4 active suppliers") derived from the standard concentration index used in competition economics. Calculated as 1 ÷ Herfindahl-Hirschman Index, where the index is the sum of each supplier's squared market share.
- Year-on-year trend on those concentration measures (consolidating, fragmenting, or stable)
- Sufficiency flag (Reliable / Directional / Insufficient)

### Layer 2 — Per-incumbent grip strength

The credible competitor list — the named suppliers a bid team should treat as their actual field — computed using a hybrid rule:

> **The credible competitors in a cell are the union of two sets: (a) the suppliers needed to cover 80% of cell contract value over the trailing five years, plus (b) any additional supplier with a contract win in the trailing 18 months whose value exceeds the cell's median contract value (where the median is computed over the trailing five years).**

The first rule produces the bedrock list of established incumbents. The second catches recent entrants who are commercially relevant but haven't accumulated enough historical share to make the historic cut.

For each name in the list, Layer 2 reports:

- Total wins in the cell (count and value)
- Cell share (percentage of cell value)
- First win in the cell (gives a tenure number — how long they've been active)
- Most recent win in the cell
- Renewal vs new-win mix — how many of their wins are renewals/extensions of work they already held versus genuinely new contracts taken from another supplier or won open
- Coverage breadth — how many distinct buyer organisations within the sector have they won from in the cell
- Direct-award reliance — what proportion of their wins came via direct award versus competitive process

This is the layer that turns *"NHS × Managed Service has 3 suppliers holding 78%"* into:

> *"NHS × Managed Service is held by Capita (32% share, 11 buyers, 7-year tenure, mostly renewals — deeply entrenched), Atos (28% share, 4 buyers, 6-year tenure, half via direct award — politically protected), and Capgemini (18% share, 3 buyers, only 3 years of tenure but recent £180m win — rising challenger)."*

The full ranked supplier list (with all wins, all values, all dates) is always accessible — the credible competitor cut is just the headline view. A user who wants the long tail drills in.

### Layer 6 — Displacement windows

The forward-looking view, separate from the historical layers:

**Expiring contracts.** Named contracts in the cell that expire within the next 18 months. For each: total contract value, current incumbent, expiry date, and a flag for whether a renewal notice has appeared yet — meaning the displacement window is genuinely open, not pre-closed by an extension already in flight.

**Forward pipeline.** Named items in the cell from the next 24 months of planning notices (the procurement-system feed of upcoming opportunities). For each: provisional total contract value, prospective buyer, and any indicative timeline. These are contracts that haven't yet appeared as bid opportunities but are visible in published procurement intentions.

### The three lenses

Same data, different framings, single switch on the dashboard view. Implementation is template-level not data-level — the cell page renders the same numbers but with different copy and emphasis depending on which lens is active.

| Element | Challenger lens | Incumbent lens | Portfolio-strategic lens |
|---|---|---|---|
| Cell concentration | *"Hard to break in — top three hold 78%."* The **barrier** the challenger faces. | *"Strong position — your peer group hold 78%."* The **advantage** the incumbent enjoys, with focus on how stable that advantage is over time. | *"This cell behaves like a market with 3.4 active suppliers. Your current share is X%; your three-year target share implies a gap of Y named contracts to displace."* The **strategic context** for setting and pursuing a multi-year portfolio share target. |
| Per-incumbent grip | Listed as *"incumbents to displace"* with grip-strength colour coding (deeper red = harder to dislodge). | Listed as *"you and your peers"* with grip-strength shown as defensive position relative to peers. | Listed as *"the field"* with each peer's projected three-year share trajectory based on their current contracts and historical renewal rates. |
| Forward pipeline | *"Targets to attack."* Items sorted by displaceability (favouring expiring contracts where no renewal notice has appeared, and contracts held by suppliers with thinner cell tenure). | *"Defences to harden."* Items sorted by importance to maintain (favouring the largest contracts the user holds, with time-to-expiry as the urgency cue). | *"Three-year capture programme."* All upcoming contracts in the cell over the next 36 months — yours to defend, peers' to attack — sorted by **revenue impact on three-year portfolio share**. The user's renewal projections, displacement opportunities, and required-win count are computed and shown as a single capture plan. |

The third lens — **portfolio-strategic** — emerged from a brainstorming follow-up on 2026-05-02 (captured in `wiki/meta/2026-05-02-competitive-cube-brainstorm.md`, "The portfolio-strategic reframe" section). It is a deliberate elevation of the cube from single-pursuit decision support to multi-year strategic-portfolio planning. The need: incumbent CFOs in concentrated cells will rationally dismiss the challenger and incumbent lenses as "no new news" — they live in their concentration; they understand their hit rate is structurally bounded by the small field. The portfolio-strategic lens addresses what they *don't* have — a structured forward-portfolio view across all named upcoming contracts in their cells, with renewal projections per peer and displacement-cost economics at portfolio level.

**The portfolio-strategic conversation looks like:**

> *"Capita, looking at the next 36 months, here are 23 central-government BPO contracts coming up for re-tender. £4.7bn of total contract value across them. You hold 11 today. Sodexo holds 7. Serco holds 5. At your historical 65% renewal rate on this kind of work, projected forward you retain 7 of your 11. If you want to grow market share, you need to take 3 from your peers — and here's the data on which 3 are most displaceable based on incumbent vulnerability and buyer openness signals. That's your three-year capture plan."*

That conversation is fundamentally different from a pursuit-by-pursuit one. It engages the chief financial officer, not the bid team. It ties to revenue forecasts, capacity planning, and capital allocation, not to win/loss adjudication. It is the kind of conversation that justifies a strategic-consulting engagement, not just an annual intelligence retainer.

The MCP tool that other PWIN products call (Qualify, Win Strategy, Verdict) is **lens-neutral** by default — it returns the structured data with all three framings available, and the calling product picks the lens based on the engagement context. Win Strategy in particular consumes the portfolio-strategic lens to drive the multi-year capture-programme methodology described in Section 6.

### Concrete example of one cell

A single dashboard page titled *"NHS & Health × Managed Service"* with three stacked panels:

- **Top panel (Layer 1):** a row of large numbers — 47 contracts, £4.1bn, top-3 share 78%, effective number of suppliers 3.4, trend ↗ consolidating. Sufficiency badge: Reliable.
- **Middle panel (Layer 2):** the credible competitor list (5 names) shown as a table with grip data. Each row clickable for a per-supplier deep dive (which would call the existing supplier-intelligence dossier).
- **Bottom panel (Layer 6):** two side-by-side lists — *"Expiring in next 18 months"* (3 named contracts) and *"Forward pipeline"* (5 named planning notices with provisional total contract value).

A toggle in the page header switches between Challenger and Incumbent framing — no data refresh, just template re-rendering.

---

## Section 4 — Architecture

The product spans both repositories — `pwin-competitive-intel` (data layer + dashboard) and `pwin-platform` (MCP tool surface). Names below are working names; final names get fixed in the implementation plan.

### Components

| Component | Location | Purpose |
|---|---|---|
| Engine module | `pwin-competitive-intel/queries/cube_engine.py` | Owns every cube calculation |
| New table — `cell_summary` | `pwin-competitive-intel/db/schema.sql` | Pre-computed per-cell aggregates the consumers read |
| New column — `notices.opp_type` | `pwin-competitive-intel/db/schema.sql` | One-time tagging of every notice |
| New supporting indexes | `pwin-competitive-intel/db/schema.sql` | Three indexes for cube query patterns |
| Dashboard tab | `pwin-competitive-intel/dashboard.html` | New "Competitive Cells" tab alongside Buyers / Suppliers / Frameworks |
| Local data API | `pwin-competitive-intel/server.py` | Three new `/api/cube/*` endpoints |
| MCP tool query module | `pwin-platform/src/competitive-intel.js` | Query functions for the three new MCP tools |
| MCP tool registration | `pwin-platform/src/mcp.js` | The three new tools registered |
| Production data API | `pwin-platform/src/api.js` | Same three endpoints exposed via HTTP |
| Marketing report generator | `pwin-competitive-intel/queries/generate_concentration_report.py` | Picks 5–10 high-value cells, renders markdown |
| Marketing report output | `pwin-competitive-intel/reports/` | Generated reports |

### Engine — the load-bearing piece

`cube_engine.py` owns three primary functions:

- **`tag_notices()`** — runs the sector + opportunity-type tagging pass over notices. Sector tagging reads from the canonical buyer layer (already done). Opportunity-type tagging applies the procurement-category-code mapping plus the title-keyword fallback. Idempotent — safe to re-run after each ingest cycle.
- **`compute_cell_summary(sector, opp_type, value_band=None, time_window_years=5)`** — for one cell, returns the full Layer 1 + Layer 2 + Layer 6 view as a structured Python dictionary. This is the function every consumer ultimately calls.
- **`refresh_cell_aggregates()`** — runs `compute_cell_summary` over all 90 cells and writes results into the pre-computed `cell_summary` table. Run nightly as part of the existing scheduler.

### The pre-computed cell_summary table

Stops every page load and every AI tool call from re-scanning thousands of awards. One row per cell — schema is small:

- Identity columns: `sector`, `opp_type`
- Headline numbers: `total_contracts`, `total_value`, `top_3_share`, `top_5_share`, `effective_n_suppliers`, `trend`, `sufficiency_flag`
- Detail (JSON column): the credible competitor list with per-supplier grip data, plus the displacement windows (expiring contracts and forward pipeline items)
- Metadata: `last_refreshed_at`

### Three new supporting indexes

- `(sector, opp_type)` on the notices table
- `(canonical_supplier_id, sector, opp_type)` on awards
- `(buyer_canonical_id, year)` on awards

### The three MCP tools

- **`get_competitive_cell(sector, opp_type, value_band?, lens?)`** — returns the full cell view as structured JSON. The `lens` parameter (challenger / incumbent / neutral) controls the framing copy; the underlying numbers are identical. Default lens is neutral.
- **`get_credible_competitors(sector, opp_type)`** — returns just the named credible-competitor list with grip data. A focused tool for callers (Win Strategy in particular) that only want the competitor names, not the full cell view.
- **`find_cells_for_supplier(canonical_supplier_id)`** — given a named supplier, returns every cell where they are in the credible-competitor list, sorted by their share. Useful for the supplier-side view (*"where am I a credible competitor?"*) and for the eventual Layer 5 challenger-evidence work in v3.

### Staged build order — the four stages of D

Each stage builds on the previous. The engine is the load-bearing piece — once it's stable, stages 2/3/4 are mostly rendering.

1. **Stage 1 — Engine.** `cube_engine.py`, the new tables and column, the tagging pass, the cell summary computation, the refresh job. Nothing user-facing yet. The cube is real but only callable from a Python REPL.
2. **Stage 2 — One-off marketing report.** `generate_concentration_report.py`. Picks 5–10 high-value cells, calls the engine, produces the markdown. This is the immediate marketing-facing output; it ships before any UI work.
3. **Stage 3 — Dashboard tab.** Updates to `dashboard.html` plus the three new local API endpoints. The internal user-facing surface.
4. **Stage 4 — MCP tools and platform API.** Updates to `competitive-intel.js`, `mcp.js`, `api.js`. The integration surface for Qualify / Win Strategy / Verdict to consume.

---

## Section 5 — Cloud-Platform Alignment

> **Update — 2026-05-02 pm.** The cloud architecture spec landed during the same brainstorming day as this spec, targeting Google Cloud UK PostgreSQL on Cloud SQL (not Cloudflare D1 as initially assumed in this section's first draft). After comparing the two, the agreed sequencing is: **the cube build does not begin until the Wave 1 cloud migration completes.** This avoids double schema work (SQLite then PostgreSQL), removes the parallel-track coordination overhead, and lets the cube ship directly against the production-grade architecture. To preserve commercial momentum, a directional concentration analysis (Section 7) ships now using existing data and coarse mappings — providing the launch and positioning material the polished cube would otherwise produce. Compare-and-contrast captured in the wiki at `wiki/meta/2026-05-02-competitive-cube-brainstorm.md`.

The remainder of this section is the original alignment register, retained for traceability and to inform the post-migration cube build.

### Points of contact

| Decision area | Owned by this spec | Owned by cloud spec | Joint sign-off |
|---|:---:|:---:|:---:|
| `opp_type` column on notices (name, semantics, values) | ✓ | | |
| `opp_type` migration mechanics (backfill timing, deployment) | | ✓ | |
| `cell_summary` table schema (columns, JSON contract) | ✓ | | |
| Where `cell_summary` physically lives in the production database | | ✓ | |
| New supporting indexes (which fields and why) | ✓ | | |
| Index storage budget within production database limits | | | ✓ |
| Refresh cadence (nightly) and trigger logic | ✓ | | |
| Where the refresh job actually runs (scheduler, worker, cron) | | ✓ | |
| `cell_summary` table size at full 90-cell coverage | provides estimate | validates against limits | ✓ |
| API endpoint shapes — `/api/cube/*` | ✓ | | |
| Gateway routing and authentication for those endpoints | | ✓ | |
| MCP tool registration and surface | ✓ | | |
| Read-budget profile (3 consumer patterns) | provides inputs | owns cost model | ✓ |
| Whether the cloud database stays as Cloudflare D1 or changes | | ✓ | |
| Local-first vs cloud-first for the marketing report generator | ✓ (local script) | | |

### Alignment protocol — how the two specs stay in sync

1. This spec is committed to the repository as a static input to the cloud architecture work.
2. The cloud architecture spec, when it lands, references this spec by file path and absorbs the inputs flagged below.
3. If the cloud spec proposes anything that contradicts an assumption made here, this spec is updated and re-versioned. The two specs do not drift silently.
4. Before either spec moves to its implementation plan, a joint review confirms the alignment register is correct and complete.
5. Implementation does not begin on either side until both specs are aligned.

### Inputs this spec sends to the cloud architecture work

For convenience to the cloud architect when they pick this spec up:

- **`cell_summary` table size.** Small — 90 rows nominally, perhaps 200 if value-band variants are added in v2. Each row has half a dozen scalar columns plus a JSON column holding the credible competitor list and displacement windows. Total table size: probably under 5 MB.
- **`opp_type` column.** A single short string column on the existing notices table. About 508,000 rows already loaded need a one-time backfill.
- **Three new indexes.** `(sector, opp_type)` on notices, `(canonical_supplier_id, sector, opp_type)` on awards, `(buyer_canonical_id, year)` on awards. Combined storage footprint estimated in the tens of megabytes.
- **Refresh job profile.** Roughly five minutes of compute per nightly run (full 90-cell recomputation against the awards table). No long-running worker needed; an ordinary scheduled job is fine.
- **Read-load profile for the production API.** Three concurrent patterns: dashboard interactive (bursty, sub-second, low row-read per query — eats from the `cell_summary` table); MCP calls from PWIN products (steady, latency-tolerant, deeper queries — also from `cell_summary` in normal operation); marketing report (heavy, infrequent — once-a-week-ish, scans across the full awards table). All reads, no writes from any consumer.
- **Failure modes.** If the nightly refresh fails, the dashboard / MCP tools should serve stale data with a *"last refreshed"* timestamp visible rather than fail. The cube is intelligence, not a transactional system — staleness is acceptable, downtime less so.

### What this spec defers to the cloud spec

- The production database target — confirmed by the cloud spec as **PostgreSQL on Cloud SQL UK** (Google Cloud `europe-west2`).
- Whether the dashboard tab is served alongside the platform or stays on a separate host (cloud spec does not yet address dashboard hosting).
- Whether the MCP server runs co-located with the database (cloud spec confirms: containerised in Cloud Run alongside the HTTP API).
- The full cost calculation for read budget under expected concurrent load.
- Authentication and access control on the production API (today's local API is internal-only; cloud spec specifies Google Workspace SSO via Identity Platform).

This treats the cloud architecture as the senior spec on infrastructure questions and this spec as the senior on data-layer schema and consumer-surface design.

### Reconciliation outcome (post-cloud-spec review)

After reading the committed cloud architecture spec, the alignment is:

- **Schema location.** The new `cell_summary` table belongs in the cloud spec's `intel` schema (not flat). The new `opp_type` column on notices follows the rest of `notices` into the `raw` schema. Indexes follow the underlying tables.
- **Drivers.** Python engine code's `sqlite3` calls become PostgreSQL via `psycopg2` (or async equivalent); the `?` placeholder syntax becomes `%s`. The `ON CONFLICT ... DO UPDATE` clause is portable across SQLite and PostgreSQL — no rewrite needed. Node MCP module's `better-sqlite3` calls become `pg` (node-postgres) async — three query functions to rewrite.
- **Refresh job.** Cron-driven `agent/scheduler.py` step becomes a Cloud Scheduler trigger to the `ingest-pipelines` Cloud Run service running the same Python entry point. The `refresh_cell_aggregates` function itself is unchanged.
- **API surface.** Three new MCP tools and three new HTTP endpoints are additive to the cloud-spec's containerised services — no refactor required, just new registrations in the existing `mcp.js` and `api.js`.

These are mechanical adjustments to the implementation plan, applied during cloud Phase 3 (containerisation) and Phase 4 (verification). The spec itself does not need rewriting — only the plan's task-level code needs the driver and connection-string changes when the cube is finally built.

---

## Section 6 — Out of Scope and Success Criteria

### Deferred to v2 — clear extensions of the same product

- **Layer 3 (per-incumbent vulnerability signals).** Public Accounts Committee mentions, Companies House financial distress flags, *"extensions running long"* anomalies, cancelled procurements as a vulnerability signal. The data sources exist (Public Accounts Committee database, Companies House enrichment, the awards table) but joining them into a coherent per-incumbent vulnerability score is its own piece of work.
- **Layer 4 (buyer-side openness signals).** Procurement-route mix per cell, average bidder count per competition, recent challenger wins as openness evidence, stakeholder turnover at the buyer-side decision-maker. Builds on the existing buyer-behaviour module and stakeholder database — both live, but their cell-level integration is v2.
- **Three-dimensional cube with contract value as a primary axis.** v1 uses value as a slicer on top of the 90 cells. If v1 reveals that the same suppliers don't actually compete across all value bands within a sector-and-type cell, v2 splits the cube to 270 cells. The v1 data will tell us whether that's needed.
- **Portfolio-strategic lens — extended time horizon and projection layer.** v1 ships the framing copy for the portfolio-strategic lens (in Section 3) but holds the underlying multi-year projection math for v2. Specifically:
    - **Extend Layer 6's forward window from 18 months to 36 months for the strategic view, and to 60 months for the strategic-programme tier.** The data is already in `awards.contract_end_date` plus `awards.contract_max_extend` plus the planning-notice feed; the v1 spec just caps the visible window at 18 months. v2 widens it.
    - **Portfolio-projection layer.** Given a named supplier and a target three-year market share, the cube projects forward: with current renewal rates per peer, what does retention look like? What's the gap to target? Which named upcoming contracts close the gap most efficiently per pound of bid spend? This is a calculation, not new data — it sits on top of the existing Layer 1, 2, and 6 outputs. Output: a ranked capture-programme with named target contracts, projected probability of taking each, and required bid-cost commitment.
    - **Renewal-rate-by-incumbent projection.** Layer 2 already captures per-incumbent renewal-versus-new-win mix as a backward-looking metric. v2 promotes it to a forward projection — *"at this peer's historical 62% renewal rate on contracts of this size in this cell, projected forward over 36 months they retain N of their M holdings."*
    - **Multi-cell aggregation per supplier.** A consultancy or outsourcer typically operates across 3–8 cells. The portfolio-strategic lens needs to aggregate one supplier's portfolio across all relevant cells into a single multi-year revenue projection. This requires a `compute_supplier_portfolio(supplier_id, target_share_per_cell)` function in the engine that loops over the supplier's active cells and aggregates the projection math.

### Deferred to v3 — bigger or more situational

- **Layer 5 (challenger-side evidence).** Per-supplier adjacent-cell wins, head-to-head win history against named incumbents elsewhere. Most differentiating piece, most situational. The data shape and the API parameter for *"give me this cell from the perspective of supplier X"* is enough to design now; the implementation waits.
- **AI-based opportunity-type tagging.** v1 uses procurement category codes plus title keyword fallback. If the residual misclassification rate proves problematic, v3 layers an AI pass on the ambiguous tail.
- **Newsroom and programme-distress integration.** Once the newsroom architecture lands and Government Major Projects Portfolio / National Infrastructure and Service Transformation Authority programme-level data is in the database, the qualitative vulnerability signals get materially richer. Not a v1 dependency.

### Explicitly not built at any stage

- A *"who showed up to the bid"* feed. The procurement data does not publish unsuccessful bidders; we infer the credible competitor pool from win history rather than try to manufacture loss data we don't have.
- A forecasting model. The cube is descriptive intelligence about market structure, not a predictive engine.
- Live alerting / push notifications on cell changes. The cube is a pull resource — users go to it when they need it.
- Multi-tenant / per-client cube views. There is one cube. Different clients reading the same cube get the same numbers. Personalisation comes from which lens they apply (challenger vs incumbent) and from Layer 5 (challenger-side evidence) when v3 lands.

### Success criteria — what tells us v1 is working

The build is complete when all four hold:

1. **The engine produces a defensible cell view for any of the 90 cells.** *"Defensible"* meaning: if a sceptical consultant points at a number in the cell and asks where it came from, the engine can show them the underlying contracts. The opp_type tagging is auditable end-to-end.
2. **The marketing-facing report ships and lands.** A 5–10 cell write-up that proves the concentration thesis empirically with hard numbers. It survives external challenge — anyone reading it can ask *"how did you get that?"* and the answer is in the methodology section of the report.
3. **The dashboard tab is sub-second responsive.** Opening any cell view, switching between cells in the cube overview, applying the value-band slicer — all under one second. This validates the pre-computed `cell_summary` table is doing its job.
4. **At least one downstream PWIN product calls the MCP tool live.** Probably Qualify, calling `get_competitive_cell` during a position-strength assessment. The call returns useful structured data the AI prompt can consume. This validates the MCP surface is real and not just decorative.

### Testing approach

- **Engine.** Unit tests for concentration calculations against a small fixture database; a regression test that verifies the cell summary stays stable across two consecutive refresh runs (no spurious churn).
- **Tagging.** A sample of 100 hand-tagged notices used as ground truth, with the inferred opp_type checked against them. Target: 90%+ agreement.
- **Report.** Peer review by someone outside the build before it ships externally.
- **Dashboard.** Manual click-through of the three views on each of the 9 sectors as a smoke test.
- **MCP.** One live integration call from Qualify, end to end, with the returned data inspected.

---

## Section 7 — Interim Directional Analysis (shipped 2026-05-02)

Because the polished cube build is deferred until post-cloud-migration, an interim directional analysis ships now to provide launch and positioning material that the cube would otherwise have produced.

**What it is.** A one-off Python script that runs against the existing SQLite database, substitutes coarse mappings for the polished canonical taxonomies, and produces a markdown report covering the same six insight categories the cube would surface.

**Substitutions made:**

- **Sector** — derived from `canonical_buyers.type` mapped to one of the nine canonical sectors. Defence, Justice & Home Affairs, and Transport cannot be cleanly isolated from Central Government using buyer type alone (Ministry of Defence is `Ministerial department`; courts are `Court` and `Tribunal` but Home Office and Ministry of Justice are `Ministerial department`). The polished cube will route by buyer name patterns to fix this.
- **Opportunity type** — derived from CPV (procurement category code) leading two digits mapped to ~30 directional buckets. The polished cube will use the platform's 10-bucket canonical opportunity-type taxonomy with title-keyword fallback.
- **Credible competitor list** — replaced by simple top-5 by contract value with no recency overlay. The polished cube will apply the 80/20 cut plus recency overlay defined in Section 3.
- **Sufficiency flag** — replaced by a minimum-5-contracts cut (any cell with fewer is dropped). The polished cube will use the three-state Reliable / Directional / Insufficient flags.

**What it produces.** A markdown report at `pwin-competitive-intel/reports/directional-concentration-analysis-2026-05-02.md` covering: total universe, per-sector concentration, sector × CPV-bucket directional cube (top 25 cells by value), direct-award reliance per sector, year-on-year trajectory, forward pipeline density.

**Known data quality limitations of the directional version** (all corrected by the polished cube):

- Total contract values are inflated because framework agreement ceiling values are summed alongside individual contract values without deduplication.
- Some "supplier" names in the data are publisher metadata strings ("see contracts finder notice for full supplier list") rather than real suppliers. The canonical supplier layer hasn't fully cleaned these.
- Six sectors are mappable cleanly from buyer type (Central Government, Local Government, NHS & Health, Education, Emergency Services, Devolved Government); three (Defence & Security, Justice & Home Affairs, Transport) are partially mapped or absorbed into Central Government.
- Trend signals on short windows (recent 12 months versus prior 4 years) are noisy where contract counts are low.

**What the directional analysis is sufficient for:**

- Launch positioning material — proves the structural concentration claim with empirical numbers and named suppliers.
- Founder narrative and analyst briefings.
- Internal commercial planning around which sectors to lead with.

**What the directional analysis is not sufficient for:**

- Per-named-pursuit displacement intelligence in a real client engagement (the polished cube is needed for that).
- External commercial claims requiring two-significant-figure precision (rounding to the nearest 10% works).
- Any analyst-grade citation about Defence, Justice, or Transport sectors specifically.

**Path to retire the directional analysis.** When the polished cube ships post-cloud-migration, the directional analysis script is preserved as historical context but the report it produces is superseded by the cube's marketing-grade output (Stage 2 of the implementation plan).

---

## Glossary — terms used in this spec

- **Cube** — the 9 × 10 grid of (sector, opportunity type) intersections. Each grid square is a cell.
- **Cell** — one intersection. Has 0 or more contracts, 0 or more suppliers populating it.
- **Concentration** — how much of a cell's contract value is held by a small number of suppliers. Measured here by top-3 share, top-5 share, and effective number of suppliers.
- **Effective number of suppliers** — a single number derived from the standard concentration index in competition economics (1 ÷ Herfindahl-Hirschman Index). Captures *"how many suppliers does this cell behave like"* in one figure.
- **Credible competitor list** — the named suppliers a bid team should treat as their actual field for any new bid in the cell. Computed by the 80/20 cut plus the recency overlay (Section 3, Layer 2).
- **Displacement window** — a forward-looking opportunity to attack incumbency in a cell. Either a named contract approaching expiry or a named planning-notice item.
- **Lens** — the framing applied to a cell view. Four valid values: *Challenger* (where is the wedge?), *Incumbent* (where am I exposed?), *Portfolio-strategic* (what's my multi-year capture programme?), or *Neutral* (data only, no framing copy).
- **Portfolio-strategic lens** — the third reading mode (added 2026-05-02 pm). Re-renders cell data for incumbents who want to *grow* multi-year market share, not just defend. Adds time-horizon extension (36–60 months) and a portfolio-projection layer that computes share gap, required-win count, and capture-programme economics across all cells a named supplier operates in. Drives Win Strategy's multi-year capture-programme methodology rather than single-pursuit decision support.
- **Sufficiency flag** — an honest signal about how reliable the concentration metrics are for a given cell. Reliable / Directional / Insufficient based on contract count.

---

**End of design specification.**
