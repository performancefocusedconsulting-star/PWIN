---
name: Production scheduling design session
description: Session 9 (2026-03-27 evening) — working through open questions for production scheduling integration, uncovered backward scheduler bug
type: project
---

Session 9 — 2026-03-27 evening. Design discussion only, no code changes.

## Questions resolved

**Q1: Parallelisation rules — RESOLVED**
- Authoring stages (storyboard, first_draft) run fully in parallel across items, constrained by author availability
- Reviews (pink, red, gold) are ideally batched — all items reach the gate together, reviewed as a coordinated event. Falls back to fluid (item-by-item) when behind schedule
- Reviewer allocation: 2-3 reviewers per workstream, not per item
- Gold review is a bottleneck by design — 1-2 senior reviewers, items queue by priority
- Cross-item dependencies: solution approach gates pricing and implementation drafting. Legal/company info is independent

**Q1b: Governance gates and production scope — RESOLVED**
- G8 (Storyboard Sign-off / Solution Lock) only gates quality/solution response questions, NOT all production
- Items that can start day 1 without waiting for G8: legal, company information, insurance review & certificate compilation, security & data protection, contract review & markup
- G2 (Solution Review) and G3 (Commercial Review) are assurance/guidance sessions, not sign-off gates. Assets should be relatively mature but not complete
- Executive/Board committees (G5/G6/G7) are the actual sign-off gates

**Q2: ResponseItem dependencies vs activity dependency model — NOT YET DISCUSSED**

**Q3: Buffer policy (minimum gap gold → submission) — NOT YET DISCUSSED**

## New issue discovered: Backward scheduler bug

The Gantt chart uses real backward-scheduled dates, not placeholders. This creates unrealistic positioning for:

1. **Forward-anchored activities** — BM-01 to BM-05 (kickoff, bid management plan, doc management, resource tracking, cost management) should start in week 1 regardless of backward schedule. Currently scheduled backward from dependents, pushing them later than reality.

2. **Continuous/recurring activities** — BM-04 (resource management), BM-05 (cost management), BM-06 (progress reporting) have dur:0 and run throughout the bid lifecycle. The scheduler has no concept of continuous activities — treats them as zero-length bars pinned to submission deadline.

**Decision needed:** Fix the activity scheduling model (add forward-anchored and continuous activity types) before or after production scheduling integration? They're related — production scheduler will inherit the same problems.

## Where to pick up tomorrow

1. Decide whether to fix the backward scheduler activity model first (forward-anchored + continuous activities) or proceed with production scheduling and fix both together
2. Resolve Q2: How do ResponseItem dependencies map to the activity dependency model — same graph or separate layer?
3. Resolve Q3: Buffer policy — minimum gap between gold review completion and submission deadline
4. Then implement the production scheduling engine
