---
document_type: skill_redesign_decision_register
skill: Agent 2 Skill 1 — Supplier Intelligence Dossier
status: phase_0_in_progress
version: 1.0
created: 2026-04-11
source_review: Serco_Dossier_Review_and_Recommendations.md (user-provided, 2026-04-11)
validation_artefacts:
  - pwin-architect-plugin/agents/market-intelligence/output/serco-group-standard.html
  - pwin-architect-plugin/agents/market-intelligence/output/serco-group-standard.json
  - pwin-architect-plugin/agents/market-intelligence/output/serco-group-deep.html (quality probe, disposable)
---

# Skill 1 (Supplier Intelligence Dossier) — v2 Redesign Decision Register

This document captures the decisions, rationale, and build plan for the v2 rewrite of the supplier intelligence dossier skill. It is the working source of truth for the redesign. Update it as decisions evolve.

## Context

The v1 skill was tested by producing standard-mode and deep-mode dossiers on Serco Group plc. The user reviewed the standard output and produced a structured review (`Serco_Dossier_Review_and_Recommendations.md`). That review was then walked through theme-by-theme in a working session on 2026-04-11 and each point was decided. The decisions below are the outcome.

The v1 skill is not being discarded. It is being treated as Version 1: broad supplier narrative dossier. The v2 target is: **deep, neutral, evidence-backed supplier intelligence dossier with uniform service taxonomy, trend analysis, contract business context, narrative signal extraction, and machine-readable downstream handoff.**

## Strategic framing

- The supplier dossier skill is a **neutral upstream intelligence asset.** It researches and compiles. It does not recommend strategy, bid/no-bid, displacement, or counter-positioning. Those belong in Agent 3.
- **JSON is canonical. HTML is rendered from JSON.** The skill emits structured data. A deterministic template renderer produces the human-readable report. The model never writes HTML directly in v2.
- **Uniform taxonomies live as platform knowledge**, not skill-internal. Service taxonomy, narrative theme taxonomy, and claim taxonomy are all shared across Agent 2's skills and consumable by Agent 3.

## Decision register — 12 decisions, all agreed

### Theme 1 — Neutrality & scoring posture

**D03 — Remove strategy-oriented language from the supplier skill.** Adopt as-stated. Strip "attack surface," "displacement," "exploit," "vulnerability map," "highest-value opportunity" from templates, prompts, and output.

**D08 / §13 — Scoring model rewrite (middle path).** Delete the rolled-up `Competitor Threat` and `Vulnerability` headline scores. Keep the factor-level research underneath those scores (margin pressure, contract friction, concentration risk, delivery complexity, commercial aggressiveness, restructuring signals, buyer dissatisfaction, partner dependency) but present them as neutral supplier properties in a new **Risk & Exposure Profile** section — not rolled into a headline number. Keep `Sector Strength` as a headline score. Add the review's proposed supplier-shape headline scores: `Supplier Breadth`, `Evidence Quality`, `Scrutiny Exposure`, `Service-Line Concentration`, `Strategic Identity Confidence`. Publish underlying factors in the machine-readable JSON with neutral names so Agent 3 can compute its own rollups.

### Theme 2 — Depth upgrades to existing modules

**D04 — Multi-year financial trajectory.** Replace current-year financial snapshot with multi-year trend analysis. Metrics: revenue, operating profit, margin, order intake, book-to-bill, order book, pipeline, free cash conversion, capital allocation, dividends/buybacks, M&A, leverage. For each: what changed, likely driver, signal, confidence. **Minimum 3 years, 5 preferred.** Softened from the review's 5-year minimum to accommodate private/PE-backed suppliers where Companies House filings lag and strip detail.

**D06 — Contract portfolio rebuild.** Every contract row must carry service-line tag (from the uniform taxonomy), strategic importance (Core / Significant / Supporting / Peripheral), business-context interpretation ("why does this contract matter"), capability proof value, route-to-market significance, and successor-route expectation. **Blocked by taxonomy lock** — cannot build until Phase 0 design session produces the taxonomy.

