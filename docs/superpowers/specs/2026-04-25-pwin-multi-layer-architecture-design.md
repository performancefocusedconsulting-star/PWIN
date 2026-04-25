# PWIN Multi-Layer Score Architecture — Design

**Date:** 25 April 2026
**Status:** Draft for review
**Author:** Architecture conversation, consolidated into spec
**Touches:** PWIN Qualify, PWIN Win Strategy, PWIN Competitive Intel, PWIN Portfolio, PWIN Platform

---

## Executive Summary

This document consolidates several strands of thinking into one architectural decision: **PWIN the score is moving out of any single product and becoming a platform-level composite** that combines multiple distinct lenses on the same opportunity.

Today, Qualify is the only thing that produces a "PWIN percentage." That conflates the company brand (PWIN), the product (Qualify), and the score itself. It also forces Qualify to carry credibility weight a 25-question questionnaire cannot bear in front of a sceptical executive audience.

Going forward:

- **Qualify becomes one of several inputs** — a structured assessment of the team's view, producing a per-category and headline pursuit-viability tier plus rationale, recommendations, evidence, and confidence. Qualify does not claim to be the probability of winning, does not surface a number, and does not use the word PWIN.
- **The PWIN score lives at the platform level** and combines several lenses: a historical pattern lens drawn from real procurement data, the Qualify assessment lens, evidence accumulated by Win Strategy during capture, a structural ceiling drawn from established methodology, and a discipline that mathematically discounts subjective claims that have no evidence behind them.
- **The score is presented as layers, not a single splashed number.** Executives see how the answer was reached before they see the answer. The single number exists for portfolio aggregation and weighted pipeline value, but it does not lead the disclosure.
- **Confidence is a first-class output alongside the score.** "PWIN 42%, medium confidence, here is what would raise it" is a fundamentally different conversation from "PWIN 42%, trust us."

The commercial thesis behind this design is unchanged. Strategic suppliers in this market spend roughly £3bn a year on bid pursuit, of which around £2bn is wasted on opportunities they were never going to win. Existing PWIN methodologies are either too subjective (vulnerable to over-scoring driven by sales optimism) or too academic (impractical at speed). The opportunity is to build a synthesis — one defensibly quantitative, transparently layered, evidence-grounded probability engine that helps senior leaders allocate capital intelligently. No competitor in the UK market is doing this today.

---

## 1. The Architectural Shift

### 1.1 The conflation problem today

Three different things currently share the name "PWIN":

| Meaning | What it is today |
|---|---|
| The brand | The umbrella name for the platform and product family |
| The score | A single percentage produced by the Qualify product |
| The methodology | The approach to thinking about probability of winning, expressed through the Qualify questionnaire |

When the score lives inside a single product, every limitation of that product becomes a limitation of the score. Qualify is a structured self-assessment with AI-assisted challenge. It is genuinely useful, but it cannot — by itself — produce a probability that a sceptical bid director will accept as the answer. They will rightly ask: what about the historical evidence? What about the capture intelligence we have gathered over the last four months? What about the structural reality that this is a new buyer and a new offering?

A 25-question scorecard cannot answer those questions on its own.

### 1.2 What changes

PWIN the score is decoupled from any individual product:

- **Qualify** produces a per-category viability tier across five categories (Buyer Need & Decision Logic; Stakeholder Position & Access; Competitive Position & Incumbent Dynamics; Procurement, Proposition & Solution Fit; Commercial, Delivery & Pursuit Readiness) on a five-band scale (Strong / On Track / Conditional / Major Concerns / Walk Away), each with rationale, recommendations, evidence, and confidence — plus a headline pursuit viability tier on the same scale. It does not produce a single probability and never displays a numerical score.
- **Win Strategy** produces capture artefacts (buyer thesis, stakeholder map, competitor field map, win themes, proof map, evidence log) that accumulate during the capture window. It does not produce a probability either.
- **Competitive Intel** (the contracts database) produces historical patterns — award shares, incumbency strength, buyer-supplier relationship history, competition density. It does not produce a probability.
- **The PWIN score itself** is computed at the platform level by combining the above into a single composite, applying structural ceilings and bias-correction discipline.

This is more honest about what each product can claim, and it lets the score draw on richer, more diverse inputs than any single product could ever produce.

### 1.3 Why this strengthens the commercial position

The competitive landscape was reviewed in a separate analysis (US-focused platforms like Cleat.ai, pWin.ai, TechnoMile). One framing from that analysis was "BidEquity sits above the algorithm — the algorithm produces the score, BidEquity decides whether to trust it." That framing is now obsolete. The decision recorded here is stronger and harder to copy: **PWIN runs the algorithm, and the algorithm is a multi-layered composite that includes the judgement layer competitors rely on consultants for.**

---

## 2. What Qualify Becomes

Qualify retains its full intellectual content. What changes is the framing of its output.

### 2.1 New output shape

| Item | What Qualify produces |
|---|---|
| Per-category viability tier | Each category placed on a five-band tier scale: **Strong / On Track / Conditional / Major Concerns / Walk Away**. Tier mapping is stage-aware (Identify / Capture / Pursue / Submit) — the same evidence base maps to a more lenient tier early in capture and a harsher tier closer to submission. |
| Headline pursuit viability tier | A roll-up across the categories on the same five-band scale, paired with confidence. This is the headline disclosed output of Qualify. |
| Per-category rationale, recommendations, and evidence | What is driving the tier, what would move it up, and what evidence backs it. |
| Per-question detail | The underlying question responses on the four-band agreement scale (Strongly Agree / Agree / Disagree / Strongly Disagree), each with an evidence-quality grade and Alex Mercer's challenge notes. |
| Rebid risk assessment | When the incumbent rebid modifier is active, the additional dedicated assessment. |
| Inflation flags | Per-category indicators where the team's self-assessment exceeded what the evidence supports. |
| Confidence indicator | How complete and how recent the assessment is. |

