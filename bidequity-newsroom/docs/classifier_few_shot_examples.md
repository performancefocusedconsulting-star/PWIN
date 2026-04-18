# Classifier few-shot examples

Version: v1.0 · April 2026

These examples are appended to the classifier system prompt. They anchor the rubric by showing how the full rubric is applied to realistic items across the score distribution, sectors, and signal types.

Each example follows the same structure:

1. **Context** — who the source is and why it was ingested
2. **Input** — the item as the classifier would see it (title, source, body preview, metadata)
3. **Expected output** — the complete classifier JSON response
4. **Why this score** — one paragraph of reasoning (for prompt-engineering reference only; not fed to the model)

The eight examples span scores 2, 4, 6, 7, 8, 9, 10, and one deliberate edge case (cross-sector ambiguity).

---

## Example 1 — Score 10 · High-signal procurement · Defence

### Context
A major UK defence procurement ITT has been formally released. This is the top of the funnel for pursuit intelligence: direct, named, immediate commercial signal.

### Input

```
Title: SKYNET 6 Enduring Capability — Invitation to Negotiate released
Source: Defence Digital blog (MOD)
URL: https://defencedigital.blog.gov.uk/2025/08/20/skynet-6-itn-released/
Published: 2025-08-20
Sector tag: Defence

Body preview:
The SKYNET 6 Enduring Capability project has released the final
Invitation to Negotiate for the Wideband Satellite System. This is a
significant milestone in delivering the UK's next generation of
military satellite communications. Bidders shortlisted during the
competitive dialogue phase have been notified. The contract
opportunity is valued in the £6bn range over the capability lifetime
and supports UK industrial capacity through a layered prime and
subsystem structure. Responses are due by Q2 2026 with contract award
targeted for late 2026.
```

### Expected output

```json
{
  "relevance_score": 10,
  "signal_strength": "high",
  "signal_type": "procurement",
  "sectors": ["Defence"],
  "buyers_mentioned": ["MOD", "Defence Digital"],
  "suppliers_mentioned": [],
  "programmes_mentioned": ["SKYNET 6", "Wideband Satellite System"],
  "summary": "MOD's Defence Digital has released the final ITN for SKYNET 6 Wideband Satellite System, a multi-billion pound military satcom programme with award targeted late 2026.",
  "pursuit_implication": "Shortlisted primes should be fully resourced now; sub-prime bid opportunities for specialist subsystems will open within 8-12 weeks as primes finalise teaming arrangements. Firms not in dialogue should reassess Tier-2 positioning rather than chase the prime.",
  "content_angle_hook": "What SKYNET 6's ITN release reveals about MOD's procurement cadence under Defence Reform — and why late entrants are already too late."
}
```

### Why this score
Direct, named, dated procurement signal in a core BidEquity sector. Active multi-billion pound contract with identifiable Tier-1 and Tier-2 pursuit implications. Content angle writes itself from the data. This is exactly what the system should surface.

---

## Example 2 — Score 9 · Oversight with programme implication · Justice

### Context
National Audit Office reports on in-flight government programmes are strong leading indicators of remediation spend and scope change. Justice sector programmes are a BidEquity core vertical.

### Input

```
Title: The Common Platform: progress and risks in modernising the
criminal courts
Source: National Audit Office
URL: https://www.nao.org.uk/reports/common-platform-2026
Published: 2026-03-14
Sector tag: Justice

Body preview:
This report examines progress on HMCTS's Common Platform programme,
which has now been in delivery since 2013. The programme has
experienced repeated schedule slippage and functional limitations,
with an estimated £320m of additional spend required to complete
outstanding scope. We find that HMCTS has not adequately planned for
the transition of legacy systems, and that user confidence among
court staff has fallen materially over the reporting period. We
recommend that MoJ and HMCTS develop a full re-baseline and publish
an updated business case by September 2026.
```

### Expected output

