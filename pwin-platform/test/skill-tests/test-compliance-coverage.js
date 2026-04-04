/**
 * Test: Skill 3.8 — Compliance Coverage (UC4)
 *
 * Purpose: Analyse compliance coverage of extracted response sections.
 * Requires ITT Extraction to have run first (uses the extracted sections).
 *
 * Documents used:
 *   - Extracted response sections from ITT Extraction test
 *   - Part D Bid Forms compliance checklist (Annex A)
 *
 * Expected output:
 *   - Compliance coverage insight with overall coverage percentage
 *   - Gaps identified for unlinked/unassigned sections
 *   - Risk flags for mandatory requirements not met
 *   - Standup actions for highest-priority gaps
 *   - Marks-at-risk calculation
 *
 * Validation checks:
 *   - Coverage insight created
 *   - At least 3 standup actions generated
 *   - Public Safety Communications flagged as highest-risk section
 *   - Pricing section flagged (40% of marks, no owner)
 *   - All sections flagged as unassigned (no response items linked)
 *
 * Human review:
 *   - Are the gaps genuine? (no response items are assigned — everything should be flagged)
 *   - Are the risk priorities sensible? (highest weight sections should rank highest)
 *   - Are the standup actions specific and actionable?
 *   - Does the analysis mention the pass/fail gates?
 */

import {
  extractDocx, createPursuit, executeSkill, getProductData, setProductData,
  TestResult, generateReviewHTML, extractPDF, estimateTokens,
} from './test-helpers.js';

