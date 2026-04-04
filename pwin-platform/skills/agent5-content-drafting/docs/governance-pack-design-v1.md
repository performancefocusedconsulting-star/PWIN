# Governance Pack Skill — Design Specification v1.0

**Date:** 2026-04-04
**Status:** Design complete, awaiting build
**Skill:** `governance-packs.yaml` (Agent 5 — Content & Response Drafting)

---

## 1. Purpose

Governance packs are the decision artefacts presented to senior leadership at bid governance gates. They enable pursue/condition/kill decisions at each stage of the bid lifecycle. This skill assembles gate-specific packs from live pursuit data and workstream documents, producing a professional-quality output that would previously require weeks of manual assembly by the bid team.

### 1.1 The Problem This Solves

Most organisations suffer from two governance failures:

1. **Early gates are rubber stamps.** Gates 0-2 lack sufficient structured evidence to challenge the "let it through" default. Opportunities that should die early survive to Gate 4, consuming months of team effort and significant bid cost before being killed.

2. **Late gate packs take weeks to assemble.** Gate 4 packs require synthesis across every workstream — commercial, legal, operations, transition, technology, HR, risk. The assembly effort (gathering data, formatting slides, iterating through reviews) dominates the timeline, not the analysis itself.

PWIN addresses both by:
- Making early gate packs evidence-rich through Qualify integration, forcing better decisions earlier
- Automating pack assembly from structured workstream outputs, reducing weeks to hours
- Ensuring every pack follows the methodology — no missing sections, no buried bad news

### 1.2 Position in Product Lifecycle

```
Qualify → Strategy → Execution → Governance Packs
                                   ↑
                          Consumes data from all three
                          + workstream documents
                          + financial models
```

The governance pack is a cross-cutting output. It does not belong to a single product — it synthesises across the pursuit lifecycle.

---

## 2. Architecture Decisions

### 2.1 One Skill, Gate-Tier-Aware

A single `governance-packs.yaml` skill handles all gate types. The `gateName` input parameter determines which gate tier template is applied. This avoids skill proliferation for what is fundamentally the same operation: assemble a pack for gate X from pursuit data.

The AI within the skill selects the correct template, sections, and data requirements based on the gate tier.

### 2.2 Three Gate Tiers

Gate packs cluster into three tiers based on scope and complexity, not the specific gate number (which varies by client methodology):

| Tier | Gates | T-Shirt Size | Purpose | Typical Length |
|------|-------|-------------|---------|----------------|
| **Qualification** | 0, 1, 2 | Small | Should we pursue? Is this real? Can we win? | 5-10 pages |
| **Solution** | 3 | Medium | Do we have a winning proposition? Are we resourced? | 15-20 pages |
| **Submission** | 4 | Large | Full approval to submit. Complete commercial, legal, operational picture. | 30-40 pages |
| **Contract** | 5 | Delta | What changed since Gate 4? Ready to sign? | 10-15 pages |

Note: Contract tier (Gate 5) is a delta pack — it references the Gate 4 pack and presents only changes, final negotiation outcomes, and transition readiness. It does not repeat the full Gate 4 content.

### 2.3 Template Knowledge in Platform Knowledge Files

Pack section templates, gate definitions, risk frameworks, and functional sign-off matrices are stored as platform knowledge files (JSON), not embedded in the skill YAML. This makes them:

- **Client-configurable** — different organisations have different gate names, IC trigger thresholds, functional sign-off roles, and risk appetite frameworks
- **Maintainable** — methodology updates don't require skill code changes
- **Served via MCP tools** — consistent with existing platform knowledge pattern

### 2.4 Three Content Modes

Every section in a governance pack operates in one of three content modes. The skill must handle each differently:

| Mode | What It Is | AI Approach | Accuracy Risk |
|------|-----------|-------------|---------------|
| **Structured data** | Financials, PI tables, headcount, dates, RAG statuses, percentages | Extract from platform/documents → place in template verbatim | Hallucinated or misplaced numbers |
| **Contextual narrative** | Framing, positioning, synthesis, recommendations, risk commentary | Synthesise across workstream conclusions → frame for audience and gate purpose | Mischaracterised context, softened qualifications |
| **Visual reference** | Solution diagrams, delivery structures, timelines, competitive positioning charts | Reference existing artefacts produced during the bid → embed or link | Wrong version, stale visual |

Key principle: **Structured data is extract-and-place. Contextual narrative is synthesis with preserved tone. Visuals are referenced, not generated.**

