---
document_type: operational_playbook
subject: FTS canonical buyer layer — cleaning patterns, curation workflow, edge cases
purpose: educate future agents and the eventual cleaning skill on the operational nuances of working with FTS publisher data
parent_design: pwin-competitive-intel/CANONICAL-LAYER-DESIGN.md
discovery: pwin-competitive-intel/DISCOVERY-REPORT.md
status: living_document
created: 2026-04-11
---

# Canonical Buyer Layer — Operational Playbook

This is the operational playbook for cleaning, deduplicating, and canonicalising UK Find a Tender Service (FTS) buyer data. It is the rule-of-thumb companion to the [decision register](CANONICAL-LAYER-DESIGN.md) and [Discovery report](DISCOVERY-REPORT.md). Read those first for the *what* and *why*; this document covers the *how* and *gotchas*.

The purpose of this document is to **educate the future cleaning skill** (planned in Phase 2 of the canonical layer build, per decision C08) on the operational patterns we have learned the hard way. Every section answers: *what should the next operator do differently knowing this?*

## 1. Coverage math — read this before you celebrate any number

The single most important framing to internalise: **"% of distinct buyer names matched" and "% of awards mapped" are two completely different numbers, and they tell you completely different things.**

Example from the Phase 0 build:

| Metric | Value | What it means |
|---|---|---|
| Distinct buyer names in glossary | 1,114 | ~9% of distinct FTS buyer names |
| £1m+ awards mapped to a canonical entity | 33.0% | The number that actually matters |

The reason they diverge: **a single mega-buyer like the Ministry of Defence appears under 1,042 distinct buyer IDs in the raw FTS data**. Mapping that one canonical entity captures 1,042 fragmented rows in one shot. By contrast, a one-off academy trust appearing under one FTS buyer ID maps for one row of credit. So the *award-weighted* coverage figure is always much higher than the *name-distinct* coverage figure for any well-targeted curation effort.

**Rule:** never report coverage as a "% of buyer names" — always report it as a "% of awards in the relevant universe" (for the £1m+ universe, or whatever filter is active). The award-weighted figure is the one that maps to bid intelligence value.

**Corollary:** when prioritising curation work, sort the unmatched residual by **award count or award value**, not by alphabetical order or buyer name frequency. The next 10 high-volume unmatched buyers will give you more coverage gain than the next 100 random ones.

## 1b. Alias coverage is the second bottleneck — and it's invisible until a dossier surfaces it

> **Added 2026-04-27** after the MoJ live dossier surfaced this. Read it before quoting any buyer-aggregation number.

There are **three** numbers that matter, not two:

1. **% of canonical entities defined** — does the canonical layer know that "Ministry of Justice" is a real entity with the canonical ID `ministry-of-justice`?
2. **% of awards mapped** — covered above. The headline-grabbing number.
3. **% of raw buyer rows linked to their canonical entity via the alias glossary** — the number we forgot to track.

(1) and (3) sound similar but they are not the same number. The canonical layer can correctly identify MoJ as one entity (point 1 = 100%) while only linking 81% of the raw MoJ rows to it (point 3 = 81%). The 19% orphaned rows still appear as raw fragmented buyers to any consumer that joins through `canonical_buyer_aliases`.

The reason: `canonical_buyer_aliases` is only as comprehensive as the aliases registered for each entity. The Phase 0 build registered 1–2 aliases per canonical entity (the basic name and the abbreviation). Real raw data emits each entity under a much wider set of name spellings — see Section 3 for the full taxonomy. Any raw row whose name doesn't exact-match a registered alias is silently dropped from canonical aggregation.

Spot-check across UK ministerial departments (2026-04-27) showed orphan rates from 1% (DfE) to 88% (FCDO):

| Dept | Orphan rate (raw rows not linked to canonical) |
|---|---:|
| FCDO | 88% |
| Cabinet Office | 84% |
| HM Treasury | 60% |
| DHSC | 47% |
| MoJ | 19% |
| MoD | 7% |
| Home Office | 5% |
| DWP | 2% |
| DfE | 1% |

The pattern is not random. The departments most likely to publish under formal legal names ("The Secretary of State for X acting through Y") and the departments most active on Contracts Finder (where the publisher consistently appends a full stop to the buyer name — "Ministry of Justice." rather than "Ministry of Justice") are the ones most affected. So the orphaning is **systematically biased** away from precisely the data we added Contracts Finder ingestion to capture.

**Rule:** when reporting coverage to anyone (including yourself), always report all three numbers — entities defined, awards mapped, raw rows linked. The third one is the dossier-quality number. The first two are misleadingly reassuring on their own.

**Operational consequence:** every buyer dossier produced before the alias backfill (action [`pwin-canonical-buyer-alias-coverage-backfill`](../../../Obsidian%20Vault/wiki/actions/pwin-canonical-buyer-alias-coverage-backfill.md)) is computed from the alias-linked subset only. The procurement-behaviour numbers (cancellation rate, PGO benchmark, competition profile) are directionally correct but quantitatively biased. Until the backfill is done, every buyer dossier should carry a "buyer aggregation X% complete pending canonical alias backfill" data-confidence line, and pre-fix dossiers should not be quoted externally as definitive.

**Lesson for the future cleaning skill:** never measure coverage by entity definition alone. Measure it by raw-row linkage rate against the orphan list, broken down by buyer (so the worst offenders surface). The cleaning skill should run an "orphan rate report" as a routine output of every canonical refresh — without it, a high-quality canonical layer can be sitting next to a low-quality alias glossary and nobody notices.

## 2. The four-source model (and why no single source is enough)

Real coverage needs four data sources merged into one canonical layer:

| Source | Covers | Realistic coverage of £1m+ awards |
|---|---|---|
| GOV.UK organisations API | Central gov departments and ALBs | ~11% |
| Hand-curated central buying agencies | NHS SBS, NHS Supply Chain, YPO, ESPO, CCS, CCS-verbose-form, etc. | ~+22pp |
| NHS ODS (NHS Digital data download) | NHS trusts, ICBs, foundation trusts, special health authorities | ~+20pp |
| ONS Local Authority codes | The ~390 UK councils (district, county, unitary, metropolitan, London borough, devolved equivalents) | ~+30pp |

Combined ceiling: **~85–90%**. The remaining 10–15% is a long tail of housing associations, schools, academy trusts, universities, police forces, and devolved sub-bodies. **Do not chase the long tail until specific bid intelligence work demands it.**

**Rule:** when adding a new source, always validate its coverage gain against the **same universe** (£1m+ awards, or whatever the active filter is). Any source whose addition is below ~5pp coverage gain is probably not worth the engineering effort unless it's strategically important for a specific bid use case.

## 3. FTS publisher behaviour patterns

This section catalogues the patterns we have observed in how FTS publishers actually emit buyer names, so the cleaning layer can normalise them without surprise.

### 3.1 Verbose legal-name forms

The same canonical entity is frequently published under both its short brand name and its full legal-name form, sometimes with the brand name in parentheses at the end:

- **Crown Commercial Service** → "The Minister for the Cabinet Office acting through Crown Commercial Service" → "The Minister for the Cabinet Office acting through Crown Commercial Service (CCS)"
- **NHS National Services Scotland** → "The Common Services Agency (more commonly known as NHS National Services Scotland)" → "The Common Services Agency (more commonly known as NHS National Services Scotland) (NSS)" → "The Common Services Agency (more commonly known as NHS National Services Scotland) (\"NSS\")" → "The Common Services Agency (more commonly known as NHS National Services Scotland) (\"the Authority\")"
- **NEPO** → "THE ASSOCIATION OF NORTH EAST COUNCILS LIMITED T/A NORTH EAST PROCUREMENT ORGANISATION"
- **APUC** → "Advanced Procurement for Universities and Colleges"

