---
name: supplier-intelligence
description: >
  Build, refresh, inject, or amend a supplier intelligence dossier on a UK
  public sector competitor or incumbent. Four modes: BUILD (new dossier),
  REFRESH (periodic re-run or upstream-data arrival), INJECT (add a source
  document), AMEND (add internal Tier 4 intelligence). Triggers on:
  "supplier dossier", "competitor profile", "supplier intel", "incumbent
  intelligence", "tell me about [supplier]", "build a profile of [company]",
  or any request to understand or update a UK public sector supplier before
  or during a pursuit.
---

# Supplier Intelligence Skill

Build and maintain structured dossiers on competitors and incumbent suppliers
in the UK public sector market. This is a **producer skill** — it gathers
intelligence rather than synthesising across other skills' outputs.

This skill conforms to the BidEquity Universal Skill Spec (see
`SKILL-UNIVERSAL-SPEC.md` in the projects folder). The structures and
disciplines below match the buyer, sector, and incumbency skills.

---

## Modes

| Command | Purpose | Web search | Version bump |
|---|---|---|---|
| `/supplier-intel build <name>` | Full deep research dossier from scratch | Yes | Major (1.0 → 2.0) |
| `/supplier-intel refresh <slug>` | Periodic re-run, OR triggered by upstream-data arrival | Yes (targeted) | Minor (3.0 → 3.1) |
| `/supplier-intel inject <slug>` | Add a specific document to an existing dossier | No | Patch (3.1 → 3.1.1) |
| `/supplier-intel amend <slug>` | Add Tier 4 internal intel (debrief, CRM note) | No | Patch (3.1.1 → 3.1.2) |

### Mode detection

Read the command. If ambiguous, ask the user which mode they intend. Do not
infer silently.

---

## CRITICAL: Save locations

Every build, refresh, inject, and amend MUST save to BOTH paths using the
**Write tool**. Skipping either path is a failed delivery.

| File | Intel cache | Workspace |
|---|---|---|
| JSON | `C:\Users\User\.pwin\intel\suppliers\<slug>-dossier.json` | `C:\Users\User\Documents\Claude\Projects\Bid Equity\suppliers\<slug>-dossier.json` |
| HTML | `C:\Users\User\.pwin\intel\suppliers\<slug>-dossier.html` | `C:\Users\User\Documents\Claude\Projects\Bid Equity\suppliers\<slug>-dossier.html` |

Create the workspace folder before writing if it does not exist.

---

## Prerequisites

This is a producer skill, so its required prerequisites are minimal.

### Required

| Artefact | Produced by | Affects |
|---|---|---|
| Supplier name (or slug for non-build modes) | User | All sections |

### Preferred

| Artefact | Produced by | Affects |
|---|---|---|
| FTS award data via MCP | `pwin-platform` (`get_supplier_profile`, `get_competitive_intel_summary`) | D2, D3, D4, D7 |
| Companies House data via MCP | `pwin-platform` | D1, D9 |

### Behaviour when prerequisites are missing

- **Required missing:** refuse and ask for the supplier name.
- **Preferred missing:** proceed with web search only. Note in
  `sourceRegister.gaps` which structured data was unavailable.

---

## Refresh triggers

Run a refresh when any of the following is true:

| Trigger | Type | Description |
|---|---|---|
| Time-based | Periodic | More than 90 days since `meta.lastModifiedDate` |
| Change-based | Reactive | Recent leadership change, financial event, M&A activity, profit warning, or contract win/loss covered in trade press |
| Source-arrival | Reactive | A new document is provided — handle via `inject` mode, not refresh |
| Artefact-arrival | Reactive | A previously-missing prerequisite has now been produced (e.g. FTS data became available; Companies House lookup now possible) — run a targeted refresh of the affected sections only |

For artefact-arrival refresh, re-derive only the sections whose `affects`
list includes the newly-arrived prerequisite. Leave all other sections
intact. Record the prerequisite arrival in the version log.

---

## Step 0: Gather platform context

Before any web research, attempt to fetch structured data from the local
pwin-platform MCP server:

1. `get_supplier_profile(slug)` — returns Companies House data (status,
   directors, SIC codes, parent), award counts, total contract value.
2. `get_competitive_intel_summary(slug)` — returns FTS award activity, top
   buyers, framework slot summary.

