# Skill Execution Workflow — Dependency Chain

## Principle

Skills are not independent — they form a pipeline. Each skill's output becomes the next skill's input. The test framework must respect this dependency chain and execute skills in the correct order.

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: DOCUMENT INGESTION (Agent 1)                              │
│                                                                     │
│  ITT Documents ──► Skill 1.1: ITT Extraction                       │
│                        ├── Response Sections (what to answer)       │
│                        ├── Evaluation Framework (how it's scored)   │
│                        ├── Procurement Context (route, value, etc)  │
│                        ├── Scoring Scheme (client marks guide)      │
│                        └── ITT Document records                     │
│                                                                     │
│  ITT Documents ──► Skill 1.5: Procurement Briefing                  │
│                        └── Strategic Briefing Report (narrative)    │
│                                                                     │
│  Extracted Data ──► Skill 1.2: Evaluation Criteria Analysis         │
│                        └── Marks concentration, scoring guidance,   │
│                            section-to-criteria mapping              │
│                                                                     │
│  Contract Docs ──► Skill 1.3: Contract Analysis                     │
│                        └── Obligations, liabilities, red lines      │
│                                                                     │
│  Extracted Data ──► Skill 1.4: Compliance Matrix                    │
│                        └── Requirement-to-section mapping           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SEED DATA (not extracted by skills — must be loaded manually       │
│  or pre-populated by the bid manager via the Execution app)         │
│                                                                     │
│  ● Activity schedule (84 activities with dates, owners,             │
│    dependencies, critical path) — from the methodology engine       │
│  ● Team / resource data (names, roles, allocation)                  │
│  ● Win themes (from strategy / capture phase)                       │
│  ● Governance gates (configured per bid complexity)                 │
│  ● Stakeholders (from capture engagement)                           │
│  ● Compliance requirements (from ITT mandatory reqs — partially     │
│    extracted by Skill 1.1, enriched by bid manager)                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: STRATEGY & INTELLIGENCE (Agent 2 + Agent 3)               │
│                                                                     │
│  Skill 2.1: Client Profiling        ──► Client intelligence        │
│  Skill 2.3: Incumbent Assessment    ──► Incumbent analysis         │
│  Skill 2.4: Competitor Profiling    ──► Battle cards               │
│  Skill 2.5: Stakeholder Mapping     ──► DMU map                    │
│  Skill 3.1: Win Theme Mapping       ──► Theme-to-criteria matrix   │
│  Skill 3.2: PWIN Scoring            ──► PWIN score                 │
│  Skill 3.4: Clarification Strategy  ──► Clarification questions    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: ONGOING MONITORING (Agent 3 — runs repeatedly)            │
│                                                                     │
│  Skill 3.5: Timeline Analysis (UC1) ──► Activity insights, risks   │
│  Skill 3.7: Standup Priorities (UC3) ──► Daily action list         │
│  Skill 3.8: Compliance Coverage (UC4) ──► Coverage gaps, risks     │
│  Skill 3.9: Win Theme Audit (UC5)   ──► Theme coverage scores     │
│  Skill 3.10: Marks Allocation (UC6) ──► Effort rebalancing        │
│  Skill 3.12: Gate Readiness (UC9)   ──► Gate pass/fail/at-risk    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 4: PRODUCTION & REVIEW (Agent 5 + Agent 3)                   │
│                                                                     │
│  Skill 5.1: Response Drafting       ──► Draft response per section │
│  Skill 5.2: Executive Summary       ──► Synthesised exec summary   │
│  Skill 3.11: Review Trajectory (UC7) ──► Score trends per section  │
│  Skill 3.6: Effort Reforecast (UC2) ──► Revised dates, bid cost   │
└─────────────────────────────────────────────────────────────────────┘
```

## What Skills Extract vs What Must Be Seeded

| Data | Source | When Available |
|------|--------|---------------|
| Response sections | **Skill 1.1** extracts from ITT | After ITT Extraction |
| Evaluation framework | **Skill 1.1** extracts | After ITT Extraction |
| Procurement context | **Skill 1.1** extracts | After ITT Extraction |
| Scoring scheme | **Skill 1.1** extracts | After ITT Extraction |
| ITT document records | **Skill 1.1** creates | After ITT Extraction |
| Compliance requirements | **Skill 1.1** partial + bid manager enriches | Partial after extraction, full after manual review |
| Strategic briefing | **Skill 1.5** generates | After Procurement Briefing |
| Evaluation criteria detail | **Skill 1.2** analyses | After Eval Criteria Analysis |
| Contract obligations/risks | **Skill 1.3** extracts | After Contract Analysis |
| **Activity schedule** | **SEED** — methodology engine / bid manager | Must be loaded before Timeline Analysis |
| **Team / resources** | **SEED** — bid manager enters | Must be loaded before resource-dependent skills |
| **Win themes** | **SEED** — from strategy / capture | Must be loaded before Win Theme Audit |
| **Governance gates** | **SEED** — configured per bid | Must be loaded before Gate Readiness |
| **Stakeholders** | **SEED** — from capture engagement | Must be loaded before Stakeholder skills |
| **Response items** | **SEED** — bid manager assigns owners | Must be loaded before production skills |

## Test Execution Order

Tests must run in this order:

### Tier 1: Document Ingestion (no dependencies)
1. `test-itt-extraction.js` — extracts the exam paper
2. `test-procurement-briefing.js` — generates day-one briefing

### Tier 2: Analysis of Extracted Data (depends on Tier 1)
3. `test-evaluation-criteria.js` — deep dive into scoring guidance
4. `test-compliance-coverage.js` — coverage gap analysis

### Tier 3: Seeded Data Tests (depends on Tier 1 + seed data)
5. `test-timeline-analysis.js` — needs activity schedule seeded
6. `test-win-theme-audit.js` — needs win themes seeded
7. `test-gate-readiness.js` — needs governance gates seeded

### Tier 4: Full Pipeline Test
8. `test-full-pipeline.js` — runs Tier 1-3 in sequence against a single pursuit, validates the complete data state at each stage

## Seed Data for ESN Lot 2

The test framework must seed realistic data for skills that can't extract it from documents. This seed data should be:
- **Realistic** for a £500m Emergency Services IT outsourcing bid
- **Consistent** with the extracted ITT data (section references match, dates make sense)
- **Loaded via the Data API** before the dependent skills run
