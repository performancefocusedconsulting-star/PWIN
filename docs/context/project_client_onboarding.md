---
name: Client onboarding design
description: 2026-04-03 — user has an onboarding checklist to review; key question is how AI can reduce onboarding burden (RAG over past bids, automated intelligence extraction, progressive enrichment vs upfront data load)
type: project
---

## Client Onboarding — Design Question

### Context
User has produced a client onboarding checklist — what needs to be set up when a new client starts using the platform + consultancy. Wants to review it against the platform architecture.

### Two linked questions

**1. What does onboarding look like?**
- Upload past bids, market intelligence, win/loss reports into bid library
- Populate client profiles, competitor dossiers, sector knowledge
- Configure win rates, loss reasons, team capabilities
- Set up pursuit pipeline with existing live opportunities
- User wants to compare their checklist against what the platform already supports

**2. How can AI reduce the onboarding burden?**
- Organisations hate onboarding — they want to start getting value immediately, not spend weeks loading data
- RAG over past bid documents could auto-extract: credentials, case studies, win themes, team CVs, pricing benchmarks, loss report insights
- Agent 2 (Market & Competitive Intelligence) could auto-build client profiles and competitor dossiers from uploaded documents rather than manual entry
- Progressive enrichment model: start with minimal data, AI fills gaps as you work on real bids, intelligence accumulates over time rather than requiring a big upfront load
- The bid library (reference/ directory) is already designed but not built — the onboarding question shapes HOW it gets populated

### How to apply
Review the user's onboarding checklist in a future session. Design the onboarding flow as a product feature, not just a consulting process. The AI-assisted onboarding could itself be a differentiator — "upload your last 5 bids and we'll build your intelligence baseline in 24 hours."
