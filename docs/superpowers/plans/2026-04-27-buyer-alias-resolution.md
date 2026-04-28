# Buyer Alias Resolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `get_buyer_profile` return one consolidated buyer profile across all raw name variants (instead of 10 fragments), and tighten the residual coverage gap in the master list with rule-based alias variants.

**Architecture:** Two pieces. (1) Rewire `buyerProfile()` in `pwin-platform/src/competitive-intel.js` to call the existing `_resolveBuyerCanonical()` resolver and aggregate awards/notices across the full set of raw buyer rows it returns. (2) Add a one-shot Python script under `pwin-competitive-intel/agent/` that scans raw buyer names not yet linked to canonical, applies new tidying rules (preamble strip, prefix strip, brand-in-parentheses extraction), inserts new rows into `canonical_buyer_aliases`, then re-runs the existing linkage script.

**Tech Stack:** Node.js ES modules with `node:sqlite` (platform side); Python 3.9+ stdlib only (data side); SQLite database at `pwin-competitive-intel/db/bid_intel.db`.

**Current state (measured 2026-04-27):**
- `buyers.canonical_id` populated on 27,807 of 55,335 raw rows (50.3%)
- Residual within-plausible-candidate orphan rate: Cabinet Office 26%, Treasury 30%, Health 13%, Justice 12%, Defence 7%, Foreign Office 0%, Home Office 4%, Work and Pensions 2%, Education 5%
- `_resolveBuyerCanonical()` already exists in `competitive-intel.js` (line 723) and is used by `buyerBehaviourProfile`. `buyerProfile()` does NOT call it — that is the primary fix.

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `pwin-platform/src/competitive-intel.js` | Modify | Replace `buyerProfile()` body; tighten `_resolveBuyerCanonical()` rawBuyerIds expansion to use `buyers.canonical_id` directly |
| `pwin-platform/test/test-buyer-profile.js` | Create | Smoke test the new buyerProfile against known buyers |
| `pwin-competitive-intel/agent/backfill-buyer-aliases.py` | Create | Generate new alias rows from raw orphans using rule-based tidying |
| `pwin-competitive-intel/agent/test-backfill-rules.py` | Create | Unit tests for the tidying rules |
| `pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md` | Modify (append) | Record what was learned, before/after numbers |

---

## Task 1: Tighten `_resolveBuyerCanonical()` rawBuyerIds expansion

**Files:**
- Modify: `pwin-platform/src/competitive-intel.js:763-768`

The resolver currently expands canonical → raw IDs by joining buyers to aliases on `LOWER(TRIM(b.name)) = a.alias_lower`. That misses raw buyers that matched canonical via the normalised path (where `load-canonical-buyers.py` populated `buyers.canonical_id` via `alias_norm` rather than exact match). Use `buyers.canonical_id` directly.

- [ ] **Step 1: Replace the rawBuyerIds query**

Find the block at lines 763-768:

```javascript
const ids = db.prepare(`
  SELECT DISTINCT b.id
  FROM buyers b
  JOIN canonical_buyer_aliases a ON LOWER(TRIM(b.name)) = a.alias_lower
  WHERE a.canonical_id = ?
`).all(canonicalId).map(r => r.id);
```

Replace with:

```javascript
const ids = db.prepare(`
  SELECT DISTINCT id FROM buyers WHERE canonical_id = ?
`).all(canonicalId).map(r => r.id);
```

- [ ] **Step 2: Quick smoke check**

Run from the repo root:

```bash
cd pwin-platform && node -e "
import('./src/competitive-intel.js').then(({ buyerBehaviourProfile }) => {
  const r = buyerBehaviourProfile('Ministry of Justice');
  console.log('canonicalId:', r.canonicalId);
  console.log('rawBuyerIds count:', r.rawBuyerIds?.length || 'N/A');
  console.log('totalNotices:', r.summary?.totalNotices || r.totalNotices);
});
"
```

Expected: rawBuyerIds count rises from previous (alias-join) value to match `SELECT COUNT(*) FROM buyers WHERE canonical_id='ministry-of-justice'` (315 today).

- [ ] **Step 3: Commit**

```bash
git add pwin-platform/src/competitive-intel.js
git commit -m "fix(intel): expand canonical→raw buyer IDs via buyers.canonical_id"
```

---

## Task 2: Rewire `buyerProfile()` to use the canonical resolver

**Files:**
- Modify: `pwin-platform/src/competitive-intel.js:49-134` (the `buyerProfile` function)

The function currently does `LIKE '%nameQuery%'` against raw buyers and aggregates per raw `buyer_id`. The new behaviour: resolve to canonical, gather all raw buyer IDs that map to it, aggregate across the whole set, return one consolidated profile. Falls back to today's raw-search behaviour if the resolver returns nothing or flags the query as ambiguous.

- [ ] **Step 1: Replace the `buyerProfile` function body**

Replace lines 49-134 (the entire `function buyerProfile(...)` block) with:

