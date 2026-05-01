# Extraction Template — Commercial / Procurement Strategy

This template is loaded when a source is classified as
`commercial_strategy` or `procurement_strategy`.

A commercial strategy is the most direct buying-behaviour signal a
buyer publishes — it states their preferred routes to market,
framework usage, supplier-base direction, social-value weighting,
risk-transfer posture, and how they expect their commercial function
to behave. It anchors the dossier's `procurementBehaviour` and
`commercialAndRiskPosture` sections with first-party evidence rather
than inference. A strategy extracted as "they prefer frameworks" is
useless; the template forces capture of named frameworks, SME targets,
social-value weightings, payment terms, and the commercial function's
own capability investments.

---

## When to apply this template

Apply when the source is any of:

- A published commercial strategy or procurement strategy
- A supplier strategy or supplier-relationship strategy
- A commercial operating model document
- A contracting strategy or contracting playbook
- A category strategy with substantive commercial content
- An NHS commercial framework strategy or ICB commercial plan
- A devolved-government procurement strategy

Do not apply to:
- Cabinet Office Commercial Function pan-government guidance (general,
  not buyer-specific)
- One-page "how to do business with us" pages (no strategic content)
- Standalone framework user agreements

---

## Extraction depth requirement

Commercial strategies are typically 20–60 pages. Deep mode requires
capture of every named framework preference, SME / VCSE target,
social-value weighting framework, contracting model preference, and
named commercial-function investment. Skip standard procurement-act
boilerplate.

---

## Template schema

