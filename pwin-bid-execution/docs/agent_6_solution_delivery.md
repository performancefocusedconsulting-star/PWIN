# Agent 6: Solution & Delivery Design

**Version:** 1.0 | April 2026
**Status:** Design specification — authoritative input for skill implementation
**Parent document:** `pwin_architect_plugin_architecture.md` (v1.5, Section 4.2a)
**Data model authority:** `bid_execution_architecture_v6.html`
**Insight skill specs:** `ai_use_cases_reference.html` (v1.1, UC8)

---

## 1. Agent Identity

**Purpose:** Supports solution architecture, operating model design, transition planning, staffing models, technology architecture, and supply chain management. The largest agent by task count but lowest AI reduction — solution design is where human expertise is most critical. AI does the structural work; humans do the creative design work.

**System prompt essence:** "You are a solution design and delivery planning specialist for UK public sector services contracts. You support the design of operating models, staffing structures, technology architectures, transition plans, and delivery frameworks. You accelerate design work by structuring requirements, identifying patterns, and producing frameworks for human specialists to refine. You never replace domain expertise — you amplify it."

**Operating principles:**
- Solution design requires human expertise. AI accelerates, humans decide.
- Always trace design decisions back to requirements — every element of the solution must link to what the client asked for.
- Flag design gaps rather than filling them with assumptions. A gap flagged is a risk managed; a gap filled silently is a liability.
- Distinguish between compliance-level design (minimum to pass) and differentiation-level design (win themes landed in the solution).
- Supply chain management involves commercial relationships — AI handles the structural and analytical work, not the negotiation.

---

## 2. Agent Configuration

**Tools available:**

| Tool | Purpose |
|---|---|
| `get_response_sections` | Read extracted requirements (the foundation for all solution design) |
| `get_evaluation_framework` | Read evaluation methodology and scoring criteria |
| `get_win_themes` | Read win themes for solution alignment |
| `get_risks` | Read risk register for solution risk context |
| `get_team_summary` | Read bid team composition |
| `get_team_member` | Read individual team member details |
| `get_compliance_requirements` | Read compliance data for solution coverage mapping |
| `get_activities_by_workstream` | Read activity status for solution workstream tracking |
| `get_bid_library_match` | Search bid library for reusable solution components (placeholder) |
| `update_activity_insight` | Write AI-generated insight to methodology activities |
| `add_risk_flag` | Write risk flags from solution/delivery analysis |
| `create_standup_action` | Generate actions for bid team from solution analysis |
| `generate_report_output` | Store narrative reports (solution documents, design packs) |
| Template populator | Populate operating model templates, staffing templates, transition plans |

