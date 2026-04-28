# Extraction Template — Industry Engagement Deck

This template is loaded when a source is classified as
`industry_engagement_deck`.

Industry engagement decks are the richest commercial intelligence
documents a buyer produces — and they are rarely indexed or searchable.
They exist because procurement law requires buyers to brief the market
before a major competition. They appear at techUK events, ADS forums,
Defence Commercial Business Forum sessions, RUSI conferences, NHS Digital
supplier days, and departmental procurement briefings. They name the
commercial function's leadership, the five-category or seven-category
spend structure, the named pipeline programmes with values, the
framework routes intended, and the SME and social-value commitments.
None of that appears in Annual Reports.

The techUK Defence Commercial Business Forum deck (February 2025,
Victoria Cope presenting) is the canonical example of this document type.
It named: five Deputy Commercial Directors by name and category, the
£4.7bn annual procurement figure, the five commercial categories, the
named programmes in each category, and the preferred CCS framework routes.
None of those appeared in the Defence Digital dossier v3.0. This template
closes that gap for any deck of this type, from any buyer.

This document type is the primary use case for the INJECT mode — it is
unlikely to be discoverable via web search but is highly valuable when
the account team has attended the briefing.

---

## When to apply this template

Apply when the source is any of:

- A slide deck presented at a supplier day, industry forum, or market-
  engagement event (whether obtained by attending, via a FOI, or as a
  published PDF)
- A written ministerial statement summarising a supplier engagement event
- A procurement pre-qualification questionnaire pack with commercial
  context slides
- A category strategy presentation delivered to potential suppliers
- An NHS Digital supplier briefing pack
- A Cabinet Office commercial pipeline presentation

Do not apply to:
- Think-tank or academic conference papers — these are analytical, not
  commercial; use the standard source register
- Press releases about events (no substantive commercial content)
- Post-event summaries by third parties (second-hand; lower tier)

---

## Extraction depth requirement

Industry engagement decks are typically 20–60 slides and are the most
information-dense documents in the Tier 1 set. Apply a full read. Every
slide that names a category, programme, supplier, framework, or
commercial commitment must be extracted. Skip purely decorative or
agenda slides.

---

## Template schema

