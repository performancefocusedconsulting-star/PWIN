---
name: API cost modelling needed
description: 2026-04-03 — user concerned about Claude API costs scaling across opportunities/clients; needs cost model per skill, cost reduction architecture, and business case validation before launch
type: project
---

## API Cost Concern — Raised Session 16

### The problem
Live skill testing cost $0.41 (3 skills, synthetic data). User's concern: with 55 skills across multiple opportunities and clients, API costs could undermine the business case and pricing model. Must be understood before go-to-market.

### What's needed
1. **Cost model per skill** — estimate tokens in/out and cost for each of the 55 skills at realistic data volumes. Identify which skills are expensive (large context) vs cheap (small reads).
2. **Cost per opportunity lifecycle** — what does it cost to run PWIN across a full bid from qualify through submission? Aggregate across typical skill invocations.
3. **Cost reduction architecture** — what design decisions reduce token usage:
   - Pre-built client profiles and competitor dossiers (stored in bid library, not re-researched per bid)
   - Claude Pro subscription for building reference data vs API for production skills
   - Caching/memoisation of sector knowledge and reasoning rules in system prompt
   - Prompt caching (Anthropic feature) to reduce repeated context costs
   - Smaller models (Haiku) for simpler skills vs Sonnet for complex analysis
   - Server-side filtering to minimise data sent to Claude (already designed in MCP query contracts)
4. **Pricing model implications** — what can PWIN charge per opportunity if API cost is X? Is the value proposition viable at scale?

### User's specific insight
Using Claude Pro subscription to maintain client profiles, competitor dossiers, and bid library data in structured format — then the API skills read pre-built intelligence rather than researching from scratch each time. This is already partially designed (reference/ directory in file store, Agent 2 recurring intelligence) but the cost implications haven't been quantified.

### How to apply
Build the cost model BEFORE go-to-market. This is a business-critical analysis, not a nice-to-have. Architecture decisions (which model per skill, what gets cached, what's pre-built) flow from this.
