# Source Hierarchy, Confidence Calibration, and Evidence Quality

This reference defines the 4-tier source hierarchy, confidence calibration
thresholds, source freshness rules, and rationale quality standards.

---

## 4-Tier Source Hierarchy

| Tier | Source class | Reliability | Use for |
|------|-------------|-------------|---------|
| 1 | Primary official — buyer annual reports, strategy documents, procurement strategy, organisational charts, board papers, NAO/PAC/regulator reports | high | Organisation context, strategy, leadership, risks |
| 2 | Procurement intelligence — Find a Tender, Contracts Finder, framework data, spending datasets | high | Procurement behaviour, supplier ecosystem, contract patterns |
| 3 | Secondary context — reputable media, think tanks, policy analysis, parliamentary committee evidence, sector briefings | medium | Strategic pressures, risks, culture indicators |
| 4 | Internal — CRM, account plans, capture notes, prior bids, relationship maps | high (when available) | Relationship history, stakeholder intelligence |

Mark clearly which sections rely on external public data versus internal data.
In most runs, no Tier 4 data will be available — flag this as an intelligence
gap, not a failure.

### Contradictory sources

When two sources give different values for the same fact (e.g., leadership
names, budget figures, programme status):

1. Prefer the higher-tier source.
2. If both sources are the same tier, prefer the more recent.
3. Record both sources in the evidence wrapper.
4. Note the discrepancy in the field's `rationale`.

---

## Confidence Calibration

These thresholds ensure consistent confidence ratings across runs and analysts.

| Confidence | Criteria |
|---|---|
| `high` | Corroborated by 2+ Tier 1–2 sources published within 2 years |
| `medium` | Single Tier 1–2 source, OR Tier 3 only, OR older than 2 years but corroborated |
| `low` | Inferred from indirect evidence, single Tier 3 source, or any source older than 3 years |

When assessing confidence, consider both source quality and recency. A single
Tier 1 source from last year is `medium`. Two Tier 1 sources from last year is
`high`. A Tier 3 media report from 4 years ago is `low`.

---

## Source Freshness Rules

- **Flag any source older than 3 years** in `sourceRegister.staleFields`.
- **Treat findings from stale sources** as `confidence: "low"` and note the
  age in the rationale.
- A 2019 document cited in 2026 is not current evidence — it may indicate a
  historical position that has since changed.
- When a stale source is the only evidence for a field, set
  `type: "inference"` (not `fact`) and note the age risk.

---

## Rationale Quality

The `rationale` field in the evidence wrapper must explain the specific
evidence chain, not restate that evidence exists.

### Strong rationale example

> "Inferred from three consecutive call-offs under CCS RM6187 with no
> open-market FTS procedures in 4 years, consistent with the buyer's stated
> 'route-to-market efficiency' commitment in their 2024 commercial strategy
> (SRC-003). The absence of open competition and reliance on a single framework
> suggests framework-first procurement behaviour."

This is strong because it names the specific signals (three call-offs, no open
procedures, a policy statement), connects them logically, and explains the
reasoning step.

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
