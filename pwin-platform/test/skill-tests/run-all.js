/**
 * Skill Test Runner — Execute All Tests
 *
 * Runs each test in sequence with configurable delays between tests.
 * Reports overall pass/fail and total API cost.
 *
 * Usage:
 *   node test/skill-tests/run-all.js
 *
 * Environment:
 *   ANTHROPIC_API_KEY  — required
 *   RATE_LIMIT_DELAY_MS — delay between API calls (default: 0)
 *   TEST_DELAY_MS — delay between tests (default: 5000)
 */

import { execSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
import { join } from 'node:path';

const TEST_DIR = import.meta.dirname;
const TEST_DELAY = parseInt(process.env.TEST_DELAY_MS || '5000', 10);

async function main() {
  console.log('╔═══════════════════════════════════════════════╗');
  console.log('║  PWIN Platform — Skill Test Suite             ║');
  console.log('╠═══════════════════════════════════════════════╣');
  console.log(`║  Rate limit delay: ${process.env.RATE_LIMIT_DELAY_MS || '0'}ms`);
  console.log(`║  Inter-test delay: ${TEST_DELAY}ms`);
  console.log('╚═══════════════════════════════════════════════╝');

  // Check prerequisites
  try {
    const health = await fetch('http://localhost:3456/api/health');
    if (!health.ok) throw new Error('Server not responding');
  } catch {
    console.error('\n  ERROR: PWIN Platform server not running. Start it first:');
    console.error('  cd pwin-platform && node src/server.js &\n');
    process.exit(1);
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('\n  ERROR: ANTHROPIC_API_KEY not set. Export it first:');
    console.error('  export ANTHROPIC_API_KEY=sk-ant-...\n');
    process.exit(1);
  }

  // Find all test files
  const testFiles = readdirSync(TEST_DIR)
    .filter(f => f.startsWith('test-') && f.endsWith('.js'))
    .sort();

  console.log(`\n  Found ${testFiles.length} tests:\n`);
  testFiles.forEach((f, i) => console.log(`    ${i + 1}. ${f}`));
  console.log('');

  const results = [];
  const startTime = Date.now();

  for (const file of testFiles) {
    console.log(`\n${'═'.repeat(60)}`);
    console.log(`  Running: ${file}`);
    console.log(`${'═'.repeat(60)}`);

    try {
      execSync(`node ${join(TEST_DIR, file)}`, {
        stdio: 'inherit',
        timeout: 600000, // 10 min max per test
        env: { ...process.env },
      });
      results.push({ file, status: 'passed' });
    } catch (err) {
      results.push({ file, status: 'failed', error: err.message });
    }

    // Delay between tests for rate limiting
    if (TEST_DELAY > 0 && file !== testFiles[testFiles.length - 1]) {
      console.log(`\n  Waiting ${TEST_DELAY / 1000}s before next test...`);
      await new Promise(r => setTimeout(r, TEST_DELAY));
    }
  }

  // Final summary
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  const passed = results.filter(r => r.status === 'passed').length;
  const failed = results.filter(r => r.status === 'failed').length;

  console.log('\n╔═══════════════════════════════════════════════╗');
  console.log('║  SKILL TEST SUITE — FINAL RESULTS             ║');
  console.log('╠═══════════════════════════════════════════════╣');
  for (const r of results) {
    const icon = r.status === 'passed' ? '✓' : '✗';
    console.log(`║  ${icon} ${r.file.padEnd(35)} ${r.status.toUpperCase()}`);
  }
  console.log('╠═══════════════════════════════════════════════╣');
  console.log(`║  Total: ${passed} passed, ${failed} failed | ${elapsed}s`);
  console.log('╚═══════════════════════════════════════════════╝');
  console.log(`\n  Review pages generated in: test/skill-tests/results/\n`);

  process.exit(failed > 0 ? 1 : 0);
}

main();
