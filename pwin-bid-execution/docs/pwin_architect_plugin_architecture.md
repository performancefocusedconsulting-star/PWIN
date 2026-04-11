# PWIN Architect — Bid Execution Product
## AI Plugin Architecture Brief for Claude Code

**Version:** 1.5 | April 2026
**Status:** Authoritative design input for all Claude Code build sessions
**Scope:** Plugin architecture, MCP server design, data schema, AI write-back capability, ITT ingestion skills, 20 AI intelligence use cases, capability-based agent architecture, cross-product interfaces, SaaS trajectory
**Aligned with:** Architecture v6 (Session 13, 2026-04-02), [[pwin-bid-execution/docs/methodology_gold_standard|Gold Standard Template]] (Session 11, 2026-04-01), AI Use Cases Reference v1.0, [[pwin-bid-execution/docs/ai_suitability_assessment|AI Suitability Assessment]] (295 L3 tasks, practitioner-validated)

---

> **HOW TO USE THIS DOCUMENT**
> This is a design architecture brief, not a requirements list. It records decisions already made and rationale agreed. Claude Code should treat every principle here as a constraint, not a suggestion. If a build decision conflicts with anything in this document, flag it explicitly rather than working around it silently.

> **SCHEMA AUTHORITY:** The authoritative data model is `bid_execution_architecture_v6.html`. This document references that model — it does not duplicate it. If any field definition here conflicts with Architecture v6, the architecture document wins.

---

## 1. What PWIN Architect Is

PWIN Architect is a pursuit intelligence platform for firms competing for high-value UK public sector contracts (£50m–£1.5bn) across Defence, Justice, Emergency Services, and Central Government. It is delivered as a managed consulting service — fees are contingent on contract award (Paid on Award). Not SaaS. Not a bid writing shop.

The platform serves two purposes simultaneously:
- An operational delivery tool used on live bid engagements
- A lead generation and sales asset for BIP Management Consulting

The anchor prospect is Serco Group — 85 rebid contracts, £1.8bn ACV due by 2028.

---

## 2. Platform Product Map

The platform is composed of discrete products, each addressing a distinct phase of the pursuit lifecycle. Every product follows the same architectural pattern: self-contained HTML application + local data store + plugin intelligence layer via MCP.

| Product | Purpose | Status |
|---|---|---|
| PWIN Coach | Bid/no-bid qualification. 24-question framework, 6 categories, PWIN formula output, Alex Mercer AI persona | Built — HTML prototype |
| Portfolio Dashboard | Pipeline management. Priority matrix, PWIN benchmarking, trajectory tracking. 12 Serco seed pursuits | Built — HTML prototype |
| Bid Execution | Full bid lifecycle management. 84 activities, 10 workstreams, governance gates, submissions engine | Architecture complete — build in progress |
| PWIN Platform (MCP Server) | Multi-product MCP server + Data API. 94 tools, JSON file store, field-level permissions, skill runner. Serves Qualify, Win Strategy, Bid Execution | Built — 94 MCP tools, Data API, 3 skills, 11 platform knowledge files, 68 tests passing |
| Bid Library | Past proposals, case studies, evidence blocks. Shared data source across all products | Concept — to be built |
| Competitor Dossiers | Pre-compiled intelligence on frequent competitors. Quarterly refresh cadence | Concept — to be built |
| Client Profiles | Buyer intelligence, stakeholder maps, procurement history by buyer | Concept — to be built |
| BidEquity Verdict | Forensic post-loss bid review. 7-domain evaluation, independent scoring, traceability analysis, Pursuit Maturity Score. Two-pass model (platform + consultant). | PRD v2.0 — build plan defined, ~11 new skills on existing platform |
| Win Strategy | AI-driven capture-phase strategy development. 4-phase pipeline: baseline PWIN scoring → guided strategy elicitation → strategy synthesis → adversarial challenge & lock | Design complete — architecture diagram agreed (Session 11) |

### The Shared Intelligence Layer

A critical architectural principle: the Bid Execution product is **one data source among several**. The plugin reasons across all of them simultaneously:

- **Bid Execution product** — live pursuit data, activity status, response item production progress, compliance coverage, review scores, governance gate status
- **Win Strategy product** — capture-phase intelligence: win themes, competitive positioning, pricing strategy framework, locked strategy and assumptions (see Section 4.6 for cross-product interface)
- **Bid Library** — past proposals, case studies, win/loss records, evidence blocks
- **Competitor Dossiers** — pre-compiled intelligence on Serco, Capita, Mitie, G4S, etc.
- **Client Profiles** — buyer intelligence, stakeholder maps, procurement history
- **External sources** — Find a Tender, Contracts Finder, LinkedIn, Companies House (via web search)

> **DESIGN PRINCIPLE:** Every product is both a data consumer and a data contributor. Bid Execution provides live pursuit data. The Bid Library receives completed bid assets. The plugin synthesises across all sources. This multi-source reasoning is what differentiates PWIN Architect from a bid management tool.

> **DEPENDENCY NOTE:** Plugin capabilities are gated by data source availability. Timeline analysis and production tracking work with Bid Execution data alone. Competitive briefings require Competitor Dossiers. Evidence-based drafting requires the Bid Library. Do not promise multi-source intelligence until the data sources exist.

---

## 3. The Bid Execution Product

### 3.1 What It Is

The Bid Execution product manages the full operational bid process from ITT receipt through to submission and post-submission. It is the most sophisticated product in the platform.

Confirmed architecture (from Claude Code build sessions, Architecture v6 — Session 8):
- **84 activities** across **10 workstreams**
- **Services archetype** as the default template (new business and rebid)
- **Governance gates** covering development assurance (solution, commercial, risk reviews) and executive governance (price, risk, margin approval)
- **Submissions engine** with ResponseSection/ResponseItem split — exam paper separated from answer sheet, 10-stage production lifecycle, per-response quality dimensions
- **ITT ingestion data layer** — ResponseSection, EvaluationFramework, ITTDocument entities as write targets for future AI skills
- **Reviews module** for formal peer/SME review of written responses at pink, red, and gold stages with dual scoring
- **Win theme tracking** with integration heatmap across all response items
- **Optional client scoring scheme** with grade bands and hurdle marks
- **Dual-track readiness** — development complete AND production complete
- **Backward-planned timeline** from submission deadline
- **Bid extended** with procurement context (route, portal, contract duration, TUPE, security clearance)

### 3.2 The 10 Workstreams

| Code | Workstream | Phase | Activities | L2s | L3 Tasks |
|---|---|---|---|---|---|
| SAL | Sales & Customer Intelligence | Development | 10 | 22 | 56 |
| SOL | Solution Design | Development | 12 | 26 | 72 |
| COM | Commercial & Pricing | Development | 7 | 15 | 39 |
| LEG | Legal & Contractual | Development | 6 | — | 19 |
| DEL | Programme & Delivery | Development | 6 | — | 17 |
| SUP | Supply Chain & Partners | Development | 6 | — | 16 |
| BM | Bid Management & Programme Control | Continuous | 16 | — | 29 |
| GOV | Internal Governance | Continuous | 6 | — | 12 |
| PRD | Proposal Production | Production | 9 | — | 18 |
| POST | Post-Submission | Post-Submission | 8 | — | 12 |
| **Total** | | | **84** | **~123** | **~295** |

### 3.3 The Data Model — 24 Entities (Architecture v6 — Session 8)

> **AUTHORITATIVE SOURCE:** The field-level schema is defined in `bid_execution_architecture_v6.html`. The summary below is for plugin design reference. If any field here conflicts with Architecture v6, the architecture document wins.

**Core Entities:**

| Entity | Purpose | Key Fields |
|---|---|---|
| **Bid** | Top-level container, extended with procurement context | archetype, tcv, acv, submissionDeadline, ittIssueDate, status, procurementRoute, portalPlatform, portalReference, contractDurationMonths, extensionOptions, tupeApplicable, securityClearanceTier, isRebid, linkedEvaluationFrameworkId |
| **BidCalendar** | Scheduling constraints | workingDays, publicHolidays, weekendWorking, teamUnavailability, clientBlackouts |
| **Workstream** | Major track of activity | code, phase (development/production/post_submission/continuous), progressPct (computed), timingHealth (computed) |
| **Activity** | Atomic unit of work — THE SPINE | code (human label e.g. SOL-04), status, outputAssurance (unassured/under_review/assured/accepted_at_gate), effortDays, teamSize, parallelisationType (P/S/C), dependencies[], dependencyThreshold, lastUpdated |

**ITT Ingestion Entities (new in Session 8):**

| Entity | Purpose | Key Fields |
|---|---|---|
| **ResponseSection** | The exam paper — what the client is asking. Populated at ITT commencement before any response work begins | reference, title, questionText, responseType, evaluationCategory, evaluationWeightPct, evaluationMaxScore, evaluationCriteria, hurdleScore, wordLimit, pageLimit, linkedResponseItemId, sourceDocumentId, createdBy (manual/csv_import/ai_ingestion) |
| **EvaluationFramework** | Tender-level evaluation structure — one per bid | methodology (meat/lowest_price/quality_only/fixed_price_quality_only), qualityWeightPct, priceWeightPct, socialValueWeightPct, priceEvaluationMethod, scoringScale, scoringDescriptors[], passFail[], presentationRequired, bafoExpected |
| **ITTDocument** | Registry of all documents received in the ITT pack | filename, title, volumeType (instructions/specification/contract/pricing/response_template/etc.), fileType, version, receivedDate, source, parsedStatus, extractedEntityCounts |

**Submissions Entities (10-stage production lifecycle):**

