# Rubric Review Guide — 24 Questions

A working reference for editing the rubric wording in `qualify-content-v0.1.json`. Use this when reviewing each of the 24 questions, one at a time.

---

## What the rubric actually does

The rubric text **is** the rule book. The AI reads each level's wording verbatim, compares it to the user's typed evidence, and decides whether to validate the user's claimed score or downgrade it. The wording is also what disciplines users at the moment they pick a label. **Tighter wording = lower pre-AI scores AND tougher AI verdicts. Same lever, two channels.**

The rubric text never enters the scoring math directly. It works entirely by gating which label the user is entitled to and which label the AI thinks the evidence supports.

---

## The pattern every rubric line must follow

A well-formed line has **three components**, every time:

| Component | What it means | Examples |
|---|---|---|
| **Artefact** | What document, output, or record exists | "strategy document", "stakeholder map", "costed counter-plan", "minuted feedback" |
| **Specificity** | How named, dated, attributed it is | "at least two named competitors", "dated within last 90 days", "signed off by capture lead" |
| **Distribution / use** | Who has it, who has acted on it, what changed because of it | "briefed to bid team", "shaping evaluation criteria", "embedded in solution design" |

**If a line is missing any of the three, rewrite it.** A line with only an artefact ("a strategy exists") gives the AI nothing to check against and the verdict becomes a vibes-check.

---

## What each of the four levels is for

The four lines answer four versions of the same question. Each line is a complete checklist for *its* level — not a partial version of the level above.

| Level | Question the line answers |
|---|---|
| **Strongly Agree** | What does it look like when this is **demonstrably true and externally verifiable**? |
| **Agree** | What does it look like when this is **internally true but not yet externally validated**? |
| **Disagree** | What does it look like when this is **partial, assumed, or in progress**? |
| **Strongly Disagree** | What does it look like when this is **absent, unaddressed, or not understood as a question**? |

The Disagree and Strongly Disagree lines deserve as much care as the top two. A loose D line ("limited evidence") lets the AI park borderline cases there without committing. A tight D line ("artefact exists but is undated, undistributed, or not owned") forces a real call.

---

## Per-question review workflow

For each of the 24 questions, work top-to-bottom in this order.

### Step 1 — Read the question text first

Make sure the question text and the rubric are talking about the same thing. The rubric must score *the question as written*, not a slightly different question. If the question text is woolly, fix the question first.

### Step 2 — Read the SA line

Ask:
- Does it name an **artefact**?
- Is it **specific** (named, dated, attributed, costed, signed off)?
- Does it require **distribution or use** (who has it, what has changed because of it)?
- Could a real bid team **point to it** if challenged in 30 seconds?

If any answer is no, rewrite the line.

### Step 3 — Read the Agree line

Ask:
- Is it the same artefact as SA but **without external validation**?
- Is the gap between SA and A a **single concrete missing item** (not a fuzzy "less mature")?
- Could a reviewer cleanly say "this is A not SA because X is missing"?

If the gap is fuzzy, the AI will land borderline cases inconsistently.

### Step 4 — Read the Disagree line

Ask:
- Does it describe **partial, assumed, or in-progress** work?
- Is the artefact still present in some form (draft, fragment, undocumented), or is it **inferred from context only**?
- Is the threshold for D obviously above SD?

### Step 5 — Read the Strongly Disagree line

Ask:
- Does it describe **absence**, not just weakness?
- Would the team **not even understand the question as a question**?
- Is it the floor — nothing below it counts as anything else?

### Step 6 — Apply the two-reviewer test

For each line independently, ask:

> **Could two different reviewers, looking at the same piece of user evidence, independently reach the same verdict using only this line?**

If yes → the line is doing its job.
If no → it is still subjective. Rewrite it as a checklist of observable artefacts.

The AI is one of those reviewers. The more checklist-shaped your line, the more reproducible the AI's verdicts become.

### Step 7 — Check the inflation signals for that question

Each question also has an `inflationSignals` array — the linguistic tells the AI watches for. They must be **paired with the rubric**:

- If you tighten the rubric, you usually need to broaden the signals (more phrases that indicate someone is over-claiming against the new standard).
- If you loosen the rubric, you must loosen the signals too — otherwise the AI returns "Validated" verdicts with `inflationDetected: true`, contradicting itself.

### Step 8 — Sanity-check the whole 4-line ladder

Read all four lines top to bottom. Ask:
- Does each level **clearly demand more** than the one below?
- Are the gaps roughly **equal** between levels (no cliff between A and D, no near-duplicate between SA and A)?
- Could a user reading the four lines **self-locate** without having to guess?

If a user cannot tell SA from A from the wording alone, neither can the AI.

---

## Anti-patterns to delete on sight

Strike any line that contains:

- **"We are confident…"** / **"The team believes…"** / **"We feel…"** — vibes, not evidence
- **"Generally aligned"** / **"Broadly understood"** / **"In good shape"** — unfalsifiable
- **"A strategy exists"** without naming distribution or sign-off — artefact without status
- **"Some" / "Several" / "A number of"** without a number — soft quantifiers
- **"Recently" / "Up to date"** without a time bound (use "within 90 days", "since last gate", etc.)
- **"Could be improved"** / **"More work needed"** in the Disagree line — describes a feeling, not a state

---

## After you finish editing

Three things, in this order, before you commit:

1. **Bump version + add changelog entry** in the JSON file header.
2. **Run the eval harness:**
   ```bash
   ANTHROPIC_API_KEY=sk-... node pwin-qualify/content/eval-harness.js
   ```
   Expect a chunk of previously-Validated fixtures to flip to Challenged. **This is not a regression** — it is the rubric doing more work. Re-grade the fixtures against the new standard and update the expected verdicts where the new wording genuinely changes the right answer.
3. **Run the build:**
   ```bash
   node pwin-qualify/content/build-content.js
   ```
   Both HTML apps will be re-injected with the new content. Commit the JSON and both HTML files together.

---

## What you should NOT touch while reviewing rubrics

Stay out of these — they are stable and tuned separately:

- **Question weights** (`qw`)
- **Category weights** (`weight`, `weightProfiles`)
- **The 4 / 3 / 2 / 1 point mapping** in `scorePts`
- **Category definitions and IDs**
- **Opportunity-type calibration paragraphs** (separate lever)

If you find yourself wanting to change one of these to make a rubric "work", the rubric wording is wrong — fix the wording, not the weight.

---

## One-line test you can apply to every edit

> **"If a bid team handed me their evidence and I read only this line, could I tell them yes or no without asking a follow-up question?"**

If yes → ship it.
If no → keep rewriting.
