#!/usr/bin/env node
/**
 * Deepen thin L3 activities in the gold standard.
 * Reads the gold standard, identifies activities with <=2 L3 tasks in target workstreams,
 * replaces their subs with expanded versions, and writes the updated gold standard.
 *
 * The expanded L3 tasks follow the same quality bar as SAL/SOL/COM:
 * - Specific, actionable task names
 * - Full RACI
 * - Structured inputs/outputs with quality criteria
 * - Setup + Ongoing L2 pattern for continuous activities
 */

const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════════
// EXPANDED ACTIVITY DEFINITIONS
// Only the subs[] and outs[] arrays — everything else stays the same
// ═══════════════════════════════════════════════════════════════════

const expansions = {

// ──────────────────────────────────────────────────────────────────
// BM WORKSTREAM
// ──────────────────────────────────────────────────────────────────

'BM-01': {
  subs: [
    {
      id: 'BM-01.1', name: 'Kickoff Preparation',
      description: 'Prepare the kickoff briefing pack, war room, and pre-meeting materials',
      tasks: [
        { id: 'BM-01.1.1', name: 'Prepare kickoff briefing pack — win strategy summary, client context, evaluation framework overview, key risks, and timeline constraints',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'All Workstream Leads' },
          outputs: [{ name: 'Kickoff briefing pack', format: 'Presentation / document', quality: ['Win strategy distilled to actionable messages for each workstream','Client context and evaluation framework summarised','Key risks and constraints identified for team awareness','Timeline constraints and non-negotiable milestones highlighted'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-01.1.2', name: 'Set up bid war room — physical or virtual collaboration space, information radiators, shared drive, communication channels',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: null, i: 'All' },
          outputs: [{ name: 'War room / collaboration environment', format: 'Physical or virtual workspace', quality: ['Central workspace established — physical room or virtual equivalent','Information radiators visible — timeline, RAG status, key dates','Shared drive and communication channels operational','Access provisioned for all confirmed team members'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    },
    {
      id: 'BM-01.2', name: 'Kickoff Execution',
      description: 'Run the kickoff meeting, confirm team structure, brief strategy, and baseline the programme',
      tasks: [
        { id: 'BM-01.2.1', name: 'Confirm bid team structure — assign roles and RACI across all workstreams, confirm named individuals, identify gaps and contingencies',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: 'HR / Resource Pool' },
          outputs: [{ name: 'RACI matrix and bid team register', format: 'Structured RACI with team contact list', quality: ['Every workstream has named lead with clear accountability','RACI covers all 84 activities — no orphan activities without owners','Security clearance requirements identified per role','Contingency plan for key-person risk documented'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-01.2.2', name: 'Brief locked win strategy to full team — ensure every team member understands what we are trying to win, how, and why',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'All' },
          outputs: [{ name: 'Strategy briefing record', format: 'Meeting record with attendees', quality: ['Win themes articulated and understood by all workstream leads','Competitive positioning explained — what differentiates us','Buyer values communicated — what the client cares about beyond the scoring','Team questions addressed and recorded'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-01.2.3', name: 'Agree master bid programme — backward-plan from submission deadline, set milestones, review points, governance gates, and critical path',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: 'Commercial Lead' },
          outputs: [{ name: 'Master bid programme (baselined)', format: 'Gantt / programme plan', quality: ['Backward-planned from submission deadline with all key milestones','Critical path identified — activities that drive the timeline','Review cycle dates set — pink, red, gold, governance gates','Workstream leads have confirmed their activity timelines are achievable','Programme baselined — this is the reference against which progress is tracked'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-01.2.4', name: 'Establish communications plan — meeting cadence, reporting lines, escalation procedures, decision log format',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Kickoff pack (activity primary output)', format: 'Kickoff document with RACI, programme, and comms plan', quality: ['Weekly standup cadence and format agreed','Reporting lines and escalation path documented','Decision log format established','Communications plan covers both internal team and governance stakeholders'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Kickoff pack: strategy summary, RACI, timeline, comms plan', format: 'Kickoff document', quality: ['Team RACI established with named individuals for all activities','Win strategy briefed to full team with understanding confirmed','Master programme backward-planned and baselined','Communications plan and meeting cadence agreed','War room / collaboration environment operational'] }]
},

'BM-02': {
  subs: [
    {
      id: 'BM-02.1', name: 'BMP Development',
      description: 'Produce the authoritative bid management plan that governs the entire bid',
      tasks: [
        { id: 'BM-02.1.1', name: 'Draft bid management plan — scope definition, governance framework, quality approach, risk management, and review schedule',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: 'Legal' },
          outputs: [{ name: 'BMP draft', format: 'Document', quality: ['Scope: what is in and out of this bid response','Governance: decision rights, escalation, gate schedule','Quality: page budgets, writing standards, review criteria','Risk: bid process risk approach, who owns what'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-02.1.2', name: 'Define submission plan — portal logistics, file formats, packaging requirements, naming conventions, submission timeline',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Bid Coordinator', i: 'IT Support' },
          outputs: [{ name: 'Submission plan', format: 'Section within BMP', quality: ['Portal access tested and confirmed','File format and size constraints documented','Naming conventions for all submission documents agreed','Submission timeline allows 48 hours contingency before deadline'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-02.1.3', name: 'Review and baseline BMP — Bid Director sign-off, distribute to team as the operational reference for the bid',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Bid management plan (activity primary output)', format: 'Comprehensive BMP document', quality: ['BMP reviewed and signed off by Bid Director','Distributed to all workstream leads as authoritative reference','Review schedule mapped to master programme milestones','Quality approach aligned to SAL-05 scoring strategy'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Bid management plan (BMP)', format: 'Comprehensive BMP document', quality: ['Covers: scope, governance, quality, risk, comms, reviews, submission plan','Review schedule mapped to master programme milestones','Quality approach aligned to SAL-05 scoring strategy','Submission plan with portal logistics and contingency','BMP accepted by Bid Director as the operational reference for the bid'] }]
},

'BM-03': {
  subs: [
    {
      id: 'BM-03.1', name: 'Collaboration Setup',
      description: 'Establish the document management infrastructure for the bid',
      tasks: [
        { id: 'BM-03.1.1', name: 'Establish document repository with folder structure mirroring workstream and activity hierarchy',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Repository structure', format: 'Folder hierarchy', quality: ['Folder structure mirrors workstream/activity hierarchy','Top-level folders for each workstream plus cross-cutting (governance, reviews, submission)','Template documents pre-loaded where corporate standards exist'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-03.1.2', name: 'Define and enforce naming conventions and version control procedures',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: null, i: 'All' },
          outputs: [{ name: 'Naming and versioning standards', format: 'Reference document', quality: ['Naming convention documented and communicated — e.g. [ActivityID]_[DocumentName]_v[X.Y]','Version control procedure clear — who can create versions, how to handle concurrent edits','Archive procedure for superseded documents'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-03.1.3', name: 'Configure access permissions and collaboration platform — ensure security, partner access, and audit trail',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'IT', i: 'Partner Lead' },
          outputs: [{ name: 'Collaboration platform operational (activity primary output)', format: 'Configured platform', quality: ['Access permissions set per role — internal, partner, read-only, edit','Security classification enforced — commercial in confidence, official sensitive as required','Audit trail enabled — who changed what, when','Partner access configured with appropriate restrictions'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Repository structure, naming conventions, platform', format: 'Configured collaboration platform', quality: ['Folder structure mirrors workstream hierarchy','Naming conventions enforced','Version control operational','Access permissions and security configured','Partner access provisioned'] }]
},

'BM-04': {
  subs: [
    {
      id: 'BM-04.1', name: 'Resource Mobilisation',
      description: 'Confirm and mobilise the full bid team at bid start',
      tasks: [
        { id: 'BM-04.1.1', name: 'Confirm and mobilise full bid team — internal resources, partner resources, and contingency bench',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'HR / Resource Pool', i: 'Partner Lead' },
          outputs: [{ name: 'Confirmed team roster', format: 'Team register', quality: ['All named roles from RACI have confirmed individuals','Start dates and availability confirmed per person','Security clearance requirements identified and applications initiated','Partner resource confirmations received'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-04.1.2', name: 'Identify resource gaps and key-person risks — develop mitigation plan for critical roles',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: 'HR' },
          outputs: [{ name: 'Resource risk register', format: 'Risk register', quality: ['Every unfilled role identified with target fill date','Key-person risks assessed — what happens if Solution Architect or Commercial Lead is unavailable?','Contingency resources identified for critical roles','Escalation path for persistent resource gaps documented'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'BM-04.2', name: 'Ongoing Resource Tracking',
      description: 'Track resource availability and manage changes throughout the bid',
      tasks: [
        { id: 'BM-04.2.1', name: 'Track resource availability and utilisation — weekly update of who is on the bid, their allocation, and any changes',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Workstream Leads' },
          outputs: [{ name: 'Resource tracker (living document)', format: 'Tracker / register', quality: ['Updated at least weekly','Allocation percentage per person tracked','Upcoming availability changes flagged in advance','Included in weekly progress report'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-04.2.2', name: 'Manage security clearance applications — track submissions, chase outstanding, escalate blockers',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'Security Manager', i: null },
          outputs: [{ name: 'Security clearance log', format: 'Tracker', quality: ['All clearance applications submitted within first week','Status tracked weekly — submitted, in progress, cleared, rejected','Blockers escalated immediately — clearance delays can block site access and data room access'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    }
  ],
  outs: [{ name: 'Resource tracker, security clearance log, availability register', format: 'Living documents', quality: ['Full team mobilised with confirmed individuals','Resource gaps identified with mitigation plans','Security clearance applications tracked to completion','Availability tracked weekly throughout the bid'] }]
},

'BM-05': {
  subs: [
    {
      id: 'BM-05.1', name: 'Budget Setup',
      description: 'Establish bid cost baseline and tracking framework',
      tasks: [
        { id: 'BM-05.1.1', name: 'Establish bid cost baseline — approved budget from bid mandate, broken down by workstream and cost category',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Finance', i: null },
          outputs: [{ name: 'Bid cost baseline', format: 'Budget tracker', quality: ['Budget broken down by workstream and cost category (people, travel, external, production)','Baseline aligned to bid mandate approval','Cost categories match corporate cost-to-bid reporting'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'BM-05.2', name: 'Ongoing Cost Tracking',
      description: 'Track bid investment against budget throughout the bid lifecycle',
      tasks: [
        { id: 'BM-05.2.1', name: 'Track actuals vs budget by workstream — weekly or fortnightly, with variance analysis',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Finance', i: 'Workstream Leads' },
          outputs: [{ name: 'Cost-to-bid report', format: 'Tracker with variance analysis', quality: ['Actuals captured per workstream and cost category','Variance against baseline highlighted — over/under/on track','Forecast to completion updated at each reporting cycle','Material variances explained with root cause'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-05.2.2', name: 'Report bid cost position at governance gates — actual spend, forecast to complete, any budget increase requests',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Finance', i: 'Bid Board' },
          outputs: [{ name: 'Governance cost summary (activity primary output)', format: 'Summary for governance pack', quality: ['Cost position presented at every governance gate','Forecast to complete realistic — not optimistic','Budget increase requests flagged early with justification','Cost-to-bid included in governance pack'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    }
  ],
  outs: [{ name: 'Cost-to-bid tracker', format: 'Living tracker with governance summaries', quality: ['Baseline established from bid mandate','Actuals tracked weekly by workstream','Variance analysis with root cause for material variances','Cost position reported at every governance gate'] }]
},

'BM-06': {
  subs: [
    {
      id: 'BM-06.1', name: 'Weekly Programme Cadence',
      description: 'Run the weekly operational rhythm of the bid',
      tasks: [
        { id: 'BM-06.1.1', name: 'Conduct weekly standups with workstream leads — progress against plan, blockers, actions, RAG status per activity',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: null },
          outputs: [{ name: 'Standup action log', format: 'Meeting record with actions', quality: ['Every workstream lead reports status against their activities','Blockers identified with owners and target resolution dates','Actions captured with owners — not just discussed','RAG status per activity updated'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-06.1.2', name: 'Produce weekly progress report — programme status against baseline, milestone tracking, RAG dashboard',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Bid Board' },
          outputs: [{ name: 'Weekly progress report', format: 'Report / dashboard', quality: ['Programme status shown against baselined plan','Milestones tracked — achieved, on track, at risk, missed','RAG dashboard per workstream and per critical activity','Key decisions needed and escalations highlighted'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    },
    {
      id: 'BM-06.2', name: 'Milestone & Escalation Reporting',
      description: 'Report significant milestones and manage escalations',
      tasks: [
        { id: 'BM-06.2.1', name: 'Track critical path and flag slippage — any activity on the critical path that is behind schedule triggers immediate escalation',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Workstream Leads' },
          outputs: [{ name: 'Critical path status', format: 'Programme update', quality: ['Critical path recalculated at each reporting cycle','Slippage on critical path activities flagged immediately — not at next weekly meeting','Impact assessment provided — how much float has been consumed, what is the deadline risk'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-06.2.2', name: 'Prepare milestone achievement reports for governance — formal record of key deliverables completed',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Bid Board' },
          outputs: [{ name: 'Milestone achievement reports (activity primary output)', format: 'Governance report', quality: ['Each key milestone formally recorded when achieved','Evidence of completion linked — e.g. solution locked, pricing approved, red review completed','Late milestones documented with root cause and impact assessment','Feeds governance pack preparation'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    }
  ],
  outs: [{ name: 'Weekly progress reports, milestone achievement reports', format: 'Reports and dashboards', quality: ['Weekly cadence maintained throughout bid','Programme status tracked against baseline','Critical path monitored with immediate escalation on slippage','Milestone achievements formally recorded','Feeds governance pack at every gate'] }]
},

'BM-07': {
  subs: [
    {
      id: 'BM-07.1', name: 'Quality Framework Design',
      description: 'Establish the quality standards and review framework for the bid response',
      tasks: [
        { id: 'BM-07.1.1', name: 'Develop page budgets per response section based on marks concentration from SAL-05 — highest marks = most pages',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Writers' },
          outputs: [{ name: 'Page budget allocation', format: 'Structured allocation table', quality: ['Every scored section has an allocated page budget','Budget proportional to marks weight — high-value sections get more space','Total pages within ITT limit (if applicable)','Buffer allocated for executive summary and cross-references'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-07.1.2', name: 'Define writing standards — tone, structure, language rules, evidence citation approach, visual guidelines',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Senior Bid Writer', i: 'Writers' },
          outputs: [{ name: 'Writing standards guide', format: 'Reference document', quality: ['Tone defined — matches client culture and evaluation expectations','Structure template per section type (method statement, case study, CV)','Evidence citation approach agreed — how to reference case studies, data, credentials','Visual guidelines — diagram style, table format, callout boxes'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-07.1.3', name: 'Design review cycle schedule — pink, red, gold review timing, reviewer allocation, feedback turnaround expectations',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: 'Reviewers' },
          outputs: [{ name: 'Review cycle schedule', format: 'Schedule within master programme', quality: ['Pink, red, gold review dates set and aligned to master programme','Reviewers allocated per section — independent of writing team','Feedback turnaround time agreed — typically 48 hours for pink/red, 24 for gold','Action resolution windows built into programme'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-07.1.4', name: 'Create compliance checklist and review scorecards — tools for reviewers to assess against evaluation criteria',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Quality Lead', i: null },
          outputs: [{ name: 'Quality plan (activity primary output)', format: 'Quality plan with tools', quality: ['Compliance checklist covers all mandatory requirements from PRD-01','Review scorecards mirror evaluation criteria — reviewers score as the evaluator would','Assessment scale defined and consistent across all reviews','Quality plan signed off by Bid Director'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Quality plan: evaluation weighting analysis, page budgets', format: 'Quality plan document with review tools', quality: ['Page budgets aligned to marks concentration','Writing standards defined and communicated','Review cycle scheduled and resourced','Compliance checklist and review scorecards ready for use'] }]
},

'BM-08': {
  subs: [
    {
      id: 'BM-08.1', name: 'Communications Setup',
      description: 'Establish internal stakeholder communications for the bid',
      tasks: [
        { id: 'BM-08.1.1', name: 'Map bid stakeholders — sponsors, governance panel, subject matter experts, partner contacts — and define communications approach per stakeholder',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Account Manager', i: null },
          outputs: [{ name: 'Stakeholder communications map', format: 'Stakeholder register', quality: ['All internal stakeholders identified — sponsors, governance, SMEs, partners','Communication frequency and channel defined per stakeholder','Escalation path clear — who can make what decisions'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-08.1.2', name: 'Establish decision log — format, ownership, circulation, and review cadence',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Decision log (living document)', format: 'Log / register', quality: ['Format agreed — date, decision, rationale, owner, impact','Circulation list defined — who sees decisions','Accessible to all bid team members','Referenced in governance packs as audit trail'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'BM-08.2', name: 'Ongoing Stakeholder Communications',
      description: 'Maintain stakeholder engagement throughout the bid',
      tasks: [
        { id: 'BM-08.2.1', name: 'Deliver scheduled stakeholder updates — progress, decisions needed, risks, and upcoming milestones',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Bid Board' },
          outputs: [{ name: 'Stakeholder update records', format: 'Update log', quality: ['Updates delivered per stakeholder communications map cadence','Key decisions and escalations highlighted — not buried','Senior stakeholders kept informed without requiring their daily involvement'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-08.2.2', name: 'Maintain decision log — capture all significant bid decisions with rationale, owner, and downstream impact',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Maintained decision log (activity primary output)', format: 'Living document', quality: ['Every significant decision captured within 24 hours','Rationale recorded — not just the decision but why','Impact on downstream activities noted','Governance-ready — can be presented at any gate review'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    }
  ],
  outs: [{ name: 'Stakeholder comms plan, decision log', format: 'Living documents', quality: ['Internal stakeholder map maintained','Communications delivered per agreed cadence','Decision log current and governance-ready','Escalation path operational'] }]
},

'BM-09': {
  subs: [
    {
      id: 'BM-09.1', name: 'Dialogue Preparation',
      description: 'Prepare for each round of competitive dialogue',
      tasks: [
        { id: 'BM-09.1.1', name: 'Develop dialogue strategy per round — objectives, negotiation positions, topics to test, red lines, and desired client reactions',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead / Commercial Lead', i: 'Solution Architect' },
          outputs: [{ name: 'Dialogue strategy document', format: 'Strategy brief per round', quality: ['Objectives for each dialogue session defined — what do we want to learn/achieve?','Negotiation positions pre-agreed with governance where required','Topics mapped to evaluation criteria — what client feedback will improve our score?','Red lines identified — positions we will not concede'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-09.1.2', name: 'Prepare dialogue pack — presentation materials, discussion topics, questions for the client, team briefing and role assignments',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: null },
          outputs: [{ name: 'Dialogue preparation pack', format: 'Presentation and briefing materials', quality: ['Materials tailored to this session\'s objectives','Team roles assigned — who presents, who listens, who takes notes','Questions for the client prepared and prioritised','Dry run completed before each session'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'BM-09.2', name: 'Dialogue Execution & Iteration',
      description: 'Execute dialogue sessions and manage the iterative solution/commercial cycle',
      tasks: [
        { id: 'BM-09.2.1', name: 'Record dialogue outcomes — client feedback, positions tested, agreements reached, and open items per session',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Dialogue session record', format: 'Structured record per session', quality: ['All client feedback captured verbatim where possible','Agreements and positions reached documented','Open items tracked with owners and deadlines','Record distributed to all workstream leads within 24 hours'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-09.2.2', name: 'Drive solution and commercial iteration per dialogue round — update SOL, COM, LEG positions based on dialogue outcomes',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads (SOL/COM/LEG)', i: null },
          outputs: [{ name: 'Iteration tracker (activity primary output)', format: 'Tracker across rounds', quality: ['Each dialogue round\'s impact on solution and commercial positions tracked','Workstream leads confirm updates to their positions after each round','Changes auditable — what changed, why, which dialogue session drove it','Cumulative position evolution visible across all rounds'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Dialogue prep packs, session records, iteration tracker', format: 'Living documents across rounds', quality: ['Strategy prepared per round with pre-agreed positions','Session outcomes recorded and distributed within 24 hours','Solution and commercial iterations tracked across rounds','Governance re-check triggered when positions change materially'] }]
},

'BM-11': {
  subs: [
    {
      id: 'BM-11.1', name: 'Submission Debrief',
      description: 'Capture immediate lessons and team feedback within 48 hours of submission',
      tasks: [
        { id: 'BM-11.1.1', name: 'Conduct structured hot debrief — facilitated session covering what went well, what didn\'t, process bottlenecks, and team wellbeing',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All attending leads', i: null },
          outputs: [{ name: 'Hot debrief notes', format: 'Structured meeting record', quality: ['Held within 48 hours of submission while memory is fresh','All workstream leads contribute — not just bid management perspective','Covers: process, quality, timeline, team dynamics, tools, client interaction','Honest assessment — not a celebration, a learning exercise'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-11.1.2', name: 'Capture immediate process lessons — specific, actionable items that should change for the next bid',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Quality Lead' },
          outputs: [{ name: 'Immediate lessons log (activity primary output)', format: 'Lessons register', quality: ['Each lesson is specific and actionable — not vague "do better next time"','Lessons categorised: process, tooling, resourcing, client management, quality','Owner assigned for each lesson — who takes it forward','Feeds BM-12 for formal lessons learned analysis'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Hot debrief notes, immediate lessons log', format: 'Meeting record and lessons register', quality: ['Debrief held within 48 hours','All workstream perspectives captured','Lessons specific and actionable with owners','Feeds formal lessons learned process'] }]
},

'BM-13': {
  subs: [
    {
      id: 'BM-13.1', name: 'Risk Register Setup',
      description: 'Establish the consolidated bid risk register at bid start',
      tasks: [
        { id: 'BM-13.1.1', name: 'Establish bid risk register — combining process risks, scheduling risks, resource risks, and initial workstream risks from SAL-06',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Risk Manager', i: 'All Workstream Leads' },
          outputs: [{ name: 'Initial bid risk register', format: 'Risk register', quality: ['All risk categories covered: process, schedule, resource, solution, commercial, delivery, legal','Risks scored for probability and impact','Risk owners assigned','Mitigation actions identified for all high/critical risks'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'BM-13.2', name: 'Ongoing Risk Management',
      description: 'Maintain the risk register as a living document throughout the bid',
      tasks: [
        { id: 'BM-13.2.1', name: 'Consolidate workstream risk registers into the single bid risk register at key milestones',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: 'Risk Manager' },
          outputs: [{ name: 'Consolidated risk register', format: 'Living document', quality: ['All workstream risks consolidated — solution (SOL-12), commercial (COM-07), delivery (DEL-01/06), legal (LEG-02)','No duplicate risks across workstreams','Cross-workstream risks identified — risks that span solution + commercial + delivery'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-13.2.2', name: 'Update risk register at each governance gate — refresh scores, close mitigated risks, add new risks, prepare governance summary',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Risk Manager', i: 'Bid Board' },
          outputs: [{ name: 'Governance-ready risk summary', format: 'Summary for governance pack', quality: ['Risk register refreshed before every governance gate','Top risks highlighted with mitigation status','New risks since last gate identified','Risk trend shown — improving, stable, or deteriorating'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-13.2.3', name: 'Manage risk escalation — risks exceeding threshold trigger immediate Bid Director review, not next weekly cycle',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Workstream Leads' },
          outputs: [{ name: 'Risk register (activity primary output)', format: 'Living risk register with escalation log', quality: ['Escalation threshold defined — high probability + high impact = immediate escalation','Escalated risks have documented Bid Director decision','Risk register feeds all governance packs','Archived at bid close as part of lessons learned'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    }
  ],
  outs: [{ name: 'Bid risk & assumptions register (living document)', format: 'Living risk register', quality: ['All workstream risks consolidated','Risk register refreshed at every governance gate','Escalation procedure operational','Top risks visible in weekly progress reports','Feeds governance pack at every gate'] }]
},

'BM-14': {
  subs: [
    {
      id: 'BM-14.1', name: 'Clarification Submission',
      description: 'Submit clarification questions per the agreed strategy',
      tasks: [
        { id: 'BM-14.1.1', name: 'Prepare clarification submissions — format questions per portal requirements, obtain Bid Director approval for strategic questions',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
          outputs: [{ name: 'Formatted clarification submissions', format: 'Portal-ready questions', quality: ['Questions formatted per client portal requirements','Strategic questions approved by Bid Director before submission','Timing aligned to SAL-07 strategy — not all questions submitted at once if staggered approach agreed'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-14.1.2', name: 'Submit clarifications via client portal — manage deadlines, confirm receipt, log submission',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: null, i: null },
          outputs: [{ name: 'Submission log', format: 'Log entry', quality: ['Submitted before client deadline with margin','Receipt confirmed — screenshot or confirmation reference','Submission logged in clarification register'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'BM-14.2', name: 'Response Distribution',
      description: 'Track and distribute clarification responses to workstream leads',
      tasks: [
        { id: 'BM-14.2.1', name: 'Monitor for client responses — check portal regularly, download and log all responses including other bidders\' published questions',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: null, i: null },
          outputs: [{ name: 'Response download log', format: 'Log', quality: ['Portal checked at agreed frequency (minimum daily during active clarification periods)','All responses downloaded and logged — including answers to other bidders\' questions','Version control applied — responses may be updated by client'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'BM-14.2.2', name: 'Triage and distribute responses to relevant workstream leads — flag responses that change assumptions or create new risks',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Clarification response log (activity primary output)', format: 'Distributed response log with impact flags', quality: ['Every response assigned to one or more workstream leads','Responses that change material assumptions flagged for BM-15 impact analysis','Distribution within 24 hours of response receipt','Impact assessment requested from affected workstreams'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    }
  ],
  outs: [{ name: 'Clarification response log with impact assessment', format: 'Living log', quality: ['All submissions tracked with receipt confirmation','Responses distributed within 24 hours','Impact flags assigned to assumption-changing responses','Register feeds BM-15 impact analysis'] }]
},

'BM-15': {
  subs: [
    {
      id: 'BM-15.1', name: 'Impact Assessment',
      description: 'Assess the impact of clarification responses on bid workstreams',
      tasks: [
        { id: 'BM-15.1.1', name: 'Triage flagged clarification responses — assess which workstreams are affected and severity of impact',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: null },
          outputs: [{ name: 'Impact triage assessment', format: 'Assessment per flagged response', quality: ['Each flagged response assessed for: scope change, assumption change, risk change, timeline impact','Affected workstreams identified — may be multiple per response','Severity rated — minor (update text), moderate (revise approach), major (fundamental change)','Major impacts escalated to Bid Director immediately'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-15.1.2', name: 'Assess cumulative impact of all clarification responses — do the collective changes alter the bid\'s competitive position or feasibility?',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead / Commercial Lead', i: null },
          outputs: [{ name: 'Cumulative impact assessment', format: 'Assessment', quality: ['Cumulative effect assessed — are we still competitive after these changes?','PWIN impact considered — do clarifications change our win probability?','Timeline impact assessed — can we still meet submission deadline with these changes?','If cumulative impact is material, triggers BM-16 win strategy refresh'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'BM-15.2', name: 'Workstream Updates',
      description: 'Drive updates across affected workstreams and track resolution',
      tasks: [
        { id: 'BM-15.2.1', name: 'Issue update instructions to affected workstreams — specific changes required, deadline for update, impact on downstream activities',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Affected Workstream Leads' },
          outputs: [{ name: 'Update instructions', format: 'Instruction per workstream', quality: ['Specific changes described — not vague "please review"','Deadline for update aligned to master programme','Downstream dependencies identified — what else changes if this changes'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'BM-15.2.2', name: 'Track resolution of all clarification-driven updates — confirm workstream positions updated, compliance matrix adjusted, risks reassessed',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Updated requirements/assumptions across workstreams (activity primary output)', format: 'Resolution tracker', quality: ['Every update instruction tracked to closure','Compliance matrix (PRD-01) updated to reflect changed requirements','Risk register (BM-13) updated if new risks identified','All updates complete before next governance gate'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    }
  ],
  outs: [{ name: 'Updated requirements/assumptions across workstreams', format: 'Resolution tracker and updated workstream documents', quality: ['Every clarification impact assessed and triaged','Cumulative impact on competitive position evaluated','Workstream updates tracked to closure','Compliance matrix and risk register updated'] }]
},

'BM-16': {
  subs: [
    {
      id: 'BM-16.1', name: 'Strategy Assessment',
      description: 'Reassess the win strategy in light of ITT-phase intelligence',
      tasks: [
        { id: 'BM-16.1.1', name: 'Assess changes since strategy lock — new intelligence from clarifications, dialogue, competitor signals, client behaviour, solution evolution',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Workstream Leads' },
          outputs: [{ name: 'Strategy change assessment', format: 'Assessment document', quality: ['All changes since SAL-06 strategy lock catalogued','Impact on win themes assessed — are they still valid?','Competitive position reassessed — new intelligence about competitors','Client behaviour signals noted — what has the client revealed through clarifications and dialogue?'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-16.1.2', name: 'Refresh win themes and competitive positioning if required — update messaging, solution emphasis, or commercial strategy',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'All Workstream Leads' },
          outputs: [{ name: 'Updated win strategy (if changed)', format: 'Strategy update brief', quality: ['Win themes revalidated or updated with rationale for change','Changes cascaded to all workstream leads','Storyboards (BM-10) updated if win themes changed','Response drafts assessed for alignment to updated themes'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'BM-16.2', name: 'PWIN Requalification',
      description: 'Formal re-qualification checkpoint — confirm continue or stop',
      tasks: [
        { id: 'BM-16.2.1', name: 'Refresh PWIN score based on current intelligence — update qualification assessment with ITT-phase evidence',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
          outputs: [{ name: 'Updated PWIN assessment', format: 'Qualification scorecard', quality: ['PWIN score recalculated with current evidence — not the original pre-ITT assessment','Each category reassessed — customer intimacy, competitive position, solution strength, etc.','Score movement explained — what changed and why','Honest assessment — if PWIN has dropped, say so'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'BM-16.2.2', name: 'Confirm continue/stop decision — formal checkpoint with Bid Director, may trigger governance escalation if PWIN has materially changed',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Bid Board' },
          outputs: [{ name: 'Continue/stop decision record (activity primary output)', format: 'Decision record', quality: ['Formal continue/stop decision documented with rationale','If PWIN has materially declined, governance escalation triggered','If continuing, any strategy adjustments confirmed','Decision record feeds next governance pack'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Win strategy refresh and continue/stop decision', format: 'Strategy update and decision record', quality: ['Strategy reassessed against ITT-phase intelligence','Win themes revalidated or updated','PWIN score refreshed with current evidence','Formal continue/stop decision documented'] }]
},

// ──────────────────────────────────────────────────────────────────
// PRD WORKSTREAM
// ──────────────────────────────────────────────────────────────────

'PRD-01': {
  subs: [
    {
      id: 'PRD-01.1', name: 'Initial Compliance Mapping',
      description: 'Map all ITT requirements to response sections at bid start',
      tasks: [
        { id: 'PRD-01.1.1', name: 'Extract every mandatory and scored requirement from the ITT — pass/fail, scored, informational, contractual',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Legal Lead', i: 'Workstream Leads' },
          outputs: [{ name: 'Requirements register', format: 'Structured register', quality: ['Every requirement extracted — not just the obvious scored questions','Requirement type classified — mandatory pass/fail, scored quality, scored price, informational','Cross-references captured — where requirements appear in multiple ITT documents','Nothing missed — two-person review of ITT documents'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'PRD-01.1.2', name: 'Map each requirement to the response section that addresses it — identify compliance position per requirement',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Solution Architect', i: null },
          outputs: [{ name: 'Initial compliance matrix', format: 'Matrix — requirement × response section', quality: ['Every requirement mapped to at least one response section','Compliance position assessed: compliant, partially compliant, non-compliant, TBD','Non-compliant items flagged immediately to Bid Director','Cross-cutting requirements (e.g. security) mapped to all relevant sections'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'PRD-01.2', name: 'Ongoing Compliance Maintenance',
      description: 'Maintain the compliance matrix as a living document throughout the bid',
      tasks: [
        { id: 'PRD-01.2.1', name: 'Update compliance positions as solution, commercial, and legal workstreams evolve — TBD items resolved, new issues identified',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: null },
          outputs: [{ name: 'Updated compliance matrix', format: 'Living matrix', quality: ['Updated at least weekly during active solution development','TBD positions resolved progressively — target zero TBDs before red review','New requirements from clarifications incorporated','Version controlled — changes tracked'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'PRD-01.2.2', name: 'Report compliance status at governance gates — overall position, outstanding non-compliances, and mitigation plan',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Bid Board' },
          outputs: [{ name: 'Compliance matrix (activity primary output)', format: 'Governance-ready compliance summary', quality: ['Compliance position summarised for governance — % compliant, % TBD, % non-compliant','Non-compliant items have documented mitigation or acceptance rationale','Zero TBDs at final governance gate — everything resolved','Compliance matrix submitted as part of final QA'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    }
  ],
  outs: [{ name: 'Compliance matrix (live)', format: 'Living compliance matrix', quality: ['Every ITT requirement mapped to response section','Compliance position tracked — compliant, partial, non-compliant, TBD','Updated continuously throughout bid','Zero TBDs at submission','Governance-ready summary at every gate'] }]
},

'PRD-03': {
  subs: [
    {
      id: 'PRD-03.1', name: 'Evidence Collection',
      description: 'Compile all evidence items from internal and partner sources',
      tasks: [
        { id: 'PRD-03.1.1', name: 'Compile internal evidence — case studies, CVs, credentials, certifications from evidence library and SOL-10 commissioning',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'SMEs', i: 'Writers' },
          outputs: [{ name: 'Internal evidence pack', format: 'Compiled evidence items', quality: ['All evidence items from SOL-10 matrix sourced or commissioned','Case studies relevant to this opportunity — not generic corporate brochures','CVs current and tailored to this bid\'s requirements','Credentials and certifications verified as current'] }],
          effort: 'Medium', type: 'Parallel' },
        { id: 'PRD-03.1.2', name: 'Collect partner evidence from SUP-05 — partner case studies, CVs, credentials, references',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'Supply Chain Lead', i: 'Partner Lead' },
          outputs: [{ name: 'Partner evidence pack', format: 'Compiled partner evidence', quality: ['All partner evidence items received per SOL-10 requirements','Quality reviewed — partner evidence meets our standards, not just theirs','Gaps identified and chased — partner evidence often arrives late'] }],
          effort: 'Medium', type: 'Parallel' },
      ]
    },
    {
      id: 'PRD-03.2', name: 'Evidence Formatting & QA',
      description: 'Format and quality-assure all evidence for submission',
      tasks: [
        { id: 'PRD-03.2.1', name: 'Format all evidence to ITT requirements — consistent style, correct templates, word/page limits, anonymisation where required',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'DTP', i: null },
          outputs: [{ name: 'Formatted evidence pack', format: 'Submission-ready evidence', quality: ['Consistent formatting across all evidence items — one brand voice','ITT template requirements met (if specified)','Word/page limits respected','Client names anonymised where required by ITT rules'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'PRD-03.2.2', name: 'Quality-assure evidence — relevance, accuracy, currency, and alignment to win themes',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Quality Lead', i: 'Writers' },
          outputs: [{ name: 'Evidence pack (activity primary output)', format: 'QA-complete evidence pack', quality: ['Every evidence item reviewed for relevance to this specific opportunity','Factual accuracy verified — dates, values, outcomes confirmed with source','Currency confirmed — evidence not older than policy threshold (typically 5 years)','Win themes reinforced through evidence selection and presentation'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Evidence pack', format: 'QA-complete evidence pack', quality: ['All required evidence sourced — internal and partner','Formatted to ITT requirements','Quality assured for relevance, accuracy, and currency','Win themes reinforced through evidence selection'] }]
},

'PRD-04': {
  subs: [
    {
      id: 'PRD-04.1', name: 'Commercial Narrative',
      description: 'Produce the written commercial response elements',
      tasks: [
        { id: 'PRD-04.1.1', name: 'Draft commercial response narrative — pricing approach, value proposition, payment mechanism explanation, investment commitment',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Bid Manager', i: 'Solution Architect' },
          outputs: [{ name: 'Commercial response narrative', format: 'Draft document', quality: ['Explains pricing approach in client-friendly language — not just numbers','Value proposition articulated — why this price represents best value','Payment mechanism described clearly','Investment commitments and efficiency trajectory explained'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'PRD-04.1.2', name: 'Assemble pricing schedules from COM-06 locked model — populate ITT pricing templates, cross-reference to narrative',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Bid Manager' },
          outputs: [{ name: 'Completed pricing schedules', format: 'ITT pricing templates', quality: ['All ITT pricing templates populated correctly','Numbers reconcile between schedules and financial model','Cross-references to narrative sections correct','Arithmetic verified independently'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'PRD-04.2', name: 'Commercial Response Package',
      description: 'Package and quality-assure the complete commercial submission',
      tasks: [
        { id: 'PRD-04.2.1', name: 'Quality-assure complete commercial response — narrative consistency with pricing, compliance with ITT commercial requirements, no contradictions',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Legal Lead' },
          outputs: [{ name: 'Pricing response documents (activity primary output)', format: 'Complete commercial submission package', quality: ['Narrative and numbers tell the same story','All ITT commercial requirements addressed','No contradictions between commercial response and technical response','Independent arithmetic check completed','Commercial response signed off by Commercial Lead and Bid Director'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Pricing response documents', format: 'Complete commercial submission package', quality: ['Narrative explains pricing approach clearly','All pricing schedules populated and verified','Narrative and numbers consistent','ITT commercial requirements met','Independently checked'] }]
},

'PRD-05': {
  subs: [
    {
      id: 'PRD-05.1', name: 'Pink Review Execution',
      description: 'Conduct the pink review — assessing storyboard quality and win theme integration',
      tasks: [
        { id: 'PRD-05.1.1', name: 'Brief review panel — evaluation criteria, scoring approach, win themes, what to look for, scorecard format',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Reviewers' },
          outputs: [{ name: 'Reviewer briefing record', format: 'Briefing document', quality: ['Reviewers understand the evaluation criteria they are simulating','Win themes communicated — reviewers check for theme penetration','Scorecard format explained — consistent scoring across all reviewers','Review timeline and feedback format agreed'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'PRD-05.1.2', name: 'Conduct pink review — reviewers assess storyboard structure, key messages, win theme integration, evidence placement, and scoring potential',
          raci: { r: 'Independent Reviewers', a: 'Bid Director', c: 'Bid Manager', i: 'Writers' },
          outputs: [{ name: 'Pink review scorecards', format: 'Scorecard per section', quality: ['Every section scored against evaluation criteria','Win theme penetration assessed — are themes landing where the marks are?','Evidence gaps identified — where is the response weak on proof?','Structural issues flagged — does the response flow logically?','Scores benchmarked — would this score well against evaluation criteria?'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'PRD-05.2', name: 'Pink Action Resolution',
      description: 'Resolve pink review actions before writers begin drafting',
      tasks: [
        { id: 'PRD-05.2.1', name: 'Consolidate and prioritise pink review actions — categorise by severity and impact on scoring potential',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Writers' },
          outputs: [{ name: 'Prioritised action list', format: 'Action tracker', quality: ['All reviewer feedback consolidated — duplicates merged','Actions prioritised: critical (blocks drafting), important (improves score), minor (nice to have)','Owner assigned per action','Deadline set — all critical actions resolved before writers begin'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'PRD-05.2.2', name: 'Resolve pink actions — update storyboards, adjust structure, reallocate evidence, brief writers on changes',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Writers' },
          outputs: [{ name: 'Pink review scorecard & actions resolved (activity primary output)', format: 'Updated storyboards with action closure record', quality: ['All critical actions resolved and verified','Storyboards updated to reflect changes','Writers briefed on revised approach per section','Action closure confirmed — not just marked done, but change verified'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Pink review scorecard & actions', format: 'Scorecards and updated storyboards', quality: ['All sections reviewed against evaluation criteria','Win theme integration assessed','Actions prioritised and resolved before drafting begins','Writers briefed on review outcomes'] }]
},

'PRD-06': {
  subs: [
    {
      id: 'PRD-06.1', name: 'Red Review Execution',
      description: 'Conduct evaluator-simulation review of complete draft response',
      tasks: [
        { id: 'PRD-06.1.1', name: 'Brief red team reviewers — provide evaluation criteria, scoring methodology, competitor intelligence, and win themes for context',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Reviewers' },
          outputs: [{ name: 'Red team briefing', format: 'Briefing pack', quality: ['Reviewers briefed on evaluation methodology — they must score as the client would','Competitor context provided — what are we competing against?','Win themes reinforced — reviewers check if themes are compelling and differentiated','Scoring scale aligned to ITT evaluation scale'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'PRD-06.1.2', name: 'Conduct red review — evaluator simulation scoring each section, assessing compliance, win theme penetration, evidence strength, and readability',
          raci: { r: 'Independent Reviewers', a: 'Bid Director', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Red review scorecards', format: 'Scorecard per section with comments', quality: ['Every section scored using the client\'s evaluation methodology','Compliance check — does the response address every requirement?','Win theme assessment — are differentiators compelling and evidenced?','Evidence strength assessed — proof points credible and relevant?','Readability check — can a non-specialist evaluator understand and score this?','Overall predicted score per section provided'] }],
          effort: 'High', type: 'Sequential' },
      ]
    },
    {
      id: 'PRD-06.2', name: 'Red Action Resolution',
      description: 'Resolve red review actions — writers revise, bid manager tracks to closure',
      tasks: [
        { id: 'PRD-06.2.1', name: 'Consolidate red review feedback and prioritise actions — critical actions must be resolved before gold review',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Writers' },
          outputs: [{ name: 'Red review action plan', format: 'Prioritised action tracker', quality: ['All feedback consolidated across reviewers','Actions categorised: score-critical (must fix), score-improving (should fix), cosmetic (if time permits)','Realistic timeline for resolution — aligned to gold review date','No action without an owner and deadline'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'PRD-06.2.2', name: 'Drive section revisions — writers update based on red review feedback, bid manager verifies critical actions are genuinely resolved',
          raci: { r: 'Writers', a: 'Bid Manager', c: null, i: 'Reviewers' },
          outputs: [{ name: 'Red review scorecard & actions resolved (activity primary output)', format: 'Revised sections with action closure record', quality: ['All score-critical actions resolved and verified — not just marked done','Revised sections checked against original reviewer comments','Score improvement validated — does the revision address the reviewer\'s concern?','Action closure record maintained for governance audit trail'] }],
          effort: 'High', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Red review scorecard & actions resolved', format: 'Scorecards, revised sections, action closure record', quality: ['Evaluator-simulation review completed for all sections','Predicted scores per section documented','All score-critical actions resolved before gold review','Revisions verified against original feedback'] }]
},

'PRD-07': {
  subs: [
    {
      id: 'PRD-07.1', name: 'Gold Review Preparation',
      description: 'Prepare the complete response for executive quality review',
      tasks: [
        { id: 'PRD-07.1.1', name: 'Assemble complete response document for gold review — all sections including executive summary, evidence, pricing, and appendices',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Bid Coordinator', i: null },
          outputs: [{ name: 'Gold review package', format: 'Complete assembled response', quality: ['All sections present and in final order','Red review actions confirmed as resolved','Executive summary drafted and included','Cross-references checked — no broken references between sections'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'PRD-07.2', name: 'Gold Review Execution & Sign-off',
      description: 'Executive review and final sign-off to proceed to submission',
      tasks: [
        { id: 'PRD-07.2.1', name: 'Conduct gold review — executive assessment of compliance, completeness, tone, win strategy coherence, and overall quality',
          raci: { r: 'Senior Independent Review Panel', a: 'Bid Director', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Gold review assessment', format: 'Executive assessment', quality: ['Compliance confirmed — all requirements addressed','Completeness verified — no missing sections or documents','Tone appropriate — consistent, professional, client-appropriate','Win strategy coherent throughout — themes land consistently across all sections','Commercial and technical narrative aligned — no contradictions'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'PRD-07.2.2', name: 'Resolve gold review actions and obtain sign-off — any remaining issues must be resolved or accepted before proceeding',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Writers' },
          outputs: [{ name: 'Gold review scorecard & sign-off (activity primary output)', format: 'Sign-off record with any residual actions', quality: ['All gold review actions resolved or formally accepted by Bid Director','Sign-off obtained — Bid Director confirms response is ready for final QA','Any conditions noted — e.g. "proceed subject to executive summary revision"','Sign-off feeds GOV-04 executive approval'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Gold review scorecard & sign-off', format: 'Executive sign-off record', quality: ['Executive quality review completed','Compliance and completeness confirmed','Win strategy coherence validated','All actions resolved or formally accepted','Bid Director sign-off obtained'] }]
},

'PRD-08': {
  subs: [
    {
      id: 'PRD-08.1', name: 'Document Formatting',
      description: 'Apply professional formatting, branding, and layout to the final document',
      tasks: [
        { id: 'PRD-08.1.1', name: 'Apply corporate template, branding, and professional layout — headers, footers, table of contents, page numbering, graphics',
          raci: { r: 'DTP', a: 'Bid Manager', c: 'Brand/Design', i: null },
          outputs: [{ name: 'Formatted document', format: 'Professionally formatted response', quality: ['Corporate template applied consistently','Table of contents generated and page-accurate','Headers/footers include document reference, version, page numbers','Graphics and diagrams professionally rendered and correctly placed','Page limits met (if applicable)'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'PRD-08.1.2', name: 'Verify all cross-references, hyperlinks, and figure/table numbering are correct',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: null, i: null },
          outputs: [{ name: 'Cross-reference check', format: 'Checklist', quality: ['All internal cross-references resolve correctly','Figure and table numbering sequential and accurate','Hyperlinks functional (if electronic submission)','Appendix references correct'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'PRD-08.2', name: 'Final Quality Assurance',
      description: 'Final proof-read and quality check before submission',
      tasks: [
        { id: 'PRD-08.2.1', name: 'Proof-read complete document — spelling, grammar, consistency of terminology, factual accuracy of repeated numbers/dates',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: null, i: null },
          outputs: [{ name: 'Proof-read checklist', format: 'Checklist', quality: ['Full document proof-read by someone who did not write it','Terminology consistent throughout — same thing called the same name everywhere','Numbers and dates consistent — TCV, contract dates, headcount match across all mentions','Company and client names correct throughout'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'PRD-08.2.2', name: 'Final compliance verification — every mandatory requirement addressed, all documents present, all formats correct',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: null },
          outputs: [{ name: 'QA checklist complete (activity primary output)', format: 'Signed QA checklist', quality: ['Compliance matrix verified — every requirement addressed in the response','All required documents present in submission package','File formats match ITT requirements (PDF, Excel, etc.)','File sizes within portal limits','QA checklist signed by Bid Manager and Bid Director'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'QA checklist complete', format: 'Signed QA checklist with formatted document', quality: ['Professional formatting applied','Cross-references verified','Proof-read completed by independent reviewer','Compliance verified against full requirements list','QA checklist signed off by Bid Manager and Bid Director'] }]
},

'PRD-09': {
  subs: [
    {
      id: 'PRD-09.1', name: 'Pre-Submission Checks',
      description: 'Final checks before upload',
      tasks: [
        { id: 'PRD-09.1.1', name: 'Conduct final pre-submission check — all documents present, correct versions, file names per ITT requirements, sizes within limits',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Bid Coordinator', i: null },
          outputs: [{ name: 'Pre-submission checklist', format: 'Checklist', quality: ['Document inventory matches ITT requirements — nothing missing','File versions are final — no draft watermarks, no tracked changes','File names match ITT naming requirements','File sizes within portal upload limits'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'PRD-09.1.2', name: 'Obtain final submission authority — confirm all governance approvals in place (GOV-05), all sign-offs complete',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Bid Board' },
          outputs: [{ name: 'Submission authority confirmation', format: 'Sign-off record', quality: ['GOV-05 final submission authority confirmed','All functional sign-offs verified','Any conditions from governance approvals confirmed as met','Authority to submit documented'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'PRD-09.2', name: 'Submission Execution',
      description: 'Upload and confirm receipt',
      tasks: [
        { id: 'PRD-09.2.1', name: 'Upload submission to client portal — manage upload process, handle any technical issues, obtain confirmation receipt',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'IT Support', i: 'Bid Director' },
          outputs: [{ name: 'Upload confirmation', format: 'Portal receipt / screenshot', quality: ['Uploaded minimum 4 hours before deadline — contingency for technical issues','Confirmation receipt obtained from portal','Screenshot evidence of successful upload captured','All documents verified as uploaded and accessible'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'PRD-09.2.2', name: 'Archive submission package — complete copy of everything submitted, stored per document management policy',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: null, i: null },
          outputs: [{ name: 'Submission confirmation receipt (activity primary output)', format: 'Archive with confirmation', quality: ['Complete submission archived — exact copies of what was submitted','Archive includes: confirmation receipt, document inventory, submission timestamp','Stored per corporate retention policy','Accessible for post-submission clarifications, BAFO preparation, and lessons learned'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Submission confirmation receipt', format: 'Confirmation with archived submission', quality: ['All pre-submission checks passed','Submission authority confirmed','Uploaded with contingency time before deadline','Confirmation receipt obtained','Complete submission archived'] }]
},

// ──────────────────────────────────────────────────────────────────
// GOV WORKSTREAM
// ──────────────────────────────────────────────────────────────────

'GOV-01': {
  subs: [
    {
      id: 'GOV-01.1', name: 'Pack Preparation',
      description: 'Prepare the governance pack for pursuit approval',
      tasks: [
        { id: 'GOV-01.1.1', name: 'Assemble pursuit approval pack — capture plan summary, PWIN score, bid mandate, resource and cost estimate, key risks, competitive assessment',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
          outputs: [{ name: 'Pursuit approval pack', format: 'Governance pack (qualification tier)', quality: ['PWIN qualification assessment included with AI assurance findings','Bid mandate with resource and cost estimate','Key risks and mitigations summarised','Competitive landscape assessment included','IC trigger criteria assessed'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'GOV-01.1.2', name: 'Prepare recommendation — pursue, pursue with conditions, or walk away — with supporting rationale',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Capture Lead', i: null },
          outputs: [{ name: 'Recommendation brief', format: 'Section within governance pack', quality: ['Clear recommendation with rationale','Conditions specified if conditional approval sought','Risks acknowledged — not an optimistic pitch','Alternative scenarios considered — what happens if we don\'t pursue?'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'GOV-01.2', name: 'Governance Review',
      description: 'Present to governance panel and capture the decision',
      tasks: [
        { id: 'GOV-01.2.1', name: 'Present pursuit approval pack to governance panel — brief the opportunity, present recommendation, facilitate debate',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Governance presentation record', format: 'Meeting record', quality: ['Presentation delivered to quorate governance panel','Key concerns from panel captured','Panel questions and challenges documented'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'GOV-01.2.2', name: 'Capture governance decision — approve, approve with conditions, reject — with conditions and actions',
          raci: { r: 'Bid Manager', a: 'Senior Responsible Executive', c: null, i: 'Bid Board' },
          outputs: [{ name: 'Pursuit approval decision record (activity primary output)', format: 'Formal decision record', quality: ['Decision formally recorded — approve / approve with conditions / reject','Conditions specified with owners and deadlines','Actions from governance discussion captured','Decision communicated to bid team within 24 hours'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Pursuit approval decision record', format: 'Formal decision record', quality: ['Governance pack presented to quorate panel','Clear decision recorded — approve / conditions / reject','Conditions have owners and deadlines','Decision communicated to bid team'] }]
},

'GOV-02': {
  subs: [
    {
      id: 'GOV-02.1', name: 'Solution Review Preparation',
      description: 'Prepare governance pack for solution and strategy review',
      tasks: [
        { id: 'GOV-02.1.1', name: 'Assemble solution review pack — solution summary, win strategy alignment, risk position, partner strategy, delivery readiness, preliminary financials',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: null },
          outputs: [{ name: 'Solution review pack', format: 'Governance pack (solution tier)', quality: ['Solution approach summarised with key design decisions','Win strategy alignment demonstrated — solution reflects win themes','Risk position updated from GOV-01','Partner strategy and teaming status included','Preliminary financial position presented'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'GOV-02.1.2', name: 'Prepare actions from GOV-01 status — demonstrate all conditions from pursuit approval have been met or addressed',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: null },
          outputs: [{ name: 'GOV-01 action status', format: 'Action tracker', quality: ['Every GOV-01 condition addressed — closed or with update','Open items have clear plan and timeline','Material changes since GOV-01 highlighted'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'GOV-02.2', name: 'Solution Governance Review',
      description: 'Present solution to governance panel and capture decision',
      tasks: [
        { id: 'GOV-02.2.1', name: 'Present solution and strategy to governance panel — demonstrate the solution is credible, competitive, and deliverable',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Solution Architect', i: 'Bid Manager' },
          outputs: [{ name: 'Solution governance presentation', format: 'Meeting record', quality: ['Solution credibility challenged and defended','Delivery feasibility assessed by panel','Competitive differentiation articulated','Panel concerns documented'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'GOV-02.2.2', name: 'Capture solution review decision — approve solution direction, approve with conditions, or require redesign',
          raci: { r: 'Bid Manager', a: 'Senior Responsible Executive', c: null, i: 'All Workstream Leads' },
          outputs: [{ name: 'Solution review decision record (activity primary output)', format: 'Formal decision record', quality: ['Decision recorded — approve / conditions / redesign','Conditions specific and actionable','If redesign required, scope and timeline agreed','Decision communicated to bid team'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Solution review decision record', format: 'Formal decision record', quality: ['Solution credibility validated by governance panel','GOV-01 conditions addressed','Decision recorded with any new conditions','Communicated to bid team'] }]
},

'GOV-03': {
  subs: [
    {
      id: 'GOV-03.1', name: 'Commercial Review Preparation',
      description: 'Prepare governance pack for pricing and risk review',
      tasks: [
        { id: 'GOV-03.1.1', name: 'Assemble pricing review pack — P&L, margin analysis, sensitivity analysis, risk tornado, partner terms, contract terms, price-to-win position',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Bid Manager' },
          outputs: [{ name: 'Pricing review pack', format: 'Governance pack (submission tier — commercial sections)', quality: ['Full financial model presentation — P&L, margins, NPV/IRR','Sensitivity analysis completed — margin at different scenarios','Risk tornado per category with probability-weighted outcomes','Contract terms summarised with negotiation positions','Price-to-win analysis included with competitor intelligence'] }],
          effort: 'High', type: 'Sequential' },
        { id: 'GOV-03.1.2', name: 'Prepare pricing recommendation — recommended price position with rationale, alternative scenarios considered',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Capture Lead', i: null },
          outputs: [{ name: 'Pricing recommendation', format: 'Recommendation brief', quality: ['Clear price recommendation with rationale','Alternative pricing scenarios presented with trade-offs','Risk-adjusted margin assessment included','Competitive position of recommended price assessed'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'GOV-03.2', name: 'Commercial Governance Review',
      description: 'Present pricing to governance panel and obtain pricing approval',
      tasks: [
        { id: 'GOV-03.2.1', name: 'Present pricing position to governance panel — defend margin, explain risk position, demonstrate competitive viability',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance Director', i: 'Bid Manager' },
          outputs: [{ name: 'Pricing governance presentation', format: 'Meeting record', quality: ['Margin position defended with evidence','Risk position challenged and responded to','Competitive viability demonstrated','Panel concerns on contract terms addressed'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'GOV-03.2.2', name: 'Capture pricing approval — approved price, margin parameters, any conditions, delegated authority for final adjustments',
          raci: { r: 'Bid Manager', a: 'Senior Responsible Executive', c: null, i: 'Commercial Lead' },
          outputs: [{ name: 'Pricing decision record (activity primary output)', format: 'Formal pricing approval record', quality: ['Approved price position documented','Margin floor confirmed — minimum acceptable margin','Conditions specified — e.g. subject to partner terms finalisation','Delegated authority for minor adjustments defined — who can approve what range without re-gate'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Pricing decision record + approved price', format: 'Formal pricing approval', quality: ['Pricing reviewed with full financial analysis','Risk position challenged and accepted','Approved price and margin floor documented','Delegated authority for minor adjustments defined'] }]
},

'GOV-04': {
  subs: [
    {
      id: 'GOV-04.1', name: 'Executive Pack Preparation',
      description: 'Prepare the comprehensive executive approval pack',
      tasks: [
        { id: 'GOV-04.1.1', name: 'Assemble executive approval pack — bid summary, approved price, margin, risk position, quality review outcomes, compliance status, recommendation to submit',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Commercial Lead / Legal Lead', i: null },
          outputs: [{ name: 'Executive approval pack', format: 'Governance pack (submission tier)', quality: ['All prior gate decisions referenced — GOV-01, GOV-02, GOV-03','Quality review outcomes summarised — pink, red, gold scores','Compliance status confirmed — from PRD-01 matrix','All outstanding actions and conditions from prior gates addressed','Functional sign-offs obtained'] }],
          effort: 'High', type: 'Sequential' },
      ]
    },
    {
      id: 'GOV-04.2', name: 'Executive Approval',
      description: 'Obtain executive sign-off at each required tier',
      tasks: [
        { id: 'GOV-04.2.1', name: 'Present at first approval tier (BU level) — secure business unit approval to submit',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'BU approval record', format: 'Decision record', quality: ['BU-level approval obtained or conditions set','Concerns documented with agreed resolution plan','If conditional, conditions have deadlines before submission'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'GOV-04.2.2', name: 'Present at additional tiers if required (ExCo / Board) — escalation for bids exceeding delegated authority thresholds',
          raci: { r: 'Bid Director', a: 'Board', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Executive approval decision record(s) (activity primary output)', format: 'Formal approval record per tier', quality: ['Approval obtained at all required tiers','If IC-trigger criteria met, Investment Committee approval obtained','All conditions across all tiers consolidated into single action tracker','Final approval authority to submit confirmed'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Executive approval decision record(s)', format: 'Formal approval at all required tiers', quality: ['All required approval tiers completed','Conditions consolidated and tracked','Investment Committee approval obtained if triggered','Final authority to submit confirmed'] }]
},

'GOV-05': {
  subs: [
    {
      id: 'GOV-05.1', name: 'Final Authority Check',
      description: 'Confirm all approvals are in place before submission',
      tasks: [
        { id: 'GOV-05.1.1', name: 'Verify all governance approvals are complete — GOV-01 through GOV-04 decisions confirmed, all conditions met',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: null },
          outputs: [{ name: 'Governance completion checklist', format: 'Checklist', quality: ['Every governance gate decision referenced','All conditions from all gates confirmed as met','No outstanding governance actions remain open','Checklist signed by Bid Manager'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'GOV-05.1.2', name: 'Confirm QA is complete — PRD-08 final QA checklist signed, all documents submission-ready',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: null },
          outputs: [{ name: 'QA confirmation', format: 'Sign-off reference', quality: ['PRD-08 QA checklist signed and referenced','Compliance matrix shows 100% addressed','All documents in final format'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'GOV-05.1.3', name: 'Grant final submission authority — Bid Director confirms everything is in place, authorises PRD-09 to proceed',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Submission authority confirmation (activity primary output)', format: 'Formal authority record', quality: ['Bid Director grants submission authority','Timestamp recorded — authority granted before submission window opens','Any last-minute conditions acknowledged','Authority communicated to submission team (PRD-09)'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Submission authority confirmation', format: 'Formal authority record', quality: ['All governance approvals verified complete','QA confirmed complete','Final submission authority granted by Bid Director','Communicated to submission team'] }]
},

'GOV-06': {
  subs: [
    {
      id: 'GOV-06.1', name: 'Legal Review Preparation',
      description: 'Prepare legal and contractual review pack',
      tasks: [
        { id: 'GOV-06.1.1', name: 'Assemble legal review pack — contract positions summary, risk allocation matrix, TUPE assessment, data protection, subcontractor terms, insurance',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Bid Manager' },
          outputs: [{ name: 'Legal review pack', format: 'Legal summary pack', quality: ['Contract mark-up positions summarised per clause area','Risk allocation matrix showing accepted vs contested positions','TUPE, data protection, and insurance assessments included','Subcontractor terms alignment assessed — back-to-back status','Areas requiring negotiation or client dialogue identified'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'GOV-06.1.2', name: 'Prepare legal risk summary — positions accepted, positions contested, residual legal risk, and recommendation',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: null, i: 'Commercial Lead' },
          outputs: [{ name: 'Legal risk summary', format: 'Risk summary', quality: ['Each contested position explained with business impact','Residual legal risk quantified where possible','Recommendation: accept, negotiate further, or escalate','Comparison to corporate risk appetite thresholds'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'GOV-06.2', name: 'Legal Governance Review',
      description: 'Present legal positions to governance panel and capture decision',
      tasks: [
        { id: 'GOV-06.2.1', name: 'Present legal and contractual positions to governance panel — explain risk, defend positions, advise on negotiation strategy',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Legal governance presentation', format: 'Meeting record', quality: ['Key legal risks presented and debated','Panel understands what risk is being accepted','Negotiation strategy for contested positions endorsed'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'GOV-06.2.2', name: 'Capture legal review decision — positions approved, negotiation mandates granted, risk acceptance documented',
          raci: { r: 'Bid Manager', a: 'Senior Responsible Executive', c: 'Legal Lead', i: 'Commercial Lead' },
          outputs: [{ name: 'Legal review decision record (activity primary output)', format: 'Formal decision record', quality: ['Contract positions approved by governance panel','Negotiation mandates granted for contested areas','Risk acceptance documented for positions accepted as-is','Any conditions for post-submission negotiation defined'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Legal review decision record', format: 'Formal decision record', quality: ['Legal positions reviewed by governance panel','Negotiation mandates granted','Risk acceptance documented','Feeds GOV-04 executive approval and POST-07 contract negotiation'] }]
},

// ──────────────────────────────────────────────────────────────────
// POST WORKSTREAM
// ──────────────────────────────────────────────────────────────────

'POST-01': {
  subs: [
    {
      id: 'POST-01.1', name: 'Presentation Design',
      description: 'Design the presentation narrative and structure',
      tasks: [
        { id: 'POST-01.1.1', name: 'Design presentation narrative — key messages aligned to win themes, tailored to evaluation panel, consistent with submitted proposal',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect', i: 'Presenting Team' },
          outputs: [{ name: 'Presentation narrative framework', format: 'Outline with key messages', quality: ['Narrative aligned to win themes — not a proposal summary but a persuasion framework','Tailored to known evaluation panel members — speaks to their concerns','Consistent with submitted proposal — no new commitments or contradictions','Clear structure: opening impact, proof points, differentiation, call to action'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-01.1.2', name: 'Identify and brief presenting team — assign roles (lead presenter, technical, commercial, Q&A support)',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Bid Manager', i: 'Presenting Team' },
          outputs: [{ name: 'Presenting team brief', format: 'Role assignments and briefing', quality: ['Presenting team selected for credibility with this client','Roles assigned — who presents each section, who handles Q&A','Team briefed on evaluation criteria and what the panel is looking for','Presenting team includes people the client will work with — not just senior bid team'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'POST-01.2', name: 'Materials Development',
      description: 'Develop presentation materials including slides, notes, and Q&A preparation',
      tasks: [
        { id: 'POST-01.2.1', name: 'Develop presentation slides — visual, compelling, minimal text, supporting not duplicating the spoken narrative',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'DTP', i: 'Presenting Team' },
          outputs: [{ name: 'Presentation deck', format: 'Slide deck', quality: ['Slides support the narrative — visual evidence, not text-heavy bullets','Branding consistent with submitted proposal','Within time allocation — timed per section','Key proof points visualised — data, diagrams, evidence'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-01.2.2', name: 'Prepare Q&A pack — anticipated questions with prepared answers, difficult questions with agreed positions, panel-specific concerns',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: 'Presenting Team' },
          outputs: [{ name: 'Q&A preparation pack (activity primary output)', format: 'Structured Q&A pack with speaker notes', quality: ['Top 30-50 anticipated questions prepared with model answers','Difficult questions identified — pricing challenges, risk concerns, past performance','Agreed positions for sensitive topics — who answers, what we say, what we don\'t say','Panel-specific questions anticipated based on known concerns'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Presentation deck, speaker notes, narrative', format: 'Complete presentation package', quality: ['Narrative aligned to win themes and evaluation criteria','Presenting team briefed and role-assigned','Slides visual and compelling','Q&A pack comprehensive with difficult questions prepared'] }]
},

'POST-02': {
  subs: [
    {
      id: 'POST-02.1', name: 'Rehearsal Programme',
      description: 'Structured rehearsal cycle with feedback and iteration',
      tasks: [
        { id: 'POST-02.1.1', name: 'Conduct first rehearsal — full run-through with timer, simulated panel, feedback on content, delivery, and timing',
          raci: { r: 'Presenting Team', a: 'Bid Director', c: 'Presentation Coach', i: 'Bid Manager' },
          outputs: [{ name: 'First rehearsal debrief', format: 'Feedback notes', quality: ['Full presentation run against timer','Feedback on: content clarity, delivery confidence, timing, visual impact','Q&A simulation included — test responses to difficult questions','Specific improvement actions per presenter identified'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-02.1.2', name: 'Iterate presentation based on rehearsal feedback — revise content, refine delivery, adjust timing',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Presenting Team', i: null },
          outputs: [{ name: 'Revised presentation materials', format: 'Updated deck, notes, Q&A pack', quality: ['All rehearsal actions addressed','Timing adjusted to fit within allocation','Weak sections strengthened — content or delivery','Q&A responses refined based on rehearsal experience'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'POST-02.1.3', name: 'Conduct final dress rehearsal — complete simulation of presentation environment, timing, Q&A, and handover',
          raci: { r: 'Presenting Team', a: 'Bid Director', c: 'Presentation Coach', i: null },
          outputs: [{ name: 'Rehearsal debrief notes (activity primary output)', format: 'Final readiness assessment', quality: ['Full simulation completed — as close to actual conditions as possible','Team confident and prepared — no major concerns remaining','Timing confirmed within allocation','Final Q&A preparation verified — team comfortable with difficult questions'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Rehearsal debrief notes, revised deck, Q&A prep', format: 'Rehearsal outputs', quality: ['Minimum two rehearsals completed','All feedback actions addressed','Team confident and prepared','Timing verified within allocation'] }]
},

'POST-03': {
  subs: [
    {
      id: 'POST-03.1', name: 'Presentation Delivery',
      description: 'Deliver the bid presentation to the evaluation panel',
      tasks: [
        { id: 'POST-03.1.1', name: 'Final team briefing — logistics, roles, last-minute intelligence, contingency plan if technology fails',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Presenting Team' },
          outputs: [{ name: 'Pre-presentation briefing', format: 'Briefing record', quality: ['Logistics confirmed — venue, time, technology, access','Roles reconfirmed — who presents what, who handles Q&A','Any last-minute intelligence shared — client mood, panel changes','Contingency plan confirmed — what if projector fails, key person unavailable'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'POST-03.1.2', name: 'Deliver presentation to evaluation panel — present, manage Q&A, observe panel reactions',
          raci: { r: 'Presenting Team', a: 'Bid Director', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Presentation delivered', format: 'Delivery record', quality: ['Presentation delivered within time allocation','Q&A handled confidently — no commitments beyond submitted proposal','Panel reactions observed and noted'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'POST-03.1.3', name: 'Capture post-presentation intelligence — panel reactions, follow-up questions, client signals, competitive intelligence',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Presenting Team', i: 'Capture Lead' },
          outputs: [{ name: 'Presentation delivered, Q&A record (activity primary output)', format: 'Intelligence debrief', quality: ['Team debrief conducted immediately after presentation','Panel reactions documented — positive signals, concerns, unexpected questions','Follow-up questions recorded — may indicate evaluation focus areas','Competitive intelligence captured — any client comments about other presentations','Intelligence feeds POST-04/05 if clarifications or BAFO follow'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Presentation delivered, Q&A record', format: 'Delivery record and intelligence debrief', quality: ['Presentation delivered within time allocation','Q&A handled without unintended commitments','Panel reactions and intelligence captured','Team debrief completed immediately'] }]
},

'POST-04': {
  subs: [
    {
      id: 'POST-04.1', name: 'Clarification Receipt & Triage',
      description: 'Receive and triage post-submission clarification requests',
      tasks: [
        { id: 'POST-04.1.1', name: 'Monitor for and receive post-submission clarification requests from client — log and triage by urgency and workstream',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Workstream Leads' },
          outputs: [{ name: 'Clarification request log', format: 'Log with triage', quality: ['All requests logged with receipt timestamp','Triage: urgency (deadline-driven), workstream assignment, complexity assessment','Requests that imply evaluation concerns flagged for strategic attention','Requests distributed to workstream leads within 24 hours'] }],
          effort: 'Low', type: 'Parallel' },
        { id: 'POST-04.1.2', name: 'Assess clarification requests for strategic signals — what is the client really asking, and what does it tell us about our competitive position?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Bid Manager', i: null },
          outputs: [{ name: 'Strategic assessment of clarifications', format: 'Assessment brief', quality: ['Each clarification assessed for strategic significance — not just answer the question','Patterns identified — are clarifications focused on a particular area of weakness?','Competitive intelligence extracted — are these questions being asked of all bidders or just us?','Strategic response approach agreed — factual vs opportunity to strengthen position'] }],
          effort: 'Low', type: 'Parallel' },
      ]
    },
    {
      id: 'POST-04.2', name: 'Response Drafting & Submission',
      description: 'Draft, review, and submit clarification responses',
      tasks: [
        { id: 'POST-04.2.1', name: 'Draft clarification responses — technically accurate, consistent with submitted proposal, strategically framed',
          raci: { r: 'Workstream Leads (per topic)', a: 'Bid Director', c: 'Bid Manager', i: null },
          outputs: [{ name: 'Draft clarification responses', format: 'Response documents', quality: ['Responses factually accurate and technically correct','Consistent with submitted proposal — no contradictions or new commitments','Strategically framed — answers the question while reinforcing win themes where possible','Reviewed by at least two people before submission'] }],
          effort: 'Medium', type: 'Parallel' },
        { id: 'POST-04.2.2', name: 'Review, approve, and submit clarification responses within client deadlines',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: null },
          outputs: [{ name: 'Clarification log, submitted responses (activity primary output)', format: 'Submitted responses with log', quality: ['All responses approved by Bid Director before submission','Submitted before client deadline with margin','Submission logged with confirmation receipt','Responses archived alongside original submission'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Clarification log, submitted responses, updated risk log', format: 'Clarification management outputs', quality: ['All clarification requests triaged and assigned','Strategic significance assessed','Responses consistent with submitted proposal','Submitted within deadlines with approval'] }]
},

'POST-05': {
  subs: [
    {
      id: 'POST-05.1', name: 'BAFO Strategy',
      description: 'Develop the BAFO strategy — what to change and what to hold',
      tasks: [
        { id: 'POST-05.1.1', name: 'Assess BAFO context — what intelligence do we have about our competitive position, what has the client signalled, what leverage do we have?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Bid Manager' },
          outputs: [{ name: 'BAFO context assessment', format: 'Assessment brief', quality: ['Competitive position assessed — are we winning, losing, or neck-and-neck?','Client signals analysed — what has the client told us or implied through clarifications?','Leverage identified — what can we offer that strengthens our position?','Risk of over-conceding assessed — how far can we move without undermining margin or deliverability?'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-05.1.2', name: 'Develop BAFO strategy — price adjustments, solution refinements, commercial concessions, and non-price value-adds',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Solution Architect / Capture Lead', i: 'Bid Manager' },
          outputs: [{ name: 'BAFO strategy document', format: 'Strategy brief with scenarios', quality: ['Price adjustment strategy defined — how much, where from, what trade-offs','Solution refinements identified — any improvements that strengthen position without cost','Commercial concessions prepared — payment terms, risk sharing, performance guarantees','Non-price value-adds identified — innovation, social value, partnership investment'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'POST-05.2', name: 'BAFO Preparation',
      description: 'Prepare the revised pricing and solution elements for BAFO submission',
      tasks: [
        { id: 'POST-05.2.1', name: 'Prepare revised pricing model — implement agreed price adjustments, update financial model, recalculate margins and sensitivities',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Bid Manager' },
          outputs: [{ name: 'Revised pricing model', format: 'Updated financial model', quality: ['Price adjustments implemented per BAFO strategy','Margin impact calculated and within approved parameters','Sensitivities recalculated against new price position','Model independently verified'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-05.2.2', name: 'Prepare updated solution or commercial documents — any changes to the submitted proposal required by BAFO strategy',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: null },
          outputs: [{ name: 'Revised pricing model, updated solution elements (activity primary output)', format: 'BAFO submission package', quality: ['All changes from original submission clearly identified','Narrative updated to reflect any solution or commercial changes','Consistency checked — no contradictions with unchanged elements','Ready for BAFO governance approval (POST-06)'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Revised pricing model, updated solution elements', format: 'BAFO submission package', quality: ['BAFO strategy defined with clear rationale','Price adjustments within approved parameters','Solution changes consistent with original submission','Ready for governance approval'] }]
},

'POST-06': {
  subs: [
    {
      id: 'POST-06.1', name: 'BAFO Governance',
      description: 'Obtain governance approval for BAFO submission',
      tasks: [
        { id: 'POST-06.1.1', name: 'Prepare BAFO governance pack — original approved position, proposed changes, margin impact, rationale, and recommendation',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Commercial Lead', i: null },
          outputs: [{ name: 'BAFO governance pack', format: 'Governance pack', quality: ['Original approved position referenced — GOV-03/04 decisions','Proposed changes clearly described with rationale','Margin impact quantified — new position vs approved position','Competitive context explained — why these changes improve PWIN'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-06.1.2', name: 'Obtain executive approval for BAFO — any material change to price or commercial position requires fresh approval',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Board-approved BAFO mandate (activity primary output)', format: 'Formal approval record', quality: ['BAFO position approved at appropriate governance level','If change exceeds delegated authority, escalated to higher tier','Approved price floor and negotiation parameters confirmed','Mandate communicated to bid team for BAFO preparation'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Board-approved BAFO mandate', format: 'Formal BAFO approval', quality: ['BAFO position approved at appropriate governance level','Margin floor and negotiation parameters confirmed','Mandate communicated to bid team'] }]
},

'POST-07': {
  subs: [
    {
      id: 'POST-07.1', name: 'Negotiation Preparation',
      description: 'Prepare negotiation positions and strategy',
      tasks: [
        { id: 'POST-07.1.1', name: 'Prepare negotiation positions — approved contract positions from GOV-06, commercial parameters from GOV-03, trade-off matrix',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Legal Lead', i: 'Bid Manager' },
          outputs: [{ name: 'Negotiation preparation pack', format: 'Strategy and positions document', quality: ['Approved positions from governance documented — what we can and cannot concede','Trade-off matrix prepared — what are we willing to give vs what we need to hold?','Authority limits clear — who can agree what during negotiation','Fallback positions identified for each key negotiation point'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'POST-07.2', name: 'Negotiation Execution',
      description: 'Lead negotiations with the client',
      tasks: [
        { id: 'POST-07.2.1', name: 'Lead commercial and contractual negotiations — manage trade-offs within approved parameters, escalate when authority limits reached',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Legal Lead', i: 'Bid Manager' },
          outputs: [{ name: 'Negotiation session records', format: 'Session records', quality: ['All negotiation sessions documented — positions discussed, concessions made, agreements reached','Trade-offs tracked — what we gave vs what we got','Client rationale for their positions captured — useful for future bids'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-07.2.2', name: 'Escalate positions exceeding approved parameters — re-gate if material change to commercial or contractual position',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Commercial Lead / Legal Lead', i: 'Bid Manager' },
          outputs: [{ name: 'Negotiated T&C schedule, agreed pricing (activity primary output)', format: 'Agreed positions with escalation record', quality: ['Final negotiated positions documented','Any positions exceeding approved parameters re-approved through governance','Client agreements confirmed in writing — not just verbal','Ready for contract execution (POST-08)'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Negotiated T&C schedule, agreed pricing', format: 'Agreed contractual and commercial positions', quality: ['Negotiations conducted within approved parameters','Escalations handled through governance where required','Final positions documented and confirmed in writing','Ready for contract execution'] }]
},

'POST-08': {
  subs: [
    {
      id: 'POST-08.1', name: 'Contract Award',
      description: 'Process the contract award and establish the commercial baseline',
      tasks: [
        { id: 'POST-08.1.1', name: 'Receive and process contract award — confirm terms match negotiated positions, execute contract per delegated authority',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Legal Lead', i: 'Finance' },
          outputs: [{ name: 'Executed contract', format: 'Signed contract', quality: ['Contract terms verified against negotiated positions — no surprises','Executed per corporate delegated authority','Contract start date and key milestones confirmed','Commercial baseline established — this is the reference for delivery'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-08.1.2', name: 'Establish commercial baseline and contract management framework — hand over from bid commercial to delivery commercial',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Delivery Director' },
          outputs: [{ name: 'Commercial baseline pack', format: 'Baseline documents', quality: ['P&L baseline documented — what was bid vs what was agreed','Key commercial terms summarised for delivery team','Contract management framework handed over','Financial model locked as the bid baseline'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    },
    {
      id: 'POST-08.2', name: 'Mobilisation Handover',
      description: 'Hand over from bid team to delivery team',
      tasks: [
        { id: 'POST-08.2.1', name: 'Prepare handover pack — solution design, mobilisation plan, risk register, assumptions, key relationships, lessons learned',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Delivery Director', i: 'All Workstream Leads' },
          outputs: [{ name: 'Handover pack', format: 'Comprehensive handover document', quality: ['Solution design and key commitments documented','Mobilisation plan with milestones and team structure','Risk register handed over with current status and mitigations','Assumptions log — what was assumed during the bid that delivery must validate','Key client relationships and stakeholder intelligence transferred'] }],
          effort: 'Medium', type: 'Sequential' },
        { id: 'POST-08.2.2', name: 'Conduct handover briefing — face-to-face session between bid team and delivery team covering all critical handover items',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Delivery Director', i: 'All Workstream Leads' },
          outputs: [{ name: 'Handover briefing record', format: 'Meeting record', quality: ['Delivery Director and key delivery leads attend','Every handover item briefed — not just document handoff','Questions from delivery team captured and answered','Transition support period agreed — bid team available for X weeks after handover'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'POST-08.2.3', name: 'Close bid — archive all bid documents, close cost-to-bid tracker, update corporate bid library, confirm bid team stand-down',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Bid Coordinator', i: null },
          outputs: [{ name: 'Handover pack, delivery team briefed, PID (activity primary output)', format: 'Bid closure record', quality: ['All bid documents archived per retention policy','Cost-to-bid tracker closed — final actuals recorded','Corporate bid library updated with reusable content','Bid team formally stood down — resources released','Win/loss analysis scheduled (if not already completed via BM-12)'] }],
          effort: 'Low', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Handover pack, delivery team briefed, PID', format: 'Handover package and bid closure', quality: ['Contract executed and commercial baseline established','Handover pack comprehensive — solution, risks, assumptions, relationships','Delivery team briefed face-to-face','Bid formally closed — documents archived, resources released'] }]
},

// ──────────────────────────────────────────────────────────────────
// DEL + SUP (already reasonably well mapped — minor expansions)
// ──────────────────────────────────────────────────────────────────

'DEL-05': {
  subs: [
    {
      id: 'DEL-05.1', name: 'Business Continuity & Disaster Recovery',
      description: 'Design the BCDR approach for the proposed service',
      tasks: [
        { id: 'DEL-05.1.1', name: 'Identify BCDR requirements from ITT — contractual obligations, RTO/RPO targets, specific scenarios the client requires coverage for',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / IT', i: 'Legal Lead' },
          outputs: [{ name: 'BCDR requirements register', format: 'Requirements list', quality: ['All contractual BCDR requirements extracted from ITT','RTO and RPO targets documented per service element','Specific scenarios identified — site loss, technology failure, pandemic, supply chain disruption','Client expectations clear — not just contractual but what they actually need'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'DEL-05.1.2', name: 'Design BCDR approach — how the service continues during major disruption, aligned to contractual requirements and proportionate to risk',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / Technology SMEs', i: 'Commercial Lead' },
          outputs: [{ name: 'BCDR plan', format: 'Plan document', quality: ['BCDR approach covers all identified scenarios','RTO/RPO targets achievable with proposed approach','Cost of BCDR proportionate to risk and included in financial model','Testing and exercising approach defined'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'DEL-05.2', name: 'Exit & Handback Planning',
      description: 'Design the exit and handback plan for contract end',
      tasks: [
        { id: 'DEL-05.2.1', name: 'Identify exit obligations from ITT — TUPE reverse transfer, data return, knowledge transfer, asset handback, service continuity during exit',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Legal Lead / HR Lead', i: 'Commercial Lead' },
          outputs: [{ name: 'Exit obligations register', format: 'Requirements list', quality: ['All contractual exit obligations extracted','TUPE reverse transfer requirements documented','Data return and destruction obligations identified','Asset handback schedule requirements noted','Service continuity during exit period defined'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'DEL-05.2.2', name: 'Design exit and handback plan — reverse TUPE, data return, knowledge transfer, asset handback, service continuity during exit period',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'HR Lead / Legal Lead', i: 'Solution Architect' },
          outputs: [{ name: 'BC/exit plan (activity primary output)', format: 'Combined BC and exit plan', quality: ['Exit timeline realistic — typically 6-12 months for complex services','Knowledge transfer approach designed — not just data handover','Asset handback schedule aligned to exit timeline','Service continuity guaranteed throughout exit period','Exit costs included in financial model'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'BC/exit plan', format: 'Combined BCDR and exit plan', quality: ['BCDR covers all contractual scenarios with achievable RTO/RPO','Exit plan covers TUPE, data, knowledge, assets, and service continuity','Costs included in financial model','Proportionate to contract value and risk'] }]
},

'SUP-04': {
  subs: [
    {
      id: 'SUP-04.1', name: 'Partner Pricing Collection',
      description: 'Manage the collection of partner pricing inputs',
      tasks: [
        { id: 'SUP-04.1.1', name: 'Issue pricing requirements to partners — scope, format, assumptions, deadline, and alignment to our commercial model structure',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Partner' },
          outputs: [{ name: 'Partner pricing brief', format: 'Pricing request document', quality: ['Scope clearly defined — what exactly are partners pricing?','Format specified — aligns to our cost model structure','Assumptions shared — volume, duration, indexation, risk allocation','Deadline clear with contingency for iteration'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'SUP-04.1.2', name: 'Collect and validate partner pricing submissions — check completeness, alignment to scope, and reasonableness',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Commercial Lead', i: null },
          outputs: [{ name: 'Validated partner pricing', format: 'Reviewed pricing submissions', quality: ['All partner pricing received by deadline','Completeness checked — all scope items priced, no gaps','Alignment verified — partner assumptions match our assumptions','Reasonableness checked — pricing in line with market expectations'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    },
    {
      id: 'SUP-04.2', name: 'Partner Pricing Alignment',
      description: 'Resolve pricing gaps and align partner pricing with our commercial model',
      tasks: [
        { id: 'SUP-04.2.1', name: 'Facilitate pricing clarification and iteration — resolve gaps, misalignments, and assumption mismatches between partners and our model',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Commercial Lead / Partner', i: null },
          outputs: [{ name: 'Partner pricing schedules (activity primary output)', format: 'Finalised partner pricing for integration into COM-03', quality: ['All gaps and misalignments resolved','Partner pricing integrated into our cost model structure','Assumptions aligned between partner and our model','Final partner pricing locked and feeds COM-03'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Partner pricing schedules', format: 'Finalised partner pricing', quality: ['All partners priced their scope completely','Assumptions aligned with our commercial model','Pricing validated for reasonableness','Feeds COM-03 for integration into overall pricing'] }]
},

'SUP-05': {
  subs: [
    {
      id: 'SUP-05.1', name: 'Evidence Requirements',
      description: 'Issue evidence requirements to partners and manage collection',
      tasks: [
        { id: 'SUP-05.1.1', name: 'Issue evidence requirements to partners — case studies, CVs, credentials, certifications required per SOL-10 evidence matrix',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Bid Manager', i: 'Partner' },
          outputs: [{ name: 'Partner evidence brief', format: 'Evidence requirements per partner', quality: ['Specific evidence items requested per SOL-10 matrix — not vague "send us some case studies"','Format and quality standards specified','Deadline clear with contingency for revision'] }],
          effort: 'Low', type: 'Sequential' },
        { id: 'SUP-05.1.2', name: 'Collect partner evidence and conduct initial quality review — relevance, currency, format compliance',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: null, i: 'Bid Manager' },
          outputs: [{ name: 'Raw partner evidence', format: 'Collected evidence items', quality: ['All requested items received or gaps identified','Initial quality review completed — relevance, currency, format','Items needing revision identified and fed back to partners'] }],
          effort: 'Medium', type: 'Parallel' },
      ]
    },
    {
      id: 'SUP-05.2', name: 'Evidence Adaptation',
      description: 'Adapt partner evidence for submission quality',
      tasks: [
        { id: 'SUP-05.2.1', name: 'Adapt partner evidence for submission — align to our brand standards, tailor to this opportunity, anonymise where required',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'Supply Chain Lead', i: 'Partner' },
          outputs: [{ name: 'Partner case studies & CVs (activity primary output)', format: 'Submission-ready partner evidence', quality: ['Partner evidence formatted to our standards — consistent with internal evidence','Tailored to this opportunity — generic partner brochures not acceptable','Anonymisation applied where ITT requires','Win themes reinforced through evidence selection and framing','Feeds PRD-03 for integration into evidence pack'] }],
          effort: 'Medium', type: 'Sequential' },
      ]
    }
  ],
  outs: [{ name: 'Partner case studies & CVs', format: 'Submission-ready partner evidence', quality: ['All required partner evidence collected','Quality reviewed for relevance and currency','Adapted to our brand standards','Feeds PRD-03 evidence assembly'] }]
},

};

// ═══════════════════════════════════════════════════════════════════
// APPLY EXPANSIONS TO GOLD STANDARD
// ═══════════════════════════════════════════════════════════════════

const gsPath = path.join(__dirname, '..', 'docs', 'methodology_gold_standard.md');
let gs = fs.readFileSync(gsPath, 'utf-8');

// For each expansion, find the activity's code block and replace subs[] and outs[]
// Strategy: parse the full code block, replace subs and outs, serialize back
const blockRegex = /```javascript\n([\s\S]*?)```/g;
let replaced = 0;

gs = gs.replace(blockRegex, (fullMatch, blockContent) => {
  // Check if this block matches one of our expansion targets
  const idMatch = blockContent.match(/id:\s*'([^']+)'/);
  if (!idMatch || !expansions[idMatch[1]]) return fullMatch;

  const actId = idMatch[1];
  const expansion = expansions[actId];

  try {
    const cleaned = blockContent.trim().replace(/[\u2018\u2019]/g, "'").replace(/[\u201C\u201D]/g, '"');
    const fn = new Function(`return (${cleaned});`);
    const obj = fn();

    // Replace subs and outs
    obj.subs = expansion.subs;
    if (expansion.outs) obj.outputs = expansion.outs;

    // Serialize back to JS-like format (not JSON — keep readable)
    const serialized = serializeActivity(obj);
    replaced++;
    return '```javascript\n' + serialized + '\n```';
  } catch (e) {
    console.error(`  Failed to expand ${actId}: ${e.message}`);
    return fullMatch;
  }
});

fs.writeFileSync(gsPath, gs);
console.error(`Expanded ${replaced} of ${Object.keys(expansions).length} activities`);

function serializeActivity(obj) {
  // Pretty-print as JS object literal — readable, not minified
  return JSON.stringify(obj, null, 2)
    // Convert JSON keys to unquoted JS keys
    .replace(/"(\w+)":/g, '$1:')
    // Convert double-quoted strings to single-quoted
    .replace(/: "([^"]*?)"/g, (m, v) => `: '${v.replace(/'/g, "\\'")}'`)
    // Fix arrays of single-quoted strings
    .replace(/\["([^"]*?)"\]/g, (m) => m.replace(/"/g, "'"))
    // Fix remaining double-quoted strings in arrays
    .replace(/"([^"]*?)"/g, (m, v) => `'${v.replace(/'/g, "\\'")}'`);
}
