# Source Classification Reference

This reference maps common document types to the dossier schema sections
they inform. Used by the **inject** and **amend** modes to determine which
sections to update when a new source is provided.

---

## Classification matrix

| Document type | Primary sections | Secondary sections | Typical tier |
|---|---|---|---|
| Annual report and accounts | organisationContext, strategicPriorities, procurementBehaviour | commercialAndRiskPosture, buyerSnapshot | Tier 1 |
| Strategy document / corporate plan | strategicPriorities, commissioningContextHypotheses | cultureAndPreferences, buyerSnapshot | Tier 1 |
| Digital strategy | strategicPriorities, cultureAndPreferences (changeMaturity), commissioningContextHypotheses | procurementBehaviour | Tier 1 |
| Commercial / procurement strategy | procurementBehaviour, cultureAndPreferences | commissioningContextHypotheses, decisionUnitAssumptions | Tier 1 |
| Organisational chart / organogram | organisationContext, decisionUnitAssumptions | buyerSnapshot | Tier 1 |
| Board papers / minutes | organisationContext, strategicPriorities | cultureAndPreferences, risksAndSensitivities | Tier 1 |
| NAO report / audit report | risksAndSensitivities, commercialAndRiskPosture | strategicPriorities, procurementBehaviour | Tier 1 |
| PAC / select committee report | risksAndSensitivities, strategicPriorities | cultureAndPreferences, commercialAndRiskPosture | Tier 1 |
| Spending review / estimates | organisationContext (fundingModel), commercialAndRiskPosture | strategicPriorities | Tier 1 |
| Procurement notice (FTS/CF) | procurementBehaviour, supplierEcosystem | commissioningContextHypotheses | Tier 2 |
| Contract award notice | supplierEcosystem, procurementBehaviour | commissioningContextHypotheses | Tier 2 |
| Planning notice / PIN | commissioningContextHypotheses, procurementBehaviour | supplierEcosystem | Tier 2 |
| Framework documentation | procurementBehaviour | supplierEcosystem | Tier 2 |
| Spending data (>£25k) | procurementBehaviour, supplierEcosystem | — | Tier 2 |
| Media article | risksAndSensitivities, strategicPriorities | organisationContext | Tier 3 |
| Think tank / policy analysis | strategicPriorities, cultureAndPreferences | commissioningContextHypotheses | Tier 3 |
| Industry briefing / market event notes | commissioningContextHypotheses, procurementBehaviour | cultureAndPreferences, decisionUnitAssumptions | Tier 3 |
| Sector briefing | strategicPriorities, risksAndSensitivities | commissioningContextHypotheses | Tier 3 |
| CRM / account plan | relationshipHistory | decisionUnitAssumptions | Tier 4 |
| Meeting notes (internal) | relationshipHistory, decisionUnitAssumptions | — | Tier 4 |
| Prior bid / feedback report | relationshipHistory | decisionUnitAssumptions | Tier 4 |
| Capture notes / intel log | relationshipHistory, decisionUnitAssumptions | commissioningContextHypotheses | Tier 4 |

---

## Classification rules

1. **Auto-classify first, then confirm.** When a source is injected, classify
   it against this matrix based on document type. If the document type is
   ambiguous, read the content and classify based on what it actually contains.

2. **Primary sections are always updated.** If the source contains relevant
   information for a primary section, that section must be updated.

3. **Secondary sections are updated only if the source contains material
   evidence.** Do not update a secondary section just because the document type
   maps to it — only if the specific content warrants it.

4. **A single source can inform multiple sections.** An annual report will
   typically update 4–6 sections. A procurement notice may only update 1–2.

5. **Tier assignment follows the source hierarchy.** Refer to
   `source-hierarchy.md` for the full tier definitions and confidence
   calibration rules.

---

## Section update rules for inject mode

When updating a section from an injected source:

### Replace rules
- **Replace** the field value when the new source provides a more authoritative
  or more recent answer to the same question. Update sourceRefs to include
  both old and new source IDs. Note the change in rationale.
- **Example:** An organogram replaces an inferred organisationStructure field
  that was previously based on web search.

### Extend rules
- **Extend** the field value when the new source adds information that
  complements rather than contradicts the existing value. Append new detail,
  add the source to sourceRefs, and extend the rationale.
- **Example:** A digital strategy adds detail to strategicPriorities themes
  already captured from a web search.

### Upgrade rules
- **Upgrade** the field's `type` from `inference` to `fact` when the new source
  provides direct evidence for something previously inferred. Update the
  rationale to explain the upgrade. Upgrade `confidence` if the new source
  meets the threshold (e.g., second corroborating Tier 1 source → high).
- **Example:** A published organogram upgrades an inferred
  organisationStructure from `type: inference` to `type: fact`.

### Gap clearance rules
- When an injected source fills a gap listed in `sourceRegister.gaps`,
  remove that entry from the gaps array.
- When an injected source resolves an entry in
  `decisionUnitAssumptions.intelligenceGaps` or
  `relationshipHistory.intelGaps`, remove that entry.
- When a gap is partially resolved, update the gap description to reflect
  what remains unknown.

---

## Section update rules for amend mode

Amend mode handles Tier 4 internal intelligence — plain-language statements
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
| "[Person] is an advocate/blocker" | relationshipHistory.knownAdvocates or knownBlockers |
| "We have a relationship with [person]" | relationshipHistory.executiveRelationships |
| "Their [attribute] is [value]" | Contextual — match to the relevant section field |

### Source registration for amends
Each amend creates a Tier 4 internal source:
```json
{
  "sourceId": "SRC-INT-001",
  "sourceName": "Account team input — [brief description]",
  "sourceType": "internal",
  "publicationDate": null,
  "accessDate": "[today's date]",
  "reliability": "Tier 4",
  "sectionsSupported": ["[target section]"],
  "url": null
}
```

Internal source IDs use the `SRC-INT-` prefix to distinguish them from
external sources. They are numbered sequentially: SRC-INT-001, SRC-INT-002.

### Tier 4 confidence rules
- A single Tier 4 source from a credible account team member: `confidence: medium`
- Corroborated by a second Tier 4 source or a Tier 1–3 source: `confidence: high`
- Unverified or second-hand: `confidence: low`
- Default to `medium` unless the user indicates uncertainty
