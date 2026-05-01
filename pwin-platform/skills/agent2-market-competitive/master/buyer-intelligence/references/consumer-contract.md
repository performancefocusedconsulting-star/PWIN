# Consumer Retrieval Contract — Buyer Dossier v3.0

This contract documents how downstream consumer skills should read the buyer
dossier. It exists because the dossier is organised by buyer subject (16
sections) but consumers reason by **decision question** and by
**intelligence lens**. The contract translates between the two.

The contract carries three retrieval views:

1. **By decision question** — the canonical pursuit-team questions that
   consumers ultimately answer (Section A: Pursue / no-pursue, Section B:
   Win Strategy, Section C: Capture Plan)
2. **By intelligence lens** — the seven lenses around which the dossier is
   organised
3. **By document → question** — for each high-value document type, which
   pursuit-team questions it informs

Consumers pick the view that matches how they reason. Most will use view 1
or view 2; view 3 is useful for inject and refresh planning.

**Important boundary:** the dossier surfaces *context, inference, and data
points*. The consumer does the synthesis. Do not expect the dossier to
pre-judge whether to pursue, what win themes to choose, or how to engage —
those are the consumer's job.

---

## Consumers of this dossier

| Consumer skill / product | Lens emphasis | Primary decision questions |
|---|---|---|
| **Qualify (PWIN-Qualify)** | Pressure, Money, Risk posture, Pursuit implications | Section A (Pursue / no-pursue) |
| **Win Strategy (Agent 3)** | Pressure, Buying behaviour, Supplier landscape, Pursuit implications | Section B (Win architecture) |
| **Capture Plan (Agent 3)** | Buying behaviour, Supplier landscape (Tier 5), Pursuit implications | Section C (Capture engagement) |
| **Bid Execution (pwin-bid-execution)** | Buying behaviour, Risk posture, Pursuit implications | Operational discipline during bid production |
| **Incumbency-Displacement (Agent 2)** | Pressure, Risk posture, Supplier landscape | What does the incumbent have / what would displace them |
| **Verdict (BidEquity-Verdict)** | All seven (forensic post-loss review) | Did the dossier predict the loss; what was missing |

---

## View 1 — Retrieval by decision question

### Section A — Pursue / no-pursue (Qualify)

#### A1: Is there a real change-driver, or is this BAU re-procurement?

```
Primary paths:
  - commissioningContextHypotheses.driversOfExternalBuying
  - organisationContext.recentChanges
  - strategicPriorities.politicalPressures
  - strategicPriorities.regulatoryPressures
  - strategicPriorities.fiscalPressures

Supporting paths:
  - buyerSnapshot.executiveSummary.headline
  - meta.refreshTriggers (recent events that triggered refresh)
  - actionRegister.actions[] where gap.frameworkQuestionsBlocked includes "A1"
```

#### A2: Are they actually ready to buy?

```
Primary paths:
  - commissioningContextHypotheses.buyingReadiness
  - commissioningContextHypotheses.approvalsPending
  - commissioningContextHypotheses.commissioningCycleStage
  - commissioningContextHypotheses.spendClassification

Supporting paths:
  - commercialAndRiskPosture.affordabilitySensitivity
  - procurementBehaviour.summaryNarrative (recent activity = buying readiness signal)
```

#### A3: What outcomes are they trying to achieve, with quantified targets?

```
Primary paths:
  - commissioningContextHypotheses.outcomesSought
  - strategicPriorities.majorProgrammes[].quantifiedTargets
  - strategicPriorities.publishedStrategyThemes
  - strategicPriorities.publicStatementsOfIntent

Supporting paths:
  - strategicPriorities.servicePerformancePressures
  - meta.extractionTemplatesApplied (deep-extracted sources = strongest evidence)
```

#### A4: How likely are they to cancel or restart?

```
Primary paths:
  - procurementBehaviourSnapshot.cancellationRateVsPeers
  - procurementBehaviourSnapshot.cancellationRatePercentage
  - procurementBehaviourSnapshot.outcomeMix
  - procurementBehaviourSnapshot.noticeToAwardDays
  - procurementBehaviourSnapshot.consultantSummarySentence

Supporting paths:
  - risksAndSensitivities.procurementControversies
  - commissioningContextHypotheses.timelineRisks
```

#### A5: What is the scrutiny exposure?

```
Primary paths:
  - risksAndSensitivities.summaryNarrative
  - risksAndSensitivities.auditFindings
  - risksAndSensitivities.programmeFailures
  - risksAndSensitivities.mediaScrutiny
  - risksAndSensitivities.publicSensitivities

Supporting paths:
  - strategicPriorities.politicalPressures
  - commercialAndRiskPosture.auditFoiExposure
```

