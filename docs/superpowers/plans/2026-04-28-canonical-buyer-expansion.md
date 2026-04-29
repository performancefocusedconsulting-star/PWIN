# Canonical Buyer Expansion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the canonical-buyer coverage gap so that all bid-relevant UK public buyers (police forces, universities, fire authorities, the missing Whitehall bodies, multi-academy trusts, housing associations) resolve to a master entity. Lift roll-up coverage from 56% of notices today to 90%+ and fix the alias-normaliser shortcomings that cause case-only and "Ltd vs Limited" misses.

**Architecture:** Reuse the existing two-table canonical layer (`canonical_buyers`, `canonical_buyer_aliases`). Each new category becomes a hand-curated knowledge JSON in `pwin-platform/knowledge/`, merged into the master glossary at `~/.pwin/platform/buyer-canonical-glossary.json` by `pwin-platform/scripts/seed-canonical-buyers.py`, then loaded into the database by `pwin-competitive-intel/agent/load-canonical-buyers.py` and supplemented by `agent/backfill-buyer-aliases.py`. The normaliser fix is a code change to two mirrored functions plus a re-run.

**Tech Stack:** Python 3.9+ stdlib only (no new deps), SQLite, JSON knowledge files. Authoritative source registers: GOV.UK organisations API (already wired), Home Office police list, Office for Students provider register, National Fire Chiefs Council list, DfE "Get Information About Schools" CSV, Regulator of Social Housing CSV.

---

## File Structure

**New knowledge files** (committed to git):
- `pwin-platform/knowledge/police-forces.json` — 43 territorial forces + Met + City of London + BTP + CNC + MoD Police + PSNI + Police Scotland + 8 joint procurement bodies + 43 PCCs
- `pwin-platform/knowledge/universities.json` — ~140 UK universities + Russell Group + UCAS-listed degree-awarding bodies
- `pwin-platform/knowledge/fire-and-rescue.json` — 50 territorial fire authorities (England 45, Scotland 1, Wales 3, NI 1) + National Fire Chiefs Council
- `pwin-platform/knowledge/whitehall-topup.json` — bodies missing from the GOV.UK fetch (FCDO, National Highways, HEE, NAO, etc.)
- `pwin-platform/knowledge/multi-academy-trusts.json` — generated from DfE GIAS CSV (~2,500 trusts)
- `pwin-platform/knowledge/housing-associations.json` — generated from Regulator of Social Housing CSV (~1,500 providers)

**New loader scripts** (committed to git):
- `pwin-platform/scripts/seed-mat-from-gias.py` — fetches DfE GIAS CSV and produces multi-academy-trusts.json
- `pwin-platform/scripts/seed-housing-from-rsh.py` — fetches Regulator of Social Housing CSV and produces housing-associations.json

**Modified scripts** (committed to git):
- `pwin-platform/scripts/seed-canonical-buyers.py` — six new merge calls, one per knowledge file
- `pwin-competitive-intel/agent/load-canonical-buyers.py` — strengthen `norm()`
- `pwin-competitive-intel/agent/backfill-buyer-aliases.py` — strengthen `_norm()` and `candidates_for()` to mirror

**Updated docs / memory** (committed / saved):
- `CLAUDE.md` — Known Limitations section: refresh canonical coverage numbers
- `~/.claude/projects/c--Users-User-Documents-GitHub-PWIN/memory/project_canonical_buyer_coverage_gap.md` — log the expansion

**Runtime artefacts** (NOT committed):
- `~/.pwin/platform/buyer-canonical-glossary.json` — regenerated each task
- `pwin-competitive-intel/db/bid_intel.db` — re-loaded each task

---

## Conventions used in every task

**Verification queries** — every task ends with a query that measures coverage delta. The plan shows the expected direction (counts go up) but not exact numbers, since we don't know them until the data lands. Steps that say "expect X to increase by ≥Y" are minimum acceptance bars.

**Idempotent runs** — `seed-canonical-buyers.py --skip-fetch` reuses the cached GOV.UK fetch instead of re-hitting the API. `load-canonical-buyers.py` always clears + reloads canonical tables. `backfill-buyer-aliases.py` only inserts new aliases. Safe to re-run every task.

**Commit cadence** — commit after each task. The knowledge JSON, the modified seed script, the regenerated glossary location is documented but the JSON itself is not committed (it lives in `~/.pwin`).

**The 0-baseline measurement** is run once at the very start of Task 1 and once at the very end of Task 8, so we can quote the headline figure ("X% → Y%").

---

### Task 0: Baseline measurement

**Files:**
- Read: `pwin-competitive-intel/db/bid_intel.db`
- Create (working notes only, not committed): scratch output

- [ ] **Step 1: Take the baseline snapshot**

Run from repo root:

```bash
cd pwin-competitive-intel && python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()

cur.execute('SELECT COUNT(DISTINCT ocid) FROM notices')
total = cur.fetchone()[0]
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower''')
mapped = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM canonical_buyers')
ents = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM canonical_buyer_aliases')
als = cur.fetchone()[0]

print(f'BASELINE 2026-04-28')
print(f'  Canonical entities:  {ents:,}')
print(f'  Canonical aliases:   {als:,}')
print(f'  Notices total:       {total:,}')
print(f'  Notices mapped:      {mapped:,}  ({100*mapped/total:.2f}%)')
print(f'  Notices unmapped:    {total-mapped:,}  ({100*(total-mapped)/total:.2f}%)')
PY
```

Expected output: ~1,939 entities, ~282,997 mapped (~55.6%). Save these numbers — they are the headline baseline that goes into the final commit message and CLAUDE.md update.

- [ ] **Step 2: Save the baseline to a working note**

Append the captured numbers to `docs/superpowers/plans/2026-04-28-canonical-buyer-expansion.md` under a new `## Baseline` section at the bottom of the file. We compare against this at the end.

- [ ] **Step 3: Commit the baseline note**

```bash
git add docs/superpowers/plans/2026-04-28-canonical-buyer-expansion.md
git commit -m "docs(intel): record canonical-buyer baseline before expansion"
```

---

### Task 1: Strengthen the alias normaliser

**Why first:** This is Problem B (alias gaps where the entity already exists). Fixing it reclaims tens of thousands of unmapped notices in one pass — and every subsequent task benefits because we won't keep re-tripping on Ltd/Limited and &/and variants.

