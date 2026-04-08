---
name: Session 14 capability-based agents
description: 2026-04-02 — persona agents replaced by 6 capability-based agents, AI suitability assessment practitioner-validated, strategic moat = methodology not platform
type: project
---

## Session 14 — Capability-Based Agent Architecture

**AI suitability assessment practitioner-validated.** 24 of 296 tasks received detailed practitioner notes describing real-world AI workflow. Ratings broadly confirmed. Dominant pattern: Agent + Skill + Proforma/Template.

**Six capability-based agents replace five persona-based agents:**
1. Document Intelligence (Phase 1, 63% reduction, foundation)
2. Market & Competitive Intelligence (Phase 3, 72% reduction, runs outside bids)
3. Strategy & Scoring Analyst (Phase 1, 58% reduction)
4. Commercial & Financial Modelling (Phase 4-5, 43% reduction)
5. Content & Response Drafting (Phase 2, 40% reduction, highest volume)
6. Solution & Delivery Design (Phase 3-5, 35% reduction, highest task count)

**Why:** Bottom-up task analysis showed clustering by AI capability, not by human role. An agent = saved configuration (prompt + tools + knowledge), not separate infrastructure.

**Key practitioner insights:** Document upload (not API) is primary input. Agent 2 runs on recurring schedule outside bids. Some tasks understate AI potential.

**Strategic moat:** Technology is commodity. IP is methodology + skill definitions + templates + quality criteria.

**Unified skill model (same session):** The 20 AI use cases and ~25 productivity skills are implemented identically — prompt + MCP tools + Claude API call. No separate "intelligence layer." Use cases are insight skills within parent agents. UC1-7,9,12→Agent 3; UC10-11→Agent 4; UC13-14→Agent 1; UC15→Agent 5; UC8→Agent 6; UC16-20→deferred V2/V3.

**All 6 agents fully specified (55 skills total):**
- Agent 1: Document Intelligence — 7 skills (agent_1_document_intelligence.md)
- Agent 2: Market & Competitive — 5 skills (agent_2_market_intelligence.md)
- Agent 3: Strategy & Scoring — 15 skills, largest by skill count (agent_3_strategy_scoring.md)
- Agent 4: Commercial & Financial — 9 skills (agent_4_commercial_financial.md)
- Agent 5: Content & Response Drafting — 7 skills (agent_5_content_drafting.md)
- Agent 6: Solution & Delivery — 14 skills, largest by task count (agent_6_solution_delivery.md)

**How to apply:** Plugin architecture v1.5. Use cases reference v1.1. Next session: MCP server architecture design — the engineering foundation all 55 skills depend on. Key design question to resolve: localStorage-to-MCP bridge (how Node.js process reads HTML app data).
