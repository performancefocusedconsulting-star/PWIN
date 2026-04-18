# Debate specifications for stance detection

Version: v1.0 · April 2026
Audience: Claude Code (seed content for `/prompts/debates/`) and BidEquity editorial

Each live debate has its own spec file in `/prompts/debates/{debate_id}.md`. The classifier loads the active debate specs at classification time. For each item, the classifier determines (a) whether the item is relevant to this debate at all, and if so (b) where the item's position sits on the five-point stance scale from strongly critiques (-2) to strongly supports (+2).

The three debates below are starter content — genuinely live in UK public-sector discourse right now, aligned to BidEquity's content remit. Add or retire debates in the dashboard. Don't exceed five active debates at once; the prompt cost scales with the number of active debates and five is more than enough live questions to hold editorial attention.

---

## Debate 001: Centralised vs federated AI procurement in government

**Debate ID:** `ai-procurement-centralisation`
**Parent topic:** `ai-public-sector`
**Status:** Active
**Opened:** April 2026

### The question

Should UK government AI procurement be consolidated into a single cross-government framework, or should departments retain significant discretion over their own AI procurement approach?

### Why this matters

DSIT, working with GDS and GCA, is developing a cross-government AI procurement framework targeted for Q3 2026 launch. The framework would consolidate purchasing power, simplify supplier onboarding, and provide assurance that AI products meet the AI Playbook's standards. However, it also risks vendor concentration, reduces departmental autonomy, and may be too slow for fast-moving AI capabilities.

This is a live, unsettled debate with material commercial implications. The outcome shapes which firms win AI work in government — consolidated winners or departmental specialists.

### The two poles

**Pole A — centralisation (+2 strongly supports / +1 supports)**

The centralised framework is the right approach. Arguments you'd see:

- Government needs consistent AI safety evaluation — impossible if every department buys differently
- Centralised purchasing gives better pricing, consistent contract terms, and clearer SME routes
- The AI Playbook's standards need a common procurement mechanism to be enforced
- Fragmented procurement creates inconsistent risk management across sensitive AI applications
- Departments lack the specialist AI commercial knowledge to buy well individually

**Pole B — federation (-2 strongly critiques / -1 critiques)**

Departmental discretion is the right approach. Arguments you'd see:

- Central frameworks move slower than AI capability evolves; lock-in on outdated tech is the risk
- Vendor concentration is a strategic risk — a single compromised framework becomes a single compromised government
- Different use cases need different suppliers; a generalist framework serves none of them well
- Departmental commercial teams are closer to their own use cases than centre
- Historical centralised frameworks (G-Cloud, DOS) have had well-documented performance issues with fast-moving capability areas

### Neutral / descriptive (0)

An item describing the framework, reporting on its development, or presenting facts without taking a position.

### What counts as evidence on each side

**Evidence for centralisation:**
- Authors from GDS, DSIT, Cabinet Office, GCA
- References to AI Playbook, AI Opportunities Action Plan, Algorithmic Transparency Recording Standard
- Language of "consistency", "assurance", "single source", "cross-government standards", "economies of scale"
- Framing around risk management and safety consistency

**Evidence for federation:**
- Authors from Institute for Government, Ada Lovelace, Alan Turing, techUK
- References to G-Cloud/DOS performance issues, vendor concentration concerns, procurement agility
- Language of "flexibility", "speed", "departmental autonomy", "innovation", "vendor lock-in"
- Framing around market dynamics, competition, and agility

### Worked examples

**Example 1 — Strongly supports centralisation (+2)**

Hypothetical item: A DSIT blog post announcing the cross-government AI procurement framework launch date, authored by the DSIT Director of AI Adoption.

> "The cross-government AI procurement framework launches in September, establishing consistent standards for AI safety evaluation and vendor assessment across all central departments. For the first time, every department will buy AI under a common assurance regime, aligned to the AI Playbook. This is a critical step in responsible AI adoption at scale."

Stance: +2. Clearly framed in the language of centralisation benefits, from a central-government source, with explicit endorsement of the consolidation approach.

**Example 2 — Critiques centralisation (-1)**

Hypothetical item: An Institute for Government analysis of the proposed framework.

