# Stakeholder database — feasibility report

**Date:** 2026-04-30
**Investigation design:** `docs/superpowers/plans/2026-04-30-stakeholder-database-feasibility-plan.md`
**Evidence:** `pwin-competitive-intel/scripts/investigation/findings/`

---

## Verdict

**Build narrower — central government Director tier only, supplemented by PAC witnesses. Defer NHS, local government, and Deputy Director/Grade 6 tier.**

The Cabinet Office organogram data is current (within 30–120 days), consistently formatted, and freely available — but only names approximately 22% of SCS posts. The named tier is primarily Director (SCS2) and above: roughly 40–60 people per department. The other 78% of posts (Deputy Director, Grade 6 commercial leads) are redacted under Cabinet Office disclosure policy and cannot be recovered from organograms alone. No automated supplementary source fills this gap at scale.

The recommended scope for v1 is: central government departments and major arm's-length bodies, Director tier and above, sourced from organograms plus PAC witness lists as an event-driven supplement. This gives a useful but limited stakeholder layer covering the senior tier relevant to Verdict and Win Strategy intelligence, not the working evaluator tier. The FTS procurement contact field is the highest-priority future enhancement — extracting `contactPoint.name` from OCDS notices would add evaluator-tier names from actual procurement activity with no external dependencies.

---

## Verdict criteria scorecard

| Criterion | Threshold (build as scoped) | Measured value | Score |
|---|---|---|---|
| Senior-tier naming rate (avg across 3 current central gov depts) | ≥ 90% named | **22.6%** (HMT 26.7%, MoD 20.2%, DfE 21.0%) | dont\_build |
| Working-evaluator coverage — depts with ≥ 1 useful alt source | ≥ 70% of sampled depts | **33%** (PAC witnesses useful for DfT, DCMS, MHCLG; not systematically available per-dept) | build\_narrower |
| Max currency lag (worst current department) | ≤ 6 months | **120 days / 4 months** (HMT Dec 2025 snapshot) | build\_as\_scoped |
| Distinct organogram formats | ≤ 2 | **1** (all current depts identical column set) | build\_as\_scoped |

**Overall: build\_narrower.** Coverage is the binding constraint. Currency and format consistency pass. The verdict is "build narrower" rather than "don't build" because: (1) the data that IS available is high quality and current, (2) Director-tier names are genuinely useful for Win Strategy and Verdict, and (3) the PAC witnesses source adds a parseable event-driven layer reaching Director-level SROs.

---

## Track 1 — organogram live ingest findings

| Department | Status | Named staff | Total SCS posts | Naming rate | Format quirks | Currency lag | Reporting-line field |
|---|---|---|---|---|---|---|---|
| HM Treasury | parsed | 44 | 165 | 26.7% | Column name drift (see note) | 120 days (Dec 2025) | Present as "Reports to Senior Post" — parser missed due to case; data exists |
| Ministry of Defence | parsed (head office only) | 43 | 213 | 20.2% | Same column drift; MoD full estate fragmented across sub-datasets | 30 days (Mar 2026) | Same as HMT |
| Department for Education | parsed | 56 | 267 | 21.0% | Same column drift | 30 days (Mar 2026) | Same as HMT |
| NHS England | parsed (2016 data) | 258 | 258 | 100% | Stopped publishing post-2016; data historical only | ~3,500 days (Sep 2016) | Present |
| Birmingham City Council | absent | — | — | — | No organogram mandate for local authorities | — | — |

**Cross-check churn signal:** 3 of 3 HMT Director General-level individuals verified still in post from a December 2025 organogram (GOV.UK governance page, correct as of October 2025). No individuals confirmed as having moved on. 16 of 19 sampled individuals are "unknown" — not confirmed moved on, but unverifiable from GOV.UK governance pages because those pages only list the top ~10–12 per department (Director General and above). Governance pages are not a reliable cross-check for the Director tier. The 3 confirmed HMT cases suggest good currency at the top tier; Director-level currency is unverified but organogram snapshot dates (30–120 days) are consistent with reasonable accuracy.

**Parse observations:** All three current central government departments share an identical column set: "Grade (or equivalent)" not "Grade", "Reports to Senior Post" not "Reports To Senior Post", "Contact E-mail" not "Contact Email", pay columns with "(£)" suffix. These are not missing columns — they are renamed variants. The Cabinet Office organogram format has drifted from the original 2011 specification. A production ingest parser must handle both the original column names and the current variants. The good news: format consistency is 1 across all three current departments — a single set of column-name mappings handles everything.

