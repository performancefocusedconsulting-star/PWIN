# Pursuit Cost Model — Proposed Extensions

**Date:** 27 April 2026
**Status:** Proposal (not a rebuild)
**Reference model:** `pwin-competitive-intel/bidequity-cfo-model.html`
**Reference methodology:** `pwin-competitive-intel/docs/strategic-supplier-pursuit-spend-methodology-2026-04-25.md`

---

## 1. What the current model already does well

The current chief financial officer (CFO) business case model is a credible foundation. It carries six contract-value tiers (framework call-off under £5m, notified small £5–25m, notified mid £25–100m, major services £100–500m, strategic programme £500m–5bn, defence mega £5bn+), each with its own per-bid cost (from £35,000 at the bottom to £25 million at the top). It then adjusts for seven distinct types of bid (open competition, restricted, competitive dialogue, framework call-off, renewal, extension, direct award), with multipliers ranging from 35% of base effort for an extension to 130% for a competitive dialogue. Five sector profiles (large outsourcer, IT and digital, defence prime, facilities management, construction) carry their own bid-spend rate as a percentage of revenue (1.4% to 2.5%), and a win-rate slider scales the bid volume up or down. This was the right starting point: it is anchored on real contracts (1,302 wins over twelve months, £172.8 billion of contract value) and on three real bid-cost data points (Marshall, Selborne, a consulting framework call-off). It produces a 1.93% blended cost-of-sale ratio that a finance director can immediately sense-check against their own books.

## 2. Why extension is needed now

Pursuit Return on Investment (Pursuit ROI = Total Contract Value × Margin × Probability of Going Out × Probability of Winning ÷ Pursuit Cost) is becoming the headline measure for the BidEquity product family. The buyer-behaviour module being built this quarter gives us the first empirical Probability of Going Out number (the chance the buyer actually proceeds to award rather than cancelling, going dormant, or pulling the work). That tightens up the top of the equation. The bottom of the equation — Pursuit Cost — is now the next leverage point. Today, pursuit cost is calculated by lumping a great deal of real-world variation into single tier-and-type multipliers. Two contracts of the same size and type can carry pursuit costs that differ by a factor of two or three depending on when the supplier engaged, whether they are defending or attacking, how many lots are in play, how long the capture period lasted, and how complex the pricing is. The model does not currently see any of that.

## 3. Five proposed extensions

### 3.1 Stage at engagement

**What it is.** A four-step setting recording when the supplier first started spending capture money: planning (before any tender notice exists), pre-publication (early signals are out), post-publication (the formal tender is live), or late capture (the supplier joined after the bid window opened).

**Why it matters.** Earlier engagement adds months of capture spend before any bid is written, but it also gives the supplier the chance to shape the buyer's requirement — which raises the probability of winning. Stage and cost cannot be modelled as one number.

**Realistic value range.** A planning-stage engagement should add roughly 1.6–2.0× to base bid cost; pre-publication 1.3–1.5×; post-publication 1.0× (the current default); late capture 0.85–0.95× (less time, less cost, but also weaker positioning).

**Evidence anchor.** The Selborne benchmark already in the methodology is a two-year capture — that is a planning-stage engagement carrying a £12 million cost on a £1.2 billion contract. A late-capture entry on the same contract would be a fraction of that.

### 3.2 Defended versus attack bid

**What it is.** A single switch indicating whether the supplier is the existing provider defending a contract or a challenger attacking it.

**Why it matters.** An incumbent already has the buyer relationships, the staff in place, the running operating model, and most of the technical evidence. A challenger has to invent all of that for the bid.

**Realistic value range.** Defended bids should run at 50–70% of attacker cost (a 30–50% saving). The current model carries this implicitly inside the renewal/recompete blended rate, but the user cannot see or override it.

**Evidence anchor.** The methodology already assumes the incumbent in a renewal works at 70% effort and the two challengers work at 100% — that 30% gap is the underlying number.

### 3.3 Number of lots

**What it is.** A whole number for how many lots the supplier is bidding on within a single tender.

**Why it matters.** Every additional lot adds work, but most of the win story (corporate credentials, sector evidence, methodology, governance) can be reused. The cost grows but it grows slower than the lot count.

**Realistic value range.** 1 lot = 1.0× (the current default). 2 lots ≈ 1.4×. 3 lots ≈ 1.7×. 4 lots ≈ 1.9×. 5+ lots ≈ 2.0–2.2× (the curve flattens because reuse dominates).

**Evidence anchor.** A power-law fit (cost = lots^0.5) produces those multipliers. The same shape is well-attested in software estimation work (Cocomo) and is consistent with the bid-team experience that lot two and lot three are mostly a bid-management overhead, not a doubling of effort.