### 2.5 Output Format

**Primary output: HTML → PDF**

- Landscape orientation, slide-sized pages (`@media print` with `page-break-before`)
- One concept per page, mirroring the PowerPoint convention governance boards expect
- Full CSS control: dashboard layouts, multi-column grids, RAG colour coding, financial tables
- Midnight Executive visual identity (consistent with other PWIN products)
- Print-to-PDF or headless render (Puppeteer/wkhtmltopdf) for distribution

This produces a PDF indistinguishable from a PowerPoint-origin document, without fighting Office XML generation. Recipients cannot tell the difference.

PowerPoint native output is deferred. If required by client demand, it becomes an Office 365 export layer concern — separate from the pack assembly skill.

---

## 3. Section Architecture

### 3.1 Common Pack Structure

Derived from analysis of real governance packs (Capita Group CRC, Capita Divisional CRC, Serco IC Gate 4, Serco Business Lifecycle methodology):

| # | Section | Content Mode | Present In |
|---|---------|-------------|------------|
| 1 | **Purpose & Decisions Required** | Narrative | All tiers |
| 2 | **Deal Dashboard** | Structured data | All tiers |
| 3 | **Actions from Previous Gate** | Structured data + narrative | Solution, Submission, Contract |
| 4 | **Opportunity & Solution Summary** | Narrative | All tiers |
| 5 | **Qualification Assessment** | Structured data + narrative | Qualification, Solution |
| 6 | **Win Strategy & Competitive Position** | Narrative | Solution, Submission |
| 7 | **Evaluation Criteria & Score-to-Win** | Structured data + narrative | Solution, Submission |
| 8 | **Financial Summary (P&L, Margin, NPV)** | Structured data | Solution, Submission, Contract |
| 9 | **Risk & Sensitivity Analysis (Tornado)** | Structured data + narrative | Submission, Contract |
| 10 | **Delivery Solution** | Narrative + visual reference | Submission |
| 10a | — Partners & Subcontractors | Narrative | Submission |
| 10b | — People | Structured data + narrative | Submission |
| 10c | — Technology | Narrative + visual reference | Submission |
| 10d | — Assets | Structured data + narrative | Submission |
| 10e | — Mobilisation, Transition & Transformation | Narrative + visual reference | Submission |
| 10f | — Social Value & Environment | Narrative | Submission |
| 11 | **Legal & Commercial Terms** | Structured data (RAG grid) | Submission, Contract |
| 12 | **Performance Mechanism** | Structured data (PI table) | Submission |
| 13 | **Payment Mechanism** | Structured data + narrative | Submission |
| 14 | **Price-to-Win & Competitive Analysis** | Narrative | Solution, Submission |
| 15 | **Bid Cost & Resource Status** | Structured data | All tiers |
| 16 | **Recommendation & Approval Sought** | Narrative | All tiers |
| 17 | **Functional Sign-Off Control Sheet** | Structured data | Submission, Contract |
| 18 | **Appendices (Tornado Detail, etc.)** | Mixed | Submission |

### 3.2 Qualification Tier (Gates 0-2) — Detail

The qualification tier pack is deliberately lean but evidence-rich. Its primary data source is PWIN Qualify output. The purpose is to force an evidence-based pursue/no-pursue decision rather than the typical "insufficient information to kill it" default that lets weak opportunities survive.

**Sections:**
1. Purpose & Decisions Required
2. Deal Dashboard (client, TCV, term, sector, deal type, procurement route)
3. Opportunity Summary (client requirement, services, strategic fit narrative)
4. Qualification Assessment — **centrepiece section**
   - PWIN score and category breakdown (from Qualify)
   - AI assurance review findings (from Qualify — the challenges to over-scoring)
   - Evidence gaps explicitly flagged: "the team has asserted X without supporting evidence"
   - Pursue/condition/walk-away recommendation from Qualify
5. Competitive Landscape (known competitors, initial positioning)
6. Bid Cost Estimate & Resource Requirement
7. IC Trigger Assessment (does this opportunity meet thresholds requiring IC involvement?)
8. Recommendation & Approval Sought

**Key design principle:** The qualification pack should make it *harder* to rubber-stamp a weak opportunity. The AI explicitly surfaces where evidence is thin and where assertions are unsubstantiated. If the team says "strong customer relationships" but Qualify scored customer intimacy at 2/5, the pack flags the contradiction.

