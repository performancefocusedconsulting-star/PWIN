# pwin-competitive-intel/scripts/investigation/fetch_organograms.py
#
# Searches data.gov.uk for senior-staff organogram CSVs for 5 UK government
# departments, downloads them, and saves a source inventory JSON.
#
# NOTE ON APPROACH:
# data.gov.uk's free-text search API returns the same top results regardless
# of query terms (the ranking is dominated by dataset popularity / modification
# recency, not keyword match). For central government departments that publish
# their organograms under standard Cabinet Office dataset slugs, we bypass
# free-text search and use direct dataset name lookups via package_show.
# For organisations that don't have a known slug, we fall back to free-text
# search and record the absence finding.

import sys, json, os, re, urllib.request, urllib.parse, time
sys.stdout.reconfigure(encoding='utf-8')

from rubric import SAMPLE_DEPARTMENTS

FINDINGS_DIR = os.path.join(os.path.dirname(__file__), "findings")
DATA_GOV_UK_API = "https://data.gov.uk/api/3/action"
RAW_DIR = os.path.join(FINDINGS_DIR, "raw_organograms")
os.makedirs(RAW_DIR, exist_ok=True)

# Known dataset slugs for departments that follow the Cabinet Office standard.
# Discovered by testing package_show directly -- the free-text search API
# does not reliably return department-specific results.
KNOWN_DATASET_SLUGS = {
    "hmt": "organogram-hm-treasury",
    "mod": "organogram-head-office-and-corporate-services-mod",
    "dfe": "organogram-department-for-education",
    "nhse": "organogram-nhs-england",
    # bcc has no organogram dataset on data.gov.uk -- confirmed by search
}


def get_package_by_slug(slug):
    url = f"{DATA_GOV_UK_API}/package_show?id={slug}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    if data.get("success"):
        return data["result"]
    return None


def search_data_gov_uk(query, rows=10):
    params = urllib.parse.urlencode({"q": query, "sort": "metadata_modified desc", "rows": rows})
    url = f"{DATA_GOV_UK_API}/package_search?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def find_senior_staff_resource(package):
    """Return the most recent senior-staff CSV resource from a data.gov.uk package."""
    resources = package.get("resources", [])
    # Must be CSV format -- exclude HTML, PDF, RDF link resources
    csv_resources = [
        r for r in resources
        if (r.get("format") or "").upper() == "CSV"
        and "junior" not in (r.get("name") or "").lower()
    ]
    # Prefer resources explicitly named "senior"
    senior = [
        r for r in csv_resources
        if "senior" in (r.get("name") or "").lower()
        or "senior" in (r.get("url") or "").lower()
    ]
    candidates = senior if senior else csv_resources
    if not candidates:
        return None
    # Sort to get the most recent publication, descending.
    # Strategy: use the resource name as the primary key when it contains an
    # ISO-style date (e.g. "2026-03-31 Organogram (Senior)") because it directly
    # names the data period. Fall back to the max 4-digit year extracted from the
    # URL for legacy resources whose names are None or non-date strings.
    def _sort_key(r):
        name = (r.get("name") or "").strip()
        url = r.get("url") or ""
        # Try ISO date at the start of the name
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", name)
        if date_match:
            return date_match.group(1)  # "2026-03-31" sorts correctly as a string
        # Fall back: extract the largest year from the URL
        years = re.findall(r"\b(20\d{2})\b", url)
        if years:
            return str(max(int(y) for y in years))
        return "0000"
    candidates.sort(key=_sort_key, reverse=True)
    return candidates[0]


def download_resource(resource, dest_path):
    url = resource["url"]
    print(f"  Downloading: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PWIN-Investigation/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
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

        # --- Dataset lookup ---
        pkg = None
        if dept_id in KNOWN_DATASET_SLUGS:
            slug = KNOWN_DATASET_SLUGS[dept_id]
            print(f"  Using known slug: {slug}")
            try:
                pkg = get_package_by_slug(slug)
            except Exception as e:
                entry["absence_note"] = f"data.gov.uk package_show error: {e}"
                results[dept_id] = entry
                continue
        else:
            # Free-text fallback for organisations without a known slug.
            # NOTE: data.gov.uk free-text search does not reliably match by
            # publisher -- it returns popularity-ranked results from the entire
            # catalogue. We use it only to confirm absence: if none of the top
            # results match the target organisation name, we treat it as
            # "no dataset found" for this organisation.
            print(f"  Searching: {dept['data_gov_uk_query']}")
            try:
                result = search_data_gov_uk(dept["data_gov_uk_query"])
            except Exception as e:
                entry["absence_note"] = f"data.gov.uk API error: {e}"
                results[dept_id] = entry
                continue
            packages = result.get("result", {}).get("results", [])
            # Only accept a result if the publishing organisation matches the
            # target department (loose substring match on the dept name)
            dept_name_lower = dept["name"].lower()
            for candidate in packages:
                org_title = (candidate.get("organization") or {}).get("title", "")
                if dept_name_lower in org_title.lower() or org_title.lower() in dept_name_lower:
                    pkg = candidate
                    break
            # pkg remains None if no match found

        if not pkg:
            entry["absence_note"] = "No dataset found on data.gov.uk for this query"
            print(f"  No dataset found")
            results[dept_id] = entry
            continue

        entry["dataset_found"] = pkg.get("title")
        entry["dataset_url"] = f"https://data.gov.uk/dataset/{pkg.get('name')}"
        org_name = pkg.get("organization", {}).get("title", "unknown")
        print(f"  Dataset: {entry['dataset_found']} (org: {org_name})")
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
            entry["absence_note"] = "Download failed -- check URL manually"

        results[dept_id] = entry
        time.sleep(1)  # polite delay

    # --- Special absence note for Birmingham (no organogram publishing regime) ---
    if "bcc" in results and not results["bcc"]["download_ok"]:
        results["bcc"]["absence_note"] = (
            "No organogram dataset found on data.gov.uk. Local authorities have no organogram "
            "publishing requirement under the Cabinet Office transparency mandate (which covers "
            "central government departments and arm's-length bodies only). Birmingham City Council "
            "does not appear to publish a senior-staff organogram in the standard Cabinet Office "
            "CSV format."
        )

    # --- NHS England absence note if stale ---
    if "nhse" in results and results["nhse"]["download_ok"]:
        # Check if the resource name contains a year indicating staleness
        name = results["nhse"].get("resource_name") or results["nhse"].get("resource_url") or ""
        if "2016" in name or "2013" in name:
            results["nhse"]["absence_note"] = (
                "Dataset found but most recent senior-staff file dates from 2016. NHS England "
                "stopped publishing organograms in the Cabinet Office standard format after its "
                "2013-2016 publication run. The downloaded file is historical only -- not suitable "
                "for current stakeholder identification."
            )

    out_path = os.path.join(FINDINGS_DIR, "track1_sources.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved source inventory to {out_path}")
    downloaded = sum(1 for e in results.values() if e["download_ok"])
    print(f"Downloaded: {downloaded}/{len(results)} departments")
    for dept_id, e in results.items():
        status = "OK" if e["download_ok"] else "ABSENT/FAILED"
        note = e.get("absence_note") or ""
        print(f"  {dept_id}: {status}  {note[:80]}")


if __name__ == "__main__":
    run()
