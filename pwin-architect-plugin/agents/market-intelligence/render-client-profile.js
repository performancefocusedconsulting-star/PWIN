#!/usr/bin/env node
/**
 * Buyer Intelligence Dossier — JSON → HTML Renderer (v2)
 *
 * Reads a v2 buyer intelligence JSON file, computes derived scores
 * (profileConfidence, coverageScore, freshnessScore) and buyer archetype,
 * and produces a printable HTML report.
 *
 * Usage:
 *   node render-client-profile.js <input.json> [output.html]
 *
 * Zero external dependencies — Node.js stdlib only.
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';

// ─── CLI ────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
if (args.length === 0 || args.includes('--help')) {
  console.log('Usage: node render-client-profile.js <data.json> [report.html]');
  process.exit(args.includes('--help') ? 0 : 1);
}

const inputPath = args[0];
const data = JSON.parse(readFileSync(inputPath, 'utf-8'));
const outputPath = args[1] || join(dirname(inputPath), 'report.html');

// ─── Computed scores ────────────────────────────────────────────────────────

function computeProfileConfidence(data) {
  const sources = data.sourceRegister?.sources || [];
  if (sources.length === 0) {
    return { rating: 'grey', rationale: 'No sources registered' };
  }
  const highCount = sources.filter(s => s.reliability === 'high').length;
  const pct = Math.round((highCount / sources.length) * 100);
  if (pct >= 60 && sources.length >= 8) {
    return { rating: 'green', rationale: `${pct}% high-reliability sources across ${sources.length} total` };
  } else if (pct >= 40 || sources.length >= 5) {
    return { rating: 'amber', rationale: `${pct}% high-reliability sources across ${sources.length} total` };
  } else {
    return { rating: 'red', rationale: `Only ${pct}% high-reliability sources, ${sources.length} total` };
  }
}

function computeCoverageScore(data) {
  const sections = [
    'buyerSnapshot', 'organisationContext', 'strategicPriorities',
    'commissioningContextHypotheses', 'procurementBehaviour',
    'decisionUnitAssumptions', 'cultureAndPreferences',
    'commercialAndRiskPosture', 'supplierEcosystem', 'risksAndSensitivities',
  ];
  let populated = 0;
  for (const s of sections) {
    const section = data[s];
    if (!section) continue;
    // Count a section as populated if it has more than just sectionConfidence
    const keys = Object.keys(section).filter(k => k !== 'sectionConfidence' && k !== 'sectionCaveat');
    const hasContent = keys.some(k => {
      const v = section[k];
      return v != null && v !== '' && !(Array.isArray(v) && v.length === 0);
    });
    if (hasContent) populated++;
  }
  const pct = Math.round((populated / sections.length) * 100);
  if (pct >= 80) return { rating: 'green', rationale: `${populated} of ${sections.length} sections populated` };
  if (pct >= 50) return { rating: 'amber', rationale: `${populated} of ${sections.length} sections populated` };
  if (populated === 0) return { rating: 'grey', rationale: 'No sections populated' };
  return { rating: 'red', rationale: `Only ${populated} of ${sections.length} sections populated` };
}

function computeFreshnessScore(data) {
  const sources = data.sourceRegister?.sources || [];
  if (sources.length === 0) return { rating: 'grey', rationale: 'No sources to assess freshness' };
  const now = new Date();
  let staleCount = 0;
  let datedCount = 0;
  for (const s of sources) {
    const d = s.publicationDate || s.accessDate;
    if (!d) continue;
    datedCount++;
    const age = (now - new Date(d)) / (1000 * 60 * 60 * 24);
    if (age > 365) staleCount++;
  }
  if (datedCount === 0) return { rating: 'grey', rationale: 'No dated sources' };
  const stalePct = Math.round((staleCount / datedCount) * 100);
  if (stalePct <= 10) return { rating: 'green', rationale: `${100 - stalePct}% of sources are within 12 months` };
  if (stalePct <= 30) return { rating: 'amber', rationale: `${stalePct}% of sources are over 12 months old` };
  return { rating: 'red', rationale: `${stalePct}% of sources are over 12 months old` };
}

function computeBuyerArchetype(data) {
  // Simple heuristic from procurement behaviour + culture + risk posture
  const culture = data.cultureAndPreferences || {};
  const risk = data.commercialAndRiskPosture || {};
  const proc = data.procurementBehaviour || {};

  const signals = {
    centralised_strategic: 0,
    devolved_operational: 0,
    transformation_driven: 0,
    compliance_driven: 0,
  };

  // Governance intensity
  const gov = culture.governanceIntensity?.value?.toLowerCase() || '';
  if (gov.includes('high') || gov.includes('formal')) signals.centralised_strategic++;
  if (gov.includes('low') || gov.includes('pragmatic')) signals.devolved_operational++;

  // Risk tolerance
  const risk_val = culture.riskTolerance?.value?.toLowerCase() || '';
  if (risk_val.includes('low') || risk_val.includes('risk-averse')) signals.compliance_driven++;
  if (risk_val.includes('high') || risk_val.includes('innovation')) signals.transformation_driven++;

  // Innovation preference
  const innov = proc.innovationVsProven?.value?.toLowerCase() || '';
  if (innov.includes('innovation') || innov.includes('digital')) signals.transformation_driven++;
  if (innov.includes('proven') || innov.includes('established')) signals.compliance_driven++;

  // Org type
  const orgType = data.buyerSnapshot?.organisationType || '';
  if (['department', 'mod'].includes(orgType)) signals.centralised_strategic++;
  if (['local_authority', 'nhs_trust'].includes(orgType)) signals.devolved_operational++;
  if (['regulator'].includes(orgType)) signals.compliance_driven++;

  const sorted = Object.entries(signals).sort((a, b) => b[1] - a[1]);
  if (sorted[0][1] === 0) return null;
  if (sorted[0][1] === sorted[1][1]) return 'mixed';
  return sorted[0][0];
}

// Apply computed values
data.computedScores = {
  profileConfidence: computeProfileConfidence(data),
  coverageScore: computeCoverageScore(data),
  freshnessScore: computeFreshnessScore(data),
};
if (data.buyerSnapshot) {
  data.buyerSnapshot.buyerArchetype = data.buyerSnapshot.buyerArchetype || computeBuyerArchetype(data);
}

// ─── HTML helpers ───────────────────────────────────────────────────────────

function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function ragDot(rating) {
  const colours = { red: '#C15050', amber: '#C68A1D', green: '#2D8A5E', grey: '#818CA2' };
  return `<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:${colours[rating] || colours.grey};vertical-align:middle;margin-right:6px;"></span>`;
}

function typeBadge(type) {
  const styles = {
    fact: 'background:rgba(45,138,94,0.12);color:#2D8A5E',
    inference: 'background:rgba(198,138,29,0.12);color:#7C5A0A',
    unknown: 'background:rgba(193,80,80,0.12);color:#C15050',
  };
  return `<span style="display:inline-block;font-size:9px;font-weight:700;letter-spacing:0.04em;padding:1px 6px;border-radius:2px;${styles[type] || styles.unknown}">${esc(type || 'unknown')}</span>`;
}

function confBadge(confidence) {
  const styles = {
    high: 'background:rgba(45,138,94,0.12);color:#2D8A5E',
    medium: 'background:rgba(198,138,29,0.12);color:#7C5A0A',
    low: 'background:rgba(193,80,80,0.12);color:#C15050',
  };
  return `<span style="display:inline-block;font-size:9px;font-weight:700;letter-spacing:0.04em;padding:1px 6px;border-radius:2px;${styles[confidence] || styles.low}">${esc(confidence || '?')}</span>`;
}

function sectionConfBadge(conf) {
  return `<div style="float:right;font-size:10px;">${confBadge(conf)}</div>`;
}

function renderEvidencedField(label, field) {
  if (!field || typeof field !== 'object' || !field.value) return '';
  return `
    <div class="ef-row">
      <div class="ef-label">${esc(label)}</div>
      <div class="ef-value">${esc(field.value)}</div>
      <div class="ef-meta">${typeBadge(field.type)} ${confBadge(field.confidence)} ${field.sourceRefs?.length ? `<span style="font-size:9px;color:#818CA2;">[${field.sourceRefs.join(', ')}]</span>` : ''}</div>
      ${field.rationale ? `<div class="ef-rationale">${esc(field.rationale)}</div>` : ''}
    </div>`;
}

function renderScoreCard(name, score) {
  const s = score || { rating: 'grey', rationale: 'Not computed' };
  return `
    <div class="score-card rag-${s.rating}">
      <div class="score-card-label">${esc(name)}</div>
      <div class="score-card-rating">${ragDot(s.rating)} ${esc({ red: 'Red', amber: 'Amber', green: 'Green', grey: 'Insufficient Evidence' }[s.rating] || 'Unknown')}</div>
      <div class="score-card-rationale">${esc(s.rationale)}</div>
    </div>`;
}

function fmtCurrency(v) {
  if (v == null) return '—';
  if (v >= 1e9) return `£${(v / 1e9).toFixed(1)}bn`;
  if (v >= 1e6) return `£${(v / 1e6).toFixed(1)}m`;
  if (v >= 1e3) return `£${(v / 1e3).toFixed(0)}k`;
  return `£${v}`;
}

// ─── Section renderers ──────────────────────────────────────────────────────

function renderSnapshot(snap) {
  if (!snap) return '';
  const rows = [
    ['Legal Name', snap.legalName],
    ['Parent Body', snap.parentBody],
    ['Organisation Type', snap.organisationType],
    ['Sector', snap.sector],
    ['Sub-sector', snap.subSector],
    ['Geographic Remit', snap.geographicRemit],
    ['Headcount', snap.headcount?.value],
    ['Annual Budget', snap.annualBudget?.value],
    ['Buyer Archetype', snap.buyerArchetype?.replace(/_/g, ' ')],
  ].filter(([, v]) => v != null);

  return `
  <div class="section no-break">
    <div class="section-title">Buyer Snapshot</div>
    <table class="kf-table">
      ${rows.map(([l, v]) => `<tr><td style="width:180px;font-weight:600;">${esc(l)}</td><td>${esc(String(v))}</td></tr>`).join('\n')}
    </table>
    ${snap.executiveSummary ? `<div class="section-text">${esc(snap.executiveSummary)}</div>` : ''}
    ${snap.keyRisks?.length ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 4px;">Key Risks</div>
    <ul class="risk-list">${snap.keyRisks.map(r => `<li>${esc(r)}</li>`).join('')}</ul>` : ''}
  </div>`;
}

function renderEvidencedSection(title, section, fields) {
  if (!section) return '';
  return `
  <div class="section">
    <div class="section-title">${esc(title)} ${sectionConfBadge(section.sectionConfidence)}</div>
    ${section.sectionCaveat ? `<div class="caveat">${esc(section.sectionCaveat)}</div>` : ''}
    ${section.summaryNarrative ? `<div class="section-text">${esc(section.summaryNarrative)}</div>` : ''}
    ${fields.map(([label, key]) => renderEvidencedField(label, section[key])).join('')}
    ${section.organisationStructure ? `<div class="section-text">${esc(section.organisationStructure)}</div>` : ''}
    ${section.recentChanges?.length ? `<div style="font-size:11px;font-weight:600;margin:10px 0 4px;">Recent Changes</div><ul class="gaps-list">${section.recentChanges.map(c => `<li>${esc(c)}</li>`).join('')}</ul>` : ''}
    ${section.intelligenceGaps?.length ? `<div style="font-size:11px;font-weight:600;margin:10px 0 4px;">Intelligence Gaps</div><ul class="gaps-list">${section.intelligenceGaps.map(g => `<li>${esc(g)}</li>`).join('')}</ul>` : ''}
  </div>`;
}

function renderLeadership(leaders) {
  if (!leaders?.length) return '';
  return `
    <table class="data-table">
      <tr><th>Name</th><th>Title</th><th>Relevance</th><th>Since</th><th>Source</th></tr>
      ${leaders.map(p => `<tr><td>${esc(p.name)}</td><td>${esc(p.title)}</td><td style="font-size:10px;">${esc(p.relevance || '—')}</td><td>${esc(p.startDate || '—')}</td><td style="font-size:10px;">${esc(p.source || '—')}</td></tr>`).join('')}
    </table>`;
}

function renderBusinessUnits(units) {
  if (!units?.length) return '';
  return `
    <table class="data-table">
      <tr><th>Unit</th><th>Remit</th><th>Relevance</th></tr>
      ${units.map(u => `<tr><td>${esc(u.name)}</td><td>${esc(u.remit || '—')}</td><td style="font-size:10px;">${esc(u.relevance || '—')}</td></tr>`).join('')}
    </table>`;
}

function renderStrategyThemes(themes) {
  if (!themes?.length) return '';
  return `
    <div style="font-size:11px;font-weight:600;margin:10px 0 4px;">Published Strategy Themes</div>
    <table class="data-table">
      <tr><th>Theme</th><th>Description</th><th>Sources</th></tr>
      ${themes.map(t => `<tr><td>${esc(t.theme)}</td><td>${esc(t.description || '—')}</td><td style="font-size:9px;">${(t.sourceRefs || []).join(', ')}</td></tr>`).join('')}
    </table>`;
}

function renderProgrammes(progs) {
  if (!progs?.length) return '';
  return `
    <div style="font-size:11px;font-weight:600;margin:10px 0 4px;">Major Programmes</div>
    <table class="data-table">
      <tr><th>Programme</th><th>Status</th><th>Value</th><th>Description</th></tr>
      ${progs.map(p => `<tr><td>${esc(p.name)}</td><td>${esc(p.status || '—')}</td><td>${esc(p.value || '—')}</td><td style="font-size:10px;">${esc(p.description || '—')}</td></tr>`).join('')}
    </table>`;
}

function renderProcBehaviour(proc) {
  if (!proc) return '';
  return `
  <div class="section page-break">
    <div class="section-title">Procurement Behaviour ${sectionConfBadge(proc.sectionConfidence)}</div>
    ${proc.summaryNarrative ? `<div class="section-text">${esc(proc.summaryNarrative)}</div>` : ''}
    <div class="eq-grid" style="grid-template-columns:repeat(3,1fr);">
      <div class="eq-card"><div class="eq-card-label">Total Awards</div><div class="eq-card-value">${proc.totalAwards || '—'}</div></div>
      <div class="eq-card"><div class="eq-card-label">Total Value</div><div class="eq-card-value">${fmtCurrency(proc.totalValue)}</div></div>
      <div class="eq-card"><div class="eq-card-label">Data Window</div><div class="eq-card-value" style="font-size:14px;">${esc(proc.dataWindow || '—')}</div></div>
    </div>
    ${proc.preferredRoutes?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Preferred Procurement Routes</div>
    <table class="data-table">
      <tr><th>Route</th><th style="text-align:center;">Count</th><th style="text-align:center;">%</th></tr>
      ${proc.preferredRoutes.map(r => `<tr><td>${esc(r.route)}</td><td style="text-align:center;">${r.count}</td><td style="text-align:center;">${r.percentage != null ? r.percentage + '%' : '—'}</td></tr>`).join('')}
    </table>` : ''}
    ${proc.categoryConcentration?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Category Concentration</div>
    <table class="data-table">
      <tr><th>Service Category</th><th style="text-align:center;">Awards</th><th style="text-align:center;">Value</th></tr>
      ${proc.categoryConcentration.map(c => `<tr><td>${esc(c.serviceCategory)}</td><td style="text-align:center;">${c.awardCount}</td><td style="text-align:center;">${fmtCurrency(c.totalValue)}</td></tr>`).join('')}
    </table>` : ''}
    ${proc.frameworkUsage?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Framework Usage</div>
    <table class="data-table">
      <tr><th>Framework</th><th>Provider</th><th style="text-align:center;">Awards</th><th style="text-align:center;">Value</th></tr>
      ${proc.frameworkUsage.map(f => `<tr><td>${esc(f.frameworkName)}</td><td>${esc(f.provider || '—')}</td><td style="text-align:center;">${f.awardCount}</td><td style="text-align:center;">${fmtCurrency(f.totalValue)}</td></tr>`).join('')}
    </table>` : ''}
    ${renderEvidencedField('Typical Contract Length', proc.typicalContractLength)}
    ${renderEvidencedField('Typical Contract Value', proc.typicalContractValue)}
    ${renderEvidencedField('Innovation vs Proven', proc.innovationVsProven)}
    ${renderEvidencedField('Price vs Quality Bias', proc.priceVsQualityBias)}
    ${renderEvidencedField('Renewal Patterns', proc.renewalPatterns)}
  </div>`;
}

function renderSupplierEcosystem(eco) {
  if (!eco) return '';
  const impColour = { critical: '#C15050', major: '#C68A1D', moderate: '#5CA3B6', minor: '#818CA2' };
  return `
  <div class="section page-break">
    <div class="section-title">Supplier Ecosystem ${sectionConfBadge(eco.sectionConfidence)}</div>
    ${eco.summaryNarrative ? `<div class="section-text">${esc(eco.summaryNarrative)}</div>` : ''}
    ${eco.incumbents?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Incumbent Suppliers</div>
    ${eco.incumbents.map(inc => `
    <div class="incumbent-card">
      <div class="incumbent-header">
        <span class="incumbent-name">${esc(inc.supplierName)}</span>
        <span style="color:${impColour[inc.strategicImportance] || '#818CA2'};font-size:10px;font-weight:700;text-transform:uppercase;">${esc(inc.strategicImportance || '—')}</span>
        ${inc.dossierRef ? `<span style="font-size:9px;color:#5CA3B6;">[dossier]</span>` : ''}
      </div>
      <div class="incumbent-detail">
        <span>Contracts: ${inc.contractCount || '—'}</span>
        <span>Value: ${fmtCurrency(inc.totalValue)}</span>
        <span>Since: ${esc(inc.longestRelationship || '—')}</span>
      </div>
      ${inc.serviceLines?.length ? `<div style="font-size:10px;color:#576482;margin-top:3px;">Service lines: ${inc.serviceLines.join(', ')}</div>` : ''}
      ${inc.entrenchmentIndicators?.length ? `<div style="font-size:10px;color:#576482;margin-top:3px;">Entrenchment: ${inc.entrenchmentIndicators.join(', ')}</div>` : ''}
      ${inc.recentActivity?.value ? `<div style="font-size:10px;margin-top:3px;">${typeBadge(inc.recentActivity.type)} ${esc(inc.recentActivity.value)}</div>` : ''}
    </div>`).join('')}` : ''}
    ${eco.adjacentSuppliers?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Adjacent Suppliers</div>
    <table class="data-table">
      <tr><th>Supplier</th><th>Service Lines</th><th>Evidence</th></tr>
      ${eco.adjacentSuppliers.map(a => `<tr><td>${esc(a.supplierName)}</td><td style="font-size:10px;">${(a.serviceLines || []).join(', ')}</td><td style="font-size:10px;">${esc(a.evidenceOfPresence || '—')}</td></tr>`).join('')}
    </table>` : ''}
    ${renderEvidencedField('Supplier Concentration', eco.supplierConcentration)}
    ${renderEvidencedField('Switching Evidence', eco.switchingEvidence)}
    ${eco.marketRefreshAreas?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Market Refresh Areas</div>
    ${eco.marketRefreshAreas.map(a => `
    <div style="padding:6px 12px;margin-bottom:4px;border-left:3px solid ${a.confidence === 'high' ? '#2D8A5E' : a.confidence === 'medium' ? '#C68A1D' : '#818CA2'};background:rgba(2,23,68,0.02);font-size:11px;">
      ${confBadge(a.confidence)} <strong>${esc(a.area)}</strong> — ${esc(a.evidence)}
    </div>`).join('')}` : ''}
  </div>`;
}

function renderRisks(risks) {
  if (!risks) return '';
  const sevColour = { high: '#C15050', medium: '#C68A1D', low: '#818CA2' };

  function renderIssueList(title, items) {
    if (!items?.length) return '';
    return `
      <div style="font-size:11px;font-weight:600;margin:12px 0 6px;">${esc(title)}</div>
      ${items.map(item => `
      <div style="padding:6px 12px;margin-bottom:4px;border-left:3px solid ${sevColour[item.severity] || '#818CA2'};font-size:11px;line-height:1.6;">
        ${esc(item.description)} ${item.date ? `<span style="color:#818CA2;">(${esc(item.date)})</span>` : ''} ${item.body ? `<span style="color:#576482;">[${esc(item.body)}]</span>` : ''}
        ${item.sourceRefs?.length ? `<span style="font-size:9px;color:#818CA2;">[${item.sourceRefs.join(', ')}]</span>` : ''}
      </div>`).join('')}`;
  }

  return `
  <div class="section">
    <div class="section-title">Risks, Sensitivities & Red Flags ${sectionConfBadge(risks.sectionConfidence)}</div>
    ${risks.summaryNarrative ? `<div class="section-text">${esc(risks.summaryNarrative)}</div>` : ''}
    ${renderIssueList('Procurement Controversies', risks.procurementControversies)}
    ${renderIssueList('Programme Failures', risks.programmeFailures)}
    ${renderIssueList('Audit Findings', risks.auditFindings)}
    ${renderIssueList('Media Scrutiny', risks.mediaScrutiny)}
    ${risks.publicSensitivities?.length ? `<div style="font-size:11px;font-weight:600;margin:12px 0 6px;">Public Sensitivities</div><ul class="gaps-list">${risks.publicSensitivities.map(s => `<li>${esc(s)}</li>`).join('')}</ul>` : ''}
    ${risks.positioningSensitivities?.length ? `<div style="font-size:11px;font-weight:600;margin:12px 0 6px;">Positioning Sensitivities</div><ul class="gaps-list">${risks.positioningSensitivities.map(s => `<li style="color:#C15050;">${esc(s)}</li>`).join('')}</ul>` : ''}
  </div>`;
}

function renderSourceRegister(sr) {
  if (!sr) return '';
  const sources = sr.sources || [];
  const tierColours = { tier1_official: '#2D8A5E', tier2_procurement: '#3A8CA0', tier3_secondary: '#C68A1D', tier4_internal: '#576482' };
  const tierLabels = { tier1_official: 'T1 Official', tier2_procurement: 'T2 Procurement', tier3_secondary: 'T3 Secondary', tier4_internal: 'T4 Internal' };

  return `
  <div class="section page-break">
    <div class="section-title">Source Register & Intelligence Gaps</div>
    <div class="eq-grid" style="grid-template-columns:repeat(4,1fr);">
      <div class="eq-card"><div class="eq-card-label">Total Sources</div><div class="eq-card-value">${sources.length}</div></div>
      <div class="eq-card"><div class="eq-card-label">High Reliability</div><div class="eq-card-value">${sources.filter(s => s.reliability === 'high').length}</div></div>
      <div class="eq-card"><div class="eq-card-label">Intelligence Gaps</div><div class="eq-card-value">${(sr.gaps || []).length}</div></div>
      <div class="eq-card"><div class="eq-card-label">Low Confidence Fields</div><div class="eq-card-value">${(sr.lowConfidenceInferences || []).length}</div></div>
    </div>
    ${sources.length ? `
    <table class="data-table" style="font-size:10px;">
      <tr><th>ID</th><th>Source</th><th>Type</th><th>Reliability</th><th>Date</th><th>Sections</th></tr>
      ${sources.map(s => `
      <tr>
        <td style="font-weight:600;">${esc(s.sourceId)}</td>
        <td>${esc(s.sourceName)}${s.url ? ` <a href="${esc(s.url)}" style="color:#5CA3B6;font-size:9px;">link</a>` : ''}</td>
        <td><span style="color:${tierColours[s.sourceType] || '#818CA2'};font-weight:600;font-size:9px;">${tierLabels[s.sourceType] || s.sourceType}</span></td>
        <td>${confBadge(s.reliability)}</td>
        <td>${esc(s.publicationDate || s.accessDate || '—')}</td>
        <td style="font-size:9px;">${(s.sectionsSupported || []).join(', ')}</td>
      </tr>`).join('')}
    </table>` : ''}
    ${sr.gaps?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Intelligence Gaps</div>
    ${sr.gaps.map(g => `
    <div class="gap-item">
      <div><strong>${esc(g.description)}</strong></div>
      <div style="font-size:10px;color:#576482;">Impact: ${esc(g.impact || '—')}</div>
      <div style="font-size:10px;color:#5CA3B6;">Action: ${esc(g.recommendedAction || '—')}</div>
    </div>`).join('')}` : ''}
  </div>`;
}

// ─── Assemble the full report ───────────────────────────────────────────────

const meta = data.meta || {};
const scores = data.computedScores || {};

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buyer Intelligence Dossier — ${esc(meta.buyerName || 'Unknown')}</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Inter, -apple-system, sans-serif; color: #021744; line-height: 1.65; font-size: 12px; max-width: 900px; margin: 0 auto; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  @page { size: A4; margin: 18mm; }
  @media print { body { padding: 0; } .page-break { page-break-before: always; } .no-break { page-break-inside: avoid; } }

  .cover { background: linear-gradient(135deg, #0D2B5C 0%, #1a3a6e 100%); padding: 40px 36px 32px; color: #F0EDE6; }
  .cover-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(240,237,230,0.45); margin-bottom: 6px; }
  .cover-title { font-family: 'Spline Sans', Inter, sans-serif; font-size: 28px; font-weight: 600; color: #F0EDE6; margin-bottom: 4px; }
  .cover-sub { font-size: 12px; color: rgba(240,237,230,0.55); margin-bottom: 24px; }
  .cover-scores { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .score-card { padding: 14px 16px; border: 1px solid rgba(240,237,230,0.15); background: rgba(240,237,230,0.04); }
  .score-card-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(240,237,230,0.5); margin-bottom: 6px; }
  .score-card-rating { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
  .score-card-rationale { font-size: 10px; color: rgba(240,237,230,0.6); line-height: 1.5; }
  .rag-red .score-card-rating { color: #E87070; }
  .rag-amber .score-card-rating { color: #D4A237; }
  .rag-green .score-card-rating { color: #6BC5A0; }
  .rag-grey .score-card-rating { color: #818CA2; }

  .report-body { padding: 28px 36px; border: 1px solid #D5D9E0; border-top: none; }
  .section { margin-bottom: 28px; }
  .section-title { font-family: 'Spline Sans', Inter, sans-serif; font-size: 15px; font-weight: 600; color: #021744; margin-bottom: 10px; padding-bottom: 7px; border-bottom: 1px solid #D5D9E0; overflow: hidden; }
  .section-text { font-size: 12px; color: #021744; line-height: 1.75; margin-bottom: 12px; white-space: pre-line; }
  .caveat { font-size: 11px; color: #C68A1D; padding: 8px 12px; background: rgba(198,138,29,0.06); border-left: 3px solid #C68A1D; margin-bottom: 12px; font-style: italic; }

  .ef-row { padding: 8px 0; border-bottom: 1px solid #F0ECE4; }
  .ef-label { font-size: 11px; font-weight: 600; color: #576482; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 3px; }
  .ef-value { font-size: 12px; color: #021744; line-height: 1.6; margin-bottom: 3px; }
  .ef-meta { display: flex; gap: 6px; align-items: center; }
  .ef-rationale { font-size: 10px; color: #818CA2; margin-top: 3px; font-style: italic; }

  .data-table { width: 100%; border-collapse: collapse; font-size: 11px; margin: 8px 0 16px; }
  .data-table th { background: #021744; color: #F0EDE6; padding: 7px 10px; text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }
  .data-table td { padding: 6px 10px; border-bottom: 1px solid #E8EBF0; vertical-align: top; }

  .kf-table { width: 100%; border-collapse: collapse; font-size: 11px; margin: 10px 0 16px; }
  .kf-table td { padding: 5px 10px; border-bottom: 1px solid #E8EBF0; }

  .eq-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
  .eq-card { padding: 12px 14px; border: 1px solid #D5D9E0; }
  .eq-card-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; color: #576482; margin-bottom: 4px; }
  .eq-card-value { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 500; color: #021744; }

  .incumbent-card { padding: 10px 14px; margin-bottom: 8px; border: 1px solid #E8EBF0; background: rgba(2,23,68,0.02); }
  .incumbent-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
  .incumbent-name { font-weight: 700; font-size: 13px; }
  .incumbent-detail { display: flex; gap: 16px; font-size: 11px; color: #576482; }

  .risk-list { list-style: none; padding: 0; margin: 8px 0; }
  .risk-list li { font-size: 11px; padding: 4px 0 4px 16px; position: relative; color: #C15050; }
  .risk-list li::before { content: '!'; position: absolute; left: 0; font-weight: 700; }

  .gaps-list { list-style: none; padding: 0; margin: 8px 0; }
  .gaps-list li { font-size: 11px; color: #576482; padding: 3px 0 3px 16px; position: relative; }
  .gaps-list li::before { content: '\\2192'; position: absolute; left: 0; color: #5CA3B6; }

  .gap-item { padding: 8px 12px; margin-bottom: 6px; border-left: 3px solid #C68A1D; background: rgba(198,138,29,0.04); }

  .report-footer { margin-top: 32px; padding-top: 14px; border-top: 1px solid #D5D9E0; font-size: 10px; color: #818CA2; display: flex; justify-content: space-between; }
</style>
</head>
<body>

<div class="cover">
  <div class="cover-label">Buyer Intelligence Dossier</div>
  <div class="cover-title">${esc(meta.buyerName || 'Unknown Buyer')}</div>
  <div class="cover-sub">${esc(meta.sector || '')} | ${esc(data.buyerSnapshot?.organisationType || '')} | Generated ${esc(meta.generatedAt || '')} | v${esc(meta.version || '')} | Depth: ${esc(meta.depthMode || '')}</div>
  <div class="cover-scores">
    ${renderScoreCard('Profile Confidence', scores.profileConfidence)}
    ${renderScoreCard('Coverage', scores.coverageScore)}
    ${renderScoreCard('Freshness', scores.freshnessScore)}
  </div>
</div>

<div class="report-body">

  ${renderSnapshot(data.buyerSnapshot)}

  ${renderEvidencedSection('Organisation & Operating Context', data.organisationContext, [
    ['Mandate', 'mandate'],
    ['Operating Model', 'operatingModel'],
    ['Funding Model', 'fundingModel'],
  ])}
  ${data.organisationContext?.keyBusinessUnits?.length ? renderBusinessUnits(data.organisationContext.keyBusinessUnits) : ''}
  ${data.organisationContext?.seniorLeadership?.length ? `<div style="font-size:11px;font-weight:600;margin:10px 0 4px;">Senior Leadership</div>${renderLeadership(data.organisationContext.seniorLeadership)}` : ''}

  ${renderEvidencedSection('Strategic Priorities & External Pressures', data.strategicPriorities, [
    ['Regulatory Pressures', 'regulatoryPressures'],
    ['Political Pressures', 'politicalPressures'],
    ['Fiscal Pressures', 'fiscalPressures'],
    ['Service Performance Pressures', 'servicePerformancePressures'],
  ])}
  ${renderStrategyThemes(data.strategicPriorities?.publishedStrategyThemes)}
  ${renderProgrammes(data.strategicPriorities?.majorProgrammes)}

  ${renderEvidencedSection('Commissioning Context Hypotheses', data.commissioningContextHypotheses, [
    ['Drivers of External Buying', 'driversOfExternalBuying'],
    ['Pressures Shaping Spend', 'pressuresShapingSpend'],
    ['Operational Pain Points', 'operationalPainPoints'],
    ['Outcomes Sought', 'outcomesSought'],
    ['Consequences of Inaction', 'consequencesOfInaction'],
  ])}

  ${renderProcBehaviour(data.procurementBehaviour)}

  ${renderEvidencedSection('Decision Unit & Stakeholder Assumptions', data.decisionUnitAssumptions, [
    ['Business Owner Roles', 'businessOwnerRoles'],
    ['Commercial Roles', 'commercialRoles'],
    ['Technical Stakeholders', 'technicalStakeholders'],
    ['Finance & Assurance Roles', 'financeAssuranceRoles'],
    ['Evaluator Groups', 'evaluatorGroups'],
  ])}

  ${renderEvidencedSection('Culture & Delivery Preferences', data.cultureAndPreferences, [
    ['Decision-Making Formality', 'decisionMakingFormality'],
    ['Governance Intensity', 'governanceIntensity'],
    ['Risk Tolerance', 'riskTolerance'],
    ['Evidence Preferences', 'evidencePreferences'],
    ['Supplier Interaction Style', 'supplierInteractionStyle'],
    ['Presentation Style', 'presentationStyle'],
  ])}

  ${renderEvidencedSection('Commercial & Risk Posture', data.commercialAndRiskPosture, [
    ['Affordability Sensitivity', 'affordabilitySensitivity'],
    ['Risk Transfer Posture', 'riskTransferPosture'],
    ['Contractual Caution', 'contractualCaution'],
    ['Cyber & Data Sensitivity', 'cyberDataSensitivity'],
    ['Mobilisation Sensitivity', 'mobilisationSensitivity'],
    ['Audit & FOI Exposure', 'auditFoiExposure'],
  ])}

  ${renderSupplierEcosystem(data.supplierEcosystem)}

  ${renderRisks(data.risksAndSensitivities)}

  ${renderSourceRegister(data.sourceRegister)}

</div>

<div class="report-footer">
  <div>BidEquity Buyer Intelligence Dossier | ${esc(meta.buyerName || '')} | Generated ${esc(meta.generatedAt || '')}</div>
  <div>Confidential — BidEquity</div>
</div>

</body>
</html>`;

writeFileSync(outputPath, html, 'utf-8');
console.log(`Rendered: ${outputPath}`);
console.log(`  Buyer: ${meta.buyerName}`);
console.log(`  Scores: profileConfidence=${scores.profileConfidence?.rating}, coverage=${scores.coverageScore?.rating}, freshness=${scores.freshnessScore?.rating}`);
console.log(`  Archetype: ${data.buyerSnapshot?.buyerArchetype || 'not computed'}`);
console.log(`  Sources: ${(data.sourceRegister?.sources || []).length}`);
console.log(`  Gaps: ${(data.sourceRegister?.gaps || []).length}`);
