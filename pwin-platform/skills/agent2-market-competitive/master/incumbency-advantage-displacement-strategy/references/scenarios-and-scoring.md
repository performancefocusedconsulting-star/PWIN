# Scenario Classification, Scoring Model & Decision Logic

This reference file is read by the agent during analysis steps 1, 5, and 10. It contains
the scenario types, scoring dimensions, decision rules, and judgement heuristics.

## Table of Contents

1. Incumbent Scenario Types
2. Scoring Model
3. Decision Logic
4. Judgement Heuristics

---

## 1. Incumbent Scenario Types

Classify the pursuit into exactly one scenario before proceeding with the assessment.
The scenario determines which playbook to apply and shapes the strategic frame.

### single_incumbent_prime
One incumbent prime supplier currently owns most or all of the relevant scope.
**Strategic implication:** Classic displacement assessment. Focus on incumbent advantage,
switching risk, and challenger differentiation.

### multi_incumbent
Multiple suppliers deliver different lots, towers, geographies, systems, or service lines.
**Strategic implication:** Do not generalise. Assess lot-by-lot or tower-by-tower
displacement feasibility. Some lots may be winnable while others are structurally
incumbent-favoured.

### incumbent_recompete
The bidder using this skill is the current incumbent.
**Strategic implication:** Flip into defensive strategy. Emphasise continuity, learning,
improvement, and next-phase value. Do not rely on relationship history alone.

### in_house_service
The current service is largely delivered internally by the buyer rather than by an external
supplier.
**Strategic implication:** Avoid replacement language. Position as enablement, augmentation,
transformation support, capability uplift, or risk-controlled transition. Assess internal
team dynamics — staff may resist outsourcing.

### fragmented_legacy_estate
Current delivery is split between in-house teams, legacy suppliers, tactical contracts,
and informal arrangements.
**Strategic implication:** Position integration, simplification, governance, and service
coherence. Assess transition complexity carefully — multiple handoffs, data sources, and
contractual relationships.

### jv_or_consortium_incumbent
The current incumbent is a joint venture, consortium, or formal partnering arrangement
between two or more suppliers.
**Strategic implication:** Assess whether the JV/consortium is cohesive or fractured. Partner
disagreements, scope redistribution, mixed performance across partners, and divergent
commercial interests can create displacement opportunities that do not exist with a single
prime. However, JV incumbents may also have broader capability coverage and deeper buyer
relationships than a single challenger. Assess each partner's contribution and any public
evidence of partnership strain.

### unknown_incumbent
Incumbent identity is unknown or unclear.
**Strategic implication:** Produce a conditional assessment framework, identify intelligence
gaps, and flag required validation actions. Do not fabricate incumbent details.

### no_true_incumbent
New service, new programme, or materially transformed requirement with no direct incumbent.
**Strategic implication:** Focus on legacy constraints, buyer maturity, adjacent suppliers,
internal operating model inertia, and whether any supplier has a first-mover or shaping
advantage.

---

## 2. Scoring Model

Score each dimension on a 1–5 scale. Every score must include a rationale and, where
applicable, source references.

| Score | Meaning |
|---|---|
| 1 | Very low / very weak |
| 2 | Low / weak |
| 3 | Moderate / mixed |
| 4 | High / strong |
| 5 | Very high / very strong |

### Scoring Dimensions

**incumbent_performance_strength**
How well the incumbent appears to be delivering against service expectations.
- High score (4–5): Incumbent appears to be delivering well, with strong buyer satisfaction signals or few credible weakness signals.
- Low score (1–2): Incumbent appears vulnerable due to evidenced performance, satisfaction, quality, or service issues.
- Score 3: Mixed signals or insufficient evidence to distinguish.

**relationship_embeddedness**
Depth of incumbent relationships with buyer stakeholders, operational teams, governance forums, and service users.
- High score: Strong relational advantage and buyer familiarity. Evaluators likely know incumbent personnel.
- Low score: Limited evidence of strong relationship lock-in. New buyer leadership or restructured teams may reduce this.

**operational_stickiness**
Degree to which incumbent knowledge, processes, informal workarounds, systems access, data, and routines are embedded in the buyer's operations.
- High score: Displacement would be operationally complex. The incumbent's departure would create knowledge gaps.
- Low score: Service is modular, well-documented, or more easily transferable.

