# Universal Skill Spec — v1.0

This document defines the contract every BidEquity intelligence skill must follow.
It exists so that the buyer, supplier, sector, and incumbency skills behave
predictably, can be co-ordinated by a future orchestrator agent, and produce
audit-trailable artefacts that improve over time rather than getting overwritten.

The four skills covered today:

| Skill | Type | Output |
|---|---|---|
| buyer-intelligence | Producer | Buyer dossier |
| supplier-intelligence | Producer | Supplier dossier |
| sector-intelligence | Producer | Sector brief |
| incumbency-advantage-displacement-strategy | Integrator | Incumbent assessment |

A **producer** skill goes out and finds intelligence in the world (procurement
data, web sources, public documents). A producer can degrade gracefully when
its preferred data source is unavailable — a thinner web-only dossier is still
useful.

An **integrator** skill takes intelligence already produced by other skills and
turns it into judgement (assessment, recommendation, decision). An integrator
cannot degrade gracefully — without its inputs, it produces a credible-looking
output with no evidence behind it. Integrators must verify their prerequisites
and refuse to run when required inputs are absent.

The rules below apply to both types unless flagged "integrator only".

---

## 1. Modes

Every skill supports four modes (sector-intelligence is exempt from `amend`
because sector data is public-domain — that exemption is documented in the skill).

| Mode | Trigger | What it does | Web search | Version bump |
|---|---|---|---|---|
| `build` | No existing artefact in the intel cache | Full research and compilation from scratch | Yes | Major (1.0 → 2.0) |
| `refresh` | Existing artefact + user requests refresh, OR `meta.refreshDue` date passed, OR a previously-missing prerequisite has just become available | Re-runs data gathering for affected sections, merges with existing, produces change summary | Yes (targeted) | Minor (3.0 → 3.1) |
| `inject` | User provides a source document (PDF, URL, file, or pasted text) | Reads source, classifies sections it informs, updates only those fields | No | Patch (3.1 → 3.1.1) |
| `amend` | User provides plain-language internal Tier 4 intelligence | Parses statement, identifies target fields, applies Tier 4 update | No | Patch (3.1.1 → 3.1.2) |

### Mode detection

If the user's request is ambiguous, ask which mode they intend. Do not infer
silently — getting the mode wrong is more damaging than asking.

---

## 2. Prerequisites block (universal, but matters most for integrators)

Every skill declares its prerequisites in a structured block at the top of
its data-gathering step. The block has two lists:

```yaml
prerequisites:
  required:
    - artefact: "<artefact name>"
      producedBy: "<upstream skill name>"
      affects: ["<sections of this skill's output that depend on it>"]
  preferred:
    - artefact: "<artefact name>"
      producedBy: "<upstream skill name>"
      affects: ["<sections>"]
```

### Behaviour when prerequisites are missing

**If a `required` prerequisite is absent:**
1. Refuse to run.
2. List which prerequisites are missing and which upstream skills produce them.
3. Recommend the order in which to run them.
4. Do not produce a partial artefact — that is misleading.

Example refusal output for an integrator:

> Prerequisites not met. This skill requires:
> - **Buyer dossier for [buyer name]** — produced by `buyer-intelligence`
> - **Supplier dossier for [incumbent name]** — produced by `supplier-intelligence`
>
> Both are absent. Run `buyer-intelligence build [buyer name]` and
> `supplier-intelligence build [incumbent name]` first, then re-run this skill.

**If a `preferred` prerequisite is absent:**
1. Proceed.
2. State at the top of the output which preferred inputs were missing.
3. Reduce confidence on the affected sections explicitly.
4. Add the missing prerequisite to `openQuestions` or equivalent.

### Producers

Producer skills have minimal `required` prerequisites — typically just "MCP
server reachable" or "buyer/supplier/sector name supplied." Their `preferred`
list captures what would improve the output (FTS data, prior internal intel).

### Integrators

