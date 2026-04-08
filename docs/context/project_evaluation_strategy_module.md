---
name: New Evaluation & Win Strategy module
description: 2026-04-01 — new product module decided: evaluation criteria, client scoring, win themes, and scoring insight together in one view. Extracted from Submissions module.
type: project
---

## Decision

New module in the Bid Execution product: **Evaluation & Win Strategy** (working title).

Consolidates three views currently scattered or missing:
1. **Customer evaluation criteria approach** — evaluation methodology breakdown, criteria-to-section mapping, marks concentration analysis
2. **Customer scoring view** — client marking scheme, grade bands, hurdle marks (currently in Submissions M5 as optional section)
3. **Win themes view** — win themes register, integration heatmap (currently in Submissions M5 as collapsible panel)

Plus insight/prioritisation derived from SAL-05 outputs:
- Score gap analysis
- Per-section scoring strategy
- Win theme integration map
- Marks concentration and effort allocation guidance

## Why

- These are the strategic positioning and scoring inputs that drive solution design, storyboard, commercial approach, and production priorities
- They don't belong in Submissions (which is about production execution)
- Bid manager needs a single place to see: what are the rules, where are the marks, what are our themes, where are our gaps
- Feeds into everything: BM-07, BM-10, SOL-10, SUP-01, writers

## Impact

- Win themes register and integration heatmap extracted from Submissions module
- Client scoring scheme extracted from Submissions module
- New views needed for evaluation criteria matrix and scoring strategy
- Submissions module retains production pipeline, response items, compliance — but loses the strategy layer
- Architecture v6 needs updating with new module definition (to be done during build planning, not during methodology mapping)

## How to apply

When building or updating the product, treat this as a distinct module (M-number TBD). Do not continue embedding strategy views inside Submissions.
