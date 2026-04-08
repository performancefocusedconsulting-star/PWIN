---
name: ITT Ingestion Layer — MVP scope decision
description: Scope cut for data model revision — ResponseSection, EvaluationFramework, ITTDocument are in; Requirement, ClarificationItem deferred to V2
type: project
---

## MVP Scope (decided 2026-03-27)

The Architecture v6 Data Model Revision proposed 5 new entities. User decided to trim to 3 for MVP to avoid god-project risk.

### In scope (build now)
- **ResponseSection** — the exam paper, separating question definition from response production
- **EvaluationFramework** — single record per bid, scoring methodology
- **ITTDocument** — document registry with parsed status
- **ResponseItem modified** — linked to ResponseSection, question fields migrated out
- **Bid extended** — procurement context fields (procurementRoute, portalPlatform, etc.)
- **Auto-migration** — existing ResponseItems with question fields get ResponseSections auto-created on load

### Deferred to V2
- **Requirement** — full requirements extraction, traceability matrix, coverage analysis. Too large for MVP; a product in its own right.
- **ClarificationItem** — manage outside the app for now; ingest status only if needed later.
- **Requirements Register view** — depends on Requirement entity
- **Traceability Matrix view** — depends on Requirement entity

**Why:** Product is not finished yet. Adding Requirements pulls in 2 new complex views, many-to-many rendering, and cross-entity linking before existing views are battle-tested. Better to live with the exam paper / answer sheet split first, then build Requirements informed by real usage.

**How to apply:** Do not build Requirement or ClarificationItem entities. ComplianceRequirement stays unchanged (no FK to Requirement until Requirement exists). ResponseSection.linkedRequirementIds is omitted from MVP schema. No new views added to Submissions module — just update Response Register to join through ResponseSection.
