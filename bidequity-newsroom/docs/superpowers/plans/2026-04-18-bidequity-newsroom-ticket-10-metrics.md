# BidEquity Newsroom — Ticket 10: Measurement & Feedback Loop

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collect LinkedIn and Beehiiv engagement metrics at three time checkpoints after every publication, surface the data in the Insights dashboard, auto-inject the top 3 performing posts into the generator's system prompt as style anchors, and send a monthly plain-text cost report by email.

**Architecture:** A `metrics` package under `src/bidequity/metrics/` owns two concerns: collectors (APScheduler one-off jobs that pull the external APIs and persist rows to the `metrics` table) and insights (pure-SQL aggregation queries used by the dashboard and the monthly email job). The generator in `intelligence/generator.py` gains a `get_style_anchor_posts()` call that runs on every generation — not cached — so the anchors rotate as top posts change. The dashboard's existing `/insights` route is extended to call the new aggregators and pass results to an updated `insights.html` template.

**Tech Stack:** LinkedIn Marketing Developer Platform API, Beehiiv API, PostgreSQL aggregation queries, APScheduler (in-process, already wired in Ticket 3), httpx (already a dependency), smtplib (stdlib), Jinja2 (already present), pytest

---

## File Map

```
bidequity-newsroom/
├── src/bidequity/
│   ├── metrics/
│   │   ├── __init__.py                  # package marker, re-exports collect_* and schedule_*
│   │   ├── collectors.py                # LinkedIn + Beehiiv metric collectors + APScheduler registration
│   │   └── insights.py                 # SQL aggregators + monthly cost report emailer
│   └── intelligence/
│       └── generator.py                # MODIFY: add get_style_anchor_posts(); inject into generation call
│   └── dashboard/
│       ├── routes.py                   # MODIFY: extend GET /insights to call insight functions
│       └── templates/
│           └── insights.html           # MODIFY: add cost card, top posts, source table, agreement gauge
└── tests/
    ├── test_metrics/
    │   ├── __init__.py
    │   ├── test_collectors.py          # mock LinkedIn + Beehiiv APIs; assert Metrics rows persisted
    │   └── test_insights.py            # insert fixtures; assert aggregation correctness
    └── conftest.py                     # MODIFY: add shared fixtures for metrics tests (publication, draft chain)
```

---

## Tasks

### Task 1: Write failing tests for collectors

**Files:**
- `bidequity-newsroom/tests/test_metrics/__init__.py`
- `bidequity-newsroom/tests/test_metrics/test_collectors.py`

TDD order: write all collector tests before any production code. Tests will fail at import until `bidequity.metrics.collectors` exists.

- [ ] Create `bidequity-newsroom/tests/test_metrics/__init__.py` (empty):

```python
```

- [ ] Create `bidequity-newsroom/tests/test_metrics/test_collectors.py`:

```python
"""
Tests for bidequity.metrics.collectors.

Tests mock the external HTTP calls (LinkedIn and Beehiiv APIs) and assert
that Metrics rows are created correctly in the database.

Run with: pytest tests/test_metrics/test_collectors.py -v
Requires DATABASE_URL in environment (see conftest.py).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel import Session, select

from bidequity.models import Draft, Item, Metrics, Publication, Source
from bidequity.metrics.collectors import (
    collect_beehiiv_metrics,
    collect_linkedin_metrics,
    schedule_metric_checkpoints,
)


# ---------------------------------------------------------------------------
# LinkedIn collector
# ---------------------------------------------------------------------------

class TestCollectLinkedinMetrics:
    """collect_linkedin_metrics writes a Metrics row with the correct values."""

    def test_persists_metrics_row_at_24h_checkpoint(self, session, sample_publication):
        """
        Given a mock LinkedIn API response with impressions/reactions/comments/shares,
        collect_linkedin_metrics should persist one Metrics row with checkpoint='24h'
        and the correct field values.
        """
        linkedin_response = {
            "elements": [
                {
                    "totalShareStatistics": {
                        "impressionCount": 1200,
                        "likeCount": 47,
                        "commentCount": 8,
                        "shareCount": 12,
                        "clickCount": 31,
                    }
                }
            ]
        }

        mock_client = AsyncMock()
        mock_client.get_share_statistics.return_value = linkedin_response

        import asyncio
        asyncio.get_event_loop().run_until_complete(
            collect_linkedin_metrics(
                publication=sample_publication,
                checkpoint="24h",
                client=mock_client,
                session=session,
            )
        )

        row = session.exec(
            select(Metrics).where(
                Metrics.publication_id == sample_publication.id,
                Metrics.checkpoint == "24h",
            )
        ).first()

        assert row is not None
        assert row.impressions == 1200
        assert row.reactions == 47
        assert row.comments == 8
        assert row.shares == 12
        assert row.checkpoint == "24h"
        assert row.raw_response == linkedin_response
        assert row.opens is None  # LinkedIn does not have opens
        assert row.clicks == 31

    def test_persists_metrics_row_at_72h_checkpoint(self, session, sample_publication):
        """Checkpoint value '72h' is stored verbatim."""
        linkedin_response = {
            "elements": [
                {
                    "totalShareStatistics": {
                        "impressionCount": 1800,
                        "likeCount": 65,
                        "commentCount": 11,
                        "shareCount": 19,
                        "clickCount": 44,
                    }
                }
            ]
        }

        mock_client = AsyncMock()
        mock_client.get_share_statistics.return_value = linkedin_response

        import asyncio
        asyncio.get_event_loop().run_until_complete(
            collect_linkedin_metrics(
                publication=sample_publication,
                checkpoint="72h",
                client=mock_client,
                session=session,
            )
        )

        row = session.exec(
            select(Metrics).where(
                Metrics.publication_id == sample_publication.id,
                Metrics.checkpoint == "72h",
            )
        ).first()

        assert row is not None
        assert row.checkpoint == "72h"
        assert row.impressions == 1800

    def test_handles_empty_elements_gracefully(self, session, sample_publication):
        """
        LinkedIn sometimes returns an empty elements list (post not yet indexed).
        The collector should still persist a Metrics row, with all counters as None,
        rather than raising.
        """
        mock_client = AsyncMock()
        mock_client.get_share_statistics.return_value = {"elements": []}

        import asyncio
        asyncio.get_event_loop().run_until_complete(
            collect_linkedin_metrics(
                publication=sample_publication,
                checkpoint="24h",
                client=mock_client,
                session=session,
            )
        )

        row = session.exec(
            select(Metrics).where(
                Metrics.publication_id == sample_publication.id,
                Metrics.checkpoint == "24h",
            )
        ).first()

        assert row is not None
        assert row.impressions is None
        assert row.reactions is None


# ---------------------------------------------------------------------------
# Beehiiv collector
# ---------------------------------------------------------------------------

class TestCollectBeehiivMetrics:
    """collect_beehiiv_metrics writes a Metrics row with opens and clicks."""

    def test_persists_opens_and_clicks_at_7d_checkpoint(self, session, sample_newsletter_publication):
        """
        Given a mock Beehiiv /publications/{id}/posts/{post_id} response,
        collect_beehiiv_metrics should persist opens and clicks at checkpoint='7d'.
        """
        beehiiv_response = {
            "data": {
                "id": "post_abc123",
                "stats": {
                    "unique_opens": 342,
                    "clicks": 89,
                }
            }
        }

        mock_client = AsyncMock()
        mock_client.get_post_stats.return_value = beehiiv_response

        import asyncio
        asyncio.get_event_loop().run_until_complete(
            collect_beehiiv_metrics(
                publication=sample_newsletter_publication,
                checkpoint="7d",
                client=mock_client,
                session=session,
            )
        )

        row = session.exec(
            select(Metrics).where(
                Metrics.publication_id == sample_newsletter_publication.id,
                Metrics.checkpoint == "7d",
            )
        ).first()

        assert row is not None
        assert row.opens == 342
        assert row.clicks == 89
        assert row.checkpoint == "7d"
        assert row.raw_response == beehiiv_response
        assert row.impressions is None   # Beehiiv does not have impressions

    def test_handles_missing_stats_key_gracefully(self, session, sample_newsletter_publication):
        """
        Beehiiv can return a post without a 'stats' key if analytics aren't ready.
        The collector should persist a row with opens=None, clicks=None, not raise.
        """
        mock_client = AsyncMock()
        mock_client.get_post_stats.return_value = {"data": {"id": "post_xyz"}}

        import asyncio
        asyncio.get_event_loop().run_until_complete(
            collect_beehiiv_metrics(
                publication=sample_newsletter_publication,
                checkpoint="24h",
                client=mock_client,
                session=session,
            )
        )

        row = session.exec(
            select(Metrics).where(
                Metrics.publication_id == sample_newsletter_publication.id,
                Metrics.checkpoint == "24h",
            )
        ).first()

        assert row is not None
        assert row.opens is None
        assert row.clicks is None


# ---------------------------------------------------------------------------
# Scheduler registration
# ---------------------------------------------------------------------------

class TestScheduleMetricCheckpoints:
    """schedule_metric_checkpoints registers three APScheduler one-off jobs."""

    def test_registers_three_jobs_for_linkedin_publication(self, session, sample_publication):
        """
        After calling schedule_metric_checkpoints, three jobs should be registered
        with the scheduler: one at 24h, one at 72h, one at 7d after published_at.
        """
        from unittest.mock import MagicMock

        mock_scheduler = MagicMock()

        import asyncio
        asyncio.get_event_loop().run_until_complete(
            schedule_metric_checkpoints(
                publication=sample_publication,
                session=session,
                scheduler=mock_scheduler,
            )
        )

        assert mock_scheduler.add_job.call_count == 3

        # Extract the run_date values from each add_job call
        run_dates = [
            call.kwargs["run_date"]
            for call in mock_scheduler.add_job.call_args_list
        ]

        base = sample_publication.published_at
        from datetime import timedelta
        expected_offsets = [timedelta(hours=24), timedelta(hours=72), timedelta(days=7)]
        for expected_delta, actual_date in zip(expected_offsets, sorted(run_dates)):
            delta = actual_date - base
            assert abs(delta.total_seconds() - expected_delta.total_seconds()) < 60, (
                f"Expected offset {expected_delta}, got {delta}"
            )
```

