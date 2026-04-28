/**
 * PWIN Platform — buyerProfile consolidation regression test
 *
 * Hits the real competitive-intel database. Ensures get_buyer_profile
 * returns one consolidated row per canonical buyer rather than fragments.
 *
 * Run: node test/test-buyer-profile.js
 */
import { buyerProfile } from '../src/competitive-intel.js';

let passed = 0, failed = 0;

function check(label, condition, detail) {
  if (condition) { passed++; console.log(`  PASS ${label}`); }
  else           { failed++; console.error(`  FAIL ${label}`, detail !== undefined ? `(got: ${JSON.stringify(detail)})` : ''); }
}

console.log('\n=== buyerProfile consolidation tests ===\n');

const moj = buyerProfile('Ministry of Justice');
const mojRow = moj.buyers?.[0];
check('MoJ resolves to one row', moj.buyers?.length === 1, moj.buyers?.length);
check('MoJ row carries canonical metadata', !!mojRow?.canonical?.canonicalId, mojRow?.canonical);
check('MoJ rolls up many member rows', (mojRow?.canonical?.memberCount || 0) > 100, mojRow?.canonical?.memberCount);
check('MoJ has awards', (mojRow?.stats?.totalAwards || 0) > 0, mojRow?.stats?.totalAwards);

const mod = buyerProfile('MOD');
const modRow = mod.buyers?.[0];
check('MOD abbreviation resolves to MoD canonical',
  modRow?.canonical?.canonicalName === 'Ministry of Defence',
  modRow?.canonical?.canonicalName);

const dft = buyerProfile('DfT');
check('DfT resolves to Department for Transport',
  dft.buyers?.[0]?.canonical?.canonicalName === 'Department for Transport',
  dft.buyers?.[0]?.canonical?.canonicalName);

const cab = buyerProfile('Cabinet Office');
check('Cabinet Office resolves canonical',
  !!cab.buyers?.[0]?.canonical?.canonicalId,
  cab.buyers?.[0]?.canonical);

const nonsense = buyerProfile('Zzzzzzz Made Up Buyer 999');
check('Unknown buyer returns empty result',
  !nonsense.buyers?.length,
  nonsense.buyers?.length);

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed ? 1 : 0);
