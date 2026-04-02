# Agent 5: Content & Response Drafting

**Version:** 1.0 | April 2026
**Status:** Design specification — authoritative input for skill implementation
**Parent document:** `pwin_architect_plugin_architecture.md` (v1.5, Section 4.2a)
**Data model authority:** `bid_execution_architecture_v6.html`
**Insight skill specs:** `ai_use_cases_reference.html` (v1.1, UC15)

---

## 1. Agent Identity

**Purpose:** Drafts response sections, executive summaries, governance packs, evidence compilation. The production workhorse — the most visible agent to the bid team because its outputs are what gets submitted.

**System prompt essence:** "You are a bid response writer and production specialist. You draft responses that answer the question asked, follow the question structure, integrate win themes with evidence, and are calibrated to the client's scoring scheme. You write to score marks, not to impress with prose. Every sentence must earn its place against the word limit."

**Operating principles:**
- Answer the question asked — not the question you wish they'd asked.
- Follow the question structure — if the client asks for 4 things, structure the answer in 4 parts.
- Integrate win themes with evidence — a theme without a case study is an assertion, not a differentiator.
- Respect word limits absolutely — every word costs proportionally against the limit.
- Write for evaluators, not for the bid team. Evaluators are scoring against criteria, not reading for pleasure.
- Governance packs must be factual and decision-ready — not advocacy documents.

---

## 2. Agent Configuration

**Tools available:**

| Tool | Purpose |
|---|---|
| `get_response_sections` | Read the exam paper — the questions this agent must answer |
| `get_response_items` | Read production items (storyboard, draft status, quality scores) |
| `get_evaluation_framework` | Read evaluation methodology and scoring scale |
| `get_win_themes` | Read win themes with evidence and linked response sections |
| `get_client_scoring_scheme` | Read client marking scheme grade bands and descriptors |
| `get_review_cycles` | Read review cycle status (pink/red/gold) and reviewer assignments |
| `get_open_review_actions` | Read unresolved review actions for a response section |
| `get_gate_status` | Read governance gate status for gate pack assembly |
| `get_gate_preparation` | Read gate preparation data (readiness indicators, blockers) |
| `get_compliance_requirements` | Read compliance matrix for final verification |
| `get_quality_gaps` | Read quality dimension gaps flagged by reviewers |
| `get_bid_library_match` | Search evidence library for matching credentials (placeholder until Bid Library product built) |
| `generate_report_output` | Write governance packs, reports, and formatted deliverables |
| Template populator | Populate response draft templates and governance pack proformas |