**Files:**
- Modify: `pwin-competitive-intel/agent/load-canonical-buyers.py:51-57` (the `norm()` function)
- Modify: `pwin-competitive-intel/agent/backfill-buyer-aliases.py:52-57` (the `_norm()` function — must stay mirrored)
- Modify: `pwin-competitive-intel/agent/backfill-buyer-aliases.py:101-192` (`candidates_for()` — add suffix-decoration stripping)
- Test: `pwin-competitive-intel/agent/test_normaliser.py` (new)

- [ ] **Step 1: Write the failing test**

Create `pwin-competitive-intel/agent/test_normaliser.py`:

```python
"""
Unit tests for the canonical-layer name normaliser.

These cases all come from real publisher names found in the unmapped pile
on 2026-04-28. Each pair must collapse to the same normalised form so the
alias matcher resolves them to the same canonical entity.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Import the normaliser from both files — they MUST stay in sync.
import importlib.util

def _load(p):
    spec = importlib.util.spec_from_file_location("m", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

LOAD = _load(os.path.join(os.path.dirname(__file__), "load-canonical-buyers.py"))
BACK = _load(os.path.join(os.path.dirname(__file__), "backfill-buyer-aliases.py"))

EQUIVALENT = [
    # Caps vs mixed case
    ("UK SHARED BUSINESS SERVICES LIMITED", "UK Shared Business Services Ltd"),
    # & vs and
    ("UK RESEARCH & INNOVATION", "UK Research and Innovation"),
    # The-prefix
    ("THE UNIVERSITY OF BIRMINGHAM", "University of Birmingham"),
    # HM caps
    ("HM REVENUE & CUSTOMS", "HM Revenue & Customs"),
    # Trailing decoration
    ("Buckinghamshire Council - e-Tendering System", "Buckinghamshire Council"),
    ("Defra Network eTendering Portal", "Department for Environment, Food and Rural Affairs"),
    # PLC / Limited / Ltd variants
    ("Highways England Company Limited", "Highways England"),
    # Punctuation noise
    ("Ministry of Justice.", "Ministry of Justice"),
]

def test_normaliser_collapses_equivalents():
    failures = []
    for a, b in EQUIVALENT:
        na, nb = LOAD.norm(a), LOAD.norm(b)
        if na != nb:
            failures.append(f"  load.norm: {a!r} -> {na!r}   !=   {b!r} -> {nb!r}")
        na, nb = BACK._norm(a), BACK._norm(b)
        if na != nb:
            failures.append(f"  back._norm: {a!r} -> {na!r}   !=   {b!r} -> {nb!r}")
    assert not failures, "\n" + "\n".join(failures)

def test_normalisers_are_mirrored():
    # Both functions must produce identical output for any input.
    for a, b in EQUIVALENT:
        for s in (a, b):
            assert LOAD.norm(s) == BACK._norm(s), f"DIVERGENCE on {s!r}: load={LOAD.norm(s)!r} back={BACK._norm(s)!r}"

if __name__ == "__main__":
    test_normalisers_are_mirrored()
    test_normaliser_collapses_equivalents()
    print("OK")
```

- [ ] **Step 2: Run the test to confirm it fails**

```bash
cd pwin-competitive-intel && python agent/test_normaliser.py
```

Expected: `AssertionError` listing the cases where current `norm()` does NOT collapse (e.g. "the university of birmingham" vs "university of birmingham", "highways england company limited" vs "highways england"). The test failure shows exactly which cases the current code misses.

- [ ] **Step 3: Update `norm()` in load-canonical-buyers.py**

Replace the body of `norm()` at lines 51-57 with:

```python
def norm(s: str) -> str:
    """Normalise a name for matching.

    Rules (all applied lowercased):
      1. Lower + strip
      2. & ↔ and
      3. Ltd / Ltd. / PLC / PLC. ↔ Limited
      4. Drop leading 'the '
      5. Drop trailing decorative suffixes (' company limited', ' (CCS)', etc.)
      6. Drop trailing portal/eTendering noise
      7. Strip punctuation, collapse whitespace
    """
    s = (s or "").lower().strip()
    s = re.sub(r"\s*[\&]\s*", " and ", s)
    s = re.sub(r"\bplc\b\.?", "limited", s)
    s = re.sub(r"\bltd\b\.?", "limited", s)
    # Drop "the " prefix
    s = re.sub(r"^the\s+", "", s)
    # Drop "company limited" suffix that decorates an organisation name
    s = re.sub(r"\s+company\s+limited\s*$", "", s)
    # Drop trailing publisher portal decorations
    s = re.sub(r"\s+[-–—]\s+(e[- ]?tendering(?:\s+system)?|tendering\s+system|portal|esourcing|procurement\s+department|procurement\s+services?).*$", "", s)
    s = re.sub(r"\s+e[- ]?tendering(?:\s+system|\s+portal)?\s*$", "", s)
    s = re.sub(r"\s+network\s+e[- ]?tendering(?:\s+portal)?\s*$", "", s)
    # Strip punctuation
    s = re.sub(r"[,\.\(\)\-\'\"]", " ", s)
    return re.sub(r"\s+", " ", s).strip()
```

- [ ] **Step 4: Update `_norm()` in backfill-buyer-aliases.py to mirror exactly**

Replace lines 52-57 of `agent/backfill-buyer-aliases.py` with the same body. The two functions MUST be identical — divergence has caused real coverage bugs in the past, which is why `test_normalisers_are_mirrored` exists.

```python
def _norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"\s*[\&]\s*", " and ", s)
    s = re.sub(r"\bplc\b\.?", "limited", s)
    s = re.sub(r"\bltd\b\.?", "limited", s)
    s = re.sub(r"^the\s+", "", s)
    s = re.sub(r"\s+company\s+limited\s*$", "", s)
    s = re.sub(r"\s+[-–—]\s+(e[- ]?tendering(?:\s+system)?|tendering\s+system|portal|esourcing|procurement\s+department|procurement\s+services?).*$", "", s)
    s = re.sub(r"\s+e[- ]?tendering(?:\s+system|\s+portal)?\s*$", "", s)
    s = re.sub(r"\s+network\s+e[- ]?tendering(?:\s+portal)?\s*$", "", s)
    s = re.sub(r"[,\.\(\)\-\'\"]", " ", s)
    return re.sub(r"\s+", " ", s).strip()
```

- [ ] **Step 5: Run the test to confirm it passes**

```bash
cd pwin-competitive-intel && python agent/test_normaliser.py
```

Expected: `OK`

- [ ] **Step 6: Re-run the loader to apply the new normaliser to the existing glossary**

```bash
cd pwin-competitive-intel && python agent/load-canonical-buyers.py
```