**switching_complexity**
Transition difficulty, including TUPE, data migration, systems dependency, mobilisation, knowledge transfer, service continuity, and security clearance requirements.
- High score: Switching risk is a major go/no-go issue. TUPE, clearance lead times, or systems dependency create structural barriers.
- Low score: Switching appears manageable with standard mobilisation controls.

**buyer_change_appetite**
Evidence that the buyer genuinely wants change, transformation, improved outcomes, innovation, better value, or supplier challenge.
- High score: Buyer appears actively open to change. Procurement language signals transformation, new leadership is driving change, or public statements indicate dissatisfaction.
- Low score: Buyer appears to prefer continuity, is likely market testing, or shows signs of risk aversion.

**incumbent_vulnerability**
Strength of evidenced incumbent weaknesses that a challenger can legitimately position against.
- High score: Multiple credible, evidenced vulnerabilities exist (performance failures, audit findings, technology debt, user dissatisfaction).
- Low score: Few reliable vulnerability signals. Claimed weaknesses are mostly anecdotal.

**challenger_differentiation**
Whether the bidder has a credible alternative offer, proof points, sector credibility, price/value advantage, or transition capability.
- High score: Bidder can credibly offer better value or lower-risk transformation. Strong proof points and sector references.
- Low score: Bidder has limited differentiation, weak proof, or unproven claims.
- **SME note:** If the challenger is an SME, assess whether balance sheet requirements, past contract value thresholds, and mobilisation capacity create structural barriers beyond normal differentiation. An SME may have strong technical capability but fail financial and scale tests.
- **Large prime note:** If the challenger is a large prime, assess whether they risk looking like an expensive, risk-heavy alternative. A large prime displacing another large prime must show a step-change in value, not merely equivalence.

**requirements_bias_to_incumbent**
Degree to which procurement documents, service model, contract structure, or evaluation criteria appear to favour the current provider.
- High score: Procurement may be structurally favourable to the incumbent. Specification mirrors current service; evaluation criteria weight experience in this specific contract.
- Low score: Procurement appears genuinely open to alternative approaches. Outcome-based specification, innovation scoring, social value weighting.

**security_clearance_barrier** *(assess where Defence, Justice, or national security scope is involved)*
Whether security clearance requirements create a structural switching barrier.
- High score: SC or DV clearance required for key delivery roles. Incumbent team already cleared. Challenger would need 6–12 months for clearance processing, creating mobilisation delay and risk.
- Low score: BPSS or no specific clearance requirements, or challenger team already holds relevant clearances.

**social_value_advantage** *(assess where social value weighting exceeds 10%)*
Whether the incumbent has established social value commitments that a challenger cannot credibly replicate at bid stage.
- High score: Incumbent has existing local employment, apprenticeships, community programmes, and SME supply chain relationships. Social value weighting is 15%+ in evaluation.
- Low score: Social value weighting is low, or the incumbent's social value commitments are generic and replicable.

**incumbent_financial_health** *(assess where Companies House data or market signals are available)*
Financial stability of the incumbent supplier.
- High score: Incumbent is financially stable. No distress signals.
- Low score: Evidence of financial pressure — profit warnings, credit downgrades, workforce reductions, parent company instability. A distressed incumbent may create a displacement window if the buyer fears service continuity risk.

**displacement_feasibility**
Overall likelihood that the incumbent can realistically be displaced. This is a derived score
informed by all other dimensions, not an independent assessment.
- High score: Credible path to challenger win. Multiple factors favour displacement.
- Low score: Incumbent likely retains unless new intelligence emerges.

### Weighting Guidance

Not all dimensions carry equal weight. Apply this hierarchy:

**Highest importance** (these most often determine the outcome):
- buyer_change_appetite
- switching_complexity
- relationship_embeddedness
- requirements_bias_to_incumbent
- challenger_differentiation

**Medium importance** (these shape the picture but rarely override the above):
- incumbent_performance_strength
- incumbent_vulnerability
- operational_stickiness

**Contextual** (score these only where the specific conditions apply):
- security_clearance_barrier
- social_value_advantage
- incumbent_financial_health

---

## 3. Decision Logic

Apply these rules after scoring. Each condition maps to a recommendation and required actions.

### Condition 1: Strong incumbent, low buyer change appetite
**When:** Incumbent performance is strong (4–5), buyer change appetite is low (1–2), and
requirements appear to mirror the current service.
**Recommendation:** `no_go` or `selective_go`
**Rationale:** The opportunity may be a compliance re-procurement, price test, or defensive
re-compete. Challenger probability is low unless there is exceptional differentiation,
privileged intelligence, or a material price/value advantage.
**Required actions:**
- Test buyer appetite for change before full bid investment
- Review specification for incumbent bias
- Identify whether any lot, workstream, or service tower is more contestable
- Do not proceed on generic transformation messaging alone

