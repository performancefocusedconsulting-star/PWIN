"""
PWIN Competitive Intelligence — Contracts Finder ingest
=======================================================
Fetches UK Contracts Finder notices via the CF search API,
parses CF JSON into normalised dicts, and persists to bid_intel.db
with data_source='cf'.

Usage:
    python ingest_cf.py                    # incremental from cf_last_date
    python ingest_cf.py --from 2021-01-01  # backfill from date
    python ingest_cf.py --limit 500        # cap notices (testing)
"""

import argparse
import hashlib
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import db_utils
from ingest import _looks_like_ch_number, _normalize_ch_number

CF_SEARCH_URL = (
    "https://www.contractsfinder.service.gov.uk"
    "/Published/Notices/OCDS/Search"
)
DB_PATH     = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"
PAGE_SIZE   = 100
RETRY_MAX   = 5
RETRY_DELAY = 10
CF_STATE_KEY = "cf_last_date"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest_cf")


# ── CF-specific helpers ──────────────────────────────────────────────────────

def _cf_hash(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:8]


def _cf_buyer_id(org: dict) -> str:
    org_id = org.get("id") or org.get("organisationId")
    if org_id:
        return f"cf-buyer-{org_id}"
    return f"cf-buyer-{_cf_hash(org.get('name', 'unknown'))}"


def _cf_supplier_id(sup: dict) -> str:
    name = sup.get("supplierName") or sup.get("name") or ""
    postcode = (sup.get("address") or {}).get("postcode", "")
    return f"cf-sup-{_cf_hash(f'{name}|{postcode}')}"


def _dt_cf(s) -> str | None:
    if not s:
        return None
    try:
        s = str(s)
        if "T" in s:
            return s[:10] + " " + s[11:19]
        return s[:10]
    except Exception:
        return None


_STATUS_MAP = {
    "live":      "active",
    "awarded":   "complete",
    "expired":   "cancelled",
    "withdrawn": "cancelled",
    "cancelled": "cancelled",
}


def _cf_buyer_row(org: dict) -> dict:
    addr = org.get("address") or {}
    return {
        "id":          _cf_buyer_id(org),
        "name":        org.get("name", "Unknown"),
        "postal_code": addr.get("postcode"),
        "locality":    addr.get("town"),
        "data_source": "cf",
    }


def _cf_supplier_row(sup: dict) -> dict:
    addr = sup.get("address") or {}
    raw_ch = sup.get("companiesHouseNumber") or sup.get("companiesHouseNo")
    ch_no = _normalize_ch_number(raw_ch) if raw_ch and _looks_like_ch_number(raw_ch) else None
    return {
        "id":                _cf_supplier_id(sup),
        "name":              sup.get("supplierName") or sup.get("name") or "Unknown",
        "companies_house_no": ch_no,
        "postal_code":       addr.get("postcode"),
        "locality":          addr.get("town"),
        "data_source":       "cf",
    }


def _cf_notice_row(notice: dict, buyer_id: str) -> dict:
    notice_id = str(notice.get("id") or notice.get("noticeIdentifier") or "")
    value = notice.get("valueHigh") or notice.get("valueLow") or notice.get("value")
    if isinstance(value, dict):
        value = value.get("amount")
    raw_status = (notice.get("status") or "").lower()
    return {
        "ocid":             f"cf-{notice_id}",
        "buyer_id":         buyer_id,
        "title":            notice.get("title"),
        "description":      notice.get("description"),
        "published_date":   _dt_cf(notice.get("publishedDate")),
        "tender_end_date":  _dt_cf(notice.get("deadlineDate")),
        "value_amount":     value,
        "value_amount_gross": value,
        "notice_type":      notice.get("noticeType") or notice.get("type"),
        "tender_status":    _STATUS_MAP.get(raw_status, raw_status) or None,
        "data_source":      "cf",
        "suitable_for_sme": 1 if notice.get("isSuitableForSme") else 0,
        "above_threshold":  0,
    }


