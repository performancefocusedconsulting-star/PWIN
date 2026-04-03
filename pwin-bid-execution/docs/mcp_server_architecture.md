# PWIN Platform — MCP Server Architecture

**Version:** 1.0 | April 2026
**Status:** Design specification — authoritative input for MCP server implementation
**Parent document:** `pwin_architect_plugin_architecture.md` (v1.5)
**Data model authority:** `bid_execution_architecture_v6.html`
**Agent specifications:** `agent_1_document_intelligence.md` through `agent_6_solution_delivery.md`
**Cross-product context:** Session 15 — multi-product platform architecture

---

## 1. Architecture Overview

### 1.1 What It Is

A single Node.js process running locally that serves two interfaces:

1. **Data API (HTTP, localhost:3456)** — serves each HTML product app with load/save endpoints for their data. Replaces localStorage as the persistence layer.
2. **MCP Server (stdio)** — exposes the platform's data as typed tool functions for Claude. Read tools for analysis, write tools for AI write-back, field-level permission enforcement.

Both interfaces read and write the same JSON file store. When the bid manager saves data in the HTML app, Claude can read it via MCP. When Claude writes an AIInsight record via MCP, the HTML app sees it on next load.

### 1.2 Why One Server, Not Multiple

- Three products (Qualify, Win Strategy, Bid Execution) share pursuit-level data
- Shared entities (PWIN score, win themes, buyer values, stakeholder map) must be accessible to all products and all agents
- One process to start, one port to configure, one data store to back up
- At SaaS transition, this single server becomes a hosted API — the tool schemas don't change

### 1.3 What It Is Not

- Not a database server. It reads and writes JSON files on disk.
- Not a web application server. It serves data APIs only — the HTML apps are opened as local files or served separately.
- Not an AI model host. Claude runs via the Anthropic API. The MCP server provides Claude with data access, not compute.

---

## 2. Data Store Layout

### 2.1 Directory Structure

```
~/.pwin/
├── server.json                          — server configuration (port, data path)
├── platform/
│   ├── sector_knowledge.json            — shared sector enrichment (from AI Enrichment Review)
│   ├── opportunity_types.json           — shared opportunity type intelligence
│   ├── sector_opp_matrix.json           — sector × opportunity type intersection intelligence
│   ├── reasoning_rules.json             — shared business rules (20 rules from Design Proforma)
│   └── confidence_model.json            — H/M/L/U rating definitions and completeness thresholds
│
├── pursuits/
│   └── {pursuitId}/
│       ├── shared.json                  — shared pursuit entities (see Section 2.2)
│       ├── qualify.json                 — PWIN Qualify product data
│       ├── bid_execution.json           — Bid Execution product data (24 entities, ~280 fields)
│       └── win_strategy.json            — Win Strategy product data (future)
│
├── reference/
│   ├── client_profiles/
│   │   └── {clientId}.json              — persistent client intelligence (Agent 2 recurring output)
│   ├── competitor_dossiers/
│   │   └── {competitorId}.json          — persistent competitor profiles (Agent 2 recurring output)
│   └── bid_library/
│       └── {bidId}.json                 — past bid assets, case studies, evidence blocks (future)
│
└── exports/                             — JSON export files (backward compatibility)
    └── {pursuitId}_{date}.json
```

### 2.2 Shared Pursuit Entities (`shared.json`)

These entities are created by one product and consumed by others. The `shared.json` file is the cross-product data bus.

