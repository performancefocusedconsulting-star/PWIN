/**
 * PWIN Platform — Intelligence dossier loader
 *
 * Canonical loader for Agent 2 intelligence dossiers landing at:
 *   ~/.pwin/intel/<type>/<slug>-<artefact>.json
 *
 * Types: buyers, suppliers, sectors, incumbency.
 * Artefact suffix is determined per type by the producing skill convention.
 *
 * If multiple versions exist (e.g. *-dossier.json and *-dossier-v2.json),
 * the most recently modified file wins.
 */

import { readFile, readdir, stat } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

const INTEL_ROOT = join(homedir(), '.pwin', 'intel');

const TYPE_TO_ARTEFACT = {
  buyers: 'dossier',
  suppliers: 'dossier',
  sectors: 'brief',
  incumbency: 'analysis',
};

function slugify(name) {
  return String(name)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

function dossierPath(type, slug) {
  const artefact = TYPE_TO_ARTEFACT[type];
  if (!artefact) throw new Error(`Unknown type: "${type}" — expected one of: ${Object.keys(TYPE_TO_ARTEFACT).join(', ')}`);
  return join(INTEL_ROOT, type, `${slug}-${artefact}.json`);
}

async function findLatestVersion(type, slug) {
  const artefact = TYPE_TO_ARTEFACT[type];
  if (!artefact) throw new Error(`Unknown type: "${type}" — expected one of: ${Object.keys(TYPE_TO_ARTEFACT).join(', ')}`);
  const dir = join(INTEL_ROOT, type);
  let entries;
  try {
    entries = await readdir(dir);
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
  // Match {slug}-{artefact}.json and {slug}-{artefact}-vN.json
  const prefix = `${slug}-${artefact}`;
  const candidates = entries.filter(f =>
    f === `${prefix}.json` ||
    (f.startsWith(`${prefix}-v`) && f.endsWith('.json'))
  );
  if (candidates.length === 0) return null;
  let bestPath = null;
  let bestMtime = -Infinity;
  for (const fname of candidates) {
    const p = join(dir, fname);
    const s = await stat(p);
    if (s.mtimeMs > bestMtime) {
      bestMtime = s.mtimeMs;
      bestPath = p;
    }
  }
  return bestPath;
}

async function getDossier(type, slug) {
  if (!TYPE_TO_ARTEFACT[type]) throw new Error(`Unknown type: "${type}" — expected one of: ${Object.keys(TYPE_TO_ARTEFACT).join(', ')}`);
  const path = await findLatestVersion(type, slug);
  if (!path) return null;
  try {
    const raw = await readFile(path, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

export {
  INTEL_ROOT,
  TYPE_TO_ARTEFACT,
  slugify,
  dossierPath,
  getDossier,
};
