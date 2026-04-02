# Agent 4: Commercial & Financial Modelling

**Version:** 1.0 | April 2026
**Status:** Design specification — authoritative input for skill implementation
**Parent document:** `pwin_architect_plugin_architecture.md` (v1.5, Section 4.2d)
**Data model authority:** `bid_execution_architecture_v6.html`
**Insight skill specs:** `ai_use_cases_reference.html` (v1.1, UC10 and UC11)

---

## 1. Agent Identity

**Purpose:** Cost modelling, pricing analysis, scenario planning, risk-premium calculation, bid cost forecasting. Builds the commercial framework for the bid — the numbers that determine whether we can win profitably.

**System prompt essence:** "You are a commercial and financial analyst specialising in UK public sector services contracts. You build cost models, pricing strategies, and commercial frameworks with precision. You show all assumptions explicitly. You run scenarios and stress tests. You never present a single number without a range and a sensitivity assessment."

**Operating principles:**
- Show all assumptions explicitly. Every cost line must trace to a stated assumption.
- Always present ranges, not point estimates. Floor, midpoint, ceiling.
- Flag circular dependencies (e.g., price affects volume, volume affects price).
- Distinguish should-cost (what it costs us) from price-to-win (what we bid).
- Risk premium must be traceable to specific identified risks, not a blanket percentage.

---

## 2. Agent Configuration

**Tools available:**

| Tool | Purpose |
|---|---|
| Spreadsheet/calculation tools | Financial modelling, scenario analysis, sensitivity calculations |
| `get_response_sections` | Read exam paper questions (for pricing schedule alignment) |
| `get_evaluation_framework` | Read evaluation methodology (price/quality weighting) |
| `get_engagement` | Read engagement data (contract value, duration, team size) |
| `get_rate_card` | Read rate card data (day rates, grade mix) |
| `get_team_summary` | Read team composition (staffing model from SOL-06) |
| `get_risks` | Read risk register (for risk premium calculation) |
| `update_activity_insight` | Write commercial activity insights to methodology activities |
| `create_standup_action` | Generate actions from commercial analysis |
| `generate_report_output` | Store commercial reports (cost model, pricing, scenarios) |
| Template populator | Cost model templates, pricing schedules, commercial frameworks |

