# BidEquity Newsroom — Ticket 8: LinkedIn Publishing

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the full LinkedIn publishing path — OAuth setup, token refresh, post formatter, publishing worker, retry logic, and scheduler integration — so that a draft approved in the editorial dashboard publishes to the BidEquity company page on schedule and surfaces failures back to the operator.

**Architecture:** A `LinkedInClient` makes authenticated `POST /v2/ugcPosts` calls using a stored OAuth 2.0 access token. The token is persisted in a `linkedin_tokens` table and refreshed by a background job 24 hours before expiry. A `publish_scheduled` APScheduler job polls every 15 minutes for publications due to go out on the `linkedin` channel, calls the formatter then the client, and updates `publications.status` to `published` (or `failed` after three retries). The one-time OAuth setup flow is handled by two FastAPI routes that Caddy blocks in production after first use.

**Tech Stack:** LinkedIn Marketing Developer Platform API (v2), OAuth 2.0, httpx, APScheduler

---

## File Map

```
bidequity-newsroom/
├── src/bidequity/
│   ├── models/
│   │   └── linkedin_token.py              # SQLModel: LinkedInToken table
│   ├── publish/
│   │   ├── __init__.py                    # package marker
│   │   ├── formatter.py                   # format_linkedin_post(draft) -> str
│   │   ├── linkedin.py                    # LinkedInClient + refresh_token_if_needed
│   │   └── linkedin_oauth.py              # /auth/linkedin + /auth/linkedin/callback routes
│   └── ingest/
│       └── scheduler.py                   # add publish_scheduled job (already exists; extend it)
├── alembic/versions/
│   └── XXXX_add_linkedin_tokens.py        # migration: linkedin_tokens table
└── tests/
    └── test_publish/
        ├── __init__.py                    # package marker
        └── test_linkedin.py               # all LinkedIn publishing tests
```

---

## Tasks

### Task 1 — Write the failing tests

> TDD: all tests must exist and fail (or be skipped) before any production code is written.

**Files:** `bidequity-newsroom/tests/test_publish/__init__.py`, `bidequity-newsroom/tests/test_publish/test_linkedin.py`

- [ ] Create `bidequity-newsroom/tests/test_publish/__init__.py` (empty).

- [ ] Create `bidequity-newsroom/tests/test_publish/test_linkedin.py`:

