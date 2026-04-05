# Governance Pack — Page Design Workbook

**Purpose:** Define the exact page sequence, layout, and data presentation for each gate tier. Complete this workbook tier by tier — it will drive the HTML template generation and skill assembly logic.

---

## How to Use This Workbook

For each gate tier, fill in the page table. Each row is one page (one slide) in the output PDF.

**Column guide:**

| Column | What to Enter |
|--------|---------------|
| **Page #** | Sequential page number |
| **Page Title** | The heading shown on the page |
| **Page Type** | Pick from: `Title`, `Dashboard`, `Narrative`, `Data Table`, `Tornado`, `RAG Matrix`, `Action Tracker`, `Mixed` |
| **Layout** | How the page is laid out. Pick from: `Full-width`, `Two-column (50/50)`, `Two-column (60/40)`, `Two-column (40/60)`, `Grid (2x2)`, `Grid (3x1)`, `Grid (4x1)`, `Header + table`, `Header + cards` |
| **Data Displayed** | List the specific data items shown on this page. Be explicit — e.g. "Client name, TCV, ACV, Term, Sector, Deal type" not just "deal info" |
| **Visualisation** | How each data item is presented. Pick from: `Metric card` (big number + label), `Table` (rows/columns), `Prose paragraph`, `Bullet list`, `RAG badge`, `RAG grid`, `Bar chart`, `Checklist`, `Status badges`, `Numbered list`, `Quote block` (for caveats/flags) |
| **Data Source** | Where the data comes from. Use: `shared.json`, `qualify.json`, `bid_execution.json`, `win_strategy.json`, `gate_definitions`, `workstream:{name}` (e.g. `workstream:legal`, `workstream:commercial`), `governance_history` |
| **Notes** | Any special instructions — e.g. "always show even if data missing", "flag contradictions", "RAG colour the whole row", "this page only appears if X" |

---

## Tier 1: Qualification Pack (Gates 0–2)

*Smallest pack. Purpose: evidence-based pursue/no-pursue decision. Primary audience: divisional leadership or BLRT.*

| Page # | Page Title | Page Type | Layout | Data Displayed | Visualisation | Data Source | Notes |
|--------|-----------|-----------|--------|----------------|---------------|-------------|-------|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |
| 9 | | | | | | | |
| 10 | | | | | | | |

**Add more rows as needed. Delete unused rows.**

### Qualification Tier — Design Questions

1. Should the PWIN Qualify assessment be one page or two? (scores summary + AI assurance findings separately?)
2. Is there a "decisions required" summary page at the end, or does the recommendation page cover this?
3. Do you want an IC trigger assessment as its own page, or embedded in the dashboard?
4. Any pages that should only appear conditionally? (e.g. competitive landscape only if intelligence exists)

---

## Tier 2: Solution Pack (Gate 3)

*Medium pack. Purpose: confirm the proposition post-ITT receipt. Primary audience: BLRT + solution reviewers.*

| Page # | Page Title | Page Type | Layout | Data Displayed | Visualisation | Data Source | Notes |
|--------|-----------|-----------|--------|----------------|---------------|-------------|-------|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |
| 9 | | | | | | | |
| 10 | | | | | | | |
| 11 | | | | | | | |
| 12 | | | | | | | |
| 13 | | | | | | | |
| 14 | | | | | | | |
| 15 | | | | | | | |
| 16 | | | | | | | |
| 17 | | | | | | | |
| 18 | | | | | | | |
| 19 | | | | | | | |
| 20 | | | | | | | |

**Add more rows as needed. Delete unused rows.**

### Solution Tier — Design Questions

1. Should the "actions from previous gate" page come before or after the deal dashboard?
2. How detailed should the preliminary financial summary be at Gate 3? One page with key metrics, or a full P&L table?
3. Win strategy — one page with themes + positioning, or separate pages for themes vs competitive analysis?
4. Is the evaluation criteria / score-to-win a table, a visual matrix, or narrative?
5. Top 10 risks at Gate 3 — table format or individual risk cards?

