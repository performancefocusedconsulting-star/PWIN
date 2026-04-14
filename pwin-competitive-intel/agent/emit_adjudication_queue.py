#!/usr/bin/env python3
"""Emit the supplier adjudication queue for the Morgan Ledger skill.

Reads bid_intel.db, re-runs Splink at a low predict threshold (0.4) to capture
pairs in the mid-band that didn't make the 0.95 clustering cut, aggregates them
up to canonical-pair level, and writes an `adjudication_queue` staging table.

This is decoupled from splink_supplier_dedup.py on purpose: the main pipeline
ships canonical_suppliers at the strict 0.95 threshold and must stay stable.
This script only reads raw suppliers + canonical mappings and writes the
staging queue — it never mutates canonical_suppliers.

Output table: adjudication_queue
  queue_id               TEXT PK       — stable hash(left_canonical, right_canonical)
  decision_type          TEXT          — 'supplier_merge' for V1
  left_canonical_id      TEXT
  right_canonical_id     TEXT
  left_name              TEXT
  right_name             TEXT
  left_member_count      INTEGER
  right_member_count     INTEGER
  left_ch_numbers        TEXT (JSON)
  right_ch_numbers       TEXT (JSON)
  left_postcodes         TEXT (JSON)   — top 3 most-frequent postcodes across raw members
  right_postcodes        TEXT (JSON)
  left_localities        TEXT (JSON)   — top 3 most-frequent localities
  right_localities       TEXT (JSON)
  left_name_variants     TEXT (JSON)   — top 3 most-frequent raw name strings
  right_name_variants    TEXT (JSON)
  left_id_kind           TEXT          — 'ch' | 'fts_synthetic' | 'other'
  right_id_kind          TEXT
  structural_flag        TEXT          — 'parent_child_suspect' | 'pre_existing_overmerge_suspect' | NULL
  max_match_probability  REAL          — best Splink score across supporting raw pairs
  supporting_pair_count  INTEGER       — how many raw pairs back this canonical-pair
  status                 TEXT          — 'pending' | 'approved' | 'rejected' | 'deferred'
  decision_json          TEXT          — Morgan's decision object once adjudicated
  reviewed_at            TEXT
  created_at             TEXT

Run:
  .venv/bin/python agent/emit_adjudication_queue.py
  .venv/bin/python agent/emit_adjudication_queue.py --predict-threshold 0.5
  .venv/bin/python agent/emit_adjudication_queue.py --sample 20000   # smoke
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

from splink_supplier_dedup import extract_suppliers, train_and_predict

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "bid_intel.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS adjudication_queue (
    queue_id TEXT PRIMARY KEY,
    decision_type TEXT NOT NULL,
    left_canonical_id TEXT NOT NULL,
    right_canonical_id TEXT NOT NULL,
    left_name TEXT,
    right_name TEXT,
    left_member_count INTEGER,
    right_member_count INTEGER,
    left_ch_numbers TEXT,
    right_ch_numbers TEXT,
    left_postcodes TEXT,
    right_postcodes TEXT,
    left_localities TEXT,
    right_localities TEXT,
    left_name_variants TEXT,
    right_name_variants TEXT,
    left_id_kind TEXT,
    right_id_kind TEXT,
    structural_flag TEXT,
    max_match_probability REAL NOT NULL,
    supporting_pair_count INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    decision_json TEXT,
    reviewed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_adj_queue_status
    ON adjudication_queue(status);
CREATE INDEX IF NOT EXISTS idx_adj_queue_prob
    ON adjudication_queue(max_match_probability DESC);
"""


_CH_BODY_RE = re.compile(r"^(?:GB-)?COH-([A-Z0-9]{2,10})$")
_VALID_CH_RE = re.compile(r"^(?:[A-Z]{2}\d{6}|\d{8})$")


def _classify_id_kind(canonical_id: str) -> str:
    """Classify canonical_id to help Morgan weight the evidence.

    Returns 'ch' for a real UK Companies House number, 'fts_synthetic' for the
    publisher-assigned FTS-* IDs that signal a name-only publisher entry, and
    'other' for anything else (the X338EBHC-style synthetic IDs we've seen).
    """
    if not canonical_id:
        return "other"
    if canonical_id.startswith("GB-FTS-"):
        return "fts_synthetic"
    m = _CH_BODY_RE.match(canonical_id)
    if m and _VALID_CH_RE.match(m.group(1)):
        return "ch"
    return "other"


_PARENT_TOKENS = (" group", " plc", " holdings", " holding group")