```python
"""Tests for LinkedIn formatter and publisher."""

from __future__ import annotations

import pytest
import httpx
import respx  # pytest plugin for mocking httpx

from bidequity.publish.formatter import format_linkedin_post
from bidequity.publish.linkedin import LinkedInClient


# ---------------------------------------------------------------------------
# Formatter tests
# ---------------------------------------------------------------------------

class _MockDraft:
    """Minimal draft-like object for formatter tests."""

    def __init__(self, linkedin_post: str) -> None:
        self.linkedin_post = linkedin_post


def test_format_strips_em_dashes() -> None:
    draft = _MockDraft("First line\n\nThe MOD — as expected — confirmed.")
    result = format_linkedin_post(draft)
    assert "\u2014" not in result
    assert " - " in result


def test_format_double_line_breaks() -> None:
    """Single newlines between paragraphs must become double newlines."""
    draft = _MockDraft("Paragraph one\nParagraph two")
    result = format_linkedin_post(draft)
    assert "\n\n" in result


def test_format_preserves_existing_double_line_breaks() -> None:
    draft = _MockDraft("Para one\n\nPara two")
    result = format_linkedin_post(draft)
    # Must not become triple-newlines
    assert "\n\n\n" not in result


def test_format_enforces_max_3000_chars() -> None:
    long_text = "A" * 100 + ". " + ("Word sentence here. " * 200)
    draft = _MockDraft(long_text)
    result = format_linkedin_post(draft)
    assert len(result) <= 3000


def test_format_truncates_at_sentence_boundary() -> None:
    # Build a post that is just over 3000 chars, with a sentence ending before the limit
    sentences = ["This is sentence number {:03d}. ".format(i) for i in range(120)]
    long_text = "".join(sentences)
    assert len(long_text) > 3000
    draft = _MockDraft(long_text)
    result = format_linkedin_post(draft)
    assert len(result) <= 3000
    # Result must end cleanly (at a sentence boundary, possibly with ellipsis)
    assert result.endswith(".") or result.endswith("...") or result.endswith(".\n")


def test_format_short_post_unchanged_length() -> None:
    text = "Hook line.\n\nMain point one.\n\nMain point two.\n\n#PublicSector #BidEquity"
    draft = _MockDraft(text)
    result = format_linkedin_post(draft)
    # Short text should not be padded or truncated
    assert len(result) <= len(text) + 10  # allow minor whitespace normalisation


# ---------------------------------------------------------------------------
# LinkedInClient tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@respx.mock
async def test_post_sends_correct_ugcposts_payload() -> None:
    """Client must POST to /v2/ugcPosts with the correct ugcPosts payload shape."""
    org_urn = "urn:li:organization:12345"
    post_text = "Hook line.\n\nMain body. #BidEquity"
    fake_urn = "urn:li:ugcPost:987654321"

    # Mock the LinkedIn API endpoint
    route = respx.post("https://api.linkedin.com/v2/ugcPosts").mock(
        return_value=httpx.Response(201, json={"id": fake_urn})
    )

    client = LinkedInClient(access_token="fake-token", org_urn=org_urn)
    returned_urn = await client.post(post_text)

    assert route.called
    assert returned_urn == fake_urn

    # Verify payload structure
    sent_payload = route.calls[0].request
    import json
    body = json.loads(sent_payload.content)

    assert body["author"] == org_urn
    assert body["lifecycleState"] == "PUBLISHED"
    content = body["specificContent"]["com.linkedin.ugc.ShareContent"]
    assert content["shareCommentary"]["text"] == post_text
    assert content["shareMediaCategory"] == "NONE"
    assert body["visibility"]["com.linkedin.ugc.MemberNetworkVisibility"] == "PUBLIC"


@pytest.mark.asyncio
@respx.mock
async def test_post_raises_on_non_201() -> None:
    """Client must raise an exception when LinkedIn returns a non-201 status."""
    respx.post("https://api.linkedin.com/v2/ugcPosts").mock(
        return_value=httpx.Response(422, json={"message": "Validation failed"})
    )

    client = LinkedInClient(access_token="fake-token", org_urn="urn:li:organization:1")
    with pytest.raises(Exception, match="422"):
        await client.post("Some post text.")


@pytest.mark.asyncio
@respx.mock
async def test_post_retry_succeeds_on_second_attempt() -> None:
    """Client must retry on 500 and succeed on subsequent attempt."""
    org_urn = "urn:li:organization:12345"
    fake_urn = "urn:li:ugcPost:111"

    # First call returns 500, second returns 201
    route = respx.post("https://api.linkedin.com/v2/ugcPosts").mock(
        side_effect=[
            httpx.Response(500, json={"message": "Internal Server Error"}),
            httpx.Response(201, json={"id": fake_urn}),
        ]
    )

    client = LinkedInClient(access_token="fake-token", org_urn=org_urn)
    returned_urn = await client.post("Some text.", max_retries=3, retry_delay=0)

    assert returned_urn == fake_urn
    assert route.call_count == 2
```

- [ ] Add `respx` to dev dependencies in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.2",
    "pytest-asyncio>=0.23",
    "ruff>=0.4",
    "mypy>=1.10",
    "respx>=0.21",
]
```

- [ ] Run `uv sync` to install `respx`.

- [ ] Run the tests to confirm they fail with `ModuleNotFoundError` (expected at this point — production code does not exist yet):

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/test_publish/ -v 2>&1 | head -40
```

Expected: all tests collected, failing with `ImportError` or `ModuleNotFoundError`.

**Commit:** `test: add failing LinkedIn formatter and publisher tests (TDD anchor)`

---

### Task 2 — LinkedInToken data model

**Files:** `bidequity-newsroom/src/bidequity/models/linkedin_token.py`

- [ ] Create `bidequity-newsroom/src/bidequity/models/__init__.py` if it does not exist (empty).

- [ ] Create `bidequity-newsroom/src/bidequity/models/linkedin_token.py`:

```python
"""SQLModel definition for the linkedin_tokens table."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class LinkedInToken(SQLModel, table=True):
    """
    Stores the current LinkedIn OAuth 2.0 token for the BidEquity company page.

    There will normally be exactly one row in this table. The OAuth setup route
    upserts on id=1. The refresh job overwrites in place.
    """

    __tablename__ = "linkedin_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    access_token: str = Field(nullable=False)
    refresh_token: str = Field(nullable=False)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

- [ ] Wire the import into `alembic/env.py` so Alembic can detect the new table. Add the import below the existing model imports comment:

```python
from bidequity.models.linkedin_token import LinkedInToken  # noqa: F401
```

- [ ] Generate the Alembic migration:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run alembic revision --autogenerate -m "add_linkedin_tokens"
```

- [ ] Inspect the generated migration file. It should contain a `CREATE TABLE linkedin_tokens` statement with columns `id`, `access_token`, `refresh_token`, `expires_at`, `created_at`, `updated_at`. Verify and, if needed, adjust the migration so it is clean.

- [ ] Apply the migration to the local database:

```bash
uv run alembic upgrade head
```

Expected: `Running upgrade ... -> XXXX_add_linkedin_tokens, add_linkedin_tokens`

**Commit:** `feat: LinkedInToken SQLModel + Alembic migration`

---

### Task 3 — LinkedIn formatter

**Files:** `bidequity-newsroom/src/bidequity/publish/__init__.py`, `bidequity-newsroom/src/bidequity/publish/formatter.py`

- [ ] Create `bidequity-newsroom/src/bidequity/publish/__init__.py` (empty).

- [ ] Create `bidequity-newsroom/src/bidequity/publish/formatter.py`:

```python
"""
LinkedIn post formatter.

Transforms a raw Draft into a LinkedIn-ready string:
  - Replaces em-dashes (U+2014) with ' - '
  - Normalises paragraph breaks to double newlines (LinkedIn collapses single ones)
  - Truncates at sentence boundary if the post exceeds MAX_CHARS
"""

from __future__ import annotations

import re

MAX_CHARS = 3000
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def format_linkedin_post(draft: object) -> str:
    """
    Format a draft object's linkedin_post field for publishing.

    Args:
        draft: Any object with a ``linkedin_post`` attribute (matches
               the SQLModel Draft shape used by the app, but kept duck-typed
               so formatter tests can use simple stubs).

    Returns:
        A LinkedIn-ready string, max MAX_CHARS characters.
    """
    text: str = getattr(draft, "linkedin_post", "")

    # 1. Replace em-dashes with ' - '
    text = text.replace("\u2014", " - ")

    # 2. Normalise line breaks.
    #    Collapse runs of 3+ newlines → 2 newlines.
    #    Convert isolated single newlines (not already adjacent to another \n) → \n\n.
    #    Order matters: collapse first to avoid creating unintended doubles.
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", "\n\n", text)

    # 3. Strip leading/trailing whitespace
    text = text.strip()

    # 4. Enforce max length, truncating at a sentence boundary
    if len(text) > MAX_CHARS:
        text = _truncate_at_sentence(text, MAX_CHARS)

    return text


def _truncate_at_sentence(text: str, limit: int) -> str:
    """
    Truncate *text* to at most *limit* characters, ending at a sentence boundary.

    Tries to find the last sentence-ending punctuation (. ! ?) at or before the
    limit. If none is found (very long first sentence), hard-truncates and appends
    '...'.
    """
    # Walk backwards from the limit looking for a sentence end
    window = text[:limit]
    # Find the last occurrence of '.', '!', or '?' in the window
    last_end = max(
        window.rfind("."),
        window.rfind("!"),
        window.rfind("?"),
    )

    if last_end != -1:
        return text[: last_end + 1]

    # No sentence boundary found — hard truncate with ellipsis
    return window.rstrip() + "..."
```

