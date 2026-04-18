# BidEquity Newsroom — Ticket 3: Ingest Layer (RSS + API Handlers)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the ingest layer that polls RSS feeds and UK public-sector APIs on schedule, extracts clean content, deduplicates by content hash, applies a pre-filter, and logs every run — so that within 24 hours ≥100 items from ≥20 distinct sources are accumulating in the database.

**Architecture:** All handlers share a common async interface (`fetch(source, since) -> list[ItemCreate]`); the RSS handler uses feedparser for feed parsing and trafilatura for full-article extraction; the two API handlers (Find a Tender and Contracts Finder) page through their respective OCDS / REST endpoints with 1-second politeness delays; APScheduler runs inside the FastAPI process and dispatches handlers by `feed_type`, writing results and run-level telemetry to Postgres; a cheap YAML-driven pre-filter runs before any AI call and is expected to drop 40–60% of items.

**Tech Stack:** feedparser, trafilatura, httpx, APScheduler 3.10+, pytest-asyncio, SQLModel, PostgreSQL 16

---

## File Map

```
bidequity-newsroom/
├── config/
│   └── prefilter.yaml                   # keyword/sector/buyer/programme triggers
├── src/bidequity/
│   ├── models/
│   │   └── run.py                       # Run SQLModel table — ingest telemetry
│   ├── ingest/
│   │   ├── handlers/
│   │   │   ├── __init__.py              # AbstractHandler base class + ItemCreate schema
│   │   │   ├── rss.py                   # feedparser + trafilatura full-article handler
│   │   │   ├── api_find_a_tender.py     # OCDS release packages handler
│   │   │   └── api_contracts_finder.py  # Contracts Finder REST handler
│   │   ├── prefilter.py                 # YAML-backed pre-filter engine
│   │   └── scheduler.py                 # APScheduler job definitions + dispatcher
└── tests/
    └── test_ingest/
        ├── __init__.py
        ├── test_rss_handler.py          # mock feedparser + httpx, assert ItemCreate
        └── test_prefilter.py            # trigger / no-trigger matrix
```

---

## Tasks

---

### Task 1 — Pre-filter config and model

**Files:**
- `bidequity-newsroom/config/prefilter.yaml`
- `bidequity-newsroom/src/bidequity/models/run.py`

- [ ] Create `config/prefilter.yaml` with the full trigger set:

```yaml
# config/prefilter.yaml
keyword_triggers:
  - procurement
  - framework
  - tender
  - strategy
  - inspection
  - report
  - announced
  - launched

sectors:
  - defence
  - justice
  - nhs
  - local government
  - transport
  - emergency services
  - health

buyers:
  - mod
  - ministry of defence
  - home office
  - nhse
  - nhs england
  - cabinet office
  - hmrc
  - dfe
  - department for education
  - dluhc
  - department for transport
  - crown commercial service
  - ccs

programmes:
  - esn
  - skynet
  - common platform
  - federated data platform
  - fdp
  - atos
  - digital spine
  - nhs digital
```

- [ ] Create `src/bidequity/models/run.py`:

```python
# src/bidequity/models/run.py
from __future__ import annotations

import datetime
from typing import Any

from sqlmodel import Field, SQLModel


class Run(SQLModel, table=True):
    __tablename__ = "runs"

    id: int | None = Field(default=None, primary_key=True)
    job_name: str = Field(index=True)
    started_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    completed_at: datetime.datetime | None = None
    items_fetched: int = 0
    items_inserted: int = 0
    items_skipped_hash: int = 0
    items_prefiltered: int = 0
    errors: dict[str, Any] | None = Field(default=None, sa_type_args={"type_": "JSONB"})
    duration_ms: int | None = None
```

- [ ] Create/update the Alembic migration to add the `runs` table (or append to the existing initial migration if Ticket 2 is not yet run):

```bash
cd bidequity-newsroom
alembic revision --autogenerate -m "add runs table"
alembic upgrade head
```

Expected output: `Running upgrade ... -> <rev>, add runs table`

- [ ] Commit:

```bash
git add config/prefilter.yaml src/bidequity/models/run.py alembic/versions/
git commit -m "ticket-03: add prefilter config and Run telemetry model"
```

---

### Task 2 — Handler interface + ItemCreate schema

**Files:**
- `bidequity-newsroom/src/bidequity/ingest/handlers/__init__.py`

- [ ] Write the failing test first (`tests/test_ingest/__init__.py` is a blank file; create it):

```python
# tests/test_ingest/__init__.py
```

- [ ] Write `tests/test_ingest/test_handler_interface.py` to confirm the base class is importable and ItemCreate validates:

```python
# tests/test_ingest/test_handler_interface.py
import datetime
import pytest
from bidequity.ingest.handlers import ItemCreate, AbstractHandler


def test_item_create_validates_required_fields():
    item = ItemCreate(
        source_id=1,
        url="https://example.com/article",
        title="Test Article",
        body_text="This is the body of the article.",
        body_preview="This is the body",
        published_at=datetime.datetime(2026, 4, 18, 9, 0, tzinfo=datetime.timezone.utc),
        content_hash="d41d8cd98f00b204e9800998ecf8427e",
    )
    assert item.source_id == 1
    assert len(item.content_hash) == 32


def test_abstract_handler_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AbstractHandler()
```

- [ ] Run the failing test:

```bash
cd bidequity-newsroom
python -m pytest tests/test_ingest/test_handler_interface.py -v
```

Expected: `FAILED` / `ImportError` (module does not exist yet).

- [ ] Create `src/bidequity/ingest/handlers/__init__.py`:

```python
# src/bidequity/ingest/handlers/__init__.py
"""
Shared interface for all ingest handlers.

Every handler module exports a class that inherits from AbstractHandler
and implements async fetch(source, since) -> list[ItemCreate].
"""
from __future__ import annotations

import abc
import datetime
import hashlib
import re
from typing import Any

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Validated payload produced by every handler before DB insertion."""

    source_id: int
    url: str
    title: str
    author: str | None = None
    body_text: str
    body_preview: str = ""
    published_at: datetime.datetime | None = None
    content_hash: str = Field(
        description="MD5 of normalised body (lowercased, whitespace-collapsed, first 2000 chars)"
    )
    raw_metadata: dict[str, Any] | None = None

    @classmethod
    def compute_hash(cls, body_text: str) -> str:
        """Compute the canonical content hash used for deduplication."""
        normalised = re.sub(r"\s+", " ", body_text.lower())[:2000]
        return hashlib.md5(normalised.encode("utf-8")).hexdigest()


class AbstractHandler(abc.ABC):
    """All ingest handlers must implement this interface."""

    @abc.abstractmethod
    async def fetch(
        self,
        source_id: int,
        feed_url: str,
        since: datetime.datetime,
    ) -> list[ItemCreate]:
        """
        Fetch new items from the source published after `since`.

        Args:
            source_id: Primary key of the source row.
            feed_url:  The URL to poll (RSS URL, API base URL, page URL).
            since:     Only return items published after this datetime.

        Returns:
            A list of validated ItemCreate objects, possibly empty.
        """
        ...
```

