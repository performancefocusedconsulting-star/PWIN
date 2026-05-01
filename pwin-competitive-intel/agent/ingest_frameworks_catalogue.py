"""
PWIN Competitive Intelligence — Framework catalogue ingest
==========================================================
Pulls UK government framework agreements from published catalogues
(Crown Commercial Service primary; NHS and local gov in Wave 2).

The HTTP layer is injectable for testing. Parsers accept raw HTML strings.

Usage:
    python ingest_frameworks_catalogue.py              # full CCS catalogue
    python ingest_frameworks_catalogue.py --limit 10   # first 10 agreements
    python ingest_frameworks_catalogue.py --dry-run    # parse only, no writes
    python ingest_frameworks_catalogue.py --url <url>  # single agreement

NOTE: CSS selectors are based on CCS site structure as of 2026-04. Run with
--dry-run on first use to verify the parser is producing sensible output
before committing to the database.
"""

import argparse
import logging
import re
import sqlite3
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
import db_utils

DB_PATH     = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"

CCS_BASE        = "https://www.crowncommercial.gov.uk"
CCS_LIST_URL    = f"{CCS_BASE}/agreements"
REQUEST_DELAY   = 1.5   # seconds between requests — polite crawling

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest_frameworks_catalogue")

_MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}


def _parse_date(text):
    """Convert various date formats to ISO YYYY-MM-DD. Returns None on failure."""
    if not text:
        return None
    text = text.strip()
    if not text:
        return None
    # Already ISO
    if len(text) == 10 and text[4] == "-":
        return text
    # DD/MM/YYYY (GCA site format)
    if re.match(r'\d{2}/\d{2}/\d{4}$', text):
        d, m, y = text.split('/')
        return f"{y}-{m}-{d}"
    # "31 March 2027" format
    parts = text.lower().split()
    if len(parts) == 3:
        month = _MONTH_MAP.get(parts[1]) or next(
            (v for k, v in _MONTH_MAP.items() if k.startswith(parts[1])), None
        )
        if month:
            try:
                return f"{parts[2]}-{month}-{int(parts[0]):02d}"
            except ValueError:
                pass
    return None