**Pattern:** the verbose form is the legal-entity name; the short form is the brand. Both are real and both appear in the data.

**Rule:** for every canonical entity, include both forms as aliases. When a brand vs legal-entity distinction is known, prefer the brand as the `canonical_name` and the legal entity as an alias — this matches how bid teams actually refer to them.

### 3.2 Suffix variants — `Limited` vs `Ltd`, `& Co` vs `and Co`, trailing punctuation

Publishers vary inconsistently between:

- "Network Rail" / "Network Rail Infrastructure Limited" / "Network Rail Infrastructure Ltd"
- "National Highways" / "National Highways Limited" / "NATIONAL HIGHWAYS LIMITED"
- "Scape Group" / "Scape Group Limited" / "Scape Procure Limited" / "Scape Procure Scotland Ltd"
- "APUC" / "APUC Limited" / "APUC Ltd"

**Rule:** for any canonical entity that has a corresponding legal company entity, always include the `Limited`, `Ltd`, and uppercase variants as aliases. Better still, the runtime matcher should normalise `Ltd` → `Limited` and `&` → `and` before alias lookup so we don't have to enumerate every combination by hand.

### 3.3 "Operated by ... acting as agent of ... acting on behalf of ..." chains

NHS Supply Chain is the worst case. The legal entity is **Supply Chain Coordination Limited (SCCL)**, the brand is **NHS Supply Chain**, and the day-to-day operations are run by **multiple agents** under contract — DHL Supply Chain Ltd, North of England Commercial Procurement Collaborative (hosted by Leeds and York Partnership NHS Foundation Trust), Health Solutions Team Limited, etc.

The published buyer name takes forms like:
- "NHS Supply Chain"
- "NHS Supply Chain operated by Supply Chain Coordination Ltd (SCCL)"
- "NHS Supply Chain Operated by DHL Supply Chain Limited acting as agent of Supply Chain Coordination Ltd (SCCL)"
- "NHS Supply Chain operated by North of England Commercial Procurement Collaborative (who are hosted by Leeds and York Partnership NHS Foundation Trust) acting on behalf of Supply Chain Coordination Ltd" — **200 characters, at the apparent FTS field limit**

**Decision pattern (locked):** brand is canonical, legal entity is an alias, operators are aliases. All variants collapse to ONE canonical entity (`nhs-supply-chain`).

**Rule:** for any entity with an "operator chain" pattern, the canonical layer should use **prefix matching** — any name starting with `"NHS Supply Chain"` is canonical NHS Supply Chain, full stop. This is much better than enumerating every operator variant by hand because new operators get added over time. Apply the same rule to HealthTrust Europe (`"HealthTrust Europe LLP (HTE) acting on behalf of [trust X]"` → canonical HTE).

### 3.4 Agent-of-trust naming (HealthTrust Europe pattern)

HealthTrust Europe LLP runs procurement on behalf of dozens of individual NHS trusts. The published buyer name takes the form `"HealthTrust Europe LLP (HTE) acting on behalf of [Trust X]"`, with one variant per trust. HTE is the canonical entity; the on-behalf-of trust is **important provenance** but is **not a separate canonical entity for matching purposes**.

**Decision pattern (locked):** collapse to single HTE canonical entity. Preserve the agent-trust pair as a side-channel attribute on the award row, not as a separate canonical entity. The agent-trust attribute can drive a future "show me HTE awards by trust" query without fragmenting the canonical map.

**Rule:** when you encounter a "X acting on behalf of Y" pattern, the canonical entity should be X, and Y should be captured as a side-channel attribute, not as a competing canonical entity.

### 3.5 Whitespace, punctuation, and case drift

Publishers introduce drift in tiny ways that defeat exact-match comparisons:

- Missing space: `"The Common Services Agency(more commonly known as NHS National Services Scotland)"` (no space before the open paren)
- Double space: `"The Minister for the Cabinet Office acting through Crown Commercial  Service"` (double space before "Service")
- Case variants: `"NATIONAL HIGHWAYS"` / `"National Highways"` / `"national highways"` — all the same entity
- Trailing whitespace at the end of names
- Curly quotes vs straight quotes around abbreviations

**Rule:** the runtime matcher should always normalise before lookup: `lower()` + `strip()` + collapse multiple spaces to single + normalise quotes. The hand-curated alias list does not need to enumerate all case/whitespace variants — the matcher should be tolerant.

### 3.6 Truncation at FTS field limits

FTS publisher field limits appear to truncate buyer names around 200 characters. Long verbose names like the NHS Supply Chain operator chain occasionally arrive truncated in the source data.

**Rule:** when matching, use prefix matching for canonical entities whose names have known long-form variants. A truncated `"NHS Supply Chain operated by North of England Commercial Procurement Collaborative (who are hosted by Leeds and York Partnership NHS Foundatio"` should still match canonical NHS Supply Chain because the prefix is unique.

### 3.7 Hosting and "trading as" relationships

Publishers commonly use the form `"X t/a Y"`, `"X trading as Y"`, or `"X (c/o Y)"` to express that one entity is operating under another's umbrella:

- "Leicestershire County Council t/a Leicestershire Traded Services (c/o ESPO)"
- "Leicestershire County Council, trading as ESPO"
- "Association of North East Councils Limited trading as NEPO"
- "Velindre NHS Trust, NHS Wales Shared Services Partnership - Procurement Services"

**Decision pattern:** the trading-name is the canonical entity for procurement purposes, because that's what bid teams care about. The legal entity behind it is a parent or alias.

**Rule:** when you see "X trading as Y" or "X t/a Y", canonicalise to Y. When you see "Y (c/o X)" or "Y hosted by X", same — Y is canonical.

## 4. Hierarchy modelling decisions

Decision recap (locked in chat 2026-04-11): **hierarchical, not flat.** Every canonical entity has a `parent_ids` array and a `child_ids` array. Recursive CTE queries traverse the hierarchy at query time.

### 4.1 When to model as parent + child vs single collapsed entity

The default is **separate canonical entities with parent-child relationships**, not collapsed entities. Examples:

- **MoD → DE&S → DE&S Land Equipment**: three distinct entities. Bid director query *"what has DE&S bought"* should return DE&S only; *"what has MoD bought"* should traverse to all descendants.
- **LHC Procurement Group → Scottish Procurement Alliance + Welsh Procurement Alliance**: three distinct entities, with LHC as parent and SPA/WPA as devolved-nation children. SPA awards are LHC awards in the rolled-up sense, but a query *"what has SPA bought"* should narrow to SPA only.
- **DHSC → NHS England → individual NHS trusts**: three tiers. Each is its own canonical entity.

**Exception — collapse, don't model as hierarchy:**

- **HealthTrust Europe acting on behalf of [Trust X]**: collapse all the agent-of-trust variants to one HTE canonical entity. The trust is a side-channel attribute on the award row, not a child entity. (See 3.4.)
- **NHS Supply Chain operated by [agent Y]**: collapse all operator variants to one NHS Supply Chain canonical entity. Agents are aliases. (See 3.3.)

**Rule of thumb:** if the entity has a real, identifiable, durable existence as a procurement actor in its own right, model it as a separate canonical entity with a parent. If it's an agent or operator under contract to a principal, collapse to the principal.

### 4.2 Rebrand handling

Highways England → National Highways (rebranded 2021). The canonical map needs to handle both names because historical FTS records still use the old name.

**Approach:** add the old name as an alias on the new canonical entity. Do NOT model the old name as a separate "superseded" entity unless time-bound queries genuinely need to distinguish "this contract was awarded to Highways England in 2018" from "this contract was awarded to National Highways in 2024."

