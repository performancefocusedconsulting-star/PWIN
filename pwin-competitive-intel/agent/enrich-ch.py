"""
PWIN Competitive Intelligence — Companies House Enrichment
==========================================================
Enriches supplier records with Companies House data:
company status, SIC codes, directors, accounts (turnover/net assets),
incorporation date, registered address, parent company.

Usage:
    python agent/enrich-ch.py                    # enrich all unenriched suppliers with CH numbers
    python agent/enrich-ch.py --refresh          # re-enrich all (even previously enriched)
    python agent/enrich-ch.py --limit 100        # cap number of API calls (testing)
    python agent/enrich-ch.py --company 02048608 # enrich a single company (testing)

Requires COMPANIES_HOUSE_API_KEY environment variable.
Register free at: https://developer.company-information.service.gov.uk/
"""

import argparse
import base64
import json
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"
CH_API = "https://api.company-information.service.gov.uk"
RATE_DELAY = 0.6  # 600ms between calls (CH rate limit: ~600/5min)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("enrich-ch")


def get_api_key():
    key = os.environ.get("COMPANIES_HOUSE_API_KEY")
    if not key:
        log.error("Set COMPANIES_HOUSE_API_KEY environment variable")
        log.error("Register free at: https://developer.company-information.service.gov.uk/")
        sys.exit(1)
    return key


def ch_fetch(path, api_key):
    """Fetch from Companies House API with basic auth."""
    url = CH_API + path
    auth = base64.b64encode(f"{api_key}:".encode()).decode()
    req = Request(url, headers={
        "Accept": "application/json",
        "Authorization": f"Basic {auth}",
    })
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 429:
            log.warning("Rate limited — waiting 30s")
            time.sleep(30)
            return ch_fetch(path, api_key)
        log.warning("CH API error %s for %s", e.code, path)
        return None
    except URLError as e:
        log.warning("Network error: %s", e.reason)
        return None


def enrich_company(conn, supplier_id, company_no, api_key):
    """Fetch all available data for a company and update the supplier record."""

    # 1. Company profile
    profile = ch_fetch(f"/company/{company_no}", api_key)
    if not profile:
        return False

    company_name = profile.get("company_name")
    status = profile.get("company_status")
    company_type = profile.get("type")
    incorporated = profile.get("date_of_creation")
    sic_codes = json.dumps(profile.get("sic_codes", []))

    # Registered address
    addr = profile.get("registered_office_address", {})
    addr_parts = [addr.get("address_line_1"), addr.get("address_line_2"),
                  addr.get("locality"), addr.get("postal_code")]
    address = ", ".join(p for p in addr_parts if p)

    # 2. Officers (current directors only)
    directors = []
    officers_data = ch_fetch(f"/company/{company_no}/officers?items_per_page=50", api_key)
    time.sleep(RATE_DELAY)
    if officers_data:
        for item in officers_data.get("items", []):
            if item.get("resigned_on"):
                continue
            role = item.get("officer_role", "")
            if role in ("director", "corporate-director", "llp-member", "corporate-llp-member"):
                directors.append(item.get("name", ""))
    directors_json = json.dumps(directors[:20])

    # 3. Filing history — find latest accounts for financial data
    turnover = None
    net_assets = None
    employees = None
    accounts_date = None

    # The accounts data isn't directly in the API — we get the filing date
    # and accounts type. Full financial data requires parsing the iXBRL filing.
    # For now, capture what the profile provides.
    accounts = profile.get("accounts", {})
    if accounts.get("last_accounts"):
        accounts_date = accounts["last_accounts"].get("made_up_to")
        # Account category tells us scale: micro-entity, small, medium, full
        # This correlates with data availability

    # 4. Parent company (from PSC or company links)
    parent = None
    # Check for corporate PSC (person of significant control)
    psc_data = ch_fetch(f"/company/{company_no}/persons-with-significant-control?items_per_page=10", api_key)
    time.sleep(RATE_DELAY)
    if psc_data:
        for psc in psc_data.get("items", []):
            if psc.get("kind") == "corporate-entity-person-with-significant-control":
                parent = psc.get("name")
                break
            if psc.get("kind") == "legal-person-person-with-significant-control":
                parent = psc.get("name")
                break

    # Update supplier record
    conn.execute("""
        UPDATE suppliers SET
            ch_company_name = ?,
            ch_status = ?,
            ch_type = ?,
            ch_incorporated = ?,
            ch_sic_codes = ?,
            ch_address = ?,
            ch_turnover = ?,
            ch_net_assets = ?,
            ch_employees = ?,
            ch_accounts_date = ?,
            ch_directors = ?,
            ch_parent = ?,
            ch_enriched_at = datetime('now')
        WHERE id = ?
    """, (
        company_name, status, company_type, incorporated,
        sic_codes, address, turnover, net_assets, employees,
        accounts_date, directors_json, parent, supplier_id,
    ))

    return True


def main():
    parser = argparse.ArgumentParser(description="Companies House enrichment")
    parser.add_argument("--refresh", action="store_true", help="Re-enrich all suppliers")
    parser.add_argument("--limit", type=int, help="Max suppliers to enrich")
    parser.add_argument("--company", help="Enrich a single company number (test)")
    args = parser.parse_args()

    api_key = get_api_key()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    if args.company:
        # Test mode — enrich one company
        log.info("Testing enrichment for %s", args.company)
        profile = ch_fetch(f"/company/{args.company}", api_key)
        if profile:
            print(json.dumps(profile, indent=2)[:2000])
        else:
            print("Not found")
        conn.close()
        return

    # Find suppliers to enrich
    if args.refresh:
        sql = "SELECT id, name, companies_house_no FROM suppliers WHERE companies_house_no IS NOT NULL"
    else:
        sql = "SELECT id, name, companies_house_no FROM suppliers WHERE companies_house_no IS NOT NULL AND ch_enriched_at IS NULL"

    if args.limit:
        sql += f" LIMIT {args.limit}"

    suppliers = conn.execute(sql).fetchall()
    total = len(suppliers)
    log.info("Found %d suppliers to enrich", total)

    enriched = 0
    failed = 0

    for i, sup in enumerate(suppliers):
        log.info("  [%d/%d] %s (CH: %s)", i + 1, total, sup["name"][:40], sup["companies_house_no"])

        # Clean company number — FTS data sometimes has "Company number XXXXXXXX" format
    ch_no = sup["companies_house_no"].strip()
    if " " in ch_no:
        # Extract just the number part
        import re
        match = re.search(r'\b(\d{6,8}|[A-Z]{2}\d{6}|OC\d{6})\b', ch_no)
        if match:
            ch_no = match.group(1)
        else:
            log.warning("  Skipping — bad CH number: %s", ch_no)
            failed += 1
            continue

    success = enrich_company(conn, sup["id"], ch_no, api_key)
        if success:
            enriched += 1
        else:
            failed += 1

        # Commit every 20 records
        if enriched % 20 == 0:
            conn.commit()

        time.sleep(RATE_DELAY)

    conn.commit()
    conn.close()

    log.info("=" * 50)
    log.info("Enrichment complete")
    log.info("  Enriched: %d", enriched)
    log.info("  Failed:   %d", failed)
    log.info("  Skipped:  %d", total - enriched - failed)


if __name__ == "__main__":
    main()
