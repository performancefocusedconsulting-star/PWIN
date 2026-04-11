# Agent 2: Market & Competitive Intelligence

**Version:** 1.0 | April 2026
**Status:** Design specification — authoritative input for skill implementation
**Parent document:** [[pwin-bid-execution/docs/pwin_architect_plugin_architecture|Plugin Architecture v1.5]] (Section 4.2b)
**Runtime:** [[pwin-architect-plugin/agents/market-intelligence/AGENT|AGENT.md]]
**All agents:** [[pwin-bid-execution/docs/agent_1_document_intelligence|1: Document]] | [[pwin-bid-execution/docs/agent_2_market_intelligence|2: Market]] | [[pwin-bid-execution/docs/agent_3_strategy_scoring|3: Strategy]] | [[pwin-bid-execution/docs/agent_4_commercial_financial|4: Commercial]] | [[pwin-bid-execution/docs/agent_5_content_drafting|5: Content]] | [[pwin-bid-execution/docs/agent_6_solution_delivery|6: Solution]]
**Data model authority:** `bid_execution_architecture_v6.html`

---

## 1. Agent Identity

**Purpose:** Researches clients, sectors, competitors, incumbent performance. Builds intelligence briefings from uploaded documents and external sources. This agent has a life outside individual bids — client intelligence should run on a recurring basis (monthly/quarterly per client) as a BidEquity operational cost, then enriched per-bid when a specific opportunity arises.

**System prompt essence:** "You are a market and competitive intelligence analyst specialising in UK public sector procurement. You research clients, sectors, competitors, and incumbent performance with rigour and source traceability. You distinguish fact from inference. You build structured intelligence briefings that inform capture strategy."

**Operating principles:**
- Cite sources for every claim. Distinguish public record from inference.
- Flag intelligence gaps explicitly — what we don't know is as important as what we do.
- Build on existing client profiles where they exist — don't duplicate prior research.
- Frame competitor analysis as strategic positioning, not personality assessment.

---

## 2. Agent Configuration

**Tools available:**

| Tool | Purpose |
|---|---|
| PDF/Word document reader | Read uploaded client docs, data room materials, annual reports, strategy documents |
| Web search | Public domain research (trade press, policy papers, NAO reports, spending reviews) |
| Contracts Finder API | Award history, contract values, supplier mapping |
| Companies House API | Competitor profiling, financial data, director history |
| `get_response_sections` | Read existing response sections (for cross-referencing intelligence to bid questions) |
| `get_win_themes` | Read win themes (for aligning intelligence to capture strategy) |
| `get_evaluation_framework` | Read evaluation framework (for assessing what the client rewards) |
| `generate_report_output` | Store intelligence reports in the bid execution app |
| Template populator | Output to proforma documents (Client Intelligence Briefing, Battle Cards, etc.) |

