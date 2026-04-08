---
name: Qualify deployment status — 2026-04-05
description: Qualify app deployed to Cloudflare Pages but needs QA fixes before going live. User to review and provide fix list next session.
type: project
---

## Current State (end of 2026-04-05 session)

**Deployed and working:**
- Cloudflare Worker (AI proxy) at `bidequity-ai-review.performancefocusedconsulting.workers.dev` — ANTHROPIC_API_KEY set as secret
- Cloudflare Pages site deployed from PWIN repo, output directory `bidequity-co`
- Netlify site paused (hit 300 build minutes limit from rapid commits)

**Issues to fix next session (user to provide detailed list):**
- Header layout overflow — PWIN score and right-side elements cut off on normal screens
- Brand not fully applied — agent rebrand was incomplete
- Form fields need review — some dropdowns are wrong, some fields need changing
- Lead gen features — some features to turn off for the public-facing version (e.g. session save/load?)
- Flow between views — no clear "next step" button after completing 24 questions
- Registration form also needs review for lead gen context

**Domain setup still needed:**
- bidequity.co currently points to paused Netlify
- Need to either: unpause Netlify when billing resets, or point domain to Cloudflare Pages
- GoDaddy DNS → Netlify currently. Would change to Cloudflare if moving permanently
- Business email DNS records must be preserved during any migration

**How to apply:** Next session starts with user's QA list. Fix all issues in one pass. Then connect domain. Then test live.
