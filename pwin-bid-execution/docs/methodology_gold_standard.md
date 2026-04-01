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

*Gold standard established from SAL-03 — Session 11, 2026-04-01*
*SAL-10 added — Session 12, 2026-04-01*
*Aligned with: Architecture v6, Plugin Architecture v1.2, Methodology Data Model (Session 10)*
