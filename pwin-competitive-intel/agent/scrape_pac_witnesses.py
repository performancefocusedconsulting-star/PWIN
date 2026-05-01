"""
PWIN Competitive Intelligence — PAC witness list scraper
========================================================
Scrapes Public Accounts Committee oral evidence sessions, extracts witness
names and organisations, and upserts into pac_witnesses in bid_intel.db.

Witness data is embedded directly in the listing page at:
  /committee/127/public-accounts-committee/publications/oral-evidence/

Each card contains: date (primary-info), inquiry title, and a
  <span class="label">Witnesses</span> block in the format:
  "Name (Role at Organisation), Name (Role at Organisation), and Name (...)"

No individual session pages need to be fetched.

Usage:
    python scrape_pac_witnesses.py              # all sessions on listing page
    python scrape_pac_witnesses.py --dry-run    # parse only, no DB writes
    python scrape_pac_witnesses.py --months 6   # filter to sessions within N months

PAC oral evidence listing:
  https://committees.parliament.uk/committee/127/public-accounts-committee/publications/oral-evidence/
"""

import argparse
import logging
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding='utf-8')

from db_utils import get_db, init_schema
from stakeholder_utils import normalise_name, slug

# ── Config ───────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / 'db' / 'bid_intel.db'
SCHEMA_PATH = Path(__file__).parent.parent / 'db' / 'schema.sql'
PAC_BASE = 'https://committees.parliament.uk'
PAC_LISTING = (
    f'{PAC_BASE}/committee/127/public-accounts-committee/publications/oral-evidence/'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger('scrape_pac')


# ── HTML fetching ─────────────────────────────────────────────────────────────

def _fetch(url: str) -> Optional[str]:
    try:
        req = Request(url, headers={
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
        })
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        log.warning('Fetch failed %s: %s', url, e)
        return None


# ── Witness parsing ───────────────────────────────────────────────────────────

# Matches "Name (Role at Organisation)" — handles:
#   "Jo Shanmugalingam (Permanent Secretary at Department for Transport)"
#   "Tom Riordan CBE (Northern Growth Envoy at HM Treasury)"
# The [A-Z] anchor skips leading "and " (lowercase).
_WITNESS_ENTRY_RE = re.compile(
    r"([A-Z][A-Za-z '\-]+?)\s*\(([^)]+)\)"
)


def _parse_witness_entry(name_raw: str, content: str) -> dict:
    """Parse role and organisation from the parenthetical content.

    content examples:
      "Permanent Secretary at HM Treasury"
      "Director General, Tax and Welfare at HM Treasury"
      "Chief Operating Officer at Department for Culture, Media and Sport"
    """
    name_raw = name_raw.strip()
    name_norm = normalise_name(name_raw)
    role_title = None
    organisation = content.strip()

    if ' at ' in content:
        idx = content.index(' at ')
        role_title = content[:idx].strip()
        organisation = content[idx + 4:].strip()

    return {
        'name_raw': name_raw,
        'name_normalised': name_norm,
        'role_title': role_title,
        'organisation': organisation,
    }


def parse_witnesses_html(
    html: str,
    session_date: str,
    session_title: str,
    session_url: str,
) -> list:
    """Extract witnesses from a PAC session card HTML fragment or listing page.

    Looks for <span class="label">Witnesses</span> blocks and parses each
    "Name (Role at Organisation)" entry. session_date / session_title /
    session_url are caller-supplied metadata (they come from the card context,
    not the inner witness text).

    Returns a list of witness dicts ready for upsert.
    """
    results = []

    # Extract all Witnesses label blocks from the HTML
    witness_blocks = re.findall(
        r'<span[^>]*\blabel\b[^>]*>Witnesses</span>(.*?)(?:</div>|<div)',
        html,
        re.DOTALL | re.IGNORECASE,
    )

    for block in witness_blocks:
        # Strip any residual HTML tags from within the block
        clean = re.sub(r'<[^>]+>', '', block)
        matches = _WITNESS_ENTRY_RE.findall(clean)
        for name_raw, content in matches:
            parsed = _parse_witness_entry(name_raw, content)
            if not parsed['name_normalised'] or len(parsed['name_normalised']) < 3:
                continue
            witness_id = f'{slug(parsed["name_normalised"])}--{session_date}'
            results.append({
                'witness_id': witness_id,
                'name_raw': parsed['name_raw'],
                'name_normalised': parsed['name_normalised'],
                'role_title': parsed['role_title'],
                'organisation': parsed['organisation'],
                'canonical_buyer_id': None,  # resolved at upsert time
                'session_date': session_date,
                'session_title': session_title,
                'session_url': session_url,
            })

    return results


# ── Session listing ───────────────────────────────────────────────────────────

_DATE_FORMATS = ['%d %B %Y', '%d %b %Y']


def _parse_date(text: str) -> Optional[str]:
    """Parse a date string like '28 April 2026' to 'YYYY-MM-DD'."""
    t = text.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(t, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


def _extract_session_cards(html: str, months_back: int = 0) -> list:
    """Extract session cards from the PAC oral evidence listing page.

    Returns list of dicts with: session_date, session_title, session_url,
    witnesses_html (the card HTML snippet for parsing witnesses).
    """
    cutoff = None
    if months_back > 0:
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=months_back * 30)

    cards = re.split(r'(?=<div[^>]+class="card card-button card-publication)', html)
    results = []

    for card in cards:
        # Extract date from primary-info div
        date_m = re.search(r'<div[^>]*primary-info[^>]*>([^<]+)</div>', card)
        if not date_m:
            continue
        date_str = _parse_date(date_m.group(1))
        if not date_str:
            continue

        # Apply date filter
        if cutoff:
            try:
                if datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc) < cutoff:
                    continue
            except ValueError:
                pass

        # Extract inquiry title
        inquiry_m = re.search(
            r'<span[^>]*\blabel\b[^>]*>Inquiry</span>\s*(.*?)(?:</div>|<div)',
            card, re.DOTALL | re.IGNORECASE,
        )
        title = re.sub(r'<[^>]+>', '', inquiry_m.group(1)).strip() if inquiry_m else 'PAC session'

        # Build session URL from oralevidence ID in card links
        oe_m = re.search(r'/oralevidence/(\d+)/', card)
        session_url = f'{PAC_BASE}/oralevidence/{oe_m.group(1)}/html/' if oe_m else PAC_LISTING

        results.append({
            'session_date': date_str,
            'session_title': title,
            'session_url': session_url,
            'card_html': card,
        })

    return results


