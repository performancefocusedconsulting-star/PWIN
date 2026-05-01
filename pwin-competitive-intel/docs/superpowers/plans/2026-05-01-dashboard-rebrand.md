# BidEquity Dashboard Rebrand Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand `dashboard.html` to the BidEquity light theme — new colours, fonts, name, and per-tab orientation panels.

**Architecture:** Single-file change to `pwin-competitive-intel/dashboard.html`. All changes are in the `<style>` block, the `<head>` font import, and the HTML body. No changes to `server.py`, query logic, or the database.

**Tech Stack:** Vanilla HTML/CSS/JS. Google Fonts (Inter, Spline Sans). No build step — edit and open in browser to verify.

---

## File changed

- Modify: `pwin-competitive-intel/dashboard.html` — font imports, CSS `:root` tokens, body/component styles, header markup, tab labels, intro panel HTML and CSS

---

## How to test

Start the server before beginning any task, keep it running throughout:

```bash
cd pwin-competitive-intel
python server.py
```

Open `http://localhost:8765/dashboard.html` in a browser. Hard-refresh (`Ctrl+Shift+R`) after each task to see changes.

---

## Task 1: Replace font imports and CSS design tokens

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html` lines 6–36

- [ ] **Step 1: Replace the `<title>` and font import lines**

Replace lines 6–8:
```html
<title>PWIN Competitive Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
```
With:
```html
<title>BidEquity Pursuit Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Spline+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
```

- [ ] **Step 2: Replace the entire `:root` block (lines 10–36)**

Replace the existing `:root { ... }` block with:
```css
/* ── DESIGN TOKENS — BidEquity brand ───────────────────────── */
:root {
  /* Palette */
  --bg-deep:    #F7F4EE;   /* Soft Sand — page canvas */
  --bg-mid:     #021744;   /* Midnight Navy — header */
  --bg-card:    #E0F4F6;   /* Pale Aqua — card fill */
  --bg-hover:   #CCF3F6;   /* Ice Aqua — row hover */
  --gold:       #7ADDE2;   /* Bright Aqua — active/accent */
  --gold-light: #5CC0C6;   /* Clear Aqua — active hover */
  --gold-dim:   rgba(122,221,226,0.15);
  --text:       #021744;   /* Midnight Navy — primary text */
  --text-bright:#021744;
  --text-muted: #576482;   /* Steel Blue — secondary text */
  --green:      #2ecc71;
  --amber:      #D17A74;   /* Terracotta — CTAs */
  --red:        #e74c3c;
  --border:     #D5D9E0;   /* Pale Slate */
  --border-row: #E8E4DC;

  /* Typography */
  --font-display: 'Spline Sans', sans-serif;
  --font-body:    'Inter', sans-serif;
  --font-mono:    'Inter', sans-serif;

  /* Shape — brand rule: zero radius everywhere */
  --radius:     0px;
  --radius-lg:  0px;
  --shadow:     0 4px 24px rgba(2,23,68,0.08);
  --shadow-sm:  0 2px 8px rgba(2,23,68,0.06);

  /* BidEquity semantic extras */
  --be-teal:        #5CA3B6;
  --be-sand:        #F7F4EE;
  --be-navy:        #021744;
  --be-terracotta:  #D17A74;
  --be-pale-aqua:   #E0F4F6;
  --be-bright-aqua: #7ADDE2;
  --be-cyan:        #60F5F7;
}
```

- [ ] **Step 3: Verify in browser**

Hard-refresh `http://localhost:8765/dashboard.html`. The page background should now be cream/sand (`#F7F4EE`). The header will look broken (still using old markup) — that's expected here.

- [ ] **Step 4: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "style(dashboard): replace design tokens with BidEquity brand palette"
```

---

## Task 2: Update body, header, and tab bar styles

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html` — CSS sections for `body`, `.header`, `.tabs`, `.tab`

- [ ] **Step 1: Update `body` background reference**

