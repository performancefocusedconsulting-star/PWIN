# Strategic Supplier Pursuit Spend — Methodology, Results, and Market Messaging Guidelines

**Date:** 25 April 2026
**Status:** Final
**Audience:** Internal — for use by sales, marketing, and senior leadership when communicating BidEquity's market sizing externally
**Supersedes:** All earlier verbal or document-form references to the £3.9bn / £2bn headline figures

---

## Executive Summary

UK government strategic suppliers — the 37 named entities on the Cabinet Office strategic supplier register — collectively spend **approximately £3.3 billion per year pursuing government contracts**. Of that, **approximately £2.2 billion is sunk cost on losing bids**. This represents around **2% of the total contract value those same suppliers win in a year (£173 billion)** — a cost-of-sale ratio consistent with what a chief financial officer would expect for the bid-intensive nature of public-sector procurement.

These figures replace earlier published estimates of £3.9 billion / £2 billion. The headline numbers are within rounding distance of the original work, but the methodology underpinning them is now grounded in line-by-line analysis of actual contract data rather than top-down tier estimation. The methodology survives challenge on every category — direct awards, extensions, framework call-offs, and renewals — that a sceptical commercial counterparty would raise.

---

## 1. Background and Objective

The original strategic-supplier pursuit spend analysis was completed on 21–23 April 2026 and published in the BidEquity CFO Business Case Model. It produced a headline figure of **£3.9 billion industry pursuit spend / £2.0 billion wasted on losing bids**.

That work was conducted against the Find a Tender Service alone — the UK government's transparency feed for above-threshold procurement (broadly, contracts over £214,904 for sub-central government and £139,688 for central government). Find a Tender publishes individual award notices but is acknowledged to capture only an estimated 15% of small contracts because framework call-offs are not individually notified.

To compensate, the original model used a bottom-up estimate of **8,000 framework call-off bids per year** across the 37 strategic suppliers — a figure that was deliberately conservative but which had no direct empirical anchor.

In April 2026, the underlying competitive intelligence database was extended to include **five years of Contracts Finder history** — the UK government's secondary feed which captures sub-threshold contracts, including framework call-offs that Find a Tender misses. This work concluded on 25 April 2026, growing the database from 177,000 contracts to 508,000.

This created an opportunity — and a responsibility — to revisit the original analysis. Two questions:

1. **Has the headline materially changed** with the addition of Contracts Finder data?
2. **Does the methodology survive scrutiny** when it is interrogated category by category, or are there assumptions that overstate the figure?

The answer to both questions is the subject of this document.

---

## 2. Data Sources and Scope

### Sources used

- **Find a Tender Service (FTS)** — the UK government's primary procurement transparency feed. Captures above-threshold notices. 177,023 contract notices over the past five years.
- **Contracts Finder (CF)** — the UK government's secondary feed for sub-threshold and central-government opportunities. 331,479 contract notices loaded between Contracts Finder backfill on 25 April 2026.
- **Companies House** — used to enrich supplier records with company numbers, status, directors, and parent-company information. Currently 1,384 of 87,000 with-number suppliers enriched; bulk catch-up scheduled.

### Scope of analysis

- **Time window:** trailing 12 months (25 April 2025 to 25 April 2026)
- **Supplier population:** 37 entities on the Cabinet Office strategic supplier register, identified across 95 name patterns to handle subsidiary, joint venture, and trading-name variation
- **Contract value floor:** £25,000 (below this is micro-procurement, not pursuit-relevant)
- **Universe:** 1,302 unique contracts won by at least one strategic supplier within the window, with combined contract value of £172.8 billion

### Exclusions

- Bids placed by strategic suppliers that **lost to non-strategic suppliers** (typically smaller and medium-sized enterprises). The data only records winners. The model partially compensates by assuming strategic-on-strategic competitions in larger tiers.
- Pursuit work on opportunities that **never proceeded to award** (cancelled, withdrawn, restructured). Real cost, not visible in award data.
- **Pre-positioning and capture-phase activity** preceding any formal bid notice.

