# Launch Validation Tour — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the conversation playbook artefact (HTML + PowerPoint deck + supporting templates and assets) that supports Paul's pre-launch validation tour for BidEquity, as specified in `docs/superpowers/specs/2026-05-02-launch-validation-tour-design.md`.

**Architecture:** Content artefacts under a new top-level `launch-validation/` folder. Single source-of-truth Markdown files for the deck and the playbook content; HTML pages render that content for live use; PowerPoint is a parallel rendering of the same source content. Templates and prompts in `templates/`. Reserve assets in `assets/`. Raw recordings, transcripts, and per-conversation synthesised files are gitignored.

**Tech Stack:** Plain HTML + CSS (Midnight Executive palette, matching the rest of the PWIN platform's HTML artefacts); Markdown for content sources, templates, and prompts; CSV for the spreadsheet fallback; PowerPoint built either by hand from the HTML deck or via Marp from the deck's Markdown source (executor's choice).

**Visual style note (applies to every HTML asset in this plan):**

- Fonts: `Cormorant Garamond` (display, numbers), `DM Mono` (labels, data, code), `DM Sans` (body)
- Palette (CSS variables — declare once at the top of every HTML file):
  - `--midnight: #0F1B2D` (deep navy backgrounds)
  - `--midnight-soft: #1B2A44` (raised surfaces)
  - `--gold: #C8A85B` (accent)
  - `--gold-soft: #E5C97A` (highlights)
  - `--bone: #F4EFE6` (foreground text)
  - `--mist: #8A93A6` (secondary text)
  - `--rule: rgba(255,255,255,0.08)` (rules and borders)
- Loaded via Google Fonts: `Cormorant+Garamond:wght@500;600`, `DM+Mono:wght@400;500`, `DM+Sans:wght@400;500;700`
- Print stylesheet on every page (suppress nav, print-friendly black-on-white)

**Authorship convention:** Some tasks are pure structure (Claude builds end-to-end). Some require Paul's authored content (Claude builds the scaffold and prompts; Paul fills the prose in his own voice). Each task names which kind it is in its header.

---

## Task 1 — Folder structure, README, gitignore

**Authorship:** Claude end-to-end.

**Files:**
- Create: `launch-validation/README.md`
- Create: `launch-validation/.gitignore`
- Create: `launch-validation/assets/.gitkeep`
- Create: `launch-validation/templates/.gitkeep`
- Create: `launch-validation/conversations/.gitkeep`

- [ ] **Step 1: Create the folder structure.**

```bash
mkdir -p launch-validation/assets launch-validation/templates launch-validation/conversations
touch launch-validation/assets/.gitkeep launch-validation/templates/.gitkeep launch-validation/conversations/.gitkeep
```

- [ ] **Step 2: Write `launch-validation/.gitignore`.**

```gitignore
# Raw recordings and transcripts — workings, not artefacts. Kept local, never committed.
*.m4a
*.mp3
*.wav
*.aac
*.ogg
*.opus
*.flac
*.webm
*.mp4
*-transcript.txt
*-transcript.md
*.transcript

# Per-conversation synthesised files contain third-party names and verbatim quotes.
# Default: gitignored. Override per-file with `git add -f` if a particular conversation has been anonymised.
conversations/20*.md
!conversations/.gitkeep
!conversations/_README.md

# Local-only synthesis log (the committed version, if any, is anonymised).
synthesis-log.local.md
synthesis-log.local.csv
```

- [ ] **Step 3: Write `launch-validation/README.md`.**

```markdown
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
```

- [ ] **Step 4: Verify structure and ignore rules.**

```bash
ls -la launch-validation/
cat launch-validation/.gitignore
cat launch-validation/README.md
```

Expected: folders exist; `.gitignore` contains the audio extensions and conversation glob; README is readable.

- [ ] **Step 5: Commit.**

```bash
git add launch-validation/.gitignore launch-validation/README.md launch-validation/assets/.gitkeep launch-validation/templates/.gitkeep launch-validation/conversations/.gitkeep
git commit -m "feat(launch-validation): initialise folder structure, README, gitignore"
```

---

## Task 2 — CFO stress-test memo template

**Authorship:** Claude builds the prompts. **Paul writes the answers** before the tour starts.

**Files:**
- Create: `launch-validation/cfo-stress-test.md`

- [ ] **Step 1: Write the file.**

```markdown
# CFO stress-test memo

**Purpose:** force a cold, forensic examination of the £3bn / £2bn moat thesis and the CFO model *before* any tour conversation. The output is not a defence — it's a list of *known soft spots*, each with either a fix or an explicit acknowledgement of "this is a soft spot we'll honestly admit." When the model reaches a finance professional, walk them through the soft spots first. That disarms the cross-examination.

**Status:** [ ] not started · [ ] in progress · [ ] complete and reviewed

**Reviewer (optional):** ____________________

---

## 1. The £3bn industry spend figure

**The claim.** The top 40 strategic suppliers to UK public sector spend roughly £3bn a year on bid pursuit.

**Underlying derivation.** _Write here: where does this number come from? What's the bottom-up build? Which assumptions and inputs?_

**What it does not include.** _Write here: out-of-scope segments, exclusions, edge cases._

**The hostile-reviewer questions.**
- What's the basis for "top 40"? Why 40 not 50 or 100?
- Is the per-firm bid spend rate based on disclosed figures or inferred?
- Are framework call-off bids counted? Direct awards? Mini-competitions?
- Is "strategic supplier" defined narrowly enough to defend?

**Soft spots.** _Write here: where would a hostile reviewer find purchase?_

**Mitigation.** _Write here: fix the model, or explicitly admit the soft spot._

---

## 2. The £2bn waste figure

**The claim.** Around £2bn of the £3bn goes on bids the suppliers were never going to win.

**Underlying derivation.** _Write here: which industry survey, which methodology, which assumptions? What's the unit economics — is it a win-rate-based claim, a confidence-band claim, a simple arithmetic claim?_

**What would change it.** _Write here: what set of assumptions would move it to £1bn? To £3bn? Where's the band?_

**The hostile-reviewer questions.**
- Is "never going to win" defined empirically (post-hoc on outcome data) or subjectively (pre-bid pursuit-quality assessment)?
- Does the figure reflect *opportunity cost* (better-spent elsewhere) or *waste in the strict sense* (zero-return spend)?
- How does this square with the fact that strategic suppliers' bid functions are profit centres at the portfolio level?

**Soft spots.** _Write here._

**Mitigation.** _Write here._

---

## 3. The per-pursuit ROI claim

**The claim.** Per-pursuit return at population-average win rates lands at roughly 0.9× — just under break-even — for low-margin services clients.

**Inputs.** Win rate: __%. Margin profile: __%. Bid spend rate: __%. Reference client: ______.

**The hostile-reviewer questions.**
- What's the source for the bid spend rate, by client segment? (Note: per the 2026-05-02 hot.md, the rates for IT consulting, engineering consulting, and management consulting are estimates pending real consulting client P&L data — name this explicitly.)
- What's the source for the win rate baseline?
- How does the margin assumption translate from operating margin (P&L line) to per-pursuit gross profit (model input)?
- Is the calculation per-bid or per-pursuit (some pursuits run multiple bids)?

**Soft spots.** _Write here._

**Mitigation.** _Write here._

---

## 4. The portfolio-level vs per-pursuit ROI distinction

**The claim.** Company-level pursuit ROI of about 3.2× (gross profit ÷ bid spend) and per-pursuit ROI of about 0.9× both hold simultaneously — winners pay for losers at the portfolio level.

**The hostile-reviewer questions.**
- Is this distinction visible in the model UI, or could a fresh reader interpret it as double-counting?
- Does the difference reconcile arithmetically in the calculations, or is it left implicit?
- Which figure should external comms lead with, and how is the other surfaced without confusing the reader?

**Soft spots.** _Write here._

**Mitigation.** _Write here._

---

## 5. The retainer model (now removed)

**Context.** Retainer ROI was removed from the CFO model on 2026-05-02 because the flat £720k figure produced ~30× for a £2bn outsourcer and ~2.9× for a £400m consulting firm — the metric was working against itself across profiles.

**Remaining question.** _Write here: what's the commercial model that replaces it? Is the answer "we don't know yet, that's why retainer ROI is silent in the CFO model"? If so, is that itself a soft spot in front of a CFO who'll ask "what does it cost?"_

**Soft spots.** _Write here._

**Mitigation.** _Write here._

---

## 6. The competitive landscape claim

**The claim.** No methodology in market combines algorithmic discipline, capture evidence, structural reality, and bias correction in one system.

**The hostile-reviewer questions.**
- How do you know? Have you stress-tested the claim against Cleat.ai, pWin.ai/TechnoMile, Shipley implementations, the proprietary tools at the strategic suppliers themselves?
- Is "in market" defined as commercially available products, or does it include in-house methodologies at strategic suppliers?

**Soft spots.** _Write here._

**Mitigation.** _Write here._

---

## Closing self-assessment

Once 1–6 are filled in, answer these:

1. **The single weakest claim in the model.** _Write here. Be honest._
2. **The claim I'm most confident defending in front of a finance professional.** _Write here._
3. **The two or three soft spots I'll lead with when handing this to a CFO.** _Write here._

When you can answer all three crisply, the model is ready for external scrutiny.
```

- [ ] **Step 2: Verify file is readable and non-trivial.**

```bash
wc -l launch-validation/cfo-stress-test.md
```

Expected: substantially more than 50 lines.

- [ ] **Step 3: Commit.**

```bash
git add launch-validation/cfo-stress-test.md
git commit -m "feat(launch-validation): CFO stress-test memo template with cross-examination prompts"
```

---

## Task 3 — Synthesis prompt

**Authorship:** Claude end-to-end. The prompt is the fixed instruction set for transcript → Markdown synthesis.

**Files:**
- Create: `launch-validation/templates/synthesis-prompt.md`

- [ ] **Step 1: Write the file.**

```markdown
# Synthesis prompt

Use this prompt verbatim when synthesising a recorded conversation transcript into the per-conversation Markdown capture file. The point of using a fixed prompt is reproducibility — every conversation gets synthesised the same way, so the synthesis log reads as comparable evidence rather than as differently-toned summaries.

---

## Prompt to paste into Claude (or equivalent)

**Role.** You are synthesising a recorded conversation between Paul Fenton (founder of BidEquity) and one trusted person in his pre-launch validation tour. The conversation has been transcribed verbatim. Your job is to produce a structured Markdown synthesis using the template below.

**Context Paul used in the conversation.**

Paul opened with this framing paragraph:

> *"I'm not here to pitch you anything. I've spent a year and a half building something — a methodology and a platform for how strategic suppliers in UK public sector should pursue their bids — and I'm a few weeks away from making it public. Before I do, I want to spend an hour with people I trust, including you, on three things I genuinely don't know the answer to. I'd value you pushing back hard rather than being kind."*

He then walked through five "substantive overview" chunks (you may not see all five — he modulates per audience):

1. **The problem.** £3bn UK strategic-supplier bid spend, £2bn of which goes on bids they were never going to win.
2. **Why nobody's solved it.** Existing approaches are too subjective (Happy Ears), too academic, or too simplistic (single weighted scorecards). Cleat.ai and pWin.ai are scoring tools, not challenge functions.
3. **What he's built.** Methodology = Pre-Gate Pursuit Playbook (S1–S5) + Bid Execution. Platform = six products: Qualify, Win Strategy, Bid Execution, Verdict, Portfolio, Competitive Intel.
4. **The proprietary asset.** Five-year, 175,000-contract UK procurement database, master-listed buyers and suppliers, framework intelligence, stakeholder map. UK-native.
5. **The honest state.** What works today, what's built but not battle-tested, what's unknown.

He then asked some subset of these four questions (rarely all four; usually two or three):

1. **Credibility configuration.** What founding-team / leadership configuration would make this platform survive a strategic supplier's "who else is behind this?" question?
2. **Trigger to change.** What would actually trigger a top-40 strategic supplier's leadership team to change how they pursue bids?
3. **Who do you know — for either side of this?** People who could help build it, or people who could buy it.
4. **What am I missing? If you were me, would you redirect this entirely?**

He closed by asking: *"What's the single thing you'd want me to think hardest about between now and when this goes public?"*

**Audience codes.**
- **A** — industry insider (ex-clients, ex-colleagues, anyone who's lived inside a strategic supplier's bid function).
- **B** — senior business non-industry (commercial generalists, board members, advisors).
- **C** — potential commercial buyer (Bid Director, Capture Director, COO at a strategic supplier).
- **D** — potential co-founder / director / partner / route-to-market collaborator.

**Your job.**

Read the transcript. Produce the structured Markdown below. Follow these rules:

1. **Prefer verbatim quotes over paraphrase.** When the audience said something specific, quote it. Paraphrase only when you have to.
2. **Don't infer beyond the transcript.** If they didn't react to a chunk, mark it "not reached" — don't guess their reaction.
3. **Be honest about ambiguity.** If a quote could be read two ways, show both.
4. **Pull out names ruthlessly.** Any name they mentioned, in either direction (introduction, suggested team member, suggested buyer), goes into the names section. Even tentative ones.
5. **Keep the texture.** The "quotes worth keeping" section captures what the synthesis log can't carry forward — the moments that have flavour. 3–5 quotes maximum.

---

## Markdown template to fill in

(Reproduces `templates/conversation-capture.md`. Output your filled-in version with the same headings, in the same order, in valid Markdown.)
```

- [ ] **Step 2: Verify the prompt is self-contained and unambiguous.**

```bash
wc -l launch-validation/templates/synthesis-prompt.md
```

Expected: roughly 60–80 lines. Read through once. Every reference to a chunk number, question number, or audience code must be defined in the prompt itself.

- [ ] **Step 3: Commit.**

```bash
git add launch-validation/templates/synthesis-prompt.md
git commit -m "feat(launch-validation): synthesis prompt for transcript to markdown capture"
```

---

## Task 4 — Per-conversation Markdown capture template

**Authorship:** Claude end-to-end.

**Files:**
- Create: `launch-validation/templates/conversation-capture.md`

- [ ] **Step 1: Write the file.**

```markdown
---
type: validation-conversation
audience: <A|B|C|D>
recording: <recorded|written-notes>
duration_minutes: <int>
date: YYYY-MM-DD
participant_initials: <XX>
participant_role: <one short line, generic enough to anonymise if needed>
---

# Conversation: <participant initials> · <YYYY-MM-DD>

## Header

- **Audience:** <A | B | C | D>
- **Recording status:** <recorded and transcribed | written notes only>
- **Duration:** <minutes>
- **Setting:** <coffee | video call | other>
- **Pre-read sent:** <yes | no | partial>

## One-line takeaway from their perspective

_What they would say BidEquity is, in their own words. Verbatim where possible. If you can't write this, the listening was thin._

>

## Reaction by chunk

| # | Chunk | RAG | Evidence (verbatim where possible) |
|---|---|---|---|
| 1 | The problem (£3bn / £2bn) | <green/amber/red/not reached> | |
| 2 | Why nobody's solved it | | |
| 3 | What he's built (methodology + platform) | | |
| 4 | The proprietary asset (data layer) | | |
| 5 | The honest state | | |

**RAG meaning.** Green = landed clearly, energised them. Amber = landed but with friction, hedging, or visible scepticism. Red = did not land or actively pushed back. "Not reached" = chunk was compressed or skipped in this conversation.

## Per-question reactions

### Q1 — Credibility configuration

_What founding-team / leadership configuration would make this platform survive scrutiny?_

>

### Q2 — Trigger to change

_What would actually trigger a top-40 strategic supplier's leadership team to change behaviour?_

>

### Q3 — Who do you know

_People for either side of this — build, partner, buy, open a buying door._

>

### Q4 — What am I missing / would you redirect

_Pivot signals. Adjacent markets, products, business models._

>

## Pivot signals

_Anything from the conversation that suggests the proposition or the model needs rethinking — not a tweak, a redirect. Quote the trigger, then describe._

-

## Names mentioned

| Name | Direction (intro / team / buyer) | Context | Action |
|---|---|---|---|
| | | | |

## Exit ask agreed

- **Asked for:** <introduction | involvement | three-month loop-back | none>
- **Committed next step:** <what Paul said he'd do, by when>

## Single-thing takeaway

_Their answer to "what's the single thing you'd want me to think hardest about between now and when this goes public?" — verbatim._

>

## Quotes worth keeping

_3–5 quotes that capture the texture of the conversation. Useful later for refining the substantive overview language._

1.
2.
3.
```

- [ ] **Step 2: Verify the template renders as valid Markdown and contains every section the synthesis prompt expects.**

```bash
cat launch-validation/templates/conversation-capture.md
```

Expected: every heading from the synthesis prompt's "Markdown template to fill in" instruction is present in the file. Cross-check against `synthesis-prompt.md` written in Task 3.

- [ ] **Step 3: Commit.**

```bash
git add launch-validation/templates/conversation-capture.md
git commit -m "feat(launch-validation): per-conversation markdown capture template"
```

---

## Task 5 — Synthesis log (CSV + Markdown index)

**Authorship:** Claude end-to-end.

**Files:**
- Create: `launch-validation/templates/synthesis-log.csv`
- Create: `launch-validation/synthesis-log.md`

- [ ] **Step 1: Write the CSV header.**

```bash
cat > launch-validation/templates/synthesis-log.csv <<'CSV'
date,participant_initials,audience,recording,duration_min,one_line_takeaway,c1_rag,c2_rag,c3_rag,c4_rag,c5_rag,q1_summary,q2_summary,q3_summary,q4_summary,pivot_signals,names_mentioned,exit_ask,single_thing_takeaway,file_link
CSV
```

- [ ] **Step 2: Write the Markdown roll-up index.**

```markdown
---
type: validation-tour-log
status: in-progress
---

# Validation tour synthesis log

The roll-up across all tour conversations. One row per conversation. The signal threshold: three different people from three different audiences flagging the same gap is real signal; one person flagging it is noise. Reviewed every 3–4 conversations, not after every one.

## Wave status

| Wave | Audience | Target count | Conversations to date | Status |
|---|---|---|---|---|
| 1 — Friendly stress test | B | 3–4 | 0 | not started |
| 2 — Domain stress test | A | 4–6 | 0 | not started |
| 3 — Buyer-side reality check | C | 3–5 | 0 | not started |
| Parallel — Recruitment track | D | 2–4 | 0 | not started |

## Conversation log

| Date | Participant | Audience | One-line takeaway | Pivot? | Link |
|---|---|---|---|---|---|
| | | | | | |

## Cross-conversation signals (reviewed every 3–4 conversations)

### Recurring pivot signals
- _Add as they emerge._

### Recurring names mentioned (3+ separate conversations)
- _Add as they emerge._

### Recurring credibility-configuration patterns
- _Add as they emerge._

### Recurring trigger-to-change patterns
- _Add as they emerge._

## Decision gate (week 7)

When 10–15 conversations are in, write the one-page memo answering:

1. **Does the proposition hold up, or am I pivoting?**
2. **What's the credibility configuration I'm committing to for launch?**
3. **Is the public LinkedIn launch on or off?**

Linked memo: `launch-decision-memo.md` (created at week 7).
```

- [ ] **Step 3: Verify both files render and the CSV header matches the Markdown columns.**

```bash
head -1 launch-validation/templates/synthesis-log.csv
cat launch-validation/synthesis-log.md
```

Expected: CSV has 20 columns; Markdown index lists wave status, conversation log table, signals section, decision gate.

- [ ] **Step 4: Commit.**

```bash
git add launch-validation/templates/synthesis-log.csv launch-validation/synthesis-log.md
git commit -m "feat(launch-validation): synthesis log (CSV header + markdown roll-up index)"
```

---

## Task 6 — Deck content source

**Authorship:** Claude end-to-end. Content lifted directly from spec Section 3, formatted as a Marp-compatible Markdown file. The HTML deck (Task 7) reads this content and re-renders it in the platform's hand-styled HTML; the PowerPoint deck (Task 8) is generated directly from this same file via Marp. One source, two renderings.

**Files:**
- Create: `launch-validation/deck-content.md`

- [ ] **Step 1: Write the deck content file.**

The frontmatter includes Marp directives (`marp: true`, palette, inline style block, Google Fonts import) so `marp deck-content.md --pptx` produces a Midnight-Executive-styled PowerPoint without further configuration. The non-Marp metadata (`title`, `date`, `audience`, `purpose`) sits alongside the Marp directives in the same frontmatter block.

```markdown
---
marp: true
theme: default
paginate: true
size: 16:9
backgroundColor: '#0F1B2D'
color: '#F4EFE6'
title: BidEquity — substantive overview (validation tour)
date: 2026-05-02
audience: validation tour (A/B/C)
purpose: visual anchor for the substantive overview phase of each conversation
style: |
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap');
  section { font-family: 'DM Sans', system-ui, sans-serif; padding: 60px 80px; background: #0F1B2D; color: #F4EFE6; }
  h1 { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 56pt; margin: 0 0 0.3em; line-height: 1.1; letter-spacing: 0.5px; }
  h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 28pt; color: #C8A85B; margin: 0 0 1em; }
  p, li { font-size: 22pt; line-height: 1.5; }
  ul, ol { padding-left: 1.2em; }
  li { margin-bottom: 0.4em; }
  strong { color: #E5C97A; font-weight: 700; }
  em { color: #8A93A6; font-style: italic; font-size: 18pt; }
  hr { border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1em 0; }
  section::after { font-family: 'DM Mono', monospace; font-size: 11pt; color: #8A93A6; letter-spacing: 1.5px; bottom: 30px; right: 60px; }
---

# Slide 1 — Title

**BidEquity**

The pre-launch conversation, May 2026.

_Speaker note: this slide is up while you deliver the framing paragraph. Do not read it. Look at them._

---

# Slide 2 — Chunk 1: The problem

The top 40 strategic suppliers to UK public sector spend roughly **£3bn a year** on bid pursuit.

By industry estimate, around **£2bn of that** goes on bids they were never going to win.

The cost isn't just the bid budgets. It's the opportunity cost of capture teams chasing the wrong things. The reputational drag of repeated losses. The executive credibility lost when over-confident win-probability scores prove unfounded.

_Speaker note: lead here to surface — early — the possibility that the audience does not see this as a problem. If they push back, the trigger question (Q2) just opened naturally. Compress the rest of the overview._

---

# Slide 3 — Chunk 2: Why nobody's solved it

Existing approaches are one of three things:

- **Too subjective** — Happy Ears: sales optimism inflating scores.
- **Too academic** — impractical at the speed of decision-making.
- **Too simplistic** — single weighted scorecards dressed up as algorithms.

None combine **algorithmic discipline, capture evidence, structural reality, and bias correction** in one system.

The US-focused tools — Cleat.ai, pWin.ai — are scoring tools, not challenge functions. They tell you the score; they don't tell you to walk away.

---

# Slide 4 — Chunk 3a: What I've built — the methodology

The **Pre-Gate Pursuit Playbook (S1–S5)**:

1. Opportunity Sense-Making
2. Buyer & Field Shaping
3. Win Architecture Design
4. Commercial Risk & Suitability Review
5. Commitment Readiness

Then **Bid Execution**.

---

# Slide 5 — Chunk 3b: What I've built — the platform

Six products:

- **Qualify** — assurance and challenge layer
- **Win Strategy** — capture playbook engine
- **Bid Execution** — production discipline
- **Verdict** — post-loss forensic review
- **Portfolio** — leadership dashboard
- **Competitive Intel** — proprietary UK contracts data layer

_Speaker note: honest register. No "AI-powered SaaS." No "next-generation."_

---

# Slide 6 — Chunk 4: The proprietary asset

A **five-year, 175,000-contract UK public sector procurement database**.

- Master-listed buyers
- Master-listed suppliers
- Framework holders
- Executive organograms
- Confidence catalogue describing exactly what the data can and cannot tell us

Built natively, not licensed. UK-specific, not adapted from a US system. Updated nightly.

This is what makes the multi-layered probability score possible. Without it, you're just running a scorecard.

_Speaker note: lands hardest with audience A. Lands lightest with audience B. Compress for B and C; expand for A._

---

# Slide 7 — Chunk 5: The honest state

**Working today.** Contracts intelligence database. Qualify (live, lead-gen ready). The methodology. The founder credibility. The website.

**Built but not yet battle-tested on a live engagement.** Win Strategy. Bid Execution. The methodology hasn't run on a paid client end-to-end yet.

**Unknown.** Whether strategic suppliers will move on this absent a forcing function. Whether the credibility configuration around me is sufficient. Whether the commercial model is the right shape — transactional / outcome-aligned / SaaS / licensing / something else.

_Speaker note: this chunk is what creates the conditions for the four questions. By the time you've said this, the audience already understands they're being invited into a real working problem._

---

# Slide 8 — Closing prompt

Three questions I'd like to think with you on:

1. What configuration of people would make this platform credible to a buyer?
2. What would actually trigger a strategic supplier to change behaviour?
3. Who do you know — for either side of this?

And:

4. What am I missing?

_Speaker note: do not read all four. Pick the two or three that fit who's in front of you. Sit with silence after each one._
```

- [ ] **Step 2: Verify the file structure (8 slides separated by `---`).**

```bash
grep -c "^# Slide " launch-validation/deck-content.md
```

Expected: `8`.

- [ ] **Step 3: Commit.**

```bash
git add launch-validation/deck-content.md
git commit -m "feat(launch-validation): deck content source (8 slides) for HTML and PowerPoint renderings"
```

---

## Task 7 — HTML slide deck

**Authorship:** Claude end-to-end. Renders `deck-content.md` as an HTML deck in Midnight Executive style.

**Files:**
- Create: `launch-validation/deck.html`

- [ ] **Step 1: Write `deck.html`.**

The deck is a single HTML file with eight `<section class="slide">` elements, advanced via arrow keys (or click). Each slide fills the viewport. Speaker notes are hidden by default and revealed with `?notes=1` query string.

```html
<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>BidEquity — substantive overview (validation tour)</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --midnight: #0F1B2D;
    --midnight-soft: #1B2A44;
    --gold: #C8A85B;
    --gold-soft: #E5C97A;
    --bone: #F4EFE6;
    --mist: #8A93A6;
    --rule: rgba(255,255,255,0.08);
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: var(--midnight); color: var(--bone); font-family: 'DM Sans', system-ui, sans-serif; overflow: hidden; }
  .deck { position: relative; width: 100vw; height: 100vh; }
  .slide { position: absolute; inset: 0; padding: 6vh 8vw; display: flex; flex-direction: column; justify-content: center; opacity: 0; pointer-events: none; transition: opacity 200ms ease; }
  .slide.active { opacity: 1; pointer-events: auto; }
  .slide h1 { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: clamp(2.5rem, 5vw, 4rem); margin: 0 0 0.5rem; letter-spacing: 0.5px; }
  .slide h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: clamp(1.6rem, 2.5vw, 2.2rem); color: var(--gold); margin: 0 0 1.5rem; }
  .slide p, .slide li { font-size: clamp(1rem, 1.5vw, 1.4rem); line-height: 1.55; max-width: 60ch; }
  .slide ol, .slide ul { padding-left: 1.5em; }
  .slide li { margin-bottom: 0.6rem; }
  .slide strong { color: var(--gold-soft); font-weight: 700; }
  .label { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.85rem; color: var(--mist); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.5rem; }
  .footer { position: absolute; bottom: 3vh; left: 8vw; right: 8vw; display: flex; justify-content: space-between; font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.75rem; color: var(--mist); letter-spacing: 1px; }
  .notes { display: none; margin-top: 2rem; padding: 1rem; border-left: 2px solid var(--gold); font-style: italic; color: var(--mist); font-size: 0.95rem; max-width: 60ch; }
  body.show-notes .notes { display: block; }
  .nav { position: absolute; top: 3vh; right: 8vw; font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.75rem; color: var(--mist); letter-spacing: 1px; }
  @media print {
    html, body { overflow: visible; height: auto; }
    .slide { opacity: 1; pointer-events: auto; position: relative; page-break-after: always; min-height: 100vh; }
    .nav, .footer { display: none; }
    body.show-notes .notes { display: block; }
  }
</style>
</head>
<body>
<div class="deck">

  <section class="slide active" data-slide="1">
    <div class="label">BidEquity / 01</div>
    <h1>BidEquity</h1>
    <h2>The pre-launch conversation</h2>
    <p>May 2026</p>
    <div class="notes">This slide is up while you deliver the framing paragraph. Do not read it. Look at them.</div>
  </section>

  <section class="slide" data-slide="2">
    <div class="label">The problem / 02</div>
    <h1>£3bn spent. £2bn wasted.</h1>
    <p>The top 40 strategic suppliers to UK public sector spend roughly <strong>£3bn a year</strong> on bid pursuit.</p>
    <p>By industry estimate, around <strong>£2bn of that</strong> goes on bids they were never going to win.</p>
    <p>The cost isn't just the bid budgets. It's the opportunity cost of capture teams chasing the wrong things. The reputational drag of repeated losses. The executive credibility lost when over-confident win-probability scores prove unfounded.</p>
    <div class="notes">Lead here to surface — early — the possibility that the audience does not see this as a problem. If they push back, the trigger question (Q2) just opened naturally. Compress the rest.</div>
  </section>

  <section class="slide" data-slide="3">
    <div class="label">The diagnosis / 03</div>
    <h1>Why nobody's solved it</h1>
    <p>Existing approaches are one of three things:</p>
    <ul>
      <li><strong>Too subjective</strong> — Happy Ears: sales optimism inflating scores.</li>
      <li><strong>Too academic</strong> — impractical at the speed of decision-making.</li>
      <li><strong>Too simplistic</strong> — single weighted scorecards dressed up as algorithms.</li>
    </ul>
    <p>None combine <strong>algorithmic discipline, capture evidence, structural reality, and bias correction</strong> in one system.</p>
    <p>The US tools — Cleat.ai, pWin.ai — are scoring tools, not challenge functions. They tell you the score; they don't tell you to walk away.</p>
  </section>

  <section class="slide" data-slide="4">
    <div class="label">The methodology / 04</div>
    <h1>The Pre-Gate Pursuit Playbook</h1>
    <ol>
      <li>Opportunity Sense-Making</li>
      <li>Buyer &amp; Field Shaping</li>
      <li>Win Architecture Design</li>
      <li>Commercial Risk &amp; Suitability Review</li>
      <li>Commitment Readiness</li>
    </ol>
    <p>Then <strong>Bid Execution</strong>.</p>
  </section>

  <section class="slide" data-slide="5">
    <div class="label">The platform / 05</div>
    <h1>Six products, one system</h1>
    <ul>
      <li><strong>Qualify</strong> — assurance and challenge layer</li>
      <li><strong>Win Strategy</strong> — capture playbook engine</li>
      <li><strong>Bid Execution</strong> — production discipline</li>
      <li><strong>Verdict</strong> — post-loss forensic review</li>
      <li><strong>Portfolio</strong> — leadership dashboard</li>
      <li><strong>Competitive Intel</strong> — proprietary UK contracts data layer</li>
    </ul>
    <div class="notes">Honest register. No "AI-powered SaaS." No "next-generation."</div>
  </section>

  <section class="slide" data-slide="6">
    <div class="label">The proprietary asset / 06</div>
    <h1>The data layer</h1>
    <p>A <strong>five-year, 175,000-contract</strong> UK public sector procurement database.</p>
    <ul>
      <li>Master-listed buyers</li>
      <li>Master-listed suppliers</li>
      <li>Framework holders</li>
      <li>Executive organograms</li>
      <li>Confidence catalogue describing exactly what the data can and cannot tell us</li>
    </ul>
    <p>Built natively, not licensed. UK-specific, not adapted from a US system. Updated nightly.</p>
    <p>This is what makes the multi-layered probability score possible. Without it, you're just running a scorecard.</p>
    <div class="notes">Lands hardest with audience A. Lands lightest with audience B. Compress for B and C; expand for A.</div>
  </section>

  <section class="slide" data-slide="7">
    <div class="label">The honest state / 07</div>
    <h1>What's true today</h1>
    <p><strong>Working today.</strong> Contracts intelligence database. Qualify (live, lead-gen ready). The methodology. The founder credibility. The website.</p>
    <p><strong>Built but not battle-tested.</strong> Win Strategy. Bid Execution. The methodology hasn't run on a paid client end-to-end yet.</p>
    <p><strong>Unknown.</strong> Whether strategic suppliers will move on this absent a forcing function. Whether the credibility configuration is sufficient. Whether the commercial model is the right shape.</p>
    <div class="notes">This chunk is what creates the conditions for the four questions. By the time you've said this, the audience already understands they're being invited into a real working problem.</div>
  </section>

  <section class="slide" data-slide="8">
    <div class="label">The conversation / 08</div>
    <h1>Three questions</h1>
    <ol>
      <li>What configuration of people would make this platform credible to a buyer?</li>
      <li>What would actually trigger a strategic supplier to change behaviour?</li>
      <li>Who do you know — for either side of this?</li>
    </ol>
    <p>And:</p>
    <ol start="4"><li>What am I missing?</li></ol>
    <div class="notes">Do not read all four. Pick the two or three that fit who's in front of you. Sit with silence after each one.</div>
  </section>

</div>

<div class="nav" id="nav">1 / 8</div>
<div class="footer"><span>BidEquity · Validation Tour</span><span>← → to navigate · ?notes=1 to show speaker notes</span></div>

<script>
(function() {
  const slides = document.querySelectorAll('.slide');
  const nav = document.getElementById('nav');
  let i = 0;
  function show(n) {
    if (n < 0 || n >= slides.length) return;
    slides[i].classList.remove('active');
    i = n;
    slides[i].classList.add('active');
    nav.textContent = (i + 1) + ' / ' + slides.length;
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') show(i + 1);
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') show(i - 1);
    if (e.key === 'Home') show(0);
    if (e.key === 'End') show(slides.length - 1);
  });
  document.addEventListener('click', () => show(i + 1));
  if (new URLSearchParams(window.location.search).get('notes') === '1') {
    document.body.classList.add('show-notes');
  }
})();
</script>
</body>
</html>
```

- [ ] **Step 2: Verify the deck opens, advances, and shows notes.**

Open `launch-validation/deck.html` in a browser. Confirm:
- Slide 1 displays at full viewport, midnight palette, gold accents.
- Arrow keys (and clicks) advance through 8 slides.
- Counter in top-right shows `1 / 8` through `8 / 8`.
- Append `?notes=1` to URL — italic speaker notes appear under the relevant slides.
- Print preview shows all 8 slides as separate pages.

- [ ] **Step 3: Commit.**

```bash
git add launch-validation/deck.html
git commit -m "feat(launch-validation): HTML slide deck (substantive overview, 8 slides, midnight palette)"
```

---

## Task 8 — PowerPoint deck (via Marp)

**Authorship:** Claude end-to-end at execution time. The PowerPoint is generated directly from `launch-validation/deck-content.md` (the Marp-shaped source built in Task 6) using the Marp CLI. No hand-building. The Marp directives (palette, fonts, inline style) are already in the source's frontmatter; this task installs the tool, runs it, and verifies the output.

**Files:**
- Create: `launch-validation/deck.pptx` (generated, not hand-edited)

**About Marp.** Marp is a small free command-line tool that converts a Markdown file into a deck. It is not a visual editor; you do not click and drag in it. You point it at `deck-content.md`, type one command, and it produces the PowerPoint. The styling is taken from the frontmatter we wrote in Task 6.

- [ ] **Step 1: Install Marp CLI.**

The platform already uses Node.js, so `npm` is available. Install Marp globally:

```bash
npm install -g @marp-team/marp-cli
```

Verify:

```bash
marp --version
```

Expected: a version number (e.g. `@marp-team/marp-cli v3.x.x`).

- [ ] **Step 2: Generate the PowerPoint.**

From the repo root:

```bash
cd launch-validation
marp deck-content.md --pptx --allow-local-files
```

This produces `deck-content.pptx` in the same folder. Rename it:

```bash
mv deck-content.pptx deck.pptx
```

(Or, in one line: `marp deck-content.md --pptx --allow-local-files -o deck.pptx`.)

- [ ] **Step 3: Open the PowerPoint and verify it matches the HTML deck.**

Open `launch-validation/deck.pptx` in PowerPoint, Keynote, or LibreOffice Impress. Confirm:
- 8 slides in the same order as `deck.html`.
- Title slide reads "BidEquity / The pre-launch conversation / May 2026".
- Slides 2–7 carry the five overview chunks, each with the right heading and body content.
- Slide 8 closes with the three (and a half) questions.
- Background reads as the dark navy palette; titles in the Cormorant Garamond serif; body text in DM Sans.
- Speaker notes from the deck source are present in the Notes pane of the relevant slides.

If anything is off, adjust the Marp directives in `deck-content.md` (Task 6 frontmatter), regenerate, and re-verify. The source is authoritative; never hand-edit `deck.pptx` directly — that would create the drift problem this approach exists to avoid.

- [ ] **Step 4: Commit.**

```bash
git add launch-validation/deck.pptx
git commit -m "feat(launch-validation): PowerPoint deck generated via Marp from deck-content.md"
```

**Regeneration note for the future.** If the deck content changes, edit `deck-content.md`, then re-run the Marp command in Step 2 to regenerate `deck.pptx`. Both `deck.html` (Task 7) and `deck.pptx` (this task) source from the same file, so they cannot drift unless one is hand-edited.

---

## Task 9 — Five-layer PWIN explainer page

**Authorship:** Claude end-to-end. One-page reserve asset. Pulled live when an audience asks "how is this different from a scorecard?".

**Files:**
- Create: `launch-validation/assets/pwin-five-layers.html`

- [ ] **Step 1: Write the file.**

```html
<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>PWIN — the five-layer probability engine</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --midnight: #0F1B2D;
    --midnight-soft: #1B2A44;
    --gold: #C8A85B;
    --gold-soft: #E5C97A;
    --bone: #F4EFE6;
    --mist: #8A93A6;
    --rule: rgba(255,255,255,0.08);
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--midnight); color: var(--bone); font-family: 'DM Sans', system-ui, sans-serif; }
  main { max-width: 980px; margin: 0 auto; padding: 6vh 6vw; }
  .label { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.85rem; color: var(--mist); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem; }
  h1 { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 3rem; margin: 0 0 0.5rem; }
  .subtitle { font-family: 'Cormorant Garamond', serif; font-style: italic; color: var(--gold); font-size: 1.4rem; margin: 0 0 3rem; }
  .layers { display: flex; flex-direction: column; gap: 0; }
  .layer { display: grid; grid-template-columns: 80px 1fr; gap: 2rem; padding: 1.5rem 0; border-top: 1px solid var(--rule); }
  .layer:last-child { border-bottom: 1px solid var(--rule); }
  .layer .num { font-family: 'Cormorant Garamond', serif; font-size: 3rem; color: var(--gold); line-height: 1; }
  .layer h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 1.6rem; margin: 0 0 0.5rem; }
  .layer p { margin: 0; line-height: 1.6; max-width: 60ch; }
  .layer .source { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.8rem; color: var(--mist); text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem; }
  .integrated { margin-top: 4rem; padding: 2rem; background: var(--midnight-soft); border-left: 3px solid var(--gold); }
  .integrated h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 1.6rem; margin: 0 0 1rem; color: var(--gold-soft); }
  .integrated p { margin: 0 0 0.8rem; line-height: 1.6; }
  @media print {
    html, body { background: white; color: black; }
    .integrated { background: #f4efe6; color: black; }
    .integrated h2 { color: #0F1B2D; }
    .layer .num, .subtitle { color: #b8973f; }
  }
</style>
</head>
<body>
<main>
  <div class="label">BidEquity / Reserve asset</div>
  <h1>The five-layer probability engine</h1>
  <p class="subtitle">PWIN is not a score. It is a system that produces one.</p>

  <section class="layers">
    <div class="layer">
      <div class="num">1</div>
      <div>
        <h2>Historical Pattern</h2>
        <p>What does the contracts data say about how often suppliers like you, in opportunities like this, with buyers like this, with competition like this, actually win? An empirical anchor drawn from 175,000 UK public sector contracts.</p>
        <p class="source">Source — Competitive Intel database</p>
      </div>
    </div>

    <div class="layer">
      <div class="num">2</div>
      <div>
        <h2>Qualify Assessment</h2>
        <p>The structured pursuit-team assessment across six categories — capture position, prime intent, solution strength, opportunity intelligence, value position, programme position. 24 weighted questions, opportunity-type calibration, modifier overlays.</p>
        <p class="source">Source — Qualify product</p>
      </div>
    </div>

    <div class="layer">
      <div class="num">3</div>
      <div>
        <h2>Capture Evidence</h2>
        <p>The artefacts produced through the capture window — buyer decision thesis, stakeholder map, competitor field map, win architecture, commercial stance — linked to the categorical claims they support. Evidence under each score, not narrative around it.</p>
        <p class="source">Source — Win Strategy product</p>
      </div>
    </div>

    <div class="layer">
      <div class="num">4</div>
      <div>
        <h2>Cognitive Discount Factor</h2>
        <p>A mathematically applied bias correction. Where the team's score is high but the supporting evidence is thin or contested, the score is discounted. Subjectivity is allowed in; over-confidence is not.</p>
        <p class="source">Source — Platform integration layer</p>
      </div>
    </div>

    <div class="layer">
      <div class="num">5</div>
      <div>
        <h2>Structural Ceiling</h2>
        <p>The hard cap imposed by the structural reality of the market — incumbency strength, framework dynamics, SMA positioning, regulatory constraints. A pursuit cannot score above its structural ceiling no matter how well the team executes.</p>
        <p class="source">Source — Platform integration layer + Competitive Intel</p>
      </div>
    </div>
  </section>

  <section class="integrated">
    <h2>What the system produces</h2>
    <p>One integrated PWIN score. Confidence-graded. Each layer visible underneath. Transparent by default.</p>
    <p>A scorecard tells you where the team thinks they are. The five-layer engine tells you whether the team is right — and if not, where the gap is and what closing it would cost.</p>
  </section>
</main>
</body>
</html>
```

- [ ] **Step 2: Verify the page renders cleanly.**

Open in a browser. Confirm:
- Five layers numbered 1–5, each with title, body, source line.
- "What the system produces" callout at the bottom.
- Print preview produces a clean, readable page.

- [ ] **Step 3: Commit.**

```bash
git add launch-validation/assets/pwin-five-layers.html
git commit -m "feat(launch-validation): five-layer PWIN explainer reserve asset"
```

---

## Task 10 — Pre-Gate Pursuit Playbook diagram page

**Authorship:** Claude end-to-end. One-page reserve asset showing S1–S5 stages with their key outputs and the four parallel workstreams.

**Files:**
- Create: `launch-validation/assets/pre-gate-playbook.html`

- [ ] **Step 1: Write the file.**

```html
<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>Pre-Gate Pursuit Playbook (S1–S5)</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --midnight: #0F1B2D;
    --midnight-soft: #1B2A44;
    --gold: #C8A85B;
    --gold-soft: #E5C97A;
    --bone: #F4EFE6;
    --mist: #8A93A6;
    --rule: rgba(255,255,255,0.08);
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--midnight); color: var(--bone); font-family: 'DM Sans', system-ui, sans-serif; }
  main { max-width: 1200px; margin: 0 auto; padding: 6vh 6vw; }
  .label { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.85rem; color: var(--mist); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem; }
  h1 { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 3rem; margin: 0 0 0.5rem; }
  .subtitle { font-family: 'Cormorant Garamond', serif; font-style: italic; color: var(--gold); font-size: 1.4rem; margin: 0 0 3rem; }
  .stages { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 3rem; }
  .stage { padding: 1.5rem; background: var(--midnight-soft); border-top: 3px solid var(--gold); }
  .stage .code { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.85rem; color: var(--gold); letter-spacing: 1.5px; margin-bottom: 0.5rem; }
  .stage h3 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 1.2rem; margin: 0 0 1rem; line-height: 1.2; }
  .stage ul { padding-left: 1em; margin: 0; font-size: 0.9rem; line-height: 1.5; color: var(--bone); }
  .stage li { margin-bottom: 0.4rem; }
  .stage li::marker { color: var(--gold); }
  .arrow { text-align: center; font-family: 'DM Mono', ui-monospace, monospace; color: var(--mist); margin: 1rem 0; letter-spacing: 2px; }
  .workstreams { padding: 2rem; background: var(--midnight-soft); border-left: 3px solid var(--gold); }
  .workstreams h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 1.6rem; margin: 0 0 1rem; color: var(--gold-soft); }
  .workstreams .label-tag { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.75rem; color: var(--mist); display: block; margin-bottom: 0.8rem; letter-spacing: 1px; }
  .workstreams ol { padding-left: 1.5em; line-height: 1.6; }
  .workstreams li strong { color: var(--gold-soft); }
  @media (max-width: 900px) { .stages { grid-template-columns: 1fr 1fr; } }
  @media print {
    html, body { background: white; color: black; }
    .stage, .workstreams { background: #f4efe6; color: black; }
    .stage .code, .workstreams h2, .stage li::marker, .subtitle { color: #b8973f; }
  }
</style>
</head>
<body>
<main>
  <div class="label">BidEquity / Reserve asset</div>
  <h1>The Pre-Gate Pursuit Playbook</h1>
  <p class="subtitle">Five stages across the 4–5 month capture window. Four workstreams running in parallel.</p>

  <section class="stages">
    <div class="stage">
      <div class="code">S1</div>
      <h3>Opportunity Sense-Making</h3>
      <ul>
        <li>Opportunity Brief</li>
        <li>Initial Buyer Need Hypothesis</li>
        <li>Initial Fit Assessment</li>
      </ul>
    </div>
    <div class="stage">
      <div class="code">S2</div>
      <h3>Buyer &amp; Field Shaping</h3>
      <ul>
        <li>Buyer Decision Thesis</li>
        <li>Stakeholder Map</li>
        <li>Competitor Field Map</li>
        <li>Incumbent Defensibility Assessment</li>
      </ul>
    </div>
    <div class="stage">
      <div class="code">S3</div>
      <h3>Win Architecture Design</h3>
      <ul>
        <li>Path to Win Statement</li>
        <li>Win Themes</li>
        <li>Proof Map</li>
        <li>Solution Spine</li>
      </ul>
    </div>
    <div class="stage">
      <div class="code">S4</div>
      <h3>Commercial Risk &amp; Suitability Review</h3>
      <ul>
        <li>Commercial Stance</li>
        <li>Suitability Review</li>
        <li>Risk Redline Summary</li>
        <li>Gap Fix Plan</li>
      </ul>
    </div>
    <div class="stage">
      <div class="code">S5</div>
      <h3>Commitment Readiness</h3>
      <ul>
        <li>Gate Pack</li>
        <li>Formal Recommendation</li>
        <li>Full Go / Conditional / Watch / No Bid</li>
      </ul>
    </div>
  </section>

  <div class="arrow">→ → →  Formal Gate  → → →  Bid Execution</div>

  <section class="workstreams">
    <h2>The four workstreams</h2>
    <span class="label-tag">Running in parallel across all five stages</span>
    <ol>
      <li><strong>Buyer &amp; Opportunity Shaping</strong> — building the buyer decision thesis, anticipating the procurement.</li>
      <li><strong>Competitive &amp; Incumbent Intelligence</strong> — mapping the field, assessing the incumbent, identifying displacement leverage.</li>
      <li><strong>Solution &amp; Proof Strategy</strong> — designing the solution spine, building the proof map, threading win themes.</li>
      <li><strong>Commercial Risk &amp; Suitability</strong> — sizing the commercial stance, reviewing risk, closing gap-fix actions.</li>
    </ol>
    <p style="margin-top:1rem; color: var(--mist);"><em>Plus a fifth workstream — Pursuit Readiness &amp; Governance — running across all four to keep the gate pack on track.</em></p>
  </section>
</main>
</body>
</html>
```

- [ ] **Step 2: Verify the page renders cleanly.**

Open in a browser. Confirm:
- Five stages displayed as a horizontal grid (or 2-column on narrow screens).
- Arrow between S5 and "Bid Execution" reads correctly.
- Workstreams section with 4+1 numbered list.
- Print preview produces a clean, single-page layout.

- [ ] **Step 3: Commit.**

```bash
git add launch-validation/assets/pre-gate-playbook.html
git commit -m "feat(launch-validation): Pre-Gate Pursuit Playbook diagram reserve asset"
```

---

## Task 11 — Data confidence catalogue page

**Authorship:** Claude builds the structure and seeds it from the existing wiki entry at `wiki/intel/pwin-contracts-data-confidence.md` (referenced in the spec). Paul reviews and edits in his own voice if he wants it sharper.

**Files:**
- Create: `launch-validation/assets/data-confidence-catalogue.html`

- [ ] **Step 1: Read the existing wiki entry to lift the content.**

```bash
ls "C:/Users/User/Documents/Obsidian Vault/wiki/intel/pwin-contracts-data-confidence.md" 2>/dev/null && cat "C:/Users/User/Documents/Obsidian Vault/wiki/intel/pwin-contracts-data-confidence.md"
```

If the wiki page does not exist or is empty, fall back to the assertions and limitations described in `CLAUDE.md` under the `pwin-competitive-intel` section ("Known Limitations") and in the spec itself. Use those as the seed content.

- [ ] **Step 2: Write `data-confidence-catalogue.html`.**

The page lists what the contracts database can and cannot honestly assert, organised by category, with a confidence band beside each claim (High / Medium / Low / None). Use the same Midnight Executive style as Tasks 9 and 10.

```html
<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>UK contracts data — what it can and cannot tell us</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --midnight: #0F1B2D;
    --midnight-soft: #1B2A44;
    --gold: #C8A85B;
    --gold-soft: #E5C97A;
    --bone: #F4EFE6;
    --mist: #8A93A6;
    --rule: rgba(255,255,255,0.08);
    --conf-high: #6FBF73;
    --conf-medium: #C8A85B;
    --conf-low: #D9805C;
    --conf-none: #8A93A6;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--midnight); color: var(--bone); font-family: 'DM Sans', system-ui, sans-serif; }
  main { max-width: 980px; margin: 0 auto; padding: 6vh 6vw; }
  .label { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.85rem; color: var(--mist); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem; }
  h1 { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 3rem; margin: 0 0 0.5rem; }
  .subtitle { font-family: 'Cormorant Garamond', serif; font-style: italic; color: var(--gold); font-size: 1.3rem; margin: 0 0 3rem; max-width: 60ch; line-height: 1.4; }
  h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 1.8rem; color: var(--gold-soft); margin: 3rem 0 1rem; }
  .claim { display: grid; grid-template-columns: 110px 1fr; gap: 1.5rem; padding: 1rem 0; border-top: 1px solid var(--rule); }
  .claim:last-child { border-bottom: 1px solid var(--rule); }
  .conf { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.8rem; letter-spacing: 1.5px; text-transform: uppercase; padding: 0.3rem 0.7rem; border-radius: 2px; height: fit-content; text-align: center; }
  .conf.high { color: var(--conf-high); border: 1px solid var(--conf-high); }
  .conf.medium { color: var(--conf-medium); border: 1px solid var(--conf-medium); }
  .conf.low { color: var(--conf-low); border: 1px solid var(--conf-low); }
  .conf.none { color: var(--conf-none); border: 1px solid var(--conf-none); }
  .claim-body p { margin: 0 0 0.4rem; line-height: 1.5; }
  .claim-body .why { font-size: 0.9rem; color: var(--mist); font-style: italic; }
  @media print {
    html, body { background: white; color: black; }
    .conf.high { color: #2e7d32; border-color: #2e7d32; }
    .conf.medium { color: #b8973f; border-color: #b8973f; }
    .conf.low { color: #b35c3c; border-color: #b35c3c; }
    .conf.none { color: #555; border-color: #555; }
    h2, .subtitle { color: #b8973f; }
  }
</style>
</head>
<body>
<main>
  <div class="label">BidEquity / Reserve asset</div>
  <h1>What the data can and cannot tell us</h1>
  <p class="subtitle">A confidence catalogue for the UK contracts intelligence database. The fact that this exists matters as much as what's on it — it's the credibility-honesty signal underneath every claim PWIN makes.</p>

  <h2>What we can assert with high confidence</h2>

  <div class="claim">
    <div class="conf high">High</div>
    <div class="claim-body">
      <p><strong>That a notice was published, on which date, by which buyer, against which CPV code.</strong></p>
      <p class="why">Because: this is what OCDS publishes verbatim. We capture it without interpretation.</p>
    </div>
  </div>

  <div class="claim">
    <div class="conf high">High</div>
    <div class="claim-body">
      <p><strong>That an award decision was published, on which date, naming which supplier(s).</strong></p>
      <p class="why">Because: same provenance, with multi-supplier awards captured via the lots and award_suppliers junctions.</p>
    </div>
  </div>

  <div class="claim">
    <div class="conf high">High</div>
    <div class="claim-body">
      <p><strong>That a contract is approaching expiry, with which incumbent, on which framework.</strong></p>
      <p class="why">Because: derived directly from notice end dates, validated by the canonical layer.</p>
    </div>
  </div>

  <h2>What we can assert with medium confidence</h2>

  <div class="claim">
    <div class="conf medium">Medium</div>
    <div class="claim-body">
      <p><strong>The total value of awards across a buyer or supplier.</strong></p>
      <p class="why">Because: framework values record the maximum, not the realised draw-down. Aggregated totals reflect ceilings, not spend.</p>
    </div>
  </div>

  <div class="claim">
    <div class="conf medium">Medium</div>
    <div class="claim-body">
      <p><strong>That a buyer is part of a consolidated parent (e.g. an executive agency under a Whitehall department).</strong></p>
      <p class="why">Because: the canonical buyer layer covers ~85% of notices. The remaining ~15% are eProcurement intermediaries, private contractors publishing under their own name, and a long tail of one-off entities.</p>
    </div>
  </div>

  <div class="claim">
    <div class="conf medium">Medium</div>
    <div class="claim-body">
      <p><strong>The directors and SIC codes of a UK-registered supplier.</strong></p>
      <p class="why">Because: only ~27% of suppliers in the database have a Companies House number on file. The rest are name-only, GB-PPON-only, non-UK, or public-sector bodies.</p>
    </div>
  </div>

  <h2>What we can assert with low confidence</h2>

  <div class="claim">
    <div class="conf low">Low</div>
    <div class="claim-body">
      <p><strong>That a sub-organisation (e.g. HMPPS, UKVI, ESFA) has a particular spend profile under its parent department.</strong></p>
      <p class="why">Because: about 5% of contract awards (concentrated in MoJ, Home Office, DfE, MoD) are dark at sub-organisation level — the parent name is published, the agency breakout is not. The £25k spend transparency overlay is built but not yet loaded; once loaded, the confidence here improves to medium for those four families.</p>
    </div>
  </div>

  <div class="claim">
    <div class="conf low">Low</div>
    <div class="claim-body">
      <p><strong>The historical win rate of a named supplier against a named buyer.</strong></p>
      <p class="why">Because: we see published awards, not non-awards. A supplier who bid and lost ten times for one win shows in the data as one win, not 1-of-11. The denominator is hidden.</p>
    </div>
  </div>

  <h2>What we cannot assert</h2>

  <div class="claim">
    <div class="conf none">None</div>
    <div class="claim-body">
      <p><strong>Why a particular award decision went a particular way.</strong></p>
      <p class="why">Because: scoring rationale is not published. We can infer pattern; we cannot read minds.</p>
    </div>
  </div>

  <div class="claim">
    <div class="conf none">None</div>
    <div class="claim-body">
      <p><strong>The bid teams' internal pre-decision win-probability scores.</strong></p>
      <p class="why">Because: they are private to each supplier. Our PWIN engine produces a probability score; it does not read the supplier's own.</p>
    </div>
  </div>

  <div class="claim">
    <div class="conf none">None</div>
    <div class="claim-body">
      <p><strong>The behaviour of strategic buyers below the FTS publication threshold.</strong></p>
      <p class="why">Because: below threshold, awards may publish on Contracts Finder (£10k threshold) or not publish at all. The Contracts Finder ingest is built and live; coverage is improving.</p>
    </div>
  </div>
</main>
</body>
</html>
```

- [ ] **Step 3: Verify the page renders cleanly.**

Open in a browser. Confirm:
- Four sections (High / Medium / Low / None confidence).
- Each claim has a confidence badge in the appropriate colour and a "Because:" line.
- Print preview produces a clean, multi-page layout with confidence colours preserved as legible tones on white.

- [ ] **Step 4: Commit.**

```bash
git add launch-validation/assets/data-confidence-catalogue.html
git commit -m "feat(launch-validation): data confidence catalogue reserve asset"
```

---

## Task 12 — HTML conversation playbook (the wrapper)

**Authorship:** Claude end-to-end. The single page Paul has open on the laptop during a conversation. Embeds the framing paragraph, the four questions, the substantive overview reference, and links to every other artefact in the folder.

**Files:**
- Create: `launch-validation/playbook.html`

- [ ] **Step 1: Write the file.**

```html
<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>BidEquity — Validation Tour Playbook</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --midnight: #0F1B2D;
    --midnight-soft: #1B2A44;
    --gold: #C8A85B;
    --gold-soft: #E5C97A;
    --bone: #F4EFE6;
    --mist: #8A93A6;
    --rule: rgba(255,255,255,0.08);
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--midnight); color: var(--bone); font-family: 'DM Sans', system-ui, sans-serif; line-height: 1.55; }
  .layout { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 220px 1fr; gap: 3rem; padding: 4vh 4vw; }
  nav { position: sticky; top: 4vh; align-self: start; font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.85rem; }
  nav h2 { color: var(--mist); text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.75rem; margin: 0 0 1rem; font-family: inherit; font-weight: 500; }
  nav ol { padding-left: 1.2em; margin: 0; }
  nav li { margin-bottom: 0.6rem; }
  nav a { color: var(--bone); text-decoration: none; }
  nav a:hover { color: var(--gold); }
  main h1 { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 2.8rem; margin: 0 0 0.5rem; }
  main .label { font-family: 'DM Mono', ui-monospace, monospace; font-size: 0.85rem; color: var(--mist); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem; }
  main h2 { font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 1.8rem; color: var(--gold-soft); margin: 3rem 0 1rem; padding-top: 2rem; border-top: 1px solid var(--rule); }
  main h3 { font-family: 'DM Sans', sans-serif; font-weight: 700; font-size: 1.05rem; margin: 1.5rem 0 0.5rem; color: var(--gold); }
  main p, main li { max-width: 70ch; }
  blockquote { margin: 1.5rem 0; padding: 1rem 1.5rem; background: var(--midnight-soft); border-left: 3px solid var(--gold); font-style: italic; color: var(--bone); }
  blockquote p { margin: 0 0 0.6rem; }
  blockquote p:last-child { margin-bottom: 0; }
  .questions { display: grid; gap: 1rem; margin: 1.5rem 0; }
  .q { padding: 1rem 1.2rem; background: var(--midnight-soft); border-left: 3px solid var(--gold); }
  .q .num { font-family: 'Cormorant Garamond', serif; color: var(--gold); font-size: 1.3rem; }
  .q .text { display: block; margin: 0.3rem 0 0.5rem; font-size: 1.05rem; }
  .q .listen { font-size: 0.85rem; color: var(--mist); font-family: 'DM Mono', ui-monospace, monospace; }
  table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.95rem; }
  th, td { text-align: left; padding: 0.7rem 0.6rem; border-bottom: 1px solid var(--rule); vertical-align: top; }
  th { font-family: 'DM Mono', ui-monospace, monospace; color: var(--mist); text-transform: uppercase; letter-spacing: 1px; font-size: 0.75rem; font-weight: 500; }
  a { color: var(--gold); }
  a:hover { color: var(--gold-soft); }
  .reminder { padding: 1.5rem; background: var(--midnight-soft); border: 1px dashed var(--gold); margin: 1.5rem 0; }
  .reminder strong { color: var(--gold-soft); }
  @media (max-width: 800px) { .layout { grid-template-columns: 1fr; } nav { position: static; } }
</style>
</head>
<body>
<div class="layout">

<nav>
  <h2>Sections</h2>
  <ol>
    <li><a href="#purpose">Purpose</a></li>
    <li><a href="#opening">Opening &amp; consent</a></li>
    <li><a href="#overview">Substantive overview</a></li>
    <li><a href="#questions">The four questions</a></li>
    <li><a href="#close">Close</a></li>
    <li><a href="#assets">Asset shelf</a></li>
    <li><a href="#prereads">Pre-read emails</a></li>
    <li><a href="#capture">Capture &amp; synthesis</a></li>
  </ol>
</nav>

<main>
  <div class="label">BidEquity / Validation Tour Playbook</div>
  <h1>The conversation playbook</h1>
  <p>This document is for me, not for them. They never see it. They see the website pre-read and my face. — Paul</p>

  <h2 id="purpose">Purpose</h2>
  <p>Three things I want from every conversation, in priority order:</p>
  <ol>
    <li><strong>Validation</strong> — does the proposition hold up under honest scrutiny?</li>
    <li><strong>Recruitment</strong> — does anyone get excited enough to come on board?</li>
    <li><strong>Pivot signal</strong> — should I redirect this entirely?</li>
  </ol>
  <p>The frame is <em>"help me solve a problem here"</em>, not <em>"here's what I built, what do you think?"</em>.</p>

  <div class="reminder"><strong>Discipline.</strong> No more than two reserve assets surfaced in any one conversation. A third means I've stopped listening.</div>

  <h2 id="opening">Opening &amp; consent (0–4 min)</h2>

  <h3>The framing paragraph (deliver verbatim, then a beat of silence)</h3>
  <blockquote>
    <p>"I'm not here to pitch you anything. I've spent a year and a half building something — a methodology and a platform for how strategic suppliers in UK public sector should pursue their bids — and I'm a few weeks away from making it public.</p>
    <p>Before I do, I want to spend an hour with people I trust, including you, on three things I genuinely don't know the answer to. I'd value you pushing back hard rather than being kind."</p>
  </blockquote>

  <h3>The recording-consent ask</h3>
  <blockquote>
    <p>"Before we start — I'd like to record this so I can listen back properly afterwards rather than scribbling notes. The recording stays with me, gets transcribed for my own synthesis, and isn't published anywhere. Is that OK with you?"</p>
  </blockquote>
  <p><em>If yes:</em> start recording. <em>If no:</em> fall back to written notes via <a href="templates/conversation-capture.md">templates/conversation-capture.md</a>. The conversation still happens, no friction.</p>

  <h2 id="overview">Substantive overview (4–16 min)</h2>
  <p>Open <a href="deck.html" target="_blank">deck.html</a> in a second tab. Walk through the eight slides, modulating per audience.</p>

  <table>
    <tr><th>Audience</th><th>Linger on</th><th>Compress</th></tr>
    <tr><td><strong>A</strong> Industry insiders</td><td>Slides 4, 5, 6 (methodology + platform + data layer)</td><td>Slides 2, 3 (problem + diagnosis)</td></tr>
    <tr><td><strong>B</strong> Senior business non-industry</td><td>Slides 2, 7 (problem + honest state)</td><td>Slides 4, 5, 6 (methodology + platform + data layer)</td></tr>
    <tr><td><strong>C</strong> Potential commercial buyers</td><td>Slides 2, 5 (problem + platform)</td><td>Slide 6 (data layer)</td></tr>
  </table>

  <p><em>Watch them while talking.</em> If a slide visibly lands or visibly bores them, compress or expand on the fly. The deck is a visual anchor, not a teleprompter.</p>

  <h2 id="questions">The four questions (16–55 min)</h2>
  <p>Pick two or three. Order organically. Silence is welcome.</p>

  <div class="questions">
    <div class="q">
      <span class="num">Q1</span>
      <span class="text">What founding-team / leadership configuration would make this platform survive a strategic supplier's "who else is behind this?" question?</span>
      <span class="listen">Listen for: CTO with platform pedigree · recognisable name on the board · partner firm fronting the route to market · names mentioned spontaneously.</span>
    </div>
    <div class="q">
      <span class="num">Q2</span>
      <span class="text">What would actually trigger a top-40 strategic supplier's leadership team to change how they pursue bids?</span>
      <span class="listen">Listen for: competitor-adopts · regulatory shift · revenue/win-rate pressure · board cost-out programme · new commercial leadership · reactions to the "challenger eats their breakfast" hypothesis.</span>
    </div>
    <div class="q">
      <span class="num">Q3</span>
      <span class="text">Who do you know — for either side of this?</span>
      <span class="listen">Listen for: build side (co-founder, director, partner) and buy side (intro to a buyer). Even tentative names. Write them down then.</span>
    </div>
    <div class="q">
      <span class="num">Q4</span>
      <span class="text">What am I missing? If you were me, would you redirect this entirely?</span>
      <span class="listen">Listen for: pivot signals · adjacent markets · adjacent products · adjacent business models.</span>
    </div>
  </div>

  <div class="reminder">If they push back on the £3bn / £2bn at slide 2, <strong>Q2 has just opened naturally</strong>. Skip the rest of the overview and run with it.</div>

  <h2 id="close">Close (55–60 min)</h2>
  <ol>
    <li><strong>The distilled prompt.</strong> <em>"What's the single thing you'd want me to think hardest about between now and when this goes public?"</em></li>
    <li><strong>One exit ask</strong> (whichever fits — never plant more than one cold):
      <ul>
        <li><em>Introduction.</em> "Who could you put me in front of for this?"</li>
        <li><em>Involvement.</em> "Is this something you'd want to be part of in some shape?" (only if the conversation has clearly gone there)</li>
        <li><em>Pressure-test loop.</em> "Can I come back to you in three months when this is in the market and tell you what happened?"</li>
      </ul>
    </li>
    <li><strong>A specific thank-you.</strong> Name the exact thing they pushed hardest on. Commit to a next step on the spot.</li>
    <li><strong>Stop the recording before standing up.</strong></li>
  </ol>

  <h2 id="assets">Reserve asset shelf</h2>
  <p>Surface live <em>only</em> when the conversation earns it. Never volunteer.</p>
  <table>
    <tr><th>Asset</th><th>Surface when they ask</th></tr>
    <tr><td><a href="../pwin-competitive-intel/bidequity-cfo-model.html" target="_blank">CFO model</a></td><td>"Where do those numbers come from?" / "What does the client maths look like?"</td></tr>
    <tr><td><a href="assets/pwin-five-layers.html" target="_blank">Five-layer PWIN explainer</a></td><td>"How is this different from a scorecard?"</td></tr>
    <tr><td><a href="https://bidequity.co.uk/qualify-app.html" target="_blank">Live Qualify walkthrough</a></td><td>"Show me how it actually works"</td></tr>
    <tr><td><a href="assets/data-confidence-catalogue.html" target="_blank">Data confidence catalogue</a></td><td>"How honest are you about what the data can and can't tell you?"</td></tr>
    <tr><td><a href="assets/pre-gate-playbook.html" target="_blank">Pre-Gate Playbook diagram</a></td><td>"What's the methodology, exactly?"</td></tr>
    <tr><td><a href="https://bidequity.co.uk/perspective/founder-interview" target="_blank">Founder interview</a></td><td>"Tell me about you" — point them at it as a follow-up read</td></tr>
  </table>

  <h2 id="prereads">Pre-read emails (send 48–72 hours before)</h2>

  <h3>For audience A — industry insiders</h3>
  <blockquote><p>"I've spent 18 months building a methodology and a platform for how strategic suppliers in UK public sector should pursue bids — including a five-year, 175,000-contract intelligence database. Before I take it public next month, I want to spend an hour with people who know how this market actually works. The site is at <a href="https://bidequity.co.uk">bidequity.co.uk</a> if you want a 10-minute scan beforehand — particularly the founder interview at /perspective. I'll talk you through what's behind it, and then I want to ask you three or four hard questions I genuinely don't know the answers to. No pitch."</p></blockquote>

  <h3>For audience B — senior business non-industry</h3>
  <blockquote><p>"I'm a few weeks away from launching a business — BidEquity — that I've been building quietly for the last 18 months. Before I do, I want to spend an hour with people whose judgement I trust, including yours. There are two or three questions I genuinely don't know the answer to that you might help me think through. The website is at <a href="https://bidequity.co.uk">bidequity.co.uk</a> if you want a quick look — the founder interview at /perspective is the closest thing to a manifesto. No pitch, no slides, just a conversation."</p></blockquote>

  <h3>For audience C — potential commercial buyers</h3>
  <blockquote><p>"I'm getting close to launching a business focused on how strategic suppliers like yours pursue UK public sector bids. Before I do, I'm taking an hour with a small number of senior people on the buyer side — not to sell to them, but to ask whether they think the proposition holds up, and what would have to be true for a firm like theirs to entertain it. Worth ten minutes of your time on <a href="https://bidequity.co.uk">bidequity.co.uk</a> first if you're willing. I'd value the honest read."</p></blockquote>

  <h2 id="capture">Capture &amp; synthesis</h2>
  <ol>
    <li>Stop the recording before standing up.</li>
    <li>Within 30 minutes: transfer the recording, transcribe (Otter / Notta / MacWhisper / equivalent).</li>
    <li>Run the transcript through <a href="templates/synthesis-prompt.md">templates/synthesis-prompt.md</a>.</li>
    <li>Save the synthesised Markdown to <code>conversations/YYYY-MM-DD-&lt;initials&gt;-&lt;audience-code&gt;.md</code> (gitignored by default).</li>
    <li>Update the row in <a href="templates/synthesis-log.csv">templates/synthesis-log.csv</a> and <a href="synthesis-log.md">synthesis-log.md</a>.</li>
    <li>Purge raw audio and transcript once the synthesis has been reviewed.</li>
    <li>Read the synthesis log every 3–4 conversations, not after every one.</li>
  </ol>
</main>

</div>
</body>
</html>
```

- [ ] **Step 2: Verify the playbook renders and every link resolves.**

Open in a browser. Confirm:
- Two-column layout with sticky nav on the left.
- Eight sections present and reachable from nav.
- All `href` links to local assets resolve (open each one). The two `bidequity.co.uk` links are intentional external links.
- The CFO-model link resolves to the local `pwin-competitive-intel/bidequity-cfo-model.html` file.
- Print preview is readable.

- [ ] **Step 3: Commit.**

```bash
git add launch-validation/playbook.html
git commit -m "feat(launch-validation): conversation playbook (HTML wrapper, framing + questions + asset shelf)"
```

---

## Task 13 — Final consistency pass and tour-readiness check

**Authorship:** Claude end-to-end. A read-through of every artefact for cross-references, broken links, and consistency.

**Files:**
- Modify (if needed): any of the files above.
- Create: `launch-validation/READY.md` (the tour-readiness checklist).

- [ ] **Step 1: Walk every cross-reference.**

```bash
ls launch-validation/
ls launch-validation/assets/
ls launch-validation/templates/
```

Then:

- Open `playbook.html` in a browser. Click every link. Note any that 404.
- Open `deck.html` and `deck.pptx` side by side. Confirm slide content matches.
- Open all three `assets/*.html` pages. Confirm they style consistently (same palette, same header pattern, same print stylesheet).
- Open `templates/synthesis-prompt.md` and `templates/conversation-capture.md` side by side. Confirm every heading the prompt names is present in the template.
- Open `templates/synthesis-log.csv` and `synthesis-log.md`. Confirm the column set is consistent.
- Open `cfo-stress-test.md`. Confirm the structure is fillable.

- [ ] **Step 2: Fix any inconsistencies inline. Recommit per fix.**

Make Edits as needed. Each fix is its own small commit, e.g.:

```bash
git add <file>
git commit -m "fix(launch-validation): correct dead link in playbook to pre-gate diagram"
```

- [ ] **Step 3: Write the tour-readiness checklist.**

Create `launch-validation/READY.md`:

```markdown
# Tour-readiness checklist

Run through this before booking the first conversation. Tour is ready when every box is ticked.

## Artefacts built
- [ ] `playbook.html` opens in browser, all links resolve.
- [ ] `deck.html` opens, advances 8 slides via arrow keys, `?notes=1` reveals speaker notes.
- [ ] `deck.pptx` mirrors the 8 slides with speaker notes in the Notes pane.
- [ ] `assets/pwin-five-layers.html` opens, prints cleanly.
- [ ] `assets/pre-gate-playbook.html` opens, prints cleanly.
- [ ] `assets/data-confidence-catalogue.html` opens, prints cleanly.
- [ ] `templates/synthesis-prompt.md` is self-contained — every reference defined within the prompt.
- [ ] `templates/conversation-capture.md` matches the structure the synthesis prompt outputs.
- [ ] `templates/synthesis-log.csv` and `synthesis-log.md` columns are consistent.
- [ ] `cfo-stress-test.md` is fillable.
- [ ] `.gitignore` excludes audio extensions, transcripts, and `conversations/20*.md`.

## Pre-tour preparation (Paul)
- [ ] CFO stress-test memo filled in. Three closing self-assessments answered.
- [ ] Audience list drafted: Wave 1 (B, 3–4 people), Wave 2 (A, 4–6 people), Wave 3 (C, 3–5 people).
- [ ] First Wave 1 conversation booked. Pre-read email sent 48–72 hours ahead.
- [ ] Recording tool chosen and tested (Otter / Notta / MacWhisper / phone voice memo).
- [ ] Transcription path tested end-to-end on a dummy 10-minute recording.
- [ ] Privacy convention chosen for the synthesis log (local-only or anonymised commit).

## On the day
- [ ] Laptop charged. Playbook open in tab 1. Deck open in tab 2. Asset pages each in a tab, ready.
- [ ] Phone or recorder ready. Consent ask rehearsed.
- [ ] Five minutes before the conversation, re-read the framing paragraph aloud.

## After every conversation
- [ ] Recording transferred and transcribed within the same day.
- [ ] Synthesis prompt run, output saved to `conversations/`.
- [ ] Synthesis log updated.
- [ ] Raw audio and transcript purged once synthesis reviewed.

## Decision gate (week 7)
- [ ] One-page memo written answering the three week-7 questions.
- [ ] Public LinkedIn launch decision: on / off / pivot.
```

- [ ] **Step 4: Commit.**

```bash
git add launch-validation/READY.md
git commit -m "feat(launch-validation): tour-readiness checklist"
```

---

## Self-review

**Spec coverage check.** Each spec section maps to at least one task:

- Spec Section 1 (Playbook structure) → Task 12 (HTML playbook wrapper).
- Spec Section 2 (Framing, four questions, exit asks) → Task 12 (embedded in playbook).
- Spec Section 3 (Substantive overview, five chunks) → Tasks 6, 7, 8 (deck content, HTML deck, PowerPoint deck).
- Spec Section 4 (Conversation flow, pre-read variants) → Task 12 (flow timing and three pre-read emails embedded in playbook).
- Spec Section 5 (Reserves: asset shelf, capture, CFO prep) → Tasks 2, 3, 4, 5, 9, 10, 11.
- Spec Section 6 (Sequencing) → Task 5 (synthesis log includes wave-status table); Task 13 (READY checklist).
- Spec "Decisions taken at spec time" → Task 1 (folder structure), Task 7 (HTML deck), Task 8 (PowerPoint), Tasks 3–5 (synthesis path).
- Spec "What gets built (artefact inventory)" — all 11 items mapped to tasks 1–13.

**Placeholder scan.** No "TBD" / "TODO" / "fill in details" / "similar to Task N" patterns. Every code block is complete and runnable as written. The CFO stress-test deliberately uses placeholders for Paul's prose — those are author-fill points, not plan failures, and the placeholder text is clearly marked `_Write here_`.

**Type / cross-reference consistency.** The synthesis prompt (Task 3) names the same five chunks, four questions, and audience codes used in the deck (Tasks 6–8), the playbook (Task 12), the capture template (Task 4), and the log (Task 5). Audience codes A/B/C/D used identically across all artefacts. The framing paragraph is identical in the spec, the playbook, and the synthesis prompt's context block.

**Scope check.** This plan covers a single artefact set with shared content. No subsystems requiring decomposition. Build sequence is naturally TDD-shaped (template → content → render): Tasks 1–5 build infrastructure and templates; Tasks 6–8 build the substantive content layer; Tasks 9–11 build the reserve assets; Task 12 wraps the playbook; Task 13 reviews and ships.

---

## Implementation note: privacy convention deferred decision

The spec deferred one decision to the implementation plan: whether the synthesis log is local-only (`synthesis-log.local.md`, fully gitignored) or committed in anonymised form (audience type only, no initials, no third-party names). This plan defaults to **the anonymised commit path** — `synthesis-log.md` is committed (Task 5), the per-conversation files in `conversations/` are gitignored (Task 1), and Paul can override to fully local by renaming `synthesis-log.md` → `synthesis-log.local.md` and adding it to `.gitignore`. If Paul prefers the fully-local default, swap the file names in Tasks 1 and 5 before execution.
