/**
 * Test: Skill 1.5 — Procurement Briefing
 *
 * Purpose: Produce a strategic narrative briefing from the full ITT documentation.
 * This is the "day one" briefing the bid team receives after ITT lands.
 *
 * Documents used:
 *   - Part A: Information Document (FULL 124 pages)
 *   - Part B: Evaluation Framework Lot 2 (pages 1-18 — criteria and weights)
 *
 * Expected output:
 *   - A narrative report (generate_report_output) covering:
 *     Programme overview and strategic context
 *     Lot 2 scope and responsibilities
 *     Evaluation model and scoring methodology
 *     Key risks and watch items
 *     Cross-lot dependencies
 *     TUPE implications
 *     Procurement timeline and key dates
 *     Recommended bid strategy considerations
 *
 * Validation checks:
 *   - Report generated (at least 1 write-back)
 *   - Report content > 2000 chars (substantive briefing)
 *   - Mentions ESN / Emergency Services Network
 *   - Mentions Airwave (the system being replaced)
 *   - Mentions TUPE
 *   - Mentions at least 2 lots by name
 *   - Mentions evaluation model (MEAT / 70/30)
 *   - Sector-specific context (Emergency Services) present
 *
 * Human review:
 *   - Is this a briefing you'd give a bid team on day one?
 *   - Does it capture the strategic significance of the programme?
 *   - Are the risks genuine and ESN-specific, not generic?
 *   - Would a bid manager learn something actionable from reading it?
 */

import {
  extractPDF, createPursuit, executeSkill, getProductData,
  TestResult, generateReviewHTML, estimateTokens,
} from './test-helpers.js';

async function run() {
  console.log('\n╔════════════════════════════════════════════════════════╗');
  console.log('║  TEST: Skill 1.5 — Procurement Briefing (ESN Lot 2)    ║');
  console.log('╚════════════════════════════════════════════════════════╝\n');

  const test = new TestResult('Procurement Briefing');

  // ── Step 1: Extract document text ──
  console.log('  Step 1: Extracting document text...');

  // Part A — FULL document (124 pages)
  const partA = await extractPDF(
    'Part A - Information/ESN ITT Part A - Information Document final 20140808.pdf'
  );
  console.log(`    Part A: ${partA.pages} pages, ${partA.chars} chars (FULL — no truncation)`);

  // Part B Lot 2 — criteria pages only (1-18)
  const partB = await extractPDF(
    'Part B - Evaluation Framework/ESN ITT Part B - Evaluation Framework Lot 2 v1.pdf',
    { pages: Array.from({length: 18}, (_, i) => i) }
  );
  console.log(`    Part B: 18 pages, ${partB.chars} chars`);

  const document = [
    '=== ESN ITT PART A: INFORMATION DOCUMENT (FULL — 124 PAGES) ===',
    partA.text,
    '',
    '=== PART B: LOT 2 EVALUATION FRAMEWORK (Criteria and Weights) ===',
    partB.text,
  ].join('\n');

  const totalTokens = estimateTokens(document);
  console.log(`    Combined: ${document.length} chars (~${totalTokens} tokens)`);

  // ── Step 2: Create pursuit ──
  console.log('\n  Step 2: Creating test pursuit...');
  const shared = await createPursuit({
    client: 'Home Office',
    opportunity: 'ESN Lot 2 — User Services (Procurement Briefing Test)',
    sector: 'Emergency Services',
    tcv: 500000000,
    opportunityType: 'IT Outsourcing',
    procurementRoute: 'restricted',
    createdBy: 'bid_execution',
  });
  const pursuitId = shared.pursuit.id;
  console.log(`    Pursuit: ${pursuitId}`);

  // ── Step 3: Execute skill ──
  console.log('\n  Step 3: Executing Procurement Briefing skill...');
  const result = await executeSkill('procurement-briefing', {
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
  console.log('\n  Step 4: Validating briefing...');

  const bidData = await getProductData(pursuitId, 'bid-execution');
  const reports = bidData.reports || [];
  const successfulWrites = result.writeResults.filter(w => w.success).length;

  test.check(successfulWrites >= 1, `At least 1 successful write-back (got ${successfulWrites})`);
  test.check(reports.length >= 1, `At least 1 report generated (got ${reports.length})`);

  // Combine all text output (report content + Claude text)
  const reportContent = reports.map(r => r.content || '').join('\n');
  const allText = (result.text || '') + '\n' + reportContent;

  test.check(allText.length > 2000, `Briefing is substantive (${allText.length} chars)`);
  test.check(/ESN|Emergency Services Network/i.test(allText), 'Mentions ESN / Emergency Services Network');
  test.check(/Airwave/i.test(allText), 'Mentions Airwave (system being replaced)');
  test.check(/TUPE/i.test(allText), 'Mentions TUPE');
  test.check(/Lot [12]/i.test(allText) && /Lot [34]/i.test(allText), 'Mentions at least 2 lots by name');
  test.check(/MEAT|70.*30|30.*70|quality.*70|technical.*70/i.test(allText), 'Mentions evaluation model (MEAT / 70-30)');
  test.check(/Emergency Services|blue light|police|fire|ambulance/i.test(allText), 'Contains Emergency Services sector context');

  // ── Step 5: Generate review HTML ──
  console.log('\n  Step 5: Generating review page...');

  const reviewPath = await generateReviewHTML('test-procurement-briefing.html', {
    title: 'Procurement Briefing — ESN Lot 2 User Services',
    subtitle: `Test run ${new Date().toISOString().slice(0,16)} | ${allText.length} chars | $${test.apiCost.toFixed(4)}`,
    sections: [
      {
        title: 'Summary',
        type: 'cards',
        items: [
          { label: 'Report Length', value: `${allText.length}`, detail: 'characters' },
          { label: 'Documents Ingested', value: `${partA.pages + 18}`, detail: 'pages (Part A full + Part B criteria)' },
          { label: 'API Cost', value: `$${test.apiCost.toFixed(4)}` },
        ],
      },
      {
        title: 'Strategic Briefing',
        subtitle: 'This is what the bid team would receive on day one of the pursuit',
        type: 'text',
        content: allText || '(no output)',
      },
    ],
  });
  console.log(`    Review page: ${reviewPath}`);

  const { passed, failed } = test.summary();
  return { passed, failed, reviewPath, pursuitId };
}

run().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