The `body` rule uses `var(--bg-deep)` — this now resolves to Soft Sand from Task 1. No code change needed. Verify the page background is sand-coloured after Task 1.

- [ ] **Step 2: Update `.header` CSS**

Find the `.header` rule (currently has `border-bottom: 2px solid var(--gold)`). Replace:
```css
.header {
  background: var(--bg-mid);
  border-bottom: 2px solid var(--gold);
  padding: 20px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
```
With:
```css
.header {
  background: var(--be-navy);
  border-bottom: 3px solid var(--be-bright-aqua);
  padding: 20px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
```

- [ ] **Step 3: Update `.header h1` and `.header-left` CSS**

Replace:
```css
.header-left { display: flex; align-items: baseline; gap: 16px; }
.header h1 {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--text-bright);
  letter-spacing: 0.5px;
}
.header h1 span { color: var(--gold); }
.header-meta {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}
```
With:
```css
.header-left { display: flex; flex-direction: column; gap: 2px; }
.header-wordmark {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: #F7F4EE;
  letter-spacing: 0.02em;
  line-height: 1.1;
}
.header-wordmark .bid  { margin-right: 0.22em; }
.header-descriptor {
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 9px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--be-cyan);
}
.header-meta {
  font-family: var(--font-body);
  font-size: 11px;
  color: rgba(247,244,238,0.55);
  display: flex;
  align-items: center;
  gap: 6px;
}
```

- [ ] **Step 4: Update tab bar CSS**

Replace the `.tabs` and `.tab` rules:
```css
.tabs {
  background: var(--bg-mid);
  padding: 0 32px;
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
}
.tab {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  padding: 12px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.tab:hover { color: var(--text); background: rgba(255,255,255,0.02); }
.tab.active {
  color: var(--gold);
  border-bottom-color: var(--gold);
}
```
With:
```css
.tabs {
  background: var(--be-sand);
  padding: 0 32px;
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--border);
  overflow-x: auto;
}
.tab {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  padding: 12px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.15s;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.tab:hover { color: var(--be-navy); }
.tab.active {
  color: var(--be-navy);
  border-bottom-color: var(--be-bright-aqua);
  font-weight: 600;
}
```

- [ ] **Step 5: Verify in browser**

The tab bar should now be sand/cream with navy text and a bright aqua underline on the active tab. The header should be dark navy.

- [ ] **Step 6: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "style(dashboard): update header and tab bar to BidEquity light theme"
```

---

## Task 3: Update header markup

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html` — `<header>` HTML block and tab labels

- [ ] **Step 1: Replace the header HTML**

Find (around line 432):
```html
<!-- ── HEADER ─────────────────────────────────────────────── -->
<header class="header">
  <div class="header-left">
    <h1><span>PWIN</span> Competitive Intelligence</h1>
  </div>
  <div class="header-meta" id="headerMeta">
    <span class="dot"></span>
    <span id="lastIngest">Connecting...</span>
  </div>
</header>
```
Replace with:
```html
<!-- ── HEADER ─────────────────────────────────────────────── -->
<header class="header">
  <div class="header-left">
    <div class="header-wordmark"><span class="bid">Bid</span><span class="equity">Equity</span></div>
    <div class="header-descriptor">Pursuit Intelligence</div>
  </div>
  <div class="header-meta" id="headerMeta">
    <span class="dot"></span>
    <span id="lastIngest">Connecting...</span>
  </div>
</header>
```

- [ ] **Step 2: Rename the tab labels**

