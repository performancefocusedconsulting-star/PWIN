/**
 * Test: Skill 1.1 — ITT Extraction
 *
 * Purpose: Extract structured data from the ESN Lot 2 ITT documents.
 * The full evaluation framework (62 pages including Annex 1 scoring guidance)
 * is fed to the skill. No truncation.
 *
 * Documents used:
 *   - Part A: Information Document (pages 1-12 overview + pages 32-45 lot descriptions)
 *   - Part B: Evaluation Framework Lot 2 (ALL 62 pages including Annex 1 scoring guidance)
 *
 * Expected output:
 *   - Response sections matching every Tier 5 evaluation criterion
 *   - Evaluation framework with 70/30 split and sub-category weights
 *   - Scoring scheme (5-point scale from the scoring guidance)
 *   - Procurement context (restricted, MEAT, Bravo, £500m+)
 *   - ITT document records
 *
 * Validation checks:
 *   - At least 15 scored response sections (the ITT has 15 Tier 5 scored criteria)
 *   - Public Safety Communications section exists with 16.8% weight
 *   - Evaluation framework total = 100, quality = 70, price = 30
 *   - Scoring scheme has at least 4 levels
 *   - Procurement route = restricted
 *   - All section weights sum to approximately 100%
 *   - Key Requirements (pass/fail) identified
 *
 * Human review:
 *   - Compare extracted sections against Part B pages 12-14 (Tier 4/5 criteria table)
 *   - Check question text captures the scoring guidance descriptors, not just section names
 *   - Verify no sections from the ITT are missing from the extraction
 *   - Check evaluation category assignments (technical vs commercial)
 */

import {
  extractPDF, createPursuit, executeSkill, getProductData,
  TestResult, generateReviewHTML, estimateTokens,
} from './test-helpers.js';