What Qualify no longer produces, and what it never says out loud:

- **Qualify never surfaces a numerical score and never uses the word PWIN.** Its disclosed vocabulary is *pursuit viability*, *confidence*, *evidence*, and *recommendations*.
- A numerical score per category is still computed under the hood (it is what drives the tier mapping and what feeds the platform-level PWIN composite), but `surfacedToUser` is `false` by design — the team sees the tier, the rationale, and the coaching, not the number.
- The verdict that follows from the integrated score (Pursue / Condition / Walk Away at platform level) is informed by Qualify's viability tier but is decided at the platform layer, where the other four layers also contribute.

### 2.2 Why Qualify is still valuable

Qualify is the *only* layer that captures the team's structured judgement. Historical pattern data tells you what happened in the past. Win Strategy artefacts tell you what intelligence has been gathered. Neither tells you what the team thinks about the opportunity in a structured, comparable, challenged form. Qualify does. It also provides the input into the cognitive discount mechanism (described in Section 4) — the mechanism that haircuts subjective claims unless evidence backs them.

### 2.3 Re-running Qualify

Qualify is designed to re-run periodically across the capture window. Each re-run is now an *update* to the platform-level PWIN score, not a separate score in its own right. The trajectory of the integrated PWIN score over time is what the executive sees — not a series of disconnected Qualify snapshots.

---

## 3. The Layer Model

The PWIN score is built from five layers, each independently defensible, each presenting its own contribution to the final composite. The layers are loosely modelled on the synthesis published in market thought leadership (the Contextual Algorithmic-Behavioural framework), adapted to PWIN's product architecture and to the data we actually have.

### 3.1 Layer 1 — Historical Pattern (the data anchor)

**What it produces:** A baseline probability grounded in real procurement data. For a given opportunity (defined by buyer, scope, value band, procurement route, market position), it answers the question: *historically, in this kind of slot, how often does an organisation like this one win?*

**What feeds it (v1):**

- Award shares within the relevant scope, by count and value
- Buyer-supplier relationship strength (how often this buyer has awarded to this supplier or its parent)
- Incumbency status and stickiness of the incumbent in this specific scope
- Procurement route distribution and the win-rate implications of route choice (open competition vs framework call-off vs direct award have very different incumbency dynamics)
- Competition density (average bidder counts and their distribution)
- Companies House enrichment for supplier identity resolution and group-level rollup

**What it does not claim (v1):** This layer is descriptive analytics, not machine learning. It is honest about pattern matching against real history. It is *not* claiming to be a predictive classifier trained on labelled outcomes — that is v3 work and depends on PWIN accumulating its own pursuit history before there is enough labelled data to train a credible model.

**Why this is enough for v1:** Honest descriptive analytics on the contracts data is already a step-change above what any UK competitor offers. None of them have a cleaned-up master list of 1,928 buyers and 82,637 canonical suppliers grounded in 175,000+ historical contracts.

### 3.2 Layer 2 — Qualify Assessment (the team's view)

**What it produces (disclosed to the user):** A per-category viability tier on a five-band scale (Strong / On Track / Conditional / Major Concerns / Walk Away), each with rationale, recommendations, evidence quality, and confidence — plus a headline pursuit viability tier on the same scale. Tier mapping is stage-aware (Identify / Capture / Pursue / Submit). When viability comes back as Conditional or worse, a qualification coaching process surfaces the major deficiencies and what would need to change to move the tier up. Qualify never surfaces a numerical score and never uses the word PWIN — its vocabulary is viability, confidence, evidence, and recommendations.

**What it produces (under the hood, fed up to the platform):** A numerical category score per category, with confidence weighting. This is what feeds the platform PWIN composite alongside the other four layers. The number is computed but `surfacedToUser` is `false` by design.

**What feeds it:** The question pack, Alex Mercer's persona, the opportunity-type calibration, and the rebid modifier when applicable.

**What it claims:** A structured, challenged, comparable view of how the pursuit team perceives the opportunity. This is genuine judgement — it is not the same as historical evidence and it is not the same as capture intelligence, but it is the input that captures the team's reading of factors no data feed can see.

**What it does not claim:** That the team's view is the answer. The Cognitive Discount Factor (Layer 4) explicitly haircuts the underlying category scores that lack supporting evidence in Win Strategy artefacts before they contribute to the platform composite.

### 3.3 Layer 3 — Capture Evidence (the validation)

**What it produces:** A categorisation of which subjective claims in the Qualify assessment are backed by evidence and which are not.

**What feeds it:** Win Strategy's accumulating capture artefacts in `win_strategy.json` — buyer interaction logs, signed teaming agreements, evidence of pre-RFP shaping, documented site visits, win theme proof points, competitor intelligence with sources.

**What it claims:** That a category score of 8/10 on Customer Relationship is materially different from the same 8/10 backed by three logged executive interactions and a captured buyer pain-point statement. The first is opinion; the second is evidence-grounded.

**Why this is the differentiator no competitor can copy:** Cleat.ai, pWin.ai, and others have no equivalent of Win Strategy. They cannot apply this layer because they do not have the artefacts to apply it against.

### 3.4 Layer 4 — Cognitive Discount Factor (the discipline)

