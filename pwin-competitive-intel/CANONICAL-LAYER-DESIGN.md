---
document_type: design_decision_register
subject: FTS canonical data layer (entity resolution + service classification + cleaning)
purpose: precondition for Skill 1 v2 supplier dossier validation and any internal query interface over FTS data
status: phase_0_discovery_pending
version: 1.0
created: 2026-04-11
related:
  - pwin-architect-plugin/agents/market-intelligence/SKILL-1-REDESIGN.md
  - pwin-competitive-intel/README.md (known limitations section)
---

# FTS Canonical Data Layer — Design Decision Register

This document captures the design decisions for the canonical/cleaning workstream that sits between the raw FTS database and any consumer (Skill 1 v2 supplier dossier, an internal query interface, downstream Agent 3 strategy work). It is the source of truth for the data layer redesign. Update it as decisions evolve.

## Context

The pwin-competitive-intel database holds 174,817 notices and 161,120 suppliers from the UK Find a Tender Service plus the OCP bulk historical file. The raw data has well-known structural problems documented in the `README.md` known-limitations section:

- **Buyer fragmentation** — Ministry of Defence currently has ~1,272 distinct buyer IDs (PPON variants, legacy GB-FTS IDs, case variants, subsidiaries like DE&S/DSTL/DIO). Same fragmentation pattern applies to NHS, large councils, and most multi-entity public bodies.
- **Supplier coverage gap** — only ~27% of suppliers carry a Companies House number; the remaining 73% are publisher name-only entries with no structured ID.
- **Service classification absent** — notices carry CPV codes which are unreliable (publisher-chosen, often wrong, poorly understood by bid teams). No service taxonomy is currently applied.
- **Framework values mis-stated** — OCDS records framework *ceilings*, not realised spend.

These limitations were tolerable while the database was used as raw enrichment for Qualify and the internal dashboard. They become **blocking** for Skill 1 v2 supplier dossier validation, because you cannot say "Serco's top buyers are X, Y, Z" if MoD is fragmented across 1,272 entities. They are also blocking for any query interface that lets a bid director ask "what P3M consulting work has the Home Office bought from whom in the last 12 months."

## Strategic posture (decisions agreed 2026-04-11)

### Decision C01 — Internal tooling only

The canonical layer and any query surface built on top of it are **internal tooling for PWIN consulting use**, not a public product. Three external-product postures were considered (paid Tussell-style product, free lead-gen tool, internal only) and the internal-only posture was chosen.

**Why:** the consulting offering is the commercial vehicle. The data layer reinforces it. Going head-to-head with Tussell, Stotles, or Spend Network as a paid product is a different game with different economics.

**How to apply:** the data model can be opinionated about PWIN consulting needs. No need to handle every edge case in the FTS dataset. No need for general-purpose APIs, public access, or per-tenant separation. The canonical layer serves a small, expert internal audience.

### Decision C02 — Two consumers, one canonical layer

The same canonical layer feeds **two distinct consumers**:

1. **Skill 1 v2 supplier dossier** (and downstream Agent 3 strategy work) — needs canonical buyers, canonical suppliers, service-tagged contracts to produce evidence-backed dossiers.
2. **Internal query interface for bid directors** — needs the same canonical layer to answer task-oriented questions like "Home Office P3M consulting awards over £1m in the last 12 months." This may eventually become a simple guided form, a natural-language query box, or a per-buyer dashboard. **Not a Phase 1 deliverable** — but the data layer is built to support it from day one.

**Why:** building the canonical layer good enough for the dossier is barely more work than building it good enough for both. Building it dossier-only and retrofitting later wastes effort.

### Decision C03 — Value threshold filtering

The canonical layer applies a value-based filter to scope the relevant universe:

- **Consulting commissions:** £1m and above
- **All other service types:** £2–3m and above (exact threshold to be tuned in Discovery)

