# BidEquity Verdict — Product Requirements Document

> **See also:** [[pwin-bid-execution/docs/mcp_server_architecture|MCP Server Architecture]] | [[pwin-competitive-intel/README|Competitive Intel DB]] | [[HOME|Map of Content]]

**Version:** 2.0
**Date:** 3 April 2026
**Author:** Paul Fenton
**Status:** Draft
**Classification:** Confidential

---

## 1. Executive Summary

BidEquity Verdict is a forensic, platform-enabled post-loss review that independently assesses why an organisation lost a strategic bid and what needs to change. It examines the entire pursuit lifecycle — from early intelligence gathering and team mobilisation through solution development, governance, proposal production, and commercial positioning — against a structured evaluation framework derived from BidEquity's pursuit methodology.

Verdict does not ask "was the proposal well written?" It asks "was the pursuit well run?" — and traces the evidence trail across every activity that determines outcome. Where evidence is absent, that absence is itself a finding.

Verdict serves a dual strategic purpose: it is the lowest-commitment entry point into the BidEquity ecosystem for new clients, and a portfolio learning tool for existing Core and Command clients. Its fixed-fee, transactional commercial model is deliberately distinct from the outcome-aligned pricing of Core and Command — a lost bid has already happened, so the value is in what the client learns and applies next time.

---

## 2. Problem Statement

When an organisation loses a strategic bid — particularly one worth £50m or more — the internal post-mortem is almost always compromised. The team that wrote the proposal reviews the proposal. The strategy that failed is assessed by the people who designed it. Authority feedback is filtered through the same assumptions and biases that shaped the losing submission.

The result is a debrief that confirms what the team already believes, misses the structural failures that determined the outcome, and produces no actionable change.

The deeper problem is that most organisations do not know what a proper post-loss review should examine. They focus on the written responses — were the answers good enough? — and ignore the upstream decisions that determined whether those answers could ever have been good enough. They never ask whether the competitive intelligence was gathered, whether the solution was properly constructed, whether the team was mobilised early enough, whether governance caught the problems that mattered, or whether the commercial model was defensible. These are the decisions that win and lose bids. The proposal is just the artefact.

The alternatives are no better. Internal reviews are free, fast, and almost always useless for driving structural change. Consultancy retrospectives are expensive, subjective, and limited by individual expertise — no platform, no structured methodology, no evaluation framework that covers the full pursuit lifecycle.

There is no product in the market that forensically evaluates the entire pursuit operation — from intelligence to submission — against a structured framework, with independent scoring and an evidence-based assessment of what was done, what was missing, and what needs to change. Verdict fills that gap.

---

## 3. Product Definition

### 3.1 What Verdict Is

A forensic post-loss review that independently evaluates the entire pursuit lifecycle — not just the written submission, but every upstream activity that determined whether the submission could succeed. The client provides documentation and evidence of their pursuit process; the platform evaluates it against BidEquity's structured methodology; BidEquity delivers findings through a consultative debrief.

Verdict asks two questions at every stage of the pursuit lifecycle: "Was this done?" and "Where is the evidence?" The combination of these two questions — activity coverage and evidence quality — is what separates Verdict from any internal review or consultancy retrospective.

### 3.2 What Verdict Is Not

Verdict is not a bid-writing critique. It does not assess prose quality in isolation. It is not a compliance check. It is a strategic and structural assessment of why the pursuit failed at the level of intelligence, strategy, mobilisation, solution, governance, production, and commercials — the full chain of decisions upstream of the words on the page. The written submission is one input. The pursuit operation that produced it is the subject of the review.

### 3.3 Product Naming Convention

The BidEquity product family uses single-word nouns that convey function and authority:

- **Core** — the foundational intelligence layer
- **Command** — operational control of the bid office
- **Verdict** — a definitive, independent judgement on a lost pursuit

"Verdict" carries connotations of authority, independence, and finality. It signals that the client receives a forensic assessment, not a polite summary.

---

## 4. Target Users

### 4.1 Primary Buyer: BD / Capture Leads

These buyers want to understand what went wrong tactically — which sections scored poorly, where the strategy was misaligned, what the competition did differently. They commission Verdict to improve their own performance and to build the case internally for investment in pursuit capability.

**Trigger:** A significant loss on a pursuit they led or were closely involved in.
**Value:** Specific, evidence-based findings they can act on immediately for the next pursuit.

### 4.2 Secondary Buyer: Senior Leadership (CCO, COO, CFO)

These buyers want an independent assessment they can trust — one not produced by the team that lost. They commission Verdict to inform investment decisions: whether to rebid, whether to restructure the pursuit function, whether the loss was strategic (wrong market) or operational (poor execution).

**Trigger:** A board-level loss, a pattern of losses, or a decision about whether to invest in pursuit capability.
**Value:** An independent, defensible assessment that separates strategic from operational failure.

### 4.3 Target Organisation Profile

- UK-based strategic suppliers to government (Defence, Emergency Services, Justice, central government)
- Annual bid portfolio of £100m+ in contract value
- Organisations that lose strategic pursuits worth £50m+ and currently rely on internal post-mortems
- Organisations considering investment in pursuit capability but lacking independent evidence of where the problems are

---

## 5. Verdict Evaluation Framework

This is the core of the product. Verdict evaluates the pursuit across eight domains, each containing specific assessment criteria. For every criterion, Verdict asks three questions: Was this activity performed? What evidence exists? How effective was the output?

The framework is derived from BidEquity's pursuit methodology — the same structured activities that govern live pursuit delivery in Core and Command. Applying it retrospectively to a lost bid surfaces exactly where the pursuit operation broke down.

---

### 5.1 Pursuit Intelligence and Competitive Positioning

This domain assesses whether the organisation understood the competitive landscape, the client, and the opportunity before committing to pursue — and whether that intelligence was translated into a differentiated win strategy.

**Assessment criteria:**

**Competitive landscape analysis.** Was a structured competitive analysis conducted? Were competitors identified and profiled? Were competitor strengths, weaknesses, and likely strategies mapped? Was this captured in a usable format — battle cards, competitive positioning matrix, or equivalent? Or was the competitive assessment informal, assumed, or absent?

**Client intelligence.** Was a comprehensive intelligence report produced on the contracting authority? Does it cover the organisation's strategic priorities, operational challenges, political drivers, budget pressures, and decision-making context? Was this intelligence gathered from multiple sources (published strategies, prior engagement, market intelligence, stakeholder conversations), or was it limited to what was in the ITT?

**Buyer personas and values mapping.** Were buyer personas developed for the key evaluators and decision-makers? Was a buyer values matrix produced — mapping what each evaluator cares about to specific elements of the proposed solution? Was the solution shaped to address those values, or was the response written to generic requirements without understanding who would read and score it?

**Decision-making unit (DMU).** Was the full decision-making unit identified — not just the named evaluation panel, but the influencers, gatekeepers, and approvers behind the formal process? Were roles, priorities, and concerns mapped for each individual?

**Stakeholder engagement.** Was there evidence of pre-tender engagement with the client? Were relationships built with relevant stakeholders before the procurement launched? Was the organisation shaping the opportunity or merely responding to it? What was the quality of access — senior sponsor, operational leads, technical authority, end users? Where was engagement attempted but unsuccessful, and why?

**Intelligence-to-strategy translation.** Was the intelligence gathered actually used? Is there a traceable link from competitive analysis and client intelligence through to win strategy, discriminator selection, and proposal messaging — or did the intelligence sit in a document that the bid team never read?

**Evidence required:** Competitive analysis documents, battle cards, client intelligence reports, buyer persona profiles, buyer values matrix, stakeholder engagement logs, pre-tender meeting notes, win strategy document with traceability to intelligence sources.

---

### 5.2 Win Strategy and Positioning

This domain assesses whether the organisation had a coherent, differentiated win strategy — and whether that strategy was grounded in evidence, aligned to evaluation criteria, and executed through the submission.

**Assessment criteria:**

**Win strategy definition.** Was there a documented win strategy? When was it produced — early enough to shape the solution and the response, or retrospectively after the writing had started? Was it reviewed and approved at a formal gate?

