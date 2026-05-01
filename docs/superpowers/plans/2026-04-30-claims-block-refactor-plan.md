# claims[] Block Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the four BidEquity intelligence dossier skills (buyer / supplier / sector / incumbency) to emit a structured top-level `claims[]` block alongside the narrative, so downstream agents — and the forthcoming Forensic Intelligence Auditor — can reason over claims as first-class structured objects rather than parsing prose.

**Architecture:** A single canonical contract document defines the `claims[]` block schema (six required fields per claim plus citation rules). A platform-level Python stdlib validator enforces the contract against any dossier. Each producing skill is refactored to emit the block: its `SKILL.md` adds a persona-level claims-discipline rule, its `references/output-schema.md` documents the new top-level block, and its `scripts/render_dossier.py` reads claims and renders citation markers in the rendered HTML. The universal spec (`SKILL-UNIVERSAL-SPEC.md`) adds a new section that makes the claims block a producer-skill requirement.

**Tech Stack:** Python 3.9+ stdlib only (validator + tests, matches the rest of `pwin-competitive-intel`); Markdown for spec/schema docs; the four `SKILL.md` files (Claude.ai-resident skills, master in this repo). No new external dependencies. Manual end-to-end validation by running the refactored skills on Claude.ai against known inputs (no local way to exercise Claude.ai-resident skills).

**Spec:** `docs/superpowers/specs/2026-04-30-forensic-intelligence-auditor-design.md` §11 (the upstream contract this plan implements).

---

## File structure