| Entity | Purpose | Key Fields |
|---|---|---|
| **ResponseItem** | Production tracking for a single response — linked 1:1 to ResponseSection. Question-definition fields now live on ResponseSection | linkedResponseSectionId, reference, status (10-stage), currentWordCount, complexityEstimate, effortDays, owner, quality dimensions (6 structured fields — AI-ready). UI resolves questionText, wordLimit, evaluationWeightPct from linked ResponseSection |
| **ComplianceRequirement** | Prescriptive tender requirement — compliance declaration + solution alignment | classification (mandatory/scored/pass_fail/evidential/contractual), complianceStatus, solutionAlignment, coverageStatus (derived from linked ResponseItems) |
| **WinTheme** | Differentiating value proposition — from capture, refined at ITT | statement, rationale, sourceActivity (SAL-04/05/06), status (draft/confirmed/revised), linkedResponseItemIds |
| **ClientScoringScheme** | Optional client marking scheme — grade bands with descriptors | maxScore, gradeBands[], isActive (false if no scheme) |
| **GradeBand** | Single level in scoring scheme | minScore, maxScore, label, descriptor (what supplier must demonstrate) |

**ResponseItem Quality Dimensions** (structured data, manual in base product, AI-ready for future):

| Field | Type | Purpose |
|---|---|---|
| qualityAnswersQuestion | yes/no/partial/not_assessed | Does it answer the question asked? |
| qualityFollowsStructure | yes/no/partial/not_assessed | Does it follow the question structure? |
| qualityScoreSelfAssessment | number (optional) | Score against client scheme (if exists) |
| qualityScoreRationale | string | Why this score, referencing grade band descriptors |
| qualityScoreGap | string | Gap to next band or hurdle mark |
| qualityCredentials | yes/no/partial/not_assessed | Past success and delivery credentials cited? |
| qualityCredentialsRefs | string | Which credentials referenced |
| qualityWinThemeAssessments | Object[] | Per-theme: {winThemeId, integrated: yes/no/partial, notes} |
| qualityComplianceMapping | string | How compliance requirements map to response text |

**Review Entities (formal peer/SME review — pink, red, gold):**

| Entity | Purpose | Key Fields |
|---|---|---|
| **ReviewCycle** | Review event for written responses | type (pink/red/gold/adhoc), targetResponseItemIds (NOT activities), status, reviewers[], overallScore |
| **ReviewAction** | Feedback item against a response | responseItemId, severity (critical/major/minor), criterion (8 quality dimensions), status, resolutionNotes, deadline |
| **ReviewScorecard** | Dual scoring per response per reviewer | scores (internal 1-5 on 8 criteria), averageScore, predictedClientScore (optional), predictedClientGradeBand, meetsHurdle |

**Governance Entities:**

| Entity | Purpose | Key Fields |
|---|---|---|
| **GovernanceGate** | Development assurance + executive governance | gateType (solution_review/commercial_review/risk_review/executive_tier1-3/methodology/submission_authority/bafo_authority), entryCriteria[], decision, conditions, riskPremiumPct, prepTemplate[] |
| **StandupAction** | Tactical daily action — high volume, short lived | parentActivityCode, parentGateId, source (manual/gate_preparation/smart_nudge/standup), status |

**Supporting Entities:**

| Entity | Purpose | Key Fields |
|---|---|---|
| **RiskAssumption** | Dual register: delivery (feeds pricing) + bid (feeds portfolio) | registerType, type (risk/assumption), probability, impact, status |
| **TeamMember** | Bid team member with rate and availability | coreRole, workstreams[], individualDayRate, isContractor, securityClearance |
| **Stakeholder** | Governance participants — sponsors, approvers, reviewers | stakeholderType (sponsor/approver/reviewer/influencer/SME), linkedGateIds[] |
| **RateCard** | Standard company day rates per role | roleName, standardDayRate |
| **Engagement** | Practice-level commercial wrapper | winFeeValue, costToBid, feeModel, healthStatus |
| **Artefact** | Submission document — auto-seeded from ResponseItems | type, status, linkedResponseItemIds, submissionFileName |

---

## 4. The Plugin Architecture

### 4.1 What the Plugin Does — Two Skill Types

The plugin contains skills across six agents. Every skill follows the same implementation pattern (prompt + MCP tools + Claude API call), but skills fall into two categories based on what they read and what they produce:

**Productivity Skills** — Human-invoked. Read uploaded documents and/or internal bid data. Produce deliverables (reports, drafts, models, structured data records).

Examples:
- ITT extraction — reads uploaded ITT pack, writes ResponseSection and EvaluationFramework records (Agent 1)
- Response drafting — reads win themes + scoring strategy + solution design, produces draft response sections (Agent 5)
- Client intelligence briefing — reads uploaded client documents + web sources, produces structured intelligence report (Agent 2)
- Cost modelling — reads solution design + rate cards, produces cost model and pricing scenarios (Agent 4)
- Gate review pack assembly — reads gate criteria + activity status, produces governance document (Agent 5)

**Insight Skills** — On-demand (V1) or scheduled/event-triggered (V2). Read internal bid data only — no uploaded documents needed. Write AIInsight records back into the application. Zero additional data entry burden.

Examples:
- Timeline analysis (UC1) — reads activity dates + dependencies, writes ActivityAIInsight with gap analysis (Agent 3)
- Compliance coverage (UC4) — reads response sections + evaluation framework, writes ComplianceCoverageAIInsight (Agent 3)
- Gate readiness (UC9) — reads gate criteria + activity status, writes GateReadinessAIInsight (Agent 3)
- Bid cost forecasting (UC11) — reads engagement + team + rate card data, writes budget forecast (Agent 4)

> **KEY DESIGN PRINCIPLE:** Both skill types use the same MCP server, the same Claude API, and the same agent configurations. The distinction is product design (who triggers it, what it reads, what it produces), not engineering. See Section 7 for the full rationale.

> **MCP TOOL SCHEMA IMPLICATION:** The MCP server must support both read-then-write-insight patterns (insight skills reading internal data) and read-external-then-write-record patterns (productivity skills creating structured data from uploaded documents). Both directions must be handled in the tool schema — see Sections 5.2 and 5.3.

> **V1/V2 SCOPE BOUNDARY:** V1 builds data targets for ResponseSection, EvaluationFramework, and ITTDocument. V2 adds Requirement and ClarificationItem entities. Skills that write to V2 entities are not built until those entities exist. See Section 9.5 for the full scope boundary.

### 4.2 One Plugin — Not Multiple

**Decision: one plugin with capability-based agents.**

Rationale:
- A bid manager mid-pursuit does not think in workstream silos — they need win themes, timeline analysis, and competitive intelligence in the same session
- Shared context (pursuit record, rules, bid library) would be duplicated and drift across multiple plugins
- Sub-agents inside a single plugin provide specialisation without fragmentation
- Client distribution on Team/Enterprise is one plugin install, not seven

### 4.2a Agent Architecture — Capability-Based, Not Persona-Based (Session 14, 2026-04-02)

**Decision: agents are organised by AI capability domain, not by human role.**

**Why this changed:** The v1.4 architecture defined five persona-routed agents (bid-manager, pursuit-director, proposal-author, commercial, stakeholder) — designed top-down from who uses the output. Bottom-up analysis of all 296 L3 tasks from the practitioner-validated AI suitability assessment revealed that the natural clustering is by what the AI does, not who it does it for. A single agent capability (e.g., document extraction) serves multiple human roles (bid manager, solution architect, capture lead). Persona routing added unnecessary complexity — the same Claude model, the same API, just different prompts and tool access.

**What an "agent" actually is:** An agent is a saved configuration — system prompt, tool access list, knowledge scope, and output format — applied to the same underlying Claude model. There is no separate software, no separate deployment, no separate infrastructure per agent. The specialisation is in the configuration, not the infrastructure.

**The six capability-based agents:**

#### Agent 1: Document Intelligence Agent
**Capability:** Ingests uploaded documents (ITT packs, contracts, policies), extracts structured data, builds compliance matrices, maps requirements.
**Tasks served:** ~22 (Extraction + Mapping clusters) | 17 High-rated | Avg reduction 63%
**Implementation:** Phase 1 — foundation agent, all others depend on its outputs
**Key skills:**
- ITT requirements extraction (SOL-01.1.1-3)
- Evaluation criteria extraction (SAL-05.1.1-3)
- Contract clause analysis (LEG-01.1.1-2)
- Compliance matrix generation (PRD-01)
- Procurement documentation ingestion (SAL-01.1.1)
**Inputs:** Uploaded PDFs/Word documents. No external APIs needed.
**Outputs:** Structured data into bid execution app + populated proforma documents.
**Tools:** PDF/Word reader, structured data writer (MCP create tools), template populator.
**Human review gate:** Light — verify extracted data completeness and accuracy.

#### Agent 2: Market & Competitive Intelligence Agent
**Capability:** Researches clients, sectors, competitors, incumbent performance. Builds intelligence briefings from uploaded documents and external sources.
**Tasks served:** ~31 (Capture Lead domain) | 18 High-rated | Avg reduction 72%
**Implementation:** Phase 3
**Key skills:**
- Client intelligence profiling (SAL-01.1.2-4, SAL-01.2.1-3)
- Incumbent performance analysis (SAL-02.1.1, 02.1.3, 02.2.1-2, 02.3.1-5)
- Competitor profiling & battle cards (SAL-03.1.2-3, 03.2.1)
- Supply chain & stakeholder mapping (SAL-01.1.4, SAL-10.1.1-2)
**Inputs:** Uploaded client documents + web search + Contracts Finder API + Companies House API.
**Outputs:** Client intelligence briefing, incumbent assessment, competitor profiles — all into proforma templates.
**Tools:** Web search, Contracts Finder API, Companies House API, document reader, template populator.
**Human review gate:** Strategic validation — verify judgements against relationship intelligence.
**Design note (from practitioner review):** This agent has a life outside individual bids. Client intelligence and competitor profiling should run on a scheduled, recurring basis (monthly or quarterly) as a BidEquity operational cost, not a per-bid activity. The platform needs a client intelligence layer that persists across bids.

