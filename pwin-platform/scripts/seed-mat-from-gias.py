"""seed-mat-from-gias.py — fetch DfE GIAS multi-academy trust register and emit
a canonical-glossary-shaped JSON. Stdlib only. Idempotent.

Run from pwin-platform/:
    python scripts/seed-mat-from-gias.py

Output: pwin-platform/knowledge/multi-academy-trusts.json
"""
import csv
import io
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge",
    "multi-academy-trusts.json",
)


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:80] or "unknown"


def fetch_gias_groups():
    """Try recent dates to find the latest allGroupsData CSV from DfE GIAS."""
    base = "https://ea-edubase-api-prod.azurewebsites.net/edubase/downloads/public/allGroupsData{}.csv"
    today = datetime.now()
    for delta in range(0, 30):
        d = today - timedelta(days=delta)
        url = base.format(d.strftime("%d%m%Y"))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PWIN/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode("utf-8-sig", errors="replace")
            print(f"  Fetched GIAS groups from {url}")
            return list(csv.DictReader(io.StringIO(raw)))
        except Exception as e:
            print(f"  {d.strftime('%d%m%Y')} failed: {e}", file=sys.stderr)
            continue
    raise RuntimeError(
        "Could not fetch GIAS groups CSV for any date in the past 30 days"
    )


def main():
    print("Fetching DfE GIAS multi-academy trust register...")
    rows = fetch_gias_groups()
    print(f"  {len(rows):,} total group rows")

    entities = []
    seen_ids = set()
    skipped_closed = 0
    skipped_wrong_type = 0

    for r in rows:
        # Column names vary slightly across GIAS CSV versions — try both forms
        status = (r.get("Group Status") or r.get("Status") or "").strip().lower()
        if status not in ("open", ""):
            skipped_closed += 1
            continue

        gtype = (r.get("Group Type") or r.get("GroupType") or "").strip().lower()
        if "multi-academy trust" not in gtype and "multi academy trust" not in gtype:
            skipped_wrong_type += 1
            continue

        name = (r.get("Group Name") or r.get("GroupName") or "").strip()
        if not name:
            continue

        uid = (r.get("Group UID") or r.get("GroupUID") or "").strip()

        # Build a stable canonical_id from the name; append UID to break ties
        cid = slugify(name)
        if cid in seen_ids:
            cid = f"{cid}-{uid}" if uid else f"{cid}-dup"
        seen_ids.add(cid)

        # Aliases: canonical name + uppercase variant (matches publisher casing)
        aliases = [name]
        if name.upper() != name:
            aliases.append(name.upper())

        entities.append({
            "canonical_id": cid,
            "canonical_name": name,
            "abbreviation": None,
            "type": "Multi-academy trust",
            "subtype": "Academy trust (England)",
            "parent_ids": ["department-for-education"],
            "child_ids": [],
            "aliases": aliases,
            "status": "active",
            "source": "hand_curated_mat",
            "gias_uid": uid or None,
        })

    print(f"  Included {len(entities):,} open MATs")
    print(f"  Skipped {skipped_closed:,} closed/proposed groups")
    print(f"  Skipped {skipped_wrong_type:,} non-MAT group types")

    out = {
        "_comment": (
            f"UK multi-academy trusts from DfE Get Information About Schools (GIAS), "
            f"fetched {datetime.now(timezone.utc).strftime('%Y-%m-%d')}. "
            "Only open MATs included. Re-run seed-mat-from-gias.py quarterly to refresh."
        ),
        "version": "1.0",
        "source": "hand_curated_mat",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "entities": entities,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(entities):,} MATs to {OUT}")


if __name__ == "__main__":
    main()
