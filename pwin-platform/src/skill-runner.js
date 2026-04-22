/**
 * PWIN Platform — Skill Runner
 *
 * Generic executor for declarative skill configs.
 * Each skill is a YAML file defining: prompt, tools, input schema, output handling.
 * The runner assembles context, calls Claude, validates output, writes results via MCP tools.
 *
 * Flow:
 *   1. Load skill config (YAML)
 *   2. Gather context: read pursuit data + platform knowledge via MCP tool handlers
 *   3. Assemble system prompt with injected context blocks
 *   4. Call Claude API with assembled prompt + tool definitions
 *   5. Process Claude's tool calls (MCP writes) and return result
 */

import { readFile, readdir } from 'node:fs/promises';
import { join, basename } from 'node:path';
import { parse as parseYAML } from './yaml-lite.js';
import * as store from './store.js';
import * as intel from './competitive-intel.js';

// ---------------------------------------------------------------------------
// Skill loading
// ---------------------------------------------------------------------------

const SKILLS_DIR = join(import.meta.dirname, '..', 'skills');

async function loadSkill(skillId) {
  // Search all agent directories for matching skill file
  const agentDirs = await readdir(SKILLS_DIR, { withFileTypes: true });
  for (const dir of agentDirs) {
    if (!dir.isDirectory()) continue;
    const files = await readdir(join(SKILLS_DIR, dir.name));
    for (const file of files) {
      if (file === `${skillId}.yaml` || file === `${skillId}.yml`) {
        const raw = await readFile(join(SKILLS_DIR, dir.name, file), 'utf-8');
        return parseYAML(raw);
      }
    }
  }
  throw new Error(`Skill not found: ${skillId}`);
}

async function listSkills() {
  const skills = [];
  const agentDirs = await readdir(SKILLS_DIR, { withFileTypes: true });
  for (const dir of agentDirs) {
    if (!dir.isDirectory()) continue;
    const files = await readdir(join(SKILLS_DIR, dir.name));
    for (const file of files) {
      if (!file.endsWith('.yaml') && !file.endsWith('.yml')) continue;
      const raw = await readFile(join(SKILLS_DIR, dir.name, file), 'utf-8');
      const config = parseYAML(raw);
      skills.push({
        id: config.id,
        agent: config.agent,
        name: config.name,
        description: config.description,
        phase: config.phase,
      });
    }
  }
  return skills;
}

// ---------------------------------------------------------------------------
// Context assembly
// ---------------------------------------------------------------------------

