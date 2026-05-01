# Buyer Behaviour Analytics v1 — scoping

**Status:** scoping for review, not yet built.
**Branch:** `claude/procurement-intelligence-analytics-MOWqZ`
**Date:** 2026-04-27 (rev 2 — adds Contracts Finder, Companies House, and four further behaviour signals to v1 scope)

## Why this exists

Win Strategy and Qualify both need a defensible empirical answer to: **"if this buyer says they intend to tender something, what's the realistic chance it actually goes to market and reaches an award?"** Today that number — call it the Probability of Going Out, PGO — is consultant judgement. This module turns it into a benchmarked figure grounded in the buyer's own track record over the last five years of UK public sector procurement data.

The lens is the **buyer**, always. Categories, suppliers, and timelines all sit *inside* a buyer view, never as the entry point.

## Data foundation

The database already merges three sources, all available to v1 from day one:

- **Find a Tender Service (FTS)** — UK above-threshold contract notices and awards (~175k records, 5+ years history). Tagged `data_source = 'fts'`.
- **Contracts Finder (CF)** — UK below-threshold contracts (the high-volume layer where most local authority and NHS trust activity lives). Loaded by `agent/ingest_cf.py`, tagged `data_source = 'cf'`. The README still says "not yet integrated" — that's stale; CF is integrated, ingestion is operational.
- **Companies House (CH)** — supplier-side enrichment with company status, directors, parent companies and SIC codes. Loaded by `agent/enrich-ch.py` for the ~27% of suppliers carrying a CH number.

This matters for v1 because:
- CF roughly doubles the buyer-behaviour sample for local authorities and NHS trusts, where most procurement sits below the FTS threshold. Without CF, "by buyer" rollups would understate volume and miss most of the cancellation pattern.
- CH lets us add an **incumbent-distress** flag — when the current contract-holder is in liquidation or dissolution, the buyer is forced into re-procurement irrespective of their stated plans. That's a forward PGO signal you can't get from FTS or CF alone.

## The buyer behaviour profile (the deliverable)

For any buyer the consultant looks up, the profile returns one page of behavioural intelligence. Every metric below covers FTS + CF combined, with an optional split where the difference matters.

### 1. Volume and trend
- Notices published per year, last 5 years (FTS + CF, with split shown)
- Awards per year, last 5 years
- Year-on-year direction (growing / steady / shrinking)

### 2. Outcome mix — the headline PGO input
For every published tender from this buyer, what eventually happened to it. Four mutually exclusive buckets:

| Outcome | How we identify it |
|---|---|
| **Awarded** | Has at least one award record with status `active` or `pending` |
| **Cancelled / withdrawn** | `tender_status` or `latest_tag` indicates explicit cancellation |
| **No compliant bid** | Has an award record but `awards.status = 'unsuccessful'` |
| **Dormant (effectively dead)** | Published more than `P95(category timeline) + 90 days` ago, no award, no cancellation marker |

Reported as both percentages and absolute counts. The dormant threshold per category is set from the timeline distribution (next section), so it's data-driven, not a fixed cutoff.

### 3. Notice-to-award timeline
- Median, 25th–75th range, 90th percentile (days from notice publication to first award)
- Reported overall and split by the buyer's top 5 categories
- Caveat documented on multi-lot tenders (we use first award date per tender)

### 4. Category footprint
- Top 10 procurement category codes by volume
- For each: notice count, outcome mix, median timeline
- Highlights categories where this buyer cancels disproportionately often

### 5. Cancellation behaviour
- Overall cancellation rate vs. peer-buyer median (peers = same organisation type, same region)
- Top 3 categories where they cancel most
- **Time-to-cancellation distribution** — when this buyer kills a tender, do they kill it at week 2 (publication error / rapid rethink) or month 6 (ran the process and lost commitment)? Late cancellers are far more costly for bidders than early ones, and the pattern is buyer-specific.