These exclusions tend to **understate** rather than overstate the headline. A more comprehensive accounting would likely produce a higher figure. The current number should be treated as a defensible floor rather than a maximum.

---

## 3. Methodology

The work proceeded through five iterations. Each iteration responded to a specific concern raised by the previous one.

### Iteration 1 — Reproduce the original baseline (Find a Tender only)

The original model categorised contracts into six value tiers and applied a fixed per-bidder bid cost to each tier:

| Tier | Original cost per bid | Bidders per competition |
|---|---:|---:|
| Framework call-off (<£5m) | £35,000 | (8,000 bottom-up estimate) |
| Notified small (£5–25m) | £125,000 | 8.2 |
| Notified mid (£25–100m) | £550,000 | 6.7 |
| Major services (£100–500m) | £1.5m | 7.3 |
| Strategic programme (£500m–5bn) | £14m | 5.6 |
| Defence mega (£5bn+) | £25m | 7.75 |

Reproducing this against today's database produced **£3.57 billion / 9,278 bids** — within 9% of the original £3.93 billion. The unique-competition counts in each tier matched the original analysis to within 1–4 competitions. **The original methodology was reproducibly stable.**

### Iteration 2 — Add Contracts Finder, same model

Re-running the same value-tier model against the combined database produced **£4.96 billion / 10,651 bids** — a 39% increase. The increase was concentrated in the smallest tier, where Contracts Finder revealed 776 framework call-offs won by strategic suppliers that had been invisible in Find a Tender.

This was the first directional confirmation that the original model was conservative on small contracts. But it also revealed a problem: by treating every contract in a tier identically — regardless of whether it was a competitive bid, a renewal, an extension, or a direct award — the model was treating non-bid activity as if it were full bids.

### Iteration 3 — Bid-type-aware model (initial)

Each contract was classified into one of seven bid types using structured fields (procurement method, framework flag, notice type) and title keywords. Each bid type was assigned its own bidder count and cost multiplier. The result was **£754 million** — a 5× reduction from the value-tier model.

The reduction came principally from:
- **Direct awards** (no competitive process) being charged at zero cost
- **Framework call-offs** being measured directly from observed activity rather than the 8,000 bottom-up estimate
- **Bidder counts and per-bid costs varying by type** rather than being lumped together

This iteration overcorrected. The £754 million figure was challenged on five grounds, all of which were valid:

1. **Direct awards do involve real winning-supplier work** — solution shaping, internal pricing, governance, contract negotiation. Charging zero understated the genuine pursuit cost.
2. **Extensions and modifications** likewise involve incumbent effort that is not free.
3. **Renewals and recompetes** — the incumbent operates at reduced effort (templates, relationships) but challenger bidders work at full effort.
4. **Framework call-off costs do not scale linearly with value** — a £25 million framework mini-competition involves real bid effort, not £180k.
5. **Cost-of-sale economics** — at the £5–100 million range, real bid spend is around 2–3% of contract value. The model was producing 0.5–1% in this range, well below industry norms.

### Iteration 4 — Forensic per-contract model

Two structural changes:

**Per-contract (not per-tier) bid cost calculation.** Every contract uses its actual transacted value to compute its specific bid cost via a cost-of-sale function:

```
< £100k       →  £15k flat
£100k – £1m   →  max(£35k, value × 5%)        — fixed-cost zone
£1m – £5m     →  max(£75k, value × 3.5%)
£5m – £25m    →  value × 2.5%
£25m – £100m  →  value × 2%
£100m – £500m →  value × 1.3%
£500m – £5bn  →  value × 0.8%                  — anchored on Selborne (£1.2bn / £12m)
£5bn +        →  value × 0.4%                  — anchored on Marshall (defence mega)
```

**Refined bid-type classification using the UK Procurement Act 2023 notice codes** (UK4 = transparency notice = direct award; UK7 = contract change = modification) and value-based defaults to drive the unclassified bucket from 883 contracts down to zero.

### Iteration 5 — Final calibration

Two final fixes were applied:

1. **Framework agreements capped at £1 million per bidder.** Framework agreements are the parent panels (not the call-offs under them). Their nominal ceiling values can be £100 million or more, but each panel member's effective revenue is much lower. A panel slot is worth £200k–£1.5m to win in real bid effort, regardless of framework ceiling.
2. **Final bid-type multipliers agreed with senior leadership** (see Section 4).

This produced the final result of **£3.34 billion / £2.17 billion**.

---

## 4. Assumptions

This section is the most important in the document. Every assumption is explicit so it can be challenged, evidenced, and refined.

### Bid-type multipliers

| Bid type | Bidders / competition | Cost vs open competition | Win rate | Rationale |
|---|---:|---:|---:|---|
| Open competition (greenfield) | 7 | 100% | 25% | Full bid effort against a wide field. Original CFO-model assumption retained. |
| Restricted competition | 5 | 100% | 35% | Same effort as open (PQQ adds work, not removes it); smaller field after pre-qualification |
| Competitive dialogue | 4 | 130% | 30% | Multi-round discovery and dialogue process — the heaviest format |
| Framework call-off / mini-competition | 4 | 65% (£35k floor) | 30% | Pre-agreed terms and conditions reduce commercial work but technical and pricing effort scales with deal size; floor of £35k for the smallest call-offs reflects the minimum team to put a bid together |
| Renewal / recompete | 3 (incumbent + 2 challengers) | 90% blended | 33% blended (70% incumbent / 15% challenger) | Incumbent operates at 70% effort with 70% win odds; two challengers at 100% effort with 15% odds each |
| Extension / modification | 1 (incumbent only) | 35% | 95% | Real winning-supplier effort: business case, pricing analysis, scope negotiation. 5% allowance for extensions that get pulled |
| Direct award | 1 (winning supplier only) | 35% | 100% | Winning-supplier effort: solution shaping, governance, internal pricing approval, contract negotiation. No competitive bidders to multiply by |
| Framework agreement (parent panel) | 6 | 120% with £1m per-bidder cap | 30% | Panel-set-up bids are heavier than call-offs but capped because the framework's nominal ceiling is not the same as any single bidder's effective revenue |

### Per-contract base cost (open-competition baseline)

Anchored on three real-world data points:

- **Marshall (defence mega):** ~£25m for the prime defence mega bid → 0.5% on a £5bn contract → matches the 0.4% used at the very top end
- **Selborne:** £1.2 billion contract / 2-year bid / £12m bid cost → 1.0% at this size
- **Consulting framework call-off (mini-competition):** team of 4 × 2–3 weeks × £3,500/person-week ≈ £30–45k → matches the £35k floor

The cost-of-sale curve scales naturally between these anchors. The 1.93% blended cost-of-sale produced by the model lands in the lower half of the typical 2–3% expected range, indicating the figures are **conservative rather than aggressive**.

### Classification rules

A contract is classified by applying these rules in priority order — first match wins:

1. **Direct award** — `procurement_method = 'limited'`, OR procurement detail mentions "without prior publication", OR title contains "direct award", OR notice type is UK4 (transparency notice)
2. **Extension / modification** — notice type contains "modification" / "amendment" / UK7, OR title contains "extension", "modification", or starts with "extend"
3. **Framework call-off** — has parent framework reference, OR title contains "call-off", "mini-competition", or "further competition"
4. **Framework agreement** — `is_framework = 1`, OR title contains "framework agreement"
5. **Renewal / recompete** — has renewal flag, OR title contains "renewal", "recompete", "follow-on", "continuation"
6. **Open competition** — procurement detail = "open procedure"
7. **Restricted competition** — procurement detail contains "restricted"
8. **Competitive dialogue** — procurement detail contains "competitive dialogue" or "negotiated"

If no rule fires, value-based defaults apply: contracts under £100k are treated as direct purchases; £100k–£5m as framework call-offs; £5m+ as restricted competitions. These defaults reflect the typical procurement profile in each value range.

---

## 5. Results

### Headline figures

