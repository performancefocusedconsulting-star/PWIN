#!/usr/bin/env node
/**
 * Supplier Intelligence Dossier — JSON → HTML Renderer (v2)
 *
 * Reads a v2 supplier dossier JSON file, computes derived scores
 * (supplierBreadth, serviceLineConcentration, evidenceQuality),
 * and produces a printable HTML report.
 *
 * Usage:
 *   node render-dossier.js <input.json> [output.html]
 *
 * If output path is omitted, writes to the same directory as the input
 * with the name report.html.
 *
 * Zero external dependencies — Node.js stdlib only.
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, basename } from 'node:path';

// ─── CLI ────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
if (args.length === 0 || args.includes('--help')) {
  console.log('Usage: node render-dossier.js <data.json> [report.html]');
  process.exit(args.includes('--help') ? 0 : 1);
}

const inputPath = args[0];
const data = JSON.parse(readFileSync(inputPath, 'utf-8'));
const outputPath = args[1] || join(dirname(inputPath), 'report.html');

// ─── Computed scores ────────────────────────────────────────────────────────

function computeSupplierBreadth(data) {
  const serviceLines = (data.serviceLineProfile || []).length;
  const sectors = new Set((data.contracts || []).map(c => c.sector).filter(Boolean));
  const buyers = new Set((data.contracts || []).map(c => c.buyer).filter(Boolean));
  const frameworks = (data.frameworks || []).filter(f => f.status === 'live').length;

  // Simple heuristic: breadth across four dimensions
  const factors = [
    { name: 'Service line count', finding: `${serviceLines} evidenced service lines`, evidenced: serviceLines > 0, evidenceSummary: `${serviceLines} categories in service line profile` },
    { name: 'Sector diversity', finding: `Active in ${sectors.size} sectors`, evidenced: sectors.size > 0, evidenceSummary: `${sectors.size} distinct sectors across contracts` },
    { name: 'Buyer diversity', finding: `${buyers.size} distinct buyers`, evidenced: buyers.size > 0, evidenceSummary: `${buyers.size} contracting authorities in contract portfolio` },
    { name: 'Framework coverage', finding: `${frameworks} live frameworks`, evidenced: frameworks > 0, evidenceSummary: `${frameworks} active framework memberships` },
  ];

  // Rating: green if strong across 3+ dimensions, amber if 2, red if 1, grey if no data
  const strong = [
    serviceLines >= 4,
    sectors.size >= 3,
    buyers.size >= 5,
    frameworks >= 3,
  ].filter(Boolean).length;

  let rating, rationale;
  if (serviceLines === 0 && sectors.size === 0) {
    rating = 'grey';
    rationale = 'Insufficient data to assess supplier breadth';
  } else if (strong >= 3) {
    rating = 'green';
    rationale = `Well-diversified: ${serviceLines} service lines, ${sectors.size} sectors, ${buyers.size} buyers`;
  } else if (strong >= 2) {
    rating = 'amber';
    rationale = `Moderate diversification: ${serviceLines} service lines, ${sectors.size} sectors, ${buyers.size} buyers`;
  } else {
    rating = 'red';
    rationale = `Concentrated supplier: limited spread across service lines, sectors, and buyers`;
  }

  return { rating, rationale, factors };
}

function computeServiceLineConcentration(data) {
  const profile = data.serviceLineProfile || [];
  if (profile.length === 0) {
    return {
      rating: 'grey',
      rationale: 'No service line data available to assess concentration',
      factors: [],
    };
  }

  // Use contract counts as a proxy for concentration
  const total = profile.reduce((sum, sl) => sum + (sl.contractCount || 0), 0);
  const coreLines = profile.filter(sl => sl.significance === 'core');
  const topLine = profile.reduce((max, sl) => (sl.contractCount || 0) > (max.contractCount || 0) ? sl : max, profile[0]);
  const topShare = total > 0 ? (topLine.contractCount || 0) / total : 0;

  const factors = [
    { name: 'Total service lines', finding: `${profile.length} evidenced`, evidenced: true, evidenceSummary: `${profile.length} categories with evidence` },
    { name: 'Core service lines', finding: `${coreLines.length} classified as core`, evidenced: true, evidenceSummary: coreLines.map(sl => sl.categoryId).join(', ') || 'None' },
    { name: 'Top line share', finding: `${topLine.categoryId}: ${Math.round(topShare * 100)}% of contracts`, evidenced: total > 0, evidenceSummary: `${topLine.contractCount || 0} of ${total} contracts` },
  ];

  let rating, rationale;
  if (topShare > 0.6 || profile.length <= 2) {
    rating = 'red';
    rationale = `Highly concentrated: ${topLine.categoryId} accounts for ${Math.round(topShare * 100)}% of contracts`;
  } else if (topShare > 0.4 || profile.length <= 3) {
    rating = 'amber';
    rationale = `Moderate concentration: ${topLine.categoryId} is the dominant line at ${Math.round(topShare * 100)}% of contracts`;
  } else {
    rating = 'green';
    rationale = `Well-distributed across ${profile.length} service lines, no single line dominates`;
  }

  return { rating, rationale, factors };
}

function computeEvidenceQuality(data) {
  const register = data.evidenceRegister || [];
  if (register.length === 0) {
    return {
      rating: 'grey',
      rationale: 'No evidence register entries to assess',
      factors: [],
    };
  }

  // Tier distribution
  const tierCounts = [0, 0, 0, 0, 0, 0, 0]; // index 1-6
  register.forEach(e => { if (e.sourceTier >= 1 && e.sourceTier <= 6) tierCounts[e.sourceTier]++; });
  const highTier = tierCounts[1] + tierCounts[2] + tierCounts[3];
  const highTierPct = Math.round((highTier / register.length) * 100);

  // Confidence distribution
  const avgConfidence = Math.round(register.reduce((sum, e) => sum + (e.confidence || 0), 0) / register.length);

  // Claim types
  const typeCounts = {};
  register.forEach(e => { typeCounts[e.claimType] = (typeCounts[e.claimType] || 0) + 1; });
  const verifiedPct = Math.round(((typeCounts['verified_fact'] || 0) / register.length) * 100);

  // Contradictions
  const contradictions = register.filter(e => e.contradictionFlag).length;

  const factors = [
    { name: 'Total claims registered', finding: `${register.length} material claims`, evidenced: true, evidenceSummary: `${register.length} entries in evidence register` },
    { name: 'High-tier sources (T1-T3)', finding: `${highTierPct}% of claims from Tier 1-3`, evidenced: true, evidenceSummary: `T1: ${tierCounts[1]}, T2: ${tierCounts[2]}, T3: ${tierCounts[3]}` },
    { name: 'Average confidence', finding: `${avgConfidence}`, evidenced: true, evidenceSummary: `Mean confidence across all claims` },
    { name: 'Verified facts', finding: `${verifiedPct}% of claims are verified facts`, evidenced: true, evidenceSummary: `${typeCounts['verified_fact'] || 0} of ${register.length}` },
    { name: 'Contradictions', finding: `${contradictions} flagged`, evidenced: true, evidenceSummary: contradictions > 0 ? `${contradictions} claims have conflicting evidence` : 'No contradictions identified' },
  ];

  let rating, rationale;
  if (highTierPct >= 60 && avgConfidence >= 70 && contradictions <= 2) {
    rating = 'green';
    rationale = `Strong evidence base: ${highTierPct}% high-tier sources, avg confidence ${avgConfidence}`;
  } else if (highTierPct >= 40 && avgConfidence >= 55) {
    rating = 'amber';
    rationale = `Adequate evidence: ${highTierPct}% high-tier sources, avg confidence ${avgConfidence}`;
  } else if (register.length < 5) {
    rating = 'grey';
    rationale = `Too few evidence entries (${register.length}) for a reliable quality assessment`;
  } else {
    rating = 'red';
    rationale = `Weak evidence base: only ${highTierPct}% high-tier sources, avg confidence ${avgConfidence}`;
  }

  return { rating, rationale, factors };
}

// Apply computed scores to the data
data.scores.supplierBreadth = computeSupplierBreadth(data);
data.scores.serviceLineConcentration = computeServiceLineConcentration(data);
data.scores.evidenceQuality = computeEvidenceQuality(data);

// ─── Hydrate evidence register ──────────────────────────────────────────────
// The model emits core fields; the renderer fills in claimId, retrievedAt,
// staleAfterDays, and runs contradiction detection.

function hydrateEvidenceRegister(data) {
  const register = data.evidenceRegister || [];
  const generatedAt = data.meta?.generatedAt || new Date().toISOString();

  // Section → staleness window mapping
  const stalenessMap = {
    'contracts': 7, 'frameworks': 7, 'bidOutcomeSignals': 7,
    'financialTrajectory': 90, 'marketVoiceSignals': 30,
    'leadership': 60, 'partnerships': 60,
    'riskExposureProfile': 30, 'serviceLineProfile': 30,
    'identity': 90, 'scores': 30, 'executiveSummary': 30,
  };

  // Assign sequential claimIds and fill renderer fields
  register.forEach((claim, i) => {
    if (!claim.claimId) claim.claimId = `C${String(i + 1).padStart(3, '0')}`;
    if (!claim.retrievedAt) claim.retrievedAt = generatedAt;

    // Derive staleAfterDays from fieldPath section
    if (!claim.staleAfterDays && claim.fieldPath) {
      const section = claim.fieldPath.split('.')[0].split('[')[0];
      claim.staleAfterDays = stalenessMap[section] || 30;
    }

    // Default contradiction fields
    if (claim.contradictionFlag === undefined) claim.contradictionFlag = false;
    if (!claim.contradicts) claim.contradicts = [];
  });

  // Simple contradiction scan: flag claims on the same fieldPath with different values
  const byField = {};
  register.forEach(claim => {
    if (!claim.fieldPath) return;
    if (!byField[claim.fieldPath]) byField[claim.fieldPath] = [];
    byField[claim.fieldPath].push(claim);
  });

  for (const [, claims] of Object.entries(byField)) {
    if (claims.length < 2) continue;
    const values = new Set(claims.map(c => c.value).filter(Boolean));
    if (values.size > 1) {
      // Different values for the same field — flag all as contradictions
      const ids = claims.map(c => c.claimId);
      claims.forEach(c => {
        c.contradictionFlag = true;
        c.contradicts = ids.filter(id => id !== c.claimId);
      });
    }
  }

  data.evidenceRegister = register;
}

hydrateEvidenceRegister(data);

// ─── HTML helpers ───────────────────────────────────────────────────────────

function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function ragDot(rating) {
  const colours = { red: '#C15050', amber: '#C68A1D', green: '#2D8A5E', grey: '#818CA2' };
  const c = colours[rating] || colours.grey;
  return `<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:${c};vertical-align:middle;margin-right:6px;"></span>`;
}

function ragClass(rating) {
  return `rag-${rating || 'grey'}`;
}

function ragLabel(rating) {
  const labels = { red: 'Red', amber: 'Amber', green: 'Green', grey: 'Insufficient Evidence' };
  return labels[rating] || 'Unknown';
}

function fmtValue(v) {
  if (v == null) return '—';
  if (typeof v === 'number') {
    if (Math.abs(v) >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)}bn`;
    if (Math.abs(v) >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}m`;
    if (Math.abs(v) >= 1_000) return `${(v / 1_000).toFixed(1)}k`;
    return String(v);
  }
  return String(v);
}

function fmtCurrency(v, currency) {
  if (v == null) return '—';
  const sym = currency === 'GBP' ? '£' : currency === 'USD' ? '$' : currency === 'EUR' ? '€' : `${currency} `;
  return sym + fmtValue(v);
}

function fmtPct(v) {
  if (v == null) return '—';
  return `${Number(v).toFixed(1)}%`;
}

function fmtDate(d) {
  if (!d) return '—';
  return String(d);
}

function claimBadge(claimType) {
  const styles = {
    verified_fact: 'background:rgba(45,138,94,0.12);color:#2D8A5E',
    derived_estimate: 'background:rgba(92,163,182,0.12);color:#3A8CA0',
    analytical_hypothesis: 'background:rgba(198,138,29,0.12);color:#7C5A0A',
    signal_to_monitor: 'background:rgba(129,140,162,0.12);color:#576482',
  };
  const labels = {
    verified_fact: 'Fact',
    derived_estimate: 'Estimate',
    analytical_hypothesis: 'Hypothesis',
    signal_to_monitor: 'Signal',
  };
  const s = styles[claimType] || styles.signal_to_monitor;
  const l = labels[claimType] || claimType;
  return `<span style="display:inline-block;font-size:9px;font-weight:700;letter-spacing:0.04em;padding:1px 6px;border-radius:2px;${s}">${esc(l)}</span>`;
}

// ─── Section renderers ──────────────────────────────────────────────────────

function renderScoreCard(name, score) {
  const s = score || { rating: 'grey', rationale: 'Not assessed' };
  return `
    <div class="score-card ${ragClass(s.rating)}">
      <div class="score-card-label">${esc(name)}</div>
      <div class="score-card-rating">${ragDot(s.rating)} ${esc(ragLabel(s.rating))}</div>
      <div class="score-card-rationale">${esc(s.rationale)}</div>
    </div>`;
}

function renderIdentity(id) {
  if (!id) return '';
  const rows = [
    ['Legal name', id.legalName],
    ['Trading names', (id.tradingNames || []).join(', ') || null],
    ['Parent group', id.parentGroup],
    ['Ultimate parent', id.ultimateParentGroup],
    ['Companies House', id.companiesHouseNo],
    ['SIC codes', (id.sicCodes || []).join(', ') || null],
    ['Registered address', id.registeredAddress],
    ['Headquarters', id.headquarters],
    ['Incorporated', id.incorporatedDate],
    ['Ownership', id.ownershipType],
    ['Listed exchange', id.listedExchange],
    ['Crown Representative', id.crownRepresentative ? 'Yes' : id.crownRepresentative === false ? 'No' : null],
    ['Strategic Supplier (Central)', id.strategicSupplierCentral ? 'Yes' : id.strategicSupplierCentral === false ? 'No' : null],
    ['Strategic Supplier (Local Gov)', id.strategicSupplierLocalGov ? 'Yes' : id.strategicSupplierLocalGov === false ? 'No' : null],
    ['Employees', id.employeeCount ? id.employeeCount.toLocaleString() : null],
  ].filter(([, v]) => v != null);

  return `
  <div class="section no-break">
    <div class="section-title">Identity</div>
    <table class="kf-table">
      ${rows.map(([label, val]) => `<tr><td style="width:200px;font-weight:600;">${esc(label)}</td><td>${esc(String(val))}</td></tr>`).join('\n      ')}
    </table>
  </div>`;
}

function renderServiceLineProfile(profile) {
  if (!profile || profile.length === 0) return '';
  return `
  <div class="section no-break">
    <div class="section-title">Service Line Profile</div>
    <table class="score-table">
      <tr><th>Service Line</th><th>Significance</th><th>Revenue</th><th>Trend</th><th>Contracts</th><th>Flagship Evidence</th></tr>
      ${profile.map(sl => `
      <tr>
        <td>${esc(sl.categoryId)}</td>
        <td><span class="significance-badge sig-${sl.significance || 'peripheral'}">${esc(sl.significance || '—')}</span></td>
        <td>${esc(sl.revenueIndicator || '—')}</td>
        <td>${esc(sl.trend || '—')}</td>
        <td style="text-align:center;">${sl.contractCount != null ? sl.contractCount : '—'}</td>
        <td>${esc(sl.flagshipEvidence || '—')}</td>
      </tr>`).join('')}
    </table>
  </div>`;
}

function renderFinancialTrajectory(ft) {
  if (!ft) return '';
  const curr = ft.currency || 'GBP';
  return `
  <div class="section page-break">
    <div class="section-title">Financial Trajectory</div>
    <div class="disclosure-badge">${esc(ft.disclosureLevel || 'unknown')}</div>
    <div class="section-text">${esc(ft.trajectoryNarrative || '')}</div>
    ${ft.years && ft.years.length > 0 ? `
    <table class="score-table">
      <tr><th>Period</th><th>Source</th><th class="num">Revenue</th><th class="num">Op. Profit</th><th class="num">Margin</th><th class="num">Order Intake</th><th class="num">Book/Bill</th><th class="num">Net Debt</th><th>Events</th></tr>
      ${ft.years.map(y => `
      <tr>
        <td>${esc(y.period)}</td>
        <td style="font-size:10px;">${esc(y.source || '—')}</td>
        <td class="num">${fmtCurrency(y.revenue, curr)}</td>
        <td class="num">${fmtCurrency(y.operatingProfit, curr)}</td>
        <td class="num">${fmtPct(y.operatingMargin)}</td>
        <td class="num">${fmtCurrency(y.orderIntake, curr)}</td>
        <td class="num">${y.bookToBill != null ? y.bookToBill.toFixed(2) : '—'}</td>
        <td class="num">${fmtCurrency(y.netDebt, curr)}</td>
        <td style="font-size:10px;">${(y.significantEvents || []).join('; ') || '—'}</td>
      </tr>`).join('')}
    </table>` : ''}
  </div>`;
}

function renderContracts(contracts) {
  if (!contracts || contracts.length === 0) return '';
  return `
  <div class="section page-break">
    <div class="section-title">Contract Portfolio</div>
    <table class="score-table">
      <tr><th>Title</th><th>Buyer</th><th>Sector</th><th>Service Lines</th><th>Importance</th><th class="num">Value</th><th>Status</th><th>End Date</th></tr>
      ${contracts.map(c => `
      <tr>
        <td>${esc(c.title)}</td>
        <td>${esc(c.buyer)}</td>
        <td>${esc(c.sector || '—')}</td>
        <td style="font-size:10px;">${(c.serviceLines || []).join(', ') || '—'}</td>
        <td><span class="significance-badge sig-${c.strategicImportance || 'peripheral'}">${esc(c.strategicImportance || '—')}</span></td>
        <td class="num">${fmtCurrency(c.value, 'GBP')}</td>
        <td>${esc(c.status || '—')}</td>
        <td>${fmtDate(c.endDate)}</td>
      </tr>
      ${c.businessContext ? `<tr><td colspan="8" style="font-size:10px;color:#576482;padding:2px 10px 8px;border-bottom:1px solid #E8EBF0;">${esc(c.businessContext)}</td></tr>` : ''}`).join('')}
    </table>
  </div>`;
}

function renderFrameworks(frameworks) {
  if (!frameworks || frameworks.length === 0) return '';
  return `
  <div class="section no-break">
    <div class="section-title">Frameworks</div>
    <table class="score-table">
      <tr><th>Name</th><th>Provider</th><th>Lots</th><th>Service Lines</th><th>Status</th><th>Position</th><th>Activity</th><th>Significance</th><th>End Date</th></tr>
      ${frameworks.map(f => `
      <tr>
        <td>${esc(f.name)}</td>
        <td>${esc(f.provider)}</td>
        <td style="font-size:10px;">${(f.lots || []).join(', ') || '—'}</td>
        <td style="font-size:10px;">${(f.serviceLines || []).join(', ') || '—'}</td>
        <td>${esc(f.status || '—')}</td>
        <td>${esc(f.supplierPosition || '—')}</td>
        <td>${esc(f.callOffActivity || '—')}</td>
        <td>${esc(f.significance || '—')}</td>
        <td>${fmtDate(f.endDate)}</td>
      </tr>`).join('')}
    </table>
  </div>`;
}

function renderLeadership(leadership) {
  if (!leadership || leadership.length === 0) return '';
  return `
  <div class="section no-break">
    <div class="section-title">Leadership</div>
    <table class="score-table">
      <tr><th>Name</th><th>Role</th><th>Function</th><th>Since</th><th>Background</th><th>Public Sector</th></tr>
      ${leadership.map(p => `
      <tr>
        <td>${esc(p.name)}</td>
        <td>${esc(p.role)}</td>
        <td>${esc(p.function || '—')}</td>
        <td>${fmtDate(p.startDate)}</td>
        <td style="font-size:10px;">${esc(p.background || '—')}</td>
        <td style="font-size:10px;">${esc(p.publicSectorBackground || '—')}</td>
      </tr>`).join('')}
    </table>
  </div>`;
}

function renderPartnerships(partnerships) {
  if (!partnerships || partnerships.length === 0) return '';
  return `
  <div class="section no-break">
    <div class="section-title">Partnerships</div>
    <table class="score-table">
      <tr><th>Partner</th><th>Type</th><th>Depth</th><th>Service Lines</th><th>Evidence</th></tr>
      ${partnerships.map(p => `
      <tr>
        <td>${esc(p.partnerName)}</td>
        <td>${esc(p.partnerType)}</td>
        <td>${esc(p.depth || '—')}</td>
        <td style="font-size:10px;">${(p.serviceLines || []).join(', ') || '—'}</td>
        <td style="font-size:10px;">${esc(p.evidence || '—')}</td>
      </tr>`).join('')}
    </table>
  </div>`;
}

function renderMarketVoice(mv) {
  if (!mv) return '';
  const verdictColour = { aligned: '#2D8A5E', partial: '#C68A1D', aspirational: '#576482', misleading: '#C15050' };
  return `
  <div class="section page-break">
    <div class="section-title">Market Voice Signals</div>
    <div class="section-headline" style="border-left-color:${verdictColour[mv.alignmentVerdict] || '#576482'}">
      Narrative-to-Reality Alignment: <strong>${esc(mv.alignmentVerdict)}</strong>
    </div>
    <div class="section-text">${esc(mv.verdictNarrative || '')}</div>
    ${mv.themes && mv.themes.length > 0 ? `
    <table class="score-table">
      <tr><th>Theme</th><th>Prominence</th><th>Evidence Alignment</th><th>Signal Type</th><th>Supporting</th><th>Contradicting</th></tr>
      ${mv.themes.map(t => `
      <tr>
        <td>${esc(t.theme)}</td>
        <td>${esc(t.prominence || '—')}</td>
        <td><span class="alignment-badge align-${t.evidenceAlignment}">${esc(t.evidenceAlignment || '—')}</span></td>
        <td style="font-size:10px;">${esc(t.signalType || '—')}</td>
        <td style="font-size:10px;">${esc(t.supportingEvidence || '—')}</td>
        <td style="font-size:10px;">${esc(t.contradictingEvidence || '—')}</td>
      </tr>`).join('')}
    </table>` : ''}
  </div>`;
}

function renderBidOutcomes(bo) {
  if (!bo) return '';
  return `
  <div class="section page-break">
    <div class="section-title">Bid Outcome Signals</div>
    <div style="font-size:11px;color:#576482;margin-bottom:12px;">Data window: ${esc(bo.dataWindow || '—')} | Awards observed: ${bo.totalAwardsObserved || 0} | Total value: ${fmtCurrency(bo.totalValueObserved, 'GBP')}</div>
    <div class="section-text">${esc(bo.summaryNarrative || '')}</div>
    ${bo.patterns && bo.patterns.length > 0 ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 8px;">Observed Patterns</div>
    ${bo.patterns.map(p => `
    <div class="pattern-item">
      <div class="pattern-type">${esc(p.patternType)}</div>
      <div>${esc(p.description)}</div>
      <div style="font-size:10px;color:#576482;margin-top:3px;">
        Rivals: ${(p.rivals || []).join(', ') || '—'} |
        Inference: <strong>${esc(p.inferenceLevel)}</strong> |
        Occurrences: ${p.occurrences || '—'} |
        Period: ${esc(p.dateRange || '—')}
      </div>
    </div>`).join('')}` : ''}
    ${bo.sectorConcentration && bo.sectorConcentration.length > 0 ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 8px;">Sector Concentration</div>
    <table class="score-table">
      <tr><th>Sector</th><th class="num">Awards</th><th class="num">Value</th><th>Trend</th></tr>
      ${bo.sectorConcentration.map(s => `
      <tr>
        <td>${esc(s.sector)}</td>
        <td class="num">${s.awardCount}</td>
        <td class="num">${fmtCurrency(s.totalValue, 'GBP')}</td>
        <td>${esc(s.trend || '—')}</td>
      </tr>`).join('')}
    </table>` : ''}
  </div>`;
}

function renderRiskExposure(re) {
  if (!re) return '';
  const levelColour = { high: '#C15050', moderate: '#C68A1D', low: '#2D8A5E', not_observed: '#818CA2' };
  return `
  <div class="section no-break">
    <div class="section-title">Risk & Exposure Profile</div>
    <div class="section-text">${esc(re.summaryNarrative || '')}</div>
    ${(re.factors || []).map(f => `
    <div class="risk-factor" style="border-left-color:${levelColour[f.level] || '#818CA2'}">
      <div class="risk-factor-header">
        <span class="risk-factor-name">${esc(f.factorName)}</span>
        <span class="risk-factor-level" style="color:${levelColour[f.level] || '#818CA2'}">${esc(f.level)}</span>
        ${claimBadge(f.claimType)}
      </div>
      <div style="font-size:11px;line-height:1.6;">${esc(f.narrative || '')}</div>
      ${f.keyEvidence ? `<div style="font-size:10px;color:#576482;margin-top:3px;">Key evidence: ${esc(f.keyEvidence)}</div>` : ''}
    </div>`).join('')}
  </div>`;
}

function renderSignalSynthesis(ss) {
  if (!ss) return '';
  const prioColour = { critical: '#C15050', watch: '#C68A1D', background: '#818CA2' };
  return `
  <div class="section no-break">
    <div class="section-title">Signal Synthesis</div>
    <div class="section-text">${esc(ss.summaryNarrative || '')}</div>
    <table class="signal-table">
      <tr><th>Priority</th><th>Signal</th><th>Source</th><th>Type</th><th>Trigger</th><th>Review By</th></tr>
      ${(ss.signals || []).map(s => `
      <tr>
        <td style="color:${prioColour[s.priority] || '#818CA2'};font-weight:700;text-transform:uppercase;font-size:10px;">${esc(s.priority)}</td>
        <td>${esc(s.signal)}</td>
        <td style="font-size:10px;">${esc(s.sourceSection || '—')}</td>
        <td>${claimBadge(s.claimType)}</td>
        <td style="font-size:10px;">${esc(s.triggerCondition || '—')}</td>
        <td>${fmtDate(s.reviewBy)}</td>
      </tr>`).join('')}
    </table>
  </div>`;
}

function renderEvidenceRegister(register) {
  if (!register || register.length === 0) return '';

  // Compute summary stats
  const tierCounts = [0, 0, 0, 0, 0, 0, 0];
  const typeCounts = {};
  let totalConf = 0;
  let contradictions = 0;
  register.forEach(e => {
    if (e.sourceTier >= 1 && e.sourceTier <= 6) tierCounts[e.sourceTier]++;
    typeCounts[e.claimType] = (typeCounts[e.claimType] || 0) + 1;
    totalConf += e.confidence || 0;
    if (e.contradictionFlag) contradictions++;
  });
  const avgConf = Math.round(totalConf / register.length);
  const maxTier = Math.max(...tierCounts.slice(1));

  const tierLabels = ['', 'T1 Official', 'T2 Policy', 'T3 Filings', 'T4 Company', 'T5 External', 'T6 Signals'];
  const tierColours = ['', '#2D8A5E', '#3A8CA0', '#5CA3B6', '#C68A1D', '#576482', '#818CA2'];

  return `
  <div class="section page-break">
    <div class="section-title">Evidence Quality</div>
    <div class="eq-grid">
      <div class="eq-card">
        <div class="eq-card-label">Total claims</div>
        <div class="eq-card-value">${register.length}</div>
      </div>
      <div class="eq-card">
        <div class="eq-card-label">Average confidence</div>
        <div class="eq-card-value">${avgConf}</div>
      </div>
      <div class="eq-card">
        <div class="eq-card-label">Contradictions</div>
        <div class="eq-card-value">${contradictions}</div>
      </div>
      <div class="eq-card">
        <div class="eq-card-label">Verified facts</div>
        <div class="eq-card-value">${typeCounts['verified_fact'] || 0}</div>
      </div>
    </div>

    <div style="margin-bottom:14px;">
      <div style="font-size:11px;font-weight:600;margin-bottom:8px;">Claims by source tier</div>
      ${[1,2,3,4,5,6].map(t => `
      <div class="eq-bar-row">
        <span class="eq-bar-label">${tierLabels[t]}</span>
        <div class="eq-bar-track"><div class="eq-bar-fill" style="width:${maxTier > 0 ? Math.round((tierCounts[t] / maxTier) * 100) : 0}%;background:${tierColours[t]};"></div></div>
        <span class="eq-bar-count">${tierCounts[t]}</span>
      </div>`).join('')}
    </div>

    <div style="margin-bottom:14px;">
      <div style="font-size:11px;font-weight:600;margin-bottom:8px;">Claims by type</div>
      ${['verified_fact', 'derived_estimate', 'analytical_hypothesis', 'signal_to_monitor'].map(ct => `
      <div class="eq-bar-row">
        <span class="eq-bar-label">${claimBadge(ct)}</span>
        <span class="eq-bar-count" style="margin-left:8px;">${typeCounts[ct] || 0}</span>
      </div>`).join('')}
    </div>
  </div>

  <div class="section no-break">
    <div class="section-title">Evidence Register</div>
    <table class="score-table" style="font-size:10px;">
      <tr><th>ID</th><th>Claim</th><th>Type</th><th>Field</th><th>Tier</th><th>Source</th><th class="num">Conf.</th></tr>
      ${register.map(e => `
      <tr${e.contradictionFlag ? ' style="background:rgba(193,80,80,0.06);"' : ''}>
        <td>${esc(e.claimId)}</td>
        <td>${esc(e.claimText)}</td>
        <td>${claimBadge(e.claimType)}</td>
        <td style="font-size:9px;color:#576482;">${esc(e.fieldPath || '—')}</td>
        <td style="text-align:center;">${e.sourceTier || '—'}</td>
        <td style="font-size:9px;">${esc(e.sourceName || '—')}</td>
        <td class="num">${e.confidence != null ? e.confidence : '—'}</td>
      </tr>`).join('')}
    </table>
  </div>`;
}

function renderRefreshGuidance(meta) {
  if (!meta || !meta.refreshDue) return '';
  const rows = Object.entries(meta.refreshDue).map(([section, date]) => {
    const windowMap = {
      contracts: '7 days', frameworks: '7 days', bidOutcomeSignals: '7 days',
      financialTrajectory: '90 days', marketVoiceSignals: '30 days',
      leadership: '60 days', partnerships: '60 days',
      riskExposureProfile: '30 days', serviceLineProfile: '30 days',
    };
    return `<tr><td>${esc(section)}</td><td>${fmtDate(date)}</td><td>${windowMap[section] || '—'}</td></tr>`;
  });
  return `
  <div class="section no-break">
    <div class="section-title">Refresh Guidance</div>
    <table class="kf-table">
      <tr><th>Section</th><th>Refresh Due</th><th>Window</th></tr>
      ${rows.join('\n      ')}
    </table>
  </div>`;
}

function renderVersionLog(meta) {
  if (!meta || !meta.versionLog || meta.versionLog.length === 0) return '';
  return `
  <div class="section no-break">
    <div class="section-title">Version History</div>
    <table class="kf-table">
      <tr><th>Version</th><th>Date</th><th>Changes</th></tr>
      ${meta.versionLog.map(v => `<tr><td>${esc(v.version)}</td><td>${fmtDate(v.date)}</td><td>${esc(v.summary)}</td></tr>`).join('\n      ')}
    </table>
  </div>`;
}

function renderLinkedAssets(la) {
  if (!la) return '';
  const sections = [
    ['Client profiles', la.clientProfiles],
    ['Sector briefs', la.sectorBriefs],
    ['Pipeline scans', la.pipelineScans],
  ].filter(([, arr]) => arr && arr.length > 0);
  if (sections.length === 0) return '';
  return `
  <div class="section no-break">
    <div class="section-title">Linked Library Assets</div>
    ${sections.map(([title, items]) => `
    <div style="font-size:11px;font-weight:600;margin-bottom:4px;">${esc(title)}</div>
    <ul class="gaps-list">${items.map(i => `<li>${esc(i)}</li>`).join('')}</ul>`).join('')}
  </div>`;
}

// ─── Assemble the full report ───────────────────────────────────────────────

const scores = data.scores || {};
const exec = data.executiveSummary || {};
const meta = data.meta || {};

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Supplier Intelligence Dossier — ${esc(meta.supplierName || 'Unknown')}</title>
<style>
  /* ── Reset & base ─────────────────────────────────────────── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    color: #021744;
    line-height: 1.65;
    font-size: 12px;
    padding: 0;
    max-width: 900px;
    margin: 0 auto;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  @page { size: A4; margin: 18mm; }
  @media print {
    body { padding: 0; }
    .page-break { page-break-before: always; }
    .no-break { page-break-inside: avoid; }
  }

  /* ── Cover ────────────────────────────────────────────────── */
  .cover {
    background: linear-gradient(135deg, #021744 0%, #0D2B5C 100%);
    padding: 40px 36px 32px;
    color: #F0EDE6;
  }
  .cover-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(240,237,230,0.45);
    margin-bottom: 6px;
  }
  .cover-title {
    font-family: 'Spline Sans', Inter, sans-serif;
    font-size: 28px;
    font-weight: 600;
    color: #F0EDE6;
    margin-bottom: 4px;
  }
  .cover-sub {
    font-size: 12px;
    color: rgba(240,237,230,0.55);
    margin-bottom: 24px;
  }
  .cover-scores {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
  .score-card {
    padding: 14px 16px;
    border: 1px solid rgba(240,237,230,0.15);
    background: rgba(240,237,230,0.04);
  }
  .score-card-label {
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(240,237,230,0.5);
    margin-bottom: 6px;
  }
  .score-card-rating {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
  }
  .score-card-rationale {
    font-size: 10px;
    color: rgba(240,237,230,0.6);
    line-height: 1.5;
  }
  .rag-red .score-card-rating { color: #E87070; }
  .rag-amber .score-card-rating { color: #D4A237; }
  .rag-green .score-card-rating { color: #6BC5A0; }
  .rag-grey .score-card-rating { color: #818CA2; }

  /* ── Body ─────────────────────────────────────────────────── */
  .report-body {
    padding: 28px 36px;
    border: 1px solid #D5D9E0;
    border-top: none;
  }

  /* ── Section ──────────────────────────────────────────────── */
  .section { margin-bottom: 28px; }
  .section-title {
    font-family: 'Spline Sans', Inter, sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: #021744;
    margin-bottom: 10px;
    padding-bottom: 7px;
    border-bottom: 1px solid #D5D9E0;
  }
  .section-headline {
    font-size: 13px;
    font-weight: 600;
    color: #0D2B5C;
    margin-bottom: 8px;
    padding: 8px 12px;
    background: rgba(92,163,182,0.06);
    border-left: 3px solid #5CA3B6;
  }
  .section-text {
    font-size: 12px;
    color: #021744;
    line-height: 1.75;
    margin-bottom: 12px;
    white-space: pre-line;
  }

  /* ── Executive summary ────────────────────────────────────── */
  .exec-headline {
    font-size: 14px;
    font-weight: 600;
    color: #021744;
    padding: 12px 14px;
    background: rgba(2,23,68,0.04);
    border-left: 3px solid #021744;
    margin-bottom: 14px;
    line-height: 1.55;
  }
  .exec-risks {
    margin: 12px 0;
    padding: 0;
    list-style: none;
  }
  .exec-risks li {
    font-size: 11px;
    padding: 4px 0 4px 16px;
    position: relative;
    color: #C15050;
  }
  .exec-risks li::before {
    content: '!';
    position: absolute;
    left: 0;
    font-weight: 700;
  }

  /* ── Score table ──────────────────────────────────────────── */
  .score-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    margin-bottom: 16px;
  }
  .score-table th {
    background: #021744;
    color: #F0EDE6;
    padding: 7px 10px;
    text-align: left;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
  }
  .score-table th.num { text-align: center; }
  .score-table td {
    padding: 6px 10px;
    border-bottom: 1px solid #E8EBF0;
    vertical-align: top;
  }
  .score-table td.num {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
  }

  /* ── Key facts table ──────────────────────────────────────── */
  .kf-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    margin: 10px 0 16px;
  }
  .kf-table th {
    background: rgba(2,23,68,0.06);
    padding: 5px 10px;
    text-align: left;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #576482;
    border-bottom: 1px solid #D5D9E0;
  }
  .kf-table td {
    padding: 5px 10px;
    border-bottom: 1px solid #E8EBF0;
  }

  /* ── Significance badges ──────────────────────────────────── */
  .significance-badge {
    display: inline-block;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 1px 6px;
    border-radius: 2px;
    text-transform: uppercase;
  }
  .sig-core { background: rgba(45,138,94,0.12); color: #2D8A5E; }
  .sig-significant { background: rgba(92,163,182,0.12); color: #3A8CA0; }
  .sig-supporting { background: rgba(198,138,29,0.12); color: #7C5A0A; }
  .sig-peripheral { background: rgba(129,140,162,0.12); color: #576482; }

  /* ── Alignment badges ─────────────────────────────────────── */
  .alignment-badge {
    display: inline-block;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 1px 6px;
    border-radius: 2px;
  }
  .align-supported { background: rgba(45,138,94,0.12); color: #2D8A5E; }
  .align-partially_supported { background: rgba(198,138,29,0.12); color: #7C5A0A; }
  .align-aspirational { background: rgba(129,140,162,0.12); color: #576482; }
  .align-contradicted { background: rgba(193,80,80,0.12); color: #C15050; }

  /* ── Disclosure badge ─────────────────────────────────────── */
  .disclosure-badge {
    display: inline-block;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 2px 8px;
    border-radius: 2px;
    background: rgba(2,23,68,0.06);
    color: #576482;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  /* ── Risk factor ──────────────────────────────────────────── */
  .risk-factor {
    padding: 10px 14px;
    margin-bottom: 8px;
    border-left: 3px solid #818CA2;
    background: rgba(2,23,68,0.02);
  }
  .risk-factor-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }
  .risk-factor-name {
    font-weight: 700;
    font-size: 12px;
  }
  .risk-factor-level {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  /* ── Pattern item ─────────────────────────────────────────── */
  .pattern-item {
    padding: 10px 14px;
    margin-bottom: 8px;
    border-left: 3px solid #5CA3B6;
    background: rgba(92,163,182,0.04);
    font-size: 12px;
    line-height: 1.6;
  }
  .pattern-type {
    font-weight: 700;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #576482;
    margin-bottom: 3px;
  }

  /* ── Signal table ─────────────────────────────────────────── */
  .signal-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    margin-bottom: 16px;
  }
  .signal-table th {
    background: #576482;
    color: white;
    padding: 6px 10px;
    text-align: left;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .signal-table td {
    padding: 6px 10px;
    border-bottom: 1px solid #E8EBF0;
    vertical-align: top;
  }

  /* ── Evidence quality ─────────────────────────────────────── */
  .eq-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }
  .eq-card {
    padding: 12px 14px;
    border: 1px solid #D5D9E0;
  }
  .eq-card-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #576482;
    margin-bottom: 4px;
  }
  .eq-card-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 500;
    color: #021744;
  }
  .eq-bar-row {
    display: flex;
    align-items: center;
    margin-bottom: 6px;
    font-size: 11px;
  }
  .eq-bar-label { width: 100px; color: #576482; }
  .eq-bar-track {
    flex: 1;
    height: 12px;
    background: #F0ECE4;
    margin: 0 8px;
    position: relative;
  }
  .eq-bar-fill { height: 100%; position: absolute; left: 0; top: 0; }
  .eq-bar-count { width: 30px; text-align: right; font-family: 'JetBrains Mono', monospace; font-weight: 600; }

  /* ── Gaps list ────────────────────────────────────────────── */
  .gaps-list {
    list-style: none;
    padding: 0;
    margin: 8px 0;
  }
  .gaps-list li {
    font-size: 11px;
    color: #576482;
    padding: 3px 0 3px 16px;
    position: relative;
  }
  .gaps-list li::before {
    content: '\\2192';
    position: absolute;
    left: 0;
    color: #5CA3B6;
  }

  /* ── Footer ───────────────────────────────────────────────── */
  .report-footer {
    margin-top: 32px;
    padding-top: 14px;
    border-top: 1px solid #D5D9E0;
    font-size: 10px;
    color: #818CA2;
    display: flex;
    justify-content: space-between;
  }
</style>
</head>
<body>

<!-- Cover -->
<div class="cover">
  <div class="cover-label">Supplier Intelligence Dossier</div>
  <div class="cover-title">${esc(meta.supplierName || 'Unknown Supplier')}</div>
  <div class="cover-sub">${esc(data.identity?.ownershipType || '')} | Generated ${esc(meta.generatedAt || '')} | v${esc(meta.version || '')} | Depth: ${esc(meta.depthMode || '')} | Taxonomy: v${esc(meta.taxonomyVersion || '')}</div>
  <div class="cover-scores">
    ${renderScoreCard('Sector Strength', scores.sectorStrength)}
    ${renderScoreCard('Scrutiny Exposure', scores.scrutinyExposure)}
    ${renderScoreCard('Strategic Identity', scores.strategicIdentityConfidence)}
    ${renderScoreCard('Supplier Breadth', scores.supplierBreadth)}
    ${renderScoreCard('Service Line Concentration', scores.serviceLineConcentration)}
    ${renderScoreCard('Evidence Quality', scores.evidenceQuality)}
  </div>
</div>

<div class="report-body">

  <!-- Executive Summary -->
  <div class="section no-break">
    <div class="section-title">Executive Summary</div>
    <div class="exec-headline">${esc(exec.headline || '')}</div>
    <div class="section-text">${esc(exec.overview || '')}</div>
    ${exec.keyRisks && exec.keyRisks.length > 0 ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 4px;">Key Risks</div>
    <ul class="exec-risks">${exec.keyRisks.map(r => `<li>${esc(r)}</li>`).join('')}</ul>` : ''}
  </div>

  ${renderIdentity(data.identity)}
  ${renderServiceLineProfile(data.serviceLineProfile)}
  ${renderFinancialTrajectory(data.financialTrajectory)}
  ${renderContracts(data.contracts)}
  ${renderFrameworks(data.frameworks)}
  ${renderLeadership(data.leadership)}
  ${renderPartnerships(data.partnerships)}
  ${renderMarketVoice(data.marketVoiceSignals)}
  ${renderBidOutcomes(data.bidOutcomeSignals)}
  ${renderRiskExposure(data.riskExposureProfile)}
  ${renderSignalSynthesis(data.signalSynthesis)}
  ${renderEvidenceRegister(data.evidenceRegister)}
  ${renderRefreshGuidance(meta)}
  ${renderVersionLog(meta)}
  ${renderLinkedAssets(data.linkedAssets)}

</div>

<div class="report-footer">
  <div>BidEquity Supplier Intelligence Dossier | ${esc(meta.supplierName || '')} | Generated ${esc(meta.generatedAt || '')}</div>
  <div>Confidential — BidEquity</div>
</div>

</body>
</html>`;

writeFileSync(outputPath, html, 'utf-8');
console.log(`Rendered: ${outputPath}`);
console.log(`  Supplier: ${meta.supplierName}`);
console.log(`  Scores: ${Object.entries(scores).map(([k, v]) => `${k}=${v.rating}`).join(', ')}`);
console.log(`  Evidence claims: ${(data.evidenceRegister || []).length}`);
console.log(`  Service lines: ${(data.serviceLineProfile || []).length}`);
console.log(`  Contracts: ${(data.contracts || []).length}`);
