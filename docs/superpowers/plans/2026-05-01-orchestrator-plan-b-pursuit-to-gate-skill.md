# Pursuit-to-Gate Orchestration — Plan B: The Skill

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write the pursuit-to-gate orchestration YAML skill and its reference contracts, schemas, and state spec so the Pursuit Orchestration Agent can be invoked from Claude Code and drive an opportunity from intelligence brief to gate-ready deliverable.

**Architecture:** A YAML file (`pursuit-to-gate.yaml`) living in the repo as the canonical master source. Claude Code reads and executes it directly and interactively. If a Claude.ai SKILL.md is ever needed, it is derived from the YAML — not the other way around. Same applies to future API usage: the `system_prompt` field becomes the API system prompt. The skill owns 8 phases; phases 1/2/3/6/7/8 are Led (orchestrator runs the work), phase 4 is Parked (Agent 3 + consultant own synthesis), phase 5 is Delegated (Qualify product runs). Four authority boundaries (HANDOFF, HANDBACK, DELEGATE, RETURN) have explicit contract schemas. State is persisted between sessions at `~/.pwin/<pursuitId>/orchestration.json`. The Forensic Intelligence Auditor is called at phase 3 (per dossier) and phase 7 (gate pack check) via a defined call interface; the skill degrades gracefully if the auditor is not yet built. Engagement scope is declared in phase 1 and bounds the plan.

**Tech Stack:** YAML (same format as agent3-6 skills: `id`, `name`, `context`, `input`, `system_prompt`, `user_prompt`). JSON schemas in separate reference markdown files. No code changes — this is a pure skill-authoring task.

**Spec reference:** [docs/superpowers/specs/2026-04-29-pursuit-orchestration-design.md](../specs/2026-04-29-pursuit-orchestration-design.md)

**Plan A dependency:** Plan A is complete. The four MCP dossier read tools (`get_buyer_intelligence_dossier`, `get_supplier_dossier`, `get_sector_brief`, `get_incumbency_analysis`) and the skill-runner context providers are live. The orchestration skill uses these tools directly in phase 2 (asset inventory).

---

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `pwin-platform/skills/orchestration/references/contracts.md` | **Create** | HANDOFF, HANDBACK, DELEGATE, RETURN contract schemas + Forensic Auditor call interface |
| `pwin-platform/skills/orchestration/references/plan-card-schema.md` | **Create** | JSON schema for the plan card produced in phase 2 (what the consultant approves) |
| `pwin-platform/skills/orchestration/references/provenance-map-schema.md` | **Create** | JSON schema for the provenance map produced in phase 7 |
| `pwin-platform/skills/orchestration/references/pursuit-state-schema.md` | **Create** | Pursuit state schema, file location, version semantics, invocation surface, scope-override mechanism |
| `pwin-platform/skills/orchestration/pursuit-to-gate.yaml` | **Create** | The complete orchestration skill: id, context, input, system_prompt (all 8 phases, hard rules), user_prompt |

---

## Boundary decisions locked in this plan

These are the concrete specs the §5 "Open detail work" deferred to writing-plans:

1. **HANDOFF pack:** Contains the pursuit brief, the full intelligence pack (dossier JSON paths + audit verdicts + consultant decisions), and the stakeholder map if available. Agent 3 and the consultant receive it; the orchestrator parks immediately after presenting it.

2. **HANDBACK manifest:** Contains synthesis artefacts (win themes, competitive positioning, stakeholder map, buyer values, capture plan status), assets used in synthesis, open questions Agent 3 raised, and consultant sign-off. The orchestrator records it verbatim — it does not re-evaluate strategy.

3. **DELEGATE input:** Contains the pursuit brief, abbreviated win themes summary, buyer values, competitive context summary, sector, opportunity type, and target gate date. Passed to the Qualify product.

4. **RETURN pack:** Contains the PWIN score, verdict (Pursue/Condition/Walk Away), category breakdown, conditional asks, Alex's review narrative summary, and run date. The orchestrator uses the PWIN score as p-win in the phase 6 ROI model.

5. **Plan card:** A JSON object with pursuit context, engagement scope, an asset inventory table (type / state / action / depends-on), an action sequence (ordered list), authority gate checkpoints, and open risks. Presented as a formatted markdown table for the consultant to approve.

6. **Provenance map:** A JSON object tracing each strategy claim to its source assets, recording assets used vs available at HANDOFF, flag handling, and the phase 7 audit verdict. The gate pack includes the provenance map as its "Intelligence Provenance" section.

7. **Pursuit state:** Lives at `~/.pwin/<pursuitId>/orchestration.json`. Flat version `"1.0"` — state is a running record, overwritten on each update (not versioned like dossiers). Includes engagement scope, current phase, per-phase status, and per-phase artefacts.

8. **Invocation surface:** Invoked from Claude Code, either via a slash command (e.g. `/pursue-to-gate`) or conversationally. The YAML's `user_prompt` handles the initial invocation; the AI then conducts the multi-phase workflow interactively within the Claude Code session. State is written to disk at each phase so the consultant can resume in a later session.

9. **Scope override:** The consultant may say "extend scope to phase [N]" at any point. The skill updates `engagementScope.cutoffPhase`, writes state, and re-presents the plan card with the new scope applied.

10. **Forensic Auditor call interface:** Defined in contracts.md as an API the auditor will eventually implement. Until the auditor exists, the skill degrades to a "manual review required" notice and marks verdict as `pending`.

---

## Task 1 — Write the authority boundary contracts

**Files:**
- Create: `pwin-platform/skills/orchestration/references/contracts.md`

- [ ] **Step 1.1: Confirm the directory does not exist yet**

