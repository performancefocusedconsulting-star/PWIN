# Claims Block Schema — v1.0

This document is the canonical contract every BidEquity intelligence dossier
must satisfy when it emits a `claims[]` block.

The block exists so that downstream agents — Win Strategy synthesis, the
Forensic Intelligence Auditor, future Qualify integrations — can reason over
the dossier's *claims* as first-class structured objects rather than parsing
prose. The narrative remains human-readable; the claims block makes the same
information machine-readable and audit-trailable.

## Where the block lives

A top-level `claims` array on the dossier JSON, alongside `meta`,
`sourceRegister`, and the section objects:

```json
{
  "meta": { ... },
  "claims": [ ... ],
  "sourceRegister": { ... },
  "buyerSnapshot": { ... },
  ...
}
```

## Required fields per claim

Every entry in `claims[]` is an object with **six required fields**:

| Field | Type | Meaning |
|---|---|---|
| `claim_id` | string | Stable, unique identifier for the claim. Format: `CLM-` followed by zero-padded sequence (e.g. `CLM-001`). For integrators, prefix with the originating context (e.g. `INC-CLM-001`). |
| `claim_text` | string | The assertion in plain prose, self-contained and readable on its own. |
| `claim_date` | string (`YYYY-MM-DD`) | When the producing skill asserted this claim — typically the dossier build/refresh date for that claim's section. |
| `source` | string | Where the claim comes from. One of: a URL; a structured `sourceRegister` reference (e.g. `SRC-001`); an upstream dossier reference for integrators (e.g. `Buyer dossier: HMRC, claim BUY-CLM-007`). |
| `source_date` | string (`YYYY-MM-DD`) or null | When the source itself was published or last updated. Null only when the source genuinely has no publication date (rare; document why in `claim_text` if so). |
| `source_tier` | integer | 1, 2, 3, or 4 — from the platform source tier table (see §9 of the FIA spec). |

## Citation rule

Every material claim in the narrative must appear in `claims[]` with a
stable `claim_id`, and the narrative must cite by `[CLM-id]` inline at the
point of assertion. Example:

> Defence Digital reports into the National Armaments Director group [CLM-014],
> following the 2024 reorganisation [CLM-015].

The auditor and other consumers walk the citation markers to trace claims
back to evidence. **A material claim with no `claim_id` citation is a
contract violation.** "Material" means any claim that bears on a downstream
decision — go/no-go, win theme, stakeholder targeting, route to market.
Background colour ("Defence Digital is a UK government function") does not
need a citation.

## Integrator addendum

Integrator skills (incumbency-advantage-displacement-strategy is the V1
example) may carry an optional **seventh field** on each claim:

| Field | Type | Meaning |
|---|---|---|
| `derivedFrom` | array of strings | Upstream claim IDs this integrator claim was synthesised from. Format: `[upstream_skill_prefix]:[claim_id]` (e.g. `["BUYER:CLM-014", "SUPPLIER:CLM-022"]`). |

The integrator's own `claim_id` remains in its local namespace
(`INC-CLM-001`), and the `derivedFrom` array names the upstream evidence.
This lets the auditor follow the chain back to source-level evidence
through multiple skill boundaries.

## V1.1 forward note

A seventh field — `volatility: low | medium | high` — is reserved for V1.1.
V1.0 dossiers do not emit it; the auditor derives volatility from the
asset profile in V1.0.

## Structural checks (V1.0 validator)

A V1.0 conforming dossier must satisfy all of:

1. Top-level `claims` key exists and is an array (may be empty for legacy
   dossiers in degraded mode, but degraded mode is documented separately —
   see §11.3 of the FIA spec).
2. Every entry in `claims[]` has all six required fields, present and
   non-null (except `source_date`, which may be null).
3. `claim_id` matches `^[A-Z][A-Z-]*[0-9]+$` and is unique within the
   dossier.
4. `claim_date` and `source_date` (if non-null) match `YYYY-MM-DD`.
5. `source_tier` is an integer in `{1, 2, 3, 4}`.
6. Every `[CLM-...]`-shaped citation marker that appears in the narrative
   prose corresponds to an existing `claim_id` in `claims[]`.

The validator implements these six checks. Future versions may add
volatility-tag validation (V1.1) and integrator `derivedFrom` resolution
(V1.x).