async function gatherContext(skill, input) {
  const context = {};
  const { pursuitId } = input;

  // Always load pursuit data if we have a pursuitId
  if (pursuitId) {
    const shared = await store.getPursuit(pursuitId);
    if (shared) {
      context.pursuit = shared.pursuit;
      context.pwinScore = shared.pwinScore;
      context.winThemes = shared.winThemes;
      context.competitivePositioning = shared.competitivePositioning;
      context.stakeholderMap = shared.stakeholderMap;
      context.buyerValues = shared.buyerValues;
      context.clientIntelligence = shared.clientIntelligence;
    }
  }

  // Load platform knowledge as specified by skill config
  const knowledge = skill.context || [];
  for (const item of knowledge) {
    switch (item) {
      case 'sector_knowledge': {
        const sector = context.pursuit?.sector;
        if (sector) {
          const data = await store.getPlatformData('sector_knowledge.json');
          context.sectorKnowledge = data?.[sector] || null;
        }
        break;
      }
      case 'opportunity_type': {
        const oppType = context.pursuit?.opportunityType;
        if (oppType) {
          const data = await store.getPlatformData('opportunity_types.json');
          context.opportunityType = data?.[oppType] || null;
        }
        break;
      }
      case 'sector_opp_matrix': {
        const sector = context.pursuit?.sector;
        const oppType = context.pursuit?.opportunityType;
        if (sector && oppType) {
          const data = await store.getPlatformData('sector_opp_matrix.json');
          if (Array.isArray(data)) {
            context.sectorOppMatrix = data.find(e =>
              e.sector.toLowerCase().includes(sector.toLowerCase()) &&
              e.opportunityType.toLowerCase().includes(oppType.toLowerCase())
            ) || null;
          }
        }
        break;
      }
      case 'reasoning_rules': {
        const data = await store.getPlatformData('reasoning_rules.json');
        context.reasoningRules = data || [];
        break;
      }
      case 'confidence_model': {
        context.confidenceModel = await store.getPlatformData('confidence_model.json');
        break;
      }
      case 'few_shot_examples': {
        context.fewShotExamples = await store.getPlatformData('few_shot_examples.json');
        break;
      }
      case 'output_schema': {
        context.outputSchema = await store.getPlatformData('output_schema.json');
        break;
      }
      case 'system_prompt': {
        context.systemPrompt = await store.getPlatformData('system_prompt.json');
        break;
      }
      case 'data_points': {
        context.dataPoints = await store.getPlatformData('data_points.json');
        break;
      }
      case 'source_hierarchy': {
        context.sourceHierarchy = await store.getPlatformData('source_hierarchy.json');
        break;
      }
      case 'supplier_dossier': {
        // Load a previously-generated supplier intelligence dossier from
        // ~/.pwin/reference/suppliers/{supplierName}.json. The supplierName
        // comes from skill input — enables downstream skills (competitive
        // strategy, incumbent assessment) to pull in the deep dossier.
        const supplierName = input?.supplierName;
        if (supplierName) {
          const slug = supplierName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
          context.supplierDossier = await store.getReferenceData('suppliers', slug);
        }
        break;
      }
      case 'governance_gates': {
        const gateData = await store.getPlatformData('governance/governance_gate_definitions.json');
        context.governanceGates = gateData || null;
        break;
      }
      case 'governance_pack_template': {
        const templateData = await store.getPlatformData('governance/governance_pack_templates.json');
        // If gateTier is known from input, load only that tier's template
        const tier = input?.gateTier || null;
        if (tier && templateData?.[tier]) {
          context.governancePackTemplate = templateData[tier];
        } else {
          context.governancePackTemplate = templateData || null;
        }
        break;
      }
      case 'governance_risk_framework': {
        context.governanceRiskFramework = await store.getPlatformData('governance/governance_risk_framework.json');
        break;
      }
      case 'governance_signoff_matrix': {
        context.governanceSignoffMatrix = await store.getPlatformData('governance/governance_signoff_matrix.json');
        break;
      }
      case 'canonical_glossary': {
        const glossaryPath = join(import.meta.dirname, '..', '..', 'pwin-competitive-intel', 'adjudicator', 'canonical_glossary.json');
        try {
          const raw = await readFile(glossaryPath, 'utf-8');
          context.canonical_glossary = JSON.parse(raw);
        } catch { /* file not present — leave undefined, placeholder stays in prompt */ }
        break;
      }
      case 'framework_taxonomy': {
        const taxonomyPath = join(import.meta.dirname, '..', '..', 'pwin-competitive-intel', 'adjudicator', 'framework_taxonomy.json');
        try {
          const raw = await readFile(taxonomyPath, 'utf-8');
          context.framework_taxonomy = JSON.parse(raw);
        } catch { /* file not present */ }
        break;
      }
      case 'adjudicator_decisions': {
        const decisionsPath = join(import.meta.dirname, '..', '..', 'pwin-competitive-intel', 'adjudicator', 'adjudicator_decisions.jsonl');
        try {
          const raw = await readFile(decisionsPath, 'utf-8');
          const lines = raw.trim().split('\n').filter(Boolean);
          context.adjudicator_decisions = lines.slice(-50).map(l => JSON.parse(l));
        } catch { /* file not present */ }
        break;
      }
      case 'canonical_playbook': {
        const playbookPath = join(import.meta.dirname, '..', '..', 'pwin-competitive-intel', 'CANONICAL-LAYER-PLAYBOOK.md');
        try {
          context.canonical_playbook = await readFile(playbookPath, 'utf-8');
        } catch { /* file not present */ }
        break;
      }
      case 'fts_buyer_data': {
        const buyerName = input?.buyerName;
        if (buyerName) {
          const data = intel.buyerProfile(buyerName);
          context.ftsBuyerData = (data?.error || !data?.buyers?.length)
            ? `No FTS data found for buyer: ${buyerName}`
            : data;
        }
        break;
      }
      case 'fts_supplier_data': {
        const supplierName = input?.supplierName;
        if (supplierName) {
          const data = intel.supplierProfile(supplierName);
          context.ftsSupplierData = (data?.error || !data?.suppliers?.length)
            ? `No FTS data found for supplier: ${supplierName}`
            : data;
        }
        break;
      }
      case 'fts_sector_data': {
        const sectorName = input?.sectorName;
        if (sectorName) {
          const data = intel.sectorProfile(sectorName);
          context.ftsSectorData = data?.error
            ? `No FTS data found for sector: ${sectorName}`
            : data;
        }
        break;
      }
      default:
        break;
    }
  }

  // Load product-specific data as specified
  const products = skill.product_data || [];
  if (pursuitId) {
    for (const product of products) {
      const pKey = product.replace('-', '_');
      context[pKey] = await store.getProductData(pursuitId, pKey);
    }
  }

  return context;
}

