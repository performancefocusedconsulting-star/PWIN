# BidEquity Newsroom — Ticket 7: Editorial Dashboard

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full editorial dashboard — Inbox, Scheduled, Published, Sources, and Insights views with HTMX-powered inline actions, keyboard shortcuts, an editorial-actions audit log, and a Sunday digest email — so Paul can triage 20 items in under 10 minutes from any device.

**Architecture:** Server-rendered FastAPI routes return Jinja2 HTML fragments; HTMX swaps individual table rows in-place on approve/reject/edit/save so the page never fully reloads. AlpineJS handles the keyboard shortcut state machine and modal visibility entirely in the browser without a build step. Pico.css provides responsive base styling with BidEquity palette overrides in a single `<style>` block in `base.html`. All editorial state (status, action log) lives in PostgreSQL; no client-side state persists beyond the current page.

**Tech Stack:** FastAPI, Jinja2, HTMX, Pico.css, AlpineJS, pytest

**Prerequisite:** Tickets 1–6 must be complete. The `drafts`, `publications`, `metrics`, `editorial_actions`, and `sources` tables must exist (Ticket 2 migration). Draft rows with `status='pending'` must be present (Ticket 6 generator output).

---

## File Map

```
bidequity-newsroom/
├── src/bidequity/dashboard/
│   ├── __init__.py                        # package marker
│   ├── routes.py                          # all dashboard FastAPI routes
│   ├── digest.py                          # Sunday digest email sender (APScheduler)
│   └── templates/
│       ├── base.html                      # CDN imports, nav, AlpineJS keyboard handler
│       ├── inbox.html                     # extends base; draft triage table
│       ├── _draft_row.html                # HTMX partial: single draft row
│       ├── _draft_row_approved.html       # HTMX partial: approved state row (greyed, no actions)
│       ├── _draft_row_rejected.html       # HTMX partial: rejected state row (struck, no actions)
│       ├── _edit_modal.html               # HTMX partial: edit modal injected into row
│       ├── scheduled.html                 # extends base; scheduled publications table
│       ├── _publication_row.html          # HTMX partial: single scheduled publication row
│       ├── published.html                 # extends base; published history with metrics
│       ├── sources.html                   # extends base; source health and toggle table
│       ├── _source_row.html               # HTMX partial: single source row
│       └── insights.html                  # extends base; aggregate analytics
└── tests/test_dashboard/
    ├── __init__.py                        # package marker
    ├── conftest.py                        # TestClient, test DB session, seed fixtures
    └── test_routes.py                     # route-level tests with FastAPI TestClient
```

---

## Tasks

### Task 1 — Write the failing route tests (TDD anchor)

> TDD: the tests must exist and fail before any routes are written.

**Files:** `bidequity-newsroom/tests/test_dashboard/__init__.py`, `bidequity-newsroom/tests/test_dashboard/conftest.py`, `bidequity-newsroom/tests/test_dashboard/test_routes.py`

- [ ] Create `bidequity-newsroom/tests/test_dashboard/__init__.py` (empty).

- [ ] Create `bidequity-newsroom/tests/test_dashboard/conftest.py`:

```python
"""Shared fixtures for dashboard route tests."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from bidequity.main import app
from bidequity.models.source import Source
from bidequity.models.item import Item
from bidequity.models.classification import Classification
from bidequity.models.draft import Draft
from bidequity.models.publication import Publication
from bidequity.models.editorial_action import EditorialAction
from bidequity.common.db import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, follow_redirects=True)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="seed_source")
def seed_source_fixture(session: Session) -> Source:
    source = Source(
        name="GOV.UK Blog",
        category="Official Blogs",
        sector="Central Gov & Cabinet Office",
        url="https://example.gov.uk/blog",
        feed_type="rss",
        cadence="daily",
        signal_strength="high",
        priority_score=8,
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@pytest.fixture(name="seed_draft")
def seed_draft_fixture(session: Session, seed_source: Source) -> Draft:
    item = Item(
        source_id=seed_source.id,
        url="https://example.gov.uk/blog/post-1",
        title="New NHS digital procurement framework announced",
        body_text="The NHS has announced a new digital procurement framework...",
        content_hash="abc123def456abc123def456abc123de",
        language="en",
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
        sectors=["Health & Social Care"],
        summary="NHS digital procurement framework announced, significant for tech suppliers.",
        pursuit_implication="Suppliers on Crown Commercial Service frameworks should monitor award notices.",
    )
    session.add(classification)
    session.commit()

    draft = Draft(
        item_id=item.id,
        prompt_version="generator-v1.0",
        linkedin_post="The NHS just announced a new digital procurement framework.\n\nHere is what this means for bid teams...",
        newsletter_para="NHS Digital has released a new procurement framework covering digital services across all trusts.",
        so_what_line="Tech suppliers should register on the framework within 30 days or miss the window.",
        status="pending",
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft
```

- [ ] Create `bidequity-newsroom/tests/test_dashboard/test_routes.py`:

```python
"""Tests for editorial dashboard routes."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from bidequity.models.draft import Draft
from bidequity.models.editorial_action import EditorialAction


# ---------------------------------------------------------------------------
# GET /inbox
# ---------------------------------------------------------------------------

def test_inbox_returns_200(client: TestClient, seed_draft: Draft) -> None:
    response = client.get("/inbox")
    assert response.status_code == 200


def test_inbox_renders_draft_title(client: TestClient, seed_draft: Draft) -> None:
    response = client.get("/inbox")
    assert "NHS digital procurement framework" in response.text


def test_inbox_renders_so_what_line(client: TestClient, seed_draft: Draft) -> None:
    response = client.get("/inbox")
    assert "register on the framework" in response.text


def test_inbox_renders_action_buttons(client: TestClient, seed_draft: Draft) -> None:
    response = client.get("/inbox")
    assert 'data-action="approve"' in response.text
    assert 'data-action="reject"' in response.text
    assert 'data-action="edit"' in response.text
    assert 'data-action="save"' in response.text


def test_inbox_keyboard_shortcut_attributes_present(client: TestClient, seed_draft: Draft) -> None:
    """AlpineJS keyboard handler requires x-data and @keydown on the container."""
    response = client.get("/inbox")
    assert "x-data" in response.text
    assert "@keydown" in response.text or "x-on:keydown" in response.text


def test_root_redirects_to_inbox(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200  # follow_redirects=True
    assert "/inbox" in str(response.url)


# ---------------------------------------------------------------------------
# POST /drafts/{id}/approve
# ---------------------------------------------------------------------------

def test_approve_sets_status_approved(
    client: TestClient, session: Session, seed_draft: Draft
) -> None:
    response = client.post(f"/drafts/{seed_draft.id}/approve")
    assert response.status_code == 200
    session.refresh(seed_draft)
    assert seed_draft.status == "approved"


def test_approve_creates_editorial_action(
    client: TestClient, session: Session, seed_draft: Draft
) -> None:
    client.post(f"/drafts/{seed_draft.id}/approve")
    actions = session.exec(
        select(EditorialAction).where(EditorialAction.draft_id == seed_draft.id)
    ).all()
    assert len(actions) == 1
    assert actions[0].action == "approve"


def test_approve_returns_html_fragment_with_approved_class(
    client: TestClient, seed_draft: Draft
) -> None:
    response = client.post(f"/drafts/{seed_draft.id}/approve")
    assert response.status_code == 200
    assert "approved" in response.text
    # HTMX response is a <tr> fragment, not a full page
    assert "<html" not in response.text


def test_approve_nonexistent_draft_returns_404(client: TestClient) -> None:
    response = client.post("/drafts/99999/approve")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /drafts/{id}/reject
# ---------------------------------------------------------------------------

def test_reject_sets_status_rejected(
    client: TestClient, session: Session, seed_draft: Draft
) -> None:
    response = client.post(f"/drafts/{seed_draft.id}/reject")
    assert response.status_code == 200
    session.refresh(seed_draft)
    assert seed_draft.status == "rejected"


def test_reject_creates_editorial_action(
    client: TestClient, session: Session, seed_draft: Draft
) -> None:
    client.post(f"/drafts/{seed_draft.id}/reject")
    actions = session.exec(
        select(EditorialAction).where(EditorialAction.draft_id == seed_draft.id)
    ).all()
    assert any(a.action == "reject" for a in actions)


def test_reject_returns_html_fragment(
    client: TestClient, seed_draft: Draft
) -> None:
    response = client.post(f"/drafts/{seed_draft.id}/reject")
    assert response.status_code == 200
    assert "<html" not in response.text


# ---------------------------------------------------------------------------
# POST /drafts/{id}/edit
# ---------------------------------------------------------------------------

def test_edit_sets_status_edited_and_persists_text(
    client: TestClient, session: Session, seed_draft: Draft
) -> None:
    new_post = "Edited LinkedIn post content for the NHS framework story."
    new_para = "Edited newsletter paragraph."
    response = client.post(
        f"/drafts/{seed_draft.id}/edit",
        data={"linkedin_post": new_post, "newsletter_para": new_para},
    )
    assert response.status_code == 200
    session.refresh(seed_draft)
    assert seed_draft.status == "edited"
    assert seed_draft.linkedin_post == new_post
    assert seed_draft.newsletter_para == new_para


def test_edit_creates_editorial_action_with_original_and_edited_text(
    client: TestClient, session: Session, seed_draft: Draft
) -> None:
    original_post = seed_draft.linkedin_post
    client.post(
        f"/drafts/{seed_draft.id}/edit",
        data={
            "linkedin_post": "Updated post text.",
            "newsletter_para": "Updated para.",
        },
    )
    actions = session.exec(
        select(EditorialAction).where(EditorialAction.draft_id == seed_draft.id)
    ).all()
    edit_action = next(a for a in actions if a.action == "edit")
    assert edit_action.original_text == original_post
    assert edit_action.edited_text == "Updated post text."


# ---------------------------------------------------------------------------
# POST /drafts/{id}/save
# ---------------------------------------------------------------------------

def test_save_sets_status_saved(
    client: TestClient, session: Session, seed_draft: Draft
) -> None:
    response = client.post(f"/drafts/{seed_draft.id}/save")
    assert response.status_code == 200
    session.refresh(seed_draft)
    assert seed_draft.status == "saved"


# ---------------------------------------------------------------------------
# GET /scheduled
# ---------------------------------------------------------------------------

def test_scheduled_returns_200(client: TestClient) -> None:
    response = client.get("/scheduled")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /published
# ---------------------------------------------------------------------------

def test_published_returns_200(client: TestClient) -> None:
    response = client.get("/published")
    assert response.status_code == 200


def test_published_accepts_filter_params(client: TestClient) -> None:
    response = client.get("/published?channel=linkedin&sector=Defence")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /sources
# ---------------------------------------------------------------------------

def test_sources_returns_200(client: TestClient, seed_source) -> None:
    response = client.get("/sources")
    assert response.status_code == 200
    assert "GOV.UK Blog" in response.text


# ---------------------------------------------------------------------------
# POST /sources/{id}/toggle
# ---------------------------------------------------------------------------

def test_source_toggle_flips_active(
    client: TestClient, session: Session, seed_source
) -> None:
    original = seed_source.active
    response = client.post(f"/sources/{seed_source.id}/toggle")
    assert response.status_code == 200
    session.refresh(seed_source)
    assert seed_source.active != original


# ---------------------------------------------------------------------------
# GET /insights
# ---------------------------------------------------------------------------

def test_insights_returns_200(client: TestClient) -> None:
    response = client.get("/insights")
    assert response.status_code == 200
```

