---
name: Session 10 UX review items
description: 9 open UX/structural changes from 2026-03-30 morning review — governance gates, activity moves, milestones, activity detail completeness
type: project
---

Session 10 — 2026-03-30. User reviewed Gantt chart and activity model, raised 9 UX/structural items (plus point 10 which became the methodology mapping exercise, now complete).

## Items to implement (all confirmed by user unless noted)

**1. Rename G8 "Storyboard Sign-off" → "Pink Review Complete"**
- It's a methodology milestone, not a formal governance gate
- Still shown in milestones view but relinked to PRD-05 (review completion) not BM-10 (storyboard production)
- Decision needed: confirm PRD-05 linkage vs keeping BM-10

**2. Reorder governance gates to logical sequence**
User's confirmed order: Pursuit Approval → Pink Review Complete → Solution & Strategy → Commercial & Finance → Legal & Contractual → Business Unit → Executive Committee → Board → Final Submission Authority
- G8 (storyboard) should be 2nd, not 8th
- G9 (final submission authority) = authority to submit after all approvals, positioned last
- Gantt currently sorts by calculated dates; logical sequence numbering needs fixing

**3. Move SAL-08 and SAL-09 to BM workstream**
- Clarification submission & response management (SAL-08 → BM-14)
- Clarification impact analysis & workstream updates (SAL-09 → BM-15)
- These are bid management activities, not sales capture
- Placement: after BM-09 (competitive dialogue) — both are procurement interaction activities

**4. SOL-02 incumbency toggle for "(rebid)"**
- Activity applies to all opportunities (reviewing current service model)
- "(rebid)" qualifier shown/hidden based on bid setup incumbency flag
- Bid manager toggles at start depending on whether incumbent or not

**5. Add "Solution Design Complete" milestone**
- Fires when SOL-11 (Solution design lock) completes
- New milestone in the key milestones view, positioned after Pink Review Complete and before Commercial/Finance Review

**6. Add risk identification activities to SOL and COM**
- SOL-12: Solution risk identification & analysis → Solution risk register
- COM-07: Commercial risk identification & analysis → Commercial risk register
- Both feed into BM-13 (bid risk register) and DEL-06 (mitigated risk register)

**7. Rename "Governance Gates" view → "Key Milestones"**
- Critical structural clarification: Internal Governance workstream (GOV-01–06) = activities with duration, ownership, deliverables
- Top-of-Gantt view = milestone timeline, NOT an activity workstream
- Split into: Procurement milestones (client-driven) + Programme milestones (derived from activity completion)
- Milestone dates derived from when underlying activities complete

**8. Add legal review to GOV workstream**
- GOV-04 (new): Legal & contractual review → Legal review decision record
- Product has gate G4 (Legal & Contractual Review) but no GOV activity to prepare for it
- GOV renumbers: GOV-01 to GOV-06

**9. Fix list view to include GOV activities**
- Activity module list view doesn't show governance activities
- Likely a filter/rendering bug — needs verification and fix

## Next discussion (evening session)

**Activity module tab differentiation** — the three views (Workstream, List, Gantt) need distinct purposes. Currently they show the same data with the same slideout, giving no reason to switch. Need to define: what question does each view answer? What does the user want to see at a glance in each? How does the new methodology data (L2/L3 tasks, inputs, quality criteria) change what each view should surface?

## Related completed work
- Point 10 (activity detail completeness) → resolved via methodology mapping exercise
- Mapping document created: `pwin-bid-execution/docs/methodology_mapping_review.html`
- Playbook uploaded: `pwin-bid-execution/docs/Bid_Lifecycle_Playbook.xlsx`
- Activity count: 79 → 83 proposed (SOL-12, COM-07, GOV-04, BM-16 new; SAL-08/09 moved)