> "The proposed framework addresses a real assurance gap. However, the experience of G-Cloud and DOS suggests that framework rigidity tends to favour incumbents, slow innovation, and concentrate risk in a small number of large vendors. If the framework is to avoid these pitfalls, it needs to include explicit provisions for rapid capability refresh, meaningful SME lots, and periodic market testing."

Stance: -1. The item is not hostile to the framework but flags substantive concerns based on historical evidence. Expresses critique within a constructive frame.

**Example 3 — Neutral / descriptive (0)**

Hypothetical item: A Public Technology news piece reporting on an industry engagement day for the framework.

> "DSIT held an industry engagement day on 14 April for suppliers interested in the forthcoming cross-government AI procurement framework. Around 120 suppliers attended. DSIT's commercial lead confirmed the framework will launch in September with initial lot awards later in the autumn."

Stance: 0. Factual reporting with no editorial position. Classifier should mark this as "relevant to debate, no stance".

**Example 4 — Strongly critiques centralisation (-2)**

Hypothetical item: A techUK policy paper calling for departmental AI procurement autonomy.

> "Centralised AI procurement at this stage of the technology's evolution will lock government into commitments that date within 24 months. The AI capability landscape is moving faster than any framework can refresh. techUK members report that departmental AI pilots are producing materially better outcomes than centrally-procured commodity solutions. We call on DSIT to pause the framework and instead strengthen departmental AI commercial capability."

Stance: -2. Explicit opposition, with concrete recommendations against the centralisation approach.

### Classifier instructions

When classifying an item:

1. First determine: is this item genuinely about AI procurement in UK government? If not, mark `debate_relevant: false` and skip stance assessment.
2. If relevant, assess the item's position on the spectrum. Consider the overall tone, the source's usual positioning, and specific language used.
3. Ambiguous items (equal evidence on both sides, or genuinely balanced analysis) should be marked stance: 0 with `confidence: low`.
4. Extract one supporting excerpt (max 200 chars) that best illustrates the stance. This becomes `item_stances.excerpt`.

### Expected data patterns over time

If the classifier is well-calibrated, we'd expect:

- Central government authors skewing positive
- Think tanks (especially IfG, Ada Lovelace) skewing mildly negative
- Trade press skewing neutral/descriptive
- Industry bodies (techUK) mixed, depending on whether the piece is from their public affairs team or their member-facing programme team

Deviation from this pattern is interesting and worth investigating.

---

## Debate 002: Incumbent continuation vs re-compete on large NHS digital programmes

**Debate ID:** `nhs-digital-incumbency`
**Parent topic:** `nhs-fdp-data`
**Status:** Active
**Opened:** April 2026

### The question

Should large NHS digital programmes (FDP, EPRs, shared service platforms) continue with their current suppliers past their initial contract terms, or should they be aggressively re-competed at every opportunity?

### Why this matters

NHS England's Federated Data Platform first break point arrives in 2027. The incumbent has delivered controversial but functional service; re-competing risks delivery disruption but reduces single-vendor dependency. The same pattern repeats across NHS shared IT, Trust-level EPR consolidation, and NHSE operational platforms.

For BidEquity, this is the single most important live commercial question in NHS digital. It determines whether incumbents or challengers win the next wave.

### The two poles

**Pole A — continuity (+2 strongly supports / +1 supports)**

Incumbents should continue past initial break points. Arguments you'd see:

- Delivery disruption is the dominant risk in large NHS programmes; continuity preserves operational stability
- The learning cost of switching is enormous; new suppliers restart from zero on NHS data complexity
- The NHS cannot afford parallel-running costs during transitions
- Incumbents have built the integrations, the workflows, the trust — all of which transfer poorly
- Re-competing every few years makes suppliers unwilling to invest in NHS-specific capability

**Pole B — re-compete (-2 strongly critiques / -1 critiques)**

Programmes should be re-competed at every break point. Arguments you'd see:

- Single-vendor lock-in is a strategic risk, politically and commercially
- Re-competes are the only mechanism for price discipline; incumbents extract monopoly rents
- The market has moved on — newer suppliers may offer materially better capability at lower price
- Public-sector procurement law exists to ensure open competition; waivers are the exception, not the rule
- Incumbent comfort breeds delivery complacency; competitive pressure is the only reliable discipline

