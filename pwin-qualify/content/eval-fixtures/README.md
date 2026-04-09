# Qualify Eval Fixtures

Each fixture is a JSON file describing a single question + evidence + the expected Alex review behaviour. The eval harness loads them all, runs the active content version through the live API, and reports any drift.

## When to add a fixture

- After tuning a rubric, add a fixture that exercises the boundary you adjusted (e.g. if you sharpen "Strongly Agree" on R4, add an evidence pair that should now be downgraded).
- After adding a new inflation trigger, add a fixture whose evidence contains the trigger phrase.
- After every real bid review where Alex's verdict was either obviously right (capture it as a "Validated" example) or obviously wrong (capture it as a regression — fix the rubric/trigger to make Alex right, then commit the fixture so it never regresses).

## Fixture schema

```json
{
  "$schema": "qualify-eval-fixture-v1",
  "id": "human-readable-id",
  "description": "what this fixture is testing",
  "source": "workbook seed | real bid | hand-crafted",
  "isConstructed": true,

  "context": {
    "org": "buyer name",
    "opp": "opportunity name",
    "sector": "Central Government | NHS | Local Government | ...",
    "oppType": "BPO | IT Outsourcing | Managed Service | Digital Outcomes | Consulting / Advisory | Infrastructure & Hardware | Software / SaaS",
    "tcv": "£XXm over Y years",
    "stage": "Pre-market engagement | Market engagement underway | ITT not yet published | ITT / RFP published | Shortlisted / BAFO | Preferred Bidder",
    "incumbent": "We are the challenger — no incumbent relationship | We are the incumbent defending this contract | No clear incumbent — new or emerging requirement",
    "notes": "any extra context the AI should know"
  },

  "questionId": "Q1..Q24 (standard) | R1..R12 (rebid)",
  "claimedScore": "Strongly Agree | Agree | Disagree | Strongly Disagree",
  "evidence": "the team's submitted evidence text",

  "expected": {
    "verdict": "Validated | Queried | Challenged",
    "inflationDetected": true,
    "suggestedScore": "Strongly Agree | Agree | Disagree | Strongly Disagree"
  },

  "idealResponseFromWorkbook": "optional — the ideal Alex response if known"
}
```

Only fields under `expected` that you set are checked. Omit `inflationDetected` if you don't want to assert on it for this fixture.

## Running

```bash
# Live run (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-... node pwin-qualify/content/eval-harness.js

# Dry run — builds prompts but makes no API calls
node pwin-qualify/content/eval-harness.js --dry-run

# Single fixture
ANTHROPIC_API_KEY=sk-... node pwin-qualify/content/eval-harness.js --fixture R4

# Specific content version
ANTHROPIC_API_KEY=sk-... node pwin-qualify/content/eval-harness.js --version 0.1.0
```

## Cost

Roughly $0.01–$0.02 per fixture with Sonnet 4.6 at typical token sizes. A full run of 10–15 fixtures should cost well under $0.30.

## Seed fixtures

The first four were seeded automatically:

- `rebid_R4_challenged.json` — Relationship Currency, expects Challenged. Workbook example.
- `rebid_R7_queried.json` — Retendering Motivation, expects Queried. Workbook example.
- `rebid_R2_validated.json` — Performance Risk Intelligence, expects Validated. Workbook example.
- `standard_Q9_internal_champion_inflation.json` — Standard Internal Champion question with vague positive sentiment. Hand-crafted.

The three rebid fixtures are constructed (not real BIP cases). The workbook flags this and asks "Replace with real case?" — when real cases are available, swap them in and set `isConstructed: false`.
