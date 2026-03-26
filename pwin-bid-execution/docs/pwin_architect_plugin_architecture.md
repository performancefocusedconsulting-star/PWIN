# PWIN Architect — Bid Execution Product
## AI Plugin Architecture Brief for Claude Code

**Version:** 1.1 | March 2026
**Status:** Authoritative design input for all Claude Code build sessions
**Scope:** Plugin architecture, MCP server design, data schema, AI write-back capability, SaaS trajectory
**Aligned with:** Architecture v6 (Session 7, 2026-03-26)

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
| Bid Execution | Full bid lifecycle management. 79 activities, 10 workstreams, governance gates, submissions engine | Architecture complete — build in progress |
| PWIN Architect Plugin | AI intelligence layer across all products. MCP-connected. Persona-routed sub-agents | Design complete — build starting |
| Bid Library | Past proposals, case studies, evidence blocks. Shared data source across all products | Concept — to be built |
| Competitor Dossiers | Pre-compiled intelligence on frequent competitors. Quarterly refresh cadence | Concept — to be built |
| Client Profiles | Buyer intelligence, stakeholder maps, procurement history by buyer | Concept — to be built |

### The Shared Intelligence Layer

A critical architectural principle: the Bid Execution product is **one data source among several**. The plugin reasons across all of them simultaneously:

- **Bid Execution product** — live pursuit data, activity status, response item production progress, compliance coverage, review scores, governance gate status
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

Confirmed architecture (from Claude Code build sessions, Architecture v6 — Session 7):
- **79 activities** across **10 workstreams**
- **Services archetype** as the default template (new business and rebid)
- **Governance gates** covering development assurance (solution, commercial, risk reviews) and executive governance (price, risk, margin approval)
- **Submissions engine** with 10-stage production lifecycle for response items and per-response quality dimensions
- **Reviews module** for formal peer/SME review of written responses at pink, red, and gold stages with dual scoring
- **Win theme tracking** with integration heatmap across all response items
- **Optional client scoring scheme** with grade bands and hurdle marks
- **Dual-track readiness** — development complete AND production complete
- **Backward-planned timeline** from submission deadline

### 3.2 The 10 Workstreams

| Code | Workstream | Phase | Activity Count |
|---|---|---|---|
| SAL | Sales & Customer Intelligence | Development | ~10 |
| SOL | Solution Design | Development | ~10 |
| COM | Commercial & Pricing | Development | ~6 |
| LEG | Legal & Contractual | Development | ~6 |
| DEL | Programme & Delivery | Development | ~6 |
| SUP | Supply Chain & Partners | Development | ~6 |
| BM | Bid Management & Programme Control | Continuous | ~12 |
| GOV | Internal Governance | Continuous | ~5 |
| PRD | Proposal Production | Production | ~9 |
| POST | Post-Submission | Post-Submission | ~8 |

### 3.3 The Data Model — 21 Entities (Architecture v6 — Session 7)

> **AUTHORITATIVE SOURCE:** The field-level schema is defined in `bid_execution_architecture_v6.html`. The summary below is for plugin design reference. If any field here conflicts with Architecture v6, the architecture document wins.

**Core Entities:**

| Entity | Purpose | Key Fields |
|---|---|---|
| **Bid** | Top-level container | archetype, tcv, acv, submissionDeadline, ittIssueDate, status (setup/active/submitted/post_submission/won/lost/withdrawn) |
| **BidCalendar** | Scheduling constraints | workingDays, publicHolidays, weekendWorking, teamUnavailability, clientBlackouts |
| **Workstream** | Major track of activity | code, phase (development/production/post_submission/continuous), progressPct (computed), timingHealth (computed) |
| **Activity** | Atomic unit of work — THE SPINE | code (human label e.g. SOL-04), status, outputAssurance (unassured/under_review/assured/accepted_at_gate), effortDays, teamSize, parallelisationType (P/S/C), dependencies[], dependencyThreshold, lastUpdated |

**Submissions Entities (10-stage production lifecycle):**

| Entity | Purpose | Key Fields |
|---|---|---|
| **ResponseItem** | ITT deliverable — the granular unit of production work | reference, questionText, responseType, status (10-stage: not_started/storyboard/storyboard_approved/first_draft/pink_ready/pink_reviewed/red_ready/red_reviewed/gold_ready/final), evaluationWeightPct, wordLimit, currentWordCount, hurdleScore (optional), quality dimensions (6 structured fields — AI-ready) |
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

### 4.1 Three Distinct Roles

The plugin performs three roles. Each must be explicitly designed for in the MCP tool schema.

**Role 1 — In-Application AI Intelligence Layer** *(primary role)*
Claude surfaces insight inside the Bid Execution product. The application is both the data source and the display layer. Claude is the reasoning engine.

Examples:
- Preventative timeline analysis — activities behind schedule, gap calculation, cascade impact, mitigation options
- Response quality monitoring — identifying responses below hurdle marks, missing win themes, weak credentials (future AI layer)
- PWIN recalibration based on changed competitive landscape or new intelligence
- Compliance gap detection before gate reviews
- Resource conflict detection across activities

