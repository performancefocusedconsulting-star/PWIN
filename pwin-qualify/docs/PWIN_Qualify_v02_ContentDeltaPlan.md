# Pursuit Viability (Qualify v0.2) — Content Delta Plan

**Status:** Approved 2026-04-15. Companion to:
- [PWIN_Qualify_v02_PositioningBrief.md](PWIN_Qualify_v02_PositioningBrief.md) — the v0.2 spec
- [PWIN_Qualify_v02_PreservationInventory.md](PWIN_Qualify_v02_PreservationInventory.md) — the carry-forward register

This document is the row-by-row diff from [qualify-content-v0.1.json](../content/qualify-content-v0.1.json) to the target `qualify-content-v0.2.json`. It defines **what changes** in the JSON, **what authoring is required**, and **in what order**. It does NOT contain the new content itself — that's the authoring sprint.

---

## 0. Locked decisions

All five §14 defaults from the positioning brief are accepted (user, 2026-04-15):

1. **RAG tier names final:** Strong / On Track / Conditional / Major Concerns / Walk Away
2. **Stage labels final:** Identify / Capture / Pursue / Submit
3. **Critical-question list:** take v6's 9 choices as starting position; tune via eval
4. **Challenger overlay output schema:** include in v0.2 (symmetric to `rebidRiskAssessment`)
5. **Per-stage critical-question caps:** model relaxation at Identify stage; design as part of content delta

---

## 1. Target v0.2 JSON top-level structure

```
qualify-content-v0.2.json
├── $schema                          (bump to qualify-content-schema-v2)
├── version                          ("0.2.0")
├── lastUpdated
├── changelog                        (append v0.2.0 entry)
├── stages                           [NEW] — 4-stage model
├── ragTiers                         [NEW] — 5 named tiers
├── ragCalibration                   [NEW] — stage × score-band → tier table
├── scoring                          [RESTRUCTURE] — 2-factor model
├── categories                       [REPLACE] — 5 v6 categories
├── weightProfiles                   [REPLACE] — 8 v6 archetype profiles
├── archetypeProfile                 [REPLACE → renamed from oppTypeProfile]
├── questionPacks
│   └── core                         [REPLACE] — renamed from "standard"; 25 v6 questions
├── modifiers
│   ├── incumbent                    [RESTRUCTURE] — 8 v6 questions; carry inflation/calibration/auto-verdict/rebidRiskAssessment
│   └── challenger                   [NEW] — 8 v6 questions; new challengerPositionAssessment output
├── persona                          [CARRY VERBATIM with enrichments registry]
├── opportunityTypeCalibration       [CARRY 7 + add 4 new archetype paragraphs]
├── outputs
│   ├── viabilityAssessment          [NEW] — top-level RAG output
│   ├── perQuestionAssurance         [CARRY → renamed from standardReport; mechanism unchanged]
│   ├── rebidRiskAssessment          [CARRY VERBATIM — incumbent overlay only]
│   └── challengerPositionAssessment [NEW] — challenger overlay only
└── sources                          [UPDATE] — references to v6 source spec + carry v0.1 sources
```

---

## 2. Per-section delta

### 2.1 `stages` [NEW]

```
stages: [
  { id: "identify", label: "Identify", expectedMaturity: "low",   description: ... },
  { id: "capture",  label: "Capture",  expectedMaturity: "med",   description: ... },
  { id: "pursue",   label: "Pursue",   expectedMaturity: "high",  description: ... },
  { id: "submit",   label: "Submit",   expectedMaturity: "very-high", description: ... }
]
```

**Authoring task A1:** Write the 4 stage descriptions (one paragraph each) using the brief §4 table as starting point.

### 2.2 `ragTiers` [NEW]

```
ragTiers: [
  { id: "strong",          label: "Strong",          ordinal: 5, oneLineMeaning: ... },
  { id: "onTrack",         label: "On Track",        ordinal: 4, oneLineMeaning: ... },
  { id: "conditional",     label: "Conditional",     ordinal: 3, oneLineMeaning: ... },
  { id: "majorConcerns",   label: "Major Concerns",  ordinal: 2, oneLineMeaning: ... },
  { id: "walkAway",        label: "Walk Away",       ordinal: 1, oneLineMeaning: ... }
]
```

**Authoring task A2:** Write the 5 one-line tier meanings (already drafted in brief §3.1; lift directly).

### 2.3 `ragCalibration` [NEW]

