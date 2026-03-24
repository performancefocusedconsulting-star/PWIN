# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PWIN is a monorepo containing multiple products, each in its own subfolder. It is in early development.

## Repository

- **Remote:** https://github.com/performancefocusedconsulting-star/PWIN
- **Main branch:** `main`
- **Structure:** Each product lives in its own subfolder (e.g. `pwin-bid-execution/`)

---

## pwin-bid-execution

A single self-contained HTML application for bid production control and assurance. Used by bid managers to track the full lifecycle of complex government bids.

### Reference Documents

- `pwin-bid-execution/docs/bid_execution_architecture_v6.html` — the WHAT (modules, data model, UX, activities)
- `pwin-bid-execution/docs/bid_execution_rules.html` — the HOW (algorithms, state transitions, formulae, thresholds)
- **Always read the relevant sections of these documents before implementing any feature.**

### Technical Constraints

- Single HTML file output. All CSS, JS, and template data in one file.
- Vanilla JavaScript only. No React, Vue, Angular, or any framework.
- No external JS dependencies beyond Google Fonts (Cormorant Garamond, DM Mono, DM Sans).
- `localStorage` for persistence. JSON import/export for portability.
- Must work in any modern browser without a server.

### Visual Identity

- Midnight Executive palette (see CSS variables in architecture document)
- Cormorant Garamond for display/numbers, DM Mono for labels/data/code, DM Sans for body text
- Deep navy backgrounds, gold accents, structured information hierarchy
- Match the visual style of the architecture document itself

### Code Organisation Within the Single File

- **CSS:** design tokens (variables), base styles, layout, component styles, print styles, animations
- **Data:** state management, mutation functions, computed properties, localStorage, template data
- **Components:** render functions per module, shared UI components (tables, forms, cards, badges, modals)
- **Controllers:** event handlers, routing, validation, calculations, alert logic

### Key Principles

- The bid manager is the sole operator. No multi-user, no login, no authentication.
- The methodology prescribes the activities. The bid manager executes, deactivates, or adjusts.
- Readiness is earned through evidence, not declared by ticking a box.
- Nudges are prompts, not autonomous updates. The system never changes status without human confirmation.
- Every state transition must follow the rules in `bid_execution_rules.html` — no invalid transitions.

---

## Adding New Products

When a new product folder is added, create a new section in this file following the same structure as above.
