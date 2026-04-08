---
name: Session 11 — Gold standard and L4/skills mental model
description: 2026-04-01 — established gold standard template from SAL-03, confirmed L4=skills architecture, Win Strategy product diagram shared
type: project
---

## Gold standard template

- Created: `pwin-bid-execution/docs/methodology_gold_standard.md`
- Reference activity: SAL-03 — Competitor analysis & positioning
- Structure: L1 (workstream) → L2 (sub-processes, 2-4 per activity) → L3 (tasks with RACI, structured inputs, outputs with quality criteria)
- SAL-03 confirmed: 2 L2s (Intelligence Gathering → Positioning & Counter-Strategy), 5 L3 tasks
- SAL-02 confirmed as direct input to SAL-03 (not just via SAL-01)

## L4 = Skills architecture confirmed

- L1/L2/L3 = methodology data model (lives in Activity template data, the WHAT)
- Agents = persona routing (the WHO — bid manager, pursuit director, etc.)
- Skills = intelligence capabilities (the HOW — timeline-analysis, competitive-intelligence, etc.)
- L4 = encoded within skills — the actual AI-assisted workflow logic
- User confirmed this mental model aligns with their forward thinking

## Win Strategy product

- User shared architectural diagram: "Phased Approach to AI-Driven Win Strategy Architecture"
- Separate product, sits outside Bid Execution, covers capture phase (pre-ITT)
- 4 phases: Baseline PWIN Scoring → Guided Strategy Elicitation (5 dimensions) → Strategy Synthesis & Draft Generation → Challenge, Refine & Lock
- 4 specialised agents: Intelligence Analyst, Facilitation, Strategy Synthesis, Challenge
- Simpler variant for lower-value deals: Battle Cards
- Key outputs feed Bid Execution: Competitive Positioning Matrix → SAL-03, Win Theme Map → SAL-04, Pricing Strategy Framework → COM-02

## Cross-product interface pattern

- New `crossProduct` input type: `{ crossProduct: 'PWIN-WINSTRAT', artifact: '...', optional: true }`
- Two operating modes: capture-informed (refinement) vs cold-start (from scratch)
- Same methodology tasks apply in both modes; effort and AI capability differ

## Next steps

- Use gold standard template to map remaining ~77 activities
- Win Strategy product needs its own section in plugin architecture doc (future)