Find the `<nav class="tabs">` block and replace:
```html
<nav class="tabs" id="tabs">
  <div class="tab active" data-view="summary">Summary</div>
  <div class="tab" data-view="search">Service Search</div>
  <div class="tab" data-view="buyer">Buyer Intelligence</div>
  <div class="tab" data-view="supplier">Supplier Intelligence</div>
  <div class="tab" data-view="expiry">Expiry Pipeline</div>
  <div class="tab" data-view="pipeline">Forward Pipeline</div>
  <div class="tab" data-view="pwin">PWIN Signals</div>
  <div class="tab" data-view="frameworks">Frameworks</div>
</nav>
```
With:
```html
<nav class="tabs" id="tabs">
  <div class="tab active" data-view="summary">Summary</div>
  <div class="tab" data-view="search">Market Search</div>
  <div class="tab" data-view="buyer">Buyer Intel</div>
  <div class="tab" data-view="supplier">Supplier Intel</div>
  <div class="tab" data-view="expiry">Expiry Pipeline</div>
  <div class="tab" data-view="pipeline">Forward Pipeline</div>
  <div class="tab" data-view="pwin">Win Signals</div>
  <div class="tab" data-view="frameworks">Frameworks</div>
</nav>
```

- [ ] **Step 3: Verify in browser**

The header should show "Bid Equity" in Spline Sans bold on navy, with "PURSUIT INTELLIGENCE" in small cyan uppercase below. Tab bar should show the renamed labels.

- [ ] **Step 4: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "style(dashboard): BidEquity wordmark, Pursuit Intelligence descriptor, tab renames"
```

---

## Task 4: Update card, table, badge, and input styles

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html` — CSS sections for cards, tables, badges, search-bar inputs, filters

- [ ] **Step 1: Update `.card` and `.card-title` styles**

Replace:
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}
.card-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 600;
  color: var(--text-bright);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.card-title span { color: var(--gold); font-weight: 700; }
```
With:
```css
.card {
  background: var(--be-pale-aqua);
  border: none;
  border-radius: 0;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}
