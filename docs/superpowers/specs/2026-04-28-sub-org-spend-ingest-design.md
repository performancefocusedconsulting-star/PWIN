---
title: Sub-organisation spend ingest — design
date: 2026-04-28
status: draft
project: pwin-competitive-intel
related:
  - wiki/actions/pwin-sub-org-overlay-layer.md
  - wiki/platform/sub-org-data-coverage.md
  - docs/research/2026-04-28-sub-org-intel-sources.md
  - docs/research/2026-04-28-sub-org-contract-registers.md
  - pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md (§18)
---

# Sub-organisation spend ingest — design

> **Plain-language design** for the £25,000 spend transparency ingest. The reader is a senior consultant who runs a bid business, not a database engineer. Technical details are referenced where needed but the design is written to be reviewable without engineering background.

## Why this work exists

Roughly 5% of UK central-government contract awards (about 22,000 of 447,000) are dark at sub-organisation level because four ministerial departments — Ministry of Justice, Home Office, Department for Education, and Ministry of Defence — publish their contract notices under the parent name with no breakout for the executive agency that's actually doing the procuring. The buried sub-organisations include UK Visas and Immigration, Border Force, HM Passport Office, Immigration Enforcement, HM Prison and Probation Service, HM Courts and Tribunals Service, the Education and Skills Funding Agency, Defence Digital, and the service commands (Strategic Command, the Army, Royal Navy, RAF).

This 5% slice covers the highest-value consulting pursuits in central government. Without dossier-grade data on these sub-organisations, the buyer-intelligence skill produces thin output for exactly the buyers that matter most.

The Procurement Act 2023 does not fix this. The buyer field on every notice is still freeform and inherits departmental publishing practice. Closing the gap requires an overlay layer that draws on data sources outside the contract-notice feed. Five waves are listed in the action note `wiki/actions/pwin-sub-org-overlay-layer.md`. **This design covers Wave 1, Item 1: ingest of the £25,000 spend transparency files for the four publish-at-parent families.**

A separate companion thread (the canonical-layer tidy-up, committed earlier on 2026-04-28) added the Education and Skills Funding Agency as a new canonical entity and closed eight residual alias gaps for the four families. That work is now complete. This design starts where it ends.

## Decisions captured during the design walkthrough

Five significant choices were made during the brainstorming session. Each is recorded here so future readers know the choice was deliberate, not an oversight.

### Decision 1 — Headline capability

The £25k spend feed will power **per-sub-organisation ranked supplier-spend tables** for the four publish-at-parent families. A consultant asking the buyer-intelligence skill for a UK Visas and Immigration dossier (or HM Prison and Probation Service, or any of the priority sub-organisations) will see a "spending signal" section showing who that body's biggest suppliers are over the last five years, ranked by total spend.

Two adjacent capabilities were considered and **rejected for v1**:

- A supplier-side cross-cut ("all sub-orgs that pay Capita"). Same data supports it; we will add a thin MCP-tool wrapper later if the demand surfaces.
- End-date sanity-checking on existing notice contracts. The research catalogue rates this at 50–60% accuracy. Too noisy to expose to a client-facing dossier without per-contract confidence work.

### Decision 2 — Department scope

Wave 1 covers **only the four publish-at-parent families** (Ministry of Justice, Home Office, Department for Education, Ministry of Defence). Other central-government departments (Department for Transport, Department for Science Innovation and Technology, Foreign Commonwealth and Development Office, etc.) already attribute their notices correctly via Find a Tender — adding their spend would be duplicative for the headline capability.

The schema and parser are nevertheless designed to be **department-agnostic**, so adding a fifth, sixth, twentieth department later is a configuration change (one new entry in the catalogue file plus a column-mapping handler), not a schema change.

This is a deliberate deferral, **not an oversight**. Wider ingest may be revisited when paid Qualify or Win Strategy explicitly need cross-department spend data for departments outside the four families.

### Decision 3 — Permissive ingest with strict render

Every spend row gets stored. Rows whose entity column doesn't map cleanly to a known canonical sub-organisation are kept with a flag rather than dropped. The data layer is permissive.