```json
{
  "relevance_score": 9,
  "signal_strength": "high",
  "signal_type": "oversight",
  "sectors": ["Justice"],
  "buyers_mentioned": ["HMCTS", "MoJ", "NAO"],
  "suppliers_mentioned": [],
  "programmes_mentioned": ["Common Platform"],
  "summary": "NAO has flagged £320m of additional spend required on HMCTS's Common Platform and recommended a full re-baseline by September 2026, following repeated schedule slippage.",
  "pursuit_implication": "Expect discrete remediation procurements within 6 months — likely broken into smaller lots to avoid further integrator risk. Firms with court-systems experience should be preparing capability statements now. Current integrator's position is weakened.",
  "content_angle_hook": "The Common Platform at 13: why NAO's re-baseline recommendation creates a rare opening in a previously locked-down HMCTS pursuit landscape."
}
```

### Why this score
NAO reports on active programmes are the highest-signal oversight content. Named programme, named buyer, specific financial figure, clear pursuit implication around remediation. Not a 10 because the procurement has not yet been announced; the signal is leading rather than immediate.

---

## Example 3 — Score 8 · Policy / Leadership · Central Government

### Context
A major cross-government strategy document. Foundational for 18-month pursuit positioning but not immediately actionable on its own.

### Input

```
Title: Blueprint for a Modern Digital Government — roadmap published
Source: Government Digital Service blog
URL: https://gds.blog.gov.uk/2026/01/20/blueprint-roadmap/
Published: 2026-01-20
Sector tag: Central Gov

Body preview:
This week, we published our roadmap for modern digital government,
setting out how teams across government are transforming public
services through joined-up platforms, AI adoption, stronger digital
infrastructure, investment in talent, smarter funding, and greater
transparency. The roadmap is structured around six missions and
sixteen commitments, with associated delivery milestones through to
2028. Key commitments include the consolidation of identity services
under GOV.UK One Login, the expansion of the GOV.UK App, and the
introduction of a cross-government AI procurement framework.
```

### Expected output

```json
{
  "relevance_score": 8,
  "signal_strength": "high",
  "signal_type": "policy",
  "sectors": ["Central Gov"],
  "buyers_mentioned": ["GDS", "DSIT"],
  "suppliers_mentioned": [],
  "programmes_mentioned": ["GOV.UK One Login", "GOV.UK App"],
  "summary": "GDS has published a roadmap for modern digital government with six missions and sixteen commitments to 2028, including a cross-government AI procurement framework.",
  "pursuit_implication": "The cross-government AI framework is the most immediate commercial signal — firms in the AI enablement space should map their capability against the sixteen commitments and prepare for pre-market engagement in H2 2026. One Login consolidation signals continued vendor rationalisation.",
  "content_angle_hook": "Sixteen commitments, one pursuit question: which of these is a framework opportunity and which is a closed in-house build?"
}
```

### Why this score
Strategy document sets direction for the next two years of central-gov digital spend. High signal because several commitments will translate into procurements. Not a 9 because the commitments are not yet specified as named procurements with timelines.

---

## Example 4 — Score 7 · Contextual · Health & Social Care

### Context
A think-tank analysis on an adjacent topic. Informs commentary and positioning but doesn't indicate immediate procurement.

### Input

```
Title: NHS Federated Data Platform: one year on
Source: The Health Foundation
URL: https://www.health.org.uk/publications/fdp-one-year-on
Published: 2026-02-05
Sector tag: Health

Body preview:
The Federated Data Platform, launched by NHS England in late 2024,
has now been operational across twenty-five integrated care boards.
This analysis draws on interviews with ICB data leaders and examines
the clinical, operational, and commercial implications of the FDP's
architecture. We find mixed evidence on cross-ICB interoperability,
and raise questions about the commercial sustainability of the
single-vendor model as contracts approach their first break points in
2027.
```

### Expected output

