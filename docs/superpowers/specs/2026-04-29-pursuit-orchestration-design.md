# Pursuit Orchestration — Design Spec

**Date:** 2026-04-29 (revised 2026-04-30)
**Status:** Reviewed 2026-04-30. One architectural change applied — Quality Assessor extracted from the orchestrator and elevated to its own agent (the Forensic Intelligence Auditor). Awaiting writing-plans.
**Authors:** Paul Fenton (design lead), Claude (brainstorm partner)
**Predecessor notes** (in the Obsidian wiki at `C:/Users/User/Documents/Obsidian Vault/wiki/`):
- `platform/agent2-to-downstream-pipeline-gap.md` — surfaced the pipeline gap that triggered this design
- `actions/orchestrator-brainstorm-prep.md` — pre-brainstorm prep with what was already decided
- `actions/pwin-plugin-orchestration-agent.md` — original action note, now superseded by this spec
- `decisions/pwin-agent0-is-client-context.md` — naming correction (Agent 0 ≠ orchestrator)
- `decisions/skill-universal-spec.md` — skill-side contract this design assumes
- `decisions/forensic-intelligence-auditor-agent.md` — the 2026-04-30 decision to extract Quality Assessor as its own agent
- `actions/pwin-forensic-intelligence-auditor-design.md` — follow-on action: design the auditor in its own brainstorm

## 1. Why this design exists

The platform produces rich intelligence dossiers (Agent 2: buyer, supplier, sector, incumbency) that no downstream PWIN product currently consumes programmatically. The gap was traced to three breaks: no MCP read tool for the rich dossiers; no skill names them as inputs; no orchestrator coordinates the assembly of intelligence into a downstream deliverable. This spec addresses the third break by designing the pursuit orchestration agent and its first and most substantial skill, **pursuit-to-gate orchestration**.

The user's stated platform philosophy is bottom-up: the four intelligence skills and the procurement / stakeholder data layer are the live work; orchestration plumbing waits until the inputs are worth orchestrating. This spec is therefore design now, build later — produced so the intelligence-skill work can continue with knowledge of how outputs will eventually be consumed, and so the orchestrator's V1 build, when it comes, has a clear blueprint.

## 2. Architectural model

### 2.1 The orchestrator is an agent with multiple skills, not a single function

Just as Agent 2 has four intelligence skills, the orchestration agent has multiple orchestration skills, each addressing a different orchestration role. This avoids the trap of treating "the orchestrator" as one monolithic function and lets each skill be specified, built, and matured independently.

### 2.2 V1 skill catalogue

Six skills, in two clusters. Quality assessment is *not* a skill of this agent — see section 2.4 below.

**Pursuit-level (driven by a specific live pursuit):**
1. **Pursuit-to-gate orchestration** — given a pursuit brief, drive the chain from intelligence assembly through to a gate-ready deliverable, bounded by the consultant's declared engagement scope.
2. **Pursuit progress reporter** — answer "where are we" questions about a live pursuit on demand.

**Data-layer (independent of any specific pursuit):**
3. **Intelligence freshness monitor** — continuously scan all intelligence assets, flag staleness against refresh thresholds, raise refresh actions proactively.
4. **External signal router** — receive signals from the newsroom product, classify relevance, identify which assets they affect, trigger targeted refreshes.
5. **Stakeholder management orchestration** — manage the stakeholder database with the same freshness, quality, and refresh discipline as the other intelligence layers.
6. **FTS / procurement feed monitor + opportunity surfacing** — continuously monitor the FTS feed (UK1–UK6 and beyond), surface relevant signals into the intelligence layer, raise opportunity prompts where appropriate.

Two further candidate skills (decision-gate prompter, cross-pursuit pattern detector) were considered and parked as "value recognised, home unclear" — they may fold into other skills, into Agent 3, or into a future bid-manager piece. Revisit after V1 ships.

### 2.3 The orchestrator is a project manager, not a synthesiser and not an auditor

The orchestration agent does not do strategic synthesis. It plans, tracks, dispatches, escalates risks, drives handoffs, and pushes the workflow forward. Strategic synthesis — the integrative thinking that produces a Win Strategy from a pile of intelligence — is owned by Agent 3 and the human bid team. This boundary is non-negotiable in the design: the orchestrator does not have win-strategy expertise and is never given authority to overrule strategic conclusions.

The orchestrator also does not perform forensic quality audit on the assets it routes. Audit is delegated to a separate agent (see §2.4). The orchestrator's quality role is limited to *triggering* the auditor at the right moments and *acting on* the verdict and actions returned.

This framing maps cleanly to where AI agents are reliably capable today: structured plan execution, dispatch and tracking, escalation. It deliberately keeps strategic judgement under human authority and audit judgement under a specialised agent.

### 2.4 Quality assessment lives in a separate agent

In an earlier draft a seventh "Quality assessor" skill sat inside the orchestrator. On reflection (2026-04-30 review session) this conflated two different concerns: project-management (which is what the orchestrator does) and forensic intelligence audit (which has its own persona, its own remit, and operates on assets the orchestrator never touches — for example, client-onboarding inputs and the procurement reference layer).

