# Source Hierarchy, Confidence Calibration, and Evidence Quality

This reference defines the 5-tier source hierarchy, confidence calibration
thresholds, source freshness rules, and rationale quality standards.

---

## 5-Tier Source Hierarchy

| Tier | Source class | Use for | Reliability |
|------|-------------|---------|-------------|
| **1** | Authoritative buyer sources — what the buyer says about itself | Facts and stated priorities | high |
| **2** | Centre-of-government sources — the rules the buyer operates under | Funding envelope, controls, standards, policy context | high |
| **3** | External scrutiny sources — independent reality-check | Risk, sensitivities, programme performance | high |
| **4** | Market and procurement intelligence — how they actually buy | Supplier landscape, buying behaviour, contract patterns | high |
| **5** | Relationship intelligence — internal account-team knowledge | Advocates, blockers, prior delivery context, account history | high (when available) |

### Tier 1 — Authoritative buyer sources

The buyer's own published material. Use for stated mandate, strategy,
priorities, leadership, performance reporting, and procurement intent.

- Annual Report and Accounts
- Outcome Delivery Plan / Single Departmental Plan / Corporate Plan
- Departmental strategy / corporate plan
- Procurement page (`gov.uk/.../doing-business-with-us`)
- Commercial pipeline / pipeline notices
- Tender notices (Find a Tender)
- Award notices (Find a Tender, Contracts Finder)
- Digital / data / AI strategy
- Cyber security strategy
- Workforce / People plan
- Estate / property / sustainability strategy
- Official statistics and dashboards
- Service performance reports
- Governance Statement (within Annual Report)

### Tier 2 — Centre-of-government sources

The funding envelope, fiscal controls, commercial standards, and policy
playbooks the buyer operates within. Use for understanding what they must do,
what they can spend, what they must comply with.

- Spending Review settlement
- Main and Supplementary Estimates
- Budget statement / fiscal forecast
- Cabinet Office commercial guidance (Sourcing Playbook, contract standards)
- HM Treasury Green Book and Managing Public Money
- DDaT Playbook
- AI Playbook / AI Action Plan
- Digital assurance guidance (CDDO, GDS Service Standard)
- Government Functional Standards (GovS series)
- Spend control thresholds and approvals
- Major Projects Portfolio data (IPA / GMPP)

### Tier 3 — External scrutiny sources

Independent assessment of the buyer's performance, programmes, and value-for-
money. Use for reality-checking the buyer's own narrative and surfacing risk
and sensitivities the buyer would not voluntarily disclose.

- National Audit Office (NAO) value-for-money reports
- Public Accounts Committee (PAC) reports
- Departmental Select Committee reports
- Inspectorate reports (CQC, Ofsted, HMICFRS, HMIP, etc.)
- Regulator reports (where the regulator has remit over the buyer)
- Ombudsman reports
- Independent reviews / commissions
- Internal audit summaries (where published)

### Tier 4 — Market and procurement intelligence

Structured procurement data showing how the buyer actually behaves in the
market — not what they say, but what they do.

- Find a Tender (FTS) — full notice corpus
- Contracts Finder
- Tussell or equivalent commercial procurement databases
- Framework award data (CCS frameworks, NHS frameworks, sector frameworks)
- Spend transparency data (>£25k publication)
- Contracts register
- pwin-platform internal procurement layer (FTS-derived signals,
  buyer-behaviour profile, supplier ecosystem)

### Tier 5 — Relationship intelligence

Internal account-team knowledge. Tier 5 data is not retrievable by web
research and only enters the dossier through **amend** mode (or, rarely,
**inject** mode for internal documents).

- CRM / account plan
- Bid library entries for prior pursuits against this buyer
- Prior bid feedback and debrief letters
- Account team interview notes
- Delivery team interview notes
- Stakeholder maps / influence diagrams
- Internal meeting notes
- Capture intel logs

In most initial builds, no Tier 5 data is available. Flag this in
`relationshipHistory.tierNote` and populate the action register with
specific Tier 5 amend asks.

---

## Tier-to-section affinity

Different sections of the dossier are reliably populated from different tiers.
Use this table to plan retrieval depth and to spot when a section is being
populated from the wrong source class.

| Dossier section | Primary tier | Secondary tier(s) |
|---|---|---|
| `buyerSnapshot` | Tier 1 | Tier 2 |
| `organisationContext` | Tier 1 | Tier 3 |
| `strategicPriorities` | Tier 1 | Tier 2, Tier 3 |
| `commissioningContextHypotheses` | Tier 1 | Tier 2, Tier 3 |
| `procurementBehaviour` | Tier 4 | Tier 1 |
| `procurementBehaviourSnapshot` | Tier 4 | — |
| `decisionUnitAssumptions` | Tier 1 | Tier 5 (amend) |
| `cultureAndPreferences` | Tier 1 | Tier 3 |
| `commercialAndRiskPosture` | Tier 1 | Tier 2, Tier 3 |
| `supplierEcosystem` | Tier 4 | Tier 3 (vulnerability signals) |
| `relationshipHistory` | Tier 5 | — |
| `risksAndSensitivities` | Tier 3 | Tier 1 |
| `pursuitImplications` | Synthesised across all tiers | — |