**D07 — Signal watch list reframed as synthesis layer.** Rather than being an independent research stream, the signal watch becomes a curation layer that pulls the top signals from each new module (management narrative, market voice, bid outcomes) into a single "what to watch next" dashboard with review-by dates. It does not do its own research — it curates.

### Theme 3 — New modules

**§10 / D10 — Uniform service taxonomy and service-line profile.** Every supplier decomposed against a canonical 3-level taxonomy (domain → service line → sub-service). Every supplier receives a **Service Line Profile** showing weighted significance (Core / Significant / Supporting / Peripheral / Not Evidenced), confidence, and flagship evidence per service line. **The taxonomy lives as platform knowledge** at `~/.pwin/platform/service-taxonomy.json`, shared across supplier dossiers, client profiles, sector scans, and Agent 3 competitive mapping. **A dedicated taxonomy design session is required before any code changes** — stress-test against 6–8 real suppliers (Serco, Capita, Mitie, Sopra, Atos, CGI, Fujitsu, Accenture) to validate coverage.

**D11 — Market voice / positioning / narrative signals.** Mine annual reports, CEO/CFO commentary, press releases, leadership statements, thought leadership, and partner announcements to extract how the supplier wants to be understood. **Headline output is the narrative-to-reality alignment verdict** (aligned / partial / aspirational / misleading), not theme frequency counts. Uses a shared platform-level narrative theme taxonomy (operational excellence, digital, AI, resilience, citizen outcomes, social value, partnership, sustainability, innovation).

**D12 — Observed bid outcomes and competitive interaction signals.** Pattern analysis of FTS procurement data to identify incumbent displacement, framework gains/losses, and award-by-award rival patterns. **Strict inference-vs-confirmation honesty** — most "losses" will be inferred from successor-award patterns, not confirmed bid outcomes. **No precise win rates without credible denominators.** Output is pattern-level findings (e.g. "Serco has lost 3 of the last 5 NHS FM rebids to Mitie"), not a win-rate scorecard.

### Theme 4 — Evidence & output plumbing

**D02 — Evidence ledger with material/prose split.** Full per-claim evidence register with claim_id, claim_text, field_name, value, source_tier, source_name, URL, pub_date, retrieved_at, effective_date, is_direct/inferred, confidence, stale_after_days, contradiction_flag. **Applied to material claims only** (anything that feeds a score, structured field, contract row, financial metric, or executive summary). Supporting narrative prose uses inline source + date + confidence citation as now. Prevents ledger fatigue while preserving lineage where it matters.

**§11 — Claim taxonomy.** Every material claim tagged as `verified_fact`, `derived_estimate`, `analytical_hypothesis`, or `signal_to_monitor`. Each evidence ledger entry carries a `claim_type` field. **Visually differentiate the four types in the HTML render** (different badges, colours, or icons) so a reader can scan a section and immediately see what is solid versus hypothesis.

**D09 — Dual output, JSON-canonical architecture.** Skill produces two artefacts: JSON machine-readable package (authoritative) and HTML human-readable report (rendered from JSON). **Architectural principle: the model never writes HTML directly.** A deterministic template renderer fills the HTML template from JSON fields. Requires building a small renderer (JS or Python script, template + variable substitution + table loops + conditional sections). Machine output structure: `supplier_profile`, `service_line_profile`, `financial_trajectory`, `strategic_contracts`, `strategic_frameworks`, `management_narrative`, `market_voice_signals`, `bid_outcome_signals`, `risk_exposure_profile`, `evidence_register`, `known_unknowns`, `contradictions`, `refresh_metadata`.

## Decisions deliberately NOT adopted

