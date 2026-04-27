# REFRESH Mode Workflow

When `existingProfile` is provided (or found in
`~/.pwin/intel/buyers/`), and the user requests a refresh (or the
`refreshDue` date has passed), you are **refreshing**, not building from
scratch.

---

## Refresh triggers

Run a refresh when any of the following is true:

| Trigger | Type | Description |
|---|---|---|
| Time-based | Periodic | `meta.refreshDue` date has passed (default 6 months) |
| Change-based | Reactive | Leadership change, machinery of government change, new strategy document, NAO/PAC critical report, spending review affecting the buyer, organisational restructure |
| Source-arrival | Reactive | A new document is provided — handle via `inject` mode, not refresh |
| Artefact-arrival | Reactive | A previously-missing prerequisite has now been produced (e.g. FTS data became available; sector brief now exists) — run a targeted refresh of the affected sections only |

For artefact-arrival refresh, re-derive only the sections whose `affects`
list (in the Prerequisites section of `SKILL.md`) includes the
newly-arrived prerequisite. Leave all other sections intact. Record the
prerequisite arrival in the version log: `"summary": "FTS data now
available — refreshed procurementBehaviour and supplierEcosystem."`

---

## Refresh workflow

1. **Re-run Step 0** to fetch latest FTS data — compare against cached
   version to detect new contracts or incumbent changes. Re-pull the
   `get_buyer_behaviour_profile` snapshot.

2. **Re-run targeted searches** for sections most likely to have changed:
   organisation context (leadership, structure, recentChanges), strategic
   priorities, and risks and sensitivities. In deep refreshes, re-canvas
   the full Tier 1 retrieval checklist.

3. **Preserve Tier 5 data.** Carry forward `relationshipHistory` content
   that is not contradicted by new information. Do NOT clear internal
   data because it was not re-provided. Preserve all SRC-INT-nnn sources.

4. **Merge findings.** Replace values when new evidence updates them;
   extend rationale when new evidence adds nuance.

5. **Extend the source register.** Append new sources continuing from
   the previous highest ID — do not restart at SRC-001. Tag every new
   source with `lensesContributed`.

6. **Re-evaluate the action register.** For each open action:
   - If new evidence resolves it, mark `status: "closed"` with
     `closedBy: "refresh"`.
   - If the action is still open, re-evaluate priority — has the
     underlying decision urgency changed?
   - If new gaps have surfaced, open new actions with sequential IDs.

7. **Refresh the procurement behaviour snapshot.** Update
   `procurementBehaviourSnapshot` with the latest signals. Set
   `snapshotTakenAt` to now.

8. **Re-derive pursuit implications.** New audit findings, new
   leadership, new programme failures all surface new buyer-derived
   implications. Existing implications that have been resolved by
   buyer action should be removed; new ones appended.

9. **Produce a `changeSummary`.** List material changes by section with
   field, previous value summary, new value summary, and reason for
   change.

10. **Increment `meta.version`** as minor: x.y → x.(y+1). Reset patch to
    0. Add a `versionLog` entry with mode: "refresh".

11. **Set `meta.refreshDue`** to 6 months from today, or the buyer's
    next known reporting milestone if earlier.

12. **Re-render HTML and save both files.**

13. **Report to user:** Summarise what changed at the lens level
    (which lenses had material updates), which actions closed, which
    new actions opened, and what the next refresh window looks like.
