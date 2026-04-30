"""
PWIN Competitive Intelligence — Government organogram ingest
============================================================
Fetches senior-staff CSV files from data.gov.uk, parses them,
and upserts stakeholder records into bid_intel.db.

Usage:
    python ingest_organograms.py              # all priority departments
    python ingest_organograms.py --dept hmt   # single department key
    python ingest_organograms.py --limit 3    # cap departments processed
    python ingest_organograms.py --dry-run    # parse only, no DB writes
"""

import argparse
import csv
import io
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.stdout.reconfigure(encoding='utf-8')

from db_utils import get_db, init_schema
from stakeholder_utils import (
    normalise_name, person_id, infer_scs_band, resolve_col,
)

# ── Config ───────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / 'db' / 'bid_intel.db'
SCHEMA_PATH = Path(__file__).parent.parent / 'db' / 'schema.sql'
DATA_GOV_UK_API = 'https://data.gov.uk/api/3/action/package_search'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger('ingest_organograms')

# ── Priority departments (v1 — central government + major ALBs) ──────────────

PRIORITY_DEPARTMENTS = {
    'hmt':              {'query': 'HM Treasury organogram senior staff salaries',                         'canonical_id': 'hm-treasury'},
    'mod':              {'query': 'Ministry of Defence organogram senior staff salaries',                  'canonical_id': 'ministry-of-defence'},
    'dfe':              {'query': 'Department for Education organogram senior staff salaries',             'canonical_id': 'department-for-education'},
    'home-office':      {'query': 'Home Office organogram senior staff salaries',                         'canonical_id': 'home-office'},
    'hmrc':             {'query': 'HMRC organogram senior staff salaries',                                'canonical_id': 'hm-revenue-and-customs'},
    'dhsc':             {'query': 'Department Health Social Care organogram senior staff',                 'canonical_id': 'department-of-health-and-social-care'},
    'mhclg':            {'query': 'Ministry Housing Communities organogram senior staff',                  'canonical_id': 'ministry-of-housing-communities-and-local-government'},
    'dwp':              {'query': 'Department Work Pensions organogram senior staff',                     'canonical_id': 'department-for-work-and-pensions'},
    'moj':              {'query': 'Ministry of Justice organogram senior staff salaries',                  'canonical_id': 'ministry-of-justice'},
    'dcms':             {'query': 'Department Culture Media Sport organogram senior staff',               'canonical_id': 'department-for-culture-media-and-sport'},
    'desnz':            {'query': 'Department Energy Security Net Zero organogram senior staff',          'canonical_id': 'department-for-energy-security-and-net-zero'},
    'dsit':             {'query': 'Department Science Innovation Technology organogram senior staff',     'canonical_id': 'department-for-science-innovation-and-technology'},
    'fcdo':             {'query': 'Foreign Commonwealth Development Office organogram senior staff',      'canonical_id': 'foreign-commonwealth-and-development-office'},
    'cabinet-office':   {'query': 'Cabinet Office organogram senior staff salaries',                     'canonical_id': 'cabinet-office'},
    'dft':              {'query': 'Department for Transport organogram senior staff salaries',            'canonical_id': 'department-for-transport'},
    'defra':            {'query': 'Department Environment Food Rural Affairs organogram senior staff',   'canonical_id': 'department-for-environment-food-and-rural-affairs'},
    'environment-agency': {'query': 'Environment Agency organogram senior staff',                        'canonical_id': 'environment-agency'},
    'ccs':              {'query': 'Crown Commercial Service organogram senior staff',                     'canonical_id': 'crown-commercial-service'},
    'homes-england':    {'query': 'Homes England organogram senior staff',                               'canonical_id': 'homes-england'},
    'ukri':             {'query': 'UK Research Innovation organogram senior staff',                      'canonical_id': 'uk-research-and-innovation'},
}

_REDACTION_MARKERS = frozenset({'N/D', 'ND', 'REDACTED', 'WITHHELD', 'N/A', 'N/D (VPR)', '', '-'})


# ── CSV decoding ─────────────────────────────────────────────────────────────

def _decode(raw: bytes) -> str:
    for enc in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError('Cannot decode CSV with any known encoding')


# ── data.gov.uk discovery ────────────────────────────────────────────────────

def _find_senior_staff_resource(package: dict) -> Optional[dict]:
    resources = package.get('resources', [])
    candidates = [
        r for r in resources
        if 'senior' in (r.get('name') or '').lower()
        or 'senior' in (r.get('url') or '').lower()
    ]
    if not candidates:
        candidates = [
            r for r in resources
            if (r.get('format') or '').upper() in ('CSV', '')
            and 'junior' not in (r.get('name') or '').lower()
        ]
    if not candidates:
        return None
    candidates.sort(
        key=lambda r: r.get('last_modified') or r.get('created') or '',
        reverse=True,
    )
    return candidates[0]


def fetch_organogram_url(query: str) -> Optional[tuple]:
    """Return (csv_url, dataset_url, snapshot_date) or None."""
    params = urlencode({'q': query, 'sort': 'metadata_modified desc', 'rows': 5})
    url = f'{DATA_GOV_UK_API}?{params}'
    try:
        with urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        log.warning('data.gov.uk API error: %s', e)
        return None

    packages = data.get('result', {}).get('results', [])
    if not packages:
        return None

    resource = _find_senior_staff_resource(packages[0])
    if not resource:
        return None

    csv_url = resource.get('url')
    dataset_url = f'https://data.gov.uk/dataset/{packages[0].get("name", "")}'
    modified = resource.get('last_modified') or resource.get('created') or ''
    snapshot_date = modified.split('T')[0] if modified else None
    return csv_url, dataset_url, snapshot_date


