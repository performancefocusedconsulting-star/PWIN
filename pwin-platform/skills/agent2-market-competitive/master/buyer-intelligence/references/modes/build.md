# BUILD Mode Workflow

The dossier build follows this sequence:

0. **Fetch FTS data** — call pwin-platform MCP tools if available
1. **Research** — web searches following the search strategy below
2. **Compile JSON** — build the structured dossier conforming to the v3.0 schema
3. **Render HTML** — run the bundled renderer to produce the BidEquity-branded report
4. **Save both files** — JSON and HTML to the user's workspace folder
5. **Verify completeness** — check all required sections are populated

---

## Step 0: Fetch structured FTS data (pwin-platform MCP)

Before running web searches, attempt to fetch structured procurement data
from the local pwin-platform MCP server. Try calling these tools:

1. `get_buyer_profile(buyerName)` — returns award counts, total contract
   value, framework usage patterns, and key incumbent suppliers from the
   FTS database
2. `get_competitive_intel_summary(buyerName)` — returns market activity
   summary including recent awards and pipeline notices
3. `get_buyer_behaviour_profile(buyerName)` — returns the buyer-behaviour
   signals (cancellation rate, notice-to-award timing, distressed-incumbent
   flag) — pin these into `procurementBehaviourSnapshot`

**If both calls succeed:**
- Treat the results as **Tier 4 structured data** — higher reliability than
  media sources, lower than Tier 1 published documents
- Inject award counts and total value into `procurementBehaviour.totalAwards`
  and `procurementBehaviour.totalValue`
- Use incumbent supplier data to seed `supplierEcosystem.incumbents`
  (validate against web search before treating as definitive)
- Pin behaviour-profile signals into `procurementBehaviourSnapshot`
- Add the FTS database as a source in the source register:
  `sourceId: SRC-FTS`, `sourceType: procurement_database`,
  `reliability: Tier 4`,
  `sourceName: Find a Tender Service (via pwin-platform MCP)`,
  `lensesContributed: ["buying-behaviour", "supplier-landscape"]`
- Remove "No FTS procurement data provided" from `sourceRegister.gaps`

**If the MCP server is not available or calls fail:**
- Proceed without FTS data — do not halt or error
- Add to `sourceRegister.gaps`: "No FTS procurement data — pwin-platform
  MCP server not available. Run with server connected for structured
  contract data."
- Open an `actionRegister` action with `type: refresh`, owner
  `analyst`, recommended next step "Re-run when MCP server is available."
- Continue to Step 1 (web search)

**Also check the intel cache:** Look for an existing dossier at
`C:\Users\User\.pwin\intel\buyers\<buyer-slug>-dossier.json`. If found,
treat it as the `existingProfile` input and follow the refresh protocol
rather than building from scratch — unless the user explicitly requests a
fresh build.

---

## Step 1: Research

Read `references/source-hierarchy.md` for the full 5-tier hierarchy,
confidence calibration, and freshness rules before starting research.

**In deep mode, before starting research, list `references/extraction-templates/`
and Read every file in it.** They are short and define what you must
extract from each document type. You apply them in step 1.3 below, but
you must know what they look like before you canvass sources, so the
extraction structure shapes how you read each document. Use the Read
tool on each `.md` file in that folder. If the directory is empty or
inaccessible, list it explicitly and record the absence in
`meta.degradedReason` rather than inferring templates do not exist.

The dossier organises buyer intelligence around **seven lenses**: Mandate,
Pressure, Money, Buying behaviour, Risk posture, Supplier landscape, and
Pursuit implications. Read `references/output-schema.md` (the lens reference
section) to see how each lens maps to dossier sections. As you research,
tag each source you register with the lens(es) it contributes to —
`sourceRegister.sources[].lensesContributed` is mandatory.

You have a `web_search` tool. USE IT. Tier 4 procurement data is essential
for procurement behaviour and supplier ecosystem, but insufficient for
organisation context, strategy, leadership, culture, and risks.

**Sections that require web search:** organisation context, strategic
priorities, risks and sensitivities, culture and preferences, commercial
posture, pursuit implications.

### Adapt search strategy to organisation type

The right document types and scrutiny bodies differ by buyer class. Do not
apply central-government query patterns to NHS, local authority, or
devolved buyers.

