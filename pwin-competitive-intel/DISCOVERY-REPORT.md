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

## Addendum 1 — GOV.UK organisations glossary build (2026-04-11, post-Discovery)

After the initial Discovery findings the canonical buyer glossary build was started with GOV.UK organisations as the first source. This addendum captures the validation results and the follow-on findings, because the validation surfaced material new intelligence about FTS publisher behaviour that future sessions should not have to re-discover.

### Glossary build outcome

`pwin-platform/scripts/seed-canonical-buyers.py` fetches the GOV.UK organisations API (1,251 raw orgs across 63 pages) and produces a hierarchical canonical glossary at `~/.pwin/platform/buyer-canonical-glossary.json`. After filtering closed organisations: **1,090 active entities**, with proper parent-child relationships, aliases, and provenance. Top hierarchies match expectation: Cabinet Office (66 children), Home Office (57), MoD (56), MoJ (43), DfT (40), DHSC (39).

### Coverage of the £1m+ awards universe — 11.2%

When the glossary's exact aliases are matched against the FTS buyer names that appear in the ≥£1m awards universe (51,286 awards across 3,589 distinct normalised buyer names):

| Match type | Awards | % of universe |
|---|---|---|
| Raw exact alias match | 4,845 | 9.4% |
| Normalised alias match (additional) | 901 | 1.8% |
| Unmatched | 45,540 | 88.8% |

The 11.2% coverage is uncomfortable but clarifying — it confirms that **most £1m+ public sector procurement spend does not sit with central government departments**. The breakdown of the unmatched 88.8% by inferred category:

| Category | Awards | % of universe | Source needed |
|---|---|---|---|
| Local government | 15,345 | 29.9% | ONS Local Authority codes / Register |
| OTHER (mostly central buying agencies) | 15,354 | 29.9% | Hand curation (see below) |
| NHS | 10,246 | 20.0% | NHS ODS (Organisation Data Service) |
| Housing | 1,719 | 3.4% | Sector source TBD |
| Schools | 1,164 | 2.3% | DfE academy trust register |
| Universities / FE | 1,154 | 2.3% | UCAS / HESA / OfS |
| Police / fire | 558 | 1.1% | Home Office police force list + NFCC |

### F8. Central buying agencies dominate the unmatched OTHER bucket

The most consequential addendum finding: ~20% of all £1m+ awards (15,354 of 51,286) flow through **central buying aggregators that are not government departments and therefore not in the GOV.UK organisations index**. They are procurement consortia, frameworks, and central agencies that aggregate demand on behalf of many other entities. They issue framework agreements and run call-offs, but they aren't categorised as government bodies anywhere because they aren't.

The full catalogue of FTS name variants for the major central buying agencies, captured for the canonical glossary hand-curation step:

#### NHS Shared Business Services Limited (NHS SBS) — 1,712 awards across variants
- NHS Shared Business Services Limited (1,496)
- NHS Shared Business Services (150)
- NHS Shared Business Services Ltd (NHS SBS) (66)

#### Yorkshire Purchasing Organisation (YPO) — 1,113 awards
- YPO (861)
- Yorkshire Purchasing Organisation (252)

#### NHS National Services Scotland (NSS / Common Services Agency) — 1,239 awards across variants
- "The Common Services Agency (more commonly known as NHS National Services Scotland)" (751 + 404 + 32 + 9 + ...)
- NHS National Services Scotland (43)
- Note: trailing whitespace and punctuation variations create the multiple buckets — they are all the same entity

#### NHS Supply Chain — 720+ awards across operator variants
- NHS Supply Chain (324)
- NHS Supply Chain operated by North of England Commercial Procurement Collaborative (290)
- NHS Supply Chain operated by DHL Supply Chain Ltd acting as agent of Supply Chain Coordination Limited (39)
- NHS Supply Chain operated by Supply Chain Coordination Ltd (SCCL) (36)
- NHS Supply Chain Operated by DHL Supply Chain Limited acting as agent of Supply Chain Coordination Ltd (31)
- Note: SCCL is the canonical legal entity. The "operated by" prefixes are agent designations.

#### NHS Wales Shared Services Partnership (NWSSP) — 464 awards across variants
- NHS Wales Shared Services Partnership-Procurement Services (hosted by Velindre University NHS Trust) (293)
- NHS Wales Shared Services Partnership (88)
- Velindre NHS Trust, NHS Wales Shared Services Partnership - Procurement Services (51 + 12)
- NHS Wales Shared Services Partnership - Procurement Services (as hosted by Velindre University NHS Trust) (14)
- NWSSP Procurement (sourcing) (6)

#### "The Minister for the Cabinet Office acting through Crown Commercial Service" — 735 awards across variants
This is **CCS**, but the verbose legal-name form is the dominant publisher pattern and does not match the plain "Crown Commercial Service" alias in the GOV.UK glossary. **High-leverage alias addition.**
- The Minister for the Cabinet Office acting through Crown Commercial Service (665)
- The Minister for the Cabinet Office acting through Crown Commercial Service (CCS) (46)
- Minister for the Cabinet Office Acting through Crown Commercial Service (14)
- Minister for the Cabinet Office acting through the Cabinet Office (4)

#### Eastern Shires Purchasing Organisation (ESPO) — 521 awards
- ESPO (515)
- ESPO on behalf of Leicestershire County Council (3)
- Leicestershire County Council t/a Leicestershire Traded Services (c/o ESPO) (1)
- Leicestershire County Council, trading as ESPO (1)

