# Stakeholder Database Feasibility Investigation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a 2–3 day three-track investigation to decide whether to build the stakeholder canonical layer — verdict is "build as scoped", "build narrower", or "don't build".

**Architecture:** Three parallel tracks — (1) live ingest test of five sample departments' organogram CSVs, (2) spot-check of ~10 alternative sources scored on a rubric, (3) local government reality check. All findings feed a single feasibility report. No database schema or MCP tools are built — this investigation sizes the work.

**Tech Stack:** Python 3.9+ stdlib only (urllib, csv, json, sqlite3). All scripts in `pwin-competitive-intel/scripts/investigation/`. Findings land in `pwin-competitive-intel/scripts/investigation/findings/`. Final report at `docs/research/2026-04-30-stakeholder-database-feasibility.md`.

---

## Task 1: Scaffold — rubric, findings directory, output structure

**Files:**
- Create: `pwin-competitive-intel/scripts/investigation/rubric.py`
- Create: `pwin-competitive-intel/scripts/investigation/findings/` (directory, kept via `.gitkeep`)

- [ ] **Step 1: Create the investigation directory**

```bash
mkdir -p pwin-competitive-intel/scripts/investigation/findings
touch pwin-competitive-intel/scripts/investigation/findings/.gitkeep
touch pwin-competitive-intel/scripts/investigation/__init__.py
```

- [ ] **Step 2: Write `rubric.py` — defines what we are measuring before we look at any data**

```python
# pwin-competitive-intel/scripts/investigation/rubric.py
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Five departments sampled to span the expected quality spread
SAMPLE_DEPARTMENTS = {
    "hmt": {
        "name": "HM Treasury",
        "data_gov_uk_query": "HM Treasury organogram senior staff salaries",
        "gov_uk_people_url": "https://www.gov.uk/government/organisations/hm-treasury/about/our-governance",
        "expected_scs_approx": 60,   # approximate SCS headcount from Cabinet Office stats
        "notes": "Small, central, organisationally tidy. Best-case baseline.",
    },
    "mod": {
        "name": "Ministry of Defence",
        "data_gov_uk_query": "Ministry of Defence organogram senior staff salaries",
        "gov_uk_people_url": "https://www.gov.uk/government/organisations/ministry-of-defence/about/our-governance",
        "expected_scs_approx": 500,
        "notes": "Large, complex, multiple agencies. Worst-case central government.",
    },
    "dfe": {
        "name": "Department for Education",
        "data_gov_uk_query": "Department for Education organogram senior staff salaries",
        "gov_uk_people_url": "https://www.gov.uk/government/organisations/department-for-education/about/our-governance",
        "expected_scs_approx": 200,
        "notes": "Middle-of-the-road; known sub-org dark spot in FTS data.",
    },
    "nhse": {
        "name": "NHS England",
        "data_gov_uk_query": "NHS England organogram senior staff",
        "gov_uk_people_url": "https://www.england.nhs.uk/about/our-people/nhs-england-executive/",
        "expected_scs_approx": None,   # different regime — ODS not Cabinet Office stats
        "notes": "Different publishing regime. Tests generalisation beyond Whitehall.",
    },
    "bcc": {
        "name": "Birmingham City Council",
        "data_gov_uk_query": "Birmingham City Council organogram senior staff",
        "gov_uk_people_url": "https://www.birmingham.gov.uk/about-the-council",
        "expected_scs_approx": None,   # no organogram requirement for local gov
        "notes": "No organogram regime. Tests what local government data exists.",
    },
}

# Standard columns in the Cabinet Office organogram CSV format (since ~2011)
STANDARD_ORGANOGRAM_COLUMNS = [
    "Post Unique Reference",
    "Name",
    "Grade",
    "Job Title",
    "Parent Department",
    "Organisation",
    "Unit",
    "Contact Phone",
    "Contact Email",
    "Reports To Senior Post",
    "Salary Cost of Reports",
    "FTE",
    "Actual Pay Floor",
    "Actual Pay Ceiling",
    "Professional/Occupational Group",
    "Notes",
    "Valid?",
]

# Thresholds for the four verdict criteria
VERDICT_THRESHOLDS = {
    "senior_coverage_pct": {
        "build_as_scoped": 90,
        "build_narrower":  70,
        # below 70 for central gov -> don't build
    },
    "evaluator_source_buyer_pct": {
        # fraction of sampled departments with >= 1 useful evaluator-level source
        "build_as_scoped": 70,
        "build_narrower":  0,   # central gov only is acceptable
    },
    "max_currency_lag_days": {
        "build_as_scoped": 180,
        "build_narrower":  365,
        # above 365 even for central gov -> don't build
    },
    "distinct_formats": {
        "build_as_scoped": 2,
        "build_narrower":  5,
        # above 5 -> don't build
    },
}

# Alternative sources to score in Track 2
ALTERNATIVE_SOURCES = [
    {
        "id": "gov_uk_people",
        "name": "GOV.UK People pages",
        "url_pattern": "https://www.gov.uk/government/organisations/{dept}/about/our-governance",
        "test": "Pull 3 departments, compare named SCS to organogram count",
        "automated": False,
    },
    {
        "id": "gov_uk_appointments_rss",
        "name": "GOV.UK appointments RSS",
        "url_pattern": "https://www.gov.uk/government/announcements.atom?announcement_filter_option=appointments",
        "test": "Download feed, count usable appointment signals in last 30 days",
        "automated": True,
    },
    {
        "id": "companies_house",
        "name": "Companies House — ALB officers",
        "url_pattern": "https://api.company-information.service.gov.uk/company/{company_number}/officers",
        "test": "Pick 3 ALBs (UKHSA, Homes England, UKRI), check officer filings",
        "automated": True,
    },
    {
        "id": "nao_reports",
        "name": "NAO published reports",
        "url_pattern": "https://www.nao.org.uk/reports/",
        "test": "Sample 3 recent VFM reports, extract named SROs and accountable officers",
        "automated": False,
    },
    {
        "id": "pac_witnesses",
        "name": "Public Accounts Committee witness lists",
        "url_pattern": "https://committees.parliament.uk/committee/127/public-accounts-committee/",
        "test": "Last 12 months of sessions — count distinct named officials by department",
        "automated": False,
    },
    {
        "id": "civil_service_jobs",
        "name": "Civil Service Jobs vacancies",
        "url_pattern": "https://www.civilservicejobs.service.gov.uk/",
        "test": "Sample one week of vacancies at Grade 7 and above — count named hiring units",
        "automated": False,
    },
    {
        "id": "linkedin_manual",
        "name": "LinkedIn (manual search)",
        "url_pattern": "https://www.linkedin.com/search/results/people/",
        "test": "Search 3 departments for Grade 7 commercial leads with public profiles; count and assess profile completeness",
        "automated": False,
    },
    {
        "id": "trade_press",
        "name": "Trade press (Civil Service World, Computer Weekly, Public Sector Executive)",
        "url_pattern": "https://www.civilserviceworld.com/",
        "test": "Last 30 days — count usable named-official mentions with role and unit",
        "automated": False,
    },
    {
        "id": "fts_contact_names",
        "name": "Procurement notice contacts in bid_intel.db",
        "url_pattern": None,
        "test": "SQL query against notices table — fraction with named contact, fraction where name looks like a real person not a team inbox",
        "automated": True,
    },
    {
        "id": "dods_people",
        "name": "Dods People (paid commercial product)",
        "url_pattern": "https://dodsgroup.com/products/dods-people/",
        "test": "Desk-only — check pricing, coverage claim, and free trial availability",
        "automated": False,
    },
]

# Score template written to findings/track2_sources.json for each source
SOURCE_SCORE_TEMPLATE = {
    "id": "",
    "name": "",
    "coverage_note": "",       # what fraction of the expected population is named
    "currency_note": "",       # how fresh; how often updated
    "structure": "",           # "structured", "semi-structured", "unstructured"
    "licence": "",             # "OGL", "public-domain", "paid", "scrape-required", "ToS-restricted"
    "useful_for_senior_tier": None,   # bool
    "useful_for_evaluator_tier": None,  # bool
    "notes": "",
}
```