Expected: validation block prints, "Total buyers" line and the four match-method counts. Note the absolute "Exact match" + "Normalised match" + "Prefix match" counts.

- [ ] **Step 7: Run the alias backfill to register tidied raw names against existing canonical entities**

```bash
cd pwin-competitive-intel && python agent/backfill-buyer-aliases.py --dry-run
```

Read the dry-run report. Expected: a non-zero "New aliases to insert" count (this is the win from the strengthened `_norm`). If it's zero, something is wrong — investigate before applying.

```bash
python agent/backfill-buyer-aliases.py
```

- [ ] **Step 8: Measure the coverage delta**

```bash
python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(DISTINCT ocid) FROM notices')
total = cur.fetchone()[0]
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower''')
mapped = cur.fetchone()[0]
print(f'After Task 1: {mapped:,} of {total:,} notices mapped ({100*mapped/total:.2f}%)')
PY
```

Expected: coverage rises from ~55.6% to at least 60% (~22,500+ additional notices mapped). Acceptance bar: ≥60%.

- [ ] **Step 9: Commit**

```bash
git add pwin-competitive-intel/agent/load-canonical-buyers.py \
        pwin-competitive-intel/agent/backfill-buyer-aliases.py \
        pwin-competitive-intel/agent/test_normaliser.py
git commit -m "fix(intel): strengthen canonical-layer normaliser

Adds rules for THE-prefix, company-limited suffix, &/and, PLC/Ltd, and
common publisher portal decorations (eTendering, Network eTendering Portal,
- Procurement Department, etc.). Mirrored across load-canonical-buyers.py
and backfill-buyer-aliases.py.

Coverage delta on full DB recorded in plan."
```

---

### Task 2: Police forces, PCCs, and joint procurement bodies

**Files:**
- Create: `pwin-platform/knowledge/police-forces.json`
- Modify: `pwin-platform/scripts/seed-canonical-buyers.py` (add merge call)
- No new test file — verification is by query.

- [ ] **Step 1: Build the police knowledge file**

Create `pwin-platform/knowledge/police-forces.json`. The full canonical list of UK territorial police forces is well-defined and stable; we hand-curate it from the Home Office's published list of police forces in England and Wales, plus Police Scotland, PSNI, and the four specialist forces.

The structure mirrors `central-buying-agencies.json`. Each force has its own canonical entity. Each PCC has its own canonical entity (separate legal personality from the force). Joint procurement bodies are separate canonical entities. The full file contents:

```json
{
  "_comment": "UK police forces, Police & Crime Commissioners, and joint procurement bodies. Hand-curated 2026-04-28 because none of these appear in the GOV.UK organisations API. Sources: Home Office list of police forces (England & Wales), Police Scotland and PSNI corporate registers. Aliases captured from real FTS publisher name variants observed in pwin-competitive-intel/db/bid_intel.db.",
  "version": "1.0",
  "source": "hand_curated_police",
  "last_updated": "2026-04-28",
  "entities": [
    {
      "canonical_id": "metropolitan-police-service",
      "canonical_name": "Metropolitan Police Service",
      "abbreviation": "MPS",
      "type": "Police force",
      "subtype": "Territorial police force (England)",
      "parent_ids": ["mayors-office-for-policing-and-crime"],
      "child_ids": [],
      "aliases": [
        "Metropolitan Police Service", "METROPOLITAN POLICE SERVICE",
        "Metropolitan Police", "Met Police", "MPS", "The Metropolitan Police"
      ],
      "status": "active",
      "source": "hand_curated_police"
    },
    {
      "canonical_id": "mayors-office-for-policing-and-crime",
      "canonical_name": "Mayor's Office for Policing and Crime",
      "abbreviation": "MOPAC",
      "type": "Police & Crime Commissioner",
      "subtype": "London PCC equivalent",
      "parent_ids": [],
      "child_ids": ["metropolitan-police-service"],
      "aliases": [
        "Mayor's Office for Policing and Crime", "MAYOR'S OFFICE FOR POLICE AND CRIME",
        "MAYORS OFFICE FOR POLICING AND CRIME", "MOPAC"
      ],
      "status": "active",
      "source": "hand_curated_police"
    },
    {
      "canonical_id": "city-of-london-police",
      "canonical_name": "City of London Police",
      "abbreviation": "CoLP",
      "type": "Police force",
      "subtype": "Territorial police force (England)",
      "parent_ids": [],
      "aliases": ["City of London Police", "CITY OF LONDON POLICE", "CoLP"],
      "status": "active",
      "source": "hand_curated_police"
    }
  ]
}
```

The full file must include all 43 territorial forces of England & Wales, the Met, City of London, the 4 specialist forces (BTP, CNC, MoD Police, Civil Nuclear Constabulary), Police Scotland (via Scottish Police Authority), PSNI, the matching 41 PCC entities (London + GMP + W Yorks + S Yorks + Merseyside have mayoral or non-PCC equivalents), and the joint procurement bodies (Yorkshire & Humber Police Procurement, South West Police Procurement Service, Joint Procurement Service for Surrey and Sussex Police, Police Digital Service, National Police Air Service operating body, Bluelight Commercial). Each entity gets all observed name variants from the raw `buyers` table as aliases.

To capture all the variants the publishers actually use, generate the alias seeds from the database before hand-finalising the JSON:

```bash
cd pwin-competitive-intel && python << 'PY'
import sqlite3, json
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('''SELECT b.name, COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
LEFT JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
WHERE cba.canonical_id IS NULL
  AND (LOWER(b.name) LIKE '%police%' OR LOWER(b.name) LIKE '%constabulary%')
GROUP BY b.name ORDER BY 2 DESC''')
for name, n in cur.fetchall():
    print(f'  {n:>5}  {name}')
PY
```

Use that list as the input for hand-curating the alias arrays. Do NOT skip a force just because no alias variant was found — every entity still gets at least its canonical name plus any obvious abbreviation.

- [ ] **Step 2: Wire the merge into `seed-canonical-buyers.py`**

In `pwin-platform/scripts/seed-canonical-buyers.py`:

(a) Add the constant near the other knowledge-file constants (around line 47):

```python
POLICE = os.path.join(KNOWLEDGE_DIR, "police-forces.json")
```

(b) In `main()`, after the existing devolved merge (around line 357), add:

```python
    print(f"\nMerging police forces and PCCs from {POLICE}...")
    police_added, police_merged = merge_hand_curated(glossary, POLICE)
    print(f"  +{police_added} new entities, {police_merged} alias merges")
```

