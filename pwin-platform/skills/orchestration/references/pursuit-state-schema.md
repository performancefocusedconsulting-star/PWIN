# Pursuit State Schema — Pursuit-to-Gate Orchestration v1.0

## Where state lives

`~/.pwin/<pursuitId>/orchestration.json`

The folder `~/.pwin/<pursuitId>/` is the standard per-pursuit directory used by all
PWIN platform products. The orchestration skill adds one file to this directory.

## Version semantics

State uses a flat `"version": "1.0"` constant. This is not a versioned artefact — it is
a running record that is overwritten on each update. The pursuit brief, plan card, and gate
pack are the versioned deliverables. The state file is operational scaffolding only.

## Full JSON schema

```json
{
  "meta": {
    "version": "1.0",
    "skillName": "pursuit-to-gate",
    "pursuitId": "string",
    "createdAt": "ISO8601",
    "lastModifiedAt": "ISO8601"
  },
  "engagementScope": {
    "cutoffPhase": 7,
    "targetGateDate": "YYYY-MM-DD",
    "scopeRationale": "string"
  },
  "currentPhase": 1,
  "phaseStatuses": {
    "1": "pending | in_progress | complete",
    "2": "pending | in_progress | complete",
    "3": "pending | in_progress | complete",
    "4": "pending | parked | complete | out_of_scope",
    "5": "pending | delegated | complete | out_of_scope",
    "6": "pending | in_progress | complete | out_of_scope",
    "7": "pending | in_progress | complete | out_of_scope",
    "8": "pending | complete | out_of_scope"
  },
  "phaseArtifacts": {
    "1": {
      "brief": null
    },
    "2": {
      "planCard": null,
      "approvedAt": null,
      "approvedBy": null
    },
    "3": {
      "assembledAssets": [],
      "auditVerdicts": [],
      "handoffPackReady": false
    },
    "4": {
      "handoffPack": null,
      "handoffSentAt": null,
      "handbackManifest": null,
      "handbackReceivedAt": null
    },
    "5": {
      "delegateInput": null,
      "delegateSentAt": null,
      "returnPack": null,
      "returnReceivedAt": null
    },
    "6": {
      "roiModel": null
    },
    "7": {
      "gatePack": null,
      "provenanceMap": null,
      "phase7AuditVerdict": null,
      "signedOffAt": null
    },
    "8": {
      "handoffToMonitoringAt": null
    }
  }
}
```

## Phase status rules

| Phase | Status transitions |
|---|---|
| 1 | pending → in_progress → complete |
| 2 | pending → in_progress → complete (requires consultant approval) |
| 3 | pending → in_progress → complete (all assets assembled + audited) |
| 4 | pending → parked (at HANDOFF) → complete (at HANDBACK) OR out_of_scope |
| 5 | pending → delegated (at DELEGATE) → complete (at RETURN) OR out_of_scope |
| 6 | pending → in_progress → complete OR out_of_scope |
| 7 | pending → in_progress → complete (requires consultant sign-off) OR out_of_scope |
| 8 | pending → complete OR out_of_scope |

A phase is `out_of_scope` when its number exceeds `engagementScope.cutoffPhase`.

## Write discipline

The skill must write updated state to `orchestration.json` after every significant action:
- After collecting the phase 1 brief
- After consultant approval of the plan card (phase 2)
- After each dossier is assembled and audited (phase 3)
- When the HANDOFF pack is sent (phase 4)
- When the HANDBACK manifest is received (phase 4)
- When the DELEGATE input is sent (phase 5)
- When the RETURN pack is received (phase 5)
- After the ROI model is computed (phase 6)
- After the gate pack is assembled (phase 7)
- After consultant sign-off (phase 7)
- After handoff to monitoring (phase 8)

## Resume behaviour

When the skill is invoked and `orchestration.json` already exists:
1. Load the file.
2. Identify `currentPhase` and the phase's status.
3. Display: "Pursuit [clientName] is at phase [N] — [status]. [Next action]."
4. Ask: resume from here, or show the full plan card?
5. Do NOT restart from phase 1 unless the consultant explicitly requests it.

## Scope override

When the consultant says "extend scope to phase [N]" or "change engagement scope":
1. Update `engagementScope.cutoffPhase` and `engagementScope.scopeRationale`.
2. Recalculate which phases are `out_of_scope`.
3. Write state immediately.
4. Re-present the plan card with the new scope applied.
5. Do not replay completed phases — resume from the current position.

## Invocation surface

The skill is invoked conversationally from Claude Code. It triggers on:

- "start pursuit for [client]" → phase 1 (brief), new state
- "resume pursuit [id]" or "continue pursuit" → load state, resume
- "drive to gate" → phase 1 if no state, or resume
- "build the intelligence pack for [opportunity]" → phase 1 / 3
- "gate pack for [client]" → phase 7 if phases 1–6 complete
- "where are we on [pursuit]" → display current status from state
- "extend scope to phase [N]" → scope override

## Gate pack output file

The signed-off gate pack is written to `~/.pwin/<pursuitId>/gate-pack.json`.
This is the primary deliverable of the pursuit-to-gate skill. It is separate from
`orchestration.json` (which is operational state, not a deliverable).
