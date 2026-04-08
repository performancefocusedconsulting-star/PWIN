# Bid Equity — Brand Guidelines v1.2

> **Status:** Canonical. This document and `brand-tokens.css` are the only sources of truth for the Bid Equity brand. Any deviation in product code is a bug.
>
> **PDF master:** matching PDF lives alongside this file (`brand-guidelines-v1.2.pdf`). The PDF is the visual master; this markdown is the developer-facing copy and is kept in sync with it.
>
> **Date:** 26 March 2026 (v1.2)
>
> **Replaces:** `brand-design-system.md` (deprecated — see stub).

---

## How to use this document

If you are writing or editing any HTML/CSS in this repo:

1. **Reference `brand-tokens.css`** with `<link rel="stylesheet" href="brand-tokens.css">` (or relative path). Never redefine the canonical token values.
2. **Use the semantic role tokens** (`--be-text-primary`, `--be-bg-page`, `--be-accent-cta`, `--be-font-display` etc.) — not the colour primitives directly.
3. **If a UI element doesn't have a token role, do not invent a hex value.** Either pick an existing token or come back here and add a semantic token first.

---

## 1. Naming conventions

| Context | Form | Example |
|---|---|---|
| **Logo / wordmark** (the visual brand mark in nav, footer, logo lock-ups) | **Two words**, capital B, capital E | "Bid Equity" |
| **Everywhere else** (page titles, body copy, headings, marketing copy, code, file names, URLs, classes) | **One word** | "BidEquity" |

The two-word form is reserved for the visual logo lock-up only. All running text uses the single-word form.

> **v1.2 → v1.3 update note:** The PDF master version 1.2 currently states "Bid Equity (two words)" universally without exception. The two-word/one-word distinction recorded above was confirmed by the brand owner on 2026-04-08 and should be reflected in the next PDF revision.

**Brand descriptor:** "Pursuit Intelligence" — always paired with the logo lock-up. Sits **beneath** the wordmark, never beside it in the canonical layout.

---

## 2. Colour palette

### Core palette (6 + descriptor exception)

| Role | Hex | Name | Usage |
|---|---|---|---|
| Primary | `#021744` | **Midnight Navy** | Main text, headings, structural elements, primary chart colour, app header background |
| Background | `#F7F4EE` | **Soft Sand** | Page canvas — **mandatory** for web, slides, docs, print. Never use pure white as a page background. |
| Secondary | `#5CA3B6` | **Calm Teal** | Structural UI on light backgrounds only — navigation borders, table headers, panel borders, horizontal rules. **Never use as text on navy** (insufficient contrast). |
| Light Accent | `#E0F4F6` | **Pale Aqua** | Card fills, subtle backgrounds, section dividers. Light backgrounds only — never on dark. |
| Primary Accent | `#7ADDE2` | **Bright Aqua** | The attention colour. Hover states, focus states, active states, selected states, hero accents, key highlights, chart secondary colour. Approved for print. Works on both light and dark backgrounds. |
| Warm Accent | `#D17A74` | **Light Terracotta** | The single warm accent. CTAs, primary buttons, callout badges, pull quotes. **Use sparingly — one focal element per section or slide.** |
| Descriptor exception | `#60F5F7` | **Bright Cyan** | Descriptor lock-up only — the "Pursuit Intelligence" line beneath the wordmark. Sits outside the core palette by design — luminous contrast against navy. **Do not use anywhere else.** |

### What's deprecated (do not use)

- `#C96F5A` (Deep Coral) — removed in v1.2. Replaced by Light Terracotta.
- `#8C3B36` (Brick Wine) — removed in v1.2. The single warm accent is Light Terracotta only.
- Any other warm colour — multiple warms in one composition is forbidden.

### Navy gradient (data visualisation)

| Step | Hex | Name | Chart usage |
|---|---|---|---|
| Navy 900 | `#021744` | Midnight Navy | Primary data series, solid fills, axis text |
| Navy 700 | `#2D3F64` | Deep Slate | Secondary data bars, darker fills |
| Navy 500 | `#576482` | Steel Blue | Mid-tone elements, supporting data |
| Navy 300 | `#818CA2` | Pewter | Tertiary data, gridlines |
| Navy 200 | `#ABB2C1` | Silver Fog | Axis labels, light backgrounds |
| Navy 100 | `#D5D9E0` | Pale Slate | Lightest tint, subtle chart backgrounds |

### Aqua gradient (data visualisation)

