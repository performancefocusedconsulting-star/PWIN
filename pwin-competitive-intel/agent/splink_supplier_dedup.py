#!/usr/bin/env python3
"""Splink supplier entity resolution — Phase 1 of the canonical layer.

Collapses the raw supplier rows in bid_intel.db into canonical entities.
Uses Splink 4 with the DuckDB backend. Runs locally, no network.

Pipeline:
  1. Extract suppliers from SQLite, normalise fields into a DuckDB working table
  2. Fit Splink model (u-values via random sampling; m-values via EM on blocked pairs)
  3. Predict pairwise match probabilities above threshold
  4. Cluster via connected components at a stricter threshold
  5. Write canonical_suppliers + supplier_to_canonical back into bid_intel.db

Run:
  .venv/bin/python agent/splink_supplier_dedup.py --sample 5000   # smoke test
  .venv/bin/python agent/splink_supplier_dedup.py                  # full run
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd
from splink import DuckDBAPI, Linker, SettingsCreator, block_on
from splink.comparison_library import (
    ExactMatch,
    JaroWinklerAtThresholds,
    LevenshteinAtThresholds,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "bid_intel.db"

# 8-char UK CH format: 2 letters + 6 digits OR 8 digits
CH_REGEX = re.compile(r"^([A-Z]{2}\d{6}|\d{8})$")
# UK postcode tolerant regex
UK_POSTCODE_REGEX = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}$")


def normalise_ch(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = re.sub(r"\s+", "", raw).upper()
    return cleaned if CH_REGEX.match(cleaned) else None


def normalise_postcode(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = re.sub(r"\s+", "", raw).upper()
    return cleaned if UK_POSTCODE_REGEX.match(cleaned) else None


def normalise_name(raw: str | None) -> str | None:
    if not raw:
        return None
    # lower, strip, collapse whitespace, normalise ampersand, quotes, and Ltd/Limited
    s = raw.lower().strip()
    s = s.replace("&", " and ")
    s = re.sub(r"[\"'`]", "", s)
    # Ltd → limited (word boundary, trailing dot tolerated)
    s = re.sub(r"\bltd\.?\b", "limited", s)
    # plc. → plc, co. → company (light-touch)
    s = re.sub(r"\bco\.?\b", "company", s)
    # Strip trailing punctuation
    s = re.sub(r"[.,;:\-]+\s*$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def normalise_loc(raw: str | None) -> str | None:
    if not raw:
        return None
    s = raw.lower().strip()
    return re.sub(r"\s+", " ", s) or None


def extract_suppliers(sample: int | None) -> pd.DataFrame:
    """Pull suppliers from SQLite and normalise into a DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        q = """
            SELECT id, name, companies_house_no, postal_code, locality, street_address
            FROM suppliers
        """
        if sample:
            q += f" ORDER BY RANDOM() LIMIT {int(sample)}"
        rows = conn.execute(q).fetchall()

    records = []
    for r in rows:
        name_c = normalise_name(r["name"])
        if not name_c:
            continue  # skip nameless rows
        records.append({
            "unique_id": r["id"],
            "name_clean": name_c,
            "name_prefix_4": name_c[:4],
            "name_prefix_6": name_c[:6],
            "postcode_clean": normalise_postcode(r["postal_code"]),
            "locality_clean": normalise_loc(r["locality"]),
            "street_clean": (r["street_address"] or "").lower().strip()[:40] or None,
            "ch_clean": normalise_ch(r["companies_house_no"]),
        })
    return pd.DataFrame.from_records(records)


def build_settings() -> SettingsCreator:
    return SettingsCreator(
        link_type="dedupe_only",
        blocking_rules_to_generate_predictions=[
            block_on("ch_clean"),
            block_on("postcode_clean", "name_prefix_4"),
            block_on("name_prefix_6", "locality_clean"),
            block_on("name_clean"),
        ],
        comparisons=[
            JaroWinklerAtThresholds("name_clean", [0.95, 0.88, 0.8]),
            ExactMatch("postcode_clean").configure(
                term_frequency_adjustments=True
            ),
            ExactMatch("ch_clean"),
            JaroWinklerAtThresholds("locality_clean", [0.9]),
            LevenshteinAtThresholds("street_clean", [2, 5]),
        ],
        retain_intermediate_calculation_columns=False,
        retain_matching_columns=True,
    )


