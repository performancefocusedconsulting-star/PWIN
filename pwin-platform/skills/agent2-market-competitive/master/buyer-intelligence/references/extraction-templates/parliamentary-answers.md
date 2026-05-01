# Extraction Template — Parliamentary Questions and Written Answers

This template is loaded when a source is classified as
`parliamentary_answers`.

Parliamentary written and oral answers are underused intelligence
sources. When an MP tables a question about a named programme, a named
official, or a departmental budget line, a minister's response on the
record is Tier 3 scrutiny with Tier 1 factual content — it either
confirms or contradicts the buyer's own published position with the
additional discipline of parliamentary accountability. Named officials,
confirmed funding figures, delivery confidence, contract awards, and
programme names all appear in Hansard before they reach annual reports.

The Defence Digital dossier (v3.0) missed several programme names and
delivery confidence signals that appeared in defence oral and written
answers. This template ensures those are systematically captured.

---

## When to apply this template

Apply when the source is any of:

- Hansard written answers (single question or a batch search result on a topic)
- Oral questions and supplementary answers (Hansard)
- Written ministerial statements (WMS)
- Departmental select committee evidence sessions (formal Q&A transcript)

Do not apply to:
- Full inquiry reports — use `nao-pac-report.md` for those
- Debates (no structured Q&A, too unstructured for this template)
- Petitions responses (not subject to the same factual discipline)

---

## Extraction depth requirement

Parliamentary answers are often short and numerous. A Hansard search for
"Defence Digital" or a named programme may return 20–50 answers across
two or three parliaments. Extract:

- Every answer that names a specific programme with a budget, timeline,
  or confidence signal
- Every answer that names a specific official (SRO, Commercial Director,
  Programme Director)
- Every answer that confirms or contradicts the buyer's published position
- Answers older than 3 years are context only (flag as potentially stale)

---

## Template schema