- [ ] Run the formatter tests:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/test_publish/test_linkedin.py -k "format" -v
```

Expected: all `test_format_*` tests pass.

**Commit:** `feat: LinkedIn post formatter with em-dash removal, line break normalisation, truncation`

---

### Task 4 — LinkedInClient and token refresh

**Files:** `bidequity-newsroom/src/bidequity/publish/linkedin.py`

- [ ] Create `bidequity-newsroom/src/bidequity/publish/linkedin.py`:

```python
"""
LinkedIn publishing client and token refresh helper.

LinkedInClient wraps the LinkedIn UGC Posts API (v2). It accepts an access token
at construction time; token lifecycle management is handled externally by
refresh_token_if_needed().

Usage:
    token = await refresh_token_if_needed(config, session)
    client = LinkedInClient(access_token=token, org_urn=config.LINKEDIN_ORG_URN)
    urn = await client.post(formatted_text)
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from bidequity.common.config import Config
from bidequity.models.linkedin_token import LinkedInToken

logger = logging.getLogger(__name__)

_LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


class LinkedInClient:
    BASE_URL = "https://api.linkedin.com/v2"

    def __init__(self, access_token: str, org_urn: str) -> None:
        self._access_token = access_token
        self._org_urn = org_urn

    async def post(
        self,
        text: str,
        *,
        max_retries: int = 3,
        retry_delay: float = 300.0,  # 5 minutes in seconds
    ) -> str:
        """
        Publish *text* as a post on the BidEquity LinkedIn company page.

        Retries up to *max_retries* times on 5xx responses, waiting
        *retry_delay* seconds between attempts.

        Args:
            text: The formatted post body (must already be within LinkedIn limits).
            max_retries: Maximum total attempts (default 3).
            retry_delay: Seconds to wait between retries (default 300 = 5 min).

        Returns:
            The LinkedIn post URN (e.g. ``"urn:li:ugcPost:123456789"``).

        Raises:
            LinkedInAPIError: On non-retryable errors or after exhausting retries.
        """
        payload = {
            "author": self._org_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        last_exc: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/ugcPosts",
                        json=payload,
                        headers=headers,
                    )

                if response.status_code == 201:
                    data = response.json()
                    urn: str = data["id"]
                    logger.info("LinkedIn post published: %s", urn)
                    return urn

                # 5xx: retryable
                if response.status_code >= 500 and attempt < max_retries:
                    logger.warning(
                        "LinkedIn API %s on attempt %d/%d — retrying in %.0fs",
                        response.status_code,
                        attempt,
                        max_retries,
                        retry_delay,
                    )
                    if retry_delay > 0:
                        await asyncio.sleep(retry_delay)
                    continue

                # 4xx or final 5xx: non-retryable
                raise LinkedInAPIError(
                    f"LinkedIn API returned {response.status_code}: {response.text}"
                )

            except httpx.RequestError as exc:
                last_exc = exc
                if attempt < max_retries:
                    logger.warning(
                        "LinkedIn request error on attempt %d/%d: %s — retrying",
                        attempt,
                        max_retries,
                        exc,
                    )
                    if retry_delay > 0:
                        await asyncio.sleep(retry_delay)
                    continue
                raise LinkedInAPIError(f"Network error after {max_retries} attempts: {exc}") from exc

        raise LinkedInAPIError(
            f"LinkedIn post failed after {max_retries} attempts"
        ) from last_exc


class LinkedInAPIError(Exception):
    """Raised when the LinkedIn API returns an error that cannot be retried."""


async def refresh_token_if_needed(config: Config, session: AsyncSession) -> str:
    """
    Return the current LinkedIn access token, refreshing it first if it expires
    within 24 hours.

    The token is read from and written back to the ``linkedin_tokens`` table.
    There must be exactly one row in that table (inserted by the OAuth setup flow).

    Args:
        config: Application config (needs LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET).
        session: An active async database session.

    Returns:
        A valid access token string.

    Raises:
        LinkedInTokenError: If no token exists or the refresh call fails.
    """
    result = await session.exec(select(LinkedInToken).limit(1))
    token_row = result.first()

    if token_row is None:
        raise LinkedInTokenError(
            "No LinkedIn token found. Run the OAuth setup flow at /auth/linkedin."
        )

    now = datetime.now(tz=timezone.utc)
    expiry_threshold = now + timedelta(hours=24)

    if token_row.expires_at.replace(tzinfo=timezone.utc) > expiry_threshold:
        # Token is still fresh — return as-is
        logger.debug("LinkedIn token valid until %s — no refresh needed", token_row.expires_at)
        return token_row.access_token

    # Token is expiring within 24h — refresh it
    logger.info("LinkedIn token expiring at %s — refreshing", token_row.expires_at)

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            _LINKEDIN_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": token_row.refresh_token,
                "client_id": config.LINKEDIN_CLIENT_ID,
                "client_secret": config.LINKEDIN_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        raise LinkedInTokenError(
            f"Token refresh failed with HTTP {response.status_code}: {response.text}"
        )

    data = response.json()
    new_access_token: str = data["access_token"]
    expires_in_seconds: int = data.get("expires_in", 5183944)  # ~60 days default
    new_refresh_token: str = data.get("refresh_token", token_row.refresh_token)
    new_expiry = now + timedelta(seconds=expires_in_seconds)

    # Update the token row in place
    token_row.access_token = new_access_token
    token_row.refresh_token = new_refresh_token
    token_row.expires_at = new_expiry
    token_row.updated_at = now
    session.add(token_row)
    await session.commit()
    await session.refresh(token_row)

    logger.info("LinkedIn token refreshed; new expiry: %s", new_expiry)
    return new_access_token


class LinkedInTokenError(Exception):
    """Raised when the LinkedIn token is missing or cannot be refreshed."""
```

- [ ] Run all LinkedIn tests:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/test_publish/ -v
```

Expected: all tests pass.

- [ ] Run ruff and mypy on the new module:

```bash
uv run ruff check src/bidequity/publish/linkedin.py
uv run mypy src/bidequity/publish/linkedin.py
```

**Commit:** `feat: LinkedInClient with ugcPosts publish + retry; refresh_token_if_needed`

---

### Task 5 — OAuth setup routes

**Files:** `bidequity-newsroom/src/bidequity/publish/linkedin_oauth.py`

These routes exist only for the one-time OAuth token exchange. In production, Caddy can be configured to block `/auth/linkedin*` after setup is complete (see notes below).

- [ ] Create `bidequity-newsroom/src/bidequity/publish/linkedin_oauth.py`:

```python
"""
LinkedIn OAuth 2.0 setup routes.

