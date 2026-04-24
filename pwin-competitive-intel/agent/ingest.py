"""
PWIN Competitive Intelligence — FTS OCDS Ingest Agent
=====================================================
Fetches UK Find a Tender OCDS release packages incrementally,
parses buyers / suppliers / notices / awards / lots,
and persists to SQLite.

Usage:
    python ingest.py              # incremental from stored cursor
    python ingest.py --full       # full re-ingest from 2024-01-01
    python ingest.py --from 2026-01-01  # custom start date
    python ingest.py --limit 500  # cap releases per run (testing)
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

import db_utils
from db_utils import (
    get_db, init_schema,
    upsert_buyer_row, upsert_supplier_row, upsert_notice_row,
    upsert_award_row, upsert_cpv_row, link_award_supplier,
)

# ── Config ─────────────────────────────────────────────────────────────────

BASE_URL    = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
DB_PATH     = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"
PAGE_SIZE   = 100
RETRY_MAX   = 5
RETRY_DELAY = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest")


# ── Database ────────────────────────────────────────────────────────────────

def get_cursor(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT value FROM ingest_state WHERE key='last_cursor'"
    ).fetchone()
    return row["value"] if row and row["value"] else ""


def set_cursor(conn: sqlite3.Connection, value: str):
    conn.execute(
        "INSERT OR REPLACE INTO ingest_state (key, value, updated) VALUES (?, ?, datetime('now'))",
        ("last_cursor", value),
    )
    conn.commit()


def get_backfill_url(conn: sqlite3.Connection) -> str:
    """Saved API next-page URL for an in-progress backfill, or empty if none."""
    row = conn.execute(
        "SELECT value FROM ingest_state WHERE key='backfill_next_url'"
    ).fetchone()
    return row["value"] if row and row["value"] else ""


def set_backfill_url(conn: sqlite3.Connection, value: str):
    conn.execute(
        "INSERT OR REPLACE INTO ingest_state (key, value, updated) VALUES (?, ?, datetime('now'))",
        ("backfill_next_url", value),
    )
    conn.commit()


def clear_backfill_url(conn: sqlite3.Connection):
    conn.execute("DELETE FROM ingest_state WHERE key='backfill_next_url'")
    conn.commit()


# ── API fetch ───────────────────────────────────────────────────────────────

def fetch_url(url: str) -> Optional[dict]:
    """Fetch a URL with retries. Returns parsed JSON or None."""
    for attempt in range(1, RETRY_MAX + 1):
        try:
            req = Request(url, headers={
                "Accept": "application/json",
                "User-Agent": "PWIN-CompetitiveIntel/1.0",
            })
            with urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            log.warning("HTTP %s on attempt %d: %s", e.code, attempt, url[:120])
            if e.code == 429:
                time.sleep(RETRY_DELAY * attempt)
            elif e.code >= 500:
                time.sleep(RETRY_DELAY)
            else:
                break
        except URLError as e:
            log.warning("Network error attempt %d: %s", attempt, e.reason)
            time.sleep(RETRY_DELAY * attempt)
        except (TimeoutError, OSError) as e:
            # Read timeouts from urlopen surface as TimeoutError (Python 3.10+),
            # and underlying socket errors as OSError. Neither is wrapped as URLError.
            log.warning("Read timeout / socket error attempt %d: %s", attempt, e)
            time.sleep(RETRY_DELAY * attempt)
        except ValueError as e:
            # json.JSONDecodeError (subclass of ValueError) — API returned non-JSON
            # (e.g. HTML maintenance page). Retry in case it's transient.
            log.warning("Non-JSON response attempt %d: %s", attempt, e)
            time.sleep(RETRY_DELAY * attempt)
    log.error("All %d retries exhausted for %s", RETRY_MAX, url[:120])
    return None


def paginate(
    updated_from: Optional[str] = None,
    start_url: Optional[str] = None,
    limit: Optional[int] = None,
    max_pages: Optional[int] = None,
    on_page_done=None,
):
    """Generator — yields individual OCDS releases, using proper cursor pagination.

    Note: the FTS API returns releases in newest-first order. updatedFrom acts as
    a lower bound; pagination walks backwards in time toward that bound.

    Args:
        updated_from: ISO date string — start of a fresh pagination
        start_url:    Resume from a previously-saved API next-page URL (overrides updated_from)
        limit:        Max releases to yield total
        max_pages:    Max pages to fetch in this invocation
        on_page_done: Callback(next_url_or_empty) invoked after each page is fully consumed.
                      Used by backfill mode to persist progress between runs.
    """
    if start_url:
        url = start_url
    else:
        params = {"limit": PAGE_SIZE, "updatedFrom": updated_from}
        url = BASE_URL + "?" + urlencode(params)

    total_yielded = 0
    page = 0

    while url:
        page += 1
        log.info("Fetching page %d", page)
        data = fetch_url(url)
        if not data:
            log.error("Failed to fetch page %d — aborting", page)
            # Don't update on_page_done — we want the same URL retried next run
            break

        releases = data.get("releases", [])
        if not releases:
            log.info("No more releases — done")
            if on_page_done:
                on_page_done("")  # Signal completion — clear saved state
            break

        for release in releases:
            yield release
            total_yielded += 1
            if limit and total_yielded >= limit:
                log.info("Reached --limit %d — stopping", limit)
                return

        # Use the API's own cursor for pagination
        next_url = data.get("links", {}).get("next")
        if next_url and next_url != url:
            if on_page_done:
                on_page_done(next_url)  # Persist progress before fetching next
            url = next_url
        else:
            if on_page_done:
                on_page_done("")  # No more pages — clear saved state
            break

        if max_pages and page >= max_pages:
            log.info("Reached --max-pages %d — stopping (resume saved)", max_pages)
            return

        time.sleep(1.0)  # Polite rate limiting


# ── Parsing helpers ─────────────────────────────────────────────────────────

def _safe(d: dict, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
        if d is None:
            return default
    return d


def _dt(s) -> Optional[str]:
    """Normalise datetime string to ISO format for SQLite, or None."""
    if not s:
        return None
    try:
        return s[:19].replace("T", " ")
    except Exception:
        return None


def _party(parties: list, role: str) -> Optional[dict]:
    for p in parties:
        if role in p.get("roles", []):
            return p
    return None


def _all_parties(parties: list, role: str) -> list:
    """Return all parties matching a role."""
    return [p for p in parties if role in p.get("roles", [])]


# Companies House numbers are 8 characters: 8 digits, or 2 letter prefix + 6 digits.
# Prefixes: SC (Scotland), NI / R (N Ireland), OC/SO/NC/NL (LLP variants),
# IP (industrial/provident), FC (foreign co branch), AC/RC/CE/ZC (other).
# We accept 6-8 trailing digits to handle older numbers recorded without leading zeros.
_CH_NUMBER_RE = re.compile(
    r'^(SC|NI|NL|OC|SO|NC|IP|FC|RC|SR|RS|AC|CE|ZC|R)?(\d{6,8})$',
    re.IGNORECASE,
)


def _looks_like_ch_number(value) -> bool:
    """Does this value plausibly look like a UK Companies House number?
    Accepts bare digits or a 2-letter (rarely 1-letter) prefix followed by digits.
    Rejects obvious foreign registers (e.g. 'HRB 304054', 'B 12345').
    """
    if not value:
        return False
    s = str(value).strip().replace(" ", "")
    return bool(_CH_NUMBER_RE.match(s))


def _normalize_ch_number(value) -> str:
    """Normalise to canonical CH form: uppercase prefix, digits zero-padded to 8."""
    s = str(value).strip().replace(" ", "")
    m = _CH_NUMBER_RE.match(s)
    if not m:
        return s
    prefix = (m.group(1) or "").upper()
    digits = m.group(2).zfill(8 - len(prefix))
    return f"{prefix}{digits}"


def _extract_coh(party: dict) -> Optional[str]:
    """Extract a Companies House number from an OCDS party.

    Handles three real-world cases seen in the UK FTS / OCP feed:
      1. identifier.scheme == 'GB-COH' (the spec-compliant case)
      2. identifier has an id but no scheme — common publisher omission.
         We accept it only if the value matches the CH number regex.
      3. same as above but in additionalIdentifiers.

    Values are validated in all cases — publishers sometimes tag non-UK
    registers (e.g. German HRB numbers) as GB-COH by mistake, so we
    reject anything that does not match the CH number format.
    """
    ident = party.get("identifier") or {}
    scheme = ident.get("scheme")
    raw_id = ident.get("id")

    if scheme == "GB-COH" and _looks_like_ch_number(raw_id):
        return _normalize_ch_number(raw_id)
    if not scheme and _looks_like_ch_number(raw_id):
        return _normalize_ch_number(raw_id)

    for ai in party.get("additionalIdentifiers", []) or []:
        ai_scheme = ai.get("scheme")
        ai_id = ai.get("id")
        if ai_scheme == "GB-COH" and _looks_like_ch_number(ai_id):
            return _normalize_ch_number(ai_id)
        if not ai_scheme and _looks_like_ch_number(ai_id):
            return _normalize_ch_number(ai_id)

    return None


def _extract_cpv(items: list) -> list:
    """Extract CPV codes from items array → list of (code, description) tuples."""
    seen = set()
    cpvs = []
    # From additionalClassifications
    for item in items:
        for cls in item.get("additionalClassifications", []):
            if cls.get("scheme") == "CPV" and cls.get("id") not in seen:
                seen.add(cls["id"])
                cpvs.append((cls["id"], cls.get("description", "")))
    # From top-level classification
    for item in items:
        cls = item.get("classification", {})
        if cls.get("scheme") == "CPV" and cls.get("id") not in seen:
            seen.add(cls["id"])
            cpvs.append((cls["id"], cls.get("description", "")))
    return cpvs


def _extract_criteria(lots: list) -> Optional[str]:
    """Extract award criteria from lots → JSON string."""
    criteria = []
    for lot in lots:
        for c in _safe(lot, "awardCriteria", "criteria") or []:
            criteria.append({
                "type": c.get("type"),
                "name": c.get("name"),
                "description": c.get("description"),
            })
    return json.dumps(criteria) if criteria else None


# ── Upsert functions ────────────────────────────────────────────────────────

def upsert_buyer(conn: sqlite3.Connection, party: dict):
    addr = party.get("address", {})
    contact = party.get("contactPoint", {})
    details = party.get("details", {})
    org_type = None
    devolved = None
    for cls in details.get("classifications", []):
        if cls.get("scheme") == "UK_CA_TYPE":
            org_type = cls.get("id")
        if cls.get("scheme") == "UK_CA_DEVOLVED_REGULATIONS":
            devolved = cls.get("id")
    upsert_buyer_row(conn, {
        "id": party.get("id"),
        "name": party.get("name"),
        "org_type": org_type,
        "devolved_region": devolved,
        "street_address": addr.get("streetAddress"),
        "locality": addr.get("locality"),
        "postal_code": addr.get("postalCode"),
        "region_code": addr.get("region"),
        "contact_name": contact.get("name"),
        "contact_email": contact.get("email"),
        "contact_telephone": contact.get("telephone"),
        "website": details.get("url"),
        "data_source": "fts",
    })


def upsert_supplier(conn: sqlite3.Connection, party: dict) -> str:
    addr = party.get("address", {})
    contact = party.get("contactPoint", {})
    details = party.get("details", {})
    return upsert_supplier_row(conn, {
        "id": party.get("id"),
        "name": party.get("name"),
        "companies_house_no": _extract_coh(party),
        "scale": details.get("scale"),
        "is_vcse": int(details.get("vcse", False)),
        "is_sheltered": int(details.get("shelteredWorkshop", False)),
        "is_public_mission": int(details.get("publicServiceMissionOrganization", False)),
        "street_address": addr.get("streetAddress"),
        "locality": addr.get("locality"),
        "postal_code": addr.get("postalCode"),
        "region_code": addr.get("region"),
        "contact_email": contact.get("email"),
        "website": details.get("url"),
        "data_source": "fts",
    })


def upsert_notice(conn: sqlite3.Connection, release: dict, buyer_id: str):
    """Upsert the notice (one row per OCID)."""
    tender = release.get("tender", {})
    bids = release.get("bids", {})
    bid_stats = {s.get("measure"): s.get("value") for s in bids.get("statistics", [])}
    awards = release.get("awards", [])

    # Value — prefer tender estimate
    val = tender.get("value", {})
    amount = val.get("amount")
    amount_gross = val.get("amountGross") or amount

    # Notice URL from documents
    docs = tender.get("documents", [])
    for a in awards:
        docs.extend(a.get("documents", []))
    notice = next((d for d in docs if d.get("format") == "text/html"), {})

    tags = release.get("tag", [])

    # Has renewal?
    has_renewal = any(a.get("hasRenewal") for a in awards)
    renewal_desc = next((a.get("renewal", {}).get("description") for a in awards if a.get("hasRenewal")), None)

    # Framework fields — Decision C06 (added 2026-04-12)
    techniques = tender.get("techniques", {})
    fa = techniques.get("frameworkAgreement", {})
    is_framework = 1 if fa else 0
    framework_method = fa.get("method")
    framework_type = fa.get("type")

    # Parent framework reference (for call-offs referencing their framework)
    parent_framework_ocid = None
    parent_framework_title = None
    for rp in release.get("relatedProcesses", []):
        if "framework" in (rp.get("relationship") or []):
            parent_framework_ocid = rp.get("identifier")
            parent_framework_title = rp.get("title")
            break

    upsert_notice_row(conn, {
        "ocid": release.get("ocid"),
        "buyer_id": buyer_id,
        "latest_release_id": release.get("id"),
        "title": tender.get("title"),
        "description": tender.get("description"),
        "procurement_method": tender.get("procurementMethod"),
        "procurement_method_detail": tender.get("procurementMethodDetails"),
        "main_category": tender.get("mainProcurementCategory") or next(
            (a.get("mainProcurementCategory") for a in awards), None),
        "legal_basis": _safe(tender, "legalBasis", "id"),
        "above_threshold": int(
            tender.get("aboveThreshold") or
            any(a.get("aboveThreshold") for a in awards) or False),
        "value_amount": amount,
        "value_amount_gross": amount_gross,
        "currency": val.get("currency", "GBP"),
        "tender_end_date": _dt(tender.get("tenderPeriod", {}).get("endDate")),
        "published_date": _dt(release.get("date")),
        "tender_status": tender.get("status"),
        "total_bids": bid_stats.get("bids"),
        "final_stage_bids": bid_stats.get("finalStageBids"),
        "sme_bids": bid_stats.get("smeFinalStageBids"),
        "vcse_bids": bid_stats.get("vcseFinalStageBids"),
        "has_renewal": int(has_renewal),
        "renewal_description": renewal_desc,
        "notice_type": notice.get("noticeType"),
        "notice_url": notice.get("url"),
        "latest_tag": ",".join(tags),
        "is_framework": is_framework,
        "framework_method": framework_method,
        "framework_type": framework_type,
        "parent_framework_ocid": parent_framework_ocid,
        "parent_framework_title": parent_framework_title,
        "data_source": "fts",
    })


def upsert_lots(conn: sqlite3.Connection, release: dict):
    """Upsert lots for this notice."""
    ocid = release.get("ocid")
    lots = release.get("tender", {}).get("lots", [])
    for lot in lots:
        lot_id = f"{ocid}-lot-{lot.get('id', '0')}"
        conn.execute("""
            INSERT INTO lots (id, ocid, lot_number, title, description, status, has_options)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=COALESCE(excluded.title, title),
                description=COALESCE(excluded.description, description),
                status=COALESCE(excluded.status, status)
        """, (
            lot_id, ocid, lot.get("id", "0"),
            lot.get("title"), lot.get("description"),
            lot.get("status"), int(lot.get("hasOptions", False)),
        ))


def upsert_awards(conn: sqlite3.Connection, release: dict, supplier_ids: dict):
    """Upsert all awards and their supplier links."""
    ocid = release.get("ocid")
    awards = release.get("awards", [])
    contracts = release.get("contracts", [])
    lots = release.get("tender", {}).get("lots", [])

    # Build contract lookup by award reference
    contract_by_award = {}
    for c in contracts:
        aid = c.get("awardID")
        if aid:
            contract_by_award[aid] = c

    # Build lot criteria lookup
    criteria_by_lot = {}
    for lot in lots:
        criteria_by_lot[lot.get("id")] = _extract_criteria([lot])

    count = 0
    for award in awards:
        award_id = award.get("id")
        if not award_id:
            continue

        # Related lot — only link if we have the lot in this release
        related_lots = award.get("relatedLots", [])
        lot_ref = related_lots[0] if related_lots else None
        candidate_lot_id = f"{ocid}-lot-{lot_ref}" if lot_ref else None
        # Check the lot exists (may have been created in a prior release we haven't seen)
        if candidate_lot_id:
            exists = conn.execute("SELECT 1 FROM lots WHERE id=?", (candidate_lot_id,)).fetchone()
            lot_id = candidate_lot_id if exists else None
        else:
            lot_id = None

        # Contract period — check linked contract first, then award
        linked_contract = contract_by_award.get(award_id, {})
        cp = linked_contract.get("period") or award.get("contractPeriod") or {}

        # Value — prefer award, then linked contract
        val = award.get("value") or linked_contract.get("value") or {}

        # Award criteria from lot
        criteria = criteria_by_lot.get(lot_ref) if lot_ref else None

        # Plausibility flag — any single award >= £10bn is a data error or a
        # framework ceiling misrecorded as an award. See canonical playbook §16.
        amount_gross = val.get("amountGross") or val.get("amount")
        value_quality = "suspect_outlier" if (
            amount_gross is not None and amount_gross >= 10e9
        ) else None

        upsert_award_row(conn, {
            "id": award_id,
            "ocid": ocid,
            "lot_id": lot_id,
            "title": award.get("title"),
            "status": award.get("status"),
            "award_date": _dt(award.get("date")),
            "value_amount": val.get("amount"),
            "value_amount_gross": amount_gross,
            "currency": val.get("currency", "GBP"),
            "contract_start_date": _dt(cp.get("startDate")),
            "contract_end_date": _dt(cp.get("endDate")),
            "contract_max_extend": _dt(cp.get("maxExtentDate")),
            "date_signed": _dt(linked_contract.get("dateSigned")),
            "contract_status": linked_contract.get("status"),
            "award_criteria": criteria,
            "value_quality": value_quality,
            "data_source": "fts",
        })

        # Link suppliers to this award
        # Suppliers may be listed in the award but not in parties — create stubs
        award_suppliers_list = award.get("suppliers", [])
        for sup in award_suppliers_list:
            sup_id = sup.get("id")
            if not sup_id:
                continue
            if sup_id not in supplier_ids:
                # Create a minimal supplier record from award data
                upsert_supplier_row(conn, {"id": sup_id, "name": sup.get("name", "Unknown"), "data_source": "fts"})
                supplier_ids[sup_id] = True
            link_award_supplier(conn, award_id, sup_id)

        count += 1

    return count


def upsert_cpv_codes(conn: sqlite3.Connection, release: dict):
    """Extract and store normalised CPV codes."""
    ocid = release.get("ocid")
    tender = release.get("tender", {})
    items = tender.get("items", [])

    # Also check top-level classification
    top_cls = tender.get("classification", {})
    cpvs = _extract_cpv(items)
    if top_cls.get("scheme") == "CPV" and top_cls.get("id"):
        cpvs.append((top_cls["id"], top_cls.get("description", "")))

    for code, desc in cpvs:
        upsert_cpv_row(conn, ocid, code, desc)


def upsert_planning(conn: sqlite3.Connection, release: dict, buyer_id: str):
    """Upsert a planning / market engagement notice."""
    ocid = release.get("ocid")
    planning = release.get("planning", {})
    tender = release.get("tender", {})
    items = tender.get("items", [])

    milestone = next(
        (m for m in planning.get("milestones", []) if m.get("type") == "engagement"),
        {}
    )
    comm = tender.get("communication", {})
    docs = planning.get("documents", [])
    notice = next((d for d in docs if d.get("format") == "text/html"), {})
    val = tender.get("value", {})

    conn.execute("""
        INSERT INTO planning_notices (
            ocid, buyer_id, title, description,
            engagement_deadline, future_notice_date,
            estimated_value, notice_url, notice_type, published_date
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(ocid) DO UPDATE SET
            future_notice_date=COALESCE(excluded.future_notice_date, future_notice_date),
            engagement_deadline=COALESCE(excluded.engagement_deadline, engagement_deadline),
            estimated_value=COALESCE(excluded.estimated_value, estimated_value),
            notice_url=COALESCE(excluded.notice_url, notice_url)
    """, (
        ocid, buyer_id,
        tender.get("title"), tender.get("description"),
        _dt(milestone.get("dueDate")),
        _dt(comm.get("futureNoticeDate")),
        val.get("amountGross") or val.get("amount"),
        notice.get("url"), notice.get("noticeType"),
        _dt(release.get("date")),
    ))

    # CPV codes for planning notices
    top_cls = tender.get("classification", {})
    cpvs = _extract_cpv(items)
    if top_cls.get("scheme") == "CPV" and top_cls.get("id"):
        cpvs.append((top_cls["id"], top_cls.get("description", "")))

    for code, desc in cpvs:
        conn.execute("""
            INSERT OR IGNORE INTO planning_cpv_codes (ocid, code, description)
            VALUES (?, ?, ?)
        """, (ocid, code, desc))


# ── Release processor ───────────────────────────────────────────────────────

def process_release(conn: sqlite3.Connection, release: dict) -> dict:
    counts = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0, "lots": 0, "planning": 0, "skipped": 0}
    tags = set(release.get("tag", []))
    parties = release.get("parties", [])

    buyer_party = _party(parties, "buyer")
    if not buyer_party:
        counts["skipped"] += 1
        return counts

    # Upsert buyer
    upsert_buyer(conn, buyer_party)
    buyer_id = buyer_party["id"]
    counts["buyers"] += 1

    # Upsert all suppliers (there can be many per release)
    supplier_parties = _all_parties(parties, "supplier")
    supplier_ids = {}
    for sp in supplier_parties:
        sid = upsert_supplier(conn, sp)
        supplier_ids[sid] = True
        counts["suppliers"] += 1

    # Planning / market engagement
    if tags & {"planning", "planningUpdate"}:
        upsert_planning(conn, release, buyer_id)
        counts["planning"] += 1
    else:
        # Notice + lots + awards + CPV codes
        upsert_notice(conn, release, buyer_id)
        counts["notices"] += 1

        lots = release.get("tender", {}).get("lots", [])
        if lots:
            upsert_lots(conn, release)
            counts["lots"] += len(lots)

        awards = release.get("awards", [])
        if awards:
            counts["awards"] += upsert_awards(conn, release, supplier_ids)

        upsert_cpv_codes(conn, release)

    return counts


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PWIN Competitive Intelligence — FTS ingest")
    parser.add_argument("--full",      action="store_true", help="Full re-ingest from 2024-01-01 (incremental mode, no resume)")
    parser.add_argument("--from",      dest="from_date",    help="Custom start date (ISO) — incremental mode")
    parser.add_argument("--backfill",  dest="backfill_from", help="Start a fresh resumable backfill from this date (ISO). Persists progress between runs.")
    parser.add_argument("--resume",    action="store_true", help="Resume an in-progress backfill from saved next-page URL")
    parser.add_argument("--max-pages", dest="max_pages", type=int, help="Stop after N pages (use with --backfill / --resume to chunk long runs)")
    parser.add_argument("--limit",     type=int,            help="Max releases to ingest (testing)")
    args = parser.parse_args()

    conn = get_db(DB_PATH)
    init_schema(conn, SCHEMA_PATH)

    # Two distinct modes:
    #   - backfill mode (--backfill / --resume): persists API next-page URL between runs,
    #     does NOT touch last_cursor (which is the incremental high-water mark)
    #   - incremental mode (--full / --from / no flags): uses last_cursor as updatedFrom,
    #     advances last_cursor to the high-water mark of processed releases
    backfill_mode = bool(args.backfill_from or args.resume)

    start_url = None
    updated_from = None

    if backfill_mode:
        if args.backfill_from and args.resume:
            log.error("Cannot use --backfill and --resume together")
            sys.exit(2)
        if args.backfill_from:
            clear_backfill_url(conn)
            updated_from = args.backfill_from
            log.info("Starting fresh backfill from %s", updated_from)
        else:  # --resume
            start_url = get_backfill_url(conn)
            if not start_url:
                log.error("No saved backfill state to resume — use --backfill <DATE> first")
                sys.exit(2)
            log.info("Resuming backfill from saved next-page URL")
    else:
        # Incremental mode
        if args.full:
            updated_from = "2024-01-01T00:00:00"
            log.info("Full ingest from %s", updated_from)
        elif args.from_date:
            updated_from = args.from_date
            log.info("Custom start: %s", updated_from)
        else:
            stored_cursor = get_cursor(conn)
            if stored_cursor:
                updated_from = stored_cursor
                log.info("Incremental from: %s", updated_from)
            else:
                updated_from = "2025-01-01T00:00:00"
                log.info("First run — starting from %s", updated_from)

    # Counters
    total = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0,
             "lots": 0, "planning": 0, "skipped": 0}
    processed = 0
    batch_size = 50
    high_water = None  # Max release date actually processed — used as next cursor

    # In backfill mode, persist the API's next-page URL after each page
    on_page_done = (lambda u: set_backfill_url(conn, u)) if backfill_mode else None

    try:
        for release in paginate(
            updated_from=updated_from,
            start_url=start_url,
            limit=args.limit,
            max_pages=args.max_pages,
            on_page_done=on_page_done,
        ):
            counts = process_release(conn, release)
            for k, v in counts.items():
                total[k] += v
            processed += 1

            # Track the latest release date we have actually committed.
            # OCDS releases are returned in updated-date order, so the last
            # one we successfully process is our resume point.
            rd = release.get("date")
            if rd and (high_water is None or rd > high_water):
                high_water = rd

            if processed % batch_size == 0:
                conn.commit()
                log.info(
                    "  %d releases | buyers=%d suppliers=%d notices=%d awards=%d lots=%d planning=%d",
                    processed, total["buyers"], total["suppliers"],
                    total["notices"], total["awards"], total["lots"], total["planning"],
                )

        conn.commit()

    except KeyboardInterrupt:
        log.warning("Interrupted — committing progress")
        conn.commit()
    except Exception as e:
        log.error("Ingest aborted with error: %s", e)
        conn.commit()
        raise
    finally:
        if backfill_mode:
            # Backfill manages its own state via backfill_next_url. Do NOT touch
            # last_cursor — that's the incremental high-water mark and would
            # corrupt future incremental runs if we moved it backwards.
            saved = get_backfill_url(conn)
            if saved:
                log.info("Backfill paused — next-page URL persisted, use --resume to continue")
            else:
                log.info("Backfill complete — no more pages")
        else:
            # Only advance the cursor if we actually processed releases.
            # Never jump forward to "now" — if a run dies mid-flight, the cursor
            # must stay where it was so the next run resumes from the gap.
            if high_water:
                cursor_value = high_water[:19].replace(" ", "T")
                set_cursor(conn, cursor_value)
                log.info("Cursor set to %s (high water mark from processed releases)", cursor_value)
            else:
                log.info("No releases processed — cursor unchanged")

        log.info("=" * 60)
        log.info("Ingest complete")
        log.info("  Releases processed : %d", processed)
        log.info("  Buyers upserted    : %d", total["buyers"])
        log.info("  Suppliers upserted : %d", total["suppliers"])
        log.info("  Notices upserted   : %d", total["notices"])
        log.info("  Awards upserted    : %d", total["awards"])
        log.info("  Lots upserted      : %d", total["lots"])
        log.info("  Planning notices   : %d", total["planning"])
        log.info("  Skipped            : %d", total["skipped"])
        conn.close()


if __name__ == "__main__":
    main()