// ---------------------------------------------------------------------------
// Prompt assembly
// ---------------------------------------------------------------------------

function assemblePrompt(skill, context, input) {
  let systemPrompt = skill.system_prompt || '';

  // Inject context blocks using {{variable}} template syntax
  systemPrompt = systemPrompt.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    if (key === 'sector_knowledge' && context.sectorKnowledge) {
      return context.sectorKnowledge.promptBlock || '';
    }
    if (key === 'opportunity_type' && context.opportunityType) {
      return context.opportunityType.promptBlock || '';
    }
    if (key === 'sector_opp_matrix' && context.sectorOppMatrix) {
      return context.sectorOppMatrix.intersectionIntelligence || '';
    }
    if (key === 'pursuit_context' && context.pursuit) {
      return JSON.stringify(context.pursuit, null, 2);
    }
    if (key === 'pwin_score' && context.pwinScore) {
      return JSON.stringify(context.pwinScore, null, 2);
    }
    if (key === 'win_themes' && context.winThemes) {
      return JSON.stringify(context.winThemes, null, 2);
    }
    if (key === 'competitive_positioning' && context.competitivePositioning) {
      return JSON.stringify(context.competitivePositioning, null, 2);
    }
    if (key === 'reasoning_rules' && context.reasoningRules) {
      return JSON.stringify(context.reasoningRules, null, 2);
    }
    if (key === 'few_shot_examples' && context.fewShotExamples) {
      return context.fewShotExamples.map((ex, i) =>
        `Example ${i + 1} — ${ex.questionCategory}\nVerdict: ${ex.verdict}\nEvidence: ${ex.evidenceSubmitted}\nIdeal Response: ${ex.idealAIResponse}`
      ).join('\n\n---\n\n');
    }
    if (key === 'confidence_model' && context.confidenceModel) {
      return JSON.stringify(context.confidenceModel, null, 2);
    }
    if (context[key] !== undefined) {
      return typeof context[key] === 'string' ? context[key] : JSON.stringify(context[key], null, 2);
    }
    return match; // leave unresolved placeholders
  });

  // Build user message from skill template + input
  // Uses the same named mappings as system prompt, plus input values
  let userMessage = skill.user_prompt || '';
  userMessage = userMessage.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    // Input values first (pursuitId, document, etc.)
    if (input[key] !== undefined) {
      return typeof input[key] === 'string' ? input[key] : JSON.stringify(input[key], null, 2);
    }
    // Named context mappings
    if (key === 'pursuit_context' && context.pursuit) return JSON.stringify(context.pursuit, null, 2);
    if (key === 'pwin_score' && context.pwinScore) return JSON.stringify(context.pwinScore, null, 2);
    if (key === 'win_themes' && context.winThemes) return JSON.stringify(context.winThemes, null, 2);
    if (key === 'competitive_positioning' && context.competitivePositioning) return JSON.stringify(context.competitivePositioning, null, 2);
    // Direct context key lookup
    if (context[key] !== undefined) {
      return typeof context[key] === 'string' ? context[key] : JSON.stringify(context[key], null, 2);
    }
    return match;
  });

  return { systemPrompt, userMessage };
}

