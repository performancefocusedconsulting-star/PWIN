# Extraction Template — NAO / PAC / Select Committee Report

This template is loaded when a source is classified as `audit_report` or
`parliamentary` (specifically: NAO value-for-money reports, PAC reports,
departmental select committee reports, and equivalent devolved scrutiny —
WAO, Audit Scotland, NIAO).

External-scrutiny reports are the highest-yield single source for the
`risk-posture`, `pressure`, and `pursuit-implications` lenses, and they
are often the only authoritative public source of incumbent-supplier
distress signals.

---

## When to apply this template

Apply when the source is any of:

- An NAO Value-for-Money report
- A PAC report
- A Departmental Select Committee report (e.g. Treasury Committee, Health
  and Social Care Committee)
- A Wales Audit Office (WAO), Audit Scotland, or NIAO equivalent report
- An Independent Review or Commission report covering the buyer

Do not apply this template to:

- Inspectorate reports (CQC, Ofsted, HMICFRS, HMIP) — those are operational
  inspections, not value-for-money scrutiny
- Internal audit summaries — covered by the annual-report template

---

## Extraction depth requirement

NAO reports are typically 40–80 pages. PAC reports are typically 30–60
pages. In deep mode, the extraction must be end-to-end — the most valuable
content (named suppliers, specific failure narratives, departmental
responses) is often in the body of the report, not the executive summary.

---

## Template schema