(c) Update the `not_covered_yet` list in `transform()` (around line 179) — remove the police line.

- [ ] **Step 3: Regenerate the master glossary**

```bash
cd pwin-platform && python scripts/seed-canonical-buyers.py --skip-fetch
```

Expected: prints "+~100 new entities" or thereabouts (depending on exact count of forces + PCCs + joint bodies hand-curated).

- [ ] **Step 4: Reload into the database**

```bash
cd pwin-competitive-intel && python agent/load-canonical-buyers.py
```

Expected: total canonical entities goes from ~1,939 to ~2,030+.

- [ ] **Step 5: Run the alias backfill**

```bash
python agent/backfill-buyer-aliases.py --dry-run
```

Read the dry-run sample. Specifically scan for police-named raw names and confirm each one resolves to the right canonical entity (e.g. "Lancashire Constabulary" → `lancashire-constabulary`, not to some random parent body). If anything looks wrong, fix the knowledge file and go back to Step 3.

```bash
python agent/backfill-buyer-aliases.py
```

- [ ] **Step 6: Verify with the police lookup query**

```bash
python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
JOIN canonical_buyers cb USING(canonical_id)
WHERE cb.type IN ('Police force', 'Police & Crime Commissioner')
   OR cb.canonical_id LIKE '%police%' OR cb.canonical_id LIKE '%constabulary%' ''')
mapped_police = cur.fetchone()[0]
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
WHERE LOWER(b.name) LIKE '%police%' OR LOWER(b.name) LIKE '%constabulary%' ''')
total_police = cur.fetchone()[0]
print(f'Police notices mapped to canonical: {mapped_police:,} of {total_police:,} ({100*mapped_police/total_police:.1f}%)')

# Spot-check the Met
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
WHERE cba.canonical_id IN ('metropolitan-police-service', 'mayors-office-for-policing-and-crime')''')
print(f'Met Police (incl. MOPAC) notices: {cur.fetchone()[0]:,}')

# Spot-check Lancashire
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
WHERE cba.canonical_id = 'lancashire-constabulary' ''')
print(f'Lancashire Constabulary notices: {cur.fetchone()[0]:,}')
PY
```

Expected: police mapping rises from ~2% (198 / 9,960) to ≥90%. Met Police notices ≥800 (was 0 before). Lancashire ≥500.

- [ ] **Step 7: Commit**

```bash
git add pwin-platform/knowledge/police-forces.json pwin-platform/scripts/seed-canonical-buyers.py
git commit -m "feat(intel): add UK police forces, PCCs, and joint procurement bodies to canonical layer

Adds ~100 entities covering all 43 territorial forces of England & Wales,
Police Scotland, PSNI, the 4 specialist forces, the matching PCC entities,
and the joint procurement bodies (Yorkshire & Humber PP, South West PP,
Police Digital Service, NPAS, Bluelight Commercial).

Closes the gap that caused buyer dossiers on the Met, Lancashire,
Thames Valley, and other forces to fail with no procurement history."
```

---

### Task 3: Universities

**Files:**
- Create: `pwin-platform/knowledge/universities.json`
- Modify: `pwin-platform/scripts/seed-canonical-buyers.py` (add merge call)

- [ ] **Step 1: Generate the alias seed list from the database**

```bash
cd pwin-competitive-intel && python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('''SELECT b.name, COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
LEFT JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
WHERE cba.canonical_id IS NULL
  AND (LOWER(b.name) LIKE '%universit%' OR LOWER(b.name) LIKE '%college%' OR LOWER(b.name) LIKE '%school of%')
GROUP BY b.name ORDER BY 2 DESC LIMIT 300''')
for name, n in cur.fetchall():
    print(f'  {n:>5}  {name}')
PY
```

Use that list as the variant source for the alias arrays.

- [ ] **Step 2: Build the universities knowledge file**

Create `pwin-platform/knowledge/universities.json`. The authoritative source is the Office for Students Register of English Higher Education Providers, plus the Scottish Funding Council list, the Higher Education Funding Council for Wales list, and the Department for the Economy NI list. Together this is ~165 universities (degree-awarding bodies). Plus the higher-education buying consortia: SUPC (Southern Universities Purchasing Consortium), TUCO (The University Caterers Organisation), HEPCW (Higher Education Purchasing Consortium Wales), APUC (Advanced Procurement for Universities and Colleges), NEUPC (North East Universities Purchasing Consortium), LUPC (London Universities Purchasing Consortium).

File structure (showing first three entries — full file must contain all ~165 universities + 6 buying consortia):

```json
{
  "_comment": "UK universities and higher-education buying consortia. Hand-curated 2026-04-28 from the OfS Register, SFC list, HEFCW list, and DfE NI list. Aliases captured from real FTS publisher name variants in pwin-competitive-intel/db/bid_intel.db.",
  "version": "1.0",
  "source": "hand_curated_universities",
  "last_updated": "2026-04-28",
  "entities": [
    {
      "canonical_id": "university-of-birmingham",
      "canonical_name": "University of Birmingham",
      "abbreviation": "UoB",
      "type": "University",
      "subtype": "Russell Group",
      "parent_ids": [],
      "aliases": [
        "University of Birmingham", "UNIVERSITY OF BIRMINGHAM",
        "The University of Birmingham", "U of Birmingham"
      ],
      "status": "active",
      "source": "hand_curated_universities"
    },
    {
      "canonical_id": "university-of-newcastle-upon-tyne",
      "canonical_name": "Newcastle University",
      "abbreviation": null,
      "type": "University",
      "subtype": "Russell Group",
      "parent_ids": [],
      "aliases": [
        "Newcastle University", "NEWCASTLE UNIVERSITY",
        "University of Newcastle upon Tyne", "University of Newcastle"
      ],
      "status": "active",
      "source": "hand_curated_universities"
    },
    {
      "canonical_id": "north-eastern-universities-purchasing-consortium",
      "canonical_name": "North East Universities Purchasing Consortium",
      "abbreviation": "NEUPC",
      "type": "Central buying agency",
      "subtype": "Higher-education buying consortium",
      "parent_ids": [],
      "aliases": ["NEUPC", "North East Universities Purchasing Consortium"],
      "status": "active",
      "source": "hand_curated_universities"
    }
  ]
}
```

- [ ] **Step 3: Wire the merge into `seed-canonical-buyers.py`**

(a) Add to constants (around line 47):

```python
UNIVERSITIES = os.path.join(KNOWLEDGE_DIR, "universities.json")
```

(b) In `main()`, after the police merge:

