#!/usr/bin/env python3
"""
Classify FTS notices by service category using the 13-category taxonomy.

For each unclassified notice in the £1m+ universe, reads title + description
and assigns the best-fit service category. Uses a two-pass approach:

  Pass 1 — Keyword scoring (free, fast, catches ~60-70%)
  Pass 2 — LLM classification for ambiguous/unmatched (optional, ~£20-50 total)

Usage:
    python3 agent/classify-services.py                    # keyword pass only
    python3 agent/classify-services.py --with-llm         # keyword + LLM for residual
    python3 agent/classify-services.py --limit 100        # test on first 100
    python3 agent/classify-services.py --stats-only       # just show current coverage

Requires: ANTHROPIC_API_KEY env var for --with-llm mode.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "bid_intel.db")
TAXONOMY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "pwin-platform", "knowledge", "service-taxonomy.json",
)

# Keyword patterns per category — each tuple is (category_id, weight, pattern)
# Higher weight = stronger signal. Patterns are compiled regex.
KEYWORD_RULES = []


def load_taxonomy():
    """Load taxonomy and build keyword rules from examples + descriptions."""
    with open(TAXONOMY_PATH) as f:
        tax = json.load(f)

    rules = []
    for cat in tax["categories"]:
        cid = cat["id"]
        # Build patterns from examples (strong signals, weight 3)
        for ex in cat.get("examples", []):
            rules.append((cid, 3, re.compile(re.escape(ex.lower()))))
        # Build patterns from description keywords (weaker, weight 1)
        desc_words = [w.strip(",. ") for w in cat["description"].lower().split()
                      if len(w) > 4 and w not in ("services", "service", "delivery", "management",
                                                   "operational", "distinct", "building", "support")]
        # Use 2-word phrases from description for better precision
        desc_tokens = cat["description"].lower().split()
        for i in range(len(desc_tokens) - 1):
            phrase = f"{desc_tokens[i]} {desc_tokens[i+1]}"
            if len(phrase) > 8:
                rules.append((cid, 1, re.compile(re.escape(phrase))))

    return tax, rules


def score_notice(title: str, description: str, rules: list) -> tuple[str | None, float]:
    """Score a notice against all keyword rules. Returns (best_category, score)."""
    text = f"{(title or '')} {(description or '')[:500]}".lower()
    scores: dict[str, float] = {}

    for cid, weight, pattern in rules:
        if pattern.search(text):
            scores[cid] = scores.get(cid, 0) + weight

    if not scores:
        return None, 0

    best = max(scores, key=scores.get)
    # Only accept if the best score is above threshold and has clear lead
    best_score = scores[best]
    if best_score < 3:
        return None, best_score  # Too weak — send to LLM

    # Check for ambiguity — if second-best is within 60% of best, it's ambiguous
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) > 1 and sorted_scores[1] >= best_score * 0.6:
        return None, best_score  # Ambiguous — send to LLM

    return best, best_score


def classify_with_llm(notices: list, taxonomy: dict, batch_size: int = 20) -> dict:
    """Classify notices using Claude API. Returns {ocid: category_id}."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  WARNING: ANTHROPIC_API_KEY not set, skipping LLM classification")
        return {}

    import urllib.request

    categories_prompt = "\n".join(
        f"- {cat['id']}: {cat['name']} — {cat['description']}"
        for cat in taxonomy["categories"]
    )

    results = {}
    total = len(notices)

    for i in range(0, total, batch_size):
        batch = notices[i:i + batch_size]
        notices_text = "\n\n".join(
            f"NOTICE {n['ocid']}:\nTitle: {n['title']}\nDescription: {(n['description'] or '')[:300]}"
            for n in batch
        )

        prompt = f"""You are classifying UK public sector procurement notices into service categories.

Categories:
{categories_prompt}

For each notice below, respond with ONLY the notice ID and the single best-fit category ID, one per line. Format: OCID|category_id

If genuinely unclear, use: OCID|unclassified

{notices_text}"""

        body = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read())
            text = resp["content"][0]["text"]
            for line in text.strip().split("\n"):
                if "|" in line:
                    parts = line.strip().split("|")
                    if len(parts) == 2:
                        ocid, cat = parts[0].strip(), parts[1].strip()
                        if any(c["id"] == cat for c in taxonomy["categories"]):
                            results[ocid] = cat
        except Exception as e:
            print(f"  LLM batch {i // batch_size + 1} failed: {e}")

        if (i // batch_size + 1) % 10 == 0:
            print(f"  LLM batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}...")

    return results


def add_columns(conn: sqlite3.Connection):
    """Add service classification columns if not present."""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(notices)").fetchall()]
    for col, typ in [("service_category", "TEXT"), ("service_match_method", "TEXT")]:
        if col not in cols:
            conn.execute(f"ALTER TABLE notices ADD COLUMN {col} {typ}")
            print(f"  Added {col} column")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notices_service ON notices(service_category)")
    conn.commit()


def print_stats(conn: sqlite3.Connection):
    """Print classification coverage stats."""
    print("\n=== SERVICE CLASSIFICATION COVERAGE ===")

    total = conn.execute("""SELECT COUNT(DISTINCT a.id) FROM awards a JOIN notices n ON a.ocid = n.ocid
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6""").fetchone()[0]
    classified = conn.execute("""SELECT COUNT(DISTINCT a.id) FROM awards a JOIN notices n ON a.ocid = n.ocid
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6 AND n.service_category IS NOT NULL""").fetchone()[0]
    print(f"  £1m+ awards classified: {classified:,} of {total:,} ({100 * classified / total:.1f}%)")

    print(f"\n  By category:")
    for r in conn.execute("""
        SELECT n.service_category, COUNT(DISTINCT a.id) awards, SUM(a.value_amount_gross) total_val
        FROM awards a JOIN notices n ON a.ocid = n.ocid
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6 AND n.service_category IS NOT NULL
        GROUP BY n.service_category ORDER BY awards DESC
    """):
        print(f"    {r[1]:>6,}  £{(r[2] or 0) / 1e6:>10,.0f}m  {r[0]}")

    print(f"\n  By match method:")
    for r in conn.execute("""
        SELECT service_match_method, COUNT(*) FROM notices
        WHERE service_category IS NOT NULL GROUP BY service_match_method
    """):
        print(f"    {r[1]:>8,}  {r[0]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-llm", action="store_true", help="Use LLM for ambiguous notices")
    parser.add_argument("--limit", type=int, help="Limit number of notices to classify")
    parser.add_argument("--stats-only", action="store_true", help="Just print current stats")
    parser.add_argument("--reclassify", action="store_true", help="Re-classify all, not just unclassified")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    add_columns(conn)

    if args.stats_only:
        print_stats(conn)
        conn.close()
        return

    taxonomy, rules = load_taxonomy()
    print(f"Loaded {len(taxonomy['categories'])} categories, {len(rules)} keyword rules")

    # Fetch notices to classify
    where_clause = "" if args.reclassify else "AND n.service_category IS NULL"
    limit_clause = f"LIMIT {args.limit}" if args.limit else ""
    notices = conn.execute(f"""
        SELECT DISTINCT n.ocid, n.title, n.description
        FROM notices n JOIN awards a ON a.ocid = n.ocid
        WHERE a.status = 'active' AND a.value_amount_gross >= 1e6
        {where_clause}
        {limit_clause}
    """).fetchall()
    print(f"\nClassifying {len(notices)} notices...")

    # Pass 1: Keyword scoring
    keyword_matched = 0
    ambiguous = []
    for n in notices:
        cat, score = score_notice(n["title"], n["description"], rules)
        if cat:
            conn.execute("UPDATE notices SET service_category = ?, service_match_method = 'keyword' WHERE ocid = ?",
                         (cat, n["ocid"]))
            keyword_matched += 1
        else:
            ambiguous.append(dict(n))

    conn.commit()
    print(f"  Pass 1 (keyword): {keyword_matched:,} classified, {len(ambiguous):,} ambiguous/unmatched")

    # Pass 2: LLM classification (optional)
    if args.with_llm and ambiguous:
        print(f"\n  Pass 2 (LLM): classifying {len(ambiguous)} notices...")
        llm_results = classify_with_llm(ambiguous, taxonomy)
        llm_matched = 0
        for ocid, cat in llm_results.items():
            conn.execute("UPDATE notices SET service_category = ?, service_match_method = 'llm' WHERE ocid = ?",
                         (cat, ocid))
            llm_matched += 1
        conn.commit()
        print(f"  Pass 2 (LLM): {llm_matched:,} classified")

    print_stats(conn)
    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