```javascript
function buyerProfile(nameQuery, limit = 20) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const resolved = _resolveBuyerCanonical(db, nameQuery);

    // No match at all — keep today's raw-search behaviour as the fallback so
    // partial-name searches against unaliased buyers still work.
    if (!resolved) {
      const buyers = db.prepare(`
        SELECT id, name, org_type, region_code FROM buyers
        WHERE LOWER(name) LIKE LOWER(?)
        ORDER BY name LIMIT 10
      `).all(`%${nameQuery}%`);
      if (!buyers.length) return { buyers: [], message: `No buyers matching '${nameQuery}'` };
      console.warn(`[buyerProfile] no canonical resolution for "${nameQuery}" — falling back to raw search (${buyers.length} hits)`);
      return _aggregateRawBuyers(db, buyers, limit);
    }

    // Ambiguous canonical match — return the candidate list so the caller
    // can re-query with a more specific name.
    if (resolved.ambiguous) {
      return {
        ambiguous: true,
        candidates: resolved.candidates,
        message: `'${nameQuery}' matches multiple canonical buyers — please be more specific`,
      };
    }

    // Fragmented (no canonical, but raw rows match the query) — aggregate
    // those raw rows as a single profile and flag the response.
    if (resolved.fragmented) {
      const buyers = db.prepare(`
        SELECT id, name, org_type, region_code FROM buyers
        WHERE id IN (${resolved.rawBuyerIds.map(() => '?').join(',')})
      `).all(...resolved.rawBuyerIds);
      console.warn(`[buyerProfile] no canonical for "${nameQuery}" — fragmented across ${buyers.length} raw rows`);
      const out = _aggregateRawBuyers(db, buyers, limit);
      out.fragmented = true;
      return out;
    }

    // Canonical hit — aggregate awards/notices across every raw buyer row
    // linked to this canonical entity.
    return _consolidatedBuyerProfile(db, resolved, limit);
  } finally {
    db.close();
  }
}

function _consolidatedBuyerProfile(db, resolved, limit) {
  const ids = resolved.rawBuyerIds;
  if (!ids.length) {
    return {
      buyers: [{
        id: resolved.canonicalId,
        name: resolved.canonicalName,
        org_type: resolved.canonicalType,
        canonical: true,
        rawIdCount: 0,
        message: 'Canonical entity has no raw buyer rows linked yet',
        stats: {},
        procurementMethods: [],
        topSuppliers: [],
        recentAwards: [],
      }],
    };
  }
  const ph = ids.map(() => '?').join(',');

  const stats = db.prepare(`
    SELECT
      COUNT(DISTINCT a.id) AS total_awards,
      COUNT(DISTINCT n.ocid) AS total_notices,
      SUM(a.value_amount_gross) AS total_spend,
      AVG(a.value_amount_gross) AS avg_value,
      MAX(a.value_amount_gross) AS max_value,
      AVG(n.total_bids) AS avg_bids
    FROM awards a
    JOIN notices n ON a.ocid = n.ocid
    WHERE n.buyer_id IN (${ph}) AND a.status IN ('active', 'pending')
  `).get(...ids);

  const methods = db.prepare(`
    SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
    FROM awards a JOIN notices n ON a.ocid = n.ocid
    WHERE n.buyer_id IN (${ph}) AND a.status IN ('active', 'pending')
    GROUP BY n.procurement_method ORDER BY cnt DESC
  `).all(...ids);

  const topSuppliers = db.prepare(`
    SELECT canonical_name AS name,
           COUNT(DISTINCT award_id) AS wins,
           SUM(value_amount_gross)  AS total_value
    FROM v_canonical_supplier_wins
    WHERE buyer_id IN (${ph}) AND value_quality IS NULL
    GROUP BY canonical_id
    ORDER BY wins DESC, total_value DESC LIMIT 15
  `).all(...ids);

  const recentAwards = db.prepare(`
    SELECT n.title, a.value_amount_gross, n.procurement_method,
           GROUP_CONCAT(DISTINCT s.name) AS suppliers,
           a.contract_end_date, a.award_date
    FROM awards a
    JOIN notices n ON a.ocid = n.ocid
    LEFT JOIN award_suppliers asup ON a.id = asup.award_id
    LEFT JOIN suppliers s ON asup.supplier_id = s.id
    WHERE n.buyer_id IN (${ph}) AND a.status IN ('active', 'pending')
    GROUP BY a.id
    ORDER BY a.award_date DESC NULLS LAST LIMIT ?
  `).all(...ids, limit);

  return {
    buyers: [{
      id: resolved.canonicalId,
      name: resolved.canonicalName,
      org_type: resolved.canonicalType,
      canonical: true,
      rawIdCount: ids.length,
      stats: {
        totalAwards: stats.total_awards,
        totalNotices: stats.total_notices,
        totalSpend: stats.total_spend,
        avgValue: stats.avg_value,
        maxValue: stats.max_value,
        avgBidsPerTender: stats.avg_bids,
      },
      procurementMethods: methods.map(m => ({ method: m.procurement_method, count: m.cnt })),
      topSuppliers: topSuppliers.map(s => ({ name: s.name, wins: s.wins, totalValue: s.total_value })),
      recentAwards: recentAwards.map(r => ({
        title: r.title,
        value: r.value_amount_gross,
        method: r.procurement_method,
        suppliers: r.suppliers,
        contractEndDate: r.contract_end_date,
        awardDate: r.award_date,
      })),
    }],
  };
}

function _aggregateRawBuyers(db, buyers, limit) {
  return {
    buyers: buyers.map(buyer => {
      const stats = db.prepare(`
        SELECT
          COUNT(DISTINCT a.id) AS total_awards,
          COUNT(DISTINCT n.ocid) AS total_notices,
          SUM(a.value_amount_gross) AS total_spend,
          AVG(a.value_amount_gross) AS avg_value,
          MAX(a.value_amount_gross) AS max_value,
          AVG(n.total_bids) AS avg_bids
        FROM awards a
        JOIN notices n ON a.ocid = n.ocid
        WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
      `).get(buyer.id);

      const methods = db.prepare(`
        SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
        FROM awards a JOIN notices n ON a.ocid = n.ocid
        WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
        GROUP BY n.procurement_method ORDER BY cnt DESC
      `).all(buyer.id);

      const topSuppliers = db.prepare(`
        SELECT canonical_name AS name,
               COUNT(DISTINCT award_id) AS wins,
               SUM(value_amount_gross)  AS total_value
        FROM v_canonical_supplier_wins
        WHERE buyer_id = ? AND value_quality IS NULL
        GROUP BY canonical_id
        ORDER BY wins DESC, total_value DESC LIMIT 15
      `).all(buyer.id);

      const recentAwards = db.prepare(`
        SELECT n.title, a.value_amount_gross, n.procurement_method,
               GROUP_CONCAT(DISTINCT s.name) AS suppliers,
               a.contract_end_date, a.award_date
        FROM awards a
        JOIN notices n ON a.ocid = n.ocid
        LEFT JOIN award_suppliers asup ON a.id = asup.award_id
        LEFT JOIN suppliers s ON asup.supplier_id = s.id
        WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
        GROUP BY a.id
        ORDER BY a.award_date DESC NULLS LAST LIMIT ?
      `).all(buyer.id, limit);

      return {
        ...buyer,
        canonical: false,
        stats: {
          totalAwards: stats.total_awards,
          totalNotices: stats.total_notices,
          totalSpend: stats.total_spend,
          avgValue: stats.avg_value,
          maxValue: stats.max_value,
          avgBidsPerTender: stats.avg_bids,
        },
        procurementMethods: methods.map(m => ({ method: m.procurement_method, count: m.cnt })),
        topSuppliers: topSuppliers.map(s => ({ name: s.name, wins: s.wins, totalValue: s.total_value })),
        recentAwards: recentAwards.map(r => ({
          title: r.title,
          value: r.value_amount_gross,
          method: r.procurement_method,
          suppliers: r.suppliers,
          contractEndDate: r.contract_end_date,
          awardDate: r.award_date,
        })),
      };
    }),
  };
}
```

