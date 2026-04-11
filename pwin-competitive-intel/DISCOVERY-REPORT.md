---
document_type: discovery_sprint_report
subject: FTS canonical data layer — Phase 0 Discovery
parent_design: pwin-competitive-intel/CANONICAL-LAYER-DESIGN.md
status: complete
phase: 0
created: 2026-04-11
duration_minutes: ~60
db_snapshot:
  notices: 174817
  awards: 186229
  suppliers: 161120
  buyers: 24180
  size_mb: 602
---

# Discovery Sprint — Findings and Recommendation

This is the Phase 0 Discovery output for the FTS canonical data layer workstream defined in [CANONICAL-LAYER-DESIGN.md](CANONICAL-LAYER-DESIGN.md). Its purpose is to quantify the data quality problem before committing to the build, and to confirm or adjust the eight decisions in that register.

## Method

A series of plain SQL queries against the existing `db/bid_intel.db` SQLite database, no Splink yet. Splink was reserved for Phase 1 because the Discovery questions could be answered with deterministic queries — exact-match deduplication ceilings, value-distribution histograms, framework signal scans, and join-based fragmentation analysis. Total runtime: ~60 minutes including a schema read and a parser code inspection.

## Headline numbers

| Metric | Value | Note |
|---|---|---|
| Raw notices | 174,817 | The unfiltered dataset |
| Raw awards | 186,229 | ~1.07 awards per notice |
| Active awards with non-null values | 151,936 | ~18% of active awards have null gross value (structural, not recent) |
| Awards ≥ £1m | **51,286** | The headline addressable universe |
| Awards ≥ £2m | **41,889** | The "other services" filter outcome |
| Awards ≥ £3m | **36,701** | Tighter alternative |
| Distinct buyers in ≥£1m universe | 7,458 | Before canonicalisation |
| Distinct suppliers in ≥£1m universe | 67,998 | Before canonicalisation |

The addressable universe is somewhat larger than my pre-Discovery estimate (~20–30k notices) but still very tractable.

## Findings — what's worse than expected

### F1. Buyer fragmentation is severe and uneven

A simple lowercase + trim normalisation of `buyers.name` collapses **24,180 raw buyer rows to 9,535 unique names** — meaning **60.6% of buyer rows are exact-match duplicates**. After Splink fuzzy matching this will collapse further, likely to **4,000–6,000 true canonical buyers**.

The fragmentation is concentrated in a small number of mega-buyers:

| Authority | Variant count (exact name match) | Notes |
|---|---|---|
| Ministry of Defence | **1,042 IDs** sharing the literal string "MINISTRY OF DEFENCE" | Plus ~290 more under DE&S/DSTL/DIO/MoD subsidiary patterns. Total MoD-family: ~1,334 |
| NHS Wales SSP | 155 | Welsh shared services |
| UK Research & Innovation | 104 | |
| British Council | 104 | |
| NHS England | 62 | |
| Transport for London | 62 | |
| Crown Commercial Service | 8+ visible variants | Including "The Minister for the Cabinet Office acting through Crown Commercial Service" with multiple distinct rows |
| London Borough of Haringey | 52 | |
| Procurement and Logistics Service | 55 | NI shared services |
| Scottish Government | 53 | |

By contrast, smaller authorities show low fragmentation — Home Office: only 60 buyer rows total across all variants. **Fragmentation is concentrated in a small number of authorities and is therefore tractable with a hand-curated canonical glossary on top of Splink.**

### F2. Framework references are completely absent from the ingest