#### Agent 3: Strategy & Scoring Analyst Agent
**Capability:** Analyses evaluation frameworks, marks concentration, win theme coverage, scoring strategy. The "how do we win" reasoning engine.
**Tasks served:** ~20 (Bid Manager analytical tasks) | 12 High-rated | Avg reduction 58%
**Implementation:** Phase 1 (alongside Agent 1 — depends on its evaluation framework output)
**Key skills:**
- Marks concentration analysis (SAL-05.2.1)
- Win theme-to-criteria mapping (SAL-04.1.2, SAL-05.2.4)
- Scoring strategy per section (SAL-05.2.3)
- PWIN scoring across all dimensions (SAL-06.2.3)
- Capture effectiveness assessment (SAL-06.1.1)
**Inputs:** Evaluation framework (from Agent 1) + win themes + response structure + competitive intelligence.
**Outputs:** Scoring strategy, marks allocation, win theme coverage matrix, PWIN score.
**Tools:** MCP read tools (evaluation framework, response sections, win themes), analytical calculator.
**Human review gate:** Strategic validation — scoring strategy is a human decision informed by AI analysis.

#### Agent 4: Commercial & Financial Modelling Agent
**Capability:** Cost modelling, pricing analysis, scenario planning, risk-premium calculation, bid cost forecasting.
**Tasks served:** ~31 (Commercial Lead domain) | 10 High-rated | Avg reduction 43%
**Implementation:** Phase 4-5
**Key skills:**
- Workforce cost modelling (COM-01.1.1)
- Non-workforce cost modelling (COM-01.1.2)
- Pricing strategy & scenario analysis (COM-02, COM-03)
- Risk premium validation (COM-05)
- Transformation cost-benefit modelling (SAL-02.3.4)
**Inputs:** Solution design outputs + rate cards + corporate cost data + upstream commercial models.
**Outputs:** Cost models (Excel), pricing scenarios, risk-adjusted commercial positions, tornado analysis.
**Tools:** Spreadsheet/calculation tools, MCP read tools (engagement, rate card, team), template populator.
**Human review gate:** Commercial sign-off — AI builds the framework for the commercial person to validate, test, and complete.
**Design note (from practitioner review):** Lower AI reduction (43%) reflects genuine need for commercial judgement. The AI builds the analytical framework and runs scenarios; the commercial lead validates assumptions and makes pricing decisions.

#### Agent 5: Content & Response Drafting Agent
**Capability:** Drafts response sections, executive summaries, governance packs, evidence compilation. The production workhorse.
**Tasks served:** ~56 (Content Generation cluster) | 4 High-rated (but highest volume) | Avg reduction 40%
**Implementation:** Phase 2
**Key skills:**
- Response section drafting (PRD-02.1.1)
- Executive summary drafting (PRD-02.1.2)
- Storyboard generation (PRD-04)
- Evidence compilation & formatting (PRD-03.1.1-2)
- Governance pack assembly (GOV-01 through GOV-06)
**Inputs:** Win themes + scoring strategy + solution design + evaluation criteria + evidence library.
**Outputs:** Draft response sections, evidence packs, governance documents — for human refinement.
**Tools:** MCP read tools (all entities), document generator, evidence library search, template populator.
**Human review gate:** Content refinement — writers and SMEs refine AI drafts, not write from scratch.

#### Agent 6: Solution & Delivery Design Agent
**Capability:** Supports solution architecture, operating model design, transition planning, staffing models, technology architecture.
**Tasks served:** ~86 (Solution Architect + Delivery Director + Technical Lead + HR Lead) | 20 High-rated | Avg reduction 35%
**Implementation:** Phase 3-5
**Key skills:**
- Operating model design support (SOL-03, SOL-04)
- Staffing model design (SOL-06.1.1)
- Technology architecture support (SOL-05)
- Transition planning (SOL-07)
- Service design (SOL-08)
- Work breakdown structure & consortium scope allocation (SAL-06.3.3)
**Inputs:** Requirements (from Agent 1) + client intelligence (from Agent 2) + corporate capability data.
**Outputs:** Design frameworks, staffing models, transition plans, operating model visualisations.
**Tools:** MCP read tools (requirements, solution entities), document generator, template populator.
**Human review gate:** Heavy — solution design is where human expertise is most critical. AI accelerates, humans decide.
**Design note (from practitioner review):** Lowest AI reduction (35%) but highest task count. AI potential is higher than the average suggests — practitioner notes on SAL-06.3.3 describe AI building visual operating models and work breakdown structures with scope allocation across consortium partners.

**Agent dependency chain:**

```
┌──────────────────────┐
│ Agent 1: Document     │ ──── Extracts from uploaded ITT docs
│ Intelligence          │      Foundation for everything else
└──────────┬───────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌──────────┐ ┌──────────┐
│ Agent 2   │ │ Agent 3   │
│ Market    │ │ Strategy  │ ──── Both depend on extracted requirements
│ Intel     │ │ & Scoring │      and evaluation framework
└─────┬────┘ └─────┬────┘
      │            │
      └──────┬─────┘
             ▼
      ┌──────────────┐
      │ Agent 4       │
      │ Commercial &  │ ──── Needs solution + strategy + intel
      │ Financial     │
      └──────┬───────┘
             │
      ┌──────┴───────┐
      ▼              ▼
┌──────────┐  ┌───────────┐
│ Agent 5   │  │ Agent 6    │
│ Content   │  │ Solution   │ ──── Production and design
│ Drafting  │  │ & Delivery │      draw on all upstream
└───────────┘  └────────────┘
```

**What differs between agents (same Claude model for all):**

| Dimension | Varies by agent |
|---|---|
| **System prompt** | Persona, operating rules, quality standards, domain vocabulary |
| **Tools available** | Web search (Agent 2 only), spreadsheet tools (Agent 4), document generation (Agent 5) |
| **Knowledge scope** | Which bid data entities to read, which upstream outputs to consume |
| **Output format** | Structured data (Agent 1), narrative report (Agent 2), draft document (Agent 5), financial model (Agent 4) |
| **Human review gate** | Light verification (Agent 1), strategic validation (Agent 3), content refinement (Agent 5), commercial sign-off (Agent 4) |

**Supersedes:** The v1.4 persona-based agents (bid-manager-agent, pursuit-director-agent, proposal-author-agent, commercial-agent, stakeholder-agent) are retired. The capabilities they provided are distributed across the six capability-based agents. Persona-specific routing (e.g., pursuit director wants a pipeline summary) is handled by skill selection and output formatting, not by separate agent configurations.

**Relationship to the three plugin roles:**
- **Role 1 (In-Application Intelligence):** Primarily Agent 3 (scoring analysis) + the 20 intelligence use cases (Section 7a). Agents read bid data via MCP, write AIInsight records back.
- **Role 2 (Output Generation):** Primarily Agent 5 (content drafting) + Agent 2 (intelligence briefings) + Agent 4 (financial models). Agents produce deliverables for human consumption.
- **Role 3 (Data Extraction & Ingestion):** Primarily Agent 1 (document intelligence). Agent reads external documents, writes structured records into the application via MCP.

### 4.3 Plugin Folder Structure

