# Source Classification Reference

This reference maps common document types to:

1. The dossier sections they inform (used by inject and amend modes)
2. The intelligence lenses they primarily contribute to
3. The tier they belong to (under the 5-tier hierarchy in `source-hierarchy.md`)
4. Whether a dedicated extraction template exists for the document type

---

## Classification matrix

| Document type | Primary sections | Secondary sections | Primary lenses | Tier | Extraction template |
|---|---|---|---|---|---|
| Annual Report and Accounts | organisationContext, strategicPriorities, procurementBehaviour, risksAndSensitivities | commercialAndRiskPosture, buyerSnapshot | money, pressure, risk-posture | Tier 1 | `annual-report.md` |
| Outcome Delivery Plan / Single Departmental Plan | strategicPriorities, commissioningContextHypotheses | buyerSnapshot, cultureAndPreferences | mandate, pressure | Tier 1 | `departmental-plan.md` |
| Departmental Strategy / Corporate Plan | strategicPriorities, commissioningContextHypotheses | cultureAndPreferences, buyerSnapshot | pressure, mandate | Tier 1 | `departmental-plan.md` |
| Digital / transformation strategy | strategicPriorities, cultureAndPreferences (changeMaturity), commissioningContextHypotheses | procurementBehaviour, pursuitImplications | pressure, money, buying-behaviour, pursuit-implications | Tier 1 | `digital-strategy.md` |
| Data strategy or data roadmap | strategicPriorities, cultureAndPreferences | commissioningContextHypotheses, supplierEcosystem | pressure, buying-behaviour | Tier 1 | (covered by `digital-strategy.md`) |
| AI strategy / AI Action Plan / AI ethics framework | strategicPriorities, cultureAndPreferences, commercialAndRiskPosture | commissioningContextHypotheses | pressure, risk-posture | Tier 1 | (covered by `digital-strategy.md`) |
| Cyber security strategy | strategicPriorities, commercialAndRiskPosture, cultureAndPreferences | supplierEcosystem (barriersToEntry) | risk-posture, pressure | Tier 1 | `cyber-strategy.md` |
| Workforce / People plan | strategicPriorities, commissioningContextHypotheses, cultureAndPreferences | commercialAndRiskPosture | mandate, pressure | Tier 1 | `workforce-strategy.md` |
| Estate / sustainability strategy | strategicPriorities | commercialAndRiskPosture | pressure, risk-posture | Tier 1 | — |
| Commercial / procurement strategy | procurementBehaviour, cultureAndPreferences, commercialAndRiskPosture | commissioningContextHypotheses, decisionUnitAssumptions | buying-behaviour, money | Tier 1 | `commercial-strategy.md` |
| Efficiency / productivity plan | commissioningContextHypotheses, commercialAndRiskPosture | strategicPriorities | money, pressure | Tier 1 | — |
| Commercial pipeline / pipeline notices | commissioningContextHypotheses, procurementBehaviour | supplierEcosystem | buying-behaviour, pressure | Tier 1 | — |
| Procurement page (`doing business with us`) | procurementBehaviour | commercialAndRiskPosture | buying-behaviour | Tier 1 | — |
| Organogram / organisational chart | organisationContext, decisionUnitAssumptions | buyerSnapshot | mandate | Tier 1 | — |
| Board papers / minutes | organisationContext, strategicPriorities, decisionUnitAssumptions | cultureAndPreferences, risksAndSensitivities | mandate, pressure | Tier 1 | — |
| Senior leadership announcement / press release | organisationContext (seniorLeadership, recentChanges), decisionUnitAssumptions | strategicPriorities | mandate, pressure | Tier 1 | `leadership-announcement.md` |
| Spending Review settlement | commercialAndRiskPosture, commissioningContextHypotheses, organisationContext (fundingModel) | strategicPriorities | money, pressure | Tier 2 | `spending-review-settlement.md` |
| Main / Supplementary Estimates | commercialAndRiskPosture, organisationContext (fundingModel) | strategicPriorities | money | Tier 2 | — |
| HMT Green Book / Managing Public Money guidance | commercialAndRiskPosture, decisionUnitAssumptions | cultureAndPreferences | money, risk-posture | Tier 2 | — |
| DDaT Playbook / AI Playbook | cultureAndPreferences, commercialAndRiskPosture | commissioningContextHypotheses | risk-posture, buying-behaviour | Tier 2 | — |
| Cabinet Office commercial guidance | procurementBehaviour, cultureAndPreferences, commercialAndRiskPosture | — | buying-behaviour, money | Tier 2 | — |
| Government Functional Standards | cultureAndPreferences, commercialAndRiskPosture | decisionUnitAssumptions | risk-posture | Tier 2 | — |
| Major Projects Portfolio (IPA / GMPP) data | strategicPriorities (majorProgrammes), risksAndSensitivities, supplierEcosystem | commissioningContextHypotheses | pressure, supplier-landscape, risk-posture | Tier 2 | `gmpp-entry.md` |
| NAO value-for-money report | risksAndSensitivities, commercialAndRiskPosture, supplierEcosystem (vulnerabilitySignals), pursuitImplications | strategicPriorities, procurementBehaviour, cultureAndPreferences | risk-posture, pressure, supplier-landscape, pursuit-implications | Tier 3 | `nao-pac-report.md` |
| PAC report | risksAndSensitivities, strategicPriorities, supplierEcosystem (vulnerabilitySignals), pursuitImplications | cultureAndPreferences, commercialAndRiskPosture | risk-posture, pressure, pursuit-implications | Tier 3 | (covered by `nao-pac-report.md`) |
| Select committee report | risksAndSensitivities, strategicPriorities | cultureAndPreferences | pressure, risk-posture | Tier 3 | (covered by `nao-pac-report.md`) |
| Inspectorate / regulator report | risksAndSensitivities, supplierEcosystem (vulnerabilitySignals) | commercialAndRiskPosture | risk-posture, supplier-landscape | Tier 3 | — |
| Ombudsman report | risksAndSensitivities | cultureAndPreferences | risk-posture | Tier 3 | — |
| Independent review / commission | strategicPriorities, risksAndSensitivities | cultureAndPreferences, organisationContext | pressure, risk-posture | Tier 3 | — |
| Procurement notice (FTS / Contracts Finder) | procurementBehaviour, supplierEcosystem | commissioningContextHypotheses | buying-behaviour, supplier-landscape | Tier 4 | — |
| Contract award notice | supplierEcosystem, procurementBehaviour | commissioningContextHypotheses | supplier-landscape, buying-behaviour | Tier 4 | — |
| Planning notice / PIN | commissioningContextHypotheses, procurementBehaviour | supplierEcosystem | buying-behaviour, pressure | Tier 4 | — |
| Framework documentation | procurementBehaviour, supplierEcosystem (barriersToEntry) | commercialAndRiskPosture | buying-behaviour, supplier-landscape | Tier 4 | — |
| Spend transparency data (>£25k) | procurementBehaviour, supplierEcosystem | — | buying-behaviour, supplier-landscape | Tier 4 | — |
| Tussell or commercial procurement database | procurementBehaviour, supplierEcosystem, procurementBehaviourSnapshot | — | buying-behaviour, supplier-landscape | Tier 4 | — |
| Media article | risksAndSensitivities, strategicPriorities | organisationContext | risk-posture, pressure | Tier 3 (mostly) | — |
| Think tank / policy analysis | strategicPriorities, cultureAndPreferences | commissioningContextHypotheses | pressure | Tier 3 | — |
| CRM / account plan | relationshipHistory | decisionUnitAssumptions | supplier-landscape | Tier 5 | — |
| Meeting notes (internal) | relationshipHistory, decisionUnitAssumptions | — | supplier-landscape | Tier 5 | — |
| Prior bid / feedback report | relationshipHistory | decisionUnitAssumptions, cultureAndPreferences | supplier-landscape, pursuit-implications | Tier 5 | — |
| Capture notes / intel log | relationshipHistory, decisionUnitAssumptions | commissioningContextHypotheses | supplier-landscape | Tier 5 | — |

