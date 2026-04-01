# SOL Workstream — Technology / Digital Archetype

**Version:** 1.0 | April 2026
**Status:** Draft for review
**Scope:** L2/L3 methodology content for the Solution Design workstream when the bid archetype is Technology / Digital — building or implementing a technical product, platform, or digital service.
**Reference:** Services archetype mapped in `methodology_gold_standard.md`. This document shows what changes.

---

## Archetype Context

The Technology / Digital archetype covers bids where the primary deliverable is a technology product, platform, or digital service — not an outsourced operational service. Examples:

- Custom software development for a government department
- Digital platform implementation (case management, citizen-facing service, data platform)
- IT infrastructure transformation (cloud migration, network modernisation)
- Systems integration programme
- Managed technology service with significant build/implementation component

**Key differences from Services archetype:**
- The "solution" is a technical architecture, not an operating model
- Requirements are user stories / epics / technical specifications, not service specifications
- There is no TUPE (no operational workforce transfers)
- Transition becomes implementation / deployment / go-live, not service handover
- Staffing is a delivery team (developers, architects, testers), not an operational workforce
- Innovation is embedded in the technical approach, not a separate roadmap
- Agile / hybrid delivery methodology replaces the service delivery model

---

## Activity Mapping — What Changes

| SOL Activity | Services Archetype | Technology/Digital Archetype | Change |
|---|---|---|---|
| SOL-01 | Requirements analysis & interpretation | Requirements analysis & interpretation | **Modified** — user stories, epics, technical specs |
| SOL-02 | Current operating model assessment | Current technology landscape assessment | **Modified** — systems, integrations, technical debt |
| SOL-03 | Target operating model design | Technical architecture & solution design | **Renamed + Modified** — architecture, not operating model |
| SOL-04 | Service delivery model design | Delivery methodology & approach | **Renamed + Modified** — Agile/hybrid, not service lines |
| SOL-05 | Technology & digital approach | *Absorbed into SOL-03* | **Deactivated** — tech IS the core solution in SOL-03 |
| SOL-06 | Staffing model & TUPE analysis | Delivery team design | **Modified** — no TUPE, delivery team structure |
| SOL-07 | Transition & mobilisation approach | Implementation & deployment plan | **Renamed + Modified** — go-live, not service handover |
| SOL-08 | Innovation & continuous improvement | *Embedded in SOL-03* | **Deactivated** — innovation is the tech approach itself |
| SOL-09 | Social value proposition | Social value proposition | **Unchanged** — still mandatory scored section |
| SOL-10 | Evidence strategy & case study identification | Evidence strategy & case study identification | **Minor modification** — tech case studies, team CVs |
| SOL-11 | Solution design lock | Solution design lock | **Unchanged** — same consolidation and lock process |
| SOL-12 | Solution risk identification & analysis | Solution risk identification & analysis | **Minor modification** — tech delivery risks |

**Active activities: 10** (SOL-05 and SOL-08 deactivated / absorbed)

---

## SOL-01 — Requirements Analysis & Interpretation (Technology/Digital)

### What changes from Services
- Requirements are expressed as user needs, user stories, epics, and technical specifications — not service specifications
- Functional vs non-functional requirements distinction is critical
- API and integration requirements are first-class concerns
- Accessibility requirements (WCAG 2.1 AA) mandatory for citizen-facing services
- GDS Service Standard and Technology Code of Practice apply for central government

### L2/L3 Structure

**L2.1: Requirements Decomposition**
1. Decompose ITT into structured requirements — functional requirements, non-functional requirements (performance, security, accessibility, scalability), integration requirements, data requirements
2. Map requirements to user needs and user journeys — who are the users, what do they need, how does the system serve them?
3. Identify technical constraints, dependencies, and assumptions — existing systems, mandated platforms, data standards, security classifications

**L2.2: Requirements Interpretation & Feasibility**
1. Interpret requirements against technical landscape and user context — what does the client really need vs what they've specified?
2. Assess technical feasibility per requirement area — can we build this, with what technology, at what complexity?
3. Synthesise requirements interpretation document — prioritised, feasibility-assessed, user-need-aligned

### Inputs
- SAL-06: Capture plan (locked)
- SAL-06.1.2: ITT documentation analysis summary
- SAL-05: Evaluation criteria matrix with scoring approach
- External: ITT documentation — technical specification, user research, service assessment
- External: GDS Service Standard, Technology Code of Practice, WCAG 2.1 AA

### Outputs
- Requirements interpretation document (functional, non-functional, integration, user needs mapped, feasibility assessed)

### Consumers
- SOL-03, SAL-07, SOL-06, SOL-07

---

## SOL-02 — Current Technology Landscape Assessment (Technology/Digital)

### What changes from Services
- Focus shifts from operating model (org, people, performance) to technology landscape (systems, data, integrations, technical debt)
- No organisational structure or workforce assessment (no TUPE)
- The question becomes: "What technology exists today that we must integrate with, migrate from, or replace?"

### L2/L3 Structure