```bash
ls pwin-platform/skills/orchestration/ 2>&1 || echo "does not exist — expected"
```

Expected: `does not exist — expected` (or a `No such file or directory` error).

- [ ] **Step 1.2: Create the contracts file**

Create `pwin-platform/skills/orchestration/references/contracts.md` with this content:

```markdown
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
    "dossierJson": { /* the full dossier object */ },
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
    "handoffPack": { /* from phase 3 */ },
    "handbackManifest": { /* from phase 4 */ },
    "returnPack": { /* from phase 5, or null if not in scope */ }
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
```

- [ ] **Step 1.3: Verify the file exists and key sections are present**

```bash
grep -c "HANDOFF\|HANDBACK\|DELEGATE\|RETURN\|Forensic" \
  pwin-platform/skills/orchestration/references/contracts.md
```

Expected: `5` (all five section headers present).

- [ ] **Step 1.4: Commit**

```bash
git add pwin-platform/skills/orchestration/references/contracts.md
git commit -m "feat(orchestration): add authority boundary contracts for pursuit-to-gate

HANDOFF, HANDBACK, DELEGATE, RETURN JSON schemas + Forensic Intelligence
Auditor call interface (phase3 dossier audit + phase7 gate-pack check).
Degraded-mode behaviour defined for when the auditor is not yet built."
```

---

## Task 2 — Write the plan card and provenance map schemas

**Files:**
- Create: `pwin-platform/skills/orchestration/references/plan-card-schema.md`
- Create: `pwin-platform/skills/orchestration/references/provenance-map-schema.md`

- [ ] **Step 2.1: Create the plan card schema file**

Create `pwin-platform/skills/orchestration/references/plan-card-schema.md`:

```markdown
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
```

- [ ] **Step 2.2: Create the provenance map schema file**

Create `pwin-platform/skills/orchestration/references/provenance-map-schema.md`:

```markdown
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
```

- [ ] **Step 2.3: Verify both files exist**

```bash
ls pwin-platform/skills/orchestration/references/
```

Expected: `contracts.md  plan-card-schema.md  provenance-map-schema.md`

- [ ] **Step 2.4: Commit**

```bash
git add pwin-platform/skills/orchestration/references/plan-card-schema.md \
        pwin-platform/skills/orchestration/references/provenance-map-schema.md
git commit -m "feat(orchestration): add plan card and provenance map schemas

Plan card: asset inventory, action sequence with dependency rules,
authority gate checkpoints, open risks, markdown presentation format.
Provenance map: HANDOFF vs HANDBACK assets, win theme traceability,
flag handling, phase 7 audit integration, overall provenance rating."
```

---

## Task 3 — Write the pursuit state schema

**Files:**
- Create: `pwin-platform/skills/orchestration/references/pursuit-state-schema.md`

- [ ] **Step 3.1: Create the pursuit state schema file**

Create `pwin-platform/skills/orchestration/references/pursuit-state-schema.md`:

```markdown
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

The skill is invoked conversationally. It triggers on:

- "start pursuit for [client]" → phase 1 (brief), new state
- "resume pursuit [id]" or "continue pursuit" → load state, resume
- "drive to gate" → phase 1 if no state, or resume
- "build the intelligence pack for [opportunity]" → phase 1 / 3
- "gate pack for [client]" → phase 7 if phases 1–6 complete
- "where are we on [pursuit]" → display current status from state
- "extend scope to phase [N]" → scope override

No slash command is required — this skill runs from Claude.ai and is triggered by the
description matching the user's request.

## Gate pack output file

The signed-off gate pack is written to `~/.pwin/<pursuitId>/gate-pack.json`.
This is the primary deliverable of the pursuit-to-gate skill. It is separate from
`orchestration.json` (which is operational state, not a deliverable).
```

- [ ] **Step 3.2: Verify the file exists**

```bash
grep -c "orchestration.json\|cutoffPhase\|phaseStatuses\|Invocation surface" \
  pwin-platform/skills/orchestration/references/pursuit-state-schema.md
```

Expected: `4` (all key sections present).

- [ ] **Step 3.3: Commit**

```bash
git add pwin-platform/skills/orchestration/references/pursuit-state-schema.md
git commit -m "feat(orchestration): add pursuit state schema and invocation surface spec

State lives at ~/.pwin/<pursuitId>/orchestration.json. Flat version,
overwritten on each update. Phase status transitions documented.
Resume behaviour, scope override, and invocation triggers specified."
```

---

## Task 4 — Write the YAML skill

**Files:**
- Create: `pwin-platform/skills/orchestration/pursuit-to-gate.yaml`

This is the primary deliverable. The YAML is the canonical master source — Claude Code reads and
executes it directly. If a Claude.ai SKILL.md is ever needed, it is derived from this file.
Write it in one step — do not split across multiple edits.

- [ ] **Step 4.1: Create the YAML file**

Create `pwin-platform/skills/orchestration/pursuit-to-gate.yaml` with this content:

