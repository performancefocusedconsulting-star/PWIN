#!/usr/bin/env node
/**
 * eval-harness.js — regression tester for Qualify content versions.
 *
 * For each fixture in pwin-qualify/content/eval-fixtures/, this script:
 *   1. Loads QUALIFY_CONTENT (current version)
 *   2. Hydrates the same persona + question that the app would
 *   3. Builds the same per-question system prompt the app builds
 *   4. Calls Claude with the fixture's evidence
 *   5. Diffs the AI response against the fixture's expected verdict and
 *      inflation flag, and reports passes/fails
 *
 * Usage:
 *   ANTHROPIC_API_KEY=sk-... node pwin-qualify/content/eval-harness.js
 *   ANTHROPIC_API_KEY=sk-... node pwin-qualify/content/eval-harness.js --version 0.1.0
 *   node pwin-qualify/content/eval-harness.js --dry-run        # build prompts only, no API calls
 *   node pwin-qualify/content/eval-harness.js --fixture R4_challenged
 *
 * The fixture format is documented in eval-fixtures/README.md.
 *
 * Cost: roughly $0.01-0.02 per fixture with Sonnet 4.6 at typical token sizes.
 * A full run of 10-15 fixtures should cost under $0.30.
 */

const fs = require('fs');
const path = require('path');

const CONTENT_DIR = __dirname;
const FIXTURES_DIR = path.join(CONTENT_DIR, 'eval-fixtures');
const MODEL = process.env.QUALIFY_EVAL_MODEL || 'claude-sonnet-4-5-20250929';

// ─── CLI ───
const args = process.argv.slice(2);
let versionArg = null;
let fixtureArg = null;
let dryRun = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--version') versionArg = args[++i];
  else if (args[i] === '--fixture') fixtureArg = args[++i];
  else if (args[i] === '--dry-run') dryRun = true;
  else if (args[i] === '--help' || args[i] === '-h') {
    console.log(fs.readFileSync(__filename, 'utf8').split('*/')[0]);
    process.exit(0);
  }
}

// ─── Load content ───
function findLatestContent() {
  const files = fs.readdirSync(CONTENT_DIR).filter(f => /^qualify-content-v[\d.]+\.json$/.test(f)).sort();
  if (!files.length) throw new Error('No content file found in ' + CONTENT_DIR);
  return path.join(CONTENT_DIR, files[files.length - 1]);
}
const contentFile = versionArg
  ? path.join(CONTENT_DIR, `qualify-content-v${versionArg}.json`)
  : findLatestContent();
const QUALIFY_CONTENT = JSON.parse(fs.readFileSync(contentFile, 'utf8'));
console.log(`Content version: ${QUALIFY_CONTENT.version} (${path.relative(process.cwd(), contentFile)})`);

// ─── Load fixtures ───
if (!fs.existsSync(FIXTURES_DIR)) {
  console.error(`No fixtures directory at ${FIXTURES_DIR}. Create it and add eval-fixture-*.json files.`);
  process.exit(1);
}
const fixtureFiles = fs.readdirSync(FIXTURES_DIR)
  .filter(f => /\.json$/.test(f))
  .filter(f => !fixtureArg || f.includes(fixtureArg))
  .sort();
if (!fixtureFiles.length) {
  console.error(`No fixtures match ${fixtureArg || '*'}`);
  process.exit(1);
}
console.log(`Fixtures: ${fixtureFiles.length}\n`);

// ─── Build runtime data structures the same way the app does ───
function buildRuntimeContent(context) {
  const cats = QUALIFY_CONTENT.categories.map(c => ({ ...c }));
  const questions = QUALIFY_CONTENT.questionPacks.standard.questions.map(q => ({
    id: q.id, cat: q.cat, topic: q.topic, text: q.text,
    rubric: q.rubric, signals: q.inflationSignals, qw: q.qw,
  }));
  const persona = JSON.parse(JSON.stringify(QUALIFY_CONTENT.persona));

  // Apply incumbent modifier if context says so
  const mods = QUALIFY_CONTENT.modifiers || {};
  for (const modId of Object.keys(mods)) {
    const mod = mods[modId];
    if (!triggerMatches(mod.trigger, context)) continue;
    if (mod.addsCategory) {
      const ac = mod.addsCategory;
      if (ac.rebalanceOthers === 'proportional') {
        const remaining = 1 - ac.weightOnActivation;
        const total = cats.reduce((s, c) => s + c.weight, 0);
        cats.forEach(c => { c.weight = (c.weight / total) * remaining; });
      }
      cats.push({ id: ac.id, name: ac.name, weight: ac.weightOnActivation });
    }
    (mod.addsQuestions || []).forEach(q => {
      questions.push({
        id: q.id, cat: q.cat, topic: q.topic, text: q.text,
        rubric: q.rubric, signals: [], qw: q.qw,
      });
    });
    if (mod.addsPersonaTriggers) {
      const wt = persona.workflowTriggers;
      const apt = mod.addsPersonaTriggers;
      (apt.inflationTriggers || []).forEach(r => wt.inflationTriggers.push(`[${r.ref}] ${r.condition} → ${r.response}`));
      (apt.calibrationRules || []).forEach(r => wt.calibrationRules.push(`[${r.ref}] ${r.condition} → ${r.response}`));
      (apt.autoVerdictRules || []).forEach(r => wt.autoChallenge.push(`[${r.ref}] ${r.condition} → ${r.response}`));
    }
  }
  return { cats, questions, persona };
}