```json
{
  "extractionType": "commercial_strategy",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact title",
    "buyerName": "string",
    "publicationDate": "ISO 8601",
    "periodCovered": "string — e.g. 'FY26-27 to FY28-29'",
    "approvingAuthority": "string — Commercial Director, Permanent Secretary, board",
    "supersedes": "string or null",
    "totalPages": "number",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "headlinePrinciples": {
    "statedPrinciples": ["string — direct extracts of the commercial principles asserted"],
    "topPriorities": ["string — explicit top-N priorities for the commercial function"],
    "rejectedPostures": ["string — explicitly rejected behaviours (e.g. 'no race to the bottom on price', 'no exploitative subcontracting')"]
  },

  "marketEngagementApproach": {
    "preferredEngagementModels": ["string — early-market engagement, supplier days, soft-market testing, dialogue, innovation partnerships, etc."],
    "publishedPipelineCommitment": "string or null — frequency, level of detail, lead time",
    "smeAndVcseEngagement": "string — strategy for engaging smaller and voluntary-sector suppliers",
    "supplierFeedbackMechanisms": ["string — feedback portals, supplier panels, post-bid debriefs"]
  },

  "preferredRoutesToMarket": {
    "frameworkPreference": "string — narrative of framework reliance (e.g. 'CCS-first', 'mixed CCS / open competition', 'sector-specific frameworks first')",
    "namedFrameworks": [
      {
        "frameworkName": "string — e.g. 'CCS RM6263 G-Cloud', 'CCS RM6188 Big Data and Analytics'",
        "scopeUse": "string — what they use it for",
        "preferredUseMode": "direct-award | further-competition | both | unclear"
      }
    ],
    "openCompetitionPosture": "string — when they go to open FTS competition vs framework call-off",
    "dpsAndDynamicMarketsPosture": "string or null — appetite for DPS, dynamic markets, innovation marketplaces"
  },

  "supplierBaseStrategy": {
    "supplierBaseDirection": "consolidate | broaden | mixed | unstated",
    "namedSupplierConcentrationConcerns": ["string — categories or contracts where concentration is acknowledged"],
    "smeSpendTarget": "string or null — explicit % or value target",
    "vcseSpendTarget": "string or null",
    "primeAndSubcontractorExpectations": "string or null — flow-down, prompt-payment expectations to subcontractors",
    "supplierRelationshipTiers": ["string — strategic / key / transactional tiering if defined"]
  },

  "socialValueAndEsg": {
    "evaluationWeighting": "string — explicit weighting (e.g. '10% minimum on PPN 06/20 themes')",
    "preferredThemes": ["string — covid recovery, jobs and skills, fighting climate change, equal opportunity, wellbeing"],
    "esgRequirements": ["string — net-zero alignment, modern slavery, supply-chain transparency"],
    "carbonReductionRequirements": "string or null — Carbon Reduction Plan PPN, scope-3 expectations"
  },

  "contractingPosture": {
    "preferredContractTypes": ["string — fixed-price, time-and-materials, outcome-based, gain-share, framework call-off"],
    "outcomeBasedAppetite": "string — high | medium | low | unstated, with rationale",
    "riskAllocationFraming": "string — risk transfer posture, balanced-risk language, exclusions",
    "paymentTermsCommitment": "string or null — Prompt Payment Code stance, days target, supplier payment KPIs",
    "ipAndDataPosture": "string or null — IP retention, data ownership, exit clauses",
    "exitAndContinuityPosture": "string or null — exit management, transition obligations, dual-running"
  },

  "innovationAndCommercialReform": {
    "innovationProcurementCommitment": "string or null — % of spend, named programmes",
    "namedInnovationVehicles": ["string — DASA, Defence Innovation Fund, GovTech Catalyst, etc."],
    "commercialReformProgrammes": ["string — function-modernisation programmes"],
    "digitalProcurementInvestments": ["string — atamis, Bravo, internal e-procurement upgrades"]
  },

  "commercialFunctionCapability": {
    "headcountAndStructure": "string or null — function size and shape",
    "namedSeniorRoles": [
      {
        "name": "string",
        "role": "string — Commercial Director, CCO, Director of Procurement",
        "background": "string or null",
        "isDecisionMaker": "boolean"
      }
    ],
    "professionalAccreditation": "string or null — CIPS, GCO standards",
    "capabilityInvestmentProgrammes": ["string"]
  },

  "spendCategorisation": [
    {
      "category": "string — e.g. 'Digital and Technology', 'Professional Services', 'Estates'",
      "annualValue": "string or null",
      "strategicImportance": "critical | major | moderate | minor | unstated",
      "directionalSignal": "growing | stable | reducing | restructuring | unclear"
    }
  ],

  "languageAndFraming": {
    "preferredTerminology": ["string"],
    "policyFrames": ["string — value-for-money, fairness, social value, modernisation, etc."],
    "prohibitedOrAvoidedLanguage": ["string"]
  },

  "publicCommitments": [
    {
      "statement": "string — direct quote",
      "speaker": "string — typically Commercial Director or Permanent Secretary",
      "topic": "string"
    }
  ],

  "pursuitImplications": [
    {
      "implication": "string — buyer-derived, bidder-neutral",
      "category": "stance | language | evidence | commercial | engagement | risk-management | timing | structural",
      "rationale": "string"
    }
  ],

  "dossierMappings": [
    {
      "extractedPath": "string",
      "mapsToDossierField": "string",
      "operation": "extend | replace | upgrade",
      "lens": "mandate | pressure | money | buying-behaviour | risk-posture | supplier-landscape | pursuit-implications",
      "answersFrameworkQuestions": ["string"],
      "closesActionIds": ["string or null"]
    }
  ],

  "extractionQualityCheck": {
    "fullRead": "boolean",
    "namedFrameworksCaptured": "number",
    "supplierBaseDirectionCaptured": "boolean",
    "socialValueWeightingCaptured": "boolean",
    "contractTypePostureCaptured": "boolean",
    "spendCategoriesCaptured": "number",
    "unextractedSections": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `headlinePrinciples` | `procurementBehaviour.summaryNarrative` | buying-behaviour | upgrade (commercial strategy is authoritative on procurement behaviour) |
| `marketEngagementApproach.preferredEngagementModels[]` | `procurementBehaviour.preferredRoutes` | buying-behaviour | extend |
| `marketEngagementApproach.publishedPipelineCommitment` | `procurementBehaviour.summaryNarrative` | buying-behaviour | extend |
| `preferredRoutesToMarket.frameworkPreference` | `procurementBehaviour.frameworkUsage` | buying-behaviour | replace (most authoritative) |
| `preferredRoutesToMarket.namedFrameworks[]` | `procurementBehaviour.frameworkUsage` | buying-behaviour | extend |
| `preferredRoutesToMarket.openCompetitionPosture` | `procurementBehaviour.preferredRoutes` | buying-behaviour | extend |
| `supplierBaseStrategy.supplierBaseDirection` | `supplierEcosystem.summaryNarrative` | supplier-landscape | upgrade |
| `supplierBaseStrategy.smeSpendTarget` + `vcseSpendTarget` | `cultureAndPreferences.socialValueAndESG` | risk-posture | extend |
| `supplierBaseStrategy.namedSupplierConcentrationConcerns[]` | `supplierEcosystem.supplierConcentration` | supplier-landscape | extend |
| `socialValueAndEsg.evaluationWeighting` | `cultureAndPreferences.socialValueAndESG` | risk-posture | replace (most authoritative) |
| `socialValueAndEsg.preferredThemes[]` | `cultureAndPreferences.socialValueAndESG` | risk-posture | extend |
| `socialValueAndEsg.carbonReductionRequirements` | `cultureAndPreferences.socialValueAndESG` | risk-posture | extend |
| `contractingPosture.preferredContractTypes[]` | `procurementBehaviour.typicalContractLength` and `commercialAndRiskPosture.affordabilitySensitivity` | buying-behaviour, money | extend |
| `contractingPosture.outcomeBasedAppetite` | `procurementBehaviour.innovationVsProven` | buying-behaviour | extend |
| `contractingPosture.riskAllocationFraming` | `commercialAndRiskPosture.riskTransferPosture` | risk-posture | upgrade |
| `contractingPosture.paymentTermsCommitment` | `commercialAndRiskPosture.affordabilitySensitivity` (signal of supplier-base health) | money | extend |
| `contractingPosture.exitAndContinuityPosture` | `commercialAndRiskPosture.mobilisationSensitivity` | risk-posture | extend |
| `innovationAndCommercialReform.innovationProcurementCommitment` | `procurementBehaviour.innovationVsProven` | buying-behaviour | extend |
| `commercialFunctionCapability.namedSeniorRoles[]` (decisionMakers) | `decisionUnitAssumptions.perRoleInterests.commercial` | buying-behaviour | upgrade |
| `spendCategorisation[]` | `procurementBehaviour.categoryConcentration` | buying-behaviour | extend |
| `languageAndFraming` | `cultureAndPreferences.languageAndFraming` | risk-posture | extend |
| `publicCommitments[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `fullRead: false` in deep mode for a strategy >20 pages.
2. `preferredRoutesToMarket.namedFrameworks` empty — every UK public-
   sector commercial strategy names at least one framework preference.
3. `supplierBaseStrategy.supplierBaseDirection` is `unstated` AND
   `namedSupplierConcentrationConcerns` empty AND no SME / VCSE target —
   commercial strategies always take a directional position on
   supplier-base shape.
4. `socialValueAndEsg.evaluationWeighting` is null AND no preferred
   themes — contemporary UK procurement strategies always reference PPN
   06/20, the Procurement Act regime, or local social-value frameworks.
5. `contractingPosture.preferredContractTypes` empty — commercial
   strategies always state contract-type preferences.
6. `pursuitImplications[]` empty — every commercial strategy carries
   bidder-relevant implications. At minimum: framework preference gates
   route eligibility; SME spend target reshapes prime-vs-subcontractor
   bid structuring; risk-allocation framing dictates response on risk
   schedules; outcome-based appetite gates pricing-model choice.
7. `dossierMappings` does not include the `pursuitImplications` mapping.

---

## Worked example (illustrative)

For a hypothetical "Home Office Commercial Strategy 2026–2029"
extraction:

```
headlinePrinciples:
  statedPrinciples:
    - "Commercial decisions made closer to delivery, with category-led specialists embedded in business units"
    - "Innovation procurement is a default tool, not an exception"
    - "Supplier diversity is a delivery-resilience lever, not a compliance task"
preferredRoutesToMarket:
  frameworkPreference: "CCS-first for commodity categories; sector-specific frameworks for migration and digital identity; open FTS for novel scope"
  namedFrameworks:
    - { frameworkName: "CCS RM6263 G-Cloud 14", scopeUse: "Cloud and platform services", preferredUseMode: "further-competition" }
    - { frameworkName: "CCS RM6263 Big Data and Analytics", scopeUse: "Data engineering, analytics platforms", preferredUseMode: "further-competition" }
    - { frameworkName: "Home Office Justice and Migration DPS", scopeUse: "Specialist migration delivery services", preferredUseMode: "further-competition" }
supplierBaseStrategy:
  supplierBaseDirection: "broaden"
  namedSupplierConcentrationConcerns: ["Border systems", "Visa application processing"]
  smeSpendTarget: "33% direct or via SME-led prime by FY28-29"
  vcseSpendTarget: "5% on community-impact migration support services"
socialValueAndEsg:
  evaluationWeighting: "10% minimum on PPN 06/20 themes; 15% on category-relevant themes for non-commodity procurements"
  preferredThemes: ["jobs and skills (priority)", "fighting climate change", "wellbeing"]
  carbonReductionRequirements: "PPN 06/21 Carbon Reduction Plan mandatory; scope-3 disclosure expected on contracts >£25m"
contractingPosture:
  preferredContractTypes: ["outcome-based for service delivery", "fixed-price with consumption layer for cloud/platform", "gain-share for fraud-prevention services"]
  outcomeBasedAppetite: "high — particularly on enforcement, returns, and intelligence"
  riskAllocationFraming: "balanced — appetite for genuine risk-sharing on innovation; rejects unlimited liability"
  paymentTermsCommitment: "30-day to suppliers, 30-day flow-down to subcontractors mandatory"
  exitAndContinuityPosture: "12-month exit window minimum on strategic services; right-to-data-extract before termination"
spendCategorisation[0]:
  category: "Digital and Technology"
  annualValue: "~£1.2bn"
  strategicImportance: "critical"
  directionalSignal: "restructuring"
pursuitImplications[0]:
  implication: "Outcome-based pricing models will be preferred for enforcement and intelligence services;
    bid responses defaulting to time-and-materials face structural disadvantage."
  category: "commercial"
  rationale: "Outcome-based appetite explicitly rated 'high' in named categories."
pursuitImplications[1]:
  implication: "Prime bidders without credible SME / VCSE flow-through structures will fail social-value gating;
    expect explicit SME spend share to be evaluated and audited."
  category: "structural"
  rationale: "33% SME spend target with audit / supplier-feedback mechanism named."
pursuitImplications[2]:
  implication: "Carbon Reduction Plan must be in place at bid time on contracts >£5m; scope-3 disclosure
    required on >£25m. Bidders without a published, audited CRP face disqualification risk."
  category: "evidence"
  rationale: "Carbon reduction explicitly mandatory per PPN 06/21, scope-3 on large contracts named."
```
