# BidEquity Newsroom — Ticket 2: Data Model & Seed Data

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Define and migrate the full PostgreSQL schema for the BidEquity content intelligence platform, seed the sources table from CSV, and verify all models and relationships with a passing test suite.

**Architecture:** SQLModel models live in `bidequity-newsroom/src/bidequity/models/` and map 1:1 to the tables defined in spec sections 4.2–4.9. Alembic handles migration; one initial migration creates all tables, extensions, and indexes in a single atomic operation. A standalone seed script reads `config/sources_seed.csv` and upserts rows so the sources table is always reproducible from source control.

**Tech Stack:** SQLModel, PostgreSQL 16 + pgvector, Alembic, pytest

---

## File Map

```
bidequity-newsroom/
├── src/bidequity/models/
│   ├── __init__.py                  # re-exports all models + metadata
│   ├── source.py                    # Source table
│   ├── item.py                      # Item table (with pgvector embedding column)
│   ├── classification.py            # Classification table
│   ├── cluster.py                   # Cluster table
│   ├── draft.py                     # Draft table
│   ├── publication.py               # Publication table
│   ├── metrics.py                   # Metrics table
│   └── editorial.py                 # EditorialAction table
├── alembic/
│   └── versions/
│       └── 0001_initial_schema.py   # Creates all tables, pgvector, and indexes
├── config/
│   └── sources_seed.csv             # 5 seed rows covering all feed_type variants
├── scripts/
│   └── seed_sources.py              # Reads CSV and upserts into sources table
└── tests/
    └── test_models.py               # Model creation, FK resolution, unique constraint, defaults
```

---

## Tasks

### Task 1: Write the failing tests first

**Files:**
- `bidequity-newsroom/tests/test_models.py`

TDD order: write all tests before any model code. Every test will fail at import until models exist — that's the correct starting state.

- [ ] Create `bidequity-newsroom/tests/__init__.py` (empty):

```python
```

- [ ] Create `bidequity-newsroom/tests/test_models.py`:

