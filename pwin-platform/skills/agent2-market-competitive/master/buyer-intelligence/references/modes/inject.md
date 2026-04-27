# INJECT Mode Workflow

Inject mode adds a single source document to an existing dossier and
updates only the sections that source informs. No web searches. No FTS
calls.

---

## Prerequisites

- An existing dossier must be in the intel cache at
  `C:\Users\User\.pwin\intel\buyers\<buyer-slug>-dossier.json`
- If no existing dossier is found, tell the user and offer to BUILD instead.

---

## Inject workflow

1. **Load existing dossier** from the intel cache.

2. **Read the source.** Depending on input type:
   - **File path** (PDF, DOCX, etc.) — use the Read tool or bash to extract
     text content. For PDFs, use the PDF skill or `read_pdf_bytes` if
     available.
   - **URL** — use `web_fetch` to retrieve the content.
   - **Pasted text** — use the content directly from the user's message.

3. **Classify the source.** Read `references/source-classification.md` for
   the full classification matrix. Determine:
   - Document type (annual report, strategy document, organogram, etc.)
   - Tier assignment (1–5)
   - Primary lenses it contributes to
   - Primary sections it informs
   - Secondary sections it may inform (only if content warrants it)
   - Whether a dedicated extraction template exists in
     `references/extraction-templates/`

4. **Apply extraction template if available.** If the document type has a
   dedicated template (rightmost column of `source-classification.md`),
   load the template and run the structured extraction before applying
   updates. The template's `dossierMappings` block tells you exactly
   which dossier fields to update with which operation. Record the
   application in `meta.extractionTemplatesApplied`.

5. **Report classification to user.** Before making changes, briefly state:
   - What the document is
   - Which lenses and sections will be updated
   - Whether any gaps will be cleared
   - Which actions in `actionRegister` will close
   This gives the user a chance to correct the classification if wrong.

6. **Extract intelligence from the source.** For each affected section,
   identify the specific fields to update and what the new evidence says
   about them.

7. **Apply updates to the dossier.** For each affected field, apply one of
   three operations (see `references/source-classification.md` for full
   rules):
   - **Replace** — new source is more authoritative or more recent
   - **Extend** — new source adds complementary information
   - **Upgrade** — new source converts an inference to a fact or raises
     confidence
   Preserve all existing evidence that is not contradicted by the new
   source.

8. **Update the source register:**
   - Add the new source with the next sequential ID (continue from the
     highest existing SRC-nnn ID, not SRC-INT-nnn)
   - Tag with `lensesContributed`
   - Set `extractionTemplateApplied` if a template was used
   - Clear any matching entries from `sourceRegister.gaps`
   - Clear any matching entries from
     `decisionUnitAssumptions.intelligenceGaps`
   - Update `sourceRegister.staleFields` if the new source refreshes a
     stale field
   - Update `sourceRegister.lowConfidenceInferences` if an inference is
     upgraded

9. **Close actions.** For every action in `actionRegister.actions` that
   the new source resolves, set `status: "closed"` and populate the
   `closure` block with `closedAt`, `closedInVersion`, `closedBy: "inject"`,
   `closingSourceId`, and a `closureNote`. May also open new actions if
   the source surfaces new gaps.

10. **Update the section confidence levels.** If the injected source
    raises a section from single-source to multi-source, or from Tier 3
    to Tier 1–2, upgrade the section confidence accordingly.

11. **Refresh pursuit implications.** If the new source surfaces
    buyer-derived pursuit implications, append them to
    `pursuitImplications.implications` with their category, rationale,
    sourceRefs, and lens linkage.

12. **Produce a change summary.** Populate `changeSummary` with every
    field that changed: section, field, previous value summary, new
    value summary, and reason for change.

13. **Update meta:**
    - Increment version as patch: x.y.z → x.y.(z+1)
    - Add entry to `versionLog` with mode: "inject", date, and summary
    - Update `sourcesSummary` to reflect new source count
    - Do NOT change `refreshDue` — inject does not reset the refresh
      schedule

14. **Re-render HTML** using the same renderer script as BUILD mode.

15. **Save both files** to the intel cache and workspace folder.

16. **Report to user:** Summarise what changed, which actions closed,
    which gaps were cleared, and what remains unknown. Provide
    `computer://` links to both files.

---

## Inject mode constraints

- **No web searches.** Inject mode processes only the provided source.
- **No FTS calls.** Use the existing procurement data in the dossier.
- **No section deletion.** Inject only adds or updates — it never removes
  information from the dossier unless the new source explicitly
  contradicts it.
- **Source register is append-only.** New sources are added; existing
  sources are never removed.
- **Action register IDs are append-only.** Closed actions retain their
  ACT-nnn ID; do not renumber.
