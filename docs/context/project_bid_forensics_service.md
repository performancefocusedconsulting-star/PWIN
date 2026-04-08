---
name: Bid forensics service concept
description: 2026-04-03 — standalone product idea: retrospective bid analysis service. Client uploads lost bid documentation, PWIN engine runs in reverse to produce quantitative post-mortem. Low-friction website service for ~£2K.
type: project
---

## Bid Forensics — Retrospective Analysis Service

### Concept
Client has lost a bid and wants to know why. Currently a manual, subjective consulting exercise. Proposed: automate it using the PWIN engine in reverse.

### How it works
1. Client uploads: ITT documents, their submitted proposal, internal gate notes, team details, any debrief/feedback received
2. Agent 1 ingests all documentation (ITT extraction + proposal parsing)
3. Agent 3 runs retrospectively: PWIN scoring, compliance coverage, marks allocation, win theme audit, evaluation criteria analysis
4. Agent 5 assesses response quality per question against the scoring scheme
5. Qualify framework produces a retrospective PWIN score — what their actual probability of winning was based on evidence, not what they believed
6. Output: structured forensic report with quantitative scores, compliance gaps, marks left on the table, quality assessment per question, AI assurance challenges, and specific recommendations

### Business model
- Fixed-price service (~£2K) listed on website
- Low onboarding friction — client just uploads documents, no platform setup needed
- Natural gateway to full platform: "imagine having this analysis during the bid, not after"
- Could sell volume — every organisation that loses a significant bid wants to know why
- User has delivered this manually before — knows the market exists

### Architecture implications
- Could be a standalone product or a mode within the existing platform
- Most skills already exist — it's a curated sequence of existing Agent 1, 3, and 5 skills
- Needs a "forensic report" output template that consolidates all skill outputs into a single deliverable
- May need a proposal parsing skill (new) — Agent 1 currently extracts ITTs, not submitted proposals
- The debrief/feedback from the client (if they received evaluator scores) becomes ground truth for calibrating the AI's assessment

### PRD produced (Session 16, v2.0)
Full PRD at `bidequity-verdict/docs/BidEquity-Verdict-PRD-v2.md`. Updated during session with:
- Two-pass execution model (Pass 1: platform analysis, Pass 2: consultant investigation + enrichment)
- Platform reuse assessment (Section 7) — most skills reusable, ~11 new YAMLs needed
- Build plan (Section 12) — 9-14 days total, 4 sprints
- API cost per engagement: <£1 at £2,000 price point
- Shared scoring skill serves both Verdict and Bid Execution pre-review AI scoring
- CLAUDE.md and plugin architecture updated with Verdict product

### How to apply
Build is scoped and ready. Key dependencies: independent scoring skill (shared with Bid Execution), proposal parsing skill (new), 7 forensic domain skills. Cross-reference with Qualify/Execution methodology completed to check coverage.
