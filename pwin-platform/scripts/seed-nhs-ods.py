#!/usr/bin/env python3
"""
PWIN Platform — Seed NHS Organisations from ODS API

Fetches NHS organisation data from the NHS ODS (Organisation Data Service)
API and produces a canonical buyer source file for merging into the
platform-level buyer glossary.

Output: pwin-platform/knowledge/nhs-organisations.json

NHS ODS covers:
  - NHS Trusts (RO197) — acute, community, mental health, ambulance
  - NHS Foundation Trusts (overlap with RO197, carry role RO98)
  - Integrated Care Boards / sub-ICBs (RO261)
  - Special Health Authorities (RO116)
  - NHS Support Agencies (RO213)

NHS entities not covered by ODS but already in the hand-curated file:
  - NHS Shared Business Services (SBS)
  - NHS Supply Chain (SCCL)
  - NHS National Services Scotland (NSS)
  - NHS Wales Shared Services Partnership (NWSSP)
  - NHS Commercial Solutions
  - HealthTrust Europe (HTE)

Sources NOT covered:
  - GP practices (too granular — ~7,000)
  - Individual hospitals within trusts
  - Social care providers

Usage:
    python3 scripts/seed-nhs-ods.py
    python3 scripts/seed-nhs-ods.py --include-inactive
"""
import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

ODS_BASE = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations"
USER_AGENT = "PWIN-CanonicalGlossary/1.0 (UK public sector procurement intelligence)"
OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge",
    "nhs-organisations.json",
)

# ODS roles to fetch — these are the procurement-relevant NHS org types
ROLES = [
    ("RO197", "NHS Trust"),
    ("RO261", "Integrated Care Board"),
    ("RO116", "Special Health Authority"),
    ("RO213", "NHS Support Agency"),
]


def fetch_role(role_id: str, status: str = "Active") -> list:
    """Fetch all orgs with the given role from ODS API."""
    url = f"{ODS_BASE}?Roles={role_id}&Status={status}&Limit=1000"
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
            return data.get("Organisations", [])
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  attempt {attempt + 1} failed: {e}; retrying", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    return []


