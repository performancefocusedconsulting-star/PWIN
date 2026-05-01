# Plan Card Schema — Pursuit-to-Gate Orchestration v1.0

The plan card is produced at the end of phase 2 and presented to the consultant for approval.
It is written to `phaseArtifacts.2.planCard` in `orchestration.json`.

## JSON Schema

```json
{
  "planCard": {
    "pursuitId": "string",
    "generatedAt": "ISO8601",
    "engagementScope": {
      "phasesInScope": [1, 2, 3, 6, 7],
      "cutoffPhase": 7,
      "targetGateDate": "YYYY-MM-DD",
      "scopeRationale": "Client engagement covers intel assembly and gate pack only"
    },
    "assetInventory": [
      {
        "assetType": "buyer_dossier | supplier_dossier | sector_brief | incumbency_analysis | stakeholder_map",
        "subjectName": "string",
        "state": "present_current | present_stale | absent",
        "version": "x.y.z | null",
        "lastBuilt": "YYYY-MM-DD | null",
        "refreshDue": "YYYY-MM-DD | null",
        "auditVerdict": "green | amber | red | pending | not_yet_run",
        "auditActions": ["string"]
      }
    ],
    "actionSequence": [
      {
        "sequenceNo": 1,
        "action": "build | refresh | audit | handoff_gate | delegate_gate | return_gate",
        "subject": "string",
        "dependsOn": [],
        "phase": 3,
        "notes": "string | null"
      }
    ],
    "decisionGates": [
      {
        "gateType": "HANDOFF | HANDBACK | DELEGATE | RETURN",
        "afterPhase": 3,
        "beforePhase": 4,
        "criteria": "string",
        "humanRequired": true
      }
    ],
    "openRisks": [
      {
        "riskId": "RISK-001",
        "description": "string",
        "impact": "high | medium | low",
        "humanAction": "string"
      }
    ],
    "consultantApproval": {
      "approvedBy": "string | null",
      "approvedAt": "ISO8601 | null",
      "notes": "string | null"
    }
  }
}
```

## Asset state rules

| State | Condition |
|---|---|
| `present_current` | File found at `~/.pwin/intel/<type>/` and `meta.refreshDue >= today` |
| `present_stale` | File found but `meta.refreshDue < today` |
| `absent` | No file found for this type + slug combination |

## Action sequence rules

- Buyer dossier and sector brief: no dependencies
- Supplier dossiers: no dependencies (can run in parallel with buyer)
- Incumbency analysis: depends on both the buyer dossier and the relevant supplier dossier
- Audit actions: depend on the preceding build or refresh for the same asset
- HANDOFF gate: depends on all audit actions being resolved

## Markdown presentation format

When presenting the plan card to the consultant, use this format:

```
PLAN CARD — [clientName] pursuit
Scope: phases 1–[cutoffPhase] | Gate target: [targetGateDate]

Asset inventory:
  #  Asset                         State             Action     Depends on
  1  Buyer dossier ([client])      absent            build      —
  2  Sector brief ([sector])       present_current   audit      —
  3  Supplier: [competitor]        present_stale     refresh    —
  4  Incumbency ([comp]/[client])  absent            build      1, 3

Action sequence:
  Step 1: Build buyer dossier → then audit (step 5)
  Step 2: Sector brief audit (no build needed)
  Step 3: Refresh [competitor] dossier → then audit (step 6)
  Step 4: Build incumbency (after steps 1, 3 complete) → then audit (step 7)
  Step 5: Audit buyer dossier [Forensic Auditor]
  Step 6: Audit [competitor] dossier [Forensic Auditor]
  Step 7: Audit incumbency [Forensic Auditor]
  Gate: HANDOFF — all assets present and audit-cleared; consultant signs off

Open risks:
  RISK-001 [high]: ...

Confirm to proceed? (y to approve, or list changes needed)
```