- [ ] **Step 2: Spot-check from the command line**

```bash
cd pwin-platform && node -e "
import('./src/competitive-intel.js').then(async (m) => {
  for (const q of ['Ministry of Justice', 'MOD', 'DfT', 'HMRC', 'Cabinet Office', 'Some Made-Up Buyer']) {
    const r = m.buyerProfile(q);
    const b = r.buyers?.[0];
    console.log(q.padEnd(30), '→', b?.name || (r.message || JSON.stringify(r)).slice(0,80),
      b ? \`(canonical=\${b.canonical}, awards=\${b.stats?.totalAwards}, suppliers=\${b.topSuppliers?.length})\` : '');
  }
});
"
```

Expected:
- "Ministry of Justice" → canonical=true, awards >2000 (vs ~few hundred per raw fragment today)
- "MOD" → resolves to "Ministry of Defence", canonical=true
- "DfT" → resolves to "Department for Transport", canonical=true
- "HMRC" → resolves to "HM Revenue and Customs", canonical=true
- "Cabinet Office" → canonical=true
- "Some Made-Up Buyer" → empty result with message

- [ ] **Step 3: Commit**

```bash
git add pwin-platform/src/competitive-intel.js
git commit -m "feat(intel): consolidate get_buyer_profile via canonical resolver"
```

---

## Task 3: Add a smoke test for buyerProfile

**Files:**
- Create: `pwin-platform/test/test-buyer-profile.js`

This is not unit-test isolated (it hits the real database) — it's a regression guard against the consolidation behaviour silently breaking. Mirrors the style of `test-skills.js`.

- [ ] **Step 1: Create the test**