The quality function is therefore extracted into a new agent — the **Forensic Intelligence Auditor** — designed in its own spec. The orchestrator's interaction with it is purely as a caller: at defined moments the orchestrator invokes the auditor on a specific asset and receives back a verdict + actions. The auditor's design (skill catalogue, audit logic, partitioning across asset types) is not in scope here. See `wiki/decisions/forensic-intelligence-auditor-agent.md`.

## 3. Pursuit-to-gate orchestration — detailed design

### 3.1 Scope flexibility

Different commercial engagements buy different amounts of the chain. Some clients buy "produce me a Win Strategy" and stop. Others buy "drive me to a gate decision." The skill design must support both without architectural change.

**Mechanism: engagement scope is declared in the phase 1 brief.** The consultant tells the orchestrator where the engagement ends (e.g. phase 4, phase 7, phase 8). The plan card produced in phase 2 is bounded by that scope. Phases beyond scope are not planned, not executed, not surfaced. Scope can be extended later by the consultant if the engagement grows; the orchestrator picks up where it stopped.

### 3.2 Eight phases

| # | Phase | Orchestrator role | Output / state at end of phase |
|---|---|---|---|
| 1 | Brief | Led | Pursuit brief: client, scope, sector, opportunity type, named competitors, engagement-scope cutoff, target gate date |
| 2 | Plan | Led; consultant approves | Plan card: dependency chain, current artefact state per input, proposed actions, sequencing, anticipated decision gates |
| 3 | Assemble | Led | Complete, quality-checked input pack ready for synthesis |
| 4 | Synthesise + Document | **Parked** | Win Strategy artefacts and document; consultant sign-off |
| 5 | Qualify | **Delegated** | PWIN score, go/no-go recommendation, conditional asks |
| 6 | Compute ROI | Led | Pursuit ROI position with sensitivity bands |
| 7 | Gate pack | Led; consultant signs off | Gate-ready presentation pack: strategy summary, qualify recommendation, ROI, provenance map, risk surface |
| 8 | Continuous | Other orchestration skills take over | Pursuit-watch handoff to freshness monitor, signal router, progress reporter |

### 3.3 Three orchestrator roles

The orchestrator behaves differently in different phases. The design distinguishes three roles, each with a different authority pattern:

- **Led.** Orchestrator runs the work directly: phases 1, 2, 3, 6, 7, 8.
- **Parked.** Orchestrator has no place; the human team owns the work. Used in phase 4 (synthesis), where Agent 3, the consultant, the bid team and (where applicable) the client bid team work iteratively. The orchestrator does not re-evaluate the strategy when it returns. Authority on the strategy itself sits with the consultant.
- **Delegated.** Orchestrator passes control to a sub-product that runs its own consultant-led pattern. Used in phase 5 (Qualify), where the Qualify product has its own AI + consultant assurance pattern internally. The orchestrator waits for the sub-product to return a result, then resumes.

The distinction between **parked** and **delegated** matters: parked phases the orchestrator stays out of entirely; delegated phases the orchestrator dispatches and awaits a structured return. Both produce the same external behaviour ("orchestrator is not running"), but they have different state semantics and different handback contracts.

### 3.4 Authority boundaries

Four explicit boundaries within the workflow, each with its own contract:

- **HANDOFF (end of phase 3 → start of phase 4).** Orchestrator presents the input pack to Agent 3 + consultant + bid team and parks. The contract specifies what Agent 3 must return and by when.
- **HANDBACK (end of phase 4 → orchestrator resumes).** Consultant signs off the synthesised Win Strategy. Document and artefacts return to the orchestrator with a manifest of what was produced.
- **DELEGATE (orchestrator → start of phase 5).** Orchestrator passes the Win Strategy + intelligence pack to the Qualify product as input. Qualify owns the run.
- **RETURN (end of phase 5 → start of phase 6).** Qualify returns its recommendation, score breakdown, and conditional asks. Orchestrator resumes.

The contents of the pack at each boundary are detail work for the implementation plan — see section 5.

### 3.5 Calls to the Forensic Intelligence Auditor agent

The orchestrator invokes the auditor at two points in the pursuit-to-gate flow. Both calls are integration points, not internal capabilities — the orchestrator is the caller; the auditor owns the audit logic.

- **During phase 3 (intelligence assembly)** — for each intelligence dossier as it lands, the orchestrator calls the auditor against that dossier. The auditor returns a verdict (green / amber / red) and an actions list. The orchestrator surfaces both to the consultant; on red the consultant decides whether to re-run, escalate, or proceed with caveats.
- **During phase 7 (gate pack)** — the orchestrator calls the auditor against the assembled gate-pack inputs (the intelligence pack used by Agent 3 and the synthesis manifest Agent 3 returned at HANDBACK). The auditor checks provenance (did synthesis use the inputs available), traceability (does each strategy claim trace back to source), and flag-handling (was anything Agent 3 raised surfaced to the consultant). The orchestrator does **not** re-evaluate the strategy itself; that authority sits with the consultant.