```json
{
  "pursuit": {
    "id": "uuid",
    "client": "string",
    "opportunity": "string",
    "sector": "enum (Defence|Justice|Emergency Services|Central Government|Health|Local Government)",
    "tcv": "number",
    "acv": "number",
    "opportunityType": "enum (BPO|IT Outsourcing|Managed Service|Consulting/Advisory|Infrastructure|Software/SaaS|Digital Outcomes)",
    "procurementRoute": "enum (open|restricted|competitive_dialogue|negotiated|framework_call_off|direct_award)",
    "incumbentStatus": "enum (incumbent|challenger|none)",
    "submissionDeadline": "ISO date",
    "contractDurationMonths": "number",
    "status": "enum (qualifying|capture|itt_live|submitted|evaluation|awarded|lost|withdrawn)",
    "createdAt": "ISO datetime",
    "updatedAt": "ISO datetime",
    "createdBy": "enum (qualify|win_strategy|bid_execution)"
  },

  "pwinScore": {
    "overall": "number (0-100)",
    "categoryScores": {
      "competitivePositioning": "number (0-100)",
      "procurementIntelligence": "number (0-100)",
      "stakeholderStrength": "number (0-100)",
      "organisationalInfluence": "number (0-100)",
      "valueProposition": "number (0-100)",
      "pursuitProgress": "number (0-100)"
    },
    "weightProfile": "enum (default|services|technology|advisory)",
    "assessmentDate": "ISO datetime",
    "source": "enum (qualify|win_strategy|bid_execution)",
    "completionPct": "number (0-100)",
    "history": [
      { "overall": "number", "date": "ISO datetime", "source": "string" }
    ]
  },

  "winThemes": [
    {
      "id": "uuid",
      "statement": "string",
      "rationale": "string",
      "evidenceStatus": "enum (substantiated|partial|unsubstantiated)",
      "linkedCredentials": ["string"],
      "competitiveDifferentiation": "string",
      "buyerValueAlignment": "string",
      "status": "enum (draft|confirmed|revised|locked)",
      "sourceProduct": "enum (win_strategy|bid_execution)",
      "createdAt": "ISO datetime"
    }
  ],

  "competitivePositioning": {
    "competitors": [
      {
        "name": "string",
        "category": "enum (incumbent|contender|dark_horse|opportunist)",
        "strengths": ["string"],
        "weaknesses": ["string"],
        "likelyStrategy": "string",
        "counterStrategy": "string",
        "ghostThemes": ["string"],
        "pricePositioning": "string",
        "confidence": "enum (H|M|L|U)"
      }
    ],
    "competitiveIntensity": "enum (low|medium|high)",
    "incumbentVulnerability": "enum (low|medium|high)",
    "bipDifferentiator": "string",
    "updatedAt": "ISO datetime"
  },

  "stakeholderMap": [
    {
      "name": "string",
      "role": "string",
      "influenceLevel": "enum (decision_maker|influencer|evaluator|gatekeeper)",
      "disposition": "enum (champion|supportive|neutral|unsupportive|unknown)",
      "bipRelationshipOwner": "string",
      "lastContactDate": "ISO date",
      "notes": "string",
      "confidence": "enum (H|M|L|U)"
    }
  ],

  "buyerValues": [
    {
      "value": "string",
      "priority": "enum (primary|secondary|tertiary)",
      "evidence": "string",
      "linkedWinThemeIds": ["uuid"],
      "confidence": "enum (H|M|L|U)"
    }
  ],

  "clientIntelligence": {
    "strategicPriorities": ["string"],
    "knownPainPoints": ["string"],
    "procurementDriver": "string",
    "sroName": "string",
    "sroBackground": "string",
    "spendHistory": [
      { "supplier": "string", "value": "number", "date": "ISO date", "scope": "string" }
    ],
    "updatedAt": "ISO datetime",
    "confidence": "enum (H|M|L|U)"
  },

  "capturePlan": {
    "status": "enum (draft|locked|superseded)",
    "lockedAt": "ISO datetime",
    "lockedBy": "enum (win_strategy|bid_execution)",
    "strategyNarrative": "string",
    "consortiumStrategy": "string",
    "pricingStrategy": "string",
    "clarificationStrategy": "string"
  }
}
```

### 2.3 Product-Specific Data

**qualify.json** — stores the Qualify product's internal state:
- `positions`: question index → score string
- `evidence`: question index → evidence text
- `reviews`: question index → AI review result (verdict, suggestedScore, confidence, narrative, challengeQuestions, captureActions, inflationDetected)
- `context`: pursuit context fields (mirrored to shared.json on save)
- `completenessScore`: calculated completeness percentage

**bid_execution.json** — stores all 24 Bid Execution entities as defined in Architecture v6. This is the authoritative schema — see `bid_execution_architecture_v6.html` for field-level definitions.

**win_strategy.json** — future. Will store strategy session data, phase progression, interrogation transcripts.

### 2.4 Data Lifecycle

```
Qualify creates pursuit    Win Strategy enriches    Bid Execution at ITT
─────────────────────      ────────────────────     ────────────────────
shared.json created        shared.json updated      shared.json consumed
  pursuit entity             win themes locked        SAL activities import
  initial PWIN score         competitive strategy     from shared entities
  buyer value gaps           stakeholder map          
  competitive maturity       client intelligence      bid_execution.json created
                             capture plan locked        24 entities populated
qualify.json created                                   Agent 1 extracts ITT
  24 question scores       win_strategy.json created    adds ResponseSections
  evidence + reviews         session data               EvaluationFramework
```

---

## 3. Data API (HTTP)

### 3.1 Endpoints

The Data API serves the HTML product apps. It replaces localStorage with a server-backed persistence layer.

**Pursuit Management:**
```
GET    /api/pursuits                          → list all pursuits (id, client, opportunity, status, pwinScore)
POST   /api/pursuits                          → create new pursuit → returns pursuitId
GET    /api/pursuits/{pursuitId}              → get shared pursuit data (shared.json)
PUT    /api/pursuits/{pursuitId}              → update shared pursuit data
DELETE /api/pursuits/{pursuitId}              → archive pursuit (moves to exports/, does not delete)
```