```javascript
/**
 * PWIN Platform — buyerProfile consolidation regression test
 *
 * Hits the real competitive-intel database. Ensures get_buyer_profile
 * returns one consolidated row per canonical buyer rather than fragments.
 *
 * Run: node test/test-buyer-profile.js
 */
import { buyerProfile } from '../src/competitive-intel.js';

let passed = 0, failed = 0;

function check(label, condition, detail) {
  if (condition) { passed++; console.log(`  ✓ ${label}`); }
  else           { failed++; console.error(`  ✗ ${label}`, detail || ''); }
}

console.log('\n=== buyerProfile consolidation tests ===\n');

const moj = buyerProfile('Ministry of Justice');
check('MoJ resolves to one canonical row', moj.buyers?.length === 1, moj);
check('MoJ row is flagged canonical', moj.buyers?.[0]?.canonical === true);
check('MoJ rolls up many raw IDs', moj.buyers?.[0]?.rawIdCount > 100, `rawIdCount=${moj.buyers?.[0]?.rawIdCount}`);
check('MoJ has awards', moj.buyers?.[0]?.stats?.totalAwards > 0);

const mod = buyerProfile('MOD');
check('MOD abbreviation resolves to MoD canonical',
  mod.buyers?.[0]?.name === 'Ministry of Defence',
  mod.buyers?.[0]?.name);
check('MOD row is canonical', mod.buyers?.[0]?.canonical === true);

const dft = buyerProfile('DfT');
check('DfT resolves to Department for Transport',
  dft.buyers?.[0]?.name === 'Department for Transport',
  dft.buyers?.[0]?.name);

const cab = buyerProfile('Cabinet Office');
check('Cabinet Office resolves canonical', cab.buyers?.[0]?.canonical === true);

const nonsense = buyerProfile('Zzzzzzz Made Up Buyer 999');
check('Unknown buyer returns empty', !nonsense.buyers?.length || nonsense.message);

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed ? 1 : 0);
```

- [ ] **Step 2: Run the test**

```bash
cd pwin-platform && node test/test-buyer-profile.js
```

Expected: all checks pass. If any fail, debug before proceeding.

- [ ] **Step 3: Commit**

```bash
git add pwin-platform/test/test-buyer-profile.js
git commit -m "test(intel): smoke-test buyerProfile consolidation"
```

---

## Task 4: Build tidying-rule unit tests

**Files:**
- Create: `pwin-competitive-intel/agent/test-backfill-rules.py`

Test the tidying rules in isolation before wiring them into the alias-backfill script.

- [ ] **Step 1: Write the tests**

```python
#!/usr/bin/env python3
"""
Unit tests for the buyer-name tidying rules used by backfill-buyer-aliases.

Run: python agent/test-backfill-rules.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import will succeed once Task 5 lands — until then this file is the contract.
from backfill_buyer_aliases import (
    strip_trailing_punct,
    strip_prefix_dash,
    strip_secretary_of_state,
    extract_paren_brand,
    strip_hm_preamble,
    tidy_variants,
)

passed = 0
failed = 0

def assert_eq(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  PASS {label}")
    else:
        failed += 1
        print(f"  FAIL {label}: got={got!r} want={want!r}")

# ── strip_trailing_punct ───────────────────────────────────────────────
assert_eq("trailing full stop",
          strip_trailing_punct("Ministry of Justice."),
          "Ministry of Justice")
assert_eq("trailing comma",
          strip_trailing_punct("Cabinet Office,"),
          "Cabinet Office")
assert_eq("no trailing punct unchanged",
          strip_trailing_punct("HM Treasury"),
          "HM Treasury")

# ── strip_prefix_dash ──────────────────────────────────────────────────
assert_eq("DoJ - prefix removed",
          strip_prefix_dash("DoJ - Department of Justice"),
          "Department of Justice")
assert_eq("MoD - prefix removed",
          strip_prefix_dash("MoD - Defence Equipment & Support"),
          "Defence Equipment & Support")
assert_eq("no dash unchanged",
          strip_prefix_dash("Department for Transport"),
          "Department for Transport")
assert_eq("dash inside name preserved",
          strip_prefix_dash("Department of Health and Social Care - Public Health"),
          "Department of Health and Social Care - Public Health")  # prefix has no all-caps abbrev

# ── strip_secretary_of_state ───────────────────────────────────────────
assert_eq("simple SoS preamble",
          strip_secretary_of_state("The Secretary of State for Justice acting through the Ministry of Justice"),
          "Ministry of Justice")
assert_eq("SoS without 'The'",
          strip_secretary_of_state("Secretary of State for Defence acting through Ministry of Defence"),
          "Ministry of Defence")
assert_eq("plain SoS no acting-through becomes department guess",
          strip_secretary_of_state("SECRETARY OF STATE FOR JUSTICE"),
          None)  # ambiguous — caller must skip

# ── extract_paren_brand ────────────────────────────────────────────────
assert_eq("brand in parens",
          extract_paren_brand("Crown Commercial Service (CCS)"),
          [("Crown Commercial Service", "CCS")])
assert_eq("brand in parens with quotes",
          extract_paren_brand('National Services Scotland ("NSS")'),
          [("National Services Scotland", "NSS")])
assert_eq("no parens",
          extract_paren_brand("Cabinet Office"),
          [])

# ── strip_hm_preamble ──────────────────────────────────────────────────
assert_eq("HM removed",
          strip_hm_preamble("HM Treasury"),
          "Treasury")
assert_eq("His Majesty's removed",
          strip_hm_preamble("His Majesty's Revenue and Customs"),
          "Revenue and Customs")
assert_eq("no preamble unchanged",
          strip_hm_preamble("Cabinet Office"),
          "Cabinet Office")

# ── tidy_variants (the orchestrator) ────────────────────────────────────
v = tidy_variants("Ministry of Justice.")
assert_eq("variants include trailing-stop strip",
          "ministry of justice" in v,
          True)

v = tidy_variants("DoJ - Department of Justice")
assert_eq("variants include prefix strip",
          "department of justice" in v,
          True)

v = tidy_variants("Crown Commercial Service (CCS)")
assert_eq("variants include CCS brand",
          "ccs" in v,
          True)
assert_eq("variants include base name",
          "crown commercial service" in v,
          True)

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
```

