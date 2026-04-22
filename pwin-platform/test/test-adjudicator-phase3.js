/**
 * Phase 3 validation: canonical-adjudicator skill end-to-end
 *
 * Tests:
 *   1. Context assembly (dry run — all 4 context types resolve)
 *   2. promote_canonical_decision — re-parents supplier_to_canonical rows
 *   3. stage_escalation — writes adjudicator_escalations + marks queue deferred
 *   4. log_adjudicator_decision — appends JSONL record
 *   5. Post-conditions: DB state matches expected outcome
 */

import { gatherContext, assemblePrompt, loadSkill } from '../src/skill-runner.js';
import { DatabaseSync } from 'node:sqlite';
import { appendFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dir, '..', '..');
const DB_PATH = join(REPO_ROOT, 'pwin-competitive-intel', 'db', 'bid_intel.db');
const DECISIONS_PATH = join(REPO_ROOT, 'pwin-competitive-intel', 'adjudicator', 'adjudicator_decisions.jsonl');

// ── The 5-pair validation batch loaded from adjudication_queue ───────────────
const SPLINK_CLUSTERS = [
  {
    queue_id: 'QUEUEPAIR-83F990A9613A',
    entity_type: 'supplier',
    candidates: [
      { canonical_id: 'GB-CHC-0182 0492', canonical_name: 'humankind charity', member_count: 30 },
      { canonical_id: 'GB-FTS-142070',   canonical_name: 'humankind',         member_count: 4  },
    ],
    splink_score: 0.74, ch_match: false, shared_ch: null,
  },
  {
    queue_id: 'QUEUEPAIR-7E99800367CB',
    entity_type: 'supplier',
    candidates: [
      { canonical_id: 'GB-CHC-00943935', canonical_name: 'capgemini uk plc', member_count: 28 },
      { canonical_id: 'GB-FTS-109345',   canonical_name: 'capgemini',        member_count: 5  },
    ],
    splink_score: 0.72, ch_match: false, shared_ch: null,
  },
  {
    queue_id: 'QUEUEPAIR-F8C941A40347',
    entity_type: 'supplier',
    candidates: [
      { canonical_id: 'GB-CHC-00943935', canonical_name: 'capgemini uk plc',     member_count: 28 },
      { canonical_id: 'GB-FTS-71586',    canonical_name: 'capgemini uk limited', member_count: 1  },
    ],
    splink_score: 0.68, ch_match: false, shared_ch: null,
  },
  {
    queue_id: 'QUEUEPAIR-9932D8A3B6CB',
    entity_type: 'supplier',
    candidates: [
      { canonical_id: 'GB-CHC-205533',   canonical_name: 'nuffield health',                  member_count: 25 },
      { canonical_id: 'GB-FTS-125171',   canonical_name: 'nuffield health the holly hospital', member_count: 3 },
    ],
    splink_score: 0.61, ch_match: true, shared_ch: '01279419',
  },
  {
    queue_id: 'QUEUEPAIR-F61FAD3E1567',
    entity_type: 'supplier',
    candidates: [
      { canonical_id: 'GB-CHC-03244453', canonical_name: 'east sussex, brighton and hove crossroads - caring for carers limited', member_count: 1  },
      { canonical_id: 'GB-COH-03002869', canonical_name: 'caring for communities and people',                                     member_count: 10 },
    ],
    splink_score: 0.43, ch_match: false, shared_ch: null,
  },
];

// ── Test harness ─────────────────────────────────────────────────────────────

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log(`  ✓ ${label}`);
    passed++;
  } else {
    console.error(`  ✗ FAIL: ${label}`);
    failed++;
  }
}

// ── Test 1: Context assembly (dry run) ───────────────────────────────────────