**What it produces:** A mathematical adjustment to the under-the-hood Qualify category scores based on Layer 3, before they contribute to the platform composite.

**How it works:** Each underlying category score from Qualify (the hidden numerical score, not the disclosed viability tier) is examined against the evidence in Win Strategy. If a category lacks supporting evidence where evidence is reasonable to expect at the current pursuit stage, a haircut is applied to reduce that category's contribution to the composite. If evidence exists, the haircut is removed proportional to the strength and recency of the evidence. This is the mechanism that prevents "Happy Ears" — the well-documented industry phenomenon where capture teams over-score subjective categories to justify continued pursuit.

A flat 15% haircut applied uniformly would punish two very different situations identically: (a) a team claiming a strong buyer relationship with no logged interactions to back it up (genuine Happy Ears that the CDF should bite), and (b) a team strategically entering a new sector at the start of capture, where evidence is not yet possible (legitimate new-territory development that the CDF should *not* punish). The CDF must distinguish them.

**Three-part design:**

**(1) Stage-aware haircut.** The haircut percentage scales with where the pursuit is in the lifecycle. The same staging that drives the Qualify viability tier mapping (Identify / Capture / Pursue / Submit) drives the CDF intensity:

| Stage | CDF haircut for unevidenced evidence-bearing categories | Why |
|---|---|---|
| Identify | 0% | No evidence is expected yet — assessment is mostly strategic fit |
| Capture | 5% | Building should be underway; light pressure on unevidenced claims |
| Pursue | 15% | Full discipline — the gap between claim and evidence becomes a real risk |
| Submit | 20% | By now the evidence should exist or the claim is empty |

**(2) Claim-type-aware application.** Not every Qualify category is the kind that needs an interaction log to back it. Each category is tagged as either *evidence-bearing* (e.g. Stakeholder Position & Access, Buyer Need & Decision Logic, Competitive Position & Incumbent Dynamics — claims here are about external relationships and intelligence and ought to be backed by logged artefacts) or *strategic-fit* (e.g. Procurement, Proposition & Solution Fit at the conceptual level; Commercial, Delivery & Pursuit Readiness at the team-capability level — claims here are about capability and judgement, not external evidence). The CDF acts on the evidence-bearing categories only. The strategic-fit categories are not haircut for absence of evidence because evidence is not the right test for them.

**(3) Doesn't double-count Historical Pattern.** The Historical Pattern layer already captures the structural challenge of new-sector entry. A supplier with no awards in defence will get a low Historical Pattern anchor for a defence pursuit — that is the data telling the truth. Adding a CDF haircut on top of an already-low anchor would double-count the same structural reality. The CDF acts only on the dimension Historical Pattern doesn't already reflect — the team's *opinion-vs-evidence gap*, not the team's *track-record-in-the-segment gap*.

**Together:** new-sector entrants get a fair read — low Historical Pattern (correctly), no piling-on from the CDF at Identify/early Capture, and the Structural Ceiling caps optimism at 25% (new customer, new offering) which is the right ceiling for that situation. Inflated assessments at Pursue/Submit get the discipline they need.

**Why it matters at v1:** Even before the historical pattern layer is mature, the Cognitive Discount Factor on its own raises PWIN above any current scoring methodology. It is a discipline mechanism, not a data mechanism. It works from day one once Qualify and Win Strategy are linked.

**Tunable parameters (deferred to implementation):**

- The four stage haircut percentages (proposed 0% / 5% / 15% / 20%) — subject to calibration once labelled outcomes accumulate
- The split of Qualify categories into evidence-bearing vs strategic-fit (proposed v0.2 split listed above) — subject to review once first live engagements run
- How evidence strength is graded (binary present/absent at v1; partial / weighted at v2)
- Decay rate (evidence loses validity over time as the buyer context evolves)

### 3.5 Layer 5 — Structural Ceiling (the reality constraint)

**What it produces:** A hard cap on the PWIN score derived from the opportunity's market position.

**How it works:** Following the SMA Threshold Matrix logic from established methodology, the ceiling depends on the buyer/offering quadrant:

| Quadrant | Maximum PWIN |
|---|---|
| Current customer, current offering | 95% |
| Current customer, new offering | 75% |
| New customer, current offering | 50% |
| New customer, new offering | 25% |

For incumbent rebid pursuits, an additional Shipley-derived cap applies: PWIN for retaining an existing contract should not exceed 70% (this enforces honest acknowledgment of customer fatigue and re-tender risk).

**Why it matters:** Without a structural ceiling, a team scoring optimistically on Qualify can produce a PWIN that violates the basic physics of the market. The ceiling forces the score to respect the macro-position regardless of micro-enthusiasm. This single mechanism alone has been shown in published methodology to materially reduce wasted bid spend.

### 3.6 The integration mechanism

The five layers are combined into a single PWIN score and a confidence indicator. The headline architecture is **Option A under the hood, layered display on the surface**:

```
Step 1  Historical Pattern produces an anchor probability (Layer 1)
Step 2  Qualify produces per-category viability tiers for disclosure
        and under-the-hood category scores for composition (Layer 2)
Step 3  Capture Evidence categorises which Qualify claims are backed (Layer 3)
Step 4  Cognitive Discount Factor adjusts the under-the-hood Qualify
        category scores per Layer 3 (Layer 4)
Step 5  Anchor + adjusted Qualify produce a raw composite PWIN
Step 6  Structural Ceiling applies as a hard cap (Layer 5)
Step 7  Confidence indicator is computed from completeness and recency

Output  PWIN score + confidence + visible layer breakdown
```

