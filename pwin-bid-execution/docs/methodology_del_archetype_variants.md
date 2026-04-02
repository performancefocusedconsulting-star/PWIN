# DEL Workstream — Archetype Variants

**Version:** 1.0 | April 2026
**Status:** Draft for review
**Scope:** L2/L3 methodology content changes for the Programme & Delivery workstream when the bid archetype is Technology/Digital or Consulting/Advisory.
**Reference:** Services archetype mapped in `methodology_gold_standard.md`. This document shows what changes.

---

## Activity Mapping — What Changes

| DEL Activity | Services | Technology/Digital | Consulting/Advisory |
|---|---|---|---|
| DEL-01 Delivery risk & assumptions | Baseline | **Minor** — risk categories shift | **Minor** — risk categories shift |
| DEL-02 Mobilisation & implementation | Baseline | **Modified** — deployment planning, not service transition | **Modified** — very light, team onboarding only |
| DEL-03 Performance framework & KPIs | Baseline | **Modified** — delivery milestones, not operational KPIs | **Modified** — deliverable quality, not SLAs |
| DEL-04 Resource & capacity plan | Baseline | **Minor** — delivery team, not operational workforce | **Minor** — consultant team, simpler |
| DEL-05 Business continuity & exit | Baseline | **Modified** — system DR + code/IP handover | **Deactivated or minimal** |
| DEL-06 Risk mitigation & residual | Baseline | **Same** | **Same** |

---

## DEL-02 — Mobilisation & Implementation Planning (Technology/Digital)

### What changes
- Mobilisation becomes **deployment planning** — standing up development environments, onboarding the delivery team, establishing the Agile cadence, not transitioning an operational service
- No TUPE transfer process
- Focus on: environment provisioning, team onboarding, client access, development infrastructure setup, sprint zero planning
- Lighter governance — Agile ceremonies replace programme boards in early stages

### L2/L3 Structure

**L2.1: Deployment Planning**
1. Plan development environment setup — infrastructure provisioning, CI/CD pipeline, test environments, access and security
2. Plan team onboarding and sprint zero — Agile team mobilisation, backlog preparation, client introductions, ways of working agreement

**L2.2: Deployment Readiness**
1. Assess deployment readiness — are environments available, is the team onboarded, is the backlog ready for sprint 1?
2. Validate deployment plan — achievable, feeds the proposal response

---

## DEL-02 — Mobilisation & Implementation Planning (Consulting/Advisory)

### What changes
- Mobilisation is **very light** — getting consultants on-site, productive, and building client relationships
- Typically 1-2 weeks, not months
- Focus on: client introductions, access (physical and systems), initial discovery/immersion, team ways of working
- No programme governance setup — consulting engagements use simple steering groups

### L2/L3 Structure

**L2.1: Team Mobilisation**
1. Plan consultant onboarding — client introductions, access, induction, initial immersion period
2. Plan early deliverables — what we produce in the first 2-4 weeks to build credibility and momentum (typically a discovery report or initial assessment)

---

## DEL-03 — Performance Framework & KPIs/SLAs (Technology/Digital)

### What changes
- Performance is **delivery milestones and acceptance criteria**, not operational KPIs/SLAs
- No service credits for underperformance — instead, there are acceptance gates and defect remediation obligations
- Performance measured by: delivered on time, passed UAT, met acceptance criteria, defect rates post-go-live
- Reporting is sprint-level (velocity, burn-down, defect rates) not monthly service performance

### L2/L3 Structure

**L2.1: Delivery Performance Framework**
1. Design acceptance criteria framework — what "done" looks like per milestone, UAT approach, client sign-off process
2. Design delivery performance metrics — velocity, sprint completion, defect rates, code quality metrics, deployment frequency
3. Assess delivery confidence — can we meet the acceptance criteria and timeline?

---

## DEL-03 — Performance Framework & KPIs/SLAs (Consulting/Advisory)

### What changes
- Performance is **deliverable quality and client satisfaction**, not operational KPIs
- No SLAs, no service credits
- Measured by: deliverable acceptance, milestone completion, client feedback, engagement satisfaction
- Reporting is milestone-based — "deliverable X accepted by steering group on date Y"

### L2/L3 Structure

**L2.1: Engagement Performance Framework**
1. Design deliverable acceptance framework — quality criteria per deliverable, client review and sign-off process
2. Design engagement satisfaction mechanism — how we track client satisfaction throughout (feedback loops, steering group pulse checks)
3. Assess delivery confidence — can we meet deliverable quality expectations with this team?

---

## DEL-05 — Business Continuity & Exit Planning (Technology/Digital)

### What changes
- BC/DR applies to the **built system**, not an operational service workforce
- DR is about system resilience — failover, backup, data recovery (designed in SOL-05 security architecture, operationalised here)
- Exit is about **code handover, documentation, IP transfer, knowledge transfer** — not reverse TUPE and service handback
- May include open source obligations, licensing handover, data return

### L2/L3 Structure

**L2.1: System Resilience & DR**
1. Operationalise the DR approach from SOL-05 — failover testing, backup procedures, recovery runbooks, RTO/RPO validation

**L2.2: Exit & Handover**
1. Design code and IP handover plan — source code, documentation, build procedures, deployment guides, training for client's internal team
2. Design data return and system decommission approach — data extraction, format, archival, system shutdown

---

## DEL-05 — Business Continuity & Exit Planning (Consulting/Advisory)

### What changes
- **Largely deactivated.** Consulting engagements don't have BC/DR requirements for operational services.
- BC is limited to: "what if a key consultant becomes unavailable?" — covered by resource risk in DEL-01
- Exit is project closedown: final deliverable handover, knowledge transfer session, lessons learned, file archive
- May be reduced to a single task rather than a full activity

### L2/L3 Structure (minimal)

**L2.1: Engagement Closedown**
1. Plan engagement closedown — final deliverable handover, knowledge transfer session, file archive, client satisfaction survey

---

*DEL archetype variants drafted — Session 12+, 2026-04-02*
*For review: compare with Services archetype in methodology_gold_standard.md*
