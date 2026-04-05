#!/usr/bin/env node
/**
 * Extract L2/L3 methodology data from the gold standard markdown
 * and produce the compact WS array for bid-execution.html
 *
 * Usage: node scripts/extract-methodology.js > ws-data.js
 */

const fs = require('fs');
const path = require('path');

const goldStandardPath = path.join(__dirname, '..', 'docs', 'methodology_gold_standard.md');
const md = fs.readFileSync(goldStandardPath, 'utf-8');

// Extract all JavaScript code blocks from the markdown
const codeBlockRegex = /```javascript\n([\s\S]*?)```/g;
const blocks = [];
let match;
while ((match = codeBlockRegex.exec(md)) !== null) {
  blocks.push(match[1].trim());
}

console.error(`Found ${blocks.length} code blocks`);

// Parse each code block as a JS object (they're JS object literals, not JSON)
// We use a function wrapper to eval them safely
const activities = [];
for (const block of blocks) {
  try {
    // Normalise smart quotes and wrap in parentheses to make it an expression
    const cleaned = block.replace(/[\u2018\u2019]/g, "'").replace(/[\u201C\u201D]/g, '"').replace(/\u2014/g, '--');
    const fn = new Function(`return (${cleaned});`);
    const obj = fn();
    if (obj && obj.id && obj.subs) {
      activities.push(obj);
    }
  } catch (e) {
    // Some blocks might be examples or non-activity data — skip
    const idMatch = block.match(/id:\s*'([^']+)'/);
    if (idMatch) {
      console.error(`  Warning: Could not parse block for ${idMatch[1]}: ${e.message}`);
    }
  }
}

console.error(`Parsed ${activities.length} activities with L2/L3 data`);

// Group activities by workstream
const wsOrder = ['SAL', 'SOL', 'COM', 'LEG', 'DEL', 'SUP', 'BM', 'PRD', 'GOV', 'POST'];
const wsNames = {
  SAL: { name: 'Sales & Capture', cls: 'sales', ph: 'DEV' },
  SOL: { name: 'Solution Design', cls: 'solution', ph: 'DEV' },
  COM: { name: 'Commercial & Pricing', cls: 'commercial', ph: 'DEV' },
  LEG: { name: 'Legal & Contractual', cls: 'legal', ph: 'DEV' },
  DEL: { name: 'Programme & Delivery', cls: 'delivery', ph: 'DEV' },
  SUP: { name: 'Supply Chain & Partners', cls: 'supply', ph: 'DEV' },
  BM:  { name: 'Bid Management & Programme Control', cls: 'bidmgmt', ph: 'CONT' },
  PRD: { name: 'Proposal Production', cls: 'production', ph: 'PRD' },
  GOV: { name: 'Internal Governance', cls: 'governance', ph: 'CONT' },
  POST:{ name: 'Post-Submission', cls: 'postsub', ph: 'POST' },
};

const byWs = {};
for (const a of activities) {
  const ws = a.workstream || a.id.replace(/-\d+$/, '').replace(/(\d+)$/, '');
  if (!byWs[ws]) byWs[ws] = [];
  byWs[ws].push(a);
}

// Format a compact activity for the WS array
function formatActivity(a) {
  const deps = a.dependencies || [];
  const depStr = deps.map(d => `'${d}'`).join(',');

  // Build subs array
  const subsLines = [];
  if (a.subs && a.subs.length > 0) {
    for (const sub of a.subs) {
      const taskLines = [];
      if (sub.tasks && sub.tasks.length > 0) {
        for (const t of sub.tasks) {
          const raci = t.raci || {};
          const raciStr = `{r:'${esc(raci.r||'')}',a:'${esc(raci.a||'')}',c:'${esc(raci.c||'')}',i:'${esc(raci.i||'')}'}`;

          // Compact outputs with quality criteria
          const outputsStr = (t.outputs || []).map(o => {
            const qualStr = (o.quality || []).map(q => `'${esc(q)}'`).join(',');
            return `{n:'${esc(o.name)}',f:'${esc(o.format||'')}',q:[${qualStr}]}`;
          }).join(',');

          taskLines.push(
            `          {id:'${t.id}',n:'${esc(t.name)}',raci:${raciStr},e:'${t.effort||'Medium'}',tp:'${t.type||'Sequential'}',o:[${outputsStr}]}`
          );
        }
      }

      subsLines.push(
        `        {id:'${sub.id}',n:'${esc(sub.name)}',t:[\n${taskLines.join(',\n')}\n        ]}`
      );
    }
  }

  // Activity-level outputs with quality criteria
  const outputsStr = (a.outputs || []).map(o => {
    const qualStr = (o.quality || []).map(q => `'${esc(q)}'`).join(',');
    return `{n:'${esc(o.name)}',f:'${esc(o.format||'')}',q:[${qualStr}]}`;
  }).join(',\n      ');

  const subsBlock = subsLines.length > 0
    ? `\n      subs:[\n${subsLines.join(',\n')}\n      ],`
    : '';

  return `    {id:'${a.id}',n:'${esc(a.name)}',o:'${esc(a.output||'')}',d:[${depStr}],dur:${a.effortDays||0},ts:${a.teamSize||1},pt:'${a.parallelisationType||'S'}',rl:'${esc(a.role||'')}',${subsBlock}
      outs:[${outputsStr}]}`;
}

function esc(s) {
  if (!s) return '';
  return String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, ' ');
}

// Generate the full WS array
const lines = ['const WS = ['];
for (const ws of wsOrder) {
  const info = wsNames[ws];
  const acts = byWs[ws] || [];

  // Sort activities by their numeric suffix
  acts.sort((a, b) => {
    const numA = parseInt(a.id.replace(/[A-Z]+-/, ''));
    const numB = parseInt(b.id.replace(/[A-Z]+-/, ''));
    return numA - numB;
  });

  const actLines = acts.map(a => formatActivity(a));
  lines.push(`  {id:'${ws}',name:'${info.name}',cls:'${info.cls}',ph:'${info.ph}',acts:[`);
  lines.push(actLines.join(',\n'));
  lines.push('  ]},');

  console.error(`  ${ws}: ${acts.length} activities, ${acts.reduce((n, a) => n + (a.subs || []).length, 0)} L2s, ${acts.reduce((n, a) => n + (a.subs || []).reduce((m, s) => m + (s.tasks || []).length, 0), 0)} L3s`);
}
lines.push('];');

// Write to stdout
console.log(lines.join('\n'));

console.error('\nDone. Pipe stdout to a file to capture the WS array.');