Two routes handle the one-time OAuth flow for the BidEquity company page:

  GET /auth/linkedin           — redirects the operator to LinkedIn's authorisation URL
  GET /auth/linkedin/callback  — exchanges the code for tokens and stores them

Required OAuth app scopes:
  - w_member_social            (post on behalf of a member — used for org posts)
  - r_organization_social      (read org's social actions)
  - w_organization_social      (post on behalf of an organisation)

After completing the flow once:
  - Add the following block to the Caddyfile to block these routes in production:
      @oauth_setup path /auth/linkedin /auth/linkedin/callback
      respond @oauth_setup 403

These routes are safe to leave in the codebase — they are blocked at the proxy
layer after first use, not removed.
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from bidequity.common.config import Config, get_config
from bidequity.common.db import get_session
from bidequity.models.linkedin_token import LinkedInToken

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["oauth"])

_LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
_LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
_REQUIRED_SCOPES = "w_member_social r_organization_social w_organization_social"

# Simple in-process state store for CSRF protection (single-operator, single server).
# Cleared after each successful exchange.
_pending_states: set[str] = set()


def _callback_url(request: Request) -> str:
    """Build the callback URL from the incoming request's base URL."""
    base = str(request.base_url).rstrip("/")
    return f"{base}/auth/linkedin/callback"


@router.get("/linkedin", response_class=RedirectResponse)
async def linkedin_auth_start(
    request: Request,
    config: Config = Depends(get_config),
) -> RedirectResponse:
    """
    Step 1: Redirect operator to LinkedIn's OAuth authorisation page.

    Visit this URL in a browser while the app is running locally.
    """
    state = secrets.token_urlsafe(32)
    _pending_states.add(state)

    params = {
        "response_type": "code",
        "client_id": config.LINKEDIN_CLIENT_ID,
        "redirect_uri": _callback_url(request),
        "state": state,
        "scope": _REQUIRED_SCOPES,
    }
    auth_url = f"{_LINKEDIN_AUTH_URL}?{urlencode(params)}"
    logger.info("Redirecting to LinkedIn OAuth: %s", auth_url)
    return RedirectResponse(url=auth_url)