def slugify(name: str) -> str:
    """Turn an NHS org name into a slug for canonical_id."""
    import re
    s = name.lower().strip()
    s = re.sub(r"[''']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def build_aliases(name: str) -> list:
    """Build alias list from the ODS name.

    ODS names are typically UPPERCASE. We include:
    - Original (uppercase)
    - Title case
    - Lowercase
    - Common 'NHS' prefix/suffix variants
    """
    aliases = set()
    name = name.strip()
    if not name:
        return []

    aliases.add(name)                    # Original: "STOCKPORT NHS FOUNDATION TRUST"
    aliases.add(name.title())            # Title: "Stockport Nhs Foundation Trust"
    aliases.add(name.lower())            # Lower: "stockport nhs foundation trust"

    # Fix "Nhs" → "NHS" in title case
    title = name.title().replace(" Nhs ", " NHS ").replace("Nhs ", "NHS ")
    if title.startswith("Nhs "):
        title = "NHS " + title[4:]
    aliases.add(title)                   # Fixed title: "Stockport NHS Foundation Trust"

    # For ICBs: FTS often uses "NHS X Integrated Care Board" but ODS might have
    # "NHS X ICB" or vice versa. Add both if relevant.
    nl = name.lower()
    if "integrated care board" in nl:
        icb_short = name.replace("INTEGRATED CARE BOARD", "ICB").replace("Integrated Care Board", "ICB")
        aliases.add(icb_short)
        aliases.add(icb_short.title().replace(" Nhs ", " NHS ").replace("Nhs ", "NHS "))
    elif nl.endswith(" icb"):
        icb_long = name[:-4] + " INTEGRATED CARE BOARD"
        aliases.add(icb_long)
        t = icb_long.title().replace(" Nhs ", " NHS ").replace("Nhs ", "NHS ")
        aliases.add(t)

    return sorted(a for a in aliases if a)


def classify_type(role_id: str, name: str) -> tuple[str, str]:
    """Return (type, subtype) based on ODS role and name patterns."""
    nl = name.lower()
    if role_id == "RO261":
        if "sub" in nl or "place" in nl or "location" in nl:
            return "Sub-ICB location", "NHS sub-ICB"
        return "Integrated Care Board", "NHS commissioning"
    if role_id == "RO197":
        if "foundation trust" in nl or "foundation" in nl:
            return "NHS Foundation Trust", "NHS provider"
        if "ambulance" in nl:
            return "NHS Ambulance Trust", "NHS provider"
        if "mental health" in nl or "mental" in nl:
            return "NHS Mental Health Trust", "NHS provider"
        if "community" in nl:
            return "NHS Community Trust", "NHS provider"
        return "NHS Trust", "NHS provider"
    if role_id == "RO116":
        return "Special Health Authority", "NHS special body"
    if role_id == "RO213":
        return "NHS Support Agency", "NHS support body"
    return "NHS organisation", "NHS other"


def fetch_all(include_inactive: bool) -> dict:
    """Fetch all NHS orgs across the target roles."""
    print("Fetching NHS organisations from ODS API...")
    all_orgs = {}  # keyed by OrgId to deduplicate cross-role overlaps

    for role_id, role_label in ROLES:
        status = "Active" if not include_inactive else "Active,Inactive"
        orgs = fetch_role(role_id, status)
        new = 0
        for o in orgs:
            oid = o["OrgId"]
            if oid not in all_orgs:
                all_orgs[oid] = {**o, "_roles": [(role_id, role_label)]}
                new += 1
            else:
                all_orgs[oid]["_roles"].append((role_id, role_label))
        print(f"  {role_label:30s} ({role_id}): {len(orgs):>4} fetched, {new:>4} new")
        time.sleep(0.5)

    print(f"  Total unique orgs: {len(all_orgs)}")
    return all_orgs


def transform(all_orgs: dict) -> dict:
    """Transform ODS orgs into canonical glossary format."""
    entities = []

    for oid, o in all_orgs.items():
        name = (o.get("Name") or "").strip()
        if not name:
            continue

        primary_role = o["_roles"][0][0]
        otype, subtype = classify_type(primary_role, name)

        entities.append({
            "canonical_id": f"nhs-{slugify(name)}",
            "canonical_name": name.title().replace(" Nhs ", " NHS ").replace("Nhs ", "NHS ").replace(" Of ", " of ").replace(" And ", " and ").replace(" The ", " the "),
            "abbreviation": None,
            "type": otype,
            "subtype": subtype,
            "ods_id": oid,
            "postcode": o.get("PostCode"),
            "parent_ids": [],
            "child_ids": [],
            "aliases": build_aliases(name),
            "status": "active" if o.get("Status") == "Active" else "inactive",
            "source": "nhs_ods",
        })

    output = {
        "_comment": "NHS organisations fetched from NHS ODS API for the canonical buyer glossary. Merged into ~/.pwin/platform/buyer-canonical-glossary.json by seed-canonical-buyers.py.",
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "nhs_ods",
        "source_url": ODS_BASE,
        "entity_count": len(entities),
        "entities": sorted(entities, key=lambda e: (e["type"], e["canonical_name"])),
    }
    return output


def print_stats(output: dict) -> None:
    print(f"\n=== NHS ODS glossary stats ===")
    print(f"  Total entities: {output['entity_count']}")
    by_type: dict[str, int] = {}
    for e in output["entities"]:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    {n:>5}  {t}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-inactive", action="store_true")
    args = parser.parse_args()

    all_orgs = fetch_all(args.include_inactive)
    output = transform(all_orgs)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"\nWrote {OUTPUT} ({size_kb:.1f} KB)")

    print_stats(output)


if __name__ == "__main__":
    main()