**Tools NOT available (by design):**
- Spreadsheet/calculation tools (that's Agent 4)
- Response drafting tools (that's Agent 5)
- MCP write tools for AIInsight (that's Agent 3)

**Knowledge scope:**
- Uploaded client documents (annual reports, strategy docs, policy papers, data room materials)
- Public domain sources (Contracts Finder, Companies House, trade press, NAO, spending reviews)
- Existing bid data via MCP read tools (for cross-referencing intelligence to the current opportunity)
- UK public sector procurement conventions (framework structures, incumbent dynamics, TUPE landscape, Procurement Act 2023 implications)
- Existing client profiles and competitor dossiers from the platform intelligence layer (where they exist)

---

## 3. Skills

Agent 2 owns 5 skills: 5 productivity skills and 0 insight skills.

### 3.1 Productivity Skills

---

#### Skill 1: Client Intelligence Profiling (`client-profiling`)

**Priority:** BUILD FIRST — foundation skill, all other Agent 2 skills build on the client context established here.
**Command:** `/pwin:client-brief`
**Trigger:** Human-invoked. Bid manager uploads client documents and/or triggers research for a specific client organisation. Also supports recurring scheduled execution (monthly/quarterly per client).

**What it does:**

Builds a comprehensive client intelligence profile by combining uploaded documents with public domain research. Produces a structured Customer Intelligence Briefing that informs capture strategy and bid positioning.

**Methodology activities covered:** SAL-01.1.2, SAL-01.1.3, SAL-01.1.4, SAL-01.2.1, SAL-01.2.2, SAL-01.2.3

**Input specification:**

| Input | Source | Required |
|---|---|---|
| Client annual report / strategy document | Uploaded PDF/Word | Recommended |
| Client policy papers / spending plans | Uploaded PDF/Word | Optional |
| Client name + sector | Human input | Yes |
| Existing client profile (if any) | Platform intelligence layer | Optional (auto-loaded if exists) |
| ITT Volume 1 (if bid-specific) | Uploaded PDF/Word | Optional |

**Process:**

```
Step 1: Existing profile check
  - Check whether a client profile already exists in the platform intelligence layer
  - If yes: load existing profile as baseline, flag sections older than 90 days for refresh
  - If no: create new profile from scratch

Step 2: Client document ingestion (SAL-01.1.2)
  - Ingest uploaded client documents (annual reports, strategy docs, policy papers)
  - Extract: strategic priorities, organisational structure, key programmes,
    budget commitments, transformation agenda, technology strategy
  - Map organisational hierarchy and key directorates

Step 3: Public domain research (SAL-01.1.3)
  - Web search for published priorities, spending reviews, NAO reports, policy drivers
  - Trade press scanning for recent announcements, leadership changes, restructures
  - Identify machinery of government changes affecting the client
  - Locate relevant select committee reports, audit findings, public accounts committee evidence

Step 4: Supply chain mapping (SAL-01.1.4)
  - Query Contracts Finder for all contracts awarded by this client in last 5 years
  - Map existing strategic suppliers: who holds what, contract values, expiry dates
  - Identify framework agreements the client uses
  - Flag contracts approaching expiry (re-procurement opportunities)
  - Extract the client's procurement patterns: preferred routes, typical timescales, evaluation preferences

Step 5: Buyer values and pain points (SAL-01.2.1, SAL-01.2.2)
  - From all sources, identify buyer values (what this client rewards)
  - Identify pain points and hot-button issues (what keeps them awake at night)
  - Analyse the procurement driver — what is the client trying to solve with this procurement?
  - Map stated priorities against revealed preferences (what they say vs what they fund)

Step 6: Customer Intelligence Briefing synthesis (SAL-01.2.3)
  - Synthesise all findings into Customer Intelligence Briefing proforma
  - Flag intelligence gaps: what we couldn't determine, what needs human input
  - Write report via generate_report_output()
  - If bid-specific: cross-reference against ResponseSections and EvaluationFramework
```

**Output template:**

```
CUSTOMER INTELLIGENCE BRIEFING
===============================
Client:                     [organisation name]
Sector:                     [sector]
Profile status:             [new/refreshed/enriched for bid]
Last updated:               [date]
Intelligence confidence:    [HIGH/MEDIUM/LOW]

CLIENT OVERVIEW
  Organisation type:        [department/agency/NDPB/NHS trust/local authority/etc.]
  Headcount:                [approximate]
  Annual budget:            [if available]
  Key directorates:         [list relevant to our services]
  Recent leadership:        [key appointments, departures, restructures]

STRATEGIC PRIORITIES
  [Numbered list of client strategic priorities with source citations]
  1. [Priority] — Source: [document/URL, page/date]
  2. [Priority] — Source: [document/URL, page/date]
  ...

POLICY DRIVERS
  [External policy context driving this client's agenda]
  - [Policy driver] — Impact: [how it affects procurement decisions]
  ...

PROCUREMENT DRIVER
  [What specific problem or objective is driving this procurement?]
  Evidence: [supporting sources]
  Hypothesis: [our interpretation — clearly labelled as inference]

EXISTING SUPPLY CHAIN
  Current strategic suppliers:
  | Supplier | Contract | Value | Expiry | Framework |
  |----------|----------|-------|--------|-----------|
  | [name]   | [desc]   | [GBP] | [date] | [y/n]     |
  ...
  Procurement patterns:     [preferred routes, typical evaluation approach]

BUYER VALUES & HOT BUTTONS
  Values (what they reward):
  - [Value 1] — Evidence: [source]
  - [Value 2] — Evidence: [source]
  ...
  Hot buttons (what they worry about):
  - [Issue 1] — Evidence: [source]
  - [Issue 2] — Evidence: [source]
  ...

INTELLIGENCE GAPS
  [What we don't know and cannot determine from available sources]
  - [Gap 1] — Recommended action: [how to fill this gap]
  - [Gap 2] — Recommended action: [how to fill this gap]
  ...

Sources: [count] documents, [count] public sources
```

**Quality criteria:**
- Every claim must have a source citation. No unsourced assertions.
- Public record must be clearly distinguished from inference. Inferences must be labelled as hypotheses.
- Supply chain data must include contract values and expiry dates where available from Contracts Finder.
- Intelligence gaps must be explicit and actionable — each gap should suggest how to fill it.
- If building on an existing profile, changes from prior version must be highlighted.
- Buyer values must cite evidence, not just restate the client's mission statement.

**Practitioner design notes (from assessment review):**
> SAL-01.1.2: "Market researcher agent given prescriptive instructions via a skill to research the client. Reference document populated. Should run monthly/quarterly as BidEquity operational cost."

> SAL-01.1.3: "Market researcher AI synthesises into template, made available in bid library."

> SAL-01.1.4: "Client profile including supply chain extracted via API from Contracts Finder."

> SAL-01.2.1: "Presenting a report constructed by AI within a digestible template."

> SAL-01.2.2: "Market researcher role ingesting documentation, synthesising hot buttons and buyer values."

> SAL-01.2.3: "Completed synthesis into customer intelligence report within hours of ITT release."

**Design note:** This skill must support two execution modes: (1) recurring scheduled execution as a platform service (monthly/quarterly per client, independent of any bid), and (2) bid-specific enrichment when a new opportunity arises. The platform needs a client intelligence layer that persists across bids.

---

#### Skill 2: Incumbent Performance Assessment (`incumbent-assessment`)

**Command:** `/pwin:incumbent-review`
**Trigger:** Human-invoked. Bid manager uploads data room materials or triggers assessment for a known incumbent.
**Depends on:** Skill 1 (Client Intelligence Profiling) — benefits from existing supply chain mapping but can run independently.

**What it does:**

Conducts a structured assessment of the incumbent supplier's performance, identifying vulnerabilities, stickiness factors, transformation opportunities, and commercial positioning. This is the intelligence foundation for displacement strategy.

**Methodology activities covered:** SAL-02.1.1, SAL-02.1.2, SAL-02.1.3, SAL-02.2.1, SAL-02.2.2, SAL-02.3.1, SAL-02.3.2, SAL-02.3.3, SAL-02.3.4, SAL-02.3.5

**Input specification:**

| Input | Source | Required |
|---|---|---|
| Incumbent name | Human input | Yes |
| Performance reports / SLA data | Uploaded from data room (PDF/Excel) | Recommended |
| Audit reports | Uploaded PDF | Optional |
| Contract value / award data | Contracts Finder API | Auto-retrieved |
| Companies House data | Companies House API | Auto-retrieved |
| Evaluation framework | MCP read (`get_evaluation_framework`) | Optional (for alignment analysis) |

**Process:**

```
Step 1: Incumbent identification and baseline
  - Confirm incumbent identity from Contracts Finder award data
  - Retrieve financial data from Companies House (revenue, profit, headcount trends)
  - Identify contract history: how long have they held this contract, any extensions?
  - Retrieve any public performance data (Procurement Act 2023 mandates release)

Step 2: SLA performance analysis (SAL-02.1.1)
  - Ingest uploaded performance reports and SLA data from data room
  - Extract: KPI categories, target vs actual, trend over contract duration
  - Identify areas of consistent underperformance
  - Identify areas of strong performance (where displacement argument is weak)
  - Flag any formal remediation notices or service credits applied

Step 3: Culture and partnership assessment (SAL-02.1.2)
  - Web search for public signals: awards, case studies, press coverage, staff reviews
  - Flag: this assessment has inherently low AI contribution (~30%)
  - Identify publicly available indicators of relationship quality
  - Note: unofficial feedback from past employees is human-only intelligence —
    flag as an intelligence gap for the bid manager to fill

Step 4: Innovation assessment (SAL-02.1.3)
  - Search for incumbent innovation track record: published case studies, awards,
    conference presentations, thought leadership
  - Assess: has the incumbent invested in transformation during the contract?
  - Identify technology choices and platform dependencies

Step 5: Price competitiveness analysis (SAL-02.2.1)
  - Retrieve contract award values from Contracts Finder
  - Analyse price trajectory across contract term (initial award vs extensions)
  - Benchmark against comparable contracts in same sector
  - Flag: detailed commercial modelling is Agent 4's domain —
    this skill provides the intelligence input

Step 6: Transition stickiness assessment (SAL-02.2.2)
  - Assess stickiness across multiple dimensions:
    - TUPE: staff numbers, terms, pension obligations, union agreements
    - Technology: proprietary platforms, integration dependencies, data migration
    - Knowledge: tacit knowledge, institutional memory, relationship networks
    - Service criticality: business continuity risk during transition
    - Political: ministerial/board sensitivity to supplier change
  - Rate each dimension: high/medium/low stickiness
  - Identify mitigation strategies per dimension

Step 7: Transformation opportunity identification (SAL-02.3.1, SAL-02.3.2, SAL-02.3.3)
  - Identify transformation opportunities across five domains:
    - Organisational: structure, operating model, governance
    - Process: automation, simplification, lean improvements
    - Technology: platform modernisation, cloud migration, integration
    - Data: analytics, insight, decision support
    - Performance: outcome-based models, continuous improvement
  - For each opportunity: evidence base, feasibility, likely client appetite
  - Assess alignment to evaluation framework (will the procurement reward transformation?)

Step 8: Commercial impact modelling (SAL-02.3.4)
  - Extract cost driver information: capital, people, volumetrics
  - Identify scenarios for commercial positioning against incumbent
  - Flag: detailed financial modelling is Agent 4 — this provides the intelligence inputs

Step 9: Synthesis (SAL-02.3.5)
  - Consolidate all findings into Incumbent Performance Assessment proforma
  - Rate overall incumbent position: strong / moderate / weak
  - Identify the displacement narrative: why should the client switch?
  - Write report via generate_report_output()
```

**Output template:**

```
INCUMBENT PERFORMANCE ASSESSMENT
=================================
Incumbent:                  [company name]
Contract:                   [contract title]
Contract value:             [GBP]
Contract duration:          [start] to [end] ([extensions granted])
Assessment confidence:      [HIGH/MEDIUM/LOW]

SLA PERFORMANCE SUMMARY
  | KPI Category | Target | Actual (avg) | Trend | Status |
  |--------------|--------|--------------|-------|--------|
  | [category]   | [x]%   | [y]%         | [up/down/flat] | [green/amber/red] |
  ...
  Remediation notices:      [count, if any]
  Service credits applied:  [value, if any]
  Overall SLA position:     [strong/acceptable/weak]

CULTURE & PARTNERSHIP QUALITY
  Public indicators:        [awards, press, staff reviews]
  Assessed quality:         [strong/adequate/poor]
  Confidence:               LOW — requires human relationship intelligence
  Intelligence gap:         [specific gaps the bid manager should fill]

INNOVATION TRACK RECORD
  Published innovations:    [list with sources]
  Technology investments:   [platforms, tools deployed during contract]
  Assessment:               [innovative/incremental/stagnant]

PRICE COMPETITIVENESS
  Award value:              [GBP at award]
  Current run-rate:         [GBP if known from extensions]
  Sector benchmark:         [comparable contract values]
  Assessment:               [competitive/market rate/premium]

TRANSITION STICKINESS ASSESSMENT
  | Dimension | Stickiness | Key Factors | Mitigation |
  |-----------|-----------|-------------|------------|
  | TUPE      | [H/M/L]  | [factors]   | [approach] |
  | Technology| [H/M/L]  | [factors]   | [approach] |
  | Knowledge | [H/M/L]  | [factors]   | [approach] |
  | Service criticality | [H/M/L] | [factors] | [approach] |
  | Political | [H/M/L]  | [factors]   | [approach] |
  Overall stickiness:       [HIGH/MEDIUM/LOW]

TRANSFORMATION OPPORTUNITIES
  | Domain | Opportunity | Evidence | Feasibility | Client Appetite |
  |--------|-------------|----------|-------------|-----------------|
  | Organisational | [desc] | [source] | [H/M/L]   | [H/M/L]        |
  | Process        | [desc] | [source] | [H/M/L]   | [H/M/L]        |
  | Technology     | [desc] | [source] | [H/M/L]   | [H/M/L]        |
  | Data           | [desc] | [source] | [H/M/L]   | [H/M/L]        |
  | Performance    | [desc] | [source] | [H/M/L]   | [H/M/L]        |

EVALUATION ALIGNMENT
  [Does the evaluation framework reward transformation? If yes, which transformation
   opportunities align with the highest-value evaluation criteria?]

COMMERCIAL IMPACT SUMMARY
  Cost drivers identified:  [capital, people, volumetrics]
  Scenario indicators:      [brief positioning signals for Agent 4]

OVERALL INCUMBENT POSITION: [STRONG / MODERATE / WEAK]
  Displacement narrative:   [1-2 sentence summary of why the client should switch]
  Key vulnerability:        [single biggest weakness to exploit]
  Key strength:             [single biggest barrier to displacement]

Sources: [count] data room documents, [count] public sources
Items requiring human input: [count]
```

**Quality criteria:**
- SLA data must be extracted accurately from source documents with trend analysis, not just point-in-time snapshots.
- Every stickiness dimension must be assessed independently — do not collapse into a single score without dimensional analysis.
- Transformation opportunities must be evidence-based, not aspirational. Each must cite a source.
- The displacement narrative must be honest — if the incumbent is strong, say so. Don't manufacture vulnerability.
- Intelligence gaps must be explicit, particularly for SAL-02.1.2 (culture/partnership) where AI contribution is inherently limited.
- Procurement Act 2023 performance data obligations must be referenced where applicable.

**Practitioner design notes (from assessment review):**
> SAL-02.1.1: "Procurement Act 2023 requires performance data release. Fundamentally a completely AI job."

> SAL-02.1.2: "AI can't be a massive contributor — talking to past employees, getting unofficial feedback. 30%."

> SAL-02.2.2: "Stickiness is contextual across many levers — TUPE, technology legacy, service criticality, political. AI risk-based model with parameters to investigate."

> SAL-02.3.1: "AI could do heavy lifting presenting options with evidence, human in loop to test and challenge."

> SAL-02.3.4: "Extracting information, building Excel with cost drivers (capital, people, volumetrics), running scenario analysis. AI-driven feature."

> SAL-02.3.5: "All above consolidated into single report, driven by agent with skills within templated document."

---

#### Skill 3: Competitor Profiling & Battle Cards (`competitor-profiling`)

**Command:** `/pwin:competitor-brief`
**Trigger:** Human-invoked. Bid manager identifies known or suspected competitors, or triggers market scan.
**Depends on:** Skill 1 (Client Intelligence Profiling) — uses supply chain mapping to identify likely bidders.

**What it does:**

Identifies credible competitors for a specific opportunity, profiles each one, and produces structured battle cards with counter-strategies and ghost themes. Maintains competitor dossiers that persist across bids.

**Methodology activities covered:** SAL-03.1.1, SAL-03.1.2, SAL-03.1.3, SAL-03.2.1, SAL-03.2.2

**Input specification:**

| Input | Source | Required |
|---|---|---|
| Opportunity description / sector | Human input or from bid data | Yes |
| Known competitors (if any) | Human input | Optional |
| Client supply chain mapping | Skill 1 output | Recommended |
| Contracts Finder award history | Contracts Finder API | Auto-retrieved |
| Evaluation framework | MCP read (`get_evaluation_framework`) | Optional (for alignment scoring) |
| Win themes | MCP read (`get_win_themes`) | Optional (for ghost theme development) |

**Process:**

```
Step 1: Competitor identification (SAL-03.1.1)
  - Query Contracts Finder for suppliers who have won similar contracts
    in same sector, same geography, same value band
  - Cross-reference with client supply chain mapping from Skill 1
  - Add any competitors named by the bid manager
  - Produce long list of potential bidders

Step 2: Competitor categorisation (SAL-03.1.2)
  - Categorise each competitor:
    - Incumbent: current contract holder
    - Contender: credible bidder with relevant track record and capacity
    - Dark horse: less obvious bidder who could surprise (adjacent sector, new entrant)
    - Opportunist: unlikely to win but may bid (capacity constrained, weak track record)
  - Short-list top 3-5 competitors for detailed profiling
  - Rationale for each categorisation with source evidence

Step 3: Competitor profiling (SAL-03.1.3)
  - For each short-listed competitor:
    - Company profile from Companies House (revenue, headcount, profit trend)
    - Recent contract wins from Contracts Finder (track record, sector presence)
    - Public positioning: website, case studies, thought leadership, press releases
    - Likely strategy hypothesis: how will they position?
    - Strengths: what they do well, where they have advantage over us
    - Weaknesses: where they are vulnerable, what they lack
    - Price positioning: historic pricing signals from award data
    - Team capacity: are they stretched across too many bids?
    - Partnership/subcontractor signals: likely teaming arrangements

Step 4: Counter-strategy development (SAL-03.2.1)
  - For each top competitor:
    - Develop counter-strategies: how do we neutralise their strengths?
    - Develop ghost themes: statements in our response that create doubt about
      competitor approaches without naming them
    - Map counter-strategies to specific ResponseSections where they should be deployed
  - Cross-reference against win themes: does each win theme counter a competitor strength?

Step 5: Validation and battle card production (SAL-03.2.2)
  - Validate competitor assessment with available evidence
  - Produce one battle card per competitor
  - Produce competitive landscape summary
  - Write reports via generate_report_output()
```

**Output template:**

```
COMPETITIVE LANDSCAPE ANALYSIS
================================
Opportunity:                [title]
Competitors assessed:       [count long list] identified, [count] profiled in detail
Assessment confidence:      [HIGH/MEDIUM/LOW]

COMPETITOR CATEGORISATION
  | Competitor | Category | Rationale | Profile? |
  |------------|----------|-----------|----------|
  | [name]     | Incumbent | [reason] | Yes      |
  | [name]     | Contender | [reason] | Yes      |
  | [name]     | Dark horse| [reason] | Yes      |
  | [name]     | Opportunist | [reason] | No    |
  ...

---

BATTLE CARD: [Competitor Name]
==============================
Category:                   [Incumbent/Contender/Dark Horse]
Revenue:                    [GBP, from Companies House]
Headcount:                  [from Companies House]
Relevant contract wins:     [count in last 3 years]

STRATEGY HYPOTHESIS
  [2-3 sentences: how will this competitor position their bid?]

STRENGTHS
  - [Strength 1] — Evidence: [source]
  - [Strength 2] — Evidence: [source]
  ...

WEAKNESSES
  - [Weakness 1] — Evidence: [source]
  - [Weakness 2] — Evidence: [source]
  ...

COUNTER-STRATEGY
  [How we neutralise their strengths and exploit their weaknesses]
  - [Counter 1] — Deploy in: [ResponseSection refs]
  - [Counter 2] — Deploy in: [ResponseSection refs]
  ...

GHOST THEMES
  [Statements for our response that create doubt about this competitor's approach]
  - "[Ghost theme text]" — Use in: [ResponseSection refs]
  - "[Ghost theme text]" — Use in: [ResponseSection refs]
  ...

PRICE POSITIONING
  Historic award values:    [from Contracts Finder]
  Likely price position:    [aggressive/market rate/premium]
  Rationale:                [evidence]

WIN PROBABILITY AGAINST:    [HIGH/MEDIUM/LOW]
  Key factor:               [single most important variable]

---
[Repeat battle card for each profiled competitor]
---

INTELLIGENCE GAPS
  - [Gap 1] — Recommended action: [how to fill]
  ...
```

**Quality criteria:**
- Competitor identification must be evidence-based from Contracts Finder data, not guesswork.
- Every strength and weakness must cite a source. Unsourced competitor claims are not permitted.
- Ghost themes must be factual and defensible — they highlight genuine differentiators, not mud-slinging.
- Strategy hypotheses must be clearly labelled as inference, not presented as fact.
- Counter-strategies must map to specific ResponseSections where they can be deployed.
- Financial data must come from Companies House, not estimates.

**Practitioner design note (from assessment review):**
> SAL-03.1.2: "Competitive landscape is small on large deals — handful of primes you compete with day in, day out. Building competitive picture in terms of strengths, weaknesses, battle cards — AI can drive."

---

#### Skill 4: Sector & Market Scanning (`sector-scanning`)

**Command:** `/pwin:sector-scan`
**Trigger:** Human-invoked. Can run standalone for general market awareness or as input to a specific bid.

**What it does:**

Scans public domain sources for sector-specific intelligence: trade press, analyst reports, policy changes, spending commitments, and market trends. Produces a sector context report that informs positioning and strategy.

**Methodology activities covered:** SAL-01.1.3 (sector-specific component), plus broader market context.

**Input specification:**

| Input | Source | Required |
|---|---|---|
| Sector / market segment | Human input | Yes |
| Client name (if bid-specific) | Human input | Optional |
| Existing sector intelligence | Platform intelligence layer | Optional (auto-loaded if exists) |

**Process:**

```
Step 1: Trade press and analyst scanning
  - Web search for sector-specific intelligence:
    - Trade press (sector-specific publications)
    - Analyst reports and market sizing
    - Industry body publications and surveys
    - Conference proceedings and thought leadership
  - Filter for last 12 months unless historical context is specifically needed

Step 2: Policy and spending analysis
  - Identify relevant policy changes (legislation, regulation, guidance)
  - Spending Review commitments affecting this sector
  - Machinery of government changes (department mergers, new agencies)
  - NAO and PAC reports highlighting systemic issues in this sector

Step 3: Market dynamics
  - Identify sector trends: consolidation, new entrants, technology shifts
  - Map major framework agreements and their renewal timelines
  - Identify upcoming procurement pipelines from published plans
  - Note regulatory changes affecting service delivery models

Step 4: Synthesis
  - Synthesise sector context relevant to the opportunity (if bid-specific)
  - Output as standalone Sector Intelligence Report or as a section within
    the Customer Intelligence Briefing (Skill 1)
  - Write via generate_report_output()
```

**Output template:**

```
SECTOR INTELLIGENCE REPORT
===========================
Sector:                     [sector name]
Scope:                      [standalone/bid-specific for {opportunity}]
Period covered:             [date range]
Assessment confidence:      [HIGH/MEDIUM/LOW]

SECTOR OVERVIEW
  Market size:              [GBP if available]
  Key trends:               [3-5 bullet points with sources]
  Growth/contraction:       [trajectory with evidence]

POLICY DRIVERS
  | Policy/Regulation | Impact on Sector | Implication for Bid |
  |-------------------|------------------|---------------------|
  | [policy]          | [impact]         | [implication]       |
  ...

SPENDING COMMITMENTS
  [Relevant spending review allocations, departmental budgets]

MARKET DYNAMICS
  Major frameworks:         [list with renewal dates]
  Pipeline:                 [upcoming procurements from published plans]
  New entrants:             [any notable market entries]
  Consolidation:            [M&A activity affecting competitive landscape]

SECTOR RISKS AND OPPORTUNITIES
  Risks:
  - [Risk 1] — Source: [citation]
  ...
  Opportunities:
  - [Opportunity 1] — Source: [citation]
  ...

Sources: [count] publications, [count] public sources
```

**Quality criteria:**
- All intelligence must be sourced and dated. Undated sector intelligence has limited value.
- Policy drivers must distinguish between enacted legislation and proposed changes.
- Spending commitments must reference specific Spending Review allocations, not general aspirations.
- If bid-specific, the report must explicitly connect sector trends to the opportunity.

---

#### Skill 5: Stakeholder Mapping (`stakeholder-mapping`)

**Command:** `/pwin:stakeholder-map`
**Trigger:** Human-invoked. Typically run early in capture phase using ITT documentation and public organisational data.
**Depends on:** Skill 1 (Client Intelligence Profiling) — uses organisational structure data.

**What it does:**

Maps the client's decision-making unit from published organisational data and ITT instructions. Provides structural mapping that the bid team enriches with relationship intelligence. This skill has inherently lower AI contribution (~27% average) because relationship intelligence is fundamentally human — AI does the structural mapping; humans add the relationship layer.

**Methodology activities covered:** SAL-10.1.1, SAL-10.1.2, SAL-10.1.3, SAL-10.2.1, SAL-10.2.3

**Input specification:**

| Input | Source | Required |
|---|---|---|
| Client name | Human input | Yes |
| ITT instructions (evaluation panel details) | Uploaded PDF/Word or from Skill 1 | Recommended |
| Client organisational structure | Web search / uploaded org charts | Optional |
| Existing stakeholder map (if any) | Platform intelligence layer | Optional |
| Relationship intelligence | Human input (post-processing) | Not AI-sourced |

**Process:**

```
Step 1: Decision-making unit identification (SAL-10.1.1)
  - Extract evaluation panel composition from ITT instructions
  - Map published organisational structure from client website/reports
  - Identify: procurement lead, senior responsible officer (SRO),
    technical evaluators, commercial evaluators, user representatives
  - Cross-reference with client intelligence profile (Skill 1) for key personnel

Step 2: Stakeholder assessment (SAL-10.1.2)
  - For each identified stakeholder:
    - Role and title
    - Likely evaluation responsibility (quality, commercial, technical)
    - Influence level: decision-maker / influencer / evaluator / user
    - Likely priorities (derived from role, directorate strategy, published speeches)
    - LinkedIn/public profile summary (where available)
  - Flag: influence assessment from public data is inherently limited —
    human relationship intelligence is essential

Step 3: Relationship mapping (SAL-10.1.3)
  - Produce structural relationship map (who reports to whom, evaluation governance)
  - Leave relationship strength fields as "not assessed" — this is human input
  - Identify previous interactions from CRM/bid history (if available)
  - Flag: this step requires significant human enrichment

Step 4: Engagement plan drafting (SAL-10.2.1)
  - Draft engagement plan per stakeholder based on:
    - Role in evaluation
    - Likely priorities
    - Available engagement channels (pre-market engagement, site visits, presentations)
  - Flag procurement rules on engagement during tender period
  - Mark engagement plan as DRAFT — requires human relationship overlay

Step 5: Capture plan readiness update (SAL-10.2.3)
  - Update stakeholder map for capture plan lock
  - Identify gaps in stakeholder coverage
  - Recommend priority stakeholders for relationship building
```

**Output template:**

```
STAKEHOLDER MAP
================
Client:                     [organisation name]
Opportunity:                [bid title]
Stakeholders mapped:        [count]
Assessment confidence:      LOW — requires human relationship enrichment

DECISION-MAKING UNIT
  | Name/Role | Title | Evaluation Role | Influence | Priorities | Relationship |
  |-----------|-------|-----------------|-----------|------------|--------------|
  | [name]    | [title] | [quality/commercial/SRO] | [decision-maker/influencer/evaluator] | [likely priorities] | NOT ASSESSED |
  ...

EVALUATION GOVERNANCE
  [How the evaluation panel is structured, moderation process, approval chain]

ENGAGEMENT PLAN (DRAFT)
  | Stakeholder | Channel | Message | Timing | Owner | Status |
  |-------------|---------|---------|--------|-------|--------|
  | [name/role] | [channel] | [key message] | [when] | [TBD] | Draft |
  ...
  Note: Engagement during tender period subject to procurement rules.
  Check ITT instructions for permitted contact channels.

GAPS AND RECOMMENDATIONS
  - [Gap 1]: [who we haven't identified and why it matters]
  - [Recommendation 1]: [priority actions for relationship building]
  ...

HUMAN INPUT REQUIRED
  The following fields cannot be completed by AI and require bid team input:
  - Relationship strength (existing/new/warm/cold per stakeholder)
  - Unofficial influence dynamics
  - Historical engagement outcomes
  - Personal preferences and communication styles
```

**Quality criteria:**
- Stakeholder names and titles must come from verifiable public sources, not guessed.
- Influence assessments must be clearly labelled as structural inference, not relationship intelligence.
- Relationship strength must never be assessed by AI — always flagged as "requires human input."
- Engagement plans must respect procurement rules during tender period.
- The template must make it obvious which fields are AI-populated and which await human enrichment.

---

### 3.2 Insight Skills

Agent 2 has no insight skills. Insight skills that consume market intelligence data (competitive context for win strategy, market-informed scoring insights) belong to Agent 3 (Strategy & Scoring Intelligence).

---

## 4. Agent Build Sequence

| Order | Skill | Type | Dependencies | Validates |
|---|---|---|---|---|
| 1 | Client Intelligence Profiling | Productivity | Web search + Contracts Finder API + document reader | Client research pipeline: ingest → research → synthesise → template output |
| 2 | Sector & Market Scanning | Productivity | Web search | Public domain research and synthesis pattern |
| 3 | Incumbent Performance Assessment | Productivity | Document reader + Contracts Finder + Companies House APIs | Multi-source intelligence synthesis with dimensional analysis |
| 4 | Competitor Profiling & Battle Cards | Productivity | Contracts Finder + Companies House APIs + MCP read tools | Competitor research, categorisation, and counter-strategy pattern |
| 5 | Stakeholder Mapping | Productivity | Web search + MCP read tools + Skill 1 output | Structural mapping with human enrichment handoff pattern |

---

## 5. Metrics

| Metric | Value |
|---|---|
| Total methodology tasks served | ~27 |
| High-rated tasks | 16 |
| Medium-rated tasks | 6 |
| Low-rated tasks | 5 |
| Average effort reduction | 53% |
| Implementation phase | Phase 5 |
| Methodology activities covered | SAL-01.1.2-4, SAL-01.2.1-3, SAL-02.1.1-3, SAL-02.2.1-2, SAL-02.3.1-5, SAL-03.1.1-3, SAL-03.2.1-2, SAL-10.1.1-3, SAL-10.2.1, SAL-10.2.3 |
| Insight skills | None (insight skills consuming market intelligence belong to Agent 3) |
| Estimated person-days saved per bid | ~15-20 |

---

## 6. Relationship to Other Agents

**Agent 2 outputs feed into:**

| Downstream Agent | What it consumes from Agent 2 |
|---|---|
| Agent 3 (Strategy & Scoring) | Competitive context for win strategy development, buyer values for theme alignment, incumbent vulnerabilities for positioning |
| Agent 4 (Commercial & Financial) | Incumbent pricing intelligence for benchmarking, contract value history, cost driver intelligence |
| Agent 5 (Content Drafting) | Competitive positioning and ghost themes for response drafting, buyer values for tone and emphasis |
| Agent 6 (Solution & Delivery) | Incumbent operating model intelligence for solution design, transition stickiness assessment, transformation opportunities |

**Agent 2 consumes from:**

| Upstream Agent | What Agent 2 reads |
|---|---|
| Agent 1 (Document Intelligence) | ResponseSections (for cross-referencing intelligence to bid questions), EvaluationFramework (for assessing what the client rewards and alignment analysis) |

**Agent 2 never writes to the bid execution app data model directly** (beyond generate_report_output for intelligence reports). Structured bid data writes are Agent 1's domain; scoring insights are Agent 3's domain.

---

## 7. Design Note: Recurring Intelligence Service

Agent 2 is unique among the agent roster — it operates both per-bid and as a recurring scheduled service. Client profiles and competitor dossiers should be maintained quarterly as a BidEquity operational cost, then enriched per-bid when a specific opportunity arises.

This has platform implications:

1. **Client Intelligence Layer:** The platform needs a client intelligence store that persists across bids. Client profiles, supply chain maps, and stakeholder maps are not bid-specific — they are organisational assets.
2. **Competitor Dossier Library:** Competitor profiles and battle cards should be maintained as living documents. On a large deal, the competitive landscape is small — the same handful of primes compete repeatedly.
3. **Scheduling:** Skills 1 and 4 must support scheduled execution (monthly/quarterly per client) independent of any active bid, triggered by the platform scheduler.
4. **Incremental Updates:** When a skill runs against a client or competitor that already has a profile, it must build on the existing profile — highlighting what has changed — rather than producing a fresh document that ignores prior research.

These requirements align with the Competitor Dossiers and Client Profiles products from the platform product map.

---

*Agent 2: Market & Competitive Intelligence | v1.0 | April 2026 | PWIN Architect*
*5 skills (5 productivity, 0 insight) | ~27 methodology tasks | 53% avg effort reduction*
