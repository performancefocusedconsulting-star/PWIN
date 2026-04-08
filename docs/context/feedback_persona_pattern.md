---
name: Structured persona pattern for agent prompts
description: Alex Mercer persona (PWIN Qualify) establishes the reusable pattern for all agent system prompts — structured object + assembly function + workflow triggers + self-audit
type: feedback
---

The Alex Mercer persona (pwin-qualify/docs/PWIN_Alex_Persona_v1.html) is the reference pattern for how all 6 agents should define their system prompts. Adopt this structure, not a flat prompt string.

**The pattern:**
- `ALEX_PERSONA` JS object with independently editable fields
- `buildPersonaPrompt()` assembly function composes system prompt at runtime from: identity → background → core beliefs → character traits → tone → language patterns → hard rules → workflow triggers → sector enrichment (conditional) → opportunity type (conditional) → output schema → success criteria (self-audit)

**Key design elements to reuse across all agents:**
1. **Workflow triggers** (Section 08) — deterministic if/then rules for critical decisions. More reliable than character descriptions. "If evidence contains only team assertions → auto-verdict CHALLENGED." Every agent skill should have skill-specific triggers.
2. **Success criteria as self-audit** (Section 09) — the AI checks its own output against concrete tests before returning. Specificity test, answerability test, non-duplication test, final check against avoid-list.
3. **Language patterns** — explicit use/avoid lists per agent. The avoid list (no "great evidence", no "you might want to consider", no hedging) should be largely shared across the platform.
4. **Calibration rules** — evidence bar adjusts to TCV, pursuit stage, opportunity type, sector. Every agent should calibrate to context, not apply abstract standards.

**Why:** Workflow triggers produce the most consistent AI behaviour. Character descriptions are interpreted variably by the model. Hard conditional rules are followed reliably. The most impactful prompt engineering investment is in the triggers, not the prose.

**How to apply:** When writing AGENT.md implementation files (future step), structure each agent's system prompt as a persona object following this pattern. Platform-level elements (core beliefs about bid management, avoid-list, calibration principle) are shared. Agent-specific elements (identity, domain expertise, skill triggers) are per-agent.