- [ ] Run tests — confirm they fail at import:

```bash
cd bidequity-newsroom
pytest tests/test_metrics/test_collectors.py -v 2>&1 | head -20
# Expected: ModuleNotFoundError on 'from bidequity.metrics.collectors import ...'
```

- [ ] Commit the failing tests:

```bash
git add tests/test_metrics/
git commit -m "test(metrics): add failing collector tests — ticket 10"
```

---

### Task 2: Write failing tests for insights

**Files:**
- `bidequity-newsroom/tests/test_metrics/test_insights.py`

- [ ] Create `bidequity-newsroom/tests/test_metrics/test_insights.py`:

```python
"""
Tests for bidequity.metrics.insights.

Inserts fixture data directly into the database and asserts aggregation results.
No external API calls. No mocking needed.

Run with: pytest tests/test_metrics/test_insights.py -v
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlmodel import Session, select

from bidequity.models import (
    Classification,
    Draft,
    EditorialAction,
    Item,
    Metrics,
    Publication,
    Source,
)
from bidequity.metrics.insights import (
    get_classifier_agreement_rate,
    get_monthly_cost_estimate,
    get_source_performance,
    get_top_performing_posts,
)


# ---------------------------------------------------------------------------
# get_monthly_cost_estimate
# ---------------------------------------------------------------------------

class TestGetMonthlyCostEstimate:

    def test_sums_classification_and_draft_costs_for_current_month(
        self, session, source_fixture
    ):
        """
        Given two Classification rows and two Draft rows in the current month,
        get_monthly_cost_estimate should return the correct subtotals and total.
        GBP total = total_usd * 0.79 (approximate; test asserts > 0, not exact rate).
        """
        now = datetime.now(tz=timezone.utc)

        # Two items with classification costs
        for i, cost in enumerate([0.000120, 0.000095]):
            item = Item(
                source_id=source_fixture.id,
                url=f"https://cost-test.example.com/item-{i}",
                title=f"Cost Test Item {i}",
                body_text="Body text for cost test.",
                content_hash=f"cost{i:028d}",
            )
            session.add(item)
            session.flush()

            session.add(
                Classification(
                    item_id=item.id,
                    prompt_version="classifier-v1.0",
                    relevance_score=8,
                    signal_strength="high",
                    signal_type="procurement",
                    sectors=["Defence"],
                    summary="Summary.",
                    cost_usd=cost,
                    classified_at=now,
                )
            )

            draft = Draft(
                item_id=item.id,
                prompt_version="generator-v1.0",
                linkedin_post="Post text.",
                newsletter_para="Para.",
                so_what_line="So what.",
                cost_usd=0.002500 if i == 0 else 0.003100,
                generated_at=now,
            )
            session.add(draft)

        session.commit()

        result = get_monthly_cost_estimate(session)

        assert result["classifier_usd"] == pytest.approx(0.000215, abs=1e-6)
        assert result["generator_usd"] == pytest.approx(0.005600, abs=1e-6)
        assert result["total_usd"] == pytest.approx(0.005815, abs=1e-5)
        assert result["total_gbp"] > 0

    def test_excludes_costs_from_previous_month(self, session, source_fixture):
        """Costs from last month are not included in the current-month total."""
        last_month = datetime.now(tz=timezone.utc) - timedelta(days=35)

        item = Item(
            source_id=source_fixture.id,
            url="https://old-cost.example.com/old",
            title="Old Item",
            body_text="Old body.",
            content_hash="old0" + "0" * 28,
        )
        session.add(item)
        session.flush()

        session.add(
            Classification(
                item_id=item.id,
                prompt_version="classifier-v1.0",
                relevance_score=6,
                signal_strength="medium",
                signal_type="policy",
                sectors=["Health & Social Care"],
                summary="Old summary.",
                cost_usd=999.0,   # large sentinel value — must not appear in result
                classified_at=last_month,
            )
        )
        session.commit()

        result = get_monthly_cost_estimate(session)
        # The 999.0 sentinel from last month must not inflate this month's classifier cost
        assert result["classifier_usd"] < 1.0


# ---------------------------------------------------------------------------
# get_top_performing_posts
# ---------------------------------------------------------------------------

class TestGetTopPerformingPosts:

    def test_returns_top_n_by_engagement_rate_at_7d_checkpoint(
        self, session, source_fixture
    ):
        """
        Given 5 publications each with a 7d Metrics row, get_top_performing_posts(n=3)
        should return the 3 with the highest (reactions + comments + shares) / impressions.
        """
        now = datetime.now(tz=timezone.utc)

        # engagement_rates: [0.10, 0.25, 0.05, 0.40, 0.15]
        # top 3 are indices 3 (0.40), 1 (0.25), 4 (0.15)
        posts_data = [
            {"impressions": 1000, "reactions": 60, "comments": 20, "shares": 20, "post": "Post A"},
            {"impressions": 1000, "reactions": 150, "comments": 60, "shares": 40, "post": "Post B"},
            {"impressions": 1000, "reactions": 30, "comments": 10, "shares": 10, "post": "Post C"},
            {"impressions": 1000, "reactions": 250, "comments": 80, "shares": 70, "post": "Post D"},
            {"impressions": 1000, "reactions": 90, "comments": 40, "shares": 20, "post": "Post E"},
        ]

        for idx, pd in enumerate(posts_data):
            item = Item(
                source_id=source_fixture.id,
                url=f"https://top-posts.example.com/{idx}",
                title=f"Top Posts Item {idx}",
                body_text="Body.",
                content_hash=f"top{idx:029d}",
            )
            session.add(item)
            session.flush()

            draft = Draft(
                item_id=item.id,
                prompt_version="generator-v1.0",
                linkedin_post=pd["post"],
                newsletter_para="Para.",
                so_what_line="So what.",
            )
            session.add(draft)
            session.flush()

            pub = Publication(
                draft_id=draft.id,
                channel="linkedin",
                final_content=pd["post"],
                scheduled_for=now,
                published_at=now,
                external_id=f"urn:li:share:{idx}",
                status="published",
            )
            session.add(pub)
            session.flush()

            session.add(
                Metrics(
                    publication_id=pub.id,
                    checkpoint="7d",
                    impressions=pd["impressions"],
                    reactions=pd["reactions"],
                    comments=pd["comments"],
                    shares=pd["shares"],
                    measured_at=now,
                )
            )

        session.commit()

        top = get_top_performing_posts(session, n=3)

        assert len(top) == 3
        # Verify descending order of engagement rate
        rates = [p["engagement_rate"] for p in top]
        assert rates == sorted(rates, reverse=True)
        # Top post should be Post D (rate ~0.40)
        assert top[0]["linkedin_post"] == "Post D"
        assert top[0]["engagement_rate"] == pytest.approx(0.40, abs=0.01)

    def test_returns_fewer_than_n_when_insufficient_data(self, session, source_fixture):
        """
        When fewer than n publications have 7d metrics, return what exists rather than raising.
        """
        top = get_top_performing_posts(session, n=3)
        # May return 0, 1, or 2 depending on prior test state — must not raise
        assert isinstance(top, list)
        assert len(top) <= 3


# ---------------------------------------------------------------------------
# get_classifier_agreement_rate
# ---------------------------------------------------------------------------

class TestGetClassifierAgreementRate:

    def test_returns_correct_approval_fraction(self, session, source_fixture):
        """
        Given 8 approve actions and 2 reject actions in the last 30 days,
        agreement_rate = 8 / (8 + 2) = 0.80.
        """
        now = datetime.now(tz=timezone.utc)

        # Build 10 draft + editorial_action rows
        for i in range(10):
            item = Item(
                source_id=source_fixture.id,
                url=f"https://agree.example.com/{i}",
                title=f"Agree Item {i}",
                body_text="Body.",
                content_hash=f"agr{i:029d}",
            )
            session.add(item)
            session.flush()

            draft = Draft(
                item_id=item.id,
                prompt_version="classifier-v1.0",
                linkedin_post="Post.",
                newsletter_para="Para.",
                so_what_line="So what.",
            )
            session.add(draft)
            session.flush()

            action = "approve" if i < 8 else "reject"
            session.add(
                EditorialAction(
                    draft_id=draft.id,
                    action=action,
                    created_at=now,
                )
            )

        session.commit()

        rate = get_classifier_agreement_rate(session, sample_days=30)
        assert rate == pytest.approx(0.80, abs=0.01)

    def test_returns_none_when_no_actions_in_window(self, session):
        """
        With no editorial actions in the window, return None rather than dividing by zero.
        """
        # Use a window so narrow no actions can exist
        rate = get_classifier_agreement_rate(session, sample_days=0)
        assert rate is None


# ---------------------------------------------------------------------------
# get_source_performance
# ---------------------------------------------------------------------------

class TestGetSourcePerformance:

    def test_returns_per_source_counts(self, session, source_fixture):
        """
        get_source_performance returns a list with one entry per source
        containing items_ingested, items_classified_high, items_approved, approval_rate.
        """
        perf = get_source_performance(session)
        assert isinstance(perf, list)
        # Each row must have the required keys
        for row in perf:
            assert "source_name" in row
            assert "items_ingested" in row
            assert "items_classified_high" in row
            assert "items_approved" in row
            assert "approval_rate" in row

    def test_high_classification_threshold_is_score_gte_7(self, session, source_fixture):
        """
        Items with relevance_score >= 7 count as 'high'; items with score < 7 do not.
        """
        now = datetime.now(tz=timezone.utc)

        for i, score in enumerate([9, 7, 6, 4]):
            item = Item(
                source_id=source_fixture.id,
                url=f"https://perf.example.com/{i}",
                title=f"Perf Item {i}",
                body_text="Body.",
                content_hash=f"prf{i:029d}",
            )
            session.add(item)
            session.flush()
            session.add(
                Classification(
                    item_id=item.id,
                    prompt_version="classifier-v1.0",
                    relevance_score=score,
                    signal_strength="high" if score >= 7 else "medium",
                    signal_type="procurement",
                    sectors=["Defence"],
                    summary="Summary.",
                    classified_at=now,
                )
            )

        session.commit()

        perf = get_source_performance(session)
        source_row = next(
            (r for r in perf if r["source_name"] == source_fixture.name), None
        )
        assert source_row is not None
        # scores 9 and 7 are high; 6 and 4 are not
        assert source_row["items_classified_high"] >= 2
```