**Product Data (per-product load/save):**
```
GET    /api/pursuits/{pursuitId}/qualify              → load qualify.json
PUT    /api/pursuits/{pursuitId}/qualify              → save qualify.json (also syncs context → shared.json)
GET    /api/pursuits/{pursuitId}/bid-execution        → load bid_execution.json
PUT    /api/pursuits/{pursuitId}/bid-execution        → save bid_execution.json
GET    /api/pursuits/{pursuitId}/win-strategy         → load win_strategy.json
PUT    /api/pursuits/{pursuitId}/win-strategy         → save win_strategy.json
```

**Shared Entities (cross-product read):**
```
GET    /api/pursuits/{pursuitId}/shared/pwin-score        → current PWIN score + history
GET    /api/pursuits/{pursuitId}/shared/win-themes        → locked win themes
GET    /api/pursuits/{pursuitId}/shared/stakeholders      → stakeholder map
GET    /api/pursuits/{pursuitId}/shared/competitors       → competitive positioning
GET    /api/pursuits/{pursuitId}/shared/buyer-values      → buyer values
GET    /api/pursuits/{pursuitId}/shared/client-intel       → client intelligence
GET    /api/pursuits/{pursuitId}/shared/capture-plan      → locked capture plan
```

**Reference Data:**
```
GET    /api/reference/client-profiles                    → list client profiles
GET    /api/reference/client-profiles/{clientId}         → single client profile
GET    /api/reference/competitor-dossiers                → list competitor dossiers
GET    /api/reference/competitor-dossiers/{competitorId} → single competitor dossier
GET    /api/reference/sector-knowledge/{sector}          → sector enrichment prompt block
GET    /api/reference/opportunity-types/{type}           → opportunity type prompt block
```

**Platform:**
```
GET    /api/platform/reasoning-rules                     → all 20 reasoning rules
GET    /api/platform/confidence-model                    → confidence rating definitions
GET    /api/health                                       → server health check (for HTML app connection detection)
```

**Import/Export (backward compatibility):**
```
POST   /api/pursuits/{pursuitId}/export                  → export pursuit to JSON file in exports/
POST   /api/pursuits/import                              → import pursuit from uploaded JSON file
```

### 3.2 Sync Rules

When a product saves data that overlaps with shared entities, the Data API must sync:

| Product saves... | Data API also writes to shared.json... |
|---|---|
| qualify.json with updated positions | Recalculates PWIN score, appends to score history |
| qualify.json with updated context | Updates pursuit entity (client, opportunity, sector, TCV, etc.) |
| win_strategy.json with locked win themes | Writes winThemes[] to shared.json |
| win_strategy.json with locked capture plan | Writes capturePlan to shared.json |
| bid_execution.json with SAL-04 win theme updates | Updates winThemes[] status in shared.json |
| bid_execution.json with SAL-10 stakeholder updates | Updates stakeholderMap in shared.json |

### 3.3 Cross-Origin Configuration

The HTML apps are opened as local files (`file://`) or served from a local dev server. The Data API must set CORS headers to allow requests from:
- `file://` (local file access)
- `http://localhost:*` (local development servers)
- The production domain (when deployed)

---

## 4. MCP Server — Read Tools

All existing read tools from `pwin_architect_plugin_architecture.md` Section 5.2 are retained unchanged. The `bidId` parameter is renamed to `pursuitId` for consistency across products. Tools are grouped by product scope.

### 4.1 Bid Execution Read Tools (existing — 30 tools)

These tools read from `bid_execution.json`. All existing filter specifications are retained.

**Activity & Timeline (6 tools):**
```
get_activities_due_within(pursuitId, days)
get_critical_path(pursuitId)
get_activities_by_workstream(pursuitId, workstreamCode)
get_activity(pursuitId, activityCode)
get_dependencies(pursuitId, activityCode)
get_workstream_summary(pursuitId)
```

**ITT Ingestion & Exam Paper (5 tools):**
```
get_response_sections(pursuitId, filters?)
  Filters: evaluationCategory, responseType, sectionNumber, hasLinkedResponseItem
get_response_section(pursuitId, reference)
get_evaluation_framework(pursuitId)
get_itt_documents(pursuitId, filters?)
  Filters: volumeType, parsedStatus
get_coverage_summary(pursuitId)
```

**Submissions & Production (7 tools):**
```
get_response_items(pursuitId, filters?)
  Filters: status, responseType, owner, evaluationWeightPct threshold
get_response_item(pursuitId, reference)
get_production_pipeline(pursuitId)
get_compliance_requirements(pursuitId, filters?)
  Filters: classification, complianceStatus, coverageStatus
get_win_themes(pursuitId)
get_client_scoring_scheme(pursuitId)
get_quality_gaps(pursuitId)
```