```python
"""
Tests for BidEquity data models.
Run with: pytest tests/test_models.py -v
Requires a running Postgres with pgvector. Set DATABASE_URL in environment.
Default: postgresql://bidequity:bidequity@localhost:5432/bidequity_test
"""
import os
from datetime import datetime, timezone

import pytest
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

# ── database URL ──────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bidequity:bidequity@localhost:5432/bidequity_test",
)


@pytest.fixture(scope="session")
def engine():
    """Create engine and build schema from SQLModel metadata for tests."""
    eng = create_engine(DATABASE_URL, echo=False)
    # pgvector extension must exist before creating the 'vector' column type
    with eng.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    SQLModel.metadata.create_all(eng)
    yield eng
    SQLModel.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s
        s.rollback()


# ── imports (fail until models are written) ───────────────────────────────────
from bidequity.models import (  # noqa: E402
    Classification,
    Cluster,
    Draft,
    EditorialAction,
    Item,
    Metrics,
    Publication,
    Source,
)


# ── Source ────────────────────────────────────────────────────────────────────

def test_source_can_be_created_and_saved(session):
    """Source row round-trips through the database."""
    src = Source(
        name="Test Blog",
        owner="Test Dept",
        category="Official Blogs",
        sector="Defence",
        url="https://example.com/blog",
        feed_url="https://example.com/blog/feed",
        feed_type="rss",
        cadence="daily",
        signal_strength="high",
        priority_score=1,
    )
    session.add(src)
    session.commit()
    session.refresh(src)

    assert src.id is not None
    assert src.active is True
    assert src.consecutive_failures == 0
    assert src.created_at is not None


def test_source_url_unique_constraint(session):
    """Two sources with the same URL raise an integrity error."""
    from sqlalchemy.exc import IntegrityError

    url = "https://example.com/unique-source"
    s1 = Source(
        name="Source A",
        category="Official Blogs",
        sector="Justice",
        url=url,
        feed_type="rss",
        cadence="daily",
        signal_strength="medium",
        priority_score=2,
    )
    s2 = Source(
        name="Source B",
        category="Official Blogs",
        sector="Justice",
        url=url,
        feed_type="rss",
        cadence="daily",
        signal_strength="medium",
        priority_score=2,
    )
    session.add(s1)
    session.commit()
    session.add(s2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


# ── Item ──────────────────────────────────────────────────────────────────────

def _make_source(session, suffix: str = "") -> Source:
    src = Source(
        name=f"Fixture Source{suffix}",
        category="Official Blogs",
        sector="Health & Social Care",
        url=f"https://fixture.example.com{suffix}",
        feed_type="rss",
        cadence="weekly",
        signal_strength="medium",
        priority_score=3,
    )
    session.add(src)
    session.commit()
    session.refresh(src)
    return src


def test_item_unique_constraint_on_content_hash(session):
    """Inserting two items with the same content_hash raises IntegrityError."""
    from sqlalchemy.exc import IntegrityError

    src = _make_source(session, "-item-dupe")
    shared_hash = "a" * 32

    i1 = Item(
        source_id=src.id,
        url="https://example.com/article-1",
        title="Article One",
        body_text="Body of article one.",
        content_hash=shared_hash,
    )
    i2 = Item(
        source_id=src.id,
        url="https://example.com/article-2",
        title="Article Two",
        body_text="Body of article two.",
        content_hash=shared_hash,
    )
    session.add(i1)
    session.commit()
    session.add(i2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_item_fk_to_source(session):
    """Item.source_id FK resolves back to the parent Source."""
    src = _make_source(session, "-item-fk")
    item = Item(
        source_id=src.id,
        url="https://example.com/fk-article",
        title="FK Article",
        body_text="Some text here.",
        content_hash="b" * 32,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    assert item.source_id == src.id
    assert item.ingested_at is not None
    assert item.language == "en"


# ── Draft ─────────────────────────────────────────────────────────────────────

def test_draft_status_defaults_to_pending(session):
    """Draft.status defaults to 'pending' without explicit assignment."""
    src = _make_source(session, "-draft")
    item = Item(
        source_id=src.id,
        url="https://example.com/draft-article",
        title="Draft Article",
        body_text="Draft body text.",
        content_hash="c" * 32,
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    draft = Draft(
        item_id=item.id,
        prompt_version="generator-v1.0",
        linkedin_post="LinkedIn post text here.",
        newsletter_para="Newsletter paragraph here.",
        so_what_line="The so-what line.",
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)

    assert draft.status == "pending"
    assert draft.generated_at is not None


# ── FK chain resolution ───────────────────────────────────────────────────────

def test_all_fk_relationships_resolve(session):
    """Full chain: Source → Item → Classification → Draft → Publication → Metrics → EditorialAction."""
    src = _make_source(session, "-chain")

    item = Item(
        source_id=src.id,
        url="https://example.com/chain-article",
        title="Chain Article",
        body_text="Full chain test.",
        content_hash="d" * 32,
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    classification = Classification(
        item_id=item.id,
        prompt_version="classifier-v1.0",
        relevance_score=8,
        signal_strength="high",
        signal_type="procurement",
        sectors=["Defence"],
        summary="A classification summary.",
    )
    session.add(classification)
    session.commit()
    session.refresh(classification)
    assert classification.item_id == item.id

    cluster = Cluster(theme="Defence Procurement Wave", item_ids=[item.id])
    session.add(cluster)
    session.commit()
    session.refresh(cluster)

    draft = Draft(
        item_id=item.id,
        cluster_id=cluster.id,
        prompt_version="generator-v1.0",
        linkedin_post="LinkedIn post.",
        newsletter_para="Newsletter para.",
        so_what_line="So what.",
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)
    assert draft.cluster_id == cluster.id

    publication = Publication(
        draft_id=draft.id,
        channel="linkedin",
        final_content="Final LinkedIn post.",
        scheduled_for=datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc),
    )
    session.add(publication)
    session.commit()
    session.refresh(publication)
    assert publication.status == "scheduled"
    assert publication.draft_id == draft.id

    metric = Metrics(
        publication_id=publication.id,
        checkpoint="24h",
        impressions=500,
        reactions=15,
    )
    session.add(metric)
    session.commit()
    session.refresh(metric)
    assert metric.publication_id == publication.id

    action = EditorialAction(
        draft_id=draft.id,
        action="approve",
    )
    session.add(action)
    session.commit()
    session.refresh(action)
    assert action.draft_id == draft.id
    assert action.created_at is not None
```