### 3.3 Solution Tier (Gate 3) — Detail

Gate 3 confirms the proposition after ITT receipt. The pack validates that the opportunity still merits pursuit now that client requirements are known in detail, and that the solution approach is credible.

**Sections:**
1. Purpose & Decisions Required
2. Deal Dashboard (updated with ITT specifics)
3. Actions from Previous Gate (Gate 2 actions: open/closed with evidence)
4. Opportunity & Solution Summary (evolved from Gate 2 with ITT detail)
5. Qualification Reassessment (has PWIN score changed since Gate 2? Why?)
6. Win Strategy & Win Themes (from Win Strategy product)
7. Evaluation Criteria & Score-to-Win Analysis
8. Preliminary Financial Summary (initial P&L, target margins)
9. Competitive Analysis (updated with ITT intelligence)
10. Key Risks & Mitigations (top 10, not full tornado)
11. Teaming & Subcontractor Strategy
12. Bid Budget & Resource Plan (detailed, against Gate 2 estimate)
13. Recommendation & Approval Sought

### 3.4 Submission Tier (Gate 4) — Detail

The heavyweight pack. Full commercial, legal, operational, and delivery picture. Board approves submission of a binding tender.

**Sections:** All 18 sections from the common structure (Section 3.1 above).

**Specific requirements derived from reference packs:**

- **Financial model** is presented, not generated. The skill narrates the P&L, highlights key ratios, and flags anomalies. The model itself is produced by the commercial workstream.
- **Risk tornado** follows the standard five-column format per risk category:

| Category | Risk in Base Case | Practical Worst Case | Realistic Downside | Realistic Upside | Practical Best Case |
|----------|------------------|---------------------|-------------------|-----------------|-------------------|
| Description | £ costed risk | £ impact + rationale | £ impact + rationale | £ impact + rationale | £ impact + rationale |

Each tornado item includes: exposure amount, probability weighting, narrative rationale, and mitigation status.

- **Legal terms grid** follows the structured tile format: one tile per legal topic (liability caps, termination, performance regime, payment, TUPE, IP, insurance, data/GDPR, change in law, subcontractors, governing law, etc.) with current position and negotiation strategy.
- **PI assessment table** per performance indicator: ASL target, solution designed to achieve (Y/N), SFP calculation acceptable (Y/N), compliant at submission (Y/N), subcontractor flow-down (Y/N), RAG status, narrative.
- **Functional sign-off control sheet**: one row per functional area (Finance, Commercial, Legal, Operations, Transformation, Risk, HR, Treasury, Insurance, Tax, Property, Pensions, Procurement, IT Security), with named signatory and sign-off date.

### 3.5 Contract Tier (Gate 5) — Detail

Delta pack from Gate 4. Focuses on: what changed in final negotiations, transition readiness, contract signature authority.

**Sections:**
1. Purpose & Decisions Required
2. Deal Dashboard (final, post-negotiation)
3. Actions from Gate 4 (all must be closed or explicitly accepted)
4. Material Changes Since Gate 4 (scope, price, terms, risk profile)
5. Final Financial Position (delta from Gate 4 model)
6. Final Risk Position (updated tornado for material changes only)
7. Contract Terms — Final Position (delta from Gate 4 legal grid)
8. Transition Readiness (director appointed, team mobilised, budget confirmed)
9. Subcontractor Readiness (conditions precedent met)
10. Contract Signature Authority & Mechanics
11. Functional Sign-Off Control Sheet (re-confirmed post-negotiation)

---

## 4. Platform Knowledge Files

Four new JSON files under `~/.pwin/platform/governance/`:

### 4.1 `governance_gate_definitions.json`

Defines the gate framework, tier mapping, and IC trigger criteria.

```json
{
  "gates": [
    {
      "gate_number": 0,
      "name": "Opportunity Identified",
      "tier": "qualification",
      "decision_type": "pursue_no_pursue",
      "description": "Internal qualification — is this opportunity real and aligned to strategy?",
      "mandatory_prerequisites": [
        "Market intelligence reviewed",
        "Strategic fit confirmed",
        "High-level risks identified"
      ]
    }
  ],
  "ic_trigger_criteria": {
    "acv_threshold": 25000000,
    "tcv_threshold": 100000000,
    "bid_cost_threshold": 1000000,
    "capex_threshold": 500000,
    "contract_length_years_threshold": 10,
    "equity_investment": true,
    "new_geography": true,
    "new_capability": true,
    "jv_or_partnership": true,
    "high_inherent_risk": true
  },
  "tier_definitions": {
    "qualification": { "gates": [0, 1, 2], "t_shirt": "small" },
    "solution": { "gates": [3], "t_shirt": "medium" },
    "submission": { "gates": [4], "t_shirt": "large" },
    "contract": { "gates": [5], "t_shirt": "delta" }
  }
}
```