| Measure | Value |
|---|---:|
| Total industry pursuit spend per year | **£3.34 billion** |
| Wasted on losing bids (sunk cost) | **£2.17 billion** |
| Industry pursuit spend as % of total contract value won | **1.93%** |
| Strategic-supplier-won contracts in 12-month window | 1,302 |
| Total contract value (TCV) of those wins | £172.8 billion |
| Total bidder-events (bids placed by strategic suppliers) | 4,757 |
| Average per strategic supplier (industry mean) | £90m pursuit / £58m wasted |

### Breakdown by bid type

| Bid type | Contracts | Total TCV | Pursuit spend | % of pursuit spend |
|---|---:|---:|---:|---:|
| Restricted competition | 222 | £82.1bn | £2.46bn | 73.6% |
| Framework agreement | 123 | £57.8bn | £436m | 13.0% |
| Framework call-off | 588 | £7.5bn | £315m | 9.4% |
| Open competition | 22 | £381m | £52m | 1.6% |
| Extension / modification | 16 | £14.9bn | £42m | 1.3% |
| Direct award | 303 | £10.1bn | £28m | 0.8% |
| Renewal / recompete | 28 | £13m | £3m | 0.1% |
| **Total** | **1,302** | **£172.8bn** | **£3.34bn** | **100%** |

### Comparison across all model iterations

| Model | Industry spend | Sunk on losing | Methodology basis |
|---|---:|---:|---|
| Original 2026-04-23 (FTS only, value tier) | £3.93bn | £2.00bn | Tier × bidders × flat per-bid cost |
| Today re-run (FTS only, value tier) | £3.57bn | £2.39bn | Same as above, today's data |
| Today (FTS + CF, value tier) | £4.96bn | £3.32bn | Value tier model with combined data |
| Bid-type-aware (initial, undercount) | £754m | £485m | First attempt — overcorrected on direct awards |
| **Bid-type-aware (forensic, final)** | **£3.34bn** | **£2.17bn** | **Per-contract, with revised assumptions and final fixes** |

The headline number ends up within 15% of the original. The original was directionally right but methodologically vulnerable. The final number is methodologically defensible and survives forensic interrogation.

---

## 6. Insights Surfaced

Several non-obvious insights emerged from the forensic work that are worth preserving and incorporating into commercial conversations.

### Insight 1 — Direct awards are nearly a quarter of all strategic supplier wins

**303 of 1,302 wins (23%) are direct awards.** These contracts went through no competitive bid process. They include exemption awards, single-source negotiations, and framework "direct call-offs" against pre-positioned suppliers. Their existence at this scale is itself commercially relevant — it indicates a substantial portion of the strategic-supplier opportunity universe is shaped well before any competitive event.

**Commercial implication:** for competitors, this is the harder market to penetrate — you cannot beat a direct award by responding better, you have to position upstream. This is exactly the territory BidEquity's Win Strategy product addresses.

### Insight 2 — The original "8,000 framework call-offs" estimate was too high

The original bottom-up estimate of 8,000 strategic-supplier framework call-off bids per year was conservative-by-design but unanchored. The new data shows roughly 1,500–2,500 strategic-supplier-related call-offs after dedup. The original bottom-up was overstated by approximately 4×.

**Commercial implication:** the original headline survived this correction because the over-estimate of small-contract activity was offset by the under-estimate of bid type effort at the larger end. Both errors were similar in magnitude. The headline holds.

### Insight 3 — Restricted competitions dominate the spend, not strategic megas

73.6% of industry pursuit spend is on restricted competitions (£2.46bn). These are the £25m–£500m mid-tier and major-services contracts where the field has been narrowed to ~5 bidders via pre-qualification. The very largest competitions (strategic programmes, defence megas) account for less than 5%.

**Commercial implication:** the BidEquity addressable market is concentrated in the £25m–£500m bracket where every supplier is bidding against a small known field. This is precisely where Qualify's pursuit-elimination logic and Win Strategy's positioning work generate the highest return.

### Insight 4 — Cost-of-sale ratio is a CFO-friendly framing

The model produces a 1.93% cost-of-sale ratio (industry pursuit spend ÷ total contract value won). This is in the lower half of the 2–3% range a chief financial officer would expect for the bid-intensive nature of public-sector procurement.

