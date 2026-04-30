import sys, json, os, csv, re
sys.stdout.reconfigure(encoding='utf-8')

from rubric import SAMPLE_DEPARTMENTS, VERDICT_THRESHOLDS

FINDINGS_DIR = os.path.join(os.path.dirname(__file__), "findings")


def load_json(filename):
    with open(os.path.join(FINDINGS_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


def load_crosscheck():
    rows = []
    path = os.path.join(FINDINGS_DIR, "track1_crosscheck.csv")
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def score_coverage(parsed, dept_info):
    """Return (named_staff, expected_approx, coverage_pct_or_None)."""
    named = parsed.get("named_staff", 0)
    total_rows = parsed.get("total_rows", 0)
    expected = dept_info.get("expected_scs_approx")
    coverage_of_expected = round(named / expected * 100, 1) if expected else None
    naming_rate = round(named / total_rows * 100, 1) if total_rows else None
    return named, total_rows, expected, coverage_of_expected, naming_rate


def _date_from_url(url):
    """Extract the snapshot date embedded in the data.gov.uk resource URL.

    URLs follow the pattern: .../<upload-timestamp>-<YYYY-MM-DD>-organogram-senior.csv
    e.g. 2026-01-15T16-07-06Z-2025-12-31-organogram-senior.csv
    """
    if not url:
        return None
    # Find the last YYYY-MM-DD before '-organogram'
    match = re.search(r'(\d{4}-\d{2}-\d{2})-organogram', url)
    return match.group(1) if match else None


def score_consistency(parsed_results):
    """Count distinct column-set fingerprints across departments."""
    fingerprints = set()
    for dept_id, p in parsed_results.items():
        if p.get("status") != "parsed":
            continue
        cols = tuple(sorted(p.get("columns_found", [])))
        fingerprints.add(cols)
    return len(fingerprints)


def score_currency(sources, parsed_results):
    """Return the maximum publication lag in days across current (non-absent) departments."""
    from datetime import datetime
    max_lag = None
    lag_details = {}
    today = datetime.today()
    for dept_id, s in sources.items():
        if not parsed_results.get(dept_id, {}).get("status") == "parsed":
            continue
        # Try resource_last_modified first, fall back to date embedded in resource URL
        date_str = s.get("resource_last_modified")
        if date_str:
            date_str = date_str.split("T")[0]
        else:
            date_str = _date_from_url(s.get("resource_url"))
        if not date_str:
            lag_details[dept_id] = {"date_source": "none", "lag_days": None}
            continue
        try:
            dt = datetime.fromisoformat(date_str)
            lag = (today - dt).days
            lag_details[dept_id] = {
                "date_source": "resource_last_modified" if s.get("resource_last_modified") else "url_embedded",
                "snapshot_date": date_str,
                "lag_days": lag,
            }
            if max_lag is None or lag > max_lag:
                max_lag = lag
        except Exception:
            lag_details[dept_id] = {"date_source": "parse_error", "lag_days": None}
    return max_lag, lag_details


def verdict_for_score(criterion, value):
    thresholds = VERDICT_THRESHOLDS[criterion]
    if criterion == "senior_coverage_pct":
        if value >= thresholds["build_as_scoped"]:
            return "build_as_scoped"
        elif value >= thresholds["build_narrower"]:
            return "build_narrower"
        return "dont_build"
    elif criterion == "max_currency_lag_days":
        if value <= thresholds["build_as_scoped"]:
            return "build_as_scoped"
        elif value <= thresholds["build_narrower"]:
            return "build_narrower"
        return "dont_build"
    elif criterion == "distinct_formats":
        if value <= thresholds["build_as_scoped"]:
            return "build_as_scoped"
        elif value <= thresholds["build_narrower"]:
            return "build_narrower"
        return "dont_build"
    return "unknown"


def run():
    sources = load_json("track1_sources.json")
    parsed = load_json("track1_parsed.json")
    crosscheck = load_crosscheck()

    # --- Coverage ---
    coverage_per_dept = {}
    naming_rates = []
    for dept_id, dept_info in SAMPLE_DEPARTMENTS.items():
        p = parsed.get(dept_id, {})
        if p.get("status") != "parsed":
            coverage_per_dept[dept_id] = {
                "status": p.get("status", "absent"),
                "named": 0,
                "total_rows": 0,
                "expected_scs_approx": dept_info.get("expected_scs_approx"),
                "coverage_of_expected_pct": None,
                "naming_rate_pct": None,
            }
            continue
        named, total_rows, expected, cov_pct, naming_rate = score_coverage(p, dept_info)
        # Skip NHSE from central-gov coverage calculation (2016 data)
        entry = {
            "status": "parsed",
            "named": named,
            "total_rows": total_rows,
            "expected_scs_approx": expected,
            "coverage_of_expected_pct": cov_pct,
            "naming_rate_pct": naming_rate,
            "notes": p.get("parse_notes", []),
        }
        if dept_id != "nhse" and expected:
            entry["verdict"] = verdict_for_score("senior_coverage_pct", cov_pct)
            naming_rates.append(naming_rate)
        coverage_per_dept[dept_id] = entry

    # Average naming rate across current central gov departments
    central_gov_naming_rate = (
        round(sum(naming_rates) / len(naming_rates), 1) if naming_rates else None
    )

    # --- Currency ---
    max_lag, lag_details = score_currency(sources, parsed)

    # --- Format consistency ---
    distinct_formats = score_consistency(parsed)

    # --- Cross-check churn signal ---
    total_checked = len(crosscheck)
    still_in_post = sum(1 for r in crosscheck if r.get("still_in_post", "").lower() == "yes")
    moved_on = sum(1 for r in crosscheck if r.get("still_in_post", "").lower() == "no")
    unknown = total_checked - still_in_post - moved_on

    summary = {
        "coverage": {
            "per_department": coverage_per_dept,
            "avg_central_gov_naming_rate_pct": central_gov_naming_rate,
            "note": (
                "naming_rate_pct = named staff / total SCS posts in organogram. "
                "Only ~20-27% of SCS posts are named; the rest are redacted under Cabinet Office disclosure policy. "
                "Named posts are primarily Director (SCS2) and above. "
                "Deputy Director and Grade 6 commercial leads (SCS1) are largely redacted."
            ),
            "verdict": verdict_for_score("senior_coverage_pct", central_gov_naming_rate) if central_gov_naming_rate else "insufficient_data",
        },
        "currency": {
            "per_department": lag_details,
            "max_publication_lag_days": max_lag,
            "verdict": verdict_for_score("max_currency_lag_days", max_lag) if max_lag else "insufficient_data",
        },
        "consistency": {
            "distinct_column_fingerprints": distinct_formats,
            "note": "All three current central gov departments share the same column set. NHSE 2016 file differs (no Office Region column). Effective distinct_formats for current data = 1.",
            "verdict": verdict_for_score("distinct_formats", distinct_formats),
        },
        "crosscheck_churn": {
            "individuals_checked": total_checked,
            "still_in_post": still_in_post,
            "moved_on": moved_on,
            "unknown": unknown,
            "churn_pct": round(moved_on / total_checked * 100, 1) if total_checked else None,
            "note": (
                "3 HMT Director General-level individuals confirmed still in post from Dec 2025 organogram. "
                "MoD and DfE governance pages name no individuals below DG level. "
                "GOV.UK governance pages only useful for top ~10-15 people per department (DG and above). "
                "16 of 19 checked are 'unknown' — not moved on, but unverifiable from public governance pages alone."
            ),
        },
    }

    out_path = os.path.join(FINDINGS_DIR, "track1_verdict_scores.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    run()
