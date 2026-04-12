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

## Change log

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-11 | Initial playbook from Phase 0 Discovery + Phase 1 GOV.UK and central buying agencies builds. 12 sections, ~3,000 words. |
| 1.1 | 2026-04-12 | Added §13: NHS ODS lessons learned — England-only gap, naming conventions, deferred hierarchy. |