```json
{
  "relevance_score": 7,
  "signal_strength": "medium",
  "signal_type": "policy",
  "sectors": ["Health"],
  "buyers_mentioned": ["NHS England"],
  "suppliers_mentioned": [],
  "programmes_mentioned": ["Federated Data Platform", "FDP"],
  "summary": "The Health Foundation has examined the FDP's first year, finding mixed interoperability evidence and flagging commercial questions about the single-vendor model ahead of 2027 break points.",
  "pursuit_implication": "Gives intellectual ammunition to firms positioning for FDP Phase 2 or adjacent ICB data work. Not an immediate procurement signal but a strong framing piece for LinkedIn commentary on incumbency risk in NHS digital.",
  "content_angle_hook": "The FDP's 2027 break point isn't a renewal — it's a re-compete. Here's what the Health Foundation's analysis tells us about where the incumbent is vulnerable."
}
```

### Why this score
Contextual — it shapes commentary rather than indicates immediate spend. Score 7 because it's a high-quality analysis of an active, named programme with a specific future commercial event (break point). If this were a routine update with no commercial angle, it would be a 5.

---

## Example 5 — Score 6 · Programme update from an official blog · Emergency Services

### Context
Home Office Digital blog post about ESN (Emergency Services Network) progression. Useful context but widely reported; finding a fresh pursuit angle is hard.

### Input

```
Title: ESN user device roll-out: quarterly update
Source: Home Office Digital blog
URL: https://hodigital.blog.gov.uk/2026/03/28/esn-device-rollout-q1/
Published: 2026-03-28
Sector tag: Emergency Services

Body preview:
This quarter we've continued to progress the roll-out of ESN user
devices across police forces in the North West region. Devices
delivered in the quarter reached 14,000, bringing the cumulative
total to 63,000 since the revised programme baseline. We continue to
work closely with force control rooms on the transition from Airwave
and have addressed a number of interoperability issues flagged in Q4.
```

### Expected output

```json
{
  "relevance_score": 6,
  "signal_strength": "medium",
  "signal_type": "leadership",
  "sectors": ["Emergency Services"],
  "buyers_mentioned": ["Home Office"],
  "suppliers_mentioned": [],
  "programmes_mentioned": ["ESN", "Emergency Services Network", "Airwave"],
  "summary": "Home Office reports 14,000 ESN user devices delivered in Q1, cumulative 63,000, with Airwave transition continuing in the North West and Q4 interoperability issues addressed.",
  "pursuit_implication": "Incremental progress. The more interesting pursuit question is the downstream tail — what comes after the prime device contract? Control-room integration, training, body-worn adjacency all remain open.",
  "content_angle_hook": "63,000 devices in, 250,000 to go. The real ESN pursuit opportunity is in what surrounds the device, not the device itself."
}
```

### Why this score
Programme update with medium signal. Worth commentary but the angle requires work — the raw content is more reporting than insight. Score 6 reflects that it's useful context but not automatically content-worthy without operator framing.

---

## Example 6 — Score 4 · Ambient news · Transport

### Context
Trade press coverage of a transport-sector topic that is genuinely news but doesn't map to BidEquity's pursuit-intelligence remit.

### Input

```
Title: Great British Railways transition hits new delay
Source: RailBusinessDaily
URL: https://railbusinessdaily.com/gbr-transition-delay-2026
Published: 2026-04-02
Sector tag: Transport

Body preview:
The transition to Great British Railways has been pushed back a
further six months, with the Department for Transport citing
complexity in the consolidation of passenger operator contracts.
Industry observers have expressed concern that the delay will affect
already-strained investment timelines for station refurbishment and
ticketing modernisation programmes.
```

### Expected output

```json
{
  "relevance_score": 4,
  "signal_strength": "low",
  "signal_type": "policy",
  "sectors": ["Transport"],
  "buyers_mentioned": ["DfT"],
  "suppliers_mentioned": [],
  "programmes_mentioned": ["Great British Railways"],
  "summary": "GBR transition delayed a further six months, affecting downstream station refurbishment and ticketing modernisation timelines.",
  "pursuit_implication": "Transport is not a current BidEquity priority sector. Delay affects in-flight programmes but does not open clear new pursuit avenues for target clients.",
  "content_angle_hook": null
}
```

### Why this score
Genuine news; low relevance to BidEquity's remit. Transport programmes are on the edge of scope and rail is particularly specialist. Score 4 reflects ambient awareness — the operator should know it happened — without triggering a content draft.

