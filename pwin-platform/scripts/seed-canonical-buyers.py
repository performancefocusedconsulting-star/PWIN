#!/usr/bin/env python3
"""
PWIN Platform — Seed Buyer Canonical Glossary

Fetches the GOV.UK organisations API and produces a hierarchical canonical
buyer glossary for the platform knowledge layer.

Output: ~/.pwin/platform/buyer-canonical-glossary.json

The glossary feeds:
  - pwin-competitive-intel canonical buyer layer (entity resolution)
  - Skill 1 v2 supplier dossier (so 'MoD's top suppliers' is meaningful)
  - Internal bid-director query interface (so hierarchy queries work)

Sources covered in this version:
  - GOV.UK organisations API: central gov + ministerial + non-ministerial
    departments, executive agencies, ALBs (NDPBs), public corporations,
    devolved administrations
  - ~1,251 entities total

Sources NOT yet covered (planned for future iterations):
  - NHS organisations (NHS ODS data: trusts, ICBs, foundations)
  - Local authorities (~350 councils via ONS LA codes)
  - Police forces (43 territorial + specialist)
  - Devolved sub-orgs that aren't on the GOV.UK index

Run this once to seed, then re-run after the GOV.UK index changes
(quarterly is plenty for central gov, which doesn't restructure often).

Usage:
    python3 scripts/seed-canonical-buyers.py
    python3 scripts/seed-canonical-buyers.py --output /tmp/test.json
    python3 scripts/seed-canonical-buyers.py --include-closed
"""
import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

API_BASE = "https://www.gov.uk/api/organisations"
USER_AGENT = "PWIN-CanonicalGlossary/1.0 (UK public sector procurement intelligence)"
DEFAULT_OUT = os.path.join(os.path.expanduser("~"), ".pwin", "platform", "buyer-canonical-glossary.json")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge")
HAND_CURATED = os.path.join(KNOWLEDGE_DIR, "central-buying-agencies.json")
NHS_ODS = os.path.join(KNOWLEDGE_DIR, "nhs-organisations.json")
LOCAL_AUTH = os.path.join(KNOWLEDGE_DIR, "local-authorities.json")


def fetch_page(page: int) -> dict:
    """Fetch one page from the GOV.UK organisations API."""
    url = f"{API_BASE}?page={page}"
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  page {page} attempt {attempt+1} failed: {e}; retrying", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    return {}


def fetch_all() -> list:
    """Fetch all organisation pages with polite delay between calls."""
    print("Fetching GOV.UK organisations API...")
    first = fetch_page(1)
    pages = first["pages"]
    total = first["total"]
    print(f"  {total} organisations across {pages} pages")
    results = list(first["results"])
    for p in range(2, pages + 1):
        if p % 10 == 0:
            print(f"  page {p}/{pages}...")
        results.extend(fetch_page(p)["results"])
        time.sleep(0.4)
    print(f"  fetched {len(results)} organisations")
    return results


def slug_from_url(web_url: str) -> str:
    """Extract slug from /government/organisations/<slug> URL."""
    if not web_url:
        return ""
    return web_url.rstrip("/").rsplit("/", 1)[-1]


def normalise_aliases(title: str, abbreviation: str | None) -> list[str]:
    """Build a deduplicated alias list for matching against raw FTS buyer names."""
    aliases = set()
    if title:
        t = title.strip()
        aliases.add(t)
        aliases.add(t.upper())
        aliases.add(t.lower())
        # Drop "The " prefix common in formal names
        if t.lower().startswith("the "):
            aliases.add(t[4:])
            aliases.add(t[4:].upper())
    if abbreviation:
        a = abbreviation.strip()
        aliases.add(a)
        aliases.add(a.upper())
    return sorted(a for a in aliases if a)