### What counts as evidence on each side

**Evidence for continuity:**
- Authors from NHS England operations, ICB CIOs, trust DDaT leads
- Language of "stability", "continuity of care", "data integrity", "transition risk"
- References to programme-specific complexity and learning curves
- Arguments framed around patient safety risk

**Evidence for re-compete:**
- Authors from think tanks (Health Foundation, King's Fund, Nuffield), NAO, industry bodies
- Language of "competition", "value for money", "vendor concentration", "lock-in"
- References to cost, performance data, alternative suppliers
- Arguments framed around market discipline and taxpayer value

### Worked examples

**Example 1 — Strongly supports continuity (+2)**

Hypothetical item: A health service journal interview with an NHS England Director responsible for FDP.

> "The Federated Data Platform has taken three years of painstaking work to embed across the first 25 ICBs. Re-competing now would waste that investment and jeopardise the Phase 2 rollout. We are focused on continuity, deepening integration, and extracting the value we planned for at the outset."

Stance: +2. Clear commitment to the incumbent model, framed around the cost of switching.

**Example 2 — Critiques continuity (-1)**

Hypothetical item: A Health Foundation report on NHS data platform effectiveness.

> "The FDP has delivered functional value but at significant political and operational cost. As we approach the first contractual break point, NHS England should use the opportunity to stress-test the commercial arrangement. A genuine market test — even if it results in the incumbent's continuation — would strengthen rather than weaken the programme's legitimacy."

Stance: -1. Not hostile to the incumbent but argues for a genuine competitive process. Constructive critique.

**Example 3 — Strongly critiques continuity (-2)**

Hypothetical item: An NAO report finding on NHS IT procurement patterns.

> "We find that the pattern of single-source extensions in large NHS digital programmes has resulted in prices materially above market benchmarks and has limited the diversity of suppliers capable of working at scale in the NHS. We recommend NHS England adopt a default of open re-compete at each contractual break point, with exemption only on clearly evidenced grounds."

Stance: -2. Formal NAO recommendation explicitly against incumbent continuation.

### Classifier instructions

1. Assess relevance: is this about a large NHS digital programme at or near a contractual break point? If the item is about small-scale NHS tech procurement with no incumbency debate, mark not relevant.
2. Programmes that count as "large": FDP, NHS Spine, national EPR initiatives, shared service platforms above £50m contract value.
3. Distinguish between the technical content of a programme (not in scope) and the commercial arrangement (in scope).
4. Watch for implicit stance in sources that present as neutral — HSJ's editorial positioning, for instance, tends to support incumbent continuity but rarely says so explicitly.

---

## Debate 003: In-house build vs managed service for government digital capability

**Debate ID:** `govt-inhouse-vs-managed`
**Parent topic:** `digital-platforms-central`
**Status:** Active
**Opened:** April 2026

### The question

Should the UK central government build and run its own digital capability in-house (civil service developers, government-operated platforms), or procure capability as managed services from commercial suppliers?

### Why this matters

The Blueprint for Modern Digital Government is explicit about rebuilding internal capability — the push to hire into GDS and departmental DDaT functions, to run GOV.UK One Login and other platforms as government products. But the managed service pattern persists across DWP, HMRC, and the MOD. This is an ideological debate with real procurement consequences.

For firms pursuing government contracts, where the government sits on this spectrum determines whether you win platform work, partner on it, or get displaced by civil service insourcing.

### The two poles

**Pole A — in-house capability (+2 strongly supports / +1 supports)**

Government should build and run digital capability in-house. Arguments you'd see:

- Strategic capability cannot be outsourced; government needs to own the skills
- Outsourced services carry dependency risk and lock-in
- In-house teams produce better, cheaper, faster results at sustained scale (GDS flagship products cited as evidence)
- Civil service salaries can compete at most grades with good organisational design
- Taxpayer-funded development creates reusable national IP; outsourced work doesn't

**Pole B — managed services (-2 strongly critiques / -1 critiques)**

Government should procure managed services from the market. Arguments you'd see:

- Civil service struggles to compete for scarce technical talent at the top grades
- Private sector suppliers carry investment risk and bring capability the government cannot afford to develop
- In-house builds have a mixed track record; well-managed services have a better one
- Procurement frameworks exist to access market capability; using them is not a failure
- Government's core job is policy and service design, not running platforms

### What counts as evidence on each side

**Evidence for in-house:**
- Authors from GDS, department DDaT teams, IfG, civil service unions
- Language of "capability", "civil service skills", "ownership", "digital government as a function"
- References to successful in-house programmes (One Login, GOV.UK itself, Notify)
- Framing around state capability

**Evidence for managed services:**
- Authors from industry bodies (techUK), commercial suppliers, some think tanks
- Language of "market capability", "access to innovation", "specialist expertise", "flexibility"
- References to in-house programme difficulties (MoJ legacy systems, HMRC)
- Framing around pragmatism and market economics

### Worked examples

**Example 1 — Supports in-house (+1)**

Hypothetical item: A GDS blog post on the growth of digital roles across central government.

> "We've hired 2,200 new DDaT colleagues across government in the past 18 months, and the pay framework is letting us retain scarce senior technical talent. This investment in civil service capability is producing better, cheaper platform work than previous generations of the same function."

Stance: +1. Clear preference for the in-house model, supported by data on capability growth.

**Example 2 — Critiques in-house (-1)**

Hypothetical item: A techUK position paper on central government digital strategy.

> "Civil service digital teams have delivered important platform work, but the scale of the AI transformation, data infrastructure modernisation, and legacy remediation required cannot be delivered without substantial supplier partnership. An approach that assumes central government can build this alone will miss the window."

Stance: -1. Frames the in-house model as insufficient rather than wrong; argues for complementary market access.

**Example 3 — Neutral (0)**

Hypothetical item: A Commons Library briefing on the size of the DDaT profession in government.

> "The Digital, Data and Technology function in central government has grown from approximately 18,000 staff in 2022 to approximately 24,000 in 2026. The growth has been concentrated in the Home Office, DWP, and DSIT, alongside the expansion of GDS."

Stance: 0. Factual reporting. No editorial position on whether this growth is correct.

### Classifier instructions

1. This debate is particularly prone to false positives. Items about "digital capability" are not necessarily about the in-house vs managed service question. Only flag as relevant if the item addresses the organisational and commercial model, not just digital capability in general.
2. Many items will appear neutral but carry implicit stance via author affiliation. Weight author source when determining stance in ambiguous cases.
3. This debate is often proxied by other debates (AI centralisation, framework consolidation). Try to score the specific argument in the item, not the item's broader ideological framing.

---

## How these specs are used by the classifier

At classification time, the classifier receives (in addition to the normal classification prompt):

1. The list of active debates with their IDs, questions, and poles
2. The debate spec files for debates the item might plausibly be relevant to (pre-filtered on keyword overlap)
3. An instruction to return `item_stances[]` alongside the normal classification output

Expected classifier response extension:

```json
{
  ...normal classification fields...,
  "item_stances": [
    {
      "debate_id": "ai-procurement-centralisation",
      "relevant": true,
      "stance": -1,
      "confidence": 0.75,
      "excerpt": "The proposed framework addresses a real assurance gap. However...",
      "rationale_internal": "Source is IfG, known for mildly critical stance; language of G-Cloud precedent flags historical concern."
    }
  ]
}
```

Items are only scored against debates they're genuinely relevant to. Most items will have zero stance entries. Items relevant to multiple debates get multiple stance entries.

## Quality gates

Before each debate spec is activated in production:

1. **Worked examples pass review**: Paul manually scores 5 real items for the debate and compares against classifier output. 80% agreement required.
2. **False positive check**: Run the classifier over 100 unrelated items; fewer than 5 should be incorrectly flagged as relevant to the debate.
3. **Source bias audit**: After 30 days live, check that stance distribution by source matches expectations. Material deviation (e.g. IfG scoring +2 on average when expected -1) suggests the spec needs refinement.

## Lifecycle

Debates are not eternal. Each debate should be reviewed quarterly:

- **Still live?** If the question has been effectively resolved by policy or procurement decision, retire the debate
- **Still interesting?** If there's no editorial content flowing from it, retire regardless of whether it's technically unresolved
- **New debates?** If a new question has emerged that's driving content, draft a new spec

Retired debates are not deleted; they're marked inactive and retained in the database. Historical stance data remains queryable.