def _cf_award_row(notice: dict, ocid: str) -> dict | None:
    notice_type = (notice.get("noticeType") or notice.get("type") or "").lower()
    if "award" not in notice_type:
        return None
    has_signal = (
        notice.get("awardedValue") is not None or
        notice.get("awardedDate") or
        notice.get("suppliers") or
        notice.get("awardedSuppliers")
    )
    if not has_signal:
        return None
    notice_id = str(notice.get("id") or notice.get("noticeIdentifier") or "")
    award_val = notice.get("awardedValue")
    if isinstance(award_val, dict):
        award_val = award_val.get("amount")
    return {
        "id":                  f"cf-award-{notice_id}",
        "ocid":                ocid,
        "award_date":          _dt_cf(notice.get("awardedDate")),
        "value_amount":        award_val,
        "value_amount_gross":  award_val,
        "contract_start_date": _dt_cf(notice.get("contractStart")),
        "contract_end_date":   _dt_cf(notice.get("contractEnd")),
        "status":              "active" if award_val is not None else None,
        "data_source":         "cf",
    }


# ── OCDS release translator ───────────────────────────────────────────────────

def _ocds_release_to_cf_notice(release: dict) -> dict:
    """Translate a CF OCDS release into the bespoke CF notice dict
    that process_cf_notice() expects.  Keeps parser logic in one place."""
    tender = release.get("tender") or {}
    parties = release.get("parties") or []
    tags = release.get("tag") or []

    # Buyer party
    buyer_party = next(
        (p for p in parties if "buyer" in (p.get("roles") or [])), {}
    )
    buyer_addr = buyer_party.get("address") or {}

    # Build organisation dict matching _cf_buyer_row expectations
    org = {
        "id":   buyer_party.get("id") or "",
        "name": buyer_party.get("name") or "",
        "address": {
            "postcode": buyer_addr.get("postalCode"),
            "town":     buyer_addr.get("locality"),
        },
    }

    # Value: prefer tender.value.amount
    tender_val = tender.get("value") or {}
    value_amount = tender_val.get("amount")

    # Notice type / status derived from tag
    is_award = any("award" in t.lower() for t in tags)
    notice_type = "Contract Award Notice" if is_award else "Contract Notice"
    raw_status  = (tender.get("status") or "").lower()

    # Tender period
    tender_period = tender.get("tenderPeriod") or {}
    contract_period = tender.get("contractPeriod") or {}

    # Suitability
    suitability = tender.get("suitability") or {}

    # CPV codes from tender.classification + tender.items
    cpv_codes: list[dict] = []
    classification = tender.get("classification")
    if classification and classification.get("id"):
        cpv_codes.append({
            "code":  classification["id"],
            "label": classification.get("description") or "",
        })

    # Award data (first award only)
    awards_list = release.get("awards") or []
    award = awards_list[0] if awards_list else None
    award_val_dict = (award or {}).get("value") or {}
    award_period = (award or {}).get("contractPeriod") or {}

    # Suppliers: from parties with supplier role, enriched with identifiers
    supplier_id_map: dict[str, dict] = {}
    for p in parties:
        if "supplier" in (p.get("roles") or []):
            p_id = p.get("id") or ""
            p_addr = p.get("address") or {}
            ident = p.get("identifier") or {}
            # Extract CH number from GB-COH scheme
            ch_no = None
            if ident.get("scheme") == "GB-COH":
                ch_no = ident.get("id")
            elif p_id.startswith("GB-COH-"):
                ch_no = p_id[len("GB-COH-"):]
            supplier_id_map[p_id] = {
                "supplierName":         p.get("name") or "",
                "companiesHouseNumber": ch_no,
                "address": {
                    "postcode": p_addr.get("postalCode"),
                    "town":     p_addr.get("locality"),
                },
            }

    # Award suppliers list (cross-reference with party details)
    suppliers = []
    if award:
        for s in (award.get("suppliers") or []):
            sid = s.get("id") or ""
            enriched = supplier_id_map.get(sid) or {
                "supplierName": s.get("name") or "",
                "address": {},
            }
            suppliers.append(enriched)

    # Derive a stable notice id from the CF OCID (strip prefix)
    ocid = release.get("ocid") or ""
    notice_id = ocid.replace("ocds-b5fd17-", "") if ocid.startswith("ocds-b5fd17-") else ocid

    return {
        "id":              notice_id,
        "title":           tender.get("title"),
        "description":     tender.get("description"),
        "publishedDate":   release.get("date"),
        "deadlineDate":    tender_period.get("endDate"),
        "valueLow":        value_amount,
        "valueHigh":       value_amount,
        "noticeType":      notice_type,
        "status":          raw_status if raw_status else ("awarded" if is_award else "live"),
        "isSuitableForSme": suitability.get("sme") or False,
        "industryCodes":   cpv_codes,
        "organisation":    org,
        "awardedDate":     (award or {}).get("date"),
        "awardedValue":    award_val_dict.get("amount"),
        "suppliers":       suppliers,
        "contractStart":   award_period.get("startDate"),
        "contractEnd":     award_period.get("endDate"),
    }