**Discriminator identification.** Were specific discriminators identified — genuine points of competitive advantage, not generic claims? Were they grounded in evidence (past performance, technical capability, innovation, key personnel) or were they aspirational? Were they mapped against evaluation criteria weighting to ensure effort was concentrated where it would score?

**Win themes and key messages.** Were win themes defined and documented? Were they consistent across the full submission — flowing through the executive summary, technical response, management approach, and commercial narrative in a coherent thread? Or did they appear in the executive summary and then vanish?

**Evaluation criteria alignment.** Was the win strategy explicitly mapped to the published evaluation criteria and scoring methodology? Was effort allocated in proportion to criteria weighting? Were high-weighted areas prioritised for the strongest discriminators and evidence, or was effort spread evenly regardless of weight?

**Evidence required:** Win strategy document, discriminator register, win theme matrix, evaluation criteria mapping with effort allocation, gate review records showing strategy approval.

---

### 5.3 Team Mobilisation and Organisation

This domain assesses whether the right team was assembled, at the right time, with the right structure and the right authority to deliver a winning submission.

**Assessment criteria:**

**Mobilisation timing.** When was the bid team mobilised relative to the procurement timeline? Was there a pre-tender capture phase, or did mobilisation begin only when the ITT was issued? How much of the pursuit timeline was consumed by team assembly and orientation rather than productive work?

**Team structure and roles.** Was there a defined organisational structure for the pursuit? Were roles and responsibilities clearly allocated — bid director, capture lead, solution architect, commercial lead, volume leads, bid manager, production team? Were there gaps — key roles unfilled, or individuals carrying multiple responsibilities that created capacity constraints?

**Seniority and authority.** Did the bid team have sufficient seniority and decision-making authority? Was the bid director empowered to make strategic and commercial decisions, or did every decision require escalation to a steering group that met fortnightly? Were subject matter experts available when needed, or were they borrowed from delivery and constantly pulled away?

**Bid plan.** Was a formal bid plan produced? Did it cover the full pursuit timeline with milestones, dependencies, review gates, and resource allocation? Was it maintained and updated, or was it produced at the start and never revisited? Were milestones linked to the authority's procurement timetable, including clarification windows, evaluation panel schedules, and submission deadlines?

**Resource adequacy.** Was the team adequately resourced relative to the complexity and scale of the pursuit? Were writing resources, solution resources, and commercial resources sufficient — or was the team understaffed from the outset, leading to compressed timelines, missed reviews, and late-stage scrambles?

**Evidence required:** Bid team organogram, RACI matrix, bid plan with milestones and resource allocation, mobilisation timeline, evidence of pre-tender capture activity.

---

### 5.4 Solution Development

This domain assesses whether the proposed solution was rigorously constructed — not just described, but properly engineered through a structured process that considered the incumbent service, the target operating model, the transition, and the risks.

**Assessment criteria:**

**Incumbent service understanding.** Was the existing service properly analysed? Was there a baseline assessment of the current operating model — technology landscape, key processes, staffing model, performance levels, known pain points? Or was the proposed solution built in a vacuum, disconnected from the reality the client is currently living with?

**Operating model design.** Was a coherent target operating model developed? Does it articulate the technology architecture, the key business processes, the people model (roles, grades, locations), and the management and governance framework? Was this developed through structured solution workshops, or was it assembled by individuals working in isolation?

**Solution workshops.** Were formal solution workshops conducted? Who participated — was it limited to the bid team, or were delivery specialists, technical architects, and operational SMEs involved? Were workshops structured around specific evaluation criteria and requirements, or were they open-ended brainstorming sessions? Were outputs documented and traceable to the written response?

**Transition and mobilisation planning.** How early was the delivery director or transition lead engaged? Was a credible transition plan developed — with phased activities, resource profiles, risk mitigations, and dependencies on the incumbent and the authority? Or was transition treated as a compliance section that received minimal attention and generic content?

**Risk assessment.** Was a structured risk assessment conducted for the proposed solution? Were risks identified, assessed, and mitigated — not just listed? Were delivery risks, commercial risks, and transition risks considered? Was TUPE analysis conducted where relevant — with a realistic assessment of workforce transfer implications, cost modelling, and engagement strategy?

**TUPE and workforce considerations.** Where TUPE applies, was it addressed substantively? Was there evidence of due diligence on the transferring workforce — grades, terms, pensions, union engagement? Was the commercial model realistic about TUPE costs, or was it based on assumptions that would not survive scrutiny?

**Solution-to-response traceability.** Was the solution documented in a way that the proposal team could translate it into scored responses? Was there a solution pack or equivalent that the writers worked from — or did each volume lead interpret the solution independently, producing inconsistency across the submission?

**Evidence required:** Incumbent service assessment, target operating model documentation, solution workshop outputs and attendee lists, transition plan, risk register with mitigations, TUPE analysis, solution pack or design authority outputs.

---

### 5.5 Governance and Review Process

This domain assesses whether the pursuit had effective governance — formal review gates, decision-making discipline, and evidence that reviews actually changed the quality of the output.

**Assessment criteria:**

**Governance framework.** Was there a defined governance process for the pursuit? Were review gates established — qualification gate, strategy gate, solution gate, draft review, final review, submission readiness? Were these scheduled in advance and linked to the bid plan milestones?

**Review cadence and attendance.** Were reviews conducted on schedule? Who attended — was it the right mix of senior leadership, subject matter experts, and independent reviewers, or was it the bid team reviewing its own work? Were reviewers given adequate time and materials to prepare, or were reviews conducted on the day with no prior reading?

**Review quality and impact.** What was the quality of feedback from reviews? Was it specific, actionable, and prioritised — or generic ("needs more detail", "strengthen the evidence")? More importantly, was review feedback acted on? Is there evidence that the submission changed as a result of governance — or did reviews happen but make no difference to the final output?

**Actions and decisions.** Were actions from review gates formally captured, assigned, and tracked to closure? Were decisions documented — particularly strategic and commercial decisions that shaped the direction of the submission? Is there an audit trail that shows how the submission evolved through governance, or does the trail go cold after the first review?

**Escalation and issue resolution.** When problems were identified — scope gaps, resource shortfalls, commercial concerns, compliance risks — was there a functioning escalation process? Were issues resolved in time to affect the submission, or were they raised, noted, and carried forward unresolved into the final document?

**Evidence required:** Governance framework document, review gate schedule, review panel membership, review feedback and scores, action logs with closure evidence, decision logs, escalation records.

---

### 5.6 Proposal Production and Quality

This domain assesses the quality of the written submission — not as a prose exercise, but as the final expression of the pursuit strategy. It evaluates whether the upstream work (intelligence, strategy, solution, governance) was effectively translated into responses that score.

**Assessment criteria:**

**Storyboarding.** Were storyboards produced before writing began? Were they reviewed and signed off — confirming the argument structure, key messages, evidence, and discriminators for each response before prose was committed? Or did writers go straight to draft, producing text that had to be restructured later?

**Tone of voice and consistency.** Is the submission written in a single, consistent voice — or does it read as though it was produced by multiple writers with different styles, levels of seniority, and interpretations of the strategy? Are win themes and key messages threaded through every volume in a coherent manner, or do they appear only where the individual writer remembered to include them?

**Win theme execution.** Do the win themes and discriminators identified in the strategy actually appear in the scored responses? Are they evidenced with specific, quantified proof points — or are they stated as claims without substantiation? Do they flow through the executive summary, technical response, management approach, and commercial narrative as a coherent thread?

**Question compliance.** Does each response answer the specific question asked — in the structure the authority requested, within the stated word or page count, addressing every sub-element of the evaluation criteria? Were responses structured against the scoring matrix to make it easy for evaluators to award marks — or did the team write what they wanted to say rather than what was asked?

**Evidence quality.** Are case studies and examples specific, relevant, and quantified? Do they demonstrate comparable scale, sector, and complexity? Are they attributed to named individuals who are proposed on the contract — or are they generic organisational credentials that could apply to any bid?

**Language and readability.** Is the English language usage clear, precise, and professional? Is the writing concise and accessible to the evaluator audience, or is it dense, jargon-heavy, or padded? Are graphics and visuals used effectively to reinforce key points, or are they decorative?

