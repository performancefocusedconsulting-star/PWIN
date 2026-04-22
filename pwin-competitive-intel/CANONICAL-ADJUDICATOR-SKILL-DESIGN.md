---
document_type: skill_design_note
subject: Canonical Adjudicator Skill — AI layer that resolves Splink ambiguities and classifies off-framework awards
purpose: design spec for the Phase 2 adjudicator skill referenced in Decision C08 of the canonical layer design register
parent_design: pwin-competitive-intel/CANONICAL-LAYER-DESIGN.md
parent_playbook: pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md
status: active — Milestones A and B complete (2026-04-22)
version: 0.3
created: 2026-04-14
---

# Canonical Adjudicator Skill — Design Note

The adjudicator skill is the AI layer that sits on top of the Splink + framework-lookup pipeline. This note defines its shape: inputs, prompt structure, knowledge files, output schema, human approval loop, and how it consumes the operational playbook.

## Purpose

Three jobs, one skill:

1. **Resolve ambiguous entity clusters.** Splink auto-resolves ~90–95% of buyer/supplier dedup cases. The adjudicator handles the residual 5–10% — the clusters where Splink's match score is mid-band (e.g. 0.4–0.8) and a judgement call is needed.
2. **Classify off-framework awards.** Contracts awarded outside a known CCS framework have no deterministic service tag. The adjudicator assigns the closest framework lot equivalent using title + description + CPV + value + buyer context.
3. **Detect drift and flag quality regressions.** On each weekly run, compare the new canonical state to last week's baseline and flag anything suspicious (sudden supplier mega-merge, MoD's award count halving, a known framework disappearing).

## Who operates it

**Operating model: Route B — Claude Code subscription, human-in-the-loop (decided 2026-04-14).**

- The deterministic pipeline (Splink clustering, framework lookup, drift metrics) still runs on cron — it's free Python, no Claude calls.
- The AI adjudication step runs **interactively in Claude Code** when the user decides to flush the queue. Runs against the existing Max subscription, not the metered API. No incremental per-decision cost.
- The user (sole operator at this stage) reviews every adjudication in the same session. "Auto-promote vs escalate" collapses into a single reviewed flow, though confidence scores are still produced so obvious cases can be skim-approved quickly.
- **Cadence is driven by need, not by the data freshness clock.** The user is not operating as a business yet, so the database does not need to be continuously current. The adjudicator is run when the canonical layer is actually needed for a consuming task (dossier build, query session, validation run), not on a fixed weekly rhythm.

**When to switch to Route A (metered API, scheduled, unattended):**
- Volume outgrows what can be reviewed in a single sitting
- A hired team member or another product needs the canonical layer to be always-fresh
- Canonicalisation-as-a-service is offered to another team or external consumer

## Inputs

