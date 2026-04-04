# Skill Test Framework

## Purpose

Structured, repeatable tests for each AI skill against real procurement data (ESN Lot 2). Each test has a defined script, input specification, expected output structure, and visual review page.

## Test Data

ESN (Emergency Services Network) — Home Office, 2014. Multi-lot IT outsourcing procurement for digital replacement of Airwave. Lot 2 (User Services) used as primary test subject.

**Location:** `pwin-bid-execution/test-data/` (gitignored — not committed to repo)

**Available documents:**
- Part A: Information Document (124 pages) — programme overview, lot descriptions, procurement process
- Part B: Evaluation Framework Lot 2 (62 pages) — scoring criteria, weights, scoring guidance
- Part B: Evaluation Framework Lot 3 (62 pages)
- Part B: Evaluation Framework Lot 4 (62 pages)
- Part C: Draft Contracts — Lot 2/3/4, ~34 schedules each (T&Cs, requirements, SLAs, pricing)
- Part D: Bid Forms — Lot 2/3/4, response templates per schedule

## How Tests Work

Each test script (`test-*.js`) does the following:

1. **Extracts** the relevant document text from PDFs/Word docs
2. **Creates** a fresh pursuit on the platform
3. **Executes** the skill with the full document content (no truncation)
4. **Validates** the output structure (sections created, fields populated, correct types)
5. **Generates** an HTML review page for human inspection
6. **Reports** pass/fail on structural checks + cost

## Running Tests

```bash
# Prerequisite: server running, API key set
export ANTHROPIC_API_KEY=sk-ant-...
cd pwin-platform
node src/server.js &

# Run a single test
node test/skill-tests/test-itt-extraction.js

# Run all tests
node test/skill-tests/run-all.js
```

## Test List

| Test | Skill | Documents Used | What It Validates |
|------|-------|----------------|-------------------|
| test-itt-extraction | 1.1 ITT Extraction | Part A (overview) + Part B Lot 2 (full 62 pages incl. Annex 1 scoring guidance) | Response sections match evaluation framework, weights correct, scoring scheme captured, procurement context complete |
| test-evaluation-criteria | 1.2 Evaluation Criteria Analysis | Part B Lot 2 (full) + extracted sections from test-itt-extraction | Marks concentration analysis, sub-criteria breakdown, hurdle identification |
| test-procurement-briefing | 1.5 Procurement Briefing | Part A (full 124 pages) + Part B Lot 2 (criteria summary) | Narrative quality, sector-specific insight, strategic recommendations |
| test-compliance-coverage | 3.8 Compliance Coverage | Extracted sections + Part D bid forms (compliance checklist) | Coverage gaps identified, mandatory requirements flagged, marks-at-risk calculated |
| test-contract-analysis | 1.3 Contract Analysis | Part C Lot 2 — T&Cs + key schedules (2.1, 7.1, 8.5) | Obligations extracted, red lines identified, risk areas flagged |
| test-timeline-analysis | 3.5 Timeline Analysis | Pre-loaded 84-activity schedule with realistic dates | Overdue activities flagged, critical path risks, resource conflicts |

## Review Process

After running a test:
1. Check the console output for structural pass/fail
2. Open the generated HTML review page in a browser
3. Compare extracted data against the source documents
4. Note any missing sections, incorrect weights, or misclassified items
5. Feed findings back into skill prompt refinement

## Rate Limit Note

Tests are designed for Tier 3 (120K input tokens/min). At Tier 1 (30K/min), tests will hit rate limits. Each test includes a configurable delay between API calls. Set `RATE_LIMIT_DELAY_MS` environment variable to control pacing (default: 0 at Tier 3, set to 65000 for Tier 1).