---

### Section B — Win Strategy (Agent 3)

#### B1: Who are the actual decision-makers and what does each care about?

```
Primary paths:
  - decisionUnitAssumptions.businessOwnerRoles
  - decisionUnitAssumptions.commercialRoles
  - decisionUnitAssumptions.technicalStakeholders
  - decisionUnitAssumptions.financeAssuranceRoles
  - decisionUnitAssumptions.evaluatorGroups
  - decisionUnitAssumptions.perRoleInterests
  - decisionUnitAssumptions.internalTensions
  - decisionUnitAssumptions.dominantDecisionLens

Supporting paths:
  - organisationContext.seniorLeadership (named SROs with backgrounds)
  - relationshipHistory.executiveRelationships (Tier 5)
```

#### B2: What does the incumbent have that a challenger doesn't?

```
Primary paths:
  - supplierEcosystem.incumbents[].entrenchmentIndicators
  - supplierEcosystem.incumbents[].strategicImportance
  - supplierEcosystem.incumbents[].longestRelationship
  - supplierEcosystem.incumbents[].contractCount

Supporting paths:
  - supplierEcosystem.barriersToEntry
  - supplierEcosystem.switchingEvidence
```

#### B3: Is the incumbent distressed?

```
Primary paths:
  - supplierEcosystem.incumbents[].vulnerabilitySignals
  - supplierEcosystem.incumbents[].vulnerabilitySignals.overallVulnerability
  - supplierEcosystem.incumbents[].recentActivity
  - procurementBehaviourSnapshot.distressedIncumbentFlag

Supporting paths:
  - risksAndSensitivities.programmeFailures (where supplier named)
  - procurementBehaviourSnapshot.distressedIncumbentEvidence
```

#### B4: What are the buyer's published priorities, programme by programme?

```
Primary paths:
  - strategicPriorities.publishedStrategyThemes
  - strategicPriorities.majorProgrammes (full array — name, value, SRO, timeline, quantified targets, dependencies)

Supporting paths:
  - strategicPriorities.publicStatementsOfIntent
  - meta.extractionTemplatesApplied (programmes from extracted strategy docs are strongest)
```

#### B5: What is their evaluation bias?

```
Primary paths:
  - procurementBehaviour.priceVsQualityBias
  - procurementBehaviour.innovationVsProven
  - cultureAndPreferences.riskTolerance
  - cultureAndPreferences.evidencePreferences
  - cultureAndPreferences.socialValueAndESG

Supporting paths:
  - decisionUnitAssumptions.dominantDecisionLens
  - cultureAndPreferences.languageAndFraming
```

#### B6: What anxiety / constraint must be neutralised before they switch?

```
Primary paths:
  - commercialAndRiskPosture.mobilisationSensitivity
  - cultureAndPreferences.riskTolerance
  - supplierEcosystem.incumbents[].entrenchmentIndicators
  - commissioningContextHypotheses.timelineRisks

Supporting paths:
  - risksAndSensitivities.positioningSensitivities
  - decisionUnitAssumptions.businessOwnerRoles (SRO career-risk angle)
  - pursuitImplications.implications[] where category == "risk-management"
```

---

### Section C — Capture Plan (Agent 3) and Bid Execution

#### C1: Who do we engage, in what order, before the quiet period?

```
Primary paths:
  - decisionUnitAssumptions (full section — roles, interests, tensions, dominant lens)
  - organisationContext.seniorLeadership
  - relationshipHistory.executiveRelationships (Tier 5)
  - relationshipHistory.knownAdvocates (Tier 5)

Supporting paths:
  - pursuitImplications.implications[] where category == "engagement"
  - cultureAndPreferences.supplierInteractionStyle

Note: the dossier provides the inputs. Engagement *order* is the Capture
Plan's output, not the dossier's.
```

#### C2: Who is an advocate, who is a blocker?

```
Primary paths (Tier 5 only — populated via amend):
  - relationshipHistory.knownAdvocates
  - relationshipHistory.knownBlockers
  - relationshipHistory.executiveRelationships

If empty: the dossier has not yet been amended. Action register should carry
a tier4-amend / tier5-amend action with owner: account-director.
```

#### C3: What is their commercial posture?

```
Primary paths:
  - commercialAndRiskPosture.affordabilitySensitivity
  - commercialAndRiskPosture.riskTransferPosture
  - commercialAndRiskPosture.contractualCaution
  - commercialAndRiskPosture.preferredCommercialModels
  - commercialAndRiskPosture.paymentTermsNorms

Supporting paths:
  - procurementBehaviour.typicalContractLength
  - commissioningContextHypotheses.spendClassification
```

