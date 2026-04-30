"""
PWIN Competitive Intelligence — Framework call-off miner
=========================================================
Mines existing notices/awards data for framework references and populates
the frameworks canonical tables.

Three signal types:
  A  parent_framework_title populated (structured field, confidence 1.0)
  B  RM reference number pattern in title/description (confidence 0.9)
  C  Known framework name mention in free text (confidence 0.7)

Usage:
    python mine_framework_calloffs.py           # run against bid_intel.db
    python mine_framework_calloffs.py --dry-run # count matches, no writes
"""

import argparse
import logging
import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
import db_utils

DB_PATH     = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mine_framework_calloffs")

# CCS reference pattern: RM followed by 4-6 digits
_RM_PATTERN = re.compile(r'\bRM\d{4,6}\b', re.IGNORECASE)

# Common punctuation to strip when normalising names
_PUNCT = re.compile(r'[^\w\s]')
_MULTI_SPACE = re.compile(r'\s+')


def _extract_rm_numbers(text):
    """Return all CCS RM reference numbers found in text, uppercased."""
    if not text:
        return []
    return [m.upper() for m in _RM_PATTERN.findall(text)]


def _normalise_fw_name(name):
    """Lowercase, strip punctuation, collapse whitespace."""
    if not name:
        return ""
    s = _PUNCT.sub(" ", name.lower())
    return _MULTI_SPACE.sub(" ", s).strip()


def _upsert_framework(conn, name, reference_no, source="contracts_only"):
    """Insert or return existing framework id. Returns the row id."""
    if reference_no:
        row = conn.execute(
            "SELECT id FROM frameworks WHERE reference_no=?", (reference_no,)
        ).fetchone()
        if row:
            return row[0]
    # Try by normalised name
    norm = _normalise_fw_name(name)
    row = conn.execute(
        "SELECT id FROM frameworks WHERE lower(name)=?", (norm,)
    ).fetchone()
    if row:
        return row[0]
    # Insert skeleton
    conn.execute("""
        INSERT INTO frameworks (name, owner, reference_no, source, last_updated)
        VALUES (?, 'unknown', ?, ?, datetime('now'))
    """, (name, reference_no, source))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def _upsert_call_off(conn, framework_id, notice_ocid, value, awarded_date, title,
                     match_method, match_confidence):
    """Insert call-off if not already recorded for this notice+framework pair."""
    exists = conn.execute(
        "SELECT 1 FROM framework_call_offs WHERE framework_id=? AND notice_ocid=?",
        (framework_id, notice_ocid)
    ).fetchone()
    if exists:
        return
    conn.execute("""
        INSERT INTO framework_call_offs
            (framework_id, notice_ocid, value, awarded_date, contract_title,
             match_method, match_confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (framework_id, notice_ocid, value, awarded_date, title,
          match_method, match_confidence))


def mine_structured_references(conn):
    """
    Signal A: notices with parent_framework_title populated (structured field).
    These come from FTS OCDS data where the contracting authority explicitly
    tagged the parent framework. Confidence = 1.0.
    """
    rows = conn.execute("""
        SELECT n.ocid, n.parent_framework_title, n.parent_framework_ocid,
               a.value_amount_gross, a.award_date, n.title
        FROM notices n
        LEFT JOIN awards a ON a.ocid = n.ocid
        WHERE n.parent_framework_title IS NOT NULL
          AND n.parent_framework_title != ''
    """).fetchall()

    inserted = 0
    for row in rows:
        fw_id = _upsert_framework(
            conn,
            name=row["parent_framework_title"],
            reference_no=row["parent_framework_ocid"],
            source="contracts_only",
        )
        match_method = "reference_no" if row["parent_framework_ocid"] else "structured_field"
        _upsert_call_off(
            conn,
            framework_id=fw_id,
            notice_ocid=row["ocid"],
            value=row["value_amount_gross"],
            awarded_date=row["award_date"],
            title=row["title"],
            match_method=match_method,
            match_confidence=1.0,
        )
        inserted += 1

    conn.commit()
    log.info("Signal A (structured): %d notices processed", inserted)
    return inserted


def mine_rm_patterns(conn):
    """
    Signal B: RM reference number patterns in title or description.
    Skips notices already linked via Signal A (parent_framework_title set).
    Confidence = 0.9.
    """
    rows = conn.execute("""
        SELECT n.ocid, n.title, n.description,
               a.value_amount_gross, a.award_date
        FROM notices n
        LEFT JOIN awards a ON a.ocid = n.ocid
        WHERE (n.parent_framework_title IS NULL OR n.parent_framework_title = '')
          AND (n.title LIKE '%RM%' OR n.description LIKE '%RM%')
    """)

    linked = 0
    for row in rows:
        text = f"{row['title'] or ''} {row['description'] or ''}"
        rm_numbers = _extract_rm_numbers(text)
        for ref in rm_numbers:
            fw_id = _upsert_framework(conn, name=ref, reference_no=ref,
                                      source="contracts_only")
            _upsert_call_off(
                conn,
                framework_id=fw_id,
                notice_ocid=row["ocid"],
                value=row["value_amount_gross"],
                awarded_date=row["award_date"],
                title=row["title"],
                match_method="reference_no",
                match_confidence=0.9,
            )
            linked += 1

    conn.commit()
    log.info("Signal B (RM pattern): %d call-offs linked", linked)
    return linked


def update_summary_counts(conn):
    """
    Update frameworks.call_off_count, call_off_value_total,
    first_call_off_date, last_call_off_date from framework_call_offs.
    """
    conn.execute("""
        UPDATE frameworks SET
            call_off_count = (
                SELECT COUNT(*) FROM framework_call_offs
                WHERE framework_id = frameworks.id
            ),
            call_off_value_total = (
                SELECT COALESCE(SUM(value), 0) FROM framework_call_offs
                WHERE framework_id = frameworks.id AND value IS NOT NULL
            ),
            first_call_off_date = (
                SELECT MIN(awarded_date) FROM framework_call_offs
                WHERE framework_id = frameworks.id
            ),
            last_call_off_date = (
                SELECT MAX(awarded_date) FROM framework_call_offs
                WHERE framework_id = frameworks.id
            ),
            last_updated = datetime('now')
    """)
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM frameworks WHERE call_off_count > 0").fetchone()[0]
    log.info("Summary counts updated: %d frameworks with call-offs", count)


def run(conn, dry_run=False):
    if dry_run:
        a = conn.execute(
            "SELECT COUNT(*) FROM notices WHERE parent_framework_title IS NOT NULL"
            " AND parent_framework_title != ''"
        ).fetchone()[0]
        b = conn.execute(
            "SELECT COUNT(*) FROM notices WHERE (parent_framework_title IS NULL"
            " OR parent_framework_title='') AND (title LIKE '%RM%'"
            " OR description LIKE '%RM%')"
        ).fetchone()[0]
        log.info("DRY RUN — Signal A candidates: %d, Signal B candidates: ~%d", a, b)
        return
    mine_structured_references(conn)
    mine_rm_patterns(conn)
    update_summary_counts(conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mine framework call-off references")
    parser.add_argument("--dry-run", action="store_true",
                        help="Count candidates without writing")
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)
    run(conn, dry_run=args.dry_run)
    conn.close()