- [ ] **Step 2: Run the test (it will fail until Task 5)**

```bash
cd pwin-competitive-intel && python agent/test-backfill-rules.py
```

Expected: ImportError on `backfill_buyer_aliases` (proves the test runs before the implementation, per TDD).

- [ ] **Step 3: Commit (the failing test)**

```bash
git add pwin-competitive-intel/agent/test-backfill-rules.py
git commit -m "test(intel): add tidying-rule tests for buyer alias backfill"
```

---

## Task 5: Implement the tidying rules and the backfill script

**Files:**
- Create: `pwin-competitive-intel/agent/backfill_buyer_aliases.py`

Snake-cased filename so the test file can import from it. Single CLI entry point with `--dry-run`. Idempotent. Stdlib only.

- [ ] **Step 1: Create the script**

```python
#!/usr/bin/env python3
"""
Backfill canonical_buyer_aliases with rule-based variants for orphaned raw buyers.

Walks every raw buyer name where buyers.canonical_id IS NULL, applies a series of
tidying rules to produce candidate alias strings, and where a candidate matches
exactly to a canonical_name or abbreviation in canonical_buyers, inserts a new
row into canonical_buyer_aliases.

Re-running load-canonical-buyers.py afterwards picks up these new aliases and
updates the buyers.canonical_id column.

Idempotent — skips aliases already present.

Usage:
    python agent/backfill_buyer_aliases.py --dry-run
    python agent/backfill_buyer_aliases.py
    python agent/backfill_buyer_aliases.py --report-only
"""
import argparse
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "db", "bid_intel.db",
)

# Known department abbreviations that appear as "ABBR - Full Name" prefixes.
# Conservative list: must be 2-5 chars, all caps or mixed-case dept-style.
PREFIX_ABBREVIATIONS = {
    "DoJ", "MoD", "DfT", "DfE", "DWP", "DH", "DHSC", "FCDO", "HMT",
    "MoJ", "DCMS", "DEFRA", "BEIS", "DBT", "DLUHC", "DESNZ", "DSIT",
    "MHCLG", "MOHA", "HO", "CO",
}


def strip_trailing_punct(name: str) -> str:
    """Remove trailing . , ; whitespace from a buyer name."""
    return re.sub(r"[\.,;]+\s*$", "", (name or "").strip())


def strip_prefix_dash(name: str) -> str:
    """Strip 'ABBR - ' prefix where ABBR is a known dept abbreviation."""
    m = re.match(r"^([A-Za-z]{2,5})\s*-\s*(.+)$", name or "")
    if m and m.group(1) in PREFIX_ABBREVIATIONS:
        return m.group(2).strip()
    return name


def strip_secretary_of_state(name: str) -> str:
    """
    'The Secretary of State for X acting through Y' → 'Y'.
    Returns None for a bare 'Secretary of State for X' (ambiguous — could be
    several departments).
    """
    s = (name or "").strip()
    m = re.match(
        r"^(?:the\s+)?secretary of state for [^,]+?\s+acting\s+(?:through|as)\s+(?:the\s+)?(.+)$",
        s, flags=re.IGNORECASE,
    )
    if m:
        return m.group(1).strip(" ,.")
    if re.match(r"^(?:the\s+)?secretary of state for", s, flags=re.IGNORECASE):
        return None
    return name


def extract_paren_brand(name: str):
    """
    'X (Y)' or 'X ("Y")' → [(X, Y)]. Returns list because future variants
    may want all of them.
    """
    out = []
    s = (name or "").strip()
    m = re.match(r'^(.+?)\s*\(\s*"?([^()"]+?)"?\s*\)\s*$', s)
    if m:
        out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def strip_hm_preamble(name: str) -> str:
    """Strip leading 'HM', 'His Majesty's', 'Her Majesty's'."""
    s = (name or "").strip()
    s = re.sub(r"^(?:HM|His\s+Majesty's|Her\s+Majesty's)\s+", "", s, flags=re.IGNORECASE)
    return s


def tidy_variants(name: str):
    """
    Generate the set of lowercased candidate alias variants for a raw buyer name.
    Always includes the trivially-tidied base form. Returns a set of strings.
    """
    base = strip_trailing_punct(name or "")
    if not base:
        return set()

    out = set()
    out.add(base.lower())

    # Prefix strip
    p = strip_prefix_dash(base)
    if p != base:
        out.add(p.lower())

    # Secretary of State preamble
    sos = strip_secretary_of_state(base)
    if sos and sos != base:
        out.add(sos.lower())

    # Brand-in-parens
    for full, brand in extract_paren_brand(base):
        out.add(full.lower())
        out.add(brand.lower())

    # HM / His Majesty's preamble — only useful when canonical lacks the preamble
    hm = strip_hm_preamble(base)
    if hm != base:
        out.add(hm.lower())

    # Discard anything empty / one char
    return {v for v in out if v and len(v) > 1}


def load_canonical_lookup(conn: sqlite3.Connection):
    """
    Build a dict { lowercased_name_or_abbreviation : canonical_id }.
    Where multiple canonicals share a lowercased form, the value is None
    (ambiguous — must skip).
    """
    lookup = {}
    ambiguous = set()
    for cid, cname, abbr in conn.execute(
        "SELECT canonical_id, canonical_name, abbreviation FROM canonical_buyers"
    ):
        for term in (cname, abbr):
            if not term:
                continue
            t = term.lower().strip()
            if not t:
                continue
            if t in ambiguous:
                continue
            if t in lookup and lookup[t] != cid:
                ambiguous.add(t)
                lookup.pop(t, None)
            else:
                lookup[t] = cid
    return lookup


def existing_aliases(conn: sqlite3.Connection):
    rows = conn.execute("SELECT alias_lower FROM canonical_buyer_aliases").fetchall()
    return {r[0] for r in rows}


def run(dry_run: bool, report_only: bool):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        canonical_lookup = load_canonical_lookup(conn)
        existing = existing_aliases(conn)

        # Walk orphans only — already-linked rows are fine
        orphans = conn.execute(
            "SELECT id, name FROM buyers WHERE canonical_id IS NULL AND name IS NOT NULL"
        ).fetchall()
        print(f"  scanning {len(orphans)} orphaned raw buyer rows")

        new_aliases = []         # (alias_lower, alias_norm, canonical_id, source_raw_name)
        ambiguous_hits = []      # (raw_name, [candidate_canonicals])
        unmatched = []

        # Lazy reuse the existing norm() function from load-canonical-buyers if possible
        def norm(s: str) -> str:
            s = (s or "").lower().strip()
            s = re.sub(r"[\&]", " and ", s)
            s = re.sub(r"\bltd\b\.?", "limited", s)
            s = re.sub(r"[,\.\(\)\-\'\"]", " ", s)
            return re.sub(r"\s+", " ", s).strip()

        seen_alias_for_canonical = set()  # (alias_lower, canonical_id) — dedupe within this run

        for row in orphans:
            raw_name = row["name"]
            variants = tidy_variants(raw_name)
            hits = {}  # alias_lower → canonical_id
            for v in variants:
                if v in canonical_lookup:
                    cid = canonical_lookup[v]
                    if cid is not None:
                        hits[v] = cid

            if not hits:
                unmatched.append(raw_name)
                continue

            # If multiple canonicals matched, that's ambiguous — record and skip
            distinct_canonicals = set(hits.values())
            if len(distinct_canonicals) > 1:
                ambiguous_hits.append((raw_name, sorted(distinct_canonicals)))
                continue

            # Single canonical — register the variant aliases that hit it
            cid = next(iter(distinct_canonicals))
            for alias_lower in hits:
                if alias_lower in existing:
                    continue
                key = (alias_lower, cid)
                if key in seen_alias_for_canonical:
                    continue
                seen_alias_for_canonical.add(key)
                new_aliases.append((alias_lower, norm(alias_lower), cid, raw_name))

        # ── Report ─────────────────────────────────────────────────────
        print(f"\n  candidate new aliases: {len(new_aliases)}")
        print(f"  raw rows still unmatched: {len(unmatched)}")
        print(f"  raw rows ambiguous (matched >1 canonical): {len(ambiguous_hits)}")

        # Top contributors among new aliases
        canon_counts = Counter(a[2] for a in new_aliases)
        if canon_counts:
            print("\n  top canonicals receiving new aliases:")
            for cid, n in canon_counts.most_common(15):
                print(f"    {n:>4}  {cid}")

        # Sample of unmatched (first 30, deduped)
        if unmatched:
            print("\n  sample of unmatched raw names (first 30 unique):")
            for n in sorted(set(unmatched))[:30]:
                print(f"    - {n}")

        # Sample ambiguous
        if ambiguous_hits:
            print("\n  sample ambiguous matches (first 15):")
            for raw, cands in ambiguous_hits[:15]:
                print(f"    - {raw!r} → {cands}")

        if report_only:
            print("\n  --report-only: not writing")
            return

        if dry_run:
            print("\n  --dry-run: not writing")
            return

        # ── Insert ──────────────────────────────────────────────────────
        ins = conn.executemany(
            "INSERT OR IGNORE INTO canonical_buyer_aliases (alias_lower, alias_norm, canonical_id) VALUES (?, ?, ?)",
            [(a, n, c) for (a, n, c, _src) in new_aliases],
        )
        conn.commit()
        print(f"\n  wrote {ins.rowcount} new alias rows (ignoring duplicates)")
        print("  next step: re-run agent/load-canonical-buyers.py to re-link buyers to canonical")
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser(description="Backfill canonical_buyer_aliases")
    ap.add_argument("--dry-run", action="store_true", help="report and exit, no writes")
    ap.add_argument("--report-only", action="store_true", help="alias of --dry-run")
    args = ap.parse_args()
    run(dry_run=args.dry_run, report_only=args.report_only)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the unit tests**

```bash
cd pwin-competitive-intel && python agent/test-backfill-rules.py
```

Expected: all tests pass. If any fail, fix the rule and re-run.

- [ ] **Step 3: Commit**

```bash
git add pwin-competitive-intel/agent/backfill_buyer_aliases.py
git commit -m "feat(intel): add buyer alias backfill script"
```

---

## Task 6: Run the backfill — dry-run, review, then for real

**Files:**
- No new files. Run-and-review.

- [ ] **Step 1: Dry run, review the report**

```bash
cd pwin-competitive-intel && python agent/backfill_buyer_aliases.py --dry-run | tee /tmp/backfill-dryrun.txt
```

Read the output:
- Count of candidate new aliases
- Top canonicals receiving new aliases — sanity check the names look right
- Sample unmatched names — look for patterns we missed (a new tidying rule may be worth adding)
- Sample ambiguous matches — these will be skipped; confirm the skips look correct

If anything looks wrong, fix the rule (Task 5 file), re-run the unit tests, and re-run the dry-run. Iterate until the report looks clean.

- [ ] **Step 2: Real run**

```bash
cd pwin-competitive-intel && python agent/backfill_buyer_aliases.py
```

Expected: prints "wrote N new alias rows" with N matching the dry-run candidate count.

- [ ] **Step 3: Re-run the canonical-buyer linkage**

```bash
cd pwin-competitive-intel && python agent/load-canonical-buyers.py
```

Expected: prints stats showing more buyers now linked than before. Note the new total.

- [ ] **Step 4: Commit (no code change, but the database hash moves — record the run)**

```bash
git commit --allow-empty -m "chore(intel): run buyer alias backfill + canonical relink"
```

---

## Task 7: Validate — orphan check + dossier diff

**Files:**
- Modify (append): `pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md`

- [ ] **Step 1: Orphan check across the reference 10 departments**

```bash
cd pwin-competitive-intel && python -c "
import sqlite3
db = sqlite3.connect('db/bid_intel.db')
checks = [
    ('ministry-of-justice', ['ministry of justice','secretary of state for justice','moj','dept of justice','department of justice']),
    ('foreign-commonwealth-development-office', ['fcdo','foreign commonwealth','foreign office','foreign and commonwealth']),
    ('cabinet-office', ['cabinet office','minister for the cabinet office']),
    ('hm-treasury', ['hm treasury',\"her majesty's treasury\",\"his majesty's treasury\",'hmt']),
    ('department-of-health-and-social-care', ['department of health','dept of health','dhsc']),
    ('ministry-of-defence', ['ministry of defence','secretary of state for defence','mod','defence equipment']),
    ('home-office', ['home office']),
    ('department-for-work-pensions', ['work and pensions','dwp']),
    ('department-for-education', ['department for education','dfe']),
]
print(f'{\"Dept\":<50} {\"Linked\":>8} {\"Plausible\":>10} {\"Orphan%\":>9}')
for cid, terms in checks:
    name = db.execute('SELECT canonical_name FROM canonical_buyers WHERE canonical_id=?', (cid,)).fetchone()[0]
    linked = db.execute('SELECT COUNT(*) FROM buyers WHERE canonical_id=?', (cid,)).fetchone()[0]
    where = ' OR '.join(['LOWER(name) LIKE ?']*len(terms))
    params = [f'%{t}%' for t in terms]
    cands = db.execute(f'SELECT COUNT(*) FROM buyers WHERE {where}', params).fetchone()[0]
    orph = db.execute(f'SELECT COUNT(*) FROM buyers WHERE ({where}) AND canonical_id IS NULL', params).fetchone()[0]
    pct = 100*orph/cands if cands else 0
    print(f'{name:<50} {linked:>8} {cands:>10} {pct:>8.0f}%')
" | tee /tmp/orphan-check-after.txt
```

Pass criterion: every department in the table shows ≤20% orphan, ideally ≤10%.

- [ ] **Step 2: Before/after dossier diff for Ministry of Justice**

```bash
cd pwin-platform && node -e "
import('./src/competitive-intel.js').then(m => {
  const r = m.buyerProfile('Ministry of Justice');
  const b = r.buyers?.[0];
  console.log('canonical:', b?.canonical);
  console.log('rawIdCount:', b?.rawIdCount);
  console.log('totalAwards:', b?.stats?.totalAwards);
  console.log('totalNotices:', b?.stats?.totalNotices);
  console.log('totalSpend:', b?.stats?.totalSpend);
  console.log('topSuppliers:', b?.topSuppliers?.length);
});
"
```

Record the totalAwards and totalNotices numbers. Compare against the pre-fix MoJ dossier in `~/.pwin/intel/buyers/` (if a recent one exists). Document the gap in the playbook (Step 3).

- [ ] **Step 3: Append a section to the playbook**

Append to `pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md`:

```markdown

## Section: 2026-04-27 buyer alias resolution fix

Two-part fix landed for the buyer-side alias problem:

1. **Lookup tool wiring.** `get_buyer_profile` (and the underlying `buyerProfile`
   in `pwin-platform/src/competitive-intel.js`) now resolves the search term to
   a canonical entity via `_resolveBuyerCanonical` and aggregates awards across
   every raw buyer row linked to that canonical. Previously: raw `LIKE` against
   `buyers.name`, returning fragments. Now: one consolidated profile per
   canonical buyer.

2. **Alias backfill.** `agent/backfill_buyer_aliases.py` walks orphan raw rows
   and inserts new alias entries based on rule-based tidying (trailing
   punctuation, "DoJ -" prefix strip, "Secretary of State for X acting
   through Y" preamble strip, brand-in-parentheses extraction, HM preamble
   strip). Re-running `load-canonical-buyers.py` afterwards re-links raw
   buyers via the new aliases.

### Numbers

| Metric | Before | After |
|---|---:|---:|
| `buyers.canonical_id` populated | 27,807 / 55,335 (50.3%) | <FILL IN> |
| MoJ within-plausible orphan rate | 12% | <FILL IN> |
| Cabinet Office orphan rate | 26% | <FILL IN> |
| Treasury orphan rate | 30% | <FILL IN> |
| MoJ dossier — totalAwards | <FILL IN> | <FILL IN> |

### What's left for a future pass

- Sub-organisation handling (Defence Digital, DE&S, DSTL etc.) — separate
  design decision, not done in this fix.
- Ambiguous-match cases skipped by the backfill — review manually if the
  count is material.
- Departments still above 10% residual orphan — manual review.
```

Replace the `<FILL IN>` markers with the numbers measured in Steps 1 and 2.

- [ ] **Step 4: Commit**

```bash
git add pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md
git commit -m "docs(intel): record buyer alias resolution fix in playbook"
```

---

## Task 8: Update the action notes

**Files:**
- Modify: `C:/Users/User/Documents/Obsidian Vault/wiki/actions/pwin-buyer-alias-resolution.md`
- Modify: `C:/Users/User/Documents/Obsidian Vault/wiki/actions/pwin-canonical-buyer-alias-coverage-backfill.md`

- [ ] **Step 1: Mark both action notes as done**

In each of the two action files, change the frontmatter `status: pending` to `status: done`, add a `closed: 2026-04-27` line, and append a brief note at the end:

```markdown

## Closed 2026-04-27

Fixed via:
- Lookup wiring: `pwin-platform/src/competitive-intel.js` `buyerProfile()` now uses `_resolveBuyerCanonical` and aggregates across all raw IDs linked to canonical.
- Alias backfill: `pwin-competitive-intel/agent/backfill_buyer_aliases.py` adds rule-based variant aliases.

See `pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md` (2026-04-27 section) for before/after numbers and known limits.

Sub-organisation handling (Defence Digital etc.) and the manual-review pass on residual orphans remain as separate follow-up items.
```

- [ ] **Step 2: Commit**

```bash
git add "C:/Users/User/Documents/Obsidian Vault/wiki/actions/pwin-buyer-alias-resolution.md" \
        "C:/Users/User/Documents/Obsidian Vault/wiki/actions/pwin-canonical-buyer-alias-coverage-backfill.md"
git commit -m "docs(actions): close buyer alias resolution actions"
```

---

## Self-review

- **Spec coverage:** every spec section maps to a task. Lookup tool fix → Tasks 1, 2, 3. Alias backfill → Tasks 4, 5, 6. Validation → Task 7. Action note close-out → Task 8. Out-of-scope items (manual review of long tail, sub-org handling) explicitly deferred in the playbook update.
- **Placeholder scan:** the playbook update has `<FILL IN>` markers — these are intentional, filled at run time with the numbers measured in Step 1/2. No other placeholders.
- **Type consistency:** `_resolveBuyerCanonical` return shape (`canonicalId`, `canonicalName`, `canonicalType`, `rawBuyerIds`, `fragmented`, `ambiguous`) is consumed in Task 2 and matches the resolver's actual output. Snake-case Python module name `backfill_buyer_aliases` matches the test import.