---

## Classification rules

1. **Auto-classify first, then confirm.** When a source is injected, classify
   it against this matrix based on document type. If the document type is
   ambiguous, read the content and classify based on what it actually contains.

2. **Primary sections are always updated.** If the source contains relevant
   information for a primary section, that section must be updated.

3. **Secondary sections are updated only if the source contains material
   evidence.** Do not update a secondary section just because the document
   type maps to it — only if the specific content warrants it.

4. **Lens tagging is mandatory.** When a source is registered, the
   `lensesContributed` field must list at least one of the seven lenses.
   Use the "Primary lenses" column above as the starting point; add
   secondary lenses if the document substantively informs them.

5. **A single source can inform multiple sections.** An annual report will
   typically update 4–6 sections and 3–4 lenses. A procurement notice may
   only update 1–2 sections and 1–2 lenses.

6. **Tier assignment follows the 5-tier hierarchy.** Refer to
   `source-hierarchy.md` for the full tier definitions and confidence
   calibration rules.

7. **Apply the extraction template if one exists.** When the document type
   has a dedicated template (see the rightmost column), load and apply it
   before writing into the dossier. Templates live in
   `references/extraction-templates/`. The template's `dossierMappings`
   array tells you which fields to update with which operation.

---

## Section update rules for inject mode