**Reviews (3 tools):**
```
get_review_cycles(pursuitId)
get_review_cycle_detail(reviewCycleId)
get_open_review_actions(pursuitId, severity?)
```

**Governance (2 tools):**
```
get_gate_status(pursuitId, gateName?)
get_gate_preparation(pursuitId, gateName)
```

**Standup & Actions (2 tools):**
```
get_standup_actions(pursuitId, filters?)
  Filters: status, owner, parentActivityCode, parentGateId, overdue_only
get_deferred_actions(pursuitId)
```

**Calendar, Commercial, Team (5 tools):**
```
get_bid_calendar(pursuitId)
get_engagement(pursuitId)
get_rate_card(pursuitId)
get_reviewer_history(pursuitId, reviewerName)
get_rules(pursuitId)
```

**Supporting (5 tools):**
```
get_risks(pursuitId, filters?)
  Filters: registerType, status, probability, impact
get_stakeholders(pursuitId)
get_team_summary(pursuitId)
get_team_member(pursuitId, memberName)
get_bid_library_match(query)                    [PLACEHOLDER]
```

> **NOTE:** `get_competitor_dossier(competitorName)` moves to Shared Read Tools (Section 4.3) — it reads from the reference data store, not from a single pursuit.

### 4.2 Qualify Read Tools (new — 6 tools)

These tools read from `qualify.json`.

```
get_qualification_assessment(pursuitId)
  → Full assessment: all 24 positions, evidence, AI reviews
  → Includes category scores, overall PWIN, completion percentage

get_qualification_by_category(pursuitId, categoryId)
  → Questions, positions, evidence, and AI reviews for one category
  → categoryId: cp|pi|ss|oi|vp|pp

get_qualification_context(pursuitId)
  → Pursuit context fields from Qualify product
  → Includes opportunity type, sector, TCV, incumbent status

get_qualification_gaps(pursuitId)
  → Questions scored Disagree or Strongly Disagree, plus unanswered questions
  → Pre-filtered for action — what needs work

get_qualification_ai_reviews(pursuitId, filters?)
  → AI review results across all questions
  → Filters: verdict (validated|queried|challenged), inflationDetected (boolean)

get_qualification_completeness(pursuitId)
  → Completeness score per section and overall
  → Minimum-to-proceed thresholds per section
  → Fields rated Unknown or Low confidence
```

### 4.3 Shared Read Tools (new — 10 tools)

These tools read from `shared.json` and the reference data store. Available to all agents across all products.

```
get_pursuit(pursuitId)
  → Shared pursuit entity: client, opportunity, sector, TCV, type, status, dates

get_pwin_score(pursuitId)
  → Current PWIN score with category breakdown and weight profile
  → Score history array for trend analysis

get_pwin_score_history(pursuitId)
  → Full PWIN score history: every assessment with date, source product, category scores
  → Used by Agent 3 for trajectory analysis

get_shared_win_themes(pursuitId)
  → Win themes from shared.json (locked by Win Strategy or refined by Bid Execution)
  → Distinct from bid_execution.get_win_themes() which reads the WinTheme entities in bid_execution.json

get_shared_stakeholder_map(pursuitId)
  → Stakeholder map from shared.json
  → Cross-product view — enriched by Qualify, Win Strategy, and Bid Execution

get_shared_competitive_positioning(pursuitId)
  → Competitors, intensity, incumbent vulnerability, differentiator from shared.json

get_shared_buyer_values(pursuitId)
  → Buyer values with priority, evidence, linked win themes from shared.json

get_shared_client_intelligence(pursuitId)
  → Client strategic priorities, pain points, SRO, spend history from shared.json

get_shared_capture_plan(pursuitId)
  → Locked capture plan from shared.json (if exists)

get_client_profile(clientId)
  → Persistent client intelligence from reference/client_profiles/
  → Maintained by Agent 2 on recurring schedule
  → [PLACEHOLDER — implement when Client Profiles product is built]

get_competitor_dossier(competitorName)
  → Pre-compiled competitor record from reference/competitor_dossiers/
  → Maintained by Agent 2 on recurring schedule
  → [PLACEHOLDER — implement when Competitor Dossiers product is built]
```

### 4.4 Platform Read Tools (new — 3 tools)

```
get_sector_knowledge(sector)
  → Sector enrichment prompt block from platform/sector_knowledge.json
  → Used by all agents for sector-calibrated analysis

get_opportunity_type_knowledge(opportunityType)
  → Opportunity type prompt block from platform/opportunity_types.json

get_reasoning_rules(category?)
  → Business rules from platform/reasoning_rules.json
  → Filters: category (winnability|desirability|deliverability|intelligence_quality|financials)
  → Used by Agent 3 for PWIN scoring and gate readiness
```

