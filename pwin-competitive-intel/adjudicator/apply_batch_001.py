#!/usr/bin/env python3
"""One-off: promote batch 001 (the top-20 re-adjudicated with enriched evidence).

Writes decisions to adjudicator_decisions.jsonl, updates adjudication_queue
row statuses, and promotes approved merges by reassigning member rows and
deleting absorbed canonical records. Run once; rerun is a no-op because
queue rows move out of 'pending'.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "bid_intel.db"
LEDGER = REPO_ROOT / "adjudicator" / "adjudicator_decisions.jsonl"

BATCH_ID = "batch_001"
# survivor = larger member_count, ties broken by CH presence then canonical_id ASC.
# Each entry is the full decision object — what gets logged AND (for approve)
# what drives the merge. queue_id is a stable hash, so reruns are idempotent.
DECISIONS: list[dict] = [
    # 1. Sovini — reject
    {"queue_id": "3301c35988706345", "recommendation": "reject_merge", "confidence": 0.85,
     "left_canonical_id": "GB-COH-03741160", "right_canonical_id": "GB-COH-08956215",
     "evidence": ["Shared postcode L30 6UR supports same-group relationship",
                  "Non-overlapping CH (left 03741160/07381427/08482515 vs right 08956215)",
                  "Distinct trading activities: property services vs trade supplies"],
     "uncertainty_notes": "Both in Sovini group; keep sister companies separate per hard rule #2"},

    # 2. Corporate Project Solutions Ltd ↔ CPS (FTS)
    {"queue_id": "9a5b466a7a48e927", "recommendation": "approve_merge", "confidence": 0.93,
     "survivor_canonical_id": "GB-COH-03014568", "absorbed_canonical_id": "GB-FTS-164434",
     "evidence": ["Same postcode RG2 6UU both sides",
                  "Right is FTS synthetic ID (publisher name-only entry)",
                  "'(CPS)' on right is abbreviation of left's canonical name"],
     "uncertainty_notes": "Would reject if FTS side resolved to a different CH"},

    # 3. Ideal Carehomes Ltd ↔ Ideal Care Homes (Number One) Ltd
    {"queue_id": "597f75650a32ad86", "recommendation": "approve_merge", "confidence": 0.95,
     "survivor_canonical_id": "GB-COH-07535382", "absorbed_canonical_id": "GB-FTS-106432",
     "evidence": ["Left canonical's name_variants already contains 'Ideal Carehomes (Number One) Limited' (with CH 10531219)",
                  "Same postcode DL3 6AH both sides",
                  "Right is FTS synthetic (no CH) — identical entity re-published without structured ID"],
     "uncertainty_notes": "Definitive because the '(Number One)' variant is already on the left canonical's rolled-up CH set"},

    # 4. Sports Coaching Specialists Ltd ↔ SCS (FTS)
    {"queue_id": "0567f0193e2c3902", "recommendation": "approve_merge", "confidence": 0.88,
     "survivor_canonical_id": "GB-COH-X338EBHC", "absorbed_canonical_id": "GB-FTS-141995",
     "evidence": ["Same postcode CO5 9SE both sides",
                  "Kelvedon/Feering are adjacent Essex villages (same postcode district)",
                  "'(SCS)' is abbreviation of 'Sports Coaching Specialists'"],
     "uncertainty_notes": "Left's ID is a synthetic non-CH format (X338EBHC) but postcode + name are strong"},

    # 5. Kier Construction Ltd ↔ Kier Group PLC — defer
    {"queue_id": "22c0895c770dbe36", "recommendation": "defer", "confidence": 0.5,
     "left_canonical_id": "GB-COH-01157281", "right_canonical_id": "GB-FTS-71492",
     "evidence": ["Shared postcode SG19 2BD (Kier HQ in Sandy)",
                  "Left already rolls up 7 CH numbers across Kier trading subsidiaries",
                  "Right is FTS synthetic labelled 'Kier Group PLC' — the listed parent holding company"],
     "uncertainty_notes": "Parent holding vs trading subsidiary is structurally distinct — flag as parent-child pattern, should route to human decision"},

    # 6. CoGrammar
    {"queue_id": "63a1ceb3d2090511", "recommendation": "approve_merge", "confidence": 0.94,
     "survivor_canonical_id": "GB-COH-10493520", "absorbed_canonical_id": "GB-FTS-136536",
     "evidence": ["Same postcode N1 7GU (N17GU on right is whitespace-only drift)",
                  "Left canonical name explicitly notes rename: 'cogrammar limited (prev hyperiondev limited)'",
                  "Right FTS synthetic is the trading-name form 'CoGrammar t/a HyperionDev'"],
     "uncertainty_notes": "Rebrand pattern — HyperionDev → CoGrammar"},

    # 7. CNLR Horizons
    {"queue_id": "a86ef96944282dbb", "recommendation": "approve_merge", "confidence": 0.92,
     "survivor_canonical_id": "GB-COH-02271807", "absorbed_canonical_id": "GB-FTS-55244",
     "evidence": ["Same postcode E1 8AA both sides",
                  "Right is trading-name variant 't/a CiC Wellbeing' of the left entity"],
     "uncertainty_notes": ""},

    # 8. Marsh
    {"queue_id": "dfa9d2b5db08bfca", "recommendation": "approve_merge", "confidence": 0.93,
     "survivor_canonical_id": "GB-COH-01507274", "absorbed_canonical_id": "GB-FTS-115573",
     "evidence": ["Postcode RG6 1PT appears on both sides",
                  "Right is the brand name 'Marsh' without legal suffix — left is the UK trading entity Marsh Ltd"],
     "uncertainty_notes": "Would reject if FTS side resolved to Marsh McLennan parent or a different Marsh entity"},

    # 9. CH&Co Catering Ltd ↔ CH&Co Group — defer
    {"queue_id": "f36fa382ec6a8516", "recommendation": "defer", "confidence": 0.5,
     "left_canonical_id": "GB-COH-02613820", "right_canonical_id": "GB-FTS-39595",
     "evidence": ["Same postcode RG6 1PT both sides",
                  "Left is 'CH&Co Catering Ltd' with subsidiary trading names (Pabulum)",
                  "Right is 'CH&Co Group' — parent holding label"],
     "uncertainty_notes": "Parent holding vs trading subsidiary — structural distinction; human decision"},

    # 10. MSCI — defer
    {"queue_id": "4066d7fdab118055", "recommendation": "defer", "confidence": 0.55,
     "left_canonical_id": "GB-COH-03981254", "right_canonical_id": "GB-FTS-139596",
     "evidence": ["Same postcode E1 6EG (MSCI London office)",
                  "Right name 'MSCI ESG Research (UK) Limited' is a distinct MSCI group subsidiary, not a variant of MSCI Ltd",
                  "FTS side has no CH so cannot confirm which MSCI entity the publisher meant"],
     "uncertainty_notes": "Could be a publisher mis-tag of MSCI Ltd, or a legitimate separate ESG Research subsidiary — cannot distinguish without CH"},

    # 11. Thinks Insight & Strategy ↔ CM Monitor t/a Britain Thinks
    {"queue_id": "79f08bc40ff2d123", "recommendation": "approve_merge", "confidence": 0.97,
     "survivor_canonical_id": "GB-COH-07291125", "absorbed_canonical_id": "GB-FTS-113810",
     "evidence": ["Same CH 07291125 on both sides — dispositive",
                  "Same postcode PL13 1PN",
                  "Rebrand pattern: Britain Thinks → Thinks Insight & Strategy"],
     "uncertainty_notes": ""},

    # 12. SRUC Innovation Limited ↔ SAC Commercial Limited
    {"queue_id": "9cf3f05a16ca8f80", "recommendation": "approve_merge", "confidence": 0.95,
     "survivor_canonical_id": "GB-COH-SC103046", "absorbed_canonical_id": "GB-FTS-105114",
     "evidence": ["Overlapping CH SC148684 (appears in both sides' CH sets)",
                  "Same postcode EH9 3JG (Edinburgh, West Mains Road — SRUC campus)",
                  "Group consolidation: SAC Commercial is SRUC's commercial trading arm"],
     "uncertainty_notes": ""},

    # 13. Ulverscroft Ltd ↔ Ulverscroft Large Print Books Ltd
    {"queue_id": "b61b730253c5a0a8", "recommendation": "approve_merge", "confidence": 0.95,
     "survivor_canonical_id": "GB-COH-01068776", "absorbed_canonical_id": "GB-FTS-63819",
     "evidence": ["Left canonical's name_variants already contains 'Ulverscroft Large Print Books Ltd'",
                  "Same locality (Leicester) both sides",
                  "Right is FTS synthetic — no CH"],
     "uncertainty_notes": "Name_variants match on left canonical is near-definitive for a no-CH right side"},

    # 14. Medscience Distribution Ltd ↔ Pharmed UK
    {"queue_id": "8447397b850568bf", "recommendation": "approve_merge", "confidence": 0.95,
     "survivor_canonical_id": "GB-COH-02491098", "absorbed_canonical_id": "GB-FTS-36786",
     "evidence": ["Left canonical's name_variants already contains 'Pharmed UK'",
                  "Same locality (Banbury) both sides",
                  "Pharmed UK is a trading name of Medscience Distribution Limited"],
     "uncertainty_notes": ""},

    # 15. Oliveti Group ↔ Oliveti Construction Ltd — reject
    {"queue_id": "4083783ed6d50ab7", "recommendation": "reject_merge", "confidence": 0.85,
     "left_canonical_id": "GB-COH-09353166", "right_canonical_id": "GB-FTS-75560",
     "evidence": ["Right FTS record carries its own distinct CH 04341581 (different from left's 09353166)",
                  "Distinct registered companies — right should stay separate"],
     "uncertainty_notes": "Left canonical may itself need splitting — its name_variants include 'Oliveti Construction Ltd' but those raw members lack the distinct CH 04341581 that right carries"},

    # 16. Oakdale Centre CIC ↔ Oakdale Therapies Ltd
    {"queue_id": "588f08be1254da38", "recommendation": "approve_merge", "confidence": 0.9,
     "survivor_canonical_id": "GB-COH-10277025", "absorbed_canonical_id": "GB-FTS-69528",
     "evidence": ["Left canonical's name_variants already contains 'Oakdale Therapies Ltd'",
                  "Same locality (Harrogate)",
                  "Left's CH set includes 12017301 (likely the Therapies CH) alongside 10277025 (Centre CIC)"],
     "uncertainty_notes": "Name variant match + locality supports merge; FTS side is no-CH publisher variant"},

    # 17. NOC Innovations Ltd ↔ National Oceanography Centre — defer
    {"queue_id": "d8d084502814a616", "recommendation": "defer", "confidence": 0.5,
     "left_canonical_id": "GB-COH-11444362", "right_canonical_id": "GB-FTS-127755",
     "evidence": ["Same locality (Southampton) both sides",
                  "Left is trading subsidiary 'NOC Innovations Ltd'",
                  "Right is the parent research body 'National Oceanography Centre'"],
     "uncertainty_notes": "Parent research body vs trading subsidiary — structurally distinct; left canonical may already over-merge both"},

    # 18. Nuance Communications Ltd ↔ Nuance Communications Ireland Ltd — defer
    {"queue_id": "0b01d90b302d0a95", "recommendation": "defer", "confidence": 0.4,
     "left_canonical_id": "GB-COH-503352", "right_canonical_id": "GB-FTS-172862",
     "evidence": ["Left canonical is ALREADY an over-merge — its UK CH 00503352 rolls up raw rows named 'Nuance Communications Ireland Limited'",
                  "Right FTS record is labelled as Ireland Ltd — could be same or distinct entity",
                  "Left localities include Dublin — suggesting the pre-existing over-merge is structural"],
     "uncertainty_notes": "Cannot safely merge when left is already contaminated; flag left canonical for a future split operation"},

    # 19. Tetra Tech RPS Energy ↔ RPS Consulting Services
    {"queue_id": "50079328720e8082", "recommendation": "approve_merge", "confidence": 0.93,
     # Survivor = right (larger member_count 32 vs 3)
     "survivor_canonical_id": "GB-COH-01756175", "absorbed_canonical_id": "GB-COH-01465554",
     "evidence": ["Overlapping CH 01470149 in both sides' CH sets",
                  "Postcode OX14 4RY appears on both (Abingdon)",
                  "RPS Group acquired by Tetra Tech 2023 — group-consolidation merge"],
     "uncertainty_notes": ""},

    # 20. Angel Care Staffing — defer
    {"queue_id": "221214409913b04a", "recommendation": "defer", "confidence": 0.5,
     "left_canonical_id": "GB-COH-13879913", "right_canonical_id": "GB-COH-13879931",
     "evidence": ["Identical normalised names both sides",
                  "Same postcode NG2 6AB",
                  "CH numbers differ by one digit: 13879913 vs 13879931"],
     "uncertainty_notes": "Could be publisher typo (same entity, one CH digit wrong) or genuine sister SPVs incorporated consecutively — cannot distinguish without CH filing check"},
]

# Status for each queue_id derived from recommendation
_STATUS = {
    "approve_merge": "approved",
    "reject_merge": "rejected",
    "defer": "deferred",
}


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    LEDGER.parent.mkdir(parents=True, exist_ok=True)

    approved_count = 0
    rejected_count = 0
    deferred_count = 0
    skipped_count = 0

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        for d in DECISIONS:
            # Read the queue row to hydrate decision metadata + guard against re-applying
            row = conn.execute(
                "SELECT status, left_canonical_id, right_canonical_id, left_name, right_name "
                "FROM adjudication_queue WHERE queue_id = ?",
                (d["queue_id"],),
            ).fetchone()
            if row is None:
                print(f"[apply] queue_id={d['queue_id']} not found — skipping")
                skipped_count += 1
                continue
            status_current = row[0]
            if status_current != "pending":
                print(f"[apply] queue_id={d['queue_id']} already {status_current!r} — skipping")
                skipped_count += 1
                continue

            status = _STATUS[d["recommendation"]]
            decision_record = {
                **d,
                "decision_type": "supplier_merge",
                "batch_id": BATCH_ID,
                "adjudicator": "morgan_ledger",
                "reviewed_at": now,
                "status": status,
                "left_canonical_id_snapshot": row[1],
                "right_canonical_id_snapshot": row[2],
                "left_name_snapshot": row[3],
                "right_name_snapshot": row[4],
            }

            if d["recommendation"] == "approve_merge":
                survivor = d["survivor_canonical_id"]
                absorbed = d["absorbed_canonical_id"]
                # Re-parent members of the absorbed canonical
                n_moved = conn.execute(
                    "UPDATE supplier_to_canonical SET canonical_id = ? WHERE canonical_id = ?",
                    (survivor, absorbed),
                ).rowcount
                # Drop the absorbed canonical record
                conn.execute(
                    "DELETE FROM canonical_suppliers WHERE canonical_id = ?",
                    (absorbed,),
                )
                # Refresh member_count on the survivor
                conn.execute(
                    """UPDATE canonical_suppliers
                          SET member_count = (
                            SELECT COUNT(*) FROM supplier_to_canonical s2c
                            WHERE s2c.canonical_id = canonical_suppliers.canonical_id
                          )
                        WHERE canonical_id = ?""",
                    (survivor,),
                )
                decision_record["members_moved"] = n_moved
                approved_count += 1
                print(f"[apply] APPROVED queue_id={d['queue_id']}  "
                      f"{absorbed} -> {survivor}  ({n_moved} members moved)")
            elif d["recommendation"] == "reject_merge":
                rejected_count += 1
                print(f"[apply] REJECTED queue_id={d['queue_id']}")
            else:
                deferred_count += 1
                print(f"[apply] DEFERRED queue_id={d['queue_id']}")

            # Mark the queue row
            conn.execute(
                """UPDATE adjudication_queue
                      SET status = ?, decision_json = ?, reviewed_at = ?
                    WHERE queue_id = ?""",
                (status, json.dumps(decision_record), now, d["queue_id"]),
            )
            # Append to the ledger — always, even for rejects/defers
            with LEDGER.open("a") as f:
                f.write(json.dumps(decision_record) + "\n")

        conn.commit()

    print()
    print(f"[apply] Summary: {approved_count} approved, {rejected_count} rejected, "
          f"{deferred_count} deferred, {skipped_count} skipped")
    print(f"[apply] Ledger: {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
