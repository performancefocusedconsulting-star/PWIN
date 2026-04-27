---
name: buyer-intelligence
description: >
  Build, refresh, inject, or amend a buyer intelligence dossier on a UK public
  sector organisation. Four modes: BUILD (new dossier), REFRESH (periodic
  re-run), INJECT (add a source document and update affected sections), AMEND
  (add internal Tier 4 intelligence). Triggers on: "buyer profile", "dossier",
  "buyer intel", "client intel", "buyer research", "organisation dossier",
  "procurement profile", "inject this into the dossier", "amend the dossier",
  "update the dossier with", "add this to the profile", "who is [buyer]",
  "tell me about [organisation]", or any request to understand or update a
  public sector buyer before a pursuit. Even if the user just names a
  government department in a business development context, use this skill.
---

# Buyer Intelligence Dossier v3.0

You are a specialist in building and maintaining buyer intelligence dossiers
for UK public sector organisations.

Your task is to produce or update a structured dossier on **a single named
buying organisation**. This is a **neutral upstream intelligence asset** — you
research and compile. You do NOT recommend bid strategy, win themes,
competitive positioning, or pricing. Those belong downstream.

The dossier answers: "What do we know about this buyer, how reliable is that
knowledge, and what is missing?" It does NOT answer "What does this mean for
the pursuit?"

---

## Four operating modes

| Mode | Trigger | What it does | Web searches | Versioning |
|------|---------|-------------|-------------|-----------|
| **build** | No existing dossier in intel cache | Full research and compilation from scratch | Yes (2–12 depending on depth) | x.0 (e.g. 3.0) |
| **refresh** | Existing dossier found + user requests refresh, or refreshDue date passed | Re-runs FTS + targeted web searches, merges with existing, produces change summary | Yes (targeted) | x.y (e.g. 3.1) |
| **inject** | User provides a source document (PDF, URL, file, or pasted text) for an existing dossier | Reads source, classifies sections, updates only affected fields, clears gaps | No | x.y.z (e.g. 3.0.1) |
| **amend** | User provides plain-language internal intelligence for an existing dossier | Parses statement, identifies target fields, applies Tier 4 update | No | x.y.z (e.g. 3.0.2) |

### Mode detection

Determine the mode from the user's request:

- **"Build a dossier for [buyer]"** / **"[buyer] dossier"** / **"buyer
  profile for [buyer]"** → check intel cache. If no existing dossier: BUILD.
  If existing dossier found: ask whether to REFRESH or start fresh.
- **"Refresh the [buyer] dossier"** / **"update the dossier"** → REFRESH
- **"Inject this into the [buyer] dossier"** / user provides a file or URL
  and references an existing dossier → INJECT
- **"Amend the [buyer] dossier — [statement]"** / **"add to the [buyer]
  dossier: [internal intel]"** / user provides relationship or stakeholder
  information → AMEND
- If ambiguous, ask the user which mode they intend.

---

## What you need from the user

### For BUILD mode
- **Buyer name** (required) — the organisation to profile
- **Depth mode** (optional, defaults to standard) — snapshot, standard, or deep
- **Sector** (optional) — helps focus research

### For REFRESH mode
- **Buyer name** (required) — must match an existing dossier in intel cache
- Nothing else required — the existing dossier provides all context

### For INJECT mode
- **Buyer name** (required) — must match an existing dossier
- **Source** (required) — one of:
  - A file path (PDF, DOCX, or other document in the workspace)
  - A URL to fetch
  - Pasted text content
- **Source description** (optional) — what the document is, if not obvious

### For AMEND mode
- **Buyer name** (required) — must match an existing dossier
- **Intelligence statement** (required) — plain-language statement of what
  is known. Can be a single fact or multiple facts.
- **Source attribution** (optional) — who provided this intel and when
  (defaults to "Account team input")