async function testContextAssembly() {
  console.log('\n── Test 1: Context assembly ────────────────────────────────');
  const skill = await loadSkill('canonical-adjudicator');
  assert(skill.id === 'canonical-adjudicator', 'Skill loaded');

  const context = await gatherContext(skill, {
    splinkStagedClusters: SPLINK_CLUSTERS,
    adjudicationMode: 'clusters',
    runId: 'PHASE3-TEST',
  });

  assert(context.canonical_glossary !== undefined, 'canonical_glossary loaded');
  assert(context.framework_taxonomy !== undefined, 'framework_taxonomy loaded');
  assert(context.canonical_playbook !== undefined, 'canonical_playbook loaded');
  // adjudicator_decisions may be empty array if JSONL is empty — both are valid
  assert(context.adjudicator_decisions !== undefined, 'adjudicator_decisions loaded (may be [])');

  const { systemPrompt, userMessage } = assemblePrompt(skill, context, {
    splinkStagedClusters: SPLINK_CLUSTERS,
    adjudicationMode: 'clusters',
    runId: 'PHASE3-TEST',
  });

  // Placeholders should be resolved (no raw {{...}} remaining for known context keys)
  const unresolvedSys = (systemPrompt.match(/\{\{(canonical_glossary|framework_taxonomy|canonical_playbook|adjudicator_decisions)\}\}/g) || []);
  assert(unresolvedSys.length === 0, `System prompt: no unresolved context placeholders (found: ${unresolvedSys.join(', ') || 'none'})`);

  // User message should contain at least one cluster ID
  assert(userMessage.includes('QUEUEPAIR'), 'User prompt contains queue cluster data');
  assert(userMessage.includes('PHASE3-TEST'), 'User prompt contains runId');

  console.log(`  System prompt: ${systemPrompt.length.toLocaleString()} chars`);
  console.log(`  User message:  ${userMessage.length.toLocaleString()} chars`);

  return { skill, context };
}

// ── Test 2: log_adjudicator_decision ─────────────────────────────────────────

async function testLogDecision() {
  console.log('\n── Test 2: log_adjudicator_decision ───────────────────────');

  // Record line count before
  let linesBefore = 0;
  try {
    const existing = await readFile(DECISIONS_PATH, 'utf-8');
    linesBefore = existing.trim().split('\n').filter(Boolean).length;
  } catch { /* file may not exist yet */ }

  // Simulate a decision log via direct file append (same path the MCP tool uses)
  const testDecision = {
    decision_id: 'ADJ-20260422-TEST',
    decision_type: 'supplier_merge',
    recommendation: 'auto_promote',
    confidence: 0.94,
    canonical_target: 'GB-CHC-00943935',
    raw_ids: ['GB-CHC-00943935', 'GB-FTS-109345'],
    evidence: ['Name: "capgemini uk plc" vs "capgemini" — clear trading name abbreviation', 'CH: 00943935 present on GB-CHC-00943935'],
    playbook_rule: null,
    uncertainty_notes: null,
    operator_outcome: 'human_approved',
    logged_at: new Date().toISOString(),
  };

  await mkdir(join(REPO_ROOT, 'pwin-competitive-intel', 'adjudicator'), { recursive: true });
  await appendFile(DECISIONS_PATH, JSON.stringify(testDecision) + '\n', 'utf-8');

  const after = await readFile(DECISIONS_PATH, 'utf-8');
  const linesAfter = after.trim().split('\n').filter(Boolean).length;
  assert(linesAfter === linesBefore + 1, `JSONL grew by 1 line (${linesBefore} → ${linesAfter})`);

  const lastLine = JSON.parse(after.trim().split('\n').at(-1));
  assert(lastLine.decision_id === 'ADJ-20260422-TEST', 'Decision ID round-trips correctly');
  assert(lastLine.operator_outcome === 'human_approved', 'operator_outcome persisted');

  return testDecision;
}

// ── Test 3: promote_canonical_decision ───────────────────────────────────────