- [ ] Run tests — confirm they fail at import:

```bash
cd bidequity-newsroom
pytest tests/test_models.py -v 2>&1 | head -30
# Expected: ModuleNotFoundError or ImportError on 'from bidequity.models import ...'
```

- [ ] Commit the failing tests:

```bash
git add tests/test_models.py tests/__init__.py
git commit -m "test(models): add failing model tests for TDD — ticket 2"
```

---

### Task 2: Source model

**Files:**
- `bidequity-newsroom/src/bidequity/models/source.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/source.py`:

```python
"""Source — one row per monitored content source (RSS, API, scrape)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    __tablename__ = "sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    owner: Optional[str] = Field(default=None)
    category: str = Field(nullable=False)
    sector: str = Field(nullable=False)
    url: str = Field(nullable=False, unique=True)
    feed_url: Optional[str] = Field(default=None)
    feed_type: str = Field(nullable=False)          # 'rss' | 'api' | 'scrape_static' | 'scrape_js'
    cadence: str = Field(nullable=False)            # 'daily' | 'weekly' | 'monthly'
    signal_strength: str = Field(nullable=False)    # 'high' | 'medium' | 'low'
    priority_score: int = Field(nullable=False, sa_column_kwargs={"type_": "SMALLINT"})
    active: bool = Field(default=True, nullable=False)
    last_polled_at: Optional[datetime] = Field(default=None)
    last_success_at: Optional[datetime] = Field(default=None)
    consecutive_failures: int = Field(default=0, nullable=False)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
```

---

### Task 3: Item model

**Files:**
- `bidequity-newsroom/src/bidequity/models/item.py`

The `embedding` column uses `pgvector`'s `VECTOR(1024)` type. SQLModel does not natively know this type, so we declare it via `sa_column` with `sqlalchemy`'s `Column` + `pgvector.sqlalchemy.Vector`.

- [ ] Create `bidequity-newsroom/src/bidequity/models/item.py`:

```python
"""Item — one row per unique piece of ingested content."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="sources.id", nullable=False)
    external_id: Optional[str] = Field(default=None)
    url: str = Field(nullable=False)
    title: str = Field(nullable=False)
    author: Optional[str] = Field(default=None)
    body_text: str = Field(nullable=False)
    body_preview: Optional[str] = Field(default=None)
    # CHAR(32) UNIQUE — MD5 of normalised body text
    content_hash: str = Field(
        nullable=False,
        unique=True,
        sa_column_kwargs={"type_": "CHAR(32)"},
    )
    # VECTOR(1024) — voyage-3-lite or equivalent; nullable until embedding job runs
    embedding: Optional[Any] = Field(
        default=None,
        sa_column=Column(Vector(1024), nullable=True),
    )
    published_at: Optional[datetime] = Field(default=None)
    ingested_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
    language: str = Field(default="en", nullable=False)
    raw_metadata: Optional[Any] = Field(
        default=None,
        sa_column_kwargs={"type_": "JSONB"},
    )
```

---

### Task 4: Classification model

**Files:**
- `bidequity-newsroom/src/bidequity/models/classification.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/classification.py`:

```python
"""Classification — Claude Haiku's structured assessment of each item."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, TEXT


class Classification(SQLModel, table=True):
    __tablename__ = "classifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="items.id", nullable=False)
    prompt_version: str = Field(nullable=False)
    relevance_score: int = Field(
        nullable=False,
        sa_column_kwargs={"type_": "SMALLINT"},
    )
    signal_strength: str = Field(nullable=False)    # 'high' | 'medium' | 'low'
    signal_type: str = Field(nullable=False)        # 'procurement' | 'policy' | 'oversight' | ...
    # TEXT[] columns — declared via sa_column to use Postgres native arrays
    sectors: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(TEXT), nullable=False),
    )
    buyers_mentioned: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(TEXT), nullable=True),
    )
    suppliers_mentioned: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(TEXT), nullable=True),
    )
    programmes_mentioned: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(TEXT), nullable=True),
    )
    summary: str = Field(nullable=False)
    pursuit_implication: Optional[str] = Field(default=None)
    content_angle_hook: Optional[str] = Field(default=None)
    cost_usd: Optional[float] = Field(
        default=None,
        sa_column_kwargs={"type_": "NUMERIC(10,6)"},
    )
    latency_ms: Optional[int] = Field(default=None)
    classified_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
```

