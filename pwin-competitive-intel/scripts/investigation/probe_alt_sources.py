import sys, json, os, urllib.request, urllib.error, csv, sqlite3, time, re, base64
from datetime import datetime, timedelta
sys.stdout.reconfigure(encoding='utf-8')

FINDINGS_DIR = os.path.join(os.path.dirname(__file__), "findings")


# --- GOV.UK Appointments RSS ---

def probe_govuk_appointments_rss():
    # Try both the old and new GOV.UK atom feed URLs for appointments
    candidates = [
        "https://www.gov.uk/government/announcements.atom?announcement_filter_option=appointments",
        "https://www.gov.uk/search/news-and-communications.atom?announcement_filter_option=appointments",
    ]
    print("Probing GOV.UK appointments RSS...")
    content = None
    used_url = None
    for url in candidates:
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                content = resp.read().decode("utf-8")
            used_url = url
            break
        except urllib.error.HTTPError as e:
            print(f"  {url} -> HTTP {e.code}")
        except Exception as e:
            print(f"  {url} -> {e}")
    if content is None:
        return {"error": "All GOV.UK appointments RSS URLs returned errors", "urls_tried": candidates}

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
        "url_used": used_url,
        "total_entries_in_feed": len(entries),
        "entries_last_30_days": len(recent),
        "sample_3": recent[:3],
        "notes": "Each entry is an appointment announcement. Check whether they name the individual and give role+department.",
    }


# --- Companies House ALB officers ---

def probe_companies_house_alb_officers():
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
            api_key = os.environ.get("COMPANIES_HOUSE_API_KEY", "")
            credentials = base64.b64encode(f"{api_key}:".encode()).decode()
            req = urllib.request.Request(url, headers={
                "User-Agent": "PWIN-Investigation/1.0",
                "Authorization": f"Basic {credentials}",
            })
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
        os.path.join(os.path.dirname(__file__), "../../db/bid_intel.db"),
        os.path.join(os.path.dirname(__file__), "../../../pwin-competitive-intel/db/bid_intel.db"),
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

    cur.execute("PRAGMA table_info(notices)")
    cols = [row[1] for row in cur.fetchall()]
    contact_cols = [c for c in cols if "contact" in c.lower()]

    if not contact_cols:
        conn.close()
        return {"error": "No contact columns found on notices table", "columns_available": cols}

    contact_col = contact_cols[0]
    print(f"  Using contact column: {contact_col}")

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
