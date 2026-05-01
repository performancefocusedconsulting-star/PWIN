# Design: Wire Missing Intelligence Feeds into Qualify's Prompt Builder

**Date:** 2026-05-01
**Status:** Approved — ready for implementation planning

---

## Problem

When Qualify was originally built, the intelligence platform did not exist. The app assembles a system prompt for Alex Mercer, but it only enriches that prompt with two data sources:

1. A buyer procurement profile (total awards, spend, method mix, top suppliers)
2. Competition signals (average bidders per tender, method breakdown)

Qualify already collects everything it needs to ask for more — the buyer's name, the sector, the opportunity type, and the names of competitors. It just doesn't use them to pull additional context back from the platform. The result is that Alex receives a thin procurement sketch when a multi-dimensional intelligence picture is now available.

---

## Scope

**File changed (Qualify app):** `pwin-qualify/docs/PWIN_Architect_v1.html`

**File changed (platform):** `pwin-platform/src/api.js` — one new HTTP endpoint added.

**Not touched:** `bidequity-co/qualify-app.html` (website public version). That app has its intel calls suppressed for the public launch and stays as-is. `pwin-qualify/content/` and the build scripts are not touched. The `{{COMPETITIVE_INTEL_PLACEHOLDER}}` prompt placeholder name is not changed.

---

## Architecture

### Approach: split feed functions with a thin orchestrator

`fetchCompetitiveIntel()` is refactored from a single monolithic function into a thin orchestrator. It calls six independent feed functions in parallel, waits for all of them, then stitches their results into one labelled block. Each feed function is self-contained: it knows its own endpoint, its own response parsing, and its own formatting. A feed that returns nothing contributes nothing to the block.

```
fetchCompetitiveIntel()          ← orchestrator, unchanged name and signature
  ├── fetchBuyerProfile(org)     ← existing logic, extracted
  ├── fetchPwinSignals(org)      ← existing logic, extracted
  ├── fetchSectorContext(sector) ← new
  ├── fetchCompetitorProfiles(competitors) ← new
  ├── fetchForwardPipeline(org)  ← new
  └── fetchExpiringContracts(org) ← new
```

All six run via `Promise.all`. Total wall-clock time is bounded by the slowest single call, not the sum of all calls.

---

## New Platform Endpoint

**`GET /api/intel/sector?name={sector}`**

The underlying function `compIntel.sectorProfile(sectorName)` already exists in the database layer. This route exposes it over HTTP so the Qualify app can call it. Implementation is a single route registration in `pwin-platform/src/api.js`, consistent with the pattern used by `/api/intel/buyer`, `/api/intel/supplier`, and `/api/intel/pwin`.

Returns sector-level procurement statistics from the database: contract volumes, typical award values, most active buyers in the sector.

---

## The Six Feed Functions

### 1. `fetchBuyerProfile(org)` — extracted from existing code
No logic change. Calls `/api/intel/buyer?name={org}`. Returns the buyer procurement profile block: total awards, total spend, average value, average bidders, procurement method mix, top five suppliers. Returns `''` if no match or platform offline.

### 2. `fetchPwinSignals(org)` — extracted from existing code
No logic change. Calls `/api/intel/pwin?buyer={org}`. Returns competition intensity signals. Returns `''` if no match or platform offline.

### 3. `fetchSectorContext(sector)` — new
Calls `/api/intel/sector?name={sector}`. Returns sector-level procurement patterns: volume of contracts awarded in this sector, typical award values, most active buyers. Gives Alex a sense of whether this buyer's behaviour is typical or anomalous for their sector. Returns `''` if no match or platform offline.

### 4. `fetchCompetitorProfiles(competitors)` — new
Takes `state.context.competitors` (comma/semicolon-separated string), splits into individual names, fires one `/api/intel/supplier?name={name}` call per competitor in parallel. For each competitor found, builds a brief: total wins, total contract value, strongest buyer relationships. Competitors not found in the database are silently skipped. If no competitors are named, or none are found, returns `''`.