#### 3.6.1 The composite formula (v1) — anchor + bounded adjustment

The Historical Pattern layer is the **anchor** and the adjusted Qualify layer is a **bounded adjustment** to that anchor. This is more defensible than a flat weighted average because the two layers describe different things — Historical Pattern says *how this kind of opportunity normally goes*, Qualify says *what this team thinks about this specific case*. The team's view is the most volatile input in the system and bounding its influence respects the relative trustworthiness of each layer.

The v1 formula:

```
Q_overall = weighted_average(Q_adjusted_per_category, category_weights)
            -- where Q_adjusted_per_category is the under-the-hood
            -- score per category after CDF haircut (Layer 4)

adjustment = ((Q_overall - 0.5) / 0.5) × 15 percentage points
             -- bounded at ±15 points; 0.5 is the neutral midpoint;
             -- so Q_overall = 0.8 produces +9pp, Q_overall = 0.2 produces -9pp

raw_composite = Historical_Pattern + adjustment

PWIN = min(raw_composite, Structural_Ceiling)
```

**Worked behaviour:**

- If the team's adjusted Qualify view sits at the neutral midpoint (Q_overall = 0.5), the composite is just the historical anchor. The team's read is consistent with the data; no shift.
- If the team's view is positive (Q_overall = 0.8), the composite shifts the anchor up by ~9 percentage points. Bounded — even maximum optimism cannot move the answer more than 15 points off the historical anchor.
- If the team's view is negative (Q_overall = 0.2), the composite shifts the anchor down by ~9 percentage points. Same bound on pessimism.

**Why ±15 points is the v1 bound:**

The bound reflects how much weight v1 is willing to give to a layer that has not yet been calibrated against outcomes. A larger bound (say ±25) makes the team's view dominate the answer in cases where Historical Pattern is moderate; a smaller bound (say ±5) makes Qualify decorative. ±15 keeps Qualify materially influential without letting it overrule a strong historical signal in either direction. The bound is a tunable parameter and should be re-calibrated once ~50 labelled pursuit outcomes exist.

**Why this is honest at v1:**

This is not Bayesian inference. It is anchor-plus-adjustment composition with explicit, transparent maths. Anyone reading the composite can trace the headline number back to the layer values. The decision (recorded here) is that **the data we have at v1 cannot support full Bayesian rigour without producing false precision**. v2 introduces explicit Bayesian updating once we have more confidence in the priors. v3 introduces a true predictive classifier once ~100 labelled pursuit outcomes accumulate.

#### 3.6.2 Worked examples

The CDF design (§3.4) and the composite formula (§3.6.1) need to be seen working on representative cases. Three worked examples follow. Categories are abbreviated; assume the v0.2 five-category model: BNDL = Buyer Need & Decision Logic (evidence-bearing), SPA = Stakeholder Position & Access (evidence-bearing), CPID = Competitive Position & Incumbent Dynamics (evidence-bearing), PPSF = Procurement, Proposition & Solution Fit (strategic-fit), CDPR = Commercial, Delivery & Pursuit Readiness (strategic-fit).

**Example A — Incumbent defending a contract at Capture stage.**

Context: large central-government BPO contract up for recompete. Team has worked the account for years.

| Layer | Value | How |
|---|---|---|
| Historical Pattern | 60% | Strong incumbency advantage in similar awards across the buyer's portfolio |
| Qualify (under-the-hood, before CDF) | BNDL: 0.75, SPA: 0.80, CPID: 0.70, PPSF: 0.85, CDPR: 0.78 |
| Evidence flag (per category) | BNDL: yes, SPA: yes, CPID: no, PPSF: n/a (strategic-fit), CDPR: n/a (strategic-fit) |
| CDF haircut at Capture | 5% on unevidenced evidence-bearing categories. CPID is the only one. |
| Q_adjusted | BNDL: 0.75, SPA: 0.80, CPID: 0.70 × 0.95 = 0.665, PPSF: 0.85, CDPR: 0.78 |
| Q_overall (weighted by category weights from v0.2 weight profile, BPO managed service) | ≈ 0.77 |
| Adjustment | ((0.77 − 0.5) / 0.5) × 15 = +8.1pp |
| Raw composite | 60% + 8.1 = 68.1% |
| Structural Ceiling | Existing customer, current offering = 95% — does not bite. **But Shipley recompete cap at 70%** does bite (incumbent rebid). |
| **Final PWIN** | **68.1%** |

The team's bullishness shifts the anchor up by 8 points, the unevidenced competitive intelligence costs them ~3 points of category contribution, the ceiling sits comfortably above the answer. Defensible read.

**Example B — Strategic new-sector entry at Identify stage.**

Context: established consultancy with no defence track record exploring whether to pursue an MOD opportunity.

| Layer | Value | How |
|---|---|---|
| Historical Pattern | 12% | Supplier has no defence award history — data correctly reflects new-sector difficulty |
| Qualify (under-the-hood, before CDF) | BNDL: 0.70, SPA: 0.60, CPID: 0.55, PPSF: 0.75, CDPR: 0.80 — team is excited about the strategic fit and capability |
| Evidence flag (per category) | All marked "n/a — Identify stage" |
| CDF haircut at Identify | **0% across all categories** — no evidence is expected at this stage. The new-sector entrant is not punished for the absence of artefacts that cannot yet exist. |
| Q_adjusted | Unchanged from raw |
| Q_overall | ≈ 0.70 |
| Adjustment | ((0.70 − 0.5) / 0.5) × 15 = +6.0pp |
| Raw composite | 12% + 6.0 = 18.0% |
| Structural Ceiling | New customer, new offering = 25% — does not bite at 18% |
| **Final PWIN** | **18%** |

