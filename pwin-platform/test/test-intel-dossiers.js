/**
 * PWIN Platform — intel-dossiers loader tests
 *
 * Run: node test/test-intel-dossiers.js
 */
import { getDossier, slugify, dossierPath } from '../src/intel-dossiers.js';
import { writeFile, mkdir, rm, utimes } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

let passed = 0, failed = 0;
function check(label, condition, detail) {
  if (condition) { passed++; console.log(`  PASS ${label}`); }
  else           { failed++; console.error(`  FAIL ${label}`, detail !== undefined ? `(got: ${JSON.stringify(detail)})` : ''); }
}

const FIXTURE_ROOT = join(homedir(), '.pwin', 'intel');
const TEST_BUYER_FILE = join(FIXTURE_ROOT, 'buyers', 'test-buyer-loader-fixture-dossier.json');
const TEST_BUYER_FILE_V2 = join(FIXTURE_ROOT, 'buyers', 'test-buyer-loader-fixture-dossier-v2.json');

async function setup() {
  await mkdir(join(FIXTURE_ROOT, 'buyers'), { recursive: true });
  await writeFile(TEST_BUYER_FILE, JSON.stringify({ meta: { version: '1.0' } }));
}

async function teardown() {
  await rm(TEST_BUYER_FILE, { force: true });
  await rm(TEST_BUYER_FILE_V2, { force: true });
}

console.log('\n=== intel-dossiers loader ===\n');

// slugify
check('slugify lowercases and kebabs', slugify('Home Office') === 'home-office');
check('slugify strips punctuation', slugify('M&S Defence!') === 'm-s-defence');
check('slugify trims leading/trailing dashes', slugify('  -Foo Bar-  ') === 'foo-bar');

// dossierPath
check('dossierPath builds the expected path',
  dossierPath('buyers', 'home-office').endsWith(join('intel', 'buyers', 'home-office-dossier.json')));
check('dossierPath uses "brief" for sectors',
  dossierPath('sectors', 'defence').endsWith('defence-brief.json'));
check('dossierPath uses "analysis" for incumbency',
  dossierPath('incumbency', 'serco-mod').endsWith('serco-mod-analysis.json'));

// getDossier — happy path
await setup();
const dossier = await getDossier('buyers', 'test-buyer-loader-fixture');
check('getDossier returns parsed JSON', dossier?.meta?.version === '1.0', dossier);

// getDossier — missing file
const missing = await getDossier('buyers', 'this-buyer-does-not-exist-123456');
check('getDossier returns null for missing file', missing === null);

// getDossier — versioned file: prefer the most recently modified
await writeFile(TEST_BUYER_FILE_V2, JSON.stringify({ meta: { version: '2.0' } }));
// touch v2 to be newer
const future = new Date(Date.now() + 1000);
await utimes(TEST_BUYER_FILE_V2, future, future);
const versioned = await getDossier('buyers', 'test-buyer-loader-fixture');
check('getDossier prefers latest mtime when multiple versions exist',
  versioned?.meta?.version === '2.0', versioned?.meta?.version);

// getDossier — unknown type errors clearly
try {
  await getDossier('made-up-type', 'whatever');
  check('getDossier rejects unknown type', false, 'expected throw');
} catch (err) {
  check('getDossier rejects unknown type', /unknown type/i.test(err.message), err.message);
}

await teardown();

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed ? 1 : 0);
