#!/usr/bin/env python3
"""
PWIN Competitive Intelligence — Scheduler
==========================================
Wrapper for cron / GitHub Actions. Runs incremental ingest.

Direct:     python scheduler.py
Cron:       0 2 * * * cd /path/to/pwin-competitive-intel && python agent/scheduler.py >> logs/ingest.log 2>&1
"""

import subprocess
import sys
import logging
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

INGEST_SCRIPT = Path(__file__).parent / "ingest.py"


def run_ingest():
    log.info("Starting scheduled ingest run")
    result = subprocess.run(
        [sys.executable, str(INGEST_SCRIPT)],
        capture_output=False,
    )
    if result.returncode == 0:
        log.info("Ingest completed successfully")
    else:
        log.error("Ingest failed with exit code %d", result.returncode)
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_ingest())
