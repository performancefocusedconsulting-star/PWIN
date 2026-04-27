# Buyer Intelligence Dossier — Output Schema v2.2

This reference defines the complete JSON output schema, field rules, and
archetype taxonomy. Read this file when constructing the dossier JSON.

## Table of Contents

1. [Full schema structure](#full-schema-structure)
2. [Organisational archetype taxonomy](#organisational-archetype-taxonomy)
3. [Schema rules](#schema-rules)
4. [Organisation type enum](#organisation-type-enum)
5. [Buying readiness enum](#buying-readiness-enum)
6. [Change maturity sub-fields](#change-maturity-sub-fields)
7. [Linked assets structure](#linked-assets-structure)

---

## Full schema structure

Produce a single JSON object with these top-level keys:

```json
{
  "meta": {
    "buyerName": "string",
    "slug": "string — kebab-case identifier",
    "sector": "string",
    "generatedAt": "ISO 8601 datetime",
    "generatedBy": "Agent 2 Skill 2 v2.2",
    "version": "2.2 on first build; increment on refresh",
    "depthMode": "snapshot | standard | deep | snapshot-data-insufficient | <mode>-partial",
    "taxonomyVersion": "2.0",
    "sourcesSummary": "string — e.g. '12 sources, 6 web searches'",
    "refreshDue": "ISO 8601 date — 6 months from today or next reporting milestone",
    "refreshTriggers": [
      "new procurement in category",
      "leadership change",
      "annual report publication",
      "strategy refresh",
      "major controversy or audit event",
      "pursuit launched against this buyer"
    ],
    "versionLog": [{ "version": "string", "date": "ISO 8601", "mode": "build | refresh | inject | amend", "summary": "string" }],
    "prerequisitesPresentAt": {
      "version": "string — version this snapshot was taken at",
      "date": "ISO 8601 date",
      "required": {
        "buyerName": "boolean"
      },
      "preferred": {
        "ftsData": "boolean",
        "sectorBrief": "boolean"
      }
    },
    "degradedReason": "string or null — only set in degraded/partial mode"
  },

  "buyerSnapshot": {
    "legalName": "string",
    "parentBody": "string or null",
    "organisationType": "enum — see Organisation type enum below",
    "sector": "string",
    "subSector": "string or null",
    "geographicRemit": "string",
    "headcount": "number or null",
    "annualBudget": "string or null",
    "organisationalArchetype": {
      "value": "enum — see Archetype taxonomy below",
      "type": "inference",
      "confidence": "high | medium | low",
      "rationale": "string — explain the evidence chain",
      "sourceRefs": ["SRC-001"]
    },
    "executiveSummary": {
      "headline": "string — one-sentence decision-grade summary",
      "narrative": "string — 2-3 paragraph overview"
    },
    "keyRisks": ["string — top 3-5 risks for any pursuit against this buyer"]
  },

  "organisationContext": {
    "sectionConfidence": "high | medium | low | none",
    "mandate": "evidenced field",
    "operatingModel": "evidenced field",
    "organisationStructure": "evidenced field",
    "keyBusinessUnits": ["string or evidenced field"],
    "seniorLeadership": [{ "name": "string", "role": "string", "since": "string or null" }],
    "fundingModel": "evidenced field",
    "recentChanges": "evidenced field — include predecessor/successor bodies, MoG changes"
  },

  "strategicPriorities": {
    "sectionConfidence": "high | medium | low | none",
    "summaryNarrative": "string",
    "publishedStrategyThemes": ["evidenced field"],
    "majorProgrammes": [{ "name": "string", "status": "string", "value": "string or null" }],
    "regulatoryPressures": ["evidenced field"],
    "politicalPressures": ["evidenced field"],
    "fiscalPressures": ["evidenced field"],
    "servicePerformancePressures": ["evidenced field"],
    "publicStatementsOfIntent": ["evidenced field"]
  },

  "commissioningContextHypotheses": {
    "sectionConfidence": "high | medium | low | none",
    "sectionCaveat": "These are hypotheses derived from available evidence. They require validation by the pursuit team.",
    "driversOfExternalBuying": ["evidenced field — type must be inference"],
    "pressuresShapingSpend": ["evidenced field — type must be inference"],
    "operationalPainPoints": ["evidenced field — type must be inference"],
    "outcomesSought": ["evidenced field — type must be inference"],
    "consequencesOfInaction": ["evidenced field — type must be inference"],
    "commissioningCycleStage": "evidenced field — type must be inference",
    "approvalsPending": "evidenced field — type must be inference",
    "marketEngagementLikelihood": "evidenced field — type must be inference",
    "buyingReadiness": "evidenced field — enum value, type must be inference",
    "timelineRisks": ["evidenced field — type must be inference"]
  },

  "procurementBehaviour": {
    "sectionConfidence": "high | medium | low | none",
    "summaryNarrative": "string",
    "totalAwards": "number",
    "totalValue": "string — e.g. '£142m'",
    "dataWindow": "string — e.g. '2020-2026'",
    "preferredRoutes": ["string — e.g. 'CCS framework call-off', 'open procedure'"],
    "frameworkUsage": ["string — framework names and lot references"],
    "sharedServiceArrangements": "string or null — e.g. 'Procures IT through NHS SBS; professional services direct'",
    "typicalContractLength": "string — e.g. '3+1+1 years'",
    "typicalContractValue": "string — e.g. '£2m-£10m'",
    "categoryConcentration": "evidenced field",
    "innovationVsProven": "evidenced field",
    "priceVsQualityBias": "evidenced field",
    "renewalPatterns": "evidenced field"
  },

  "decisionUnitAssumptions": {
    "sectionConfidence": "high | medium | low | none",
    "sectionCaveat": "Inferred from published structures and procurement patterns. Requires pursuit-team validation.",
    "businessOwnerRoles": ["evidenced field — type must be inference"],
    "commercialRoles": ["evidenced field — type must be inference"],
    "technicalStakeholders": ["evidenced field — type must be inference"],
    "financeAssuranceRoles": ["evidenced field — type must be inference"],
    "evaluatorGroups": ["evidenced field — type must be inference"],
    "intelligenceGaps": ["string"]
  },

  "cultureAndPreferences": {
    "sectionConfidence": "high | medium | low | none",
    "decisionMakingFormality": "evidenced field",
    "governanceIntensity": "evidenced field",
    "riskTolerance": "evidenced field",
    "evidencePreferences": "evidenced field",
    "supplierInteractionStyle": "evidenced field",
    "presentationStyle": "evidenced field",
    "socialValueAndESG": "evidenced field — PPN 06/20 approach, net zero commitments, SME spend targets, community benefit expectations",
    "changeMaturity": "object — see Change maturity sub-fields below"
  },

  "commercialAndRiskPosture": {
    "sectionConfidence": "high | medium | low | none",
    "affordabilitySensitivity": "evidenced field",
    "riskTransferPosture": "evidenced field",
    "contractualCaution": "evidenced field",
    "cyberDataSensitivity": "evidenced field",
    "mobilisationSensitivity": "evidenced field",
    "auditFoiExposure": "evidenced field",
    "securityClearanceRequirements": "evidenced field — SC/DV/BPSS obligations, relevant for Defence, Justice, and intelligence-community buyers"
  },

  "supplierEcosystem": {
    "sectionConfidence": "high | medium | low | none",
    "summaryNarrative": "string",
    "incumbents": [
      {
        "supplierName": "string",
        "serviceLines": ["string — from 13-category taxonomy"],
        "contractCount": "number",
        "totalValue": "string",
        "longestRelationship": "string — e.g. 'since 2018'",
        "strategicImportance": "critical | major | moderate | minor",
        "recentActivity": "growing | stable | thinning",
        "entrenchmentIndicators": {
          "systems": "string or null",
          "tupeWorkforce": "string or null",
          "data": "string or null",
          "relationships": "string or null"
        },
        "dossierRef": "string or null — asset ID of supplier dossier if one exists"
      }
    ],
    "adjacentSuppliers": ["string"],
    "supplierConcentration": "evidenced field",
    "switchingEvidence": "evidenced field",
    "marketRefreshAreas": ["string"]
  },

  "relationshipHistory": {
    "sectionConfidence": "high | medium | low | none",
    "tierNote": "string — e.g. 'No Tier 4 data provided...'",
    "priorContracts": [
      { "contractName": "string", "value": "string", "period": "string", "status": "active | closed" }
    ],
    "activeProgrammes": ["string"],
    "pastBids": [
      { "opportunityName": "string", "date": "string", "outcome": "win | loss | no-bid", "feedbackReceived": "string or null" }
    ],
    "executiveRelationships": ["string"],
    "knownAdvocates": ["string"],
    "knownBlockers": ["string"],
    "intelGaps": ["string"]
  },

  "risksAndSensitivities": {
    "sectionConfidence": "high | medium | low | none",
    "summaryNarrative": "string — decision-grade summary of risk landscape",
    "procurementControversies": ["evidenced field"],
    "programmeFailures": ["evidenced field"],
    "auditFindings": ["evidenced field"],
    "mediaScrutiny": ["evidenced field"],
    "publicSensitivities": ["evidenced field"],
    "positioningSensitivities": ["evidenced field"]
  },

  "sourceRegister": {
    "sources": [
      {
        "sourceId": "SRC-001",
        "sourceName": "string — e.g. 'HMRC Annual Report 2024-25'",
        "sourceType": "annual_report | strategy_document | board_paper | procurement_notice | audit_report | media | parliamentary | framework_data | internal | other",
        "publicationDate": "ISO 8601 or null",
        "accessDate": "ISO 8601",
        "reliability": "Tier 1 | Tier 2 | Tier 3 | Tier 4",
        "sectionsSupported": ["string — section names this source informs"],
        "url": "string or null"
      }
    ],
    "gaps": ["string — areas where no source was found"],
    "staleFields": ["string — fields relying on sources older than 3 years"],
    "lowConfidenceInferences": ["string — inferences with low confidence that need validation"]
  },

  "computedScores": {
    "buyerRiskAversionScore": null,
    "changeMaturityScore": null,
    "innovationAppetiteScore": null,
    "incumbencyStrengthScore": null,
    "commercialSensitivityScore": null,
    "relationshipStrengthScore": null,
    "winDifficultyScore": null
  },

  "linkedAssets": {
    "supplierDossiers": [{ "assetId": "string", "assetType": "supplier-dossier", "assetName": "string", "generatedAt": "ISO 8601" }],
    "sectorBriefs": [{ "assetId": "string", "assetType": "sector-brief", "assetName": "string", "generatedAt": "ISO 8601" }],
    "pipelineScans": [{ "assetId": "string", "assetType": "pipeline-scan", "assetName": "string", "generatedAt": "ISO 8601" }]
  },

  "changeSummary": [
    {
      "section": "string — section name",
      "field": "string — field name",
      "previousValue": "string — summary of old value",
      "newValue": "string — summary of new value",
      "changeReason": "string — why this changed"
    }
  ]
}
```

**Note:** `changeSummary` is populated ONLY on refresh runs. Set to null on
first-build runs.

---

## Organisational archetype taxonomy

The `buyerSnapshot.organisationalArchetype` field uses the per-field evidence
wrapper. The value must be one of the following. This describes the
**organisation's dominant buying behaviour** — not a specific opportunity.

| Archetype | Meaning | Pursuit implication |
|---|---|---|
| `strategic_central_commissioner` | Mature commercial centre, strong governance, expects sophisticated outcome-led propositions | High bar for quality; needs strategic narrative |
| `framework_first_operator` | Buys through accessible routes; speed and compliant fit matter more than visionary repositioning | Match framework requirements precisely; don't oversell |
| `devolved_capacity_constrained` | Limited commercial bandwidth; clarity, low-friction compliance, and implementation confidence matter most | Make it easy to buy; reduce burden on buyer team |
| `programme_led_transformer` | Driven by transformation agenda; open to flexible procedure, dialogue, and solution shaping | Co-creation opportunity; invest in pre-market engagement |
| `incumbent_locked_risk_averse` | Market formally open but practically difficult to unseat due to operational, data, security, or TUPE lock-in | Understand lock-in mechanism; find the lever |
| `politically_sensitive_high_scrutiny` | Procurement shaped by controversy, citizen impact, ministerial attention, or audit exposure | Risk-proof the proposition; anticipate scrutiny |
| `compliance_procurement_machine` | Highly process-led, evaluation-led, defensible; less interested in narrative, more in audit-proof quality | Score maximisation; follow the evaluation criteria exactly |

---

## Schema rules

- `meta.generatedBy`: `"Agent 2 Skill 2 v2.2"`
- `meta.taxonomyVersion`: `"2.0"`
- `meta.version`: `"2.2"` on first build; increment on refresh
- All `computedScores` values: `null` — the renderer derives scores from
  evidence fields
- Use ISO 8601 dates throughout
- Use `null` for unknown/unavailable fields, not empty strings
- Source register IDs: sequential — SRC-001, SRC-002, etc.
- `meta.refreshDue`: set to 6 months from today, or the buyer's next known
  reporting milestone if earlier. Do not leave null on first build.

---

## Organisation type enum

`organisationType` must be one of:

| Value | Covers |
|---|---|
| `department` | Central government departments (e.g., HMRC, Home Office) |
| `agency` | Executive agencies (e.g., DVLA, Companies House) |
| `ndpb` | Non-departmental public bodies |
| `nhs_trust` | NHS trusts (acute, mental health, community, ambulance) |
| `nhs_icb` | Integrated care boards |
| `local_authority` | County, district, unitary, metropolitan, London borough councils |
| `devolved` | Welsh Government, Scottish Government, NI Executive and their bodies |
| `mod` | Ministry of Defence and defence agencies (DE&S, Dstl, etc.) |
| `regulator` | Regulators (Ofcom, Ofgem, CQC, etc.) |
| `other` | Anything not covered above |

---

## Buying readiness enum

`buyingReadiness` must be one of:

- `pre-pipeline` — no evidence of procurement intent
- `pipeline-identified` — procurement appears in published pipeline
- `pre-market-engagement` — signals of upcoming market engagement
- `post-market-engagement` — market engagement completed, procurement expected
- `procurement-live` — active procurement in progress
- `awarded` — contract recently awarded

---

## Change maturity sub-fields

The `cultureAndPreferences.changeMaturity` object contains six sub-fields.
Each uses the per-field evidence wrapper. Each value must be one of: `high`,
`medium`, `low`, `unknown`.

| Sub-field | Assess from |
|---|---|
| `deliveryMaturity` | Programme delivery record, audit findings on delivery |
| `digitalMaturity` | Transformation investment, published digital roadmaps |
| `governanceMaturity` | Audit findings, assurance structure, governance framework |
| `supplierManagementMaturity` | Contract management patterns, renegotiation behaviour |
| `coCreationTolerance` | Market engagement style, dialogue procedure usage |
| `phaseOrAgileCapability` | Evidence of phased or iterative delivery in prior contracts |

---

## Linked assets structure

Each array in `linkedAssets` contains asset pointer objects:

```json
{
  "assetId": "string — platform asset identifier",
  "assetType": "supplier-dossier | sector-brief | pipeline-scan",
  "assetName": "string — human-readable name",
  "generatedAt": "ISO 8601 datetime"
}
```

Use empty arrays `[]` if no linked assets exist. Do not use `null` for these
arrays.