- [ ] **Step 3: Commit the scaffold**

```bash
cd pwin-competitive-intel
git add scripts/investigation/
git commit -m "feat(investigation): scaffold rubric and findings directory for stakeholder feasibility"
```

---

## Task 2: Locate organogram URLs and download raw CSVs

**Files:**
- Create: `pwin-competitive-intel/scripts/investigation/fetch_organograms.py`
- Create: `pwin-competitive-intel/scripts/investigation/findings/track1_sources.json`

This task finds the correct download URL for each department's senior-staff organogram CSV, downloads it, and saves the raw CSV locally. It uses the data.gov.uk CKAN API to search, then downloads the most recent senior-staff resource.

- [ ] **Step 1: Write `fetch_organograms.py`**

```python
# pwin-competitive-intel/scripts/investigation/fetch_organograms.py
import sys, json, os, urllib.request, urllib.parse, time
sys.stdout.reconfigure(encoding='utf-8')

from rubric import SAMPLE_DEPARTMENTS

FINDINGS_DIR = os.path.join(os.path.dirname(__file__), "findings")
DATA_GOV_UK_API = "https://data.gov.uk/api/3/action/package_search"
RAW_DIR = os.path.join(FINDINGS_DIR, "raw_organograms")
os.makedirs(RAW_DIR, exist_ok=True)


def search_data_gov_uk(query, rows=10):
    params = urllib.parse.urlencode({"q": query, "sort": "metadata_modified desc", "rows": rows})
    url = f"{DATA_GOV_UK_API}?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def find_senior_staff_resource(package):
    """Return the most recent senior-staff CSV resource from a data.gov.uk package."""
    resources = package.get("resources", [])
    candidates = [
        r for r in resources
        if "senior" in r.get("name", "").lower()
        or "senior" in r.get("url", "").lower()
    ]
    if not candidates:
        # Fall back: any CSV that isn't "junior"
        candidates = [
            r for r in resources
            if r.get("format", "").upper() in ("CSV", "")
            and "junior" not in r.get("name", "").lower()
        ]
    if not candidates:
        return None
    # Prefer most recently modified
    candidates.sort(key=lambda r: r.get("last_modified") or r.get("created") or "", reverse=True)
    return candidates[0]


def download_resource(resource, dest_path):
    url = resource["url"]
    print(f"  Downloading: {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            content = resp.read()
        with open(dest_path, "wb") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def run():
    results = {}
    for dept_id, dept in SAMPLE_DEPARTMENTS.items():
        print(f"\n--- {dept['name']} ---")
        entry = {
            "dept_id": dept_id,
            "name": dept["name"],
            "query_used": dept["data_gov_uk_query"],
            "dataset_found": None,
            "dataset_url": None,
            "resource_name": None,
            "resource_url": None,
            "resource_format": None,
            "resource_last_modified": None,
            "local_path": None,
            "download_ok": False,
            "absence_note": None,
        }

        try:
            result = search_data_gov_uk(dept["data_gov_uk_query"])
        except Exception as e:
            entry["absence_note"] = f"data.gov.uk API error: {e}"
            results[dept_id] = entry
            continue

        packages = result.get("result", {}).get("results", [])
        if not packages:
            entry["absence_note"] = "No dataset found on data.gov.uk for this query"
            print(f"  No dataset found")
            results[dept_id] = entry
            continue

        # Take the top result
        pkg = packages[0]
        entry["dataset_found"] = pkg.get("title")
        entry["dataset_url"] = f"https://data.gov.uk/dataset/{pkg.get('name')}"
        print(f"  Dataset: {entry['dataset_found']}")
        print(f"  URL: {entry['dataset_url']}")

        resource = find_senior_staff_resource(pkg)
        if not resource:
            entry["absence_note"] = "Dataset found but no senior-staff CSV resource identified"
            print(f"  No senior-staff resource found in dataset")
            results[dept_id] = entry
            continue

        entry["resource_name"] = resource.get("name")
        entry["resource_url"] = resource.get("url")
        entry["resource_format"] = resource.get("format")
        entry["resource_last_modified"] = resource.get("last_modified")
        print(f"  Resource: {entry['resource_name']} ({entry['resource_format']})")
        print(f"  Last modified: {entry['resource_last_modified']}")

        dest = os.path.join(RAW_DIR, f"{dept_id}_senior_staff.csv")
        ok = download_resource(resource, dest)
        if ok:
            entry["local_path"] = dest
            entry["download_ok"] = True
        else:
            entry["absence_note"] = "Download failed — check URL manually"

        results[dept_id] = entry
        time.sleep(1)  # polite delay

    out_path = os.path.join(FINDINGS_DIR, "track1_sources.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved source inventory to {out_path}")
    downloaded = sum(1 for e in results.values() if e["download_ok"])
    print(f"Downloaded: {downloaded}/{len(results)} departments")


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: Run the fetcher**

```bash
cd pwin-competitive-intel/scripts/investigation
python fetch_organograms.py
```

Expected output: a summary showing how many of the five departments returned a dataset and a downloadable CSV. At minimum HM Treasury, MoD, and DfE should succeed. NHS England and Birmingham City Council may return "no dataset found" — this is expected and is itself a finding.

Check `findings/track1_sources.json` is written and `findings/raw_organograms/` contains at least 3 CSVs.

- [ ] **Step 3: For any department where the automated search failed, do a manual lookup**

Open `https://www.data.gov.uk/search?q=organogram+senior+{department}` in a browser. If a dataset is found, download the most recent senior-staff CSV manually and save to `findings/raw_organograms/{dept_id}_senior_staff.csv`. Update `track1_sources.json` with the manual URL and set `"download_ok": true`.

