---
name: Data migration approach — auto-migrate, don't break existing data
description: When restructuring data model, auto-migrate existing records silently rather than requiring re-entry
type: feedback
---

When splitting or restructuring entities, auto-migrate existing data on load. Don't force users to re-enter data they've already created.

**Why:** Users may have been testing with real bid data. A clean break wastes their work.

**How to apply:** For the ResponseItem → ResponseSection split, on app load detect ResponseItems with legacy question fields (questionText, evaluationWeightPct, wordLimit), auto-create linked ResponseSections, and strip the duplicated fields. Silent, zero-effort migration.