**Why:** the bulk of the 174k notices are sub-£100k POs, micro-procurements, and tail-end framework call-offs that PWIN consulting will never bid for, qualify, or care about. Filtering them out at the canonical layer reduces the relevant universe from ~174k notices to an estimated ~20–30k, with proportional reductions in canonical buyer count (~3k from 118k) and canonical supplier count (~5k from 161k).

**How to apply:** raw notices are retained in the database but the canonical layer's `canonical_notices` view applies the threshold. Downstream consumers query the canonical view by default. The raw layer remains available for any future analysis that needs the tail (e.g. competition intensity signals where supplier counts matter).

### Decision C04 — Framework-lot taxonomy, not CPV

CPV codes are explicitly rejected as the primary service taxonomy. Reasons:

- Publishers pick the closest available CPV rather than the right one
- Same service maps to multiple plausible CPV codes
- Bid directors do not think in CPV, never have, never will
- Coverage is inconsistent across publishers

The canonical service taxonomy is built from **published CCS framework lot structures**, because:

- They already exist and are authoritative (CCS publishes them)
- They map directly to how buyers actually buy
- Suppliers are already classified against them — every framework holder has a lot allocation visible in CCS data
- Bid directors and capture leads already speak this language ("we're going for MCF4 Lot 5" is meaningful and shared vocabulary)
- They get refreshed when frameworks renew, so there is a natural maintenance cycle

### Decision C05 — Eight CCS frameworks form the canonical scheme

The taxonomy is built from the lot structures of these CCS frameworks (all live or recent at 2026-04-11):

| Domain | Framework | Approx lots | Covers |
|---|---|---|---|
| Management Consulting | **MCF4 (RM6309)** | ~9 | Strategy, transformation, P3M, finance, people, ops, tech consulting |
| Digital Services | **DOS6 (RM1043.8)** | 4 | Digital outcomes, specialists, user research |
| IT / Cloud Services | **Tech Services 4 (RM6259)** | ~6 | Transition, transformation, ops services, EUC, networks |
| Cloud Procurement | **G-Cloud 14 (RM1557.14)** | 3 | Cloud hosting, software, support |
| Cyber Security | **CAS (RM6263)** | ~5 | Cyber assessment, advisory, monitoring, incident response |
| HR / People | **People Services (RM6277)** | Several | Recruitment, training, workforce |
| FM / Workplace | **Workplace Services (RM6232)** | Several | FM, real estate, workplace consulting |
| Estates / Property | **EPS (RM6165)** | Several | Construction consulting, property advisory |

Combined, this produces an estimated **40–50 service categories** rooted in published CCS taxonomies. Discovery will confirm the exact lot count and validate framework selection.

### Decision C06 — Hybrid classification: framework lookup + LLM adjudication

Service classification uses the same hybrid pattern as entity resolution:

1. **Framework call-offs** — deterministic lookup. The contract was awarded via a known framework lot, so the lot ID *is* the service classification. Free, instant, perfect accuracy.
2. **Off-framework awards** — LLM classification against the same lot scheme. Given title + description + estimated CPV + value + buyer, the classifier maps the contract to the closest framework lot equivalent. Cheap (~£20–50 to classify the entire historical residual once with a small model, pence for the weekly delta), auditable, explainable.

**Why hybrid:** doing this entirely in an LLM is unnecessary and expensive when a large proportion of relevant notices are already framework call-offs. Doing it entirely deterministically loses the off-framework universe, which is where many of the highest-value direct awards live.

### Decision C07 — Splink for entity resolution