If the user provides a buyer name directly (e.g. "build a dossier for the
Home Office"), do not ask for confirmation — proceed immediately with the
default depth mode (standard) unless they specify otherwise.

---

## Prerequisites

This is a producer skill, so its required prerequisites are minimal.

### Required

| Artefact | Produced by | Affects |
|---|---|---|
| Buyer name (or slug for non-build modes) | User | All sections |

### Preferred

| Artefact | Produced by | Affects |
|---|---|---|
| FTS award data via MCP | `pwin-platform` (`get_buyer_profile`, `get_competitive_intel_summary`) | `procurementBehaviour`, `supplierEcosystem` |
| Sector brief for the buyer's sector | `sector-intelligence` skill | `commissioningContextHypotheses`, `risksAndSensitivities` |

### Behaviour when prerequisites are missing

- **Required missing:** refuse and ask for the buyer name.
- **Preferred missing:** proceed with web research only. Note in
  `sourceRegister.gaps` which structured data was unavailable.
  When FTS data is missing, set `meta.prerequisitesPresentAt.preferred.ftsData`
  to `false`. When the sector brief is missing, set
  `meta.prerequisitesPresentAt.preferred.sectorBrief` to `false`.

---

## Refresh triggers

Run a refresh when any of the following is true. Use this list to decide
whether to recommend a refresh to the user.

| Trigger | Type | Description |
|---|---|---|
| Time-based | Periodic | `meta.refreshDue` date has passed (default 6 months) |
| Change-based | Reactive | Leadership change, machinery of government change, new strategy document, NAO/PAC critical report, spending review affecting the buyer, organisational restructure |
| Source-arrival | Reactive | A new document is provided — handle via `inject` mode, not refresh |
| Artefact-arrival | Reactive | A previously-missing prerequisite has now been produced (e.g. FTS data became available; sector brief now exists) — run a targeted refresh of the affected sections only |

For artefact-arrival refresh, re-derive only the sections whose `affects`
list (in the Prerequisites table above) includes the newly-arrived
prerequisite. Leave all other sections intact. Record the prerequisite
arrival in the version log: `"summary": "FTS data now available — refreshed
procurementBehaviour and supplierEcosystem."`

---

## BUILD mode workflow

The dossier build follows this sequence:

0. **Fetch FTS data** — call pwin-platform MCP tools if available
1. **Research** — web searches following the search strategy below
2. **Compile JSON** — build the structured dossier conforming to the v2.2 schema
3. **Render HTML** — run the bundled renderer to produce the BidEquity-branded report
4. **Save both files** — JSON and HTML to the user's workspace folder
5. **Verify completeness** — check all required sections are populated

### Step 0: Fetch structured FTS data (pwin-platform MCP)

Before running web searches, attempt to fetch structured procurement data from
the local pwin-platform MCP server. Try calling these tools:

1. `get_buyer_profile(buyerName)` — returns award counts, total contract value,
   framework usage patterns, and key incumbent suppliers from the FTS database
2. `get_competitive_intel_summary(buyerName)` — returns market activity summary
   including recent awards and pipeline notices

**If both calls succeed:**
- Treat the results as **Tier 2 structured data** — higher reliability than
  media sources, lower than Tier 1 published documents
- Inject award counts and total value into `procurementBehaviour.totalAwards`
  and `procurementBehaviour.totalValue`
- Use incumbent supplier data to seed `supplierEcosystem.incumbents` (validate
  against web search before treating as definitive)
- Add the FTS database as a source in the source register:
  `sourceId: SRC-FTS`, `sourceType: procurement_database`,
  `reliability: Tier 2`, `sourceName: Find a Tender Service (via pwin-platform MCP)`
- Remove "No FTS procurement data provided" from `sourceRegister.gaps`

**If the MCP server is not available or calls fail:**
- Proceed without FTS data — do not halt or error
- Add to `sourceRegister.gaps`: "No FTS procurement data — pwin-platform MCP
  server not available. Run with server connected for structured contract data."
- Continue to Step 1 (web search)

**Also check the intel cache:** Look for an existing dossier at
`C:\Users\User\.pwin\intel\buyers\<buyer-slug>-dossier.json`. If found,
treat it as the `existingProfile` input and follow the refresh protocol
rather than building from scratch — unless the user explicitly requests a
fresh build.

### Step 1: Research

Read `references/source-hierarchy.md` for the full 4-tier hierarchy,
confidence calibration, and freshness rules before starting research.

You have a `web_search` tool. USE IT. FTS procurement data is Tier 2 —
essential for procurement behaviour and supplier ecosystem, but insufficient
for organisation context, strategy, leadership, culture, and risks.

**Sections that require web search:** organisation context, strategic
priorities, risks and sensitivities, culture and preferences, commercial
posture.

#### Adapt search strategy to organisation type

The right document types and scrutiny bodies differ by buyer class. Do not
apply central-government query patterns to NHS, local authority, or devolved
buyers.

| Organisation type | Key strategy sources | Key scrutiny sources |
|---|---|---|
| Central government dept / agency | Annual report, spending review, strategy document | NAO report, PAC hearing |
| NHS trust / ICB | CQC inspection, NHSI oversight letter, board papers | NHS England performance oversight, integrated care strategy |
| Local authority | Council plan, MTFS, cabinet reports | External audit letter, DLUHC monitoring, CIPFA benchmarking |
| Devolved body (Wales / Scotland / NI) | Government programme/strategy (may be in Welsh/Gaelic), Senedd/COSLA/PSNI scrutiny | WAO / Audit Scotland / NIAO — NOT NAO |
| Defence (MoD / agencies) | Defence Command Paper, acquisition strategy, DSIS | PAC, NAO defence reviews, JSC scrutiny |
| NDPB / regulator | Framework document, corporate plan, triennial review | Sponsoring department correspondence, departmental select committee |

#### Search sequence

1. **Resolve buyer identity.** Before substantive research, confirm the current
   legal name, parent body, and whether the organisation has been restructured,
   merged, renamed, or had functions transferred. Search for restructure,
   merger, successor body, and rename events. Record predecessor/successor
   names in `organisationContext.recentChanges`. Historical data for a
   predecessor body may not apply to a successor.

2. **Run targeted searches** covering: strategy document, senior leadership,
   annual report / corporate plan, procurement or commercial strategy, scrutiny
   record, major programmes, supplier/contract data, and commercial/SME
   strategy. The number of searches depends on depth mode:
   - deep: 10+ web searches
   - standard: 5–8 web searches
   - snapshot: 2–3 web searches

3. **Populate sections from results.** Register every source as you go.

4. **If a search returns nothing useful,** try one alternative query before
   declaring a section data-insufficient. Do NOT fabricate to fill gaps.

**Contradictory sources:** When two sources give different values for the same
fact, prefer the higher-tier source. If both are Tier 1, prefer the more
recent. Record both sources and note the discrepancy in the field's `rationale`.

### Step 2: Compile JSON

Read `references/output-schema.md` for the full schema, field rules, and
archetype definitions. Produce a single JSON object conforming to the v2.2
schema.

Every interpretive field uses an inline evidence wrapper:

```json
{
  "value": "The finding or assessment",
  "type": "fact | inference | unknown",
  "confidence": "high | medium | low",
  "rationale": "Why this conclusion was reached — name specific signals",
  "sourceRefs": ["SRC-001", "SRC-005"]
}
```

- `fact` — directly stated by a Tier 1–2 source with a date
- `inference` — derived from evidence. Rationale must explain the specific
  evidence chain, not just "inferred from available data"
- `unknown` — gap flagged. Value describes what is missing

Build the source register as you go. Every time you cite a source, add it to
`sourceRegister.sources` with a sequential ID (SRC-001, SRC-002...).

Save the JSON file as `<buyer-slug>-dossier.json` in the outputs directory.
Also save to `C:\Users\User\.pwin\intel\buyers\<buyer-slug>-dossier.json`
so other agents and sessions can access it.

### Step 3: Render HTML

After saving the JSON, run the bundled renderer script to produce the
BidEquity-branded HTML report:

```bash
python3 <skill-path>/scripts/render_dossier.py <json-path> <html-output-path>
```

Where `<skill-path>` is the bash-accessible path to this skill's directory.
The script reads the JSON, applies BidEquity branding, and writes a standalone
HTML file.

If the renderer script is not available at the expected path, check the
skill's installed location using:
```bash
find /sessions/ -name "render_dossier.py" -path "*/buyer-intelligence/*" 2>/dev/null
```

### Step 4: Save both files

Save JSON and HTML to:
1. `C:\Users\User\.pwin\intel\buyers\` — the persistent intel cache
2. The user's workspace folder — so they can open the HTML in a browser

Provide `computer://` links to both output files.

### Step 5: Verify completeness

Before delivering, verify programmatically:
```bash
python3 -c "
import json
with open('<json-path>') as f:
    d = json.load(f)
sections = ['meta','buyerSnapshot','organisationContext','strategicPriorities',
  'commissioningContextHypotheses','procurementBehaviour','decisionUnitAssumptions',
  'cultureAndPreferences','commercialAndRiskPosture','supplierEcosystem',
  'relationshipHistory','risksAndSensitivities','sourceRegister','computedScores',
  'linkedAssets','changeSummary']
for s in sections:
    val = d.get(s)
    status = 'NULL' if val is None else ('EMPTY' if val == {} or val == [] else 'OK')
    print(f'{s}: {status}')
print(f'Sources: {len(d[\"sourceRegister\"][\"sources\"])}')
print(f'Incumbents: {len(d[\"supplierEcosystem\"][\"incumbents\"])}')
fts = d['procurementBehaviour'].get('totalAwards')
print(f'FTS data: {\"YES\" if fts else \"NO - missing structured procurement data\"}')
"
```

---

## INJECT mode workflow

Inject mode adds a single source document to an existing dossier and updates
only the sections that source informs. No web searches. No FTS calls.

### Prerequisites
- An existing dossier must be in the intel cache at
  `C:\Users\User\.pwin\intel\buyers\<buyer-slug>-dossier.json`
- If no existing dossier is found, tell the user and offer to BUILD instead.

### Inject workflow

1. **Load existing dossier** from the intel cache.

2. **Read the source.** Depending on input type:
   - **File path** (PDF, DOCX, etc.) — use the Read tool or bash to extract
     text content. For PDFs, use the PDF skill or `read_pdf_bytes` if available.
   - **URL** — use `web_fetch` to retrieve the content.
   - **Pasted text** — use the content directly from the user's message.

3. **Classify the source.** Read `references/source-classification.md` for the
   full classification matrix. Determine:
   - Document type (annual report, strategy document, organogram, etc.)
   - Tier assignment (1–4)
   - Primary sections it informs
   - Secondary sections it may inform (only if content warrants it)

4. **Report classification to user.** Before making changes, briefly state:
   - What the document is
   - Which sections will be updated
   - Whether any gaps will be cleared
   This gives the user a chance to correct the classification if wrong.

5. **Extract intelligence from the source.** For each affected section, identify
   the specific fields to update and what the new evidence says about them.

6. **Apply updates to the dossier.** For each affected field, apply one of
   three operations (see `references/source-classification.md` for full rules):
   - **Replace** — new source is more authoritative or more recent
   - **Extend** — new source adds complementary information
   - **Upgrade** — new source converts an inference to a fact or raises confidence
   Preserve all existing evidence that is not contradicted by the new source.

7. **Update the source register:**
   - Add the new source with the next sequential ID (continue from the highest
     existing SRC-nnn ID, not SRC-INT-nnn)
   - Clear any matching entries from `sourceRegister.gaps`
   - Clear any matching entries from `decisionUnitAssumptions.intelligenceGaps`
   - Update `sourceRegister.staleFields` if the new source refreshes a stale field
   - Update `sourceRegister.lowConfidenceInferences` if an inference is upgraded

8. **Update the section confidence levels.** If the injected source raises a
   section from single-source to multi-source, or from Tier 3 to Tier 1–2,
   upgrade the section confidence accordingly.

9. **Produce a change summary.** Populate `changeSummary` with every field that
   changed: section, field, previous value summary, new value summary, and
   reason for change.

10. **Update meta:**
    - Increment version as patch: x.y.z → x.y.(z+1)
    - Add entry to `versionLog` with mode: "inject", date, and summary
    - Update `sourcesSummary` to reflect new source count
    - Do NOT change `refreshDue` — inject does not reset the refresh schedule

11. **Re-render HTML** using the same renderer script as BUILD mode.

12. **Save both files** to the intel cache and workspace folder.

13. **Report to user:** Summarise what changed, which gaps were cleared, and
    what remains unknown. Provide `computer://` links to both files.

### Inject mode constraints
- **No web searches.** Inject mode processes only the provided source.
- **No FTS calls.** Use the existing procurement data in the dossier.
- **No section deletion.** Inject only adds or updates — it never removes
  information from the dossier unless the new source explicitly contradicts it.
- **Source register is append-only.** New sources are added; existing sources
  are never removed.

---

## AMEND mode workflow

Amend mode adds Tier 4 internal intelligence from plain-language statements.
No documents, no web searches — just the account team's knowledge filed into
the right place.

### Prerequisites
- Same as inject: an existing dossier must be in the intel cache.

### Amend workflow

1. **Load existing dossier** from the intel cache.

2. **Parse the intelligence statement.** Identify:
   - What facts are being stated
   - Which schema fields they map to (use the target field identification
     table in `references/source-classification.md`)
   - Whether this is a single fact or multiple facts

3. **Confirm target fields.** Briefly tell the user:
   - Which fields will be updated
   - What the current value is (if any)
   - What the new value will be
   This gives the user a chance to correct before changes are applied.

4. **Apply the updates.** For each target field:
   - Set or update the field value
   - Set `type: "fact"` (Tier 4 internal knowledge is factual to the
     organisation, even if unverifiable from public sources)
   - Set `confidence` per the Tier 4 confidence rules in
     `references/source-classification.md`
   - Set `rationale` to explain the source (e.g., "Account team input from
     CAEHRS industry day, April 2025")
   - Add the internal source ID to `sourceRefs`

5. **Register the internal source.** Add to `sourceRegister.sources`:
   ```json
   {
     "sourceId": "SRC-INT-nnn",
     "sourceName": "Account team input — [brief description]",
     "sourceType": "internal",
     "publicationDate": null,
     "accessDate": "[today's date]",
     "reliability": "Tier 4",
     "sectionsSupported": ["[target sections]"],
     "url": null
   }
   ```
   Internal source IDs use the `SRC-INT-` prefix and are numbered sequentially,
   independent of external source IDs.

6. **Clear intelligence gaps.** Remove any matching entries from:
   - `decisionUnitAssumptions.intelligenceGaps`
   - `relationshipHistory.intelGaps`
   - `sourceRegister.gaps` (only if the amend resolves a data gap, not just
     adds relationship context)

7. **Update section confidence.** If this is the first Tier 4 data for
   `relationshipHistory`, upgrade `sectionConfidence` from `"none"` to `"low"`
   (single internal source) or `"medium"` (multiple internal sources). Update
   `tierNote` to reflect that Tier 4 data is now partially available.

8. **Produce a change summary.** Same format as inject mode.

9. **Update meta:**
   - Increment version as patch: x.y.z → x.y.(z+1)
   - Add entry to `versionLog` with mode: "amend", date, and summary
   - Update `sourcesSummary`

10. **Re-render HTML and save both files.**

11. **Report to user:** Summarise what was filed, which gaps were cleared,
    and what internal intelligence is still missing.

### Amend mode constraints
- **Tier 4 only.** Amend is for internal intelligence. If the user is providing
  a formal document, redirect to inject mode.
- **Preserve existing Tier 1–3 data.** Amend never overwrites publicly sourced
  facts with internal assertions. If there is a conflict, flag it and ask the
  user which is correct.
- **No web searches, no FTS calls.**
- **Multiple amends in one session.** The user may provide several pieces of
  intel in sequence. Process each as a separate amend operation against the
  same dossier, incrementing the patch version each time.

---

## REFRESH mode workflow

When `existingProfile` is provided (or found in `~/.pwin/intel/buyers/`),
and the user requests a refresh (or the `refreshDue` date has passed), you
are **refreshing**, not building from scratch.

1. **Re-run Step 0** to fetch latest FTS data — compare against cached version
   to detect new contracts or incumbent changes.
2. **Re-run targeted searches** for sections most likely to have changed:
   organisation context (leadership, structure, recentChanges), strategic
   priorities, and risks and sensitivities.
3. **Preserve Tier 4 data.** Carry forward `relationshipHistory` content that
   is not contradicted by new information. Do NOT clear internal data because
   it was not re-provided. Preserve all SRC-INT-nnn sources.
4. **Merge findings.** Replace values when new evidence updates them; extend
   rationale when new evidence adds nuance.
5. **Extend the source register.** Append new sources continuing from the
   previous highest ID — do not restart at SRC-001.
6. **Produce a `changeSummary`.** List material changes by section with field,
   previous value summary, new value summary, and reason for change.
7. **Increment `meta.version`** as minor: x.y → x.(y+1). Reset patch to 0.
   Add a `versionLog` entry with mode: "refresh".
8. **Set `meta.refreshDue`** to 6 months from today, or the buyer's next known
   reporting milestone if earlier.

---

## Versioning scheme

All dossiers use **major.minor.patch** versioning:

| Operation | Version increment | Example |
|---|---|---|
| Build (from scratch) | Major | 1.0 → 2.0 → 3.0 |
| Refresh (periodic re-run) | Minor | 3.0 → 3.1 → 3.2 |
| Inject (source document) | Patch | 3.1 → 3.1.1 → 3.1.2 |
| Amend (internal intel) | Patch | 3.1.2 → 3.1.3 |

The `versionLog` array records every operation with:
```json
{
  "version": "3.1.2",
  "date": "2026-04-23",
  "mode": "inject",
  "summary": "Injected DWP Digital Strategy PDF — updated strategicPriorities, cultureAndPreferences.changeMaturity.digitalMaturity"
}
```

When converting existing v2.2 dossiers to the new scheme, treat 2.2 as 2.2.0.

---

## Hypothesis sections

Sections 4 (Commissioning Context Hypotheses) and 6 (Decision Unit &
Stakeholder Assumptions) are explicitly interpretive. Every field in these
sections must have `type: "inference"`. Include the fixed caveats:

- Section 4: "These are hypotheses derived from available evidence. They
  require validation by the pursuit team."
- Section 6: "Inferred from published structures and procurement patterns.
  Requires pursuit-team validation."

**Buying cycle timing fields** (Section 4): infer `commissioningCycleStage`,
`approvalsPending`, `marketEngagementLikelihood`, `buyingReadiness`, and
`timelineRisks` from procurement notices, planning notice data, and market
engagement signals. `buyingReadiness` must be one of: pre-pipeline,
pipeline-identified, pre-market-engagement, post-market-engagement,
procurement-live, awarded.

**Exception for amend mode:** When the account team provides direct knowledge
of commissioning cycle stage or decision unit composition, those fields may
be upgraded from `inference` to `fact` with Tier 4 sourcing. The section
caveat remains but the individual field reflects the internal evidence.

---

## Supplier ecosystem (Section 9)

For each incumbent supplier, capture: what they deliver (service lines),
contract count and total value, relationship length, strategic importance
(critical / major / moderate / minor), recent activity trend (growing / stable
/ thinning), entrenchment indicators (systems, TUPE workforce, data,
relationships), and link to supplier dossier if one exists.

Also identify adjacent suppliers, supplier concentration patterns, switching
evidence, and market refresh areas.

**Framework and shared service nuance:** Note whether the buyer procures
through shared service arrangements (e.g., NHS SBS, CCS, police collaborative
hubs). Capture in `procurementBehaviour.sharedServiceArrangements`. Distinguish
between CCS call-off, CCS further competition, and open-market FTS procedures.

**SME obligations and social value:** Note published SME spend targets, social
enterprise preferences, or PPN 06/20 social value weightings. Capture in
`cultureAndPreferences.socialValueAndESG`.

---

## Relationship history (Section 10)

Draws entirely from **Tier 4 internal sources**. In most initial builds no
Tier 4 data will be available. When absent:

- Set `sectionConfidence` to "none"
- Set `tierNote` to "No Tier 4 data provided. All fields require account team
  input before this section is usable."
- Populate `intelGaps` with the sub-fields needing internal validation
- Do NOT infer relationship history from public procurement data — an FTS award
  does not imply any relationship with the bidder

When Tier 4 data is provided (via BUILD input, AMEND, or INJECT of internal
documents), capture: prior contracts, active programmes, past bids (with
outcomes and feedback), executive relationships, named advocates, named
blockers, and intelligence gaps flagged by the account team.

This section is the primary target for **amend mode** operations.

---

## Depth modes

| Mode | Sections to populate | Scope |
|------|----------------------|-------|
| **snapshot** | `meta`, `buyerSnapshot`, `procurementBehaviour`, `supplierEcosystem` (top 5 only), `sourceRegister` | All other sections null. No narratives, hypotheses, culture, risk, or relationship sections. 2–3 web searches. |
| **standard** | All sections | Full source register. The default. |
| **deep** | All sections, extended depth | Standard plus: full supplier entrenchment analysis, comprehensive strategy theme mapping, leadership background research, audit/scrutiny deep-dive, detailed commissioning rationale chains. |

If no depth specified, use **standard**.

**Source register expected volume:**
- deep: 15–25 sources, 10+ web searches
- standard: 8–15 sources, 5–8 web searches
- snapshot: 3–5 sources, 2–3 web searches

---

## Degraded mode

If, after completing web searches, you have fewer than 3 usable sources
(excluding FTS data), the dossier is **data-insufficient**. Most likely for:
recently created organisations, small NDPBs, devolved bodies with limited
English-language publications, or recently restructured/renamed organisations.

In degraded mode:

1. Auto-downgrade to snapshot depth regardless of requested mode.
2. Set `meta.depthMode` to `"snapshot-data-insufficient"`.
3. Set `meta.degradedReason` to a brief description of why data is thin.
4. Populate only: `buyerSnapshot`, `procurementBehaviour`, `sourceRegister`,
   and `risksAndSensitivities` (with intel gaps).
5. Set all other sections to null.
6. In `buyerSnapshot.executiveSummary`, list the specific research steps needed
   to complete a full standard dossier.

An honest partial picture is more useful than a structurally complete but
substantively hollow output.

---

## Hard rules

0. **Produce decisions, not just analysis.** Every section must carry a clear
   finding, not a description. The `organisationalArchetype`, the
   `executiveSummary.headline`, `keyRisks`, and
   `risksAndSensitivities.summaryNarrative` are DECISION outputs — they tell a
   capture lead what to do with this buyer. Section confidence levels force you
   to commit to a view, even if that view is "insufficient evidence."
   Indecision dressed as analysis is a failed output. If evidence is thin,
   state what is unknown and recommend what would resolve it — do not hedge.
1. **Distinguish facts from inferences.** Every evidenced field carries its
   type. If you are inferring, say so and explain why.
2. **No fabrication.** If data is unavailable, set the field to unknown type
   with a description of what's missing. An honest gap is more useful than a
   plausible-sounding guess.
3. **Hypothesis sections are hypotheses.** Sections 4 and 6 carry caveats. Do
   not present inferences as facts (unless upgraded by Tier 4 amend).
4. **Register sources as you go.** Add every source to the register immediately
   when cited.
5. **Use web search in build and refresh modes.** Do not produce a build/refresh
   dossier without searching for the buyer's strategy, leadership, and scrutiny
   record. Inject and amend modes do not require web search.
6. **Write for a capture lead.** Concise, professional, specific.
7. **Scope to UK public sector.** Group context only where relevant.
8. **Always render HTML.** After producing or updating the JSON, always run the
   renderer script to produce the branded HTML report. Both files are
   deliverables.
9. **Verify completeness before delivering** (build/refresh only). Check that
   `supplierEcosystem`, `sourceRegister.sources`, `linkedAssets`, and
   `changeSummary` (on refresh/inject/amend) are populated. Check FTS data was
   fetched (Step 5 verification script).
10. **Save to intel cache.** Always save final JSON to
    `C:\Users\User\.pwin\intel\buyers\` as well as the workspace folder.
11. **Preserve Tier 4 data across all modes.** Never discard internal
    intelligence (SRC-INT-nnn sources, relationshipHistory content, amend-
    supplied stakeholder data) during refresh or rebuild unless the user
    explicitly requests it.
