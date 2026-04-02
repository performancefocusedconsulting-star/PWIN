# Agent 1: Document Intelligence

**Version:** 1.0 | April 2026
**Status:** Design specification — authoritative input for skill implementation
**Parent document:** `pwin_architect_plugin_architecture.md` (v1.5, Section 4.2a)
**Data model authority:** `bid_execution_architecture_v6.html`
**Insight skill specs:** `ai_use_cases_reference.html` (v1.1, UC13 and UC14)

---

## 1. Agent Identity

**Purpose:** Ingest uploaded bid documents (ITT packs, contracts, policies, clarification logs), extract structured data, and write it into the bid execution app via MCP. This agent transforms documents into actionable bid data. Every other agent depends on its outputs.

**System prompt essence:** "You are a document intelligence analyst specialising in UK public sector procurement. You read bid documentation with absolute precision — every requirement, every clause, every evaluation criterion. You extract structured data, not summaries. You flag ambiguity rather than interpreting it. You never invent requirements that aren't in the document."

**Operating principles:**
- Extract, don't interpret. Flag ambiguity for human resolution.
- Miss nothing. A missed mandatory requirement is a disqualification risk.
- Preserve source traceability. Every extracted item links back to its source document, page, and clause.
- Structured output only. No narrative unless specifically requested. Data goes into the app via MCP write tools.

---

## 2. Agent Configuration

**Tools available:**

| Tool | Purpose |
|---|---|
| PDF/Word document reader | Read uploaded ITT pack documents |
| `create_response_section` | Write extracted exam paper questions |
| `batch_create_response_sections` | Bulk write during full ITT ingestion |
| `create_evaluation_framework` | Write extracted evaluation methodology |
| `create_itt_document` | Register documents in the ITT document registry |
| `update_bid_procurement_context` | Write procurement context fields to Bid entity |
| `ingest_scoring_scheme` | Write client scoring scheme with grade bands |
| `get_response_sections` | Read existing sections (for clarification/amendment cross-referencing) |
| `get_compliance_requirements` | Read compliance data (for impact analysis) |
| `get_risks` | Read risk register (for clarification impact on assumptions) |
| `flag_response_section_amended` | Mark sections affected by clarification/amendment |
| `create_standup_action` | Generate actions from clarification/amendment impact |
| `generate_report_output` | Store narrative reports (ITT briefing) |

