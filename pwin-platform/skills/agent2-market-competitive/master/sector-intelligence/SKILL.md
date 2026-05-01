---
name: sector-intelligence
description: >
  Build, refresh, or inject a sector intelligence brief on a UK public sector
  market (central government, local authority, NHS, defence, justice,
  transport, education, social care). Three modes: BUILD (new brief),
  REFRESH (periodic re-run or upstream-data arrival), INJECT (add a source
  document). No AMEND mode — sector intelligence is public-domain. Triggers
  on: "sector brief", "sector intel", "market overview", "what's happening
  in [sector]", "policy environment for [sector]", "[sector] procurement
  trends".
---

# Sector Intelligence Skill

Build and maintain structured briefs on UK public sector markets. Sector
briefs inform buyer intelligence, supplier dossiers, win strategy, and
qualification. This is a **producer skill**.

This skill conforms to the BidEquity Universal Skill Spec (see
`SKILL-UNIVERSAL-SPEC.md` in the projects folder).

---

## Modes

| Command | Purpose | Web search | Version bump |
|---|---|---|---|
| `/sector-intel build <sector>` | Full sector brief from scratch | Yes | Major (1.0 → 2.0) |
| `/sector-intel refresh <slug>` | Periodic re-run or upstream-data arrival | Yes (targeted) | Minor (3.0 → 3.1) |
| `/sector-intel inject <slug>` | Add a specific document to existing brief | No | Patch (3.1 → 3.1.1) |

There is no AMEND mode. Sector intelligence is public-domain — internal
amendments are not applicable. Use INJECT to add newly-published policy
documents or reports.

### Mode detection

Read the command. If ambiguous, ask the user which mode they intend.

---

## CRITICAL: Save locations

Every build, refresh, and inject MUST save to BOTH paths using the
**Write tool**. Skipping either path is a failed delivery.

| File | Intel cache | Workspace |
|---|---|---|
| JSON | `C:\Users\User\.pwin\intel\sectors\<slug>-brief.json` | `C:\Users\User\Documents\Claude\Projects\Bid Equity\sectors\<slug>-brief.json` |
| HTML | `C:\Users\User\.pwin\intel\sectors\<slug>-brief.html` | `C:\Users\User\Documents\Claude\Projects\Bid Equity\sectors\<slug>-brief.html` |

Create the workspace folder before writing if it does not exist.

---

## Prerequisites

This is a producer skill, so its required prerequisites are minimal.

### Required

| Artefact | Produced by | Affects |
|---|---|---|
| Sector name (or slug for non-build modes) | User | All sections |

### Preferred

| Artefact | Produced by | Affects |
|---|---|---|
| FTS spend data via MCP | `pwin-platform` (`get_competitive_intel_summary` filtered by sector) | S2 (spend & budget), S3 (market trends) |
| Platform sector knowledge via MCP | `pwin-platform` (`get_sector_knowledge`) | S6 (implications) |

### Behaviour when prerequisites are missing

- **Required missing:** refuse and ask for the sector name.
- **Preferred missing:** proceed with web research only. Note in
  `sourceRegister.gaps` which structured data was unavailable.

---

## Refresh triggers

Run a refresh when any of the following is true:

| Trigger | Type | Description |
|---|---|---|
| Time-based | Periodic | More than 90 days since `meta.lastModifiedDate` |
| Change-based | Reactive | Spending review published, major policy announcement, new legislation, ministerial change affecting the sector |
| Source-arrival | Reactive | A new document is provided — handle via `inject` mode |
| Artefact-arrival | Reactive | A previously-missing prerequisite has now been produced (e.g. FTS sector data became available) — run a targeted refresh of the affected sections only |

---

## Step 0: Gather platform context

Before any web research, attempt to fetch structured data from the local
pwin-platform MCP server:

1. `get_sector_knowledge(slug)` — returns platform sector reasoning (drivers, archetypes, evaluation patterns).
2. `get_competitive_intel_summary(sectorSlug)` — returns FTS spend data filtered by the sector's CPV codes.