**Independent scoring.** Verdict independently scores the submission against the published evaluation criteria — matching the authority's scoring methodology, scale, and descriptive bands. This produces a parallel score for each evaluated section, which is compared against the authority's feedback (where available) and the client's own internal assessment. Variance analysis identifies where the client's perception of their submission quality diverged from how it actually scored — and why.

**Evidence required:** Storyboards with sign-off records, style guide or tone of voice guidance, win theme compliance matrix, word/page count tracking, response structure mapped to evaluation criteria, case study register, independent scoring output versus authority scores.

---

### 5.7 Commercial and Pricing

This domain assesses whether the commercial proposition was competitive, defensible, and aligned with the overall win strategy — and whether it was constructed through a rigorous process rather than assembled at the last minute.

**Assessment criteria:**

**Pricing strategy.** Was there a documented pricing strategy that preceded the financial model? Was it aligned with the win strategy — for example, if the strategy was to compete on value, was the pricing positioned to demonstrate investment and capability rather than undercutting? Was the pricing strategy reviewed and approved at a formal gate?

**Commercial model coherence.** Does the pricing model reflect the proposed solution — or is there a disconnect between what was proposed operationally and what was priced commercially? Were all solution elements costed, including transition, mobilisation, TUPE, and ongoing service delivery? Were assumptions documented and defensible?

**Risk allocation.** How were commercial risks allocated — and was this allocation deliberate? Were risk premiums built in where appropriate, or was risk transferred to the client or absorbed without acknowledgement? Was the risk position consistent with the narrative in the commercial response?

**Competitive positioning.** Where benchmark data or market intelligence was available, was the pricing positioned competitively? Was there evidence that the organisation understood the likely price range for the contract — or was pricing produced in isolation without reference to the competitive context?

**Pricing-narrative alignment.** Does the pricing submission tell the same story as the technical and management submissions? If the technical response promises investment, innovation, and senior personnel, does the pricing reflect those commitments — or is there a visible gap between what was promised and what was priced?

**Evidence required:** Pricing strategy document, commercial model with assumptions, risk allocation matrix, competitive pricing benchmarks (where available), pricing review gate records, reconciliation between solution scope and financial model.

---

### 5.8 Post-Submission and Presentation

This domain assesses what happened after the written submission was uploaded — the presentation, BAFO, and contract negotiation stages that can determine the outcome even when the written submission scores well. Not all procurements include these stages, but where they occurred, the quality of the organisation's post-submission response is a material finding.

**Assessment criteria:**

**Presentation preparation.** If the procurement included a presentation or interview stage, was there a structured preparation process? Was the presentation designed as a strategic narrative that reinforced the win themes and addressed known evaluator concerns — or was it a last-minute assembly of slides from the written submission? Were speakers selected for credibility and seniority appropriate to the audience, or were they the people who happened to be available?

**Presentation rehearsal and coaching.** Were rehearsals conducted? Were they structured — with a simulated evaluation panel, timed runs, and challenging questions — or were they informal read-throughs? Were speakers coached on delivery, messaging discipline, and handling hostile questions? Was feedback from rehearsals acted on and incorporated into the final presentation?

**Evaluator question anticipation.** Were likely evaluator questions anticipated and prepared for? Were answers structured, evidence-based, and aligned with the win strategy — or were speakers left to improvise? Did the team prepare for the difficult questions (pricing justification, delivery risk, incumbent transition, key person availability) as well as the comfortable ones?

**BAFO response (where applicable).** If a Best and Final Offer stage occurred, was the BAFO response strategic — genuinely improving the offer based on what was learned during the evaluation process — or was it a mechanical price reduction with no strategic rationale? Was the BAFO decision governed through a formal gate, or was it made under time pressure without proper commercial review?

**Contract negotiation readiness.** If negotiations occurred before the award decision was finalised, was the organisation prepared? Were negotiation positions documented in advance? Were red lines, trade-offs, and fallback positions agreed at a governance level — or was the negotiation team improvising in the room?

**Post-submission intelligence.** After submission, did the organisation continue to gather intelligence — through legitimate channels — about the evaluation process, competitor positioning, or client thinking? Was this intelligence used to shape the presentation or BAFO response, or did the team go dark after submission?

**Evidence required:** Presentation deck and speaker notes, rehearsal schedule and feedback records, anticipated questions and prepared answers, BAFO decision records with commercial rationale, contract negotiation brief with approved positions, post-submission engagement log.

---

### 5.9 Evaluation Framework Summary

The eight domains above are assessed in a structured, weighted format. Each domain receives an overall maturity rating and a set of specific findings. The weighting reflects the relative impact each domain has on pursuit outcome:

| Domain | Weight | Rationale |
|--------|--------|-----------|
| Pursuit Intelligence and Competitive Positioning | 15% | Upstream intelligence determines whether the win strategy is grounded in reality |
| Win Strategy and Positioning | 20% | The strategy is the highest-leverage factor — a flawed strategy cannot be rescued by good writing |
| Team Mobilisation and Organisation | 10% | Necessary condition — inadequate mobilisation constrains everything downstream |
| Solution Development | 15% | The quality of the solution determines the ceiling for the technical and commercial response |
| Governance and Review Process | 10% | Governance is the mechanism by which problems are caught and quality is assured |
| Proposal Production and Quality | 15% | The scored submission — the artefact that directly determines the evaluation outcome |
| Commercial and Pricing | 10% | Pricing is often a pass/fail filter — competitive positioning matters as much as technical quality |
| Post-Submission and Presentation | 5% | Where applicable — presentation, BAFO, and negotiation can determine outcome after a strong written submission |

**Note:** Domain 5.8 is conditionally assessed. Not all procurements include a presentation, BAFO, or negotiation stage. Where these stages did not occur, the domain is excluded from the weighted calculation and the remaining domain weights are normalised to 100%. The weight of 5% reflects that the written submission carries more evaluative weight than the presentation in most public sector procurements, but a poor presentation can lose a bid that was otherwise winning.

Each domain is scored on a five-point maturity scale:

| Rating | Description |
|--------|-------------|
| **Absent** | No evidence of the activity being performed. A fundamental gap. |
| **Informal** | Activity performed but ad hoc, undocumented, or not structured. Limited evidence. |
| **Defined** | Activity performed with some structure and documentation, but inconsistently applied or not quality-assured. |
| **Managed** | Activity performed systematically with clear evidence, governance, and quality assurance. Meets expected standard for a pursuit of this complexity. |
| **Optimised** | Activity performed to a high standard with evidence of continuous improvement, cross-functional integration, and measurable impact on pursuit quality. |

The weighted domain scores produce an overall Pursuit Maturity Score — a single metric that benchmarks the organisation's pursuit operation against what would be expected for a bid of this scale and complexity.

---

## 6. Platform Requirements

### 6.1 Inputs

The client provides two categories of documentation:

**Category A — Procurement and submission (required):**

| Input | Description |
|-------|-------------|
| Procurement documentation | ITT, evaluation criteria, scoring methodology, lot structure, clarification responses |
| Submitted proposal | Full submission including technical, management, commercial, and pricing volumes |
| Authority feedback | Evaluation scores, written feedback, debrief notes (preferred but not required) |

**Category B — Pursuit process evidence (requested):**

| Input | Description |
|-------|-------------|
| Win strategy and intelligence | Competitive analysis, client intelligence reports, buyer persona documents, stakeholder engagement logs, win strategy document |
| Solution development | Solution pack, operating model documentation, workshop outputs, transition plan, risk register, TUPE analysis |
| Governance and management | Bid plan, team organogram, RACI, governance framework, review gate records, action logs, decision logs |
| Production management | Storyboards, style guide, win theme matrix, word count tracking, internal scoring records |
| Commercial | Pricing strategy, commercial model, risk allocation, competitive benchmarking |
| Post-submission (where applicable) | Presentation deck and speaker notes, rehearsal records, anticipated Q&A preparation, BAFO decision records, contract negotiation brief |

Category B inputs are what make Verdict forensic rather than superficial. Where Category B documentation is absent, that absence is itself a finding — it indicates activities that were either not performed or not documented, both of which are failure modes.