**Tools NOT available (by design):**
- Web search (that's Agent 2)
- Spreadsheet/calculation tools (that's Agent 4)
- Response drafting tools (that's Agent 5)

**Knowledge scope:**
- Uploaded ITT document pack (primary input)
- Existing bid data via MCP read tools (for cross-referencing during amendments/clarifications)
- UK public procurement conventions (evaluation methodology patterns, mandatory/desirable classification, MEAT scoring, pass/fail thresholds)

---

## 3. Skills

Agent 1 owns 7 skills: 5 productivity skills and 2 insight skills.

### 3.1 Productivity Skills

---

#### Skill 1: ITT Extraction (`itt-extraction`)

**Priority:** BUILD FIRST — foundation skill, all other Agent 1 skills depend on it.
**Command:** `/pwin:ingest-itt`
**Trigger:** Human-invoked. Bid manager uploads ITT document pack and runs command.

**What it does:**

Reads the full ITT document pack and extracts three categories of structured data:

1. **ResponseSections (the exam paper)** — every question the bid must answer, with evaluation weight, word/page limit, scoring criteria, hurdle marks, and response type.
2. **EvaluationFramework (the scoring methodology)** — MEAT/lowest price/quality only, quality/price/social value weights, scoring scale, pass/fail criteria, presentation/BAFO expectations.
3. **ITTDocuments (the document registry)** — every document in the pack with volume type, version, file type, and parse status.

Plus procurement context fields written to the Bid entity: procurement route, portal, contract duration, extension options, TUPE applicability, security clearance tier.

**Input specification:**

| Input | Source | Required |
|---|---|---|
| ITT Volume 1 — Instructions to Tenderers | Uploaded PDF/Word | Yes |
| ITT Volume 5 — Response Templates | Uploaded PDF/Word | Yes (for response section structure) |
| ITT Volume 2 — Specification | Uploaded PDF/Word | Optional in V1 (requirements extraction is V2) |
| ITT Volume 3 — Contract / T&Cs | Uploaded PDF/Word | Optional (contract analysis is a separate skill) |
| ITT Volume 4 — Pricing Schedules | Uploaded PDF/Word | Optional (commercial analysis is Agent 4) |
| Any additional volumes/annexes | Uploaded PDF/Word | Optional |

**Process:**

```
Step 1: Document registration
  — Catalogue every document uploaded
  — Classify by volume type (instructions/specification/contract/pricing/response_template/other)
  — Write ITTDocument records via create_itt_document()

Step 2: Evaluation framework extraction
  — Read Volume 1 for evaluation methodology
  — Extract: methodology type, quality/price/social value weights, scoring scale,
    scoring descriptors per band, pass/fail criteria, moderation process,
    presentation requirement, BAFO expectation
  — Write via create_evaluation_framework()

Step 3: Response section extraction
  — Read Volume 5 (response templates) for question structure
  — Cross-reference with Volume 1 for evaluation criteria per section
  — For each response section, extract:
    - reference (e.g., "Q2.1", "Section 4.1")
    - title
    - questionText (full question including sub-parts)
    - responseType (quality/price/social_value/commercial/legal)
    - evaluationCategory
    - evaluationWeightPct
    - evaluationMaxScore
    - evaluationCriteria (what evaluators are looking for)
    - hurdleScore (if applicable)
    - wordLimit / pageLimit
    - sourceDocumentId (link to ITTDocument)
  — Write via batch_create_response_sections()

Step 4: Procurement context extraction
  — Extract from Volume 1:
    - procurementRoute (open/restricted/competitive_dialogue/negotiated/framework_call_off)
    - portalPlatform and portalReference
    - contractDurationMonths and extensionOptions
    - tupeApplicable (boolean)
    - securityClearanceTier
    - isRebid indicator
    - Key dates: submission deadline, clarification deadline, evaluation period, contract start
  — Write via update_bid_procurement_context()

Step 5: Client scoring scheme (if exists)
  — If Volume 1 contains a marking scheme with grade bands and descriptors:
    - Extract maxScore, each grade band (minScore, maxScore, label, descriptor)
    - Write via ingest_scoring_scheme()
  — If no marking scheme found, flag as absent (isActive: false)
```

**Output template:**

The primary output is structured data written directly to the app via MCP. Additionally, the skill produces a summary report:

```
ITT Ingestion Summary
=====================
Documents registered:        [count] documents across [count] volumes
Response sections extracted:  [count] sections
  - Quality:                 [count] ([weight]% of total marks)
  - Price:                   [count]
  - Social Value:            [count]
Evaluation framework:        [methodology type], [quality]%/[price]%/[sv]%
Scoring scale:               [scale description]
Client marking scheme:       [found/not found]
Hurdle marks:                [count] sections with hurdle requirements
Procurement route:           [route]
Submission deadline:         [date]
Contract value:              [duration] months + [extensions]
TUPE:                        [applicable/not applicable]
Security clearance:          [tier or none]

Extraction confidence:       [HIGH/MEDIUM/LOW]
Items requiring human review: [count]
  - [list of sections/fields where extraction was uncertain]
```

**Quality criteria:**
- Every response section in the ITT response template must be captured. Zero tolerance for missed sections.
- Evaluation weights must sum to 100% (or flag discrepancy for human review).
- Hurdle marks must be identified for every section that has one — a missed hurdle is a submission risk.
- Source traceability: every extracted field links to a document + page/section reference.
- If a field cannot be confidently extracted, it must be flagged as "requires human review" — never guessed.

**Practitioner design note (from assessment review):**
> "The bid manager downloads from the portal, uploads to the bid folder, then uploads to the AI tool. The AI tool triggers a series of activities via an AI agent to scrape the relevant information from the documentation and then pre-populate a proforma. That documentation will include the procurement timetable, requirements, compliance matrix, etc. I do not expect, in terms of effort on the bid manager, that being more than two to three hours of actual time. Of the 10 man-days currently allocated, I would consider that to be in the 90%."

---

#### Skill 2: Evaluation Criteria Analysis (`evaluation-criteria`)

**Command:** `/pwin:evaluation-analysis`
**Trigger:** Human-invoked. Typically run immediately after ITT extraction, or standalone if evaluation documents are updated.
**Depends on:** Skill 1 (ITT extraction) must have run first — needs ResponseSections and EvaluationFramework.

**What it does:**

Deep analysis of the evaluation framework beyond the extraction done by Skill 1. This skill reasons over the extracted data to produce strategic insight about the scoring landscape.

**Process:**

```
Step 1: Marks concentration analysis (SAL-05.2.1)
  — Read all ResponseSections via get_response_sections()
  — Rank sections by marks value (evaluationMaxScore × evaluationWeightPct)
  — Identify the top 20% of sections that drive the majority of marks
  — Categorise: high-value (>10% of total marks), medium (5-10%), low (<5%)
  — Flag hurdle sections that override return-on-effort calculations

Step 2: Scoring guidance extraction (SAL-05.1.3)
  — Where client marking scheme exists (from Skill 1):
    - For each grade band, extract what differentiates it from the band below
    - Identify the phrases and evidence types that distinguish top scores
    - Map grade band descriptors to quality dimensions (answers question, follows structure, credentials, win themes)
  — Where no marking scheme: flag that scoring strategy must be derived from evaluation criteria text alone

Step 3: Section-to-criteria mapping (SAL-05.1.2)
  — Cross-reference evaluation criteria with response sections
  — Calculate marks-per-page ratio per section
  — Identify sections where evaluation criteria text suggests a different weighting than the official weight

Step 4: Win theme alignment matrix (SAL-05.2.4)
  — Read win themes via get_win_themes()
  — Map each win theme to the sections where it can be landed
  — Produce integration matrix: theme × section, showing where themes generate marks
  — Flag high-value sections with no theme alignment (strategic gap)
```

**Output template:**

```
Evaluation Landscape Analysis
=============================
Total marks available:      [total]
Quality marks:              [count] across [sections] sections
Price marks:                [count]
Social value marks:         [count]

MARKS CONCENTRATION
  Top 5 sections:           [list with marks, weight, and hurdle status]
  These sections represent: [x]% of available quality marks
  Recommendation:           [specific effort allocation guidance]

HURDLE SECTIONS
  [count] sections with hurdle requirements
  [list with section ref, hurdle score, grade band descriptor for hurdle]
  Risk: Failure in any hurdle section = disqualification regardless of total score

SCORING DIFFERENTIATION
  To achieve top band in high-value sections, responses must demonstrate:
  [section-by-section guidance derived from grade descriptors]

WIN THEME ALIGNMENT
  [matrix: theme × top sections]
  Strategic gaps: [high-value sections with no theme coverage]
```

**Quality criteria:**
- Marks must be validated against the extracted EvaluationFramework (weights sum check).
- Every hurdle section must be identified and flagged prominently.
- Win theme gaps must reference specific sections and marks at risk.

---

#### Skill 3: Contract Analysis (`contract-analysis`)

**Command:** `/pwin:contract-review`
**Trigger:** Human-invoked. Bid manager uploads contract documents (may be part of initial ITT pack or separate).

**What it does:**

Reads contract documents (T&Cs, schedules, annexes) and extracts structured analysis of obligations, liabilities, and risk areas. Supports LEG-01 activities.

**Process:**

```
Step 1: Contract document ingestion
  — Read all contract volumes (T&Cs, schedules, annexes)
  — If not already registered by Skill 1, write ITTDocument records

Step 2: Obligation and liability extraction (LEG-01.1.1)
  — Extract every obligation imposed on the supplier
  — Categorise: performance obligation, reporting obligation, financial obligation,
    compliance obligation, personnel obligation, IP obligation
  — For each: clause reference, obligation text, consequence of breach, liability cap (if stated)
  — Flag unlimited liability clauses

Step 3: Red line and risk identification (LEG-01.1.2)
  — Identify terms that create unacceptable exposure:
    - Unlimited liability
    - Uncapped liquidated damages
    - Unilateral termination rights
    - IP assignment (vs licence)
    - Non-standard indemnity provisions
    - Restrictive non-compete clauses
    - Onerous TUPE obligations beyond statutory
    - Parent company guarantee requirements
    - Security requirements beyond standard
  — Classify: red line (cannot accept), amber (needs amendment), green (standard)
  — For red/amber items: source clause, risk description, recommended position

Step 4: Contract markup support (LEG-01.2.1)
  — For each red/amber item, draft:
    - Proposed amendment text
    - Rationale for the amendment (why it matters commercially)
    - Fallback position if amendment is rejected
  — Output as structured table for legal review
```

**Output template:**

```
Contract Risk Analysis
======================
Documents reviewed:         [count]
Total clauses analysed:     [count]
Obligations identified:     [count] across [categories] categories

RED LINES ([count])
  [clause ref] — [risk summary] — [clause extract]
  Recommended position: [amendment text]
  Fallback: [alternative position]
  ...

AMBER — NEEDS AMENDMENT ([count])
  [clause ref] — [risk summary] — [clause extract]
  Recommended amendment: [text]
  ...

GREEN — STANDARD ([count] — no action required)

LIABILITY SUMMARY
  Cap: [capped/uncapped] at [value if stated]
  Indemnities: [count] indemnity provisions, [count] unlimited
  LDs: [present/absent], [capped/uncapped]
  Termination: [mutual/unilateral], notice period: [period]

TUPE IMPLICATIONS
  [TUPE applicable/not applicable]
  [Key obligations and timeline requirements]

Items requiring legal review: [count]
  [list of clauses where AI extraction confidence is low]
```

**Quality criteria:**
- Every red line must cite the specific clause reference.
- Amendment text must be legally coherent (not creative drafting — the legal lead refines).
- TUPE implications must be extracted accurately — these feed into the solution design (Agent 6).
- Confidence assessment: clauses where the AI is uncertain about interpretation must be flagged.

---

#### Skill 4: Compliance Matrix Generation (`compliance-matrix`)

**Command:** `/pwin:compliance-matrix`
**Trigger:** Human-invoked. Run after ITT extraction and requirements analysis are complete.
**Depends on:** Skill 1 (ITT extraction) — needs ResponseSections.

**What it does:**

Maps every mandatory and scored requirement from the ITT to the response section that addresses it. Creates the compliance matrix as a living data structure in the bid execution app. Supports PRD-01 activities.

**Process:**

```
Step 1: Requirement identification
  — Read all ResponseSections via get_response_sections()
  — For each section, extract implicit and explicit requirements from:
    - questionText (what the client is asking)
    - evaluationCriteria (what evaluators will look for)
    - Any mandatory/pass-fail flags
  — Classify each requirement:
    - mandatory (must comply or disqualified)
    - scored (marks allocated for compliance quality)
    - pass_fail (binary yes/no)
    - evidential (evidence required, e.g., case studies, certifications)
    - contractual (compliance with contract terms)

Step 2: Compliance position mapping
  — For each requirement, assess initial compliance position:
    - compliant (can meet requirement)
    - partially_compliant (can meet with caveats or clarification)
    - non_compliant (cannot meet — requires clarification, amendment, or risk acceptance)
    - not_assessed (insufficient information — needs solution workstream input)
  — Flag mandatory requirements with non_compliant status as disqualification risks

Step 3: Coverage mapping (PRD-01.1.1)
  — Map every requirement to the ResponseSection(s) that must address it
  — Identify requirements addressed across multiple sections
  — Identify requirements with no coverage (gap)

Step 4: Write compliance data
  — Write ComplianceRequirement records or update coverage status
  — Generate compliance matrix summary
```

**Output template:**

```
Compliance Matrix
=================
Total requirements identified:  [count]
  Mandatory:                   [count] — [compliant/partial/non-compliant/not assessed]
  Scored:                      [count]
  Pass/fail:                   [count]
  Evidential:                  [count]

DISQUALIFICATION RISKS ([count])
  [req ref] — [requirement text] — Status: [non_compliant/not_assessed]
  Covered by: [section ref or NONE]
  Action required: [specific action]

COVERAGE GAPS ([count])
  [requirements with no ResponseSection coverage]

CROSS-REFERENCE MATRIX
  [requirement × response section mapping table]

Compliance confidence: [HIGH/MEDIUM/LOW]
Items requiring workstream input: [count]
```

---

#### Skill 5: Procurement Documentation Ingestion (`procurement-ingestion`)

**Command:** `/pwin:itt-briefing`
**Trigger:** Human-invoked. Typically the first thing run when an ITT is received.

**What it does:**

Produces a narrative strategic briefing from the ITT pack — a human-readable report for the bid team that contextualises the opportunity before the detailed extraction work begins. This is a rapid-turnaround skill that produces a deliverable document, not structured data.

This is distinct from Skill 1 (which writes structured data to the app). This skill produces a report that the bid team reads in the first hours after ITT receipt.

**Process:**

```
Step 1: Rapid document scan
  — Read all uploaded documents at a summary level
  — Identify document types, volumes, total page count

Step 2: Strategic briefing generation
  — Evaluation methodology summary: how will this be scored?
  — Key risks: unusual terms, tight timelines, onerous requirements
  — Competitive dynamics: what does the ITT structure tell us about the client's expectations?
  — Effort allocation: based on marks concentration, where should the team invest?
  — Procurement timeline: key dates, clarification windows, submission deadline
  — TUPE implications: high-level assessment
  — Security requirements: clearance tier and implications for team composition
  — Clarification priorities: what must we ask in the first round?

Step 3: Report generation
  — Write narrative report via generate_report_output()
  — Report follows a standard proforma template (see templates/itt-briefing/)
```

**Output template:**

```
ITT STRATEGIC BRIEFING
======================
Opportunity: [title]
Client: [name]
Submission deadline: [date] ([working days] working days from today)
Contract value: [TCV] over [duration]

EVALUATION METHODOLOGY
  [summary of how this will be scored]

MARKS LANDSCAPE
  [quick summary of where the marks are]

KEY RISKS
  [top 3-5 risks from the documentation]

COMPETITIVE POSITIONING SIGNALS
  [what the ITT structure tells us about client expectations]

CLARIFICATION PRIORITIES
  [top 5 questions we should ask immediately]

TEAM IMPLICATIONS
  TUPE: [summary]
  Security: [clearance requirements]
  Timeline: [critical path observations]

RECOMMENDATION
  [pursue/proceed with caution/flag for go/no-go review]
```

**Quality criteria:**
- Must be producible within minutes of document upload — not a deep analysis.
- Must flag the single most important risk prominently.
- Clarification priorities must be specific and actionable, not generic.
- The recommendation must be honest — if the ITT contains dealbreakers, say so.

**Practitioner design note:**
> "The completed synthesis of all the previous activities into the customer intelligence report is a single document that's synthesised and produced by the AI within hours of the ITT documentation being released."

---

### 3.2 Insight Skills

---

#### Skill 6: Clarification Impact Propagation (`clarification-impact`) — UC13

**Command:** `/pwin:clarification-impact`
**Trigger:** On-demand (V1). Scheduled on SAL-08 completion (V2).
**Depends on:** Skill 1 (ITT extraction) — needs ResponseSections to cross-reference against.
**V2 dependency:** Full implementation requires ClarificationItem entity (V2). V1 operates on uploaded clarification documents with manual cross-referencing.

**What it does:**

Reads published clarification Q&As and cross-references against the ResponseSection register. Identifies every section, requirement, and assumption affected by the clarification responses. Generates targeted actions for each affected workstream lead.

**Full specification:** `ai_use_cases_reference.html`, UC13.

**Process (V1 — uploaded clarification document):**

```
Step 1: Ingest clarification document
  — Read uploaded clarification Q&A log (PDF/Excel)
  — Extract each Q&A pair: question number, question text, answer text, date published

Step 2: Impact cross-referencing
  — For each answer, cross-reference against:
    - ResponseSections: does this answer change questionText, evaluationCriteria,
      wordLimit, hurdleScore, or marks allocation?
    - ComplianceRequirements: does this answer change compliance position?
    - RiskAssumptions: does this answer invalidate any stated assumption?
  — Classify impact: material (changes response approach), minor (cosmetic/clarification only),
    none (not relevant to our response)

Step 3: Write impact data
  — flag_response_section_amended() for affected sections
  — Create new RiskAssumption records for invalidated assumptions
  — create_standup_action() per affected workstream lead with specific instruction

Step 4: Competitor intelligence extraction
  — Identify questions not submitted by the bidding firm
  — Assess what each competitor question reveals about their approach
  — Write competitor intelligence to SAL-03 activity insight
```

**Output:** AIInsight records written to app (see UC13 spec for schema). Plus summary report of impact assessment.

---

#### Skill 7: ITT Amendment Detection (`amendment-detection`) — UC14

**Command:** `/pwin:amendment-review`
**Trigger:** On-demand (V1). Triggered by new ITTDocument version (V2).
**Depends on:** Skill 1 (ITT extraction) — needs existing ResponseSections and EvaluationFramework to compare against.

**What it does:**

When the client issues an amended ITT document, this skill compares the new version against the extracted data from the original, identifies all changes, assesses cumulative impact, and determines whether the win strategy needs revisiting.

**Full specification:** `ai_use_cases_reference.html`, UC14.

**Process:**

```
Step 1: Version comparison
  — Read the amended document
  — Compare against existing ResponseSections and EvaluationFramework
  — Identify every field that has changed: questionText, evaluationCriteria,
    evaluationMaxScore, hurdleScore, wordLimit, evaluationWeightPct

Step 2: Cumulative impact assessment
  — Has the overall evaluation basis materially changed?
  — Has the total marks allocation shifted between categories?
  — Do multiple amendments cluster in one evaluation category? (strategic signal)
  — Does any amendment make a previously compliant requirement non-compliant?

Step 3: Write impact data
  — flag_response_section_amended() for affected sections
  — create_standup_action() for win strategy review if cumulative impact is material
  — Register amended document via create_itt_document() with version increment

Step 4: Win strategy trigger
  — If cumulative impact exceeds threshold: generate StandupAction for Bid Manager
    and Pursuit Director to review win strategy assumptions
```

**Output:** AIInsight records + amendment summary. See UC14 spec for schema.

---

## 4. Agent Build Sequence

| Order | Skill | Type | Dependencies | Validates |
|---|---|---|---|---|
| 1 | ITT Extraction | Productivity | MCP server + write tools | Full ingestion pipeline: upload → extract → write to app |
| 2 | Procurement Ingestion (ITT Briefing) | Productivity | Document reader | Rapid narrative output — can build before MCP if needed |
| 3 | Evaluation Criteria Analysis | Productivity | Skill 1 output + MCP read tools | Cross-entity reasoning over extracted data |
| 4 | Compliance Matrix | Productivity | Skill 1 output + MCP read/write tools | ComplianceRequirement creation and coverage mapping |
| 5 | Contract Analysis | Productivity | Document reader + MCP write tools | Legal document extraction pattern |
| 6 | Clarification Impact | Insight | Skill 1 output + MCP read/write tools | Amendment/clarification cross-referencing pattern |
| 7 | Amendment Detection | Insight | Skill 1 output + MCP read/write tools | Version comparison pattern |

---

## 5. Metrics

| Metric | Value |
|---|---|
| Total methodology tasks served | ~22 |
| High-rated tasks | 17 |
| Average effort reduction | 63% |
| Implementation phase | Phase 3 (first agent to build after MCP server) |
| Methodology activities covered | SAL-01.1.1, SAL-05.1.1-3, SAL-05.2.1-4, SAL-07.2.1, SOL-01.1.1-3, SOL-01.2.1-3, LEG-01.1.1-2, LEG-01.2.1, PRD-01.1.1-2 |
| Insight skills | UC13 (Clarification Impact), UC14 (Amendment Detection) |
| Estimated person-days saved per bid | ~25-30 (from extraction and analysis tasks alone) |

---

## 6. Relationship to Other Agents

**Agent 1 outputs feed directly into:**

| Downstream Agent | What it consumes from Agent 1 |
|---|---|
| Agent 2 (Market Intelligence) | ResponseSections for competitive analysis context |
| Agent 3 (Strategy & Scoring) | EvaluationFramework, ResponseSections, marks concentration — the foundation for all scoring strategy |
| Agent 4 (Commercial & Financial) | Contract obligations, liability structure, TUPE implications |
| Agent 5 (Content Drafting) | ResponseSections (the questions to answer), evaluation criteria (what evaluators look for), compliance requirements (what must be addressed) |
| Agent 6 (Solution & Delivery) | Requirements (SOL-01 extraction), TUPE data, security requirements, contract obligations |

**Agent 1 never depends on other agents.** It reads only from uploaded documents and existing bid data. This is by design — it's the foundation layer.

---

*Agent 1: Document Intelligence | v1.0 | April 2026 | PWIN Architect*
*7 skills (5 productivity, 2 insight) | ~22 methodology tasks | 63% avg effort reduction*
