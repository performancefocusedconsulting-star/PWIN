---
name: Free-tier sector intel tool — NOT PURSUING (superseded 2026-04-08)
description: Free public-facing procurement lookup tool for Defence/Justice/Transport/Emergency Services — concept dropped. Competitive intel is now an internal-only enrichment asset.
type: project
---

**Status: SUPERSEDED — do not pursue.** Decision taken on 2026-04-08 after a product strategy rethink.

**Original concept (now dropped):** Free, sector-focused procurement intelligence web tool as top-of-funnel for BidEquity. Tussell-lite for Defence/Justice/Transport/Emergency Services. Public-facing search, buyer profiles, supplier profiles, expiring contract alerts, sector dashboards, auth-gated to capture lead identity.

**Why it was dropped:** The user concluded they do not want to ship a public-facing procurement lookup product. The strategic value of the lead-gen funnel via Qualify alone is sufficient; building a separate public intelligence tool was not the right use of effort.

**What replaces it:**
- **The competitive intelligence database lives on, but as an internal-only enrichment asset.** It exists to enrich the other platform products (Verdict post-loss forensics, Win Strategy competitor profiling, Bid Execution incumbent detection, future paid Qualify tier). It is not customer-facing.
- **Qualify lead gen ships deliberately under-enriched** — no procurement intel injection. See feedback_qualify_lead_gen_scope.md.
- **Online positioning** must explicitly state that the demo is intentionally limited and that the full product layers significant AI and market intelligence on top.

**What this kills (do not work on):**
- UX/UI/auth design for a public lookup tool
- Sector classification rules driven by free-tool requirements (note: sector classification might still be useful internally, but it's no longer a near-term priority)
- Email digest infrastructure (weekly alerts)
- User account / behavioural tracking infrastructure for a public product
- Public documentation of the data layer

**What survives (still valuable for internal use):**
- Continued investment in data depth, accuracy, completeness of pwin-competitive-intel
- Companies House enrichment (for Verdict and Win Strategy supplier profiling)
- Buyer entity resolution (so internal tools that ask about MoD get the full picture, not 1/1272 of it)
- Hetzner migration for durable nightly job
- Contracts Finder as second data source

**Why save this memory at all instead of deleting:** Because the rationale for *why* it was rejected matters. If the question comes up again ("should we build a public intel lookup?") future-me should know it was already considered and consciously declined, not just never thought of.
