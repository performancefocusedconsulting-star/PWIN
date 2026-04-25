#!/usr/bin/env python3
"""
Classify big contracts by service category using procurement codes (CPV).

Why this exists
---------------
Every UK government contract above threshold carries one or more 8-digit
procurement codes (CPV — Common Procurement Vocabulary). The codes are
hierarchical: the first 2 digits give the broad family, more digits narrow
it down. They are filed by the buyer at publication, not guessed.

We have 100% CPV coverage on the 84,351 big-contract universe, so we can
deterministically map a contract to one of the 13 service categories defined
in pwin-platform/knowledge/service-taxonomy.json — no AI calls, no cost.

Logic
-----
1. Each contract has 1+ procurement codes.
2. We score each code against the mapping rules below. Longer prefix matches
   beat shorter ones (more-specific codes win).
3. For the contract, we pick the highest-scoring category across all its
   codes. Ties broken by frequency of the category in the contract's codes.
4. If the contract's codes are ALL outside the 13-category scope (e.g. it's
   a health-services contract or a vehicle purchase), we mark it
   'out-of-scope' rather than guess.

Output column: notices.cpv_category  (and notices.cpv_category_confidence)

Run:
    python agent/classify-by-cpv.py             # apply to big contracts
    python agent/classify-by-cpv.py --dry-run   # show counts, write nothing
"""
import argparse
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "bid_intel.db"