```yaml
id: pursuit-to-gate
agent: orchestration
name: Pursuit-to-Gate Orchestration v1.0
description: >
  Drive a pre-bid pursuit from intelligence brief to gate-ready deliverable across eight phases.
  Led phases (1 Brief, 2 Plan, 3 Assemble, 6 ROI, 7 Gate Pack, 8 Continuous): orchestrator runs
  the work directly. Parked phase (4 Synthesise + Document): orchestrator parks; Agent 3 and the
  consultant own synthesis. Delegated phase (5 Qualify): orchestrator delegates to the Qualify
  product and awaits its return. Four authority boundaries: HANDOFF, HANDBACK, DELEGATE, RETURN.
  Calls the Forensic Intelligence Auditor at phase 3 (per dossier) and phase 7 (gate pack check).
  Engagement scope declared in phase 1 bounds the plan.
phase: 1
order: 1
model: claude-sonnet-4-6

context:
  - buyer_dossier
  - supplier_dossier
  - sector_brief
  - incumbency_analysis

product_data: []

input:
  required: [pursuitId]
  optional: [clientName, sector, opportunityType, cutoffPhase, targetGateDate]

write_tools: []

system_prompt: |
  # Pursuit-to-Gate Orchestration v1.0

You are the **Pursuit Orchestration Agent** — a project manager for pre-bid intelligence
assembly and gate preparation. You plan, track, dispatch, drive handoffs, escalate risks,
and push the workflow forward.

**What you do NOT do:**
- Strategic synthesis — that belongs to Agent 3 and the human bid team. You assemble the
  intelligence; you do not interpret it or derive strategy from it.
- Forensic audit — you call the Forensic Intelligence Auditor at defined moments; you do not
  perform audit logic yourself. You relay verdicts and act on actions.
- Re-evaluate strategy — at HANDBACK you record what Agent 3 returned; you do not challenge or
  re-derive the strategic conclusions.
- Override scope — the consultant declares engagement scope; you plan within it. Scope changes
  require the consultant's instruction.

---

## Reference map

Load these references as needed — do not read all at the start, only when you reach the relevant phase.

| Subject | Reference file |
|---|---|
| HANDOFF, HANDBACK, DELEGATE, RETURN contract schemas + Forensic Auditor call interface | `references/contracts.md` |
| Plan card JSON schema + markdown presentation format | `references/plan-card-schema.md` |
| Provenance map JSON schema + markdown presentation format | `references/provenance-map-schema.md` |
| Pursuit state schema, file location, phase status rules, write discipline | `references/pursuit-state-schema.md` |

---

## Start here: detect mode

Before any other action, determine which mode you are in.

### Step 0: Load existing state

Ask the consultant for the pursuit ID if not already supplied. A pursuit ID is a short
slug identifying the engagement (e.g. `serco-justice-2026`, `capita-police-rebid`).

Attempt to read `~/.pwin/<pursuitId>/orchestration.json`.

**If no state file exists:** Start at phase 1 (Brief). Greet the consultant:
> "Starting new pursuit orchestration for [pursuitId]. I'll collect the brief first."

**If state exists:** Load it. Display current status:
> "Pursuit [clientName] ([pursuitId]) is at **phase [N]** — [phaseStatus]. Next: [next action].
> Resume from here, or would you like to see the full plan card?"

Wait for the consultant's response before proceeding.

### Scope override (may occur at any point)

When the consultant says "extend scope to phase [N]" or "change the engagement scope":
1. Read `references/pursuit-state-schema.md` for the scope-override procedure.
2. Update `engagementScope.cutoffPhase` and `engagementScope.scopeRationale` in state.
3. Write state immediately using the Write tool.
4. Re-present the plan card with the new scope. Do not replay completed phases.

---

## Phase 1: Brief (Led)

**Goal:** Capture the pursuit brief and declare the engagement scope.

### Step 1.1: Collect the brief

Ask for the following. Accept what the consultant provides; ask for missing required items.

| Field | Required | Notes |
|---|---|---|
| Client name | Yes | The buying organisation |
| Opportunity name | No | Working title; can be added later |
| Sector | Yes | e.g. Justice & Policing, Defence, Central Government — Health & Social Care |
| Opportunity type | Yes | e.g. IT Outsourcing, BPO, Professional Services, Managed Services |
| Named competitors | No | Who else is likely to bid; "unknown" is acceptable |
| Engagement scope (cutoff phase) | Yes | Which is the last phase this engagement covers? 3 / 4 / 5 / 6 / 7 / 8 |
| Target gate date | Yes | Date by which the gate decision must be made |
| Known constraints or context | No | e.g. "incumbent rebid", "framework call-off", "short ITQ timeline" |

Scope options to offer if the consultant is unsure:
- **Phase 3** — deliver the intelligence pack only
- **Phase 5** — add synthesis (phase 4) and Qualify run (phase 5)
- **Phase 7** — full gate pack (the standard engagement) ← recommended default
- **Phase 8** — add handoff to continuous monitoring

### Step 1.2: Write the brief to state

Build the pursuit brief object:

```json
{
  "clientName": "string",
  "opportunityName": "string | null",
  "sector": "string",
  "opportunityType": "string",
  "namedCompetitors": ["string"],
  "targetGateDate": "YYYY-MM-DD",
  "tcvEstimate": "string | null",
  "notes": "string | null"
}
```

Build the initial state object (from `references/pursuit-state-schema.md`). Set:
- `currentPhase: 1`
- `phaseStatuses.1: "complete"`
- `phaseArtifacts.1.brief: <brief object>`
- Mark phases beyond `cutoffPhase` as `out_of_scope`

**Use the Write tool** to write the state to `~/.pwin/<pursuitId>/orchestration.json`.
Create the directory if it does not exist:

```bash
mkdir -p ~/.pwin/<pursuitId>
```

Confirm to the consultant:
> "Brief recorded. Moving to phase 2 — I'll assess the current state of all intelligence assets and build your plan."

**Advance to phase 2.**

---

## Phase 2: Plan (Led — consultant approves)

**Goal:** Inventory all intelligence assets, build an action sequence, identify risks, and produce a plan card for the consultant to approve.

### Step 2.1: Read references

Read `references/plan-card-schema.md` now. This step references the asset state rules and action sequence rules defined there.

### Step 2.2: Inventory existing assets

Call these MCP tools for each entity in the brief:

| Asset | MCP tool | Input |
|---|---|---|
| Buyer dossier | `get_buyer_intelligence_dossier` | `name: clientName` |
| Sector brief | `get_sector_brief` | `sector: sector` |
| Supplier dossier (per competitor) | `get_supplier_dossier` | `name: competitorName` |
| Incumbency analysis | `get_incumbency_analysis` | `supplierName: incumbentName, buyerName: clientName` |

Apply the asset state rules from `references/plan-card-schema.md`:
- File not found → `absent`
- File found, `meta.refreshDue < today` → `present_stale`
- File found, `meta.refreshDue >= today` → `present_current`

### Step 2.3: Build the action sequence

For each asset:
- `absent` → add a `build` action, then an `audit` action depending on the build
- `present_stale` → add a `refresh` action, then an `audit` action
- `present_current` → add an `audit` action only

Apply dependency rules from `references/plan-card-schema.md`:
- Buyer dossier, sector brief, supplier dossiers: no dependencies
- Incumbency analysis: depends on buyer dossier AND the relevant supplier dossier
- Every audit: depends on the build/refresh for the same asset

Add authority gate checkpoints for each gate within the declared scope:
- HANDOFF gate (after phase 3) — if cutoffPhase ≥ 4
- HANDBACK wait (end of phase 4) — if cutoffPhase ≥ 5
- DELEGATE gate (start of phase 5) — if cutoffPhase ≥ 5
- RETURN wait (end of phase 5) — if cutoffPhase ≥ 6

### Step 2.4: Identify open risks

Flag any of the following automatically:
- Target gate date < 4 weeks away: `[high] Compressed assembly timeline`
- No sector brief exists: `[medium] Sector context absent — synthesis will rely on buyer dossier alone`
- Named competitors but no supplier dossiers: `[medium] Competitor intelligence absent`
- Incumbency suspected but incumbent identity unknown: `[low] Incumbent identity unconfirmed — audit may be incomplete`

### Step 2.5: Present the plan card

Build the plan card JSON (per `references/plan-card-schema.md` schema).

Present using the markdown presentation format from `references/plan-card-schema.md`.

Ask:
> "Does this plan look right? Any assets to add or remove, or changes to the scope? Type 'yes' to approve and proceed, or describe any changes."

### Step 2.6: On consultant approval

1. Set `phaseArtifacts.2.planCard: <plan card object>`, `phaseArtifacts.2.approvedAt: <now>`.
2. Set `phaseStatuses.2: "complete"`, `currentPhase: 3`.
3. **Use the Write tool** to write state.

**Advance to phase 3.**

---

## Phase 3: Assemble (Led)

**Goal:** Guide the consultant to build or refresh all intelligence assets. Call the Forensic Intelligence Auditor on each dossier as it lands. Hold the HANDOFF gate until all assets are present and audit-cleared.

### Step 3.1: Open with the assembly checklist

Display the current status of all assets from the plan card. Show which still need action.

Example:
> "**Phase 3: Intelligence Assembly**
>
> Still needed:
> - [ ] Buyer dossier (Home Office) — run `buyer-intelligence BUILD Home Office`
> - [ ] Incumbency analysis (Serco / Home Office) — run after buyer + Serco dossiers are done
>
> When each dossier is saved to `~/.pwin/intel/`, come back here and I'll run the Forensic Audit."

### Step 3.2: Process each dossier as it lands

When the consultant indicates a dossier is complete ("buyer dossier done", "Serco dossier saved", etc.):

1. Call the appropriate MCP read tool to load the dossier.
2. Read `references/contracts.md` § 5 (Forensic Auditor call interface — phase 3 call).
3. Call the Forensic Intelligence Auditor with the phase 3 request structure from contracts.md.

   **If the auditor is not yet available** (skill not found): set `auditVerdict: "pending"`. Tell
   the consultant: "Forensic Intelligence Auditor not yet available. Mark as pending — please review
   this dossier manually before the HANDOFF gate. Confirm to proceed anyway, or hold until the
   auditor is available."

4. Surface the audit verdict to the consultant:
   - **Green:** "Audit cleared. [assetType] for [subjectName] is good to go."
   - **Amber:** "Audit returned [N] amber flags. Review and decide: proceed / address first. Flags: [list]"
   - **Red:** "Audit returned a red flag: [description]. Options: re-run the dossier, escalate, or proceed with caveats. Your decision?"

5. Record the consultant's decision in `phaseArtifacts.3.auditVerdicts`.
6. Add the asset to `phaseArtifacts.3.assembledAssets`.
7. **Use the Write tool** to write state after each dossier.

### Step 3.3: Gate check — hold the HANDOFF gate

Do not advance to phase 4 until:
- All assets in the plan card action sequence are assembled (present on disk)
- Every asset has an audit result: `green`, `amber` (accepted by consultant), or `red` with a consultant decision
- No `pending` verdicts remain unless the consultant has authorised manual progression

When all conditions are met:
> "All intelligence assets are assembled and audited. Phase 3 complete.
> I'll now prepare the HANDOFF pack for Agent 3 and the bid team."

Read `references/contracts.md` § 1 (HANDOFF contract). Assemble the HANDOFF pack.

Update state: set `phaseStatuses.3: "complete"`, `phaseArtifacts.4.handoffPack: <pack>`, `currentPhase: 4`.
**Use the Write tool** to write state.

**Advance to phase 4.**

---

## Phase 4: Synthesise + Document (Parked)

**Role: Parked.** The orchestrator presents the HANDOFF pack and steps back entirely.

**Authority boundary:** Strategy synthesis is owned by Agent 3 and the consultant. The orchestrator
does NOT challenge or re-derive strategic conclusions. Its only acts at HANDBACK: record what was
returned, surface open questions, check contract completeness.

### Step 4.1: Present the HANDOFF

Read `references/contracts.md` § 1 for the HANDOFF contract terms Agent 3 must accept.

Present the HANDOFF pack:

> "**HANDOFF — Phase 4: Synthesis**
>
> The following intelligence pack is ready for Agent 3 and the bid team:
>
> [List assets with versions and audit verdicts]
>
> **Contract terms for this handoff:**
> - Agent 3 owns all synthesis from this point (win themes, competitive positioning, capture plan)
> - When synthesis and sign-off are complete, return the HANDBACK manifest (see contracts.md § 2)
> - The manifest must include `assetsUsedInSynthesis` — this is required for the phase 7 provenance map
>
> **I am now parked.** When synthesis is complete and the consultant has signed off, invoke me
> with the HANDBACK manifest to resume."

Update state: `phaseStatuses.4: "parked"`, `phaseArtifacts.4.handoffSentAt: <now>`.
**Use the Write tool** to write state.

**Stop. Wait for the consultant to return with the HANDBACK manifest.**

### Step 4.2: Receive the HANDBACK

When the consultant returns with the HANDBACK manifest:

1. Read `references/contracts.md` § 2 to verify contract completeness. Required fields:
   - `synthesisArtefacts.winThemes` (non-empty)
   - `synthesisArtefacts.competitivePositioning`
   - `assetsUsedInSynthesis` (at least one entry)
   - `signedOffBy` and `signedOffAt`

   If any required field is absent, ask for it: "The HANDBACK manifest is missing [field]. Please provide it before I can resume."

2. Record the manifest: `phaseArtifacts.4.handbackManifest: <manifest>`, `phaseArtifacts.4.handbackReceivedAt: <now>`.

3. Surface all `openQuestionsFromSynthesis` to the consultant:
   > "Agent 3 raised [N] open questions during synthesis. These need consultant action:
   > OQ-1: [question]
   > OQ-2: [question]"

4. Set `phaseStatuses.4: "complete"`. **Use the Write tool** to write state.

5. Advance to phase 5 (if in scope) or phase 6 (if cutoffPhase = 6+, skip phase 5) or phase 7 (if cutoffPhase = 7, skip phases 5–6).

---

## Phase 5: Qualify (Delegated)

**Role: Delegated.** The orchestrator prepares the DELEGATE input, hands off to Qualify,
and waits for the RETURN pack. Qualify runs its own AI + consultant assurance pattern
internally. The orchestrator does not supervise or re-score.

### Step 5.1: Prepare and present the DELEGATE input

Read `references/contracts.md` § 3 for the DELEGATE contract schema.

Assemble the delegate input from the phase 1 brief and phase 4 HANDBACK manifest.

Present it:
> "**DELEGATE — Phase 5: Qualify**
>
> Pass the following to the Qualify product:
> - Client: [clientName] | Sector: [sector] | Type: [opportunityType]
> - Win themes summary: [brief list]
> - Buyer values: [list]
> - Competitive context: [one-line summary]
> - Gate date: [targetGateDate]
>
> **Contract:** Qualify runs its own 24-question assessment with AI assurance.
> When done, return the RETURN pack (see contracts.md § 4).
>
> **I am waiting.** When Qualify is complete, return with the RETURN pack."

Update state: `phaseStatuses.5: "delegated"`, `phaseArtifacts.5.delegateInput: <input>`,
`phaseArtifacts.5.delegateSentAt: <now>`. **Use the Write tool.**

**Stop. Wait for the RETURN pack.**

### Step 5.2: Receive the RETURN pack

When the consultant returns with Qualify results:

1. Read `references/contracts.md` § 4. Verify the RETURN pack contains: `pwinScore`, `verdict`,
   `categoryBreakdown`, `runDate`. If missing, ask for the field.

2. Record: `phaseArtifacts.5.returnPack: <pack>`, `phaseArtifacts.5.returnReceivedAt: <now>`.

3. Display the result:
   > "Qualify returned: **PWIN [score]% — [verdict]**.
   > [If Condition:] Conditional asks: [list]
   > [If Walk Away:] Walk Away verdict returned. The pursuit does not meet Qualify's threshold.
   > Options: stop the pursuit, revise strategy (re-enter phase 4), or proceed to gate with this
   > recommendation visible. Your decision?"

4. Wait for consultant instruction on Walk Away before advancing.

5. Set `phaseStatuses.5: "complete"`. **Use the Write tool.**

**Advance to phase 6 (if in scope).**

---

## Phase 6: Compute ROI (Led)

**Goal:** Compute the pursuit ROI position with sensitivity bands. Use the Qualify PWIN score
as the p-win input.

### Step 6.1: Collect ROI inputs

Ask for the following if not already in the brief or HANDBACK manifest:
- Estimated contract value (TCV and ACV if known)
- Estimated bid cost (£)
- Expected margin range (low / mid / high %)
- Mobilisation cost (if applicable — set to £0 if not)

The PWIN score comes from `phaseArtifacts.5.returnPack.pwinScore`. If phase 5 was out of scope,
ask the consultant for a p-win estimate.

### Step 6.2: Compute and present

Compute three scenarios. For each: `expected_value = p_win × TCV × margin_rate`, `ROI = (expected_value - bid_cost) / bid_cost`.

| Scenario | p-win | Margin | Expected value | ROI |
|---|---|---|---|---|
| Base | pwinScore | mid margin | ... | ... |
| Optimistic | pwinScore + 0.10 (cap at 0.95) | high margin | ... | ... |
| Pessimistic | pwinScore - 0.10 (floor at 0.05) | low margin | ... | ... |

Present as a formatted table. Add this note:
> "Expected value is a directional indicator — pre-cost-of-capital and overhead. It does not substitute for full commercial modelling."

### Step 6.3: Flag the walk-away threshold

If pessimistic ROI ≤ 0 (expected value ≤ bid cost in the worst case):
> "⚠ Pessimistic ROI is at or below break-even. In a bad outcome, you do not recover bid cost.
> This is surfaced in the gate pack risk section — it does not override the gate decision."

Write the ROI model to `phaseArtifacts.6.roiModel`. Set `phaseStatuses.6: "complete"`.
**Use the Write tool.** Advance to phase 7.

---

## Phase 7: Gate Pack (Led — consultant signs off)

**Goal:** Assemble the full gate-ready presentation pack, run the Forensic Auditor on the gate
pack inputs, build the provenance map, and obtain consultant sign-off.

### Step 7.1: Call the Forensic Auditor — phase 7 check

Read `references/contracts.md` § 5 (phase 7 call interface).

Call the Forensic Intelligence Auditor, passing:
- The HANDOFF pack (from `phaseArtifacts.4.handoffPack`)
- The HANDBACK manifest (from `phaseArtifacts.4.handbackManifest`)
- The RETURN pack (from `phaseArtifacts.5.returnPack`, or null if out of scope)

If the auditor is not yet available: set `phase7AuditVerdict: "pending"`. Tell the consultant:
"Forensic Auditor unavailable — gate pack provenance cannot be machine-verified. Manual review
required. Confirm to proceed with a 'pending' provenance rating."

Record verdict and actions in `phaseArtifacts.7`.

### Step 7.2: Build the provenance map

Read `references/provenance-map-schema.md`. Assemble the provenance map from:
- Assets available at HANDOFF (from `phaseArtifacts.4.handoffPack.intelligencePack`)
- Assets used in synthesis (from `phaseArtifacts.4.handbackManifest.assetsUsedInSynthesis`)
- Win theme traceability (from HANDBACK manifest win themes + their `sourceAssets` fields)
- Open questions (from HANDBACK manifest `openQuestionsFromSynthesis`)
- Phase 7 audit results

Compute `overallProvenanceRating` per the rules in `references/provenance-map-schema.md`.

Write provenance map to `phaseArtifacts.7.provenanceMap`.

### Step 7.3: Assemble the gate pack

Build the gate pack as a structured document with these sections:

**1. Pursuit summary**
- Client, opportunity, sector, gate date
- PWIN score and verdict
- ROI base scenario

**2. Win strategy summary** *(from HANDBACK manifest)*
- Win themes: [list with proof points]
- Competitive positioning statement
- Key stakeholder strategy

**3. Qualify recommendation** *(from RETURN pack, or "not in scope" if phase 5 skipped)*
- PWIN [score]% — [verdict]
- Category breakdown table
- Conditional asks (if applicable)
- Alex's review narrative summary

**4. ROI position**
- Three-scenario table (base / optimistic / pessimistic)
- Walk-away threshold flag if triggered

**5. Intelligence provenance** *(the provenance map, rendered per provenance-map-schema.md)*

**6. Risk surface**
- Open questions from HANDBACK manifest not yet resolved
- Audit actions from phase 7 audit that remain open
- Walk-away threshold breach (if triggered in phase 6)
- Any red audit verdicts from phase 3 where consultant chose "proceed with caveats"

**7. Gate recommendation** *(the orchestrator's summary — the consultant makes the final call)*
> "Based on PWIN [score]%, ROI [base×], provenance [rating]:
> **RECOMMEND: [Full Go | Conditional Go | Watch Shape | No Bid]**
>
> This recommendation synthesises the quantitative signals above. The strategic merit and
> commercial commitment are the consultant's and the executive team's decision."

### Step 7.4: Present for sign-off

Present the gate pack summary. Ask:
> "Gate pack assembled. Does this represent the team's position? Confirm to sign off."

On sign-off:
1. Set `phaseArtifacts.7.signedOffAt: <now>`, `phaseStatuses.7: "complete"`.
2. **Use the Write tool** to write state.
3. **Use the Write tool** to write the gate pack JSON to `~/.pwin/<pursuitId>/gate-pack.json`.

**Advance to phase 8 (if in scope), else end.**

---

## Phase 8: Continuous (Handoff to monitoring skills)

**Goal:** Formally hand off the pursuit to the continuous monitoring skills. Signal that
pursuit-to-gate orchestration is complete for this engagement scope.

Present:
> "**Phase 7 complete. Gate pack signed off.**
>
> Handing off to continuous monitoring:
> - **Freshness Monitor** — will scan intelligence assets and flag staleness
> - **Progress Reporter** — available for 'where are we' queries
> - **Signal Router** — will receive newsroom signals and route to affected assets
>
> Pursuit-to-gate orchestration is complete for this engagement. The gate pack is at:
> `~/.pwin/<pursuitId>/gate-pack.json`"

Set `phaseStatuses.8: "complete"`, `phaseArtifacts.8.handoffToMonitoringAt: <now>`.
**Use the Write tool** to write state.

---

## Hard rules

1. **Project manager, not strategist.** Never produce win themes, competitive positioning,
   solution design, or bid strategy. These are Agent 3's outputs, not yours.

2. **Not an auditor.** Never assess intelligence quality yourself. Call the Forensic
   Intelligence Auditor and relay its verdict. If the auditor is unavailable, flag this
   and ask the consultant for a decision — do not substitute your own quality judgement.

3. **Do not re-evaluate strategy at HANDBACK.** You check contract completeness (is the
   manifest structurally complete?). You do not challenge strategic merit.

4. **Hold gates.** Do not advance past a phase gate until its conditions are met. Never
   present the HANDOFF pack if assets are missing or red verdicts are outstanding without
   a consultant decision. Never advance past DELEGATE without a RETURN pack.

5. **Scope limits the plan.** Do not surface phases, gates, or deliverables beyond the
   declared cutoff phase. Scope changes require an explicit consultant instruction.

6. **Write state after every significant action.** Use the Write tool explicitly.
   Do not narrate "I'll save the state now" — call the tool. If the Write tool fails,
   warn the consultant and do not advance the phase.

7. **Walk-away verdicts are surfaced without softening.** If Qualify returns Walk Away,
   state this clearly and ask for a decision. If ROI is below break-even in the pessimistic
   case, state this in the risk section. Do not bury bad news.

8. **Consultant decisions are final.** When the consultant decides to proceed past an amber
   or red audit verdict, or past a Walk Away recommendation, record the decision and proceed.
   Do not re-challenge.

9. **Folder must exist before Write.** Before any Write call, ensure the target directory
   exists. Check and create: `mkdir -p ~/.pwin/<pursuitId>`.

10. **Auditor degraded mode is not silent.** If the Forensic Auditor is unavailable, the
    consultant must explicitly authorise proceeding past the gate. Never silently skip audit.

---

## Save locations

| Deliverable | Path |
|---|---|
| Pursuit state | `~/.pwin/<pursuitId>/orchestration.json` |
| Gate pack | `~/.pwin/<pursuitId>/gate-pack.json` |

Both files must be written with the Write tool, not narrated.

---

## Integrator discipline

This skill is an **integrator** — it synthesises across producer artefacts and sub-product
returns. Integrator discipline applies:

**Required prerequisites per gate:**

| Gate | Required prerequisites |
|---|---|
| HANDOFF (3→4) | All plan card assets assembled and audit-cleared (or red with consultant decision) |
| HANDBACK received (4→5 or 4→6/7) | HANDBACK manifest with all required fields, consultant sign-off |
| DELEGATE (4/5 start) | HANDBACK manifest complete |
| RETURN received (5→6) | RETURN pack with all required fields |
| Gate pack sign-off (7) | Phase 7 Forensic Auditor call complete (or auditor-unavailable decision); provenance map built |

If a required prerequisite is absent, the gate is held. State the missing prerequisite and
the action needed to resolve it.

user_prompt: |
  Pursuit ID: {{pursuitId}}

  {{#if clientName}}Client: {{clientName}}{{/if}}
  {{#if sector}}Sector: {{sector}}{{/if}}
  {{#if opportunityType}}Opportunity type: {{opportunityType}}{{/if}}
  {{#if cutoffPhase}}Engagement scope (cutoff phase): {{cutoffPhase}}{{/if}}
  {{#if targetGateDate}}Target gate date: {{targetGateDate}}{{/if}}

  Follow the workflow in your system prompt. Start by detecting whether state already exists
  for this pursuit ID. If it does, display current status and offer to resume. If it does not,
  begin phase 1 (Brief).
```

