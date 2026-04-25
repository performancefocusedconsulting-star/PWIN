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

Steps 4 and 5 are new (added 2026-04-25) — they keep the cleaning current
on every night's load. Without them, the database loads new raw data but
never tags or matches it.

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

    log.info("Nightly pipeline complete")
    sys.exit(0 if fts_rc == 0 else fts_rc)
