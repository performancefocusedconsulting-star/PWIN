# BidEquity Newsroom — Ticket 4: Scrapers, Embeddings & Semantic Dedupe

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the ingest pipeline with static and JS scrapers for sources without RSS feeds, add Voyage embedding generation for all ingested items, and implement semantic duplicate detection via pgvector so that near-identical items are flagged before reaching the classifier.

**Architecture:** Two new `feed_type` handlers (`scrape_static` via httpx + selectolax, `scrape_js` via Playwright) live alongside the Ticket 3 RSS/API handlers and dispatch from the same scheduler. A background embedding worker batches unembedded items every 30 minutes and writes 1024-dimensional Voyage vectors into `items.embedding`. A semantic dedupe job then runs kNN queries (k=3, cosine distance < 0.06) over recently ingested items against the full corpus and sets a new `semantic_duplicate` boolean flag; flagged items are retained for audit but skipped by the classifier. Dead source detection is added to the scheduler as a daily 09:00 UTC job that emails an alert for any `active=true` source with no new items in 14 days.

**Tech Stack:** selectolax, Playwright, httpx, pdfplumber, Voyage API (`voyage-3-lite`), pgvector, APScheduler

> **Note:** The source map contains 28 Web/PDF sources. An audit action exists (`wiki/actions/bidequity-newsroom-source-map-audit.md`) to classify each by actual ingest method before implementing scrapers. The recommended approach is to start with the 84 RSS/API sources and add scrapers one at a time. The `scrape_pdf` handler below is required because high-signal sources (NAO reports, committee publications, departmental ARAs) publish as PDF — these are not optional.

---

## File Map

| File | Description |
|---|---|
| `bidequity-newsroom/src/bidequity/ingest/handlers/scrape_static.py` | Static HTML scraper: httpx + selectolax, CSS selectors from `source.notes` JSONB |
| `bidequity-newsroom/src/bidequity/ingest/handlers/scrape_js.py` | Playwright JS scraper: browser reused, context per source, same selector config pattern |
| `bidequity-newsroom/src/bidequity/ingest/handlers/scrape_pdf.py` | PDF scraper: httpx download + pdfplumber text extraction, feed_type='scrape_pdf' |
| `bidequity-newsroom/src/bidequity/ingest/dedupe.py` | `embed_pending_items()` and `flag_semantic_duplicates()` — embedding worker + semantic dedupe |
| `bidequity-newsroom/src/bidequity/ingest/scheduler.py` | Extend existing scheduler with `check_dead_sources()` job (daily 09:00 UTC) |
| `bidequity-newsroom/alembic/versions/0002_add_semantic_duplicate.py` | Alembic migration: add `semantic_duplicate BOOLEAN NOT NULL DEFAULT false` to `items` |
| `bidequity-newsroom/tests/test_ingest/test_scrape_static.py` | Unit tests: mock httpx + selectolax responses, assert `ItemCreate` fields |
| `bidequity-newsroom/tests/test_ingest/test_scrape_js.py` | Unit tests: mock Playwright page, assert `ItemCreate` fields |
| `bidequity-newsroom/tests/test_ingest/test_scrape_pdf.py` | Unit tests: mock httpx download + pdfplumber extraction, assert body_text populated |
| `bidequity-newsroom/tests/test_ingest/test_dedupe.py` | Unit tests: exact-hash dedupe (covered in Ticket 3), embedding worker, semantic dedupe flag |

---

## Tasks

### Task 1 — Write failing tests for `scrape_static` handler

- [ ] Create `bidequity-newsroom/tests/test_ingest/test_scrape_static.py`
- [ ] Import `pytest`, `pytest-asyncio`, `respx` (httpx mock), and `ItemCreate` from `bidequity.models`
- [ ] Write `test_fetch_returns_item_list`: mock two HTML responses — the listing page and one article body page — assert that `fetch()` returns a `list[ItemCreate]` with `title`, `url`, `body_text`, and `published_at` populated
- [ ] Write `test_missing_date_selector_sets_published_at_none`: provide a selector config without `date_selector`, assert `published_at` is `None` rather than raising
- [ ] Write `test_malformed_selector_skips_article`: mock a listing page where the configured `title_selector` matches nothing, assert empty list returned (no exception)
- [ ] Write `test_body_fetch_failure_skips_article`: mock article body fetch returning HTTP 500, assert that article is skipped, no exception propagates
- [ ] Run tests — confirm all four fail with `ImportError` or `ModuleNotFoundError` (handler does not exist yet)