The stage × internal-score-band → tier matrix per brief §5. Encoded as:

```
ragCalibration: {
  scoreBands: [
    { id: "top",          minPct: 0.85 },
    { id: "upperMiddle",  minPct: 0.70 },
    { id: "middle",       minPct: 0.55 },
    { id: "lowerMiddle",  minPct: 0.35 },
    { id: "bottom",       minPct: 0.00 }
  ],
  matrix: {
    identify: { top: "strong", upperMiddle: "strong",  middle: "onTrack",       lowerMiddle: "conditional",   bottom: "majorConcerns" },
    capture:  { top: "strong", upperMiddle: "onTrack", middle: "onTrack",       lowerMiddle: "conditional",   bottom: "majorConcerns" },
    pursue:   { top: "strong", upperMiddle: "onTrack", middle: "conditional",   lowerMiddle: "majorConcerns", bottom: "walkAway" },
    submit:   { top: "strong", upperMiddle: "onTrack", middle: "conditional",   lowerMiddle: "majorConcerns", bottom: "walkAway" }
  },
  criticalQuestionCaps: {
    identify: { strongDisagreeOnCritical: "conditional",   multipleStrongDisagree: "majorConcerns" },
    capture:  { strongDisagreeOnCritical: "majorConcerns", multipleStrongDisagree: "walkAway" },
    pursue:   { strongDisagreeOnCritical: "majorConcerns", multipleStrongDisagree: "walkAway" },
    submit:   { strongDisagreeOnCritical: "walkAway",      multipleStrongDisagree: "walkAway" }
  }
}
```

**Authoring task A3:** Set initial threshold values (above are starting positions per brief §5); confirm via eval-harness boundary fixtures before lock.

### 2.4 `scoring` [RESTRUCTURE]

Drop: `pwinFormula` string, `phases` array (replaced by `stages` + `ragCalibration`), `stageTargets` (same).

Keep: `scorePts` (4-point scale).

Add:
```
scoring: {
  scorePts: { "Strongly Agree": 4, "Agree": 3, "Disagree": 2, "Strongly Disagree": 1 },
  evidenceQualityMultipliers: {
    "high":     1.0,
    "medium":   0.85,
    "low":      0.65,
    "veryLow":  0.40
  },
  formula: {
    perQuestion:  "((response - 1) / 3) * evidenceQualityMultiplier",
    perCategory:  "weighted_average(perQuestion × within_category_qw)",
    perPursuit:   "sum(perCategory × archetype_weighted_category_weight)",
    tierMapping:  "ragCalibration.matrix[stage][scoreBand], capped by criticalQuestionCaps[stage]"
  },
  surfacedToUser: false
}
```

**Authoring task A4:** Confirm evidence-quality multiplier values match v0.1 Alex's existing internal calibration intuitions.

### 2.5 `categories` [REPLACE]

| v0.1 (6) | v0.2 (5 v6 categories) |
|---|---|
| `cp` Competitive Positioning (0.20) | `bndl` Buyer Need & Decision Logic (0.25) |
| `pi` Procurement Intelligence (0.10) | `spa` Stakeholder Position & Access (0.20) |
| `ss` Stakeholder Strength (0.20) | `cpid` Competitive Position & Incumbent Dynamics (0.20) |
| `oi` Organisational Influence (0.20) | `ppsf` Procurement, Proposition & Solution Fit (0.20) |
| `vp` Value Proposition (0.20) | `cdpr` Commercial, Delivery & Pursuit Readiness (0.15) |
| `pp` Pursuit Progress (0.10) | — |

### 2.6 `weightProfiles` [REPLACE]

Replace v0.1's 4 profiles (default/services/technology/advisory) with v6's 8 archetype profiles. Lift values directly from v6 spec `archetype_weights` block.

### 2.7 `archetypeProfile` [RENAME from `oppTypeProfile` + REPLACE values]

| v0.1 mapping (→ profile) | v0.2 archetype id |
|---|---|
| BPO → services | `bpo_managed_service` |
| IT Outsourcing → services | `digital_transformation_si` |
| Managed Service → services | `bpo_managed_service` |
| Digital Outcomes → services | `digital_transformation_si` (or `consulting_advisory` depending on shape) |
| Consulting / Advisory → advisory | `consulting_advisory` |
| Infrastructure & Hardware → technology | `digital_product_saas` (closest match; flag for review) |
| Software / SaaS → technology | `digital_product_saas` |
| — | `facilities_operational` [NEW] |
| — | `hybrid_transformation_managed` [NEW] |
| — | `framework_panel` [NEW] |