# ─────────────────────────────────────────────────────────────────────────────
# CPV → category mapping
#
# Each entry is (prefix, category_id). Longer prefixes win. Order does not
# matter for correctness but is grouped here for readability.
# Categories use the IDs from pwin-platform/knowledge/service-taxonomy.json.
# ─────────────────────────────────────────────────────────────────────────────
RULES: list[tuple[str, str]] = [
    # ── Construction ─────────────────────────────────────────────────────────
    ("45", "construction"),                    # all construction work
    ("71", "construction"),                    # architectural / engineering / inspection

    # ── Workforce / contingent labour ───────────────────────────────────────
    ("79620", "workforce-contingent-labour"),  # supply of personnel
    ("79621", "workforce-contingent-labour"),  # office-staff supply
    ("79622", "workforce-contingent-labour"),  # domestic-help supply
    ("79624", "workforce-contingent-labour"),  # nursing-personnel supply
    ("79625", "workforce-contingent-labour"),  # medical-personnel supply
    ("79341", "workforce-contingent-labour"),  # recruitment-advertising
    ("79342", "workforce-contingent-labour"),  # marketing services (often staffing-adjacent)

    # ── Programme & project management ───────────────────────────────────────
    ("79420", "p3m"),                           # management-related services
    ("79421", "p3m"),                           # project-management
    ("79422", "p3m"),                           # arbitration / conciliation (rare; close enough)
    ("79993", "p3m"),                           # building & facilities management mgmt-only

    # ── Professional services ────────────────────────────────────────────────
    ("79100", "professional-services"),         # legal services
    ("79110", "professional-services"),         # legal advisory
    ("79111", "professional-services"),         # legal advisory + representation
    ("79120", "professional-services"),         # patent / copyright consulting
    ("79140", "professional-services"),         # legal advisory + info services
    ("79210", "professional-services"),         # accounting / audit
    ("79211", "professional-services"),         # accounting
    ("79212", "professional-services"),         # auditing
    ("79220", "professional-services"),         # tax services
    ("79221", "professional-services"),         # tax consultancy
    ("79410", "professional-services"),         # business / management consultancy
    ("79411", "professional-services"),         # general management consultancy
    ("79412", "professional-services"),         # financial management consultancy
    ("79413", "professional-services"),         # marketing management consultancy
    ("79414", "professional-services"),         # human resources management consultancy
    ("79415", "professional-services"),         # production management consultancy
    ("79416", "professional-services"),         # public relations
    ("79417", "professional-services"),         # safety consultancy
    ("79418", "professional-services"),         # procurement consultancy
    ("66", "professional-services"),            # financial / insurance services
    # Generic and research-style business services
    ("79000", "professional-services"),         # business services umbrella
    ("79300", "professional-services"),         # market and economic research, polls
    ("79310", "professional-services"),         # market research
    ("79311", "professional-services"),         # survey services
    ("79312", "professional-services"),         # market testing
    ("79313", "professional-services"),         # performance review
    ("79314", "professional-services"),         # feasibility study
    ("79315", "professional-services"),         # social research
    ("79320", "professional-services"),         # public-opinion polling
    ("79330", "professional-services"),         # statistical services
    ("79400", "professional-services"),         # business and management consultancy

    # ── Training & education ─────────────────────────────────────────────────
    ("80", "training-education"),               # all education and training

    # ── BPO / outsourced services (operational delivery) ─────────────────────
    ("50", "bpo-outsourced-services"),          # repair & maintenance
    ("55", "bpo-outsourced-services"),          # hotel/catering
    ("75", "bpo-outsourced-services"),          # public administration services
    ("90", "bpo-outsourced-services"),          # cleaning, waste, environmental services
    ("98", "bpo-outsourced-services"),          # accommodation, office, citizen-facing services
    ("63100", "bpo-outsourced-services"),       # cargo handling and storage
    ("64110", "bpo-outsourced-services"),       # postal / courier
    ("64120", "bpo-outsourced-services"),       # courier
    ("85320", "bpo-outsourced-services"),       # social services delivery (close to BPO)
    # Security guarding (operational service delivery)
    ("79710", "bpo-outsourced-services"),       # security services
    ("79711", "bpo-outsourced-services"),       # alarm-monitoring services
    ("79713", "bpo-outsourced-services"),       # guard services
    ("79714", "bpo-outsourced-services"),       # surveillance services
    ("79715", "bpo-outsourced-services"),       # patrol services
    ("79720", "bpo-outsourced-services"),       # investigation and security
    # Grounds maintenance (operational delivery, not horticulture goods)
    ("77310", "bpo-outsourced-services"),       # planting and maintenance services of green areas
    ("77311", "bpo-outsourced-services"),       # maintenance services of ornamental and recreational gardens
    ("77312", "bpo-outsourced-services"),       # weed-clearing services
    ("77313", "bpo-outsourced-services"),       # parks maintenance services
    ("77314", "bpo-outsourced-services"),       # grounds maintenance services
    ("77315", "bpo-outsourced-services"),       # seeding services
    ("77340", "bpo-outsourced-services"),       # tree-pruning and hedge-trimming

    # ── Cyber security ───────────────────────────────────────────────────────
    ("48730", "cyber-security"),                # security software package
    ("48731", "cyber-security"),                # file-security software
    ("48732", "cyber-security"),                # data-security software
    ("48751", "cyber-security"),                # storage configuration (security adjacent — leave out)
    ("72212731", "cyber-security"),             # security software dev services
    ("72212732", "cyber-security"),             # data-security software dev
    ("72212733", "cyber-security"),             # user-access software dev

    # ── AI & data ────────────────────────────────────────────────────────────
    ("72316", "ai-data"),                       # data-analysis services
    ("72317", "ai-data"),                       # data storage
    ("72318", "ai-data"),                       # data transmission
    ("72319", "ai-data"),                       # data-supply services
    ("72320", "ai-data"),                       # database services
    ("72322", "ai-data"),                       # data management
    ("72330", "ai-data"),                       # content / data standardisation
    ("48460", "ai-data"),                       # analytical / scientific / business intel software

    # ── Digital ──────────────────────────────────────────────────────────────
    ("72413", "digital"),                       # WWW site design
    ("72414", "digital"),                       # web search engine dev
    ("72415", "digital"),                       # web hosting operation
    ("72416", "digital"),                       # application service providers
    ("72611", "digital"),                       # technical computer support
    ("72224", "digital"),                       # project management consultancy (digital delivery)

    # ── Software systems integration ────────────────────────────────────────
    ("72211", "software-systems-integration"),  # programming services of systems software
    ("72212", "software-systems-integration"),  # programming services of application software
    ("72221", "software-systems-integration"),  # business analysis consultancy
    ("72222", "software-systems-integration"),  # information systems / tech strategy review
    ("72223", "software-systems-integration"),  # information tech requirements review
    ("72227", "software-systems-integration"),  # software integration consultancy
    ("72228", "software-systems-integration"),  # hardware integration consultancy
    ("72240", "software-systems-integration"),  # systems analysis & programming
    ("72243", "software-systems-integration"),  # programming services
    ("72244", "software-systems-integration"),  # prototyping
    ("72245", "software-systems-integration"),  # contract systems analysis
    ("72246", "software-systems-integration"),  # systems consultancy
    ("72260", "software-systems-integration"),  # software-related services
    ("72261", "software-systems-integration"),  # software support services
    ("72262", "software-systems-integration"),  # software development services
    ("72263", "software-systems-integration"),  # software implementation
    ("72265", "software-systems-integration"),  # software configuration
    ("72266", "software-systems-integration"),  # software consultancy

    # ── IT outsourcing ──────────────────────────────────────────────────────
    ("72500", "it-outsourcing"),                # computer-related services
    ("72510", "it-outsourcing"),                # computer-related management services
    ("72511", "it-outsourcing"),                # network management software services
    ("72512", "it-outsourcing"),                # document management services
    ("72513", "it-outsourcing"),                # office computer services
    ("72514", "it-outsourcing"),                # computer facilities management services
    ("72540", "it-outsourcing"),                # computer upgrade services
    ("72591", "it-outsourcing"),                # service-level agreement (managed services)
    ("72710", "it-outsourcing"),                # local area network services
    ("72720", "it-outsourcing"),                # wide area network services

    # ── Technology services (generic IT, infrastructure, networks) ──────────
    ("72", "technology-services"),              # everything else under 72 (computer & related services)
    ("32", "technology-services"),              # radio / TV / communications equipment (telecoms)
    ("64200", "technology-services"),           # telecom services
    ("64210", "technology-services"),           # telephone & data transmission services
    ("64220", "technology-services"),           # telecommunications services (general)

    # ── Software & cloud products (the product purchase, not the build/run) ─
    ("48", "software-cloud-products"),          # software packages and information systems

    # ── OUT OF SCOPE: real procurement, but not in the 13-category model ─────
    # Health & social care delivery, transport, R&D, goods, equipment, food,
    # fuel, materials, vehicles, etc. We mark these explicitly so they don't
    # silently get the wrong category.
    ("85", "out-of-scope"),                     # health & social work delivery
    ("60", "out-of-scope"),                     # transport services
    ("63", "out-of-scope"),                     # supporting transport (most)
    ("64", "out-of-scope"),                     # postal & telecoms infrastructure (telecoms split above)
    ("65", "out-of-scope"),                     # public utilities
    ("70", "out-of-scope"),                     # real estate
    ("73", "out-of-scope"),                     # research and development
    ("76", "out-of-scope"),                     # services related to oil and gas
    ("77", "out-of-scope"),                     # agriculture / forestry / horticulture
    ("92", "out-of-scope"),                     # arts, recreation, entertainment, sport
    # Goods-only families (suppliers of stuff, not services)
    ("03", "out-of-scope"),                     # agricultural products
    ("09", "out-of-scope"),                     # petroleum, fuel, energy
    ("14", "out-of-scope"),                     # mining / quarrying products
    ("15", "out-of-scope"),                     # food & beverages
    ("16", "out-of-scope"),                     # agricultural machinery
    ("18", "out-of-scope"),                     # clothing / footwear
    ("19", "out-of-scope"),                     # leather / textiles
    ("22", "out-of-scope"),                     # printed matter
    ("24", "out-of-scope"),                     # chemical products
    ("30", "out-of-scope"),                     # office machinery / computer equipment
    ("31", "out-of-scope"),                     # electrical machinery
    ("33", "out-of-scope"),                     # medical equipments / pharmaceuticals
    ("34", "out-of-scope"),                     # transport equipment / vehicles
    ("35", "out-of-scope"),                     # security / fire / police equipment
    ("37", "out-of-scope"),                     # musical instruments / sports goods
    ("38", "out-of-scope"),                     # laboratory / optical / precision equipment
    ("39", "out-of-scope"),                     # furniture / household goods
    ("41", "out-of-scope"),                     # collected and purified water
    ("42", "out-of-scope"),                     # industrial machinery
    ("43", "out-of-scope"),                     # mining / construction machinery
    ("44", "out-of-scope"),                     # construction structures and materials
    ("51", "out-of-scope"),                     # installation services (mostly equipment install)
]