**Edge case:** if GOV.UK ever publishes a `superseding_organisations` link from old to new, the seed script should pick it up and the alias-merge for the old name will silently skip ("alias merge with no target") — which is fine. The old name's aliases live on the new entity.

### 4.3 The closed-org filter is too aggressive

The seed script filters out any GOV.UK entry where `details.closed_at` is set. We discovered during the build that **GOV.UK marks Crown Commercial Service as closed since 2026-03-31** even though it appears to be the most active central buyer in the entire FTS dataset. This is either a recent restructuring (CCS being absorbed) or a GOV.UK data error.

**Rule:** the closed-org filter is a heuristic, not a truth. **Always sanity-check the closed-org list against high-volume FTS buyers before each refresh.** If a closed entity is dominant in the historical FTS data, add it as a hand-curated active entity to preserve coverage. Document the GOV.UK status in the entity's `notes` field so future operators know to re-validate it.

**Anti-pattern:** never include closed entities indiscriminately by removing the filter — there are 161 genuinely defunct organisations in the GOV.UK index (Audit Commission, Strategic Health Authorities, the various pre-2010 quango bonfire victims, etc.) that would pollute the active glossary if added.

## 5. Curation workflow — how to add the next batch

When the next operator (human or skill) adds NHS ODS or ONS LA codes or any other source, follow this workflow.

### 5.1 Always start by quantifying the gap

Before writing any code, run a coverage query against the current glossary:

```python
# Pseudo-SQL
SELECT b.name, COUNT(*) cnt
FROM awards a JOIN notices n ON a.ocid=n.ocid JOIN buyers b ON n.buyer_id=b.id
WHERE a.status='active' AND a.value_amount_gross >= 1e6
GROUP BY LOWER(TRIM(b.name))
ORDER BY cnt DESC
LIMIT 30
```

Filter to those that DON'T match the current glossary. The top 30 unmatched gives you the priority list. Anything below ~50 awards is probably long tail and not worth this iteration.

### 5.2 Identify each top-30 entity

For each unmatched buyer, classify it: NHS / council / housing / education / blue light / central buying agency / other. Use string heuristics on the name (the categoriser used during Discovery is in the playbook below) but **always sanity-check by reading the award titles** for ambiguous cases. Example: NHMF (NPC) LIMITED was identified by reading the FTS notice title `"NHMF Frameworx Estate Services Framework Agreements 2023"`.

### 5.3 Find the actual FTS name variants for each entity

For each entity you're going to add, run:

```sql
SELECT b.name, COUNT(*) cnt
FROM buyers b LEFT JOIN notices n ON n.buyer_id=b.id LEFT JOIN awards a ON a.ocid=n.ocid
WHERE LOWER(b.name) LIKE '%<entity_keyword>%'
  AND a.status='active' AND a.value_amount_gross >= 1e6
GROUP BY b.name
ORDER BY cnt DESC LIMIT 10
```

This returns every distinct publisher variant. **Capture all of them as aliases in the curated entry.** The Discovery report addendum 1 has the variant catalogue for the 17 central buying agencies — it took ~30 min to compile and saved hours of trial and error.

### 5.4 Decide hierarchy placement

For each new entity, decide:
- Does it have a parent in the existing glossary? (E.g. PaLS NI → BSO NI → Department of Health NI; APUC → Scottish Government)
- Does it have children worth modelling? (E.g. LHC → SPA + WPA)
- Or is it standalone? (E.g. YPO has no parent)

Use the rules in §4.1.

### 5.5 Hand-curated entry shape

Every hand-curated entry should have:

```json
{
  "canonical_id": "slug-form-of-name",
  "canonical_name": "Brand or short form preferred",
  "abbreviation": "ABBR",
  "type": "Central buying agency",
  "subtype": "Specific category for filtering",
  "parent_ids": ["parent-canonical-id"],
  "child_ids": [],
  "aliases": [
    "All",
    "FTS",
    "Variants",
    "Including capitalisation",
    "And legal-entity suffixes"
  ],
  "status": "active",
  "source": "hand_curated",
  "notes": "Why this entry exists, where the variants came from, any open questions"
}
```

The `notes` field is critical — it carries the **why** for the next operator. Don't skip it.

### 5.6 Re-validate immediately after merging

After running the seed script, **always re-run the coverage query** and report the gain. If the gain is below your expectation, the aliases probably don't match the actual publisher strings — go back and grep the database for the entity's name to find what's missing.

### 5.7 Capture open questions, do not silently skip

If you encounter an entity whose identity you can't confirm, **add it to the `open_questions` array** at the top of the curated JSON file. Do not silently skip it. Future iterations can resolve it later. The NHMF case during Discovery is the model — it was an open question for one round, then resolved in the next round.

## 6. Outlier detection and unit/currency errors

**The FTS data contains obviously broken values that pollute aggregations.** Examples discovered during Discovery:

- Salisbury NHS Foundation Trust: £2,001,508m total across just 5 awards (£2 trillion)
- YPO: £1,848,195m total
- Police, Fire and Crime Commissioner for Northamptonshire: £352,000m
- NHS Shared Business Services: £346,252m

These are framework ceilings being recorded as individual award values, possibly with currency unit confusion (€/£/k/m).

**Rule:** the canonical layer should add an outlier-detection step at ingest time:

- Any award with `value_amount_gross > £500m` should be **flagged for review**, not silently included in aggregations
- Stored in a `suspect_values` table or marked with a `value_quality` field on the award row
- The runtime should exclude flagged values from any aggregation by default, with an opt-in to include them

**Without this step**, any "top buyer by total value" or "biggest contracts" query is going to be dominated by garbage. The outlier detection is small (~2 hours) and high-payoff for trustworthiness.

## 7. Quick categorisation heuristic

The categoriser used during Discovery, for filtering unmatched buyers into rough buckets:

```python
def categorise(name: str) -> str:
    nl = (name or '').lower()
    if any(k in nl for k in ('nhs', 'health', 'hospital', 'icb', 'integrated care')):
        return 'NHS'
    if any(k in nl for k in ('council', 'borough', 'county', 'district', 'metropolitan')):
        return 'LOCAL_GOV'
    if any(k in nl for k in ('university', 'college')):
        return 'EDUCATION'
    if any(k in nl for k in ('police', 'fire')):
        return 'BLUE_LIGHT'
    if any(k in nl for k in ('school', 'academy', 'trust')):
        return 'SCHOOLS'
    if 'housing' in nl:
        return 'HOUSING'
    return 'OTHER'
```

This is **good enough for prioritisation** but not for canonical assignment. Use it to decide which source to add next, not to assign canonical IDs. Note that 'trust' overlaps with NHS trusts and academy trusts — when in doubt, read the award titles.

## 8. What Splink will and will not solve

Splink is the right tool for the **residual fuzzy-matching problem**, not the bulk dedup. Specifically:

**Splink WILL solve:**
- Soft variants of central gov names that survived hand curation (typos, transposed words, missing initials)
- "NHS Property Services" vs "NHS Property Services Ltd" vs "NHS PS" type variations
- Postcode-confirmed matches where the name is slightly different but the address is identical
- The long tail of single-occurrence buyers that share an address with a known canonical entity

**Splink WILL NOT solve:**
- Mega-buyer fragmentation where the name is identical (1,042 "MINISTRY OF DEFENCE" rows) — `GROUP BY LOWER(TRIM(name))` solves this in milliseconds and Splink is overkill
- Out-of-scope entities (NHS trusts, councils) where the entity type is missing entirely from the glossary — Splink can't match against something that isn't there
- Operator chain patterns (NHS Supply Chain) — these need prefix matching, not fuzzy matching
- Closed-org gotchas (CCS) — these need human judgement and a hand-curated override

