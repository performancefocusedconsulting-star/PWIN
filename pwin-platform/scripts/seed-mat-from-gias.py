"""seed-mat-from-gias.py — build a canonical-glossary-shaped JSON for UK
multi-academy trusts (MATs) by combining:
  1. DfE GIAS Open Academies spreadsheet (Trust ID + Name + CH number)
  2. DfE Financial Benchmarking & Insights Tool (FBIT) suggest API
     (confirms canonical trust name + Companies House number)
  3. FBIT queries driven by buyer names in the PWIN intel database,
     to maximise coverage of trusts that actually appear in procurement data.

Stdlib only. Idempotent — re-running produces the same output given the same
upstream data.

Run from pwin-platform/:
    python scripts/seed-mat-from-gias.py

Output: pwin-platform/knowledge/multi-academy-trusts.json
"""
import csv
import io
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
import uuid
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

# ── Paths ────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
OUT = os.path.join(_ROOT, "knowledge", "multi-academy-trusts.json")
_DB = os.path.join(
    os.path.dirname(_ROOT),
    "pwin-competitive-intel", "db", "bid_intel.db",
)

# ── Helpers ──────────────────────────────────────────────────────────────────
def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:80] or "unknown"


def title_case_trust(s):
    """Convert ALL-CAPS trust name to proper title case."""
    if not s or s != s.upper() or len(s) <= 3:
        return s
    minor = {"a", "an", "the", "and", "but", "or", "for", "nor", "so",
             "yet", "at", "by", "in", "of", "on", "to", "up", "as", "if",
             "is", "it", "its", "c", "e", "rc"}
    words = s.lower().split()
    out = []
    for i, w in enumerate(words):
        out.append(w if (i > 0 and w in minor) else w.capitalize())
    return " ".join(out)


# ── Step 1 — GIAS Open Academies spreadsheet (xlsx, no extra deps) ───────────
XLSX_URL = (
    "https://assets.publishing.service.gov.uk/media/"
    "69dfb16f53469bbcdf408f1c/"
    "Open_academies__free_schools__studio_schools_and_UTCs__and_"
    "academy_projects_in_development_March_2026.xlsx"
)

_NOISE = re.compile(
    r"^(archive versions|for converter|sponsor|predecessor|application|"
    r"for further|n/a|\d+$|type of establishment|phase of|parliamentary|"
    r"local authority|government)",
    re.I,
)
_TRUST_KW = re.compile(
    r"trust|academies|academy trust|schools|learning|education|"
    r"foundation|federation|partnership|community",
    re.I,
)


def _parse_xlsx(raw_bytes):
    """Return dict of trust_id -> {name, ch} from the Open Academies sheet."""
    trust_data = defaultdict(list)
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
        with z.open("xl/sharedStrings.xml") as f:
            ss_xml = f.read().decode("utf-8")
        strings = re.findall(r"<t[^>]*>([^<]+)</t>", ss_xml)
        with z.open("xl/worksheets/sheet3.xml") as f:
            ws_xml = f.read().decode("utf-8")

    all_rows = re.findall(r"<row r=\"(\d+)\"[^>]*>(.*?)</row>", ws_xml, re.DOTALL)

    for row_str, row_xml in all_rows:
        if int(row_str) <= 11:
            continue

        def _cell(col, rxml=row_xml):
            m = re.search(rf"<c r=\"{col}\d+\"([^>]*)>(.*?)</c>", rxml, re.DOTALL)
            if not m:
                return ""
            attrs, content = m.groups()
            if 't="s"' in attrs or "t='s'" in attrs or 't="s"' in attrs:
                v = re.search(r"<v>(\d+)</v>", content)
                return strings[int(v.group(1))] if v else ""
            v = re.search(r"<v>([^<]+)</v>", content)
            return v.group(1) if v else ""

        trust_id = _cell("Q")
        if not re.match(r"^TR\d{5,}$", trust_id):
            continue
        trust_data[trust_id].append((_cell("M"), _cell("R")))

    out = {}
    for tid, entries in trust_data.items():
        m_cnt = Counter(
            m for m, r in entries
            if m and not _NOISE.match(m) and _TRUST_KW.search(m)
        )
        ch_cnt = Counter(r for m, r in entries if re.match(r"^\d{7,8}$", r or ""))
        best_m = m_cnt.most_common(1)[0][0] if m_cnt else ""
        best_ch = ch_cnt.most_common(1)[0][0] if ch_cnt else ""
        if best_m:
            out[tid] = {"name": best_m, "ch": best_ch}
    return out