---

### Task 5: Cluster model

**Files:**
- `bidequity-newsroom/src/bidequity/models/cluster.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/cluster.py`:

```python
"""Cluster — groups of related items covering the same story or programme."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT
from sqlmodel import Field, SQLModel


class Cluster(SQLModel, table=True):
    __tablename__ = "clusters"

    id: Optional[int] = Field(default=None, primary_key=True)
    theme: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
    # BIGINT[] — list of item IDs belonging to this cluster
    item_ids: List[int] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(BIGINT), nullable=False),
    )
```

---

### Task 6: Draft model

**Files:**
- `bidequity-newsroom/src/bidequity/models/draft.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/draft.py`:

```python
"""Draft — generated content ready for editorial review."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlmodel import Field, SQLModel


class Draft(SQLModel, table=True):
    __tablename__ = "drafts"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="items.id", nullable=False)
    cluster_id: Optional[int] = Field(
        default=None,
        foreign_key="clusters.id",
        nullable=True,
    )
    prompt_version: str = Field(nullable=False)
    linkedin_post: str = Field(nullable=False)
    newsletter_para: str = Field(nullable=False)
    so_what_line: str = Field(nullable=False)
    # JSONB array of supporting point strings
    supporting_points: Optional[Any] = Field(
        default=None,
        sa_column_kwargs={"type_": "JSONB"},
    )
    cost_usd: Optional[float] = Field(
        default=None,
        sa_column_kwargs={"type_": "NUMERIC(10,6)"},
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
    # 'pending' | 'approved' | 'edited' | 'rejected' | 'saved'
    status: str = Field(default="pending", nullable=False)
```

---

### Task 7: Publication model

**Files:**
- `bidequity-newsroom/src/bidequity/models/publication.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/publication.py`:

```python
"""Publication — approved drafts that have been or will be published."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Publication(SQLModel, table=True):
    __tablename__ = "publications"

    id: Optional[int] = Field(default=None, primary_key=True)
    draft_id: int = Field(foreign_key="drafts.id", nullable=False)
    channel: str = Field(nullable=False)        # 'linkedin' | 'newsletter'
    final_content: str = Field(nullable=False)
    scheduled_for: datetime = Field(nullable=False)
    published_at: Optional[datetime] = Field(default=None)
    external_id: Optional[str] = Field(default=None)   # LinkedIn URN or Beehiiv post ID
    external_url: Optional[str] = Field(default=None)
    # 'scheduled' | 'published' | 'failed'
    status: str = Field(default="scheduled", nullable=False)
```

---

### Task 8: Metrics model

**Files:**
- `bidequity-newsroom/src/bidequity/models/metrics.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/metrics.py`:

```python
"""Metrics — engagement data pulled post-publication at 24h, 72h, and 7d."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlmodel import Field, SQLModel


class Metrics(SQLModel, table=True):
    __tablename__ = "metrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    publication_id: int = Field(foreign_key="publications.id", nullable=False)
    measured_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
    checkpoint: str = Field(nullable=False)     # '24h' | '72h' | '7d'
    impressions: Optional[int] = Field(default=None)
    reactions: Optional[int] = Field(default=None)
    comments: Optional[int] = Field(default=None)
    shares: Optional[int] = Field(default=None)
    clicks: Optional[int] = Field(default=None)     # newsletter
    opens: Optional[int] = Field(default=None)      # newsletter
    raw_response: Optional[Any] = Field(
        default=None,
        sa_column_kwargs={"type_": "JSONB"},
    )
```

---

### Task 9: EditorialAction model

**Files:**
- `bidequity-newsroom/src/bidequity/models/editorial.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/editorial.py`:

```python
"""EditorialAction — append-only log of every editorial decision."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EditorialAction(SQLModel, table=True):
    __tablename__ = "editorial_actions"

    id: Optional[int] = Field(default=None, primary_key=True)
    draft_id: int = Field(foreign_key="drafts.id", nullable=False)
    # 'approve' | 'edit' | 'reject' | 'save'
    action: str = Field(nullable=False)
    original_text: Optional[str] = Field(default=None)
    edited_text: Optional[str] = Field(default=None)
    reason: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
```

