#!/usr/bin/env node
/**
 * Render a v2.2 buyer intelligence dossier JSON into a standalone HTML report.
 *
 * Usage:
 *   node scripts/render-buyer-dossier.js [path/to/data.json]
 *
 * If no path is given, reads from ~/.pwin/reference/clients/ and renders the
 * most recently modified dossier. Output is written alongside the JSON as
 * report.html and the path is printed to stdout.
 */

import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { homedir } from 'node:os';

// ── Locate input ────────────────────────────────────────────────────────────

function findLatest() {
  const base = join(homedir(), '.pwin', 'reference', 'clients');
  let newest = null, newestMtime = 0;
  for (const slug of readdirSync(base)) {
    const p = join(base, slug, 'data.json');
    try {
      const { mtimeMs } = statSync(p);
      if (mtimeMs > newestMtime) { newestMtime = mtimeMs; newest = p; }
    } catch { /* skip */ }
  }
  return newest;
}

const inputPath = process.argv[2] || findLatest();
if (!inputPath) { console.error('No dossier found. Pass a path or run the buyer-intelligence skill first.'); process.exit(1); }

const p = JSON.parse(readFileSync(inputPath, 'utf-8'));
const outPath = join(dirname(inputPath), 'report.html');

// ── Helpers ──────────────────────────────────────────────────────────────────

const strip = s => String(s ?? '').replace(/<cite[^>]*>|<\/cite>/g, '').trim();

function ev(field) {
  if (!field) return '—';
  if (typeof field === 'string') return strip(field);
  return strip(field.value ?? '—');
}

function confClass(field) {
  const c = (typeof field === 'object' ? field?.confidence : null) || '';
  return { high: 'conf-high', medium: 'conf-med', low: 'conf-low', unknown: 'conf-unk' }[c] || 'conf-unk';
}

function badge(field) {
  if (!field || typeof field !== 'object' || !field.confidence) return '';
  const labels = { high: 'HIGH', medium: 'MED', low: 'LOW', unknown: 'UNK' };
  return `<span class="badge ${confClass(field)}">${labels[field.confidence] ?? field.confidence.toUpperCase()}</span>`;
}

function typeTag(field) {
  if (!field || typeof field !== 'object' || !field.type) return '';
  const colours = { fact: 'tag-fact', signal: 'tag-signal', inference: 'tag-inf', unknown: 'tag-unk' };
  return `<span class="tag ${colours[field.type] || ''}">${field.type}</span>`;
}

function evRow(label, field) {
  if (!field) return '';
  const val = ev(field);
  if (!val || val === '—') return '';
  return `<tr>
    <td class="kl">${label}</td>
    <td>${val} ${typeTag(field)} ${badge(field)}</td>
  </tr>`;
}

function nl2p(s) {
  return strip(s).split(/\n+/).filter(Boolean).map(l => `<p>${l}</p>`).join('');
}

function fmt(v) { return v == null ? '—' : String(v); }

function srcLink(sources, id) {
  const s = (sources || []).find(x => x.sourceId === id);
  if (!s) return id;
  return s.url ? `<a href="${s.url}" target="_blank">${s.sourceName || id}</a>` : (s.sourceName || id);
}

// ── Data ─────────────────────────────────────────────────────────────────────

const meta   = p.meta || {};
const snap   = p.buyerSnapshot || {};
const supp   = p.buyerSnapshot_supplementary || {};
const proc   = p.procurementBehaviour || {};
const eco    = p.supplierEcosystem || {};
const sreg   = p.sourceRegister || {};
const sources = sreg.sources || [];

const genDate = meta.generatedAt ? new Date(meta.generatedAt).toLocaleDateString('en-GB', { day:'numeric', month:'long', year:'numeric' }) : '—';
const refDate = meta.refreshDue  ? new Date(meta.refreshDue).toLocaleDateString('en-GB', { day:'numeric', month:'long', year:'numeric' }) : '—';

