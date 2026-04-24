#!/usr/bin/env python3
"""
Generate Obsidian wiki pages for every canonical buyer entity.

Reads  : ~/.pwin/platform/buyer-canonical-glossary.json
Writes : wiki/public-sector-buyers/ (one markdown file per entity + _index.md)

Routing:
  gov_uk_api + Ministerial/Non-ministerial/Devolved -> departments/
  gov_uk_api (everything else)                       -> albs-and-agencies/
  nhs_ods                                            -> nhs/
  ons_la_codes                                       -> local-authorities/
  hand_curated by type                               -> central-buying | nhs | local-authorities | albs-and-agencies

Idempotent. Preserves everything from '## Notes' onwards across regens.
Re-run after glossary updates.

Usage:
    python agent/generate-buyer-wiki.py
    python agent/generate-buyer-wiki.py --dry-run
    python agent/generate-buyer-wiki.py --wiki /path/to/vault/wiki/public-sector-buyers
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date

GLOSSARY_DEFAULT = os.path.join(os.path.expanduser("~"), ".pwin", "platform", "buyer-canonical-glossary.json")
WIKI_DEFAULT = "C:/Users/User/Documents/Obsidian Vault/wiki/public-sector-buyers"

SENTINEL = "<!-- GENERATED-ABOVE - do not edit above this line; rebuilt from the glossary -->"
NOTES_HEADING = "## Notes"
NOTES_STUB = (
    NOTES_HEADING
    + "\n\n<!-- free-form intelligence: incumbents, procurement behaviour, reorg history, contacts -->\n"
)

# Characters forbidden in Windows filenames; replace with hyphen.
FILENAME_FORBIDDEN = re.compile(r'[<>:"/\\|?*]')


def safe_filename(name: str) -> str:
    name = FILENAME_FORBIDDEN.sub("-", name)
    name = re.sub(r"\s+", " ", name).strip()
    # Trailing dots/spaces break on Windows.
    return name.rstrip(". ")


def route_folder(entity: dict) -> str:
    src = entity.get("source")
    t = entity.get("type") or ""
    if src == "gov_uk_api":
        if t in ("Ministerial department", "Non-ministerial department", "Devolved government"):
            return "departments"
        return "albs-and-agencies"
    if src == "nhs_ods":
        return "nhs"
    if src == "ons_la_codes":
        return "local-authorities"
    if src == "hand_curated":
        if t == "Central buying agency":
            return "central-buying"
        if t in ("Scottish NHS Board", "NI HSC Trust"):
            return "nhs"
        if t == "Combined authority":
            return "local-authorities"
        return "albs-and-agencies"
    return "albs-and-agencies"


def type_slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")


def load_glossary(path: str) -> dict:
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        # The shipped glossary is latin-1 in places (Windows-1252 punctuation).
        return json.loads(raw.decode("latin-1"))


def resolve_filenames(entities: list) -> dict:
    """Return {canonical_id: (folder, filename_stem)} with collisions disambiguated.

    First entity with a given (folder, stem) wins the bare name; later entities
    get '<stem> (<canonical_id>)'.
    """
    mapping = {}
    taken = set()
    for e in entities:
        folder = route_folder(e)
        stem = safe_filename(e["canonical_name"])
        key = (folder, stem.lower())
        if key in taken:
            stem = f"{stem} ({e['canonical_id']})"
            key = (folder, stem.lower())
        taken.add(key)
        mapping[e["canonical_id"]] = (folder, stem)
    return mapping


def build_generated_block(entity: dict, filename_map: dict, id_to_name: dict) -> str:
    name = entity["canonical_name"]
    abbr = entity.get("abbreviation")
    t = entity.get("type")
    src = entity.get("source")
    status = entity.get("status", "active")
    url = entity.get("gov_uk_url")

    def link_for(cid):
        # Wikilinks resolve by filename stem. Use disambiguated stem if set.
        if cid in filename_map:
            return filename_map[cid][1]
        return id_to_name.get(cid, cid)

    parents = [link_for(p) for p in (entity.get("parent_ids") or []) if p in id_to_name]
    children = sorted({link_for(c) for c in (entity.get("child_ids") or []) if c in id_to_name})
    aliases = sorted({a for a in (entity.get("aliases") or []) if a and a != name})

    tags = ["buyer", (src or "unknown").replace("_", "-")]
    if t:
        tags.append(type_slug(t))

    fm = ["---", f"canonical_id: {entity['canonical_id']}"]
    if abbr:
        fm.append(f'abbreviation: "{_yaml_escape(abbr)}"')
    if t:
        fm.append(f'type: "{_yaml_escape(t)}"')
    fm.append(f"source: {src}")
    fm.append(f"status: {status}")
    if parents:
        fm.append("parents:")
        for p in parents:
            fm.append(f'  - "[[{p}]]"')
    else:
        fm.append("parents: []")
    if children:
        fm.append("children:")
        for c in children:
            fm.append(f'  - "[[{c}]]"')
    else:
        fm.append("children: []")
    if aliases:
        fm.append("aliases:")
        for a in aliases:
            fm.append(f'  - "{_yaml_escape(a)}"')
    if url:
        fm.append(f"gov_uk_url: {url}")
    fm.append(f"tags: [{', '.join(tags)}]")
    fm.append(f"generated_at: {date.today().isoformat()}")
    fm.append("---")

    body = ["", f"# {name}", ""]
    meta_line_parts = []
    if t:
        meta_line_parts.append(f"**Type:** {t}")
    if parents:
        label = "Parent" + ("s" if len(parents) > 1 else "")
        meta_line_parts.append(f"**{label}:** " + ", ".join(f"[[{p}]]" for p in parents))
    if abbr:
        meta_line_parts.append(f"**Abbreviation:** {abbr}")
    if meta_line_parts:
        body.append("  ·  ".join(meta_line_parts))
    if url:
        body.append(f"**GOV.UK:** {url}")
    body.append("")

    if children:
        body.append("## Children")
        body.append("")
        for c in children:
            body.append(f"- [[{c}]]")
        body.append("")

    if aliases:
        body.append("## Aliases")
        body.append("")
        body.append(" · ".join(aliases))
        body.append("")

    body.append(SENTINEL)
    body.append("")

    return "\n".join(fm) + "\n" + "\n".join(body)


def _yaml_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def load_existing_notes(path: str) -> str:
    """Return everything from the '## Notes' heading onward, or the stub if absent."""
    if not os.path.exists(path):
        return NOTES_STUB
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return NOTES_STUB
    # Prefer a Notes heading after the sentinel; fall back to the first one.
    sent_idx = content.find(SENTINEL)
    start = content.find(NOTES_HEADING, sent_idx if sent_idx >= 0 else 0)
    if start < 0:
        return NOTES_STUB
    notes = content[start:]
    if not notes.endswith("\n"):
        notes += "\n"
    return notes


def write_entity(out_dir: str, entity: dict, filename_map: dict, id_to_name: dict, dry_run: bool):
    folder, stem = filename_map[entity["canonical_id"]]
    path = os.path.join(out_dir, folder, stem + ".md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    generated = build_generated_block(entity, filename_map, id_to_name)
    notes = load_existing_notes(path)
    content = generated + "\n" + notes
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read() == content:
                return "unchanged"
    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return "written"


def build_index(out_dir: str, entities: list, meta: dict, filename_map: dict, dry_run: bool):
    by_source = Counter(e.get("source") for e in entities)
    by_type = Counter(e.get("type") for e in entities)
    by_folder = Counter(route_folder(e) for e in entities)

    def by_type_sorted(type_name):
        return sorted(
            [e for e in entities if e.get("type") == type_name],
            key=lambda e: e["canonical_name"].lower(),
        )

    ministerial = by_type_sorted("Ministerial department")
    non_ministerial = by_type_sorted("Non-ministerial department")
    devolved = by_type_sorted("Devolved government")
    consortia = by_type_sorted("Central buying agency")
    combined_auths = by_type_sorted("Combined authority")

    out = []
    out.append("# UK Public Sector Buyers")
    out.append("")
    out.append(
        "Entity map of UK public sector buyer organisations. "
        "Each file below represents one canonical buyer; parent/child relationships "
        "are wikilinks so the Obsidian graph and backlinks surface the org chart."
    )
    out.append("")
    out.append(f"- **Source of truth:** `~/.pwin/platform/buyer-canonical-glossary.json` (v{meta.get('version', '?')}, generated {meta.get('generated_at', '?')})")
    out.append("- **Regenerate:** `python pwin-competitive-intel/agent/generate-buyer-wiki.py`")
    out.append(f"- **Total entities:** {len(entities)}")
    out.append("")

    out.append("## Breakdown")
    out.append("")
    out.append("| Source | Count |")
    out.append("|---|---:|")
    for src, n in by_source.most_common():
        out.append(f"| `{src}` | {n} |")
    out.append("")
    out.append("| Folder | Count |")
    out.append("|---|---:|")
    for folder, n in sorted(by_folder.items()):
        out.append(f"| `{folder}/` | {n} |")
    out.append("")

    def list_entities(section_title, items, show_abbr=True):
        if not items:
            return
        out.append(f"## {section_title}")
        out.append("")
        for e in items:
            stem = filename_map[e["canonical_id"]][1]
            suffix = f" ({e['abbreviation']})" if show_abbr and e.get("abbreviation") else ""
            if stem == e["canonical_name"]:
                out.append(f"- [[{stem}]]{suffix}")
            else:
                out.append(f"- [[{stem}|{e['canonical_name']}]]{suffix}")
        out.append("")

    list_entities("Ministerial departments", ministerial)
    list_entities("Non-ministerial departments", non_ministerial)
    list_entities("Devolved governments", devolved, show_abbr=False)
    list_entities("Central buying agencies and consortia", consortia)
    list_entities("Combined authorities", combined_auths, show_abbr=False)

    out.append("## Browse the rest by folder")
    out.append("")
    out.append("- `albs-and-agencies/` — arm's-length bodies, executive agencies, NDPBs, tribunals, courts. Open a parent department above and follow children, or use the graph view.")
    out.append("- `nhs/` — NHS trusts, foundation trusts, ICBs, Scottish NHS boards, NI HSC trusts.")
    out.append("- `local-authorities/` — district, unitary, county, metropolitan, London borough, NI district councils.")
    out.append("")

    gaps = meta.get("not_covered_yet") or []
    if gaps:
        out.append("## Known gaps")
        out.append("")
        # The glossary's not_covered_yet is stale — NHS and LAs are now covered.
        for gap in gaps:
            lg = gap.lower()
            if "nhs" in lg or "local authorit" in lg or "council" in lg:
                out.append(f"- ~~{gap}~~ — now covered")
            else:
                out.append(f"- {gap}")
        out.append("")

    out.append("## Top types (descriptive)")
    out.append("")
    out.append("| Type | Count |")
    out.append("|---|---:|")
    for t, n in by_type.most_common(15):
        out.append(f"| {t} | {n} |")
    out.append("")

    out.append("## How this is used across PWIN")
    out.append("")
    out.append("- **pwin-competitive-intel** — the glossary powers `get_buyer_profile` and supplier-history roll-ups across a department's entire footprint, not just the named entity.")
    out.append("- **pwin-strategy** (Agent 3) — stakeholder map and competitor field map enrichment in S2; Buyer Decision Thesis context in S3.")
    out.append("- **pwin-qualify** (paid tier, future) — buyer context and incumbent detection injected into AI assurance review.")
    out.append("- **pwin-bid-execution** — incumbent flags and buyer patterns during bid production.")
    out.append("- **bidequity-verdict** — incumbent detection and buyer relationship mapping for post-loss forensics.")
    out.append("")

    out.append("## Working notes")
    out.append("")
    out.append("Open any entity and append intelligence under its `## Notes` section — incumbents, procurement behaviour, reorg history, reliable contacts, framework usage. The generator preserves that content across regens. Do not edit above the `GENERATED-ABOVE` sentinel; anything there will be overwritten.")
    out.append("")
    out.append("Re-run the generator whenever the glossary is rebuilt (e.g. after a GOV.UK API refresh or machinery-of-government change). New entities are created with an empty Notes stub; existing entities retain their notes.")
    out.append("")

    content = "\n".join(out)
    path = os.path.join(out_dir, "_index.md")
    os.makedirs(out_dir, exist_ok=True)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read() == content:
                return "unchanged"
    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return "written"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glossary", default=GLOSSARY_DEFAULT)
    ap.add_argument("--wiki", default=WIKI_DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    data = load_glossary(args.glossary)
    entities = data["entities"]
    id_to_name = {e["canonical_id"]: e["canonical_name"] for e in entities}

    filename_map = resolve_filenames(entities)
    collisions = defaultdict(list)
    for cid, (folder, stem) in filename_map.items():
        collisions[(folder, stem)].append(cid)
    dupes = {k: v for k, v in collisions.items() if len(v) > 1}
    if dupes:
        # Shouldn't happen after resolve_filenames; defensive.
        print(f"WARNING: unresolved filename collisions: {len(dupes)}", file=sys.stderr)

    stats = Counter()
    for e in entities:
        stats[write_entity(args.wiki, e, filename_map, id_to_name, args.dry_run)] += 1

    idx_status = build_index(args.wiki, entities, data, filename_map, args.dry_run)

    print(f"Entities  : {len(entities)}")
    print(f"Written   : {stats['written']}")
    print(f"Unchanged : {stats['unchanged']}")
    print(f"Index     : {idx_status}")
    print(f"Target    : {args.wiki}")
    if args.dry_run:
        print("(dry run - no files written)")


if __name__ == "__main__":
    main()
