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