**Rule:** before reaching for Splink, ask "is this a fuzzy matching problem or a missing-data problem?" Fuzzy matching is the smaller of the two. Most of the work is adding missing canonical entities from the right source.

## 9. Open questions to carry forward

These are the unresolved questions from the Phase 0 + Phase 1 (so far) work that the cleaning skill should know about:

1. **Crown Commercial Service closed status** — GOV.UK marks CCS as closed since 2026-03-31. Real restructuring or data error? Sanity-check on the next refresh and resolve in the curated entry.
2. **GOV.UK refresh cadence** — how often to re-fetch the GOV.UK organisations API? Quarterly is probably fine for central gov, which doesn't restructure often. Annual minimum.
3. **NHS ODS data freshness** — NHS ODS publishes monthly. The canonical layer should track the snapshot date so we can detect drift.
4. **ONS LA codes refresh** — councils restructure occasionally (e.g. North Yorkshire unitary 2023). The canonical layer needs to handle the transition without losing historical contracts.
5. **Long-tail housing associations** — top 20 might be worth a future curation bloc; the rest can stay unmatched.
6. **University procurement** — APUC and SUPC are added as buying consortia, but individual universities also issue large procurements directly. UCAS / HESA / OfS data could close this gap if needed.
7. **Devolved NI sub-bodies** — PaLS, BSO, EA NI are added; the rest of the NI public sector is uncovered.
8. **Schools and academy trusts** — long tail, mostly small. Defer.
9. **Police forces** — 43 territorial forces + specialist forces. Small but coverable.
10. **Award date data is unreliable** — only 67 awards have a 2025 `award_date` set vs tens of thousands by `published_date`. Probably the parser populates `notices.published_date` correctly but not `awards.award_date`. Flagged in Discovery report; needs investigating during the framework-fields ingest patch.

## 10. Audit trail rules

Every canonical entity must carry provenance:

- `source` field — `"gov_uk_api"` / `"hand_curated"` / `"nhs_ods"` / `"ons_la_codes"` / etc.
- `notes` field — *why* this entry exists, where the variants came from, any caveats
- The seed script should never silently overwrite a hand-curated entry with a fresh GOV.UK fetch. If the canonical_id matches, alias-merge into the GOV.UK entry — don't replace the hand-curated entry.

**Rule:** if you ever need to debug "why is this buyer mapped to X", you should be able to trace it back to the source file and entry that created the mapping. No untraceable canonical assignments.

## 11. The continuous matching loop (planned, not yet built)

The canonical layer needs **two operating modes**:

1. **Batch mode** — runs once during initial build, processes the full historical buyer table, produces the initial canonical map. This is what we're doing now in Phase 1.
2. **Incremental mode** — runs nightly after the FTS ingest cron. For each NEW buyer ID that appeared in the latest batch, find the closest existing canonical entity. Auto-assign if confidence > threshold; queue for human (or skill) review otherwise.

The incremental loop is where the **Claude-skill-as-adjudicator** (decision C08) earns its keep. It reviews the queued ambiguous cases, decides, and writes back the canonical assignment. Without the loop, the canonical map drifts out of date as soon as the cron runs.

**Rule for the cleaning skill:** the skill's primary job is the adjudication queue, not bulk dedup. Bulk dedup is a deterministic Python pipeline. The skill's role is the 5–10% edge cases that the pipeline can't auto-decide.

## 12. Things future operators should NOT do

Anti-patterns we have already encountered or considered:

- **Don't lower the closed-org filter to be permissive** — see §4.3. The right answer is targeted hand-curation, not a blanket policy change.
- **Don't enumerate every operator variant by hand for entities like NHS Supply Chain** — use prefix matching at the runtime layer instead. Hand enumeration is brittle as new operators get added.
- **Don't trust value aggregations until outliers are detected** — see §6. Salisbury NHS at £2 trillion will dominate any "top buyers by spend" view until the £500m plausibility filter is in place.
- **Don't assume any single source covers more than ~30% of the £1m+ universe** — see §2. The four-source model exists because no single source is sufficient.
- **Don't classify Splink as the primary tool** — see §8. It's the residual tool. Most of the work is curation, not fuzzy matching.
- **Don't merge alias supplements blind** — always print what was merged, so human reviewers can spot bad merges (e.g. an alias supplement targeted the wrong canonical entity).
- **Don't silently drop unmatched entries** — always log them, count them, and surface the top-N to the next iteration's curation list.

## 13. NHS ODS — lessons learned (2026-04-12)

### NHS ODS is England-only

The ODS API at `directory.spineservices.nhs.uk` covers **English NHS organisations only**. Scottish NHS boards, Northern Ireland HSC trusts, and Welsh NHS bodies beyond those already in the hand-curated NWSSP entry are NOT included. This was not obvious before the build and caused the coverage estimate to be wrong (+5.8pp actual vs ~+20pp estimated).

**What ODS does cover (391 entities fetched):**
- 248 NHS Trusts (acute, community, mental health, ambulance)
- 121 ICBs and sub-ICB locations
- 14 Special Health Authorities
- 8 NHS Support Agencies

**What ODS does NOT cover (remaining ~3,104 unmatched NHS awards):**

| Gap | Entities needed | Source |
|---|---|---|
| Scottish NHS boards | ~15 (GGC, Highland, Lothian, Tayside, Fife, Forth Valley, Grampian, Lanarkshire, Ayrshire & Arran, Borders, D&G, Orkney, Shetland, Western Isles) | NHS Scotland ODS or hand-curate |
| NI HSC trusts | ~6 (Belfast, South Eastern, Northern, Southern, Western, NI Ambulance) | Hand-curate from NI HSC data |
| NHS procurement vehicles | ~5–10 (NOE CPC, NHS London Procurement Partnership, East of England NHS Collaborative Hub) | Hand-curate |
| Legacy CCGs | ~50+ (now Inactive since ICB transition July 2022) | Fetch with `--include-inactive` flag if historical matching matters |
| NHS England regional teams | ~7 ("NHS England (North)", "NHSE (London region)") | Hand-curate as children of NHS England |

**Rule for future operators:** when estimating coverage gain from a government data source, always check whether it covers all four UK nations or only England. Major sources that are England-only: NHS ODS, Ofsted, CQC. Sources that cover UK-wide: GOV.UK organisations API (mostly), Companies House, FTS itself.

### ODS naming conventions vs FTS naming conventions

ODS names are typically **UPPERCASE** (e.g. "STOCKPORT NHS FOUNDATION TRUST") which matches the FTS convention well. The alias builder generates title-case variants with `NHS` kept uppercase, which catches most FTS forms. However:

- FTS occasionally uses "NHS [Place] Integrated Care Board" while ODS uses "NHS [PLACE] INTEGRATED CARE BOARD" — the lowercase/title-case/uppercase alias triplet in the builder handles this.
- ICB names in FTS sometimes include the abbreviated form "ICB" while ODS uses "INTEGRATED CARE BOARD" — the alias builder adds both forms.
- Ambulance trusts in FTS may appear as "NHS North East Ambulance Service" while ODS has "NORTH EAST AMBULANCE SERVICE NHS FOUNDATION TRUST" — word order differs. **This is NOT caught by exact alias matching and needs Splink or a normalised-token matching approach.**

### Hierarchy not yet captured

The initial ODS fetch used the list endpoint (fast, no per-org detail calls). Parent-child relationships (trust → ICB → NHS England) are available via the ODS detail endpoint but were deferred to keep the first pass fast. When hierarchy matters for the query layer, a follow-up pass should call `GET /organisations/{OrgId}` for each entity and extract the `Rels` array.

