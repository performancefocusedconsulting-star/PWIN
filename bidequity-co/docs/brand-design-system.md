# BidEquity — Brand Design System v1.2

Extracted from `bid-execution-branded.html`. Applies to all BidEquity products: Qualify, Execution, Verdict.

---

## Fonts

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Display / headings | **Spline Sans** | 600-700 | Page titles, section headers, metric values, brand name, modal titles |
| Body / UI | **Inter** | 400-600 | Body text, labels, buttons, nav, form controls, badges, table headers |

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Spline+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap
```

**Replaces:** Cormorant Garamond (display), DM Mono (labels), DM Sans (body)

---

## Colour Palette

### Core Tokens
```css
:root {
  /* Backgrounds — warm parchment, not cold navy */
  --bg0: #F7F4EE;    /* Page background (warm off-white) */
  --bg1: #FFFFFF;    /* Card/panel background */
  --bg2: #FFFFFF;    /* Secondary surface */
  --bg3: #F0ECE4;    /* Tertiary surface / hover state */
  --bg4: #E8E4DC;    /* Quaternary / column headers */

  /* Borders */
  --bdr: #D5D9E0;    /* Primary border */
  --bdr-s: #E8E4DC;  /* Subtle border */

  /* Accent — teal, not gold */
  --gold: #5CA3B6;       /* Primary accent (teal) */
  --gold-d: rgba(92,163,182,.08);   /* Accent background tint */
  --gold-g: rgba(92,163,182,.04);   /* Accent ghost */

  /* Text */
  --t1: #021744;    /* Primary text (deep navy) */
  --t2: #576482;    /* Secondary text */
  --t3: #818CA2;    /* Tertiary / labels */
  --t4: #ABB2C1;    /* Placeholder / disabled */

  /* Semantic colours */
  --grn: #2D8A5E;   --grn-d: rgba(45,138,94,.08);
  --red: #C15050;   --red-d: rgba(193,80,80,.08);
  --amb: #C68A1D;   --amb-d: rgba(198,138,29,.08);
  --blu: #3B82B8;   --blu-d: rgba(59,130,184,.08);
  --pur: #7C5BA8;   --pur-d: rgba(124,91,168,.08);
  --cyn: #3FA3AA;   --cyn-d: rgba(63,163,170,.08);
  --pink: #B06688;  --pink-d: rgba(176,102,136,.08);
  --lime: #5A8A3D;  --lime-d: rgba(90,138,61,.08);
}
```

### Key Differences from Old Palette
| Element | Old (Midnight Executive) | New (BidEquity Brand) |
|---------|--------------------------|----------------------|
| Page background | Deep navy (#0B1628) | Warm parchment (#F7F4EE) |
| Card background | Dark navy (#132247) | White (#FFFFFF) |
| Primary accent | Gold (#b8860b) | Teal (#5CA3B6) |
| Header bar | Dark navy gradient | Solid navy (#021744) |
| Text on background | White/light | Dark navy (#021744) |
| Overall feel | Dark mode, executive | Light mode, professional, warm |

---

## Header

```css
.hdr {
  padding: 14px 28px;
  border-bottom: 1px solid var(--bdr);
  background: #021744;          /* Solid dark navy */
  position: sticky; top: 0; z-index: 100;
}
.hdr-brand {
  font-family: 'Spline Sans', sans-serif;
  font-size: 20px; font-weight: 700;
  color: #F0EDE6;               /* Warm white */
  letter-spacing: .04em;
}
.hdr-sub {
  font-family: 'Inter', sans-serif;
  font-size: 10px; font-weight: 500;
  letter-spacing: .06em; text-transform: uppercase;
  color: #60F5F7;               /* Bright cyan for product name */
}
```

---

## Typography Scale

| Class | Font | Size | Weight | Colour | Usage |
|-------|------|------|--------|--------|-------|
| `.sl` | Inter | 10px | 600 | var(--gold) | Section label (uppercase, tracked) |
| `.pg-title` | Spline Sans | 24px | 600 | var(--t1) | Page title |
| `.pg-desc` | Inter | 13px | 400 | var(--t2) | Page description |
| `.sh` | Spline Sans | 16px | 600 | var(--t1) | Section heading |
| `.sh2` | Spline Sans | 14px | 500 | var(--t1) | Sub-section heading |
| `.bt` | Inter | 13px | 400 | var(--t2) | Body text |

---

## Component Patterns

### Cards — no border-radius
```css
.cd { background: var(--bg2); border: 1px solid var(--bdr); padding: 14px; }
/* No border-radius anywhere — sharp edges throughout */
```

### Badges
```css
.fe { font-size: 9px; padding: 1px 6px; border-radius: 0; }
/* No border-radius — rectangular badges */
```

### Buttons
```css
.btn { padding: 7px 14px; font-size: 10px; letter-spacing: .04em;
       text-transform: uppercase; border: 1px solid var(--bdr); }
/* No border-radius */
```

### Tables
```css
.tb th { background: #5CA3B6; color: #FFFFFF; font-size: 10px;
         text-transform: uppercase; letter-spacing: .03em; }
/* Teal header row, not navy */
```

### Progress bars
```css
.prog { height: 4px; border-radius: 0; }
/* Zero radius — consistent with sharp-edge brand */
```

---

## Brand Rules

1. **No border-radius anywhere.** Every element has sharp corners — cards, buttons, badges, inputs, progress bars, modals, slideouts.
2. **Light mode.** Warm parchment background, white cards, dark text. Not dark mode.
3. **Teal accent (#5CA3B6)**, not gold. Used for: active nav, primary buttons, table headers, focus states, accent borders.
4. **Header is the only dark element.** Solid #021744 navy with warm white brand name and bright cyan (#60F5F7) product sub-label.
5. **Spline Sans for display, Inter for everything else.** No monospace font in the brand (DM Mono is retired).
6. **Uppercase tracking** on labels, badges, buttons, nav items. Letter-spacing .04em–.12em.
7. **Workstream colours** are retained (gold, blue, green, pink, amber, cyan, lime, purple, red) but map to the new semantic colour set.