---

### Task 10: Models `__init__.py`

**Files:**
- `bidequity-newsroom/src/bidequity/models/__init__.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/__init__.py`:

```python
"""
bidequity.models
~~~~~~~~~~~~~~~~
Re-exports all SQLModel table classes and the shared SQLModel metadata.
Import everything from here, not from the individual modules.
"""
from sqlmodel import SQLModel

from .classification import Classification
from .cluster import Cluster
from .draft import Draft
from .editorial import EditorialAction
from .item import Item
from .metrics import Metrics
from .publication import Publication
from .source import Source

__all__ = [
    "SQLModel",
    "Source",
    "Item",
    "Classification",
    "Cluster",
    "Draft",
    "Publication",
    "Metrics",
    "EditorialAction",
]
```

- [ ] Run tests — confirm they now import and pass (database must be reachable):

```bash
cd bidequity-newsroom
pytest tests/test_models.py -v
# Expected: all 6 tests pass
```

Expected output:
```
tests/test_models.py::test_source_can_be_created_and_saved PASSED
tests/test_models.py::test_source_url_unique_constraint PASSED
tests/test_models.py::test_item_unique_constraint_on_content_hash PASSED
tests/test_models.py::test_item_fk_to_source PASSED
tests/test_models.py::test_draft_status_defaults_to_pending PASSED
tests/test_models.py::test_all_fk_relationships_resolve PASSED

6 passed
```

- [ ] Commit models:

```bash
git add src/bidequity/models/
git commit -m "feat(models): add SQLModel table definitions for all 8 core tables — ticket 2"
```

---

### Task 11: Alembic initial migration

**Files:**
- `bidequity-newsroom/alembic/versions/0001_initial_schema.py`

This migration is hand-authored (not `alembic revision --autogenerate`) so that it explicitly creates the pgvector extension, all indexes from the spec, and uses native Postgres column types where they matter (VECTOR, SMALLINT, CHAR, BIGINT[], TEXT[], JSONB).

- [ ] Create `bidequity-newsroom/alembic/versions/0001_initial_schema.py`:

```python
"""Initial schema — all tables, pgvector extension, and indexes.

Revision ID: 0001
Revises: (none)
Create Date: 2026-04-18
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── pgvector extension ────────────────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── sources ───────────────────────────────────────────────────────────────
    op.create_table(
        "sources",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("owner", sa.Text, nullable=True),
        sa.Column("category", sa.Text, nullable=False),
        sa.Column("sector", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=False, unique=True),
        sa.Column("feed_url", sa.Text, nullable=True),
        sa.Column("feed_type", sa.Text, nullable=False),
        sa.Column("cadence", sa.Text, nullable=False),
        sa.Column("signal_strength", sa.Text, nullable=False),
        sa.Column("priority_score", sa.SmallInteger, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_polled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consecutive_failures", sa.Integer, nullable=False, server_default="0"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── items ─────────────────────────────────────────────────────────────────
    op.create_table(
        "items",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "source_id",
            sa.BigInteger,
            sa.ForeignKey("sources.id"),
            nullable=False,
        ),
        sa.Column("external_id", sa.Text, nullable=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("author", sa.Text, nullable=True),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("body_preview", sa.Text, nullable=True),
        sa.Column("content_hash", sa.CHAR(32), nullable=False, unique=True),
        # VECTOR(1024) via raw DDL — Alembic does not natively type pgvector
        sa.Column("embedding", sa.Text, nullable=True),  # placeholder, overridden below
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("language", sa.Text, nullable=False, server_default="en"),
        sa.Column("raw_metadata", postgresql.JSONB, nullable=True),
    )
    # Replace placeholder 'embedding' column with proper VECTOR(1024) type
    op.execute("ALTER TABLE items DROP COLUMN embedding")
    op.execute("ALTER TABLE items ADD COLUMN embedding vector(1024)")

    # ── clusters (created before drafts because drafts FK to clusters) ────────
    op.create_table(
        "clusters",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("theme", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("item_ids", postgresql.ARRAY(sa.BigInteger), nullable=False),
    )

    # ── classifications ───────────────────────────────────────────────────────
    op.create_table(
        "classifications",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "item_id",
            sa.BigInteger,
            sa.ForeignKey("items.id"),
            nullable=False,
        ),
        sa.Column("prompt_version", sa.Text, nullable=False),
        sa.Column("relevance_score", sa.SmallInteger, nullable=False),
        sa.Column("signal_strength", sa.Text, nullable=False),
        sa.Column("signal_type", sa.Text, nullable=False),
        sa.Column("sectors", postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column("buyers_mentioned", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("suppliers_mentioned", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("programmes_mentioned", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("pursuit_implication", sa.Text, nullable=True),
        sa.Column("content_angle_hook", sa.Text, nullable=True),
        sa.Column("cost_usd", sa.Numeric(10, 6), nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column(
            "classified_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── drafts ────────────────────────────────────────────────────────────────
    op.create_table(
        "drafts",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "item_id",
            sa.BigInteger,
            sa.ForeignKey("items.id"),
            nullable=False,
        ),
        sa.Column(
            "cluster_id",
            sa.BigInteger,
            sa.ForeignKey("clusters.id"),
            nullable=True,
        ),
        sa.Column("prompt_version", sa.Text, nullable=False),
        sa.Column("linkedin_post", sa.Text, nullable=False),
        sa.Column("newsletter_para", sa.Text, nullable=False),
        sa.Column("so_what_line", sa.Text, nullable=False),
        sa.Column("supporting_points", postgresql.JSONB, nullable=True),
        sa.Column("cost_usd", sa.Numeric(10, 6), nullable=True),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("status", sa.Text, nullable=False, server_default="pending"),
    )

    # ── publications ──────────────────────────────────────────────────────────
    op.create_table(
        "publications",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "draft_id",
            sa.BigInteger,
            sa.ForeignKey("drafts.id"),
            nullable=False,
        ),
        sa.Column("channel", sa.Text, nullable=False),
        sa.Column("final_content", sa.Text, nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_id", sa.Text, nullable=True),
        sa.Column("external_url", sa.Text, nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default="scheduled"),
    )

    # ── metrics ───────────────────────────────────────────────────────────────
    op.create_table(
        "metrics",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "publication_id",
            sa.BigInteger,
            sa.ForeignKey("publications.id"),
            nullable=False,
        ),
        sa.Column(
            "measured_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("checkpoint", sa.Text, nullable=False),
        sa.Column("impressions", sa.Integer, nullable=True),
        sa.Column("reactions", sa.Integer, nullable=True),
        sa.Column("comments", sa.Integer, nullable=True),
        sa.Column("shares", sa.Integer, nullable=True),
        sa.Column("clicks", sa.Integer, nullable=True),
        sa.Column("opens", sa.Integer, nullable=True),
        sa.Column("raw_response", postgresql.JSONB, nullable=True),
    )

    # ── editorial_actions ─────────────────────────────────────────────────────
    op.create_table(
        "editorial_actions",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "draft_id",
            sa.BigInteger,
            sa.ForeignKey("drafts.id"),
            nullable=False,
        ),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("original_text", sa.Text, nullable=True),
        sa.Column("edited_text", sa.Text, nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── indexes (from spec section 4.3 and 4.4) ───────────────────────────────
    # IVFFlat for vector similarity search — requires rows to exist for training;
    # in production, run AFTER initial data load. Safe on empty table at migration time.
    op.execute(
        "CREATE INDEX idx_items_embedding ON items "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
    op.create_index("idx_items_published_at", "items", [sa.text("published_at DESC")])
    op.create_index("idx_items_source_id", "items", ["source_id"])
    op.create_index("idx_class_item_id", "classifications", ["item_id"])
    op.create_index(
        "idx_class_relevance",
        "classifications",
        [sa.text("relevance_score DESC")],
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("editorial_actions")
    op.drop_table("metrics")
    op.drop_table("publications")
    op.drop_table("drafts")
    op.drop_table("classifications")
    op.drop_table("clusters")
    op.drop_table("items")
    op.drop_table("sources")
    op.execute("DROP EXTENSION IF EXISTS vector")
```

- [ ] Run migration against the development database:

```bash
cd bidequity-newsroom
alembic upgrade head
# Expected output (no errors):
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> 0001, Initial schema
```