```
pwin-architect-plugin/
│
├── .claude-plugin/
│   └── plugin.json                    — single manifest
│
├── .mcp.json                          — all connectors declared here
│
├── agents/                            — capability-based agent configurations
│   ├── document-intelligence/
│   │   └── AGENT.md                  — ITT extraction, compliance mapping, contract analysis
│   ├── market-intelligence/
│   │   └── AGENT.md                  — client profiling, competitor analysis, incumbent review
│   ├── strategy-scoring/
│   │   └── AGENT.md                  — evaluation analysis, marks allocation, win strategy
│   ├── commercial-financial/
│   │   └── AGENT.md                  — cost modelling, pricing, scenario analysis
│   ├── content-drafting/
│   │   └── AGENT.md                  — response drafting, evidence compilation, governance packs
│   └── solution-delivery/
│       └── AGENT.md                  — operating model, staffing, transition, technology
│
├── skills/                            — reusable prompt + tool + template configurations per agent
│   ├── document-intelligence/         — Agent 1 skills
│   │   ├── itt-extraction/            — PRIMARY SKILL — build first
│   │   │   └── SKILL.md
│   │   ├── evaluation-criteria/
│   │   │   └── SKILL.md
│   │   ├── contract-analysis/
│   │   │   └── SKILL.md
│   │   ├── compliance-matrix/
│   │   │   └── SKILL.md
│   │   ├── procurement-ingestion/
│   │   │   └── SKILL.md
│   │   ├── clarification-impact/      — UC13 insight skill
│   │   │   └── SKILL.md
│   │   └── amendment-detection/       — UC14 insight skill
│   │       └── SKILL.md
│   ├── market-intelligence/           — Agent 2 skills
│   │   ├── client-profiling/
│   │   │   └── SKILL.md
│   │   ├── incumbent-assessment/
│   │   │   └── SKILL.md
│   │   ├── competitor-profiling/
│   │   │   └── SKILL.md
│   │   └── sector-scanning/
│   │       └── SKILL.md
│   ├── strategy-scoring/              — Agent 3 skills (largest — includes most insight skills)
│   │   ├── marks-concentration/
│   │   │   └── SKILL.md
│   │   ├── win-theme-mapping/
│   │   │   └── SKILL.md
│   │   ├── scoring-strategy/
│   │   │   └── SKILL.md
│   │   ├── pwin-scoring/
│   │   │   └── SKILL.md
│   │   ├── timeline-analysis/         — UC1 insight skill — BUILD FIRST
│   │   │   └── SKILL.md
│   │   ├── compliance-coverage/       — UC4 insight skill
│   │   │   └── SKILL.md
│   │   ├── standup-prioritisation/    — UC3 insight skill
│   │   │   └── SKILL.md
│   │   ├── gate-readiness/            — UC9 insight skill
│   │   │   └── SKILL.md
│   │   ├── marks-allocation/          — UC6 insight skill
│   │   │   └── SKILL.md
│   │   ├── win-theme-audit/           — UC5 insight skill
│   │   │   └── SKILL.md
│   │   ├── review-trajectory/         — UC7 insight skill
│   │   │   └── SKILL.md
│   │   ├── effort-reforecasting/      — UC2 insight skill
│   │   │   └── SKILL.md
│   │   └── stakeholder-engagement/    — UC12 insight skill
│   │       └── SKILL.md
│   ├── commercial-financial/          — Agent 4 skills
│   │   ├── cost-modelling/
│   │   │   └── SKILL.md
│   │   ├── pricing-scenarios/
│   │   │   └── SKILL.md
│   │   ├── risk-premium/
│   │   │   └── SKILL.md
│   │   ├── risk-pricing-validation/   — UC10 insight skill
│   │   │   └── SKILL.md
│   │   └── bid-cost-forecasting/      — UC11 insight skill
│   │       └── SKILL.md
│   ├── content-drafting/              — Agent 5 skills
│   │   ├── response-drafting/
│   │   │   └── SKILL.md
│   │   ├── storyboard-generation/
│   │   │   └── SKILL.md
│   │   ├── evidence-compilation/
│   │   │   └── SKILL.md
│   │   ├── governance-packs/
│   │   │   └── SKILL.md
│   │   └── presentation-intelligence/ — UC15 insight skill
│   │       └── SKILL.md
│   └── solution-delivery/             — Agent 6 skills
│       ├── operating-model/
│       │   └── SKILL.md
│       ├── staffing-model/
│       │   └── SKILL.md
│       ├── transition-planning/
│       │   └── SKILL.md
│       ├── technology-architecture/
│       │   └── SKILL.md
│       └── reviewer-calibration/      — UC8 insight skill
│           └── SKILL.md
│
├── templates/                         — output proforma documents per skill
│   ├── client-intelligence-briefing/
│   ├── incumbent-assessment/
│   ├── competitor-battle-card/
│   ├── scoring-strategy/
│   ├── response-section-draft/
│   ├── governance-pack/
│   ├── cost-model/
│   └── gate-readiness-report/
│
├── reference/                         — static intelligence (ingested via Role 3)
│   ├── bid-library/
│   ├── competitor-dossiers/
│   ├── client-profiles/
│   └── framework-guides/
│
└── commands/                          — explicit slash commands (map to agent + skill)
    ├── ingest-itt.md                  — Agent 1 → itt-extraction skill
    ├── itt-briefing.md                — Agent 1 → procurement-ingestion skill
    ├── client-brief.md                — Agent 2 → client-profiling skill
    ├── competitor-brief.md            — Agent 2 → competitor-profiling skill
    ├── incumbent-review.md            — Agent 2 → incumbent-assessment skill
    ├── scoring-strategy.md            — Agent 3 → scoring-strategy skill
    ├── marks-analysis.md              — Agent 3 → marks-concentration skill
    ├── draft-response.md              — Agent 5 → response-drafting skill
    ├── gate-pack.md                   — Agent 5 → governance-packs skill
    ├── timeline-review.md             — Intelligence → UC1
    ├── compliance-check.md            — Intelligence → UC4
    └── standup-priorities.md          — Intelligence → UC3
```

**Layer responsibilities:**

| Layer | Contains | How used |
|---|---|---|
| Agents | Capability-based configurations (system prompt, tools, knowledge scope) | Selected by command or orchestration layer based on task type |
| Skills | Reusable prompt + tool + template combinations within each agent. Includes both productivity skills (human-invoked, produce deliverables) and insight skills (on-demand/scheduled, write AIInsight records). Both types are implemented identically. | The atomic unit of work — one skill = one defined task |
| Templates | Output proforma documents | Define the shape and structure of every deliverable |
| Reference | Static intelligence documents | Claude draws on during analysis without prompting |
| Commands | Slash command trigger definitions | User-invoked, each maps to a specific agent + skill combination |

### 4.4 ITT Ingestion Skills — Scope and Phasing

Three purpose-built skills automate the extraction of structured data from UK government procurement documentation. These are Role 3 skills — they read external documents and write structured records into the application.

**Skill 1: itt-intelligence (V1)**

| Aspect | Detail |
|---|---|
| **Purpose** | Strategic briefing from the ITT pack — narrative output for the bid team |
| **Input** | Full ITT pack documents (all volumes) |
| **Output** | Written briefing: evaluation methodology, key risks, competitive dynamics, effort allocation recommendations, procurement timeline, TUPE implications, security requirements |
| **Writes to** | No data records — this is a narrative deliverable (Role 2, not Role 3) |
| **Dependencies** | None — works with any ITT pack, no platform entities required |
| **Command** | `/pwin:itt-briefing` |
| **Build priority** | Can build immediately — no data target dependencies |

**Skill 2: itt-ingestion (V1 scope)**

| Aspect | Detail |
|---|---|
| **Purpose** | Structured data extraction from ITT pack into platform entities |
| **Input** | Volume 1 (Instructions/Evaluation), Volume 5 (Response Templates), document metadata |
| **V1 Output** | ResponseSection records (exam paper), EvaluationFramework (scoring methodology), ITTDocument records (document registry), Bid procurement context fields |
| **V2 Output (deferred)** | Requirement records (from Volume 2 Specification), ComplianceRequirement linkage, traceability matrix links |
| **Writes to (V1)** | `create_response_section`, `batch_create_response_sections`, `create_evaluation_framework`, `create_itt_document`, `update_bid_procurement_context` |
| **Dependencies** | ResponseSection, EvaluationFramework, ITTDocument entities must exist in the platform |
| **Command** | `/pwin:ingest-itt` |
| **Build priority** | After Sprint 1a completes (data targets must exist first) |

**Skill 3: clarification-qa (V2 — deferred)**

| Aspect | Detail |
|---|---|
| **Purpose** | Monitor clarification Q&As for requirement changes, competitive intelligence, and action tracking |
| **Input** | Clarification log documents published during tender period |
| **Output** | ClarificationItem records, requirement impact flags, competitive intelligence notes, action items |
| **Writes to** | `create_clarification_item`, `flag_requirement_clarification_impact` (both V2 tools) |
| **Dependencies** | ClarificationItem entity and Requirement entity must exist — both are V2 |
| **Command** | `/pwin:clarification-monitor` |
| **Why deferred** | Depends on Requirement and ClarificationItem entities which are V2 scope. Clarification management can be handled outside the product for MVP |

> **V1/V2 BOUNDARY:** itt-intelligence and itt-ingestion (V1 scope) can be built once the data targets from Sprint 1a exist. Requirements extraction, traceability, and clarification monitoring are deferred to V2 — they require entities that are not in the V1 data model.

---

## 5. MCP Server Design

> **AUTHORITATIVE SOURCE:** The full MCP server architecture is defined in `mcp_server_architecture.md` (v1.0, Session 15). That document supersedes this section for: multi-product data store layout, Data API endpoints, shared entity schemas, Qualify-specific tools, platform knowledge tools, confidence model, and graceful degradation. This section is retained as a quick reference for Bid Execution-specific tool schemas.

### 5.1 What It Is

A single Node.js process running locally that serves two interfaces: (1) a Data API over HTTP (localhost:3456) for each HTML product app to load/save data, and (2) an MCP Server over stdio for Claude to read/write bid data. Both interfaces read and write the same JSON file store. The server is a multi-product platform service — it serves PWIN Qualify, Win Strategy, and Bid Execution from a shared pursuit-level data store. See `mcp_server_architecture.md` for the full architecture.

### 5.2 Read Tools

These tools feed Claude with application data for analysis.

**Activity & Timeline:**
```
get_activities_due_within(bidId, days)
  → Activities where plannedEnd is within N working days of today
  → PREFERRED for targeted analysis — do not load all activities

get_critical_path(bidId)
  → Activities where dependency analysis shows critical path, with buffer times

get_activities_by_workstream(bidId, workstreamCode)
  → All activities in a workstream with status

get_activity(bidId, activityCode)
  → Full activity record including dependencies and current AIInsight

get_dependencies(bidId, activityCode)
  → Full upstream and downstream dependency chain as a graph

get_workstream_summary(bidId)
  → All workstreams with progressPct, timingHealth, and phase
```

**ITT Ingestion & Exam Paper:**
```
get_response_sections(bidId, filters?)
  → ResponseSections (the exam paper) with evaluation weights, word limits, linked ResponseItem status
  → Filters: evaluationCategory, responseType, sectionNumber, hasLinkedResponseItem
  → Returns joined data: ResponseSection fields + linked ResponseItem status (if exists)

get_response_section(bidId, reference)
  → Full ResponseSection record with linked ResponseItem (if exists)

get_evaluation_framework(bidId)
  → EvaluationFramework for this bid (or null if not yet captured)
  → methodology, quality/price/social value weights, scoring scale, pass/fail criteria

get_itt_documents(bidId, filters?)
  → ITTDocument registry with parse status
  → Filters: volumeType, parsedStatus

get_coverage_summary(bidId)
  → ResponseSection count (total exam paper size)
  → ResponseItem count (production started)
  → Coverage percentage (sections with linked ResponseItems)
  → Unstarted sections list (exam questions with no production)
```