Print a summary:

```
Supplier:           <name>
FTS awards loaded:  <count> awards totalling <value>
Framework slots:    <list>
Key buyers:         <list>
```

**If both calls succeed:** Treat results as Tier 2 structured data. Inject
into D2/D3/D4 and seed D9 financial fields where Companies House data is
present. Add the FTS database as a source: `sourceId: SRC-FTS`,
`sourceType: procurement_database`, `tier: 2`.

**If MCP is not available or calls fail:** Proceed with web research only.
Add to `sourceRegister.gaps`: "FTS / Companies House data unavailable —
pwin-platform MCP server not connected at build time."

---

## Step 1: Slug and metadata

Derive `<slug>` from the supplier name: lowercase, hyphens not spaces,
remove Ltd/plc/Group. Examples: `serco-group`, `capita-plc`,
`mitie-group`, `babcock-international`.

Initialise the meta block:

```json
{
  "meta": {
    "slug": "<slug>",
    "supplierName": "<Full Legal Name>",
    "skillName": "supplier-intelligence",
    "version": "1.0.0",
    "mode": "build",
    "builtDate": "<YYYY-MM-DD>",
    "lastModifiedDate": "<YYYY-MM-DD>",
    "refreshDue": "<built date + 90 days>",
    "depthMode": "standard",
    "degradedMode": false,
    "degradedModeReason": null,
    "sourceCount": 0,
    "internalSourceCount": 0,
    "prerequisitesPresentAt": {
      "version": "1.0.0",
      "date": "<YYYY-MM-DD>",
      "required": {
        "supplierName": true
      },
      "preferred": {
        "ftsData": "<true|false>",
        "companiesHouseData": "<true|false>"
      }
    },
    "versionLog": [
      {
        "version": "1.0.0",
        "date": "<YYYY-MM-DD>",
        "mode": "build",
        "summary": "Initial dossier build for <supplierName>."
      }
    ]
  }
}
```

---

## Step 2: Research — Domain coverage

For BUILD mode, cover all 9 domains. For REFRESH, cover stale or
change-affected domains only.

**D1 — Identity & Structure**
- Full legal name, registered number (Companies House), parent company, subsidiaries
- SIC codes, incorporation date, group structure

**D2 — UK Public Sector Footprint**
- Total UK public sector revenue (£m), % of group revenue
- Sector breakdown: central government, local authority, NHS, defence, justice, transport
- Geographic spread (England, Scotland, Wales, NI)

**D3 — Framework & Contract Positions**
- Active CCS framework slots (lot numbers, expiry)
- Other framework positions: NHS SBS, G-Cloud, DOS/Digital, YPO, ESPO
- Top 10 live contracts (buyer, value, expiry, CPV)

**D4 — Incumbency Map**
- Contracts expiring in next 24 months (from FTS data)
- Rebid vulnerability score per contract
- Known pipeline pursuits (press, procurement portals)

**D5 — Capabilities & Service Lines**
- Core delivery capability areas
- Technology / digital stack
- Accreditations and certifications (Cyber Essentials+, ISO 27001, etc.)

**D6 — Key People**
- CEO, CFO, Public Sector MD, BD Director
- Recent leadership changes (12 months)
- Known relationships with key buyer organisations

**D7 — Competitive Positioning**
- Win rate signals (FTS award ratio)
- Key competitors per sector
- Differentiation narrative (from annual report / investor presentations)
- Known weaknesses (press, debrief intel, Glassdoor)

**D8 — Recent Signals**
- Contract wins/losses (last 90 days)
- Press coverage (last 90 days)
- Regulatory or reputational events
- Investor / analyst commentary

**D9 — Financial Health**
- Revenue trend (3 years), EBITDA margin, net debt
- Public sector revenue as % of total
- Contract risk provisions / notable impairments
- Credit risk summary

Use the evidence wrapper for every data point:

```json
{
  "value": "<the fact>",
  "type": "fact | estimate | signal | inference",
  "confidence": "high | medium | low",
  "rationale": "<why this confidence level>",
  "sourceRefs": ["SRC-001"]
}
```

**Use the Write tool** to save the JSON to both paths after Step 2 completes
— actually call the tool, do not narrate saving. Do not proceed to Step 3
until both Write tool calls have completed.

---

## Step 3: Strategic scores