```python
    print(f"\nMerging universities and HE consortia from {UNIVERSITIES}...")
    uni_added, uni_merged = merge_hand_curated(glossary, UNIVERSITIES)
    print(f"  +{uni_added} new entities, {uni_merged} alias merges")
```

(c) Remove "Universities (excluding HE buying consortia)" from `not_covered_yet` (line 184).

- [ ] **Step 4: Regenerate, reload, backfill**

```bash
cd pwin-platform && python scripts/seed-canonical-buyers.py --skip-fetch
cd ../pwin-competitive-intel && python agent/load-canonical-buyers.py
python agent/backfill-buyer-aliases.py --dry-run
# Inspect dry-run for ambiguity / mismatches, then:
python agent/backfill-buyer-aliases.py
```

- [ ] **Step 5: Verify**

```bash
python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
JOIN canonical_buyers cb USING(canonical_id)
WHERE cb.type IN ('University') OR cb.subtype = 'Higher-education buying consortium' ''')
print(f'University notices mapped: {cur.fetchone()[0]:,}')

cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
WHERE LOWER(b.name) LIKE '%universit%' ''')
print(f'University-named notices total: {cur.fetchone()[0]:,}')
PY
```

Expected: ≥80% of university-named notices now resolve.

- [ ] **Step 6: Commit**

```bash
git add pwin-platform/knowledge/universities.json pwin-platform/scripts/seed-canonical-buyers.py
git commit -m "feat(intel): add UK universities and HE buying consortia to canonical layer

Adds ~170 entities covering all UK degree-awarding universities (OfS register
+ SFC + HEFCW + DfE NI) plus the six HE buying consortia (SUPC, TUCO,
HEPCW, APUC, NEUPC, LUPC).

Closes ~26,000 unmapped notices from university buyers."
```

---

### Task 4: Fire & rescue authorities

**Files:**
- Create: `pwin-platform/knowledge/fire-and-rescue.json`
- Modify: `pwin-platform/scripts/seed-canonical-buyers.py` (add merge call)

- [ ] **Step 1: Generate the alias seed list**

```bash
cd pwin-competitive-intel && python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('''SELECT b.name, COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
LEFT JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
WHERE cba.canonical_id IS NULL
  AND (LOWER(b.name) LIKE '%fire %' OR LOWER(b.name) LIKE '%fire and rescue%' OR LOWER(b.name) LIKE '%fire & rescue%' OR LOWER(b.name) LIKE '%fire authority%')
GROUP BY b.name ORDER BY 2 DESC''')
for name, n in cur.fetchall():
    print(f'  {n:>5}  {name}')
PY
```

- [ ] **Step 2: Build the knowledge file**

Create `pwin-platform/knowledge/fire-and-rescue.json` with all 50 territorial fire and rescue authorities (England 45, Scottish FRS 1, Welsh FRSs 3, NI FRS 1) plus the National Fire Chiefs Council. Some fire authorities are governed by combined authorities, PCC-equivalents, or unitary councils — model as separate canonical entities since they publish under their own name in tender data.

Same structure as `police-forces.json`. Each entity has `type: "Fire and rescue authority"`.

- [ ] **Step 3: Wire the merge**

(a) Add constant in `seed-canonical-buyers.py`:

```python
FIRE_RESCUE = os.path.join(KNOWLEDGE_DIR, "fire-and-rescue.json")
```

(b) Add merge call after universities in `main()`:

```python
    print(f"\nMerging fire and rescue authorities from {FIRE_RESCUE}...")
    fire_added, fire_merged = merge_hand_curated(glossary, FIRE_RESCUE)
    print(f"  +{fire_added} new entities, {fire_merged} alias merges")
```

- [ ] **Step 4: Regenerate, reload, backfill**

```bash
cd pwin-platform && python scripts/seed-canonical-buyers.py --skip-fetch
cd ../pwin-competitive-intel && python agent/load-canonical-buyers.py
python agent/backfill-buyer-aliases.py --dry-run
python agent/backfill-buyer-aliases.py
```

- [ ] **Step 5: Verify**

```bash
python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
JOIN canonical_buyers cb USING(canonical_id)
WHERE cb.type = 'Fire and rescue authority' ''')
print(f'Fire & rescue notices mapped: {cur.fetchone()[0]:,}')
PY
```

Expected: ≥80% of fire-named notices now resolve.

- [ ] **Step 6: Commit**

```bash
git add pwin-platform/knowledge/fire-and-rescue.json pwin-platform/scripts/seed-canonical-buyers.py
git commit -m "feat(intel): add UK fire & rescue authorities to canonical layer

Adds 50 territorial fire authorities (England 45, Scotland 1, Wales 3,
NI 1) plus the National Fire Chiefs Council. Closes ~3,000 unmapped
notices."
```

---

### Task 5: Major missing Whitehall bodies

**Files:**
- Create: `pwin-platform/knowledge/whitehall-topup.json`
- Modify: `pwin-platform/scripts/seed-canonical-buyers.py` (add merge call)

- [ ] **Step 1: Audit which top-tier bodies are missing**

```bash
cd pwin-competitive-intel && python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
# Top 100 unmapped buyers — gives us the gap-list
cur.execute('''SELECT b.name, COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
LEFT JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
WHERE cba.canonical_id IS NULL
GROUP BY b.name ORDER BY 2 DESC LIMIT 100''')
for name, n in cur.fetchall():
    print(f'  {n:>5}  {name}')
PY
```

Filter the top 100 unmapped to identify central-government bodies that *should* be on the GOV.UK list but were missed (FCDO, Highways England / National Highways, Health Education England, NAO, HSE, MCA, DVLA, Atomic Weapons Establishment, UK Atomic Energy Authority, Sellafield, NDA Shared Services, Government Property Agency, etc.).

- [ ] **Step 2: Build the top-up knowledge file**

Create `pwin-platform/knowledge/whitehall-topup.json` with one entity per missing body. Each gets aliases from the audit step + canonical name + abbreviation.

- [ ] **Step 3: Wire the merge**

```python
WHITEHALL_TOPUP = os.path.join(KNOWLEDGE_DIR, "whitehall-topup.json")
```

```python
    print(f"\nMerging Whitehall top-up entities from {WHITEHALL_TOPUP}...")
    wt_added, wt_merged = merge_hand_curated(glossary, WHITEHALL_TOPUP)
    print(f"  +{wt_added} new entities, {wt_merged} alias merges")
```

- [ ] **Step 4: Regenerate, reload, backfill, verify**

