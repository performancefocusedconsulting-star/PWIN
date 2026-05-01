# Output Schema and Report Template

This file defines the structured output the agent must produce. The agent outputs **both**:
1. A JSON object conforming to the schema below (for downstream agent consumption)
2. A markdown report conforming to the template below (for human consumption)

Both must contain the same information. The JSON is the machine-readable interface contract.
The markdown is the human-readable deliverable.

## Table of Contents

1. File Naming Convention
2. Versioning
3. JSON Output Schema
4. Markdown Report Template

---

## 1. File Naming Convention

All outputs use this naming pattern:

```
{pursuitId}_incumbent_assessment_{YYYY-MM-DD}.md
{pursuitId}_incumbent_assessment_{YYYY-MM-DD}.json
```

Example: `PUR-2026-0042_incumbent_assessment_2026-04-24.md`

When producing a refresh (not a first assessment), the new date distinguishes it from
previous versions. Do not overwrite previous assessments — the history is valuable.

---

## 2. Versioning

Each assessment carries an `assessmentDate` in the JSON and a date in the filename.
When refreshing:
- Include a `previousAssessmentDate` field in the JSON
- Include a delta summary at the top of the markdown: "Changes since [date]: ..."
- Note which scores changed and whether the recommendation changed

---

## 3. JSON Output Schema

The schema conforms to the BidEquity Universal Skill Spec. The `meta`,
`changeSummary`, and `sourceRegister` blocks are universal; the
`incumbentAssessment` body is integrator-specific.

