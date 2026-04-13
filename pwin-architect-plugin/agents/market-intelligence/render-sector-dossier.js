#!/usr/bin/env node
/**
 * Sector Intelligence Dossier — JSON → HTML Renderer (v1)
 *
 * Reads a v1 sector intelligence JSON file and produces a printable HTML report.
 * Scores are AI-assessed (not computed) — the renderer just displays them.
 *
 * Usage:
 *   node render-sector-dossier.js <input.json> [output.html]
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';

const args = process.argv.slice(2);
if (args.length === 0 || args.includes('--help')) {
  console.log('Usage: node render-sector-dossier.js <data.json> [report.html]');
  process.exit(args.includes('--help') ? 0 : 1);
}

const inputPath = args[0];
const data = JSON.parse(readFileSync(inputPath, 'utf-8'));
const outputPath = args[1] || join(dirname(inputPath), 'report.html');

// ─── Helpers ────────────────────────────────────────────────────────────────

function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function ragDot(rating) {
  const c = { red: '#C15050', amber: '#C68A1D', green: '#2D8A5E', grey: '#818CA2' };
  return `<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:${c[rating] || c.grey};vertical-align:middle;margin-right:6px;"></span>`;
}

function typeBadge(type) {
  const styles = {
    fact: 'background:rgba(45,138,94,0.12);color:#2D8A5E',
    signal: 'background:rgba(92,163,182,0.12);color:#3A8CA0',
    inference: 'background:rgba(198,138,29,0.12);color:#7C5A0A',
    unknown: 'background:rgba(193,80,80,0.12);color:#C15050',
  };
  return `<span style="display:inline-block;font-size:9px;font-weight:700;padding:1px 6px;border-radius:2px;${styles[type] || styles.unknown}">${esc(type || 'unknown')}</span>`;
}

function confBadge(confidence) {
  const styles = {
    high: 'background:rgba(45,138,94,0.12);color:#2D8A5E',
    medium: 'background:rgba(198,138,29,0.12);color:#7C5A0A',
    low: 'background:rgba(193,80,80,0.12);color:#C15050',
  };
  return `<span style="display:inline-block;font-size:9px;font-weight:700;padding:1px 6px;border-radius:2px;${styles[confidence] || styles.low}">${esc(confidence || '?')}</span>`;
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

function renderEvidencedFieldArray(label, arr) {
  if (!arr?.length) return '';
  return `
    <div class="ef-array-label">${esc(label)}</div>
    ${arr.map(f => renderEvidencedField('', f)).join('')}`;
}

function renderScoreCard(name, score) {
  const s = score || { rating: 'grey', rationale: 'Not assessed' };
  return `
    <div class="score-card rag-${s.rating}">
      <div class="score-card-label">${esc(name)}</div>
      <div class="score-card-rating">${ragDot(s.rating)} ${esc({ red: 'Red', amber: 'Amber', green: 'Green', grey: 'Insufficient' }[s.rating] || 'Unknown')}</div>
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

function renderSectorIdentity(si) {
  if (!si) return '';
  return `
  <div class="section no-break">
    <div class="section-title">Sector Identity</div>
    ${si.inScopeDefinition ? `<div class="section-text"><strong>In scope:</strong> ${esc(si.inScopeDefinition)}</div>` : ''}
    ${si.outOfScopeDefinition ? `<div class="section-text"><strong>Out of scope:</strong> ${esc(si.outOfScopeDefinition)}</div>` : ''}
    ${si.subsectors?.length ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 6px;">Subsectors</div>
    <table class="data-table">
      <tr><th>Name</th><th>Description</th><th>Significance</th></tr>
      ${si.subsectors.map(s => `<tr><td><strong>${esc(s.name)}</strong></td><td>${esc(s.description || '—')}</td><td style="font-size:10px;">${esc(s.significance || '—')}</td></tr>`).join('')}
    </table>` : ''}
    ${si.jurisdictionNotes ? `<div class="section-text" style="font-size:11px;color:#576482;">${esc(si.jurisdictionNotes)}</div>` : ''}
  </div>`;
}

function renderSectorAnatomy(sa) {
  if (!sa) return '';
  return `
  <div class="section">
    <div class="section-title">Sector Anatomy ${sectionConfBadge(sa.sectionConfidence)}</div>
    ${renderEvidencedField('Formal Structure', sa.formalStructure)}
    ${renderEvidencedField('Commissioning Model', sa.commissioningModel)}
    ${renderEvidencedField('Delivery Model', sa.deliveryModel)}
    ${renderEvidencedField('Funding Flows', sa.fundingFlows)}
    ${sa.oversightBodies?.length ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 6px;">Oversight Bodies</div>
    <table class="data-table">
      <tr><th>Body</th><th>Role</th><th>Relevance</th></tr>
      ${sa.oversightBodies.map(b => `<tr><td>${esc(b.name)}</td><td>${esc(b.role || '—')}</td><td style="font-size:10px;">${esc(b.relevance || '—')}</td></tr>`).join('')}
    </table>` : ''}
    ${sa.regulators?.length ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 6px;">Regulators</div>
    <table class="data-table">
      <tr><th>Regulator</th><th>Scope</th><th>Procurement Impact</th></tr>
      ${sa.regulators.map(r => `<tr><td>${esc(r.name)}</td><td>${esc(r.scope || '—')}</td><td style="font-size:10px;">${esc(r.procurementImpact || '—')}</td></tr>`).join('')}
    </table>` : ''}
  </div>`;
}

function renderFinancialContext(fc) {
  if (!fc) return '';
  return `
  <div class="section page-break">
    <div class="section-title">Financial & Demand Context ${sectionConfBadge(fc.sectionConfidence)}</div>
    ${renderEvidencedField('Funding Sources', fc.fundingSources)}
    ${renderEvidencedField('Budget Cycle', fc.budgetCycle)}
    ${renderEvidencedField('Savings Targets', fc.savingsTargets)}
    ${renderEvidencedField('Demand Pressures', fc.demandPressures)}
    ${renderEvidencedField('Capital vs Revenue Bias', fc.capitalVsRevenueBias)}
    ${renderEvidencedField('Mandatory vs Discretionary Spend', fc.mandatoryVsDiscretionarySpend)}
    ${renderEvidencedField('Reform Dependency', fc.reformDependency)}
    ${renderEvidencedFieldArray('Financial Pressure Indicators', fc.financialPressureIndicators)}
  </div>`;
}

function renderProcurementBehaviour(pb) {
  if (!pb) return '';
  return `
  <div class="section page-break">
    <div class="section-title">Procurement Behaviour ${sectionConfBadge(pb.sectionConfidence)}</div>
    ${pb.summaryNarrative ? `<div class="section-text">${esc(pb.summaryNarrative)}</div>` : ''}
    ${pb.ftsDataSummary ? `
    <div class="eq-grid" style="grid-template-columns:repeat(3,1fr);">
      <div class="eq-card"><div class="eq-card-label">Total Awards</div><div class="eq-card-value">${pb.ftsDataSummary.totalAwards || '—'}</div></div>
      <div class="eq-card"><div class="eq-card-label">Total Value</div><div class="eq-card-value">${fmtCurrency(pb.ftsDataSummary.totalValue)}</div></div>
      <div class="eq-card"><div class="eq-card-label">Data Window</div><div class="eq-card-value" style="font-size:14px;">${esc(pb.ftsDataSummary.dataWindow || '—')}</div></div>
    </div>` : ''}
    ${pb.commonRoutesToMarket?.length ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 6px;">Common Routes to Market</div>
    <table class="data-table">
      <tr><th>Route</th><th>Prevalence</th><th>Context</th></tr>
      ${pb.commonRoutesToMarket.map(r => `<tr><td>${esc(r.route)}</td><td><span class="prev-${r.prevalence}">${esc(r.prevalence)}</span></td><td style="font-size:10px;">${esc(r.context || '—')}</td></tr>`).join('')}
    </table>` : ''}
    ${pb.frameworkUsagePatterns?.length ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 6px;">Framework Usage</div>
    <table class="data-table">
      <tr><th>Framework</th><th>Provider</th><th>Relevance</th><th>Renewal</th></tr>
      ${pb.frameworkUsagePatterns.map(f => `<tr><td>${esc(f.frameworkName)}</td><td>${esc(f.provider || '—')}</td><td>${esc(f.relevance || '—')}</td><td>${esc(f.renewalDate || '—')}</td></tr>`).join('')}
    </table>` : ''}
    ${renderEvidencedField('Dynamic Market Relevance', pb.dynamicMarketRelevance)}
    ${renderEvidencedField('Open Framework Relevance', pb.openFrameworkRelevance)}
    ${renderEvidencedField('Pre-Market Engagement Patterns', pb.preMarketEngagementPatterns)}
    ${renderEvidencedField('Procedure Selection Signals', pb.procedureSelectionSignals)}
    ${renderEvidencedField('Contract Packaging Patterns', pb.contractPackagingPatterns)}
    ${renderEvidencedField('Award Criteria Bias', pb.awardCriteriaBias)}
    ${renderEvidencedField('Transparency Signal Quality', pb.transparencySignalQuality)}
  </div>`;
}

function renderDemandDrivers(dd) {
  if (!dd) return '';
  const groups = [
    ['Policy Drivers', dd.policyDrivers],
    ['Statutory Change Drivers', dd.statutoryChangeDrivers],
    ['Service Backlog Drivers', dd.serviceBacklogDrivers],
    ['Workforce Drivers', dd.workforceDrivers],
    ['Digital Drivers', dd.digitalDrivers],
    ['Efficiency Drivers', dd.efficiencyDrivers],
    ['Compliance Drivers', dd.complianceDrivers],
  ].filter(([, arr]) => arr?.length);
  if (!groups.length) return '';
  return `
  <div class="section">
    <div class="section-title">Demand Drivers ${sectionConfBadge(dd.sectionConfidence)}</div>
    ${groups.map(([label, arr]) => renderEvidencedFieldArray(label, arr)).join('')}
  </div>`;
}

function renderBuyerArchetypes(archetypes) {
  if (!archetypes?.length) return '';
  return `
  <div class="section page-break">
    <div class="section-title">Buyer Archetypes</div>
    <div class="section-text" style="font-size:11px;color:#576482;">The engine room — calibrated to how real buyers in this sector actually behave.</div>
    ${archetypes.map(a => `
    <div class="archetype-card">
      <div class="archetype-header">
        <span class="archetype-name">${esc(a.archetypeName)}</span>
        <span style="font-size:10px;color:#818CA2;">${esc(a.archetypeId)}</span>
        ${confBadge(a.confidence)}
      </div>
      <div class="archetype-desc">${esc(a.description || '')}</div>
      ${a.typicalEntities?.length ? `<div class="archetype-row"><strong>Typical entities:</strong> ${a.typicalEntities.map(e => esc(e)).join(', ')}</div>` : ''}
      ${a.coreObjectives?.length ? `<div class="archetype-row"><strong>Core objectives:</strong> ${a.coreObjectives.map(e => esc(e)).join('; ')}</div>` : ''}
      ${a.budgetBehaviour ? `<div class="archetype-row"><strong>Budget:</strong> pressure ${esc(a.budgetBehaviour.pressureLevel || '—')}, discretionary ${esc(a.budgetBehaviour.discretionarySpendLikelihood || '—')}, business case bias ${esc(a.budgetBehaviour.businessCaseBias || '—')}</div>` : ''}
      ${a.procurementBehaviour ? `<div class="archetype-row"><strong>Procurement:</strong> framework ${esc(a.procurementBehaviour.frameworkPropensity || '—')}, competitive flexible ${esc(a.procurementBehaviour.competitiveFlexiblePropensity || '—')}, pre-market ${esc(a.procurementBehaviour.preMarketEngagementPropensity || '—')}</div>` : ''}
      ${a.evaluationBiases?.length ? `<div class="archetype-row"><strong>Evaluation biases:</strong> ${a.evaluationBiases.map(e => esc(e)).join(', ')}</div>` : ''}
      ${a.likelyWinThemes?.length ? `<div class="archetype-row" style="color:#2D8A5E;"><strong>Likely win themes:</strong> ${a.likelyWinThemes.map(e => esc(e)).join('; ')}</div>` : ''}
      ${a.likelyLossModes?.length ? `<div class="archetype-row" style="color:#C15050;"><strong>Likely loss modes:</strong> ${a.likelyLossModes.map(e => esc(e)).join('; ')}</div>` : ''}
    </div>`).join('')}
  </div>`;
}

function renderOpportunityArchetypes(archetypes) {
  if (!archetypes?.length) return '';
  return `
  <div class="section page-break">
    <div class="section-title">Opportunity Archetypes</div>
    <div class="section-text" style="font-size:11px;color:#576482;">Known opportunity patterns with predictable scope, routes, and qualification tests.</div>
    ${archetypes.map(a => `
    <div class="archetype-card">
      <div class="archetype-header">
        <span class="archetype-name">${esc(a.name)}</span>
        <span style="font-size:10px;color:#818CA2;">${esc(a.archetypeId)}</span>
      </div>
      ${a.typicalProblemStatements?.length ? `<div class="archetype-row"><strong>Problem statements:</strong> ${a.typicalProblemStatements.map(e => esc(e)).join('; ')}</div>` : ''}
      ${a.likelyContractShape ? `<div class="archetype-row"><strong>Shape:</strong> ${esc(a.likelyContractShape.valueBand || '—')}, ${esc(a.likelyContractShape.durationBand || '—')}, ${esc(a.likelyContractShape.serviceModel || '—')}</div>` : ''}
      ${a.likelyRouteToMarket?.length ? `<div class="archetype-row"><strong>Route:</strong> ${a.likelyRouteToMarket.map(e => esc(e)).join(', ')}</div>` : ''}
      ${a.likelyDecisionCriteria?.length ? `<div class="archetype-row"><strong>Decision criteria:</strong> ${a.likelyDecisionCriteria.map(e => esc(e)).join('; ')}</div>` : ''}
      ${a.criticalCredentials?.length ? `<div class="archetype-row"><strong>Critical credentials:</strong> ${a.criticalCredentials.map(e => esc(e)).join(', ')}</div>` : ''}
      ${a.qualificationTests?.length ? `<div class="archetype-row" style="color:#0D2B5C;"><strong>Qualification tests:</strong><ul style="margin:4px 0 0 20px;">${a.qualificationTests.map(e => `<li>${esc(e)}</li>`).join('')}</ul></div>` : ''}
    </div>`).join('')}
  </div>`;
}

function renderCompetitiveLandscape(cl) {
  if (!cl) return '';
  return `
  <div class="section">
    <div class="section-title">Competitive Landscape ${sectionConfBadge(cl.sectionConfidence)}</div>
    ${cl.summaryNarrative ? `<div class="section-text">${esc(cl.summaryNarrative)}</div>` : ''}
    ${cl.incumbentTypes?.length ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 6px;">Incumbent Types</div>
    <table class="data-table">
      <tr><th>Type</th><th>Typical Names</th><th>Service Lines</th><th>Entrenchment</th></tr>
      ${cl.incumbentTypes.map(i => `<tr><td>${esc(i.type)}</td><td style="font-size:10px;">${(i.typicalNames || []).join(', ')}</td><td style="font-size:10px;">${(i.serviceLines || []).join(', ')}</td><td>${esc(i.entrenchmentLevel || '—')}</td></tr>`).join('')}
    </table>` : ''}
    ${cl.platformLockInPatterns?.length ? `<div style="font-size:11px;font-weight:600;margin:10px 0 6px;">Platform Lock-in Patterns</div><ul class="bullet-list">${cl.platformLockInPatterns.map(p => `<li>${esc(p)}</li>`).join('')}</ul>` : ''}
    ${renderEvidencedField('SME vs SI Dynamics', cl.smeVsSiDynamics)}
    ${renderEvidencedField('Partnering Norms', cl.partneringNorms)}
    ${renderEvidencedField('Switching Barrier Patterns', cl.switchingBarrierPatterns)}
    ${cl.commonDifferentiators?.length ? `<div style="font-size:11px;font-weight:600;margin:10px 0 6px;color:#2D8A5E;">Common Differentiators</div><ul class="bullet-list">${cl.commonDifferentiators.map(d => `<li>${esc(d)}</li>`).join('')}</ul>` : ''}
    ${cl.commodityZones?.length ? `<div style="font-size:11px;font-weight:600;margin:10px 0 6px;color:#C68A1D;">Commodity Zones</div><ul class="bullet-list">${cl.commodityZones.map(d => `<li>${esc(d)}</li>`).join('')}</ul>` : ''}
  </div>`;
}

function renderWinImplications(wi) {
  if (!wi) return '';
  const listBlock = (label, arr, colour) => arr?.length ? `<div style="font-size:11px;font-weight:600;margin:10px 0 6px;${colour ? `color:${colour};` : ''}">${esc(label)}</div><ul class="bullet-list">${arr.map(i => `<li>${esc(i)}</li>`).join('')}</ul>` : '';
  return `
  <div class="section page-break">
    <div class="section-title">Win Implications ${sectionConfBadge(wi.sectionConfidence)}</div>
    <div class="section-text" style="font-size:11px;color:#576482;">The section the downstream agent consumes most heavily — the "so what" that turns sector intelligence into pursuit actions.</div>
    ${listBlock('Likely Win Themes', wi.likelyWinThemes, '#2D8A5E')}
    ${listBlock('Likely Discriminators', wi.likelyDiscriminators, '#2D8A5E')}
    ${listBlock('Likely Red Flags', wi.likelyRedFlags, '#C15050')}
    ${listBlock('Proof Points Buyers Trust', wi.proofPointsBuyersTrust)}
    ${listBlock('Message Angles That Resonate', wi.messageAnglesThatResonate)}
    ${listBlock('Commercial Positions to Avoid', wi.commercialPositionsToAvoid, '#C15050')}
    ${listBlock('Delivery Risks to Mitigate', wi.deliveryRisksToMitigate, '#C68A1D')}
    ${renderEvidencedField('Ideal Partnering Model', wi.idealPartneringModel)}
    ${listBlock('Qualification Implications', wi.qualificationImplications, '#0D2B5C')}
    ${listBlock('Go / No-Go Implications', wi.goNoGoImplications, '#0D2B5C')}
  </div>`;
}

function renderForwardSignalModel(fsm) {
  if (!fsm) return '';
  const impactColour = { accelerator: '#2D8A5E', blocker: '#C15050', modifier: '#C68A1D', neutral: '#818CA2' };
  const signalTable = (label, arr) => arr?.length ? `
    <div style="font-size:11px;font-weight:600;margin:10px 0 6px;">${esc(label)}</div>
    <table class="data-table">
      <tr><th>Signal</th><th>Type</th><th>Impact</th><th>Timing</th><th>Conf.</th></tr>
      ${arr.map(s => `<tr>
        <td>${esc(s.signal)}</td>
        <td>${typeBadge(s.type)}</td>
        <td style="color:${impactColour[s.pursuitImpact] || '#818CA2'};font-weight:600;font-size:10px;">${esc(s.pursuitImpact || '—')}</td>
        <td style="font-size:10px;">${esc(s.expectedTiming || '—')}</td>
        <td>${confBadge(s.confidence)}</td>
      </tr>`).join('')}
    </table>` : '';
  return `
  <div class="section">
    <div class="section-title">Forward Signal Model ${sectionConfBadge(fsm.sectionConfidence)}</div>
    ${signalTable('Leading Indicators', fsm.leadingIndicators)}
    ${signalTable('Notice Signals', fsm.noticeSignals)}
    ${signalTable('Budget Events', fsm.budgetEvents)}
    ${signalTable('Reform Milestones', fsm.reformMilestones)}
    ${signalTable('Framework Refreshes', fsm.frameworkRefreshes)}
    ${signalTable('Leadership Changes', fsm.leadershipChanges)}
    ${signalTable('Acceleration Signals', fsm.accelerationSignals)}
    ${signalTable('Delay Signals', fsm.delaySignals)}
  </div>`;
}

function renderPursuitHandoff(ph) {
  if (!ph) return '';
  return `
  <div class="section page-break pursuit-handoff">
    <div class="section-title" style="color:#F0EDE6;">Pursuit Handoff</div>
    <div class="section-text" style="color:rgba(240,237,230,0.75);font-size:11px;">Compact machine-readable summary consumed by the downstream qualification agent.</div>
    <div class="handoff-grid">
      ${ph.dominantBuyerArchetype ? `<div class="handoff-card"><div class="handoff-label">Dominant Buyer Archetype</div><div class="handoff-value">${esc(ph.dominantBuyerArchetype)}</div></div>` : ''}
      ${ph.confidence ? `<div class="handoff-card"><div class="handoff-label">Handoff Confidence</div><div class="handoff-value">${esc(ph.confidence)}</div></div>` : ''}
    </div>
    ${ph.scores ? `
    <div class="handoff-scores">
      ${['attractiveness', 'accessibility', 'contestability', 'scopeStability', 'budgetPressure'].map(k => ph.scores[k] ? `
      <div class="handoff-score-card rag-${ph.scores[k].rating}">
        <div class="handoff-score-label">${k.replace(/([A-Z])/g, ' $1').trim()}</div>
        <div class="handoff-score-rating">${ragDot(ph.scores[k].rating)} ${esc(ph.scores[k].rating || 'grey')}</div>
      </div>`: '').join('')}
    </div>` : ''}
    ${ph.preferredRoutesToMarket?.length ? `<div class="handoff-block"><strong>Preferred routes:</strong> ${ph.preferredRoutesToMarket.map(esc).join(', ')}</div>` : ''}
    ${ph.likelyWinThemes?.length ? `<div class="handoff-block"><strong>Likely win themes:</strong><ul style="margin:4px 0 0 20px;color:#F0EDE6;">${ph.likelyWinThemes.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>` : ''}
    ${ph.topWatchouts?.length ? `<div class="handoff-block"><strong>Top watchouts:</strong><ul style="margin:4px 0 0 20px;color:#F0EDE6;">${ph.topWatchouts.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>` : ''}
    ${ph.qualificationImplications?.length ? `<div class="handoff-block"><strong>Qualification implications:</strong><ul style="margin:4px 0 0 20px;color:#F0EDE6;">${ph.qualificationImplications.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>` : ''}
    ${ph.goNoGoImplications?.length ? `<div class="handoff-block"><strong>Go/no-go implications:</strong><ul style="margin:4px 0 0 20px;color:#F0EDE6;">${ph.goNoGoImplications.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>` : ''}
  </div>`;
}

function renderSourceRegister(er) {
  if (!er) return '';
  const sources = er.sources || [];
  const tierLabels = { tier1_official: 'T1 Official', tier2_procurement: 'T2 Procurement', tier3_secondary: 'T3 Secondary', tier4_internal: 'T4 Internal' };
  return `
  <div class="section page-break">
    <div class="section-title">Source Register & Unknowns</div>
    ${sources.length ? `
    <table class="data-table" style="font-size:10px;">
      <tr><th>ID</th><th>Source</th><th>Type</th><th>Reliability</th><th>Date</th></tr>
      ${sources.map(s => `<tr>
        <td style="font-weight:600;">${esc(s.sourceId)}</td>
        <td>${esc(s.sourceName)}${s.url ? ` <a href="${esc(s.url)}" style="color:#5CA3B6;font-size:9px;">link</a>` : ''}</td>
        <td style="font-size:9px;">${tierLabels[s.sourceType] || esc(s.sourceType)}</td>
        <td>${confBadge(s.reliability)}</td>
        <td>${esc(s.publicationDate || s.accessDate || '—')}</td>
      </tr>`).join('')}
    </table>` : ''}
    ${er.unknownsModel?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Unknowns Model</div>
    ${er.unknownsModel.map(u => `
    <div class="gap-item">
      <div><strong>${esc(u.unknown)}</strong> <span style="font-size:9px;color:#C15050;font-weight:700;text-transform:uppercase;">[${esc(u.impactIfWrong)}]</span></div>
      <div style="font-size:10px;color:#5CA3B6;">Reducing evidence: ${esc(u.reducingEvidence)}</div>
    </div>`).join('')}` : ''}
    ${er.gaps?.length ? `
    <div style="font-size:11px;font-weight:600;margin:14px 0 6px;">Intelligence Gaps</div>
    ${er.gaps.map(g => `
    <div class="gap-item">
      <div><strong>${esc(g.description)}</strong></div>
      <div style="font-size:10px;color:#576482;">Impact: ${esc(g.impact || '—')}</div>
      <div style="font-size:10px;color:#5CA3B6;">Action: ${esc(g.recommendedAction || '—')}</div>
    </div>`).join('')}` : ''}
  </div>`;
}

// ─── Assemble ───────────────────────────────────────────────────────────────

const meta = data.meta || {};
const scores = data.scores || {};

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sector Intelligence Dossier — ${esc(meta.sectorName || 'Unknown')}</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Inter, -apple-system, sans-serif; color: #021744; line-height: 1.65; font-size: 12px; max-width: 900px; margin: 0 auto; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  @page { size: A4; margin: 18mm; }
  @media print { body { padding: 0; } .page-break { page-break-before: always; } .no-break { page-break-inside: avoid; } }

  .cover { background: linear-gradient(135deg, #1a3a6e 0%, #2d5a8f 100%); padding: 40px 36px 32px; color: #F0EDE6; }
  .cover-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(240,237,230,0.45); margin-bottom: 6px; }
  .cover-title { font-family: 'Spline Sans', Inter, sans-serif; font-size: 28px; font-weight: 600; color: #F0EDE6; margin-bottom: 4px; }
  .cover-sub { font-size: 12px; color: rgba(240,237,230,0.55); margin-bottom: 24px; }
  .cover-scores { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
  .score-card { padding: 12px 14px; border: 1px solid rgba(240,237,230,0.15); background: rgba(240,237,230,0.04); }
  .score-card-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(240,237,230,0.5); margin-bottom: 6px; }
  .score-card-rating { font-size: 12px; font-weight: 600; margin-bottom: 4px; }
  .score-card-rationale { font-size: 10px; color: rgba(240,237,230,0.6); line-height: 1.4; }
  .rag-red .score-card-rating, .rag-red .handoff-score-rating { color: #E87070; }
  .rag-amber .score-card-rating, .rag-amber .handoff-score-rating { color: #D4A237; }
  .rag-green .score-card-rating, .rag-green .handoff-score-rating { color: #6BC5A0; }
  .rag-grey .score-card-rating, .rag-grey .handoff-score-rating { color: #818CA2; }

  .report-body { padding: 28px 36px; border: 1px solid #D5D9E0; border-top: none; }
  .section { margin-bottom: 28px; }
  .section-title { font-family: 'Spline Sans', Inter, sans-serif; font-size: 15px; font-weight: 600; color: #021744; margin-bottom: 10px; padding-bottom: 7px; border-bottom: 1px solid #D5D9E0; overflow: hidden; }
  .section-text { font-size: 12px; color: #021744; line-height: 1.75; margin-bottom: 12px; }

  .ef-row { padding: 8px 0; border-bottom: 1px solid #F0ECE4; }
  .ef-array-label { font-size: 11px; font-weight: 600; margin: 12px 0 4px; color: #0D2B5C; }
  .ef-label { font-size: 11px; font-weight: 600; color: #576482; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 3px; }
  .ef-value { font-size: 12px; color: #021744; line-height: 1.6; margin-bottom: 3px; }
  .ef-meta { display: flex; gap: 6px; align-items: center; }
  .ef-rationale { font-size: 10px; color: #818CA2; margin-top: 3px; font-style: italic; }

  .data-table { width: 100%; border-collapse: collapse; font-size: 11px; margin: 8px 0 16px; }
  .data-table th { background: #021744; color: #F0EDE6; padding: 7px 10px; text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }
  .data-table td { padding: 6px 10px; border-bottom: 1px solid #E8EBF0; vertical-align: top; }

  .eq-grid { display: grid; gap: 12px; margin-bottom: 16px; }
  .eq-card { padding: 12px 14px; border: 1px solid #D5D9E0; }
  .eq-card-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; color: #576482; margin-bottom: 4px; }
  .eq-card-value { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 500; color: #021744; }

  .archetype-card { padding: 12px 14px; margin-bottom: 10px; border: 1px solid #D5D9E0; border-left: 4px solid #5CA3B6; background: rgba(92,163,182,0.03); }
  .archetype-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
  .archetype-name { font-weight: 700; font-size: 13px; color: #021744; }
  .archetype-desc { font-size: 11px; color: #576482; margin-bottom: 6px; font-style: italic; }
  .archetype-row { font-size: 11px; color: #021744; margin-bottom: 3px; line-height: 1.6; }

  .prev-dominant { color: #2D8A5E; font-weight: 700; text-transform: uppercase; font-size: 10px; }
  .prev-common { color: #3A8CA0; font-weight: 600; text-transform: uppercase; font-size: 10px; }
  .prev-occasional { color: #C68A1D; font-weight: 600; text-transform: uppercase; font-size: 10px; }
  .prev-rare { color: #818CA2; font-weight: 600; text-transform: uppercase; font-size: 10px; }

  .bullet-list { list-style: none; padding: 0; margin: 4px 0 12px; }
  .bullet-list li { font-size: 11px; color: #021744; padding: 3px 0 3px 16px; position: relative; line-height: 1.6; }
  .bullet-list li::before { content: '\\2192'; position: absolute; left: 0; color: #5CA3B6; }

  .gap-item { padding: 8px 12px; margin-bottom: 6px; border-left: 3px solid #C68A1D; background: rgba(198,138,29,0.04); }

  .pursuit-handoff { background: linear-gradient(135deg, #0D2B5C 0%, #1a3a6e 100%); color: #F0EDE6; padding: 24px 28px; margin-bottom: 28px; }
  .pursuit-handoff .section-title { border-bottom-color: rgba(240,237,230,0.2); }
  .handoff-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px; }
  .handoff-card { padding: 10px 12px; background: rgba(240,237,230,0.05); border: 1px solid rgba(240,237,230,0.15); }
  .handoff-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(240,237,230,0.5); margin-bottom: 4px; }
  .handoff-value { font-size: 14px; font-weight: 600; }
  .handoff-scores { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 16px; }
  .handoff-score-card { padding: 8px 10px; background: rgba(240,237,230,0.05); border: 1px solid rgba(240,237,230,0.15); }
  .handoff-score-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.06em; color: rgba(240,237,230,0.5); margin-bottom: 4px; }
  .handoff-score-rating { font-size: 12px; font-weight: 600; }
  .handoff-block { margin-bottom: 10px; font-size: 12px; color: rgba(240,237,230,0.9); }

  .report-footer { margin-top: 32px; padding-top: 14px; border-top: 1px solid #D5D9E0; font-size: 10px; color: #818CA2; display: flex; justify-content: space-between; }
</style>
</head>
<body>

<div class="cover">
  <div class="cover-label">Sector Intelligence Dossier</div>
  <div class="cover-title">${esc(meta.sectorName || 'Unknown Sector')}</div>
  <div class="cover-sub">${esc(meta.jurisdiction || '')} | Generated ${esc(meta.generatedAt || '')} | v${esc(meta.version || '')} | Depth: ${esc(meta.depthMode || '')} | Confidence: ${esc(meta.overallConfidence || '—')}</div>
  <div class="cover-scores">
    ${renderScoreCard('Attractiveness', scores.sectorAttractiveness)}
    ${renderScoreCard('Urgency', scores.urgencyOfDemand)}
    ${renderScoreCard('Accessibility', scores.accessibilityOfBuyers)}
    ${renderScoreCard('Route Fit', scores.routeToMarketFit)}
    ${renderScoreCard('Overall Pursuit', scores.overallPursuitRelevance)}
  </div>
</div>

<div class="report-body">

  ${renderPursuitHandoff(data.pursuitHandoff)}
  ${renderSectorIdentity(data.sectorIdentity)}
  ${renderSectorAnatomy(data.sectorAnatomy)}
  ${renderFinancialContext(data.financialAndDemandContext)}
  ${renderProcurementBehaviour(data.procurementBehaviour)}
  ${renderDemandDrivers(data.demandDrivers)}
  ${renderBuyerArchetypes(data.buyerArchetypes)}
  ${renderOpportunityArchetypes(data.opportunityArchetypes)}
  ${renderCompetitiveLandscape(data.competitiveLandscape)}
  ${renderWinImplications(data.winImplications)}
  ${renderForwardSignalModel(data.forwardSignalModel)}
  ${renderSourceRegister(data.evidenceRegister)}

</div>

<div class="report-footer">
  <div>BidEquity Sector Intelligence Dossier | ${esc(meta.sectorName || '')} | Generated ${esc(meta.generatedAt || '')}</div>
  <div>Confidential — BidEquity</div>
</div>

</body>
</html>`;

writeFileSync(outputPath, html, 'utf-8');
console.log(`Rendered: ${outputPath}`);
console.log(`  Sector: ${meta.sectorName} (${meta.jurisdiction || 'UK'})`);
console.log(`  Confidence: ${meta.overallConfidence || 'not assessed'}`);
console.log(`  Buyer archetypes: ${(data.buyerArchetypes || []).length}`);
console.log(`  Opportunity archetypes: ${(data.opportunityArchetypes || []).length}`);
console.log(`  Sources: ${(data.evidenceRegister?.sources || []).length}`);
console.log(`  Pursuit handoff: ${data.pursuitHandoff ? 'populated' : 'MISSING'}`);