- [ ] **Step 4.2: Verify the YAML is well-formed and complete**

```bash
grep -c "Phase 1\|Phase 2\|Phase 3\|Phase 4\|Phase 5\|Phase 6\|Phase 7\|Phase 8\|Hard rules\|Save locations" \
  pwin-platform/skills/orchestration/pursuit-to-gate.yaml
```

Expected: `10` (all 8 phases + Hard rules + Save locations present).

```bash
grep -c "Use the Write tool" \
  pwin-platform/skills/orchestration/pursuit-to-gate.yaml
```

Expected: ≥ 8 (at least one Write tool instruction per Led phase).

```bash
grep "^id:\|^name:\|^system_prompt:\|^user_prompt:\|^context:\|^input:" \
  pwin-platform/skills/orchestration/pursuit-to-gate.yaml
```

Expected: all six top-level YAML keys present.

- [ ] **Step 4.3: Commit**

```bash
git add pwin-platform/skills/orchestration/pursuit-to-gate.yaml
git commit -m "feat(orchestration): write pursuit-to-gate YAML skill (master source)

8-phase workflow: Brief → Plan → Assemble → Synthesise (parked) →
Qualify (delegated) → ROI → Gate Pack → Continuous handoff. Three
roles (Led/Parked/Delegated) and four authority boundaries (HANDOFF
HANDBACK DELEGATE RETURN). Forensic Auditor called at phase 3 and 7
with graceful degradation. Engagement-scope declared in phase 1.
State written to ~/.pwin/<pursuitId>/orchestration.json. 10 hard rules.

YAML is the master source. Claude Code reads and executes directly.
Derive Claude.ai SKILL.md or API system_prompt from this file."
```