.card-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--be-navy);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--be-teal);
}
.card-title span { color: var(--be-teal); font-weight: 700; }
```

- [ ] **Step 2: Update `.stat-box` and stat value styles**

Replace:
```css
.stat-box {
  background: var(--bg-mid);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
  transition: border-color 0.2s;
}
.stat-box:hover { border-color: var(--gold-dim); }
.stat-value {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--gold);
  line-height: 1.1;
}
.stat-label {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
```
With:
```css
.stat-box {
  background: white;
  border: 1px solid var(--border);
  border-radius: 0;
  padding: 20px;
  text-align: center;
  transition: border-color 0.2s;
}
.stat-box:hover { border-color: var(--be-bright-aqua); }
.stat-value {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--be-navy);
  line-height: 1.1;
  font-feature-settings: "tnum" 1, "lnum" 1;
}
.stat-label {
  font-family: var(--font-body);
  font-size: 11px;
  color: var(--text-muted);
```

- [ ] **Step 3: Update table styles**

Replace the `thead th` and `tbody td` rules:
```css
thead th {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
tbody td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-row);
  color: var(--text);
  vertical-align: middle;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```
With:
```css
thead th {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--be-sand);
  background: var(--be-teal);
  text-align: left;
  padding: 10px 12px;
  white-space: nowrap;
}
tbody td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-row);
  color: var(--text);
  vertical-align: middle;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-feature-settings: "tnum" 1, "lnum" 1;
}
```

Also update the row hover and expandable row styles:
```css
tr.expandable:hover { background: var(--be-pale-aqua); }
tbody tr { transition: background 0.15s; }
tbody tr:hover { background: var(--be-pale-aqua); border-left: 2px solid var(--be-bright-aqua); }
```

And update the detail row inner background:
```css
tr.detail-row .detail-inner {
  padding: 16px 20px;
  background: white;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text);
  white-space: normal;
  word-break: break-word;
}
```

And the detail row link colour:
```css
tr.detail-row .detail-inner a {
  color: var(--be-teal);
  text-decoration: none;
}
```

- [ ] **Step 4: Update `.td.num` for tabular numerals**

Replace:
```css
td.num {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--text-bright);
  text-align: right;
}
td.mono {
  font-family: var(--font-mono);
  font-size: 12px;
}
```
With:
```css
td.num {
  font-family: var(--font-body);
  font-weight: 600;
  font-feature-settings: "tnum" 1, "lnum" 1;
  color: var(--be-navy);
  text-align: right;
}
td.mono {
  font-family: var(--font-body);
  font-size: 12px;
  font-feature-settings: "tnum" 1;
}
```

- [ ] **Step 5: Update badge styles**

Replace:
```css
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
}
.badge-red    { background: rgba(231,76,60,0.15); color: var(--red); }
.badge-amber  { background: rgba(243,156,18,0.15); color: var(--amber); }
.badge-green  { background: rgba(46,204,113,0.15); color: var(--green); }
```
With:
```css
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 0;
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 500;
}
.badge-red    { background: rgba(209,122,116,0.15); color: #8B3A35; }
.badge-amber  { background: var(--be-pale-aqua); color: var(--be-teal); }
.badge-green  { background: var(--be-pale-aqua); color: var(--be-navy); }
```

- [ ] **Step 6: Update search-bar and filter input styles**

Replace:
```css
.search-bar input {
  flex: 1;
  background: var(--bg-mid);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  color: var(--text-bright);
  font-family: var(--font-body);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.search-bar input::placeholder { color: var(--text-muted); }
.search-bar input:focus { border-color: var(--gold); }
.search-bar button, .btn {
  background: var(--gold);
  color: var(--bg-deep);
  border: none;
  border-radius: var(--radius);
  padding: 10px 24px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: background 0.2s;
}
.search-bar button:hover, .btn:hover { background: var(--gold-light); }
```
With:
```css
.search-bar input {
  flex: 1;
  background: white;
  border: 1px solid var(--border);
  border-radius: 0;
  padding: 12px 16px;
  color: var(--be-navy);
  font-family: var(--font-body);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.search-bar input::placeholder { color: var(--text-muted); }
.search-bar input:focus { border-color: var(--be-bright-aqua); box-shadow: 0 0 0 2px rgba(122,221,226,0.25); }
.search-bar button, .btn {
  background: var(--be-terracotta);
  color: var(--be-sand);
  border: none;
  border-radius: 0;
  padding: 10px 24px;
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: background 0.2s;
}
.search-bar button:hover, .btn:hover { background: #B8645E; }
```

Also update the filter bar and filter inputs:
```css
.filters {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 0;
  border: 1px solid var(--border);
}
.filter-group input, .filter-group select {
  background: white;
  border: 1px solid var(--border);
  border-radius: 0;
  padding: 8px 12px;
  color: var(--be-navy);
  font-family: var(--font-body);
  font-size: 13px;
  outline: none;
}
.filter-group input:focus, .filter-group select:focus { border-color: var(--be-bright-aqua); }
.filter-group select option { background: white; color: var(--be-navy); }
```

- [ ] **Step 7: Update the range slider and spinner**

Replace:
```css
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: var(--gold);
  cursor: pointer;
}
```
With:
```css
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px; height: 14px;
  border-radius: 0;
  background: var(--be-terracotta);
  cursor: pointer;
}
```

Replace spinner border-top-color:
```css
.spinner {
  width: 24px; height: 24px;
  border: 2px solid var(--border);
  border-top-color: var(--be-teal);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}
```

- [ ] **Step 8: Verify in browser**

Cycle through all tabs. Cards should be pale aqua, table headers teal with sand text, buttons terracotta, inputs white with aqua focus ring. No dark backgrounds anywhere except the header.

- [ ] **Step 9: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "style(dashboard): light-theme cards, tables, badges, inputs"
```

---

## Task 5: Add the intro panel component and HTML for all 8 tabs

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html` — new `.tab-intro` CSS, HTML added to each view section

- [ ] **Step 1: Add the intro panel CSS**

Add this block immediately after the closing `}` of the `.loading` spinner CSS rule (before `/* ── TWO-COL LAYOUT */`):

```css
/* ── TAB INTRO PANELS ───────────────────────────────────────── */
.tab-intro {
  background: white;
  border-left: 4px solid var(--be-teal);
  padding: 16px 20px;
  margin-bottom: 24px;
}
.tab-intro-heading {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--be-navy);
  margin-bottom: 4px;
}
.tab-intro-body {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
}
.tab-intro-body strong { color: var(--be-navy); font-weight: 500; }
```

- [ ] **Step 2: Add intro panel to Summary tab**

In the HTML, find:
```html
  <!-- SUMMARY VIEW -->
  <section class="view active" id="view-summary">
    <div class="stat-grid" id="summaryStats"></div>