This is the test case from the design discussion. The new-sector entrant gets a fair read. Historical Pattern correctly reflects that this is a structurally hard pursuit (the data is not flattered). The CDF does not pile on. The team's strategic conviction lifts the answer modestly. The ceiling is the cap of last resort and does not bite. The supplier sees 18% PWIN with banded confidence — a low number that is honest about the structural challenge, not a punitive zero.

**Example C — Optimistic team at Submit, evidence base is thin.**

Context: competitive segment where this supplier has a moderate track record. Team has been in capture for months and is now at submission, but the evidence log is thin and several subjective claims have nothing backing them.

| Layer | Value | How |
|---|---|---|
| Historical Pattern | 40% | Competitive segment, moderate supplier record |
| Qualify (under-the-hood, before CDF) | BNDL: 0.85, SPA: 0.80, CPID: 0.75, PPSF: 0.78, CDPR: 0.82 |
| Evidence flag (per category) | BNDL: no, SPA: no, CPID: no, PPSF: n/a, CDPR: n/a |
| CDF haircut at Submit | 20% on unevidenced evidence-bearing categories. All three of BNDL, SPA, CPID. |
| Q_adjusted | BNDL: 0.85 × 0.80 = 0.68, SPA: 0.80 × 0.80 = 0.64, CPID: 0.75 × 0.80 = 0.60, PPSF: 0.78, CDPR: 0.82 |
| Q_overall | ≈ 0.69 |
| Adjustment | ((0.69 − 0.5) / 0.5) × 15 = +5.7pp |
| Raw composite | 40% + 5.7 = 45.7% |
| Structural Ceiling | (Mixed — assume new customer, current offering = 50% — does bite if raw goes higher) |
| **Final PWIN** | **45.7%** |

The team's view, before discipline, would have lifted the anchor to 40% + 11.4pp = 51.4% (above the structural ceiling, capped at 50%). The CDF discipline brings the unevidenced over-scoring back down. The supplier sees a moderate-confidence 46% — appropriately moderated for a pursuit where the team is bullish but has not built the evidence base.

These three examples demonstrate the three behaviours that mattered most in the design discussion: incumbents get fair credit for evidenced position, new-sector entrants get a fair (low but honest) read without punitive piling-on, and optimistic teams without evidence are appropriately disciplined.

#### 3.6.3 Why this v1 mechanism is honest

This is not Bayesian inference. It is transparent anchor-plus-adjustment composition with explicit maths. Anyone reading the composite can trace the headline number back to the layer values, and the decision (recorded here) is that **the data we have at v1 cannot support full Bayesian rigour without producing false precision**. A layered, transparent, well-documented composite is more honest at v1. v2 introduces explicit Bayesian updating once we have more confidence in the priors and once enough labelled outcomes exist to calibrate them.

---

## 4. Integration Architecture and Display

### 4.1 The default executive view

Rather than a single number splashed across the top, the executive view defaults to a layered display that shows how the answer was reached before showing the answer. The intended pattern:

```
PWIN  42%   Confidence: Medium
─────────────────────────────────────────────────
Historical pattern         35%         high confidence (47 comparable awards)
Qualify viability          On Track    medium confidence
                                       (4 of 5 categories Strong or On Track,
                                        1 Conditional — Stakeholder Position)
After cognitive discount   52%         3 of 8 subjective claims have evidence
Structural ceiling         50%         hard cap (new customer, current offering)

Trajectory  +7 points in 14 days, driven by buyer interaction
            logged 18 April 2026
```

Note the deliberate mix of representations. Layers that come from data (Historical Pattern, Cognitive Discount, Structural Ceiling) are shown as percentages because that is what they natively produce. The Qualify layer is shown as a five-band tier because that is what Qualify natively produces and discloses — the number that feeds the composite is computed under the hood and never displayed at the Qualify layer. The single PWIN headline (42%) exists for portfolio aggregation and the standard weighted pipeline value calculation. But it does not lead the disclosure. The layers do.

### 4.2 Why this solves executive scepticism

The well-documented phenomenon of executive distrust of single-number bid forecasts is not irrational — it reflects accumulated experience of being misled by confident scores from optimistic capture teams. The disclosure pattern proposed here addresses the root cause: the executive sees the components, the evidence behind them, and the structural reality, before the headline. This is the same pattern senior leaders trust in financial reporting (the bottom line is real, but the schedules are read first).

### 4.3 Confidence as a first-class output

Confidence is not a footnote. It is computed from:

- **Coverage** — how many layers have reported. If only Qualify has run, confidence is low. Full coverage (all five layers) raises confidence.
- **Recency** — how recently each layer was updated. Stale data lowers confidence.
- **Evidence ratio** — what fraction of subjective Qualify claims have backing evidence in Win Strategy.
- **Sample size for the historical pattern** — how many comparable historical awards inform the anchor. A specific buyer-scope-value combination with 47 comparable awards is high confidence; a niche slot with 6 comparable awards is low.

Confidence is presented on a banded scale (Low / Medium / High) in the executive view, with the underlying components available on demand.

### 4.4 Weighted pipeline value

For portfolio aggregation, the standard industry calculation applies:

**Weighted Pipeline Value = TCV × PGo × PWIN**

where PGo (Probability of Go — the chance the buyer actually issues, funds, and awards the procurement) is captured from Win Strategy's stage 2 (Buyer & Field Shaping) outputs. Today PGo is implicit; this design surfaces it as a first-class second probability alongside PWIN. The Portfolio Dashboard reads both and rolls them up.

