# Pursuit Viability (Qualify v0.2) — Positioning Brief

**Status:** Draft for sign-off. Once accepted, this document is the canonical product spec for Qualify v0.2 and supersedes the relevant sections of [pwin-qualify/docs/PWIN-Qualify-Design v1.html](PWIN-Qualify-Design%20v1.html). Companion documents:

- [PWIN_Qualify_v02_PreservationInventory.md](PWIN_Qualify_v02_PreservationInventory.md) — what carries forward, what changes (signed off 2026-04-15: relationship-heavy v0.1 questions Q13–Q16 RETIRED; orphan Excel content DEFERRED)
- The v6 source spec (`pursuit_winnability_product_spec_v6` / `pursuit_winnability_platform_schema_v1`) drafted in ChatGPT — supplies new questions, hurdles, challenge prompts, actions

**Author of underlying decisions:** user (bid-manager / domain expert), 2026-04-15.

---

## 1. Name and one-line purpose

**Product name:** Pursuit Viability (working subtitle: *the Qualify product*)

**One-line purpose:** A coaching tool that assesses how viable a pursuit is at the current stage, advises the team on what to do to improve viability, or recommends pulling out when viability is too low to justify continued investment.

**Explicitly NOT:** a probability of winning, a PWIN score, an autonomous decision-maker, a strategy generator, or a replacement for governance gate decisions.

---

## 2. What Pursuit Viability is for, and where it sits

### Used in two contexts (per user, 2026-04-15)

1. **Consulting capture support.** Brought in early during a consulting assignment to help the bid team build a viable pursuit, coach them through the gaps, and recommend stop/continue points.
2. **Late-entry diagnostic.** Brought in on a deal already in flight to give an honest read on viability and what's needed to recover (or whether to qualify out).

### Position in the PWIN product family

```
                                      Pursuit Viability
                                      (coaches the team
                                       on viability —
                                       supports go/no-go)
                                            ▲
                                            │ reads
                                            │
   Intel pipeline → Win Strategy → Bid Execution → Verdict
   (produces       (produces        (executes        (forensic
    artifacts)      artifacts)       the bid)         post-loss)
```

- Pursuit Viability **consumes** evidence that other products produce. It does not own pursuit artifacts (Stakeholder Map, Win Themes, Competitor Field Map, Solution Spine, Capture Plan etc. — those belong to Win Strategy and the intel/competitor profiling skills).
- Pursuit Viability **coaches toward** producing those artifacts when they're missing — it tells the team what evidence would lift their viability assessment, but it does not generate the evidence itself.
- Pursuit Viability **supports** the formal go/no-go decision; it does not replace it. The output is a coached recommendation, not a verdict.

---

## 3. Headline output

The user-facing output of every Pursuit Viability assessment has three components, in this order:

### 3.1 Viability tier (5-band named RAG)

| Tier | Meaning |
|---|---|
| **Strong** | Viability is high for the current stage. Position is earned and evidenced. Continue and consolidate. |
| **On Track** | Viability is appropriate for the current stage. Some gaps but nothing structural. Continue with focused improvements. |
| **Conditional** | Viability is at the lower edge of acceptable for the current stage. Specific conditions must be met before further investment is justified. |
| **Major Concerns** | Viability is below what the stage requires. Material reshaping is required, or the pursuit should move to watch/shape rather than active pursuit. |
| **Walk Away** | Viability is structurally weak. Continued investment is not justified. Recommend qualifying out or returning to early-stage shaping only if the underlying conditions change. |

The tier is the **headline**. It is the only thing presented at a glance. The underlying score is computed but never shown as a number, percentage, or band-chart.

### 3.2 Viability narrative

A short Alex Mercer narrative (3–5 paragraphs) explaining:
- Why this tier was assigned at this stage
- The two or three things that most determined the tier
- The single biggest risk to the assessment if the team disagrees with it
- The strongest argument *against* the assigned tier (forces honesty)