```
Replace with:
```html
  <!-- SUMMARY VIEW -->
  <section class="view active" id="view-summary">
    <div class="tab-intro">
      <div class="tab-intro-heading">What's in the database</div>
      <div class="tab-intro-body">A real-time snapshot of all contracts, buyers, and suppliers loaded from the UK government's public procurement feed. No inputs needed — the data updates automatically each night.</div>
    </div>
    <div class="stat-grid" id="summaryStats"></div>
```

- [ ] **Step 3: Add intro panel to Market Search tab**

Find:
```html
  <!-- SERVICE SEARCH VIEW -->
  <section class="view" id="view-search">
    <div class="filters">
```
Replace with:
```html
  <!-- MARKET SEARCH VIEW -->
  <section class="view" id="view-search">
    <div class="tab-intro">
      <div class="tab-intro-heading">Find contracts by what was bought</div>
      <div class="tab-intro-body">Search across all active and recently-awarded contracts by service type, buying organisation, and minimum value. Use this to size a market, identify incumbents, and see who buys what from whom.</div>
    </div>
    <div class="filters">
```

- [ ] **Step 4: Add intro panel to Buyer Intel tab**

Find:
```html
  <!-- BUYER INTELLIGENCE VIEW -->
  <section class="view" id="view-buyer">
    <div class="search-bar">
```
Replace with:
```html
  <!-- BUYER INTEL VIEW -->
  <section class="view" id="view-buyer">
    <div class="tab-intro">
      <div class="tab-intro-heading">Profile a buying organisation</div>
      <div class="tab-intro-body">Type any buyer name to see their full spending history: total awards, preferred suppliers, procurement methods, and behavioural patterns. Works best with the official buyer name — try <strong>Ministry of Defence</strong> or <strong>NHS England</strong>.</div>
    </div>
    <div class="search-bar">
```

- [ ] **Step 5: Add intro panel to Supplier Intel tab**

Find:
```html
  <!-- SUPPLIER INTELLIGENCE VIEW -->
  <section class="view" id="view-supplier">
    <div class="search-bar">
```
Replace with:
```html
  <!-- SUPPLIER INTEL VIEW -->
  <section class="view" id="view-supplier">
    <div class="tab-intro">
      <div class="tab-intro-heading">Profile a supplier</div>
      <div class="tab-intro-body">Type any supplier name to see their contract wins across all buyers, with Companies House data (directors, parent company, turnover) where available. Variants and trading names are automatically grouped.</div>
    </div>
    <div class="search-bar">
```

- [ ] **Step 6: Add intro panel to Expiry Pipeline tab**

Find:
```html
  <!-- EXPIRY PIPELINE VIEW -->
  <section class="view" id="view-expiry">
    <div class="filters">
```
Replace with:
```html
  <!-- EXPIRY PIPELINE VIEW -->
  <section class="view" id="view-expiry">
    <div class="tab-intro">
      <div class="tab-intro-heading">Contracts coming up for renewal</div>
      <div class="tab-intro-body">Spot re-bid and pipeline opportunities by filtering contracts due to expire within your chosen timeframe. Filter by buyer, service category, or minimum value.</div>
    </div>
    <div class="filters">
