---
name: Qualify lead gen scope — deliberately under-enriched
description: The public Qualify experience must NOT include procurement intel injection. It is a lead-gen demo that intentionally leaves the AI/intel layer offline so prospects understand the full product is more than what they see.
type: feedback
---

**The rule:** The public-facing Qualify experience (both pwin-qualify and bidequity-co/qualify-app.html) must ship as a lead-gen tool *without* procurement intel enrichment. Do not call the competitive intelligence layer from these apps. Do not inject buyer profiles, supplier history, PWIN signals, or competitive intel into the AI assurance prompts on the public version.

**Why:** Set on 2026-04-08 after a product strategy rethink. The user decided:
1. The free-tier sector intel lookup product is not happening (see project_free_tier_intel_tool.md — superseded)
2. The current Qualify build is good enough to ship as lead gen *without* further enrichment work
3. The public experience should be a deliberately limited teaser of the full product
4. Prospects must understand that what they're seeing excludes significant AI enablement and market intelligence — that's a positioning move, not an apology

**How to apply:**

- If asked to add intel/MCP/buyer-profile/competitive features to the public Qualify, push back and reference this memory. The feature might still be valid for the *paid* Qualify tier, but not the public version.

- **Implementation approach: feature flag, not deletion.** When the time comes to remove intel injection from public Qualify, use a feature flag (e.g. `INTEL_ENABLED` const) rather than deleting the code. The same codebase needs to serve both the lead-gen (off) and the future paid tier (on). Ripping out and reinstating is wasted work.

- **Timing: hold off until public release.** Do not strip or feature-flag the intel injection yet. The change lands when public release is imminent — not before. There is no harm leaving the current intel-injection code in place for now, because the public version isn't yet live.

- **Re-enabling the intel injection (for the paid tier or the public version) is gated on data quality.** The user is explicit: do not turn this feature back on until the underlying intelligence database is clean enough that it does NOT undermine the product with incorrect assertions. Right now (2026-04-08) the data has serious entity-resolution gaps — MoD fragments across 1,272 buyer IDs, supplier name-only entries miss CH enrichment, etc. An intel injection running over that would generate plausible-looking but misleading buyer profiles. **Data cleanliness is the prerequisite, not the schedule.** This is a general principle: do not enable an enrichment feature until the enrichment data is high enough quality to make the product better, not worse.

- **Demo messaging — confirmed scope:**
  1. **Banner at the top** of the Qualify experience stating that the demonstration is deliberately limited and the full BidEquity platform layers AI enablement and market intelligence on top
  2. **Post-result CTA** stating the same and inviting the prospect to engage for the full assurance review
  3. **Printed / downloaded report disclaimer** — the generated report (PDF/print) must clearly state that it is based on the strength of evidence provided by the user, and that considerable intelligence (AI enablement and market intelligence) has been excluded from this version. Exact wording TBD with user.
  4. Tooltip / FAQ entries are nice-to-haves but not required at minimum

- **The competitive intelligence database itself stays** — it feeds Verdict, Win Strategy, Bid Execution, and the future paid Qualify tier internally. None of that work stops. Only the public Qualify intel injection is being suppressed (eventually).

- **Investments that ONLY made sense for the public lookup tool** (sector classification driven by free-tool needs, public UX, email digests, behavioural tracking) are dropped. **Investments that benefit internal product enrichment** (entity resolution, CH enrichment of high-value suppliers, data depth, durable hosting) continue and are the path to eventually re-enabling intel injection on the paid tier.