def fetch_gias_xlsx():
    """Download the Open Academies xlsx (cached if already present) and parse it."""
    cache = os.path.join(_ROOT, "knowledge", ".tmp_academies.xlsx")
    if os.path.exists(cache):
        print(f"  Using cached xlsx at {cache}")
        with open(cache, "rb") as f:
            raw = f.read()
    else:
        print(f"  Downloading {XLSX_URL[:80]}...")
        req = urllib.request.Request(XLSX_URL, headers={"User-Agent": "PWIN/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        with open(cache, "wb") as f:
            f.write(raw)
        print(f"  Downloaded {len(raw):,} bytes")
    return _parse_xlsx(raw)


# ── Step 2 — FBIT suggest API ────────────────────────────────────────────────
_FBIT_BASE = (
    "https://financial-benchmarking-and-insights-tool.education.gov.uk"
    "/api/suggest?type=trust&search="
)
_FBIT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "X-Correlation-ID": str(uuid.uuid4()),
    "Referer": "https://financial-benchmarking-and-insights-tool.education.gov.uk/",
}


def _fbit_suggest(term, results):
    """Query FBIT and add results to the `results` dict (ch -> name)."""
    try:
        url = _FBIT_BASE + urllib.parse.quote(term)
        req = urllib.request.Request(url, headers=_FBIT_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        for item in data:
            doc = item.get("document", {})
            cn = doc.get("companyNumber", "")
            name = doc.get("trustName", "")
            if cn and name:
                results[cn] = name
    except Exception:
        pass


def fetch_fbit_trusts(db_path):
    """Query FBIT for every MAT-like buyer name in the intel database."""
    fbit = {}

    # Read buyer names from DB if it exists
    if not os.path.exists(db_path):
        print(f"  Intel DB not found at {db_path}, skipping FBIT enrichment")
        return fbit

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT b.name
        FROM notices n
        JOIN buyers b ON n.buyer_id = b.id
        LEFT JOIN canonical_buyer_aliases cba ON LOWER(b.name) = cba.alias_lower
        WHERE cba.canonical_id IS NULL
          AND (
            LOWER(b.name) LIKE '%academy%'
            OR LOWER(b.name) LIKE '%learning trust%'
            OR LOWER(b.name) LIKE '%education trust%'
            OR LOWER(b.name) LIKE '%schools trust%'
            OR LOWER(b.name) LIKE '%multi-academy%'
            OR LOWER(b.name) LIKE '%multi academy%'
          )
        ORDER BY b.name
        """
    )
    buyer_names = [r[0] for r in cur.fetchall()]
    conn.close()
    print(f"  {len(buyer_names)} MAT-like unmapped buyer names in DB")

    queried = set()
    for name in buyer_names:
        words = re.sub(r"[^a-zA-Z\s]", " ", name).split()
        term = " ".join(words[:3])[:20].strip()
        if not term or term.lower() in queried or len(term) < 3:
            continue
        queried.add(term.lower())
        _fbit_suggest(term, fbit)
        time.sleep(0.12)

    return fbit


# ── Step 3 — Merge into glossary entities ────────────────────────────────────
def build_entities(excel_trusts, fbit_trusts):
    """Merge both sources into a deduplicated entity list."""
    entities = {}  # canonical_id -> entity

    def _add(canonical_name, ch, gias_id=None, extra_aliases=None):
        cid = slugify(canonical_name)
        aliases = [canonical_name]
        uc = canonical_name.upper()
        if uc != canonical_name:
            aliases.append(uc)
        for a in (extra_aliases or []):
            if a.lower() not in {x.lower() for x in aliases}:
                aliases.append(a)

        if cid in entities:
            # Merge aliases and CH
            existing = entities[cid]
            seen = {x.lower() for x in existing["aliases"]}
            for a in aliases:
                if a.lower() not in seen:
                    existing["aliases"].append(a)
                    seen.add(a.lower())
            if ch and not existing.get("gias_ch"):
                existing["gias_ch"] = ch
        else:
            e = {
                "canonical_id": cid,
                "canonical_name": canonical_name,
                "abbreviation": None,
                "type": "Multi-academy trust",
                "subtype": "Academy trust (England)",
                "parent_ids": ["department-for-education"],
                "child_ids": [],
                "aliases": list(dict.fromkeys(aliases)),
                "status": "active",
                "source": "hand_curated_mat",
            }
            if ch:
                e["gias_ch"] = ch
            if gias_id:
                e["gias_trust_id"] = gias_id
            entities[cid] = e

    # Excel trusts (mixed-case names, best quality for canonical_name)
    for tid, info in excel_trusts.items():
        _add(info["name"], info["ch"], gias_id=tid)

    # FBIT trusts (ALL CAPS → title case)
    for ch, name in fbit_trusts.items():
        canonical = title_case_trust(name)
        _add(canonical, ch, extra_aliases=[name] if name != canonical else None)

    return sorted(entities.values(), key=lambda e: e["canonical_name"])


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Building UK multi-academy trust register...")
    print()

    print("Step 1: GIAS Open Academies spreadsheet")
    excel_trusts = fetch_gias_xlsx()
    print(f"  {len(excel_trusts)} MATs from GIAS spreadsheet")

    print()
    print("Step 2: FBIT suggest API (DB-driven queries)")
    fbit_trusts = fetch_fbit_trusts(_DB)
    print(f"  {len(fbit_trusts)} trusts from FBIT")

    print()
    print("Step 3: Building entity list")
    entities = build_entities(excel_trusts, fbit_trusts)
    print(f"  {len(entities)} unique MAT entities")

    out = {
        "_comment": (
            f"UK multi-academy trusts, built from DfE GIAS Open Academies spreadsheet "
            f"and FBIT suggest API (CH numbers verified), "
            f"generated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}. "
            "Re-run seed-mat-from-gias.py quarterly to refresh."
        ),
        "version": "1.0",
        "source": "hand_curated_mat",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "entities": entities,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(entities)} MATs to {OUT}")


if __name__ == "__main__":
    main()
