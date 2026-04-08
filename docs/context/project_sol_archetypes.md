---
name: SOL workstream archetypes
description: 2026-04-01 — three archetypes for SOL workstream: Services (mapped), Technology/Digital, Consulting/Advisory. Same activity codes, different L2/L3 content. Option B chosen.
type: project
---

## Decision

Three bid archetypes, each with archetype-specific SOL workstream L2/L3 content:
1. **Services / Outsourcing** — mapped in gold standard (Session 12). Operating model, service delivery, TUPE, transition, innovation.
2. **Technology / Digital** — technical architecture, delivery methodology, implementation/deployment, no TUPE.
3. **Consulting / Advisory** — approach/methodology, engagement model, team CVs, lighter solution.

## Approach (Option B — validated and expanded)

Same activity codes across all archetypes. L2/L3 content varies by archetype. Archetype selected in wizard Stage 2 loads appropriate methodology content. Some activities deactivated for certain archetypes via existing wizard mechanism.

**Validated 2026-04-02:** The assumption that only SOL varies was partially wrong. Three workstreams need full archetype variant documents:

| Workstream | Variant Document |
|---|---|
| SOL | methodology_sol_technology_archetype.md, methodology_sol_consulting_archetype.md |
| COM | methodology_com_archetype_variants.md |
| DEL | methodology_del_archetype_variants.md |

15 additional activities across SAL, LEG, SUP, BM, PRD, POST have archetype notes in the gold standard for minor/guidance-level changes.

## How to apply

- Services archetype content is in methodology_gold_standard.md (authoritative)
- SOL, COM, DEL variants in separate documents
- Other workstreams: archetype notes embedded in gold standard activities
- Product implementation: three levels of wizard adaptation — (1) activity deactivation, (2) L2/L3 content swap, (3) guidance note adjustment
