# Provenance Map Schema — Pursuit-to-Gate Orchestration v1.0

The provenance map is produced in phase 7 (gate pack) using the HANDOFF pack,
the HANDBACK manifest, and the phase 7 Forensic Auditor verdict.
It is included as the "Intelligence Provenance" section of the gate pack.

## Purpose

The provenance map answers three questions for the gate audience:
1. What intelligence did the bid team synthesise from?
2. Did synthesis use what was available?
3. Are the strategy claims traceable to source?

## JSON Schema

```json
{
  "provenanceMap": {
    "pursuitId": "string",
    "generatedAt": "ISO8601",
    "handoffPackGeneratedAt": "ISO8601",
    "handbackManifestDate": "YYYY-MM-DD",
    "assetsAvailableAtHandoff": [
      {
        "assetType": "string",
        "subjectName": "string",
        "version": "x.y.z",
        "auditVerdict": "green | amber | red | pending"
      }
    ],
    "assetsUsedInSynthesis": [
      {
        "assetType": "string",
        "subjectName": "string",
        "version": "string",
        "sectionsInformed": ["string"]
      }
    ],
    "assetsAvailableButNotUsed": [
      {
        "assetType": "string",
        "subjectName": "string",
        "agentReason": "string | null"
      }
    ],
    "winThemeTraceability": [
      {
        "themeId": "WT-1",
        "themeName": "string",
        "sourceAssets": ["buyer_dossier: <clientName>"],
        "traceabilityStatus": "full | partial | untraced",
        "auditNote": "string | null"
      }
    ],
    "flagsRaisedBySynthesis": [
      {
        "questionId": "OQ-1",
        "question": "string",
        "surfacedToConsultant": true,
        "consultantResponse": "string | null"
      }
    ],
    "phase7AuditVerdict": "green | amber | red | pending",
    "phase7AuditActions": ["string"],
    "overallProvenanceRating": "strong | adequate | weak",
    "overallProvenanceRationale": "string"
  }
}
```

## Overall provenance rating rules

| Rating | Condition |
|---|---|
| `strong` | Phase 7 audit green; all win themes fully traceable; all flags handled |
| `adequate` | Phase 7 audit amber; at least one win theme partially traceable; all flags surfaced |
| `weak` | Phase 7 audit red; one or more win themes untraced; or flags not surfaced to consultant |

## Markdown presentation in the gate pack

```
INTELLIGENCE PROVENANCE

Assets available at HANDOFF:       [N] assets — [N green / N amber / N red]
Assets used in synthesis:          [N of N available]
Assets available but unused:       [N] — [list if any]

Win theme traceability:
  WT-1 [theme name]:  full     — sourced from [assets]
  WT-2 [theme name]:  partial  — [asset] informed but not cited
  WT-3 [theme name]:  untraced — no source asset identified (see RISK-00N)

Phase 7 audit: [green/amber/red]
Overall provenance rating: [strong/adequate/weak]

[List audit actions if any remain open]
```