```json
{
  "extractionType": "nao_pac_report",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string",
    "publisher": "NAO | PAC | select-committee | WAO | audit-scotland | NIAO | independent-review",
    "publicationDate": "ISO 8601",
    "buyerName": "string — the buyer being scrutinised",
    "scope": "string — what specifically was scrutinised (a programme, a category of spend, a service)",
    "totalPages": "number",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "subjectOfScrutiny": {
    "programmeOrService": "string",
    "valueOrSpendInScope": "string or null",
    "periodCovered": "string",
    "scopeBoundary": "string — what was and wasn't in scope of the scrutiny"
  },

  "findings": [
    {
      "finding": "string — what the report concludes",
      "type": "fact | evaluative-judgement",
      "severity": "fundamental | significant | material | minor",
      "evidenceCited": "string — what evidence the report bases this on"
    }
  ],

  "valueForMoneyJudgement": {
    "overall": "string — e.g. 'good value', 'mixed value', 'poor value', 'cannot conclude'",
    "byComponent": [
      { "component": "string", "judgement": "string", "rationale": "string" }
    ],
    "keyDriversOfPoorValue": ["string — where applicable"]
  },

  "costAndScheduleAnalysis": {
    "originalBudget": "string or null",
    "currentBudget": "string or null",
    "spendToDate": "string or null",
    "costOverrun": "string or null — % and absolute",
    "originalEndDate": "string or null",
    "currentEndDate": "string or null",
    "scheduleSlippage": "string or null"
  },

  "supplierIssues": [
    {
      "supplierName": "string — exactly as named in the report",
      "contractValue": "string or null",
      "contractStatus": "active | terminated | expired | renegotiated | unknown",
      "issuesIdentified": ["string"],
      "rootCauseAttribution": "supplier | buyer | shared | structural | unclear",
      "consequencesForBuyer": "string",
      "vulnerabilityForChallenger": "string — what this means for a competitor wanting to displace"
    }
  ],

  "departmentalResponse": {
    "recommendationsIssued": "number",
    "recommendationsAccepted": "number",
    "recommendationsPartiallyAccepted": "number",
    "recommendationsRejected": "number",
    "namedRejections": [
      { "recommendation": "string", "departmentResponse": "string" }
    ],
    "remedialActionsCommitted": ["string"],
    "remedialActionsTimeline": "string or null"
  },

  "lessonsLearnedThemes": [
    {
      "theme": "string — e.g. 'unrealistic delivery confidence', 'weak commercial controls', 'inadequate workforce planning'",
      "occursIn": "string — which programmes / functions",
      "isRecurring": "boolean — true if NAO/PAC have flagged this in prior reports for this buyer"
    }
  ],

  "namedRoles": [
    {
      "name": "string",
      "role": "string",
      "context": "string — typically the SRO, Permanent Secretary, or named accountable officer"
    }
  ],

  "languageAndFraming": {
    "criticalLanguage": ["string — phrases the report uses pejoratively about the buyer"],
    "endorsedLanguage": ["string — what the report frames positively, if anything"],
    "rejectedClaims": ["string — buyer claims the report tested and found wanting"]
  },

  "pursuitImplications": [
    {
      "implication": "string — buyer-derived, bidder-neutral; what any future bidder against this buyer should observe in light of this report",
      "category": "stance | language | evidence | commercial | engagement | risk-management | timing | structural",
      "rationale": "string"
    }
  ],

  "dossierMappings": [
    {
      "extractedPath": "string",
      "mapsToDossierField": "string",
      "operation": "extend | replace | upgrade",
      "lens": "risk-posture | pressure | supplier-landscape | pursuit-implications",
      "answersFrameworkQuestions": ["string"],
      "closesActionIds": ["string or null"]
    }
  ],

  "extractionQualityCheck": {
    "fullRead": "boolean",
    "findingsCaptured": "number — must equal count of distinct findings in the report",
    "supplierIssuesCaptured": "number — every named supplier with reported issues must be captured",
    "recommendationsCaptured": "boolean",
    "departmentalResponseCaptured": "boolean — must be true if the report includes one",
    "unextractedSections": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `findings[]` (fundamental / significant) | `risksAndSensitivities.auditFindings` | risk-posture | extend |
| `valueForMoneyJudgement.overall` (where poor) | `risksAndSensitivities.summaryNarrative` (input to synthesis) | risk-posture | extend |
| `costAndScheduleAnalysis` (where overrun > 10% or slippage > 6 months) | `risksAndSensitivities.programmeFailures` | risk-posture | extend |
| `supplierIssues[]` | `supplierEcosystem.incumbents[].vulnerabilitySignals.auditFindings` | supplier-landscape | extend |
| `supplierIssues[].issuesIdentified` (for terminated contracts) | `supplierEcosystem.incumbents[].vulnerabilitySignals.cancelledContracts` | supplier-landscape | extend |
| `supplierIssues[].vulnerabilityForChallenger` | `supplierEcosystem.switchingEvidence` | supplier-landscape | extend |
| `subjectOfScrutiny.programmeOrService` | `strategicPriorities.majorProgrammes[].status` (degraded if scrutiny is negative) | pressure | upgrade |
| `lessonsLearnedThemes[]` (where `isRecurring: true`) | `cultureAndPreferences.changeMaturity.deliveryMaturity` | risk-posture | replace if degraded |
| `lessonsLearnedThemes[]` | `cultureAndPreferences.evidencePreferences` | risk-posture | extend |
| `departmentalResponse.namedRejections[]` | `cultureAndPreferences.governanceIntensity` (signals confidence-vs-deference) | risk-posture | extend |
| `namedRoles[]` (named SRO or accountable officer) | `decisionUnitAssumptions.businessOwnerRoles` | buying-behaviour | extend |
| `languageAndFraming.rejectedClaims` | `cultureAndPreferences.languageAndFraming.avoidLanguage` | risk-posture | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Special handling — recurring lessons

When `lessonsLearnedThemes[].isRecurring` is true (the same theme has been
flagged in prior NAO/PAC reports against the same buyer), the extraction
must produce a **high-priority pursuit implication** in the
`evidence` category. Recurring lessons are the strongest signal of a
cultural pattern the buyer cannot self-correct, and any pursuit must
over-evidence the affected area.

Example: if NAO has flagged "unrealistic delivery confidence" three years
running, a pursuit implication should read:

```
{
  "implication": "Over-evidence delivery confidence — NAO has flagged unrealistic delivery confidence in three consecutive reports (2023, 2024, 2026). Lead with delivery track record, not transformation ambition. Expect commercial-side scepticism on aggressive milestone commitments.",
  "category": "evidence",
  "rationale": "NAO recurring-theme pattern (3 reports, 3 years). Any new programme will inherit elevated assurance burden."
}
```

---

## Quality check rules

The extraction is rejected if:

1. `fullRead: false` in deep mode.
2. `findingsCaptured: 0` — NAO/PAC reports always have findings.
3. `valueForMoneyJudgement.overall` is null — there is always an overall
   judgement.
4. `supplierIssuesCaptured: 0` when the report names suppliers — supplier
   issues are the highest-value extraction for the supplier-landscape lens.
5. `departmentalResponse.recommendationsIssued: 0` — NAO and PAC reports
   always issue recommendations.
6. `pursuitImplications[]` empty — every external-scrutiny report carries
   implications, especially around evidence and language.

---

## Cross-template note

When this template runs alongside the `digital-strategy` template (e.g.
NAO has scrutinised a digital programme that the strategy named), the
two should align:

- The strategy says "Single Customer Account will save £56m by FY28"
- The NAO report says "the £56m savings target rests on optimistic
  adoption assumptions and may be unachievable"

Both extractions should land in the dossier. The NAO finding adds a
`vulnerabilitySignal` against any incumbent on that programme, and a
pursuit implication that "any bidder must independently assure the
adoption-curve assumptions, not lift them from the strategy."

This is exactly the value of the seven-lens model: two different documents
contribute to different lenses (the strategy → Pressure / Money; the NAO
report → Risk posture / Pursuit implications), and the dossier holds both
without one overwriting the other.