[Splink](https://github.com/moj-analytical-services/splink) is the chosen tool for buyer and supplier entity resolution. Built and maintained by the UK Ministry of Justice analytical services team, MIT licensed, designed for probabilistic record linkage at UK government data scale, backed by DuckDB/SQLite/Spark. Supports both deduplication (within FTS) and linkage (against the Companies House register for the 73% of suppliers without a CH number).

**Why Splink over alternatives:** built for this exact domain by the team that linked criminal-justice records at MoJ. Scales without re-platforming. Explainable Fellegi-Sunter match scores rather than opaque ML. Supports active learning for edge cases. Free.

Other tools considered and rejected: `dedupe` (smaller scale, less suited to government data), `recordlinkage` (older, simpler, less scalable), `rapidfuzz` plus custom rules (reinvents Splink), OpenRefine (interactive only, no pipeline story), LLM-based fuzzy matching (prohibitively expensive and unauditable at this scale).

### Decision C09 — Raw layer is write-through, canonical layer is bulk-safe

Weekly OCP bulk imports and nightly FTS incremental ingests write directly to the **raw** tables (`buyers`, `suppliers`, `notices`, `lots`, `awards`, `award_suppliers`, `cpv_codes`). No manual cleaning is ever performed on those tables, because `upsert_buyer` and `upsert_supplier` unconditionally overwrite the `name` column on every refresh — any hand-edits made at the raw layer would be silently lost next Monday.

All cleaning, deduplication, canonicalisation and service-tagging lives in **separate canonical tables** (`canonical_buyers`, `canonical_suppliers`, `canonical_notices`, plus mapping tables that join raw IDs to canonical IDs). These tables are the output of the Phase 1 pipeline and the Phase 2 adjudicator skill. The weekly bulk never touches them.

**Promotion flow on each weekly run:**

1. OCP bulk and/or FTS incremental writes to the raw tables (overwrites allowed, no hand-edits protected).
2. Canonical pipeline runs Splink + framework lookup + LLM adjudication over the diff since last run.
3. New raw IDs that match existing canonical entities are linked via the mapping tables (no duplicate canonical records).
4. New raw IDs that do not match any existing canonical entity are staged for adjudicator review.
5. Human-approved decisions promote staged rows into canonical tables. Ambiguous rows stay in staging until adjudicated.
6. Canonical tables are the default surface for all downstream consumers (Skill 1 v2 dossier, internal query interface, future Qualify paid tier).

**Why this matters:** it makes the weekly bulk refresh **safe to re-run at any time**. Re-importing the OCP file cannot destroy cleaned data, because the cleaned data lives in different tables. It also means corrections flow one-way: you never edit raw rows to fix them — you record the correction in the canonical/mapping layer so it survives every subsequent refresh.

**How to apply:** any future request to "clean up a supplier name" or "merge these two buyers" is implemented as a canonical-layer edit, not a raw-layer UPDATE. Tooling that invites raw-table edits (dashboards, admin forms) must be explicitly prohibited or routed through the canonical layer.

### Decision C08 — Pipeline-first architecture, LLM-second

The canonical layer is a **deterministic Python pipeline** (Splink + framework lookup + cleaning rules) that runs after every weekly FTS update. **An LLM-backed Claude skill sits above the pipeline as an adjudicator and operator with three jobs:**

1. Review ambiguous match clusters that Splink cannot auto-decide (the 5–10% edge cases)
2. Classify off-framework awards against the framework lot taxonomy
3. Detect drift and flag quality regressions on each weekly run

**Why this split:** LLM-only is too expensive, slow, and unauditable for the bulk work. Pipeline-only cannot resolve the ambiguous cases that matter most. The split puts each tool where it is genuinely best.

## Decisions deliberately NOT adopted

- **CPV codes as the service taxonomy.** Rejected (C04). Unreliable and foreign to the bid audience.
- **Process the entire 174k-notice universe.** Rejected (C03). Filtered by value threshold to ~20–30k.
- **Tussell-style external product.** Rejected (C01). Internal only.
- **Free public lookup tool.** Rejected (C01). Already declined separately on 2026-04-08 per `feedback_qualify_lead_gen_scope`.
- **LLM-only entity resolution and classification.** Rejected (C07, C08). Pipeline-first.
- **Free-form invented service taxonomy.** Rejected (C05). Built from published CCS framework lot structures.

## Dependencies and sequencing

This workstream is **parallel to** Skill 1 v2 redesign, not blocking the early phases. But the dependency tightens at validation time:

| Skill 1 v2 phase | Dependency on canonical layer |
|---|---|
| Phase 0 — design lock | None. Taxonomy/schema/scoring sessions can proceed. |
| Phase 1 — infrastructure | None. |
| Phase 2 — skill rewrite | Soft. The skill prompts can be drafted assuming canonical buyers/suppliers exist. |
| Phase 3 — validation | **Hard block.** Cannot validate v2 against Serco/Capita/Mitie if MoD is still fragmented across 1,272 entities and contracts are not service-tagged. |

The two workstreams should run in parallel and converge at the start of Skill 1 v2 Phase 3.

## Build phases

### Phase 0 — Discovery (1–2 days)

Quantify the problem before committing to the build.

**Outputs:**
- Splink baseline run against the existing DB. How many true canonical entities sit behind the 118k buyers and 161k suppliers?
- Value-threshold simulation. How many notices survive the £1m consulting / £2–3m other-services filter?
- CCS framework coverage check. How many of the surviving notices are framework call-offs (free deterministic classification) vs off-framework (LLM classification needed)?
- Companies House register fuzzy-match feasibility. Can we recover CH numbers for the 73% name-only suppliers?
- Confirm or revise the eight-framework selection.

**Decision gate:** does the scope match the budget? If yes, proceed to Phase 1. If no, narrow further (e.g. raise thresholds, drop frameworks, defer CH recovery).

### Phase 1 — Build the canonical layer (~1 week)

- Splink configuration and training for buyer dedup, supplier dedup, supplier-to-CH linkage
- `canonical_buyers`, `canonical_suppliers`, `service_taxonomy`, `canonical_notices` tables
- Framework lot lookup tables for the 8 CCS frameworks
- Off-framework LLM classifier (cheap model, batch mode)
- Pipeline integration into the nightly cron after FTS ingest

### Phase 2 — Adjudicator skill design (~3–5 days)

- Claude skill that reviews Splink ambiguous clusters, surfaces them for human approval, and writes back canonical decisions
- Quality drift detector that compares each weekly run against the previous baseline
- Maintenance loop for the canonical entity glossary (MoD, NHS, top councils get hand-curated canonical records)

### Phase 3 — Validation

- Re-run Skill 1 v2 Phase 3 against the canonical layer
- Confirm Serco/Capita/Mitie dossiers produce coherent buyer and supplier counts
- Confirm a query like "Home Office P3M consulting awards over £1m in the last 12 months" returns sensible results

## Open questions for Discovery

1. **Exact value thresholds** — £1m consulting is locked, but £2m vs £3m for other services should be set after seeing the distribution
2. **Framework selection** — are the eight CCS frameworks the right cut, or are there others (e.g. Network Services, NHS frameworks, defence-specific) that need to be in scope?
3. **Companies House recovery method** — Splink against the full CH register (~5M companies) is feasible but heavy; might need to scope down to "active companies in relevant SIC codes" first
4. **Canonical entity glossary scope** — how much hand-curation upfront for the obvious cases (MoD, NHS England, the 350+ councils)?
5. **How to surface canonical layer to existing consumers** — does the Qualify intel injection switch to canonical buyers immediately, or only when public release is reconsidered?
6. **Maintenance cadence for the framework lot scheme** — when CCS publishes a new framework version (e.g. MCF5 supersedes MCF4), how does the taxonomy update flow?

## Change log

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-11 | Initial decision register. Eight decisions agreed in working session. Phase 0 Discovery pending. |
| 1.1 | 2026-04-14 | Added Decision C09 — raw layer is write-through, canonical layer is bulk-safe. Locks in the "frozen baseline + clean on arrival" pattern so weekly OCP refreshes cannot clobber cleaned data. |
