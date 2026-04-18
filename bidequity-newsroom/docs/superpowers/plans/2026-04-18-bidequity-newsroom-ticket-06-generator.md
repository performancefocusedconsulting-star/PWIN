# BidEquity Newsroom — Ticket 6: Generator Stage

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the draft generation stage — clusterer, generator worker, scheduler integration, prompt files, and eval golden set — so that every item scoring ≥ 7 at classification time is automatically drafted as a publishable LinkedIn post and newsletter paragraph in BidEquity's "Warm Logic" voice with a clear pursuit-lens insight.

**Architecture:** Items with `relevance_score >= 7` are first grouped by semantic similarity (pgvector cosine > 0.85 within a 7-day window) by the clusterer; each cluster and each unclustered item then receives one Sonnet 4.6 call with the brand voice, structural templates, and style anchors in a cached system prompt, producing a structured `GeneratorOutput` that is persisted as a `drafts` row. The scheduler wires the clusterer and generator into the existing APScheduler infrastructure as a single post-morning-classifier job at 07:30 UTC.

**Tech Stack:** Anthropic SDK (claude-sonnet-4-6), prompt caching, pgvector clustering, pytest

---

## File Map

```
bidequity-newsroom/
├── prompts/generator/
│   ├── brand_voice.md                         # BidEquity "Warm Logic" voice spec + constraints
│   ├── how_i_work.md                          # Paul's editorial preferences (stub — Paul to complete)
│   └── templates/
│       ├── linkedin_template.md               # Structural template for LinkedIn posts
│       └── newsletter_template.md             # Structural template for newsletter paragraphs
├── src/bidequity/intelligence/
│   ├── clusterer.py                           # Cosine-similarity grouping of recent high-signal items
│   └── generator.py                           # Sonnet call, GeneratorOutput parsing, Draft persistence
├── evals/
│   └── generator_golden.json                  # 10 reference items for manual quality review
└── tests/test_intelligence/
    ├── test_clusterer.py                      # Unit tests for clustering logic
    └── test_generator.py                      # Unit tests for generator worker
```

`bidequity-newsroom/src/bidequity/ingest/scheduler.py` — existing file; `generate_pending_drafts` job added.

---

## Tasks

### Phase 1 — Prompt files (write first, everything downstream depends on them)

- [ ] **1.1** Create `bidequity-newsroom/prompts/generator/brand_voice.md` with the full "Warm Logic" spec (see content below).
- [ ] **1.2** Create `bidequity-newsroom/prompts/generator/templates/linkedin_template.md` with structural template (see content below).
- [ ] **1.3** Create `bidequity-newsroom/prompts/generator/templates/newsletter_template.md` with structural template (see content below).
- [ ] **1.4** Create `bidequity-newsroom/prompts/generator/how_i_work.md` as a stub with placeholder text and a note that Paul should complete it before promoting to production.
- [ ] **1.5** Commit prompt files. Message: `feat(generator): add Warm Logic brand voice and post templates`.

---

### Phase 2 — Tests first (TDD)

- [ ] **2.1** Create `bidequity-newsroom/tests/test_intelligence/test_clusterer.py`:
  - Insert 3 `Item` rows into a test database with mock `VECTOR(1024)` embeddings: `item_a` and `item_b` with cosine similarity 0.92, `item_c` dissimilar (cosine sim ~0.40 to both).
  - Call `cluster_recent_items(session, window_days=7, threshold=0.85)`.
  - Assert one `Cluster` row created.
  - Assert `item_a.id` and `item_b.id` are both in `cluster.item_ids`.
  - Assert `item_c.id` is NOT in any cluster.
  - Assert return value contains exactly one `Cluster`.

