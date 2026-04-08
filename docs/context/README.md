# Strategic context — auto-memory mirror

This directory is a **manual snapshot** of the auto-memory state used by the
Claude Code session, mirrored into the repo as a backup measure so the
strategic context survives if the codespace is destroyed.

## What lives here

The files in this directory capture **strategic context that is not derivable
from the code or git history**: product decisions, the reasoning behind those
decisions, things that have been considered and rejected, the user's
preferences for how to collaborate, and pointers to external resources.

The naming convention follows the auto-memory taxonomy:

| Prefix | Meaning |
|---|---|
| `user_` | Profile and role context for the user |
| `feedback_` | Rules of engagement — what to do, what to avoid, with the *why* |
| `project_` | State of in-flight work, open decisions, things in motion |
| `reference_` | Pointers to external systems, datasets, or tools |
| `MEMORY.md` | One-line index of every memory with a short hook |

## Source of truth

**The source of truth lives outside this repo**, at:

```
/home/codespace/.claude/projects/-workspaces-PWIN/memory/
```

That directory is the working set — Claude reads and writes to it during
sessions. This `docs/context/` directory is a one-way mirror taken at the
moments listed below.

## Snapshot policy

This is a **manual snapshot**, not an automatic sync. The files here may
be stale relative to the working memory. The way to refresh them is the
ritual at the bottom of this file.

### Snapshot history

| Date       | Trigger                                                                 |
|------------|-------------------------------------------------------------------------|
| 2026-04-08 | Initial snapshot — after the OCP bulk import session and the product strategy pivot |

When refreshing, append a new row above with the date and a one-line reason.

## How to refresh

From the repo root:

```bash
cp /home/codespace/.claude/projects/-workspaces-PWIN/memory/*.md docs/context/
git add docs/context/
git status     # check what's actually changed
git commit -m "Refresh strategic context snapshot — <reason>"
git push
```

Don't refresh blindly at the end of every session — most session work
doesn't change strategic context. Refresh when:

- A new project memory has been created (a new initiative or decision is in flight)
- An existing memory has been materially rewritten (e.g. a strategic pivot)
- A new feedback memory has been created (a new rule of engagement)
- A new reference memory has been created (a new external resource)
- You're about to destroy or rebuild the codespace and want to be sure
  the working memory is captured before it's gone

## What this directory is NOT

- **Not** human-facing product documentation. Product docs live in
  `pwin-<product>/docs/`.
- **Not** code documentation. Inline comments and module docstrings serve
  that purpose.
- **Not** auto-synced. If you change a memory file in the working memory
  directory, this mirror does not update on its own.
- **Not** the source of truth for an active session. Claude reads from
  the working memory directory; this mirror exists for disaster recovery
  and for human review of accumulated context.
