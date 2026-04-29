"""
Download £25k spend transparency files listed in spend-catalogue.json.

Downloads only files with status='pending' in spend_files_state.
Marks each file 'downloaded' on success, 'error' on failure.
Idempotent — safe to re-run; already-downloaded files are skipped.
"""
import hashlib
import json
import logging
import sqlite3
import time
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)

AGENT_DIR   = Path(__file__).parent
CATALOGUE   = AGENT_DIR / "spend-catalogue.json"
DATA_DIR    = AGENT_DIR.parent / "data" / "spend"
DB_PATH     = AGENT_DIR.parent / "db" / "bid_intel.db"
SCHEMA_PATH = AGENT_DIR.parent / "db" / "schema.sql"

POLITE_DELAY = 1.0   # seconds between requests


# ── File ID ──────────────────────────────────────────────────────────────────

def _file_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


# ── Local path ───────────────────────────────────────────────────────────────

def _local_path(entry: dict) -> Path:
    dept = entry["department"]
    slug = f"{entry['year']}-{entry['month']:02d}"
    if entry.get("entity_override"):
        slug += f"-{entry['entity_override']}"
    ext = ".ods" if entry.get("url", "").endswith(".ods") else ".csv"
    return DATA_DIR / dept / f"{slug}{ext}"


# ── Catalogue loader ─────────────────────────────────────────────────────────

def load_catalogue() -> list[dict]:
    with open(CATALOGUE, encoding="utf-8") as f:
        data = json.load(f)
    # Skip comment-only entries (those with _note but no url)
    return [e for e in data["entries"] if "url" in e]


# ── DB helpers ───────────────────────────────────────────────────────────────

def _open_db() -> sqlite3.Connection:
    import db_utils
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    db_utils.init_schema(conn, SCHEMA_PATH)
    return conn


def _ensure_state_rows(conn: sqlite3.Connection, entries: list[dict]) -> None:
    """Insert a spend_files_state row for each catalogue entry if not present."""
    for e in entries:
        fid = _file_id(e["url"])
        conn.execute(
            "INSERT OR IGNORE INTO spend_files_state "
            "(id, department, year, month, entity_override, source_url, format_id, status) "
            "VALUES (?,?,?,?,?,?,?,'pending')",
            (fid, e["department"], e["year"], e["month"],
             e.get("entity_override"), e["url"], e["format_id"])
        )
    conn.commit()


def _pending(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM spend_files_state WHERE status='pending'"
    ).fetchall()


def _mark(conn: sqlite3.Connection, fid: str, status: str,
          local_path: str = None, checksum: str = None, error: str = None) -> None:
    conn.execute(
        "UPDATE spend_files_state SET status=?, local_path=?, file_checksum=?, "
        "error_message=?, loaded_at=datetime('now') WHERE id=?",
        (status, local_path, checksum, error, fid)
    )
    conn.commit()


# ── Download ─────────────────────────────────────────────────────────────────

def _checksum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(row: sqlite3.Row, entry_map: dict) -> tuple[str, str | None, str | None]:
    """
    Download one file. Returns (status, local_path, error_message).
    """
    url   = row["source_url"]
    entry = entry_map.get(url, {})
    dest  = _local_path({
        "department":     row["department"],
        "year":           row["year"],
        "month":          row["month"],
        "entity_override": row["entity_override"],
        "url":            url,
    })
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "PWIN-spend-ingest/1.0 (internal research tool)"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        dest.write_bytes(data)
        cs = _checksum(dest)
        log.info("Downloaded %s → %s (%d bytes)", url, dest, len(data))
        return "downloaded", str(dest), cs
    except Exception as exc:
        log.error("Failed to download %s: %s", url, exc)
        return "error", None, str(exc)


# ── Main ─────────────────────────────────────────────────────────────────────

def run(dry_run: bool = False) -> None:
    entries    = load_catalogue()
    entry_map  = {e["url"]: e for e in entries}
    conn       = _open_db()

    _ensure_state_rows(conn, entries)
    pending = _pending(conn)
    log.info("%d files pending download", len(pending))

    for i, row in enumerate(pending):
        if dry_run:
            log.info("[dry-run] would download %s", row["source_url"])
            continue

        status, path, extra = _download(row, entry_map)
        _mark(conn, row["id"], status, local_path=path,
              checksum=extra if status == "downloaded" else None,
              error=extra if status == "error" else None)

        if i < len(pending) - 1:
            time.sleep(POLITE_DELAY)

    conn.close()
    log.info("Fetch complete")


if __name__ == "__main__":
    import argparse
    import sys
    sys.path.insert(0, str(AGENT_DIR))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="Download £25k spend transparency files")
    p.add_argument("--dry-run", action="store_true", help="Show what would be downloaded without downloading")
    args = p.parse_args()
    run(dry_run=args.dry_run)