def train_and_predict(df: pd.DataFrame, predict_threshold: float):
    """Fit the Splink model and return pairwise predictions above threshold."""
    settings = build_settings()
    linker = Linker(df, settings, db_api=DuckDBAPI())

    # Initial probability: proportion of random pairs that are matches
    deterministic_rules = [
        "l.ch_clean = r.ch_clean",
        "l.name_clean = r.name_clean and l.postcode_clean = r.postcode_clean",
    ]
    linker.training.estimate_probability_two_random_records_match(
        deterministic_rules, recall=0.8
    )
    # u-values via random sampling (how similar are random non-matches)
    linker.training.estimate_u_using_random_sampling(max_pairs=10_000_000)
    # m-values via EM for each blocking rule independently
    linker.training.estimate_parameters_using_expectation_maximisation(
        "l.ch_clean = r.ch_clean"
    )
    linker.training.estimate_parameters_using_expectation_maximisation(
        "l.postcode_clean = r.postcode_clean and l.name_prefix_4 = r.name_prefix_4"
    )
    preds = linker.inference.predict(threshold_match_probability=predict_threshold)
    return linker, preds


def write_canonical(
    conn: sqlite3.Connection, clusters_df: pd.DataFrame, source_df: pd.DataFrame
) -> tuple[int, int]:
    """Materialise canonical_suppliers + supplier_to_canonical in SQLite.

    Returns (n_canonical, n_supplier_rows).
    """
    # clusters_df already carries the source columns (retain_matching_columns=True).
    # If anything's missing, merge it in.
    needed = [c for c in ("name_clean", "ch_clean") if c not in clusters_df.columns]
    joined = (
        clusters_df.merge(
            source_df[["unique_id", *needed]], on="unique_id", how="left"
        )
        if needed
        else clusters_df
    )

    # For each canonical cluster, pick the most-frequent name_clean as the canonical_name.
    def pick_rep(group):
        # Prefer rows with a CH number; otherwise most-frequent name
        with_ch = group[group["ch_clean"].notna()]
        pool = with_ch if not with_ch.empty else group
        top = pool["name_clean"].value_counts().idxmax()
        chs = sorted({c for c in group["ch_clean"].dropna().unique()})
        return pd.Series({
            "canonical_name": top,
            "member_count": len(group),
            "ch_numbers": json.dumps(chs) if chs else None,
            "distinct_ch_count": len(chs),
        })

    canonical_df = (
        joined.groupby("cluster_id", dropna=False).apply(pick_rep).reset_index()
    )

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS canonical_suppliers (
            canonical_id TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL,
            member_count INTEGER NOT NULL,
            ch_numbers TEXT,
            distinct_ch_count INTEGER NOT NULL,
            source TEXT NOT NULL DEFAULT 'splink',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS supplier_to_canonical (
            supplier_id TEXT PRIMARY KEY,
            canonical_id TEXT NOT NULL,
            FOREIGN KEY (canonical_id) REFERENCES canonical_suppliers(canonical_id)
        );
        CREATE INDEX IF NOT EXISTS idx_s2c_canonical ON supplier_to_canonical(canonical_id);
        DELETE FROM supplier_to_canonical;
        DELETE FROM canonical_suppliers;
    """)

    conn.executemany(
        """INSERT INTO canonical_suppliers
           (canonical_id, canonical_name, member_count, ch_numbers, distinct_ch_count)
           VALUES (?, ?, ?, ?, ?)""",
        [
            (str(r.cluster_id), r.canonical_name, int(r.member_count),
             r.ch_numbers, int(r.distinct_ch_count))
            for r in canonical_df.itertuples(index=False)
        ],
    )
    conn.executemany(
        "INSERT INTO supplier_to_canonical (supplier_id, canonical_id) VALUES (?, ?)",
        [(r.unique_id, str(r.cluster_id)) for r in clusters_df.itertuples(index=False)],
    )
    conn.commit()

    # Deterministic post-pass: merge clusters sharing the same canonical_name.
    # Splink can leave identical-name records in separate clusters when other
    # fields (postcode, street) disagree — e.g. Serco Limited at several offices.
    # For same-name cases we treat these as the same legal entity; downstream
    # analysis can re-split by address if needed.
    before = conn.execute("SELECT COUNT(*) FROM canonical_suppliers").fetchone()[0]
    conn.executescript("""
        -- Pick survivor per canonical_name: cluster with highest member_count
        CREATE TEMP TABLE survivors AS
          SELECT canonical_name,
                 (SELECT canonical_id FROM canonical_suppliers c2
                  WHERE c2.canonical_name = c1.canonical_name
                  ORDER BY member_count DESC, canonical_id LIMIT 1) AS survivor_id
          FROM canonical_suppliers c1
          GROUP BY canonical_name;

        -- Reassign members to the survivor
        UPDATE supplier_to_canonical
           SET canonical_id = (
             SELECT survivor_id FROM survivors s
             JOIN canonical_suppliers c ON c.canonical_name = s.canonical_name
             WHERE c.canonical_id = supplier_to_canonical.canonical_id
           )
         WHERE canonical_id NOT IN (SELECT survivor_id FROM survivors);

        -- Drop non-survivor rows
        DELETE FROM canonical_suppliers
         WHERE canonical_id NOT IN (SELECT survivor_id FROM survivors);

        -- Refresh member_count on survivors
        UPDATE canonical_suppliers
           SET member_count = (
             SELECT COUNT(*) FROM supplier_to_canonical s2c
             WHERE s2c.canonical_id = canonical_suppliers.canonical_id
           );

        DROP TABLE survivors;
    """)
    conn.commit()
    after = conn.execute("SELECT COUNT(*) FROM canonical_suppliers").fetchone()[0]
    print(f"[splink] Post-pass name-merge: {before:,} → {after:,} "
          f"({before - after:,} duplicate-name clusters merged)")
    return after, len(clusters_df)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=None,
                    help="If set, run against a random sample of N suppliers (smoke test)")
    ap.add_argument("--predict-threshold", type=float, default=0.9,
                    help="Pairwise match probability threshold for prediction")
    ap.add_argument("--cluster-threshold", type=float, default=0.95,
                    help="Match probability for connected-components clustering")
    ap.add_argument("--no-write", action="store_true",
                    help="Skip writing canonical tables (diagnostic only)")
    args = ap.parse_args()

    t0 = time.time()
    print(f"[splink] Loading suppliers from {DB_PATH}"
          f"{' (sample=' + str(args.sample) + ')' if args.sample else ''}…")
    df = extract_suppliers(args.sample)
    print(f"[splink] Normalised {len(df):,} supplier rows in {time.time()-t0:.1f}s")
    print(f"[splink]   with CH:        {df['ch_clean'].notna().sum():,}")
    print(f"[splink]   with postcode:  {df['postcode_clean'].notna().sum():,}")
    print(f"[splink]   with locality:  {df['locality_clean'].notna().sum():,}")

    t1 = time.time()
    print(f"[splink] Training model + predicting pairs (threshold="
          f"{args.predict_threshold})…")
    linker, preds = train_and_predict(df, args.predict_threshold)
    pred_df = preds.as_pandas_dataframe()
    print(f"[splink] {len(pred_df):,} candidate pairs above threshold "
          f"in {time.time()-t1:.1f}s")

    t2 = time.time()
    print(f"[splink] Clustering (threshold={args.cluster_threshold})…")
    clusters = linker.clustering.cluster_pairwise_predictions_at_threshold(
        preds, threshold_match_probability=args.cluster_threshold
    )
    clusters_df = clusters.as_pandas_dataframe()
    n_canonical = clusters_df["cluster_id"].nunique()
    print(f"[splink] {len(clusters_df):,} rows clustered into {n_canonical:,} "
          f"canonical entities in {time.time()-t2:.1f}s")
    compression = 1 - n_canonical / max(len(clusters_df), 1)
    print(f"[splink] Compression: {compression*100:.1f}%  "
          f"({len(clusters_df):,} → {n_canonical:,})")

    if args.no_write or args.sample:
        print("[splink] --no-write or --sample set: skipping DB writes.")
    else:
        t3 = time.time()
        print("[splink] Writing canonical_suppliers + supplier_to_canonical…")
        with sqlite3.connect(DB_PATH) as conn:
            n_can, n_rows = write_canonical(conn, clusters_df, df)
        print(f"[splink] Wrote {n_can:,} canonical / {n_rows:,} mappings in "
              f"{time.time()-t3:.1f}s")

    print(f"[splink] Done in {time.time()-t0:.1f}s total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
