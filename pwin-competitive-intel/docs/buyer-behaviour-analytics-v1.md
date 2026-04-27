# Buyer Behaviour Analytics v1 — scoping

**Status:** scoping for review, not yet built.
**Branch:** `claude/procurement-intelligence-analytics-MOWqZ`
**Date:** 2026-04-27

## Why this exists

Win Strategy and Qualify both need a defensible empirical answer to: **"if this buyer says they intend to tender something, what's the realistic chance it actually goes to market and reaches an award?"** Today that number — call it the Probability of Going Out, PGO — is consultant judgement. This module turns it into a benchmarked figure grounded in the buyer's own track record over the last five years of UK Find a Tender data.

The lens is the **buyer**, always. Categories, suppliers, and timelines all sit *inside* a buyer view, never as the entry point.

## The buyer behaviour profile (the deliverable)

For any buyer the consultant looks up, the profile returns one page of behavioural intelligence:

### 1. Volume and trend
- Notices published per year, last 5 years
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

Reported as both percentages and absolute counts. The "dormant" threshold per category is set from the timeline distribution (next section), so it's data-driven, not a fixed cutoff.

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
- Average time-to-cancellation from publication (a buyer who cancels at month 6 behaves very differently from one who cancels at month 1)

### 6. PGO summary line
A single sentence the consultant can lift straight into a Win Strategy document:

> *"Over the last 5 years, [Buyer] has published [N] tenders. [X%] reached award, [Y%] were cancelled, [Z%] received no compliant bid, [W%] went dormant. Median time from publication to award was [D] days, with the slowest 10% taking over [P90] days. PGO benchmark for tenders of this category from this buyer: [X% award rate]."*

## What's in scope for v1 (build now)

- Outcome mix (all four buckets)
- Notice-to-award timeline distribution
- Category footprint with per-category outcome mix
- Cancellation behaviour
- PGO summary line
- Peer-buyer comparison for cancellation rate

All of this is buildable from data already in the database. No new ingest work.

## What's out of scope for v1 (Phase 2)

These need the planning-notice-to-tender linking step (heuristic match on buyer + title + category + date proximity) before they become reliable:

- Slippage patterns (planning indicative date vs. actual publication date)
- Planned-to-published conversion rate
- Full lifecycle PGO (planning → published → awarded), as opposed to v1's published → awarded

Phase 2 should follow once v1 is in real use and the consultant can tell us whether the lifecycle linkage is worth the engineering effort.

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

**No new ingest.** All four outcome signals (`tender_status`, `latest_tag`, `awards.status`, absence-of-award) are already populated. No schema changes needed.

## Open questions for the user before build

1. **Time window.** Default to last 5 years, or configurable per query?
2. **Minimum sample size.** A buyer with only 3 published tenders shouldn't show percentages — what's the floor? Suggest: hide outcome mix below 10 tenders, show counts only.
3. **Peer-buyer definition.** Same organisation type + same region is the obvious cut. Is that good enough, or do we need sector / spend-band peers too?
4. **Dormant threshold.** P95 of category timeline + 90 days is the proposal. Is "P95 + 90" the right buffer, or should it be more conservative (e.g. P99) to avoid mislabelling slow-but-live procurements as dead?
5. **MCP tool consumers.** Confirm Win Strategy and Qualify (paid tier) are the intended consumers — anything else (Verdict, Bid Execution) that should be in scope from day one?

## Build estimate

- Command-line query + tests: 2–3 days
- MCP tool wrapper: 0.5 day
- Dashboard panel: 1–2 days
- Documentation: 0.5 day

**Total: roughly one week of focused work** for v1, assuming the open questions above are answered up front.