def transform(orgs: list, include_closed: bool) -> dict:
    """Transform raw GOV.UK organisations into the canonical glossary schema."""
    entities = []
    skipped_closed = 0
    for o in orgs:
        details = o.get("details") or {}
        closed_at = details.get("closed_at")
        if closed_at and not include_closed:
            skipped_closed += 1
            continue

        slug = details.get("slug") or slug_from_url(o.get("web_url", ""))
        if not slug:
            continue

        title = (o.get("title") or "").strip()
        abbreviation = details.get("abbreviation") or None
        fmt = (o.get("format") or "Other").strip()

        parent_ids = [
            slug_from_url(p.get("web_url", "")) or (p.get("details") or {}).get("slug")
            for p in (o.get("parent_organisations") or [])
        ]
        parent_ids = [p for p in parent_ids if p]

        child_ids = [
            slug_from_url(c.get("web_url", "")) or (c.get("details") or {}).get("slug")
            for c in (o.get("child_organisations") or [])
        ]
        child_ids = [c for c in child_ids if c]

        superseded_by = [
            slug_from_url(s.get("web_url", "")) or (s.get("details") or {}).get("slug")
            for s in (o.get("superseding_organisations") or [])
        ]
        superseded_by = [s for s in superseded_by if s]

        entities.append({
            "canonical_id": slug,
            "canonical_name": title,
            "abbreviation": abbreviation,
            "type": fmt,
            "parent_ids": parent_ids,
            "child_ids": child_ids,
            "aliases": normalise_aliases(title, abbreviation),
            "status": "closed" if closed_at else "active",
            "closed_at": closed_at,
            "superseded_by": superseded_by,
            "gov_uk_url": o.get("web_url"),
            "gov_uk_id": o.get("analytics_identifier"),
        })

    # Tag GOV.UK entries with their source for provenance
    for e in entities:
        e["source"] = "gov_uk_api"

    glossary = {
        "version": "1.1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": [
            {"name": "GOV.UK organisations API", "url": API_BASE},
            {"name": "Hand-curated central buying agencies", "file": "pwin-platform/knowledge/central-buying-agencies.json"},
        ],
        "scope": "UK central government departments and ALBs (GOV.UK API) plus central buying agencies and procurement consortia (hand curated)",
        "not_covered_yet": [
            "NHS organisations (trusts, ICBs)",
            "Local authorities (councils)",
            "Police forces",
            "Universities (excluding HE buying consortia)",
            "Schools and academy trusts",
        ],
        "skipped_closed": skipped_closed,
        "entities": entities,
    }
    return glossary


def merge_hand_curated(glossary: dict, hand_curated_path: str) -> tuple[int, int]:
    """Merge hand-curated entries into the glossary in-place.

    Returns (added_count, alias_supplement_count).

    Special handling for entities of type 'Alias supplement': these append
    their aliases to an existing canonical entry (matched by canonical_id)
    rather than creating a duplicate. This is how we avoid creating two
    'Crown Commercial Service' entries when the GOV.UK API already has one.
    """
    if not os.path.exists(hand_curated_path):
        print(f"  WARNING: hand-curated file not found at {hand_curated_path}")
        return 0, 0

    with open(hand_curated_path) as f:
        hand = json.load(f)

    by_id = {e["canonical_id"]: e for e in glossary["entities"]}

    added = 0
    merged = 0
    for entry in hand.get("entities", []):
        cid = entry["canonical_id"]

        # Merge model: canonical_id is the merge key.
        # If the canonical_id already exists, append the hand-curated
        # aliases to the existing entry rather than creating a duplicate.
        if cid in by_id:
            existing = by_id[cid]
            seen = set(a.lower() for a in existing["aliases"])
            new_aliases = [a for a in entry.get("aliases", []) if a.lower() not in seen]
            existing["aliases"].extend(new_aliases)
            if new_aliases:
                print(f"    +{len(new_aliases)} aliases merged into {cid}")
            merged += 1
            continue

        # An alias-only entry whose target doesn't exist in this fetch.
        # Skip silently rather than creating a meaningless new entity.
        if entry.get("type") in ("Alias merge", "Alias supplement"):
            print(f"    SKIP alias-merge with no target: {cid}")
            continue

        # New canonical entity — fill defaults and add
        entry.setdefault("status", "active")
        entry.setdefault("closed_at", None)
        entry.setdefault("superseded_by", [])
        entry.setdefault("gov_uk_url", None)
        entry.setdefault("gov_uk_id", None)
        glossary["entities"].append(entry)
        by_id[cid] = entry
        added += 1
        print(f"    +new entity: {cid}")

    glossary["entity_count"] = len(glossary["entities"])
    glossary["entities"] = sorted(glossary["entities"], key=lambda e: (e["type"], e["canonical_name"]))
    return added, merged