```

- [ ] **Step 7: Add intro panel to Forward Pipeline tab**

Find:
```html
  <!-- FORWARD PIPELINE VIEW -->
  <section class="view" id="view-pipeline">
    <div class="filters">
```
Replace with:
```html
  <!-- FORWARD PIPELINE VIEW -->
  <section class="view" id="view-pipeline">
    <div class="tab-intro">
      <div class="tab-intro-heading">Tenders not yet live</div>
      <div class="tab-intro-body">Planning and market engagement notices published by buyers before a formal tender is released — typically 3 to 18 months ahead. Filter by buyer name or organisation type.</div>
    </div>
    <div class="filters">
```

- [ ] **Step 8: Add intro panel to Win Signals tab**

Find the PWIN Signals view section (will have `id="view-pwin"`). Find:
```html
  <!-- PWIN SIGNALS VIEW -->
  <section class="view" id="view-pwin">
```
Replace the comment and opening tag, then insert the intro panel before the first child element:
```html
  <!-- WIN SIGNALS VIEW -->
  <section class="view" id="view-pwin">
    <div class="tab-intro">
      <div class="tab-intro-heading">Competitive pressure by buyer and category</div>
      <div class="tab-intro-body">Shows how many suppliers typically compete for contracts in each buyer/category combination, the average contract value, and how often work is awarded by open versus direct competition.</div>
    </div>
```

- [ ] **Step 9: Add intro panel to Frameworks tab**

Find the frameworks view section (will have `id="view-frameworks"`). Insert the intro panel as the first child:
```html
    <div class="tab-intro">
      <div class="tab-intro-heading">Pre-agreed supplier shortlists</div>
      <div class="tab-intro-body">Frameworks are agreements that let buyers award contracts quickly to pre-approved suppliers without a full tender. Browse by owner, status, or category to see which frameworks are active in your market.</div>
    </div>
```

- [ ] **Step 10: Verify in browser**

Click through every tab. Each should show its intro panel — white background, teal left border, heading in navy Spline Sans, body in grey Inter. Check that the panel sits above the filter bar or search bar, not inside a card.

- [ ] **Step 11: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "feat(dashboard): add per-tab orientation panels"
```

---

## Task 6: Fix residual dark-theme elements

**Files:**
- Modify: `pwin-competitive-intel/dashboard.html` — inline styles and any remaining hardcoded dark values

- [ ] **Step 1: Fix the Frameworks tab inline search input style**

The frameworks filter bar has an inline style: `style="...background:var(--surface);color:var(--text);border:1px solid rgba(255,255,255,0.1)..."` on both the search input and the select dropdowns. Find these (search for `var(--surface)`) and replace each occurrence's inline style with:
```
style="flex:2;min-width:200px;padding:8px 12px;background:white;color:var(--be-navy);border:1px solid var(--border);border-radius:0"
```
And for the select dropdowns:
```
style="flex:1;min-width:140px;padding:8px;background:white;color:var(--be-navy);border:1px solid var(--border);border-radius:0"
```

- [ ] **Step 2: Fix the expiry days label colour**

Find:
```html
<span id="expiryDaysLabel" style="font-family:var(--font-mono);font-size:12px;color:var(--gold);min-width:50px;">365 days</span>
```
Replace with:
```html
<span id="expiryDaysLabel" style="font-family:var(--font-body);font-size:12px;font-weight:600;color:var(--be-navy);min-width:50px;">365 days</span>
```

- [ ] **Step 3: Fix JS-rendered `var(--gold)` colour references**

The search summary line in JavaScript uses `color:var(--gold)` in two template literal spans. After the token swap `var(--gold)` = Bright Aqua `#7ADDE2`, which has poor contrast on the sand background. Find (around line 1019):

