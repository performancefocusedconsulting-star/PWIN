/**
 * PWIN Platform — JSON File Store
 *
 * Reads and writes JSON files on disk under ~/.pwin/
 * Each pursuit gets its own directory with shared.json + product files.
 * Platform-level data (sector knowledge, reasoning rules) lives in platform/.
 */

import { readFile, writeFile, mkdir, readdir, rename, stat } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { homedir } from 'node:os';
import { randomUUID } from 'node:crypto';

const DATA_ROOT = join(homedir(), '.pwin');

// --- Low-level file operations ---

async function ensureDir(dirPath) {
  await mkdir(dirPath, { recursive: true });
}

async function readJSON(filePath) {
  try {
    const raw = await readFile(filePath, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

async function writeJSON(filePath, data) {
  await ensureDir(dirname(filePath));
  await writeFile(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

// --- Paths ---

function pursuitDir(pursuitId) {
  return join(DATA_ROOT, 'pursuits', pursuitId);
}

function sharedPath(pursuitId) {
  return join(pursuitDir(pursuitId), 'shared.json');
}

function productPath(pursuitId, product) {
  const allowed = ['qualify', 'bid_execution', 'win_strategy'];
  if (!allowed.includes(product)) throw new Error(`Unknown product: ${product}`);
  return join(pursuitDir(pursuitId), `${product}.json`);
}

function platformPath(filename) {
  return join(DATA_ROOT, 'platform', filename);
}

function referencePath(type, id) {
  return join(DATA_ROOT, 'reference', type, `${id}.json`);
}

function exportPath(pursuitId, date) {
  const dateStr = date || new Date().toISOString().slice(0, 10);
  return join(DATA_ROOT, 'exports', `${pursuitId}_${dateStr}.json`);
}

// --- Pursuit CRUD ---

async function listPursuits() {
  const dir = join(DATA_ROOT, 'pursuits');
  await ensureDir(dir);
  const entries = await readdir(dir, { withFileTypes: true });
  const pursuits = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const shared = await readJSON(join(dir, entry.name, 'shared.json'));
    if (!shared?.pursuit) continue;
    const p = shared.pursuit;
    pursuits.push({
      id: p.id,
      client: p.client,
      opportunity: p.opportunity,
      status: p.status,
      pwinScore: shared.pwinScore?.overall ?? null,
    });
  }
  return pursuits;
}

async function createPursuit(data) {
  const id = randomUUID();
  const now = new Date().toISOString();
  const shared = {
    pursuit: {
      id,
      client: data.client || '',
      opportunity: data.opportunity || '',
      sector: data.sector || null,
      tcv: data.tcv || null,
      acv: data.acv || null,
      opportunityType: data.opportunityType || null,
      procurementRoute: data.procurementRoute || null,
      incumbentStatus: data.incumbentStatus || null,
      submissionDeadline: data.submissionDeadline || null,
      contractDurationMonths: data.contractDurationMonths || null,
      status: data.status || 'qualifying',
      createdAt: now,
      updatedAt: now,
      createdBy: data.createdBy || 'qualify',
    },
    pwinScore: null,
    winThemes: [],
    competitivePositioning: null,
    stakeholderMap: [],
    buyerValues: [],
    clientIntelligence: null,
    capturePlan: null,
  };
  await writeJSON(sharedPath(id), shared);
  return shared;
}

async function getPursuit(pursuitId) {
  return readJSON(sharedPath(pursuitId));
}

async function updatePursuit(pursuitId, data) {
  const existing = await readJSON(sharedPath(pursuitId));
  if (!existing) return null;
  const merged = {
    ...existing,
    pursuit: { ...existing.pursuit, ...data, updatedAt: new Date().toISOString() },
  };
  await writeJSON(sharedPath(pursuitId), merged);
  return merged;
}

async function archivePursuit(pursuitId) {
  const dir = pursuitDir(pursuitId);
  try {
    await stat(dir);
  } catch {
    return null;
  }
  const shared = await readJSON(sharedPath(pursuitId));
  const expPath = exportPath(pursuitId);
  await ensureDir(dirname(expPath));

  // Export full pursuit data
  const qualify = await readJSON(productPath(pursuitId, 'qualify'));
  const bidExec = await readJSON(productPath(pursuitId, 'bid_execution'));
  const winStrat = await readJSON(productPath(pursuitId, 'win_strategy'));
  const archive = { shared, qualify, bid_execution: bidExec, win_strategy: winStrat, archivedAt: new Date().toISOString() };
  await writeJSON(expPath, archive);

  // Rename pursuit directory to mark archived
  await rename(dir, `${dir}__archived`);
  return archive;
}

// --- Product data ---

async function getProductData(pursuitId, product) {
  return readJSON(productPath(pursuitId, product));
}

async function saveProductData(pursuitId, product, data) {
  await writeJSON(productPath(pursuitId, product), data);
  return data;
}

// --- Shared entity accessors ---

async function getSharedEntity(pursuitId, entity) {
  const shared = await readJSON(sharedPath(pursuitId));
  if (!shared) return undefined; // pursuit does not exist
  return shared[entity] ?? null; // entity exists but value is null
}

async function updateSharedEntity(pursuitId, entity, data) {
  const shared = await readJSON(sharedPath(pursuitId));
  if (!shared) return null;
  shared[entity] = data;
  shared.pursuit.updatedAt = new Date().toISOString();
  await writeJSON(sharedPath(pursuitId), shared);
  return data;
}

// --- Platform data ---

async function getPlatformData(filename) {
  return readJSON(platformPath(filename));
}

async function savePlatformData(filename, data) {
  await writeJSON(platformPath(filename), data);
  return data;
}

// --- Reference data ---

async function getReferenceData(type, id) {
  return readJSON(referencePath(type, id));
}

async function saveReferenceData(type, id, data) {
  await writeJSON(referencePath(type, id), data);
  return data;
}

async function listReferenceData(type) {
  const dir = join(DATA_ROOT, 'reference', type);
  await ensureDir(dir);
  const entries = await readdir(dir);
  return entries.filter(f => f.endsWith('.json')).map(f => f.replace('.json', ''));
}

// --- Export/Import ---

async function exportPursuit(pursuitId) {
  const shared = await readJSON(sharedPath(pursuitId));
  if (!shared) return null;
  const qualify = await readJSON(productPath(pursuitId, 'qualify'));
  const bidExec = await readJSON(productPath(pursuitId, 'bid_execution'));
  const winStrat = await readJSON(productPath(pursuitId, 'win_strategy'));
  const exp = { shared, qualify, bid_execution: bidExec, win_strategy: winStrat, exportedAt: new Date().toISOString() };
  const expFile = exportPath(pursuitId);
  await writeJSON(expFile, exp);
  return { path: expFile, data: exp };
}

async function importPursuit(data) {
  if (!data?.shared?.pursuit?.id) throw new Error('Import data must include shared.pursuit.id');
  const id = data.shared.pursuit.id;
  await writeJSON(sharedPath(id), data.shared);
  if (data.qualify) await writeJSON(productPath(id, 'qualify'), data.qualify);
  if (data.bid_execution) await writeJSON(productPath(id, 'bid_execution'), data.bid_execution);
  if (data.win_strategy) await writeJSON(productPath(id, 'win_strategy'), data.win_strategy);
  return id;
}

export {
  DATA_ROOT,
  listPursuits,
  createPursuit,
  getPursuit,
  updatePursuit,
  archivePursuit,
  getProductData,
  saveProductData,
  getSharedEntity,
  updateSharedEntity,
  getPlatformData,
  savePlatformData,
  getReferenceData,
  saveReferenceData,
  listReferenceData,
  exportPursuit,
  importPursuit,
};
