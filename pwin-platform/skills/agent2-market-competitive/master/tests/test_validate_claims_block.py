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
