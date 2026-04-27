# Extraction Template — Annual Report and Accounts

This template is loaded when a source is classified as `annual_report`.

Annual reports are the broadest single document a buyer publishes. They
cover financial state, leadership, performance, governance, audit, and
strategic narrative — feeding six of the seven dossier lenses (everything
except `pursuit-implications`, which is synthesised from the rest).

---

## When to apply this template

Apply when the source is any of:

- A central-government department's Annual Report and Accounts
- An executive agency's annual report
- An NDPB's annual report
- An NHS trust's or ICB's annual report and accounts
- A local authority's Statement of Accounts (with narrative)
- A devolved-government body's annual report

Apply to a **single financial year**. If the user provides multiple years,
run the template once per year, treating each as its own source.

---

## Extraction depth requirement

Annual reports are typically 100–300 pages. In deep mode, the extraction
must cover at minimum:

- Performance Report section (in full)
- Accountability Report (governance + remuneration)
- Financial statements (key totals only — no need to reconcile)
- Auditor's report (the qualification, if any)
- Strategic foreword by Permanent Secretary / CEO

Skip:
- Detailed remuneration tables (sample only)
- Detailed accounting policy notes
- Mandatory environmental reporting boilerplate (capture the headline only)

---

## Template schema

```json
{
  "extractionType": "annual_report",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact title (e.g. 'HMRC Annual Report and Accounts 2024-25')",
    "buyerName": "string",
    "financialYear": "string — e.g. 'FY24-25'",
    "publicationDate": "ISO 8601",
    "permanentSecretaryOrCEO": "string — author of the foreword",
    "auditor": "string — typically 'Comptroller and Auditor General' for central gov",
    "totalPages": "number",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "scaleAndShape": {
    "totalExpenditure": "string — e.g. '£62.3bn'",
    "totalIncome": "string or null",
    "headcount": {
      "total": "number or null",
      "fullTimeEquivalent": "number or null",
      "yearOnYearChange": "string or null — e.g. '+3.2% (1,847 net additions)'"
    },
    "geographicFootprint": "string or null",
    "operationalScale": "string — e.g. 'processed 33m self-assessment returns; collected £786bn in tax revenue'"
  },

  "leadership": {
    "permanentSecretaryOrCEO": {
      "name": "string",
      "since": "string or null",
      "background": "string or null",
      "isNewThisYear": "boolean"
    },
    "chair": "string or null",
    "boardChanges": [
      {
        "name": "string",
        "role": "string",
        "changeType": "appointed | departed | role-changed",
        "date": "string or null",
        "reason": "string or null"
      }
    ],
    "nonExecutiveDirectors": ["string — list of names and roles"],
    "executiveCommitteeStructure": "string — brief description of how the org is led"
  },

  "performance": {
    "kpiResults": [
      {
        "kpiName": "string",
        "target": "string",
        "actual": "string",
        "delta": "string — met | missed | exceeded | partially-met",
        "narrativeContext": "string — why if missed or exceeded"
      }
    ],
    "majorProgrammeStatus": [
      {
        "programmeName": "string",
        "status": "on-track | amber | red | delivered | descoped | delayed",
        "narrativeContext": "string",
        "ipaRagRating": "string or null — if reported"
      }
    ],
    "operationalHighlights": ["string"],
    "operationalShortfalls": ["string"]
  },

  "financialState": {
    "departmentalExpenditureLimit": "string or null",
    "capitalDel": "string or null",
    "resourceDel": "string or null",
    "underspendOrOverspend": "string or null",
    "reserves": "string or null",
    "fiscalPressureSignals": ["string — going-concern statements, unfunded liabilities, contingent liabilities flagged"],
    "savingsAchieved": ["string — named savings programmes and amounts"],
    "savingsTargets": ["string — savings targets disclosed for upcoming years"]
  },

  "governanceAndRisk": {
    "principalRisks": [
      {
        "riskName": "string",
        "description": "string",
        "rating": "string or null",
        "mitigations": "string or null",
        "yearOnYearChange": "new | rising | stable | falling | resolved | null"
      }
    ],
    "internalAuditConclusion": "string or null — overall opinion (e.g. 'moderate', 'limited', 'unsatisfactory')",
    "externalAuditQualification": {
      "qualified": "boolean",
      "qualificationDescription": "string or null",
      "areasOfConcern": ["string"]
    },
    "namedControlWeaknesses": ["string"],
    "irregularityOrLossDisclosures": ["string — any reportable losses, frauds, or special payments"]
  },

  "majorContractsAndSuppliers": [
    {
      "supplierName": "string",
      "scope": "string",
      "value": "string or null",
      "contractStatus": "active | terminated | extended | renegotiated | null",
      "narrativeContext": "string or null — why mentioned in the report"
    }
  ],

  "strategicForeword": {
    "headlineNarrative": "string — Permanent Secretary's framing of the year",
    "namedAchievements": ["string"],
    "namedChallenges": ["string"],
    "forwardLookCommitments": ["string — what they say next year will deliver"],
    "languageAndFraming": ["string — distinctive terms or framings used"]
  },

  "publicCommitments": [
    {
      "statement": "string — direct quote from the report",
      "speaker": "string — typically Permanent Secretary",
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
    "principalRisksCaptured": "number — must equal count in the report",
    "majorProgrammesCaptured": "number",
    "boardChangesCaptured": "number",
    "auditQualificationCaptured": "boolean",
    "unextractedSections": ["string — sections deliberately skipped, with reason"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `scaleAndShape.totalExpenditure` | `buyerSnapshot.annualBudget` | mandate | replace (annual report is authoritative) |
| `scaleAndShape.headcount.total` | `buyerSnapshot.headcount` | mandate | replace |
| `leadership.permanentSecretaryOrCEO` + `boardChanges` | `organisationContext.seniorLeadership` | mandate | extend or replace |
| `leadership.boardChanges[]` | `organisationContext.recentChanges` | mandate, pressure | extend |
| `performance.kpiResults` | `strategicPriorities.servicePerformancePressures` (where missed) | pressure | extend |
| `performance.majorProgrammeStatus[]` (where amber/red) | `risksAndSensitivities.programmeFailures` | risk-posture | extend |
| `performance.majorProgrammeStatus[]` (any) | `strategicPriorities.majorProgrammes[].status` | pressure | upgrade (annual report is more current than the strategy doc) |
| `financialState.fiscalPressureSignals` | `strategicPriorities.fiscalPressures` | pressure, money | extend |
| `financialState.savingsTargets` | `commissioningContextHypotheses.pressuresShapingSpend` | money, pressure | extend |
| `governanceAndRisk.principalRisks[]` | `risksAndSensitivities.summaryNarrative` (synthesise across) | risk-posture | extend |
| `governanceAndRisk.externalAuditQualification` | `risksAndSensitivities.auditFindings` | risk-posture | extend |
| `governanceAndRisk.namedControlWeaknesses` | `commercialAndRiskPosture.auditFoiExposure` | risk-posture | extend |
| `majorContractsAndSuppliers[]` | `supplierEcosystem.incumbents[]` | supplier-landscape | extend (with vulnerability signals if context is negative) |
| `strategicForeword.languageAndFraming` | `cultureAndPreferences.languageAndFraming` | risk-posture | extend |
| `publicCommitments[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `fullRead: false` in deep mode for a report >50 pages.
2. `governanceAndRisk.principalRisks` is empty — annual reports always have
   a principal-risks register.
3. `governanceAndRisk.externalAuditQualification.qualified` is null —
   the auditor's opinion must be captured (qualified or not).
4. `leadership.permanentSecretaryOrCEO.name` is null — the foreword author
   is always named.
5. `pursuitImplications[]` is empty — annual reports always carry
   implications. Common ones: any audit qualification → "over-evidence
   the qualified area"; any red programme → "demonstrate delivery
   confidence in adjacent programmes"; new permanent secretary → "engage
   on incoming priorities".