- [ ] **2.2** Create `bidequity-newsroom/tests/test_intelligence/test_generator.py`:
  - Mock `AsyncAnthropic.messages.create` to return a valid `GeneratorOutput` JSON block:
    ```json
    {
      "linkedin_post": "Test LinkedIn post content here.",
      "newsletter_para": "Test newsletter paragraph here.",
      "so_what_line": "Bid teams should act now.",
      "supporting_points": ["Point one.", "Point two.", "Point three."]
    }
    ```
  - Call `generate_draft(item, classification, client, session, prompt_version="generator-v1.0")`.
  - Assert a `Draft` row persisted with `linkedin_post`, `newsletter_para`, `so_what_line`, `supporting_points` matching mock output.
  - Assert `draft.item_id == item.id`.
  - Assert `draft.cost_usd` is not None and > 0.
  - Assert `draft.status == "pending"`.
  - Call `generate_draft` again with a `cluster` argument containing 2 additional items; assert all 3 cluster items' body text appears in the captured prompt's user message.
  - Assert `draft.cluster_id == cluster.id` when cluster is provided.

- [ ] **2.3** Run `pytest bidequity-newsroom/tests/test_intelligence/ -x` — confirm both test files fail with `ImportError` (modules not yet created). This is the expected TDD red state.

- [ ] **2.4** Commit failing tests. Message: `test(generator): add failing tests for clusterer and generator`.

---

### Phase 3 — Clusterer implementation

- [ ] **3.1** Create `bidequity-newsroom/src/bidequity/intelligence/clusterer.py`:

```python
"""
Semantic clustering of recent high-signal items using pgvector embeddings.

Groups items with cosine similarity > threshold within a rolling window.
Each cluster reduces N redundant drafts to one. Items already assigned to
a cluster in a prior run are skipped (idempotent).
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Sequence

from sqlmodel import Session, select

from bidequity.models import Cluster, Item


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Pure-Python cosine similarity. Avoids N^2 SQL query cost at this volume."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


async def cluster_recent_items(
    session: Session,
    window_days: int = 7,
    threshold: float = 0.85,
) -> list[Cluster]:
    """
    Group items from the last `window_days` with relevance_score >= 7 by
    semantic similarity. Items already assigned to a cluster are skipped.

    Algorithm:
      1. Load candidate items (with embeddings) from the window.
      2. Exclude items already in a cluster.
      3. For each pair, compute cosine similarity Python-side.
      4. Union-find grouping: items above threshold join the same group.
      5. Groups of 2+ items become Cluster rows; singletons are left unclustered.

    Returns list of new Cluster rows created in this run.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    # Load candidate items — those with embeddings, high relevance, in window
    stmt = (
        select(Item)
        .join(Item.classifications)  # join to get relevance_score
        .where(Item.ingested_at > cutoff)
        .where(Item.embedding.is_not(None))
        # Filter: relevance_score >= 7 via joined classification
        # (use the latest classification per item)
    )
    items: Sequence[Item] = session.exec(stmt).all()

    # Exclude items already in a cluster
    already_clustered: set[int] = set()
    for cluster in session.exec(select(Cluster)).all():
        already_clustered.update(cluster.item_ids)

    candidates = [item for item in items if item.id not in already_clustered]

    if len(candidates) < 2:
        return []

    # Union-find
    parent: dict[int, int] = {item.id: item.id for item in candidates}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        parent[find(x)] = find(y)

    # Compare all pairs; union those above threshold
    for i, item_a in enumerate(candidates):
        vec_a: list[float] = list(item_a.embedding)
        for item_b in candidates[i + 1 :]:
            vec_b: list[float] = list(item_b.embedding)
            sim = _cosine_similarity(vec_a, vec_b)
            if sim >= threshold:
                union(item_a.id, item_b.id)

    # Group by root
    groups: dict[int, list[int]] = {}
    for item in candidates:
        root = find(item.id)
        groups.setdefault(root, []).append(item.id)

    # Persist clusters for groups of 2+
    new_clusters: list[Cluster] = []
    for root, ids in groups.items():
        if len(ids) >= 2:
            # Use first item's title as the cluster theme label
            lead = next(c for c in candidates if c.id == ids[0])
            theme = lead.title[:120] if lead.title else f"cluster-{root}"
            cluster = Cluster(theme=theme, item_ids=ids)
            session.add(cluster)
            new_clusters.append(cluster)

    session.commit()
    for c in new_clusters:
        session.refresh(c)

    return new_clusters
```

- [ ] **3.2** Run `pytest bidequity-newsroom/tests/test_intelligence/test_clusterer.py -x` — confirm tests pass.
- [ ] **3.3** Commit. Message: `feat(generator): implement clusterer with union-find cosine grouping`.

---