---

## 5. Data Confidence Audit

This section catalogues honestly what the contracts data does and does not support, organised into three confidence bands. This catalogue is itself a feature of the design — most of the market sells confident numbers built on weaker foundations. PWIN's commercial differentiation rests partly on being explicit about its own confidence.

### 5.1 High confidence — concrete, supported by direct data

| Insight | Why it is high confidence |
|---|---|
| Award share within a defined scope (count and value) | Direct count and direct value from awards table; supported by canonical buyer and supplier master lists |
| Incumbency mapping | Who currently holds an expiring contract is recorded data |
| Buyer-supplier relationship strength | Direct count of awards from a buyer to a supplier (or its parent group via Companies House enrichment) over a defined period |
| Procurement route distribution | Recorded procurement method per notice |
| Framework holder identity | Direct data on who holds a parent framework |
| Contract value distributions by buyer and scope | Direct data, with the framework-ceiling caveat noted in §5.4 |

### 5.2 Medium confidence — informed inference

| Insight | Why confidence is medium |
|---|---|
| Likely competitor field for a given opportunity | Defensible in concentrated markets (BPO, defence, IT outsourcing) where the realistic bidder set is well-known. Weaker in fragmented markets |
| Competition density signals | Field is not consistently populated across all publishers; usable in aggregate, less reliable for individual opportunities |
| Win-share interpreted as win-rate | Win-share is direct data; treating it as "win rate" requires an assumption about which tenders the supplier bid on |
| Buyer behaviour patterns at high specificity | Strong at aggregate level, sample size collapses fast at narrow buyer × scope × value slices |

### 5.3 Low confidence — not derivable from the data

| Insight | Why we cannot claim it from this data alone |
|---|---|
| True win rate (wins ÷ bids submitted) | Losing bidders are not labelled in UK procurement data |
| Head-to-head outcomes against named competitors | Same problem |
| Reasons a particular bidder won | No evaluation data is published in machine-readable form |
| Forward predictions for unfamiliar buyer-scope combinations | Insufficient comparable history |
| Quality of winning bid features | No evaluation scoring is published |

### 5.4 Specific data caveats that flow into the score

- **Framework values are ceilings, not realised spend.** OCDS records the maximum the buyer is permitted to draw from a framework, not actual call-off volumes. Total-value rollups are flagged with a quality marker on egregious outliers (anything above £10bn is treated as a probable data error).
- **Companies House coverage is partial.** Roughly 27% of suppliers in the database carry a Companies House number on file. The remainder are publisher name-only entries, GB-PPON identifiers, non-UK suppliers, or public sector bodies. Group-level rollup via Companies House parent fields is therefore complete only on the enriched subset.
- **Canonical layer maturity.** Buyer canonical layer covers 70.3% of the £1m+ award universe (1,928 entities). Supplier canonical layer is at 82,637 canonical entities from 161,119 raw records. Both are mature enough for v1 scoring; further work on name-only supplier matching is deferred until v1 is validated against live dossier work.

---

## 6. Product Responsibilities