Old opp-type strings remain as **aliases** for backward-compatibility so v0.1 pursuit data doesn't lose its archetype on migration.

**Authoring task A5:** Confirm Infrastructure & Hardware mapping (most likely `digital_product_saas` but possibly its own future archetype).

### 2.8 `questionPacks.core` [REPLACE — renamed from `standard`]

Drop all 24 v0.1 questions. Add v6's 25 (Q01–Q25). Per-question structure for each v0.2 question:

```
{
  id: "Q01",
  cat: "bndl",
  topic: "Reason for change now",
  text: "...",
  critical: true|false,                          // v6 critical flag
  whyAsked: "...",                               // from v6 why_asked
  rubric: {                                      // 4-band, v0.1 structure
    "Strongly Agree":     "...",
    "Agree":              "...",
    "Disagree":           "...",
    "Strongly Disagree":  "..."
  },
  hurdles: { ... },                              // v6 hurdle text per band
  benchmarkExamples: { ... },                    // v6 benchmark example per band
  challengeQuestionsByLevel: { ... },            // v6 tiered challenge
  recommendedActionsByLevel: { ... },            // v6 tiered actions
  inflationSignals: [ ... ],                     // CARRIED from closest v0.1 question
  qw: 0.20,                                      // within-category weight
  v0_1_provenance: ["Q1", "Q2"]                  // audit trail of which v0.1 questions this replaces
}
```