Integrator skills have substantial `required` prerequisites — the upstream
artefacts whose outputs they synthesise. The incumbency skill is the canonical
integrator — its required prerequisites include pursuit context, buyer dossier,
and supplier dossier (incumbent). Its preferred prerequisites include ITT
documents, stakeholder map, capture plan, latest Qualify run.

---

## 3. Versioning

All artefacts use `meta.version` as `major.minor.patch`.

| Operation | Increment | Example |
|---|---|---|
| Build (from scratch) | Major | 1.0 → 2.0 |
| Refresh (periodic re-run or artefact-arrival) | Minor | 3.0 → 3.1 |
| Inject (source document) | Patch | 3.1 → 3.1.1 |
| Amend (Tier 4 intel) | Patch | 3.1.1 → 3.1.2 |

Refresh resets the patch count to zero. Build resets minor and patch to zero.

When converting older artefacts to the new scheme, treat `2.2` as `2.2.0`.

---

## 4. Version log

Every artefact carries a `meta.versionLog` array recording every operation:

```json
{
  "versionLog": [
    {
      "version": "3.0.0",
      "date": "2026-04-01",
      "mode": "build",
      "summary": "Initial dossier build for HMRC."
    },
    {
      "version": "3.0.1",
      "date": "2026-04-12",
      "mode": "inject",
      "summary": "Injected DWP Digital Strategy PDF — updated strategicPriorities, cultureAndPreferences.changeMaturity.digitalMaturity."
    },
    {
      "version": "3.1.0",
      "date": "2026-04-20",
      "mode": "refresh",
      "summary": "Periodic refresh — leadership change picked up, recentChanges and decisionUnitAssumptions updated."
    }
  ]
}
```

The log is append-only. Never rewrite history.

---

## 5. Change summary

Every non-build operation populates a `changeSummary` array recording what
moved. This is what an orchestrator (or a human reviewer) reads to understand
what's different since last time.

```json
{
  "changeSummary": [
    {
      "section": "strategicPriorities",
      "field": "digitalTransformation.value",
      "before": "Modernising legacy systems",
      "after": "Migrating critical services to cloud by 2027 per Digital Strategy 2025",
      "reason": "DWP Digital Strategy PDF added — upgrades inference to fact, raises confidence."
    }
  ]
}
```

The change summary describes **what changed in this operation**. The version
log records **that an operation happened**. Both must be present on every
non-build operation.

For refresh mode, also include a one-line `deltaSummary` at the top of the
markdown output: "Changes since [previous date]: [bullet list]."

---

## 6. Source register

The source register has a consistent structure across all skills:

```json
{
  "sourceRegister": {
    "sources": [
      {
        "sourceId": "SRC-001",
        "sourceType": "annual_report | foi | audit_report | regulator_report | news | supplier_marketing | inference | framework_data | companies_house | procurement_database | ...",
        "title": "string",
        "publicationDate": "YYYY-MM-DD or null",
        "accessDate": "YYYY-MM-DD",
        "url": "string or null",
        "tier": 1,
        "sectionsSupported": ["..."],
        "evidenceAge": "14 months",
        "notes": "string"
      }
    ],
    "internalSources": [
      {
        "sourceId": "SRC-INT-001",
        "sourceType": "internal",
        "sourceName": "Account team input — DWP industry day, April 2026",
        "tier": 4,
        "accessDate": "YYYY-MM-DD",
        "sectionsSupported": ["..."]
      }
    ],
    "gaps": ["What is missing and what would close it"],
    "staleFields": ["Fields where evidence is >24 months old"],
    "lowConfidenceInferences": ["Fields where confidence is low and corroboration is needed"]
  }
}
```

### Source ID prefixes

| Prefix | Meaning |
|---|---|
| `SRC-001`, `SRC-002` | External sources (Tier 1–3) |
| `SRC-INJ-001` | Sources added via inject mode (continue from highest existing SRC-nnn) |
| `SRC-INT-001` | Internal sources (Tier 4 — debriefs, CRM notes, account team) |