**Submissions & Production:**
```
get_response_items(bidId, filters?)
  → ResponseItems with production status, quality dimensions, word counts
  → Joins linked ResponseSection for question text, word limit, evaluation weight
  → Filters: status, responseType, owner, evaluationWeightPct threshold
  → IMPORTANT: use filters for targeted analysis, not full list

get_response_item(bidId, reference)
  → Full ResponseItem record with all quality dimension fields
  → Includes linked ResponseSection data (question text, evaluation criteria, word limit)

get_production_pipeline(bidId)
  → Summary counts at each of the 10 production stages
  → Denominator = ResponseSection count (total exam paper)
  → Pipeline distribution, evaluation weight coverage, quality coverage %

get_compliance_requirements(bidId, filters?)
  → ComplianceRequirements with complianceStatus, coverageStatus, solutionAlignment
  → Filters: classification, complianceStatus, coverageStatus

get_win_themes(bidId)
  → All WinTheme records with integration counts per theme

get_client_scoring_scheme(bidId)
  → ClientScoringScheme with GradeBands (or null if not active)

get_quality_gaps(bidId)
  → ResponseItems with quality dimensions assessed as 'no' or 'partial',
    or self-assessed scores below hurdle marks — pre-filtered for action
  → Includes hurdle score from linked ResponseSection
```

**Reviews:**
```
get_review_cycles(bidId)
  → All ReviewCycle records with status, type, and action summary counts

get_review_cycle_detail(reviewCycleId)
  → Full cycle with scorecards, actions, gate logic status

get_open_review_actions(bidId, severity?)
  → Open/in-progress ReviewActions, optionally filtered by severity
```

**Governance:**
```
get_gate_status(bidId, gateName?)
  → Entry criteria for named gate (or all gates) with current pass/fail per criterion

get_gate_preparation(bidId, gateName)
  → Preparation actions for named gate with completion status
```

**Standup & Actions (new — required by UC3, UC18):**
```
get_standup_actions(bidId, filters?)
  → StandupAction records with owner, dueDate, status, source, dates
  → Filters: status, owner, parentActivityCode, parentGateId, overdue_only
  → Required by UC3 (prioritisation) and UC18 (velocity analysis)

get_deferred_actions(bidId)
  → StandupActions with deferred_count >= 2
  → Pre-filtered for bid manager decision (complete/cancel/escalate)
```

**Calendar & Scheduling (new — required by UC1, UC2):**
```
get_bid_calendar(bidId)
  → BidCalendar with publicHolidays, teamUnavailability, weekendWorking
  → Required for working-day gap calculations in UC1, UC2
```

**Commercial & Engagement (new — required by UC10, UC11):**
```
get_engagement(bidId)
  → Engagement record: costToBid, winFeeValue, feeModel, healthStatus, interventions[]
  → Required by UC10 (risk/pricing), UC11 (spend forecast)

get_rate_card(bidId)
  → RateCard records: roleName, standardDayRate
  → Required by UC2 (resource conflict), UC11 (spend forecast)
```

**Review Calibration (new — required by UC8/UC17):**
```
get_reviewer_history(bidId, reviewerName)
  → All ReviewScorecard records for a specific reviewer across all cycles
  → Includes scores, predictedClientScore, averageScore per cycle
  → Required by UC8 (calibration/bias detection)
```

**Supporting:**
```
get_risks(bidId, filters?)
  → Open RiskAssumptions in both registers (delivery + bid)
  → Filters: registerType, status, probability, impact
  → Required by UC10 (risk pattern detection)

get_stakeholders(bidId)
  → All stakeholder records with type and linked gates

get_team_summary(bidId)
  → TeamMembers with workstream assignments, availability, spend forecast

get_team_member(bidId, memberName)
  → Full TeamMember record with workstreams, rate, clearance
  → Required by UC2, UC12, UC16, UC19, UC20

get_rules(bidId)
  → All embedded rules applicable to this bid archetype

get_bid_library_match(query)
  → Relevant past bid assets matching semantic query [PLACEHOLDER — implement later]

get_competitor_dossier(competitorName)
  → Pre-compiled competitor record [PLACEHOLDER — implement later]
```

### 5.3 Write Tools — AI Write-Back

These tools enable Claude to write structured findings into the application. This is the AI write-back capability.

**Critical rule: write tools must only write to AI-owned fields. They must reject any attempt to modify bid manager-owned fields.**

**Activity-Level Insights:**
```
update_activity_insight(bidId, activityCode, insight: ActivityAIInsight)
  → Appends new AIInsight record to activity
  → APPEND-ONLY — never update or delete previous records

add_risk_flag(bidId, activityCode, risk: { description, severity, cascade_activities[] })
  → Appends risk to activity and to bid-level risk register
```

**Response-Level Insights (future — AI quality monitoring):**
```
update_response_insight(bidId, responseReference, insight: ResponseItemAIInsight)
  → Appends AI quality assessment to response item
  → APPEND-ONLY — never update or delete previous records
  → [PLACEHOLDER — implement when AI quality monitoring is built]
```

**Bid-Level Insights:**
```
update_bid_insight(bidId, insight: BidAIInsight)
  → Appends bid-level insight with PWIN recalibration
  → APPEND-ONLY

log_gate_recommendation(bidId, gateName, recommendation: GateRecommendation)
  → Writes AI gate readiness assessment before review meeting
```

**Gate-Level Insights (new — required by UC9):**
```
create_gate_readiness_report(bidId, gateId, report: GateReadinessAIInsight)
  → Writes gate readiness assessment: per-criterion pass/fail/at-risk,
    process integrity concerns, recovery assessment
  → APPEND-ONLY
  → Auto-generates StandupActions for recoverable amber criteria
```

**Compliance & Coverage Insights (new — required by UC4, UC5, UC6):**
```
create_compliance_coverage_insight(bidId, insight: ComplianceCoverageAIInsight)
  → Weighted coverage risk matrix per ResponseSection
  → Compliance gap register with disqualification risk flags
  → APPEND-ONLY

update_win_theme_coverage_score(bidId, responseSectionReference, score: number)
  → AI-owned field on ResponseSection: win theme coverage score
  → Written by UC5 (win theme audit)

create_effort_allocation_insight(bidId, insight: EffortAllocationAIInsight)
  → Effort efficiency scores, ranked reallocation table, recommended transfers
  → Written by UC6 (marks allocation)
  → APPEND-ONLY
```

**Standup & Action Generation (new — required by UC3, UC9, UC13):**
```
create_standup_action(bidId, action: StandupActionInput)
  → Creates StandupAction with source: ai_generated
  → Used by UC3 (mitigation accepted), UC9 (gate prep), UC13 (clarification impact)

update_standup_action_deferred(bidId, actionId, data: { deferred_count, escalation_recommended, recommended_decision })
  → Writes AI-owned fields on existing StandupAction
  → Used by UC3 (carry-forward flagging), UC18 (velocity analysis)
```

**Response Section Amendment (new — required by UC13, UC14):**
```
flag_response_section_amended(bidId, reference, reason: string)
  → Sets ResponseSection.lastAmended to current timestamp
  → AI-writable field — records that a clarification or amendment affected this section
  → Used by UC13 (clarification impact), UC14 (ITT amendment)
```

**Team Performance Insights (new — required by UC16-20, V2/V3):**
```
create_team_member_insight(bidId, memberName, insight: TeamMemberAIInsight)
  → Quality profile, coaching brief, strength profile
  → APPEND-ONLY
  → Framing: coaching and resourcing intelligence only
  → Access restricted to bid manager and bid director roles
  → [V2/V3 — requires multi-bid data for meaningful signal]
```

**Ingestion (Role 3) — V1:**
```
create_response_section(bidId, data: ResponseSectionInput)
  → Creates ResponseSection from parsed ITT response template
  → Used by /pwin:ingest-itt and CSV import
  → Returns created record with UUID

batch_create_response_sections(bidId, data: ResponseSectionInput[])
  → Batch creation for efficiency during full ITT ingestion
  → Returns array of created records with UUIDs

create_itt_document(bidId, data: ITTDocumentInput)
  → Creates ITTDocument record in the document registry
  → Returns created record with UUID

create_evaluation_framework(bidId, data: EvaluationFrameworkInput)
  → Creates or updates the EvaluationFramework for a bid (one per bid)
  → Returns created/updated record

update_bid_procurement_context(bidId, data: BidProcurementContextInput)
  → Updates procurement context fields on Bid (route, portal, duration, TUPE, etc.)
  → Only writes to procurement context fields, not bid manager-owned fields

ingest_scoring_scheme(bidId, scheme: ClientScoringSchemeInput)
  → Creates or updates ClientScoringScheme with GradeBands from parsed ITT

generate_report_output(bidId, type: string, content: string)
  → Stores AI-generated report with reference link in bid record
```

**Ingestion (Role 3) — V2 (deferred, depends on Requirement and ClarificationItem entities):**
```
create_requirement(bidId, data: RequirementInput)
  → Creates Requirement from parsed specification [V2]

batch_create_requirements(bidId, data: RequirementInput[])
  → Batch creation for full specification ingestion [V2]

link_requirement_to_response_section(requirementId, responseSectionId)
  → Adds traceability link (many-to-many) [V2]

create_clarification_item(bidId, data: ClarificationItemInput)
  → Creates ClarificationItem from parsed Q&A log [V2]

flag_requirement_clarification_impact(requirementId, clarificationItemId)
  → Sets impact flag on Requirement [V2]

ingest_compliance_requirement(bidId, requirement: ComplianceRequirementInput)
  → Creates ComplianceRequirement, optionally linked to parent Requirement [V2]
```

---

## 6. The AIInsight Schema — The Missing Piece

The `AIInsight` entity exists in the data model but its field-level definition has not been formalised. **This is the first thing to implement** — everything else depends on it.

### 6.1 Activity-Level AIInsight