| Layer | Owning product | Data location | How it surfaces |
|---|---|---|---|
| Historical Pattern | Competitive Intel | SQLite (local), Cloudflare D1 (production, when re-prioritised) | New MCP tool to be added: `get_pwin_historical_anchor` |
| Qualify Assessment | Qualify | `qualify.json` per pursuit (existing platform pattern) | Existing MCP tools, with output schema updated to remove single PWIN claim |
| Capture Evidence | Win Strategy | `win_strategy.json` per pursuit | New MCP tool to be added: `get_evidence_index` (returns evidence-claim mapping) |
| Cognitive Discount | Platform | Computed at platform level | New platform-level computation, not owned by any single product |
| Structural Ceiling | Platform | Derived from opportunity metadata in `shared.json` | New platform-level computation |
| Integrated PWIN | Platform | Computed and cached per pursuit | New MCP tool: `get_pwin_score` (replaces Qualify's score-as-output role) |
| Confidence Indicator | Platform | Computed alongside PWIN | Bundled with `get_pwin_score` output |
| PGo (Probability of Go) | Win Strategy | `win_strategy.json` per pursuit | New MCP tool: `get_pgo_assessment` |
| Weighted Pipeline Value | Portfolio | Computed from TCV × PGo × PWIN | Surfaced in the Portfolio Dashboard |

---

## 7. Sequenced Roadmap

The roadmap is sequenced so that **each version stands alone commercially**. None depends on a later version being delivered to be valuable.

### 7.1 v1 — Honest descriptive analytics + layered surface (months)

**What ships:**

- Qualify outputs change to remove the single PWIN claim. Qualify produces per-category viability tiers across five categories on the five-band scale (Strong / On Track / Conditional / Major Concerns / Walk Away), each with rationale, recommendations, evidence, and confidence — plus a headline pursuit viability tier and the qualification coaching layer that fires on Conditional or worse. The numerical category score that feeds the platform composite is computed but not displayed.
- Historical Pattern layer ships with descriptive analytics: award shares, incumbency strength, buyer-supplier relationship strength, procurement route distribution. No ML.
- Cognitive Discount Factor ships in basic form: subjective category claims attract a default haircut unless evidence exists in Win Strategy.
- Structural Ceiling ships at full strength (SMA quadrants + Shipley recompete cap). This is a small mechanism that delivers brutal honesty.
- The layered executive display ships as the default view.
- Confidence indicator ships as Low / Medium / High based on coverage, recency, evidence ratio, and historical sample size.
- PGo separation ships at platform level, populated from Win Strategy stage 2 outputs (or marked unknown).
- The competitive positioning is refreshed (Section 8).

**Commercial proposition at v1:** "The only multi-layered probability engine in UK public sector procurement, with disclosed confidence and evidence-grounded discipline. We run the algorithm, we run the judgement layer, we run the evidence validation, and we are explicit about what we do and do not know."

**What v1 does *not* claim:**

- ML-powered prediction
- Continuous Bayesian updating (the maths is layered composition, not formal Bayesian inference)
- True win-rate calibration (we have win-share, not win-rate)

### 7.2 v2 — Continuous Bayesian updating + capture-driven re-scoring (months later)

**What v2 adds:**

- The integration mechanism upgrades from layered composition to formal Bayesian updating. Each new input (a logged buyer interaction, a competitor field map update, a Qualify re-run) produces an explicit prior-to-posterior shift the executive can see and reason about.
- Trajectory presentation in the executive view ("the score moved from 47% to 62% over the last fortnight, driven by …").
- The Cognitive Discount mechanism gets more refined — evidence weight and decay are properly modelled.
- Win Strategy artefact ingestion is automated rather than periodic.

**Commercial proposition at v2:** "PWIN is a live, dynamic probability that responds to capture intelligence as it arrives. Not a periodic snapshot — a continuously calibrated reading of the pursuit."

### 7.3 v3 — True predictive classifier (year+ out)

**What v3 adds:**

- A trained ML classifier (likely Random Forest or gradient boosting) replaces the descriptive Historical Pattern layer with a true predictive component, using PWIN's accumulated labelled pursuit history as the primary training set, augmented by the contracts data as feature engineering.
- Calibration of PWIN scores against actual outcomes — does a 65% PWIN actually correspond to a 65% win frequency in the historical record?
- Sector-specific specialisation (UK Social Value modifier maturity, defence-specific overlays, etc.).

**Commercial proposition at v3:** "Calibrated predictive intelligence trained on PWIN's own pursuit history — a moat no competitor can replicate."

**Pre-condition for starting v3:** PWIN has accumulated approximately 100 labelled pursuits (won/lost) with rich feature data (Qualify scores, Win Strategy artefacts, contracts data context). Until that pre-condition is met, attempting v3 produces a model trained on too few examples and over-claims accuracy.

### 7.4 Discrete features that can ship in any version

- **UK Social Value modifier** — a sector-specific structural overlay following the same modifier mechanism as the incumbent rebid layer. Activates for UK central government tenders. Adds dedicated questions and weight (10–30% per government policy). Ships when convenient; not gated on v1/v2/v3.
- **Price-to-Win estimation** — uses contracts data to estimate competitor pricing positions in scope. Useful at any version. Naturally a Win Strategy capability.

---

## 8. Refreshed Competitive Positioning

The previous competitive analysis positioned BidEquity as the strategic advisory layer "above the algorithm." That framing is now retired. The refreshed positioning:

> **PWIN: the only multi-layered probability engine for UK public sector procurement.**
>
> One integrated score, drawn from real procurement history, the team's structured assessment, capture evidence accumulated through the bid window, mathematically applied bias correction, and the structural reality of the market. UK-native. Confidence-graded. Transparent by default.

### 8.1 Where this positions PWIN against the field

| Dimension | Cleat.ai (US GovCon) | pWin.ai / TechnoMile (US GovCon) | PWIN (UK public sector) |
|---|---|---|---|
| Score architecture | Single weighted scorecard | Single weighted scorecard, Shipley-shaped | Multi-layered composite with explicit components |
| Historical data layer | Implicit (relies on user CRM) | Implicit (relies on user CRM) | Native — 175k UK contracts, 5+ years, master-listed buyers and suppliers |
| Bias correction discipline | None | None | Cognitive Discount Factor with evidence linkage |
| Structural ceiling | None | Shipley caps mentioned, not enforced | Explicit SMA quadrant + Shipley caps enforced |
| Confidence as output | No | No | First-class — every score carries banded confidence |
| Capture evidence linkage | No equivalent product | No equivalent product | Win Strategy artefacts feed PWIN directly |
| UK regulatory context | None | None | Procurement Act 2023, Social Value model, UK frameworks |
| Market | US federal | US federal | UK public sector |

### 8.2 The defensibility argument

Most competitors in this space are scoring tools. They lack the capture intelligence layer (no Win Strategy equivalent), the historical data layer (no UK contracts database), or the structural discipline (no enforced ceilings, no evidence-grounded discount mechanism). PWIN's moat is that all five layers are owned, integrated, and presented as one experience. A competitor would need to build multiple products and connect them to replicate this — not a feature parity exercise.

### 8.3 The commercial story

"Strategic suppliers in the UK public sector spend roughly £3bn a year on bid pursuit. By industry estimate, around £2bn of that spend goes on opportunities the bidders were never going to win. The cost of this waste is not just the bid budgets — it is the opportunity cost of capture teams chasing the wrong things, the reputational drag of repeated losses, and the executive credibility lost when over-confident PWIN scores prove unfounded.

The cause of the waste is well-documented. Existing PWIN methodologies are either too subjective (vulnerable to over-scoring driven by sales optimism — the Happy Ears phenomenon) or too academic (impractical at the speed of decision-making). No methodology in market combines algorithmic discipline, capture evidence, structural reality, and bias correction in one system.

PWIN is that system. It is the multi-layered probability engine designed to allocate the £3bn intelligently — and to recover the £2bn currently being wasted."

---

## 9. Open Questions and Decisions Deferred

The following are explicitly *not* locked in by this design and are deferred to implementation planning or future spec work.

1. ~~**Default Cognitive Discount Factor percentage.**~~ **Resolved (2026-04-25).** A flat haircut was rejected because it punishes new-sector entry as if it were inflation. The CDF is now stage-aware (0% / 5% / 15% / 20% across Identify / Capture / Pursue / Submit), claim-type-aware (acts only on evidence-bearing categories, not strategic-fit categories), and explicitly does not double-count the Historical Pattern layer. See §3.4. The four stage percentages and the evidence-bearing/strategic-fit category split remain subject to calibration against labelled outcomes.

2. ~~**Layer weights in the composite formula.**~~ **Resolved (2026-04-25).** v1 uses anchor + bounded adjustment, not a weighted average: the Historical Pattern is the anchor, the adjusted Qualify shifts it by up to ±15 percentage points based on how the team's view differs from the neutral midpoint. See §3.6.1. The ±15 bound is the v1 default and is a tunable parameter to be re-calibrated once ~50 labelled pursuit outcomes exist.

3. **Confidence band thresholds.** The Low / Medium / High confidence indicator needs explicit thresholds against the four contributing factors (coverage, recency, evidence ratio, sample size).

4. **Where the design document lives long-term.** Saved at the brainstorming default location; possibly should move to `pwin-platform/docs/architecture/` as a platform architecture document. Decision deferred to user preference.

5. **Migration path for existing Qualify outputs.** Pursuits that already have a Qualify-produced PWIN score need a migration policy. Options: re-score under the new architecture, mark as "v0 score, not comparable," or freeze and display alongside the new score. Implementation choice.

6. **Display of the Bayesian update trajectory in v2.** This design commits to showing trajectory but does not specify the visualisation. Frontend design work for v2.

7. **PGo elicitation mechanics.** PGo lives in Win Strategy stage 2 outputs, but the mechanics of how the consultant elicits and calibrates a PGo number are out of scope for this document and need a separate Win Strategy spec.

8. **Social Value modifier scope.** The design notes the Social Value modifier as a discrete feature that can ship in any version. The exact question pack, weighting integration, and trigger conditions need a separate spec.

9. **The "true win rate" claim and external messaging.** The data confidence audit in §5 is honest about what we can and cannot derive. Marketing materials and the website Qualify experience must not over-claim. A messaging review is needed before any public launch claim that uses PWIN's confidence-graded scoring as a differentiator.

10. **Qualify's standalone consulting use case.** The consulting standalone HTML app that ships to consultants on laptops cannot access platform-level PWIN computation when offline — but this is no longer a problem on the new framing. Qualify's job is the viability assessment, the coaching layer, and the disclosed tier output, none of which depend on the platform PWIN composite. The standalone runs the full Qualify experience offline; the platform PWIN composite simply doesn't surface in standalone mode. Implementation: confirm the offline build does not attempt to read or display platform PWIN.

---

## 10. Glossary

For non-technical readers, the terms used in this document mean:

| Term | What it means in plain English |
|---|---|
| Bayesian updating | A statistical method that takes a starting belief and refines it as new evidence arrives. Useful here because capture intelligence accumulates over months and the score should respond. |
| Capture phase | The four-to-five month window before a formal tender is issued, during which a supplier shapes the buyer's thinking and gathers intelligence. |
| Cognitive Discount Factor (CDF) | The mechanism that mathematically reduces the impact of subjective scores on the final number unless evidence backs them up. |
| Composite score | A single number built from multiple separate inputs, each contributing a known share. |
| Confidence indicator | A graded label (Low / Medium / High) that tells the reader how much weight the score can bear, based on how complete and recent the inputs are. |
| Evidence ratio | What proportion of the team's subjective claims are backed by logged artefacts (interactions, agreements, documented activity). |
| PGo (Probability of Go) | The probability that the buyer actually issues the tender, secures the funding, and makes an award. Independent of how likely the supplier is to win. |
| PWIN | Probability of Winning. The probability that the bidder is awarded the contract, assuming the procurement happens. |
| Structural ceiling | A hard upper limit on the score based on the opportunity's market position (existing customer vs new customer, existing offering vs new offering). |
| TCV (Total Contract Value) | The full value of the contract over its lifetime. |
| Weighted Pipeline Value | TCV × PGo × PWIN. The risk-adjusted value of an opportunity in the pipeline. |

---

## 11. References

Source material informing this design:

- The CAB-PWIN methodology synthesis published in market thought leadership (Contextual Algorithmic-Behavioural framework — historical baseline, structural ceilings, Bayesian updating, Cognitive Discount Factor)
- SMA Threshold Matrix (quadrant-based PWIN ceilings)
- Shipley Associates methodology (recompete cap, customer-perspective assessment, color team reviews)
- Competitive analysis: Cleat.ai (CLEATUS), pWin.ai, TechnoMile — US GovCon platforms (`pwin-competitive-analysis-v1.md`, 25 April 2026)
- PWIN Qualify functional design (`pwin-qualify/docs/PWIN-Qualify-Design v1.html`)
- PWIN Qualify content system (`pwin-qualify/content/qualify-content-v0.2.json`)
- PWIN Win Strategy plugin architecture (`pwin-platform/docs/architecture/pwin_architect_plugin_architecture.md`)
- PWIN Competitive Intel database design (`pwin-competitive-intel/CANONICAL-LAYER-DESIGN.md`, schema, query layer)
- PWIN repository CLAUDE.md — architecture decision framework

---

*End of design document.*
