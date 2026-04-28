"""
Unit tests for the canonical-layer name normaliser.

These cases all come from real publisher names found in the unmapped pile
on 2026-04-28. Each pair must collapse to the same normalised form so the
alias matcher resolves them to the same canonical entity.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import importlib.util

def _load(p):
    spec = importlib.util.spec_from_file_location("m", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

LOAD = _load(os.path.join(os.path.dirname(__file__), "load-canonical-buyers.py"))
BACK = _load(os.path.join(os.path.dirname(__file__), "backfill-buyer-aliases.py"))

EQUIVALENT = [
    # Caps vs mixed case
    ("UK SHARED BUSINESS SERVICES LIMITED", "UK Shared Business Services Ltd"),
    # & vs and
    ("UK RESEARCH & INNOVATION", "UK Research and Innovation"),
    # The-prefix
    ("THE UNIVERSITY OF BIRMINGHAM", "University of Birmingham"),
    # HM caps
    ("HM REVENUE & CUSTOMS", "HM Revenue & Customs"),
    # Trailing decoration: portal/eTendering
    ("Buckinghamshire Council - e-Tendering System", "Buckinghamshire Council"),
    # PLC / Limited / Ltd variants
    ("Highways England Company Limited", "Highways England"),
    # Punctuation noise
    ("Ministry of Justice.", "Ministry of Justice"),
]

def test_normaliser_collapses_equivalents():
    failures = []
    for a, b in EQUIVALENT:
        na, nb = LOAD.norm(a), LOAD.norm(b)
        if na != nb:
            failures.append(f"  load.norm: {a!r} -> {na!r}   !=   {b!r} -> {nb!r}")
        na, nb = BACK._norm(a), BACK._norm(b)
        if na != nb:
            failures.append(f"  back._norm: {a!r} -> {na!r}   !=   {b!r} -> {nb!r}")
    assert not failures, "\n" + "\n".join(failures)

def test_normalisers_are_mirrored():
    for a, b in EQUIVALENT:
        for s in (a, b):
            assert LOAD.norm(s) == BACK._norm(s), f"DIVERGENCE on {s!r}: load={LOAD.norm(s)!r} back={BACK._norm(s)!r}"

NON_EQUIVALENT = [
    # 'The' inside a real name vs adjacent entity — the leading-article strip must not collide
    ("The Crown Estate", "Crown Estate Commissioners"),
    # 'Ltd' as a substring of a word must not match the \bltd\b rule
    ("Ltdshire Council", "Limitedshire Council"),
    # Different councils with similar names must remain distinct
    ("Buckinghamshire Council", "Birmingham Council"),
    # eTendering inside a name (not a trailing publisher decoration) must survive
    ("Acme eTendering Solutions Ltd", "Acme Solutions Limited"),
]

def test_normaliser_preserves_distinctions():
    failures = []
    for a, b in NON_EQUIVALENT:
        if LOAD.norm(a) == LOAD.norm(b):
            failures.append(f"  load.norm over-collapses: {a!r} and {b!r} both -> {LOAD.norm(a)!r}")
        if BACK._norm(a) == BACK._norm(b):
            failures.append(f"  back._norm over-collapses: {a!r} and {b!r} both -> {BACK._norm(a)!r}")
    assert not failures, "\n" + "\n".join(failures)

if __name__ == "__main__":
    test_normalisers_are_mirrored()
    test_normaliser_collapses_equivalents()
    test_normaliser_preserves_distinctions()
    print("OK")
