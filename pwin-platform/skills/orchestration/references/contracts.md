# Authority Boundary Contracts — Pursuit-to-Gate Orchestration v1.0

These contracts govern the four handoff points in the pursuit-to-gate workflow. Every contract specifies:
who produces the pack, what is in it, who receives it, and what the receiver must do with it.

---

## 1. HANDOFF (end of phase 3 → start of phase 4)

**Producer:** Orchestrator (after all dossiers are assembled and audit-cleared)
**Receiver:** Agent 3 (Win Strategy Analyst) + consultant + bid team

### Contract: what the orchestrator presents

```json
{
  "handoffPack": {
    "packVersion": "1.0",
    "generatedAt": "ISO8601",
    "pursuitId": "string",
    "engagementScope": {
      "cutoffPhase": 7,
      "targetGateDate": "YYYY-MM-DD",
      "scopeRationale": "string"
    },
    "pursuitBrief": {
      "clientName": "string",
      "opportunityName": "string | null",
      "sector": "string",
      "opportunityType": "string",
      "namedCompetitors": ["string"],
      "targetGateDate": "YYYY-MM-DD",
      "tcvEstimate": "string | null",
      "notes": "string | null"
    },
    "intelligencePack": [
      {
        "assetType": "buyer_dossier | supplier_dossier | sector_brief | incumbency_analysis",
        "subjectName": "string",
        "filePath": "~/.pwin/intel/<type>/<slug>-<artefact>.json",
        "version": "x.y.z",
        "auditVerdict": "green | amber | red | pending",
        "auditActions": ["string"],
        "consultantDecision": "proceed | proceed_with_caveats | re-run | null"
      }
    ],
    "stakeholderMap": null
  }
}
```

### Terms Agent 3 must accept before synthesis begins

1. All strategy synthesis (win themes, competitive positioning, capture plan) is owned by Agent 3 and the consultant — the orchestrator has no authority over strategy outputs.
2. When synthesis is complete, the consultant signs off and the team returns a HANDBACK manifest conforming to section 2 of this contract.
3. The manifest must include `assetsUsedInSynthesis` — every intelligence asset actually used (not just available). This is required for the phase 7 provenance map.

---

## 2. HANDBACK (end of phase 4 → orchestrator resumes)

**Producer:** Agent 3 + consultant (signed off by the consultant)
**Receiver:** Orchestrator

### Contract: what Agent 3 and the consultant must return

```json
{
  "handbackManifest": {
    "manifestVersion": "1.0",
    "signedOffAt": "ISO8601",
    "signedOffBy": "string",
    "pursuitId": "string",
    "synthesisArtefacts": {
      "winThemes": [
        {
          "themeId": "WT-1",
          "themeName": "string",
          "themeStatement": "string",
          "proofPoints": ["string"],
          "sourceAssets": ["buyer_dossier: <clientName>", "sector_brief: <sector>"]
        }
      ],
      "competitivePositioning": {
        "positioningStatement": "string",
        "competitorResponsePlans": [
          {
            "competitorName": "string",
            "displacementNarrative": "string",
            "sourceAssets": ["string"]
          }
        ]
      },
      "stakeholderMap": {},
      "buyerValues": ["string"],
      "clientIntelligenceNotes": "string",
      "capturePlanStatus": "draft | locked",
      "capturePlanSummary": "string"
    },
    "openQuestionsFromSynthesis": [
      {
        "questionId": "OQ-1",
        "question": "string",
        "raisedBy": "Agent 3",
        "requiresConsultantAction": true
      }
    ],
    "caveatsFromSynthesis": ["string"],
    "assetsUsedInSynthesis": [
      {
        "assetType": "string",
        "subjectName": "string",
        "version": "string",
        "sectionsInformed": ["string"]
      }
    ]
  }
}
```

### Terms the orchestrator must accept on HANDBACK

1. The orchestrator records the manifest verbatim. It does NOT re-evaluate strategic conclusions.
2. It surfaces all `openQuestionsFromSynthesis` to the consultant for resolution.
3. It uses `assetsUsedInSynthesis` as the evidence base for the phase 7 provenance map.