---

## Example 7 — Score 2 · Off-topic · Cross-sector

### Context
An item that surfaced through RSS but is not relevant to BidEquity. The classifier should drop it cleanly without wasting downstream generation budget.

### Input

```
Title: Civil Service careers fair returns to Birmingham
Source: Civil Service World
URL: https://www.civilserviceworld.com/news/article/birmingham-careers-fair
Published: 2026-04-10
Sector tag: Central Gov

Body preview:
The annual Civil Service careers fair returns to Birmingham's ICC on
15 May 2026, with more than thirty departments attending and
dedicated streams for Fast Stream applicants, experienced-hire
candidates, and apprenticeship routes. Registration opens this week.
```

### Expected output

```json
{
  "relevance_score": 2,
  "signal_strength": "low",
  "signal_type": "other",
  "sectors": ["Central Gov"],
  "buyers_mentioned": [],
  "suppliers_mentioned": [],
  "programmes_mentioned": [],
  "summary": "Civil Service annual careers fair to be held at Birmingham ICC on 15 May 2026.",
  "pursuit_implication": "No pursuit relevance.",
  "content_angle_hook": null
}
```

### Why this score
Workforce event, no procurement or policy signal, no content hook. This is the kind of item the pre-filter should catch first, but occasionally one slips through — the classifier correctly scores it low and it is dropped.

---

## Example 8 — Edge case · Score 7 · Cross-sector ambiguity · Local Gov + Health

### Context
Items that span two sectors (most often Local Gov and Health, given the social care interface) need careful sector tagging. The classifier should tag both sectors rather than picking one arbitrarily.

### Input

```
Title: Greater Manchester adult social care commissioning review
Source: Local Government Chronicle
URL: https://www.lgcplus.com/gmca-social-care-review-2026
Published: 2026-03-10
Sector tag: Local Gov

Body preview:
Greater Manchester Combined Authority has announced a strategic
review of adult social care commissioning across its ten constituent
councils. The review, running to September 2026, will assess current
provider concentration, pricing pressure from 2025's fair cost of
care exercise, and the integration opportunity presented by pooled
arrangements with the Greater Manchester Integrated Care Partnership.
An early-market engagement event for providers and strategic partners
is scheduled for May 2026.
```

### Expected output

```json
{
  "relevance_score": 7,
  "signal_strength": "high",
  "signal_type": "procurement",
  "sectors": ["Local Gov", "Health"],
  "buyers_mentioned": ["Greater Manchester Combined Authority", "GMCA", "Greater Manchester Integrated Care Partnership"],
  "suppliers_mentioned": [],
  "programmes_mentioned": [],
  "summary": "GMCA has launched a strategic review of adult social care commissioning across ten councils to September 2026, with early-market engagement scheduled for May 2026.",
  "pursuit_implication": "Pre-market engagement is the buy-signal. Firms with adult social care commissioning, pooled-budget, or ICP interface experience should register for the May event. The scope of the eventual procurement is being shaped now.",
  "content_angle_hook": "Adult social care commissioning reviews are where the next generation of major local-gov contracts are being scoped. GMCA's May engagement is the moment to get into the room."
}
```

### Why this score
Genuine cross-sector item. The correct classifier behaviour is to tag both Local Gov and Health rather than forcing a single category. Score 7 because the pre-market engagement gives a concrete commercial signal without a formal procurement yet being announced. Illustrates for the model that multi-sector tagging is expected and correct.

---

## Implementation notes

When these examples are appended to the classifier system prompt:

- Include all eight regardless of input item — they collectively anchor the full rubric
- Do not reorder them; the deliberate sequence (10 → 9 → 8 → 7 → 6 → 4 → 2 → edge case) shows the rubric applied descending
- The "Why this score" sections are for maintainer reference and should **not** be included in the prompt to the model
- Store each example in a separate file in `/prompts/classifier/examples/` (e.g. `01_defence_procurement.md`) to allow individual review and replacement without rebuilding the whole set
- Re-evaluate annually or when the sector priorities change materially