Source IDs are append-only. Do not renumber when refreshing.

### Tiers

| Tier | What |
|---|---|
| 1 | Procurement documents, official filings, NAO/PAC, regulatory decisions |
| 2 | Audit reports, scrutiny reports, FTS award data (structured), inspectorate reports |
| 3 | Annual reports, FOI responses, board papers, trade press |
| 4 | Internal intelligence — debrief notes, CRM, account team observations |

Tier 4 sources can never overwrite Tier 1–2 facts. If they conflict, flag the
conflict and ask the user which is correct.

---

## 7. Refresh triggers

A skill should refresh in any of the following situations. The skill's
SKILL.md must enumerate them explicitly so the user (or orchestrator) knows
when to invoke a refresh.

| Trigger | Type | Example |
|---|---|---|
| Time-based | Periodic | More than X days since last refresh (default 90 for producers, 20 working days for integrators on active pursuits) |
| Change-based | Reactive | New ITT uploaded, PWIN moved by >0.5, gate within 5 working days, leadership change picked up |
| Source-arrival | Reactive | A document has been provided — handled via `inject` mode (not refresh) |
| **Artefact-arrival** | Reactive | A previously-missing prerequisite has now been produced by an upstream skill — handled via targeted `refresh` mode |

The artefact-arrival trigger is the one most often missed. It distinguishes
inject (a *document* arrived) from refresh (an *upstream artefact* arrived).
When a previously-missing prerequisite becomes available:

1. Run `refresh`, not `build`.
2. Re-derive only the sections whose `affects` list includes the newly-arrived
   prerequisite.
3. Leave all other sections intact.
4. Record the prerequisite arrival in the version log:
   `"summary": "Capture plan now available — refreshed relationship_embeddedness, buyer_change_appetite, win_themes."`
5. Update `meta.prerequisitesPresentAt` (see next section).

---

## 8. State capture — `prerequisitesPresentAt`

Each artefact records, at its current version, which prerequisites existed
at write time:

```json
{
  "meta": {
    "prerequisitesPresentAt": {
      "version": "3.1.0",
      "date": "2026-04-20",
      "required": {
        "buyer_dossier": true,
        "supplier_dossier_incumbent": true,
        "pursuit_context": true
      },
      "preferred": {
        "itt_documents": true,
        "stakeholder_map": false,
        "capture_plan": false,
        "latest_qualify_run": true
      }
    }
  }
}
```

This makes it trivially auditable what evidence the artefact was built on.
A future orchestrator (or red-team reviewer) can compare current platform
state to `prerequisitesPresentAt` and decide whether a refresh is due.

---

## 9. Save and verify discipline

This is the lesson from the buyer skill testing — the model would narrate
"I'm saving the file" without actually calling the Write tool, or save to
one path but not both.

### Required pattern in every skill

**1. Save locations table at the top of the SKILL.md** (before any workflow
steps), declaring both paths the artefact must be written to:

| File | Intel cache | Workspace |
|---|---|---|
| JSON | `C:\Users\User\.pwin\intel\<type>\<slug>-<artefact>.json` | `C:\Users\User\Documents\Claude\Projects\Bid Equity\<type>\<slug>-<artefact>.json` |
| HTML | (same pattern, .html) | (same pattern, .html) |

**2. Explicit instruction to use the Write tool** at every save point:

> **Use the Write tool** to save each file — actually call the tool, do not
> narrate saving.

**3. Mandatory verification step** at the end of every build/refresh/inject/amend.
A short Python check that:
- Loads the JSON
- Reports the version, mode, source count, section coverage
- Confirms FTS data presence (or absence with reason)
- Checks that both files exist on disk at both paths

**4. Folder creation before save** — the workspace folder must be created
via Bash if it doesn't exist; do not assume.

**5. HTML render is mandatory** — every JSON save is followed by running the
bundled `render.py` script and saving the HTML to both paths.