---

### Task 2 — Implement `scrape_static` handler

- [ ] Create `bidequity-newsroom/src/bidequity/ingest/handlers/scrape_static.py`
- [ ] Add module-level docstring explaining feed_type, selector contract, and error policy
- [ ] Define `_SelectorConfig` TypedDict: `list_selector: str`, `title_selector: str`, `url_selector: str`, `date_selector: str | None`
- [ ] Implement `async def fetch(source: Source, since: datetime) -> list[ItemCreate]`:
  - Parse `source.notes` JSONB as `_SelectorConfig`; raise `ValueError` with source name if required keys missing
  - `async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:`
  - `GET source.url` — on non-200 status log warning and return `[]`
  - Parse HTML with `selectolax.parser.HTMLParser`
  - For each element matched by `list_selector`:
    - Extract `title` from `title_selector` (`.text(strip=True)`)
    - Extract `url` from `url_selector` (`href` attribute, resolved against base URL via `urllib.parse.urljoin`)
    - Extract `published_at` from `date_selector` (`datetime` attribute, parse with `datetime.fromisoformat`); set `None` if selector missing or parse fails
    - Skip article if `published_at` is not `None` and `published_at < since` (already seen)
  - For each candidate URL, `GET url` — on non-200 status log warning and `continue`
  - Extract body text with `trafilatura.extract(html, include_comments=False, include_tables=False)` — skip if returns `None`
  - Append `ItemCreate(source_id=source.id, url=url, title=title, body_text=body, published_at=published_at, ...)`
- [ ] Run `test_scrape_static.py` — all four tests must pass

---

### Task 3 — Write failing tests for `scrape_js` handler

- [ ] Create `bidequity-newsroom/tests/test_ingest/test_scrape_js.py`
- [ ] Write `test_fetch_returns_item_list`: mock `playwright.async_api.Page` object using `unittest.mock.AsyncMock`; mock `page.goto()`, `page.query_selector_all()`, `page.eval_on_selector()`, `page.content()` returning a minimal HTML article; assert `fetch()` returns non-empty `list[ItemCreate]`
- [ ] Write `test_js_navigation_timeout_skips_source`: mock `page.goto()` raising `playwright.async_api.TimeoutError`; assert returns `[]`, no exception raised
- [ ] Write `test_body_page_timeout_skips_article`: mock listing page successfully, mock article page `goto()` raising `playwright.async_api.TimeoutError`; assert article is skipped
- [ ] Run tests — confirm all fail (handler does not exist yet)

---

### Task 4 — Implement `scrape_js` handler

- [ ] Create `bidequity-newsroom/src/bidequity/ingest/handlers/scrape_js.py`
- [ ] Add module-level docstring and usage note: "Only use this handler when JS rendering is required. Playwright adds ~500 MB dependency and ~2s per page overhead."
- [ ] At module level, declare `_browser: Browser | None = None` and `async def _get_browser() -> Browser:` that launches Chromium headless (`playwright.async_api.async_playwright`, `p.chromium.launch(headless=True)`) and caches in `_browser`
- [ ] Implement `async def fetch(source: Source, since: datetime) -> list[ItemCreate]`:
  - Parse `source.notes` JSONB the same way as `scrape_static` (reuse or import `_SelectorConfig`)
  - `browser = await _get_browser()`
  - `context = await browser.new_context()`
  - `page = await context.new_page()`
  - `try: await page.goto(source.url, timeout=30_000)` — on `TimeoutError` log warning, close context, return `[]`
  - Query listing elements with `await page.query_selector_all(list_selector)`
  - For each element, extract `title`, `href`, `datetime` via `element.eval_handle` or `element.get_attribute`
  - Skip if `published_at < since`
  - Open new tab for article: `article_page = await context.new_page()`; `await article_page.goto(url, timeout=30_000)` — on `TimeoutError` skip
  - `html = await article_page.content()` — extract body via `trafilatura.extract`
  - `await article_page.close()`
  - Append `ItemCreate(...)`
  - `finally: await context.close()`