### Phase 4 — Generator implementation

- [ ] **4.1** Create `bidequity-newsroom/src/bidequity/intelligence/generator.py`:

```python
"""
Draft generator: takes a high-signal item + optional cluster context and
produces a LinkedIn post, newsletter paragraph, so-what line, and 3 supporting
points in BidEquity's Warm Logic voice, via Claude Sonnet 4.6.

Prompt caching: the system prompt (brand voice + templates + style anchors) is
sent with cache_control so the 1-hour cache TTL applies. Per-item user prompt
is never cached (unique per item).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from anthropic import AsyncAnthropic
from pydantic import BaseModel
from sqlmodel import Session, select

from bidequity.models import Classification, Cluster, Draft, Item, Publication

PROMPTS_DIR = Path(__file__).parents[4] / "prompts" / "generator"


class GeneratorOutput(BaseModel):
    linkedin_post: str
    newsletter_para: str
    so_what_line: str
    supporting_points: list[str]  # exactly 3

    def validate_supporting_points(self) -> None:
        if len(self.supporting_points) != 3:
            raise ValueError(
                f"supporting_points must have exactly 3 items, got {len(self.supporting_points)}"
            )


def _load_prompt_file(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


def _load_style_anchors(session: Session, n: int = 3) -> list[str]:
    """
    Load the top-N published posts by engagement (reactions + shares) in the
    last 30 days for style anchoring. Returns list of linkedin_post strings.
    Returns empty list if no published posts yet.
    """
    from bidequity.models import Metrics

    # Join publications -> drafts -> metrics, order by engagement desc
    # Simplified: return last N published linkedin posts
    pubs = session.exec(
        select(Publication)
        .where(Publication.channel == "linkedin")
        .where(Publication.status == "published")
        .order_by(Publication.published_at.desc())
        .limit(n)
    ).all()
    return [p.final_content for p in pubs]


def _load_published_this_week(session: Session) -> list[str]:
    """
    Returns linkedin_post text from all items published in the current
    calendar week. Used to avoid repetition of angles.
    """
    from datetime import datetime, timedelta, timezone

    week_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=datetime.now(timezone.utc).weekday())

    pubs = session.exec(
        select(Publication)
        .where(Publication.channel == "linkedin")
        .where(Publication.published_at >= week_start)
    ).all()
    return [p.final_content for p in pubs]


def _build_system_prompt(style_anchors: list[str]) -> str:
    brand_voice = _load_prompt_file("brand_voice.md")
    how_i_work = _load_prompt_file("how_i_work.md")
    linkedin_template = _load_prompt_file("templates/linkedin_template.md")
    newsletter_template = _load_prompt_file("templates/newsletter_template.md")

    anchors_section = ""
    if style_anchors:
        formatted = "\n\n---\n\n".join(
            f"EXAMPLE {i + 1}:\n{post}" for i, post in enumerate(style_anchors)
        )
        anchors_section = f"""
## Style anchors (recent high-performing posts — match this register)

{formatted}
"""

    return f"""You are the editorial intelligence for BidEquity, a UK strategic pursuit consultancy.
Your job is to draft LinkedIn posts and newsletter paragraphs that give procurement and bid professionals
a clear, pursuit-relevant insight — not generic commentary.

{brand_voice}

{how_i_work}

## LinkedIn post structure

{linkedin_template}

## Newsletter paragraph structure

{newsletter_template}

{anchors_section}

## Output contract

Respond ONLY with valid JSON matching this exact schema:

{{
  "linkedin_post": "<string: full LinkedIn post, 1,200–1,500 chars>",
  "newsletter_para": "<string: newsletter paragraph, 150–250 words>",
  "so_what_line": "<string: one sentence, the pursuit move>",
  "supporting_points": ["<string>", "<string>", "<string>"]
}}

No markdown fences. No commentary outside the JSON object.
"""


def _build_user_prompt(
    item: Item,
    classification: Classification,
    cluster_items: list[Item],
    published_this_week: list[str],
) -> str:
    cluster_section = ""
    if cluster_items:
        related = "\n\n".join(
            f"RELATED ITEM {i + 1}:\nTitle: {ci.title}\n\n{ci.body_text[:600]}"
            for i, ci in enumerate(cluster_items[:3])
        )
        cluster_section = f"""
## Related items covering the same story (synthesise — do not repeat each separately)

{related}
"""

    week_section = ""
    if published_this_week:
        week_section = f"""
## Already published this week (avoid repeating these angles)

{chr(10).join(f'- {p[:200]}' for p in published_this_week)}
"""

    return f"""## Item to draft

Title: {item.title}
Source: {item.source_id}
Published: {item.published_at}

{item.body_text[:2000]}

## Classifier output

Relevance score: {classification.relevance_score}/10
Signal type: {classification.signal_type}
Sectors: {', '.join(classification.sectors)}
Summary: {classification.summary}
Pursuit implication: {classification.pursuit_implication or 'Not provided'}
Suggested hook: {classification.content_angle_hook or 'Not provided'}
{cluster_section}{week_section}
Now produce the JSON draft.
"""


async def generate_draft(
    item: Item,
    classification: Classification,
    client: AsyncAnthropic,
    session: Session,
    prompt_version: str,
    cluster: Optional[Cluster] = None,
) -> Draft:
    """
    Generates a LinkedIn post, newsletter paragraph, so-what line, and 3
    supporting points for the given item. Caches the system prompt.

    Args:
        item: The Item row to draft content for.
        classification: The latest Classification for the item.
        client: AsyncAnthropic client instance.
        session: SQLModel session for DB writes.
        prompt_version: Semantic version string (e.g. "generator-v1.0").
        cluster: Optional Cluster containing related items to synthesise.

    Returns:
        Persisted Draft row with status "pending".
    """
    style_anchors = _load_style_anchors(session)
    published_this_week = _load_published_this_week(session)

    cluster_items: list[Item] = []
    if cluster is not None:
        other_ids = [i for i in cluster.item_ids if i != item.id]
        cluster_items = [
            session.get(Item, iid)
            for iid in other_ids[:3]
            if session.get(Item, iid) is not None
        ]

    system_prompt = _build_system_prompt(style_anchors)
    user_prompt = _build_user_prompt(
        item, classification, cluster_items, published_this_week
    )

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_text = response.content[0].text.strip()

    # Strip markdown fences if model wraps anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    output = GeneratorOutput.model_validate_json(raw_text)
    output.validate_supporting_points()

    # Cost tracking
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    # Sonnet 4.6: $3/M input, $15/M output (USD)
    cost_usd = (input_tokens * 3 + output_tokens * 15) / 1_000_000

    draft = Draft(
        item_id=item.id,
        cluster_id=cluster.id if cluster else None,
        prompt_version=prompt_version,
        linkedin_post=output.linkedin_post,
        newsletter_para=output.newsletter_para,
        so_what_line=output.so_what_line,
        supporting_points=output.supporting_points,
        cost_usd=cost_usd,
        status="pending",
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft
```

