---
name: Output format — web-native with Office export
description: 2026-04-04 — skill outputs should be rich web-native content internally (structured markdown/HTML) with one-click export to Office 365 formats (.pptx, .docx, .pdf) for corporate compliance
type: feedback
---

Skill outputs should not target Office formats directly. The platform produces rich, interactive, data-connected content as the primary experience. Corporate format requirements are met via an export layer.

**Why:** Existing corporate processes require Office 365 (.pptx gate packs, .docx narratives, .pdf submissions). But AI-generated content can be far richer — live dashboards, drillable data, embedded RAG status. Targeting Office directly means automating the old process. Web-native with Office export means disrupting the experience while respecting the workflow.

**How to apply:**
- Skill output format = structured markdown or HTML internally
- Rendering/export layer converts to .pptx / .docx / .pdf as needed
- One source of truth, multiple output formats, zero rework
- The user works in the platform. The governance board receives the pack in the format they expect.
- Architecture decision: do NOT build Office XML generation into skills. Build a separate export module that renders any structured output into the required format.
- This is a commercial differentiator for BidEquity — "live intelligence environment for the bid team, corporate-compliant deliverables for governance"
