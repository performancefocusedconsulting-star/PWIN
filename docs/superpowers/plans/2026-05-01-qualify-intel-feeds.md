# Qualify Intelligence Feeds Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire sector context, competitor profiles, forward pipeline, and expiring contracts into Qualify's prompt builder, and fix existing field-name bugs that have prevented buyer stats and PWIN signals from rendering.

**Architecture:** `fetchCompetitiveIntel()` in `PWIN_Architect_v1.html` is refactored into a thin orchestrator calling six independent feed functions in parallel. A new `/api/intel/sector` endpoint is added to the platform to expose the already-existing `sectorProfile()` function over HTTP. All functions return a formatted text block or `''` — the orchestrator stitches non-empty blocks into one labelled prompt section.

**Tech Stack:** Vanilla JavaScript (ES2020, single HTML file), Node.js HTTP server (`pwin-platform/src/api.js`), SQLite via `competitive-intel.js`.

---

## Pre-flight: what you need to know

### Field name bugs in the existing code
The current `fetchCompetitiveIntel()` uses snake_case field names (`s.total_awards`, `m.procurement_method`, `sig.awards_count`) but the platform API returns camelCase (`s.totalAwards`, `m.method`, `sig.awardsCount`). This means the buyer stats and PWIN signals sections have never rendered real data. The refactor fixes all of these.

### Canonical resolution is already in place
- `buyerProfile()` resolves via canonical alias layer — "MoJ" → all MoJ sub-organisations.
- `supplierProfile()` queries `v_canonical_supplier_wins`, which includes both canonical and raw names — "Serco" matches all Serco entities.
- No changes needed in Qualify; the platform handles it.

### Only the consulting standalone is modified
`pwin-qualify/docs/PWIN_Architect_v1.html` — this is the only Qualify file that changes.
`bidequity-co/qualify-app.html` is **not touched**.

### Cache key change
The existing cache is keyed on `org` only. The new cache is keyed on `org + sector + competitors`. The cache variable is renamed from `{ org, data, ts }` to `{ key, data, ts }`.

---

## File Map

| File | Change |
|---|---|
| `pwin-platform/src/api.js` | Add one new route: `GET /api/intel/sector?name=` |
| `pwin-qualify/docs/PWIN_Architect_v1.html` | Replace `_intelCache` declaration + `fetchCompetitiveIntel()` with 6 feed functions + orchestrator |

---

## Task 1: Add the sector endpoint to the platform

**Files:**
- Modify: `pwin-platform/src/api.js`

- [ ] **Step 1.1: Locate the insertion point**

Open `pwin-platform/src/api.js`. Find this block (around line 351):

```javascript
    // GET /api/intel/pwin?buyer=&category=
    if (method === 'GET' && url.startsWith('/api/intel/pwin')) {
```

The new route goes immediately after the closing `}` of the pwin block, before the cpv route.

- [ ] **Step 1.2: Insert the sector route**

Add this block after the pwin route's closing `}`:

```javascript
    // GET /api/intel/sector?name=xxx
    if (method === 'GET' && url.startsWith('/api/intel/sector')) {
      const qs = new URLSearchParams(url.split('?')[1] || '');
      const name = qs.get('name');
      if (!name) return badRequest(res, 'name parameter required');
      return json(res, 200, compIntel.sectorProfile(name));
    }
```

- [ ] **Step 1.3: Start the platform and verify the endpoint**

```bash
cd pwin-platform
node src/server.js
```

In a second terminal:

```bash
curl "http://localhost:3456/api/intel/sector?name=Central%20Government"
```

Expected: a JSON object with keys `sector`, `summary`, `topBuyers`, `topSuppliers`, `procurementMethods`, `forwardPipeline`. Example:

```json
{
  "sector": "Central Government",
  "summary": { "buyerCount": 45, "awardCount": 15234, "totalSpend": 45000000000, "avgAwardValue": 2950000, "avgBidsPerTender": 4.1 },
  "topSuppliers": [{ "name": "Serco", "wins": 342, "totalValue": 1400000000 }],
  ...
}
```

If `sectorProfile` is not a function, the server will throw — check that `sectorProfile` appears in the `export {}` block at the bottom of `pwin-platform/src/competitive-intel.js`. It should be there already.

- [ ] **Step 1.4: Commit**

```bash
git add pwin-platform/src/api.js
git commit -m "feat(platform): expose sectorProfile via GET /api/intel/sector"
```

---

## Task 2: Replace the intel fetch code in PWIN_Architect_v1.html

This is a single replacement of the entire `_intelCache` declaration and `fetchCompetitiveIntel()` function with the refactored orchestrator plus six independent feed functions. All field name bugs are fixed in this step.