When updating a section from an injected source:

### Replace rules
- **Replace** the field value when the new source provides a more
  authoritative or more recent answer to the same question. Update sourceRefs
  to include both old and new source IDs. Note the change in rationale.
- **Example:** An organogram replaces an inferred organisationStructure field
  that was previously based on web search.

### Extend rules
- **Extend** the field value when the new source adds information that
  complements rather than contradicts the existing value. Append new detail,
  add the source to sourceRefs, and extend the rationale.
- **Example:** A digital strategy adds detail to strategicPriorities themes
  already captured from a web search.

### Upgrade rules
- **Upgrade** the field's `type` from `inference` to `fact` when the new
  source provides direct evidence for something previously inferred. Update
  the rationale to explain the upgrade. Upgrade `confidence` if the new
  source meets the threshold (e.g., second corroborating Tier 1 source →
  high).
- **Example:** A published organogram upgrades an inferred
  organisationStructure from `type: inference` to `type: fact`.

### Gap clearance rules
- When an injected source fills a gap listed in `sourceRegister.gaps`,
  remove that entry from the gaps array.
- When an injected source resolves an entry in
  `decisionUnitAssumptions.intelligenceGaps` or
  `relationshipHistory.intelGaps`, remove that entry.
- When an injected source closes one or more open actions in
  `actionRegister.actions`, set their `status` to `closed` and populate the
  `closure` block with `closedAt`, `closedInVersion`, `closedBy: "inject"`,
  `closingSourceId`, and a `closureNote`.
- When a gap is partially resolved, update the gap description to reflect
  what remains unknown, and lower the priority of the corresponding action
  if appropriate.

---

## Section update rules for amend mode

Amend mode handles Tier 5 internal intelligence — plain-language statements
from the account team, not formal documents.

### Target field identification
Parse the user's statement to identify which field(s) it informs:

| Statement pattern | Target field |
|---|---|
| "We know [person] is [role]" | decisionUnitAssumptions (relevant role array) |
| "The [role] is [person]" | organisationContext.seniorLeadership or decisionUnitAssumptions |
| "We bid for [opportunity] and [outcome]" | relationshipHistory.pastBids |
| "We have a contract for [description]" | relationshipHistory.priorContracts |
| "We're working on [programme]" | relationshipHistory.activeProgrammes |
| "[Person] is an advocate / blocker" | relationshipHistory.knownAdvocates or knownBlockers |
| "We have a relationship with [person]" | relationshipHistory.executiveRelationships |
| "Their [attribute] is [value]" | Contextual — match to the relevant section field |
| "The commercial team prefers [pattern]" | decisionUnitAssumptions.perRoleInterests.commercial |
| "The internal tension is [pattern]" | decisionUnitAssumptions.internalTensions |

### Source registration for amends
Each amend creates a Tier 5 internal source:
```json
{
  "sourceId": "SRC-INT-001",
  "sourceName": "Account team input — [brief description]",
  "sourceType": "internal",
  "publicationDate": null,
  "accessDate": "[today's date]",
  "reliability": "Tier 5",
  "sectionsSupported": ["[target section]"],
  "lensesContributed": ["supplier-landscape"],
  "extractionTemplateApplied": null,
  "url": null
}
```

Internal source IDs use the `SRC-INT-` prefix to distinguish them from
external sources. They are numbered sequentially: SRC-INT-001, SRC-INT-002.

### Tier 5 confidence rules
- A single Tier 5 source from a credible account team member: `confidence: medium`
- Corroborated by a second Tier 5 source or a Tier 1–3 source: `confidence: high`
- Unverified or second-hand: `confidence: low`
- Default to `medium` unless the user indicates uncertainty

### Action register interaction
- Amend mode closes Tier 5 actions in the action register (those with
  `type: tier4-amend` from the legacy naming, or `type: tier5-amend` going
  forward — both interpretations close the same way).
- When the amend resolves an action, populate the `closure` block with
  `closedBy: "amend"` and `closingSourceId: "SRC-INT-nnn"`.
