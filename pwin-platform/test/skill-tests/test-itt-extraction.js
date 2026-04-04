/**
 * Test: Skill 1.1 — ITT Extraction
 *
 * GENERIC TEST — works against any ITT document set. No hard-coded
 * section names, weights, or document-specific expectations.
 *
 * What this test validates:
 *
 * STRUCTURAL (automated — any document):
 *   - Skill executes without error
 *   - At least 1 response section created
 *   - Every scored section has: reference, evaluationMaxScore > 0, questionText
 *   - Scored section weights sum to approximately 100%
 *   - Evaluation framework exists with quality + price weights summing to 100
 *   - Scoring scheme exists with at least 3 levels, each with a description
 *   - Procurement context has at least 3 populated fields
 *   - At least 1 ITT document record created
 *   - No section has empty question text
 *   - Question text is substantive (median length > 80 chars)
 *
 * QUALITY (human review via HTML page):
 *   - Do the sections match what's in the source document?
 *   - Are any sections from the ITT missing?
 *   - Is the question text capturing the evaluation criteria, not just section titles?
 *   - Are the weights correct?
 *   - Are pass/fail requirements correctly identified?
 *   - Is the scoring scheme accurate?
 *
 * INPUT: Provide document paths as command line args or via config.
 *   node test-itt-extraction.js
 *   (reads from config at top of file — edit paths for your dataset)
 */

import {
  extractPDF, createPursuit, executeSkill, getProductData,
  TestResult, generateReviewHTML, estimateTokens,
} from './test-helpers.js';

// ═══════════════════════════════════════════════════════════════
// DATASET CONFIGURATION — edit these for your test data
// ═══════════════════════════════════════════════════════════════

const DATASET = {
  name: 'ESN Lot 2 — User Services',
  pursuit: {
    client: 'Home Office',
    opportunity: 'Emergency Services Network — Lot 2 User Services',
    sector: 'Emergency Services',
    tcv: 500000000,
    opportunityType: 'IT Outsourcing',
    procurementRoute: 'restricted',
    submissionDeadline: '2014-10-31',
    contractDurationMonths: 84,
    createdBy: 'bid_execution',
  },
  // Documents to feed to the skill — full paths relative to test-data/
  documents: [
    {
      path: 'Part B - Evaluation Framework/ESN ITT Part B - Evaluation Framework Lot 2 v1.pdf',
      label: 'Evaluation Framework (full)',
      pages: null, // null = all pages
    },
    {
      path: 'Part A - Information/ESN ITT Part A - Information Document final 20140808.pdf',
      label: 'ITT Information (overview)',
      pages: [0,1,2,3,4,5,6,7,8,9,10,11, 32,33,34,35,36,37,38,39,40,41,42,43,44],
    },
  ],
  model: 'claude-haiku-4-5-20251001',
};

// ═══════════════════════════════════════════════════════════════

