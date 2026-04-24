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
    "/Published/Notices/PublishedSearchApi/Search"
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


# ── API fetch ────────────────────────────────────────────────────────────────

def fetch_cf_page(from_date: str, to_date: str, page: int) -> dict | None:
    payload = json.dumps({
        "publishedFrom": from_date,
        "publishedTo":   to_date,
        "size":          PAGE_SIZE,
        "page":          page,
    }).encode("utf-8")

    for attempt in range(1, RETRY_MAX + 1):
        try:
            req = Request(
                CF_SEARCH_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept":       "application/json",
                    "User-Agent":   "PWIN-CompetitiveIntel/1.0",
                },
                method="POST",
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
    log.error("All %d retries exhausted for page %d [%s..%s]", RETRY_MAX, page, from_date[:10], to_date[:10])
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
