# Extraction Template — Workforce / People Strategy

This template is loaded when a source is classified as
`workforce_strategy` or `people_plan`.

A workforce strategy reveals the buyer's posture on insourcing vs
outsourcing, contractor caps, capability gaps, and where they expect
to lean on suppliers vs grow in-house. It also tells the bidder which
workforce-related policy frames the buyer cares about (apprenticeships,
diversity, regional employment, social value via local hire). A
strategy extracted as "headcount up by 5%" is useless; the template
forces capture of the substance — capability gaps, named programmes,
DDaT-specific arrangements, contractor-cap signals, reskilling
investments.

---

## When to apply this template

Apply when the source is any of:

- A published workforce strategy or people plan
- A capability strategy (especially DDaT capability strategy)
- A talent strategy or talent pipeline strategy
- An NHS workforce strategy or long-term workforce plan
- A civil service workforce plan
- A skills strategy specific to a department or arm's-length body
- A reorganisation document with substantive workforce content

Do not apply to generic HR policy documents, equality and diversity
statements, or remuneration disclosures (those belong to the
annual-report template).

---

## Extraction depth requirement

Workforce strategies are typically 20–80 pages. Deep mode requires
capture of FTE baselines and targets, capability gaps, named
programmes, contractor / temporary-resource posture, and supplier-
relevant signals (DDaT contractor caps, social-value commitments,
apprenticeship targets). Skip generic HR boilerplate.

---

## Template schema

