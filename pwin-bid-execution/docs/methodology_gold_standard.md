# Methodology Mapping — Gold Standard Reference

**Version:** 1.0 | April 2026
**Purpose:** Defines the canonical data structure and quality bar for L1/L2/L3 methodology mapping across all 79 activities. Every activity in the methodology must be mapped to this standard before populating the Bid Execution product template data.

**Reference activity:** SAL-03 — Competitor analysis & positioning

---

## Data Structure Specification

Each activity follows this structure in the template data:

```javascript
{
  id: 'SAL-03',
  name: 'Competitor analysis & positioning',
  workstream: 'SAL',
  phase: 'DEV',
  role: 'Capture Lead',                    // Default owner — tasks inherit unless overridden
  output: 'Competitive landscape assessment',
  dependencies: ['SAL-01', 'SAL-02'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',                // S=Specialist, P=Parallelisable, C=Coordination

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
    { from: 'SAL-02', artifact: 'Incumbent performance assessment' },
    { external: true, artifact: 'Contracts Finder / FTS award history' },
    { external: true, artifact: 'Public domain competitor intelligence (annual reports, press, LinkedIn)' },
    { crossProduct: 'PWIN-WINSTRAT', artifact: 'Competitive Positioning Matrix', optional: true,
      note: 'From Win Strategy product if capture phase completed — refinement not cold-start' }
  ],

  // ── L2 sub-processes (always present, consistent nesting) ──────────
  subs: [
    {
      id: 'SAL-03.1',
      name: 'Competitive Intelligence Gathering',
      description: 'Identify and profile all credible competitors using available intelligence sources',

      // ── L3 tasks ─────────────────────────────────────────────────
      tasks: [
        {
          id: 'SAL-03.1.1',
          name: 'Identify credible competitors from procurement history and market intelligence',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Market Intelligence / Partners', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
            { external: true, artifact: 'Contracts Finder / FTS award history' },
            { external: true, artifact: 'Sector procurement announcements' }
          ],
          outputs: [
            {
              name: 'Competitor long list',
              format: 'Structured register',
              quality: [
                'Every competitor has an evidence basis for inclusion (not guesswork)',
                'Sources cited for each entry (award notice, market intel, client mention)',
                'Covers incumbents, known bidders, and plausible new entrants'
              ]
            }
          ],
          effort: 'Low',            // Low / Medium / High relative to activity total
          type: 'Sequential'        // Sequential / Parallel
        },
        {
          id: 'SAL-03.1.2',
          name: 'Categorise competitors: Incumbent / Contender / Dark Horse / Opportunist',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Market Intelligence', i: 'Partner Lead' },
          inputs: [
            { from: 'SAL-03.1.1', artifact: 'Competitor long list' },
            { from: 'SAL-02', artifact: 'Incumbent performance assessment' }
          ],
          outputs: [
            {
              name: 'Competitive landscape map (categorised)',
              format: 'Matrix / visual map',
              quality: [
                'Every identified competitor is categorised',
                'Category rationale documented for each (not just a label)',
                'Incumbent strengths and vulnerabilities explicitly captured',
                'Assessment distinguishes between known facts and assumptions'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'SAL-03.1.3',
          name: 'Profile each credible competitor — likely strategy, strengths, weaknesses, price position',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect / SMEs', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-03.1.2', artifact: 'Competitive landscape map (categorised)' },
            { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
            { external: true, artifact: 'Public domain intelligence (annual reports, award notices, press, LinkedIn)' }
          ],
          outputs: [
            {
              name: 'Competitor profiles',
              format: 'Per-competitor structured profile',
              quality: [
                'Each profile covers: likely bid strategy, key strengths, exploitable weaknesses, likely price position',
                'Profiles are specific to this opportunity (not generic company summaries)',
                'Confidence level stated for each assessment (known / inferred / assumed)',
                'Top 2-3 competitors identified for detailed counter-strategy'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'         // Can profile multiple competitors simultaneously
        }
      ]
    },
    {
      id: 'SAL-03.2',
      name: 'Competitive Positioning & Counter-Strategy',
      description: 'Develop actionable counter-strategies and ghost themes based on competitor intelligence',

      tasks: [
        {
          id: 'SAL-03.2.1',
          name: 'Develop counter-strategies and ghost themes for top 2-3 competitors',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-03.1.3', artifact: 'Competitor profiles' },
            { from: 'SAL-01', artifact: 'Customer intelligence briefing' }
          ],
          outputs: [
            {
              name: 'Counter-strategy register',
              format: 'Structured register',
              quality: [
                'Each counter-strategy is actionable — maps to a specific response tactic or solution feature',
                'Ghost themes are phrased from the evaluator perspective (what the competitor will claim)',
                'Counter-narratives prepared for each ghost theme',
                'Strategies are differentiated per competitor (not one generic approach)'
              ]
            },
            {
              name: 'Ghost themes',
              format: 'Structured list',
              quality: [
                'Each ghost theme identifies: which competitor, what they will claim, why it resonates with the buyer',
                'Corresponding counter-position defined for each',
                'Usable by proposal authors without further interpretation'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SAL-03.2.2',
          name: 'Validate competitive positioning with bid team and adjust',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SAL-03.2.1', artifact: 'Counter-strategy register' },
            { from: 'SAL-03.1.3', artifact: 'Competitor profiles' }
          ],
          outputs: [
            {
              name: 'Competitive landscape assessment (validated — activity primary output)',
              format: 'Document / structured register',
              quality: [
                'Bid team has reviewed and challenged — not single-author opinion',
                'Adjustments from validation captured and incorporated',
                'Final assessment is the authoritative competitive view for the bid',
                'Downstream consumers identified: SAL-04 (win themes), COM-02 (price-to-win)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output (the deliverable that downstream activities consume) ──
  outputs: [
    {
      name: 'Competitive landscape assessment',
      format: 'Document / structured register',
      quality: [
        'All credible competitors identified with evidence basis',
        'Each competitor categorised (Incumbent / Contender / Dark Horse / Opportunist)',
        'Top 2-3 competitors profiled: strategy, strengths, weaknesses, price position',
        'Counter-strategies are actionable — each maps to a specific response tactic',
        'Ghost themes defined and usable by proposal authors',
        'Validated by bid team — not single-author opinion'
      ]
    }
  ],

  // ── Downstream consumers (who uses this output) ────────────────────
  consumers: [
    { activity: 'SAL-04', consumes: 'Competitive landscape assessment', usage: 'Win themes shaped to counter competitor positioning' },
    { activity: 'COM-02', consumes: 'Competitive landscape assessment', usage: 'Price-to-win calibrated against competitor price positions' },
    { activity: 'SAL-06', consumes: 'Competitive landscape assessment', usage: 'Capture plan incorporates competitive strategy' }
  ]
}
```

---

## Anatomy of the Gold Standard

### What each layer contains

| Layer | What it defines | Question it answers |
|---|---|---|
| **L1 — Workstream** | Phase, default role | *Who owns this area of work?* |
| **L2 — Sub-process** | Distinct stages within the activity | *What are the major steps? Does one flow into the next?* |
| **L3 — Task** | Atomic unit of work with RACI, inputs, outputs, quality criteria | *What exactly must be done, by whom, using what, producing what, and how do we know it's good enough?* |
| **L4 — Skill** (future, not in methodology) | AI-assisted workflow logic | *How does the AI help the bid manager execute or monitor this task?* |

### Rules for L2 sub-processes

1. **Always present.** Even if an activity has only one logical sub-process, wrap the tasks in an L2 container for consistent nesting.
2. **Flow, not silos.** L2s within an activity typically flow sequentially (gather → position, draft → review, analyse → recommend). Name them to reflect the flow.
3. **2-4 per activity is typical.** If you have more than 4, consider whether the activity should be split. If you have 1, check whether there's genuinely no internal structure.

### Rules for L3 tasks

1. **Checkable.** Each task must be completable — the bid manager can tick it done. If you can't tell when it's done, it's not a task.
2. **Named inputs.** Every input is either `{ from: 'ACTIVITY-CODE', artifact: 'name' }` (internal, machine-traversable) or `{ external: true, artifact: 'description' }`. No vague "various documents."
3. **Quality criteria on outputs.** Each output has discrete `quality[]` items — these are what the bid manager (V1) or workstream lead (V2) ticks to confirm quality. They drive status derivation:
   - All tasks ticked → `draft_complete`
   - All quality criteria ticked → `final`
4. **RACI at task level.** The activity `role` is the default. Override at task level only when a different person is responsible.
5. **Effort is relative.** Low / Medium / High within the activity's total effort. Not absolute person-days — the activity-level `effortDays` governs the total.
6. **Type reflects parallelism.** Sequential = must follow previous task. Parallel = can run alongside other tasks (e.g., profiling multiple competitors simultaneously).

### Rules for inputs

1. **Internal inputs use `from` field** — always an activity code, always an artifact name. This makes them machine-traversable for dependency analysis and status derivation.
2. **External inputs use `external: true`** — procurement documents, public data, client-provided materials. These don't have upstream status to track.
3. **Cross-product inputs use `crossProduct`** — outputs from other PWIN products (e.g., Win Strategy). Always `optional: true` because the other product may not have been used.
4. **Task-level inputs can reference sibling tasks** — use the task ID (e.g., `SAL-03.1.1`) when one task within an activity feeds the next. This enables intra-activity dependency tracking.

### Rules for outputs and quality criteria

1. **Activity-level output** = the deliverable that downstream activities consume. This is what appears in the dependency chain.
2. **Task-level outputs** = intermediate artefacts produced during the activity. The final task's output should align with (or be) the activity-level output.
3. **Quality criteria are discrete checks**, not descriptions. "Each competitor has evidence basis for inclusion" is checkable. "Good quality analysis" is not.
4. **Quality criteria drive status.** The system derives `final` status only when all quality criteria are ticked. Write them as the actual things a reviewer would verify.

### Rules for consumers

1. **Explicit downstream mapping.** Every activity output should list which activities consume it and what they use it for.
2. **This enables cascade analysis.** If SAL-03 is late, the timeline-analysis skill can immediately identify SAL-04 and COM-02 as impacted and calculate slip.

---

## Cross-Product Interface Pattern

When an activity can receive inputs from another PWIN product (e.g., the Win Strategy product feeding into the Execution product), use this pattern:

```javascript
{ crossProduct: 'PRODUCT-CODE', artifact: 'Artifact name', optional: true,
  note: 'Context for when this input exists vs when it does not' }
```

**Two operating modes result:**

| Mode | When | Effect on the activity |
|---|---|---|
| **Capture-informed** | Cross-product input exists | L3 tasks become refinement and validation against the ITT, not cold-start |
| **Cold-start** | No cross-product input | L3 tasks build the deliverable from scratch — higher effort, AI has less to work with |

The methodology does not change between modes — the same tasks apply. But the effort estimate and AI assistance capability differ. The activity guidance should note both modes where relevant.

---

## Checklist: Is This Activity Mapped to Gold Standard?

Use this checklist before marking any activity as mapping-complete:

- [ ] **L2s defined** — at least 1, typically 2-4, with clear flow between them
- [ ] **L3 tasks defined** — each is checkable, named, with RACI
- [ ] **All inputs are structured** — `from` + `artifact` for internal, `external: true` for external, `crossProduct` for cross-product
- [ ] **All outputs have quality criteria** — discrete, checkable items (not descriptions)
- [ ] **Activity-level output matches** — the final task output aligns with the activity's primary deliverable
- [ ] **Consumers listed** — which downstream activities use this output and why
- [ ] **Effort feels proportionate** — L3 task count and effort ratings make sense against the activity's total person-days
- [ ] **RACI is specific** — named roles, not "team" or "various"
- [ ] **Cross-product inputs identified** — if the Win Strategy product or other PWIN products could feed this activity, the interface is explicit
- [ ] **Both operating modes considered** — capture-informed vs cold-start noted where relevant

---

## SAL-01 — Customer Engagement & Intelligence Gathering

```javascript
{
  id: 'SAL-01',
  name: 'Customer engagement & intelligence gathering',
  workstream: 'SAL',
  phase: 'DEV',
  role: 'Capture Lead',
  output: 'Customer intelligence briefing',
  dependencies: [],                        // Day-1 start — no upstream dependencies
  effortDays: 10,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires domain knowledge and client access

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { external: true, artifact: 'ITT / OJEU notice / procurement documentation' },
    { external: true, artifact: 'Client published strategies, spending reviews, annual reports' },
    { external: true, artifact: 'Sector policy documents and regulatory landscape' },
    { external: true, artifact: 'Account history and CRM data (previous bids, meetings, contacts)' },
    { external: true, artifact: 'Public domain market intelligence (trade press, analyst reports, industry events)' },
    { crossProduct: 'PWIN-COACH', artifact: 'PWIN qualification assessment', optional: true,
      note: 'From PWIN Coach if bid/no-bid qualification was completed — provides initial opportunity framing and PWIN score' },
    { crossProduct: 'PWIN-WINSTRAT', artifact: 'Capture-phase client intelligence', optional: true,
      note: 'From Win Strategy product if capture phase completed — existing buyer values and client insight to refine, not rebuild' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SAL-01.1',
      name: 'Opportunity Intelligence Gathering',
      description: 'Build a comprehensive picture of this specific opportunity, the client\'s strategic context, procurement landscape, and supplier ecosystem',

      tasks: [
        {
          id: 'SAL-01.1.1',
          name: 'Gather and review procurement documentation — ITT notice, prior information notices, market engagement outputs',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Bid Manager', i: 'Commercial Lead' },
          inputs: [
            { external: true, artifact: 'ITT / OJEU notice / procurement documentation' },
            { external: true, artifact: 'Prior information notices and market engagement records' }
          ],
          outputs: [
            {
              name: 'Procurement context summary',
              format: 'Structured briefing',
              quality: [
                'Procurement route, timeline, and key milestones documented',
                'Contract scope, value, and duration captured',
                'Lot structure and evaluation approach identified (if published)',
                'Procurement history for this requirement noted (previous contracts, extensions, re-lets)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'SAL-01.1.2',
          name: 'Review client strategic plans, spending reviews, policy drivers, and published priorities',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Market Intelligence', i: 'Solution Architect' },
          inputs: [
            { external: true, artifact: 'Client published strategies, spending reviews, annual reports' },
            { external: true, artifact: 'Sector policy documents and regulatory landscape' }
          ],
          outputs: [
            {
              name: 'Client strategic context summary',
              format: 'Structured briefing',
              quality: [
                'Client\'s strategic priorities and policy drivers documented with sources',
                'Budget pressures, efficiency targets, or transformation agendas identified',
                'Political and regulatory context noted (machinery of government changes, spending reviews, policy shifts)',
                'Links between client strategy and this specific procurement identified'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'SAL-01.1.3',
          name: 'Compile market and sector intelligence relevant to this requirement',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'SME / Market Intelligence', i: 'Partner Lead' },
          inputs: [
            { external: true, artifact: 'Public domain market intelligence (trade press, analyst reports, industry events)' },
            { external: true, artifact: 'Sector policy documents and regulatory landscape' }
          ],
          outputs: [
            {
              name: 'Market and sector intelligence pack',
              format: 'Structured briefing',
              quality: [
                'Relevant sector trends, innovations, and policy changes identified',
                'Market dynamics that affect this opportunity documented (consolidation, new entrants, regulation)',
                'Intelligence is specific to this opportunity\'s sector and scope — not generic market overview',
                'Sources cited for all assertions'
              ]
            }
          ],
          effort: 'Low',
          type: 'Parallel'
        },
        {
          id: 'SAL-01.1.4',
          name: 'Map client\'s existing strategic suppliers, partners, and past procurement activity at a strategic level',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager / Market Intelligence', i: 'Commercial Lead' },
          inputs: [
            { external: true, artifact: 'Contracts Finder / FTS award history' },
            { external: true, artifact: 'Client annual reports, published supplier lists, framework agreements' },
            { external: true, artifact: 'Account history and CRM data (previous bids, meetings, contacts)' }
          ],
          outputs: [
            {
              name: 'Client supplier landscape map',
              format: 'Structured register',
              quality: [
                'Current incumbent(s) and contract history documented',
                'Client\'s strategic supplier and partner relationships identified (frameworks, JVs, preferred suppliers)',
                'Past procurement patterns noted — how this client buys, typical contract structures, evaluation preferences',
                'Potential teaming or supply chain implications identified',
                'Sources cited — award notices, published data, not assumptions'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'SAL-01.2',
      name: 'Buyer Values & Client Problem Analysis',
      description: 'Understand what this client strategically cares about, what problem they are trying to solve, and what their hot-button issues and priorities are — distinct from formal evaluation criteria (SAL-05)',

      tasks: [
        {
          id: 'SAL-01.2.1',
          name: 'Identify client\'s strategic priorities, pain points, and hot-button issues from available intelligence',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager', i: 'Solution Architect' },
          inputs: [
            { from: 'SAL-01.1.2', artifact: 'Client strategic context summary' },
            { from: 'SAL-01.1.1', artifact: 'Procurement context summary' },
            { external: true, artifact: 'Account history and CRM data (previous bids, meetings, contacts)' }
          ],
          outputs: [
            {
              name: 'Buyer values register',
              format: 'Structured register',
              quality: [
                'Each buyer value is a strategic priority the client cares about — not a scoring criterion',
                'Values are specific to this client and opportunity (not generic "value for money")',
                'Evidence basis cited for each value (published strategy, known constraint, intelligence)',
                'Distinction clear between known values, inferred values, and assumptions',
                'Examples: "partnership investment / gain share model", "reducing re-offending rates", "digital transformation of frontline services"'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-01.2.2',
          name: 'Analyse the current problem or opportunity the client is trying to solve — what is driving this procurement?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect / SME', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-01.1.2', artifact: 'Client strategic context summary' },
            { from: 'SAL-01.1.4', artifact: 'Client supplier landscape map' },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' }
          ],
          outputs: [
            {
              name: 'Client problem statement',
              format: 'Structured narrative',
              quality: [
                'Articulates why this procurement exists — what problem, gap, or opportunity the client is addressing',
                'Distinguishes between stated objectives (what the ITT says) and underlying drivers (what is really going on)',
                'Links the problem to client strategic context — not an isolated requirement',
                'Identifies implications for our solution approach — what would a winning response need to address?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-01.2.3',
          name: 'Synthesise customer intelligence briefing — the consolidated output consumed by downstream activities',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: null, i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-01.1.1', artifact: 'Procurement context summary' },
            { from: 'SAL-01.1.2', artifact: 'Client strategic context summary' },
            { from: 'SAL-01.1.3', artifact: 'Market and sector intelligence pack' },
            { from: 'SAL-01.1.4', artifact: 'Client supplier landscape map' },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
            { from: 'SAL-01.2.2', artifact: 'Client problem statement' }
          ],
          outputs: [
            {
              name: 'Customer intelligence briefing (activity primary output)',
              format: 'Document / structured briefing pack',
              quality: [
                'All six upstream artefacts consolidated into a single authoritative briefing',
                'Key findings and implications for bid strategy highlighted',
                'Gaps in intelligence explicitly flagged with plan to close',
                'Reviewed by Bid Director — not single-author opinion',
                'Usable by SAL-03 (competitor analysis), SAL-04 (win themes), and SAL-10 (stakeholder engagement) without further interpretation'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Customer intelligence briefing',
      format: 'Document / structured briefing pack',
      quality: [
        'Procurement context documented — route, timeline, scope, contract structure',
        'Client strategic priorities and policy drivers documented with sources',
        'Market and sector intelligence specific to this opportunity compiled',
        'Client supplier landscape mapped — incumbent, strategic partners, procurement patterns',
        'Buyer values identified as strategic priorities — distinct from evaluation scoring criteria',
        'Client problem statement articulated — why this procurement exists and what a winning response must address',
        'Intelligence gaps flagged with mitigation plan',
        'Validated by Bid Director — not single-author opinion'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SAL-03', consumes: 'Customer intelligence briefing', usage: 'Competitor analysis informed by client context and supplier landscape' },
    { activity: 'SAL-04', consumes: 'Customer intelligence briefing', usage: 'Win themes shaped by buyer values and client problem statement' },
    { activity: 'SAL-10', consumes: 'Customer intelligence briefing', usage: 'Stakeholder mapping built on initial client intelligence and relationship data' },
    { activity: 'SOL-01', consumes: 'Customer intelligence briefing', usage: 'Requirements interpretation informed by client strategic context (indirect via SAL-06)' }
  ]
}
```

---

## SAL-02 — Incumbent Performance Review

```javascript
{
  id: 'SAL-02',
  name: 'Incumbent performance review',
  workstream: 'SAL',
  phase: 'DEV',
  role: 'Capture Lead',
  // ARCHETYPE NOTES:
  // Technology/Digital: Minor — incumbent is a technology provider, not a service operator.
  //   L2.3 transformational disruption may emphasise different technologies. Same structure.
  // Consulting/Advisory: Minor — incumbent may be another consultancy. Stickiness is about
  //   relationships and knowledge, not TUPE/assets. Same structure, different emphasis.
  output: 'Incumbent performance assessment',
  dependencies: [],                        // Day-1 start — can run in parallel with SAL-01
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires competitive intelligence and sector knowledge
  // Note: applies to all bids (understanding the incumbent). Additional depth for rebids where we ARE the incumbent.
  // "(rebid)" qualifier toggled at bid setup via incumbency flag — does not change the tasks, changes the source of intelligence.
  // When we are the incumbent: internal delivery data, honest self-assessment.
  // When we are the challenger: external research, published data, FOIs, client intelligence from SAL-01.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-01', artifact: 'Customer intelligence briefing', note: 'Soft dependency — can start in parallel, refines when SAL-01 outputs available' },
    { external: true, artifact: 'Contracts Finder / FTS award history — previous contract awards, values, durations' },
    { external: true, artifact: 'Published contract performance data (KPIs, audit reports, FOI responses)' },
    { external: true, artifact: 'Client publications referencing service delivery (annual reports, board papers, committee minutes)' },
    { external: true, artifact: 'Trade press and industry commentary on incumbent performance' },
    { external: true, artifact: 'Internal delivery data and performance records (if we are the incumbent)' },
    { crossProduct: 'PWIN-WINSTRAT', artifact: 'Incumbent intelligence from capture phase', optional: true,
      note: 'From Win Strategy product if capture phase completed — existing incumbent assessment to refine' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SAL-02.1',
      name: 'Incumbent Service Delivery & Performance Assessment',
      description: 'Assess how the incumbent has performed against the contract — service delivery, SLAs, client satisfaction, behaviour, and value-add — to understand what we are competing against',

      tasks: [
        {
          id: 'SAL-02.1.1',
          name: 'Review incumbent service delivery against contractual SLAs and performance framework — met, exceeded, or fallen short',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager / Delivery Director', i: 'Solution Architect' },
          inputs: [
            { external: true, artifact: 'Published contract performance data (KPIs, audit reports, FOI responses)' },
            { external: true, artifact: 'Client publications referencing service delivery (annual reports, board papers, committee minutes)' },
            { external: true, artifact: 'Internal delivery data and performance records (if we are the incumbent)' }
          ],
          outputs: [
            {
              name: 'Incumbent performance summary',
              format: 'Structured assessment',
              quality: [
                'Contractual SLAs and KPIs identified with incumbent performance against each (met / exceeded / failed)',
                'Evidence basis cited for every performance claim — not opinion',
                'Performance trajectory noted — improving, stable, or declining',
                'Distinguishes between our own data (if incumbent) and external evidence (if challenger)'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-02.1.2',
          name: 'Assess incumbent behaviour, culture, and partnership quality — does the client like working with them?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-02.1.1', artifact: 'Incumbent performance summary' },
            { from: 'SAL-01', artifact: 'Customer intelligence briefing', note: 'Client sentiment and relationship intelligence' },
            { external: true, artifact: 'Trade press and industry commentary on incumbent performance' }
          ],
          outputs: [
            {
              name: 'Incumbent relationship & culture assessment',
              format: 'Structured assessment',
              quality: [
                'Assessment covers: partnership behaviours, responsiveness, transparency, cultural fit with client',
                'Client satisfaction signals captured — are they looking for continuity or change?',
                'Assessment distinguishes between contractual delivery (task SAL-02.1.1) and relationship quality',
                'Evidence basis cited — not speculation about client sentiment'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-02.1.3',
          name: 'Assess incumbent innovation, continuous improvement, and value-add beyond the contract',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect / SME', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-02.1.1', artifact: 'Incumbent performance summary' },
            { external: true, artifact: 'Published case studies, awards, or innovation evidence from incumbent' }
          ],
          outputs: [
            {
              name: 'Incumbent innovation & value-add assessment',
              format: 'Structured assessment',
              quality: [
                'Specific innovations or improvements delivered by incumbent identified (not vague "they innovated")',
                'Assessment of whether incumbent has invested beyond contractual obligations',
                'Gaps identified — areas where client expected innovation but incumbent did not deliver',
                'Implication for our bid: where can we differentiate on innovation and investment?'
              ]
            }
          ],
          effort: 'Low',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'SAL-02.2',
      name: 'Incumbent Stickiness & Competitive Risk Assessment',
      description: 'Assess how entrenched the incumbent is — transition risk, price competitiveness, switching cost — to determine how hard they are to unseat and where we must differentiate',

      tasks: [
        {
          id: 'SAL-02.2.1',
          name: 'Assess incumbent price competitiveness — is the current price point one we can compete against, or must we differentiate elsewhere?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Partner Lead' },
          inputs: [
            { external: true, artifact: 'Contracts Finder / FTS award history — previous contract awards, values, durations' },
            { from: 'SAL-02.1.1', artifact: 'Incumbent performance summary' }
          ],
          outputs: [
            {
              name: 'Incumbent price position assessment',
              format: 'Structured assessment',
              quality: [
                'Known or estimated incumbent price position documented with evidence basis',
                'Assessment of whether price competition is viable or differentiation is required',
                'Contract value trajectory noted — has price grown, shrunk, or remained stable through extensions?',
                'Implication for our commercial strategy identified — compete on price, value, or both'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-02.2.2',
          name: 'Assess transition stickiness — TUPE complexity, asset transfer, knowledge transfer burden, client switching cost',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Commercial Lead / HR / Legal', i: 'Solution Architect' },
          inputs: [
            { external: true, artifact: 'Published workforce and TUPE data (if available)' },
            { from: 'SAL-02.1.1', artifact: 'Incumbent performance summary' },
            { external: true, artifact: 'Contract terms and transition provisions (if published or known)' }
          ],
          outputs: [
            {
              name: 'Transition risk assessment',
              format: 'Structured assessment',
              quality: [
                'TUPE scale and complexity assessed — workforce size, terms, pension implications',
                'Asset transfer requirements identified — property, equipment, IP, systems',
                'Knowledge transfer risk assessed — how dependent is service continuity on incumbent-specific knowledge?',
                'Client switching cost estimated — what disruption does changing supplier cause the client?',
                'Overall stickiness rating with rationale — how hard is this incumbent to unseat?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SAL-02.3',
      name: 'Transformational Disruption & Innovation Opportunity Assessment',
      description: 'Assess whether we can leapfrog the incumbent through transformational innovation — and critically, whether the client\'s procurement framework will reward it. The tandem test: can we drive transformational impact AND does the evaluation methodology align to value it?',

      tasks: [
        {
          id: 'SAL-02.3.1',
          name: 'Identify transformational opportunities — where can emerging technology, new delivery models, or fundamentally different approaches disrupt the incumbent\'s current operating model?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect / CTO / Innovation Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-02.1.1', artifact: 'Incumbent performance summary' },
            { from: 'SAL-02.1.3', artifact: 'Incumbent innovation & value-add assessment' },
            { from: 'SAL-01.1.2', artifact: 'Client strategic context summary', note: 'Soft input — is the client\'s strategic direction toward transformation or continuity?' },
            { external: true, artifact: 'Technology landscape intelligence — AI, automation, quantum computing, digital platforms, emerging capabilities' },
            { external: true, artifact: 'Our organisational capability portfolio — technology assets, delivery models, IP, partnerships' }
          ],
          outputs: [
            {
              name: 'Transformational opportunity register',
              format: 'Structured register',
              quality: [
                'Each opportunity identifies a specific area where the incumbent\'s operating model can be disrupted',
                'Technology or approach is named and specific — not vague "we\'ll use AI"',
                'Expected impact quantified or estimated — cost reduction, service improvement, outcome transformation',
                'Feasibility assessed — is this proven, emerging, or speculative?',
                'Link to incumbent weakness explicit — which gap or stagnation does this exploit?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-02.3.2',
          name: 'Assess alignment to evaluation framework and client appetite — will the procurement reward transformational approaches or penalise non-compliance with a prescriptive specification?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Bid Manager / Commercial Lead', i: 'Solution Architect' },
          inputs: [
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register', note: 'Does the client value innovation and investment?' },
            { external: true, artifact: 'ITT / OJEU notice / procurement documentation — evaluation methodology, specification type (prescriptive vs outcome-based)' }
          ],
          outputs: [
            {
              name: 'Evaluation alignment assessment',
              format: 'Structured assessment per opportunity',
              quality: [
                'Each transformational opportunity assessed against the evaluation framework — will it score or be penalised?',
                'Specification type characterised — prescriptive (must comply) vs outcome-based (can innovate)',
                'Client appetite for change assessed — do they want continuity or transformation?',
                'Risk of non-compliance identified for each opportunity — can we propose this within the rules?',
                'Clear recommendation: pursue, park, or reframe each opportunity'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-02.3.3',
          name: 'Assess our organisational capability to deliver the disruption — do we have the technology, skills, partners, and track record to credibly propose this?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect / CTO / Delivery Director', i: 'Partner Lead' },
          inputs: [
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' },
            { from: 'SAL-02.3.2', artifact: 'Evaluation alignment assessment' },
            { external: true, artifact: 'Our organisational capability portfolio — technology assets, delivery models, IP, partnerships' },
            { external: true, artifact: 'Partner and supply chain innovation capability' }
          ],
          outputs: [
            {
              name: 'Capability gap assessment',
              format: 'Structured assessment per opportunity',
              quality: [
                'Each viable opportunity assessed for our readiness to deliver — technology, skills, capacity',
                'Credibility test applied — do we have track record or evidence to back this claim?',
                'Capability gaps identified with mitigation — partner, recruit, develop, or acquire',
                'Opportunities with no credible delivery path flagged for rejection — not proposed on aspiration alone'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-02.3.4',
          name: 'Model the commercial impact — does the transformational approach drive a fundamentally different cost base and price point?',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Capture Lead / Solution Architect', i: 'Partner Lead' },
          inputs: [
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' },
            { from: 'SAL-02.3.3', artifact: 'Capability gap assessment' },
            { from: 'SAL-02.2.1', artifact: 'Incumbent price position assessment' }
          ],
          outputs: [
            {
              name: 'Commercial disruption model',
              format: 'Structured financial assessment',
              quality: [
                'Each viable opportunity modelled for cost impact — what does it do to the delivery cost base?',
                'Investment requirement estimated — what upfront investment is needed and over what payback period?',
                'Price point implication assessed — does this create a competitive price advantage or require gain-share/partnership model?',
                'Comparison to incumbent price position — does this change the commercial competitive dynamic?',
                'Risk/reward balance stated — is the investment case credible and proportionate?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-02.3.5',
          name: 'Synthesise incumbent performance assessment — consolidated view across all three dimensions informing competitive strategy, win approach, and go/no-go',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: null, i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-02.1.1', artifact: 'Incumbent performance summary' },
            { from: 'SAL-02.1.2', artifact: 'Incumbent relationship & culture assessment' },
            { from: 'SAL-02.1.3', artifact: 'Incumbent innovation & value-add assessment' },
            { from: 'SAL-02.2.1', artifact: 'Incumbent price position assessment' },
            { from: 'SAL-02.2.2', artifact: 'Transition risk assessment' },
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' },
            { from: 'SAL-02.3.2', artifact: 'Evaluation alignment assessment' },
            { from: 'SAL-02.3.3', artifact: 'Capability gap assessment' },
            { from: 'SAL-02.3.4', artifact: 'Commercial disruption model' }
          ],
          outputs: [
            {
              name: 'Incumbent performance assessment (activity primary output)',
              format: 'Document / structured assessment',
              quality: [
                'All nine upstream assessments consolidated into single authoritative view',
                'Clear statement of incumbent strengths we must counter or match',
                'Clear statement of incumbent weaknesses we can exploit',
                'Stickiness rating with evidence — can this incumbent realistically be unseated?',
                'Transformational disruption potential assessed — can we leapfrog, and will the procurement reward it?',
                'Commercial disruption impact quantified — does innovation change the price dynamic?',
                'Go/no-go implications stated — does the combined picture support pursuit?',
                'Implications for win strategy and differentiation approach identified',
                'Reviewed by Bid Director — not single-author opinion'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Incumbent performance assessment',
      format: 'Document / structured assessment',
      quality: [
        'Service delivery performance assessed against contractual SLAs with evidence',
        'Client relationship quality and partnership behaviours assessed',
        'Innovation and value-add beyond contract assessed',
        'Incumbent price competitiveness assessed with commercial implications',
        'Transition stickiness assessed — TUPE, assets, knowledge, switching cost',
        'Overall stickiness rating with rationale',
        'Transformational disruption opportunities identified, evaluation-aligned, capability-assessed, and commercially modelled',
        'Go/no-go implications stated — does the combined picture support pursuit?',
        'Implications for win strategy and differentiation explicitly stated',
        'Validated by Bid Director — not single-author opinion'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SAL-03', consumes: 'Incumbent performance assessment', usage: 'Competitor analysis uses incumbent assessment to categorise and profile the incumbent as a competitor' },
    { activity: 'SAL-04', consumes: 'Incumbent performance assessment', usage: 'Win themes shaped by incumbent weaknesses, differentiation opportunities, and transformational propositions' },
    { activity: 'COM-02', consumes: 'Incumbent performance assessment', usage: 'Price-to-win calibrated against incumbent price position and commercial disruption model' },
    { activity: 'SAL-06', consumes: 'Incumbent performance assessment', usage: 'Capture plan incorporates stickiness assessment, transition risk, and disruption strategy' },
    { activity: 'SOL-03', consumes: 'Incumbent performance assessment', usage: 'Target operating model informed by transformational opportunities and incumbent operating model gaps (indirect via SAL-06)' }
  ]
}
```

---

## SAL-04 — Win Theme Development & Refinement

```javascript
{
  id: 'SAL-04',
  name: 'Win theme development & refinement',
  workstream: 'SAL',
  phase: 'DEV',
  role: 'Capture Lead',
  output: 'Win theme document',
  dependencies: ['SAL-01', 'SAL-03'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — strategic positioning, not parallelisable
  // Note: two operating modes —
  // Capture-informed: win themes arrive from Win Strategy product, refined against ITT and updated intelligence
  // Cold-start: themes developed from scratch using SAL-01, SAL-02, SAL-03 outputs

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
    { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
    { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
    { from: 'SAL-02', artifact: 'Incumbent performance assessment', note: 'Especially L2.3 transformational disruption opportunities' },
    { from: 'SAL-10', artifact: 'Stakeholder relationship map & engagement plan', note: 'Soft input — which stakeholders care about which themes' },
    { external: true, artifact: 'ITT documentation — scope, requirements, specification' },
    { crossProduct: 'PWIN-WINSTRAT', artifact: 'Win Theme Map', optional: true,
      note: 'From Win Strategy product if capture phase completed — themes to refine, not develop from scratch' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SAL-04.1',
      name: 'Win Theme Identification & Development',
      description: 'Identify or import win themes, test each against buyer values, competitive positioning, disruption potential, and evidence — ensure every theme is differentiated, relevant, and substantiable',

      tasks: [
        {
          id: 'SAL-04.1.1',
          name: 'Import or develop initial win themes — from Win Strategy product (capture-informed) or from scratch using buyer values, competitive positioning, and disruption opportunities (cold-start)',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager', i: 'Solution Architect' },
          inputs: [
            { crossProduct: 'PWIN-WINSTRAT', artifact: 'Win Theme Map', optional: true },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
            { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
            { from: 'SAL-02', artifact: 'Incumbent performance assessment' }
          ],
          outputs: [
            {
              name: 'Draft win themes register (3–5 themes)',
              format: 'Structured register',
              quality: [
                'Each theme is a written statement — substantive, not just a label',
                'Each theme identifies a specific differentiator or value driver',
                'Themes cover the breadth of the opportunity — not all clustered in one dimension',
                'Source identified for each theme — capture phase, buyer values, competitive gap, or disruption opportunity'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-04.1.2',
          name: 'Test each theme against buyer values — does this resonate with what the client actually cares about?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-04.1.1', artifact: 'Draft win themes register' },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
            { from: 'SAL-01.2.2', artifact: 'Client problem statement' }
          ],
          outputs: [
            {
              name: 'Buyer values alignment assessment per theme',
              format: 'Matrix (themes × buyer values)',
              quality: [
                'Every theme mapped to at least one buyer value — orphan themes flagged',
                'Alignment strength rated (strong / moderate / weak) with rationale',
                'Buyer values without a corresponding theme identified — coverage gap',
                'Themes that don\'t resonate with any buyer value challenged or removed'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'SAL-04.1.3',
          name: 'Test each theme against competitive positioning — does this differentiate us from the incumbent and key competitors?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-04.1.1', artifact: 'Draft win themes register' },
            { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
            { from: 'SAL-02.1.3', artifact: 'Incumbent innovation & value-add assessment' },
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' }
          ],
          outputs: [
            {
              name: 'Competitive differentiation assessment per theme',
              format: 'Structured assessment',
              quality: [
                'Each theme assessed: can competitors credibly claim the same thing?',
                'Themes that are genuinely differentiating identified vs those that are table stakes',
                'Counter-strategies and ghost themes (from SAL-03) cross-referenced — do our themes neutralise competitor claims?',
                'Transformational disruption themes explicitly tested — do they create clear competitive separation?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-04.1.4',
          name: 'Ensure each theme is evidence-backed — do we have credentials, case studies, or demonstrable capability to substantiate this claim?',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Bid Manager / SMEs', i: 'Bid Coordinator' },
          inputs: [
            { from: 'SAL-04.1.1', artifact: 'Draft win themes register' },
            { from: 'SAL-02.3.3', artifact: 'Capability gap assessment' },
            { external: true, artifact: 'Existing case studies, credentials, CVs, and evidence library' }
          ],
          outputs: [
            {
              name: 'Evidence substantiation assessment per theme',
              format: 'Structured assessment',
              quality: [
                'Each theme assessed for evidence strength — proven, partial, or aspirational',
                'Specific evidence items identified or flagged as gaps for each theme',
                'Themes with no credible evidence basis challenged — can we stand this up in a proposal?',
                'Evidence gaps fed forward to SOL-10 (evidence strategy) for resolution'
              ]
            }
          ],
          effort: 'Low',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'SAL-04.2',
      name: 'Win Theme Refinement & Messaging',
      description: 'Refine themes against ITT documentation, develop clear messaging for each theme that informs solution development, commercial proposition, and storyboard drafting',

      tasks: [
        {
          id: 'SAL-04.2.1',
          name: 'Refine themes against ITT documentation — align language, scope, and emphasis to the actual requirement and specification',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Bid Manager', i: 'Solution Architect' },
          inputs: [
            { from: 'SAL-04.1.1', artifact: 'Draft win themes register' },
            { from: 'SAL-04.1.2', artifact: 'Buyer values alignment assessment' },
            { from: 'SAL-04.1.3', artifact: 'Competitive differentiation assessment' },
            { from: 'SAL-04.1.4', artifact: 'Evidence substantiation assessment' },
            { external: true, artifact: 'ITT documentation — scope, requirements, specification' }
          ],
          outputs: [
            {
              name: 'Refined win themes with ITT alignment',
              format: 'Structured register (updated)',
              quality: [
                'Themes rewritten in language that mirrors ITT terminology and client vocabulary',
                'Each theme scoped to the actual requirement — not broader than what the bid covers',
                'Themes prioritised based on testing (buyer values, differentiation, evidence) — not all equal weight',
                'Themes that failed testing removed or substantially reworked'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-04.2.2',
          name: 'Develop clear messaging per theme — concise statements that inform solution design, commercial proposition, and storyboard structure',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-04.2.1', artifact: 'Refined win themes with ITT alignment' }
          ],
          outputs: [
            {
              name: 'Win theme messaging pack',
              format: 'Structured messaging document',
              quality: [
                'Each theme has a clear, concise headline message usable by proposal authors',
                'Supporting narrative for each theme — what it means, why it matters to the client, how we deliver it',
                'Messaging links to solution design implications — what must the solution demonstrate to support this theme?',
                'Messaging links to commercial proposition — what must the pricing approach reflect?',
                'Messages are written for the evaluator — not internal shorthand'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-04.2.3',
          name: 'Validate win themes and messaging with bid team — confirm for capture plan lock',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SAL-04.2.2', artifact: 'Win theme messaging pack' },
            { from: 'SAL-04.2.1', artifact: 'Refined win themes with ITT alignment' }
          ],
          outputs: [
            {
              name: 'Win theme document (validated — activity primary output)',
              format: 'Document / structured register with messaging',
              quality: [
                'Bid team has reviewed and challenged — not single-author opinion',
                'Each theme confirmed as differentiated, buyer-relevant, evidence-backed, and ITT-aligned',
                'Messaging confirmed as clear and usable by solution architects, commercial leads, and proposal authors',
                'Themes prioritised — primary vs secondary — to guide emphasis in the response',
                'Downstream consumers identified and briefed: SAL-05 (scoring strategy), SAL-06 (capture plan lock), BM-10 (storyboard), SOL-03 (solution design)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Win theme document',
      format: 'Document / structured register with messaging',
      quality: [
        'Win themes identified (3–5), tested, and prioritised',
        'Each theme tested against buyer values, competitive positioning, and evidence availability',
        'Themes refined against ITT documentation — language, scope, and emphasis aligned',
        'Clear messaging per theme — headline, narrative, solution implications, commercial implications',
        'Themes validated by bid team — not single-author opinion',
        'Messaging usable by solution architects, commercial leads, and proposal authors without further interpretation'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SAL-05', consumes: 'Win theme document', usage: 'Scoring strategy aligned to ensure win themes are reflected in high-scoring evaluation sections' },
    { activity: 'SAL-06', consumes: 'Win theme document', usage: 'Capture plan lock incorporates confirmed win themes and messaging' },
    { activity: 'SOL-03', consumes: 'Win theme document', usage: 'Target operating model design shaped by win theme messaging and solution implications' },
    { activity: 'COM-01', consumes: 'Win theme document', usage: 'Should-cost model reflects commercial implications of win themes (e.g., investment, gain share)' },
    { activity: 'BM-10', consumes: 'Win theme document', usage: 'Storyboard structure built around win theme messaging and prioritisation' }
  ]
}
```

---

## SAL-05 — Evaluation Criteria Mapping & Scoring Strategy

```javascript
{
  id: 'SAL-05',
  name: 'Evaluation criteria mapping & scoring strategy',
  workstream: 'SAL',
  phase: 'DEV',
  role: 'Bid Manager',                     // Shifts from Capture Lead — this is bid mechanics, not sales intelligence
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED emphasis — evaluation is typically 60-70% team quality
  //   (CVs, experience, credentials). Score gap analysis shifts from solution capability gaps
  //   to team credential gaps. L2.2 scoring strategy must reflect CV-weighted evaluation.
  //   Guidance text should note: "For consulting, the team IS the primary scoring dimension."
  output: 'Evaluation criteria matrix with scoring approach',
  dependencies: ['SAL-04'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires evaluation methodology expertise

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-04', artifact: 'Win theme document' },
    { from: 'SAL-01.2.1', artifact: 'Buyer values register', note: 'Context for what the client values — distinct from how they formally score' },
    { from: 'SAL-03', artifact: 'Competitive landscape assessment', note: 'Where competitors may outscore us' },
    { external: true, artifact: 'ITT evaluation methodology — criteria, weightings, scoring model, pass/fail thresholds' },
    { external: true, artifact: 'Client marking scheme / scoring guidance (if published)', note: 'Optional — not all procurements provide granular scoring guidance' },
    { external: true, artifact: 'ITT response structure — questions, word/page limits, submission requirements' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SAL-05.1',
      name: 'Evaluation Framework Analysis',
      description: 'Understand the rules of the game — how will evaluators mark, what are the weightings, where are the thresholds, and what does a maximum-scoring response look like?',

      tasks: [
        {
          id: 'SAL-05.1.1',
          name: 'Deconstruct the ITT evaluation methodology — criteria, weightings, scoring model, pass/fail thresholds, hurdle marks, moderation process',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Commercial Lead' },
          inputs: [
            { external: true, artifact: 'ITT evaluation methodology — criteria, weightings, scoring model, pass/fail thresholds' },
            { external: true, artifact: 'Client marking scheme / scoring guidance (if published)' }
          ],
          outputs: [
            {
              name: 'Evaluation methodology breakdown',
              format: 'Structured analysis',
              quality: [
                'All evaluation criteria identified with published weightings',
                'Scoring model documented — percentage, points, banded, ranked, or hybrid',
                'Pass/fail thresholds and hurdle marks identified per section (if any)',
                'Quality/price split documented with calculation methodology',
                'Moderation and consensus process noted (if published)',
                'Ambiguities or gaps in the published methodology flagged for clarification (feeds SAL-07)'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-05.1.2',
          name: 'Map evaluation criteria to response sections — which question is worth how many marks, and what proportion of the total?',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Solution Architect' },
          inputs: [
            { from: 'SAL-05.1.1', artifact: 'Evaluation methodology breakdown' },
            { external: true, artifact: 'ITT response structure — questions, word/page limits, submission requirements' }
          ],
          outputs: [
            {
              name: 'Evaluation criteria matrix',
              format: 'Matrix (response sections × criteria × weightings)',
              quality: [
                'Every response section mapped to its evaluation criteria and weighting',
                'Mark value calculated per section — absolute points and percentage of total quality score',
                'Word/page limits mapped against marks available — marks-per-page ratio identified',
                'Sections ranked by marks concentration — where the outcome will be decided',
                'Any sections with disproportionate effort-to-marks ratio flagged'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-05.1.3',
          name: 'Where client marking scheme exists, analyse granular scoring guidance — what does a top-scoring response look like per criterion?',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead / Solution Architect', i: 'Writers' },
          inputs: [
            { from: 'SAL-05.1.2', artifact: 'Evaluation criteria matrix' },
            { external: true, artifact: 'Client marking scheme / scoring guidance (if published)' }
          ],
          outputs: [
            {
              name: 'Scoring guidance analysis per section',
              format: 'Per-section structured analysis',
              quality: [
                'Where marking scheme exists: grade descriptors analysed — what distinguishes "outstanding" from "good" from "acceptable"?',
                'Key differentiating phrases and expectations extracted per grade band',
                'Where no marking scheme: evaluation criteria interpreted to infer what evaluators will look for',
                'Actionable guidance for writers: what must each response demonstrate to achieve maximum marks'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SAL-05.2',
      name: 'Scoring Optimisation Strategy',
      description: 'Develop the strategy to maximise our score — where to concentrate effort, how to align win themes to high-value sections, and where we have scoring gaps to mitigate',

      tasks: [
        {
          id: 'SAL-05.2.1',
          name: 'Analyse marks concentration — identify the high-value sections that disproportionately drive the outcome',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-05.1.2', artifact: 'Evaluation criteria matrix' },
            { from: 'SAL-05.1.3', artifact: 'Scoring guidance analysis per section' }
          ],
          outputs: [
            {
              name: 'Marks concentration analysis',
              format: 'Prioritised assessment',
              quality: [
                'Sections categorised by strategic importance — high-value (must win), medium (must be strong), low (must pass)',
                'Effort allocation guidance — where to invest disproportionate writing and review effort',
                'Hurdle risk sections identified — where failure to meet threshold eliminates regardless of total score',
                'Quality/price interaction modelled — what quality score do we need to win at our expected price point?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-05.2.2',
          name: 'Conduct score gap analysis — can we realistically score 100% in each section, and if not, why not, and what is the mitigation?',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead / Solution Architect / Commercial Lead', i: 'Partner Lead' },
          inputs: [
            { from: 'SAL-05.1.3', artifact: 'Scoring guidance analysis per section' },
            { from: 'SAL-05.2.1', artifact: 'Marks concentration analysis' },
            { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
            { from: 'SAL-04.1.4', artifact: 'Evidence substantiation assessment per theme' }
          ],
          outputs: [
            {
              name: 'Score gap analysis',
              format: 'Per-section structured assessment',
              quality: [
                'Each section assessed: can we credibly score maximum marks? (yes / partial / no)',
                'Where gaps exist: root cause identified — missing credentials, capability gap, lack of track record, compliance limitation',
                'Mitigation strategy per gap — partnering, subcontracting, recruitment, capability development, alternative evidence',
                'Residual risk after mitigation assessed — can the gap be fully closed or must we accept a scoring deficit?',
                'Impact quantified — what is the points cost of each unmitigated gap on total score?',
                'Critical gaps escalated — any that fundamentally threaten competitiveness flagged for go/no-go consideration'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SAL-05.2.3',
          name: 'Develop scoring strategy per section — what must each response demonstrate to achieve maximum marks, incorporating gap mitigations',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead / Solution Architect', i: 'Writers' },
          inputs: [
            { from: 'SAL-05.2.1', artifact: 'Marks concentration analysis' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' },
            { from: 'SAL-05.1.3', artifact: 'Scoring guidance analysis per section' }
          ],
          outputs: [
            {
              name: 'Per-section scoring strategy',
              format: 'Structured strategy per response section',
              quality: [
                'Each section has a clear scoring objective — target grade band and rationale',
                'Key content requirements identified per section to achieve target score',
                'Gap mitigations incorporated — where we cannot score maximum, the alternative approach is specified',
                'Win theme integration points identified — which themes to emphasise in which sections'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-05.2.4',
          name: 'Align win themes to evaluation sections — ensure our differentiators land where the marks are',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Solution Architect' },
          inputs: [
            { from: 'SAL-04', artifact: 'Win theme document' },
            { from: 'SAL-05.2.3', artifact: 'Per-section scoring strategy' },
            { from: 'SAL-05.2.1', artifact: 'Marks concentration analysis' }
          ],
          outputs: [
            {
              name: 'Win theme integration map',
              format: 'Matrix (themes × response sections)',
              quality: [
                'Every win theme mapped to the response sections where it will be articulated',
                'High-value sections have at least one primary win theme assigned',
                'Theme coverage is balanced — no theme orphaned from high-scoring sections',
                'Feeds directly into BM-10 storyboard structure and the win theme integration heatmap in the product'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'SAL-05.2.5',
          name: 'Confirm scoring strategy with bid team for capture plan lock',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SAL-05.2.1', artifact: 'Marks concentration analysis' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' },
            { from: 'SAL-05.2.3', artifact: 'Per-section scoring strategy' },
            { from: 'SAL-05.2.4', artifact: 'Win theme integration map' }
          ],
          outputs: [
            {
              name: 'Evaluation criteria matrix with scoring approach (validated — activity primary output)',
              format: 'Document / structured matrix with strategy',
              quality: [
                'Bid team has reviewed and challenged — not single-author opinion',
                'Score gap mitigations accepted or escalated — no unaddressed critical gaps',
                'Scoring strategy aligned with win themes and commercial approach',
                'Effort allocation confirmed — team understands where to concentrate',
                'Downstream consumers briefed: BM-07 (quality management), BM-10 (storyboard), writers'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Evaluation criteria matrix with scoring approach',
      format: 'Document / structured matrix with strategy',
      quality: [
        'Evaluation methodology fully deconstructed — criteria, weightings, scoring model, thresholds',
        'Every response section mapped to criteria and marks value',
        'Scoring guidance analysed — what top-scoring responses look like per section',
        'Marks concentration identified — high-value sections prioritised',
        'Score gap analysis complete — gaps identified, root-caused, and mitigated',
        'Per-section scoring strategy with target grade bands and content requirements',
        'Win themes aligned to evaluation sections — differentiators land where marks are',
        'Validated by bid team — not single-author opinion'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SAL-06', consumes: 'Evaluation criteria matrix with scoring approach', usage: 'Capture plan lock incorporates scoring strategy and gap mitigations' },
    { activity: 'BM-07', consumes: 'Evaluation criteria matrix', usage: 'Quality plan builds page budgets and review criteria from marks analysis' },
    { activity: 'BM-10', consumes: 'Win theme integration map + per-section scoring strategy', usage: 'Storyboard structure shaped by where marks are concentrated and which themes to emphasise where' },
    { activity: 'SOL-10', consumes: 'Score gap analysis', usage: 'Evidence strategy prioritises credentials and case studies to close scoring gaps' },
    { activity: 'SUP-01', consumes: 'Score gap analysis', usage: 'Supply chain strategy informed by gaps requiring partner credentials or capability' }
  ]
}
```

---

## SAL-06 — Capture Plan Finalisation & Win Strategy Lock

```javascript
{
  id: 'SAL-06',
  name: 'Capture plan finalisation & win strategy lock',
  workstream: 'SAL',
  phase: 'DEV',
  role: 'Bid Director',                    // Elevated — this is the strategic go/no-go, not operational
  // ARCHETYPE NOTES:
  // Technology/Digital: Minor — L2.3 consortium strategy may be sole bidder or tech partner,
  //   not subcontractor consortium. Work breakdown is simpler.
  // Consulting/Advisory: Minor — L2.3 consortium uses associate networks, not formal
  //   subcontracting. Partnership model is lighter. Work breakdown focuses on team
  //   composition, not scope allocation between organisations.
  output: 'Capture plan (locked) — METHODOLOGY GATE',
  dependencies: ['SAL-04', 'SAL-05', 'SAL-10'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — senior leadership synthesis
  // Note: this is a METHODOLOGY GATE. The capture plan must reach "assured" before
  // downstream activities (SOL-01, BM-01, GOV-01) can proceed.
  // The fundamental question: based on everything we now know — capture intelligence,
  // ITT documentation, competitive position, stakeholder relationships, scoring landscape,
  // solution feasibility, commercial risk — should we bid, and if so, with what strategy?

  // ── Structured inputs ──────────────────────────────────────────────
  // This is the synthesis activity — it consumes the primary output from every
  // upstream SAL activity plus cross-product inputs from the qualifier and win strategy.
  inputs: [
    { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
    { from: 'SAL-02', artifact: 'Incumbent performance assessment' },
    { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
    { from: 'SAL-04', artifact: 'Win theme document' },
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' },
    { from: 'SAL-10', artifact: 'Stakeholder relationship map & engagement plan' },
    { external: true, artifact: 'ITT documentation pack — specification, contract, evaluation methodology, instructions' },
    { external: true, artifact: 'Resource availability and capacity forecast' },
    { external: true, artifact: 'Organisational strategic plan and sector growth targets' },
    { crossProduct: 'PWIN-COACH', artifact: 'PWIN qualification score and category assessments', optional: true,
      note: 'From PWIN Coach product — 24-question qualification across competitive strategy, relationship superiority, value proposition alignment, pursuit momentum. Provides quantified baseline.' },
    { crossProduct: 'PWIN-WINSTRAT', artifact: 'Locked win strategy and capture plan', optional: true,
      note: 'From Win Strategy product if capture phase completed — strategy to validate against ITT reality' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SAL-06.1',
      name: 'Capture Effectiveness & ITT Alignment Assessment',
      description: 'Assess how well our capture phase influenced the procurement — compare what the ITT says against what we were trying to shape. Once the ITT lands, influence is over. This is the reality check.',

      tasks: [
        {
          id: 'SAL-06.1.1',
          name: 'Assess capture effectiveness — how well does the ITT align to what our capture activity was trying to influence? Evaluation criteria, solution scope, commercial terms, transition approach',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager', i: 'Solution Architect' },
          inputs: [
            { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
            { from: 'SAL-10', artifact: 'Stakeholder relationship map & engagement plan' },
            { external: true, artifact: 'ITT documentation pack — specification, contract, evaluation methodology, instructions' },
            { crossProduct: 'PWIN-WINSTRAT', artifact: 'Locked win strategy and capture plan', optional: true }
          ],
          outputs: [
            {
              name: 'Capture effectiveness assessment',
              format: 'Structured assessment',
              quality: [
                'Each area of capture influence assessed: evaluation criteria, solution scope, commercial terms, transition provisions',
                'Alignment rated per area — strong (ITT reflects our influence), partial (some alignment), weak (ITT went a different direction)',
                'Surprises and deviations from expectations identified — what did the client do that we didn\'t expect?',
                'Implications for win strategy — where must we adapt vs where can we proceed as planned?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-06.1.2',
          name: 'Conduct rapid ITT documentation analysis — requirements breakdown, contract red lines, payment mechanism, SLA framework, transition provisions',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Commercial Lead / Legal / Solution Architect', i: 'Capture Lead' },
          inputs: [
            { external: true, artifact: 'ITT documentation pack — specification, contract, evaluation methodology, instructions' },
            { from: 'SAL-02', artifact: 'Incumbent performance assessment', note: 'Transition risk context' }
          ],
          outputs: [
            {
              name: 'ITT documentation analysis summary',
              format: 'Structured briefing',
              quality: [
                'Requirements scope and complexity characterised — what is being asked for at a strategic level?',
                'Contract red lines and non-negotiable terms identified',
                'Payment mechanism and financial model characterised — fixed price, cost-plus, gain share, payment profile',
                'SLA framework and performance regime characterised — severity, consequences, earn-back provisions',
                'Transition and mobilisation expectations identified — timeline, TUPE obligations, asset transfer',
                'Key risks and showstoppers flagged for qualification assessment'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SAL-06.2',
      name: 'Full Pursuit Qualification & PWIN Scoring',
      description: 'The 360-degree qualification — competitive, stakeholder, solution, commercial, risk, resources, bid cost. Traditionally takes weeks; with AI acceleration the team arrives at go/no-go with dramatically more information already synthesised.',

      tasks: [
        {
          id: 'SAL-06.2.1',
          name: 'Complete Deal Qualification Checklist (DQC) — attractiveness, deliverability, risk, win likelihood, informed by ITT documentation analysis',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Commercial Lead / Solution Architect / Legal', i: 'Bid Board' },
          inputs: [
            { from: 'SAL-06.1.2', artifact: 'ITT documentation analysis summary' },
            { from: 'SAL-02', artifact: 'Incumbent performance assessment' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' },
            { crossProduct: 'PWIN-COACH', artifact: 'PWIN qualification score and category assessments', optional: true }
          ],
          outputs: [
            {
              name: 'Deal Qualification Checklist (DQC)',
              format: 'Structured checklist with commentary',
              quality: [
                'Attractiveness assessed — strategic value, margin potential, pipeline fit, growth opportunity',
                'Deliverability assessed — solution feasibility, resource availability, capability, partner readiness',
                'Risk assessed — contract terms, commercial risk, transition complexity, legal exposure',
                'Win likelihood assessed — competitive position, stakeholder alignment, scoring gaps, incumbent stickiness',
                'Each dimension scored with evidence basis — not gut feel',
                'Showstoppers explicitly called out — any single dimension that makes this unwinnable or undeliverable'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SAL-06.2.2',
          name: 'Assess strategic fit against sector portfolio and growth plan — is this the right opportunity for us right now?',
          raci: { r: 'Bid Director', a: 'Partner / Senior Responsible Executive', c: 'Capture Lead', i: 'Account Manager' },
          inputs: [
            { from: 'SAL-06.2.1', artifact: 'Deal Qualification Checklist (DQC)' },
            { external: true, artifact: 'Organisational strategic plan and sector growth targets' }
          ],
          outputs: [
            {
              name: 'Strategic fit assessment',
              format: 'Structured assessment',
              quality: [
                'Fit against sector portfolio assessed — does this opportunity strengthen our market position?',
                'Resource opportunity cost considered — what else could this team be working on?',
                'Pipeline balance assessed — does this create over-concentration in one sector or client?',
                'Reputational risk considered — is this an opportunity that enhances or risks our brand?'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'SAL-06.2.3',
          name: 'Score PWIN against all dimensions — competitive position, stakeholder relationships, solution readiness, scoring landscape, transition risk, transformational opportunity',
          raci: { r: 'Bid Director', a: 'Partner / Senior Responsible Executive', c: 'Capture Lead / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-06.2.1', artifact: 'Deal Qualification Checklist (DQC)' },
            { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
            { from: 'SAL-10', artifact: 'Stakeholder relationship map & engagement plan' },
            { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' },
            { from: 'SAL-02', artifact: 'Incumbent performance assessment' },
            { crossProduct: 'PWIN-COACH', artifact: 'PWIN qualification score and category assessments', optional: true }
          ],
          outputs: [
            {
              name: 'PWIN score and rationale',
              format: 'Quantified score with structured rationale',
              quality: [
                'PWIN score calculated (%) with confidence band',
                'Score broken down by dimension — competitive, relationship, solution, commercial, delivery',
                'Each dimension has evidence basis from upstream activities — not estimated from experience alone',
                'Comparison to PWIN Coach baseline score (if available) — has our position improved or deteriorated since qualification?',
                'Key swing factors identified — what would move PWIN up or down most?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-06.2.4',
          name: 'Synthesise win strategy — the integrated narrative tying win themes, scoring strategy, competitive positioning, stakeholder engagement, and transformational approach into a coherent plan',
          raci: { r: 'Bid Director', a: 'Partner / Senior Responsible Executive', c: 'Capture Lead / Solution Architect / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-04', artifact: 'Win theme document' },
            { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' },
            { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
            { from: 'SAL-10', artifact: 'Stakeholder relationship map & engagement plan' },
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' },
            { from: 'SAL-06.1.1', artifact: 'Capture effectiveness assessment' }
          ],
          outputs: [
            {
              name: 'Win strategy narrative',
              format: 'Structured strategy document',
              quality: [
                'Winning approach articulated — full frontal on price + solution, differentiation play, defensive rebid, or transformational disruption',
                'Win themes integrated with scoring strategy — how each theme lands in the evaluation framework',
                'Competitive counter-strategy embedded — how we neutralise each key competitor',
                'Stakeholder engagement strategy aligned — messaging and approach per key stakeholder',
                'Transformation and innovation strategy incorporated where applicable',
                'Strategy is coherent — no contradictions between commercial approach, solution, and win themes'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SAL-06.3',
      name: 'Consortium Design & Partnership Strategy',
      description: 'Make the strategic decision on consortium structure and partnership model — who we partner with, in what structure, and why that design is a competitive advantage. This is a win strategy decision, not an afterthought. It feeds SUP-01 (partner identification) and COM-03 (commercial structure).',

      tasks: [
        {
          id: 'SAL-06.3.1',
          name: 'Define the consortium strategy — prime/sub, JV, SPV, or sole bidder — with rationale tied to win strategy and competitive positioning',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Commercial Lead / Capture Lead', i: 'Legal' },
          inputs: [
            { from: 'SAL-06.2.4', artifact: 'Win strategy narrative' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis', note: 'Where we need partner capability to close scoring gaps' },
            { from: 'SAL-02.3.3', artifact: 'Capability gap assessment', note: 'Where we need partner capability to deliver transformation' },
            { from: 'SAL-01.1.4', artifact: 'Client supplier landscape map', note: 'Who the client already works with, framework incumbents' }
          ],
          outputs: [
            {
              name: 'Consortium strategy',
              format: 'Structured strategy paper',
              quality: [
                'Consortium model defined — prime/sub, JV, SPV, or sole bidder — with rationale',
                'Strategic rationale for the model linked to win strategy — how this structure creates competitive advantage',
                'Client perception considered — does this model signal the right things to the evaluators?',
                'Risk and governance implications of the model assessed — JV/SPV complexity vs prime/sub simplicity',
                'Alignment to procurement requirements confirmed — some procurements mandate or restrict certain models'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-06.3.2',
          name: 'Identify required partner capabilities — mapped to score gaps, capability gaps, and solution components that we cannot deliver alone',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'Partner Lead' },
          inputs: [
            { from: 'SAL-06.3.1', artifact: 'Consortium strategy' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' },
            { from: 'SAL-02.3.3', artifact: 'Capability gap assessment' },
            { from: 'SOL-01', artifact: 'Requirements interpretation document', note: 'Soft input — solution areas requiring partner capability' }
          ],
          outputs: [
            {
              name: 'Partner capability requirements',
              format: 'Structured requirements register',
              quality: [
                'Every capability gap that requires a partner is documented — what we need and why',
                'Each requirement linked to the scoring or solution gap it addresses',
                'Target partner profile defined per requirement — type of organisation, scale, credentials, track record',
                'Priority ranked — critical partners (without whom we cannot bid) vs valuable partners (who strengthen the bid)'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-06.3.3',
          name: 'Define the target delivery model across the consortium — who owns what scope, high-level work breakdown, accountability structure',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Solution Architect / Commercial Lead', i: 'Delivery Director' },
          inputs: [
            { from: 'SAL-06.3.1', artifact: 'Consortium strategy' },
            { from: 'SAL-06.3.2', artifact: 'Partner capability requirements' },
            { from: 'SOL-03', artifact: 'Target operating model', note: 'Soft input — solution structure that the consortium must deliver' }
          ],
          outputs: [
            {
              name: 'Consortium delivery model and work breakdown',
              format: 'High-level work breakdown with accountability map',
              quality: [
                'Scope allocation defined per delivery agent — who owns which solution components and service lines',
                'Accountability and interface model defined — who is responsible to the client for what',
                'Dependencies between consortium members identified — where integration risk exists',
                'High-level enough to brief potential partners — not so detailed it constrains partner creativity',
                'Feeds SUP-01 (partner identification brief) and COM-03 (commercial structure and pricing requests)'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SAL-06.4',
      name: 'Capture Plan Assembly & Bid Mandate Lock',
      description: 'Assemble the full 360-degree capture plan document, prepare the bid mandate for governance, and formally lock the strategy as the baseline for the bid',

      tasks: [
        {
          id: 'SAL-06.4.1',
          name: 'Assemble capture plan — the locked strategic baseline document covering all dimensions including consortium strategy',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
          inputs: [
            { from: 'SAL-06.1.1', artifact: 'Capture effectiveness assessment' },
            { from: 'SAL-06.1.2', artifact: 'ITT documentation analysis summary' },
            { from: 'SAL-06.2.1', artifact: 'Deal Qualification Checklist (DQC)' },
            { from: 'SAL-06.2.2', artifact: 'Strategic fit assessment' },
            { from: 'SAL-06.2.3', artifact: 'PWIN score and rationale' },
            { from: 'SAL-06.2.4', artifact: 'Win strategy narrative' },
            { from: 'SAL-06.3.1', artifact: 'Consortium strategy' },
            { from: 'SAL-06.3.2', artifact: 'Partner capability requirements' },
            { from: 'SAL-06.3.3', artifact: 'Consortium delivery model and work breakdown' }
          ],
          outputs: [
            {
              name: 'Capture plan document',
              format: 'Comprehensive strategy document',
              quality: [
                'Covers all dimensions: customer intelligence, competitive landscape, stakeholder position, win strategy, scoring approach, solution direction, commercial framework, consortium strategy, risk, resources',
                'Consortium strategy and work breakdown documented — who we partner with, in what structure, who owns what scope',
                'Requirements understanding demonstrated — what the client is asking for at a strategic level',
                'Contract and commercial risk profile documented — red lines, payment mechanism, SLA regime',
                'Solution direction articulated — what we believe we can deliver and how',
                'Resource plan included — team, skills, cost of bid at each phase',
                'Timeline and key milestones documented',
                'All upstream activity outputs referenced — not duplicated but consolidated and synthesised'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-06.4.2',
          name: 'Prepare formal Bid Mandate for Bid Board approval — budget, resource, win strategy, consortium, risk, PWIN, go/no-go recommendation',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Commercial Lead / Legal', i: 'Partner' },
          inputs: [
            { from: 'SAL-06.4.1', artifact: 'Capture plan document' },
            { external: true, artifact: 'Resource availability and capacity forecast' }
          ],
          outputs: [
            {
              name: 'Bid Mandate document',
              format: 'Governance decision paper',
              quality: [
                'Clear go/no-go recommendation with rationale',
                'PWIN score and key swing factors presented',
                'Bid cost quantified — resource investment at each phase',
                'Key risks and mitigations summarised — not a full risk register but the strategic risks that affect the go/no-go',
                'Win strategy summary — the one-page version of what we plan to do and why',
                'Resource ask specified — named team, skills, availability, security clearance requirements',
                'Conditions for bid (if any) — e.g. "proceed only if partner X confirms teaming agreement"'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-06.4.3',
          name: 'Confirm lock — capture plan baselined, win strategy locked, consortium strategy locked, methodology gate passed. Feeds GOV-01 (Pursuit Approval)',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: null, i: 'Bid Team (collective)' },
          inputs: [
            { from: 'SAL-06.4.1', artifact: 'Capture plan document' },
            { from: 'SAL-06.4.2', artifact: 'Bid Mandate document' }
          ],
          outputs: [
            {
              name: 'Capture plan (locked) — activity primary output — METHODOLOGY GATE',
              format: 'Baselined document with formal sign-off',
              quality: [
                'Capture plan formally baselined — this is the strategic reference point for the entire bid',
                'Win strategy locked — downstream activities (SOL, COM, PRD) build against this strategy',
                'Bid mandate approved or conditionally approved — organisational commitment secured',
                'Bid team briefed on locked strategy — all workstream leads understand the direction',
                'Any conditions for bid documented and assigned for resolution',
                'GOV-01 (Pursuit Approval) can now proceed with formal governance review'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Capture plan (locked) — METHODOLOGY GATE',
      format: 'Baselined strategy document with bid mandate',
      quality: [
        'Capture effectiveness assessed — ITT alignment to capture influence',
        'ITT documentation analysed — requirements, contract, payment mechanism, SLAs, transition',
        'Deal qualification complete — attractiveness, deliverability, risk, win likelihood',
        'Strategic fit confirmed against portfolio and growth plan',
        'PWIN scored with evidence basis across all dimensions',
        'Win strategy synthesised — coherent narrative integrating themes, scoring, competitive positioning, stakeholders',
        'Consortium strategy defined — structure, partner capabilities, work breakdown as competitive advantage',
        'Capture plan assembled as 360-degree strategic baseline',
        'Bid mandate prepared with go/no-go recommendation, bid cost, and resource ask',
        'Formally locked and baselined — methodology gate passed'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'GOV-01', consumes: 'Capture plan (locked) + Bid Mandate', usage: 'Pursuit Approval governance gate — formal organisational go/no-go' },
    { activity: 'SOL-01', consumes: 'Capture plan (locked)', usage: 'Requirements analysis starts from locked strategic baseline and ITT documentation analysis' },
    { activity: 'BM-01', consumes: 'Capture plan (locked)', usage: 'Kickoff planning uses capture plan as the strategy briefing for the bid team' },
    { activity: 'BM-10', consumes: 'Win strategy narrative', usage: 'Storyboard development builds response structure around locked win strategy' },
    { activity: 'BM-09', consumes: 'Capture plan (locked)', usage: 'Competitive dialogue preparation informed by locked strategy and stakeholder assessment' },
    { activity: 'SOL-03', consumes: 'Win strategy narrative', usage: 'Target operating model design shaped by locked win strategy and solution direction' },
    { activity: 'COM-01', consumes: 'Capture plan (locked)', usage: 'Should-cost model informed by commercial framework and payment mechanism from capture plan' },
    { activity: 'SUP-01', consumes: 'Consortium strategy + partner capability requirements', usage: 'Partner identification has a clear brief on who to approach and why' },
    { activity: 'COM-03', consumes: 'Consortium delivery model and work breakdown', usage: 'Commercial structure and pricing requests built on locked consortium design' }
  ]
}
```

---

## SAL-07 — Pre-submission Clarification Strategy & Drafting

```javascript
{
  id: 'SAL-07',
  name: 'Pre-submission clarification strategy & drafting',
  workstream: 'SAL',
  phase: 'DEV',
  role: 'Capture Lead',                    // Strategic activity — Capture Lead not Bid Manager
  output: 'Clarification question register (prioritised)',
  dependencies: ['SAL-04', 'SOL-01'],
  effortDays: 3,
  teamSize: 2,
  parallelisationType: 'P',               // Parallelisable — questions harvested from multiple workstreams simultaneously
  // Note: this activity sits in SAL (not BM) because it is fundamentally about competitive
  // strategy, not operational question management. BM-14/15 handle the tracking, submission,
  // and impact analysis of clarifications. SAL-07 is about exploiting the clarification process
  // as a competitive weapon.
  //
  // Two playbooks depending on position:
  // INCUMBENT: minimise disclosure. Provide minimum information as late as possible — TUPE data,
  // CHEAPY lists, performance records. Delay to disrupt challengers' pricing and transition planning.
  // Don't volunteer anything. What you DON'T disclose is as important as what you ask.
  // CHALLENGER: maximise exposure of incumbent weaknesses. Ask questions that force transparency
  // on service performance, staffing levels, contract compliance. Elevate issues the client
  // has been tolerating. Use questions to create doubt about the status quo.
  //
  // In both cases: what you choose NOT to ask is as strategic as what you do ask.
  // Questions can reveal strategy to competitors if published — framing and timing are critical.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-06.1.2', artifact: 'ITT documentation analysis summary', note: 'Ambiguities, gaps, and red lines flagged during capture plan' },
    { from: 'SAL-06.2.4', artifact: 'Win strategy narrative', note: 'Strategic intent shapes which questions to ask and how to frame them' },
    { from: 'SAL-04', artifact: 'Win theme document', note: 'Questions that test whether evaluation framework rewards our themes' },
    { from: 'SAL-05.2.2', artifact: 'Score gap analysis', note: 'Gaps that could be mitigated by clarification responses' },
    { from: 'SOL-01', artifact: 'Requirements interpretation document', note: 'Technical ambiguities that block solution design' },
    { external: true, artifact: 'ITT documentation pack — specification, contract, evaluation methodology, instructions' },
    { external: true, artifact: 'Clarification submission rules — deadline, format, portal, publication policy (anonymous or attributed)' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SAL-07.1',
      name: 'Clarification Need Identification',
      description: 'Harvest clarification needs from all workstreams — technical, commercial, legal, strategic — and consolidate into a single register before prioritisation',

      tasks: [
        {
          id: 'SAL-07.1.1',
          name: 'Harvest clarification needs from ITT documentation analysis — ambiguities, contradictions, gaps, and red lines flagged during SAL-06',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
          inputs: [
            { from: 'SAL-06.1.2', artifact: 'ITT documentation analysis summary' },
            { external: true, artifact: 'ITT documentation pack — specification, contract, evaluation methodology, instructions' }
          ],
          outputs: [
            {
              name: 'Documentation-driven clarification needs',
              format: 'Structured register',
              quality: [
                'Every ambiguity, contradiction, and gap flagged in SAL-06.1.2 reviewed for clarification need',
                'Contract red lines that require negotiation or clarification identified',
                'Evaluation methodology ambiguities that affect scoring strategy captured',
                'Each need categorised: contractual / evaluation / specification / procedural'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-07.1.2',
          name: 'Harvest clarification needs from solution and commercial workstreams — technical ambiguity, contractual risk, pricing assumptions that block progress',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Solution Architect / Commercial Lead / Legal', i: 'Workstream Leads' },
          inputs: [
            { from: 'SOL-01', artifact: 'Requirements interpretation document' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' }
          ],
          outputs: [
            {
              name: 'Workstream-driven clarification needs',
              format: 'Structured register',
              quality: [
                'Technical ambiguities from requirements analysis captured — what blocks solution design?',
                'Commercial and pricing assumptions that need client confirmation identified',
                'Legal and contractual questions from contract review captured',
                'Each need linked to the workstream and activity it impacts — machine-traversable for impact analysis'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'          // Can harvest from multiple workstreams simultaneously
        },
        {
          id: 'SAL-07.1.3',
          name: 'Develop competitive clarification strategy — how to exploit the clarification process as a strategic weapon based on our position (incumbent vs challenger)',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-06.2.4', artifact: 'Win strategy narrative' },
            { from: 'SAL-04', artifact: 'Win theme document' },
            { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
            { from: 'SAL-02', artifact: 'Incumbent performance assessment' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' }
          ],
          outputs: [
            {
              name: 'Competitive clarification strategy',
              format: 'Structured strategy with question register',
              quality: [
                'Position-specific playbook defined — incumbent (minimise disclosure, delay information) or challenger (maximise exposure of incumbent weaknesses)',
                'Strategic questions identified — questions that influence interpretation, test appetite for innovation, or create competitive advantage',
                'Information disclosure strategy defined — what information we will provide, when, and in what form (especially TUPE data, CHEAPY lists, performance records if incumbent)',
                'Timing strategy defined — when to submit information or responses for maximum competitive disruption',
                'Questions that probe score gap mitigations — can the client confirm acceptable alternatives?',
                'Counter-intelligence assessed — what do competitors learn from our questions and what do we learn from theirs?',
                'What NOT to ask explicitly considered — questions we deliberately withhold to avoid revealing our approach or aiding competitors'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'SAL-07.2',
      name: 'Clarification Strategy & Question Drafting',
      description: 'Prioritise, draft, and vet clarification questions — framing for maximum value extraction without revealing strategy to competitors',

      tasks: [
        {
          id: 'SAL-07.2.1',
          name: 'Categorise and prioritise questions by strategic impact — which questions materially affect win probability or solution approach?',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Workstream Leads' },
          inputs: [
            { from: 'SAL-07.1.1', artifact: 'Documentation-driven clarification needs' },
            { from: 'SAL-07.1.2', artifact: 'Workstream-driven clarification needs' },
            { from: 'SAL-07.1.3', artifact: 'Strategic clarification opportunities' }
          ],
          outputs: [
            {
              name: 'Prioritised clarification register (draft)',
              format: 'Structured register with priority ranking',
              quality: [
                'All clarification needs consolidated into single register',
                'Each question categorised: strategic / technical / commercial / legal / procedural',
                'Priority assigned: critical (blocks progress or affects win probability), important (reduces risk or improves solution), nice-to-have (useful but not essential)',
                'Questions that are unlikely to get a useful response identified and deprioritised',
                'Duplicate or overlapping questions consolidated'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-07.2.2',
          name: 'Draft questions with strategic intent — framing that extracts maximum value, exploits competitive position, and controls information disclosure',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Bid Manager / Solution Architect', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-07.2.1', artifact: 'Prioritised clarification register (draft)' },
            { from: 'SAL-07.1.3', artifact: 'Competitive clarification strategy' },
            { external: true, artifact: 'Clarification submission rules — deadline, format, portal, publication policy (anonymous or attributed)' }
          ],
          outputs: [
            {
              name: 'Drafted clarification questions with timing plan',
              format: 'Submission-ready question register with scheduled submission dates',
              quality: [
                'Each question drafted in neutral, professional language that does not telegraph our bid strategy',
                'Strategic questions framed as genuine clarification — not leading or obviously self-serving',
                'Challenger questions that elevate incumbent weakness framed to prompt client transparency without appearing adversarial',
                'Publication risk assessed per question — if all bidders see the answer, does it help or hurt us?',
                'If questions are attributed (not anonymous), sensitivity reviewed — does asking this reveal our approach?',
                'Timing plan defined — which questions to submit early, which to hold, which to time for maximum competitive disruption',
                'Information disclosure schedule defined (if incumbent) — when to provide TUPE data, CHEAPY lists, etc. and in what format',
                'Reference to specific ITT section/clause included per question for traceability'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SAL-07.2.3',
          name: 'Vet and approve clarification register — Bid Director sign-off before submission to BM-14 for submission management',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Capture Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-07.2.2', artifact: 'Drafted clarification questions' }
          ],
          outputs: [
            {
              name: 'Clarification question register (prioritised) — activity primary output',
              format: 'Approved submission-ready register',
              quality: [
                'All questions reviewed and approved by Bid Director',
                'Strategic risk of each question accepted — no questions that inadvertently reveal approach',
                'Priority confirmed — submission order if there is a question limit',
                'Expected value of each answer documented — what will we do with the response?',
                'Handover to BM-14 (clarification submission & response management) confirmed'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Clarification question register (prioritised)',
      format: 'Approved submission-ready register with timing plan',
      quality: [
        'Clarification needs harvested from all workstreams — documentation, solution, commercial, legal, strategic',
        'Competitive clarification strategy defined — position-specific playbook (incumbent vs challenger)',
        'Questions categorised by type and prioritised by strategic impact',
        'Questions drafted with strategic framing — extracts value without revealing approach',
        'Timing and information disclosure strategy defined — what to submit when for maximum competitive advantage',
        'Publication and attribution risk assessed per question',
        'What NOT to ask explicitly considered and documented',
        'All questions vetted and approved by Bid Director',
        'Expected value of each answer documented — what we will do with the response'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'BM-14', consumes: 'Clarification question register (prioritised)', usage: 'Clarification submission and response management — operational handling of submission, tracking, and response logging' },
    { activity: 'BM-15', consumes: 'Clarification question register (prioritised)', usage: 'Impact analysis uses the expected-value documentation to assess whether responses change assumptions (indirect via BM-14)' }
  ]
}
```

---

## SAL-10 — Stakeholder Relationship Mapping & Engagement

```javascript
{
  id: 'SAL-10',
  name: 'Stakeholder relationship mapping & engagement',
  workstream: 'SAL',
  phase: 'DEV',
  role: 'Capture Lead',
  output: 'Stakeholder relationship map & engagement plan',
  dependencies: ['SAL-01'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',                // Specialist — relationship intelligence, not parallelisable

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
    { external: true, artifact: 'Client organisation chart / published structure' },
    { external: true, artifact: 'Previous bid relationship history (CRM, account records)' },
    { external: true, artifact: 'Public domain stakeholder intelligence (LinkedIn, conference appearances, published papers)' },
    { crossProduct: 'PWIN-WINSTRAT', artifact: 'Stakeholder influence assessment', optional: true,
      note: 'From Win Strategy product if capture phase completed — refines existing map rather than building from scratch' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SAL-10.1',
      name: 'Stakeholder Identification & Mapping',
      description: 'Identify all relevant client stakeholders, map their roles in the decision-making unit, and assess influence, disposition, and priorities',

      tasks: [
        {
          id: 'SAL-10.1.1',
          name: 'Identify decision-making unit (DMU) — all stakeholders involved in evaluation, approval, and award',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
            { external: true, artifact: 'Client organisation chart / published structure' },
            { external: true, artifact: 'Previous bid relationship history (CRM, account records)' }
          ],
          outputs: [
            {
              name: 'DMU register',
              format: 'Structured register',
              quality: [
                'All known evaluation panel members, approvers, and influencers identified',
                'Each stakeholder has role, title, organisation unit, and relationship to the requirement',
                'Gaps in knowledge explicitly flagged (unknown panel members, unnamed technical evaluators)',
                'Sources cited for each entry (not guesswork)'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-10.1.2',
          name: 'Assess each stakeholder — influence level, disposition toward us, known priorities and concerns',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager / Partners', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-10.1.1', artifact: 'DMU register' },
            { from: 'SAL-01', artifact: 'Customer intelligence briefing' },
            { external: true, artifact: 'Public domain stakeholder intelligence (LinkedIn, conference appearances, published papers)' }
          ],
          outputs: [
            {
              name: 'Stakeholder influence & disposition map',
              format: 'Matrix (influence × disposition)',
              quality: [
                'Every DMU member assessed on influence (high/medium/low) and disposition (champion/supporter/neutral/sceptic/blocker)',
                'Known priorities and hot-button issues documented per stakeholder',
                'Assessment distinguishes between known facts, inferred positions, and assumptions',
                'Key relationships between stakeholders noted (reporting lines, alliances, tensions)'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-10.1.3',
          name: 'Map existing relationship strength — who knows whom, quality of access, last meaningful contact',
          raci: { r: 'Account Manager', a: 'Capture Lead', c: 'Bid Director / Partners', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-10.1.2', artifact: 'Stakeholder influence & disposition map' },
            { external: true, artifact: 'Previous bid relationship history (CRM, account records)' }
          ],
          outputs: [
            {
              name: 'Relationship strength assessment',
              format: 'Per-stakeholder structured assessment',
              quality: [
                'Each stakeholder scored for relationship strength (strong/developing/weak/none)',
                'Named relationship owner on our side for each stakeholder',
                'Last meaningful contact date and nature recorded',
                'Relationship gaps identified — high-influence stakeholders with weak/no access'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SAL-10.2',
      name: 'Engagement Planning & Execution',
      description: 'Develop targeted engagement strategy per stakeholder, execute engagement activities, and track outcomes to inform win strategy',

      tasks: [
        {
          id: 'SAL-10.2.1',
          name: 'Develop targeted engagement plan — objectives, approach, and messaging per stakeholder',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-10.1.2', artifact: 'Stakeholder influence & disposition map' },
            { from: 'SAL-10.1.3', artifact: 'Relationship strength assessment' },
            { from: 'SAL-01', artifact: 'Customer intelligence briefing' }
          ],
          outputs: [
            {
              name: 'Stakeholder engagement plan',
              format: 'Per-stakeholder action plan',
              quality: [
                'Engagement objective defined per stakeholder (inform / influence / validate / convert)',
                'Approach matched to disposition — different tactics for champions vs sceptics',
                'Key messages aligned to each stakeholder\'s known priorities',
                'Engagement owner assigned and accepted for each stakeholder',
                'Compliance boundaries noted — what engagement is permissible under procurement rules'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SAL-10.2.2',
          name: 'Execute engagement activities and log outcomes — intelligence gained, sentiment shifts, commitments',
          raci: { r: 'Account Manager', a: 'Capture Lead', c: 'Bid Director / Partners', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-10.2.1', artifact: 'Stakeholder engagement plan' }
          ],
          outputs: [
            {
              name: 'Engagement log',
              format: 'Structured activity log',
              quality: [
                'Each engagement recorded: date, stakeholder, owner, channel, outcome',
                'Intelligence gained captured — new information about priorities, concerns, competitive landscape',
                'Sentiment shifts noted — disposition changes from previous assessment',
                'Follow-up actions identified and assigned'
              ]
            }
          ],
          effort: 'High',
          type: 'Iterative'           // Ongoing through pre-bid phase, not a one-shot task
        },
        {
          id: 'SAL-10.2.3',
          name: 'Update stakeholder map and confirm readiness for capture plan lock',
          raci: { r: 'Capture Lead', a: 'Bid Director', c: 'Account Manager', i: null },
          inputs: [
            { from: 'SAL-10.2.2', artifact: 'Engagement log' },
            { from: 'SAL-10.1.2', artifact: 'Stakeholder influence & disposition map' }
          ],
          outputs: [
            {
              name: 'Stakeholder relationship map & engagement plan (validated — activity primary output)',
              format: 'Document / structured register',
              quality: [
                'Stakeholder map updated with latest intelligence from engagements',
                'Disposition and influence assessments refreshed post-engagement',
                'Remaining relationship gaps identified with mitigation plan',
                'Stakeholder intelligence explicitly linked to win strategy implications — which themes resonate with which stakeholders',
                'Assessment reviewed by Bid Director — not single-author opinion'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Stakeholder relationship map & engagement plan',
      format: 'Document / structured register',
      quality: [
        'All DMU members identified with role, influence, and disposition',
        'Relationship strength assessed per stakeholder with named owners',
        'Engagement plan with targeted objectives and messaging per stakeholder',
        'Engagement outcomes logged with intelligence gained and sentiment shifts',
        'Stakeholder intelligence linked to win strategy implications',
        'Validated by Bid Director — not single-author opinion'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SAL-04', consumes: 'Stakeholder relationship map', usage: 'Win themes tailored to resonate with key stakeholder priorities' },
    { activity: 'SAL-06', consumes: 'Stakeholder relationship map & engagement plan', usage: 'Capture plan incorporates stakeholder strategy and relationship readiness assessment' },
    { activity: 'BM-08', consumes: 'Stakeholder relationship map', usage: 'Bid-phase stakeholder comms plan builds on pre-bid relationship map' },
    { activity: 'BM-09', consumes: 'Stakeholder influence & disposition map', usage: 'Competitive dialogue preparation targets key stakeholder concerns' }
  ]
}
```

---

---

## SOL-01 — Requirements Analysis & Interpretation

```javascript
{
  id: 'SOL-01',
  name: 'Requirements analysis & interpretation',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Solution Architect',
  output: 'Requirements interpretation document',
  dependencies: ['SAL-06'],
  effortDays: 5,
  teamSize: 2,
  parallelisationType: 'P',               // Parallelisable — multiple workstream leads can analyse requirements concurrently
  // Note: this is the first activity after capture plan lock. SAL-06.1.2 did a rapid
  // ITT analysis for go/no-go; SOL-01 goes much deeper — decomposing, categorising,
  // interpreting, and aligning requirements to our solution capability.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'Strategic baseline — win strategy, buyer values, competitive position inform interpretation' },
    { from: 'SAL-06.1.2', artifact: 'ITT documentation analysis summary', note: 'Rapid analysis from go/no-go — starting point, not a substitute for deep analysis' },
    { from: 'SAL-01.2.1', artifact: 'Buyer values register', note: 'Understanding WHY the client is asking helps interpret WHAT they mean' },
    { from: 'SAL-01.2.2', artifact: 'Client problem statement', note: 'The underlying problem drives unstated requirements' },
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'How requirements will be scored shapes interpretation priorities' },
    { external: true, artifact: 'ITT documentation pack — specification, schedules, annexes, contract, evaluation methodology' },
    { external: true, artifact: 'Industry standards, regulatory requirements, and good practice frameworks relevant to the requirement' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-01.1',
      name: 'ITT Decomposition & Requirements Extraction',
      description: 'Break down the ITT documentation into a structured set of requirements — functional, technical, performance, contractual, compliance, and format — before interpretation begins',

      tasks: [
        {
          id: 'SOL-01.1.1',
          name: 'Decompose ITT documentation into structured requirements — extract every requirement from specification, schedules, annexes, and contract',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Bid Manager / Workstream Leads', i: 'Commercial Lead' },
          inputs: [
            { external: true, artifact: 'ITT documentation pack — specification, schedules, annexes, contract, evaluation methodology' }
          ],
          outputs: [
            {
              name: 'Structured requirements register',
              format: 'Structured register',
              quality: [
                'Every requirement extracted — not just the obvious specification items but also contract obligations, performance standards, and compliance conditions',
                'Requirements sourced and referenced — ITT section, clause, and page for each',
                'Requirements from different documents cross-referenced — specification requirement linked to corresponding contract clause and evaluation criterion',
                'Hidden requirements identified — obligations embedded in contract schedules, annexes, or evaluation criteria that are not obvious from the specification alone'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-01.1.2',
          name: 'Categorise requirements by type and priority — mandatory vs desirable, scored vs pass/fail, explicit vs implied',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Bid Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-01.1.1', artifact: 'Structured requirements register' },
            { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' }
          ],
          outputs: [
            {
              name: 'Categorised requirements register',
              format: 'Structured register (enriched)',
              quality: [
                'Each requirement categorised by type: functional, technical, performance, contractual, compliance, format/submission',
                'Priority categorised: mandatory (must comply), desirable (scored if exceeded), pass/fail (threshold)',
                'Explicit vs implied distinction noted — explicit requirements stated in the ITT, implied requirements inferred from context, industry standards, or regulatory obligations',
                'Scoring linkage noted — which evaluation criterion and marks value each requirement contributes to'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-01.1.3',
          name: 'Identify ambiguities, contradictions, gaps, and unstated requirements — what is missing, unclear, or inconsistent in the documentation?',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Workstream Leads (SOL/COM/LEG/DEL)', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-01.1.2', artifact: 'Categorised requirements register' },
            { external: true, artifact: 'Industry standards, regulatory requirements, and good practice frameworks relevant to the requirement' }
          ],
          outputs: [
            {
              name: 'Requirements issues log',
              format: 'Structured log',
              quality: [
                'Ambiguities identified — requirements that can be interpreted in more than one way',
                'Contradictions identified — requirements in different documents that conflict',
                'Gaps identified — areas where requirements are expected but absent',
                'Unstated requirements identified — things the client clearly needs but hasn\'t explicitly asked for (informed by buyer values and client problem statement)',
                'Each issue assessed for impact — does this block solution design, affect scoring, or create delivery risk?',
                'Issues flagged for clarification fed forward to SAL-07'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'          // Different workstream leads can identify issues in their domain simultaneously
        }
      ]
    },
    {
      id: 'SOL-01.2',
      name: 'Requirements Interpretation & Solution Alignment',
      description: 'Interpret what the client really means — informed by buyer values and strategic context — and assess our solution alignment per requirement area',

      tasks: [
        {
          id: 'SOL-01.2.1',
          name: 'Interpret requirements against buyer values and client strategic context — what does the client really mean, and what is driving each requirement?',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Capture Lead / Account Manager', i: 'Workstream Leads' },
          inputs: [
            { from: 'SOL-01.1.2', artifact: 'Categorised requirements register' },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
            { from: 'SAL-01.2.2', artifact: 'Client problem statement' },
            { from: 'SAL-06', artifact: 'Capture plan (locked)' }
          ],
          outputs: [
            {
              name: 'Requirements interpretation notes',
              format: 'Per-requirement structured annotation',
              quality: [
                'Key requirements annotated with interpretation — what the client wrote vs what they likely mean',
                'Buyer value linkage documented — which buyer values drive which requirements',
                'Strategic intent behind requirements identified where possible — why is the client asking for this?',
                'Interpretation distinguishes between confident reading and assumptions to be tested'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-01.2.2',
          name: 'Assess our solution alignment per requirement area — where are we strong, where do we need to develop, where do we have gaps?',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Workstream Leads (SOL/COM/LEG/DEL)', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-01.2.1', artifact: 'Requirements interpretation notes' },
            { from: 'SOL-01.1.3', artifact: 'Requirements issues log' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' }
          ],
          outputs: [
            {
              name: 'Solution alignment assessment',
              format: 'Structured assessment per requirement area',
              quality: [
                'Each requirement area assessed: strong alignment (can respond confidently), partial (need to develop), gap (no current capability or approach)',
                'Gaps linked to score gap analysis from SAL-05 — consistency between scoring gaps and solution gaps',
                'Areas requiring partner or supply chain capability identified (feeds SUP-01)',
                'Priority areas for solution design effort identified — where to focus SOL-03 onwards'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'          // Different workstream leads assess alignment in their domain
        },
        {
          id: 'SOL-01.2.3',
          name: 'Synthesise requirements interpretation document — the consolidated output consumed by solution design and clarification strategy',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: null, i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-01.1.1', artifact: 'Structured requirements register' },
            { from: 'SOL-01.1.2', artifact: 'Categorised requirements register' },
            { from: 'SOL-01.1.3', artifact: 'Requirements issues log' },
            { from: 'SOL-01.2.1', artifact: 'Requirements interpretation notes' },
            { from: 'SOL-01.2.2', artifact: 'Solution alignment assessment' }
          ],
          outputs: [
            {
              name: 'Requirements interpretation document (activity primary output)',
              format: 'Document / structured register with interpretation',
              quality: [
                'All requirements extracted, categorised, and interpreted in a single authoritative document',
                'Solution alignment per requirement area documented — strengths, development needs, gaps',
                'Issues log consolidated — ambiguities, contradictions, gaps with impact and clarification referral',
                'Priority areas for solution design effort clearly identified',
                'Reviewed by Bid Director — not single-author interpretation',
                'Usable by SOL-03 (target operating model), SAL-07 (clarification strategy), and all solution workstream activities without further analysis'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Requirements interpretation document',
      format: 'Document / structured register with interpretation',
      quality: [
        'Every requirement extracted from ITT documentation — specification, contract, schedules, annexes',
        'Requirements categorised by type, priority, and scoring linkage',
        'Ambiguities, contradictions, gaps, and unstated requirements identified with impact assessment',
        'Requirements interpreted against buyer values and client strategic context',
        'Solution alignment assessed per requirement area — strengths, gaps, development needs',
        'Validated by Bid Director — not single-author interpretation'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-03', consumes: 'Requirements interpretation document', usage: 'Target operating model designed against interpreted requirements and solution alignment' },
    { activity: 'SAL-07', consumes: 'Requirements issues log', usage: 'Ambiguities and gaps become clarification questions' },
    { activity: 'SOL-04', consumes: 'Requirements interpretation document', usage: 'Service delivery model addresses functional and performance requirements' },
    { activity: 'SOL-05', consumes: 'Requirements interpretation document', usage: 'Technology approach addresses technical requirements' },
    { activity: 'SOL-06', consumes: 'Requirements interpretation document', usage: 'Staffing model informed by workforce requirements' },
    { activity: 'SUP-01', consumes: 'Solution alignment assessment', usage: 'Supply chain strategy addresses gaps requiring partner capability' },
    { activity: 'LEG-01', consumes: 'Requirements interpretation document', usage: 'Contract review informed by contractual requirements extracted' }
  ]
}
```

---

---

## SOL-02 — Current Operating Model Assessment

```javascript
{
  id: 'SOL-02',
  name: 'Current operating model assessment',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Solution Architect',
  output: 'As-is operating model assessment',
  dependencies: [],                        // Day-1 start — can run in parallel with SAL activities
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires delivery and operational expertise
  // Note: 9 times out of 10 in government this is a re-compete for an existing service,
  // not a greenfield site. This activity is the default for all bids.
  // Greenfield bids skip or significantly reduce this activity — toggle at bid setup via
  // incumbency/rebid flag. When greenfield: focus on understanding what infrastructure,
  // contracts, or context exists, not a full operating model assessment.
  //
  // Distinct from SAL-02 (competitive intelligence — how sticky is the incumbent?).
  // SOL-02 answers: "What am I inheriting on day one, and what do I need to transition
  // into the future service?"
  //
  // Previously named "Current service model review (rebid)" — renamed to reflect the
  // full scope: organisation, people, performance, systems, and operating model.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-02', artifact: 'Incumbent performance assessment', note: 'Competitive view of incumbent — SAL-02 looks at stickiness, SOL-02 looks at operational detail' },
    { from: 'SAL-01', artifact: 'Customer intelligence briefing', note: 'Client strategic context informs what aspects of the operating model matter most' },
    { external: true, artifact: 'ITT documentation — service specification, schedules, performance framework' },
    { external: true, artifact: 'Current contract documentation (if available) — scope, service levels, performance reports' },
    { external: true, artifact: 'TUPE and workforce data (if disclosed by client or incumbent)' },
    { external: true, artifact: 'Published organisational and operational data — annual reports, committee papers, audit reports' },
    { external: true, artifact: 'Internal delivery knowledge (if we are the incumbent)' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-02.1',
      name: 'Current Operating Model Discovery',
      description: 'Map the as-is state across all operating dimensions — organisation, people, systems, tools, and data — to understand what exists today and what we are taking on from day one',

      tasks: [
        {
          id: 'SOL-02.1.1',
          name: 'Map current organisational structure — departments, sub-departments, reporting lines, governance framework, interfaces with client organisation',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Account Manager', i: 'HR Lead' },
          inputs: [
            { external: true, artifact: 'Published organisational and operational data — annual reports, committee papers, audit reports' },
            { external: true, artifact: 'ITT documentation — service specification, schedules, performance framework' },
            { external: true, artifact: 'Internal delivery knowledge (if we are the incumbent)' }
          ],
          outputs: [
            {
              name: 'Current organisational structure map',
              format: 'Structured assessment with org chart',
              quality: [
                'Organisational structure documented — departments, sub-departments, teams, reporting lines',
                'Governance framework mapped — decision-making, escalation, client interface points',
                'Key management roles and responsibilities identified',
                'Interfaces between supplier organisation and client organisation documented',
                'Gaps in knowledge flagged — what we can\'t determine from available information'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-02.1.2',
          name: 'Assess current workforce — headcount, roles, grades, management structure, TUPE-relevant employment terms and conditions',
          raci: { r: 'HR Lead / Solution Architect', a: 'Bid Director', c: 'Commercial Lead / Legal', i: 'Delivery Director' },
          inputs: [
            { external: true, artifact: 'TUPE and workforce data (if disclosed by client or incumbent)' },
            { from: 'SOL-02.1.1', artifact: 'Current organisational structure map' },
            { external: true, artifact: 'Internal delivery knowledge (if we are the incumbent)' }
          ],
          outputs: [
            {
              name: 'Current workforce assessment',
              format: 'Structured register with analysis',
              quality: [
                'Workforce headcount and profile documented — roles, grades, locations, employment type (permanent, contractor, agency)',
                'Management structure and people governance documented — how the workforce is managed today',
                'TUPE-relevant terms assessed where data available — pension, benefits, collective agreements',
                'Skills and capability profile assessed at team/function level — what capability exists in the workforce?',
                'Data gaps explicitly flagged — what TUPE and workforce data is missing and when it might be disclosed'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'SOL-02.1.3',
          name: 'Review current systems, tools, and data landscape — technology stack, legacy systems, data flows, integration points, licensing',
          raci: { r: 'Technical Lead / Solution Architect', a: 'Bid Director', c: 'Technology SME', i: 'Commercial Lead' },
          inputs: [
            { external: true, artifact: 'ITT documentation — service specification, schedules, performance framework' },
            { external: true, artifact: 'Published organisational and operational data — annual reports, committee papers, audit reports' },
            { external: true, artifact: 'Internal delivery knowledge (if we are the incumbent)' }
          ],
          outputs: [
            {
              name: 'Current technology and data landscape assessment',
              format: 'Structured assessment',
              quality: [
                'Systems and tools supporting service delivery identified — including legacy, bespoke, and COTS platforms',
                'Data landscape documented — key data sets, data flows, integration points between systems',
                'Ownership and licensing documented — which systems transfer, which are client-owned, which are incumbent IP?',
                'Technology risks identified — end-of-life systems, unsupported platforms, security vulnerabilities',
                'Data migration and system transition implications identified at a strategic level'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'SOL-02.2',
      name: 'Current Performance & Service Baseline',
      description: 'Understand how the service is performing today, document the operating model as a whole, and identify what we are inheriting on day one — the transition baseline',

      tasks: [
        {
          id: 'SOL-02.2.1',
          name: 'Assess current service performance against existing KPIs and SLA framework — what is the performance baseline we are inheriting or competing against?',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director', i: 'Commercial Lead' },
          inputs: [
            { external: true, artifact: 'Current contract documentation (if available) — scope, service levels, performance reports' },
            { from: 'SAL-02.1.1', artifact: 'Incumbent performance summary', note: 'Competitive view of performance from SAL-02 — SOL-02 goes deeper into operational detail' }
          ],
          outputs: [
            {
              name: 'Current performance baseline',
              format: 'Structured performance assessment',
              quality: [
                'Existing KPIs and SLA framework documented — what is being measured and how?',
                'Performance against each KPI/SLA assessed where data available — meeting, exceeding, or failing',
                'Performance trends identified — improving, stable, or declining areas',
                'Performance gaps and pain points linked to operating model root causes where identifiable',
                'Baseline established for comparison with our proposed service improvement'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-02.2.2',
          name: 'Document the current operating model — how organisation, people, systems, and processes combine to deliver the service today',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Technical Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-02.1.1', artifact: 'Current organisational structure map' },
            { from: 'SOL-02.1.2', artifact: 'Current workforce assessment' },
            { from: 'SOL-02.1.3', artifact: 'Current technology and data landscape assessment' },
            { from: 'SOL-02.2.1', artifact: 'Current performance baseline' }
          ],
          outputs: [
            {
              name: 'Current operating model document',
              format: 'Structured operating model assessment',
              quality: [
                'Operating model documented as an integrated view — not just individual components in isolation',
                'How organisation, people, systems, processes, and governance work together described',
                'Key dependencies and interdependencies between components identified',
                'Strengths of the current model identified — what works well and should be retained or built upon',
                'Weaknesses and structural issues identified — what drives the performance gaps?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-02.2.3',
          name: 'Identify what we are inheriting on day one and key transition implications — the handover baseline that feeds transition planning',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Commercial Lead / Legal', i: 'HR Lead' },
          inputs: [
            { from: 'SOL-02.2.2', artifact: 'Current operating model document' },
            { from: 'SOL-02.1.2', artifact: 'Current workforce assessment' },
            { from: 'SOL-02.1.3', artifact: 'Current technology and data landscape assessment' }
          ],
          outputs: [
            {
              name: 'Day-one inheritance and transition implications (activity primary output complement)',
              format: 'Structured assessment',
              quality: [
                'Day-one inheritance clearly defined — what transfers to us: people, systems, assets, data, contracts, obligations',
                'What remains with the client or outgoing supplier identified — boundaries of transfer',
                'Key transition risks identified at a strategic level — feeds SOL-07 (transition planning)',
                'Service continuity requirements identified — what must not be disrupted during handover',
                'Implications for our target operating model design articulated — what constraints does the as-is place on our future model?'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'As-is operating model assessment',
      format: 'Document / structured assessment',
      quality: [
        'Current organisational structure mapped — departments, reporting lines, governance, client interfaces',
        'Current workforce assessed — headcount, roles, management, TUPE-relevant terms',
        'Current systems, tools, and data landscape documented — technology stack, legacy, integration, licensing',
        'Current service performance baselined against existing KPIs and SLAs',
        'Integrated operating model documented — how components work together to deliver the service',
        'Day-one inheritance defined — what transfers, what stays, transition implications',
        'Gaps in available information explicitly flagged'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-03', consumes: 'As-is operating model assessment', usage: 'Target operating model designed as transformation from the as-is baseline' },
    { activity: 'SOL-04', consumes: 'As-is operating model assessment', usage: 'Service delivery model understands what exists to build upon or replace' },
    { activity: 'SOL-05', consumes: 'Current technology and data landscape assessment', usage: 'Technology approach addresses legacy migration, system replacement, and integration' },
    { activity: 'SOL-06', consumes: 'Current workforce assessment', usage: 'Staffing model and TUPE analysis built on workforce baseline' },
    { activity: 'SOL-07', consumes: 'Day-one inheritance and transition implications', usage: 'Transition plan built on what we are inheriting and continuity requirements' },
    { activity: 'COM-01', consumes: 'As-is operating model assessment', usage: 'Should-cost model informed by current operating costs and workforce profile' }
  ]
}
```

---

---

## SOL-03 — Target Operating Model Design

```javascript
{
  id: 'SOL-03',
  name: 'Target operating model design',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Solution Architect',
  output: 'Target operating model',
  dependencies: ['SOL-01', 'SOL-02'],
  effortDays: 45,
  teamSize: 3,
  parallelisationType: 'P',               // Parallelisable — service lines can be designed concurrently
  // Note: this is the longest activity in the product (45 days) and the heart of the bid.
  // Almost every downstream SOL activity depends on it.
  //
  // SOL-03 is the ARCHITECTURE — the "what and why."
  // SOL-04 through SOL-09 are the DETAILED DESIGN — the "how exactly."
  // SOL-03 sets the strategic-level operating model framework; subsequent activities
  // fill in service delivery detail, technology, staffing, transition, innovation, social value.
  //
  // For a services re-compete, the TOM is the transformation story:
  // As-is (SOL-02) → Future state (SOL-03) → How we get there (SOL-07)

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-01', artifact: 'Requirements interpretation document' },
    { from: 'SOL-02', artifact: 'As-is operating model assessment' },
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'Win strategy and competitive positioning shape solution design' },
    { from: 'SAL-06.2.4', artifact: 'Win strategy narrative', note: 'Solution must deliver the win themes and differentiators' },
    { from: 'SAL-04', artifact: 'Win theme document', note: 'Messaging and theme integration points for the solution' },
    { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register', note: 'Innovation and disruption opportunities to incorporate where evaluation-aligned' },
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'Solution design prioritised by where the marks are' },
    { from: 'SAL-01.2.1', artifact: 'Buyer values register', note: 'Solution must address what the client strategically cares about' },
    { external: true, artifact: 'ITT documentation — service specification, output requirements, performance framework' },
    { external: true, artifact: 'Industry good practice, reference architectures, and regulatory frameworks' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-03.1',
      name: 'Solution Vision & Design Principles',
      description: 'Make the foundational solution positioning decision — where on the spectrum between low-capex compliance and high-capex transformation does this solution sit? Then establish the design principles that flow from that choice.',

      tasks: [
        {
          id: 'SOL-03.1.1',
          name: 'Determine solution positioning — where on the spectrum between low-capex/compliant and high-capex/transformational does this solution land, and why?',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Commercial Lead / Capture Lead / Delivery Director', i: 'Partner' },
          inputs: [
            { from: 'SAL-06.2.4', artifact: 'Win strategy narrative' },
            { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' },
            { from: 'SAL-02', artifact: 'Incumbent performance assessment', note: 'Can we beat them on price or must we differentiate through transformation?' },
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
            { external: true, artifact: 'ITT documentation — service specification, output requirements, performance framework' }
          ],
          outputs: [
            {
              name: 'Solution positioning decision',
              format: 'Structured decision paper',
              quality: [
                'Position on the compliance-to-transformation spectrum explicitly stated with rationale',
                'Key factors driving the positioning documented — evaluation framework, buyer appetite, commercial strategy, competitive landscape, incumbent stickiness',
                'Investment appetite defined — what level of upfront capex is the organisation willing to commit?',
                'Lifetime value argument articulated — if high capex, what is the payback through lower operating cost or better outcomes?',
                'Trade-offs acknowledged — what do we gain and what do we sacrifice at this positioning?',
                'Alignment to win strategy confirmed — does this positioning deliver our win themes?'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-03.1.2',
          name: 'Establish solution design principles — the rules that guide all downstream design decisions, flowing from the positioning choice',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Technical Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-03.1.1', artifact: 'Solution positioning decision' },
            { from: 'SOL-01', artifact: 'Requirements interpretation document' },
            { from: 'SAL-04', artifact: 'Win theme document' }
          ],
          outputs: [
            {
              name: 'Solution design principles',
              format: 'Structured principles document',
              quality: [
                'Design principles are specific to this bid — not generic "best practice" statements',
                'Each principle flows from the positioning decision or a key requirement — traceable rationale',
                'Principles are actionable — a solution designer can use them to make trade-off decisions',
                'Principles address: service philosophy, technology strategy, people approach, governance model, commercial alignment',
                'Principles are testable — the final TOM can be assessed against them'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-03.1.3',
          name: 'Define solution scope and boundary — what is in, what is out, where our service interfaces with the client and third parties',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Commercial Lead / Delivery Director', i: 'Legal' },
          inputs: [
            { from: 'SOL-01', artifact: 'Requirements interpretation document' },
            { from: 'SOL-02', artifact: 'As-is operating model assessment' },
            { external: true, artifact: 'ITT documentation — service specification, output requirements, performance framework' }
          ],
          outputs: [
            {
              name: 'Solution scope and boundary definition',
              format: 'Structured scope document',
              quality: [
                'Service boundary clearly defined — what we deliver vs what the client retains vs what third parties provide',
                'Interface points identified — where our service meets client operations, other suppliers, regulatory bodies',
                'Scope assumptions documented — areas where the ITT is ambiguous and we have assumed in or out',
                'Exclusions explicitly stated with rationale — what we are deliberately not proposing and why',
                'Dependencies on client or third parties identified — what must others provide for our model to work?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SOL-03.2',
      name: 'Operating Model Architecture',
      description: 'Design the high-level operating model — service lines, governance, organisation concept — that subsequent activities (SOL-04 through SOL-09) will detail',

      tasks: [
        {
          id: 'SOL-03.2.1',
          name: 'Design the high-level operating model framework — service lines, how they relate, how they map to requirements and deliver against the specification',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Workstream Leads', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-03.1.1', artifact: 'Solution positioning decision' },
            { from: 'SOL-03.1.2', artifact: 'Solution design principles' },
            { from: 'SOL-03.1.3', artifact: 'Solution scope and boundary definition' },
            { from: 'SOL-01', artifact: 'Requirements interpretation document' },
            { from: 'SOL-02', artifact: 'As-is operating model assessment' }
          ],
          outputs: [
            {
              name: 'Operating model framework',
              format: 'Operating model canvas / architecture diagram with narrative',
              quality: [
                'Service lines defined — each with clear purpose, scope, and relationship to requirements',
                'How service lines integrate and interact documented — dependencies, shared services, escalation paths',
                'Transformation story articulated — how the future model improves on the as-is (from SOL-02)',
                'Framework is at architecture level — sufficient for downstream activities to detail, not so detailed it constrains them',
                'Requirements coverage demonstrated — every key requirement area has a home in the model'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-03.2.2',
          name: 'Design the governance and management model — how the service will be managed, client interface, decision-making, escalation, performance reporting',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Account Manager', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-03.2.1', artifact: 'Operating model framework' },
            { from: 'SOL-02.1.1', artifact: 'Current organisational structure map', note: 'Understand current governance to design appropriate future model' },
            { external: true, artifact: 'ITT documentation — governance and reporting requirements' }
          ],
          outputs: [
            {
              name: 'Governance and management model',
              format: 'Structured governance design',
              quality: [
                'Management tiers defined — strategic, operational, tactical — with purpose and cadence',
                'Client interface model designed — joint governance, reporting, escalation, relationship management',
                'Decision-making framework documented — who decides what, at which level, with what authority',
                'Performance reporting structure designed — what gets reported, to whom, at what frequency',
                'Continuous improvement and contract management mechanisms included'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'SOL-03.2.3',
          name: 'Design the organisational concept — future structure, key roles, capability requirements at a strategic level (detail in SOL-06)',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'HR Lead / Delivery Director', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-03.2.1', artifact: 'Operating model framework' },
            { from: 'SOL-02.1.2', artifact: 'Current workforce assessment', note: 'What workforce exists vs what the future model needs' },
            { from: 'SOL-02.1.1', artifact: 'Current organisational structure map' }
          ],
          outputs: [
            {
              name: 'Organisational concept',
              format: 'High-level org design with narrative',
              quality: [
                'Future organisational structure designed at strategic level — functions, teams, reporting lines',
                'Key leadership and specialist roles identified with capability requirements',
                'Relationship to current workforce indicated — what broadly transfers, what changes, what is new',
                'Organisational design principles stated — spans of control, empowerment, flexibility',
                'Sufficient for SOL-06 to detail staffing model and TUPE analysis — not so detailed it pre-empts that work'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'SOL-03.3',
      name: 'Solution Integration & Narrative',
      description: 'Ensure the TOM is coherent, addresses all requirements, delivers the win themes, and is validated as the baseline for all detailed design',

      tasks: [
        {
          id: 'SOL-03.3.1',
          name: 'Map solution to requirements — demonstrate how the TOM addresses every key requirement area from SOL-01',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Workstream Leads', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-03.2.1', artifact: 'Operating model framework' },
            { from: 'SOL-01', artifact: 'Requirements interpretation document' }
          ],
          outputs: [
            {
              name: 'Requirements-to-solution mapping',
              format: 'Traceability matrix',
              quality: [
                'Every key requirement area mapped to the solution component that addresses it',
                'Coverage gaps identified — requirements not yet addressed by the TOM',
                'Strength of response per requirement area assessed — strong, adequate, needs development',
                'Gaps assigned to downstream detailed design activities for resolution'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-03.3.2',
          name: 'Map solution to win themes — demonstrate how the TOM delivers our differentiators and competitive messaging',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Capture Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-03.2.1', artifact: 'Operating model framework' },
            { from: 'SAL-04', artifact: 'Win theme document' },
            { from: 'SAL-05.2.4', artifact: 'Win theme integration map' }
          ],
          outputs: [
            {
              name: 'Win theme-to-solution mapping',
              format: 'Structured mapping',
              quality: [
                'Every win theme mapped to the solution features and design choices that deliver it',
                'Win themes that are strongly supported by the TOM identified — these become headline solution messages',
                'Win themes that are weakly supported flagged — solution must be strengthened or theme reconsidered',
                'Solution features that don\'t connect to any win theme questioned — are they necessary or scope creep?'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'SOL-03.3.3',
          name: 'Validate TOM with bid team — confirm as the baseline for detailed design activities (SOL-04 onwards) and identify risks and dependencies',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SOL-03.2.1', artifact: 'Operating model framework' },
            { from: 'SOL-03.2.2', artifact: 'Governance and management model' },
            { from: 'SOL-03.2.3', artifact: 'Organisational concept' },
            { from: 'SOL-03.3.1', artifact: 'Requirements-to-solution mapping' },
            { from: 'SOL-03.3.2', artifact: 'Win theme-to-solution mapping' }
          ],
          outputs: [
            {
              name: 'Target operating model (validated — activity primary output)',
              format: 'Comprehensive TOM document',
              quality: [
                'Bid team has reviewed and challenged — not single-author design',
                'Solution positioning confirmed — team understands and supports the compliance/transformation balance',
                'Requirements coverage confirmed — all key areas addressed or assigned to downstream activities',
                'Win theme delivery confirmed — solution supports the competitive narrative',
                'Risks and open issues documented — what could go wrong and what needs resolving in detailed design',
                'Downstream activities briefed — SOL-04 through SOL-09 understand their design envelope',
                'TOM baselined as the reference point — changes require formal review'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Target operating model',
      format: 'Comprehensive TOM document',
      quality: [
        'Solution positioning decision made and documented — compliance/transformation spectrum with rationale',
        'Design principles established — specific, actionable, traceable to positioning and requirements',
        'Scope and boundary defined — what is in, what is out, interfaces with client and third parties',
        'Operating model framework designed — service lines, integration, transformation story from as-is',
        'Governance and management model designed — tiers, client interface, decision-making, reporting',
        'Organisational concept designed — future structure, key roles, capability requirements',
        'Requirements coverage demonstrated — every key area mapped to solution component',
        'Win theme delivery demonstrated — solution supports competitive narrative',
        'Validated by bid team and baselined for detailed design'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-04', consumes: 'Target operating model', usage: 'Service delivery model details how each service line operates within the TOM framework' },
    { activity: 'SOL-05', consumes: 'Target operating model', usage: 'Technology approach designed to enable the operating model' },
    { activity: 'SOL-06', consumes: 'Organisational concept', usage: 'Staffing model and TUPE analysis details the workforce within the org design' },
    { activity: 'SOL-07', consumes: 'Target operating model', usage: 'Transition plan bridges from as-is (SOL-02) to future state (SOL-03)' },
    { activity: 'SOL-08', consumes: 'Target operating model', usage: 'Innovation roadmap builds on the TOM\'s transformation story' },
    { activity: 'SOL-09', consumes: 'Target operating model', usage: 'Social value proposition embedded within the operating model' },
    { activity: 'SOL-11', consumes: 'Target operating model', usage: 'Solution design lock consolidates TOM with all detailed design outputs' },
    { activity: 'COM-01', consumes: 'Target operating model', usage: 'Should-cost model built from the operating model framework and organisational concept' },
    { activity: 'DEL-01', consumes: 'Target operating model', usage: 'Implementation plan designed around the TOM structure' }
  ]
}
```

---

---

## SOL-04 — Service Delivery Model Design

```javascript
{
  id: 'SOL-04',
  name: 'Service delivery model design',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Solution Architect',
  output: 'Service delivery model',
  dependencies: ['SOL-03'],
  effortDays: 30,
  teamSize: 3,
  parallelisationType: 'P',               // Parallelisable — different service lines designed concurrently
  // Note: SOL-03 defined the architecture (what service lines exist and why).
  // SOL-04 details how each one actually operates — processes, workflows, resources,
  // service levels, interfaces. This is the "how exactly" layer.
  // The output must be sufficiently detailed for COM-01 to build a should-cost model.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-03', artifact: 'Target operating model' },
    { from: 'SOL-03.2.1', artifact: 'Operating model framework', note: 'Service line definitions and integration points' },
    { from: 'SOL-03.2.2', artifact: 'Governance and management model', note: 'Management structure the delivery model operates within' },
    { from: 'SOL-01', artifact: 'Requirements interpretation document', note: 'Functional and performance requirements each service line must address' },
    { from: 'SOL-02', artifact: 'As-is operating model assessment', note: 'Current service processes to build upon or replace' },
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'Where the marks are — prioritise design effort accordingly' },
    { external: true, artifact: 'ITT documentation — service specification, output requirements, performance framework, SLAs' },
    { external: true, artifact: 'Industry good practice, reference delivery models, and regulatory requirements' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-04.1',
      name: 'Service Line Design',
      description: 'Detail how each service line operates — processes, workflows, resource model, capacity, and interfaces between service lines',

      tasks: [
        {
          id: 'SOL-04.1.1',
          name: 'Design service delivery processes per service line — workflows, activities, handoffs, triggers, volumes, and operating procedures',
          raci: { r: 'Solution Architect / Service Line Leads', a: 'Bid Director', c: 'Delivery Director / SMEs', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-03.2.1', artifact: 'Operating model framework' },
            { from: 'SOL-01', artifact: 'Requirements interpretation document' },
            { from: 'SOL-02', artifact: 'As-is operating model assessment' },
            { external: true, artifact: 'ITT documentation — service specification, output requirements' }
          ],
          outputs: [
            {
              name: 'Service delivery process designs',
              format: 'Per-service-line process documentation',
              quality: [
                'Each service line has documented delivery processes — not just what is delivered but how',
                'Workflows define activities, roles, handoffs, triggers, and decision points',
                'Volume assumptions documented — what throughput the process is designed to handle',
                'Process improvements over the as-is model identified — what changes and what the improvement delivers',
                'Processes are specific enough to cost — resource types, effort, and frequency identifiable'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'          // Different service lines designed concurrently by different team members
        },
        {
          id: 'SOL-04.1.2',
          name: 'Design resource and capacity model per service line — what resources deliver this service, at what capacity, with what scalability?',
          raci: { r: 'Solution Architect / Service Line Leads', a: 'Bid Director', c: 'Delivery Director / HR Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-04.1.1', artifact: 'Service delivery process designs' },
            { from: 'SOL-03.2.3', artifact: 'Organisational concept' },
            { external: true, artifact: 'ITT documentation — volume projections, demand variability, growth expectations' }
          ],
          outputs: [
            {
              name: 'Resource and capacity model',
              format: 'Per-service-line resource model',
              quality: [
                'Resource types and quantities defined per service line — roles, FTEs, skills, location',
                'Capacity designed against expected volumes — with headroom assumptions stated',
                'Scalability mechanisms defined — how does capacity flex with demand (up and down)?',
                'Peak and trough scenarios considered — not just average steady-state',
                'Resource model is directly costable — feeds COM-01 should-cost model'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'
        },
        {
          id: 'SOL-04.1.3',
          name: 'Design interfaces and dependencies between service lines — how work flows across boundaries, shared services, escalation paths',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Service Line Leads', i: 'Delivery Director' },
          inputs: [
            { from: 'SOL-04.1.1', artifact: 'Service delivery process designs' },
            { from: 'SOL-03.2.1', artifact: 'Operating model framework' }
          ],
          outputs: [
            {
              name: 'Service line interface and dependency map',
              format: 'Interface matrix with process documentation',
              quality: [
                'All interfaces between service lines identified and documented — triggers, handoffs, data flows',
                'Shared services and common capabilities identified — what is centralised vs distributed',
                'Escalation paths across service line boundaries defined',
                'Dependencies that create bottleneck or single-point-of-failure risk identified',
                'End-to-end service journeys traced across service lines — does the integrated model work for the end user?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'        // Requires all service line designs to integrate
        }
      ]
    },
    {
      id: 'SOL-04.2',
      name: 'Performance & Assurance Framework',
      description: 'Connect the delivery model to the performance framework — which components deliver which outcomes, how we assure quality, and how we continuously improve',

      tasks: [
        {
          id: 'SOL-04.2.1',
          name: 'Map SLA/KPI commitments to delivery components — which parts of the delivery model are responsible for which performance outcomes?',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-04.1.1', artifact: 'Service delivery process designs' },
            { from: 'SOL-04.1.3', artifact: 'Service line interface and dependency map' },
            { external: true, artifact: 'ITT documentation — performance framework, SLAs, KPIs, service credits' }
          ],
          outputs: [
            {
              name: 'SLA/KPI-to-delivery commitment matrix',
              format: 'Structured matrix',
              quality: [
                'Every SLA and KPI mapped to the service line and process component responsible for delivering it',
                'Where multiple service lines contribute to a single KPI, the contribution model is defined',
                'Commitments are achievable within the resource and capacity model — not aspirational',
                'Service credit and penalty exposure assessed per commitment — what is the financial risk?',
                'Monitoring mechanism identified per KPI — how will we know if we are meeting the commitment?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-04.2.2',
          name: 'Design quality assurance and continuous improvement mechanisms — how we monitor, measure, and improve service delivery over the contract term',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Quality Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-04.2.1', artifact: 'SLA/KPI-to-delivery commitment matrix' },
            { from: 'SOL-03.2.2', artifact: 'Governance and management model' }
          ],
          outputs: [
            {
              name: 'Quality assurance and continuous improvement framework',
              format: 'Structured framework document',
              quality: [
                'Quality assurance mechanisms defined — inspection, audit, review, self-assessment cadence',
                'Performance monitoring and reporting mechanisms designed — dashboards, alerts, thresholds',
                'Continuous improvement process defined — how improvements are identified, assessed, approved, and implemented',
                'Lessons learned and knowledge management mechanisms included',
                'Framework is proportionate to contract value and complexity — not over-engineered'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-04.2.3',
          name: 'Validate service delivery model — confirm it delivers against requirements, is costable for COM-01, and is deliverable within the organisational concept',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SOL-04.1.1', artifact: 'Service delivery process designs' },
            { from: 'SOL-04.1.2', artifact: 'Resource and capacity model' },
            { from: 'SOL-04.1.3', artifact: 'Service line interface and dependency map' },
            { from: 'SOL-04.2.1', artifact: 'SLA/KPI-to-delivery commitment matrix' },
            { from: 'SOL-04.2.2', artifact: 'Quality assurance and continuous improvement framework' }
          ],
          outputs: [
            {
              name: 'Service delivery model (validated — activity primary output)',
              format: 'Comprehensive delivery model document',
              quality: [
                'Bid team has reviewed and challenged — not single-author design',
                'Requirements coverage confirmed — every functional and performance requirement addressed',
                'Commercial readiness confirmed — resource model, capacity model, and process designs are sufficiently detailed for costing',
                'Deliverability confirmed — the delivery team believes this model can be mobilised and operated',
                'Risks and assumptions documented — what could go wrong and what has been assumed',
                'Baselined for downstream consumption — SOL-06 (staffing), SOL-07 (transition), COM-01 (costing)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Service delivery model',
      format: 'Comprehensive delivery model document',
      quality: [
        'Service delivery processes designed per service line — workflows, activities, volumes, operating procedures',
        'Resource and capacity model defined per service line — roles, FTEs, scalability mechanisms',
        'Service line interfaces and dependencies mapped — handoffs, shared services, escalation',
        'SLA/KPI commitments mapped to delivery components with monitoring mechanisms',
        'Quality assurance and continuous improvement framework designed',
        'Model validated as deliverable, costable, and requirements-compliant'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-06', consumes: 'Resource and capacity model', usage: 'Staffing model details workforce within the resource model' },
    { activity: 'SOL-07', consumes: 'Service delivery model', usage: 'Transition plan designs how to mobilise and stand up each service line' },
    { activity: 'SOL-09', consumes: 'Service delivery model', usage: 'Social value embedded within service delivery processes' },
    { activity: 'SOL-10', consumes: 'Service delivery model', usage: 'Evidence strategy identifies case studies for each service line capability' },
    { activity: 'SOL-11', consumes: 'Service delivery model', usage: 'Solution design lock consolidates delivery model with all other solution outputs' },
    { activity: 'COM-01', consumes: 'Service delivery model', usage: 'Should-cost model built from resource model, capacity model, and process designs' },
    { activity: 'DEL-03', consumes: 'SLA/KPI-to-delivery commitment matrix', usage: 'KPI/SLA framework details the performance commitments' }
  ]
}
```

---

---

## SOL-05 — Technology & Digital Approach

```javascript
{
  id: 'SOL-05',
  name: 'Technology & digital approach',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Technical Lead',
  output: 'Technology solution design',
  dependencies: ['SOL-03', 'SUP-02'],
  effortDays: 20,
  teamSize: 2,
  parallelisationType: 'P',               // Parallelisable — architecture and data streams can run concurrently
  // Note: this is the technology enablement layer for the operating model.
  // SOL-03 defined what the service looks like, SOL-04 defined how it delivers,
  // SOL-05 defines what technology makes it work.
  // The dependency on SUP-02 (partner technology assessment) ensures partner platforms
  // and COTS products are evaluated before committing to the architecture.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-03', artifact: 'Target operating model' },
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'Processes and workflows that technology must enable' },
    { from: 'SOL-02.1.3', artifact: 'Current technology and data landscape assessment', note: 'What exists today — legacy, platforms, data, licensing' },
    { from: 'SOL-01', artifact: 'Requirements interpretation document', note: 'Technical requirements' },
    { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register', note: 'Technology disruption opportunities identified during capture' },
    { from: 'SUP-02', artifact: 'Partner technology assessment', note: 'Partner platforms, COTS products, third-party technology options' },
    { external: true, artifact: 'ITT documentation — technical requirements, security standards, data handling requirements' },
    { external: true, artifact: 'Government security and information assurance frameworks (e.g., Cyber Essentials, ISO 27001, OFFICIAL/SECRET classifications)' },
    { external: true, artifact: 'Our technology portfolio — platforms, IP, development capability, hosting infrastructure' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-05.1',
      name: 'Technology Architecture & Platform Design',
      description: 'Design the target technology architecture — platforms, infrastructure, applications, security — and the build/buy/reuse decisions that underpin it',

      tasks: [
        {
          id: 'SOL-05.1.1',
          name: 'Design target technology architecture — platforms, infrastructure, applications, and how they support the service delivery model',
          raci: { r: 'Technical Lead', a: 'Solution Architect', c: 'Delivery Director / Technology SMEs', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SOL-04', artifact: 'Service delivery model' },
            { from: 'SOL-01', artifact: 'Requirements interpretation document' },
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' },
            { external: true, artifact: 'ITT documentation — technical requirements' }
          ],
          outputs: [
            {
              name: 'Target technology architecture',
              format: 'Architecture document with diagrams',
              quality: [
                'Technology architecture covers all layers — infrastructure, platform, application, user interface',
                'Each technology component mapped to the service delivery process it enables',
                'Transformational technology opportunities from SAL-02 L2.3 incorporated where evaluation-aligned',
                'Architecture principles stated — cloud strategy, scalability approach, resilience, maintainability',
                'Technology roadmap across contract term outlined — what is delivered at mobilisation vs phased in'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-05.1.2',
          name: 'Assess build vs buy vs reuse decisions — what do we develop bespoke, what COTS/partner platforms do we adopt, what existing systems do we retain and enhance?',
          raci: { r: 'Technical Lead', a: 'Solution Architect', c: 'Commercial Lead / Partner Lead', i: 'Delivery Director' },
          inputs: [
            { from: 'SOL-05.1.1', artifact: 'Target technology architecture' },
            { from: 'SOL-02.1.3', artifact: 'Current technology and data landscape assessment' },
            { from: 'SUP-02', artifact: 'Partner technology assessment' },
            { external: true, artifact: 'Our technology portfolio — platforms, IP, development capability, hosting infrastructure' }
          ],
          outputs: [
            {
              name: 'Build/buy/reuse assessment',
              format: 'Structured decision register per component',
              quality: [
                'Every significant technology component assessed: build bespoke, buy COTS/SaaS, reuse existing, or partner-provided',
                'Decision rationale documented per component — cost, capability, risk, time-to-deploy, lock-in',
                'Partner and COTS dependencies identified with licensing and commercial implications',
                'Legacy systems to be retained have a lifecycle and risk assessment — supportability, end-of-life, migration path',
                'Decisions are commercially viable — feeds directly into COM-01 technology cost model'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-05.1.3',
          name: 'Design cyber security and information assurance approach — security architecture, data classification, accreditation requirements',
          raci: { r: 'Security Architect / Technical Lead', a: 'Solution Architect', c: 'Client Security (if available) / Legal', i: 'Bid Director' },
          inputs: [
            { from: 'SOL-05.1.1', artifact: 'Target technology architecture' },
            { external: true, artifact: 'ITT documentation — security standards, data handling requirements' },
            { external: true, artifact: 'Government security and information assurance frameworks (e.g., Cyber Essentials, ISO 27001, OFFICIAL/SECRET classifications)' }
          ],
          outputs: [
            {
              name: 'Security and information assurance design',
              format: 'Security architecture document',
              quality: [
                'Security architecture designed — access control, encryption, network security, endpoint protection',
                'Data classification and handling requirements addressed — what data at what classification, storage, transmission, retention',
                'Accreditation requirements identified — what certifications and assurance processes are needed and timeline',
                'Security compliance with ITT requirements and government frameworks demonstrated',
                'Security risks identified and mitigated — residual risk accepted or escalated'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'SOL-05.2',
      name: 'Data & Integration Design',
      description: 'Design how data flows through the solution and how systems integrate — migration from legacy, integration with client and third parties, and data management',

      tasks: [
        {
          id: 'SOL-05.2.1',
          name: 'Design data architecture and migration approach — data model, data flows, migration from legacy systems, data quality strategy',
          raci: { r: 'Technical Lead / Data Architect', a: 'Solution Architect', c: 'Technology SMEs', i: 'Delivery Director' },
          inputs: [
            { from: 'SOL-05.1.1', artifact: 'Target technology architecture' },
            { from: 'SOL-02.1.3', artifact: 'Current technology and data landscape assessment' },
            { from: 'SOL-05.1.2', artifact: 'Build/buy/reuse assessment' }
          ],
          outputs: [
            {
              name: 'Data architecture and migration design',
              format: 'Structured design document',
              quality: [
                'Target data model designed — key data entities, relationships, ownership, lifecycle',
                'Data flows mapped — how data moves between systems, services, and external parties',
                'Data migration approach defined — what migrates, from where, transformation rules, validation approach',
                'Data quality strategy defined — cleansing, validation, ongoing quality management',
                'Data migration risks identified — volume, complexity, quality, downtime implications'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-05.2.2',
          name: 'Design integration architecture — how systems connect, APIs, interfaces with client systems and third-party platforms',
          raci: { r: 'Technical Lead', a: 'Solution Architect', c: 'Technology SMEs / Partner Technical Leads', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-05.1.1', artifact: 'Target technology architecture' },
            { from: 'SOL-05.1.2', artifact: 'Build/buy/reuse assessment' },
            { from: 'SOL-04.1.3', artifact: 'Service line interface and dependency map' }
          ],
          outputs: [
            {
              name: 'Integration architecture',
              format: 'Integration design document',
              quality: [
                'All system-to-system interfaces identified and designed — internal, client, and third-party',
                'Integration patterns defined — APIs, messaging, batch, real-time, file transfer',
                'Client system integration requirements addressed — what we connect to, protocol, frequency, ownership',
                'Third-party and partner system integration designed — dependencies, SLAs, fallback',
                'Integration testing approach outlined — how we validate interfaces work end-to-end'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'SOL-05.2.3',
          name: 'Validate technology solution — confirm it enables the delivery model, is costable, is deliverable, and meets security requirements',
          raci: { r: 'Technical Lead', a: 'Solution Architect', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SOL-05.1.1', artifact: 'Target technology architecture' },
            { from: 'SOL-05.1.2', artifact: 'Build/buy/reuse assessment' },
            { from: 'SOL-05.1.3', artifact: 'Security and information assurance design' },
            { from: 'SOL-05.2.1', artifact: 'Data architecture and migration design' },
            { from: 'SOL-05.2.2', artifact: 'Integration architecture' }
          ],
          outputs: [
            {
              name: 'Technology solution design (validated — activity primary output)',
              format: 'Comprehensive technology design document',
              quality: [
                'Technology architecture, data architecture, and integration architecture consolidated',
                'Build/buy/reuse decisions confirmed with commercial implications quantified',
                'Security and IA approach confirmed as compliant with requirements and government frameworks',
                'Technology solution validated as enabling the service delivery model — no gaps',
                'Costable for COM-01 — licensing, development, hosting, support costs identifiable',
                'Deliverable within transition timeline — technology readiness mapped to mobilisation phases',
                'Risks and assumptions documented — technology risk feeds SOL-12'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Technology solution design',
      format: 'Comprehensive technology design document',
      quality: [
        'Target technology architecture designed — infrastructure, platform, application, user interface',
        'Build/buy/reuse decisions made per component with rationale and commercial implications',
        'Cyber security and information assurance approach designed and compliance demonstrated',
        'Data architecture and migration approach designed — model, flows, migration, quality',
        'Integration architecture designed — internal, client, and third-party interfaces',
        'Solution validated as enabling delivery model, costable, deliverable, and security-compliant'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-07', consumes: 'Technology solution design', usage: 'Transition plan includes technology migration and deployment' },
    { activity: 'SOL-11', consumes: 'Technology solution design', usage: 'Solution design lock consolidates technology design with all solution outputs' },
    { activity: 'COM-01', consumes: 'Technology solution design', usage: 'Should-cost model includes technology costs — licensing, development, hosting, support' },
    { activity: 'SOL-12', consumes: 'Technology solution design', usage: 'Solution risk register includes technology and migration risks' },
    { activity: 'DEL-01', consumes: 'Technology solution design', usage: 'Implementation plan includes technology deployment phases' }
  ]
}
```

---

---

## SOL-06 — Staffing Model & TUPE Analysis

```javascript
{
  id: 'SOL-06',
  name: 'Staffing model & TUPE analysis',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'HR Lead / Solution Architect',
  output: 'Staffing model with TUPE schedule',
  dependencies: ['SOL-04'],
  effortDays: 8,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires HR/TUPE expertise
  // Note: this is the people dimension of the solution. TUPE is the dominant complexity
  // in government re-competes — the transferring workforce brings terms, conditions,
  // pensions, and legal obligations that fundamentally shape the cost model.
  // People costs are typically 60-80% of a services contract cost base.
  //
  // Distinct from SOL-07 (transition planning) — SOL-06 is about the target workforce
  // and TUPE obligations; SOL-07 is about how we get from as-is to future state.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-03.2.3', artifact: 'Organisational concept', note: 'Strategic-level future structure and key roles' },
    { from: 'SOL-04.1.2', artifact: 'Resource and capacity model', note: 'What the service delivery model needs — roles, FTEs, skills' },
    { from: 'SOL-02.1.2', artifact: 'Current workforce assessment', note: 'What workforce exists today — headcount, roles, terms, TUPE data' },
    { from: 'SOL-02.1.1', artifact: 'Current organisational structure map', note: 'How the workforce is currently organised' },
    { external: true, artifact: 'TUPE and workforce data (as disclosed by client or incumbent)' },
    { external: true, artifact: 'ITT documentation — workforce requirements, TUPE provisions, pension requirements' },
    { external: true, artifact: 'TUPE legislation and case law guidance — Transfer of Undertakings (Protection of Employment) Regulations' },
    { external: true, artifact: 'Pension scheme documentation (if applicable) — LGPS, NHSPS, or other public sector pension obligations' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-06.1',
      name: 'Target Staffing Model Design',
      description: 'Design the future workforce — roles, grades, FTEs, structure — mapped to the service delivery model and organisational concept',

      tasks: [
        {
          id: 'SOL-06.1.1',
          name: 'Design target workforce structure — roles, grades, FTEs, reporting lines, mapped to service lines and organisational concept',
          raci: { r: 'HR Lead / Solution Architect', a: 'Bid Director', c: 'Delivery Director / Service Line Leads', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-03.2.3', artifact: 'Organisational concept' },
            { from: 'SOL-04.1.2', artifact: 'Resource and capacity model' },
            { external: true, artifact: 'ITT documentation — workforce requirements' }
          ],
          outputs: [
            {
              name: 'Target staffing model',
              format: 'Structured workforce model',
              quality: [
                'Every role defined — title, grade, function, service line, reporting line, location',
                'FTE count per role with rationale — linked to service delivery process and volume assumptions',
                'Management structure defined — spans of control, team sizes, supervisory ratios',
                'Shift patterns and working arrangements documented where applicable',
                'Model is directly costable — grade, rate, hours identifiable per role for COM-01'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-06.1.2',
          name: 'Define skills and capability requirements per role — what competencies, qualifications, clearances, and experience does the future workforce need?',
          raci: { r: 'HR Lead / Solution Architect', a: 'Bid Director', c: 'Service Line Leads / SMEs', i: 'Delivery Director' },
          inputs: [
            { from: 'SOL-06.1.1', artifact: 'Target staffing model' },
            { from: 'SOL-04', artifact: 'Service delivery model' },
            { external: true, artifact: 'ITT documentation — workforce requirements, security clearance requirements' }
          ],
          outputs: [
            {
              name: 'Skills and capability requirements matrix',
              format: 'Per-role competency framework',
              quality: [
                'Each role has defined competency requirements — skills, qualifications, experience, clearances',
                'Mandatory vs desirable competencies distinguished',
                'Security clearance requirements mapped per role — SC, DV, BPSS, CTC as applicable',
                'Specialist or scarce skills identified — roles that will be difficult to fill',
                'Training and development needs anticipated — what upskilling will the workforce need?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SOL-06.2',
      name: 'TUPE & Workforce Transition Analysis',
      description: 'Analyse the TUPE-transferring workforce, identify the gap between what transfers and what the target model needs, and validate the overall staffing model',

      tasks: [
        {
          id: 'SOL-06.2.1',
          name: 'Analyse TUPE-transferring workforce — headcount, terms and conditions, pensions, collective agreements, protected rights, and legal obligations',
          raci: { r: 'HR Lead', a: 'Bid Director', c: 'Legal / Commercial Lead', i: 'Solution Architect' },
          inputs: [
            { from: 'SOL-02.1.2', artifact: 'Current workforce assessment' },
            { external: true, artifact: 'TUPE and workforce data (as disclosed by client or incumbent)' },
            { external: true, artifact: 'TUPE legislation and case law guidance' },
            { external: true, artifact: 'Pension scheme documentation (if applicable)' }
          ],
          outputs: [
            {
              name: 'TUPE analysis and schedule',
              format: 'Structured TUPE register with analysis',
              quality: [
                'Transferring workforce profiled — headcount, roles, grades, locations, employment type',
                'Terms and conditions analysed — pay, benefits, hours, leave, notice periods, collective agreements',
                'Pension obligations assessed — scheme type (LGPS, NHSPS, private), employer contribution rates, Fair Deal/New Fair Deal implications',
                'Protected rights identified — what cannot be changed post-transfer and for how long',
                'TUPE cost impact quantified — what does the transferring workforce cost vs our target model assumptions?',
                'TUPE data gaps flagged — what information is still missing and the risk of the unknown'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-06.2.2',
          name: 'Conduct workforce gap analysis — delta between transferring workforce and target staffing model: recruit, redeploy, upskill, or restructure',
          raci: { r: 'HR Lead / Solution Architect', a: 'Bid Director', c: 'Delivery Director / Legal', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-06.1.1', artifact: 'Target staffing model' },
            { from: 'SOL-06.1.2', artifact: 'Skills and capability requirements matrix' },
            { from: 'SOL-06.2.1', artifact: 'TUPE analysis and schedule' }
          ],
          outputs: [
            {
              name: 'Workforce gap analysis',
              format: 'Structured gap register with resolution strategy',
              quality: [
                'Role-by-role comparison: transferring workforce mapped to target staffing model',
                'Gaps identified by type: new roles to recruit, surplus roles to redeploy/exit, skills gaps to upskill',
                'Resolution strategy per gap — recruitment, redeployment, training, restructuring, agency/contractor',
                'Timeline for resolution — what can be done pre-mobilisation vs during transition vs steady-state',
                'Cost implications quantified — recruitment, redundancy, training, interim resourcing costs for COM-01',
                'Legal risk assessed — restructuring and redundancy implications under TUPE'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-06.2.3',
          name: 'Validate staffing model — confirm it delivers the service, is TUPE-compliant, and is costable for COM-01',
          raci: { r: 'HR Lead / Solution Architect', a: 'Bid Director', c: 'Commercial Lead / Legal', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-06.1.1', artifact: 'Target staffing model' },
            { from: 'SOL-06.2.1', artifact: 'TUPE analysis and schedule' },
            { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis' }
          ],
          outputs: [
            {
              name: 'Staffing model with TUPE schedule (validated — activity primary output)',
              format: 'Comprehensive workforce model with TUPE register',
              quality: [
                'Target staffing model confirmed as sufficient to deliver the service delivery model',
                'TUPE compliance confirmed — legal obligations met, protected rights respected',
                'Workforce gap resolution strategy accepted — recruitment, redeployment, and training plans viable',
                'Total workforce cost quantified — transferring workforce + new hires + gap resolution costs',
                'Pension and benefits obligations quantified — employer cost fully modelled for COM-01',
                'Risks documented — TUPE data gaps, restructuring risk, scarce skills, clearance timelines'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Staffing model with TUPE schedule',
      format: 'Comprehensive workforce model with TUPE register',
      quality: [
        'Target workforce structure designed — roles, grades, FTEs, reporting lines per service line',
        'Skills and capability requirements defined per role including clearance requirements',
        'TUPE-transferring workforce analysed — terms, pensions, protected rights, cost impact',
        'Workforce gap analysis complete — gaps identified, resolution strategy per gap, timeline, cost',
        'Total workforce cost quantified and costable for COM-01',
        'TUPE-compliant and legally validated'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-07', consumes: 'Staffing model with TUPE schedule', usage: 'Transition plan includes workforce mobilisation, TUPE transfer, and gap resolution timeline' },
    { activity: 'SOL-11', consumes: 'Staffing model with TUPE schedule', usage: 'Solution design lock consolidates staffing model with all solution outputs' },
    { activity: 'COM-01', consumes: 'Staffing model with TUPE schedule', usage: 'Should-cost model — people costs typically 60-80% of cost base' },
    { activity: 'SOL-12', consumes: 'Staffing model with TUPE schedule', usage: 'Solution risk register includes TUPE, pension, and workforce risks' },
    { activity: 'LEG-02', consumes: 'TUPE analysis and schedule', usage: 'Legal review of TUPE obligations and employment law compliance' }
  ]
}
```

---

---

## SOL-07 — Transition & Mobilisation Approach

```javascript
{
  id: 'SOL-07',
  name: 'Transition & mobilisation approach',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Delivery Director',
  output: 'Transition plan',
  dependencies: ['SOL-04', 'SOL-05', 'SOL-06'],
  effortDays: 16,
  teamSize: 2,
  parallelisationType: 'P',               // Parallelisable — people, technology, and service transition planned concurrently
  // Note: this is the bridge activity — as-is (SOL-02) → future state (SOL-03) → how
  // we get there (SOL-07). The overriding constraint is service continuity — the client
  // cannot tolerate disruption during transition.
  //
  // Transition is a major scoring area in government bids. Evaluators want to see that
  // the bidder has thought through the risk and has a credible, phased plan. This is
  // often where challengers are most vulnerable vs incumbents.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-03', artifact: 'Target operating model', note: 'The future state we are transitioning to' },
    { from: 'SOL-02', artifact: 'As-is operating model assessment', note: 'The current state we are transitioning from' },
    { from: 'SOL-02.2.3', artifact: 'Day-one inheritance and transition implications', note: 'What we inherit and service continuity requirements' },
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'Detailed service delivery that must be stood up during transition' },
    { from: 'SOL-05', artifact: 'Technology solution design', note: 'Technology migration, data migration, system deployment' },
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'TUPE transfer, workforce gap resolution, day-one readiness' },
    { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis', note: 'Recruitment and upskilling timeline' },
    { external: true, artifact: 'ITT documentation — transition and mobilisation requirements, timeline, service continuity obligations' },
    { external: true, artifact: 'Contract documentation — mobilisation period, performance requirements during transition, service credits' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-07.1',
      name: 'Transition Planning',
      description: 'Design the transition approach across all dimensions — people, technology, service — with service continuity as the overriding constraint',

      tasks: [
        {
          id: 'SOL-07.1.1',
          name: 'Design the transition approach and phasing — pre-contract, day one, transition period, steady state — with service continuity as the overriding constraint',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SOL-02', artifact: 'As-is operating model assessment' },
            { from: 'SOL-02.2.3', artifact: 'Day-one inheritance and transition implications' },
            { external: true, artifact: 'ITT documentation — transition and mobilisation requirements, timeline, service continuity obligations' }
          ],
          outputs: [
            {
              name: 'Transition approach and phase plan',
              format: 'Structured phase plan',
              quality: [
                'Transition phases defined — pre-contract preparation, day one, transition period (typically 3-6 months), steady state',
                'Service continuity strategy articulated — how service is maintained at every phase of transition',
                'Cutover approach defined — big bang, phased, parallel running, or hybrid — with rationale',
                'Dependencies on client and outgoing supplier explicitly identified — what we need from them and when',
                'Critical path through transition identified — what must happen in sequence, what can be parallel'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-07.1.2',
          name: 'Plan people transition — TUPE transfer process, day-one workforce readiness, induction, gap recruitment timeline, training programme',
          raci: { r: 'HR Lead / Delivery Director', a: 'Bid Director', c: 'Legal / Solution Architect', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis' },
            { from: 'SOL-07.1.1', artifact: 'Transition approach and phase plan' }
          ],
          outputs: [
            {
              name: 'People transition plan',
              format: 'Structured plan with timeline',
              quality: [
                'TUPE transfer process designed — consultation timeline, communication plan, day-one logistics',
                'Day-one workforce readiness defined — who must be in place, with what induction, on what terms',
                'Recruitment timeline for gap roles — sequenced against transition phases and service need',
                'Training and upskilling programme designed — what skills, for whom, by when',
                'Employee engagement and retention approach during transition — managing uncertainty and attrition risk'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'
        },
        {
          id: 'SOL-07.1.3',
          name: 'Plan technology and data transition — system migration, data migration, new platform deployment, parallel running, legacy decommission',
          raci: { r: 'Technical Lead', a: 'Solution Architect', c: 'Delivery Director / Technology SMEs', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-05', artifact: 'Technology solution design' },
            { from: 'SOL-05.2.1', artifact: 'Data architecture and migration design' },
            { from: 'SOL-07.1.1', artifact: 'Transition approach and phase plan' }
          ],
          outputs: [
            {
              name: 'Technology transition plan',
              format: 'Structured plan with timeline',
              quality: [
                'System migration sequence defined — which systems when, dependencies, parallel running periods',
                'Data migration plan detailed — extraction, transformation, loading, validation, rollback approach',
                'New platform deployment phased against transition timeline — what is available at day one vs later',
                'Legacy system decommission planned — when systems are switched off, data archival, licence termination',
                'Technology transition risks identified — downtime, data loss, integration failure, parallel running cost'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'SOL-07.2',
      name: 'Mobilisation Programme & Risk',
      description: 'Design the mobilisation governance, identify and mitigate transition risks, and validate the plan as achievable, costable, and credible',

      tasks: [
        {
          id: 'SOL-07.2.1',
          name: 'Design the mobilisation programme — governance, milestones, dependencies, resource plan, client and outgoing-supplier interface',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / Bid Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-07.1.1', artifact: 'Transition approach and phase plan' },
            { from: 'SOL-07.1.2', artifact: 'People transition plan' },
            { from: 'SOL-07.1.3', artifact: 'Technology transition plan' }
          ],
          outputs: [
            {
              name: 'Mobilisation programme',
              format: 'Programme plan with governance structure',
              quality: [
                'Mobilisation governance designed — programme board, workstream leads, reporting cadence, decision rights',
                'Milestones defined with acceptance criteria — measurable, not just dates',
                'Dependencies mapped — between transition workstreams, on client, on outgoing supplier, on third parties',
                'Mobilisation resource plan defined — who is needed, when, distinct from steady-state team',
                'Client and outgoing-supplier interface designed — joint working arrangements, information sharing, escalation'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-07.2.2',
          name: 'Identify transition risks and develop mitigation strategies — what could go wrong during transition and how we prevent or manage it',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / HR Lead / Technical Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-07.2.1', artifact: 'Mobilisation programme' },
            { from: 'SOL-07.1.2', artifact: 'People transition plan' },
            { from: 'SOL-07.1.3', artifact: 'Technology transition plan' }
          ],
          outputs: [
            {
              name: 'Transition risk register',
              format: 'Structured risk register with mitigations',
              quality: [
                'Risks identified across all transition dimensions — people, technology, service, commercial, client dependency',
                'Each risk assessed for likelihood and impact — particularly impact on service continuity',
                'Mitigation strategies defined per risk — preventive and contingent actions',
                'Key dependency risks highlighted — risks we cannot fully mitigate because they depend on client or outgoing supplier action',
                'Residual risk accepted or escalated — no unaddressed high-impact risks'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-07.2.3',
          name: 'Validate transition plan — confirm it delivers service continuity, is achievable within timeline, and is costable',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SOL-07.1.1', artifact: 'Transition approach and phase plan' },
            { from: 'SOL-07.1.2', artifact: 'People transition plan' },
            { from: 'SOL-07.1.3', artifact: 'Technology transition plan' },
            { from: 'SOL-07.2.1', artifact: 'Mobilisation programme' },
            { from: 'SOL-07.2.2', artifact: 'Transition risk register' }
          ],
          outputs: [
            {
              name: 'Transition plan (validated — activity primary output)',
              format: 'Comprehensive transition and mobilisation document',
              quality: [
                'Bid team has reviewed and challenged — not single-author plan',
                'Service continuity confirmed — no unacceptable disruption at any phase',
                'Timeline achievable — critical path fits within contract mobilisation period',
                'Dependencies on client and outgoing supplier are reasonable and clearly communicated',
                'Transition costs quantified — mobilisation team, dual running, recruitment, training, technology migration',
                'Risks documented with mitigations — credible plan for managing what could go wrong',
                'Plan is compelling for evaluators — demonstrates we have thought this through in detail'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Transition plan',
      format: 'Comprehensive transition and mobilisation document',
      quality: [
        'Transition approach and phasing designed — pre-contract through to steady state',
        'Service continuity strategy articulated with cutover approach',
        'People transition planned — TUPE, induction, recruitment, training',
        'Technology transition planned — migration, deployment, parallel running, decommission',
        'Mobilisation programme designed — governance, milestones, dependencies, resource plan',
        'Transition risks identified and mitigated',
        'Plan validated as achievable, costable, and credible for evaluators'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-11', consumes: 'Transition plan', usage: 'Solution design lock consolidates transition plan with all solution outputs' },
    { activity: 'SOL-12', consumes: 'Transition risk register', usage: 'Solution risk register incorporates transition risks' },
    { activity: 'COM-01', consumes: 'Transition plan', usage: 'Should-cost model includes mobilisation and transition costs' },
    { activity: 'COM-06', consumes: 'Transition plan', usage: 'Commercial model includes transition pricing and investment profile' },
    { activity: 'DEL-01', consumes: 'Transition plan', usage: 'Implementation plan aligns with transition phasing and milestones' }
  ]
}
```

---

---

## SOL-08 — Innovation & Continuous Improvement

```javascript
{
  id: 'SOL-08',
  name: 'Innovation & continuous improvement',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Solution Architect',
  output: 'Innovation roadmap',
  dependencies: ['SOL-03'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires innovation strategy and commercial thinking
  // Note: innovation is increasingly a standalone scored section in UK government bids.
  // It is not just a nice-to-have — evaluators want a defined strategy, a roadmap with
  // investment commitment, and measurable outcomes.
  //
  // Critically, the innovation roadmap is inseparable from the commercial trajectory.
  // AI and automation will progressively replace human effort over the contract term,
  // changing the cost base year on year. The question is: who benefits from that
  // productivity gain, how is it shared, and how is it governed contractually?
  // This activity directly informs the commercial workstream (COM-01, COM-06).

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-03', artifact: 'Target operating model' },
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'Processes and workflows where innovation can drive productivity' },
    { from: 'SOL-05', artifact: 'Technology solution design', note: 'Technology platform that enables innovation' },
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'Workforce that innovation will progressively transform — TUPE implications of role displacement' },
    { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register', note: 'Innovation opportunities identified during capture — now built into a roadmap' },
    { from: 'SAL-02.3.4', artifact: 'Commercial disruption model', note: 'Commercial impact of innovation already modelled at strategic level' },
    { from: 'SAL-04', artifact: 'Win theme document', note: 'Innovation as a win theme — messaging and differentiation' },
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'How innovation will be evaluated and scored' },
    { from: 'SAL-01.2.1', artifact: 'Buyer values register', note: 'Does the client value innovation and investment?' },
    { external: true, artifact: 'ITT documentation — innovation requirements, continuous improvement obligations, benchmarking provisions' },
    { external: true, artifact: 'Technology landscape — AI, automation, emerging capabilities relevant to this service domain' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-08.1',
      name: 'Innovation Strategy & Roadmap',
      description: 'Define the innovation vision, build a phased roadmap across the contract term, and identify what we bring from day one that changes the game',

      tasks: [
        {
          id: 'SOL-08.1.1',
          name: 'Define innovation strategy — vision, principles, and how innovation aligns to buyer values, win themes, and the evaluation framework',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Capture Lead / Technical Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-04', artifact: 'Win theme document' },
            { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
            { external: true, artifact: 'ITT documentation — innovation requirements, continuous improvement obligations' }
          ],
          outputs: [
            {
              name: 'Innovation strategy',
              format: 'Structured strategy document',
              quality: [
                'Innovation vision articulated — what does this service look like in 5 years vs today?',
                'Innovation principles defined — aligned to client values, not innovation for its own sake',
                'Alignment to evaluation framework demonstrated — how innovation will score',
                'Innovation ambition calibrated to solution positioning (from SOL-03.1.1) — if compliance play, innovation is measured improvement; if transformation play, innovation is step change'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-08.1.2',
          name: 'Design innovation roadmap across the contract term — what innovations, when, what investment required, what outcomes delivered',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Technical Lead / Delivery Director', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-08.1.1', artifact: 'Innovation strategy' },
            { from: 'SAL-02.3.1', artifact: 'Transformational opportunity register' },
            { from: 'SOL-04', artifact: 'Service delivery model' },
            { from: 'SOL-05', artifact: 'Technology solution design' },
            { external: true, artifact: 'Technology landscape — AI, automation, emerging capabilities' }
          ],
          outputs: [
            {
              name: 'Innovation roadmap',
              format: 'Phased roadmap with investment and outcomes',
              quality: [
                'Innovations phased across contract term — year 1, year 2-3, year 4-5 — not everything at once',
                'Each innovation has: description, enabling technology, investment required, expected outcome, measurement criteria',
                'AI and automation opportunities specifically identified — which processes, which roles affected, what productivity gain',
                'Roadmap is realistic — builds on the technology platform (SOL-05) and delivery model (SOL-04)',
                'Dependencies identified — what must be in place before each innovation can be delivered'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-08.1.3',
          name: 'Identify day-one innovations — what we bring from the start that the incumbent does not have and that immediately improves the service',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Technical Lead / Delivery Director', i: 'Capture Lead' },
          inputs: [
            { from: 'SOL-08.1.2', artifact: 'Innovation roadmap' },
            { from: 'SOL-02', artifact: 'As-is operating model assessment', note: 'What the current service lacks' }
          ],
          outputs: [
            {
              name: 'Day-one innovation register',
              format: 'Structured register',
              quality: [
                'Each day-one innovation identifies what it replaces or improves vs the current service',
                'Innovations are deliverable from day one — not dependent on transition completion',
                'Impact is tangible and demonstrable — the client sees the difference immediately',
                'Credible — we have evidence, track record, or working prototypes to substantiate each claim'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SOL-08.2',
      name: 'Continuous Improvement Framework',
      description: 'Design the governance for ongoing improvement and establish the process by which innovations are identified, assessed, approved, funded, and measured throughout the contract',

      tasks: [
        {
          id: 'SOL-08.2.1',
          name: 'Design continuous improvement governance — how improvements are identified, assessed, approved, funded, and measured over the contract term',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Quality Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-08.1.1', artifact: 'Innovation strategy' },
            { from: 'SOL-03.2.2', artifact: 'Governance and management model' },
            { external: true, artifact: 'ITT documentation — continuous improvement obligations, benchmarking provisions' }
          ],
          outputs: [
            {
              name: 'Continuous improvement framework',
              format: 'Governance and process document',
              quality: [
                'Improvement identification process defined — how ideas surface from staff, data, client, technology scanning',
                'Assessment and prioritisation criteria defined — impact, feasibility, cost, alignment to client priorities',
                'Approval and funding mechanism designed — who approves, what budget, what governance',
                'Implementation process defined — how approved improvements get delivered without disrupting service',
                'Measurement framework — how we track whether improvements actually delivered the expected outcome'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SOL-08.3',
      name: 'Innovation Commercial Model & Workforce Impact',
      description: 'Design the commercial wrapper for innovation — how productivity gains are shared, how innovation investment is funded, and how the workforce transforms as AI and automation reduce headcount over the contract term',

      tasks: [
        {
          id: 'SOL-08.3.1',
          name: 'Model the innovation productivity curve — how AI, automation, and process improvement progressively reduce cost base over the contract term',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Commercial Lead / Technical Lead', i: 'Delivery Director' },
          inputs: [
            { from: 'SOL-08.1.2', artifact: 'Innovation roadmap' },
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SAL-02.3.4', artifact: 'Commercial disruption model' }
          ],
          outputs: [
            {
              name: 'Innovation productivity curve model',
              format: 'Year-on-year cost and productivity model',
              quality: [
                'Year-on-year productivity trajectory modelled — not a flat line but a progressive curve',
                'Headcount impact per innovation quantified — which roles reduce, by how many FTEs, in which year',
                'Cost reduction quantified per year — total cost base trajectory over contract term',
                'Assumptions clearly stated — adoption rate, technology maturity, client readiness, change management success',
                'Sensitivity analysis — what if adoption is slower or faster than assumed?'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-08.3.2',
          name: 'Design value sharing and investment framework — who benefits from productivity gains, how innovation investment is funded, and how this is contractually governed',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Solution Architect / Legal', i: 'Partner' },
          inputs: [
            { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model' },
            { from: 'SOL-08.1.2', artifact: 'Innovation roadmap' },
            { external: true, artifact: 'ITT documentation — innovation requirements, benchmarking provisions, gain share provisions' }
          ],
          outputs: [
            {
              name: 'Innovation value sharing and investment framework',
              format: 'Structured commercial framework',
              quality: [
                'Value sharing mechanism defined — gain share split, annual price reduction trajectory, or reinvestment commitment',
                'Investment model defined — where innovation funding comes from: upfront capex, efficiency reinvestment, dedicated fund, or client co-investment',
                'Investment vs return profile modelled — when does the crossover happen between investment and saving?',
                'Contractual governance designed — benchmarking, open-book, annual pricing reviews, innovation milestones, performance guarantees',
                'Client benefit clearly articulated — how the client sees lower cost, better outcomes, or both over the contract term',
                'Supplier margin impact understood — profitability trajectory as headcount reduces but investment increases'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-08.3.3',
          name: 'Plan workforce transformation alongside innovation — how roles evolve, redeploy, or reduce as AI and automation are introduced, within TUPE and employment law constraints',
          raci: { r: 'HR Lead / Solution Architect', a: 'Bid Director', c: 'Legal / Delivery Director', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model' },
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-08.1.2', artifact: 'Innovation roadmap' }
          ],
          outputs: [
            {
              name: 'Workforce transformation plan',
              format: 'Phased workforce change plan',
              quality: [
                'Role evolution mapped to innovation roadmap — which roles change, when, to what',
                'Redeployment and reskilling strategy for displaced roles — not just redundancy but career pathways',
                'TUPE and employment law implications of role displacement addressed — what can and cannot be done within legal constraints',
                'Natural attrition factored in — headcount reduction through turnover vs active restructuring',
                'Employee engagement approach — how workforce transformation is communicated and managed without destabilising service delivery'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-08.3.4',
          name: 'Validate innovation roadmap — credible investment case, measurable outcomes, commercially viable, workforce impact managed, aligned to evaluation criteria',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SOL-08.1.2', artifact: 'Innovation roadmap' },
            { from: 'SOL-08.1.3', artifact: 'Day-one innovation register' },
            { from: 'SOL-08.2.1', artifact: 'Continuous improvement framework' },
            { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model' },
            { from: 'SOL-08.3.2', artifact: 'Innovation value sharing and investment framework' },
            { from: 'SOL-08.3.3', artifact: 'Workforce transformation plan' }
          ],
          outputs: [
            {
              name: 'Innovation roadmap (validated — activity primary output)',
              format: 'Comprehensive innovation strategy with commercial model',
              quality: [
                'Innovation roadmap validated as realistic and deliverable',
                'Investment case is credible — funding source identified, return modelled, risk assessed',
                'Productivity curve accepted by commercial team — feeds directly into pricing model',
                'Value sharing framework accepted — client benefit and supplier margin impact understood',
                'Workforce transformation plan is legally compliant and operationally viable',
                'Day-one innovations are credible and substantiated',
                'Continuous improvement framework is proportionate and sustainable',
                'Overall innovation proposition aligned to evaluation criteria and win themes'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Innovation roadmap',
      format: 'Comprehensive innovation strategy with commercial model',
      quality: [
        'Innovation strategy defined — vision, principles, evaluation alignment',
        'Phased roadmap across contract term — innovations, investment, outcomes, timelines',
        'Day-one innovations identified — immediate impact vs current service',
        'Continuous improvement governance framework designed',
        'Productivity curve modelled — year-on-year cost trajectory as AI/automation reduce headcount',
        'Value sharing and investment framework designed — who benefits, how funded, contractual governance',
        'Workforce transformation planned — role evolution, reskilling, TUPE-compliant displacement management',
        'Validated as commercially viable, deliverable, and evaluation-aligned'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'COM-01', consumes: 'Innovation productivity curve model', usage: 'Should-cost model incorporates year-on-year cost reduction from innovation' },
    { activity: 'COM-06', consumes: 'Innovation value sharing and investment framework', usage: 'Commercial model designs gain share, pricing trajectory, and innovation investment provisions' },
    { activity: 'SOL-11', consumes: 'Innovation roadmap', usage: 'Solution design lock consolidates innovation with all solution outputs' },
    { activity: 'SOL-12', consumes: 'Innovation roadmap', usage: 'Solution risk register includes innovation delivery and adoption risks' },
    { activity: 'LEG-01', consumes: 'Innovation value sharing and investment framework', usage: 'Contract review incorporates innovation and gain share provisions' }
  ]
}
```

---

---

## SOL-09 — Social Value Proposition

```javascript
{
  id: 'SOL-09',
  name: 'Social value proposition',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Solution Architect',
  output: 'Social value plan',
  dependencies: ['SOL-04'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires social value expertise and local context knowledge
  // Note: social value is mandatory in UK government procurement (PPN 06/20) with a
  // minimum 10% weighting (often higher). It is not optional and not a tick-box exercise.
  // It is a scored section with real marks.
  //
  // Social value must be specific, measurable, and embedded in the delivery model — not
  // bolted on. Evaluators can spot when social value is a separate wish list disconnected
  // from the actual service. Local context matters enormously.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-03', artifact: 'Target operating model', note: 'Social value must be embedded in the operating model, not bolted on' },
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'Service processes where social value can be delivered' },
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'Workforce commitments — apprenticeships, local employment, diversity' },
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'How social value will be evaluated and weighted' },
    { from: 'SAL-01.2.1', artifact: 'Buyer values register', note: 'Client priorities that social value should align to' },
    { external: true, artifact: 'ITT documentation — social value requirements, evaluation criteria, local priorities' },
    { external: true, artifact: 'Social Value Model (PPN 06/20) — themes, reporting metrics, TOMs framework' },
    { external: true, artifact: 'Local area context — demographics, deprivation data, economic priorities, environmental targets, council plans' },
    { external: true, artifact: 'Supply chain social value commitments (from SUP workstream where available)' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-09.1',
      name: 'Social Value Strategy & Commitment Design',
      description: 'Analyse what the client requires and values, then design specific, measurable social value commitments aligned to the Social Value Model themes and local context',

      tasks: [
        {
          id: 'SOL-09.1.1',
          name: 'Analyse social value requirements and evaluation criteria — what the ITT requires, what themes are weighted, what the client\'s local priorities are',
          raci: { r: 'Solution Architect / Social Value Lead', a: 'Bid Director', c: 'Capture Lead / Bid Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' },
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
            { external: true, artifact: 'ITT documentation — social value requirements, evaluation criteria, local priorities' },
            { external: true, artifact: 'Social Value Model (PPN 06/20) — themes, reporting metrics, TOMs framework' },
            { external: true, artifact: 'Local area context — demographics, deprivation data, economic priorities, environmental targets, council plans' }
          ],
          outputs: [
            {
              name: 'Social value requirements analysis',
              format: 'Structured analysis',
              quality: [
                'All social value evaluation criteria identified with weightings and marks',
                'Social Value Model themes mapped to ITT requirements — which themes matter most for this procurement',
                'Local context analysed — what social value outcomes are most relevant to this geography and community',
                'Client priorities beyond the formal criteria identified — what resonates with this buyer',
                'Scoring guidance analysed — what does a top-scoring social value response look like?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-09.1.2',
          name: 'Design social value commitments — specific, measurable, embedded in delivery model and supply chain, aligned to Social Value Model themes and local priorities',
          raci: { r: 'Solution Architect / Social Value Lead', a: 'Bid Director', c: 'Delivery Director / HR Lead / Supply Chain Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-09.1.1', artifact: 'Social value requirements analysis' },
            { from: 'SOL-04', artifact: 'Service delivery model' },
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { external: true, artifact: 'Supply chain social value commitments (from SUP workstream where available)' }
          ],
          outputs: [
            {
              name: 'Social value commitment register',
              format: 'Structured register with measurable commitments',
              quality: [
                'Each commitment is specific and measurable — quantity, location, timeline, target population',
                'Commitments aligned to Social Value Model themes and TOMs metrics where applicable',
                'Commitments are embedded in the delivery model — linked to specific service, staffing, or supply chain components',
                'Supply chain social value commitments included — not just our own but partners and subcontractors',
                'Commitments are locally relevant — targeted at the geography, demographics, and priorities of the client area',
                'Commitments are proportionate to contract value and scope — credible, not aspirational'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SOL-09.1.3',
          name: 'Define monitoring and reporting framework — how social value commitments will be tracked, measured, and reported over the contract term',
          raci: { r: 'Solution Architect / Social Value Lead', a: 'Bid Director', c: 'Delivery Director / Bid Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-09.1.2', artifact: 'Social value commitment register' },
            { from: 'SOL-03.2.2', artifact: 'Governance and management model' }
          ],
          outputs: [
            {
              name: 'Social value monitoring and reporting framework',
              format: 'Structured framework',
              quality: [
                'Each commitment has a defined metric, data source, collection frequency, and reporting mechanism',
                'Reporting aligned to client requirements — format, frequency, governance forum',
                'Accountability defined — who is responsible for delivering and reporting each commitment',
                'Corrective action process defined — what happens if a commitment is behind target',
                'Framework is sustainable — not so burdensome that reporting overhead undermines delivery'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SOL-09.2',
      name: 'Social Value Integration & Validation',
      description: 'Ensure social value is genuinely embedded in the operating model and validate the plan as deliverable, measurable, and scoring-ready',

      tasks: [
        {
          id: 'SOL-09.2.1',
          name: 'Embed social value commitments in the operating model — link each commitment to specific service delivery, staffing, or supply chain components',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / HR Lead / Supply Chain Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-09.1.2', artifact: 'Social value commitment register' },
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SOL-04', artifact: 'Service delivery model' }
          ],
          outputs: [
            {
              name: 'Social value integration map',
              format: 'Commitment-to-delivery-component mapping',
              quality: [
                'Every commitment mapped to the operating model component that delivers it — not free-standing',
                'Delivery mechanism for each commitment is explicit — not just "we will" but how exactly',
                'Resource and cost implications identified per commitment — feeds COM-01',
                'Commitments that depend on supply chain partners are confirmed with those partners',
                'No orphan commitments — everything connects to the delivery model'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-09.2.2',
          name: 'Validate social value plan — commitments are deliverable, measurable, proportionate, and will score against evaluation criteria',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SOL-09.1.2', artifact: 'Social value commitment register' },
            { from: 'SOL-09.1.3', artifact: 'Social value monitoring and reporting framework' },
            { from: 'SOL-09.2.1', artifact: 'Social value integration map' }
          ],
          outputs: [
            {
              name: 'Social value plan (validated — activity primary output)',
              format: 'Comprehensive social value document',
              quality: [
                'Bid team has reviewed and challenged — not single-author plan',
                'Every commitment confirmed as deliverable within the operating model and resource plan',
                'Every commitment confirmed as measurable — metrics, data sources, and reporting defined',
                'Commitments are proportionate — neither underweight (won\'t score) nor overcommitted (can\'t deliver)',
                'Alignment to evaluation criteria confirmed — plan will score well',
                'Cost implications quantified and accepted — feeds COM-01',
                'Plan is compelling for evaluators — demonstrates genuine local impact, not generic promises'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Social value plan',
      format: 'Comprehensive social value document',
      quality: [
        'Social value requirements analysed — themes, weightings, local priorities, scoring guidance',
        'Commitments designed — specific, measurable, locally relevant, proportionate to contract',
        'Monitoring and reporting framework defined — metrics, accountability, corrective action',
        'Commitments embedded in operating model — linked to delivery, staffing, and supply chain',
        'Supply chain social value included — partner commitments, not just our own',
        'Validated as deliverable, measurable, and evaluation-aligned'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-11', consumes: 'Social value plan', usage: 'Solution design lock consolidates social value with all solution outputs' },
    { activity: 'COM-01', consumes: 'Social value plan', usage: 'Should-cost model includes social value delivery costs' },
    { activity: 'SUP-01', consumes: 'Social value commitment register', usage: 'Supply chain strategy incorporates partner social value commitments' }
  ]
}
```

---

---

## SOL-12 — Solution Risk Identification & Analysis

```javascript
{
  id: 'SOL-12',
  name: 'Solution risk identification & analysis',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Solution Architect',
  output: 'Solution risk register',
  dependencies: ['SOL-03', 'SOL-04'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires risk management expertise across solution dimensions
  // Note: this is a consolidation and synthesis activity. By this point, risks have been
  // identified across multiple upstream activities (technology, staffing, transition, innovation).
  // SOL-12 brings them together, identifies gaps, prioritises, and ensures mitigations are assigned.
  // Feeds BM-13 (bid risk register) and governance gates.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-03', artifact: 'Target operating model', note: 'Architectural risks, design assumptions' },
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'Delivery and performance risks' },
    { from: 'SOL-05', artifact: 'Technology solution design', note: 'Technology, migration, and security risks' },
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'TUPE, pension, workforce, and scarce skills risks' },
    { from: 'SOL-07.2.2', artifact: 'Transition risk register', note: 'Transition-specific risks already identified' },
    { from: 'SOL-08', artifact: 'Innovation roadmap', note: 'Innovation delivery and adoption risks' },
    { from: 'SOL-09', artifact: 'Social value plan', note: 'Social value commitment delivery risks' },
    { from: 'SOL-01.1.3', artifact: 'Requirements issues log', note: 'Unresolved ambiguities and gaps that create risk' },
    { from: 'SAL-05.2.2', artifact: 'Score gap analysis', note: 'Scoring risks from capability or evidence gaps' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-12.1',
      name: 'Solution Risk Consolidation',
      description: 'Harvest all solution-related risks from upstream activities and identify any gaps — delivery risks, compliance risks, and assumption risks not yet captured',

      tasks: [
        {
          id: 'SOL-12.1.1',
          name: 'Harvest solution risks from all upstream SOL activities — consolidate technology, staffing, transition, innovation, and social value risks into a single register',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Workstream Leads (SOL/COM/DEL)', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-05', artifact: 'Technology solution design' },
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-07.2.2', artifact: 'Transition risk register' },
            { from: 'SOL-08', artifact: 'Innovation roadmap' },
            { from: 'SOL-09', artifact: 'Social value plan' }
          ],
          outputs: [
            {
              name: 'Consolidated solution risk register (draft)',
              format: 'Structured risk register',
              quality: [
                'All risks from upstream SOL activities harvested into a single register',
                'Duplicates consolidated — same risk identified by multiple activities merged',
                'Risk categorisation applied — delivery, technology, workforce, transition, compliance, commercial, innovation',
                'Source activity referenced for each risk — traceability to where it was identified'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-12.1.2',
          name: 'Identify additional delivery and compliance risks not captured upstream — gaps, dependencies, assumptions that could fail, integration risks across solution components',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Workstream Leads (SOL/COM/DEL)', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-12.1.1', artifact: 'Consolidated solution risk register (draft)' },
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SOL-04', artifact: 'Service delivery model' },
            { from: 'SOL-01.1.3', artifact: 'Requirements issues log' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' }
          ],
          outputs: [
            {
              name: 'Complete solution risk register (draft)',
              format: 'Structured risk register (enriched)',
              quality: [
                'Cross-cutting risks identified — risks that arise from the interaction between solution components, not within any single one',
                'Assumption risks captured — key design assumptions that, if wrong, invalidate part of the solution',
                'Compliance risks identified — where the solution is non-compliant or partially compliant with requirements',
                'Dependency risks captured — risks that depend on client, outgoing supplier, or partner action',
                'Scoring risks from SAL-05 gap analysis cross-referenced — capability gaps that create delivery risk as well as scoring risk'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SOL-12.2',
      name: 'Risk Assessment & Mitigation',
      description: 'Assess, prioritise, and mitigate all consolidated risks — produce the authoritative solution risk register for governance',

      tasks: [
        {
          id: 'SOL-12.2.1',
          name: 'Assess and prioritise consolidated risks — likelihood, impact, proximity, and assign risk owner for each',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Workstream Leads', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-12.1.2', artifact: 'Complete solution risk register (draft)' }
          ],
          outputs: [
            {
              name: 'Prioritised solution risk register',
              format: 'Structured risk register with assessments',
              quality: [
                'Every risk assessed for likelihood (high/medium/low), impact (high/medium/low), and proximity (when could it materialise)',
                'Risk priority derived — critical, significant, moderate, low',
                'Risk owner assigned for every risk — named role, not "team"',
                'Top 10 risks identified — the risks that could fundamentally threaten solution delivery or bid success'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-12.2.2',
          name: 'Develop mitigation strategies for high-priority risks and confirm residual risk position',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Risk Owners / Workstream Leads', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-12.2.1', artifact: 'Prioritised solution risk register' }
          ],
          outputs: [
            {
              name: 'Mitigated solution risk register',
              format: 'Structured risk register with mitigations',
              quality: [
                'Every high and significant risk has a defined mitigation strategy — preventive and contingent actions',
                'Mitigation owner and timeline assigned — who does what by when',
                'Residual risk assessed post-mitigation — what risk remains after mitigations are applied?',
                'Risks that cannot be mitigated to acceptable levels flagged for escalation — these may affect go/no-go or require commercial provisions (e.g., risk pricing)',
                'Cost of mitigation identified where significant — feeds COM-01'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-12.2.3',
          name: 'Validate solution risk register — confirm it is complete, mitigations are credible, and the register is ready for governance gates and BM-13',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'SOL-12.2.2', artifact: 'Mitigated solution risk register' }
          ],
          outputs: [
            {
              name: 'Solution risk register (validated — activity primary output)',
              format: 'Authoritative risk register',
              quality: [
                'Bid team has reviewed and challenged — not single-author risk assessment',
                'All solution dimensions covered — no blind spots across technology, workforce, transition, innovation, compliance',
                'Top risks are understood and accepted by Bid Director — residual risk position is clear',
                'Mitigations are credible and resourced — not aspirational',
                'Register is ready for governance gates (GOV-02) and consolidation into BM-13',
                'Risk position informs whether solution design can be locked (SOL-11)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Solution risk register',
      format: 'Authoritative risk register',
      quality: [
        'All solution risks consolidated from upstream activities',
        'Cross-cutting, assumption, compliance, and dependency risks identified',
        'Every risk assessed for likelihood, impact, proximity with named owner',
        'High-priority risks mitigated with credible strategies and assigned owners',
        'Residual risk position confirmed — accepted by Bid Director',
        'Register validated by bid team and ready for governance'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'SOL-11', consumes: 'Solution risk register', usage: 'Solution design lock considers risk position before baselining the solution' },
    { activity: 'BM-13', consumes: 'Solution risk register', usage: 'Bid risk register consolidates solution risks with commercial, legal, and programme risks' },
    { activity: 'GOV-02', consumes: 'Solution risk register', usage: 'Solution & strategy governance review assesses solution risk position' },
    { activity: 'DEL-06', consumes: 'Solution risk register', usage: 'Mitigated risk register for delivery planning' },
    { activity: 'COM-01', consumes: 'Solution risk register', usage: 'Should-cost model includes risk mitigation costs and risk-priced contingency' }
  ]
}
```

---

---

## SOL-10 — Evidence Strategy & Case Study Identification

```javascript
{
  id: 'SOL-10',
  name: 'Evidence strategy & case study identification',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Bid Manager',
  output: 'Evidence requirements matrix',
  dependencies: ['SOL-04', 'SAL-05'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires knowledge of evidence library and bid content strategy
  // Note: this activity bridges SAL-05 (scoring strategy) and PRD-03 (evidence assembly).
  // SAL-05 tells us where the marks are and where our gaps are.
  // SOL-10 identifies what evidence we need to close those gaps and score.
  // PRD-03 actually assembles and formats the evidence pack.
  //
  // Evidence is not just case studies — it includes credentials, CVs, reference letters,
  // certifications, accreditations, awards, client testimonials, and performance data.
  // Supply chain evidence matters too — if we rely on a partner for capability, we need
  // their evidence (SUP-05).

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'Where the marks are and what evidence evaluators expect' },
    { from: 'SAL-05.2.2', artifact: 'Score gap analysis', note: 'Evidence gaps that create scoring risk — highest priority' },
    { from: 'SAL-04.1.4', artifact: 'Evidence substantiation assessment per theme', note: 'Which win themes have evidence gaps' },
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'What capabilities we need to evidence' },
    { from: 'SOL-03', artifact: 'Target operating model', note: 'Solution components that need credibility evidence' },
    { external: true, artifact: 'Existing evidence library — case studies, CVs, credentials, certifications, reference letters' },
    { external: true, artifact: 'ITT documentation — evidence requirements, format specifications, submission instructions' },
    { crossProduct: 'PWIN-BIDLIB', artifact: 'Bid Library content', optional: true,
      note: 'From Bid Library product if available — searchable repository of past evidence' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-10.1',
      name: 'Evidence Requirements Analysis',
      description: 'Determine what evidence is needed, where it matters most for scoring, what we already have, and where the gaps are',

      tasks: [
        {
          id: 'SOL-10.1.1',
          name: 'Map evidence requirements to evaluation sections — what type of evidence does each scored section need to achieve maximum marks?',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead / Solution Architect', i: 'Writers' },
          inputs: [
            { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' },
            { external: true, artifact: 'ITT documentation — evidence requirements, format specifications' }
          ],
          outputs: [
            {
              name: 'Evidence requirements map',
              format: 'Matrix (evaluation sections × evidence types needed)',
              quality: [
                'Every scored section assessed for evidence requirements — case studies, CVs, credentials, certifications, data, references',
                'Evidence type specified per section — what would a top-scoring response cite?',
                'Priority aligned to marks concentration — high-value sections get priority evidence sourcing',
                'Format requirements noted — some procurements specify case study format, word limits, templates'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-10.1.2',
          name: 'Assess current evidence availability — search existing library, identify what is reusable, what is outdated, and where the gaps are',
          raci: { r: 'Bid Coordinator / Bid Manager', a: 'Bid Director', c: 'SMEs / Account Managers', i: 'Writers' },
          inputs: [
            { from: 'SOL-10.1.1', artifact: 'Evidence requirements map' },
            { external: true, artifact: 'Existing evidence library — case studies, CVs, credentials, certifications, reference letters' },
            { crossProduct: 'PWIN-BIDLIB', artifact: 'Bid Library content', optional: true }
          ],
          outputs: [
            {
              name: 'Evidence availability assessment',
              format: 'Structured gap analysis',
              quality: [
                'Every evidence requirement assessed: available (ready to use), adaptable (needs updating), gap (does not exist)',
                'Available evidence assessed for currency — is it recent enough to be credible?',
                'Available evidence assessed for relevance — does it relate to this sector, scale, and service type?',
                'Gaps clearly identified with impact — which gaps affect high-value scoring sections?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-10.1.3',
          name: 'Cross-reference evidence gaps with score gap analysis — where evidence gaps create scoring risk, prioritise accordingly',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Solution Architect' },
          inputs: [
            { from: 'SOL-10.1.2', artifact: 'Evidence availability assessment' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis' },
            { from: 'SAL-04.1.4', artifact: 'Evidence substantiation assessment per theme' }
          ],
          outputs: [
            {
              name: 'Prioritised evidence gap register',
              format: 'Structured register with priority ranking',
              quality: [
                'Evidence gaps ranked by scoring impact — which gaps cost us the most marks?',
                'Gaps that overlap with SAL-05 score gaps highlighted — double jeopardy (capability gap AND evidence gap)',
                'Win theme evidence gaps cross-referenced — themes we cannot substantiate',
                'Resolution approach identified per gap — commission new, source from partner, adapt existing, accept deficit'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SOL-10.2',
      name: 'Evidence Sourcing & Commission',
      description: 'Retrieve existing evidence, adapt it for this bid, and commission new evidence where gaps exist — ensuring all high-priority evidence is in hand or in progress',

      tasks: [
        {
          id: 'SOL-10.2.1',
          name: 'Retrieve and adapt existing evidence from content library — case studies, CVs, credentials, certifications, reference letters',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'SMEs / Account Managers', i: 'Writers' },
          inputs: [
            { from: 'SOL-10.1.2', artifact: 'Evidence availability assessment' },
            { external: true, artifact: 'Existing evidence library' }
          ],
          outputs: [
            {
              name: 'Adapted evidence pack (existing)',
              format: 'Collection of adapted evidence items',
              quality: [
                'Each evidence item adapted for this bid — sector, scale, and service context aligned',
                'Currency confirmed — dates, data, and outcomes are recent and verifiable',
                'Format aligned to ITT requirements — word limits, templates, structure',
                'Client permission confirmed where required — reference letters, testimonials, named clients'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'          // Multiple evidence items can be adapted concurrently
        },
        {
          id: 'SOL-10.2.2',
          name: 'Commission new evidence where gaps identified — new case studies, reference letters, updated CVs, partner credentials, performance data',
          raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'SMEs / Account Managers / Partner Leads', i: 'Bid Director' },
          inputs: [
            { from: 'SOL-10.1.3', artifact: 'Prioritised evidence gap register' }
          ],
          outputs: [
            {
              name: 'Evidence commission register',
              format: 'Structured register with status tracking',
              quality: [
                'Every high-priority gap has a commission action — who is producing what by when',
                'Partner evidence requirements communicated to SUP-05 — case studies, CVs, credentials from partners',
                'New case studies commissioned with clear brief — what to cover, what outcomes to highlight, what format',
                'CV updates commissioned for key personnel — aligned to role requirements in staffing model',
                'Timeline realistic — evidence will be available before PRD-03 (evidence assembly) needs it'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'SOL-10.2.3',
          name: 'Validate evidence requirements matrix — all high-priority evidence either sourced or commissioned, feeds PRD-03 for assembly',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
          inputs: [
            { from: 'SOL-10.1.1', artifact: 'Evidence requirements map' },
            { from: 'SOL-10.1.3', artifact: 'Prioritised evidence gap register' },
            { from: 'SOL-10.2.1', artifact: 'Adapted evidence pack (existing)' },
            { from: 'SOL-10.2.2', artifact: 'Evidence commission register' }
          ],
          outputs: [
            {
              name: 'Evidence requirements matrix (validated — activity primary output)',
              format: 'Comprehensive evidence matrix with sourcing status',
              quality: [
                'Every evaluation section has evidence identified or commissioned',
                'High-priority gaps closed or actively being resolved — no unaddressed critical evidence gaps',
                'Evidence sourcing status tracked — available, in adaptation, commissioned, outstanding',
                'Residual evidence gaps documented with impact and mitigation — what we cannot evidence and the scoring cost',
                'Handover to PRD-03 confirmed — evidence assembly team knows what they are working with'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Evidence requirements matrix',
      format: 'Comprehensive evidence matrix with sourcing status',
      quality: [
        'Evidence requirements mapped to every evaluation section by type',
        'Current evidence availability assessed — reusable, adaptable, gap',
        'Evidence gaps prioritised by scoring impact and cross-referenced with score gap analysis',
        'Existing evidence retrieved and adapted for this bid',
        'New evidence commissioned with clear briefs and timelines',
        'All high-priority evidence sourced or in progress — no unaddressed critical gaps'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'PRD-03', consumes: 'Evidence requirements matrix + adapted evidence pack', usage: 'Evidence assembly uses the matrix and sourced evidence to compile the final evidence pack' },
    { activity: 'SUP-05', consumes: 'Partner evidence requirements', usage: 'Partner credentials and references activity responds to evidence gaps requiring partner input' },
    { activity: 'SOL-11', consumes: 'Evidence requirements matrix', usage: 'Solution design lock confirms evidence position alongside solution outputs' },
    { activity: 'BM-10', consumes: 'Evidence requirements matrix', usage: 'Storyboard development incorporates evidence placement per response section' }
  ]
}
```

---

---

## SOL-11 — Solution Design Lock

```javascript
{
  id: 'SOL-11',
  name: 'Solution design lock',
  workstream: 'SOL',
  phase: 'DEV',
  role: 'Solution Architect',
  output: 'Solution design pack (locked & assured)',
  dependencies: ['SOL-03', 'SOL-04', 'SOL-05', 'SOL-06', 'SOL-07', 'SOL-08', 'SOL-09', 'SOL-10', 'SOL-12'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'C',               // Coordination — bringing everything together, not parallel work
  // Note: this is a consolidation and lock activity, not a design activity.
  // All design work is done in SOL-01 through SOL-12. SOL-11 brings it together,
  // assures it, and baselines it.
  //
  // Once locked, solution changes require formal review. This is the handover point
  // from solution design to proposal production. Everything downstream (pricing,
  // storyboard, drafting) builds on what is locked here.
  //
  // Fires "Solution Design Complete" milestone in the key milestones view.
  // Feeds GOV-02 (Solution & Strategy Review) governance gate.

  // ── Structured inputs ──────────────────────────────────────────────
  // Every SOL activity output feeds into this consolidation
  inputs: [
    { from: 'SOL-01', artifact: 'Requirements interpretation document' },
    { from: 'SOL-02', artifact: 'As-is operating model assessment' },
    { from: 'SOL-03', artifact: 'Target operating model' },
    { from: 'SOL-04', artifact: 'Service delivery model' },
    { from: 'SOL-05', artifact: 'Technology solution design' },
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
    { from: 'SOL-07', artifact: 'Transition plan' },
    { from: 'SOL-08', artifact: 'Innovation roadmap' },
    { from: 'SOL-09', artifact: 'Social value plan' },
    { from: 'SOL-10', artifact: 'Evidence requirements matrix' },
    { from: 'SOL-12', artifact: 'Solution risk register' },
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'Win strategy baseline — is the solution still aligned?' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'SOL-11.1',
      name: 'Solution Consolidation',
      description: 'Bring all solution workstream outputs together into a single design pack and confirm they are complete, consistent, and coherent as an integrated solution',

      tasks: [
        {
          id: 'SOL-11.1.1',
          name: 'Consolidate all solution workstream outputs into a single design pack — TOM, service delivery, technology, staffing, transition, innovation, social value, evidence, risk',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Workstream Leads', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SOL-04', artifact: 'Service delivery model' },
            { from: 'SOL-05', artifact: 'Technology solution design' },
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-07', artifact: 'Transition plan' },
            { from: 'SOL-08', artifact: 'Innovation roadmap' },
            { from: 'SOL-09', artifact: 'Social value plan' },
            { from: 'SOL-10', artifact: 'Evidence requirements matrix' },
            { from: 'SOL-12', artifact: 'Solution risk register' }
          ],
          outputs: [
            {
              name: 'Consolidated solution design pack (draft)',
              format: 'Comprehensive solution document',
              quality: [
                'All solution components present — no missing workstream outputs',
                'Document structure is navigable — clear sections, cross-references, summary',
                'Version control applied — each component at its validated/final version'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-11.1.2',
          name: 'Conduct completeness and coherence check — are all components present, consistent with each other, and aligned to the win strategy?',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Workstream Leads', i: 'Capture Lead' },
          inputs: [
            { from: 'SOL-11.1.1', artifact: 'Consolidated solution design pack (draft)' },
            { from: 'SOL-01', artifact: 'Requirements interpretation document' },
            { from: 'SAL-06', artifact: 'Capture plan (locked)' }
          ],
          outputs: [
            {
              name: 'Solution coherence assessment',
              format: 'Structured review checklist with findings',
              quality: [
                'Consistency checked across components — staffing model matches service delivery, technology enables the operating model, transition delivers the future state',
                'Requirements coverage confirmed — cross-reference against SOL-01 requirements interpretation',
                'Win strategy alignment confirmed — solution still delivers the win themes and competitive positioning from SAL-06',
                'Contradictions or gaps between components identified and resolved',
                'Open issues documented — anything unresolved that governance must accept'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'SOL-11.2',
      name: 'Solution Assurance & Lock',
      description: 'Assure the solution is deliverable, costable, compliant, and competitive — then baseline and lock for downstream consumption',

      tasks: [
        {
          id: 'SOL-11.2.1',
          name: 'Conduct internal solution assurance review — is the solution deliverable, costable, compliant, and competitive?',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Delivery Director / Commercial Lead / Technical Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-11.1.1', artifact: 'Consolidated solution design pack (draft)' },
            { from: 'SOL-11.1.2', artifact: 'Solution coherence assessment' },
            { from: 'SOL-12', artifact: 'Solution risk register' }
          ],
          outputs: [
            {
              name: 'Solution assurance record',
              format: 'Structured assurance review output',
              quality: [
                'Deliverability confirmed — the delivery team believes this solution can be mobilised and operated',
                'Costability confirmed — commercial team can build a should-cost model from this design',
                'Compliance confirmed — solution addresses all mandatory requirements and scored criteria',
                'Competitiveness assessed — solution delivers the win themes and creates differentiation',
                'Risk position accepted — solution risk register reviewed, residual risks acknowledged',
                'Residual issues documented — anything that must be resolved during production or accepted as risk'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SOL-11.2.2',
          name: 'Baseline and lock solution design pack — formal sign-off, "Solution Design Complete" milestone fires, feeds GOV-02',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Solution Architect', i: 'Bid Team (collective)' },
          inputs: [
            { from: 'SOL-11.1.1', artifact: 'Consolidated solution design pack (draft)' },
            { from: 'SOL-11.2.1', artifact: 'Solution assurance record' }
          ],
          outputs: [
            {
              name: 'Solution design pack (locked & assured — activity primary output)',
              format: 'Baselined solution document with formal sign-off',
              quality: [
                'Solution design pack formally baselined — this is the authoritative solution reference for the bid',
                'Bid Director sign-off recorded — accountability for the solution accepted',
                '"Solution Design Complete" milestone fires in the product',
                'Changes after lock require formal change review — not ad hoc modification',
                'Downstream activities briefed — COM-01 (costing), BM-10 (storyboard), PRD-02 (drafting) all build from this baseline',
                'GOV-02 (Solution & Strategy Review) can now proceed with formal governance assurance'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Solution design pack (locked & assured)',
      format: 'Baselined solution document with formal sign-off',
      quality: [
        'All solution workstream outputs consolidated into single authoritative pack',
        'Completeness and coherence confirmed — components are consistent and integrated',
        'Requirements coverage confirmed against SOL-01',
        'Win strategy alignment confirmed against SAL-06',
        'Solution assured as deliverable, costable, compliant, and competitive',
        'Risk position accepted — solution risk register acknowledged',
        'Formally baselined with Bid Director sign-off — changes require formal review'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'GOV-02', consumes: 'Solution design pack (locked & assured)', usage: 'Solution & Strategy Review governance gate — formal organisational assurance of the solution' },
    { activity: 'COM-01', consumes: 'Solution design pack (locked & assured)', usage: 'Should-cost model built from the locked solution — staffing, technology, transition, innovation costs' },
    { activity: 'BM-10', consumes: 'Solution design pack (locked & assured)', usage: 'Storyboard development structures the response around the locked solution' },
    { activity: 'PRD-02', consumes: 'Solution design pack (locked & assured)', usage: 'Section drafting references the locked solution as the authoritative source' }
  ]
}
```

---

---

## COM-01 — Should-cost Model Development

```javascript
{
  id: 'COM-01',
  name: 'Should-cost model development',
  workstream: 'COM',
  phase: 'DEV',
  role: 'Commercial Lead',
  output: 'Should-cost model',
  dependencies: ['SOL-04', 'SOL-06'],
  effortDays: 8,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires commercial and financial modelling expertise
  // Note: this is the BOTTOM-UP costing activity — what does our solution actually cost
  // to deliver? Built from first principles using solution workstream outputs.
  // This is the "truth" that gets presented to executives at gate reviews.
  // Executives then determine the profit margin based on risk appetite.
  //
  // The top-down price-to-win (COM-02) runs in parallel — the tension between
  // bottom-up cost and top-down win price is where the real commercial strategy lives.
  // If bottom-up exceeds top-down, something gives: solution, margin, or bid decision.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'Processes, resource model, capacity — what to cost' },
    { from: 'SOL-04.1.2', artifact: 'Resource and capacity model', note: 'FTEs, roles, grades per service line' },
    { from: 'SOL-05', artifact: 'Technology solution design', note: 'Licensing, development, hosting, support costs' },
    { from: 'SOL-05.1.2', artifact: 'Build/buy/reuse assessment', note: 'COTS licensing vs build costs' },
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'Workforce costs — salaries, pensions, NI, benefits, TUPE cost impact' },
    { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis', note: 'Recruitment, redundancy, training costs' },
    { from: 'SOL-07', artifact: 'Transition plan', note: 'Mobilisation and one-off transition costs' },
    { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model', note: 'Year-on-year cost trajectory as AI/automation reduce headcount' },
    { from: 'SOL-09', artifact: 'Social value plan', note: 'Cost of delivering social value commitments' },
    { from: 'SOL-12', artifact: 'Solution risk register', note: 'Risk mitigation costs and contingency requirements' },
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'Commercial framework and payment mechanism context from capture plan' },
    { external: true, artifact: 'Corporate rate cards, salary benchmarks, overhead rates, standard cost assumptions' },
    { external: true, artifact: 'ITT documentation — pricing schedule structure, cost categories, indexation provisions' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'COM-01.1',
      name: 'Cost Build-Up',
      description: 'Build the should-cost model from first principles — workforce, non-workforce, transition, and partner costs — aligned to the locked solution design',

      tasks: [
        {
          id: 'COM-01.1.1',
          name: 'Build workforce cost model — people costs from SOL-06 staffing model: salaries, pensions, employer NI, benefits, training, recruitment costs per role per year',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'HR Lead / Finance', i: 'Solution Architect' },
          inputs: [
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis' },
            { external: true, artifact: 'Corporate rate cards, salary benchmarks, overhead rates' }
          ],
          outputs: [
            {
              name: 'Workforce cost model',
              format: 'Structured cost model (per role, per year)',
              quality: [
                'Every role costed — salary/day rate, employer NI, pension contribution, benefits, overhead',
                'TUPE-transferring workforce costed at their actual terms — not our standard rates',
                'Gap resolution costs included — recruitment fees, redundancy provisions, interim/agency costs',
                'Training and upskilling costs included per the workforce gap analysis',
                'Year-on-year workforce cost profile — not flat, reflects planned changes across contract term'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'COM-01.1.2',
          name: 'Build non-workforce cost model — technology, facilities, consumables, travel, insurance, management overhead, third-party services',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Technical Lead / Delivery Director', i: 'Finance' },
          inputs: [
            { from: 'SOL-05', artifact: 'Technology solution design' },
            { from: 'SOL-05.1.2', artifact: 'Build/buy/reuse assessment' },
            { from: 'SOL-09', artifact: 'Social value plan' },
            { external: true, artifact: 'Corporate cost assumptions, standard overhead rates' }
          ],
          outputs: [
            {
              name: 'Non-workforce cost model',
              format: 'Structured cost model (per category, per year)',
              quality: [
                'Technology costs itemised — licensing, hosting, development, support, maintenance per year',
                'Facilities and property costs included where applicable — rent, utilities, equipment',
                'Social value delivery costs quantified per commitment',
                'Management overhead and corporate charges applied appropriately',
                'Year-on-year non-workforce profile modelled — technology costs may reduce as development completes'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'COM-01.1.3',
          name: 'Build transition and mobilisation cost model — one-off costs from SOL-07: dual running, recruitment, technology migration, training, mobilisation team',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Delivery Director', i: 'Finance' },
          inputs: [
            { from: 'SOL-07', artifact: 'Transition plan' }
          ],
          outputs: [
            {
              name: 'Transition cost model',
              format: 'Structured one-off cost model',
              quality: [
                'All one-off transition costs quantified — mobilisation team, dual running period, parallel systems',
                'Recruitment and onboarding costs for gap roles included',
                'Technology migration costs included — data migration, system deployment, parallel running',
                'Training and induction costs for transferring and new workforce included',
                'Clear distinction between one-off transition costs and recurring steady-state costs'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'COM-01.1.4',
          name: 'Incorporate partner and supply chain cost placeholder — to be updated when COM-03 confirms partner pricing',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Supply Chain Lead', i: 'Partner Leads' },
          inputs: [
            { external: true, artifact: 'Indicative partner cost estimates (pre-COM-03)' }
          ],
          outputs: [
            {
              name: 'Partner cost placeholder',
              format: 'Estimated partner cost line items',
              quality: [
                'All known partner and subcontractor cost elements identified with indicative values',
                'Placeholder marked for update when COM-03 (partner pricing) confirms actual costs',
                'Risk range noted — what is the variance between indicative and likely final partner costs?'
              ]
            }
          ],
          effort: 'Low',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'COM-01.2',
      name: 'Cost Modelling & Assumptions',
      description: 'Model the full cost trajectory across the contract term, document every assumption, and validate the should-cost model as the basis for pricing',

      tasks: [
        {
          id: 'COM-01.2.1',
          name: 'Model cost trajectory across the contract term — year-on-year cost profile incorporating innovation productivity curve and planned changes',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Solution Architect / Finance', i: 'Delivery Director' },
          inputs: [
            { from: 'COM-01.1.1', artifact: 'Workforce cost model' },
            { from: 'COM-01.1.2', artifact: 'Non-workforce cost model' },
            { from: 'COM-01.1.3', artifact: 'Transition cost model' },
            { from: 'COM-01.1.4', artifact: 'Partner cost placeholder' },
            { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model' }
          ],
          outputs: [
            {
              name: 'Contract-term cost model',
              format: 'Year-on-year cost projection',
              quality: [
                'Full contract term modelled year by year — not a flat annual cost extrapolated',
                'Innovation productivity curve incorporated — headcount and cost reductions phased per SOL-08 roadmap',
                'Transition costs profiled in year 0/1 — clear distinction from steady-state recurring costs',
                'Indexation and inflation assumptions applied where applicable',
                'Total cost of service and total cost of ownership both calculated'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'COM-01.2.2',
          name: 'Document all cost assumptions — inflation, attrition, utilisation, volume, demand variability, rate card basis, contingency approach',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Solution Architect' },
          inputs: [
            { from: 'COM-01.2.1', artifact: 'Contract-term cost model' },
            { from: 'SOL-12', artifact: 'Solution risk register', note: 'Risk-driven contingency requirements' }
          ],
          outputs: [
            {
              name: 'Cost assumptions register',
              format: 'Structured assumptions register',
              quality: [
                'Every material cost assumption documented — basis, source, confidence level',
                'Key assumptions identified — the ones that, if wrong, materially change the cost',
                'Contingency approach documented — how risk is priced (explicit contingency line, risk premium, or absorbed in margin)',
                'Assumptions register feeds directly into COM-05 (sensitivity analysis) — each assumption is a sensitivity variable'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-01.2.3',
          name: 'Validate should-cost model — confirm it reflects the locked solution, is internally consistent, and provides a credible basis for pricing',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Solution Architect', i: 'Bid Manager' },
          inputs: [
            { from: 'COM-01.2.1', artifact: 'Contract-term cost model' },
            { from: 'COM-01.2.2', artifact: 'Cost assumptions register' }
          ],
          outputs: [
            {
              name: 'Should-cost model (validated — activity primary output)',
              format: 'Comprehensive cost model with assumptions',
              quality: [
                'Cost model reconciles to the locked solution — every SOL output is costed',
                'Bottom-up total is internally consistent — workforce + non-workforce + transition + partner = total',
                'Year-on-year cost trajectory is credible — reflects planned innovation and workforce changes',
                'All assumptions documented and flagged for sensitivity testing',
                'Model is structured for executive presentation — clear, auditable, defensible',
                'Ready for comparison against top-down price-to-win (COM-02)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Should-cost model',
      format: 'Comprehensive cost model with assumptions',
      quality: [
        'Workforce costs built from staffing model — per role, per year, TUPE terms reflected',
        'Non-workforce costs built — technology, facilities, social value, overhead',
        'Transition costs profiled — one-off mobilisation and migration costs',
        'Partner costs included (indicative pending COM-03)',
        'Year-on-year cost trajectory modelled — innovation productivity curve incorporated',
        'All assumptions documented with confidence levels',
        'Validated as reflective of locked solution, internally consistent, and executive-presentable'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'COM-02', consumes: 'Should-cost model', usage: 'Price-to-win analysis compares bottom-up cost against top-down win price' },
    { activity: 'COM-05', consumes: 'Should-cost model + cost assumptions register', usage: 'Sensitivity analysis stress-tests key assumptions' },
    { activity: 'COM-06', consumes: 'Should-cost model', usage: 'Pricing finalisation builds price from validated cost base plus margin' },
    { activity: 'GOV-03', consumes: 'Should-cost model', usage: 'Pricing & risk governance review examines the cost base' }
  ]
}
```

---

---

## COM-02 — Price-to-Win Analysis

```javascript
{
  id: 'COM-02',
  name: 'Price-to-win analysis',
  workstream: 'COM',
  phase: 'DEV',
  role: 'Commercial Lead',
  output: 'Price-to-win assessment',
  dependencies: ['SAL-03', 'COM-01'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires commercial intelligence and pricing strategy expertise
  // Note: this is the TOP-DOWN pricing activity — starts from the market and works
  // backward. What's the current contract value? What do competitors bid? Where must
  // we land to win? Then compare against the bottom-up cost (COM-01).
  //
  // The tension between bottom-up cost and top-down win price is where the real
  // commercial strategy lives. If bottom-up exceeds top-down, something gives:
  // solution, margin, or bid decision.
  //
  // PROCUREMENT ACT 2023 context: replaces old MEAT (Most Economically Advantageous
  // Tender) with MAT (Most Advantageous Tender). The word "economically" is dropped —
  // quality, social value, and strategic factors can be weighted more heavily.
  // New assessment mechanisms and transparency requirements. The quality/price
  // interaction is now potentially more quality-dominant, which changes the price-to-win
  // calculus — a higher price may be viable if quality score is sufficiently strong.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'COM-01', artifact: 'Should-cost model', note: 'Bottom-up cost to compare against top-down price envelope' },
    { from: 'SAL-03', artifact: 'Competitive landscape assessment', note: 'Competitor profiles and likely price positioning' },
    { from: 'SAL-02.2.1', artifact: 'Incumbent price position assessment', note: 'Current contract value and incumbent cost base' },
    { from: 'SAL-01.2.1', artifact: 'Buyer values register', note: 'Client budget signals and affordability context' },
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'Quality/price split and scoring model — determines how much price matters vs quality' },
    { from: 'SAL-05.2.2', artifact: 'Score gap analysis', note: 'Our likely quality score position — can we win on quality at a higher price?' },
    { from: 'SOL-08.3.2', artifact: 'Innovation value sharing and investment framework', note: 'How innovation investment changes the price trajectory' },
    { external: true, artifact: 'Contracts Finder / FTS award data — current and historical contract values for this requirement' },
    { external: true, artifact: 'Industry benchmarking data — unit costs, service rates, commodity pricing (Gartner, ISG, NelsonHall, RICS, or sector-specific benchmarks)' },
    { external: true, artifact: 'Procurement Act 2023 assessment framework — MAT criteria, transparency requirements, new evaluation mechanisms' },
    { external: true, artifact: 'ITT documentation — pricing evaluation methodology, price/quality weighting, affordability cap (if any)' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'COM-02.1',
      name: 'Market Price Intelligence',
      description: 'Build the top-down price picture from all available intelligence — current contract, competitors, benchmarks, client budget, and the regulatory framework that governs how price is evaluated',

      tasks: [
        {
          id: 'COM-02.1.1',
          name: 'Establish the current cost baseline — existing contract value, historical award data, and industry benchmarking for comparable services or commodities',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Capture Lead / Market Intelligence', i: 'Solution Architect' },
          inputs: [
            { from: 'SAL-02.2.1', artifact: 'Incumbent price position assessment' },
            { external: true, artifact: 'Contracts Finder / FTS award data — current and historical contract values' },
            { external: true, artifact: 'Industry benchmarking data — unit costs, service rates, commodity pricing' }
          ],
          outputs: [
            {
              name: 'Market price baseline',
              format: 'Structured price intelligence',
              quality: [
                'Current contract value documented with source — known award value, extensions, amendments',
                'Historical price trajectory noted — has the contract value grown, shrunk, or remained stable?',
                'Industry benchmarks applied where available — unit costs for commodity elements (e.g., cost per endpoint, cost per FTE managed, cost per transaction)',
                'Benchmark sources cited — Gartner, ISG, NelsonHall, RICS, or sector-specific — with publication date and relevance assessment',
                'Where no benchmarks exist, comparable contract values used as proxy with confidence assessment'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-02.1.2',
          name: 'Assess competitor price positioning — what are credible competitors likely to bid based on their cost base, strategy, and market behaviour?',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Capture Lead', i: 'Partner Lead' },
          inputs: [
            { from: 'SAL-03', artifact: 'Competitive landscape assessment' },
            { from: 'COM-02.1.1', artifact: 'Market price baseline' }
          ],
          outputs: [
            {
              name: 'Competitor price position assessment',
              format: 'Per-competitor estimated price range',
              quality: [
                'Each credible competitor assessed for likely price range — low/mid/high with rationale',
                'Assessment based on known cost structures, market behaviour, strategic intent (buying the contract, defending margin, disrupting)',
                'Incumbent price advantage or disadvantage quantified — are they likely to bid below current value?',
                'Confidence level stated per assessment — known, inferred, or assumed'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-02.1.3',
          name: 'Assess client budget and affordability — what can the client afford, what signals have they given, and how does the Procurement Act MAT framework affect price evaluation?',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Capture Lead / Account Manager', i: 'Bid Manager' },
          inputs: [
            { from: 'SAL-01.2.1', artifact: 'Buyer values register' },
            { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' },
            { external: true, artifact: 'ITT documentation — pricing evaluation methodology, price/quality weighting, affordability cap (if any)' },
            { external: true, artifact: 'Procurement Act 2023 assessment framework — MAT criteria, new evaluation mechanisms' }
          ],
          outputs: [
            {
              name: 'Client affordability and evaluation context assessment',
              format: 'Structured assessment',
              quality: [
                'Client budget signals documented — affordability cap, spending review constraints, value-for-money expectations',
                'Price/quality weighting analysed — under Procurement Act MAT framework, how much does price actually drive the outcome?',
                'Assessment of whether quality-dominant evaluation enables a premium price position — can we win at a higher price with a superior quality score?',
                'New Procurement Act mechanisms assessed — direct award thresholds, competitive flexible procedure, dynamic markets (if relevant to this procurement)',
                'Affordability risk assessed — is there a price ceiling above which the client simply cannot award, regardless of quality?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'COM-02.2',
      name: 'Price-to-Win Modelling',
      description: 'Synthesise all intelligence into a price envelope, compare against bottom-up cost, and determine where to position — factoring in quality/price interaction under the new Procurement Act MAT framework',

      tasks: [
        {
          id: 'COM-02.2.1',
          name: 'Model the price envelope — floor, competitive midpoint, and ceiling — incorporating quality/price interaction and Procurement Act MAT assessment framework',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Capture Lead / Finance', i: 'Solution Architect' },
          inputs: [
            { from: 'COM-02.1.1', artifact: 'Market price baseline' },
            { from: 'COM-02.1.2', artifact: 'Competitor price position assessment' },
            { from: 'COM-02.1.3', artifact: 'Client affordability and evaluation context assessment' },
            { from: 'SAL-05.2.2', artifact: 'Score gap analysis', note: 'Our likely quality score position' }
          ],
          outputs: [
            {
              name: 'Price-to-win envelope',
              format: 'Structured price range with rationale',
              quality: [
                'Three price points defined: floor (minimum viable margin), competitive midpoint (likely winning range), ceiling (maximum the market will bear)',
                'Quality/price interaction modelled — at our expected quality score, what price range wins? Under MAT, quality advantage may justify price premium',
                'Each price point has a rationale — not arbitrary numbers but evidence-based from market intelligence',
                'Industry benchmarks used as validation — does our envelope align with market rates for comparable services?',
                'Scenario analysis: what happens if our quality score is higher or lower than expected?'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'COM-02.2.2',
          name: 'Compare bottom-up cost against top-down price envelope — is the gap bridgeable? What are the options if it is not?',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Solution Architect / Finance', i: 'Partner' },
          inputs: [
            { from: 'COM-02.2.1', artifact: 'Price-to-win envelope' },
            { from: 'COM-01', artifact: 'Should-cost model' }
          ],
          outputs: [
            {
              name: 'Bottom-up vs top-down gap analysis',
              format: 'Structured gap assessment with options',
              quality: [
                'Gap between bottom-up cost and top-down win price quantified — total and per year',
                'Gap characterised: positive (margin available), neutral (break-even), or negative (cost exceeds win price)',
                'If negative: options identified and quantified — solution descope, innovation acceleration, margin reduction, partner renegotiation, or walk away',
                'If positive: margin range identified — what profit is available at each price point in the envelope?',
                'Commercial strategy recommendation stated — where in the envelope should we land, and why?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-02.2.3',
          name: 'Validate price-to-win assessment — confirm the recommended price position and escalate if bottom-up exceeds top-down',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Partner', i: 'Bid Manager' },
          inputs: [
            { from: 'COM-02.2.1', artifact: 'Price-to-win envelope' },
            { from: 'COM-02.2.2', artifact: 'Bottom-up vs top-down gap analysis' }
          ],
          outputs: [
            {
              name: 'Price-to-win assessment (validated — activity primary output)',
              format: 'Executive pricing intelligence document',
              quality: [
                'Recommended price position stated with rationale — where in the envelope and why',
                'Market intelligence summarised — current value, competitor positioning, benchmarks, client affordability',
                'Quality/price interaction under MAT framework assessed — does our quality advantage justify our price position?',
                'Bottom-up vs top-down gap clearly stated — margin available or gap to close',
                'If gap exists: options presented with recommendation for executive decision',
                'Assessment ready for executive presentation at pricing governance gate'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Price-to-win assessment',
      format: 'Executive pricing intelligence document',
      quality: [
        'Market price baseline established — current contract value, historical data, industry benchmarks',
        'Competitor price positioning assessed per credible competitor',
        'Client affordability and budget context assessed',
        'Procurement Act MAT framework implications analysed — quality/price interaction',
        'Price envelope modelled — floor, midpoint, ceiling with evidence-based rationale',
        'Bottom-up vs top-down gap quantified with options if negative',
        'Recommended price position stated for executive decision'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'COM-05', consumes: 'Price-to-win assessment', usage: 'Sensitivity analysis tests the price position against key assumptions' },
    { activity: 'COM-06', consumes: 'Price-to-win assessment', usage: 'Pricing finalisation lands the actual price within the validated envelope' },
    { activity: 'GOV-03', consumes: 'Price-to-win assessment', usage: 'Pricing governance review uses market intelligence to assess proposed price' }
  ]
}
```

---

---

## COM-03 — Subcontractor & Supply Chain Pricing

```javascript
{
  id: 'COM-03',
  name: 'Subcontractor & supply chain pricing',
  workstream: 'COM',
  phase: 'DEV',
  role: 'Commercial Lead',
  output: 'Partner pricing schedule',
  dependencies: ['SUP-04'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires commercial negotiation and partner management
  // Note: the consortium strategy, structure, and work breakdown are already locked
  // in SAL-06 L2.3. This activity executes against that strategic framework —
  // defining the detailed commercial structure between parties and getting firm
  // pricing from each partner.
  //
  // The output updates COM-01 — partner cost placeholders replaced with actual pricing.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SAL-06.3.1', artifact: 'Consortium strategy', note: 'Prime/sub, JV, SPV — the locked strategic framework' },
    { from: 'SAL-06.3.3', artifact: 'Consortium delivery model and work breakdown', note: 'Who owns what scope — the basis for pricing requests' },
    { from: 'SUP-04', artifact: 'Partner pricing schedules', note: 'Raw partner pricing submissions' },
    { from: 'SUP-02', artifact: 'Partner solution inputs pack', note: 'What each partner is delivering — scope context for pricing' },
    { from: 'COM-01', artifact: 'Should-cost model', note: 'Our cost assumptions — partner pricing must align' },
    { from: 'COM-01.2.2', artifact: 'Cost assumptions register', note: 'Volume, indexation, demand assumptions that partners must price against' },
    { external: true, artifact: 'Corporate procurement and partner commercial policies' },
    { external: true, artifact: 'ITT documentation — pricing schedule structure, subcontractor disclosure requirements' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'COM-03.1',
      name: 'Commercial Structure & Work Breakdown Detailing',
      description: 'Take the consortium strategy locked in SAL-06 and detail the commercial framework between parties — margin stack, risk sharing, payment flow — before issuing pricing requests',

      tasks: [
        {
          id: 'COM-03.1.1',
          name: 'Detail the inter-party commercial framework — margin stack, risk sharing principles, payment flow, indexation basis, volume commitments between consortium members',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Legal / Partner Commercial Leads', i: 'Finance' },
          inputs: [
            { from: 'SAL-06.3.1', artifact: 'Consortium strategy' },
            { from: 'SAL-06.3.3', artifact: 'Consortium delivery model and work breakdown' },
            { external: true, artifact: 'Corporate procurement and partner commercial policies' }
          ],
          outputs: [
            {
              name: 'Inter-party commercial framework',
              format: 'Structured commercial terms document',
              quality: [
                'Margin stack defined — how margin is allocated across the consortium (prime margin, partner margin, management fee)',
                'Risk sharing principles defined — who bears what risk (delivery, performance, financial, TUPE)',
                'Payment flow designed — how money flows from client through prime to partners, payment terms, retention',
                'Indexation and volume commitment basis aligned — partners price against the same assumptions as our model',
                'Framework is commercially viable for all parties — not so aggressive that partners walk away or price in risk'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'COM-03.1.2',
          name: 'Prepare structured pricing requests for each partner — scope, volumes, assumptions, timeline, format aligned to work breakdown and our commercial model',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Supply Chain Lead / Solution Architect', i: 'Partner Leads' },
          inputs: [
            { from: 'COM-03.1.1', artifact: 'Inter-party commercial framework' },
            { from: 'SAL-06.3.3', artifact: 'Consortium delivery model and work breakdown' },
            { from: 'COM-01.2.2', artifact: 'Cost assumptions register' }
          ],
          outputs: [
            {
              name: 'Partner pricing request packs',
              format: 'Per-partner structured pricing request',
              quality: [
                'Each partner receives a clear scope definition — what they are pricing, aligned to the work breakdown',
                'Volume and demand assumptions specified — partners price the same volumes we are modelling',
                'Pricing format specified — aligned to our commercial model structure for easy integration',
                'Timeline specified — when we need firm pricing by, aligned to COM-06 pricing lock',
                'Commercial terms summarised — margin, risk, payment, indexation basis included so partners price realistically'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'COM-03.2',
      name: 'Partner Pricing Collection & Negotiation',
      description: 'Collect, validate, and negotiate partner pricing — ensuring submissions are complete, assumptions align, and terms are commercially viable',

      tasks: [
        {
          id: 'COM-03.2.1',
          name: 'Review and validate partner pricing submissions — completeness, assumption alignment, competitiveness, and fit within our commercial model',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Solution Architect', i: 'Supply Chain Lead' },
          inputs: [
            { from: 'SUP-04', artifact: 'Partner pricing schedules' },
            { from: 'COM-03.1.2', artifact: 'Partner pricing request packs' },
            { from: 'COM-01', artifact: 'Should-cost model' }
          ],
          outputs: [
            {
              name: 'Partner pricing validation assessment',
              format: 'Per-partner structured review',
              quality: [
                'Each partner submission reviewed for completeness — all scope elements priced, no gaps',
                'Assumption alignment confirmed — volumes, indexation, demand basis consistent with our model',
                'Competitiveness assessed — is the partner pricing reasonable vs market benchmarks?',
                'Integration with our cost model tested — does the partner pricing fit within the overall commercial framework?',
                'Issues and gaps documented per partner — what needs resolving before pricing can be confirmed'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'          // Multiple partners reviewed concurrently
        },
        {
          id: 'COM-03.2.2',
          name: 'Negotiate partner pricing and terms — resolve gaps, align assumptions, agree final pricing and risk allocation per partner',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Partner Commercial Leads / Legal', i: 'Finance' },
          inputs: [
            { from: 'COM-03.2.1', artifact: 'Partner pricing validation assessment' }
          ],
          outputs: [
            {
              name: 'Negotiated partner pricing',
              format: 'Per-partner confirmed pricing with terms',
              quality: [
                'Final pricing agreed per partner — firm, not indicative',
                'Assumptions aligned and documented — any remaining differences explicitly noted',
                'Commercial terms agreed — margin, risk sharing, payment terms, indexation, volume commitments',
                'Pricing validity period confirmed — how long the partner will hold these prices',
                'Any conditions or caveats from partners documented — e.g. "subject to teaming agreement"'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'COM-03.3',
      name: 'Partner Pricing Integration',
      description: 'Integrate confirmed partner pricing into the should-cost model and validate the complete partner pricing schedule',

      tasks: [
        {
          id: 'COM-03.3.1',
          name: 'Integrate confirmed partner pricing into the should-cost model — replace placeholders, reconcile assumptions, update year-on-year cost trajectory',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Solution Architect' },
          inputs: [
            { from: 'COM-03.2.2', artifact: 'Negotiated partner pricing' },
            { from: 'COM-01', artifact: 'Should-cost model' }
          ],
          outputs: [
            {
              name: 'Updated should-cost model (partner pricing confirmed)',
              format: 'Updated cost model',
              quality: [
                'Partner cost placeholders replaced with confirmed pricing',
                'Year-on-year cost trajectory updated with actual partner pricing profiles',
                'Any assumption differences between our model and partner pricing reconciled or risk-noted',
                'Total cost of service recalculated with actual partner costs'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-03.3.2',
          name: 'Validate partner pricing schedule — all partners priced, assumptions aligned, commercially viable, feeds COM-05 and COM-06',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Supply Chain Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'COM-03.3.1', artifact: 'Updated should-cost model (partner pricing confirmed)' },
            { from: 'COM-03.2.2', artifact: 'Negotiated partner pricing' }
          ],
          outputs: [
            {
              name: 'Partner pricing schedule (validated — activity primary output)',
              format: 'Comprehensive partner pricing document',
              quality: [
                'All partners have confirmed, firm pricing — no outstanding indicative submissions',
                'Commercial terms agreed per partner — margin, risk, payment, indexation',
                'Should-cost model updated and reconciled with actual partner costs',
                'Partner pricing risks documented — conditions, caveats, assumption sensitivities',
                'Schedule ready for COM-05 (sensitivity analysis) and COM-06 (pricing finalisation)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Partner pricing schedule',
      format: 'Comprehensive partner pricing document',
      quality: [
        'Inter-party commercial framework defined — margin stack, risk sharing, payment flow',
        'Structured pricing requests issued per partner aligned to work breakdown',
        'All partner pricing collected, validated, and negotiated to firm terms',
        'Partner pricing integrated into should-cost model — placeholders replaced',
        'Commercial terms agreed per partner — ready for back-to-back formalisation (SUP-06)',
        'All partners confirmed — no outstanding indicative submissions'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'COM-05', consumes: 'Partner pricing schedule', usage: 'Sensitivity analysis includes partner pricing assumptions and risks' },
    { activity: 'COM-06', consumes: 'Partner pricing schedule', usage: 'Pricing finalisation includes confirmed partner costs' },
    { activity: 'SUP-06', consumes: 'Inter-party commercial framework + negotiated terms', usage: 'Back-to-back commercial terms formalised from agreed framework' },
    { activity: 'COM-01', consumes: 'Updated should-cost model', usage: 'Should-cost model updated with confirmed partner pricing (feedback loop)' }
  ]
}
```

---

---

## COM-04 — Commercial Model & Payment Mechanisms

```javascript
{
  id: 'COM-04',
  name: 'Commercial model & payment mechanisms',
  workstream: 'COM',
  phase: 'DEV',
  role: 'Commercial Lead',
  output: 'Commercial model document',
  dependencies: ['SOL-04', 'LEG-02'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires commercial structuring expertise
  // Note: this is distinct from COM-01 (what it costs) and COM-02 (what we charge).
  // COM-04 answers: "what is the commercial structure of the contract?"
  // — how we get paid, how risk is allocated financially, how the payment mechanism works.
  //
  // In government services contracts, the payment mechanism is often complex:
  // fixed price, unitary charge, payment by results, milestone, outcome-based, or hybrid.
  // Service credits, gain share, indexation, benchmarking, parent company guarantees.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'What is being delivered — the commercial model must align to service structure' },
    { from: 'SOL-08.3.2', artifact: 'Innovation value sharing and investment framework', note: 'How productivity gains from AI/automation are shared contractually' },
    { from: 'LEG-02', artifact: 'Risk allocation matrix', note: 'How risk is distributed — informs financial risk allocation in the commercial model' },
    { from: 'COM-01', artifact: 'Should-cost model', note: 'Cost base the commercial model must cover' },
    { from: 'SAL-06.1.2', artifact: 'ITT documentation analysis summary', note: 'Payment mechanism and SLA regime from initial analysis' },
    { external: true, artifact: 'ITT documentation — payment mechanism, pricing schedule structure, service credit regime, indexation provisions, financial standing requirements' },
    { external: true, artifact: 'Contract documentation — commercial terms, financial schedules, gain share provisions, benchmarking clauses' },
    { external: true, artifact: 'Corporate commercial policies — acceptable risk thresholds, guarantee limits, margin floors' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'COM-04.1',
      name: 'Payment Mechanism & Pricing Structure Design',
      description: 'Design how we get paid and how the price is structured — the commercial architecture of the contract',

      tasks: [
        {
          id: 'COM-04.1.1',
          name: 'Design the payment mechanism — how we get paid: fixed price, cost-plus, unitary charge, milestone payments, outcome-based, payment by results, or hybrid',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Legal', i: 'Delivery Director' },
          inputs: [
            { from: 'SOL-04', artifact: 'Service delivery model' },
            { external: true, artifact: 'ITT documentation — payment mechanism, pricing schedule structure' },
            { external: true, artifact: 'Contract documentation — commercial terms, financial schedules' }
          ],
          outputs: [
            {
              name: 'Payment mechanism design',
              format: 'Structured commercial design',
              quality: [
                'Payment mechanism defined — how revenue is earned and invoiced (fixed, variable, milestone, outcome-based, or hybrid)',
                'Payment profile modelled — when cash flows, payment terms, invoicing frequency',
                'Mechanism aligned to service delivery structure — payment units map to what we actually deliver',
                'Client affordability considered — does the payment profile work for the client\'s budget cycle?',
                'Cash flow implications assessed — is the payment mechanism viable for our working capital position?'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'COM-04.1.2',
          name: 'Design the pricing structure — how the price is presented: annual charge, rate card, unit pricing, blended rates, or combination aligned to ITT pricing schedules',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Bid Manager', i: 'Solution Architect' },
          inputs: [
            { from: 'COM-04.1.1', artifact: 'Payment mechanism design' },
            { from: 'COM-01', artifact: 'Should-cost model' },
            { external: true, artifact: 'ITT documentation — pricing schedule structure, required format' }
          ],
          outputs: [
            {
              name: 'Pricing structure design',
              format: 'Structured pricing framework',
              quality: [
                'Pricing structure aligned to ITT pricing schedule format — not our preferred format but the client\'s required format',
                'Cost model mapped to pricing structure — every cost element has a home in the pricing schedules',
                'Pricing transparency calibrated — how much cost detail is visible to the client (open book, partially visible, or closed)',
                'Rate card structure designed where applicable — day rates, unit rates, volume tiers'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-04.1.3',
          name: 'Design indexation and benchmarking provisions — how prices change over the contract term, and how the client verifies value for money',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Legal', i: 'Delivery Director' },
          inputs: [
            { from: 'COM-04.1.1', artifact: 'Payment mechanism design' },
            { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model', note: 'Year-on-year cost reduction changes the indexation calculus' },
            { external: true, artifact: 'Contract documentation — indexation provisions, benchmarking clauses' }
          ],
          outputs: [
            {
              name: 'Indexation and benchmarking framework',
              format: 'Structured commercial framework',
              quality: [
                'Indexation mechanism defined — which index (CPI, RPI, AWE, bespoke), applied to which cost elements, at what frequency',
                'Interaction with innovation productivity curve modelled — if costs reduce through AI/automation, does indexation apply on top or net?',
                'Benchmarking provisions addressed — if the contract includes periodic benchmarking, how does our pricing accommodate it?',
                'Annual price review mechanism designed if applicable — what triggers a review, what can change, what is locked'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'COM-04.2',
      name: 'Financial Risk & Commercial Terms',
      description: 'Design the financial risk allocation, service credit regime, innovation value sharing, and validate the complete commercial model',

      tasks: [
        {
          id: 'COM-04.2.1',
          name: 'Design service credit and deduction regime — how underperformance is penalised financially, our exposure, and earn-back mechanisms',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Legal / Delivery Director', i: 'Finance' },
          inputs: [
            { from: 'LEG-02', artifact: 'Risk allocation matrix' },
            { from: 'SOL-04.2.1', artifact: 'SLA/KPI-to-delivery commitment matrix' },
            { external: true, artifact: 'Contract documentation — service credit regime, deduction mechanisms' }
          ],
          outputs: [
            {
              name: 'Service credit and deduction analysis',
              format: 'Structured financial risk assessment',
              quality: [
                'Service credit regime understood — which KPIs trigger credits, at what thresholds, at what financial value',
                'Maximum monthly and annual exposure quantified — what is the worst-case service credit deduction?',
                'Earn-back mechanisms identified — can we recover credits through sustained good performance?',
                'Financial risk mapped to delivery model — which service lines carry the highest credit exposure?',
                'Mitigation approach defined — how we manage delivery to avoid credit exposure'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-04.2.2',
          name: 'Incorporate innovation value sharing mechanism — gain share, reinvestment commitments, annual price reduction trajectory aligned to SOL-08 framework',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Solution Architect / Legal', i: 'Finance' },
          inputs: [
            { from: 'SOL-08.3.2', artifact: 'Innovation value sharing and investment framework' },
            { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model' },
            { from: 'COM-04.1.1', artifact: 'Payment mechanism design' }
          ],
          outputs: [
            {
              name: 'Innovation commercial provisions',
              format: 'Structured commercial terms',
              quality: [
                'Gain share mechanism contractualised — how savings from innovation are split between client and supplier',
                'Annual price reduction trajectory incorporated if applicable — scheduled reductions reflecting productivity gains',
                'Innovation investment commitment defined — how much we invest, from what source, with what governance',
                'Innovation milestones linked to commercial triggers — what happens if innovation is not delivered as planned?',
                'Mechanism is sustainable — supplier margin is protected while client receives progressive benefit'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-04.2.3',
          name: 'Validate commercial model — coherent with cost model, legally viable, aligned to ITT requirements, commercially sustainable',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Legal / Solution Architect', i: 'Bid Manager' },
          inputs: [
            { from: 'COM-04.1.1', artifact: 'Payment mechanism design' },
            { from: 'COM-04.1.2', artifact: 'Pricing structure design' },
            { from: 'COM-04.1.3', artifact: 'Indexation and benchmarking framework' },
            { from: 'COM-04.2.1', artifact: 'Service credit and deduction analysis' },
            { from: 'COM-04.2.2', artifact: 'Innovation commercial provisions' }
          ],
          outputs: [
            {
              name: 'Commercial model document (validated — activity primary output)',
              format: 'Comprehensive commercial model document',
              quality: [
                'Payment mechanism, pricing structure, indexation, service credits, and innovation provisions consolidated',
                'Commercial model coherent with should-cost model (COM-01) — costs flow into the pricing structure correctly',
                'Legally viable — LEG-02 risk allocation reflected, no unacceptable commercial risk',
                'Aligned to ITT requirements — pricing schedule format, commercial terms, financial standing requirements met',
                'Commercially sustainable — margin protected, cash flow viable, risk exposure quantified and manageable',
                'Ready for executive review at pricing governance gate (GOV-03)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Commercial model document',
      format: 'Comprehensive commercial model document',
      quality: [
        'Payment mechanism designed — how we get paid, cash flow modelled',
        'Pricing structure designed — aligned to ITT pricing schedule format',
        'Indexation and benchmarking provisions designed',
        'Service credit exposure quantified with earn-back and mitigation',
        'Innovation gain share and price reduction provisions incorporated',
        'Validated as coherent, legally viable, ITT-aligned, and commercially sustainable'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'COM-05', consumes: 'Commercial model document', usage: 'Sensitivity analysis tests commercial assumptions — service credit exposure, indexation, gain share' },
    { activity: 'COM-06', consumes: 'Commercial model document', usage: 'Pricing finalisation integrates commercial model with cost model and price-to-win' },
    { activity: 'SUP-06', consumes: 'Commercial model document', usage: 'Back-to-back terms flow down the commercial model to partners' },
    { activity: 'GOV-03', consumes: 'Commercial model document', usage: 'Pricing governance review examines the commercial structure and risk exposure' },
    { activity: 'PRD-04', consumes: 'Commercial model document', usage: 'Pricing response documents present the commercial model to the client' }
  ]
}
```

---

---

## COM-05 — Margin Structure & Sensitivity Analysis

```javascript
{
  id: 'COM-05',
  name: 'Margin structure & sensitivity analysis',
  workstream: 'COM',
  phase: 'DEV',
  role: 'Commercial Lead',
  output: 'Margin model with sensitivities',
  dependencies: ['COM-01', 'COM-03'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires financial modelling expertise
  // Note: this is standard financial stress testing — testing assumptions and risks to
  // identify both OPPORTUNITIES (upside) and THREATS (downside), and how each could
  // impact the overall revenue and cost structure and therefore delivered margin.
  //
  // The executive needs to see the full range: downside risk, base case, and upside
  // opportunity. If things go better than assumed, what does that look like? If things
  // go worse, what's the exposure? This is the decision paper that determines what
  // margin the organisation is willing to accept.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'COM-01', artifact: 'Should-cost model', note: 'The cost base to apply margin to' },
    { from: 'COM-01.2.1', artifact: 'Contract-term cost model', note: 'Year-on-year cost profile' },
    { from: 'COM-01.2.2', artifact: 'Cost assumptions register', note: 'Each assumption becomes a sensitivity variable' },
    { from: 'COM-02', artifact: 'Price-to-win assessment', note: 'The price envelope — margin modelled at each price point' },
    { from: 'COM-03', artifact: 'Partner pricing schedule', note: 'Partner costs and associated risks' },
    { from: 'COM-04', artifact: 'Commercial model document', note: 'Payment mechanism, service credits, gain share — all create financial variability' },
    { from: 'COM-04.2.1', artifact: 'Service credit and deduction analysis', note: 'Downside exposure from underperformance' },
    { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model', note: 'Upside if innovation accelerates, downside if it delays' },
    { from: 'SOL-12', artifact: 'Solution risk register', note: 'Solution risks with financial implications' },
    { external: true, artifact: 'Corporate financial policies — minimum margin thresholds, risk appetite, contingency requirements' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'COM-05.1',
      name: 'Sensitivity & Stress Testing',
      description: 'Standard financial stress testing — test every key assumption for both upside opportunity and downside risk, and model commercial scenarios. This comes first because the sensitivities inform which price points and margin positions are viable.',

      tasks: [
        {
          id: 'COM-05.1.1',
          name: 'Conduct sensitivity analysis on key cost assumptions — test each variable for upside (better than assumed) and downside (worse than assumed) impact on margin',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Solution Architect', i: 'Delivery Director' },
          inputs: [
            { from: 'COM-01.2.2', artifact: 'Cost assumptions register' },
            { from: 'COM-01.2.1', artifact: 'Contract-term cost model' }
          ],
          outputs: [
            {
              name: 'Cost assumption sensitivity analysis',
              format: 'Sensitivity matrix with tornado charts',
              quality: [
                'Each key assumption tested independently — what happens if it is X% better or worse than base case?',
                'Variables tested include: attrition, utilisation, volume, inflation, wage growth, recruitment cost, technology cost, partner cost variance',
                'Upside opportunities identified — which assumptions, if they go better, create the most margin improvement?',
                'Downside risks identified — which assumptions, if they go worse, create the most margin erosion?',
                'Top 5 sensitivity drivers ranked — the variables that matter most to the financial outcome',
                'Tornado chart or equivalent presentation — visual ranking of sensitivities for executive communication'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'COM-05.1.2',
          name: 'Stress-test commercial model scenarios — maximum service credit exposure, gain share under/overperformance, volume variance, indexation deviation',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Legal', i: 'Solution Architect' },
          inputs: [
            { from: 'COM-04.2.1', artifact: 'Service credit and deduction analysis' },
            { from: 'COM-04.2.2', artifact: 'Innovation commercial provisions' },
            { from: 'COM-01.2.1', artifact: 'Contract-term cost model' },
            { from: 'SOL-12', artifact: 'Solution risk register' }
          ],
          outputs: [
            {
              name: 'Commercial scenario stress test',
              format: 'Scenario-based financial impact analysis',
              quality: [
                'Downside scenarios modelled: maximum service credit deductions, innovation failure, volume shortfall, adverse indexation, partner pricing overrun',
                'Upside scenarios modelled: innovation acceleration, volume growth, performance bonus, lower attrition, favourable indexation',
                'Combined worst case modelled — what if multiple downside scenarios hit simultaneously?',
                'Combined best case modelled — what does the upside opportunity look like?',
                'Break-even analysis — at what point do downside scenarios push margin below acceptable threshold?'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'COM-05.2',
      name: 'Margin Modelling & Executive Decision Paper',
      description: 'Model the margin at multiple price points informed by the stress test results, produce the contract-term P&L, and present the executive decision paper',

      tasks: [
        {
          id: 'COM-05.2.1',
          name: 'Model margin structure at multiple price points across the price-to-win envelope — informed by sensitivity and stress test results',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Partner' },
          inputs: [
            { from: 'COM-01', artifact: 'Should-cost model' },
            { from: 'COM-02', artifact: 'Price-to-win assessment' },
            { from: 'COM-03', artifact: 'Partner pricing schedule' },
            { from: 'COM-05.1.1', artifact: 'Cost assumption sensitivity analysis' },
            { from: 'COM-05.1.2', artifact: 'Commercial scenario stress test' }
          ],
          outputs: [
            {
              name: 'Margin model at multiple price points',
              format: 'Financial model with scenario comparison',
              quality: [
                'Margin calculated at floor, midpoint, and ceiling price points from COM-02 envelope',
                'Margin expressed as absolute value and percentage — total contract and per annum',
                'Sensitivity impact overlaid — at each price point, what is the margin range under best/base/worst case?',
                'Corporate minimum margin threshold tested — which price points meet the floor under stress?',
                'Partner margin and prime margin distinguished — where margin sits in the consortium'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-05.2.2',
          name: 'Model the P&L profile across the contract term — margin trajectory year by year as innovation reduces costs, indexation adjusts prices, and volumes evolve',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Solution Architect', i: 'Delivery Director' },
          inputs: [
            { from: 'COM-05.2.1', artifact: 'Margin model at multiple price points' },
            { from: 'COM-01.2.1', artifact: 'Contract-term cost model' },
            { from: 'SOL-08.3.1', artifact: 'Innovation productivity curve model' },
            { from: 'COM-04', artifact: 'Commercial model document' }
          ],
          outputs: [
            {
              name: 'Contract-term P&L profile',
              format: 'Year-on-year P&L model',
              quality: [
                'Revenue, cost, and margin profiled year by year across full contract term',
                'Innovation productivity gains reflected — costs reduce, margin may improve if price holds or reduces slower',
                'Indexation impact modelled — how price and cost indexation interact over time',
                'Transition year(s) modelled separately — typically lower margin during mobilisation',
                'Cash flow profile included — when margin is earned, working capital implications'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'COM-05.2.3',
          name: 'Produce risk-adjusted margin view and validate — the executive decision paper presenting base case, upside, downside, and recommendation',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Senior Responsible Executive' },
          inputs: [
            { from: 'COM-05.2.1', artifact: 'Margin model at multiple price points' },
            { from: 'COM-05.2.2', artifact: 'Contract-term P&L profile' },
            { from: 'COM-05.1.1', artifact: 'Cost assumption sensitivity analysis' },
            { from: 'COM-05.1.2', artifact: 'Commercial scenario stress test' },
            { external: true, artifact: 'Corporate financial policies — minimum margin thresholds, risk appetite, contingency requirements' }
          ],
          outputs: [
            {
              name: 'Margin model with sensitivities (validated — activity primary output)',
              format: 'Executive financial decision paper',
              quality: [
                'Base case margin presented at recommended price point — absolute and percentage',
                'Upside opportunity quantified — what margin looks like if things go better than assumed',
                'Downside risk quantified — what margin looks like if things go worse, and at what point it becomes unacceptable',
                'Top sensitivity drivers clearly communicated — the 5 variables executives should focus on',
                'Risk-adjusted margin view presented — expected margin accounting for probability-weighted scenarios',
                'Recommendation stated — proposed margin and price position with rationale',
                'Corporate margin threshold tested — does the recommendation meet the organisation\'s financial requirements?',
                'Paper is executive-ready — clear, visual, defensible, supports the pricing governance decision'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Margin model with sensitivities',
      format: 'Executive financial decision paper',
      quality: [
        'Margin modelled at multiple price points across the price-to-win envelope',
        'Contract-term P&L profiled year by year — revenue, cost, margin trajectory',
        'Key cost assumptions sensitivity-tested — upside opportunities and downside risks ranked',
        'Commercial scenarios stress-tested — service credits, gain share, volume, indexation',
        'Risk-adjusted margin view produced — probability-weighted expected outcome',
        'Executive recommendation stated — proposed margin and price with rationale',
        'Paper is executive-ready for pricing governance decision'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'COM-06', consumes: 'Margin model with sensitivities', usage: 'Pricing finalisation uses the validated margin and sensitivity analysis to set the final price' },
    { activity: 'GOV-03', consumes: 'Margin model with sensitivities', usage: 'Pricing governance review examines margin, sensitivities, and risk-adjusted view' },
    { activity: 'COM-07', consumes: 'Margin model with sensitivities', usage: 'Commercial risk register incorporates financial risks from sensitivity analysis' }
  ]
}
```

---

---

## COM-06 — Pricing Model Finalisation

```javascript
{
  id: 'COM-06',
  name: 'Pricing model finalisation',
  workstream: 'COM',
  phase: 'DEV',
  role: 'Commercial Lead',
  output: 'Pricing model (locked & assured)',
  dependencies: ['COM-01', 'COM-02', 'COM-03', 'COM-04', 'COM-05', 'DEL-01'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires commercial lead to bring everything together
  // Note: this is the lock activity for the commercial workstream — same pattern as
  // SOL-11 for solution. Everything converges here: cost model, price-to-win, partner
  // pricing, commercial model, margin analysis, risk contingency.
  //
  // The output is the final price that goes into the bid — the actual numbers the
  // client sees. Not a strategy paper but the submitted pricing schedules.
  //
  // Distinct from GOV-03 (Pricing & Risk Review) which is the governance gate that
  // approves the price. COM-06 assembles and locks; GOV-03 assures and approves.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'COM-01', artifact: 'Should-cost model', note: 'The validated cost base' },
    { from: 'COM-02', artifact: 'Price-to-win assessment', note: 'The validated price envelope and recommended position' },
    { from: 'COM-03', artifact: 'Partner pricing schedule', note: 'Confirmed partner costs' },
    { from: 'COM-04', artifact: 'Commercial model document', note: 'Payment mechanism, pricing structure, service credits, innovation provisions' },
    { from: 'COM-05', artifact: 'Margin model with sensitivities', note: 'Executive decision paper — margin, sensitivities, recommended price position' },
    { from: 'COM-07', artifact: 'Commercial risk register', note: 'Risk-priced contingency to include in the price' },
    { from: 'DEL-01', artifact: 'Implementation plan', note: 'Implementation and delivery costs that feed pricing' },
    { external: true, artifact: 'ITT documentation — pricing schedule templates, submission format, required pricing breakdowns' },
    { external: true, artifact: 'Executive pricing guidance — approved margin and price position from COM-05 review' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'COM-06.1',
      name: 'Pricing Assembly',
      description: 'Set the final price position and populate the pricing schedules in the format the client requires',

      tasks: [
        {
          id: 'COM-06.1.1',
          name: 'Set the final price position — land within the validated envelope based on margin analysis, sensitivity results, and executive guidance',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Senior Responsible Executive' },
          inputs: [
            { from: 'COM-02', artifact: 'Price-to-win assessment' },
            { from: 'COM-05', artifact: 'Margin model with sensitivities' },
            { external: true, artifact: 'Executive pricing guidance — approved margin and price position' }
          ],
          outputs: [
            {
              name: 'Final price position',
              format: 'Confirmed price with rationale',
              quality: [
                'Price position set within the validated COM-02 envelope — not outside the tested range',
                'Margin at this price point confirmed as acceptable — tested under COM-05 sensitivities',
                'Executive guidance incorporated — any conditions or constraints from the margin review reflected',
                'Price position rationale documented — why this point in the envelope, not just a number'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-06.1.2',
          name: 'Populate pricing schedules in the ITT-required format — translate the commercial model into the client\'s pricing tables, rate cards, and financial submissions',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Bid Manager', i: 'Solution Architect' },
          inputs: [
            { from: 'COM-06.1.1', artifact: 'Final price position' },
            { from: 'COM-01', artifact: 'Should-cost model' },
            { from: 'COM-03', artifact: 'Partner pricing schedule' },
            { from: 'COM-04', artifact: 'Commercial model document' },
            { from: 'COM-07', artifact: 'Commercial risk register', note: 'Risk contingency allocation' },
            { external: true, artifact: 'ITT documentation — pricing schedule templates, submission format' }
          ],
          outputs: [
            {
              name: 'Completed pricing schedules',
              format: 'Client-required pricing submission format',
              quality: [
                'All pricing schedules populated in the ITT-required format — no gaps or blank cells',
                'Cost model mapped correctly to pricing schedule structure — every cost element has a home',
                'Partner costs correctly allocated within the pricing schedules',
                'Risk contingency allocated appropriately — visible or embedded per commercial strategy',
                'Year-on-year pricing profile reflects innovation productivity trajectory and indexation',
                'Pricing schedules are arithmetically correct — totals reconcile, cross-references check'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'COM-06.2',
      name: 'Pricing Validation & Lock',
      description: 'Final reconciliation and lock — confirm everything adds up, sign off, and baseline for governance and submission',

      tasks: [
        {
          id: 'COM-06.2.1',
          name: 'Conduct final pricing reconciliation — confirm cost model, commercial model, partner pricing, risk contingency, and submitted price all reconcile',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance', i: 'Bid Manager' },
          inputs: [
            { from: 'COM-06.1.2', artifact: 'Completed pricing schedules' },
            { from: 'COM-01', artifact: 'Should-cost model' },
            { from: 'COM-04', artifact: 'Commercial model document' }
          ],
          outputs: [
            {
              name: 'Pricing reconciliation record',
              format: 'Structured reconciliation checklist',
              quality: [
                'Bottom-up cost model reconciles to pricing schedules — no unexplained differences',
                'Partner pricing in schedules matches confirmed partner pricing from COM-03',
                'Commercial model provisions (indexation, service credits, gain share) correctly reflected in pricing',
                'Risk contingency correctly allocated — amount and location in the pricing confirmed',
                'Margin at submitted price confirmed against COM-05 approved position',
                'Arithmetic verified — totals, cross-references, formulas all correct'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-06.2.2',
          name: 'Lock pricing model — formal sign-off, baseline for GOV-03 (Pricing & Risk Review) and PRD-04 (pricing response documents)',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Commercial Lead / Finance', i: 'Bid Team (collective)' },
          inputs: [
            { from: 'COM-06.1.2', artifact: 'Completed pricing schedules' },
            { from: 'COM-06.2.1', artifact: 'Pricing reconciliation record' }
          ],
          outputs: [
            {
              name: 'Pricing model (locked & assured — activity primary output)',
              format: 'Baselined pricing document with formal sign-off',
              quality: [
                'Pricing model formally baselined — this is the authoritative price for the bid',
                'Bid Director sign-off recorded — accountability for the price accepted',
                'Pricing schedules locked — changes after lock require formal change review',
                'Reconciliation confirmed — cost model, commercial model, and submitted price all consistent',
                'Ready for GOV-03 (Pricing & Risk Review) governance gate',
                'Ready for PRD-04 (pricing response documents) to package for submission'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Pricing model (locked & assured)',
      format: 'Baselined pricing document with completed schedules',
      quality: [
        'Final price position set within validated envelope with rationale',
        'Pricing schedules populated in ITT-required format — complete, correct, reconciled',
        'Cost model, partner pricing, commercial provisions, and risk contingency all reflected',
        'Year-on-year pricing profile reflects innovation and indexation trajectory',
        'Formally reconciled and locked with Bid Director sign-off'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'GOV-03', consumes: 'Pricing model (locked & assured)', usage: 'Pricing & Risk Review governance gate — formal approval of the submitted price' },
    { activity: 'PRD-04', consumes: 'Pricing model (locked & assured)', usage: 'Pricing response documents packaged from locked pricing schedules' },
    { activity: 'DEL-06', consumes: 'Pricing model (locked & assured)', usage: 'Risk mitigation register updated with residual commercial risk at locked price' }
  ]
}
```

---

---

## COM-07 — Commercial Risk Identification & Analysis

```javascript
{
  id: 'COM-07',
  name: 'Commercial risk identification & analysis',
  workstream: 'COM',
  phase: 'DEV',
  role: 'Commercial Lead',
  output: 'Commercial risk register',
  dependencies: ['COM-01', 'COM-04', 'LEG-02'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',               // Specialist — requires commercial risk expertise
  // Note: same pattern as SOL-12 — consolidates risks from the commercial workstream
  // into a single register. Feeds BM-13 (bid risk register) and governance gates.
  // Also feeds COM-06 — risk contingency must be priced before pricing locks.

  // ── Structured inputs ──────────────────────────────────────────────
  inputs: [
    { from: 'COM-01', artifact: 'Should-cost model', note: 'Cost assumptions that create risk' },
    { from: 'COM-01.2.2', artifact: 'Cost assumptions register', note: 'Each assumption is a potential risk' },
    { from: 'COM-02', artifact: 'Price-to-win assessment', note: 'Pricing position risk — are we too high or too low?' },
    { from: 'COM-03', artifact: 'Partner pricing schedule', note: 'Partner pricing risks — conditions, caveats, assumption gaps' },
    { from: 'COM-04', artifact: 'Commercial model document', note: 'Payment mechanism, service credit, gain share risks' },
    { from: 'COM-05', artifact: 'Margin model with sensitivities', note: 'Financial stress test results — where the risks bite hardest' },
    { from: 'LEG-02', artifact: 'Risk allocation matrix', note: 'Legal risk allocation that drives commercial risk' },
    { external: true, artifact: 'Contract documentation — liability caps, indemnities, termination provisions, force majeure' },
    { external: true, artifact: 'Corporate risk appetite and commercial policies' }
  ],

  // ── L2 sub-processes ──────────────────────────────────────────────
  subs: [
    {
      id: 'COM-07.1',
      name: 'Commercial Risk Consolidation',
      description: 'Harvest all commercial risks from upstream activities and identify additional risks not yet captured',

      tasks: [
        {
          id: 'COM-07.1.1',
          name: 'Harvest commercial risks from all COM activities — cost assumptions, pricing position, partner terms, payment mechanism, service credits, innovation commercial model',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Legal', i: 'Bid Manager' },
          inputs: [
            { from: 'COM-01.2.2', artifact: 'Cost assumptions register' },
            { from: 'COM-03', artifact: 'Partner pricing schedule' },
            { from: 'COM-04', artifact: 'Commercial model document' },
            { from: 'COM-05', artifact: 'Margin model with sensitivities' }
          ],
          outputs: [
            {
              name: 'Consolidated commercial risk register (draft)',
              format: 'Structured risk register',
              quality: [
                'All risks from COM-01 through COM-05 harvested — cost, pricing, partner, commercial model, margin risks',
                'Sensitivity analysis top drivers from COM-05 included as risks — the assumptions most likely to move the outcome',
                'Partner-specific risks captured — conditions, caveats, pricing validity, dependency risks',
                'Duplicates consolidated and categorised'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-07.1.2',
          name: 'Identify additional commercial risks not captured upstream — contract terms, foreign exchange, regulatory change, client budget, market shift, competitor pricing behaviour',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Legal / Finance', i: 'Capture Lead' },
          inputs: [
            { from: 'COM-07.1.1', artifact: 'Consolidated commercial risk register (draft)' },
            { from: 'LEG-02', artifact: 'Risk allocation matrix' },
            { from: 'COM-02', artifact: 'Price-to-win assessment' },
            { external: true, artifact: 'Contract documentation — liability caps, indemnities, termination provisions' },
            { external: true, artifact: 'Corporate risk appetite and commercial policies' }
          ],
          outputs: [
            {
              name: 'Complete commercial risk register (draft)',
              format: 'Structured risk register (enriched)',
              quality: [
                'Contract-driven risks captured — liability exposure, indemnity obligations, termination costs',
                'Market and competitive risks captured — what if the market shifts or competitors behave unexpectedly?',
                'Regulatory and policy risks captured — Procurement Act changes, spending review impacts, policy shifts',
                'Client budget risks captured — what if the client\'s funding changes mid-contract?',
                'Foreign exchange risks captured where applicable — partner costs in other currencies'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'COM-07.2',
      name: 'Risk Assessment & Mitigation',
      description: 'Assess, prioritise, mitigate, and quantify contingency for all commercial risks',

      tasks: [
        {
          id: 'COM-07.2.1',
          name: 'Assess and prioritise commercial risks — likelihood, impact, financial exposure, and assign risk owner',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Legal', i: 'Delivery Director' },
          inputs: [
            { from: 'COM-07.1.2', artifact: 'Complete commercial risk register (draft)' }
          ],
          outputs: [
            {
              name: 'Prioritised commercial risk register',
              format: 'Structured risk register with assessments',
              quality: [
                'Every risk assessed for likelihood, impact, and financial exposure (£ value)',
                'Risk priority derived — critical, significant, moderate, low',
                'Risk owner assigned for every risk — named role',
                'Top commercial risks identified — the risks that could materially affect margin or contract viability'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-07.2.2',
          name: 'Develop mitigation strategies and quantify contingency requirements — what risk premium or contingency should be priced into the bid?',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Legal', i: 'Partner' },
          inputs: [
            { from: 'COM-07.2.1', artifact: 'Prioritised commercial risk register' }
          ],
          outputs: [
            {
              name: 'Mitigated commercial risk register with contingency',
              format: 'Structured risk register with mitigations and contingency',
              quality: [
                'Every high and significant risk has a mitigation strategy — preventive and contingent actions',
                'Contingency requirement quantified — how much risk premium should be included in the price?',
                'Contingency allocation recommended — explicit line item vs embedded in margin vs absorbed',
                'Residual risk after mitigation assessed — what exposure remains?',
                'Unmitigatable risks flagged for executive acceptance — risks the organisation must knowingly take'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'COM-07.2.3',
          name: 'Validate commercial risk register — complete, contingency quantified, ready for COM-06 pricing and governance gates',
          raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'COM-07.2.2', artifact: 'Mitigated commercial risk register with contingency' }
          ],
          outputs: [
            {
              name: 'Commercial risk register (validated — activity primary output)',
              format: 'Authoritative commercial risk register',
              quality: [
                'All commercial dimensions covered — cost, pricing, partner, contractual, market, regulatory',
                'Top risks understood and accepted by Bid Director',
                'Contingency quantified and recommended for COM-06 pricing',
                'Mitigations are credible and resourced',
                'Register ready for BM-13 consolidation and GOV-03 governance review'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  // ── Activity-level output ─────────────────────────────────────────
  outputs: [
    {
      name: 'Commercial risk register',
      format: 'Authoritative commercial risk register',
      quality: [
        'All commercial risks consolidated from upstream COM activities',
        'Additional contract, market, regulatory, and client budget risks identified',
        'Every risk assessed for likelihood, impact, and financial exposure',
        'Mitigation strategies defined with contingency quantified',
        'Residual risk position accepted by Bid Director',
        'Contingency recommendation ready for COM-06 pricing'
      ]
    }
  ],

  // ── Downstream consumers ──────────────────────────────────────────
  consumers: [
    { activity: 'COM-06', consumes: 'Commercial risk register', usage: 'Pricing finalisation includes risk contingency in the submitted price' },
    { activity: 'BM-13', consumes: 'Commercial risk register', usage: 'Bid risk register consolidates commercial risks with solution, legal, and programme risks' },
    { activity: 'GOV-03', consumes: 'Commercial risk register', usage: 'Pricing governance review examines commercial risk position' },
    { activity: 'DEL-06', consumes: 'Commercial risk register', usage: 'Mitigated risk register incorporates commercial risks for delivery planning' }
  ]
}
```

---

---

## LEG-01 — Contract Review & Markup

```javascript
{
  id: 'LEG-01',
  name: 'Contract review & markup',
  workstream: 'LEG',
  phase: 'DEV',
  role: 'Legal Lead',
  output: 'Contract markup with positions log',
  dependencies: [],                        // Day-1 start
  effortDays: 8,
  teamSize: 1,
  parallelisationType: 'S',

  inputs: [
    { from: 'SAL-06.1.2', artifact: 'ITT documentation analysis summary', note: 'Contract red lines already flagged at strategic level' },
    { from: 'SOL-01', artifact: 'Requirements interpretation document', note: 'Contractual requirements extracted during SOL-01' },
    { external: true, artifact: 'ITT contract documentation — T&Cs, schedules, annexes, framework call-off terms' },
    { external: true, artifact: 'Corporate legal policies — standard positions, risk appetite, authority limits' }
  ],

  subs: [
    {
      id: 'LEG-01.1',
      name: 'Contract Analysis',
      description: 'Systematically review the contract documentation to identify all obligations, liabilities, and risk areas',

      tasks: [
        {
          id: 'LEG-01.1.1',
          name: 'Review all contract documents — T&Cs, schedules, annexes — identify obligations, liabilities, and non-standard provisions',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Delivery Director' },
          inputs: [
            { external: true, artifact: 'ITT contract documentation — T&Cs, schedules, annexes, framework call-off terms' },
            { external: true, artifact: 'Corporate legal policies — standard positions, risk appetite' }
          ],
          outputs: [
            {
              name: 'Contract analysis register',
              format: 'Clause-by-clause structured analysis',
              quality: [
                'Every material clause reviewed and categorised — standard, non-standard, onerous, unacceptable',
                'Obligations identified and mapped — what we are committing to do',
                'Liabilities identified and quantified where possible — caps, uncapped exposure, indemnities',
                'Non-standard provisions flagged with risk commentary'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'LEG-01.1.2',
          name: 'Identify red lines and risk areas — terms we cannot accept, terms that need amendment, terms that create unacceptable exposure',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead / Finance', i: 'Senior Responsible Executive' },
          inputs: [
            { from: 'LEG-01.1.1', artifact: 'Contract analysis register' },
            { external: true, artifact: 'Corporate legal policies — authority limits, non-negotiable positions' }
          ],
          outputs: [
            {
              name: 'Red lines and risk register',
              format: 'Prioritised risk register',
              quality: [
                'Red lines identified — terms that are non-negotiable for us (must change or cannot bid)',
                'Amber issues identified — terms we want to change but can accept with mitigation',
                'Financial exposure quantified per risk area — what is the worst case?',
                'Each issue linked to the specific contract clause for traceability'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'LEG-01.2',
      name: 'Contract Response',
      description: 'Prepare the contract markup and negotiation strategy',

      tasks: [
        {
          id: 'LEG-01.2.1',
          name: 'Prepare contract markup and redline — proposed amendments with rationale for each change',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'LEG-01.1.2', artifact: 'Red lines and risk register' }
          ],
          outputs: [
            {
              name: 'Contract markup / redline',
              format: 'Tracked-changes contract document',
              quality: [
                'Every proposed amendment has a rationale — not just tracked changes but why',
                'Amendments are proportionate — not a blanket rewrite but targeted risk reduction',
                'Language is legally precise and commercially sensible',
                'Markup is submission-ready — format matches client expectations'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'LEG-01.2.2',
          name: 'Develop negotiation strategy and positions log — fallback positions, must-haves vs nice-to-haves, feeds competitive dialogue (BM-09)',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Senior Responsible Executive' },
          inputs: [
            { from: 'LEG-01.2.1', artifact: 'Contract markup / redline' },
            { from: 'LEG-01.1.2', artifact: 'Red lines and risk register' }
          ],
          outputs: [
            {
              name: 'Contract markup with positions log (activity primary output)',
              format: 'Markup document with negotiation positions',
              quality: [
                'Each amendment has a preferred position and fallback position',
                'Must-haves distinguished from nice-to-haves — what we will walk away from vs what we will concede',
                'Negotiation strategy documented — sequencing, trade-offs, package deals',
                'Positions log is usable by the bid team during competitive dialogue or post-submission negotiation'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Contract markup with positions log',
      format: 'Markup document with negotiation positions',
      quality: [
        'All contract documents reviewed clause by clause',
        'Red lines and risk areas identified with financial exposure',
        'Contract markup prepared with rationale per amendment',
        'Negotiation positions log with preferred and fallback positions'
      ]
    }
  ],

  consumers: [
    { activity: 'LEG-02', consumes: 'Contract markup with positions log', usage: 'Risk allocation analysis builds on contract risk areas' },
    { activity: 'COM-04', consumes: 'Contract markup with positions log', usage: 'Commercial model incorporates contract terms — payment mechanism, service credits, liabilities' },
    { activity: 'LEG-06', consumes: 'Contract markup with positions log', usage: 'Subcontractor terms flow down from prime contract positions' },
    { activity: 'BM-09', consumes: 'Positions log', usage: 'Competitive dialogue preparation uses negotiation strategy' }
  ]
}
```

---

## LEG-02 — Risk Allocation Analysis

```javascript
{
  id: 'LEG-02',
  name: 'Risk allocation analysis',
  workstream: 'LEG',
  phase: 'DEV',
  role: 'Legal Lead',
  output: 'Risk allocation matrix',
  dependencies: ['LEG-01'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',

  inputs: [
    { from: 'LEG-01', artifact: 'Contract markup with positions log' },
    { from: 'SOL-03', artifact: 'Target operating model', note: 'Solution structure determines where delivery risk sits' },
    { from: 'SOL-07', artifact: 'Transition plan', note: 'Transition risk allocation' },
    { external: true, artifact: 'Corporate risk appetite and risk allocation policies' }
  ],

  subs: [
    {
      id: 'LEG-02.1',
      name: 'Risk Identification & Allocation',
      description: 'Map how risk is allocated across the contract and assess acceptability',

      tasks: [
        {
          id: 'LEG-02.1.1',
          name: 'Map risk allocation across the contract — who bears what risk (client, supplier, shared) for each category: delivery, financial, transition, TUPE, technology, force majeure',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead / Delivery Director', i: 'Finance' },
          inputs: [
            { from: 'LEG-01', artifact: 'Contract markup with positions log' },
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SOL-07', artifact: 'Transition plan' }
          ],
          outputs: [
            {
              name: 'Risk allocation map',
              format: 'Matrix (risk category × allocation)',
              quality: [
                'Every material risk category mapped — delivery, financial, transition, TUPE, technology, regulatory, force majeure',
                'Allocation documented per risk — client bears, supplier bears, shared, or unclear',
                'Where allocation is unclear or disputed, the contract clause is referenced',
                'Comparison to standard market allocation noted — where is this contract unusually aggressive?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'LEG-02.1.2',
          name: 'Assess acceptability of risk allocation against corporate risk appetite — where are we taking too much risk?',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Finance / Commercial Lead', i: 'Senior Responsible Executive' },
          inputs: [
            { from: 'LEG-02.1.1', artifact: 'Risk allocation map' },
            { external: true, artifact: 'Corporate risk appetite and risk allocation policies' }
          ],
          outputs: [
            {
              name: 'Risk allocation acceptability assessment',
              format: 'Structured assessment',
              quality: [
                'Each risk allocation assessed against corporate risk appetite — acceptable, tolerable, unacceptable',
                'Financial exposure quantified for unacceptable and tolerable allocations',
                'Cumulative risk exposure assessed — total worst-case across all categories'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'LEG-02.1.3',
          name: 'Develop risk mitigation positions and recommend contract amendments — feeds LEG-01 markup and COM-04 commercial model',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Delivery Director' },
          inputs: [
            { from: 'LEG-02.1.2', artifact: 'Risk allocation acceptability assessment' }
          ],
          outputs: [
            {
              name: 'Risk allocation matrix (validated — activity primary output)',
              format: 'Comprehensive risk allocation document',
              quality: [
                'Risk allocation matrix complete with acceptability assessment',
                'Mitigation positions developed for unacceptable/tolerable allocations — contract amendment, commercial provision, or operational mitigation',
                'Recommendations fed back to LEG-01 (additional markup) and COM-04 (risk pricing)',
                'Residual risk position documented — what risk we accept at this allocation'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Risk allocation matrix',
      format: 'Comprehensive risk allocation document',
      quality: [
        'All material risks mapped by category with allocation (client/supplier/shared)',
        'Acceptability assessed against corporate risk appetite',
        'Mitigation positions developed for unacceptable allocations',
        'Residual risk position documented'
      ]
    }
  ],

  consumers: [
    { activity: 'COM-04', consumes: 'Risk allocation matrix', usage: 'Commercial model incorporates financial risk allocation' },
    { activity: 'COM-07', consumes: 'Risk allocation matrix', usage: 'Commercial risk register uses legal risk allocation as input' },
    { activity: 'GOV-03', consumes: 'Risk allocation matrix', usage: 'Pricing governance review examines contractual risk position' }
  ]
}
```

---

## LEG-03 — Insurance & Liability Review

```javascript
{
  id: 'LEG-03',
  name: 'Insurance & liability review',
  workstream: 'LEG',
  phase: 'DEV',
  role: 'Legal Lead',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: Minor — insurance requirements typically lighter (PI dominant,
  //   no PL/EL for service delivery). Same process, reduced scope.
  output: 'Insurance requirements assessment',
  dependencies: [],                        // Day-1 start
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',

  inputs: [
    { external: true, artifact: 'ITT contract documentation — insurance requirements, liability provisions, indemnity clauses' },
    { external: true, artifact: 'Current corporate insurance portfolio — PI, PL, EL, cyber, product liability coverage and limits' },
    { from: 'LEG-01', artifact: 'Contract markup with positions log', note: 'Soft dependency — can start in parallel, refines when LEG-01 identifies liability provisions' }
  ],

  subs: [
    {
      id: 'LEG-03.1',
      name: 'Insurance Requirements Analysis',
      description: 'Identify what insurance the contract requires, assess gaps against current coverage, and quantify cost',

      tasks: [
        {
          id: 'LEG-03.1.1',
          name: 'Identify insurance requirements from the contract — PI, PL, EL, cyber, product liability minimum levels and specific provisions',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Insurance / Risk Manager', i: 'Commercial Lead' },
          inputs: [
            { external: true, artifact: 'ITT contract documentation — insurance requirements, liability provisions' }
          ],
          outputs: [
            {
              name: 'Insurance requirements register',
              format: 'Structured requirements list',
              quality: [
                'All insurance requirements extracted from contract — type, minimum level, specific provisions',
                'Duration and maintenance period requirements noted — how long must coverage continue post-contract?',
                'Any unusual or non-standard insurance requirements flagged'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'LEG-03.1.2',
          name: 'Assess current insurance coverage against requirements — gaps, additional premiums, exclusions that need addressing',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Insurance / Risk Manager / Finance', i: 'Commercial Lead' },
          inputs: [
            { from: 'LEG-03.1.1', artifact: 'Insurance requirements register' },
            { external: true, artifact: 'Current corporate insurance portfolio' }
          ],
          outputs: [
            {
              name: 'Insurance gap assessment',
              format: 'Gap analysis',
              quality: [
                'Each requirement matched against current coverage — compliant, partially covered, gap',
                'Additional cover or increased limits required identified with estimated premium impact',
                'Exclusions in current policies that conflict with contract requirements flagged',
                'Timeline for procuring additional cover assessed — can we be compliant by contract start?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'LEG-03.1.3',
          name: 'Quantify insurance cost and confirm compliance — additional premium cost feeds COM-01, compliance position confirmed',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Finance / Insurance', i: 'Commercial Lead' },
          inputs: [
            { from: 'LEG-03.1.2', artifact: 'Insurance gap assessment' }
          ],
          outputs: [
            {
              name: 'Insurance requirements assessment (activity primary output)',
              format: 'Compliance assessment with cost impact',
              quality: [
                'Compliance position confirmed — can we meet all insurance requirements?',
                'Additional premium cost quantified — feeds COM-01 non-workforce cost model',
                'Any non-compliance flagged with mitigation — negotiation position or alternative provision',
                'Assessment ready for governance review'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Insurance requirements assessment',
      format: 'Compliance assessment with cost impact',
      quality: [
        'All insurance requirements identified from contract',
        'Current coverage assessed against requirements — gaps identified',
        'Additional premium cost quantified',
        'Compliance position confirmed or non-compliance flagged with mitigation'
      ]
    }
  ],

  consumers: [
    { activity: 'COM-01', consumes: 'Insurance requirements assessment', usage: 'Should-cost model includes additional insurance premiums' },
    { activity: 'COM-07', consumes: 'Insurance requirements assessment', usage: 'Commercial risk register includes insurance compliance risk' }
  ]
}
```

---

## LEG-04 — TUPE Obligations Assessment

```javascript
{
  id: 'LEG-04',
  name: 'TUPE obligations assessment',
  workstream: 'LEG',
  phase: 'DEV',
  role: 'Legal Lead',
  // ARCHETYPE NOTES:
  // Technology/Digital: DEACTIVATED — no TUPE in technology delivery.
  // Consulting/Advisory: DEACTIVATED — no TUPE in consulting engagements.
  output: 'TUPE compliance assessment',
  dependencies: ['SOL-06'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',

  inputs: [
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'SOL-06 does the HR/commercial TUPE analysis — LEG-04 does the legal compliance review' },
    { from: 'SOL-06.2.1', artifact: 'TUPE analysis and schedule', note: 'Detailed TUPE register and terms assessment' },
    { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis', note: 'Restructuring plans that have TUPE legal implications' },
    { external: true, artifact: 'TUPE Regulations 2006 (as amended), relevant case law, and government guidance' },
    { external: true, artifact: 'Contract TUPE provisions — information disclosure, consultation obligations, pension requirements' }
  ],

  subs: [
    {
      id: 'LEG-04.1',
      name: 'TUPE Legal Compliance',
      description: 'Review the TUPE analysis from a legal perspective — are our plans compliant with regulations, case law, and contractual obligations?',

      tasks: [
        {
          id: 'LEG-04.1.1',
          name: 'Assess TUPE obligations from a legal perspective — regulations, case law, pension obligations (Fair Deal / New Fair Deal), consultation requirements, information rights',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'HR Lead / Commercial Lead', i: 'Delivery Director' },
          inputs: [
            { from: 'SOL-06.2.1', artifact: 'TUPE analysis and schedule' },
            { external: true, artifact: 'TUPE Regulations 2006 (as amended), relevant case law, and government guidance' },
            { external: true, artifact: 'Contract TUPE provisions' }
          ],
          outputs: [
            {
              name: 'TUPE legal obligations assessment',
              format: 'Structured legal assessment',
              quality: [
                'All TUPE regulatory obligations identified — information, consultation, terms protection, pension',
                'Pension obligations assessed under Fair Deal / New Fair Deal — employer cost and risk',
                'Consultation timeline and requirements defined — who must be consulted, when, about what',
                'Contractual TUPE provisions cross-referenced with regulatory requirements — any conflicts?'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'LEG-04.1.2',
          name: 'Review SOL-06 staffing plans for legal compliance — are the restructuring, redeployment, and gap resolution plans legally sound under TUPE?',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'HR Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis' },
            { from: 'LEG-04.1.1', artifact: 'TUPE legal obligations assessment' }
          ],
          outputs: [
            {
              name: 'Staffing plan legal compliance review',
              format: 'Legal review with recommendations',
              quality: [
                'Proposed restructuring assessed for TUPE compliance — can we make these changes post-transfer?',
                'Redundancy provisions assessed — if role displacement is planned, is the ETO reason defensible?',
                'Terms harmonisation approach assessed — what can and cannot be changed and when',
                'Legal risks quantified — tribunal exposure, compensation costs if challenged'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'LEG-04.1.3',
          name: 'Identify TUPE legal risks and develop mitigation advice — feeds SOL-12 and COM-07',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'HR Lead / Commercial Lead', i: 'Finance' },
          inputs: [
            { from: 'LEG-04.1.1', artifact: 'TUPE legal obligations assessment' },
            { from: 'LEG-04.1.2', artifact: 'Staffing plan legal compliance review' }
          ],
          outputs: [
            {
              name: 'TUPE compliance assessment (activity primary output)',
              format: 'Comprehensive TUPE legal assessment',
              quality: [
                'TUPE legal obligations fully documented',
                'Staffing plans confirmed as legally compliant or amendments recommended',
                'Legal risks identified, quantified, and mitigation advice provided',
                'Pension obligations confirmed with cost implications for COM-01',
                'Assessment ready for governance review'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'TUPE compliance assessment',
      format: 'Comprehensive TUPE legal assessment',
      quality: [
        'All TUPE regulatory and contractual obligations documented',
        'Pension obligations assessed under Fair Deal / New Fair Deal',
        'Staffing plans reviewed for legal compliance',
        'Legal risks quantified with mitigation advice',
        'Compliance confirmed or amendments recommended'
      ]
    }
  ],

  consumers: [
    { activity: 'SOL-12', consumes: 'TUPE compliance assessment', usage: 'Solution risk register includes TUPE legal risks' },
    { activity: 'COM-07', consumes: 'TUPE compliance assessment', usage: 'Commercial risk register includes TUPE financial exposure' },
    { activity: 'COM-01', consumes: 'TUPE compliance assessment', usage: 'Should-cost model updated with pension obligation costs from legal assessment' }
  ]
}
```

---

## LEG-05 — Data Protection & Security Review

```javascript
{
  id: 'LEG-05',
  name: 'Data protection & security review',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: Minor — typically lighter data protection scope. Advisory doesn't
  //   usually process large volumes of personal data. Still relevant for some engagements.
  workstream: 'LEG',
  phase: 'DEV',
  role: 'Legal Lead',
  output: 'DPIA / security assessment',
  dependencies: ['SOL-05'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: critical for defence, justice, and central government contracts.
  // Security classification (OFFICIAL, SECRET, TOP SECRET) drives everything.

  inputs: [
    { from: 'SOL-05', artifact: 'Technology solution design', note: 'What systems process what data — the basis for the DPIA and security review' },
    { from: 'SOL-05.1.3', artifact: 'Security and information assurance design', note: 'Technical security architecture' },
    { external: true, artifact: 'ITT documentation — data handling requirements, security classification, vetting requirements, accreditation standards' },
    { external: true, artifact: 'UK GDPR, Data Protection Act 2018, ICO guidance' },
    { external: true, artifact: 'Government security frameworks — HMG Security Policy Framework, Cyber Essentials, ISO 27001' }
  ],

  subs: [
    {
      id: 'LEG-05.1',
      name: 'Data Protection & IA Assessment',
      description: 'Conduct the legal data protection and information assurance review',

      tasks: [
        {
          id: 'LEG-05.1.1',
          name: 'Conduct Data Protection Impact Assessment (DPIA) — personal data handling, lawful basis, data processor/controller roles, data subject rights, international transfers',
          raci: { r: 'Legal Lead / DPO', a: 'Bid Director', c: 'Technical Lead / Solution Architect', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-05', artifact: 'Technology solution design' },
            { external: true, artifact: 'UK GDPR, Data Protection Act 2018, ICO guidance' }
          ],
          outputs: [
            {
              name: 'Data Protection Impact Assessment (DPIA)',
              format: 'Structured DPIA document',
              quality: [
                'All personal data processing identified — what data, whose data, what processing, what purpose',
                'Lawful basis established per processing activity',
                'Data processor / controller / joint controller roles defined between us, client, and partners',
                'Data subject rights obligations documented — access, rectification, erasure, portability',
                'International transfer implications assessed (if applicable)',
                'Privacy risks identified with mitigations'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'LEG-05.1.2',
          name: 'Assess information security requirements — security classification, accreditation pathway, vetting levels, Cyber Essentials/ISO 27001 compliance',
          raci: { r: 'Legal Lead / Security Lead', a: 'Bid Director', c: 'Technical Lead', i: 'HR Lead' },
          inputs: [
            { from: 'SOL-05.1.3', artifact: 'Security and information assurance design' },
            { external: true, artifact: 'ITT documentation — security classification, vetting requirements, accreditation standards' },
            { external: true, artifact: 'Government security frameworks' }
          ],
          outputs: [
            {
              name: 'Information security compliance assessment',
              format: 'Structured compliance assessment',
              quality: [
                'Security classification requirements documented — OFFICIAL, SECRET, or higher',
                'Accreditation pathway defined — what certifications needed, timeline, process',
                'Vetting requirements mapped to roles — SC, DV, BPSS, CTC per role in staffing model',
                'Current compliance status assessed — what we already hold vs what we need to obtain',
                'Compliance gaps and timeline risks identified'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'LEG-05.1.3',
          name: 'Identify data protection and security risks — feeds SOL-12 solution risk register',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Technical Lead / Security Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'LEG-05.1.1', artifact: 'Data Protection Impact Assessment (DPIA)' },
            { from: 'LEG-05.1.2', artifact: 'Information security compliance assessment' }
          ],
          outputs: [
            {
              name: 'DPIA / security assessment (activity primary output)',
              format: 'Comprehensive data protection and security document',
              quality: [
                'DPIA complete with privacy risks and mitigations',
                'Security compliance position confirmed — compliant, gap, or timeline risk',
                'Combined data protection and security risks documented',
                'Cost implications identified — accreditation, vetting, additional security infrastructure',
                'Assessment ready for governance review'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'DPIA / security assessment',
      format: 'Comprehensive data protection and security document',
      quality: [
        'DPIA complete — personal data processing, lawful basis, roles, rights, risks',
        'Security compliance assessed — classification, accreditation, vetting',
        'Compliance gaps and timeline risks identified',
        'Cost implications quantified for COM-01'
      ]
    }
  ],

  consumers: [
    { activity: 'SOL-12', consumes: 'DPIA / security assessment', usage: 'Solution risk register includes data protection and security risks' },
    { activity: 'COM-01', consumes: 'DPIA / security assessment', usage: 'Should-cost model includes accreditation, vetting, and security infrastructure costs' },
    { activity: 'SOL-06', consumes: 'Information security compliance assessment', usage: 'Staffing model incorporates vetting requirements per role' }
  ]
}
```

---

## LEG-06 — Subcontractor Terms Review

```javascript
{
  id: 'LEG-06',
  name: 'Subcontractor terms review',
  workstream: 'LEG',
  phase: 'DEV',
  role: 'Legal Lead',
  // ARCHETYPE NOTES:
  // Technology/Digital: Minor — may include technology licensing agreements alongside subcontracts.
  // Consulting/Advisory: Minor — associate agreements, not formal subcontracts. Lighter review.
  output: 'Subcontract terms summary',
  dependencies: ['SUP-03', 'LEG-01'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',

  inputs: [
    { from: 'SUP-03', artifact: 'Signed teaming agreements', note: 'The teaming agreements to review' },
    { from: 'LEG-01', artifact: 'Contract markup with positions log', note: 'Prime contract terms that must flow down' },
    { from: 'COM-03.1.1', artifact: 'Inter-party commercial framework', note: 'Commercial terms agreed between parties' },
    { external: true, artifact: 'Corporate subcontracting policies and standard terms' }
  ],

  subs: [
    {
      id: 'LEG-06.1',
      name: 'Subcontractor Legal Review',
      description: 'Review subcontractor and partner legal arrangements for completeness, compliance, and back-to-back alignment',

      tasks: [
        {
          id: 'LEG-06.1.1',
          name: 'Review partner/subcontractor teaming agreements and terms — legal structure, liability, IP, confidentiality, termination, dispute resolution',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead / Supply Chain Lead', i: 'Partner Leads' },
          inputs: [
            { from: 'SUP-03', artifact: 'Signed teaming agreements' },
            { external: true, artifact: 'Corporate subcontracting policies and standard terms' }
          ],
          outputs: [
            {
              name: 'Subcontractor legal review',
              format: 'Structured legal assessment per partner',
              quality: [
                'Each teaming agreement reviewed for legal completeness — all essential terms present',
                'Liability and indemnity provisions assessed — are they proportionate and enforceable?',
                'IP ownership and licensing provisions confirmed — who owns what, especially for jointly developed IP',
                'Termination and exit provisions assessed — can we exit a partner if they underperform?',
                'Confidentiality and data sharing provisions confirmed'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'          // Multiple partner agreements reviewed concurrently
        },
        {
          id: 'LEG-06.1.2',
          name: 'Ensure back-to-back alignment — subcontractor terms flow down from prime contract appropriately, no gaps in risk coverage',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Finance' },
          inputs: [
            { from: 'LEG-06.1.1', artifact: 'Subcontractor legal review' },
            { from: 'LEG-01', artifact: 'Contract markup with positions log' },
            { from: 'COM-03.1.1', artifact: 'Inter-party commercial framework' }
          ],
          outputs: [
            {
              name: 'Back-to-back alignment assessment',
              format: 'Gap analysis',
              quality: [
                'Key prime contract obligations mapped to subcontractor terms — are they flowed down?',
                'Gaps in flow-down identified — risks we bear to the client but have not passed to the partner',
                'Commercial terms alignment confirmed — payment, indexation, service credits flow through consistently',
                'Risk allocation between prime and subcontractor is clear and documented'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'LEG-06.1.3',
          name: 'Validate subcontractor terms — legally sound, commercially aligned, feeds SUP-06 for formalisation',
          raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead / Supply Chain Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'LEG-06.1.1', artifact: 'Subcontractor legal review' },
            { from: 'LEG-06.1.2', artifact: 'Back-to-back alignment assessment' }
          ],
          outputs: [
            {
              name: 'Subcontract terms summary (activity primary output)',
              format: 'Comprehensive subcontractor legal summary',
              quality: [
                'All partner agreements reviewed and assessed',
                'Back-to-back alignment confirmed or gaps flagged for resolution',
                'Legal risks documented per partner relationship',
                'Recommendations for SUP-06 (back-to-back commercial terms) formalisation',
                'Assessment ready for governance review'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Subcontract terms summary',
      format: 'Comprehensive subcontractor legal summary',
      quality: [
        'All partner teaming agreements legally reviewed',
        'Back-to-back alignment assessed — prime terms flowed down appropriately',
        'Legal risks per partner documented',
        'Ready for SUP-06 formalisation'
      ]
    }
  ],

  consumers: [
    { activity: 'SUP-06', consumes: 'Subcontract terms summary', usage: 'Back-to-back commercial terms formalised from legal review' },
    { activity: 'GOV-03', consumes: 'Subcontract terms summary', usage: 'Pricing governance review examines subcontractor risk position' }
  ]
}
```

---

---

## DEL — Programme & Delivery: Ownership Note

> **Key distinction:** SOL workstream = solution design by the Solution Architect (the WHAT).
> DEL workstream = delivery planning owned by the Delivery Director (the HOW WE MAKE IT HAPPEN).
> SOL designs the solution. DEL takes ownership, refines, operationalises, and accepts accountability.
> The RACI shifts from Solution Architect (R) to Delivery Director (R).

---

## DEL-01 — Delivery Risk & Assumptions Register

```javascript
{
  id: 'DEL-01',
  name: 'Delivery risk & assumptions register',
  workstream: 'DEL',
  phase: 'DEV',
  role: 'Delivery Director',
  output: 'Delivery risk & assumptions register (living document)',
  dependencies: ['SOL-03', 'SOL-04'],
  effortDays: 8,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: this is the Delivery Director's own risk and assumptions register.
  // SOL-12 captures solution design risks (Solution Architect's view).
  // COM-07 captures commercial risks (Commercial Lead's view).
  // DEL-01 captures delivery-specific risks AND the key assumptions that underpin
  // the delivery plan — things we've assumed about how delivery will work that,
  // if wrong, change everything.
  // BM-13 consolidates all registers into the single bid risk register.
  // This is a LIVING DOCUMENT — maintained throughout the bid lifecycle.

  inputs: [
    { from: 'SOL-03', artifact: 'Target operating model', note: 'Solution design to assess for delivery risk' },
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'Delivery processes to assess for operational risk' },
    { from: 'SOL-07', artifact: 'Transition plan', note: 'Transition risks from Delivery Director perspective' },
    { from: 'SOL-12', artifact: 'Solution risk register', note: 'Solution risks to review and accept from delivery perspective' },
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'Strategic assumptions from capture plan' },
    { external: true, artifact: 'Corporate delivery risk framework and lessons from previous contracts' }
  ],

  subs: [
    {
      id: 'DEL-01.1',
      name: 'Risk & Assumption Identification',
      description: 'Establish the Delivery Director\'s risk and assumptions register — delivery-specific risks plus the key assumptions that underpin the entire delivery plan',

      tasks: [
        {
          id: 'DEL-01.1.1',
          name: 'Identify delivery-specific risks not covered in SOL-12 — bid-to-delivery handover, client readiness, operational ramp-up, supply chain delivery, service continuity during transition',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-12', artifact: 'Solution risk register' },
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SOL-07', artifact: 'Transition plan' }
          ],
          outputs: [
            {
              name: 'Delivery risk register',
              format: 'Structured risk register',
              quality: [
                'Delivery-specific risks identified — distinct from solution design risks',
                'Risks cover: bid-to-delivery handover, client dependency, operational ramp-up, supply chain, service continuity, resource availability',
                'Each risk assessed for likelihood, impact, and proximity',
                'Risk owner assigned — Delivery Director or delegated to delivery team member'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'DEL-01.1.2',
          name: 'Document key delivery assumptions — assumptions about client behaviour, volumes, timelines, third-party dependencies, resource availability that underpin the delivery plan',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'Finance' },
          inputs: [
            { from: 'SOL-04', artifact: 'Service delivery model' },
            { from: 'SAL-06', artifact: 'Capture plan (locked)' },
            { external: true, artifact: 'Corporate delivery risk framework and lessons from previous contracts' }
          ],
          outputs: [
            {
              name: 'Delivery assumptions register',
              format: 'Structured assumptions register',
              quality: [
                'Every material delivery assumption documented — what we are assuming will be true',
                'Each assumption has: description, basis, owner, validation approach, impact if wrong',
                'Key assumptions distinguished from routine assumptions — the ones that change the plan if wrong',
                'Assumptions register feeds COM-05 sensitivity analysis — each is a potential variable'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        }
      ]
    },
    {
      id: 'DEL-01.2',
      name: 'Living Register Management',
      description: 'Maintain and update the register through the bid lifecycle and prepare for governance',

      tasks: [
        {
          id: 'DEL-01.2.1',
          name: 'Maintain and update through the bid lifecycle — refresh as solution, commercial, and legal activities surface new risks and validate assumptions',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Bid Team', i: null },
          inputs: [
            { from: 'DEL-01.1.1', artifact: 'Delivery risk register' },
            { from: 'DEL-01.1.2', artifact: 'Delivery assumptions register' }
          ],
          outputs: [
            {
              name: 'Updated delivery risk & assumptions register',
              format: 'Living register (versioned)',
              quality: [
                'Register updated at key milestones — post solution lock, post pricing lock, pre-governance',
                'New risks added as they emerge — not a one-time exercise',
                'Assumptions validated or flagged as unvalidated — status tracked',
                'Version history maintained — what changed and why'
              ]
            }
          ],
          effort: 'Low',
          type: 'Iterative'
        },
        {
          id: 'DEL-01.2.2',
          name: 'Prepare risk and assumption position for governance gates — summarise for GOV-02 and GOV-03 entry criteria',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: null, i: 'Bid Manager' },
          inputs: [
            { from: 'DEL-01.2.1', artifact: 'Updated delivery risk & assumptions register' }
          ],
          outputs: [
            {
              name: 'Delivery risk & assumptions register (activity primary output — living document)',
              format: 'Governance-ready risk summary',
              quality: [
                'Top delivery risks summarised for executive audience',
                'Key unvalidated assumptions flagged — what the organisation is betting on',
                'Feeds BM-13 for consolidation into single bid risk register',
                'Meets governance gate entry criteria for risk'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Delivery risk & assumptions register (living document)',
      format: 'Structured risk and assumptions register',
      quality: [
        'Delivery-specific risks identified and assessed — distinct from solution and commercial risks',
        'Key delivery assumptions documented with validation status',
        'Register maintained as living document through bid lifecycle',
        'Governance-ready summary prepared for gate reviews'
      ]
    }
  ],

  consumers: [
    { activity: 'BM-13', consumes: 'Delivery risk & assumptions register', usage: 'Bid risk register consolidates delivery risks with solution and commercial risks' },
    { activity: 'DEL-06', consumes: 'Delivery risk & assumptions register', usage: 'Final risk mitigation and residual acceptance builds on this register' },
    { activity: 'GOV-02', consumes: 'Delivery risk & assumptions register', usage: 'Solution & strategy review examines delivery risk position' },
    { activity: 'COM-06', consumes: 'Delivery risk & assumptions register', usage: 'Pricing finalisation informed by delivery risk position' }
  ]
}
```

---

## DEL-02 — Mobilisation & Implementation Planning

```javascript
{
  id: 'DEL-02',
  name: 'Mobilisation & implementation planning',
  workstream: 'DEL',
  phase: 'DEV',
  role: 'Delivery Director',
  output: 'Mobilisation plan',
  dependencies: ['SOL-07'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: SOL-07 designs the transition approach (Solution Architect).
  // DEL-02 is where the Delivery Director takes ownership and turns it into
  // an operational programme plan they are accountable for delivering.

  inputs: [
    { from: 'SOL-07', artifact: 'Transition plan', note: 'The solution-designed transition approach — DEL-02 operationalises it' },
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'Workforce to mobilise' },
    { from: 'SOL-05', artifact: 'Technology solution design', note: 'Technology to deploy' },
    { from: 'DEL-01', artifact: 'Delivery risk & assumptions register', note: 'Delivery risks that affect mobilisation' },
    { external: true, artifact: 'ITT documentation — mobilisation timeline, service commencement requirements' },
    { external: true, artifact: 'Corporate mobilisation playbook and lessons from previous transitions' }
  ],

  subs: [
    {
      id: 'DEL-02.1',
      name: 'Operational Mobilisation Plan',
      description: 'Take the SOL-07 transition plan and develop the operational programme the Delivery Director will execute',

      tasks: [
        {
          id: 'DEL-02.1.1',
          name: 'Develop the detailed mobilisation programme — Gantt, dependencies, resource loading, milestones, acceptance criteria — operationalising SOL-07 transition plan',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / HR Lead / Technical Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-07', artifact: 'Transition plan' },
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-05', artifact: 'Technology solution design' }
          ],
          outputs: [
            {
              name: 'Detailed mobilisation programme',
              format: 'Programme plan with Gantt, dependencies, resource loading',
              quality: [
                'SOL-07 transition plan operationalised into an executable programme with named workstreams',
                'Dependencies between workstreams mapped — people, technology, service, assets',
                'Resource loading defined — who is needed when during mobilisation (distinct from steady state)',
                'Milestones have measurable acceptance criteria — not just dates but what "done" looks like',
                'Critical path through mobilisation identified — what must happen in sequence'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'DEL-02.1.2',
          name: 'Design mobilisation governance and reporting — how the mobilisation programme will be managed, tracked, and reported to the client',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Bid Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'DEL-02.1.1', artifact: 'Detailed mobilisation programme' }
          ],
          outputs: [
            {
              name: 'Mobilisation governance framework',
              format: 'Governance and reporting structure',
              quality: [
                'Mobilisation governance structure defined — board, workstream leads, reporting cadence',
                'Client reporting designed — what the client sees, how often, in what format',
                'Escalation and decision-making framework defined for mobilisation period',
                'Handover point defined — when does mobilisation governance transition to steady-state governance?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'DEL-02.2',
      name: 'Mobilisation Readiness',
      description: 'Assess what can be done pre-contract and validate the plan',

      tasks: [
        {
          id: 'DEL-02.2.1',
          name: 'Assess mobilisation readiness and pre-contract preparation — what can be started before contract signature to accelerate mobilisation',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'HR Lead / Technical Lead', i: 'Legal' },
          inputs: [
            { from: 'DEL-02.1.1', artifact: 'Detailed mobilisation programme' },
            { from: 'DEL-01', artifact: 'Delivery risk & assumptions register' }
          ],
          outputs: [
            {
              name: 'Pre-contract preparation plan',
              format: 'Action list with timeline',
              quality: [
                'Activities that can start pre-contract identified — recruitment, clearance applications, technology procurement, training development',
                'Pre-contract investment required quantified — cost of early start at risk',
                'Risk of pre-contract activity assessed — what if we don\'t win after investing?'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'DEL-02.2.2',
          name: 'Validate mobilisation plan — achievable, resourced, feeds the proposal response',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Bid Team (collective)', i: null },
          inputs: [
            { from: 'DEL-02.1.1', artifact: 'Detailed mobilisation programme' },
            { from: 'DEL-02.1.2', artifact: 'Mobilisation governance framework' },
            { from: 'DEL-02.2.1', artifact: 'Pre-contract preparation plan' }
          ],
          outputs: [
            {
              name: 'Mobilisation plan (validated — activity primary output)',
              format: 'Comprehensive mobilisation document',
              quality: [
                'Delivery Director accepts accountability for the mobilisation plan',
                'Plan is achievable within the contracted mobilisation period',
                'Resources identified and available (or plan to secure them)',
                'Risks documented in DEL-01 register',
                'Plan is compelling for the proposal — demonstrates operational readiness'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Mobilisation plan',
      format: 'Comprehensive mobilisation document',
      quality: [
        'SOL-07 transition plan operationalised into executable programme',
        'Governance and reporting designed for mobilisation period',
        'Pre-contract preparation activities identified',
        'Delivery Director accepts accountability for delivery'
      ]
    }
  ],

  consumers: [
    { activity: 'PRD-02', consumes: 'Mobilisation plan', usage: 'Proposal drafting references the mobilisation plan for transition response sections' },
    { activity: 'COM-01', consumes: 'Mobilisation plan', usage: 'Should-cost model includes mobilisation resource costs' },
    { activity: 'GOV-02', consumes: 'Mobilisation plan', usage: 'Solution & strategy review examines mobilisation readiness' }
  ]
}
```

---

## DEL-03 — Performance Framework & KPIs/SLAs

```javascript
{
  id: 'DEL-03',
  name: 'Performance framework & KPIs/SLAs',
  workstream: 'DEL',
  phase: 'DEV',
  role: 'Delivery Director',
  output: 'KPI/SLA framework',
  dependencies: [],                        // Day-1 start — can begin reviewing ITT performance requirements immediately
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: SOL-04.2 maps SLAs to delivery components (Solution Architect's design view).
  // DEL-03 is the Delivery Director's operational view — how we will actually manage
  // performance day-to-day, report to the client, and ensure we meet commitments.

  inputs: [
    { from: 'SOL-04.2.1', artifact: 'SLA/KPI-to-delivery commitment matrix', note: 'Solution design maps SLAs to components — DEL-03 operationalises' },
    { from: 'SOL-04.2.2', artifact: 'Quality assurance and continuous improvement framework', note: 'QA mechanisms designed in solution — DEL-03 makes them operational' },
    { from: 'SOL-02.2.1', artifact: 'Current performance baseline', note: 'Where performance is today — the baseline we must improve upon' },
    { external: true, artifact: 'ITT documentation — performance framework, KPIs, SLAs, service credits, reporting requirements' },
    { external: true, artifact: 'Contract documentation — performance schedules, measurement methodology, penalty/reward provisions' }
  ],

  subs: [
    {
      id: 'DEL-03.1',
      name: 'Performance Framework Design',
      description: 'Design the operational performance management regime the Delivery Director will run',

      tasks: [
        {
          id: 'DEL-03.1.1',
          name: 'Design the KPI/SLA operational framework — how each commitment will be measured, monitored, managed, and improved in live service',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SOL-04.2.1', artifact: 'SLA/KPI-to-delivery commitment matrix' },
            { external: true, artifact: 'ITT documentation — performance framework, KPIs, SLAs' },
            { external: true, artifact: 'Contract documentation — measurement methodology' }
          ],
          outputs: [
            {
              name: 'Operational performance framework',
              format: 'Structured framework document',
              quality: [
                'Every KPI/SLA has a defined measurement method — data source, calculation, frequency, baseline',
                'Monitoring approach defined — real-time, daily, weekly, monthly per KPI',
                'Escalation triggers defined — at what threshold does a KPI move from green to amber to red?',
                'Recovery mechanisms designed — what happens when a KPI is trending toward breach?',
                'Framework is operationally sustainable — not so complex that reporting itself becomes a burden'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'DEL-03.1.2',
          name: 'Design the performance reporting model — dashboards, reports, client governance forums, escalation triggers',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Technical Lead / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'DEL-03.1.1', artifact: 'Operational performance framework' },
            { external: true, artifact: 'ITT documentation — reporting requirements, governance forums' }
          ],
          outputs: [
            {
              name: 'Performance reporting model',
              format: 'Reporting and governance design',
              quality: [
                'Report types, frequency, and audience defined — operational, management, executive, client',
                'Dashboard design outlined — what the client sees, what we use internally',
                'Governance forum structure aligned to reporting — right data at the right level',
                'Trend and predictive reporting included — not just backward-looking actuals'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'DEL-03.1.3',
          name: 'Assess our ability to meet the performance framework — confidence assessment per KPI/SLA, identifies risks for DEL-01',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / Service Line Leads', i: 'Commercial Lead' },
          inputs: [
            { from: 'DEL-03.1.1', artifact: 'Operational performance framework' },
            { from: 'SOL-02.2.1', artifact: 'Current performance baseline' }
          ],
          outputs: [
            {
              name: 'KPI/SLA framework (validated — activity primary output)',
              format: 'Comprehensive performance framework with confidence assessment',
              quality: [
                'Confidence assessment per KPI — high/medium/low with rationale',
                'KPIs where we are at risk of breach identified — feeds DEL-01 risk register',
                'Improvement trajectory documented — where current baseline is below target, the path to compliance',
                'Framework confirmed as deliverable by the Delivery Director'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'KPI/SLA framework',
      format: 'Comprehensive performance framework with confidence assessment',
      quality: [
        'Every KPI/SLA has measurement method, monitoring approach, escalation triggers, recovery mechanisms',
        'Performance reporting model designed — dashboards, reports, governance forums',
        'Confidence assessment per KPI with risk identification',
        'Delivery Director accepts accountability for performance delivery'
      ]
    }
  ],

  consumers: [
    { activity: 'COM-04', consumes: 'KPI/SLA framework', usage: 'Commercial model incorporates service credit exposure from KPI confidence assessment' },
    { activity: 'PRD-02', consumes: 'KPI/SLA framework', usage: 'Proposal drafting references the performance framework for service delivery response sections' },
    { activity: 'DEL-01', consumes: 'KPI/SLA framework', usage: 'Delivery risk register updated with KPI breach risks' }
  ]
}
```

---

## DEL-04 — Resource & Capacity Plan

```javascript
{
  id: 'DEL-04',
  name: 'Resource & capacity plan',
  workstream: 'DEL',
  phase: 'DEV',
  role: 'Delivery Director',
  output: 'Resource plan',
  dependencies: ['SOL-06'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: SOL-06 designs the target staffing model (Solution Architect's view — the workforce the solution needs).
  // DEL-04 is the Delivery Director taking ownership of workforce planning — how to actually
  // resource, mobilise, manage, and sustain the delivery team. Includes bid team to delivery
  // team handover planning.

  inputs: [
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'The target workforce design — DEL-04 operationalises' },
    { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis', note: 'Gaps to fill — recruitment, redeployment, upskilling' },
    { from: 'DEL-02', artifact: 'Mobilisation plan', note: 'Mobilisation resource requirements' },
    { external: true, artifact: 'Corporate resource pool — available people, pipeline, recruitment capacity' },
    { external: true, artifact: 'ITT documentation — resource and key personnel requirements' }
  ],

  subs: [
    {
      id: 'DEL-04.1',
      name: 'Delivery Resource Planning',
      description: 'The Delivery Director\'s operational workforce plan — how to resource, mobilise, and sustain the delivery team',

      tasks: [
        {
          id: 'DEL-04.1.1',
          name: 'Develop the delivery resource plan — operational workforce plan building on SOL-06, including mobilisation resourcing, bid-to-delivery handover, and steady-state workforce management',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'HR Lead / Solution Architect', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-06.2.2', artifact: 'Workforce gap analysis' },
            { from: 'DEL-02', artifact: 'Mobilisation plan' },
            { external: true, artifact: 'Corporate resource pool — available people, pipeline, recruitment capacity' }
          ],
          outputs: [
            {
              name: 'Delivery resource plan',
              format: 'Operational workforce plan',
              quality: [
                'SOL-06 staffing model accepted and operationalised by Delivery Director',
                'Mobilisation resourcing planned — who is needed before, during, and after mobilisation',
                'Bid-to-delivery team handover planned — how knowledge transfers from bid team to delivery team',
                'Steady-state workforce management approach defined — attrition management, succession, development',
                'Resource risks identified — scarce skills, clearance delays, market availability'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'DEL-04.1.2',
          name: 'Plan resource mobilisation and onboarding — recruitment timeline, clearance processing, training, onboarding programme',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'HR Lead', i: 'Finance' },
          inputs: [
            { from: 'DEL-04.1.1', artifact: 'Delivery resource plan' },
            { external: true, artifact: 'ITT documentation — resource and key personnel requirements' }
          ],
          outputs: [
            {
              name: 'Resource mobilisation and onboarding plan',
              format: 'Structured timeline with actions',
              quality: [
                'Recruitment timeline per role — aligned to mobilisation programme milestones',
                'Clearance processing timeline factored in — SC/DV applications take months',
                'Training and induction programme designed — what new team members need before they are productive',
                'Onboarding sequence defined — who starts when, in what order, with what support'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'DEL-04.1.3',
          name: 'Validate resource plan — achievable, costable, risks identified, Delivery Director accepts accountability',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'HR Lead / Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'DEL-04.1.1', artifact: 'Delivery resource plan' },
            { from: 'DEL-04.1.2', artifact: 'Resource mobilisation and onboarding plan' }
          ],
          outputs: [
            {
              name: 'Resource plan (validated — activity primary output)',
              format: 'Comprehensive delivery resource document',
              quality: [
                'Delivery Director accepts the resource plan as achievable',
                'Resource risks documented and fed to DEL-01',
                'Costable for COM-01 — mobilisation resourcing costs quantified',
                'Compelling for the proposal — demonstrates we can stand up the team'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Resource plan',
      format: 'Comprehensive delivery resource document',
      quality: [
        'SOL-06 staffing model operationalised by Delivery Director',
        'Mobilisation resourcing and bid-to-delivery handover planned',
        'Resource mobilisation and onboarding timeline defined',
        'Delivery Director accepts accountability for resourcing'
      ]
    }
  ],

  consumers: [
    { activity: 'COM-01', consumes: 'Resource plan', usage: 'Should-cost model includes mobilisation resourcing costs' },
    { activity: 'PRD-02', consumes: 'Resource plan', usage: 'Proposal drafting references the resource plan for team and mobilisation response sections' },
    { activity: 'DEL-01', consumes: 'Resource plan', usage: 'Delivery risk register updated with resourcing risks' }
  ]
}
```

---

## DEL-05 — Business Continuity & Exit Planning

```javascript
{
  id: 'DEL-05',
  name: 'Business continuity & exit planning',
  workstream: 'DEL',
  phase: 'DEV',
  role: 'Delivery Director',
  output: 'BC/exit plan',
  dependencies: [],                        // Day-1 start
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: unique to DEL — no SOL equivalent. Required in most government contracts.
  // BC/DR addresses service resilience during the contract.
  // Exit/handback addresses what happens when the contract ends.

  inputs: [
    { from: 'SOL-03', artifact: 'Target operating model', note: 'What needs to be resilient / handed back' },
    { from: 'SOL-05', artifact: 'Technology solution design', note: 'Systems that need DR and data that needs to be returned' },
    { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule', note: 'Workforce that reverse-TUPEs on exit' },
    { external: true, artifact: 'ITT documentation — BC/DR requirements, exit provisions, handback obligations' },
    { external: true, artifact: 'Contract documentation — exit schedule, termination provisions, data return obligations' },
    { external: true, artifact: 'Corporate BC/DR standards and frameworks' }
  ],

  subs: [
    {
      id: 'DEL-05.1',
      name: 'Business Continuity & Disaster Recovery',
      description: 'Design how the service continues during major disruption',

      tasks: [
        {
          id: 'DEL-05.1.1',
          name: 'Design business continuity and disaster recovery approach — how the service continues during major disruption, site loss, technology failure, or pandemic',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Technical Lead / Solution Architect', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SOL-05', artifact: 'Technology solution design' },
            { external: true, artifact: 'ITT documentation — BC/DR requirements' },
            { external: true, artifact: 'Corporate BC/DR standards and frameworks' }
          ],
          outputs: [
            {
              name: 'Business continuity and disaster recovery plan',
              format: 'Structured BC/DR document',
              quality: [
                'Key services and critical processes identified with recovery time objectives (RTO) and recovery point objectives (RPO)',
                'BC scenarios covered — site loss, technology failure, supply chain failure, pandemic, key person loss',
                'DR approach for technology designed — failover, backup, replication, restoration',
                'BC invocation and communication procedures outlined',
                'Testing and exercising approach defined — how BC/DR will be validated'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    },
    {
      id: 'DEL-05.2',
      name: 'Exit & Handback Planning',
      description: 'Design how the contract ends — reverse TUPE, data return, knowledge transfer, asset handback',

      tasks: [
        {
          id: 'DEL-05.2.1',
          name: 'Design exit and handback plan — reverse TUPE, data return, knowledge transfer, asset handback, service continuity during exit period',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Legal / HR Lead / Technical Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SOL-06', artifact: 'Staffing model with TUPE schedule' },
            { from: 'SOL-05', artifact: 'Technology solution design' },
            { external: true, artifact: 'Contract documentation — exit schedule, termination provisions, data return obligations' }
          ],
          outputs: [
            {
              name: 'BC/exit plan (validated — activity primary output)',
              format: 'Comprehensive BC/DR and exit document',
              quality: [
                'Exit timeline and phasing designed — aligned to contract termination provisions',
                'Reverse TUPE process outlined — workforce transfer to successor or client',
                'Data return and system decommission approach designed — what data, what format, what timeline',
                'Knowledge transfer approach designed — documentation, shadowing, handover period',
                'Asset handback identified — property, equipment, IP, licences',
                'Service continuity during exit period assured — no degradation while handing back'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'BC/exit plan',
      format: 'Comprehensive BC/DR and exit document',
      quality: [
        'BC/DR approach designed with RTO/RPO per critical service',
        'DR technology approach defined — failover, backup, restoration',
        'Exit and handback plan designed — reverse TUPE, data, knowledge, assets',
        'Service continuity assured during both disruption and exit'
      ]
    }
  ],

  consumers: [
    { activity: 'PRD-02', consumes: 'BC/exit plan', usage: 'Proposal drafting references BC/DR and exit plan for relevant response sections' },
    { activity: 'COM-01', consumes: 'BC/exit plan', usage: 'Should-cost model includes BC/DR infrastructure costs' },
    { activity: 'LEG-01', consumes: 'BC/exit plan', usage: 'Contract review validates exit provisions align with our plan' }
  ]
}
```

---

## DEL-06 — Risk Mitigation & Residual Acceptance

```javascript
{
  id: 'DEL-06',
  name: 'Risk mitigation & residual acceptance',
  workstream: 'DEL',
  phase: 'DEV',
  role: 'Delivery Director',
  output: 'Mitigated risk register (assured)',
  dependencies: ['DEL-01', 'COM-06'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: this is the Delivery Director's final risk consolidation and acceptance activity.
  // It brings together solution (SOL-12), commercial (COM-07), and delivery (DEL-01)
  // risks from the Delivery Director's perspective — what delivery risk remains after
  // all mitigations? The Delivery Director must accept the residual risk position.
  // BM-13 is the bid-level consolidation (Bid Manager's view).
  // DEL-06 is the delivery-level consolidation (Delivery Director's view).

  inputs: [
    { from: 'DEL-01', artifact: 'Delivery risk & assumptions register' },
    { from: 'SOL-12', artifact: 'Solution risk register' },
    { from: 'COM-07', artifact: 'Commercial risk register' },
    { from: 'COM-06', artifact: 'Pricing model (locked & assured)', note: 'Risk contingency included in pricing — what risk has been priced?' },
    { from: 'LEG-02', artifact: 'Risk allocation matrix', note: 'Contractual risk allocation' },
    { from: 'LEG-04', artifact: 'TUPE compliance assessment', note: 'TUPE legal risks' },
    { from: 'LEG-05', artifact: 'DPIA / security assessment', note: 'Data protection and security risks' }
  ],

  subs: [
    {
      id: 'DEL-06.1',
      name: 'Final Risk Consolidation & Acceptance',
      description: 'Bring all risk registers together from the Delivery Director\'s perspective, confirm mitigations, and accept the residual risk position for governance',

      tasks: [
        {
          id: 'DEL-06.1.1',
          name: 'Consolidate all risk registers from delivery perspective — solution, commercial, delivery, legal — into one assured view',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Solution Architect / Commercial Lead / Legal Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'DEL-01', artifact: 'Delivery risk & assumptions register' },
            { from: 'SOL-12', artifact: 'Solution risk register' },
            { from: 'COM-07', artifact: 'Commercial risk register' },
            { from: 'LEG-02', artifact: 'Risk allocation matrix' },
            { from: 'LEG-04', artifact: 'TUPE compliance assessment' },
            { from: 'LEG-05', artifact: 'DPIA / security assessment' }
          ],
          outputs: [
            {
              name: 'Consolidated delivery risk register',
              format: 'Comprehensive risk register',
              quality: [
                'All risks from solution, commercial, delivery, and legal workstreams consolidated from delivery perspective',
                'Duplicates removed, cross-cutting risks identified',
                'Every risk categorised — delivery, solution, commercial, legal, transition, people, technology'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'DEL-06.1.2',
          name: 'Confirm mitigation status and residual risk position — all mitigations assigned and in progress, residual risk accepted by Delivery Director',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: 'Risk Owners', i: 'Commercial Lead' },
          inputs: [
            { from: 'DEL-06.1.1', artifact: 'Consolidated delivery risk register' },
            { from: 'COM-06', artifact: 'Pricing model (locked & assured)', note: 'What risk contingency has been priced?' }
          ],
          outputs: [
            {
              name: 'Residual risk position statement',
              format: 'Risk acceptance document',
              quality: [
                'Every high/significant risk has confirmed mitigation status — in progress, complete, or accepted',
                'Residual risk quantified — what exposure remains after mitigations and pricing contingency?',
                'Delivery Director formally accepts the residual risk position',
                'Risks that exceed Delivery Director authority escalated to Bid Director / Senior Executive'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'DEL-06.1.3',
          name: 'Prepare risk position for final governance — the authoritative delivery risk view for GOV-03 (Pricing & Risk Review)',
          raci: { r: 'Delivery Director', a: 'Bid Director', c: null, i: 'Bid Manager' },
          inputs: [
            { from: 'DEL-06.1.1', artifact: 'Consolidated delivery risk register' },
            { from: 'DEL-06.1.2', artifact: 'Residual risk position statement' }
          ],
          outputs: [
            {
              name: 'Mitigated risk register (assured — activity primary output)',
              format: 'Governance-ready assured risk register',
              quality: [
                'Complete risk register with mitigation status and residual position',
                'Delivery Director sign-off recorded — accountability for delivery risk accepted',
                'Executive summary for governance audience — top risks, mitigations, residual exposure',
                'Ready for GOV-03 (Pricing & Risk Review) and feeds BM-13 consolidation'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Mitigated risk register (assured)',
      format: 'Governance-ready assured risk register',
      quality: [
        'All workstream risks consolidated from delivery perspective',
        'Mitigation status confirmed per risk',
        'Residual risk position quantified and accepted by Delivery Director',
        'Governance-ready with executive summary'
      ]
    }
  ],

  consumers: [
    { activity: 'GOV-03', consumes: 'Mitigated risk register (assured)', usage: 'Pricing & Risk Review examines the delivery risk position alongside pricing' },
    { activity: 'BM-13', consumes: 'Mitigated risk register (assured)', usage: 'Bid risk register consolidates with other risk views' }
  ]
}
```

---

---

## SUP-01 — Partner Identification & Selection

```javascript
{
  id: 'SUP-01',
  name: 'Partner identification & selection',
  workstream: 'SUP',
  phase: 'DEV',
  role: 'Supply Chain Lead',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED — partner model is associate network (individual consultants
  //   or small specialist firms), not large subcontractors. Due diligence is lighter.
  //   Selection criteria shift to individual expertise, not organisational capability.
  //   Guidance: "For consulting, partners are associates — assess individual expertise and availability."
  output: 'Partner shortlist with rationale',
  dependencies: ['SOL-01'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: SAL-06 L2.3 defined the consortium strategy, partner capability requirements,
  // and work breakdown. SUP-01 EXECUTES against that brief — sourcing, assessing, and
  // selecting the specific firms. It does not re-identify what we need.

  inputs: [
    { from: 'SAL-06.3.1', artifact: 'Consortium strategy', note: 'The strategic framework — prime/sub, JV, SPV' },
    { from: 'SAL-06.3.2', artifact: 'Partner capability requirements', note: 'What capabilities we need and why — the brief to source against' },
    { from: 'SAL-06.3.3', artifact: 'Consortium delivery model and work breakdown', note: 'Who owns what scope' },
    { from: 'SAL-05.2.2', artifact: 'Score gap analysis', note: 'Where partner credentials close scoring gaps' },
    { from: 'SOL-01', artifact: 'Requirements interpretation document', note: 'Technical requirements that partners must address' },
    { external: true, artifact: 'Market intelligence — known firms, framework incumbents, specialist providers' },
    { external: true, artifact: 'Corporate preferred supplier list and partner relationship history' }
  ],

  subs: [
    {
      id: 'SUP-01.1',
      name: 'Partner Search & Assessment',
      description: 'Source candidate partners against the SAL-06 brief, conduct due diligence, and select the shortlist',

      tasks: [
        {
          id: 'SUP-01.1.1',
          name: 'Source candidate partners against SAL-06 capability requirements — develop a long-list of firms that match each partner requirement',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Capture Lead / Solution Architect', i: 'Commercial Lead' },
          inputs: [
            { from: 'SAL-06.3.2', artifact: 'Partner capability requirements' },
            { external: true, artifact: 'Market intelligence — known firms, framework incumbents, specialist providers' },
            { external: true, artifact: 'Corporate preferred supplier list and partner relationship history' }
          ],
          outputs: [
            {
              name: 'Partner long-list',
              format: 'Structured register per capability requirement',
              quality: [
                'At least 2-3 candidates identified per capability requirement — not single-sourced',
                'Each candidate has rationale for inclusion — why they match the requirement',
                'Existing relationships and prior experience noted per candidate',
                'Initial market availability confirmed — are they likely to be available and interested?'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'SUP-01.1.2',
          name: 'Conduct due diligence on shortlisted partners — capability, capacity, security clearance, financial standing, cultural fit, conflict of interest',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Legal / Commercial Lead', i: 'Finance' },
          inputs: [
            { from: 'SUP-01.1.1', artifact: 'Partner long-list' },
            { from: 'SAL-06.3.1', artifact: 'Consortium strategy' }
          ],
          outputs: [
            {
              name: 'Partner due diligence assessments',
              format: 'Per-partner structured assessment',
              quality: [
                'Capability assessed against specific requirement — can they deliver the scope?',
                'Capacity assessed — are they available, or are they committed on competing bids?',
                'Security clearance status confirmed — do they hold the required clearances or can they obtain them?',
                'Financial standing assessed — are they stable enough for a multi-year subcontract?',
                'Conflict of interest checked — are they bidding with a competitor?'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'
        },
        {
          id: 'SUP-01.1.3',
          name: 'Select and confirm partner shortlist — recommended partners per capability requirement with rationale',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'Capture Lead' },
          inputs: [
            { from: 'SUP-01.1.2', artifact: 'Partner due diligence assessments' }
          ],
          outputs: [
            {
              name: 'Partner shortlist with rationale (activity primary output)',
              format: 'Recommended partner register',
              quality: [
                'Recommended partner per capability requirement — with rationale and backup option',
                'Due diligence summary per selected partner — capability, clearance, financial, conflict status',
                'Any conditions or risks per partner noted — "subject to clearance", "capacity concern"',
                'Shortlist feeds SUP-02 (solution inputs), SUP-03 (teaming), SUP-05 (credentials)'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Partner shortlist with rationale',
      format: 'Recommended partner register with due diligence',
      quality: [
        'Partners sourced against SAL-06 capability requirements — not re-identified, executed',
        'Due diligence conducted — capability, capacity, clearance, financial, conflict',
        'Recommended partner per requirement with rationale and backup'
      ]
    }
  ],

  consumers: [
    { activity: 'SUP-02', consumes: 'Partner shortlist', usage: 'Selected partners briefed for solution design contribution' },
    { activity: 'SUP-03', consumes: 'Partner shortlist', usage: 'Teaming agreement negotiation initiated with selected partners' },
    { activity: 'SUP-05', consumes: 'Partner shortlist', usage: 'Evidence requirements issued to selected partners' },
    { activity: 'GOV-02', consumes: 'Partner shortlist', usage: 'Solution & strategy review examines partner selection' }
  ]
}
```

---

## SUP-02 — Partner Solution Inputs & Design Contribution

```javascript
{
  id: 'SUP-02',
  name: 'Partner solution inputs & design contribution',
  workstream: 'SUP',
  phase: 'DEV',
  role: 'Supply Chain Lead',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED — associates contribute CVs and methodology input, not
  //   solution design components. Briefing is lighter. Integration is about team composition.
  output: 'Partner solution inputs pack',
  dependencies: ['SUP-01', 'SOL-03'],
  effortDays: 10,
  teamSize: 2,
  parallelisationType: 'P',

  inputs: [
    { from: 'SUP-01', artifact: 'Partner shortlist with rationale' },
    { from: 'SOL-03', artifact: 'Target operating model', note: 'The solution framework partners must contribute to' },
    { from: 'SAL-06.3.3', artifact: 'Consortium delivery model and work breakdown', note: 'What scope each partner owns' },
    { external: true, artifact: 'Partner briefing packs — scope, requirements, design contribution expectations, timelines' }
  ],

  subs: [
    {
      id: 'SUP-02.1',
      name: 'Partner Solution Integration',
      description: 'Brief partners, collect their solution inputs, and integrate into the overall solution design',

      tasks: [
        {
          id: 'SUP-02.1.1',
          name: 'Brief partners on solution scope and design contribution requirements — what we need from them, in what format, by when',
          raci: { r: 'Supply Chain Lead', a: 'Solution Architect', c: 'Bid Manager', i: 'Commercial Lead' },
          inputs: [
            { from: 'SUP-01', artifact: 'Partner shortlist with rationale' },
            { from: 'SOL-03', artifact: 'Target operating model' },
            { from: 'SAL-06.3.3', artifact: 'Consortium delivery model and work breakdown' }
          ],
          outputs: [
            {
              name: 'Partner design contribution briefs',
              format: 'Per-partner structured brief',
              quality: [
                'Each partner has a clear brief — scope, deliverables, format, timeline',
                'Design constraints and integration points specified — how their contribution fits the overall solution',
                'Quality expectations set — what a good partner solution input looks like'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'SUP-02.1.2',
          name: 'Collect and review partner solution inputs — approach, capability statements, technical contributions, key personnel CVs',
          raci: { r: 'Supply Chain Lead', a: 'Solution Architect', c: 'Technical Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SUP-02.1.1', artifact: 'Partner design contribution briefs' }
          ],
          outputs: [
            {
              name: 'Partner solution submissions (reviewed)',
              format: 'Per-partner solution input pack',
              quality: [
                'Each partner submission reviewed for completeness against the brief',
                'Technical quality assessed — is the contribution credible and aligned?',
                'Gaps and issues documented — what needs rework or clarification',
                'Key personnel CVs reviewed for relevance and quality'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'
        },
        {
          id: 'SUP-02.1.3',
          name: 'Integrate partner inputs into the solution design — confirm alignment with overall TOM and service delivery model',
          raci: { r: 'Solution Architect', a: 'Bid Director', c: 'Supply Chain Lead / Technical Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SUP-02.1.2', artifact: 'Partner solution submissions (reviewed)' },
            { from: 'SOL-03', artifact: 'Target operating model' }
          ],
          outputs: [
            {
              name: 'Partner solution inputs pack (validated — activity primary output)',
              format: 'Integrated partner contribution document',
              quality: [
                'All partner contributions integrated into the solution design — no orphan inputs',
                'Integration points confirmed — partner contributions align at boundaries with our solution',
                'Consistency checked — partner approaches do not contradict the overall TOM',
                'Gaps resolved or flagged — any outstanding partner design contributions tracked'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Partner solution inputs pack',
      format: 'Integrated partner contribution document',
      quality: [
        'All partners briefed and submissions collected',
        'Contributions reviewed for quality and completeness',
        'Integrated into overall solution design without conflicts'
      ]
    }
  ],

  consumers: [
    { activity: 'SOL-05', consumes: 'Partner solution inputs pack', usage: 'Technology approach includes partner technology contributions' },
    { activity: 'SOL-11', consumes: 'Partner solution inputs pack', usage: 'Solution design lock includes partner contributions' },
    { activity: 'SUP-04', consumes: 'Partner solution inputs pack', usage: 'Partner pricing based on confirmed scope from their design contribution' }
  ]
}
```

---

## SUP-03 — Teaming Agreement Negotiation

```javascript
{
  id: 'SUP-03',
  name: 'Teaming agreement negotiation',
  workstream: 'SUP',
  phase: 'DEV',
  role: 'Supply Chain Lead',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED — associate agreements, not teaming agreements. Much simpler
  //   terms: day rate, availability, expenses, IP (usually straightforward). No exclusivity
  //   typically. Much lighter legal complexity than formal subcontracting.
  output: 'Signed teaming agreements',
  dependencies: ['SUP-01'],
  effortDays: 15,
  teamSize: 1,
  parallelisationType: 'S',

  inputs: [
    { from: 'SUP-01', artifact: 'Partner shortlist with rationale' },
    { from: 'SAL-06.3.1', artifact: 'Consortium strategy', note: 'Legal structure — prime/sub, JV, SPV' },
    { external: true, artifact: 'Corporate teaming agreement templates and standard terms' },
    { external: true, artifact: 'Legal advice on teaming structure and IP provisions' }
  ],

  subs: [
    {
      id: 'SUP-03.1',
      name: 'Teaming & Legal Framework',
      description: 'Negotiate and execute teaming agreements with all selected partners',

      tasks: [
        {
          id: 'SUP-03.1.1',
          name: 'Issue NDAs and initiate teaming discussions — establish confidentiality and exclusivity framework with each partner',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Legal Lead', i: 'Commercial Lead' },
          inputs: [
            { from: 'SUP-01', artifact: 'Partner shortlist with rationale' },
            { external: true, artifact: 'Corporate teaming agreement templates and standard terms' }
          ],
          outputs: [
            {
              name: 'Executed NDAs and teaming discussion framework',
              format: 'Signed NDAs per partner',
              quality: [
                'NDAs executed with all shortlisted partners before any confidential information shared',
                'Exclusivity terms agreed where required — partner committed to our bid, not competing',
                'Teaming discussion scope and timeline agreed — what will be negotiated and by when'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'SUP-03.1.2',
          name: 'Negotiate and execute teaming agreements — scope, obligations, exclusivity, IP, confidentiality, termination, dispute resolution',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Legal Lead / Commercial Lead', i: 'Partner Leads' },
          inputs: [
            { from: 'SUP-03.1.1', artifact: 'Executed NDAs' },
            { from: 'SAL-06.3.1', artifact: 'Consortium strategy' },
            { external: true, artifact: 'Legal advice on teaming structure and IP provisions' }
          ],
          outputs: [
            {
              name: 'Signed teaming agreements',
              format: 'Executed agreements per partner',
              quality: [
                'Teaming agreement covers: scope, obligations, exclusivity, IP ownership, confidentiality, termination, dispute resolution',
                'IP provisions clear — who owns what, especially jointly developed IP',
                'Termination provisions protect us — can exit a partner who underperforms or breaches',
                'Agreement is consistent with the consortium strategy from SAL-06'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SUP-03.1.3',
          name: 'Confirm teaming status for all partners — signed, in progress, or at risk — feeds LEG-06 for legal review',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Legal Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SUP-03.1.2', artifact: 'Signed teaming agreements' }
          ],
          outputs: [
            {
              name: 'Teaming status register (activity primary output complement)',
              format: 'Status tracker',
              quality: [
                'Every partner has a teaming status — signed, in negotiation, at risk, or failed',
                'At-risk partners have mitigation plan — backup partner identified or fallback scope approach',
                'All signed agreements available for LEG-06 legal review'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Signed teaming agreements',
      format: 'Executed agreements per partner with status register',
      quality: [
        'NDAs executed before confidential information shared',
        'Teaming agreements cover all essential terms',
        'All partners have confirmed teaming status',
        'At-risk partners have mitigation plans'
      ]
    }
  ],

  consumers: [
    { activity: 'LEG-06', consumes: 'Signed teaming agreements', usage: 'Subcontractor terms review assesses legal provisions' },
    { activity: 'SUP-06', consumes: 'Signed teaming agreements', usage: 'Back-to-back terms build on teaming agreement framework' },
    { activity: 'COM-03', consumes: 'Signed teaming agreements', usage: 'Commercial structure requires confirmed teaming before pricing requests' }
  ]
}
```

---

## SUP-04 — Partner Pricing

```javascript
{
  id: 'SUP-04',
  name: 'Partner pricing',
  workstream: 'SUP',
  phase: 'DEV',
  role: 'Supply Chain Lead',
  output: 'Partner pricing schedules',
  dependencies: ['SUP-02', 'SOL-04'],
  effortDays: 8,
  teamSize: 1,
  parallelisationType: 'S',
  // Note: SUP-04 manages the partner side of the pricing process.
  // COM-03 manages the commercial side (structure, negotiation, integration).
  // SUP-04 ensures partners submit on time, in format, and resolves issues.

  inputs: [
    { from: 'SUP-02', artifact: 'Partner solution inputs pack', note: 'Confirmed partner scope — what they are pricing' },
    { from: 'COM-03.1.2', artifact: 'Partner pricing request packs', note: 'The structured pricing requests issued by COM-03' },
    { from: 'SOL-04', artifact: 'Service delivery model', note: 'Delivery context for partner pricing' }
  ],

  subs: [
    {
      id: 'SUP-04.1',
      name: 'Partner Pricing Management',
      description: 'Manage the partner pricing submission process — ensure timely, complete, and aligned submissions',

      tasks: [
        {
          id: 'SUP-04.1.1',
          name: 'Manage partner pricing submission process — ensure partners respond to COM-03 pricing requests on time and in the required format',
          raci: { r: 'Supply Chain Lead', a: 'Commercial Lead', c: 'Bid Manager', i: 'Partner Leads' },
          inputs: [
            { from: 'COM-03.1.2', artifact: 'Partner pricing request packs' },
            { from: 'SUP-02', artifact: 'Partner solution inputs pack' }
          ],
          outputs: [
            {
              name: 'Partner pricing submissions',
              format: 'Per-partner pricing schedules',
              quality: [
                'All partners have submitted pricing by the deadline',
                'Submissions are in the required format — aligned to our pricing structure',
                'Late or non-compliant submissions flagged and escalated immediately'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Parallel'
        },
        {
          id: 'SUP-04.1.2',
          name: 'Facilitate pricing clarification and iteration — resolve gaps, align assumptions between partners and our commercial model',
          raci: { r: 'Supply Chain Lead', a: 'Commercial Lead', c: 'Finance / Solution Architect', i: 'Partner Leads' },
          inputs: [
            { from: 'SUP-04.1.1', artifact: 'Partner pricing submissions' },
            { from: 'COM-03.2.1', artifact: 'Partner pricing validation assessment', note: 'Issues identified by COM-03 review' }
          ],
          outputs: [
            {
              name: 'Partner pricing schedules (clarified — activity primary output)',
              format: 'Final partner pricing submissions',
              quality: [
                'All pricing queries resolved — gaps closed, assumptions aligned',
                'Partner pricing ready for COM-03 negotiation and integration',
                'Any outstanding issues or caveats documented for COM-03'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Partner pricing schedules',
      format: 'Per-partner pricing submissions (clarified)',
      quality: [
        'All partners have submitted complete pricing on time',
        'Queries resolved and assumptions aligned',
        'Ready for COM-03 negotiation and integration'
      ]
    }
  ],

  consumers: [
    { activity: 'COM-03', consumes: 'Partner pricing schedules', usage: 'Commercial structure and pricing integration' }
  ]
}
```

---

## SUP-05 — Partner Credentials & References

```javascript
{
  id: 'SUP-05',
  name: 'Partner credentials & references',
  workstream: 'SUP',
  phase: 'DEV',
  role: 'Supply Chain Lead',
  output: 'Partner case studies & CVs',
  dependencies: ['SUP-01'],
  effortDays: 5,
  teamSize: 2,
  parallelisationType: 'P',

  inputs: [
    { from: 'SUP-01', artifact: 'Partner shortlist with rationale' },
    { from: 'SOL-10', artifact: 'Evidence requirements matrix', note: 'What evidence is needed from partners — case studies, CVs, credentials' },
    { from: 'SOL-10.1.3', artifact: 'Prioritised evidence gap register', note: 'Which gaps require partner evidence to close' },
    { external: true, artifact: 'ITT documentation — evidence requirements, CV format, case study format' }
  ],

  subs: [
    {
      id: 'SUP-05.1',
      name: 'Partner Evidence Collection',
      description: 'Collect, review, and prepare partner evidence for the bid',

      tasks: [
        {
          id: 'SUP-05.1.1',
          name: 'Issue evidence requirements to partners — case studies, CVs, credentials, certifications required per SOL-10 evidence matrix',
          raci: { r: 'Supply Chain Lead', a: 'Bid Manager', c: 'Bid Coordinator', i: 'Partner Leads' },
          inputs: [
            { from: 'SOL-10', artifact: 'Evidence requirements matrix' },
            { from: 'SOL-10.1.3', artifact: 'Prioritised evidence gap register' },
            { external: true, artifact: 'ITT documentation — evidence requirements, CV format, case study format' }
          ],
          outputs: [
            {
              name: 'Partner evidence briefs',
              format: 'Per-partner evidence request',
              quality: [
                'Each partner has a clear brief — what evidence, in what format, by when',
                'Priority evidence flagged — items that close scoring gaps are urgent',
                'Format requirements specified — aligned to ITT submission requirements'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        },
        {
          id: 'SUP-05.1.2',
          name: 'Collect, review, and adapt partner evidence — quality, relevance, format aligned to ITT requirements',
          raci: { r: 'Supply Chain Lead', a: 'Bid Manager', c: 'Bid Coordinator', i: 'Partner Leads' },
          inputs: [
            { from: 'SUP-05.1.1', artifact: 'Partner evidence briefs' }
          ],
          outputs: [
            {
              name: 'Partner case studies & CVs (validated — activity primary output)',
              format: 'Per-partner evidence pack',
              quality: [
                'All partner evidence collected and reviewed for quality and relevance',
                'Case studies adapted for this bid context — not generic partner marketing material',
                'CVs aligned to ITT format and relevant to the roles partners will fill',
                'Evidence gaps that partners could not fill documented — feeds back to SOL-10',
                'Evidence pack ready for PRD-03 (evidence assembly)'
              ]
            }
          ],
          effort: 'High',
          type: 'Parallel'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Partner case studies & CVs',
      format: 'Per-partner evidence pack (reviewed and adapted)',
      quality: [
        'All required partner evidence collected',
        'Quality and relevance reviewed — adapted for this bid',
        'Format aligned to ITT requirements',
        'Ready for PRD-03 evidence assembly'
      ]
    }
  ],

  consumers: [
    { activity: 'PRD-03', consumes: 'Partner case studies & CVs', usage: 'Evidence assembly includes partner evidence in the submission pack' },
    { activity: 'SOL-10', consumes: 'Partner case studies & CVs', usage: 'Evidence matrix updated with confirmed partner evidence (feedback loop)' }
  ]
}
```

---

## SUP-06 — Back-to-back Commercial Terms

```javascript
{
  id: 'SUP-06',
  name: 'Back-to-back commercial terms',
  workstream: 'SUP',
  phase: 'DEV',
  role: 'Supply Chain Lead',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED — associate terms, not back-to-back subcontracts. Flow-down
  //   is much simpler. May not need formal back-to-back — a simple associate engagement letter.
  output: 'Back-to-back terms agreed',
  dependencies: ['SUP-03', 'LEG-06', 'COM-04'],
  effortDays: 5,
  teamSize: 1,
  parallelisationType: 'S',

  inputs: [
    { from: 'SUP-03', artifact: 'Signed teaming agreements', note: 'The teaming framework to build on' },
    { from: 'LEG-06', artifact: 'Subcontract terms summary', note: 'Legal review of back-to-back alignment' },
    { from: 'COM-04', artifact: 'Commercial model document', note: 'Prime contract commercial terms to flow down' },
    { from: 'COM-03.1.1', artifact: 'Inter-party commercial framework', note: 'Agreed commercial framework between parties' },
    { from: 'COM-03.2.2', artifact: 'Negotiated partner pricing', note: 'Agreed partner commercial terms' }
  ],

  subs: [
    {
      id: 'SUP-06.1',
      name: 'Back-to-back Formalisation',
      description: 'Develop, negotiate, and agree back-to-back subcontract terms flowing down from the prime contract',

      tasks: [
        {
          id: 'SUP-06.1.1',
          name: 'Develop back-to-back subcontract terms flowing down from prime contract — using LEG-06 review and COM-03 commercial framework',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Legal Lead / Commercial Lead', i: 'Finance' },
          inputs: [
            { from: 'LEG-06', artifact: 'Subcontract terms summary' },
            { from: 'COM-04', artifact: 'Commercial model document' },
            { from: 'COM-03.1.1', artifact: 'Inter-party commercial framework' }
          ],
          outputs: [
            {
              name: 'Draft back-to-back subcontract terms',
              format: 'Per-partner draft subcontract',
              quality: [
                'Prime contract obligations appropriately flowed down to subcontractors',
                'Risk allocation between prime and sub is clear — aligned to LEG-06 assessment',
                'Commercial terms flow through — payment, indexation, service credits, gain share',
                'Terms are fair and proportionate — partners will accept them'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SUP-06.1.2',
          name: 'Negotiate and agree back-to-back terms with each partner',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Legal Lead / Commercial Lead', i: 'Partner Leads' },
          inputs: [
            { from: 'SUP-06.1.1', artifact: 'Draft back-to-back subcontract terms' },
            { from: 'COM-03.2.2', artifact: 'Negotiated partner pricing' }
          ],
          outputs: [
            {
              name: 'Agreed back-to-back terms per partner',
              format: 'Agreed subcontract terms (heads of terms or full subcontract)',
              quality: [
                'Terms agreed with each partner — signed or documented heads of terms',
                'No material gaps in flow-down — risk coverage is complete',
                'Partner acceptance confirmed — they will contract on these terms post-award'
              ]
            }
          ],
          effort: 'High',
          type: 'Sequential'
        },
        {
          id: 'SUP-06.1.3',
          name: 'Confirm all partner commercial terms are agreed — feeds GOV-03 (pricing governance)',
          raci: { r: 'Supply Chain Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Bid Manager' },
          inputs: [
            { from: 'SUP-06.1.2', artifact: 'Agreed back-to-back terms per partner' }
          ],
          outputs: [
            {
              name: 'Back-to-back terms agreed (activity primary output)',
              format: 'Comprehensive partner commercial status',
              quality: [
                'All partners have agreed commercial terms — no outstanding negotiations',
                'Flow-down coverage confirmed — prime contract risk is not stranded with us',
                'Status ready for GOV-03 pricing governance review'
              ]
            }
          ],
          effort: 'Low',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [
    {
      name: 'Back-to-back terms agreed',
      format: 'Agreed subcontract terms per partner',
      quality: [
        'Prime contract terms flowed down appropriately',
        'Terms negotiated and agreed with each partner',
        'Risk coverage complete — no gaps in flow-down',
        'Ready for governance review'
      ]
    }
  ],

  consumers: [
    { activity: 'GOV-03', consumes: 'Back-to-back terms agreed', usage: 'Pricing governance review confirms subcontractor terms are agreed' }
  ]
}
```

---

---

## BM — Bid Management & Programme Control: Ownership Note

> **Key distinction:** The Bid Manager owns the bid programme — process, timeline, resources, quality, risk consolidation, and communications. These are operational management activities, not solution design or commercial strategy. Many run continuously throughout the bid (duration 0 = ongoing).

---

## BM-01 — Kickoff Planning & Execution

```javascript
{
  id: 'BM-01',
  name: 'Kickoff planning & execution',
  workstream: 'BM',
  phase: 'DEV',
  role: 'Bid Manager',
  output: 'Kickoff pack: strategy summary, RACI, timeline, comms plan',
  dependencies: ['SAL-06'],
  effortDays: 3,
  teamSize: 1,
  parallelisationType: 'C',

  inputs: [
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'Win strategy, consortium, commercial framework — the strategy briefing' },
    { from: 'SAL-06.4.2', artifact: 'Bid Mandate document', note: 'Approved resources and budget' },
    { external: true, artifact: 'ITT documentation — timeline, submission deadline, key milestones' },
    { external: true, artifact: 'Corporate bid governance framework — standard RACI, reporting cadence' }
  ],

  subs: [
    {
      id: 'BM-01.1',
      name: 'Bid Kickoff',
      description: 'Establish the bid team, brief the strategy, and agree the master programme',

      tasks: [
        {
          id: 'BM-01.1.1',
          name: 'Confirm bid team structure, assign roles and RACI across all workstreams, brief the locked win strategy',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: 'Bid Board' },
          inputs: [
            { from: 'SAL-06', artifact: 'Capture plan (locked)' },
            { from: 'SAL-06.4.2', artifact: 'Bid Mandate document' }
          ],
          outputs: [
            {
              name: 'RACI matrix and bid team register',
              format: 'Structured RACI with team contact list',
              quality: [
                'Every workstream has named lead with clear accountability',
                'RACI covers all activities — no orphan activities without owners',
                'Win strategy briefed to all team members — everyone understands what we are trying to win and how',
                'Comms plan established — meeting cadence, reporting lines, escalation'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        },
        {
          id: 'BM-01.1.2',
          name: 'Agree master bid programme with milestones, review points, governance gates, and submission deadline — backward-planned from submission',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: 'Commercial Lead' },
          inputs: [
            { external: true, artifact: 'ITT documentation — timeline, submission deadline, key milestones' }
          ],
          outputs: [
            {
              name: 'Kickoff pack (activity primary output)',
              format: 'Kickoff document with RACI, programme, and comms plan',
              quality: [
                'Master bid programme backward-planned from submission deadline',
                'Key milestones identified — solution lock, pricing lock, review cycles, governance gates',
                'Critical path identified — what activities drive the timeline',
                'Programme baselined — this is the reference against which progress is tracked'
              ]
            }
          ],
          effort: 'Medium',
          type: 'Sequential'
        }
      ]
    }
  ],

  outputs: [{ name: 'Kickoff pack: strategy summary, RACI, timeline, comms plan', format: 'Kickoff document', quality: ['Team RACI established', 'Win strategy briefed', 'Master programme backward-planned', 'Comms plan agreed'] }],
  consumers: [
    { activity: 'BM-02', consumes: 'Kickoff pack', usage: 'BMP builds on kickoff outputs' },
    { activity: 'BM-03', consumes: 'Kickoff pack', usage: 'Repository setup follows team structure' },
    { activity: 'BM-04', consumes: 'Kickoff pack', usage: 'Resource tracking starts from confirmed team' },
    { activity: 'BM-06', consumes: 'Kickoff pack', usage: 'Progress reporting baseline is the master programme' }
  ]
}
```

---

## BM-02 — Bid Management Plan Production

```javascript
{
  id: 'BM-02', name: 'Bid management plan production', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Bid management plan (BMP)', dependencies: ['BM-01'], effortDays: 2, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'BM-01', artifact: 'Kickoff pack' },
    { from: 'SAL-06', artifact: 'Capture plan (locked)' },
    { external: true, artifact: 'Corporate bid management templates and standards' }
  ],

  subs: [{
    id: 'BM-02.1', name: 'BMP Production', description: 'Produce the authoritative bid management plan',
    tasks: [{
      id: 'BM-02.1.1',
      name: 'Produce bid management plan covering scope, governance, quality approach, risk management, communications, review schedule, and submission plan',
      raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: 'Legal / Partner' },
      inputs: [{ from: 'BM-01', artifact: 'Kickoff pack' }, { from: 'SAL-06', artifact: 'Capture plan (locked)' }],
      outputs: [{
        name: 'Bid management plan (activity primary output)', format: 'Comprehensive BMP document',
        quality: ['Covers: scope, governance, quality, risk, comms, reviews, submission plan', 'Review schedule mapped to master programme milestones', 'Quality approach aligned to SAL-05 scoring strategy', 'BMP accepted by Bid Director as the operational reference for the bid']
      }],
      effort: 'High', type: 'Sequential'
    }]
  }],

  outputs: [{ name: 'Bid management plan (BMP)', format: 'Comprehensive BMP', quality: ['Scope, governance, quality, risk, comms, reviews, submission all covered', 'Accepted by Bid Director'] }],
  consumers: [{ activity: 'BM-06', consumes: 'BMP', usage: 'Progress reporting follows the BMP governance framework' }]
}
```

---

## BM-03 — Document Management & Version Control Setup

```javascript
{
  id: 'BM-03', name: 'Document management & version control setup', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Repository structure, naming conventions, collaboration platform', dependencies: ['BM-01'], effortDays: 1, teamSize: 1, parallelisationType: 'C',

  inputs: [{ from: 'BM-01', artifact: 'Kickoff pack', note: 'Team structure determines access permissions' }, { external: true, artifact: 'Corporate IT platform — SharePoint, Teams, or equivalent' }],

  subs: [{
    id: 'BM-03.1', name: 'Collaboration Setup', description: 'Establish the bid collaboration infrastructure',
    tasks: [{
      id: 'BM-03.1.1',
      name: 'Establish document repository, folder structure, naming conventions, version control, access permissions, and collaboration platform',
      raci: { r: 'Bid Manager', a: 'Bid Director', c: 'IT / Bid Support', i: 'All Team' },
      inputs: [{ from: 'BM-01', artifact: 'Kickoff pack' }],
      outputs: [{
        name: 'Repository and collaboration setup (activity primary output)', format: 'Configured platform with conventions guide',
        quality: ['Folder structure mirrors workstreams and deliverables', 'Naming convention documented and communicated', 'Version control enforced — no uncontrolled document proliferation', 'Access permissions set — security-appropriate for this bid classification']
      }],
      effort: 'Low', type: 'Sequential'
    }]
  }],

  outputs: [{ name: 'Repository structure, naming conventions, collaboration platform', format: 'Configured platform', quality: ['Structure, naming, version control, access all established'] }],
  consumers: [{ activity: 'All workstreams', consumes: 'Collaboration platform', usage: 'All bid team members use the established structure' }]
}
```

---

## BM-04 — Resource Management & Tracking

```javascript
{
  id: 'BM-04', name: 'Resource management & tracking', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Resource tracker, security clearance log, availability register', dependencies: ['BM-01'], effortDays: 0, teamSize: 1, parallelisationType: 'C',

  inputs: [{ from: 'BM-01', artifact: 'Kickoff pack' }, { from: 'SAL-06.4.2', artifact: 'Bid Mandate document', note: 'Approved resource budget' }, { external: true, artifact: 'Corporate HR and security clearance systems' }],

  subs: [{
    id: 'BM-04.1', name: 'Bid Team Resource Management', description: 'Ongoing bid team resource tracking — availability, clearances, changes',
    tasks: [
      { id: 'BM-04.1.1', name: 'Confirm and mobilise full bid team — internal, partner, and contingency resources', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'HR / Resource Pool', i: 'Partner Leads' },
        inputs: [{ from: 'BM-01', artifact: 'Kickoff pack' }],
        outputs: [{ name: 'Confirmed team roster', format: 'Resource register', quality: ['Every role filled or plan to fill documented', 'Partner resources confirmed with availability', 'Contingency identified for key person risk'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'BM-04.1.2', name: 'Track resource availability, manage security clearance applications, handle resource changes throughout the bid', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'HR / Security Manager', i: 'Workstream Leads' },
        inputs: [{ from: 'BM-04.1.1', artifact: 'Confirmed team roster' }],
        outputs: [{ name: 'Resource tracker with clearance log (activity primary output — living document)', format: 'Living tracker', quality: ['Availability tracked and updated weekly', 'Clearance applications initiated and status tracked', 'Resource changes logged with impact on programme assessed'] }],
        effort: 'Low', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Resource tracker, security clearance log, availability register', format: 'Living tracker', quality: ['Team confirmed and mobilised', 'Clearance status tracked', 'Changes managed with programme impact assessed'] }],
  consumers: [{ activity: 'BM-06', consumes: 'Resource tracker', usage: 'Progress reporting includes resource status' }]
}
```

---

## BM-05 — Bid Cost Management

```javascript
{
  id: 'BM-05', name: 'Bid cost management', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Cost-to-bid tracker', dependencies: ['BM-01'], effortDays: 0, teamSize: 1, parallelisationType: 'C',

  inputs: [{ from: 'SAL-06.4.2', artifact: 'Bid Mandate document', note: 'Approved bid budget' }, { external: true, artifact: 'Corporate finance systems — timesheets, expense tracking' }],

  subs: [{
    id: 'BM-05.1', name: 'Cost-to-Bid Tracking', description: 'Track bid investment against approved budget',
    tasks: [
      { id: 'BM-05.1.1', name: 'Track bid investment against budget — actual vs forecast, by workstream, with variance reporting', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Finance', i: 'Workstream Leads' },
        inputs: [{ from: 'SAL-06.4.2', artifact: 'Bid Mandate document' }],
        outputs: [{ name: 'Cost-to-bid tracker (activity primary output — living document)', format: 'Financial tracker', quality: ['Actual spend tracked by workstream against budget', 'Forecast to complete updated weekly', 'Overruns flagged with approval workflow — Bid Director authorises overspend', 'Cost-to-bid reported to Bid Board at governance gates'] }],
        effort: 'Low', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Cost-to-bid tracker', format: 'Financial tracker', quality: ['Budget vs actual tracked', 'Overruns flagged and approved', 'Reported at governance gates'] }],
  consumers: [{ activity: 'BM-06', consumes: 'Cost-to-bid tracker', usage: 'Progress reporting includes bid investment status' }]
}
```

---

## BM-06 — Progress Reporting

```javascript
{
  id: 'BM-06', name: 'Progress reporting', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Weekly progress reports, milestone achievement reports', dependencies: ['BM-01'], effortDays: 0, teamSize: 1, parallelisationType: 'C',

  inputs: [{ from: 'BM-01', artifact: 'Kickoff pack', note: 'Master programme is the baseline' }, { from: 'BM-02', artifact: 'Bid management plan (BMP)', note: 'Reporting framework' }, { from: 'BM-04', artifact: 'Resource tracker' }, { from: 'BM-05', artifact: 'Cost-to-bid tracker' }],

  subs: [{
    id: 'BM-06.1', name: 'Programme Reporting', description: 'Weekly reporting cycle throughout the bid',
    tasks: [
      { id: 'BM-06.1.1', name: 'Conduct weekly standups with workstream leads — progress, blockers, actions, RAG status per activity', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: null },
        inputs: [{ from: 'BM-01', artifact: 'Kickoff pack' }],
        outputs: [{ name: 'Standup action log', format: 'Living action tracker', quality: ['Every workstream reports RAG status weekly', 'Blockers identified and escalated within 24 hours', 'Actions assigned with owners and deadlines'] }],
        effort: 'Low', type: 'Iterative' },
      { id: 'BM-06.1.2', name: 'Produce weekly progress reports and milestone achievement tracking — programme status against baseline', raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'Bid Board' },
        inputs: [{ from: 'BM-06.1.1', artifact: 'Standup action log' }, { from: 'BM-04', artifact: 'Resource tracker' }, { from: 'BM-05', artifact: 'Cost-to-bid tracker' }],
        outputs: [{ name: 'Weekly progress reports (activity primary output — recurring)', format: 'Progress report', quality: ['Programme status against baseline — on track, at risk, or slipped', 'Milestone achievement tracked — what is complete, what is due', 'Resource and cost status summarised', 'Key risks and escalations highlighted'] }],
        effort: 'Low', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Weekly progress reports, milestone achievement reports', format: 'Recurring reports', quality: ['Programme tracked against baseline weekly', 'Blockers escalated', 'Milestones tracked'] }],
  consumers: [{ activity: 'BM-13', consumes: 'Progress reports', usage: 'Bid risk register updated with programme risks from reporting' }]
}
```

---

## BM-07 — Quality Management Approach

```javascript
{
  id: 'BM-07', name: 'Quality management approach', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Quality plan: evaluation weighting analysis, page budgets, scoring strategy', dependencies: ['SAL-05', 'BM-01'], effortDays: 3, teamSize: 1, parallelisationType: 'C',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED emphasis — quality plan shifts. Evaluation emphasis is on
  //   team quality, methodology credibility, and past performance rather than solution depth.
  //   Review criteria should assess CV quality, methodology clarity, and evidence relevance.
  //   Page budgets may allocate more space to team credentials sections.

  inputs: [
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'Where the marks are — drives page budgets and quality focus' },
    { from: 'SAL-05.2.3', artifact: 'Per-section scoring strategy', note: 'What each response must demonstrate' },
    { from: 'BM-01', artifact: 'Kickoff pack' },
    { external: true, artifact: 'ITT documentation — submission format requirements, word/page limits' }
  ],

  subs: [{
    id: 'BM-07.1', name: 'Quality Planning', description: 'Develop the quality plan that governs how responses are written and reviewed',
    tasks: [
      { id: 'BM-07.1.1', name: 'Develop quality plan — page budgets per section based on marks concentration, writing standards, review criteria, compliance checklist', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: 'Writers' },
        inputs: [{ from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' }, { external: true, artifact: 'ITT documentation — submission format requirements, word/page limits' }],
        outputs: [{ name: 'Quality plan', format: 'Bid quality management document', quality: ['Page/word budgets allocated per section — proportionate to marks available', 'Writing standards defined — tone, voice, structure, evidence citation', 'Review criteria aligned to evaluation criteria — reviewers assess what evaluators will assess', 'Compliance checklist prepared — every mandatory requirement tracked'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'BM-07.1.2', name: 'Design review cycle schedule — pink, red, gold review timing, reviewer allocation, feedback turnaround expectations', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: 'Reviewers' },
        inputs: [{ from: 'BM-07.1.1', artifact: 'Quality plan' }, { from: 'BM-01', artifact: 'Kickoff pack' }],
        outputs: [{ name: 'Quality plan with review schedule (activity primary output)', format: 'Quality management document', quality: ['Pink/red/gold review dates set against master programme', 'Reviewers identified per section — SME alignment to content area', 'Feedback turnaround expectations set — tight enough to maintain programme', 'Review criteria distributed to reviewers before reviews begin'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Quality plan: evaluation weighting analysis, page budgets, scoring strategy', format: 'Quality management document', quality: ['Page budgets proportionate to marks', 'Writing standards defined', 'Review cycle scheduled with named reviewers'] }],
  consumers: [
    { activity: 'BM-10', consumes: 'Quality plan', usage: 'Storyboard development uses page budgets and scoring strategy' },
    { activity: 'PRD-02', consumes: 'Quality plan', usage: 'Writers use quality standards and page budgets' },
    { activity: 'PRD-05', consumes: 'Quality plan', usage: 'Pink review uses review criteria from quality plan' }
  ]
}
```

---

## BM-08 — Stakeholder & Communications Management

```javascript
{
  id: 'BM-08', name: 'Stakeholder & communications management', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Stakeholder comms plan, decision log', dependencies: ['BM-01'], effortDays: 2, teamSize: 1, parallelisationType: 'C',
  // Note: this is INTERNAL stakeholder management — bid-phase communications, decision
  // tracking, escalation. Distinct from SAL-10 (client stakeholder strategy).

  inputs: [{ from: 'BM-01', artifact: 'Kickoff pack' }, { from: 'SAL-10', artifact: 'Stakeholder relationship map & engagement plan', note: 'Client stakeholder context — BM-08 manages internal comms around it' }],

  subs: [{
    id: 'BM-08.1', name: 'Internal Stakeholder Management', description: 'Manage bid-phase communications, decisions, and escalations',
    tasks: [
      { id: 'BM-08.1.1', name: 'Establish bid-phase communications plan — internal reporting, stakeholder updates, decision log, escalation procedures', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: 'Bid Board' },
        inputs: [{ from: 'BM-01', artifact: 'Kickoff pack' }],
        outputs: [{ name: 'Comms plan and decision log (activity primary output — living document)', format: 'Communications framework with decision register', quality: ['Communications plan covers all internal stakeholders — bid team, Bid Board, executive sponsors', 'Decision log tracks all material decisions with rationale and owner', 'Escalation procedures defined — what gets escalated, to whom, in what timeframe'] }],
        effort: 'Medium', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Stakeholder comms plan, decision log', format: 'Living communications framework', quality: ['Internal comms plan established', 'Decision log maintained', 'Escalation procedures defined'] }],
  consumers: [{ activity: 'BM-06', consumes: 'Decision log', usage: 'Progress reporting references key decisions' }]
}
```

---

## BM-09 — Competitive Dialogue Management (if applicable)

```javascript
{
  id: 'BM-09', name: 'Competitive dialogue management (if applicable)', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Dialogue prep packs, session records, iteration tracker per round', dependencies: ['SAL-06', 'SOL-03'], effortDays: 0, teamSize: 2, parallelisationType: 'P',
  // Note: only activated for competitive dialogue or competitive procedure with negotiation
  // procurement routes. Set during bid setup based on procurement type.

  inputs: [
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'Win strategy and negotiation positions' },
    { from: 'SAL-07', artifact: 'Clarification question register (prioritised)', note: 'Strategic questions and competitive gaming approach' },
    { from: 'SOL-03', artifact: 'Target operating model', note: 'Solution to present and iterate' },
    { from: 'LEG-01.2.2', artifact: 'Contract markup with positions log', note: 'Negotiation positions for contract discussions' }
  ],

  subs: [{
    id: 'BM-09.1', name: 'Competitive Dialogue', description: 'Manage dialogue sessions — preparation, execution, recording, and solution iteration per round',
    tasks: [
      { id: 'BM-09.1.1', name: 'Prepare dialogue packs per round — presentation materials, discussion topics, questions, negotiation positions, team briefing', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Solution Architect / Commercial Lead / Legal Lead', i: 'Capture Lead' },
        inputs: [{ from: 'SAL-06', artifact: 'Capture plan (locked)' }, { from: 'SOL-03', artifact: 'Target operating model' }, { from: 'LEG-01.2.2', artifact: 'Contract markup with positions log' }],
        outputs: [{ name: 'Dialogue preparation packs', format: 'Per-round preparation document', quality: ['Presentation materials aligned to win strategy and client feedback from previous rounds', 'Discussion topics and questions prepared — strategic, not reactive', 'Negotiation positions confirmed with fallbacks per LEG-01', 'Team briefed on objectives and boundaries for each session'] }],
        effort: 'High', type: 'Iterative' },
      { id: 'BM-09.1.2', name: 'Record dialogue outcomes, track iterations, and update solution/commercial per round', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All attending leads', i: 'Bid Team' },
        inputs: [{ from: 'BM-09.1.1', artifact: 'Dialogue preparation packs' }],
        outputs: [{ name: 'Dialogue session records and iteration tracker (activity primary output)', format: 'Session notes with action register', quality: ['Every session recorded — what was discussed, agreed, and action items', 'Client feedback captured and distributed to relevant workstreams', 'Solution and commercial iterations tracked per round — what changed and why', 'Impact on programme and timeline assessed per iteration'] }],
        effort: 'High', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Dialogue prep packs, session records, iteration tracker', format: 'Per-round dialogue management pack', quality: ['Sessions prepared with strategic intent', 'Outcomes recorded and distributed', 'Iterations tracked with programme impact'] }],
  consumers: [
    { activity: 'SOL-03', consumes: 'Dialogue outcomes', usage: 'Solution design iterated based on client feedback (feedback loop)' },
    { activity: 'COM-04', consumes: 'Dialogue outcomes', usage: 'Commercial model iterated based on contract discussions' }
  ]
}
```

---

## BM-10 — Storyboard Development & Sign-off

```javascript
{
  id: 'BM-10', name: 'Storyboard development & sign-off', workstream: 'BM', phase: 'PROD', role: 'Bid Manager',
  output: 'Approved storyboard — METHODOLOGY GATE', dependencies: ['SAL-06', 'SAL-05', 'SOL-11'], effortDays: 5, teamSize: 2, parallelisationType: 'P',
  // METHODOLOGY GATE — storyboard must be approved before section drafting (PRD-02) begins.
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED — storyboard structure is fundamentally different.
  //   CV-led sections, methodology-led sections, not solution-narrative sections.
  //   Writer briefs focus on team credentials and methodology description, not solution depth.
  //   Guidance: "For consulting, storyboard around: team, methodology, case studies, approach."

  inputs: [
    { from: 'SOL-11', artifact: 'Solution design pack (locked & assured)', note: 'The locked solution to structure the response around' },
    { from: 'SAL-04', artifact: 'Win theme document', note: 'Win themes and messaging to integrate per section' },
    { from: 'SAL-05.2.4', artifact: 'Win theme integration map', note: 'Which themes land in which sections' },
    { from: 'SAL-05.2.3', artifact: 'Per-section scoring strategy', note: 'Target score and content requirements per section' },
    { from: 'BM-07', artifact: 'Quality plan', note: 'Page budgets and writing standards' },
    { external: true, artifact: 'ITT documentation — response structure, question wording, evaluation criteria per question' }
  ],

  subs: [
    {
      id: 'BM-10.1', name: 'Storyboard Design', description: 'Develop the response structure per section — what each section will say, how, and who writes it',
      tasks: [
        { id: 'BM-10.1.1', name: 'Develop storyboard per response section — section structure, key messages, win theme integration, evidence placement, page allocation, writer assignment', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Solution Architect / Capture Lead / Workstream Leads', i: 'Writers' },
          inputs: [{ from: 'SOL-11', artifact: 'Solution design pack (locked & assured)' }, { from: 'SAL-05.2.4', artifact: 'Win theme integration map' }, { from: 'SAL-05.2.3', artifact: 'Per-section scoring strategy' }, { from: 'BM-07', artifact: 'Quality plan' }],
          outputs: [{ name: 'Draft storyboards per section', format: 'Per-section storyboard template', quality: ['Every response section has a storyboard — structure, key messages, evidence, win themes', 'Writer assigned per section with confirmed availability', 'Page budget allocated per section from quality plan', 'Win themes placed per SAL-05 integration map — differentiators land where marks are'] }],
          effort: 'High', type: 'Parallel' },
        { id: 'BM-10.1.2', name: 'Brief each writer using storyboard — confirm scope, win themes, scoring target, page budget, evidence requirements, and deadline', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: 'Writers' },
          inputs: [{ from: 'BM-10.1.1', artifact: 'Draft storyboards per section' }],
          outputs: [{ name: 'Writer briefs issued', format: 'Per-writer briefing pack', quality: ['Every writer has a clear brief — what to write, why, how to score, by when', 'Win themes and scoring strategy communicated — not just "answer the question"', 'Evidence and credentials to cite identified per section'] }],
          effort: 'Medium', type: 'Parallel' }
      ]
    },
    {
      id: 'BM-10.2', name: 'Storyboard Approval', description: 'Review and approve the storyboard as the baseline for drafting',
      tasks: [
        { id: 'BM-10.2.1', name: 'Review and approve storyboard — Bid Director sign-off, methodology gate passed, drafting can begin', raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Solution Architect / Capture Lead', i: 'Bid Manager' },
          inputs: [{ from: 'BM-10.1.1', artifact: 'Draft storyboards per section' }, { from: 'BM-10.1.2', artifact: 'Writer briefs issued' }],
          outputs: [{ name: 'Approved storyboard (activity primary output — METHODOLOGY GATE)', format: 'Approved storyboard pack', quality: ['All sections have approved storyboards — no section without a plan', 'Win strategy alignment confirmed — solution, themes, and scoring strategy coherent in the storyboard', 'Bid Director sign-off recorded', 'Methodology gate passed — PRD-02 (section drafting) can now begin'] }],
          effort: 'Medium', type: 'Sequential' }
      ]
    }
  ],

  outputs: [{ name: 'Approved storyboard — METHODOLOGY GATE', format: 'Approved storyboard pack', quality: ['Every section has storyboard with structure, messages, themes, evidence, writer, budget', 'Bid Director approved', 'Methodology gate passed — drafting can begin'] }],
  consumers: [
    { activity: 'PRD-02', consumes: 'Approved storyboard', usage: 'Section drafting follows the storyboard — writers build from the approved plan' },
    { activity: 'PRD-05', consumes: 'Approved storyboard', usage: 'Pink review assesses drafts against the storyboard' }
  ]
}
```

---

## BM-11 — Hot Debrief (Post-submission)

```javascript
{
  id: 'BM-11', name: 'Hot debrief (post-submission)', workstream: 'BM', phase: 'POST', role: 'Bid Manager',
  output: 'Hot debrief notes, immediate lessons log', dependencies: ['PRD-09'], effortDays: 1, teamSize: 1, parallelisationType: 'C',

  inputs: [{ external: true, artifact: 'Submission confirmation record' }, { external: true, artifact: 'Team availability for debrief within 48 hours' }],

  subs: [{
    id: 'BM-11.1', name: 'Submission Debrief', description: 'Capture immediate lessons while the bid is fresh',
    tasks: [{
      id: 'BM-11.1.1', name: 'Conduct internal hot debrief within 48 hours of submission — what went well, what didn\'t, immediate process lessons, team feedback',
      raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: null },
      inputs: [{ external: true, artifact: 'Submission confirmation record' }],
      outputs: [{ name: 'Hot debrief notes (activity primary output)', format: 'Structured debrief notes', quality: ['Conducted within 48 hours — while memory is fresh', 'What went well captured — repeat these things', 'What didn\'t go well captured — honest, no blame', 'Immediate process improvement suggestions noted'] }],
      effort: 'Low', type: 'Sequential'
    }]
  }],

  outputs: [{ name: 'Hot debrief notes, immediate lessons log', format: 'Debrief notes', quality: ['Within 48 hours', 'Honest assessment', 'Improvement suggestions captured'] }],
  consumers: [{ activity: 'BM-12', consumes: 'Hot debrief notes', usage: 'Lessons learned builds on immediate debrief' }]
}
```

---

## BM-12 — Lessons Learned & Knowledge Capture

```javascript
{
  id: 'BM-12', name: 'Lessons learned & knowledge capture', workstream: 'BM', phase: 'POST', role: 'Bid Manager',
  output: 'Lessons report, content library updates, process improvement actions', dependencies: ['BM-11'], effortDays: 3, teamSize: 1, parallelisationType: 'C',

  inputs: [{ from: 'BM-11', artifact: 'Hot debrief notes' }, { external: true, artifact: 'Client debrief feedback (when available — may be weeks after submission)' }, { external: true, artifact: 'Submitted proposal for reference' }],

  subs: [{
    id: 'BM-12.1', name: 'Formal Debrief & Knowledge Capture', description: 'Client debrief, internal lessons learned, and content library update',
    tasks: [
      { id: 'BM-12.1.1', name: 'Request and attend formal client debrief — capture scoring, evaluator feedback, and improvement areas', raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Commercial Lead', i: 'Bid Manager' },
        inputs: [{ external: true, artifact: 'Client debrief feedback' }],
        outputs: [{ name: 'Client debrief notes with scoring', format: 'Structured debrief record', quality: ['Client scoring per section captured where disclosed', 'Evaluator feedback documented — what scored well, what scored poorly', 'Competitor intelligence captured — what the winner did differently (if disclosed)'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'BM-12.1.2', name: 'Conduct internal lessons learned review with full bid team — process, strategy, solution, commercial, and team performance', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: null },
        inputs: [{ from: 'BM-11', artifact: 'Hot debrief notes' }, { from: 'BM-12.1.1', artifact: 'Client debrief notes with scoring' }],
        outputs: [{ name: 'Lessons learned report', format: 'Structured lessons report', quality: ['Process lessons — what worked and what to change', 'Strategy lessons — was the win strategy right?', 'Solution lessons — was the solution competitive?', 'Improvement actions identified, assigned, and tracked'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'BM-12.1.3', name: 'Update content library with new case studies, evidence, and reusable content from this bid', raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'SMEs', i: 'All' },
        inputs: [{ from: 'BM-12.1.2', artifact: 'Lessons learned report' }],
        outputs: [{ name: 'Content library updates (activity primary output)', format: 'Updated library entries', quality: ['New case studies from this engagement added to library', 'Reusable content identified and catalogued', 'Evidence that proved effective flagged for future bids'] }],
        effort: 'Low', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Lessons report, content library updates, process improvement actions', format: 'Lessons package', quality: ['Client feedback captured', 'Internal lessons documented', 'Content library updated', 'Improvement actions assigned'] }],
  consumers: [{ activity: 'Bid Library (future product)', consumes: 'Content library updates', usage: 'Bid Library product ingests new evidence and reusable content' }]
}
```

---

## BM-13 — Bid Risk & Assumptions Register

```javascript
{
  id: 'BM-13', name: 'Bid risk & assumptions register', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Bid risk register (process risks, scheduling assumptions, resource risks)', dependencies: [], effortDays: 0, teamSize: 1, parallelisationType: 'C',
  // Note: this is the BID-LEVEL consolidated risk register — the Bid Manager's view.
  // Distinct from SOL-12 (solution risk), COM-07 (commercial risk), DEL-01 (delivery risk).
  // BM-13 consolidates all of these PLUS bid process risks (scheduling, resourcing, quality).

  inputs: [
    { from: 'SOL-12', artifact: 'Solution risk register' },
    { from: 'COM-07', artifact: 'Commercial risk register' },
    { from: 'DEL-01', artifact: 'Delivery risk & assumptions register' },
    { from: 'DEL-06', artifact: 'Mitigated risk register (assured)' },
    { from: 'BM-06', artifact: 'Weekly progress reports', note: 'Programme risks surfaced through reporting' }
  ],

  subs: [{
    id: 'BM-13.1', name: 'Bid Risk Consolidation', description: 'The single consolidated bid risk register — all risks from all workstreams plus bid process risks',
    tasks: [
      { id: 'BM-13.1.1', name: 'Consolidate all workstream risk registers into the single bid risk register — solution, commercial, delivery, legal, plus bid process risks', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: null },
        inputs: [{ from: 'SOL-12', artifact: 'Solution risk register' }, { from: 'COM-07', artifact: 'Commercial risk register' }, { from: 'DEL-01', artifact: 'Delivery risk & assumptions register' }],
        outputs: [{ name: 'Consolidated bid risk register', format: 'Comprehensive risk register', quality: ['All workstream risks consolidated', 'Bid process risks added — scheduling, resourcing, quality, submission logistics', 'Duplicates removed, cross-cutting risks identified', 'Single view for Bid Director and governance gates'] }],
        effort: 'Medium', type: 'Iterative' },
      { id: 'BM-13.1.2', name: 'Maintain and prepare for governance — living document, updated at key milestones, governance-ready summary', raci: { r: 'Bid Manager', a: 'Bid Director', c: null, i: 'All Workstream Leads' },
        inputs: [{ from: 'BM-13.1.1', artifact: 'Consolidated bid risk register' }, { from: 'DEL-06', artifact: 'Mitigated risk register (assured)' }],
        outputs: [{ name: 'Bid risk register (activity primary output — living document)', format: 'Governance-ready risk register', quality: ['Updated at key milestones — post solution lock, post pricing lock, pre-governance', 'Top bid risks summarised for executive audience', 'Feeds all governance gates as entry criterion'] }],
        effort: 'Low', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Bid risk register', format: 'Consolidated governance-ready register', quality: ['All workstream risks consolidated', 'Bid process risks included', 'Living document updated at milestones', 'Governance-ready'] }],
  consumers: [
    { activity: 'GOV-02', consumes: 'Bid risk register', usage: 'Solution & strategy review examines risk position' },
    { activity: 'GOV-03', consumes: 'Bid risk register', usage: 'Pricing & risk review examines consolidated risk position' }
  ]
}
```

---

## BM-14 — Clarification Submission & Response Management

```javascript
{
  id: 'BM-14', name: 'Clarification submission & response management', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Clarification response log with impact assessment', dependencies: ['SAL-07'], effortDays: 5, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'SAL-07', artifact: 'Clarification question register (prioritised)', note: 'The approved questions with strategic timing plan' },
    { external: true, artifact: 'Procurement portal access and submission procedures' }
  ],

  subs: [{
    id: 'BM-14.1', name: 'Clarification Operations', description: 'Operationally manage the clarification submission and response process',
    tasks: [
      { id: 'BM-14.1.1', name: 'Submit clarification questions per SAL-07 strategy and timing plan — manage portal submissions, track deadlines', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
        inputs: [{ from: 'SAL-07', artifact: 'Clarification question register (prioritised)' }],
        outputs: [{ name: 'Submitted questions log', format: 'Tracking register', quality: ['All approved questions submitted on time per the timing plan', 'Submission confirmation recorded per question', 'Any questions held back per strategic timing plan tracked'] }],
        effort: 'Low', type: 'Sequential' },
      { id: 'BM-14.1.2', name: 'Track and distribute clarification responses — log all responses, distribute to relevant workstreams, flag responses that change assumptions', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: null },
        inputs: [{ from: 'BM-14.1.1', artifact: 'Submitted questions log' }],
        outputs: [{ name: 'Clarification response log (activity primary output)', format: 'Comprehensive response tracker', quality: ['Every response logged — date, question reference, response summary, impact assessment', 'Responses distributed to relevant workstream leads within 24 hours', 'Responses that change assumptions or requirements flagged for BM-15 impact analysis', 'Client-published responses from other bidders also captured and assessed'] }],
        effort: 'Medium', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Clarification response log with impact assessment', format: 'Response tracker', quality: ['All responses logged and distributed', 'Impact flagged for analysis', 'Competitor questions captured if published'] }],
  consumers: [{ activity: 'BM-15', consumes: 'Clarification response log', usage: 'Impact analysis triages responses that affect the bid' }]
}
```

---

## BM-15 — Clarification Impact Analysis & Workstream Updates

```javascript
{
  id: 'BM-15', name: 'Clarification impact analysis & workstream updates', workstream: 'BM', phase: 'DEV', role: 'Bid Manager',
  output: 'Updated requirements/assumptions across workstreams', dependencies: ['BM-14'], effortDays: 3, teamSize: 2, parallelisationType: 'P',

  inputs: [
    { from: 'BM-14', artifact: 'Clarification response log', note: 'Responses flagged as having impact' },
    { from: 'SOL-01', artifact: 'Requirements interpretation document', note: 'Current requirements baseline to assess against' }
  ],

  subs: [{
    id: 'BM-15.1', name: 'Impact Triage', description: 'Triage clarification responses that affect the bid and drive workstream updates',
    tasks: [
      { id: 'BM-15.1.1', name: 'Triage flagged clarification responses — assess impact on solution, commercial, delivery, legal, and compliance workstreams', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: null },
        inputs: [{ from: 'BM-14', artifact: 'Clarification response log' }],
        outputs: [{ name: 'Clarification impact assessment', format: 'Per-response impact record', quality: ['Each flagged response assessed for impact — which workstreams affected, what changes', 'Impact categorised: no impact, minor update, significant rework, showstopper', 'Affected compliance requirements and response items flagged in the product'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'BM-15.1.2', name: 'Drive workstream updates — ensure affected solution, commercial, or legal positions are updated and track resolution', raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Affected Workstream Leads', i: null },
        inputs: [{ from: 'BM-15.1.1', artifact: 'Clarification impact assessment' }],
        outputs: [{ name: 'Updated requirements/assumptions across workstreams (activity primary output)', format: 'Impact resolution tracker', quality: ['Every impacted item has an assigned owner and resolution action', 'Updates tracked to completion — no flagged-but-unresolved items at submission', 'Programme impact assessed — does the clarification change the timeline?', 'Unreviewed clarification impacts shown as action items in the product workspace'] }],
        effort: 'High', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Updated requirements/assumptions across workstreams', format: 'Impact resolution tracker', quality: ['All flagged responses triaged', 'Workstream updates assigned and tracked', 'No unresolved impacts at submission'] }],
  consumers: [
    { activity: 'SOL-01', consumes: 'Updated requirements', usage: 'Requirements interpretation updated with clarification responses (feedback loop)' },
    { activity: 'BM-13', consumes: 'Clarification impact assessment', usage: 'Bid risk register updated with clarification-driven risks' }
  ]
}
```

---

## BM-16 — Win Strategy Refresh (Post-ITT)

```javascript
{
  id: 'BM-16', name: 'Win strategy refresh (post-ITT)', workstream: 'BM', phase: 'DEV', role: 'Bid Director',
  output: 'Updated win strategy, refreshed PWIN score', dependencies: ['BM-01', 'SOL-01'], effortDays: 2, teamSize: 1, parallelisationType: 'S',
  // Note: NEW activity from playbook B4 (Qualification). Formal mid-bid recheck:
  // is the win strategy still valid after ITT analysis and early solution work?
  // Has the competitive landscape changed? Should we still bid?

  inputs: [
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'The original strategy to revalidate' },
    { from: 'SOL-01', artifact: 'Requirements interpretation document', note: 'What we now know about the requirement' },
    { from: 'SAL-06.1.1', artifact: 'Capture effectiveness assessment', note: 'How well capture influenced the ITT' },
    { from: 'BM-15', artifact: 'Updated requirements/assumptions across workstreams', note: 'Clarification responses that may have changed the picture' },
    { external: true, artifact: 'Updated competitive intelligence — any new information about competitors since SAL-06' }
  ],

  subs: [{
    id: 'BM-16.1', name: 'Strategy Revalidation', description: 'Formal mid-bid recheck of the win strategy',
    tasks: [
      { id: 'BM-16.1.1', name: 'Refresh win strategy assessment — has anything changed since SAL-06 that affects our competitive position, win themes, or approach?', raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Capture Lead / Solution Architect / Commercial Lead', i: 'Bid Manager' },
        inputs: [{ from: 'SAL-06', artifact: 'Capture plan (locked)' }, { from: 'SOL-01', artifact: 'Requirements interpretation document' }, { external: true, artifact: 'Updated competitive intelligence' }],
        outputs: [{ name: 'Win strategy refresh assessment', format: 'Structured revalidation', quality: ['Each element of the win strategy assessed: still valid, needs adjustment, or invalidated', 'Competitive landscape rechecked — any new intelligence?', 'Win themes revalidated against actual requirements from SOL-01'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'BM-16.1.2', name: 'Refresh PWIN score and confirm continue/stop decision — formal re-qualification checkpoint', raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Capture Lead', i: 'Bid Board' },
        inputs: [{ from: 'BM-16.1.1', artifact: 'Win strategy refresh assessment' }],
        outputs: [{ name: 'Updated win strategy and refreshed PWIN score (activity primary output)', format: 'Updated strategy document with PWIN', quality: ['PWIN score refreshed with current intelligence — has it improved or deteriorated?', 'Continue/stop recommendation stated with rationale', 'If strategy adjustments needed, updated win strategy documented and communicated to bid team', 'Win Strategy Re-confirmation recorded — formal checkpoint passed'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Updated win strategy, refreshed PWIN score', format: 'Strategy update with PWIN', quality: ['Strategy revalidated against current intelligence', 'PWIN refreshed', 'Continue/stop decision confirmed'] }],
  consumers: [
    { activity: 'BM-10', consumes: 'Updated win strategy', usage: 'Storyboard development uses the refreshed strategy if adjustments were made' },
    { activity: 'SAL-04', consumes: 'Updated win strategy', usage: 'Win themes refined if strategy refresh identified changes needed (feedback loop)' }
  ]
}
```

---

---

## PRD — Proposal Production: Pipeline Note

> **Production pipeline:** Compliance (PRD-01) → Storyboard (BM-10) → **Pink review of storyboard (PRD-05)** → Drafting (PRD-02) + Evidence assembly (PRD-03) + Pricing response (PRD-04) → **Red review of draft (PRD-06)** → Revisions → **Gold review of final (PRD-07)** → QA & formatting (PRD-08) → Submit (PRD-09).
> All activities managed by the Bid Manager but RACI reflects who does the work: writers write, reviewers review, DTP formats.

---

## PRD-01 — Compliance Matrix & Requirements Mapping

```javascript
{
  id: 'PRD-01', name: 'Compliance matrix & requirements mapping', workstream: 'PRD', phase: 'PROD', role: 'Bid Manager',
  output: 'Compliance matrix (live)', dependencies: ['SOL-01'], effortDays: 3, teamSize: 1, parallelisationType: 'S',

  inputs: [
    { from: 'SOL-01', artifact: 'Requirements interpretation document' },
    { external: true, artifact: 'ITT documentation — all mandatory and scored requirements' }
  ],

  subs: [{
    id: 'PRD-01.1', name: 'Compliance Assurance', description: 'Map every ITT requirement to the response and maintain compliance position throughout the bid',
    tasks: [
      { id: 'PRD-01.1.1', name: 'Map every ITT mandatory and scored requirement to the response section that addresses it — identify compliance position per requirement',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Legal / Solution Architect', i: 'Workstream Leads' },
        inputs: [{ from: 'SOL-01', artifact: 'Requirements interpretation document' }, { external: true, artifact: 'ITT documentation — all mandatory and scored requirements' }],
        outputs: [{ name: 'Compliance matrix (draft)', format: 'Requirements-to-response mapping', quality: ['Every mandatory requirement mapped to a response section', 'Compliance position per requirement: compliant, partial, non-compliant, not yet assessed', 'Non-compliant items flagged with risk and mitigation approach', 'Matrix structured to match client expected format if specified'] }],
        effort: 'High', type: 'Sequential' },
      { id: 'PRD-01.1.2', name: 'Maintain compliance matrix as a living document throughout the bid — update as solution, commercial, and clarification responses evolve',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Workstream Leads', i: null },
        inputs: [{ from: 'PRD-01.1.1', artifact: 'Compliance matrix (draft)' }],
        outputs: [{ name: 'Compliance matrix (live — activity primary output)', format: 'Living compliance register', quality: ['Updated at key milestones — post solution lock, post pricing, pre-governance', 'Non-compliant items tracked to resolution', 'Compliance status reported at governance gates', 'Final compliance check feeds PRD-09 (submission)'] }],
        effort: 'Low', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Compliance matrix (live)', format: 'Living requirements-to-response mapping', quality: ['All requirements mapped', 'Compliance position tracked', 'Non-compliance flagged and mitigated'] }],
  consumers: [
    { activity: 'PRD-09', consumes: 'Compliance matrix', usage: 'Final compliance check before submission' },
    { activity: 'GOV-05', consumes: 'Compliance matrix', usage: 'Final submission authority requires compliance confirmation' }
  ]
}
```

---

## PRD-02 — Section Drafting & Content Assembly

```javascript
{
  id: 'PRD-02', name: 'Section drafting & content assembly', workstream: 'PRD', phase: 'PROD', role: 'Bid Manager',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED — writing shifts from solution narrative to methodology
  //   description, team credentials, case studies. Executive summary is approach-led.
  //   Writers produce different types of content — less technical depth, more methodology
  //   credibility and team evidence.
  output: 'Draft response sections', dependencies: ['PRD-05', 'SOL-11'], effortDays: 60, teamSize: 4, parallelisationType: 'P',
  // Note: 60 person-days, team of 4 — the largest production activity.
  // Writers produce drafts against the pink-reviewed storyboard briefs.

  inputs: [
    { from: 'PRD-05', artifact: 'Pink review scorecard & actions', note: 'Storyboard approved via pink review — writers build from reviewed plan' },
    { from: 'BM-10', artifact: 'Approved storyboard', note: 'Per-section storyboard and writer briefs' },
    { from: 'SOL-11', artifact: 'Solution design pack (locked & assured)', note: 'The authoritative solution to write about' },
    { from: 'SAL-04', artifact: 'Win theme document', note: 'Win themes and messaging to weave through responses' },
    { from: 'BM-07', artifact: 'Quality plan', note: 'Page budgets, writing standards, review criteria' }
  ],

  subs: [{
    id: 'PRD-02.1', name: 'Response Drafting', description: 'Writers produce section drafts in parallel against storyboard briefs',
    tasks: [
      { id: 'PRD-02.1.1', name: 'Produce quality/technical response section drafts — each writer follows their storyboard brief, integrates win themes, cites evidence, stays within page budget',
        raci: { r: 'Writers / SMEs (per section)', a: 'Workstream Leads', c: 'Solution Architect', i: 'Bid Manager' },
        inputs: [{ from: 'BM-10', artifact: 'Approved storyboard' }, { from: 'SOL-11', artifact: 'Solution design pack (locked & assured)' }, { from: 'SAL-04', artifact: 'Win theme document' }],
        outputs: [{ name: 'Quality/technical section drafts', format: 'Per-section draft documents', quality: ['Each section follows its storyboard structure and brief', 'Win themes integrated per the integration map', 'Evidence and credentials cited where specified', 'Within page/word budget per BM-07 quality plan', 'Written to score — addresses evaluation criteria, not just answers the question'] }],
        effort: 'High', type: 'Parallel' },
      { id: 'PRD-02.1.2', name: 'Produce executive summary and overarching narrative — ties the response together, leads with win strategy',
        raci: { r: 'Senior Bid Writer', a: 'Bid Director', c: 'Capture Lead', i: 'Bid Manager' },
        inputs: [{ from: 'SAL-04', artifact: 'Win theme document' }, { from: 'SOL-11', artifact: 'Solution design pack (locked & assured)' }],
        outputs: [{ name: 'Executive summary draft', format: 'Draft document', quality: ['Leads with win strategy and key differentiators', 'Tells the story of why we should win — not a summary of what follows', 'Aligned to buyer values and evaluation priorities'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'PRD-02.1.3', name: 'Bid Manager tracks drafting progress, manages writer issues, ensures programme adherence',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Writers', i: null },
        inputs: [{ from: 'BM-07', artifact: 'Quality plan' }],
        outputs: [{ name: 'Draft response sections (activity primary output)', format: 'Complete set of draft sections', quality: ['All sections drafted to at least first-draft standard', 'Progress tracked against programme — no sections missing deadline without escalation', 'Sections ready for red review (PRD-06)'] }],
        effort: 'Low', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Draft response sections', format: 'Complete draft response', quality: ['All sections drafted against storyboard', 'Win themes integrated', 'Evidence cited', 'Page budgets met', 'Ready for red review'] }],
  consumers: [
    { activity: 'PRD-06', consumes: 'Draft response sections', usage: 'Red review evaluates the near-complete drafts' }
  ]
}
```

---

## PRD-03 — Evidence, Case Studies & CV Assembly

```javascript
{
  id: 'PRD-03', name: 'Evidence, case studies & CV assembly', workstream: 'PRD', phase: 'PROD', role: 'Bid Coordinator',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED — evidence pack is CV-dominated. Case studies focus on
  //   advisory outcomes, not service delivery. The assembly task is fundamentally "package
  //   the CVs and case studies" — the team IS the evidence.
  output: 'Evidence pack', dependencies: ['SUP-05', 'SOL-10'], effortDays: 16, teamSize: 2, parallelisationType: 'P',

  inputs: [
    { from: 'SOL-10', artifact: 'Evidence requirements matrix', note: 'What evidence is needed per section' },
    { from: 'SOL-10.2.1', artifact: 'Adapted evidence pack (existing)', note: 'Evidence already sourced and adapted' },
    { from: 'SOL-10.2.2', artifact: 'Evidence commission register', note: 'New evidence being produced — track delivery' },
    { from: 'SUP-05', artifact: 'Partner case studies & CVs', note: 'Partner evidence' },
    { external: true, artifact: 'ITT documentation — evidence format requirements, CV templates, case study templates' }
  ],

  subs: [{
    id: 'PRD-03.1', name: 'Evidence Assembly', description: 'Compile, format, and quality-assure the complete evidence pack for submission',
    tasks: [
      { id: 'PRD-03.1.1', name: 'Compile all evidence items — case studies, CVs, credentials, certifications, reference letters — from SOL-10 sourcing and SUP-05 partner evidence',
        raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'SMEs / Partner Leads', i: 'Writers' },
        inputs: [{ from: 'SOL-10.2.1', artifact: 'Adapted evidence pack (existing)' }, { from: 'SUP-05', artifact: 'Partner case studies & CVs' }, { from: 'SOL-10.2.2', artifact: 'Evidence commission register' }],
        outputs: [{ name: 'Compiled evidence items', format: 'Per-item evidence documents', quality: ['All items from SOL-10 evidence matrix accounted for — sourced, commissioned, or gap documented', 'Commissioned evidence that has been delivered collected and reviewed', 'Outstanding items tracked with delivery date'] }],
        effort: 'Medium', type: 'Parallel' },
      { id: 'PRD-03.1.2', name: 'Format evidence to ITT requirements and quality-assure — consistent style, correct templates, word limits, anonymisation where required',
        raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'DTP', i: null },
        inputs: [{ from: 'PRD-03.1.1', artifact: 'Compiled evidence items' }, { external: true, artifact: 'ITT documentation — evidence format requirements' }],
        outputs: [{ name: 'Evidence pack (activity primary output)', format: 'Submission-ready evidence pack', quality: ['All evidence formatted to ITT requirements — correct templates, within word limits', 'Client-sensitive information anonymised where required', 'Evidence cross-referenced to response sections — reviewers can trace claims to evidence', 'Evidence pack complete and ready for red review alongside response drafts'] }],
        effort: 'High', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Evidence pack', format: 'Submission-ready evidence documents', quality: ['All evidence compiled, formatted, and quality-assured', 'Gaps documented', 'Cross-referenced to response sections'] }],
  consumers: [{ activity: 'PRD-06', consumes: 'Evidence pack', usage: 'Red review includes evidence alongside response drafts' }]
}
```

---

## PRD-04 — Pricing Schedules & Commercial Response

```javascript
{
  id: 'PRD-04', name: 'Pricing schedules & commercial response', workstream: 'PRD', phase: 'PROD', role: 'Commercial Lead',
  // ARCHETYPE NOTES:
  // Technology/Digital: MODIFIED — milestone-based pricing schedules, not annual service charge.
  // Consulting/Advisory: MODIFIED — rate card / day-rate schedules, much simpler pricing documents.
  //   Commercial narrative is lighter — "here are our rates" not complex pricing explanation.
  output: 'Pricing response documents', dependencies: ['COM-06'], effortDays: 5, teamSize: 1, parallelisationType: 'S',
  // Note: COM-06 locks the pricing model and populates schedules.
  // PRD-04 packages them for submission — formatting, compliance check, assembly with the rest of the response.

  inputs: [
    { from: 'COM-06', artifact: 'Pricing model (locked & assured)', note: 'The locked pricing schedules' },
    { from: 'COM-04', artifact: 'Commercial model document', note: 'Commercial narrative to accompany pricing' },
    { external: true, artifact: 'ITT documentation — pricing submission format, required supporting narrative' }
  ],

  subs: [{
    id: 'PRD-04.1', name: 'Pricing Response Production', description: 'Package the locked pricing for submission',
    tasks: [
      { id: 'PRD-04.1.1', name: 'Produce commercial response narrative — explain the pricing approach, payment mechanism, value proposition in the format the ITT requires',
        raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Finance / Bid Manager', i: 'Legal' },
        inputs: [{ from: 'COM-04', artifact: 'Commercial model document' }, { external: true, artifact: 'ITT documentation — pricing submission format' }],
        outputs: [{ name: 'Commercial response narrative', format: 'Written commercial response sections', quality: ['Explains the pricing approach clearly for evaluators', 'Value-for-money argument articulated', 'Payment mechanism and commercial terms described in evaluator-friendly language'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'PRD-04.1.2', name: 'Assemble and format pricing response documents — schedules, narrative, supporting documents packaged for submission',
        raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'Commercial Lead', i: null },
        inputs: [{ from: 'COM-06', artifact: 'Pricing model (locked & assured)' }, { from: 'PRD-04.1.1', artifact: 'Commercial response narrative' }],
        outputs: [{ name: 'Pricing response documents (activity primary output)', format: 'Submission-ready pricing pack', quality: ['Pricing schedules formatted per ITT requirements', 'Commercial narrative assembled with pricing', 'Cross-references between narrative and schedules confirmed', 'Ready for red/gold review alongside quality response'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Pricing response documents', format: 'Submission-ready pricing pack', quality: ['Pricing schedules formatted', 'Commercial narrative written', 'Ready for review'] }],
  consumers: [{ activity: 'PRD-06', consumes: 'Pricing response documents', usage: 'Red review includes pricing alongside quality response' }]
}
```

---

## PRD-05 — Pink Review (Storyboard Review)

```javascript
{
  id: 'PRD-05', name: 'Pink review (storyboard/outline)', workstream: 'PRD', phase: 'PROD', role: 'Bid Manager',
  output: 'Pink review scorecard & actions', dependencies: ['BM-10'], effortDays: 3, teamSize: 1, parallelisationType: 'C',
  // Note: the pink review is a review of the STORYBOARD — the plan for what will be
  // written. It validates the response structure, key messages, win theme placement,
  // and evidence strategy BEFORE writers invest time drafting.
  // This is NOT a review of early drafts.

  inputs: [
    { from: 'BM-10', artifact: 'Approved storyboard', note: 'The storyboards to review' },
    { from: 'SAL-05.2.3', artifact: 'Per-section scoring strategy', note: 'What each section must demonstrate to score' },
    { from: 'SAL-04', artifact: 'Win theme document', note: 'Win themes that must be integrated' },
    { from: 'BM-07', artifact: 'Quality plan', note: 'Review criteria' }
  ],

  subs: [
    {
      id: 'PRD-05.1', name: 'Pink Team Review', description: 'Independent review of storyboards against evaluation criteria and win strategy',
      tasks: [{
        id: 'PRD-05.1.1', name: 'Conduct pink team review of storyboards — assess response structure, key messages, win theme integration, evidence placement, and scoring potential per section',
        raci: { r: 'Independent Reviewers', a: 'Bid Director', c: 'Capture Lead', i: 'Writers' },
        inputs: [{ from: 'BM-10', artifact: 'Approved storyboard' }, { from: 'SAL-05.2.3', artifact: 'Per-section scoring strategy' }, { from: 'SAL-04', artifact: 'Win theme document' }],
        outputs: [{ name: 'Pink review scorecard', format: 'Per-section review assessment', quality: ['Every storyboard section reviewed against evaluation criteria', 'Win theme integration assessed — are differentiators placed where marks are?', 'Response structure assessed — will this structure score or is it missing key elements?', 'Evidence placement assessed — is the right evidence planned for the right sections?', 'Actions raised per section — what must change before writers start drafting'] }],
        effort: 'High', type: 'Sequential'
      }]
    },
    {
      id: 'PRD-05.2', name: 'Pink Action Resolution', description: 'Resolve pink review actions before drafting begins',
      tasks: [{
        id: 'PRD-05.2.1', name: 'Resolve pink review actions — update storyboards, adjust structure, reallocate evidence, brief writers on changes',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Writers / Solution Architect', i: null },
        inputs: [{ from: 'PRD-05.1.1', artifact: 'Pink review scorecard' }],
        outputs: [{ name: 'Pink review scorecard & actions (resolved — activity primary output)', format: 'Updated storyboards with action resolution record', quality: ['All critical and major actions resolved before drafting begins', 'Updated storyboards issued to writers as revised briefs', 'Minor actions communicated to writers for incorporation during drafting', 'Pink review closure recorded — methodology checkpoint passed'] }],
        effort: 'Medium', type: 'Sequential'
      }]
    }
  ],

  outputs: [{ name: 'Pink review scorecard & actions', format: 'Review record with resolved actions', quality: ['Storyboards reviewed by independent panel', 'Actions resolved before drafting', 'Writers briefed on any changes'] }],
  consumers: [{ activity: 'PRD-02', consumes: 'Pink-reviewed storyboards', usage: 'Writers draft against the pink-reviewed and updated storyboards' }]
}
```

---

## PRD-06 — Red Review (Full Draft)

```javascript
{
  id: 'PRD-06', name: 'Red review (full draft)', workstream: 'PRD', phase: 'PROD', role: 'Bid Manager',
  output: 'Red review scorecard & actions resolved', dependencies: ['PRD-02', 'PRD-03', 'PRD-04'], effortDays: 5, teamSize: 1, parallelisationType: 'C',
  // Note: the red review is an EVALUATOR SIMULATION — reviewers score the near-complete
  // draft as if they were the client evaluation panel.

  inputs: [
    { from: 'PRD-02', artifact: 'Draft response sections', note: 'Near-complete drafts (80-90%)' },
    { from: 'PRD-03', artifact: 'Evidence pack', note: 'Evidence reviewed alongside responses' },
    { from: 'PRD-04', artifact: 'Pricing response documents', note: 'Commercial response included in red review' },
    { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach', note: 'Scoring criteria reviewers assess against' },
    { from: 'BM-07', artifact: 'Quality plan', note: 'Review criteria and scoring methodology' }
  ],

  subs: [
    {
      id: 'PRD-06.1', name: 'Red Team Review', description: 'Evaluator simulation — independent panel scores the draft as the client would',
      tasks: [{
        id: 'PRD-06.1.1', name: 'Conduct red team review — evaluator simulation scoring each section against evaluation criteria, assessing win theme penetration, evidence strength, and compliance',
        raci: { r: 'Senior Independent Review Panel', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'Bid Manager' },
        inputs: [{ from: 'PRD-02', artifact: 'Draft response sections' }, { from: 'PRD-03', artifact: 'Evidence pack' }, { from: 'PRD-04', artifact: 'Pricing response documents' }, { from: 'SAL-05', artifact: 'Evaluation criteria matrix with scoring approach' }],
        outputs: [{ name: 'Red review scorecard', format: 'Per-section scored assessment', quality: ['Every section scored against evaluation criteria — predicted client score', 'Win theme integration assessed — are differentiators landing?', 'Evidence strength assessed — are claims substantiated?', 'Compliance confirmed per section — any non-compliance flagged as critical', 'Actions raised with severity: critical (must fix), major (should fix), minor (improve if time)'] }],
        effort: 'High', type: 'Sequential'
      }]
    },
    {
      id: 'PRD-06.2', name: 'Red Action Resolution', description: 'Resolve red review actions — critical actions must be resolved before gold review',
      tasks: [{
        id: 'PRD-06.2.1', name: 'Resolve red review actions — writers revise sections, bid manager tracks to closure, critical actions must be resolved before gold review',
        raci: { r: 'Writers (per section)', a: 'Bid Manager', c: 'Reviewers', i: 'Bid Director' },
        inputs: [{ from: 'PRD-06.1.1', artifact: 'Red review scorecard' }],
        outputs: [{ name: 'Red review scorecard & actions resolved (activity primary output)', format: 'Action resolution record with revised drafts', quality: ['All critical actions resolved — no unaddressed critical issues at gold review', 'Major actions resolved or accepted with rationale', 'Revised sections demonstrate score improvement vs red review assessment', 'Red review closure recorded — ready for gold review'] }],
        effort: 'High', type: 'Sequential'
      }]
    }
  ],

  outputs: [{ name: 'Red review scorecard & actions resolved', format: 'Scored review with resolved actions', quality: ['Evaluator simulation scores per section', 'Critical/major actions resolved', 'Score improvement demonstrated', 'Ready for gold review'] }],
  consumers: [{ activity: 'PRD-07', consumes: 'Red-reviewed response', usage: 'Gold review assesses the final revised response' }]
}
```

---

## PRD-07 — Gold Review (Final/Executive)

```javascript
{
  id: 'PRD-07', name: 'Gold review (final/executive)', workstream: 'PRD', phase: 'PROD', role: 'Bid Manager',
  output: 'Gold review scorecard & sign-off', dependencies: ['PRD-06', 'COM-06'], effortDays: 3, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'PRD-06', artifact: 'Red review scorecard & actions resolved', note: 'Red-reviewed and revised response' },
    { from: 'COM-06', artifact: 'Pricing model (locked & assured)', note: 'Final pricing confirmed' }
  ],

  subs: [{
    id: 'PRD-07.1', name: 'Gold Team Review', description: 'Final executive quality and compliance review — the last check before formatting and submission',
    tasks: [{
      id: 'PRD-07.1.1', name: 'Conduct gold team review — executive quality check: compliance, completeness, tone, win strategy coherence, and final sign-off to proceed to submission',
      raci: { r: 'Bid Board / Partner level', a: 'Senior Responsible Executive', c: 'Commercial Lead / Legal Lead', i: 'Bid Manager' },
      inputs: [{ from: 'PRD-06', artifact: 'Red review scorecard & actions resolved' }, { from: 'COM-06', artifact: 'Pricing model (locked & assured)' }],
      outputs: [{ name: 'Gold review scorecard & sign-off (activity primary output)', format: 'Executive review with sign-off', quality: ['Compliance confirmed — all mandatory requirements addressed', 'Completeness confirmed — no missing sections or annexes', 'Tone and quality confirmed — executive-level presentation standard', 'Win strategy coherence confirmed — the response tells a winning story', 'Gold review sign-off recorded — approved for formatting and submission', 'Any final actions are minor only — no material changes at this stage'] }],
      effort: 'High', type: 'Sequential'
    }]
  }],

  outputs: [{ name: 'Gold review scorecard & sign-off', format: 'Executive sign-off record', quality: ['Compliance, completeness, tone, strategy confirmed', 'Executive sign-off recorded', 'Approved for formatting and submission'] }],
  consumers: [{ activity: 'PRD-08', consumes: 'Gold-reviewed response', usage: 'Final QA and formatting of approved response' }]
}
```

---

## PRD-08 — Final QA & Formatting

```javascript
{
  id: 'PRD-08', name: 'Final QA & formatting', workstream: 'PRD', phase: 'PROD', role: 'Bid Coordinator',
  output: 'QA checklist complete', dependencies: ['PRD-07'], effortDays: 3, teamSize: 1, parallelisationType: 'S',

  inputs: [
    { from: 'PRD-07', artifact: 'Gold review scorecard & sign-off', note: 'Gold-approved content' },
    { external: true, artifact: 'ITT documentation — formatting requirements, branding guidelines, page limits, file format requirements' },
    { external: true, artifact: 'Corporate branding templates and style guide' }
  ],

  subs: [{
    id: 'PRD-08.1', name: 'Document Production', description: 'Format, proof-read, and quality-assure the final submission documents',
    tasks: [
      { id: 'PRD-08.1.1', name: 'Apply formatting, branding, and layout — corporate template, page limits, headers/footers, table of contents, cross-references, graphics',
        raci: { r: 'Bid Coordinator / DTP', a: 'Bid Manager', c: 'Brand/Design', i: 'Bid Director' },
        inputs: [{ from: 'PRD-07', artifact: 'Gold review scorecard & sign-off' }, { external: true, artifact: 'Corporate branding templates and style guide' }],
        outputs: [{ name: 'Formatted proposal documents', format: 'Submission-ready documents', quality: ['Corporate branding applied consistently', 'Page/word limits met per section', 'Table of contents, cross-references, and figure numbering correct', 'Graphics and diagrams formatted to print quality'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'PRD-08.1.2', name: 'Proof-read, spell-check, and cross-reference — final quality assurance pass before submission',
        raci: { r: 'Bid Coordinator', a: 'Bid Manager', c: 'Senior Bid Writer', i: null },
        inputs: [{ from: 'PRD-08.1.1', artifact: 'Formatted proposal documents' }],
        outputs: [{ name: 'QA checklist complete (activity primary output)', format: 'QA sign-off with error-free documents', quality: ['Proof-read complete — spelling, grammar, punctuation', 'Cross-references verified — all internal references correct', 'Page/word counts confirmed within limits', 'Print test completed — formatting survives PDF conversion', 'QA checklist signed off — documents are submission-ready'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'QA checklist complete', format: 'QA sign-off with formatted documents', quality: ['Formatted, proof-read, cross-referenced, print-tested', 'QA checklist signed off'] }],
  consumers: [{ activity: 'PRD-09', consumes: 'Formatted documents', usage: 'Submission packaging uses the QA-approved documents' }]
}
```

---

## PRD-09 — Submission Packaging & Upload

```javascript
{
  id: 'PRD-09', name: 'Submission packaging & upload', workstream: 'PRD', phase: 'PROD', role: 'Bid Manager',
  output: 'Submission confirmation receipt', dependencies: ['PRD-08', 'GOV-05'], effortDays: 2, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'PRD-08', artifact: 'QA checklist complete', note: 'Formatted, QA-approved documents' },
    { from: 'PRD-01', artifact: 'Compliance matrix (live)', note: 'Final compliance check' },
    { from: 'GOV-05', artifact: 'Submission authority confirmation', note: 'Formal authority to submit' },
    { external: true, artifact: 'Procurement portal access, credentials, and submission instructions' }
  ],

  subs: [{
    id: 'PRD-09.1', name: 'Final Submission', description: 'Final compliance check, package, upload, and confirm',
    tasks: [
      { id: 'PRD-09.1.1', name: 'Conduct final compliance check — verify all mandatory requirements addressed, all documents present, all formats correct',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Legal / Commercial Lead', i: null },
        inputs: [{ from: 'PRD-01', artifact: 'Compliance matrix (live)' }, { from: 'PRD-08', artifact: 'QA checklist complete' }],
        outputs: [{ name: 'Final compliance sign-off', format: 'Compliance confirmation', quality: ['Every mandatory requirement confirmed as addressed', 'All required documents present and in correct format', 'File sizes within portal limits', 'Compliance sign-off recorded'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'PRD-09.1.2', name: 'Package and upload submission — portal upload, confirmation receipt obtained, submission archived',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'IT Support', i: 'All Workstream Leads' },
        inputs: [{ from: 'PRD-09.1.1', artifact: 'Final compliance sign-off' }, { from: 'GOV-05', artifact: 'Submission authority confirmation' }, { external: true, artifact: 'Procurement portal access and submission instructions' }],
        outputs: [{ name: 'Submission confirmation receipt (activity primary output)', format: 'Portal confirmation with archive', quality: ['Submission uploaded to portal before deadline — with contingency time', 'Portal confirmation receipt obtained and recorded', 'Complete submission archived — all documents, pricing, evidence, supporting materials', 'Bid team notified of successful submission', 'BM-11 (hot debrief) triggered'] }],
        effort: 'High', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Submission confirmation receipt', format: 'Portal confirmation with submission archive', quality: ['Submitted before deadline', 'Confirmation receipt obtained', 'Complete archive created', 'Hot debrief triggered'] }],
  consumers: [
    { activity: 'BM-11', consumes: 'Submission confirmation', usage: 'Hot debrief triggered within 48 hours' },
    { activity: 'POST-01', consumes: 'Submitted proposal', usage: 'Presentation preparation references the submitted response' }
  ]
}
```

---

---

## GOV — Internal Governance: Pattern Note

> **All governance activities follow the same pattern:** (1) Prepare the gate review pack from upstream inputs, (2) Conduct the review, capture the decision, distribute actions/conditions. Every gate is configurable — activated or deactivated at bid setup based on contract value, complexity, and organisational policy.

---

## GOV-01 — Pursuit Approval (configurable)

```javascript
{
  id: 'GOV-01', name: 'Pursuit approval (configurable)', workstream: 'GOV', phase: 'DEV', role: 'Bid Director',
  output: 'Pursuit approval decision record', dependencies: ['SAL-06'], effortDays: 2, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'SAL-06', artifact: 'Capture plan (locked)', note: 'The full capture plan and bid mandate' },
    { from: 'SAL-06.4.2', artifact: 'Bid Mandate document', note: 'Go/no-go recommendation, budget, resource ask' },
    { from: 'SAL-06.2.3', artifact: 'PWIN score and rationale', note: 'Probability of win for the governance panel' }
  ],

  subs: [{
    id: 'GOV-01.1', name: 'Pursuit Governance', description: 'Prepare and conduct the pursuit approval gate',
    tasks: [
      { id: 'GOV-01.1.1', name: 'Prepare pursuit approval review pack — capture plan summary, bid mandate, PWIN score, resource ask, key risks, go/no-go recommendation',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
        inputs: [{ from: 'SAL-06', artifact: 'Capture plan (locked)' }, { from: 'SAL-06.4.2', artifact: 'Bid Mandate document' }],
        outputs: [{ name: 'Pursuit approval review pack', format: 'Executive summary for governance panel', quality: ['One-page executive summary plus supporting detail', 'PWIN score, key risks, resource ask, and recommendation clearly presented', 'Pack distributed to governance panel with adequate read-ahead time'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'GOV-01.1.2', name: 'Conduct pursuit approval review — present to governance panel, debate, capture decision (approve / approve with conditions / reject)',
        raci: { r: 'Bid Director', a: 'Senior Responsible Executive / Bid Board', c: 'Capture Lead / Commercial Lead', i: 'Bid Manager' },
        inputs: [{ from: 'GOV-01.1.1', artifact: 'Pursuit approval review pack' }],
        outputs: [{ name: 'Pursuit approval decision record (activity primary output)', format: 'Decision record with conditions', quality: ['Decision recorded: approved, approved with conditions, or rejected', 'Conditions documented with owners and deadlines if conditional approval', 'Budget and resource commitment confirmed', 'Decision communicated to bid team'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Pursuit approval decision record', format: 'Governance decision record', quality: ['Decision recorded', 'Conditions captured', 'Commitment confirmed'] }],
  consumers: [{ activity: 'BM-01', consumes: 'Pursuit approval', usage: 'Kickoff proceeds on approval — conditions tracked' }]
}
```

---

## GOV-02 — Solution & Strategy Review (configurable)

```javascript
{
  id: 'GOV-02', name: 'Solution & strategy review (configurable)', workstream: 'GOV', phase: 'DEV', role: 'Bid Director',
  output: 'Solution review decision record', dependencies: ['SAL-06', 'SOL-03', 'DEL-01', 'SUP-01'], effortDays: 2, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'SOL-11', artifact: 'Solution design pack (locked & assured)', note: 'The locked solution for governance review' },
    { from: 'SOL-12', artifact: 'Solution risk register', note: 'Solution risk position' },
    { from: 'DEL-01', artifact: 'Delivery risk & assumptions register', note: 'Delivery risk position' },
    { from: 'BM-13', artifact: 'Bid risk register', note: 'Consolidated bid risk position' },
    { from: 'SUP-01', artifact: 'Partner shortlist with rationale', note: 'Partner selection for governance review' }
  ],

  subs: [{
    id: 'GOV-02.1', name: 'Solution Governance', description: 'Prepare and conduct the solution & strategy review gate',
    tasks: [
      { id: 'GOV-02.1.1', name: 'Prepare solution review pack — solution summary, risk position, win strategy alignment, partner strategy, delivery readiness',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Solution Architect / Delivery Director', i: null },
        inputs: [{ from: 'SOL-11', artifact: 'Solution design pack (locked & assured)' }, { from: 'SOL-12', artifact: 'Solution risk register' }, { from: 'BM-13', artifact: 'Bid risk register' }],
        outputs: [{ name: 'Solution review pack', format: 'Executive summary for governance panel', quality: ['Solution summarised at executive level — TOM, delivery model, transition, innovation', 'Risk position presented — top risks with mitigations', 'Win strategy alignment confirmed — solution delivers the competitive narrative', 'Pack distributed with adequate read-ahead time'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'GOV-02.1.2', name: 'Conduct solution & strategy review — present, debate, capture decision',
        raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Solution Architect / Delivery Director / Commercial Lead', i: 'Bid Manager' },
        inputs: [{ from: 'GOV-02.1.1', artifact: 'Solution review pack' }],
        outputs: [{ name: 'Solution review decision record (activity primary output)', format: 'Decision record with conditions', quality: ['Decision recorded: approved, approved with conditions, or requires rework', 'Conditions documented with owners and deadlines', 'Solution baseline confirmed or rework scope defined', 'Decision communicated to bid team'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Solution review decision record', format: 'Governance decision record', quality: ['Decision recorded', 'Conditions captured', 'Solution baseline confirmed or rework defined'] }],
  consumers: [{ activity: 'COM-01', consumes: 'Solution review decision', usage: 'Costing proceeds on approved solution — any conditions may affect cost model' }]
}
```

---

## GOV-03 — Pricing & Risk Review (configurable)

```javascript
{
  id: 'GOV-03', name: 'Pricing & risk review (configurable)', workstream: 'GOV', phase: 'DEV', role: 'Bid Director',
  output: 'Pricing decision record + approved price', dependencies: ['COM-06', 'DEL-06', 'LEG-02', 'SUP-06'], effortDays: 2, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'COM-06', artifact: 'Pricing model (locked & assured)', note: 'The locked price for approval' },
    { from: 'COM-05', artifact: 'Margin model with sensitivities', note: 'Margin, sensitivities, risk-adjusted view' },
    { from: 'COM-07', artifact: 'Commercial risk register', note: 'Commercial risk position' },
    { from: 'DEL-06', artifact: 'Mitigated risk register (assured)', note: 'Delivery risk position' },
    { from: 'LEG-02', artifact: 'Risk allocation matrix', note: 'Contractual risk position' },
    { from: 'SUP-06', artifact: 'Back-to-back terms agreed', note: 'Partner commercial terms confirmed' },
    { from: 'BM-13', artifact: 'Bid risk register', note: 'Consolidated risk position' }
  ],

  subs: [{
    id: 'GOV-03.1', name: 'Commercial Governance', description: 'Prepare and conduct the pricing & risk review gate — the executive pricing approval',
    tasks: [
      { id: 'GOV-03.1.1', name: 'Prepare pricing review pack — price position, margin, sensitivities, risk, partner terms, contract terms, recommendation',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Commercial Lead / Finance', i: null },
        inputs: [{ from: 'COM-06', artifact: 'Pricing model (locked & assured)' }, { from: 'COM-05', artifact: 'Margin model with sensitivities' }, { from: 'COM-07', artifact: 'Commercial risk register' }, { from: 'DEL-06', artifact: 'Mitigated risk register (assured)' }],
        outputs: [{ name: 'Pricing review pack', format: 'Executive pricing decision paper', quality: ['Price, margin, sensitivities presented clearly for executive decision', 'Risk position summarised — top commercial, delivery, and contractual risks', 'Partner terms status confirmed', 'Recommendation stated — proceed at this price, or adjust'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'GOV-03.1.2', name: 'Conduct pricing & risk review — present to governance panel, debate pricing position, capture pricing approval',
        raci: { r: 'Bid Director', a: 'Senior Responsible Executive / Finance Director', c: 'Commercial Lead / Legal Lead', i: 'Bid Manager' },
        inputs: [{ from: 'GOV-03.1.1', artifact: 'Pricing review pack' }],
        outputs: [{ name: 'Pricing decision record + approved price (activity primary output)', format: 'Pricing approval with decision record', quality: ['Price approved at specific level — or adjusted with rationale', 'Margin accepted at the approved price — executive commitment', 'Risk appetite confirmed — residual risks accepted by governance', 'Any pricing conditions documented — e.g. "hold price subject to partner confirmation"', 'Approved price is the authoritative figure for submission'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Pricing decision record + approved price', format: 'Governance pricing approval', quality: ['Price approved', 'Margin accepted', 'Risk appetite confirmed', 'Authoritative figure for submission'] }],
  consumers: [{ activity: 'GOV-04', consumes: 'Pricing approval', usage: 'Executive approval builds on pricing decision' }]
}
```

---

## GOV-04 — Executive Approval (configurable — may be multi-tier)

```javascript
{
  id: 'GOV-04', name: 'Executive approval (configurable — may be multi-tier)', workstream: 'GOV', phase: 'PROD', role: 'Bid Director',
  output: 'Executive approval decision record(s)', dependencies: ['GOV-03', 'PRD-06', 'PRD-07'], effortDays: 2, teamSize: 1, parallelisationType: 'C',
  // Note: may be multi-tier — BU → ExCo → Board depending on TCV thresholds.
  // Each tier is a separate review with escalating authority.

  inputs: [
    { from: 'GOV-03', artifact: 'Pricing decision record + approved price' },
    { from: 'PRD-07', artifact: 'Gold review scorecard & sign-off', note: 'Quality of the response confirmed' },
    { from: 'BM-13', artifact: 'Bid risk register', note: 'Final risk position' }
  ],

  subs: [{
    id: 'GOV-04.1', name: 'Executive Governance', description: 'Multi-tier executive approval — escalates by TCV threshold',
    tasks: [
      { id: 'GOV-04.1.1', name: 'Prepare executive approval pack — bid summary, price, margin, risk, quality assessment, recommendation to submit',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Commercial Lead', i: null },
        inputs: [{ from: 'GOV-03', artifact: 'Pricing decision record + approved price' }, { from: 'PRD-07', artifact: 'Gold review scorecard & sign-off' }, { from: 'BM-13', artifact: 'Bid risk register' }],
        outputs: [{ name: 'Executive approval pack', format: 'Board-level decision paper', quality: ['One-page executive summary — bid, price, margin, PWIN, key risks, recommendation', 'Supporting detail available if requested', 'Tailored to each governance tier if multi-tier'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'GOV-04.1.2', name: 'Obtain executive approval — present at each required tier (BU / ExCo / Board), capture approval to submit',
        raci: { r: 'Bid Director', a: 'Senior Responsible Executive / Board', c: 'Commercial Lead / Finance Director', i: 'Bid Manager' },
        inputs: [{ from: 'GOV-04.1.1', artifact: 'Executive approval pack' }],
        outputs: [{ name: 'Executive approval decision record(s) (activity primary output)', format: 'Per-tier approval records', quality: ['Approval obtained at every required tier', 'Any conditions from each tier documented and resolved', 'Authority to submit confirmed — the organisation commits to this bid', 'Approval records archived for audit trail'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Executive approval decision record(s)', format: 'Multi-tier approval records', quality: ['All required tiers approved', 'Conditions resolved', 'Authority to submit confirmed'] }],
  consumers: [{ activity: 'GOV-05', consumes: 'Executive approval', usage: 'Final submission authority requires executive approval' }]
}
```

---

## GOV-05 — Final Submission Authority (configurable)

```javascript
{
  id: 'GOV-05', name: 'Final submission authority (configurable)', workstream: 'GOV', phase: 'PROD', role: 'Bid Director',
  output: 'Submission authority confirmation', dependencies: ['GOV-04', 'PRD-08'], effortDays: 1, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'GOV-04', artifact: 'Executive approval decision record(s)', note: 'All executive approvals obtained' },
    { from: 'PRD-08', artifact: 'QA checklist complete', note: 'Documents are formatted and QA-approved' },
    { from: 'PRD-01', artifact: 'Compliance matrix (live)', note: 'Final compliance confirmed' }
  ],

  subs: [{
    id: 'GOV-05.1', name: 'Submission Authority', description: 'The final gate — authority to press submit',
    tasks: [{
      id: 'GOV-05.1.1', name: 'Confirm final submission authority — all approvals obtained, documents QA-complete, compliance confirmed, authority to submit granted',
      raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Bid Manager', i: null },
      inputs: [{ from: 'GOV-04', artifact: 'Executive approval decision record(s)' }, { from: 'PRD-08', artifact: 'QA checklist complete' }, { from: 'PRD-01', artifact: 'Compliance matrix (live)' }],
      outputs: [{ name: 'Submission authority confirmation (activity primary output)', format: 'Formal submission authority', quality: ['All governance approvals confirmed — pursuit, solution, pricing, executive, legal', 'Documents confirmed as QA-complete and compliant', 'Submission authority formally granted — the bid may be submitted', 'Authority recorded with timestamp for audit trail'] }],
      effort: 'Low', type: 'Sequential'
    }]
  }],

  outputs: [{ name: 'Submission authority confirmation', format: 'Formal authority record', quality: ['All approvals confirmed', 'Documents QA-complete', 'Authority granted'] }],
  consumers: [{ activity: 'PRD-09', consumes: 'Submission authority', usage: 'Submission can proceed — portal upload authorised' }]
}
```

---

## GOV-06 — Legal & Contractual Review (configurable)

```javascript
{
  id: 'GOV-06', name: 'Legal & contractual review (configurable)', workstream: 'GOV', phase: 'DEV', role: 'Legal Lead',
  output: 'Legal review decision record', dependencies: ['LEG-01', 'LEG-02', 'LEG-04'], effortDays: 2, teamSize: 1, parallelisationType: 'C',
  // Note: proposed in Session 10 — product has gate G4 (Legal & Contractual Review)
  // but no corresponding GOV activity to prepare for it. This fills the gap.

  inputs: [
    { from: 'LEG-01', artifact: 'Contract markup with positions log' },
    { from: 'LEG-02', artifact: 'Risk allocation matrix' },
    { from: 'LEG-04', artifact: 'TUPE compliance assessment' },
    { from: 'LEG-05', artifact: 'DPIA / security assessment' },
    { from: 'LEG-06', artifact: 'Subcontract terms summary' }
  ],

  subs: [{
    id: 'GOV-06.1', name: 'Legal Governance', description: 'Prepare and conduct the legal & contractual review gate',
    tasks: [
      { id: 'GOV-06.1.1', name: 'Prepare legal review pack — contract positions, risk allocation, TUPE, data protection, subcontractor terms summary',
        raci: { r: 'Legal Lead', a: 'Bid Director', c: 'Commercial Lead', i: 'Bid Manager' },
        inputs: [{ from: 'LEG-01', artifact: 'Contract markup with positions log' }, { from: 'LEG-02', artifact: 'Risk allocation matrix' }, { from: 'LEG-04', artifact: 'TUPE compliance assessment' }, { from: 'LEG-05', artifact: 'DPIA / security assessment' }, { from: 'LEG-06', artifact: 'Subcontract terms summary' }],
        outputs: [{ name: 'Legal review pack', format: 'Executive legal summary for governance', quality: ['Contract positions summarised — red lines, key risks, negotiation strategy', 'Risk allocation presented with acceptability assessment', 'TUPE and data protection compliance confirmed or risks flagged', 'Subcontractor terms status confirmed'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'GOV-06.1.2', name: 'Conduct legal & contractual review — present to governance panel, capture decision on contract positions and risk acceptance',
        raci: { r: 'Legal Lead', a: 'Bid Director / Senior Responsible Executive', c: 'Commercial Lead', i: 'Bid Manager' },
        inputs: [{ from: 'GOV-06.1.1', artifact: 'Legal review pack' }],
        outputs: [{ name: 'Legal review decision record (activity primary output)', format: 'Decision record', quality: ['Contract positions approved or adjusted', 'Risk allocation accepted or further mitigation required', 'Red lines confirmed — what we will not accept in negotiation', 'Decision communicated to bid team and LEG workstream'] }],
        effort: 'Medium', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Legal review decision record', format: 'Governance decision record', quality: ['Contract positions approved', 'Risk allocation accepted', 'Red lines confirmed'] }],
  consumers: [{ activity: 'GOV-03', consumes: 'Legal review decision', usage: 'Pricing & risk review incorporates approved legal position' }]
}
```

---

## POST — Post-Submission: Context Note

> **Post-submission activities have client-imposed deadlines.** Not all apply to every bid — presentation, BAFO, and negotiation are activated during setup based on procurement type. The system monitors post-submission health on the practice portfolio the same way it monitors pre-submission readiness.

---

## POST-01 — Presentation Design & Development

```javascript
{
  id: 'POST-01', name: 'Presentation design & development', workstream: 'POST', phase: 'POST', role: 'Bid Director',
  output: 'Presentation deck, speaker notes, narrative', dependencies: ['PRD-09'], effortDays: 10, teamSize: 2, parallelisationType: 'P',

  inputs: [
    { from: 'PRD-09', artifact: 'Submission confirmation receipt', note: 'The submitted proposal — the presentation must be consistent with what was submitted' },
    { from: 'SAL-04', artifact: 'Win theme document', note: 'Win themes drive the presentation narrative' },
    { from: 'SAL-10', artifact: 'Stakeholder relationship map & engagement plan', note: 'Who is on the evaluation panel — tailor the presentation' },
    { external: true, artifact: 'Client invitation to present — format, duration, panel composition, topic guidance' }
  ],

  subs: [{
    id: 'POST-01.1', name: 'Presentation Preparation', description: 'Design and develop the bid presentation',
    tasks: [
      { id: 'POST-01.1.1', name: 'Design presentation narrative and structure — aligned to win themes, tailored to evaluation panel, consistent with submitted proposal',
        raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Capture Lead / Solution Architect', i: 'Bid Manager' },
        inputs: [{ from: 'SAL-04', artifact: 'Win theme document' }, { from: 'SAL-10', artifact: 'Stakeholder relationship map & engagement plan' }, { external: true, artifact: 'Client invitation to present' }],
        outputs: [{ name: 'Presentation narrative and structure', format: 'Presentation outline', quality: ['Narrative leads with win strategy — why we should win', 'Tailored to known panel members and their priorities', 'Consistent with submitted proposal — no contradictions', 'Structured to the client\'s format and time constraints'] }],
        effort: 'High', type: 'Sequential' },
      { id: 'POST-01.1.2', name: 'Develop presentation materials — slides, speaker notes, Q&A preparation, supporting visuals and demos',
        raci: { r: 'Bid Manager / Presentation Coach', a: 'Bid Director', c: 'Solution Architect / Commercial Lead', i: 'DTP' },
        inputs: [{ from: 'POST-01.1.1', artifact: 'Presentation narrative and structure' }],
        outputs: [{ name: 'Presentation deck, speaker notes, narrative (activity primary output)', format: 'Complete presentation pack', quality: ['Professional presentation materials — not a proposal re-read', 'Speaker notes per slide — what to say, not what to show', 'Q&A preparation — anticipated tough questions with agreed answers', 'Supporting visuals or demos prepared if applicable'] }],
        effort: 'High', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Presentation deck, speaker notes, narrative', format: 'Complete presentation pack', quality: ['Win-strategy-led narrative', 'Tailored to panel', 'Q&A prepared'] }],
  consumers: [{ activity: 'POST-02', consumes: 'Presentation materials', usage: 'Rehearsals use the presentation pack' }]
}
```

---

## POST-02 — Presentation Rehearsals & Coaching

```javascript
{
  id: 'POST-02', name: 'Presentation rehearsals & coaching', workstream: 'POST', phase: 'POST', role: 'Bid Director',
  output: 'Rehearsal debrief notes, revised deck, Q&A prep', dependencies: ['POST-01'], effortDays: 3, teamSize: 1, parallelisationType: 'C',

  inputs: [{ from: 'POST-01', artifact: 'Presentation deck, speaker notes, narrative' }],

  subs: [{
    id: 'POST-02.1', name: 'Rehearsal & Coaching', description: 'Structured rehearsals with feedback and iteration',
    tasks: [{
      id: 'POST-02.1.1', name: 'Conduct structured presentation rehearsals — simulate the evaluation panel, provide feedback, iterate the presentation and Q&A responses',
      raci: { r: 'Presenting Team', a: 'Senior Responsible Executive', c: 'Presentation Coach / SMEs', i: 'Bid Manager' },
      inputs: [{ from: 'POST-01', artifact: 'Presentation deck, speaker notes, narrative' }],
      outputs: [{ name: 'Rehearsal debrief notes, revised deck, Q&A prep (activity primary output)', format: 'Iterated presentation pack', quality: ['At least 2 full rehearsals conducted — with debrief after each', 'Panel simulation included — mock questions from evaluator perspective', 'Presentation refined based on feedback — not just practiced but improved', 'Q&A responses refined and pressure-tested', 'Presenting team confident and aligned'] }],
      effort: 'High', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Rehearsal debrief notes, revised deck, Q&A prep', format: 'Rehearsed presentation pack', quality: ['Multiple rehearsals conducted', 'Presentation iterated', 'Team confident'] }],
  consumers: [{ activity: 'POST-03', consumes: 'Rehearsed presentation', usage: 'Delivery uses the rehearsed materials' }]
}
```

---

## POST-03 — Presentation Delivery

```javascript
{
  id: 'POST-03', name: 'Presentation delivery', workstream: 'POST', phase: 'POST', role: 'Bid Director',
  output: 'Presentation delivered, Q&A record', dependencies: ['POST-02'], effortDays: 1, teamSize: 1, parallelisationType: 'C',

  inputs: [{ from: 'POST-02', artifact: 'Rehearsal debrief notes, revised deck, Q&A prep' }],

  subs: [{
    id: 'POST-03.1', name: 'Presentation Delivery', description: 'Deliver the presentation and manage Q&A',
    tasks: [{
      id: 'POST-03.1.1', name: 'Deliver bid presentation to evaluation panel — present, manage Q&A, capture panel reactions and follow-up questions',
      raci: { r: 'Bid Director / Senior Executive / Presenting Team', a: 'Senior Responsible Executive', c: 'Commercial Lead / Solution Architect', i: 'Bid Manager' },
      inputs: [{ from: 'POST-02', artifact: 'Rehearsal debrief notes, revised deck, Q&A prep' }],
      outputs: [{ name: 'Presentation delivered, Q&A record (activity primary output)', format: 'Delivery record', quality: ['Presentation delivered within time allocation', 'Q&A managed — all questions answered or follow-up committed', 'Panel reactions noted — informal intelligence on how it landed', 'Any follow-up commitments documented and assigned'] }],
      effort: 'High', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Presentation delivered, Q&A record', format: 'Delivery record', quality: ['Delivered on time', 'Q&A managed', 'Follow-ups captured'] }],
  consumers: [{ activity: 'BM-12', consumes: 'Presentation record', usage: 'Lessons learned includes presentation performance' }]
}
```

---

## POST-04 — Post-submission Clarification Management

```javascript
{
  id: 'POST-04', name: 'Post-submission clarification management', workstream: 'POST', phase: 'POST', role: 'Bid Manager',
  output: 'Clarification log, submitted responses, updated risk log', dependencies: ['PRD-09'], effortDays: 5, teamSize: 2, parallelisationType: 'P',

  inputs: [{ from: 'PRD-09', artifact: 'Submission confirmation receipt', note: 'The submitted proposal — clarifications reference it' }, { external: true, artifact: 'Client post-submission clarification requests' }],

  subs: [{
    id: 'POST-04.1', name: 'Post-Submission Clarification', description: 'Manage client clarification requests received after submission',
    tasks: [
      { id: 'POST-04.1.1', name: 'Receive, log, and triage post-submission clarification requests from client — assess impact and assign to workstream leads',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'All Workstream Leads', i: 'Commercial Lead' },
        inputs: [{ external: true, artifact: 'Client post-submission clarification requests' }],
        outputs: [{ name: 'Clarification triage log', format: 'Tracking register', quality: ['Every request logged with date, topic, urgency, and assigned owner', 'Impact assessed — does this change our position or just need explanation?'] }],
        effort: 'Medium', type: 'Iterative' },
      { id: 'POST-04.1.2', name: 'Draft, review, and submit clarification responses within client deadlines — ensuring consistency with submitted proposal',
        raci: { r: 'Workstream Leads (per topic)', a: 'Bid Director', c: 'Legal / Commercial', i: 'Bid Manager' },
        inputs: [{ from: 'POST-04.1.1', artifact: 'Clarification triage log' }],
        outputs: [{ name: 'Clarification log, submitted responses (activity primary output)', format: 'Response log with submitted answers', quality: ['All responses submitted within client deadlines', 'Responses consistent with submitted proposal — no contradictions', 'Responses reviewed by Bid Director before submission', 'Any responses that change our risk position flagged and risk log updated'] }],
        effort: 'High', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Clarification log, submitted responses, updated risk log', format: 'Response tracker', quality: ['All requests answered on time', 'Consistency with submission maintained', 'Risk log updated'] }],
  consumers: [{ activity: 'POST-05', consumes: 'Clarification responses', usage: 'BAFO preparation considers any positions changed through clarification' }]
}
```

---

## POST-05 — BAFO Preparation & Revised Pricing

```javascript
{
  id: 'POST-05', name: 'BAFO preparation & revised pricing', workstream: 'POST', phase: 'POST', role: 'Commercial Lead',
  // ARCHETYPE NOTES:
  // Consulting/Advisory: MODIFIED — BAFO is typically "reduce your day rates." Very simple.
  //   No solution rework. Strategy is: how far can we reduce rates while maintaining margin?
  output: 'Revised pricing model, updated solution elements', dependencies: ['POST-04'], effortDays: 10, teamSize: 2, parallelisationType: 'P',

  inputs: [
    { from: 'POST-04', artifact: 'Clarification log', note: 'Positions clarified that may affect BAFO' },
    { from: 'COM-06', artifact: 'Pricing model (locked & assured)', note: 'The original pricing to revise' },
    { from: 'COM-05', artifact: 'Margin model with sensitivities', note: 'Sensitivity analysis informs how far we can move' },
    { external: true, artifact: 'Client BAFO invitation — scope of changes permitted, timeline, format' }
  ],

  subs: [{
    id: 'POST-05.1', name: 'BAFO Preparation', description: 'Develop the BAFO strategy and revised pricing',
    tasks: [
      { id: 'POST-05.1.1', name: 'Develop BAFO strategy — what to change, what to hold, how far to move on price, any solution adjustments',
        raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Capture Lead / Solution Architect', i: 'Finance' },
        inputs: [{ from: 'COM-05', artifact: 'Margin model with sensitivities' }, { external: true, artifact: 'Client BAFO invitation' }],
        outputs: [{ name: 'BAFO strategy', format: 'Strategy paper', quality: ['Clear rationale for what to change and what to hold', 'Price movement informed by sensitivity analysis — know the margin impact', 'Solution adjustments (if any) are consistent with submitted approach', 'Competitive intelligence considered — what might competitors do in BAFO?'] }],
        effort: 'High', type: 'Sequential' },
      { id: 'POST-05.1.2', name: 'Prepare revised pricing and any updated solution elements — ready for BAFO governance approval',
        raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Solution Architect / Finance', i: 'Bid Manager' },
        inputs: [{ from: 'POST-05.1.1', artifact: 'BAFO strategy' }, { from: 'COM-06', artifact: 'Pricing model (locked & assured)' }],
        outputs: [{ name: 'Revised pricing model, updated solution elements (activity primary output)', format: 'BAFO pricing and solution pack', quality: ['Revised pricing model complete — changes clearly tracked against original', 'Margin at revised price confirmed — still meets minimum threshold', 'Solution adjustments documented — what changed and why', 'Ready for POST-06 (BAFO governance approval)'] }],
        effort: 'High', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Revised pricing model, updated solution elements', format: 'BAFO submission pack', quality: ['Changes tracked against original', 'Margin confirmed', 'Ready for governance'] }],
  consumers: [{ activity: 'POST-06', consumes: 'Revised pricing', usage: 'BAFO governance approves the revised position' }]
}
```

---

## POST-06 — BAFO Governance Approval

```javascript
{
  id: 'POST-06', name: 'BAFO governance approval', workstream: 'POST', phase: 'POST', role: 'Commercial Lead',
  output: 'Board-approved BAFO mandate', dependencies: ['POST-05'], effortDays: 2, teamSize: 1, parallelisationType: 'C',

  inputs: [{ from: 'POST-05', artifact: 'Revised pricing model, updated solution elements' }],

  subs: [{
    id: 'POST-06.1', name: 'BAFO Governance', description: 'Obtain governance approval for the revised commercial position',
    tasks: [{
      id: 'POST-06.1.1', name: 'Obtain governance approval for BAFO — any material change to price or commercial position requires fresh executive approval',
      raci: { r: 'Commercial Lead', a: 'Senior Responsible Executive / Board', c: 'Bid Director / Finance Director', i: 'Bid Manager' },
      inputs: [{ from: 'POST-05', artifact: 'Revised pricing model, updated solution elements' }],
      outputs: [{ name: 'Board-approved BAFO mandate (activity primary output)', format: 'Governance approval record', quality: ['BAFO position approved — revised price and any solution changes authorised', 'Margin at revised price accepted by governance', 'Authority to submit BAFO confirmed', 'Conditions documented if conditional approval'] }],
      effort: 'High', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Board-approved BAFO mandate', format: 'Governance approval', quality: ['Revised position approved', 'Authority to submit confirmed'] }],
  consumers: [{ activity: 'POST-07', consumes: 'BAFO mandate', usage: 'Contract negotiation proceeds with approved BAFO position' }]
}
```

---

## POST-07 — Contract Negotiation Support

```javascript
{
  id: 'POST-07', name: 'Contract negotiation support', workstream: 'POST', phase: 'POST', role: 'Commercial Lead',
  output: 'Negotiated T&C schedule, agreed pricing', dependencies: ['PRD-09'], effortDays: 5, teamSize: 1, parallelisationType: 'S',

  inputs: [
    { from: 'LEG-01', artifact: 'Contract markup with positions log', note: 'Negotiation positions and fallbacks' },
    { from: 'COM-06', artifact: 'Pricing model (locked & assured)', note: 'Pricing position for negotiation' },
    { from: 'POST-06', artifact: 'Board-approved BAFO mandate', note: 'Revised position if BAFO occurred' },
    { external: true, artifact: 'Client preferred bidder notification and negotiation invitation' }
  ],

  subs: [{
    id: 'POST-07.1', name: 'Contract Negotiation', description: 'Support commercial and contractual negotiation with the client',
    tasks: [
      { id: 'POST-07.1.1', name: 'Lead commercial and contractual negotiations with client — using approved positions, manage trade-offs, escalate when authority limits reached',
        raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Legal Lead / Senior Executive', i: 'Finance' },
        inputs: [{ from: 'LEG-01', artifact: 'Contract markup with positions log' }, { from: 'COM-06', artifact: 'Pricing model (locked & assured)' }, { external: true, artifact: 'Client negotiation invitation' }],
        outputs: [{ name: 'Negotiated T&C schedule, agreed pricing (activity primary output)', format: 'Agreed contract terms', quality: ['Terms negotiated within approved positions — no unauthorised concessions', 'Trade-offs managed — concessions in one area balanced by gains in another', 'Any positions outside approved authority escalated to governance for fresh approval', 'Agreed terms documented and ready for contract signature'] }],
        effort: 'High', type: 'Iterative' }
    ]
  }],

  outputs: [{ name: 'Negotiated T&C schedule, agreed pricing', format: 'Agreed contract terms', quality: ['Negotiated within approved positions', 'Documented and ready for signature'] }],
  consumers: [{ activity: 'POST-08', consumes: 'Agreed terms', usage: 'Award processing proceeds on agreed contract' }]
}
```

---

## POST-08 — Award Processing & Mobilisation Handover

```javascript
{
  id: 'POST-08', name: 'Award processing & mobilisation handover', workstream: 'POST', phase: 'POST', role: 'Bid Manager',
  output: 'Handover pack, delivery team briefed, PID', dependencies: ['POST-07'], effortDays: 3, teamSize: 1, parallelisationType: 'C',

  inputs: [
    { from: 'POST-07', artifact: 'Negotiated T&C schedule, agreed pricing' },
    { from: 'DEL-02', artifact: 'Mobilisation plan', note: 'The mobilisation plan to hand over to delivery' },
    { from: 'SOL-11', artifact: 'Solution design pack (locked & assured)', note: 'The solution to be delivered' }
  ],

  subs: [{
    id: 'POST-08.1', name: 'Award & Handover', description: 'Process the award and hand over from bid team to delivery team',
    tasks: [
      { id: 'POST-08.1.1', name: 'Process contract award — receive confirmation, execute contract, establish commercial baseline',
        raci: { r: 'Commercial Lead', a: 'Bid Director', c: 'Legal Lead / Finance', i: 'Bid Manager' },
        inputs: [{ from: 'POST-07', artifact: 'Negotiated T&C schedule, agreed pricing' }],
        outputs: [{ name: 'Executed contract', format: 'Signed contract', quality: ['Contract executed on agreed terms', 'Commercial baseline established — this is what we committed to deliver at what price', 'Contract stored and accessible to delivery team'] }],
        effort: 'Medium', type: 'Sequential' },
      { id: 'POST-08.1.2', name: 'Hand over from bid team to delivery team — solution, mobilisation plan, risk register, assumptions, key relationships, lessons learned',
        raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Delivery Director', i: 'All Workstream Leads' },
        inputs: [{ from: 'SOL-11', artifact: 'Solution design pack (locked & assured)' }, { from: 'DEL-02', artifact: 'Mobilisation plan' }],
        outputs: [{ name: 'Handover pack, delivery team briefed, PID (activity primary output)', format: 'Comprehensive handover package', quality: ['Solution design, mobilisation plan, and risk register handed over — not just documents but knowledge', 'Delivery team briefed on win strategy, client relationships, key commitments, and known risks', 'Project Initiation Document (PID) prepared — the delivery team\'s starting point', 'Bid team formally stood down — bid costs closed out', 'Key relationships transitioned — client contacts introduced to delivery leadership'] }],
        effort: 'High', type: 'Sequential' }
    ]
  }],

  outputs: [{ name: 'Handover pack, delivery team briefed, PID', format: 'Delivery handover package', quality: ['Knowledge transferred not just documents', 'Delivery team briefed', 'PID prepared', 'Bid team stood down'] }],
  consumers: [{ activity: 'Delivery (post-bid)', consumes: 'Handover pack', usage: 'Delivery team begins mobilisation from the handover' }]
}
```

---

*Gold standard methodology mapping complete — Session 12, 2026-04-01*
*All 10 workstreams mapped: SAL, SOL, COM, LEG, DEL, SUP, BM, PRD, GOV, POST*
*Aligned with: Architecture v6, Plugin Architecture v1.2, Methodology Data Model (Session 10)*
