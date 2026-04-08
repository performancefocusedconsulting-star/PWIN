---
name: Production parallelisation rules
description: How production stages parallelise across response items — authoring parallel, reviews ideally batched, solution gates pricing/implementation
type: feedback
---

Authoring stages (storyboard, first_draft) run fully in parallel across items, constrained only by author availability.

Reviews (pink, red, gold) are ideally batched — all items reach pink_ready together, review happens as a coordinated event, feedback given collectively so documentation is locked down together. When production runs behind schedule, reviews fall back to fluid (item-by-item as ready). AI monitoring/nudging through lifecycle should improve quality pre-review and reduce need for rushed fluid reviews.

**Why:** Batched reviews give reviewers full context across the submission, catch consistency issues, and lock down documentation together. Fluid reviews are a compromise when time pressure forces it.

**How to apply:** Schedule review target dates as batch synchronisation points. Items that finish drafting early wait for the batch (or get early fluid review if significantly ahead). The scheduling engine should show which items are holding up the batch.

Reviewer allocation: typically 2-3 reviewers per workstream, not per item.

Gold review is a bottleneck by design — 1-2 senior reviewers, items queue by priority.

Cross-item dependencies: legal/company info items are fast-track with no upstream dependencies, can be drafted and completed early. Core solution lock-down gates pricing and implementation document production. Model these as explicit dependencies (solution → pricing, solution → implementation).