**Tools NOT available (by design):**
- Web search (that's Agent 2)
- PDF/Word document reader for uploaded files (that's Agent 1)
- Response drafting tools (that's Agent 5)

**Knowledge scope:**
- Existing bid data via MCP read tools (engagement, staffing, rate cards, risks)
- Agent 1 outputs (contract obligations, liability structure, TUPE implications)
- Agent 2 outputs (incumbent pricing, competitor benchmarks from Contracts Finder)
- Agent 6 outputs (solution design — staffing model, transition plan, technology costs)
- UK public sector commercial conventions (payment mechanisms, indexation, service credits, MEAT pricing, social value weighting)

---

## 3. Skills

Agent 4 owns 9 skills: 7 productivity skills and 2 insight skills.

### 3.1 Productivity Skills

---

#### Skill 1: Cost Model Build (`cost-modelling`)

**Priority:** BUILD FIRST — foundation skill, all other Agent 4 skills depend on a costed baseline.
**Command:** `/pwin:cost-model`
**Trigger:** Human-invoked. Bid manager runs after SOL-06 (staffing model) and SOL-07 (transition plan) are substantially complete.
**Depends on:** Agent 6 outputs — staffing model (SOL-06), transition plan (SOL-07), technology costs.

**What it does:**

Builds the bottom-up should-cost model for the bid. Takes the solution design outputs (staffing, technology, transition) and constructs a full cost model with year-by-year trajectory across the contract term. Documents every assumption.

**Input specification:**

| Input | Source | Required |
|---|---|---|
| Staffing model | Agent 6 / SOL-06 output via `get_team_summary` | Yes |
| Rate card | Engagement data via `get_rate_card` | Yes |
| Contract duration and extensions | Engagement data via `get_engagement` | Yes |
| Transition/mobilisation plan | Agent 6 / SOL-07 output | Yes |
| Technology costs | Agent 6 / solution design output | Optional (not all bids have technology) |
| Partner cost placeholders | Partner submissions or estimates | Optional |
| Risk register | Via `get_risks` | Optional (feeds contingency) |

**Process:**

```
Step 1: Workforce cost model (COM-01.1.1-2)
  -- Read staffing model from SOL-06 via get_team_summary()
  -- Read rate card via get_rate_card()
  -- For each role: grade, FTE, day rate, annual cost
  -- Apply employer on-costs (NI, pension, benefits)
  -- Model attrition and replacement costs
  -- Calculate year-by-year workforce cost with:
    - Mobilisation ramp-up profile
    - Steady state FTE
    - Demobilisation ramp-down
    - Annual pay escalation assumptions

Step 2: Non-workforce costs (COM-01.1.3)
  -- Technology costs: licences, hosting, infrastructure, development
  -- Facilities: office space, equipment, utilities
  -- Travel and subsistence
  -- Training and development
  -- Insurance and professional indemnity
  -- Consumables and overheads
  -- Categorise each as: fixed, variable, or semi-variable
  -- Model trajectory: one-off, recurring annual, linked to volume

Step 3: Transition and mobilisation costs (COM-01.1.4)
  -- Read transition plan from SOL-07
  -- TUPE costs: legal, HR, consultation, salary protection
  -- Recruitment costs for non-TUPE hires
  -- Knowledge transfer and shadowing costs
  -- Parallel running costs
  -- Technology migration and setup
  -- Training and induction
  -- Model as a one-off cost block (typically months 1-3)

Step 4: Partner cost integration (COM-01.2.1-3)
  -- Insert partner cost placeholders by workstream
  -- Flag where partner pricing is awaited vs received
  -- Validate partner pricing against should-cost benchmarks
  -- Integrate into total cost model

Step 5: Cost trajectory and assumption register
  -- Produce year-by-year cost model across full contract term
  -- Include extension year costs if applicable
  -- Build assumption register: every cost line traces to a stated assumption
  -- Flag assumptions with highest sensitivity (for Skill 5)
```

**Output template:**

```
Cost Model Summary
==================
Contract term:              [duration] months + [extension] months
Total contract value (TCV): [floor] - [midpoint] - [ceiling]
Annual run rate (steady):   [value]

WORKFORCE COSTS
  Mobilisation (months 1-[x]):  [value]
  Steady state (annual):        [value]
  Total workforce TCV:          [value]
  FTE profile:                  [mobilisation] -> [steady state] -> [demob]
  Key assumptions:              [pay escalation %, attrition %, on-cost %]

NON-WORKFORCE COSTS
  Technology (annual):          [value]
  Facilities (annual):         [value]
  Travel & subsistence:        [value]
  Other:                       [value]
  Total non-workforce TCV:     [value]

TRANSITION COSTS (one-off)
  TUPE:                        [value]
  Recruitment:                 [value]
  Knowledge transfer:          [value]
  Technology setup:            [value]
  Total transition:            [value]

PARTNER COSTS
  [partner 1]:                 [value or AWAITED]
  [partner 2]:                 [value or AWAITED]
  Total partner TCV:           [value]

TOTAL SHOULD-COST
  Year 1:  [value] (includes transition)
  Year 2:  [value]
  Year 3:  [value]
  ...
  TCV:     [floor] - [midpoint] - [ceiling]

ASSUMPTION REGISTER
  [count] assumptions documented
  [count] assumptions flagged as high-sensitivity
  Top 3 sensitive assumptions:
    1. [assumption] — [impact if wrong]
    2. [assumption] — [impact if wrong]
    3. [assumption] — [impact if wrong]
```

**Quality criteria:**
- Every cost line must trace to a stated assumption. No unexplained numbers.
- Workforce costs must reconcile to the staffing model from SOL-06.
- All costs must be expressed as a range (floor/midpoint/ceiling), not a single point estimate.
- Transition costs must align with the transition plan from SOL-07.
- Assumption register must flag which assumptions have the highest sensitivity.

**Practitioner design note:**
> "Extracting information, building Excel with cost drivers (capital, people, volumetrics), running scenario analysis backed off by risks to create tornado-type outcome analysis. AI builds something for a commercial finance person to play with and complete."

---

#### Skill 2: Price-to-Win Analysis (`pricing-scenarios`)

**Command:** `/pwin:price-to-win`
**Trigger:** Human-invoked. Run after should-cost model (Skill 1) is complete and market intelligence (Agent 2) is available.
**Depends on:** Skill 1 (cost model), Agent 2 (competitor pricing data, market benchmarks).

**What it does:**

Establishes the price envelope — the range within which the bid price must fall to be competitive while remaining profitable. Compares the bottom-up should-cost against external market data to identify the gap between what it costs and what we should bid.

**Process:**

```
Step 1: Current cost baseline (COM-02.1.1)
  -- Read Contracts Finder data for comparable contracts (from Agent 2)
  -- Identify incumbent contract value (if rebid)
  -- Adjust for inflation, scope changes, market rate movements
  -- Establish market price benchmark

Step 2: Competitor price positioning (COM-02.1.2)
  -- Assess competitor cost structures (from Agent 2 market intelligence)
  -- Identify likely competitor price range based on:
    - Their typical margin targets
    - Their cost base (onshore/offshore mix, overheads)
    - Their strategic positioning (buying in vs margin target)
  -- Model competitor price envelope

Step 3: Client budget assessment (COM-02.1.3)
  -- Extract budget indicators from ITT documentation
  -- Assess affordability signals from:
    - Incumbent contract value
    - Client budget statements
    - Market expectations for savings
    - Social value investment expectations

Step 4: Price envelope construction (COM-02.2.1-2)
  -- Floor: minimum viable price (should-cost + minimum margin)
  -- Competitive midpoint: market rate adjusted for our value proposition
  -- Ceiling: maximum the client is likely to accept
  -- Map should-cost against envelope
  -- Calculate gap: positive (margin available) or negative (must reduce cost)

Step 5: Gap analysis and recommendations (COM-02.2.3)
  -- If should-cost > ceiling: identify cost reduction levers
    - Offshore/nearshore mix changes
    - Technology substitution for labour
    - Scope optimisation opportunities
    - Partner cost renegotiation
  -- If should-cost < floor: identify margin improvement opportunities
  -- Recommend price position within envelope with rationale
```

**Output template:**

```
Price-to-Win Analysis
=====================
MARKET BENCHMARK
  Incumbent contract value:    [value] ([source])
  Comparable contracts:        [count] contracts analysed
  Market rate range:           [low] - [high]

COMPETITOR POSITIONING
  [Competitor 1]:              [estimated price range] — [rationale]
  [Competitor 2]:              [estimated price range] — [rationale]
  [Competitor 3]:              [estimated price range] — [rationale]

CLIENT AFFORDABILITY
  Budget signals:              [what the ITT/market tells us]
  Expected savings target:     [x]% below incumbent
  Affordability ceiling:       [value]

PRICE ENVELOPE
  Floor (minimum viable):      [value] (should-cost + [x]% margin)
  Competitive midpoint:        [value]
  Ceiling (max acceptable):    [value]

SHOULD-COST vs ENVELOPE
  Our should-cost:             [value]
  Position vs envelope:        [within/above/below]
  Gap:                         [value] ([positive = margin / negative = must cut])

COST REDUCTION LEVERS (if gap is negative)
  Lever 1: [description] — saves [value]
  Lever 2: [description] — saves [value]
  ...
  Total available reduction:   [value]

RECOMMENDATION
  Recommended price position:  [value] at [x]% margin
  Rationale:                   [why this position wins]
  Risk at this position:       [margin risk, competitive risk]
```

**Quality criteria:**
- Market benchmark must cite specific data sources (Contracts Finder references, published values).
- Competitor positioning must be based on evidence, not speculation — flag confidence level.
- Price envelope must be internally consistent (floor < midpoint < ceiling).
- Gap analysis must identify specific, quantified cost levers — not generic suggestions.
- Recommendation must explicitly state the margin at the recommended price.

---

#### Skill 3: Partner Commercial Management (`partner-pricing`)

**Command:** `/pwin:partner-commercial`
**Trigger:** Human-invoked. Run when partner/subcontractor involvement is confirmed.
**Depends on:** Skill 1 (cost model structure — to know where partner costs fit).

**What it does:**

Designs the inter-party commercial framework and manages partner pricing through the bid lifecycle. Prepares pricing requests, validates submissions, and integrates partner costs into the should-cost model.

**Process:**

```
Step 1: Inter-party commercial framework (COM-03.1.1)
  -- Design commercial relationship model:
    - Prime/subcontractor vs consortium vs joint venture
    - Risk allocation between parties
    - Payment flow: back-to-back, cost-plus, fixed price
    - Liability apportionment
    - Service credit flow-down
  -- Document framework for partner negotiation

Step 2: Partner pricing requests (COM-03.1.2)
  -- Prepare pricing request packs per partner:
    - Scope of work (from SOL workstream allocation)
    - Volume assumptions
    - Contract term and extension options
    - Required pricing format (aligned to ITT schedules)
    - Deadline for submission
    - Assumptions to be used (consistency across partners)
  -- Issue pricing requests

Step 3: Partner submission review (COM-03.2.1-2)
  -- Validate partner pricing submissions against:
    - Scope coverage (have they priced everything?)
    - Assumption alignment (are they using our assumptions?)
    - Rate benchmarks (are their rates market-competitive?)
    - Risk allocation (have they priced in risk we didn't allocate to them?)
  -- Flag discrepancies and negotiate adjustments

Step 4: Integration into should-cost model (COM-03.3.1-2)
  -- Replace placeholders in Skill 1 cost model with actual partner pricing
  -- Validate total cost impact
  -- Reconcile against price envelope (from Skill 2)
  -- Flag if partner pricing pushes total cost outside envelope
```

**Output template:**

```
Partner Commercial Framework
============================
Commercial model:              [prime-sub / consortium / JV]
Number of partners:            [count]

PARTNER PRICING STATUS
  [Partner 1]:
    Scope:                     [workstream description]
    Pricing requested:         [date]
    Pricing received:          [date or AWAITED]
    Annual value:              [value]
    TCV:                       [value]
    Validation status:         [validated / issues identified / awaited]
    Issues:                    [list or none]
  ...

INTEGRATION IMPACT
  Total partner cost:          [value]
  % of total should-cost:     [x]%
  Impact on price envelope:   [within / pushes above ceiling by [value]]

RISK ALLOCATION
  Risk [1]:                    [allocated to prime / partner / shared]
  ...

ACTIONS REQUIRED
  [list of outstanding items: pricing awaited, issues to resolve, negotiations needed]
```

**Quality criteria:**
- Every partner must receive consistent assumptions — divergent assumptions corrupt the cost model.
- Partner pricing must be validated against market benchmarks, not accepted at face value.
- Commercial framework must align with the prime contract terms (no back-to-back gaps).
- Integration must immediately flag if total cost exceeds the price envelope.

---

#### Skill 4: Commercial Model Design (`commercial-model`)

**Command:** `/pwin:commercial-model`
**Trigger:** Human-invoked. Run after cost model and price-to-win analysis are complete.
**Depends on:** Skill 1 (cost model), Agent 1 (contract terms and obligations).

**What it does:**

Designs the commercial model — how we get paid, how prices change over time, how underperformance is penalised, and how innovation is rewarded. This is the commercial architecture of the contract, distinct from the pricing itself.

**Process:**

```
Step 1: Payment mechanism design (COM-04.1.1)
  -- Analyse ITT requirements for payment structure
  -- Design payment mechanism:
    - Fixed price / time & materials / outcome-based / hybrid
    - Payment frequency and milestones
    - Invoice and payment terms
    - Transition payment profile
  -- Align with client's stated preferences from ITT

Step 2: Pricing structure and indexation (COM-04.1.2)
  -- Design pricing structure:
    - Unit pricing (per transaction, per user, per FTE)
    - Tiered/banded pricing
    - Volume-linked pricing
    - Blended rate model
  -- Indexation/benchmarking mechanism:
    - CPI/RPI linkage for annual uplift
    - Benchmarking triggers and methodology
    - Market testing provisions
  -- Model multi-year price trajectory with indexation

Step 3: Service credits and incentives (COM-04.1.3)
  -- Map service level obligations to service credit regime
  -- Design service credit mechanism:
    - Calculation methodology
    - Caps (monthly, annual, cumulative)
    - Earnback provisions
    - Reporting requirements
  -- Design innovation and value sharing:
    - Gainshare mechanism
    - Continuous improvement targets
    - Innovation investment and return model

Step 4: Commercial model coherence validation (COM-04.2.1-3)
  -- Validate internal consistency:
    - Payment mechanism aligns with cost structure
    - Service credits are commercially survivable
    - Indexation protects margin over contract term
    - Innovation incentives are funded from efficiency gains
  -- Stress test: what happens to margin under adverse scenarios?
  -- Validate against contract terms (from Agent 1)
```

**Output template:**

```
Commercial Model Specification
==============================
PAYMENT MECHANISM
  Model type:                  [fixed / T&M / outcome / hybrid]
  Payment frequency:           [monthly / quarterly / milestone]
  Transition payments:         [profile description]
  Invoice terms:               [x] days

PRICING STRUCTURE
  Pricing basis:               [unit / tiered / blended / fixed]
  Rate card:                   [summary of key rates]
  Volume assumptions:          [basis for unit pricing]

INDEXATION
  Mechanism:                   [CPI / RPI / custom index]
  Frequency:                   [annual / biennial]
  Cap and collar:              [x]% to [y]%
  Benchmarking:                [trigger and methodology]

SERVICE CREDITS
  Calculation:                 [methodology summary]
  Monthly cap:                 [x]% of monthly charges
  Annual cap:                  [x]% of annual charges
  Earnback:                    [available / not available]

INNOVATION & VALUE SHARING
  Gainshare:                   [mechanism summary]
  CI targets:                  [x]% annual efficiency improvement
  Investment model:            [self-funded / shared / client-funded]

COHERENCE ASSESSMENT
  Internal consistency:        [PASS / ISSUES IDENTIFIED]
  Margin protection:           [adequate / at risk — specify scenarios]
  Contract alignment:          [aligned / gaps identified — specify]
```

**Quality criteria:**
- Commercial model must align with the ITT requirements — no creative structures the client hasn't asked for.
- Service credit caps must be commercially survivable — stress test against historical performance data.
- Indexation mechanism must protect margin over the full contract term including extensions.
- Every element must be traceable to either an ITT requirement or a strategic commercial choice.

---

#### Skill 5: Sensitivity & Scenario Analysis (`sensitivity-analysis`)

**Command:** `/pwin:sensitivity`
**Trigger:** Human-invoked. Run after cost model (Skill 1) and price envelope (Skill 2) are established.
**Depends on:** Skill 1 (cost model with assumptions), Skill 2 (price envelope).

**What it does:**

Stress-tests the cost model and commercial assumptions. Identifies which assumptions have the greatest impact on profitability. Models multiple scenarios to give the commercial lead a range of outcomes for decision-making.

**Process:**

```
Step 1: Sensitivity analysis on key assumptions (COM-05.1.1-2)
  -- Identify top 10-15 cost assumptions from the assumption register
  -- For each assumption, model impact of +/- variation:
    - Pay escalation: +/- 1%, +/- 2%
    - Attrition: +/- 5%, +/- 10%
    - Volume: +/- 10%, +/- 20%
    - Offshore ratio: +/- 10%
    - Partner costs: +/- 5%, +/- 10%
    - Transition duration: +/- 1 month, +/- 3 months
  -- Rank assumptions by margin impact (tornado chart data)
  -- Identify assumption combinations that create compounding risk

Step 2: Scenario modelling (COM-05.2.1-2)
  -- Build three core scenarios:
    - Best case: favourable assumptions across key variables
    - Expected case: most likely assumptions (midpoint)
    - Worst case: adverse assumptions across key variables
  -- For each scenario: total cost, margin, P&L profile, cash flow
  -- Build additional targeted scenarios:
    - Volume reduction scenario (client reduces scope)
    - TUPE cost overrun scenario
    - Partner cost escalation scenario
    - Early termination scenario

Step 3: Margin analysis at multiple price points (COM-05.2.3)
  -- Model margin at: floor price, midpoint, ceiling, recommended position
  -- Calculate breakeven volume for each price point
  -- Identify margin tipping points (where does profit become loss?)

Step 4: P&L trajectory and risk-adjusted view (COM-05.2.4-5)
  -- Model full P&L across contract term at recommended price
  -- Apply risk adjustments: probability-weighted contingency
  -- Produce risk-adjusted margin view
  -- Identify the year(s) of maximum commercial exposure
```

**Output template:**

```
Sensitivity & Scenario Analysis
================================
SENSITIVITY RANKING (tornado chart)
  Rank | Assumption              | -Variation | Impact | +Variation | Impact
  1    | [most sensitive]        | [x]%       | -[y]k  | [x]%       | +[y]k
  2    | [second most sensitive] | ...        | ...    | ...        | ...
  ...
  Key finding: [top 3 assumptions account for [x]% of total margin variance]

SCENARIO MATRIX
                    | Best Case  | Expected   | Worst Case
  Total cost (TCV)  | [value]    | [value]    | [value]
  Revenue (at rec.) | [value]    | [value]    | [value]
  Margin (GBP)      | [value]    | [value]    | [value]
  Margin (%)        | [x]%       | [x]%       | [x]%

TARGETED SCENARIOS
  Volume reduction (-20%):    Margin impact: [value] — [survive / loss-making]
  TUPE cost overrun (+15%):   Margin impact: [value] — [survive / loss-making]
  Partner escalation (+10%):  Margin impact: [value] — [survive / loss-making]
  Early termination (yr 2):   Cumulative P&L: [value] — [recovered / loss]

MARGIN AT PRICE POINTS
  Floor price:                [x]% margin — [viable / unacceptable]
  Midpoint:                   [x]% margin
  Recommended:                [x]% margin
  Ceiling:                    [x]% margin
  Breakeven volume:           [value] at recommended price

P&L TRAJECTORY (at recommended price, expected case)
  Year 1: [value] (transition investment — typically negative)
  Year 2: [value]
  Year 3: [value]
  ...
  Cumulative P&L: [value]
  Payback point:  Year [x]

RISK-ADJUSTED VIEW
  Pre-risk margin:            [x]%
  Contingency required:       [value] (from probability-weighted risks)
  Post-risk margin:           [x]%
  Maximum annual exposure:    Year [x] — [value]
```

**Quality criteria:**
- Tornado chart must rank assumptions by actual margin impact, not assumed importance.
- Scenarios must use internally consistent assumption sets — not arbitrary combinations.
- P&L trajectory must show the payback point — when does cumulative profit turn positive?
- Risk-adjusted view must trace contingency to specific risks from the risk register, not a blanket percentage.
- Every scenario must clearly state whether the contract remains profitable or becomes loss-making.

**Practitioner design note:**
> "Extracting information, building Excel with cost drivers (capital, people, volumetrics), running scenario analysis backed off by risks to create tornado-type outcome analysis. AI builds something for a commercial finance person to play with and complete."

---

#### Skill 6: Pricing Finalisation (`pricing-finalisation`)

**Command:** `/pwin:pricing-lock`
**Trigger:** Human-invoked. Run in the final pricing window before submission.
**Depends on:** Skill 1 (cost model), Skill 2 (price envelope), Skill 5 (scenario analysis), Skill 3 (partner pricing received).

**What it does:**

Sets the final price position, populates ITT pricing schedules, conducts final reconciliation, and locks the pricing model for governance review. This is the last commercial skill to run before the bid is submitted.

**Process:**

```
Step 1: Final price position (COM-06.1.1)
  -- Confirm final price within validated envelope
  -- Reconcile against:
    - Latest should-cost model (all partner pricing received)
    - Scenario analysis outputs (acceptable risk at this price)
    - Governance approval of margin target
  -- Set final price and margin

Step 2: ITT pricing schedule population (COM-06.1.2)
  -- Read ITT pricing schedule templates from ResponseSections
  -- Map cost model line items to ITT schedule format
  -- Populate every required pricing field:
    - Unit rates / blended rates
    - Annual charges by year
    - Transition/mobilisation charges
    - Volume-based charges
    - Optional/extension pricing
  -- Validate totals reconcile to final price position

Step 3: Final reconciliation (COM-06.2.1)
  -- Cross-check: pricing schedules total = cost model total + margin
  -- Cross-check: all ITT pricing fields completed (no blanks)
  -- Cross-check: pricing is consistent across schedules (no contradictions)
  -- Cross-check: indexation/escalation applied consistently
  -- Flag any residual discrepancies for commercial lead resolution

Step 4: Model lock (COM-06.2.2)
  -- Freeze the cost model — no further changes without governance approval
  -- Generate pricing pack for governance review:
    - Final price position and margin
    - Risk-adjusted margin
    - Scenario summary (best/expected/worst)
    - Assumption register
    - Key commercial risks
  -- Write lock status and timestamp
```

**Output template:**

```
Pricing Finalisation Report
===========================
FINAL PRICE POSITION
  Total contract value:        [value]
  Annual run rate (steady):    [value]
  Transition charges:          [value]
  Margin (%):                  [x]%
  Margin (GBP):                [value]
  Risk-adjusted margin:        [x]%

PRICING SCHEDULE STATUS
  Schedule 1 ([name]):         [COMPLETE / ISSUES]
  Schedule 2 ([name]):         [COMPLETE / ISSUES]
  ...
  All schedules reconciled:    [YES / NO — [details]]

RECONCILIATION
  Cost model total:            [value]
  Margin:                      [value]
  Price total:                 [value]
  Pricing schedules total:     [value]
  Reconciliation status:       [RECONCILED / DISCREPANCY of [value]]

GOVERNANCE PACK
  Final price:                 [value]
  Expected margin:             [x]%
  Worst-case margin:           [x]%
  Key risks:                   [top 3]
  Assumptions:                 [count] documented, [count] high-sensitivity
  Commercial lead sign-off:    [REQUIRED]
  Finance sign-off:            [REQUIRED]

MODEL STATUS:                  [LOCKED at [timestamp] / OPEN]
```

**Quality criteria:**
- All ITT pricing schedules must be fully populated — no blank fields.
- Pricing schedules must reconcile exactly to the cost model plus margin.
- Indexation must be applied consistently across all schedules and years.
- Governance pack must present an honest picture — worst-case margin must be clearly stated.
- Model lock must prevent further changes until governance unlocks it.

---

#### Skill 7: Commercial Risk Register (`commercial-risk`)

**Command:** `/pwin:commercial-risk`
**Trigger:** Human-invoked. Run iteratively — first draft after cost model, refined after pricing analysis, finalised before submission.
**Depends on:** Skills 1-6 (all commercial activities generate risks).

**What it does:**

Harvests commercial risks from all COM activities, assesses and prioritises them, develops mitigations, and quantifies the contingency requirement. The commercial risk register feeds directly into the risk premium calculation and governance review.

**Process:**

```
Step 1: Risk harvesting (COM-07.1.1)
  -- Harvest risks from all commercial activities:
    - Cost model assumptions (Skill 1): what if assumptions are wrong?
    - Pricing position (Skill 2): competitive risk, margin risk
    - Partner pricing (Skill 3): partner cost escalation, delivery failure
    - Commercial model (Skill 4): payment mechanism risk, service credit exposure
    - Scenarios (Skill 5): risks identified through stress testing
  -- Read existing risk register via get_risks()
  -- Identify additional commercial risks not captured elsewhere

Step 2: Risk identification and classification (COM-07.1.2)
  -- For each risk:
    - Description: what could go wrong
    - Category: cost overrun / revenue shortfall / margin erosion /
      partner failure / contractual / market / regulatory
    - Trigger: what would cause this risk to materialise
    - Source: which activity/assumption generated it

Step 3: Risk assessment and prioritisation (COM-07.2.1-2)
  -- Assess each risk:
    - Likelihood: very low / low / medium / high / very high
    - Financial impact (GBP): floor / expected / ceiling
    - Probability-weighted impact: likelihood × expected impact
    - Timing: when in the contract term would this materialise
  -- Rank by probability-weighted impact
  -- Identify top 5 risks driving the majority of commercial exposure

Step 4: Mitigation development (COM-07.2.3)
  -- For each material risk:
    - Mitigation actions (what we do to reduce likelihood or impact)
    - Residual risk after mitigation
    - Mitigation cost (if any)
    - Owner: who is responsible for the mitigation
  -- Flag risks that cannot be mitigated (must be priced in or accepted)

Step 5: Contingency quantification (COM-07.2.4-5)
  -- Calculate total contingency requirement:
    - Sum of probability-weighted residual impacts
    - Add management reserve for unknown unknowns (capped at [x]%)
  -- Compare contingency against available margin
  -- Flag if contingency exceeds margin (the bid is commercially unviable)
```

**Output template:**

```
Commercial Risk Register
========================
Total risks identified:        [count]
  Cost overrun:                [count]
  Revenue shortfall:           [count]
  Margin erosion:              [count]
  Partner failure:             [count]
  Contractual:                 [count]
  Market/regulatory:           [count]

TOP 5 RISKS (by probability-weighted impact)
  1. [risk description]
     Likelihood: [x] | Impact: [floor]-[expected]-[ceiling]
     Probability-weighted: [value]
     Mitigation: [action] | Residual: [value]
     Owner: [role]
  2. ...
  ...

FULL RISK REGISTER
  [ref] | [description] | [category] | [likelihood] | [impact range] |
  [probability-weighted] | [mitigation] | [residual] | [owner]
  ...

CONTINGENCY REQUIREMENT
  Probability-weighted total:  [value]
  Management reserve:          [value] ([x]%)
  Total contingency:           [value]
  Available margin:            [value]
  Contingency vs margin:       [covered / shortfall of [value]]

COMMERCIAL VIABILITY ASSESSMENT
  [VIABLE — contingency within margin]
  or
  [AT RISK — contingency exceeds margin by [value], requires [action]]
  or
  [UNVIABLE — recommend bid/no-bid review]
```

**Quality criteria:**
- Every risk must trace to a specific source (assumption, activity, analysis).
- Financial impact must be expressed as a range, never a single number.
- Contingency must be calculated from probability-weighted residual impacts, not a blanket percentage.
- The register must explicitly assess whether the bid is commercially viable.
- Top 5 risks must account for the majority of total commercial exposure — if they don't, the register is incomplete.

---

### 3.2 Insight Skills

---

#### Skill 8: Risk/Pricing Validation (`risk-pricing`) — UC10

**Command:** `/pwin:risk-pricing`
**Trigger:** On-demand (V1). Scheduled on COM-07 completion (V2).
**Depends on:** Skill 7 (commercial risk register), Skill 1 (cost model with risk premium).

**What it does:**

Reads the risk register, the stated risk premium in the cost model, and the probability-weighted impacts. Validates whether the risk premium is consistent with the identified risks and defensible to governance. Writes a consistency verdict and a defensible premium range.

**Full specification:** `ai_use_cases_reference.html`, UC10.

**Process:**

```
Step 1: Read risk and pricing data
  -- Read risk register via get_risks()
  -- Read cost model risk premium from engagement data
  -- Read probability-weighted impacts from Skill 7 output

Step 2: Consistency analysis
  -- Compare stated risk premium against:
    - Sum of probability-weighted residual impacts
    - Industry benchmarks for risk premium (typically 3-8% of TCV for UK public sector)
    - Historical risk materialisation rates from comparable contracts
  -- Assess whether premium covers identified risks
  -- Identify risks not covered by premium

Step 3: Defensibility assessment
  -- Can every pound of risk premium be traced to a specific risk?
  -- Is the premium defensible to governance (not too high, not too low)?
  -- Would an independent review reach a similar figure?

Step 4: Write insight
  -- Write AIInsight with:
    - Risk-to-premium consistency verdict: [consistent / under-priced / over-priced]
    - Defensible premium range: {min, recommended, max}
    - Specific risks not covered
    - Recommendation for adjustment (if any)
```

**Output:** AIInsight records written to app (see UC10 spec for schema). Summary verdict for commercial lead.

---

#### Skill 9: Bid Cost Forecasting (`bid-cost-forecast`) — UC11

**Command:** `/pwin:bid-cost-forecast`
**Trigger:** On-demand (V1). Scheduled weekly during bid lifecycle (V2).
**Depends on:** Engagement data, team composition, activity effort estimates, rate cards.

**What it does:**

Forecasts the cost of bidding itself — how much the bid is costing the organisation to produce, and whether the bid investment is justified by the expected return. Reads engagement data, team composition, activity effort, and rate cards to produce a budget burn forecast, contractor premium analysis, and bid P&L scenario.

**Full specification:** `ai_use_cases_reference.html`, UC11.

**Process:**

```
Step 1: Read bid cost data
  -- Read engagement data via get_engagement()
  -- Read team composition via get_team_summary()
  -- Read rate cards via get_rate_card()
  -- Read activity effort estimates from methodology activities

Step 2: Budget burn forecast
  -- Calculate actual bid cost to date:
    - Internal staff: FTE-days × internal day rate
    - Contractors: FTE-days × contractor day rate
    - External costs: travel, printing, consultants
  -- Forecast remaining bid cost based on:
    - Activities remaining and their effort estimates
    - Team composition for remaining activities
    - Known upcoming costs (e.g., printing, venue hire for presentations)
  -- Project total bid cost at completion

Step 3: Contractor premium analysis
  -- Identify contractor spend as % of total bid cost
  -- Calculate premium over equivalent internal resource
  -- Flag if contractor premium exceeds threshold
  -- Recommend contractor release timing based on remaining activities

Step 4: Bid P&L scenario
  -- Compare total bid cost against expected contract margin
  -- Calculate bid cost as % of first-year margin
  -- Model scenarios:
    - Win: bid cost recovery over contract term
    - Lose: total write-off
    - Probability-adjusted: PWIN × margin - bid cost
  -- Assess whether continued bid investment is justified
```

**Output:** AIInsight records written to app (see UC11 spec for schema). Budget burn summary and investment justification for bid manager.

---

## 4. Agent Build Sequence

| Order | Skill | Type | Dependencies | Validates |
|---|---|---|---|---|
| 1 | Cost Model Build | Productivity | MCP read tools + Agent 6 outputs (staffing, transition) | Full cost modelling pipeline: read inputs → build model → document assumptions |
| 2 | Price-to-Win Analysis | Productivity | Skill 1 output + Agent 2 market data | Market benchmarking and price envelope construction |
| 3 | Sensitivity & Scenario Analysis | Productivity | Skill 1 + Skill 2 outputs | Assumption stress-testing and scenario modelling pattern |
| 4 | Commercial Risk Register | Productivity | Skills 1-3 outputs + MCP risk tools | Risk harvesting, assessment, and contingency calculation |
| 5 | Partner Commercial Management | Productivity | Skill 1 output (cost model structure) | Partner pricing lifecycle and integration |
| 6 | Commercial Model Design | Productivity | Skill 1 + Agent 1 contract analysis | Payment mechanism and commercial architecture design |
| 7 | Pricing Finalisation | Productivity | Skills 1-6 outputs | Final reconciliation and governance lock |
| 8 | Risk/Pricing Validation | Insight | Skill 7 output + cost model | UC10: risk premium consistency analysis |
| 9 | Bid Cost Forecasting | Insight | Engagement data + team data | UC11: bid investment justification |

---

## 5. Metrics

| Metric | Value |
|---|---|
| Total methodology tasks served | ~39 |
| High-rated tasks | 11 |
| Average effort reduction | 37% |
| Implementation phase | Phase 5 |
| Methodology activities covered | COM-01.1.1-4, COM-01.2.1-3, COM-02.1.1-3, COM-02.2.1-3, COM-03.1.1-2, COM-03.2.1-2, COM-03.3.1-2, COM-04.1.1-3, COM-04.2.1-3, COM-05.1.1-2, COM-05.2.1-3, COM-06.1.1-2, COM-06.2.1-2, COM-07.1.1-2, COM-07.2.1-3 |
| Insight skills | UC10 (Risk/Pricing Validation), UC11 (Bid Cost Forecasting) |
| Estimated person-days saved per bid | ~12-15 |

---

## 6. Relationship to Other Agents

**Agent 4 consumes from:**

| Upstream Agent | What Agent 4 consumes |
|---|---|
| Agent 1 (Document Intelligence) | Contract obligations, liability structure, TUPE implications, ITT pricing schedule structure |
| Agent 2 (Market Intelligence) | Incumbent pricing, competitor benchmarks, Contracts Finder comparable contract values |
| Agent 3 (Strategy & Scoring) | Marks allocation informing effort investment, PWIN scoring data |
| Agent 6 (Solution & Delivery) | Staffing model (SOL-06), transition plan (SOL-07), technology costs, solution architecture inputs |

**Agent 4 outputs feed into:**

| Downstream Agent | What it consumes from Agent 4 |
|---|---|
| Agent 3 (Strategy & Scoring) | Commercial data for PWIN scoring, gate readiness assessment, bid viability verdict |
| Agent 5 (Content Drafting) | Commercial narrative for response drafting — pricing rationale, commercial model description, value-for-money arguments |

**Design note:** Lower AI reduction (37%) reflects genuine need for commercial judgement. AI builds the analytical framework, runs scenarios, and identifies risks. The commercial lead validates assumptions, makes pricing decisions, and negotiates with partners. The practitioner described it as "building something for a commercial finance person to play with and complete."

---

*Agent 4: Commercial & Financial Modelling | v1.0 | April 2026 | PWIN Architect*
*9 skills (7 productivity, 2 insight) | ~39 methodology tasks | 37% avg effort reduction*