### 6. Procurement method mix
The split between open competition, restricted procedure, competitive dialogue, framework call-off, and direct award. Each has a different historical "kill rate". A buyer running 70% of activity through framework call-offs (where the framework is already awarded) has a structurally different PGO profile from one running everything as fresh open competition. Surfaced on the buyer card alongside outcome mix because the two interact.

### 7. Competition intensity
- Average bid count per tender, overall and by top categories
- Trend over the last 5 years (rising / flat / falling)
- Buyers whose tenders historically attract fewer than 3 bidders in a given category have a structurally elevated chance of the next tender ending in "no compliant bid"
- *(Stretch — see Phase 2)* Bid counts deduplicated by Companies House parent company, so two suppliers under the same corporate parent count as one bidder

### 8. Amendment behaviour
When a buyer publishes a tender, then changes the deadline, then changes the specification, then changes it again, that's an indecision signal. The amendment trail is captured in the tag history on each tender. Reported as:
- Amendment rate (% of this buyer's tenders that received at least one amendment)
- Average amendments per tender
- Correlation with downstream cancellation — a high-amendment buyer typically has measurably higher cancellation rates and longer publication-to-award timelines

### 9. Incumbent-distress flag
For each of this buyer's currently-active contracts, joins `awards.contract_end_date` against the incumbent supplier's Companies House status. Surfaces a list of contracts where the incumbent is in:
- Dissolution / dissolved
- Liquidation (administration, receivership, voluntary)
- Compulsory strike-off proceedings
- Cessation of trading

This is a near-term forced-procurement signal — when the incumbent fails, the buyer has to re-procure regardless of plans, which raises PGO on any planned procurement in that category. Coverage caveat: the flag fires only for suppliers with a Companies House number on file (~27% of all suppliers, but skewed toward the larger contract-holders that matter most).

### 10. PGO summary line
A single sentence the consultant can lift straight into a Win Strategy document:

> *"Over the last 5 years, [Buyer] has published [N] tenders. [X%] reached award, [Y%] were cancelled, [Z%] received no compliant bid, [W%] went dormant. Median time from publication to award was [D] days, with the slowest 10% taking over [P90] days. Tenders in this category typically attract [B] bidders. [N] currently-active contracts have an incumbent in financial distress. PGO benchmark for tenders of this category from this buyer: [X% award rate]."*

## What's in scope for v1 (build now)

- Volume and trend (FTS + CF combined, with split)
- Outcome mix (all four buckets)
- Notice-to-award timeline distribution
- Category footprint with per-category outcome mix
- Cancellation behaviour, including time-to-cancellation distribution
- Procurement method mix
- Competition intensity (raw bid counts, no parent-company dedup yet)
- Amendment behaviour
- Incumbent-distress flag (uses existing Companies House enrichment)
- PGO summary line
- Peer-buyer comparison for cancellation rate

All of this is buildable from data already in the database. No new ingest work.

## What's out of scope for v1 (Phase 2)

Three things needing additional engineering before they become reliable:

1. **Slippage and planned-to-published conversion.** Need the planning-notice-to-tender linking step (heuristic match on buyer + title + category + date proximity) — covers full lifecycle PGO (planning → published → awarded) instead of v1's published → awarded.
2. **Competition intensity adjusted for parent-company linkage.** Needs a join from canonical supplier IDs to Companies House parent-company records, then deduplication of bidder counts by parent. Sharpens the "no compliant bid" risk estimate by correcting for cases where multiple trading names sit under one corporate group.
3. **Buyer financial-distress overlay.** Council s.114 notices and NHS trust deficit positions — both available externally — are the strongest predictor of cancellation risk and are not yet in the database. Smallest dataset to ingest, highest external uplift.

Phase 2 should follow once v1 is in real use and the consultant can tell us whether each of these is genuinely needed or whether v1 is enough.

## Where it lives

Three surfaces, same query layer underneath:

1. **Command-line query** — `python queries/queries.py buyer-behaviour "Ministry of Defence"` extends the existing `buyer` command pattern in `queries/queries.py:126`. Fastest to build, used by consultants directly.
2. **MCP tool** — `get_buyer_behaviour_profile(buyer_name)` added to `pwin-platform/src/competitive-intel.js`. This is what makes the data available to Win Strategy and Qualify when the consultant runs an AI assurance pass.
3. **Dashboard tab** — extends the existing buyer profile view in `dashboard.html` with a new "Behaviour" panel. Last priority, nice to have.

Build order: command-line first (validates the queries), then MCP tool (unlocks downstream products), then dashboard (visualisation).

## Dependencies

**Canonical buyer layer.** The whole module is only as trustworthy as the buyer-aggregation underneath it. Today the canonical layer covers 70% of award value across 1,928 buyer entities. For names inside that coverage (most central government, large NHS trusts, major local authorities) the rollups will be clean. For long-tail buyers we either:
- Fall back to raw buyer ID + name-prefix matching, with a "fragmented buyer" warning on the output, or
- Skip them in v1 and document the limitation.

The recommendation: ship v1 against the canonical layer where it exists, raw + warning where it doesn't. Don't block v1 on canonical-layer completeness.

**Cross-source canonicalisation.** FTS and CF use different buyer ID schemes (`cf-buyer-*` for CF). The canonical layer needs to map both into the same canonical buyer entity, otherwise volume and outcome mix will appear split across two records for the same real buyer. Confirm whether this mapping is already complete in `canonical_buyers` / the buyer glossary; if not, it's a pre-requisite for v1.

**No new ingest.** All v1 signals (`tender_status`, `latest_tag`, `awards.status`, bid count fields, amendment tags, supplier `ch_status`) are already populated. No schema changes needed.

## Competitive landscape note

Tussell covers the descriptive layer (who buys what, who wins what, pipeline, framework holdings) on similar underlying data — they aggregate FTS, Contracts Finder, and the devolved feeds with strong entity resolution. The differentiation here is the **predictive PGO layer** sitting on top: outcome mix, behavioural pattern, incumbent distress, and the conditional PGO interpretation that feeds Win Strategy and Qualify. Don't rebuild what Tussell does well — build the predictive layer, and treat Tussell as a possible commercial data source for things we lack (e.g. devolved coverage) if their licensing supports downstream use.

## Open questions for the user before build

1. **Time window.** Default to last 5 years, or configurable per query?
2. **Minimum sample size.** A buyer with only 3 published tenders shouldn't show percentages — what's the floor? Suggest: hide outcome mix below 10 tenders, show counts only.
3. **Peer-buyer definition.** Same organisation type + same region is the obvious cut. Is that good enough, or do we need sector / spend-band peers too?
4. **Dormant threshold.** P95 of category timeline + 90 days is the proposal. Is "P95 + 90" the right buffer, or should it be more conservative (e.g. P99) to avoid mislabelling slow-but-live procurements as dead?
5. **FTS / CF split reporting.** Default to merged, with a one-line "of which CF: X%" caption on each metric? Or always show side-by-side? CF and FTS may behave differently on cancellation, and we won't know until we look.
6. **Cross-source canonicalisation status.** Are FTS and CF buyer IDs already mapped to the same canonical entities? If not, fixing this is a v1 prerequisite, not a v2 nicety.
7. **MCP tool consumers.** Confirm Win Strategy and Qualify (paid tier) are the intended consumers — anything else (Verdict, Bid Execution) that should be in scope from day one?

## Build estimate

- Command-line query + tests (10 metrics): 3–4 days
- MCP tool wrapper: 0.5 day
- Dashboard panel: 1–2 days
- Documentation: 0.5 day

**Total: roughly one to one-and-a-half weeks of focused work** for v1, assuming the open questions above are answered up front and the FTS/CF canonicalisation is already complete.