**Role 2 — Data-Driven Output Generation**
The bid manager's live data drives AI-authored deliverables that would otherwise require manual effort.

Examples:
- Weekly stakeholder update reports
- Gate review packs (with entry criteria status pulled from live data)
- Pipeline health briefings for pursuit directors
- PWIN portfolio summaries for leadership
- Lessons learned reports post-submission

**Role 3 — Data Extraction and Ingestion Bridge**
Claude reads external content and transforms it into structured records consumable by the application.

Examples:
- Parse ITT document → extract requirements → create ResponseItem records in Submissions
- Parse ITT evaluation criteria → create ClientScoringScheme with GradeBands
- Parse compliance matrix → create ComplianceRequirement records
- Ingest client strategy document → populate Client Profile fields
- Read competitor award notice → update Competitor Dossier
- Process clarification Q&A → flag impacted ResponseItems and ComplianceRequirements

> **KEY DISTINCTION:** Role 1 reads application data and writes AI insight back. Role 3 reads external data and writes structured records into the application. Both write directions are different and must be handled separately in the MCP tool schema.

### 4.2 One Plugin — Not Multiple

**Decision: one plugin with persona-routed sub-agents.**

Rationale:
- A bid manager mid-pursuit does not think in workstream silos — they need win themes, timeline analysis, and competitive intelligence in the same session
- Shared context (pursuit record, rules, bid library) would be duplicated and drift across multiple plugins
- Sub-agents inside a single plugin provide specialisation without fragmentation
- Client distribution on Team/Enterprise is one plugin install, not seven

### 4.3 Plugin Folder Structure

```
pwin-architect-plugin/
│
├── .claude-plugin/
│   └── plugin.json                    — single manifest
│
├── .mcp.json                          — all connectors declared here
│
├── skills/                            — shared methodology, fires automatically
│   ├── bid-qualification/
│   │   └── SKILL.md
│   ├── pipeline-management/
│   │   └── SKILL.md
│   ├── gate-governance/
│   │   └── SKILL.md
│   ├── win-themes/
│   │   └── SKILL.md
│   ├── competitive-intelligence/
│   │   └── SKILL.md
│   ├── timeline-analysis/             — PRIMARY SKILL — build first
│   │   └── SKILL.md
│   ├── response-quality/              — NEW: quality dimension analysis
│   │   └── SKILL.md
│   └── clarification-qa/
│       └── SKILL.md
│
├── agents/                            — persona-specific sub-agents
│   ├── bid-manager-agent/
│   │   └── AGENT.md                  — activity health, timeline, stakeholder comms
│   ├── pursuit-director-agent/
│   │   └── AGENT.md                  — pipeline view, gate decisions, PWIN portfolio
│   ├── proposal-author-agent/
│   │   └── AGENT.md                  — response quality, storyboard, compliance, drafting
│   ├── commercial-agent/
│   │   └── AGENT.md                  — pricing, P2W, BAFO strategy
│   └── stakeholder-agent/
│       └── AGENT.md                  — reports, exec briefings, gate packs
│
├── reference/                         — static intelligence (ingested via Role 3)
│   ├── bid-library/
│   ├── competitor-dossiers/
│   ├── client-profiles/
│   └── framework-guides/
│
└── commands/                          — explicit slash commands
    ├── timeline-review.md             — /pwin:timeline-review — BUILD FIRST
    ├── pursuit-health.md              — /pwin:pursuit-health
    ├── stakeholder-update.md          — /pwin:stakeholder-update
    ├── gate-pack.md                   — /pwin:gate-pack
    ├── ingest-requirements.md         — /pwin:ingest-requirements (Role 3)
    ├── response-quality-check.md      — /pwin:response-quality (NEW)
    └── competitive-brief.md           — /pwin:competitive-brief
```

**Layer responsibilities:**

| Layer | Contains | How used |
|---|---|---|
| Skills | Shared bid methodology in Markdown | Fires automatically when Claude encounters relevant context |
| Agents | Persona-specific reasoning and workflow | Activated by user role or explicit command |
| Reference | Static intelligence documents | Claude draws on during analysis without prompting |
| Commands | Slash command trigger definitions | User-invoked, launch with structured input forms |

---

## 5. MCP Server Design

### 5.1 What It Is

A lightweight Node.js process (~200-300 lines) running locally alongside the application. Exposes the application's data as typed tool functions over stdio. When moving to SaaS, the server moves to a hosted API endpoint — **the tool schemas do not change**.

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

**Submissions & Production:**
```
get_response_items(bidId, filters?)
  → ResponseItems with production status, quality dimensions, word counts
  → Filters: status, responseType, owner, evaluationWeightPct threshold
  → IMPORTANT: use filters for targeted analysis, not full list

get_response_item(bidId, reference)
  → Full ResponseItem record with all quality dimension fields

get_production_pipeline(bidId)
  → Summary counts at each of the 10 production stages
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

**Supporting:**
```
get_risks(bidId)
  → Open RiskAssumptions in both registers (delivery + bid)

get_stakeholders(bidId)
  → All stakeholder records with type and linked gates

get_team_summary(bidId)
  → TeamMembers with workstream assignments, availability, spend forecast

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