- [ ] Run the tests to confirm they fail with `ModuleNotFoundError` or `404` — not with a Python syntax error:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/test_dashboard/ -v 2>&1 | head -40
```

**Commit:** `test: add failing dashboard route tests (TDD anchor for Task 2)`

---

### Task 2 — Dashboard package, models, and routes skeleton

**Files:**
- `bidequity-newsroom/src/bidequity/dashboard/__init__.py`
- `bidequity-newsroom/src/bidequity/dashboard/routes.py`
- `bidequity-newsroom/src/bidequity/models/draft.py` (extend if it exists, create if not)
- `bidequity-newsroom/src/bidequity/models/editorial_action.py`
- `bidequity-newsroom/src/bidequity/models/publication.py`
- `bidequity-newsroom/src/bidequity/models/source.py`
- `bidequity-newsroom/src/bidequity/models/item.py`
- `bidequity-newsroom/src/bidequity/models/classification.py`

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/__init__.py` (empty).

- [ ] Ensure all required SQLModel definitions exist. Create or update each model file to match the schema in spec section 4. Below are the minimal definitions needed for the dashboard:

`bidequity-newsroom/src/bidequity/models/source.py`:
```python
"""Source SQLModel."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner: Optional[str] = None
    category: str
    sector: str
    url: str = Field(unique=True)
    feed_url: Optional[str] = None
    feed_type: str
    cadence: str
    signal_strength: str
    priority_score: int
    active: bool = True
    last_polled_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    consecutive_failures: int = 0
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

`bidequity-newsroom/src/bidequity/models/item.py`:
```python
"""Item SQLModel."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="source.id")
    external_id: Optional[str] = None
    url: str
    title: str
    author: Optional[str] = None
    body_text: str
    body_preview: Optional[str] = None
    content_hash: str = Field(unique=True)
    published_at: Optional[datetime] = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    language: str = "en"
```

`bidequity-newsroom/src/bidequity/models/classification.py`:
```python
"""Classification SQLModel."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlmodel import Field, SQLModel


class Classification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    prompt_version: str
    relevance_score: int
    signal_strength: str
    signal_type: str
    sectors: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(TEXT)))
    buyers_mentioned: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(TEXT)))
    suppliers_mentioned: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(TEXT)))
    programmes_mentioned: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(TEXT)))
    summary: str
    pursuit_implication: Optional[str] = None
    content_angle_hook: Optional[str] = None
    cost_usd: Optional[float] = None
    latency_ms: Optional[int] = None
    classified_at: datetime = Field(default_factory=datetime.utcnow)
```

`bidequity-newsroom/src/bidequity/models/draft.py`:
```python
"""Draft SQLModel."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Draft(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    cluster_id: Optional[int] = None
    prompt_version: str
    linkedin_post: str
    newsletter_para: str
    so_what_line: str
    cost_usd: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"   # 'pending' | 'approved' | 'edited' | 'rejected' | 'saved'
```

`bidequity-newsroom/src/bidequity/models/publication.py`:
```python
"""Publication SQLModel."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Publication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    draft_id: int = Field(foreign_key="draft.id")
    channel: str           # 'linkedin' | 'newsletter'
    final_content: str
    scheduled_for: datetime
    published_at: Optional[datetime] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    status: str = "scheduled"   # 'scheduled' | 'published' | 'failed'
```

`bidequity-newsroom/src/bidequity/models/editorial_action.py`:
```python
"""EditorialAction SQLModel — append-only audit log."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EditorialAction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    draft_id: int = Field(foreign_key="draft.id")
    action: str            # 'approve' | 'edit' | 'reject' | 'save'
    original_text: Optional[str] = None
    edited_text: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/routes.py` with all routes returning `200` placeholder responses (routes first, templates next):

```python
"""Editorial dashboard routes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from bidequity.common.db import get_session
from bidequity.models.draft import Draft
from bidequity.models.editorial_action import EditorialAction
from bidequity.models.item import Item
from bidequity.models.classification import Classification
from bidequity.models.publication import Publication
from bidequity.models.source import Source

router = APIRouter()
templates = Jinja2Templates(directory="src/bidequity/dashboard/templates")


# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------

@router.get("/", response_class=RedirectResponse)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/inbox", status_code=302)


# ---------------------------------------------------------------------------
# Inbox
# ---------------------------------------------------------------------------