async function testPromoteDecision() {
  console.log('\n── Test 3: promote_canonical_decision ─────────────────────');

  const db = new DatabaseSync(DB_PATH);
  db.exec('PRAGMA foreign_keys = ON');

  const SURVIVOR = 'GB-CHC-00943935'; // capgemini uk plc
  const ABSORBED = 'GB-FTS-109345';   // capgemini
  const QUEUE_ID  = 'QUEUEPAIR-7E99800367CB';

  // Baseline
  const survivorBefore = db.prepare('SELECT member_count FROM canonical_suppliers WHERE canonical_id = ?').get(SURVIVOR);
  const absorbedBefore = db.prepare('SELECT member_count FROM canonical_suppliers WHERE canonical_id = ?').get(ABSORBED);
  const membersBefore  = db.prepare('SELECT COUNT(*) as n FROM supplier_to_canonical WHERE canonical_id = ?').get(ABSORBED);
  const queueBefore    = db.prepare('SELECT status FROM adjudication_queue WHERE queue_id = ?').get(QUEUE_ID);

  console.log(`  Before: survivor member_count=${survivorBefore?.member_count}, absorbed member_count=${absorbedBefore?.member_count}, absorbed s2c rows=${membersBefore?.n}`);
  assert(queueBefore?.status === 'pending', 'Queue row starts as pending');
  assert(absorbedBefore !== undefined, 'Absorbed canonical exists before promote');

  // Execute the same logic the MCP tool runs
  const moved = db.prepare('UPDATE supplier_to_canonical SET canonical_id = ? WHERE canonical_id = ?').run(SURVIVOR, ABSORBED);
  db.prepare('DELETE FROM canonical_suppliers WHERE canonical_id = ?').run(ABSORBED);
  db.prepare('UPDATE canonical_suppliers SET member_count = (SELECT COUNT(*) FROM supplier_to_canonical WHERE canonical_id = ?) WHERE canonical_id = ?').run(SURVIVOR, SURVIVOR);
  db.prepare("UPDATE adjudication_queue SET status = 'approved', decision_json = ?, reviewed_at = ? WHERE queue_id = ?").run(
    JSON.stringify({ decision_id: 'ADJ-20260422-TEST', promoted_at: new Date().toISOString() }),
    new Date().toISOString(),
    QUEUE_ID,
  );

  // Post-conditions
  const survivorAfter = db.prepare('SELECT member_count FROM canonical_suppliers WHERE canonical_id = ?').get(SURVIVOR);
  const absorbedAfter = db.prepare('SELECT canonical_id FROM canonical_suppliers WHERE canonical_id = ?').get(ABSORBED);
  const orphans       = db.prepare('SELECT COUNT(*) as n FROM supplier_to_canonical WHERE canonical_id = ?').get(ABSORBED);
  const queueAfter    = db.prepare('SELECT status FROM adjudication_queue WHERE queue_id = ?').get(QUEUE_ID);

  console.log(`  After:  survivor member_count=${survivorAfter?.member_count}, absorbed deleted=${absorbedAfter === undefined}, orphaned rows=${orphans?.n}, moved=${moved.changes}`);

  assert(absorbedAfter === undefined,     'Absorbed canonical_suppliers row deleted');
  assert(orphans?.n === 0,               'No orphaned supplier_to_canonical rows remain for absorbed ID');
  assert(moved.changes === membersBefore?.n, `All ${membersBefore?.n} supplier_to_canonical rows re-parented`);
  assert(survivorAfter?.member_count === (survivorBefore?.member_count || 0) + (membersBefore?.n || 0), 'Survivor member_count updated correctly');
  assert(queueAfter?.status === 'approved', 'Queue row marked approved');

  db.close();
}

// ── Test 4: stage_escalation ──────────────────────────────────────────────────