### Condition 2: Weak incumbent, high change appetite, manageable transition
**When:** Incumbent performance is weak (1–2), buyer change appetite is high (4–5), and
transition risk is manageable (switching complexity 1–3).
**Recommendation:** `go`
**Rationale:** Credible displacement potential if the challenger can evidence better outcomes,
transition confidence, and a positive future-state proposition.
**Required actions:**
- Build displacement narrative around evolution, outcomes, and confidence
- Provide proof from comparable transitions
- Translate incumbent weaknesses into positive solution themes
- Ensure commercial model supports transition commitments

### Condition 3: Weak incumbent but high transition risk
**When:** Incumbent performance is weak (1–2), but TUPE, systems dependency, data migration,
or mobilisation risk is high (switching complexity 4–5).
**Recommendation:** `go_with_conditions`
**Rationale:** The buyer may want change but fear disruption. The bid is only attractive if
the challenger can make transition feel lower risk than staying.
**Required actions:**
- Build detailed mobilisation and service continuity plan
- Model TUPE cost and workforce risk
- Provide named transition governance and hypercare approach
- Use evidence of similar service transfers
- Escalate to delivery, legal, HR, and commercial leads before final go decision

### Condition 4: Anecdotal vulnerability evidence
**When:** Incumbent vulnerabilities are based mainly on Tier 6 (internal intelligence) or
Tier 7 (inference) evidence.
**Recommendation:** `conditional_go_pending_validation` or `intelligence_gap`
**Rationale:** Anecdotal intelligence can shape hypotheses but must not drive overconfident
bid decisions or direct proposal claims.
**Required actions:**
- Validate through procurement documents, public reports, clarification questions, or further buyer engagement
- Label all such points as `unverified_intelligence`
- Convert into neutral future-state themes rather than negative claims

### Condition 5: Bidder is the incumbent with known issues
**When:** The bidder is the current incumbent and has known service issues.
**Recommendation:** `defensive_recompete`
**Rationale:** The strategy must avoid complacency and must show learning, correction,
investment, and a credible next-phase improvement roadmap.
**Required actions:**
- Acknowledge lessons learned professionally where appropriate
- Evidence corrective actions and performance recovery
- Emphasise continuity plus improvement
- Show future roadmap, innovation, governance upgrades, and measurable value
- Avoid relying only on relationship history or operational familiarity

### Condition 6: Unknown incumbent
**When:** The incumbent identity is unknown or the current delivery model is unclear.
**Recommendation:** `intelligence_gap`
**Rationale:** A reliable go/no-go conclusion is not possible without identifying the current
provider or current operating model.
**Required actions:**
- Produce a framework assessment with provisional scenarios
- Identify priority information gaps
- Generate questions for sales, capture, buyer engagement, or public source research
- Do not overstate incumbent vulnerability

### Condition 7: Procurement as price test
**When:** The buyer appears to be using procurement mainly to create price tension with the
incumbent (strong incumbent performance, repeated extensions, similar scope, high price
weighting, limited transformation language).
**Recommendation:** `no_go` or `price_disciplined_selective_go`
**Rationale:** The challenger risks funding a procurement that ultimately helps the buyer
negotiate with the incumbent.
**Required actions:**
- Test whether the buyer has credible dissatisfaction or transformation intent
- Assess whether price weighting is high enough to justify participation
- Avoid high-cost bid investment unless a differentiated route to win exists
- Consider selective pursuit or partnering strategy

### Condition 8: Multi-lot with varying incumbent strength
**When:** Procurement is multi-lot and incumbent strength varies by lot.
**Recommendation:** `selective_go`
**Rationale:** Some lots may be winnable while others are structurally incumbent-favoured.
**Required actions:**
- Score each lot separately using the full scoring model
- Identify contestable service towers
- Align bid investment to winnable lots
- Do not apply blanket pursuit logic across all lots

---

## 4. Judgement Heuristics

These are pattern-recognition rules drawn from practitioner experience. Apply them when the
data is ambiguous or when a specific signal appears. They explain *why* a pattern matters,
which helps the LLM reason about edge cases rather than following rules mechanically.

