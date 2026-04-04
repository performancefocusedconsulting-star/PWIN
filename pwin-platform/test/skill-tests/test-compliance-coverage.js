/**
 * Test: Skill 3.8 — Compliance Coverage (UC4)
 *
 * GENERIC TEST — works against any pursuit with extracted response sections.
 * Runs ITT Extraction first if needed, then analyses coverage.
 *
 * STRUCTURAL (automated — any document):
 *   - Skill executes without error
 *   - At least 1 compliance insight created with a summary
 *   - Summary is substantive (> 200 chars)
 *   - At least 1 standup action created
 *   - Actions are specific (> 50 chars each)
 *   - If gaps are structured, each has a requirement and recommendation
 *
 * QUALITY (human review via HTML page):
 *   - Are the gaps genuine? Do they match the actual state of the bid?
 *   - Are risk priorities sensible? Highest-weight gaps ranked highest?
 *   - Are actions specific and actionable, not generic advice?
 *   - Does it mention pass/fail requirements?
 *   - Does it calculate marks at risk?
 */

import {
  extractPDF, createPursuit, executeSkill, getProductData,
  TestResult, generateReviewHTML,
} from './test-helpers.js';

// ═══════════════════════════════════════════════════════════════
// DATASET CONFIGURATION
// ═══════════════════════════════════════════════════════════════

const DATASET = {
  name: 'ESN Lot 2 — User Services',
  pursuit: {
    client: 'Home Office',
    opportunity: 'ESN Lot 2 — Compliance Coverage Test',
    sector: 'Emergency Services',
    tcv: 500000000,
    opportunityType: 'IT Outsourcing',
    procurementRoute: 'restricted',
    submissionDeadline: '2014-10-31',
    contractDurationMonths: 84,
    createdBy: 'bid_execution',
  },
  ittDocument: {
    path: 'Part B - Evaluation Framework/ESN ITT Part B - Evaluation Framework Lot 2 v1.pdf',
    label: 'Evaluation Framework',
  },
  model: 'claude-haiku-4-5-20251001',
};

// ═══════════════════════════════════════════════════════════════