**Files:**
- Modify: `pwin-qualify/docs/PWIN_Architect_v1.html`

- [ ] **Step 2.1: Find the block to replace**

Search for `let _intelCache` in `pwin-qualify/docs/PWIN_Architect_v1.html`. It should be a single line immediately before `async function fetchCompetitiveIntel()`. Read from that line through the closing `}` of `fetchCompetitiveIntel()` (the function ends around line 4834). That entire block is what you are replacing.

- [ ] **Step 2.2: Replace the block**

Replace the entire `_intelCache` declaration + `fetchCompetitiveIntel()` function with the following. This is the complete replacement — do not keep any of the original code:

```javascript
// ── Intel cache ───────────────────────────────────────────────────────────────
let _intelCache = { key: null, data: null, ts: 0 };

// ── Buyer procurement profile ─────────────────────────────────────────────────
async function fetchBuyerProfile(org) {
  try {
    const resp = await fetch(`${INTEL_API}/api/intel/buyer?name=${encodeURIComponent(org)}`)
      .then(r => r.ok ? r.json() : null).catch(() => null);
    if (!resp?.buyers?.length) return '';
    const b = resp.buyers[0];
    const s = b.stats || {};
    if (!s.totalAwards) return '';
    const lines = ['PROCUREMENT INTELLIGENCE — Buyer Profile:'];
    lines.push(`Buyer: ${b.name} (${b.org_type || 'unknown type'})`);
    lines.push(`Awards in database: ${s.totalAwards} | Total spend: £${s.totalSpend ? (s.totalSpend / 1e6).toFixed(1) + 'm' : 'unknown'}`);
    lines.push(`Average award value: £${s.avgValue ? (s.avgValue / 1e6).toFixed(1) + 'm' : 'unknown'}`);
    if (s.avgBidsPerTender) lines.push(`Average bidders per tender: ${Number(s.avgBidsPerTender).toFixed(1)}`);
    if (b.procurementMethods?.length) {
      const methods = b.procurementMethods.map(m => `${m.method || 'unknown'}: ${m.count}`).join(', ');
      lines.push(`Procurement methods used: ${methods}`);
    }
    if (b.topSuppliers?.length) {
      lines.push('Top suppliers for this buyer:');
      b.topSuppliers.slice(0, 5).forEach(sup => {
        lines.push(`  - ${sup.name}: ${sup.wins} award(s), £${sup.totalValue ? (sup.totalValue / 1e6).toFixed(1) + 'm' : 'unknown'} total`);
      });
    }
    return lines.join('\n');
  } catch { return ''; }
}

// ── PWIN competition signals ──────────────────────────────────────────────────
async function fetchPwinSignals(org) {
  try {
    const resp = await fetch(`${INTEL_API}/api/intel/pwin?buyer=${encodeURIComponent(org)}`)
      .then(r => r.ok ? r.json() : null).catch(() => null);
    if (!resp?.signals?.length) return '';
    const sig = resp.signals[0];
    const lines = ['PROCUREMENT INTELLIGENCE — Competition Signals:'];
    if (sig.awardsCount) lines.push(`Competition level: ${sig.awardsCount} awards tracked`);
    if (sig.avgBidsPerTender) lines.push(`Average bids per tender: ${Number(sig.avgBidsPerTender).toFixed(1)}`);
    const total = (sig.openAwards || 0) + (sig.limitedAwards || 0) + (sig.directAwards || 0) + (sig.selectiveAwards || 0);
    if (total > 0) {
      lines.push(`Method breakdown: open=${sig.openAwards || 0}, limited=${sig.limitedAwards || 0}, direct=${sig.directAwards || 0}, selective=${sig.selectiveAwards || 0}`);
    }
    return lines.join('\n');
  } catch { return ''; }
}

// ── Sector context ────────────────────────────────────────────────────────────
async function fetchSectorContext(sector) {
  if (!sector) return '';
  try {
    const resp = await fetch(`${INTEL_API}/api/intel/sector?name=${encodeURIComponent(sector)}`)
      .then(r => r.ok ? r.json() : null).catch(() => null);
    if (!resp?.summary) return '';
    const { summary, topSuppliers } = resp;
    const lines = [`SECTOR CONTEXT — ${resp.sector}:`];
    if (summary.awardCount) lines.push(`Contracts in database: ${summary.awardCount.toLocaleString()} | Total sector spend: £${summary.totalSpend ? (summary.totalSpend / 1e9).toFixed(1) + 'bn' : 'unknown'}`);
    if (summary.avgAwardValue) lines.push(`Typical award value: £${(summary.avgAwardValue / 1e6).toFixed(1)}m`);
    if (summary.avgBidsPerTender) lines.push(`Average bidders per tender (sector): ${Number(summary.avgBidsPerTender).toFixed(1)}`);
    if (topSuppliers?.length) {
      lines.push('Dominant suppliers in this sector:');
      topSuppliers.slice(0, 3).forEach(s => {
        lines.push(`  - ${s.name}: ${s.wins} wins, £${s.totalValue ? (s.totalValue / 1e9).toFixed(1) + 'bn' : 'unknown'} total`);
      });
    }
    return lines.join('\n');
  } catch { return ''; }
}

// ── Competitor profiles ───────────────────────────────────────────────────────
async function fetchCompetitorProfiles(competitors, currentBuyer) {
  if (!competitors) return '';
  const names = competitors.split(/[,;]+/).map(s => s.trim()).filter(Boolean);
  if (!names.length) return '';
  try {
    const responses = await Promise.all(
      names.map(name =>
        fetch(`${INTEL_API}/api/intel/supplier?name=${encodeURIComponent(name)}`)
          .then(r => r.ok ? r.json() : null).catch(() => null)
      )
    );
    const lines = [];
    responses.forEach(resp => {
      if (!resp?.suppliers?.length) return;
      const sup = resp.suppliers[0];
      const s = sup.stats || {};
      const parts = [`${sup.name}: ${s.totalWins || 0} wins overall, £${s.totalValue ? (s.totalValue / 1e6).toFixed(0) + 'm' : 'unknown'} total`];
      if (sup.buyerRelationships?.length) {
        const match = sup.buyerRelationships.find(r => r.buyer.toLowerCase().includes(currentBuyer.toLowerCase()));
        if (match) {
          parts.push(`(${match.awards} wins with this buyer, £${match.totalValue ? (match.totalValue / 1e6).toFixed(0) + 'm' : 'unknown'})`);
        }
        const top3 = sup.buyerRelationships.slice(0, 3).map(r => `${r.buyer} (${r.awards})`).join(', ');
        parts.push(`Strongest relationships: ${top3}`);
      }
      lines.push(parts.join(' — '));
    });
    if (!lines.length) return '';
    return ['COMPETITOR PROFILES:', ...lines].join('\n');
  } catch { return ''; }
}

// ── Forward pipeline ──────────────────────────────────────────────────────────
async function fetchForwardPipeline(org) {
  try {
    const resp = await fetch(`${INTEL_API}/api/intel/pipeline?buyer=${encodeURIComponent(org)}`)
      .then(r => r.ok ? r.json() : null).catch(() => null);
    if (!resp?.notices?.length) return '';
    const lines = ['FORWARD PIPELINE — Upcoming tenders for this buyer:'];
    resp.notices.slice(0, 5).forEach(n => {
      const date = n.futureNoticeDate || n.engagementDeadline || 'date unknown';
      const value = n.estimatedValue ? `est. £${(n.estimatedValue / 1e6).toFixed(1)}m` : 'value unknown';
      lines.push(`  - ${n.title || 'Untitled'}: ${value}, expected ${date}`);
    });
    return lines.join('\n');
  } catch { return ''; }
}

// ── Expiring contracts ────────────────────────────────────────────────────────
async function fetchExpiringContracts(org) {
  try {
    const resp = await fetch(`${INTEL_API}/api/intel/expiring?buyer=${encodeURIComponent(org)}&days=365`)
      .then(r => r.ok ? r.json() : null).catch(() => null);
    if (!resp?.contracts?.length) return '';
    const lines = ['EXPIRING CONTRACTS — Contracts ending within 12 months:'];
    resp.contracts.slice(0, 5).forEach(c => {
      const value = c.value ? `£${(c.value / 1e6).toFixed(1)}m` : 'value unknown';
      lines.push(`  - ${c.title || 'Untitled'} (${c.suppliers || 'supplier unknown'}, ${value}) — expires ${c.contractEndDate || 'unknown'}`);
    });
    return lines.join('\n');
  } catch { return ''; }
}

// ── Orchestrator ──────────────────────────────────────────────────────────────
async function fetchCompetitiveIntel() {
  const org = state.context.org;
  if (!org || org.length < 3) return '';

  const sector = state.context.sector || '';
  const competitors = state.context.competitors || '';
  const cacheKey = `${org}|${sector}|${competitors}`;

  if (_intelCache.key === cacheKey && Date.now() - _intelCache.ts < 300000) return _intelCache.data;

  const [buyerBlock, pwinBlock, sectorBlock, competitorBlock, pipelineBlock, expiringBlock] = await Promise.all([
    fetchBuyerProfile(org),
    fetchPwinSignals(org),
    fetchSectorContext(sector),
    fetchCompetitorProfiles(competitors, org),
    fetchForwardPipeline(org),
    fetchExpiringContracts(org),
  ]);

  const sections = [buyerBlock, pwinBlock, sectorBlock, competitorBlock, pipelineBlock, expiringBlock].filter(Boolean);
  const result = sections.length ? '\n' + sections.join('\n\n') : '';

  _intelCache = { key: cacheKey, data: result, ts: Date.now() };
  return result;
}
```