Synthesis-output audit (auditing the Win Strategy itself, the go/no-go recommendation, the gate-pack narrative) is **out of scope** for the V1 auditor and therefore out of scope for these orchestrator calls. The orchestrator does not pretend to compensate for that gap.

## 4. What the orchestration agent inherits from the wider platform

- **Skill Universal Spec** ([decision](wiki/decisions/skill-universal-spec.md)) — every intelligence skill exposes `prerequisites.required[]`, `prerequisites.preferred[]`, `meta.prerequisitesPresentAt`, `meta.versionLog[]`, `changeSummary[]`, refresh triggers including the artefact-arrival trigger. The orchestrator reads against this contract; it does not invent its own discovery mechanism.
- **Existing dossier files** at `~/.pwin/intel/<type>/<slug>-<artefact>.json`. The orchestrator's read tools load from this canonical location.
- **MCP platform tools** for FTS and Companies House data via the existing `compIntel` layer.
- **Agent 0 (Client Operating Context)** as the upstream client-onboarding context. The orchestrator does not generate client context; it consumes it.
- **Forensic Intelligence Auditor agent** as the quality-assurance service. The orchestrator calls it at the two points described in section 3.5; it does not own audit logic itself. See `wiki/decisions/forensic-intelligence-auditor-agent.md`.

## 5. Open detail work for the implementation plan

These are concrete and important but they are refinements on the architectural spine, not architectural questions. They will be settled in the writing-plans phase that follows this spec:

- **Contract specifications:**
  - Input pack structure at HANDOFF (what's in it, in what shape)
  - Synthesis manifest at HANDBACK (what Agent 3 declares about what it produced)
  - Qualify input contract at DELEGATE (what Qualify needs from the orchestrator)
  - Qualify return contract at RETURN
- **Plan card structure** (phase 2 output the consultant approves)
- **Provenance map** (phase 7 deliverable component)
- **Pursuit state** — where it lives, who reads it, who writes it, version semantics
- **Invocation surface** — slash command, conversational interface, both, with what arguments
- **Engagement-scope override** — how a consultant extends scope mid-engagement
- **MCP read tools** — `get_buyer_intelligence_dossier`, `get_supplier_dossier`, `get_sector_brief`, `get_incumbency_analysis`, `get_stakeholder_map` — needed before the orchestrator can run end-to-end. These are also called for separately by the [Agent 2 → downstream pipeline gap](wiki/platform/agent2-to-downstream-pipeline-gap.md) note.
- **Skill-side context provider** in the skill-runner so each Agent 3 skill can request `buyer_dossier`, `supplier_dossier` etc. as part of its declared context.

## 6. What is deliberately out of scope

- **The other five orchestration skills.** This spec covers only Pursuit-to-gate orchestration. The pursuit progress reporter and the four data-layer skills (freshness monitor, signal router, stakeholder, FTS feed monitor) will get their own design specs as they come up the priority list.
- **The Forensic Intelligence Auditor agent.** Its full design — persona, V1 input remit, skill partitioning, verdict semantics, action types, claim-level metadata required from producing skills — lives in a separate spec to be brainstormed in its own session. This spec only treats the auditor as a service the orchestrator calls.
- **Decision-gate prompter and cross-pursuit pattern detector.** Parked as "value recognised, home unclear." Revisit after V1 ships.
- **Implementation details.** No code in this spec. The implementation plan that follows will turn the architectural decisions here into specific skill files, MCP tool implementations, and platform changes.
- **Renderer or UI work.** The orchestrator's interface to the consultant is part of the open detail work above; the broader question of how the consultant *experiences* the platform (HTML dossiers, dashboards, conversational interface) is its own design conversation tracked in [dossier-rendering-information-design.md](wiki/platform/dossier-rendering-information-design.md).
- **Agent 3 internal architecture.** This spec assumes Agent 3 owns synthesis and treats Agent 3 as a black box at the orchestrator boundary. Agent 3's own architecture (its skills, its synthesis pattern, its human-collaboration model) is downstream design work outside this scope.

## 7. Sequencing and dependencies

This spec is design only. The implementation work it implies cannot start before:

- The user reviews and approves this spec.
- A concrete implementation plan is produced from it (writing-plans skill).
- The four intelligence skills are mature enough that an orchestrator running against them will produce useful results.

The orchestrator design is therefore future-facing. The platform's bottom-up philosophy means intelligence-skill quality remains the higher priority; this spec ensures that intelligence-skill maturation happens with knowledge of how outputs will be consumed.

## 8. Acceptance criteria for this spec

The spec is correct if a senior reader can answer all of:

- What does the orchestration agent do, and what does it not do?
- What skills does it have in V1?
- For pursuit-to-gate orchestration specifically — what are the phases, what role does the orchestrator play in each, and where are the authority boundaries?
- How does engagement-scope flexibility work?
- What is deliberately deferred to the implementation plan?
- What is deliberately out of scope?

If any of these is unclear, the spec needs revision before implementation planning starts.