This is the single most actionable finding. The current ingest at [agent/ingest.py:410-475](agent/ingest.py#L410-L475) captures `procurementMethod`, `procurementMethodDetails`, `legalBasis`, `mainProcurementCategory` from each OCDS release — but **drops** `tender.frameworkAgreement` and `relatedProcesses` entirely. These are standard OCDS fields the Find a Tender publisher emits, including:

- `tender.techniques.frameworkAgreement.isFrameworkAgreement` (boolean)
- `tender.techniques.frameworkAgreement.periodEnd` (date)
- `tender.techniques.frameworkAgreement.maximumValue` (object)
- `relatedProcesses` (array of `{relationship: ["framework"], identifier: <parent OCID>, ...}`)

Net effect: **zero** of the 51,286 ≥£1m awards have any framework hint in `procurement_method_detail`. Direct-text scanning of titles and descriptions for the 8 CCS framework names is also dead — MCF4 returns 5 mentions, DOS6 returns 1, Tech Services returns 2. Frameworks simply aren't named in notice text.

**Implication:** Decision C06 (deterministic framework lookup + LLM adjudication) is **non-viable until the ingest is patched** to capture the framework fields. Without the patch, the deterministic half of C06 collapses entirely and every classification has to go through the LLM classifier — expensive and unnecessary.

### F3. Value data has obvious unit/currency outliers

Top buyer by total value across active ≥£1m awards is "Salisbury NHS Foundation Trust" with **£2,001,508m (£2 trillion)** across just 5 awards. Other obvious outliers:

- YPO: £1,848,195m total
- Police, Fire and Crime Commissioner for Northamptonshire: £352,000m
- NHS Shared Business Services: £346,252m
- London Borough of Newham: £269,100m

These are framework ceilings and possibly currency unit confusion (€/£/k/m) being recorded as individual award values. The canonical layer needs an outlier-detection step that flags awards above plausibility thresholds (~£500m+) for review and stores them separately rather than letting them poison aggregations.

### F4. Companies House enrichment has barely run at scale

Only **234 of 43,838** suppliers with CH numbers are CH-enriched (`ch_status IS NOT NULL`). The recent indentation bug we fixed today (commit `4e5fcc8`) blocked the cron for ~5 days, but that doesn't account for the gap — if the cron had ever run reliably at the `--limit 200` cap, we should see thousands of enriched suppliers, not 234. At the current rate, full enrichment of the 43,838 suppliers with CH numbers would take ~220 nights (over 7 months). **The enrichment cron's pace and history need investigating independently — the indentation fix alone will not catch us up.**

## Findings — what's better than expected

### F5. The buyer universe was misreported in CLAUDE.md

CLAUDE.md states the database holds "118k buyers." The actual count is **24,180** raw rows, which becomes **~9,535 after exact-match dedup** and probably **4,000–6,000 after Splink**. That's an order of magnitude smaller than the doc implies and dramatically more tractable. CLAUDE.md should be corrected.

### F6. Value distribution is clean above £1m

Once you filter to active awards with values, the £1m+ band is **33.8% of the universe** (51k of 152k) — a meaningful slice, not a long tail. The user-chosen value thresholds (£1m consulting, £2m+ other) are well-calibrated against the actual distribution.

### F7. Supplier dedup ceiling is healthier than feared

161k → 103k after lowercase+trim (35.7% reduction, 57k duplicate rows removed). Many of the 72.8% without CH numbers will turn out to be the same companies fragmented across name variants. The real canonical supplier count after Splink is likely **60,000–80,000**, of which only ~3,000–5,000 fall inside the ≥£1m addressable universe.

## Confidence in each Decision Register entry after Discovery

| Decision | Status | Change |
|---|---|---|
| C01 — Internal tooling only | **Confirmed** | None |
| C02 — Two consumers, one canonical layer | **Confirmed** | None |
| C03 — Value threshold filtering | **Confirmed and quantified** | £1m gives 51k awards, £2m gives 42k awards. Locks at the user's chosen levels. |
| C04 — Framework-lot taxonomy not CPV | **Confirmed** | None |
| C05 — Eight CCS frameworks | **No change** | Still the right candidate set; will validate during Phase 1 once framework data is recoverable |
| **C06 — Hybrid classification** | **Blocked by upstream gap** | The deterministic half requires the ingest patch (F2). Without it, only the LLM half is viable. **Adds the ingest patch as Phase 1 task #1.** |
| C07 — Splink for entity resolution | **Confirmed and clearly worth it** | F1 shows 60% raw fragmentation; Splink is the right tool |
| C08 — Pipeline-first architecture | **Confirmed** | None |

## Decision gate

**Does the scope match the budget?** Yes — with one structural addition: **the ingest patch becomes Phase 1 task #1**. The patch is small (1–2 days) and unblocks Decision C06 cleanly. Without it, the deterministic shortcut in C06 is dead and the whole classification approach collapses onto the LLM, which is wasteful for the framework call-off subset.

**Recommendation: proceed to Phase 1.**

## Phase 1 task list (revised in light of Discovery)

In priority order:

1. **Patch the ingest to capture OCDS framework fields** (1–2 days)
   - Extend `notices` table or add a new `framework_links` table
   - Parse `tender.techniques.frameworkAgreement.*` and `relatedProcesses` in `upsert_notice`
   - Re-import the OCP bulk file (~4 min) to back-populate framework references for the historical universe
   - Verify framework coverage on a few known cases (e.g. CCS-procured frameworks)

2. **Run Splink against the buyer table to produce a baseline canonical map** (~1 day)
   - Install Splink + DuckDB (one new Python dependency)
   - Configure block-by-postcode or block-by-first-3-letters of name
   - Train against the obvious mega-buyer cases (MoD, NHS variants, CCS) as positive labels
   - Output: `canonical_buyers` table with `canonical_id` linking back to raw `buyer_id` rows
   - Target: collapse 24k → 4–6k

3. **Add value-outlier detection** (~2 hours)
   - Sanity check at ingest time: flag awards with `value_amount_gross > £500m` for review
   - Store flagged awards in a `suspect_values` table; exclude from aggregations until reviewed

4. **Investigate CH enrichment cron history** (~1 hour)
   - Independent of today's indentation fix
   - Decide whether to lift the `--limit 200` cap and increase nightly throughput
   - At ~600ms per CH call this is ~2 minutes per 200, so a 1000-row cap would still complete in ~10 minutes

5. **Run Splink against the supplier table** (~1 day)
   - Same approach as buyer dedup, blocked by postcode + lowercased name token
   - Produce `canonical_suppliers` table
   - Target: collapse 161k → 60–80k canonical, with the ≥£1m universe condensed to ~3–5k

6. **Defer: CH-register fuzzy-match recovery for the 117k name-only suppliers**
   - Real work, but lower value than the items above
   - Park until canonical layer exists and we can scope the recovery against the £1m+ universe specifically

## Open issues to flag

- **CLAUDE.md needs updating** — buyer count line is wrong (118k vs actual 24k), and the framework-data gap should be documented as a known limitation until the patch lands
- **The CH enrichment near-zero progress** is a separate puzzle from today's indentation fix — needs root-causing
- **Award date data is unreliable** — only 67 awards have a 2025 award_date set despite tens of thousands of 2025 awards by `published_date`. The ingest is probably populating `notices.published_date` correctly but not `awards.award_date`. Worth investigating during the framework patch since both touch the same parser

## Sign-off

Discovery complete on 2026-04-11. All eight decisions in the register confirmed (C06 with the upstream blocker). Proceeding to Phase 1 with the ingest patch as task #1.