- [ ] Verify tables exist:

```bash
psql $DATABASE_URL -c "\dt"
# Expected: sources, items, clusters, classifications, drafts, publications, metrics, editorial_actions
```

- [ ] Verify the vector column and indexes:

```bash
psql $DATABASE_URL -c "\d items" | grep -E "embedding|vector"
psql $DATABASE_URL -c "SELECT indexname FROM pg_indexes WHERE tablename IN ('items','classifications') ORDER BY indexname;"
# Expected indexes: idx_class_item_id, idx_class_relevance, idx_items_embedding, idx_items_published_at, idx_items_source_id
```

- [ ] Test migration rollback:

```bash
alembic downgrade base
alembic upgrade head
# Both commands must succeed cleanly
```

- [ ] Commit migration:

```bash
git add alembic/versions/0001_initial_schema.py
git commit -m "feat(migrations): initial schema — all tables, pgvector, and indexes"
```

---

### Task 12: Seed CSV

**Files:**
- `bidequity-newsroom/config/sources_seed.csv`

Five rows are enough for tests and local dev. The full 120-source register is added by the operator after Ticket 1 infrastructure is live.

- [ ] Create `bidequity-newsroom/config/sources_seed.csv`:

```csv
name,owner,category,sector,url,feed_url,feed_type,cadence,signal_strength,priority_score
GOV.UK Policy Blog,Cabinet Office,Official Blogs,Central Gov & Cabinet Office,https://www.gov.uk/search/policy-papers-and-consultations,https://www.gov.uk/search/policy-papers-and-consultations.atom,rss,daily,high,1
Find a Tender Service,Crown Commercial Service,Procurement Portals,Central Gov & Cabinet Office,https://www.find-a-tender.service.gov.uk,https://www.find-a-tender.service.gov.uk/api/1.0/releases,api,daily,high,1
NHS England News,NHS England,Official Blogs,Health & Social Care,https://www.england.nhs.uk/news,https://www.england.nhs.uk/feed,rss,daily,high,2
PublicTechnology.net,Incisive Media,Trade Press,Central Gov & Cabinet Office,https://www.publictechnology.net,,scrape_static,daily,medium,2
Defence Equipment & Support,Ministry of Defence,Official Blogs,Defence,https://des.mod.uk,,scrape_js,weekly,medium,3
```

---

### Task 13: Seed script

**Files:**
- `bidequity-newsroom/scripts/seed_sources.py`

- [ ] Create `bidequity-newsroom/scripts/seed_sources.py`:

```python
"""
Seed the sources table from config/sources_seed.csv.

Usage:
    python scripts/seed_sources.py [--csv path/to/sources_seed.csv]

The script is idempotent: it upserts on the unique `url` column.
Running it twice with the same CSV produces the same database state.

Environment variable DATABASE_URL must be set, or fall back to the
default local dev connection string.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

# Allow running from repo root or from scripts/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from bidequity.models import Source  # noqa: E402

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bidequity:bidequity@localhost:5432/bidequity",
)

DEFAULT_CSV = ROOT / "config" / "sources_seed.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed sources table from CSV.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help=f"Path to sources CSV (default: {DEFAULT_CSV})",
    )
    return parser.parse_args()


def upsert_source(session: Session, row: dict) -> tuple[str, str]:
    """Insert or update a source row. Returns (url, action)."""
    existing = session.exec(
        # Use raw SQL for the upsert to avoid SQLModel's lack of ON CONFLICT support
        text("SELECT id FROM sources WHERE url = :url"),
        params={"url": row["url"]},
    ).fetchone()

    now = datetime.utcnow()
    if existing:
        session.exec(
            text(
                """
                UPDATE sources SET
                    name = :name,
                    owner = :owner,
                    category = :category,
                    sector = :sector,
                    feed_url = :feed_url,
                    feed_type = :feed_type,
                    cadence = :cadence,
                    signal_strength = :signal_strength,
                    priority_score = :priority_score,
                    updated_at = :updated_at
                WHERE url = :url
                """
            ),
            params={**row, "updated_at": now},
        )
        return row["url"], "updated"
    else:
        source = Source(
            name=row["name"],
            owner=row.get("owner") or None,
            category=row["category"],
            sector=row["sector"],
            url=row["url"],
            feed_url=row.get("feed_url") or None,
            feed_type=row["feed_type"],
            cadence=row["cadence"],
            signal_strength=row["signal_strength"],
            priority_score=int(row["priority_score"]),
        )
        session.add(source)
        return row["url"], "inserted"


def main() -> None:
    args = parse_args()
    csv_path: Path = args.csv

    if not csv_path.exists():
        print(f"ERROR: CSV not found at {csv_path}", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(DATABASE_URL, echo=False)

    inserted = 0
    updated = 0
    errors = 0

    with Session(engine) as session:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    url, action = upsert_source(session, row)
                    if action == "inserted":
                        inserted += 1
                    else:
                        updated += 1
                    print(f"  [{action}] {row['name']} ({url})")
                except Exception as exc:
                    print(f"  [error] {row.get('name', '?')}: {exc}", file=sys.stderr)
                    errors += 1
                    session.rollback()
                    continue
        session.commit()

    print(
        f"\nDone. {inserted} inserted, {updated} updated, {errors} errors."
    )
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] Run the seed script against the local database:

```bash
cd bidequity-newsroom
python scripts/seed_sources.py
# Expected output:
#   [inserted] GOV.UK Policy Blog (https://www.gov.uk/...)
#   [inserted] Find a Tender Service (https://www.find-a-tender.service.gov.uk)
#   [inserted] NHS England News (https://www.england.nhs.uk/news)
#   [inserted] PublicTechnology.net (https://www.publictechnology.net)
#   [inserted] Defence Equipment & Support (https://des.mod.uk)
#
# Done. 5 inserted, 0 updated, 0 errors.
```

- [ ] Run again to verify idempotency:

```bash
python scripts/seed_sources.py
# Expected: 0 inserted, 5 updated, 0 errors
```

- [ ] Verify rows in database:

```bash
psql $DATABASE_URL -c "SELECT name, sector, feed_type, active FROM sources ORDER BY id;"
# Expected: 5 rows, all active=true, matching feed_type variants
```

- [ ] Commit seed files:

```bash
git add config/sources_seed.csv scripts/seed_sources.py
git commit -m "feat(seed): sources_seed.csv with 5 representative rows and seed_sources.py upsert script"
```

---

### Task 14: Final test run and acceptance check

**Files:** (none new — verification only)

- [ ] Run the full test suite against the seeded database:

```bash
cd bidequity-newsroom
pytest tests/test_models.py -v
# Expected: 6 passed, 0 failed
```

- [ ] Verify acceptance criteria from spec section 12.3:

```bash
# 1. Database contains seeded sources with correct tier classifications
psql $DATABASE_URL -c \
  "SELECT name, sector, signal_strength, priority_score FROM sources ORDER BY priority_score, name;"

# 2. Sources list query (as the dashboard route will use)
psql $DATABASE_URL -c \
  "SELECT id, name, sector, feed_type, active, consecutive_failures FROM sources WHERE active = true;"
```

- [ ] Confirm migration is idempotent (no pending migrations):

```bash
alembic current
# Expected: 0001 (head)
```

- [ ] Final commit tagging ticket completion:

```bash
git add .
git commit -m "feat(ticket-02): data model and seed data complete — all tables, migration, seed CSV, seed script, tests passing"
```

---

## Dependency Notes

- **pgvector Python package** (`pip install pgvector`) must be installed before running the Item model or migration. Add to `pyproject.toml` under `[project.dependencies]`.
- **IVFFlat index note**: The `idx_items_embedding` index uses `lists = 100` (suitable for tables up to ~1M rows). On a fresh empty table this is valid but the index will not be usable until at least `lists * 39 = 3,900` rows exist. That is expected — the embedding index is only needed at Ticket 4 volume.
- **Alembic `env.py`** must import `bidequity.models` so that `SQLModel.metadata` is populated before `autogenerate` runs. If the migration is hand-authored (as it is here), this is not strictly required, but it is good practice to ensure future `--autogenerate` commands work.
- **Test database**: the test fixture creates and drops schema on every `session` scope run. A dedicated `bidequity_test` database avoids clobbering the development database. Set `DATABASE_URL=postgresql://bidequity:bidequity@localhost:5432/bidequity_test` in `.env.test`.