The render layer is strict. Client-facing dossier output **never** shows raw publisher-side text. Anything that didn't canonicalise gets aggregated into a single tidy line — for example "Home Office — other directorates not at sub-organisation level: £41m (4.2% of family)". The consultant always sees how much sits in the residual; the client never sees ugly publisher-side spelling.

This protects report quality while keeping the data complete. We grow the canonical layer evidence-driven: when a directorate-level entity name accumulates enough volume to warrant a canonical entry, it gets one (with a `type: Directorate` flag so it doesn't pollute the sub-organisation list). New entries surface in the weekly review queue (described under Operational layer below).

### Decision 4 — Time horizon

We ingest **the last five years** of spend across the four families. Roughly 1,800 monthly files, about 5–10 million payment rows.

Five years matches typical Find a Tender contract lifespan, captures one full supplier rotation (incumbent intelligence signal), and stops short of pre-2020 body-name churn (Office for Students didn't exist before 2018, ESFA was formed in 2017 from a merger). Older history can be added later by re-running the ingest with an earlier start date — the design supports that.

### Decision 5 — Architectural shape

The spend data lives in the existing `bid_intel.db`, alongside notices and awards. The spend signal surfaces as a new section inside the existing `get_buyer_profile` MCP tool — no new tool, no new database file, no new operational surface.

This was chosen over two alternatives: (a) a separate `spend.db` file with cross-database joins, rejected because the separation is aesthetic rather than functional and the cross-database query pattern adds complexity without benefit; (b) a separate MCP tool `get_sub_org_spend_profile`, rejected because folding into `get_buyer_profile` means consumers (the buyer-intelligence skill) immediately benefit without a code change.

If the demand for a standalone tool surfaces later, it would be a thin wrapper over the same tables.

## What the system does, end to end

### Section 1 — Components and data flow

Six pieces, all in `pwin-competitive-intel/`:

1. **Static catalogue file** — a single JSON text file in the repo listing every monthly spend file we want, organised by department and date. Roughly 1,200–1,500 entries.
2. **Download script** — reads the catalogue, fetches each file from gov.uk politely (1-second delay between files), records each completed download via a checksum bookmark, retries on failure, resumable.
3. **Local file cache** — raw downloaded files saved to `data/spend/<dept>/<YYYY-MM>.csv`, gitignored, kept locally so we don't re-download when fixing the parser.
4. **Reader / parser** — four small format handlers (one per department family) that pull supplier, amount, date, and entity into a uniform row format. The rest of the pipeline never sees the raw file shape.
5. **Canonicalisation pass** — a second script that walks new payment rows and matches supplier names to the canonical supplier list (the 82,637-entity Splink layer) and entity names to the canonical sub-organisation list (which extends `canonical_buyer_aliases` from the existing canonical layer).
6. **Surface** — the spend signal flows into `get_buyer_profile` as a new section. `get_buyer_profile` is a tool inside the PWIN platform (a "Model Context Protocol" tool — the platform's standard way of exposing a query to the buyer-intelligence skill running from Claude.ai). The skill consumes the new section via the existing tool, with no consumer code change.

### Section 2 — What we store

Two new tables in `bid_intel.db`, plus a small extension to an existing one.

**Table A — `spend_transactions`.** One row per payment over £25,000. Columns include the source department, raw entity column value, raw supplier name, amount, payment date, expense category, source file reference, plus two canonicalisation pointer columns (`canonical_sub_org_id` and `canonical_supplier_id`). Pointer columns are populated by the canonicalisation pass; rows where they remain NULL are flagged "uncanonicalised" and handled by the strict render rule.

**Table B — `spend_files_state`.** One row per spend file we've ever loaded. File path, source URL, checksum, loaded-at timestamp, row count, parser version. Same pattern as the existing OCDS bookmark table. Re-running the ingest skips files we already have.

**Extension — `canonical_buyer_aliases`** (existing table, no schema change). New rows get added covering spend-side variants of sub-organisation names (e.g. "UK Visas and Immigration", "UKVIP", "HMPPS"). Same matching machinery as the contract-notice ingest. The buyer canonical layer benefits from every spend-side alias automatically.

No schema changes to existing tables — `notices`, `awards`, `suppliers`, `buyers`, `canonical_buyers`, `canonical_suppliers` all stay exactly as they are today.

### Section 3 — Finding and downloading the files

A static catalogue, not a scraper. Each entry in the catalogue carries department, year, month, the file URL on gov.uk, and the column-format identifier the file uses.

Why static catalogue rather than scraper: the gov.uk collection pages restructure periodically, file names don't follow a predictable pattern, and chasing those moving targets with a scraper is fragile. A flat catalogue is more honest to maintain — a missing month is one entry to fix; a renamed file is one URL to update.

The catalogue is refreshed annually. Per the Operational layer (Section 4 below), the annual refresh is a scheduled background agent, not a manual task.

### Section 4 — Operational layer (the human-in-the-loop concern)

This section captures a specific concern raised during the design: with many other priorities, the consultant cannot rely on remembering to do periodic manual maintenance work. The OCDS daily ingest experience has demonstrated that the failure mode is forgetting to check that an automated job worked.

**Three things in earlier drafts secretly required the consultant to remember to act. Each is removed by design:**

**A. Annual catalogue refresh** — implemented as a scheduled recurring background agent (created via the `/schedule` mechanism) that fires on 1 March every year. The agent walks each department's gov.uk transparency-spend collection page (one for Home Office, one for MoD, one for DfE, plus the multiple MoJ pages — MoJ HQ, HMCTS, and the eleven arm's-length-body pages), finds new file URLs that have appeared since the last refresh, either auto-updates the catalogue when the file naming follows the previously-seen pattern, or sends a one-paragraph email summary asking for human review when something looks novel. The consultant does not book a calendar slot.

**B. Monthly download health check** — the monthly download runs inside the existing `scheduler.py` that already executes the contract-notice ingest, Companies House enrichment, and the daily pipeline scan. After the run, a one-line health summary is appended to the **same digest email** the consultant already reads each morning. Format:

> Spend ingest health for 2026-04: 30 of 30 streams refreshed. 0 download failures. 1,847 new payment rows. 4.2% unmapped share (within tolerance). 2 new entity names detected — review queue updated.

If any threshold trips (download failure, unmapped share above 10%, parser failure, missing month), the line flips to a red flag in the digest. Same flag mechanism as the existing daily pipeline scan.

**C. Quality / canonicalisation review** — two markdown files auto-regenerated weekly inside the wiki:
- `wiki/intel/spend-health.md` — green/amber/red status per family on one screen. If everything is green, the consultant skims it in 5 seconds.
- `wiki/intel/spend-alias-review-queue.md` — the list of new high-volume entity-column values that didn't canonicalise, each with a suggested canonical match. The consultant spends ten minutes a week saying yes/no/skip in the file; a script picks up the decisions and updates the alias list.

**Threshold rules (defined upfront, not discovered later):**
- Download failure of any file → immediate red flag in the digest.
- Unmapped share above 10% for any family → amber until reviewed.
- New entity name accumulating more than £1m in spend without a canonical match → amber until reviewed.
- Parser failure on any file → red flag with the file name and error.

**Net check-and-balance burden on the consultant:** read the existing daily digest line (5 seconds), click the alias review queue once a week (~10 minutes). Annual refresh, monthly download, weekly health check all happen on schedule whether the consultant is paying attention or not, and surface in places they are already paying attention to.

### Section 5 — Reading and matching (parsing and canonicalisation)

**Parsing.** Each department writes its files in a slightly different shape. Home Office uses a clean "Entity" column. Ministry of Justice publishes thirteen separate streams (one per arm's-length body) — for those, the sub-organisation is in the file name, not in a column. Ministry of Defence uses "Top Level Budget" with values at department-grade rather than sub-organisation-grade granularity. Department for Education has its own column conventions.

The reader has one small handler per format — four handlers — and each one knows how to pull supplier, amount, date, and entity into the uniform row format. The rest of the pipeline never sees the raw file shape.

Why this is not fragile: departments do not restructure their files arbitrarily. Once a format is set up it stays consistent for years. If something does break (a column name changes, a new file format appears), the parser fails loudly, the row is not silently corrupted, and the morning digest email shows red. We do not lose data; we simply do not process the affected month until the parser is updated.

**Canonicalisation.** A second pass walks new payment rows and matches supplier name to canonical_suppliers (using the same exact-and-normalised matching logic as the existing canonical layer) and entity name to canonical_buyers (via canonical_buyer_aliases). Most matches are easy: "ATOS IT SERVICES UK LTD" in spend versus "Atos IT Services UK Ltd" in our canonical list — same company after a casing normalisation. The trickier rows (foreign supplier variants, trading names, government-body-as-supplier) get flagged and surface in the weekly review queue.

First full ingest of 5 years across the four families is roughly 5–10 million payment rows. Canonicalisation pass takes 10–20 minutes on the local laptop. One-off cost; subsequent monthly passes are tiny because they only need to re-canonicalise rows the alias list has changed for.

### Section 6 — What the consultant sees in a dossier

Today, asking the buyer-intelligence skill for a dossier on UK Visas and Immigration produces a thin output. There are almost no contract notices in the database that name UKVI as the buyer — UKVI's contracts are nearly all filed under "Home Office". Today's dossier is mostly narrative cross-reference (annual reports, NAO findings) without hard supplier data.

After this design lands, the same dossier request returns a new section in the data the skill receives. Indicative shape:

> **Spending signal — UK Visas and Immigration (last 5 years, source: £25k spend transparency feed)**
>
> | Rank | Supplier | Total spend | Last paid | Direction |
> |---:|---|---:|---|---:|
> | 1 | Atos IT Services UK Ltd | £342m | 2026-03 | ↑ |
> | 2 | Capita Plc | £198m | 2026-03 | → |
> | 3 | Mastek UK Ltd | £156m | 2026-04 | ↑ |
> | 4 | Sopra Steria Ltd | £89m | 2026-02 | ↓ |
> | 5 | Mitie Group Plc | £67m | 2026-04 | → |
> | … | | | | |
>
> *(numbers indicative only)*
>
> Coverage: 94% of UKVI-family spend canonicalised. £41m sits under directorate-level publishers (Migration and Borders Group, Asylum Support) and is not attributed at sub-organisation level.

The buyer-intelligence skill's existing prompts already know how to reason about supplier concentration, incumbent dominance, and recent rotation. They simply could not see the data before — now they can.

**Two protections** for client-facing reports:

1. The coverage footer always shows. The consultant sees how much is unmapped, every time, and can quote figures with full transparency.
2. No raw publisher-side text leaks into client output. Everything that did not canonicalise gets aggregated into one tidy "—other directorates" line. The consultant sees the residual size; the client never sees ugly text.

**Where this lands across the four families:**

- **For sub-organisations that already publish in their own name on Find a Tender** (HMPPS, HMCTS, DE&S, Dstl, DIO, SDA, the four MoJ arm's-length bodies that publish, etc.) — the spend section is a *confirmation overlay* alongside the existing notice-derived data. Lets the consultant cross-check incumbent claims.
- **For the four buried Home Office sub-organisations** (UKVI, Border Force, HMPO, Immigration Enforcement) — this is the only structured incumbent data we will ever have. The dossier transforms from thin to genuinely useful.
- **For Defence Digital** — partial gain only. The MoD £25k feed rolls up to Strategic Command; Defence Digital is buried at this aggregation level. The fix for Defence Digital is the NISTA major projects feed (Wave 1, Item 2 in the action note), a separate workstream.

## Success criteria

Six things, each easy to check:

1. First-time full ingest completes without errors for all four families across the 5-year window.
2. At least 85% of family spend canonicalises (maps cleanly to a known sub-organisation). Below 85% means the canonical layer needs more work before the dossier is ready for that family.
3. A sample dossier generated for UK Visas and Immigration carries a meaningful supplier-spend section with a coverage footer. Same for HM Prison and Probation Service, Defence Digital, and the Education and Skills Funding Agency. Copies can be inspected before declaring done.
4. The morning digest email carries the new spend-health line, and a deliberately-broken file (testing) flips it red.
5. The weekly alias-review queue regenerates without intervention; new high-volume entity values surface for triage.
6. The annual catalogue-refresh agent is scheduled and confirmed-firing in March 2027.

## What we deliberately did not do (audit trail)

Each line records something considered, **rejected for v1**, recorded so future readers know the choice was deliberate.

| What we did not do | Why |
|---|---|
| Ingest spend for departments outside the four publish-at-parent families | Their notices already attribute correctly — adds duplicative data with no headline-capability gain. Schema and parser are department-agnostic so adding them later is a configuration change. |
| Pre-build canonical entries for directorates and policy units (Migration and Borders Group, Asylum Support, etc.) before ingest | Per the permissive-ingest decision: let the data tell us which directorates carry enough volume to warrant canonical entries. Strict render rule protects client output in the meantime. |
| Try to infer contract structure (title, total value, start, end date) from spend rows | Research catalogue §6.3: supplier identity 85–95% achievable but contract structure cannot be derived from payment data. Open Contracting Partnership has explicitly said this is hard. We stay payment-by-payment only. |
| End-date sanity-checking on notice contracts ("notice says 2027 but no payments since 2025-Q3") | 50–60% accuracy without per-contract confidence work — too noisy for a client-facing dossier. Reconsider when we have the confidence work to back it. |
| Supplier-side cross-cut queries ("all sub-orgs that pay Capita") as a headline view | Same data supports it; future MCP tool is a thin wrapper. Not a v1 capability — keeps surface focused on the headline. |
| Fix Defence Digital below Top Level Budget level | MoD £25k feed rolls up to Strategic Command; Defence Digital is buried. The fix is the NISTA major projects feed (Wave 1, Item 2 in the action note) — separate workstream. |
| Cover single-source defence contracts (SSRO regime) | Not in any spend feed at any granularity. The data does not exist publicly. NAO/PAC/trade press partial coverage only. |
| Buy a Tussell or Stotles subscription | Wave 4 in the action note. Trial decision after Waves 1–3 are landed and we know the residual gap. |

## Known limitations that remain after v1

These are honest limits we will carry, not bugs to fix. Each surfaces explicitly in the dossier footer so consultants do not misquote.

- **Spend is not contracts.** Total spend per supplier is a *lower bound* on contract value (it can grow via change notices we do not see) and the start date is the first material payment, which often lags contract signature by months. The dossier footer makes this explicit so consultants do not quote spend numbers as contract values to clients.
- **1–3 month publisher lag.** Departments publish their spend with a 1–3 month delay. A brand-new £100m programme would only show up in our data months after the contract was signed — the contract notice on Find a Tender comes first. Flagged in the dossier footer.
- **Defence Digital incumbent map remains thin** at this layer. Closing it requires the NISTA major projects feed (Wave 1, Item 2).
- **Pre-2020 body-name churn** (Office for Students did not exist, ESFA was formed in 2017 from a merger of two predecessor bodies). The 5-year window stops short of the worst churn, but the consultant should know spend before approximately 2018 carries old body-name attribution that may not match today's canonical entries.
- **Supplier canonicalisation is imperfect.** The existing 82,637-entity Splink layer covers most named UK suppliers cleanly, but foreign supplier variants ("Microsoft Ireland Operations Limited"), trading names, and government-body-as-supplier rows have higher unmapped rates. Surface in the weekly review queue.

## References

- Action note: `wiki/actions/pwin-sub-org-overlay-layer.md` (the parent action; this design covers Wave 1, Item 1)
- Executive summary: `wiki/platform/sub-org-data-coverage.md`
- Source catalogue research: `docs/research/2026-04-28-sub-org-intel-sources.md`
- Contract-register research: `docs/research/2026-04-28-sub-org-contract-registers.md`
- Canonical layer playbook: `pwin-competitive-intel/CANONICAL-LAYER-PLAYBOOK.md` (especially §17, §18)
- Companion canonical-layer tidy-up: commit `0dbc8e2` (ESFA + 8 alias variants, 2026-04-28)