### 4.5 Read Tool Summary

| Scope | Tools | Source File |
|---|---|---|
| Bid Execution | 30 (existing, renamed bidId→pursuitId) | bid_execution.json |
| Qualify | 6 (new) | qualify.json |
| Shared | 10 (new, includes 2 placeholders) | shared.json + reference/ |
| Platform | 3 (new) | platform/ |
| **Total** | **49** | |

---

## 5. MCP Server — Write Tools

All existing write tools from `pwin_architect_plugin_architecture.md` Section 5.3 are retained unchanged. New shared and qualify write tools are added.

### 5.1 Bid Execution Write Tools (existing — 17 tools)

**Critical rule: write tools must only write to AI-owned fields. They must reject any attempt to modify bid manager-owned fields. See Section 7 for the field ownership map.**

**Activity-Level Insights (2 tools):**
```
update_activity_insight(pursuitId, activityCode, insight: ActivityAIInsight)
  → Appends new AIInsight record to activity — APPEND-ONLY
add_risk_flag(pursuitId, activityCode, risk)
  → Appends risk to activity and bid-level risk register
```

**Response-Level Insights (1 tool):**
```
update_response_insight(pursuitId, responseReference, insight: ResponseItemAIInsight)
  → APPEND-ONLY — [PLACEHOLDER — implement when AI quality monitoring is built]
```

**Bid-Level Insights (2 tools):**
```
update_bid_insight(pursuitId, insight: BidAIInsight)
  → Appends bid-level insight with PWIN recalibration — APPEND-ONLY
log_gate_recommendation(pursuitId, gateName, recommendation: GateRecommendation)
  → Writes AI gate readiness assessment
```

**Gate-Level Insights (1 tool):**
```
create_gate_readiness_report(pursuitId, gateId, report: GateReadinessAIInsight)
  → APPEND-ONLY — auto-generates StandupActions for amber criteria
```

**Compliance & Coverage Insights (3 tools):**
```
create_compliance_coverage_insight(pursuitId, insight: ComplianceCoverageAIInsight)
  → APPEND-ONLY
update_win_theme_coverage_score(pursuitId, responseSectionReference, score)
  → AI-owned field on ResponseSection
create_effort_allocation_insight(pursuitId, insight: EffortAllocationAIInsight)
  → APPEND-ONLY
```

**Standup & Action Generation (2 tools):**
```
create_standup_action(pursuitId, action: StandupActionInput)
  → Creates StandupAction with source: ai_generated
update_standup_action_deferred(pursuitId, actionId, data)
  → Writes AI-owned fields on existing StandupAction
```

**Response Section Amendment (1 tool):**
```
flag_response_section_amended(pursuitId, reference, reason)
  → Sets ResponseSection.lastAmended — AI-writable field
```

**Ingestion (5 tools):**
```
create_response_section(pursuitId, data: ResponseSectionInput)
batch_create_response_sections(pursuitId, data: ResponseSectionInput[])
create_itt_document(pursuitId, data: ITTDocumentInput)
create_evaluation_framework(pursuitId, data: EvaluationFrameworkInput)
update_bid_procurement_context(pursuitId, data: BidProcurementContextInput)
```

**Scoring & Reports (2 tools):**
```
ingest_scoring_scheme(pursuitId, scheme: ClientScoringSchemeInput)
generate_report_output(pursuitId, type, content)
```

> **NOTE:** V2 write tools (create_requirement, batch_create_requirements, link_requirement_to_response_section, create_clarification_item, flag_requirement_clarification_impact, ingest_compliance_requirement) are deferred — see plugin architecture Section 9.5.

### 5.2 Qualify Write Tools (new — 4 tools)

```
save_qualification_review(pursuitId, questionIdx, review: QualifyAIReview)
  → Writes AI assurance review result for one question
  → Fields: verdict, suggestedScore, confidenceLevel, narrative, inflationDetected,
    inflationReason, challengeQuestions[], captureActions[], sectorContext,
    opportunityRisk, incumbentRiskAssessment, evidenceGaps[], stageCalibration

batch_save_qualification_reviews(pursuitId, reviews: QualifyAIReview[])
  → Writes AI reviews for all 24 questions in a single pass
  → Used by the full AI Review tab (Tab 4)

update_qualification_pwin(pursuitId, scores: CategoryScores)
  → Recalculates and writes PWIN score to qualify.json AND shared.json
  → Appends to shared.json pwinScore.history

generate_qualification_report(pursuitId, content)
  → Generates and stores the full qualification report
  → The key output from the Qualify product
```

### 5.3 Shared Write Tools (new — 6 tools)