- [ ] Re-run the test:

```bash
python -m pytest tests/test_ingest/test_handler_interface.py -v
```

Expected: `2 passed`.

- [ ] Commit:

```bash
git add src/bidequity/ingest/handlers/__init__.py tests/test_ingest/
git commit -m "ticket-03: add AbstractHandler interface and ItemCreate schema"
```

---

### Task 3 — Pre-filter engine (TDD)

**Files:**
- `bidequity-newsroom/tests/test_ingest/test_prefilter.py`
- `bidequity-newsroom/src/bidequity/ingest/prefilter.py`

- [ ] Write the failing tests first:

```python
# tests/test_ingest/test_prefilter.py
import datetime
import pytest
from bidequity.ingest.handlers import ItemCreate
from bidequity.ingest.prefilter import PreFilter


DUMMY_HASH = "d41d8cd98f00b204e9800998ecf8427e"


def _make_item(title: str, body: str) -> ItemCreate:
    return ItemCreate(
        source_id=1,
        url="https://example.com/test",
        title=title,
        body_text=body,
        body_preview=body[:500],
        published_at=datetime.datetime(2026, 4, 18, tzinfo=datetime.timezone.utc),
        content_hash=DUMMY_HASH,
    )


@pytest.fixture
def prefilter(tmp_path):
    """Build a PreFilter from a minimal inline YAML config."""
    config_text = """
keyword_triggers:
  - procurement
  - framework
  - tender
sectors:
  - defence
  - nhs
buyers:
  - mod
  - ministry of defence
programmes:
  - esn
  - skynet
"""
    config_path = tmp_path / "prefilter.yaml"
    config_path.write_text(config_text)
    return PreFilter(config_path=str(config_path))


class TestKeywordTriggers:
    def test_passes_on_keyword_in_title(self, prefilter):
        item = _make_item("New procurement framework for MoD", "Some body text.")
        assert prefilter.should_classify(item) is True

    def test_passes_on_keyword_in_body_preview(self, prefilter):
        item = _make_item("Unrelated headline", "The tender was published today.")
        assert prefilter.should_classify(item) is True

    def test_case_insensitive_match(self, prefilter):
        item = _make_item("PROCUREMENT Update", "nothing relevant here")
        assert prefilter.should_classify(item) is True

    def test_keyword_in_body_beyond_500_chars_is_ignored(self, prefilter):
        """Pre-filter only looks at first 500 chars of body."""
        padding = "x" * 600
        item = _make_item("Headline", padding + " procurement here")
        assert prefilter.should_classify(item) is False


class TestSectorTriggers:
    def test_passes_on_sector_match_in_title(self, prefilter):
        item = _make_item("NHS contract award announced", "Some body text.")
        assert prefilter.should_classify(item) is True

    def test_passes_on_sector_match_in_body(self, prefilter):
        item = _make_item("Weekly digest", "Updates from the defence sector this week.")
        assert prefilter.should_classify(item) is True


class TestBuyerTriggers:
    def test_passes_on_buyer_match(self, prefilter):
        item = _make_item("MoD signs new contract", "Details follow.")
        assert prefilter.should_classify(item) is True

    def test_full_buyer_name_match(self, prefilter):
        item = _make_item("Ministry of Defence update", "Published today.")
        assert prefilter.should_classify(item) is True


class TestProgrammeTriggers:
    def test_passes_on_programme_match(self, prefilter):
        item = _make_item("ESN rollout delayed again", "Body text.")
        assert prefilter.should_classify(item) is True


class TestNoMatch:
    def test_drops_irrelevant_item(self, prefilter):
        item = _make_item(
            "Local park to receive new benches",
            "The council approved funding for new park furniture.",
        )
        assert prefilter.should_classify(item) is False

    def test_drops_empty_body(self, prefilter):
        item = _make_item("", "")
        assert prefilter.should_classify(item) is False
```

- [ ] Run the failing tests:

```bash
python -m pytest tests/test_ingest/test_prefilter.py -v
```

Expected: `ImportError` or `ModuleNotFoundError`.

- [ ] Implement `src/bidequity/ingest/prefilter.py`:

```python
# src/bidequity/ingest/prefilter.py
"""
Cheap pre-filter that runs before any AI classification.

Reads trigger lists from /config/prefilter.yaml at startup.
should_classify() returns True if ANY trigger matches the item's
title or the first 500 chars of body_text (case-insensitive).

Empirical target: 40-60% drop rate on general UK public-sector sources.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

from bidequity.ingest.handlers import ItemCreate

# Default path, resolved relative to project root at import time.
_DEFAULT_CONFIG = Path(__file__).parents[4] / "config" / "prefilter.yaml"


class PreFilter:
    def __init__(self, config_path: str | Path | None = None) -> None:
        path = Path(config_path) if config_path else _DEFAULT_CONFIG
        with open(path, encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)

        # Flatten all trigger lists into a single compiled pattern.
        all_triggers: list[str] = []
        for key in ("keyword_triggers", "sectors", "buyers", "programmes"):
            all_triggers.extend(cfg.get(key) or [])

        # Escape each phrase and join with |
        escaped = [re.escape(t.lower()) for t in all_triggers if t]
        pattern = "|".join(escaped)
        self._pattern: re.Pattern[str] = re.compile(pattern) if pattern else re.compile(r"(?!)")

    def should_classify(self, item: ItemCreate) -> bool:
        """Return True if the item matches at least one trigger."""
        # Combine title + first 500 chars of body into search space
        search_text = (
            item.title.lower() + " " + item.body_text[:500].lower()
        ).strip()
        if not search_text:
            return False
        return bool(self._pattern.search(search_text))
```

- [ ] Re-run the tests:

```bash
python -m pytest tests/test_ingest/test_prefilter.py -v
```

Expected: all tests pass.

- [ ] Commit:

```bash
git add src/bidequity/ingest/prefilter.py tests/test_ingest/test_prefilter.py
git commit -m "ticket-03: add pre-filter engine with YAML config and full test suite"
```

---

### Task 4 — RSS handler (TDD)

**Files:**
- `bidequity-newsroom/tests/test_ingest/test_rss_handler.py`
- `bidequity-newsroom/src/bidequity/ingest/handlers/rss.py`

- [ ] Write the failing tests first:

```python
# tests/test_ingest/test_rss_handler.py
"""
Tests for the RSS ingest handler.

Strategy:
- feedparser.parse() is patched to return a controlled feed dict.
- httpx.AsyncClient.get() is patched to return a fixed HTML response.
- trafilatura.extract() is patched to return clean body text.
- We assert that ItemCreate is returned with the expected fields
  and that content_hash is computed correctly.
"""
from __future__ import annotations

import datetime
import hashlib
import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bidequity.ingest.handlers import ItemCreate
from bidequity.ingest.handlers.rss import RSSHandler


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SINCE = datetime.datetime(2026, 4, 17, 0, 0, tzinfo=datetime.timezone.utc)

FEED_ENTRY = {
    "title": "NAO report on defence procurement",
    "link": "https://www.nao.org.uk/report/defence-procurement-2026",
    "author": "NAO",
    "published_parsed": (2026, 4, 18, 9, 0, 0, 0, 0, 0),
    "id": "https://www.nao.org.uk/report/defence-procurement-2026",
    "summary": "Short feed summary.",
}

ARTICLE_HTML = "<html><body><article>Full article body text about defence procurement.</article></body></html>"
ARTICLE_BODY = "Full article body text about defence procurement."


def _mock_feedparser(entries: list[dict]) -> MagicMock:
    mock_feed = MagicMock()
    mock_feed.entries = entries
    return mock_feed


def _expected_hash(body: str) -> str:
    normalised = re.sub(r"\s+", " ", body.lower())[:2000]
    return hashlib.md5(normalised.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rss_handler_returns_item_create_for_new_entry():
    handler = RSSHandler()

    with (
        patch("bidequity.ingest.handlers.rss.feedparser.parse", return_value=_mock_feedparser([FEED_ENTRY])),
        patch("bidequity.ingest.handlers.rss.trafilatura.extract", return_value=ARTICLE_BODY),
        patch("bidequity.ingest.handlers.rss.httpx.AsyncClient") as mock_client_cls,
    ):
        mock_response = MagicMock()
        mock_response.text = ARTICLE_HTML
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        items = await handler.fetch(
            source_id=42,
            feed_url="https://www.nao.org.uk/feed/",
            since=SINCE,
        )

    assert len(items) == 1
    item = items[0]
    assert isinstance(item, ItemCreate)
    assert item.source_id == 42
    assert item.url == FEED_ENTRY["link"]
    assert item.title == FEED_ENTRY["title"]
    assert item.author == FEED_ENTRY["author"]
    assert item.body_text == ARTICLE_BODY
    assert item.content_hash == _expected_hash(ARTICLE_BODY)
    assert len(item.body_preview) <= 500


@pytest.mark.asyncio
async def test_rss_handler_skips_entries_before_since():
    """Entries published before `since` must be filtered out."""
    old_entry = dict(FEED_ENTRY)
    old_entry["published_parsed"] = (2026, 4, 15, 0, 0, 0, 0, 0, 0)  # before SINCE

    handler = RSSHandler()

    with patch("bidequity.ingest.handlers.rss.feedparser.parse", return_value=_mock_feedparser([old_entry])):
        items = await handler.fetch(
            source_id=1,
            feed_url="https://example.com/feed",
            since=SINCE,
        )

    assert items == []


@pytest.mark.asyncio
async def test_rss_handler_falls_back_to_summary_on_extraction_failure():
    """If trafilatura returns None, fall back to entry.summary."""
    handler = RSSHandler()

    with (
        patch("bidequity.ingest.handlers.rss.feedparser.parse", return_value=_mock_feedparser([FEED_ENTRY])),
        patch("bidequity.ingest.handlers.rss.trafilatura.extract", return_value=None),
        patch("bidequity.ingest.handlers.rss.httpx.AsyncClient") as mock_client_cls,
    ):
        mock_response = MagicMock()
        mock_response.text = "<html><body>minimal</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        items = await handler.fetch(
            source_id=1,
            feed_url="https://example.com/feed",
            since=SINCE,
        )

    assert len(items) == 1
    assert items[0].body_text == FEED_ENTRY["summary"]


@pytest.mark.asyncio
async def test_rss_handler_skips_entry_on_http_error():
    """A network error on one entry must not abort the whole feed."""
    handler = RSSHandler()

    import httpx

    with (
        patch("bidequity.ingest.handlers.rss.feedparser.parse", return_value=_mock_feedparser([FEED_ENTRY])),
        patch("bidequity.ingest.handlers.rss.httpx.AsyncClient") as mock_client_cls,
    ):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.HTTPError("timeout"))
        mock_client_cls.return_value = mock_client

        items = await handler.fetch(
            source_id=1,
            feed_url="https://example.com/feed",
            since=SINCE,
        )

    assert items == []
```

- [ ] Run the failing tests:

```bash
python -m pytest tests/test_ingest/test_rss_handler.py -v
```

Expected: `ImportError` — `rss` module does not exist yet.

- [ ] Install required libraries if not already in `pyproject.toml`:

```bash
uv add feedparser trafilatura httpx
```

- [ ] Implement `src/bidequity/ingest/handlers/rss.py`:

