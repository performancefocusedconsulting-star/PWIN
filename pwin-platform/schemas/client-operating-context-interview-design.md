# Client Operating Context — Interview Skill Design

**Status:** design v1, 2026-04-14
**Consumes:** nothing (top of the chain)
**Produces:** populated `client-operating-context.json` per the lean-8 schema

---

## Purpose

Structured AI-led interview skill that produces a signed-off Client Operating Context document as part of a billable onboarding engagement (£15–25k range). Three role-based interview variants, synchronous with consultant facilitation, voice-in / text-out, live claim capture with in-session approval.

This is the **first** of the four-step onboarding package:
1. Desk baseline (AI alone, ~1 hour)
2. **AI-avatar structured interview — this skill**
3. Archive mining (separate skill, later)
4. Leadership workshop (facilitated, captures tensions)

---

## Three interview variants

Each variant maps to a client role and populates a specific subset of the schema. The full context doc requires all three.

### Variant 1 — Leadership Interview

- **Interviewee:** Managing Partner / CEO / growth lead
- **Duration:** 90 minutes
- **Mode:** AI-led (avatar runs the script, consultant on standby)
- **Schema coverage:**
  - `strategicObjectives` (growth priorities, priority sectors, target contract bands, strategic tensions)
  - `pursuitPreferences` (preferred buyers, routes, deal archetypes, avoid archetypes, no-go triggers)
  - `riskGuardrails.redLines`
  - `differentiation.trueDifferentiators` (leadership's view — archive agent will cross-check later)
  - `identity.businessModel`, `identity.size` confirmation

### Variant 2 — Bid Operations Interview

- **Interviewee:** Bid Director / Pursuit Lead / Head of Sales Ops
- **Duration:** 90 minutes
- **Mode:** Consultant-led (human runs the conversation, AI listens and drafts claims)
- **Schema coverage:**
  - `historicPerformance` (win/loss patterns, common loss reasons, bad-win patterns, should-have-no-bid patterns)
  - `differentiation.doNotOverclaim`, `differentiation.proofPoints` (known approved claims)
  - `capabilityMap.capacityConstraints`
  - `pursuitPreferences.noGoTriggers` (operational triggers, distinct from leadership's strategic no-gos)

Reason this variant is consultant-led: the real material here is political and unflattering — "we keep winning work we shouldn't," "this capability is weaker than we tell clients." An AI avatar asking that directly will get sanitised answers. A consultant with rapport will not.

### Variant 3 — Commercial Interview

- **Interviewee:** Finance Director / Commercial Director
- **Duration:** 60 minutes
- **Mode:** AI-led
- **Schema coverage:**
  - `commercialProfile` (preferred roles, pricing preferences, margin expectations, risk tolerance, bid-cost tolerance)
  - `riskGuardrails.marginFloorPct`, `riskGuardrails.approvalThresholds`
  - `riskGuardrails.capabilityStretchTolerance`, `partnerDependencyTolerance`

---

## Claim capture flow (per question)

Every question in every variant follows the same live loop:

1. **AI asks the question** (text-to-speech if voice out enabled, otherwise on-screen text the avatar "speaks").
2. **Client answers verbally.**
3. **AI transcribes** (Whisper or equivalent) and displays transcript in left panel.
4. **AI drafts a claim** from the answer and renders it as a claim card in the right panel:
   - `statement` (what the client said, cleaned up)
   - `claimType` (fact / interpretation / assumption / hypothesis / unknown — AI's initial typing)
   - `confidence` (AI's initial read)
   - `sources` (auto-filled with this interview's sourceId)
5. **Client reviews the claim card** and one of:
   - Taps "approve as-is" → claim enters schema with `approvedForAiUse: true`
   - Taps "edit" → edits statement or claim type, then approves
   - Taps "reject" → claim is discarded, AI moves on
   - Says "not sure" → claim is saved with `claimType: assumption` and flagged for leadership workshop
6. **AI moves to next question**, branching based on answer.

Consultant can intervene at any point to override AI's claim typing, add context, or redirect the interview.

---

## UI shape (synchronous session)

Split-screen web app, run on a laptop or large tablet in the room (or shared over video call):

```
┌──────────────────────────────────────────────────────────────────┐
│  LEADERSHIP INTERVIEW — Example Consulting Ltd                    │
│  Interviewer: Sarah Chen (Managing Partner)                       │
│  Progress: Section 3 of 7 — Pursuit Preferences     [42 min left] │
├─────────────────────────────┬────────────────────────────────────┤
│                             │                                    │
│  TRANSCRIPT                 │  LIVE CLAIMS                       │
│                             │                                    │
│  [AI]: What types of        │  ┌──────────────────────────────┐  │
│  pursuits does the firm     │  │ Preferred buyer type         │  │
│  most want to win over      │  │ UK central government        │  │
│  the next 12 months?        │  │ Type: fact  Conf: high       │  │
│                             │  │ [Approve] [Edit] [Reject]    │  │
│  [SARAH]: Mostly UK         │  └──────────────────────────────┘  │
│  central government, some   │                                    │
│  NHS, but only digital      │  ┌──────────────────────────────┐  │
│  transformation — we've     │  │ Preferred deal archetype     │  │
│  got burned on managed      │  │ Digital transformation       │  │
│  services...                │  │ Type: fact  Conf: high       │  │
│                             │  │ [Approve] [Edit] [Reject]    │  │
│                             │  └──────────────────────────────┘  │
│                             │                                    │
│                             │  ┌──────────────────────────────┐  │
│                             │  │ Avoid archetype              │  │
│                             │  │ Managed services (burned)    │  │
│                             │  │ Type: fact  Conf: high       │  │
│                             │  │ Reason: prior losses         │  │
│                             │  │ [Approve] [Edit] [Reject]    │  │
│                             │  └──────────────────────────────┘  │
│                             │                                    │
├─────────────────────────────┴────────────────────────────────────┤
│  [🎤 Recording]  [⏸ Pause]  [Consultant intervene]  [Next section]│
└──────────────────────────────────────────────────────────────────┘
```

Consultant has a separate "intervene" action — overrides AI's next question, flags a claim for review, or pauses the session.

---

## Interview guides (per variant)

Each variant is a structured YAML guide — sections, questions, follow-up branches, claim-mapping rules. Not a rigid script; more like a prompt template the avatar uses.

**Guide structure:**

```yaml
variant: leadership
sections:
  - id: strategic-objectives
    durationMinutes: 20
    openingQuestion: "Looking at the next 12-24 months, what does successful growth look like for the firm?"
    branches:
      - if: answer_mentions("sector")
        followup: "Which sectors specifically? And which ones are you deliberately stepping back from?"
        mapsTo: strategicObjectives.prioritySectors
      - if: answer_mentions("size" or "scale")
        followup: "What contract value range should pursuits fall into? What's too small, and what's too big for the firm to absorb?"
        mapsTo: strategicObjectives.targetContractValueBands
      - if: answer_is_vague()
        followup: "Can you give me an example of a deal from the last 12 months that would be 'successful growth' for you? And one that wasn't?"
    tensionProbes:
      - "You mentioned wanting bigger deals. What gets in the way — capacity, commercial risk, or leadership alignment?"
    claimExtractionHints:
      - "Convert directional statements to claimType: fact only if client confirms with specifics. Otherwise interpretation."
```

The guide is versioned content, editable by the consultant between engagements. Like Qualify's `qualify-content.json` pattern — the scoring brain is config, not code.

---

## Deliverables per session

### End of each session
- Populated schema subset for that variant (JSON file)
- Transcript (markdown + audio file)
- Session summary for consultant review:
  - Claims approved (count)
  - Claims rejected (count)
  - Claims flagged as assumption for leadership workshop
  - Tensions surfaced (for workshop agenda)

### End of full interview cycle (3 sessions)
- Merged client-operating-context.json (all three variants stitched together)
- Divergence report: claims from one variant that contradict another (e.g. leadership says "we want larger deals", bid ops says "we keep losing anything over £5m") — feeds `strategicTensions`
- Workshop agenda: contested claims, assumptions awaiting leadership resolution
- Client signoff doc: PDF rendering of the schema for client approval and `approvedForAiUse: true` flip

---

## What's in scope for V1

- Three interview guides (YAML, editable)
- Voice-in transcription (Whisper API)
- Text-out avatar rendering (simple — stylised waveform or static persona image, not synthetic video)
- Live claim capture UI (split screen, approve/edit/reject)
- Consultant intervene action
- Session-level schema output (JSON)
- Transcript export (markdown)
- Cross-variant merge at end of cycle
- Client signoff PDF rendering

## What's out of scope for V1

- Archive mining (separate skill, later)
- Divergence detector in full (merge surfaces contradictions; richer detection is V2)
- Leadership workshop facilitation tooling (workshop runs on a whiteboard; AI just produces the agenda)
- Voice-out synthetic avatar video (text-out only)
- Multi-language support (English only)
- Fully async interview mode (synchronous only — client + consultant both present)
- Integration with PWIN platform (standalone web app; JSON imports into platform post-signoff)

---

## Build order

1. **Interview guide authoring** (1 week) — write the three guides as YAML, including all question branches and claim-mapping rules. This is the content brain; everything else is scaffolding.
2. **Claim capture UI** (1.5 weeks) — split-screen web app, transcript + claim cards, approve/edit/reject, intervene, session state persistence.
3. **Voice pipeline** (0.5 weeks) — Whisper integration, live transcription display.
4. **Avatar layer** (0.5 weeks) — text-out only (rendered text or TTS, no synthetic video).
5. **Session output + cross-variant merge** (0.5 weeks) — schema assembly, divergence surfacing, transcript export, signoff PDF.
6. **Pilot with one real client** (1–2 weeks calendar) — run all three interviews, refine guides based on what the consultant had to intervene on.

Total build: ~4 weeks to pilot-ready.

---

## Key risks and how to handle them

**Risk 1: Client hates the avatar.**
Mitigate by making the avatar minimal — just an AI interviewer card, no synthetic face, no uncanny valley. Frame as "AI-assisted structured interview," not "meet your AI interviewer."

**Risk 2: AI misreads claim types.**
Mitigate by defaulting to the weakest typing the answer will support (`interpretation` over `fact`, `assumption` over `interpretation`) and requiring explicit client approval to upgrade. The consultant can bulk-upgrade in post-review.

**Risk 3: Leadership gives sanitised answers.**
That's exactly why the Bid Operations variant is consultant-led — the real material comes out there. The Leadership interview is expected to be partly aspirational; the divergence with Bid Ops surfaces the gap.

**Risk 4: Transcription errors around proper nouns, client names, programme names.**
Mitigate by loading a client-specific vocabulary into Whisper before the session (firm name, known competitors, key programmes, named partners). Consultant briefs the AI before the session starts.

**Risk 5: Session runs over time.**
Hard stops built into the guide. If 90 minutes elapse, AI surfaces "unanswered critical questions" as flagged assumptions for the workshop rather than pushing through.

---

## Open design questions

1. **TTS or not?** Does the avatar actually *speak* the questions aloud, or does it just display them as text the consultant reads? TTS adds production polish but makes the session feel less like a real conversation when there's already a human in the room.
2. **Recording consent and storage.** Where do session audio files live? Client-confidential by default. Clarify retention policy before building — some clients will refuse recorded sessions.
3. **Mid-session edits to the schema.** Can the consultant add a claim manually during the session (outside the AI's question flow), or only edit claims the AI has drafted? Simpler to restrict to AI-drafted only in V1.
4. **What if the client wants to pause and resume across days?** Session state persistence is needed either way, but a multi-day leadership interview has very different energy than a single 90-minute session. Recommend: hard single-session rule for V1.