**L2.1: Current Systems & Data Landscape**
1. Map current technology estate — systems, platforms, databases, infrastructure, hosting, licensing
2. Assess integration landscape — how current systems connect, APIs, data flows, dependencies on other programmes
3. Assess data landscape — data stores, data quality, data ownership, data standards, data migration complexity

**L2.2: Technical Debt & Constraints Assessment**
1. Assess technical debt and legacy risk — end-of-life systems, unsupported platforms, security vulnerabilities, maintainability
2. Identify constraints and mandated platforms — what must be retained, what client infrastructure we must use, security boundaries
3. Synthesise current technology landscape assessment — the as-is baseline for architecture decisions

### Inputs
- SAL-01: Customer intelligence briefing
- External: ITT documentation — technical environment, existing systems, integration requirements
- External: Client technical documentation (if provided) — architecture diagrams, data dictionaries, API specifications

### Outputs
- Current technology landscape assessment (systems, data, integrations, technical debt, constraints)

### Consumers
- SOL-03, SOL-07, COM-01

---

## SOL-03 — Technical Architecture & Solution Design (Technology/Digital)

### What changes from Services
- This is the core activity — it replaces both SOL-03 (TOM) and SOL-05 (Technology) from the Services archetype
- The output is a technical architecture, not an operating model
- Includes application architecture, data architecture, infrastructure architecture, security architecture, and integration architecture
- The solution positioning decision still applies but is framed differently: buy/configure COTS vs build bespoke vs hybrid

### L2/L3 Structure

**L2.1: Solution Vision & Architecture Principles**
1. Determine solution approach — buy/configure COTS platform, build bespoke, hybrid, or integrate existing — with rationale for this opportunity
2. Establish architecture principles — cloud-native, API-first, open standards, accessibility, security-by-design, GDS-aligned
3. Define solution scope and boundary — what we build vs what we integrate with vs what the client provides

**L2.2: Technical Architecture Design**
1. Design application architecture — services, components, modules, user interfaces, business logic, data access
2. Design data architecture — data model, data stores, data flows, integration patterns, data migration approach
3. Design infrastructure and hosting architecture — cloud platform, environments, deployment pipeline, scalability, resilience, disaster recovery
4. Design security architecture — authentication, authorisation, encryption, data classification, penetration testing, accreditation approach

**L2.3: Solution Validation & Prototyping**
1. Map solution to requirements — demonstrate how the architecture addresses every functional and non-functional requirement
2. Map solution to win themes — demonstrate how technical choices deliver competitive differentiation
3. Prototype or prove key technical risks — demonstrate feasibility of high-risk components (if time permits and evaluation rewards it)
4. Validate architecture with bid team — confirm as baseline for delivery planning, costing, and proposal

### Inputs
- SOL-01: Requirements interpretation document
- SOL-02: Current technology landscape assessment
- SAL-06: Capture plan (locked) — win strategy
- SAL-04: Win theme document
- SAL-02.3.1: Transformational opportunity register
- External: ITT documentation — technical specification
- External: Cloud platform capabilities, COTS product assessments, partner technology offerings

### Outputs
- Technical architecture & solution design (application, data, infrastructure, security — validated)

### Consumers
- SOL-04, SOL-06, SOL-07, SOL-11, COM-01, GOV-02

---

## SOL-04 — Delivery Methodology & Approach (Technology/Digital)

### What changes from Services
- Replaces service delivery model with delivery methodology
- Agile, hybrid, or waterfall approach — how the solution will be built, tested, and delivered
- Sprint/iteration planning, release management, testing strategy, DevOps/CI-CD approach
- Quality assurance is testing strategy, not service quality framework

### L2/L3 Structure

**L2.1: Delivery Methodology Design**
1. Define delivery methodology — Agile (Scrum/Kanban), hybrid, SAFe, or waterfall — with rationale for this programme
2. Design sprint/iteration structure — cadence, ceremonies, artefacts, definition of done, release planning
3. Design DevOps and CI/CD approach — build pipeline, automated testing, deployment automation, environment management

**L2.2: Quality & Assurance Framework**
1. Design testing strategy — unit, integration, system, performance, security, accessibility, UAT — approach, automation, tools
2. Design acceptance and go-live criteria — what "done" looks like, client sign-off process, staged rollout approach
3. Validate delivery methodology — confirm it fits the client's governance expectations, is costable, and the team can execute it

### Inputs
- SOL-03: Technical architecture & solution design
- SOL-01: Requirements interpretation document
- SAL-05: Evaluation criteria matrix with scoring approach
- External: Client governance and assurance expectations
- External: GDS Service Standard assessment framework (if applicable)

### Outputs
- Delivery methodology & approach (methodology, sprint structure, DevOps, testing strategy, acceptance criteria)

### Consumers
- SOL-06, SOL-07, SOL-11, COM-01

---

## SOL-05 — DEACTIVATED (Technology/Digital)

Technology & digital approach is absorbed into SOL-03 for this archetype. SOL-03 IS the technology solution.

---

## SOL-06 — Delivery Team Design (Technology/Digital)