## 14. Next steps for the residual 29.7% (2026-04-12)

As of five-source coverage at **70.3%** (1,928 canonical entities, 36,048 of 51,286 £1m+ awards matched), the remaining 29.7% splits into two distinct problems that require different tools.

### Bucket A — entities genuinely not in the glossary (~20-25pp)

These buyers are not in any of the five sources and no amount of fuzzy matching will find them. They need **new source data or targeted hand-curation rounds**. The composition:

- Housing associations (The Hyde Group is already added; the rest of the top 20 housing associations are not)
- Universities and FE colleges
- Police forces (43 territorial + specialist)
- Academy trusts and multi-academy trusts
- Utilities (Southern Water, Network Rail subsidiaries, etc.)
- One-off or obscure buyers

**Recommendation:** do NOT chase this tail proactively. Add entities one-by-one when specific dossier or query work demands them. The 70.3% coverage is sufficient for Skill 1 v2 Phase 3 validation, which only needs Serco/Capita/Mitie and their top buyers to be canonical. If a specific bid pursuit names a buyer that isn't in the glossary, add it then.

### Bucket B — name-variant drift from entities that ARE in the glossary (~5-8pp)

These buyers are in the glossary under a slightly different name. Examples:
- Word-order differences: "NHS North East Ambulance Service" vs ODS "NORTH EAST AMBULANCE SERVICE NHS FOUNDATION TRUST"
- Missed normalisation: ampersand vs "and", "Ltd" vs "Limited" variants not yet aliased
- Prefix-match cases: HealthTrust Europe agent-of-trust variants, NHS Supply Chain operator variants not yet enumerated

Two approaches were evaluated:

| Approach | Time | Expected gain | Complexity | Dependencies |
|---|---|---|---|---|
| **Improved token matching** — Jaccard similarity on word tokens + prefix rules for known patterns (NHS Supply Chain, HTE) | ~2 hours | ~3-5pp | Low — pure Python, no new deps | None |
| **Full Splink** — install, configure blocking rules, train model, run, review, tune | ~half day | ~4-6pp | Medium — adds splink + duckdb as deps | None (Splink is free, open source, MIT, runs locally) |

Splink gives ~1-2pp more than token matching for this dataset but costs 3× the setup time. **Splink becomes genuinely valuable later for the supplier entity resolution work** (161k entities, real fuzzy-match problem at scale) — that's where the probabilistic model training and blocking rules earn their keep. For 1,500 residual buyer names against a 1,928-entity glossary, simple token matching is proportionate.

**Decision (2026-04-12):** defer both approaches. The 70.3% coverage is sufficient for immediate downstream needs. When the next round of work demands higher buyer coverage, start with the 2-hour token matching pass. Reserve Splink setup for the supplier dedup workstream.

### Current coverage summary for reference

| Source | Entities | Step gain | Cumulative |
|---|---|---|---|
| GOV.UK organisations API | 1,090 | 11.2% | 11.2% |
| Hand-curated central buying agencies | +24 | +21.8pp | 33.0% |
| NHS ODS (England trusts, ICBs, SHAs) | +391 | +5.8pp | 38.8% |
| ONS Local Authorities (361 LADs + 21 counties) | +382 | +28.2pp | 67.0% |
| Devolved/combined (Scottish NHS, NI HSC, CAs, misc) | +42 | +3.3pp | 70.3% |
| **Token matching (deferred)** | 0 | est. +3-5pp | ~73-75% |
| **Splink fuzzy (deferred to supplier dedup)** | 0 | est. +1-2pp on top | ~75-77% |
| **New source data for long tail (on demand)** | varies | the remaining ~23% | ~varies |

## 15. Supplier entity resolution — Splink v1 build (2026-04-14)

The supplier dedup workstream ran as a single Splink pass with a deterministic post-pass. Producer: [agent/splink_supplier_dedup.py](agent/splink_supplier_dedup.py). Inputs read from `suppliers`; outputs written to `canonical_suppliers` + `supplier_to_canonical` in `db/bid_intel.db`.

**Headline result:** 161,119 raw supplier rows → **82,637 canonical entities** (48.7% compression, ~13 minutes end-to-end). Sits in the middle of the playbook's 60–80k prediction from §7/§8.

### Pipeline

1. Extract + normalise suppliers from SQLite into a DuckDB working DataFrame
   - `name_clean`: lower, trim, `&→and`, strip quotes, `Ltd→limited`, `Co→company`, trailing punctuation stripped, whitespace collapsed
   - `postcode_clean`: upper + strip spaces + UK regex filter (drops foreign/garbage postcodes)
   - `ch_clean`: upper + strip + UK CH regex (8 chars, 2 letters + 6 digits OR 8 digits)
   - `locality_clean`, `street_clean` (first 40 chars)
2. Splink 4 with DuckDB backend, four blocking rules: `ch_clean`, `postcode_clean + name_prefix_4`, `name_prefix_6 + locality_clean`, `name_clean` exact
3. Comparisons: JaroWinkler name, ExactMatch postcode/CH/locality, LevenshteinAtThresholds on street
4. u-values via random sampling (10M pairs), m-values via EM on the CH-block and postcode-prefix block
5. Cluster at match probability 0.95
6. **Deterministic post-pass**: merge any two canonical clusters sharing an identical `canonical_name`

### Why the post-pass matters

Splink alone produced 102,481 clusters. The post-pass merged 19,844 duplicate-name clusters down to the final 82,637. Most were variants of the same entity at different offices (e.g. Serco Limited across 5+ clusters because pairs with identical names but different postcodes scored 0.85–0.94, just below the 0.95 cluster threshold).

**Rule:** after Splink, always run an identical-name collapse as a separate deterministic step. Splink is tuned to be conservative on name-only matches because it legitimately can't tell if two records with the same name at different addresses are the same company — but for UK supplier data at this scale, same-normalised-name = same entity is a safe heuristic.

### Known residual issues

- **Subsidiary grouping is a judgement call.** Atkins Limited (125 members, 3 CH) includes `AtkinsRéalis` (the rebrand) and `Faithful+Gould` (subsidiary consulting arm). For bid-intelligence purposes they share a parent group, but queries about "Atkins Engineering" vs "the consulting arm" need finer splits. **Defer** until a specific use case demands it.
- **Same normalised name, different legal entities** — rare edge case. Two genuinely unrelated companies with identical normalised names would be collapsed by the post-pass. For UK public-sector suppliers this is unlikely to cause real harm but is worth auditing when it matters.
- **Post-pass SQL is slow** (~12 min on 102k clusters) due to correlated subqueries in the `UPDATE supplier_to_canonical ... WHERE canonical_id NOT IN (survivors)` step. Not a correctness issue but could be optimised with indexes for future re-runs.

### Splink dependency and environment

Splink + DuckDB + pandas are installed in `.venv/` at the project root. Pin file: [requirements-splink.txt](requirements-splink.txt). The rest of `pwin-competitive-intel` (ingest, enrichment, dashboard, query layer) remains pure Python stdlib — these deps are scoped to the canonical layer only. The nightly GitHub Actions cron is unchanged.

### Follow-ups

- Run against the £1m+ award universe specifically (supplier count there is ~3–5k, a more tractable target for manual validation)
- Join `canonical_suppliers` into Skill 1 v2 dossier queries — the original blocker per Phase 3 of Skill 1
- Splink-against-Companies-House register (C07 third job) — deferred until this v1 is validated against live dossier work

## 16. Value-outlier detection — `awards.value_quality` (2026-04-14)