```yaml
meta:
  pursuitId: string
  skillName: "incumbency-advantage-displacement-strategy"
  version: string  # x.y.z e.g. "1.0.0", "3.1.2"
  mode: build | refresh | inject | amend
  builtDate: YYYY-MM-DD
  lastModifiedDate: YYYY-MM-DD
  depthMode: quick | standard | deep
  degradedMode: boolean
  degradedModeReason: string | null
  sourceCount: integer
  internalSourceCount: integer
  prerequisitesPresentAt:
    version: string
    date: YYYY-MM-DD
    required:
      pursuitContext: boolean
      buyerDossier: boolean
      supplierDossierIncumbent: boolean
    preferred:
      ittDocuments: boolean
      stakeholderMap: boolean
      capturePlan: boolean
      latestQualifyRun: boolean
      sectorBrief: boolean
      clientIntelligence: boolean
  versionLog:
    - version: string
      date: YYYY-MM-DD
      mode: build | refresh | inject | amend
      summary: string

changeSummary:
  - section: string
    field: string
    before: string
    after: string
    reason: string

deltaSummary: string | null  # one-line summary of changes since previous version (refresh only)

claims:
  - claimId: string           # INC-CLM-NNN format (integrator prefix required)
    claimText: string         # assertion text, self-contained
    claimDate: YYYY-MM-DD     # when this skill asserted the claim
    source: string            # SRC-nnn, URL, or upstream dossier reference e.g. "Buyer dossier: HMRC, claim CLM-014"
    sourceDate: YYYY-MM-DD | null
    sourceTier: 1 | 2 | 3 | 4
    derivedFrom: list[string] # optional — upstream claim IDs e.g. ["BUYER:CLM-014", "SUPPLIER:CLM-022"]

incumbentAssessment:
  executiveJudgement:
    summary: string
    headlineRecommendation: go | go_with_conditions | selective_go | no_go | defensive_recompete | intelligence_gap
    rationale: string
    confidence: high | medium | low
    deltaSummary: string | null (for refreshes — what changed and why)

  incumbentScenario:
    type: single_incumbent_prime | multi_incumbent | incumbent_recompete | in_house_service | fragmented_legacy_estate | jv_or_consortium_incumbent | unknown_incumbent | no_true_incumbent
    summary: string
    confidence: high | medium | low

  incumbentProfile:
    supplierName: string
    knownSubcontractors: list[string]
    contractHistory:
      - contractTitle: string
        buyer: string
        startDate: string
        endDate: string
        extensionOptions: string
        contractValue: string
        scope: string
        sourceRefs: list[string]
    deliveryModel: string
    knownKeyPersonnel: list[string]
    financialHealthIndicators: string | null
    confidence: high | medium | low

  procurementContext:
    routeToMarket: string
    frameworkDetails: string | null
    lotStructure: string
    evaluationWeightings:
      quality: number
      price: number
      socialValue: number
      other: number
    requirementsBiasToIncumbent:
      score: number (1-5)
      rationale: string
      evidenceRefs: list[string]
    buyerIntent:
      classification: renewal | market_test | transformation | cost_reduction | service_recovery | compliance_reprocurement | unknown
      rationale: string
      confidence: high | medium | low

  performanceAssessment:
    overallRating: strong | adequate | weak | unknown
    slaEvidence:
      - finding: string
        sourceRef: string
        claimLabel: evidenced_fact | informed_inference | unverified_intelligence | open_question | requires_human_validation
        evidenceAge: string (e.g. "14 months")
        confidence: high | medium | low
    serviceFailures: list[string]
    serviceStrengths: list[string]
    clientSatisfactionSignals: list[string]
    assessmentLimitations: list[string]

  incumbentAdvantage:
    performanceStrength:
      score: number (1-5)
      rationale: string
    relationshipEmbeddedness:
      score: number (1-5)
      rationale: string
    operationalKnowledge:
      score: number (1-5)
      rationale: string
    systemsAndDataStickiness:
      score: number (1-5)
      rationale: string
    tupeAndWorkforceComplexity:
      score: number (1-5)
      rationale: string
    switchingCost:
      score: number (1-5)
      rationale: string
    securityClearanceBarrier:
      score: number (1-5) | null
      rationale: string | null
      applicable: boolean
    socialValueAdvantage:
      score: number (1-5) | null
      rationale: string | null
      applicable: boolean
    incumbentFinancialHealth:
      score: number (1-5) | null
      rationale: string | null
      applicable: boolean
    overallStickinessScore: number (1-5)

  incumbentVulnerabilities:
    - vulnerability: string
      evidence: string
      sourceRef: string
      claimLabel: evidenced_fact | informed_inference | unverified_intelligence | open_question | requires_human_validation
      confidence: high | medium | low
      permittedBidUse: string (direct | indirect | internal_only | none)
      riskOfUsingInBid: low | medium | high

  buyerSwitchingPsychology:
    likelyBuyerConcerns: list[string]
    changeAppetite:
      score: number (1-5)
      rationale: string
    fearOfTransition:
      score: number (1-5)
      rationale: string
    relationshipLoyaltyRisk:
      score: number (1-5)
      rationale: string
    procurementIntentHypothesis: string

  challengerPosition:
    challengerDifferentiation:
      score: number (1-5)
      rationale: string
    challengerType: sme | large_prime | mid_tier | consortium | unknown
    requiredProofPoints: list[string]
    weaknessesInChallengerPosition: list[string]

  strategy:
    strategicPosture: evolution_not_replacement | service_recovery | transformation | price_challenge | innovation_challenge | defensive_recompete | selective_lot_strategy | defer_pending_intelligence
    coreNarrative: string
    winThemes: list[string]
    messagesToUse: list[string]
    messagesToAvoid: list[string]
    clarificationQuestions: list[string]

  recompeteStrategy:
    isApplicable: boolean
    strengthsToEmphasise: list[string]
    weaknessesToAddress: list[string]
    continuousImprovementNarrative: string
    renewalRisks: list[string]

  goNoGoImplications:
    incumbentAdvantageScore: number (1-5)
    incumbentVulnerabilityScore: number (1-5)
    buyerChangeAppetiteScore: number (1-5)
    transitionRiskScore: number (1-5)
    challengerDifferentiationScore: number (1-5)
    displacementFeasibilityScore: number (1-5)
    recommendedDecision: go | go_with_conditions | selective_go | no_go | defensive_recompete | intelligence_gap
    decisionRationale: string
    conditionsToProceed: list[string]
    conditionsToWalkAway: list[string]
    pwinScoreAlignment: aligned | misaligned | pwin_not_available
    pwinReconciliationNote: string | null

  bidExecutionActions:
    solutionActions: list[string]
    commercialActions: list[string]
    legalAndContractActions: list[string]
    deliveryActions: list[string]
    evidenceActions: list[string]
    relationshipAndCaptureActions: list[string]
    redTeamQuestions: list[string]

  openQuestions: list[string]

internalAmendments:
  - sourceId: string  # SRC-INT-001 etc
    date: YYYY-MM-DD
    type: debrief | crmNote | accountTeam | partnerIntel
    author: string
    content: string
    sectionsAffected: list[string]
    confidence: high | medium | low
    claimLabel: unverified_intelligence | requires_human_validation

sourceRegister:
  sources:
    - sourceId: string  # SRC-001, SRC-002, SRC-INJ-005 etc
      tier: 1 | 2 | 3
      sourceType: procurement_document | foi | audit_report | regulator_report | news | supplier_marketing | inference | framework_data | companies_house | upstream_artefact | unknown
      title: string
      publicationDate: YYYY-MM-DD | null
      accessDate: YYYY-MM-DD
      url: string | null
      sectionsSupported: list[string]
      evidenceAge: string  # e.g. "14 months"
      reliability: high | medium | low
      notes: string
  internalSources:
    - sourceId: string  # SRC-INT-001 etc
      tier: 4
      sourceType: internal
      sourceName: string
      accessDate: YYYY-MM-DD
      sectionsSupported: list[string]
  gaps: list[string]
  staleFields: list[string]
  lowConfidenceInferences: list[string]
```