async function run() {
  console.log('\n╔═══════════════════════════════════════════════╗');
  console.log('║  TEST: Skill 1.1 — ITT Extraction (ESN Lot 2) ║');
  console.log('╚═══════════════════════════════════════════════╝\n');

  const test = new TestResult('ITT Extraction');

  // ── Step 1: Extract document text ──
  console.log('  Step 1: Extracting document text...');

  // Part A overview (pages 1-12 + lot descriptions 32-45)
  const partA = await extractPDF(
    'Part A - Information/ESN ITT Part A - Information Document final 20140808.pdf',
    { pages: [...Array(12).keys(), ...Array.from({length: 14}, (_, i) => 32 + i)] }
  );
  console.log(`    Part A: ${partA.pages} total pages, extracted ${partA.chars} chars`);

  // Part B Lot 2 — ALL pages including Annex 1 scoring guidance
  const partB = await extractPDF(
    'Part B - Evaluation Framework/ESN ITT Part B - Evaluation Framework Lot 2 v1.pdf'
  );
  console.log(`    Part B: ${partB.pages} pages, ${partB.chars} chars (FULL — no truncation)`);

  const document = [
    'ESN INVITATION TO TENDER — LOT 2: USER SERVICES',
    'Authority: Home Office (Secretary of State for the Home Department)',
    'Programme: Emergency Services Network (ESN)',
    'Date: 8 August 2014',
    'Procurement: Restricted procedure, OJEU 2014/S 077-133654',
    'Contract: 84 months, estimated £500m+ across all lots',
    'Submission: Bravo eSourcing portal',
    'TUPE: Applicable (transferring from Airwave)',
    '',
    '=== PART A: INFORMATION DOCUMENT (Key Sections) ===',
    partA.text,
    '',
    '=== PART B: LOT 2 EVALUATION FRAMEWORK (FULL — 62 PAGES) ===',
    partB.text,
  ].join('\n');

  const totalTokens = estimateTokens(document);
  console.log(`    Combined document: ${document.length} chars (~${totalTokens} tokens)`);
  test.check(totalTokens > 10000, `Document has sufficient content (~${totalTokens} tokens)`);

  // ── Step 2: Create pursuit ──
  console.log('\n  Step 2: Creating test pursuit...');
  const shared = await createPursuit({
    client: 'Home Office',
    opportunity: 'ESN Lot 2 — User Services (ITT Extraction Test)',
    sector: 'Emergency Services',
    tcv: 500000000,
    opportunityType: 'IT Outsourcing',
    procurementRoute: 'restricted',
    submissionDeadline: '2014-10-31',
    contractDurationMonths: 84,
    createdBy: 'bid_execution',
  });
  const pursuitId = shared.pursuit.id;
  console.log(`    Pursuit: ${pursuitId}`);

  // ── Step 3: Execute skill ──
  console.log('\n  Step 3: Executing ITT Extraction skill...');
  const result = await executeSkill('itt-extraction', {
    pursuitId,
    document,
    _model: 'claude-haiku-4-5-20251001',
  });

  if (result.error) {
    console.error(`    ERROR: ${result.error}`);
    test.check(false, `Skill executed without error: ${result.error}`);
    test.summary();
    return;
  }

  console.log(`    Model: ${result.model}`);
  console.log(`    Tokens: ${result.usage.input_tokens} in / ${result.usage.output_tokens} out`);
  console.log(`    Write-backs: ${result.writeResults.length}`);
  test.recordUsage(result.usage, result.model);

  // ── Step 4: Validate output ──
  console.log('\n  Step 4: Validating extracted data...');
  const bidData = await getProductData(pursuitId, 'bid-execution');

  const sections = bidData.responseSections || [];
  const scored = sections.filter(s => (s.evaluationMaxScore || 0) > 0);
  const framework = bidData.evaluationFramework || {};
  const context = bidData.procurementContext || {};
  const scoring = bidData.clientScoringScheme || {};
  const docs = bidData.ittDocuments || [];

  // Structural checks
  test.check(sections.length >= 15, `At least 15 response sections extracted (got ${sections.length})`);
  test.check(scored.length >= 15, `At least 15 scored sections (got ${scored.length})`);

  // Section weight checks
  const totalWeight = scored.reduce((sum, s) => sum + (s.evaluationMaxScore || 0), 0);
  test.check(Math.abs(totalWeight - 100) < 5, `Scored section weights sum to ~100% (got ${totalWeight.toFixed(1)}%)`);

  // Public Safety Communications — the highest weighted technical section
  const psc = sections.find(s => s.reference?.includes('Public Safety') || (s.evaluationMaxScore === 16.8));
  test.check(!!psc, 'Public Safety Communications section found');
  if (psc) {
    test.check(psc.evaluationMaxScore === 16.8, `PSC weight is 16.8% (got ${psc.evaluationMaxScore})`);
    test.check(psc.hurdleScore > 0, `PSC has a hurdle score (got ${psc.hurdleScore})`);
  }

  // Pricing section
  const pricing = sections.find(s => (s.evaluationMaxScore || 0) >= 25 && s.evaluationCategory === 'commercial');
  test.check(!!pricing, 'Pricing section found (28.5%)');
  if (pricing) {
    test.check(pricing.evaluationMaxScore >= 28, `Pricing weight is ~28.5% (got ${pricing.evaluationMaxScore})`);
  }

  // Evaluation framework
  test.check(framework.totalScore === 100, `Framework total = 100 (got ${framework.totalScore})`);
  test.check(framework.qualityWeight === 70, `Framework quality = 70% (got ${framework.qualityWeight})`);
  test.check(framework.priceWeight === 30, `Framework price = 30% (got ${framework.priceWeight})`);

  // Scoring scheme
  test.check(!!scoring.levels, 'Scoring scheme has levels');
  if (scoring.levels) {
    test.check(scoring.levels.length >= 4, `At least 4 scoring levels (got ${scoring.levels.length})`);
    const hasDescriptions = scoring.levels.every(l => l.description && l.description.length > 10);
    test.check(hasDescriptions, 'All scoring levels have substantive descriptions');
  }

  // Procurement context
  test.check(context.procurementRoute === 'restricted', `Route = restricted (got ${context.procurementRoute})`);
  test.check(context.evaluationModel?.includes('advantageous') || context.evaluationModel?.includes('MEAT'),
    `Evaluation model = MEAT (got ${context.evaluationModel})`);
  test.check(context.estimatedContractValue >= 100000000, `Contract value > £100m (got ${context.estimatedContractValue})`);

  // ITT documents
  test.check(docs.length >= 1, `At least 1 ITT document recorded (got ${docs.length})`);

  // Question text quality — check that scored sections have substantive question text
  const thinQuestions = scored.filter(s => (s.questionText || '').length < 100);
  if (thinQuestions.length > 0) {
    test.warn(`${thinQuestions.length} scored sections have thin question text (<100 chars) — may need scoring guidance enrichment`);
  }
  const richQuestions = scored.filter(s => (s.questionText || '').length > 200);
  test.check(richQuestions.length >= 5, `At least 5 sections have rich question text >200 chars (got ${richQuestions.length})`);

  // Key requirements
  const keyReqs = sections.filter(s => s.hurdleScore > 0);
  test.check(keyReqs.length >= 2, `At least 2 sections have hurdle scores (got ${keyReqs.length})`);

  // ── Step 5: Generate review HTML ──
  console.log('\n  Step 5: Generating review page...');

  const maxScore = Math.max(...scored.map(s => s.evaluationMaxScore || 0));
  const reviewPath = await generateReviewHTML('test-itt-extraction.html', {
    title: 'ITT Extraction — ESN Lot 2 User Services',
    subtitle: `Test run ${new Date().toISOString().slice(0,16)} | ${sections.length} sections | $${test.apiCost.toFixed(4)}`,
    sections: [
      {
        title: 'Summary',
        type: 'cards',
        items: [
          { label: 'Response Sections', value: sections.length, detail: `${scored.length} scored + ${sections.length - scored.length} returnable` },
          { label: 'Evaluation Split', value: `${framework.qualityWeight || '?'} / ${framework.priceWeight || '?'}`, detail: 'Technical / Commercial' },
          { label: 'Hurdle Gates', value: keyReqs.length, detail: 'Pass/fail requirements' },
          { label: 'Weight Sum', value: `${totalWeight.toFixed(1)}%`, detail: 'Scored sections total' },
          { label: 'API Cost', value: `$${test.apiCost.toFixed(4)}`, detail: `${test.tokensIn} in / ${test.tokensOut} out` },
        ],
      },
      {
        title: 'Scored Response Sections (ranked by weight)',
        subtitle: 'Compare against Part B pages 12-14: Tier 4/5 criteria table',
        type: 'table',
        headers: ['#', 'Reference', 'Weight', 'Category', 'Type', 'Hurdle', 'Question Text'],
        rows: scored
          .sort((a, b) => (b.evaluationMaxScore || 0) - (a.evaluationMaxScore || 0))
          .map(s => [
            s.sectionNumber || '?',
            s.reference || '?',
            `<strong>${s.evaluationMaxScore}%</strong>`,
            `<span class="badge badge-${s.evaluationCategory === 'commercial' ? 'warn' : 'pass'}">${s.evaluationCategory}</span>`,
            s.responseType || '?',
            s.hurdleScore > 0 ? `<span class="badge badge-fail">${s.hurdleScore}</span>` : '—',
            `<div style="font-size:11px;color:#576482;max-width:500px;">${(s.questionText || '').replace(/</g, '&lt;')}</div>`,
          ]),
      },
      {
        title: 'Returnable / Compliance Sections',
        type: 'table',
        headers: ['#', 'Reference', 'Type', 'Hurdle', 'Requirement'],
        rows: sections
          .filter(s => (s.evaluationMaxScore || 0) === 0)
          .map(s => [
            s.sectionNumber || '?',
            s.reference || '?',
            s.responseType || '?',
            s.hurdleScore > 0 ? `<span class="badge badge-fail">PASS/FAIL</span>` : '—',
            `<div style="font-size:11px;max-width:500px;">${(s.questionText || '').replace(/</g, '&lt;')}</div>`,
          ]),
      },
      {
        title: 'Procurement Context',
        type: 'json',
        data: context,
      },
      {
        title: 'Evaluation Framework',
        type: 'json',
        data: framework,
      },
      {
        title: 'Client Scoring Scheme',
        type: 'json',
        data: scoring,
      },
      {
        title: 'Claude Output',
        subtitle: 'Raw text response from the skill execution',
        type: 'text',
        content: result.text || '(no text output)',
      },
    ],
  });
  console.log(`    Review page: ${reviewPath}`);

  // ── Summary ──
  const { passed, failed } = test.summary();
  return { passed, failed, reviewPath, pursuitId };
}

run().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
