# PGO Factor Model — design companion to buyer-behaviour analytics v1

**Status:** design layer above the v1 build.
**Date:** 2026-04-27.
**Companion to:** `buyer-behaviour-analytics-v1.md`.

## 1. Why this exists

PGO — short for **Probability of Going Out** — is the empirical answer to a question every bid director asks: *if a buyer says they intend to tender something, what's the realistic chance it actually goes to market and reaches an award?*

Today that number is consultant judgement. The buyer-behaviour module that just shipped gives us the raw signal — five years of how this buyer has actually behaved across the UK government's contract notices and the lower-value contract feed. This document explains how those signals combine into a single calibrated PGO number per pursuit, and why we've chosen to build it the way we have.

## 2. PGO is a failure-mode decomposition, not a single percentage

The temptation is to express PGO as one number — "73% likely to go out". That hides what matters. A buyer reaches a 73% PGO for very different reasons: one is slow and indecisive, another is decisive but cancels late, a third has a financially distressed incumbent forcing a re-procurement they hadn't planned. Treating these as the same number is dishonest.

So PGO is built as a **decomposition by failure mode**. We name the ways a tender can fail to reach award and we estimate the probability of each. The named modes are:

**Observable in our database:**
- **Explicit cancellation.** The buyer publishes, then formally pulls the tender.
- **No compliant bid.** The buyer publishes and runs the process, but no bidder meets the threshold.
- **Dormant past category benchmark.** The buyer publishes, then nothing happens — no award, no cancellation — for longer than the slowest 5% of tenders in that category. Effectively dead.

**External or judgement-based:**
- **Policy refocus.** A change in departmental priority kills the procurement before publication.
- **Insourcing decision.** The buyer decides to do it in-house instead.
- **Budget cut mid-process.** Money disappears between announcement and award.
- **Legal challenge.** A bidder challenges the process and the buyer withdraws or restarts.
- **Award-stage withdrawal.** The process completes but the buyer doesn't sign.

A consultant reading the output sees not just *"PGO is 64%"* but *"PGO is 64%, and the dominant risk is dormant-past-benchmark, not cancellation"*. That tells the bid team what to watch for and what mitigations matter.

## 3. The three-tier factor model

The factors that drive PGO sit in three tiers, organised by how we get the data.

### Tier 1 — observable in our database

These are the six factors the v1 buyer-behaviour module produces directly:

- **Historical cancellation rate by buyer × category** — from the outcome-mix section of the buyer profile.
- **Schedule adherence** — planned versus actual timelines, drawn from the notice-to-award timeline distribution.
- **Competition intensity** — average bid count per tender, from the competition-intensity section.
- **Amendment behaviour** — the indecision signal, from the amendment-behaviour section.
- **Outcome mix patterns** — the four-bucket split (awarded / cancelled / no compliant bid / dormant) that the profile reports as a headline.
- **Incumbent distress** — supplied by the Companies House flag in the v1 module, surfacing buyers whose current contract-holder is in liquidation or being struck off.

### Tier 2 — observable from external public data

These six factors are visible to anyone with a browser, but they're not in our database yet. They need bringing in:

- **The government's Major Projects Portfolio** — the Infrastructure and Projects Authority publishes a delivery-confidence rating (red/amber/green) for every major government project annually.
- **Council section 114 notices** — when a local authority effectively declares it cannot balance its budget, published on the Department for Levelling Up, Housing and Communities register.
- **NHS trust deficit positions** — published quarterly by NHS England, showing which trusts are in the worst financial trouble.
- **Cabinet Office commercial pipeline** — the rolling list of upcoming central-government procurements published by the Crown Commercial Service.
- **Departmental business plans and Spending Review allocations** — published by HM Treasury and individual departments, showing where money is going to land.
- **National Audit Office and Public Accounts Committee reports** — public audits that flag procurement competence and risk.

### Tier 3 — structured judgement

The remaining four factors are not in any feed and never will be. They sit with the consultant:

- **Strategic fit with departmental priorities** — does this procurement actually advance what ministers say they want?
- **Procurement capability** — does the buyer's commercial team have the people and skills to actually run this?
- **Business case gate status (where not public)** — has the procurement passed its internal funding gates?
- **Political and ministerial risk** — could a reshuffle, a manifesto change, or a single news story kill it?

## 4. The combination model

The three tiers combine as:

> **PGO = base rate (Tier 1) × observable modifier (Tier 2) × judgement overlay (Tier 3)**

In plain English: **Tier 1 anchors the number** in what the buyer has actually done over the last five years. **Tier 2 nudges that number** up or down for external signals visible to anyone looking — a council that just issued a section 114 notice will cancel more procurements than its history suggests. **Tier 3 is where consultant judgement adds value** — the human read on political risk, capability, and gate status that no feed will ever capture.

This ordering matters. If the consultant's judgement is the only input, PGO is a guess. If only the database speaks, PGO misses obvious external warning signs. The model forces all three voices into the answer and makes each one's contribution visible.

## 5. PGO and PWIN have asymmetric precision

PGO and PWIN — your win probability if the tender goes out — behave very differently across the life of a pursuit.

- **Early in capture**, PGO is **trustworthy** (anchored in five years of history) and PWIN is **largely guesswork** (no published requirements, no scoring scheme, limited intelligence).
- **Late in capture**, PGO becomes **residual** (most of the failure modes have already played out — the tender is published, evaluated, near award) and PWIN becomes **well-evidenced** (you know the requirements, you've seen the questions, you have a feel for the competition).

The practical rule: **lead with PGO early in capture, lead with PWIN late in capture.** This is why we never show their product alone — multiplying two numbers of asymmetric precision throws away the diagnostic value of each.

## 6. Forward-looking ROI versus total ROI

At every stage gate the question is *"is the remaining spend worth the current expected return?"* — not *"was the total worth it?"*. By the late stages of a bid, sunk cost dominates and only PWIN matters. Total ROI is a Verdict measure — the post-loss forensic look-back. Forward-looking ROI is the live decision tool.

## 7. What's built today versus what's next

**Built today.** The buyer-behaviour v1 module produces all six Tier 1 inputs and gives the consultant a single PGO summary line they can lift straight into a Win Strategy document.

**Not yet built.** Tier 2 external overlays — the strongest single predictor of cancellation for councils and NHS trusts, and the highest-value next addition. Tier 3 structured judgement framework — a guided way for the consultant to record and apply their overlay rather than doing it freehand. The Phase 2 work order is in `actions.v2_phase_2` of the session handoff.