- [ ] Run tests — confirm they fail at import:

```bash
cd bidequity-newsroom
pytest tests/test_metrics/test_insights.py -v 2>&1 | head -20
# Expected: ModuleNotFoundError on 'from bidequity.metrics.insights import ...'
```

- [ ] Commit the failing insight tests:

```bash
git add tests/test_metrics/test_insights.py
git commit -m "test(metrics): add failing insight aggregation tests — ticket 10"
```

---

### Task 3: Add shared test fixtures for metrics tests

**Files:**
- `bidequity-newsroom/tests/conftest.py` (modify — add new fixtures)

The existing conftest.py provides the database engine and session. Add `source_fixture`, `sample_publication`, and `sample_newsletter_publication` fixtures that the metrics tests depend on.

- [ ] Append to `bidequity-newsroom/tests/conftest.py`:

```python
# ── metrics test fixtures ─────────────────────────────────────────────────────

from datetime import datetime, timezone
from bidequity.models import Draft, Item, Publication, Source


@pytest.fixture
def source_fixture(session) -> Source:
    """A minimal Source row for use in metrics tests."""
    src = Source(
        name="Metrics Test Source",
        category="Official Blogs",
        sector="Defence",
        url=f"https://metrics-fixture.example.com/{id(session)}",
        feed_type="rss",
        cadence="daily",
        signal_strength="high",
        priority_score=1,
    )
    session.add(src)
    session.commit()
    session.refresh(src)
    return src


@pytest.fixture
def sample_publication(session, source_fixture) -> Publication:
    """A published LinkedIn Publication for use in collector tests."""
    item = Item(
        source_id=source_fixture.id,
        url="https://metrics-fixture.example.com/pub-li",
        title="Sample LinkedIn Item",
        body_text="Body text for sample LinkedIn publication.",
        content_hash="li" + "0" * 30,
    )
    session.add(item)
    session.flush()

    draft = Draft(
        item_id=item.id,
        prompt_version="generator-v1.0",
        linkedin_post="Sample LinkedIn post text.",
        newsletter_para="Sample newsletter paragraph.",
        so_what_line="Sample so-what.",
    )
    session.add(draft)
    session.flush()

    pub = Publication(
        draft_id=draft.id,
        channel="linkedin",
        final_content="Sample LinkedIn post text.",
        scheduled_for=datetime.now(tz=timezone.utc),
        published_at=datetime.now(tz=timezone.utc),
        external_id="urn:li:share:99900001",
        status="published",
    )
    session.add(pub)
    session.commit()
    session.refresh(pub)
    return pub


@pytest.fixture
def sample_newsletter_publication(session, source_fixture) -> Publication:
    """A published newsletter Publication for use in collector tests."""
    item = Item(
        source_id=source_fixture.id,
        url="https://metrics-fixture.example.com/pub-nl",
        title="Sample Newsletter Item",
        body_text="Body text for sample newsletter publication.",
        content_hash="nl" + "0" * 30,
    )
    session.add(item)
    session.flush()

    draft = Draft(
        item_id=item.id,
        prompt_version="generator-v1.0",
        linkedin_post="Sample LinkedIn.",
        newsletter_para="Sample newsletter paragraph.",
        so_what_line="Sample so-what.",
    )
    session.add(draft)
    session.flush()

    pub = Publication(
        draft_id=draft.id,
        channel="newsletter",
        final_content="Sample newsletter paragraph.",
        scheduled_for=datetime.now(tz=timezone.utc),
        published_at=datetime.now(tz=timezone.utc),
        external_id="beehiiv_post_99900001",
        status="published",
    )
    session.add(pub)
    session.commit()
    session.refresh(pub)
    return pub
```

