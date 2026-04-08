---
name: Session 13 AI use cases
description: 2026-04-02 — 20 AI intelligence use cases designed, three-layer architecture, MCP alignment, combined roadmap
type: project
---

## Session 13 — AI Use Cases and Plugin Architecture Alignment

**20 AI intelligence use cases** designed across 5 themes (Schedule, Proposal Quality, Commercial/Governance, Data Ingestion, Team Performance). All 24 entities covered. UC8/UC17 consolidated (duplicate). Theme E (UC16-20) deferred to V2/V3 (needs multi-bid data).

**Three-layer architecture confirmed:**
- Layer 1: Bid Execution App (data + UI, single HTML file)
- Layer 2: AI Skills (productivity, from suitability assessment — Plugin Roles 2 & 3)
- Layer 3: AI Intelligence (supervisory, 20 use cases — Plugin Role 1)
- MCP server is shared infrastructure between Layers 2 and 3

**Documents updated:**
- Architecture v6 (Session 13 added)
- Plugin architecture (v1.3 → v1.4): new MCP tools, AIInsight schemas, build sequence aligned
- ai_use_cases_reference.html created (complete 20 use case specification)

**Build priority (intelligence):** UC1 (Timeline) + UC4 (Compliance) first → UC3 + UC9 + UC6 second → remaining interleaved with skills.

**Key challenges:** single-file/plugin boundary, MCP query granularity, scheduled triggers (V2), context window management, Theme E data maturity.

**Why:** MCP server architecture is the next design conversation.
