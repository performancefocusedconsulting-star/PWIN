# Extraction Template — Acquisition Pipeline

This template is loaded when a source is classified as
`acquisition_pipeline`.

An acquisition pipeline document is the most direct route into a buyer's
investment intentions at programme level. For Ministry of Defence, this
is the MOD Acquisition Pipeline Excel file published on the "Doing
Business with Defence" guidance page. Equivalent documents exist for
other large commissioners (CCS pipeline, NHS England investment
programme). The pipeline names every major programme with cost
confidence, schedule, phase, and route to market — exactly the content
missing from narrative strategy documents.

The Defence Digital dossier (v3.0) missed every named programme in the
pipeline despite them being publicly available. This template exists to
ensure that does not recur. Apply it whenever an acquisition pipeline
document is available.

---

## When to apply this template

Apply when the source is any of:

- MOD Acquisition Pipeline (Excel, published on `gov.uk/guidance/doing-business-with-defence`)
- Defence Sourcing Portal published pipeline (quarterly or annual)
- CCS pipeline publication (category pipelines for major spend areas)
- NHS England capital / digital investment programme schedule
- Any departmental "upcoming procurements" or "pipeline commitments" publication that names individual programmes with values and expected dates

Do not apply to:
- Planning notices (PIN / Prior Information Notices) for individual tenders — these are individual records, not pipeline overviews
- Roadmaps that name initiatives but carry no value or schedule data

---

## Extraction depth requirement

Pipeline Excel files often contain 50–200 programme rows. Deep mode
requires capture of every programme above £50m estimated whole-life cost
that the buyer is responsible for procuring. For the MoD Acquisition
Pipeline, capture all programmes in the "assessment", "demonstration",
"manufacture", or "in-service extension" phases, as these represent
near-term commercial activity.

---

## Template schema