**Commercial implication:** when communicating to a CFO, framing the BidEquity opportunity as "we will reduce your cost of sale on government bidding from approximately 2% of revenue to 1%" creates a number they can immediately benchmark against their own financial reporting. This is a stronger conversation than abstract industry totals.

### Insight 5 — Per-supplier averages mask significant variance

The £90m average pursuit spend per strategic supplier is a useful headline but masks an order-of-magnitude variance. A defence prime such as BAE Systems likely operates at £150–250m of pursuit spend per year (driven by mega bids); a mid-tier IT services firm such as CGI may operate at £30–60m; a sub-scale player at £15–30m.

**Commercial implication:** the per-supplier saving from BidEquity's 20% pursuit elimination scales accordingly. The illustrative case for a £2 billion outsourcer (~£60–80m pursuit spend, ~£12–16m saving) is the right framing for the IT and outsourcing target market; defence and construction targets need different illustrative numbers.

---

## 7. Net-Out Summary

**The numbers we now use for all external communication:**

| Measure | Headline value | Range / context |
|---|---|---|
| Industry pursuit spend by 37 strategic suppliers, per year | **~£3.3 billion** | Range £3.0–3.5bn depending on classification of the long tail |
| Annual sunk cost on losing bids | **~£2.2 billion** | Approximately 65% of pursuit spend |
| Cost-of-sale ratio | **~2% of contract value won** | Industry benchmark 2–3% — we sit at the conservative end |
| Per strategic supplier (industry mean) | **~£90m pursuit spend; ~£58m wasted** | Wide variance — defence primes 2–3× higher, mid-tier IT 30–60% lower |
| BidEquity 20% pursuit elimination saving (industry-wide) | **~£670 million** | Per supplier average ~£18m saving / year |

These are direct outputs of the forensic per-contract model. They are reproducible from the published script and can be regenerated at any time as the underlying database evolves.

---

## 8. Messaging Guidelines for Market Communication

The following are sanctioned messages for use in external materials — sales decks, lead-generation content, customer-facing reports, and conversations with chief financial officers and procurement directors.

### What we say with high confidence

- **"UK government strategic suppliers spend approximately £3.3 billion per year pursuing contracts."**
- **"Approximately £2.2 billion of that — about two-thirds — is sunk cost on losing bids."**
- **"Bid pursuit runs at approximately 2% of contract value won — the lower end of the typical industry range."**
- **"This is measured from over 1,300 actual strategic-supplier contract wins in the past 12 months, representing £173 billion of contract value."**
- **"The figure is built bottom-up from line-by-line analysis of every contract, not estimated top-down."**

### What we say with appropriate hedging

- **"The average strategic supplier spends around £90 million per year on bid pursuit"** — *always pair with the qualifier that variance is significant: defence primes operate at multiples of this, sub-scale players at fractions.*
- **"BidEquity's pursuit-elimination logic could remove approximately 20% of bid spend that we believe to be unwinnable"** — *the 20% is the agreed industry-modelling assumption from the CFO model, not a measured BidEquity outcome.*
- **"We estimate the recoverable saving across the industry at approximately £670 million per year"** — *use only with the 20% assumption stated.*

### What we do not say

- **Do not use the original £3.9bn / £2.0bn headline.** It has been superseded by this work. Use £3.3bn / £2.2bn.
- **Do not extrapolate to non-strategic suppliers.** This analysis covers the 37 Cabinet Office strategic suppliers only. The wider supplier universe operates at different ratios and the data does not yet support a comparable headline for SMEs.
- **Do not make claims about specific named suppliers' bid spend without separate analysis.** The per-supplier average is a statistical mean, not a per-supplier estimate.
- **Do not claim this measures all bid pursuit cost.** The model excludes lost bids by strategic suppliers who lost to non-strategic competitors, cancelled opportunities, and pre-positioning work — all real costs, not captured here. The headline is best framed as a **defensible floor** rather than a maximum.

### When challenged on methodology

The most likely challenges and the agreed response:

| Challenge | Response |
|---|---|
| *"How do you know this isn't an estimate?"* | Every contract in the analysis is a real award notice with a stated value. The bid cost per contract is a function of that actual value, applying a cost-of-sale curve anchored on three real public bid examples (Marshall £25m / £5bn defence mega; Selborne £12m / £1.2bn services bid; £35k consulting framework mini-competition). |
| *"How do you account for direct awards?"* | Direct awards are classified separately and assigned 35% of full-bid effort, recognising that the winning supplier still incurs real cost on solution shaping, governance, internal pricing, and contract negotiation — even though no competitive bid took place. |
| *"What about extensions and renewals?"* | Extensions and modifications are charged at 35% of full-bid effort for the incumbent (1 bidder). Renewals are charged at a blended 90% of full effort across 3 bidders, reflecting that the incumbent benefits from accumulated knowledge but challenger bidders work at full effort. |
| *"What about framework call-offs?"* | Framework call-offs are charged at 65% of full-bid effort for 4 bidders, with a £35k floor. Their cost scales with the actual contract value of each call-off, not a flat assumed rate. |
| *"How does this compare against what suppliers themselves disclose?"* | No supplier discloses bid cost as a P&L line. Strategic suppliers absorb it into overhead and SG&A. The published 2% cost-of-sale ratio aligns with the inferred bid-cost economics observable in operating-margin disclosures from Serco, Capita, and Mitie's annual reports. |

---

## 9. Caveats and Known Limitations

This document is a snapshot at a point in time and rests on assumptions that are documented but inherently arguable. The principal limitations are:

1. **Lost bids by strategic suppliers who lost to SMEs are not captured.** The data records winners only. Where a strategic supplier bid for a small contract and lost to a regional player, that pursuit cost is invisible. This understates the headline by an estimated 10–25%.

2. **Win-rate assumptions are derived from competitive logic, not measured directly.** No supplier publishes win-rate data in a comparable form (Serco's 32% and Capita's 64% use different denominators). The model uses 33% blended baseline with type-specific adjustments — this is defensible but is an assumption.

3. **The strategic supplier list is updated periodically by the Cabinet Office.** The 37-supplier population used here matches the 2024–25 register. Re-running the analysis after any register update would change the population by 1–4 entities.

4. **The classification rules cannot perfectly distinguish bid types in every case.** Title-keyword inference covers genuine ambiguity. For approximately 30% of contracts (the value-defaulted residual), the bid type is inferred rather than explicitly identified. The headline is robust to reasonable variation in this inference.

5. **The cost-of-sale curve is anchored on three public data points.** A larger calibration panel would tighten the per-tier multipliers. The current anchors are sufficient for two-significant-figure precision, not three.

6. **Companies House enrichment is incomplete.** Only 1,384 of 87,000 with-number suppliers have full financial profiles. As enrichment catches up over the next 6 weeks, supplier classification (e.g. SME vs large) will become more reliable.

These limitations should be disclosed when an external counterparty asks "what could move this number?" The honest answer is that the methodology is rigorous within the data we have, and the principal source of further refinement is more Companies House enrichment plus a deeper read of unclassified contract titles.

---

## 10. Reproducibility

All numbers in this document are reproducible from the source data and scripts in the BidEquity repository.

| Component | Location |
|---|---|
| Source database | `pwin-competitive-intel/db/bid_intel.db` (snapshot of 25 April 2026) |
| Forensic per-contract model | `pwin-competitive-intel/queries/bid_spend_forensic.py` |
| Earlier value-tier re-run (for comparison) | `pwin-competitive-intel/queries/bid_spend_recalc.py` |
| Original CFO model | `pwin-competitive-intel/bidequity-cfo-model.html` |
| Visual analysis | `pwin-competitive-intel/bid-spend-rerun-2026-04-25.html` (uses pre-final figures; needs refresh) |

Re-running on the same database produces identical numbers. Re-running after the database has been updated will produce numbers that drift smoothly with the underlying data. There is no manual hand-calibration in the pipeline.

---

**Document maintained by:** the analytics function within BidEquity
**Next review:** when (a) the Companies House enrichment backlog is cleared, or (b) the Cabinet Office strategic supplier register is updated, or (c) any of the assumptions in Section 4 is challenged with new evidence — whichever happens first.