@router.get("/inbox", response_class=HTMLResponse)
async def inbox(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    drafts_with_context = []
    drafts = session.exec(
        select(Draft).where(Draft.status == "pending").order_by(Draft.generated_at.desc())  # type: ignore[arg-type]
    ).all()
    for draft in drafts:
        item = session.get(Item, draft.item_id)
        classification = session.exec(
            select(Classification)
            .where(Classification.item_id == draft.item_id)
            .order_by(Classification.classified_at.desc())  # type: ignore[arg-type]
        ).first()
        source = session.get(Source, item.source_id) if item else None
        drafts_with_context.append({
            "draft": draft,
            "item": item,
            "classification": classification,
            "source": source,
        })
    # Sort by relevance_score DESC; items without classification sort last
    drafts_with_context.sort(
        key=lambda x: x["classification"].relevance_score if x["classification"] else -1,
        reverse=True,
    )
    return templates.TemplateResponse(
        "inbox.html",
        {"request": request, "drafts_with_context": drafts_with_context},
    )


# ---------------------------------------------------------------------------
# Draft actions (HTMX endpoints — return row fragments)
# ---------------------------------------------------------------------------

def _get_draft_or_404(draft_id: int, session: Session) -> Draft:
    draft = session.get(Draft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


def _get_draft_context(draft: Draft, session: Session) -> dict:
    item = session.get(Item, draft.item_id)
    classification = session.exec(
        select(Classification)
        .where(Classification.item_id == draft.item_id)
        .order_by(Classification.classified_at.desc())  # type: ignore[arg-type]
    ).first()
    source = session.get(Source, item.source_id) if item else None
    return {"draft": draft, "item": item, "classification": classification, "source": source}


@router.post("/drafts/{draft_id}/approve", response_class=HTMLResponse)
async def approve_draft(
    request: Request,
    draft_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    draft = _get_draft_or_404(draft_id, session)
    draft.status = "approved"
    session.add(EditorialAction(draft_id=draft.id, action="approve"))
    session.add(draft)
    session.commit()
    session.refresh(draft)
    ctx = _get_draft_context(draft, session)
    return templates.TemplateResponse(
        "_draft_row_approved.html", {"request": request, **ctx}
    )


@router.post("/drafts/{draft_id}/reject", response_class=HTMLResponse)
async def reject_draft(
    request: Request,
    draft_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    draft = _get_draft_or_404(draft_id, session)
    draft.status = "rejected"
    session.add(EditorialAction(draft_id=draft.id, action="reject"))
    session.add(draft)
    session.commit()
    session.refresh(draft)
    ctx = _get_draft_context(draft, session)
    return templates.TemplateResponse(
        "_draft_row_rejected.html", {"request": request, **ctx}
    )


@router.post("/drafts/{draft_id}/edit", response_class=HTMLResponse)
async def edit_draft(
    request: Request,
    draft_id: int,
    linkedin_post: str = Form(...),
    newsletter_para: str = Form(...),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    draft = _get_draft_or_404(draft_id, session)
    original_text = draft.linkedin_post
    draft.linkedin_post = linkedin_post
    draft.newsletter_para = newsletter_para
    draft.status = "edited"
    session.add(EditorialAction(
        draft_id=draft.id,
        action="edit",
        original_text=original_text,
        edited_text=linkedin_post,
    ))
    session.add(draft)
    session.commit()
    session.refresh(draft)
    ctx = _get_draft_context(draft, session)
    return templates.TemplateResponse(
        "_draft_row_approved.html", {"request": request, **ctx}
    )


@router.post("/drafts/{draft_id}/save", response_class=HTMLResponse)
async def save_draft(
    request: Request,
    draft_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    draft = _get_draft_or_404(draft_id, session)
    draft.status = "saved"
    session.add(EditorialAction(draft_id=draft.id, action="save"))
    session.add(draft)
    session.commit()
    session.refresh(draft)
    ctx = _get_draft_context(draft, session)
    return templates.TemplateResponse(
        "_draft_row.html", {"request": request, **ctx}
    )


# ---------------------------------------------------------------------------
# Scheduled
# ---------------------------------------------------------------------------

@router.get("/scheduled", response_class=HTMLResponse)
async def scheduled(
    request: Request, session: Session = Depends(get_session)
) -> HTMLResponse:
    publications = session.exec(
        select(Publication)
        .where(Publication.status == "scheduled")
        .order_by(Publication.scheduled_for.asc())  # type: ignore[arg-type]
    ).all()
    pubs_with_context = []
    for pub in publications:
        draft = session.get(Draft, pub.draft_id)
        item = session.get(Item, draft.item_id) if draft else None
        pubs_with_context.append({"publication": pub, "draft": draft, "item": item})
    return templates.TemplateResponse(
        "scheduled.html",
        {"request": request, "pubs_with_context": pubs_with_context},
    )


@router.post("/publications/{pub_id}/reschedule", response_class=HTMLResponse)
async def reschedule_publication(
    request: Request,
    pub_id: int,
    scheduled_for: str = Form(...),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    pub = session.get(Publication, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    pub.scheduled_for = datetime.fromisoformat(scheduled_for)
    session.add(pub)
    session.commit()
    session.refresh(pub)
    draft = session.get(Draft, pub.draft_id)
    item = session.get(Item, draft.item_id) if draft else None
    return templates.TemplateResponse(
        "_publication_row.html",
        {"request": request, "publication": pub, "draft": draft, "item": item},
    )


@router.delete("/publications/{pub_id}", response_class=HTMLResponse)
async def delete_publication(
    pub_id: int,
    session: Session = Depends(get_session),
) -> Response:
    pub = session.get(Publication, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    # Revert draft to pending so it reappears in inbox
    draft = session.get(Draft, pub.draft_id)
    if draft:
        draft.status = "pending"
        session.add(draft)
    session.delete(pub)
    session.commit()
    # HTMX: returning empty 200 removes the row when hx-swap="outerHTML"
    return Response(status_code=200, content="")


# ---------------------------------------------------------------------------
# Published
# ---------------------------------------------------------------------------

@router.get("/published", response_class=HTMLResponse)
async def published(
    request: Request,
    channel: Optional[str] = None,
    sector: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    query = select(Publication).where(Publication.status == "published")
    if channel:
        query = query.where(Publication.channel == channel)
    publications = session.exec(query.order_by(Publication.published_at.desc())).all()  # type: ignore[arg-type]
    pubs_with_context = []
    for pub in publications:
        draft = session.get(Draft, pub.draft_id)
        item = session.get(Item, draft.item_id) if draft else None
        pubs_with_context.append({"publication": pub, "draft": draft, "item": item})
    return templates.TemplateResponse(
        "published.html",
        {
            "request": request,
            "pubs_with_context": pubs_with_context,
            "filters": {"channel": channel, "sector": sector, "from_date": from_date, "to_date": to_date},
        },
    )


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

@router.get("/sources", response_class=HTMLResponse)
async def sources(
    request: Request, session: Session = Depends(get_session)
) -> HTMLResponse:
    all_sources = session.exec(select(Source).order_by(Source.sector, Source.name)).all()
    return templates.TemplateResponse(
        "sources.html", {"request": request, "sources": all_sources}
    )


@router.post("/sources/{source_id}/toggle", response_class=HTMLResponse)
async def toggle_source(
    request: Request,
    source_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.active = not source.active
    source.updated_at = datetime.utcnow()
    session.add(source)
    session.commit()
    session.refresh(source)
    return templates.TemplateResponse(
        "_source_row.html", {"request": request, "source": source}
    )


@router.post("/sources", response_class=HTMLResponse)
async def add_source(
    request: Request,
    name: str = Form(...),
    url: str = Form(...),
    feed_url: Optional[str] = Form(default=None),
    feed_type: str = Form(...),
    sector: str = Form(...),
    category: str = Form(...),
    cadence: str = Form(...),
    signal_strength: str = Form(...),
    priority_score: int = Form(...),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    source = Source(
        name=name,
        url=url,
        feed_url=feed_url,
        feed_type=feed_type,
        sector=sector,
        category=category,
        cadence=cadence,
        signal_strength=signal_strength,
        priority_score=priority_score,
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return templates.TemplateResponse(
        "_source_row.html", {"request": request, "source": source}
    )


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

@router.get("/insights", response_class=HTMLResponse)
async def insights(
    request: Request, session: Session = Depends(get_session)
) -> HTMLResponse:
    # Total drafts by status
    all_drafts = session.exec(select(Draft)).all()
    total = len(all_drafts)
    approved = sum(1 for d in all_drafts if d.status in ("approved", "edited"))
    rejected = sum(1 for d in all_drafts if d.status == "rejected")
    approval_rate = round(approved / total * 100) if total > 0 else 0

    # Classifier agreement rate: proportion of approve+edit actions vs total actioned
    all_actions = session.exec(select(EditorialAction)).all()
    actioned = len(all_actions)
    agreed = sum(1 for a in all_actions if a.action in ("approve", "edit"))
    classifier_agreement = round(agreed / actioned * 100) if actioned > 0 else 0

    # Source approval rates
    source_stats: dict[str, dict] = {}
    for draft in all_drafts:
        item = session.get(Item, draft.item_id)
        if not item:
            continue
        source = session.get(Source, item.source_id)
        if not source:
            continue
        key = source.name
        if key not in source_stats:
            source_stats[key] = {"approved": 0, "total": 0}
        source_stats[key]["total"] += 1
        if draft.status in ("approved", "edited"):
            source_stats[key]["approved"] += 1
    top_sources = sorted(
        [
            {
                "name": k,
                "total": v["total"],
                "approved": v["approved"],
                "rate": round(v["approved"] / v["total"] * 100) if v["total"] > 0 else 0,
            }
            for k, v in source_stats.items()
        ],
        key=lambda x: x["rate"],
        reverse=True,
    )[:10]

    return templates.TemplateResponse(
        "insights.html",
        {
            "request": request,
            "total_drafts": total,
            "approved_drafts": approved,
            "rejected_drafts": rejected,
            "approval_rate": approval_rate,
            "classifier_agreement": classifier_agreement,
            "top_sources": top_sources,
        },
    )
```

- [ ] Register the router in `main.py`. Add inside `create_app()` after the `/healthz` route:

```python
from bidequity.dashboard.routes import router as dashboard_router
app.include_router(dashboard_router)
```

- [ ] Run the tests. Expect most to fail with `TemplateNotFoundError` (routes exist; templates do not yet):

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/test_dashboard/ -v 2>&1 | tail -20
```

**Commit:** `feat: dashboard routes skeleton; models; router registered in main`

---

### Task 3 — base.html template

**Files:** `bidequity-newsroom/src/bidequity/dashboard/templates/base.html`

- [ ] Create the templates directory:

```bash
mkdir -p c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom/src/bidequity/dashboard/templates
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/base.html`:

```html
<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{% block title %}BidEquity Newsroom{% endblock %}</title>

  <!-- Pico.css — classless, semantic HTML styling -->
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.slate.min.css"
  />

  <!-- HTMX — server-driven interactivity, no SPA -->
  <script src="https://unpkg.com/htmx.org@1.9.12" defer></script>

  <!-- AlpineJS — keyboard shortcuts and modal state -->
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

  <style>
    /* BidEquity palette overrides */
    :root {
      --be-navy:      #0d1b2a;
      --be-ink:       #1a2e44;
      --be-gold:      #c9a84c;
      --be-gold-dim:  #8a6e2f;
      --be-text:      #e8edf2;
      --be-muted:     #7a8a99;
      --be-success:   #2e7d32;
      --be-danger:    #b71c1c;
      --be-warning:   #e65100;
    }

    body {
      background: var(--be-navy);
      color: var(--be-text);
      font-family: "DM Sans", system-ui, sans-serif;
    }

    /* Top navigation */
    nav.top-nav {
      background: var(--be-ink);
      border-bottom: 1px solid var(--be-gold-dim);
      padding: 0.6rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 2rem;
    }

    nav.top-nav .brand {
      font-weight: 700;
      color: var(--be-gold);
      font-size: 1rem;
      letter-spacing: 0.04em;
      text-decoration: none;
    }

    nav.top-nav a {
      color: var(--be-muted);
      text-decoration: none;
      font-size: 0.875rem;
      padding: 0.25rem 0;
      border-bottom: 2px solid transparent;
      transition: color 0.15s, border-color 0.15s;
    }

    nav.top-nav a:hover,
    nav.top-nav a.active {
      color: var(--be-text);
      border-bottom-color: var(--be-gold);
    }

    main.container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1.5rem 1rem;
    }

    /* Relevance score badges */
    .badge {
      display: inline-block;
      padding: 0.15rem 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.75rem;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }
    .badge-high   { background: #1b4332; color: #74c69d; }
    .badge-medium { background: #3d2b00; color: #ffd166; }
    .badge-low    { background: #2a1a1a; color: #ef8080; }

    .badge-score-high   { background: #1b4332; color: #74c69d; }
    .badge-score-medium { background: #3d2b00; color: #ffd166; }
    .badge-score-low    { background: #2a1a1a; color: #ef8080; }

    /* Action buttons */
    .action-btn {
      padding: 0.2rem 0.6rem;
      font-size: 0.78rem;
      border-radius: 0.2rem;
      border: 1px solid;
      cursor: pointer;
      transition: opacity 0.1s;
      background: transparent;
    }
    .action-btn:hover { opacity: 0.85; }

    .btn-approve { border-color: var(--be-success); color: #74c69d; }
    .btn-reject  { border-color: var(--be-danger);  color: #ef8080; }
    .btn-edit    { border-color: var(--be-gold-dim); color: var(--be-gold); }
    .btn-save    { border-color: var(--be-muted);    color: var(--be-muted); }

    /* HTMX loading indicator on rows */
    tr.htmx-request { opacity: 0.5; pointer-events: none; }

    /* Approved / rejected row states */
    tr.row-approved { opacity: 0.55; }
    tr.row-rejected { opacity: 0.35; text-decoration: line-through; }

    /* Edit modal overlay */
    .edit-modal-overlay {
      position: fixed; inset: 0;
      background: rgba(0,0,0,0.7);
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .edit-modal {
      background: var(--be-ink);
      border: 1px solid var(--be-gold-dim);
      border-radius: 0.5rem;
      padding: 1.5rem;
      width: min(680px, 95vw);
      max-height: 90vh;
      overflow-y: auto;
    }
    .edit-modal h3 { color: var(--be-gold); margin-top: 0; }
    .edit-modal textarea {
      width: 100%;
      background: var(--be-navy);
      color: var(--be-text);
      border: 1px solid var(--be-muted);
      border-radius: 0.25rem;
      padding: 0.5rem;
      font-family: "DM Mono", monospace;
      font-size: 0.85rem;
      resize: vertical;
    }

    /* Keyboard shortcut hint bar */
    .shortcut-hint {
      font-size: 0.72rem;
      color: var(--be-muted);
      margin-bottom: 0.75rem;
    }
    .shortcut-hint kbd {
      background: var(--be-ink);
      border: 1px solid var(--be-muted);
      border-radius: 0.2rem;
      padding: 0.1rem 0.35rem;
      font-size: 0.7rem;
    }

    /* Source health dots */
    .health-dot {
      display: inline-block;
      width: 0.55rem; height: 0.55rem;
      border-radius: 50%;
      margin-right: 0.35rem;
    }
    .health-ok      { background: #74c69d; }
    .health-warn    { background: #ffd166; }
    .health-fail    { background: #ef8080; }

    /* Responsive: hide lower-priority columns on mobile */
    @media (max-width: 640px) {
      .hide-mobile { display: none; }
      nav.top-nav  { gap: 1rem; }
    }
  </style>
</head>
<body>

<!-- Top navigation -->
<nav class="top-nav">
  <a href="/" class="brand">BidEquity Newsroom</a>
  <a href="/inbox"     {% if request.url.path == '/inbox'     %}class="active"{% endif %}>Inbox</a>
  <a href="/scheduled" {% if request.url.path == '/scheduled' %}class="active"{% endif %}>Scheduled</a>
  <a href="/published" {% if request.url.path == '/published' %}class="active"{% endif %}>Published</a>
  <a href="/sources"   {% if request.url.path == '/sources'   %}class="active"{% endif %}>Sources</a>
  <a href="/insights"  {% if request.url.path == '/insights'  %}class="active"{% endif %}>Insights</a>
</nav>

<!-- Keyboard shortcut handler (AlpineJS) -->
<!--
  Shortcuts apply when a draft row is "focused" (via J/K navigation).
  x-data on body maintains focused_id state.
  Actual hx-post triggers are dispatched programmatically via htmx.trigger().
-->
<div
  x-data="{
    focused_id: null,
    row_ids: [],
    init() {
      this.refreshRows();
    },
    refreshRows() {
      this.row_ids = Array.from(document.querySelectorAll('tr[data-draft-id]'))
        .map(el => parseInt(el.dataset.draftId));
    },
    focusedIndex() {
      return this.row_ids.indexOf(this.focused_id);
    },
    moveDown() {
      const idx = this.focusedIndex();
      const next = idx < this.row_ids.length - 1 ? idx + 1 : idx;
      this.focused_id = this.row_ids[next] ?? null;
      this.highlightFocused();
    },
    moveUp() {
      const idx = this.focusedIndex();
      const prev = idx > 0 ? idx - 1 : 0;
      this.focused_id = this.row_ids[prev] ?? null;
      this.highlightFocused();
    },
    highlightFocused() {
      document.querySelectorAll('tr[data-draft-id]').forEach(el => {
        el.style.outline = el.dataset.draftId == this.focused_id
          ? '2px solid var(--be-gold)' : '';
      });
      const el = document.querySelector('tr[data-draft-id=\"' + this.focused_id + '\"]');
      if (el) el.scrollIntoView({ block: 'nearest' });
    },
    triggerAction(action) {
      if (!this.focused_id) return;
      const el = document.querySelector('tr[data-draft-id=\"' + this.focused_id + '\"]');
      if (!el) return;
      const btn = el.querySelector('[data-action=\"' + action + '\"]');
      if (btn) btn.click();
    }
  }"
  @keydown.window="
    if (['INPUT','TEXTAREA','SELECT'].includes($event.target.tagName)) return;
    if ($event.key === 'j' || $event.key === 'J') { $event.preventDefault(); moveDown(); }
    if ($event.key === 'k' || $event.key === 'K') { $event.preventDefault(); moveUp(); }
    if ($event.key === 'a' || $event.key === 'A') { triggerAction('approve'); }
    if ($event.key === 'r' || $event.key === 'R') { triggerAction('reject');  }
    if ($event.key === 'e' || $event.key === 'E') { triggerAction('edit');    }
    if ($event.key === 's' || $event.key === 'S') { triggerAction('save');    }
  "
>
  <main class="container">
    {% block content %}{% endblock %}
  </main>
</div>

</body>
</html>
```

- [ ] Run the tests. `test_inbox_keyboard_shortcut_attributes_present` should now pass if templates resolve correctly. Expect `TemplateNotFoundError: inbox.html` next:

```bash
uv run pytest tests/test_dashboard/test_routes.py::test_inbox_keyboard_shortcut_attributes_present -v
```

**Commit:** `feat: base.html with Pico.css, HTMX, AlpineJS keyboard shortcuts`

---

### Task 4 — Inbox and draft row templates

**Files:**
- `bidequity-newsroom/src/bidequity/dashboard/templates/inbox.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/_draft_row.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/_draft_row_approved.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/_draft_row_rejected.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/_edit_modal.html`

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/inbox.html`:

```html
{% extends "base.html" %}
{% block title %}Inbox — BidEquity Newsroom{% endblock %}

{% block content %}
<hgroup>
  <h2>Inbox</h2>
  <p>Pending drafts ranked by relevance. <strong>{{ drafts_with_context | length }}</strong> items awaiting review.</p>
</hgroup>

<p class="shortcut-hint">
  <kbd>J</kbd> / <kbd>K</kbd> navigate &nbsp;
  <kbd>A</kbd> approve &nbsp;
  <kbd>R</kbd> reject &nbsp;
  <kbd>E</kbd> edit &nbsp;
  <kbd>S</kbd> save for later
</p>

{% if drafts_with_context %}
<div style="overflow-x: auto;">
  <table role="grid">
    <thead>
      <tr>
        <th>Title / Source</th>
        <th class="hide-mobile">Sector</th>
        <th class="hide-mobile" style="width:3.5rem; text-align:center;">Score</th>
        <th>So What</th>
        <th style="width:11rem;">Actions</th>
      </tr>
    </thead>
    <tbody id="inbox-rows"
           hx-on::after-swap="document.querySelector('[x-data]').__x.$data.refreshRows()">
      {% for ctx in drafts_with_context %}
        {% include "_draft_row.html" %}
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
  <p style="color: var(--be-muted); padding: 2rem 0;">
    Inbox is empty — no pending drafts. Run the generator to produce new drafts.
  </p>
{% endif %}
{% endblock %}
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/_draft_row.html`:

```html
{# Partial: a single pending draft row. Used in inbox.html and returned by HTMX save action. #}
{# Variables expected: draft, item, classification, source #}
<tr id="draft-{{ draft.id }}"
    data-draft-id="{{ draft.id }}"
    hx-swap="outerHTML"
    hx-target="closest tr">

  <td>
    <a href="{{ item.url if item else '#' }}"
       target="_blank"
       rel="noopener"
       style="color: var(--be-text); font-weight: 600; font-size: 0.9rem; text-decoration: none;">
      {{ item.title if item else "(no title)" }}
    </a>
    <br/>
    <small style="color: var(--be-muted);">
      {{ source.name if source else "Unknown source" }}
      {% if source %}&nbsp;&middot;&nbsp;{{ source.sector }}{% endif %}
    </small>
    {% if classification and classification.pursuit_implication %}
    <br/>
    <small style="color: var(--be-muted); font-style: italic;">
      {{ classification.pursuit_implication | truncate(120) }}
    </small>
    {% endif %}
  </td>

  <td class="hide-mobile" style="vertical-align: top; padding-top: 0.8rem;">
    {% if classification %}
      {% for sector in classification.sectors %}
        <span class="badge badge-medium" style="margin-bottom: 0.2rem; display: inline-block;">
          {{ sector }}
        </span>
      {% endfor %}
    {% endif %}
  </td>

  <td class="hide-mobile" style="text-align: center; vertical-align: top; padding-top: 0.8rem;">
    {% if classification %}
      {% set score = classification.relevance_score %}
      {% if score >= 8 %}
        <span class="badge badge-score-high">{{ score }}</span>
      {% elif score >= 6 %}
        <span class="badge badge-score-medium">{{ score }}</span>
      {% else %}
        <span class="badge badge-score-low">{{ score }}</span>
      {% endif %}
    {% else %}
      <span class="badge badge-score-low">—</span>
    {% endif %}
  </td>

  <td style="vertical-align: top; padding-top: 0.8rem; font-size: 0.85rem;">
    {{ draft.so_what_line }}
  </td>

  <td style="vertical-align: top; padding-top: 0.7rem; white-space: nowrap;">
    <button class="action-btn btn-approve"
            data-action="approve"
            hx-post="/drafts/{{ draft.id }}/approve"
            hx-swap="outerHTML"
            hx-target="closest tr">
      Approve
    </button>
    <button class="action-btn btn-edit"
            data-action="edit"
            hx-get="/drafts/{{ draft.id }}/edit-modal"
            hx-swap="outerHTML"
            hx-target="closest tr">
      Edit
    </button>
    <br style="margin: 0.2rem 0;" />
    <button class="action-btn btn-reject"
            data-action="reject"
            hx-post="/drafts/{{ draft.id }}/reject"
            hx-swap="outerHTML"
            hx-target="closest tr">
      Reject
    </button>
    <button class="action-btn btn-save"
            data-action="save"
            hx-post="/drafts/{{ draft.id }}/save"
            hx-swap="outerHTML"
            hx-target="closest tr">
      Save
    </button>
  </td>
</tr>
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/_draft_row_approved.html`:

```html
{# Partial: approved/edited draft row — no action buttons, greyed. #}
{# Variables expected: draft, item, classification, source #}
<tr id="draft-{{ draft.id }}"
    class="row-approved"
    data-draft-id="{{ draft.id }}">

  <td>
    <a href="{{ item.url if item else '#' }}"
       target="_blank" rel="noopener"
       style="color: var(--be-muted); font-weight: 600; font-size: 0.9rem; text-decoration: none;">
      {{ item.title if item else "(no title)" }}
    </a>
    <br/>
    <small style="color: var(--be-muted);">
      {{ source.name if source else "Unknown source" }}
    </small>
  </td>

  <td class="hide-mobile">
    {% if classification %}
      {% for sector in classification.sectors %}
        <span class="badge badge-medium">{{ sector }}</span>
      {% endfor %}
    {% endif %}
  </td>

  <td class="hide-mobile" style="text-align: center;">
    {% if classification %}
      <span class="badge badge-score-high">{{ classification.relevance_score }}</span>
    {% endif %}
  </td>

  <td style="font-size: 0.85rem; color: var(--be-muted);">
    {{ draft.so_what_line }}
  </td>

  <td>
    <span class="badge" style="background: #1b4332; color: #74c69d;">
      {{ draft.status | capitalize }}
    </span>
  </td>
</tr>
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/_draft_row_rejected.html`:

```html
{# Partial: rejected draft row — struck through, no actions. #}
{# Variables expected: draft, item, source #}
<tr id="draft-{{ draft.id }}"
    class="row-rejected"
    data-draft-id="{{ draft.id }}"
    style="color: var(--be-muted);">

  <td>
    <span style="font-size: 0.9rem;">
      {{ item.title if item else "(no title)" }}
    </span>
    <br/>
    <small>{{ source.name if source else "Unknown source" }}</small>
  </td>

  <td class="hide-mobile"></td>
  <td class="hide-mobile"></td>

  <td style="font-size: 0.85rem;">{{ draft.so_what_line }}</td>

  <td>
    <span class="badge" style="background: #2a1a1a; color: #ef8080;">Rejected</span>
  </td>
</tr>
```

- [ ] Add the edit-modal GET route to `routes.py`. This route renders the modal inline; the Edit button targets `outerHTML` of the row, replacing it with a modal-containing row:

```python
@router.get("/drafts/{draft_id}/edit-modal", response_class=HTMLResponse)
async def edit_modal(
    request: Request,
    draft_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    draft = _get_draft_or_404(draft_id, session)
    ctx = _get_draft_context(draft, session)
    return templates.TemplateResponse("_edit_modal.html", {"request": request, **ctx})
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/_edit_modal.html`:

```html
{# Partial: edit modal, replaces the draft row via hx-swap="outerHTML". #}
{# On submit, the form targets the original tr id and restores a normal row. #}
{# Variables expected: draft, item, source #}
<tr id="draft-{{ draft.id }}" data-draft-id="{{ draft.id }}" hx-swap="outerHTML" hx-target="closest tr">
  <td colspan="5" style="padding: 0;">
    <div class="edit-modal-overlay"
         x-data="{ open: true }"
         x-show="open"
         @keydown.escape.window="open = false; htmx.ajax('GET', '/inbox-row/{{ draft.id }}', {target: '#draft-{{ draft.id }}', swap: 'outerHTML'})">

      <div class="edit-modal" @click.stop>
        <h3>Edit draft</h3>
        <p style="color: var(--be-muted); font-size: 0.85rem; margin-bottom: 1rem;">
          <strong>{{ item.title if item else "(no title)" }}</strong>
          <br/>{{ source.name if source else "" }}
        </p>

        <form hx-post="/drafts/{{ draft.id }}/edit"
              hx-target="#draft-{{ draft.id }}"
              hx-swap="outerHTML">

          <label for="edit-linkedin-{{ draft.id }}" style="font-size: 0.85rem; color: var(--be-muted);">
            LinkedIn post
          </label>
          <textarea id="edit-linkedin-{{ draft.id }}"
                    name="linkedin_post"
                    rows="8"
                    style="margin-bottom: 1rem;">{{ draft.linkedin_post }}</textarea>

          <label for="edit-newsletter-{{ draft.id }}" style="font-size: 0.85rem; color: var(--be-muted);">
            Newsletter paragraph
          </label>
          <textarea id="edit-newsletter-{{ draft.id }}"
                    name="newsletter_para"
                    rows="4">{{ draft.newsletter_para }}</textarea>

          <div style="display: flex; gap: 0.75rem; margin-top: 1.25rem; justify-content: flex-end;">
            <button type="button"
                    class="action-btn btn-save"
                    @click="open = false"
                    style="padding: 0.4rem 1rem;">
              Cancel
            </button>
            <button type="submit"
                    class="action-btn btn-approve"
                    style="padding: 0.4rem 1.25rem;">
              Save &amp; approve
            </button>
          </div>
        </form>
      </div>
    </div>
  </td>
</tr>
```

- [ ] Add a helper route to `routes.py` for the Escape-key cancel path (returns the draft row in its current state):

```python
@router.get("/inbox-row/{draft_id}", response_class=HTMLResponse)
async def inbox_row(
    request: Request,
    draft_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    """Returns the current state of a draft row (used by edit modal cancel)."""
    draft = _get_draft_or_404(draft_id, session)
    ctx = _get_draft_context(draft, session)
    template = "_draft_row.html" if draft.status == "pending" else "_draft_row_approved.html"
    return templates.TemplateResponse(template, {"request": request, **ctx})
```

- [ ] Run the inbox tests:

```bash
uv run pytest tests/test_dashboard/ -k "inbox or approve or reject or edit or save" -v
```

Expected: all inbox and action tests pass.

**Commit:** `feat: inbox.html and all draft row partials; edit modal; inbox tests pass`

---

### Task 5 — Scheduled, Published, Sources, and Insights templates

**Files:**
- `bidequity-newsroom/src/bidequity/dashboard/templates/scheduled.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/_publication_row.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/published.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/sources.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/_source_row.html`
- `bidequity-newsroom/src/bidequity/dashboard/templates/insights.html`

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/scheduled.html`:

```html
{% extends "base.html" %}
{% block title %}Scheduled — BidEquity Newsroom{% endblock %}

{% block content %}
<hgroup>
  <h2>Scheduled</h2>
  <p><strong>{{ pubs_with_context | length }}</strong> publication(s) queued.</p>
</hgroup>

{% if pubs_with_context %}
<div style="overflow-x: auto;">
  <table role="grid">
    <thead>
      <tr>
        <th>Title</th>
        <th>Channel</th>
        <th>Scheduled for</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for ctx in pubs_with_context %}
        {% set pub = ctx.publication %}
        {% set draft = ctx.draft %}
        {% set item = ctx.item %}
        <tr id="pub-{{ pub.id }}" hx-swap="outerHTML" hx-target="closest tr">
          <td>
            <span style="font-weight: 600; font-size: 0.9rem;">
              {{ item.title if item else "(untitled)" }}
            </span>
          </td>
          <td>
            <span class="badge badge-medium">{{ pub.channel }}</span>
          </td>
          <td style="font-variant-numeric: tabular-nums; font-size: 0.875rem;">
            {{ pub.scheduled_for.strftime('%d %b %Y %H:%M') if pub.scheduled_for else "—" }}
          </td>
          <td style="white-space: nowrap;">
            <details style="display: inline;">
              <summary class="action-btn btn-edit" style="display: inline-block; cursor: pointer;">
                Reschedule
              </summary>
              <form hx-post="/publications/{{ pub.id }}/reschedule"
                    hx-target="#pub-{{ pub.id }}"
                    hx-swap="outerHTML"
                    style="display: flex; gap: 0.5rem; align-items: center; margin-top: 0.5rem;">
                <input type="datetime-local"
                       name="scheduled_for"
                       value="{{ pub.scheduled_for.strftime('%Y-%m-%dT%H:%M') if pub.scheduled_for else '' }}"
                       style="font-size: 0.8rem; padding: 0.2rem 0.4rem;" />
                <button type="submit" class="action-btn btn-approve">Confirm</button>
              </form>
            </details>
            &nbsp;
            <button class="action-btn btn-reject"
                    hx-delete="/publications/{{ pub.id }}"
                    hx-target="#pub-{{ pub.id }}"
                    hx-swap="outerHTML"
                    hx-confirm="Remove from schedule and return to inbox?">
              Remove
            </button>
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
  <p style="color: var(--be-muted); padding: 2rem 0;">No scheduled publications.</p>
{% endif %}
{% endblock %}
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/_publication_row.html`:

```html
{# Partial: single scheduled publication row, returned by reschedule HTMX action. #}
<tr id="pub-{{ publication.id }}" hx-swap="outerHTML" hx-target="closest tr">
  <td>
    <span style="font-weight: 600; font-size: 0.9rem;">
      {{ item.title if item else "(untitled)" }}
    </span>
  </td>
  <td>
    <span class="badge badge-medium">{{ publication.channel }}</span>
  </td>
  <td style="font-variant-numeric: tabular-nums; font-size: 0.875rem;">
    {{ publication.scheduled_for.strftime('%d %b %Y %H:%M') if publication.scheduled_for else "—" }}
  </td>
  <td>
    <span class="badge" style="background: #1b4332; color: #74c69d;">Rescheduled</span>
  </td>
</tr>
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/published.html`:

```html
{% extends "base.html" %}
{% block title %}Published — BidEquity Newsroom{% endblock %}

{% block content %}
<hgroup>
  <h2>Published</h2>
  <p>Historical publications with engagement metrics.</p>
</hgroup>

<!-- Filter bar -->
<form method="get" action="/published"
      style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem; align-items: flex-end;">
  <label style="font-size: 0.85rem;">
    Channel
    <select name="channel" style="font-size: 0.85rem; padding: 0.25rem 0.5rem; margin-top: 0.25rem;">
      <option value="">All</option>
      <option value="linkedin"   {% if filters.channel == 'linkedin'   %}selected{% endif %}>LinkedIn</option>
      <option value="newsletter" {% if filters.channel == 'newsletter' %}selected{% endif %}>Newsletter</option>
    </select>
  </label>
  <label style="font-size: 0.85rem;">
    Sector
    <input type="text" name="sector"
           value="{{ filters.sector or '' }}"
           placeholder="e.g. Defence"
           style="font-size: 0.85rem; padding: 0.25rem 0.5rem; width: 9rem; margin-top: 0.25rem;" />
  </label>
  <button type="submit" class="action-btn btn-edit" style="padding: 0.3rem 1rem;">Filter</button>
  <a href="/published" class="action-btn btn-save" style="padding: 0.3rem 0.75rem; text-decoration: none;">Clear</a>
</form>

{% if pubs_with_context %}
<div style="overflow-x: auto;">
  <table role="grid">
    <thead>
      <tr>
        <th>Title</th>
        <th>Channel</th>
        <th class="hide-mobile">Published</th>
        <th class="hide-mobile">Impressions</th>
        <th class="hide-mobile">Reactions</th>
        <th class="hide-mobile">Shares</th>
      </tr>
    </thead>
    <tbody>
      {% for ctx in pubs_with_context %}
        {% set pub = ctx.publication %}
        {% set item = ctx.item %}
        <tr>
          <td>
            {% if pub.external_url %}
              <a href="{{ pub.external_url }}" target="_blank" rel="noopener"
                 style="color: var(--be-text); font-weight: 600; font-size: 0.9rem; text-decoration: none;">
                {{ item.title if item else "(untitled)" }}
              </a>
            {% else %}
              <span style="font-weight: 600; font-size: 0.9rem;">
                {{ item.title if item else "(untitled)" }}
              </span>
            {% endif %}
          </td>
          <td><span class="badge badge-medium">{{ pub.channel }}</span></td>
          <td class="hide-mobile" style="font-size: 0.85rem;">
            {{ pub.published_at.strftime('%d %b %Y') if pub.published_at else "—" }}
          </td>
          <td class="hide-mobile" style="font-variant-numeric: tabular-nums; text-align: right;">—</td>
          <td class="hide-mobile" style="font-variant-numeric: tabular-nums; text-align: right;">—</td>
          <td class="hide-mobile" style="font-variant-numeric: tabular-nums; text-align: right;">—</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
  <p style="color: var(--be-muted); padding: 2rem 0;">No published items yet.</p>
{% endif %}
{% endblock %}
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/sources.html`:

```html
{% extends "base.html" %}
{% block title %}Sources — BidEquity Newsroom{% endblock %}

{% block content %}
<hgroup>
  <h2>Sources</h2>
  <p><strong>{{ sources | length }}</strong> sources configured.</p>
</hgroup>

<!-- Add source form -->
<details style="margin-bottom: 1.5rem;">
  <summary class="action-btn btn-edit" style="display: inline-block; cursor: pointer; padding: 0.35rem 1rem;">
    + Add source
  </summary>
  <form hx-post="/sources"
        hx-target="#sources-tbody"
        hx-swap="afterbegin"
        style="margin-top: 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem 1.5rem;
               background: var(--be-ink); padding: 1rem; border-radius: 0.4rem; border: 1px solid var(--be-gold-dim);">
    <label>
      Name
      <input type="text" name="name" required style="width: 100%; font-size: 0.85rem;" />
    </label>
    <label>
      Sector
      <input type="text" name="sector" required style="width: 100%; font-size: 0.85rem;" />
    </label>
    <label>
      URL
      <input type="url" name="url" required style="width: 100%; font-size: 0.85rem;" />
    </label>
    <label>
      Feed URL (optional)
      <input type="url" name="feed_url" style="width: 100%; font-size: 0.85rem;" />
    </label>
    <label>
      Category
      <input type="text" name="category" required style="width: 100%; font-size: 0.85rem;" />
    </label>
    <label>
      Feed type
      <select name="feed_type" style="width: 100%; font-size: 0.85rem;">
        <option value="rss">rss</option>
        <option value="api">api</option>
        <option value="scrape_static">scrape_static</option>
        <option value="scrape_js">scrape_js</option>
      </select>
    </label>
    <label>
      Cadence
      <select name="cadence" style="width: 100%; font-size: 0.85rem;">
        <option value="daily">daily</option>
        <option value="weekly">weekly</option>
        <option value="monthly">monthly</option>
      </select>
    </label>
    <label>
      Signal strength
      <select name="signal_strength" style="width: 100%; font-size: 0.85rem;">
        <option value="high">high</option>
        <option value="medium">medium</option>
        <option value="low">low</option>
      </select>
    </label>
    <label>
      Priority score (1–10)
      <input type="number" name="priority_score" min="1" max="10" value="5"
             style="width: 100%; font-size: 0.85rem;" />
    </label>
    <div style="grid-column: span 2; text-align: right; margin-top: 0.5rem;">
      <button type="submit" class="action-btn btn-approve" style="padding: 0.4rem 1.25rem;">Add source</button>
    </div>
  </form>
</details>

<div style="overflow-x: auto;">
  <table role="grid">
    <thead>
      <tr>
        <th>Name</th>
        <th class="hide-mobile">Sector</th>
        <th class="hide-mobile">Type / Cadence</th>
        <th>Health</th>
        <th>Active</th>
      </tr>
    </thead>
    <tbody id="sources-tbody">
      {% for source in sources %}
        {% include "_source_row.html" %}
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/_source_row.html`:

```html
{# Partial: single source row. Variables expected: source #}
<tr id="source-{{ source.id }}"
    hx-swap="outerHTML"
    hx-target="closest tr">

  <td>
    <a href="{{ source.url }}" target="_blank" rel="noopener"
       style="color: var(--be-text); font-weight: 600; font-size: 0.88rem; text-decoration: none;">
      {{ source.name }}
    </a>
    {% if source.owner %}
      <br/><small style="color: var(--be-muted);">{{ source.owner }}</small>
    {% endif %}
  </td>

  <td class="hide-mobile" style="font-size: 0.85rem;">{{ source.sector }}</td>

  <td class="hide-mobile" style="font-size: 0.82rem; color: var(--be-muted);">
    <span class="badge badge-low">{{ source.feed_type }}</span>
    &nbsp;{{ source.cadence }}
  </td>

  <td>
    {% if not source.active %}
      <span class="health-dot" style="background: var(--be-muted);"></span>
      <small style="color: var(--be-muted);">Disabled</small>
    {% elif source.consecutive_failures >= 5 %}
      <span class="health-dot health-fail"></span>
      <small style="color: #ef8080;">{{ source.consecutive_failures }} failures</small>
    {% elif source.consecutive_failures >= 2 %}
      <span class="health-dot health-warn"></span>
      <small style="color: #ffd166;">{{ source.consecutive_failures }} failures</small>
    {% else %}
      <span class="health-dot health-ok"></span>
      <small style="color: var(--be-muted);">
        {% if source.last_success_at %}
          {{ source.last_success_at.strftime('%d %b') }}
        {% else %}
          Never polled
        {% endif %}
      </small>
    {% endif %}
  </td>

  <td>
    <button class="action-btn {% if source.active %}btn-reject{% else %}btn-approve{% endif %}"
            hx-post="/sources/{{ source.id }}/toggle"
            hx-target="#source-{{ source.id }}"
            hx-swap="outerHTML">
      {% if source.active %}Disable{% else %}Enable{% endif %}
    </button>
  </td>
</tr>
```

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/templates/insights.html`:

```html
{% extends "base.html" %}
{% block title %}Insights — BidEquity Newsroom{% endblock %}

{% block content %}
<hgroup>
  <h2>Insights</h2>
  <p>Editorial performance and operating costs.</p>
</hgroup>

<!-- Stats grid -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem;">

  <div style="background: var(--be-ink); border: 1px solid var(--be-gold-dim); border-radius: 0.4rem; padding: 1rem;">
    <div style="font-size: 0.75rem; color: var(--be-muted); text-transform: uppercase; letter-spacing: 0.05em;">
      Total drafts
    </div>
    <div style="font-size: 2rem; font-weight: 700; color: var(--be-text); font-variant-numeric: tabular-nums;">
      {{ total_drafts }}
    </div>
  </div>

  <div style="background: var(--be-ink); border: 1px solid var(--be-gold-dim); border-radius: 0.4rem; padding: 1rem;">
    <div style="font-size: 0.75rem; color: var(--be-muted); text-transform: uppercase; letter-spacing: 0.05em;">
      Approval rate
    </div>
    <div style="font-size: 2rem; font-weight: 700; color: #74c69d; font-variant-numeric: tabular-nums;">
      {{ approval_rate }}%
    </div>
    <div style="font-size: 0.78rem; color: var(--be-muted);">
      {{ approved_drafts }} approved &middot; {{ rejected_drafts }} rejected
    </div>
  </div>

  <div style="background: var(--be-ink); border: 1px solid var(--be-gold-dim); border-radius: 0.4rem; padding: 1rem;">
    <div style="font-size: 0.75rem; color: var(--be-muted); text-transform: uppercase; letter-spacing: 0.05em;">
      Classifier agreement
    </div>
    <div style="font-size: 2rem; font-weight: 700; color: {% if classifier_agreement >= 80 %}#74c69d{% elif classifier_agreement >= 60 %}#ffd166{% else %}#ef8080{% endif %}; font-variant-numeric: tabular-nums;">
      {{ classifier_agreement }}%
    </div>
    <div style="font-size: 0.78rem; color: var(--be-muted);">Target: ≥ 80%</div>
  </div>

</div>

<!-- Top sources by approval rate -->
{% if top_sources %}
<h3 style="color: var(--be-gold); margin-bottom: 0.75rem; font-size: 1rem;">Top sources by approval rate</h3>
<table role="grid" style="font-size: 0.875rem;">
  <thead>
    <tr>
      <th>Source</th>
      <th style="text-align: right;">Drafts</th>
      <th style="text-align: right;">Approved</th>
      <th style="text-align: right;">Rate</th>
    </tr>
  </thead>
  <tbody>
    {% for src in top_sources %}
    <tr>
      <td>{{ src.name }}</td>
      <td style="text-align: right; font-variant-numeric: tabular-nums;">{{ src.total }}</td>
      <td style="text-align: right; font-variant-numeric: tabular-nums;">{{ src.approved }}</td>
      <td style="text-align: right; font-variant-numeric: tabular-nums;">
        {% if src.rate >= 80 %}
          <span class="badge badge-score-high">{{ src.rate }}%</span>
        {% elif src.rate >= 50 %}
          <span class="badge badge-score-medium">{{ src.rate }}%</span>
        {% else %}
          <span class="badge badge-score-low">{{ src.rate }}%</span>
        {% endif %}
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% else %}
  <p style="color: var(--be-muted);">No editorial actions recorded yet. Begin triaging the inbox to generate insights.</p>
{% endif %}
{% endblock %}
```

- [ ] Run the full test suite:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/test_dashboard/ -v
```

Expected: all tests pass.

**Commit:** `feat: scheduled, published, sources, insights templates; all dashboard tests pass`

---

### Task 6 — Sunday digest email

**Files:** `bidequity-newsroom/src/bidequity/dashboard/digest.py`

- [ ] Create `bidequity-newsroom/src/bidequity/dashboard/digest.py`:

```python
"""Sunday evening digest email — summary of the week's pending drafts sent to the operator."""

import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from sqlmodel import Session, select

from bidequity.common.config import get_config
from bidequity.models.draft import Draft
from bidequity.models.item import Item
from bidequity.models.classification import Classification
from bidequity.models.source import Source

logger = logging.getLogger(__name__)


def _build_digest_body(drafts_with_context: list[dict]) -> str:
    """Format the weekly digest as plain text."""
    now = datetime.utcnow()
    week_start = (now - timedelta(days=7)).strftime("%d %b")
    week_end = now.strftime("%d %b %Y")

    lines = [
        "BidEquity Newsroom — Weekly Digest",
        f"Week of {week_start} to {week_end}",
        "=" * 60,
        "",
        f"{len(drafts_with_context)} item(s) pending review in your inbox.",
        "",
    ]

    for i, ctx in enumerate(drafts_with_context, start=1):
        draft = ctx["draft"]
        item = ctx["item"]
        classification = ctx["classification"]
        source = ctx["source"]

        title = item.title if item else "(no title)"
        source_name = source.name if source else "Unknown"
        score = classification.relevance_score if classification else "?"
        so_what = draft.so_what_line

        lines += [
            f"{i}. [{score}/10] {title}",
            f"   Source: {source_name}",
            f"   So what: {so_what}",
            "",
        ]

    lines += [
        "=" * 60,
        "Open your inbox to triage: https://newsroom.bidequity.co.uk/inbox",
        "",
        "You are receiving this because you are the BidEquity Newsroom operator.",
    ]
    return "\n".join(lines)


def send_weekly_digest(session: Session) -> None:
    """
    Query pending drafts from the past 7 days and send a plain-text digest email
    via SMTP (Cloudflare Email Routing relay at smtp.cloudflare.net).

    Called by APScheduler every Sunday at 18:00 UTC.
    """
    config = get_config()

    # Check SMTP config is available
    smtp_host = getattr(config, "SMTP_HOST", "smtp.cloudflare.net")
    smtp_port = getattr(config, "SMTP_PORT", 587)
    smtp_user = getattr(config, "SMTP_USER", "")
    smtp_password = getattr(config, "SMTP_PASSWORD", "")
    digest_to = getattr(config, "DIGEST_TO_EMAIL", "")
    digest_from = getattr(config, "DIGEST_FROM_EMAIL", "newsroom@bidequity.co.uk")

    if not digest_to:
        logger.warning("DIGEST_TO_EMAIL not configured — skipping weekly digest")
        return

    # Fetch pending drafts ordered by relevance DESC
    since = datetime.utcnow() - timedelta(days=7)
    drafts = session.exec(
        select(Draft)
        .where(Draft.status == "pending")
        .where(Draft.generated_at >= since)
    ).all()

    if not drafts:
        logger.info("No pending drafts this week — skipping digest")
        return

    drafts_with_context = []
    for draft in drafts:
        item = session.get(Item, draft.item_id)
        classification = session.exec(
            select(Classification)
            .where(Classification.item_id == draft.item_id)
            .order_by(Classification.classified_at.desc())  # type: ignore[arg-type]
        ).first()
        source = session.get(Source, item.source_id) if item else None
        drafts_with_context.append({
            "draft": draft,
            "item": item,
            "classification": classification,
            "source": source,
        })

    # Sort by relevance score DESC
    drafts_with_context.sort(
        key=lambda x: x["classification"].relevance_score if x["classification"] else -1,
        reverse=True,
    )

    body = _build_digest_body(drafts_with_context)
    subject = f"BidEquity Newsroom — {len(drafts_with_context)} item(s) to review"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = digest_from
    msg["To"] = digest_to

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            if smtp_user and smtp_password:
                smtp.login(smtp_user, smtp_password)
            smtp.send_message(msg)
        logger.info("Weekly digest sent to %s (%d items)", digest_to, len(drafts_with_context))
    except smtplib.SMTPException as exc:
        logger.error("Failed to send weekly digest: %s", exc)
        raise


def register_digest_job(scheduler, session_factory) -> None:  # type: ignore[no-untyped-def]
    """
    Register the Sunday 18:00 UTC digest job with APScheduler.

    Call from the FastAPI lifespan after the scheduler is started:

        from bidequity.dashboard.digest import register_digest_job
        register_digest_job(scheduler, session_factory)
    """
    scheduler.add_job(
        func=lambda: _run_digest(session_factory),
        trigger="cron",
        day_of_week="sun",
        hour=18,
        minute=0,
        id="weekly_digest",
        replace_existing=True,
    )
    logger.info("Weekly digest job registered: Sundays 18:00 UTC")


def _run_digest(session_factory) -> None:  # type: ignore[no-untyped-def]
    """Thin wrapper to open a session and call send_weekly_digest."""
    with session_factory() as session:
        send_weekly_digest(session)
```

- [ ] Add the SMTP env vars to `config.py` (append to the `Config` class):

```python
# Digest email (weekly Sunday summary)
SMTP_HOST: str = "smtp.cloudflare.net"
SMTP_PORT: int = 587
SMTP_USER: str = ""
SMTP_PASSWORD: str = ""
DIGEST_TO_EMAIL: str = ""
DIGEST_FROM_EMAIL: str = "newsroom@bidequity.co.uk"
```

- [ ] Add the SMTP vars to `.env.example`:

```dotenv
# Weekly digest email (Cloudflare Email Routing SMTP relay)
SMTP_HOST=smtp.cloudflare.net
SMTP_PORT=587
SMTP_USER=newsroom@bidequity.co.uk
SMTP_PASSWORD=your-cloudflare-smtp-password
DIGEST_TO_EMAIL=paul@bidequity.co.uk
DIGEST_FROM_EMAIL=newsroom@bidequity.co.uk
```

- [ ] Run ruff and mypy on the new file:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run ruff check src/bidequity/dashboard/digest.py
uv run mypy src/bidequity/dashboard/digest.py
```

**Commit:** `feat: Sunday digest email; SMTP config; APScheduler job registration`

---

### Task 7 — Wire router into main and add Alembic migration

**Files:**
- `bidequity-newsroom/src/bidequity/main.py` (update)
- `bidequity-newsroom/alembic/env.py` (update imports)
- New Alembic migration for dashboard models

- [ ] Update `bidequity-newsroom/src/bidequity/main.py` to mount the dashboard router and configure Jinja2 templates:

```python
"""FastAPI application factory."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from bidequity.common.observability import init_sentry
from bidequity.dashboard.routes import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_sentry()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="BidEquity Newsroom", version="0.1.0", lifespan=lifespan)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(dashboard_router)
    return app


app = create_app()
```

- [ ] Update `bidequity-newsroom/alembic/env.py` to import all dashboard models so Alembic can generate the migration. Add these imports after the comment `# Import all models here`:

```python
from bidequity.models.source import Source  # noqa: F401
from bidequity.models.item import Item  # noqa: F401
from bidequity.models.classification import Classification  # noqa: F401
from bidequity.models.draft import Draft  # noqa: F401
from bidequity.models.publication import Publication  # noqa: F401
from bidequity.models.editorial_action import EditorialAction  # noqa: F401
```

- [ ] Generate the migration (requires a running local Postgres with the database created):

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run alembic revision --autogenerate -m "dashboard_models"
```

- [ ] Review the generated migration file in `alembic/versions/`. Verify it creates tables for: `source`, `item`, `classification`, `draft`, `publication`, `editorialaction`.

- [ ] Apply the migration:

```bash
uv run alembic upgrade head
```

**Commit:** `feat: Alembic migration for all dashboard models; main.py mounts dashboard router`

---

### Task 8 — Final integration check

**Files:** none (verification only)

- [ ] Run the full test suite:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/ -v
```

Expected: all tests pass including `test_healthz` and all `test_dashboard` tests.

- [ ] Run linting and type checking:

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
```

Expected: no errors.

- [ ] Start the app locally and manually verify the inbox renders:

```bash
uv run uvicorn bidequity.main:app --port 8000 --reload
# Open http://localhost:8000/inbox in a browser
```

- [ ] Verify the following manually:
  - Inbox loads without error (empty state message if no drafts, table if seed data exists)
  - Navigation links highlight the active page
  - Sources page renders the health-dot column
  - Insights page renders the stats grid

- [ ] Verify HTMX CDN is reachable and the `hx-post` attributes are present in the rendered inbox HTML (view source on the inbox page).

- [ ] Verify keyboard shortcuts are wired (open inbox, press `J` — check browser console for Alpine errors).

**Commit:** `chore: ticket-7 dashboard complete; all tests pass`

---

## Acceptance Criteria

| Criterion | How to verify |
|---|---|
| Paul can triage 20 items in < 10 minutes | Open inbox with 20 pending drafts; time complete triage using keyboard shortcuts |
| Approve / reject / edit / save update database immediately | After each action, query `drafts` table directly — status is correct |
| Editing updates persist | Approve via edit modal; check `drafts.linkedin_post` and `editorial_actions` in Postgres |
| Mobile view works | Open `/inbox` on a phone or at 375px viewport width; action buttons are visible and tappable |
| Keyboard shortcuts functional | In inbox, press `J`/`K` to navigate rows; `A` fires the Approve HTMX call for the focused row |
| Sunday digest sends correctly | Call `send_weekly_digest(session)` in a REPL with seeded draft data; verify email arrives |
| All route tests pass | `uv run pytest tests/test_dashboard/ -v` — all green |

---

## Implementation Notes

**HTMX row swap pattern.** Each `<tr>` carries `id="draft-{id}"` and `hx-swap="outerHTML"` on the row itself. Action buttons inside the row use `hx-target="closest tr"` and `hx-post` pointing to the relevant endpoint. The endpoint returns a replacement `<tr>` fragment — either the approved, rejected, or pending-state partial. This is the minimal HTMX pattern for row-level mutation without a full page reload.

**AlpineJS keyboard handler.** The `x-data` block lives on the `<div>` wrapping `<main>`, giving it access to the entire page DOM. It maintains a `focused_id` and a `row_ids` array, rebuilt after each HTMX swap via the `hx-on::after-swap` hook on the `<tbody>`. When a keyboard shortcut fires, it queries the focused row's button by `data-action` attribute and programmatically clicks it, which triggers the HTMX request normally.

**Edit modal pattern.** Pressing `E` (or clicking Edit) calls `GET /drafts/{id}/edit-modal`, which returns a replacement `<tr>` containing a full-page overlay modal. Submitting the form posts to `POST /drafts/{id}/edit` and returns the approved-state `<tr>` partial, which HTMX swaps back in, collapsing the modal. Pressing Escape calls `htmx.ajax('GET', '/inbox-row/{id}', ...)` to restore the pending-state row without persisting changes.

**SQLite in tests.** The conftest uses SQLite in-memory via `StaticPool` for test isolation. The `ARRAY(TEXT)` columns in `Classification` (sectors, buyers_mentioned, etc.) are defined with explicit `sa_column=Column(ARRAY(TEXT))` using PostgreSQL's ARRAY type. In SQLite test runs, these columns fall back to JSON-serialised text — acceptable for route tests that only check status codes and basic string presence. If array-column behaviour must be tested exactly, use a real Postgres test database via `pytest-postgresql`.

**Digest SMTP.** Cloudflare Email Routing provides a free SMTP relay at `smtp.cloudflare.net:587` with STARTTLS. The `SMTP_USER` is the From address; the `SMTP_PASSWORD` is the app-specific token generated in the Cloudflare Email dashboard. No outbound email service subscription is required at Phase 1 volumes.