# ── API fetch ────────────────────────────────────────────────────────────────

def fetch_cf_page(from_date: str, to_date: str, cursor: str | None = None) -> dict | None:
    """Fetch one page of CF OCDS releases.

    Uses the GET /Published/Notices/OCDS/Search endpoint.
    On the first call pass cursor=None; subsequent pages use the cursor
    returned in data["links"]["next"].
    Returns the raw OCDS response dict (keys: releases, links, …) or None.
    """
    if cursor:
        url = cursor  # links.next is the full URL already
    else:
        url = (
            f"{CF_SEARCH_URL}"
            f"?publishedFrom={from_date}"
            f"&publishedTo={to_date}"
            f"&stages=planning,tender,award"
            f"&limit={PAGE_SIZE}"
        )

    for attempt in range(1, RETRY_MAX + 1):
        try:
            req = Request(
                url,
                headers={
                    "Accept":     "application/json",
                    "User-Agent": "PWIN-CompetitiveIntel/1.0",
                },
                method="GET",
            )
            with urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            log.warning("HTTP %s attempt %d", e.code, attempt)
            if e.code == 429:
                time.sleep(RETRY_DELAY * attempt)
            elif e.code >= 500:
                time.sleep(RETRY_DELAY)
            else:
                break
        except (URLError, TimeoutError, OSError) as e:
            log.warning("Network error attempt %d: %s", attempt, e)
            time.sleep(RETRY_DELAY * attempt)
        except ValueError as e:
            log.warning("Non-JSON response attempt %d: %s", attempt, e)
            time.sleep(RETRY_DELAY * attempt)
    log.error("All %d retries exhausted [%s..%s]", RETRY_MAX, from_date[:10], to_date[:10])
    return None


# ── Notice processor ─────────────────────────────────────────────────────────

def process_cf_notice(conn: sqlite3.Connection, notice: dict) -> dict:
    counts = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0}

    notice_id = str(notice.get("id") or notice.get("noticeIdentifier") or "")
    if not notice_id:
        log.warning("CF notice has no id — skipping")
        return counts

    org = notice.get("organisation") or notice.get("buyerOrganisation") or {}
    if not org or not org.get("name"):
        log.debug("Notice %s has no organisation — skipping", notice_id)
        return counts

    # Buyer
    buyer_row = _cf_buyer_row(org)
    db_utils.upsert_buyer_row(conn, buyer_row)
    buyer_id = buyer_row["id"]
    counts["buyers"] += 1

    # Notice
    notice_row = _cf_notice_row(notice, buyer_id)
    ocid = notice_row["ocid"]
    db_utils.upsert_notice_row(conn, notice_row)
    counts["notices"] += 1

    # CPV codes — CF uses industryCodes or cpvCodes
    for cpv in (notice.get("industryCodes") or notice.get("cpvCodes") or []):
        code = cpv.get("code") or cpv.get("id")
        if code:
            db_utils.upsert_cpv_row(conn, ocid, str(code),
                                    cpv.get("label") or cpv.get("description") or "")

    # Award + suppliers (award notices only)
    award_row = _cf_award_row(notice, ocid)
    if award_row:
        db_utils.upsert_award_row(conn, award_row)
        award_id = award_row["id"]
        counts["awards"] += 1

        for sup in (notice.get("suppliers") or notice.get("awardedSuppliers") or []):
            sup_row = _cf_supplier_row(sup)
            db_utils.upsert_supplier_row(conn, sup_row)
            db_utils.link_award_supplier(conn, award_id, sup_row["id"])
            counts["suppliers"] += 1

    return counts