@router.get("/linkedin/callback", response_class=HTMLResponse)
async def linkedin_auth_callback(
    code: str,
    state: str,
    request: Request,
    config: Config = Depends(get_config),
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    """
    Step 2: Exchange authorisation code for tokens and store them.

    LinkedIn redirects here after the operator grants access.
    """
    # CSRF check
    if state not in _pending_states:
        raise HTTPException(status_code=400, detail="Invalid OAuth state — possible CSRF attack.")
    _pending_states.discard(state)

    # Exchange code for tokens
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            _LINKEDIN_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": _callback_url(request),
                "client_id": config.LINKEDIN_CLIENT_ID,
                "client_secret": config.LINKEDIN_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        logger.error("LinkedIn token exchange failed: %s", response.text)
        raise HTTPException(
            status_code=502,
            detail=f"LinkedIn token exchange failed: {response.status_code}",
        )

    data = response.json()
    access_token: str = data["access_token"]
    refresh_token: str = data.get("refresh_token", "")
    expires_in: int = data.get("expires_in", 5183944)  # ~60 days
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)

    # Upsert: there is at most one token row (id=1)
    token = LinkedInToken(
        id=1,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        updated_at=datetime.now(tz=timezone.utc),
    )
    await session.merge(token)
    await session.commit()

    logger.info("LinkedIn OAuth complete. Token stored; expires %s.", expires_at)

    return HTMLResponse(
        content="""
        <html><body style="font-family:sans-serif;padding:2rem">
        <h2>LinkedIn OAuth complete</h2>
        <p>Access token stored successfully. This page is safe to close.</p>
        <p><strong>Next step:</strong> Block these routes in your Caddyfile:
        <pre>@oauth_setup path /auth/linkedin /auth/linkedin/callback
respond @oauth_setup 403</pre>
        </p>
        </body></html>
        """,
        status_code=200,
    )
```

- [ ] Register the OAuth router in `main.py`. Add the import and `include_router` call inside `create_app()`:

```python
from bidequity.publish.linkedin_oauth import router as linkedin_oauth_router

def create_app() -> FastAPI:
    app = FastAPI(title="BidEquity Newsroom", version="0.1.0", lifespan=lifespan)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(linkedin_oauth_router)

    return app
```

- [ ] Run the full test suite to confirm no regressions:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/ -v
```

Expected: all existing tests still pass; no new failures.

- [ ] Run ruff and mypy on the new module:

```bash
uv run ruff check src/bidequity/publish/linkedin_oauth.py
uv run mypy src/bidequity/publish/linkedin_oauth.py
```

**Commit:** `feat: LinkedIn OAuth setup routes (/auth/linkedin + /auth/linkedin/callback)`

---

### Task 6 — Publishing scheduler job

**Files:** `bidequity-newsroom/src/bidequity/ingest/scheduler.py` (extend existing file)

The scheduler already exists from Ticket 3/4. This task adds the `publish_scheduled` job.

- [ ] Open `bidequity-newsroom/src/bidequity/ingest/scheduler.py` and add the following job function and registration. Add the import block at the top and the job function + registration where the other jobs are registered:

**Imports to add (merge into existing imports):**

```python
import logging
from datetime import datetime, timezone

import sentry_sdk
from sqlmodel import select

from bidequity.common.config import get_config
from bidequity.common.db import get_session
from bidequity.models.linkedin_token import LinkedInToken  # noqa: F401 (referenced via session)
from bidequity.publish.formatter import format_linkedin_post
from bidequity.publish.linkedin import LinkedInClient, LinkedInAPIError, LinkedInTokenError, refresh_token_if_needed

logger = logging.getLogger(__name__)

_MAX_PUBLISH_RETRIES = 3
_ALERT_CHANNEL = "dashboard"  # placeholder — replace with email/Sentry alert when wired
```

**Job function to add:**

