---
name: Compliance matrix V1 scope
description: Compliance matrix UX deferred from V1 — activity and gates retained, tracking done externally via AI+Excel
type: feedback
---

Compliance matrix is NOT stripped from architecture — only hidden from UX in V1.

**Why:** Technical requirements compliance management is out of scope for V1 product UI, but the compliance *work* still happens externally using AI and Excel. The product must still acknowledge compliance as a required activity and enforce governance gates.

**How to apply:**
- Data model (ComplianceRequirement entity) stays in architecture unchanged
- PRD-01 activity (compliance matrix & requirements mapping) stays — it's real work, just done outside the tool
- Governance hard gates for compliance gaps stay — they still block readiness
- Remove from UX only: View 2 (Client Compliance Matrix), compliance import wizard step, compliance matrix print/export
- Sprint 6 AI compliance scaffolding folds into Plugin Architecture, not a standalone sprint item
- Do NOT delete or restructure the underlying data model — V2 will bring compliance management into the product