| Organisation type | Key strategy sources | Key scrutiny sources |
|---|---|---|
| Central government dept / agency | Annual report, spending review, departmental plan, strategy document | NAO report, PAC hearing |
| NHS trust / ICB | CQC inspection, NHSI oversight letter, board papers | NHS England performance oversight, integrated care strategy |
| Local authority | Council plan, MTFS, cabinet reports | External audit letter, DLUHC monitoring, CIPFA benchmarking |
| Devolved body (Wales / Scotland / NI) | Government programme/strategy (may be in Welsh/Gaelic), Senedd/COSLA/PSNI scrutiny | WAO / Audit Scotland / NIAO — NOT NAO |
| Defence (MoD / agencies) | Defence Command Paper, acquisition strategy, DSIS | PAC, NAO defence reviews, JSC scrutiny |
| NDPB / regulator | Framework document, corporate plan, triennial review | Sponsoring department correspondence, departmental select committee |

### Retrieval checklist (Tier-organised)

Canvas the following document types when building a dossier on a UK
central-government department. Adapt by organisation type per the table
above. Not every document will exist for every buyer; record absences as
gaps in the action register.

**Tier 1 — Authoritative buyer sources (must-check)**
- Annual Report and Accounts (including Performance Report and Governance Statement)
- Outcome Delivery Plan / Single Departmental Plan / Corporate Plan
- Departmental Strategy
- Digital / transformation strategy
- Data strategy or data roadmap
- AI Strategy / AI Action Plan / AI ethics framework
- Cyber security strategy or guidance
- Workforce / People plan
- Estate / sustainability strategy
- Commercial / procurement strategy
- Efficiency / productivity plan
- Commercial pipeline / pipeline notices
- Procurement page (`doing business with us`)
- Senior leadership announcement / press release (most recent)
- Official statistics and dashboards (where service performance is reported)
- Research and evaluation reports
- SME / VCSE action plan
- Framework document, if agency / ALB
- Public body review / sponsorship review, if applicable

**Tier 2 — Centre-of-government (sample as needed)**
- Spending Review settlement
- Main Estimate and Supplementary Estimate
- Major Projects Portfolio data (IPA / GMPP)
- DDaT Playbook, AI Playbook, digital assurance guidance (where the buyer
  is bound by them)

**Tier 3 — External scrutiny (must-check for risk posture)**
- NAO reports
- PAC reports
- Departmental select committee reports
- Inspectorate or regulator reports (where applicable)

**Tier 4 — Market and procurement intelligence (auto-fetched in Step 0)**
- Find a Tender notices and award notices
- Contracts Finder records
- Contracts register
- Spend transparency data
- Buyer-behaviour profile

**Tier 5 — Relationship intelligence (only via amend mode)**
- CRM / account plan, prior bid feedback, account team interviews

### Search sequence

1. **Resolve buyer identity.** Before substantive research, confirm the
   current legal name, parent body, and whether the organisation has been
   restructured, merged, renamed, or had functions transferred. Search for
   restructure, merger, successor body, and rename events. Record
   predecessor/successor names in `organisationContext.recentChanges`.
   Historical data for a predecessor body may not apply to a successor.

2. **Canvas the retrieval checklist.** Work through the Tier 1, Tier 2, and
   Tier 3 lists above. The number of searches depends on depth mode:
   - **deep:** canvas the full list; for the top 3–5 highest-substance
     documents (typically annual report, departmental plan, digital
     strategy, NAO report if recent, GMPP entry if available), apply the
     dedicated extraction template from
     `references/extraction-templates/`. End-to-end read, structured
     extraction, mapped into the dossier per the template's
     `dossierMappings` block. 10+ web searches, 15–25 sources.
   - **standard:** canvas the Tier 1 must-check list and Tier 3 NAO/PAC.
     5–8 web searches, 8–15 sources. No extraction templates.
   - **snapshot:** Annual Report + Outcome Delivery Plan + most recent
     scrutiny report. 2–3 web searches, 3–5 sources.

3. **Apply extraction templates (deep mode).** When a source matches a
   document type with a dedicated template (see
   `references/source-classification.md` rightmost column), load the
   template, extract per its schema, and use the template's
   `dossierMappings` to populate the dossier with the right operations
   (extend / replace / upgrade). Record the extraction in
   `meta.extractionTemplatesApplied`.

4. **Tag every source with lenses.**
   `sourceRegister.sources[].lensesContributed` is mandatory. Use the lens
   column in `references/source-classification.md` as the starting point.

5. **Populate the action register.** Every gap, stale field, and
   low-confidence inference identified during research becomes an entry in
   `actionRegister.actions` with priority, owner role, and recommended
   next step. Do not finish the build with an empty action register
   unless the dossier has zero gaps (effectively never).