- [ ] **4.2** Run `pytest bidequity-newsroom/tests/test_intelligence/test_generator.py -x` — confirm tests pass.
- [ ] **4.3** Commit. Message: `feat(generator): implement generator worker with prompt caching and Draft persistence`.

---

### Phase 5 — Scheduler integration

- [ ] **5.1** Open `bidequity-newsroom/src/bidequity/ingest/scheduler.py` and add the `generate_pending_drafts` job:

```python
async def generate_pending_drafts() -> None:
    """
    Runs after the morning classifier batch (07:30 UTC).

    1. Cluster recent high-signal items (cosine > 0.85, last 7 days).
    2. For each item with relevance_score >= 7 and no draft yet:
       - If the item is in a new cluster, generate one draft for the cluster lead.
       - If unclustered, generate one draft for the item.
    Skips items already in clusters that already have a draft.
    """
    from anthropic import AsyncAnthropic

    from bidequity.common.config import settings
    from bidequity.common.db import get_session
    from bidequity.intelligence.clusterer import cluster_recent_items
    from bidequity.intelligence.generator import generate_draft
    from bidequity.models import Classification, Draft, Item

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    prompt_version = settings.generator_prompt_version  # e.g. "generator-v1.0"

    with get_session() as session:
        # Step 1: cluster
        new_clusters = await cluster_recent_items(session)

        # Build set of cluster lead item IDs (first in each cluster)
        cluster_leads: dict[int, "Cluster"] = {}
        for cluster in new_clusters:
            lead_id = cluster.item_ids[0]
            cluster_leads[lead_id] = cluster

        # Build set of all clustered item IDs (non-leads skipped)
        all_clustered_ids: set[int] = set()
        for cluster in new_clusters:
            all_clustered_ids.update(cluster.item_ids)

        # Step 2: find items needing drafts
        # Items with score >= 7, ingested in last 7 days, no draft yet
        from datetime import datetime, timedelta, timezone
        from sqlmodel import select, not_, exists

        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        candidate_items = session.exec(
            select(Item)
            .join(Classification, Classification.item_id == Item.id)
            .where(Item.ingested_at > cutoff)
            .where(Classification.relevance_score >= 7)
            .where(
                not_(
                    exists(
                        select(Draft.id).where(Draft.item_id == Item.id)
                    )
                )
            )
        ).all()

        for item in candidate_items:
            classification = session.exec(
                select(Classification)
                .where(Classification.item_id == item.id)
                .order_by(Classification.classified_at.desc())
                .limit(1)
            ).first()

            if classification is None:
                continue

            # Non-lead clustered items: skip (cluster lead covers them)
            if item.id in all_clustered_ids and item.id not in cluster_leads:
                continue

            cluster = cluster_leads.get(item.id)
            await generate_draft(
                item=item,
                classification=classification,
                client=client,
                session=session,
                prompt_version=prompt_version,
                cluster=cluster,
            )
```