#### Procurement and Logistics Service NI (PaLS / BSO PaLS) — 659 awards across variants
- Procurement and Logistics Service (491)
- BSO Procurement and Logistics Service (59)
- Business Services Organisation, Procurement and Logistics Service (47)
- Business Services Organisation Procurement and Logistics Service (45)
- Regional Business Services Organisation Procurement and Logistics Service (10)
- Procurement & Logistics Service (7)

#### Fusion21 Members Consortium — 344 awards
- Fusion21 Members Consortium (344)

#### Scotland Excel — 295 awards
- Scotland Excel (295)

#### NHMF (NPC) LIMITED — 605 awards
- Single name variant only. **Identity to confirm at curation time** — likely a housing-sector procurement vehicle but the abbreviation is not in any obvious source. Worth resolving before locking the glossary.

#### Crescent Purchasing Consortium (CPC) — 211 awards
- CRESCENT PURCHASING LIMITED (117)
- Crescent Purchasing Consortium Limited (59)
- Crescent Purchasing Consortium (CPC) (26)
- Crescent Purchasing Consortium (9)

#### Scape Group — 81 awards across variants
- Scape Procure Limited (29)
- Scape Group Limited (25)
- Scape Procure Scotland Ltd (16)
- Scape Group Limited (trading as SCAPE) (6)
- Scape Procure Limited (trading as SCAPE) (4)

#### LHC Procurement Group — 43 awards
- LHC Procurement Group for the Welsh Procurement Alliance (WPA) (32)
- LHC Procurement Group for the Scottish Procurement Alliance (SPA) (9)
- (Plus another set of variants under "Scottish Procurement Alliance" mapping back to LHC)

#### HealthTrust Europe (HTE) — 157+ awards across hospital-trust variants
- HealthTrust Europe LLP (HTE) acting as agent for the University Hospitals of Coventry... (41)
- HealthTrust Europe LLP (HTE) acting on behalf of [Trust X] (multiple variants per trust)
- Note: HTE acts as agent for many NHS trusts, each with its own bracketed variant. The canonical entity is HTE; the on-behalf-of suffixes are valuable provenance but should not fragment the canonical mapping.

#### Welsh Government Commercial Delivery — 14 awards
- Welsh Government Commercial Delivery (14)

#### Northern Ireland Public Sector Bodies — multiple
- Education Authority NI (267) — already large enough to warrant entry
- Other devolved entities to be catalogued

#### Higher Education Purchasing Consortia
- APUC Limited (123) / APUC Ltd (11) — Advanced Procurement for Universities and Colleges (Scotland)
- Southern Universities Purchasing Consortium (SUPC) (65)

#### NEPO — North East Procurement Organisation — 82 awards across legal-name variants
- THE ASSOCIATION OF NORTH EAST COUNCILS LIMITED T/A NORTH EAST PROCUREMENT ORGANISATION (76)
- Association of North East Councils Limited trading as NEPO (2)
- The Association of North East Councils, trading as NEPO (2)
- Association of North East Councils Ltd trading as NEPO (1)
- NEPO (1)

### Implications for Phase 1 sequencing

The original Phase 1 task list assumed the deterministic canonical glossary could be built with GOV.UK alone. Reality is **four data sources are required** to reach 85–90% coverage of the £1m+ universe:

| # | Source | Method | Effort | Coverage gain | Cumulative |
|---|---|---|---|---|---|
| 1 | GOV.UK organisations | API fetch (built 2026-04-11) | done | 11% | 11% |
| 2 | Central buying agencies | Hand curation, ~25–30 entities | 2 hours | ~20% | 31% |
| 3 | NHS ODS | CSV download from NHS Digital | half day | ~20% | 51% |
| 4 | ONS Local Authority codes | CSV download from ONS | half day | ~30% | 81% |
| 5 | Better normalisation + Splink fuzzy | catches central gov mismatches and the long tail | 1 day | ~5–8% | ~88% |
| 6 | Defer: schools, blue light, housing, devolved sub-orgs | One-by-one as the dossier work demands them | — | the remaining 12% | ~88% (target) |

**Realistic target: 85–90% of £1m+ awards mapped to a canonical entity within ~3 days of work.** The remaining 10–15% is a long tail of one-off and obscure entities not worth chasing until specific dossier work demands them.

The hand-curated central buying agencies list is the next step (highest leverage per hour of work) and is in progress at the time of this addendum.

### Open questions surfaced by the addendum

1. **NHMF (NPC) LIMITED** — 605 ≥£1m awards but the abbreviation does not match any obvious public source. Needs identity confirmation before locking the glossary.
2. **HealthTrust Europe agent-of-trust naming** — should the canonical map collapse all "HTE acting on behalf of [Trust X]" variants to HTE, or preserve the agent-trust pairs as separate canonical entries? Likely collapse to HTE with the trust as a side-channel attribute.
3. **NHS Supply Chain operator chain** — SCCL is the legal entity, NHS Supply Chain is the brand, DHL/NoE CPC are operators acting as agents. The glossary needs a single canonical entry for NHS Supply Chain with the operator-of variants as aliases, and probably a note about the SCCL legal entity.
4. **LHC vs Scottish Procurement Alliance vs Welsh Procurement Alliance** — these are three distinct buying alliances all operating through the LHC Procurement Group brand. Should they be one canonical entity (LHC) or three (LHC, SPA, WPA)? Probably three, with LHC as the parent and SPA/WPA as children.

## Sign-off

Discovery complete on 2026-04-11. All eight decisions in the register confirmed (C06 with the upstream blocker). Proceeding to Phase 1 with the ingest patch as task #1, hand-curated central buying agencies as task #2, NHS ODS as task #3, ONS LA codes as task #4.