After all 9 domains, compute three strategic scores (0–10 scale):

**Sector Strength Score** — how entrenched is this supplier in the relevant sector?
- Sub-factors: framework coverage (0–3), contract tenure (0–3), buyer relationship depth (0–2), capability breadth (0–2)

**Competitor Threat Score** — how dangerous are they to us on this opportunity?
- Sub-factors: incumbency relevance (0–3), bid capacity / BD investment (0–3), price aggression signals (0–2), differentiation strength (0–2)

**Vulnerability Score** — how exposed are they to displacement?
- Sub-factors: contract expiry concentration (0–3), financial stress signals (0–3), reputational risk (0–2), leadership instability (0–2)

Output each score with factor breakdown and a 2-sentence rationale.

---

## Step 4: Save both files — MANDATORY

Create workspace folders first (run in Bash):

```bash
mkdir -p "C:/Users/User/Documents/Claude/Projects/Bid Equity/suppliers"
mkdir -p "C:/Users/User/.pwin/intel/suppliers"
```

**Use the Write tool** to save each file — actually call the tool, do not
narrate saving:

1. **JSON → intel cache:** `C:\Users\User\.pwin\intel\suppliers\<slug>-dossier.json`
2. **JSON → workspace:** `C:\Users\User\Documents\Claude\Projects\Bid Equity\suppliers\<slug>-dossier.json`

Then run the renderer to produce HTML and write it to both paths in one
call:

```bash
python scripts/render.py <slug>
```

The renderer reads from `C:\Users\User\.pwin\intel\suppliers\<slug>-dossier.json`
and writes the rendered HTML to:

3. **HTML → intel cache:** `C:\Users\User\.pwin\intel\suppliers\<slug>-dossier.html`
4. **HTML → workspace:** `C:\Users\User\Documents\Claude\Projects\Bid Equity\suppliers\<slug>-dossier.html`

Provide `computer://` links to the two workspace files.

---

## Step 5: Verification

Run this check after saving — it reports the version, mode, source count,
domain coverage, FTS presence, and confirms both files exist on disk:

```bash
python -c "
import json, os
slug = '<slug>'
cache_path = fr'C:\\Users\\User\\.pwin\\intel\\suppliers\\{slug}-dossier.json'
with open(cache_path) as f:
    d = json.load(f)
meta = d['meta']
print(f'Slug:    {meta[\"slug\"]}')
print(f'Version: {meta[\"version\"]}')
print(f'Mode:    {meta[\"mode\"]}')
print(f'Sources: {meta[\"sourceCount\"]}')
domains = [k for k in d if k.startswith('D')]
print(f'Domains: {len(domains)}/9 present')
scores = d.get('strategicScores', {})
print(f'Scores:  sector_strength={scores.get(\"sectorStrength\",{}).get(\"score\",\"MISSING\")} '
      f'competitor_threat={scores.get(\"competitorThreat\",{}).get(\"score\",\"MISSING\")} '
      f'vulnerability={scores.get(\"vulnerability\",{}).get(\"score\",\"MISSING\")}')
fts = bool(d.get('D3', {}).get('frameworkPositions'))
print(f'FTS data: {\"YES\" if fts else \"NO - missing structured procurement data\"}')
for p in [
    fr'C:\\Users\\User\\.pwin\\intel\\suppliers\\{slug}-dossier.json',
    fr'C:\\Users\\User\\Documents\\Claude\\Projects\\Bid Equity\\suppliers\\{slug}-dossier.json',
    fr'C:\\Users\\User\\.pwin\\intel\\suppliers\\{slug}-dossier.html',
    fr'C:\\Users\\User\\Documents\\Claude\\Projects\\Bid Equity\\suppliers\\{slug}-dossier.html',
]:
    exists = 'YES' if os.path.exists(p) else 'MISSING - SAVE NOW'
    print(f'FILE SAVED: {exists} - {p}')
"
```

If any file is missing, the build is incomplete — call the Write tool for
that path and re-verify.

---

## INJECT mode workflow

Inject mode adds a single source document to an existing dossier and updates
only the sections that source informs. No web searches. No FTS calls.

### Prerequisites
- Existing dossier in the intel cache. If absent, tell the user and offer
  BUILD instead.

### Workflow

