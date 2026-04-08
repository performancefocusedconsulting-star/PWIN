"""
PWIN Competitive Intelligence — OCP Bulk Import
================================================
One-off bulk importer for the Open Contracting Partnership Data Registry
bulk file for the UK Find a Tender Service.

The OCP registry (https://data.open-contracting.org/en/publication/41) publishes
a weekly-refreshed JSONL file containing all UK FTS releases as OCDS "compiled"
releases (one merged record per contract OCID). This script reads that file and
feeds each release through the same process_release() path as the live API
ingest, so parsing and upsert logic stays in one place.

Usage:
    # Download first if not already present:
    curl -L -o data/ocp-uk-fts.jsonl.gz \
      "https://data.open-contracting.org/en/publication/41/download?name=full.jsonl.gz"

    # Then:
    python agent/import_ocp.py                      # full import
    python agent/import_ocp.py --limit 1000         # bounded (testing)
    python agent/import_ocp.py --file <path>        # custom input path

Notes:
    * Compiled releases are tagged "compiled", not "planning", so this import
      contributes zero rows to the planning_notices table. Forward-pipeline
      planning notices continue to flow via the live ingest.py API job.
    * The import is idempotent — all upserts key on OCID / party ID, so
      rerunning is safe and will refresh existing rows with the latest
      compiled-release state.
    * This script does NOT touch the incremental cursor (last_cursor) or any
      backfill state — those belong to the live API ingest.
"""

import argparse
import gzip
import json
import logging
import sys
import time
from pathlib import Path

# Reuse the live ingest's parse + upsert logic so there is one source of truth.
sys.path.insert(0, str(Path(__file__).parent))
import ingest
from ingest import get_db, init_schema, process_release

DEFAULT_FILE = Path(__file__).parent.parent / "data" / "ocp-uk-fts.jsonl.gz"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("import_ocp")


def main():
    parser = argparse.ArgumentParser(description="Import OCP bulk JSONL into the PWIN intel DB")
    parser.add_argument("--file",  default=str(DEFAULT_FILE), help="Path to OCP JSONL.gz file")
    parser.add_argument("--limit", type=int, help="Max records to import (testing)")
    parser.add_argument("--commit-every", type=int, default=1000, help="Commit every N records")
    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.exists():
        log.error("Input file not found: %s", input_path)
        log.error("Download it first with:")
        log.error("  curl -L -o %s \\", input_path)
        log.error("    'https://data.open-contracting.org/en/publication/41/download?name=full.jsonl.gz'")
        sys.exit(1)

    size_mb = input_path.stat().st_size / (1024 * 1024)
    log.info("Input: %s (%.1f MB)", input_path, size_mb)

    conn = get_db(ingest.DB_PATH)
    init_schema(conn)

    # Baseline counts for a clean delta report at the end
    baseline = {}
    for t in ["buyers", "suppliers", "notices", "lots", "awards",
              "planning_notices", "cpv_codes", "award_suppliers"]:
        try:
            baseline[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except Exception:
            baseline[t] = 0

    totals = {"buyers": 0, "suppliers": 0, "notices": 0, "awards": 0,
              "lots": 0, "planning": 0, "skipped": 0}
    processed = 0
    parse_errors = 0
    start = time.time()

    log.info("Beginning import — commit every %d records", args.commit_every)
    try:
        with gzip.open(input_path, "rt", encoding="utf-8") as fp:
            for line in fp:
                if args.limit and processed >= args.limit:
                    log.info("Reached --limit %d — stopping", args.limit)
                    break

                try:
                    release = json.loads(line)
                except json.JSONDecodeError as e:
                    parse_errors += 1
                    if parse_errors <= 5:
                        log.warning("JSON parse error at record %d: %s", processed, e)
                    continue

                try:
                    counts = process_release(conn, release)
                    for k, v in counts.items():
                        totals[k] += v
                    processed += 1
                except Exception as e:
                    log.warning("Upsert failed for ocid=%s: %s", release.get("ocid"), e)
                    continue

                if processed % args.commit_every == 0:
                    conn.commit()
                    elapsed = time.time() - start
                    rate = processed / elapsed if elapsed > 0 else 0
                    log.info(
                        "  %d processed | %.0f rec/s | buyers=%d suppliers=%d notices=%d awards=%d lots=%d skipped=%d",
                        processed, rate, totals["buyers"], totals["suppliers"],
                        totals["notices"], totals["awards"], totals["lots"], totals["skipped"],
                    )

        conn.commit()
    except KeyboardInterrupt:
        log.warning("Interrupted — committing progress")
        conn.commit()

    elapsed = time.time() - start

    # Delta report
    after = {}
    for t in baseline:
        try:
            after[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except Exception:
            after[t] = 0

    log.info("=" * 60)
    log.info("OCP import complete")
    log.info("  Records processed      : %d", processed)
    log.info("  Parse errors           : %d", parse_errors)
    log.info("  Elapsed                : %.1f s", elapsed)
    if elapsed > 0:
        log.info("  Throughput             : %.0f rec/s", processed / elapsed)
    log.info("  Process counters       : %s", totals)
    log.info("")
    log.info("  Table deltas:")
    for t in baseline:
        delta = after[t] - baseline[t]
        log.info("    %-20s %12s  (+%s)", t, f"{after[t]:,}", f"{delta:,}")

    # Date range of notices now that import is done
    try:
        row = conn.execute(
            "SELECT MIN(published_date), MAX(published_date) FROM notices"
        ).fetchone()
        if row and row[0]:
            log.info("")
            log.info("  Notices date range     : %s → %s", row[0], row[1])
    except Exception:
        pass

    conn.close()


if __name__ == "__main__":
    main()