### 5. `fetchForwardPipeline(org)` — new
Calls `/api/intel/pipeline?buyer={org}`. Returns up to five planning notices (upcoming tenders the buyer has signalled). Each entry: opportunity title, estimated value, expected publication date. Gives Alex a forward-looking view of the buyer's priorities. Returns `''` if no results or platform offline.

### 6. `fetchExpiringContracts(org)` — new
Calls `/api/intel/expiring?buyer={org}&days=365`. Returns up to five contracts this buyer holds that expire within 12 months, including the current supplier (incumbent) for each. Gives Alex a factual basis for challenging on incumbent risk and competitive timing. Returns `''` if no results or platform offline.

---

## Graceful Degradation

Every feed returns either a formatted text block or `''`. The orchestrator assembles only the non-empty blocks. If the platform is offline, all feeds return `''` and Alex receives an unenriched prompt — exactly as before this change. No errors surface to the user.

If a supplier or buyer name typed by the consultant does not match anything in the database, the corresponding feed returns `''` and that section is absent. No false information is introduced.

---

## Canonical Name Resolution

Name matching is the platform's responsibility, not Qualify's. The app passes whatever the consultant typed and the platform resolves it.

**Buyers:** `buyerProfile()` was rewired through the canonical buyer alias layer on 2026-04-28. Typing "MoJ" or "Ministry of Justice" should already aggregate across all sub-organisations (HMCTS, HMPPS, etc.).

**Suppliers:** During implementation, verify whether `supplierProfile()` routes through the canonical supplier layer (`supplier_to_canonical` join). If it still does a plain name match, fix it at that point so "Serco" aggregates across all Serco entities in the database. This is a platform-side fix — the Qualify app changes nothing.

The principle: Qualify sends the name as typed. The platform handles resolution. All callers benefit automatically.

---

## Output Format

The assembled block is a single string substituted for `{{COMPETITIVE_INTEL_PLACEHOLDER}}` in the system prompt. Sections are ordered from most established (historical buyer behaviour) to most forward-looking (upcoming pipeline). Sections with no data are omitted entirely — no empty headers.

```
PROCUREMENT INTELLIGENCE — Buyer Profile:
Buyer: Ministry of Justice (central_government)
Awards in database: 342 | Total spend: £1.4bn
Average award value: £4.1m
Average bidders per tender: 4.2
Procurement methods: open: 120, restricted: 98, direct: 44
Top suppliers:
  - Serco: 38 awards, £1.4bn total
  - Capita: 12 awards, £280m total
  ...

PROCUREMENT INTELLIGENCE — Competition Signals:
Competition level: 342 awards tracked
Average bids per tender: 4.2
Method breakdown: open=120, limited=98, direct=44, selective=12

SECTOR CONTEXT — Central Government:
[sector-level volume and value statistics from the database]

COMPETITOR PROFILES:
Serco: 38 wins at Ministry of Justice, £1.4bn total. Strongest relationships: HMPPS (22 wins), HMCTS (11 wins).
Capita: 12 wins at Ministry of Justice, £280m total. Strongest relationships: Legal Aid Agency (8 wins).

FORWARD PIPELINE — Upcoming tenders for this buyer:
- Prisoner rehabilitation services: est. £45m, expected publication June 2026
- Court digital services framework: est. £120m, expected publication August 2026

EXPIRING CONTRACTS — Contracts ending within 12 months:
- Prisoner escorting services (Serco, £95m) — expires September 2026
- Legal aid digital services (Capita, £22m) — expires January 2027
```

Section labels are explicit so Alex can treat each as a distinct source when forming challenges rather than drawing from an undifferentiated wall of text.

---

## Caching

The existing 5-minute cache (keyed on `org`) is extended to key on `org + sector + competitors`. If any of the three change (different buyer, different sector, different competitor list), the cache is invalidated and a fresh set of calls fires.

---

## What Does Not Change

- The `{{COMPETITIVE_INTEL_PLACEHOLDER}}` placeholder name in the system prompt
- The call site: `buildPersonaPrompt(schema).replace('{{COMPETITIVE_INTEL_PLACEHOLDER}}', intelBlock)`
- The website public version (`bidequity-co/qualify-app.html`)
- The content build system, eval harness, or any other Qualify file
- All existing scoring, category, and persona logic
