"""
PWIN Competitive Intelligence — Framework consolidation
=======================================================
Merges framework records from catalogue ingest and call-off mining.
Deduplicates by reference_no (exact) or name (normalised).
Produces a JSON gap report.

Usage:
    python consolidate_frameworks.py              # merge + report
    python consolidate_frameworks.py --report-only # report without merge
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
import db_utils

DB_PATH      = Path(__file__).parent.parent / "db" / "bid_intel.db"
SCHEMA_PATH  = Path(__file__).parent.parent / "db" / "schema.sql"
REPORT_PATH  = Path(__file__).parent.parent / "db" / "framework_consolidation_report.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("consolidate_frameworks")

_PUNCT = re.compile(r'[^\w\s]')
_MULTI_SPACE = re.compile(r'\s+')


def _norm_name(name):
    if not name:
        return ""
    s = _PUNCT.sub(" ", name.lower())
    return _MULTI_SPACE.sub(" ", s).strip()


def consolidate(conn):
    """
    Merge duplicate framework records.

    Pass 1: merge by exact reference_no match.
    Pass 2: merge by normalised name match (where no reference_no).
    """
    merged = 0

    # Pass 1: exact reference_no
    refs = conn.execute(
        "SELECT reference_no FROM frameworks WHERE reference_no IS NOT NULL"
        " GROUP BY reference_no HAVING COUNT(*) > 1"
    ).fetchall()

    for ref_row in refs:
        ref = ref_row[0]
        rows = conn.execute(
            "SELECT id, name, source, call_off_count, call_off_value_total,"
            " description, expiry_date, source_url"
            " FROM frameworks WHERE reference_no=? ORDER BY"
            " CASE source WHEN 'both' THEN 0 WHEN 'catalogue_only' THEN 1 ELSE 2 END",
            (ref,)
        ).fetchall()
        if len(rows) < 2:
            continue

        # Keep first row, merge others into it
        keep = rows[0]
        for dup in rows[1:]:
            # Repoint call-offs, suppliers, lots to the kept record
            conn.execute("""
                UPDATE framework_call_offs SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE framework_suppliers SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE framework_lots SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            # Update kept record with any enriched fields from dup
            new_source = "both" if keep["source"] != dup["source"] else keep["source"]
            conn.execute("""
                UPDATE frameworks SET
                    description = COALESCE(description, ?),
                    expiry_date = COALESCE(expiry_date, ?),
                    source_url  = COALESCE(source_url, ?),
                    source      = ?,
                    last_updated = datetime('now')
                WHERE id = ?
            """, (dup["description"], dup["expiry_date"], dup["source_url"], new_source, keep["id"]))
            conn.execute("DELETE FROM frameworks WHERE id=?", (dup["id"],))
            merged += 1

    conn.commit()

    # Pass 2: normalised name (no reference_no)
    unnamed = conn.execute(
        "SELECT id, name, source, call_off_count, description, expiry_date, source_url"
        " FROM frameworks WHERE reference_no IS NULL"
    ).fetchall()

    groups = {}
    for row in unnamed:
        key = _norm_name(row["name"])
        if key not in groups:
            groups[key] = []
        groups[key].append(row)

    for key, rows in groups.items():
        if len(rows) < 2:
            continue
        # Sort: catalogue_only first (richer data), then contracts_only
        rows_sorted = sorted(rows, key=lambda r: 0 if r["source"] == "catalogue_only" else 1)
        keep = rows_sorted[0]
        for dup in rows_sorted[1:]:
            conn.execute("""
                UPDATE framework_call_offs SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE framework_suppliers SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            conn.execute("""
                UPDATE framework_lots SET framework_id=? WHERE framework_id=?
            """, (keep["id"], dup["id"]))
            new_source = "both" if keep["source"] != dup["source"] else keep["source"]
            conn.execute("""
                UPDATE frameworks SET
                    description = COALESCE(description, ?),
                    expiry_date = COALESCE(expiry_date, ?),
                    source_url  = COALESCE(source_url, ?),
                    source      = ?,
                    last_updated = datetime('now')
                WHERE id = ?
            """, (dup["description"], dup["expiry_date"], dup["source_url"], new_source, keep["id"]))
            conn.execute("DELETE FROM frameworks WHERE id=?", (dup["id"],))
            merged += 1

    conn.commit()

    # Recalculate denormalised counts after all merges
    conn.execute("""
        UPDATE frameworks SET
            call_off_count = (
                SELECT COUNT(*) FROM framework_call_offs WHERE framework_id = frameworks.id
            ),
            call_off_value_total = (
                SELECT COALESCE(SUM(value), 0) FROM framework_call_offs
                WHERE framework_id = frameworks.id AND value IS NOT NULL
            )
    """)
    conn.commit()

    log.info("Consolidation complete: %d duplicate records merged", merged)
    return merged


def build_gap_report(conn):
    """Build a summary report of source coverage gaps."""
    import datetime as _dt
    contracts_only = conn.execute(
        "SELECT name, reference_no, call_off_count, call_off_value_total"
        " FROM frameworks WHERE source='contracts_only'"
        " ORDER BY call_off_value_total DESC"
    ).fetchall()

    catalogue_only = conn.execute(
        "SELECT name, reference_no, expiry_date"
        " FROM frameworks WHERE source='catalogue_only'"
        " ORDER BY name"
    ).fetchall()

    both = conn.execute(
        "SELECT COUNT(*) FROM frameworks WHERE source='both'"
    ).fetchone()[0]

    return {
        "generated_at": _dt.datetime.now().isoformat(),
        "contracts_only_count": len(contracts_only),
        "catalogue_only_count": len(catalogue_only),
        "both_count": both,
        "total": len(contracts_only) + len(catalogue_only) + both,
        "contracts_only": [dict(r) for r in contracts_only],
        "catalogue_only": [dict(r) for r in catalogue_only],
        "notes": {
            "contracts_only": "Frameworks seen in real call-offs but absent from published catalogues. "
                              "Typically departmental frameworks (MoD, Home Office). Enrich manually.",
            "catalogue_only": "Frameworks in the CCS catalogue but with no recorded call-offs. "
                              "May be new, unused, or represent a data coverage gap.",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate framework records")
    parser.add_argument("--report-only", action="store_true",
                        help="Print gap report without merging")
    args = parser.parse_args()

    conn = db_utils.get_db(DB_PATH)
    db_utils.init_schema(conn, SCHEMA_PATH)

    if not args.report_only:
        consolidate(conn)

    report = build_gap_report(conn)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log.info("Gap report written to %s", REPORT_PATH)
    log.info("  contracts_only: %d  catalogue_only: %d  both: %d",
             report["contracts_only_count"],
             report["catalogue_only_count"],
             report["both_count"])
    conn.close()