- [ ] Verify conftest changes don't break existing model tests:

```bash
cd bidequity-newsroom
pytest tests/test_models.py -v
# Expected: all prior tests still pass
```

- [ ] Commit:

```bash
git add tests/conftest.py
git commit -m "test(conftest): add source_fixture and publication fixtures for metrics tests — ticket 10"
```

---

### Task 4: LinkedIn API client

**Files:**
- `bidequity-newsroom/src/bidequity/publish/linkedin.py` (modify — add `LinkedInClient.get_share_statistics`)

The `LinkedInClient` class already exists from Ticket 8 (handles OAuth and `POST /v2/ugcPosts`). Add one new method for the metrics collector.

- [ ] Add to the `LinkedInClient` class in `bidequity-newsroom/src/bidequity/publish/linkedin.py`:

```python
async def get_share_statistics(self, org_urn: str, share_urn: str) -> dict:
    """
    GET /v2/organizationalEntityShareStatistics
    ?q=organizationalEntity
    &organizationalEntity={org_urn}
    &shares[0]={share_urn}

    Returns the raw API response dict.
    Raises httpx.HTTPStatusError on non-2xx responses.
    """
    url = "https://api.linkedin.com/v2/organizationalEntityShareStatistics"
    params = {
        "q": "organizationalEntity",
        "organizationalEntity": org_urn,
        "shares[0]": share_urn,
    }
    response = await self._client.get(
        url,
        params=params,
        headers={"Authorization": f"Bearer {await self._get_access_token()}"},
    )
    response.raise_for_status()
    return response.json()
```

- [ ] Commit:

```bash
git add src/bidequity/publish/linkedin.py
git commit -m "feat(linkedin): add get_share_statistics method for metrics collection — ticket 10"
```

---

### Task 5: Beehiiv API client

**Files:**
- `bidequity-newsroom/src/bidequity/publish/beehiiv.py` (modify — add `BeehiivClient.get_post_stats`)

The `BeehiivClient` already exists from Ticket 9. Add one new method.

- [ ] Add to the `BeehiivClient` class in `bidequity-newsroom/src/bidequity/publish/beehiiv.py`:

```python
async def get_post_stats(self, post_id: str) -> dict:
    """
    GET /publications/{pub_id}/posts/{post_id}

    Returns the full post response dict including a 'stats' key when analytics are ready.
    Raises httpx.HTTPStatusError on non-2xx responses.
    """
    url = f"{self._base_url}/publications/{self._publication_id}/posts/{post_id}"
    response = await self._client.get(
        url,
        headers={"Authorization": f"Bearer {self._api_key}"},
    )
    response.raise_for_status()
    return response.json()
```

- [ ] Commit:

```bash
git add src/bidequity/publish/beehiiv.py
git commit -m "feat(beehiiv): add get_post_stats method for metrics collection — ticket 10"
```

---

### Task 6: Metrics collectors

**Files:**
- `bidequity-newsroom/src/bidequity/metrics/__init__.py`
- `bidequity-newsroom/src/bidequity/metrics/collectors.py`

- [ ] Create `bidequity-newsroom/src/bidequity/metrics/__init__.py`:

```python
"""bidequity.metrics — engagement data collection and insight aggregation."""
from .collectors import (
    collect_beehiiv_metrics,
    collect_linkedin_metrics,
    schedule_metric_checkpoints,
)
from .insights import (
    get_classifier_agreement_rate,
    get_monthly_cost_estimate,
    get_source_performance,
    get_top_performing_posts,
)

__all__ = [
    "collect_linkedin_metrics",
    "collect_beehiiv_metrics",
    "schedule_metric_checkpoints",
    "get_monthly_cost_estimate",
    "get_top_performing_posts",
    "get_classifier_agreement_rate",
    "get_source_performance",
]
```

- [ ] Create `bidequity-newsroom/src/bidequity/metrics/collectors.py`:

