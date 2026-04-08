---
name: Post-mapping action items from Session 12
description: 2026-04-01 — five follow-up actions after completing all 84 activities / 295 L3 tasks across 10 workstreams
type: project
---

## Action 1: Validate archetype assumption across ALL workstreams — DONE (2026-04-02)

Current assumption: only the SOL workstream varies between the three archetypes (Services, Technology/Digital, Consulting/Advisory). Other workstreams (SAL, COM, LEG, DEL, SUP, BM, PRD, GOV, POST) stay the same.

**RESULT:** Assumption partially failed. COM and DEL also need variant documents. 15 other activities need archetype notes. See commit d21d37e.

**Action:** Go through every non-SOL workstream and validate whether this assumption holds. Check each activity for archetype sensitivity. For example:
- COM: does the commercial model change fundamentally for consulting (time & materials vs fixed price)?
- LEG: TUPE doesn't apply for consulting/digital — does LEG-04 deactivate?
- DEL: transition planning is very different for digital (deployment) vs consulting (light mobilisation)
- SUP: partner model may be very different for consulting (associate network) vs services (subcontractor consortium)
- PRD: response structure may differ — consulting bids are often CV-led, not solution-narrative-led

**Why:** If we build the product assuming only SOL varies, we may discover mid-build that other workstreams need archetype variants too. Better to validate now.

## Action 2: Build role-based agent personas from L3 RACI data

Now we have 295 L3 tasks with full RACI, we can build per-role views:

**2a: Client Agent / Agent MD per role**
- For each role (Bid Manager, Bid Director, Solution Architect, Commercial Lead, Delivery Director, Legal Lead, etc.), extract all L3 tasks where they are R or A
- This creates a complete role-based task list: "As the Bid Manager, here are all 87 tasks you are responsible for across the bid lifecycle"
- This becomes the Claude agent persona brief — the agent knows what the role does, what they own, and what they produce

**2b: L4 skills and SOPs from L3 tasks**
- Each L3 task can be decomposed into L4 steps — the actual procedure for executing the task
- These become standard operating procedures (SOPs) for each task
- For AI-suitable tasks, L4 becomes the skill definition: inputs, processing logic, outputs, quality checks
- This is a bottom-up approach to building AI skills — grounded in the actual methodology, not speculative

**Why:** The L3 methodology is the WHAT. L4/skills are the HOW. Building bottom-up from confirmed methodology ensures AI capabilities are grounded in real bid process, not generic AI hype.

## Action 3: AI suitability assessment across all 295 L3 tasks

For every L3 task, assess:

**AI suitability rating:**
- **High** — AI can execute autonomously or near-autonomously (e.g., document analysis, requirements extraction, compliance mapping, risk register consolidation, evidence library search)
- **Medium** — AI can assist and accelerate but human judgement required (e.g., stakeholder sentiment assessment, win theme development, scoring strategy, commercial modelling)
- **Low** — fundamentally human activity (e.g., client relationship meetings, governance presentations, negotiation, team leadership)

**For each task rated High or Medium, capture:**
- What the AI agent would need as input (documents, data, context)
- What external documentation inputs are needed that we may not currently have access to
- What the AI would produce as output
- What human oversight is needed (review, approve, iterate)
- Key challenges or blockers (data availability, judgement complexity, client sensitivity)
- Estimated productivity impact — how much faster/better with AI vs without

**Why:** This creates the roadmap for the PWIN Architect Plugin — grounded in actual methodology tasks, prioritised by impact, with clear input/output requirements. It also identifies where we need to acquire or connect to external data sources (e.g., Contracts Finder API, Gartner benchmarks, Companies House data).

## Action 4: Competitive Dialogue methodology detail

BM-09 exists as an activity ("Competitive dialogue management") with 2 L3 tasks covering preparation and session recording. However, competitive dialogue (CD) and competitive procedure with negotiation (CPN) are complex procurement routes with their own distinct lifecycle and activities.