Print a summary:

```
Sector:          <name>
FTS spend data:  £<total> across <count> contracts
Top buyers:      <list>
Top CPV codes:   <list>
```

**If both calls succeed:** Treat results as Tier 2 structured data. Inject
into S2 and seed S3. Add as source: `sourceId: SRC-FTS`,
`sourceType: procurement_database`, `tier: 2`.

**If MCP is not available:** Proceed with web research only. Add to
`sourceRegister.gaps`: "FTS sector data unavailable — pwin-platform MCP
server not connected at build time."

---

## Step 1: Slug and metadata

Derive `<slug>` from the sector name: lowercase, hyphens not spaces.
Examples: `central-government`, `local-government`, `nhs-health`,
`defence`, `justice-home-affairs`, `transport`, `education`, `social-care`.

Initialise the meta block:

```json
{
  "meta": {
    "slug": "<slug>",
    "sectorName": "<Display Name>",
    "skillName": "sector-intelligence",
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
        "sectorName": true
      },
      "preferred": {
        "ftsSpendData": "<true|false>",
        "platformSectorKnowledge": "<true|false>"
      }
    },
    "versionLog": [
      {
        "version": "1.0.0",
        "date": "<YYYY-MM-DD>",
        "mode": "build",
        "summary": "Initial sector brief build for <sectorName>."
      }
    ]
  }
}
```

---

## Step 2: Research — Six sections

For BUILD mode, cover all 6 sections. For REFRESH, cover stale or
change-affected sections only.

### S1 — Policy & Regulatory Environment
- Current government policy direction affecting procurement in this sector
- Key legislation (active and pending): procurement reform, sector-specific regulation
- Scrutiny bodies and oversight (PAC, NAO, select committees, regulators)
- Policy risks: change of government direction, spending reviews, reform programmes
- Key policy documents published in last 12 months

### S2 — Spending & Budget Landscape
- Total addressable spend: estimated annual public procurement value (£bn)
- Budget trajectory: SR commitments, departmental settlements, pressures
- Procurement channel mix: direct award, framework, open competition, DPS
- Top frameworks by value (CCS, sector-specific)
- Grant vs contract balance
- FTS data: contract volume, total value, average contract value, CPV breakdown

### S3 — Market Trends & Dynamics
- Demand drivers: demographics, digital transformation, efficiency mandates
- Service delivery model shifts: insourcing / outsourcing trend, joint ventures
- Technology adoption: AI, digital platforms, data sharing
- Workforce / skills context affecting supplier delivery
- ESG and social value requirements
- Pipeline signals: major recompetes expected in next 24 months

### S4 — Trade Press & Commentary
- Key publications covering this sector
- Recent commentary themes (last 90 days): what are the headlines?
- Trade body positions: industry associations, employer groups
- Consultant / analyst views
- Parliamentary activity: recent debates, written questions, select committee inquiries

### S5 — Peer Comparisons & Benchmarks
- UK vs international service delivery models
- Performance benchmarks: cost per unit, outcome metrics, satisfaction scores
- Case studies of delivery innovation or failure
- Comparable procurement markets (devolved nations, EU equivalents)

### S6 — Implications for Pursuit & Positioning
- What buyer priorities should shape solution design in this sector?
- What evaluation criteria patterns recur (quality vs price split, social value weight)?
- What differentiation angles work in this sector?
- What risks should be flagged in qualification?
- Signal watch list: what to monitor that would change the pursuit strategy?

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

## Step 3: Sector summary card

After all 6 sections, produce the summary card:

```json
{
  "sectorSummary": {
    "addressableSpendGbpbn": "evidence_wrapper",
    "spendTrajectory": "growing | stable | declining",
    "topFrameworks": ["string"],
    "avgContractValueGbpm": "evidence_wrapper",
    "socialValueWeightTypicalPct": "evidence_wrapper",
    "qualityPriceSplitTypical": "evidence_wrapper",
    "keyBuyerOrganisations": ["string"],
    "majorRecompetes24m": ["string"],
    "sectorRiskLevel": "high | medium | low",
    "riskRationale": "string 2 sentences"
  }
}
```