- [ ] **Step 2.3: Verify the call sites are unchanged**

Search for `fetchCompetitiveIntel` in `pwin-qualify/docs/PWIN_Architect_v1.html`. There should be exactly two occurrences after your edit:
1. The function declaration: `async function fetchCompetitiveIntel()`
2. A call site: `const intelBlock = await fetchCompetitiveIntel();`

If there is a third occurrence, it is a stale reference — investigate before continuing.

Search for `_intelCache` — should appear exactly three times: the declaration, the cache read check, and the cache write.

- [ ] **Step 2.4: Verify the placeholder replacement is unchanged**

Search for `COMPETITIVE_INTEL_PLACEHOLDER` — should still appear in two places:
1. Inside `buildPersonaPrompt()`: `prompt += '{{COMPETITIVE_INTEL_PLACEHOLDER}}\n';`
2. At the call site: `.replace('{{COMPETITIVE_INTEL_PLACEHOLDER}}', intelBlock)`

Neither of these lines should have changed. If they differ, something was accidentally edited — restore from git.

- [ ] **Step 2.5: Commit**

```bash
git add pwin-qualify/docs/PWIN_Architect_v1.html
git commit -m "feat(qualify): wire sector, competitor, pipeline, expiring feeds into Alex's prompt

Refactors fetchCompetitiveIntel() into thin orchestrator + 6 feed functions.
Fixes existing field-name bugs (camelCase mismatch) that prevented buyer
stats and PWIN signals from rendering. New feeds: sector context,
competitor profiles (per named rival), forward pipeline, expiring contracts."
```