If no data exists at all (expected for Birmingham, likely for NHS England), record this in `track1_sources.json` under `"absence_note"` — e.g. `"No organogram publishing requirement for local authorities"`.

- [ ] **Step 4: Commit raw organograms and source inventory**

```bash
cd pwin-competitive-intel
# Raw CSVs are data — add them so findings are reproducible
git add scripts/investigation/fetch_organograms.py
git add scripts/investigation/findings/track1_sources.json
git add scripts/investigation/findings/raw_organograms/
git commit -m "feat(investigation): fetch organogram CSVs for 5 sample departments"
```

---

## Task 3: Parse and characterise organogram CSVs

**Files:**
- Create: `pwin-competitive-intel/scripts/investigation/parse_organograms.py`
- Create: `pwin-competitive-intel/scripts/investigation/findings/track1_parsed.json`

- [ ] **Step 1: Write `parse_organograms.py`**

```python
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
```

- [ ] **Step 2: Run the parser**

```bash
cd pwin-competitive-intel/scripts/investigation
python parse_organograms.py
```

Expected output: for each department that has a CSV, a count of named staff, grade breakdown, list of any missing columns, and the encoding used. If MoD or DfE shows more than 2 distinct formats or missing standard columns, note it in `track1_parsed.json` under `"parse_notes"` manually before moving on.

- [ ] **Step 3: Spot-check the output**

Open `findings/track1_parsed.json`. For each parsed department, verify:
- `named_staff` is plausible (HM Treasury ~40–80, MoD ~300–600, DfE ~100–250)
- `by_grade` shows SCS bands (look for strings containing "SCS", "Director", "Grade 6", or "Deputy Director")
- `field_completeness_pct` for `"Reports To Senior Post"` is present and > 50% — this is the reporting-line field needed for the org chart
- `sample_5` contains real-looking names (not all redacted)

If `named_staff` is unexpectedly low (< 20 for any central government department), check whether the wrong resource was downloaded (might have got the junior-staff CSV instead).