```json
{
  "extractionType": "industry_engagement_deck",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact title of the deck e.g. 'Defence Commercial Business Forum — Commercial Update'",
    "eventName": "string or null — e.g. 'techUK Defence Commercial Business Forum'",
    "eventDate": "ISO 8601 or year-month",
    "presentingOrganisation": "string",
    "presenters": [
      {
        "name": "string",
        "role": "string — exact role as shown in the deck",
        "isDecisionMaker": "boolean"
      }
    ],
    "intendedAudience": "string — e.g. 'strategic supplier community', 'SME market', 'prime contractors'",
    "totalSlides": "number or null",
    "extractionDepth": "full-read | key-sections"
  },

  "headlineMessages": {
    "openingCommitments": ["string — verbatim or close-paraphrase of stated commercial commitments"],
    "priorities": ["string — the top 3–5 commercial priorities as stated"],
    "toneSignals": "string — overall posture (e.g. 'partnership-first', 'value-for-money drive', 'SME growth focus')"
  },

  "commercialFunctionStructure": {
    "totalAnnualProcurementValue": "string or null — headline figure (e.g. '£4.7bn per year')",
    "numberOfContracts": "string or null — e.g. '503 contract awards in FY23-24'",
    "commercialDirectorOrEquivalent": {
      "name": "string or null",
      "role": "string",
      "background": "string or null"
    },
    "categoryLeads": [
      {
        "name": "string or null",
        "role": "string — e.g. 'Deputy Commercial Director, Digital Platforms'",
        "categoryScope": "string — what categories / programmes they lead"
      }
    ],
    "functionStructureNotes": "string or null — any reorganisation or structural change signalled"
  },

  "spendCategories": [
    {
      "categoryName": "string — e.g. 'Digital Platforms', 'Connectivity', 'Cyber and Intelligence'",
      "annualValue": "string or null",
      "categoryLead": "string or null — name of the category lead if named",
      "keyProgrammes": ["string — named programmes in this category"],
      "primaryFrameworks": ["string — named CCS or departmental frameworks used in this category"],
      "smeAndVcseTargets": "string or null",
      "directionalSignal": "growing | stable | reducing | restructuring | unstated"
    }
  ],

  "namedProgrammes": [
    {
      "programmeName": "string",
      "category": "string — which spend category this sits in",
      "estimatedValue": "string or null — as stated in the deck",
      "phase": "concept | assessment | demonstration | manufacture | in-service | in-service-extension | not-stated",
      "routeToMarket": "open-competition | single-source | framework-calloff | negotiated | tbc | not-stated",
      "namedFramework": "string or null",
      "expectedTimeline": "string or null — launch date or in-service date",
      "incumbentSignal": "string or null — named or implied incumbent",
      "sroOrSponsor": "string or null"
    }
  ],

  "frameworkUsage": [
    {
      "frameworkName": "string",
      "frameworkReferenceNo": "string or null",
      "usageDescription": "string — what categories they use it for",
      "callOffVolume": "string or null — stated spend or number of call-offs",
      "preferredUsageMode": "direct-award | further-competition | both | not-stated"
    }
  ],

  "marketEngagementSignals": {
    "supplierDayAnnouncements": ["string"],
    "earlyMarketEngagementPlanned": ["string — named competitions where pre-market engagement is offered"],
    "smeEngagementCommitments": ["string"],
    "publishedPipelineCommitment": "string or null",
    "feedbackMechanisms": ["string"]
  },

  "commercialCommitmentsOnRecord": [
    {
      "commitment": "string — direct quote or close paraphrase",
      "speaker": "string — name and role",
      "topic": "string",
      "slide": "number or null"
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
    "headlineProcurementValueCaptured": "boolean",
    "categoryLeadNamesCaptured": "number",
    "namedProgrammesCaptured": "number",
    "frameworksCaptured": "number",
    "pursuitImplicationsCaptured": "number",
    "unextractedSlides": ["string or number"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `commercialFunctionStructure.totalAnnualProcurementValue` | `procurementBehaviourSnapshot.totalSpend` | money | upgrade (stated by the buyer's own commercial director > inferred from FTS) |
| `commercialFunctionStructure.commercialDirectorOrEquivalent` | `decisionUnitAssumptions.perRoleInterests.commercial` | buying-behaviour | upgrade |
| `commercialFunctionStructure.categoryLeads[]` | `decisionUnitAssumptions.perRoleInterests.commercial` | buying-behaviour | extend |
| `spendCategories[]` | `procurementBehaviour.categoryConcentration` | buying-behaviour, money | upgrade (named categories with values > inferred from FTS aggregations) |
| `namedProgrammes[]` | `strategicPriorities.majorProgrammes[]` | pressure, money | extend |
| `namedProgrammes[].routeToMarket` + `namedFramework` | `procurementBehaviour.frameworkUsage` | buying-behaviour | extend |
| `namedProgrammes[].expectedTimeline` | `commissioningContextHypotheses.upcomingProcurements[]` | buying-behaviour, pressure | upgrade |
| `frameworkUsage[]` | `procurementBehaviour.frameworkUsage` | buying-behaviour | upgrade (named by commercial director is most authoritative) |
| `marketEngagementSignals.earlyMarketEngagementPlanned[]` | `procurementBehaviour.marketEngagementStyle` | buying-behaviour | extend |
| `commercialCommitmentsOnRecord[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `headlineProcurementValueCaptured: false` — any commercial briefing
   deck names the organisation's annual procurement value. If it is not
   captured, the deck has not been fully read.
2. `categoryLeadNamesCaptured` = 0 — decks of this type name the
   category leads by role. Zero means the structure slides were not read.
3. `namedProgrammesCaptured` = 0 — the primary purpose of these decks
   is to signal what programmes are coming and on what route. Zero
   programmes captured is a failed extraction.
4. `frameworksCaptured` = 0 — every commercial briefing deck references
   the frameworks the buyer uses. Zero captures means the routes-to-market
   slides were not extracted.
5. `pursuitImplicationsCaptured` = 0 — category structure, named category
   leads, framework gates, and pipeline timing are all directly
   pursuit-relevant. Zero implications means the bidder-relevance pass
   was not applied.
6. `dossierMappings` does not include the `decisionUnitAssumptions` mapping
   for category leads — named commercial leads with category scope is the
   highest-value field this document type provides.

---

## Worked example (illustrative — techUK Defence Commercial Business Forum, Feb 2025)

```
documentMeta:
  title: "Defence Commercial Business Forum — Commercial Landscape Update"
  eventName: "techUK Defence Commercial Business Forum"
  eventDate: "2025-02"
  presentingOrganisation: "Ministry of Defence / Defence Digital"
  presenters:
    - name: "Victoria Cope"
      role: "Director General Commercial, Defence Digital"
      isDecisionMaker: true

commercialFunctionStructure:
  totalAnnualProcurementValue: "£4.7bn per year"
  numberOfContracts: "503 contract awards in FY23-24"
  commercialDirectorOrEquivalent:
    name: "Victoria Cope"
    role: "Director General Commercial, Defence Digital"
  categoryLeads:
    - name: "Kakaras"
      role: "Deputy Commercial Director"
      categoryScope: "Digital Platforms"
    - name: "Lightfoot"
      role: "Deputy Commercial Director"
      categoryScope: "Connectivity and Networks"
    - name: "Barras"
      role: "Deputy Commercial Director"
      categoryScope: "Cyber and Intelligence"
    - name: "Mundy"
      role: "Deputy Commercial Director"
      categoryScope: "IT Infrastructure and Managed Services"
    - name: "Hamley"
      role: "Deputy Commercial Director"
      categoryScope: "Professional Services"

spendCategories:
  - categoryName: "Digital Platforms"
    categoryLead: "Kakaras"
    keyProgrammes: ["Foundry", "Zodiac", "Future C4I (pre-pipeline)"]
    primaryFrameworks: ["TEPAS 2 / RM6098", "Tech Services 3 / RM6100"]
    directionalSignal: "growing"
  - categoryName: "Connectivity and Networks"
    categoryLead: "Lightfoot"
    keyProgrammes: ["MODNET Next Generation", "NGCN", "SK6 WSS (ground segment integration)"]
    primaryFrameworks: ["Network Services 3 / RM6116", "MVDS / RM6261"]
    directionalSignal: "restructuring"
  - categoryName: "Professional Services"
    categoryLead: "Hamley"
    keyProgrammes: ["TACSYS professional services", "Foundry programme management"]
    primaryFrameworks: ["DIPS (Digital and IT Professional Services)", "MCF 4 / RM6187"]
    annualValue: "~£400m"
    directionalSignal: "stable"

frameworkUsage:
  - frameworkName: "TEPAS 2"
    frameworkReferenceNo: "RM6098"
    usageDescription: "Primary route for digital platform and application development"
    preferredUsageMode: "further-competition"
  - frameworkName: "DIPS"
    usageDescription: "Professional services, consultancy, programme management"
    preferredUsageMode: "both"

pursuitImplications:
  - implication: "The commercial function is organised around five categories each with a named
      Deputy Commercial Director. Bid teams should identify which category their offer sits in
      and engage the named lead before tender — cold bids into anonymous commercial teams
      are structurally disadvantaged."
    category: "engagement"
    rationale: "Named category leads with named scopes; category structure confirmed by DG Commercial."
  - implication: "£4.7bn annual procurement at 503 awards implies an average contract value of
      ~£9.3m. Bids positioned as strategic partnerships without a realistic programme anchor
      are unlikely to land — the commercial function buys at programme level."
    category: "commercial"
    rationale: "Headline figures from DG Commercial on the record."
```