- **Full 5-year financial history as minimum.** Softened to 3-year minimum, 5 preferred, to accommodate private suppliers.
- **Signal watch as independent research stream.** Reframed as synthesis layer over new modules to avoid double-counting signals.
- **Full ledger entry for every citation.** Scoped to material claims only to avoid token cost and reader fatigue.
- **Back-fill JSON for the deep Serco probe.** The deep HTML was a quality probe, disposable once comparison is complete. No paired JSON needed.

## Dependencies

1. **Service taxonomy must exist** before D06 (contract tagging), D10 (service profile), D11 (narrative taxonomy pattern)
2. **Schemas must be locked** (evidence ledger + claim taxonomy + machine output structure) before any new writing begins
3. **Scoring model finalised** (Risk & Exposure factor list + new headline scores) before AGENT.md Skill 1 rewrite
4. **Renderer must exist** before JSON-first skill can produce deliverable artefacts
5. **D03 language cleanup** is trivial, can happen in parallel with anything

## Build plan — four phases

### Phase 0 — Design lock (blocks everything else)

Three focused working sessions, each producing a concrete committed artefact:

| Session | Duration | Output artefact |
|---|---|---|
| **Taxonomy design** | 3–4 hours | `~/.pwin/platform/service-taxonomy.json` stress-tested against 6–8 real suppliers | **DONE** 2026-04-12 — v2.0, 13 categories |
| **Schema design** | 2–3 hours | Updated `supplier-dossier-schema.json` with evidence ledger, claim taxonomy, new module fields, machine output structure | **DONE** 2026-04-12 — v2 schema, 16 sections |
| **Scoring model** | 1–2 hours | Scoring spec: exact factors and weights for the five new headline scores and the Risk & Exposure factor list | Pending |

**Recommendation: run these as three separate sessions, not one marathon.** Taxonomy session first — it's the structural spine everything else hangs off.

### Phase 1 — Infrastructure

- Build the JSON→HTML renderer (template + variable substitution + loops + conditionals). Half to one day.
- Commit platform knowledge files (service taxonomy, narrative theme taxonomy).
- **D03 language cleanup can run in parallel here** — trivial text edits to AGENT.md and templates, quick win.

### Phase 2 — Skill rewrite

- Rewrite Skill 1 section in [AGENT.md](AGENT.md) against new schema and principles.
- Update `supplier-dossier-report.html` template for new sections (Service Line Profile, Financial Trajectory, Market Voice, Bid Outcomes, Risk & Exposure Profile, visual claim-type badges).
- Update prompts to emit JSON-first against the new schema.
- 1–2 days of work.

### Phase 3 — Validation

- Re-run Serco as primary validation case.
- Run 1–2 contrasting suppliers (suggest Capita for a comparable BPO/BPS and Mitie for a pure FM contrast).
- A/B comparison against the v1 standard and v1 deep outputs.
- Confirm the v2 output actually delivers the intelligence density the review demanded.

## Open questions for Phase 0

To be resolved in the design sessions:

1. **Taxonomy coverage edge cases** — where do consulting firms, research/evaluation services, contact centres, policy advisory sit? Does "Professional and Advisory Services" cover Deloitte, Accenture, and PA Consulting cleanly?
2. **Exact weights for the five new headline scores** — the review proposes the score names but not the factor weightings. Needs locking.
3. **How to treat private/PE-backed suppliers where Companies House is the only financial source** — separate schema variant or same schema with more fields as nullable?
4. **Renderer language** — JS (Node) or Python? Depends on where else the PWIN platform does rendering. Check `pwin-platform/src/` before choosing.
5. **Visual claim-type differentiation** — which four visual treatments for fact / estimate / hypothesis / signal? Needs a small design pass.

## Change log

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-11 | Initial decision register. All 12 decisions agreed in theme-by-theme working session. Phase 0 pending. |
| 1.1 | 2026-04-12 | Taxonomy design complete (service-taxonomy.json v2.0, 13 categories). Schema design complete (supplier-dossier-schema.json v2, 16 sections, all 12 decisions implemented). Scoring model session remains. |