- [ ] **Step 4: Commit**

```bash
cd pwin-competitive-intel
git add scripts/investigation/parse_organograms.py scripts/investigation/findings/track1_parsed.json
git commit -m "feat(investigation): parse organogram CSVs — named staff counts and field completeness"
```

---

## Task 4: Manual cross-check of sampled individuals

**Files:**
- Create: `pwin-competitive-intel/scripts/investigation/findings/track1_crosscheck.csv`

This is a manual step. For each parsed department, `track1_parsed.json` contains a `sample_5` list. For each named individual, look them up on at least one external source and record whether they are still in the same role.

- [ ] **Step 1: Create the cross-check CSV template**

Create `findings/track1_crosscheck.csv` with this header row and fill in one row per individual:

```
dept_id,dept_name,name_in_organogram,grade_in_organogram,job_title_in_organogram,unit_in_organogram,source_checked,source_url,current_role_matches,current_unit_matches,still_in_post,notes
```

Example row (fill in after each lookup):
```
hmt,HM Treasury,Jane Smith,SCS2,Director General Economic Affairs,Fiscal Group,GOV.UK People page,https://www.gov.uk/government/organisations/hm-treasury/about/our-governance,yes,yes,yes,Listed as DG Economic Affairs on the page
```

- [ ] **Step 2: Perform the lookups — 5 individuals × up to 5 departments = up to 25 lookups**

For each individual in `sample_5`:

1. **First try GOV.UK People page** for the department (URL is in `SAMPLE_DEPARTMENTS[dept_id]["gov_uk_people_url"]`). Search for the name on that page.
2. **If not found there, try LinkedIn** — search for `"{name}" site:linkedin.com/in` in a browser, look at the current role.
3. **If not found there, try a Google search** for `"{name}" "{department name}" site:gov.uk`.

Record result in the CSV. Use `"still_in_post"` = `yes` / `no` / `unknown`.

The currency finding from this step: if the organogram's `resource_last_modified` date is X months ago and `N` out of the 5 sampled individuals have moved on, that gives a rough churn signal. Record as a note in `track1_crosscheck.csv`.

- [ ] **Step 3: Commit the cross-check**

```bash
cd pwin-competitive-intel
git add scripts/investigation/findings/track1_crosscheck.csv
git commit -m "feat(investigation): manual cross-check of sampled organogram individuals against external sources"
```

---

## Task 5: Score Track 1 against verdict criteria

**Files:**
- Create: `pwin-competitive-intel/scripts/investigation/score_track1.py`
- Create: `pwin-competitive-intel/scripts/investigation/findings/track1_verdict_scores.json`

- [ ] **Step 1: Write `score_track1.py`**

```python
# pwin-competitive-intel/scripts/investigation/score_track1.py
import sys, json, os, csv
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
    expected = dept_info.get("expected_scs_approx")
    if expected:
        return named, expected, round(named / expected * 100, 1)
    return named, None, None


def score_consistency(parsed_results):
    """Count distinct column-set fingerprints across departments."""
    fingerprints = set()
    for dept_id, p in parsed_results.items():
        if p.get("status") != "parsed":
            continue
        cols = tuple(sorted(p.get("columns_found", [])))
        fingerprints.add(cols)
    return len(fingerprints)


def score_currency(sources):
    """Return the maximum publication lag in days across departments."""
    from datetime import datetime
    max_lag = None
    for dept_id, s in sources.items():
        modified = s.get("resource_last_modified")
        if not modified:
            continue
        try:
            # data.gov.uk returns ISO format e.g. "2024-10-15T00:00:00"
            dt = datetime.fromisoformat(modified.split("T")[0])
            today = datetime.today()
            lag = (today - dt).days
            if max_lag is None or lag > max_lag:
                max_lag = lag
        except Exception:
            pass
    return max_lag


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

    scores = {}

    # Coverage per department
    coverage_scores = []
    for dept_id, dept_info in SAMPLE_DEPARTMENTS.items():
        p = parsed.get(dept_id, {})
        if p.get("status") != "parsed":
            scores[dept_id] = {"coverage": "absent", "named": 0, "expected": dept_info.get("expected_scs_approx")}
            continue
        named, expected, pct = score_coverage(p, dept_info)
        entry = {"named": named, "expected": expected, "coverage_pct": pct}
        if pct is not None:
            entry["verdict"] = verdict_for_score("senior_coverage_pct", pct)
            coverage_scores.append(pct)
        scores[dept_id] = entry

    avg_central_gov_coverage = (
        sum(coverage_scores) / len(coverage_scores) if coverage_scores else None
    )

    # Currency lag
    max_lag = score_currency(sources)

    # Format consistency
    distinct_formats = score_consistency(parsed)

    # Cross-check churn signal
    total_checked = len(crosscheck)
    still_in_post = sum(1 for r in crosscheck if r.get("still_in_post", "").lower() == "yes")
    moved_on = sum(1 for r in crosscheck if r.get("still_in_post", "").lower() == "no")

    summary = {
        "coverage": {
            "per_department": scores,
            "avg_central_gov_coverage_pct": avg_central_gov_coverage,
            "verdict": verdict_for_score("senior_coverage_pct", avg_central_gov_coverage) if avg_central_gov_coverage else "insufficient_data",
        },
        "currency": {
            "max_publication_lag_days": max_lag,
            "verdict": verdict_for_score("max_currency_lag_days", max_lag) if max_lag else "insufficient_data",
        },
        "consistency": {
            "distinct_column_fingerprints": distinct_formats,
            "verdict": verdict_for_score("distinct_formats", distinct_formats),
        },
        "crosscheck_churn": {
            "individuals_checked": total_checked,
            "still_in_post": still_in_post,
            "moved_on": moved_on,
            "unknown": total_checked - still_in_post - moved_on,
            "churn_pct": round(moved_on / total_checked * 100, 1) if total_checked else None,
        },
    }

    out_path = os.path.join(FINDINGS_DIR, "track1_verdict_scores.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: Run the scorer**

```bash
cd pwin-competitive-intel/scripts/investigation
python score_track1.py
```

Expected: a JSON summary printed to stdout and saved to `findings/track1_verdict_scores.json`. Each criterion shows its measured value and a per-criterion verdict (`build_as_scoped` / `build_narrower` / `dont_build` / `insufficient_data`).

- [ ] **Step 3: Read the early-stop signal**

Per the spec: if all five sample departments parse cleanly with ≥ 90% senior coverage and ≤ 2 distinct formats, the Track 1 verdict is `build_as_scoped` — you can stop and move directly to Task 8 (write the report). If all five fail or are absent, stop and move directly to Task 8 with a `dont_build` verdict. Otherwise continue to Tasks 6 and 7.

- [ ] **Step 4: Commit**

```bash
cd pwin-competitive-intel
git add scripts/investigation/score_track1.py scripts/investigation/findings/track1_verdict_scores.json
git commit -m "feat(investigation): score Track 1 organogram findings against verdict criteria"
```

---

## Task 6: Automated Track 2 sources

**Files:**
- Create: `pwin-competitive-intel/scripts/investigation/probe_alt_sources.py`
- Create: `pwin-competitive-intel/scripts/investigation/findings/track2_automated.json`

Three sources can be probed programmatically: GOV.UK appointments RSS, Companies House ALB officers, and FTS procurement contact names.

- [ ] **Step 1: Write `probe_alt_sources.py`**

```python
# pwin-competitive-intel/scripts/investigation/probe_alt_sources.py
import sys, json, os, urllib.request, csv, sqlite3, time, re
from datetime import datetime, timedelta
sys.stdout.reconfigure(encoding='utf-8')

