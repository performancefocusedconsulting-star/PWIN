# Launch Validation Tour

The conversation playbook and supporting artefacts for Paul's pre-launch validation tour for BidEquity. Spec at `../docs/superpowers/specs/2026-05-02-launch-validation-tour-design.md`.

## What's here

| File | Purpose |
|---|---|
| `playbook.html` | Primary HTML conversation playbook. Open this on the laptop during conversations. |
| `deck.html` | HTML slide deck (substantive overview). Visual anchor used live. |
| `deck.pptx` | PowerPoint deck (same content). Portable leave-behind / send-after. |
| `deck-content.md` | Single source of truth for the deck and the playbook overview content. |
| `cfo-stress-test.md` | Pre-tour memo: forensic self-examination of the CFO model and £3bn / £2bn thesis. Written by Paul before any conversation. |
| `templates/synthesis-prompt.md` | Fixed instruction set for converting a transcript to the structured Markdown capture template. |
| `templates/conversation-capture.md` | Per-conversation synthesised structure. One file per conversation. |
| `templates/synthesis-log.csv` | Spreadsheet fallback and cross-tour roll-up index. |
| `assets/pwin-five-layers.html` | Reserve asset: five-layer PWIN explainer page. |
| `assets/pre-gate-playbook.html` | Reserve asset: Pre-Gate Pursuit Playbook diagram (S1–S5). |
| `assets/data-confidence-catalogue.html` | Reserve asset: confidence-graded extract of what the contracts database can and can't tell us. |
| `conversations/` | Per-conversation synthesised Markdown files. Gitignored by default. |

## How the conversation flow uses this

1. **Pre-conversation:** send the framing email (template embedded in `playbook.html`). Audience reads the website pre-read independently.
2. **At the conversation:** open `playbook.html` on the laptop. Open `deck.html` in a second tab as the visual anchor when the substantive overview phase begins.
3. **During the conversation:** if a reserve asset is earned, open the relevant page from `assets/`.
4. **After the conversation:** transcribe the recording, run it through `templates/synthesis-prompt.md`, save the output to `conversations/YYYY-MM-DD-<initials>-<audience-code>.md`, update `templates/synthesis-log.csv`. Purge the raw audio and transcript once the synthesis is reviewed.

## Privacy

Raw audio, transcripts, and per-conversation synthesised files are gitignored. The synthesis log can be either local-only (`synthesis-log.local.csv`, gitignored) or committed in anonymised form (`templates/synthesis-log.csv`). Pick one as a project-level convention before the first conversation.

## Editing the deck

`deck-content.md` is the single source of truth for both `deck.html` and `deck.pptx`.

- **`deck.html`** is hand-built HTML that reads the same content. To change a slide's wording or order, edit `deck-content.md` and update `deck.html` to match.
- **`deck.pptx`** is generated from `deck-content.md` via Marp (a small command-line tool). Never hand-edit `deck.pptx` directly. To regenerate after a content change, install Marp once (`npm install -g @marp-team/marp-cli`) then run `marp deck-content.md --pptx --allow-local-files -o deck.pptx` from this folder.