// ---------------------------------------------------------------------------
// Claude API call
// ---------------------------------------------------------------------------

async function callClaude(systemPrompt, messages, tools, model) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY environment variable is required to execute skills');
  }

  // messages can be a string (first turn) or array (multi-turn)
  const msgArray = typeof messages === 'string'
    ? [{ role: 'user', content: messages }]
    : Array.isArray(messages) ? messages : [{ role: 'user', content: String(messages) }];

  const body = {
    model: model || 'claude-sonnet-4-20250514',
    max_tokens: 16384,
    system: systemPrompt,
    messages: msgArray,
  };

  // If tools are defined, include them for structured output
  if (tools && tools.length > 0) {
    body.tools = tools;
    body.tool_choice = { type: 'auto' };
  }

  // Retry with exponential backoff for rate limits
  let response;
  for (let attempt = 0; attempt < 3; attempt++) {
    if (attempt > 0) {
      const delay = Math.pow(2, attempt) * 30000; // 30s, 60s
      console.error(`[skill-runner] Rate limited, waiting ${delay/1000}s before retry ${attempt + 1}...`);
      await new Promise(r => setTimeout(r, delay));
    }

    response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'anthropic-beta': 'web-search-2025-03-05',
      },
      body: JSON.stringify(body),
    });

    if (response.ok) break;

    if (response.status === 429 && attempt < 2) {
      continue; // retry after backoff
    }

    const errText = await response.text();
    throw new Error(`Claude API error ${response.status}: ${errText}`);
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// Tool definitions for Claude (write-back tools)
// ---------------------------------------------------------------------------