# ── Date windowing ────────────────────────────────────────────────────────────

def _date_windows(from_date: str, to_date: str):
    """Yield (from_iso, to_iso) monthly windows between two ISO date strings."""
    start = datetime.fromisoformat(from_date[:10])
    end   = datetime.fromisoformat(to_date[:10])
    while start <= end:
        if start.month == 12:
            month_end = start.replace(day=31)
        else:
            month_end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        window_end = min(month_end, end)
        yield (
            start.strftime("%Y-%m-%dT00:00:00"),
            window_end.strftime("%Y-%m-%dT23:59:59"),
        )
        start = window_end + timedelta(days=1)


def ingest_window(
    conn: sqlite3.Connection,
    from_date: str,
    to_date: str,
    limit: int | None = None,
) -> dict:
    total = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0}
    processed = 0
    cursor: str | None = None
    page = 1

    while True:
        log.info("CF page %d  [%s -> %s]", page, from_date[:10], to_date[:10])
        data = fetch_cf_page(from_date, to_date, cursor)
        if not data:
            log.error("Failed to fetch page %d — aborting this window", page)
            break

        releases = data.get("releases") or []
        if not releases:
            log.info("No results on page %d — window done", page)
            break

        for release in releases:
            notice = _ocds_release_to_cf_notice(release)
            counts = process_cf_notice(conn, notice)
            for k in total:
                total[k] += counts.get(k, 0)
            processed += 1
            if limit and processed >= limit:
                log.info("Reached --limit %d", limit)
                conn.commit()
                return total

        conn.commit()

        # CF OCDS uses cursor-based pagination via links.next
        links = data.get("links") or {}
        next_url = links.get("next")
        if not next_url:
            break
        cursor = next_url
        page += 1
        time.sleep(1.0)

    return total


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PWIN Competitive Intel — Contracts Finder ingest")
    parser.add_argument("--from", dest="from_date",
                        help="Start date ISO (default: cf_last_date stored in DB)")
    parser.add_argument("--limit", type=int,
                        help="Max notices per run (testing)")
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    if args.from_date:
        start = args.from_date
        log.info("CF ingest from %s (--from flag)", start[:10])
    else:
        start = db_utils.get_ingest_state(conn, CF_STATE_KEY) or "2021-01-01T00:00:00"
        log.info("CF ingest from %s (stored cursor)", start[:10])

    log.info("CF ingest to   %s", now[:10])

    grand_total = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0}
    last_window_end = None

    try:
        for from_dt, to_dt in _date_windows(start, now):
            window = ingest_window(conn, from_dt, to_dt, args.limit)
            for k in grand_total:
                grand_total[k] += window.get(k, 0)
            last_window_end = to_dt
            db_utils.set_ingest_state(conn, CF_STATE_KEY, last_window_end[:19])
            conn.commit()
            if args.limit and grand_total["notices"] >= args.limit:
                break
    except KeyboardInterrupt:
        log.warning("Interrupted — progress committed up to last window")
    except Exception as e:
        log.error("CF ingest aborted: %s", e)
        raise
    finally:
        if last_window_end:
            db_utils.set_ingest_state(conn, CF_STATE_KEY, last_window_end[:19])
            log.info("CF cursor advanced to %s", last_window_end[:10])

        log.info("=" * 60)
        log.info("CF ingest complete")
        log.info("  Notices    : %d", grand_total["notices"])
        log.info("  Awards     : %d", grand_total["awards"])
        log.info("  Buyers     : %d", grand_total["buyers"])
        log.info("  Suppliers  : %d", grand_total["suppliers"])
        conn.close()


if __name__ == "__main__":
    main()