**Ingestion (Role 3):**
```
ingest_response_item(bidId, item: ResponseItemInput)
  → Creates new ResponseItem from parsed ITT document
  → Used by /pwin:ingest-requirements command

ingest_compliance_requirement(bidId, requirement: ComplianceRequirementInput)
  → Creates ComplianceRequirement from parsed compliance matrix

ingest_scoring_scheme(bidId, scheme: ClientScoringSchemeInput)
  → Creates or updates ClientScoringScheme with GradeBands from parsed ITT

ingest_stakeholder(bidId, stakeholder: StakeholderInput)
  → Creates Stakeholder record from parsed document

generate_report_output(bidId, type: string, content: string)
  → Stores AI-generated report with reference link in bid record
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
  total_response_items:     integer
  pipeline_distribution:    Object                   — counts at each of the 10 stages
  quality_coverage_pct:     number                   — % of items with quality dimensions assessed
  below_hurdle_count:       integer                  — items predicted below hurdle mark
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

### 6.4 The Ownership Boundary

**Claude never writes to bid manager-owned fields. This must be enforced at the MCP server API layer — not just as a convention.**

| Bid Manager Owns (Claude must never write) | Claude Owns (bid manager must never edit) |
|---|---|
| Activity: owner, status, plannedStart/End, actualStart/End, notes, dependencies[], outputAssurance | AIInsight: rag_status, gap_working_days, cascade_risk, downstream_impact[], ai_narrative, mitigation_options[], rule_violations[], confidence |
| ResponseItem: status (10-stage), all quality dimension fields, owner, dueDate, notes | ResponseItemAIInsight: all fields (future) |
| ComplianceRequirement: complianceStatus, complianceExplanation, solutionAlignment | — |
| ReviewAction: status, resolutionNotes (these are reviewer-owned, also not AI-writable) | — |
| GovernanceGate: decision, conditions, riskPremiumPct | GateRecommendation (AI advisory) |
| WinTheme: statement, rationale, status | — |

> **KEY PRINCIPLE:** Quality dimensions on ResponseItem are bid manager-owned in the base product. When the AI quality monitoring layer is built, AI writes to ResponseItemAIInsight (a separate entity) — it never overwrites the bid manager's manual assessment. The two assessments coexist, enabling comparison.

### 6.5 Append-Only Rule

AIInsight records are append-only. Each analysis run creates a new record. Previous records are never updated or deleted. This preserves a full audit trail and enables trend analysis over time (is the bid getting healthier or worse?).

---

## 7. The Timeline Analysis Use Case

This is the primary in-application intelligence use case and the first to build.

**What it does:** Claude reads all activity data for an active bid, applies the embedded rules and dependency graph, identifies activities that are behind schedule or at risk of slipping, calculates gap and cascade impact, and writes structured AIInsight records back into the application. The user sees AI analysis as native application content — not a chat response.

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

**Context window constraint:** For a bid with 79 activities, Claude must never load all records simultaneously. The MCP server must expose filtered queries. The timeline analysis skill must use `get_activities_due_within()` and `get_critical_path()` rather than loading everything.

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

### 9.1 Phasing — Plugin Comes After Core Modules

The plugin architecture is a forward-looking design document. The immediate build priority is completing the core Bid Execution modules:

**Phase 1 (current):** Complete core modules — Submissions (10-stage lifecycle, quality dimensions, win themes, client scoring), Reviews (dual scorecard), Governance (development reviews absorbed), Workspace, Activity Tracker deepening, Readiness Dashboard.

**Phase 2 (after core):** Data visualisation pass — how each module's data is presented, dashboard design, cross-module views.

**Phase 3 (after visualisation):** Plugin implementation — AIInsight entities, MCP server, timeline analysis skill, write-back capability.

### 9.2 Plugin Build Sequence — When the Time Comes

1. **Formalise AIInsight entities** — add ActivityAIInsight, ResponseItemAIInsight (placeholder), and BidAIInsight to the Architecture v6 data model.

2. **Write the MCP tool schema document** — derive all read and write tools from Architecture v6 entities (Sections 5.2 and 5.3 above) as a standalone reference file.

3. **Implement MCP server — read tools first** — Node.js stdio process. Validate that Claude can retrieve activity and response item data correctly before adding write tools.

4. **Add write tools with boundary enforcement** — the MCP server must reject any write to a bid manager-owned field at the API layer.

5. **Build the timeline-analysis SKILL.md** — the primary intelligence skill. Encodes the six-layer analysis described in Section 7.

6. **Implement `/pwin:timeline-review` command** — validate the full end-to-end loop: command triggers → MCP reads → Claude analyses → MCP writes AIInsight → application renders.

### 9.3 Design Constraints — Non-Negotiable

- **One plugin, not multiple.** Sub-agents provide persona specialisation inside the single plugin.
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
- Full plugin manifest with all five agents — timeline-analysis skill and bid-manager-agent are the build priority; other agents follow

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

*PWIN Architect — AI Plugin Architecture Brief | v1.1 | March 2026 | BIP Management Consulting | Confidential*
*Aligned with Architecture v6, Session 7 (2026-03-26)*