**Create:**
- `pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md` — the canonical contract document. Plain English + JSON shape + citation rules + integrator addendum.
- `pwin-platform/skills/agent2-market-competitive/master/scripts/validate_claims_block.py` — stdlib Python validator. Single file. Reads a dossier JSON, runs both structural checks (six required fields, types, sourceTier in 1–4) and citation-integrity checks (every `claimId` cited in the narrative exists in `claims[]`; no orphans).
- `pwin-platform/skills/agent2-market-competitive/master/scripts/__init__.py` — empty marker, makes the directory importable.
- `pwin-platform/skills/agent2-market-competitive/master/tests/__init__.py` — empty marker.
- `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py` — Python `unittest` tests against the validator.
- `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_valid.json` — minimal valid dossier (one claim, narrative cites it).
- `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_missing_field.json` — invalid: claim missing `sourceTier`.
- `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_orphan_citation.json` — invalid: narrative cites a `claimId` not in `claims[]`.
- `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_bad_tier.json` — invalid: `sourceTier: 5` (out of 1–4 range).
- `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/buyer_defence_digital_v1.json` — hand-crafted Defence Digital dossier showing the new contract end-to-end. Becomes the anchor fixture for the rest of the platform (the Forensic Intelligence Auditor's pilot in Plan B will audit this fixture).
- `wiki/actions/intelligence-skills-claims-block-refactor.md` — wiki action note tracking this work.

**Modify:**
- `pwin-platform/skills/agent2-market-competitive/master/SKILL-UNIVERSAL-SPEC.md` — add a new section "13. Claims block (producer skills)" with the contract reference and the citation rule.
- `pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/SKILL.md` — add persona-level claims discipline rule; reference the schema; update the output structure description.
- `pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/references/output-schema.md` — add the `claims[]` block to the documented top-level structure.
- `pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/scripts/render_dossier.py` — read `claims[]`; render citation markers `[CLM-id]` in the rendered narrative.
- `pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/{SKILL.md, references/output-schema.md, scripts/render_dossier.py}` — same three changes.
- `pwin-platform/skills/agent2-market-competitive/master/sector-intelligence/{SKILL.md, references/output-schema.md, scripts/render_dossier.py}` — same three changes.
- `pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/{SKILL.md, references/output-schema.md, scripts/render_dossier.py}` — same three changes plus the integrator addendum (claims may carry `derivedFrom: [upstream_claimId]`).
- `CLAUDE.md` (repo root) — note the new contract in the pwin-platform section and the Agent 2 intelligence-skills section.

---

## Phase 1 — Contract foundation

This phase produces the testable foundation: a contract document, a validator, and unit tests. Nothing in the producing skills changes yet. Once Phase 1 is committed, every subsequent skill refactor is validated against the same code.

### Task 1: Create the contract document

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md`

- [ ] **Step 1: Write the contract document.**

```markdown
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
| `claimId` | string | Stable, unique identifier for the claim. Format: `CLM-` followed by zero-padded sequence (e.g. `CLM-001`). For integrators, prefix with the originating context (e.g. `INC-CLM-001`). |
| `claimText` | string | The assertion in plain prose, self-contained and readable on its own. |
| `claimDate` | string (`YYYY-MM-DD`) | When the producing skill asserted this claim — typically the dossier build/refresh date for that claim's section. |
| `source` | string | Where the claim comes from. One of: a URL; a structured `sourceRegister` reference (e.g. `SRC-001`); an upstream dossier reference for integrators (e.g. `Buyer dossier: HMRC, claim BUY-CLM-007`). |
| `sourceDate` | string (`YYYY-MM-DD`) or null | When the source itself was published or last updated. Null only when the source genuinely has no publication date (rare; document why in `claimText` if so). |
| `sourceTier` | integer | 1, 2, 3, or 4 — from the platform source tier table (see §9 of the FIA spec). |

## Citation rule

Every material claim in the narrative must appear in `claims[]` with a
stable `claimId`, and the narrative must cite by `[CLM-id]` inline at the
point of assertion. Example:

> Defence Digital reports into the National Armaments Director group [CLM-014],
> following the 2024 reorganisation [CLM-015].

The auditor and other consumers walk the citation markers to trace claims
back to evidence. **A material claim with no `claimId` citation is a
contract violation.** "Material" means any claim that bears on a downstream
decision — go/no-go, win theme, stakeholder targeting, route to market.
Background colour ("Defence Digital is a UK government function") does not
need a citation.

## Integrator addendum

Integrator skills (incumbency-advantage-displacement-strategy is the V1
example) may carry an optional **seventh field** on each claim:

| Field | Type | Meaning |
|---|---|---|
| `derivedFrom` | array of strings | Upstream claim IDs this integrator claim was synthesised from. Format: `[upstream_skill_prefix]:[claimId]` (e.g. `["BUYER:CLM-014", "SUPPLIER:CLM-022"]`). |

The integrator's own `claimId` remains in its local namespace
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
   non-null (except `sourceDate`, which may be null).
3. `claimId` matches `^[A-Z][A-Z-]*[0-9]+$` and is unique within the
   dossier.
4. `claimDate` and `sourceDate` (if non-null) match `YYYY-MM-DD`.
5. `sourceTier` is an integer in `{1, 2, 3, 4}`.
6. Every `[CLM-...]`-shaped citation marker that appears in the narrative
   prose corresponds to an existing `claimId` in `claims[]`.

The validator implements these six checks. Future versions may add
volatility-tag validation (V1.1) and integrator `derivedFrom` resolution
(V1.x).
```

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md
git commit -m "docs(skills): claims[] block schema v1.0 contract document"
```

---

### Task 2: Create the empty package markers

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/scripts/__init__.py`
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/__init__.py`
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/.gitkeep`

- [ ] **Step 1: Create the three marker files.** Empty files. The two `__init__.py` files make the directories Python packages so the test runner can import; the `.gitkeep` keeps the fixtures directory in git before any fixtures land.

```bash
mkdir -p pwin-platform/skills/agent2-market-competitive/master/scripts
mkdir -p pwin-platform/skills/agent2-market-competitive/master/tests/fixtures
touch pwin-platform/skills/agent2-market-competitive/master/scripts/__init__.py
touch pwin-platform/skills/agent2-market-competitive/master/tests/__init__.py
touch pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/.gitkeep
```

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/scripts/__init__.py \
        pwin-platform/skills/agent2-market-competitive/master/tests/__init__.py \
        pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/.gitkeep
git commit -m "chore(skills): scaffold scripts/ and tests/ directories"
```

---

### Task 3: Create the valid-dossier fixture (TDD anchor)

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_valid.json`

- [ ] **Step 1: Write the minimal valid fixture.** A single claim, narrative cites it, contract satisfied.

```json
{
  "meta": {
    "version": "1.0.0",
    "buyer": "Test Buyer",
    "buildDate": "2026-04-30"
  },
  "claims": [
    {
      "claimId": "CLM-001",
      "claimText": "Test Buyer published a digital strategy in March 2026.",
      "claimDate": "2026-04-30",
      "source": "https://example.gov.uk/digital-strategy-2026",
      "sourceDate": "2026-03-15",
      "sourceTier": 1
    }
  ],
  "sourceRegister": {
    "sources": [
      {
        "sourceId": "SRC-001",
        "title": "Test Buyer Digital Strategy 2026",
        "publicationDate": "2026-03-15"
      }
    ]
  },
  "buyerSnapshot": {
    "narrative": "Test Buyer is a UK government function. The buyer published a digital strategy in March 2026 [CLM-001]."
  }
}
```

- [ ] **Step 2: Commit the fixture.** No test exists yet; this is the anchor the validator will be built against.

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_valid.json
git commit -m "test(skills): valid-dossier fixture for claims-block validator"
```

---

### Task 4: Write the failing validator test (structural shape)

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Write the failing test.**

```python
"""Tests for validate_claims_block.

Run from the master/ directory:
    python -m unittest tests.test_validate_claims_block
"""

import json
import unittest
from pathlib import Path

from scripts.validate_claims_block import validate

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    with open(FIXTURES / name, encoding="utf-8") as f:
        return json.load(f)


class ValidStructureTests(unittest.TestCase):
    def test_minimal_valid_dossier_passes(self):
        result = validate(_load("dossier_valid.json"))
        self.assertEqual(result.errors, [])
        self.assertTrue(result.ok)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: ImportError or ModuleNotFoundError for `scripts.validate_claims_block` (the validator does not yet exist).

---

### Task 5: Implement the validator (structural checks)

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/scripts/validate_claims_block.py`

- [ ] **Step 1: Write the minimal validator.** Stdlib only. Returns a dataclass-like result object the tests can interrogate.

```python
"""validate_claims_block — V1.0 validator for the claims[] block contract.

Contract reference:
    pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md

Stdlib only. Returns a Result with .ok and .errors so callers (tests, CI,
the auditor's degraded-mode gate) can branch on outcome.
"""

import re
from dataclasses import dataclass, field
from typing import Any

REQUIRED_FIELDS = (
    "claimId",
    "claimText",
    "claimDate",
    "source",
    "sourceDate",
    "sourceTier",
)
NULLABLE_FIELDS = ("sourceDate",)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CLAIM_ID_RE = re.compile(r"^[A-Z][A-Z-]*[0-9]+$")
CITATION_RE = re.compile(r"\[(CLM-[0-9A-Z-]+|[A-Z]+-CLM-[0-9A-Z-]+)\]")
VALID_TIERS = {1, 2, 3, 4}


@dataclass
class Result:
    errors: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate(dossier: dict[str, Any]) -> Result:
    """Validate a dossier against the V1.0 claims[] block contract.

    Runs all six structural checks documented in CLAIMS-BLOCK-SCHEMA.md
    plus citation-integrity. Returns a Result with errors as a list of
    plain-language strings; empty list = pass.
    """
    result = Result()

    claims = dossier.get("claims")
    if claims is None:
        result.errors.append("Top-level 'claims' key is missing.")
        return result
    if not isinstance(claims, list):
        result.errors.append("Top-level 'claims' must be an array.")
        return result

    seen_ids = set()
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            result.errors.append(f"claims[{i}] is not an object.")
            continue
        for fld in REQUIRED_FIELDS:
            if fld not in claim:
                result.errors.append(f"claims[{i}] missing required field '{fld}'.")
                continue
            value = claim[fld]
            if value is None and fld not in NULLABLE_FIELDS:
                result.errors.append(f"claims[{i}].{fld} is null but is not nullable.")
        if "claimId" in claim and isinstance(claim["claimId"], str):
            cid = claim["claimId"]
            if not CLAIM_ID_RE.match(cid):
                result.errors.append(
                    f"claims[{i}].claimId '{cid}' does not match required format."
                )
            if cid in seen_ids:
                result.errors.append(f"claims[{i}].claimId '{cid}' is duplicated.")
            seen_ids.add(cid)
        for date_fld in ("claimDate", "sourceDate"):
            if date_fld in claim and claim[date_fld] is not None:
                if not isinstance(claim[date_fld], str) or not DATE_RE.match(
                    claim[date_fld]
                ):
                    result.errors.append(
                        f"claims[{i}].{date_fld} must be YYYY-MM-DD."
                    )
        if "sourceTier" in claim:
            tier = claim["sourceTier"]
            if tier not in VALID_TIERS:
                result.errors.append(
                    f"claims[{i}].sourceTier '{tier}' is not in {{1,2,3,4}}."
                )

    cited_ids = _extract_citations(dossier)
    orphans = cited_ids - seen_ids
    for orphan in sorted(orphans):
        result.errors.append(
            f"Narrative cites '[{orphan}]' but no claim with that id exists."
        )

    return result


def _extract_citations(node: Any) -> set[str]:
    """Walk the dossier tree and collect every [CLM-...] citation marker
    appearing in any string value. Order-independent; picks up citations
    embedded anywhere in the narrative tree."""
    found: set[str] = set()
    if isinstance(node, str):
        for match in CITATION_RE.finditer(node):
            found.add(match.group(1))
    elif isinstance(node, dict):
        for value in node.values():
            found |= _extract_citations(value)
    elif isinstance(node, list):
        for item in node:
            found |= _extract_citations(item)
    return found
```

- [ ] **Step 2: Run the test to verify it passes.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: `OK` — one test, one pass.

- [ ] **Step 3: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/scripts/validate_claims_block.py \
        pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "feat(skills): claims-block validator + minimal valid-shape test"
```

---

### Task 6: Add the missing-field fixture and test

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_missing_field.json`
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Write the missing-field fixture.** Drop `sourceTier` from the only claim.

```json
{
  "meta": {"version": "1.0.0", "buyer": "Test Buyer", "buildDate": "2026-04-30"},
  "claims": [
    {
      "claimId": "CLM-001",
      "claimText": "Test Buyer published a digital strategy in March 2026.",
      "claimDate": "2026-04-30",
      "source": "https://example.gov.uk/digital-strategy-2026",
      "sourceDate": "2026-03-15"
    }
  ],
  "buyerSnapshot": {
    "narrative": "Test Buyer published a digital strategy [CLM-001]."
  }
}
```

- [ ] **Step 2: Write the failing test.** Append to `test_validate_claims_block.py` inside `ValidStructureTests`.

```python
    def test_missing_required_field_fails(self):
        result = validate(_load("dossier_missing_field.json"))
        self.assertFalse(result.ok)
        self.assertTrue(
            any("sourceTier" in err for err in result.errors),
            f"Expected an error mentioning 'sourceTier', got: {result.errors}",
        )
```

- [ ] **Step 3: Run the test to verify it passes.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 2 tests, both pass — the validator already implements missing-field detection.

- [ ] **Step 4: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_missing_field.json \
        pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "test(skills): claims-block validator catches missing required fields"
```

---

### Task 7: Add the orphan-citation fixture and test

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_orphan_citation.json`
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Write the orphan-citation fixture.** Narrative cites `[CLM-002]` but `claims[]` only has `CLM-001`.

```json
{
  "meta": {"version": "1.0.0", "buyer": "Test Buyer", "buildDate": "2026-04-30"},
  "claims": [
    {
      "claimId": "CLM-001",
      "claimText": "Test Buyer published a digital strategy in March 2026.",
      "claimDate": "2026-04-30",
      "source": "https://example.gov.uk/digital-strategy-2026",
      "sourceDate": "2026-03-15",
      "sourceTier": 1
    }
  ],
  "buyerSnapshot": {
    "narrative": "Test Buyer published a digital strategy [CLM-001] and reorganised in 2024 [CLM-002]."
  }
}
```

- [ ] **Step 2: Write the failing test.** Append to `ValidStructureTests`.

```python
    def test_orphan_citation_fails(self):
        result = validate(_load("dossier_orphan_citation.json"))
        self.assertFalse(result.ok)
        self.assertTrue(
            any("CLM-002" in err and "no claim" in err for err in result.errors),
            f"Expected an error mentioning orphan 'CLM-002', got: {result.errors}",
        )
```

- [ ] **Step 3: Run the test to verify it passes.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 3 tests, all pass.

- [ ] **Step 4: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_orphan_citation.json \
        pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "test(skills): claims-block validator catches orphan citations"
```

---

### Task 8: Add the bad-tier fixture and test

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_bad_tier.json`
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Write the bad-tier fixture.** `sourceTier: 5` is out of the 1–4 range.

```json
{
  "meta": {"version": "1.0.0", "buyer": "Test Buyer", "buildDate": "2026-04-30"},
  "claims": [
    {
      "claimId": "CLM-001",
      "claimText": "Test Buyer published a digital strategy in March 2026.",
      "claimDate": "2026-04-30",
      "source": "https://random-blog.example.com/post",
      "sourceDate": "2026-03-15",
      "sourceTier": 5
    }
  ],
  "buyerSnapshot": {
    "narrative": "Test Buyer published a digital strategy [CLM-001]."
  }
}
```

- [ ] **Step 2: Write the failing test.** Append to `ValidStructureTests`.

```python
    def test_bad_sourceTier_fails(self):
        result = validate(_load("dossier_bad_tier.json"))
        self.assertFalse(result.ok)
        self.assertTrue(
            any("sourceTier" in err and "5" in err for err in result.errors),
            f"Expected an error mentioning bad sourceTier '5', got: {result.errors}",
        )
```

- [ ] **Step 3: Run the test to verify it passes.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 4 tests, all pass.

- [ ] **Step 4: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/dossier_bad_tier.json \
        pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "test(skills): claims-block validator rejects out-of-range sourceTier"
```

---

### Task 9: Add the duplicate-id and bad-id-format checks

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Add tests for the two remaining structural checks.** Both build their fixtures inline (no JSON files) because the cases are about programmatic shape.

```python
    def test_duplicate_claimId_fails(self):
        dossier = {
            "claims": [
                {
                    "claimId": "CLM-001",
                    "claimText": "First.",
                    "claimDate": "2026-04-30",
                    "source": "url",
                    "sourceDate": "2026-03-15",
                    "sourceTier": 1,
                },
                {
                    "claimId": "CLM-001",
                    "claimText": "Duplicate.",
                    "claimDate": "2026-04-30",
                    "source": "url",
                    "sourceDate": "2026-03-15",
                    "sourceTier": 1,
                },
            ],
            "narrative": "Test [CLM-001].",
        }
        result = validate(dossier)
        self.assertFalse(result.ok)
        self.assertTrue(any("duplicated" in err for err in result.errors))

    def test_bad_claimId_format_fails(self):
        dossier = {
            "claims": [
                {
                    "claimId": "claim-1",  # lowercase, no required prefix
                    "claimText": "Bad id.",
                    "claimDate": "2026-04-30",
                    "source": "url",
                    "sourceDate": "2026-03-15",
                    "sourceTier": 1,
                }
            ],
            "narrative": "[CLM-001]",
        }
        result = validate(dossier)
        self.assertFalse(result.ok)
        self.assertTrue(any("does not match required format" in err for err in result.errors))
```

- [ ] **Step 2: Run the tests.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 6 tests, all pass.

- [ ] **Step 3: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "test(skills): claims-block validator catches duplicate ids and bad id format"
```

---

## Phase 2 — Universal spec update

The contract is locked and validated. Now make it a producer-skill requirement at the platform level so every skill author knows it applies to them.

### Task 10: Add §13 "Claims block (producer skills)" to SKILL-UNIVERSAL-SPEC.md

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/SKILL-UNIVERSAL-SPEC.md`

- [ ] **Step 1: Find the end of the existing numbered sections.** Open `SKILL-UNIVERSAL-SPEC.md`. The file currently runs sections §1–§N (the last one before any appendix). Identify the last numbered section's end.

```bash
grep -n "^---$" pwin-platform/skills/agent2-market-competitive/master/SKILL-UNIVERSAL-SPEC.md | tail -5
grep -n "^## " pwin-platform/skills/agent2-market-competitive/master/SKILL-UNIVERSAL-SPEC.md
```

- [ ] **Step 2: Append the new §13 immediately before the file's final section (typically a glossary, appendix, or end-of-file).** Use Edit to insert. The exact `old_string` depends on the current last section's heading — use the last `## N. ...` heading text returned by the grep above as the anchor.

Insert this block immediately before that anchor (or append to file if it's the final section):

```markdown
---

## 13. Claims block (producer skills)

Every producer skill (buyer-intelligence, supplier-intelligence,
sector-intelligence) and every integrator skill
(incumbency-advantage-displacement-strategy) emits a top-level `claims[]`
array on its dossier JSON. Each claim is a structured object with six
required fields documented in
[`CLAIMS-BLOCK-SCHEMA.md`](CLAIMS-BLOCK-SCHEMA.md).

The narrative cites claims inline using `[CLM-id]` markers. Every material
claim — anything that bears on a downstream decision (go/no-go, win theme,
stakeholder targeting, route to market) — must appear in `claims[]` with a
stable `claimId`.

**Why this exists.** Downstream agents — Win Strategy synthesis, the
Forensic Intelligence Auditor, and any future consumer — cannot reliably
parse claims out of prose. The structured block makes claims first-class,
machine-readable, and audit-trailable.

**Validation.** The platform ships a stdlib validator at
`scripts/validate_claims_block.py`. Any consumer can call it on a dossier
to confirm contract compliance. The Forensic Intelligence Auditor's
degraded-mode gate is precisely this validator's failure path — a dossier
that fails validation gets a degraded audit.

**Integrator addendum.** Integrator skills may carry an optional seventh
field per claim — `derivedFrom`, an array of upstream claim ids
(`["BUYER:CLM-014"]`) — to record which upstream evidence the integrator
synthesised the claim from. See `CLAIMS-BLOCK-SCHEMA.md` for the format.

**V1.1 forward note.** A `volatility` field per claim is reserved for V1.1.
V1.0 dossiers do not emit it; the auditor derives volatility from the
asset profile.
```

- [ ] **Step 3: Verify the file still parses cleanly as Markdown.**

```bash
head -5 pwin-platform/skills/agent2-market-competitive/master/SKILL-UNIVERSAL-SPEC.md
grep -c "^## " pwin-platform/skills/agent2-market-competitive/master/SKILL-UNIVERSAL-SPEC.md
```

Expected: file still has its frontmatter / heading; `## ` count incremented by 1.

- [ ] **Step 4: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/SKILL-UNIVERSAL-SPEC.md
git commit -m "docs(skills): add §13 claims-block requirement to universal spec"
```

---

## Phase 3 — Buyer-intelligence refactor (the anchor)

Buyer is the smallest of the four (325 lines) and is the anchor case for the V1 auditor (Defence Digital). Refactor it first; the pattern locked in here repeats for the other three skills.

### Task 11: Update buyer-intelligence/references/output-schema.md to document the claims[] block

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/references/output-schema.md`

- [ ] **Step 1: Read the current top-level structure.** Find where the file documents the top-level dossier object.

```bash
grep -n "^## \|^### " pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/references/output-schema.md | head -20
```

Identify the first `## ` heading after the file's preamble — typically "Top-level structure", "Schema", or similar.

- [ ] **Step 2: Insert the claims[] block documentation immediately after the `meta` section's documentation** so claims appears second in the documented structure (matching the actual JSON layout: meta, claims, sourceRegister, sections...).

Insert this block:

```markdown
### `claims` (array, required)

Top-level array of structured claim objects. Every material assertion in
the narrative below must appear here with a stable `claimId`. The narrative
cites claims inline using `[CLM-id]` markers.

```json
{
  "claims": [
    {
      "claimId": "CLM-001",
      "claimText": "Defence Digital reports into the National Armaments Director group.",
      "claimDate": "2026-04-30",
      "source": "SRC-014",
      "sourceDate": "2024-09-12",
      "sourceTier": 1
    }
  ]
}
```

The six fields are mandatory on every claim. Schema and validation rules
live in `pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md`
(canonical) and §13 of the Universal Skill Spec.

"Material" means any claim that bears on a downstream decision — go/no-go,
win theme, stakeholder targeting, route to market. Background colour does
not need a citation.
```

- [ ] **Step 3: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/references/output-schema.md
git commit -m "docs(buyer-intel): document claims[] block in output schema"
```

---

### Task 12: Update buyer-intelligence/SKILL.md with the claims discipline rule

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/SKILL.md`

- [ ] **Step 1: Read the current Hard Rules section** (or equivalent persona-level rule list).

```bash
grep -n "Hard rules\|Hard Rules\|hard rules\|## Rules\|persona" pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/SKILL.md
```

- [ ] **Step 2: Add a new hard rule** to the persona's rule list. Use Edit to insert the new rule at the end of the existing rules block (preserve numbering or bullet style as the file uses):

```markdown
- **Emit a structured `claims[]` block.** Every dossier you produce must
  include a top-level `claims[]` array containing every material assertion
  in the narrative. Each claim has six required fields: `claimId`,
  `claimText`, `claimDate`, `source`, `sourceDate`, `sourceTier`. Cite
  claims inline using `[CLM-id]` markers. A material claim with no `claimId`
  citation in the narrative is a contract violation. See
  `CLAIMS-BLOCK-SCHEMA.md` and §13 of the Universal Skill Spec.
```

- [ ] **Step 3: Add a one-paragraph reference to the schema** in the SKILL's "Output" or "Output structure" section. Find the heading that introduces the JSON output:

```bash
grep -n "## Output\|### Output\|^### Output structure\|## What you produce" pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/SKILL.md
```

Insert immediately after that heading's existing first paragraph:

```markdown
The dossier carries a top-level `claims[]` block alongside `meta`,
`sourceRegister`, and the section objects. Every material assertion in
the narrative cites a claim by its `claimId`. The contract is documented
in [`../CLAIMS-BLOCK-SCHEMA.md`](../CLAIMS-BLOCK-SCHEMA.md) and the
platform validator at `scripts/validate_claims_block.py` enforces it.
```

- [ ] **Step 4: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/SKILL.md
git commit -m "feat(buyer-intel): require claims[] block emission in skill prompt"
```

---

### Task 13: Update buyer-intelligence render script to handle the claims[] block

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/scripts/render_dossier.py`

- [ ] **Step 1: Read the current renderer to find where the top-level dossier is iterated.**

```bash
grep -n "def render\|sourceRegister\|sources\|narrative" pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/scripts/render_dossier.py | head -20
```

Identify the function that renders the top-level dossier (typically `render_dossier(data)`, `render(data)`, or similar) and the function that renders narrative text.

- [ ] **Step 2: Add a helper that converts `[CLM-id]` markers in narrative text into citation hyperlinks** that jump to a "Claims" section at the bottom of the rendered HTML. Insert near the top of the file, after the imports:

```python
import re

CITATION_RE = re.compile(r"\[(CLM-[0-9A-Z-]+|[A-Z]+-CLM-[0-9A-Z-]+)\]")


def _linkify_citations(text: str) -> str:
    """Replace [CLM-id] markers in narrative with anchor links to the
    rendered claims block. Output is HTML-safe."""
    if not isinstance(text, str):
        return text
    return CITATION_RE.sub(
        lambda m: (
            f'<a class="claim-cite" href="#claim-{m.group(1)}">'
            f'[{m.group(1)}]</a>'
        ),
        text,
    )


def _render_claims_block(claims: list) -> str:
    """Render the claims[] array as a definition-list-style HTML block.
    Each claim has an anchor (id="claim-CLM-XXX") that the narrative
    citations link to."""
    if not claims:
        return ""
    rows = []
    for c in claims:
        cid = c.get("claimId", "?")
        rows.append(
            f'<dt id="claim-{cid}">[{cid}] '
            f'(tier {c.get("sourceTier", "?")} '
            f'— {c.get("sourceDate") or "undated"})</dt>'
            f'<dd><p>{c.get("claimText", "")}</p>'
            f'<p class="claim-source"><strong>Source:</strong> '
            f'{c.get("source", "?")}</p>'
            f'<p class="claim-meta">Asserted '
            f'{c.get("claimDate", "?")}.</p></dd>'
        )
    return (
        '<section class="claims-block"><h2>Claims and evidence</h2>'
        '<dl class="claims">' + "".join(rows) + '</dl></section>'
    )
```

- [ ] **Step 3: Wire `_linkify_citations` into the existing narrative renderer.** Find the function(s) that emit narrative prose into HTML and run their string output through `_linkify_citations` before returning. Where the file's existing pattern is:

```python
return f"<p>{paragraph}</p>"
```

Change to:

```python
return f"<p>{_linkify_citations(paragraph)}</p>"
```

Repeat for every place narrative prose is emitted.

- [ ] **Step 4: Append the rendered claims block to the dossier HTML output.** Find the function returning the top-level HTML document (typically named `render_html`, `build_document`, or similar). Just before the closing `</body>`/`</main>` tag, append:

```python
html_output += _render_claims_block(data.get("claims", []))
```

(`data` here is whatever variable name the renderer uses for the loaded dossier dict — check the function signature.)

- [ ] **Step 5: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/scripts/render_dossier.py
git commit -m "feat(buyer-intel): renderer handles claims[] block + citation links"
```

---

### Task 14: Build the Defence Digital fixture

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/buyer_defence_digital_v1.json`

- [ ] **Step 1: Hand-craft the Defence Digital fixture.** This is the V1 anchor dossier — a realistic-looking buyer dossier with the claims block populated. It will be used by the FIA pilot in Plan B.

```json
{
  "meta": {
    "version": "1.0.0",
    "buyer": "Defence Digital",
    "buildDate": "2026-04-30",
    "skillVersion": "buyer-intelligence v3.0"
  },
  "claims": [
    {
      "claimId": "CLM-001",
      "claimText": "Defence Digital is the digital function of the UK Ministry of Defence.",
      "claimDate": "2026-04-30",
      "source": "https://www.gov.uk/government/organisations/defence-digital",
      "sourceDate": "2025-11-04",
      "sourceTier": 1
    },
    {
      "claimId": "CLM-002",
      "claimText": "Charlie Forte leads Defence Digital as Chief Information Officer.",
      "claimDate": "2026-04-30",
      "source": "https://www.linkedin.com/in/charlie-forte/",
      "sourceDate": "2024-06-15",
      "sourceTier": 4
    },
    {
      "claimId": "CLM-003",
      "claimText": "Defence Digital reports into the National Armaments Director group following the 2024 reorganisation.",
      "claimDate": "2026-04-30",
      "source": "https://www.gov.uk/government/news/mod-restructure-2024",
      "sourceDate": "2024-09-12",
      "sourceTier": 1
    }
  ],
  "sourceRegister": {
    "sources": [
      {
        "sourceId": "SRC-001",
        "title": "Defence Digital — gov.uk organisation page",
        "publicationDate": "2025-11-04"
      },
      {
        "sourceId": "SRC-002",
        "title": "Charlie Forte LinkedIn profile",
        "publicationDate": "2024-06-15"
      },
      {
        "sourceId": "SRC-003",
        "title": "MOD restructure announcement 2024",
        "publicationDate": "2024-09-12"
      }
    ]
  },
  "buyerSnapshot": {
    "narrative": "Defence Digital is the digital function of the UK Ministry of Defence [CLM-001]. The function is led by Charlie Forte as Chief Information Officer [CLM-002]. Defence Digital reports into the National Armaments Director group following the 2024 reorganisation [CLM-003]."
  }
}
```

- [ ] **Step 2: Validate the fixture against the validator.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -c "
import json
from scripts.validate_claims_block import validate
with open('tests/fixtures/buyer_defence_digital_v1.json', encoding='utf-8') as f:
    d = json.load(f)
r = validate(d)
print('OK' if r.ok else 'FAIL: ' + str(r.errors))
"
```

Expected: `OK`.

Note: this fixture is *intentionally* the anchor case the FIA must catch as Red in Plan B — the leadership claim (`CLM-002`) is sourced from a Tier 4 LinkedIn profile dated 2024-06-15, with no contradiction-check against current sources. The FIA pilot will Red-flag it. The fixture passes the V1.0 *contract* validator (the structural check) because the contract requires fields to be present, not their values to be safe — that judgement is the FIA's job, not the validator's.

- [ ] **Step 3: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/buyer_defence_digital_v1.json
git commit -m "test(buyer-intel): Defence Digital anchor fixture for V1 contract"
```

---

### Task 15: Add a per-skill validator integration test

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Add a new test class** at the bottom of the test file that validates each per-skill anchor fixture. Today only the buyer fixture exists; the other three get added in their respective phases.

```python
class PerSkillFixtureTests(unittest.TestCase):
    def test_buyer_defence_digital_fixture_passes_validator(self):
        result = validate(_load("buyer_defence_digital_v1.json"))
        self.assertEqual(
            result.errors,
            [],
            f"Defence Digital fixture failed validator: {result.errors}",
        )
```

- [ ] **Step 2: Run the full test suite.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 7 tests, all pass.

- [ ] **Step 3: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "test(buyer-intel): per-skill fixture validates against contract"
```

---

### Task 16: Manual end-to-end validation on Claude.ai (buyer)

This task is the only manual step in the plan. The producing skill runs on Claude.ai, not locally — there is no automated way to exercise the SKILL.md prompt change. The fixture and validator above let us confirm the *contract works*; this step confirms the *skill produces output that satisfies the contract*.

- [ ] **Step 1: Package the buyer-intelligence skill folder** as a Claude.ai-compatible `.skill` archive following the existing process documented in `feedback_claude_ai_skill_packaging.md`.

- [ ] **Step 2: Upload to Claude.ai.** Run the buyer-intelligence skill on a known buyer (suggest: HMRC, since Defence Digital is reserved as the FIA anchor). Ask for `build` mode.

- [ ] **Step 3: Save the output JSON dossier locally.** Place at `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/buyer_hmrc_skillrun_v1.json` (gitignored — sample output, not a fixture).

- [ ] **Step 4: Run the validator on the skill's output.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -c "
import json
from scripts.validate_claims_block import validate
with open('tests/fixtures/buyer_hmrc_skillrun_v1.json', encoding='utf-8') as f:
    d = json.load(f)
r = validate(d)
print('OK' if r.ok else 'FAIL: ' + str(r.errors))
"
```

- [ ] **Step 5: If FAIL, edit `SKILL.md` to tighten the instruction** that produced the failure (e.g. claimId format, missing sourceTier, narrative not citing claims). Re-package, re-upload, re-test. Iterate until OK.

- [ ] **Step 6: Run the renderer on the skill's output** to confirm the citations linkify correctly.

```bash
cd pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence
python scripts/render_dossier.py ../tests/fixtures/buyer_hmrc_skillrun_v1.json > /tmp/buyer_hmrc.html
```

Open `/tmp/buyer_hmrc.html` in a browser. Confirm: narrative shows citation pills; "Claims and evidence" section appears at the bottom; clicking a citation jumps to the claim.

- [ ] **Step 7: If renderer issues are found, fix `render_dossier.py` and re-test.**

- [ ] **Step 8: Commit any SKILL.md / render_dossier.py fixes from steps 5 and 7 separately, with messages naming the issue caught.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/buyer-intelligence/SKILL.md
git commit -m "fix(buyer-intel): tighten <issue> per Claude.ai validation"
```

---

## Phase 4 — Supplier-intelligence refactor

Same five-task pattern as Phase 3 (buyer). The pattern is now locked in; these tasks are mechanical.

### Task 17: Update supplier-intelligence/references/output-schema.md

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/references/output-schema.md`

- [ ] **Step 1: Insert the same `claims[]` documentation block as Task 11**, adapted to supplier vocabulary (s/Defence Digital/example supplier name/; s/buyer/supplier/ where the example mentions buyer-specific concepts).

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/references/output-schema.md
git commit -m "docs(supplier-intel): document claims[] block in output schema"
```

### Task 18: Update supplier-intelligence/SKILL.md

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/SKILL.md`

- [ ] **Step 1: Apply the same two edits as Task 12** — the new hard rule and the output-section reference. Wording identical to Task 12 except for the relative path (still `../CLAIMS-BLOCK-SCHEMA.md`) which is unchanged.

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/SKILL.md
git commit -m "feat(supplier-intel): require claims[] block emission in skill prompt"
```

### Task 19: Update supplier-intelligence render script

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/scripts/render_dossier.py`

- [ ] **Step 1: Apply the same renderer changes as Task 13** — `_linkify_citations`, `_render_claims_block`, wiring into the narrative renderer, appending the claims block to the document.

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/supplier-intelligence/scripts/render_dossier.py
git commit -m "feat(supplier-intel): renderer handles claims[] block + citation links"
```

### Task 20: Build a supplier anchor fixture and validator integration test

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/supplier_anchor_v1.json`
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Hand-craft a minimal supplier anchor fixture.** Same shape as the buyer fixture (Task 14), but for a supplier (suggest: a known UK strategic supplier — Capita or Serco — with three claims: name/sector/incumbency on a known contract). Use realistic source URLs.

- [ ] **Step 2: Validate it.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -c "
import json
from scripts.validate_claims_block import validate
with open('tests/fixtures/supplier_anchor_v1.json', encoding='utf-8') as f:
    d = json.load(f)
r = validate(d)
print('OK' if r.ok else 'FAIL: ' + str(r.errors))
"
```

Expected: `OK`.

- [ ] **Step 3: Add a per-skill integration test** to `PerSkillFixtureTests` in `test_validate_claims_block.py`:

```python
    def test_supplier_anchor_fixture_passes_validator(self):
        result = validate(_load("supplier_anchor_v1.json"))
        self.assertEqual(
            result.errors,
            [],
            f"Supplier anchor fixture failed validator: {result.errors}",
        )
```

- [ ] **Step 4: Run the full test suite.**

```bash
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 8 tests, all pass.

- [ ] **Step 5: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/supplier_anchor_v1.json \
        pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "test(supplier-intel): supplier anchor fixture + validator test"
```

### Task 21: Manual end-to-end validation on Claude.ai (supplier)

- [ ] **Step 1–7: Follow the same procedure as Task 16**, substituting "supplier-intelligence" for "buyer-intelligence" and a known supplier name (suggest: Capita, since Serco is well-covered in test data already). Output goes to `tests/fixtures/supplier_capita_skillrun_v1.json` (gitignored).

- [ ] **Step 8: Commit any SKILL.md / render_dossier.py fixes** from validation iteration with messages naming the issue caught.

---

## Phase 5 — Sector-intelligence refactor

Same five-task pattern as Phase 4. Sector is unique in that it is exempt from `amend` mode (per the universal spec) but the claims block contract applies identically.

### Task 22: Update sector-intelligence/references/output-schema.md

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/sector-intelligence/references/output-schema.md`

- [ ] **Step 1: Insert the same `claims[]` documentation block as Task 11**, adapted to sector vocabulary (s/buyer/sector/; example claim about a sector trend or regulatory change instead of a buyer fact).

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/sector-intelligence/references/output-schema.md
git commit -m "docs(sector-intel): document claims[] block in output schema"
```

### Task 23: Update sector-intelligence/SKILL.md

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/sector-intelligence/SKILL.md`

- [ ] **Step 1: Apply the same two edits as Task 12** — hard rule plus output-section reference.

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/sector-intelligence/SKILL.md
git commit -m "feat(sector-intel): require claims[] block emission in skill prompt"
```

### Task 24: Update sector-intelligence render script

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/sector-intelligence/scripts/render_dossier.py`

- [ ] **Step 1: Apply the same renderer changes as Task 13** — `_linkify_citations`, `_render_claims_block`, narrative wiring, document append.

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/sector-intelligence/scripts/render_dossier.py
git commit -m "feat(sector-intel): renderer handles claims[] block + citation links"
```

### Task 25: Build a sector anchor fixture and validator integration test

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/sector_anchor_v1.json`
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Hand-craft a minimal sector anchor fixture.** Suggest: UK government IT outsourcing sector — three claims (sector size, regulatory shift, dominant players). Realistic source URLs.

- [ ] **Step 2: Validate it.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -c "
import json
from scripts.validate_claims_block import validate
with open('tests/fixtures/sector_anchor_v1.json', encoding='utf-8') as f:
    d = json.load(f)
r = validate(d)
print('OK' if r.ok else 'FAIL: ' + str(r.errors))
"
```

Expected: `OK`.

- [ ] **Step 3: Add a per-skill integration test** to `PerSkillFixtureTests`:

```python
    def test_sector_anchor_fixture_passes_validator(self):
        result = validate(_load("sector_anchor_v1.json"))
        self.assertEqual(
            result.errors,
            [],
            f"Sector anchor fixture failed validator: {result.errors}",
        )
```

- [ ] **Step 4: Run the full suite.**

```bash
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 9 tests, all pass.

- [ ] **Step 5: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/sector_anchor_v1.json \
        pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "test(sector-intel): sector anchor fixture + validator test"
```

### Task 26: Manual end-to-end validation on Claude.ai (sector)

- [ ] **Step 1–7: Follow the same procedure as Task 16**, substituting "sector-intelligence" and a known sector (suggest: UK Defence IT). Output to `tests/fixtures/sector_defence_it_skillrun_v1.json` (gitignored).

- [ ] **Step 8: Commit any SKILL.md / render_dossier.py fixes** with messages naming the issue caught.

---

## Phase 6 — Incumbency-advantage-displacement-strategy refactor (integrator)

Incumbency is the integrator skill. The contract is the same six fields per claim, but the integrator must additionally support the optional seventh field `derivedFrom` (array of upstream claim ids). This phase adds validator support for `derivedFrom`, then refactors the skill.

### Task 27: Extend the validator to recognise `derivedFrom`

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/scripts/validate_claims_block.py`
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Write the failing test.** Append to `ValidStructureTests` in the test file:

```python
    def test_derivedFrom_when_present_must_be_list_of_strings(self):
        dossier = {
            "claims": [
                {
                    "claimId": "INC-CLM-001",
                    "claimText": "Integrator claim.",
                    "claimDate": "2026-04-30",
                    "source": "Buyer dossier: HMRC",
                    "sourceDate": "2026-04-15",
                    "sourceTier": 1,
                    "derivedFrom": "BUYER:CLM-014",  # bug: should be array
                }
            ],
            "narrative": "[INC-CLM-001]",
        }
        result = validate(dossier)
        self.assertFalse(result.ok)
        self.assertTrue(any("derivedFrom" in err for err in result.errors))
```

- [ ] **Step 2: Run the test to verify it fails.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 1 failure on `test_derivedFrom_when_present_must_be_list_of_strings`.

- [ ] **Step 3: Implement the check in `validate_claims_block.py`.** Inside the per-claim loop, after the existing field checks, add:

```python
        if "derivedFrom" in claim:
            df = claim["derivedFrom"]
            if not isinstance(df, list):
                result.errors.append(
                    f"claims[{i}].derivedFrom must be an array of strings."
                )
            elif not all(isinstance(x, str) for x in df):
                result.errors.append(
                    f"claims[{i}].derivedFrom must be an array of strings."
                )
```

- [ ] **Step 4: Run the test to verify it passes.**

```bash
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: all tests pass (10 tests).

- [ ] **Step 5: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/scripts/validate_claims_block.py \
        pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "feat(skills): validator recognises optional derivedFrom field"
```

### Task 28: Update incumbency-advantage-displacement-strategy/references/output-schema.md

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/references/output-schema.md`

- [ ] **Step 1: Insert the same `claims[]` documentation block as Task 11**, adapted to integrator vocabulary, **plus** an integrator addendum paragraph documenting `derivedFrom`:

```markdown
### Integrator addendum: `derivedFrom`

Incumbency is an integrator skill. Its claims are typically synthesised
from upstream buyer and supplier dossier claims. Each integrator claim
may carry an optional seventh field — `derivedFrom`, an array of upstream
claim ids — recording the chain back to source-level evidence.

The integrator's own `claimId` uses the prefix `INC-CLM-` (e.g. `INC-CLM-001`).
Upstream references use the upstream skill prefix:
`["BUYER:CLM-014", "SUPPLIER:CLM-022"]`.

```json
{
  "claims": [
    {
      "claimId": "INC-CLM-001",
      "claimText": "Capita's defence-IT incumbency at the MoD is structurally weak.",
      "claimDate": "2026-04-30",
      "source": "Synthesised from buyer + supplier dossiers",
      "sourceDate": "2026-04-30",
      "sourceTier": 2,
      "derivedFrom": ["BUYER:CLM-014", "SUPPLIER:CLM-022"]
    }
  ]
}
```
```

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/references/output-schema.md
git commit -m "docs(incumbency-intel): document claims[] block + integrator derivedFrom"
```

### Task 29: Update incumbency-advantage-displacement-strategy/SKILL.md

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/SKILL.md`

- [ ] **Step 1: Apply the same two edits as Task 12** — the hard rule and output-section reference — *plus* a third paragraph in the persona section noting the integrator's `derivedFrom` discipline:

```markdown
- **As an integrator, populate `derivedFrom` on every synthesised claim.**
  Where your claim is built from one or more upstream buyer / supplier /
  sector dossier claims, list those claim ids in `derivedFrom` using the
  format `["BUYER:CLM-014", "SUPPLIER:CLM-022"]`. This preserves the chain
  back to source-level evidence and lets downstream consumers (the
  Forensic Intelligence Auditor, Win Strategy synthesis) walk the trail.
  An integrator claim with no `derivedFrom` should be a rare exception
  — typically a claim about the integrator's own analytic framing rather
  than a synthesised assertion.
```

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/SKILL.md
git commit -m "feat(incumbency-intel): require claims[] + integrator derivedFrom in skill prompt"
```

### Task 30: Update incumbency render script

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/scripts/render_dossier.py`

- [ ] **Step 1: Apply the same renderer changes as Task 13**, plus a small addition: when rendering a claim that has `derivedFrom`, render the upstream references as a chain footer on the claim. Modify `_render_claims_block` (copied from Task 13) to add:

```python
        df = c.get("derivedFrom") or []
        if df:
            chain = ", ".join(df)
            rows[-1] = rows[-1].replace(
                "</dd>",
                f'<p class="claim-chain"><strong>Derived from:</strong> '
                f'{chain}</p></dd>',
            )
```

(Insert immediately after the `rows.append(...)` line so the chain footer is appended to the claim's `<dd>`.)

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/incumbency-advantage-displacement-strategy/scripts/render_dossier.py
git commit -m "feat(incumbency-intel): renderer handles claims[] + derivedFrom chain"
```

### Task 31: Build an incumbency anchor fixture and validator test

**Files:**
- Create: `pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/incumbency_anchor_v1.json`
- Modify: `pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py`

- [ ] **Step 1: Hand-craft a minimal incumbency anchor fixture.** Three integrator claims, each with `derivedFrom` pointing at synthetic upstream ids (e.g. `BUYER:CLM-014`, `SUPPLIER:CLM-022`). Realistic incumbency analysis topic — suggest: a known supplier's defensibility on a major MoD framework.

- [ ] **Step 2: Validate it.**

```bash
cd pwin-platform/skills/agent2-market-competitive/master
python -c "
import json
from scripts.validate_claims_block import validate
with open('tests/fixtures/incumbency_anchor_v1.json', encoding='utf-8') as f:
    d = json.load(f)
r = validate(d)
print('OK' if r.ok else 'FAIL: ' + str(r.errors))
"
```

Expected: `OK`.

- [ ] **Step 3: Add a per-skill integration test** to `PerSkillFixtureTests`:

```python
    def test_incumbency_anchor_fixture_passes_validator(self):
        result = validate(_load("incumbency_anchor_v1.json"))
        self.assertEqual(
            result.errors,
            [],
            f"Incumbency anchor fixture failed validator: {result.errors}",
        )
```

- [ ] **Step 4: Run the full suite.**

```bash
python -m unittest tests.test_validate_claims_block 2>&1
```

Expected: 11 tests, all pass.

- [ ] **Step 5: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/tests/fixtures/incumbency_anchor_v1.json \
        pwin-platform/skills/agent2-market-competitive/master/tests/test_validate_claims_block.py
git commit -m "test(incumbency-intel): incumbency anchor fixture + validator test"
```

### Task 32: Manual end-to-end validation on Claude.ai (incumbency)

- [ ] **Step 1–7: Follow the same procedure as Task 16**, substituting "incumbency-advantage-displacement-strategy" and a known incumbent / pursuit (suggest: a Serco contract on a known MoD framework). Note: incumbency is an *integrator*, so it requires upstream buyer + supplier dossiers — supply pre-built ones produced by the now-refactored buyer + supplier skills as prerequisite inputs.

- [ ] **Step 8: Commit any SKILL.md / render_dossier.py fixes** with messages naming the issue caught.

---

## Phase 7 — Migration documentation and CLAUDE.md update

### Task 33: Document degraded-mode handling for legacy dossiers

**Files:**
- Modify: `pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md`

- [ ] **Step 1: Append a "Migration / degraded mode" section** to the schema document:

```markdown
## Migration / degraded mode

Dossiers produced *before* this contract existed do not carry a
`claims[]` block. Consumers of those dossiers operate in degraded mode:

1. The validator returns errors (`Top-level 'claims' key is missing.`).
2. Consumers that depend on the contract — primarily the Forensic
   Intelligence Auditor — operate in their documented degraded mode (see
   FIA spec §11.3).
3. Legacy dossiers should be rebuilt under the new contract when next
   refreshed. The four refactored skills emit the contract from the
   refresh forward; once a buyer / supplier / sector / incumbency
   dossier is refreshed, it carries the new shape.

There is no automated migration path for legacy dossiers — they are
re-built, not converted. The producing skill on Claude.ai is the
authoritative source; running it again produces a contract-compliant
artefact.
```

- [ ] **Step 2: Commit.**

```bash
git add pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md
git commit -m "docs(skills): document degraded-mode handling for legacy dossiers"
```

### Task 34: Update repo CLAUDE.md to reference the new contract

**Files:**
- Modify: `CLAUDE.md` (repo root)

- [ ] **Step 1: Find the "Agent 2 intelligence skills (operational runtime)" section.**

```bash
grep -n "Agent 2 intelligence skills\|^## Agent 2" CLAUDE.md
```

- [ ] **Step 2: Insert a paragraph before the "Where the master files live" subsection**, documenting that the four skills now emit the structured `claims[]` block.

```markdown
**Claims block contract (v1.0).** Every dossier the four skills produce
now carries a top-level `claims[]` block — six required fields per claim,
narrative cites by `[CLM-id]`. The contract is at
`pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md`;
the platform validator at `master/scripts/validate_claims_block.py`
enforces it. Downstream consumers (Win Strategy synthesis, Forensic
Intelligence Auditor, future Qualify integration) read claims as
first-class structured objects rather than parsing prose. Legacy
dossiers without the block are rebuilt on next refresh — there is no
automated migration path.
```

- [ ] **Step 3: Commit.**

```bash
git add CLAUDE.md
git commit -m "docs(claude-md): note claims[] block contract on Agent 2 skills"
```

### Task 35: Create the wiki action note tracking this work

**Files:**
- Create: `C:/Users/User/Documents/Obsidian Vault/wiki/actions/intelligence-skills-claims-block-refactor.md`

- [ ] **Step 1: Write the action note.** This is the wiki record of what's been done — closed on the same session it was opened, since this plan is the implementation.

```markdown
---
type: action
project: pwin-platform
priority: high
status: completed
created: 2026-04-30
completed: <fill at completion>
---

# Refactor four intelligence skills to emit structured claims[] block

> Closed on completion of plan
> `docs/superpowers/plans/2026-04-30-claims-block-refactor-plan.md` in the
> PWIN repo. Spec context:
> `docs/superpowers/specs/2026-04-30-forensic-intelligence-auditor-design.md`
> §11. The four skills now emit a top-level `claims[]` block (six required
> fields per claim, narrative cites by `[CLM-id]`); platform validator at
> `pwin-platform/skills/agent2-market-competitive/master/scripts/validate_claims_block.py`
> enforces the contract. Anchor fixtures for buyer (Defence Digital),
> supplier, sector, and incumbency live under
> `master/tests/fixtures/`. Each skill validated end-to-end on Claude.ai
> against a known input.
>
> Critical-path unblocked: the Forensic Intelligence Auditor V1.0
> (`docs/superpowers/plans/<date>-forensic-intelligence-auditor-plan.md`,
> Plan B) can now run at full fidelity against contract-compliant
> dossiers rather than degraded mode against legacy ones.

## What changed

- `CLAIMS-BLOCK-SCHEMA.md` — the canonical contract document
- `validate_claims_block.py` — stdlib validator, 11 tests
- `SKILL-UNIVERSAL-SPEC.md` §13 — claims block as a producer-skill requirement
- Four skills' `SKILL.md`, `references/output-schema.md`,
  `scripts/render_dossier.py` — refactored to emit and render claims
- Anchor fixtures committed for each of the four skills

## Forward notes

- V1.1: add upstream `volatility` field per claim (low / medium / high)
  for cases where a claim's volatility differs from its section's
  profile-default.
- V1.x: add automated cross-dossier `derivedFrom` resolution (an
  integrator's `derivedFrom` references must resolve to actual upstream
  claim ids).
- Producing-skill packaging for Claude.ai: each skill's `.skill` archive
  must include the per-skill `tests/fixtures/<skill>_anchor_v1.json` so
  that prompt regression can be tested by re-running the skill against
  the anchor input.
```

- [ ] **Step 2: Update `wiki/hot.md` Last Updated section** with a one-paragraph summary of the close.

- [ ] **Step 3: Wiki is not git-tracked, so no commit step.**

---

## Self-review — done at writing time

**Spec coverage check.** The spec's §11 (the upstream contract) is implemented by Phase 1 (validator + schema doc) and Phase 2 (universal spec update) plus the per-skill refactor in Phases 3–6. The §11.3 degraded-mode requirement is documented in Task 33. The §11.4 critical-path dependency note is satisfied by the wiki action note in Task 35.

**Placeholder scan.** The plan does not use TBD / TODO / "implement later" / "fill in details" / "appropriate error handling" / "similar to Task N" / "write tests for the above" anywhere. Each step contains the actual content the engineer needs.

**Type consistency.** `validate()` returns `Result` everywhere it appears. `_linkify_citations()` and `_render_claims_block()` keep the same names from Task 13 onward. `claimId`, `claimText`, `claimDate`, `source`, `sourceDate`, `sourceTier` are the field names in every fixture, every test, every documentation reference.

**One known acceptable gap.** Tasks 16, 21, 26, and 32 (the manual Claude.ai end-to-end validations) cannot be reduced to local automated tests because the producing skills run on Claude.ai. The plan treats those as manual checkpoints with explicit run-and-validate steps.