### Note on upstream-artefact sourcing

When this skill consumes data from a buyer dossier or supplier dossier, it
records that consumption in `sourceRegister.sources` with
`sourceType: upstream_artefact`. The `notes` field should reference the
upstream artefact's slug and version, e.g. `"buyer-intelligence v3.1.0
home-office-dossier"`. This makes the integrator's evidence chain
auditable back to the producer skill outputs that informed it.

---

## 4. Markdown Report Template

Use this template for the human-readable output. Every section must be populated.
Sections that cannot be completed due to data gaps must state why and what is needed.

```markdown
# Incumbency Advantage & Displacement Strategy

**Pursuit:** {pursuitId}
**Date:** {YYYY-MM-DD}
**Depth:** {quick | standard | deep}
**Confidence:** {high | medium | low}

{If degraded mode: "**DEGRADED MODE:** This assessment is produced with limited data.
[Specific gaps]. Sections marked * require validation before use in a governance decision."}

{If refresh: "**Changes since {previous date}:** [Delta summary — what changed, which
scores moved, whether the recommendation changed]."}

## 1. Executive Judgement

- **Recommendation:** {go | go_with_conditions | selective_go | no_go | defensive_recompete | intelligence_gap}
- **Displacement feasibility:** {1-5}
- **Incumbent advantage:** {1-5}
- **Buyer change appetite:** {1-5}
- **Transition risk:** {1-5}
- **Confidence:** {high | medium | low}

{Concise judgement explaining whether the incumbent can realistically be displaced or
defended against, what conditions matter, and what the bid team should do.}

## 2. Incumbent Scenario Classification

**Scenario type:** {type}

**Rationale:** {Explain the current delivery context and why this classification matters.}

**Strategic implication:** {How the scenario changes win strategy and go/no-go.}

## 3. Contract and Procurement Context

- **Current contract history:**
- **Contract value and duration:**
- **Current scope:**
- **Procurement route:**
- **Framework (if applicable):**
- **Lot structure:**
- **Evaluation criteria:**
- **Evidence of incumbent bias in requirements:**
- **Buyer intent hypothesis:**

**Assessment:** {Whether this looks like a genuine displacement opportunity, market test,
renewal, transformation, cost reduction, service recovery, or compliance re-procurement.}

## 4. Incumbent Profile

- **Incumbent supplier:**
- **Known subcontractors:**
- **Delivery model:**
- **Known key personnel:**
- **Relationship footprint:**
- **Relevant adjacent contracts:**
- **Financial health indicators:**

**Confidence:** {high | medium | low}

## 5. Performance and Satisfaction Assessment

**Overall performance rating:** {strong | adequate | weak | unknown}

| Finding | Source | Claim Label | Evidence Age | Confidence | Implication |
|---|---|---|---|---|---|

**Assessment:** {What the evidence suggests and what it does not prove.}

## 6. Incumbent Advantage and Stickiness Analysis

| Dimension | Score (1-5) | Rationale | Bid Implication |
|---|---:|---|---|
| Performance strength | | | |
| Relationship embeddedness | | | |
| Operational knowledge | | | |
| Systems and data stickiness | | | |
| TUPE and workforce complexity | | | |
| Switching cost | | | |
| Requirements bias to incumbent | | | |
| Security clearance barrier* | | | |
| Social value advantage* | | | |
| Incumbent financial health* | | | |

*Contextual dimensions — scored only where applicable.

**Overall stickiness score:** {1-5}

**Assessment:** {Why displacement would be easy, difficult, or conditional.}

## 7. Vulnerability Analysis

| Vulnerability | Evidence | Claim Label | Confidence | Permitted Bid Use | Risk of Using |
|---|---|---|---|---|---|

**Assessment:** {Which vulnerabilities are strategically useful and which require validation.}

## 8. Buyer Switching Psychology

**Why the buyer may stay:**
- {Reason}

**Why the buyer may change:**
- {Reason}

**Likely buyer fears:**
- {Reason}

**Relationship loyalty risk:** {low | medium | high}

**Assessment:** {The emotional, operational, political, and commercial psychology of switching.}

## 9. Challenger Credibility

**Challenger type:** {sme | large_prime | mid_tier | consortium | unknown}
**Challenger differentiation score:** {1-5}

**Strengths:**
- {Strength}

**Gaps:**
- {Gap}

**Required proof points:**
- {Proof point}

**Assessment:** {Whether the bidder can credibly displace or defend, based on its own
capability and evidence.}

## 10. Displacement or Defensive Strategy

**Strategic posture:** {posture}

**Core narrative:** {Recommended narrative.}

**Strategic approach:** {Explain the strategy.}

## 11. Go/No-Go Implications

| Factor | Score (1-5) | Directional Impact | Rationale |
|---|---:|---|---|
| Incumbent advantage | | strengthens/weakens incumbent | |
| Incumbent vulnerability | | strengthens/weakens challenger | |
| Buyer change appetite | | strengthens/weakens challenger | |
| Transition risk | | strengthens/weakens incumbent | |
| Challenger differentiation | | strengthens/weakens challenger | |
| Displacement feasibility | | overall | |

**Recommended decision:** {decision}

**PWIN alignment:** {aligned | misaligned | not available}
{If misaligned: reconciliation note.}

**Conditions to proceed:**
- {Condition}

**Conditions to walk away:**
- {Condition}

## 12. Win Themes, Messages to Use, and Messages to Avoid

**Win themes:**
- {Theme}

**Messages to use:**
- {Message}

**Messages to avoid:**
- {Message}

## 13. Proof Points Required

- {Proof point}

## 14. Bid Execution Action Plan

| Workstream | Actions |
|---|---|
| Solution | |
| Commercial | |
| Legal and contract | |
| Delivery and mobilisation | |
| Evidence | |
| Relationship and capture | |

## 15. Red-Team Questions

- Are we underestimating the incumbent's relationship advantage?
- Are we assuming buyer dissatisfaction without evidence?
- Are we treating transition risk as lower than the buyer will perceive it?
- Are we relying on generic transformation claims rather than specific proof?
- Are the requirements structurally favourable to the incumbent?
- Would our proposed solution feel safer than staying with the incumbent?
- What would cause the buyer to choose continuity over change?
- What evidence would make us stop bidding?
{Add pursuit-specific red-team questions here.}

## 16. Source Register and Confidence Assessment

| Source | Type | Date | Age | Reliability | Claims Supported | Notes |
|---|---|---|---|---|---|---|

**Overall confidence:** {high | medium | low}

**Evidence limitations:**
- {Limitation}

## 17. Open Questions for Human Validation

- {Question}
```