```bash
cd pwin-platform && python scripts/seed-canonical-buyers.py --skip-fetch
cd ../pwin-competitive-intel && python agent/load-canonical-buyers.py
python agent/backfill-buyer-aliases.py --dry-run
python agent/backfill-buyer-aliases.py

# Verify each new entity resolves at least one raw buyer
python << 'PY'
import sqlite3, json
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
with open(r'C:/Users/User/Documents/GitHub/PWIN/pwin-platform/knowledge/whitehall-topup.json', encoding='utf-8') as f:
    wt = json.load(f)
for e in wt['entities']:
    cur.execute('SELECT COUNT(DISTINCT b.id) FROM buyers b WHERE b.canonical_id = ?', (e['canonical_id'],))
    n = cur.fetchone()[0]
    flag = '' if n > 0 else '   <-- ZERO matches, check aliases'
    print(f'  {n:>4}  {e["canonical_name"]}{flag}')
PY
```

Any zero-match entity should be re-checked — likely an alias gap.

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/knowledge/whitehall-topup.json pwin-platform/scripts/seed-canonical-buyers.py
git commit -m "feat(intel): top up canonical layer with Whitehall bodies missing from GOV.UK API

Adds FCDO, National Highways, Health Education England, NAO, HSE,
Maritime and Coastguard Agency, DVLA, UKAEA, AWE, Sellafield, NDA Shared
Services, Government Property Agency, and other top-tier bodies that
were absent from the GOV.UK organisations API or published under names
the API didn't surface."
```

---

### Task 6: Multi-academy trusts

**Files:**
- Create: `pwin-platform/scripts/seed-mat-from-gias.py` (new fetcher)
- Create: `pwin-platform/knowledge/multi-academy-trusts.json` (generated, committed)
- Modify: `pwin-platform/scripts/seed-canonical-buyers.py` (add merge call)

- [ ] **Step 1: Build the MAT fetcher**

Create `pwin-platform/scripts/seed-mat-from-gias.py`. Source: DfE "Get Information About Schools" (GIAS) — public CSV download at `https://get-information-schools.service.gov.uk/Downloads`. The relevant download is "Multi-academy trusts" (~2,500 active trusts). The CSV has columns including `GroupUID`, `GroupName`, `GroupType`, `GroupTypeID`, `Status`, plus Companies House number.

The script downloads the CSV (URL hard-coded, with a User-Agent header), filters to `Status = "Open"` and `GroupType` containing "trust", and emits a JSON file matching the same shape as `central-buying-agencies.json`. Each MAT becomes one canonical entity.

```python
"""seed-mat-from-gias.py — fetch DfE GIAS multi-academy trust register
and emit a canonical-glossary-shaped JSON. Stdlib only. Idempotent."""
import csv, io, json, os, re, sys, urllib.request
from datetime import datetime, timezone

GIAS_URL = "https://get-information-schools.service.gov.uk/Downloads/Group/Latest"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "knowledge", "multi-academy-trusts.json")

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:80] or "unknown"

def fetch_csv():
    req = urllib.request.Request(GIAS_URL, headers={"User-Agent": "PWIN/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(raw)))

def main():
    rows = fetch_csv()
    entities = []
    seen = set()
    for r in rows:
        if (r.get("Status") or "").strip().lower() != "open":
            continue
        gtype = (r.get("GroupType") or "").lower()
        if "trust" not in gtype and "multi-academy" not in gtype:
            continue
        name = (r.get("GroupName") or "").strip()
        if not name:
            continue
        cid = slugify(name)
        if cid in seen:
            cid = f"{cid}-{r.get('GroupUID')}"
        seen.add(cid)
        entities.append({
            "canonical_id": cid,
            "canonical_name": name,
            "abbreviation": None,
            "type": "Multi-academy trust",
            "parent_ids": ["department-for-education"],
            "child_ids": [],
            "aliases": [name, name.upper(), name.lower()],
            "status": "active",
            "source": "dfe_gias",
        })
    out = {
        "_comment": f"Fetched from DfE GIAS on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.",
        "version": "1.0",
        "source": "dfe_gias",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "entities": entities,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(entities)} MATs to {OUT}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the fetcher to produce the knowledge file**

```bash
cd pwin-platform && python scripts/seed-mat-from-gias.py
```

Expected: writes `pwin-platform/knowledge/multi-academy-trusts.json` with ~2,500 entities.

- [ ] **Step 3: Wire the merge**

```python
MAT = os.path.join(KNOWLEDGE_DIR, "multi-academy-trusts.json")
```

```python
    print(f"\nMerging multi-academy trusts from {MAT}...")
    mat_added, mat_merged = merge_hand_curated(glossary, MAT)
    print(f"  +{mat_added} new entities, {mat_merged} alias merges")
```

Remove "Schools and academy trusts" from `not_covered_yet`.

- [ ] **Step 4: Regenerate, reload, backfill**

```bash
cd pwin-platform && python scripts/seed-canonical-buyers.py --skip-fetch
cd ../pwin-competitive-intel && python agent/load-canonical-buyers.py
python agent/backfill-buyer-aliases.py
```

- [ ] **Step 5: Verify and review ambiguity**

The MAT names are short and may collide with school names that are not the trust ("Oasis Academy" both names a trust and many individual schools). Review the backfill dry-run carefully — flag ambiguous matches and either (a) tighten an alias, (b) drop the alias, or (c) leave the entity unmatched if that is the right answer.

```bash
python agent/backfill-buyer-aliases.py --dry-run | grep -A 2 "ambiguous" | head -50
```

- [ ] **Step 6: Commit**

```bash
git add pwin-platform/scripts/seed-mat-from-gias.py \
        pwin-platform/knowledge/multi-academy-trusts.json \
        pwin-platform/scripts/seed-canonical-buyers.py
git commit -m "feat(intel): add UK multi-academy trusts to canonical layer

Adds ~2,500 MATs from the DfE Get Information About Schools register.
The fetcher (seed-mat-from-gias.py) is idempotent — re-run quarterly
to pick up new trusts and trust closures.

All MATs roll up to department-for-education as parent."
```

---

### Task 7: Housing associations

**Files:**
- Create: `pwin-platform/scripts/seed-housing-from-rsh.py` (new fetcher)
- Create: `pwin-platform/knowledge/housing-associations.json` (generated, committed)
- Modify: `pwin-platform/scripts/seed-canonical-buyers.py` (add merge call)

- [ ] **Step 1: Build the housing fetcher**

Source: Regulator of Social Housing "list of registered providers" — published as Excel spreadsheet on `https://www.gov.uk/government/publications/current-registered-providers-of-social-housing`. The CSV alternative is the RSH "Statistical data return" provider register. ~1,500 active providers split between local authorities (already canonicalised) and private registered providers (housing associations + for-profit providers).

