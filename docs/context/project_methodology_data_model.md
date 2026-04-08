---
name: Methodology data model design
description: Session 10 (2026-03-30) — confirmed data structure for L1/L2/L3 methodology content, status derivation, slideout UX, checkbox ownership
type: project
---

## Data structure confirmed

Activity template extended with:
- `role`: default owner role, tasks inherit unless overridden
- `subs[]`: L2 sub-processes, always present (consistent nesting), each with `tasks[]`
- `tasks[]`: L3 with name, RACI (r/a/c/i), inputs, outputs, guidance, effort, type
- `inputs[]`: structured references `{ from: 'SOL-03', artifact: 'Target operating model' }` — machine-traversable. External inputs omit `from`.
- `outputs[]`: name, format, `quality[]` as discrete checkable items (not free text)
- RACI at task level, activity `role` is default override

## Status derivation

- not_started → in_progress: manual start OR first task ticked
- in_progress → draft_complete: automatic when all tasks ticked
- draft_complete → final: automatic when all quality criteria ticked
- Reverse: unticking drops status back
- Progress bar: task completion % shown within in_progress

## UX decisions

- Activity slideout: 780px wide, three new sections (inputs with live status, L2/L3 task checklists, outputs with quality criteria)
- V1: bid manager ticks everything (single operator)
- V2: workstream leads tick tasks, bid manager approves quality criteria
- Gantt milestone diamonds: open linked activity slideout, not navigate to governance module

## Methodology mapping

- 83 proposed activities (79 + SOL-12, COM-07, GOV-04, BM-16; SAL-08/09 moved to BM)
- ~48 mapped from playbook, ~35 need L3 authoring
- Review document: methodology_mapping_review.html — needs line-by-line review before populating
