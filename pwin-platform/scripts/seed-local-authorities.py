#!/usr/bin/env python3
"""
PWIN Platform — Seed Local Authorities from ONS + FTS

Builds a canonical glossary of UK local authorities by combining:
  1. ONS Open Geography Portal LAD (Local Authority District) 2024 list
     — the authoritative register of ~361 UK councils with codes and types
  2. County layer (E10) for English county councils
  3. FTS buyer data — actual published council names used in procurement

The ONS LAD code prefix encodes the authority type:
  E06 = English unitary authority
  E07 = English non-metropolitan district
  E08 = English metropolitan borough
  E09 = London borough
  E10 = English county (separate layer)
  W06 = Welsh unitary authority
  S12 = Scottish council area
  N09 = Northern Ireland district

For each authority, template-based aliases are generated from the area
name + authority type. FTS-observed names that match by keyword are
added as additional aliases to catch publisher drift.

Output: pwin-platform/knowledge/local-authorities.json

Usage:
    python3 scripts/seed-local-authorities.py
    python3 scripts/seed-local-authorities.py --db-path /path/to/bid_intel.db
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import urllib.request
from datetime import datetime, timezone

ONS_LAD_URL = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "LAD_DEC_2024_UK_NC/FeatureServer/0/query"
    "?where=1%3D1&outFields=LAD24CD,LAD24NM&returnGeometry=false"
    "&resultRecordCount=500&f=json"
)
ONS_CTY_URL = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "CTY_DEC_2024_EN_NC/FeatureServer/0/query"
    "?where=1%3D1&outFields=CTY24CD,CTY24NM&returnGeometry=false"
    "&resultRecordCount=100&f=json"
)
USER_AGENT = "PWIN-CanonicalGlossary/1.0 (UK public sector procurement intelligence)"
OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge",
    "local-authorities.json",
)
DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "pwin-competitive-intel", "db", "bid_intel.db",
)


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  attempt {attempt + 1} failed: {e}; retrying", file=sys.stderr)
    return {}


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[''']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def classify_and_alias(code: str, name: str) -> tuple[str, str, list[str]]:
    """Return (type, subtype, aliases) based on ONS code prefix and area name."""
    prefix = code[:3]
    aliases = set()
    n = name.strip()

    def add(s):
        aliases.add(s)
        aliases.add(s.upper())
        aliases.add(s.lower())

    if prefix == "E06":
        # English unitary authority
        add(f"{n} Council")
        add(f"{n} City Council")
        add(f"{n} Borough Council")
        add(f"{n} Unitary Authority")
        return "Unitary authority", "English unitary", sorted(aliases)

    elif prefix == "E07":
        # English non-metropolitan district
        add(f"{n} District Council")
        add(f"{n} Borough Council")
        add(f"{n} Council")
        return "District council", "English district", sorted(aliases)

    elif prefix == "E08":
        # English metropolitan borough
        add(f"{n} Metropolitan Borough Council")
        add(f"Metropolitan Borough of {n}")
        add(f"Metropolitan Borough Council of {n}")
        add(f"City of {n} Metropolitan District Council")
        add(f"{n} City Council")
        add(f"{n} Metropolitan District Council")
        add(f"{n} Council")
        add(f"{n} MBC")
        return "Metropolitan borough", "English metropolitan", sorted(aliases)

    elif prefix == "E09":
        # London borough
        add(f"London Borough of {n}")
        add(f"LB of {n}")
        add(f"{n} London Borough Council")
        add(f"{n} Council")
        # Special case: City of London / City of Westminster
        if n.startswith("City of"):
            add(n)
            add(f"{n} Corporation")
        return "London borough", "London", sorted(aliases)

    elif prefix == "E10":
        # English county
        add(f"{n} County Council")
        add(f"{n} Council")
        return "County council", "English county", sorted(aliases)

    elif prefix == "W06":
        # Welsh unitary authority
        add(f"{n} Council")
        add(f"{n} County Council")
        add(f"{n} County Borough Council")
        # Some Welsh councils use "Cyngor" prefix
        add(f"Cyngor {n}")
        return "County borough", "Welsh unitary", sorted(aliases)

    elif prefix == "S12":
        # Scottish council area
        add(f"{n} Council")
        add(f"City of {n} Council")
        add(f"{n}")
        return "Council area", "Scottish council", sorted(aliases)

    elif prefix == "N09":
        # Northern Ireland district
        add(f"{n} District Council")
        add(f"{n} City Council")
        add(f"{n} Council")
        add(f"{n} City Council and District Council")
        add(f"{n} Borough Council")
        return "NI district", "Northern Ireland", sorted(aliases)

    else:
        add(f"{n} Council")
        return "Local authority", "Other", sorted(aliases)


def fetch_fts_council_names(db_path: str) -> dict[str, int]:
    """Extract all council-like buyer names from the FTS database.

    Returns {lowercased_name: award_count}.
    """
    if not os.path.exists(db_path):
        print(f"  FTS database not found at {db_path} — skipping FTS cross-match")
        return {}

    c = sqlite3.connect(db_path)
    rows = c.execute("""
        SELECT b.name, COUNT(*) cnt
        FROM awards a JOIN notices n ON a.ocid=n.ocid JOIN buyers b ON n.buyer_id=b.id
        WHERE a.status='active' AND a.value_amount_gross >= 1e6
        GROUP BY LOWER(TRIM(b.name))
    """).fetchall()
    c.close()

    council_kws = ['council', 'borough', 'county council', 'city council',
                   'district council', 'metropolitan']
    result = {}
    for name, cnt in rows:
        nl = (name or '').lower().strip()
        if any(k in nl for k in council_kws):
            # Filter false positives
            if any(k in nl for k in ('nhs', 'health', 'police', 'fire', 'school', 'academy', 'university')):
                continue
            result[nl] = (name.strip(), cnt)
    return result


def match_fts_to_ons(entities: list, fts_councils: dict) -> int:
    """Add FTS-observed name variants as aliases to the matching ONS entity.

    Simple keyword matching: for each FTS council name, find the ONS entity
    whose area name appears in the FTS name. Returns count of matches made.
    """
    matched = 0
    used_fts = set()

    for entity in entities:
        # Extract area name tokens from canonical_name (strip "Council" etc.)
        area_words = [w for w in entity["_area_name"].lower().split()
                      if w not in ('and', 'the', 'of', 'upon', 'in', 'le')]

        existing_aliases_lower = set(a.lower() for a in entity["aliases"])

        for fts_key, (fts_name, fts_cnt) in fts_councils.items():
            if fts_key in used_fts:
                continue
            # Check if most area words appear in the FTS name
            fts_words = set(fts_key.split())
            if len(area_words) >= 2:
                if sum(1 for w in area_words if w in fts_words) >= len(area_words) * 0.7:
                    if fts_name.lower() not in existing_aliases_lower:
                        entity["aliases"].append(fts_name)
                        entity["aliases"].append(fts_name.upper())
                        existing_aliases_lower.add(fts_name.lower())
                        existing_aliases_lower.add(fts_name.upper().lower())
                    used_fts.add(fts_key)
                    matched += 1
            elif len(area_words) == 1:
                # Single-word area name — must be a strong match
                if area_words[0] in fts_words and 'council' in fts_words:
                    if fts_name.lower() not in existing_aliases_lower:
                        entity["aliases"].append(fts_name)
                        entity["aliases"].append(fts_name.upper())
                        existing_aliases_lower.add(fts_name.lower())
                    used_fts.add(fts_key)
                    matched += 1

    return matched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default=DEFAULT_DB, help="Path to FTS bid_intel.db for cross-matching")
    args = parser.parse_args()

    # 1. Fetch ONS LAD 2024
    print("Fetching ONS LAD 2024...")
    lad_data = fetch_json(ONS_LAD_URL)
    lads = [(f["attributes"]["LAD24CD"], f["attributes"]["LAD24NM"])
            for f in lad_data.get("features", [])]
    print(f"  {len(lads)} local authority districts")

    # 2. Fetch ONS County 2024
    print("Fetching ONS County 2024...")
    cty_data = fetch_json(ONS_CTY_URL)
    counties = [(f["attributes"]["CTY24CD"], f["attributes"]["CTY24NM"])
                for f in cty_data.get("features", [])]
    print(f"  {len(counties)} counties")

    all_areas = lads + counties

    # 3. Build canonical entities
    entities = []
    for code, name in all_areas:
        otype, subtype, aliases = classify_and_alias(code, name)
        entities.append({
            "canonical_id": f"la-{slugify(name)}",
            "canonical_name": f"{name} Council" if "Council" not in name else name,
            "abbreviation": None,
            "type": otype,
            "subtype": subtype,
            "ons_code": code,
            "parent_ids": [],
            "child_ids": [],
            "aliases": aliases,
            "status": "active",
            "source": "ons_la_codes",
            "_area_name": name,
        })

    print(f"  {len(entities)} canonical entities built")

    # 4. Cross-match against FTS council names
    print(f"\nCross-matching against FTS database at {args.db_path}...")
    fts_councils = fetch_fts_council_names(args.db_path)
    print(f"  {len(fts_councils)} distinct council-like FTS buyer names found")
    matched = match_fts_to_ons(entities, fts_councils)
    print(f"  {matched} FTS names matched to ONS entities and added as aliases")

    # 5. Strip internal fields and write
    for e in entities:
        del e["_area_name"]

    output = {
        "_comment": "UK local authorities from ONS Open Geography Portal LAD/CTY 2024, cross-matched against FTS buyer names.",
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "ons_la_codes",
        "source_urls": [ONS_LAD_URL[:80] + "...", ONS_CTY_URL[:80] + "..."],
        "entity_count": len(entities),
        "entities": sorted(entities, key=lambda e: (e["type"], e["canonical_name"])),
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"\nWrote {OUTPUT} ({size_kb:.1f} KB)")

    # Stats
    by_type = {}
    for e in output["entities"]:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    print(f"\n=== Local authority glossary stats ===")
    print(f"  Total entities: {output['entity_count']}")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    {n:>5}  {t}")


if __name__ == "__main__":
    main()