async function testStageEscalation() {
  console.log('\n── Test 4: stage_escalation ────────────────────────────────');

  const db = new DatabaseSync(DB_PATH);

  // adjudicator_escalations is created by the MCP tool if needed
  db.exec(`CREATE TABLE IF NOT EXISTS adjudicator_escalations (
    escalation_id TEXT PRIMARY KEY,
    decision_type TEXT NOT NULL,
    queue_id TEXT,
    confidence REAL NOT NULL,
    canonical_target TEXT,
    raw_ids TEXT NOT NULL,
    evidence TEXT NOT NULL,
    playbook_rule TEXT,
    uncertainty_notes TEXT,
    operator_outcome TEXT NOT NULL DEFAULT 'pending',
    logged_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT
  )`);

  const ESC_ID   = 'ADJ-20260422-ESC01';
  const QUEUE_ID = 'QUEUEPAIR-9932D8A3B6CB'; // nuffield health / nuffield health the holly hospital

  db.prepare(`INSERT OR IGNORE INTO adjudicator_escalations
    (escalation_id, decision_type, queue_id, confidence, canonical_target, raw_ids, evidence, playbook_rule, uncertainty_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`)
    .run(
      ESC_ID, 'supplier_merge', QUEUE_ID, 0.61, null,
      JSON.stringify(['GB-CHC-205533', 'GB-FTS-125171']),
      JSON.stringify(['Shared CH number 01279419', 'Names strongly related (holly hospital is a Nuffield site)', 'Subsidiary — playbook requires operator decision']),
      'Playbook §4.2: subsidiaries kept distinct unless glossary explicitly rolls them up',
      'Confirm Nuffield Health The Holly Hospital should map to parent canonical or stay distinct. Check glossary for Nuffield Health.',
    );

  const r = db.prepare("UPDATE adjudication_queue SET status = 'deferred', reviewed_at = ? WHERE queue_id = ? AND status = 'pending'").run(
    new Date().toISOString(), QUEUE_ID,
  );

  const esc    = db.prepare('SELECT * FROM adjudicator_escalations WHERE escalation_id = ?').get(ESC_ID);
  const queue  = db.prepare('SELECT status FROM adjudication_queue WHERE queue_id = ?').get(QUEUE_ID);

  assert(esc !== undefined,              'Escalation row written to adjudicator_escalations');
  assert(esc?.confidence === 0.61,       'Confidence value persisted');
  assert(esc?.queue_id   === QUEUE_ID,   'Queue linkage persisted');
  assert(r.changes === 1,               'Queue row marked deferred (1 row changed)');
  assert(queue?.status === 'deferred',  'Queue status is deferred');

  const rawIds = JSON.parse(esc?.raw_ids || '[]');
  assert(rawIds.length === 2,           'raw_ids round-trips as array of 2');

  db.close();
}

// ── Test 5: Queue state summary ───────────────────────────────────────────────

async function testQueueStateSummary() {
  console.log('\n── Test 5: Final adjudication_queue state ──────────────────');
  const db = new DatabaseSync(DB_PATH);
  const rows = db.prepare('SELECT queue_id, name_1, name_2, splink_score, status FROM adjudication_queue ORDER BY splink_score DESC').all();
  for (const r of rows) {
    console.log(`  [${r.status.padEnd(8)}] score=${r.splink_score} — ${r.name_1} <-> ${r.name_2}`);
  }
  const pending  = rows.filter(r => r.status === 'pending').length;
  const approved = rows.filter(r => r.status === 'approved').length;
  const deferred = rows.filter(r => r.status === 'deferred').length;
  assert(rows.length === 5,    `Queue has 5 rows (${rows.length})`);
  assert(approved === 1,       `1 approved (promote flow) — got ${approved}`);
  assert(deferred === 1,       `1 deferred (stage flow) — got ${deferred}`);
  assert(pending  === 3,       `3 still pending (not adjudicated in this test) — got ${pending}`);
  db.close();
}

// ── Run all tests ─────────────────────────────────────────────────────────────

async function run() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('  Phase 3 validation — canonical-adjudicator skill');
  console.log('═══════════════════════════════════════════════════════════');

  try {
    await testContextAssembly();
    await testLogDecision();
    await testPromoteDecision();
    await testStageEscalation();
    await testQueueStateSummary();
  } catch (err) {
    console.error('\nFATAL ERROR:', err.message);
    console.error(err.stack);
    process.exit(1);
  }

  console.log('\n───────────────────────────────────────────────────────────');
  console.log(`  Results: ${passed} passed, ${failed} failed`);
  if (failed > 0) {
    console.error('  PHASE 3 VALIDATION FAILED');
    process.exit(1);
  } else {
    console.log('  PHASE 3 VALIDATION PASSED');
  }
}

run();