### 4.2 `governance_pack_templates.json`

Defines the section structure per gate tier, including content mode and data sources for each section.

Structure: tier → sections[] → { id, title, content_mode, data_sources[], instructions, required }

### 4.3 `governance_risk_framework.json`

Defines the risk tornado format, severity scales, probability weightings, and standard risk categories.

```json
{
  "tornado_columns": [
    "practical_worst_case",
    "realistic_downside",
    "base_case",
    "realistic_upside",
    "practical_best_case"
  ],
  "probability_weights": {
    "practical_worst_case": 0.05,
    "realistic_downside": 0.20,
    "base_case": 0.50,
    "realistic_upside": 0.20,
    "practical_best_case": 0.05
  },
  "standard_categories": [
    "volumes",
    "subcontractor",
    "change_in_law",
    "service_credits",
    "technology",
    "headcount",
    "redundancy",
    "transition",
    "pricing_indexation",
    "fx_risk",
    "asset_condition",
    "performance_regime"
  ]
}
```

### 4.4 `governance_signoff_matrix.json`

Defines functional sign-off areas, typical role titles, and what each area is accountable for reviewing.

```json
{
  "functional_areas": [
    {
      "area": "Finance",
      "role_title": "Divisional FD / Group Finance",
      "accountable_for": "Deal financials, bid model, P&L, NPV/IRR, sensitivity analysis",
      "required_at_tiers": ["solution", "submission", "contract"]
    },
    {
      "area": "Commercial",
      "role_title": "Divisional Commercial Director",
      "accountable_for": "Commercial model, pricing strategy, ICAs, payment mechanism",
      "required_at_tiers": ["solution", "submission", "contract"]
    }
  ]
}
```

---

## 5. Data Requirements by Tier

### 5.1 Qualification Tier

| Data | Source | Required/Optional |
|------|--------|-------------------|
| Pursuit metadata (client, TCV, term, sector) | Platform — shared.json | Required |
| PWIN score and category breakdown | Platform — qualify.json | Required |
| AI assurance review findings | Platform — qualify.json | Required |
| Competitive landscape (known competitors) | Workstream document or Win Strategy | Optional |
| Bid cost estimate | Workstream document | Required |
| IC trigger assessment | Platform — computed from pursuit metadata vs thresholds | Required |

### 5.2 Solution Tier

All qualification data, plus:

| Data | Source | Required/Optional |
|------|--------|-------------------|
| ITT document analysis | Platform — bid_execution.json (ITT ingestion) | Required |
| Win strategy and themes | Platform — win_strategy.json | Required |
| Evaluation criteria and weightings | Workstream document (evaluation framework) | Required |
| Preliminary financial model | Workstream document (Excel/structured output) | Required |
| Teaming and subcontractor strategy | Workstream document | Required |
| Updated competitive analysis | Workstream document | Required |
| Top 10 risks | Platform — bid_execution.json (risk register) | Required |
| Gate 2 actions and status | Platform — governance history | Required |

### 5.3 Submission Tier

All solution data, plus:

| Data | Source | Required/Optional |
|------|--------|-------------------|
| Full financial model (P&L, cashflow, balance sheet) | Workstream document (Excel) | Required |
| Risk tornado (per category) | Workstream document (commercial/risk) | Required |
| Legal terms grid (per clause area) | Workstream document (legal) | Required |
| PI assessment table | Workstream document (operations) | Required |
| Delivery solution — per workstream | Workstream documents (ops, tech, HR, MTT, assets, social value) | Required |
| Subcontractor status and gap analysis | Workstream document (commercial/procurement) | Required |
| Payment mechanism summary | Workstream document (commercial) | Required |
| Price-to-win analysis | Workstream document (commercial/BD) | Required |
| Red team review outcomes | Workstream document (bid management) | Required |
| Bid cost actuals vs budget | Platform — bid_execution.json | Required |
| Functional sign-offs | Platform — governance workflow | Required |

### 5.4 Contract Tier

Submission data (by reference), plus:

| Data | Source | Required/Optional |
|------|--------|-------------------|
| Gate 4 pack (reference) | Platform — governance history | Required |
| Negotiation outcomes (delta from Gate 4) | Workstream document (commercial/legal) | Required |
| Final financial position (delta) | Workstream document (commercial) | Required |
| Transition readiness assessment | Workstream document (MTT lead) | Required |
| Subcontractor conditions precedent | Workstream document (procurement) | Required |

---

## 6. Accuracy & Validation

### 6.1 Structured Data Accuracy

- **Extract-and-place principle**: for quantitative data (financials, margins, headcount, PI targets, risk exposures), the AI extracts exact values from defined fields in structured documents and places them into defined positions in the pack template. No inference, no rounding, no interpretation.
- **Cross-reference validation**: before output, the skill validates internal consistency:
  - Does TCV = sum of annual revenue values?
  - Do margin percentages match the £ values / revenue?
  - Are dates internally consistent (submission deadline after pack date)?
  - Do headcount numbers reconcile between people section and financial model?
- **Staleness flags**: if any source document is older than a configurable threshold (default: 7 days for submission tier), the pack flags it with a warning on the relevant section.

### 6.2 Contextual Narrative Accuracy

- **Preserved tone and qualification**: the AI must preserve the tone and caveats from source documents. If a workstream document says "significant gap risk remains," the pack must not soften this to "some residual risk exists." The system prompt explicitly instructs: preserve qualifications, caveats, and assumptions alongside every data point.
- **Source attribution**: every narrative section includes a metadata reference to the source workstream document(s) from which the synthesis was drawn. Not visible in the pack output, but available as a validation layer.
- **No editorialising on numbers**: the AI frames and contextualises financial data but does not opine on whether margins are acceptable. That is the governance board's decision.

### 6.3 Human-in-the-Loop

The skill produces a draft pack. The bid manager reviews before distribution to the governance board. This is not a limitation — it is governance. The value is reducing review time from days to hours, not eliminating review.

The draft includes a cover page marked "DRAFT — For Bid Director Review" with:
- Pack generation timestamp
- Source document versions used
- Any validation warnings or staleness flags
- Sections where data was unavailable (marked as "[AWAITING INPUT — {workstream}]")

---

## 7. Skill Design

### 7.1 Input Parameters

```yaml
input:
  required:
    - pursuitId
    - gateName          # e.g. "gate-4" or "submission-review"
  optional:
    - gateTier          # override: "qualification" | "solution" | "submission" | "contract"
    - includeAppendices # boolean, default true for submission tier
    - draftWatermark    # boolean, default true
```

`gateTier` can be explicitly provided or inferred from `gateName` via the gate definitions knowledge file.

### 7.2 System Prompt Structure

The system prompt contains:
1. Agent identity and role
2. The three content modes and how to handle each
3. Pack assembly principles (from Section 1 — never bury bad news, preserve qualifications, evidence over assertion)
4. Output formatting rules (landscape pages, one concept per page, Midnight Executive palette)
5. Validation checklist to run before output

The system prompt does NOT contain section templates — those come from the platform knowledge files loaded as context.

### 7.3 User Prompt Structure

The user prompt assembles:
1. Gate tier template (from `governance_pack_templates.json`)
2. Pursuit data (from platform — shared.json, qualify.json, bid_execution.json, win_strategy.json)
3. Workstream document contents (from platform data store or referenced documents)
4. Risk framework (from `governance_risk_framework.json`)
5. Functional sign-off matrix (from `governance_signoff_matrix.json`)
6. IC trigger criteria assessment (computed from pursuit metadata)

### 7.4 Write Tools

```yaml
write_tools:
  - generate_report_output    # HTML pack output
  - update_governance_record  # log pack generation in pursuit governance history
```

---

## 8. Visual Design

### 8.1 Output Format

HTML document designed for PDF rendering. Landscape A4, slide-sized pages.

### 8.2 Page Types

| Page Type | Layout | Used For |
|-----------|--------|----------|
| **Title page** | Centred, minimal | Pack cover with pursuit name, gate, date, classification |
| **Dashboard** | Multi-metric grid | Deal dashboard, IC trigger assessment |
| **Narrative** | Two-column or full-width prose | Executive summary, solution narrative, recommendations |
| **Data table** | Full-width structured table | P&L, PI assessment, legal terms grid, sign-off sheet |
| **Tornado** | Horizontal bar chart + table | Risk & sensitivity analysis |
| **RAG matrix** | Grid with colour-coded cells | Compliance assessment, workstream status |
| **Action tracker** | Table with status indicators | Previous gate actions, outstanding items |

