# Section-specific notes

Detailed guidance for sections of the dossier that need special handling
beyond the schema. These notes apply across all four modes.

---

## Hypothesis sections (Sections 4 and 6)

Sections 4 (`commissioningContextHypotheses`) and 6
(`decisionUnitAssumptions`) are explicitly interpretive. Every field in
these sections must have `type: "inference"`. Include the fixed caveats:

- **Section 4 caveat:** "These are hypotheses derived from available
  evidence. They require validation by the pursuit team."
- **Section 6 caveat:** "Inferred from published structures and
  procurement patterns. Requires pursuit-team validation."

### Buying cycle timing fields (Section 4)

Infer `commissioningCycleStage`, `approvalsPending`,
`marketEngagementLikelihood`, `buyingReadiness`, and `timelineRisks`
from procurement notices, planning notice data, and market engagement
signals. `buyingReadiness` must be one of: `pre-pipeline`,
`pipeline-identified`, `pre-market-engagement`,
`post-market-engagement`, `procurement-live`, `awarded`.

### Spend classification (Section 4)

Infer `spendClassification` from the strategic context:

- **mandatory** — legal, regulatory, or contractual obligation to
  procure (cannot defer or descope)
- **discretionary** — optional spend; could be deferred, descoped, or
  cancelled if pressure rises
- **reactive** — triggered by a specific event (audit finding,
  programme failure, incident, ministerial direction)
- **strategic** — tied to a strategic agenda (transformation,
  modernisation, savings programme); political commitment
- **mixed** — components of multiple classifications
- **unknown** — insufficient evidence to classify

The classification directly shapes pursuit confidence in downstream
consumers.

### Per-role interests, tensions, dominant lens (Section 6)

`decisionUnitAssumptions.perRoleInterests` is the cast list with
substance — what each role actually optimises for, with evidence basis.
`internalTensions` names the friction points between roles.
`dominantDecisionLens` is the headline judgement: which lens
(commercial / operational / political / technical / financial) carries
the most weight in this buyer's decisions.

All three are inferences. Look for evidence in: procurement weighting
patterns, public statements, prior award rationales, and audit
findings.

### Exception for amend mode

When the account team provides direct knowledge of commissioning cycle
stage, decision unit composition, per-role interests, or internal
tensions, those fields may be upgraded from `inference` to `fact` with
Tier 5 sourcing. The section caveat remains, but the individual field
reflects the internal evidence.

---

## Supplier ecosystem (Section 9)

For each incumbent supplier, capture:

- What they deliver (`serviceLines` from the 13-category taxonomy)
- Contract count and total value
- Relationship length (`longestRelationship`)
- Strategic importance (`critical | major | moderate | minor`)
- Recent activity trend (`growing | stable | thinning`)
- Entrenchment indicators: systems, TUPE workforce, data, relationships,
  scope creep history, IP held
- Vulnerability signals (the displacement-opportunity layer): cancelled
  contracts, audit findings, performance issues, public complaints,
  early terminations, leadership departures at the supplier, with an
  overall vulnerability rating (`high | medium | low | none`)
- Link to supplier dossier if one exists (`dossierRef`)

Also identify:

- `adjacentSuppliers` — present in the buyer's broader supplier base
  but not currently incumbents on the relevant scope
- `supplierConcentration` — how concentrated spend is across suppliers
- `switchingEvidence` — historical record of the buyer displacing
  incumbents
- `marketRefreshAreas` — categories where the buyer has signalled
  intent to broaden the supplier base
- `barriersToEntry` — frameworks not accessible, accreditations
  required, security clearance levels, named domain expertise,
  prior-experience thresholds

### Framework and shared service nuance

Note whether the buyer procures through shared service arrangements
(e.g., NHS SBS, CCS, police collaborative hubs). Capture in
`procurementBehaviour.sharedServiceArrangements`. Distinguish between
CCS call-off, CCS further competition, and open-market FTS procedures.

### SME obligations and social value

Note published SME spend targets, social enterprise preferences, or
PPN 06/20 social value weightings. Capture in
`cultureAndPreferences.socialValueAndESG`.

---

## Relationship history (Section 10)

Draws entirely from **Tier 5 internal sources**. In most initial builds
no Tier 5 data will be available. When absent:

- Set `sectionConfidence` to `"none"`
- Set `tierNote` to "No Tier 5 data provided. All fields require
  account team input before this section is usable."
- Populate `intelGaps` with the sub-fields needing internal validation
- **Do NOT infer relationship history from public procurement data** —
  an FTS award does not imply any relationship with the bidder
- Open Tier 5 amend actions in `actionRegister.actions` with owner
  `account-director`

When Tier 5 data is provided (via BUILD input, AMEND, or INJECT of
internal documents), capture: prior contracts, active programmes, past
bids (with outcomes and feedback), executive relationships, named
advocates, named blockers, and intelligence gaps flagged by the account
team.

This section is the primary target for **amend mode** operations.

---

## Pursuit implications (Section 14)

The seventh-lens section. Buyer-derived, bidder-neutral implications.
Things any pursuit against this buyer should observe regardless of who
is bidding. See the categories in `references/output-schema.md`:
`stance`, `language`, `evidence`, `commercial`, `engagement`,
`risk-management`, `timing`, `structural`.

This section is mandatory in standard and deep modes. Common sources:

- **NAO/PAC reports** — surface evidence and risk-management
  implications (over-evidence delivery confidence; expect aggressive
  scrutiny on commercial controls)
- **Annual reports** — surface stance and language implications
  (foreword language tells you what the Permanent Secretary endorses)
- **Digital strategies** — surface stance and structural implications
  (build-vs-buy posture, supplier consolidation direction)
- **Senior leadership announcements** — surface engagement and
  risk-management implications (new SRO career risk; new minister
  priority shift)
- **Tier 5 amend** — surface engagement and risk-management
  implications that public sources cannot (named blockers, internal
  tensions)

Each implication must be backed by specific evidence (sourceRefs)
and tagged to:

- At least one `linkedFrameworkQuestion` (e.g. `A1: change-driver`)
- At least one `derivedFromLens` from the other six lenses

---

## Degraded mode

If, after completing web searches, you have fewer than 3 usable sources
(excluding FTS data), the dossier is **data-insufficient**. Most likely
for: recently created organisations, small NDPBs, devolved bodies with
limited English-language publications, or recently restructured/renamed
organisations.

In degraded mode:

1. Auto-downgrade to snapshot depth regardless of requested mode.
2. Set `meta.depthMode` to `"snapshot-data-insufficient"`.
3. Set `meta.degradedReason` to a brief description of why data is thin.
4. Populate only: `buyerSnapshot`, `procurementBehaviour`,
   `procurementBehaviourSnapshot`, `sourceRegister`, and
   `risksAndSensitivities` (with intel gaps).
5. Set all other sections to null.
6. Populate `actionRegister.actions` heavily — every section that is
   null should have at least one action describing what would resolve
   it.
7. In `buyerSnapshot.executiveSummary`, list the specific research
   steps needed to complete a full standard dossier.

An honest partial picture is more useful than a structurally complete
but substantively hollow output.
