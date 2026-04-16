# Pursuit Viability (Qualify v0.2) — Preservation Inventory

**Status:** Pre-brief artifact. The purpose of this document is to enumerate everything in the current Qualify product (v0.1) and the planned tuning surface, so that the v0.2 brief and content delta cannot silently drop anything. Every element below must be explicitly accounted for in the v0.2 brief as one of:

- **CARRY** — keep unchanged in v0.2
- **ENRICH** — keep, with v6 spec material added (additive — original meaning preserved)
- **REPLACE** — current element supersedes by v6 element, with rationale
- **DEFER** — out of scope for v0.2, parked for later
- **RETIRE** — explicitly removed, with rationale

If an element appears in this inventory and is *not* assigned a disposition in the brief, that is a bug in the brief.

**Source files inventoried:**
- [pwin-qualify/content/qualify-content-v0.1.json](../content/qualify-content-v0.1.json) — the live scoring brain
- [pwin-qualify/docs/PWIN_Architect_v1.html](PWIN_Architect_v1.html) — consulting standalone canon
- [bidequity-co/qualify-app.html](../../bidequity-co/qualify-app.html) — website MVP
- [pwin-qualify/content/README.md](../content/README.md) — operating model
- [pwin-qualify/docs/PWIN_Rebid_Module_Review.xlsx](PWIN_Rebid_Module_Review.xlsx) — rebid design pack
- Memory: `feedback_qualify_finetune_scope`, `feedback_qualify_lead_gen_scope`, `feedback_qualify_rubric_visibility`, `project_qualify_two_versions`, `project_qualify_orphan_logic`, `project_qualify_finetune_intent`, `project_qualify_multiclient_onboarding`, `project_qualify_v02_repositioning`

---

## 1. Scoring engine (currently surfaced; v0.2 keeps but hides number)

| Element | Detail | v0.2 implication |
|---|---|---|
| 4-point scale `scorePts` | Strongly Agree=4, Agree=3, Disagree=2, Strongly Disagree=1 | Engine retained; surfaced as RAG |
| `pwinFormula` | `sum across categories of (catScore / maxCat) * cat.weight; catScore = sum of (scorePts[answer] * question.qw)` | Engine retained internally |
| `phases` (6 bands) | Pre-Capture / Capture Commenced / Active Capture / Pre-ITT / ITT Ready / Strong Position with thresholds 0/.15/.35/.55/.7/.85 | Becomes basis for stage-calibrated RAG thresholds — **do not silently drop these calibration points** |
| `stageTargets` (6 stages) | Pre-market / Market engagement / ITT not yet published / ITT published / Shortlisted-BAFO / Preferred Bidder, with minimum %s | Direct input into the 4-stage model + RAG calibration table |

## 2. Categories and weights

| Element | Detail | v0.2 implication |
|---|---|---|
| 6 categories `cp/pi/ss/oi/vp/pp` | Competitive Positioning, Procurement Intelligence, Stakeholder Strength, Organisational Influence, Value Proposition, Pursuit Progress | Replaced by v6 5-category model — must call this out as a deliberate REPLACE with the rebalancing rationale (relationship-heavy categories collapsed) |
| `weightProfiles` | default / services / technology / advisory variant weights | Replaced by v6 archetype-adjusted weights — but the *concept* of opp-type weight rebalancing is preserved |
| `oppTypeProfile` | Maps 7 opp-type strings to weight profile ids | Replaced by v6 8-archetype list, but mapping concept preserved; need explicit decision on retiring the current opp-type strings or aliasing them |

## 3. The 24 standard questions (the substantive change area)