### 3.3 Conditions and actions

- **If Conditional or Major Concerns:** the specific conditions that would lift the tier, with named role owners and a time horizon.
- **If Walk Away:** the underlying reasons, and what would have to change in the world (not just in the team's effort) to re-open viability.
- **If On Track or Strong:** the two or three actions that would harden the position from On Track → Strong, or keep Strong from drifting.

Per-question outputs (Validated / Queried / Challenged + suggested score + challenge questions + capture actions + inflation detection) remain available as drill-down — that mechanism is preserved from v0.1. The score number stays internal.

---

## 4. The 4-stage model

v6 proposed six stages; v0.1 had six phase bands and six stage targets. Both are too granular and `capture_phase`/`active_capture` blur. v0.2 collapses to four:

| Stage | Procurement reality | What viability is mostly about at this stage |
|---|---|---|
| **Identify** | Opportunity scanned. Pre-market or earliest market-engagement signals. No formal commitment. | Strategic fit, contestability, "is this worth pursuing at all?" |
| **Capture** | Active capture. Buyer engagement underway. Pre-ITT. | Buyer understanding, stakeholder access, competitive position, proposition shape |
| **Pursue** | ITT/RFP live. Formal pursuit in progress. | Evidence depth, scoreability, delivery confidence, commercial viability |
| **Submit** | Submitted / shortlist / BAFO / preferred bidder | Submission strength, competitive defensibility, late-stage risk |

**Stage matters because expected maturity matters.** A thin evidence base at Identify is normal; the same gap at Submit is a Walk Away. Same answers, different RAG tier, because the bar moves with the stage.

(Late post-award activity belongs in Bid Execution, not Qualify. v0.1's "Preferred Bidder" stage is intentionally absorbed into Submit and not extended further.)

---

## 5. Stage-calibrated RAG (the calibration table)

The same internal score produces different RAG tiers depending on stage. The calibration table — directional, to be tuned via the eval harness — is the bridge:

| Internal score band | Identify | Capture | Pursue | Submit |
|---|---|---|---|---|
| Top band | Strong | Strong | Strong | Strong |
| Upper-middle | Strong | On Track | On Track | On Track |
| Middle | On Track | On Track | Conditional | Conditional |
| Lower-middle | Conditional | Conditional | Major Concerns | Major Concerns |
| Bottom | Major Concerns | Major Concerns | Walk Away | Walk Away |

Two anchor effects:
- **Same score, later stage → lower tier.** A position that's appropriate at Capture becomes inadequate at Pursue.
- **Strong is hard to achieve at Identify** by design. Most Identify-stage pursuits should land at On Track or Conditional; Strong at this stage requires structural advantage that genuinely doesn't need further validation.

Critical-question caps still apply (per §7): if a flagged-critical question lands at Strongly Disagree, the headline tier cannot exceed Major Concerns regardless of overall score. Multiple critical fails → Walk Away. This is how the engine prevents an inflated total from masking a structural weakness.

---

## 6. Question model

### 6.1 Categories — replace v0.1's 6 with v6's 5

v0.1 categories (Competitive Positioning / Procurement Intelligence / **Stakeholder Strength / Organisational Influence** / Value Proposition / Pursuit Progress) over-weighted relationships and influence. v0.2 adopts v6's 5-category model:

| Category | Default weight |
|---|---|
| Buyer Need & Decision Logic | 25% |
| Stakeholder Position & Access | 20% |
| Competitive Position & Incumbent Dynamics | 20% |
| Procurement, Proposition & Solution Fit | 20% |
| Commercial, Delivery & Pursuit Readiness | 15% |

Stakeholder Position & Access stays as a category because access-quality is real signal — but it's bounded at 20% rather than the ~40% combined weight relationship/influence carried in v0.1. This is the structural fix to the user's stated unhappiness.

### 6.2 Archetype-adjusted weights — preserve the v0.1 mechanism, refresh the values

v0.1 already supports per-archetype weight rebalancing via `weightProfiles` + `oppTypeProfile`. v0.2 replaces the four profiles (default/services/technology/advisory) with v6's eight archetype-specific weight sets (Consulting / Digital Transformation-SI / Digital Product-SaaS / BPO-Managed Service / Facilities-Operational / Hybrid / Framework-Panel / Incumbent Renewal). The mechanism is unchanged; the values change.

The "weights are stable" guidance in `feedback_qualify_finetune_scope` is **deliberately broken once** for v0.2 because the categories themselves change. After v0.2 ships, the weights re-stabilise.

### 6.3 25 core questions

The v6 core 25 (Q01–Q25) replace the v0.1 standard 24. The full per-question disposition table is in [PreservationInventory §3](PWIN_Qualify_v02_PreservationInventory.md). Headline:

- **20 v0.1 questions REPLACE** to v6 questions (mapping per v6 `original_vs_new_mapping`)
- **4 v0.1 questions RETIRE** (Q13 Network of Influence, Q14 Personal Agendas, Q15 Power Dynamics, Q16 Political Coaching) — folded into v6 stakeholder/decision-architecture questions, not given dedicated weight. Confirmed 2026-04-15.
- **Each v0.2 question retains v0.1's per-question structure**: 4-band rubric, `inflationSignals` array, within-category weight (`qw`)
- **v0.2 questions also gain** v6's hurdles, benchmark examples, tiered challenge questions, and tiered actions — these enrich the rubric, not replace it

### 6.4 Critical questions

A subset of questions are flagged `critical: true` (per v6). Critical questions trigger the cap behaviour described in §5: weak performance on a critical question caps the headline RAG tier.

Critical in v6 core 25: Q01, Q06, Q09, Q13, Q16, Q17, Q19, Q21, Q22.

### 6.5 Per-question content carry-forward

For every v0.2 question, the v0.1 element that has no clean v6 equivalent is **the inflation-signals phrase list**. v6 does not provide these. Each v0.2 question must inherit an inflation-signals list — either ported from the v0.1 question it most closely replaces, or newly authored where no equivalent exists. **No v0.2 question ships without inflation signals.** This is non-negotiable; inflation detection is core to Alex's value.

---

## 7. Overlay model — incumbent and challenger

v0.1 has an incumbent (rebid) modifier. v0.2 keeps the modifier mechanism (the architectural pattern is correct) and uses it to host two overlays:

- **Incumbent overlay** — replaces the v0.1 12-question rebid module with v6's 8 incumbent overlay questions (I01–I08), but the v0.1 `whyItMatters` paragraphs, `inflationTriggers` (RI-1..RI-4), `calibrationRules` (RC-1..RC-4), and `autoVerdictRules` (RA-1..RA-3) are CARRIED — they're sharper than v6's equivalents.
- **Challenger overlay** — net new in v0.2. v6's 8 challenger overlay questions (C01–C08). No v0.1 equivalent to merge from.
- **Open-field** — no overlay (default state).

### Rebid Risk Assessment output is preserved

The 9-field `rebidRiskAssessment` output (decayRiskProfile, challengerExploitAssessment, retenderingMotivationAssessment, blindSpots, incumbentStrategyRecommendation with 4 postures, specificRemediationActions, performanceNarrativeGaps, switchingCostQuantification) is **carried forward verbatim** for incumbent overlays. Most of these fields have no v6 equivalent and are uniquely valuable.

A symmetric **Challenger Position Assessment** output is added for challenger overlays — same idea, mirror fields (e.g. `displacementCaseStrength`, `incumbentCounterReadiness`, `switchingRiskNeutralisation`). Field design is a v0.2 build task.

The five rebid design principles, particularly *"the rebid question is not 'will we win?' — it is 'what do our competitors know that we don't?'"*, carry verbatim into v0.2 because they encode the philosophy. The principle generalises naturally to challenger context.

---

## 8. Alex Mercer persona — full carry-forward, with enrichment

Alex is the heart of the product. **Default disposition for every persona sub-element is CARRY VERBATIM.** See [PreservationInventory §5](PWIN_Qualify_v02_PreservationInventory.md) for the element-by-element register; everything in there carries.

What changes:
- **Calibration rules** are extended — v0.1's four rules are based on v0.1's 6-category model; the rules are re-cast in v0.2 terms but every rule's *intent* is preserved, plus new rules are added for the 4-stage model and the challenger overlay.
- **Challenge generation** is enriched — Alex now has v6's tiered challenge prompts (one set per response level per question) as a structured library to draw from, sharpening per-question challenge specificity.
- **Action generation** is enriched — same as challenge generation, with v6's tiered action templates.
- **Verdict vocabulary** stays Validated / Queried / Challenged at the per-question level (Alex's vocabulary). The new RAG tiers (Strong / On Track / Conditional / Major Concerns / Walk Away) are the *pursuit-level* output, not Alex's per-question output.
- **What Alex cannot do in v0.2** that he could in v0.1: surface a PWIN number. The synthesised pursuit-level verdict is now a tier + narrative. Per-question suggestedScore stays as a drill-down value, never as the headline.

The `roleStatement`, `coreBeliefs`, `characterTraits`, `toneGuidance`, `languagePatterns`, `hardRules`, `successCriteria` all CARRY VERBATIM. v6 does not get to reshape Alex; Alex absorbs v6's depth.

---

## 9. Opportunity-type calibration — carry forward, expand for new archetypes

The 7 v0.1 calibration paragraphs CARRY VERBATIM. v6 introduces 8 archetypes; net new ones (Facilities/Field Operational, Hybrid Transformation+Managed Service, Framework/Panel, Incumbent Renewal — the last is implicitly the incumbent overlay rather than an archetype) need new calibration paragraphs authored in the same voice and depth. Also: v0.1's "Digital Outcomes" and "Infrastructure & Hardware" calibrations have no clean v6 equivalent — they CARRY as v0.2-only enrichments.

---

## 10. Scoring engine (internal)

Internal scoring stays simple. Two factors per question, multiplied:

```
question_internal_score = response_value × evidence_quality_multiplier
```

Then summed within category, weighted by category weight, weighted by archetype profile, capped by critical-question rules, and mapped through the §5 calibration table to produce the headline RAG tier.

**What v0.2 does not adopt from v6:**
- 5-multiplier scoring (artifact_sufficiency × evidence_quality × freshness × judgment_quality × response) — too complex, replaced by 2-factor
- Maturity-vs-winnability dual scoring — surfaced as part of the narrative, not as two separate numbers
- Universal score / archetype-adjusted score / maturity score triple — only one internal number is computed; it never surfaces

The internal score, the per-question Alex outputs, and the underlying answers are all available for export and audit (consultant use cases need this). They are simply not the headline.

---

## 11. Two apps, one brain — divergence rules

v0.2 preserves the existing two-app model unchanged in shape:

- **Consulting standalone** ([PWIN_Architect_v1.html](PWIN_Architect_v1.html)) — full intelligence stack, intel injection on, rubric panel visible, all overlays available. Canon.
- **Website MVP** ([bidequity-co/qualify-app.html](../../bidequity-co/qualify-app.html)) — deliberately under-enriched lead-gen; intel injection off, rubric panel hidden, overlays off (or limited). Stripped variant. Per `feedback_qualify_lead_gen_scope` and `feedback_qualify_rubric_visibility`. **v0.2 also moves this app server-side** (rubrics, persona, calibration, RAG matrix, overlay output schemas held in the Cloudflare Worker, browser becomes thin display layer) — per `project_qualify_serverside_migration` (un-deferred 2026-04-15) because v0.2 creates the IP that's worth protecting.

The brand-colour drift is the only intentional drift. Per-client onboarding forks (per `project_qualify_multiclient_onboarding`) continue to work as today — the build script is unchanged.

---

## 12. Build, eval, publish — operational continuity

The `build-content.js` sentinel-injection mechanism, the `--check` idempotency mode, and the eval harness all CARRY. What changes:

- The content schema version bumps from v0.1 to v0.2 (new file: `qualify-content-v0.2.json`)
- All v0.1 eval fixtures are **invalidated** by the question changes; fixtures must be re-authored against v0.2 questions before the eval harness is meaningful for v0.2
- The build emits an additional artifact: a **calibration table fixture** that the eval harness can use to verify stage→tier mapping behaviour at boundary points

---

## 13. Out of scope for v0.2 (so this brief doesn't scope-creep itself)

- v6's 23-artifact library as a Qualify input (per locked decision: Qualify does not own artifacts)
- v6's 6-agent architecture (Alex stays the single coaching agent; ingestion/research/strategy are other PWIN products)
- v6's 13-scenario benchmark library (currently unmapped in source; defer)
- A second numeric maturity score output
- The orphan content in `PWIN_AI_Enrichment_Review.xlsx` and `BWIN Qualify_AI Design_Proforma_v2.xlsx` (DEFER per user 2026-04-15; revisit at v0.3)
- Any artifact ownership that overlaps Win Strategy or the intel/competitor profiling skills

---

## 14. Open questions to resolve before content delta begins

These are the only things still genuinely open. Defaults are proposed; user decision needed.

1. **Are the 5 RAG tier names final** — *Strong / On Track / Conditional / Major Concerns / Walk Away* — or do you want to test alternatives? (Default: yes, ship with these.)
2. **Are the 4 stage labels final** — *Identify / Capture / Pursue / Submit* — or want a different labelling? (Default: yes, ship with these.)
3. **Critical-question list** — v6 flags 9 of 25 as critical. Want to review the list before content delta, or take v6's choices as a starting position and tune via eval? (Default: take v6's choices, tune via eval.)
4. **Challenger overlay output schema** — v0.2 needs a `challengerPositionAssessment` symmetric to the existing `rebidRiskAssessment`. Author it now as part of v0.2, or ship v0.2 with incumbent overlay only and add challenger overlay output in v0.2.1? (Default: include in v0.2 since the questions are already in scope; output design is a 1–2 day task.)
5. **Per-stage critical-question caps** — should some critical-question caps relax at Identify stage? E.g. a Strongly Disagree on a Procurement-Scoreability question is structurally fatal at Submit but probably appropriate at Identify. (Default: yes, model this in the cap rules; design as part of content delta.)

---

## 15. What happens after sign-off on this brief

1. **Content delta plan** — a row-by-row diff from `qualify-content-v0.1.json` to `qualify-content-v0.2.json` based on this brief and the preservation inventory. Output: a delta document and a target JSON skeleton.
2. **Authoring sprint** — the new question rubrics, hurdles, inflation signals (carry/port/new), challenge prompts, action templates, calibration rules, calibration table, and challenger overlay output schema. The biggest single piece of work.
3. **Eval re-baseline** — author a starter set of fixtures against v0.2; run the harness; tune the calibration table and critical-question caps until tier outputs land where the user expects.
4. **App wiring** — minor changes to both HTML apps to (a) suppress the PWIN number and category radar, (b) render the RAG tier + narrative + conditions as the headline, (c) extend the modifier system for the challenger overlay, (d) extend the stage selector to the 4-stage model.
5. **Brand/positioning copy** — landing pages, in-app strings, the term "PWIN" replaced with "Pursuit Viability" wherever it appears.

Realistic timeline (rough): content delta + authoring 2–3 weeks; eval re-baseline 1 week; app wiring 1 week; copy refresh 2–3 days. Total ≈ 4–6 weeks of focused work.

---

**Sign-off needed:** Read end-to-end. Flag anything that doesn't match your intent. Once accepted, this brief is the spec and the delta plan is the next deliverable.