---

## `claims` (array, required)

Top-level array of structured claim objects. Every material assertion in
the incumbent assessment must appear here with a stable `claimId`. The
narrative cites claims inline using `[INC-CLM-id]` markers.

As an integrator skill, incumbency-advantage-displacement-strategy uses
the `INC-CLM-` prefix to distinguish its claims from those in the upstream
producer dossiers it consumes. The optional `derivedFrom` field records
which upstream claims the integrator claim was synthesised from, enabling
the Forensic Intelligence Auditor to trace the full evidence chain.

```json
{
  "claims": [
    {
      "claimId": "INC-CLM-001",
      "claimText": "Serco has held the MoJ Electronic Monitoring contract continuously since 2014, giving it deep operational knowledge of tagging hardware, offender compliance workflows, and MoJ governance contacts.",
      "claimDate": "2026-05-01",
      "source": "Supplier dossier: serco-group-plc, claim CLM-001",
      "sourceDate": "2023-11-15",
      "sourceTier": 1,
      "derivedFrom": ["SUPPLIER:CLM-001"]
    }
  ]
}
```

The six base fields are mandatory on every claim. `derivedFrom` is optional
but expected on every claim that synthesises from an upstream producer
dossier. Schema and validation rules live in
`pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md`
(canonical) and §13 of the Universal Skill Spec.