1. **Repeated contract extensions.** If the buyer has repeatedly extended the incumbent contract, assess whether this signals satisfaction, lack of alternatives, transition anxiety, procurement delay, or market weakness. Extensions driven by buyer procurement capacity constraints (common in central government) mean something very different from extensions driven by buyer satisfaction.

2. **Highly prescriptive specification.** If the specification is highly detailed and operationally prescriptive, test whether it has been shaped around the incumbent's current service model. This is common when buyer teams have worked closely with the incumbent for years and unconsciously describe what they have rather than what they need.

3. **Innovation language vs. price weighting.** If the buyer emphasises innovation but evaluation heavily weights price, test whether the opportunity is primarily a cost-reduction exercise. Innovation-light, price-heavy procurements are often market tests or contract renegotiation tools.

4. **Persistent poor performance.** If the incumbent has poor performance but remains in place, assume the buyer may fear switching risk more than service failure. This is especially common in politically sensitive services where a transition failure would generate public scrutiny.

5. **Limited public evidence.** If there is limited public evidence of incumbent weakness, focus challenger strategy on future requirements rather than alleged failure. The absence of evidence is not evidence of strong performance, but it limits the credibility of a displacement narrative built on incumbent criticism.

6. **Strong local teams.** If the incumbent has strong local teams embedded in the buyer's operations, protect continuity in the narrative and avoid implying unnecessary disruption to people who evaluators may know personally.

7. **Material TUPE.** If TUPE is material, the commercial model must reflect workforce risk, not just delivery ambition. Savings promises that are incompatible with TUPE cost absorption will be spotted by experienced evaluators.

8. **Politically exposed service.** If the service is politically exposed (ministerial interest, media scrutiny, election sensitivity), the transition narrative must emphasise resilience, assurance, continuity, and no service degradation. Bold transformation messaging is high-risk in this context.

9. **New buyer leadership.** If the buyer has recently changed leadership (new SRO, new director, new minister, machinery of government change), reassess change appetite. New leadership may create a displacement window — or may increase risk aversion during a settling-in period.

10. **Cross-contract incumbent.** If the incumbent is also a strategic supplier to the buyer across other contracts, assess cross-contract relationship advantage. The buyer may be reluctant to displace on one contract if it risks the broader supplier relationship.

11. **Incumbent as subcontractor.** If the incumbent is a subcontractor in another bidder's ecosystem, assess whether partnering, neutralising, or competing is the best approach. The incumbent may be less committed to retaining if the prime relationship has deteriorated.

12. **Audit criticism of service, not supplier.** If public audit findings criticise the service but not the supplier directly, avoid attributing failure solely to the incumbent. Service failures often reflect buyer constraints, underfunding, policy, legacy technology, or scope design rather than supplier performance.

13. **Old but stable technology.** If the incumbent's solution is old but stable, the challenger must avoid looking like an unnecessary technology risk. Position modernisation as a managed evolution, not a forced migration.

14. **Low buyer delivery maturity.** If the buyer has low delivery maturity (weak contract management, limited technical capability, poor governance), a radical transformation message may increase perceived risk. Position capability uplift for the buyer as well as the service.

15. **Expensive but trusted incumbent.** If the incumbent is expensive but trusted, a challenger should position value and control — not simply lower cost. A pure price play against a trusted incumbent rarely wins unless the procurement is explicitly price-driven.

16. **Framework call-off dynamics.** If the procurement is a call-off from a framework, assess whether framework membership limits the competitive field, whether the incumbent has a preferred position on the framework, and whether framework expiry or refresh creates a timing opportunity.

17. **SME challenger against large incumbent.** If the challenger is an SME competing against a large prime, assess whether the buyer values agility and specialism (SME advantage) or requires scale, financial resilience, and multi-site capability (large prime advantage). Balance sheet requirements and past contract value thresholds in PQQ/SQ stages may structurally exclude SMEs regardless of capability.

18. **Incumbent financial distress.** If there are signals of incumbent financial distress (profit warnings, workforce reductions, parent company instability, credit downgrades), assess whether the buyer is aware and whether this creates an active displacement window. Buyers may accelerate re-procurement or add service continuity clauses — both create opportunity for a financially stable challenger.

19. **Spending review and budget cycle timing.** If the procurement falls during or immediately after a spending review, assess whether budget constraints are driving cost-reduction procurement rather than transformation. Post-spending-review procurements in central government often prioritise efficiency savings over service improvement.