---

## 3. DELEGATE (orchestrator → start of phase 5)

**Producer:** Orchestrator
**Receiver:** Qualify product

### Contract: what the orchestrator passes to Qualify

```json
{
  "delegateInput": {
    "pursuitId": "string",
    "context": "orchestrated_pursuit_phase5",
    "pursuitBrief": {
      "clientName": "string",
      "sector": "string",
      "opportunityType": "string",
      "tcvEstimate": "string | null",
      "targetGateDate": "YYYY-MM-DD"
    },
    "winThemesSummary": ["string"],
    "buyerValues": ["string"],
    "competitiveContextSummary": "string",
    "stakeholderMaturitySummary": "string | null"
  }
}
```

### Terms Qualify must accept

1. Qualify runs its own AI + consultant assurance pattern (Alex Mercer). The orchestrator does not supervise or re-score.
2. When the Qualify run is complete, the consultant returns the RETURN pack conforming to section 4 of this contract.

---

## 4. RETURN (end of phase 5 → start of phase 6)

**Producer:** Qualify product (via consultant)
**Receiver:** Orchestrator

### Contract: what Qualify returns

```json
{
  "returnPack": {
    "returnedAt": "ISO8601",
    "pursuitId": "string",
    "pwinScore": 0.0,
    "verdict": "Pursue | Condition | Walk Away",
    "categoryBreakdown": {
      "clientPriority": 0.0,
      "pursuitIntelligence": 0.0,
      "solutionStrength": 0.0,
      "ourIntelligence": 0.0,
      "valueProposition": 0.0,
      "pricingPosition": 0.0
    },
    "conditionalAsks": ["string"],
    "reviewNarrative": "string",
    "runDate": "YYYY-MM-DD"
  }
}
```

---

## 5. Forensic Intelligence Auditor call interface

The orchestrator calls the Forensic Intelligence Auditor at two points. This section defines the call interface the auditor must implement when built. Until it exists, the orchestrator degrades gracefully.

### Phase 3 call — per-dossier audit

**Orchestrator passes:**
```json
{
  "auditRequest": {
    "callPoint": "phase3_dossier",
    "dossierType": "buyer_dossier | supplier_dossier | sector_brief | incumbency_analysis",
    "subjectName": "string",
    "dossierJson": { },
    "pursuitContext": {
      "clientName": "string",
      "sector": "string",
      "opportunityType": "string"
    }
  }
}
```

**Auditor returns:**
```json
{
  "auditResult": {
    "dossierType": "string",
    "subjectName": "string",
    "verdict": "green | amber | red",
    "flagCount": { "amber": 0, "red": 0 },
    "actions": ["string"],
    "auditedAt": "ISO8601"
  }
}
```

### Phase 7 call — gate pack input check

**Orchestrator passes:**
```json
{
  "auditRequest": {
    "callPoint": "phase7_gate_pack",
    "handoffPack": { },
    "handbackManifest": { },
    "returnPack": { }
  }
}
```

**Auditor returns:**
```json
{
  "auditResult": {
    "verdict": "green | amber | red",
    "provenanceAudit": {
      "assetsAvailableAtHandoff": ["string"],
      "assetsUsedBySynthesis": ["string"],
      "assetsAvailableButNotUsed": ["string"],
      "traceable": ["string"],
      "untraced": ["string"],
      "flagsHandled": ["string"],
      "flagsUnhandled": ["string"]
    },
    "actions": ["string"],
    "auditedAt": "ISO8601"
  }
}
```

### Degraded mode (auditor not yet built)

If the Forensic Intelligence Auditor skill is not available, the orchestrator:
1. Sets `auditVerdict: "pending"` for the affected dossier or gate-pack check.
2. Surfaces this to the consultant: "Forensic Intelligence Auditor not yet available. Manual review required before proceeding past this gate."
3. Records the consultant's decision (proceed manually / hold).
4. Does not advance the phase until the consultant explicitly authorises progression.

---