def download_csv(url: str) -> Optional[bytes]:
    try:
        req = Request(url, headers={'User-Agent': 'PWIN-Intel/1.0'})
        with urlopen(req, timeout=30) as resp:
            return resp.read()
    except Exception as e:
        log.warning('Download failed %s: %s', url, e)
        return None


# ── Parsing ──────────────────────────────────────────────────────────────────

def parse_organogram_csv(raw_bytes: bytes, source: dict) -> list:
    """Parse a senior-staff CSV, returning a list of stakeholder dicts.

    source dict must contain: canonical_id, source_url, snapshot_date.
    Named rows only — redacted/blank names are skipped.
    """
    text = _decode(raw_bytes)
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    canonical_id = source.get('canonical_id', '')
    results = []

    for row in rows:
        name_raw = resolve_col(row, 'name')
        if not name_raw or name_raw.upper().strip() in _REDACTION_MARKERS:
            continue

        name_norm = normalise_name(name_raw)
        job_title = resolve_col(row, 'job_title')
        unit = resolve_col(row, 'unit')
        organisation = resolve_col(row, 'organisation')
        parent_department = resolve_col(row, 'parent_department')
        reports_to = resolve_col(row, 'reports_to')

        pid = person_id(name_norm, canonical_id)
        band = infer_scs_band(job_title)

        results.append({
            'person_id': pid,
            'name_raw': name_raw,
            'name_normalised': name_norm,
            'job_title': job_title,
            'unit': unit,
            'organisation': organisation,
            'parent_department': parent_department,
            'canonical_buyer_id': canonical_id,
            'scs_band_inferred': band,
            'reports_to_post': reports_to,
            'source': 'organogram',
            'source_url': source.get('source_url'),
            'snapshot_date': source.get('snapshot_date'),
        })

    return results


# ── DB write ─────────────────────────────────────────────────────────────────

def upsert_stakeholder(conn, record: dict):
    """Upsert one stakeholder. If job_title or unit changed, write history."""
    existing = conn.execute(
        'SELECT job_title, unit, canonical_buyer_id FROM stakeholders WHERE person_id = ?',
        (record['person_id'],),
    ).fetchone()

    if existing:
        old_title = existing['job_title'] if hasattr(existing, '__getitem__') else existing[0]
        old_unit = existing['unit'] if hasattr(existing, '__getitem__') else existing[1]
        old_buyer = existing['canonical_buyer_id'] if hasattr(existing, '__getitem__') else existing[2]
        if old_title != record['job_title'] or old_unit != record['unit']:
            conn.execute(
                'INSERT INTO stakeholder_history '
                '(person_id, snapshot_date, job_title, unit, canonical_buyer_id) '
                'VALUES (?, ?, ?, ?, ?)',
                (record['person_id'], record['snapshot_date'],
                 old_title, old_unit, old_buyer),
            )

    conn.execute(
        '''INSERT OR REPLACE INTO stakeholders
           (person_id, name_raw, name_normalised, job_title, unit, organisation,
            parent_department, canonical_buyer_id, scs_band_inferred, reports_to_post,
            source, source_url, snapshot_date, ingested_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
        (
            record['person_id'], record['name_raw'], record['name_normalised'],
            record['job_title'], record['unit'], record['organisation'],
            record['parent_department'], record['canonical_buyer_id'],
            record['scs_band_inferred'], record['reports_to_post'],
            record['source'], record['source_url'], record['snapshot_date'],
        ),
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def run(dept_filter=None, limit=None, dry_run=False):
    conn = get_db(DB_PATH)
    init_schema(conn, SCHEMA_PATH)

    depts = PRIORITY_DEPARTMENTS
    if dept_filter:
        depts = {k: v for k, v in depts.items() if k == dept_filter}
        if not depts:
            log.error('Unknown dept key: %s. Valid keys: %s', dept_filter, list(PRIORITY_DEPARTMENTS))
            return
    if limit:
        depts = dict(list(depts.items())[:limit])

    total = 0
    for dept_id, dept_info in depts.items():
        log.info('Processing %s...', dept_id)

        result = fetch_organogram_url(dept_info['query'])
        if not result:
            log.warning('  No organogram found for %s', dept_id)
            continue

        csv_url, dataset_url, snapshot_date = result
        log.info('  CSV: %s (snapshot %s)', csv_url, snapshot_date)

        raw = download_csv(csv_url)
        if not raw:
            log.warning('  Download failed for %s', dept_id)
            continue

        source = {
            'canonical_id': dept_info['canonical_id'],
            'source_url': dataset_url,
            'snapshot_date': snapshot_date,
        }
        records = parse_organogram_csv(raw, source)
        log.info('  Parsed %d named staff records', len(records))

        if not dry_run:
            for rec in records:
                upsert_stakeholder(conn, rec)
            conn.commit()

        total += len(records)
        log.info('  Done (%d records%s)', len(records), ' -- dry run' if dry_run else '')
        time.sleep(1)

    conn.close()
    log.info('Complete. Total records processed: %d', total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest government organogram CSV files')
    parser.add_argument('--dept', help='Single department key (e.g. hmt, mod, dfe)')
    parser.add_argument('--limit', type=int, help='Max number of departments to process')
    parser.add_argument('--dry-run', action='store_true', help='Parse but do not write to database')
    args = parser.parse_args()
    run(dept_filter=args.dept, limit=args.limit, dry_run=args.dry_run)