```
update_shared_win_themes(pursuitId, themes: WinTheme[])
  → Updates win themes in shared.json
  → Source product tagged automatically

update_shared_stakeholder_map(pursuitId, stakeholders: Stakeholder[])
  → Updates stakeholder map in shared.json

update_shared_competitive_positioning(pursuitId, positioning: CompetitivePositioning)
  → Updates competitive positioning in shared.json

update_shared_buyer_values(pursuitId, values: BuyerValue[])
  → Updates buyer values in shared.json

update_shared_client_intelligence(pursuitId, intel: ClientIntelligence)
  → Updates client intelligence in shared.json

lock_capture_plan(pursuitId, plan: CapturePlan)
  → Writes and locks capture plan in shared.json
  → Sets status: locked, lockedAt, lockedBy
  → Once locked, cannot be modified without explicit unlock (bid manager action)
```

### 5.4 Reference Write Tools (new — 2 tools)

```
update_client_profile(clientId, profile: ClientProfile)
  → Creates or updates client profile in reference/client_profiles/
  → Used by Agent 2 on recurring schedule
  → [PLACEHOLDER — implement when Client Profiles product is built]

update_competitor_dossier(competitorName, dossier: CompetitorDossier)
  → Creates or updates competitor dossier in reference/competitor_dossiers/
  → Used by Agent 2 on recurring schedule
  → [PLACEHOLDER — implement when Competitor Dossiers product is built]
```

### 5.5 Write Tool Summary

| Scope | Tools | Target File |
|---|---|---|
| Bid Execution | 17 (existing, renamed bidId→pursuitId) + 2 V2 deferred | bid_execution.json |
| Qualify | 4 (new) | qualify.json + shared.json |
| Shared | 6 (new) | shared.json |
| Reference | 2 (new, placeholders) | reference/ |
| **Total** | **29** | |

---

## 6. Query Contracts

### 6.1 Filtering — Server-Side Only

All filters are applied server-side. The MCP server returns only matching records. Claude never receives data it didn't ask for. This reduces token usage and prevents reasoning over irrelevant data.

### 6.2 Context Window Budget

For a typical complex bid (84 activities, 30-40 response sections, 6 governance gates), estimated token budgets per tool call:

| Tool | Estimated Tokens | Constraint |
|---|---|---|
| get_activities_due_within(pursuitId, 14) | ~2,000-3,000 | 10-15 activities typically due within 14 days |
| get_response_sections(pursuitId) — unfiltered | ~4,000-6,000 | 30-40 sections × ~120 tokens each |
| get_response_sections(pursuitId, {evaluationCategory: "quality"}) | ~2,000-3,000 | Filtered to quality sections only |
| get_critical_path(pursuitId) | ~1,500-2,500 | Critical path is typically 15-20 activities |
| get_qualification_assessment(pursuitId) | ~3,000-5,000 | 24 questions × ~150 tokens each |
| get_pursuit(pursuitId) | ~300-500 | Single entity, small payload |

**Design rule:** No single tool call should return more than ~8,000 tokens. If a query would exceed this, the tool must require filters or return a summary with a drill-down tool for detail.

### 6.3 Pagination

For tools that could return large result sets (activities, response sections, compliance requirements), pagination is available but not mandatory:

```
get_response_sections(pursuitId, { limit: 10, offset: 0 })
```

Default behaviour: return all matching records (no pagination). Pagination is available as an escape valve, not the default pattern.

---

## 7. Field-Level Permission Enforcement

### 7.1 The Rule

**Claude never writes to bid manager-owned fields. This is enforced at the MCP server API layer — not as a prompt convention.**

Every write tool validates the incoming payload against the field ownership map before writing. If a write attempt includes a bid manager-owned field, the server returns an error with the field name and owner.

### 7.2 Ownership Map

The complete field ownership map is defined in `pwin_architect_plugin_architecture.md` Section 6.8. The MCP server loads this map at startup and validates every write against it.

**Implementation pattern:**

