# Extraction Template — Digital / Transformation Strategy

This template is loaded when a source is classified as `strategy_document`
of digital, transformation, technology, data, AI, or modernisation flavour.

It enforces a structured, end-to-end extraction so the dossier captures
substance — programmes, quantified targets, named SROs, technology
direction, public commitments — not slogans like "they have a digital
strategy."

---

## When to apply this template

Apply when the source is any of:

- A published digital strategy
- A transformation strategy or transformation plan
- A technology strategy or technology operating model
- A data strategy or data roadmap
- An AI strategy / AI Action Plan / AI ethics framework
- A modernisation programme document
- A "future of [department]" strategic vision document

If the source is a workforce, cyber, or estate strategy, do not use this
template — those will get their own templates. If unsure, default to the
annual-report template's looser structure.

---

## Extraction depth requirement

This template MUST be applied with `extractionDepth: "full-read"` in deep
mode. Skim-reads do not satisfy the template — the quality check at the
end will fail if the extraction is shallow.

---

## Template schema

Produce a JSON object conforming to this schema for each digital strategy
source. The output is *intermediate* — it is not part of the dossier
directly. The `dossierMappings` block at the end declares how each part of
the extraction lands in the dossier.

```json
{
  "extractionType": "digital_strategy",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact document title",
    "publisher": "string — buyer or parent department",
    "publicationDate": "ISO 8601",
    "periodCovered": "string — e.g. 'FY25/26 to FY28/29'",
    "approvingAuthority": "string or null — minister, board, permanent secretary",
    "supersedes": "string or null — predecessor strategy if named",
    "documentLength": "string — e.g. '64 pages'",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "headlineNarrative": {
    "statedProblem": "string — what the strategy says is broken or insufficient today, in their words (≥50 words, must include actual scope, not slogan)",
    "statedAmbition": "string — what they want to be true at the end of the period (≥50 words)",
    "statedChangeDriver": "string — why now (legislation, fiscal pressure, ministerial mandate, prior strategy outcome, audit finding)",
    "tone": "transformational | incremental | corrective | catch-up",
    "toneRationale": "string — one line explaining the tone classification"
  },

  "programmes": [
    {
      "programmeName": "string — exact name as written",
      "description": "string — substance of what the programme will do (≥50 words; must include actual scope, not slogan)",
      "budget": {
        "total": "string or null — e.g. '£180m'",
        "period": "string or null — e.g. 'over 3 years'",
        "fundingSource": "string or null — e.g. 'Spending Review 2025 settlement, capital + revenue split'",
        "confidenceInBudget": "stated | implied | unstated"
      },
      "timeline": {
        "start": "string or null",
        "milestones": ["string — dated milestones if given"],
        "end": "string or null"
      },
      "sro": "string or null — named accountable owner with role",
      "deliveryRoles": [
        { "name": "string", "role": "string", "responsibility": "string" }
      ],
      "deliveryModel": "in-house | outsourced | hybrid | platform-led | partnership | unstated",
      "quantifiedTargets": [
        {
          "metric": "string — fiscal-savings | fte-displacement | productivity | transaction-time | customer-satisfaction | error-rate | digital-adoption | other",
          "value": "string — exact figure as stated",
          "baseline": "string or null",
          "byWhen": "string or null",
          "stretchOrCommitted": "committed | stretch | aspirational | unclear"
        }
      ],
      "dependencies": [
        { "on": "string", "type": "internal-programme | external-policy | parent-dept | supplier | technology | workforce | data" }
      ],
      "risksAcknowledged": ["string — risks the document itself names"],
      "supplierImplications": "string — what this programme means for external suppliers (existing incumbent threatened? new market opening? consolidation?)"
    }
  ],

  "strategicThemes": [
    {
      "theme": "string — e.g. 'cloud-first', 'shared platforms', 'data-driven decisions', 'API-first government'",
      "rationale": "string — why this theme is in the strategy",
      "implicationsForSuppliers": ["string — what bidders need to demonstrate to land against this theme"]
    }
  ],

  "technologyDirection": {
    "stackChoices": ["string — named platforms, frameworks, vendors, or anti-choices"],
    "buildVsBuyPosture": "build-first | buy-first | hybrid | unstated",
    "openSourcePosture": "string or null",
    "dataResidency": "string or null — UK-only, sovereign cloud, etc.",
    "cyberPosture": "string or null — accreditations expected, security model",
    "interoperabilityStandards": ["string — named standards, e.g. GDS API standards, FHIR"],
    "legacyDecommissioning": ["string — named legacy systems being retired, with timelines if stated"]
  },

  "operatingModelImplications": {
    "inHouseVsOutsourced": "string — direction of travel",
    "smeStrategy": "string or null — SME spend targets, opening up to challengers",
    "supplierConsolidation": "string or null — fewer/larger or more/smaller",
    "workforceImpact": "string or null — reskilling, hiring, displacement"
  },

  "namedStakeholders": [
    {
      "name": "string",
      "role": "string",
      "responsibilityInStrategy": "string",
      "isDecisionMaker": "boolean",
      "background": "string or null"
    }
  ],

  "publicCommitments": [
    {
      "statement": "string — direct quote",
      "speaker": "string or null",
      "speakerRole": "string or null",
      "date": "ISO 8601 or null",
      "venue": "string or null — parliament, conference, written ministerial statement"
    }
  ],

  "scrutinyAndAssurance": {
    "namedReviewers": ["string — NAO, GDS, IPA, internal audit, etc."],
    "gateReviewsExpected": ["string"],
    "transparencyCommitments": ["string — published progress reports, dashboards"]
  },

  "languageAndFraming": {
    "preferredTerminology": ["string — 5-10 terms used repeatedly"],
    "policyFrames": ["string — 'value for money', 'AI-enabled', 'mission-led', etc."],
    "avoidLanguage": ["string — terms the document explicitly rejects or critiques"]
  },

  "pursuitImplications": [
    {
      "implication": "string — buyer-derived, bidder-neutral",
      "category": "stance | language | evidence | commercial | engagement | risk-management | timing | structural",
      "rationale": "string"
    }
  ],

  "dossierMappings": [
    {
      "extractedPath": "string — JSON path within this extraction",
      "mapsToDossierField": "string — dotted path in dossier",
      "operation": "extend | replace | upgrade",
      "lens": "mandate | pressure | money | buying-behaviour | risk-posture | supplier-landscape | pursuit-implications",
      "answersFrameworkQuestions": ["string"],
      "closesActionIds": ["string or null"]
    }
  ],

  "extractionQualityCheck": {
    "fullRead": "boolean — true if end-to-end read was performed",
    "minimumProgrammeCount": "number — must equal count of named programmes in document",
    "minimumQuantifiedTargets": "number — must equal count of explicit numerical targets",
    "minimumThemeCount": "number — must equal count of strategic themes named",
    "unextractedSections": ["string — any sections deliberately skipped, with reason"]
  }
}
```

