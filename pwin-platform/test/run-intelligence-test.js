/**
 * Standalone intelligence skill test runner.
 * No server required — calls executeSkill directly.
 *
 * Usage:
 *   ANTHROPIC_API_KEY=sk-ant-... node test/run-intelligence-test.js
 *
 * Options (env vars):
 *   SKILL       buyer-intelligence | sector-intelligence | supplier-intelligence (default: buyer-intelligence)
 *   BUYER       buyer name  (default: Department for Work and Pensions)
 *   SECTOR      sector name (default: not set)
 *   SUPPLIER    supplier name (default: not set)
 *   DEPTH       snapshot | standard | deep (default: snapshot)
 *   MODEL       override model ID (e.g. claude-haiku-4-5-20251001 for rate-limited keys)
 */

import { writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { executeSkill } from '../src/skill-runner.js';

const SKILL    = process.env.SKILL    || 'buyer-intelligence';
const BUYER    = process.env.BUYER    || 'Department for Work and Pensions';
const SECTOR   = process.env.SECTOR   || null;
const SUPPLIER = process.env.SUPPLIER || null;
const DEPTH    = process.env.DEPTH    || 'snapshot';
const MODEL    = process.env.MODEL    || null;

if (!process.env.ANTHROPIC_API_KEY) {
  console.error('ANTHROPIC_API_KEY is not set.');
  console.error('Run as: ANTHROPIC_API_KEY=sk-ant-... node test/run-intelligence-test.js');
  process.exit(1);
}

function buildInput() {
  const base = { depthMode: DEPTH, ...(MODEL ? { _model: MODEL } : {}) };
  if (SKILL === 'buyer-intelligence')    return { ...base, buyerName: BUYER };
  if (SKILL === 'sector-intelligence')   return { ...base, sectorName: SECTOR || 'Central Government' };
  if (SKILL === 'supplier-intelligence') return { ...base, supplierName: SUPPLIER || 'Serco' };
  return base;
}

const input = buildInput();

console.log(`\n${'═'.repeat(60)}`);
console.log(`  Skill:  ${SKILL}`);
console.log(`  Input:  ${JSON.stringify(input)}`);
console.log(`  Depth:  ${DEPTH}`);
console.log(`${'═'.repeat(60)}\n`);

const start = Date.now();

try {
  const result = await executeSkill(SKILL, input);

  const elapsed = ((Date.now() - start) / 1000).toFixed(1);

  if (result.dryRun) {
    console.log('DRY RUN — no API key used. Assembled prompt:\n');
    console.log('SYSTEM:\n', result.systemPrompt.slice(0, 500), '...\n');
    console.log('USER:\n', result.userMessage.slice(0, 500), '...\n');
    process.exit(0);
  }

  const { usage, writeResults, text } = result;

  console.log(`Completed in ${elapsed}s`);
  console.log(`Tokens: ${usage?.input_tokens ?? '?'} in / ${usage?.output_tokens ?? '?'} out`);

  if (writeResults?.length) {
    for (const w of writeResults) {
      console.log(`Write: ${w.tool} — ${w.success ? `OK (${JSON.stringify(w.result)})` : `FAILED: ${w.error}`}`);
    }
  }

  // Save raw result to file for inspection
  const outDir = join(import.meta.dirname, 'skill-tests', 'results');
  await mkdir(outDir, { recursive: true });
  const slug = input.buyerName || input.sectorName || input.supplierName || 'output';
  const filename = `${SKILL}-${slug.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${Date.now()}.json`;
  const outPath = join(outDir, filename);
  await writeFile(outPath, JSON.stringify(result, null, 2), 'utf-8');
  console.log(`\nFull result saved to: test/skill-tests/results/${filename}`);

  // Print text output if any (usually empty — skill writes via tool call)
  if (text?.trim()) {
    console.log('\n--- Claude text output ---\n');
    console.log(text.slice(0, 2000));
    if (text.length > 2000) console.log(`... (${text.length - 2000} more chars in saved file)`);
  }

} catch (err) {
  console.error(`\nFailed after ${((Date.now() - start) / 1000).toFixed(1)}s:`, err.message);
  process.exit(1);
}