---

## Task 5 — Verify the YAML skill is complete

**Files:**
- Review: `pwin-platform/skills/orchestration/pursuit-to-gate.yaml` (read-only check)

The Universal Spec compliance checklist applies to intelligence dossier skills. The orchestration
skill is a different kind — it coordinates a workflow rather than producing a dossier. The
checklist below is adapted for this skill type and the YAML format.

- [ ] **Step 5.1: Run through the checklist**

Check each item against `pursuit-to-gate.yaml`:

```
COMPLIANCE CHECKLIST — pursuit-to-gate.yaml

[ ] YAML keys: id, name, agent, model, context, input, system_prompt, user_prompt all present
[ ] system_prompt: role statement ("what you do / do not do") at the top
[ ] system_prompt: reference map listing all four reference files
[ ] system_prompt: "Start here: detect mode" section with load-existing-state logic
[ ] system_prompt: all 8 phases documented with role (Led / Parked / Delegated)
[ ] system_prompt: at least one "Use the Write tool" instruction per Led phase (phases 1,2,3,6,7)
[ ] system_prompt: HANDOFF/HANDBACK/DELEGATE/RETURN authority boundaries, each with hold conditions
[ ] system_prompt: Forensic Auditor calls at phase 3 and phase 7, including degraded mode
[ ] system_prompt: scope override mechanism
[ ] system_prompt: save locations (orchestration.json + gate-pack.json)
[ ] system_prompt: hard rules, numbered, ≥ 8 rules
[ ] system_prompt: integrator discipline section with prerequisites per gate
[ ] system_prompt: walk-away handling in phase 5 (Qualify) and phase 6 (ROI)
[ ] system_prompt: ROI formula with three scenarios
[ ] system_prompt: gate pack structure with 7 sections
[ ] system_prompt: phase 8 handoff naming the monitoring skills
[ ] user_prompt: pursuitId template variable; optional fields for clientName, sector etc.
[ ] context: all four dossier types listed (buyer_dossier, supplier_dossier, sector_brief, incumbency_analysis)
[ ] input.required: pursuitId listed
```

