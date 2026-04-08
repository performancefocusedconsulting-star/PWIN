---
name: Submissions module redesign session
description: Major redesign of Submissions module — Response Requirements as reference view, Production Pipeline with ribbon and slideout, next target is scheduling integration
type: project
---

Session completed 2026-03-27. Submissions module (M5) substantially redesigned across 12 commits.

**What was built:**

1. **Compliance matrix UX deferred to V2** — data model, PRD-01 activity, governance hard gates all retained. Tracking managed externally (AI + Excel) in V1. Gap report also deferred.

2. **Response Requirements tab** — pure reference view (no production data). Grouped by evaluationCategory with collapsible section headers showing weight % from EvaluationFramework. Sorted by client document structure. Columns: Ref, Title, Type, Output, Marks, Hurdle. Question detail panel (780px) with full question text, evaluation criteria, hurdle callout, scoring/limits, source reference. Edit button for mid-bid amendments (marks, word/page limits, hurdle, criteria, question text) with lastAmended flag.

3. **Reference Ribbon** — three panels: Evaluation Split Bar (proportional stacked bar), Total Pages + Est. Effort (large gold numbers), Submission Inventory (card grid by responseType listing individual item names).

4. **CSV Import** — 8 required columns (reference, title, questionText, responseType, evaluationCategory, evaluationMaxScore, evaluationCriteria, sectionNumber), 3 optional (hurdleScore, wordLimit, pageLimit). Validates enums.

5. **Production Pipeline tab** — 10-stage lifecycle flow diagram (numbered, with connectors). Collapsible stage groups. Row columns: Ref, Title, Type, Marks, Owner, Status (display only), Schedule indicator (days ahead/behind). No inline editing — all editing in production slideout.

6. **Production Slideout** (780px) — full question text, status transitions, owner dropdown from team org chart, word limit read-only, effort editable (person-days), stage deadline. Production Log with 4 structured sections: Next Steps, Issues & Blockers, Risks, Conversation Log.

7. **Production Ribbon** — six metrics: Progress (colour-coded vs time elapsed), Coverage, Overdue count, Effort Left, Unassigned count, Stage Distribution Bar with legend.

**What's next — Production Scheduling Integration:**

This is the next major build target, fully documented in the architecture doc (Next Session, decision #19). Key points:

- Backward-schedule production stage dates per ResponseItem from submission deadline (Final → Gold → Red → Pink → First Draft → Storyboard)
- Pre-populate stage dates on day one — not blank
- Activities are NOT all sequential — many run in parallel. Scheduling must respect parallelisation types (sequential, parallel, staggered)
- Surface dependency impact when dates change: downstream compression, dependency chains, submission risk
- Production log captures WHY behind date changes; scheduling engine captures WHAT (revised dates + consequences)
- Critical path through production stages should be visible
- Integration with existing Gantt view in Activity Tracker

**Open questions to resolve:**
- Parallelisation rules for production stages: which stages can overlap across different ResponseItems?
- How do ResponseItem dependencies map to the existing activity dependency model?
- Buffer policy: minimum buffer between gold review completion and submission deadline?

**Why:** The user understands dependencies deeply from bid management experience. The current stage deadline is manual/blank — it needs to be auto-derived from the backward schedule with impact analysis when changed. This connects the production lifecycle to the scheduling engine that already exists for the 79 methodology activities.