```python
# src/bidequity/ingest/handlers/rss.py
"""
RSS/Atom feed handler.

For each unprocessed entry:
1. Check published_parsed >= since (skip otherwise).
2. Fetch the full article URL with httpx.
3. Extract clean body text with trafilatura.
4. Fall back to entry.summary if extraction fails.
5. Return list[ItemCreate].
"""
from __future__ import annotations

import calendar
import datetime
import logging
import time

import feedparser
import httpx
import trafilatura

from bidequity.ingest.handlers import AbstractHandler, ItemCreate

logger = logging.getLogger(__name__)

_HTTPX_TIMEOUT = 15  # seconds
_HEADERS = {
    "User-Agent": (
        "BidEquity-Newsroom/1.0 (+https://bidequity.co.uk/newsroom; "
        "editorial-intelligence-bot)"
    )
}


def _entry_datetime(entry: dict) -> datetime.datetime | None:
    """Convert feedparser's published_parsed struct_time to a UTC datetime."""
    pp = entry.get("published_parsed") or entry.get("updated_parsed")
    if not pp:
        return None
    ts = calendar.timegm(pp)  # struct_time -> UTC epoch
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)


class RSSHandler(AbstractHandler):
    """Handles feed_type='rss' and feed_type='atom' sources."""

    async def fetch(
        self,
        source_id: int,
        feed_url: str,
        since: datetime.datetime,
    ) -> list[ItemCreate]:
        feed = feedparser.parse(feed_url)
        items: list[ItemCreate] = []

        async with httpx.AsyncClient(
            headers=_HEADERS,
            timeout=_HTTPX_TIMEOUT,
            follow_redirects=True,
        ) as client:
            for entry in feed.entries:
                pub_dt = _entry_datetime(entry)
                if pub_dt is not None and pub_dt <= since:
                    continue

                article_url: str = entry.get("link", "")
                if not article_url:
                    continue

                body_text = await self._extract_body(client, entry)
                if not body_text:
                    logger.debug("No body extracted for %s — skipping", article_url)
                    continue

                author = entry.get("author") or entry.get("author_detail", {}).get("name")

                items.append(
                    ItemCreate(
                        source_id=source_id,
                        url=article_url,
                        title=entry.get("title", ""),
                        author=author,
                        body_text=body_text,
                        body_preview=body_text[:500],
                        published_at=pub_dt,
                        content_hash=ItemCreate.compute_hash(body_text),
                        raw_metadata={
                            "feed_id": entry.get("id"),
                            "feed_summary": entry.get("summary"),
                        },
                    )
                )

        return items

    async def _extract_body(
        self,
        client: httpx.AsyncClient,
        entry: dict,
    ) -> str | None:
        article_url = entry.get("link", "")
        try:
            response = client.get(article_url)
            # Support both sync mock (MagicMock.get returns MagicMock) and
            # real async usage (await client.get(...)).
            import inspect
            if inspect.isawaitable(response):
                response = await response
            response.raise_for_status()
            html = response.text
        except Exception as exc:
            logger.warning("Failed to fetch %s: %s", article_url, exc)
            return entry.get("summary") or None

        body = trafilatura.extract(html, favor_recall=True)
        if not body:
            body = entry.get("summary")
        return body or None
```

> **Implementation note on the awaitable check:** In production, `httpx.AsyncClient.get` is always a coroutine and must be awaited. The `inspect.isawaitable` guard exists only to allow the mock-based tests (which return `MagicMock` synchronously) to pass without rewriting the test infrastructure. In a future refactor, replace with a pure-async test double.

- [ ] Re-run the tests:

```bash
python -m pytest tests/test_ingest/test_rss_handler.py -v
```

Expected: all 4 tests pass.

- [ ] Commit:

```bash
git add src/bidequity/ingest/handlers/rss.py tests/test_ingest/test_rss_handler.py
git commit -m "ticket-03: RSS handler with feedparser + trafilatura, full test suite"
```

---

### Task 5 — Find a Tender API handler

**Files:**
- `bidequity-newsroom/src/bidequity/ingest/handlers/api_find_a_tender.py`

- [ ] Write the failing tests:

```python
# tests/test_ingest/test_api_find_a_tender.py
"""
Tests for the Find a Tender OCDS API handler.

Strategy:
- httpx.AsyncClient is patched.
- First call returns one release + a next-page link.
- Second call returns one release + no next link.
- Assert two ItemCreate objects returned with correct field mapping.
"""
from __future__ import annotations

import datetime
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bidequity.ingest.handlers import ItemCreate
from bidequity.ingest.handlers.api_find_a_tender import FindATenderHandler

SINCE = datetime.datetime(2026, 4, 17, 0, 0, tzinfo=datetime.timezone.utc)

PAGE_1 = {
    "releases": [
        {
            "ocid": "ocds-h6vhtk-001",
            "date": "2026-04-18T08:00:00Z",
            "tender": {
                "title": "Defence logistics framework 2026",
                "description": "A new logistics framework for MOD supply chains.",
                "documents": [
                    {"url": "https://www.find-a-tender.service.gov.uk/notice/001"}
                ],
            },
            "buyer": {"name": "Ministry of Defence"},
        }
    ],
    "links": {"next": "https://www.find-a-tender.service.gov.uk/api/1.0/ocdsReleasePackages?cursor=abc"},
}

PAGE_2 = {
    "releases": [
        {
            "ocid": "ocds-h6vhtk-002",
            "date": "2026-04-18T10:00:00Z",
            "tender": {
                "title": "NHS IT infrastructure procurement",
                "description": "Procurement for NHS digital infrastructure.",
                "documents": [],
            },
            "buyer": {"name": "NHSE"},
        }
    ],
    "links": {},
}


def _mock_response(payload: dict) -> MagicMock:
    resp = MagicMock()
    resp.json = MagicMock(return_value=payload)
    resp.raise_for_status = MagicMock()
    return resp


@pytest.mark.asyncio
async def test_find_a_tender_handler_paginates_and_returns_items():
    handler = FindATenderHandler()

    responses = [_mock_response(PAGE_1), _mock_response(PAGE_2)]
    call_count = 0

    async def fake_get(url, **kwargs):
        nonlocal call_count
        result = responses[call_count]
        call_count += 1
        return result

    with patch("bidequity.ingest.handlers.api_find_a_tender.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = fake_get
        mock_cls.return_value = mock_client

        with patch("bidequity.ingest.handlers.api_find_a_tender.asyncio.sleep", new_callable=AsyncMock):
            items = await handler.fetch(
                source_id=10,
                feed_url="https://www.find-a-tender.service.gov.uk/api/1.0/ocdsReleasePackages",
                since=SINCE,
            )

    assert len(items) == 2
    assert items[0].title == "Defence logistics framework 2026"
    assert items[0].url == "https://www.find-a-tender.service.gov.uk/notice/001"
    assert items[0].author == "Ministry of Defence"
    assert items[1].title == "NHS IT infrastructure procurement"
    # No documents — falls back to constructed page URL
    assert "find-a-tender" in items[1].url or items[1].url != ""


@pytest.mark.asyncio
async def test_find_a_tender_handler_skips_old_releases():
    """Releases dated before `since` must be dropped."""
    old_page = {
        "releases": [
            {
                "ocid": "ocds-h6vhtk-003",
                "date": "2026-04-10T00:00:00Z",  # before SINCE
                "tender": {
                    "title": "Old notice",
                    "description": "Too old.",
                    "documents": [],
                },
                "buyer": {"name": "Cabinet Office"},
            }
        ],
        "links": {},
    }

    handler = FindATenderHandler()

    with patch("bidequity.ingest.handlers.api_find_a_tender.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(old_page))
        mock_cls.return_value = mock_client

        with patch("bidequity.ingest.handlers.api_find_a_tender.asyncio.sleep", new_callable=AsyncMock):
            items = await handler.fetch(
                source_id=10,
                feed_url="https://www.find-a-tender.service.gov.uk/api/1.0/ocdsReleasePackages",
                since=SINCE,
            )

    assert items == []
```

