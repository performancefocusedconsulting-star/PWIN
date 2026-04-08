---
name: Skills need domain depth not scaffolding
description: 2026-04-04 — skill YAML prompts are too shallow; production skills need workflow management, multi-stage processes, template-driven outputs, and real domain knowledge from the user
type: feedback
---

Current 55 skill prompts are high-level scaffolding — they describe WHAT the skill does in a paragraph, not HOW it does it in detail. This is adequate for analysis skills (timeline review, compliance gaps) but insufficient for production skills that create real bid artefacts.

**Why:** Production skills like governance packs, response drafting, and capture plans produce deliverables that take weeks in practice. A single Claude call with a thin prompt cannot replicate this. The user flagged governance packs specifically — 60-70 slides for a major gate, takes weeks, involves multiple workstream leads, feeds mobilisation handover.

**How to apply:**
- Analysis skills (Agent 3 insight skills) = current single-call pattern is fine
- Production skills (Agent 5, parts of Agent 4/6) = need multi-stage workflows with state, checkpoints, human review, document outputs, and scheduling
- The user will provide example outputs and templates. These go in skill subfolders as reference docs
- Refine skills depth-first, one at a time, starting with the highest-value production skills
- Don't attempt to refine all 55 at once — work with the user on 5-6 priority skills