**Tools NOT available (by design):**
- Web search (that's Agent 2)
- Document reader for uploaded ITT files (that's Agent 1)
- Spreadsheet/calculation tools (that's Agent 4)
- AIInsight write tools (that's Agent 3, except UC15 which this agent owns)

**Knowledge scope:**
- All upstream structured data via MCP read tools (response sections, evaluation framework, win themes, review scorecards, gate status)
- Client scoring scheme grade band descriptors (the rubric evaluators score against)
- Evidence library (placeholder — credential matching against past case studies, CVs, certifications)
- UK public sector bid writing conventions (structured responses, evaluator-centric language, evidence-based assertions)

---

## 3. Skills

Agent 5 owns 7 skills: 6 productivity skills and 1 insight skill.

### 3.1 Productivity Skills

---

#### Skill 1: Response Section Drafting (`response-drafting`)

**Priority:** BUILD FIRST — highest-volume skill. PRD-02 alone is 60 person-days of effort in methodology, with 35-60% direct AI reduction.
**Command:** `/pwin:draft-response`
**Trigger:** Human-invoked. Bid manager selects a ResponseSection and runs command.
**Depends on:** Agent 1 (ITT extraction — needs ResponseSections), Agent 3 (scoring strategy — needs marks allocation and win theme coverage guidance).

**What it does:**

Drafts a complete response section for a single question in the ITT response template. The draft is calibrated to the evaluation criteria, integrates win themes with evidence, respects the word limit, and self-assesses against the client's scoring scheme where one exists.

**Input specification:**

| Input | Source | Required |
|---|---|---|
| ResponseSection reference | MCP — which question to answer | Yes |
| Storyboard / response structure | MCP — from PRD-02 storyboard stage (if complete) | Recommended |
| Win themes with evidence | MCP — via get_win_themes() | Yes (for quality sections) |
| Evaluation criteria | MCP — from ResponseSection.evaluationCriteria | Yes |
| Client scoring scheme | MCP — via get_client_scoring_scheme() | Optional (not all bids have one) |
| Solution design inputs | Agent 6 output — the substance the response describes | Recommended |
| Competitive positioning | Agent 2 output — differentiation context | Optional |
| Marks allocation guidance | Agent 3 output — where to focus effort within the response | Optional |

**Process:**

```
Step 1: Question analysis
  — Read the ResponseSection (questionText, evaluationCriteria, wordLimit, hurdleScore,
    evaluationMaxScore, evaluationWeightPct)
  — Decompose the question into its constituent parts (sub-questions, requirements)
  — Identify what the evaluator is looking for in each part
  — Read the scoring scheme grade descriptors (if client marking scheme exists)

Step 2: Input assembly
  — Read the linked storyboard/structure (if storyboard stage complete)
  — Read relevant win themes via get_win_themes() — filter to those linked to this section
  — Read evidence/credentials linked to each win theme
  — Read solution design inputs (if available from Agent 6)
  — Read competitive positioning (if available from Agent 2)
  — Read marks allocation guidance (if available from Agent 3)

Step 3: Response drafting
  — Structure the response to mirror the question structure
    (if 4 sub-parts, the answer has 4 corresponding sections)
  — For each section:
    - Answer the specific question asked
    - Integrate the most relevant win theme with supporting evidence
    - Use evaluator-centric language (demonstrate, evidence, assure)
    - Cite specific credentials, case studies, metrics where available
  — Apply word limit discipline — allocate words proportionally to marks per sub-part
  — Include headings and signposting for evaluator scanning

Step 4: Self-assessment
  — Assess the draft against each evaluation criterion listed in the ResponseSection
  — Where client marking scheme exists:
    - Map the draft to the most likely grade band based on grade descriptors
    - Identify what would move the response to the next grade band up
  — Check: does the response answer ALL parts of the question?
  — Check: is the response within word limit?
  — Check: does every assertion have supporting evidence?

Step 5: Gap identification
  — Flag sections where response is below hurdle score (estimated)
  — Flag win themes that should be integrated but have no supporting evidence
  — Flag sub-parts of the question that are weakly answered
  — Flag evidence gaps (claims without case studies or credentials)
  — Note where solution design input is missing (substance gaps)
```

**Output template:**

```
Response Draft: [section reference] — [title]
================================================
Word limit: [limit] | Word count: [actual] | [within/over] limit
Evaluation weight: [weight]% | Max score: [max] | Hurdle: [score or none]

DRAFT RESPONSE
--------------
[Full drafted response text, structured to mirror question parts]

SELF-ASSESSMENT
---------------
Evaluation criterion 1: [criterion text]
  Assessment: [how the draft addresses this]
  Estimated grade band: [band] (if marking scheme exists)
  To improve: [what would move to next band]

Evaluation criterion 2: ...

OVERALL ASSESSMENT
  Estimated score: [score] / [max] ([grade band])
  Hurdle status: [PASS/AT RISK/FAIL]
  Confidence: [HIGH/MEDIUM/LOW]

WIN THEME INTEGRATION
  [theme 1]: Integrated at [paragraph/section ref] with evidence: [credential]
  [theme 2]: Integrated at [paragraph/section ref] with evidence: [credential]
  [theme 3]: NOT integrated — [reason: no evidence / not relevant to this section]

GAPS AND WEAKNESSES
  [numbered list of specific gaps, missing evidence, weak sections]
  Each gap: [description] | Impact: [marks at risk] | Action: [what's needed]
```

**Quality criteria:**
- Must answer all parts of the question — no partial coverage.
- Must follow the question structure (if 4 sub-parts, answer has 4 sections).
- Must integrate at least one win theme with supporting evidence per high-value section.
- Must be within word limit.
- Must include self-assessment against grade descriptors where marking scheme exists.
- Gaps and weaknesses must be explicitly flagged, not glossed over.

**Practitioner design note (from assessment review):**
> "PRD-02 alone is 60 person-days of effort. Even a 35-60% reduction is 21-36 days saved. This is where the volume is. The AI doesn't replace the author — it produces a first draft that the author refines. The difference is starting from a structured, evidence-integrated draft rather than a blank page."

---

#### Skill 2: Executive Summary Drafting (`executive-summary`)

**Command:** `/pwin:exec-summary`
**Trigger:** Human-invoked. Typically run after all or most response sections have been drafted and reviewed.
**Depends on:** Skill 1 (response drafting — needs draft responses for thematic synthesis), Agent 3 (win themes, competitive positioning).

**What it does:**

Drafts the executive summary — the single document every evaluator reads. Synthesises the overarching bid narrative from all response sections, win themes, competitive positioning, and solution summary. This is not a summary of the bid — it's the strategic narrative that frames how the evaluator reads everything else.

**Process:**

```
Step 1: Narrative input assembly
  — Read all ResponseSections and their draft status via get_response_sections()
  — Read all win themes via get_win_themes() — identify the 3-5 dominant themes
  — Read competitive positioning (Agent 2) — what differentiates this bid
  — Read solution summary (Agent 6) — the headline offer
  — Read evaluation framework — what matters most to this client

Step 2: Narrative architecture
  — Opening: client challenge / opportunity framing (shows understanding)
  — Differentiators: 3-5 reasons why this bid wins (linked to evaluation criteria)
  — Evidence anchors: the strongest credentials, each tied to a differentiator
  — Solution headline: what the client gets (outcome-focused, not input-focused)
  — Closing: commitment, transition confidence, relationship intent

Step 3: Draft executive summary
  — Write to word/page limit
  — Every paragraph must serve a scoring purpose — no filler
  — Win themes must be landed with evidence, not stated as assertions
  — Language must match the client's language (from ITT, not supplier jargon)
  — Structure for scanning: evaluators skim before they read

Step 4: Cross-reference check
  — Verify every claim in the executive summary is substantiated in a response section
  — Verify win themes in the summary are consistently landed in the detailed responses
  — Flag any disconnects between summary narrative and response section content
```

**Output template:**

```
Executive Summary Draft
=======================
Word limit: [limit] | Word count: [actual]

DRAFT
-----
[Full executive summary text]

WIN THEME COVERAGE
  [theme]: Landed at [paragraph ref] with [evidence]
  ...

CROSS-REFERENCE CHECK
  [claim in summary] → [substantiated in section ref] ✓
  [claim in summary] → [NOT substantiated — GAP] ✗
  ...

NARRATIVE COHERENCE
  Key differentiators emphasised: [list]
  Evaluation criteria addressed: [list with coverage assessment]
  Client language alignment: [assessment]
```

**Quality criteria:**
- Must be within word/page limit.
- Every differentiator must be evidence-backed, not assertion-only.
- Must address the evaluation criteria that carry the most marks.
- Must use the client's language and framing, not supplier-centric language.
- Cross-reference check must confirm consistency with detailed response sections.

---

#### Skill 3: Evidence Compilation (`evidence-compilation`)

**Command:** `/pwin:evidence-pack`
**Trigger:** Human-invoked. Run per response section or across the full bid.
**Depends on:** Skill 1 (response drafting — needs to know what evidence each section requires).

**What it does:**

Searches the evidence library for relevant case studies, CVs, credentials, and certifications. Matches evidence to response sections by evaluation criteria. Formats evidence to ITT requirements. QAs for consistency across the submission.

**Process:**

```
Step 1: Evidence requirement identification
  — Read ResponseSections via get_response_sections()
  — For each section, identify evidence requirements from:
    - evaluationCriteria (what evaluators expect to see demonstrated)
    - questionText (explicit requests for case studies, CVs, credentials)
    - Win themes linked to this section (each theme needs supporting evidence)
  — Classify evidence type needed: case study, CV, certification, reference,
    methodology document, accreditation, financial statement

Step 2: Evidence library search
  — Search evidence library via get_bid_library_match() for each requirement
  — Match by: sector, contract value, service type, technology, client type,
    team member, certification type
  — Rank matches by relevance to evaluation criteria
  — Flag where no suitable match exists (evidence gap)

Step 3: Evidence formatting
  — Format each evidence item to ITT requirements:
    - Case studies: client, challenge, approach, outcomes, relevance statement
    - CVs: role-relevant experience, qualifications, security clearance status
    - Credentials: certification body, validity dates, scope
  — Apply word/page limits per evidence item (if specified by ITT)
  — Ensure consistency: same case study referenced in multiple sections must
    use consistent facts and figures

Step 4: Quality assurance
  — Cross-check: are the same metrics quoted consistently across all references?
  — Date check: is any evidence outdated (case studies >5 years, expired certifications)?
  — Relevance check: does each evidence item clearly support the evaluation criterion it's cited against?
  — Coverage check: every high-value response section has at least one evidence item
```

**Output template:**

```
Evidence Compilation Report
===========================
Response sections requiring evidence: [count]
Evidence items matched: [count]
Evidence gaps: [count]

PER-SECTION EVIDENCE MAP
  [section ref] — [title]
    Required: [evidence type needed]
    Matched:  [evidence item title] — Relevance: [HIGH/MEDIUM/LOW]
    Matched:  [evidence item title] — Relevance: [HIGH/MEDIUM/LOW]
    Gap:      [evidence type with no match]
    ...

EVIDENCE GAPS ([count])
  [section ref] — [missing evidence type] — Impact: [marks at risk]
  Action required: [source new evidence / request from delivery team / omit]

CONSISTENCY CHECK
  [case study title]: Referenced in [count] sections — [CONSISTENT/INCONSISTENT]
    [inconsistency detail if applicable]

CURRENCY CHECK
  [evidence items expiring within bid contract period]
  [case studies older than 5 years]
```

**Quality criteria:**
- Every response section with scored evaluation criteria must have at least one evidence match.
- Evidence gaps must be explicitly flagged with marks-at-risk assessment.
- Consistency check must catch conflicting metrics across sections (e.g., different revenue figures for the same case study).
- Evidence items must be formatted to ITT specification, not generic format.

---

#### Skill 4: Governance Pack Assembly (`governance-packs`)

**Command:** `/pwin:gate-pack`
**Trigger:** Human-invoked. Bid manager runs before each governance gate.
**Depends on:** Live bid data from all agents — this skill assembles, it does not create source data.

**What it does:**

For each governance gate, assembles the preparation pack from live bid data. The output is a decision-ready document that governance reviewers can read and act on without needing to interrogate the bid team. Each gate has a different pack structure because different decisions require different information.

**Process:**

```
Step 1: Gate identification
  — Read gate status via get_gate_status()
  — Identify which gate is being prepared (GOV-01 through GOV-06)
  — Read gate preparation data via get_gate_preparation()
  — Read gate-specific readiness indicators and blockers

Step 2: Gate-specific data assembly

  GOV-01 — Pursuit Approval (go/no-go):
    — Capture plan summary (opportunity, client, competitive landscape)
    — Bid mandate (strategic rationale, portfolio fit)
    — PWIN score and basis
    — Cost-to-bid estimate and resource plan
    — Risk summary (top 5 risks with mitigations)
    — Recommendation: pursue / do not pursue / pursue with conditions

  GOV-02 — Solution Review:
    — Solution summary (operating model, staffing, technology)
    — Risk position (delivery risks, assumptions, dependencies)
    — Win strategy alignment (does the solution support the win themes?)
    — Compliance status (mandatory requirements met/not met)
    — Solution differentiators vs expected competitor approaches
    — Open issues requiring resolution before submission

  GOV-03 — Pricing Review:
    — Price position (total, per annum, vs budget/benchmark)
    — Margin analysis (target, achieved, risk-adjusted)
    — Pricing sensitivities (what happens if key assumptions change)
    — Risk pricing (contingency, risk register items priced/unpriced)
    — Partner/subcontractor pricing status (confirmed/provisional)
    — Commercial risk summary

  GOV-04 — Executive Approval (final go/no-go):
    — Full bid summary: price, margin, risk, quality assessment
    — PWIN score (updated from GOV-01)
    — Review cycle results (pink/red/gold scores, quality trajectory)
    — Compliance status (final position)
    — Outstanding risks and mitigations
    — Recommendation: submit / do not submit / submit with conditions

  GOV-06 — Legal Review:
    — Contract positions (accepted, amended, outstanding)
    — Risk allocation summary (liability cap, indemnities, LDs)
    — TUPE position and cost implications
    — Data protection and security obligations
    — IP position (licence vs assignment)
    — Outstanding legal issues and fallback positions

Step 3: Pack formatting
  — Apply governance pack template for the specific gate
  — Structure for decision-making: situation, analysis, recommendation
  — Include supporting data tables and summaries
  — Flag items requiring decision (not just information)

Step 4: Readiness assessment
  — Assess whether the gate is ready to convene based on data completeness
  — Flag missing inputs that would prevent an informed decision
  — List pre-conditions not yet met
```

**Output template:**

```
GOVERNANCE PACK: [Gate Name] — [GOV-XX]
========================================
Bid: [title]
Gate date: [scheduled or proposed]
Pack prepared: [date]

READINESS ASSESSMENT
  Gate ready to convene: [YES/NO]
  Missing inputs: [list or none]
  Pre-conditions outstanding: [list or none]

[GATE-SPECIFIC SECTIONS — as defined in Step 2 above]

DECISION REQUIRED
  [specific decision(s) the governance board must make]
  Recommendation: [specific recommendation with rationale]

APPENDICES
  [supporting data, risk register extract, scoring summaries]
```

**Quality criteria:**
- Every data point must be sourced from live bid data, not fabricated or assumed.
- The pack must be decision-ready — a governance reviewer should not need to ask "what do you want me to decide?"
- Missing inputs must be flagged prominently, not buried.
- The recommendation must be honest and evidence-based — governance packs are not advocacy documents.

---

#### Skill 5: Production Formatting & QA (`production-formatting`)

**Command:** `/pwin:format-check`
**Trigger:** Human-invoked. Run before each review cycle and before final submission.
**Depends on:** Skill 1 (response drafting — needs draft content to format and check).

**What it does:**

Applies corporate template formatting, checks page and word limits, proof-reads, spell-checks, and verifies internal cross-references. The quality gate before content enters the review cycle or goes to final submission.

**Process:**

```
Step 1: Template application
  — Apply corporate response template formatting to draft content
  — Check font, heading styles, numbering conventions, table formatting
  — Apply consistent figure/table captioning and numbering
  — Verify headers/footers match ITT requirements (bid reference, page numbers)

Step 2: Limit compliance
  — Check word count per response section against wordLimit
  — Check page count per section against pageLimit (if applicable)
  — Flag sections exceeding limits with overrun amount
  — Identify candidates for reduction (lowest-value content per evaluation criteria)

Step 3: Language QA
  — Spell-check with UK English dictionary
  — Grammar and readability check
  — Acronym consistency (first use expanded, subsequent abbreviated)
  — Terminology consistency (same concept uses the same term throughout)
  — Passive voice flagging (evaluators prefer active, confident language)

Step 4: Cross-reference verification
  — Do internal cross-references ("see Section 3.2") point to the correct content?
  — Do figure/table references match actual figure/table numbers?
  — Are case study references consistent across sections?
  — Do personnel references match CV pack names and titles?

Step 5: QA report generation
  — Produce itemised QA report with severity ratings
  — Critical: exceeds word/page limit, missing mandatory content
  — Major: broken cross-references, inconsistent evidence
  — Minor: spelling, grammar, formatting inconsistencies
```

**Output template:**

```
Production QA Report
====================
Sections checked: [count]
Total issues: [count] (Critical: [c] | Major: [m] | Minor: [n])

CRITICAL ISSUES ([count])
  [section ref] — [issue] — [detail]
  ...

MAJOR ISSUES ([count])
  [section ref] — [issue] — [detail]
  ...

MINOR ISSUES ([count])
  [section ref] — [issue] — [detail]
  ...

WORD/PAGE LIMIT COMPLIANCE
  [section ref]: [actual] / [limit] — [PASS/OVER by X]
  ...

CROSS-REFERENCE CHECK
  [ref] → [target] — [VALID/BROKEN]
  ...

OVERALL: [READY FOR REVIEW / ISSUES MUST BE RESOLVED]
```

**Quality criteria:**
- Word/page limit checks must be exact — no tolerance for overruns.
- Cross-reference checks must cover all internal references, not a sample.
- Spelling must use UK English conventions (programme, organisation, licence).
- QA report must be actionable — every issue has a specific location and fix.

---

#### Skill 6: Final Compliance Verification (`compliance-verification`)

**Command:** `/pwin:final-compliance`
**Trigger:** Human-invoked. Run as the last check before submission.
**Depends on:** All upstream skills — this is the final gate before the bid leaves the building.

**What it does:**

Final pre-submission compliance check. Verifies all mandatory requirements are addressed, all mandatory documents are present, all pricing schedules are populated, all declarations are signed. This is a pass/fail gate — any failure is a disqualification risk.

**Process:**

```
Step 1: Mandatory requirement verification
  — Read all ComplianceRequirements via get_compliance_requirements()
  — Filter to mandatory and pass_fail requirements
  — For each: verify the linked ResponseSection contains a compliant response
  — Flag any mandatory requirement with non_compliant or not_assessed status

Step 2: Document completeness check
  — Read the ITT-specified list of mandatory documents
  — Verify each mandatory document exists in the submission pack:
    - All response sections (quality, price, social value)
    - Pricing schedules (all tabs/sheets populated)
    - Declarations and certificates (signed/completed)
    - Case studies (correct number, within format requirements)
    - CVs (all named personnel, correct format)
    - Certificates and accreditations (valid, in date)
    - Any ITT-specific mandatory annexes

Step 3: Pricing schedule verification
  — All mandatory cells populated (no blanks in required fields)
  — Totals consistent (line items sum to totals)
  — Currency and VAT treatment consistent
  — All pricing assumptions documented

Step 4: Declaration and certification check
  — All mandatory declarations completed
  — Signatory details correct (name, title, authority)
  — Dates within validity period
  — Any required third-party certifications included

Step 5: Submission logistics check
  — File naming convention matches ITT requirements
  — File formats match ITT requirements (PDF, Word, Excel as specified)
  — File sizes within portal upload limits (if known)
  — Submission deadline: [time remaining]
```

**Output template:**

```
SUBMISSION READINESS CHECKLIST
==============================
Submission deadline: [date/time] — [hours remaining]
Overall status: [READY / NOT READY — [count] blockers]

MANDATORY REQUIREMENTS ([pass count]/[total])
  [req ref] — [requirement] — [PASS/FAIL]
  ...

MANDATORY DOCUMENTS ([present count]/[required count])
  [document] — [PRESENT/MISSING]
  ...

PRICING SCHEDULES
  [schedule name] — [COMPLETE/INCOMPLETE — [detail]]
  ...

DECLARATIONS & CERTIFICATES
  [declaration] — [COMPLETE/INCOMPLETE]
  ...

SUBMISSION LOGISTICS
  File naming: [COMPLIANT/NON-COMPLIANT]
  File formats: [COMPLIANT/NON-COMPLIANT]
  ...

BLOCKERS ([count])
  [numbered list of items that MUST be resolved before submission]

WARNINGS ([count])
  [items that are non-blocking but represent risk]

VERDICT: [CLEAR TO SUBMIT / DO NOT SUBMIT — resolve blockers first]
```

**Quality criteria:**
- Zero tolerance for missed mandatory requirements — every mandatory item must be verified.
- Blockers must be binary: the bid either can or cannot be submitted.
- Warnings are distinct from blockers — they represent risk, not disqualification.
- The verdict must be unambiguous. If there is any doubt, the answer is DO NOT SUBMIT.

---

### 3.2 Insight Skills

---

#### Skill 7: Post-Submission Presentation Intelligence (`presentation-intelligence`) — UC15

**Command:** `/pwin:presentation-prep`
**Trigger:** On-demand (V1). Triggered when POST-01 starts (V2).
**Depends on:** Gold review completion — needs ReviewScorecard data from the final review cycle.

**What it does:**

Reads the gold review scorecards, response items, win themes, and unresolved review actions. Identifies the 3-5 questions evaluators will most likely probe — those where the predicted client score falls in a lower grade band or sits narrowly above a hurdle. For each, drafts the most probable evaluator question, a recommended answer, and the evidence to have to hand. This is presentation rehearsal intelligence.

**Full specification:** `ai_use_cases_reference.html`, UC15.

**Process:**

```
Step 1: Vulnerability identification
  — Read ReviewScorecard data from gold review via get_review_cycles()
    (predictedClientScore, predictedClientGradeBand, per-dimension scores)
  — Read ResponseSection data (evaluationCriteria, hurdleScore, evaluationMaxScore)
  — Read ResponseItem data (qualityScoreGap, owner, status)
  — Identify the 3-5 most vulnerable sections:
    - Predicted score in a lower grade band (e.g., "Good" when "Excellent" needed)
    - Narrowly above hurdle (within one grade band of failing)
    - High-mark sections with quality gaps
    - Sections with unresolved gold review actions (accepted but not fixed)

Step 2: Evaluator question prediction
  — For each vulnerable section:
    - Analyse the evaluation criteria and grade band descriptors
    - Identify what would cause an evaluator to score down
    - Draft the most probable evaluator question (what they will probe)
    - Draft a recommended answer (concise, evidence-backed, confident)
    - List the evidence to have to hand (case study details, metrics, named personnel)

Step 3: Win theme reinforcement
  — Read win themes via get_win_themes()
  — Identify win themes underintegrated in the written submission
    (linked to response sections but weakly evidenced)
  — For each: draft a verbal reinforcement opportunity
    (the presentation is a second chance to land themes the submission didn't land fully)

Step 4: Accepted weakness briefing
  — Read ReviewAction records with status = accepted (not resolved) from gold review
  — For each accepted weakness:
    - What the reviewer flagged
    - Why it was accepted (time/evidence constraint)
    - The evaluator's likely line of questioning
    - Recommended response if probed

Step 5: Write back to application
  — Write presentation preparation brief to POST-01 activity output field
  — Write win theme reinforcement recommendations
  — Write rehearsal script outline to POST-02 activity as preparation input
```

**Output:** AIInsight records written to app (see UC15 spec for schema). Plus:

```
PRESENTATION PREPARATION BRIEF
===============================
Bid: [title]
Presentation date: [date or TBC]
Prepared from: Gold review completed [date]

PREDICTED PROBE AREAS (ranked by risk)

1. [Section ref] — [title]
   Predicted score: [score]/[max] ([grade band])
   Hurdle: [score or N/A] — [ABOVE/AT RISK]
   Most likely question: "[drafted evaluator question]"
   Recommended answer: "[concise, evidence-backed response]"
   Evidence to hand: [case study, metric, named person]

2. [Section ref] — [title]
   ...

WIN THEME REINFORCEMENT OPPORTUNITIES
  [theme]: Underintegrated in [section ref(s)]
  Verbal opportunity: "[how to reinforce in presentation]"
  ...

ACCEPTED WEAKNESSES — PROBE PREPARATION
  [review action ref]: [weakness description]
  Accepted because: [rationale]
  If probed: "[recommended response]"
  ...

REHEARSAL PRIORITIES
  1. [highest-risk probe area — rehearse first]
  2. [second-highest — rehearse second]
  ...
```

**Quality criteria:**
- Probe areas must be ranked by marks-at-risk, not arbitrarily.
- Evaluator questions must be specific to the evaluation criteria, not generic.
- Recommended answers must be concise enough to deliver verbally (not essay-length).
- Evidence references must be specific (named case study, named person, specific metric) — not "relevant experience."
- Win theme reinforcement must identify genuine gaps, not repeat themes already well-landed.

---

## 4. Agent Build Sequence

| Order | Skill | Type | Dependencies | Validates |
|---|---|---|---|---|
| 1 | Response Section Drafting | Productivity | Agent 1 output (ResponseSections) + Agent 3 output (win themes, scoring strategy) + MCP read tools | Full drafting pipeline: read question → assemble inputs → draft → self-assess |
| 2 | Executive Summary Drafting | Productivity | Skill 1 output + MCP read tools | Cross-section narrative synthesis |
| 3 | Evidence Compilation | Productivity | MCP read tools + evidence library (placeholder) | Evidence matching and gap identification pattern |
| 4 | Governance Pack Assembly | Productivity | MCP read tools (all entities) + generate_report_output | Gate-specific data assembly and report generation |
| 5 | Production Formatting & QA | Productivity | Skill 1 output + template engine | Format verification and cross-reference checking |
| 6 | Final Compliance Verification | Productivity | MCP read tools (ComplianceRequirements, ITTDocuments) | Pre-submission compliance gate |
| 7 | Presentation Intelligence | Insight | Gold review data + MCP read tools | UC15 — evaluator question prediction from review scorecards |

---

## 5. Metrics

| Metric | Value |
|---|---|
| Total methodology tasks served | ~27 |
| High-rated tasks | 9 |
| Medium-rated tasks | 8 |
| Low-rated tasks | 10 |
| Average effort reduction | 34% |
| Implementation phase | Phase 4 (alongside Agent 3 expansion) |
| Methodology activities covered | PRD-02.1.1-3, PRD-03.1.1-2, PRD-08.1.1-2, PRD-09.1.1, GOV-01.1.1, GOV-02.1.1, GOV-03.1.1, GOV-04.1.1, GOV-06.1.1, POST-01 |
| Insight skills | UC15 (Post-Submission Presentation Intelligence) |
| Estimated person-days saved per bid | ~20-25 (high volume despite moderate reduction %) |
| NOTE | PRD-02 alone is 60 person-days effort — even 35-60% reduction = 21-36 days saved |

---

## 6. Relationship to Other Agents

**Agent 5 consumes from ALL other agents — it sits at the end of the dependency chain:**

| Upstream Agent | What Agent 5 consumes |
|---|---|
| Agent 1 (Document Intelligence) | ResponseSections (the questions to answer), evaluation criteria (what evaluators look for), compliance requirements (what must be addressed) |
| Agent 2 (Market Intelligence) | Competitive positioning (how to differentiate responses), client profiling (language, priorities, culture) |
| Agent 3 (Strategy & Scoring) | Scoring strategy, marks allocation guidance (where to focus effort), win theme coverage requirements (which themes to land where), review quality analysis (what reviewers flagged) |
| Agent 4 (Commercial & Financial) | Commercial narrative and pricing rationale (for pricing response sections), cost model summaries (for governance packs) |
| Agent 6 (Solution & Delivery) | Solution design (the substance responses describe), operating model, staffing, transition approach, technical architecture |

**Agent 5 outputs feed into:**

| Downstream Consumer | What it receives from Agent 5 |
|---|---|
| Agent 3 (Strategy & Scoring) | Response drafts feed review quality analysis (Agent 3 analyses what Agent 5 produces) |
| Review cycles | Formatted drafts enter the pink/red/gold review pipeline |
| Governance gates | Gate packs enable governance decision-making |
| Final submission | The ultimate deliverable — what gets submitted to the client |

**Agent 5 never produces source data.** It assembles, drafts, and formats. The substance comes from all other agents. This is by design — it's the production layer.

---

*Agent 5: Content & Response Drafting | v1.0 | April 2026 | PWIN Architect*
*7 skills (6 productivity, 1 insight) | ~27 methodology tasks | 34% avg effort reduction*