---

## Step 4: Save both files — MANDATORY

Create workspace folders first (run in Bash):

```bash
mkdir -p "C:/Users/User/Documents/Claude/Projects/Bid Equity/sectors"
mkdir -p "C:/Users/User/.pwin/intel/sectors"
```

**Use the Write tool** to save each file — actually call the tool, do not
narrate saving:

1. **JSON → intel cache:** `C:\Users\User\.pwin\intel\sectors\<slug>-brief.json`
2. **JSON → workspace:** `C:\Users\User\Documents\Claude\Projects\Bid Equity\sectors\<slug>-brief.json`

Then run the renderer to produce HTML and write it to both paths in one
call:

```bash
python scripts/render.py <slug>
```

The renderer reads from the intel cache path and writes to:

3. **HTML → intel cache:** `C:\Users\User\.pwin\intel\sectors\<slug>-brief.html`
4. **HTML → workspace:** `C:\Users\User\Documents\Claude\Projects\Bid Equity\sectors\<slug>-brief.html`

Provide `computer://` links to the two workspace files.

---

## Step 5: Verification

Run this check after saving:

```bash
python -c "
import json, os
slug = '<slug>'
cache_path = fr'C:\\Users\\User\\.pwin\\intel\\sectors\\{slug}-brief.json'
with open(cache_path) as f:
    d = json.load(f)
meta = d['meta']
print(f'Slug:    {meta[\"slug\"]}')
print(f'Version: {meta[\"version\"]}')
print(f'Mode:    {meta[\"mode\"]}')
print(f'Sources: {meta[\"sourceCount\"]}')
sections = [k for k in d if k.startswith('S') and len(k) == 2]
print(f'Sections: {len(sections)}/6 present')
fts = bool(d.get('S2', {}).get('ftsSpendData'))
print(f'FTS data: {\"YES\" if fts else \"NO - missing structured procurement data\"}')
for p in [
    fr'C:\\Users\\User\\.pwin\\intel\\sectors\\{slug}-brief.json',
    fr'C:\\Users\\User\\Documents\\Claude\\Projects\\Bid Equity\\sectors\\{slug}-brief.json',
    fr'C:\\Users\\User\\.pwin\\intel\\sectors\\{slug}-brief.html',
    fr'C:\\Users\\User\\Documents\\Claude\\Projects\\Bid Equity\\sectors\\{slug}-brief.html',
]:
    exists = 'YES' if os.path.exists(p) else 'MISSING - SAVE NOW'
    print(f'FILE SAVED: {exists} - {p}')
"
```

If any file is missing, the build is incomplete — call the Write tool for
that path and re-verify.

---

## INJECT mode workflow

Inject mode adds a single source document to an existing brief and updates
only the sections that source informs.

### Prerequisites
- Existing brief in the intel cache. If absent, tell the user and offer
  BUILD instead.

### Workflow

1. Load existing brief from the intel cache.
2. Read the source (Read tool for files, web_fetch for URLs, or pasted text).
3. Classify the source against `references/source-classification.md`:
   document type, tier, primary sections it informs (S1–S6), secondary sections.
4. Tell the user what the document is, which sections will be updated, and
   whether any gaps will be cleared. Pause for correction.
5. For each affected section, apply one of:
   - **Replace** — new source is more authoritative or recent
   - **Extend** — new source adds complementary information
   - **Upgrade** — new source converts inference to fact or raises confidence
   Preserve existing evidence not contradicted by the new source.
6. Update the source register: add new source with next sequential ID.
   Clear matching entries from `sourceRegister.gaps`.
7. Populate `changeSummary` with every field that changed.
8. Update meta:
   - Bump version: x.y.z → x.y.(z+1)
   - Append `versionLog` entry with mode `inject`
   - Update `lastModifiedDate`
9. Re-render HTML. Save both files.
10. Run the verification step.

### Constraints
- No web searches. Inject processes only the provided source.
- Source register is append-only.