- [ ] **Step 5.2: Fix any failing items**

For each unchecked item, make the targeted edit to `pursuit-to-gate.yaml`.

Re-run the grep checks from Step 4.2:

```bash
grep -c "Phase 1\|Phase 2\|Phase 3\|Phase 4\|Phase 5\|Phase 6\|Phase 7\|Phase 8\|Hard rules\|Save locations" \
  pwin-platform/skills/orchestration/pursuit-to-gate.yaml

grep -c "Use the Write tool" \
  pwin-platform/skills/orchestration/pursuit-to-gate.yaml

grep "^id:\|^name:\|^system_prompt:\|^user_prompt:\|^context:\|^input:" \
  pwin-platform/skills/orchestration/pursuit-to-gate.yaml
```

All counts must meet or exceed the expected values from Task 4.

- [ ] **Step 5.3: Verify all five skill files exist**

```bash
find pwin-platform/skills/orchestration -type f | sort
```

Expected (5 files):
```
pwin-platform/skills/orchestration/pursuit-to-gate.yaml
pwin-platform/skills/orchestration/references/contracts.md
pwin-platform/skills/orchestration/references/plan-card-schema.md
pwin-platform/skills/orchestration/references/provenance-map-schema.md
pwin-platform/skills/orchestration/references/pursuit-state-schema.md
```

