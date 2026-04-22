/**
 * PWIN Platform — MCP Server (stdio transport)
 *
 * Exposes platform data as typed tool functions for Claude.
 * Read tools for analysis, write tools for AI write-back.
 * Field-level permission enforcement on all writes.
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { randomUUID } from 'node:crypto';
import * as store from './store.js';
import { validateAIWrite } from './permissions.js';
import * as compIntel from './competitive-intel.js';

function createMcpServer() {
  const server = new McpServer({
    name: 'pwin-platform',
    version: '0.1.0',
  });

  // ==========================================================================
  // SHARED READ TOOLS (Section 4.3)
  // ==========================================================================

  server.tool(
    'get_pursuit',
    'Get shared pursuit entity: client, opportunity, sector, TCV, type, status, dates',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getSharedEntity(pursuitId, 'pursuit');
      if (!data) return { content: [{ type: 'text', text: `Pursuit ${pursuitId} not found` }], isError: true };
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_pwin_score',
    'Get current PWIN score with category breakdown and weight profile',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getSharedEntity(pursuitId, 'pwinScore');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_pwin_score_history',
    'Get full PWIN score history: every assessment with date, source product, category scores',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const score = await store.getSharedEntity(pursuitId, 'pwinScore');
      const history = score?.history || [];
      return { content: [{ type: 'text', text: JSON.stringify(history, null, 2) }] };
    }
  );

  server.tool(
    'get_shared_win_themes',
    'Get win themes from shared data (locked by Win Strategy or refined by Bid Execution)',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getSharedEntity(pursuitId, 'winThemes');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_shared_stakeholder_map',
    'Get cross-product stakeholder map enriched by Qualify, Win Strategy, and Bid Execution',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getSharedEntity(pursuitId, 'stakeholderMap');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_shared_competitive_positioning',
    'Get competitors, intensity, incumbent vulnerability, differentiator',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getSharedEntity(pursuitId, 'competitivePositioning');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_shared_buyer_values',
    'Get buyer values with priority, evidence, linked win themes',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getSharedEntity(pursuitId, 'buyerValues');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_shared_client_intelligence',
    'Get client strategic priorities, pain points, SRO, spend history',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getSharedEntity(pursuitId, 'clientIntelligence');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_shared_capture_plan',
    'Get locked capture plan (if exists)',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getSharedEntity(pursuitId, 'capturePlan');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  // ==========================================================================
  // QUALIFY READ TOOLS (Section 4.2)
  // ==========================================================================

  server.tool(
    'get_qualification_assessment',
    'Get full assessment: all 24 positions, evidence, AI reviews, category scores, overall PWIN, completion %',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getProductData(pursuitId, 'qualify');
      if (!data) return { content: [{ type: 'text', text: `No Qualify data for pursuit ${pursuitId}` }] };
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_qualification_by_category',
    'Get questions, positions, evidence, AI reviews for one category',
    { pursuitId: z.string(), categoryId: z.enum(['cp', 'pi', 'ss', 'oi', 'vp', 'pp']) },
    async ({ pursuitId, categoryId }) => {
      const data = await store.getProductData(pursuitId, 'qualify');
      if (!data) return { content: [{ type: 'text', text: `No Qualify data for pursuit ${pursuitId}` }] };

      // Category index ranges: cp=0-3, pi=4-7, ss=8-11, oi=12-15, vp=16-19, pp=20-23
      const catMap = { cp: [0, 3], pi: [4, 7], ss: [8, 11], oi: [12, 15], vp: [16, 19], pp: [20, 23] };
      const [start, end] = catMap[categoryId];
      const result = { categoryId, positions: {}, evidence: {}, reviews: {} };
      for (let i = start; i <= end; i++) {
        if (data.positions?.[i] !== undefined) result.positions[i] = data.positions[i];
        if (data.evidence?.[i] !== undefined) result.evidence[i] = data.evidence[i];
        if (data.reviews?.[i] !== undefined) result.reviews[i] = data.reviews[i];
      }
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'get_qualification_context',
    'Get pursuit context fields from Qualify product',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getProductData(pursuitId, 'qualify');
      if (!data) return { content: [{ type: 'text', text: `No Qualify data for pursuit ${pursuitId}` }] };
      return { content: [{ type: 'text', text: JSON.stringify(data.context || {}, null, 2) }] };
    }
  );

  server.tool(
    'get_qualification_gaps',
    'Get questions scored Disagree or Strongly Disagree, plus unanswered questions',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getProductData(pursuitId, 'qualify');
      if (!data) return { content: [{ type: 'text', text: `No Qualify data for pursuit ${pursuitId}` }] };
      const gaps = [];
      for (let i = 0; i < 24; i++) {
        const score = data.positions?.[i];
        if (!score || score === '1' || score === '2') {
          gaps.push({ questionIndex: i, score: score || null, evidence: data.evidence?.[i] || null });
        }
      }
      return { content: [{ type: 'text', text: JSON.stringify(gaps, null, 2) }] };
    }
  );

  server.tool(
    'get_qualification_ai_reviews',
    'Get AI review results across all questions, optionally filtered by verdict or inflation',
    { pursuitId: z.string(), verdict: z.enum(['validated', 'queried', 'challenged']).optional(), inflationDetected: z.boolean().optional() },
    async ({ pursuitId, verdict, inflationDetected }) => {
      const data = await store.getProductData(pursuitId, 'qualify');
      if (!data) return { content: [{ type: 'text', text: `No Qualify data for pursuit ${pursuitId}` }] };
      let reviews = Object.entries(data.reviews || {}).map(([idx, r]) => ({ questionIndex: parseInt(idx), ...r }));
      if (verdict) reviews = reviews.filter(r => r.verdict === verdict);
      if (inflationDetected !== undefined) reviews = reviews.filter(r => r.inflationDetected === inflationDetected);
      return { content: [{ type: 'text', text: JSON.stringify(reviews, null, 2) }] };
    }
  );

  server.tool(
    'get_qualification_completeness',
    'Get completeness score per section and overall, with minimum-to-proceed thresholds',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await store.getProductData(pursuitId, 'qualify');
      if (!data) return { content: [{ type: 'text', text: `No Qualify data for pursuit ${pursuitId}` }] };

      const categories = ['cp', 'pi', 'ss', 'oi', 'vp', 'pp'];
      const catMap = { cp: [0, 3], pi: [4, 7], ss: [8, 11], oi: [12, 15], vp: [16, 19], pp: [20, 23] };
      const completeness = {};
      let totalAnswered = 0;
      for (const cat of categories) {
        const [start, end] = catMap[cat];
        let answered = 0;
        for (let i = start; i <= end; i++) {
          if (data.positions?.[i]) answered++;
        }
        totalAnswered += answered;
        completeness[cat] = { answered, total: 4, pct: Math.round((answered / 4) * 100) };
      }
      return {
        content: [{ type: 'text', text: JSON.stringify({
          overall: { answered: totalAnswered, total: 24, pct: Math.round((totalAnswered / 24) * 100) },
          categories: completeness,
          minimumToProceed: 60,
        }, null, 2) }],
      };
    }
  );

  // ==========================================================================
  // PLATFORM READ TOOLS (Section 4.4)
  // ==========================================================================

  server.tool(
    'get_sector_knowledge',
    'Get sector enrichment prompt block for sector-calibrated analysis',
    { sector: z.string() },
    async ({ sector }) => {
      const data = await store.getPlatformData('sector_knowledge.json');
      const block = data?.[sector] || null;
      return { content: [{ type: 'text', text: JSON.stringify(block, null, 2) }] };
    }
  );

  server.tool(
    'get_opportunity_type_knowledge',
    'Get opportunity type prompt block',
    { opportunityType: z.string() },
    async ({ opportunityType }) => {
      const data = await store.getPlatformData('opportunity_types.json');
      const block = data?.[opportunityType] || null;
      return { content: [{ type: 'text', text: JSON.stringify(block, null, 2) }] };
    }
  );

  server.tool(
    'get_reasoning_rules',
    'Get business rules for PWIN scoring and gate readiness, optionally filtered by category',
    { category: z.string().optional() },
    async ({ category }) => {
      const data = await store.getPlatformData('reasoning_rules.json');
      if (!data) return { content: [{ type: 'text', text: '[]' }] };
      let rules = Array.isArray(data) ? data : [];
      if (category) rules = rules.filter(r => r.category.toLowerCase().replace(/[& ]/g, '_') === category.toLowerCase().replace(/[& ]/g, '_'));
      return { content: [{ type: 'text', text: JSON.stringify(rules, null, 2) }] };
    }
  );

  server.tool(
    'get_confidence_model',
    'Get confidence rating definitions (H/M/L/U) and completeness thresholds',
    {},
    async () => {
      const data = await store.getPlatformData('confidence_model.json');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_data_points',
    'Get the 51 intelligence data point definitions with sources and confidence rules',
    { section: z.string().optional() },
    async ({ section }) => {
      const data = await store.getPlatformData('data_points.json');
      if (!data) return { content: [{ type: 'text', text: '[]' }] };
      let points = Array.isArray(data) ? data : [];
      if (section) points = points.filter(p => p.section.toLowerCase().includes(section.toLowerCase()));
      return { content: [{ type: 'text', text: JSON.stringify(points, null, 2) }] };
    }
  );

  server.tool(
    'get_few_shot_examples',
    'Get AI calibration few-shot examples (evidence input → ideal AI review)',
    {},
    async () => {
      const data = await store.getPlatformData('few_shot_examples.json');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_output_schema',
    'Get AI output schema field definitions (current + proposed)',
    {},
    async () => {
      const data = await store.getPlatformData('output_schema.json');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_system_prompt',
    'Get the core system prompt sections (persona, scepticism, scoring, tone, challenge/capture standards)',
    {},
    async () => {
      const data = await store.getPlatformData('system_prompt.json');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_source_hierarchy',
    'Get source priority hierarchy for intelligence data gathering',
    {},
    async () => {
      const data = await store.getPlatformData('source_hierarchy.json');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_success_factors',
    'Get the 12 success factors for AI system validation',
    {},
    async () => {
      const data = await store.getPlatformData('success_factors.json');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_sector_opp_matrix',
    'Get intersection intelligence for a sector × opportunity type combination',
    { sector: z.string().optional(), opportunityType: z.string().optional() },
    async ({ sector, opportunityType }) => {
      const data = await store.getPlatformData('sector_opp_matrix.json');
      if (!data) return { content: [{ type: 'text', text: '[]' }] };
      let entries = Array.isArray(data) ? data : [];
      if (sector) entries = entries.filter(e => e.sector.toLowerCase().includes(sector.toLowerCase()));
      if (opportunityType) entries = entries.filter(e => e.opportunityType.toLowerCase().includes(opportunityType.toLowerCase()));
      return { content: [{ type: 'text', text: JSON.stringify(entries, null, 2) }] };
    }
  );

  // ==========================================================================
  // GOVERNANCE KNOWLEDGE TOOLS
  // ==========================================================================

  server.tool(
    'get_governance_gates',
    'Get gate definitions with tier mapping, prerequisites, and outcomes. Optionally filter by tier or gate number.',
    { tier: z.enum(['qualification', 'solution', 'submission', 'contract']).optional(), gateNumber: z.number().optional() },
    async ({ tier, gateNumber }) => {
      const data = await store.getPlatformData('governance/governance_gate_definitions.json');
      if (!data) return { content: [{ type: 'text', text: 'null' }] };
      let result = { tier_definitions: data.tier_definitions, ic_trigger_criteria: data.ic_trigger_criteria, no_bid_criteria: data.no_bid_criteria };
      let gates = data.gates || [];
      if (tier) gates = gates.filter(g => g.tier === tier);
      if (gateNumber !== undefined) gates = gates.filter(g => g.gate_number === gateNumber);
      result.gates = gates;
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'get_governance_pack_template',
    'Get governance pack section structure for a given gate tier (qualification, solution, submission, contract)',
    { tier: z.enum(['qualification', 'solution', 'submission', 'contract']) },
    async ({ tier }) => {
      const data = await store.getPlatformData('governance/governance_pack_templates.json');
      const template = data?.[tier] || null;
      return { content: [{ type: 'text', text: JSON.stringify(template, null, 2) }] };
    }
  );

  server.tool(
    'get_governance_risk_framework',
    'Get risk tornado format, probability weightings, standard risk categories, and RAG definitions',
    {},
    async () => {
      const data = await store.getPlatformData('governance/governance_risk_framework.json');
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_governance_signoff_matrix',
    'Get functional sign-off areas, role titles, accountabilities, and gate tier requirements',
    { tier: z.enum(['qualification', 'solution', 'submission', 'contract']).optional() },
    async ({ tier }) => {
      const data = await store.getPlatformData('governance/governance_signoff_matrix.json');
      if (!data) return { content: [{ type: 'text', text: 'null' }] };
      let result = { ...data };
      if (tier) {
        result.functional_areas = data.functional_areas.filter(a =>
          !a.required_at_tiers || a.required_at_tiers.includes(tier)
        );
      }
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  // ==========================================================================
  // BID EXECUTION READ TOOLS — first 10 (Section 4.1, Steps 4)
  // ==========================================================================

  // Helper: read bid execution data and return a field or filtered subset
  async function readBidExec(pursuitId) {
    return await store.getProductData(pursuitId, 'bid_execution');
  }

  server.tool(
    'get_activities_due_within',
    'Get activities due within N days',
    { pursuitId: z.string(), days: z.number() },
    async ({ pursuitId, days }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.activities) return { content: [{ type: 'text', text: '[]' }] };
      const cutoff = new Date(Date.now() + days * 86400000).toISOString();
      const due = data.activities.filter(a => a.plannedEnd && a.plannedEnd <= cutoff && a.status !== 'completed');
      return { content: [{ type: 'text', text: JSON.stringify(due, null, 2) }] };
    }
  );

  server.tool(
    'get_critical_path',
    'Get critical path activities',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.activities) return { content: [{ type: 'text', text: '[]' }] };
      const critical = data.activities.filter(a => a.criticalPath);
      return { content: [{ type: 'text', text: JSON.stringify(critical, null, 2) }] };
    }
  );

  server.tool(
    'get_activities_by_workstream',
    'Get all activities for a given workstream code',
    { pursuitId: z.string(), workstreamCode: z.string() },
    async ({ pursuitId, workstreamCode }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.activities) return { content: [{ type: 'text', text: '[]' }] };
      const filtered = data.activities.filter(a => a.workstreamCode === workstreamCode);
      return { content: [{ type: 'text', text: JSON.stringify(filtered, null, 2) }] };
    }
  );

  server.tool(
    'get_activity',
    'Get a single activity by activity code',
    { pursuitId: z.string(), activityCode: z.string() },
    async ({ pursuitId, activityCode }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.activities) return { content: [{ type: 'text', text: `Activity ${activityCode} not found` }], isError: true };
      const activity = data.activities.find(a => a.activityCode === activityCode);
      if (!activity) return { content: [{ type: 'text', text: `Activity ${activityCode} not found` }], isError: true };
      return { content: [{ type: 'text', text: JSON.stringify(activity, null, 2) }] };
    }
  );

  server.tool(
    'get_dependencies',
    'Get dependency chain for an activity',
    { pursuitId: z.string(), activityCode: z.string() },
    async ({ pursuitId, activityCode }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.activities) return { content: [{ type: 'text', text: '[]' }] };
      const activity = data.activities.find(a => a.activityCode === activityCode);
      if (!activity) return { content: [{ type: 'text', text: `Activity ${activityCode} not found` }], isError: true };
      const deps = (activity.dependencies || []).map(depCode =>
        data.activities.find(a => a.activityCode === depCode) || { activityCode: depCode, missing: true }
      );
      return { content: [{ type: 'text', text: JSON.stringify({ activity: activityCode, dependencies: deps }, null, 2) }] };
    }
  );

  server.tool(
    'get_workstream_summary',
    'Get summary of all workstreams with activity counts and status breakdown',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.activities) return { content: [{ type: 'text', text: '{}' }] };
      const summary = {};
      for (const a of data.activities) {
        const ws = a.workstreamCode || 'unassigned';
        if (!summary[ws]) summary[ws] = { total: 0, byStatus: {} };
        summary[ws].total++;
        summary[ws].byStatus[a.status || 'unknown'] = (summary[ws].byStatus[a.status || 'unknown'] || 0) + 1;
      }
      return { content: [{ type: 'text', text: JSON.stringify(summary, null, 2) }] };
    }
  );

  server.tool(
    'get_response_sections',
    'Get response sections with optional filters',
    {
      pursuitId: z.string(),
      evaluationCategory: z.string().optional(),
      responseType: z.string().optional(),
      sectionNumber: z.string().optional(),
      hasLinkedResponseItem: z.boolean().optional(),
      limit: z.number().optional(),
      offset: z.number().optional(),
    },
    async ({ pursuitId, evaluationCategory, responseType, sectionNumber, hasLinkedResponseItem, limit, offset }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.responseSections) return { content: [{ type: 'text', text: '[]' }] };
      let sections = data.responseSections;
      if (evaluationCategory) sections = sections.filter(s => s.evaluationCategory === evaluationCategory);
      if (responseType) sections = sections.filter(s => s.responseType === responseType);
      if (sectionNumber) sections = sections.filter(s => s.sectionNumber === sectionNumber);
      if (hasLinkedResponseItem !== undefined) sections = sections.filter(s => hasLinkedResponseItem ? s.linkedResponseItem : !s.linkedResponseItem);
      if (offset) sections = sections.slice(offset);
      if (limit) sections = sections.slice(0, limit);
      return { content: [{ type: 'text', text: JSON.stringify(sections, null, 2) }] };
    }
  );

  server.tool(
    'get_response_section',
    'Get a single response section by reference',
    { pursuitId: z.string(), reference: z.string() },
    async ({ pursuitId, reference }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.responseSections) return { content: [{ type: 'text', text: `Section ${reference} not found` }], isError: true };
      const section = data.responseSections.find(s => s.reference === reference);
      if (!section) return { content: [{ type: 'text', text: `Section ${reference} not found` }], isError: true };
      return { content: [{ type: 'text', text: JSON.stringify(section, null, 2) }] };
    }
  );

  server.tool(
    'get_evaluation_framework',
    'Get the evaluation framework for a pursuit',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.evaluationFramework || null, null, 2) }] };
    }
  );

  server.tool(
    'get_coverage_summary',
    'Get ITT coverage summary: sections mapped vs unmapped, evaluation weight coverage',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.responseSections) return { content: [{ type: 'text', text: '{}' }] };
      const total = data.responseSections.length;
      const linked = data.responseSections.filter(s => s.linkedResponseItem).length;
      return {
        content: [{ type: 'text', text: JSON.stringify({
          totalSections: total,
          linkedToResponseItem: linked,
          unlinked: total - linked,
          coveragePct: total > 0 ? Math.round((linked / total) * 100) : 0,
        }, null, 2) }],
      };
    }
  );

  // ==========================================================================
  // SHARED WRITE TOOLS (Section 5.3)
  // ==========================================================================

  server.tool(
    'update_shared_win_themes',
    'Update win themes in shared data — source product tagged automatically',
    { pursuitId: z.string(), themes: z.array(z.object({
      id: z.string().optional(),
      statement: z.string(),
      rationale: z.string().optional(),
      evidenceStatus: z.enum(['substantiated', 'partial', 'unsubstantiated']).optional(),
      linkedCredentials: z.array(z.string()).optional(),
      competitiveDifferentiation: z.string().optional(),
      buyerValueAlignment: z.string().optional(),
      status: z.enum(['draft', 'confirmed', 'revised', 'locked']).optional(),
    })) },
    async ({ pursuitId, themes }) => {
      const tagged = themes.map(t => ({ ...t, id: t.id || randomUUID(), sourceProduct: 'ai', createdAt: t.createdAt || new Date().toISOString() }));
      await store.updateSharedEntity(pursuitId, 'winThemes', tagged);
      return { content: [{ type: 'text', text: JSON.stringify({ updated: tagged.length }, null, 2) }] };
    }
  );

  server.tool(
    'update_shared_stakeholder_map',
    'Update stakeholder map in shared data',
    { pursuitId: z.string(), stakeholders: z.array(z.object({
      name: z.string(),
      role: z.string().optional(),
      influenceLevel: z.enum(['decision_maker', 'influencer', 'evaluator', 'gatekeeper']).optional(),
      disposition: z.enum(['champion', 'supportive', 'neutral', 'unsupportive', 'unknown']).optional(),
      bipRelationshipOwner: z.string().optional(),
      lastContactDate: z.string().optional(),
      notes: z.string().optional(),
      confidence: z.enum(['H', 'M', 'L', 'U']).optional(),
    })) },
    async ({ pursuitId, stakeholders }) => {
      await store.updateSharedEntity(pursuitId, 'stakeholderMap', stakeholders);
      return { content: [{ type: 'text', text: JSON.stringify({ updated: stakeholders.length }, null, 2) }] };
    }
  );

  server.tool(
    'update_shared_competitive_positioning',
    'Update competitive positioning in shared data',
    { pursuitId: z.string(), positioning: z.object({
      competitors: z.array(z.object({
        name: z.string(),
        category: z.enum(['incumbent', 'contender', 'dark_horse', 'opportunist']).optional(),
        strengths: z.array(z.string()).optional(),
        weaknesses: z.array(z.string()).optional(),
        likelyStrategy: z.string().optional(),
        counterStrategy: z.string().optional(),
        ghostThemes: z.array(z.string()).optional(),
        pricePositioning: z.string().optional(),
        confidence: z.enum(['H', 'M', 'L', 'U']).optional(),
      })).optional(),
      competitiveIntensity: z.enum(['low', 'medium', 'high']).optional(),
      incumbentVulnerability: z.enum(['low', 'medium', 'high']).optional(),
      bipDifferentiator: z.string().optional(),
    }) },
    async ({ pursuitId, positioning }) => {
      const data = { ...positioning, updatedAt: new Date().toISOString() };
      await store.updateSharedEntity(pursuitId, 'competitivePositioning', data);
      return { content: [{ type: 'text', text: JSON.stringify({ updated: true }, null, 2) }] };
    }
  );

  server.tool(
    'update_shared_buyer_values',
    'Update buyer values in shared data',
    { pursuitId: z.string(), values: z.array(z.object({
      value: z.string(),
      priority: z.enum(['primary', 'secondary', 'tertiary']).optional(),
      evidence: z.string().optional(),
      linkedWinThemeIds: z.array(z.string()).optional(),
      confidence: z.enum(['H', 'M', 'L', 'U']).optional(),
    })) },
    async ({ pursuitId, values }) => {
      await store.updateSharedEntity(pursuitId, 'buyerValues', values);
      return { content: [{ type: 'text', text: JSON.stringify({ updated: values.length }, null, 2) }] };
    }
  );

  server.tool(
    'update_shared_client_intelligence',
    'Update client intelligence in shared data',
    { pursuitId: z.string(), intel: z.object({
      strategicPriorities: z.array(z.string()).optional(),
      knownPainPoints: z.array(z.string()).optional(),
      procurementDriver: z.string().optional(),
      sroName: z.string().optional(),
      sroBackground: z.string().optional(),
      spendHistory: z.array(z.object({ supplier: z.string(), value: z.number(), date: z.string().optional(), scope: z.string().optional() })).optional(),
      confidence: z.enum(['H', 'M', 'L', 'U']).optional(),
    }) },
    async ({ pursuitId, intel }) => {
      const data = { ...intel, updatedAt: new Date().toISOString() };
      await store.updateSharedEntity(pursuitId, 'clientIntelligence', data);
      return { content: [{ type: 'text', text: JSON.stringify({ updated: true }, null, 2) }] };
    }
  );

  server.tool(
    'lock_capture_plan',
    'Write and lock capture plan — once locked, cannot be modified without explicit unlock',
    { pursuitId: z.string(), plan: z.object({
      strategyNarrative: z.string().optional(),
      consortiumStrategy: z.string().optional(),
      pricingStrategy: z.string().optional(),
      clarificationStrategy: z.string().optional(),
      lockedBy: z.enum(['win_strategy', 'bid_execution']).optional(),
    }) },
    async ({ pursuitId, plan }) => {
      const existing = await store.getSharedEntity(pursuitId, 'capturePlan');
      if (existing?.status === 'locked') {
        return { content: [{ type: 'text', text: 'Capture plan is already locked. Bid manager must unlock before modification.' }], isError: true };
      }
      const data = { ...plan, status: 'locked', lockedAt: new Date().toISOString(), lockedBy: plan.lockedBy || 'win_strategy' };
      await store.updateSharedEntity(pursuitId, 'capturePlan', data);
      return { content: [{ type: 'text', text: JSON.stringify({ locked: true }, null, 2) }] };
    }
  );

  // ==========================================================================
  // QUALIFY WRITE TOOLS (Section 5.2)
  // ==========================================================================

  server.tool(
    'save_qualification_review',
    'Write AI assurance review result for one question',
    { pursuitId: z.string(), questionIdx: z.number(), review: z.object({
      verdict: z.enum(['validated', 'queried', 'challenged']),
      suggestedScore: z.string().optional(),
      confidenceLevel: z.enum(['H', 'M', 'L', 'U']).optional(),
      narrative: z.string().optional(),
      inflationDetected: z.boolean().optional(),
      inflationReason: z.string().optional(),
      challengeQuestions: z.array(z.string()).optional(),
      captureActions: z.array(z.string()).optional(),
      sectorContext: z.string().optional(),
      opportunityRisk: z.string().optional(),
      incumbentRiskAssessment: z.string().optional(),
      evidenceGaps: z.array(z.string()).optional(),
      stageCalibration: z.string().optional(),
    }) },
    async ({ pursuitId, questionIdx, review }) => {
      const data = await store.getProductData(pursuitId, 'qualify') || { positions: {}, evidence: {}, reviews: {}, context: {} };
      data.reviews = data.reviews || {};
      data.reviews[questionIdx] = { ...review, generatedAt: new Date().toISOString() };
      await store.saveProductData(pursuitId, 'qualify', data);
      return { content: [{ type: 'text', text: JSON.stringify({ saved: true, questionIdx }, null, 2) }] };
    }
  );

  server.tool(
    'batch_save_qualification_reviews',
    'Write AI reviews for all 24 questions in a single pass',
    { pursuitId: z.string(), reviews: z.array(z.object({
      questionIdx: z.number(),
      verdict: z.enum(['validated', 'queried', 'challenged']),
      suggestedScore: z.string().optional(),
      confidenceLevel: z.enum(['H', 'M', 'L', 'U']).optional(),
      narrative: z.string().optional(),
      inflationDetected: z.boolean().optional(),
      inflationReason: z.string().optional(),
      challengeQuestions: z.array(z.string()).optional(),
      captureActions: z.array(z.string()).optional(),
      evidenceGaps: z.array(z.string()).optional(),
    })) },
    async ({ pursuitId, reviews }) => {
      const data = await store.getProductData(pursuitId, 'qualify') || { positions: {}, evidence: {}, reviews: {}, context: {} };
      data.reviews = data.reviews || {};
      const now = new Date().toISOString();
      for (const r of reviews) {
        const { questionIdx, ...rest } = r;
        data.reviews[questionIdx] = { ...rest, generatedAt: now };
      }
      await store.saveProductData(pursuitId, 'qualify', data);
      return { content: [{ type: 'text', text: JSON.stringify({ saved: reviews.length }, null, 2) }] };
    }
  );

  server.tool(
    'update_qualification_pwin',
    'Recalculate and write PWIN score to qualify.json AND shared.json',
    { pursuitId: z.string(), scores: z.object({
      competitivePositioning: z.number(),
      procurementIntelligence: z.number(),
      stakeholderStrength: z.number(),
      organisationalInfluence: z.number(),
      valueProposition: z.number(),
      pursuitProgress: z.number(),
    }) },
    async ({ pursuitId, scores }) => {
      const overall = Math.round(Object.values(scores).reduce((a, b) => a + b, 0) / 6);
      const now = new Date().toISOString();

      // Update qualify.json
      const data = await store.getProductData(pursuitId, 'qualify') || {};
      data.pwinScore = { overall, categoryScores: scores, updatedAt: now };
      await store.saveProductData(pursuitId, 'qualify', data);

      // Update shared.json PWIN score + append history
      const existing = await store.getSharedEntity(pursuitId, 'pwinScore') || { history: [] };
      const pwinScore = {
        overall,
        categoryScores: scores,
        weightProfile: existing.weightProfile || 'default',
        assessmentDate: now,
        source: 'qualify',
        completionPct: data.completenessScore || null,
        history: [...(existing.history || []), { overall, date: now, source: 'qualify' }],
      };
      await store.updateSharedEntity(pursuitId, 'pwinScore', pwinScore);

      return { content: [{ type: 'text', text: JSON.stringify({ overall, scores, synced: true }, null, 2) }] };
    }
  );

  // ==========================================================================
  // BID EXECUTION WRITE TOOLS — first batch (Section 5.1)
  // ==========================================================================

  server.tool(
    'update_activity_insight',
    'Append new AIInsight record to activity — APPEND-ONLY',
    { pursuitId: z.string(), activityCode: z.string(), insight: z.object({
      type: z.string(),
      summary: z.string(),
      detail: z.string().optional(),
      severity: z.enum(['info', 'warning', 'critical']).optional(),
      recommendations: z.array(z.string()).optional(),
    }) },
    async ({ pursuitId, activityCode, insight }) => {
      validateAIWrite('ActivityAIInsight', insight);
      const data = await readBidExec(pursuitId);
      if (!data?.activities) return { content: [{ type: 'text', text: `No bid execution data for ${pursuitId}` }], isError: true };
      const activity = data.activities.find(a => a.activityCode === activityCode);
      if (!activity) return { content: [{ type: 'text', text: `Activity ${activityCode} not found` }], isError: true };
      activity.aiInsights = activity.aiInsights || [];
      activity.aiInsights.push({ id: randomUUID(), ...insight, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ appended: true, activityCode }, null, 2) }] };
    }
  );

  server.tool(
    'add_risk_flag',
    'Append risk to activity and bid-level risk register',
    { pursuitId: z.string(), activityCode: z.string(), risk: z.object({
      description: z.string(),
      probability: z.enum(['low', 'medium', 'high']).optional(),
      impact: z.enum(['low', 'medium', 'high']).optional(),
      mitigation: z.string().optional(),
    }) },
    async ({ pursuitId, activityCode, risk }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.activities) return { content: [{ type: 'text', text: `No bid execution data for ${pursuitId}` }], isError: true };
      const activity = data.activities.find(a => a.activityCode === activityCode);
      if (!activity) return { content: [{ type: 'text', text: `Activity ${activityCode} not found` }], isError: true };
      const riskRecord = { id: randomUUID(), ...risk, activityCode, source: 'ai_generated', createdAt: new Date().toISOString() };
      activity.risks = activity.risks || [];
      activity.risks.push(riskRecord);
      data.risks = data.risks || [];
      data.risks.push(riskRecord);
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ added: true, riskId: riskRecord.id }, null, 2) }] };
    }
  );

  server.tool(
    'update_bid_insight',
    'Append bid-level insight with PWIN recalibration — APPEND-ONLY',
    { pursuitId: z.string(), insight: z.object({
      type: z.string(),
      summary: z.string(),
      detail: z.string().optional(),
      pwinImpact: z.number().optional(),
      recommendations: z.array(z.string()).optional(),
    }) },
    async ({ pursuitId, insight }) => {
      validateAIWrite('BidAIInsight', insight);
      const data = await readBidExec(pursuitId) || {};
      data.bidInsights = data.bidInsights || [];
      data.bidInsights.push({ id: randomUUID(), ...insight, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ appended: true }, null, 2) }] };
    }
  );

  server.tool(
    'create_response_section',
    'Create a new response section (ITT ingestion)',
    { pursuitId: z.string(), data: z.object({
      reference: z.string(),
      sectionNumber: z.string().optional(),
      questionText: z.string().optional(),
      evaluationCategory: z.string().optional(),
      evaluationMaxScore: z.number().optional(),
      hurdleScore: z.number().optional(),
      wordLimit: z.number().optional(),
      responseType: z.string().optional(),
    }) },
    async ({ pursuitId, data: sectionData }) => {
      const bidData = await readBidExec(pursuitId) || {};
      bidData.responseSections = bidData.responseSections || [];
      const section = { id: randomUUID(), ...sectionData, createdBy: 'ai_ingestion', createdAt: new Date().toISOString() };
      bidData.responseSections.push(section);
      await store.saveProductData(pursuitId, 'bid_execution', bidData);
      return { content: [{ type: 'text', text: JSON.stringify({ created: true, id: section.id, reference: section.reference }, null, 2) }] };
    }
  );

  server.tool(
    'batch_create_response_sections',
    'Create multiple response sections in one pass (ITT ingestion)',
    { pursuitId: z.string(), sections: z.array(z.object({
      reference: z.string(),
      sectionNumber: z.string().optional(),
      questionText: z.string().optional(),
      evaluationCategory: z.string().optional(),
      evaluationMaxScore: z.number().optional(),
      hurdleScore: z.number().optional(),
      wordLimit: z.number().optional(),
      responseType: z.string().optional(),
    })) },
    async ({ pursuitId, sections }) => {
      const bidData = await readBidExec(pursuitId) || {};
      bidData.responseSections = bidData.responseSections || [];
      const now = new Date().toISOString();
      const created = sections.map(s => ({ id: randomUUID(), ...s, createdBy: 'ai_ingestion', createdAt: now }));
      bidData.responseSections.push(...created);
      await store.saveProductData(pursuitId, 'bid_execution', bidData);
      return { content: [{ type: 'text', text: JSON.stringify({ created: created.length }, null, 2) }] };
    }
  );

  server.tool(
    'create_evaluation_framework',
    'Create evaluation framework for a pursuit (ITT ingestion)',
    { pursuitId: z.string(), framework: z.object({
      totalScore: z.number().optional(),
      qualityWeight: z.number().optional(),
      priceWeight: z.number().optional(),
      categories: z.array(z.object({
        name: z.string(),
        weight: z.number().optional(),
        maxScore: z.number().optional(),
      })).optional(),
    }) },
    async ({ pursuitId, framework }) => {
      const data = await readBidExec(pursuitId) || {};
      data.evaluationFramework = { id: randomUUID(), ...framework, createdBy: 'ai_ingestion', createdAt: new Date().toISOString() };
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ created: true }, null, 2) }] };
    }
  );

  // ==========================================================================
  // BID EXECUTION READ TOOLS — remaining (Section 4.1)
  // ==========================================================================

  server.tool(
    'get_itt_documents',
    'Get ITT documents with optional filters by volume type or parsed status',
    {
      pursuitId: z.string(),
      volumeType: z.string().optional(),
      parsedStatus: z.string().optional(),
    },
    async ({ pursuitId, volumeType, parsedStatus }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.ittDocuments) return { content: [{ type: 'text', text: '[]' }] };
      let docs = data.ittDocuments;
      if (volumeType) docs = docs.filter(d => d.volumeType === volumeType);
      if (parsedStatus) docs = docs.filter(d => d.parsedStatus === parsedStatus);
      return { content: [{ type: 'text', text: JSON.stringify(docs, null, 2) }] };
    }
  );

  server.tool(
    'get_response_items',
    'Get response items with optional filters by status, type, owner, or evaluation weight threshold',
    {
      pursuitId: z.string(),
      status: z.string().optional(),
      responseType: z.string().optional(),
      owner: z.string().optional(),
      evaluationWeightPctMin: z.number().optional(),
      limit: z.number().optional(),
      offset: z.number().optional(),
    },
    async ({ pursuitId, status, responseType, owner, evaluationWeightPctMin, limit, offset }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.responseItems) return { content: [{ type: 'text', text: '[]' }] };
      let items = data.responseItems;
      if (status) items = items.filter(i => i.status === status);
      if (responseType) items = items.filter(i => i.responseType === responseType);
      if (owner) items = items.filter(i => i.owner === owner);
      if (evaluationWeightPctMin !== undefined) items = items.filter(i => (i.evaluationWeightPct || 0) >= evaluationWeightPctMin);
      if (offset) items = items.slice(offset);
      if (limit) items = items.slice(0, limit);
      return { content: [{ type: 'text', text: JSON.stringify(items, null, 2) }] };
    }
  );

  server.tool(
    'get_response_item',
    'Get a single response item by reference',
    { pursuitId: z.string(), reference: z.string() },
    async ({ pursuitId, reference }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.responseItems) return { content: [{ type: 'text', text: `Response item ${reference} not found` }], isError: true };
      const item = data.responseItems.find(i => i.reference === reference);
      if (!item) return { content: [{ type: 'text', text: `Response item ${reference} not found` }], isError: true };
      return { content: [{ type: 'text', text: JSON.stringify(item, null, 2) }] };
    }
  );

  server.tool(
    'get_production_pipeline',
    'Get production pipeline: response items grouped by status with counts',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.responseItems) return { content: [{ type: 'text', text: '{}' }] };
      const pipeline = {};
      for (const item of data.responseItems) {
        const st = item.status || 'unassigned';
        if (!pipeline[st]) pipeline[st] = { count: 0, items: [] };
        pipeline[st].count++;
        pipeline[st].items.push({ reference: item.reference, owner: item.owner, dueDate: item.dueDate });
      }
      return { content: [{ type: 'text', text: JSON.stringify(pipeline, null, 2) }] };
    }
  );

  server.tool(
    'get_compliance_requirements',
    'Get compliance requirements with optional filters',
    {
      pursuitId: z.string(),
      classification: z.string().optional(),
      complianceStatus: z.string().optional(),
      coverageStatus: z.string().optional(),
    },
    async ({ pursuitId, classification, complianceStatus, coverageStatus }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.complianceRequirements) return { content: [{ type: 'text', text: '[]' }] };
      let reqs = data.complianceRequirements;
      if (classification) reqs = reqs.filter(r => r.classification === classification);
      if (complianceStatus) reqs = reqs.filter(r => r.complianceStatus === complianceStatus);
      if (coverageStatus) reqs = reqs.filter(r => r.coverageStatus === coverageStatus);
      return { content: [{ type: 'text', text: JSON.stringify(reqs, null, 2) }] };
    }
  );

  server.tool(
    'get_win_themes',
    'Get win themes from bid execution data (product-level, distinct from shared win themes)',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.winThemes || [], null, 2) }] };
    }
  );

  server.tool(
    'get_client_scoring_scheme',
    'Get client marking/scoring scheme',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.clientScoringScheme || null, null, 2) }] };
    }
  );

  server.tool(
    'get_quality_gaps',
    'Get response items with quality issues: low self-assessment, missing evidence, weak win theme coverage',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.responseItems) return { content: [{ type: 'text', text: '[]' }] };
      const gaps = data.responseItems.filter(i => {
        if (i.qualityScoreGap && i.qualityScoreGap > 0) return true;
        if (i.qualityCredentials === false || i.qualityCredentials === 'none') return true;
        if (i.winThemeCoverageScore !== undefined && i.winThemeCoverageScore < 50) return true;
        return false;
      });
      return { content: [{ type: 'text', text: JSON.stringify(gaps, null, 2) }] };
    }
  );

  server.tool(
    'get_review_cycles',
    'Get all review cycles for a pursuit',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.reviewCycles || [], null, 2) }] };
    }
  );

  server.tool(
    'get_review_cycle_detail',
    'Get detailed review cycle including reviewer feedback and actions',
    { pursuitId: z.string(), reviewCycleId: z.string() },
    async ({ pursuitId, reviewCycleId }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.reviewCycles) return { content: [{ type: 'text', text: `Review cycle ${reviewCycleId} not found` }], isError: true };
      const cycle = data.reviewCycles.find(r => r.id === reviewCycleId);
      if (!cycle) return { content: [{ type: 'text', text: `Review cycle ${reviewCycleId} not found` }], isError: true };
      return { content: [{ type: 'text', text: JSON.stringify(cycle, null, 2) }] };
    }
  );

  server.tool(
    'get_open_review_actions',
    'Get open review actions, optionally filtered by severity',
    { pursuitId: z.string(), severity: z.enum(['critical', 'major', 'minor']).optional() },
    async ({ pursuitId, severity }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.reviewActions) return { content: [{ type: 'text', text: '[]' }] };
      let actions = data.reviewActions.filter(a => a.status !== 'completed' && a.status !== 'closed');
      if (severity) actions = actions.filter(a => a.severity === severity);
      return { content: [{ type: 'text', text: JSON.stringify(actions, null, 2) }] };
    }
  );

  server.tool(
    'get_gate_status',
    'Get governance gate status, optionally for a specific gate',
    { pursuitId: z.string(), gateName: z.string().optional() },
    async ({ pursuitId, gateName }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.gates) return { content: [{ type: 'text', text: '[]' }] };
      let gates = data.gates;
      if (gateName) gates = gates.filter(g => g.name === gateName || g.id === gateName);
      return { content: [{ type: 'text', text: JSON.stringify(gates, null, 2) }] };
    }
  );

  server.tool(
    'get_gate_preparation',
    'Get gate preparation data: criteria status, blockers, readiness assessment',
    { pursuitId: z.string(), gateName: z.string() },
    async ({ pursuitId, gateName }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.gates) return { content: [{ type: 'text', text: `Gate ${gateName} not found` }], isError: true };
      const gate = data.gates.find(g => g.name === gateName || g.id === gateName);
      if (!gate) return { content: [{ type: 'text', text: `Gate ${gateName} not found` }], isError: true };
      return { content: [{ type: 'text', text: JSON.stringify(gate, null, 2) }] };
    }
  );

  server.tool(
    'get_standup_actions',
    'Get standup actions with optional filters',
    {
      pursuitId: z.string(),
      status: z.string().optional(),
      owner: z.string().optional(),
      parentActivityCode: z.string().optional(),
      parentGateId: z.string().optional(),
      overdueOnly: z.boolean().optional(),
    },
    async ({ pursuitId, status, owner, parentActivityCode, parentGateId, overdueOnly }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.standupActions) return { content: [{ type: 'text', text: '[]' }] };
      let actions = data.standupActions;
      if (status) actions = actions.filter(a => a.status === status);
      if (owner) actions = actions.filter(a => a.owner === owner);
      if (parentActivityCode) actions = actions.filter(a => a.parentActivityCode === parentActivityCode);
      if (parentGateId) actions = actions.filter(a => a.parentGateId === parentGateId);
      if (overdueOnly) {
        const now = new Date().toISOString();
        actions = actions.filter(a => a.dueDate && a.dueDate < now && a.status !== 'completed');
      }
      return { content: [{ type: 'text', text: JSON.stringify(actions, null, 2) }] };
    }
  );

  server.tool(
    'get_deferred_actions',
    'Get actions that have been deferred at least once',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.standupActions) return { content: [{ type: 'text', text: '[]' }] };
      const deferred = data.standupActions.filter(a => (a.deferred_count || 0) > 0);
      return { content: [{ type: 'text', text: JSON.stringify(deferred, null, 2) }] };
    }
  );

  server.tool(
    'get_bid_calendar',
    'Get bid calendar: milestones, deadlines, key dates',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.calendar || data?.milestones || [], null, 2) }] };
    }
  );

  server.tool(
    'get_engagement',
    'Get engagement/commercial data for a pursuit',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.engagement || null, null, 2) }] };
    }
  );

  server.tool(
    'get_rate_card',
    'Get rate card data for a pursuit',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.rateCard || null, null, 2) }] };
    }
  );

  server.tool(
    'get_risks',
    'Get risk register with optional filters',
    {
      pursuitId: z.string(),
      registerType: z.string().optional(),
      status: z.string().optional(),
      probability: z.enum(['low', 'medium', 'high']).optional(),
      impact: z.enum(['low', 'medium', 'high']).optional(),
    },
    async ({ pursuitId, registerType, status, probability, impact }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.risks) return { content: [{ type: 'text', text: '[]' }] };
      let risks = data.risks;
      if (registerType) risks = risks.filter(r => r.registerType === registerType);
      if (status) risks = risks.filter(r => r.status === status);
      if (probability) risks = risks.filter(r => r.probability === probability);
      if (impact) risks = risks.filter(r => r.impact === impact);
      return { content: [{ type: 'text', text: JSON.stringify(risks, null, 2) }] };
    }
  );

  server.tool(
    'get_team_summary',
    'Get team summary with member count, roles, and allocation',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.team) return { content: [{ type: 'text', text: '{}' }] };
      const members = Array.isArray(data.team) ? data.team : data.team.members || [];
      const summary = {
        totalMembers: members.length,
        byRole: {},
        members: members.map(m => ({ name: m.name, role: m.role, allocation: m.allocation })),
      };
      for (const m of members) {
        const role = m.role || 'unassigned';
        summary.byRole[role] = (summary.byRole[role] || 0) + 1;
      }
      return { content: [{ type: 'text', text: JSON.stringify(summary, null, 2) }] };
    }
  );

  server.tool(
    'get_team_member',
    'Get details for a specific team member',
    { pursuitId: z.string(), memberName: z.string() },
    async ({ pursuitId, memberName }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.team) return { content: [{ type: 'text', text: `Team member ${memberName} not found` }], isError: true };
      const members = Array.isArray(data.team) ? data.team : data.team.members || [];
      const member = members.find(m => m.name === memberName);
      if (!member) return { content: [{ type: 'text', text: `Team member ${memberName} not found` }], isError: true };
      return { content: [{ type: 'text', text: JSON.stringify(member, null, 2) }] };
    }
  );

  server.tool(
    'get_reviewer_history',
    'Get review history for a specific reviewer',
    { pursuitId: z.string(), reviewerName: z.string() },
    async ({ pursuitId, reviewerName }) => {
      const data = await readBidExec(pursuitId);
      if (!data?.reviewCycles) return { content: [{ type: 'text', text: '[]' }] };
      const history = [];
      for (const cycle of data.reviewCycles) {
        const reviews = (cycle.reviews || []).filter(r => r.reviewer === reviewerName);
        if (reviews.length > 0) history.push({ cycleId: cycle.id, cycleName: cycle.name, reviews });
      }
      return { content: [{ type: 'text', text: JSON.stringify(history, null, 2) }] };
    }
  );

  server.tool(
    'get_stakeholders',
    'Get stakeholders from bid execution data (product-level)',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.stakeholders || [], null, 2) }] };
    }
  );

  server.tool(
    'get_rules',
    'Get bid-level rules and constraints',
    { pursuitId: z.string() },
    async ({ pursuitId }) => {
      const data = await readBidExec(pursuitId);
      return { content: [{ type: 'text', text: JSON.stringify(data?.rules || {}, null, 2) }] };
    }
  );

  // Placeholder — implement when bid library product is built
  server.tool(
    'get_bid_library_match',
    'Search bid library for matching past bid assets [PLACEHOLDER]',
    { query: z.string() },
    async ({ query }) => {
      return { content: [{ type: 'text', text: JSON.stringify({ placeholder: true, message: 'Bid library not yet implemented', query }, null, 2) }] };
    }
  );

  // ==========================================================================
  // SHARED READ TOOLS — placeholders (Section 4.3)
  // ==========================================================================

  server.tool(
    'get_client_profile',
    'Get persistent client intelligence from reference data [PLACEHOLDER]',
    { clientId: z.string() },
    async ({ clientId }) => {
      const data = await store.getReferenceData('client_profiles', clientId);
      if (!data) return { content: [{ type: 'text', text: JSON.stringify({ placeholder: true, message: `Client profile ${clientId} not yet created` }, null, 2) }] };
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_competitor_dossier',
    'Get pre-compiled competitor record from reference data [PLACEHOLDER]',
    { competitorName: z.string() },
    async ({ competitorName }) => {
      const data = await store.getReferenceData('competitor_dossiers', competitorName);
      if (!data) return { content: [{ type: 'text', text: JSON.stringify({ placeholder: true, message: `Competitor dossier ${competitorName} not yet created` }, null, 2) }] };
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  // ==========================================================================
  // BID EXECUTION WRITE TOOLS — remaining (Section 5.1)
  // ==========================================================================

  server.tool(
    'update_response_insight',
    'Append AI insight to a response item — APPEND-ONLY [PLACEHOLDER]',
    { pursuitId: z.string(), responseReference: z.string(), insight: z.object({
      type: z.string(),
      summary: z.string(),
      detail: z.string().optional(),
      qualityScore: z.number().optional(),
      recommendations: z.array(z.string()).optional(),
    }) },
    async ({ pursuitId, responseReference, insight }) => {
      validateAIWrite('ResponseItemAIInsight', insight);
      const data = await readBidExec(pursuitId) || {};
      if (!data.responseItems) return { content: [{ type: 'text', text: `No response items for ${pursuitId}` }], isError: true };
      const item = data.responseItems.find(i => i.reference === responseReference);
      if (!item) return { content: [{ type: 'text', text: `Response item ${responseReference} not found` }], isError: true };
      item.aiInsights = item.aiInsights || [];
      item.aiInsights.push({ id: randomUUID(), ...insight, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ appended: true, responseReference }, null, 2) }] };
    }
  );

  server.tool(
    'log_gate_recommendation',
    'Write AI gate readiness assessment',
    { pursuitId: z.string(), gateName: z.string(), recommendation: z.object({
      readiness: z.enum(['ready', 'conditional', 'not_ready']),
      summary: z.string(),
      conditions: z.array(z.string()).optional(),
      risks: z.array(z.string()).optional(),
      blockers: z.array(z.string()).optional(),
    }) },
    async ({ pursuitId, gateName, recommendation }) => {
      const data = await readBidExec(pursuitId) || {};
      data.gates = data.gates || [];
      const gate = data.gates.find(g => g.name === gateName || g.id === gateName);
      if (!gate) return { content: [{ type: 'text', text: `Gate ${gateName} not found` }], isError: true };
      gate.aiRecommendations = gate.aiRecommendations || [];
      gate.aiRecommendations.push({ id: randomUUID(), ...recommendation, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ logged: true, gateName }, null, 2) }] };
    }
  );

  server.tool(
    'create_gate_readiness_report',
    'Create gate readiness AI insight — APPEND-ONLY, auto-generates StandupActions for amber criteria',
    { pursuitId: z.string(), gateId: z.string(), report: z.object({
      overallReadiness: z.enum(['green', 'amber', 'red']),
      criteriaAssessments: z.array(z.object({
        criterion: z.string(),
        status: z.enum(['green', 'amber', 'red']),
        finding: z.string(),
        action: z.string().optional(),
      })).optional(),
      summary: z.string(),
      recommendations: z.array(z.string()).optional(),
    }) },
    async ({ pursuitId, gateId, report }) => {
      const data = await readBidExec(pursuitId) || {};
      data.gateReadinessInsights = data.gateReadinessInsights || [];
      const insight = { id: randomUUID(), gateId, ...report, generatedAt: new Date().toISOString() };
      data.gateReadinessInsights.push(insight);

      // Auto-generate standup actions for amber criteria
      if (report.criteriaAssessments) {
        data.standupActions = data.standupActions || [];
        for (const ca of report.criteriaAssessments) {
          if (ca.status === 'amber' && ca.action) {
            data.standupActions.push({
              id: randomUUID(),
              description: ca.action,
              parentGateId: gateId,
              source: 'ai_generated',
              status: 'open',
              createdAt: new Date().toISOString(),
            });
          }
        }
      }

      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ created: true, insightId: insight.id }, null, 2) }] };
    }
  );

  server.tool(
    'create_compliance_coverage_insight',
    'Create compliance coverage AI insight — APPEND-ONLY',
    { pursuitId: z.string(), insight: z.object({
      type: z.string(),
      summary: z.string(),
      coveragePct: z.number().optional(),
      gaps: z.array(z.object({ requirement: z.string(), status: z.string(), recommendation: z.string().optional() })).optional(),
    }) },
    async ({ pursuitId, insight }) => {
      validateAIWrite('ComplianceCoverageAIInsight', insight);
      const data = await readBidExec(pursuitId) || {};
      data.complianceCoverageInsights = data.complianceCoverageInsights || [];
      data.complianceCoverageInsights.push({ id: randomUUID(), ...insight, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ created: true }, null, 2) }] };
    }
  );

  server.tool(
    'update_win_theme_coverage_score',
    'Update AI-owned win theme coverage score on a response section',
    { pursuitId: z.string(), responseSectionReference: z.string(), score: z.number() },
    async ({ pursuitId, responseSectionReference, score }) => {
      const data = await readBidExec(pursuitId) || {};
      if (!data.responseSections) return { content: [{ type: 'text', text: 'No response sections' }], isError: true };
      const section = data.responseSections.find(s => s.reference === responseSectionReference);
      if (!section) return { content: [{ type: 'text', text: `Section ${responseSectionReference} not found` }], isError: true };
      section.winThemeCoverageScore = score;
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ updated: true, reference: responseSectionReference, score }, null, 2) }] };
    }
  );

  server.tool(
    'create_effort_allocation_insight',
    'Create effort allocation AI insight — APPEND-ONLY',
    { pursuitId: z.string(), insight: z.object({
      type: z.string(),
      summary: z.string(),
      allocations: z.array(z.object({ reference: z.string(), currentEffort: z.number().optional(), recommendedEffort: z.number().optional(), rationale: z.string().optional() })).optional(),
    }) },
    async ({ pursuitId, insight }) => {
      validateAIWrite('EffortAllocationAIInsight', insight);
      const data = await readBidExec(pursuitId) || {};
      data.effortAllocationInsights = data.effortAllocationInsights || [];
      data.effortAllocationInsights.push({ id: randomUUID(), ...insight, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ created: true }, null, 2) }] };
    }
  );

  server.tool(
    'create_standup_action',
    'Create a new standup action with source: ai_generated',
    { pursuitId: z.string(), action: z.object({
      description: z.string(),
      parentActivityCode: z.string().optional(),
      parentGateId: z.string().optional(),
      priority: z.enum(['low', 'medium', 'high', 'critical']).optional(),
      suggestedOwner: z.string().optional(),
      suggestedDueDate: z.string().optional(),
    }) },
    async ({ pursuitId, action }) => {
      const data = await readBidExec(pursuitId) || {};
      data.standupActions = data.standupActions || [];
      const record = { id: randomUUID(), ...action, source: 'ai_generated', status: 'open', createdAt: new Date().toISOString() };
      data.standupActions.push(record);
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ created: true, actionId: record.id }, null, 2) }] };
    }
  );

  server.tool(
    'update_standup_action_deferred',
    'Write AI-owned fields on existing standup action (deferred count, escalation, recommendation)',
    { pursuitId: z.string(), actionId: z.string(), deferred_count: z.number().optional(), escalation_recommended: z.boolean().optional(), recommended_decision: z.string().optional() },
    async ({ pursuitId, actionId, deferred_count, escalation_recommended, recommended_decision }) => {
      const data = await readBidExec(pursuitId) || {};
      if (!data.standupActions) return { content: [{ type: 'text', text: 'No standup actions' }], isError: true };
      const action = data.standupActions.find(a => a.id === actionId);
      if (!action) return { content: [{ type: 'text', text: `Action ${actionId} not found` }], isError: true };
      if (deferred_count !== undefined) action.deferred_count = deferred_count;
      if (escalation_recommended !== undefined) action.escalation_recommended = escalation_recommended;
      if (recommended_decision !== undefined) action.recommended_decision = recommended_decision;
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ updated: true, actionId }, null, 2) }] };
    }
  );

  server.tool(
    'flag_response_section_amended',
    'Set ResponseSection.lastAmended — AI-writable field for tracking ITT amendments',
    { pursuitId: z.string(), reference: z.string(), reason: z.string() },
    async ({ pursuitId, reference, reason }) => {
      const data = await readBidExec(pursuitId) || {};
      if (!data.responseSections) return { content: [{ type: 'text', text: 'No response sections' }], isError: true };
      const section = data.responseSections.find(s => s.reference === reference);
      if (!section) return { content: [{ type: 'text', text: `Section ${reference} not found` }], isError: true };
      section.lastAmended = { reason, at: new Date().toISOString() };
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ flagged: true, reference }, null, 2) }] };
    }
  );

  server.tool(
    'create_itt_document',
    'Create an ITT document record (ITT ingestion)',
    { pursuitId: z.string(), document: z.object({
      name: z.string(),
      volumeType: z.string().optional(),
      parsedStatus: z.enum(['pending', 'parsed', 'failed']).optional(),
      pageCount: z.number().optional(),
      sections: z.array(z.string()).optional(),
    }) },
    async ({ pursuitId, document }) => {
      const data = await readBidExec(pursuitId) || {};
      data.ittDocuments = data.ittDocuments || [];
      const doc = { id: randomUUID(), ...document, createdBy: 'ai_ingestion', createdAt: new Date().toISOString() };
      data.ittDocuments.push(doc);
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ created: true, documentId: doc.id }, null, 2) }] };
    }
  );

  server.tool(
    'update_bid_procurement_context',
    'Update bid procurement context fields',
    { pursuitId: z.string(), context: z.object({
      procurementRoute: z.string().optional(),
      frameworkReference: z.string().optional(),
      lotNumber: z.string().optional(),
      contractType: z.string().optional(),
      estimatedContractValue: z.number().optional(),
      submissionMethod: z.string().optional(),
      evaluationModel: z.string().optional(),
    }) },
    async ({ pursuitId, context }) => {
      const data = await readBidExec(pursuitId) || {};
      data.procurementContext = { ...(data.procurementContext || {}), ...context, updatedAt: new Date().toISOString() };
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ updated: true }, null, 2) }] };
    }
  );

  server.tool(
    'ingest_scoring_scheme',
    'Ingest client scoring/marking scheme',
    { pursuitId: z.string(), scheme: z.object({
      name: z.string().optional(),
      levels: z.array(z.object({
        score: z.number(),
        label: z.string(),
        description: z.string().optional(),
      })).optional(),
      maxScore: z.number().optional(),
      passMark: z.number().optional(),
    }) },
    async ({ pursuitId, scheme }) => {
      const data = await readBidExec(pursuitId) || {};
      data.clientScoringScheme = { ...scheme, ingestedAt: new Date().toISOString(), createdBy: 'ai_ingestion' };
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ ingested: true }, null, 2) }] };
    }
  );

  server.tool(
    'generate_report_output',
    'Generate and store a report output',
    { pursuitId: z.string(), reportType: z.string(), content: z.string() },
    async ({ pursuitId, reportType, content: reportContent }) => {
      const data = await readBidExec(pursuitId) || {};
      data.reports = data.reports || [];
      data.reports.push({ id: randomUUID(), type: reportType, content: reportContent, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { content: [{ type: 'text', text: JSON.stringify({ generated: true, reportType }, null, 2) }] };
    }
  );

  // ==========================================================================
  // QUALIFY WRITE TOOLS — remaining (Section 5.2)
  // ==========================================================================

  server.tool(
    'generate_qualification_report',
    'Generate and store the full qualification report — key output from Qualify product',
    { pursuitId: z.string(), reportContent: z.string() },
    async ({ pursuitId, reportContent }) => {
      const data = await store.getProductData(pursuitId, 'qualify') || {};
      data.report = { content: reportContent, generatedAt: new Date().toISOString() };
      await store.saveProductData(pursuitId, 'qualify', data);
      return { content: [{ type: 'text', text: JSON.stringify({ generated: true }, null, 2) }] };
    }
  );

  // ==========================================================================
  // REFERENCE WRITE TOOLS — placeholders (Section 5.4)
  // ==========================================================================

  server.tool(
    'update_client_profile',
    'Create or update client profile in reference data [PLACEHOLDER]',
    { clientId: z.string(), profile: z.object({
      name: z.string(),
      sector: z.string().optional(),
      strategicPriorities: z.array(z.string()).optional(),
      knownPainPoints: z.array(z.string()).optional(),
      relationships: z.array(z.object({ contact: z.string(), role: z.string().optional(), strength: z.string().optional() })).optional(),
    }) },
    async ({ clientId, profile }) => {
      // Reference data writes go to reference/client_profiles/{clientId}.json
      const existing = await store.getReferenceData('client_profiles', clientId);
      const merged = { ...(existing || {}), ...profile, updatedAt: new Date().toISOString() };
      // Use low-level write since store doesn't have a saveReferenceData yet
      const { writeFile, mkdir } = await import('node:fs/promises');
      const { join, dirname } = await import('node:path');
      const filePath = join(store.DATA_ROOT, 'reference', 'client_profiles', `${clientId}.json`);
      await mkdir(dirname(filePath), { recursive: true });
      await writeFile(filePath, JSON.stringify(merged, null, 2), 'utf-8');
      return { content: [{ type: 'text', text: JSON.stringify({ updated: true, clientId }, null, 2) }] };
    }
  );

  server.tool(
    'update_competitor_dossier',
    'Create or update competitor dossier in reference data [PLACEHOLDER]',
    { competitorName: z.string(), dossier: z.object({
      name: z.string(),
      strengths: z.array(z.string()).optional(),
      weaknesses: z.array(z.string()).optional(),
      recentWins: z.array(z.object({ opportunity: z.string(), value: z.number().optional(), date: z.string().optional() })).optional(),
      typicalStrategy: z.string().optional(),
      pricePositioning: z.string().optional(),
    }) },
    async ({ competitorName, dossier }) => {
      const { writeFile, mkdir } = await import('node:fs/promises');
      const { join, dirname } = await import('node:path');
      const existing = await store.getReferenceData('competitor_dossiers', competitorName);
      const merged = { ...(existing || {}), ...dossier, updatedAt: new Date().toISOString() };
      const filePath = join(store.DATA_ROOT, 'reference', 'competitor_dossiers', `${competitorName}.json`);
      await mkdir(dirname(filePath), { recursive: true });
      await writeFile(filePath, JSON.stringify(merged, null, 2), 'utf-8');
      return { content: [{ type: 'text', text: JSON.stringify({ updated: true, competitorName }, null, 2) }] };
    }
  );

  // ==========================================================================
  // COMPETITIVE INTELLIGENCE TOOLS (FTS OCDS data)
  // ==========================================================================

  server.tool(
    'get_competitive_intel_summary',
    'Get summary statistics from the UK procurement intelligence database (buyers, suppliers, awards, values)',
    {},
    async () => {
      const result = compIntel.dbSummary();
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'get_buyer_profile',
    'Get buyer procurement profile: spend, top suppliers, procurement methods, award history. Use for understanding a client before qualifying or bidding.',
    {
      name: z.string().describe('Buyer name or partial match (e.g. "Home Office", "NHS", "Ministry of Defence")'),
      limit: z.number().optional().describe('Max recent awards to return (default 20)'),
    },
    async ({ name, limit }) => {
      const result = compIntel.buyerProfile(name, limit);
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'get_supplier_profile',
    'Get supplier/competitor profile: win history, buyer relationships, active contracts (incumbencies). Use for competitive positioning analysis.',
    {
      name: z.string().describe('Supplier name or partial match (e.g. "Serco", "Capita", "Deloitte")'),
      limit: z.number().optional().describe('Max recent awards to return (default 20)'),
    },
    async ({ name, limit }) => {
      const result = compIntel.supplierProfile(name, limit);
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'get_expiring_contracts',
    'Find contracts expiring within N days — core sales prospecting tool. Filter by value, buyer, and category.',
    {
      days: z.number().optional().describe('Days until expiry (default 365)'),
      minValue: z.number().optional().describe('Minimum contract value in GBP'),
      buyer: z.string().optional().describe('Buyer name filter (partial match)'),
      category: z.string().optional().describe('Category filter: services, goods, or works'),
    },
    async ({ days, minValue, buyer, category }) => {
      const result = compIntel.expiringContracts({ days, minValue, buyer, category });
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'get_forward_pipeline',
    'Get planning and market engagement notices — upcoming tenders not yet published. Early positioning intelligence.',
    {
      buyer: z.string().optional().describe('Buyer name filter (partial match)'),
    },
    async ({ buyer }) => {
      const result = compIntel.forwardPipeline({ buyer });
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'get_pwin_signals',
    'Get competition level analysis per buyer and category: avg bidders, procurement method breakdown, direct award rates. Core PWIN input for qualification.',
    {
      buyer: z.string().optional().describe('Buyer name filter (partial match)'),
      category: z.string().optional().describe('Category filter: services, goods, or works'),
    },
    async ({ buyer, category }) => {
      const result = compIntel.pwinSignals({ buyer, category });
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool(
    'search_cpv_codes',
    'Search procurement notices by CPV (Common Procurement Vocabulary) code prefix. Use to find opportunities in specific sectors.',
    {
      code: z.string().describe('CPV code or prefix (e.g. "79410000" for management consultancy, "72" for IT services)'),
    },
    async ({ code }) => {
      const result = compIntel.cpvSearch(code);
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  // ==========================================================================
  // CANONICAL ADJUDICATOR WRITE TOOLS
  // ==========================================================================

  server.tool(
    'log_adjudicator_decision',
    'Append a canonical adjudicator decision to the decisions log. Call for EVERY decision in the session regardless of recommendation (auto_promote, escalate, or reject).',
    {
      decision: z.object({
        decision_id: z.string().describe('Sequential run ID: ADJ-YYYYMMDD-NNN'),
        decision_type: z.enum(['buyer_merge', 'supplier_merge', 'service_classification', 'drift_flag']),
        recommendation: z.enum(['auto_promote', 'escalate', 'reject']),
        confidence: z.number().min(0).max(1),
        canonical_target: z.string().nullable().optional(),
        raw_ids: z.array(z.string()),
        evidence: z.array(z.string()),
        playbook_rule: z.string().nullable().optional(),
        uncertainty_notes: z.string().nullable().optional(),
      }),
      operator_outcome: z.enum(['human_approved', 'human_rejected', 'pending']).describe(
        'human_approved = operator confirmed; human_rejected = operator overturned; pending = escalated, not yet resolved'
      ).optional(),
    },
    async ({ decision, operator_outcome }) => {
      const { appendFile, mkdir } = await import('node:fs/promises');
      const { join: pathJoin } = await import('node:path');
      const { fileURLToPath } = await import('node:url');
      const dir = pathJoin(fileURLToPath(import.meta.url), '..', '..', '..', 'pwin-competitive-intel', 'adjudicator');
      const filePath = pathJoin(dir, 'adjudicator_decisions.jsonl');
      await mkdir(dir, { recursive: true });
      const record = {
        ...decision,
        operator_outcome: operator_outcome || 'pending',
        logged_at: new Date().toISOString(),
      };
      await appendFile(filePath, JSON.stringify(record) + '\n', 'utf-8');
      return { content: [{ type: 'text', text: JSON.stringify({ logged: true, decision_id: decision.decision_id }, null, 2) }] };
    }
  );

  server.tool(
    'promote_canonical_decision',
    'Execute an approved supplier merge in the canonical layer. Re-parents all supplier_to_canonical rows from the absorbed canonical to the survivor, deletes the absorbed record, and refreshes member_count. Marks the adjudication_queue row approved. Only valid for supplier_merge decisions confirmed by the operator.',
    {
      queue_id: z.string().describe('Row ID from adjudication_queue — the stable pair hash'),
      survivor_canonical_id: z.string().describe('Canonical ID to keep — all absorbed members reparent here'),
      absorbed_canonical_id: z.string().describe('Canonical ID to dissolve — all its members move to survivor'),
      decision_id: z.string().describe('ADJ-YYYYMMDD-NNN from the adjudicator log, for traceability'),
    },
    async ({ queue_id, survivor_canonical_id, absorbed_canonical_id, decision_id }) => {
      const { DatabaseSync } = await import('node:sqlite');
      const { join: pathJoin } = await import('node:path');
      const { fileURLToPath } = await import('node:url');
      const dbPath = pathJoin(fileURLToPath(import.meta.url), '..', '..', '..', 'pwin-competitive-intel', 'db', 'bid_intel.db');
      let db;
      try {
        db = new DatabaseSync(dbPath);
      } catch (e) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: `Cannot open database: ${e.message}` }) }] };
      }
      try {
        db.exec('PRAGMA foreign_keys = ON');
        const row = db.prepare('SELECT status FROM adjudication_queue WHERE queue_id = ?').get(queue_id);
        if (!row) return { content: [{ type: 'text', text: JSON.stringify({ error: `queue_id ${queue_id} not found in adjudication_queue` }) }] };
        if (row.status !== 'pending') return { content: [{ type: 'text', text: JSON.stringify({ error: `queue_id ${queue_id} is already ${row.status} — not re-applying` }) }] };
        const survivor = db.prepare('SELECT canonical_id FROM canonical_suppliers WHERE canonical_id = ?').get(survivor_canonical_id);
        if (!survivor) return { content: [{ type: 'text', text: JSON.stringify({ error: `Survivor ${survivor_canonical_id} not found in canonical_suppliers` }) }] };
        const moved = db.prepare('UPDATE supplier_to_canonical SET canonical_id = ? WHERE canonical_id = ?').run(survivor_canonical_id, absorbed_canonical_id);
        db.prepare('DELETE FROM canonical_suppliers WHERE canonical_id = ?').run(absorbed_canonical_id);
        db.prepare('UPDATE canonical_suppliers SET member_count = (SELECT COUNT(*) FROM supplier_to_canonical WHERE canonical_id = ?) WHERE canonical_id = ?').run(survivor_canonical_id, survivor_canonical_id);
        db.prepare("UPDATE adjudication_queue SET status = 'approved', decision_json = ?, reviewed_at = ? WHERE queue_id = ?").run(
          JSON.stringify({ decision_id, promoted_at: new Date().toISOString() }),
          new Date().toISOString(),
          queue_id,
        );
        return { content: [{ type: 'text', text: JSON.stringify({ promoted: true, decision_id, survivor_canonical_id, absorbed_canonical_id, members_moved: moved.changes }, null, 2) }] };
      } catch (e) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: e.message }) }] };
      } finally {
        db.close();
      }
    }
  );

  server.tool(
    'stage_escalation',
    'Write an escalated adjudicator decision to the adjudicator_escalations staging table and mark the corresponding adjudication_queue row as deferred. Call after log_adjudicator_decision for every recommendation=escalate decision.',
    {
      decision_id: z.string().describe('ADJ-YYYYMMDD-NNN from the adjudicator log'),
      decision_type: z.enum(['buyer_merge', 'supplier_merge', 'service_classification', 'drift_flag']),
      confidence: z.number().min(0).max(1),
      queue_id: z.string().nullable().optional().describe('adjudication_queue row to mark deferred; omit for non-queue escalations'),
      canonical_target: z.string().nullable().optional(),
      raw_ids: z.array(z.string()),
      evidence: z.array(z.string()),
      playbook_rule: z.string().nullable().optional(),
      uncertainty_notes: z.string().nullable().optional(),
    },
    async ({ decision_id, decision_type, confidence, queue_id, canonical_target, raw_ids, evidence, playbook_rule, uncertainty_notes }) => {
      const { DatabaseSync } = await import('node:sqlite');
      const { join: pathJoin } = await import('node:path');
      const { fileURLToPath } = await import('node:url');
      const dbPath = pathJoin(fileURLToPath(import.meta.url), '..', '..', '..', 'pwin-competitive-intel', 'db', 'bid_intel.db');
      let db;
      try {
        db = new DatabaseSync(dbPath);
      } catch (e) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: `Cannot open database: ${e.message}` }) }] };
      }
      try {
        db.exec(`CREATE TABLE IF NOT EXISTS adjudicator_escalations (
          escalation_id TEXT PRIMARY KEY,
          decision_type TEXT NOT NULL,
          queue_id TEXT,
          confidence REAL NOT NULL,
          canonical_target TEXT,
          raw_ids TEXT NOT NULL,
          evidence TEXT NOT NULL,
          playbook_rule TEXT,
          uncertainty_notes TEXT,
          operator_outcome TEXT NOT NULL DEFAULT 'pending',
          logged_at TEXT NOT NULL DEFAULT (datetime('now')),
          resolved_at TEXT
        )`);
        db.prepare(`INSERT OR IGNORE INTO adjudicator_escalations
          (escalation_id, decision_type, queue_id, confidence, canonical_target, raw_ids, evidence, playbook_rule, uncertainty_notes)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`)
          .run(decision_id, decision_type, queue_id || null, confidence, canonical_target || null, JSON.stringify(raw_ids), JSON.stringify(evidence), playbook_rule || null, uncertainty_notes || null);
        let queueUpdated = false;
        if (queue_id) {
          const r = db.prepare("UPDATE adjudication_queue SET status = 'deferred', reviewed_at = ? WHERE queue_id = ? AND status = 'pending'").run(new Date().toISOString(), queue_id);
          queueUpdated = r.changes > 0;
        }
        return { content: [{ type: 'text', text: JSON.stringify({ staged: true, escalation_id: decision_id, queue_updated: queueUpdated }, null, 2) }] };
      } catch (e) {
        return { content: [{ type: 'text', text: JSON.stringify({ error: e.message }) }] };
      } finally {
        db.close();
      }
    }
  );

  return server;
}

async function startMCP() {
  const server = createMcpServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('[PWIN Platform] MCP server connected via stdio');
  return server;
}

export { createMcpServer, startMCP };