---

## View 2 — Retrieval by intelligence lens

### Mandate lens

What this buyer exists to deliver.

```
- buyerSnapshot.legalName, organisationType, sector, geographicRemit, headcount, annualBudget
- buyerSnapshot.organisationalArchetype
- organisationContext.mandate, operatingModel, organisationStructure
- organisationContext.keyBusinessUnits, seniorLeadership
- organisationContext.fundingModel
```

### Pressure lens

What is forcing action now.

```
- strategicPriorities.publishedStrategyThemes
- strategicPriorities.regulatoryPressures, politicalPressures, fiscalPressures
- strategicPriorities.servicePerformancePressures
- strategicPriorities.publicStatementsOfIntent
- commissioningContextHypotheses.driversOfExternalBuying
- commissioningContextHypotheses.pressuresShapingSpend
- commissioningContextHypotheses.consequencesOfInaction
- risksAndSensitivities.summaryNarrative (where scrutiny is the pressure)
- organisationContext.recentChanges (machinery of government, leadership change)
```

### Money lens

What is funded, constrained, or exposed.

```
- buyerSnapshot.annualBudget
- organisationContext.fundingModel
- commissioningContextHypotheses.spendClassification
- commissioningContextHypotheses.approvalsPending
- commercialAndRiskPosture.affordabilitySensitivity
- procurementBehaviour.totalValue, typicalContractValue
- procurementBehaviour.totalAwards
- strategicPriorities.majorProgrammes[].quantifiedTargets (savings, displacement)
- strategicPriorities.fiscalPressures
```

### Buying behaviour lens

How they actually procure.

```
- procurementBehaviour (full section)
- procurementBehaviourSnapshot (full section — the Tier 4 pinned data)
- commercialAndRiskPosture.preferredCommercialModels
- commercialAndRiskPosture.paymentTermsNorms
- decisionUnitAssumptions.dominantDecisionLens
```

### Risk posture lens

What they are trying to avoid.

```
- cultureAndPreferences.riskTolerance, governanceIntensity, evidencePreferences
- cultureAndPreferences.changeMaturity
- commercialAndRiskPosture (full section)
- risksAndSensitivities (full section)
```

### Supplier landscape lens

Who is embedded, who is vulnerable.

```
- supplierEcosystem (full section, including per-incumbent vulnerabilitySignals)
- supplierEcosystem.barriersToEntry
- procurementBehaviourSnapshot.distressedIncumbentFlag
- relationshipHistory (Tier 5 — only when amended)
```

### Pursuit implications lens

What any pursuit against this buyer should do or avoid.

```
- pursuitImplications.summaryNarrative
- pursuitImplications.implications[] (full array — buyer-derived, bidder-neutral)
- buyerSnapshot.keyRisks
- buyerSnapshot.executiveSummary.headline
```

---

## View 3 — Retrieval by document type → questions answered

When planning a refresh or considering which document to inject, use this
table to forecast which decision questions will be (re-)answered.

| Document type | Questions primarily informed | Lenses primarily contributed |
|---|---|---|
| Annual Report | A2, A3, A5, B5, C3 | Mandate, Money, Risk posture |
| Outcome Delivery Plan | A1, A3, B4, B5 | Mandate, Pressure |
| Departmental Strategy | A1, A3, B4, B5 | Mandate, Pressure |
| Digital / transformation strategy | A1, A3, B4, B5 | Pressure, Money, Buying behaviour, Pursuit implications |
| Cyber security strategy | B5, C3 | Risk posture, Pressure |
| Workforce / People plan | A3, B6 | Mandate, Pressure |
| Commercial / procurement strategy | A2, B5, C3 | Buying behaviour, Money |
| Spending Review settlement | A1, A2, A3, C3 | Money, Pressure |
| Major Projects Portfolio (IPA / GMPP) | A1, A4, B3, B4 | Pressure, Supplier landscape, Risk posture |
| NAO / PAC report | A1, A5, B3, B6 | Risk posture, Pressure, Pursuit implications |
| Senior leadership announcement | A1, B1 | Mandate, Pressure |
| FTS / Contracts Finder data | A4, B2, B3, C3 | Buying behaviour, Supplier landscape |
| Buyer-behaviour profile | A4, B3 | Buying behaviour, Supplier landscape |
| Tier 5 amend (CRM, account intel) | B1, C1, C2 | Supplier landscape, Pursuit implications |

---

## Versioning

This contract is versioned alongside the dossier schema. v3.0 contract
matches v3.0 schema. When the schema changes, update this contract before
publishing the schema change so consumers stay aligned.
