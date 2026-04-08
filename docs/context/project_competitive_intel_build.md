---
name: Competitive intel product built
description: pwin-competitive-intel full build 2026-04-06 — FTS ingest, CH enrichment, dashboard, MCP, D1 Worker, Qualify integration
type: project
---

pwin-competitive-intel product built and tested on 2026-04-06.

**Components built:**
- Ingest agent (Python stdlib) — FTS OCDS API, cursor pagination, multi-lot, multi-supplier
- SQLite schema — normalised: notices (OCID-keyed), lots, awards, award_suppliers, cpv_codes, planning_notices
- Companies House enrichment (agent/enrich-ch.py) — pulls status, directors, SIC codes, parent company, accounts. 236/5888 suppliers enriched so far. Needs COMPANIES_HOUSE_API_KEY env var.
- Query CLI — 8 commands: summary, buyer, supplier, expiring, pipeline, pwin, cpv, awards
- Dashboard (dashboard.html) — 6 tabs, expandable detail rows on pipeline/expiry, CH panel on supplier profiles
- Data server (server.py, port 8765) — local HTTP API for dashboard
- MCP tools — 7 read tools in pwin-platform/src/mcp.js via competitive-intel.js module (uses node:sqlite)
- Platform Data API — /api/intel/* endpoints in pwin-platform/src/api.js
- Cloudflare Worker (workers/intel-api.js) — serves same endpoints from D1 serverless SQLite
- D1 sync script (agent/sync-d1.py) — exports SQLite → SQL for wrangler d1 execute
- GitHub Actions updated — nightly: FTS ingest → CH enrichment (200/night) → D1 sync
- Both Qualify apps (pwin-qualify + bidequity-co/qualify-app.html) wired to fetch competitive intel before AI reviews

**Data layer state (2026-04-08, end of session):**
- Date coverage: **2021-01-01 → 2026-04-08** (5+ years), loaded from OCP bulk file
- 2025 notices are ~2.2x 2024 volume — real regulatory effect (Procurement Act 2023 commenced 24 Feb 2025, step-change visible in Apr-May 2025). Not a data error.
- Planning notices (forward pipeline) stay API-fed only — OCP compiled releases never represent pure planning-stage records
- Two historical backups exist in db/ — pre-OCP and pre-CH-fix — safe to delete once stable
- `agent/import_ocp.py` re-runs cleanly any time OCP refreshes (weekly)

**Product role (revised 2026-04-08):** Internal-only enrichment asset. Feeds Verdict (post-loss forensics), Win Strategy (competitor profiling), Bid Execution (incumbent detection), and the future paid Qualify tier. **It is NOT a customer-facing product.** The free-tier public lookup tool was considered and rejected — see project_free_tier_intel_tool.md (superseded). The lead-gen Qualify experience does NOT call this layer — see feedback_qualify_lead_gen_scope.md.

**Pending work, in priority order for next session:**

1. **Buyer entity resolution — #1 blocker.** MoD fragments across 1,272 distinct buyer IDs in the current data (PPON variants, GB-FTS legacy, case variants, MoD subsidiaries). A query for "Ministry of Defence" via a single buyer_id returns ~0.0003% of the real picture. Internal products that ask "tell me about buyer X" cannot give credible answers until this is resolved. Phase 1 plan: canonical buyer table for top 50 buyers manually mapped, plus a `canonical_buyer_id` column and aggregation view. ~1 day.

2. **Companies House name-matching for unidentified suppliers.** The c6ccbff extractor fix recovered structured CH IDs that publishers had stripped of scheme tags. The remaining gap is suppliers where there was *never* a CH ID in the OCDS record — only a name. Big UK companies like Babcock Land Defence, Frazer Nash, Kellogg Brown & Root sit in this gap. Recovering them requires fuzzy name matching against the Companies House register. ~1 day.

3. **Kick off CH enrichment for the ≥£5m high-value supplier set.** Extractor improvements in c6ccbff doubled the enrichable pool to ~13k suppliers with known CH numbers. At 200/night it's ~65 nights; at the CH free-tier max (~170k/day theoretical) it's one burst day. Decision needed: cadence and host.

4. **Move nightly incremental off Codespace to durable host.** Recommended: Hetzner CAX11, ~€5/mo, EU region. Codespace restart killed a long-running backfill mid-session. The nightly workflow is correctly wired to repo root `.github/workflows/ingest.yml` and fires at 02:00 UTC, but GitHub Actions cache-based state is fragile.

5. **Strip intel injection from public Qualify** (pwin-qualify and bidequity-co/qualify-app.html). The lead-gen demo must not call /api/intel/* — see feedback_qualify_lead_gen_scope.md. Confirm with user before changing.

6. **D1 deploy re-evaluation — DESCOPED in priority.** Was driven by production Qualify needing intel access. With Qualify intel-stripped, D1 only matters when other products start consuming intel in production. Still need to verify wrangler can load a 572 MB DB before any deploy attempt, but no longer urgent.

7. **GB-PPON crosswalk investigation.** PPON is the new UK org numbering system mandated by the Procurement Act. ~23k supplier appearances use it. If Cabinet Office publishes a PPON↔CH lookup, more enrichment unlocks. ~15 min to research.

8. **Sector classification rules — DROPPED unless re-justified.** Was a free-tier product prerequisite. Still potentially useful as an internal categorisation layer for Verdict/Win Strategy reporting, but no longer near-term.

9. **Contracts Finder API as second data source** (below-threshold contracts). Different schema, parallel ingest path. Lower priority — only useful if Verdict/Win Strategy users actually need below-threshold context.

10. **GitHub secrets to set (if not already):** COMPANIES_HOUSE_API_KEY, CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID.

**Dashboard access (Codespace):**
- Start server: `nohup python3 server.py > /tmp/server.log 2>&1 &`
- Access via Codespace Ports tab → port 8765 → /dashboard.html
- NOT localhost in browser (Codespace networking)

**Key design decisions:**
- Qualify auto-detects: localhost → platform API (3456), production → Worker URL
- Intel fetch fails silently — enriches but doesn't gate AI reviews
- 5-min cache per organisation name
- Server API transforms DB column names to match dashboard field names
- CH enrichment rate limited to 600ms between calls, 200/night in CI
- FTS API needs 1s delay between pages to avoid 429s; full historical ingest needs overnight run

**Why:** Cross-cutting intelligence layer feeding Qualify AI assurance context, Win Strategy competitor profiling, and sales pipeline prospecting.