function triggerMatches(trigger, ctx) {
  if (!trigger) return false;
  const path = (trigger.field || '').split('.');
  let val = { context: ctx };
  for (const seg of path) val = val ? val[seg] : undefined;
  if (val == null || val === '') return false;
  if (typeof val !== 'string') return false;
  const valLower = val.toLowerCase().trim();
  return (trigger.matches || []).some(m =>
    typeof m === 'string' && m.toLowerCase().trim() === valLower
  );
}

// ─── Build the per-question system prompt the same way the app does ───
function buildSystemPrompt(persona, context, outputSchema) {
  const p = persona;
  let prompt = '';
  prompt += p.identity.roleStatement + '\n\n';
  prompt += p.background.narrative + '\n\n';
  prompt += 'WHAT YOU HOLD TO BE TRUE:\n';
  p.coreBeliefs.forEach(b => prompt += `— ${b}\n`);
  prompt += '\nHOW YOU THINK:\n';
  p.characterTraits.forEach(t => prompt += `— ${t}\n`);
  prompt += '\nTONE:\n';
  p.toneGuidance.forEach(t => prompt += `— ${t}\n`);
  prompt += '\nLANGUAGE — USE: ' + p.languagePatterns.use.join(' | ');
  prompt += '\nLANGUAGE — NEVER: ' + p.languagePatterns.avoid.join(' | ') + '\n\n';
  prompt += 'YOU WILL: ' + p.hardRules.will.join(' | ') + '\n';
  prompt += 'YOU WILL NOT: ' + p.hardRules.willNot.join(' | ') + '\n\n';
  const t = p.workflowTriggers;
  prompt += 'AUTOMATIC VERDICT TRIGGERS:\n';
  [...t.autoChallenge, ...t.autoQuery].forEach(r => prompt += `— ${r}\n`);
  prompt += '\nCALIBRATION RULES:\n';
  t.calibrationRules.forEach(r => prompt += `— ${r}\n`);
  prompt += '\nINFLATION TRIGGERS:\n';
  t.inflationTriggers.forEach(r => prompt += `— ${r}\n`);
  prompt += '\n';
  if (context.sector) prompt += `SECTOR CONTEXT: This is a ${context.sector} sector opportunity.\n\n`;
  if (context.oppType) {
    const oppBlock = QUALIFY_CONTENT.opportunityTypeCalibration[context.oppType];
    if (oppBlock) prompt += `OPPORTUNITY TYPE CONTEXT:\n${oppBlock}\n\n`;
  }
  prompt += outputSchema + '\n\n';
  const sc = p.successCriteria;
  prompt += 'BEFORE RETURNING YOUR RESPONSE, CHECK:\n';
  [...sc.verdictQuality, ...sc.challengeQuality, ...sc.actionQuality, ...sc.finalCheck]
    .forEach(c => prompt += `□ ${c}\n`);
  return prompt;
}

const PER_Q_SCHEMA = `Respond ONLY with a valid JSON object — no markdown, no preamble:
{
  "verdict": "Validated | Queried | Challenged",
  "suggestedScore": "Strongly Agree | Agree | Disagree | Strongly Disagree",
  "narrative": "2-3 sentences",
  "challengeQuestions": ["q1", "q2"],
  "captureActions": ["action 1", "action 2"],
  "inflationDetected": true | false,
  "inflationPhrase": "the verbatim phrase if detected, else null"
}`;

// ─── Call the API (uses native fetch) ───
async function callClaude(systemPrompt, userPrompt) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY not set');
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 1500,
      system: systemPrompt,
      messages: [{ role: 'user', content: userPrompt }],
    }),
  });
  if (!r.ok) {
    const body = await r.text();
    throw new Error(`API ${r.status}: ${body.slice(0, 500)}`);
  }
  return await r.json();
}