def _fetch_url(url, timeout=30):
    """Fetch URL and return HTML as string. Raises on HTTP error."""
    req = Request(url, headers={"User-Agent": "PWIN-Competitive-Intel/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ── CCS HTML parsers ──────────────────────────────────────────────────────────

class _LinkCollector(HTMLParser):
    """Collects href values from <a> tags inside a named class container."""
    def __init__(self, container_class, href_prefix):
        super().__init__()
        self.container_class = container_class
        self.href_prefix = href_prefix
        self.links = []
        self._in_container = False
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class") or ""
        if self.container_class in cls:
            self._in_container = True
            self._depth = 0
        if self._in_container:
            self._depth += 1
            if tag == "a":
                href = attrs.get("href", "")
                if href.startswith(self.href_prefix):
                    self.links.append(href)

    def handle_endtag(self, tag):
        if self._in_container:
            self._depth -= 1
            if self._depth <= 0:
                self._in_container = False


def parse_ccs_list(html, base_url=CCS_BASE):
    """
    Extract absolute URLs for individual agreement pages from the CCS list page.
    Returns a list of full URLs.

    NOTE: Adjust container_class if the CCS list page structure has changed.
    """
    collector = _LinkCollector(
        container_class="agreements-list",
        href_prefix="/agreements/",
    )
    collector.feed(html)
    # Fall back to RM-prefixed /agreements/<ref> links (CCS convention for real frameworks)
    if not collector.links:
        paths = re.findall(r'href="(/agreements/RM[0-9][a-zA-Z0-9.\-]*)"', html)
        collector.links = list(dict.fromkeys(paths))  # deduplicate preserving order
    return [f"{base_url}{path}" for path in collector.links]


class _AgreementParser(HTMLParser):
    """
    Parses a single GCA (formerly CCS) agreement detail page.
    Extracts: name, reference_no, expiry_date, description, lots.

    GCA site structure (as of 2026-04):
    - Name: <h1 class="...page-title...">
    - Description: <div class="govuk-body-l"> (first one after h1)
    - Reference/dates: <dt>Agreement ID</dt><dd>RM6348</dd> in Key Facts aside
    - Lots: <span class="apollo-list--definition__key__inner">Lot 1a: Name</span>
    """
    def __init__(self):
        super().__init__()
        self.name = None
        self.reference_no = None
        self.expiry_date_raw = None
        self.description = None
        self.lots = []
        self._capture = None
        self._desc_depth = 0
        self._in_dt = False
        self._last_dt_text = ""
        self._in_dd = False
        self._dd_key = None
        self._in_lot_span = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class") or ""

        if tag == "h1" and "page-title" in cls:
            self._capture = "name"
        elif tag == "div":
            if "govuk-body-l" in cls and self.name and self.description is None:
                self._capture = "description"
                self._desc_depth = 1
            elif self._capture == "description":
                self._desc_depth += 1
        elif tag == "dt":
            self._in_dt = True
            self._last_dt_text = ""
        elif tag == "dd":
            self._in_dd = True
            if "apollo-list--definition__value" in cls:
                self._dd_key = self._last_dt_text
            else:
                self._dd_key = None
        elif tag == "span" and "apollo-list--definition__key__inner" in cls:
            self._in_lot_span = True

    def handle_endtag(self, tag):
        if tag == "h1" and self._capture == "name":
            self._capture = None
        elif tag == "div" and self._capture == "description":
            self._desc_depth -= 1
            if self._desc_depth == 0:
                self._capture = None
        elif tag == "dt":
            self._in_dt = False
        elif tag == "dd":
            self._in_dd = False
            self._dd_key = None
        elif tag == "span" and self._in_lot_span:
            self._in_lot_span = False

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        if self._capture == "name":
            self.name = (self.name or "") + data
        elif self._capture == "description":
            self.description = (self.description or "") + data
        elif self._in_lot_span:
            m = re.match(r'Lot\s+([0-9]+[a-zA-Z]*)\s*[:\-]\s*(.*)', data, re.IGNORECASE)
            if m:
                self.lots.append({
                    "lot_number": m.group(1),
                    "lot_name": m.group(2).strip(),
                    "scope": None,
                })
        elif self._in_dt:
            self._last_dt_text = data
        elif self._in_dd and self._dd_key:
            if self._dd_key == "Agreement ID" and not self.reference_no:
                self.reference_no = data
            elif self._dd_key == "End date" and not self.expiry_date_raw:
                self.expiry_date_raw = data


def parse_ccs_agreement(html):
    """
    Parse a CCS agreement detail page. Returns a dict with:
    name, reference_no, expiry_date (ISO), description, lots (list of dicts).
    """
    parser = _AgreementParser()
    parser.feed(html)

    # Strip RM prefix noise from reference_no if present
    ref = parser.reference_no
    if ref:
        ref = ref.strip()
        # Normalise to uppercase RM format
        m = re.search(r'RM\d{4,6}', ref, re.IGNORECASE)
        ref = m.group(0).upper() if m else ref

    return {
        "name": (parser.name or "").strip() or None,
        "reference_no": ref,
        "expiry_date": _parse_date(parser.expiry_date_raw),
        "description": (parser.description or "").strip() or None,
        "lots": parser.lots,
    }


# ── Database write ────────────────────────────────────────────────────────────

def _upsert_catalogue_framework(conn, data, source_url):
    """
    Insert or update a framework record from catalogue data.
    If the record already exists (by reference_no), updates catalogue fields.
    Sets source = 'both' if it was previously 'contracts_only'.
    """
    if not data.get("name"):
        return None

    existing = None
    if data.get("reference_no"):
        existing = conn.execute(
            "SELECT id, source FROM frameworks WHERE reference_no=?",
            (data["reference_no"],)
        ).fetchone()

    if not existing:
        existing = conn.execute(
            "SELECT id, source FROM frameworks WHERE lower(name)=lower(?)",
            (data["name"],)
        ).fetchone()

    new_source = "both" if (existing and existing["source"] in ("contracts_only", "both")) else "catalogue_only"

    if existing:
        conn.execute("""
            UPDATE frameworks SET
                name         = COALESCE(?, name),
                reference_no = COALESCE(?, reference_no),
                expiry_date  = COALESCE(?, expiry_date),
                description  = COALESCE(?, description),
                owner        = 'Crown Commercial Service',
                owner_type   = 'central_gov',
                source       = ?,
                source_url   = ?,
                last_updated = datetime('now')
            WHERE id = ?
        """, (data["name"], data.get("reference_no"), data.get("expiry_date"),
              data.get("description"), new_source, source_url, existing["id"]))
        fw_id = existing["id"]
    else:
        conn.execute("""
            INSERT INTO frameworks
                (name, reference_no, owner, owner_type, expiry_date,
                 description, source, source_url, last_updated)
            VALUES (?, ?, 'Crown Commercial Service', 'central_gov',
                    ?, ?, 'catalogue_only', ?, datetime('now'))
        """, (data["name"], data.get("reference_no"), data.get("expiry_date"),
              data.get("description"), source_url))
        fw_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    for lot in data.get("lots", []):
        conn.execute("""
            INSERT OR IGNORE INTO framework_lots
                (framework_id, lot_number, lot_name, scope)
            VALUES (?, ?, ?, ?)
        """, (fw_id, lot.get("lot_number"), lot.get("lot_name"), lot.get("scope")))

    conn.execute("""
        UPDATE frameworks SET lot_count = (
            SELECT COUNT(*) FROM framework_lots WHERE framework_id = ?
        ) WHERE id = ?
    """, (fw_id, fw_id))

    conn.commit()
    return fw_id


# ── Main run ──────────────────────────────────────────────────────────────────

def run(conn, dry_run=False, limit=None, fetch_fn=_fetch_url):
    """
    Fetch the CCS agreements list, then fetch and parse each agreement.
    fetch_fn is injectable for testing.
    """
    log.info("Fetching CCS agreements list from %s", CCS_LIST_URL)
    try:
        list_html = fetch_fn(CCS_LIST_URL)
    except (HTTPError, URLError) as e:
        log.error("Failed to fetch CCS list: %s", e)
        return 0

    urls = parse_ccs_list(list_html)
    log.info("Found %d agreement URLs", len(urls))

    if limit:
        urls = urls[:limit]

    ingested = 0
    for i, url in enumerate(urls):
        time.sleep(REQUEST_DELAY)
        try:
            html = fetch_fn(url)
        except (HTTPError, URLError) as e:
            log.warning("Failed to fetch %s: %s", url, e)
            continue

        data = parse_ccs_agreement(html)
        if not data.get("name"):
            log.warning("No name parsed from %s — skipping", url)
            continue

        if dry_run:
            log.info("DRY RUN [%d/%d]: %s (%s) expiry=%s lots=%d",
                     i + 1, len(urls), data["name"], data.get("reference_no"),
                     data.get("expiry_date"), len(data.get("lots", [])))
        else:
            _upsert_catalogue_framework(conn, data, source_url=url)
            log.info("[%d/%d] Ingested: %s (%s)",
                     i + 1, len(urls), data["name"], data.get("reference_no"))

        ingested += 1

    log.info("Catalogue ingest complete: %d agreements processed", ingested)
    return ingested


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest framework catalogue from CCS")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--url", type=str, default=None,
                        help="Parse a single agreement URL")
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)

    if args.url:
        html = _fetch_url(args.url)
        data = parse_ccs_agreement(html)
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        run(conn, dry_run=args.dry_run, limit=args.limit)

    conn.close()
