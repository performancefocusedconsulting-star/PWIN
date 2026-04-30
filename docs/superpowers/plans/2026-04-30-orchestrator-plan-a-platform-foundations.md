# Pursuit Orchestration — Plan A: Platform Foundations

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the platform-level lookup tools and skill-runner context-providers needed to load Agent 2 intelligence dossiers (buyer / supplier / sector / incumbency) into any downstream skill or caller. This is the prerequisite layer for the pursuit-to-gate orchestration skill, but is independently useful for Agent 3, Verdict, and the future paid Qualify tier.

**Architecture:** A single new module (`intel-dossiers.js`) becomes the canonical loader for dossiers landing at `~/.pwin/intel/<type>/<slug>-<artefact>.json`. Four new MCP tools register thin wrappers over that loader. The skill-runner's existing context-provider switch is extended with four new cases (`buyer_dossier`, `sector_brief`, `incumbency_analysis`) and one corrective fix (`supplier_dossier` — currently reads from a stale path that the producing skills do not write to).

**Tech Stack:** Node.js (ES modules), `@modelcontextprotocol/sdk`, `zod` for tool schemas (already used at the MCP boundary), `node:fs/promises` for file I/O. Tests follow the existing assertion-counter pattern in `pwin-platform/test/`.

**Spec reference:** [docs/superpowers/specs/2026-04-29-pursuit-orchestration-design.md](../specs/2026-04-29-pursuit-orchestration-design.md), §5 ("Open detail work").

**Stakeholder map deliberately deferred.** The spec lists `get_stakeholder_map` as a fifth tool, but the stakeholder canonical layer has not been built yet (tracked in `wiki/actions/pwin-stakeholder-canonical-layer.md`). Adding a tool whose backing data does not exist would be a placeholder. Plan A therefore covers the four dossier types that the existing Agent 2 skills already produce.

---

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `pwin-platform/src/intel-dossiers.js` | **Create** | Loader: `getDossier(type, slug)`, `slugify(name)`, type → artefact-suffix map |
| `pwin-platform/test/test-intel-dossiers.js` | **Create** | Direct module unit tests; sets up and tears down its own fixtures inside `~/.pwin/intel/` |
| `pwin-platform/src/mcp.js` | **Modify** | Register four new MCP tools after the existing intel block (around line 1722) |
| `pwin-platform/src/skill-runner.js` | **Modify** | Fix `case 'supplier_dossier'` (lines 151–162); add three new cases |
| `pwin-platform/test/test-skills.js` | **Modify** | Add coverage for the four new context items |
| `docs/superpowers/specs/2026-04-29-pursuit-orchestration-design.md` | **Modify** | Strike the four items in §5 that Plan A closes |

---

## Boundary decisions locked in this plan

These are the design refinements §5 of the spec defers to writing-plans. Plan A locks the following:

1. **Canonical dossier path:** `~/.pwin/intel/<type>/<slug>-<artefact>.json`. This matches the convention already used by the producing Agent 2 skills (e.g. `~/.pwin/intel/buyers/home-office-dossier.json`).
2. **Type → artefact-suffix map:** `buyers→dossier`, `suppliers→dossier`, `sectors→brief`, `incumbency→analysis`. If a producing skill uses a different suffix in future, the map is the single point of update.
3. **Slug derivation:** `name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')` — same regex the existing skill-runner uses.
4. **Versioning behaviour:** if multiple versions of the same dossier exist (e.g. `home-office-dossier.json` and `home-office-dossier-v2.json`), the loader returns the file with the most recent `mtime`. This is mtime-deterministic and avoids parsing version numbers out of filenames.
5. **Missing-file behaviour:** the loader returns `null` (matching `store.js`'s `readJSON` convention). MCP tools and skill-runner cases return a structured "not found" payload rather than erroring.
6. **Type identifier convention:** the type identifiers are the directory names under `~/.pwin/intel/` — `buyers`, `suppliers`, `sectors`, `incumbency`. Plural where there's a collection of entities; singular for the analysis layer that's keyed by (supplier, buyer) pairs.

---

## Task 1 — Create the `intel-dossiers` loader module

**Files:**
- Create: `pwin-platform/src/intel-dossiers.js`
- Create: `pwin-platform/test/test-intel-dossiers.js`

The test sets up and tears down its own fixture files inside `~/.pwin/intel/` using a unique slug (`test-buyer-loader-fixture`) that won't collide with real dossiers.

- [ ] **Step 1.1: Write the failing test**

Create file `pwin-platform/test/test-intel-dossiers.js`:

```javascript
/**
 * PWIN Platform — intel-dossiers loader tests
 *
 * Run: node test/test-intel-dossiers.js
 */
import { getDossier, slugify, dossierPath } from '../src/intel-dossiers.js';
import { writeFile, mkdir, rm, utimes } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

let passed = 0, failed = 0;
function check(label, condition, detail) {
  if (condition) { passed++; console.log(`  PASS ${label}`); }
  else           { failed++; console.error(`  FAIL ${label}`, detail !== undefined ? `(got: ${JSON.stringify(detail)})` : ''); }
}

const FIXTURE_ROOT = join(homedir(), '.pwin', 'intel');
const TEST_BUYER_FILE = join(FIXTURE_ROOT, 'buyers', 'test-buyer-loader-fixture-dossier.json');
const TEST_BUYER_FILE_V2 = join(FIXTURE_ROOT, 'buyers', 'test-buyer-loader-fixture-dossier-v2.json');

async function setup() {
  await mkdir(join(FIXTURE_ROOT, 'buyers'), { recursive: true });
  await writeFile(TEST_BUYER_FILE, JSON.stringify({ meta: { version: '1.0' } }));
}

async function teardown() {
  await rm(TEST_BUYER_FILE, { force: true });
  await rm(TEST_BUYER_FILE_V2, { force: true });
}

console.log('\n=== intel-dossiers loader ===\n');

// slugify
check('slugify lowercases and kebabs', slugify('Home Office') === 'home-office');
check('slugify strips punctuation', slugify('M&S Defence!') === 'm-s-defence');
check('slugify trims leading/trailing dashes', slugify('  -Foo Bar-  ') === 'foo-bar');

// dossierPath
check('dossierPath builds the expected path',
  dossierPath('buyers', 'home-office').endsWith(join('intel', 'buyers', 'home-office-dossier.json')));
check('dossierPath uses "brief" for sectors',
  dossierPath('sectors', 'defence').endsWith('defence-brief.json'));
check('dossierPath uses "analysis" for incumbency',
  dossierPath('incumbency', 'serco-mod').endsWith('serco-mod-analysis.json'));

// getDossier — happy path
await setup();
const dossier = await getDossier('buyers', 'test-buyer-loader-fixture');
check('getDossier returns parsed JSON', dossier?.meta?.version === '1.0', dossier);

// getDossier — missing file
const missing = await getDossier('buyers', 'this-buyer-does-not-exist-123456');
check('getDossier returns null for missing file', missing === null);

// getDossier — versioned file: prefer the most recently modified
await writeFile(TEST_BUYER_FILE_V2, JSON.stringify({ meta: { version: '2.0' } }));
// touch v2 to be newer
const future = new Date(Date.now() + 1000);
await utimes(TEST_BUYER_FILE_V2, future, future);
const versioned = await getDossier('buyers', 'test-buyer-loader-fixture');
check('getDossier prefers latest mtime when multiple versions exist',
  versioned?.meta?.version === '2.0', versioned?.meta?.version);

// getDossier — unknown type errors clearly
try {
  await getDossier('made-up-type', 'whatever');
  check('getDossier rejects unknown type', false, 'expected throw');
} catch (err) {
  check('getDossier rejects unknown type', /unknown type/i.test(err.message), err.message);
}

await teardown();

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed ? 1 : 0);
```

- [ ] **Step 1.2: Run the test, confirm it fails**

```bash
cd pwin-platform && node test/test-intel-dossiers.js
```

Expected: fails with `Cannot find module '../src/intel-dossiers.js'`.

- [ ] **Step 1.3: Implement the loader module**

Create file `pwin-platform/src/intel-dossiers.js`:

```javascript
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
  if (!artefact) throw new Error(`Unknown intelligence type: ${type}`);
  return join(INTEL_ROOT, type, `${slug}-${artefact}.json`);
}

async function findLatestVersion(type, slug) {
  const artefact = TYPE_TO_ARTEFACT[type];
  if (!artefact) throw new Error(`Unknown intelligence type: ${type}`);
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
  if (!TYPE_TO_ARTEFACT[type]) throw new Error(`Unknown intelligence type: ${type}`);
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
```

- [ ] **Step 1.4: Re-run the test, confirm it passes**

```bash
cd pwin-platform && node test/test-intel-dossiers.js
```

Expected: `10 passed, 0 failed`.

- [ ] **Step 1.5: Verify against a real dossier on disk**

```bash
cd pwin-platform && node -e "import('./src/intel-dossiers.js').then(async m => { const d = await m.getDossier('buyers', 'home-office'); console.log('buyer:', d?.meta?.buyerName, 'version:', d?.meta?.version); })"
```

Expected: `buyer: Home Office version: 2.4` (or whatever the latest version on disk is).

If this prints `buyer: undefined`, the file naming convention on disk does not match the artefact map. Investigate before proceeding.

- [ ] **Step 1.6: Commit**

```bash
git add pwin-platform/src/intel-dossiers.js pwin-platform/test/test-intel-dossiers.js
git commit -m "feat(platform): add intel-dossiers loader module

Canonical loader for Agent 2 intelligence dossiers at
~/.pwin/intel/<type>/<slug>-<artefact>.json. Type → artefact-suffix
map for buyers/suppliers/sectors/incumbency. Mtime-based version
preference. Foundation for the orchestrator's MCP read tools and
skill-runner context providers."
```

---

## Task 2 — Register four MCP read tools

**Files:**
- Modify: `pwin-platform/src/mcp.js` (add four `server.tool` registrations after the existing intel block, around line 1722)

These tools are thin wrappers over `intelDossiers.getDossier()`. The loader is unit-tested in Task 1; this task is registration only.

- [ ] **Step 2.1: Add the import at the top of `mcp.js`**

Find the existing import block at the top of `pwin-platform/src/mcp.js` and add:

```javascript
import * as intelDossiers from './intel-dossiers.js';
```

- [ ] **Step 2.2: Locate the insertion point**

In `pwin-platform/src/mcp.js`, find the existing `get_supplier_profile` tool (around line 1696). Immediately after that block (after its closing `);`), and before the next tool (`get_expiring_contracts` around line 1708), insert four new tool registrations.

- [ ] **Step 2.3: Insert the four tool registrations**

Insert this block:

```javascript
  // ==========================================================================
  // Agent 2 INTELLIGENCE DOSSIERS — read-only loaders for the rich dossiers
  // produced by the four Agent 2 skills. These are distinct from
  // get_buyer_profile / get_supplier_profile, which return the lighter
  // procurement-database summary from competitive-intel.js.
  // ==========================================================================

  server.tool(
    'get_buyer_intelligence_dossier',
    'Load the Agent 2 buyer-intelligence dossier (rich narrative + structured claims). Distinct from get_buyer_profile which returns the lighter procurement-database summary. Returns the most recently modified version on disk.',
    {
      name: z.string().describe('Buyer name; will be slugified to find the dossier file (e.g. "Home Office" → home-office-dossier.json)'),
    },
    async ({ name }) => {
      const slug = intelDossiers.slugify(name);
      const data = await intelDossiers.getDossier('buyers', slug);
      if (!data) {
        return { content: [{ type: 'text', text: JSON.stringify({ found: false, slug, message: `No buyer dossier found for "${name}" at ~/.pwin/intel/buyers/${slug}-dossier.json` }, null, 2) }] };
      }
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_supplier_dossier',
    'Load the Agent 2 supplier-intelligence dossier (rich narrative + structured claims). Distinct from get_supplier_profile which returns the lighter procurement-database summary. Returns the most recently modified version on disk.',
    {
      name: z.string().describe('Supplier name; will be slugified to find the dossier file'),
    },
    async ({ name }) => {
      const slug = intelDossiers.slugify(name);
      const data = await intelDossiers.getDossier('suppliers', slug);
      if (!data) {
        return { content: [{ type: 'text', text: JSON.stringify({ found: false, slug, message: `No supplier dossier found for "${name}" at ~/.pwin/intel/suppliers/${slug}-dossier.json` }, null, 2) }] };
      }
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_sector_brief',
    'Load the Agent 2 sector-intelligence brief. Returns the most recently modified version on disk.',
    {
      sector: z.string().describe('Sector name; will be slugified to find the brief file'),
    },
    async ({ sector }) => {
      const slug = intelDossiers.slugify(sector);
      const data = await intelDossiers.getDossier('sectors', slug);
      if (!data) {
        return { content: [{ type: 'text', text: JSON.stringify({ found: false, slug, message: `No sector brief found for "${sector}" at ~/.pwin/intel/sectors/${slug}-brief.json` }, null, 2) }] };
      }
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );

  server.tool(
    'get_incumbency_analysis',
    'Load the Agent 2 incumbency advantage / displacement strategy analysis. Keyed by a (supplier, buyer) pair slug. Returns the most recently modified version on disk.',
    {
      supplierName: z.string().describe('Incumbent supplier name (e.g. "Serco")'),
      buyerName: z.string().describe('Buyer name (e.g. "Ministry of Defence")'),
    },
    async ({ supplierName, buyerName }) => {
      const slug = `${intelDossiers.slugify(supplierName)}-${intelDossiers.slugify(buyerName)}`;
      const data = await intelDossiers.getDossier('incumbency', slug);
      if (!data) {
        return { content: [{ type: 'text', text: JSON.stringify({ found: false, slug, message: `No incumbency analysis found for "${supplierName}" at "${buyerName}" at ~/.pwin/intel/incumbency/${slug}-analysis.json` }, null, 2) }] };
      }
      return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
  );
```

- [ ] **Step 2.4: Verify the file parses by starting the MCP server briefly**

```bash
cd pwin-platform && timeout 3 node src/server.js --mcp 2>&1 | head -20 || true
```

Expected: tool registrations log without errors. If a `ReferenceError` or `SyntaxError` appears, fix before continuing.

- [ ] **Step 2.5: Smoke-test against the real Home Office dossier**

```bash
cd pwin-platform && node -e "
import('./src/intel-dossiers.js').then(async m => {
  const d = await m.getDossier('buyers', 'home-office');
  if (!d) { console.error('FAIL: home-office dossier not found'); process.exit(1); }
  console.log('PASS: loaded', d.meta?.buyerName, 'v' + d.meta?.version);
});
"
```

Expected: `PASS: loaded Home Office v2.4` or similar.

- [ ] **Step 2.6: Commit**

```bash
git add pwin-platform/src/mcp.js
git commit -m "feat(platform): add four MCP tools for Agent 2 dossier reads

get_buyer_intelligence_dossier, get_supplier_dossier, get_sector_brief,
get_incumbency_analysis. Thin wrappers over intel-dossiers.js loader.
Distinct from existing get_buyer_profile / get_supplier_profile which
return the lighter compIntel procurement summaries.

Stakeholder map deferred — backing canonical layer not yet built."
```

---

## Task 3 — Skill-runner context-provider extensions

**Files:**
- Modify: `pwin-platform/src/skill-runner.js` (lines 151–162 + insertion of three new cases)
- Modify: `pwin-platform/test/test-skills.js` (add coverage)

The existing `case 'supplier_dossier'` reads from `~/.pwin/reference/suppliers/{slug}.json` — a path the producing Agent 2 skills do not write to. This is dead code in production. Plan A redirects it to the correct intel path and adds three new context-provider cases.

- [ ] **Step 3.1: Write the failing test**

Open `pwin-platform/test/test-skills.js` and find the existing test cases. Add a new test block (placement: after the existing setup section but inside the main test flow, before `console.log` of the final tally). Insert:

```javascript
// ---------------------------------------------------------------------------
// Test: Agent 2 dossier context-providers
// ---------------------------------------------------------------------------

console.log('\n=== Agent 2 dossier context-providers ===\n');

// Build a synthetic skill that requests all four dossier context items.
// Use the real Home Office dossier on disk for buyer; suppliers/sectors/
// incumbency are tested via fixtures written into the user's ~/.pwin/intel
// directory by this test, then cleaned up.

import { writeFile as _wf, mkdir as _mk, rm as _rm } from 'node:fs/promises';
import { join as _join } from 'node:path';
import { homedir as _hd } from 'node:os';

const _intelRoot = _join(_hd(), '.pwin', 'intel');
const _fix = {
  supplier: _join(_intelRoot, 'suppliers', 'plan-a-test-supplier-dossier.json'),
  sector: _join(_intelRoot, 'sectors', 'plan-a-test-sector-brief.json'),
  incumbency: _join(_intelRoot, 'incumbency', 'plan-a-test-supplier-plan-a-test-buyer-analysis.json'),
};

await _mk(_join(_intelRoot, 'suppliers'), { recursive: true });
await _mk(_join(_intelRoot, 'sectors'), { recursive: true });
await _mk(_join(_intelRoot, 'incumbency'), { recursive: true });
await _wf(_fix.supplier, JSON.stringify({ meta: { supplierName: 'Plan A Test Supplier', version: '1.0' } }));
await _wf(_fix.sector, JSON.stringify({ meta: { sector: 'Plan A Test Sector', version: '1.0' } }));
await _wf(_fix.incumbency, JSON.stringify({ meta: { incumbent: 'Plan A Test Supplier', buyer: 'Plan A Test Buyer', version: '1.0' } }));

const _dossierSkill = {
  id: 'plan-a-dossier-context-test',
  context: ['buyer_dossier', 'supplier_dossier', 'sector_brief', 'incumbency_analysis'],
};
const _dossierInput = {
  pursuitId,
  buyerName: 'Home Office',
  supplierName: 'Plan A Test Supplier',
  sector: 'Plan A Test Sector',
  incumbentBuyerName: 'Plan A Test Buyer',
};

const _ctx = await gatherContext(_dossierSkill, _dossierInput);

assert(_ctx.buyerDossier?.meta?.buyerName === 'Home Office',
  `buyer_dossier loads Home Office (got ${_ctx.buyerDossier?.meta?.buyerName})`);
assert(_ctx.supplierDossier?.meta?.supplierName === 'Plan A Test Supplier',
  `supplier_dossier loads from intel path (got ${_ctx.supplierDossier?.meta?.supplierName})`);
assert(_ctx.sectorBrief?.meta?.sector === 'Plan A Test Sector',
  `sector_brief loads (got ${_ctx.sectorBrief?.meta?.sector})`);
assert(_ctx.incumbencyAnalysis?.meta?.incumbent === 'Plan A Test Supplier',
  `incumbency_analysis loads keyed by supplier+buyer slug (got ${_ctx.incumbencyAnalysis?.meta?.incumbent})`);

// Missing-file behaviour: each context item is null, not undefined, when not found
const _missingSkill = { id: 'plan-a-dossier-missing-test', context: ['buyer_dossier'] };
const _missingCtx = await gatherContext(_missingSkill, { pursuitId, buyerName: 'Nonexistent Buyer 999' });
assert(_missingCtx.buyerDossier === null, 'buyer_dossier returns null for missing dossier');

// Cleanup fixtures
await _rm(_fix.supplier, { force: true });
await _rm(_fix.sector, { force: true });
await _rm(_fix.incumbency, { force: true });
```

(The leading underscores on the local names avoid collision with the existing test file's variables.)

- [ ] **Step 3.2: Run the test, confirm it fails**

```bash
cd pwin-platform && node test/test-skills.js 2>&1 | tail -30
```

Expected: existing tests pass; the four new assertions fail with messages like `buyer_dossier loads Home Office (got undefined)` — because `buyer_dossier`, `sector_brief`, and `incumbency_analysis` are not registered cases yet, and `supplier_dossier` reads from the wrong location.

- [ ] **Step 3.3: Add the import in skill-runner**

Open `pwin-platform/src/skill-runner.js`. Find the existing `import * as store from './store.js';` line near the top of the file. Add immediately below it:

```javascript
import * as intelDossiers from './intel-dossiers.js';
```

- [ ] **Step 3.4: Fix the existing `supplier_dossier` case**

In `pwin-platform/src/skill-runner.js`, find the existing case (lines 151–162):

```javascript
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
```

Replace it with:

```javascript
      case 'supplier_dossier': {
        // Load the Agent 2 supplier-intelligence dossier from
        // ~/.pwin/intel/suppliers/{slug}-dossier.json. supplierName comes
        // from skill input.
        const supplierName = input?.supplierName;
        if (supplierName) {
          context.supplierDossier = await intelDossiers.getDossier(
            'suppliers',
            intelDossiers.slugify(supplierName)
          );
        }
        break;
      }
```

- [ ] **Step 3.5: Add the three new cases**

Immediately after the `supplier_dossier` case in the same file, insert:

```javascript
      case 'buyer_dossier': {
        // Load the Agent 2 buyer-intelligence dossier from
        // ~/.pwin/intel/buyers/{slug}-dossier.json. buyerName comes from
        // skill input; falls back to the pursuit's client name if not
        // supplied directly.
        const buyerName = input?.buyerName || context.pursuit?.client;
        if (buyerName) {
          context.buyerDossier = await intelDossiers.getDossier(
            'buyers',
            intelDossiers.slugify(buyerName)
          );
        }
        break;
      }
      case 'sector_brief': {
        // Load the Agent 2 sector brief from
        // ~/.pwin/intel/sectors/{slug}-brief.json. sector comes from skill
        // input or the pursuit record.
        const sector = input?.sector || context.pursuit?.sector;
        if (sector) {
          context.sectorBrief = await intelDossiers.getDossier(
            'sectors',
            intelDossiers.slugify(sector)
          );
        }
        break;
      }
      case 'incumbency_analysis': {
        // Load the Agent 2 incumbency analysis from
        // ~/.pwin/intel/incumbency/{supplier-slug}-{buyer-slug}-analysis.json.
        // Requires both supplierName and incumbentBuyerName in the input.
        const supplierName = input?.supplierName;
        const buyerName = input?.incumbentBuyerName || input?.buyerName || context.pursuit?.client;
        if (supplierName && buyerName) {
          const slug = `${intelDossiers.slugify(supplierName)}-${intelDossiers.slugify(buyerName)}`;
          context.incumbencyAnalysis = await intelDossiers.getDossier('incumbency', slug);
        }
        break;
      }
```

- [ ] **Step 3.6: Re-run the test**

```bash
cd pwin-platform && node test/test-skills.js 2>&1 | tail -20
```

Expected: all assertions pass. Look for the `Agent 2 dossier context-providers` block reporting `5 passed` (4 happy-path + 1 missing-file) and the overall `failed` count remaining 0.

- [ ] **Step 3.7: Confirm no existing tests regressed**

```bash
cd pwin-platform && node test/test-skills.js 2>&1 | grep -E "passed|failed" | tail -5
```

Expected: total passed count higher than before (by 5), failed count 0.

- [ ] **Step 3.8: Commit**

```bash
git add pwin-platform/src/skill-runner.js pwin-platform/test/test-skills.js
git commit -m "feat(platform): wire Agent 2 dossiers into skill-runner context

Fix supplier_dossier case (was reading from stale ~/.pwin/reference path
the producing skills do not write to). Add buyer_dossier, sector_brief,
incumbency_analysis context providers, all routed through the new
intel-dossiers loader."
```

---

## Task 4 — Close the spec items Plan A delivers

**Files:**
- Modify: `docs/superpowers/specs/2026-04-29-pursuit-orchestration-design.md`

The spec's §5 (Open detail work for the implementation plan) lists items including the five MCP read tools and the skill-side context provider. Plan A closes four of the five MCP tools (stakeholder deferred) and the context-provider extension. Mark these as delivered so the next plan-phase has accurate state.

- [ ] **Step 4.1: Edit §5 of the spec**

Open `docs/superpowers/specs/2026-04-29-pursuit-orchestration-design.md`. Find the bullet beginning `- **MCP read tools** —`. Replace the bullet and the one immediately below it (the skill-side context provider bullet) with:

```markdown
- **MCP read tools** — `get_buyer_intelligence_dossier`, `get_supplier_dossier`, `get_sector_brief`, `get_incumbency_analysis` are **delivered by Plan A** ([docs/superpowers/plans/2026-04-30-orchestrator-plan-a-platform-foundations.md](../plans/2026-04-30-orchestrator-plan-a-platform-foundations.md)). `get_stakeholder_map` is deferred until the stakeholder canonical layer is built (`wiki/actions/pwin-stakeholder-canonical-layer.md`).
- **Skill-side context provider in the skill-runner** — **delivered by Plan A.** `buyer_dossier`, `supplier_dossier`, `sector_brief`, `incumbency_analysis` are now available context items for any skill.
```

- [ ] **Step 4.2: Commit the spec update**

```bash
git add docs/superpowers/specs/2026-04-29-pursuit-orchestration-design.md
git commit -m "docs(orchestration): mark MCP tools and context providers delivered

Plan A closes 4 of the 5 MCP read tools (stakeholder deferred to its
own canonical-layer build) and the skill-runner context-provider
extension. Spec §5 updated to reflect delivered state.

See docs/superpowers/plans/2026-04-30-orchestrator-plan-a-platform-foundations.md."
```

---

## Self-review

Spec coverage: each bullet of §5 of the spec has a task. ✓
Placeholder scan: no TBDs, no "implement appropriately" language, all code blocks contain real code. ✓
Type consistency: `getDossier(type, slug)` is used identically across Tasks 1, 2, 3. `slugify` is the named export from `intel-dossiers.js` and is called the same way everywhere. The four context-item names (`buyer_dossier`, `supplier_dossier`, `sector_brief`, `incumbency_analysis`) are spelled identically in the spec, the skill-runner cases, and the test. ✓
Scope: bounded to platform-level loaders + tools + context providers. No orchestrator skill code. No auditor code. ✓

## What this plan deliberately does NOT cover

- The pursuit-to-gate skill itself (Plan B).
- The orchestrator's calls into the Forensic Intelligence Auditor (Plan C, blocked on the auditor's own design spec).
- A `get_stakeholder_map` MCP tool (deferred — backing canonical layer not yet built).
- Renderer or HTML format loaders for dossiers (the loader returns the JSON only; HTML rendering is the producing skill's responsibility).
- Any change to the producing Agent 2 skills' output format. If a producing skill changes its file naming or output location in future, the `TYPE_TO_ARTEFACT` map and the file-discovery logic in `intel-dossiers.js` are the only update points.

---

## Execution handoff

Plan complete and saved to [docs/superpowers/plans/2026-04-30-orchestrator-plan-a-platform-foundations.md](.). Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session with checkpoints for review.

Pick which approach when ready.