```
ActivityAIInsight {
  id:                   UUID                         — new record each run
  activityId:           FK → Activity
  bidId:                FK → Bid
  gap_working_days:     integer | null               — null if on track
  rag_status:           'RED' | 'AMBER' | 'GREEN'   — AI field, separate from manager's status
  is_critical_path:     boolean                      — derived from dependency analysis
  cascade_risk:         'HIGH' | 'MEDIUM' | 'LOW' | 'NONE'
  downstream_impact:    ActivityImpact[]             — [{ activityCode, name, slip_days }]
  ai_narrative:         string                       — max 3 sentences, plain English
  mitigation_options:   MitigationOption[]           — min 2, max 4
  rule_violations:      string[]                     — rule codes e.g. ['RULE-012']
  confidence:           'HIGH' | 'MEDIUM' | 'LOW'
  generated_at:         ISO datetime
  model_version:        string                       — e.g. 'claude-sonnet-4-6'
}

MitigationOption {
  option:               string                       — e.g. 'Accelerate' | 'Descope' | 'Escalate' | 'Accept'
  action:               string                       — specific action to take
  recovers_days:        integer                      — working days recovered if taken
  trade_off:            string                       — what is given up
}

ActivityImpact {
  activityCode:         string                       — e.g. 'SOL-07'
  name:                 string
  slip_days:            integer
}
```

### 6.2 Response-Level AIInsight (Future — AI Quality Monitoring)

> **NOTE:** This schema is designed for the future AI quality monitoring layer. In the base product, quality dimensions are manually assessed by the bid manager. This entity enables AI to continuously assess the same dimensions automatically.

```
ResponseItemAIInsight {
  id:                   UUID
  responseItemId:       FK → ResponseItem
  bidId:                FK → Bid
  answers_question:     'YES' | 'NO' | 'PARTIAL'
  follows_structure:    'YES' | 'NO' | 'PARTIAL'
  predicted_score:      integer | null               — against ClientScoringScheme if active
  predicted_grade_band: string | null                — e.g. 'Good — 7-8'
  meets_hurdle:         boolean | null               — predicted_score >= hurdleScore
  credentials_present:  boolean
  credentials_refs:     string[]                     — which credentials detected
  win_themes_detected:  string[]                     — WinTheme references found in text
  win_themes_missing:   string[]                     — linked WinThemes NOT found
  word_count:           integer | null               — AI-measured current word count
  word_count_status:    'WITHIN_LIMIT' | 'OVER_LIMIT' | 'SIGNIFICANTLY_UNDER' | null
  quality_narrative:    string                       — max 3 sentences, plain English
  improvement_actions:  string[]                     — specific improvements recommended
  confidence:           'HIGH' | 'MEDIUM' | 'LOW'
  generated_at:         ISO datetime
  model_version:        string
}
```

### 6.3 Bid-Level AIInsight

```
BidAIInsight {
  id:                   UUID
  bidId:                FK → Bid
  pwin_recommended:     integer (0-100)
  pwin_delta:           integer                      — change from previous, positive = improving
  pwin_rationale:       string                       — max 4 sentences
  portfolio_rag:        'RED' | 'AMBER' | 'GREEN'
  at_risk_activities:   string[]                     — activity codes currently RED or at risk
  production_health:    ProductionHealth
  resource_conflicts:   ResourceConflict[]
  gate_readiness:       GateReadiness
  generated_at:         ISO datetime
  model_version:        string
}

ProductionHealth {
  total_response_sections:  integer                  — the full exam paper (denominator)
  total_response_items:     integer                  — production started (numerator)
  production_coverage_pct:  number                   — response_items / response_sections * 100
  pipeline_distribution:    Object                   — counts at each of the 10 stages
  quality_coverage_pct:     number                   — % of items with quality dimensions assessed
  below_hurdle_count:       integer                  — items predicted below hurdle mark (hurdle from ResponseSection)
  win_theme_coverage_pct:   number                   — % of linked themes integrated
  compliance_gaps:          integer                  — mandatory requirements at unmapped/gap
}

ResourceConflict {
  person:               string
  activities:           string[]                     — activity codes assigned concurrently
  conflict_description: string
}

GateReadiness {
  gate:                 string
  ready:                boolean
  blockers:             string[]                     — activity codes or rule codes blocking
}
```

### 6.4 Gate Readiness AIInsight (new — UC9)

```
GateReadinessAIInsight {
  id:                   UUID
  gateId:               FK → GovernanceGate
  bidId:                FK → Bid
  overall_status:       'GREEN' | 'AMBER' | 'RED'
  criteria_assessments: CriterionAssessment[]
  process_integrity:    ProcessIntegrityFlag[]
  governance_gaps:      GovernanceGap[]
  recovery_assessment:  string                       — can amber criteria be recovered in time?
  ai_narrative:         string                       — max 4 sentences
  generated_at:         ISO datetime
  model_version:        string
}

CriterionAssessment {
  criterion:            string                       — entry criterion description
  status:               'PASS' | 'FAIL' | 'AT_RISK'
  linked_activity:      string | null                — activity code if applicable
  recovery_days:        integer | null               — working days to recover, null if pass
  recommended_action:   string | null
}

ProcessIntegrityFlag {
  activity_code:        string
  concern:              string                       — e.g. 'reviewer and owner are the same person'
  severity:             'HIGH' | 'MEDIUM'
}

GovernanceGap {
  gate_id:              string
  gap_type:             'NO_APPROVER' | 'INACTIVE_APPROVER' | 'NO_REVIEWER'
  description:          string
}
```

### 6.5 Compliance Coverage AIInsight (new — UC4)

```
ComplianceCoverageAIInsight {
  id:                   UUID
  bidId:                FK → Bid
  section_risks:        SectionRisk[]
  compliance_gaps:      ComplianceGap[]
  disqualification_risks: string[]                   — ResponseSection references at disqualification risk
  ai_narrative:         string
  generated_at:         ISO datetime
  model_version:        string
}

SectionRisk {
  response_section_ref: string
  marks_at_risk:        number
  days_to_submission:   integer
  coverage_status:      string
  recommended_action:   string
  risk_severity:        'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
}

ComplianceGap {
  requirement_text:     string
  classification:       string
  compliance_status:    string
  risk_label:           'DISQUALIFICATION' | 'SCORE_LOSS' | 'MINOR'
}
```

### 6.6 Effort Allocation AIInsight (new — UC6)

```
EffortAllocationAIInsight {
  id:                   UUID
  bidId:                FK → Bid
  section_efficiency:   SectionEfficiency[]
  recommended_transfers: EffortTransfer[]
  hurdle_exceptions:    string[]                     — sections exempt from efficiency calc
  ai_narrative:         string
  generated_at:         ISO datetime
  model_version:        string
}

SectionEfficiency {
  response_section_ref: string
  marks_available:      number
  effort_days:          number
  marks_per_day:        number
  classification:       'OVER_INVESTED' | 'UNDER_INVESTED' | 'BALANCED' | 'HURDLE_EXEMPT'
}

EffortTransfer {
  from_section:         string
  to_section:           string
  person_days:          number
  marks_impact:         string                       — e.g. 'releases 2 days from 5-mark section to 25-mark section'
}
```

### 6.7 Team Member AIInsight (new — UC16-20, V2/V3)

> **NOTE:** These schemas require multi-bid data for meaningful signal. Build data collection in V1, surface intelligence in V2/V3. All ai_narrative fields must be framed as coaching and resourcing intelligence, not performance evaluation.

```
TeamMemberAIInsight {
  id:                   UUID
  teamMemberName:       string
  bidId:                FK → Bid
  recurring_weaknesses: RecurringWeakness[]
  improvement_trajectory: 'IMPROVING' | 'PLATEAUING' | 'DECLINING'
  strength_profile:     StrengthDimension[]
  coaching_brief:       string                       — specific, actionable, non-evaluative
  disputed_action_rate: number | null                — % of actions disputed
  ai_narrative:         string                       — coaching framing only
  generated_at:         ISO datetime
  model_version:        string
}

RecurringWeakness {
  criterion:            string                       — quality dimension name
  action_count:         integer
  avg_severity:         string
  pattern:              string                       — description of recurring pattern
}

StrengthDimension {
  criterion:            string
  above_team_avg_by:    number                       — points above team average
  recommendation:       string                       — e.g. 'deploy on highest-mark questions in this dimension'
}
```

### 6.8 The Ownership Boundary

**Claude never writes to bid manager-owned fields. This must be enforced at the MCP server API layer — not just as a convention.**

| Bid Manager Owns (Claude must never write) | Claude Owns (bid manager must never edit) | AI Can Create (Role 3 ingestion) |
|---|---|---|
| Activity: owner, status, plannedStart/End, actualStart/End, notes, dependencies[], outputAssurance | ActivityAIInsight: rag_status, gap_working_days, cascade_risk, downstream_impact[], ai_narrative, mitigation_options[], rule_violations[], confidence. Activity.forecastEnd (AI-owned, separate from plannedEnd — UC2) | — |
| ResponseItem: status (10-stage), all quality dimension fields, owner, dueDate, notes | ResponseItemAIInsight: all fields (future). ResponseItem.effortAllocationEfficiency (AI-owned — UC6) | — |
| ResponseSection: questionText, evaluationCriteria, evaluationMaxScore, hurdleScore, wordLimit | ResponseSection.winThemeCoverageScore (AI-owned — UC5). ResponseSection.lastAmended (AI-writable for clarification/amendment flagging — UC13, UC14) | ResponseSection: all fields (ingested data — exam paper) |
| ComplianceRequirement: complianceStatus, complianceExplanation, solutionAlignment | ComplianceRequirement.impactedByClarification (AI-writable — UC13). ComplianceCoverageAIInsight: all fields (UC4) | — |
| ReviewAction: status, resolutionNotes (reviewer-owned) | — | — |
| GovernanceGate: decision, conditions, riskPremiumPct | GateReadinessAIInsight: all fields (UC9). GateRecommendation (AI advisory) | — |
| WinTheme: statement, rationale, status | WinTheme.portfolioSaturationRating (AI-owned — UC5) | — |
| StandupAction: owner, dueDate, status (for existing actions) | StandupAction.deferred_count, escalation_recommended, recommended_decision (AI-owned — UC3, UC18) | StandupAction: new records with source: ai_generated (UC3, UC9, UC13) |
| TeamMember: all core fields | TeamMemberAIInsight: all fields (V2/V3 — UC16-20). Coaching framing only. | — |
| Engagement: all fields | EffortAllocationAIInsight: all fields (UC6). BidAIInsight.budget_forecast (UC11) | — |
| — | — | EvaluationFramework: all fields (ingested data) |
| — | — | ITTDocument: all fields (ingested data) |
| — | — | Bid: procurement context fields only (procurementRoute, portalPlatform, etc.) |