```python
async def publish_scheduled() -> None:
    """
    Pick up publications due for LinkedIn and send them.

    Runs every 15 minutes. For each publication WHERE:
      - channel = 'linkedin'
      - status = 'scheduled'
      - scheduled_for <= now()

    1. Loads the associated draft.
    2. Formats the post via format_linkedin_post().
    3. Posts to LinkedIn via LinkedInClient.
    4. On success: sets status='published', external_id=urn, published_at=now().
    5. On failure: increments a retry counter (stored in publications.raw_metadata).
       After MAX_PUBLISH_RETRIES failures: sets status='failed' and captures to Sentry.
    """
    # Import here to avoid circular imports at module load time
    from bidequity.models.publication import Publication  # type: ignore[import]
    from bidequity.models.draft import Draft  # type: ignore[import]

    config = get_config()
    now = datetime.now(tz=timezone.utc)

    async for session in get_session():
        # Fetch due LinkedIn publications
        stmt = (
            select(Publication)
            .where(Publication.channel == "linkedin")
            .where(Publication.status == "scheduled")
            .where(Publication.scheduled_for <= now)
        )
        result = await session.exec(stmt)
        due = result.all()

        if not due:
            return

        logger.info("publish_scheduled: %d publication(s) due", len(due))

        # Refresh the token once per run (not per post)
        try:
            access_token = await refresh_token_if_needed(config, session)
        except LinkedInTokenError as exc:
            logger.error("Cannot publish — LinkedIn token unavailable: %s", exc)
            sentry_sdk.capture_exception(exc)
            return

        client = LinkedInClient(
            access_token=access_token,
            org_urn=config.LINKEDIN_ORG_URN,
        )

        for pub in due:
            # Determine how many times we've already attempted this publication
            raw_meta: dict = pub.raw_metadata or {}  # type: ignore[assignment]
            attempt_count: int = raw_meta.get("publish_attempts", 0)

            if attempt_count >= _MAX_PUBLISH_RETRIES:
                # Already failed the maximum number of times; mark failed
                pub.status = "failed"
                session.add(pub)
                await session.commit()
                logger.error(
                    "Publication %d marked failed after %d attempts",
                    pub.id,
                    attempt_count,
                )
                sentry_sdk.capture_message(
                    f"LinkedIn publication {pub.id} failed after {attempt_count} attempts",
                    level="error",
                )
                continue

            # Load the draft to format the post
            draft_result = await session.exec(
                select(Draft).where(Draft.id == pub.draft_id)  # type: ignore[arg-type]
            )
            draft = draft_result.first()
            if draft is None:
                logger.error("Publication %d has no associated draft — skipping", pub.id)
                continue

            formatted_text = format_linkedin_post(draft)

            try:
                urn = await client.post(
                    formatted_text,
                    max_retries=1,   # outer retry loop handles multi-attempt backoff
                    retry_delay=0,
                )
                pub.status = "published"
                pub.external_id = urn
                pub.published_at = datetime.now(tz=timezone.utc)
                pub.raw_metadata = {**raw_meta, "publish_attempts": attempt_count + 1}
                session.add(pub)
                await session.commit()
                logger.info("Publication %d published as %s", pub.id, urn)

            except LinkedInAPIError as exc:
                attempt_count += 1
                pub.raw_metadata = {**raw_meta, "publish_attempts": attempt_count}

                if attempt_count >= _MAX_PUBLISH_RETRIES:
                    pub.status = "failed"
                    sentry_sdk.capture_exception(exc)
                    logger.error(
                        "Publication %d failed permanently after %d attempts: %s",
                        pub.id,
                        attempt_count,
                        exc,
                    )
                else:
                    logger.warning(
                        "Publication %d attempt %d/%d failed: %s — will retry",
                        pub.id,
                        attempt_count,
                        _MAX_PUBLISH_RETRIES,
                        exc,
                    )

                session.add(pub)
                await session.commit()
```

**Registration (add to the scheduler setup function where other jobs are registered):**

```python
scheduler.add_job(
    publish_scheduled,
    trigger="interval",
    minutes=15,
    id="publish_scheduled",
    replace_existing=True,
    misfire_grace_time=300,
)
logger.info("publish_scheduled job registered (every 15 minutes)")
```