- [ ] Add `async def close_browser()` for graceful shutdown in tests and app teardown
- [ ] Run `test_scrape_js.py` — all three tests must pass

---

### Task 5 — Wire new handlers into dispatcher

- [ ] Open `bidequity-newsroom/src/bidequity/ingest/scheduler.py` (existing Ticket 3 file)
- [ ] Import `scrape_static` and `scrape_js` from their handler modules
- [ ] In the `_dispatch(source)` function (or equivalent dispatch dict), add cases for `feed_type == 'scrape_static'` and `feed_type == 'scrape_js'`
- [ ] Confirm that the existing error isolation wrapper (per-source try/except that increments `consecutive_failures` and never crashes the batch) covers both new handlers
- [ ] No new tests needed here — integration is exercised by the acceptance test in Task 11

---

### Task 6 — Write failing tests for `dedupe.py` — embedding worker

- [ ] Create `bidequity-newsroom/tests/test_ingest/test_dedupe.py`
- [ ] Write `test_embed_pending_items_calls_voyage_api`:
  - Insert 3 `Item` rows with `embedding = NULL` and `ingested_at = now()`
  - Mock `httpx.AsyncClient.post` to return a Voyage API response: `{"data": [{"embedding": [0.1]*1024}, {"embedding": [0.2]*1024}, {"embedding": [0.3]*1024}]}`
  - Call `await embed_pending_items(session)`
  - Assert all 3 rows now have `embedding IS NOT NULL`
  - Assert `httpx.post` was called once (batch of 3, not 3 individual calls)
- [ ] Write `test_embed_pending_items_skips_already_embedded`:
  - Insert 1 item with `embedding` already set, 1 with `embedding = NULL`
  - Mock Voyage API
  - Assert Voyage API called with input list of length 1 (not 2)
- [ ] Write `test_embed_pending_items_skips_items_older_than_24h`:
  - Insert 1 item with `ingested_at = now() - 25 hours`, `embedding = NULL`
  - Call `await embed_pending_items(session)`
  - Assert Voyage API not called
- [ ] Run tests — confirm all fail (`dedupe.py` does not exist yet)

---

### Task 7 — Implement `embed_pending_items` in `dedupe.py`

- [ ] Create `bidequity-newsroom/src/bidequity/ingest/dedupe.py`
- [ ] Add imports: `httpx`, `os`, `datetime`, `sqlmodel`, `Item` model, `select` from `sqlmodel`
- [ ] Add module-level constant `VOYAGE_EMBED_URL = "https://api.voyageai.com/v1/embeddings"` and `VOYAGE_MODEL = "voyage-3-lite"`
- [ ] Implement `async def embed_pending_items(session: AsyncSession) -> int:`
  ```python
  cutoff = datetime.utcnow() - timedelta(hours=24)
  stmt = select(Item).where(Item.embedding.is_(None), Item.ingested_at >= cutoff)
  items = (await session.exec(stmt)).all()
  if not items:
      return 0
  processed = 0
  for batch_start in range(0, len(items), 100):
      batch = items[batch_start : batch_start + 100]
      inputs = [item.body_preview or item.body_text[:500] for item in batch]
      async with httpx.AsyncClient(timeout=60) as client:
          resp = await client.post(
              VOYAGE_EMBED_URL,
              headers={"Authorization": f"Bearer {os.environ['VOYAGE_API_KEY']}"},
              json={"input": inputs, "model": VOYAGE_MODEL},
          )
          resp.raise_for_status()
          data = resp.json()["data"]
      for item, embedding_obj in zip(batch, data):
          item.embedding = embedding_obj["embedding"]
          session.add(item)
      await session.commit()
      processed += len(batch)
  return processed
  ```
- [ ] Run `test_dedupe.py` — embedding tests must pass

---

### Task 8 — Write failing tests for `dedupe.py` — semantic dedupe