**Format:** PDF, Word, Excel, PowerPoint. The platform must ingest multi-volume submissions and cross-reference against evaluation criteria structures and pursuit process documentation.

### 6.2 Two-Pass Execution Model

Verdict operates through a two-pass process that combines platform analysis with consultant-led investigation. This is the core delivery model — the platform does the analytical heavy lifting; the consultant provides the human judgement that documentary evidence alone cannot deliver.

**Pass 1 — Platform Analysis (automated, ~2 hours processing)**

The platform ingests all client-provided documentation and runs the evaluation engine:

- **Document ingestion.** Agent 1 skills parse the ITT/procurement documentation (extraction of evaluation criteria, scoring methodology, response structure) and the client's submitted proposal (mapping responses to evaluation criteria, extracting claims, evidence, and key messages per section).
- **Process evaluation.** Each of the seven Verdict domains is assessed for activity coverage and evidence quality. The platform maps the client's pursuit process documentation against the expected activities for a pursuit of this complexity and flags gaps — activities not performed, evidence not captured, governance not applied.
- **Submission scoring.** Each response section is independently scored against the published evaluation criteria — matching the authority's scoring methodology, scale, and descriptive bands. This uses the same independent scoring skill that operates within Bid Execution's review module (pre-Pink and pre-Red AI quality assessment). One skill, two products.
- **Traceability analysis.** The platform traces the connection between upstream activities and downstream submission quality. Did the intelligence gathered appear in the win strategy? Did the win strategy translate into the storyboards? Did the storyboards translate into the written responses? Breaks in this chain are where pursuit quality is lost.

**Pass 1 produces:**
- Draft domain maturity ratings (7 domains × 5-point scale)
- Independent section-by-section scoring with variance analysis (where authority feedback is available)
- A structured list of **gaps, probe questions, and areas requiring human investigation** — these are the questions the consultant takes into the interview

**Pass 2 — Consultant Investigation and Enrichment (~1 day)**

The consultant reviews the Pass 1 output and conducts a structured interview or workshop with the client's bid team, armed with the AI-generated probe questions.

- **Interview focus.** The AI knows what's missing because it looked for evidence against every criterion. Where evidence is absent, it generates specific probe questions. The consultant's value is in knowing which questions to push on, reading the room, and surfacing what people don't put in writing.
- **Evidence enrichment.** Interview findings are captured and fed back into the platform. Activities rated "Absent" because no document was provided may move to "Informal" once the consultant learns they were done verbally but never documented.
- **Domain re-assessment.** The platform re-runs the domain assessments with the enriched data. Maturity ratings may shift in either direction.
- **Report finalisation.** The consultant reviews the Pass 2 output, applies professional judgement to edge cases, and finalises the Verdict Report.

**The output the client receives is always the Pass 2 report** — the one that reflects both documentary evidence and interview findings. The consultant's time per engagement is focused: approximately half a day for the interview plus half a day for report review and the debrief session.

### 6.3 Evaluation Engine Layers

The evaluation engine (used in both Pass 1 and Pass 2) operates across three layers:

**Layer 1 — Process evaluation.** Each of the seven Verdict domains is assessed for activity coverage and evidence quality. The platform maps the client's pursuit process documentation against the expected activities for a pursuit of this complexity and flags gaps — activities not performed, evidence not captured, governance not applied.

**Layer 2 — Submission scoring.** Each response section is independently scored against the published evaluation criteria — matching the authority's scoring methodology, scale, and descriptive bands. Qualitative scoring assesses narrative quality, evidence strength, specificity, and alignment with stated requirements. Quantitative scoring assesses pricing coherence, risk allocation, and competitive positioning. This produces a parallel score for comparison against the authority's feedback and the client's own internal assessment.

**Layer 3 — Traceability analysis.** The platform traces the connection between upstream activities and downstream submission quality. Did the intelligence gathered appear in the win strategy? Did the win strategy translate into the storyboards? Did the storyboards translate into the written responses? Did the solution workshops produce outputs that the writers could use? Breaks in this chain are where pursuit quality is lost — and where Verdict's diagnosis is most valuable.

### 6.4 Pattern Analysis Engine (Portfolio Tier)

For Verdict Portfolio engagements (three pursuits), the platform identifies cross-pursuit patterns across all eight domains:

- Recurring process gaps — activities systematically absent across multiple pursuits
- Governance patterns — review gates that consistently fail to improve output quality
- Evidence quality patterns — consistently weak case studies, absence of quantified outcomes, generic credentials
- Scoring patterns — recurring weaknesses in specific evaluation areas
- Mobilisation patterns — persistent late starts, under-resourcing, or team structure failures
- Commercial patterns — pricing structures that repeatedly fall outside competitive range
- Traceability failures — consistent disconnects between strategy and execution

**Output:** A portfolio-level diagnostic that synthesises findings across all reviewed pursuits into organisational-level insights — the structural weaknesses in the pursuit operation that no individual debrief would surface.

### 6.5 Outputs

| Deliverable | Content | Tier |
|-------------|---------|------|
| Verdict Report | Full eight-domain evaluation with maturity ratings, specific findings, and evidence assessment per domain. Pursuit Maturity Score. | Single + Portfolio |
| Scoring Report | Independent section-by-section scoring against evaluation criteria. Comparison with authority feedback and client internal assessment. Variance analysis. | Single + Portfolio |
| Traceability Map | Visual representation of the intelligence-to-submission chain, showing where upstream activities connected to or disconnected from the scored response. | Single + Portfolio |
| Recommendation Register | Prioritised recommendations mapped to specific domains and pursuit lifecycle stages, with impact rating and implementation guidance. | Single + Portfolio |
| Portfolio Pattern Report | Cross-pursuit pattern analysis across all eight domains. Organisational-level findings, recurring failure modes, and structural recommendations. | Portfolio only |
| Consultative Debrief | Live session (remote or in-person), structured around findings. Forensic walkthrough that pressure-tests assumptions, surfaces blind spots, and translates analysis into action. | Single + Portfolio |

### 6.6 Data Retention and Compounding

All Verdict data feeds into the BidEquity platform's compounding intelligence layer. With client consent, pursuit performance data from Verdict engagements contributes to:

- The client's pursuit performance baseline (if they progress to Core or Command)
- BidEquity's aggregate benchmarking dataset (anonymised)
- Pattern libraries that inform future Verdict scoring calibration
- Domain-specific maturity benchmarks by sector and contract type

This is a critical architectural requirement. Verdict is not a standalone tool — it is the entry point into the compounding data asset that sits at the heart of the BidEquity platform. The Pursuit Maturity Score and domain-level ratings feed directly into Core and Command engagement planning, creating a warm handover from retrospective diagnosis to live pursuit intelligence.

---

## 7. Platform Reuse Assessment

Verdict is not a new platform build. It is a new product configuration of existing BidEquity platform capabilities. The PWIN Platform MCP server (94 tools, 55 skills, 11 platform knowledge files) already supports the analytical engine Verdict requires.

### 7.1 Reused As-Is

| Component | What It Does for Verdict |
|-----------|------------------------|
| MCP server + Data API | Verdict is another product in the same platform. `verdict.json` alongside `qualify.json` and `bid_execution.json`. |
| Platform knowledge (11 files) | Sector-calibrated analysis, reasoning rules, scoring standards, confidence model — all apply to retrospective analysis. |
| Skill runner | Verdict skills are YAML configs executed by the same generic runner. |
| Shared pursuit entities | A Verdict engagement creates a pursuit with the same shared entities (client, sector, TCV, competitive positioning). |
| Agent 1: ITT Extraction | Parses the procurement documentation — identical use case. |
| Agent 3: Compliance Coverage (UC4) | Assesses coverage gaps against evaluation criteria — already retrospective in nature. |
| Agent 3: Win Theme Audit (UC5) | Assesses win theme coverage per section — directly applicable. |
| Agent 3: Marks Allocation (UC6) | Analyses effort-per-mark efficiency — directly applicable. |
| Agent 3: Gate Readiness (UC9) | Assesses governance quality — directly applicable. |
| Agent 3: Review Trajectory (UC7) | Tracks score trajectory across review cycles — directly applicable. |

