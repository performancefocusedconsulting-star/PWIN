---
name: Skill workflow engine needed for production skills
description: 2026-04-04 — current skill runner is single-call; production skills need multi-stage workflows with state tracking, prerequisites, human review loops, document outputs, and scheduling (T-10, T-5, T-3 patterns)
type: project
---

## Production Skill Workflow — Design Requirement

### The gap
Current skill runner: YAML config → one Claude call → write results. Fine for analysis. Not sufficient for production skills that manage multi-day processes.

### Example: Governance Packs (Skill 5.4)
- T-10: Check data readiness, flag gaps to bid manager
- T-8: Ingest workstream lead inputs (solution, commercial, legal, risk)
- T-7: Assemble first draft pack, structured by template
- T-5: Workstream leads review, annotate, feed back
- T-4: Revise based on feedback
- T-3: Dispatch to approving body
- T-0: Gate meeting
- Post-gate: Conditions captured, pack archived, feeds mobilisation handover

### Template-driven approach confirmed
- Client organisations have their own defined gate pack formats
- Large strategic suppliers provide their templates during onboarding
- Smaller organisations use BidEquity best-practice defaults
- AI populates the template from bid data, doesn't invent the structure
- This is a key differentiator: BidEquity wraps around the client's process

### Skill folder structure agreed
```
skills/agent5-content-drafting/
  governance-packs.yaml           ← skill prompt
  governance-packs/
    reference/                    ← example outputs, what good looks like
    templates/                    ← empty structures to be populated
    workflow.md                   ← multi-stage process definition
```

### What's needed
1. User provides example governance packs (uploading when found)
2. Workflow engine design for multi-stage skills (state, checkpoints, scheduling)
3. Template ingestion and mapping capability
4. Document output format (markdown → exportable to PPT/PDF)
5. Depth-first refinement: get one production skill to quality, use as pattern

### Priority production skills for deep refinement
1. Governance Packs (5.4) — user described in detail
2. Response Section Drafting (5.1)
3. Capture Plan Assembly (3.3)
4. Operating Model Design (6.2) — highest effort (45 person-days)
5. Executive Summary (5.2) — most-read page of any bid
6. Cost Modelling (4.1) — commercial foundation
