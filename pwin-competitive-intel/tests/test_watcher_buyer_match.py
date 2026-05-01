"""
Tests for watcher.gather_buyer_context canonical buyer resolution.

Integration tests — require the live bid_intel.db with canonical layer loaded.
Tests are skipped automatically when the DB is absent (CI / fresh checkout).
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))

from watcher import _norm_buyer_name, gather_buyer_context, BID_INTEL_DB

DB_AVAILABLE = BID_INTEL_DB.exists() and BID_INTEL_DB.stat().st_size > 0

skip_no_db = pytest.mark.skipif(not DB_AVAILABLE, reason="bid_intel.db not available")


# ── Unit tests — no DB required ───────────────────────────────────────────────

class TestNormBuyerName:
    def test_lowercases(self):
        assert _norm_buyer_name("Home Office") == "home office"

    def test_strips_leading_the(self):
        assert _norm_buyer_name("The Home Office") == "home office"

    def test_ampersand_to_and(self):
        assert _norm_buyer_name("Health & Safety Executive") == "health and safety executive"

    def test_strips_punctuation(self):
        assert _norm_buyer_name("Dept. of Transport") == "dept of transport"

    def test_collapses_whitespace(self):
        assert _norm_buyer_name("  Home   Office  ") == "home office"

    def test_empty(self):
        assert _norm_buyer_name("") == ""


# ── Integration tests — require live DB ───────────────────────────────────────

@skip_no_db
def test_compound_buyer_returns_awards():
    """BLC0329: 'BlueLight Commercial / NPCC / Home Office' must return awards."""
    result = gather_buyer_context("BlueLight Commercial / NPCC / Home Office")
    assert len(result.get("recent_awards", [])) >= 10, (
        "Expected ≥10 recent awards for Home Office; got "
        f"{len(result.get('recent_awards', []))}"
    )


@skip_no_db
def test_compound_buyer_returns_suppliers():
    result = gather_buyer_context("BlueLight Commercial / NPCC / Home Office")
    assert len(result.get("top_suppliers", [])) > 0


@skip_no_db
def test_simple_buyer_resolves():
    result = gather_buyer_context("Home Office")
    assert len(result.get("recent_awards", [])) >= 10


@skip_no_db
def test_unknown_buyer_returns_empty_gracefully():
    result = gather_buyer_context("Completely Nonexistent Organisation XYZ123")
    assert isinstance(result, dict)
    assert result.get("recent_awards", []) == [] or result == {"matched_buyers": []}