function buildClaudeTools(skill, depthMode) {
  const writeTools = skill.write_tools || [];
  const researchTools = skill.research_tools || [];
  if (writeTools.length === 0 && researchTools.length === 0) return [];

  // Scale web search budget to depth mode to stay within rate limits
  const searchBudget = depthMode === 'snapshot' ? 4 : depthMode === 'standard' ? 8 : 15;

  // Research tools — server-side tools handled by the Anthropic API
  const researchToolDefs = {
    web_search: {
      type: 'web_search_20250305',
      name: 'web_search',
      max_uses: searchBudget,
    },
  };

  // Map skill tool names to Claude tool definitions (write tools)
  const toolDefs = {
    batch_create_response_sections: {
      name: 'batch_create_response_sections',
      description: 'Create multiple response sections from ITT extraction',
      input_schema: {
        type: 'object',
        properties: {
          sections: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                reference: { type: 'string' },
                sectionNumber: { type: 'string' },
                questionText: { type: 'string' },
                evaluationCategory: { type: 'string' },
                evaluationMaxScore: { type: 'number' },
                hurdleScore: { type: 'number' },
                wordLimit: { type: 'number' },
                responseType: { type: 'string' },
              },
              required: ['reference'],
            },
          },
        },
        required: ['sections'],
      },
    },
    create_evaluation_framework: {
      name: 'create_evaluation_framework',
      description: 'Create evaluation framework from ITT extraction',
      input_schema: {
        type: 'object',
        properties: {
          totalScore: { type: 'number' },
          qualityWeight: { type: 'number' },
          priceWeight: { type: 'number' },
          categories: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                name: { type: 'string' },
                weight: { type: 'number' },
                maxScore: { type: 'number' },
              },
            },
          },
        },
      },
    },
    create_itt_document: {
      name: 'create_itt_document',
      description: 'Create an ITT document record',
      input_schema: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          volumeType: { type: 'string' },
          parsedStatus: { type: 'string', enum: ['pending', 'parsed', 'failed'] },
          pageCount: { type: 'number' },
          sections: { type: 'array', items: { type: 'string' } },
        },
        required: ['name'],
      },
    },
    update_bid_procurement_context: {
      name: 'update_bid_procurement_context',
      description: 'Update bid procurement context fields',
      input_schema: {
        type: 'object',
        properties: {
          procurementRoute: { type: 'string' },
          frameworkReference: { type: 'string' },
          lotNumber: { type: 'string' },
          contractType: { type: 'string' },
          estimatedContractValue: { type: 'number' },
          submissionMethod: { type: 'string' },
          evaluationModel: { type: 'string' },
        },
      },
    },
    ingest_scoring_scheme: {
      name: 'ingest_scoring_scheme',
      description: 'Ingest client scoring/marking scheme',
      input_schema: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          levels: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                score: { type: 'number' },
                label: { type: 'string' },
                description: { type: 'string' },
              },
            },
          },
          maxScore: { type: 'number' },
          passMark: { type: 'number' },
        },
      },
    },
    update_activity_insight: {
      name: 'update_activity_insight',
      description: 'Append AI insight to an activity',
      input_schema: {
        type: 'object',
        properties: {
          activityCode: { type: 'string' },
          insight: {
            type: 'object',
            properties: {
              type: { type: 'string' },
              summary: { type: 'string' },
              detail: { type: 'string' },
              severity: { type: 'string', enum: ['info', 'warning', 'critical'] },
              recommendations: { type: 'array', items: { type: 'string' } },
            },
            required: ['type', 'summary'],
          },
        },
        required: ['activityCode', 'insight'],
      },
    },
    add_risk_flag: {
      name: 'add_risk_flag',
      description: 'Flag a risk on an activity',
      input_schema: {
        type: 'object',
        properties: {
          activityCode: { type: 'string' },
          risk: {
            type: 'object',
            properties: {
              description: { type: 'string' },
              probability: { type: 'string', enum: ['low', 'medium', 'high'] },
              impact: { type: 'string', enum: ['low', 'medium', 'high'] },
              mitigation: { type: 'string' },
            },
            required: ['description'],
          },
        },
        required: ['activityCode', 'risk'],
      },
    },
    create_standup_action: {
      name: 'create_standup_action',
      description: 'Create a standup action',
      input_schema: {
        type: 'object',
        properties: {
          description: { type: 'string' },
          parentActivityCode: { type: 'string' },
          priority: { type: 'string', enum: ['low', 'medium', 'high', 'critical'] },
          suggestedOwner: { type: 'string' },
          suggestedDueDate: { type: 'string' },
        },
        required: ['description'],
      },
    },
    create_compliance_coverage_insight: {
      name: 'create_compliance_coverage_insight',
      description: 'Create compliance coverage insight',
      input_schema: {
        type: 'object',
        properties: {
          type: { type: 'string' },
          summary: { type: 'string' },
          coveragePct: { type: 'number' },
          gaps: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                requirement: { type: 'string' },
                status: { type: 'string' },
                recommendation: { type: 'string' },
              },
            },
          },
        },
        required: ['type', 'summary'],
      },
    },
    generate_report_output: {
      name: 'generate_report_output',
      description: 'Generate and store a report',
      input_schema: {
        type: 'object',
        properties: {
          reportType: { type: 'string' },
          content: { type: 'string' },
        },
        required: ['reportType', 'content'],
      },
    },
    store_intelligence_dossier: {
      name: 'store_intelligence_dossier',
      description: 'Store a v2 supplier intelligence dossier as structured JSON in the platform library. The dossier object must conform to supplier-dossier-schema v2. The renderer will produce the HTML report from this data.',
      input_schema: {
        type: 'object',
        properties: {
          dossier: {
            type: 'object',
            description: 'The complete v2 dossier object conforming to supplier-dossier-schema.json. Must include meta (with supplierName, slug), identity, scores, serviceLineProfile, financialTrajectory, contracts, riskExposureProfile, evidenceRegister, and executiveSummary.',
          },
        },
        required: ['dossier'],
      },
    },
    store_client_profile: {
      name: 'store_client_profile',
      description: 'Store a v2 buyer intelligence dossier as structured JSON in the platform library. The profile object must conform to client-profile-schema v2. The renderer will produce the HTML report from this data.',
      input_schema: {
        type: 'object',
        properties: {
          profile: {
            type: 'object',
            description: 'The complete v2 buyer profile object conforming to client-profile-schema.json. Must include meta (with buyerName, slug), buyerSnapshot, organisationContext, procurementBehaviour, supplierEcosystem, and sourceRegister.',
          },
        },
        required: ['profile'],
      },
    },
    store_sector_dossier: {
      name: 'store_sector_dossier',
      description: 'Store a v1 sector intelligence dossier as structured JSON in the platform library. The dossier object must conform to sector-intelligence-dossier v1. Includes the pursuit handoff payload for downstream consumption.',
      input_schema: {
        type: 'object',
        properties: {
          dossier: {
            type: 'object',
            description: 'The complete v1 sector dossier object. Must include meta, sectorIdentity, sectorAnatomy, financialAndDemandContext, procurementBehaviour, demandDrivers, buyerArchetypes, opportunityArchetypes, competitiveLandscape, winImplications, forwardSignalModel, evidenceRegister, scores, and pursuitHandoff.',
          },
        },
        required: ['dossier'],
      },
    },
  };

  const tools = [
    ...writeTools.filter(name => toolDefs[name]).map(name => toolDefs[name]),
    ...researchTools.filter(name => researchToolDefs[name]).map(name => researchToolDefs[name]),
  ];
  return tools;
}

