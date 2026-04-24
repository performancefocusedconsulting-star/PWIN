#!/usr/bin/env python3
"""
PWIN Competitive Intelligence — Scheduler
==========================================
Nightly wrapper: FTS ingest → CF ingest → (CH enrichment run separately).
CF failure is non-fatal; FTS failure causes non-zero exit.

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

INGEST_SCRIPT    = Path(__file__).parent / "ingest.py"
INGEST_CF_SCRIPT = Path(__file__).parent / "ingest_cf.py"


def run_script(script: Path, label: str) -> int:
    log.info("Starting %s", label)
    result = subprocess.run([sys.executable, str(script)], capture_output=False)
    if result.returncode == 0:
        log.info("%s completed successfully", label)
    else:
        log.error("%s failed with exit code %d", label, result.returncode)
    return result.returncode


if __name__ == "__main__":
    fts_rc = run_script(INGEST_SCRIPT, "FTS ingest")
    cf_rc  = run_script(INGEST_CF_SCRIPT, "CF ingest")  # non-fatal in v1
    if cf_rc != 0:
        log.warning("CF ingest failed — continuing (non-fatal)")
    sys.exit(0 if fts_rc == 0 else fts_rc)