> **KEY PRINCIPLE:** Quality dimensions on ResponseItem are bid manager-owned in the base product. When the AI quality monitoring layer is built, AI writes to ResponseItemAIInsight (a separate entity) — it never overwrites the bid manager's manual assessment. The two assessments coexist, enabling comparison.

### 6.5 Append-Only Rule

AIInsight records are append-only. Each analysis run creates a new record. Previous records are never updated or deleted. This preserves a full audit trail and enables trend analysis over time (is the bid getting healthier or worse?).

---

## 7. The Unified Skill Model (Session 14)

### 7.1 One Implementation Pattern — Not Two Layers

**Decision: there is no separate "intelligence layer." Every AI capability — whether it extracts documents, drafts responses, or analyses timeline risk — is implemented as a skill within an agent.**

A skill is a Claude API call with:
1. A **system prompt** — agent persona, operating rules, quality standards
2. **MCP tool access** — which read/write tools the skill can use
3. **Input specification** — what data or documents the skill consumes
4. **Output specification** — structured data (AIInsight), narrative report, or deliverable document
5. **Quality criteria** — how to evaluate whether the output is good

The previous architecture (v1.4) described two separate systems: "Layer 2 — AI Skills (productivity)" from the suitability assessment and "Layer 3 — AI Intelligence (supervisory)" from the 20 use cases. In practice, both are implemented identically — prompt + tools + Claude API call = output. The distinction was a product design concept (who triggers it, what it reads) not an engineering distinction. Maintaining two separate systems for the same pattern adds complexity without benefit.

**What differs between skills is configuration, not infrastructure:**

| Dimension | Productivity Skills | Insight Skills |
|---|---|---|
| **Triggered by** | Bid manager: "analyse this ITT" | On-demand command (V1) or schedule/event (V2) |
| **Reads** | Uploaded documents + internal bid data | Internal bid data only |
| **Produces** | Deliverables (reports, drafts, models, structured data) | AIInsight records written back into the app |
| **Example** | Agent 1: extract requirements from uploaded PDF | Agent 3: analyse timeline gaps from activity dates |
| **Human review** | Review and refine output | Review flagged risks and accept/reject mitigations |

Both use the same MCP server, the same Claude API, the same agent configurations.

### 7.2 The 20 Use Cases — Now Skills Within Agents

The 20 AI use cases designed in Session 13 are implemented as insight skills distributed across the six capability-based agents. Each use case becomes a skill within the agent whose data domain it belongs to.

**Full specification:** `ai_use_cases_reference.html` in the docs folder. This remains the authoritative design reference for what each skill reasons over, what it writes back, and its UX implications. The only change is organisational — use cases are no longer a separate system but skills within agents.

**Use case to agent mapping:**

| Agent | Insight Skills (from use cases) | Rationale |
|---|---|---|
| **Agent 3: Strategy & Scoring** | UC1 (Timeline Analysis), UC2 (Effort Reforecasting), UC3 (Standup Prioritisation), UC4 (Compliance Coverage), UC5 (Win Theme Audit), UC6 (Marks Allocation), UC7 (Review Trajectory) | All reason over activity spine, response quality, and scoring data — Agent 3's core domain |
| **Agent 4: Commercial & Financial** | UC10 (Risk/Pricing Validation), UC11 (Bid Cost Forecasting) | Commercial data domain |
| **Agent 1: Document Intelligence** | UC13 (Clarification Impact), UC14 (ITT Amendment Detection) | Document ingestion and cross-referencing |
| **Agent 5: Content & Response Drafting** | UC15 (Presentation Intelligence) | Content generation domain |
| **Agent 3: Strategy & Scoring** | UC9 (Gate Readiness), UC12 (Stakeholder Engagement) | Governance analysis |
| **Agent 6: Solution & Delivery** | UC8 (Reviewer Calibration) | Team/reviewer data domain |
| **Deferred (V2/V3)** | UC16-20 (Team Performance) | Requires multi-bid data |

**Key design decisions (unchanged from Session 13):**
- All 24 data entities are covered. No data is collected but unanalysed.
- Every use case specifies: entities and fields consumed, what Claude reasons over, what is written back and where, and the UX design implication.
- UC8 and UC17 are duplicates — consolidated to single implementation.
- Theme E (UC16-20) requires multi-bid data — V2/V3 capability.
- All insight skills launch as on-demand in V1. Scheduled triggers are V2.

**Build priority (insight skills):**

| Priority | Skill(s) | Agent | Rationale |
|---|---|---|---|
| 1 | UC1 (Timeline) + UC4 (Compliance) | Agent 3 | MCP foundation, highest value, proves AIInsight pattern |
| 2 | UC3 (Standup) + UC9 (Gate Readiness) | Agent 3 | Daily operational + governance value |
| 3 | UC6 (Marks Allocation) | Agent 3 | Direct score improvement |
| 4 | UC5, UC7 | Agent 3 | Proposal quality |
| 5 | UC13 | Agent 1 | Clarification chain (V2 data dependency) |
| 6 | UC10, UC11 | Agent 4 | Commercial intelligence |
| 7 | UC14, UC15 | Agents 1, 5 | Amendment detection, presentation intelligence |
| 8 | UC2, UC8, UC12 | Agents 3, 6 | Secondary insight layer |
| 9 | UC16-20 | Deferred | Team performance (requires multi-bid data) |

### 7.3 Timeline Analysis — Reference Skill (Build First)

Timeline analysis (UC1) is the first insight skill to build because it proves the full end-to-end loop: command triggers → MCP reads → Claude analyses → MCP writes AIInsight → application renders.

**What it does:** Claude reads activity data for an active bid, applies the embedded rules and dependency graph, identifies activities behind schedule or at risk, calculates gap and cascade impact, and writes structured AIInsight records back into the application. The user sees AI analysis as native application content — not a chat response.

**The intelligence goes beyond simple date comparison:**

1. Gap in working days (not calendar days) — uses BidCalendar
2. Distinction between late-but-recoverable and past the point of recovery
3. Dependency cascade — compound slip across the full dependency chain, respecting dependencyThreshold settings
4. Rule violation detection — flags sequencing violations, not just date violations
5. Predictive warning — flags on-time activities with risk characteristics:
   - Insufficient buffer before a hard deadline
   - Resource assigned to multiple concurrent activities (cross-reference TeamMember.workstreams)
   - Dependency on a third party with no confirmed commitment
6. Critical path prioritisation — one day on the critical path is weighted as more serious than three days on a non-critical workstream

**The closed loop:**

```
Application         MCP Server                    Claude
───────────         ──────────                    ──────
Activities    ───▶   get_critical_path()        ───▶  Reads schedule
Planned dates ───▶   get_activities_due_within() ───▶  Identifies gaps
Rules         ───▶   get_rules()               ───▶  Applies rule logic
Dependencies  ───▶   get_dependencies()         ───▶  Traces cascade
     ▲                                                 │
     │                                                 ▼
UI updates   ◀──    update_activity_insight()   ◀──  Writes findings
Risk register◀──    add_risk_flag()             ◀──  With confidence
                                                      And mitigations
```

**Context window constraint:** For a bid with 84 activities, Claude must never load all records simultaneously. The MCP server must expose filtered queries. The timeline analysis skill must use `get_activities_due_within()` and `get_critical_path()` rather than loading everything.

---

## 8. SaaS Trajectory

### 8.1 Current State

Self-contained HTML applications with local data storage. Intentional — proves methodology on live engagements before infrastructure investment. HTML-first, single-file, vanilla JavaScript only.

### 8.2 What Changes at SaaS — and What Does Not

| Layer | Now | SaaS |
|---|---|---|
| Data persistence | localStorage / local JSON | Supabase (Postgres) |
| MCP server | Local Node.js stdio process | Azure Function or Supabase Edge Function |
| Authentication | None — single user, local | OAuth / Row Level Security, multi-tenant |
| Plugin distribution | ZIP file or GitHub | Private marketplace |
| Application hosting | Local file / Azure Static Web Apps | Azure Static Web Apps (same) |
| **Plugin intelligence layer** | **Plugin skills, agents, commands** | **Unchanged — no rebuild** |
| **MCP tool schemas** | **Defined in .mcp.json** | **Unchanged — same schemas, different host** |
| **Data model / schema** | **As defined in Architecture v6** | **Unchanged — becomes database schema directly** |

> **THE KEY PRINCIPLE:** The intelligence layer does not change at SaaS transition. Only the infrastructure underneath changes. Every schema field and MCP tool definition built now is a permanent investment. The Architecture v6 schema becomes the database schema. The MCP tool definitions become API endpoint definitions.

### 8.3 Recommended SaaS Stack (When the Decision Is Made)

- **Database:** Supabase — Postgres-compatible, real-time subscriptions, built-in auth, Row Level Security for multi-tenancy
- **MCP server:** Supabase Edge Function or Azure Function — same tool schemas, HTTP transport instead of stdio
- **Hosting:** Azure Static Web Apps — already the target for current HTML application
- **Plugin distribution:** Anthropic plugin marketplace with organisation-scoped private distribution

---

## 9. Build Instructions for Claude Code

### 9.1 Phasing — Data Targets Before MCP, MCP Before Skills

The plugin architecture is a forward-looking design document. Build priority follows a clear dependency chain: data targets → MCP server → first agent + skills → remaining agents + skills.

