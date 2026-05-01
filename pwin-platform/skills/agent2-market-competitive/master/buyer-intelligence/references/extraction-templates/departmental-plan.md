# Extraction Template — Departmental Plan

This template is loaded when a source is classified as
`outcome_delivery_plan`, `single_departmental_plan`, or `corporate_plan`.

Departmental plans are the buyer's own statement of what they intend to
achieve — the mandate side of the dossier. They name the priority
outcomes, the indicators by which performance is measured, the major
delivery vehicles, and the trade-offs the leadership has accepted. A
plan extracted as "the department has priorities X, Y, Z" is useless;
the template forces capture of the actual outcome statements,
indicators, delivery vehicles, and stated trade-offs.

---

## When to apply this template

Apply when the source is any of:

- An Outcome Delivery Plan (UK central government, post-2021 format)
- A Single Departmental Plan (UK central government, 2015–2020 format)
- A Corporate Plan (executive agency, NDPB, regulator)
- A devolved government's Programme for Government (Wales, Scotland)
  or Programme for Government commitments document (Northern Ireland)
- An NHS trust strategic plan or ICB integrated care strategy
- A local authority Council Plan or corporate strategy

For digital, transformation, workforce, or commercial sub-strategies,
do not use this template — use the matching topic-specific template.
For Annual Reports, use the annual-report template (which captures
prior-year performance against the plan).

---

## Extraction depth requirement

Plans are typically 20–80 pages. Deep mode requires capturing every
named priority outcome, indicator, and major delivery vehicle. Skip
boilerplate (mission statements, generic ministerial forewords,
stakeholder-engagement appendices) and focus on the substantive plan
content.

---

## Template schema

