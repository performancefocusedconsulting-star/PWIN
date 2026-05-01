# Extraction Template — Spending Review Settlement

This template is loaded when a source is classified as `spending_review_settlement`.

A Spending Review settlement is the HM Treasury publication that fixes a
department's multi-year funding envelope. It is the single most
load-bearing money document in a buyer dossier — it determines what
they can spend, on what, with what strings, against what efficiency
targets. Slogans like "the department received a Spending Review
settlement" are useless. The template forces capture of the actual
numbers, conditions, and unfunded gaps.

---

## When to apply this template

Apply when the source is any of:

- A Spending Review settlement letter (HMT to department)
- A department's published response to a Spending Review settlement
- An HMT Spending Review chapter covering this specific department
- A Spending Review technical annex relevant to this department
- A multi-year financial settlement (e.g. NHS long-term plan settlement,
  police funding settlement, devolved-administration block grant)

For Main and Supplementary Estimates, do not use this template — those
report in-year movements against an already-set envelope. Use the
annual-report template's `financialState` block instead.

---

## Extraction depth requirement

Settlements are typically 4–20 pages. In deep mode, the extraction must
cover:

- Headline totals (Capital DEL + Resource DEL year-by-year)
- Real-terms growth/cut figures
- Named ring-fenced commitments
- Productivity / efficiency expectations
- Conditions or strings attached
- Department-stated unfunded pressures (where the response or commentary
  acknowledges them)

Skip:

- Cross-cutting HMT framing not specific to this department
- Macroeconomic context paragraphs

---

## Template schema

