# Forensic Intelligence Auditor — Design Spec

**Date:** 2026-04-30
**Status:** Drafted from brainstorm with Paul Fenton on 2026-04-30. Awaiting user review, then writing-plans.
**Authors:** Paul Fenton (design lead, v1.0 input spec), Claude (brainstorm partner, consolidation)

**Predecessor notes:**
- `docs/superpowers/specs/2026-04-29-pursuit-orchestration-design.md` — the orchestrator spec that called the auditor out as its own agent and described the integration points
- `wiki/decisions/forensic-intelligence-auditor-agent.md` — the 2026-04-30 decision to extract the quality function from the orchestrator and elevate it to its own agent (persona, exam question, V1 remit, authority, output sketch)
- `wiki/actions/pwin-forensic-intelligence-auditor-design.md` — the action note that scoped this brainstorm and listed nine open design questions
- Paul's v1.0 input spec (pasted into the 2026-04-30 brainstorm) — the working draft this design consolidates and extends

---

## 1. Why this design exists

The platform produces rich intelligence dossiers — buyer, supplier, sector, incumbency. Downstream agents (Agent 3 win strategy synthesis, Qualify, the consultant's own work) act on what the dossiers say. When a dossier is wrong in a way nobody notices, downstream gets something dangerously wrong.

The Defence Digital dossier produced a leadership claim — that a named individual still led the function — with a cited source, but no claim-date, no source-date, and no contradiction-check against current sources where the same individual is no longer in post. A win strategy built on that claim could have targeted a stakeholder who is or is not in role on a date the dossier never specified. That is the failure mode the auditor exists to catch.

The auditor's exam question is therefore: **what could a downstream agent get dangerously wrong if it trusted this?** Everything in this spec follows from that single question. It deliberately re-frames quality away from "is the dossier good" — a producer-side question — toward "is the dossier safe to act on" — a consumer-side question.

This spec is the V1.0 design. It commits to scope, architectural shape, output contract, and the upstream contract the producing intelligence skills must satisfy. It is paired with the pursuit-orchestration spec, which calls the auditor at phase 3 of its workflow.

---

## 2. Identity

- **Agent name:** Forensic Intelligence Auditor (FIA).
- **Persona:** forensic intelligence auditor safeguarding downstream decisions.
- **Exam question:** *what could a downstream agent get dangerously wrong if it trusted this?*

**Boundary.** The auditor classifies, surfaces, and recommends. It does not generate strategy. It never resolves contradictions between sources. It has no authority to block, retry, or quarantine. The orchestrator, the consultant, and the producing skills decide what to do with the verdict and the actions returned.

This boundary is non-negotiable in the design. The whole value of an auditor is that its judgement is independent of the workflow that consumes its judgement. Giving it veto authority over downstream agents would compromise that independence.

---

## 3. V1.0 scope

**In scope (V1.0):** the four intelligence dossiers — buyer, supplier, sector, incumbency. These are the assets currently on the live platform path that have downstream consumers either today or in the immediate near term.

**V1.1 backlog** (designed and built later, after V1.0 lands and the parameterised engine has been validated on the dossier family):

- Canonical reference layers — the master lists of buyers, suppliers, sub-organisations, government organisations
- Procurement / FTS data — the contract notices, awards, and supplier-history feed
- Stakeholder records — the structured database of contacts, roles, and engagement history
- Newsroom signal stream — the external-signal feed (when built)

**Parked, return when Agent 3 maturity develops:** the orchestrator's phase 7 audit call. Phase 7 audits a synthesis manifest — Agent 3's declaration of what inputs it used and how — and checks provenance, traceability, and flag-handling. That is structurally a different audit problem from auditing a dossier (it audits a manifest making claims about what was used, not the assets themselves), and it depends on Agent 3 emitting a structured manifest in the first place. We come back to it once Agent 3's synthesis-and-manifest pattern has matured. Until then, the orchestrator's phase 7 audit hook is wired but stubbed.

**Out of scope, V2:** synthesis-output audit. Auditing the win strategy itself, the go/no-go recommendation, the gate-pack narrative — the things downstream agents *produce* — is a different audit problem from auditing the *inputs* downstream agents *consume*. This is V2 of the auditor and lives outside this spec entirely.

---

## 4. Architectural model

### 4.1 Single generic parameterised audit skill

The auditor is one audit engine driven by per-asset profiles. Each profile is a JSON file declaring, for that asset type:

- Required sections (so structural completeness is a profile-derived check, not a hand-coded one)
- Volatility classes for each section's claims (e.g. "leadership = high volatility, awarded contracts = low volatility")
- Decision-safety mappings for each section's claims (e.g. "go/no-go-driving claims are Critical")
- Required claim-level fields (the contract from §11)
- Source-tier expectations per section (e.g. "leadership claims should be Tier 1 or 2")

Adding a new asset type means writing a new profile, not writing a new skill. The audit logic — the engine — stays in one place.

### 4.2 V1.0 ships with four asset profiles

One profile per dossier type: buyer, supplier, sector, incumbency. The four profiles share most of their structure (all four dossiers follow the universal skill spec) but differ in the specifics of which sections matter, which claims are Critical, and which volatility classes apply.

### 4.3 Pilot gate before scaling

The parameterised approach is the V1.0 architectural choice but it is not yet validated. The pilot gate is explicit:

1. Build the engine + the buyer-dossier profile.
2. Run the audit against the Defence Digital dossier as the anchor case (see §14).
3. Run the audit against at least one structurally different sibling — incumbency analysis is the natural pick because it is the most synthetic dossier (it cross-references multiple inputs and produces an integrated assessment, where buyer is more straightforwardly descriptive).
4. Re-evaluate: does the parameterised engine generalise cleanly across the dossier family, or does each dossier type need so much profile-specific logic that a per-asset skill split would be cleaner?
5. If it generalises, build the supplier and sector profiles. If it doesn't, fall back to per-asset skills.

This gate exists because option C in the brainstorm (single generic engine) was the right architectural bet but is not yet a proven one. The pilot tests it before the rest of the dossier family commits to it.

---

## 5. Triggers

The auditor runs against a given asset on three triggers — they are not mutually exclusive.

1. **Producer-emit (primary).** Every producing intelligence skill (buyer-intelligence, supplier-intelligence, sector-intelligence, incumbency-advantage-displacement-strategy) calls the auditor on the asset it has just produced. Audit travels with the dossier from the moment of production. This is the load-bearing path.

2. **Consumer-pull (on demand).** Anyone consuming the asset — the orchestrator at phase 3, the consultant via slash command, the freshness monitor when it flags staleness — can pull a fresh audit. The auditor returns the most recent stored audit if it is recent enough; otherwise it re-runs.

3. **Weekly scheduled re-audit.** A sweep job runs weekly across stored dossiers. Any dossier whose most recent audit is older than seven days is re-audited. This catches the freshness and volatility dimensions drifting on assets nobody is currently asking about — a leadership claim made three weeks ago does not need to be re-checked because the dossier itself changed; it needs to be re-checked because the *world* changed.

The cap is therefore "once per asset per refresh, plus on-demand pulls, plus once a week from the sweep" — bounded and predictable. Audit runs are cheap relative to the producing skills they audit, so the trigger overhead is acceptable.

---

## 6. Storage and rollup

### 6.1 Per-asset audit storage

Two parallel destinations. They are written together in a single transaction:

- **Co-located audit file** alongside each asset. Following the universal skill spec sibling-file convention, an audit on `~/.pwin/intel/buyer/defence-digital-dossier.json` writes its audit to `~/.pwin/intel/buyer/defence-digital-audit.json`. This means a dossier and its audit travel together when copied, read, or referenced.

- **Central audit log.** Append-only. One row per audit run. Carries audit ID, asset reference, timestamp, verdict, dimension scores, and a pointer to the full audit artefacts. This is the source of truth for "show me every audit run on this asset over time" and "show me every audit that turned red this week" queries.

### 6.2 Pursuit-level rollup

When the orchestrator (or the consultant) wants a single view across all the inputs a pursuit relies on, the auditor exposes a pursuit-level rollup. V1.0 uses a worst-case rule: if any input asset's most recent audit is red, the pursuit-level verdict is red. Amber if any is amber and none are red. Green only if every input is green.

A weighted-by-stakes rollup — where a red on a high-stakes input outweighs a red on a low-stakes one — is parked for V2. By that point we will have enough audit runs to know empirically which inputs carry decision weight. Picking the weights cold today would be cargo-cult precision.

---

## 7. MCP tool surface

### 7.1 V1.0 prototype — four tools

These four are sufficient to wire every named integration point in the orchestrator spec and in this spec.

1. **`audit_asset(asset_path, asset_type)`** — runs an audit. Used by producing skills on emit and by the consultant on demand. Returns the three artefacts (QA Scorecard, Claim Audit Log, Remediation Queue) and writes them to both storage destinations.

2. **`get_audit_for_asset(asset_id)`** — returns the most recent stored audit for an asset. Used by the orchestrator at phase 3 to read the audit already attached to a freshly-produced dossier without re-running.

3. **`get_pursuit_audit_summary(pursuit_id)`** — reads the most recent audit for every input asset the pursuit lists, applies the worst-case rollup rule, and returns one rolled-up traffic-light verdict plus the per-asset breakdown.

4. **`list_audits_overdue(threshold_days=7)`** — returns assets whose most recent audit is older than the threshold. Used by the weekly scheduled sweep and by the freshness monitor.

### 7.2 V1.0 backlog — two more tools, must-add before V1.0 is considered complete

These two are not on a critical path for the prototype but they are the lens that turns the audit log into pattern recognition. They must be added before the auditor V1.0 is signed off as complete.

5. **`list_red_audits(since_date)`** — returns every audit run that came back red since a date. Powers a "what's gone red this week" management view and is essential for the loop where audit data drives improvement of the producing skills.

6. **`get_audit_history(asset_id)`** — returns the full audit history for an asset (every run, every verdict, every dimension score, every remediation queue, in time order). Powers "is this dossier improving or drifting" diagnostics.

---

## 8. Six audit domains

The auditor evaluates each asset against six domains. Five of them score on a 0–10 scale and feed the verdict; the sixth (Remediation) is the action output, not a scored dimension.

1. **Structural Completeness.** Are all the sections required by the asset profile present? Are the rendered output formats (HTML, markdown, JSON) all present in the right directories so downstream consumers can find them? Output integrity sits inside this domain as a sub-check rather than as its own domain — same kind of question, same place.

2. **Evidence Integrity.** Is the confidence declared on each claim supported by the evidence shape behind it? A claim asserted with high confidence but backed only by a small-sample inference fails this domain. A claim backed by multiple sources of Tier 1 or 2 quality and asserted with appropriate confidence passes it.

3. **Temporal Validity.** Two related but distinct properties:
   - **Volatility (type-level, asset-profile-derived in V1.0).** How likely is *this kind* of claim to change? "Person currently in role" claims are intrinsically high volatility; "contract awarded in 2022" claims are intrinsically low volatility. The asset profile declares the volatility class for each section's claims.
   - **State (instance-level, auditor-set at audit time).** What does this specific claim look like *right now*? Stable, transitional (showing transitional-state contradictions or organisational change), or outdated (source date or claim date past the freshness threshold for its volatility class).

   V1.1 may add upstream volatility tagging on individual claims (so a claim can override its section's profile-default), but V1.0 holds volatility as a profile property and state as an audit-time finding.

4. **Contradiction Exposure.** Are conflicting claims surfaced rather than buried? The auditor's stance is **never resolve, always surface**. Even where a Tier 1 source disagrees with a Tier 4, the auditor records the contradiction with both sources, both tiers, and the topic, and marks it unresolved. The consultant decides which to believe; the auditor never auto-picks a winner. This is the auditor's hardest rule to enforce because it runs counter to the natural urge to tidy up data — but auto-resolution is itself a way the auditor could send downstream wrong, especially when a high-tier source is stale.

5. **Decision Safety.** The auditor classifies each material claim by how dangerous it would be to act on if wrong, and surfaces the unsafe ones explicitly:

   | Level    | Impact                                           |
   | -------- | ------------------------------------------------ |
   | Critical | Drives go/no-go, route-to-market, or stakeholder targeting |
   | High     | Drives win themes                                |
   | Medium   | Provides context                                 |
   | Low      | Background colour                                |

   Classification is auditor-side at audit time, with profile-derived heuristics (e.g. "leadership claims in the buyer profile are Critical when downstream stakeholder mapping is in scope").

6. **Remediation.** Not a scored dimension. The action output of the audit. Detailed in §10.

---

## 9. Source tier table (1–4, authority-first)

A platform-level reference table the auditor uses across all asset profiles. The producing skills emit `source_tier` on each claim; the auditor uses it for evidence integrity, contradiction handling, and decision-safety severity weighting.

| Tier | Source type | Examples |
|---|---|---|
| 1 | Official / primary | The buyer's own published strategy or annual report; the authority's published tender notice; statutory filings (Companies House, Charity Commission); a named on-the-record statement from a relevant officer |
| 2 | Authoritative secondary | Government data feeds (Find a Tender Service, Companies House, gov.uk spend transparency); recognised regulator publications; ONS, Cabinet Office, or NAO reports |
| 3 | Reputable third-party | Established trade press (FT, Civil Service World, GovComputing); analyst houses (Tussell, GlobalData); recognised consultancy reports |
| 4 | Open / unverified | LinkedIn posts, Reddit, blog posts, single anonymous source, AI-generated summaries without a named source behind them |

---

## 10. Three output artefacts

Every audit run produces three artefacts, written together to both storage destinations.

### 10.1 QA Scorecard

The headline view. Carries:

- **Overall verdict:** green / amber / red.
- **Five 0–10 dimension scores:** Source Traceability, Evidence Strength, Freshness, Contradiction Exposure, Decision Safety. The five scored dimensions are facets of the six domains in §8: Source Traceability and Evidence Strength are facets of Evidence Integrity; Freshness is the state-side of Temporal Validity; Contradiction Exposure and Decision Safety map directly to their domains. Structural Completeness is gated, not scored — a structural failure caps the overall verdict at Amber rather than producing its own number.
- **`safeForDownstreamUse: bool`.**
- **`safeUseConditions[]`** — free-text conditions a downstream consumer must satisfy if `safeForDownstreamUse` is conditional (e.g. "Validate leadership and reporting structure before stakeholder mapping").

**Verdict rubric — worst-dimension wins, with a Critical-claim override:**

- **Green** if every dimension scored 8 or higher.
- **Amber** if the lowest dimension scored 5 to 7.
- **Red** if the lowest dimension scored below 5, *or* if any Critical-classified claim fails on Source Traceability, Freshness, or Decision Safety regardless of dimension scores.

The Critical-claim override exists because averaging or worst-dimension alone can hide a single catastrophic claim behind otherwise reasonable scores. The Defence Digital case is exactly this failure mode: most dimensions score amber-or-better, but a Critical claim (the leadership attribution) is unsafe, which forces overall Red.

**Per-dimension 0–10 rubric in V1.0:** placeholder thresholds calibrated against intuition and the anchor case. Tightened during the pilot once we have real audit runs against real dossiers. Pinning precise thresholds before evidence exists is cargo-cult precision and is explicitly not done in the V1.0 spec.

### 10.2 Claim Audit Log

A per-claim audit table. Each row carries:

- `claim_id` (from the producing skill's structured claims block — see §11)
- `claim_text`
- `confidenceDeclared` (the producing skill's stated confidence)
- `confidenceAssessed` (the auditor's view of what the evidence actually supports)
- `evidenceShape` (closed enum: `direct_statement`, `multi_source_convergence`, `inferred_pattern`, `small_sample_inference`)
- `decisionSafety` (Critical / High / Medium / Low, auditor-classified)
- `state` (stable / transitional / outdated, auditor-set)
- `severity` (low / medium / high — how serious is this finding)
- `issue` (free-text description of the audit finding)
- `sources[]` (the source(s) cited, each with tier and date)

This artefact is the working document a consultant reads when the verdict is amber or red and they want to see exactly which claims drove it.

### 10.3 Remediation Queue

The action output. Detailed in §10.4 below.

### 10.4 Remediation queue — closed action-type enum

Each entry carries:

- `priority`: `critical` | `high` | `medium` | `low`
- `owner`: `dossier_agent` | `human_analyst`
- `action_type`: closed enum, eight values (below)
- `target`: the section, claim, or source the action applies to
- `detail`: free-text reason and case-specific instruction

**Action-type enum:**

| Value | Meaning |
|---|---|
| `refresh_section` | Re-run the producing skill on a specific section |
| `add_source` | Find and add a missing or higher-tier source for a claim |
| `dating_check` | Date-stamp a claim missing temporal metadata |
| `expose_contradiction` | Surface a buried unresolved conflict |
| `escalate_to_human` | Too uncertain or too high-stakes for the producing skill alone |
| `await_signoff` | Auditor done; consultant must explicitly accept conditions before downstream use |
| `suppress_from_downstream` | Claim is unsafe; do not feed downstream until fixed |
| `rebuild_from_scratch` | Dossier so degraded that section-level fixes will not help |

The closed enum makes machine-actionable triage possible: the orchestrator can route a `refresh_section` differently from an `escalate_to_human`. The free-text `detail` keeps the human-readable case-specific explanation that is most of the value of the existing prose remediation tasks in the v1.0 input spec.

---

## 11. Upstream contract — what producing skills must emit

The auditor is only as useful as the structure it has to work with. For V1.0 the four intelligence dossier skills must emit a structured claims block; the auditor never parses prose to extract claims.

### 11.1 V1.0 contract (dossiers)

Each dossier carries a top-level `claims[]` block. Each claim is a structured object with six required fields:

- `claim_id` — stable, traceable identifier so the narrative can cite the claim and the audit log can refer to it
- `claim_text` — the assertion itself, in plain prose
- `claim_date` — when the producing skill asserted this (the date of the audit-relevant assertion, not the date of the dossier as a whole)
- `source` — URL, document reference, or structured identifier for where the claim comes from
- `source_date` — when the source itself was published or last updated
- `source_tier` — 1, 2, 3, or 4, from the table in §9

The narrative renders the claims and cites them by `claim_id`. The auditor only audits the `claims[]` block.

### 11.2 V1.1 contract — upstream volatility tag

V1.1 adds a seventh field per claim:

- `volatility` — closed enum: `low` | `medium` | `high`. Emitted by the producing skill when a claim's volatility differs from its section's profile-default. (For example, an "awarded contract" claim is normally low volatility, but if the contract is being re-let the producing skill can override to high.)

V1.0 does not require this field. Volatility in V1.0 is profile-derived from the section the claim sits in. V1.1 lets a claim override its section's profile-default.

### 11.3 Migration / degraded mode

Dossiers produced before the structured `claims[]` contract existed cannot be audited at full fidelity. The auditor operates in a degraded mode against legacy dossiers:

- Best-effort extraction of claims from the narrative and the source register
- Verdict capped at amber regardless of dimension scores (the auditor is honest that it cannot fully audit what it cannot fully see)
- Remediation queue includes a `rebuild_from_scratch` action with `priority: high` against the dossier as a whole

This stops the auditor lying about quality on dossiers it cannot properly assess, while still producing some signal so the consultant knows where the legacy stock is.

### 11.4 Critical-path dependency

The `claims[]` contract is a refactor against the four producing intelligence skills. It is the critical path for the auditor: nothing in this spec works usefully against a real dossier until those skills emit the structured block. The action note tracking this work lives at `wiki/actions/intelligence-skills-claims-block-refactor.md` (to be created).

---

## 12. Hard rules

These are persona-level rules that override any other consideration in the audit run. They are baked into the prompt the engine uses.

1. Never upgrade confidence without evidence.
2. Never collapse conflicting sources.
3. Never allow stale leadership or structure claims through unflagged.
4. Never treat small datasets as deterministic.
5. Always expose uncertainty.
6. Always flag high-risk claims.

---

## 13. Anchor case — Defence Digital "Charlie Forte"

The V1.0 acceptance test is the Defence Digital buyer-intelligence dossier. The dossier produced a leadership claim — that a named individual still led the function — citing a source, but with no claim-date, no source-date, and no contradiction-check against current sources where the same individual is no longer in post.

Under the V1.0 auditor against the buyer-dossier profile, the case must come out **Red**. Specifically:

- The claim is in a section the profile classifies as high volatility (leadership)
- The claim is downstream-relevant for stakeholder mapping, so it is classified Critical for decision safety
- The claim has no `claim_date` or `source_date` in the V1.0 contract sense — Source Traceability and Freshness both score low
- The contradiction with current sources where the individual is no longer in post is flagged under Contradiction Exposure

Under the verdict rubric, even if other dimensions score amber-or-better, the Critical-claim override on Source Traceability + Freshness + Decision Safety forces overall Red. This is the test that the rubric works.

If a future V1.0 audit run produces anything other than Red on this case, the rubric is wrong — not the case.

---

## 14. Implementation priorities

The order in which V1.0 components must be built. The first item is the critical path; nothing else is useful without it.

1. **Producing-skill contract refactor.** The four intelligence skills emit the V1.0 `claims[]` block (§11). Until this lands, the auditor can only run in degraded mode.
2. **Audit engine + buyer-dossier profile.** The first asset profile, against the anchor case.
3. **Pilot gate run.** Audit Defence Digital. Audit at least one structurally different sibling (incumbency analysis recommended). Re-evaluate the parameterised approach. Proceed only if it generalises cleanly.
4. **Three more asset profiles.** Supplier, sector, incumbency.
5. **MCP tools — V1.0 prototype four.** `audit_asset`, `get_audit_for_asset`, `get_pursuit_audit_summary`, `list_audits_overdue`.
6. **Storage layer.** Co-located audit files plus central audit log.
7. **Producer-emit hook in each producing skill.** Each calls `audit_asset` on emit.
8. **Weekly re-audit sweep job.**
9. **V1.0-complete additions.** `list_red_audits`, `get_audit_history`. Required before V1.0 is signed off as complete.
10. **V1.1 follow-on.** Upstream volatility tag; reference-layer profile; procurement profile; stakeholder profile; newsroom profile.
11. **Parked.** Orchestrator phase 7 capability (provenance / traceability / flag-handling on Agent 3 manifest), returning to design when Agent 3 maturity develops.
12. **V2.** Synthesis-output audit (win strategy itself, go/no-go recommendation, gate-pack narrative).

---

## 15. Out of scope (recap)

Stated explicitly so a reader knows what this spec does not cover.

- Synthesis-output audit (win strategy / Qualify / gate-pack narrative). V2.
- Orchestrator phase 7 calls. Parked until Agent 3 maturity develops.
- Reference-layer, procurement, stakeholder, and newsroom asset profiles. V1.1.
- Pursuit-level weighted-by-stakes rollup. V2.
- Auto-resolution of contradictions between sources.
- Auditor authority to block, retry, or quarantine. The auditor advises; consumers act.
- Upstream volatility tagging on individual claims. V1.1.
- The four intelligence skills' claims-block refactor itself — that is its own action, scoped from this spec but planned and tracked separately.

---

## 16. Open detail work for the implementation plan

Concrete and important but refinements on the architectural spine, not architectural choices. Settled in the writing-plans phase.

- **Audit profile JSON schema.** The exact shape of an asset profile — required sections, volatility classes, decision-safety mappings, source-tier expectations.
- **Per-dimension 0–10 rubric specifics.** Placeholder thresholds in V1.0; tightened during pilot. The plan writes the placeholder; the pilot tightens it.
- **Central audit log storage choice.** SQLite table on the platform server, JSONL append-only file, or both? Choice is a local trade-off, not architectural.
- **Sweep job scheduling and execution.** Cron or platform scheduler? Where the job code lives.
- **Slash command surface.** What does the consultant type to pull an audit? `/audit <asset>`? Other?
- **Audit ID format and traceability conventions.** Stable IDs that survive re-audits and degraded-mode runs.
- **Orchestrator integration test.** How phase 3 wiring is verified end-to-end against the orchestrator spec.

---

## 17. Acceptance criteria for this spec

The spec is correct if a senior reader can answer all of:

- What is the auditor's persona and exam question, and what is the boundary of its authority?
- What asset types does V1.0 audit, and what is deferred to V1.1, parked, or V2?
- What is the architectural shape — single skill, family of skills, or generic engine? What is the pilot gate that validates it?
- When does the auditor run? Where does it write? How is a pursuit-level view built?
- What MCP tools does V1.0 ship, and which two more must be added before V1.0 is complete?
- What are the six audit domains and the verdict rubric?
- What contract must the producing intelligence skills satisfy for the auditor to work? What happens to legacy dossiers?
- Why does the Defence Digital "Charlie Forte" case come out Red under the V1.0 auditor?

---

## 18. Sequencing and dependencies

This spec is design only. The implementation plan that follows turns it into ordered work. The work cannot start before:

- The user reviews and approves this spec.
- The wiki decision record at `wiki/decisions/forensic-intelligence-auditor-agent.md` is updated to reflect the design choices made here that go beyond it (notably: contradiction-resolution stance, the parameterised engine + pilot gate, the closed action-type enum, the V1.0 prototype tool surface, the V1.0 backlog tools, and the V1.0/V1.1/V2 scope split).
- A concrete implementation plan is produced from this spec via the writing-plans skill.

The producing-skill `claims[]` contract refactor (§11.4) is the first build-step the implementation plan covers, and is also the first dependency on the four intelligence skills outside this agent.