```json
{
  "extractionType": "departmental_plan",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact title",
    "buyerName": "string",
    "planType": "outcome-delivery-plan | single-departmental-plan | corporate-plan | programme-for-government | trust-strategy | council-plan | other",
    "periodCovered": "string — e.g. 'FY25-26 to FY28-29'",
    "publicationDate": "ISO 8601",
    "approvingAuthority": "string — Permanent Secretary, Chief Executive, Council Leader, board",
    "supersedes": "string or null — predecessor plan",
    "totalPages": "number",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "strategicObjectives": [
    {
      "objectiveId": "string — e.g. 'Priority 1', 'Outcome A'",
      "objectiveStatement": "string — exact statement (≥30 words; if shorter, this is a slogan and the plan needs deeper read)",
      "rationale": "string — why this is a priority (legislative driver, manifesto, fiscal pressure, prior performance gap)",
      "linkedToCrossGovOutcome": "string or null — links to broader cross-government priorities if cited"
    }
  ],

  "priorityOutcomes": [
    {
      "underObjective": "string — objectiveId from above",
      "outcomeStatement": "string — what success looks like in concrete terms",
      "indicators": [
        {
          "indicatorName": "string",
          "currentBaseline": "string or null",
          "target": "string",
          "byWhen": "string",
          "stretchOrCommitted": "committed | stretch | aspirational | unclear"
        }
      ],
      "deliveryVehicles": [
        {
          "vehicleName": "string — programme, partnership, function, in-house team",
          "vehicleType": "in-house-programme | major-programme | partnership | regulatory-action | grant-scheme | commissioned-service | shared-service | other",
          "supplierImplications": "string — opens / threatens / sustains specific supplier categories"
        }
      ],
      "dependencies": ["string — internal or external dependencies"]
    }
  ],

  "majorProgrammes": [
    {
      "programmeName": "string",
      "linkedOutcomes": ["string — outcomeStatement(s) it serves"],
      "scopeSummary": "string — what the programme actually does (≥40 words)",
      "budget": "string or null",
      "sro": "string or null",
      "deliveryWindow": "string or null",
      "currentStatus": "early | in-flight | delivery-phase | mobilising | unstated"
    }
  ],

  "resourceAllocation": {
    "headlineSplit": "string or null — narrative split across objectives if disclosed",
    "ringFencedSpend": ["string — ring-fenced commitments"],
    "tradeOffsAcknowledged": ["string — explicit trade-offs the plan accepts (deprioritised areas, deferred work)"]
  },

  "performanceFramework": {
    "reportingCadence": "string or null — annual, quarterly, monthly",
    "publishedDashboards": ["string — named dashboards or transparency products"],
    "scrutinyArrangements": ["string — IPA gates, board oversight, select committee, audit"]
  },

  "risksAcknowledged": [
    {
      "riskName": "string",
      "category": "delivery | demand | financial | political | reform | workforce | supplier | technology | data | other",
      "mitigations": "string or null"
    }
  ],

  "languageAndFraming": {
    "preferredTerminology": ["string — distinctive terms used repeatedly"],
    "policyFrames": ["string — value-for-money, mission-led, place-based, etc."],
    "absentLanguage": ["string — terms a comparable plan elsewhere uses but this one notably avoids"]
  },

  "namedStakeholders": [
    {
      "name": "string",
      "role": "string",
      "responsibilityInPlan": "string",
      "isDecisionMaker": "boolean"
    }
  ],

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
    "objectivesCaptured": "number — must equal count in document",
    "outcomesCaptured": "number",
    "indicatorsCaptured": "number",
    "majorProgrammesCaptured": "number",
    "tradeOffsCaptured": "number",
    "unextractedSections": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `strategicObjectives[].objectiveStatement` | `strategicPriorities.summaryNarrative` (synthesised) and `strategicPriorities.publishedStrategyThemes` | mandate, pressure | extend |
| `priorityOutcomes[].outcomeStatement` | `commissioningContextHypotheses.outcomesSought` | pressure, mandate | extend |
| `priorityOutcomes[].indicators[]` | `strategicPriorities.publishedStrategyThemes` (with quantified targets) | pressure | extend |
| `priorityOutcomes[].deliveryVehicles[]` | `procurementBehaviour.summaryNarrative` (where commissioned externally) | buying-behaviour | extend |
| `priorityOutcomes[].deliveryVehicles[].supplierImplications` | `supplierEcosystem.summaryNarrative` (forward direction signal) | supplier-landscape | extend |
| `majorProgrammes[]` | `strategicPriorities.majorProgrammes[]` | pressure, money | extend or upgrade |
| `resourceAllocation.tradeOffsAcknowledged[]` | `commissioningContextHypotheses.spendClassification` (signals discretionary cuts) | money | extend |
| `resourceAllocation.ringFencedSpend[]` | `commissioningContextHypotheses.pressuresShapingSpend` | money, pressure | extend |
| `performanceFramework.scrutinyArrangements[]` | `commercialAndRiskPosture.auditFoiExposure` | risk-posture | extend |
| `risksAcknowledged[]` | `risksAndSensitivities.summaryNarrative` (synthesised) | risk-posture | extend |
| `languageAndFraming` | `cultureAndPreferences.languageAndFraming` | risk-posture | extend |
| `namedStakeholders[]` (decisionMakers) | `decisionUnitAssumptions.perRoleInterests` | buying-behaviour | extend |
| `publicCommitments[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `fullRead: false` in deep mode for a plan >30 pages.
2. `strategicObjectives` is empty — every plan has named objectives.
3. `priorityOutcomes` is empty — plans always cascade objectives into
   outcomes (or equivalent terminology like "deliverables", "missions").
4. `priorityOutcomes[].indicators` is empty across the entire plan —
   contemporary UK government plans always include performance
   indicators, even if light.
5. `majorProgrammes` is empty AND the document references programmes
   in narrative — the programmes were named but not extracted.
6. Any `objectiveStatement` is under 30 words. That is the slogan
   threshold. Plans express objectives in substance, not headlines.
7. `pursuitImplications[]` is empty — every plan carries implications.
   At minimum: prioritised areas attract competition, deprioritised
   areas suggest descope risk; named delivery vehicles signal supplier
   strategy direction.

---

## Worked example (illustrative)

For a hypothetical "Department for Work and Pensions Outcome Delivery
Plan FY25-26 to FY28-29" extraction:

```
strategicObjectives[0]:
  objectiveId: "Priority 1"
  objectiveStatement: "Maximise employment by helping more people into well-paid,
    rewarding work, supporting employers to recruit and retain talent, and
    breaking down barriers to opportunity for working-age people across the UK."
  rationale: "Manifesto commitment on employment activation; fiscal pressure to
    reduce working-age inactivity; record-high economic-inactivity figures."
priorityOutcomes[0]:
  underObjective: "Priority 1"
  outcomeStatement: "Increase the employment rate among working-age adults from
    74.8% (Q4 2024 baseline) to 80% by Q4 2028."
  indicators:
    - { indicatorName: "Working-age employment rate", currentBaseline: "74.8%", target: "80%", byWhen: "Q4 2028", stretchOrCommitted: "stretch" }
    - { indicatorName: "Health-related inactivity flow into work", currentBaseline: "32k/quarter", target: "55k/quarter", byWhen: "FY27-28", stretchOrCommitted: "committed" }
  deliveryVehicles:
    - { vehicleName: "WorkWell pilots scaled to national programme", vehicleType: "commissioned-service", supplierImplications: "Major opportunity for employability and occupational-health providers; threat to national prime contractor model if framework refreshed" }
majorProgrammes[0]:
  programmeName: "Health Transformation Programme"
  linkedOutcomes: ["health-related inactivity flow into work"]
  scopeSummary: "End-to-end transformation of work-capability assessment and
    health-related benefits delivery, replacing PIP/ESA assessment contracts,
    integrating with NHS occupational health, and delivering single digital
    customer journey by FY27-28."
  sro: "Director General, Service Transformation"
resourceAllocation.tradeOffsAcknowledged: ["Reduced face-to-face Jobcentre footprint in lowest-demand areas to fund WorkWell scaling"]
pursuitImplications[0]:
  implication: "Major recompete window for employability/occupational-health
    services in FY26-27; incumbents face displacement risk if WorkWell
    framework structure differs from current Restart-style prime model."
  category: "structural"
  rationale: "WorkWell scaling is named as a primary delivery vehicle with
    supplier-implication signal indicating market-refresh intent."
```
