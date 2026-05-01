# BidEquity Competitive Intelligence Dashboard — Rebrand Design

**Date:** 2026-05-01
**Scope:** Visual rebrand of `pwin-competitive-intel/dashboard.html`
**Approach:** Option B — rebrand with light-theme polish (not cosmetic-only, not full rebuild)

---

## Problem

The dashboard uses a dark "Midnight Executive" theme (deep navy, gold accents, rounded corners, Cormorant Garamond / DM Mono fonts) that is inconsistent with the BidEquity brand. It is also referred to as "PWIN Competitive Intelligence" throughout, which is internal jargon. Tab names give no indication of what each tab does, and there is no on-screen orientation text.

---

## What we are changing

Three things:

1. **Brand** — apply BidEquity brand colours, typography, and shape rules throughout
2. **Name** — rename from "PWIN Competitive Intelligence" to "BidEquity" with "Pursuit Intelligence" as the descriptor
3. **Orientation** — add an intro panel to every tab explaining its purpose and how to use it

What we are **not** changing: the data layer, server, tab structure, interaction logic, or any query behaviour.

---

## Section 1 — Colour, typography, and shape

All CSS variables are replaced. The mapping is:

| Role | Current (dark) | New (BidEquity light) |
|---|---|---|
| Page background | `#0a1628` | Soft Sand `#F7F4EE` |
| Card fill | `#162544` | Pale Aqua `#E0F4F6` |
| Header bar | `#0f1d32` | Midnight Navy `#021744` (stays dark — brand rule) |
| Primary text | `#e8e0d0` | Midnight Navy `#021744` |
| Muted text | `#8a9ab5` | Steel Blue `#576482` |
| Accent / active | Gold `#c9a84c` | Bright Aqua `#7ADDE2` |
| Structural lines | Gold-tinted | Teal `#5CA3B6` (headers), Pale Slate `#D5D9E0` (rows) |
| CTA buttons | Gold | Terracotta `#D17A74` |
| Corner radius | 8px / 12px | 0px — sharp edges throughout |
| Display font | Cormorant Garamond | Spline Sans |
| Body / data font | DM Sans / DM Mono | Inter (tabular numerals for numeric columns) |

Font loading: replace Google Fonts import with `Spline+Sans:wght@400;500;600;700` and `Inter:wght@300;400;500;600`.

The full BidEquity token set is defined in `bidequity-co/brand-tokens.css`. Because `dashboard.html` is served by `server.py` (which roots at `pwin-competitive-intel/`), that file is outside the served directory and cannot be linked directly. Token values are inlined into the dashboard's `<style>` block using the canonical values from `brand-tokens.css` as the source of truth. If brand tokens change, the dashboard CSS variables must be updated to match.

---

## Section 2 — Header and tab bar

### Header

The dark navy header bar is kept (BidEquity brand: wordmark lives on navy). Content changes:

- **Wordmark:** "Bid Equity" in Spline Sans bold, two words, matching the `.be-wordmark` pattern
- **Descriptor:** "PURSUIT INTELLIGENCE" in uppercase tracked Inter below the wordmark, coloured Bright Cyan `#60F5F7` (the brand's descriptor lock-up colour)
- **Browser title:** `<title>` becomes "BidEquity Pursuit Intelligence"
- **Status indicator:** live/offline dot and last-updated timestamp stay, moved to the right side in smaller quiet Inter

### Tab bar

Moves from dark navy to light sand background. Tab labels updated:

| Old label | New label | Reason |
|---|---|---|
| Summary | Summary | No change |
| Service Search | Market Search | Clearer purpose |
| Buyer Intelligence | Buyer Intel | Shorter |
| Supplier Intelligence | Supplier Intel | Shorter |
| Expiry Pipeline | Expiry Pipeline | No change |
| Forward Pipeline | Forward Pipeline | No change |
| PWIN Signals | Win Signals | Removes internal jargon |
| Frameworks | Frameworks | No change |

Active tab: Midnight Navy text, 2px Bright Aqua underline. Inactive: Steel Blue text. Hover: Navy text. No radius.

---

## Section 3 — Tab intro panels

Every tab gets a panel at the top of its content area containing: a short heading, one sentence of purpose, and one "how to use it" line. Panel style: Pale Aqua background, Teal left border (3px), Navy text, sharp corners.

### Summary
**What's in the database**
A real-time snapshot of all contracts, buyers, and suppliers loaded from the UK government's public procurement feed. No inputs needed — the data updates automatically each night.

### Market Search
**Find contracts by what was bought**
Search across all active and recently-awarded contracts by service type, buying organisation, and minimum value. Use this to size a market, identify incumbents, and see who buys what from whom.

### Buyer Intel
**Profile a buying organisation**
Type any buyer name to see their full spending history: total awards, preferred suppliers, procurement methods, and behavioural patterns. Works best with the official buyer name — try "Ministry of Defence" or "NHS England".

### Supplier Intel
**Profile a supplier**
Type any supplier name to see their contract wins across all buyers, with Companies House data (directors, parent company, turnover) where available. Variants and trading names are automatically grouped.

### Expiry Pipeline
**Contracts coming up for renewal**
Spot re-bid and pipeline opportunities by filtering contracts due to expire within your chosen timeframe. Filter by buyer, service category, or minimum value.

### Forward Pipeline
**Tenders not yet live**
Planning and market engagement notices published by buyers before a formal tender is released — typically 3 to 18 months ahead. Filter by buyer name or organisation type.

### Win Signals
**Competitive pressure by buyer and category**
Shows how many suppliers typically compete for contracts in each buyer/category combination, the average contract value, and how often work is awarded by open versus direct competition.

### Frameworks
**Pre-agreed supplier shortlists**
Frameworks are agreements that let buyers award contracts quickly to pre-approved suppliers without a full tender. Browse by owner, status, or category to see which frameworks are active in your market.

---

## Section 4 — Cards, tables, and buttons

### Cards
- Background: Pale Aqua `#E0F4F6`
- Border: none
- Corner radius: 0
- Card title: Midnight Navy, Spline Sans medium weight
- Shadow: `0 2px 8px rgba(2,23,68,0.06)`

### Tables
- Header row: Teal `#5CA3B6` background, Sand `#F7F4EE` text
- Row background: white, alternating with faint sand `#FAF8F3`
- Row border: Pale Slate `#D5D9E0`
- Numbers: Inter with `font-feature-settings: "tnum" 1, "lnum" 1` for column alignment
- Row hover: Pale Aqua background, 2px Bright Aqua left border

### Badges
- Service category badges: Pale Aqua background, Navy text (replaces dark-background coloured badges)
- Framework badge: Teal background, Sand text
- Warning/amber states: pale terracotta background, Navy text

### Buttons and inputs
- Primary buttons: Terracotta `#D17A74` background, Sand text, 0 radius
- Input fields: white background, Pale Slate `#D5D9E0` border, Bright Aqua `#7ADDE2` focus ring
- All corners: 0 radius

---

## Out of scope — future enhancement

**Performance Reports tab** (UK7 + UK9 notices)

A future tab surfacing Contract Details (UK7) and Contract Performance (UK9) notices as an incumbent-vulnerability win signal. UK9 performance scores against agreed KPIs are a direct signal of whether an incumbent is at risk at renewal. Both notice types are already captured nightly by `agent/ingest.py`; no ingest changes needed when this tab is built. See wiki action `competitive-intel-uk7-uk9-performance-reports-tab.md`.

---

## Files changed

- `pwin-competitive-intel/dashboard.html` — all CSS variables, font imports, header markup, tab labels, tab intro panels, card/table/button styles

No changes to `server.py`, any agent scripts, or the database schema.
