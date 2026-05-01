# pwin-competitive-intel/scripts/investigation/parse_organograms.py
import sys, json, os, csv, io, random
sys.stdout.reconfigure(encoding='utf-8')

from rubric import SAMPLE_DEPARTMENTS, STANDARD_ORGANOGRAM_COLUMNS

FINDINGS_DIR = os.path.join(os.path.dirname(__file__), "findings")
RAW_DIR = os.path.join(FINDINGS_DIR, "raw_organograms")


def try_decode(raw_bytes):
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw_bytes.decode(enc), enc
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode CSV with any known encoding")


def parse_senior_staff_csv(path):
    with open(path, "rb") as f:
        raw = f.read()

    text, encoding_used = try_decode(raw)
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    columns_found = list(reader.fieldnames or [])

    # Named staff: has a non-empty Name that isn't a redaction placeholder
    REDACTION_MARKERS = {"N/D", "ND", "REDACTED", "WITHHELD", "N/A", "-", ""}
    named = [
        r for r in rows
        if r.get("Name", "").strip().upper() not in REDACTION_MARKERS
    ]

    by_grade = {}
    for r in named:
        grade = r.get("Grade", "Unknown").strip()
        by_grade[grade] = by_grade.get(grade, 0) + 1

    # Field completeness as % of named rows that have the field populated
    completeness = {}
    for col in STANDARD_ORGANOGRAM_COLUMNS:
        if col in columns_found:
            populated = sum(1 for r in named if r.get(col, "").strip())
            completeness[col] = round(populated / len(named) * 100, 1) if named else 0.0
        else:
            completeness[col] = None  # column absent entirely

    # Random sample of 5 for manual cross-check
    sample = random.sample(named, min(5, len(named)))
    sample_out = [
        {
            "name": r.get("Name", "").strip(),
            "grade": r.get("Grade", "").strip(),
            "job_title": r.get("Job Title", "").strip(),
            "unit": r.get("Unit", "").strip(),
            "organisation": r.get("Organisation", "").strip(),
            "reports_to": r.get("Reports To Senior Post", "").strip(),
        }
        for r in sample
    ]

    missing_standard_cols = [c for c in STANDARD_ORGANOGRAM_COLUMNS if c not in columns_found]
    extra_cols = [c for c in columns_found if c not in STANDARD_ORGANOGRAM_COLUMNS]

    return {
        "encoding_used": encoding_used,
        "total_rows": len(rows),
        "named_staff": len(named),
        "redacted_or_blank": len(rows) - len(named),
        "by_grade": by_grade,
        "columns_found": columns_found,
        "missing_standard_columns": missing_standard_cols,
        "extra_columns": extra_cols,
        "field_completeness_pct": completeness,
        "sample_5": sample_out,
        "parse_notes": [],
    }


def run():
    sources_path = os.path.join(FINDINGS_DIR, "track1_sources.json")
    with open(sources_path, encoding="utf-8") as f:
        sources = json.load(f)

    results = {}
    for dept_id, source in sources.items():
        print(f"\n--- {source['name']} ---")
        if not source.get("download_ok") or not source.get("local_path"):
            print(f"  Skipping (no local CSV): {source.get('absence_note', 'unknown reason')}")
            results[dept_id] = {
                "name": source["name"],
                "status": "absent",
                "absence_note": source.get("absence_note"),
            }
            continue

        path = source["local_path"]
        if not os.path.exists(path):
            print(f"  File not found at {path}")
            results[dept_id] = {
                "name": source["name"],
                "status": "file_missing",
                "absence_note": f"Expected file not found: {path}",
            }
            continue

        try:
            parsed = parse_senior_staff_csv(path)
            parsed["name"] = source["name"]
            parsed["status"] = "parsed"
            parsed["source_url"] = source.get("resource_url")
            parsed["resource_last_modified"] = source.get("resource_last_modified")
            results[dept_id] = parsed
            print(f"  Named staff: {parsed['named_staff']} (redacted/blank: {parsed['redacted_or_blank']})")
            print(f"  Grades found: {list(parsed['by_grade'].keys())}")
            print(f"  Missing standard columns: {parsed['missing_standard_columns']}")
            print(f"  Encoding: {parsed['encoding_used']}")
        except Exception as e:
            print(f"  PARSE ERROR: {e}")
            results[dept_id] = {
                "name": source["name"],
                "status": "parse_error",
                "absence_note": str(e),
            }

    out_path = os.path.join(FINDINGS_DIR, "track1_parsed.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved parsed findings to {out_path}")
    parsed_ok = sum(1 for v in results.values() if v.get("status") == "parsed")
    print(f"Successfully parsed: {parsed_ok}/{len(results)}")


if __name__ == "__main__":
    run()
