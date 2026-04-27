# AMEND Mode Workflow

Amend mode adds Tier 5 internal intelligence from plain-language
statements. No documents, no web searches — just the account team's
knowledge filed into the right place.

---

## Prerequisites

- Same as inject: an existing dossier must be in the intel cache at
  `C:\Users\User\.pwin\intel\buyers\<buyer-slug>-dossier.json`
- If no existing dossier is found, tell the user and offer to BUILD instead.

---

## Amend workflow

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
   - Which actions in `actionRegister` will close
   This gives the user a chance to correct before changes are applied.

4. **Apply the updates.** For each target field:
   - Set or update the field value
   - Set `type: "fact"` (Tier 5 internal knowledge is factual to the
     organisation, even if unverifiable from public sources)
   - Set `confidence` per the Tier 5 confidence rules in
     `references/source-classification.md`
   - Set `rationale` to explain the source (e.g., "Account team input
     from CAEHRS industry day, April 2025")
   - Add the internal source ID to `sourceRefs`

5. **Register the internal source.** Add to `sourceRegister.sources`:

   ```json
   {
     "sourceId": "SRC-INT-nnn",
     "sourceName": "Account team input — [brief description]",
     "sourceType": "internal",
     "publicationDate": null,
     "accessDate": "[today's date]",
     "reliability": "Tier 5",
     "sectionsSupported": ["[target sections]"],
     "lensesContributed": ["supplier-landscape"],
     "extractionTemplateApplied": null,
     "url": null
   }
   ```

   Internal source IDs use the `SRC-INT-` prefix and are numbered
   sequentially, independent of external source IDs.

6. **Clear intelligence gaps.** Remove any matching entries from:
   - `decisionUnitAssumptions.intelligenceGaps`
   - `relationshipHistory.intelGaps`
   - `sourceRegister.gaps` (only if the amend resolves a data gap, not
     just adds relationship context)

7. **Close actions.** For every action in `actionRegister.actions` of
   `type: "tier4-amend"` that this statement resolves, set `status: "closed"`
   and populate the `closure` block with `closedAt`, `closedInVersion`,
   `closedBy: "amend"`, `closingSourceId: "SRC-INT-nnn"`, and a `closureNote`.

8. **Update section confidence.** If this is the first Tier 5 data for
   `relationshipHistory`, upgrade `sectionConfidence` from `"none"` to
   `"low"` (single internal source) or `"medium"` (multiple internal
   sources). Update `tierNote` to reflect that Tier 5 data is now
   partially available.

9. **Update pursuit implications.** Tier 5 intel often surfaces
   pursuit implications that public sources cannot — known advocates,
   internal tensions, blocker dynamics. Append to
   `pursuitImplications.implications` where applicable, with sourceRefs
   pointing to the SRC-INT-nnn ID.

10. **Produce a change summary.** Same format as inject mode.

11. **Update meta:**
    - Increment version as patch: x.y.z → x.y.(z+1)
    - Add entry to `versionLog` with mode: "amend", date, and summary
    - Update `sourcesSummary`

12. **Re-render HTML and save both files.**

13. **Report to user:** Summarise what was filed, which actions closed,
    which gaps were cleared, and what internal intelligence is still
    missing.

---

## Amend mode constraints

- **Tier 5 only.** Amend is for internal intelligence. If the user is
  providing a formal document, redirect to inject mode.
- **Preserve existing Tier 1–3 data.** Amend never overwrites publicly
  sourced facts with internal assertions. If there is a conflict, flag
  it and ask the user which is correct.
- **No web searches, no FTS calls.**
- **Multiple amends in one session.** The user may provide several
  pieces of intel in sequence. Process each as a separate amend
  operation against the same dossier, incrementing the patch version
  each time.
