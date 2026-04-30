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

    def test_missing_required_field_fails(self):
        result = validate(_load("dossier_missing_field.json"))
        self.assertFalse(result.ok)
        self.assertTrue(
            any("sourceTier" in err for err in result.errors),
            f"Expected an error mentioning 'sourceTier', got: {result.errors}",
        )

    def test_orphan_citation_fails(self):
        result = validate(_load("dossier_orphan_citation.json"))
        self.assertFalse(result.ok)
        self.assertTrue(
            any("CLM-002" in err and "no claim" in err for err in result.errors),
            f"Expected an error mentioning orphan 'CLM-002', got: {result.errors}",
        )

    def test_bad_source_tier_fails(self):
        result = validate(_load("dossier_bad_tier.json"))
        self.assertFalse(result.ok)
        self.assertTrue(
            any("sourceTier" in err and "5" in err for err in result.errors),
            f"Expected an error mentioning bad sourceTier '5', got: {result.errors}",
        )

    def test_duplicate_claim_id_fails(self):
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

    def test_bad_claim_id_format_fails(self):
        dossier = {
            "claims": [
                {
                    "claimId": "claim-1",
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
        self.assertTrue(
            any("does not match required format" in err for err in result.errors)
        )


if __name__ == "__main__":
    unittest.main()