### 7.2 Reused With Prompt Adaptation

| Component | Adaptation Required |
|-----------|-------------------|
| Agent 2 skills (client profiling, competitor profiling) | Reframe from "build intelligence for a live bid" to "assess whether intelligence was gathered and used." |
| Agent 5: Compliance Verification | Reframe from "pre-submission gate" to "post-submission forensic check." |
| Agent 4: Commercial Risk | Reframe from "build risk register" to "assess whether commercial risks were identified and mitigated." |

### 7.3 New Build Required

| Component | Effort | Description |
|-----------|--------|-------------|
| Proposal parsing skill | 1 YAML | Agent 1 currently extracts ITTs, not submitted proposals. New skill ingests the client's response and maps it to the evaluation criteria structure. |
| Independent scoring skill | 1 YAML | Scores each response section against evaluation criteria using the authority's scoring methodology. **Shared with Bid Execution** — same skill serves pre-review AI scoring in live bids and retrospective scoring in Verdict. |
| 8 forensic domain assessment skills | 8 YAMLs | One per Verdict domain (including conditional Domain 5.8 Post-Submission). Takes existing analysis patterns and reframes as retrospective forensic findings with maturity ratings (Absent/Informal/Defined/Managed/Optimised). |
| Traceability analysis skill | 1 YAML | Maps the chain from intelligence → strategy → storyboards → submission. Genuinely new analysis — no existing skill does cross-artefact traceability. |
| Verdict report assembly skill | 1 YAML | Consolidates all domain findings into the structured Verdict Report with Pursuit Maturity Score. |
| Interview question generation | Part of domain skills | Each forensic domain skill produces a "gaps and probe questions" output alongside the maturity rating — consumed by the consultant for Pass 2. |
| Verdict data model (`verdict.json`) | 1 day | Domain ratings, section scores, traceability findings, interview notes, final report. Add to Data API routes and MCP tools. |
| Portfolio pattern engine | 2-3 days | Cross-pursuit analysis reading multiple Verdict engagements. Phase 2 deliverable. |

### 7.4 Shared Scoring Skill — Cross-Product Design Note

The independent scoring skill is a single capability that serves two products:

- **In Bid Execution (live):** Before a Pink or Red review, the AI independently scores each response section, assesses structure, evidence quality, win theme integration, compliance, and predicts the evaluator's likely score. Feedback is appended as a ResponseItemAIInsight. This is designed in the plugin architecture (Section 6.6) but not yet built — the data model slot (ResponseItemAIInsight) and MCP tool (`update_response_insight`) exist as placeholders.

- **In Verdict (retrospective):** After submission, the AI scores each response section against the evaluation criteria using the authority's published scoring methodology. The output is compared against the authority's actual scores (where available) and the client's internal assessment, producing variance analysis.

Same skill, same scoring logic, different context. Build once, deploy in both products.

### 7.5 Estimated API Cost Per Engagement

Based on live testing of the platform skills (Session 16, April 2026):

| Step | Skills Invoked | Estimated Cost |
|------|---------------|----------------|
| Ingest procurement docs | ITT Extraction | ~$0.03 |
| Ingest submitted proposal | Proposal Parsing (new) | ~$0.05–0.10 |
| 8 domain assessments (Pass 1) | 8 forensic skills (Domain 5.8 where applicable) | ~$0.24 |
| Independent scoring | Scoring skill × 5–10 sections | ~$0.15–0.30 |
| Traceability analysis | 1 skill | ~$0.05 |
| Pass 2 re-assessment | 8 forensic skills (enriched) | ~$0.24 |
| Report assembly | 1 skill | ~$0.05 |
| **Total per Single Verdict** | | **~$0.80–1.00** |

At £2,000 price point with <£1 API cost, gross margin on platform costs is effectively 100%. The cost driver is consultant time, not technology.

### 7.6 Client Operating Context — Optional Enrichment, Not a Prerequisite

Agent 0 (the Client Operating Context skill, designed 2026-04-14) produces a platform-level, slow-moving model of the bidding organisation itself — capabilities, delivery archetypes, commercial posture, capacity constraints, red lines, avoid-archetypes. It is captured at onboarding as part of Core/Command engagements, not per pursuit.

**Levels are different — acknowledge it honestly.** Agent 0 describes the firm; Verdict forensically reviews a single lost opportunity. They operate at portfolio and instance levels respectively, and Verdict must not be designed to assume the portfolio layer exists.

**Commercial reality drives the boundary.** Verdict is the £2k low-commitment gateway product; Agent 0 is heavier onboarding tied to Core/Command. The realistic buyer flow is **Verdict first, Agent 0 later** for most new clients. Verdict therefore ships standalone and scores against absolute methodology benchmarks. Agent 0, where present, is an enrichment layer — not a prerequisite.

**Where the Client Operating Context materially sharpens Verdict (when available):**

- **Calibration of 5.3 Team Mobilisation** — "under-mobilised" becomes "under-mobilised *for this firm's* typical delivery shape".
- **Calibration of 5.7 Commercial and Pricing** — pricing discipline is judged against the firm's stated margin floor and commercial posture, not an industry abstraction.
- **Red-line / avoid-archetype cross-check** — if the lost pursuit falls inside a declared avoid-archetype or crosses a red line, the finding becomes a strategic pursuit-selection failure, which is a higher-order finding than any domain score.
- **Pass 2 probe sharpening** — consultant interview questions can reference specific stated commitments ("your margin floor is X; this bid priced at Y — who approved the exception?").
- **Pattern Analysis Engine (§6.4)** — this is where Agent 0's value is strongest. Portfolio-tier pattern insights across multiple Verdicts are only meaningful relative to a stable operating baseline. A client running Verdict repeatedly without Agent 0 gets per-pursuit findings but weaker portfolio patterns.

**Where it does not help.** Domains 5.1 (intelligence), 5.2 (win strategy), 5.6 (production quality), and 5.8 (post-submission) are judgeable from pursuit documentation alone.

**Design rules:**

1. Verdict skills MUST run to completion without the Client Operating Context. When absent, skills score against absolute methodology benchmarks and the report calls this out as a calibration limit.
2. When the Client Operating Context IS present and approved for AI use, Verdict skills read it as enrichment context — they do not re-interview leadership or write parallel capability / delivery / commercial-posture fields.
3. Recurring Verdict findings that sharpen the operating picture flow back into the Client Operating Context via a controlled write path (TBD), never by forking the entity.
4. Schema ownership sits with Agent 0 at `pwin-platform/schemas/client-operating-context.json`. Verdict depends on the schema contract; version changes must be coordinated.

---

## 8. Commercial Model

### 8.1 Pricing Structure

Verdict operates on a fixed-fee, transactional basis — deliberately different from the Paid on Award model used by Core and Command.

| Tier | Price | Scope |
|------|-------|-------|
| Verdict Single | £2,000 | One pursuit: full eight-domain evaluation, independent scoring, traceability map, recommendation register, consultative debrief |
| Verdict Portfolio | £5,000 | Three pursuits: everything in Single applied three times, plus cross-pursuit pattern analysis and portfolio-level diagnostic |

**Pricing note:** The £2,000 / £5,000 figures are indicative starting points. Final pricing may flex with pursuit complexity (contract value, number of evaluation lots, volume of submission documentation), but the principle is fixed-fee and agreed before work begins. The Portfolio tier at £5,000 for three reviews represents a clear saving over three Singles at £6,000 — the discount incentivises the multi-bid engagement that generates the most valuable intelligence for both parties.

### 8.2 Commercial Logic

A lost bid has already happened. There is no future outcome to align against. The value is in what the client learns and applies next time. This makes fixed-fee the only credible model — it removes friction, signals confidence in the deliverable, and makes the entry point as low-commitment as possible.

The Portfolio discount is not a volume incentive for its own sake. Three reviews produce the cross-pursuit pattern analysis, which is where the compounding intelligence activates — and where the conversion to Core or Command becomes natural.

---

## 9. Strategic Positioning

### 9.1 Within the BidEquity Ecosystem