**Authoring task A6 (largest single task):** For each of Q01–Q25:
- Lift `text`, `critical`, `whyAsked`, `hurdles`, `benchmarkExamples`, `challengeQuestionsByLevel`, `recommendedActionsByLevel` directly from v6 spec
- Author the 4-band `rubric` in v0.1 voice (v6's hurdles are uniform across questions; v0.1 rubrics are per-question; the v0.2 rubric must be per-question and Alex-flavoured)
- Port `inflationSignals` from the closest v0.1 question per the mapping below; for v6 questions with no v0.1 ancestor, author new inflation signals
- Set `qw` (within-category weight; default to equal-weighting then tune via eval)
- Set `v0_1_provenance` from the v6 `original_vs_new_mapping`

**Inflation-signal port table** (which v0.1 question's signals migrate to which v0.2 question, based on closest semantic match in v6's `original_vs_new_mapping`):

| v0.2 Q | Carries inflation signals from v0.1 |
|---|---|
| Q01 (Reason for change now) | Q3 (Winning Proposition), Q22 (Communication Transparency) |
| Q02 (High-priority problem) | Q3, Q21 |
| Q03 (Outcomes and trade-offs) | Q17 (Co-Developed VP) |
| Q04 (Status quo / retain incumbent) | NEW signals — author |
| Q05 (Why now) | Q7 (Decision Timeline) |
| Q06 (Real decision-makers) | Q8 (Final Veto Rights), Q13 (Network of Influence) |
| Q07 (Access or reliable insight) | Q9 (Internal Champion), Q12 (Decision Authority Relationships) |
| Q08 (Stakeholder anxieties) | Q14 (Personal Agendas), Q15 (Power Dynamics) |
| Q09 (Credible and relevant bidder) | Q11 (Evaluator Coverage), Q20 (Validated Alignment) |
| Q10 (Active buyer pull) | Q21 (Client Engagement), Q23 (Message Adoption) |
| Q11 (Strongest rival identified) | Q2 (Competitive Intelligence) |
| Q12 (Incumbent strengths and vulnerabilities) | Q10 (Competitor Relationships) |
| Q13 (Evidenced advantage over likely winner) | Q1 (Strategy Foundation), Q19 (Differentiated) |
| Q14 (Path to win not based on luck) | Q4 (Countertactics) |
| Q15 (Competitor positioning and response) | Q4 |
| Q16 (Strengths are scoreable) | Q6 (Decision Criteria & Drivers) |
| Q17 (Mandatorys / suitability met) | Q5 (Approval Steps) |
| Q18 (Proposition aligned) | Q17, Q18 (Client Value Justification) |
| Q19 (Proof reduces risk) | Q19 |
| Q20 (Differentiators influence scoring) | Q19, Q20 |
| Q21 (Commercially viable to win) | NEW signals — author |
| Q22 (Delivery & partner credibility) | NEW signals — author |
| Q23 (Risks manageable) | NEW signals — author |
| Q24 (Pursuit team ready) | Q7 |
| Q25 (Opportunity genuinely contestable) | Q24 (Future Focus), Q22 |

(v0.1 questions Q13/Q14/Q15/Q16 inflation signals all flow into v0.2 Q06–Q08 — relationship-bias signals don't disappear; they're re-purposed against the new questions.)

### 2.9 `modifiers.incumbent` [RESTRUCTURE]

Carry verbatim:
- `id`, `name`, `trigger` (extend `matches` if needed)
- All 5 `designPrinciples`
- All 5 `architecture` descriptions (re-cast wording where needed for "Pursuit Viability" terminology, never PWIN)
- All 4 `addsPersonaTriggers.inflationTriggers` (RI-1..RI-4)
- All 4 `addsPersonaTriggers.calibrationRules` (RC-1..RC-4) — re-cast question references to v6 I01–I08 IDs
- All 3 `addsPersonaTriggers.autoVerdictRules` (RA-1..RA-3) — re-cast question references
- Full `addsOutput` (rebidRiskAssessment, all 9 fields including `performanceNarrativeGaps` and `switchingCostQuantification`)
- All 3 `fewShotExamples`

Replace:
- `addsCategory` — replaced by overlay-specific weight injection in archetype profiles (the 7th-category mechanism is replaced by additional questions inside the 5-category model; cleaner)
- `addsQuestions` — v0.1's 12 R-questions replaced by v6's 8 incumbent overlay questions (I01–I08)

The 4 sub-categories from v0.1 (Contract Performance Reality / Position Decay / Retendering Intelligence / Challenger Threat) carry as **conceptual groupings** in the I01–I08 questions, not as a category structure.

**Authoring task A7:** Map each v0.1 R-question's `whyItMatters` paragraph to the closest v6 I-question; carry verbatim into the I-question (v6's hurdles are uniform; v0.1's whyItMatters is richer per-question and is exactly the kind of content Alex needs).

| v0.2 I-question | Carries `whyItMatters` from v0.1 R-question |
|---|---|
| I01 (Buyer would retain us beyond continuity) | R1 (Client Perception Alignment), R6 (Champion Authenticity) |
| I02 (Buyer's reasons to switch away) | R2 (Performance Risk Intelligence), R3 (Value Perception Gap) |
| I03 (Material delivery issues understood) | R2 |
| I04 (Renewal-plus-improvement story) | R12 (Mobilisation Readiness Signal), R3 |
| I05 (Where challengers will attack) | R10 (Challenger Intelligence) |
| I06 (Buyer recognises switching risk) | R11 (Switching Cost Narrative) |
| I07 (Not overexposed on price/complacency/fatigue) | R4 (Relationship Currency), R5 (Political Map Currency) |
| I08 (Defensible value-for-money + improvement) | R7 (Retendering Motivation), R8 (ITT Specification Influence), R9 (Client's Preferred Outcome) |

### 2.10 `modifiers.challenger` [NEW]

```
challenger: {
  id: "challenger",
  name: "Challenger Position Modifier",
  description: "...",
  trigger: { field: "context.role", matches: ["challenger", "Challenger", "We are challenging an incumbent"] },
  designPrinciples: [ ... ],          // [NEW] author
  architecture: [ ... ],              // [NEW] author
  addsQuestions: [ C01..C08 from v6 ],
  addsPersonaTriggers: {
    inflationTriggers: [ ... ],       // [NEW] author — challenger-specific (e.g. "they will switch because they are unhappy" without evidence)
    calibrationRules: [ ... ],        // [NEW] author
    autoVerdictRules: [ ... ]         // [NEW] author
  },
  addsOutput: { ... }                 // see §2.13
}
```

**Authoring task A8:** Author challenger overlay design principles (5), architecture descriptions (5), inflation triggers (4 target), calibration rules (4 target), auto-verdict rules (3 target). Mirror the depth and shape of the incumbent overlay; voice and structure exist as patterns to follow.

### 2.11 `persona` [CARRY VERBATIM with enrichment registry]

The whole `persona` block carries verbatim. The brief locks: `meta` bumped, `identity`/`background`/`coreBeliefs`/`characterTraits`/`toneGuidance`/`languagePatterns`/`hardRules`/`successCriteria` all unchanged.

Enrichments — added as new sub-blocks, not replacing existing:

```
persona: {
  ... existing carried verbatim ...,
  workflowTriggers: {
    autoChallenge:    [ ... existing 3 carried verbatim ... ],
    autoQuery:        [ ... existing 1 carried verbatim ... ],
    calibrationRules: [
      ... existing 4, with question references re-cast to v0.2 IDs ...,
      ... new rules for the 4-stage model ...,            // NEW
      ... new rules for challenger overlay ...            // NEW
    ],
    inflationTriggers: [ ... existing 3 carried verbatim ... ]
  },
  challengeLibrary: { ... },          // [NEW] structured tiered prompts from v6
  actionLibrary:    { ... }           // [NEW] structured tiered action templates from v6
}
```

**Authoring task A9:** Re-cast v0.1's 4 calibration rules to use v0.2 question IDs (mechanical) + author 4 new stage-aware calibration rules (e.g. "Identify stage + Strongly Agree on any Procurement-Scoreability question → flag stage mismatch") + author 4 new challenger-overlay calibration rules.

### 2.12 `opportunityTypeCalibration` [CARRY 7 + NEW 4]

Carry verbatim: BPO, IT Outsourcing, Managed Service, Digital Outcomes, Consulting / Advisory, Infrastructure & Hardware, Software / SaaS.

Author new (matching the same voice and depth):
- Facilities / Field / Operational Service
- Hybrid Transformation + Managed Service
- Framework / Panel Appointment
- (Incumbent Renewal / Rebid is the incumbent overlay, not a separate calibration paragraph — confirm in the brief)

**Authoring task A10:** Write the 3 new calibration paragraphs.

### 2.13 `outputs` [RESTRUCTURE]

```
outputs: {
  viabilityAssessment: {                   // [NEW] — top-level RAG output
    id: "viabilityAssessment",
    name: "Pursuit Viability Assessment",
    description: "...",
    schema: [
      { fieldName: "tier",                   description: "RAG tier id from ragTiers" },
      { fieldName: "narrative",              description: "3–5 paragraph Alex narrative explaining the tier" },
      { fieldName: "topThreeDeterminants",   description: "..." },
      { fieldName: "strongestArgumentAgainst", description: "..." },
      { fieldName: "conditions",             description: "If Conditional/Major Concerns: what would lift the tier" },
      { fieldName: "actions",                description: "Named-role actions, time-bound" },
      { fieldName: "stage",                  description: "..." },
      { fieldName: "criticalQuestionCapsApplied", description: "Audit trail" }
    ]
  },
  perQuestionAssurance: {                  // [CARRY — renamed from standardReport]
    id: "perQuestionAssurance",
    name: "Per-Question Assurance Review",
    description: "Per-question Alex Mercer review producing a verdict (Validated/Queried/Challenged), suggestedScore, narrative, challenge questions, capture actions, and inflation detection. Mechanism unchanged from v0.1.",
    schemaLocation: "inline in app — see buildPersonaPrompt outputSchema parameter"
  },
  rebidRiskAssessment: {                   // [CARRY VERBATIM from v0.1 modifiers.incumbent.addsOutput]
    ... lift verbatim ...
  },
  challengerPositionAssessment: {          // [NEW]
    id: "challengerPositionAssessment",
    name: "Challenger Position Assessment",
    description: "Mirror of rebidRiskAssessment for challenger pursuits. Answers: how viable is our displacement case, and what would the incumbent counter with?",
    schema: [
      { fieldName: "displacementCaseStrength" },        // mirror of incumbentVulnerabilityScore
      { fieldName: "switchingCaseRiskProfile" },        // 4-quadrant RAG: switching motivation / switching risk neutralisation / proof adjacency / contestability
      { fieldName: "incumbentCounterReadiness" },       // mirror of challengerExploitAssessment
      { fieldName: "buyerSwitchingMotivationAssessment" }, // mirror of retenderingMotivationAssessment
      { fieldName: "blindSpots" },                      // mirror — what challengers typically don't know
      { fieldName: "challengerStrategyRecommendation" },// mirror — 4 postures
      { fieldName: "specificDisplacementActions" },     // mirror of specificRemediationActions
      { fieldName: "switchingRiskNeutralisationGaps" }, // mirror of performanceNarrativeGaps
      { fieldName: "proofAdjacencyAssessment" }         // mirror of switchingCostQuantification
    ]
  }
}
```

**Authoring task A11:** Author full descriptions, exampleOutput, and reviewNotes for each `viabilityAssessment` field and each `challengerPositionAssessment` field, matching the depth of `rebidRiskAssessment`.

### 2.14 `sources` [UPDATE]

Add references to the v6 source spec, the positioning brief, and the preservation inventory. Keep v0.1 source references for provenance.

---

## 3. App-side changes (out of JSON, but in scope of v0.2 ship)

### 3.1 Both apps

- Suppress the PWIN number, percentage, and category radar from the headline. Replace with the RAG tier + viability narrative + conditions block.
- Per-question Alex outputs remain as drill-down (mechanism unchanged).
- Stage selector: replace v0.1's stage list with the 4 v0.2 stages.
- Context form: add `role` field (incumbent / challenger / open_field) so the new challenger overlay can trigger.

### 3.2 Consulting standalone ([PWIN_Architect_v1.html](PWIN_Architect_v1.html))

- Add challenger overlay (incumbent already supported)
- Render `challengerPositionAssessment` output when challenger overlay is active
- Add export of internal score for consultant audit purposes (not surfaced in normal UI)

### 3.3 Website MVP ([bidequity-co/qualify-app.html](../../bidequity-co/qualify-app.html))

- Same headline replacement
- **Server-side migration in scope for v0.2** (un-deferred 2026-04-15). Browser becomes thin client: rubrics, hurdles, persona, calibration matrix, RAG logic, and overlay output schemas all move into the Cloudflare Worker. Browser POSTs `{stage, archetype, role, answers[], evidence[]}`; Worker returns `{tier, narrative, conditions, perQuestion[]}`. Question text remains visible (visitors must see questions to answer them); nothing else surfaces in browser source. See [Phase 5b](#phase-5b) below.
- Overlays: TBC — open question whether website MVP gets challenger/incumbent overlays at all (per `feedback_qualify_lead_gen_scope`, MVP is deliberately under-enriched). Default: NO overlays in MVP; overlays are a paid-tier differentiator. Confirm with user before app-wiring.

### 3.4 Build script

`build-content.js` needs no functional change — sentinel injection works for any content shape. The `--check` mode runs unchanged.

---

## 4. Eval harness changes

- All v0.1 fixtures are invalidated by question changes. Park them in `eval-fixtures/v0.1-archive/`.
- Author starter v0.2 fixtures: minimum 1 per RAG tier × 1 per stage × 1 incumbent + 1 challenger = ~10 fixtures to lock the calibration table.
- Add a new fixture type: **boundary fixtures** that test the stage→tier mapping at the score-band edges (e.g. "score = 0.84 at Capture stage → On Track; score = 0.85 at Capture stage → Strong"). These tune `ragCalibration` thresholds.
- Add a new fixture type: **critical-cap fixtures** that test the critical-question cap behaviour at each stage.

**Authoring task A12:** Build the v0.2 fixture set (~15 fixtures total).

---

## 5. Authoring task summary and rough effort

Honest effort estimate (Claude doing the work end-to-end, not user authoring in evenings):

| ID | Task | Effort |
|---|---|---|
| A1 | 4 stage descriptions | 0.25 day |
| A2 | 5 RAG tier meanings (lift from brief) | 0.1 day |
| A3 | RAG calibration thresholds + tune via eval | 0.5 day initial + ongoing |
| A4 | Confirm evidence-quality multipliers | 0.1 day |
| A5 | Confirm Infrastructure & Hardware archetype mapping | 0.1 day |
| **A6** | **25 v0.2 questions: lift v6 text/hurdles/challenges/actions, author rubrics, port inflation signals, set qw + provenance** | **3 days** |
| A7 | Map 12 v0.1 R-question whyItMatters paragraphs onto 8 I-questions | 0.5 day |
| A8 | Challenger overlay: principles, architecture, inflation/calibration/auto-verdict rules (mostly mirror incumbent overlay) | 1 day |
| A9 | Persona calibration rules: re-cast 4 + author 4 stage rules + 4 challenger rules | 0.5 day |
| A10 | 3 new opportunity-type calibration paragraphs | 0.5 day |
| A11 | Full schemas for `viabilityAssessment` + `challengerPositionAssessment` outputs | 0.5 day |
| A12 | v0.2 eval fixtures (~15 fixtures) | 1 day |
| — | App wiring — consulting standalone | 1 day |
| — | App wiring — website MVP **including server-side migration (Phase 5b)** | 3 days |
| — | Brand/copy refresh ("PWIN" → "Pursuit Viability") | 0.5 day |

**Honest total: 10–13 days of focused work, ~2–3 weeks elapsed in normal session cadence.** Earlier 4–6 week estimate was padded.

---

## 6. Sequencing — what gets done in what order

**Cutover approach (agreed 2026-04-15):** v0.2 replaces v0.1 in place. No parallel build, no archive routes, no localStorage migration. Tag the v0.1 commit (`git tag qualify-v0.1-final`) before Phase 1 starts so it's recoverable in one command. No paying customers in flight, so the ceremony of a coordinated cutover isn't justified.

### Phase 1 — Foundation (no authoring of question content yet)
1. Create `qualify-content-v0.2.json` skeleton with all sections present but `questionPacks.core.questions` empty
2. A1 (stages), A2 (RAG tiers), A3 initial values (calibration table), A4 (multipliers), A5 (archetype mapping)
3. Set up `categories`, `weightProfiles`, `archetypeProfile` from v6 spec

### Phase 2 — Question authoring (the big sprint)
4. A6 — author all 25 questions in waves of 5 (one wave per category)
5. A7 — port whyItMatters paragraphs into incumbent overlay
6. A8 — author challenger overlay
7. A9 — re-cast and extend persona calibration rules
8. A10 — 3 new opp-type calibration paragraphs

### Phase 3 — Outputs and personas
9. A11 — author `viabilityAssessment` + `challengerPositionAssessment` schemas
10. Carry-forward checks: persona block, opportunityTypeCalibration block, modifiers.incumbent.addsOutput (`rebidRiskAssessment`)
11. Build script `--check`: confirm v0.2 builds and is idempotent

### Phase 4 — Eval and tune
12. A12 — author v0.2 fixture set
13. Run eval; tune `ragCalibration` thresholds, `criticalQuestionCaps`, evidence-quality multipliers, within-category weights (`qw`)
14. Lock the calibration table

### Phase 5 — App wiring
15. Both apps: PWIN-number suppression, RAG tier rendering, stage selector, context.role field
16. Consulting standalone: challenger overlay rendering, `challengerPositionAssessment` rendering
17. Brand/copy refresh

<a id="phase-5b"></a>
### Phase 5b — Website MVP server-side migration
18. Move `qualify-content-v0.2.json` into the Cloudflare Worker (`bidequity-co/workers/ai-review.js`)
19. Worker assembles the full system prompt server-side (questions + rubrics + persona + calibration + overlay logic + RAG mapping)
20. Refactor `bidequity-co/qualify-app.html` to thin client: posts `{stage, archetype, role, answers[], evidence[]}` to Worker, receives `{tier, narrative, conditions, perQuestion[]}`, renders only what comes back
21. Confirm overlay scope on website MVP (default: no overlays per `feedback_qualify_lead_gen_scope`)
22. Verify View Source on the deployed MVP shows only question text — no rubrics, persona, calibration, or RAG matrix
23. Add `wrangler deploy` step to the publishing workflow in `pwin-qualify/content/README.md`

### Phase 6 — Ship
19. End-to-end test with both apps against the eval fixtures
20. User acceptance walkthrough on a real pursuit
21. Cut v0.2 build, commit JSON + both HTML files together

---

## 7. Open items not blocking content delta

- **Website MVP overlay scope** (§3.3 default = no overlays; needs user confirmation before app wiring, but does not block JSON authoring)
- **Per-archetype critical-question lists** — v6's 9 critical flags are universal; eval may show some questions are critical only for some archetypes (e.g. `Q17 Mandatorys/Suitability` is critical at any stage for Framework/Panel but less so for Consulting). Tune via eval, not pre-authored.
- **Orphan content** ([PWIN_AI_Enrichment_Review.xlsx](PWIN_AI_Enrichment_Review.xlsx) and [BWIN Qualify_AI Design_Proforma_v2.xlsx](BWIN%20Qualify_AI%20Design_Proforma_v2.xlsx)) — DEFERRED to v0.3 per user 2026-04-15. Not in this delta.

---

**This delta plan is the complete authoring brief for v0.2.** With this and the preservation inventory, any authoring task above could be picked up by Claude (or by the user) without further specification of what needs to change. The next step is execution — start with Phase 1.