// ---------------------------------------------------------------------------
// Write-back execution — process Claude's tool_use blocks
// ---------------------------------------------------------------------------

async function executeWriteBacks(skill, pursuitId, claudeResponse) {
  const results = [];

  for (const block of claudeResponse.content || []) {
    if (block.type !== 'tool_use') continue;

    const { name, input } = block;
    try {
      const result = await executeToolCall(name, pursuitId, input);
      results.push({ tool: name, success: true, result });
    } catch (err) {
      results.push({ tool: name, success: false, error: err.message });
    }
  }

  return results;
}

async function executeToolCall(toolName, pursuitId, input) {
  // Server-side tools (web_search) are handled by the Anthropic API —
  // they never reach this function. Only write tools route here.
  switch (toolName) {
    case 'batch_create_response_sections': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      data.responseSections = data.responseSections || [];
      const { randomUUID } = await import('node:crypto');
      const now = new Date().toISOString();
      const created = input.sections.map(s => ({ id: randomUUID(), ...s, createdBy: 'ai_ingestion', createdAt: now }));
      data.responseSections.push(...created);
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { created: created.length };
    }
    case 'create_evaluation_framework': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      const { randomUUID } = await import('node:crypto');
      data.evaluationFramework = { id: randomUUID(), ...input, createdBy: 'ai_ingestion', createdAt: new Date().toISOString() };
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { created: true };
    }
    case 'create_itt_document': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      data.ittDocuments = data.ittDocuments || [];
      const { randomUUID } = await import('node:crypto');
      const doc = { id: randomUUID(), ...input, createdBy: 'ai_ingestion', createdAt: new Date().toISOString() };
      data.ittDocuments.push(doc);
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { created: true, documentId: doc.id };
    }
    case 'update_bid_procurement_context': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      data.procurementContext = { ...(data.procurementContext || {}), ...input, updatedAt: new Date().toISOString() };
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { updated: true };
    }
    case 'ingest_scoring_scheme': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      data.clientScoringScheme = { ...input, ingestedAt: new Date().toISOString(), createdBy: 'ai_ingestion' };
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { ingested: true };
    }
    case 'update_activity_insight': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      const activity = (data.activities || []).find(a => a.activityCode === input.activityCode);
      if (!activity) throw new Error(`Activity ${input.activityCode} not found`);
      const { randomUUID } = await import('node:crypto');
      activity.aiInsights = activity.aiInsights || [];
      activity.aiInsights.push({ id: randomUUID(), ...input.insight, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { appended: true };
    }
    case 'add_risk_flag': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      const activity = (data.activities || []).find(a => a.activityCode === input.activityCode);
      if (!activity) throw new Error(`Activity ${input.activityCode} not found`);
      const { randomUUID } = await import('node:crypto');
      const risk = { id: randomUUID(), ...input.risk, activityCode: input.activityCode, source: 'ai_generated', createdAt: new Date().toISOString() };
      activity.risks = activity.risks || [];
      activity.risks.push(risk);
      data.risks = data.risks || [];
      data.risks.push(risk);
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { added: true, riskId: risk.id };
    }
    case 'create_standup_action': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      data.standupActions = data.standupActions || [];
      const { randomUUID } = await import('node:crypto');
      const action = { id: randomUUID(), ...input, source: 'ai_generated', status: 'open', createdAt: new Date().toISOString() };
      data.standupActions.push(action);
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { created: true, actionId: action.id };
    }
    case 'create_compliance_coverage_insight': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      data.complianceCoverageInsights = data.complianceCoverageInsights || [];
      const { randomUUID } = await import('node:crypto');
      data.complianceCoverageInsights.push({ id: randomUUID(), ...input, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { created: true };
    }
    case 'generate_report_output': {
      const data = await store.getProductData(pursuitId, 'bid_execution') || {};
      data.reports = data.reports || [];
      const { randomUUID } = await import('node:crypto');
      data.reports.push({ id: randomUUID(), type: input.reportType, content: input.content, generatedAt: new Date().toISOString() });
      await store.saveProductData(pursuitId, 'bid_execution', data);
      return { generated: true };
    }
    case 'store_intelligence_dossier': {
      const dossier = input.dossier;
      const slug = dossier.meta?.slug || dossier.meta?.supplierName?.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'unknown';
      // v2: store as {slug}/data.json inside reference/suppliers/
      const { writeFile, mkdir } = await import('node:fs/promises');
      const { join } = await import('node:path');
      const dirPath = join(store.DATA_ROOT, 'reference', 'suppliers', slug);
      await mkdir(dirPath, { recursive: true });
      const dataPath = join(dirPath, 'data.json');
      await writeFile(dataPath, JSON.stringify(dossier, null, 2), 'utf-8');
      return { stored: true, path: `reference/suppliers/${slug}/data.json` };
    }
    case 'store_client_profile': {
      const profile = input.profile;
      const slug = profile.meta?.slug || profile.meta?.buyerName?.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'unknown';
      const { writeFile, mkdir } = await import('node:fs/promises');
      const { join } = await import('node:path');
      const dirPath = join(store.DATA_ROOT, 'reference', 'clients', slug);
      await mkdir(dirPath, { recursive: true });
      const dataPath = join(dirPath, 'data.json');
      await writeFile(dataPath, JSON.stringify(profile, null, 2), 'utf-8');
      return { stored: true, path: `reference/clients/${slug}/data.json` };
    }
    case 'store_sector_dossier': {
      const dossier = input.dossier;
      const slug = dossier.meta?.sectorName?.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'unknown';
      const jurisdiction = (dossier.meta?.jurisdiction || 'uk').toLowerCase().replace(/[^a-z0-9]+/g, '-');
      const folder = `${slug}-${jurisdiction}`;
      const { writeFile, mkdir } = await import('node:fs/promises');
      const { join } = await import('node:path');
      const dirPath = join(store.DATA_ROOT, 'reference', 'sectors', folder);
      await mkdir(dirPath, { recursive: true });
      const dataPath = join(dirPath, 'data.json');
      await writeFile(dataPath, JSON.stringify(dossier, null, 2), 'utf-8');
      return { stored: true, path: `reference/sectors/${folder}/data.json` };
    }
    default:
      throw new Error(`Unknown tool: ${toolName}`);
  }
}

