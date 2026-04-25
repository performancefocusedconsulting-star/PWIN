#!/usr/bin/env python3
"""
Validate a sample of the OCP bulk file against the OCDS release schema
AND a set of practical sanity checks tuned to what our parser actually reads.

Why this exists
---------------
The Open Contracting Partnership publishes weekly bulk files of UK procurement
data in their "compiled release" format. We've ingested 175k+ releases from
the bulk file. This script samples the file and asks two questions:

  1. Schema-clean? — does each release validate against the published OCDS
     release schema (structural correctness, type safety, codelist values)?
  2. Parser-relevant? — for the fields OUR parser cares about (buyer, parties,
     awards, suppliers, value, dates), are there issues we may be silently
     swallowing? E.g. award with suppliers but no supplier id; buyer role
     party with no name; unparseable dates; negative or zero values where
     positive expected.

Run:
    .venv/Scripts/python.exe agent/validate_ocp_sample.py            # 5,000 sample
    .venv/Scripts/python.exe agent/validate_ocp_sample.py --n 1000   # smaller sample
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import sys
import time
import urllib.request
from pathlib import Path

import jsonschema

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
BULK_PATH = ROOT / "data" / "ocp-uk-fts.jsonl.gz"
LOG_DIR = ROOT / "logs"
SCHEMA_CACHE = ROOT / "data" / "ocds-release-schema-1.1.5.json"

OCDS_RELEASE_SCHEMA_URL = (
    "https://standard.open-contracting.org/schema/1__1__5/release-schema.json"
)


def load_schema():
    if SCHEMA_CACHE.exists():
        return json.loads(SCHEMA_CACHE.read_text(encoding="utf-8"))
    print(f"Downloading schema from {OCDS_RELEASE_SCHEMA_URL}...")
    with urllib.request.urlopen(OCDS_RELEASE_SCHEMA_URL, timeout=30) as r:
        text = r.read().decode("utf-8")
    SCHEMA_CACHE.parent.mkdir(exist_ok=True)
    SCHEMA_CACHE.write_text(text, encoding="utf-8")
    return json.loads(text)


def parser_relevant_checks(release: dict, errs: list[str]):
    """Sanity checks tuned to what our ingest.py actually reads."""
    parties = release.get("parties") or []
    party_ids = {p.get("id") for p in parties if p.get("id")}

    # Buyer
    buyer = release.get("buyer") or {}
    buyer_id = buyer.get("id")
    if not buyer_id and not buyer.get("name"):
        errs.append("missing-buyer")
    elif buyer_id and buyer_id not in party_ids:
        errs.append("buyer-id-not-in-parties")

    # Awards & suppliers
    for award in release.get("awards") or []:
        suppliers = award.get("suppliers") or []
        if not suppliers and award.get("status") == "active":
            errs.append("active-award-no-suppliers")
        for s in suppliers:
            if not s.get("name") and not s.get("id"):
                errs.append("supplier-no-name-no-id")
            elif s.get("id") and s.get("id") not in party_ids:
                errs.append("supplier-id-not-in-parties")
        val = (award.get("value") or {}).get("amount")
        if val is not None and isinstance(val, (int, float)) and val < 0:
            errs.append("award-value-negative")

    # Tender value
    tender = release.get("tender") or {}
    t_val = (tender.get("value") or {}).get("amount")
    if t_val is not None and isinstance(t_val, (int, float)) and t_val < 0:
        errs.append("tender-value-negative")

    # Date sanity (ours uses publishedDate, tenderPeriod, awardedDate, contractStart/End)
    for path, val in [
        ("release.date", release.get("date")),
        ("tender.tenderPeriod.endDate", (tender.get("tenderPeriod") or {}).get("endDate")),
    ]:
        if val and not isinstance(val, str):
            errs.append(f"date-not-string:{path}")

    # CPV codes — tender.classification + tender.items[].classification
    classification = tender.get("classification")
    has_cpv = bool(classification and classification.get("id"))
    for item in tender.get("items") or []:
        if (item.get("classification") or {}).get("id"):
            has_cpv = True
            break
    if release.get("awards") and not has_cpv:
        errs.append("award-no-cpv-on-tender")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000, help="How many releases to sample")
    args = ap.parse_args()

    LOG_DIR.mkdir(exist_ok=True)

    print(f"Loading OCDS release schema...")
    schema = load_schema()
    # Resolve $refs against the local schema only (release schema is self-contained
    # plus references within the same file). Using Draft7Validator keeps it fast.
    validator = jsonschema.Draft7Validator(schema)

    print(f"Streaming first {args.n:,} compiled releases from {BULK_PATH.name}...")
    schema_errors = collections.Counter()         # error_type -> count
    schema_paths = collections.Counter()          # JSON pointer-ish path -> count
    parser_errors = collections.Counter()
    sample_parser_examples: dict[str, list[str]] = collections.defaultdict(list)
    n_releases = 0
    n_with_any_schema_error = 0
    n_with_any_parser_error = 0
    t0 = time.time()

    with gzip.open(BULK_PATH, "rt", encoding="utf-8") as f:
        for line in f:
            if n_releases >= args.n:
                break
            n_releases += 1
            try:
                release = json.loads(line)
            except json.JSONDecodeError:
                schema_errors["broken-json-line"] += 1
                continue

            # Schema validation — capture top-level error categories
            had_schema_err = False
            for err in validator.iter_errors(release):
                had_schema_err = True
                # Bucket by validator (e.g. 'required', 'type', 'enum', 'format', 'pattern')
                schema_errors[err.validator or "unknown"] += 1
                # Also bucket by where the error happened (first 3 path elements)
                path_str = "/".join(str(p) for p in list(err.absolute_path)[:3]) or "<root>"
                schema_paths[path_str] += 1
            if had_schema_err:
                n_with_any_schema_error += 1

            # Parser-relevant checks
            release_errs: list[str] = []
            parser_relevant_checks(release, release_errs)
            if release_errs:
                n_with_any_parser_error += 1
                for e in set(release_errs):
                    parser_errors[e] += 1
                    if len(sample_parser_examples[e]) < 3:
                        sample_parser_examples[e].append(release.get("ocid", "?"))

            if n_releases % 500 == 0:
                print(f"  processed {n_releases:,}  ({time.time()-t0:.1f}s)")

    elapsed = time.time() - t0
    print(f"\nProcessed {n_releases:,} releases in {elapsed:.1f}s")

    # ── Report ─────────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("SCHEMA VALIDATION (against OCDS 1.1.5 release schema)")
    print("=" * 70)
    pct = 100 * n_with_any_schema_error / max(n_releases, 1)
    print(f"  Releases with ANY schema error: {n_with_any_schema_error:,} of {n_releases:,} ({pct:.1f}%)")
    print(f"\n  Top error categories:")
    for k, v in schema_errors.most_common(10):
        print(f"    {v:>7,}  {k}")
    print(f"\n  Top error locations (where in the JSON):")
    for k, v in schema_paths.most_common(10):
        print(f"    {v:>7,}  {k}")

    print()
    print("=" * 70)
    print("PARSER-RELEVANT SANITY CHECKS")
    print("=" * 70)
    pct = 100 * n_with_any_parser_error / max(n_releases, 1)
    print(f"  Releases with ANY parser-relevant issue: {n_with_any_parser_error:,} of {n_releases:,} ({pct:.1f}%)")
    print()
    for k, v in parser_errors.most_common():
        print(f"  {v:>7,} ({100*v/n_releases:>5.1f}%)  {k}")
        for ex in sample_parser_examples[k]:
            print(f"           example ocid: {ex}")

    # Write structured log
    log_path = LOG_DIR / "validate-ocp-sample.log"
    log_path.write_text(
        json.dumps({
            "n_releases": n_releases,
            "elapsed_seconds": elapsed,
            "schema_errors": dict(schema_errors),
            "schema_paths": dict(schema_paths),
            "parser_errors": dict(parser_errors),
            "parser_examples": {k: v for k, v in sample_parser_examples.items()},
            "n_with_any_schema_error": n_with_any_schema_error,
            "n_with_any_parser_error": n_with_any_parser_error,
        }, indent=2),
        encoding="utf-8",
    )
    print(f"\nFull log written to {log_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