// ── HTML ─────────────────────────────────────────────────────────────────────

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buyer Intelligence — ${meta.buyerName || 'Unknown'}</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'DM Sans', Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    color: #021744;
    font-size: 12px;
    line-height: 1.7;
    max-width: 940px;
    margin: 0 auto;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  @page { size: A4; margin: 16mm; }
  @media print { .no-break { page-break-inside: avoid; } .page-break { page-break-before: always; } }

  /* Cover */
  .cover {
    background: linear-gradient(135deg, #021744 0%, #0D2B5C 100%);
    padding: 44px 40px 36px;
    color: #F0EDE6;
  }
  .cover-eyebrow { font-size: 10px; text-transform: uppercase; letter-spacing: .12em; color: rgba(240,237,230,.45); margin-bottom: 8px; }
  .cover-name { font-size: 30px; font-weight: 700; margin-bottom: 4px; line-height: 1.2; }
  .cover-sub { font-size: 12px; color: rgba(240,237,230,.55); margin-bottom: 28px; }
  .cover-cards { display: flex; gap: 14px; flex-wrap: wrap; }
  .cover-card { flex: 1; min-width: 140px; padding: 14px 16px; border: 1px solid rgba(240,237,230,.15); background: rgba(240,237,230,.04); }
  .cover-card-label { font-size: 9px; text-transform: uppercase; letter-spacing: .08em; color: rgba(240,237,230,.5); margin-bottom: 4px; }
  .cover-card-value { font-size: 13px; font-weight: 600; line-height: 1.4; }

  /* Meta strip */
  .meta-strip {
    display: flex; gap: 24px; flex-wrap: wrap;
    padding: 10px 40px;
    background: #0D2B5C;
    color: rgba(240,237,230,.65);
    font-size: 10px;
  }
  .meta-strip span { display: flex; gap: 6px; align-items: center; }
  .meta-strip b { color: rgba(240,237,230,.9); }

  /* Body */
  .body { padding: 32px 40px; }

  /* Section */
  .section { margin-bottom: 32px; }
  .section-title {
    font-size: 14px; font-weight: 700; color: #021744;
    padding-bottom: 8px; border-bottom: 2px solid #021744;
    margin-bottom: 14px; text-transform: uppercase; letter-spacing: .05em;
  }
  .section-intro { color: #3A4A6B; margin-bottom: 14px; font-size: 12px; line-height: 1.75; }
  .section-intro p { margin-bottom: 6px; }

  /* Archetype callout */
  .archetype-box {
    background: rgba(2,23,68,.04); border-left: 4px solid #5CA3B6;
    padding: 12px 16px; margin-bottom: 16px;
  }
  .archetype-label { font-size: 9px; text-transform: uppercase; letter-spacing: .08em; color: #5CA3B6; margin-bottom: 4px; }
  .archetype-value { font-size: 14px; font-weight: 700; color: #021744; }

  /* Key facts table */
  table.kf { width: 100%; border-collapse: collapse; margin-bottom: 14px; }
  table.kf .kl { width: 200px; font-weight: 600; color: #3A4A6B; font-size: 11px; padding: 6px 10px 6px 0; vertical-align: top; border-bottom: 1px solid #E8EBF0; }
  table.kf td { padding: 6px 10px 6px 0; border-bottom: 1px solid #E8EBF0; vertical-align: top; font-size: 12px; }

  /* Data table */
  table.dt { width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 11px; }
  table.dt th { background: #021744; color: #F0EDE6; padding: 7px 10px; text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: .04em; }
  table.dt td { padding: 7px 10px; border-bottom: 1px solid #E8EBF0; vertical-align: top; }
  table.dt tr:hover td { background: rgba(2,23,68,.025); }
  .imp-critical { color: #C15050; font-weight: 700; }
  .imp-high     { color: #C67810; font-weight: 600; }
  .imp-medium   { color: #2D8A5E; }

  /* Badges */
  .badge { display: inline-block; font-size: 9px; font-weight: 700; letter-spacing: .04em; padding: 1px 6px; border-radius: 2px; margin-left: 4px; vertical-align: middle; }
  .conf-high { background: rgba(45,138,94,.12); color: #2D8A5E; }
  .conf-med  { background: rgba(198,138,29,.12); color: #7C5A0A; }
  .conf-low  { background: rgba(193,80,80,.12);  color: #C15050; }
  .conf-unk  { background: rgba(100,100,120,.10); color: #666; }

  /* Type tags */
  .tag { display: inline-block; font-size: 8px; text-transform: uppercase; letter-spacing: .04em; padding: 1px 5px; border-radius: 2px; margin-left: 3px; vertical-align: middle; }
  .tag-fact   { background: rgba(92,163,182,.15); color: #3A8CA0; }
  .tag-signal { background: rgba(198,138,29,.12); color: #7C5A0A; }
  .tag-inf    { background: rgba(128,90,180,.12); color: #5A3A90; }
  .tag-unk    { background: rgba(100,100,120,.10); color: #666; }

  /* Risk list */
  .risk-list { list-style: none; margin: 0; padding: 0; }
  .risk-list li { padding: 6px 0 6px 18px; position: relative; border-bottom: 1px solid #E8EBF0; font-size: 11.5px; }
  .risk-list li::before { content: '▸'; position: absolute; left: 0; color: #5CA3B6; }

  /* Source list */
  .src-list { list-style: none; margin: 0; padding: 0; }
  .src-list li { padding: 7px 0; border-bottom: 1px solid #E8EBF0; font-size: 11px; }
  .src-list a { color: #0D2B5C; }
  .src-type { color: #5CA3B6; font-size: 10px; margin-left: 6px; }

  /* Gap list */
  .gap-list { list-style: none; margin: 0; padding: 0; }
  .gap-list li { padding: 5px 0 5px 16px; position: relative; font-size: 11px; color: #555; border-bottom: 1px solid #E8EBF0; }
  .gap-list li::before { content: '○'; position: absolute; left: 0; color: #C15050; }

  /* Footer */
  .footer { margin-top: 40px; padding: 14px 40px; background: #F5F6F8; border-top: 1px solid #D5D9E0; font-size: 10px; color: #888; display: flex; justify-content: space-between; }

  a { color: #0D2B5C; }
</style>
</head>
<body>

<!-- COVER -->
<div class="cover">
  <div class="cover-eyebrow">Buyer Intelligence Dossier · v${meta.version || '2.2'} · ${meta.depthMode || 'snapshot'} depth</div>
  <div class="cover-name">${meta.buyerName || '—'}</div>
  <div class="cover-sub">${snap.organisationType || ''} · ${(meta.sector || '').replace(/_/g,' ')} · ${snap.geographicRemit || ''}</div>
  <div class="cover-cards">
    <div class="cover-card">
      <div class="cover-card-label">Annual budget</div>
      <div class="cover-card-value">${ev(snap.annualBudget).split(';')[0]}</div>
    </div>
    <div class="cover-card">
      <div class="cover-card-label">Headcount</div>
      <div class="cover-card-value">${ev(snap.headcount).split('(')[0].trim()}</div>
    </div>
    <div class="cover-card">
      <div class="cover-card-label">Visible procurement spend</div>
      <div class="cover-card-value">${fmt(proc.totalValue)}</div>
    </div>
    <div class="cover-card">
      <div class="cover-card-label">Awards in dataset</div>
      <div class="cover-card-value">${fmt(proc.totalAwards)}</div>
    </div>
  </div>
</div>
<div class="meta-strip">
  <span>Generated <b>${genDate}</b></span>
  <span>By <b>${meta.generatedBy || '—'}</b></span>
  <span>Refresh due <b>${refDate}</b></span>
  <span>Sources <b>${sources.length}</b></span>
  <span>Depth <b>${meta.depthMode || '—'}</b></span>
</div>

<div class="body">

<!-- ── SECTION 1: ORGANISATION SNAPSHOT ──────────────────────────────── -->
<div class="section no-break">
  <div class="section-title">1 · Organisation Snapshot</div>

  ${snap.executiveSummary?.headline ? `
  <div class="archetype-box">
    <div class="archetype-label">Executive summary</div>
    <div class="archetype-value" style="font-size:13px;font-weight:400;line-height:1.6;">${strip(snap.executiveSummary.headline)}</div>
  </div>` : ''}

  ${snap.organisationalArchetype ? `
  <div class="archetype-box" style="border-color:#021744;">
    <div class="archetype-label">Organisational archetype</div>
    <div class="archetype-value">${ev(snap.organisationalArchetype).replace(/_/g,' ')}</div>
    ${snap.organisationalArchetype.rationale ? `<div style="font-size:11px;color:#555;margin-top:6px;">${strip(snap.organisationalArchetype.rationale)}</div>` : ''}
  </div>` : ''}

  <table class="kf">
    ${evRow('Legal name', snap.legalName || snap.buyerName || meta.buyerName)}
    ${evRow('Parent body', snap.parentBody)}
    ${evRow('Organisation type', snap.organisationType)}
    ${evRow('Sector / sub-sector', (snap.sector || '') + (snap.subSector ? ' · ' + snap.subSector.replace(/_/g,' ') : ''))}
    ${evRow('Geographic remit', snap.geographicRemit)}
    ${evRow('Annual budget', snap.annualBudget)}
    ${evRow('Headcount', snap.headcount)}
  </table>

  ${snap.executiveSummary?.keyRisks?.length ? `
  <div style="font-weight:600;font-size:11px;margin-bottom:6px;color:#3A4A6B;">Key organisational risks</div>
  <ul class="risk-list">
    ${snap.executiveSummary.keyRisks.map(r => `<li>${strip(r)}</li>`).join('')}
  </ul>` : ''}
</div>

<!-- ── SECTION 2: LEADERSHIP & CONTEXT ───────────────────────────────── -->
<div class="section no-break">
  <div class="section-title">2 · Leadership &amp; Strategic Context</div>
  <table class="kf">
    ${evRow('Senior leadership', supp.senior_leadership)}
    ${evRow('Strategic priorities', supp.strategic_priorities_snapshot)}
    ${evRow('Recent changes', supp.recent_changes)}
  </table>
  ${meta.refreshTriggers?.length ? `
  <div style="font-size:11px;color:#555;margin-top:8px;">
    <b>Refresh triggers:</b> ${meta.refreshTriggers.join(' · ')}
  </div>` : ''}
</div>

<!-- ── SECTION 3: PROCUREMENT BEHAVIOUR ──────────────────────────────── -->
<div class="section">
  <div class="section-title">3 · Procurement Behaviour</div>

  ${proc.summaryNarrative ? `<div class="section-intro">${nl2p(proc.summaryNarrative)}</div>` : ''}

  <table class="kf">
    ${evRow('Preferred routes to market', proc.preferredRoutes)}
    ${evRow('Framework usage', proc.frameworkUsage)}
    ${evRow('Shared service arrangements', proc.sharedServiceArrangements)}
    ${evRow('Typical contract length', proc.typicalContractLength)}
    ${evRow('Typical contract value', proc.typicalContractValue)}
    ${evRow('Category concentration', proc.categoryConcentration)}
    ${evRow('Innovation vs proven', proc.innovationVsProven)}
    ${evRow('Price vs quality bias', proc.priceVsQualityBias)}
    ${evRow('Renewal patterns', proc.renewalPatterns)}
  </table>

  ${proc.dataWindow ? `<div style="font-size:10px;color:#888;margin-top:-8px;">Data window: ${strip(proc.dataWindow)}</div>` : ''}
</div>

<!-- ── SECTION 4: SUPPLIER ECOSYSTEM ─────────────────────────────────── -->
<div class="section page-break">
  <div class="section-title">4 · Supplier Ecosystem</div>

  ${eco.summaryNarrative ? `<div class="section-intro">${nl2p(eco.summaryNarrative)}</div>` : ''}

  ${eco.incumbents?.length ? `
  <table class="dt">
    <thead><tr>
      <th>Supplier</th>
      <th>Service lines</th>
      <th>Contracts</th>
      <th>Total value</th>
      <th>Strategic importance</th>
      <th>Entrenchment</th>
    </tr></thead>
    <tbody>
    ${eco.incumbents.map(s => `<tr>
      <td style="font-weight:600;">${fmt(s.supplierName)}</td>
      <td>${(s.serviceLines || []).join(', ')}</td>
      <td style="text-align:center;">${fmt(s.contractCount)}</td>
      <td style="white-space:nowrap;">${fmt(s.totalValue)}</td>
      <td class="imp-${s.strategicImportance || 'medium'}">${fmt(s.strategicImportance)}</td>
      <td style="font-size:10.5px;color:#555;">${(s.entrenchmentIndicators || '').slice(0,120)}${(s.entrenchmentIndicators || '').length > 120 ? '…' : ''}</td>
    </tr>`).join('')}
    </tbody>
  </table>` : ''}

  <table class="kf">
    ${evRow('Supplier concentration', eco.supplierConcentration)}
    ${evRow('Switching evidence', eco.switchingEvidence)}
    ${eco.adjacentSuppliers ? `<tr><td class="kl">Adjacent suppliers</td><td>${strip(eco.adjacentSuppliers)}</td></tr>` : ''}
    ${eco.marketRefreshAreas ? `<tr><td class="kl">Market refresh areas</td><td>${strip(eco.marketRefreshAreas)}</td></tr>` : ''}
  </table>
</div>

<!-- ── SECTION 5: SOURCE REGISTER ─────────────────────────────────────── -->
<div class="section no-break">
  <div class="section-title">5 · Evidence &amp; Source Register</div>

  ${sources.length ? `
  <ul class="src-list">
    ${sources.map(s => `<li>
      <b>${s.sourceId}</b> —
      ${s.url ? `<a href="${s.url}" target="_blank">${s.sourceName || s.url}</a>` : (s.sourceName || '—')}
      <span class="src-type">${s.sourceType || ''}</span>
      ${s.publicationDate ? `<span style="color:#888;font-size:10px;"> · ${s.publicationDate}</span>` : ''}
    </li>`).join('')}
  </ul>` : '<p style="color:#888;">No sources recorded.</p>'}

  ${sreg.gaps?.length ? `
  <div style="margin-top:16px;font-weight:600;font-size:11px;color:#3A4A6B;margin-bottom:6px;">Evidence gaps</div>
  <ul class="gap-list">
    ${sreg.gaps.map(g => `<li>${strip(g)}</li>`).join('')}
  </ul>` : ''}

  ${sreg.lowConfidenceInferences?.length ? `
  <div style="margin-top:12px;font-weight:600;font-size:11px;color:#3A4A6B;margin-bottom:6px;">Low-confidence inferences</div>
  <ul class="gap-list">
    ${sreg.lowConfidenceInferences.map(g => `<li>${strip(typeof g === 'object' ? (g.inference || JSON.stringify(g)) : g)}</li>`).join('')}
  </ul>` : ''}
</div>

</div><!-- /body -->

<div class="footer">
  <span>${meta.buyerName} · Buyer Intelligence Dossier · ${meta.depthMode} · v${meta.version}</span>
  <span>Generated ${genDate} · Refresh due ${refDate} · ${meta.generatedBy}</span>
</div>

</body>
</html>`;

writeFileSync(outPath, html, 'utf-8');
console.log(`Report written to: ${outPath}`);