- [ ] In `bidequity-newsroom/tests/test_ingest/test_dedupe.py`, add:
- [ ] Write `test_flag_semantic_duplicates_flags_near_identical_items`:
  - Insert `item_a` ingested 2 hours ago with a known embedding vector `[0.1]*1024`
  - Insert `item_b` ingested 30 minutes ago, `semantic_duplicate = False`, from the same source, with embedding `[0.1001]*1024` (cosine distance < 0.06)
  - Mock the pgvector kNN query result to return `item_a.id`
  - Call `await flag_semantic_duplicates(session)`
  - Reload `item_b` from DB; assert `item_b.semantic_duplicate is True`
- [ ] Write `test_flag_semantic_duplicates_does_not_flag_dissimilar_items`:
  - Insert `item_a` (older) with embedding `[0.1]*1024`
  - Insert `item_b` (recent) with embedding `[0.9]*1024` (cosine distance > 0.06)
  - Mock kNN query to return no matches
  - Call `await flag_semantic_duplicates(session)`
  - Assert `item_b.semantic_duplicate is False`
- [ ] Write `test_flag_semantic_duplicates_skips_items_without_embeddings`:
  - Insert 1 item with `embedding = NULL` ingested recently
  - Assert `flag_semantic_duplicates` completes without error and makes no DB writes
- [ ] Run tests — confirm all three fail

---

### Task 9 — Add `semantic_duplicate` column via Alembic migration

- [ ] Create `bidequity-newsroom/alembic/versions/0002_add_semantic_duplicate.py`
- [ ] Migration content:
  ```python
  """Add semantic_duplicate column to items

  Revision ID: 0002
  Revises: 0001
  Create Date: 2026-04-18
  """
  from alembic import op
  import sqlalchemy as sa

  revision = '0002'
  down_revision = '0001'
  branch_labels = None
  depends_on = None

  def upgrade() -> None:
      op.add_column(
          'items',
          sa.Column(
              'semantic_duplicate',
              sa.Boolean(),
              nullable=False,
              server_default='false',
          ),
      )

  def downgrade() -> None:
      op.drop_column('items', 'semantic_duplicate')
  ```
- [ ] Add `semantic_duplicate: bool = Field(default=False)` to the `Item` SQLModel class in `bidequity-newsroom/src/bidequity/models/item.py`
- [ ] Run `alembic upgrade head` locally — confirm migration applies cleanly
- [ ] Run full test suite — confirm no regressions from schema change

---

### Task 10 — Implement `flag_semantic_duplicates` in `dedupe.py`

- [ ] Add `flag_semantic_duplicates` to `bidequity-newsroom/src/bidequity/ingest/dedupe.py`:
  ```python
  async def flag_semantic_duplicates(session: AsyncSession) -> int:
      cutoff = datetime.utcnow() - timedelta(hours=24)
      stmt = (
          select(Item)
          .where(
              Item.embedding.is_not(None),
              Item.ingested_at >= cutoff,
              Item.semantic_duplicate.is_(False),
          )
      )
      recent_items = (await session.exec(stmt)).all()
      flagged = 0
      for item in recent_items:
          result = await session.exec(
              sa.text(
                  """
                  SELECT id FROM items
                  WHERE embedding <=> :vec < 0.06
                    AND ingested_at < :ingested_at
                    AND id != :item_id
                  LIMIT 3
                  """
              ),
              {"vec": item.embedding, "ingested_at": item.ingested_at, "item_id": item.id},
          )
          if result.first() is not None:
              item.semantic_duplicate = True
              session.add(item)
              flagged += 1
      await session.commit()
      return flagged
  ```
- [ ] Run semantic dedupe tests in `test_dedupe.py` — all three must pass
- [ ] Run full `test_dedupe.py` — all tests (embedding + semantic dedupe) must pass

---

### Task 11 — Write failing test for dead source check