**Phase 1a (current — Sprint 1a):** ITT ingestion data layer — ResponseSection, EvaluationFramework, ITTDocument entities. ResponseItem migration. CSV import. Auto-migration of existing data.

**Phase 1 (in progress):** Complete core Bid Execution modules — Submissions (10-stage lifecycle, quality dimensions, win themes, client scoring, ResponseSection/ResponseItem joined view), Reviews (dual scorecard), Governance (development reviews absorbed), Workspace, Activity Tracker, Readiness Dashboard.

**Phase 2 — MCP Server (critical path):** Shared infrastructure for all six agents. Data access layer with filtered queries, field-level permission model (owner: bid_manager | ai), AIInsight entity schemas and append-only write capability. This is the foundation everything else depends on.

**Phase 3 — Agent 1 (Document Intelligence) + Agent 3 first insight skills:** Two parallel tracks:
- Agent 1 productivity skills: ITT extraction, compliance mapping, contract analysis (itt-intelligence, itt-ingestion V1 scope). Transforms the first 2 weeks of every bid.
- Agent 3 insight skills: UC1 (Timeline Analysis) + UC4 (Compliance Coverage). Proves the AIInsight write-back pattern and MCP architecture. UX conventions established: RAG flags on Gantt, heat maps on Response Register, mitigation cards, persistent banners.

**Phase 4 — Agent 3 expanded + Agent 5 (Content Drafting):** Two parallel tracks:
- Agent 3 additional insight skills: UC3 (Standup Prioritisation) + UC9 (Gate Readiness) + UC6 (Marks Allocation). Daily operational, governance, and scoring value.
- Agent 5 productivity skills: Response drafting, storyboard generation, evidence compilation. Highest-visibility skills — writers refine AI drafts instead of writing from scratch.

**Phase 5 — Agent 2 (Market Intelligence) + Agent 4 (Commercial):**
- Agent 2 productivity skills: Client profiling, competitor analysis, incumbent assessment, sector scanning. Includes recurring/scheduled operation outside individual bids.
- Agent 4 productivity skills: Cost modelling, pricing scenarios, risk premium validation. Plus insight skills UC10 (Risk/Pricing) + UC11 (Bid Cost Forecasting).

**Phase 6 — Agent 6 (Solution & Delivery) + remaining insight skills:**
- Agent 6 productivity skills: Operating model, staffing, transition, technology architecture.
- Remaining insight skills distributed across agents: UC5, UC7, UC8, UC12, UC13, UC14, UC15.

**Phase 7 (V2):** Requirement and ClarificationItem entities. Requirements Register and Traceability Matrix views. itt-ingestion extended scope (specification extraction). clarification-qa skill. Full requirements traceability. Theme E team performance insight skills (UC16-20) — requires multi-bid data.

> **UNIFIED SKILL MODEL (Session 14):** There is no separate "intelligence layer." All AI capabilities — productivity skills and insight skills — are implemented identically as skills within agents. The difference is trigger type (human-invoked vs on-demand/scheduled) and data direction (reads external docs vs reads internal data only). See Section 7 for the full rationale. The `ai_use_cases_reference.html` document remains the authoritative specification for what each insight skill reasons over and writes back.

### 9.2 Plugin Build Sequence — When the Time Comes

1. **Formalise AIInsight entities** — add ActivityAIInsight, ResponseItemAIInsight (placeholder), and BidAIInsight to the Architecture v6 data model.

2. **Write the MCP tool schema document** — derive all read and write tools from Architecture v6 entities (Sections 5.2 and 5.3 above) as a standalone reference file.

3. **Implement MCP server — read tools first** — Node.js stdio process. Validate that Claude can retrieve activity and response item data correctly before adding write tools.

4. **Add write tools with boundary enforcement** — the MCP server must reject any write to a bid manager-owned field at the API layer.

5. **Build Agent 1 (Document Intelligence) AGENT.md and first productivity skill** — itt-extraction SKILL.md. The foundation agent — all other agents depend on its outputs.

6. **Build Agent 3 (Strategy & Scoring) first insight skill** — timeline-analysis SKILL.md (UC1). Encodes the six-layer analysis described in Section 7.3. Proves the AIInsight write-back pattern.

7. **Implement `/pwin:ingest-itt` and `/pwin:timeline-review` commands** — validate two end-to-end loops: (a) document upload → Agent 1 productivity skill → MCP writes structured data; (b) command triggers → Agent 3 insight skill → MCP reads → Claude analyses → MCP writes AIInsight → application renders.

### 9.3 Design Constraints — Non-Negotiable

- **One plugin, not multiple.** Six capability-based agents provide specialisation inside the single plugin (see Section 4.2a).
- **Both IDs must be present.** UUID is the system identifier. Activity code (SOL-04) is the human label. Both are required and must coexist on every activity record.
- **Enumerated values are fixed.** No free text variants for status, RAG, classification, or confidence fields. Use the defined enums exactly.
- **AIInsight is append-only.** Never update or delete a previous AI insight record.
- **Claude never writes to bid manager-owned fields.** Enforce this at the MCP server layer, not just as a convention.
- **Use filtered MCP queries.** Never load all activities or response items simultaneously. Use targeted queries with filters.
- **Design for SaaS from day one.** Every field name, enum value, and tool schema will become a database column or API endpoint. Name things accordingly.
- **Architecture v6 is the schema authority.** If this document conflicts with the architecture doc, the architecture doc wins.

### 9.4 Out of Scope for This Build Phase

- Bid Library, Competitor Dossier, and Client Profile MCP tools — include as placeholder definitions in the schema document but do not implement yet
- ResponseItemAIInsight implementation — schema is defined, implementation waits for AI quality monitoring build
- Scheduled task configuration — this is a Cowork setup step, not a build step
- SaaS infrastructure — Supabase, hosted MCP server, multi-tenancy — these come after the HTML prototype is validated on a live engagement
- Full plugin manifest with all six agents — Agent 1 (Document Intelligence) and timeline-analysis intelligence skill are the build priority; other agents follow per the dependency chain in Section 4.2a

### 9.5 V1/V2 Scope Boundary (decided Session 8, 2026-03-27)

**V1 — Build Now:**

| What | Status |
|---|---|
| ResponseSection entity (exam paper) | Sprint 1a |
| EvaluationFramework entity (one per bid) | Sprint 1a |
| ITTDocument entity (document registry) | Sprint 1a |
| Bid extended with procurement context | Sprint 1a |
| ResponseItem migrated (question fields → ResponseSection) | Sprint 1a |
| CSV import for ResponseSections | Sprint 1a |
| Auto-migration of existing ResponseItem data | Sprint 1a |
| Submissions Response Register joins through ResponseSection | Sprint 1a |
| Coverage Dashboard uses ResponseSection as denominator | Sprint 1a |
| itt-intelligence skill (narrative briefing) | Phase 2 |
| itt-ingestion skill V1 scope (ResponseSection, EvaluationFramework, ITTDocument extraction) | Phase 2 |
| MCP read tools for new entities | Phase 3 |
| MCP write tools for V1 entities (create_response_section, create_evaluation_framework, etc.) | Phase 3 |

**V2 — Deferred (build when core product is battle-tested):**

| What | Why deferred |
|---|---|
| Requirement entity | Too large for MVP — a product in its own right. Pulls in Requirements Register view, Traceability Matrix view, many-to-many cross-referencing |
| ClarificationItem entity | Clarification management can live outside the app for now |
| Requirements Register view in Submissions | Depends on Requirement entity |
| Traceability Matrix view in Submissions | Depends on Requirement entity + ResponseSection many-to-many |
| ComplianceRequirement.linkedRequirementId FK | No parent Requirement entity in V1 |
| ResponseSection.linkedRequirementIds | No Requirement entity in V1 |
| itt-ingestion extended scope (specification extraction) | No Requirement entity to write to |
| clarification-qa skill | No ClarificationItem entity to write to |
| MCP write tools for V2 entities | No entities to write to |

> **WHY THIS BOUNDARY:** The product isn't finished yet. Adding Requirement pulls in two complex new views and many-to-many rendering before existing views are battle-tested. Better to live with the exam paper / answer sheet split, ship the core product, and let real usage inform the shape of Requirements when the time comes.

---

## 10. Key Terms Reference

| Term | Definition |
|---|---|
| PWIN | Probability of Win — expressed as 0-100 integer |
| ITT | Invitation to Tender |
| BAFO | Best and Final Offer |
| TCV | Total Contract Value |
| ACV | Annual Contract Value |
| Gate | Internal governance review at defined stage of bid lifecycle |
| MCP | Model Context Protocol — Anthropic's open standard for AI-to-tool integration |
| AIInsight | The structured object Claude writes back into the application after analysis |
| Write-back | The act of Claude writing structured findings into the application (not just responding in chat) |
| Append-only | Records that are added to but never edited or deleted |
| Critical path | The sequence of activities where any slip directly extends the submission date |
| Services archetype | The default bid template for services contracts (as opposed to Technology or Advisory) |
| Paid on Award | PWIN Architect's commercial model — fees contingent on contract award |
| Production lifecycle | 10-stage progression for response items: not_started → storyboard → storyboard_approved → first_draft → pink_ready → pink_reviewed → red_ready → red_reviewed → gold_ready → final |
| Quality dimensions | 6 structured assessment fields per response item (answers question, follows structure, score, credentials, win themes, compliance mapping) |
| Dual scoring | Internal quality score (1-5, diagnostic) + predicted client score (predictive) used in Reviews |
| Win theme | Differentiating value proposition statement developed during capture and refined at ITT receipt |

---

*PWIN Architect — AI Plugin Architecture Brief | v1.5 | April 2026 | BIP Management Consulting | Confidential*
*Aligned with Architecture v6, Session 14 (2026-04-02). Incorporates 20 AI intelligence use cases, practitioner-validated AI suitability assessment (295 L3 tasks), and capability-based agent architecture (6 agents, ~25 skills).*
