#!/usr/bin/env python3
"""
Patch the canonical buyer glossary with alias additions for known orphan
variants that surface against existing canonical entities.

Specifically:
- "The Legal Aid Agency" (8 rows) → legal-aid-agency
- "D S T L Defence Science & Technology Laboratory" (2 rows) → dstl
- "Defence Infrastructure Organisation (DIO) : Defence Infrastructure Organisation (DIO)" (1 row) → dio
- "DE&S Deca" (4 rows) → defence-equipment-and-support (rolling up — small enough not to warrant separate canonical for now)
- "Department of Justice - Youth Justice Agency" + 4 variants (5 rows) → youth-justice-agency-of-northern-ireland

Idempotent: extends existing canonical entries in-place rather than adding new ones.

Usage:
    python agent/patch_alias_gaps.py
"""
import json
import os
import sys
from datetime import datetime, timezone

GLOSSARY_PATH = os.path.join(
    os.path.expanduser("~"), ".pwin", "platform", "buyer-canonical-glossary.json"
)


PATCHES = {
    "legal-aid-agency": [
        "The Legal Aid Agency",
        "the legal aid agency",
    ],
    "defence-science-and-technology-laboratory": [
        "D S T L Defence Science & Technology Laboratory",
        "d s t l defence science & technology laboratory",
        "D S T L",
        "Defence, Science and Technology Laboratory",
    ],
    "defence-infrastructure-organisation": [
        "Defence Infrastructure Organisation (DIO) : Defence Infrastructure Organisation (DIO)",
        "defence infrastructure organisation (dio) : defence infrastructure organisation (dio)",
        "DIO Commercial",
        "Ministry of Defence, DIO, Defence Infrastructure Organisation (DIO)",
    ],
    "defence-equipment-and-support": [
        "DE&S Deca",
        "de&s deca",
        "DGM PT, DE&S",
    ],
    "youth-justice-agency-of-northern-ireland": [
        "Department of Justice - Youth Justice Agency",
        "department of justice - youth justice agency",
        "Department of Justice for Northern Ireland - Youth Justice Agency",
        "DoJ - Youth Justice Agency",
        "The Department of Justice - Youth Justice Agency",
        "Youth Justice Agency",
    ],
}


def main():
    if not os.path.exists(GLOSSARY_PATH):
        print(f"ERROR: glossary not found at {GLOSSARY_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(GLOSSARY_PATH) as f:
        gloss = json.load(f)

    by_id = {e["canonical_id"]: e for e in gloss["entities"]}

    total_added = 0
    for canonical_id, new_aliases in PATCHES.items():
        if canonical_id not in by_id:
            print(f"  SKIP: canonical_id {canonical_id} not in glossary")
            continue
        entity = by_id[canonical_id]
        existing = set(a.lower().strip() for a in entity.get("aliases", []))
        added_for_this = 0
        for new in new_aliases:
            if new.lower().strip() not in existing:
                entity.setdefault("aliases", []).append(new)
                existing.add(new.lower().strip())
                added_for_this += 1
        print(f"  {canonical_id:<55}  +{added_for_this} aliases (total now {len(entity['aliases'])})")
        total_added += added_for_this

    gloss["generated_at"] = datetime.now(timezone.utc).isoformat()

    with open(GLOSSARY_PATH, "w") as f:
        json.dump(gloss, f, indent=2)

    print(f"\n  Total aliases added: {total_added}")
    print("  Next step: run python agent/load-canonical-buyers.py to apply")


if __name__ == "__main__":
    main()