---

## Track 2 — alternative source scorecard

| Source | Useful for senior tier | Useful for evaluator tier | Structure | Licence | Notes |
|---|---|---|---|---|---|
| GOV.UK People pages | yes | no | semi-structured | OGL | DG/Perm Sec tier only (~10–12 per dept). Not paginated or bulk-accessible. |
| GOV.UK appointments RSS | no | no | broken | OGL | Old URL 404s; new URL returns mixed content, not filtered to appointments. Currently unusable. |
| Companies House (ALB officers) | no | no | structured | OGL | Returns only 1 statutory director per ALB — not the executive board. Not viable. |
| NAO published reports | yes | no | unstructured (PDF) | OGL | Named SROs in PDFs only; ~1–3 officials per report. Requires PDF parsing. Sparse. |
| PAC witness lists | yes | yes (Director-level SROs) | semi-structured HTML | Parliament open | **Best supplementary source.** Names 3–5 officials per session at Director level; ~30 sessions/year; consistent HTML structure. Covers major spending departments. |
| Civil Service Jobs | no | no | semi-structured | OGL | Names hiring departments, not current post holders. Vacancies = posts being vacated. |
| LinkedIn (manual) | yes | yes | semi-structured | ToS-restricted | Rich but ToS prevents bulk use. Manual validation only. Costs LinkedIn Sales Navigator for scale. |
| Trade press | yes | no | unstructured | Scrape-required | Appointment notices exist but sparse, paywalled, and unstructured. |
| FTS contact names (bid_intel.db) | no | yes (if extracted) | structured | OGL | **Highest-priority future enhancement.** Contact names embedded in OCDS `contactPoint.name` but not extracted to current schema. One-column schema change would add evaluator-tier names for ~175k notices. |
| Dods People (paid) | yes | yes | structured | paid | Enterprise pricing; no trial confirmed. The buy-vs-build comparison if building proves too costly. |

**Recommended volatile-tier event sources (to supplement twice-yearly canonical refresh):**

1. **PAC witness lists** — consistent HTML, easily parsed, Director-level SROs, ~30 sessions/year. Wire as a weekly scrape of the publications page watching for new oral evidence entries.
2. **NAO report pages** — lower yield but covers Accounting Officers for major programmes. Wire as a monthly scrape to catch new report names and link to PAC follow-up sessions.
3. **FTS OCDS contactPoint (future)** — not currently available in bid_intel.db but is the highest-value addition. A one-column schema change to the ingest pipeline adds procurement contact names for every current notice, covering Grade 7 / commercial lead tier with no additional external dependency.

---

## Track 3 — local government reality check

**LGA canonical officer list:** Not found. No cross-council database of senior officers exists. The LGA Transparency Code (2015) obliges councils to publish their own data, but publication is decentralised to ~350+ individual council websites with no aggregation.

**Council website sample:**

| Council | Senior officers named | Detail level | Last updated shown |
|---|---|---|---|
| Birmingham CC | No — pages reached but no officer listing surfaced | N/A | N/A |
| Manchester CC | Partially — Chief Executive (Tom Stannard) confirmed; full directory URL unstable | Name + title only | Unknown |
| London Borough of Hackney | Not confirmed — URL 404d, not recovered | Unknown | Unknown |
| Oxfordshire CC | Yes — 10 named directors confirmed | Name + title + contact | Unknown |
| South Cambridgeshire DC | Partially — Chief Executive (Liz Watts) confirmed; leadership page exists | Name + title | Unknown |

**Local government recommendation:** Defer local government coverage from v1. There is no canonical cross-council officer list, council websites use inconsistent formats and unstable URL structures, coverage only reaches Chief Officer tier (not procurement leads), and the engineering effort to maintain scrapers for ~350+ council websites is disproportionate to the intelligence value for PWIN's current use cases (central government and major NHS procurement). If local government buyer stakeholders are needed for a specific pursuit, per-pursuit manual research is the right approach.

---

## Recommended next step

The verdict is "build narrower" with a clearly scoped v1:

**What to build:**
- Ingest central government organogram CSVs from data.gov.uk for ~20 departments + major ALBs
- Map the actual column names (see parse_notes in track1_parsed.json) — single set of mappings covers all current publishers
- Build a `stakeholders` table: `person_id`, `name`, `job_title`, `unit`, `organisation`, `parent_department`, `scs_band_inferred` (from job title keywords: "Permanent Secretary", "Director General", "Director"), `source`, `snapshot_date`
- Wire PAC witness list scraper as a weekly event-driven supplement
- **Do not** attempt Deputy Director / Grade 6 tier from organograms — the data is not there