FINDINGS_DIR = os.path.join(os.path.dirname(__file__), "findings")

# --- GOV.UK Appointments RSS ---

def probe_govuk_appointments_rss():
    url = "https://www.gov.uk/government/announcements.atom?announcement_filter_option=appointments"
    print("Probing GOV.UK appointments RSS...")
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            content = resp.read().decode("utf-8")
    except Exception as e:
        return {"error": str(e)}

    # Count entries in the last 30 days
    from xml.etree import ElementTree as ET
    root = ET.fromstring(content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)
    cutoff = datetime.utcnow() - timedelta(days=30)
    recent = []
    for entry in entries:
        updated = entry.findtext("atom:updated", namespaces=ns) or ""
        try:
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            dt = None
        title = entry.findtext("atom:title", namespaces=ns) or ""
        if dt and dt >= cutoff:
            recent.append({"title": title, "updated": updated})

    return {
        "total_entries_in_feed": len(entries),
        "entries_last_30_days": len(recent),
        "sample_3": recent[:3],
        "notes": "Each entry is an appointment announcement. Check whether they name the individual and give role+department.",
    }


# --- Companies House ALB officers ---

def probe_companies_house_alb_officers():
    # Three ALBs with known Companies House numbers:
    # UKHSA: 12886087, Homes England: 09231073, UKRI: 10612548
    albs = [
        {"name": "UK Health Security Agency", "company_number": "12886087"},
        {"name": "Homes England", "company_number": "09231073"},
        {"name": "UK Research and Innovation", "company_number": "10612548"},
    ]
    results = []
    for alb in albs:
        print(f"  Probing Companies House for {alb['name']}...")
        url = f"https://api.company-information.service.gov.uk/company/{alb['company_number']}/officers?items_per_page=10"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PWIN-Investigation/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            results.append({"name": alb["name"], "error": str(e)})
            time.sleep(0.6)
            continue

        officers = data.get("items", [])
        active = [o for o in officers if not o.get("resigned_on")]
        results.append({
            "name": alb["name"],
            "company_number": alb["company_number"],
            "total_officers": data.get("total_results", 0),
            "active_officers": len(active),
            "sample_3": [
                {
                    "name": o.get("name"),
                    "role": o.get("officer_role"),
                    "appointed_on": o.get("appointed_on"),
                }
                for o in active[:3]
            ],
        })
        time.sleep(0.6)

    return results


# --- FTS procurement contact names ---