- [ ] Run the full test suite to confirm no regressions:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run pytest tests/ -v
```

- [ ] Run ruff and mypy:

```bash
uv run ruff check src/bidequity/ingest/scheduler.py
uv run mypy src/bidequity/ingest/scheduler.py
```

**Commit:** `feat: publish_scheduled APScheduler job — LinkedIn 15-min poll with retry and Sentry alert`

---

### Task 7 — End-to-end smoke test (manual, no API call)

> This is a manual verification step, not an automated test. Its purpose is to confirm the wiring compiles and the scheduler registers without crashing the app.

- [ ] Start the FastAPI app locally:

```bash
cd c:/Users/User/Documents/GitHub/PWIN/bidequity-newsroom
uv run uvicorn bidequity.main:app --port 8000 --reload
```

- [ ] Confirm the app starts without import errors.

- [ ] Confirm `/healthz` still returns 200:

```bash
curl -s http://localhost:8000/healthz
```

Expected: `{"status":"ok"}`

- [ ] Confirm the OAuth routes are registered:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/auth/linkedin
```

Expected: `307` (redirect to LinkedIn) or `422` if `LINKEDIN_CLIENT_ID` is empty — both confirm the route is registered. A `404` means the router was not wired in.

- [ ] Stop the app with Ctrl-C.

- [ ] Run the full test suite one final time:

```bash
uv run pytest tests/ -v
```

Expected: all tests pass.

- [ ] Run the full linting and type-check pass:

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
```

Expected: no errors.

**Commit:** `chore: ticket-8 LinkedIn publishing complete; all tests pass`

---

## Acceptance Criteria

| Criterion | How to verify |
|---|---|
| A test draft approved in dashboard publishes to BidEquity company page on schedule | Run OAuth flow at `/auth/linkedin`, approve a draft in the dashboard, observe the `publish_scheduled` job fire within 15 minutes, check `publications.status = 'published'` and `external_id` set to a LinkedIn URN |
| Formatter strips em-dashes | `uv run pytest tests/test_publish/test_linkedin.py::test_format_strips_em_dashes -v` passes |
| Formatter enforces max 3000 chars at sentence boundary | `uv run pytest tests/test_publish/test_linkedin.py::test_format_enforces_max_3000_chars -v` passes |
| Formatter normalises double line breaks | `uv run pytest tests/test_publish/test_linkedin.py::test_format_double_line_breaks -v` passes |
| Publisher sends correct ugcPosts payload | `uv run pytest tests/test_publish/test_linkedin.py::test_post_sends_correct_ugcposts_payload -v` passes |
| Retry succeeds on second attempt after 500 | `uv run pytest tests/test_publish/test_linkedin.py::test_post_retry_succeeds_on_second_attempt -v` passes |
| Failure case surfaces in dashboard | After 3 failed publish attempts, `publications.status = 'failed'` and Sentry captures the error |
| OAuth routes registered | `curl http://localhost:8000/auth/linkedin` returns 307 (redirect) or 422 (missing config) — not 404 |
| Token refresh runs proactively | With a token expiring in < 24h, `refresh_token_if_needed()` calls the LinkedIn token endpoint and updates the DB row |

---

## Production Notes

### Blocking OAuth routes after setup

After the initial OAuth flow completes, add this block to the Caddyfile to prevent the setup routes being accessible in production:

```caddy
newsroom.bidequity.co.uk {
    @oauth_setup path /auth/linkedin /auth/linkedin/callback
    respond @oauth_setup 403

    basicauth * {
        {$DASHBOARD_USERNAME} {$DASHBOARD_PASSWORD_HASH}
    }
    reverse_proxy localhost:8000
}
```

### LinkedIn app configuration

In the LinkedIn Developer portal (`developer.linkedin.com`):
- Create an app associated with the BidEquity company page
- Add product: **Marketing Developer Platform** (enables `w_organization_social`)
- Set Authorised redirect URL to `https://newsroom.bidequity.co.uk/auth/linkedin/callback`
- Note the Client ID and Client Secret into `.env` as `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`
- Set `LINKEDIN_ORG_URN` to `urn:li:organization:<id>` (find the org ID at `linkedin.com/company/bidequity/admin`)

### Token lifetime

LinkedIn access tokens issued via the Marketing Developer Platform expire after approximately 60 days. The refresh job handles this automatically. If the refresh token itself expires (rare; typically 365 days), the OAuth flow must be re-run once.
