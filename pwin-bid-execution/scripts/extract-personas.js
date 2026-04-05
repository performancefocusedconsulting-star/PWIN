#!/usr/bin/env node
/**
 * Extract role-based agent personas from L3 RACI data in the gold standard.
 * Produces a markdown document with per-role task lists.
 *
 * Usage: node scripts/extract-personas.js > docs/role_based_personas.md
 */

const fs = require('fs');
const path = require('path');

const goldStandardPath = path.join(__dirname, '..', 'docs', 'methodology_gold_standard.md');
const md = fs.readFileSync(goldStandardPath, 'utf-8');

// Extract all JavaScript code blocks
const codeBlockRegex = /```javascript\n([\s\S]*?)```/g;
const blocks = [];
let match;
while ((match = codeBlockRegex.exec(md)) !== null) {
  blocks.push(match[1].trim());
}

// Parse activities
const activities = [];
for (const block of blocks) {
  try {
    const cleaned = block.replace(/[\u2018\u2019]/g, "'").replace(/[\u201C\u201D]/g, '"').replace(/\u2014/g, '--');
    const fn = new Function(`return (${cleaned});`);
    const obj = fn();
    if (obj && obj.id && obj.subs) activities.push(obj);
  } catch (e) { /* skip non-activity blocks */ }
}

console.error(`Parsed ${activities.length} activities`);

// Collect RACI per role
const roles = {}; // role -> { responsible: [], accountable: [], consulted: [], informed: [] }

function addRole(roleName, type, taskId, taskName, activityId, activityName) {
  if (!roleName || roleName === 'null' || roleName === 'undefined') return;
  // Normalise: some roles have slashes like "SME / Market Intelligence"
  // Split on ' / ' to handle multiple roles
  const roleNames = roleName.includes(' / ') ? roleName.split(' / ').map(r => r.trim()) : [roleName.trim()];
  for (const rn of roleNames) {
    if (!roles[rn]) roles[rn] = { responsible: [], accountable: [], consulted: [], informed: [] };
    roles[rn][type].push({ taskId, taskName, activityId, activityName });
  }
}

for (const act of activities) {
  for (const sub of (act.subs || [])) {
    for (const task of (sub.tasks || sub.t || [])) {
      const raci = task.raci;
      if (!raci) continue;
      const tid = task.id;
      const tn = task.name || task.n;
      addRole(raci.r, 'responsible', tid, tn, act.id, act.name);
      addRole(raci.a, 'accountable', tid, tn, act.id, act.name);
      addRole(raci.c, 'consulted', tid, tn, act.id, act.name);
      addRole(raci.i, 'informed', tid, tn, act.id, act.name);
    }
  }
}

// Sort roles by total responsibility (R+A) descending
const sortedRoles = Object.entries(roles).sort((a, b) => {
  const aTotal = a[1].responsible.length + a[1].accountable.length;
  const bTotal = b[1].responsible.length + b[1].accountable.length;
  return bTotal - aTotal;
});

console.error(`Found ${sortedRoles.length} distinct roles`);

// Generate markdown
const lines = [];
lines.push('# Role-Based Agent Personas');
lines.push('');
lines.push('**Generated:** ' + new Date().toISOString().slice(0, 10));
lines.push('**Source:** methodology_gold_standard.md — 84 activities, 296 L3 tasks');
lines.push('');
lines.push('Each role below shows every L3 task where that role appears in the RACI matrix. This is the foundation for building AI agent personas — each agent knows exactly what the role does, what they own, and what they produce.');
lines.push('');

// Summary table
lines.push('## Summary');
lines.push('');
lines.push('| Role | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) | Total R+A |');
lines.push('|------|----------------|-----------------|---------------|-------------|-----------|');
for (const [role, data] of sortedRoles) {
  lines.push(`| ${role} | ${data.responsible.length} | ${data.accountable.length} | ${data.consulted.length} | ${data.informed.length} | ${data.responsible.length + data.accountable.length} |`);
}
lines.push('');

// Workstream distribution per role
lines.push('## Workstream Distribution');
lines.push('');
lines.push('Shows which workstreams each role operates across (R+A tasks only).');
lines.push('');

