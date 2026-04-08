---
name: Session 15 multi-product architecture
description: 2026-04-04 — MCP server must be multi-product platform service; Qualify data model mapped; shared pursuit entities defined; AI enrichment docs reviewed
type: project
---

## Session 15 — Multi-Product Platform Architecture

### MCP server is a platform service, not product-specific

The MCP server cannot serve Bid Execution alone. Three products share the same pursuit lifecycle data:
- **PWIN Qualify** — "Should we pursue?" (pre-capture, lead generation, website CTA)
- **Win Strategy** — "How do we win?" (capture phase, consulting workshops, not yet designed)
- **Bid Execution** — "Execute the bid" (ITT phase, 84 activities)

Data flows downstream: Qualify → Win Strategy → Bid Execution. The MCP server needs pursuit-level shared entities accessible to all products.

### PWIN Qualify data model (from prototype + design docs)

**Core entities:** Pursuit Context (org, opp, sector, TCV, oppType, route, stage, incumbent, competitors, importance), 6 Categories with dynamic weight profiles (services/technology/advisory), 24 Questions with 4-point Likert scale + rubrics + inflation signals, Positions (scores), Evidence (free text), AI Reviews (verdict/suggestedScore/confidence/narrative/challengeQuestions/captureActions).

**Design doc contradiction noted:** Design doc (Section 08) says dynamic weights were rejected for comparability reasons. Built app implements them via WEIGHT_PROFILES. Decision was reversed after design doc was written.

**Persistence:** JSON file export/import (no localStorage). No MCP integration yet.

### Cross-product data overlap is substantial

Every Qualify category maps to Bid Execution SAL activities:
- Competitive Positioning → SAL-03, SAL-04 (competitor analysis, win themes)
- Procurement Intelligence → SAL-05, SAL-06, SAL-07 (evaluation framework, ITT analysis)
- Stakeholder Strength → SAL-10 (stakeholder engagement)
- Organisational Influence → SAL-10 (deeper layer), SAL-06.2 (DQC)
- Value Proposition → SAL-04, SAL-06.2 (win themes, strategy synthesis)
- Pursuit Progress → SAL-10 (engagement tracking), SAL-01 (customer intel)

### Shared pursuit entities identified

| Entity | Created by | Enriched by | Consumed by |
|---|---|---|---|
| Pursuit (ID, client, opportunity, sector, TCV, type) | Qualify | Win Strategy, Bid Execution | All |
| PWIN Score (category scores, overall, weight profile) | Qualify | Win Strategy, Bid Execution | All |
| Competitive Positioning | Qualify (maturity) | Win Strategy (full) | Bid Execution SAL-03 |
| Stakeholder Map | Qualify (maturity) | Win Strategy (full) | Bid Execution SAL-10 |
| Buyer Values | Qualify (gaps) | Win Strategy (full) | Bid Execution SAL-01.2 |
| Win Themes | — | Win Strategy (creates) | Bid Execution SAL-04 (imports) |
| Client Intelligence | — | Win Strategy (builds) | Bid Execution SAL-01 |
| Capture Plan | — | Win Strategy (produces) | Bid Execution SAL-06.4 (imports) |

### Two AI enrichment documents reviewed (both incomplete)

**AI Enrichment Review (PWIN_AI_Enrichment_Review.xlsx):**
- 7 sheets: sector enrichment (5 sectors), opportunity type intelligence (5 types), sector×opp matrix (7 intersections), few-shot examples (4 worked examples), output schema (11 fields), system prompt core (5 sections)
- Content is complete and high quality. Review/approval columns not filled in.
- This is the AI assurance reviewer's brain — maps to a Qualify product skill.
- Sector and opportunity knowledge should be SHARED across the platform, not Qualify-specific.

**AI Design Proforma (BWIN Qualify_AI Design_Proforma_v2.xlsx):**
- 8 sheets: 51 data points across 8 sections, 20 reasoning rules (winnability/desirability/deliverability/intelligence quality/financials), template schema, source hierarchy, confidence model (H/M/L/U), success factors, design notes
- This is the intelligence-gathering phase (Phase 1) spec — maps directly to Agent 1 + Agent 2 capabilities
- The 51 data points overlap heavily with Bid Execution entities
- The confidence model (H/M/L/U ratings per data point) is NEW and valuable — should be adopted platform-wide
- 8 open design decisions in Sheet 8 (completeness threshold, competitor sourcing, BIP knowledge base, fatal flaw override, persona selection, data security, rules versioning, V1 scope)

### Architectural decisions confirmed

1. **One server, one data store, multiple products** — not separate servers per product
2. **Shared knowledge base** — sector intelligence, opportunity type intelligence populated once, consumed by all products
3. **Existing Bid Execution MCP tools (47) don't change** — they become product-specific tools within a multi-product server
4. **The 55 skills already defined cover most of what the Qualify AI needs** — it's the same agent capabilities at an earlier lifecycle stage

### MCP server architecture completed (same session)

Full spec: `mcp_server_architecture.md` (v1.0). Single Node.js process, dual interface (HTTP Data API + stdio MCP), JSON file store per pursuit. 78 MCP tools (49 read + 29 write). localStorage replaced. Confidence model (H/M/L/U) adopted platform-wide. Field-level permissions enforced server-side. ~2,300 lines estimated, 13-step build sequence.

### PWIN AI platform design is now COMPLETE

All design docs done: 6 agent specs (55 skills), plugin architecture v1.5, MCP server v1.0, AI use cases v1.1, suitability assessment.

### What happens next

**Implementation:** MCP server build Steps 1-8 (skeleton → file store → Data API → read/write tools → permissions → Agent 1 Skill 1 end-to-end → Agent 3 UC1 end-to-end).

**Practitioner review needed:** Two enrichment spreadsheets (platform-level knowledge, review columns empty).

**Design backlog:** Proforma/template library, module renumbering, competitive dialogue methodology, SQ stage methodology.