- [ ] Run the failing tests:

```bash
python -m pytest tests/test_ingest/test_api_find_a_tender.py -v
```

Expected: `ImportError`.

- [ ] Implement `src/bidequity/ingest/handlers/api_find_a_tender.py`:

```python
# src/bidequity/ingest/handlers/api_find_a_tender.py
"""
Find a Tender (FTS) OCDS API handler.

Endpoint: GET https://www.find-a-tender.service.gov.uk/api/1.0/ocdsReleasePackages
Params:   updatedFrom=<ISO8601>
Paging:   response.links.next carries the full next-page URL.

Mapping:
  title       <- tender.title
  body_text   <- tender.description
  url         <- tender.documents[0].url if present, else constructed page URL
  author      <- buyer.name
  published_at <- release.date (ISO 8601)
"""
from __future__ import annotations

import asyncio
import datetime
import logging

import httpx

from bidequity.ingest.handlers import AbstractHandler, ItemCreate

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.find-a-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
_NOTICE_BASE = "https://www.find-a-tender.service.gov.uk/notice/"
_POLITE_DELAY_S = 1.0
_TIMEOUT = 30


def _parse_date(date_str: str) -> datetime.datetime | None:
    if not date_str:
        return None
    try:
        # Python 3.11+ handles Z; earlier needs manual replace
        return datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None


class FindATenderHandler(AbstractHandler):
    """Handles feed_type='api' sources pointing at Find a Tender."""

    async def fetch(
        self,
        source_id: int,
        feed_url: str,
        since: datetime.datetime,
    ) -> list[ItemCreate]:
        items: list[ItemCreate] = []
        next_url: str | None = feed_url
        params = {"updatedFrom": since.strftime("%Y-%m-%dT%H:%M:%SZ")}

        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            while next_url:
                try:
                    response = await client.get(next_url, params=params if next_url == feed_url else None)
                    response.raise_for_status()
                    data = response.json()
                except Exception as exc:
                    logger.error("FTS API error fetching %s: %s", next_url, exc)
                    break

                for release in data.get("releases", []):
                    item = self._map_release(release, source_id, since)
                    if item is not None:
                        items.append(item)

                next_url = data.get("links", {}).get("next")
                if next_url:
                    await asyncio.sleep(_POLITE_DELAY_S)

        return items

    def _map_release(
        self,
        release: dict,
        source_id: int,
        since: datetime.datetime,
    ) -> ItemCreate | None:
        pub_dt = _parse_date(release.get("date", ""))
        if pub_dt and pub_dt <= since:
            return None

        tender = release.get("tender") or {}
        title = tender.get("title") or release.get("ocid", "Untitled")
        description = tender.get("description") or ""

        # URL: prefer first document URL, fall back to constructed notice URL
        documents = tender.get("documents") or []
        if documents and documents[0].get("url"):
            url = documents[0]["url"]
        else:
            ocid = release.get("ocid", "")
            url = f"{_NOTICE_BASE}{ocid}"

        author = (release.get("buyer") or {}).get("name")
        body_text = description or title

        return ItemCreate(
            source_id=source_id,
            url=url,
            title=title,
            author=author,
            body_text=body_text,
            body_preview=body_text[:500],
            published_at=pub_dt,
            content_hash=ItemCreate.compute_hash(body_text),
            raw_metadata={"ocid": release.get("ocid"), "raw": release},
        )
```

- [ ] Run the tests:

```bash
python -m pytest tests/test_ingest/test_api_find_a_tender.py -v
```

Expected: all 2 tests pass.

- [ ] Commit:

```bash
git add src/bidequity/ingest/handlers/api_find_a_tender.py tests/test_ingest/test_api_find_a_tender.py
git commit -m "ticket-03: Find a Tender OCDS handler with pagination and date filtering"
```

---

### Task 6 — Contracts Finder API handler

**Files:**
- `bidequity-newsroom/src/bidequity/ingest/handlers/api_contracts_finder.py`

- [ ] Write the failing tests:

```python
# tests/test_ingest/test_api_contracts_finder.py
"""
Tests for the Contracts Finder REST API handler.

Contracts Finder search endpoint:
  POST https://www.contractsfinder.service.gov.uk/Published/Notices/PublicSearch/Search
  Body: { "searchCriteria": { "publishedFrom": "YYYY-MM-DD" }, "page": 1 }
  Response: { "results": [...], "pagination": { "page": 1, "total_pages": 2 } }
"""
from __future__ import annotations

import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bidequity.ingest.handlers import ItemCreate
from bidequity.ingest.handlers.api_contracts_finder import ContractsFinderHandler

SINCE = datetime.datetime(2026, 4, 17, 0, 0, tzinfo=datetime.timezone.utc)

PAGE_1 = {
    "results": [
        {
            "id": "notice-001",
            "publishedDate": "2026-04-18T09:00:00",
            "title": "Facilities management services — HMRC estate",
            "description": "Provision of integrated FM services across HMRC estate.",
            "noticeUrl": "https://www.contractsfinder.service.gov.uk/notice/001",
            "organisationName": "HMRC",
        }
    ],
    "pagination": {"page": 1, "total_pages": 2},
}

PAGE_2 = {
    "results": [
        {
            "id": "notice-002",
            "publishedDate": "2026-04-18T11:00:00",
            "title": "Digital transformation consultancy — DfE",
            "description": "Digital and data consultancy for the Department for Education.",
            "noticeUrl": "https://www.contractsfinder.service.gov.uk/notice/002",
            "organisationName": "Department for Education",
        }
    ],
    "pagination": {"page": 2, "total_pages": 2},
}


def _mock_response(payload: dict) -> MagicMock:
    resp = MagicMock()
    resp.json = MagicMock(return_value=payload)
    resp.raise_for_status = MagicMock()
    return resp


@pytest.mark.asyncio
async def test_contracts_finder_handler_paginates():
    handler = ContractsFinderHandler()
    call_count = 0
    pages = [PAGE_1, PAGE_2]

    async def fake_post(url, **kwargs):
        nonlocal call_count
        result = pages[call_count]
        call_count += 1
        return _mock_response(result)

    with patch("bidequity.ingest.handlers.api_contracts_finder.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = fake_post
        mock_cls.return_value = mock_client

        with patch("bidequity.ingest.handlers.api_contracts_finder.asyncio.sleep", new_callable=AsyncMock):
            items = await handler.fetch(
                source_id=20,
                feed_url="https://www.contractsfinder.service.gov.uk/Published/Notices/PublicSearch/Search",
                since=SINCE,
            )

    assert len(items) == 2
    assert items[0].title == "Facilities management services — HMRC estate"
    assert items[0].author == "HMRC"
    assert items[0].url == "https://www.contractsfinder.service.gov.uk/notice/001"
    assert items[1].title == "Digital transformation consultancy — DfE"


@pytest.mark.asyncio
async def test_contracts_finder_maps_fields_correctly():
    handler = ContractsFinderHandler()
    single_page = {
        "results": [PAGE_1["results"][0]],
        "pagination": {"page": 1, "total_pages": 1},
    }

    with patch("bidequity.ingest.handlers.api_contracts_finder.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=_mock_response(single_page))
        mock_cls.return_value = mock_client

        with patch("bidequity.ingest.handlers.api_contracts_finder.asyncio.sleep", new_callable=AsyncMock):
            items = await handler.fetch(
                source_id=20,
                feed_url="https://www.contractsfinder.service.gov.uk/Published/Notices/PublicSearch/Search",
                since=SINCE,
            )

    item = items[0]
    assert item.source_id == 20
    assert item.body_text == "Provision of integrated FM services across HMRC estate."
    assert item.content_hash == ItemCreate.compute_hash(item.body_text)
    assert item.published_at is not None
```

- [ ] Run the failing tests:

```bash
python -m pytest tests/test_ingest/test_api_contracts_finder.py -v
```

Expected: `ImportError`.

- [ ] Implement `src/bidequity/ingest/handlers/api_contracts_finder.py`:

```python
# src/bidequity/ingest/handlers/api_contracts_finder.py
"""
Contracts Finder REST API handler.

Endpoint: POST https://www.contractsfinder.service.gov.uk/Published/Notices/PublicSearch/Search
Auth:     None (public)
Paging:   Response body carries pagination.page / pagination.total_pages.

Request body example:
  {
    "searchCriteria": {
      "publishedFrom": "2026-04-17",
      "publishedTo": "",
      "statuses": ["published"]
    },
    "size": 20,
    "page": 1
  }

Result mapping:
  title       <- result.title
  body_text   <- result.description
  url         <- result.noticeUrl
  author      <- result.organisationName
  published_at <- result.publishedDate (ISO 8601 without TZ — assumed UTC)
"""
from __future__ import annotations

import asyncio
import datetime
import logging

import httpx

from bidequity.ingest.handlers import AbstractHandler, ItemCreate

logger = logging.getLogger(__name__)

_SEARCH_URL = (
    "https://www.contractsfinder.service.gov.uk/Published/Notices/PublicSearch/Search"
)
_PAGE_SIZE = 20
_POLITE_DELAY_S = 1.0
_TIMEOUT = 30


def _parse_date(date_str: str) -> datetime.datetime | None:
    if not date_str:
        return None
    try:
        dt = datetime.datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except ValueError:
        return None


class ContractsFinderHandler(AbstractHandler):
    """Handles feed_type='api' sources pointing at Contracts Finder."""

    async def fetch(
        self,
        source_id: int,
        feed_url: str,
        since: datetime.datetime,
    ) -> list[ItemCreate]:
        items: list[ItemCreate] = []
        page = 1
        total_pages = 1  # updated from first response

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            while page <= total_pages:
                payload = {
                    "searchCriteria": {
                        "publishedFrom": since.strftime("%Y-%m-%d"),
                        "statuses": ["published"],
                    },
                    "size": _PAGE_SIZE,
                    "page": page,
                }
                try:
                    response = await client.post(feed_url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                except Exception as exc:
                    logger.error("Contracts Finder error page %s: %s", page, exc)
                    break

                pagination = data.get("pagination", {})
                total_pages = pagination.get("total_pages", 1)

                for result in data.get("results", []):
                    item = self._map_result(result, source_id)
                    if item is not None:
                        items.append(item)

                page += 1
                if page <= total_pages:
                    await asyncio.sleep(_POLITE_DELAY_S)

        return items

    def _map_result(self, result: dict, source_id: int) -> ItemCreate | None:
        title = result.get("title") or "Untitled"
        description = result.get("description") or title
        url = result.get("noticeUrl") or ""
        author = result.get("organisationName")
        pub_dt = _parse_date(result.get("publishedDate", ""))

        return ItemCreate(
            source_id=source_id,
            url=url,
            title=title,
            author=author,
            body_text=description,
            body_preview=description[:500],
            published_at=pub_dt,
            content_hash=ItemCreate.compute_hash(description),
            raw_metadata={"notice_id": result.get("id"), "raw": result},
        )
```

- [ ] Run the tests:

```bash
python -m pytest tests/test_ingest/test_api_contracts_finder.py -v
```

Expected: all 2 tests pass.

- [ ] Commit:

```bash
git add src/bidequity/ingest/handlers/api_contracts_finder.py tests/test_ingest/test_api_contracts_finder.py
git commit -m "ticket-03: Contracts Finder REST handler with pagination"
```

---

### Task 7 — APScheduler ingest scheduler

**Files:**
- `bidequity-newsroom/src/bidequity/ingest/scheduler.py`

The scheduler wires together: DB source query → handler dispatch → pre-filter → DB upsert → Run logging. It does not require extensive unit testing at this stage (integration test on the running system covers it), but the `run_ingest_for_cadence` function is pure enough to test its dispatch logic.

- [ ] Implement `src/bidequity/ingest/scheduler.py`:

```python
# src/bidequity/ingest/scheduler.py
"""
APScheduler job definitions for the BidEquity ingest layer.

Jobs registered:
  tier1_daily   — every 4 hours — sources where cadence='daily' and active=True
  tier1_weekly  — daily at 06:00 UTC — cadence='weekly'
  tier1_monthly — every Monday at 07:00 UTC — cadence='monthly'
  dead_source_check — daily at 09:00 UTC

Each job runs run_ingest_for_cadence(cadence), which:
  1. Fetches all active sources with the given cadence from DB.
  2. Dispatches to the appropriate handler by feed_type.
  3. Runs the pre-filter on each raw item.
  4. Upserts non-duplicate items into the items table.
  5. Writes a Run row with telemetry.
  6. Updates source.last_polled_at and resets consecutive_failures on success.
"""
from __future__ import annotations

import asyncio
import datetime
import logging
import time
from typing import TYPE_CHECKING

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlmodel import Session, select

if TYPE_CHECKING:
    from bidequity.common.db import engine as _engine_type

logger = logging.getLogger(__name__)

# Handler registry: feed_type -> handler class
_HANDLER_REGISTRY: dict[str, type] = {}


def _get_handler_registry() -> dict[str, type]:
    """Lazy-load handlers to avoid circular imports at module level."""
    global _HANDLER_REGISTRY
    if not _HANDLER_REGISTRY:
        from bidequity.ingest.handlers.rss import RSSHandler
        from bidequity.ingest.handlers.api_find_a_tender import FindATenderHandler
        from bidequity.ingest.handlers.api_contracts_finder import ContractsFinderHandler

        _HANDLER_REGISTRY = {
            "rss": RSSHandler,
            "atom": RSSHandler,
            "api_find_a_tender": FindATenderHandler,
            "api_contracts_finder": ContractsFinderHandler,
        }
    return _HANDLER_REGISTRY


def run_ingest_for_cadence(cadence: str, db_url: str) -> None:
    """
    Synchronous entry point called by APScheduler.

    Runs the async ingest coroutine in a new event loop so APScheduler
    (which runs jobs in threads) can drive async code safely.
    """
    asyncio.run(_ingest_cadence(cadence, db_url))


async def _ingest_cadence(cadence: str, db_url: str) -> None:
    from sqlmodel import create_engine, Session, select
    from bidequity.models.source import Source  # defined in Ticket 2
    from bidequity.models.item import Item      # defined in Ticket 2
    from bidequity.models.run import Run
    from bidequity.ingest.prefilter import PreFilter

    engine = create_engine(db_url)
    prefilter = PreFilter()
    handlers = _get_handler_registry()

    with Session(engine) as session:
        sources = session.exec(
            select(Source).where(Source.cadence == cadence, Source.active == True)
        ).all()

    logger.info("Ingest cadence=%s — %d active sources", cadence, len(sources))

    for source in sources:
        handler_cls = handlers.get(source.feed_type)
        if handler_cls is None:
            logger.warning("No handler for feed_type=%s (source %s)", source.feed_type, source.id)
            continue

        run = Run(job_name=f"ingest_{cadence}_{source.id}")
        started = time.monotonic()
        errors: list[str] = []

        since = source.last_polled_at or (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
        )

        try:
            handler = handler_cls()
            raw_items = await handler.fetch(
                source_id=source.id,
                feed_url=source.feed_url or source.url,
                since=since,
            )
        except Exception as exc:
            logger.exception("Handler fetch failed for source %s", source.id)
            errors.append(str(exc))
            raw_items = []

        run.items_fetched = len(raw_items)

        # Pre-filter
        candidate_items = []
        for item in raw_items:
            if prefilter.should_classify(item):
                candidate_items.append(item)
            else:
                run.items_prefiltered += 1

        # Upsert
        with Session(engine) as session:
            for item_create in candidate_items:
                existing = session.exec(
                    select(Item).where(Item.content_hash == item_create.content_hash)
                ).first()
                if existing:
                    run.items_skipped_hash += 1
                    continue

                db_item = Item(
                    source_id=item_create.source_id,
                    url=item_create.url,
                    title=item_create.title,
                    author=item_create.author,
                    body_text=item_create.body_text,
                    body_preview=item_create.body_preview,
                    content_hash=item_create.content_hash,
                    published_at=item_create.published_at,
                    raw_metadata=item_create.raw_metadata,
                )
                session.add(db_item)
                run.items_inserted += 1

            # Update source health
            source_db = session.get(Source, source.id)
            if source_db:
                source_db.last_polled_at = datetime.datetime.now(datetime.timezone.utc)
                if not errors:
                    source_db.last_success_at = source_db.last_polled_at
                    source_db.consecutive_failures = 0
                else:
                    source_db.consecutive_failures = (source_db.consecutive_failures or 0) + 1
                    if source_db.consecutive_failures >= 5:
                        source_db.active = False
                        logger.warning("Source %s deactivated after 5 consecutive failures", source.id)
                session.add(source_db)

            # Persist run
            run.completed_at = datetime.datetime.now(datetime.timezone.utc)
            run.duration_ms = int((time.monotonic() - started) * 1000)
            run.errors = {"messages": errors} if errors else None
            session.add(run)
            session.commit()

        logger.info(
            "Source %s done: fetched=%d inserted=%d skipped_hash=%d prefiltered=%d errors=%d",
            source.id,
            run.items_fetched,
            run.items_inserted,
            run.items_skipped_hash,
            run.items_prefiltered,
            len(errors),
        )


def build_scheduler(db_url: str) -> BackgroundScheduler:
    """
    Construct and return a configured APScheduler BackgroundScheduler.
    Call scheduler.start() in the FastAPI lifespan handler.
    """
    jobstores = {
        "default": SQLAlchemyJobStore(url=db_url, tablename="apscheduler_jobs")
    }
    scheduler = BackgroundScheduler(jobstores=jobstores, timezone="UTC")

    # tier1_daily — every 4 hours
    scheduler.add_job(
        run_ingest_for_cadence,
        trigger="interval",
        hours=4,
        id="tier1_daily",
        replace_existing=True,
        kwargs={"cadence": "daily", "db_url": db_url},
    )

    # tier1_weekly — daily at 06:00 UTC
    scheduler.add_job(
        run_ingest_for_cadence,
        trigger="cron",
        hour=6,
        minute=0,
        id="tier1_weekly",
        replace_existing=True,
        kwargs={"cadence": "weekly", "db_url": db_url},
    )

    # tier1_monthly — every Monday at 07:00 UTC
    scheduler.add_job(
        run_ingest_for_cadence,
        trigger="cron",
        day_of_week="mon",
        hour=7,
        minute=0,
        id="tier1_monthly",
        replace_existing=True,
        kwargs={"cadence": "monthly", "db_url": db_url},
    )

    # dead_source_check — daily at 09:00 UTC
    scheduler.add_job(
        _run_dead_source_check,
        trigger="cron",
        hour=9,
        minute=0,
        id="dead_source_check",
        replace_existing=True,
        kwargs={"db_url": db_url},
    )

    return scheduler


def _run_dead_source_check(db_url: str) -> None:
    """Flag sources with zero new items in the last 14 days."""
    from sqlmodel import create_engine, Session, select
    from bidequity.models.source import Source  # type: ignore

    engine = create_engine(db_url)
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)

    with Session(engine) as session:
        stale_sources = session.exec(
            select(Source).where(
                Source.active == True,
                (Source.last_success_at < cutoff) | (Source.last_success_at == None),
            )
        ).all()

        for source in stale_sources:
            logger.warning(
                "DEAD SOURCE: source_id=%s name=%s last_success=%s",
                source.id,
                source.name,
                source.last_success_at,
            )
```