// ---------------------------------------------------------------------------
// Main execution
// ---------------------------------------------------------------------------

async function executeSkill(skillId, input) {
  const skill = await loadSkill(skillId);

  // Validate required input
  for (const req of skill.input?.required || []) {
    if (input[req] === undefined) {
      throw new Error(`Missing required input: ${req}`);
    }
  }

  // Gather context
  const context = await gatherContext(skill, input);

  // Assemble prompt
  const { systemPrompt, userMessage } = assemblePrompt(skill, context, input);

  // Build Claude tools from skill config (depth-aware search budget)
  const tools = buildClaudeTools(skill, input?.depthMode);

  // If no API key, return the assembled prompt (dry run)
  if (!process.env.ANTHROPIC_API_KEY) {
    return {
      dryRun: true,
      skillId,
      systemPrompt,
      userMessage,
      toolCount: tools.length,
      contextKeys: Object.keys(context),
    };
  }

  // Multi-turn tool use loop: call Claude, execute tool calls, send results back, repeat
  const allWriteResults = [];
  const allTextBlocks = [];
  let messages = [{ role: 'user', content: userMessage }];
  let totalUsage = { input_tokens: 0, output_tokens: 0 };
  let lastResponse = null;
  const MAX_TURNS = 10;

  // Allow model override from input (e.g. for rate limit workaround)
  const modelOverride = input._model || skill.model;

  for (let turn = 0; turn < MAX_TURNS; turn++) {
    // Rate limit protection: wait between turns
    if (turn > 0) await new Promise(r => setTimeout(r, 2000));

    const response = await callClaude(systemPrompt, messages, tools, modelOverride);
    lastResponse = response;
    totalUsage.input_tokens += response.usage?.input_tokens || 0;
    totalUsage.output_tokens += response.usage?.output_tokens || 0;

    // Collect text blocks
    for (const block of response.content || []) {
      if (block.type === 'text') allTextBlocks.push(block.text);
    }

    // If no tool use, we're done
    if (response.stop_reason !== 'tool_use') break;

    // Server-side tools (web_search) are executed by the Anthropic API
    // and their results appear as content blocks in the response. We only
    // need to execute our own write tools (store_intelligence_dossier etc).
    // If the only tool_use blocks are server-side, the API handles them
    // internally and stop_reason will be 'tool_use' to continue the loop.

    const toolResults = [];
    let hasClientToolCalls = false;
    for (const block of response.content || []) {
      if (block.type !== 'tool_use') continue;
      // Server-side tools are identified by their type prefix or by not
      // being in our write tools list. The API returns server tool results
      // automatically — we only execute client-side write tools.
      const isServerTool = block.name === 'web_search';
      if (isServerTool) continue; // API handles these

      hasClientToolCalls = true;
      const { id, name, input: toolInput } = block;
      try {
        const result = await executeToolCall(name, input.pursuitId, toolInput);
        allWriteResults.push({ tool: name, success: true, result });
        toolResults.push({ type: 'tool_result', tool_use_id: id, content: JSON.stringify(result) });
      } catch (err) {
        allWriteResults.push({ tool: name, success: false, error: err.message });
        toolResults.push({ type: 'tool_result', tool_use_id: id, content: `Error: ${err.message}`, is_error: true });
      }
    }

    // Add assistant response + tool results to conversation for next turn
    messages = [
      ...messages,
      { role: 'assistant', content: response.content },
      ...(toolResults.length > 0 ? [{ role: 'user', content: toolResults }] : []),
    ];
  }

  return {
    skillId,
    model: lastResponse?.model,
    stopReason: lastResponse?.stop_reason,
    text: allTextBlocks.join('\n'),
    writeResults: allWriteResults,
    usage: totalUsage,
  };
}

export { loadSkill, listSkills, executeSkill, gatherContext, assemblePrompt };
