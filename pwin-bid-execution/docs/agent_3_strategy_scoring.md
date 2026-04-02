# Agent 3: Strategy & Scoring Analyst

**Version:** 1.0 | April 2026
**Status:** Design specification — authoritative input for skill implementation
**Parent document:** `pwin_architect_plugin_architecture.md` (v1.5, Section 4.2c)
**Data model authority:** `bid_execution_architecture_v6.html`
**Insight skill specs:** `ai_use_cases_reference.html` (v1.1, UC1-7, UC9, UC12)

---

## 1. Agent Identity

**Purpose:** Analyses evaluation frameworks, marks concentration, win theme coverage, scoring strategy, and PWIN scoring. Also owns the largest set of insight skills (UC1-7, UC9, UC12) that reason over the activity spine, response quality, and governance data. The "how do we win" and "are we on track" reasoning engine.

**System prompt essence:** "You are a bid strategy and scoring analyst. You reason over evaluation frameworks, marks concentration, win theme coverage, and competitive positioning to maximise the probability of winning. You also monitor bid health — timeline, compliance, gate readiness, and production quality — surfacing risks and recommending mitigations. You think in terms of marks, scores, hurdle requirements, and disqualification risk."

**Operating principles:**
- Every recommendation must be grounded in the evaluation framework — marks available, scoring criteria, hurdle requirements.
- Distinguish between score improvement (more marks) and risk avoidance (don't get disqualified).
- Hurdle sections override return-on-effort calculations — below-hurdle is disqualification regardless of marks.
- When writing AIInsight records, be specific and actionable — "SOL-04 is 3 working days behind" not "timeline concerns exist."

---

## 2. Agent Configuration

**Tools available:**

| Tool | Purpose |
|---|---|
| `get_activities` | Read activity spine (dates, status, dependencies) |
| `get_response_sections` | Read exam paper (questions, weights, hurdles) |
| `get_evaluation_framework` | Read scoring methodology and grade bands |
| `get_win_themes` | Read win theme register |
| `get_compliance_requirements` | Read compliance matrix |
| `get_reviews` | Read review scorecards across cycles |
| `get_governance_gates` | Read gate definitions and entry criteria |
| `get_standup_actions` | Read standup action register |
| `get_calendar` | Read bid calendar and key dates |
| `get_engagement_data` | Read stakeholder engagement records |
| `get_team` | Read team assignments and availability |
| `get_stakeholders` | Read stakeholder register |
| `get_risks` | Read risk register |
| `update_activity_insight` | Write AI insight against an activity |
| `add_risk_flag` | Write new risk flag to risk register |
| `update_bid_insight` | Write bid-level AI insight |
| `log_gate_recommendation` | Write gate readiness recommendation |
| `create_gate_readiness_report` | Write structured gate readiness assessment |
| `create_compliance_coverage_insight` | Write compliance coverage analysis |
| `update_win_theme_coverage_score` | Write win theme saturation score per section |
| `create_effort_allocation_insight` | Write marks-per-effort optimisation data |
| `create_standup_action` | Generate actions from insight analysis |
| `update_standup_action_deferred` | Flag deferred standup actions with carry-forward |
| `generate_report_output` | Store narrative strategy documents |

**Tools NOT available (by design):**
- Web search (that's Agent 2)
- PDF/Word document reader for uploaded files (that's Agent 1)
- Spreadsheet/calculation tools (that's Agent 4)

**Knowledge scope:**
- All bid execution app data via MCP read tools (the full live state of the bid)
- Evaluation framework and scoring methodology (extracted by Agent 1)
- Win themes and competitive positioning (from capture phase and Agent 2 intelligence)
- UK public procurement scoring conventions (MEAT methodology, quality/price weighting, hurdle mark patterns, grade band descriptors)

---

## 3. Skills

Agent 3 owns 15 skills: 4 productivity skills and 11 insight skills. This is the LARGEST agent by skill count.

### 3.1 Productivity Skills

---

#### Skill 1: Win Theme Refinement (`win-theme-mapping`)

**Priority:** BUILD FIRST among productivity skills — win themes are foundational to scoring strategy.
**Command:** `/pwin:win-themes`
**Trigger:** Human-invoked. Run when win themes arrive from capture phase (pre-ITT) or need refinement against ITT documentation.
**Methodology activities:** SAL-04.1.1-4, SAL-04.2.1-2

**What it does:**

Imports or develops win themes, tests them against buyer values and competitive positioning, checks evidence backing, refines them against ITT documentation, and develops messaging per theme. Produces a complete win theme register with strategic alignment data.

**Process:**

```
Step 1: Win theme import or development
  - If themes exist from capture phase: import via get_win_themes() or manual input
  - If no themes exist: derive from ITT evaluation criteria, buyer priorities,
    and competitive positioning (requires Agent 2 input for competitive context)
  - Each theme: name, description, evidence status, competitive differentiation claim

Step 2: Buyer value alignment (SAL-04.1.1-2)
  - Read EvaluationFramework and ResponseSections via MCP
  - Map each win theme to the buyer values expressed in evaluation criteria
  - Score alignment: strong (directly addresses stated criterion),
    moderate (indirectly relevant), weak (tenuous link)
  - Flag themes with no buyer value alignment — these are "nice to say" not "need to say"

Step 3: Competitive differentiation test (SAL-04.1.3)
  - For each theme, assess: does this differentiate us from likely competitors?
  - Classify: unique differentiator, shared strength (competitors have this too),
    table stakes (everyone must claim this)
  - Flag table-stakes themes — they need reframing as differentiators or deprioritising

Step 4: Evidence backing check (SAL-04.1.4)
  - For each theme, identify required evidence: case studies, metrics, testimonials,
    certifications, team CVs, methodology artefacts
  - Status per evidence item: available, in progress, not available, not applicable
  - Flag themes with no available evidence — a theme without evidence is a claim, not a win theme

Step 5: ITT refinement (SAL-04.2.1)
  - Cross-reference themes against ITT response sections
  - Identify where each theme can be landed (which questions, which sub-parts)
  - Refine theme messaging to use the client's language from the ITT

Step 6: Messaging development (SAL-04.2.2)
  - For each theme, develop:
    - Headline message (one sentence)
    - Supporting narrative (2-3 sentences)
    - Evidence proof point
    - Section-specific variant messaging (how the theme is expressed in each section)
```

**Output template:**

```
Win Theme Register
==================
Total themes:               [count]
  Strong differentiators:   [count]
  Shared strengths:         [count]
  Table stakes:             [count]

THEME DETAIL
  Theme: [name]
  Headline: [one sentence]
  Buyer value alignment:    [strong/moderate/weak] — [specific criterion]
  Competitive position:     [unique/shared/table stakes]
  Evidence status:          [x/y items available]
  Sections for deployment:  [list of section refs]
  Messaging: [section-specific variant text]

EVIDENCE GAPS
  [themes with missing or incomplete evidence]

STRATEGIC GAPS
  [high-value sections with no theme coverage]

RECOMMENDATIONS
  [specific actions to strengthen weak themes or fill gaps]
```

**Quality criteria:**
- Every theme must have at least one buyer value alignment — themes without alignment to evaluation criteria are deprioritised.
- Evidence status must be honest — "available" means the evidence exists and can be cited, not that it could theoretically be obtained.
- Table-stakes themes must be flagged and either reframed or deprioritised — they don't win marks.
- Section mapping must cover all high-value sections (top 20% by marks).

**Practitioner design note:**
> "Win themes originate pre-ITT from the sales lead, refined at ITT receipt, not created from scratch. AI comes up with a draft for the individual to test and challenge."

---

#### Skill 2: PWIN Scoring (`pwin-scoring`)

**Command:** `/pwin:pwin-score`
**Trigger:** Human-invoked. Run at bid/no-bid decision point (SAL-06) and periodically during bid production to track trajectory.
**Methodology activities:** SAL-06.2.1, SAL-06.2.2, SAL-06.2.3

**What it does:**

Completes the Deal Qualification Checklist, assesses strategic fit, and scores PWIN across all dimensions. Produces a scored assessment with dimension breakdown, rationale, and trend analysis.

**Process:**

```
Step 1: Deal Qualification Checklist (SAL-06.2.1)
  - Assess each qualification criterion:
    - Can we deliver the solution? (capability match)
    - Can we price competitively? (commercial viability)
    - Can we staff the bid team? (resource availability)
    - Can we meet the timeline? (production feasibility)
    - Do we have relevant past performance? (evidence base)
    - Is this strategically aligned? (portfolio fit)
    - Do we have the incumbent relationship context? (competitive position)
  - Each criterion: pass/fail/conditional with rationale

Step 2: PWIN dimension scoring (SAL-06.2.2)
  - Score each PWIN dimension on a 1-10 scale with rationale:
    - Competitive position: incumbency, relationships, track record with this client
    - Stakeholder relationships: buyer access, influencer mapping, sponsor strength
    - Solution strength: capability match, innovation, methodology maturity
    - Price competitiveness: market rate alignment, cost structure, value positioning
    - Team capability: named individuals, availability, relevant experience
    - Risk profile: delivery risk, contractual risk, reputational risk
  - Each score grounded in available evidence, not optimism

Step 3: Overall PWIN calculation (SAL-06.2.3)
  - Weighted average across dimensions (weights configurable per opportunity type)
  - Classify: Green (>70%), Amber (40-70%), Red (<40%)
  - If any dimension is 3 or below: flag as "single-dimension kill risk"

Step 4: Trend analysis (if previous scores exist)
  - Compare current scores against previous PWIN assessments
  - Identify dimensions trending up/down
  - Flag dimensions that have deteriorated since last assessment
```

**Output template:**

```
PWIN Assessment
===============
Date:                      [date]
Overall PWIN:              [score]% — [GREEN/AMBER/RED]
Deal Qualification:        [PASS/CONDITIONAL/FAIL]

DIMENSION SCORES
  Competitive position:    [x/10] — [one-line rationale]
  Stakeholder relationships: [x/10] — [one-line rationale]
  Solution strength:       [x/10] — [one-line rationale]
  Price competitiveness:   [x/10] — [one-line rationale]
  Team capability:         [x/10] — [one-line rationale]
  Risk profile:            [x/10] — [one-line rationale]

SINGLE-DIMENSION RISKS
  [any dimension at 3 or below — these can kill the bid regardless of overall score]

TREND (if previous assessments exist)
  [dimension-by-dimension comparison with direction arrows]
  [narrative on what has changed and why]

RECOMMENDATION
  [pursue/proceed with caution/recommend no-bid]
  [specific actions to improve weakest dimensions]
```

**Quality criteria:**
- Scores must be evidence-based, not aspirational. A 7/10 on solution strength requires demonstrable capability, not hope.
- The overall PWIN must weight dimensions appropriately — price competitiveness in a lowest-price evaluation is heavily weighted.
- Single-dimension kill risks must be prominently flagged — they override the aggregate score.
- Trend analysis must compare like-for-like — same dimensions, same scale.

---

#### Skill 3: Capture Plan Assembly (`capture-plan`)

**Command:** `/pwin:capture-plan`
**Trigger:** Human-invoked. Run at the conclusion of the capture/strategy phase (SAL-06.4) to lock down all strategy outputs into a formal document.
**Methodology activities:** SAL-06.4.1, SAL-06.4.2
**Depends on:** Skills 1 and 2 (win themes and PWIN score), plus Agent 2 outputs (competitive intelligence) and Agent 4 outputs (commercial positioning).

**What it does:**

Assembles all upstream strategy outputs into a locked Capture Plan document and prepares the Bid Mandate for board approval. This is a synthesis and document-generation skill — it reads from multiple data sources and produces two formal deliverables.

**Process:**

```
Step 1: Strategy data assembly
  - Read win themes via get_win_themes()
  - Read PWIN assessment via get_bid_insight() (latest PWIN scoring output)
  - Read evaluation framework via get_evaluation_framework()
  - Read competitive intelligence (from Agent 2 outputs stored as bid insights)
  - Read risk register via get_risks()
  - Read team assignments via get_team()
  - Read calendar via get_calendar() for key dates

Step 2: Capture Plan document generation (SAL-06.4.1)
  - Assemble into standard Capture Plan template:
    - Opportunity overview (client, contract, value, duration)
    - Evaluation methodology and marks landscape
    - Win themes with evidence status
    - Competitive positioning and differentiation strategy
    - Scoring strategy (where to invest effort for maximum marks)
    - PWIN assessment with dimension breakdown
    - Risk register with mitigations
    - Team structure and key personnel
    - Key dates and production timeline
    - Consortium/teaming strategy (if applicable)
  - Write via generate_report_output()

Step 3: Bid Mandate preparation (SAL-06.4.2)
  - Extract from Capture Plan the board-facing summary:
    - Opportunity value and strategic fit
    - PWIN score and key risks
    - Resource commitment required (team, cost, elapsed time)
    - Go/no-go recommendation with rationale
    - Approval conditions (if conditional)
  - Write via generate_report_output()
```

**Output template:**

```
CAPTURE PLAN
============
[Full structured document — see template in templates/capture-plan/]

Sections:
  1. Opportunity Overview
  2. Evaluation Methodology & Marks Landscape
  3. Win Strategy (themes, evidence, competitive positioning)
  4. Scoring Strategy (effort allocation by section value)
  5. PWIN Assessment
  6. Risk Register & Mitigations
  7. Team & Resource Plan
  8. Key Dates & Production Timeline
  9. Consortium/Teaming Strategy
  10. Appendices (detailed evaluation analysis, compliance matrix status)

---

BID MANDATE
===========
For: [approval board/governance body]
Recommendation: [bid/no-bid/bid with conditions]
PWIN: [score]%
Resource commitment: [person-days], [cost estimate]
Key risk: [single most important risk]
Approval conditions: [list if conditional]
```

**Quality criteria:**
- The Capture Plan must be internally consistent — win themes, scoring strategy, effort allocation, and PWIN score must tell the same story.
- The Bid Mandate must be decision-ready — a board member should be able to approve or reject based on this document alone.
- All data must be current — stale PWIN scores or outdated win themes undermine the document.
- Strategy outputs from other agents (Agent 2 competitive intelligence, Agent 4 commercial positioning) must be incorporated, not duplicated.

---

#### Skill 4: Competitive Clarification Strategy (`clarification-strategy`)

**Command:** `/pwin:clarification-strategy`
**Trigger:** Human-invoked. Run after win themes and competitive strategy are established, before the clarification window opens.
**Methodology activities:** SAL-07.1.3
**Depends on:** Skills 1 and 2, plus Agent 1 (ITT extraction for response sections) and Agent 2 (competitive intelligence).

**What it does:**

Develops a clarification strategy — which questions to ask, when, and how they serve competitive positioning. Clarification questions are not neutral information requests; they are strategic instruments that can shape the evaluation landscape.

**Process:**

```
Step 1: Clarification opportunity identification
  - Read ResponseSections via get_response_sections()
  - Read EvaluationFramework via get_evaluation_framework()
  - Read win themes via get_win_themes()
  - Identify areas of genuine ambiguity in the ITT that affect response strategy
  - Identify evaluation criteria where clarification could confirm our approach is aligned

Step 2: Competitive strategy overlay
  - For each potential clarification question, assess:
    - Does this question reveal our strategy to competitors? (risk)
    - Does this question shape the evaluation in our favour? (opportunity)
    - Does this question create advantage through timing? (first-mover)
    - Is this question likely to be asked by competitors anyway? (table stakes)
  - Classify: strategic (shapes evaluation), tactical (confirms approach),
    operational (logistics), defensive (protects compliance)

Step 3: Timing strategy
  - Map clarification windows from calendar
  - Sequence questions: operational first (low risk), strategic last (maximise timing advantage)
  - Identify questions that must be asked early (they affect solution design timeline)

Step 4: Prioritisation and drafting
  - Rank questions by strategic value × risk balance
  - Draft question text for each (neutral phrasing that doesn't reveal strategy)
  - Write competitive rationale per question (internal only — not submitted)
```

**Output template:**

```
Clarification Strategy
======================
Total clarification questions:  [count]
  Strategic:                   [count]
  Tactical:                    [count]
  Operational:                 [count]
  Defensive:                   [count]

PRIORITY QUESTIONS
  Priority 1: [question text]
    Category: [strategic/tactical/operational/defensive]
    Competitive rationale: [why this question serves our win strategy]
    Timing: [early/mid/late window]
    Risk assessment: [what this reveals about our approach]
    Linked sections: [response section refs affected]

  Priority 2: ...

TIMING PLAN
  Early window: [questions that must go first]
  Mid window: [questions that build on early answers]
  Late window: [strategic questions timed for maximum advantage]

DO NOT ASK
  [questions considered and rejected — with rationale for why they would harm our position]
```

**Quality criteria:**
- Every question must have a competitive rationale — "we don't understand" is not a strategy.
- Questions must be phrased neutrally — they must not reveal our solution approach or win themes.
- The "do not ask" list is as important as the priority list — it prevents accidental strategy leakage.
- Timing must respect the procurement calendar — questions submitted after the deadline are worthless.

**Practitioner design note:**
> "AI comes up with a draft strategy in terms of topics, areas to probe, timing, positioning, as a first draft for human-in-the-loop individuals to test and challenge."

---

### 3.2 Insight Skills

All insight skills below are defined in full in `ai_use_cases_reference.html`. This section provides the operational summary for each — what it reads, what it writes, and how it integrates with the bid execution app. Reference the use cases document for complete specifications including data schemas, trigger conditions, and edge cases.

---

#### Skill 5: Timeline Analysis (`timeline-analysis`) — UC1

**Priority:** BUILD FIRST — this is the PRIMARY insight skill for Agent 3 and the first insight skill built across the entire system (Phase 3).
**Command:** `/pwin:timeline-review`
**Trigger:** On-demand (V1). Scheduled daily or on activity status change (V2).
**Full specification:** `ai_use_cases_reference.html`, UC1. Plugin architecture Section 7.3.

**What it does:**

Reads activity dates, dependencies, and the bid calendar. Identifies timeline gaps, cascade risks, and downstream impact. Writes ActivityAIInsight records with specific, quantified findings.

**Reads:** Activities (dates, status, dependencies, effort), calendar (working days, holidays, key milestones), team assignments.

**Writes:** ActivityAIInsight with: `gap_working_days`, `rag_status`, `cascade_risk` (boolean), `downstream_impact` (list of affected activities), `mitigation_options` (ranked list).

**MCP tools used:**
- Read: `get_activities`, `get_calendar`, `get_team`
- Write: `update_activity_insight`, `add_risk_flag`, `create_standup_action`

**Output:** Per-activity RAG status with cascade analysis. Bid-level timeline summary showing critical path health and overall schedule confidence.

---

#### Skill 6: Effort Reforecasting (`effort-reforecast`) — UC2

**Command:** `/pwin:effort-reforecast`
**Trigger:** On-demand (V1). Triggered by significant timeline deviation (V2).
**Full specification:** `ai_use_cases_reference.html`, UC2.

**What it does:**

Reads activity effort estimates, team assignments, and rate card data. Produces revised forecast dates based on actual progress, resource conflicts, and a revised bid cost estimate.

**Reads:** Activities (planned vs actual effort), team (assignments, availability, rate card), calendar.

**Writes:** Revised forecast dates per activity, resource conflict register, revised bid cost estimate.

**MCP tools used:**
- Read: `get_activities`, `get_team`, `get_calendar`
- Write: `update_activity_insight`, `update_bid_insight`, `add_risk_flag`

**Output:** Revised effort forecast with variance analysis, resource conflict flags, and updated bid cost projection.

---

#### Skill 7: Standup Prioritisation (`standup-priorities`) — UC3

**Command:** `/pwin:standup-priorities`
**Trigger:** On-demand (V1). Scheduled daily pre-standup (V2).
**Full specification:** `ai_use_cases_reference.html`, UC3.

**What it does:**

Reads standup actions, activity status, and gate proximity to produce a daily prioritised action list (maximum 5 items). Flags deferred actions with carry-forward warnings.

**Reads:** Standup actions (status, owner, due date, deferrals), activities (status, gate proximity), governance gates (next gate date, entry criteria).

**Writes:** Prioritised daily action list, carry-forward flags on deferred actions.

**MCP tools used:**
- Read: `get_standup_actions`, `get_activities`, `get_governance_gates`, `get_calendar`
- Write: `create_standup_action`, `update_standup_action_deferred`

**Output:** Top 5 priority actions for today with rationale, plus deferred action escalation list.

---

#### Skill 8: Compliance Coverage (`compliance-coverage`) — UC4

**Command:** `/pwin:compliance-check`
**Trigger:** On-demand (V1). Scheduled pre-gate or on response section status change (V2).
**Full specification:** `ai_use_cases_reference.html`, UC4.

**What it does:**

Reads response sections, the evaluation framework, and compliance requirements. Produces a weighted risk matrix identifying compliance gaps, coverage weaknesses, and disqualification risks.

**Reads:** Response sections (status, content coverage), evaluation framework (mandatory requirements, hurdle marks), compliance requirements (position, evidence status).

**Writes:** ComplianceCoverageAIInsight with: weighted risk matrix, compliance gap list, disqualification risk flags.

**MCP tools used:**
- Read: `get_response_sections`, `get_evaluation_framework`, `get_compliance_requirements`
- Write: `create_compliance_coverage_insight`, `add_risk_flag`, `create_standup_action`

**Output:** Compliance coverage heatmap with gap analysis, disqualification risk register, and priority remediation actions.

---

#### Skill 9: Win Theme Audit (`win-theme-audit`) — UC5

**Command:** `/pwin:win-theme-audit`
**Trigger:** On-demand (V1). Scheduled post-review cycle (V2).
**Full specification:** `ai_use_cases_reference.html`, UC5.

**What it does:**

Reads win themes, response items, and review scorecards. Assesses win theme coverage per section, portfolio saturation per theme, and produces a priority list for under-represented themes.

**Reads:** Win themes (register), response items (draft content, status), review scorecards (theme coverage assessments from reviewers).

**Writes:** Win theme coverage score per section, portfolio saturation score per theme, priority rewrite list.

**MCP tools used:**
- Read: `get_win_themes`, `get_response_sections`, `get_reviews`
- Write: `update_win_theme_coverage_score`, `create_standup_action`

**Output:** Theme saturation matrix (theme x section), under-coverage flags, and priority list of sections needing theme reinforcement.

---

#### Skill 10: Marks Allocation Optimisation (`marks-allocation`) — UC6

**Command:** `/pwin:marks-allocation`
**Trigger:** On-demand (V1). Scheduled when effort data changes significantly (V2).
**Full specification:** `ai_use_cases_reference.html`, UC6.

**What it does:**

Reads response sections, response items, and the evaluation framework. Calculates effort-per-mark efficiency across sections and recommends reallocation to maximise score return.

**Reads:** Response sections (marks, weight, hurdle status), response items (effort invested, status), evaluation framework (scoring bands).

**Writes:** EffortAllocationAIInsight with: efficiency score per section (effort invested vs marks available), reallocation recommendations, over-invested/under-invested flags.

**MCP tools used:**
- Read: `get_response_sections`, `get_evaluation_framework`, `get_activities`
- Write: `create_effort_allocation_insight`, `create_standup_action`

**Output:** Efficiency ranking of sections by effort-to-marks ratio, reallocation recommendations with expected score impact, hurdle section investment adequacy check.

---

#### Skill 11: Review Trajectory (`review-trajectory`) — UC7

**Command:** `/pwin:review-trajectory`
**Trigger:** On-demand (V1). Triggered after review cycle completion (V2).
**Full specification:** `ai_use_cases_reference.html`, UC7.

**What it does:**

Reads review scorecards across review cycles (pink, red, gold) and review actions. Tracks score trajectory per response item, flags sections trending below hurdle, and produces a recovery priority list.

**Reads:** Review scorecards (scores per cycle, reviewer comments), review actions (status, completion), response sections (hurdle marks, evaluation weight).

**Writes:** Trajectory per response item across pink-red-gold cycles, below-hurdle flags, recovery priority list with specific improvement actions.

**MCP tools used:**
- Read: `get_reviews`, `get_response_sections`, `get_evaluation_framework`
- Write: `update_activity_insight`, `add_risk_flag`, `create_standup_action`

**Output:** Score trajectory chart data per section across review cycles, sections at risk of below-hurdle score at submission, recovery priority list ranked by marks-at-risk.

---

#### Skill 12: Gate Readiness (`gate-readiness`) — UC9

**Command:** `/pwin:gate-readiness`
**Trigger:** On-demand (V1). Scheduled 3 working days before each gate (V2).
**Full specification:** `ai_use_cases_reference.html`, UC9.

**What it does:**

Reads governance gate definitions, entry criteria, and activity status. Produces a per-criterion pass/fail/at-risk assessment with process integrity flags and governance gap identification.

**Reads:** Governance gates (entry criteria, gate date, gate type), activities (status, completion evidence), compliance requirements (coverage status), review scorecards (if gate requires review completion).

**Writes:** GateReadinessAIInsight with: per-criterion assessment (pass/fail/at-risk), process integrity flags (criteria that cannot be met), governance gaps, recommended gate outcome (proceed/conditional/defer).

**MCP tools used:**
- Read: `get_governance_gates`, `get_activities`, `get_compliance_requirements`, `get_reviews`
- Write: `create_gate_readiness_report`, `log_gate_recommendation`, `create_standup_action`

**Output:** Gate readiness dashboard data with per-criterion RAG status, recommended gate decision, and remediation actions for at-risk criteria.

---

#### Skill 13: Stakeholder Engagement Risk (`stakeholder-engagement-risk`) — UC12

**Command:** `/pwin:stakeholder-risk`
**Trigger:** On-demand (V1). Scheduled pre-gate (V2).
**Full specification:** `ai_use_cases_reference.html`, UC12.

**What it does:**

Reads stakeholder register, governance gates, and engagement data. Identifies gate participation gaps, clearance risks, and sponsor engagement deficits that could block governance or undermine bid quality.

**Reads:** Stakeholders (role, clearance status, availability, engagement history), governance gates (required participants, sign-off authorities), engagement data (meeting attendance, review participation, action completion).

**Writes:** Gate participation gap flags, clearance risk register (stakeholders without required clearance), sponsor engagement actions.

**MCP tools used:**
- Read: `get_stakeholders`, `get_governance_gates`, `get_engagement_data`, `get_team`
- Write: `update_bid_insight`, `add_risk_flag`, `create_standup_action`

**Output:** Stakeholder engagement risk register with gap flags per upcoming gate, clearance risk timeline, and specific engagement actions for the bid manager.

---

## 4. Agent Build Sequence

| Order | Skill | Type | Phase | Dependencies | Validates |
|---|---|---|---|---|---|
| 1 | Timeline Analysis (UC1) | Insight | Phase 3 | MCP read tools + activity data | First insight skill in the system — validates the AIInsight write pattern |
| 2 | Compliance Coverage (UC4) | Insight | Phase 3 | Agent 1 output (response sections, evaluation framework) | Cross-entity insight reasoning over compliance data |
| 3 | Win Theme Refinement | Productivity | Phase 4 | Win theme data (from capture phase or manual entry) | Win theme register creation and strategic alignment |
| 4 | PWIN Scoring | Productivity | Phase 4 | Multiple data sources across app | Multi-dimensional scoring and trend analysis |
| 5 | Gate Readiness (UC9) | Insight | Phase 4 | Governance gates + activity data | Gate recommendation pattern |
| 6 | Standup Prioritisation (UC3) | Insight | Phase 4 | Standup actions + activity data | Daily operational insight pattern |
| 7 | Win Theme Audit (UC5) | Insight | Phase 5 | Win themes + review scorecards | Post-review insight pattern |
| 8 | Review Trajectory (UC7) | Insight | Phase 5 | Review scorecards across cycles | Multi-cycle trajectory analysis |
| 9 | Marks Allocation (UC6) | Insight | Phase 5 | Response sections + effort data | Effort optimisation reasoning |
| 10 | Effort Reforecasting (UC2) | Insight | Phase 5 | Activities + team + rate card | Resource and cost projection |
| 11 | Capture Plan Assembly | Productivity | Phase 5 | Skills 1-2 + Agent 2 + Agent 4 outputs | Multi-agent synthesis document |
| 12 | Competitive Clarification Strategy | Productivity | Phase 5 | Skills 1-2 + Agent 1 + Agent 2 outputs | Strategic question generation |
| 13 | Stakeholder Engagement Risk (UC12) | Insight | Phase 6 | Stakeholder + engagement data | Engagement gap analysis |

---

## 5. Metrics

| Metric | Value |
|---|---|
| Total productivity tasks served | ~20 (8 High, 9 Medium, 3 Low) |
| Average effort reduction (productivity) | 52% |
| Insight skills | 11 (UC1, UC2, UC3, UC4, UC5, UC6, UC7, UC9, UC12) |
| Total skills | 15 (largest agent by skill count) |
| Implementation phases | Phase 3 (UC1, UC4 — first insight skills) through Phase 6 |
| Methodology activities covered | SAL-04.1.1-4, SAL-04.2.1-2, SAL-06.2.1-3, SAL-06.4.1-2, SAL-07.1.3 |
| Insight scope | Activity spine, response quality, governance gates, compliance, win themes, effort allocation, review trajectory, stakeholder engagement |
| Estimated person-days saved per bid | ~15-20 (productivity) + continuous monitoring value (insight skills) |

---

## 6. Relationship to Other Agents

**Agent 3 consumes from:**

| Source Agent | What Agent 3 consumes |
|---|---|
| Agent 1 (Document Intelligence) | EvaluationFramework, ResponseSections, compliance data, marks concentration — the foundation for all scoring and strategy work |
| Agent 2 (Market Intelligence) | Competitive intelligence for win theme differentiation, PWIN scoring (competitive position dimension), clarification strategy |
| Agent 4 (Commercial & Financial) | Commercial data for bid cost insight, price competitiveness dimension in PWIN scoring |

**Agent 3 feeds into:**

| Downstream Agent | What it consumes from Agent 3 |
|---|---|
| Agent 4 (Commercial & Financial) | Marks allocation insight informs effort investment and commercial resource planning |
| Agent 5 (Content Drafting) | Scoring strategy, win theme register, grade band guidance — tells Agent 5 what to write and how to score maximum marks |

**Agent 3 is the primary AIInsight writer.** It is the only agent that writes insight records across the full activity spine, response quality, governance, and compliance domains. (Agent 1 writes UC13/UC14 insights for clarification/amendment impact. Agent 4 writes UC10/UC11 insights for commercial and resource data.)

---

*Agent 3: Strategy & Scoring Analyst | v1.0 | April 2026 | PWIN Architect*
*15 skills (4 productivity, 11 insight) | ~20 methodology tasks + 11 use cases | 52% avg effort reduction*
