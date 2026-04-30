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