---

## REFRESH mode workflow

When `existingProfile` is found in the intel cache and the user requests a
refresh, the `refreshDue` date has passed, or a previously-missing
prerequisite has just become available.

### Workflow

1. Load existing brief.
2. Re-run Step 0 (MCP fetch) to get latest FTS sector data.
3. Identify which sections to refresh:
   - **Time-based / change-based:** S1 (policy), S2 (spending if SR or budget cycle), S4 (recent commentary).
   - **Artefact-arrival:** only the sections whose `affects` list includes the newly-arrived prerequisite.
4. Preserve existing data not contradicted by new evidence.
5. Append new sources to `sourceRegister.sources`.
6. Populate `changeSummary`.
7. Update meta:
   - Bump version: x.y → x.(y+1).0
   - Append `versionLog` entry with mode `refresh`
   - Update `lastModifiedDate`, `refreshDue`, `prerequisitesPresentAt`
8. Re-render HTML. Save both files.
9. Run verification.
10. Output `deltaSummary` listing what changed since the previous version.

---

## Versioning scheme

| Operation | Increment | Example |
|---|---|---|
| Build | Major | 1.0.0 → 2.0.0 |
| Refresh (any trigger) | Minor (patch resets to 0) | 3.0.1 → 3.1.0 |
| Inject | Patch | 3.1.0 → 3.1.1 |

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
        "sourceType": "policy_document",
        "title": "Transforming Public Procurement — Cabinet Office 2025",
        "publicationDate": "2025-02-01",
        "accessDate": "2026-04-24",
        "url": "https://...",
        "sectionsSupported": ["S1", "S2"],
        "evidenceAge": "14 months",
        "notes": "..."
      }
    ],
    "internalSources": [],
    "gaps": [],
    "staleFields": [],
    "lowConfidenceInferences": []
  }
}
```

Tier mapping:
- **Tier 1:** Official government publications, legislation, regulatory decisions, NAO/PAC reports
- **Tier 2:** FTS spend data, framework registers, procurement notices
- **Tier 3:** Trade press, think tanks, parliamentary records, analyst reports

(No Tier 4 — sector intelligence is public-domain.)

Source IDs are append-only. Do not renumber on refresh or rebuild.

---

## Hard rules

1. **Save to BOTH paths.** Skipping either is a failed delivery.
2. **Use the Write tool — actually call it.** Do not narrate saving.
3. **Always render HTML.** A JSON-only delivery is incomplete.
4. **Run verification after every save.** Do not declare done until
   verification confirms file existence on disk.
5. **Source register is append-only.** Never renumber existing IDs.
6. **Refresh on artefact-arrival.** When a previously-missing prerequisite
   becomes available, run a targeted refresh, not a fresh build.
7. **Emit a structured `claims[]` block.** Every dossier you produce must
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
8. **Write currency symbols as literal Unicode characters.** The pound
   sterling sign must always appear as `£` (Unicode U+00A3) in every JSON
   string value — never as `Â£`, `&pound;`, `&#163;`, or any other encoding
   artefact. Before delivering any dossier, scan your output for the string
   `Â£`. If found, stop, correct every affected string, and re-emit the full
   JSON. `Â£` is never correct in any field of this dossier.

---

## Output: HTML render

Run `python scripts/render.py <slug>` after every JSON save. The renderer
applies BidEquity branding:

- Midnight Navy `#021744`, Soft Sand `#F7F4EE`, Bright Aqua `#7ADDE2`
- Calm Teal `#5CA3B6`, Pale Aqua `#E0F4F6`, Light Terracotta `#D17A74`

The sector brief JSON carries a top-level `claims[]` block alongside `meta`,
`sourceRegister`, and the section objects (S1–S6). Every material assertion
in the narrative cites a claim by its `claimId`. The contract is documented
in [`../CLAIMS-BLOCK-SCHEMA.md`](../CLAIMS-BLOCK-SCHEMA.md); the platform
validator at `../scripts/validate_claims_block.py` enforces it.