---

## Required dossier mappings (must produce all that apply)

Every applicable mapping must appear in `dossierMappings`. The template
fails quality check if mappings are missing for content that was extracted.

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `programmes[]` | `strategicPriorities.majorProgrammes[]` | pressure, money | extend (or replace if reproduces existing programmes) |
| `headlineNarrative.statedChangeDriver` | `commissioningContextHypotheses.driversOfExternalBuying` | pressure | extend |
| `headlineNarrative.statedAmbition` | `commissioningContextHypotheses.outcomesSought` | pressure | extend |
| `programmes[].quantifiedTargets` | `strategicPriorities.majorProgrammes[].quantifiedTargets` | money, pressure | extend |
| `programmes[].sro` | `organisationContext.seniorLeadership` (if not already there) | mandate | extend |
| `strategicThemes[]` | `strategicPriorities.publishedStrategyThemes` | pressure | extend |
| `technologyDirection.buildVsBuyPosture` | `cultureAndPreferences.changeMaturity.digitalMaturity` | risk-posture | upgrade (inference → fact) |
| `technologyDirection.cyberPosture` | `commercialAndRiskPosture.cyberDataSensitivity` | risk-posture | extend |
| `technologyDirection.dataResidency` | `commercialAndRiskPosture.cyberDataSensitivity` | risk-posture | extend |
| `operatingModelImplications.smeStrategy` | `cultureAndPreferences.socialValueAndESG` | risk-posture | extend |
| `operatingModelImplications.supplierConsolidation` | `supplierEcosystem.summaryNarrative` (forward direction signal) | supplier-landscape | extend |
| `namedStakeholders[]` (where decisionMaker) | `decisionUnitAssumptions.businessOwnerRoles` or `technicalStakeholders` | buying-behaviour | extend |
| `publicCommitments[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `scrutinyAndAssurance` | `commercialAndRiskPosture.auditFoiExposure` | risk-posture | extend |
| `languageAndFraming` | `cultureAndPreferences.languageAndFraming` | risk-posture | replace (this is the most authoritative source for buyer language) |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected (and must be re-run) if any of the following
apply:

1. **`fullRead: false`** in deep mode. If the strategy is over 30 pages, an
   end-to-end read must be performed.
2. **`minimumProgrammeCount: 0`** when the document is a transformation
   strategy. Strategies always name programmes.
3. **`minimumQuantifiedTargets: 0`** when the document is a savings or
   efficiency-driven strategy. Such strategies always cite targets.
4. **Any programme with `description` < 50 words.** That is the slogan
   threshold — descriptions below it indicate the model didn't read the
   substance.
5. **`pursuitImplications[]` empty.** Every digital strategy carries
   pursuit implications. An empty array means the model didn't synthesise.
6. **`dossierMappings` does not include `pursuitImplications` mapping.**
   The seventh lens is mandatory.

---

## Worked example (illustrative)

For a hypothetical "HMRC Tax Administration 2030" strategy, the extraction
should produce something like:

```
programmes[0]:
  programmeName: "Single Customer Account"
  description: "Consolidate the 24 separate digital accounts citizens currently
    use across HMRC services into one customer account, providing a single
    sign-on, unified inbox, real-time tax position, and self-service
    capability for 95% of citizen interactions by 2028. Phased migration
    starting Q3 2026 for self-assessment, extending through PAYE, VAT, and
    business taxes."
  budget: { total: "£180m", period: "FY25-FY28", fundingSource: "SR25 capital", confidence: "stated" }
  sro: "Carl Stratton, Director of Customer Strategy and Tax Design"
  deliveryModel: "hybrid"
  quantifiedTargets:
    - { metric: "fiscal-savings", value: "£56m", byWhen: "FY28", stretchOrCommitted: "committed" }
    - { metric: "transaction-time", value: "70% reduction in average customer journey", baseline: "current 12-min average", byWhen: "FY28", stretchOrCommitted: "stretch" }
    - { metric: "digital-adoption", value: "95% of interactions self-service", byWhen: "FY28", stretchOrCommitted: "committed" }
  supplierImplications: "Major opportunity for digital identity and customer-experience suppliers; threat to incumbent self-assessment platform supplier (Capgemini RM3804 lot 1)"
```

That level of detail satisfies the template. "HMRC has a digital strategy"
does not.