def probe_fts_contact_names():
    db_candidates = [
        os.path.join(os.path.dirname(__file__), "../../../db/bid_intel.db"),  # pwin-competitive-intel/db/bid_intel.db
        os.path.join(os.path.dirname(__file__), "../../../../pwin-competitive-intel/db/bid_intel.db"),
    ]
    db_path = None
    for p in db_candidates:
        if os.path.exists(p):
            db_path = p
            break

    if not db_path:
        return {"error": "bid_intel.db not found — check path", "candidates_tried": db_candidates}

    print(f"  Querying bid_intel.db at {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # First check what contact-related columns exist on the notices table
    cur.execute("PRAGMA table_info(notices)")
    cols = [row[1] for row in cur.fetchall()]
    contact_cols = [c for c in cols if "contact" in c.lower()]

    if not contact_cols:
        conn.close()
        return {"error": "No contact columns found on notices table", "columns_available": cols}

    # Use the first contact name column found
    contact_col = contact_cols[0]
    print(f"  Using contact column: {contact_col}")

    # What fraction of recent notices have a named contact?
    cur.execute(f"""
        SELECT
            COUNT(*) as total_recent,
            SUM(CASE WHEN {contact_col} IS NOT NULL AND TRIM({contact_col}) != '' THEN 1 ELSE 0 END) as has_contact,
            SUM(CASE WHEN {contact_col} IS NOT NULL
                      AND TRIM({contact_col}) != ''
                      AND {contact_col} NOT LIKE '%@%'
                      AND LENGTH(TRIM({contact_col})) > 5
                 THEN 1 ELSE 0 END) as looks_like_person_name
        FROM notices
        WHERE published_date >= date('now', '-12 months')
    """)
    row = cur.fetchone()
    total, has_contact, looks_like_person = row

    # Sample of plausible person names
    cur.execute(f"""
        SELECT {contact_col}, COUNT(*) as n
        FROM notices
        WHERE published_date >= date('now', '-12 months')
          AND {contact_col} IS NOT NULL
          AND TRIM({contact_col}) != ''
          AND {contact_col} NOT LIKE '%@%'
          AND LENGTH(TRIM({contact_col})) > 5
        GROUP BY {contact_col}
        ORDER BY n DESC
        LIMIT 10
    """)
    top_names = [{"contact": r[0], "notice_count": r[1]} for r in cur.fetchall()]
    conn.close()

    return {
        "db_path": db_path,
        "contact_column_used": contact_col,
        "recent_notices_total": total,
        "has_any_contact": has_contact,
        "pct_with_contact": round(has_contact / total * 100, 1) if total else 0,
        "looks_like_person_name": looks_like_person,
        "pct_person_name": round(looks_like_person / total * 100, 1) if total else 0,
        "top_10_contacts": top_names,
        "notes": "Contacts that are not email addresses and > 5 chars are treated as plausible person names. Review top_10_contacts to confirm.",
    }


def run():
    results = {}

    results["govuk_appointments_rss"] = probe_govuk_appointments_rss()
    results["companies_house_alb_officers"] = probe_companies_house_alb_officers()
    results["fts_contact_names"] = probe_fts_contact_names()

    out_path = os.path.join(FINDINGS_DIR, "track2_automated.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: Run the probe**

```bash
cd pwin-competitive-intel/scripts/investigation
python probe_alt_sources.py
```

Expected: GOV.UK RSS returns recent appointment announcements (5–20 per month is typical). Companies House returns active officers for UKHSA, Homes England, UKRI. FTS contact names query shows what fraction of recent notices carry a named contact.

- [ ] **Step 3: Commit**

```bash
cd pwin-competitive-intel
git add scripts/investigation/probe_alt_sources.py scripts/investigation/findings/track2_automated.json
git commit -m "feat(investigation): probe automated Track 2 sources (GOV.UK RSS, Companies House, FTS contacts)"
```

---

## Task 7: Manual alternative source spot-checks and local government reality check

**Files:**
- Create: `pwin-competitive-intel/scripts/investigation/findings/track2_manual.json`
- Create: `pwin-competitive-intel/scripts/investigation/findings/track3_local_gov.md`

This task is manual research. Work through the non-automated sources from the rubric and record findings. Then do the local government reality check.

- [ ] **Step 1: Spot-check GOV.UK People pages for 3 departments**

Visit each URL, count named SCS listed, note whether grade and unit are given, compare count to `track1_parsed.json` named_staff:

- HM Treasury: `https://www.gov.uk/government/organisations/hm-treasury/about/our-governance`
- MoD: `https://www.gov.uk/government/organisations/ministry-of-defence/about/our-governance`
- DfE: `https://www.gov.uk/government/organisations/department-for-education/about/our-governance`

Record: number named, grade depth, whether reporting line shown, date last updated.

- [ ] **Step 2: Sample NAO reports for named SROs**

Visit `https://www.nao.org.uk/reports/` and open 3 recent value-for-money reports. In each, search for "Senior Responsible Owner", "Accounting Officer", or the name of the named official in the foreword. Record: name, role, department, report date.

- [ ] **Step 3: Check Public Accounts Committee witness lists**

Visit `https://committees.parliament.uk/committee/127/public-accounts-committee/publications/?type=oral-evidence` — filter last 12 months. Open 3 session pages. Record: named officials, their departments, their stated roles.

- [ ] **Step 4: LinkedIn manual search (3 departments)**

Search LinkedIn for:
- `"Grade 7" "commercial" "Ministry of Defence"` — count profiles with role and unit visible
- `"Grade 7" "commercial" "Department for Education"` — same
- `"Senior Responsible Owner" "HMRC" OR "HM Revenue"` — same

Record: typical profile completeness (role + unit + start date visible?), number of results visible without connection, whether profiles are current.

- [ ] **Step 5: Record all manual findings in `track2_manual.json`**

Create `findings/track2_manual.json` with one entry per source following the `SOURCE_SCORE_TEMPLATE` from `rubric.py`. Fill in all fields — no blanks.

```json
[
  {
    "id": "gov_uk_people",
    "name": "GOV.UK People pages",
    "coverage_note": "<fill in: e.g. 'HMT: 12 named DG/Director only. MoD: 8 named top tier only. DfE: 15 named.'>" ,
    "currency_note": "<fill in: e.g. 'Page footer shows last updated date. HMT updated 2024-11. MoD updated 2024-09.'>" ,
    "structure": "<fill in: structured / semi-structured / unstructured>" ,
    "licence": "<fill in: OGL / public-domain / paid / scrape-required>" ,
    "useful_for_senior_tier": true,
    "useful_for_evaluator_tier": false,
    "notes": "<fill in your observations>"
  }
]
```

Include entries for: `gov_uk_people`, `nao_reports`, `pac_witnesses`, `linkedin_manual`, `trade_press`, `civil_service_jobs`, `dods_people`.

- [ ] **Step 6: Local government reality check — write `track3_local_gov.md`**

Check these three things and record findings:

1. **LGA canonical officer list**: Visit `https://www.local.gov.uk/our-support/guidance-and-resources/data-and-transparency` — does any dataset give chief officers, Section 151 officers, or monitoring officers across all English councils? Note dataset name and URL if found, or note absence.

2. **Sample 5 council websites**: Visit the "About the council" or "Senior leadership" page for each:
   - Birmingham City Council: `https://www.birmingham.gov.uk/info/20003/council_and_democracy`
   - Manchester City Council: `https://www.manchester.gov.uk/info/100004/about_the_council`
   - London Borough of Hackney: `https://hackney.gov.uk/about-the-council`
   - Oxfordshire County Council: `https://www.oxfordshire.gov.uk/council/about-your-council`
   - South Cambridgeshire District Council: `https://www.scambs.gov.uk/council-and-democracy/`
   For each: record whether senior officers are named, what detail is given (role, grade, contact), and whether the page shows a last-updated date.

3. **Recommendation**: Based on what you find, write one sentence recommending whether local-government coverage should be in v1 or deferred.

- [ ] **Step 7: Commit**

```bash
cd pwin-competitive-intel
git add scripts/investigation/findings/track2_manual.json
git add scripts/investigation/findings/track3_local_gov.md
git commit -m "feat(investigation): manual Track 2 source spot-checks and Track 3 local government reality check"
```

---

## Task 8: Write the feasibility report

**Files:**
- Create: `docs/research/2026-04-30-stakeholder-database-feasibility.md`

This task assembles all findings into the structured report defined in the spec.

- [ ] **Step 1: Load all findings and determine the overall verdict**

Open and read:
- `findings/track1_verdict_scores.json` — the four criterion scores from the organogram ingest
- `findings/track2_automated.json` — GOV.UK RSS, Companies House, FTS contacts
- `findings/track2_manual.json` — manual source scores
- `findings/track3_local_gov.md` — local government reality check

The overall verdict is determined by the weakest of the four criteria that have data:
- If any criterion scores `dont_build` for central government departments → verdict is `dont_build`
- If all central-government criteria score `build_as_scoped` → verdict is `build_as_scoped`
- Otherwise → verdict is `build_narrower` (state which sub-universe to include)

For the working-evaluator coverage criterion: score this based on Track 2 findings. If GOV.UK People pages + NAO reports + PAC witnesses together give named Grade 6 / SRO individuals for ≥ 70% of the sampled departments, it passes. If only central government departments pass, it's `build_narrower`.

- [ ] **Step 2: Write the report to `docs/research/2026-04-30-stakeholder-database-feasibility.md`**

Follow this exact structure (fill in each section from your findings — no placeholder text):

```markdown
# Stakeholder database — feasibility report
**Date:** 2026-04-30  
**Investigation design:** `docs/superpowers/specs/2026-04-30-stakeholder-database-feasibility-design.md`

## Verdict

**[Build as scoped / Build narrower / Don't build]**

[One paragraph. If "build narrower": state the recommended scope (e.g. "central government departments and major ALBs only; NHS and local government deferred"). If "don't build": state the recommended alternative (per-pursuit research, paid Dods People feed, or other). If "build as scoped": confirm all four criteria passed.]

## Verdict criteria scorecard

| Criterion | Threshold (build as scoped) | Measured value | Score |
|---|---|---|---|
| Senior-tier coverage (avg across central gov departments) | ≥ 90% named with reporting line | [fill in %] | [build_as_scoped / build_narrower / dont_build] |
| Working-evaluator coverage — departments with ≥ 1 useful alt source | ≥ 70% of sampled departments | [fill in %] | [score] |
| Max currency lag (worst department) | ≤ 6 months | [fill in days] | [score] |
| Distinct organogram formats | ≤ 2 | [fill in count] | [score] |

## Track 1 — organogram live ingest findings

| Department | Status | Named staff | Expected (approx) | Coverage | Formats quirks | Currency lag | Reporting-line field |
|---|---|---|---|---|---|---|---|
| HM Treasury | [parsed / absent / parse_error] | [n] | ~60 | [%] | [notes] | [days] | [% complete] |
| Ministry of Defence | ... | ... | ~500 | ... | ... | ... | ... |
| Department for Education | ... | ... | ~200 | ... | ... | ... | ... |
| NHS England | ... | ... | N/A | ... | ... | ... | ... |
| Birmingham City Council | ... | ... | N/A | ... | ... | ... | ... |

**Cross-check churn signal:** [N] of [total] sampled individuals verified still in post, [N] confirmed moved on, [N] unknown. Organogram snapshot age: [days]. Estimated annual churn at this rate: [%].

**Parse observations:** [Any encoding issues, extra/missing columns, non-standard grade labels, year-on-year format changes. If all departments shared the same column set with no quirks, say so explicitly.]

## Track 2 — alternative source scorecard

| Source | Useful for senior tier | Useful for evaluator tier | Structure | Licence | Notes |
|---|---|---|---|---|---|
| GOV.UK People pages | [yes/no] | [yes/no] | [structured/semi/unstructured] | [OGL/etc] | [fill in] |
| GOV.UK appointments RSS | ... | ... | ... | ... | ... |
| Companies House (ALB officers) | ... | ... | ... | ... | ... |
| NAO published reports | ... | ... | ... | ... | ... |
| PAC witness lists | ... | ... | ... | ... | ... |
| Civil Service Jobs | ... | ... | ... | ... | ... |
| LinkedIn (manual) | ... | ... | ... | ... | ... |
| Trade press | ... | ... | ... | ... | ... |
| FTS contact names | ... | ... | ... | ... | ... |
| Dods People (paid) | ... | ... | ... | ... | ... |

**Recommended volatile-tier event sources:** [List 2–3 sources that most reliably surface named working-evaluator individuals with role and unit, suitable for wiring as an event-driven supplement to the twice-yearly canonical refresh. Explain why each was chosen.]

## Track 3 — local government reality check

**LGA canonical officer list:** [Found / Not found. If found: URL and coverage. If not found: confirm no central feed exists.]

**Council website sample:**

| Council | Senior officers named | Detail level | Last updated shown |
|---|---|---|---|
| Birmingham CC | [yes/no] | [role only / role + grade / role + grade + contact] | [date or unknown] |
| Manchester CC | ... | ... | ... |
| London Borough of Hackney | ... | ... | ... |
| Oxfordshire CC | ... | ... | ... |
| South Cambridgeshire DC | ... | ... | ... |

**Local government recommendation:** [One sentence from Track 3 step 6.]

## Recommended next step

[If "build as scoped" or "build narrower": state the first three things to do to turn the existing action in `wiki/actions/pwin-stakeholder-canonical-layer.md` into a buildable spec — specifically schema types, ingest parser design, and MCP tool signatures. Reference the architecture note at `wiki/platform/stakeholder-data-layer-architecture.md`.]

[If "don't build": state what to update in the action file to record the verdict and the recommended alternative.]

## Appendix — sample parsed records

For each successfully parsed department, paste the `sample_5` array from `findings/track1_parsed.json`.
```

- [ ] **Step 3: Commit the report**

The report lives under the repo root (`docs/research/`), not inside `pwin-competitive-intel/`. Run from the repo root:

```bash
# From c:\Users\User\Documents\GitHub\PWIN
git add docs/research/2026-04-30-stakeholder-database-feasibility.md
git commit -m "docs(research): stakeholder database feasibility report with verdict and evidence"
```

---

## Task 9: Update the wiki action and close out

**Files:**
- Modify: `C:/Users/User/Documents/Obsidian Vault/wiki/actions/pwin-stakeholder-canonical-layer.md`

- [ ] **Step 1: Update the action file with the investigation verdict**

Open `wiki/actions/pwin-stakeholder-canonical-layer.md`. Add a section at the top (below the frontmatter) recording the verdict:

```markdown
## Investigation result — 2026-04-30

**Verdict:** [Build as scoped / Build narrower / Don't build]

**Evidence:** `docs/research/2026-04-30-stakeholder-database-feasibility.md`

**Recommended scope (if build):** [fill in — e.g. "central government departments + major ALBs; NHS and local government deferred"]

**Next action:** [e.g. "Move to design pass — schema types, ingest parser, MCP tool signatures" or "Update priority to low — use Dods People feed instead"]
```

Update the frontmatter `status` field from `pending` to either `ready-to-design` (if build verdict) or `deferred` / `closed` (if don't build).

- [ ] **Step 2: Commit the investigation scripts together**

```bash
cd pwin-competitive-intel
git add scripts/investigation/
git commit -m "feat(investigation): complete stakeholder feasibility investigation scripts and findings"
```

- [ ] **Step 3: If verdict is "build" or "build narrower" — invoke the brainstorming skill for the database design**

The next session should open `docs/research/2026-04-30-stakeholder-database-feasibility.md`, confirm the verdict, then invoke `superpowers:brainstorming` to design the actual schema, ingest parser, entity-resolution approach, and MCP tool signatures. That session's spec will reference this report as its evidence base.

If the verdict is "don't build", the action file records the decision and the priority roadmap is updated accordingly. No further session is needed for this item.
```