1. Load existing dossier from the intel cache.
2. Read the source (Read tool for files, web_fetch for URLs, or pasted text).
3. Classify the source against `references/source-classification.md`:
   document type, tier, primary domains it informs (D1–D9), secondary domains.
4. Tell the user what the document is, which domains will be updated, and
   whether any gaps will be cleared. Pause for correction.
5. For each affected domain, apply one of:
   - **Replace** — new source is more authoritative or recent
   - **Extend** — new source adds complementary information
   - **Upgrade** — new source converts inference to fact or raises confidence
   Preserve existing evidence not contradicted by the new source.
6. Update the source register: add new source with next sequential ID
   (continuing from highest existing SRC-nnn). Clear matching entries from
   `sourceRegister.gaps`, `sourceRegister.staleFields`, and
   `sourceRegister.lowConfidenceInferences`.
7. Populate `changeSummary` with every field that changed.
8. Update meta:
   - Bump version: x.y.z → x.y.(z+1)
   - Append `versionLog` entry with mode `inject`, date, and one-line summary
   - Update `lastModifiedDate`
   - Do NOT change `refreshDue` (inject does not reset the refresh schedule)
   - Update `prerequisitesPresentAt` if a prerequisite is now satisfied
9. Re-render HTML. Save both files (Write tool, both paths).
10. Run the verification step.
11. Report what changed, what gaps were cleared, what remains unknown.

### Constraints
- No web searches. No FTS calls. Inject processes only the provided source.
- Source register is append-only.

---

## AMEND mode workflow

Amend mode adds Tier 4 internal intelligence from plain-language statements.
No documents, no web searches.

### Prerequisites
- Existing dossier in the intel cache.

### Workflow

1. Load existing dossier from the intel cache.
2. Parse the intelligence statement. Identify which fields it maps to and
   whether it is a single fact or multiple facts.
3. Confirm target fields with the user before applying.
4. Append to the `amendments` array:
   ```json
   {
     "sourceId": "SRC-INT-001",
     "date": "<YYYY-MM-DD>",
     "type": "debrief | crmNote | accountTeam | partnerIntel",
     "author": "<initials or role>",
     "content": "<the intel>",
     "domainsAffected": ["D7", "D8"],
     "confidence": "high | medium | low"
   }
   ```
5. Apply the intelligence to the affected domain fields. Tag with the
   internal source ID. Tier 4 intelligence cannot overwrite Tier 1–2 facts —
   if there is a conflict, flag and ask the user.
6. Add the source to `sourceRegister.internalSources`.
7. Clear matching entries from `sourceRegister.gaps` if the amend resolves
   a data gap.
8. Populate `changeSummary` and update meta:
   - Bump version: x.y.z → x.y.(z+1)
   - Append `versionLog` entry with mode `amend`
   - Update `lastModifiedDate`
   - Increment `internalSourceCount`
9. Re-render HTML. Save both files.
10. Run the verification step.

### Constraints
- Tier 4 only. If the user is providing a formal document, redirect to inject.
- Amend never overwrites Tier 1–2 facts.

---

## REFRESH mode workflow

When `existingProfile` is found in the intel cache and the user requests a
refresh, the `refreshDue` date has passed, or a previously-missing
prerequisite has just become available.

### Workflow

1. Load existing dossier.
2. Re-run Step 0 (MCP fetch) to get latest FTS / Companies House data.
3. Identify which sections to refresh:
   - **Time-based / change-based refresh:** sections most likely to have
     changed (D6 leadership, D8 recent signals, D9 financial health, D4
     contracts expiring).
   - **Artefact-arrival refresh:** only the sections whose `affects` list
     includes the newly-arrived prerequisite.
4. Preserve all existing data not contradicted by new evidence. Preserve
   `amendments` array entirely (Tier 4 internal intel is never discarded
   on refresh).
5. Merge findings: replace values when new evidence updates them; extend
   rationale when new evidence adds nuance.
6. Append new sources to `sourceRegister.sources`, continuing from highest
   existing ID. Update `gaps`, `staleFields`, `lowConfidenceInferences`.
7. Populate `changeSummary` with material changes.
8. Update meta:
   - Bump version: x.y → x.(y+1).0 (minor bump, patch reset)
   - Append `versionLog` entry with mode `refresh`
   - Update `lastModifiedDate` and `refreshDue` (built date + 90 days)
   - Update `prerequisitesPresentAt` snapshot