| Step | Hex | Name | Chart usage |
|---|---|---|---|
| Aqua 100 | `#CCF3F6` | Ice Aqua | Lightest tint, area fill backgrounds |
| Aqua 200 | `#A3E8EC` | Soft Aqua | Light chart fills |
| Aqua 300 | `#7ADDE2` | Bright Aqua | Primary aqua data series |
| Aqua 400 | `#5CC0C6` | Clear Aqua | Mid-tone emphasis |
| Aqua 500 | `#3FA3AA` | Teal Aqua | Stronger emphasis |
| Aqua 600 | `#24878E` | Deep Aqua | Maximum emphasis, chart borders |

### Data viz rule

Charts use **only** the Navy and Aqua gradient palettes. **No other colours.** Light Terracotta is the single permitted exception, reserved exclusively for **loss indicators, negative variances, or key insights that must surface immediately.**

### Pairing rules — quick reference

**Always:**
- Midnight Navy text on Soft Sand background — the workhorse
- Soft Sand text on Midnight Navy background — for hero / dark sections
- Bright Aqua accents on either background — the signature highlight
- Light Terracotta CTAs on either background — sparingly

**Never:**
- Calm Teal as text on navy — insufficient contrast
- Pale Aqua as text — background tint only
- Pure white as a background — always Soft Sand
- Multiple warm colours in one composition
- Terracotta in charts (except for the loss/insight exception)

---

## 3. Typography

**Two fonts only.** Both Google Fonts (free, open-source).

```html
<link href="https://fonts.googleapis.com/css2?family=Spline+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

| Context | Font | Weight | Notes |
|---|---|---|---|
| Logo / wordmark | **Spline Sans** | 600–700 | Tight line height. Colour: Midnight Navy on light, Soft Sand on dark. |
| Descriptor ("Pursuit Intelligence") | Inter | 500 | Letter-spacing 0.18em uppercase. Colour: `#60F5F7` (Bright Cyan). |
| Main headings | **Spline Sans** | 500–600 | |
| Sub-headings | **Spline Sans** | 500 | |
| Body copy / UI / data / dashboards | Inter | 400–500 | Use `font-feature-settings: "tnum" 1, "lnum" 1` for tabular numerals in scorecards and metrics. |
| Labels / captions | Inter | 500 | Slight letter-spacing. |
| **Navigation** | **Spline Sans** | 500 | Per typography rules: Spline Sans is reserved for display contexts including navigation. |

### Typography rules

- **Spline Sans** is reserved for display: logo, headlines, slide titles, navigation. Do not use it for body text.
- **Inter** is the workhorse: body, data tables, dashboards, labels, all running text.
- **No third font.** No JetBrains Mono, no Cormorant, no DM Mono. Inter handles tabular numerals via `font-feature-settings: "tnum"` — use that, not a monospace font.
- Strong numeral support is essential (dashboards, scorecards, metrics) — Inter handles this well.
- No more than two weights of each font in a single document.

---

## 4. Component patterns

### Brand wordmark lock-up

The lock-up is **always** wordmark-on-top, descriptor-beneath:

```
Bid Equity
PURSUIT INTELLIGENCE
```

Use the canonical `.be-wordmark` class from `brand-tokens.css`:

```html
<a href="/" class="be-wordmark">
  <span class="be-wordmark__name">
    <span class="be-wordmark__bid">Bid</span><span class="be-wordmark__equity">Equity</span>
  </span>
  <span class="be-wordmark__descriptor">Pursuit Intelligence</span>
</a>
```

The two-word visual rendering comes from the inline-flex layout plus a `margin-right` on `.be-wordmark__bid`. Do not type a literal space between the spans — the class handles it.

### Page background

```css
body { background: var(--be-bg-page); /* = #F7F4EE Soft Sand */ }
```

**Mandatory.** Pure white (`#FFFFFF`) is forbidden as a page canvas.

### Cards / panels (light mode)

```css
.card { background: var(--be-bg-card); /* = #E0F4F6 Pale Aqua */ }
```

Pale Aqua for card fills and section dividers. Sharp corners — no border-radius.

### CTAs / primary buttons

```css
.cta {
  background: var(--be-accent-cta);   /* = #D17A74 Light Terracotta */
  color: var(--be-text-on-dark);      /* = #F7F4EE Soft Sand */
  font-family: var(--be-font-display);
  font-weight: var(--be-fw-body-bold);
  border: none;
}
```

Use sparingly. Limit to **one focal CTA per section or slide.**

### Hover / focus / active / selected states