```javascript
const OWNERSHIP = {
  // Activity entity
  'Activity.owner':           'bid_manager',
  'Activity.status':          'bid_manager',
  'Activity.plannedStart':    'bid_manager',
  'Activity.plannedEnd':      'bid_manager',
  'Activity.actualStart':     'bid_manager',
  'Activity.actualEnd':       'bid_manager',
  'Activity.notes':           'bid_manager',
  'Activity.dependencies':    'bid_manager',
  'Activity.outputAssurance': 'bid_manager',
  'Activity.forecastEnd':     'ai',          // AI-owned, separate from plannedEnd

  // ActivityAIInsight — entirely AI-owned
  'ActivityAIInsight.*':      'ai',

  // ResponseItem entity
  'ResponseItem.status':                    'bid_manager',
  'ResponseItem.qualityAnswersQuestion':    'bid_manager',
  'ResponseItem.qualityFollowsStructure':   'bid_manager',
  'ResponseItem.qualityScoreSelfAssessment':'bid_manager',
  'ResponseItem.qualityScoreRationale':     'bid_manager',
  'ResponseItem.qualityScoreGap':           'bid_manager',
  'ResponseItem.qualityCredentials':        'bid_manager',
  'ResponseItem.qualityCredentialsRefs':    'bid_manager',
  'ResponseItem.qualityWinThemeAssessments':'bid_manager',
  'ResponseItem.qualityComplianceMapping':  'bid_manager',
  'ResponseItem.owner':                     'bid_manager',
  'ResponseItem.dueDate':                   'bid_manager',
  'ResponseItem.notes':                     'bid_manager',
  'ResponseItem.effortAllocationEfficiency':'ai',           // UC6

  // ResponseItemAIInsight — entirely AI-owned
  'ResponseItemAIInsight.*': 'ai',

  // ResponseSection entity
  'ResponseSection.questionText':           'bid_manager',
  'ResponseSection.evaluationCriteria':     'bid_manager',
  'ResponseSection.evaluationMaxScore':     'bid_manager',
  'ResponseSection.hurdleScore':            'bid_manager',
  'ResponseSection.wordLimit':              'bid_manager',
  'ResponseSection.winThemeCoverageScore':  'ai',           // UC5
  'ResponseSection.lastAmended':            'ai',           // UC13, UC14

  // Ingested entities — AI creates, bid manager can edit after
  'ResponseSection.createdBy':              'system',       // manual|csv_import|ai_ingestion
  'EvaluationFramework.*':                  'ai_ingestion', // created by AI, editable by BM after
  'ITTDocument.*':                          'ai_ingestion',

  // GovernanceGate entity
  'GovernanceGate.decision':                'bid_manager',
  'GovernanceGate.conditions':              'bid_manager',
  'GovernanceGate.riskPremiumPct':          'bid_manager',
  'GateReadinessAIInsight.*':               'ai',

  // WinTheme entity
  'WinTheme.statement':                     'bid_manager',
  'WinTheme.rationale':                     'bid_manager',
  'WinTheme.status':                        'bid_manager',
  'WinTheme.portfolioSaturationRating':     'ai',           // UC5

  // StandupAction entity
  'StandupAction.owner':                    'bid_manager',  // for existing actions
  'StandupAction.dueDate':                  'bid_manager',
  'StandupAction.status':                   'bid_manager',
  'StandupAction.deferred_count':           'ai',           // UC3, UC18
  'StandupAction.escalation_recommended':   'ai',
  'StandupAction.recommended_decision':     'ai',

  // ComplianceRequirement entity
  'ComplianceRequirement.complianceStatus':      'bid_manager',
  'ComplianceRequirement.complianceExplanation': 'bid_manager',
  'ComplianceRequirement.solutionAlignment':     'bid_manager',
  'ComplianceRequirement.impactedByClarification':'ai',      // UC13

  // Engagement, TeamMember — entirely bid manager
  'Engagement.*':                           'bid_manager',
  'TeamMember.*':                           'bid_manager',

  // AI insight entities — entirely AI-owned
  'BidAIInsight.*':                         'ai',
  'ComplianceCoverageAIInsight.*':          'ai',
  'EffortAllocationAIInsight.*':            'ai',
  'TeamMemberAIInsight.*':                  'ai',
};
```

### 7.3 Validation Logic

```javascript
function validateWrite(entity, fields, caller) {
  if (caller !== 'ai') return; // only enforce for AI writes

  for (const field of Object.keys(fields)) {
    const key = `${entity}.${field}`;
    const wildcardKey = `${entity}.*`;

    const owner = OWNERSHIP[key] || OWNERSHIP[wildcardKey];

    if (owner === 'bid_manager') {
      throw new MCPError(
        `PERMISSION_DENIED: AI cannot write to ${key} (owned by bid_manager)`
      );
    }
  }
}
```

### 7.4 Append-Only Enforcement

All AIInsight entities are append-only. The MCP server must:
- Reject any `UPDATE` or `DELETE` operation on AIInsight records
- Assign a new UUID and `generated_at` timestamp to every new record
- Preserve the full history for trend analysis

---

## 8. Confidence Model (Platform-Wide)

Adopted from the Qualify AI Design Proforma. Applied to all shared entities and agent outputs.

### 8.1 Confidence Ratings

| Rating | Label | Definition | Display |
|---|---|---|---|
| **H** | Confirmed | Data taken from a named source document or confirmed directly by the user with a specific reference | Green |
| **M** | Inferred | Data reasonably inferred from available context. AI has moderate confidence but source is not direct | Amber |
| **L** | Assumed | Data not available from any source. AI has made an assumption based on general knowledge | Red |
| **U** | Unknown | Data point could not be populated. Explicitly unknown. | Dark Red |