Script structure mirrors `seed-mat-from-gias.py`:

```python
"""seed-housing-from-rsh.py — fetch RSH registered-provider list and emit
a canonical-glossary-shaped JSON. Filters out the local-authority entries
(already canonical) and keeps only private registered providers."""
# (same shape as seed-mat-from-gias.py — fetch CSV, filter, emit JSON)
```

If the RSH publishes Excel only and not CSV, document the manual download step in the script's docstring and parse with `openpyxl` — or, better, document a manual one-time CSV export step and have the script consume the local CSV path.

- [ ] **Step 2: Run the fetcher**

```bash
cd pwin-platform && python scripts/seed-housing-from-rsh.py
```

Expected: writes `pwin-platform/knowledge/housing-associations.json` with ~1,500 entities (housing associations only, LAs filtered out).

- [ ] **Step 3: Wire the merge**

```python
HOUSING = os.path.join(KNOWLEDGE_DIR, "housing-associations.json")
```

```python
    print(f"\nMerging housing associations from {HOUSING}...")
    h_added, h_merged = merge_hand_curated(glossary, HOUSING)
    print(f"  +{h_added} new entities, {h_merged} alias merges")
```

- [ ] **Step 4: Regenerate, reload, backfill, verify**

```bash
cd pwin-platform && python scripts/seed-canonical-buyers.py --skip-fetch
cd ../pwin-competitive-intel && python agent/load-canonical-buyers.py
python agent/backfill-buyer-aliases.py --dry-run
python agent/backfill-buyer-aliases.py

python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
JOIN canonical_buyers cb USING(canonical_id)
WHERE cb.type IN ('Housing association', 'Registered provider') ''')
print(f'Housing notices mapped: {cur.fetchone()[0]:,}')
PY
```

- [ ] **Step 5: Commit**

```bash
git add pwin-platform/scripts/seed-housing-from-rsh.py \
        pwin-platform/knowledge/housing-associations.json \
        pwin-platform/scripts/seed-canonical-buyers.py
git commit -m "feat(intel): add UK housing associations to canonical layer

Adds ~1,500 private registered providers from the Regulator of Social
Housing register. Local-authority RPs filtered out — they are already
canonicalised through the ONS LA-codes route."
```

---

### Task 8: Final verification, dossier refresh, and documentation

**Files:**
- Modify: `CLAUDE.md` (Known Limitations and architecture state sections)
- Modify: `~/.claude/projects/c--Users-User-Documents-GitHub-PWIN/memory/project_canonical_buyer_coverage_gap.md`

- [ ] **Step 1: Final coverage measurement**

```bash
cd pwin-competitive-intel && python << 'PY'
import sqlite3
conn = sqlite3.connect('db/bid_intel.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM canonical_buyers')
ents = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM canonical_buyer_aliases')
als = cur.fetchone()[0]
cur.execute('SELECT COUNT(DISTINCT ocid) FROM notices')
total = cur.fetchone()[0]
cur.execute('''SELECT COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower''')
mapped = cur.fetchone()[0]

print(f'FINAL 2026-04-28')
print(f'  Canonical entities:  {ents:,}  (was 1,939)')
print(f'  Canonical aliases:   {als:,}')
print(f'  Notices mapped:      {mapped:,} of {total:,} ({100*mapped/total:.2f}%)  (was 55.6%)')

# Coverage by type
print()
print('  Top categories by mapped notices:')
cur.execute('''SELECT cb.type, COUNT(DISTINCT n.ocid) FROM notices n
JOIN buyers b ON n.buyer_id = b.id
JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
JOIN canonical_buyers cb USING(canonical_id)
GROUP BY cb.type ORDER BY 2 DESC LIMIT 15''')
for t, n in cur.fetchall():
    print(f'    {n:>7,}  {t or "(none)"}')
PY
```

Acceptance bar: ≥90% mapped. If not yet there, audit the remaining unmapped pile and decide whether (a) the gap is real (genuinely non-canonicalisable buyers), (b) a category we said we'd cover wasn't fully covered (loop back to its task), or (c) the alias normaliser has a remaining gap (loop back to Task 1).

- [ ] **Step 2: Dossier refresh trigger**

The buyer profile dossiers (Agent 2 buyer-intelligence skill output, MCP `get_buyer_profile`) read through canonical entities. Pre-Task-1 dossiers were built against the old roll-up. Add a memory entry recording the cut-off date so any future query knows to refresh dossiers older than this run.

```bash
cat > "$HOME/.claude/projects/c--Users-User-Documents-GitHub-PWIN/memory/project_dossier_refresh_2026_04_28.md" << 'EOF'
---
name: dossier_refresh_after_canonical_expansion
description: Buyer dossiers built before 2026-04-28 should be refreshed — canonical roll-up expanded substantially that day (police, universities, fire, MAT, housing, Whitehall top-up).
type: project
---

Canonical buyer layer expanded 2026-04-28 from 1,939 entities to ~6,200.
Coverage of contract notices rose from 55.6% to 90%+.

**Why:** Major categories (police forces, universities, fire authorities,
multi-academy trusts, housing associations, missing Whitehall bodies) were
added as canonical entities in a single planned push, so any buyer profile
or buyer-behaviour dossier built before this date saw a much narrower
data picture.

**How to apply:** When a user asks for or references a buyer dossier
(via `get_buyer_profile`, `get_buyer_behaviour_profile`, or the buyer-
intelligence skill), check the dossier's `generated_at` timestamp. If it
predates 2026-04-28, recommend a refresh before relying on the figures —
especially for police, university, fire, academy-trust, or housing-
association buyers.

The platform itself does not auto-invalidate stored dossiers. Refresh is
the consumer's responsibility.
EOF
```

Add the pointer to MEMORY.md:

```bash
# Append to the memory index
echo '- [project_dossier_refresh_2026_04_28.md](project_dossier_refresh_2026_04_28.md) — Buyer dossiers older than 2026-04-28 should be refreshed; canonical roll-up grew from 1,939 entities to ~6,200 that day.' \
  >> "$HOME/.claude/projects/c--Users-User-Documents-GitHub-PWIN/memory/MEMORY.md"
```

- [ ] **Step 3: Update CLAUDE.md**