# ── Canonical buyer resolution ─────────────────────────────────────────────────

def _resolve_buyer(conn, organisation: Optional[str]) -> Optional[str]:
    """Return canonical_buyer_id for an organisation name, or None."""
    if not organisation:
        return None
    q = organisation.strip().lower()
    row = conn.execute(
        'SELECT canonical_id FROM canonical_buyer_aliases WHERE alias_lower = ?', (q,)
    ).fetchone()
    if row:
        return row[0]
    rows = conn.execute(
        'SELECT canonical_id FROM canonical_buyers WHERE LOWER(canonical_name) LIKE ? LIMIT 2',
        (f'%{q}%',),
    ).fetchall()
    if len(rows) == 1:
        return rows[0][0]
    return None


# ── DB write ─────────────────────────────────────────────────────────────────

def upsert_witness(conn, record: dict):
    conn.execute(
        '''INSERT OR REPLACE INTO pac_witnesses
           (witness_id, name_raw, name_normalised, role_title, organisation,
            canonical_buyer_id, session_date, session_title, session_url, scraped_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
        (
            record['witness_id'], record['name_raw'], record['name_normalised'],
            record['role_title'], record['organisation'],
            record['canonical_buyer_id'],
            record['session_date'], record['session_title'], record['session_url'],
        ),
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def run(months=0, dry_run=False):
    conn = get_db(DB_PATH)
    init_schema(conn, SCHEMA_PATH)

    log.info('Fetching PAC oral evidence listing...')
    html = _fetch(PAC_LISTING)
    if not html:
        log.error('Cannot fetch PAC listing')
        conn.close()
        return

    cards = _extract_session_cards(html, months_back=months)
    log.info('Found %d session cards', len(cards))

    total = 0
    for card in cards:
        witnesses = parse_witnesses_html(
            card['card_html'],
            session_date=card['session_date'],
            session_title=card['session_title'],
            session_url=card['session_url'],
        )
        log.info('  %s — %s: %d witnesses', card['session_date'], card['session_title'][:60], len(witnesses))

        for w in witnesses:
            w['canonical_buyer_id'] = _resolve_buyer(conn, w['organisation'])
            if not dry_run:
                upsert_witness(conn, w)
            total += 1

    if not dry_run:
        conn.commit()

    conn.close()
    log.info('Done. Total witness records: %d', total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape PAC witness lists from oral evidence listing page')
    parser.add_argument('--months', type=int, default=0, help='Filter to sessions within N months (default: all on page)')
    parser.add_argument('--dry-run', action='store_true', help='Parse but do not write to database')
    args = parser.parse_args()
    run(months=args.months, dry_run=args.dry_run)