def _structural_flag(left_name: str | None, right_name: str | None,
                     left_ch_count: int, right_ch_count: int,
                     right_id_kind: str) -> str | None:
    """Tag pairs that need special handling beyond Splink's score.

    Two patterns we saw in batch 001 that Morgan should always defer on:

    - parent_child_suspect: one side carries a 'Group/PLC/Holdings' suffix and
      the other is its trading-subsidiary form. Structurally distinct legal
      entities even when address + name prefix match (Kier Group PLC vs Kier
      Construction Ltd; CH&Co Group vs CH&Co Catering Ltd).

    - pre_existing_overmerge_suspect: the left canonical already rolls up
      3+ distinct CH numbers AND the right is a no-CH FTS synthetic. Adding
      the synthetic to an already-broad canonical deepens any existing
      contamination. Flagged so the user can decide whether to split the
      left canonical first.
    """
    ln = (left_name or "").lower()
    rn = (right_name or "").lower()

    left_has_parent_token = any(t in ln for t in _PARENT_TOKENS)
    right_has_parent_token = any(t in rn for t in _PARENT_TOKENS)
    if left_has_parent_token ^ right_has_parent_token:
        return "parent_child_suspect"

    if left_ch_count >= 3 and right_id_kind == "fts_synthetic":
        return "pre_existing_overmerge_suspect"
    if right_ch_count >= 3 and right_id_kind != "ch":
        # symmetry guard — rare, but possible if publisher side is the large one
        return "pre_existing_overmerge_suspect"

    return None


def _top_values(conn: sqlite3.Connection, canonical_id: str, col: str,
                k: int = 3) -> list[str]:
    """Top-k non-null most-frequent values of `col` across raw members."""
    q = f"""
        SELECT s.{col} AS v, COUNT(*) c
        FROM suppliers s
        JOIN supplier_to_canonical s2c ON s2c.supplier_id = s.id
        WHERE s2c.canonical_id = ? AND s.{col} IS NOT NULL AND s.{col} != ''
        GROUP BY s.{col}
        ORDER BY c DESC
        LIMIT ?
    """
    return [r[0] for r in conn.execute(q, (canonical_id, k)).fetchall()]


def _pair_id(left: str, right: str) -> str:
    a, b = sorted([left, right])
    return hashlib.sha1(f"{a}|{b}".encode()).hexdigest()[:16]


def build_queue(predict_threshold: float, cluster_threshold: float,
                sample: int | None) -> list[dict]:
    print(f"[queue] Loading suppliers from {DB_PATH}"
          f"{' (sample=' + str(sample) + ')' if sample else ''}…")
    df = extract_suppliers(sample)
    print(f"[queue] Normalised {len(df):,} rows")

    t = time.time()
    print(f"[queue] Running Splink at predict_threshold={predict_threshold} "
          f"(will filter to [{predict_threshold}, {cluster_threshold}) for queue)…")
    _linker, preds = train_and_predict(df, predict_threshold)
    pred_df = preds.as_pandas_dataframe()
    print(f"[queue] {len(pred_df):,} raw pairs above {predict_threshold} "
          f"in {time.time()-t:.1f}s")

    # Keep only the mid-band: ≥ predict_threshold AND < cluster_threshold.
    # Pairs ≥ cluster_threshold were already auto-clustered by the main pipeline.
    midband = pred_df[
        (pred_df["match_probability"] >= predict_threshold)
        & (pred_df["match_probability"] < cluster_threshold)
    ].copy()
    print(f"[queue] {len(midband):,} pairs in mid-band "
          f"[{predict_threshold}, {cluster_threshold})")

    if midband.empty:
        return []

    # Look up each raw supplier's canonical_id
    with sqlite3.connect(DB_PATH) as conn:
        s2c = dict(conn.execute(
            "SELECT supplier_id, canonical_id FROM supplier_to_canonical"
        ).fetchall())

    midband["left_canonical"] = midband["unique_id_l"].map(s2c)
    midband["right_canonical"] = midband["unique_id_r"].map(s2c)
    # Drop pairs where either side didn't resolve to a canonical (shouldn't
    # happen after a full run, but guard against smoke/sample mismatches)
    midband = midband.dropna(subset=["left_canonical", "right_canonical"])
    # Drop self-canonical pairs (raw rows already share a canonical → not a merge question)
    midband = midband[midband["left_canonical"] != midband["right_canonical"]]
    print(f"[queue] {len(midband):,} cross-canonical supporting pairs")

    if midband.empty:
        return []

    # Aggregate to canonical-pair level: normalise ordering
    def _order(row):
        a, b = row["left_canonical"], row["right_canonical"]
        return (a, b) if a < b else (b, a)

    midband["_pair"] = midband.apply(_order, axis=1)
    agg = midband.groupby("_pair").agg(
        max_match_probability=("match_probability", "max"),
        supporting_pair_count=("match_probability", "size"),
    ).reset_index()

    # Hydrate canonical details
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        canonicals = {
            r["canonical_id"]: dict(r)
            for r in conn.execute(
                "SELECT canonical_id, canonical_name, member_count, "
                "ch_numbers, distinct_ch_count FROM canonical_suppliers"
            )
        }

    # Hydrate per-canonical evidence (postcodes, localities, raw name variants)
    # in one pass. Only touch canonicals we actually reference in agg.
    referenced_ids = {c for pair in agg["_pair"] for c in pair}
    evidence: dict[str, dict] = {}
    with sqlite3.connect(DB_PATH) as conn:
        for cid in referenced_ids:
            evidence[cid] = {
                "postcodes": _top_values(conn, cid, "postal_code"),
                "localities": _top_values(conn, cid, "locality"),
                "name_variants": _top_values(conn, cid, "name"),
            }

    records = []
    for _, r in agg.iterrows():
        left, right = r["_pair"]
        lc, rc = canonicals.get(left), canonicals.get(right)
        if not lc or not rc:
            continue
        le, re_ = evidence[left], evidence[right]
        left_id_kind = _classify_id_kind(left)
        right_id_kind = _classify_id_kind(right)
        left_ch_count = int(lc["distinct_ch_count"] or 0)
        right_ch_count = int(rc["distinct_ch_count"] or 0)
        structural = _structural_flag(
            lc["canonical_name"], rc["canonical_name"],
            left_ch_count, right_ch_count, right_id_kind,
        )
        records.append({
            "queue_id": _pair_id(left, right),
            "decision_type": "supplier_merge",
            "left_canonical_id": left,
            "right_canonical_id": right,
            "left_name": lc["canonical_name"],
            "right_name": rc["canonical_name"],
            "left_member_count": lc["member_count"],
            "right_member_count": rc["member_count"],
            "left_ch_numbers": lc["ch_numbers"],
            "right_ch_numbers": rc["ch_numbers"],
            "left_postcodes": json.dumps(le["postcodes"]) if le["postcodes"] else None,
            "right_postcodes": json.dumps(re_["postcodes"]) if re_["postcodes"] else None,
            "left_localities": json.dumps(le["localities"]) if le["localities"] else None,
            "right_localities": json.dumps(re_["localities"]) if re_["localities"] else None,
            "left_name_variants": json.dumps(le["name_variants"]) if le["name_variants"] else None,
            "right_name_variants": json.dumps(re_["name_variants"]) if re_["name_variants"] else None,
            "left_id_kind": left_id_kind,
            "right_id_kind": right_id_kind,
            "structural_flag": structural,
            "max_match_probability": float(r["max_match_probability"]),
            "supporting_pair_count": int(r["supporting_pair_count"]),
        })
    records.sort(key=lambda x: x["max_match_probability"], reverse=True)
    return records