### What changes from Services
- No TUPE — there is no transferring operational workforce
- Focus is on the delivery team: developers, architects, testers, product managers, scrum masters, UX designers
- Key personnel CVs are critical for scoring
- Security clearance requirements often apply (SC, DV for government systems)
- Onshore/offshore/nearshore model may apply

### L2/L3 Structure

**L2.1: Delivery Team Structure**
1. Design delivery team structure — roles, seniority, reporting lines, mapped to the delivery methodology and technical architecture
2. Define skills and capability requirements per role — technology skills, domain knowledge, clearances, certifications
3. Define team scaling profile — how the team ramps up, peak team during build, run team post-go-live

**L2.2: Team Sourcing & Key Personnel**
1. Identify key personnel — named individuals for critical roles (lead architect, delivery manager, test lead, security lead) with CVs
2. Assess sourcing approach — permanent, contractor, partner-provided, offshore/nearshore mix with rationale
3. Validate delivery team — confirm capability to deliver the architecture, costable for COM-01, key personnel CVs substantiate claims

### Inputs
- SOL-03: Technical architecture & solution design
- SOL-04: Delivery methodology & approach
- External: ITT documentation — team requirements, key personnel requirements, clearance requirements
- External: Our workforce and partner capability — available people, skills, clearances

### Outputs
- Delivery team design (structure, roles, skills, scaling, key personnel CVs, sourcing approach)

### Consumers
- SOL-07, SOL-11, COM-01, SOL-12

---

## SOL-07 — Implementation & Deployment Plan (Technology/Digital)

### What changes from Services
- "Transition" becomes "implementation" — building and deploying the solution, not handing over an operational service
- No TUPE transfer process
- Focus on: development phases, environments, testing stages, data migration, integration testing, go-live, parallel running, legacy decommission
- Rollout strategy: big bang, phased by feature, phased by geography/user group, pilot then scale

### L2/L3 Structure

**L2.1: Implementation Planning**
1. Design implementation phases — discovery, alpha, beta, live (GDS) or equivalent phasing — with milestones and deliverables per phase
2. Plan data migration — extraction, transformation, loading, validation, rollback approach, parallel running period
3. Plan integration delivery — phased integration testing, partner system interfaces, client system connections, end-to-end testing

**L2.2: Deployment & Go-Live**
1. Design rollout strategy — big bang, phased, pilot-then-scale — with rationale and risk assessment
2. Design go-live support and early-life management — hypercare period, incident management, defect resolution, performance monitoring
3. Validate implementation plan — achievable within timeline, costable, risks identified, client dependencies clear

### Inputs
- SOL-03: Technical architecture & solution design
- SOL-04: Delivery methodology & approach
- SOL-06: Delivery team design
- SOL-02: Current technology landscape assessment
- External: ITT documentation — implementation timeline, go-live requirements, parallel running expectations

### Outputs
- Implementation & deployment plan (phases, data migration, integration, rollout, go-live support)

### Consumers
- SOL-11, SOL-12, COM-01, DEL-01

---

## SOL-08 — DEACTIVATED (Technology/Digital)

Innovation & continuous improvement is embedded in SOL-03 for this archetype. The technology approach IS the innovation. Post-go-live continuous improvement and product evolution is covered within the delivery methodology (SOL-04) as backlog management and iterative enhancement.

---

## SOL-09 — Social Value Proposition (Technology/Digital)

### What changes from Services
- **Unchanged.** Social value is still mandatory (PPN 06/20, minimum 10% weighting).
- Commitments may skew toward: digital skills, STEM apprenticeships, SME subcontracting, accessibility, environmental impact of cloud hosting, open source contributions.
- Same L2/L3 structure as Services archetype.

---

## SOL-10 — Evidence Strategy & Case Study Identification (Technology/Digital)

### What changes from Services
- **Minor modification.** Same structure but evidence emphasis shifts:
  - Case studies focus on similar technology implementations, similar scale, similar client domain
  - Key personnel CVs are often the primary evidence (named individuals with specific tech skills)
  - Platform/product credentials — certifications, accreditations, security assessments for COTS products
  - GDS assessment outcomes if applicable — past alpha/beta/live assessments
- Same L2/L3 structure as Services archetype.

---

## SOL-11 — Solution Design Lock (Technology/Digital)

### What changes from Services
- **Unchanged.** Same consolidation and lock process. Components being consolidated are different (technical architecture instead of TOM) but the lock mechanism is identical.
- Same L2/L3 structure as Services archetype.

---

## SOL-12 — Solution Risk Identification & Analysis (Technology/Digital)

### What changes from Services
- **Minor modification.** Same structure but risk categories shift:
  - Technology delivery risk — can we build this on time, on budget?
  - Integration risk — will systems connect as designed?
  - Data migration risk — data quality, volume, transformation complexity
  - Key personnel risk — dependency on named individuals, clearance delays
  - No TUPE or operational workforce risk
  - Security accreditation risk — will the system pass accreditation in time for go-live?
- Same L2/L3 structure as Services archetype.

---

*Technology/Digital archetype drafted — Session 12, 2026-04-01*
*For review: compare with Services archetype in methodology_gold_standard.md*
