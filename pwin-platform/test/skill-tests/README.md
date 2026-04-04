# Skill Test Framework

## Design Principle

Tests validate the **skill's capability**, not knowledge of a specific document. All automated checks are structural and generic — they work against any procurement dataset. No test knows in advance what sections, weights, or content the document contains. The skill must find that independently.

Human review happens separately via generated HTML pages, where the reviewer compares the skill's output against the source documents.

## Two Types of Validation

### Automated (generic — any document)
- Did the skill produce output?
- Is the output structurally complete? (sections have references, weights, question text)
- Do weights sum correctly?
- Is the text substantive, not thin summaries?
- Are actions specific, not generic advice?

### Human Review (per-dataset — needs a person)
- Is the extraction accurate against the source?
- Are any sections missing?
- Are weights correct?
- Is the narrative strategically useful?
- Would a bid manager act on the recommendations?

## Test Data

Place procurement documents in `pwin-bid-execution/test-data/` (gitignored). The current test dataset is ESN Lot 2 (Home Office Emergency Services Network, 2014). To test against a different opportunity, edit the `DATASET` config block at the top of each test script.

## Running Tests

```bash
# Prerequisites
export ANTHROPIC_API_KEY=sk-ant-...
cd pwin-platform
node src/server.js &

# Run one test
node test/skill-tests/test-itt-extraction.js

# Run all tests in dependency order
node test/skill-tests/run-all.js

# With rate limit protection (Tier 1 accounts)
RATE_LIMIT_DELAY_MS=65000 node test/skill-tests/run-all.js
```

## Test Execution Order

Tests follow the skill dependency chain (see WORKFLOW.md):

1. **ITT Extraction** — no dependencies, extracts the exam paper
2. **Procurement Briefing** — no dependencies, produces narrative
3. **Compliance Coverage** — depends on ITT Extraction output
4. (Future) Timeline Analysis — depends on seeded activity data
5. (Future) Win Theme Audit — depends on seeded themes + extracted sections

## Reviewing Results

After tests run, open the HTML files in `test/skill-tests/results/`:

1. Check the **Automated Checks** section — all must pass
2. Read the **extracted data tables** — compare against source documents
3. Read the **AI narrative output** — judge quality as a bid professional
4. Note issues for skill prompt refinement

## Adapting for a New Dataset

1. Copy procurement documents to `pwin-bid-execution/test-data/`
2. Edit the `DATASET` block in each test script:
   - Update document paths
   - Update pursuit metadata (client, sector, value, etc.)
3. Run the tests — automated checks work unchanged
4. Review the HTML output against your new documents

## Seed Data

Some skills need data that documents can't provide (activity schedules, team, win themes). Use `seed-esn-data.js` as a template — edit for your dataset:

```bash
# After ITT Extraction has run:
node test/skill-tests/seed-esn-data.js <pursuitId>
```

The seed data deliberately includes issues for the AI to find: overdue activities, resource conflicts, unassigned sections, draft win themes.
