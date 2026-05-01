---
title: Fix the buyer alias problem in the procurement database
date: 2026-04-27
status: approved
author: pfenton
---

# Fix the buyer alias problem in the procurement database

## The problem

When we ask the procurement database for everything about a buyer (e.g. Ministry of Justice), we only find a fraction of the records. Today: 41% of raw buyer rows in the database link to a master list entry. The other 59% are stranded.

Two things cause this:

1. **The lookup tool ignores the master list.** `get_buyer_profile` in `pwin-platform/src/competitive-intel.js` does a fuzzy text search against raw names and never consults `canonical_buyer_aliases`.
2. **The master list is too thin.** Each master entry has roughly 2 spellings registered. Real raw data carries the same buyer under a dozen variants — full stops, capitalisation, legal preambles ("Secretary of State for X acting through Y"), prefixes ("DoJ - "), brand-in-parentheses forms.

The bias falls on Contracts Finder data (it always appends a full stop) and on central government records (which carry legal preambles). Those are exactly the records the buyer dossiers most need.

## Out of scope

The following are real problems but explicitly NOT being fixed in this work:

- Manual review of the worst-offender departments (Foreign Office, Cabinet Office, Treasury, Health). Deferred until we see what the automated fix achieves.
- Sub-organisation handling (Defence Digital → its own master entry vs alias to Ministry of Defence). Separate design call.
- Replacing the alias-table approach with fuzzy resolution (Splink or similar). Considered and deferred — try the cheap fix first, decide whether bigger work is needed afterwards.

## Two pieces of work

### Piece 1 — Wire the buyer lookup tool through the master list

**File:** `pwin-platform/src/competitive-intel.js`, function `buyerProfile()`.

**Behaviour change:**

1. Normalise the search term (lowercase, trim whitespace, strip trailing punctuation).
2. Look it up against `canonical_buyer_aliases` to get a master ID.
3. If found: pull all raw buyer rows linked to that master ID, aggregate awards/notices across them, return one consolidated buyer profile.
4. If not found: fall back to today's behaviour (raw `LIKE '%name%'`) and log a warning identifying the unmatched lookup, so coverage gaps surface.

**Pattern:** mirror what `supplierProfile()` in the same file already does via `v_canonical_supplier_wins`. The supplier half of the canonical pattern is wired in. The buyer half isn't.

**Sanity-check tests:**
- "MOD" resolves to Ministry of Defence
- "DfT" resolves to Department for Transport
- "Ministry of Justice" returns one consolidated profile, not 10 fragments
- "Some Made-Up Buyer" falls back gracefully and logs a warning

### Piece 2 — Backfill the master list

**New file:** `pwin-competitive-intel/agent/backfill-buyer-aliases.py`.

**What it does:** walk every raw buyer name in `buyers`, apply tidying rules, and where a tidied name exact-matches a `canonical_name` or `abbreviation` in `canonical_buyers`, insert a new row into `canonical_buyer_aliases`.

**Tidying rules (applied in order):**

1. Lowercase and trim.
2. Strip trailing punctuation: full stop, comma, semicolon.
3. Strip leading prefixes: "DoJ - ", "MoD - ", "DfT - ", and similar abbreviation-then-dash patterns.
4. Strip "Secretary of State for X acting through Y" preambles → "Y".
5. Strip "The Common Services Agency (more commonly known as Z)" patterns → "Z".
6. Pull brands out of parentheses: "Crown Commercial Service (CCS)" → also try "Crown Commercial Service" and "CCS".
7. Strip "His Majesty's" / "Her Majesty's" / "HM" preambles where they aren't part of the canonical name.
8. Match the tidied result against `canonical_name` (lowercased) and `abbreviation` (lowercased) of every master entry.

**Match policy:**
- Only insert an alias on an exact match after tidying. Do not fuzzy match — a wrong fuzzy match silently corrupts data.
- Never overwrite or delete existing aliases.
- Skip raw names that match more than one master entry (ambiguous — leave for manual review).

**Output report at end:**
- Total raw names processed
- New aliases inserted
- Raw names still unmatched (count + sample of 50)
- Raw names matched to multiple master entries (count + sample)

**Idempotent:** safe to re-run; it skips aliases already in the table.

## How we'll know it worked

Run the orphan check across the same 10 departments documented in `wiki/actions/pwin-canonical-buyer-alias-coverage-backfill.md`:

| Dept | Today | Target |
|---|---:|---:|
| Foreign Office | 88% missing | <20% |
| Cabinet Office | 84% missing | <20% |
| Treasury | 60% missing | <20% |
| Health | 47% missing | <20% |
| Justice | 19% missing | <10% |
| Defence | 7% missing | <5% |
| Home Office | 5% missing | <5% |
| Work and Pensions | 2% missing | <5% |
| Education | 1% missing | <5% |

Plus a before/after comparison of one buyer dossier: pull Ministry of Justice through the new lookup and the old one, count how many records each finds. The gap quantifies the bias in pre-fix dossiers.

## Files touched

- `pwin-platform/src/competitive-intel.js` (modified — `buyerProfile()`)
- `pwin-competitive-intel/agent/backfill-buyer-aliases.py` (new)
- `pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md` (append a section recording what was learned)

## Risks

- **The script writes new rows to a live table.** Mitigation: run with `--dry-run` first, review the report, then run for real. The tidying rules are conservative (exact match only after tidying).
- **A tidying rule could over-strip a name.** Mitigation: report flags ambiguous matches; we review the sample before accepting.
- **The lookup change could regress a Qualify call site.** Mitigation: fallback path keeps the old behaviour for any term that doesn't resolve.