// ─── Run a single fixture ───
async function runFixture(fixtureFile) {
  const fixture = JSON.parse(fs.readFileSync(path.join(FIXTURES_DIR, fixtureFile), 'utf8'));
  const { id, description, context, questionId, evidence, expected } = fixture;

  const { questions, persona } = buildRuntimeContent(context);
  const q = questions.find(qq => qq.id === questionId);
  if (!q) throw new Error(`Question ${questionId} not found in active question set`);

  const systemPrompt = buildSystemPrompt(persona, context, PER_Q_SCHEMA);
  const userPrompt = `PURSUIT CONTEXT:
Organisation: ${context.org}
Sector: ${context.sector || ''}
Opportunity Type: ${context.oppType || ''}
Total Contract Value: ${context.tcv || ''}
Pursuit Stage: ${context.stage || ''}
Incumbent Position: ${context.incumbent || ''}
${context.notes ? 'Notes: ' + context.notes : ''}

QUESTION (${q.cat.toUpperCase()} / ${q.topic}):
${q.text}

RUBRIC:
${Object.entries(q.rubric).map(([k, v]) => `${k}: ${v}`).join('\n')}

CLAIMED SCORE: ${fixture.claimedScore}

EVIDENCE PROVIDED BY THE TEAM:
${evidence}

Review this evidence against the question and rubric. Apply your inflation triggers and calibration rules.`;

  if (dryRun) {
    return {
      id, ok: null, dryRun: true,
      systemPromptLen: systemPrompt.length,
      userPromptLen: userPrompt.length,
    };
  }

  let response, parsed, error;
  try {
    response = await callClaude(systemPrompt, userPrompt);
    const text = response.content.map(b => b.text || '').join('').replace(/```json|```/g, '').trim();
    parsed = JSON.parse(text);
  } catch (e) {
    error = e.message;
  }

  if (error) return { id, ok: false, error };

  // Diff against expected
  const checks = [];
  if (expected.verdict) {
    checks.push({
      check: `verdict === "${expected.verdict}"`,
      ok: parsed.verdict === expected.verdict,
      actual: parsed.verdict,
    });
  }
  if (expected.inflationDetected != null) {
    checks.push({
      check: `inflationDetected === ${expected.inflationDetected}`,
      ok: parsed.inflationDetected === expected.inflationDetected,
      actual: parsed.inflationDetected,
    });
  }
  if (expected.suggestedScore) {
    checks.push({
      check: `suggestedScore === "${expected.suggestedScore}"`,
      ok: parsed.suggestedScore === expected.suggestedScore,
      actual: parsed.suggestedScore,
    });
  }

  const usage = response.usage || {};
  const cost = (usage.input_tokens || 0) * 3e-6 + (usage.output_tokens || 0) * 15e-6;
  return {
    id, description, ok: checks.every(c => c.ok),
    checks, parsed, usage, cost,
  };
}

// ─── Main ───
(async () => {
  const results = [];
  let totalCost = 0;
  for (const file of fixtureFiles) {
    process.stdout.write(`  ${file} ... `);
    try {
      const r = await runFixture(file);
      results.push(r);
      if (r.dryRun) {
        console.log(`dry-run (sys=${r.systemPromptLen}b, user=${r.userPromptLen}b)`);
      } else if (r.error) {
        console.log(`ERROR: ${r.error}`);
      } else {
        const tag = r.ok ? 'PASS' : 'FAIL';
        const cost = r.cost ? ` [$${r.cost.toFixed(4)}]` : '';
        console.log(`${tag}${cost}`);
        if (!r.ok) {
          r.checks.filter(c => !c.ok).forEach(c => {
            console.log(`        FAIL: ${c.check} (got: ${JSON.stringify(c.actual)})`);
          });
          if (r.parsed && r.parsed.narrative) {
            console.log(`        narrative: ${r.parsed.narrative.slice(0, 150)}...`);
          }
        }
        totalCost += r.cost || 0;
      }
    } catch (e) {
      console.log(`THREW: ${e.message}`);
      results.push({ id: file, ok: false, error: e.message });
    }
  }

  if (dryRun) {
    console.log('\nDry run complete.');
    return;
  }

  const pass = results.filter(r => r.ok === true).length;
  const fail = results.filter(r => r.ok === false).length;
  console.log(`\n${pass} passed, ${fail} failed`);
  console.log(`Total API cost: $${totalCost.toFixed(4)}`);
  process.exit(fail === 0 ? 0 : 1);
})();
