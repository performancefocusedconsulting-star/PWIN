/**
 * PWIN Platform — Data API (HTTP)
 *
 * Serves each HTML product app with load/save endpoints.
 * Replaces localStorage as the persistence layer.
 * Runs on localhost:3456 by default.
 */

import { createServer } from 'node:http';
import * as store from './store.js';

const PORT = parseInt(process.env.PWIN_PORT || '3456', 10);

// --- HTTP helpers ---

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function json(res, status, data) {
  cors(res);
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

function notFound(res, msg) {
  json(res, 404, { error: msg || 'Not found' });
}

function badRequest(res, msg) {
  json(res, 400, { error: msg || 'Bad request' });
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString();
  if (!raw) return null;
  try { return JSON.parse(raw); }
  catch { return null; }
}

// --- Route matching ---

function match(method, url, pattern) {
  if (method === 'OPTIONS') return null;
  const parts = url.split('?')[0].split('/').filter(Boolean);
  const patParts = pattern.split('/').filter(Boolean);
  if (parts.length !== patParts.length) return null;
  const params = {};
  for (let i = 0; i < patParts.length; i++) {
    if (patParts[i].startsWith('{') && patParts[i].endsWith('}')) {
      params[patParts[i].slice(1, -1)] = parts[i];
    } else if (patParts[i] !== parts[i]) {
      return null;
    }
  }
  return params;
}

// --- Request handler ---

async function handleRequest(req, res) {
  const { method, url } = req;

  // CORS preflight
  if (method === 'OPTIONS') {
    cors(res);
    res.writeHead(204);
    res.end();
    return;
  }

  try {
    let params;

    // --- Health ---
    if (method === 'GET' && (params = match(method, url, '/api/health')) !== null) {
      return json(res, 200, { status: 'ok', version: '0.1.0', dataRoot: store.DATA_ROOT });
    }

    // --- Pursuit Management ---

    // GET /api/pursuits
    if (method === 'GET' && (params = match(method, url, '/api/pursuits')) !== null) {
      const pursuits = await store.listPursuits();
      return json(res, 200, pursuits);
    }

    // POST /api/pursuits
    if (method === 'POST' && (params = match(method, url, '/api/pursuits')) !== null) {
      const body = await readBody(req);
      if (!body) return badRequest(res, 'Request body required');
      const shared = await store.createPursuit(body);
      return json(res, 201, shared);
    }

    // GET /api/pursuits/{pursuitId}
    if (method === 'GET' && (params = match(method, url, '/api/pursuits/{pursuitId}')) !== null) {
      const data = await store.getPursuit(params.pursuitId);
      if (!data) return notFound(res, `Pursuit ${params.pursuitId} not found`);
      return json(res, 200, data);
    }

    // PUT /api/pursuits/{pursuitId}
    if (method === 'PUT' && (params = match(method, url, '/api/pursuits/{pursuitId}')) !== null) {
      const body = await readBody(req);
      if (!body) return badRequest(res, 'Request body required');
      const data = await store.updatePursuit(params.pursuitId, body);
      if (!data) return notFound(res, `Pursuit ${params.pursuitId} not found`);
      return json(res, 200, data);
    }

    // DELETE /api/pursuits/{pursuitId}
    if (method === 'DELETE' && (params = match(method, url, '/api/pursuits/{pursuitId}')) !== null) {
      const data = await store.archivePursuit(params.pursuitId);
      if (!data) return notFound(res, `Pursuit ${params.pursuitId} not found`);
      return json(res, 200, { archived: true, pursuitId: params.pursuitId });
    }

    // --- Product Data ---

    // GET /api/pursuits/{pursuitId}/{product}
    if (method === 'GET' && (params = match(method, url, '/api/pursuits/{pursuitId}/{product}')) !== null) {
      const productMap = { 'qualify': 'qualify', 'bid-execution': 'bid_execution', 'win-strategy': 'win_strategy' };
      const product = productMap[params.product];
      if (!product) return notFound(res);
      const data = await store.getProductData(params.pursuitId, product);
      return json(res, 200, data || {});
    }

    // PUT /api/pursuits/{pursuitId}/{product}
    if (method === 'PUT' && (params = match(method, url, '/api/pursuits/{pursuitId}/{product}')) !== null) {
      const productMap = { 'qualify': 'qualify', 'bid-execution': 'bid_execution', 'win-strategy': 'win_strategy' };
      const product = productMap[params.product];
      if (!product) return notFound(res);
      const body = await readBody(req);
      if (!body) return badRequest(res, 'Request body required');

      // Sync rules: qualify context → shared.json pursuit entity
      if (product === 'qualify' && body.context) {
        await store.updatePursuit(params.pursuitId, body.context);
      }

      const data = await store.saveProductData(params.pursuitId, product, body);
      return json(res, 200, data);
    }

    // --- Shared Entities ---

    const sharedEntities = {
      'pwin-score': 'pwinScore',
      'win-themes': 'winThemes',
      'stakeholders': 'stakeholderMap',
      'competitors': 'competitivePositioning',
      'buyer-values': 'buyerValues',
      'client-intel': 'clientIntelligence',
      'capture-plan': 'capturePlan',
    };

    // GET /api/pursuits/{pursuitId}/shared/{entity}
    if (method === 'GET') {
      const sharedMatch = url.split('?')[0].match(/^\/api\/pursuits\/([^/]+)\/shared\/([^/]+)$/);
      if (sharedMatch) {
        const [, pursuitId, entitySlug] = sharedMatch;
        const entityKey = sharedEntities[entitySlug];
        if (!entityKey) return notFound(res, `Unknown shared entity: ${entitySlug}`);
        const data = await store.getSharedEntity(pursuitId, entityKey);
        if (data === undefined) return notFound(res, `Pursuit ${pursuitId} not found`);
        return json(res, 200, data);
      }
    }

    // --- Reference Data ---

    // GET /api/reference/client-profiles
    if (method === 'GET' && (params = match(method, url, '/api/reference/client-profiles')) !== null) {
      const ids = await store.listReferenceData('client_profiles');
      return json(res, 200, ids);
    }

    // GET /api/reference/client-profiles/{clientId}
    if (method === 'GET' && (params = match(method, url, '/api/reference/client-profiles/{clientId}')) !== null) {
      const data = await store.getReferenceData('client_profiles', params.clientId);
      if (!data) return notFound(res);
      return json(res, 200, data);
    }

    // GET /api/reference/competitor-dossiers
    if (method === 'GET' && (params = match(method, url, '/api/reference/competitor-dossiers')) !== null) {
      const ids = await store.listReferenceData('competitor_dossiers');
      return json(res, 200, ids);
    }

    // GET /api/reference/competitor-dossiers/{competitorId}
    if (method === 'GET' && (params = match(method, url, '/api/reference/competitor-dossiers/{competitorId}')) !== null) {
      const data = await store.getReferenceData('competitor_dossiers', params.competitorId);
      if (!data) return notFound(res);
      return json(res, 200, data);
    }

    // GET /api/reference/sector-knowledge/{sector}
    if (method === 'GET' && (params = match(method, url, '/api/reference/sector-knowledge/{sector}')) !== null) {
      const data = await store.getPlatformData('sector_knowledge.json');
      if (!data) return json(res, 200, {});
      return json(res, 200, data[params.sector] || {});
    }

    // GET /api/reference/opportunity-types/{type}
    if (method === 'GET' && (params = match(method, url, '/api/reference/opportunity-types/{type}')) !== null) {
      const data = await store.getPlatformData('opportunity_types.json');
      if (!data) return json(res, 200, {});
      return json(res, 200, data[params.type] || {});
    }

    // --- Platform ---

    // GET /api/platform/reasoning-rules
    if (method === 'GET' && (params = match(method, url, '/api/platform/reasoning-rules')) !== null) {
      const data = await store.getPlatformData('reasoning_rules.json');
      return json(res, 200, data || []);
    }

    // GET /api/platform/confidence-model
    if (method === 'GET' && (params = match(method, url, '/api/platform/confidence-model')) !== null) {
      const data = await store.getPlatformData('confidence_model.json');
      return json(res, 200, data || {});
    }

    // --- Import/Export ---

    // POST /api/pursuits/{pursuitId}/export
    if (method === 'POST' && (params = match(method, url, '/api/pursuits/{pursuitId}/export')) !== null) {
      const result = await store.exportPursuit(params.pursuitId);
      if (!result) return notFound(res, `Pursuit ${params.pursuitId} not found`);
      return json(res, 200, { exported: true, path: result.path });
    }

    // POST /api/pursuits/import
    if (method === 'POST' && (params = match(method, url, '/api/pursuits/import')) !== null) {
      const body = await readBody(req);
      if (!body) return badRequest(res, 'Request body required');
      const id = await store.importPursuit(body);
      return json(res, 201, { imported: true, pursuitId: id });
    }

    // --- Fallthrough ---
    notFound(res, `No route: ${method} ${url}`);

  } catch (err) {
    console.error(`[API] Error handling ${method} ${url}:`, err);
    json(res, 500, { error: err.message });
  }
}

// --- Server lifecycle ---

function startAPI() {
  return new Promise((resolve) => {
    const server = createServer(handleRequest);
    server.listen(PORT, () => {
      console.log(`[PWIN Platform] Data API listening on http://localhost:${PORT}`);
      resolve(server);
    });
  });
}

export { startAPI, PORT };