### 8.2 Application

Every data point in shared entities includes a `confidence` field (H|M|L|U). Agents must:
- Set confidence when writing shared data
- Flag data rated L or U as requiring human verification
- Not present inferred data as confirmed fact (SF-06 from Design Proforma)
- Include source reference for H-rated data points

---

## 9. Graceful Degradation

### 9.1 When the Server Is Not Running

Each HTML app should detect the server connection on load:

```javascript
async function checkPlatformServer() {
  try {
    const response = await fetch('http://localhost:3456/api/health', { timeout: 2000 });
    if (response.ok) return 'connected';
  } catch (e) {
    return 'disconnected';
  }
}
```

**When disconnected:**
- App loads from its last-saved local state (kept in localStorage as a cache)
- Banner displayed: "PWIN Platform Server not connected — AI features unavailable. Data is read-only."
- All edit controls remain functional but saves go to localStorage only
- When server reconnects, app syncs localStorage cache to server (server state wins on conflict)

### 9.2 When the Server Has No Data for This Pursuit

- App creates a new pursuit via `POST /api/pursuits`
- If migrating from localStorage, app sends full state via `PUT /api/pursuits/{id}/{product}`
- One-time migration, then localStorage becomes cache only

---

## 10. SaaS Migration Path

| Component | Local (current) | SaaS (future) |
|---|---|---|
| Data store | JSON files on disk | Supabase (Postgres) |
| Data API | localhost:3456 HTTP | Hosted API (Azure Function or Supabase Edge Function) |
| MCP transport | stdio (local process) | HTTP (hosted endpoint) |
| Authentication | None — single user | OAuth + Row Level Security |
| Multi-tenancy | Single user, local files | Supabase RLS per organisation |
| File store | `~/.pwin/` directory | Supabase Storage or Azure Blob |

**What does NOT change:**
- MCP tool names and schemas
- Field ownership map
- AIInsight append-only pattern
- Agent configurations and skill definitions
- Shared entity schema
- Query filter specifications

> **THE KEY PRINCIPLE:** Every tool schema, field name, and entity structure defined in this document becomes a database column, API endpoint, or RLS policy at SaaS transition. Name things accordingly. Design for the permanent state, not the temporary implementation.

---

## 11. Implementation Priority

### 11.1 Build Sequence

| Step | What | Dependencies | Validates |
|---|---|---|---|
| 1 | Server skeleton — HTTP listener + stdio MCP | Node.js | Server starts, health check responds |
| 2 | File store — read/write JSON files for one pursuit | Step 1 | Data persists across server restarts |
| 3 | Bid Execution Data API — load/save endpoints | Step 2 | HTML app can load/save via fetch instead of localStorage |
| 4 | Bid Execution read tools — first 10 (activities, response sections, evaluation framework) | Step 2 | Claude can read bid data |
| 5 | Bid Execution write tools — AIInsight + ingestion tools | Step 4 + field ownership map | Claude can write insights and ingest ITT data |
| 6 | Field-level permission enforcement | Step 5 | Write to bid_manager field is rejected |
| 7 | Agent 1 Skill 1 (ITT Extraction) end-to-end | Steps 3-6 | Full loop: upload → extract → MCP write → app displays |
| 8 | Agent 3 Skill 5 (Timeline Analysis UC1) end-to-end | Steps 4-6 | Full loop: command → MCP read → analyse → MCP write AIInsight → app displays |
| 9 | Shared entity tools — pursuit, PWIN score | Step 2 | Cross-product data accessible |
| 10 | Qualify Data API + read/write tools | Step 9 | Qualify app connects to server |
| 11 | Platform knowledge tools — sector, opportunity type, reasoning rules | Step 2 | Sector-calibrated agent analysis |
| 12 | Remaining Bid Execution read/write tools (full 47) | Step 4 | All 55 skills have data access |
| 13 | Reference data tools — client profiles, competitor dossiers | Step 2 | Agent 2 recurring intelligence |

### 11.2 Estimated Size

The MCP server is a lightweight Node.js application. Estimated lines of code:

| Component | Lines |
|---|---|
| Server skeleton + HTTP listener | ~100 |
| File store (read/write JSON) | ~150 |
| Data API routes (all products) | ~200 |
| MCP tool handlers (49 read + 29 write) | ~1,500 |
| Field ownership map + validation | ~200 |
| Shared entity sync logic | ~150 |
| **Total** | **~2,300** |

This is a single-file server or a small module with 3-4 files. Not a large application.

---

*PWIN Platform — MCP Server Architecture | v1.0 | April 2026 | BIP Management Consulting | Confidential*
*Serves: PWIN Qualify, Win Strategy, Bid Execution | 49 read tools, 29 write tools | JSON file store → Supabase migration path*