def merge_nhs_ods(glossary: dict, nhs_path: str) -> int:
    """Merge NHS ODS entities into the glossary in-place. Returns added count."""
    if not os.path.exists(nhs_path):
        print(f"  WARNING: NHS ODS file not found at {nhs_path}")
        print(f"  Run: python3 scripts/seed-nhs-ods.py  to generate it")
        return 0

    with open(nhs_path) as f:
        nhs = json.load(f)

    by_id = {e["canonical_id"]: e for e in glossary["entities"]}

    added = 0
    merged = 0
    for entry in nhs.get("entities", []):
        cid = entry["canonical_id"]
        if cid in by_id:
            # Merge aliases
            existing = by_id[cid]
            seen = set(a.lower() for a in existing["aliases"])
            new_aliases = [a for a in entry.get("aliases", []) if a.lower() not in seen]
            existing["aliases"].extend(new_aliases)
            if new_aliases:
                merged += 1
            continue

        entry.setdefault("closed_at", None)
        entry.setdefault("superseded_by", [])
        entry.setdefault("gov_uk_url", None)
        entry.setdefault("gov_uk_id", None)
        glossary["entities"].append(entry)
        by_id[cid] = entry
        added += 1

    glossary["entity_count"] = len(glossary["entities"])
    glossary["entities"] = sorted(glossary["entities"], key=lambda e: (e["type"], e["canonical_name"]))
    if merged:
        print(f"    {merged} alias merges into existing entries")
    return added


def write_output(glossary: dict, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(glossary, f, indent=2, ensure_ascii=False)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\nWrote {output_path} ({size_kb:.1f} KB)")


def print_stats(glossary: dict) -> None:
    print(f"\n=== Canonical buyer glossary stats ===")
    print(f"  Total entities       : {glossary['entity_count']}")
    print(f"  Skipped (closed)     : {glossary['skipped_closed']}")
    by_type: dict[str, int] = {}
    with_parent = 0
    with_children = 0
    for e in glossary["entities"]:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
        if e["parent_ids"]:
            with_parent += 1
        if e["child_ids"]:
            with_children += 1
    print(f"\n  By type:")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    {n:>5}  {t}")
    print(f"\n  With parent_ids      : {with_parent}")
    print(f"  With child_ids       : {with_children}")
    print(f"\n  Top hierarchies (entities with most children):")
    parents = sorted(
        [e for e in glossary["entities"] if e["child_ids"]],
        key=lambda e: -len(e["child_ids"]),
    )[:10]
    for p in parents:
        print(f"    {len(p['child_ids']):>3} children: {p['canonical_name']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=DEFAULT_OUT, help=f"Output JSON path (default: {DEFAULT_OUT})")
    parser.add_argument("--include-closed", action="store_true", help="Include closed organisations in the output")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip GOV.UK fetch and re-merge from existing output (for fast iteration on hand-curated data)")
    args = parser.parse_args()

    if args.skip_fetch and os.path.exists(args.output):
        print(f"Loading existing glossary from {args.output} (skipping GOV.UK fetch)")
        with open(args.output) as f:
            glossary = json.load(f)
        # Strip any prior hand-curated entries before re-merging
        glossary["entities"] = [e for e in glossary["entities"] if e.get("source") != "hand_curated"]
    else:
        orgs = fetch_all()
        glossary = transform(orgs, include_closed=args.include_closed)

    print(f"\nMerging hand-curated central buying agencies from {HAND_CURATED}...")
    added, merges = merge_hand_curated(glossary, HAND_CURATED)
    print(f"  +{added} new entities, {merges} alias merges")

    print(f"\nMerging NHS ODS organisations from {NHS_ODS}...")
    nhs_added = merge_nhs_ods(glossary, NHS_ODS)
    print(f"  +{nhs_added} new NHS entities")

    print(f"\nMerging local authorities from {LOCAL_AUTH}...")
    la_added = merge_nhs_ods(glossary, LOCAL_AUTH)  # Same merge logic works
    print(f"  +{la_added} new local authority entities")

    write_output(glossary, args.output)
    print_stats(glossary)


if __name__ == "__main__":
    main()