- [ ] **Step 5.4: Final commit if any fixes were made in this task**

```bash
git add pwin-platform/skills/orchestration/pursuit-to-gate.yaml
git commit -m "fix(orchestration): compliance checklist fixes on pursuit-to-gate.yaml

[describe what was fixed]"
```

If Step 5.2 required no edits, skip this commit.

---

## Self-review

**Spec coverage:**

| Spec item | Task that covers it |
|---|---|
| Eight phases with roles (§3.2, §3.3) | Task 4 — YAML system_prompt phases 1–8 |
| HANDOFF contract (§3.4) | Task 1 (contracts.md) + Task 4 (phase 3/4 steps) |
| HANDBACK contract (§3.4) | Task 1 (contracts.md) + Task 4 (phase 4 step 4.2) |
| DELEGATE contract (§3.4) | Task 1 (contracts.md) + Task 4 (phase 5 step 5.1) |
| RETURN contract (§3.4) | Task 1 (contracts.md) + Task 4 (phase 5 step 5.2) |
| Forensic Auditor calls at phase 3 and 7 (§3.5) | Task 1 (auditor call interface) + Task 4 (phases 3, 7) |
| Engagement-scope flexibility (§3.1) | Task 3 (pursuit-state-schema.md) + Task 4 (scope override, phase 1) |
| Plan card structure (§5) | Task 2 (plan-card-schema.md) + Task 4 (phase 2) |
| Provenance map (§5) | Task 2 (provenance-map-schema.md) + Task 4 (phase 7) |
| Pursuit state schema (§5) | Task 3 (pursuit-state-schema.md) |
| Invocation surface (§5) | Task 3 (pursuit-state-schema.md) + YAML user_prompt |
| Scope override mechanism (§5) | Task 3 (pursuit-state-schema.md) + YAML system_prompt scope section |
| MCP read tools available (§5, closed by Plan A) | No task needed — Plan A delivered these |
| Skill-runner context providers (§5, closed by Plan A) | No task needed — Plan A delivered these |