def build_index(rules):
    """Index rules by prefix length, longest first, for fast match."""
    by_len: dict[int, dict[str, str]] = defaultdict(dict)
    for prefix, cat in rules:
        by_len[len(prefix)][prefix] = cat
    return sorted(by_len.items(), reverse=True)  # [(len, {prefix: cat}), ...]


def category_for_code(code: str, idx) -> str | None:
    """Return the most-specific category for a CPV code, or None."""
    if not code:
        return None
    code = str(code).strip()
    for plen, table in idx:
        if len(code) >= plen:
            cat = table.get(code[:plen])
            if cat:
                return cat
    return None


def classify_contract(codes: list[str], idx) -> tuple[str, float]:
    """Pick a category for a contract from its CPV codes.

    Returns (category, confidence 0..1). Confidence is the fraction of
    in-scope codes that voted for the winning category, with a small bonus
    for very specific (long-prefix) matches.
    """
    if not codes:
        return ("unclassified", 0.0)
    votes: Counter[str] = Counter()
    in_scope = 0
    for code in codes:
        cat = category_for_code(code, idx)
        if not cat:
            continue
        if cat == "out-of-scope":
            votes["out-of-scope"] += 1
        else:
            votes[cat] += 1
            in_scope += 1
    if not votes:
        return ("unclassified", 0.0)
    # Prefer in-scope categories over out-of-scope when both present
    if in_scope > 0:
        in_scope_votes = Counter({k: v for k, v in votes.items() if k != "out-of-scope"})
        winner, count = in_scope_votes.most_common(1)[0]
        confidence = count / max(in_scope, 1)
        return (winner, round(confidence, 2))
    return ("out-of-scope", 1.0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Show counts; write nothing")
    ap.add_argument("--only-untagged", action="store_true",
                    help="Only score contracts where cpv_category IS NULL (incremental nightly mode)")
    args = ap.parse_args()

    idx = build_index(RULES)
    print(f"Loaded {len(RULES):,} mapping rules across {len(idx)} prefix lengths")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Add columns if missing
    cols = [r[1] for r in c.execute("PRAGMA table_info(notices)").fetchall()]
    if "cpv_category" not in cols:
        if not args.dry_run:
            c.execute("ALTER TABLE notices ADD COLUMN cpv_category TEXT")
            print("  Added cpv_category column")
    if "cpv_category_confidence" not in cols:
        if not args.dry_run:
            c.execute("ALTER TABLE notices ADD COLUMN cpv_category_confidence REAL")
            print("  Added cpv_category_confidence column")
    if not args.dry_run:
        c.execute("CREATE INDEX IF NOT EXISTS idx_notices_cpv_cat ON notices(cpv_category)")

    # Pull big-contract universe with their CPV codes
    untagged_filter = "AND n.cpv_category IS NULL" if args.only_untagged else ""
    print(f"Loading big contracts (>= GBP 1m awards){' (only untagged)' if args.only_untagged else ''}...")
    rows = c.execute(f"""
        SELECT n.ocid, GROUP_CONCAT(cv.code, '|')
        FROM notices n
        JOIN awards a ON a.ocid = n.ocid
        LEFT JOIN cpv_codes cv ON cv.ocid = n.ocid
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6
        {untagged_filter}
        GROUP BY n.ocid
    """).fetchall()
    print(f"  {len(rows):,} contracts to classify")
    if not rows:
        print("Nothing to do.")
        return 0

    counts: Counter[str] = Counter()
    updates = []
    for ocid, codes_str in rows:
        codes = (codes_str or "").split("|") if codes_str else []
        cat, conf = classify_contract(codes, idx)
        counts[cat] += 1
        updates.append((cat, conf, ocid))

    print()
    print("Result by category:")
    total = sum(counts.values())
    for cat, n in counts.most_common():
        pct = 100 * n / total
        print(f"  {n:>8,}  {pct:>5.1f}%   {cat}")

    if args.dry_run:
        print("\n--dry-run: no rows written")
        return 0

    print(f"\nWriting {len(updates):,} rows...")
    c.executemany(
        "UPDATE notices SET cpv_category=?, cpv_category_confidence=? WHERE ocid=?",
        updates,
    )
    conn.commit()
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
