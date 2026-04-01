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
      name: 'Capture Plan Assembly & Bid Mandate Lock',
      description: 'Assemble the full 360-degree capture plan document, prepare the bid mandate for governance, and formally lock the strategy as the baseline for the bid',

      tasks: [
        {
          id: 'SAL-06.3.1',
          name: 'Assemble capture plan — the locked strategic baseline document covering all dimensions',
          raci: { r: 'Bid Manager', a: 'Bid Director', c: 'Capture Lead', i: null },
          inputs: [
            { from: 'SAL-06.1.1', artifact: 'Capture effectiveness assessment' },
            { from: 'SAL-06.1.2', artifact: 'ITT documentation analysis summary' },
            { from: 'SAL-06.2.1', artifact: 'Deal Qualification Checklist (DQC)' },
            { from: 'SAL-06.2.2', artifact: 'Strategic fit assessment' },
            { from: 'SAL-06.2.3', artifact: 'PWIN score and rationale' },
            { from: 'SAL-06.2.4', artifact: 'Win strategy narrative' }
          ],
          outputs: [
            {
              name: 'Capture plan document',
              format: 'Comprehensive strategy document',
              quality: [
                'Covers all dimensions: customer intelligence, competitive landscape, stakeholder position, win strategy, scoring approach, solution direction, commercial framework, risk, resources',
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
          id: 'SAL-06.3.2',
          name: 'Prepare formal Bid Mandate for Bid Board approval — budget, resource, win strategy, risk, PWIN, go/no-go recommendation',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: 'Commercial Lead / Legal', i: 'Partner' },
          inputs: [
            { from: 'SAL-06.3.1', artifact: 'Capture plan document' },
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
          id: 'SAL-06.3.3',
          name: 'Confirm lock — capture plan baselined, win strategy locked, methodology gate passed. Feeds GOV-01 (Pursuit Approval)',
          raci: { r: 'Bid Director', a: 'Senior Responsible Executive', c: null, i: 'Bid Team (collective)' },
          inputs: [
            { from: 'SAL-06.3.1', artifact: 'Capture plan document' },
            { from: 'SAL-06.3.2', artifact: 'Bid Mandate document' }
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
    { activity: 'COM-01', consumes: 'Capture plan (locked)', usage: 'Should-cost model informed by commercial framework and payment mechanism from capture plan' }
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
                'Key messages aligned to each stakeholder's known priorities',
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

*Gold standard established from SAL-03 — Session 11, 2026-04-01*
*SAL workstream complete — Session 12, 2026-04-01*
*SOL workstream complete — Session 12, 2026-04-01*
*Aligned with: Architecture v6, Plugin Architecture v1.2, Methodology Data Model (Session 10)*