```json
{
  "extractionType": "acquisition_pipeline",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact title e.g. 'MOD Acquisition Pipeline April 2025'",
    "buyerOrganisation": "string — e.g. 'Ministry of Defence'",
    "publishingUnit": "string — e.g. 'Defence Equipment and Support' or 'Defence Commercial'",
    "publicationDate": "ISO 8601 or year-month string",
    "reportingPeriod": "string — e.g. 'FY24-25 Q4'",
    "totalProgrammesListed": "number or null",
    "extractionDepth": "full | above-threshold | sample"
  },

  "programmes": [
    {
      "programmeName": "string — exact name as listed (e.g. 'Skynet 6 WSS', 'MODNET', 'Future C4I', 'F-IUS')",
      "abbreviation": "string or null — official abbreviation used",
      "responsibleOrganisation": "string — which part of the buyer is responsible (e.g. 'Defence Digital', 'DE&S Maritime', 'Joint Forces Command')",
      "phase": "concept | assessment | demonstration | manufacture | in-service | in-service-extension | other",
      "approvedCostBand": "string or null — e.g. '£1bn–£2bn', '£2bn+'",
      "estimatedWholeCost": "string or null — exact figure if stated",
      "annualBudget": "string or null — in-year budget if stated",
      "expectedInServiceDate": "string or null — e.g. '2027', 'FY27-28'",
      "expectedProcurementStart": "string or null — when the procurement competition is expected to launch",
      "routeToMarket": "open-competition | single-source | framework-calloff | negotiated | tbc | not-stated",
      "namedFramework": "string or null — which framework, if route is framework-calloff",
      "sroName": "string or null — Senior Responsible Owner name if listed",
      "costConfidence": "green | amber | red | not-stated",
      "scheduleConfidence": "green | amber | red | not-stated",
      "inNISTAReport": "boolean — whether this programme also appears in the NISTA/GMPP report",
      "keySuppliers": ["string — named incumbent or shortlisted suppliers if listed"],
      "notes": "string or null — any material flags (e.g. 'subject to SDR review', 'on hold', 'single source')"
    }
  ],

  "pipelineSummary": {
    "totalValueAbove50m": "string or null — aggregate estimated value of programmes above £50m in the pipeline",
    "phaseDistribution": {
      "concept": "number",
      "assessment": "number",
      "demonstration": "number",
      "manufacture": "number",
      "inService": "number",
      "inServiceExtension": "number"
    },
    "routeToMarketDistribution": {
      "openCompetition": "number",
      "singleSource": "number",
      "frameworkCalloff": "number",
      "tbc": "number"
    },
    "nearTermCompetitions": [
      {
        "programmeName": "string",
        "expectedLaunch": "string",
        "estimatedValue": "string or null",
        "routeToMarket": "string"
      }
    ]
  },

  "incumbentSignals": [
    {
      "programmeName": "string",
      "incumbentSupplier": "string",
      "contractType": "string — prime | subcontractor | framework holder",
      "renewalRisk": "high | medium | low | unknown",
      "rationale": "string"
    }
  ],

  "frameworkRouteSignals": [
    {
      "frameworkName": "string",
      "frameworkReferenceNo": "string or null — e.g. 'RM6098'",
      "programmesExpected": ["string — programme names expected to route through this framework"],
      "estimatedCallOffValue": "string or null"
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
    "programmesAbove50mCaptured": "number",
    "nearTermCompetitionsCaptured": "number",
    "routeToMarketPopulated": "boolean",
    "sroNamesCaptured": "number",
    "incumbentSignalsCaptured": "number",
    "unextractedCategories": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `programmes[].programmeName` + phase + cost | `strategicPriorities.majorProgrammes[]` | pressure, money | extend |
| `programmes[].responsibleOrganisation` | `organisationContext` (confirms sub-org scope) | mandate | extend |
| `programmes[].routeToMarket` + `namedFramework` | `procurementBehaviour.frameworkUsage` | buying-behaviour | extend |
| `programmes[].routeToMarket` = single-source | `procurementBehaviour.summaryNarrative` (single-source prevalence) | buying-behaviour | extend |
| `programmes[].expectedProcurementStart` | `commissioningContextHypotheses.upcomingProcurements[]` | pressure | upgrade (pipeline is more authoritative than inference) |
| `programmes[].sroName` | `decisionUnitAssumptions` (SRO as commercial decision node) | mandate | extend |
| `incumbentSignals[]` | `supplierEcosystem.incumbentSuppliers[]` | supplier-landscape | extend |
| `frameworkRouteSignals[]` | `supplierEcosystem.barriersToEntry` | supplier-landscape | extend |
| `pipelineSummary.nearTermCompetitions[]` | `commissioningContextHypotheses.upcomingProcurements[]` | buying-behaviour, pressure | upgrade |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `extractionDepth: sample` and the pipeline has more than 20 programmes
   above £50m — full read is required.
2. `programmesAbove50mCaptured` = 0 — even a short pipeline document will
   have at least one significant programme.
3. `routeToMarketPopulated: false` — pipeline documents always indicate
   route (even if `tbc`). Not capturing it wastes the primary commercial signal.
4. `pursuitImplications[]` empty — near-term competitions, single-source
   concentration, framework-gate implications, and SRO names are all
   bidder-relevant. A pipeline that names no pursuit implications has not
   been extracted correctly.

---

## Worked example (illustrative — MoD Acquisition Pipeline)

```
programmeName: "Skynet 6 WSS (Wide-band Satellite Service)"
responsibleOrganisation: "Defence Digital / DE&S"
phase: "manufacture"
approvedCostBand: "£2bn+"
expectedInServiceDate: "2030"
routeToMarket: "single-source"
keySuppliers: ["Airbus Defence and Space"]
inNISTAReport: true
notes: "Successor to Skynet 5 PFI; in-orbit payload under separate programme"

programmeName: "Future C4I"
responsibleOrganisation: "Defence Digital"
phase: "assessment"
approvedCostBand: "£1bn–£2bn"
expectedProcurementStart: "2027"
routeToMarket: "open-competition"
namedFramework: null
costConfidence: "amber"
scheduleConfidence: "amber"

programmeName: "MODNET Next Generation"
responsibleOrganisation: "Defence Digital"
phase: "demonstration"
approvedCostBand: "£500m–£1bn"
routeToMarket: "framework-calloff"
namedFramework: "Network Services 3 / RM6116"

frameworkRouteSignals:
  - frameworkName: "TEPAS 2"
    frameworkReferenceNo: "RM6098"
    programmesExpected: ["Foundry", "Zodiac", "TACSYS professional services"]
    estimatedCallOffValue: "~£200m over 3 years"

pursuitImplications:
  - implication: "Future C4I represents the highest-value open competition in Defence Digital's pipeline
      for the next three years; winning a design-partnership or early-market engagement role is a
      strategic entry point for the prime competition."
    category: "timing"
    rationale: "£1bn–£2bn, assessment phase, open competition, procurement start 2027."
  - implication: "Skynet 6 WSS is single-source to Airbus — no competition opportunity. Sub-supply
      and integration services remain available through TEPAS 2."
    category: "structural"
    rationale: "Single-source confirmed; Airbus named incumbent."
```