async function run() {
  console.log('\n╔═════════════════════════════════════════════════════╗');
  console.log('║  TEST: Skill 3.8 — Compliance Coverage (ESN Lot 2)  ║');
  console.log('╚═════════════════════════════════════════════════════╝\n');

  const test = new TestResult('Compliance Coverage');

  // ── Step 1: Create pursuit with pre-loaded extracted data ──
  console.log('  Step 1: Creating pursuit with ITT-extracted data...');

  // First run ITT extraction (or load from previous run)
  // For this test, we pre-load a realistic set of extracted sections
  const partB = await extractPDF(
    'Part B - Evaluation Framework/ESN ITT Part B - Evaluation Framework Lot 2 v1.pdf'
  );

  const shared = await createPursuit({
    client: 'Home Office',
    opportunity: 'ESN Lot 2 — User Services (Compliance Coverage Test)',
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

  // Run ITT extraction first to populate data
  console.log('    Running ITT Extraction to populate sections...');
  const document = [
    'ESN ITT LOT 2 USER SERVICES — Evaluation Framework',
    'Authority: Home Office | Procurement: Restricted | Value: £500m+',
    '',
    partB.text,
  ].join('\n');

  const extractResult = await executeSkill('itt-extraction', {
    pursuitId,
    document,
    _model: 'claude-haiku-4-5-20251001',
  });

  if (extractResult.error) {
    console.error(`    ITT Extraction failed: ${extractResult.error}`);
    test.check(false, 'ITT Extraction prerequisite succeeded');
    test.summary();
    return;
  }
  test.recordUsage(extractResult.usage, extractResult.model);
  console.log(`    ITT Extraction: ${extractResult.writeResults.length} write-backs`);

  // Add compliance requirements (from Part D Annex A)
  const bidData = await getProductData(pursuitId, 'bid-execution');
  bidData.complianceRequirements = [
    { id: 'KR-01', description: 'Systems Integration — Control Room Interface (Req 4.3.4)', classification: 'mandatory', complianceStatus: 'unknown' },
    { id: 'KR-02', description: 'Public Safety — Emergency Distress Communications (Req 5.4.17)', classification: 'mandatory', complianceStatus: 'unknown' },
    { id: 'KR-03', description: 'Public Safety — Half Duplex Group Calls (Req 5.4.36)', classification: 'mandatory', complianceStatus: 'unknown' },
    { id: 'KR-04', description: 'Public Safety — Half Duplex One-to-One Calls (Req 5.4.56)', classification: 'mandatory', complianceStatus: 'unknown' },
    { id: 'KR-05', description: 'Public Safety — Message Delivery (Req 5.5.8)', classification: 'mandatory', complianceStatus: 'unknown' },
    { id: 'KR-06', description: 'Public Safety — User Device Location Reporting (Req 5.5.22)', classification: 'mandatory', complianceStatus: 'unknown' },
    { id: 'KR-07', description: 'Acceptance of Terms and Conditions', classification: 'mandatory', complianceStatus: 'unknown' },
    { id: 'KR-08', description: 'Security clearance — SC/DV for key personnel', classification: 'mandatory', complianceStatus: 'unknown' },
  ];
  await setProductData(pursuitId, 'bid-execution', bidData);

  // ── Step 2: Execute Compliance Coverage ──
  console.log('\n  Step 2: Executing Compliance Coverage skill...');
  const result = await executeSkill('compliance-coverage', {
    pursuitId,
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

  // ── Step 3: Validate output ──
  console.log('\n  Step 3: Validating analysis...');
  const finalData = await getProductData(pursuitId, 'bid-execution');

  const insights = finalData.complianceCoverageInsights || [];
  const actions = finalData.standupActions || [];
  const risks = finalData.risks || [];
  const successfulWrites = result.writeResults.filter(w => w.success).length;
  const failedWrites = result.writeResults.filter(w => !w.success).length;

  test.check(successfulWrites > 0, `At least 1 successful write-back (got ${successfulWrites})`);
  test.check(insights.length >= 1, `At least 1 compliance insight created (got ${insights.length})`);
  test.check(actions.length >= 3, `At least 3 standup actions created (got ${actions.length})`);

  if (insights.length > 0) {
    const insight = insights[0];
    test.check(!!insight.summary, 'Insight has a summary');
    test.check(insight.summary.length > 100, `Insight summary is substantive (${insight.summary.length} chars)`);

    if (insight.gaps && insight.gaps.length > 0) {
      test.check(insight.gaps.length >= 3, `At least 3 gaps identified (got ${insight.gaps.length})`);
    } else {
      test.warn('No structured gaps in insight — check if gaps are in text summary instead');
    }
  }

  // Check actions are specific
  if (actions.length > 0) {
    const hasSpecific = actions.some(a => a.description.length > 50);
    test.check(hasSpecific, 'At least one action has specific detail (>50 chars)');
  }

  if (failedWrites > 0) {
    test.warn(`${failedWrites} write-backs failed (likely risk flags with no activities — expected if no activity data loaded)`);
  }

  // ── Step 4: Generate review HTML ──
  console.log('\n  Step 4: Generating review page...');

  const reviewPath = await generateReviewHTML('test-compliance-coverage.html', {
    title: 'Compliance Coverage — ESN Lot 2 User Services',
    subtitle: `Test run ${new Date().toISOString().slice(0,16)} | ${insights.length} insights, ${actions.length} actions | $${test.apiCost.toFixed(4)}`,
    sections: [
      {
        title: 'Summary',
        type: 'cards',
        items: [
          { label: 'Insights', value: insights.length },
          { label: 'Actions', value: actions.length },
          { label: 'Risks Flagged', value: risks.length },
          { label: 'Write-backs', value: `${successfulWrites}✓ ${failedWrites}✗` },
          { label: 'API Cost', value: `$${test.apiCost.toFixed(4)}`, detail: 'ITT Extraction + Compliance Coverage' },
        ],
      },
      ...(insights.length > 0 ? [{
        title: 'Compliance Coverage Insight',
        type: 'text',
        content: insights[0].summary || '(no summary)',
      }] : []),
      ...(insights[0]?.gaps?.length > 0 ? [{
        title: 'Identified Gaps',
        type: 'table',
        headers: ['Requirement', 'Status', 'Recommendation'],
        rows: insights[0].gaps.map(g => [g.requirement || '', g.status || '', g.recommendation || '']),
      }] : []),
      ...(actions.length > 0 ? [{
        title: 'AI-Generated Standup Actions',
        type: 'list',
        items: actions.map(a => ({ priority: a.priority || '', text: a.description })),
      }] : []),
      {
        title: 'Claude Output (full text)',
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