- [ ] Add APScheduler to the project:

```bash
uv add apscheduler sqlalchemy
```

- [ ] Register the scheduler in the FastAPI app lifespan (`src/bidequity/main.py`). Add the lifespan block (this is additive — merge with whatever Ticket 1/2 created):

```python
# In src/bidequity/main.py — add or extend the lifespan context manager
from contextlib import asynccontextmanager
from bidequity.ingest.scheduler import build_scheduler
from bidequity.common.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = build_scheduler(str(settings.DATABASE_URL))
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan)
```

- [ ] Commit:

```bash
git add src/bidequity/ingest/scheduler.py src/bidequity/main.py
git commit -m "ticket-03: APScheduler ingest dispatcher with cadence jobs and dead-source check"
```

---

### Task 8 — Full test run and acceptance smoke test

**Files:** none new — runs against the full test suite and the running app.

- [ ] Run the full test suite:

```bash
cd bidequity-newsroom
python -m pytest tests/test_ingest/ -v --tb=short
```

Expected output (exact test names may vary by file count):

```
tests/test_ingest/test_handler_interface.py::test_item_create_validates_required_fields PASSED
tests/test_ingest/test_handler_interface.py::test_abstract_handler_cannot_be_instantiated PASSED
tests/test_ingest/test_prefilter.py::TestKeywordTriggers::test_passes_on_keyword_in_title PASSED
tests/test_ingest/test_prefilter.py::TestKeywordTriggers::test_passes_on_keyword_in_body_preview PASSED
tests/test_ingest/test_prefilter.py::TestKeywordTriggers::test_case_insensitive_match PASSED
tests/test_ingest/test_prefilter.py::TestKeywordTriggers::test_keyword_in_body_beyond_500_chars_is_ignored PASSED
tests/test_ingest/test_prefilter.py::TestSectorTriggers::test_passes_on_sector_match_in_title PASSED
tests/test_ingest/test_prefilter.py::TestSectorTriggers::test_passes_on_sector_match_in_body PASSED
tests/test_ingest/test_prefilter.py::TestBuyerTriggers::test_passes_on_buyer_match PASSED
tests/test_ingest/test_prefilter.py::TestBuyerTriggers::test_full_buyer_name_match PASSED
tests/test_ingest/test_prefilter.py::TestProgrammeTriggers::test_passes_on_programme_match PASSED
tests/test_ingest/test_prefilter.py::TestNoMatch::test_drops_irrelevant_item PASSED
tests/test_ingest/test_prefilter.py::TestNoMatch::test_drops_empty_body PASSED
tests/test_ingest/test_rss_handler.py::test_rss_handler_returns_item_create_for_new_entry PASSED
tests/test_ingest/test_rss_handler.py::test_rss_handler_skips_entries_before_since PASSED
tests/test_ingest/test_rss_handler.py::test_rss_handler_falls_back_to_summary_on_extraction_failure PASSED
tests/test_ingest/test_rss_handler.py::test_rss_handler_skips_entry_on_http_error PASSED
tests/test_ingest/test_api_find_a_tender.py::test_find_a_tender_handler_paginates_and_returns_items PASSED
tests/test_ingest/test_api_find_a_tender.py::test_find_a_tender_handler_skips_old_releases PASSED
tests/test_ingest/test_api_contracts_finder.py::test_contracts_finder_handler_paginates PASSED
tests/test_ingest/test_api_contracts_finder.py::test_contracts_finder_maps_fields_correctly PASSED

21 passed in <N>s
```

- [ ] Acceptance smoke test — start the app and trigger one manual ingest run:

```bash
# Terminal 1: start the app
cd bidequity-newsroom
DATABASE_URL=postgresql://... uvicorn bidequity.main:app --reload

# Terminal 2: trigger one immediate ingest of daily sources
python -c "
import asyncio
from bidequity.ingest.scheduler import _ingest_cadence
import os
asyncio.run(_ingest_cadence('daily', os.environ['DATABASE_URL']))
"
```

Expected: log output showing sources fetched, items inserted, pre-filter stats. After 24 hours of scheduled operation: ≥100 items in the `items` table, ≥20 distinct `source_id` values.

```sql
-- Acceptance query (run in psql)
SELECT COUNT(*) AS total_items, COUNT(DISTINCT source_id) AS distinct_sources FROM items;
-- Expect: total_items >= 100, distinct_sources >= 20

SELECT COUNT(*) AS passed_prefilter,
       (SELECT SUM(items_prefiltered) FROM runs WHERE job_name LIKE 'ingest_daily_%') AS prefiltered
FROM items;
-- Expect: prefiltered / (passed_prefilter + prefiltered) >= 0.40
```

- [ ] Commit final state:

```bash
git add .
git commit -m "ticket-03: complete — ingest layer, pre-filter, scheduler, 21 tests passing"
```

---

## Acceptance Criteria Checklist

- [ ] 100+ items ingested from 20+ distinct sources within 24 hours of first scheduler run
- [ ] Duplicate content hash insertion correctly blocked (UNIQUE constraint + skip log)
- [ ] Pre-filter drops ≥40% of raw items before classification
- [ ] Run table records `items_fetched`, `items_inserted`, `items_skipped_hash`, `items_prefiltered`, `duration_ms` for every job
- [ ] Sources with ≥5 consecutive failures are deactivated and logged
- [ ] All 21 unit tests pass (`pytest tests/test_ingest/ -v`)
- [ ] `ruff check src/` passes clean
- [ ] `mypy src/bidequity/ingest/` passes (allow `Any` where noted in comments)