Every question carries: `id`, `cat`, `topic`, `text`, `rubric` (4 bands), `inflationSignals` array, `qw` (within-category weight). Per-question dispositions per the v6 `original_vs_new_mapping` (which I'll table in the brief):

| Q# | Topic | v0.1 category | Likely v0.2 disposition |
|---|---|---|---|
| Q1 | Strategy Foundation | cp | REPLACE → v6 Q13/Q15/Q16/Q20 |
| Q2 | Competitive Intelligence | cp | REPLACE → v6 Q11/Q13/Q15/Q21 |
| Q3 | Winning Proposition | cp | REPLACE → v6 Q18/Q19/Q20/Q10 |
| Q4 | Countertactics | cp | REPLACE → v6 Q15/Q14/Q12 |
| Q5 | Clarity of Approval Steps | pi | REPLACE → v6 Q06/Q04/Q25 |
| Q6 | Decision Criteria & Drivers | pi | REPLACE → v6 Q03/Q16/Q18/Q20 |
| Q7 | Decision Timeline | pi | REPLACE → v6 Q05/Q24 (downgrade — timeline ≠ winnability) |
| Q8 | Final Veto Rights | pi | REPLACE → v6 Q06/Q25 |
| Q9 | Internal Champion | ss | REPLACE → v6 Q07/Q09/Q10 |
| Q10 | Competitor Relationships | ss | REPLACE → v6 Q12/Q15 |
| Q11 | Evaluator Coverage | ss | REPLACE → v6 Q07/Q09/Q19 |
| Q12 | Decision Authority Relationships | ss | REPLACE → v6 Q07/Q09/Q13 |
| Q13 | Network of Influence | oi | RETIRE (folded into v6 Q06/Q07) — flag explicitly |
| Q14 | Personal Agendas | oi | RETIRE/REDUCE (folded into v6 Q07/Q08) — relationship-heavy, deliberate |
| Q15 | Power Dynamics | oi | RETIRE/REDUCE (folded into v6 Q06/Q08) — relationship-heavy, deliberate |
| Q16 | Political Coaching | oi | RETIRE/REDUCE (folded into v6 Q07/Q08/Q10) — relationship-heavy, deliberate |
| Q17 | Co-Developed VP | vp | REPLACE → v6 Q18/Q03 |
| Q18 | Client Value Justification | vp | REPLACE → v6 Q18/Q21 |
| Q19 | Differentiated | vp | REPLACE → v6 Q20/Q13 |
| Q20 | Validated Alignment | vp | REPLACE → v6 Q18/Q19/Q09 |
| Q21 | Client Engagement | pp | REPLACE → v6 Q10/Q25 |
| Q22 | Communication Transparency | pp | REPLACE → v6 Q10/Q25 |
| Q23 | Message Adoption | pp | REPLACE → v6 Q10/Q18/Q20 |
| Q24 | Future Focus | pp | REPLACE → v6 Q10/Q25 (weakened) |

**Per-question elements that MUST carry forward into the new questions** (regardless of which v6 question replaces which v0.1 question):
- Rubric structure: 4 named bands (Strongly Agree → Strongly Disagree), one paragraph each. Tuning surface per `feedback_qualify_finetune_scope`. **CARRY mechanism, REPLACE content.**
- `inflationSignals` arrays (per-question phrase lists). The v6 spec does not provide these — they must be **CARRIED** by porting onto the new questions (and added to where v6 questions have no equivalent in v0.1).
- `qw` (within-category weight) — concept retained even if values change.

## 4. Rebid / incumbent modifier layer

The whole modifier mechanism is in scope for v0.2 because it's the proof case for context overlays. v6 introduces explicit **challenger** and **incumbent** overlays that supersede the current 12-question rebid module — this is an upgrade, but specific elements must be preserved:

| Element | Source | v0.2 implication |
|---|---|---|
| Modifier mechanism (`applyContentModifiers()` pattern, base-rebuild-then-reapply) | runtime | CARRY — the architectural pattern is correct and reused for stage and overlay |
| Trigger field `context.incumbent` + match strings | content JSON | CARRY (will need a `context.role` field for challenger/open_field too) |
| 5 design principles | content JSON | CARRY — these are the *philosophy*, must survive verbatim into v0.2 brief, particularly: "the rebid question is not 'will we win?' — it is 'what do our competitors know that we don't?'" |
| 5 architecture descriptions | content JSON | ENRICH — re-cast for v0.2 (RAG output, no PWIN number) but retain the principles |
| 12 R-questions (R1–R12) | content JSON | REPLACE → v6 8 incumbent overlay questions (I01–I08), but the *whyItMatters* paragraphs from v0.1 are richer than v6's hurdles — CARRY those into the new overlay questions |
| 4 sub-categories (Contract Performance Reality / Position Decay / Retendering Intelligence / Challenger Threat) | content JSON | CARRY as conceptual grouping inside the v6 incumbent overlay |
| 4 inflation triggers (RI-1..RI-4) | content JSON | CARRY — these are uniquely strong, v6 has no equivalent specificity for incumbent inflation |
| 4 calibration rules (RC-1..RC-4) | content JSON | CARRY — auto-downgrade rules (e.g. Strongly Agree on Relationship Currency where last contact >90 days → Queried) |
| 3 auto-verdict rules (RA-1..RA-3) | content JSON | CARRY — auto-CHALLENGED rules |
| `rebidRiskAssessment` output schema (9 fields) | content JSON | CARRY — fields incl. decayRiskProfile (already RAG!), challengerExploitAssessment, retenderingMotivationAssessment, blindSpots, incumbentStrategyRecommendation (4 postures), specificRemediationActions, performanceNarrativeGaps, switchingCostQuantification — most of these have no v6 equivalent and are uniquely valuable |
| 3 few-shot examples (CHALLENGED, QUERIED, VALIDATED) | content JSON | CARRY — gold-standard Alex outputs for the rebid context |
| New: challenger overlay (v6 C01–C08) | v6 spec | ADD — currently absent from v0.1; explicit ADD |

## 5. Alex Mercer persona — full object

The persona is the heart of the product. Every sub-element must be addressed in the brief. Default disposition is **CARRY**; v6 enriches Alex's challenge/coaching depth, never replaces him.

| Element | Detail | v0.2 disposition |
|---|---|---|
| `meta` | version, lastUpdated, owner | CARRY (bump version) |
| `identity.name` | Alex Mercer | CARRY |
| `identity.title` | Senior Bid Director & Pursuit Assurance Lead | CARRY |
| `identity.roleStatement` | "You conduct independent gate reviews… you hold the mirror… last line of defence between optimism and commercial consequences" | CARRY VERBATIM |
| `background.narrative` | 17 years, MoJ start, NHS evaluator side, three £100m+ losses observed | CARRY VERBATIM |
| `coreBeliefs` (6 statements) | Most bids lost before ITT; gap between belief and truth = largest commercial risk; relationship without documented commitment = goodwill; PI most under-invested; 6mo evidence = history; internal consensus ≠ external validation | CARRY VERBATIM |
| `characterTraits` (5) | Question behind question; pattern recognition; calibrate to context; always make a call; protective not adversarial | CARRY VERBATIM |
| `toneGuidance` (5) | Declarative; no hedging on Challenged; pattern language permitted; acknowledge strength plainly; coaching register for actions | CARRY VERBATIM |
| `languagePatterns.use` (7 phrases) | "The evidence tells me…", "Named individual. Named commitment. Named date.", etc. | CARRY VERBATIM |
| `languagePatterns.avoid` (10 phrases) | "Great evidence", "Well done", "Best practice suggests", "Perhaps", etc. | CARRY VERBATIM |
| `hardRules.will` (4) | Always deliver verdict; name inflation signal; suggest named role owner; ask answerable questions | CARRY VERBATIM |
| `hardRules.willNot` (4) | Validate to protect morale; ask generic questions; congratulate for minimum standard; hedge Challenged into Queried | CARRY VERBATIM |
| `workflowTriggers.autoChallenge` (3 rules) | Internal-only assertions; future-tense intent; unnamed contacts → auto-CHALLENGED | CARRY VERBATIM (still apply with v6 questions) |
| `workflowTriggers.autoQuery` (1 rule) | Named individual but no documented commitment → downgrade Strongly Agree to Queried | CARRY VERBATIM |
| `workflowTriggers.calibrationRules` (4 rules) | TCV >£50m + Strongly Agree on Stakeholder; Pre-market + Strongly Agree on PI; Challenger position + Strongly Agree on Authority/Champion; Incumbent position + Strongly Disagree on Competitive Positioning | ENRICH — port to new question IDs; v6 stage model expands to 4 stages so calibration triggers extend |
| `workflowTriggers.inflationTriggers` (3 rules) | Soft-language phrases; comparative superiority without named competitor; Strongly Agree with <50 words | CARRY VERBATIM |
| `successCriteria.verdictQuality` (4 checks) | Unambiguous; downgrade reason stated; opportunity context referenced; inflation phrase quoted verbatim | CARRY VERBATIM |
| `successCriteria.challengeQuality` (3 checks) | Specificity, answerability, non-duplication | CARRY VERBATIM |
| `successCriteria.actionQuality` (3 checks) | Executable; named role owner; at least one client-facing | CARRY VERBATIM |
| `successCriteria.finalCheck` (3 checks) | Team would know what to do; no avoid-list phrases; verdict consistent with triggers | CARRY VERBATIM |

**Persona enrichment from v6** (additive, not replacement):
- v6's per-question challenge questions (4 tiers per question) → ENRICH Alex's challenge generation with structured tiered prompts
- v6's per-question recommended actions (4 tiers) → ENRICH Alex's action generation
- v6's score-cap reasons → ENRICH Alex's downgrade vocabulary
- v6's "what counts as executed thinking" criteria → ENRICH `successCriteria.verdictQuality`

## 6. Opportunity-type calibration paragraphs (7)

These are the 7 paragraphs in `opportunityTypeCalibration`. Each is injected into Alex's prompt when the opp type matches.

| Calibration | v0.2 disposition |
|---|---|
| BPO | CARRY VERBATIM (v6 BPO archetype is broader; this paragraph is sharper) |
| IT Outsourcing | CARRY VERBATIM (v6 collapses into Digital Transformation/SI; this paragraph is sharper) |
| Managed Service | CARRY VERBATIM (folds into v6 BPO/Managed Service archetype; calibration text retained) |
| Digital Outcomes | CARRY VERBATIM (no clean v6 equivalent — must explicitly carry or DEFER) |
| Consulting / Advisory | CARRY VERBATIM (v6 Professional Consulting/Advisory is the same archetype) |
| Infrastructure & Hardware | CARRY VERBATIM (no clean v6 equivalent — must explicitly carry or DEFER) |
| Software / SaaS | CARRY VERBATIM (v6 Digital Product/SaaS/Platform is the same archetype) |

**The v6 spec adds two archetypes** (Facilities/Field/Operational; Hybrid Transformation+Managed Service; Framework/Panel; Incumbent Renewal/Rebid). v0.2 must add calibration paragraphs for any added archetypes, in the same voice and depth as the existing 7.

## 7. Output schema (the AI response contract)

| Element | v0.2 disposition |
|---|---|
| `standardReport` (per-question Validated/Queried/Challenged + suggestedScore + narrative + challenge questions + capture actions + inflation detection) | CARRY mechanism. Per-question outputs unchanged in shape. Top-level summary changes: PWIN number → RAG tier + viability narrative + conditions |
| `rebidRiskAssessment` (9 fields) | CARRY (see §4) |
| New top-level: viability RAG | ADD — 5-band named tier with rationale, conditions, stage-calibrated thresholds |

## 8. Build, eval, publish workflow (operational)

| Element | v0.2 disposition |
|---|---|
| Sentinel-injected build (`build-content.js`) | CARRY — the build mechanism is fit for purpose |
| Two-app divergence rules (intel injection on/off, rubric visibility on/off) | CARRY (per `feedback_qualify_lead_gen_scope`, `feedback_qualify_rubric_visibility`) |
| Eval harness with fixtures | CARRY — but **every fixture needs to be re-validated** against v0.2 questions; v0.1 fixtures will not map 1:1 |
| `--check` mode (idempotency check) | CARRY |
| Brand-colour drift (the only allowed drift between apps) | CARRY |
| Multi-client onboarding via per-client JSON forks (per `project_qualify_multiclient_onboarding`) | CARRY — v0.2 must remain forkable in the same way |
| Tuning surface = rubrics + inflation signals + persona triggers + opp-type calibration (per `feedback_qualify_finetune_scope`) | CARRY — these four areas remain the tuning surface in v0.2 |
| Question weights and category weights remain stable (per same memory) | RECONSIDER — v0.2 changes the weighting model (5 categories, archetype-adjusted). This is a deliberate exception to "weights are stable" and must be flagged explicitly in the brief |

## 9. Orphan / not-yet-incorporated logic

Per `project_qualify_orphan_logic`, two Excel files contain Qualify logic not yet in the JSON:
- [PWIN_AI_Enrichment_Review.xlsx](PWIN_AI_Enrichment_Review.xlsx) — review columns not yet completed
- [BWIN Qualify_AI Design_Proforma_v2.xlsx](BWIN%20Qualify_AI%20Design_Proforma_v2.xlsx) — 51 data points, 20 reasoning rules, confidence model — not yet completed

**Disposition:** DEFER explicitly. v0.2 brief should acknowledge these as known orphan content and flag whether they survive into v0.2 scope or get rolled into a v0.3.

## 10. Decisions already made for v0.2 (anchor list)

These four are LOCKED, per `project_qualify_v02_repositioning`:

1. Rename PWIN → Pursuit Viability
2. Qualify does NOT own pursuit artifacts (references and coaches; never generates)
3. Scoring stays internal — no number in UX
4. Output = 5-band named-tier RAG, stage-and-maturity-calibrated, 4-stage model

## 11. What is explicitly OUT of v0.2 scope

So the brief doesn't accidentally reintroduce them:

- v6's 23-artifact library as a Qualify input
- v6's 5-multiplier scoring (response × artifact_sufficiency × evidence_quality × freshness × judgment_quality) — use a 2-factor (response × evidence quality) with stage-aware caps
- v6's 6-agent architecture (A_INT/A_ART/A_MAT/A_WIN/A_RED/A_COACH) — Alex remains the single coaching agent; ingestion/research/strategy live in other PWIN products
- v6's 13-scenario benchmark library (currently unmapped — `benchmark_scenario_id` is null on every v6 question)
- A second numeric "maturity score" output — surface maturity-vs-viability as part of the RAG narrative if at all
- Any artifact ownership that overlaps Win Strategy or the intel/competitor profiling skills

---

## Sign-off prompt before brief is written

Read this inventory end-to-end. Confirm:

1. Anything missing that you want preserved?
2. Any disposition above (CARRY / ENRICH / REPLACE / DEFER / RETIRE) you disagree with — particularly the RETIRE calls on Q13–Q16 (the relationship-heavy questions)?
3. The orphan content in §9 — DEFER for v0.2 OK, or do you want it inventoried into the v0.2 content delta?

Once signed off, the brief becomes the diff: every row above gets a one-line status in the brief, with rationale where it differs from current.