### 8.3 Visual Identity

Consistent with PWIN product family:
- Midnight Executive palette (deep navy backgrounds, gold accents)
- Cormorant Garamond for display headings and key numbers
- DM Mono for data labels and table content
- DM Sans for body narrative
- Structured information hierarchy with clear section breaks

---

## 9. Commercial Value

### 9.1 Early Gate Value (Qualification Tier)

The primary commercial value is not time saved — it is **decisions improved**. By making early gate packs evidence-rich through Qualify integration, PWIN enables organisations to kill weak opportunities at Gate 2 instead of Gate 4. The cost saving is the 3-6 weeks of bid team effort that would have been invested in a doomed pursuit.

Conservative estimate: if 20% of opportunities that currently pass Gate 2 should have been killed, and average Gate 3-4 bid cost is £200K-£1M, the governance pack skill pays for the entire platform engagement on the first kill.

### 9.2 Late Gate Value (Submission Tier)

Time compression: Gate 4 pack assembly reduced from 2-3 weeks to 2-3 days (draft generation in hours, human review and refinement over 1-2 days).

Quality improvement: every pack follows methodology, every section present, every risk category assessed, no missing sign-offs.

Consistency: governance boards see the same structure every time, enabling faster decision-making through familiarity.

### 9.3 Continuous Governance Value

Because PWIN tracks pursuit data throughout the lifecycle, the pack is not a point-in-time assembly — it is a snapshot of continuously maintained data. The bid manager can generate a governance pack at any point, not just at formal gates. This enables:
- Ad-hoc governance reviews when risk profile changes
- Board pre-reads generated automatically ahead of scheduled gates
- Portfolio-level governance dashboards aggregating pack data across pursuits

---

## 10. Build Sequence

| Step | Deliverable | Dependencies |
|------|------------|--------------|
| 1 | Design specification (this document) | None — complete |
| 2 | Platform knowledge files (4 JSON files) | Reference documents analysed |
| 3 | MCP tools to serve governance knowledge | Platform knowledge files |
| 4 | Rebuilt `governance-packs.yaml` skill | Knowledge files + MCP tools |
| 5 | HTML/CSS template for pack output | Visual identity system |
| 6 | Test with sample pursuit data | All above |

---

## 11. Open Questions

1. **Client onboarding**: How are governance knowledge files customised per client? Is this a one-time setup during onboarding, or does the platform ship with a sensible default that clients adapt?

2. **Workstream document ingestion**: How do workstream lead documents get into the platform? Are they uploaded as files, or does the AI-assisted workflow write structured data directly to the platform data store?

3. **Financial model integration**: The financial model (Excel) is the hardest artefact to integrate. Options: (a) structured JSON export from Excel, (b) AI reads Excel directly, (c) commercial lead enters key figures into platform. Which approach for V1?

4. **Visual artefacts**: Solution diagrams, delivery structure charts, and timeline Gantts are referenced in the pack. Where are these stored? Are they generated during the bid workflow and uploaded to the platform?

5. **Governance history**: Should the platform maintain a governance history per pursuit (gate dates, decisions, conditions, action items) that feeds into the "actions from previous gate" section? This would require new data model entities.

---

## 12. Reference Documents

The following documents informed this design:

| Document | Type | Source | Key Patterns Extracted |
|----------|------|--------|----------------------|
| Group CRC — MOD FSDC (2019) | Real Group CRC pack, £364m MOD deal | Capita | Full pack structure, tornado risk format, sign-off control sheet, financial presentation |
| CM Divisional CRC Pack — lite | Divisional CRC template with placeholders | Capita | Template structure, section headings, P&L layout |
| IC Gate 4 Pack — London Cycle Hire | Real IC Gate 4 pack, £307m TfL deal | Serco | IC trigger dashboard, ITPD strategy, negotiation register, delivery solution (7 sections), legal terms grid, PI assessment table, payment/performance mechanism, competitive analysis |
| Business Lifecycle & Bid Methodology v4 | Governance framework and methodology training | Serco | Gate 0-5 definitions, mandatory activities per gate, qualification criteria, BLRT accountability, solution hats, red team review |
| Growth Hub Sales Accelerator | Sales pipeline methodology | Capita | Stage-gate alignment, governance review integration points, Revenue Storm tool mapping |