async function run() {
  console.log(`\n╔═══════════════════════════════════════════════════════╗`);
  console.log(`║  TEST: ITT Extraction — ${DATASET.name.padEnd(30)}║`);
  console.log(`╚═══════════════════════════════════════════════════════╝\n`);

  const test = new TestResult(`ITT Extraction: ${DATASET.name}`);

  // ── Step 1: Extract documents ──
  console.log('  Step 1: Extracting documents...');
  const docParts = [];
  for (const doc of DATASET.documents) {
    const extracted = await extractPDF(doc.path, { pages: doc.pages });
    console.log(`    ${doc.label}: ${extracted.extractedPages}/${extracted.pageCount} pages, ${extracted.chars} chars`);
    docParts.push(`=== ${doc.label.toUpperCase()} ===\n${extracted.text}`);
  }
  const document = docParts.join('\n\n');
  const totalTokens = estimateTokens(document);
  console.log(`    Combined: ~${totalTokens} tokens`);

  // ── Step 2: Create pursuit ──
  console.log('\n  Step 2: Creating pursuit...');
  const shared = await createPursuit(DATASET.pursuit);
  const pursuitId = shared.pursuit.id;
  console.log(`    Pursuit: ${pursuitId}`);

  // ── Step 3: Execute skill ──
  console.log('\n  Step 3: Executing ITT Extraction...');
  const result = await executeSkill('itt-extraction', {
    pursuitId,
    document,
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

  // ── Step 4: Generic structural validation ──
  console.log('\n  Step 4: Structural validation...');
  const bid = await getProductData(pursuitId, 'bid-execution');

  const sections = bid.responseSections || [];
  const scored = sections.filter(s => (s.evaluationMaxScore || 0) > 0);
  const unscored = sections.filter(s => (s.evaluationMaxScore || 0) === 0);
  const framework = bid.evaluationFramework || {};
  const context = bid.procurementContext || {};
  const scoring = bid.clientScoringScheme || {};
  const docs = bid.ittDocuments || [];

  // --- Response Sections ---
  test.check(sections.length >= 1, `Response sections created (${sections.length})`);
  test.check(scored.length >= 1, `Scored sections found (${scored.length})`);

  // Every scored section must have key fields
  const missingRef = scored.filter(s => !s.reference);
  test.check(missingRef.length === 0, `All scored sections have a reference (${missingRef.length} missing)`);

  const missingText = scored.filter(s => !s.questionText || s.questionText.length < 10);
  test.check(missingText.length === 0, `All scored sections have question text (${missingText.length} empty/thin)`);

  const missingCategory = scored.filter(s => !s.evaluationCategory);
  test.check(missingCategory.length === 0, `All scored sections have an evaluation category (${missingCategory.length} missing)`);

  // Weights should sum to approximately 100%
  const totalWeight = scored.reduce((sum, s) => sum + (s.evaluationMaxScore || 0), 0);
  test.check(totalWeight > 80 && totalWeight < 120, `Scored weights sum to ~100% (got ${totalWeight.toFixed(1)}%)`);

  // Question text quality — median length
  const textLengths = scored.map(s => (s.questionText || '').length).sort((a, b) => a - b);
  const medianLength = textLengths[Math.floor(textLengths.length / 2)] || 0;
  test.check(medianLength > 80, `Median question text length > 80 chars (got ${medianLength})`);
  if (medianLength < 150) {
    test.warn(`Median question text is ${medianLength} chars — may be section titles only, not full evaluation criteria`);
  }

  // --- Evaluation Framework ---
  test.check(!!framework.totalScore, `Evaluation framework has a total score (${framework.totalScore})`);
  test.check(!!framework.qualityWeight || !!framework.priceWeight, 'Evaluation framework has quality or price weights');

  if (framework.qualityWeight && framework.priceWeight) {
    const fwTotal = framework.qualityWeight + framework.priceWeight;
    test.check(fwTotal >= 95 && fwTotal <= 105, `Framework weights sum to ~100% (${fwTotal}%)`);
  }

  // --- Scoring Scheme ---
  test.check(!!scoring.levels && scoring.levels.length >= 3, `Scoring scheme has >= 3 levels (${scoring.levels?.length || 0})`);

  if (scoring.levels) {
    const withDesc = scoring.levels.filter(l => l.description && l.description.length > 10);
    test.check(withDesc.length === scoring.levels.length, `All scoring levels have descriptions (${withDesc.length}/${scoring.levels.length})`);
  }

  // --- Procurement Context ---
  const contextFields = Object.entries(context).filter(([k, v]) => v && k !== 'updatedAt');
  test.check(contextFields.length >= 3, `Procurement context has >= 3 fields populated (${contextFields.length})`);

  // --- ITT Documents ---
  test.check(docs.length >= 1, `ITT document records created (${docs.length})`);

  // --- Hurdle scores / pass-fail ---
  const hurdleSections = sections.filter(s => s.hurdleScore > 0);
  if (hurdleSections.length > 0) {
    test.pass(`Pass/fail hurdle sections identified (${hurdleSections.length})`);
  } else {
    test.warn('No hurdle scores found — check if the ITT has mandatory pass/fail requirements');
  }

  // --- Write-back success ---
  const failedWrites = result.writeResults.filter(w => !w.success);
  test.check(failedWrites.length === 0, `All write-backs succeeded (${failedWrites.length} failed)`);

  // ── Step 5: Generate review HTML ──
  console.log('\n  Step 5: Generating review page...');

  const reviewPath = await generateReviewHTML(`test-itt-extraction-${Date.now()}.html`, {
    title: `ITT Extraction — ${DATASET.name}`,
    subtitle: `${new Date().toISOString().slice(0, 16)} | ${sections.length} sections | $${test.apiCost.toFixed(4)} | ${result.model}`,
    sections: [
      // Automated checks
      {
        title: 'Automated Checks',
        subtitle: 'Structural validation — these must pass for any ITT document',
        type: 'checklist',
        items: test.checks.map(c => ({ pass: c.pass, message: c.message })),
      },
      // Summary cards
      {
        title: 'Extraction Summary',
        type: 'cards',
        items: [
          { label: 'Total Sections', value: String(sections.length), detail: `${scored.length} scored + ${unscored.length} returnable` },
          { label: 'Weight Sum', value: `${totalWeight.toFixed(1)}%`, detail: 'Scored sections' },
          { label: 'Framework', value: `${framework.qualityWeight || '?'} / ${framework.priceWeight || '?'}`, detail: 'Quality / Price' },
          { label: 'Scoring Levels', value: String(scoring.levels?.length || 0) },
          { label: 'Hurdle Gates', value: String(hurdleSections.length) },
          { label: 'Context Fields', value: String(contextFields.length) },
        ],
      },
      // Scored sections — full detail for human review
      {
        title: 'Scored Response Sections — REVIEW THESE',
        subtitle: 'Compare each section against the source document. Check: correct reference, correct weight, complete question text, correct category.',
        type: 'table',
        headers: ['#', 'Reference', 'Weight %', 'Category', 'Type', 'Hurdle', 'Question Text (full)'],
        rows: scored
          .sort((a, b) => (b.evaluationMaxScore || 0) - (a.evaluationMaxScore || 0))
          .map((s, i) => [
            String(i + 1),
            s.reference || '?',
            `<strong>${s.evaluationMaxScore}%</strong>`,
            s.evaluationCategory || '?',
            s.responseType || '?',
            s.hurdleScore > 0 ? `<strong style="color:#C15050;">${s.hurdleScore}</strong>` : '—',
            `<div style="font-size:11px;color:#576482;max-width:600px;white-space:pre-wrap;">${(s.questionText || '').replace(/</g, '&lt;')}</div>`,
          ]),
      },
      // Returnable sections
      ...(unscored.length > 0 ? [{
        title: 'Returnable / Compliance Sections',
        type: 'table',
        headers: ['#', 'Reference', 'Type', 'Hurdle', 'Requirement'],
        rows: unscored.map((s, i) => [
          String(i + 1),
          s.reference || '?',
          s.responseType || '?',
          s.hurdleScore > 0 ? '<strong style="color:#C15050;">PASS/FAIL</strong>' : '—',
          `<div style="font-size:11px;max-width:500px;">${(s.questionText || '').replace(/</g, '&lt;')}</div>`,
        ]),
      }] : []),
      // Raw data for deep inspection
      { title: 'Procurement Context', type: 'json', data: context },
      { title: 'Evaluation Framework', type: 'json', data: framework },
      { title: 'Scoring Scheme', type: 'json', data: scoring },
      { title: 'ITT Documents', type: 'json', data: docs },
      // Claude's text output
      {
        title: 'Claude Output',
        subtitle: 'Raw text response — check for any observations the skill made about the document',
        type: 'text',
        content: result.text || '(no text)',
      },
    ],
  });
  console.log(`    Review page: ${reviewPath}`);

  // ── Summary ──
  const { passed, failed } = test.summary();
  process.exit(failed > 0 ? 1 : 0);
}

run().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