```javascript
document.getElementById('searchSummary').innerHTML = `
  <span class="mono" style="color:var(--gold)">${fmtNumber(data.count)}</span> awards matching
  <strong>${svcLabel}</strong> at <strong>${buyerLabel}</strong> ≥ ${fmtCurrency(Number(minValue))}
  — total value <span class="mono" style="color:var(--gold)">${fmtCurrency(totalValue)}</span>
`;
```

Replace both `color:var(--gold)` with `color:var(--be-navy);font-weight:600`:

```javascript
document.getElementById('searchSummary').innerHTML = `
  <span class="mono" style="color:var(--be-navy);font-weight:600">${fmtNumber(data.count)}</span> awards matching
  <strong>${svcLabel}</strong> at <strong>${buyerLabel}</strong> ≥ ${fmtCurrency(Number(minValue))}
  — total value <span class="mono" style="color:var(--be-navy);font-weight:600">${fmtCurrency(totalValue)}</span>
`;
```

- [ ] **Step 4: Scan for any remaining `var(--gold)` in inline styles**

Search the file for `var(--gold)` in inline `style=""` attributes (the CSS rule uses are already handled by Task 1's token swap). Fix any found by replacing with `var(--be-teal)` or `var(--be-navy)` as appropriate.

- [ ] **Step 4: Fix the `.proc-bar` background**

The procurement method bar has `background: rgba(255,255,255,0.05)` which is invisible on light bg. Replace:
```css
.proc-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  min-width: 120px;
  background: rgba(255,255,255,0.05);
}
```
With:
```css
.proc-bar {
  display: flex;
  height: 8px;
  border-radius: 0;
  overflow: hidden;
  min-width: 120px;
  background: var(--border);
}
```

- [ ] **Step 5: Fix empty state styles**

Replace:
```css
.empty-state h3 {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--text);
  margin-bottom: 8px;
}
```
With:
```css
.empty-state h3 {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--be-navy);
  margin-bottom: 8px;
}
```

Replace:
```css
.empty-state code {
  font-family: var(--font-mono);
  background: var(--bg-card);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--gold);
}
```
With:
```css
.empty-state code {
  font-family: var(--font-body);
  background: var(--be-pale-aqua);
  padding: 4px 10px;
  border-radius: 0;
  font-size: 12px;
  color: var(--be-teal);
}
```

- [ ] **Step 6: Full visual sweep in browser**

Cycle through every tab. Look for:
- Any dark/navy background that shouldn't be there (other than the header)
- Any gold-coloured text or borders
- Any rounded corners (all should be sharp)
- Any white text on a white/sand background (invisible text)

Fix any issues found.

- [ ] **Step 7: Commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "style(dashboard): fix residual dark-theme elements and inline styles"
```

---

## Task 7: Final check and wrap-up

- [ ] **Step 1: Full tab-by-tab browser review**

Open `http://localhost:8765/dashboard.html`. Go through every tab in order:

| Tab | Check |
|---|---|
| Summary | Sand bg, pale aqua cards, teal table headers, navy stat values, no dark |
| Market Search | Intro panel visible, teal table header, terracotta Search button |
| Buyer Intel | Intro panel visible, white input with aqua focus, terracotta Search button |
| Supplier Intel | Intro panel visible, same as Buyer Intel |
| Expiry Pipeline | Intro panel visible, filter bar white bg, terracotta Apply Filters |
| Forward Pipeline | Intro panel visible, filter bar white bg |
| Win Signals | Intro panel visible, teal table header |
| Frameworks | Intro panel visible, no dark filter inputs |

- [ ] **Step 2: Check header**

Confirm the header shows: "Bid Equity" in Spline Sans bold (sand text on navy), "PURSUIT INTELLIGENCE" in small cyan uppercase below it.

- [ ] **Step 3: Check browser tab title**

The browser tab should read "BidEquity Pursuit Intelligence".

- [ ] **Step 4: Final commit**

```bash
git add pwin-competitive-intel/dashboard.html
git commit -m "style(dashboard): complete BidEquity rebrand — light theme, wordmark, intro panels"
```
