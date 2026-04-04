/**
 * Skill Test Framework — Shared Helpers
 *
 * Generic infrastructure for testing AI skills against any procurement dataset.
 * No dataset-specific logic here — all validation is structural.
 */

import { execSync } from 'node:child_process';
import { writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';

const API_BASE = process.env.PWIN_API || 'http://localhost:3456';
const TEST_DATA = join(import.meta.dirname, '..', '..', '..', 'pwin-bid-execution', 'test-data');
const OUTPUT_DIR = join(import.meta.dirname, 'results');
const RATE_LIMIT_DELAY = parseInt(process.env.RATE_LIMIT_DELAY_MS || '0', 10);

// ---------------------------------------------------------------------------
// Document Extraction
// ---------------------------------------------------------------------------

async function extractPDF(relativePath, { pages } = {}) {
  const fullPath = join(TEST_DATA, relativePath);
  const script = `
import fitz, sys, json
doc = fitz.open(${JSON.stringify(fullPath)})
pages = ${pages ? JSON.stringify(pages) : 'None'}
texts = []
if pages:
    for i in pages:
        if i < len(doc):
            texts.append(doc[i].get_text())
else:
    for i in range(len(doc)):
        texts.append(doc[i].get_text())
result = {'pageCount': len(doc), 'extractedPages': len(texts), 'text': '\\n'.join(texts), 'chars': sum(len(t) for t in texts)}
print(json.dumps(result))
`;
  const result = execSync(`python3 -c ${JSON.stringify(script)}`, {
    maxBuffer: 50 * 1024 * 1024,
    timeout: 30000,
  });
  return JSON.parse(result.toString());
}

async function extractDocx(relativePath) {
  const fullPath = join(TEST_DATA, relativePath);
  const script = `
import zipfile, xml.etree.ElementTree as ET, json
with zipfile.ZipFile(${JSON.stringify(fullPath)}) as z:
    tree = ET.parse(z.open('word/document.xml'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    lines = []
    for p in tree.findall('.//w:p', ns):
        texts = [t.text for t in p.findall('.//w:t', ns) if t.text]
        if texts: lines.append(''.join(texts))
print(json.dumps({'text': '\\n'.join(lines), 'lines': len(lines)}))
`;
  const result = execSync(`python3 -c ${JSON.stringify(script)}`, {
    maxBuffer: 10 * 1024 * 1024,
    timeout: 15000,
  });
  return JSON.parse(result.toString());
}

// ---------------------------------------------------------------------------
// API Helpers
// ---------------------------------------------------------------------------

async function apiPost(path, data) {
  const r = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return r.json();
}

async function apiGet(path) {
  const r = await fetch(`${API_BASE}${path}`);
  return r.json();
}

async function apiPut(path, data) {
  const r = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return r.json();
}

async function createPursuit(data) {
  return apiPost('/api/pursuits', data);
}

async function executeSkill(skillId, input) {
  if (RATE_LIMIT_DELAY > 0) {
    console.log(`  ⏳ Rate limit delay: ${RATE_LIMIT_DELAY / 1000}s`);
    await new Promise(r => setTimeout(r, RATE_LIMIT_DELAY));
  }
  return apiPost(`/api/skills/${skillId}/execute`, input);
}

async function getProductData(pursuitId, product) {
  return apiGet(`/api/pursuits/${pursuitId}/${product}`);
}

async function setProductData(pursuitId, product, data) {
  return apiPut(`/api/pursuits/${pursuitId}/${product}`, data);
}

// ---------------------------------------------------------------------------
// Test Result Tracker
// ---------------------------------------------------------------------------

class TestResult {
  constructor(testName) {
    this.testName = testName;
    this.checks = [];
    this.warnings = [];
    this.startTime = Date.now();
    this.apiCost = 0;
    this.tokensIn = 0;
    this.tokensOut = 0;
  }

  pass(message) {
    this.checks.push({ pass: true, message });
    console.log(`  ✓ ${message}`);
  }

  fail(message) {
    this.checks.push({ pass: false, message });
    console.log(`  ✗ ${message}`);
  }

  check(condition, message) {
    condition ? this.pass(message) : this.fail(message);
  }

  warn(message) {
    this.warnings.push(message);
    console.log(`  ⚠ ${message}`);
  }

  recordUsage(usage, model) {
    const ti = usage?.input_tokens || 0;
    const to = usage?.output_tokens || 0;
    this.tokensIn += ti;
    this.tokensOut += to;
    if (model?.includes('haiku')) {
      this.apiCost += ti / 1_000_000 * 0.25 + to / 1_000_000 * 1.25;
    } else if (model?.includes('opus')) {
      this.apiCost += ti / 1_000_000 * 15 + to / 1_000_000 * 75;
    } else {
      this.apiCost += ti / 1_000_000 * 3 + to / 1_000_000 * 15;
    }
  }

  summary() {
    const passed = this.checks.filter(c => c.pass).length;
    const failed = this.checks.filter(c => !c.pass).length;
    const elapsed = ((Date.now() - this.startTime) / 1000).toFixed(1);
    console.log(`\n  ═══════════════════════════════════════`);
    console.log(`  ${this.testName}: ${passed} passed, ${failed} failed, ${this.warnings.length} warnings`);
    console.log(`  Tokens: ${this.tokensIn} in / ${this.tokensOut} out | Cost: $${this.apiCost.toFixed(4)} | Time: ${elapsed}s`);
    console.log(`  ═══���═══════════════════════════════════\n`);
    return { passed, failed, warnings: this.warnings.length, cost: this.apiCost, elapsed };
  }
}

// ---------------------------------------------------------------------------
// HTML Review Page Generator
// ---------------------------------------------------------------------------

async function generateReviewHTML(filename, { title, subtitle, sections }) {
  await mkdir(OUTPUT_DIR, { recursive: true });

  const esc = (s) => String(s || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  const sectionHTML = sections.map(s => {
    let content = '';
    if (s.type === 'table') {
      content = `<table><thead><tr>${s.headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>`;
      for (const row of s.rows) {
        content += `<tr>${row.map(c => `<td>${c}</td>`).join('')}</tr>`;
      }
      content += '</tbody></table>';
    } else if (s.type === 'cards') {
      content = `<div class="cards">${s.items.map(i =>
        `<div class="card"><div class="card-label">${esc(i.label)}</div><div class="card-value">${esc(i.value)}</div>${i.detail ? `<div class="card-detail">${esc(i.detail)}</div>` : ''}</div>`
      ).join('')}</div>`;
    } else if (s.type === 'text') {
      content = `<div class="text-block">${esc(s.content)}</div>`;
    } else if (s.type === 'json') {
      content = `<pre class="json-block">${esc(JSON.stringify(s.data, null, 2))}</pre>`;
    } else if (s.type === 'list') {
      content = `<div class="action-list">${s.items.map(i =>
        `<div class="action-item"><div class="action-priority">${esc(i.priority)}</div>${esc(i.text)}</div>`
      ).join('')}</div>`;
    } else if (s.type === 'checklist') {
      content = `<div class="checklist">${s.items.map(i =>
        `<div class="check-item ${i.pass ? 'check-pass' : 'check-fail'}"><span class="check-icon">${i.pass ? '✓' : '✗'}</span> ${esc(i.message)}</div>`
      ).join('')}</div>`;
    }
    return `<div class="section"><h2>${esc(s.title)}</h2>${s.subtitle ? `<div class="section-sub">${esc(s.subtitle)}</div>` : ''}${content}</div>`;
  }).join('\n');

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${esc(title)}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#F7F4EE;color:#021744;font-family:Inter,system-ui,sans-serif;font-size:14px;line-height:1.6;}
.header{background:#021744;color:#F0EDE6;padding:20px 32px;position:sticky;top:0;z-index:10;}
.header h1{font-size:20px;font-weight:700;}.header .sub{color:#60F5F7;font-size:10px;letter-spacing:.08em;text-transform:uppercase;margin-top:2px;}
.container{max-width:1200px;margin:0 auto;padding:24px 32px;}
.section{margin-bottom:32px;}
h2{font-size:18px;font-weight:600;margin-bottom:12px;padding-bottom:8px;border-bottom:2px solid #5CA3B6;}
.section-sub{font-size:11px;color:#818CA2;margin-bottom:12px;}
table{width:100%;border-collapse:collapse;background:#fff;margin-bottom:12px;}
th{background:#5CA3B6;color:#fff;font-size:10px;letter-spacing:.04em;text-transform:uppercase;padding:8px 12px;text-align:left;}
td{padding:8px 12px;border-bottom:1px solid #E8E4DC;font-size:12px;vertical-align:top;}
tr:hover td{background:#F0ECE4;}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;}
.card{background:#fff;border:1px solid #D5D9E0;padding:16px;}
.card-label{font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:#818CA2;margin-bottom:4px;}
.card-value{font-size:24px;font-weight:700;color:#5CA3B6;}.card-detail{font-size:11px;color:#576482;margin-top:4px;}
.text-block{background:#fff;border:1px solid #D5D9E0;border-left:3px solid #5CA3B6;padding:16px;font-size:13px;color:#576482;line-height:1.8;white-space:pre-wrap;}
.json-block{background:#021744;color:#60F5F7;padding:16px;font-size:11px;line-height:1.6;overflow-x:auto;max-height:500px;overflow-y:auto;}
.action-list{display:flex;flex-direction:column;gap:6px;}
.action-item{background:#fff;border:1px solid #D5D9E0;border-left:3px solid #C68A1D;padding:10px 14px;font-size:12px;}
.action-priority{font-size:9px;letter-spacing:.06em;text-transform:uppercase;color:#C68A1D;margin-bottom:2px;}
.checklist{display:flex;flex-direction:column;gap:4px;}
.check-item{padding:6px 12px;font-size:12px;border-left:3px solid;}
.check-pass{background:rgba(45,138,94,.05);border-color:#2D8A5E;color:#2D8A5E;}
.check-fail{background:rgba(193,80,80,.05);border-color:#C15050;color:#C15050;}
.check-icon{font-weight:700;margin-right:6px;}
</style>
</head>
<body>
<div class="header"><h1>${esc(title)}</h1><div class="sub">${esc(subtitle)}</div></div>
<div class="container">${sectionHTML}</div>
</body></html>`;

  const outPath = join(OUTPUT_DIR, filename);
  await writeFile(outPath, html, 'utf-8');
  return outPath;
}

function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

export {
  TEST_DATA, OUTPUT_DIR, RATE_LIMIT_DELAY,
  extractPDF, extractDocx,
  apiPost, apiGet, apiPut,
  createPursuit, executeSkill, getProductData, setProductData,
  TestResult, generateReviewHTML, estimateTokens,
};
