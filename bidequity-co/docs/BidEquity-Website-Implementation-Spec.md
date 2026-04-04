# BidEquity Website — Implementation Spec

**Date:** 4 April 2026
**Scope:** Two workstreams to be applied to the live site at bidequity.co.
**Workstream A:** Methodology reframing — replacing "methodology" language across the site.
**Workstream B:** BidEquity Verdict — adding the third product tier.

This spec was written after reviewing the live site on 4 April 2026. All "Current" copy below is verbatim from the published pages. Nothing in this spec duplicates changes that have already been applied.

The site is a static HTML/CSS site with no build tools or frameworks.

---

## Brand Rules (apply to all changes)

- UK English spelling throughout (organisation, programme, colour)
- No exclamation marks
- Fonts: Spline Sans for headings, Inter for body, JetBrains Mono for monospace labels
- Colour palette only: Midnight Navy (#021744), Soft Sand (#F7F4EE), Calm Teal (#3D7A8A on sand, #5CA3B6 on dark), Pale Aqua (#E0F4F6), Bright Aqua (#7ADDE2), Coral (#C96F5A), Wine (#8C3B36)
- Soft Sand is the page canvas. White (#FFFFFF) is used only for card/panel backgrounds.

---

# WORKSTREAM A — METHODOLOGY REFRAMING

## The Rule

**Do not use "methodology" in headlines, taglines, card titles, section headers, or lead sentences.** The word is permitted only in:
- Technical depth on the About page (describing what the platform contains)
- The phrase "scoring methodology" when referring to a contracting authority's evaluation approach

**Substitution table:**

| Instead of | Use |
|---|---|
| Methodology-led | Experience-encoded |
| Our methodology | Our platform / our approach / what we have built |
| Structured methodology | Practitioner experience encoded into a platform |
| Methodology and platform | Experience and platform / platform-driven capability |
| A proprietary methodology | Two decades of pursuit execution, encoded |
| The methodology determines what needs to be done | The platform encodes what needs to be done |
| Encoded Methodology | Encoded Experience |

---

## File: `index.html` (Homepage)

### A1. Tagline strip

**Current:** `Methodology-led · Platform-enabled · Outcome-aligned`

**Replace with:** `Experience-encoded · Platform-driven · Outcome-aligned`

This appears in the hero section, likely as a `.mono` or small-caps text element immediately above or below the headline.

---

### A2. "Compress Cost of Sale" proof card

**Current:**
> Methodology and platform working together to structurally reduce what it costs to produce a competitive submission.

**Replace with:**
> An AI-enabled platform that structurally reduces what it costs to produce a competitive submission. Not incremental. Structural.

---

### A3. "Encoded Methodology" differentiator card

**Current card title:** `Encoded Methodology`

**Current card body:**
> Two decades of complex programme acquisition encoded into specific activities, dependencies, and decision points. Not generic frameworks. The methodology that determines outcome.

**Replace card title with:** `Encoded Experience`

**Replace card body with:**
> Two decades of personally executing complex programme pursuits — encoded into a platform that knows which activities drive win probability, which dependencies cause failure, and where effort is wasted.

---

### A4. In-practice vignette in differentiators section

**Current (contains one methodology reference):**
> ...We deployed the methodology on day one — dependency-mapped the critical path...

**Replace with:**
> ...We deployed the platform on day one — dependency-mapped the critical path...

---

## File: `about.html` (About page)

### A5. "How we work" section heading

**Current:**
> AI-enabled methodology. Human-assured judgement.

**Replace with:**
> AI-enabled platform. Human-assured judgement.

---

### A6. "How we work" body paragraph

**Current:**
> The methodology determines what needs to be done. The platform absorbs the repetitive, structured work so that the team's time is concentrated on the judgements that determine outcome: win strategy, pricing, competitive differentiation, and submission quality.

**Replace with:**
> The platform encodes what needs to be done and absorbs the heavy lifting — governance documentation, compliance assembly, review coordination. Senior people spend their time on the judgements that determine outcome: win strategy, pricing, competitive differentiation, and submission quality.

---

### A7. Pillar strip — three labels

**Current labels:**
- `Methodology-led` — Calibrated effort models, dependency maps, and archetype configurations built from real pursuit experience — not theory.
- `Platform-enabled` — Technology that amplifies the methodology — automating structured activities, surfacing patterns, and compressing the effort required to compete.
- `Outcome-aligned` — Our fees are contingent on contract award. We share the risk and the conviction.

**Replace with:**
- `Experience-encoded` — Two decades of pursuit execution — encoded into a platform that knows which activities drive win probability and where effort is wasted.
- `Platform-driven` — AI-enabled technology that absorbs the heavy lifting, accelerates decisions, and gives senior people their time back to focus on what moves the score.
- `Outcome-aligned` — Our fees are contingent on contract award. We share the risk and the conviction. *(No change to this one.)*

---

### A8. In-practice vignette

**Current:**
> The third attempt used a single integrated methodology from qualification through submission.

**Replace with:**
> The third attempt used a single integrated approach from qualification through submission.

---

### A9. "Methodology and platform, together."

**Current (appears as a standalone line after the pillar strip or in-practice section):**
> Methodology and platform, together.

**Replace with:**
> Experience and platform, together.

---

### A10. Paid on Award — "scoring methodology" reference

**Current:**
> We qualify the opportunity together using our scoring methodology.

**Replace with:**
> We qualify the opportunity together using our scoring framework.

Note: "scoring methodology" here refers to BidEquity's own approach, not a contracting authority's evaluation methodology, so it should be replaced.

---

### A11. "What we are not" section — methodology reference

**Current (in the BidEquity summary line at the end of the disruption section):**
> BidEquity operates across all three dimensions — methodology, technology, and commercial alignment — and breaks the pattern on each.

**Replace with:**
> BidEquity operates across all three dimensions — practitioner experience, AI-enabled platform, and commercial alignment — and breaks the pattern on each.

---

## File: `services.html` (Services page)

### A12. Page hero subheading

**Current:**
> Structured methodology across the full pursuit lifecycle.

**Replace with:**
> Structured pursuit capability across the full lifecycle.

---

### A13. Pursuit lifecycle section heading

**Current:**
> Four capability areas. One integrated methodology.

**Replace with:**
> Four capability areas. One integrated platform.

---

### A14. Pursuit lifecycle section intro paragraph

**Current:**
> Our methodology spans the full pursuit lifecycle — from the decision to compete through to post-outcome learning. Each capability area is structured, repeatable, and governed by data.

**Replace with:**
> Our platform spans the full pursuit lifecycle — from the decision to compete through to post-outcome learning. Each capability area is structured, repeatable, and governed by data.

---

### A15. Cost advantage section heading and body

**Current heading/body:**
> The combination of structured methodology and AI-enabled capability delivers a step change in what it costs to compete.

**Replace with:**
> The combination of practitioner experience and AI-enabled capability delivers a step change in what it costs to compete.

---

### A16. Cost advantage — "Methodology" callout

**Current callout label:** `Methodology.`
**Current callout body:**
> Calibrated effort models and dependency maps that eliminate guesswork and rework.

**Replace callout label with:** `Experience.`
**Replace callout body with:**
> Effort models and dependency maps built from real pursuit execution — eliminating guesswork and rework.

---

## File: `qualify.html` (Qualify page)

No methodology changes needed. The page does not contain "methodology" in its current live copy.

---

## File: `contact.html` (Contact page)

No methodology changes needed. The page does not contain "methodology" in its current live copy.

---

## File: `styles.css`

No methodology-related CSS changes. The reframing is copy-only.

---

## Footer (all pages)

If the tagline "Methodology-led · Platform-enabled · Outcome-aligned" appears in the site footer, replace with "Experience-encoded · Platform-driven · Outcome-aligned". Check the footer template/HTML that is shared across all pages.

---

# WORKSTREAM B — BIDEQUITY VERDICT

## Product Summary

BidEquity Verdict is a forensic post-loss bid review. The client provides procurement documentation, their submitted proposal, and any authority feedback. BidEquity's platform independently scores and reviews. Includes a structured consultative debrief.

**Two pricing tiers:**
- **Verdict Single** — £2,000 fixed fee. One pursuit, one forensic review, one consultative debrief.
- **Verdict Portfolio** — £5,000 fixed fee. Three pursuits reviewed, plus cross-pursuit pattern analysis.

**Commercial model:** Fixed fee, paid per engagement. Deliberately different from the Paid on Award model used by Core and Command.

**Strategic role:** Entry point into the BidEquity ecosystem. Low commitment, high value. Multiple Verdicts reveal organisational patterns that feed into Core/Command watch lists.

---

## File: `services.html`

### B1. Update the engagement tiers section intro

Find the section containing "Choose the depth of engagement." and the paragraph beginning "Both tiers are anchored to the Paid on Award model."

**Replace the heading and intro paragraph with:**

```html
<p class="mono color-teal mb-16">Engagement tiers</p>
<h2>Choose the depth of engagement.</h2>
<div class="divider divider--coral"></div>
<p class="text-center-intro">
  Three engagement models. Verdict is transactional — a fixed-fee forensic review of a lost pursuit, from £2,000. Core and Command are outcome-aligned — fees contingent on contract award. Choose the depth your bid operation needs.
</p>
```

---

### B2. Insert Verdict tier card — convert grid to 3 columns

Find the `.tier-grid` container that holds the two existing tier cards (BidEquity Core and BidEquity Command).

**Insert the following Verdict card as the FIRST child of `.tier-grid`, before the Core card:**

```html
<div class="tier-card tier-card--verdict">
  <div class="tier-card__label">Forensic post-loss review</div>
  <h3>BidEquity Verdict</h3>
  <span class="poa-badge poa-badge--verdict">Fixed Fee · Per Pursuit</span>
  <p>You lost a strategic bid. We tell you why — independently, forensically, and without the biases that compromise internal reviews. Platform-scored analysis, win strategy assessment, and a structured debrief that converts a loss into intelligence for the next pursuit.</p>

  <div class="verdict-tiers">
    <div class="verdict-tier">
      <p class="verdict-tier__name">Verdict Single</p>
      <p class="verdict-tier__price">£2,000</p>
      <p class="verdict-tier__desc">Forensic review of a single lost pursuit with consultative debrief.</p>
    </div>
    <div class="verdict-tier">
      <p class="verdict-tier__name">Verdict Portfolio</p>
      <p class="verdict-tier__price">£5,000</p>
      <p class="verdict-tier__desc">Three pursuits reviewed, plus cross-pursuit pattern analysis.</p>
    </div>
  </div>

  <ul>
    <li>Independent proposal scoring against evaluation criteria</li>
    <li>Win strategy and positioning assessment</li>
    <li>Governance and structural failure analysis</li>
    <li>Prioritised recommendations for next pursuit</li>
    <li>Structured consultative debrief</li>
    <li>Cross-pursuit pattern analysis (Portfolio)</li>
  </ul>
</div>
```

---

### B3. Update bottom CTA to reference Verdict

Find the CTA section at the bottom of the page (the dark section containing "See how the model works for your situation.").

**Replace with:**

```html
<section class="section section--dark cta-strip text-center">
  <div class="container">
    <h2>See how the model works for your situation.</h2>
    <p class="cta-strip__sub">Start with a Verdict on a recent loss, or qualify your next live pursuit.</p>
    <div class="cta-strip__buttons">
      <a href="contact.html" class="hero__cta">Request a Verdict</a>
      <a href="qualify.html" class="hero__cta hero__cta--outline">Qualify a Pursuit</a>
    </div>
  </div>
</section>
```

---

### B4. Update JSON-LD structured data in `services.html`

If `services.html` has a `<script type="application/ld+json">` block with a service listing, add Verdict as an additional service entry following the same pattern as Core and Command:

```json
{
  "@type": "Offer",
  "itemOffered": {
    "@type": "Service",
    "name": "BidEquity Verdict",
    "description": "Forensic post-loss review — independent platform-scored analysis, win strategy assessment, and consultative debrief. Fixed fee from £2,000."
  }
}
```

---

## File: `styles.css`

### B5. Update `.tier-grid` to 3 columns

Find the existing `.tier-grid` rule and change it:

```css
/* REPLACE existing .tier-grid rule */
.tier-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; margin-top: 48px; }

/* REPLACE existing mobile breakpoint for .tier-grid */
@media (max-width: 768px) {
  .tier-grid { grid-template-columns: 1fr; }
}
```

---

### B6. Add Verdict-specific styles

Add the following new CSS rules after the existing `.tier-card` rules:

```css
/* ─── VERDICT TIER CARD ─── */
.tier-card--verdict { border-top: 4px solid var(--bright-aqua); }

.poa-badge--verdict {
  color: var(--bright-aqua);
  border-color: var(--bright-aqua);
}

/* ─── VERDICT PRICING TIERS (inside card) ─── */
.verdict-tiers {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  margin: 20px 0;
  padding: 20px 0;
  border-top: 1px solid var(--pale-aqua);
  border-bottom: 1px solid var(--pale-aqua);
}
.verdict-tier { text-align: center; }
.verdict-tier__name {
  font-family: var(--font-mono); font-size: 0.7rem;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--teal); margin-bottom: 4px;
}
.verdict-tier__price {
  font-family: var(--font-heading); font-weight: 700;
  font-size: 1.6rem; color: var(--navy); line-height: 1.2;
  margin-bottom: 4px;
}
.verdict-tier__desc {
  font-size: 0.8rem; color: #2A3B5C; opacity: 0.8;
  max-width: none;
}

@media (max-width: 480px) {
  .verdict-tiers { grid-template-columns: 1fr; }
}

/* ─── CTA BUTTON PAIR ─── */
.cta-strip__buttons {
  display: flex; gap: 16px; justify-content: center;
  flex-wrap: wrap;
}
.hero__cta--outline {
  background: transparent;
  border: 2px solid var(--coral);
  color: var(--sand);
}
.hero__cta--outline:hover,
.hero__cta--outline:focus-visible {
  background: var(--coral); color: var(--sand);
}
```

---

## File: `index.html` (Homepage)

### B7. Add Verdict reference in Paid on Award section

Find the section containing the heading "Paid on Award" and the paragraph "Our remuneration is mathematically tethered to your success."

**Add the following line after that paragraph, before the "Explore Our Services" CTA:**

```html
<p class="mt-24 text-sand-muted" style="font-size: 0.95rem;">
  Not ready for an outcome-aligned engagement? Start with <a href="services.html" class="link-coral">BidEquity Verdict</a> — a fixed-fee forensic review of a recent loss. From £2,000.
</p>
```

---

### B8. Update JSON-LD structured data in `index.html`

Find the `<script type="application/ld+json">` block in the `<head>` of `index.html`. In the `hasOfferCatalog.itemListElement` array, add the following as the FIRST item (before Core and Command):

```json
{
  "@type": "Offer",
  "itemOffered": {
    "@type": "Service",
    "name": "BidEquity Verdict",
    "description": "Forensic post-loss review — independent platform-scored analysis, win strategy assessment, and consultative debrief. Fixed fee from £2,000."
  }
}
```

---

## File: `about.html`

### B9. Add Verdict reference in CTA section

Find the CTA at the bottom of the page ("Talk to us about a pursuit" or "Start a Conversation"). Add a secondary line beneath the CTA button:

```html
<p class="mt-24 text-muted" style="font-size: 0.9rem;">
  Lost a recent bid? <a href="services.html" class="link-coral">BidEquity Verdict</a> provides an independent forensic review — from £2,000.
</p>
```

---

## File: `contact.html`

### B10. Add Verdict as a subject option in the contact form

Find the `<select>` element for the "Subject" field. The current options are:

```
Discuss a live pursuit
Understand the Paid on Award model
Pipeline review or qualification
General enquiry
```

**Add the following option as the second item in the list (after "Discuss a live pursuit"):**

```html
<option value="request-verdict">Request a Verdict — post-loss review</option>
```

---

## File: `qualify.html`

No changes needed. The qualify page is for live pursuits; Verdict is for lost pursuits. Keep these pathways distinct.

---

# IMPLEMENTATION ORDER

1. **`styles.css`** — Changes B5, B6 (Verdict CSS). No methodology CSS changes needed.
2. **`index.html`** — Changes A1, A2, A3, A4 (methodology reframing), then B7, B8 (Verdict references).
3. **`about.html`** — Changes A5, A6, A7, A8, A9, A10, A11 (methodology reframing), then B9 (Verdict reference).
4. **`services.html`** — Changes A12, A13, A14, A15, A16 (methodology reframing), then B1, B2, B3, B4 (Verdict tier card and CTA).
5. **`contact.html`** — Change B10 (Verdict subject option).
6. **Footer (all pages)** — Check for tagline in footer and update per A1 if present.
7. **Verify** — Open each page in a browser. Confirm:
   - "Methodology" does not appear in any headline, tagline, card title, section header, or lead sentence
   - The three-column tier grid renders correctly on desktop
   - The tier grid collapses to single-column below 768px
   - All internal links work
   - The contact form subject dropdown includes the Verdict option
   - JSON-LD includes Verdict as a service

---

# CHANGE SUMMARY

| File | Methodology changes | Verdict changes | Total |
|------|---|---|---|
| `index.html` | A1, A2, A3, A4 | B7, B8 | 6 |
| `about.html` | A5, A6, A7, A8, A9, A10, A11 | B9 | 8 |
| `services.html` | A12, A13, A14, A15, A16 | B1, B2, B3, B4 | 9 |
| `contact.html` | — | B10 | 1 |
| `styles.css` | — | B5, B6 | 2 |
| `qualify.html` | — | — | 0 |
| Footer (all) | A1 (if present) | — | 1 |
| **Total** | **16** | **10** | **27** |