---

## Tier 3: Submission Pack (Gate 4)

*Heavyweight pack. Purpose: full approval to submit binding tender. Primary audience: Investment Committee / Group CRC.*

| Page # | Page Title | Page Type | Layout | Data Displayed | Visualisation | Data Source | Notes |
|--------|-----------|-----------|--------|----------------|---------------|-------------|-------|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |
| 9 | | | | | | | |
| 10 | | | | | | | |
| 11 | | | | | | | |
| 12 | | | | | | | |
| 13 | | | | | | | |
| 14 | | | | | | | |
| 15 | | | | | | | |
| 16 | | | | | | | |
| 17 | | | | | | | |
| 18 | | | | | | | |
| 19 | | | | | | | |
| 20 | | | | | | | |
| 21 | | | | | | | |
| 22 | | | | | | | |
| 23 | | | | | | | |
| 24 | | | | | | | |
| 25 | | | | | | | |
| 26 | | | | | | | |
| 27 | | | | | | | |
| 28 | | | | | | | |
| 29 | | | | | | | |
| 30 | | | | | | | |
| 31 | | | | | | | |
| 32 | | | | | | | |
| 33 | | | | | | | |
| 34 | | | | | | | |
| 35 | | | | | | | |
| 36 | | | | | | | |
| 37 | | | | | | | |
| 38 | | | | | | | |
| 39 | | | | | | | |
| 40 | | | | | | | |

**Add more rows as needed. Delete unused rows.**

### Submission Tier — Design Questions

1. The Capita CRC and Serco IC packs both lead with purpose/agenda then deal dashboard. Same here, or executive summary first?
2. Financial section — how many pages? The Capita CRC had: P&L (1 page), Balance Sheet (1), Cashflow (1), NPV/IRR/Payback (1), Sensitivity (1) = 5 pages. The Serco IC had: P&L + price walk + sensitivities = 3 pages. What level of financial detail?
3. Risk tornado — one summary page + one page per risk category (like Capita CRC), or condensed to summary + top risks only?
4. Delivery solution — the Serco IC had 7 sub-sections (partners, people, technology, assets, MTT, social value, plus service architecture). One page per sub-section, or combine some?
5. Legal terms — the Serco IC used a single dense grid page covering all clause areas. Same approach, or one page per topic?
6. Performance indicators — one table page for all PIs, or split operational PIs and system PIs across two pages?
7. Price-to-win / competitive — one page or two?
8. Where does the sign-off control sheet sit — last page, or immediately after the recommendation?
9. Should there be an appendix section for supporting detail (full tornado breakdowns, full PI tables)?

---

## Tier 4: Contract Pack (Gate 5)

*Delta pack. Purpose: authority to sign contract. Primary audience: same as Gate 4 plus contract signatories.*

| Page # | Page Title | Page Type | Layout | Data Displayed | Visualisation | Data Source | Notes |
|--------|-----------|-----------|--------|----------------|---------------|-------------|-------|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |
| 9 | | | | | | | |
| 10 | | | | | | | |
| 11 | | | | | | | |
| 12 | | | | | | | |
| 13 | | | | | | | |
| 14 | | | | | | | |
| 15 | | | | | | | |

**Add more rows as needed. Delete unused rows.**

### Contract Tier — Design Questions

1. Should every page explicitly reference the Gate 4 position and show the delta, or just present the final state?
2. Transition readiness — one page with a checklist, or detailed with Gantt/timeline reference?
3. Does the board need to see the full updated sign-off sheet, or just the areas that re-signed?

---

## Visual Reference

### Available Page Types

