# BidEquity Platform — Skill Test Log

**Purpose:** Complete record of every test run, findings, prompt refinements, and retest outcomes across all skills. This document tracks the journey from first test to production readiness.

**Convention:** Each test run gets a numbered entry. Findings drive actions. Actions drive retests. The log builds a complete audit trail of how each skill was refined.

---

## Readiness Tracker

| Skill | Status | Last Tested | Runs | Issues Open | Notes |
|-------|--------|-------------|------|-------------|-------|
| 1.1 ITT Extraction | TESTING | — | 0 | — | Awaiting rate limit upgrade |
| 1.2 Evaluation Criteria | NOT TESTED | — | 0 | — | Test script not yet written |
| 1.3 Contract Analysis | NOT TESTED | — | 0 | — | |
| 1.4 Compliance Matrix | NOT TESTED | — | 0 | — | |
| 1.5 Procurement Briefing | TESTING | — | 0 | — | Awaiting rate limit upgrade |
| 1.6 Clarification Impact | NOT TESTED | — | 0 | — | |
| 1.7 Amendment Detection | NOT TESTED | — | 0 | — | |
| 3.5 Timeline Analysis | NOT TESTED | — | 0 | — | Needs seed data loaded |
| 3.7 Standup Priorities | NOT TESTED | — | 0 | — | |
| 3.8 Compliance Coverage | TESTING | — | 0 | — | Awaiting rate limit upgrade |
| 3.9 Win Theme Audit | NOT TESTED | — | 0 | — | |
| 3.12 Gate Readiness | NOT TESTED | — | 0 | — | |

---

## Test Run Log

### Run Template

Copy this for each test run:

```
### Run [NUMBER] — [SKILL NAME]

**Date:** YYYY-MM-DD
**Dataset:** [e.g. ESN Lot 2]
**Model:** [e.g. claude-haiku-4-5-20251001]
**Tokens:** [in] in / [out] out
**Cost:** $X.XXXX
**Automated checks:** X passed / X failed
**Review page:** [filename in results/]

#### Findings

**What it got right:**
- 

**What it got wrong:**
- 

**What was missing:**
- 

**Quality assessment:**
[Would you trust this output? Is it production-ready or needs refinement?]

#### Actions

| # | Action | Type | Status |
|---|--------|------|--------|
| 1 | [description] | prompt / data model / test script | done / pending |

#### Retest Required?
[Yes/No — if yes, link to retest run number]
```

---

## Preliminary Test Runs (Pre-Framework)

These runs were conducted before the test framework was formalised. Recorded here for completeness.

### Run P1 — ITT Extraction (ad hoc, synthetic data)

**Date:** 2026-04-03
**Dataset:** Synthetic HMPPS Probation Case Management ITT (hand-written test document)
**Model:** claude-sonnet-4-20250514
**Tokens:** 21,260 in / 1,719 out
**Cost:** $0.03 (Sonnet)

#### Findings
- Correctly extracted 5 response sections with marks, hurdle scores, word limits
- Evaluation framework correct (60/40 split)
- Procurement context correct (restricted, hybrid, £25m, Jaggaer)
- Client scoring scheme captured (0-5 scale, pass mark 3)
- This was a small synthetic document — not a real test of extraction capability

#### Actions
| # | Action | Type | Status |
|---|--------|------|--------|
| 1 | Need to test against real procurement documents, not synthetic | test data | done (ESN uploaded) |

---

### Run P2 — ITT Extraction (ESN Lot 2, truncated)

**Date:** 2026-04-04
**Dataset:** ESN Lot 2 Evaluation Framework — pages 1-18 only (Annex 1 scoring guidance excluded)
**Model:** claude-haiku-4-5-20251001
**Tokens:** 28,635 in / 5,621 out
**Cost:** $0.0142 (Haiku)

#### Findings
- 28 response sections extracted (17 scored, 11 returnable)
- Section structure correct — matched Tier 4/5 criteria from the evaluation framework
- **ISSUE: Question text was thin** — captured section titles and brief descriptions only, not the full scoring guidance descriptors from Annex 1
- Evaluation framework correct (70/30 split)
- Scoring scheme captured but with generic descriptions
- Procurement context correct
- Key requirements (pass/fail) correctly identified

#### Actions
| # | Action | Type | Status |
|---|--------|------|--------|
| 1 | Feed full 62-page document including Annex 1 scoring guidance | test data | pending (rate limit) |
| 2 | Test scripts rewritten to be generic — no hard-coded ESN data | test script | done |
| 3 | Rate limit upgrade requested | infrastructure | pending |

---

### Run P3 — Compliance Coverage (ESN Lot 2)

**Date:** 2026-04-04
**Dataset:** ESN Lot 2 extracted sections (from Run P2) + 8 manually added compliance requirements
**Model:** claude-haiku-4-5-20251001
**Tokens:** 80,948 in / 12,117 out (multi-turn)
**Cost:** $0.0354 (Haiku)

#### Findings
- 18 write-backs: 1 compliance insight, 5 standup actions, 12 risk flags (all risk flags failed — no activities loaded)
- Coverage analysis was substantive and accurate:
  - Correctly identified 0% response assignment (no owners on any section)
  - Correctly flagged Public Safety Communications as highest-risk section (16.8%, KEY REQUIREMENT)
  - Correctly identified pass/fail gates on T&Cs, standards, insurance
  - Correctly calculated marks at risk
- **ISSUE: Risk flags failed** because there were no activities in the bid data to attach them to
- **ISSUE: Some analysis was in the text output, not in the structured gaps field**
- Actions were specific and prioritised sensibly

#### Actions
| # | Action | Type | Status |
|---|--------|------|--------|
| 1 | Load seed data (activities, team, themes, gates) before compliance test | test data | done (seed-esn-data.js created) |
| 2 | Increase max_tokens from 8192 to 16384 | skill runner | done |
| 3 | Consider prompting skill to put all gaps in the structured field, not just text | prompt | pending |

---

## Formal Test Runs

*(Begin here once rate limit is upgraded and full test suite runs)*

---

## Prompt Refinement History

Track every change to skill YAML prompts here, linked to the test run that triggered it.

| Date | Skill | Change | Triggered by | Result |
|------|-------|--------|-------------|--------|
| — | — | — | — | — |

---

## Cumulative Cost Tracker

| Date | Runs | Model | Total Cost | Cumulative |
|------|------|-------|------------|------------|
| 2026-04-03 | P1 (Sonnet) | Sonnet | $0.03 | $0.03 |
| 2026-04-03 | 3 test runs (Sonnet) | Sonnet | $0.09 | $0.12 |
| 2026-04-04 | P2, P3 (Haiku) | Haiku | $0.05 | $0.17 |

---

*BidEquity Platform — Skill Test Log | Started 2026-04-03*
