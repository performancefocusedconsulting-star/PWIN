#!/usr/bin/env python3
"""
PWIN Competitive Intelligence — Nightly Scheduler
==================================================
Single source of truth for the nightly pipeline. Both the local Windows
nightly.bat and the GitHub Actions workflow call this script.

Pipeline (all incremental — safe to re-run):
  1. Load new Find a Tender contracts          (ingest.py)
  2. Load new Contracts Finder contracts       (ingest_cf.py — non-fatal)
  3. Enrich suppliers from Companies House     (enrich-ch.py --limit 200)
  4. Tag new big contracts with service        (classify-by-cpv.py --only-untagged)
     categories using procurement codes
  5. Match new buyers to the master list       (fuzzy-match-buyers.py
     using fuzzy matching at threshold 95       --threshold 95 --apply)
  6. Daily pipeline scan (triage into BOOK /   (run-pipeline-scan.py --hours 24)
     QUALIFY / INTEL / WATCH)
  7. £25k spend transparency ingest            (ingest_spend.py — non-fatal)
  8. Framework call-off mining                 (mine_framework_calloffs.py — non-fatal)

Optional (pass --with-frameworks-catalogue):
  9. CCS framework catalogue ingest            (ingest_frameworks_catalogue.py)
 10. Framework consolidation / dedup           (consolidate_frameworks.py)

Optional (pass --with-organograms, run twice-yearly):
 11. Organogram ingest — senior civil servants (ingest_organograms.py)
     Published by each department ~March and ~September. Re-running is safe
     (idempotent upsert; changed roles are written to stakeholder_history).

NOT in this nightly:
  - Splink supplier matching (full wipe-and-replace, ~13 min) — run monthly
    or after large bulk imports:
      .venv/Scripts/python.exe agent/splink_supplier_dedup.py

Each step except step 1 is non-fatal (a failure logs and continues).
The exit code is non-zero only if the FTS ingest itself failed.

Direct:  python agent/scheduler.py
Cron:    0 2 * * * cd /path/to/pwin-competitive-intel && python agent/scheduler.py
"""

import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / f"ingest_{datetime.now().strftime('%Y%m')}.log"),
    ],
)
log = logging.getLogger("scheduler")

AGENT_DIR = Path(__file__).parent


def run_step(label: str, args: list[str], fatal: bool = False) -> int:
    log.info("=" * 60)
    log.info("STEP: %s", label)
    log.info("=" * 60)
    cmd = [sys.executable] + args
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode == 0:
        log.info("%s: completed", label)
    elif fatal:
        log.error("%s: failed (exit %d) — fatal", label, result.returncode)
    else:
        log.warning("%s: failed (exit %d) — continuing", label, result.returncode)
    return result.returncode


if __name__ == "__main__":
    import argparse as _ap
    _parser = _ap.ArgumentParser()
    _parser.add_argument("--with-frameworks-catalogue", action="store_true",
                         help="Also run the monthly CCS catalogue ingest")
    _parser.add_argument("--with-organograms", action="store_true",
                         help="Also run the twice-yearly organogram ingest (senior civil servants)")
    _args = _parser.parse_args()

    log.info("Nightly pipeline starting")

    fts_rc = run_step("Find a Tender ingest",
                      [str(AGENT_DIR / "ingest.py")], fatal=True)

    run_step("Contracts Finder ingest",
             [str(AGENT_DIR / "ingest_cf.py")])

    run_step("Companies House enrichment (200/night)",
             [str(AGENT_DIR / "enrich-ch.py"), "--limit", "200"])

    run_step("Service-category tagging (procurement codes, incremental)",
             [str(AGENT_DIR / "classify-by-cpv.py"), "--only-untagged"])

    run_step("Buyer fuzzy matching (threshold 95)",
             [str(AGENT_DIR / "fuzzy-match-buyers.py"), "--threshold", "95", "--apply"])

    # Daily pipeline scan: triage last 24h of new notices into BOOK / QUALIFY /
    # INTEL / WATCH, write Obsidian pursuit files for actionable items, upsert
    # crm.db, save digest. Email send is a separate step (Gmail token).
    # Non-fatal — a failed scan must not stop the data pipeline.
    run_step("Daily pipeline scan (Agent 2 triage)",
             [str(AGENT_DIR / "run-pipeline-scan.py"), "--hours", "24"])

    # £25k spend transparency: download any new files from the catalogue,
    # parse into spend_transactions, canonicalise entity + supplier names.
    # Non-fatal — a failure here must not stop the core data pipeline.
    run_step("Spend transparency: parse downloaded files + canonicalise",
             [str(AGENT_DIR / "ingest_spend.py")])

    # Framework call-off mining: links newly ingested contracts to the frameworks
    # canonical layer. Non-fatal — a failure here must not stop the core pipeline.
    run_step("Framework call-off mining",
             [str(AGENT_DIR / "mine_framework_calloffs.py")])

    # Twice-yearly: organogram ingest (run with --with-organograms, ~March and ~September)
    if _args.with_organograms:
        run_step("Organogram ingest (senior civil servants, all priority departments)",
                 [str(AGENT_DIR / "ingest_organograms.py")])

    # Monthly: CCS catalogue ingest (run with --with-frameworks-catalogue)
    if _args.with_frameworks_catalogue:
        run_step("CCS framework catalogue ingest",
                 [str(AGENT_DIR / "ingest_frameworks_catalogue.py")])
        run_step("Framework consolidation",
                 [str(AGENT_DIR / "consolidate_frameworks.py")])

    log.info("Nightly pipeline complete")
    sys.exit(0 if fts_rc == 0 else fts_rc)