Verdict occupies a specific position in the BidEquity product hierarchy:

**Verdict** → Post-loss forensic review (retrospective, transactional, fixed-fee)
**Core** → Pursuit intelligence and qualification (live pursuits, outcome-aligned)
**Command** → Embedded bid office capability (live pursuits, outcome-aligned)

Verdict is the entry point. Core is the ongoing engagement. Command is the deepest integration. Each product builds on the data generated by the previous one. The eight domains evaluated by Verdict map directly to the workstreams managed by Core and Command — the same methodology applied retrospectively (Verdict) or in real time (Core/Command).

### 9.2 Conversion Flywheel

The conversion logic operates in three stages:

**Stage 1: Single Verdict.** Client brings one lost pursuit. Receives a full eight-domain evaluation on a real pursuit they care about. The depth of the analysis — covering activities and evidence they never expected an external reviewer to examine — builds trust in a way that no pitch deck can match.

**Stage 2: Portfolio Verdict.** Client commissions two more reviews. The pattern report surfaces structural issues they had never identified — recurring process gaps, governance failures, and mobilisation problems that repeat across different bid teams and different pursuits.

**Stage 3: Core or Command engagement.** The conversation shifts from "review this bid" to "fix our bid operation." The domain maturity ratings and pattern analysis from Verdict become the watch list and priority workstreams for the Core or Command engagement. The client arrives with a data-driven understanding of where their pursuit operation is broken — and BidEquity arrives with the methodology to fix it.

### 9.3 For Existing Clients

For organisations already using Core or Command, Verdict extends the compounding data advantage across historical losses, losses from before the engagement started, or losses in business units not yet covered by the BidEquity relationship.

---

## 10. Differentiation

| Dimension | Internal Reviews | Consultancy Retrospectives | BidEquity Verdict |
|-----------|-----------------|---------------------------|-------------------|
| Scope | Focused on the written responses | Limited to what the consultant examines | Full pursuit lifecycle — eight domains from intelligence to commercials |
| Evidence assessment | Assumes activities were performed | Takes the team's account at face value | Asks "where is the evidence?" for every activity. Absence is a finding. |
| Independence | Conducted by the team that lost | Individual consultant's judgement | Platform-scored, methodology-driven, structured evaluation framework |
| Scoring | No independent scoring | Subjective assessment | Calibrated parallel scoring against authority criteria with variance analysis |
| Traceability | None | None | Maps the chain from intelligence through strategy to submission — identifies where it broke |
| Actionability | Confirms existing beliefs | Report with generic recommendations | Prioritised recommendations mapped to specific domains and pursuit lifecycle stages |
| Data value | Discarded after the meeting | A document, not a dataset | Feeds compounding intelligence platform with Pursuit Maturity Score and domain-level benchmarks |
| Cost | Free | £10,000–£30,000+ | £2,000–£5,000 fixed fee |
| Speed | Days (but shallow) | Weeks | Days (platform-enabled depth across all eight domains) |

---

## 11. Go-to-Market Strategy

### 11.1 Positioning

Verdict is positioned as the sharpest, lowest-risk way to experience BidEquity's methodology and platform. The messaging leads with the problem (compromised internal debriefs that only examine the written response), not the product.

**Primary line:** "You lost. The question is whether you learn anything from it."

**Challenger lines (social, campaigns):**
- "Your internal debrief confirmed what the team already believed. Ours won't."
- "The most expensive loss is the one you repeat."
- "You reviewed the proposal. We review the pursuit."
- "An independent verdict — not a consolation exercise."

**Institutional lines (capability documents):**
- "Forensic post-loss analysis across the full pursuit lifecycle. Platform-scored. Independently assured."
- "From loss to learning: structured pursuit intelligence applied retrospectively."

### 11.2 Launch Channels

| Channel | Approach |
|---------|----------|
| BidEquity website | Verdict tier card on services page, CTA from homepage, contact form subject option |
| LinkedIn (organic) | Challenger-register content series on post-loss review failures — 4-6 posts building to Verdict launch |
| Direct outreach | Targeted approach to BD leads at known recent losers of major public sector contracts (£50m+) |
| Existing pipeline | Offer Verdict to prospects in early-stage conversations as a low-commitment entry point |
| Industry events | Position Verdict in conference presentations on pursuit performance and win rate improvement |

### 11.3 Sales Motion

Verdict is a transactional sale, not a consultative one. The decision cycle should be short — days, not months. The sales motion reflects this:

1. **Trigger identification.** Monitor Contract Award Notices for major contract awards. The losers are Verdict prospects.
2. **Outreach.** Direct, challenger-register approach: "You just lost [contract]. We can tell you why — independently, in a week, for £2,000."
3. **Scoping call.** 30-minute call to confirm inputs available, agree timeline, and set expectations. Specifically assess what Category B (pursuit process) evidence the client can provide — this determines the depth of the forensic analysis.
4. **Delivery.** Platform analysis and debrief within 5–10 working days of receiving documentation.
5. **Conversion.** Post-debrief, offer Portfolio tier if the client has additional losses to review. Post-Portfolio, transition the conversation to Core or Command using the Pursuit Maturity Score and domain ratings as the basis.

### 11.4 Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Verdict engagements per quarter | 5 (Year 1), 12 (Year 2) | CRM tracking |
| Single-to-Portfolio conversion rate | 40% | Clients commissioning Portfolio after initial Single |
| Verdict-to-Core/Command conversion rate | 25% (Year 1), 35% (Year 2) | Clients progressing to outcome-aligned engagement |
| Time from documentation receipt to debrief | 10 working days (Single), 15 working days (Portfolio) | Delivery tracking |
| Client satisfaction (debrief NPS) | 60+ | Post-debrief survey |
| Average revenue per Verdict client (12-month) | £8,000+ | Including upsell to Portfolio and subsequent products |
| Category B evidence provision rate | 60%+ | Proportion of clients providing pursuit process documentation beyond the submission itself |

---

## 12. Build Plan

### 12.1 Platform Position

Verdict is built on the existing PWIN Platform MCP server (94 tools, 55 skills, 11 platform knowledge files). The platform already supports document ingestion, evaluation criteria analysis, compliance coverage, win theme audit, governance assessment, and structured report generation. Verdict adds a product-specific data file, ~11 new skill configs, and a two-pass execution flow.

This means the original phased roadmap assumption — that Phase 1 would be "consultancy-led with platform-assisted analysis" — underestimates the automation available from day one. The platform can run the full eight-domain analysis automatically in Pass 1; the consultant's role is Pass 2 (investigation, enrichment, professional judgement).

### 12.2 Build Sequence

**Sprint 1: Data Model and Platform Integration (2–3 days)**

| Task | Detail |
|------|--------|
| Create `verdict.json` schema | Domain ratings, section scores, traceability findings, interview notes, probe questions, final report, Pursuit Maturity Score |
| Add Verdict Data API routes | GET/PUT `/api/pursuits/{id}/verdict` |
| Add Verdict MCP tools | `get_verdict_assessment`, `update_verdict_domain`, `save_verdict_scores`, `generate_verdict_report` |
| Extend shared entities | Verdict engagement metadata in `shared.json` — linked to existing pursuit |

**Sprint 2: Core Skills (3–5 days)**

| Task | Detail |
|------|--------|
| Proposal parsing skill | New Agent 1 skill — ingests submitted proposal, maps responses to evaluation criteria, extracts claims and evidence per section |
| Independent scoring skill | Scores each response section against evaluation criteria. **Shared with Bid Execution** pre-review AI scoring. Build once, configure for both products. |
| 8 forensic domain assessment skills | One per Verdict domain (Domain 5.8 conditionally assessed). Each produces: maturity rating, specific findings, evidence assessment, gaps, and probe questions for consultant interview |
| Traceability analysis skill | Maps intelligence → strategy → storyboards → submission. Identifies breaks in the chain. |
| Verdict report assembly skill | Consolidates all domain outputs into final Verdict Report with Pursuit Maturity Score |

**Sprint 3: Delivery Infrastructure (2–3 days)**

