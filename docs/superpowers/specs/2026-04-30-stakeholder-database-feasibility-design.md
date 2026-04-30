---
title: Stakeholder database — feasibility investigation design
date: 2026-04-30
status: draft
type: investigation-spec
related:
  - C:/Users/User/Documents/Obsidian Vault/wiki/platform/stakeholder-data-layer-architecture.md
  - C:/Users/User/Documents/Obsidian Vault/wiki/actions/pwin-stakeholder-canonical-layer.md
  - C:/Users/User/Documents/GitHub/PWIN/docs/research/2026-04-28-sub-org-intel-sources.md
---

# Stakeholder database — feasibility investigation design

## Why this exists

A stakeholder canonical layer has been outlined in two wiki documents (the architecture note and the action). The outline reaches roughly 70% of the *thinking* but only 30% of the *specification*: schema named not typed, MCP tools named not signed, ingest mechanism hand-waved, format consistency acknowledged-but-unsolved. Before turning that outline into a buildable spec, we need to know whether the underlying data justifies the build at all.

The lesson from the Find a Tender Service ingest is that data quality only reveals itself when you parse it — paper-quality and real-quality diverge. A pure desk survey of organograms would have missed the Excel-serial dates, the cp1252 encoding, the OpenDocument Spreadsheet quirks, and the 5% sub-organisation dark spot in the four largest ministerial departments. The investigation must include a small live ingest test, not just a documentation review.

## The decision being made

At the end of the investigation, pick one of three verdicts:

- **Build as scoped** — the wide universe (central government + arm's-length bodies + NHS + local government) is good enough across the tiered seniority range to justify the build described in `wiki/actions/pwin-stakeholder-canonical-layer.md`.
- **Build narrower** — a subset of the universe (e.g. central government only) clears the bar. Other parts deferred or dropped.
- **Don't build** — quality is too patchy, too stale, or too inconsistent across the universe for the database to reliably serve buyer-intelligence dossiers, Win Strategy stakeholder mapping, and Qualify context assembly. Use alternative approach (per-pursuit researcher, paid feed, etc.).

## The framing the investigation honours

Three answers from the brainstorming session set the boundary conditions:

| Boundary | Answer | Implication for the investigation |
|---|---|---|
| Universe | Wide-and-broad first, with central government as the value floor | The investigation samples beyond Whitehall (NHS, local government) but treats central government as the must-clear bar |
| Depth of seniority | Working evaluator (Grade 7 / SRO) up to senior executive (DG / Director) | Organograms cap at SCS-1 / Grade 6 — the lower half needs an alternative source regardless of how good organograms turn out to be |
| Currency tolerance | Tiered by seniority — twice-yearly canonical for the durable senior tier; event-driven for the volatile lower tier | The investigation must validate two refresh mechanisms, not one |

## Verdict criteria

The verdict is decided against four criteria. The investigation must produce concrete numbers for each.

| Criterion | Build as scoped | Build narrower | Don't build |
|---|---|---|---|
| **Senior-tier coverage** (DG / Director / 2-star / named SROs) for top-20 priority buyers, measured against the Senior Civil Servant + Grade 6 population implied by Cabinet Office workforce statistics | ≥ 90% named with reporting line | ≥ 90% for central government, < 70% beyond | < 70% even for central government |
| **Working-evaluator coverage** — at least one alternative source per department that names Grade 7 / SRO level individuals with sufficient role detail to be useful (i.e. not just a name in a press story but role and unit) | Yes for ≥ 70% of priority buyers | Central government only | No reliable source for any department |
| **Currency** of the canonical refresh — worst-case publication lag observed across the sampled departments (snapshot date to actual published-on-data.gov.uk date) | ≤ 6 months for the senior tier across the worst-performing sampled department | ≤ 6 months for central government departments, > 12 months for NHS or local government | > 12 months even for central government |
| **Format consistency** across departments and across years (the test is whether one parser can handle all sampled departments with at most one branch per department, and whether year-on-year schema changes are non-breaking) | ≤ 2 distinct organogram formats to parse, no breaking changes year-on-year | 3–5 formats | > 5 formats, or breaking changes year-on-year |

## Investigation structure

Three tracks, run in parallel.

### Track 1 — official organogram quality (live ingest test)

Pull, parse, and characterise the latest organogram from a deliberately spread sample of five departments:

| Department | Why chosen |
|---|---|
| HM Treasury | Small, central, organisationally tidy. Best-case baseline. |
| Ministry of Defence | Large, complex, multiple agencies, historically inconsistent publishing. Worst-case central government. |
| Department for Education | Middle of the road; known sub-organisation dark spot in the FTS data, so a useful comparison point. |
| NHS England | Different publishing regime entirely (NHS ODS, not data.gov.uk organograms). Tests whether the approach generalises beyond Whitehall. |
| Birmingham City Council (or equivalent large unitary) | No organogram regime at all. Tests what local government data even exists. |

For each:

1. Locate the latest organogram (or note its absence and where the gap was confirmed).
2. Parse it. Record: file format, encoding, schema (column names, key fields), quirks, and consistency vs. previous year.
3. Count named senior staff by grade. Compare against department headcount published elsewhere (Cabinet Office workforce statistics) to estimate completeness.
4. Cross-check five randomly-sampled named individuals against an external source (LinkedIn, GOV.UK People page, a recent NAO report) — does the role and unit match reality?
5. Record publication lag (snapshot date vs. actual publication date).

### Track 2 — alternative source survey (spot-check)

Score each candidate source on **coverage, currency, structure, licence**:

| Source | What it gives | Test |
|---|---|---|
| GOV.UK People pages (e.g. `gov.uk/government/organisations/<dept>/about/our-governance`) | Current top-tier SCS by department | Pull 3 departments, compare to organogram |
| GOV.UK appointments / news RSS | Event-driven appointment notices | Subscribe one week, count usable signals |
| Companies House | ALB officers and directors | Pick 3 ALBs, check how many have CH filings naming current officers |
| NAO published reports | Named SROs and accountable officers | Sample 3 recent value-for-money reports, extract named officials |
| Public Accounts Committee witness lists | Named senior civil servants giving evidence | Last 12 months — count distinct names by department |
| Civil Service Jobs | Vacancy listings (role + grade + unit) | Sample one week — useful for spotting backfills |
| LinkedIn (manual search) | Working-evaluator level, otherwise unreachable | Search 3 departments, count Grade 7 commercial leads with public profiles |
| Trade press (Civil Service World, Computer Weekly, Public Sector Executive) | Named officials in news | Last 30 days — count usable named-official mentions |
| Procurement notice contacts in `bid_intel.db` | Named contracting authority contact (`contact_point.name`) | Pull from existing FTS database — what fraction of recent notices have a named contact, what fraction look real |
| Dods People (paid product) | The canonical commercial product for UK government people data | Desk-only — check pricing, coverage claim, free trial availability |

### Track 3 — local government and wider public sector reality check

Local government has no equivalent of the central organogram regime. Track 1 includes one large unitary as a depth probe (does Birmingham publish anything organogram-like in any format?). Track 3 is the breadth complement: across a wider range of councils, is *anything* canonical published centrally, or is coverage only achievable via per-council scrape?

Tasks:

1. Check the Local Government Association data sets — does any single feed give chief officers / Section 151 officers / monitoring officers across all 317 English councils?
2. Sample five council websites of varying size (e.g. Birmingham, Manchester, a London borough, a large rural shire, a small district) — what's published, in what format, with what update cadence?
3. Note the implication for v1: if there is no canonical local-government layer, recommend deferring local-government coverage and building only what central government and ALBs support.

## Output dimensions (what the investigation produces)

For each combination of {sector, source}, record:

- **Coverage** — what fraction of expected senior staff are named
- **Completeness** — which fields are populated (role, grade, unit, reporting line, salary band, appointment date)
- **Currency** — publication lag (snapshot date vs. actual publication date) and refresh cadence (how often the source updates)
- **Consistency** — whether the parsing rules generalise across departments and across years
- **Licence** — Open Government Licence / public domain / paid / scrape-required (with terms-of-service implications)

## Effort budget

Two to three days of focused work:

| Phase | Time |
|---|---|
| Data acquisition (download organogram CSVs, locate alternative source samples) | Half a day |
| Parse and ingest-test the five sample departments | One day |
| Alternative source spot-checks | Half a day |
| Write-up and recommendation | Half a day |

If the parsing reveals worse-than-expected format inconsistency, the investigation should stop and report rather than expand into a full ingest build. The point is to size the build, not to do it.

## Deliverable

A feasibility report at `docs/research/2026-04-30-stakeholder-database-feasibility.md`. Structure:

1. **One-page summary** with the verdict (build as scoped / build narrower / don't build), the recommended scope if "build" or "build narrower", and the headline numbers behind the verdict.
2. **Verdict criteria scorecard** — each of the four criteria scored against the evidence collected, in a table.
3. **Track 1 findings** — the five-department live ingest test, with format / coverage / currency notes per department.
4. **Track 2 findings** — alternative source scorecard.
5. **Track 3 findings** — local government reality check.
6. **Recommended next step** — if the verdict is "build", which alternative sources to wire as the volatile-tier event-driven layer; if "build narrower", which slice; if "don't build", what alternative approach to pursue.
7. **Appendix** — sample parsed records from each ingested organogram, raw scoring inputs.

## Out of scope

- Building any of the canonical schema
- Writing any MCP tools
- Designing the entity-resolution logic for matching people across snapshots
- Designing the five-dimension confidence scoring model
- Anything beyond pulling data sufficient to answer the verdict question

These are deferred to the design pass that comes *after* a "build" or "build narrower" verdict.

## Decision points where the investigation stops early

- **Stop after Track 1 if** the five sample departments all have organograms that parse cleanly into a single schema with ≥ 90% senior coverage, OR all five have organograms so format-inconsistent that parsing isn't tractable. Either extreme makes the verdict obvious without needing Tracks 2 and 3.
- **Stop after Track 2 if** every priority buyer has at least one good alternative source for the working-evaluator tier — that's enough to confirm the volatile layer is feasible regardless of organogram quality.
- **Otherwise** run all three tracks before writing the report.
