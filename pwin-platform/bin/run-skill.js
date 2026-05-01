#!/usr/bin/env node
/**
 * PWIN Platform — Skill CLI runner
 *
 * Lets non-Node callers (scheduler.py, cron, manual debug) execute a skill
 * and read its result as JSON on stdout. Skill writes (file, MCP, DB) are
 * still handled by the skill-runner — the CLI just exposes the entry point.
 *
 * Usage:
 *   node bin/run-skill.js <skillId> [--key value ...]
 *   node bin/run-skill.js daily-pipeline-scan --lookbackHours 24
 *   node bin/run-skill.js --dry-run daily-pipeline-scan
 *
 * Exit codes:
 *   0  skill ran (look at stdout JSON for skill-level outcome)
 *   1  skill threw or skill not found
 *   2  bad arguments
 */

import { executeSkill, gatherContext, loadSkill, assemblePrompt } from '../src/skill-runner.js';

const args = process.argv.slice(2);
let dryRun = false;

const positional = [];
const input = {};
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--dry-run') {
    dryRun = true;
    continue;
  }
  if (a.startsWith('--')) {
    const key = a.slice(2);
    const next = args[i + 1];
    if (next === undefined || next.startsWith('--')) {
      input[key] = true;
    } else {
      // Coerce numerics and booleans for convenience
      if (/^-?\d+$/.test(next)) input[key] = parseInt(next, 10);
      else if (/^-?\d*\.\d+$/.test(next)) input[key] = parseFloat(next);
      else if (next === 'true') input[key] = true;
      else if (next === 'false') input[key] = false;
      else input[key] = next;
      i++;
    }
  } else {
    positional.push(a);
  }
}

const [skillId] = positional;
if (!skillId) {
  console.error('Usage: run-skill.js <skillId> [--key value ...] [--dry-run]');
  process.exit(2);
}

try {
  if (dryRun) {
    // Don't call Claude — just return the assembled prompt + context keys.
    // Useful for verifying context wiring without burning API spend.
    const skill = await loadSkill(skillId);
    const context = await gatherContext(skill, input);
    const { systemPrompt, userMessage } = assemblePrompt(skill, context, input);
    console.log(JSON.stringify({
      dryRun: true,
      skillId,
      input,
      contextKeys: Object.keys(context),
      contextSummary: summariseContext(context),
      systemPromptLength: systemPrompt.length,
      userMessageLength: userMessage.length,
      userMessagePreview: userMessage.slice(0, 1500),
    }, null, 2));
    process.exit(0);
  }

  const result = await executeSkill(skillId, input);
  // Use process.stdout.write + explicit exit to avoid a Windows-only libuv
  // cleanup assertion that fires on shutdown when node:sqlite handles are in
  // play. Exit synchronously so the runtime never reaches that cleanup path.
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  process.stdout.once('drain', () => process.exit(0));
  // If drain fired already, force exit on next tick
  setImmediate(() => process.exit(0));
} catch (err) {
  console.error(`run-skill: ${err.message}`);
  if (process.env.PWIN_DEBUG) console.error(err.stack);
  process.exit(1);
}

function summariseContext(context) {
  const summary = {};
  for (const [k, v] of Object.entries(context)) {
    if (v == null) summary[k] = null;
    else if (Array.isArray(v)) summary[k] = `array(${v.length})`;
    else if (typeof v === 'object') {
      // For known intel objects, surface counts
      if (typeof v.count === 'number') summary[k] = `object{count:${v.count}}`;
      else if (typeof v.noticeCount === 'number') summary[k] = `object{noticeCount:${v.noticeCount}, planningCount:${v.planningCount || 0}}`;
      else summary[k] = `object{keys:${Object.keys(v).length}}`;
    }
    else if (typeof v === 'string') summary[k] = `string(${v.length})`;
    else summary[k] = typeof v;
  }
  return summary;
}