---

## Task 3: Integration test

**Prerequisite:** Platform running (`node pwin-platform/src/server.js`) with the database populated (run `python pwin-competitive-intel/agent/ingest.py` if the db is empty).

- [ ] **Step 3.1: Open the consulting standalone app in a browser**

Open `pwin-qualify/docs/PWIN_Architect_v1.html` directly in a browser (file:// URL is fine).

- [ ] **Step 3.2: Fill in the context panel**

Enter values that are likely to be in the database:
- Buyer org: `Ministry of Justice`
- Sector: `Central Government`
- Competitors: `Serco, Capita`
- Any other required context fields to reach the Review button

- [ ] **Step 3.3: Intercept the API call and inspect the system prompt**

Open browser DevTools (F12) → Network tab. Click the Review button. Find the outbound request to the Claude API (or the local AI review endpoint). Inspect the request payload — look at the `system` field.

Expected: the system prompt contains some combination of the following section headers (whichever have data):
```
PROCUREMENT INTELLIGENCE — Buyer Profile:
PROCUREMENT INTELLIGENCE — Competition Signals:
SECTOR CONTEXT — Central Government:
COMPETITOR PROFILES:
FORWARD PIPELINE — Upcoming tenders for this buyer:
EXPIRING CONTRACTS — Contracts ending within 12 months:
```

If buyer stats are showing real numbers (not `unknown`) — the field name bug is fixed.
If PWIN signals are showing a competition level — the field name bug is fixed.

- [ ] **Step 3.4: Test graceful degradation**

Stop the platform (`Ctrl+C`). Click Review again. The system prompt should still be sent — just without the intel sections. No error should surface to the user. Verify in DevTools that the request still fires and the response returns.

- [ ] **Step 3.5: Test cache invalidation**

Restart the platform. Run a review (populates the cache). Change the sector dropdown to a different value. Run another review. Verify in the Network tab that a new set of intel calls fires (not served from cache), and the system prompt now shows the new sector's name in the `SECTOR CONTEXT` header.

---

## Known edge cases (no action required, document only)

- **Competitor not in database:** Silent skip — the COMPETITOR PROFILES section is absent if no names match. Expected behaviour.
- **Pipeline returns no notices:** FORWARD PIPELINE section absent. Expected — many buyers have no planning notices in the database.
- **Sector name doesn't match SECTOR_ORG_TYPES in competitive-intel.js:** The function falls back to a LIKE match on buyer name. If that also fails, section is absent. No action needed unless a sector consistently returns nothing, in which case add the sector's org_type mapping to `SECTOR_ORG_TYPES` in `competitive-intel.js`.
- **Multiple canonical matches for a competitor:** `supplierProfile()` returns up to 10 matches sorted by member count. The code uses `resp.suppliers[0]` — the largest canonical entity. This is correct behaviour for an ambiguous name like "Capita" (Capita plc vs Capita Business Services).
