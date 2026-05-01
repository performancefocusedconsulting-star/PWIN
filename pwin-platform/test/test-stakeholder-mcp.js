/**
 * Tests for competitive-intel.js stakeholder query functions.
 * Requires a bid_intel.db with at least one stakeholder row.
 * Run after Task 3 has ingested at least one department.
 */

import { getStakeholders, getStakeholderByName, findEvaluators } from '../src/competitive-intel.js';

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  PASS: ${message}`);
    passed++;
  } else {
    console.error(`  FAIL: ${message}`);
    failed++;
  }
}

console.log('\n=== Stakeholder MCP functions ===\n');

// getStakeholders — valid buyer
console.log('getStakeholders("HM Treasury")');
const result1 = getStakeholders('HM Treasury');
assert(!result1.error, 'no error for known buyer');
assert(Array.isArray(result1.stakeholders), 'stakeholders is an array');
if (result1.stakeholders.length > 0) {
  const first = result1.stakeholders[0];
  assert('name_normalised' in first, 'has name_normalised');
  assert('scs_band_inferred' in first, 'has scs_band_inferred');
  assert('job_title' in first, 'has job_title');
}

// getStakeholders — tier filter
console.log('\ngetStakeholders("HM Treasury", { tier: "DirectorGeneral" })');
const result2 = getStakeholders('HM Treasury', { tier: 'DirectorGeneral' });
assert(!result2.error, 'no error with tier filter');
if (result2.stakeholders.length > 0) {
  assert(
    result2.stakeholders.every(s => s.scs_band_inferred === 'DirectorGeneral'),
    'all results match the requested tier'
  );
}

// getStakeholders — unknown buyer
console.log('\ngetStakeholders("XYZZY Unknown Dept")');
const result3 = getStakeholders('XYZZY Unknown Dept');
assert(!result3.error || result3.stakeholders !== undefined, 'returns gracefully for unknown buyer');

// getStakeholderByName
console.log('\ngetStakeholderByName("Gallagher")');
const result4 = getStakeholderByName('Gallagher');
assert(!result4.error, 'no error');
assert('results' in result4, 'has results field');
assert(typeof result4.count === 'number', 'has count field');

// findEvaluators
console.log('\nfindEvaluators("HM Treasury")');
const result5 = findEvaluators('HM Treasury');
assert(!result5.error, 'no error');
assert('pac_witnesses' in result5, 'has pac_witnesses field');
assert(Array.isArray(result5.pac_witnesses), 'pac_witnesses is an array');

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