| Type | Best For | Example |
|------|----------|---------|
| **Title** | Cover page, section dividers | Pursuit name, gate, date, classification |
| **Dashboard** | Key metrics at a glance | Grid of metric cards with big numbers |
| **Narrative** | Explanations, strategy, recommendations | Prose with optional sidebar cards |
| **Data Table** | Financial data, structured comparisons | P&L, PI assessment, sign-off sheet |
| **Tornado** | Risk sensitivity analysis | Horizontal bars + scenario table |
| **RAG Matrix** | Status assessment grids | Legal terms grid, compliance matrix |
| **Action Tracker** | Gate actions, outstanding items | Table with status badges |
| **Mixed** | Combination of data + narrative | Dashboard top + narrative bottom |

### Available Layouts

| Layout | Description |
|--------|-------------|
| **Full-width** | Single column, edge to edge |
| **Two-column (50/50)** | Equal split |
| **Two-column (60/40)** | Main content left, supporting right |
| **Two-column (40/60)** | Supporting left, main content right |
| **Grid (2x2)** | Four equal quadrants |
| **Grid (3x1)** | Three equal columns |
| **Grid (4x1)** | Four equal columns (dashboard metrics) |
| **Header + table** | Title/summary top, full-width table below |
| **Header + cards** | Title/summary top, metric cards below |

### Available Visualisations

| Visualisation | Best For | Example |
|---------------|----------|---------|
| **Metric card** | Single KPI | Big "£307m" with "Total Contract Value" label |
| **Table** | Structured multi-row data | P&L, risk register, PI assessment |
| **Prose paragraph** | Context, narrative, strategy | Executive summary, opportunity description |
| **Bullet list** | Key points, decisions required | Numbered decisions for the board |
| **RAG badge** | Single status indicator | Green dot next to a line item |
| **RAG grid** | Multi-item status matrix | Legal terms with coloured cells |
| **Bar chart** | Comparative values | Tornado risk bars |
| **Checklist** | Completion tracking | Mandatory prerequisites |
| **Status badges** | Action/item status | "Closed" / "Open" / "Overdue" pills |
| **Numbered list** | Ordered items, priorities | Approval items sought |
| **Quote block** | Caveats, warnings, flags | "[ASSERTION — no supporting evidence]" |

---

## Worked Example — Qualification Tier (for reference)

*This is a starter example. Override or delete it entirely based on your judgement.*

| Page # | Page Title | Page Type | Layout | Data Displayed | Visualisation | Data Source | Notes |
|--------|-----------|-----------|--------|----------------|---------------|-------------|-------|
| 1 | [Gate Name] — [Client Name] | Title | Full-width | Pursuit name, client, gate, date, TCV headline, classification | Centred display text | shared.json | Draft watermark if not final |
| 2 | Deal Dashboard | Dashboard | Grid (4x1) + Grid (4x1) | Row 1: Client, TCV, ACV, Term. Row 2: Sector, Deal Type, Procurement Route, Submission Deadline | Metric cards | shared.json | IC triggers flagged in red if met |
| 3 | Opportunity Summary | Narrative | Two-column (60/40) | Left: what client is buying, why now, services in scope. Right: key dates timeline, procurement stage | Prose + bullet list | shared.json, qualify.json | One page max |
| 4 | Qualification Assessment | Mixed | Two-column (50/50) | Left: PWIN score (large), 6 category scores as horizontal bars. Right: AI assurance findings as bullet list | Metric card + bar chart + bullet list | qualify.json | Flag evidence gaps with quote blocks |
| 5 | Competitive Landscape | Narrative | Full-width | Known competitors, positioning assessment, differentiators | Prose + table (competitor comparison) | win_strategy.json | Conditional — only include if intelligence exists |
| 6 | Bid Cost & Resource | Data Table | Header + table | Bid cost estimate, cost to Gate 4, key roles required, timeline | Table + metric cards | bid_execution.json | |
| 7 | Recommendation | Narrative | Two-column (60/40) | Left: recommendation (pursue/condition/walk), rationale, conditions if any. Right: decisions required (numbered), approval sought | Prose + numbered list | qualify.json | Always the final page before sign-off |
