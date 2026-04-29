"""seed-housing-from-rsh.py — fetch the RSH (Regulator of Social Housing)
registered providers list and emit a canonical-glossary-shaped JSON.

Filters to private registered providers only (designation != 'Local authority').
Local-authority registered providers are already in the canonical buyer layer.

The RSH publishes the register as a monthly xlsx snapshot at:
  https://www.gov.uk/government/publications/current-registered-providers-of-social-housing

This script scrapes that page for the current xlsx link, downloads it, and
parses it using only the Python standard library (zipfile + xml.etree).
No external dependencies required.

Idempotent — safe to re-run; output is deterministic for the same source file.

Usage:
    python3 scripts/seed-housing-from-rsh.py
    python3 scripts/seed-housing-from-rsh.py --output /tmp/housing-test.json
"""
import argparse
import io
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

GOV_UK_PAGE = "https://www.gov.uk/government/publications/current-registered-providers-of-social-housing"
USER_AGENT = "PWIN-CanonicalGlossary/1.0 (UK public sector procurement intelligence)"

DEFAULT_OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge", "housing-associations.json"
)

SS_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:80] or "unknown"


def find_download_url() -> str:
    """Scrape the GOV.UK page for the xlsx/csv download link."""
    req = urllib.request.Request(GOV_UK_PAGE, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", errors="replace")
    hits = re.findall(
        r'href="(https://assets\.publishing\.service\.gov\.uk[^"]+\.(?:csv|xlsx))"',
        html
    )
    csv_hits = [h for h in hits if h.endswith(".csv")]
    if csv_hits:
        return csv_hits[0]
    if hits:
        return hits[0]
    raise RuntimeError(
        "Could not find an xlsx or csv download link on the RSH GOV.UK page. "
        "The page layout may have changed — check: " + GOV_UK_PAGE
    )


def parse_xlsx(content: bytes) -> list[dict]:
    """Parse xlsx bytes using zipfile + xml.etree (stdlib only).

    Returns a list of dicts with keys matching the xlsx column headers.
    """
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        # Shared strings table (all string values are stored here by index)
        with z.open("xl/sharedStrings.xml") as f:
            ss_tree = ET.parse(f)
        shared_strings = [
            "".join(t.text or "" for t in si.iter(f"{{{SS_NS}}}t"))
            for si in ss_tree.findall(f".//{{{SS_NS}}}si")
        ]

        # First worksheet
        with z.open("xl/worksheets/sheet1.xml") as f:
            ws_tree = ET.parse(f)

    rows = ws_tree.findall(f".//{{{SS_NS}}}row")
    if not rows:
        return []

    def cell_value(cell_el) -> str:
        cell_type = cell_el.get("t", "")
        v_el = cell_el.find(f"{{{SS_NS}}}v")
        if v_el is None:
            return ""
        raw = v_el.text or ""
        if cell_type == "s":
            idx = int(raw)
            return shared_strings[idx] if idx < len(shared_strings) else ""
        return raw

    def row_values(row_el) -> list[str]:
        return [cell_value(c) for c in row_el.findall(f"{{{SS_NS}}}c")]

    headers = row_values(rows[0])
    records = []
    for row_el in rows[1:]:
        vals = row_values(row_el)
        # Pad to header length in case trailing empty cells are omitted
        while len(vals) < len(headers):
            vals.append("")
        records.append(dict(zip(headers, vals)))
    return records


def build_aliases(name: str) -> list[str]:
    """Return a small set of alias forms for a provider name."""
    aliases = set()
    if name:
        aliases.add(name)
        aliases.add(name.upper())
        # Drop trailing 'Limited' / 'Ltd' variant
        for suffix in (" Limited", " Ltd", " limited", " ltd"):
            if name.endswith(suffix):
                short = name[: -len(suffix)].strip()
                if short:
                    aliases.add(short)
                    aliases.add(short.upper())
    return sorted(a for a in aliases if a)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch RSH registered providers and emit housing-associations.json")
    parser.add_argument("--output", default=DEFAULT_OUT, help="Output path (default: knowledge/housing-associations.json)")
    args = parser.parse_args()

    print("Finding RSH registered providers download link...")
    url = find_download_url()
    print(f"  Downloading: {url}")

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        content = r.read()
    print(f"  Downloaded {len(content):,} bytes")

    records = parse_xlsx(content)
    print(f"  {len(records)} rows in spreadsheet")

    entities = []
    seen_ids: set[str] = set()
    skipped_la = 0

    for rec in records:
        name = rec.get("Organisation name", "").strip()
        designation = rec.get("Designation", "").strip()
        reg_no = rec.get("Registration number", "").strip()

        if not name:
            continue

        # Skip local authorities — they are already in the canonical buyer layer
        if designation.lower() == "local authority":
            skipped_la += 1
            continue

        cid = slugify(name)
        # Disambiguate the rare case of two providers with the same slug
        if cid in seen_ids:
            cid = f"{cid}-{slugify(reg_no)}" if reg_no else f"{cid}-dup"
        seen_ids.add(cid)

        entities.append({
            "canonical_id": cid,
            "canonical_name": name,
            "abbreviation": None,
            "type": "Registered provider",
            "subtype": "Housing association",
            "parent_ids": [],
            "child_ids": [],
            "aliases": build_aliases(name),
            "status": "active",
            "source": "hand_curated_housing",
            "registration_number": reg_no,
            "designation": designation,
        })

    out = {
        "_comment": (
            f"UK private registered providers of social housing (RSH register), "
            f"fetched {datetime.now(timezone.utc).strftime('%Y-%m-%d')}. "
            f"Local-authority RPs excluded ({skipped_la} skipped) — already in canonical layer."
        ),
        "version": "1.0",
        "source": "hand_curated_housing",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "entities": entities,
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(entities)} housing providers to {args.output}")
    print(f"  Skipped {skipped_la} local-authority RPs (already canonicalised)")


if __name__ == "__main__":
    main()