for (const [role, data] of sortedRoles) {
  const raTotal = data.responsible.length + data.accountable.length;
  if (raTotal === 0) continue;

  const raTasks = [...data.responsible, ...data.accountable];
  const wsCount = {};
  for (const t of raTasks) {
    const ws = t.activityId.replace(/-\d+$/, '');
    wsCount[ws] = (wsCount[ws] || 0) + 1;
  }
  const wsStr = Object.entries(wsCount).sort((a, b) => b[1] - a[1]).map(([ws, n]) => `${ws}(${n})`).join(', ');
  lines.push(`- **${role}** [${raTotal}]: ${wsStr}`);
}
lines.push('');

// Detailed per-role sections
lines.push('---');
lines.push('');

for (const [role, data] of sortedRoles) {
  const raTotal = data.responsible.length + data.accountable.length;
  if (raTotal === 0 && data.consulted.length === 0) continue;

  lines.push(`## ${role}`);
  lines.push('');

  // Agent brief summary
  const uniqueActsR = [...new Set(data.responsible.map(t => t.activityId))];
  const uniqueActsA = [...new Set(data.accountable.map(t => t.activityId))];
  const allUniqueActs = [...new Set([...uniqueActsR, ...uniqueActsA])];
  const wsSet = [...new Set(allUniqueActs.map(a => a.replace(/-\d+$/, '')))];

  lines.push('### Agent Brief');
  lines.push('');
  lines.push(`- **Responsible for:** ${data.responsible.length} tasks across ${uniqueActsR.length} activities`);
  lines.push(`- **Accountable for:** ${data.accountable.length} tasks across ${uniqueActsA.length} activities`);
  lines.push(`- **Consulted on:** ${data.consulted.length} tasks`);
  lines.push(`- **Informed about:** ${data.informed.length} tasks`);
  lines.push(`- **Workstreams:** ${wsSet.join(', ')}`);
  lines.push('');

  // Responsible tasks grouped by activity
  if (data.responsible.length > 0) {
    lines.push('### Responsible (R) — Tasks This Role Executes');
    lines.push('');
    const byAct = {};
    for (const t of data.responsible) {
      if (!byAct[t.activityId]) byAct[t.activityId] = { name: t.activityName, tasks: [] };
      byAct[t.activityId].tasks.push(t);
    }
    for (const [actId, info] of Object.entries(byAct)) {
      lines.push(`**${actId}** — ${info.name}`);
      for (const t of info.tasks) {
        lines.push(`- \`${t.taskId}\` ${t.taskName}`);
      }
      lines.push('');
    }
  }

  // Accountable tasks grouped by activity
  if (data.accountable.length > 0) {
    lines.push('### Accountable (A) — Tasks This Role Approves/Owns');
    lines.push('');
    const byAct = {};
    for (const t of data.accountable) {
      if (!byAct[t.activityId]) byAct[t.activityId] = { name: t.activityName, tasks: [] };
      byAct[t.activityId].tasks.push(t);
    }
    for (const [actId, info] of Object.entries(byAct)) {
      lines.push(`**${actId}** — ${info.name}`);
      for (const t of info.tasks) {
        lines.push(`- \`${t.taskId}\` ${t.taskName}`);
      }
      lines.push('');
    }
  }

  // Consulted — just list task IDs (compact)
  if (data.consulted.length > 0) {
    lines.push('### Consulted (C)');
    lines.push('');
    const byAct = {};
    for (const t of data.consulted) {
      if (!byAct[t.activityId]) byAct[t.activityId] = { name: t.activityName, tasks: [] };
      byAct[t.activityId].tasks.push(t);
    }
    for (const [actId, info] of Object.entries(byAct)) {
      lines.push(`- **${actId}** (${info.name}): ${info.tasks.map(t => '`' + t.taskId + '`').join(', ')}`);
    }
    lines.push('');
  }

  // Informed — just list task IDs (compact)
  if (data.informed.length > 0) {
    lines.push('### Informed (I)');
    lines.push('');
    const byAct = {};
    for (const t of data.informed) {
      if (!byAct[t.activityId]) byAct[t.activityId] = { name: t.activityName, tasks: [] };
      byAct[t.activityId].tasks.push(t);
    }
    for (const [actId, info] of Object.entries(byAct)) {
      lines.push(`- **${actId}** (${info.name}): ${info.tasks.map(t => '`' + t.taskId + '`').join(', ')}`);
    }
    lines.push('');
  }

  lines.push('---');
  lines.push('');
}

// Output
process.stdout.write(lines.join('\n'));
console.error('Done.');