def write_queue(records: list[dict]) -> tuple[int, int]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        existing = {
            r[0] for r in conn.execute(
                "SELECT queue_id FROM adjudication_queue"
            ).fetchall()
        }
        new = [r for r in records if r["queue_id"] not in existing]
        if new:
            conn.executemany(
                """INSERT INTO adjudication_queue
                   (queue_id, decision_type, left_canonical_id, right_canonical_id,
                    left_name, right_name, left_member_count, right_member_count,
                    left_ch_numbers, right_ch_numbers,
                    left_postcodes, right_postcodes,
                    left_localities, right_localities,
                    left_name_variants, right_name_variants,
                    left_id_kind, right_id_kind,
                    structural_flag,
                    max_match_probability, supporting_pair_count)
                   VALUES (:queue_id, :decision_type, :left_canonical_id,
                           :right_canonical_id, :left_name, :right_name,
                           :left_member_count, :right_member_count,
                           :left_ch_numbers, :right_ch_numbers,
                           :left_postcodes, :right_postcodes,
                           :left_localities, :right_localities,
                           :left_name_variants, :right_name_variants,
                           :left_id_kind, :right_id_kind,
                           :structural_flag,
                           :max_match_probability, :supporting_pair_count)""",
                new,
            )
            conn.commit()
        return len(new), len(existing)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict-threshold", type=float, default=0.4,
                    help="Lower bound of the adjudication mid-band (default 0.4)")
    ap.add_argument("--cluster-threshold", type=float, default=0.95,
                    help="Upper bound — pairs at or above were auto-clustered")
    ap.add_argument("--sample", type=int, default=None,
                    help="Sample N suppliers for a smoke run")
    args = ap.parse_args()

    t0 = time.time()
    records = build_queue(
        predict_threshold=args.predict_threshold,
        cluster_threshold=args.cluster_threshold,
        sample=args.sample,
    )
    print(f"[queue] Assembled {len(records):,} canonical-pair candidates")

    if records:
        inserted, kept = write_queue(records)
        print(f"[queue] Wrote {inserted:,} new rows to adjudication_queue "
              f"(kept {kept:,} existing)")
    else:
        print("[queue] Nothing to write")

    print(f"[queue] Done in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