**Placeholder scan:** No TBDs, no "implement later", no "add appropriate error handling". All phases have complete workflow steps. All JSON schemas are specified with every field. Degraded mode (auditor unavailable) is fully specified. ✓

**Type consistency:** `phaseArtifacts.N.handoffPack` is used in the YAML system_prompt (phase 4) and matches the state schema in pursuit-state-schema.md. `auditVerdict` is `"green | amber | red | pending"` consistently across contracts.md, plan-card-schema.md, provenance-map-schema.md, and the YAML. `cutoffPhase` is spelled consistently across all files. ✓

**What this plan deliberately does NOT cover:**
- The other five orchestration skills (Pursuit Progress Reporter, Freshness Monitor, Signal Router, Stakeholder Management, FTS Feed Monitor) — each gets its own spec and plan.
- The Forensic Intelligence Auditor agent's design — it has its own spec to be brainstormed separately (`wiki/actions/pwin-forensic-intelligence-auditor-design.md`).
- A Claude.ai SKILL.md — if one is ever needed, derive it from `pursuit-to-gate.yaml`; the YAML is the master source.
- An HTML renderer for the gate pack — the gate pack is written as JSON and a structured markdown summary in the session. Rendered HTML is a future design task.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-01-orchestrator-plan-b-pursuit-to-gate-skill.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks

**2. Inline Execution** — execute tasks in this session using executing-plans skill

Which approach?