**What to defer:**
- NHS England organograms (stopped publishing 2016)
- Local government (no bulk mechanism)
- Deputy Director / Grade 6 tier (redacted in organograms; no bulk source)
- FTS contact names (one sprint to add the column, but validate on a few queries first)

**First three actions to turn the action file into a buildable spec:**
1. **Schema design:** Define `stakeholders` table columns, decide whether to link to `canonical_buyers` via `buyer_id`, and specify the SCS band inference rules from job title
2. **Ingest parser design:** Write `parse_organogram_v2.py` using the correct column name mappings (Grade → "Grade (or equivalent)", etc.) and the reporting-line field ("Reports to Senior Post")
3. **MCP tool signatures:** Define `get_stakeholders(buyer_id, tier?)`, `get_stakeholder_by_name(name)`, and `find_evaluators(buyer_id)` — the three access patterns Win Strategy and Verdict need

See `wiki/platform/stakeholder-data-layer-architecture.md` for the architectural framing.

---

## Appendix — sample parsed records

### HM Treasury (sample\_5, December 2025 organogram)

```json
[
  {"name": "Vickerstaff, Matthew", "grade": "", "job_title": "Director of Finance and Deputy CEO Infrastructure Projects Authority", "unit": "National Infrastructure and Service Transformation Authority", "organisation": "HM Treasury", "reports_to": ""},
  {"name": "Gallagher, Daniel", "grade": "", "job_title": "Director - Economics", "unit": "Economics", "organisation": "HM Treasury", "reports_to": ""},
  {"name": "Coady, Rebecca", "grade": "", "job_title": "Director - Corporate Centre", "unit": "Corporate Centre", "organisation": "HM Treasury", "reports_to": ""},
  {"name": "Russell, Elizabeth", "grade": "", "job_title": "Second Permanent Secretary", "unit": "Ministerial & Communications", "organisation": "HM Treasury", "reports_to": ""},
  {"name": "Glover, Jessica", "grade": "", "job_title": "Director General and Chief Economic Adviser", "unit": "Ministerial & Communications", "organisation": "HM Treasury", "reports_to": ""}
]
```

### Ministry of Defence — Head Office (sample\_5, March 2026 organogram)

```json
[
  {"name": "Rouse, Deana (Deana), Miss", "grade": "", "job_title": "Director Resources HO&CF", "unit": "LEVEL 2: COO", "organisation": "Ministry of Defence", "reports_to": ""},
  {"name": "Cooke, Kerry, Ms", "grade": "", "job_title": "NAD-CSM-PFO Programme Director", "unit": "LEVEL 2: COO", "organisation": "Ministry of Defence", "reports_to": ""},
  {"name": "Mitchell, Austin (Austin), Mr", "grade": "", "job_title": "Secretary of State COS-2", "unit": "LEVEL 2: DELIVERY AND STRATEGY", "organisation": "Ministry of Defence", "reports_to": ""},
  {"name": "Berthon, Richard (Richard), Mr", "grade": "", "job_title": "FCAS Director", "unit": "LEVEL 2: DCDS MILCAP", "organisation": "Ministry of Defence", "reports_to": ""},
  {"name": "Cameron, Eliza (Eliza), Mrs", "grade": "", "job_title": "Strat Hub-Strategy-Dir", "unit": "LEVEL 2: DELIVERY AND STRATEGY", "organisation": "Ministry of Defence", "reports_to": ""}
]
```

### Department for Education (sample\_5, March 2026 organogram)

```json
[
  {"name": "Isabelle Trowler", "grade": "", "job_title": "Director", "unit": "Families Group", "organisation": "Department for Education", "reports_to": ""},
  {"name": "Helen Waite", "grade": "", "job_title": "Director", "unit": "CSC Strategy and Care System", "organisation": "Department for Education", "reports_to": ""},
  {"name": "Kate Dixon", "grade": "", "job_title": "Director", "unit": "Strategy and Safer Streets", "organisation": "Department for Education", "reports_to": ""},
  {"name": "Kate Dethridge", "grade": "", "job_title": "Director", "unit": "Regions Group: South East", "organisation": "Department for Education", "reports_to": ""},
  {"name": "Sophie Taylor", "grade": "", "job_title": "Director", "unit": "Educational Engagement, Access and Wellbeing (EEAW)", "organisation": "Department for Education", "reports_to": ""}
]
```