Section 6 anticipated a £500m plausibility threshold for suspect values. Re-validating against the actual data distribution on 2026-04-14 showed that the £500m line would flag ~2,900 awards, most of which are **legitimate framework ceilings**, not data errors (e.g. MoD Global Bulk Fuels £1.35bn, CCS E-Vouchers £1.5bn, National Highways Charter 4 £1bn, YPO Apprenticeships £8bn). £500m is too aggressive.

### Threshold chosen: £10bn

Inspection of all 54 active awards above £10bn showed:
- 2 egregious data errors: Salisbury NHS at £1,000,000m (£1tn) for an apprenticeships framework (×2 duplicate rows), and North East Councils £100bn for "Travel Management Services"
- ~50 framework ceilings that are legitimate but extreme (YPO Apprenticeships £10bn, MoD MSS framework £3.2bn, Sellafield reseller £12bn etc.)

The £10bn line catches the data errors cleanly. Values below £10bn include real mega-frameworks that should not be blanket-flagged. Total flagged across all statuses: **78 rows**.

**Rule:** any single award with `value_amount_gross >= £10bn` is flagged `value_quality = 'suspect_outlier'`. Aggregations (total spend, top buyers, top suppliers, avg/max value) exclude flagged rows by default via `AND value_quality IS NULL`.

### What this does NOT fix

This flag only catches unambiguous data errors. It does **not** solve the broader framework-ceiling-vs-realised-spend conflation issue — values in the £100m–£10bn band are mostly framework ceilings, not realised award values, and will still over-state aggregated spend. Separating ceilings from realised values is a larger methodological problem that needs a dedicated design pass (e.g. use `notices.is_framework=1` + `framework_method` to distinguish framework establishment notices from call-off awards).

### Implementation

- Schema: added `awards.value_quality TEXT` column + `idx_awards_value_quality` index
- Ingest: [agent/ingest.py](agent/ingest.py) `upsert_awards` computes the flag on insert; UPSERT refreshes it on each update
- Backfill: one-shot SQL `UPDATE awards SET value_quality = 'suspect_outlier' WHERE value_amount_gross >= 10e9` applied 2026-04-14
- Queries: [queries/queries.py](queries/queries.py) aggregation sites updated (`summary`, buyer profile, supplier profile, supplier→buyer relationships, CPV search total_value)

### Re-evaluation triggers