| Task | Detail |
|------|--------|
| Client intake workflow | Structured document upload and classification (Category A vs B) |
| Pass 2 enrichment flow | API endpoint for consultant to submit interview findings; triggers domain re-assessment |
| Verdict Report template | Branded output format covering all eight domains |
| Scoring comparison | Variance analysis between AI scores, authority scores (if available), and client self-assessment |

**Sprint 4: Portfolio Tier (2–3 days)**

| Task | Detail |
|------|--------|
| Portfolio pattern engine | Cross-pursuit analysis reading multiple Verdict engagements |
| Portfolio Report template | Organisational-level findings and structural recommendations |
| Benchmarking data structure | Store Pursuit Maturity Scores and domain ratings for future cross-client benchmarking |

**Total estimated build: 9–14 days** (compared to the original 12-month roadmap which assumed building the evaluation engine from scratch).

### 12.3 Phased Commercial Launch

The build plan above produces a commercially launchable product. The phased launch is about market validation, not platform readiness:

**Month 1: Founding client engagements (2–3 Verdict Singles)**
- Validate the eight-domain framework against real lost bids
- Refine forensic domain skill prompts based on actual client documentation
- Calibrate independent scoring against known authority outcomes
- Establish consultant delivery process (intake → Pass 1 → interview → Pass 2 → debrief)

**Month 2–3: Commercial launch**
- Website integration (tier card, CTA, contact form)
- LinkedIn content series and direct outreach to known recent losers
- First Portfolio engagement
- Pricing validation

**Month 4–6: Scale and conversion**
- Single-to-Portfolio conversion tracking
- Verdict-to-Core/Command pipeline activation
- Benchmarking dataset growing
- Process evaluation automation refinements

**Month 7–12: Platform maturation**
- Anonymised cross-client benchmarks
- Automated trigger identification (Contract Award Notice monitoring)
- Self-service intake portal
- Core/Command integration (domain ratings feed engagement planning)

---

## 13. Dependencies and Risks

### 13.1 Dependencies

| Dependency | Impact | Mitigation |
|------------|--------|------------|
| Platform evaluation engine readiness | Verdict quality depends on credible, calibrated scoring and process evaluation | Phase 1 uses consultant-validated analysis; full automation phased across Phases 2–3 |
| Client provision of Category B evidence | The depth of the forensic analysis depends on the client providing pursuit process documentation, not just the submission | Design the intake process to make it easy; explain why each document matters; design the report to surface gaps where evidence was not provided |
| Access to authority feedback | Parallel scoring comparison is most powerful when authority feedback is available | Design analysis to deliver value even without authority feedback — the independent scoring and process evaluation stand alone |
| Procurement documentation quality | Evaluation criteria and scoring methodology vary significantly across contracting authorities | Build rubric library covering the four target sectors; design for flexibility |
| Client willingness to share losing submissions | Organisations may be reluctant to expose both a lost proposal and their pursuit process to an external party | Position independence as the value — the analysis is only useful because it comes from outside. NDA and confidentiality framework as standard. |

### 13.2 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Scoring diverges significantly from authority without clear rationale | Medium | High — undermines credibility | Calibration against known outcomes; consultant review; transparent methodology in debrief |
| Clients provide Category A but not Category B — limiting the forensic depth | High | Medium — reduces the value of the process evaluation domains | Design report to work at two levels: submission-only and full pursuit review. Position Category B provision as the differentiator that makes Verdict forensic. |
| Low initial demand — organisations do not commission post-loss reviews | Medium | Medium — delays flywheel activation | Direct outreach tied to specific known losses; reduced rate for initial case studies |
| Verdict cannibalises Core/Command pipeline | Low | Medium | Verdict scope is retrospective only; no overlap with live pursuit products |
| Delivery timeline slips beyond 10 days | Medium | Medium | Phase 1 relies on consultant capacity; limit concurrent engagements until platform automation is live |
| Evaluation framework is too detailed for the documentation clients actually retain | Medium | Medium | Build the framework to be comprehensive but assess what is available, not what is missing. Absence of evidence is a finding, not a blocker. |

---

## 14. Success Criteria

Verdict succeeds if it achieves three things within its first twelve months:

1. **Standalone commercial viability.** Revenue from Verdict engagements covers direct delivery costs by Month 9, with a path to positive contribution margin by Month 12.

2. **Conversion engine activation.** At least 25% of Verdict clients progress to a Core or Command conversation within 6 months of their first Verdict engagement. The Pursuit Maturity Score and domain-level findings are used as the basis for those conversations.

3. **Compounding data contribution.** Verdict engagement data is structured and retained in the platform, contributing to Pursuit Maturity Score benchmarks, pattern libraries, and scoring calibration that improve both Verdict delivery and Core/Command engagement planning.

4. **Framework validation.** The eight-domain evaluation framework is validated through at least 10 engagements in the first 12 months, with refinements incorporated based on real-world application. The framework becomes a recognised, defensible standard for pursuit capability assessment.

---

## 15. Open Questions

| Question | Owner | Status |
|----------|-------|--------|
| Should Verdict pricing flex by contract value (e.g. higher fee for £500m+ pursuits)? | Commercial | Open |
| What is the minimum viable evaluation engine capability for Phase 1 launch? | Platform | Open |
| Should the first 3–5 engagements be offered at a founding client rate to build case studies and validate the framework? | Commercial | Open |
| How does data consent work — can client data contribute to anonymised benchmarks by default, or explicit opt-in? | Legal / Commercial | Open |
| What is the right approach when a client provides Category A but refuses Category B documentation? Reduced-scope Verdict or decline? | Product | Open |
| Should the Pursuit Maturity Score be positioned as a standalone benchmark product, separate from Verdict? | Strategy | Open — deferred to post-Phase 2 review |
| Should Verdict extend beyond public sector to regulated private sector (e.g. utilities, rail, healthcare)? | Strategy | Open — deferred to post-Phase 2 review |

---

## Appendix A: Cross-Reference — Verdict Domains vs Qualify & Execution Methodology

This appendix maps each Verdict evaluation domain against the existing PWIN Qualify categories (6 categories, 24 questions) and Bid Execution activities (84 activities across 10 workstreams). It identifies coverage and gaps.

### A.1 Domain 5.1: Pursuit Intelligence & Competitive Positioning (15%)

| Verdict Criterion | Qualify Coverage | Bid Execution Activities |
|---|---|---|
| Competitive landscape analysis | cp: Strategy Foundation, Competitive Intelligence, Countertactics (3 questions) | SAL-03 Competitor analysis & positioning |
| Client intelligence | pp: Client Engagement, Communication Transparency (2 questions) | SAL-01 Customer engagement & intelligence gathering |
| Buyer personas & values mapping | vp: Client Value Justification, Validated Alignment (2 questions) | SAL-01 (buyer values within intel gathering) |
| Decision-making unit | ss: Decision Authority Relationships, Evaluator Coverage (2 questions) | SAL-10 Stakeholder relationship mapping |
| Stakeholder engagement | ss: Internal Champion, Competitor Relationships (2 questions) | SAL-10, SAL-01 |
| Intelligence-to-strategy translation | oi: Network of Influence, Political Coaching (partial) | SAL-06 Capture plan finalisation (locks strategy from intelligence) |

**Coverage: STRONG.** Qualify's 6 categories and 24 questions cover this domain comprehensively. SAL workstream activities (SAL-01, SAL-03, SAL-10) provide the process evidence layer. **No gaps identified.**

### A.2 Domain 5.2: Win Strategy & Positioning (20%)

| Verdict Criterion | Qualify Coverage | Bid Execution Activities |
|---|---|---|
| Win strategy definition | cp: Strategy Foundation, Winning Proposition | SAL-04 Win theme development, SAL-06 Capture plan lock |
| Discriminator identification | cp: Winning Proposition; vp: Differentiated | SAL-04, SAL-05 Evaluation criteria mapping |
| Win themes & key messages | vp: Co-Developed, Differentiated, Validated Alignment | SAL-04, BM-10 Storyboard development |
| Evaluation criteria alignment | pi: Decision Criteria & Drivers | SAL-05 Evaluation criteria mapping & scoring strategy |