- [ ] **5.2** Register the job in the APScheduler setup block (within the same file's `configure_scheduler` function or equivalent):

```python
scheduler.add_job(
    generate_pending_drafts,
    "cron",
    hour=7,
    minute=30,
    id="generate_pending_drafts",
    replace_existing=True,
    misfire_grace_time=3600,
)
```

- [ ] **5.3** Add `generator_prompt_version: str = "generator-v1.0"` to the `Settings` model in `bidequity/common/config.py`.
- [ ] **5.4** Run full test suite: `pytest bidequity-newsroom/tests/ -x`. Confirm all tests pass.
- [ ] **5.5** Commit. Message: `feat(generator): wire generate_pending_drafts into APScheduler at 07:30 UTC`.

---

### Phase 6 — Eval golden set

- [ ] **6.1** Create `bidequity-newsroom/evals/generator_golden.json` with 10 items drawn from the classifier golden set (or representative items). Each entry contains the input (`title`, `body`, `classification`) and `reference_notes` (what a good draft must contain — not exact text). See seed content below.
- [ ] **6.2** Commit. Message: `eval(generator): add 10-item golden set for manual quality review`.

---

### Phase 7 — Final verification

- [ ] **7.1** Run `pytest bidequity-newsroom/tests/ -v` — all tests pass.
- [ ] **7.2** Run `ruff check bidequity-newsroom/src/ bidequity-newsroom/tests/` — no errors.
- [ ] **7.3** Run `mypy bidequity-newsroom/src/bidequity/intelligence/clusterer.py bidequity-newsroom/src/bidequity/intelligence/generator.py` — no errors (or document any `type: ignore` with rationale).
- [ ] **7.4** Final commit. Message: `chore(generator): final lint and type-check pass — Ticket 6 complete`.

---

## Prompt file content

### `brand_voice.md`

```markdown
# BidEquity Brand Voice — "Warm Logic"

## What Warm Logic means

BidEquity writes like a senior pursuit strategist who actually reads — not a content
marketer. Every piece earns trust by being analytically precise and genuinely useful.
The warmth comes from care: we care that the reader leaves better equipped than they
arrived. The logic comes from evidence: we don't speculate, we trace implications.

Warm: we write to people, not about people. We acknowledge that bidding is hard,
that the stakes are high, and that most teams are under-resourced. We don't talk down.

Logic: every post leads to a specific, defensible move. If the insight doesn't help
someone decide whether to bid, how to position, or what to watch for next, cut it.

## Tone

- Confident without being arrogant. We know what we're talking about; we don't need
  to prove it through jargon or volume.
- Direct. Lead with the insight. Do not warm up, circulate, or contextualise before
  saying the thing.
- Specific. Name the programme, the buyer, the framework. "A major government
  department" is not good enough.
- Grounded. If it's speculative, flag it. "This is our read" or "watch for" signals
  appropriate uncertainty.
- Human. Contractions are fine. Passive voice is not.

## What BidEquity never does

- Never name a specific active bid in progress (competitor intelligence risk).
- Never fabricate quotes. If a source said it, cite it. If no one said it, don't
  attribute it.
- Never make investment recommendations.
- Never use em-dashes. LinkedIn renders them as hyphens; the rhythm breaks. Use
  a colon or a full stop instead.
- Never use "delve", "leverage" (as a verb), "unlock", "game-changer",
  "transformative", or "stakeholder engagement" as filler.
- Never pad to length. Every sentence must carry weight.

## Hard length constraints

- LinkedIn posts: 1,200–1,500 characters (not words). The hook is the first line.
  LinkedIn truncates at ~200 chars before "see more" — make the first line earn
  the click.
- Newsletter paragraphs: 150–250 words. One idea per paragraph. Signposted.
- So-what line: one sentence, maximum 25 words. The pursuit move, stated plainly.

## The pursuit lens (the defining element)

Every piece must answer: what does this mean for someone deciding whether to pursue
a bid? Not "this is interesting news". Not "this is worth watching". The move.

BAD (generic trade-press framing):
> "The MOD has published an updated Defence Procurement Policy Manual, replacing
> the previous version from 2022. The update introduces new guidance on commercial
> frameworks and social value requirements."

GOOD (pursuit-lens framing):
> "MOD's updated procurement manual puts social value scoring into every future
> framework competition — not as a nice-to-have but as a weighted criterion. Bid
> teams that have been treating social value as a compliance box will lose ground
> to those who have built genuine programmes. The window to develop evidence is
> now, before the frameworks open."

BAD (generic):
> "NHS England has announced a new digital transformation strategy setting out
> its ambitions for the next five years, including greater use of AI and
> interoperability standards."

GOOD (pursuit-lens):
> "NHS England's five-year digital strategy signals a shift from buy-the-platform
> to prove-the-outcomes. Suppliers who win in this cycle will be those with
> reference sites showing measurable interoperability gains — not those with
> the most impressive slide decks. If you're building a bid case for an NHS
> digital opportunity in the next 18 months, your win strategy needs a live
> reference site or it has a gap."

## Hashtag strategy

Always end LinkedIn posts with 3–5 hashtags on a new line. Preferred tags:
#BidEquity #UKProcurement #PublicSector #BidStrategy #PursuitIntelligence
Sector-specific additions as appropriate:
#DefenceProcurement #NHSDigital #LocalGovernment #JusticeProcurement

## Citing sources

Always include a source reference — either the publication name in-text
("per the NAO report published Monday") or a URL at the end of the post.
```

---

### `templates/linkedin_template.md`

```markdown
# LinkedIn Post Template

## Structure

**Hook line** (first line, ~100–160 chars)
The grab. State the insight or provocation directly. No scene-setting. No "I was
reading..." No rhetorical question unless it is sharper than the statement form.

Example hooks that work:
- "NHS England just moved the goalposts on digital procurement. Quietly."
- "MOD's new procurement cadence isn't a policy update. It's a capability test."
- "The NAO's findings on ESN don't just expose a programme in trouble — they
  preview what the next generation of technology bids will be evaluated against."

**Development** (2–3 sentences)
What happened and why it matters structurally. Specific. Named. Sourced.
No more than two development sentences — if you need more, the hook was not sharp enough.

**Pursuit-lens insight** (prefixed "What this means for bid teams:")
One to two sentences. The move. Specific enough to act on.
This is the line that separates BidEquity from trade press.

**Soft CTA** (one sentence, optional but preferred)
Not "follow us for more". A forward-looking prompt that invites engagement.
Examples: "What's your read on this?" / "We're tracking this — DM if you want
the fuller picture." / "Happy to share our framework for thinking about this."

**Hashtags** (new line, 3–5 tags)
```

---

### `templates/newsletter_template.md`

```markdown
# Newsletter Paragraph Template

## Structure

Newsletter paragraphs are written for people reading on a Thursday evening who
want to arrive at Friday knowing what moved in their space. They are not blog posts.
They are not social posts. They are signposted analysis.

**Lead sentence**
States what happened. Specific. Sourced.

**Analysis** (2–4 sentences)
What it means structurally. Who it affects. Why the timing matters.
One sentence per idea. No padding. Use signposting words:
"Notably,..." / "The implication:" / "This matters because..."

**So-what for pursuit teams** (1 sentence, prefixed "For bid teams:")
The pursuit move. Plain language. Specific.

## Length

150–250 words. If it runs longer, something is not specific enough.
Cut the adjectives before you cut the substance.

## Tone

More considered than LinkedIn — this is a reader who has chosen to subscribe,
not a scroll-stopper. You can assume slightly more context. Still no padding.
```

---

## Eval golden set seed content

The `generator_golden.json` file contains 10 items. Entries follow this schema:

```json
{
  "id": "gen-golden-01",
  "title": "...",
  "body": "...",
  "classification": {
    "relevance_score": 8,
    "signal_type": "procurement",
    "sectors": ["..."],
    "summary": "...",
    "pursuit_implication": "...",
    "content_angle_hook": "..."
  },
  "reference_notes": {
    "must_contain": ["..."],
    "must_not_contain": ["..."],
    "quality_criteria": "..."
  }
}
```

The 10 items should cover the signal-type taxonomy spread:
- 2 × procurement (one ITT/ITN, one framework expiry)
- 2 × policy (one with immediate bid implication, one structural/trend)
- 1 × oversight (NAO or PAC report on an active programme)
- 1 × financial (budget announcement or settlement with sector implication)
- 1 × leadership (SRO appointment or exec change at a major buyer)
- 1 × incumbent rebid signal (contract extension or recompete announcement)
- 1 × low-signal item that barely clears the 7 threshold (tests floor quality)
- 1 × multi-item cluster scenario (two related items grouped — tests synthesis)

`reference_notes.must_contain` captures the key facts and pursuit-lens points a
good draft must include. `reference_notes.must_not_contain` captures failure modes
to check against (e.g. "fabricated quotes", "generic commentary without a move").
`reference_notes.quality_criteria` is a one-sentence human judgement guide for
Paul's manual review (e.g. "A passing draft names the programme, cites the NAO
report, and states a specific action for incumbents vs new entrants").

---

## Acceptance criteria

- [ ] All 7 pytest tests pass (3 clusterer + 4 generator).
- [ ] `generate_pending_drafts` scheduler job is registered at 07:30 UTC.
- [ ] `ruff` and `mypy` pass with no errors on the two new intelligence modules.
- [ ] Both `clusterer.py` and `generator.py` exist with the function signatures matching the spec exactly.
- [ ] Prompt caching `cache_control: ephemeral` is present on the system prompt in `generate_draft`.
- [ ] `Draft.cost_usd` is populated on every generated draft.
- [ ] Paul reviews 10 golden items manually and judges output "publishable with light edits" on at least 8 of 10.
- [ ] Clustering demonstrably reduces redundant drafts: when two near-identical items are ingested, only one draft is generated.

---

## Notes for the implementing agent

- **Prompt files are production code.** Never overwrite them without bumping `prompt_version` and re-running the golden eval.
- **`how_i_work.md` is a stub.** Paul must complete it before the generator prompt is promoted to production. The stub should say: "TODO: Paul to complete this file with his editorial preferences before promoting generator-v1.0 to production."
- **Cost model.** Sonnet 4.6 pricing used in `generator.py` cost calc: $3/M input, $15/M output. Verify against current Anthropic pricing before first production run.
- **`_cosine_similarity` is Python-side** by design — at ~80 items/week volume, the N^2 pairs are trivial. If volume grows to >500 items/window, switch to a pgvector `<=> operator` query with `ORDER BY ... LIMIT` and a graph-based grouping.
- **Cluster theme label** is the lead item title (truncated to 120 chars). This is a data-quality placeholder — the dashboard ticket (Ticket 7) can allow Paul to rename cluster themes.
- **`how_i_work.md` seeding.** The spec references Paul's Cowork context files. If these are available at `~/.claude/` or equivalent, load them into `how_i_work.md` rather than leaving a stub.