---

## 10. Compliance checklist

Every skill's `SKILL.md` must contain, at minimum:

- [ ] Frontmatter with `name` and `description` (description triggers on the
      operational language a user would use, not just the artefact name)
- [ ] Mode table with all four modes (or three for sector, with carve-out
      explanation)
- [ ] Mode detection paragraph
- [ ] CRITICAL: Save locations table (both paths)
- [ ] Prerequisites block — required and preferred
- [ ] Step 0 (or equivalent) — gather platform context via MCP
- [ ] Workflow steps with explicit "Use the Write tool" instructions
- [ ] Refresh triggers section enumerating all four trigger types
- [ ] Inject mode workflow
- [ ] Amend mode workflow (or carve-out)
- [ ] Versioning scheme paragraph
- [ ] Mandatory verification step at the end of build/refresh
- [ ] HTML render step
- [ ] Hard rules (numbered)
- [ ] Source register specification

---

## 11. Output schema universal fields

These fields appear at the top of every artefact JSON, regardless of skill:

```json
{
  "meta": {
    "slug": "string",
    "subjectName": "string",
    "skillName": "buyer-intelligence | supplier-intelligence | sector-intelligence | incumbency-advantage-displacement-strategy",
    "version": "x.y.z",
    "mode": "build | refresh | inject | amend",
    "builtDate": "YYYY-MM-DD",
    "lastModifiedDate": "YYYY-MM-DD",
    "refreshDue": "YYYY-MM-DD",
    "sourceCount": 0,
    "internalSourceCount": 0,
    "depthMode": "snapshot | standard | deep",
    "degradedMode": false,
    "degradedModeReason": null,
    "prerequisitesPresentAt": { /* see section 8 */ },
    "versionLog": [ /* see section 4 */ ]
  },
  "changeSummary": [ /* see section 5, empty on build */ ],
  "sourceRegister": { /* see section 6 */ },
  /* skill-specific sections follow */
}
```

Skills can extend this with their own sections but must not omit any of the
universal fields.

---

## 12. The integrator pattern in full

Integrator skills (today: incumbency; future: any skill that synthesises
across producer outputs) carry additional discipline beyond the universal
spec:

1. **Required prerequisites are real** — the skill refuses if absent, with
   a clear "run X first" instruction.
2. **Producer artefacts are read, not re-derived** — the integrator does not
   re-research the buyer or the incumbent; it consumes the buyer/supplier
   dossiers via MCP read tools.
3. **Conflicts between producer artefacts are flagged**, not silently
   resolved. If the supplier dossier says one thing and the buyer dossier
   implies another, the integrator surfaces the conflict for human resolution.
4. **The integrator's output is itself a producer artefact** — i.e. another
   downstream integrator (e.g. a future "win-strategy" agent) can consume it
   the same way this one consumes its inputs.
5. **The artefact-arrival refresh trigger is mandatory** — integrator outputs
   are most affected by upstream artefact arrival, so the targeted-refresh
   pattern is load-bearing for them.

---

## 13. Open question — orchestrator role

This spec defines the contract each skill exposes. It does **not** define
the agent that reads those contracts and decides what to run when. That
orchestrator role is currently undefined in the platform architecture and
is parked at `wiki/actions/pwin-plugin-orchestration-agent.md`.

The spec is designed so that an orchestrator, when built, has a uniform
API to read against:

- `meta.prerequisitesPresentAt` tells the orchestrator what evidence the
  artefact was built on
- The skill's declared `prerequisites` block tells the orchestrator what
  needs to exist before this skill can run
- The artefact-arrival refresh trigger tells the orchestrator what to
  invoke when an upstream artefact appears
- The version log and change summary tell the orchestrator what has changed
  since its last poll

Until the orchestrator exists, the consultant plays the role manually. The
spec is the documentation of what the consultant has to track — and the
target API for when we automate it.