### 3.4 Capture period length

**What it is.** Months of capture work before the formal bid is released.

**Why it matters.** The current model is silent on this. A six-month capture and a two-week capture both get charged the same in today's tier-and-type lookup. Capture spend is real — partner time, buyer engagement, solution architecting, market shaping.

**Realistic value range.** Add roughly £20,000–£40,000 per capture month for a notified-mid contract; £80,000–£150,000 per capture month for a major-services contract; £400,000+ per month for a strategic programme. Floor at zero (some contracts are pure post-publication response).

**Evidence anchor.** The Selborne reference (£12 million over 24 months ≈ £500,000 per month) anchors the strategic-programme rate. The consulting framework call-off (4 people × 2–3 weeks ≈ £35,000 in the bid window with no real capture) anchors the floor.

### 3.5 Pricing complexity

**What it is.** A four-step setting: fixed price, open book (transparent costs plus an agreed margin), variable price (indexed or volume-linked), or risk-share (gain/pain mechanism tied to outcomes).

**Why it matters.** Open book and risk-share contracts demand far more financial modelling, scenario analysis, governance review, and pricing-committee time than a fixed-price submission. The cost difference is not in the writing — it is in the assurance work behind the price.

**Realistic value range.** Fixed price 1.0× (default). Open book 1.20–1.30×. Variable 1.10–1.15×. Risk-share 1.30–1.50× (the heaviest because it requires probabilistic financial modelling).

**Evidence anchor.** Major government services contracts using risk-share (rail franchising, prison services, employment programmes) are widely understood inside the bid community to carry materially higher pricing-team and assurance burden. The methodology already notes that "the saving is highest on research-heavy phases and lowest on governance-intensive activities" — risk-share is governance-intensive almost by definition.

## 4. Interaction with Probability of Going Out

The Pursuit ROI formula treats Pursuit Cost and Probability of Going Out (PGO) as independent inputs. They are not fully independent. The clearest case is stage at engagement: a planning-stage engagement raises capture cost (by working longer and earlier) **and** raises PGO (because the supplier can help the buyer shape a viable requirement, reducing the chance the project is cancelled or goes dormant). Defended bids similarly tilt both numbers — incumbents can read distress signals earlier and pull out before sunk cost mounts.

The right design move is not to merge the two numbers. The model should expose them side by side, with a short consultant note where the link is strongest (for example: "moving from post-publication to planning-stage engagement adds an estimated £180k of capture cost but lifts PGO from 55% to 75% — net Pursuit ROI improves"). The consultant should always see both inputs before the calculation runs, never the joint number alone.

## 5. Suggested build order

**Ship first** (high value, low effort — the parameters already exist in adjacent form in the methodology):

1. **Defended versus attack bid** — already implicit in the renewal multiplier; surfacing it as an explicit switch is a half-day change.
2. **Number of lots** — clean mathematical curve, no new evidence required, useful on almost every live pursuit.

**Design before building** (real value, but the calibration needs work):

3. **Stage at engagement** — needs the capture-period interaction modelled cleanly so the numbers are not double-counted.
4. **Pricing complexity** — the multipliers need calibration against three or four real risk-share bids before going live.

**Defer until live engagement validation** (least clear today):

5. **Capture period length** — the cost-per-month rates are anchored on only two real data points. A handful of live BidEquity engagements will produce a much better curve. Build the field, collect the data, calibrate later.

## 6. Open questions for the consultant

1. For defended bids, is the 30–50% saving net of the additional effort an incumbent now has to put into a *retention narrative* (proving they have not become complacent)? Or is that effort already inside the saving?
2. Should number-of-lots scaling differ by bid type? A framework call-off with three lots may behave differently from a competitive dialogue with three lots (the dialogue has multiple rounds per lot, compounding the effort).
3. For pricing complexity, where does target-cost contracting (a hybrid of open book and risk-share, used in NHS and rail) sit? Is it close enough to risk-share to share the multiplier, or does it deserve its own setting?
4. For capture period length, do we want to allow the consultant to enter actual months elapsed (which suits Verdict's retrospective use) or expected months ahead (which suits Qualify's forward-looking use)? Or both, with the model picking up whichever is filled?
5. When a bid is on a large framework with multiple lots **and** the supplier is the incumbent on some lots only, how should the model combine the defended and number-of-lots multipliers? Pure multiplication will overstate the saving on the lots they actually defend.

---

**Next step.** When two or three of these answers are clear, we can extend the existing HTML model in place — adding the new inputs alongside the current sliders rather than rebuilding the calculator. The methodology document already has a clear "Section 4 — Assumptions" structure; the new variables should be folded in there, with each one carrying its own evidence anchor exactly as the current ones do.