**Tools NOT available (by design):**
- Web search (that's Agent 2)
- Spreadsheet/financial calculation tools (that's Agent 4)
- Response drafting tools (that's Agent 5)
- Document extraction from uploaded files (that's Agent 1)

**Knowledge scope:**
- Existing bid data via MCP read tools (requirements, evaluation framework, win themes, risks, team)
- UK public sector service delivery conventions (operating model patterns, TUPE obligations, security clearance tiers, social value frameworks)
- Solution architecture patterns for government services contracts (outsourcing, managed services, transformation programmes)
- Bid library of previous solution designs (placeholder — reusable components, frameworks, templates)

---

## 3. Skills

Agent 6 owns 14 skills: 13 productivity skills and 1 insight skill. This is the LARGEST agent by skill count.

### 3.1 Productivity Skills — Solution Design (6 skills)

---

#### Skill 1: Current State Assessment (`current-state`)

**Command:** `/pwin:current-state`
**Trigger:** Human-invoked. Typically run early in the solution workstream when the bid team begins analysing the incumbent environment.
**Depends on:** Agent 1 (ITT extraction) — needs requirements and specification data. Agent 2 (Market Intelligence) — benefits from incumbent operating model intelligence.
**Covers:** SOL-02.1.1-3, SOL-02.2.1-3

**What it does:**

Maps the current organisational structure, workforce, technology landscape, and service performance of the incumbent delivery environment. Produces a structured current state assessment that identifies day-one inheritance and transition implications.

**Process:**

```
Step 1: Organisational structure mapping
  — Read requirements and specification data via get_response_sections()
  — Extract references to current organisational structure, teams, reporting lines
  — Map current service lines, functional areas, management layers
  — Identify client-retained functions vs outsourced functions

Step 2: Workforce assessment
  — Extract workforce data from ITT documentation (TUPE list, staff numbers, roles, grades)
  — Assess workforce composition: permanent/contingent, clearance levels, location
  — Identify skills concentrations and single points of failure
  — Flag any TUPE consultation timeline constraints

Step 3: Technology landscape review
  — Extract technology references from specification/requirements
  — Map current systems, platforms, tools, licences
  — Assess technology ownership: client-owned, incumbent-owned, third-party
  — Identify day-one technology dependencies and access requirements

Step 4: Service performance assessment
  — Extract current KPIs/SLAs from contract documentation
  — Identify performance gaps flagged in the ITT (reasons for re-procurement)
  — Map pain points the client wants addressed (signals from evaluation criteria)
  — Assess current service maturity level

Step 5: Operating model documentation
  — Consolidate findings into current state operating model view
  — Document governance, escalation, reporting structures
  — Map interfaces with client organisation

Step 6: Transition implications
  — Identify day-one inheritance items (staff, systems, contracts, data)
  — Flag items requiring immediate action at contract start
  — Assess transition complexity: simple lift-and-shift vs transformation
  — Write risk flags via add_risk_flag() for critical inheritance items
```

**Output template:**

```
Current State Assessment
========================
Source documents reviewed:    [count]
Organisational units mapped:  [count]
Workforce size:              [count] FTEs ([TUPE transferring/not applicable])
Technology systems:          [count] systems ([client-owned/incumbent-owned/third-party])

ORGANISATIONAL STRUCTURE
  Service lines:             [list]
  Management layers:         [count]
  Client-retained functions: [list]
  Outsourced functions:      [list]

WORKFORCE PROFILE
  Total headcount:           [count]
  Permanent:                 [count] | Contingent: [count]
  Security cleared:          [count] at [tier]
  Key roles:                 [list of critical roles]
  TUPE status:               [applicable/not applicable/partial]
  TUPE consultation deadline:[date if applicable]

TECHNOLOGY LANDSCAPE
  Client-owned systems:      [list]
  Incumbent-owned systems:   [list — transition risk]
  Third-party contracts:     [list — novation/re-procurement required]
  Day-one access requirements: [list]

CURRENT PERFORMANCE
  KPIs met:                  [count]/[total]
  Known pain points:         [list from ITT signals]
  Service maturity:          [assessment]

TRANSITION IMPLICATIONS
  Day-one inheritance items: [count]
  Critical path items:       [list]
  Transition complexity:     [simple/moderate/complex/transformation]

Items requiring human review: [count]
  [list of areas where information is incomplete or ambiguous]
```

**Quality criteria:**
- Every workforce number must cite its source document and clause.
- TUPE data must be extracted precisely — errors create legal exposure.
- Technology ownership must be correctly classified — incumbent-owned systems are a transition risk.
- Day-one inheritance items must be comprehensive — a missed item becomes a mobilisation crisis.
- Where information is unavailable from the ITT pack, the gap must be flagged explicitly, not filled with assumptions.

---

#### Skill 2: Target Operating Model Design (`operating-model`)

**Priority:** HIGHEST EFFORT skill — 45 person-days in methodology. This is the centrepiece of the solution workstream.
**Command:** `/pwin:target-model`
**Trigger:** Human-invoked. Run after current state assessment is complete and win themes are defined.
**Depends on:** Skill 1 (Current State), Agent 1 (requirements), Agent 3 (win themes and scoring strategy).
**Covers:** SOL-03.1.1-3, SOL-03.2.1-3, SOL-03.3.1-3

**What it does:**

Produces a structured target operating model framework for human solution architects to refine. Determines solution positioning, establishes design principles, defines scope and boundaries, designs the high-level operating model including governance and organisational concept, and maps the solution to requirements and win themes.

**Process:**

```
Step 1: Solution positioning (SOL-03.1.1)
  — Read evaluation framework via get_evaluation_framework()
  — Read win themes via get_win_themes()
  — Determine positioning: compliance (deliver what's asked) vs transformation
    (deliver what's asked plus measurable improvement)
  — Assess risk appetite: how much innovation does the evaluation framework reward?
  — Draft positioning statement for bid manager review

Step 2: Design principles (SOL-03.1.2)
  — Extract client's stated principles from specification
  — Map win themes to design principles (each theme implies a design choice)
  — Draft 5-8 design principles that guide all solution decisions
  — Ensure principles are testable (each major design decision can be validated
    against them)

Step 3: Scope and boundary definition (SOL-03.1.3)
  — Read requirements via get_response_sections()
  — Define: in-scope services, out-of-scope, client-retained, shared
  — Map interfaces between supplier scope and client-retained functions
  — Identify scope ambiguities — flag as clarification candidates or risk items

Step 4: High-level operating model design (SOL-03.2.1)
  — Structure service lines from scope definition
  — Design service delivery tiers (strategic/tactical/operational)
  — Map functional capabilities to service lines
  — Define capacity model principles (demand-driven/fixed/hybrid)
  — Produce operating model diagram structure (for human refinement)

Step 5: Governance model design (SOL-03.2.2)
  — Design governance layers: strategic (board), operational (service review),
    tactical (team), exception (escalation)
  — Define meeting cadence, attendees, decision rights
  — Map governance to client expectations (from evaluation criteria)
  — Design reporting framework aligned to SLA/KPI structure

Step 6: Organisational concept (SOL-03.2.3)
  — Design target organisational structure
  — Define role families, grade structure, reporting lines
  — Map to staffing model (feeds into Skill 7)
  — Design management span of control
  — Identify key leadership roles

Step 7: Requirements traceability (SOL-03.3.1)
  — Map every solution element to the requirement(s) it addresses
  — Read compliance requirements via get_compliance_requirements()
  — Identify requirements not yet addressed by any solution element (gaps)
  — Write risk flags via add_risk_flag() for uncovered requirements

Step 8: Win theme alignment (SOL-03.3.2)
  — Map each win theme to the solution elements that deliver it
  — For each high-value response section, confirm which win themes are
    demonstrable through the solution design
  — Identify win themes with weak solution evidence — flag for strengthening
  — Write insight via update_activity_insight()

Step 9: Validation preparation (SOL-03.3.3)
  — Produce validation checklist for bid team review
  — List open design decisions requiring human resolution
  — Create standup actions via create_standup_action() for each open decision
```

**Output template:**

```
Target Operating Model — Design Framework
==========================================
Solution positioning:         [compliance/transformation/hybrid]
Design principles:            [count] principles defined
Service lines:                [count]
Governance layers:            [count]
Requirements coverage:        [covered]/[total] ([percentage]%)

POSITIONING STATEMENT
  [1-2 paragraph positioning statement for bid team review]

DESIGN PRINCIPLES
  1. [Principle] — derived from [win theme/requirement/client signal]
  2. [Principle] — ...
  ...

SCOPE DEFINITION
  In-scope:                   [service lines with brief description]
  Out-of-scope:               [excluded items]
  Client-retained:            [retained functions]
  Shared:                     [shared responsibilities]
  Scope ambiguities:          [items requiring clarification] — [count]

HIGH-LEVEL OPERATING MODEL
  Service delivery tiers:     [strategic/tactical/operational]
  Service lines:              [list with brief description]
  Capacity model:             [demand-driven/fixed/hybrid]
  [Operating model diagram structure — for human refinement]

GOVERNANCE MODEL
  Governance layers:          [list with cadence and decision rights]
  Reporting framework:        [structure aligned to SLA/KPI]
  Escalation path:            [defined]

ORGANISATIONAL CONCEPT
  Structure type:             [functional/matrix/service-line]
  Role families:              [count]
  Key leadership roles:       [list]
  Management ratio:           [span of control]

REQUIREMENTS TRACEABILITY
  Requirements covered:       [count]/[total]
  Coverage gaps:              [count] — REQUIRES HUMAN RESOLUTION
  [gap list with requirement reference and recommended solution element]

WIN THEME ALIGNMENT
  [theme × solution element matrix]
  Themes with weak evidence:  [list] — REQUIRES STRENGTHENING

OPEN DESIGN DECISIONS ([count])
  [list of decisions requiring human resolution]

This document is a FRAMEWORK for human solution architects to refine.
Every design element requires human validation before inclusion in the response.
```

**Quality criteria:**
- Every solution element must trace to at least one requirement. Untraceable elements are scope creep.
- Win themes must be demonstrably embedded in the design, not bolted on.
- Design principles must be specific to this bid, not generic consulting boilerplate.
- Scope boundaries must be precise — ambiguity in scope creates commercial risk.
- Open design decisions must be explicitly listed — the AI must not resolve design choices that require domain expertise.

**Practitioner design note:**
> "The operating model is 45 person-days because it's the single most important deliverable. The AI can structure it, map requirements, identify gaps, and produce frameworks — but a human solution architect must design the actual model. If the AI saves 35% of those 45 days, that's still 15-16 person-days saved on structuring, mapping, and gap analysis alone."

---

#### Skill 3: Service Delivery Model (`service-delivery`)

**Command:** `/pwin:service-model`
**Trigger:** Human-invoked. Run after the target operating model is designed.
**Depends on:** Skill 2 (Target Operating Model) — needs service lines and operating model structure.
**Covers:** SOL-04.1.1-3, SOL-04.2.1-3

**What it does:**

Designs the service delivery model for each service line defined in the operating model. Maps delivery processes, resource/capacity models, interfaces, SLA/KPI commitments, and quality assurance mechanisms.

**Process:**

```
Step 1: Service line decomposition
  — Read operating model output from Skill 2
  — For each service line, identify:
    - Core processes (request-to-fulfilment, incident-to-resolution, etc.)
    - Inputs, outputs, dependencies
    - Resource requirements (volume, skills, availability)

Step 2: Process design per service line (SOL-04.1.1)
  — Map end-to-end processes for each service line
  — Define process steps, roles, handoffs, decision points
  — Identify automation opportunities
  — Design exception handling paths

Step 3: Resource and capacity model (SOL-04.1.2)
  — Model demand patterns (peak/trough, seasonal, growth trajectory)
  — Size resource requirement per process per service line
  — Define capacity management approach (fixed/flex/hybrid)
  — Map resource to staffing model (feeds Skill 7)

Step 4: Interface and dependency mapping (SOL-04.1.3)
  — Map interfaces between service lines
  — Map interfaces with client-retained functions
  — Map interfaces with supply chain partners (feeds Skills 12-13)
  — Identify single points of failure in interface chain

Step 5: SLA/KPI mapping (SOL-04.2.1)
  — Read contractual SLAs from requirements
  — Map each SLA to the delivery process that fulfils it
  — Identify SLAs that span multiple service lines (coordination risk)
  — Design operational targets (internal stretch beyond contractual minimum)

Step 6: Quality assurance design (SOL-04.2.2-3)
  — Design QA mechanisms per service line
  — Design continuous improvement framework
  — Define measurement and reporting approach
  — Map QA to governance model from Skill 2
```

**Output template:**

```
Service Delivery Model
======================
Service lines designed:      [count]
Total processes mapped:      [count]
SLAs mapped:                 [count]/[total contractual SLAs]

PER SERVICE LINE:
  [Service Line Name]
  ─────────────────
  Core processes:            [count]
  Resource requirement:      [FTE count] ([skills summary])
  Capacity model:            [fixed/flex/hybrid]
  SLAs owned:                [list with targets]
  Interfaces:                [internal: count] [external: count]
  Automation opportunities:  [list]

INTERFACE MAP
  [service line × service line matrix showing interface type]
  Single points of failure:  [list] — RISK FLAG

SLA COVERAGE
  Contractual SLAs covered:  [count]/[total]
  Multi-service-line SLAs:   [count] — coordination risk flagged
  Operational stretch targets: [list]

QA FRAMEWORK
  QA mechanisms per line:    [summary]
  CI framework:              [approach]
  Reporting cadence:         [schedule]

Items requiring human review: [count]
```

**Quality criteria:**
- Every contractual SLA must map to at least one delivery process. Unmapped SLAs are delivery risk.
- Resource sizing must be traceable to demand assumptions — not rounded numbers.
- Interfaces must be comprehensively mapped — unmapped interfaces fail at mobilisation.
- Automation opportunities must be realistic and costed (feeds into Agent 4).

---

#### Skill 4: Technology Architecture (`technology-architecture`)

**Command:** `/pwin:tech-architecture`
**Trigger:** Human-invoked. Run when the solution design requires a technology component.
**Depends on:** Skill 1 (Current State — technology landscape), Skill 2 (Target Operating Model — technology requirements).
**Covers:** SOL-05.1.1-3, SOL-05.2.1-3

**What it does:**

Designs the target technology architecture including platform selection rationale, security architecture, data architecture, and integration architecture. Produces a structured design framework for technology architects to refine.

**Process:**

```
Step 1: Technology requirements extraction
  — Read requirements via get_response_sections()
  — Extract all technology-related requirements (functional, non-functional, security)
  — Map to current state technology landscape from Skill 1
  — Identify technology gaps (current vs required)

Step 2: Target architecture design (SOL-05.1.1)
  — Design target technology stack aligned to operating model
  — Structure: presentation layer, application layer, data layer, integration layer,
    infrastructure layer
  — Map technology components to service lines from Skill 3

Step 3: Build/buy/reuse decision matrix (SOL-05.1.2)
  — For each technology component, assess:
    - Build: custom development, full control, higher cost/risk
    - Buy: COTS/SaaS, faster deployment, licence cost, vendor dependency
    - Reuse: existing capability from current estate or bidder portfolio
  — Score each option against: cost, time-to-deploy, risk, client preference,
    contractual constraints
  — Produce decision matrix for technology lead review

Step 4: Security architecture (SOL-05.1.3)
  — Extract security requirements from ITT (clearance tier, data classification,
    network requirements)
  — Design security layers: identity/access, network, data, application, physical
  — Map to government security frameworks (Cyber Essentials, ISO 27001, etc.)
  — Identify accreditation requirements and timeline

Step 5: Data architecture (SOL-05.2.1)
  — Map data flows between systems and service lines
  — Design data governance framework
  — Identify data migration requirements from current state
  — Assess data sovereignty and residency requirements

Step 6: Integration architecture (SOL-05.2.2-3)
  — Map system-to-system integrations
  — Design integration patterns (API, ESB, file transfer, real-time/batch)
  — Map integrations to client systems
  — Identify integration risks and dependencies
```

**Output template:**

```
Technology Architecture — Design Framework
==========================================
Technology components:        [count]
Build/buy/reuse decisions:    [build: count] [buy: count] [reuse: count]
Integrations mapped:          [count]
Security tier:                [tier]

TARGET ARCHITECTURE
  Presentation layer:         [components]
  Application layer:          [components]
  Data layer:                 [components]
  Integration layer:          [components]
  Infrastructure:             [components]

BUILD/BUY/REUSE MATRIX
  [component × option matrix with scoring]

SECURITY ARCHITECTURE
  Clearance requirement:      [tier]
  Accreditation needed:       [list with timeline]
  Data classification:        [level]
  Key security controls:      [list]

DATA ARCHITECTURE
  Data stores:                [count]
  Migration requirement:      [volume/complexity]
  Data sovereignty:           [constraints]

INTEGRATION MAP
  Internal integrations:      [count]
  Client system integrations: [count]
  Third-party integrations:   [count]
  Integration risks:          [list]

Items requiring technology lead review: [count]
```

**Quality criteria:**
- Every technology component must trace to a requirement or operating model need.
- Build/buy/reuse decisions must include rationale, not just a recommendation.
- Security architecture must align precisely to the stated clearance tier — over-engineering is cost; under-engineering is non-compliance.
- Integration risks must be flagged prominently — integration failure is the most common technology delivery risk.

---

#### Skill 5: Innovation & Social Value (`innovation-social-value`)

**Command:** `/pwin:innovation-plan`
**Trigger:** Human-invoked. Run when innovation and social value response sections are being developed.
**Depends on:** Skill 2 (Target Operating Model), Agent 3 (scoring strategy — to understand marks available for innovation/social value).
**Covers:** SOL-08.1.1-3, SOL-08.2.1, SOL-08.3.1-4, SOL-09.1.1-3, SOL-09.2.1-2

**What it does:**

Designs the innovation strategy, innovation roadmap, day-one innovations, continuous improvement governance, and productivity curve. Analyses social value requirements, designs commitments, defines monitoring framework, and embeds social value in the operating model.

**Process:**

```
Step 1: Innovation strategy design (SOL-08.1.1)
  — Read evaluation criteria for innovation-related sections
  — Assess client appetite for innovation (conservative/moderate/ambitious)
  — Define innovation positioning: safe (proven methods) vs bold (new approaches)
  — Align innovation strategy to win themes

Step 2: Innovation roadmap (SOL-08.1.2)
  — Design phased innovation programme: day-one, year-one, ongoing
  — For each innovation: benefit case, implementation effort, risk level
  — Map innovations to service lines and delivery processes
  — Identify quick wins vs strategic investments

Step 3: Day-one innovations (SOL-08.1.3)
  — Identify innovations deliverable from contract start
  — These must be credible, demonstrable, and low-risk
  — Map to evaluation criteria to demonstrate immediate value

Step 4: Continuous improvement governance (SOL-08.2.1)
  — Design CI framework: how innovations are proposed, assessed, approved, implemented
  — Define innovation governance within overall governance model
  — Map to reporting and review cadence

Step 5: Productivity curve modelling (SOL-08.3.1-4)
  — Model efficiency improvements over contract life
  — Map productivity gains to cost reductions (feeds Agent 4)
  — Define milestones and measurement criteria
  — Assess risk of non-delivery on productivity commitments

Step 6: Social value requirements analysis (SOL-09.1.1)
  — Read social value evaluation criteria
  — Map to Social Value Act 2012 themes (where applicable)
  — Identify mandatory vs scored social value commitments
  — Assess marks available for social value

Step 7: Social value commitments design (SOL-09.1.2-3)
  — Design specific, measurable social value commitments
  — Map commitments to evaluation criteria
  — Define delivery mechanisms within operating model
  — Draft monitoring and reporting framework

Step 8: Social value embedding (SOL-09.2.1-2)
  — Embed social value in operating model design
  — Map to supply chain requirements (feeds Skills 12-13)
  — Design community engagement approach where required
```

**Output template:**

```
Innovation Roadmap + Social Value Plan
======================================
Innovation items:             [count] ([day-one: count] [year-one: count] [ongoing: count])
Productivity target:          [x]% efficiency gain over [y] years
Social value commitments:     [count]

INNOVATION STRATEGY
  Client appetite:            [conservative/moderate/ambitious]
  Positioning:                [safe/bold/balanced]
  Alignment to win themes:    [mapped]

INNOVATION ROADMAP
  Day-one innovations:        [list with benefit case and risk level]
  Year-one innovations:       [list]
  Ongoing programme:          [framework description]

PRODUCTIVITY CURVE
  Year 1:                     [x]% improvement
  Year 2:                     [x]% cumulative
  Year [n]:                   [x]% cumulative
  Measurement approach:       [defined]
  Non-delivery risk:          [assessment]

CI GOVERNANCE
  Governance framework:       [summary]
  Innovation forum cadence:   [frequency]
  Approval process:           [defined]

SOCIAL VALUE PLAN
  Mandatory commitments:      [count]
  Scored commitments:         [count]
  Marks available:            [x]% of total marks

  COMMITMENTS
  [For each commitment:]
    - Commitment:             [specific, measurable statement]
    - Theme:                  [Social Value Act theme]
    - Delivery mechanism:     [how it's delivered through the operating model]
    - Measurement:            [KPI/metric]
    - Monitoring:             [reporting cadence and method]

Items requiring human review: [count]
```

**Quality criteria:**
- Day-one innovations must be genuinely deliverable from day one — aspirational innovations flagged as day-one destroy credibility.
- Productivity curve must be realistic and evidence-based — over-commitment creates commercial risk.
- Social value commitments must be specific and measurable — generic commitments score poorly.
- Innovation roadmap must align to the solution design — innovations disconnected from the operating model are not credible.

---

#### Skill 6: Solution Consolidation & Risk (`solution-consolidation`)

**Command:** `/pwin:solution-pack`
**Trigger:** Human-invoked. Run when individual solution workstreams are substantially complete and the design pack needs consolidation.
**Depends on:** Skills 1-5 (all solution design skills), plus Skills 7-8 (staffing and transition).
**Covers:** SOL-10 (evidence), SOL-11 (consolidation), SOL-12 (risk)

**What it does:**

Consolidates all solution outputs into a single design pack, maps evidence requirements to evaluation sections, assesses evidence availability, conducts completeness checks, and harvests/consolidates solution risks into the risk register.

**Process:**

```
Step 1: Evidence requirements mapping (SOL-10)
  — Read evaluation framework via get_evaluation_framework()
  — Read response sections via get_response_sections()
  — Map evidence requirements to evaluation sections:
    - Case studies (which sections require them, how many, what type)
    - Certifications (ISO, Cyber Essentials, etc.)
    - References (client references, letters of support)
    - CVs (named individuals, role profiles)
    - Financial evidence (accounts, insurance certificates)
  — Assess evidence availability: available, in progress, gap
  — Cross-reference evidence gaps with score gap analysis from Agent 3

Step 2: Solution consolidation (SOL-11)
  — Collect outputs from all solution skills (1-5, 7-8)
  — Check internal consistency:
    - Does the staffing model match the operating model?
    - Does the technology architecture support the service delivery model?
    - Does the transition plan address all day-one inheritance items?
    - Do innovation commitments align with the productivity curve?
    - Does the governance model cover all service lines?
  — Identify inconsistencies and conflicts
  — Produce consolidated solution design pack

Step 3: Completeness check
  — Map solution outputs to every response section
  — For each quality response section, confirm:
    - Solution content exists to answer the question
    - Evidence is identified and available
    - Win themes are embedded
    - Compliance requirements are addressed
  — Flag incomplete sections via create_standup_action()

Step 4: Solution risk consolidation (SOL-12)
  — Read existing risks via get_risks()
  — Harvest risks from all solution workstreams
  — Consolidate into solution risk register:
    - Design risks (solution choices that create exposure)
    - Delivery risks (can we build what we've designed?)
    - Commercial risks (cost implications of design choices)
    - Transition risks (mobilisation and change risks)
    - Supply chain risks (partner dependencies)
  — For each risk: likelihood, impact, mitigation, owner
  — Write via add_risk_flag()
```

**Output template:**

```
Solution Design Pack — Consolidation Report
============================================
Solution workstreams consolidated: [count]
Evidence items mapped:            [count] ([available: count] [gap: count])
Consistency checks:               [passed: count] [failed: count]
Solution risks:                   [count] ([high: count] [medium: count] [low: count])

EVIDENCE REQUIREMENTS
  Case studies required:     [count] — [available/gap status]
  Certifications required:   [count] — [available/gap status]
  References required:       [count] — [available/gap status]
  CVs required:              [count] — [available/gap status]
  Financial evidence:        [count] — [available/gap status]
  
  EVIDENCE GAPS ([count])
  [For each gap:]
    - Section:               [response section reference]
    - Evidence type:         [type]
    - Marks at risk:         [marks value]
    - Action required:       [specific action]

CONSISTENCY CHECK
  [For each check:]
    - Check:                 [description]
    - Status:                [PASS/FAIL]
    - Issue:                 [description if FAIL]
    - Resolution required:   [action]

COMPLETENESS
  Sections with full coverage:    [count]/[total]
  Sections with partial coverage: [count]
  Sections with no coverage:      [count] — URGENT
  [list of uncovered sections with marks value]

SOLUTION RISK REGISTER
  [count] risks consolidated from [workstreams]
  
  HIGH RISKS ([count])
  [For each:]
    - Risk:                  [description]
    - Source workstream:      [workstream]
    - Likelihood:            [H/M/L]
    - Impact:                [H/M/L]
    - Mitigation:            [action]
    - Owner:                 [role]
  
  MEDIUM/LOW RISKS: [count] — see full register

Items requiring human resolution: [count]
```

**Quality criteria:**
- Every response section must have a coverage assessment — no sections can be overlooked.
- Evidence gaps must be linked to marks at risk — this drives prioritisation.
- Consistency checks must be specific and actionable — "staffing model doesn't match operating model" is not enough; specify which roles or service lines are misaligned.
- Risk register must consolidate, not duplicate — risks from multiple workstreams about the same issue must be merged.

---

### 3.2 Productivity Skills — Staffing & Transition (2 skills)

---

#### Skill 7: Staffing Model Design (`staffing-model`)

**Command:** `/pwin:staffing-model`
**Trigger:** Human-invoked. Run after the target operating model and service delivery model are designed.
**Depends on:** Skill 2 (Target Operating Model — organisational concept), Skill 3 (Service Delivery Model — resource requirements).
**Covers:** SOL-06.1.1-2, SOL-06.2.1-3

**What it does:**

Designs the target workforce structure, defines role specifications, analyses the TUPE workforce, conducts gap analysis, and identifies recruitment/training requirements.

**Process:**

```
Step 1: Target workforce structure (SOL-06.1.1)
  — Read organisational concept from Skill 2
  — Read resource requirements from Skill 3
  — Design role families, grades, FTE count per role
  — Define reporting lines and management structure
  — Map roles to service lines and locations

Step 2: Role specification (SOL-06.1.2)
  — For each role, define:
    - Title, grade, service line, location
    - Responsibilities and accountabilities
    - Skills and qualifications required
    - Security clearance requirement
    - Named individual (if key person) or generic
  — Prioritise key personnel for CV preparation

Step 3: TUPE workforce analysis (SOL-06.2.1)
  — Read TUPE list data from current state assessment (Skill 1)
  — Map transferring staff to target roles
  — Identify: direct matches, roles requiring retraining, surplus roles
  — Assess TUPE cost implications (feeds Agent 4)

Step 4: Gap analysis (SOL-06.2.2)
  — Compare target structure with TUPE workforce
  — Identify gaps: roles with no TUPE match
  — Identify surplus: TUPE staff with no target role
  — Quantify recruitment requirement
  — Quantify training/upskilling requirement

Step 5: Staffing model validation (SOL-06.2.3)
  — Validate staffing model against:
    - Service delivery volumes (are there enough people?)
    - Budget constraints (feeds Agent 4 cost model)
    - Availability of skills in the market
    - Clearance processing timelines
  — Flag risks via add_risk_flag()
  — Create standup actions for unresolved staffing decisions
```

**Output template:**

```
Staffing Model
==============
Total FTEs:                   [count]
TUPE transferring:            [count]
New recruitment:              [count]
Role families:                [count]
Key personnel (named):        [count]

TARGET WORKFORCE STRUCTURE
  [For each service line:]
    - Service line:           [name]
    - Headcount:              [FTE]
    - Roles:                  [list with grades]
    - Management:             [ratio]

TUPE ANALYSIS
  Transferring staff:         [count]
  Direct match to target:     [count]
  Requires retraining:        [count]
  Surplus (no target role):   [count]
  Cost implications:          [summary — detail in Agent 4]

GAP ANALYSIS
  Roles to recruit:           [count] ([list])
  Skills to develop:          [list]
  Clearances to process:      [count] at [tier] — [estimated timeline]

RISKS
  [staffing-specific risks with likelihood/impact/mitigation]

Items requiring human review: [count]
  [list — e.g., key personnel selection, management appointments]
```

**Quality criteria:**
- FTE count must reconcile to the service delivery model resource requirements.
- TUPE analysis must handle staff data with precision — inaccuracies create legal and commercial risk.
- Gap analysis must be honest — understating the recruitment requirement is a delivery risk.
- Security clearance processing times must be factored into the mobilisation timeline.

---

#### Skill 8: Transition & Mobilisation Planning (`transition-planning`)

**Command:** `/pwin:transition-plan`
**Trigger:** Human-invoked. Run when the solution design is sufficiently mature to plan the transition.
**Depends on:** Skill 1 (Current State — inheritance items), Skill 7 (Staffing Model — people transition), Skill 4 (Technology Architecture — technology transition).
**Covers:** SOL-07.1.1-3, SOL-07.2.1-3

**What it does:**

Designs the transition approach and phasing, plans people transition (TUPE), plans technology/data transition, designs the mobilisation programme, and identifies transition risks.

**Process:**

```
Step 1: Transition approach and phasing (SOL-07.1.1)
  — Read day-one inheritance items from Skill 1
  — Design transition phases: mobilisation, transition, steady state
  — Define go-live criteria for each phase
  — Map critical path from contract award to service commencement
  — Design parallel running approach (if applicable)

Step 2: People transition planning (SOL-07.1.2)
  — Read TUPE analysis from Skill 7
  — Plan TUPE consultation process and timeline
  — Design staff communication programme
  — Plan induction and onboarding
  — Map security clearance processing to timeline

Step 3: Technology/data transition (SOL-07.1.3)
  — Read technology landscape from Skill 1 and Skill 4
  — Plan system migrations, data transfers, access provisioning
  — Design testing and cutover approach
  — Plan rollback strategy for failed transitions
  — Map technology dependencies to transition phases

Step 4: Mobilisation programme design (SOL-07.2.1)
  — Design work breakdown structure for mobilisation
  — Map workstreams: people, technology, process, governance, commercial
  — Define milestones and dependencies
  — Design mobilisation governance (who decides what during transition)
  — Produce Gantt-ready structure (for human refinement)

Step 5: Transition risk identification (SOL-07.2.2-3)
  — Identify transition-specific risks:
    - People: TUPE disputes, key person availability, clearance delays
    - Technology: migration failure, data loss, integration issues
    - Process: parallel running complexity, service degradation
    - Commercial: transition cost overrun, incumbent cooperation
  — For each risk: likelihood, impact, mitigation, owner
  — Write via add_risk_flag()
  — Map transition risks to mobilisation programme milestones
```

**Output template:**

```
Transition & Mobilisation Plan
==============================
Transition phases:            [count]
Duration to steady state:     [weeks/months]
Mobilisation workstreams:     [count]
Transition risks:             [count] ([high: count] [medium: count] [low: count])

TRANSITION APPROACH
  Phase 1 — Mobilisation:    [week x to week y] — [objectives]
  Phase 2 — Transition:      [week x to week y] — [objectives]
  Phase 3 — Steady State:    [from week x] — [objectives]
  Go-live criteria:           [list per phase]
  Parallel running:           [approach and duration]

PEOPLE TRANSITION
  TUPE consultation:          [timeline]
  Staff communication:        [programme summary]
  Induction/onboarding:       [programme summary]
  Clearance processing:       [count] staff, [estimated duration]

TECHNOLOGY TRANSITION
  System migrations:          [count] systems
  Data transfers:             [volume and approach]
  Testing approach:           [summary]
  Rollback strategy:          [defined]
  Critical dependencies:      [list]

MOBILISATION PROGRAMME
  Workstreams:                [list]
  Key milestones:             [list with dates/dependencies]
  Governance:                 [mobilisation governance structure]
  [Gantt-ready structure for human refinement]

TRANSITION RISKS ([count])
  [For each high risk:]
    - Risk:                   [description]
    - Category:               [people/technology/process/commercial]
    - Likelihood:             [H/M/L]
    - Impact:                 [H/M/L]
    - Mitigation:             [action]
    - Linked milestone:       [mobilisation milestone]

Items requiring human review: [count]
```

**Quality criteria:**
- Transition timeline must be realistic against the contractual timeline — over-optimistic transition plans are the most common delivery failure.
- TUPE consultation timeline must comply with statutory requirements (minimum 30 days for <100 staff, 45 days for 100+).
- Technology transition must include rollback plans — no migration should be irreversible without testing.
- Mobilisation programme must identify the critical path — the one chain of dependencies that determines go-live date.

---

### 3.3 Productivity Skills — Delivery (3 skills)

---

#### Skill 9: Delivery Readiness (`delivery-readiness`)

**Command:** `/pwin:delivery-readiness`
**Trigger:** Human-invoked. Run during the delivery workstream to consolidate delivery risks, assumptions, and mobilisation detail.
**Depends on:** Skills 1-8 (solution design outputs), Agent 4 (cost model for delivery budget).
**Covers:** DEL-01 (risk/assumptions), DEL-02 (mobilisation detail), DEL-04 (delivery resource plan)

**What it does:**

Identifies delivery-specific risks, documents delivery assumptions, develops the detailed mobilisation programme, and plans resource mobilisation and onboarding.

**Process:**

```
Step 1: Delivery risk identification (DEL-01)
  — Read existing risks via get_risks()
  — Identify delivery-specific risks not captured in solution risk register:
    - Resource availability risks
    - Client dependency risks (access, decisions, approvals)
    - Third-party dependency risks
    - Environment/infrastructure readiness risks
    - Knowledge transfer risks
  — Document delivery assumptions:
    - Client will provide [x] by [date]
    - Incumbent will cooperate during transition
    - Security clearances will be processed within [x] weeks
    - [etc.]
  — Write risks via add_risk_flag()

Step 2: Detailed mobilisation programme (DEL-02)
  — Elaborate the mobilisation programme from Skill 8
  — Add detailed task breakdowns per workstream
  — Define resource assignments for mobilisation activities
  — Identify mobilisation budget requirements (feeds Agent 4)
  — Design mobilisation reporting cadence

Step 3: Delivery resource plan (DEL-04)
  — Read staffing model from Skill 7
  — Plan phased resource onboarding aligned to transition plan
  — Design onboarding programme (induction, training, shadowing)
  — Map resource dependencies to mobilisation milestones
  — Identify resource risks (availability, clearance, notice periods)
```

**Output template:**

```
Delivery Readiness Assessment
=============================
Delivery risks:               [count]
Assumptions documented:        [count]
Mobilisation tasks:            [count]
Resource onboarding phases:    [count]

DELIVERY RISKS ([count])
  [For each:]
    - Risk:                   [description]
    - Category:               [resource/client/third-party/environment/knowledge]
    - Likelihood:             [H/M/L]
    - Impact:                 [H/M/L]
    - Mitigation:             [action]
    - Owner:                  [role]

DELIVERY ASSUMPTIONS ([count])
  [For each:]
    - Assumption:             [statement]
    - If invalid:             [consequence]
    - Validation approach:    [how we'll confirm]

MOBILISATION PROGRAMME (DETAILED)
  [workstream breakdown with tasks, owners, dependencies]

RESOURCE MOBILISATION
  Phase 1 onboarding:        [count] staff by [date]
  Phase 2 onboarding:        [count] staff by [date]
  Onboarding programme:      [summary]
  Resource risks:             [list]

Delivery readiness confidence: [HIGH/MEDIUM/LOW]
Items requiring resolution before submission: [count]
```

**Quality criteria:**
- Every assumption must have a "what if" consequence — assumptions without consequences aren't assumptions, they're hopes.
- Resource onboarding must align to transition milestones — people arriving before there's work or after go-live are both problems.
- Client dependency risks must be stated diplomatically but honestly — the response must demonstrate awareness without blaming the client.

---

#### Skill 10: Performance Framework Design (`performance-framework`)

**Command:** `/pwin:performance-framework`
**Trigger:** Human-invoked. Run when the delivery model needs a performance measurement, business continuity, and exit framework.
**Depends on:** Skill 3 (Service Delivery Model — SLAs/KPIs), Skill 2 (Target Operating Model — governance).
**Covers:** DEL-03.1.1-3, DEL-05.1.1, DEL-05.2.1

**What it does:**

Designs the KPI/SLA operational framework, performance reporting model, business continuity approach, and exit/handback plan.

**Process:**

```
Step 1: KPI/SLA framework design (DEL-03.1.1)
  — Read contractual SLAs from requirements
  — Design operational measurement framework:
    - How each SLA is measured (data source, calculation method, frequency)
    - Service credits/deductions regime
    - Reporting format and cadence
    - Dispute resolution process for contested measurements

Step 2: Performance reporting model (DEL-03.1.2-3)
  — Design reporting hierarchy:
    - Operational dashboards (daily/weekly)
    - Service review reports (monthly)
    - Strategic performance reports (quarterly)
  — Define report recipients and distribution
  — Design trend analysis and early warning indicators
  — Map to governance model from Skill 2

Step 3: Business continuity approach (DEL-05.1.1)
  — Design BCDR framework:
    - Business impact analysis per service line
    - Recovery time objectives (RTO) and recovery point objectives (RPO)
    - DR procedures per critical service
    - Testing cadence and approach
  — Map to contractual BCDR requirements

Step 4: Exit and handback plan (DEL-05.2.1)
  — Design exit framework:
    - Exit triggers and notice periods
    - Knowledge transfer programme
    - Data extraction and handover
    - Staff transition (reverse TUPE)
    - System decommissioning
    - Exit governance and milestones
  — Map to contractual exit obligations
```

**Output template:**

```
Performance & Continuity Framework
===================================
SLAs covered:                 [count]
Reports designed:             [count] across [levels] levels
BCDR services covered:        [count]
Exit plan milestones:         [count]

KPI/SLA FRAMEWORK
  [For each SLA:]
    - SLA:                    [reference and description]
    - Measurement:            [data source and calculation]
    - Target:                 [contractual target]
    - Stretch target:         [operational target]
    - Reporting frequency:    [daily/weekly/monthly]
    - Service credit:         [regime if applicable]

REPORTING MODEL
  Level 1 — Operational:     [content, frequency, audience]
  Level 2 — Service Review:  [content, frequency, audience]
  Level 3 — Strategic:       [content, frequency, audience]
  Early warning indicators:   [list]

BCDR FRAMEWORK
  Critical services:          [list with RTO/RPO]
  DR approach:                [summary]
  Testing cadence:            [schedule]

EXIT PLAN
  Exit timeline:              [phases and duration]
  Knowledge transfer:         [programme summary]
  Data handover:              [approach]
  Staff transition:           [approach]
  [milestone list]

Items requiring human review: [count]
```

**Quality criteria:**
- Every contractual SLA must have a defined measurement method — an SLA without a measurement method is a dispute waiting to happen.
- BCDR must address all critical services — gaps are compliance failures.
- Exit plan must be contractually compliant — missing exit obligations create lock-in risk for the client and commercial risk for the supplier.
- Reporting model must be practical — over-complex reporting consumes delivery resource.

---

#### Skill 11: Delivery Risk Consolidation (`delivery-risk`)

**Command:** `/pwin:delivery-risk`
**Trigger:** Human-invoked. Run as a final delivery workstream activity before governance review.
**Depends on:** Skills 6, 9, 10 (solution risks, delivery risks, performance framework).
**Covers:** DEL-06.1.1-3

**What it does:**

Consolidates all risk registers from the delivery perspective — solution risks, commercial risks, delivery risks, transition risks, supply chain risks — confirms mitigation status, and prepares the risk position for governance review.

**Process:**

```
Step 1: Risk consolidation (DEL-06.1.1)
  — Read all risks via get_risks()
  — Consolidate risks from all sources:
    - Solution design risks (from Skill 6)
    - Delivery risks (from Skill 9)
    - Commercial risks (from Agent 4)
    - Transition risks (from Skill 8)
    - Supply chain risks (from Skills 12-13)
  — De-duplicate: merge risks about the same issue from different workstreams
  — Classify by category and severity

Step 2: Mitigation status review (DEL-06.1.2)
  — For each risk, confirm:
    - Mitigation action defined? (yes/no)
    - Mitigation owner assigned? (yes/no)
    - Mitigation in progress/complete? (status)
    - Residual risk after mitigation? (H/M/L)
  — Flag risks with no mitigation or no owner

Step 3: Governance preparation (DEL-06.1.3)
  — Produce governance-ready risk summary:
    - Top 10 risks by severity
    - Risks requiring escalation (board-level decisions)
    - Risk appetite assessment (are we within tolerance?)
    - Recommended risk position for bid/no-bid decision
  — Write consolidated risk position via update_activity_insight()
```

**Output template:**

```
Consolidated Delivery Risk Register
====================================
Total risks:                  [count]
  High:                       [count]
  Medium:                     [count]
  Low:                        [count]
Sources consolidated:         [list of workstreams]
Risks de-duplicated:          [count merged]

TOP 10 RISKS
  [For each:]
    - Rank:                   [1-10]
    - Risk:                   [description]
    - Source:                  [workstream]
    - Likelihood:             [H/M/L]
    - Impact:                 [H/M/L]
    - Mitigation:             [action]
    - Mitigation status:      [defined/in progress/complete/NONE]
    - Residual risk:          [H/M/L]
    - Owner:                  [role]

ESCALATION ITEMS ([count])
  [risks requiring board-level decision]

MITIGATION GAPS
  Risks with no mitigation:  [count] — REQUIRES IMMEDIATE ACTION
  Risks with no owner:       [count]

RISK APPETITE ASSESSMENT
  Overall risk position:      [within tolerance/elevated/exceeds tolerance]
  Recommendation:             [proceed/proceed with conditions/escalate for review]

FULL REGISTER
  [complete risk table — all risks with full detail]
```

**Quality criteria:**
- De-duplication must be intelligent — risks worded differently but describing the same issue must be merged, not double-counted.
- Every high-severity risk must have a defined mitigation and an assigned owner.
- The governance summary must be honest about the overall risk position — downplaying risk is more dangerous than overstating it.
- Escalation items must be specific about what decision is needed from governance.

---

### 3.4 Productivity Skills — Supply Chain (2 skills)

---

#### Skill 12: Partner Sourcing & Due Diligence (`partner-sourcing`)

**Command:** `/pwin:partner-search`
**Trigger:** Human-invoked. Run when the solution design identifies capability gaps that require supply chain partners.
**Depends on:** Skill 2 (Target Operating Model — capability gaps), Skill 3 (Service Delivery Model — partner delivery requirements).
**Covers:** SUP-01.1.1-3, SUP-02.1.1-3, SUP-03.1.1-3

**What it does:**

Sources candidate partners against capability requirements, conducts due diligence assessment, selects a shortlist, briefs partners, manages solution input collection and review, and tracks teaming agreement status.

**Process:**

```
Step 1: Capability requirements definition (SUP-01.1.1)
  — Read operating model and service delivery model for capability gaps
  — Define partner requirements:
    - Capability needed (what they must deliver)
    - Capacity needed (scale)
    - Certifications/accreditations required
    - Security clearance requirements
    - Geographic/location requirements
    - Contract history requirements (e.g., similar contracts)

Step 2: Partner sourcing (SUP-01.1.2)
  — Search bid library for previous partner relationships
  — Structure partner assessment criteria:
    - Capability match
    - Capacity and scalability
    - Financial stability
    - Cultural fit
    - Competitive conflict check
  — Produce candidate longlist with scoring

Step 3: Due diligence (SUP-01.1.3)
  — For shortlisted partners, structure due diligence:
    - Financial health (accounts, credit check)
    - Legal compliance (litigation history, regulatory status)
    - Delivery track record (reference checks)
    - Insurance and liability coverage
    - Security clearance capability
  — Produce due diligence assessment per partner

Step 4: Partner briefing (SUP-02.1.1)
  — Produce partner briefing pack:
    - Opportunity overview (non-confidential)
    - Role and scope for the partner
    - Solution input requirements (what we need from them)
    - Timeline for inputs
    - Confidentiality requirements

Step 5: Solution input management (SUP-02.1.2-3)
  — Track solution inputs from each partner:
    - What was requested vs what was received
    - Quality assessment of inputs
    - Integration status (incorporated into solution design?)
  — Flag gaps and chase outstanding items via create_standup_action()

Step 6: Teaming agreement tracking (SUP-03.1.1-3)
  — Track teaming/NDA agreement status per partner:
    - NDA: signed/pending/not started
    - Teaming agreement: signed/pending/not started
    - Key terms agreed/outstanding
  — Flag agreements not signed as submission risk
```

**Output template:**

```
Partner Sourcing & Due Diligence
================================
Capability gaps identified:    [count]
Partners assessed:             [count]
Partners shortlisted:          [count]
Solution inputs received:      [count]/[total required]
Teaming agreements signed:     [count]/[total required]

CAPABILITY REQUIREMENTS
  [For each gap:]
    - Capability:              [description]
    - Service line:            [where it fits]
    - Criticality:             [essential/desirable]

PARTNER SHORTLIST
  [For each partner:]
    - Partner:                 [name]
    - Capability match:        [score/assessment]
    - Due diligence status:    [complete/in progress/not started]
    - Due diligence result:    [pass/conditional/fail]
    - NDA status:              [signed/pending]
    - Teaming agreement:       [signed/pending/not started]
    - Solution inputs:         [received/outstanding]

SOLUTION INPUT STATUS
  Inputs received:             [count]/[total]
  Inputs integrated:           [count]
  Outstanding:                 [list with chase dates]

SUBMISSION RISKS
  Unsigned agreements:         [count] — [list]
  Outstanding inputs:          [count] — [list]
  Due diligence concerns:      [list]

Items requiring human review: [count]
  [e.g., partner selection decisions, commercial negotiations]
```

**Quality criteria:**
- Capability requirements must trace to the operating model — partners must fill identified gaps, not create dependencies for their own sake.
- Due diligence must be structured and evidenced — not a rubber stamp.
- Teaming agreement status must be tracked against submission deadline — unsigned agreements on submission day are a showstopper.
- Solution inputs must be quality-assessed — poor partner inputs degrade the overall solution quality.

---

#### Skill 13: Partner Evidence & Commercial Coordination (`partner-coordination`)

**Command:** `/pwin:partner-coordination`
**Trigger:** Human-invoked. Run during the evidence collection and pricing phases.
**Depends on:** Skill 12 (Partner Sourcing — partner selection must be complete), Agent 4 (Commercial & Financial — pricing structure).
**Covers:** SUP-04.1.1-2, SUP-05.1.1-2, SUP-06.1.1-3

**What it does:**

Manages partner pricing submissions (coordinates with Agent 4), issues evidence requirements, collects/reviews/adapts partner evidence, and develops back-to-back subcontract terms.

**Process:**

```
Step 1: Partner pricing coordination (SUP-04.1.1-2)
  — Issue pricing templates to partners (format from Agent 4)
  — Track pricing submissions: submitted/outstanding/under review
  — Review partner pricing for:
    - Completeness against template
    - Internal consistency
    - Alignment with overall pricing strategy
  — Flag pricing issues to Agent 4 for commercial resolution

Step 2: Evidence requirements issuance (SUP-05.1.1)
  — Map evidence requirements to partners:
    - Case studies (what type, what format, what quality standard)
    - CVs for key personnel
    - Certifications and accreditations
    - References
    - Method statements for partner-delivered components
  — Issue evidence requirements with deadlines
  — Track responses

Step 3: Evidence collection and review (SUP-05.1.2)
  — Collect partner evidence submissions
  — Quality review:
    - Does the case study match the requirement?
    - Does the CV demonstrate the required experience?
    - Are certifications current and relevant?
    - Does the method statement align with the overall solution?
  — Adapt partner evidence to fit response format and style
  — Flag inadequate evidence for re-submission

Step 4: Subcontract terms development (SUP-06.1.1-3)
  — Draft back-to-back subcontract terms:
    - Map prime contract obligations to partner scope
    - Define performance requirements and SLAs
    - Structure payment terms (aligned to prime contract)
    - Define liability and indemnity provisions
    - Define exit and termination provisions
  — Produce terms summary for legal and commercial review
  — Track negotiation status per partner
```

**Output template:**

```
Partner Evidence & Commercial Coordination
===========================================
Partners coordinated:          [count]
Pricing submissions:           [received: count]/[total: count]
Evidence items collected:      [received: count]/[total: count]
Subcontract terms:             [drafted: count]/[total: count]

PRICING STATUS
  [For each partner:]
    - Partner:                 [name]
    - Pricing submitted:       [yes/no/partial]
    - Review status:           [complete/in review/issues flagged]
    - Issues:                  [list if any]

EVIDENCE STATUS
  [For each partner:]
    - Partner:                 [name]
    - Case studies:            [received/outstanding] — quality: [adequate/needs revision]
    - CVs:                     [received/outstanding] — quality: [adequate/needs revision]
    - Certifications:          [received/outstanding]
    - Method statements:       [received/outstanding] — quality: [adequate/needs revision]

SUBCONTRACT TERMS
  [For each partner:]
    - Partner:                 [name]
    - Terms drafted:           [yes/no]
    - Key terms agreed:        [list]
    - Outstanding terms:       [list]
    - Legal review:            [complete/pending]

SUBMISSION RISKS
  Outstanding pricing:         [list with deadline impact]
  Outstanding evidence:        [list with marks at risk]
  Unsigned subcontracts:       [list with risk assessment]

Items requiring human review: [count]
  [e.g., commercial negotiations, evidence quality judgements]
```

**Quality criteria:**
- Partner pricing must be received and reviewed with sufficient time for integration into the overall cost model — last-minute partner pricing is a commercial risk.
- Evidence must be adapted to fit the response style and format — raw partner evidence inserted verbatim degrades response quality.
- Subcontract terms must genuinely flow down prime contract obligations — misalignment creates delivery risk.
- All partner coordination must track against the submission deadline — the agent must flag items at risk of missing the deadline.

---

### 3.5 Insight Skills (1 skill)

---

#### Skill 14: Reviewer Calibration (`reviewer-calibration`) — UC8

**Command:** `/pwin:reviewer-calibration`
**Trigger:** On-demand. Bid manager invokes before or after a formal review cycle.
**Depends on:** Review scorecard data from at least two completed review cycles. Requires RVW (Reviews) module data.

**What it does:**

Reads reviewer scorecard history across review cycles. Identifies dimensional bias, optimism/pessimism tendencies, severity calibration drift, and predictive accuracy. Writes a calibration brief per review cycle that helps the bid manager contextualise reviewer feedback and identify systemic patterns.

**Full specification:** `ai_use_cases_reference.html`, UC8.

**Process:**

```
Step 1: Reviewer history analysis
  — Read all reviewer scorecards across completed review cycles
  — For each reviewer, calculate:
    - Average score vs panel average (optimism/pessimism index)
    - Score variance (consistency)
    - Dimensional bias (which quality dimensions do they score higher/lower?)
    - Trend over cycles (are they getting stricter or more lenient?)

Step 2: Calibration assessment
  — Compare each reviewer's scoring pattern to the panel:
    - Identify outliers (reviewers whose scores consistently diverge)
    - Identify dimensional specialists (reviewers who are stricter on
      specific quality dimensions — this is valuable, not a bias)
    - Identify severity drift (reviewers who change calibration across cycles)

Step 3: Predictive accuracy (where data permits)
  — If previous bid outcomes are available:
    - Correlate reviewer scores with client scores
    - Identify which reviewers' assessments best predict client evaluation
    - This is the most valuable insight — it tells the bid manager whose
      scores to weight most heavily

Step 4: Calibration brief generation
  — Write calibration brief for bid manager:
    - Per-reviewer calibration profile
    - Panel-level calibration assessment
    - Recommendations for review panel composition
    - Flags for reviews where calibration may affect quality judgements
  — Write as AIInsight via update_activity_insight()
  — Bid manager only — reviewer calibration data is not shared with reviewers
```

**Output:** AIInsight records written to app (see UC8 spec for schema). Plus calibration summary report for bid manager.

---

## 4. Agent Build Sequence

| Order | Skill | Type | Dependencies | Validates |
|---|---|---|---|---|
| 1 | Current State Assessment | Productivity | Agent 1 output + MCP read tools | Foundation for all solution design |
| 2 | Target Operating Model Design | Productivity | Skill 1 + Agent 3 win themes | Core solution framework — highest effort skill |
| 3 | Service Delivery Model | Productivity | Skill 2 output | Service-level decomposition and SLA mapping |
| 4 | Technology Architecture | Productivity | Skills 1, 2 output | Technology design framework |
| 5 | Staffing Model Design | Productivity | Skills 2, 3 output | Workforce structure and TUPE analysis |
| 6 | Transition & Mobilisation Planning | Productivity | Skills 1, 4, 7 output | Transition and mobilisation programme |
| 7 | Innovation & Social Value | Productivity | Skills 2, 3 + Agent 3 | Innovation roadmap and social value plan |
| 8 | Solution Consolidation & Risk | Productivity | Skills 1-5, 7-8 | Design pack consolidation and risk register |
| 9 | Delivery Readiness | Productivity | Skills 1-8 + Agent 4 | Delivery risk and mobilisation detail |
| 10 | Performance Framework Design | Productivity | Skills 2, 3 | KPI/SLA framework and BCDR |
| 11 | Delivery Risk Consolidation | Productivity | Skills 6, 9, 10 | Final risk position for governance |
| 12 | Partner Sourcing & Due Diligence | Productivity | Skills 2, 3 | Supply chain assessment |
| 13 | Partner Evidence & Commercial Coordination | Productivity | Skill 12 + Agent 4 | Partner evidence and commercial integration |
| 14 | Reviewer Calibration | Insight | Review scorecard data (RVW module) | Reviewer bias and calibration analysis |

---

## 5. Metrics

| Metric | Value |
|---|---|
| Total methodology tasks served | ~101 |
| High-rated tasks | 17 |
| Medium-rated tasks | 58 |
| Low-rated tasks | 26 |
| Average effort reduction | 35% |
| Implementation phase | Phase 5-6 |
| Methodology activities covered | SOL-02.1.1-3, SOL-02.2.1-3, SOL-03.1.1-3, SOL-03.2.1-3, SOL-03.3.1-3, SOL-04.1.1-3, SOL-04.2.1-3, SOL-05.1.1-3, SOL-05.2.1-3, SOL-06.1.1-2, SOL-06.2.1-3, SOL-07.1.1-3, SOL-07.2.1-3, SOL-08.1.1-3, SOL-08.2.1, SOL-08.3.1-4, SOL-09.1.1-3, SOL-09.2.1-2, SOL-10, SOL-11, SOL-12, DEL-01, DEL-02, DEL-03.1.1-3, DEL-04, DEL-05.1.1, DEL-05.2.1, DEL-06.1.1-3, SUP-01.1.1-3, SUP-02.1.1-3, SUP-03.1.1-3, SUP-04.1.1-2, SUP-05.1.1-2, SUP-06.1.1-3 |
| Insight skills | UC8 (Reviewer Calibration) |
| Estimated person-days saved per bid | ~35-40 (high task count compensates for lower reduction %) |
| Skill count | 14 (13 productivity, 1 insight) — LARGEST agent by skill count |

---

## 6. Relationship to Other Agents

**Agent 6 consumes from:**

| Upstream Agent | What Agent 6 consumes |
|---|---|
| Agent 1 (Document Intelligence) | Extracted requirements (the foundation for all solution design), TUPE data, security requirements, contract obligations |
| Agent 2 (Market Intelligence) | Client intelligence, incumbent operating model, market context for solution positioning |
| Agent 3 (Strategy & Scoring) | Scoring strategy (where to differentiate in the solution), win themes (what the solution must demonstrate), score gap analysis |

**Agent 6 feeds into:**

| Downstream Agent | What it consumes from Agent 6 |
|---|---|
| Agent 4 (Commercial & Financial) | Staffing model (feeds cost model), transition costs, technology costs, partner pricing, productivity curve (gainshare/efficiency savings) |
| Agent 5 (Content Drafting) | Solution design is the substance that responses describe — operating model, service delivery, technology, staffing, transition, innovation, social value |

**Agent 6 has the LONGEST dependency chain** — it consumes from Agents 1, 2, and 3, and feeds into Agents 4 and 5. This reflects the reality that solution design sits at the centre of the bid: it takes inputs from intelligence and strategy, and produces the substance that commercial modelling and response drafting depend on.

**Agent 6 never operates in isolation.** Every skill depends on upstream data from other agents, and every output feeds downstream work. The build sequence (Phase 5-6) reflects this — Agents 1-3 must be operational before Agent 6 can function.

---

## 7. Design Note

Lowest AI reduction (35%) but highest task count (101) and largest skill count (14). This reflects the reality that solution design requires deep domain expertise — an AI cannot design an operating model for a defence logistics contract without human specialists. But it CAN:

- **Structure requirements** into design frameworks
- **Produce templates** for operating models, staffing models, transition plans
- **Map requirements to solution elements** and identify gaps
- **Track evidence** and flag missing items
- **Consolidate outputs** from multiple workstreams
- **Harvest and consolidate risks** across all solution domains
- **Manage supply chain coordination** (structural and analytical work)

The AI does the structural work; humans do the creative design work. The 35% reduction comes almost entirely from structuring, mapping, tracking, and consolidating — not from design itself.

---

*Agent 6: Solution & Delivery Design | v1.0 | April 2026 | PWIN Architect*
*14 skills (13 productivity, 1 insight) | ~101 methodology tasks | 35% avg effort reduction*