9. Re-render HTML. Save both files.
10. Run the verification step.
11. Output a `deltaSummary` at the top of the HTML / markdown summary
    listing what changed since the previous version.

---

## Versioning scheme

| Operation | Increment | Example |
|---|---|---|
| Build | Major | 1.0.0 → 2.0.0 |
| Refresh (any trigger) | Minor (patch resets to 0) | 3.0.2 → 3.1.0 |
| Inject | Patch | 3.1.0 → 3.1.1 |
| Amend | Patch | 3.1.1 → 3.1.2 |

The `meta.versionLog` array records every operation: `version`, `date`,
`mode`, one-line `summary`. The log is append-only.

---

## Source register and tiers

```json
{
  "sourceRegister": {
    "sources": [
      {
        "sourceId": "SRC-001",
        "tier": 1,
        "sourceType": "annual_report",
        "title": "Serco Group Annual Report 2024",
        "publicationDate": "2025-03-15",
        "accessDate": "2026-04-24",
        "url": "https://...",
        "sectionsSupported": ["D1", "D2", "D9"],
        "evidenceAge": "13 months",
        "notes": "..."
      }
    ],
    "internalSources": [
      {
        "sourceId": "SRC-INT-001",
        "tier": 4,
        "sourceType": "internal",
        "sourceName": "Account team debrief — MoJ EM bid, March 2026",
        "accessDate": "2026-04-24",
        "sectionsSupported": ["D7"]
      }
    ],
    "gaps": [],
    "staleFields": [],
    "lowConfidenceInferences": []
  }
}
```

Tier mapping:
- **Tier 1:** Companies House filings, annual reports, official regulatory filings
- **Tier 2:** FTS award data, framework registers, NAO/PAC reports, audit reports
- **Tier 3:** Trade press, think tanks, LinkedIn, analyst reports, Glassdoor
- **Tier 4:** Internal CRM, debrief notes, account team intelligence

Source IDs are append-only. Do not renumber on refresh or rebuild.

---

## Hard rules

1. **Save to BOTH paths.** Skipping either is a failed delivery.
2. **Use the Write tool — actually call it.** Do not narrate saving.
3. **Always render HTML.** A JSON-only delivery is incomplete.
4. **Run verification after every save.** Do not declare done until
   verification confirms file existence on disk.
5. **Preserve Tier 4 data.** Internal intel is never discarded on refresh.
6. **Tier 4 cannot overwrite Tier 1–2.** Conflicts must be flagged.
7. **Source register is append-only.** Never renumber existing IDs.
8. **Refresh on artefact-arrival.** When a previously-missing prerequisite
   becomes available, run a targeted refresh, not a fresh build.
9. **Emit a structured `claims[]` block.** Every dossier you produce must
   include a top-level `claims[]` array containing every material assertion
   in the narrative. Each claim has six required fields: `claimId`,
   `claimText`, `claimDate`, `source`, `sourceDate`, `sourceTier`. Cite
   claims inline using `[CLM-id]` markers — **one claim ID per bracket**.
   Where multiple claims support the same assertion, cite them consecutively:
   `[CLM-001][CLM-007]`, **never** `[CLM-001, CLM-007]`. Comma-separated IDs
   inside a single bracket are invisible to the validator and all downstream
   consumers. A material claim with no `claimId` citation is a contract
   violation. See `../CLAIMS-BLOCK-SCHEMA.md` and §13 of the Universal
   Skill Spec.
10. **Write currency symbols as literal Unicode characters.** The pound
    sterling sign must always appear as `£` (Unicode U+00A3) in every JSON
    string value — never as `Â£`, `&pound;`, `&#163;`, or any other encoding
    artefact. Before delivering any dossier, scan your output for the string
    `Â£`. If found, stop, correct every affected string, and re-emit the full
    JSON. `Â£` is never correct in any field of this dossier.

---

## Output: HTML render

Run `python scripts/render.py <json-path> <html-output-path>` after every
JSON save. The renderer applies BidEquity branding:

- Midnight Navy `#021744`, Soft Sand `#F7F4EE`, Bright Aqua `#7ADDE2`
- Calm Teal `#5CA3B6`, Pale Aqua `#E0F4F6`, Light Terracotta `#D17A74`