```python
"""
bidequity.metrics.collectors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pulls engagement data from LinkedIn and Beehiiv APIs and persists Metrics rows.

Three checkpoints per publication: 24h, 72h, 7d after published_at.
APScheduler one-off jobs are registered by schedule_metric_checkpoints()
immediately after a publication goes live (called from the publish workers).
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from sqlmodel import Session

from bidequity.models import Metrics, Publication

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from bidequity.publish.linkedin import LinkedInClient
    from bidequity.publish.beehiiv import BeehiivClient

logger = logging.getLogger(__name__)

# Checkpoint definitions: label → timedelta from published_at
CHECKPOINTS: dict[str, timedelta] = {
    "24h": timedelta(hours=24),
    "72h": timedelta(hours=72),
    "7d": timedelta(days=7),
}


async def collect_linkedin_metrics(
    publication: Publication,
    checkpoint: str,
    client: "LinkedInClient",
    session: Session,
) -> Metrics:
    """
    Fetch share statistics from the LinkedIn Marketing Developer Platform for
    a single publication and persist a Metrics row.

    Endpoint: GET /v2/organizationalEntityShareStatistics
              ?q=organizationalEntity
              &organizationalEntity={LINKEDIN_ORG_URN}
              &shares[0]={publication.external_id}

    Fields populated: impressions, reactions (likeCount), comments, shares, clicks.
    opens is always None for LinkedIn.
    raw_response stores the full API dict for auditability.
    """
    import os

    org_urn = os.environ["LINKEDIN_ORG_URN"]

    try:
        raw = await client.get_share_statistics(
            org_urn=org_urn,
            share_urn=publication.external_id,
        )
    except Exception as exc:
        logger.warning(
            "LinkedIn metrics fetch failed for publication %s at %s: %s",
            publication.id,
            checkpoint,
            exc,
        )
        raw = {}

    elements = raw.get("elements", [])
    stats = (
        elements[0].get("totalShareStatistics", {}) if elements else {}
    )

    metrics = Metrics(
        publication_id=publication.id,
        checkpoint=checkpoint,
        measured_at=datetime.now(tz=timezone.utc),
        impressions=stats.get("impressionCount"),
        reactions=stats.get("likeCount"),
        comments=stats.get("commentCount"),
        shares=stats.get("shareCount"),
        clicks=stats.get("clickCount"),
        opens=None,
        raw_response=raw if raw else None,
    )
    session.add(metrics)
    session.commit()
    session.refresh(metrics)

    logger.info(
        "LinkedIn metrics persisted: publication=%s checkpoint=%s impressions=%s",
        publication.id,
        checkpoint,
        metrics.impressions,
    )
    return metrics


async def collect_beehiiv_metrics(
    publication: Publication,
    checkpoint: str,
    client: "BeehiivClient",
    session: Session,
) -> Metrics:
    """
    Fetch post analytics from the Beehiiv API for a single publication and
    persist a Metrics row.

    Endpoint: GET /publications/{pub_id}/posts/{post_id}

    Fields populated: opens (unique_opens), clicks.
    impressions, reactions, comments, shares are always None for Beehiiv.
    raw_response stores the full API dict.
    """
    try:
        raw = await client.get_post_stats(post_id=publication.external_id)
    except Exception as exc:
        logger.warning(
            "Beehiiv metrics fetch failed for publication %s at %s: %s",
            publication.id,
            checkpoint,
            exc,
        )
        raw = {}

    stats = raw.get("data", {}).get("stats", {})

    metrics = Metrics(
        publication_id=publication.id,
        checkpoint=checkpoint,
        measured_at=datetime.now(tz=timezone.utc),
        impressions=None,
        reactions=None,
        comments=None,
        shares=None,
        clicks=stats.get("clicks"),
        opens=stats.get("unique_opens"),
        raw_response=raw if raw else None,
    )
    session.add(metrics)
    session.commit()
    session.refresh(metrics)

    logger.info(
        "Beehiiv metrics persisted: publication=%s checkpoint=%s opens=%s clicks=%s",
        publication.id,
        checkpoint,
        metrics.opens,
        metrics.clicks,
    )
    return metrics


async def schedule_metric_checkpoints(
    publication: Publication,
    session: Session,
    scheduler: "AsyncIOScheduler",
) -> None:
    """
    Register three APScheduler date-triggered one-off jobs after a publication
    goes live: 24h, 72h, and 7d after published_at.

    The appropriate collector function (LinkedIn or Beehiiv) is selected from
    publication.channel. The Session and API clients are resolved inside each
    job via FastAPI dependency injection to avoid holding a session across the
    delay.

    Called by the publish workers (linkedin.py and beehiiv.py) immediately
    after a successful publish.
    """
    from bidequity.common.db import get_session  # late import to avoid circular
    from bidequity.publish.linkedin import LinkedInClient
    from bidequity.publish.beehiiv import BeehiivClient

    base_time: datetime = publication.published_at
    if base_time.tzinfo is None:
        base_time = base_time.replace(tzinfo=timezone.utc)

    for checkpoint, delta in CHECKPOINTS.items():
        run_at = base_time + delta

        if publication.channel == "linkedin":
            collector_fn = _run_linkedin_checkpoint
        else:
            collector_fn = _run_beehiiv_checkpoint

        scheduler.add_job(
            collector_fn,
            trigger="date",
            run_date=run_at,
            kwargs={
                "publication_id": publication.id,
                "checkpoint": checkpoint,
            },
            id=f"metrics_{publication.id}_{checkpoint}",
            replace_existing=True,
            misfire_grace_time=3600,  # up to 1h late is acceptable
        )
        logger.info(
            "Scheduled %s metrics job for publication %s at %s",
            checkpoint,
            publication.id,
            run_at.isoformat(),
        )


async def _run_linkedin_checkpoint(publication_id: int, checkpoint: str) -> None:
    """
    Top-level callable for APScheduler. Resolves its own DB session and
    LinkedIn client, then delegates to collect_linkedin_metrics.
    """
    from bidequity.common.db import get_session
    from bidequity.publish.linkedin import LinkedInClient
    from sqlmodel import select

    async with get_session() as session:
        publication = session.exec(
            select(Publication).where(Publication.id == publication_id)
        ).first()
        if not publication:
            logger.error("Publication %s not found for LinkedIn metrics job", publication_id)
            return

        client = LinkedInClient.from_env()
        await collect_linkedin_metrics(
            publication=publication,
            checkpoint=checkpoint,
            client=client,
            session=session,
        )


async def _run_beehiiv_checkpoint(publication_id: int, checkpoint: str) -> None:
    """
    Top-level callable for APScheduler. Resolves its own DB session and
    Beehiiv client, then delegates to collect_beehiiv_metrics.
    """
    from bidequity.common.db import get_session
    from bidequity.publish.beehiiv import BeehiivClient
    from sqlmodel import select

    async with get_session() as session:
        publication = session.exec(
            select(Publication).where(Publication.id == publication_id)
        ).first()
        if not publication:
            logger.error("Publication %s not found for Beehiiv metrics job", publication_id)
            return

        client = BeehiivClient.from_env()
        await collect_beehiiv_metrics(
            publication=publication,
            checkpoint=checkpoint,
            client=client,
            session=session,
        )
```

- [ ] Run collector tests — they should now pass:

```bash
cd bidequity-newsroom
pytest tests/test_metrics/test_collectors.py -v
# Expected: all collector tests pass
```

- [ ] Commit:

```bash
git add src/bidequity/metrics/__init__.py src/bidequity/metrics/collectors.py
git commit -m "feat(metrics): LinkedIn and Beehiiv collectors with APScheduler checkpoints — ticket 10"
```

---

### Task 7: Insights aggregators

**Files:**
- `bidequity-newsroom/src/bidequity/metrics/insights.py`

- [ ] Create `bidequity-newsroom/src/bidequity/metrics/insights.py`:

```python
"""
bidequity.metrics.insights
~~~~~~~~~~~~~~~~~~~~~~~~~~
Pure-SQL aggregation functions over the metrics, classifications, drafts,
and editorial_actions tables. No external API calls. Used by the dashboard
/insights route and the monthly cost report email.
"""
from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import Optional

from sqlalchemy import func, text
from sqlmodel import Session, select

from bidequity.models import Classification, Draft, EditorialAction, Metrics, Publication, Source

logger = logging.getLogger(__name__)

# Approximate USD → GBP conversion rate. Replace with a live rate call if needed.
_USD_TO_GBP = 0.79


def get_monthly_cost_estimate(session: Session) -> dict:
    """
    Sum classification and generation costs for the current calendar month.

    Returns:
        {
            "classifier_usd": float,
            "generator_usd": float,
            "total_usd": float,
            "total_gbp": float,
        }
    """
    now = datetime.now(tz=timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    classifier_usd: float = session.exec(
        select(func.coalesce(func.sum(Classification.cost_usd), 0)).where(
            Classification.classified_at >= month_start
        )
    ).one()

    generator_usd: float = session.exec(
        select(func.coalesce(func.sum(Draft.cost_usd), 0)).where(
            Draft.generated_at >= month_start
        )
    ).one()

    total_usd = float(classifier_usd) + float(generator_usd)
    return {
        "classifier_usd": float(classifier_usd),
        "generator_usd": float(generator_usd),
        "total_usd": total_usd,
        "total_gbp": round(total_usd * _USD_TO_GBP, 2),
    }


def get_top_performing_posts(session: Session, n: int = 3) -> list[dict]:
    """
    Return the top n published LinkedIn posts by engagement rate at the 7d checkpoint.

    Engagement rate = (reactions + comments + shares) / impressions.
    Posts with zero impressions are excluded to avoid division by zero.

    Returns a list of dicts:
        [
            {
                "draft_id": int,
                "linkedin_post": str,
                "impressions": int,
                "reactions": int,
                "comments": int,
                "shares": int,
                "engagement_rate": float,
            },
            ...
        ]
    """
    rows = session.exec(
        text(
            """
            SELECT
                d.id           AS draft_id,
                d.linkedin_post,
                m.impressions,
                COALESCE(m.reactions, 0)  AS reactions,
                COALESCE(m.comments, 0)   AS comments,
                COALESCE(m.shares, 0)     AS shares,
                (
                    COALESCE(m.reactions, 0)
                    + COALESCE(m.comments, 0)
                    + COALESCE(m.shares, 0)
                )::float / NULLIF(m.impressions, 0) AS engagement_rate
            FROM publications p
            JOIN drafts d       ON d.id = p.draft_id
            JOIN metrics m      ON m.publication_id = p.id
            WHERE p.channel    = 'linkedin'
              AND p.status     = 'published'
              AND m.checkpoint = '7d'
              AND m.impressions > 0
            ORDER BY engagement_rate DESC
            LIMIT :n
            """
        ),
        params={"n": n},
    ).all()

    return [
        {
            "draft_id": r.draft_id,
            "linkedin_post": r.linkedin_post,
            "impressions": r.impressions,
            "reactions": r.reactions,
            "comments": r.comments,
            "shares": r.shares,
            "engagement_rate": round(float(r.engagement_rate), 4) if r.engagement_rate else 0.0,
        }
        for r in rows
    ]


def get_classifier_agreement_rate(
    session: Session, sample_days: int = 30
) -> Optional[float]:
    """
    Compute a proxy for classifier-human agreement over the last sample_days days.

    Agreement rate = approved_count / (approved_count + rejected_count).

    Only 'approve' and 'reject' actions are counted; 'edit' and 'save' are neutral.
    Returns None if there are no approve or reject actions in the window
    (avoids division by zero on a fresh system).
    """
    if sample_days == 0:
        return None

    now = datetime.now(tz=timezone.utc)
    from datetime import timedelta
    window_start = now - timedelta(days=sample_days)

    counts = session.exec(
        text(
            """
            SELECT
                SUM(CASE WHEN action = 'approve' THEN 1 ELSE 0 END) AS approved,
                SUM(CASE WHEN action = 'reject'  THEN 1 ELSE 0 END) AS rejected
            FROM editorial_actions
            WHERE action IN ('approve', 'reject')
              AND created_at >= :window_start
            """
        ),
        params={"window_start": window_start},
    ).one()

    approved = int(counts.approved or 0)
    rejected = int(counts.rejected or 0)
    total = approved + rejected

    if total == 0:
        return None

    return round(approved / total, 4)


def get_source_performance(session: Session) -> list[dict]:
    """
    Per-source breakdown: items ingested, items classified high (score >= 7),
    items approved by the operator, and approval rate.

    Returns:
        [
            {
                "source_id": int,
                "source_name": str,
                "items_ingested": int,
                "items_classified_high": int,
                "items_approved": int,
                "approval_rate": float,   # approved / ingested; 0.0 if no items
            },
            ...
        ]
    Sorted by items_ingested DESC.
    """
    rows = session.exec(
        text(
            """
            SELECT
                s.id   AS source_id,
                s.name AS source_name,
                COUNT(DISTINCT i.id)  AS items_ingested,
                COUNT(DISTINCT c.id) FILTER (WHERE c.relevance_score >= 7)
                                      AS items_classified_high,
                COUNT(DISTINCT ea.id) FILTER (WHERE ea.action = 'approve')
                                      AS items_approved
            FROM sources s
            LEFT JOIN items i         ON i.source_id = s.id
            LEFT JOIN classifications c ON c.item_id = i.id
            LEFT JOIN drafts d        ON d.item_id = i.id
            LEFT JOIN editorial_actions ea ON ea.draft_id = d.id
            GROUP BY s.id, s.name
            ORDER BY items_ingested DESC
            """
        )
    ).all()

    return [
        {
            "source_id": r.source_id,
            "source_name": r.source_name,
            "items_ingested": int(r.items_ingested or 0),
            "items_classified_high": int(r.items_classified_high or 0),
            "items_approved": int(r.items_approved or 0),
            "approval_rate": (
                round(int(r.items_approved or 0) / int(r.items_ingested), 4)
                if int(r.items_ingested or 0) > 0
                else 0.0
            ),
        }
        for r in rows
    ]


async def send_monthly_cost_report(session: Session, smtp_config: dict) -> None:
    """
    Build and send a plain-text monthly cost report by email.

    Called on the 1st of each month at 09:00 UTC by an APScheduler cron job
    registered in main.py.

    smtp_config keys: host, port, username, password, from_addr, to_addr.
    If smtp_config is incomplete or SMTP fails, the error is logged but not raised
    (a missed email is not a system failure).
    """
    try:
        cost = get_monthly_cost_estimate(session)
        top_posts = get_top_performing_posts(session, n=3)
        agreement = get_classifier_agreement_rate(session, sample_days=30)

        # --- build report body ---
        lines = [
            "BidEquity Newsroom — Monthly Cost & Performance Report",
            "=" * 55,
            "",
            f"Report generated: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "OPERATING COST THIS MONTH",
            "-" * 30,
            f"  Classifier (Haiku):   ${cost['classifier_usd']:.4f}",
            f"  Generator (Sonnet):   ${cost['generator_usd']:.4f}",
            f"  Total (USD):          ${cost['total_usd']:.4f}",
            f"  Total (GBP approx):   £{cost['total_gbp']:.2f}",
            "",
            "TOP PERFORMING POSTS (last 30 days, 7d checkpoint)",
            "-" * 50,
        ]

        if top_posts:
            for i, post in enumerate(top_posts, 1):
                preview = post["linkedin_post"][:120].replace("\n", " ")
                lines.append(
                    f"  {i}. Engagement rate: {post['engagement_rate']:.1%} "
                    f"({post['impressions']} impressions)"
                )
                lines.append(f"     \"{preview}...\"")
                lines.append("")
        else:
            lines.append("  No posts with 7d metrics yet.")
            lines.append("")

        lines += [
            "CLASSIFIER AGREEMENT RATE (last 30 days)",
            "-" * 45,
        ]
        if agreement is not None:
            status = (
                "GREEN (>= 80%)" if agreement >= 0.80
                else "AMBER (70-80%)" if agreement >= 0.70
                else "RED (< 70%)"
            )
            lines.append(f"  Agreement rate: {agreement:.1%}  [{status}]")
        else:
            lines.append("  Insufficient data (no approve/reject actions in window).")

        lines += [
            "",
            "---",
            "Reconcile classifier + generator costs against Anthropic billing dashboard.",
            "https://console.anthropic.com/settings/billing",
        ]

        body = "\n".join(lines)

        # --- send ---
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = (
            f"BidEquity Newsroom: Monthly Cost Report — "
            f"{datetime.now(tz=timezone.utc).strftime('%B %Y')}"
        )
        msg["From"] = smtp_config["from_addr"]
        msg["To"] = smtp_config["to_addr"]

        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as smtp:
            smtp.starttls()
            smtp.login(smtp_config["username"], smtp_config["password"])
            smtp.send_message(msg)

        logger.info("Monthly cost report sent to %s", smtp_config["to_addr"])

    except Exception as exc:
        logger.error("Failed to send monthly cost report: %s", exc, exc_info=True)
```

