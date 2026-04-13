#!/usr/bin/env node
/**
 * Run a skill locally in Claude Code instead of through the skill runner API.
 *
 * Assembles the system prompt + user prompt from the skill YAML,
 * injects FTS data and other inputs, and writes the combined prompt
 * to stdout or a file for pasting into Claude Code.
 *
 * Usage:
 *   node scripts/run-skill-local.js <skill-id> [options]
 *
 * Options:
 *   --supplier <name>       Supplier name (for supplier-dossier)
 *   --buyer <name>          Buyer name (for buyer-intelligence)
 *   --depth <mode>          snapshot | standard | deep (default: standard)
 *   --sectors <list>        Comma-separated sector list
 *   --fts-supplier <name>   Pull FTS data for this supplier from the intel DB
 *   --fts-buyer <name>      Pull FTS data for this buyer from the intel DB
 *   --out <file>            Write prompt to file instead of stdout
 *   --prompt-only           Only output the user prompt (system prompt goes to a separate file)
 *
 * Examples:
 *   node scripts/run-skill-local.js supplier-dossier --supplier "Serco Group plc" --depth deep --fts-supplier "SERCO"
 *   node scripts/run-skill-local.js buyer-intelligence --buyer "Ministry of Defence" --depth standard --fts-buyer "Ministry of Defence"
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

// ─── Parse args ─────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
if (args.length === 0 || args.includes('--help')) {
  console.log(`Usage: node scripts/run-skill-local.js <skill-id> [options]

Skills:
  supplier-dossier      Supplier Intelligence Dossier v2
  buyer-intelligence    Buyer Intelligence Dossier v2

Options:
  --supplier <name>     Supplier name
  --buyer <name>        Buyer name
  --depth <mode>        snapshot | standard | deep (default: standard)
  --sectors <list>      Comma-separated sectors
  --fts-supplier <name> Pull FTS supplier data from intel DB
  --fts-buyer <name>    Pull FTS buyer data from intel DB
  --out <path>          Write to file instead of stdout`);
  process.exit(0);
}

const skillId = args[0];
function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : null;
}

const supplierName = getArg('--supplier');
const buyerName = getArg('--buyer');
const depthMode = getArg('--depth') || 'standard';
const sectors = getArg('--sectors') || '';
const ftsSupplier = getArg('--fts-supplier');
const ftsBuyer = getArg('--fts-buyer');
const outFile = getArg('--out');

// ─── Load skill YAML ────────────────────────────────────────────────────────

import { parse } from '../src/yaml-lite.js';

function findSkillFile(id) {
  const dirs = ['agent1-document-intelligence', 'agent2-market-competitive', 'agent3-strategy-scoring',
    'agent4-commercial-financial', 'agent5-content-drafting', 'agent6-solution-delivery'];
  for (const dir of dirs) {
    const path = join(ROOT, 'skills', dir, `${id}.yaml`);
    if (existsSync(path)) return path;
  }
  throw new Error(`Skill not found: ${id}`);
}

const skillPath = findSkillFile(skillId);
const skill = parse(readFileSync(skillPath, 'utf-8'));
console.error(`Loaded skill: ${skill.name} (${skill.id})`);

// ─── Pull FTS data ──────────────────────────────────────────────────────────

const DB_PATH = join(ROOT, '..', 'pwin-competitive-intel', 'db', 'bid_intel.db');
let ftsData = '';
let chData = '';

if ((ftsSupplier || ftsBuyer) && existsSync(DB_PATH)) {
  console.error(`Pulling FTS data from ${DB_PATH}...`);

  if (ftsSupplier) {
    try {
      const script = `
import sqlite3, json, sys
db = sqlite3.connect("${DB_PATH}")
db.row_factory = sqlite3.Row
rows = db.execute("""
  SELECT n.ocid, n.title, b.name as buyer_name, n.main_category,
         n.procurement_method, n.service_category, n.is_framework,
         a.value_amount, a.currency, a.award_date,
         a.contract_start_date, a.contract_end_date, a.contract_max_extend,
         a.contract_status, s.name as supplier_name
  FROM awards a
  JOIN award_suppliers asup ON asup.award_id = a.id
  JOIN suppliers s ON s.id = asup.supplier_id
  JOIN notices n ON n.ocid = a.ocid
  LEFT JOIN suppliers b ON b.id = n.buyer_id
  WHERE UPPER(s.name) LIKE ?
  ORDER BY a.value_amount DESC NULLS LAST
  LIMIT 50
""", ("%${ftsSupplier.toUpperCase()}%",)).fetchall()
data = [dict(r) for r in rows]
json.dump(data, sys.stdout, indent=2, default=str)
`;
      ftsData = execSync(`python3 -c '${script.replace(/'/g, "'\\''")}'`, { encoding: 'utf-8', timeout: 30000 });
      console.error(`  FTS supplier data: ${JSON.parse(ftsData).length} awards`);
    } catch (e) {
      console.error(`  FTS supplier data pull failed: ${e.message}`);
    }

    // Companies House
    try {
      const chScript = `
import sqlite3, json, sys
db = sqlite3.connect("${DB_PATH}")
db.row_factory = sqlite3.Row
row = db.execute("""
  SELECT name, companies_house_no, ch_sic_codes, ch_parent, ch_directors,
         ch_status, ch_incorporated, ch_turnover, ch_employees, ch_address
  FROM suppliers
  WHERE UPPER(name) LIKE ? AND companies_house_no IS NOT NULL
  LIMIT 1
""", ("%${ftsSupplier.toUpperCase()}%",)).fetchone()
if row: json.dump(dict(row), sys.stdout, indent=2, default=str)
else: print("{}")
`;
      chData = execSync(`python3 -c '${chScript.replace(/'/g, "'\\''")}'`, { encoding: 'utf-8', timeout: 10000 });
      console.error(`  Companies House data: ${chData.trim() !== '{}' ? 'found' : 'not found'}`);
    } catch (e) {
      console.error(`  CH data pull failed: ${e.message}`);
    }
  }

  if (ftsBuyer) {
    try {
      const script = `
import sqlite3, json, sys
db = sqlite3.connect("${DB_PATH}")
db.row_factory = sqlite3.Row
rows = db.execute("""
  SELECT n.ocid, n.title, n.main_category, n.procurement_method,
         n.service_category, n.is_framework,
         a.value_amount, a.currency, a.award_date,
         a.contract_start_date, a.contract_end_date, a.contract_max_extend,
         a.contract_status,
         GROUP_CONCAT(DISTINCT s2.name) as supplier_names
  FROM notices n
  JOIN suppliers b ON b.id = n.buyer_id
  JOIN awards a ON a.ocid = n.ocid
  LEFT JOIN award_suppliers asup ON asup.award_id = a.id
  LEFT JOIN suppliers s2 ON s2.id = asup.supplier_id
  WHERE b.name LIKE ?
  GROUP BY a.id
  ORDER BY a.value_amount DESC NULLS LAST
  LIMIT 60
""", ("%${ftsBuyer}%",)).fetchall()
data = [dict(r) for r in rows]
json.dump(data, sys.stdout, indent=2, default=str)
`;
      ftsData = execSync(`python3 -c '${script.replace(/'/g, "'\\''")}'`, { encoding: 'utf-8', timeout: 30000 });
      console.error(`  FTS buyer data: ${JSON.parse(ftsData).length} awards`);
    } catch (e) {
      console.error(`  FTS buyer data pull failed: ${e.message}`);
    }
  }
} else if (ftsSupplier || ftsBuyer) {
  console.error(`Warning: Intel DB not found at ${DB_PATH} — no FTS data will be injected`);
}

// ─── Assemble prompt ────────────────────────────────────────────────────────

let systemPrompt = skill.system_prompt || '';
let userPrompt = skill.user_prompt || '';

// Replace template variables
const replacements = {
  supplierName: supplierName || buyerName || '',
  buyerName: buyerName || supplierName || '',
  depthMode: depthMode,
  sectors: sectors,
  sector: sectors,
  ftsSupplierData: ftsData || 'No FTS data available.',
  ftsBuyerData: ftsData || 'No FTS data available.',
  companiesHouseData: chData || 'No Companies House data available.',
  existingDossier: 'No existing dossier.',
  existingProfile: 'No existing profile.',
  // Context placeholders — these would normally come from platform knowledge
  sector_knowledge: '[Sector knowledge will be available from your own knowledge base]',
  source_hierarchy: '[Source hierarchy is defined in the system prompt above]',
  confidence_model: '[Confidence model is defined in the system prompt above]',
};

for (const [key, value] of Object.entries(replacements)) {
  systemPrompt = systemPrompt.replace(new RegExp(`\\{\\{${key}\\}\\}`, 'g'), value);
  userPrompt = userPrompt.replace(new RegExp(`\\{\\{${key}\\}\\}`, 'g'), value);
}

// ─── Output ─────────────────────────────────────────────────────────────────

const storageNote = skillId === 'supplier-dossier'
  ? `\n\nWhen you have produced the JSON, save it to: ~/.pwin/reference/suppliers/${(supplierName || 'unknown').toLowerCase().replace(/[^a-z0-9]+/g, '-')}/data.json\nThen run the renderer: node pwin-architect-plugin/agents/market-intelligence/render-dossier.js ~/.pwin/reference/suppliers/${(supplierName || 'unknown').toLowerCase().replace(/[^a-z0-9]+/g, '-')}/data.json`
  : `\n\nWhen you have produced the JSON, save it to: ~/.pwin/reference/clients/${(buyerName || 'unknown').toLowerCase().replace(/[^a-z0-9]+/g, '-')}/data.json\nThen run the renderer: node pwin-architect-plugin/agents/market-intelligence/render-client-profile.js ~/.pwin/reference/clients/${(buyerName || 'unknown').toLowerCase().replace(/[^a-z0-9]+/g, '-')}/data.json`;

const systemFile = outFile ? outFile.replace('.md', '-system.md') : null;
const userFile = outFile || null;

if (outFile) {
  writeFileSync(systemFile, `# System Prompt\n\n${systemPrompt}`, 'utf-8');
  writeFileSync(userFile, `# User Prompt\n\n${userPrompt}\n\n---\n\n# Storage\n${storageNote}`, 'utf-8');
  console.error(`\nWritten:`);
  console.error(`  System prompt: ${systemFile} (${systemPrompt.length} chars)`);
  console.error(`  User prompt:   ${userFile} (${userPrompt.length} chars)`);
} else {
  // Write system prompt to a temp file, output user prompt to stdout
  const tmpSystem = '/tmp/skill-system-prompt.md';
  writeFileSync(tmpSystem, systemPrompt, 'utf-8');
  console.error(`\nSystem prompt written to: ${tmpSystem} (${systemPrompt.length} chars)`);
  console.error(`User prompt below (${userPrompt.length} chars):`);
  console.error(`Storage:${storageNote}`);
  console.error(`\n${'─'.repeat(70)}\n`);
  console.log(userPrompt);
}