- [ ] In `bidequity-newsroom/tests/test_ingest/test_scheduler.py` (create if not exists), add:
- [ ] Write `test_check_dead_sources_sends_alert_for_stale_source`:
  - Insert `source_a` with `active=True`, `last_success_at = now() - 15 days`
  - Insert `source_b` with `active=True`, `last_success_at = now() - 1 day` (healthy)
  - Insert `source_c` with `active=False`, `last_success_at = now() - 30 days` (inactive — should be ignored)
  - Mock `smtplib.SMTP` (or the Cloudflare Email Routing call, whichever is used)
  - Call `await check_dead_sources(session)`
  - Assert email was sent exactly once, mentioning `source_a.name` in the body
  - Assert `source_b` and `source_c` did not trigger an alert
- [ ] Run test — confirm it fails (`check_dead_sources` does not exist yet)

---

### Task 12 — Implement `check_dead_sources` and schedule it

- [ ] Open `bidequity-newsroom/src/bidequity/ingest/scheduler.py`
- [ ] Add imports: `smtplib`, `email.mime.text`, `os`
- [ ] Implement `async def check_dead_sources(session: AsyncSession) -> list[str]:`
  ```python
  cutoff = datetime.utcnow() - timedelta(days=14)
  stmt = select(Source).where(
      Source.active.is_(True),
      or_(Source.last_success_at.is_(None), Source.last_success_at < cutoff),
  )
  dead = (await session.exec(stmt)).all()
  if not dead:
      return []
  names = [s.name for s in dead]
  body = "The following sources have not successfully ingested any items in 14 days:\n\n"
  body += "\n".join(f"  - {n}" for n in names)
  body += "\n\nCheck the Sources view in the dashboard and re-activate or disable these sources."
  _send_alert_email(
      subject=f"[BidEquity] {len(dead)} dead source(s) detected",
      body=body,
  )
  return names
  ```
- [ ] Implement `def _send_alert_email(subject: str, body: str) -> None:` using `smtplib.SMTP` with Cloudflare Email Routing (SMTP relay at `smtp.cloudflare.net:587`), credentials from `os.environ["ALERT_EMAIL_FROM"]` and `os.environ["ALERT_EMAIL_TO"]` and `os.environ["CLOUDFLARE_SMTP_PASSWORD"]`
- [ ] In the APScheduler setup block, register:
  ```python
  scheduler.add_job(
      _run_check_dead_sources,
      CronTrigger(hour=9, minute=0),
      id="check_dead_sources",
      replace_existing=True,
  )
  ```
  where `_run_check_dead_sources` is a thin async wrapper that opens a session and calls `check_dead_sources(session)`
- [ ] Run `test_scheduler.py::test_check_dead_sources_sends_alert_for_stale_source` — must pass

---

### Task 13 — Wire embedding and semantic dedupe into scheduler

- [ ] In `bidequity-newsroom/src/bidequity/ingest/scheduler.py`, register two new jobs:
  ```python
  # Embedding worker — every 30 minutes
  scheduler.add_job(
      _run_embed_pending_items,
      IntervalTrigger(minutes=30),
      id="embed_pending_items",
      replace_existing=True,
  )

  # Semantic dedupe — every 30 minutes, 5 minutes after embedding
  scheduler.add_job(
      _run_flag_semantic_duplicates,
      IntervalTrigger(minutes=30, start_date=now + timedelta(minutes=5)),
      id="flag_semantic_duplicates",
      replace_existing=True,
  )
  ```
- [ ] Both wrappers open `AsyncSession`, call the respective function from `dedupe.py`, log the return count, ping Healthchecks.io
- [ ] Run full test suite: `pytest bidequity-newsroom/tests/ -v` — confirm 0 failures

---

### Task 14 — Integration smoke test

- [ ] In `bidequity-newsroom/tests/test_ingest/test_integration.py` (create if not exists), add:
- [ ] Write `test_scrape_static_end_to_end`:
  - Seed one `Source` row with `feed_type='scrape_static'` and a valid `notes` JSONB (use a known-stable UK gov URL or a locally served mock HTML page via `pytest-httpserver`)
  - Call `await fetch(source, since=datetime.utcnow() - timedelta(days=7))`
  - Assert at least one `ItemCreate` returned with non-empty `body_text`
  - This test is marked `@pytest.mark.integration` and skipped unless `INTEGRATION_TESTS=1` env var is set — it makes real HTTP calls