- [ ] Run insight tests — they should now pass:

```bash
cd bidequity-newsroom
pytest tests/test_metrics/test_insights.py -v
# Expected: all insight tests pass
```

- [ ] Commit:

```bash
git add src/bidequity/metrics/insights.py
git commit -m "feat(metrics): insights aggregators — cost, top posts, agreement rate, source performance — ticket 10"
```

---

### Task 8: Register monthly cost report job in APScheduler

**Files:**
- `bidequity-newsroom/src/bidequity/main.py` (modify — add APScheduler cron job for 1st of month)

The `scheduler` object is already wired in `main.py` from Ticket 3. Add one cron job at startup.

- [ ] In `bidequity-newsroom/src/bidequity/main.py`, inside the `lifespan` function (or wherever existing scheduler jobs are registered), add:

```python
from bidequity.metrics.insights import send_monthly_cost_report
from bidequity.common.config import settings

# Monthly cost report — 1st of each month at 09:00 UTC
scheduler.add_job(
    _send_monthly_cost_report_job,
    trigger="cron",
    day=1,
    hour=9,
    minute=0,
    timezone="UTC",
    id="monthly_cost_report",
    replace_existing=True,
)
```

- [ ] Add the top-level async function directly in `main.py`:

```python
async def _send_monthly_cost_report_job() -> None:
    """APScheduler entry point for the monthly cost report."""
    from bidequity.common.db import get_session
    from bidequity.metrics.insights import send_monthly_cost_report
    import os

    smtp_config = {
        "host": os.environ.get("SMTP_HOST", "smtp.cloudflare.com"),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "username": os.environ.get("SMTP_USERNAME", ""),
        "password": os.environ.get("SMTP_PASSWORD", ""),
        "from_addr": os.environ.get("SMTP_FROM", "newsroom@bidequity.co.uk"),
        "to_addr": os.environ.get("DASHBOARD_USERNAME", "pfenton@me.com"),
    }

    async with get_session() as session:
        await send_monthly_cost_report(session=session, smtp_config=smtp_config)
```

- [ ] Add the required env vars to `.env.example` and to the appendix variables list:

```bash
# SMTP (for monthly cost report)
SMTP_HOST=smtp.cloudflare.com
SMTP_PORT=587
SMTP_USERNAME=newsroom@bidequity.co.uk
SMTP_PASSWORD=...
SMTP_FROM=newsroom@bidequity.co.uk
```

- [ ] Commit:

```bash
git add src/bidequity/main.py .env.example
git commit -m "feat(scheduler): register monthly cost report cron job on 1st of month 09:00 UTC — ticket 10"
```

---

### Task 9: Generator style anchor injection

**Files:**
- `bidequity-newsroom/src/bidequity/intelligence/generator.py` (modify)

The generator already builds its system prompt and user prompt. Add a `get_style_anchor_posts()` helper and inject the result into each generation call. This runs fresh on every call — not cached at the module level — so that the anchors update weekly as the top-posts data changes.

- [ ] Add to `bidequity-newsroom/src/bidequity/intelligence/generator.py`:

```python
def get_style_anchor_posts(session: Session) -> list[str]:
    """
    Return the linkedin_post text of the top 3 performing posts at the 7d
    checkpoint (by engagement rate). Returns an empty list if fewer than 3
    posts have 7d metrics — the generator degrades gracefully with no anchors.

    Called fresh on every generation. Not cached.
    """
    from bidequity.metrics.insights import get_top_performing_posts

    top = get_top_performing_posts(session, n=3)
    return [p["linkedin_post"] for p in top]
```

- [ ] In the same file, modify the system prompt assembly function (likely named `_build_system_prompt` or similar) to accept and include style anchors:

```python
def _build_system_prompt(style_anchors: list[str]) -> str:
    """
    Assemble the generator system prompt.
    style_anchors: list of up to 3 linkedin_post strings from recent top performers.
    This section is NOT part of the cached prompt prefix because anchors change weekly.
    """
    # ... existing prompt assembly code ...

    anchor_section = ""
    if style_anchors:
        formatted = "\n\n---\n\n".join(
            f"ANCHOR POST {i+1}:\n{post}" for i, post in enumerate(style_anchors)
        )
        anchor_section = (
            "\n\n## STYLE ANCHORS\n\n"
            "The following posts recently achieved the highest engagement rate on the "
            "BidEquity LinkedIn page. Use them as style references — not as content to "
            "repeat. Match the register, sentence rhythm, and pursuit-lens framing.\n\n"
            + formatted
        )

    return base_system_prompt + anchor_section
```

- [ ] Modify the generation entrypoint (the function called by the worker) to fetch anchors and pass them:

```python
async def generate_draft(item: Item, classification, cluster_items: list, session: Session) -> Draft:
    """
    Generate a LinkedIn post, newsletter paragraph, and supporting material
    for a single classified item.
    """
    style_anchors = get_style_anchor_posts(session)
    system_prompt = _build_system_prompt(style_anchors=style_anchors)

    # ... rest of existing generation logic using system_prompt ...
```

- [ ] Commit:

```bash
git add src/bidequity/intelligence/generator.py
git commit -m "feat(generator): inject top-3 style anchor posts into system prompt on every generation — ticket 10"
```

---

### Task 10: Insights dashboard route update

**Files:**
- `bidequity-newsroom/src/bidequity/dashboard/routes.py` (modify)

The existing `GET /insights` route needs to call the four new aggregator functions and pass the results to the template.

- [ ] Modify the `/insights` route handler in `bidequity-newsroom/src/bidequity/dashboard/routes.py`:

```python
@router.get("/insights", response_class=HTMLResponse)
async def insights_view(request: Request, session: Session = Depends(get_session)):
    """Insights dashboard: cost, top posts, classifier agreement, source performance."""
    from bidequity.metrics.insights import (
        get_classifier_agreement_rate,
        get_monthly_cost_estimate,
        get_source_performance,
        get_top_performing_posts,
    )

    monthly_cost = get_monthly_cost_estimate(session)
    top_posts = get_top_performing_posts(session, n=3)
    agreement_rate = get_classifier_agreement_rate(session, sample_days=30)
    source_performance = get_source_performance(session)

    # Derive agreement status for the gauge
    if agreement_rate is None:
        agreement_status = "unknown"
    elif agreement_rate >= 0.80:
        agreement_status = "green"
    elif agreement_rate >= 0.70:
        agreement_status = "amber"
    else:
        agreement_status = "red"

    return templates.TemplateResponse(
        "insights.html",
        {
            "request": request,
            "monthly_cost": monthly_cost,
            "top_posts": top_posts,
            "agreement_rate": agreement_rate,
            "agreement_status": agreement_status,
            "source_performance": source_performance,
        },
    )
```

- [ ] Commit:

```bash
git add src/bidequity/dashboard/routes.py
git commit -m "feat(dashboard): extend /insights route with cost, top posts, agreement, source perf data — ticket 10"
```

---

### Task 11: Insights dashboard template update

**Files:**
- `bidequity-newsroom/src/bidequity/dashboard/templates/insights.html` (modify)

The existing template shows placeholder content. Replace with four real data sections.

