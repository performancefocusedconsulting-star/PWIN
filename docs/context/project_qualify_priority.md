---
name: Qualify is #1 priority — lead gen product
description: 2026-04-05 — Qualify is the live lead generation tool. Website CTAs point to it. Must work end-to-end with AI assurance review via Netlify Function proxy.
type: project
---

## Priority

PWIN Qualify is the number one product priority. The website (bidequity.co) is live with CTAs directing users to qualify their pursuit. This is the lead generation mechanism.

**Why:** User needs to start building marketing momentum. Qualify is the gateway product — free qualification tool that captures leads and demonstrates AI capability.

## Architecture for production

- Website `qualify.html` — registration form (lead capture via Netlify forms) → redirects to `qualify-app.html`
- `qualify-app.html` — rebranded prototype with full 24-question assessment + AI assurance review
- `netlify/functions/ai-review.js` — serverless proxy that adds ANTHROPIC_API_KEY (env var) and forwards to Claude API
- Registration stored in localStorage — return visitors skip the gate

## AI readiness

The AI is production-ready. Alex Mercer persona, per-question rubrics, inflation detection, opportunity type enrichment (7 types), calibration rules, auto-challenge triggers — all built and tested. No additional skill development needed for V1.

## Deployment requirement

User must set `ANTHROPIC_API_KEY` as an environment variable in the Netlify dashboard before AI review will work.

**How to apply:** Qualify work takes priority over Bid Execution backlog items. Get it live and generating leads first.