Assembled at runtime by the skill runner (same pattern as Qualify's context engine):

| Input | Source | Notes |
|---|---|---|
| Splink ambiguous clusters | pipeline output JSON | One record per cluster with Splink score, candidate raw IDs, their raw names, their raw addresses, their known CH numbers if any |
| Off-framework awards needing classification | pipeline output JSON | One record per award with title, description, CPV, value, buyer canonical ID, existing framework tags if partial |
| Canonical entity glossary | `canonical_glossary.json` (curated) | Hand-maintained records for MoD, NHS England, top councils. Aliases, subsidiaries, legacy IDs, historical name changes. |
| Framework lot taxonomy | `framework_taxonomy.json` (generated from CCS) | All lots across the 8 CCS frameworks with descriptions, examples, typical value bands, buyer archetypes |
| Operational playbook | `CANONICAL-LAYER-PLAYBOOK.md` (already exists) | The rule-of-thumb knowledge — coverage math, cleaning patterns, edge cases, "always review" triggers |
| Last week's baseline | previous canonical snapshot | For drift detection |
| Recent adjudicator decisions | `adjudicator_decisions.jsonl` | Rolling log, used as few-shot examples |

## Knowledge files

Three structured JSON files the skill loads alongside the playbook prose:

### `canonical_glossary.json`

Hand-curated records for the top ~100 canonical buyers that account for the bulk of £1m+ award volume. Shape:

```json
{
  "canonical_buyers": [
    {
      "canonical_id": "mod",
      "canonical_name": "Ministry of Defence",
      "aliases": ["MOD", "Ministry of Defence", "Min of Def", ...],
      "subsidiaries": [
        {"canonical_id": "des", "canonical_name": "Defence Equipment & Support"},
        {"canonical_id": "dstl", "canonical_name": "Defence Science and Technology Laboratory"},
        ...
      ],
      "legacy_ids": ["GB-FTS-...", "PPON-..."],
      "known_ch_numbers": [],
      "notes": "MoD fragments across 1,272+ FTS IDs. Subsidiaries are kept distinct (DE&S is a trading entity, not a rollup to MoD)."
    }
  ]
}
```

### `framework_taxonomy.json`

Generated from CCS lot publications. Shape:

```json
{
  "frameworks": [
    {
      "framework_id": "MCF4",
      "framework_rm": "RM6309",
      "framework_name": "Management Consultancy Framework 4",
      "lots": [
        {
          "lot_id": "MCF4-L5",
          "lot_name": "Finance",
          "description": "...",
          "typical_examples": ["...", "..."],
          "typical_value_band": "£1m–£20m",
          "exclusions": ["...audit work belongs to Audit Services..."]
        }
      ]
    }
  ]
}
```

### `adjudicator_decisions.jsonl`

Append-only log of every decision the skill has made, with outcome (auto-promoted, human-approved, human-rejected). Used as few-shot examples for subsequent runs. Seeds the skill's institutional memory.

## Prompt structure

Uses the Alex Mercer pattern (persona memory). The adjudicator persona — working name **Morgan Ledger** — is a senior data steward with a procurement background. Cautious by default, transparent about uncertainty, refuses to guess when evidence is thin.

```
## Identity
You are Morgan Ledger, canonical data steward for PWIN's competitive intelligence
database. You take raw FTS publisher data and decide when two rows are the
same real-world entity, when they are not, and how to classify contracts
against the CCS framework service taxonomy.

## Hard rules
- You never auto-merge two canonical entities already hand-curated in the glossary.
  Subsidiaries are kept distinct unless the glossary explicitly rolls them up.
- You never classify an off-framework award above £5m without a confidence score
  of 0.9+. If you can't reach that threshold, escalate for human review.
- You show your working. Every decision has: candidate IDs, evidence considered,
  playbook rule applied (if any), confidence score, escalate-or-promote flag.
- You follow the playbook. When the playbook says "always review", you never
  auto-promote regardless of Splink score.

## Inputs you will receive per decision
- Splink cluster or off-framework award
- Glossary (read-only)
- Framework taxonomy (read-only)
- Playbook excerpts relevant to this decision
- Recent few-shot examples

## Output schema
{
  "decision_id": "...",
  "decision_type": "buyer_merge | supplier_merge | service_classification | drift_flag",
  "recommendation": "auto_promote | escalate | reject",
  "confidence": 0.0–1.0,
  "canonical_target": "...",      // canonical_id the raw rows should map to
  "evidence": ["...", "..."],     // bullet list of what drove the decision
  "playbook_rule": "...",         // if any rule was applied, cite it
  "uncertainty_notes": "..."      // what would change your mind
}
```

## Output schema (structured)

Every adjudicator invocation returns a JSON array of decision objects. The runner consumes them, writes to canonical tables for `auto_promote`, writes to a staging table for `escalate`, and discards `reject`. Every decision is appended to `adjudicator_decisions.jsonl`.

## Human approval loop

For `escalate` decisions the runner produces a short HTML review page (same pattern as the Qualify report) listing the staged decisions with the evidence and the adjudicator's reasoning. The reviewer clicks approve/reject/modify. Approved decisions promote to canonical tables and are added back to the few-shot log. This keeps the loop tight — the reviewer sees Morgan's reasoning, doesn't start from scratch, and the skill learns from every resolution.

## Drift detection

Runs once per weekly cycle, after promotion. Compares canonical-layer metrics to last week's snapshot. Flags:

- Canonical buyer count change >5%
- Canonical supplier count change >5%
- Any glossary-curated buyer losing >20% of award volume
- Any framework lot's tagged-award count changing >30%
- Any supplier jumping more than 3 confidence bands on any metric

Flagged drift goes to the human review page tagged `drift_flag` with last week / this week numbers and the skill's hypothesis.

## Cost model

**Route B (current operating model): £0 incremental.** The adjudicator runs inside Claude Code against the Max subscription. No per-token cost. The only "cost" is the user's time in the review session (expected 20–40 minutes per run once the queue stabilises).

**Route A (future, if and when scheduled unattended operation is needed):** cost to be measured in Phase 0 Discovery, not fabricated here. Real cost drivers, in order of impact:

1. **Prompt caching hit rate** — persona + playbook + glossary reused across calls in a 5-minute window reads at ~10% of normal input cost. Biggest single lever.
2. **Model choice** — Haiku ~5× cheaper than Sonnet, Opus ~5× more expensive. Adjudication probably wants Sonnet; bulk off-framework classification may be fine on Haiku.
3. **Batch mode** — 50% of standard pricing for non-latency-sensitive runs. Weekly cron is a natural fit.
4. **Few-shot retrieval strategy** — loading all-decisions-ever per call blows tokens linearly; nearest-neighbour retrieval keeps it bounded.
5. **Actual volume** — Splink ambiguous cluster count and off-framework contract count for the £1m+ universe are unknown until Phase 0 measurement.

A Phase 0 cost measurement should run a representative sample of 100 ambiguous clusters and 100 off-framework awards end-to-end, count tokens, and quote a weekly operating cost with a single significant figure of confidence. Until then, any API cost number is a guess.

## Integration with the pipeline

Under Route B, the pipeline splits into a **scheduled deterministic half** (free, unattended) and an **on-demand AI half** (Claude Code session when needed):

**Scheduled (cron, no Claude calls):**
```
1. FTS incremental ingest → raw tables
   (weekly: OCP bulk ingest → raw tables, also)
2. Splink pipeline → staged canonical proposals table
3. Framework lookup → deterministic service tags for call-offs
4. Drift metrics computed → drift_flags staging table
```

**On-demand (user opens Claude Code, invokes the adjudicator skill):**
```
5. Skill reads staged proposals + drift flags + glossary + playbook
6. Morgan adjudicates each item, produces structured decisions
7. User reviews decisions inline in the session, approves/rejects/modifies
8. Approved decisions promoted to canonical tables
9. All decisions logged to adjudicator_decisions.jsonl for future few-shots
```

The staging tables accumulate between sessions. There is no data-freshness SLA — the canonical layer is brought up to date when a consuming task needs it (dossier build, query session, validation run).

## What this skill does NOT do

- **It does not edit raw tables.** Raw tables are always write-through from publisher data (Decision C09). The adjudicator writes to canonical and mapping tables only.
- **It does not invent new canonical entities from thin air.** If a buyer doesn't match anything in the glossary and Splink can't cluster it confidently, it becomes its own canonical record, one-to-one with the raw row. Hand-curation can later merge it into a mega-entity.
- **It does not guess service classifications for contracts it can't confidently tag.** Unclassified contracts stay unclassified. A "Unclassified / Other" bucket is honest; a wrong tag is worse than no tag.
- **It does not override explicit playbook rules.** The playbook is the constitution. Morgan is bound by it.

## Open design questions

1. ~~Where does the skill run?~~ **Decided 2026-04-22:** (c) Claude Code plugin skill in `pwin-platform/skills/competitive-intel/canonical-adjudicator.yaml`, triggered manually by the operator. Write-backs go via three MCP tools in `pwin-platform/src/mcp.js`: `log_adjudicator_decision` (JSONL append), `promote_canonical_decision` (canonical table mutation), `stage_escalation` (escalation staging table). Route B operating model confirmed — no API cost, Max subscription only.
2. **How are few-shot examples selected at runtime?** All-decisions-ever will blow the context window within months. Need a retrieval step — probably nearest-neighbour on decision type + entity shape.
3. **Human review UX.** Does the review page live in the competitive-intel dashboard, in pwin-bid-execution, or as a standalone tool? Affects how approvals flow back.
4. **Morgan vs Alex.** Two personas now (Alex Mercer for Qualify, Morgan Ledger for canonicalisation). Both follow the same pattern, and that's deliberate — but we should confirm we want a separate identity for data stewardship rather than a generic "system" voice.
5. **Playbook format for skill consumption.** The playbook is currently markdown prose. It's human-readable but the skill will consume the whole file as prompt context. May need a structured extract (`playbook_rules.json`) for token efficiency once the playbook grows past ~500 lines.

## Dependencies and sequencing

| Phase | What's needed | Status |
|---|---|---|
| Phase 0 — Discovery | Splink baseline + value-threshold simulation | Done (see DISCOVERY-REPORT.md) |
| Phase 1 — Pipeline build | Splink configuration, canonical tables, framework lookup | Done — 82,637 canonical suppliers, buyer canonical layer at 70.3% coverage |
| Phase 2 — Adjudicator skill | Skill YAML, skill-runner context types, MCP write tools, framework taxonomy, schema staging tables | **Done 2026-04-22** — Milestones A + B complete |
| Phase 3 — Validation | Run skill against a real `adjudication_queue` batch, validate promote/stage flow end-to-end | Next |

## Change log

| Version | Date | Summary |
|---|---|---|
| 0.1 | 2026-04-14 | Initial draft. Three jobs, prompt shape, knowledge files, cost model, open questions. |
| 0.2 | 2026-04-14 | Switched default operating model to Route B (Claude Code subscription, on-demand, human-in-the-loop). Removed fabricated API cost table; replaced with cost drivers and Phase 0 measurement plan. Pipeline split into scheduled deterministic half and on-demand AI half. |
| 0.3 | 2026-04-22 | **Milestone A + B complete.** Skill YAML at `pwin-platform/skills/competitive-intel/canonical-adjudicator.yaml`. Four context types added to skill-runner.js (`canonical_glossary`, `framework_taxonomy`, `adjudicator_decisions`, `canonical_playbook`). `framework_taxonomy.json` built — v0.1, 5 CCS frameworks, 20 lots. Three MCP write tools added: `log_adjudicator_decision`, `promote_canonical_decision`, `stage_escalation`. Staging tables (`adjudication_queue`, `adjudicator_escalations`) documented in `db/schema.sql`. Open design question 1 resolved — Route B, plugin skill + MCP write tools confirmed. |