- [ ] Replace or extend the content block in `bidequity-newsroom/src/bidequity/dashboard/templates/insights.html`:

```html
{% extends "base.html" %}

{% block title %}Insights — BidEquity Newsroom{% endblock %}

{% block content %}
<div class="insights-page">
  <h1>Insights</h1>

  <!-- ── Monthly Cost Card ─────────────────────────────────────── -->
  <section class="card cost-card">
    <h2>Operating Cost — This Month</h2>
    <div class="cost-grid">
      <div class="cost-item">
        <span class="cost-label">Classifier (Haiku)</span>
        <span class="cost-value">${{ "%.4f"|format(monthly_cost.classifier_usd) }}</span>
      </div>
      <div class="cost-item">
        <span class="cost-label">Generator (Sonnet)</span>
        <span class="cost-value">${{ "%.4f"|format(monthly_cost.generator_usd) }}</span>
      </div>
      <div class="cost-item total">
        <span class="cost-label">Total</span>
        <span class="cost-value">
          ${{ "%.4f"|format(monthly_cost.total_usd) }}
          &nbsp;<small>(approx. £{{ "%.2f"|format(monthly_cost.total_gbp) }})</small>
        </span>
      </div>
    </div>
    <p class="cost-note">
      Reconcile against
      <a href="https://console.anthropic.com/settings/billing" target="_blank" rel="noopener">
        Anthropic billing
      </a>.
    </p>
  </section>

  <!-- ── Top Performing Posts ──────────────────────────────────── -->
  <section class="card top-posts-card">
    <h2>Top Performing Posts <small>(7-day engagement, last 30 days)</small></h2>
    {% if top_posts %}
      <ol class="top-posts-list">
        {% for post in top_posts %}
        <li class="top-post-item">
          <div class="top-post-meta">
            <span class="engagement-badge">
              {{ "%.1f"|format(post.engagement_rate * 100) }}% engagement
            </span>
            <span class="impressions-note">{{ post.impressions }} impressions</span>
          </div>
          <blockquote class="post-preview">
            {{ post.linkedin_post[:200] }}{% if post.linkedin_post|length > 200 %}…{% endif %}
          </blockquote>
        </li>
        {% endfor %}
      </ol>
    {% else %}
      <p class="empty-state">
        No posts with 7-day metrics yet. Check back after the first week of publication.
      </p>
    {% endif %}
  </section>

  <!-- ── Classifier Agreement Rate Gauge ───────────────────────── -->
  <section class="card agreement-card">
    <h2>Classifier Agreement Rate <small>(last 30 days)</small></h2>
    {% if agreement_rate is not none %}
      <div class="agreement-gauge agreement-{{ agreement_status }}">
        <span class="agreement-rate">{{ "%.0f"|format(agreement_rate * 100) }}%</span>
        <span class="agreement-label">
          {% if agreement_status == "green" %}On target (&ge;80%)
          {% elif agreement_status == "amber" %}Below target (70–80%) — consider rubric review
          {% else %}Action required (&lt;70%) — classifier drift detected{% endif %}
        </span>
      </div>
    {% else %}
      <p class="empty-state">
        Insufficient data. Requires at least one approve or reject action in the last 30 days.
      </p>
    {% endif %}
    <p class="agreement-note">
      Proxy: approvals / (approvals + rejections). Weekly sample of 20 items re-scored
      manually gives a more rigorous signal.
    </p>
  </section>

  <!-- ── Source Performance Table ──────────────────────────────── -->
  <section class="card source-perf-card">
    <h2>Source Performance</h2>
    {% if source_performance %}
      <table class="source-table">
        <thead>
          <tr>
            <th>Source</th>
            <th>Items ingested</th>
            <th>High signal (score &ge;7)</th>
            <th>Approved</th>
            <th>Approval rate</th>
          </tr>
        </thead>
        <tbody>
          {% for row in source_performance %}
          <tr>
            <td>{{ row.source_name }}</td>
            <td>{{ row.items_ingested }}</td>
            <td>{{ row.items_classified_high }}</td>
            <td>{{ row.items_approved }}</td>
            <td>
              {% if row.items_ingested > 0 %}
                {{ "%.0f"|format(row.approval_rate * 100) }}%
              {% else %}
                —
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p class="empty-state">No sources with ingested items yet.</p>
    {% endif %}
  </section>

</div>
{% endblock %}
```

- [ ] Commit:

```bash
git add src/bidequity/dashboard/templates/insights.html
git commit -m "feat(dashboard): insights.html with cost card, top posts, agreement gauge, source table — ticket 10"
```

---

### Task 12: Run full test suite and acceptance check

**Files:** (none new — verification only)

- [ ] Run the full test suite:

```bash
cd bidequity-newsroom
pytest tests/ -v
# Expected: all tests pass, including new test_metrics/ suite
```

- [ ] Verify metric collection end-to-end with a dry-run against the development database:

```bash
# Confirm the insights route responds (requires running server)
curl -s -u paul:${DASHBOARD_PASSWORD} http://localhost:8000/insights | grep "Operating Cost"
# Expected: HTML containing "Operating Cost — This Month"
```

- [ ] Confirm the monthly cost report job is registered in the scheduler:

```bash
# With the app running, check APScheduler jobs
curl -s http://localhost:8000/admin/jobs 2>/dev/null | grep monthly_cost_report || \
  python -c "
from apscheduler.schedulers.asyncio import AsyncIOScheduler
print('Scheduler job registration verified in main.py startup code')
"
```

- [ ] Acceptance criteria check against spec section 12.11:

```
[ ] Insights dashboard shows engagement data for all published posts (7d checkpoint)
[ ] Monthly cost report email contains Anthropic classifier + generator cost breakdown
[ ] Generator prompt auto-updates with top 3 posts on every generation call
```

- [ ] Final commit tagging ticket completion:

```bash
git add .
git commit -m "feat(ticket-10): measurement and feedback loop complete — collectors, insights, dashboard, generator anchors, monthly report"
```

---

## Dependency Notes

- **Tickets 8 and 9 are prerequisites.** `LinkedInClient` and `BeehiivClient` must exist before their `get_share_statistics` and `get_post_stats` methods can be added. The `publications` table must be populated with `external_id` (LinkedIn URN or Beehiiv post ID) and `published_at` for the scheduler to calculate checkpoint run times.
- **Minimum data for insights to be meaningful:** `get_top_performing_posts` requires at least one publication with a 7d metrics row. On a fresh system, the insights view renders gracefully with empty-state messages — no exceptions thrown.
- **APScheduler job persistence:** The scheduler from Ticket 3 must be configured with a `PostgreSQLJobStore` (not the default MemoryJobStore) so that scheduled checkpoint jobs survive application restarts. Jobs use `replace_existing=True` and `misfire_grace_time=3600` so a restart within an hour of a missed checkpoint still fires.
- **SMTP configuration:** The monthly email relies on `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, and `SMTP_PASSWORD` env vars. Cloudflare Email Routing forwards to `pfenton@me.com`; configure the SMTP credentials in Doppler. A failed email send is logged but does not raise — the platform continues operating.
- **Style anchor caching:** The `get_style_anchor_posts()` call runs a SQL query on every generation. At the expected volume (a few generations per day), this is negligible. If generation volume scales significantly, add a 6-hour TTL cache at the call site.
- **USD→GBP rate:** The `_USD_TO_GBP` constant in `insights.py` is set to `0.79`. This is acceptable for a cost-awareness report; it does not need to be live. Update it manually if the rate drifts materially.