**What's needed:**
- CD/CPN is not just one activity — it's a multi-round process with distinct phases: initial dialogue, solution iteration per round, commercial negotiation per round, final tender invitation
- Each round has: preparation, presentation/discussion, feedback capture, solution/commercial iteration, governance re-check
- The solution and pricing evolve through dialogue — SOL and COM activities may iterate multiple times
- There are specific rules under the Procurement Act about what can and cannot change during dialogue
- The methodology currently treats CD as a single BM activity — it should probably be a sub-methodology or activation that changes how multiple activities behave (iterative vs single-pass)

**Approach:** Either expand BM-09 with detailed L3/L4 tasks covering the multi-round dialogue lifecycle, or design CD/CPN as an activation mode that modifies the behaviour of existing activities (SOL, COM, LEG iterate per round rather than running once). The latter is architecturally cleaner.

**Why:** CD/CPN is increasingly common in UK government procurement, especially for complex services (defence, justice, health). If the product doesn't handle it properly, it misses a significant portion of the target market.

## Action 5: Selection Questionnaire (SQ) stage methodology

The product is currently designed around the main procurement stage: ITT receipt through to contract award. But most UK government procurements have an earlier stage — previously called PQQ/RFP, now called **Selection Questionnaire (SQ)** under the Procurement Act 2023.

**What the SQ stage involves:**
- Assessment of suitability — organisational capability, financial standing, insurance, compliance, exclusion grounds
- Past performance and referenceability — case studies, credentials, client references
- Technical capability — relevant experience, qualifications, capacity
- Typically lighter: fewer activities, shorter timeline, no pricing, no solution design
- The output is: pass/fail to proceed to ITT, or a scored shortlist

**Current assumption:** Tackle ITT stage first (done), then adapt for SQ. The hypothesis is that SQ is a subset — mostly deactivating activities rather than creating new ones.

**What needs validating:**
- Which of the 84 activities apply at SQ stage? Probably a small subset: SAL-01 (intelligence), SAL-10 (stakeholders), SOL-10 (evidence), SUP-01 (partners for referenceability), PRD-02 (SQ response writing), PRD-08/09 (QA and submission), GOV-01 (pursuit approval)
- Are there SQ-specific activities not in the current methodology? E.g., exclusion grounds assessment, financial standing documentation, Selection Questionnaire form completion
- How does the product handle the transition from SQ to ITT? Does a bid that passes SQ carry forward its data into the ITT stage?

**Approach:** Design SQ as an activation mode or "phase 1" within the existing product. Minimal new activities, mostly deactivation of ITT-stage activities. The key is ensuring data continuity from SQ to ITT.

**Why:** Many opportunities start at SQ stage. If the product only supports ITT onwards, bid managers must manage SQ externally and manually transition into the product at ITT receipt. This breaks the end-to-end lifecycle promise.

## How to approach these actions

These are analysis exercises, not design exercises. They should be done in separate sessions:
- Action 1: ~2 hours — systematic walkthrough of each non-SOL workstream per archetype
- Action 2: data extraction exercise — pull RACI per role from gold standard, create role task lists
- Action 3: ~4-6 hours — systematic assessment of each L3 task for AI suitability
- Action 4: ~2 hours — design the CD/CPN activation model (probably an architecture session, not just methodology)
- Action 5: ~2-3 hours — map which activities apply at SQ stage, identify any SQ-specific activities, design the SQ→ITT data continuity

All should be captured in new documents in the docs folder, not in the gold standard itself.

## Priority order (suggested)

1. **Action 1** (archetype validation) — DONE (2026-04-02)
2. **Action 3** (AI suitability) — DONE (2026-04-02). See ai_suitability_assessment.md
3. **Action 2** (role-based agents) — builds on Action 3, creates the agent persona briefs
4. **Action 5** (SQ stage) — product scope expansion, important but not blocking the ITT-stage build
5. **Action 4** (competitive dialogue) — procurement route variant, important but less common than standard ITT