```json
{
  "extractionType": "spending_review_settlement",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact document title",
    "buyerName": "string",
    "settlementName": "string — e.g. 'Spending Review 2025'",
    "periodCovered": "string — e.g. 'FY26-27 to FY28-29' (typically 3 years)",
    "publicationDate": "ISO 8601",
    "publisher": "HM Treasury | department response | other",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "envelope": {
    "totalDelByYear": [
      {
        "year": "string — e.g. 'FY26-27'",
        "resourceDel": "string — e.g. '£62.4bn'",
        "capitalDel": "string — e.g. '£8.7bn'",
        "totalDel": "string"
      }
    ],
    "realTermsGrowthOrCut": [
      {
        "year": "string",
        "value": "string — e.g. '+1.8%' or '-2.4%'",
        "comparator": "string — e.g. 'against FY24-25 baseline'"
      }
    ],
    "comparisonToPriorSr": "string — narrative comparison to prior SR period (more generous? tighter? real-terms flat?)"
  },

  "ringFencedCommitments": [
    {
      "commitment": "string — what is ring-fenced",
      "value": "string — total or annual figure",
      "rationale": "string — why ring-fenced (statutory, manifesto, prior commitment, etc.)",
      "implicationForExternalBuying": "string — protects/threatens specific spend lines"
    }
  ],

  "productivityAndEfficiency": {
    "headlineTarget": "string or null — e.g. '5% real-terms productivity gain by FY28-29'",
    "namedSavingsProgrammes": [
      {
        "programmeName": "string",
        "value": "string — savings target",
        "byWhen": "string",
        "deliveryRoute": "string or null — automation, workforce reduction, contract renegotiation, demand management"
      }
    ],
    "specifiedReformConditions": ["string — conditions HMT attaches to the settlement"],
    "techAndDigitalInvestmentEarmarks": ["string — named pots for digital, AI, automation, data"]
  },

  "unfundedOrContingentItems": [
    {
      "item": "string — what is not funded or only partly funded",
      "shortfallEstimate": "string or null",
      "departmentPosition": "string — what the department has said (acceptance, escalation, mitigation route)",
      "implicationForExternalBuying": "string — likely descope, deferral, or pressure on related contracts"
    }
  ],

  "newOrExpandedFundingLines": [
    {
      "lineName": "string",
      "value": "string",
      "period": "string",
      "purpose": "string — what the money is for",
      "deliveryVehicle": "string or null — programme, body, framework, in-house team"
    }
  ],

  "languageAndFraming": {
    "policyFrames": ["string — e.g. 'value for money', 'productivity', 'public service reform', 'AI-enabled efficiency'"],
    "keyJustifications": ["string — language used to justify the settlement shape"],
    "treasuryConditions": ["string — distinctive HMT phrasings about expectations"]
  },

  "namedStakeholders": [
    {
      "name": "string",
      "role": "string — e.g. 'Chief Secretary to the Treasury', 'Permanent Secretary', 'Finance Director'",
      "context": "string — how they appear in the document"
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
    "envelopeYearsCaptured": "number — must equal years in document",
    "ringFencedCommitmentsCaptured": "number",
    "productivityTargetCaptured": "boolean",
    "unfundedItemsAcknowledged": "boolean — true if document or department response acknowledged any",
    "unextractedSections": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `envelope.totalDelByYear[]` | `organisationContext.fundingModel` | mandate, money | replace (settlement is authoritative) |
| `envelope.realTermsGrowthOrCut` | `strategicPriorities.fiscalPressures` | pressure, money | extend |
| `ringFencedCommitments[]` | `commissioningContextHypotheses.pressuresShapingSpend` | money, pressure | extend |
| `ringFencedCommitments[].implicationForExternalBuying` | `commissioningContextHypotheses.spendClassification` (where mandatory/strategic) | money | upgrade |
| `productivityAndEfficiency.headlineTarget` | `commercialAndRiskPosture.affordabilitySensitivity` | money, risk-posture | upgrade (inference → fact) |
| `productivityAndEfficiency.namedSavingsProgrammes[]` | `strategicPriorities.fiscalPressures` | money, pressure | extend |
| `productivityAndEfficiency.specifiedReformConditions[]` | `commissioningContextHypotheses.driversOfExternalBuying` | pressure | extend |
| `productivityAndEfficiency.techAndDigitalInvestmentEarmarks[]` | `strategicPriorities.majorProgrammes[]` (as funded headroom) | money, pressure | extend |
| `unfundedOrContingentItems[]` | `commissioningContextHypotheses.timelineRisks` | money, risk-posture | extend |
| `unfundedOrContingentItems[]` (where department escalating) | `commissioningContextHypotheses.spendClassification` (reactive/discretionary) | money | extend |
| `newOrExpandedFundingLines[]` | `strategicPriorities.majorProgrammes[]` | pressure, money | extend |
| `languageAndFraming` | `cultureAndPreferences.languageAndFraming` | risk-posture | extend |
| `publicCommitments[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `fullRead: false` in deep mode for a settlement >5 pages.
2. `envelope.totalDelByYear` empty — every settlement contains DEL totals.
3. `productivityAndEfficiency.headlineTarget` null AND
   `productivityAndEfficiency.namedSavingsProgrammes` empty —
   contemporary UK settlements always carry productivity/efficiency
   asks. If genuinely absent, record explicit reason in
   `unextractedSections`.
4. `pursuitImplications[]` empty — settlements always carry implications.
   At minimum: affordability-sensitivity recalibration; ring-fenced
   spend ringing protection or threat for specific contract types;
   any productivity target → over-evidence delivered savings in
   bid responses.
5. `dossierMappings` does not include the `pursuitImplications` mapping.

---

## Worked example (illustrative)

For a hypothetical "DfT Spending Review 2025 Settlement" extraction:

```
envelope.totalDelByYear[0]:
  year: "FY26-27"
  resourceDel: "£18.2bn"
  capitalDel: "£8.6bn"
  totalDel: "£26.8bn"
envelope.realTermsGrowthOrCut[0]: { year: "FY26-27", value: "-0.8%", comparator: "against FY24-25" }
ringFencedCommitments[0]:
  commitment: "HS2 Phase 1 completion to Old Oak Common"
  value: "£12.4bn over period"
  rationale: "manifesto commitment, prior contractual obligations"
  implicationForExternalBuying: "protects HS2 supply-chain spend; squeezes non-HS2 capital"
productivityAndEfficiency.namedSavingsProgrammes[0]:
  programmeName: "Operational efficiency programme — back-office automation"
  value: "£420m by FY28-29"
  byWhen: "FY28-29"
  deliveryRoute: "automation, shared services consolidation"
unfundedOrContingentItems[0]:
  item: "Strategic Road Network renewals beyond core maintenance envelope"
  shortfallEstimate: "~£800m over period vs. National Highways ask"
  departmentPosition: "Continuing to engage HMT; expected to absorb via prioritisation"
  implicationForExternalBuying: "Likely descope or deferral of non-statutory renewals; competitive pressure on price"
pursuitImplications[0]:
  implication: "Expect aggressive price scrutiny on operational service contracts; affordability narrative essential."
  category: "commercial"
  rationale: "Real-terms RDel cut combined with named back-office automation savings target"
```

That level of substance satisfies the template. "DfT received its
Spending Review settlement" does not.