If a section is being populated only from Tier 3 (media or analysis), that's
a freshness/reliability flag — push for a Tier 1 source if available, or
mark the section confidence accordingly.

---

## Confidence Calibration

These thresholds ensure consistent confidence ratings across runs and
analysts.

| Confidence | Criteria |
|---|---|
| `high` | Corroborated by 2+ Tier 1–2 sources published within 2 years, OR Tier 4 procurement data with >12 months coverage and consistent pattern |
| `medium` | Single Tier 1–2 source, OR Tier 3 only, OR older than 2 years but corroborated, OR Tier 4 with patchy coverage |
| `low` | Inferred from indirect evidence, single Tier 3 source, single Tier 5 source, or any source older than 3 years |

When assessing confidence, consider both source quality and recency. A single
Tier 1 source from last year is `medium`. Two Tier 1 sources from last year
is `high`. A Tier 3 media report from 4 years ago is `low`. A Tier 5 (account
team) source counts as `medium` by default unless the user indicates
uncertainty.

### Cross-tier corroboration

The strongest evidence is **Tier 1 + Tier 4** corroboration: the buyer says
they prefer framework call-offs (Tier 1 strategy doc), and 80% of awards in
the data confirm it (Tier 4). When Tier 1 and Tier 4 disagree, Tier 4 wins
on what the buyer *actually does*; Tier 1 may still win on what they
*intend* to do (forward-looking).

When Tier 1 and Tier 3 disagree, the disagreement is itself the finding —
record both and surface the gap as a pursuit implication.

---

## Source Freshness Rules

- **Flag any source older than 3 years** in `sourceRegister.staleFields`.
- **Treat findings from stale sources** as `confidence: "low"` and note the
  age in the rationale.
- A 2019 document cited in 2026 is not current evidence — it may indicate a
  historical position that has since changed.
- When a stale source is the only evidence for a field, set
  `type: "inference"` (not `fact`) and note the age risk.
- Stale Tier 4 procurement data is special-cased: a 4-year-old award notice
  is still evidence of *what was awarded* (a fact), but is weak evidence of
  *current buying behaviour* (which is the inference layer above the awards).

### Re-derivation triggers

A stale field should be added to the action register with type `refresh` and
a recommended next step naming the document or signal that would refresh it:

- Strategic priorities stale → look for a refreshed strategy document, the
  current Outcome Delivery Plan, or the most recent ministerial speech.
- Procurement behaviour stale → the snapshot section is auto-refreshed each
  build; if a stale field persists, it usually means the buyer has had no
  recent activity, which is itself a signal.
- Leadership stale → check the buyer's website for current SRO and
  permanent secretary, plus LinkedIn appointment announcements.

---

## Rationale Quality

The `rationale` field in the evidence wrapper must explain the specific
evidence chain, not restate that evidence exists.

### Strong rationale example

> "Inferred from three consecutive call-offs under CCS RM6187 with no
> open-market FTS procedures in 4 years, consistent with the buyer's stated
> 'route-to-market efficiency' commitment in their 2024 commercial strategy
> (SRC-003). The absence of open competition and reliance on a single
> framework suggests framework-first procurement behaviour."

This is strong because it names the specific signals (three call-offs, no
open procedures, a policy statement), connects them logically, and explains
the reasoning step.

### Weak rationale example

> "Inferred from available procurement data."

This adds nothing. It does not name which data, which pattern, or why that
pattern supports the conclusion. Always name the specific signals and explain
the reasoning step.

### Rationale checklist

A good rationale should:
1. Name the specific evidence (document name, data pattern, or observation)
2. Explain why that evidence supports the conclusion
3. Note any caveats or alternative explanations if relevant
4. Reference source IDs so the reader can verify

---

## Migration from v2.2 (4-tier) to v3.0 (5-tier)

The v2.2 schema treated CRM, account plans, prior bids, and account-team
intel as Tier 4 (alongside FTS data). v3.0 separates these:

- **Old Tier 4** → split into **new Tier 4** (market/procurement intelligence)
  and **new Tier 5** (relationship intelligence).
- Existing `SRC-INT-nnn` source IDs stay as-is — they map cleanly to Tier 5.
- Existing Tier 4 procurement-data sources stay as Tier 4.
- Existing dossiers do not need a tier renumbering pass; new sources adopt
  the 5-tier model going forward.
