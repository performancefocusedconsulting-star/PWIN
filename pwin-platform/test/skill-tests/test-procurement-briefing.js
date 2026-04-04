/**
 * Test: Skill 1.5 — Procurement Briefing
 *
 * GENERIC TEST — validates that the skill produces a substantive strategic
 * briefing from any ITT document. No hard-coded content expectations.
 *
 * STRUCTURAL (automated — any document):
 *   - Skill executes without error
 *   - Report generated (at least 1 write-back)
 *   - Output is substantive (> 2000 chars)
 *   - Output mentions the client name from the pursuit context
 *   - Output contains structured sections (headings or clear structure)
 *   - Output mentions evaluation or scoring (must address how the bid is assessed)
 *   - Output mentions risk or challenge (must surface strategic concerns)
 *
 * QUALITY (human review via HTML page):
 *   - Would you give this briefing to a bid team on day one?
 *   - Does it capture the strategic significance of the opportunity?
 *   - Are risks genuine and specific, not generic?
 *   - Does it cover: scope, evaluation model, timeline, key risks, TUPE, dependencies?
 *   - Would a bid manager learn something actionable from it?
 */

import {
  extractPDF, createPursuit, executeSkill, getProductData,
  TestResult, generateReviewHTML, estimateTokens,
} from './test-helpers.js';

// ═══════════════════════════════════════════════════════════════
// DATASET CONFIGURATION
// ═══════════════════════════════════════════════════════════════

const DATASET = {
  name: 'ESN Lot 2 — User Services',
  pursuit: {
    client: 'Home Office',
    opportunity: 'ESN Lot 2 — Procurement Briefing Test',
    sector: 'Emergency Services',
    tcv: 500000000,
    opportunityType: 'IT Outsourcing',
    procurementRoute: 'restricted',
    createdBy: 'bid_execution',
  },
  documents: [
    {
      path: 'Part A - Information/ESN ITT Part A - Information Document final 20140808.pdf',
      label: 'ITT Information Document (full)',
      pages: null, // all pages
    },
    {
      path: 'Part B - Evaluation Framework/ESN ITT Part B - Evaluation Framework Lot 2 v1.pdf',
      label: 'Evaluation Framework (criteria)',
      pages: Array.from({length: 18}, (_, i) => i), // pages 1-18 only
    },
  ],
  model: 'claude-haiku-4-5-20251001',
};

// ═══════════════════════════════════════════════════════════════

async function run() {
  console.log(`\n╔═══════════════════════════════════════════════════════╗`);
  console.log(`║  TEST: Procurement Briefing — ${DATASET.name.padEnd(22)}║`);
  console.log(`╚═══════════════════════════════════════════════════════╝\n`);

  const test = new TestResult(`Procurement Briefing: ${DATASET.name}`);

  // ── Step 1: Extract documents ──
  console.log('  Step 1: Extracting documents...');
  const docParts = [];
  for (const doc of DATASET.documents) {
    const extracted = await extractPDF(doc.path, { pages: doc.pages });
    console.log(`    ${doc.label}: ${extracted.extractedPages}/${extracted.pageCount} pages, ${extracted.chars} chars`);
    docParts.push(`=== ${doc.label.toUpperCase()} ===\n${extracted.text}`);
  }
  const document = docParts.join('\n\n');
  console.log(`    Combined: ~${estimateTokens(document)} tokens`);

  // ── Step 2: Create pursuit ──
  console.log('\n  Step 2: Creating pursuit...');
  const shared = await createPursuit(DATASET.pursuit);
  const pursuitId = shared.pursuit.id;
  console.log(`    Pursuit: ${pursuitId}`);

  // ── Step 3: Execute skill ──
  console.log('\n  Step 3: Executing Procurement Briefing...');
  const result = await executeSkill('procurement-briefing', {
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
  const reports = bid.reports || [];
  const successfulWrites = result.writeResults.filter(w => w.success).length;

  test.check(successfulWrites >= 1, `At least 1 write-back succeeded (${successfulWrites})`);
  test.check(reports.length >= 1, `Report generated (${reports.length})`);

  // Combine all output text
  const reportContent = reports.map(r => r.content || '').join('\n');
  const allText = ((result.text || '') + '\n' + reportContent).trim();

  // --- Substantive output ---
  test.check(allText.length > 2000, `Output is substantive (${allText.length} chars)`);

  if (allText.length < 500) {
    test.fail('Output too short to be a useful briefing');
    test.summary();
    return;
  }

  // --- Contains client reference ---
  const clientName = DATASET.pursuit.client;
  const mentionsClient = new RegExp(clientName, 'i').test(allText);
  test.check(mentionsClient, `Mentions the client (${clientName})`);

  // --- Contains evaluation/scoring content ---
  const mentionsEvaluation = /evaluat|scor|criteria|weight|MEAT|quality.*price|price.*quality/i.test(allText);
  test.check(mentionsEvaluation, 'Mentions evaluation, scoring, or criteria');

  // --- Contains risk/challenge content ---
  const mentionsRisk = /risk|challenge|concern|threat|issue|mitigation|vulnerab/i.test(allText);
  test.check(mentionsRisk, 'Mentions risks, challenges, or concerns');

  // --- Has structure (headings or sections) ---
  const hasStructure = /^#{1,3} |^\*\*[A-Z]|\n[A-Z][a-z]+ [A-Z]|\d\.\s+[A-Z]/m.test(allText);
  test.check(hasStructure, 'Output has visible structure (headings or numbered sections)');

  // --- Sector relevance ---
  const sector = DATASET.pursuit.sector;
  if (sector) {
    const sectorTerms = {
      'Emergency Services': /emergency|police|fire|ambulance|blue light|999|public safety/i,
      'Defence': /defence|defense|MOD|military|DE&S/i,
      'Justice': /justice|probation|HMPPS|prison|MoJ/i,
      'Central Government': /cabinet office|government|departmental|whitehall/i,
      'NHS / Health': /NHS|health|ICB|clinical|hospital/i,
    };
    const pattern = sectorTerms[sector];
    if (pattern) {
      test.check(pattern.test(allText), `Contains sector-relevant language (${sector})`);
    }
  }

  // ── Step 5: Generate review HTML ──
  console.log('\n  Step 5: Generating review page...');

  const reviewPath = await generateReviewHTML(`test-procurement-briefing-${Date.now()}.html`, {
    title: `Procurement Briefing — ${DATASET.name}`,
    subtitle: `${new Date().toISOString().slice(0, 16)} | ${allText.length} chars | $${test.apiCost.toFixed(4)}`,
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
          { label: 'Output Length', value: String(allText.length), detail: 'characters' },
          { label: 'Documents Fed', value: String(DATASET.documents.length) },
          { label: 'Reports Created', value: String(reports.length) },
          { label: 'Cost', value: `$${test.apiCost.toFixed(4)}` },
        ],
      },
      {
        title: 'Strategic Briefing — REVIEW THIS',
        subtitle: 'Would you give this to a bid team on day one? Is it specific, actionable, and strategically useful?',
        type: 'text',
        content: allText,
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