```json
{
  "extractionType": "workforce_strategy",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact title",
    "buyerName": "string",
    "publicationDate": "ISO 8601",
    "periodCovered": "string — e.g. 'FY26-27 to FY28-29'",
    "approvingAuthority": "string — Permanent Secretary, Chief People Officer, Trust Board",
    "supersedes": "string or null",
    "totalPages": "number",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "scaleAndShape": {
    "totalHeadcountBaseline": "number or null",
    "totalHeadcountTarget": "number or null",
    "fteByYear": [
      { "year": "string", "fte": "number", "narrativeContext": "string or null" }
    ],
    "headcountTrajectory": "growth | stable | reduction | mixed | unstated",
    "geographicDistribution": "string or null — HQ, regional centres, hubs and spokes, fully distributed",
    "permanentVsContractorMix": "string or null — current ratio and target ratio if stated"
  },

  "capabilityGaps": [
    {
      "capabilityArea": "string — e.g. 'data engineering', 'product management', 'commercial leadership', 'fraud investigation'",
      "gapDescription": "string",
      "severity": "critical | significant | moderate | unclear",
      "plannedResponse": "hire | reskill | partner | outsource | platform | accept-gap"
    }
  ],

  "namedProgrammes": [
    {
      "programmeName": "string",
      "scopeSummary": "string — what the programme actually does (≥40 words)",
      "targetPopulation": "string — who it serves (e.g. 'all DDaT staff', 'Band 7 nurses', 'commercial function')",
      "budget": "string or null",
      "byWhen": "string or null",
      "supplierImplications": "string or null — opens / threatens specific supplier categories"
    }
  ],

  "contractorAndTemporaryResource": {
    "currentPosture": "string — narrative of current contractor reliance",
    "namedContractorCap": "string or null — explicit cap, e.g. 'reduce DDaT contractor spend by 30% by FY27-28'",
    "specificCategoriesAffected": ["string — categories where caps bite hardest"],
    "interimAndAgencyPosture": "string or null",
    "associatePoolStrategy": "string or null — talent pools, alumni programmes, surge capability"
  },

  "insourcingVsOutsourcing": {
    "directionalStance": "in-house-first | balanced | platform-led | partnership-first | outsourced-where-non-core | unstated",
    "namedFunctionsBeingInsourced": ["string"],
    "namedFunctionsBeingOutsourced": ["string"],
    "rationaleFraming": "string — capability building, cost, risk, control, mission focus"
  },

  "skillsAndDevelopment": {
    "investmentTotal": "string or null — total L&D budget or commitment",
    "namedAcademiesOrSchools": ["string — Government Skills, NHS Leadership Academy, internal academy"],
    "apprenticeshipTargets": "string or null — number, level, categories",
    "graduateTargets": "string or null",
    "reskillingProgrammes": ["string — internal mobility programmes"],
    "namedExternalProviders": ["string — suppliers explicitly named in the document"]
  },

  "diversityInclusionAndSocialValue": {
    "diversityCommitments": ["string"],
    "socialValueWorkforceCommitments": ["string — local hire, ex-offender, care leavers, reservists, etc."],
    "apprenticeshipLevyDirection": "string or null",
    "regionalDistributionTargets": ["string — Places for Growth, Levelling Up, regional hubs"]
  },

  "leadershipAndOrganisation": {
    "namedSeniorAppointments": ["string — Chief People Officer, Director of Capability, etc."],
    "structuralChanges": ["string — new directorates, hub creation, function consolidation"],
    "operatingModelImplications": "string or null"
  },

  "namedStakeholders": [
    {
      "name": "string",
      "role": "string",
      "responsibilityInStrategy": "string",
      "isDecisionMaker": "boolean"
    }
  ],

  "languageAndFraming": {
    "preferredTerminology": ["string"],
    "policyFrames": ["string — capability building, mission-led, productivity, modern employer, etc."],
    "prohibitedOrAvoidedLanguage": ["string"]
  },

  "publicCommitments": [
    {
      "statement": "string — direct quote",
      "speaker": "string",
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
    "capabilityGapsCaptured": "number",
    "namedProgrammesCaptured": "number",
    "contractorCapPostureCaptured": "boolean",
    "insourcingPostureCaptured": "boolean",
    "unextractedSections": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `scaleAndShape.totalHeadcountBaseline` + `totalHeadcountTarget` | `buyerSnapshot.headcount` | mandate | replace (workforce strategy is authoritative) |
| `scaleAndShape.headcountTrajectory` | `organisationContext.recentChanges` | mandate, pressure | extend |
| `capabilityGaps[]` | `commissioningContextHypotheses.operationalPainPoints` | pressure | extend |
| `capabilityGaps[]` (where plannedResponse is `outsource` or `partner`) | `procurementBehaviour.summaryNarrative` (forward direction signal) | buying-behaviour | extend |
| `namedProgrammes[]` | `strategicPriorities.majorProgrammes[]` (where strategic) | pressure | extend |
| `namedProgrammes[].supplierImplications` | `supplierEcosystem.summaryNarrative` (market refresh signal) | supplier-landscape | extend |
| `contractorAndTemporaryResource.namedContractorCap` | `commercialAndRiskPosture.affordabilitySensitivity` | money, risk-posture | extend |
| `contractorAndTemporaryResource.specificCategoriesAffected[]` | `procurementBehaviour.summaryNarrative` (likely demand reduction) | buying-behaviour | extend |
| `contractorAndTemporaryResource` (any cap signal) | `commissioningContextHypotheses.pressuresShapingSpend` | money, pressure | extend |
| `insourcingVsOutsourcing.directionalStance` | `procurementBehaviour.innovationVsProven` (not exact, but captures direction) and `supplierEcosystem.summaryNarrative` | buying-behaviour, supplier-landscape | upgrade |
| `insourcingVsOutsourcing.namedFunctionsBeingOutsourced[]` | `supplierEcosystem.marketRefreshAreas` | supplier-landscape | extend |
| `insourcingVsOutsourcing.namedFunctionsBeingInsourced[]` | `supplierEcosystem.summaryNarrative` (incumbent threat signal) | supplier-landscape | extend |
| `skillsAndDevelopment.namedExternalProviders[]` | `supplierEcosystem.incumbents[]` | supplier-landscape | extend |
| `diversityInclusionAndSocialValue.socialValueWorkforceCommitments[]` | `cultureAndPreferences.socialValueAndESG` | risk-posture | extend |
| `diversityInclusionAndSocialValue.regionalDistributionTargets[]` | `cultureAndPreferences.socialValueAndESG` | risk-posture | extend |
| `languageAndFraming` | `cultureAndPreferences.languageAndFraming` | risk-posture | extend |
| `namedStakeholders[]` (decisionMakers) | `decisionUnitAssumptions.perRoleInterests` (HR/people lens) | buying-behaviour | extend |
| `publicCommitments[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `fullRead: false` in deep mode for a strategy >20 pages.
2. `capabilityGaps` empty — every workforce strategy names gaps; an
   empty array indicates the gap-analysis chapter wasn't read.
3. `insourcingVsOutsourcing.directionalStance` is `unstated` AND no
   `namedFunctionsBeingInsourced` / `namedFunctionsBeingOutsourced` —
   contemporary UK public-sector workforce strategies always take a
   directional position.
4. `contractorAndTemporaryResource.currentPosture` empty when the
   document mentions DDaT, digital, or commercial workforce —
   contractor reliance is universally addressed in those contexts.
5. `pursuitImplications[]` empty — every workforce strategy carries
   bidder-relevant implications. At minimum: any insourcing direction
   threatens incumbent contracts in those functions; any contractor cap
   shifts demand structure; any named outsource direction opens
   addressable market.
6. `dossierMappings` does not include the `pursuitImplications` mapping.

---

## Worked example (illustrative)

For a hypothetical "Department for Education People Plan FY26-FY29"
extraction:

```
scaleAndShape:
  totalHeadcountBaseline: 7820
  totalHeadcountTarget: 7400
  headcountTrajectory: "reduction"
  permanentVsContractorMix: "Currently 88:12 perm:contractor across DDaT; target 95:5 by FY28-29"
capabilityGaps[0]:
  capabilityArea: "data engineering and data science"
  gapDescription: "Insufficient internal capacity to deliver National Pupil Database
    modernisation and DfE-wide data infrastructure ambitions"
  severity: "critical"
  plannedResponse: "hire"
capabilityGaps[1]:
  capabilityArea: "policy implementation delivery"
  gapDescription: "Gap between policy design and operational delivery has driven historical schedule slippage"
  severity: "significant"
  plannedResponse: "reskill"
namedProgrammes[0]:
  programmeName: "DDaT Insourcing Programme"
  scopeSummary: "Move 30% of currently outsourced DDaT services back in-house by FY28-29,
    prioritising data engineering, product management, and user research. Phased migration
    starting Q3 2026."
  budget: "£28m capital + £42m run by FY28-29"
  supplierImplications: "Major threat to incumbent DDaT prime suppliers; market refresh likely on framework recompete in FY27-28."
contractorAndTemporaryResource:
  namedContractorCap: "Reduce DDaT contractor day-rate spend by 40% by FY28-29"
  specificCategoriesAffected: ["digital delivery managers", "user research", "product owners", "delivery managers"]
insourcingVsOutsourcing:
  directionalStance: "in-house-first"
  namedFunctionsBeingInsourced: ["DDaT product and delivery", "user research", "data engineering"]
  namedFunctionsBeingOutsourced: ["niche specialist technical capabilities (cyber, AI ethics)"]
  rationaleFraming: "Capability building, value for money, control of strategic data assets"
diversityInclusionAndSocialValue:
  regionalDistributionTargets: ["Places for Growth: 40% of new roles outside London by FY28-29"]
pursuitImplications[0]:
  implication: "DDaT prime contracts face active displacement risk; recompete window
    likely in FY27-28 with significantly reduced scope or replaced by smaller specialist lots."
  category: "structural"
  rationale: "DDaT Insourcing Programme explicitly targets 30% reduction in outsourced DDaT services with budget allocated."
pursuitImplications[1]:
  implication: "Bid pricing must reflect aggressive contractor day-rate scrutiny;
    expect questions on ratecard reduction trajectory and rate-card cap commitments."
  category: "commercial"
  rationale: "Named contractor day-rate spend reduction target of 40% sets explicit price expectation."
```
