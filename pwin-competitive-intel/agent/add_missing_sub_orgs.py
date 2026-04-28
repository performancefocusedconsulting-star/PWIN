#!/usr/bin/env python3
"""
Add a small set of missing major sub-organisations to the canonical buyer glossary.

Each entry follows the same shape as existing glossary entries (parent_ids,
aliases, abbreviation, etc.) so that re-running load-canonical-buyers.py picks
them up cleanly. Idempotent — re-running the script overwrites by canonical_id
rather than adding duplicates.

Usage:
    python agent/add_missing_sub_orgs.py
"""
import json
import os
import sys
from datetime import datetime, timezone

GLOSSARY_PATH = os.path.join(
    os.path.expanduser("~"), ".pwin", "platform", "buyer-canonical-glossary.json"
)


# Each entry: canonical_id, canonical_name, abbreviation, parent_id, type, aliases.
# Aliases include common spellings the raw FTS / Contracts Finder data uses.
NEW_ENTITIES = [
    {
        "canonical_id": "defence-digital",
        "canonical_name": "Defence Digital",
        "abbreviation": None,
        "parent_id": "ministry-of-defence",
        "type": "Sub-organisation",
        "aliases": [
            "Defence Digital",
            "defence digital",
            "DEFENCE DIGITAL",
            "Strategic Command, Defence Digital",
            "Ministry of Defence - Defence Digital",
            "Ministry of Defence, Defence Digital",
            "MOD Defence Digital",
            "Defence Digital, Ministry of Defence",
            "DD",
        ],
    },
    {
        "canonical_id": "uk-strategic-command",
        "canonical_name": "UK Strategic Command",
        "abbreviation": "STRATCOM",
        "parent_id": "ministry-of-defence",
        "type": "Sub-organisation",
        "aliases": [
            "UK Strategic Command",
            "uk strategic command",
            "Strategic Command",
            "strategic command",
            "STRATEGIC COMMAND",
            "STRATCOM",
            "Joint Forces Command",
            "Strategic Command Commercial",
            "Ministry of Defence - Strategic Command",
            "Ministry of Defence, Strategic Command",
            "Strategic Command, Ministry of Defence",
        ],
    },
    {
        "canonical_id": "british-army",
        "canonical_name": "British Army",
        "abbreviation": None,
        "parent_id": "ministry-of-defence",
        "type": "Sub-organisation",
        "aliases": [
            "British Army",
            "british army",
            "BRITISH ARMY",
            "Army Headquarters",
            "army headquarters",
            "ARMY HEADQUARTERS",
            "Army HQ",
            "Army Personnel Centre",
            "Land Forces",
            "Army Command",
            "Ministry of Defence - British Army",
            "Ministry of Defence, British Army",
            "British Army, Ministry of Defence",
        ],
    },
    {
        "canonical_id": "royal-navy",
        "canonical_name": "Royal Navy",
        "abbreviation": "RN",
        "parent_id": "ministry-of-defence",
        "type": "Sub-organisation",
        "aliases": [
            "Royal Navy",
            "royal navy",
            "ROYAL NAVY",
            "Navy Command",
            "navy command",
            "NAVY COMMAND",
            "Naval Command",
            "Naval Command Headquarters",
            "Ministry of Defence - Royal Navy",
            "Ministry of Defence, Royal Navy",
            "Royal Navy, Ministry of Defence",
        ],
    },
    {
        "canonical_id": "royal-air-force",
        "canonical_name": "Royal Air Force",
        "abbreviation": "RAF",
        "parent_id": "ministry-of-defence",
        "type": "Sub-organisation",
        "aliases": [
            "Royal Air Force",
            "royal air force",
            "ROYAL AIR FORCE",
            "RAF",
            "Air Command",
            "air command",
            "AIR COMMAND",
            "RAF Air Command",
            "Ministry of Defence - Royal Air Force",
            "Ministry of Defence, Royal Air Force",
        ],
    },
    {
        "canonical_id": "defence-business-services",
        "canonical_name": "Defence Business Services",
        "abbreviation": "DBS",
        "parent_id": "ministry-of-defence",
        "type": "Sub-organisation",
        "aliases": [
            "Defence Business Services",
            "defence business services",
            "DEFENCE BUSINESS SERVICES",
            "DBS",
            "Ministry of Defence - Defence Business Services",
        ],
    },
    {
        "canonical_id": "royal-fleet-auxiliary",
        "canonical_name": "Royal Fleet Auxiliary",
        "abbreviation": "RFA",
        "parent_id": "ministry-of-defence",
        "type": "Sub-organisation",
        "aliases": [
            "Royal Fleet Auxiliary",
            "royal fleet auxiliary",
            "Royal Fleet Auxiliary (RFA)",
            "RFA",
        ],
    },
    {
        "canonical_id": "infrastructure-and-projects-authority",
        "canonical_name": "Infrastructure and Projects Authority",
        "abbreviation": "IPA",
        "parent_id": "cabinet-office",
        "type": "Sub-organisation",
        "aliases": [
            "Infrastructure and Projects Authority",
            "infrastructure and projects authority",
            "INFRASTRUCTURE AND PROJECTS AUTHORITY",
            "IPA",
            "Infrastructure and Projects Authority (IPA)",
            "Infrastructure and Projects Authority : Cabinet Office",
            "Cabinet Office (Infrastructure and Projects Authority)",
        ],
    },
    {
        "canonical_id": "national-infrastructure-commission",
        "canonical_name": "National Infrastructure Commission",
        "abbreviation": "NIC",
        "parent_id": "hm-treasury",
        "type": "Sub-organisation",
        "aliases": [
            "National Infrastructure Commission",
            "national infrastructure commission",
            "NATIONAL INFRASTRUCTURE COMMISSION",
            "NIC",
            "National Infrastructure Commission : HM Treasury",
            "National Infrastructure Commission, HM Treasury",
        ],
    },
]


def main():
    if not os.path.exists(GLOSSARY_PATH):
        print(f"ERROR: glossary not found at {GLOSSARY_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(GLOSSARY_PATH) as f:
        gloss = json.load(f)

    by_id = {e["canonical_id"]: e for e in gloss["entities"]}

    added = 0
    updated = 0
    for new in NEW_ENTITIES:
        entity = {
            "canonical_id": new["canonical_id"],
            "canonical_name": new["canonical_name"],
            "abbreviation": new["abbreviation"],
            "aliases": list(dict.fromkeys(new["aliases"])),
            "type": new["type"],
            "parent_ids": [new["parent_id"]] if new["parent_id"] else [],
            "child_ids": [],
            "closed_at": None,
            "gov_uk_id": None,
            "gov_uk_url": None,
            "source": "manual_sub_org_pass_2026_04_28",
            "status": "active",
            "superseded_by": [],
        }
        if new["canonical_id"] in by_id:
            # Replace in place
            idx = next(i for i, e in enumerate(gloss["entities"]) if e["canonical_id"] == new["canonical_id"])
            gloss["entities"][idx] = entity
            updated += 1
        else:
            gloss["entities"].append(entity)
            added += 1

    gloss["entity_count"] = len(gloss["entities"])
    gloss["generated_at"] = datetime.now(timezone.utc).isoformat()

    with open(GLOSSARY_PATH, "w") as f:
        json.dump(gloss, f, indent=2)

    print(f"  added: {added}")
    print(f"  updated: {updated}")
    print(f"  glossary now has {gloss['entity_count']} entities")
    print(f"  next step: run python agent/load-canonical-buyers.py to apply")


if __name__ == "__main__":
    main()