```json
{
  "extractionType": "parliamentary_answers",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "searchScope": {
    "searchTermsUsed": ["string — e.g. 'Defence Digital', 'Skynet 6', 'MODNET'"],
    "hansardUrl": "string or null",
    "dateRangeSearched": "string — e.g. '2023-01 to 2026-04'",
    "answersReviewed": "number",
    "answersExtracted": "number"
  },

  "answers": [
    {
      "answerRef": "string — Hansard reference e.g. 'HC Deb 14 Jan 2025 c123W'",
      "date": "ISO 8601",
      "questioningMp": "string — name and constituency",
      "answeringMinister": "string — name and role",
      "answerType": "written | oral | wms",
      "topic": "string — one-line description of the topic",
      "programmesNamed": ["string"],
      "officialsNamed": [
        {
          "name": "string",
          "role": "string",
          "context": "string — why named (SRO, DG, commercial director)"
        }
      ],
      "budgetOrValueConfirmed": "string or null — exact figure quoted in the answer",
      "deliveryConfidenceSignal": "on-track | delayed | at-risk | cancelled | not-stated",
      "contractOrAwardConfirmed": "string or null — named contract, supplier, or route",
      "keyQuote": "string — verbatim extract (30–100 words) of the most material part of the answer",
      "standsPolicyPosition": "confirms | contradicts | nuances | neutral",
      "confidenceNote": "string or null — any ministerial hedging language"
    }
  ],

  "synthesisFindings": {
    "programmesWithConfirmedBudgets": [
      {
        "programmeName": "string",
        "budgetConfirmed": "string",
        "mostRecentAnswerRef": "string"
      }
    ],
    "officialsNamedAcrossAnswers": [
      {
        "name": "string",
        "role": "string",
        "firstNamedDate": "ISO 8601",
        "answerRefs": ["string"]
      }
    ],
    "deliverySignals": [
      {
        "programmeName": "string",
        "signal": "on-track | delayed | at-risk | cancelled",
        "mostRecentAnswerRef": "string",
        "quote": "string"
      }
    ],
    "policyPositionsDivergingFromPublished": [
      {
        "topic": "string",
        "publishedPosition": "string — what the buyer's own docs say",
        "parliamentaryPosition": "string — what the minister confirmed on the record",
        "answerRef": "string"
      }
    ]
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
      "extractedPath": "string",
      "mapsToDossierField": "string",
      "operation": "extend | replace | upgrade",
      "lens": "mandate | pressure | money | buying-behaviour | risk-posture | supplier-landscape | pursuit-implications",
      "answersFrameworkQuestions": ["string"],
      "closesActionIds": ["string or null"]
    }
  ],

  "extractionQualityCheck": {
    "answersWithProgrammeNamesCaptured": "number",
    "officialsNamedCaptured": "number",
    "budgetFiguresConfirmed": "number",
    "deliverySignalsCaptured": "number",
    "divergencesFromPublishedPositionCaptured": "number",
    "unextractedAreas": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `answers[].programmesNamed[]` + budget confirmed | `strategicPriorities.majorProgrammes[]` | pressure, money | extend |
| `answers[].officialsNamed[]` | `decisionUnitAssumptions.perRoleInterests` | mandate | extend |
| `synthesisFindings.officialsNamedAcrossAnswers[]` | `organisationContext.seniorLeadership[]` | mandate | extend (parliamentary record is authoritative on who holds a named role at that date) |
| `answers[].budgetOrValueConfirmed` | `commercialAndRiskPosture` (confirmed funding quantum) | money | upgrade (on-record confirmed > inferred from strategy docs) |
| `synthesisFindings.deliverySignals[]` | `risksAndSensitivities.programmeLevelRisks[]` | risk-posture | extend |
| `synthesisFindings.policyPositionsDivergingFromPublished[]` | `risksAndSensitivities.summaryNarrative` | risk-posture | extend |
| `answers[].contractOrAwardConfirmed` | `supplierEcosystem.incumbentSuppliers[]` | supplier-landscape | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `answersWithProgrammeNamesCaptured` = 0 for a named-programme search
   that targeted a major programme. If Hansard returns zero results for
   a programme that exists in the acquisition pipeline, record this as a
   confirmed gap in `sourceRegister.gaps` with the programme name and
   search terms used.
2. `officialsNamedCaptured` = 0 for a search that covered the last two
   years. Parliamentary answers routinely name officials in roles — zero
   captures indicates the search was too narrow.
3. `keyQuote` missing on any answer rated as material (programme name +
   budget or delivery signal). Verbatim quotes from Hansard are
   authoritative and should be preserved.

---

## Worked example (illustrative — Defence Digital parliamentary answers)

```
searchScope:
  searchTermsUsed: ["Defence Digital", "Skynet 6", "MODNET", "Future C4I", "Foundry"]
  dateRangeSearched: "2023-01 to 2026-04"
  answersReviewed: 34
  answersExtracted: 11

answers[0]:
  answerRef: "HC Deb 19 Nov 2024 c412W"
  date: "2024-11-19"
  questioningMp: "John Healey MP (Wentworth and Dearne)"
  answeringMinister: "Luke Pollard (Minister for the Armed Forces)"
  answerType: "written"
  topic: "Skynet 6 WSS contract and in-service date"
  programmesNamed: ["Skynet 6 WSS"]
  officialsNamed: []
  budgetOrValueConfirmed: "The Skynet 6 wide-band satellite service contract is valued at
    approximately £2.7 billion over its lifetime."
  deliveryConfidenceSignal: "on-track"
  contractOrAwardConfirmed: "Airbus Defence and Space, awarded 2020"
  keyQuote: "The Skynet 6 Wide-Band Satellite Service is being delivered by Airbus Defence
    and Space under a contract awarded in 2020. The programme remains on track. The
    whole-life value is approximately £2.7 billion."
  standsPolicyPosition: "confirms"

synthesisFindings:
  programmesWithConfirmedBudgets:
    - programmeName: "Skynet 6 WSS"
      budgetConfirmed: "£2.7bn whole-life"
      mostRecentAnswerRef: "HC Deb 19 Nov 2024 c412W"
  officialsNamedAcrossAnswers:
    - name: "Victoria Cope"
      role: "Director General Commercial, Defence Digital"
      firstNamedDate: "2024-02-15"
      answerRefs: ["HC Deb 15 Feb 2024 c210W"]

pursuitImplications:
  - implication: "Skynet 6 WSS confirmed at £2.7bn whole-life to Airbus; no competition route.
      Bid teams should position for integration, ground-segment, or managed services
      alongside Airbus as sub-supplier."
    category: "structural"
    rationale: "Single-source confirmed on record."
```