- [ ] Write `test_embed_and_dedupe_pipeline`:
  - Using test DB (via Ticket 3's `conftest.py` fixtures), insert 2 items with identical `body_preview`
  - Run `embed_pending_items(session)` with mocked Voyage API returning identical vectors for both items
  - Run `flag_semantic_duplicates(session)`
  - Assert the second item (later `ingested_at`) has `semantic_duplicate = True`
  - Assert the first item has `semantic_duplicate = False`
- [ ] Run `test_embed_and_dedupe_pipeline` (unit — no real HTTP): must pass

---

### Task 15 — Commit

- [ ] Stage: `alembic/versions/0002_add_semantic_duplicate.py`, `src/bidequity/ingest/handlers/scrape_static.py`, `src/bidequity/ingest/handlers/scrape_js.py`, `src/bidequity/ingest/dedupe.py`, `src/bidequity/ingest/scheduler.py` (updated), `src/bidequity/models/item.py` (updated), all new test files
- [ ] Commit message: `feat(ingest): Ticket 4 — static/JS scrapers, Voyage embeddings, semantic dedupe, dead source check`
- [ ] Do NOT push until acceptance criteria below are verified

---

## Acceptance Criteria

Before marking this ticket complete, confirm:

1. **Scraper dispatch**: `feed_type='scrape_static'` and `feed_type='scrape_js'` route correctly in the scheduler dispatcher — verify by seeding one source of each type and running a manual ingest pass
2. **CSS selector config**: a source with well-formed `notes` JSONB produces `ItemCreate` objects; a source with malformed `notes` logs a warning and returns `[]` without crashing the batch
3. **Embeddings populated**: after running `embed_pending_items`, query `SELECT COUNT(*) FROM items WHERE embedding IS NULL AND ingested_at > now()-interval '24h'` returns 0
4. **Semantic dedupe**: insert two items with identical `body_preview` + identical Voyage vectors; after `flag_semantic_duplicates`, the later item has `semantic_duplicate = true`
5. **Classifier skips duplicates**: verify that the classifier batch worker (Ticket 5) filters on `semantic_duplicate = false` — note this constraint for Ticket 5 implementation
6. **Dead source alert**: set `last_success_at` on a test source to 15 days ago; run `check_dead_sources`; confirm alert email received at `ALERT_EMAIL_TO`
7. **No batch crashes**: a source returning HTTP 500, a source with a JS timeout, and a source with a missing `notes` field all log warnings and allow the rest of the batch to complete

---

## Known Dependencies and Gotchas

- **Ticket 3 prerequisite**: this ticket assumes `Source`, `Item`, `ItemCreate` models, the `content_hash` unique constraint, and the APScheduler setup are already in place from Ticket 3.
- **pgvector IVFFlat index**: `CREATE INDEX idx_items_embedding ON items USING ivfflat (embedding vector_cosine_ops)` from the Ticket 2 migration is required for the kNN query to be performant. If that index is absent the dedupe query will still work but will be slow at scale. Verify it exists before running `flag_semantic_duplicates` in production.
- **Voyage vector dimensions**: `voyage-3-lite` outputs 1024-dimensional vectors. The `items.embedding` column must be `VECTOR(1024)`. If the schema was seeded with a different dimension, alter the column before running the embedding worker.
- **Playwright install**: `playwright install chromium` must be run in the virtualenv after `uv add playwright`. Add this to the GitHub Actions deploy workflow and the dev setup section of `README.md`.
- **Browser reuse across calls**: `_browser` is a module-level singleton in `scrape_js.py`. It is not safe to share across async workers in a multi-process deployment. At Ticket 4's target scale (single-process monolith) this is fine; revisit if the scheduler moves to a worker pool.
- **Cloudflare SMTP credentials**: Cloudflare Email Routing's SMTP relay requires domain verification. If the bidequity.co.uk domain is not yet verified in Cloudflare, the dead-source alert will fail silently. Test `_send_alert_email` manually before depending on it for monitoring.
- **`since` semantics for scrapers**: the `since` parameter is a best-effort filter. Scrapers that can extract `published_at` use it; those where `date_selector` is absent or unparseable return all items found and rely on the `content_hash` unique constraint in `items` to absorb duplicates.