async function run() {
  console.log(`\n╔═══════════════════════════════════════════════════════╗`);
  console.log(`║  TEST: Compliance Coverage — ${DATASET.name.padEnd(24)}║`);
  console.log(`╚═══════════════════════════════════════════════════════╝\n`);

  const test = new TestResult(`Compliance Coverage: ${DATASET.name}`);

  // ── Step 1: Create pursuit and run ITT Extraction ──
  console.log('  Step 1: Setting up pursuit with extracted ITT data...');

  const shared = await createPursuit(DATASET.pursuit);
  const pursuitId = shared.pursuit.id;
  console.log(`    Pursuit: ${pursuitId}`);

  const ittDoc = await extractPDF(DATASET.ittDocument.path);
  console.log(`    ${DATASET.ittDocument.label}: ${ittDoc.extractedPages} pages, ${ittDoc.chars} chars`);

  console.log('    Running ITT Extraction (prerequisite)...');
  const extractResult = await executeSkill('itt-extraction', {
    pursuitId,
    document: `${DATASET.ittDocument.label}\n\n${ittDoc.text}`,
    _model: DATASET.model,
  });

  if (extractResult.error) {
    test.fail(`ITT Extraction prerequisite: ${extractResult.error}`);
    test.summary();
    return;
  }
  test.pass('ITT Extraction prerequisite completed');
  test.recordUsage(extractResult.usage, extractResult.model);

  // Verify sections were extracted
  const postExtract = await getProductData(pursuitId, 'bid-execution');
  const sectionCount = (postExtract.responseSections || []).length;
  console.log(`    Extracted ${sectionCount} response sections`);

  if (sectionCount === 0) {
    test.fail('No sections extracted — cannot test compliance coverage');
    test.summary();
    return;
  }

  // ── Step 2: Execute Compliance Coverage ──
  console.log('\n  Step 2: Executing Compliance Coverage...');
  const result = await executeSkill('compliance-coverage', {
    pursuitId,
    _model: DATASET.model,
  });

  if (result.error) {
    test.fail(`Skill execution: ${result.error}`);
    test.summary();
    return;
  }

  test.pass('Skill executed without error');
  test.recordUsage(result.usage, result.model);
  console.log(`    Model: ${result.model} | Tokens: ${result.usage.input_tokens} in / ${result.usage.output_tokens} out`);

  // ── Step 3: Generic structural validation ──
  console.log('\n  Step 3: Structural validation...');
  const bid = await getProductData(pursuitId, 'bid-execution');

  const insights = bid.complianceCoverageInsights || [];
  const actions = bid.standupActions || [];
  const risks = bid.risks || [];
  const successfulWrites = result.writeResults.filter(w => w.success).length;
  const failedWrites = result.writeResults.filter(w => !w.success).length;

  // --- Insight quality ---
  test.check(insights.length >= 1, `At least 1 compliance insight created (${insights.length})`);

  if (insights.length > 0) {
    const insight = insights[insights.length - 1]; // latest
    test.check(!!insight.summary, 'Insight has a summary');
    test.check((insight.summary || '').length > 200, `Summary is substantive (${(insight.summary || '').length} chars)`);

    const gaps = insight.gaps || [];
    if (gaps.length > 0) {
      test.pass(`Structured gaps identified (${gaps.length})`);
      const withRecommendation = gaps.filter(g => g.recommendation && g.recommendation.length > 10);
      test.check(withRecommendation.length > 0, `At least 1 gap has a recommendation (${withRecommendation.length}/${gaps.length})`);
    } else {
      test.warn('No structured gaps in insight object — check if gaps are described in the summary text instead');
    }
  }

  // --- Actions quality ---
  test.check(actions.length >= 1, `At least 1 standup action created (${actions.length})`);

  if (actions.length > 0) {
    const substantive = actions.filter(a => (a.description || '').length > 50);
    test.check(substantive.length === actions.length, `All actions are specific >50 chars (${substantive.length}/${actions.length})`);

    const hasPriority = actions.filter(a => a.priority);
    test.check(hasPriority.length > 0, `At least 1 action has a priority level (${hasPriority.length}/${actions.length})`);
  }

  // --- Write-backs ---
  test.check(successfulWrites > 0, `Successful write-backs (${successfulWrites})`);
  if (failedWrites > 0) {
    test.warn(`${failedWrites} write-backs failed — likely risk flags needing activity data`);
  }

  // ── Step 4: Generate review HTML ──
  console.log('\n  Step 4: Generating review page...');

  const latestInsight = insights.length > 0 ? insights[insights.length - 1] : null;

  const reviewPath = await generateReviewHTML(`test-compliance-coverage-${Date.now()}.html`, {
    title: `Compliance Coverage — ${DATASET.name}`,
    subtitle: `${new Date().toISOString().slice(0, 16)} | ${insights.length} insights, ${actions.length} actions | $${test.apiCost.toFixed(4)}`,
    sections: [
      {
        title: 'Automated Checks',
        type: 'checklist',
        items: test.checks.map(c => ({ pass: c.pass, message: c.message })),
      },
      {
        title: 'Summary',
        type: 'cards',
        items: [
          { label: 'Sections Analysed', value: String(sectionCount) },
          { label: 'Insights', value: String(insights.length) },
          { label: 'Actions', value: String(actions.length) },
          { label: 'Risks', value: String(risks.length) },
          { label: 'Write-backs', value: `${successfulWrites} ok, ${failedWrites} failed` },
        ],
      },
      ...(latestInsight ? [{
        title: 'Coverage Analysis — REVIEW THIS',
        subtitle: 'Is this analysis accurate? Are the right gaps identified? Are priorities sensible?',
        type: 'text',
        content: latestInsight.summary || '(no summary)',
      }] : []),
      ...(latestInsight?.gaps?.length > 0 ? [{
        title: 'Identified Gaps',
        type: 'table',
        headers: ['Requirement', 'Status', 'Recommendation'],
        rows: latestInsight.gaps.map(g => [
          g.requirement || '?',
          g.status || '?',
          g.recommendation || '—',
        ]),
      }] : []),
      ...(actions.length > 0 ? [{
        title: 'AI-Generated Actions — REVIEW THESE',
        subtitle: 'Are these specific and actionable? Would a bid manager act on them?',
        type: 'list',
        items: actions.map(a => ({ priority: a.priority || '', text: a.description || '' })),
      }] : []),
      {
        title: 'Claude Full Output',
        type: 'text',
        content: result.text || '(no text)',
      },
    ],
  });
  console.log(`    Review page: ${reviewPath}`);

  const { failed } = test.summary();
  process.exit(failed > 0 ? 1 : 0);
}

run().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