```css
.element:hover, .element:focus-visible, .element.active {
  color: var(--be-accent-attention);   /* = #7ADDE2 Bright Aqua */
}
```

Bright Aqua is *the* attention colour. Use consistently for all interactive feedback states.

### Sharp edges

**Zero border-radius anywhere.** Cards, buttons, badges, inputs, progress bars, modals, slideouts — all sharp corners.

---

## 5. Brand voice (summary)

Tone: **"McKinsey meets specialist operator."**

- Confident, not loud
- Forensic — every claim backed by methodology
- Commercially grounded — bid economics, not features
- Procurement-native
- Challenger where appropriate

**Two registers:**

- **Institutional** (client docs, engagement letters): formal, PE-house language. Mandates, co-investment, conviction.
- **Challenger** (marketing, LinkedIn, website): sharper, more direct. Short sentences. Lead with the problem.

**Language principles:**

- UK English (programme, organisation, colour)
- Active voice
- Lead with outcomes, not features
- Avoid: "support", "assist", "help with", "synergies", "leverage", "world-class", "best-in-class"
- Never start a sentence with "Leveraging" or "Utilising"
- No exclamation marks in professional content

**AI messaging:**

- Use **"AI-enabled"** not "AI-powered"
- Trust strip: **AI-enabled · Human-led · Secure by design**
- Never lead with AI as the headline differentiator

---

## 6. Strategic identity (summary)

- **Name:** Bid Equity (logo) / BidEquity (everywhere else)
- **Descriptor:** Pursuit Intelligence
- **Commercial tagline:** Paid on Award (avoid "No Win, No Fee")
- **One-line proposition:** *"The institutional intelligence layer for high-stakes contract acquisition, backed by a success-contingent model."*
- **Target audience:** Senior commercial decision-makers (Partners, BD Directors, CCO/COO/CFO, Heads of Bids) at firms competing for £50m–£1.5bn UK public sector contracts.
- **Sectors:** Defence, Justice, Emergency Services, transformation programmes, central government.

---

## 7. Offer architecture (summary)

**Two-tier model:**

- **Bid Equity Core — Paid on Award.** Managed intelligence overlay. Small base + success fee.
- **Bid Equity Command — Embedded + Profit-Aligned.** Embedded bid management office. Base + award fee + profit share on verified efficiency gains.

**Operating model modules** (each branded as "Bid Equity [Module]"):

1. Qualify — pursuit decision and opportunity scoring
2. Plan — strategy architecture and resource allocation
3. Shape — pre-tender positioning and relationship mapping
4. Compete — competitive intelligence and differentiation
5. Score — evaluation matrix alignment and scoring optimisation
6. Price — commercial modelling and pricing strategy
7. Comply — traceability, mandatory requirements, risk management
8. Review — structured reviews and quality gates
9. Ready — submission readiness and final assurance
10. Learn — post-outcome analysis and capability building

---

## 8. Production status

**Confirmed (this version):**
- 6-colour palette + descriptor exception
- Navy and Aqua 6-step gradient palettes
- Spline Sans + Inter typography
- Naming conventions (logo two words, body one word — per 2026-04-08 update)
- Soft Sand mandatory page canvas
- `brand-tokens.css` as canonical implementation

**Outstanding:**
- Logo file (Structural Cipher concept — needs designer)
- CMYK / Pantone equivalents for print
- Module badge icon set
- Document templates (governance pack)
- Canva brand kit configuration

---

## Version history

| Version | Date | Summary |
|---|---|---|
| 1.0 | 24 March 2026 | Initial consolidation. Palette, typography, name format, descriptor, voice, offer architecture established. |
| 1.1 | 25 March 2026 | Added colour usage guidance for light/dark assets across web, slides, docs, social, print. Expanded pairing rules. |
| 1.2 | 26 March 2026 | Removed Deep Coral (`#C96F5A`) and Brick Wine (`#8C3B36`). Added Light Terracotta (`#D17A74`) as the single warm accent. Soft Sand mandatory canvas. Bright Aqua approved for print. Chart colours restricted to Navy + Aqua gradients with Terracotta as loss/insight exception. Added 6-step gradient palettes. |
| 1.2.1 | 8 April 2026 | (This markdown only — pending PDF v1.3.) Naming convention split: "Bid Equity" two words is logo-only; "BidEquity" one word everywhere else. Added in-repo `brand-tokens.css` as canonical implementation. Deprecated `brand-design-system.md`. Removed JetBrains Mono from product apps (use Inter with `font-feature-settings: "tnum"`). |