6. **If a search returns nothing useful,** try one alternative query
   before declaring a section data-insufficient. Do NOT fabricate to fill
   gaps.

**Contradictory sources:** When two sources give different values for the
same fact, prefer the higher-tier source. If both are Tier 1, prefer the
more recent. Record both sources and note the discrepancy in the field's
`rationale`. When Tier 1 says one thing and Tier 4 procurement data says
another, Tier 4 wins on what the buyer *actually does*; Tier 1 wins on
what they *intend*.

---

## Step 2: Compile JSON

Read `references/output-schema.md` for the full schema, field rules, and
archetype definitions. Produce a single JSON object conforming to the v3.0
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

Build the source register as you go. Every time you cite a source, add it
to `sourceRegister.sources` with a sequential ID (SRC-001, SRC-002...) and
a `lensesContributed` array.

Save the JSON file as `<buyer-slug>-dossier.json` in the outputs directory.
Also save to `C:\Users\User\.pwin\intel\buyers\<buyer-slug>-dossier.json`
so other agents and sessions can access it.

---

## Step 3: Render HTML

After saving the JSON, run the bundled renderer script to produce the
BidEquity-branded HTML report:

```bash
python3 <skill-path>/scripts/render_dossier.py <json-path> <html-output-path>
```

Where `<skill-path>` is the bash-accessible path to this skill's directory.
The script reads the JSON, applies BidEquity branding, and writes a
standalone HTML file.

If the renderer script is not available at the expected path, check the
skill's installed location using:
```bash
find /sessions/ -name "render_dossier.py" -path "*/buyer-intelligence/*" 2>/dev/null
```

---

## Step 4: Save both files

Save JSON and HTML to:
1. `C:\Users\User\.pwin\intel\buyers\` — the persistent intel cache
2. The user's workspace folder — so they can open the HTML in a browser

Provide `computer://` links to both output files.

---

## Step 5: Verify completeness

Before delivering, verify programmatically:

```bash
python3 -c "
import json
with open('<json-path>') as f:
    d = json.load(f)
sections = ['meta','buyerSnapshot','organisationContext','strategicPriorities',
  'commissioningContextHypotheses','procurementBehaviour','procurementBehaviourSnapshot',
  'decisionUnitAssumptions','cultureAndPreferences','commercialAndRiskPosture',
  'supplierEcosystem','relationshipHistory','risksAndSensitivities','pursuitImplications',
  'sourceRegister','actionRegister','computedScores','linkedAssets','changeSummary']
for s in sections:
    val = d.get(s)
    status = 'NULL' if val is None else ('EMPTY' if val == {} or val == [] else 'OK')
    print(f'{s}: {status}')
print(f'Sources: {len(d[\"sourceRegister\"][\"sources\"])}')
print(f'Incumbents: {len(d[\"supplierEcosystem\"][\"incumbents\"])}')
print(f'Open actions: {len([a for a in d[\"actionRegister\"][\"actions\"] if a[\"status\"] == \"open\"])}')
print(f'Pursuit implications: {len(d[\"pursuitImplications\"][\"implications\"])}')
fts = d['procurementBehaviour'].get('totalAwards')
print(f'FTS data: {\"YES\" if fts else \"NO - missing structured procurement data\"}')
snapshot = d.get('procurementBehaviourSnapshot', {}).get('snapshotSourcedFrom')
print(f'Behaviour snapshot: {snapshot or \"MISSING\"}')

# Deep-mode template gate
depth = d.get('meta', {}).get('depthMode', '')
templates_applied = d.get('meta', {}).get('extractionTemplatesApplied', [])
if depth == 'deep':
    n = len(templates_applied)
    if n < 3:
        print(f'TEMPLATE GATE FAIL: depthMode=deep but only {n} templates applied (>=3 required)')
        print('REMEDY: either re-run with extraction templates loaded from references/extraction-templates/, or honestly downgrade meta.depthMode to standard with degradedReason')
    else:
        print(f'Template gate: {n} templates applied (OK)')
else:
    print(f'Template gate: not enforced (depthMode={depth})')
"
```

If the template gate fails, do not deliver. Either re-run the deep-mode
research step with `references/extraction-templates/` Read into context,
or honestly downgrade `meta.depthMode` to `standard` and record the
reason in `meta.degradedReason`. Silent skipping is not acceptable.

Then read `references/consumer-contract.md` and verify that each decision
question has at least one populated path in the dossier. If a
consumer-critical path is missing, raise it as an action before delivering.
