#!/usr/bin/env python3
"""Apply Morgan batch 002: 11 approve, 5 reject, 4 defer.

Same mechanism as apply_batch_001.py — reads queue rows, writes decision
ledger, promotes approved merges atomically. Idempotent via queue_id
status guard.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "bid_intel.db"
LEDGER = REPO_ROOT / "adjudicator" / "adjudicator_decisions.jsonl"

BATCH_ID = "batch_002"

DECISIONS: list[dict] = [
    # 1. Kongsberg — defer
    {"queue_id": "63e903a1d99f7f8e", "recommendation": "defer", "confidence": 0.55,
     "left_canonical_id": "GB-COH-BR021842", "right_canonical_id": "GB-COH-SC107343",
     "evidence": ["Same postcode AB32 6FE both sides",
                  "BR-prefix on left = UK branch of Norwegian parent (Kongsberg Maritime AS)",
                  "SC-prefix on right = UK-incorporated Scottish subsidiary — structurally distinct legal form"],
     "uncertainty_notes": "Public-sector buyers treat them as the same company in practice; formal legal status differs"},

    # 2. My Holding Group Ltd ↔ MY Holdings Group
    {"queue_id": "6d9ee75cbeedd7ce", "recommendation": "approve_merge", "confidence": 0.93,
     "survivor_canonical_id": "GB-COH-10843461", "absorbed_canonical_id": "GB-FTS-129081",
     "evidence": ["Same postcode EN5 5TZ both sides",
                  "Left's name_variants already contains 'MY Holdings Group Ltd'"],
     "uncertainty_notes": ""},

    # 3. CBRE Investment Management Indirect ↔ CBRE Global Investors — reject
    {"queue_id": "3486a30fc7f3f305", "recommendation": "reject_merge", "confidence": 0.85,
     "left_canonical_id": "GB-COH-02076511", "right_canonical_id": "GB-FTS-2745",
     "evidence": ["Shared CBRE London office at EC4M 9AF expected for group companies",
                  "Distinct product-line subsidiaries (Investment Management vs Global Investors)",
                  "Previously rejected in batch 001 — same reasoning"],
     "uncertainty_notes": "Right has no CH, so cannot formally confirm — but name + name_variants support distinct entities"},

    # 4. AstraZeneca ↔ AstraZeneca Pharmaceuticals Limited — reject
    {"queue_id": "ec442954e6b17aa5", "recommendation": "reject_merge", "confidence": 0.8,
     "left_canonical_id": "GB-COH-03674842", "right_canonical_id": "GB-FTS-23242",
     "evidence": ["Left CH 03674842 = AstraZeneca UK Limited",
                  "AstraZeneca Pharmaceuticals Limited is a separate UK subsidiary (CH 06935519)",
                  "Left's name_variants includes 'AstraZeneca UK Ltd' but NOT 'Pharmaceuticals'"],
     "uncertainty_notes": "FTS side has no CH — cannot definitively confirm, but the named entity is a distinct AZ subsidiary"},

    # 5. JLA Limited ↔ JLA Fire & Security Limited — reject
    {"queue_id": "81971d2cef077f86", "recommendation": "reject_merge", "confidence": 0.9,
     "left_canonical_id": "GB-COH-01094178", "right_canonical_id": "GB-COH-06486921",
     "evidence": ["Non-overlapping CH (01094178 vs 06486921)",
                  "Distinct trading businesses (laundry/catering vs fire/security)",
                  "Previously rejected in batch 001"],
     "uncertainty_notes": ""},

    # 6. Vision Events UK Limited ↔ Vision Events
    {"queue_id": "bc2ceed932ac3735", "recommendation": "approve_merge", "confidence": 0.9,
     # Both are FTS-prefixed by canonical_id but left carries a real CH. Survivor = left (has CH, more members tied in future merges).
     "survivor_canonical_id": "GB-FTS-108754", "absorbed_canonical_id": "GB-FTS-45203",
     "evidence": ["Same postcode EH20 9LZ both sides",
                  "Left carries CH SC104232; right is FTS synthetic with no CH",
                  "'Vision Events' is the brand form of 'Vision Events UK Limited'"],
     "uncertainty_notes": "Left's canonical_id is FTS-prefixed despite having a real CH — canonical layer oddity worth investigating"},

    # 7. Cash Registers (Buccleuch) Limited ↔ Cash Registers Buccleugh
    {"queue_id": "e2214c1eeaa212fc", "recommendation": "approve_merge", "confidence": 0.9,
     "survivor_canonical_id": "GB-FTS-23382", "absorbed_canonical_id": "GB-FTS-34082",
     "evidence": ["Same postcode EH20 9LZ both sides",
                  "'Buccleugh' is a spelling typo of 'Buccleuch' (Scottish surname)",
                  "Identical underlying business — same small firm with publisher name variance"],
     "uncertainty_notes": "Neither side has a CH — merging by strong postcode + name match"},

    # 8. Orthodontic Centre UK Ltd ↔ Orthoworld 2000 Limited — reject
    {"queue_id": "104612889b3109fa", "recommendation": "reject_merge", "confidence": 0.85,
     "left_canonical_id": "GB-FTS-50900", "right_canonical_id": "GB-FTS-50983",
     "evidence": ["Shared postcode M26 1GG but distinct business names",
                  "Left's name_variants contain 'Orthocentres Limited' — rebrand of Orthodontic Centre",
                  "Right's name_variants are 'Orthoworld 2000 Ltd/Limited' — completely different firm"],
     "uncertainty_notes": "Unrelated orthodontic firms sharing a Manchester business park address"},

    # 9. Humankind Charity ↔ Waythrough (distinct CHC IDs) — defer
    {"queue_id": "6a8e45e760df84e6", "recommendation": "defer", "confidence": 0.5,
     "left_canonical_id": "GB-CHC-0182 0492", "right_canonical_id": "GB-CHC-515755",
     "evidence": ["Left's name_variants contain 'Waythrough' and 'Humankind Charity operating as Waythrough' — suggests rebrand",
                  "Right has its own distinct charity ID GB-CHC-515755 — not the same registered entity"],
     "uncertainty_notes": "Rebrand pattern on left is suggestive; two distinct charity IDs argue against merge — human judgement needed"},

    # 10. Humankind Charity ↔ Humankind (FTS)
    {"queue_id": "4d0d0ba7fb460099", "recommendation": "approve_merge", "confidence": 0.88,
     "survivor_canonical_id": "GB-CHC-0182 0492", "absorbed_canonical_id": "GB-FTS-33278",
     "evidence": ["Left's name_variants contain 'Humankind Charity'",
                  "Durham locality match across both sides",
                  "Right is FTS synthetic — publisher-truncated name"],
     "uncertainty_notes": ""},

    # 11. Change Grow Live ↔ Change Grow Live Services Ltd
    {"queue_id": "23de1c60a0002a9c", "recommendation": "approve_merge", "confidence": 0.94,
     "survivor_canonical_id": "GB-CHC-06228752", "absorbed_canonical_id": "GB-COH-n/a",
     "evidence": ["Left's name_variants contain 'Change Grow Live Services Ltd' verbatim",
                  "Same Brighton locality",
                  "Right is a no-CH placeholder canonical (GB-COH-n/a)"],
     "uncertainty_notes": "Right canonical_id is the 'n/a' sentinel — worth noting for canonical-ID-quality review"},

    # 12. Change Grow Live ↔ Change, Grow, Live
    {"queue_id": "7bd914acbb3e8cfc", "recommendation": "approve_merge", "confidence": 0.92,
     "survivor_canonical_id": "GB-CHC-06228752", "absorbed_canonical_id": "GB-FTS-39114",
     "evidence": ["Punctuation variant of the left's canonical name",
                  "Same Brighton locality"],
     "uncertainty_notes": ""},

    # 13. Change Grow Live ↔ Change Grow Live (CGL)
    {"queue_id": "345d39dbb5a0316d", "recommendation": "approve_merge", "confidence": 0.95,
     "survivor_canonical_id": "GB-CHC-06228752", "absorbed_canonical_id": "GB-FTS-83121",
     "evidence": ["Left's name_variants contain 'Change Grow Live (CGL)' verbatim",
                  "Same Brighton locality"],
     "uncertainty_notes": ""},

    # 14. Touchstone Leeds ↔ Touchstone - Leeds
    {"queue_id": "836cf99fcbc9b341", "recommendation": "approve_merge", "confidence": 0.95,
     "survivor_canonical_id": "GB-CHC-1012053", "absorbed_canonical_id": "GB-FTS-86373",
     "evidence": ["Left's name_variants contain 'Touchstone - Leeds' verbatim (hyphen variant)",
                  "Same Leeds locality"],
     "uncertainty_notes": ""},

    # 15. Avalon Group (charity) ↔ Avalon Group (Social Care) Ltd — defer
    {"queue_id": "1dd5aae715db278a", "recommendation": "defer", "confidence": 0.5,
     "left_canonical_id": "GB-CHC-1048236", "right_canonical_id": "GB-COH-02976727",
     "evidence": ["Both Harrogate-based, name overlap",
                  "Left is a registered charity (CHC ID); right is a Companies House Ltd",
                  "Right's name_variants include plain 'Avalon Group' — supports same-entity hypothesis"],
     "uncertainty_notes": "Charity vs trading-Ltd is a structural pattern — could be charity's trading arm or a separate entity. Human judgement needed"},

    # 16. Manchester University NHS FT ↔ Manchester Surgical Services Limited — reject
    {"queue_id": "a52b13c2508cbc78", "recommendation": "reject_merge", "confidence": 0.9,
     "left_canonical_id": "GB-CHC-1049274", "right_canonical_id": "GB-COH-07053471",
     "evidence": ["Completely different entities (NHS trust vs commercial surgical Ltd)",
                  "Splink matched on 'Manchester' prefix only",
                  "Right has its own CH 07053471"],
     "uncertainty_notes": ""},

    # 17. Manchester University NHS FT ↔ Manchester University Foundation Trust
    {"queue_id": "ef088b1c13cccb4a", "recommendation": "approve_merge", "confidence": 0.9,
     "survivor_canonical_id": "GB-CHC-1049274", "absorbed_canonical_id": "GB-FTS-116183",
     "evidence": ["Publisher omitted 'NHS' from the trust name",
                  "Same Manchester locality",
                  "Right has no CH — publisher variant"],
     "uncertainty_notes": ""},

    # 18. Manchester University NHS FT ↔ Manchester Foundation Trust — defer
    {"queue_id": "217b362a1b7af376", "recommendation": "defer", "confidence": 0.5,
     "left_canonical_id": "GB-CHC-1049274", "right_canonical_id": "GB-FTS-136463",
     "evidence": ["Short form 'Manchester Foundation Trust' is ambiguous",
                  "Could refer to MFT, Greater Manchester Mental Health FT, or The Christie FT",
                  "Left's name_variants don't include this short form"],
     "uncertainty_notes": "Too ambiguous to merge without additional evidence (postcode, award titles)"},

    # 19. Manchester University NHS FT ↔ Manchester University Hospitals NHSFT
    {"queue_id": "134cb7347105b604", "recommendation": "approve_merge", "confidence": 0.92,
     "survivor_canonical_id": "GB-CHC-1049274", "absorbed_canonical_id": "GB-FTS-155693",
     "evidence": ["'Manchester University Hospitals' is the legacy pre-merger name",
                  "NHSFT is the abbreviated form of NHS Foundation Trust",
                  "Right's name_variants include 'Manchester University NHS Foundation Trust' verbatim"],
     "uncertainty_notes": ""},

    # 20. Manchester University NHS FT ↔ Manchester University Hospital NHS Foundation Trust.
    {"queue_id": "195e6d686637f256", "recommendation": "approve_merge", "confidence": 0.95,
     "survivor_canonical_id": "GB-CHC-1049274", "absorbed_canonical_id": "GB-FTS-157529",
     "evidence": ["Trivial variant: singular 'Hospital' + trailing period",
                  "Same Manchester locality"],
     "uncertainty_notes": ""},
]

_STATUS = {"approve_merge": "approved", "reject_merge": "rejected", "defer": "deferred"}


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    LEDGER.parent.mkdir(parents=True, exist_ok=True)

    approved = rejected = deferred = skipped = 0

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        for d in DECISIONS:
            row = conn.execute(
                "SELECT status, left_canonical_id, right_canonical_id, left_name, right_name "
                "FROM adjudication_queue WHERE queue_id = ?",
                (d["queue_id"],),
            ).fetchone()
            if row is None:
                print(f"[apply] queue_id={d['queue_id']} not found — skipping")
                skipped += 1
                continue
            if row[0] != "pending":
                print(f"[apply] queue_id={d['queue_id']} already {row[0]!r} — skipping")
                skipped += 1
                continue

            status = _STATUS[d["recommendation"]]
            decision_record = {
                **d, "decision_type": "supplier_merge", "batch_id": BATCH_ID,
                "adjudicator": "morgan_ledger", "reviewed_at": now, "status": status,
                "left_canonical_id_snapshot": row[1], "right_canonical_id_snapshot": row[2],
                "left_name_snapshot": row[3], "right_name_snapshot": row[4],
            }

            if d["recommendation"] == "approve_merge":
                survivor = d["survivor_canonical_id"]
                absorbed = d["absorbed_canonical_id"]
                n_moved = conn.execute(
                    "UPDATE supplier_to_canonical SET canonical_id = ? WHERE canonical_id = ?",
                    (survivor, absorbed),
                ).rowcount
                conn.execute(
                    "DELETE FROM canonical_suppliers WHERE canonical_id = ?",
                    (absorbed,),
                )
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
                approved += 1
                print(f"[apply] APPROVED {d['queue_id']}  {absorbed} -> {survivor}  ({n_moved} moved)")
            elif d["recommendation"] == "reject_merge":
                rejected += 1
                print(f"[apply] REJECTED {d['queue_id']}")
            else:
                deferred += 1
                print(f"[apply] DEFERRED {d['queue_id']}")

            conn.execute(
                "UPDATE adjudication_queue SET status = ?, decision_json = ?, reviewed_at = ? WHERE queue_id = ?",
                (status, json.dumps(decision_record), now, d["queue_id"]),
            )
            with LEDGER.open("a") as f:
                f.write(json.dumps(decision_record) + "\n")

        conn.commit()

    print()
    print(f"[apply] batch_002: {approved} approved, {rejected} rejected, {deferred} deferred, {skipped} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