- If FTS publisher behaviour changes (e.g. more errors start appearing below £10bn), lower the threshold
- If genuine >£10bn single awards start appearing (HS2 mega-lots, nuclear decommissioning), raise the threshold or move to a heuristic flag (e.g. flag only when value > N × buyer's 95th percentile)

## §16 — Buyer alias backfill (2026-04-28)

The canonical layer correctly identified the right entities (1,929 of them) but
the alias table was too thin: each canonical had ~2 spellings registered
(canonical name + abbreviation). Real raw data uses many more variants. Two
gaps surfaced live on 2026-04-27 when a buyer dossier was produced and
spot-checks showed orphan rates of 60–88% on FCDO, Cabinet Office, Treasury,
and DHSC.

### What the fix did

Two pieces of work, both implemented per design spec
[`docs/superpowers/specs/2026-04-27-buyer-alias-resolution-design.md`](../docs/superpowers/specs/2026-04-27-buyer-alias-resolution-design.md):

1. **`pwin-platform/src/competitive-intel.js` — `buyerProfile()` rewritten.**
   Now resolves through `_resolveBuyerCanonical()` first (the helper that was
   already being used by `buyerBehaviourProfile`). If the lookup resolves
   cleanly, all raw buyer rows are aggregated into one consolidated profile
   via `buyers.canonical_id` join. If ambiguous, candidates are returned. If
   no canonical match, falls back to raw LIKE with a `fragmented: true` flag
   so consumers can detect the degraded case. The supplier half of this
   pattern was already wired via `v_canonical_supplier_wins`; this brings
   the buyer half to parity.

2. **`agent/backfill-buyer-aliases.py` — new script.** Walks every raw buyer
   name, applies tidying rules (trailing punctuation, HM/His Majesty's
   preamble, dept-prefix-then-dash, brand-in-parentheses, "Secretary of State
   for X acting through Y", "more commonly known as Z", "on behalf of X"),
   and where a tidied name **exactly** matches a canonical name or
   abbreviation, registers a new alias and back-fills `buyers.canonical_id`
   if it was NULL. Exact-match-only — never fuzzy. Idempotent. `--dry-run`
   mode for safe review.

### Result

371 new aliases registered. 126 raw buyer rows that previously had
`canonical_id = NULL` are now linked to the right canonical entity. Orphan
rates by department, before vs after:

| Dept | Before | After | Spec target |
|---|---:|---:|---:|
| Foreign Office | 88% | 11% | <20% ✅ |
| Cabinet Office | 84% | 26% | <20% — close, sub-org work needed |
| Treasury | 60% | 30% | <20% — only 3 raw rows remain (sub-orgs) |
| Health | 47% | 12% | <20% ✅ |
| Justice | 19% | <1% | <10% ✅ |
| Defence | 7% | 7% | <5% — sub-unit names dominate residual |
| Home Office | 5% | 3% | <5% ✅ |
| Work and Pensions | 2% | 2% | <5% ✅ |
| Education | 1% | 5% | <5% — within target band |

### What's left

The residual orphans are all the same shape: **sub-organisations that are
either separate canonical entities (Government Property Agency, IPA,
National Infrastructure Commission) or naming variants that hang detail
off the parent ("Ministry of Defence, Strategic Command Commercial,
Defence Intelligence")**. The design spec explicitly deferred sub-org
handling to a separate design call. This is the next canonical-layer task
when a downstream product needs sub-org-level resolution.

## §17 — Sub-organisation pass (2026-04-28)

The deferred sub-org work landed on 2026-04-28. Three pieces:

1. **Nine missing major sub-orgs added to the glossary** via
   `agent/add_missing_sub_orgs.py`: Defence Digital, UK Strategic Command,
   British Army, Royal Navy, Royal Air Force, Defence Business Services,
   Royal Fleet Auxiliary (all under `ministry-of-defence`); Infrastructure
   and Projects Authority (under `cabinet-office`); National Infrastructure
   Commission (under `hm-treasury`). Each entry carries the common name
   variants the raw data uses ("Strategic Command, Defence Digital",
   "Ministry of Defence - Defence Digital", etc.) so the glossary alone
   resolves the bulk of orphan rows after `load-canonical-buyers.py`
   re-runs.

2. **Multi-part candidate splitting added to `backfill-buyer-aliases.py`.**
   Real raw names chain entities together using `,`, ` : `, and ` - ` —
   "Government Property Agency : Cabinet Office", "Strategic Command,
   Defence Digital, Ministry of Defence". The new rule splits on these
   separators, strips trailing parenthesised abbreviations from each piece,
   and offers each piece as its own candidate alias.

3. **Hierarchy-aware ambiguity resolution.** When the same raw name matches
   multiple canonicals (e.g. "Defence Equipment & Support, Ministry of
   Defence" matches both DE&S and MoD), the new resolver checks whether
   the matches are all on the same hierarchy line. If they are, it picks
   the most-specific descendant (DE&S in this example). Genuinely
   unrelated multi-matches still go to the ambiguous bucket.

### Result

- 9 new canonical entities; 1,938 canonical entities total.
- 667 new aliases registered, 1,427 raw buyer rows newly back-filled.
- Sub-org dossiers now consolidate end-to-end:

| Sub-org | Members | Awards | Total spend |
|---|---:|---:|---:|
| Defence Digital | 10 | 48 | £37m |
| UK Strategic Command | 11 | 10 | £19m |
| Government Property Agency | 10 | 167 | £1,116m |
| Crown Commercial Service | 36 | 818 | £580bn (frameworks) |
| Infrastructure and Projects Authority | 1 | 5 | £2m |
| National Infrastructure Commission | 2 | 7 | £0.5m |
| British Army | 2 | 4 | £4m |
| Royal Air Force | 2 | 1 | <£1m |

- Department-family orphan rates (parent + descendants):

| Dept | After §16 | After §17 |
|---|---:|---:|
| Foreign Office | 11% | 0% |
| Cabinet Office | 26% | 16% |
| Treasury | 30% | 0% |
| Health | 12% | 12% |
| Justice | <1% | 10% (note 1) |
| Defence | 7% | 2% |

Note 1: MoJ rose to 10% because the new multi-part rule re-routed some
"Department of Justice (NI)" rows that were previously linked to MoJ as a
mis-match (Department of Justice for Northern Ireland is a separate
canonical with its own parent). The "rise" is a correction.

### Lessons (additional)

- **Glossary is the source of truth, not the database tables.** The morning
  pass (§16) added 371 aliases directly into the database. The §17 pass
  re-ran `load-canonical-buyers.py` (which wipes and reloads from glossary)
  and lost those 371 morning-only aliases. New rules in the backfill
  recovered most of them, but the lesson is: durable changes belong in the
  glossary file (`~/.pwin/platform/buyer-canonical-glossary.json`), not
  just in the database.
- **Hierarchy is more useful than alias coverage past a point.** The §16
  pass tried to teach more aliases. The §17 pass teaches the matcher to
  reason about sub-org → parent relationships. The latter scales — every
  new sub-org you add automatically picks up multi-part raw rows that name
  it alongside the parent — without any new alias rules.
- **One commit per major data layer change.** The two passes (§16 + §17)
  produced different snapshots of `buyers.canonical_id` because of how
  `load-canonical-buyers.py` wipes and rebuilds. Future passes should
  always be: edit glossary → reload → run backfill → measure → commit, in
  that order, with no intermediate database-only edits.

### Lessons

- **Mirror the supplier pattern when adding new resolution paths.** The
  `_resolveBuyerCanonical` + `v_canonical_supplier_wins` pattern was already
  there — `buyerProfile()` just hadn't been wired through it. Half-finished
  work on a foundational layer compounds quickly when downstream skills
  rely on the data.
- **Exact-match-only after tidying is the right default.** The dry-run
  flagged 315 ambiguous matches that, if fuzzy-resolved, would have
  silently corrupted the alias table. Examples: SPA (Scottish Procurement
  Alliance vs Service Prosecuting Authority), DCMS (the pre-2023 vs the
  current Department for Culture, Media...). Conservative wins.
- **The improvement isn't where you'd expect it on a raw count.** Of 55,342
  raw buyer rows scanned, only 126 ended up newly back-filled. But those
  126 sit on the heaviest-traffic departments (FCDO, Cabinet Office, HMT,
  DHSC) which were under-aggregated by 50%+ before — so the dossier-quality
  impact is much larger than the raw-row count implies.

## §18 — Alias gap closures, UK7 capture fix, and the publish-at-parent finding (2026-04-28)

Three things landed this day, building on §17.

### Alias gap closures

Five small alias gaps closed for sub-organisations that publish on Find a Tender in their own name but had spelling variants we weren't catching (`patch_alias_gaps.py`):

- "The Legal Aid Agency" (8 raw rows) → `legal-aid-agency`
- "D S T L" spaced variants (2 rows) → `defence-science-and-technology-laboratory`
- "DIO : DIO" colon-doubled variant (1 row) → `defence-infrastructure-organisation`
- "DE&S Deca" + "DGM PT, DE&S" (6 rows) → `defence-equipment-and-support`
- Five "Department of Justice — Youth Justice Agency" variants (5 rows) → `youth-justice-agency-of-northern-ireland`

Total: 14 new aliases registered, persisted in the glossary file so they survive future reloads.

### Procurement Act 2023 UK7 notice capture

The ingest parser was reading the OCDS `noticeType` field from `tender.documents` and `awards[].documents` only. The Procurement Act 2023 introduced UK7 (contract details, mandatory within 30 days of contract signature) which attaches its document to `contracts[].documents`. The parser was silently dropping the UK7 marker — verified against a real OCDS release for notice 038645-2026 (Bank of England UPS maintenance, £41k).

Fix extends the document scan to include `contracts[].documents`, `contracts[].implementation.documents`, and `contracts[].amendments[].documents`. For compiled releases that carry UK4 + UK6 + UK7 together, candidate HTML documents are sorted by `datePublished` descending so the most recent notice type wins. The same fix recovers UK9 (performance), UK10 (change), and UK11 (contract end) notices — none of which were being captured before.

Effect from the next nightly ingest: every contract above threshold will carry a UK7 marker with confirmed contract period (start/end), supplier, value, and procurement method. Through-life signals (KPI performance, change events, contract terminations) flow correctly. No retroactive backfill applied — that's a separate workstream.

### The publish-at-parent finding

The structural finding that frames future work: **about 5% of contract awards (22,057 of 447,201) are dark at sub-organisation level because four ministerial departments publish under the parent name with no breakout for executive agencies.**

| Department | Family awards | Parent's share | Buried sub-organisations |
|---|---:|---:|---|
| Ministry of Justice | 4,413 | 95% | HMPPS, HMCTS, Office of the Public Guardian |
| Home Office | 2,258 | 91% | UKVI, Border Force, HM Passport Office, Immigration Enforcement |
| Department for Education | 4,528 | 88% | ESFA, Ofsted, Ofqual, Office for Students |
| Ministry of Defence | 9,854 | 79% | Defence Digital, Strategic Command, the service commands. DE&S, Dstl, DIO, SDA correctly attributed. |

The Procurement Act 2023 does not fix this — the buyer field is still freeform and inherits departmental publishing practice. Closing the gap requires an overlay layer (£25k spend transparency, NISTA major projects, NAO/PAC reports, framework call-offs, departmental annual reports), not a contract-feed change.

The remaining 93% of the contract universe names sub-organisations correctly. Local authorities, NHS bodies, devolved administrations, universities, police forces, and most ministerial departments (DHSC, DfT, Cabinet Office, DSIT, HMT, Defra, etc.) all publish at sub-organisation level.

### Lessons

- **The canonical layer is sound for 93% of the universe.** Today's alias gaps and the UK7 fix close most of what was fixable in the data layer. The 5% residual is a publisher-data limitation, not a canonical-layer flaw, and requires an overlay strategy rather than further canonicalisation work.
- **UK7 ≠ sub-organisation breakout.** The Procurement Act 2023 makes contract data richer per notice but does not change which departments publish at parent level. Future planning should treat the overlay layer as a permanent component, not a temporary scaffold.
- **The OCDS structural-where for notice documents is not consistent across notice types.** UK4/UK5/UK6 attach to tender.documents or awards[].documents; UK7 and UK11 attach to contracts[].documents; UK9 attaches to contracts[].implementation.documents; UK10 attaches to contracts[].amendments[].documents. Any future parser work should scan all five locations and prefer the latest by datePublished.

### See also

- `wiki/platform/sub-org-data-coverage.md` — executive summary with hard numbers and the overlay-strategy plan
- `docs/research/2026-04-28-sub-org-intel-sources.md` — full catalogue of overlay-layer source candidates
- `docs/research/2026-04-28-sub-org-contract-registers.md` — contract-register-specific deep dive plus Procurement Act 2023 transparency regime analysis
- `wiki/actions/pwin-sub-org-overlay-layer.md` — the new action note for the next workstream

## §19 — £25k spend transparency ingest: Wave 1 pipeline built (2026-04-29)

This section documents the first concrete step in closing the publish-at-parent gap identified in §18. The approach is an overlay layer that enriches the contract database with payment-level data from the UK government's monthly transparency publication.

### What was built

Eight implementation tasks delivered in one session. Everything is Python stdlib only — no new external dependencies.

**New data tables** (`spend_files_state`, `spend_transactions`) in the existing `bid_intel.db`:

- `spend_files_state`: one row per spend file in the catalogue. Tracks download status (`pending → downloaded → loaded → error`), file checksum, row count, and the local path on disk.
- `spend_transactions`: one row per payment line. Stores raw text (`raw_entity`, `raw_supplier_name`) plus canonicalised IDs (`canonical_sub_org_id`, `canonical_supplier_id`). Amount, date, expense type, and expense area captured for filtering.

**New scripts (all in `agent/`):**

| Script | What it does |
|---|---|
| `spend-catalogue.json` | Static list of 48 verified gov.uk download URLs for 2025 data (Home Office 12, MoJ HQ 6, HMCTS 6, LAA 2, DfE 10, MoD 12). Not a scraper — a curated config file updated once a year. |
| `fetch_spend.py` | Downloads pending files from the catalogue, 1s polite delay between requests, writes to `data/spend/<dept>/`, marks status in `spend_files_state`. |
| `parse_spend.py` | Four format handlers — one per department family. Yields normalised rows for each payment line. |
| `canonicalise_spend.py` | Matches `raw_entity` → `canonical_sub_org_id` via `canonical_buyer_aliases`; `raw_supplier_name` → `canonical_supplier_id` via `canonical_suppliers`. Normaliser is a copy of `load-canonical-buyers.py::norm` (same rules, same result). Unmatched rows stay NULL — never rejected. |
| `ingest_spend.py` | Orchestrator: calls fetch → parse → canonicalise in order. Idempotent. |
| `generate_spend_health.py` | Produces a Markdown health section (file counts, row counts, canonicalisation %, any download errors) for the nightly digest. |

**MCP surface change** (`pwin-platform/src/competitive-intel.js`): `_buildConsolidatedProfile` now calls `_buildSpendSignal(db, canonicalId)` and adds a `spendSignal` property to every buyer profile returned. Null when no data yet or when the table doesn't exist (graceful degradation).

**Nightly pipeline**: `scheduler.py` gains a non-fatal spend step after the daily pipeline scan. `save_digest` in `run-pipeline-scan.py` appends the health section to the nightly digest markdown.

### MoD publishes ODS, not CSV

Every other department publishes a plain comma-separated file. MoD publishes an OpenDocument Spreadsheet (`.ods`). The parser handles this using Python's built-in `zipfile` + `xml.etree.ElementTree` — the ODS format is a ZIP archive containing `content.xml`. No external packages added.

Rule: always inspect the first URL in any new department's catalogue entry before writing the parser. Assume nothing about file format.

### The entity_override pattern for MoJ

MoJ publishes three separate files per month — one for MoJ HQ, one for HMCTS, one for LAA (and historically HMPPS). Each file covers one sub-organisation but the file itself contains no entity column (it's all one entity's payments). The catalogue carries an `entity_override` field per entry (`"ministry-of-justice"`, `"hm-courts-and-tribunals-service"`, `"legal-aid-agency"`). `ingest_spend.py` reads this from the catalogue and writes it as `raw_entity` for all rows from that file, bypassing the file-level parser which returns `""`.

This pattern is general: any department that uses per-sub-org separate files (rather than a single multi-sub-org file with an entity column) uses `entity_override`. The schema is department-agnostic — adding a new family is a catalogue edit, not a code change.

### Permissive ingest, strict render

All rows are stored regardless of whether the entity or supplier matched a canonical ID. The `canonical_sub_org_id` and `canonical_supplier_id` columns are nullable. Unmatched rows are not visible in client output — `_buildSpendSignal` only surfaces totals and top suppliers, which are computed from all rows.

The rule: never reject a row because a name didn't match. The canonical IDs are enrichment, not a gate. Rejecting unmatched rows would silently shrink the spend picture and bias it toward suppliers already in the canonical layer.

### What to run next

```bash
cd pwin-competitive-intel
python agent/ingest_spend.py   # downloads 48 files, parses, canonicalises
```

Expect approximately 3–5 minutes for the downloads (1s delay between requests), then a few seconds for parsing and canonicalisation.

After the first run, check:

```bash
python agent/generate_spend_health.py
```

### What this does not yet cover

- **HMPPS 2025 data** — not yet found and confirmed. Try `https://www.gov.uk/government/publications/hm-prison-and-probation-service-spending-over-25000-2025` and add to the catalogue if it exists.
- **Prior years (2020–2024)** — the catalogue seeds 2025 only. Add earlier entries to `spend-catalogue.json` following the same pattern; the pipeline will pick them up on the next run.
- **NISTA major projects portfolio** — Wave 1 Item 2. The only open-data source that explicitly tags Defence Digital programmes as Defence Digital. Planned but not yet built.
- **Organograms** — Wave 1 Item 3. For stakeholder mapping. Planned but not yet built.

### Coverage numbers as of 2026-04-29

Canonical buyer layer: 2,247 entities, 75.73% of all notices mapped (385,909 of 509,553). The spend ingest adds a second intelligence dimension — payment-level supplier data — that the contract-notice layer alone cannot provide for the four publish-at-parent departments.

---

## Change log

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-11 | Initial playbook from Phase 0 Discovery + Phase 1 GOV.UK and central buying agencies builds. 12 sections, ~3,000 words. |
| 1.1 | 2026-04-12 | Added §13: NHS ODS lessons learned — England-only gap, naming conventions, deferred hierarchy. |
| 1.2 | 2026-04-12 | Added §14: Next steps for the residual 29.7%. Token matching vs Splink analysis. Five-source coverage at 70.3%. |
| 1.3 | 2026-04-14 | Added §15: Supplier entity resolution Splink v1 build. 161k → 82,637 canonical (48.7% compression). |
| 1.4 | 2026-04-28 | Added §16: Buyer alias backfill — `buyerProfile()` rewritten, 371 aliases registered, 126 raw rows back-filled. FCDO/DHSC/Justice now under target orphan rate; Cabinet Office and Treasury residual is sub-org work (deferred). |
| 1.4 | 2026-04-14 | Added §16: Value-outlier detection. `awards.value_quality` flag at £10bn threshold. 78 awards flagged. |
| 1.5 | 2026-04-28 | Added §17: Sub-organisation pass. 9 new canonicals (Defence Digital, UK Strategic Command, IPA, NIC, etc.), multi-part candidate splitting, hierarchy-aware ambiguity resolution. 667 new aliases, 1,427 rows back-filled. Sub-org dossiers operational. |
| 1.6 | 2026-04-28 | Added §18: Five additional alias gaps closed (LAA, Dstl spaced, DIO doubled, DE&S Deca, NI Youth Justice). Procurement Act 2023 UK7 / UK9 / UK10 / UK11 notice capture fixed in `agent/ingest.py` — parser was reading `noticeType` from the wrong OCDS location. Publish-at-parent finding documented: 5% of contract awards (22k of 447k) dark at sub-organisation level across MoJ, Home Office, DfE, MoD; UK7 doesn't fix this; overlay strategy required. |
| 1.7 | 2026-04-29 | Added §19: £25k spend transparency ingest Wave 1 pipeline (8 tasks). 48 verified URLs in catalogue. ODS reader for MoD. entity_override pattern for MoJ streams. spendSignal added to buyer profile. Nightly digest integration. 23 tests. |