**Coverage: STRONG.** Qualify's cp and vp categories map directly. SAL-04/05/06 provide the process evidence. BM-10 (storyboard) bridges strategy to execution. **No gaps identified.**

### A.3 Domain 5.3: Team Mobilisation & Organisation (10%)

| Verdict Criterion | Qualify Coverage | Bid Execution Activities |
|---|---|---|
| Mobilisation timing | pp: Future Focus (tangential only) | BM-01 Kickoff planning |
| Team structure & roles | — | BM-01 (RACI in output), BM-04 Resource management |
| Seniority & authority | oi: Power Dynamics (tangential) | BM-08 Stakeholder & communications management |
| Bid plan | — | BM-02 Bid management plan, BM-06 Progress reporting |
| Resource adequacy | — | BM-04 Resource management, BM-05 Bid cost management |

**Coverage: PARTIAL.** Qualify does not assess team mobilisation — it focuses on the opportunity, not the bid operation. Bid Execution has the BM (Bid Management) workstream, but these are process activities, not assessment criteria. **Gap: No existing skill specifically assesses whether the team was adequate for the complexity. The Verdict forensic skill for this domain is genuinely new assessment logic, not a reframe of existing analysis.**

### A.4 Domain 5.4: Solution Development (15%)

| Verdict Criterion | Qualify Coverage | Bid Execution Activities |
|---|---|---|
| Incumbent service understanding | — | SOL-02 Current operating model assessment |
| Operating model design | — | SOL-03 Target operating model design |
| Solution workshops | — | SOL-03, SOL-04 (workshop outputs are inputs) |
| Transition & mobilisation planning | — | SOL-07 Transition & mobilisation approach |
| Risk assessment | — | SOL-12 Solution risk identification, DEL-01 Delivery risk register |
| TUPE & workforce | — | SOL-06 Staffing model & TUPE analysis, LEG-04 TUPE obligations |
| Solution-to-response traceability | — | SOL-11 Solution design lock, BM-10 Storyboard (bridge) |

**Coverage: STRONG on activities, ABSENT on Qualify.** Qualify doesn't assess solution quality — it's a pre-ITT qualification tool. Bid Execution's SOL workstream (12 activities) covers the entire solution development lifecycle. Agent 6 skills map directly. **No gap in activities; the Verdict forensic skill reframes Agent 6 forward-looking skills as retrospective assessment.**

### A.5 Domain 5.5: Governance & Review Process (10%)

| Verdict Criterion | Qualify Coverage | Bid Execution Activities |
|---|---|---|
| Governance framework | — | GOV-01 through GOV-06 (6 configurable gates) |
| Review cadence & attendance | — | PRD-05 Pink review, PRD-06 Red review, PRD-07 Gold review |
| Review quality & impact | — | Review scorecards and actions (data model: reviewCycles, reviewActions) |
| Actions & decisions | — | BM-08 Decision log, GOV gate decision records |
| Escalation & issue resolution | — | BM-13 Bid risk register, BM-06 Progress reporting |

**Coverage: STRONG on Bid Execution.** The governance gate model (GOV-01 to GOV-06) and review cycle model (Pink/Red/Gold) are fully designed. Agent 3 skills (gate-readiness, review-trajectory) already assess governance quality. **No gap. Qualify deliberately excludes governance — it's a pre-bid tool.**

### A.6 Domain 5.6: Proposal Production & Quality (20%)

| Verdict Criterion | Qualify Coverage | Bid Execution Activities |
|---|---|---|
| Storyboarding | — | BM-10 Storyboard development & sign-off |
| Tone of voice & consistency | — | BM-07 Quality management approach |
| Win theme execution | — | PRD-02 Section drafting (win themes in content) |
| Question compliance | — | PRD-01 Compliance matrix, PRD-08 Final QA |
| Evidence quality | — | SOL-10 Evidence strategy, PRD-03 Evidence & case study assembly |
| Language & readability | — | PRD-08 Final QA & formatting |
| Independent scoring | — | **NOT YET BUILT** — ResponseItemAIInsight is a placeholder |

**Coverage: STRONG on activities, KEY GAP on independent scoring.** The production activities (PRD-01 through PRD-09) cover the full production lifecycle. Agent 5 skills cover drafting and formatting. **The independent scoring skill is the critical gap — designed (ResponseItemAIInsight entity, `update_response_insight` MCP tool) but not built. This is the shared skill that serves both Verdict and Bid Execution pre-review AI scoring.**

### A.7 Domain 5.7: Commercial & Pricing (10%)

| Verdict Criterion | Qualify Coverage | Bid Execution Activities |
|---|---|---|
| Pricing strategy | — | COM-02 Price-to-win analysis |
| Commercial model coherence | — | COM-01 Should-cost model, COM-04 Commercial model |
| Risk allocation | — | COM-07 Commercial risk register, DEL-06 Risk mitigation |
| Competitive positioning | — | COM-02 Price-to-win, SAL-03 Competitor analysis |
| Pricing-narrative alignment | — | COM-06 Pricing model finalisation (lock), PRD-04 Pricing response |

**Coverage: STRONG.** COM workstream (7 activities) covers the full commercial lifecycle. Agent 4 skills map directly. **No gap.**

### A.8 Domain 5.8: Post-Submission & Presentation (5%, conditional)

| Verdict Criterion | Qualify Coverage | Bid Execution Activities |
|---|---|---|
| Presentation preparation | — | POST-01 Presentation design & development |
| Presentation rehearsal & coaching | — | POST-02 Presentation rehearsals & coaching |
| Evaluator question anticipation | — | POST-02 (rehearsal includes Q&A prep), Agent 5 Skill 5.7 (presentation-intelligence UC15) |
| BAFO response | — | POST-05 BAFO preparation & revised pricing, POST-06 BAFO governance approval |
| Contract negotiation readiness | — | POST-07 Contract negotiation support |
| Post-submission intelligence | — | POST-04 Post-submission clarification management |

**Coverage: STRONG on Bid Execution.** The POST workstream (8 activities) covers the full post-submission lifecycle. Agent 5 Skill 5.7 (presentation-intelligence) already predicts evaluator probe questions from review data. **No gap in activities. Domain is conditionally assessed — excluded from scoring when the procurement did not include a presentation/BAFO stage.**

### A.9 Summary: What's Missing from Verdict That Qualify and Execution Already Cover

Nothing material. The Verdict PRD's 8 domains are well-covered by the combined Qualify + Execution methodology. The coverage pattern is:

| Domain | Qualify | Execution | Gap? |
|---|---|---|---|
| 5.1 Intelligence | **Strong** (categories cp, pi, ss, oi, vp, pp) | Strong (SAL workstream) | No |
| 5.2 Win Strategy | **Strong** (categories cp, vp) | Strong (SAL-04/05/06) | No |
| 5.3 Team Mobilisation | Weak | Moderate (BM workstream) | **Yes — no assessment skill** |
| 5.4 Solution | Absent | **Strong** (SOL workstream, 12 activities) | No |
| 5.5 Governance | Absent | **Strong** (GOV gates, Pink/Red/Gold) | No |
| 5.6 Proposal Quality | Absent | Strong (PRD workstream) | **Yes — independent scoring skill not built** |
| 5.7 Commercial | Absent | **Strong** (COM workstream) | No |
| 5.8 Post-Submission | Absent | **Strong** (POST workstream, 8 activities) | No (conditional domain) |

### A.10 What Verdict Covers That Neither Product Currently Assesses

1. **Retrospective maturity rating** — the 5-point scale (Absent → Optimised) applied per domain is new. Existing skills produce findings and recommendations; they don't produce a normalised maturity assessment.

2. **Cross-artefact traceability** — tracking whether intelligence actually flowed through to strategy, strategy to storyboards, storyboards to responses. No existing skill does this.

3. **Variance analysis** — comparing AI-generated scores against authority scores and client self-assessment. This is a Verdict-specific analysis requiring all three data points.

4. **Portfolio pattern analysis** — cross-pursuit patterns are beyond the scope of any single-pursuit product. This is a Verdict Portfolio tier feature.

---

*BidEquity Verdict PRD v2.0 — April 2026*
*Confidential — not for external distribution without approval.*