In `CLAUDE.md`, under the "pwin-competitive-intel — Known Limitations" section (the bullet starting "Canonical entity layer."), update the numbers to reflect the new coverage. Add a one-line note about the 2026-04-28 expansion. Do not delete the historic note — keep it as decision history.

- [ ] **Step 4: Update the project memory entry**

Edit `~/.claude/projects/c--Users-User-Documents-GitHub-PWIN/memory/project_canonical_buyer_coverage_gap.md` to mark this expansion complete and to record the new coverage headline.

- [ ] **Step 5: Update the plan's `## Baseline` and append a `## Final` section**

Edit this plan file to record the final numbers under a new `## Final` section so the before/after delta is permanently captured in the plan document.

- [ ] **Step 6: Final commit**

```bash
git add CLAUDE.md docs/superpowers/plans/2026-04-28-canonical-buyer-expansion.md
git commit -m "docs(intel): record canonical buyer expansion (1,939 → ~6,200 entities, 55.6% → 90%+ coverage)

Closes the canonical-coverage gap that caused buyer dossiers to fail
on police forces, universities, fire authorities, multi-academy trusts,
and housing associations. Major categories now canonicalised:

  - Police forces, PCCs, joint procurement bodies (~100 entities)
  - Universities and HE buying consortia (~170 entities)
  - Fire & rescue authorities (50 entities)
  - Multi-academy trusts (~2,500 entities)
  - Housing associations (~1,500 entities)
  - Whitehall top-up (~30 entities missing from GOV.UK API)
  - Strengthened alias normaliser to handle Ltd/Limited, &/and, THE-prefix,
    and publisher portal decoration suffixes."
```

---

## Self-Review Notes

**Spec coverage:** Each of the seven user-agreed priority items has a dedicated task: Task 1 = alias normaliser, Task 2 = police, Task 3 = universities, Task 4 = fire, Task 5 = Whitehall top-up, Task 6 = MAT, Task 7 = housing. Task 0 establishes baseline; Task 8 records final delta and refreshes downstream consumers.

**Placeholders:** Each task has actual code blocks. Where the dataset is too large to inline (the full police list, the full universities list), the task gives the structure and the source register, plus a database query that surfaces the publisher variants for alias seeding. The MAT and housing-association files are auto-generated by committed scripts, so the file content is not hand-listed.

**Type consistency:** The canonical entity shape is fixed by the existing schema (`canonical_id`, `canonical_name`, `abbreviation`, `type`, `subtype`, `parent_ids`, `child_ids`, `aliases`, `status`, `source`). The new `type` values introduced — `Police force`, `Police & Crime Commissioner`, `University`, `Fire and rescue authority`, `Multi-academy trust`, `Housing association`/`Registered provider` — are consistently used in their respective task verifications. The merge function `merge_hand_curated()` is an existing function with a stable signature.

**Risk note:** The MAT and housing-association files have ~2,500 and ~1,500 entries respectively — many of those names are short and may collide ambiguously with other entities (a school's name, a company name). Tasks 6 and 7 each include an explicit "review the backfill dry-run for ambiguous matches" step. This is the highest-risk part of the plan.

---

## Baseline

Captured 2026-04-28 before any changes:

| Metric | Value |
|---|---|
| Canonical entities | 1,939 |
| Canonical aliases | 3,942 |
| Notices total | 509,048 |
| Notices mapped to a canonical buyer | 282,997 (55.59%) |
| Notices unmapped | 226,051 (44.41%) |
| Notice value mapped | £6,114bn of £8,519bn (71.77%) |

Note: notice value is heavily inflated by framework ceiling values (OCDS records framework *maximum* values, not realised spend). The notice-count figure is the more honest coverage measure.

## Progress checkpoint — 2026-04-28 end of session

**Tasks 0–3 complete.** Tasks 4–8 pending.

| Stage | Coverage | Entity count | Commits |
|---|---|---|---|
| Baseline | 55.59% (282,997 / 509,048) | 1,939 | `acae60e` (plan + baseline) |
| After Task 1 (normaliser) | 63.69% | 1,939 | `ee041ae`, `931990c` |
| After Task 2 (police) | 65.21% | 2,029 | `9960333` (parallel work), `f6da1dd` (SPA fix) |
| After Task 3 (universities) | **70.36%** | **2,083** | `abd34a7` |

**Net progress this session:** 55.59% → 70.36% notice coverage (+14.77pp), 1,939 → 2,083 canonical entities. Police-named notices now 97.7% mapped (was ~2%). University-named notices now 98% mapped (was 0%).

## Progress checkpoint — 2026-04-29 end of session

**Tasks 0–4 complete.** Tasks 5–8 pending.

| Stage | Coverage | Entity count | Commits |
|---|---|---|---|
| After Task 4 (fire & rescue) | **71.01%** | **2,236** | `02752bc`, `4b3d75b` (cleanup) |

**Net progress this session:** 70.36% → 71.01% (+0.65pp), 2,083 → 2,236 canonical entities. Fire & rescue notices: 3,174 mapped (106% of fire-named notices — captures aliases the raw query missed). `fire-and-rescue.json` cleaned: duplicates and trailing-whitespace aliases removed, IoW marked `status: historical`.

### How to resume

Next session should pick up **Task 5 (Whitehall top-up)** then continue through Tasks 6–8. The pattern is established:

1. Run the top-100-unmapped audit query to see what's left.
2. Build the knowledge JSON hand-curated from the unmapped list.
3. Wire merge into `seed-canonical-buyers.py` (add constant + call in `main()` before `write_output`).
4. Regenerate (`--skip-fetch`), reload (`load-canonical-buyers.py`), backfill, verify, commit.

**`seed-canonical-buyers.py` current state of `main()`** ends with:
```python
    print(f"\nMerging fire and rescue authorities from {FIRE_RESCUE}...")
    fire_added, fire_merged = merge_hand_curated(glossary, FIRE_RESCUE)
    print(f"  +{fire_added} new entities, {fire_merged} alias merges")

    write_output(glossary, args.output)
    print_stats(glossary)
```
New merges (WHITEHALL_TOPUP, MAT, HOUSING) go between the fire block and `write_output`.

### Open notes

- Tasks 6 & 7 still need URL/format confirmation for DfE GIAS and Regulator of Social Housing data sources at execution time.
- Acceptance bar for the whole programme is ≥90% notice coverage. At 71.01% with three tasks still to run (Whitehall top-up ~10,000+, MAT ~5,000, housing ~10,000). Remaining tasks should clear 90%.

## Final

(To be populated by Task 8, Step 5.)
