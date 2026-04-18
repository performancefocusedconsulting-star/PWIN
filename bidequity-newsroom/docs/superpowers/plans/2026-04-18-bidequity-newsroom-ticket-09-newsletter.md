# BidEquity Newsroom — Ticket 9: Newsletter Publishing

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the week's approved items into a Beehiiv newsletter draft every Thursday evening and provide a dashboard route for the operator to write an editor's note and confirm publication, so a test newsletter reaches the Beehiiv list by Friday 8am.

**Architecture:** A `BeehiivClient` wraps the Beehiiv v2 REST API using `httpx` (async), creating posts as drafts then confirming them. A `compile_weekly_newsletter` function queries the `publications` table for the week's approved newsletter items, renders them with a Jinja2 HTML email template (inline CSS, BidEquity Warm Logic palette), and posts the result to Beehiiv. An APScheduler job triggers the compile+create-draft step every Thursday at 18:00 UTC; the operator writes an editor's note and clicks confirm via a new FastAPI dashboard route, which calls `BeehiivClient.confirm_post`.

**Tech Stack:** Beehiiv API v2, Jinja2 HTML templates, APScheduler, httpx

---

## File Map

| File | Description |
|---|---|
| `bidequity-newsroom/src/bidequity/models/editors_note.py` | `EditorsNote` SQLModel table: `id`, `week_start DATE UNIQUE`, `content TEXT`, `created_at` |
| `bidequity-newsroom/alembic/versions/xxxx_add_editors_note.py` | Alembic migration adding the `editors_notes` table |
| `bidequity-newsroom/src/bidequity/publish/beehiiv.py` | `BeehiivClient` async class: `create_post`, `confirm_post` |
| `bidequity-newsroom/src/bidequity/publish/newsletter_compiler.py` | `compile_weekly_newsletter` and `get_or_create_editors_note` |
| `bidequity-newsroom/src/bidequity/publish/templates/newsletter.html` | Full Jinja2 HTML email template with inline CSS, Warm Logic palette |
| `bidequity-newsroom/src/bidequity/dashboard/routes.py` | New GET/POST `/newsletter/{week}` route (editor's note + confirm UI) |
| `bidequity-newsroom/src/bidequity/dashboard/templates/newsletter_preview.html` | Dashboard Jinja2 template showing compiled HTML preview + editor's note textarea |
| `bidequity-newsroom/src/bidequity/ingest/scheduler.py` | New `compile_newsletter` APScheduler job (Thursday 18:00 UTC) |
| `bidequity-newsroom/tests/test_publish/test_beehiiv.py` | Unit tests for `BeehiivClient` with mocked httpx |
| `bidequity-newsroom/tests/test_publish/test_newsletter_compiler.py` | Integration tests for `compile_weekly_newsletter` |

---

## Tasks

### Phase 1 — Data model

- [ ] **1.1** Create `bidequity-newsroom/src/bidequity/models/editors_note.py` with `EditorsNote` SQLModel:
  ```python
  class EditorsNote(SQLModel, table=True):
      __tablename__ = "editors_notes"
      id: int | None = Field(default=None, primary_key=True)
      week_start: date = Field(sa_column=Column(Date, unique=True, nullable=False))
      content: str = Field(default="")
      created_at: datetime = Field(default_factory=datetime.utcnow)
  ```

- [ ] **1.2** Generate an Alembic migration for `editors_notes`. Run `alembic revision --autogenerate -m "add_editors_note"`. Verify the generated file creates the table with a UNIQUE constraint on `week_start`. Commit the migration file.

- [ ] **1.3** Apply the migration locally (`alembic upgrade head`) and confirm the table exists.

---

### Phase 2 — Tests first (TDD)

- [ ] **2.1** Create `bidequity-newsroom/tests/test_publish/test_beehiiv.py`. Write all three tests before touching `beehiiv.py`:

  **Test: `test_create_post_sends_correct_payload`**
  - Mock `httpx.AsyncClient.post` to return `{"data": {"id": "post_abc123"}}` with status 201.
  - Call `BeehiivClient("key", "pub_id").create_post("Test Title", "<p>Hello</p>", scheduled_for=None)`.
  - Assert `post` was called with URL `https://api.beehiiv.com/v2/publications/pub_id/posts`.
  - Assert payload contains `{"title": "Test Title", "content_html": "<p>Hello</p>", "status": "draft"}`.
  - Assert `scheduled_at` key is absent (or None) when `scheduled_for=None`.
  - Assert return value is `"post_abc123"`.

  **Test: `test_create_post_with_scheduled_for`**
  - Same mock setup. Call with `scheduled_for=datetime(2026, 4, 25, 8, 0, tzinfo=timezone.utc)`.
  - Assert payload `scheduled_at` equals `"2026-04-25T08:00:00+00:00"`.

  **Test: `test_confirm_post_sends_patch`**
  - Mock `httpx.AsyncClient.patch` to return `{}` with status 200.
  - Call `BeehiivClient("key", "pub_id").confirm_post("post_abc123")`.
  - Assert `patch` called with URL `https://api.beehiiv.com/v2/publications/pub_id/posts/post_abc123`.
  - Assert payload is `{"status": "confirmed"}`.

  Run `pytest tests/test_publish/test_beehiiv.py` — all three must fail (no implementation yet).

- [ ] **2.2** Create `bidequity-newsroom/tests/test_publish/test_newsletter_compiler.py`. Write tests before touching `newsletter_compiler.py`:

  **Test: `test_compile_weekly_newsletter_includes_all_items`**
  - In a test DB session, insert one `Draft` (status=`approved`, `newsletter_para="Para A"`) and its `Publication` (channel=`newsletter`, `scheduled_for` = `week_start + 1 day`, `status=scheduled`), plus a second draft/publication (`newsletter_para="Para B"`). Also insert an out-of-window publication (8 days out) that must NOT appear.
  - Call `compile_weekly_newsletter(session, week_start)`.
  - Assert returned HTML contains `"Para A"` and `"Para B"`.
  - Assert out-of-window item's content is absent.

  **Test: `test_compile_weekly_newsletter_callout_present`**
  - Insert one draft whose `newsletter_para` contains a `so_what_line` field accessible from the joined `Draft`. Call `compile_weekly_newsletter`. Assert the HTML contains the string `"What this means for bid teams:"`.

  **Test: `test_editors_note_placeholder_when_none_exists`**
  - Call `get_or_create_editors_note(session, week_start)` with no matching row in `editors_notes`.
  - Assert the return value is an empty string `""`.

  **Test: `test_editors_note_returns_saved_content`**
  - Insert an `EditorsNote(week_start=week_start, content="My note")`.
  - Call `get_or_create_editors_note(session, week_start)`.
  - Assert the return value is `"My note"`.

  Run `pytest tests/test_publish/test_newsletter_compiler.py` — all four must fail.

---

### Phase 3 — Beehiiv client implementation

- [ ] **3.1** Create `bidequity-newsroom/src/bidequity/publish/beehiiv.py`:

  ```python
  import httpx
  from datetime import datetime
  
  
  class BeehiivClient:
      BASE_URL = "https://api.beehiiv.com/v2"
  
      def __init__(self, api_key: str, publication_id: str) -> None:
          self._api_key = api_key
          self._publication_id = publication_id
          self._headers = {
              "Authorization": f"Bearer {api_key}",
              "Content-Type": "application/json",
          }
  
      async def create_post(
          self,
          title: str,
          html_content: str,
          scheduled_for: datetime | None = None,
      ) -> str:
          """
          Create a draft post in Beehiiv.
          Returns the Beehiiv post ID string.
          """
          payload: dict = {
              "title": title,
              "content_html": html_content,
              "status": "draft",
          }
          if scheduled_for is not None:
              payload["scheduled_at"] = scheduled_for.isoformat()
  
          async with httpx.AsyncClient() as client:
              response = await client.post(
                  f"{self.BASE_URL}/publications/{self._publication_id}/posts",
                  headers=self._headers,
                  json=payload,
                  timeout=30.0,
              )
              response.raise_for_status()
              return response.json()["data"]["id"]
  
      async def confirm_post(self, post_id: str) -> None:
          """
          Promote a draft post to confirmed (queued for send).
          """
          async with httpx.AsyncClient() as client:
              response = await client.patch(
                  f"{self.BASE_URL}/publications/{self._publication_id}/posts/{post_id}",
                  headers=self._headers,
                  json={"status": "confirmed"},
                  timeout=30.0,
              )
              response.raise_for_status()
  ```

- [ ] **3.2** Run `pytest tests/test_publish/test_beehiiv.py` — all three tests must pass. Fix any failures before continuing.

- [ ] **3.3** Commit: `git commit -m "feat(publish): BeehiivClient with create_post and confirm_post"`

---

### Phase 4 — Newsletter HTML template

- [ ] **4.1** Create `bidequity-newsroom/src/bidequity/publish/templates/newsletter.html`. This is a full HTML email template with **inline CSS only** (email clients strip `<style>` tags in many environments — critical for Beehiiv deliverability). Use the BidEquity Warm Logic palette:

  - Background: `#f8f6f1`
  - Text: `#1a1a1a`
  - Accent / links: `#2d5a8e`
  - Callout background: `#e8e4dc`
  - Editor's note background: `#ede9e1`
  - Font stack: `Georgia, 'Times New Roman', serif` for headlines; `Arial, Helvetica, sans-serif` for body

  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{ week_label }} — BidEquity Intelligence</title>
  </head>
  <body style="margin:0;padding:0;background-color:#f8f6f1;font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;">
  
    <!-- Wrapper -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"
           style="background-color:#f8f6f1;">
      <tr>
        <td align="center" style="padding:32px 16px;">
  
          <!-- Inner container -->
          <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0"
                 style="max-width:600px;width:100%;background-color:#ffffff;border-radius:4px;
                        box-shadow:0 1px 4px rgba(0,0,0,0.06);">
  
            <!-- Header -->
            <tr>
              <td style="background-color:#1a1a1a;padding:28px 36px;border-radius:4px 4px 0 0;">
                <p style="margin:0;font-family:Georgia,'Times New Roman',serif;font-size:22px;
                           font-weight:bold;color:#f8f6f1;letter-spacing:0.5px;">BidEquity</p>
                <p style="margin:6px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;
                           color:#a0a0a0;letter-spacing:0.3px;">Pursuit Intelligence — {{ week_label }}</p>
              </td>
            </tr>
  
            <!-- Editor's note (conditional) -->
            {% if editors_note %}
            <tr>
              <td style="padding:24px 36px 0;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td style="background-color:#ede9e1;border-left:3px solid #2d5a8e;
                                padding:16px 20px;border-radius:0 4px 4px 0;">
                      <p style="margin:0 0 4px;font-family:Arial,Helvetica,sans-serif;font-size:11px;
                                 text-transform:uppercase;letter-spacing:1px;color:#666666;">
                        Editor's Note
                      </p>
                      <p style="margin:0;font-family:Georgia,'Times New Roman',serif;font-size:15px;
                                 font-style:italic;color:#1a1a1a;line-height:1.6;">
                        {{ editors_note }}
                      </p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            {% endif %}
  
            <!-- Items -->
            <tr>
              <td style="padding:24px 36px;">
  
                {% for item in items %}
                <!-- Item {{ loop.index }} -->
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"
                       style="margin-bottom:{{ '0' if loop.last else '28px' }};
                              border-bottom:{{ 'none' if loop.last else '1px solid #e8e4dc' }};
                              padding-bottom:{{ '0' if loop.last else '28px' }};">
                  <tr>
                    <td>
                      <!-- Title linked to source -->
                      <p style="margin:0 0 8px;">
                        <a href="{{ item.source_url }}"
                           style="font-family:Georgia,'Times New Roman',serif;font-size:18px;
                                  font-weight:bold;color:#2d5a8e;text-decoration:none;line-height:1.3;">
                          {{ item.title }}
                        </a>
                      </p>
  
                      <!-- Source + sector metadata -->
                      <p style="margin:0 0 10px;font-family:Arial,Helvetica,sans-serif;
                                 font-size:12px;color:#888888;">
                        {{ item.source_name }}{% if item.sector %} &middot; {{ item.sector }}{% endif %}
                      </p>
  
                      <!-- Summary (2-3 sentences from newsletter_para) -->
                      {% if loop.index == deeper_cut_index %}
                        <!-- Deeper cut: full newsletter_para -->
                        <p style="margin:0 0 12px;font-family:Arial,Helvetica,sans-serif;font-size:15px;
                                   color:#1a1a1a;line-height:1.7;">
                          {{ item.newsletter_para }}
                        </p>
                        <p style="margin:0 0 12px;font-family:Arial,Helvetica,sans-serif;font-size:12px;
                                   color:#888888;font-style:italic;">&#9660; Deeper cut this week</p>
                      {% else %}
                        <p style="margin:0 0 12px;font-family:Arial,Helvetica,sans-serif;font-size:15px;
                                   color:#1a1a1a;line-height:1.7;">
                          {{ item.summary }}
                        </p>
                      {% endif %}
  
                      <!-- "What this means for bid teams:" callout -->
                      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                        <tr>
                          <td style="background-color:#e8e4dc;border-left:3px solid #2d5a8e;
                                      padding:12px 16px;border-radius:0 4px 4px 0;">
                            <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:13px;
                                       color:#1a1a1a;line-height:1.6;">
                              <strong style="color:#2d5a8e;">What this means for bid teams:</strong>
                              {{ item.so_what_line }}
                            </p>
                          </td>
                        </tr>
                      </table>
  
                    </td>
                  </tr>
                </table>
                {% endfor %}
  
              </td>
            </tr>
  
            <!-- Footer -->
            <tr>
              <td style="background-color:#f0ece4;padding:20px 36px;border-radius:0 0 4px 4px;
                          border-top:1px solid #e0dbd2;">
                <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:12px;
                           color:#888888;line-height:1.6;text-align:center;">
                  BidEquity &mdash; Pursuit Intelligence for UK public-sector bid teams<br />
                  <a href="{{ unsubscribe_url }}"
                     style="color:#2d5a8e;text-decoration:underline;">Unsubscribe</a>
                  &nbsp;&middot;&nbsp;
                  <a href="https://bidequity.co.uk"
                     style="color:#2d5a8e;text-decoration:underline;">bidequity.co.uk</a>
                </p>
              </td>
            </tr>
  
          </table>
          <!-- /Inner container -->
  
        </td>
      </tr>
    </table>
    <!-- /Wrapper -->
  
  </body>
  </html>
  ```

  Template variables expected by the compiler:
  - `week_label` — human-readable string e.g. `"Week of 21 April 2026"`
  - `editors_note` — string (may be empty; block is suppressed if falsy)
  - `items` — list of dicts with keys: `title`, `source_url`, `source_name`, `sector`, `newsletter_para`, `summary`, `so_what_line`
  - `deeper_cut_index` — 1-based index of the item to render in expanded form (highest `relevance_score` in the week's set)
  - `unsubscribe_url` — Beehiiv auto-populates `{{unsubscribe_url}}` at send time; pass through as a literal Jinja2 raw block

  **Important:** because Beehiiv's own template engine also uses `{{ }}` syntax, wrap the unsubscribe token in a Jinja2 `{% raw %}` block so it passes through unescaped:
  ```html
  <a href="{% raw %}{{unsubscribe_url}}{% endraw %}" ...>Unsubscribe</a>
  ```

- [ ] **4.2** Commit: `git commit -m "feat(publish): newsletter HTML email template with Warm Logic palette"`

---

### Phase 5 — Newsletter compiler implementation

- [ ] **5.1** Create `bidequity-newsroom/src/bidequity/publish/newsletter_compiler.py`:

  ```python
  from __future__ import annotations
  
  import os
  from datetime import date, timedelta
  from typing import Any
  
  from jinja2 import Environment, FileSystemLoader
  from sqlmodel import Session, select
  
  from bidequity.models.draft import Draft
  from bidequity.models.editors_note import EditorsNote
  from bidequity.models.item import Item
  from bidequity.models.publication import Publication
  from bidequity.models.source import Source
  from bidequity.models.classification import Classification
  
  
  _TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
  _env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), autoescape=True)
  
  
  def get_or_create_editors_note(session: Session, week_start: date) -> str:
      """Return the editor's note content for this week, or empty string if not yet written."""
      stmt = select(EditorsNote).where(EditorsNote.week_start == week_start)
      note = session.exec(stmt).first()
      return note.content if note else ""
  
  
  async def compile_weekly_newsletter(session: Session, week_start: date) -> str:
      """
      Query approved/scheduled newsletter publications for the given week,
      render newsletter.html, and return the HTML string.
      """
      week_end = week_start + timedelta(days=7)
  
      # Join publications -> drafts -> items -> sources, classifications
      stmt = (
          select(Publication, Draft, Item, Source, Classification)
          .join(Draft, Publication.draft_id == Draft.id)
          .join(Item, Draft.item_id == Item.id)
          .join(Source, Item.source_id == Source.id)
          .join(
              Classification,
              Classification.item_id == Item.id,
              isouter=True,
          )
          .where(Publication.channel == "newsletter")
          .where(Publication.status.in_(["approved", "scheduled"]))
          .where(Publication.scheduled_for >= week_start)
          .where(Publication.scheduled_for < week_end)
          .order_by(Classification.relevance_score.desc())
      )
      rows = session.exec(stmt).all()
  
      items: list[dict[str, Any]] = []
      for pub, draft, item, source, classification in rows:
          items.append(
              {
                  "title": item.title,
                  "source_url": item.url,
                  "source_name": source.name,
                  "sector": source.sector,
                  "newsletter_para": draft.newsletter_para,
                  # summary = first two sentences of newsletter_para as a fallback
                  "summary": _first_sentences(draft.newsletter_para, n=2),
                  "so_what_line": draft.so_what_line,
                  "relevance_score": classification.relevance_score if classification else 0,
              }
          )
  
      # Deeper cut = first item (highest relevance_score, already sorted)
      deeper_cut_index = 1 if items else 0
  
      editors_note = get_or_create_editors_note(session, week_start)
      week_label = f"Week of {week_start.strftime('%-d %B %Y')}"
  
      template = _env.get_template("newsletter.html")
      return template.render(
          week_label=week_label,
          editors_note=editors_note,
          items=items,
          deeper_cut_index=deeper_cut_index,
          unsubscribe_url="{{unsubscribe_url}}",  # Beehiiv-native token, passed through
      )
  
  
  def _first_sentences(text: str, n: int = 2) -> str:
      """Return the first n sentences of text."""
      sentences = text.split(". ")
      return ". ".join(sentences[:n]) + ("." if len(sentences) > n else "")
  ```

  Note on Windows `%-d` strftime flag: `%-d` (day without leading zero) is Linux-specific. Use `%#d` on Windows, or use a helper:
  ```python
  week_label = f"Week of {week_start.day} {week_start.strftime('%B %Y')}"
  ```
  Use the portable form to keep the test suite cross-platform.

- [ ] **5.2** Run `pytest tests/test_publish/test_newsletter_compiler.py` — all four tests must pass. Fix any failures before continuing.

- [ ] **5.3** Commit: `git commit -m "feat(publish): newsletter_compiler with compile_weekly_newsletter and editors_note helpers"`

---

### Phase 6 — APScheduler job

- [ ] **6.1** In `bidequity-newsroom/src/bidequity/ingest/scheduler.py`, add the newsletter compile job alongside the existing ingest jobs. The job:
  1. Computes `week_start` as the Monday of the current ISO week.
  2. Calls `compile_weekly_newsletter(session, week_start)` to get the HTML.
  3. Constructs the post title: `f"BidEquity Intelligence — {week_label}"`.
  4. Calls `BeehiivClient(settings.BEEHIIV_API_KEY, settings.BEEHIIV_PUBLICATION_ID).create_post(title, html_content)`.
  5. Stores the returned Beehiiv post ID against a new or existing `Publication` row (set `external_id = post_id`, `status = "draft"`).
  6. Logs success or failure to the application logger and Sentry if configured.

  ```python
  from apscheduler.triggers.cron import CronTrigger
  
  scheduler.add_job(
      compile_and_draft_newsletter,
      trigger=CronTrigger(day_of_week="thu", hour=18, minute=0, timezone="UTC"),
      id="compile_newsletter",
      replace_existing=True,
  )
  ```

- [ ] **6.2** Add `BEEHIIV_API_KEY` and `BEEHIIV_PUBLICATION_ID` to `.env.example` and to `bidequity-newsroom/src/bidequity/common/config.py` (`settings` object).

- [ ] **6.3** Commit: `git commit -m "feat(scheduler): add Thursday 18:00 UTC newsletter compile job"`

---

### Phase 7 — Dashboard route (editor's note + confirm)

- [ ] **7.1** In `bidequity-newsroom/src/bidequity/dashboard/routes.py`, add two new routes:

  **GET `/newsletter/{week}`**
  - `week` is an ISO date string (`YYYY-MM-DD`) representing `week_start`.
  - Queries the current `editors_notes` row for that week (empty string if none).
  - Calls `compile_weekly_newsletter(session, week_start)` to get the preview HTML.
  - Looks up the `Publication` row for that week where `channel='newsletter'` to retrieve `external_id` (Beehiiv draft post ID) and `status`.
  - Renders `newsletter_preview.html` with: `week`, `editors_note`, `preview_html`, `beehiiv_post_id`, `already_confirmed` flag.

  **POST `/newsletter/{week}`**
  - Reads form fields: `editors_note` (text), `action` (`"save"` or `"confirm"`).
  - If `editors_note` is provided: upserts `EditorsNote(week_start=week_start, content=editors_note)`.
  - If `action == "confirm"`:
    - Re-compiles the newsletter HTML (so the latest editor's note is reflected).
    - Calls `BeehiivClient.confirm_post(beehiiv_post_id)`.
    - Sets `Publication.status = "scheduled"` (or `"confirmed"`) in the DB.
    - Redirects back to GET `/newsletter/{week}` with a success flash message.
  - If `action == "save"`: just saves the editor's note and redirects back.

- [ ] **7.2** Create `bidequity-newsroom/src/bidequity/dashboard/templates/newsletter_preview.html`. This is a standard dashboard Jinja2 template (extending `base.html` if present). It must include:
  - A heading showing the week label.
  - A status badge: `Draft in Beehiiv` (yellow) / `Confirmed` (green) / `No draft yet` (grey).
  - A `<form method="POST">` containing:
    - A `<textarea name="editors_note">` pre-populated with the current editor's note (label: "Editor's note", placeholder: "2–3 sentences setting context for this week's items").
    - A `Save note` submit button (`name="action" value="save"`).
    - A `Confirm and send` submit button (`name="action" value="confirm"`, disabled if `already_confirmed` or if `beehiiv_post_id` is None, with tooltip "Compile the newsletter first by waiting for Thursday's job or triggering it manually").
  - Below the form: a bordered `<iframe>` or `<div>` showing the rendered `preview_html` so the operator can visually review before confirming.
  - An HTMX trigger on the textarea (`hx-post`, `hx-trigger="change delay:2s"`) for auto-save of the editor's note without a full page reload.

- [ ] **7.3** Commit: `git commit -m "feat(dashboard): newsletter preview and editor's note route"`

---

### Phase 8 — End-to-end smoke test

- [ ] **8.1** With `BEEHIIV_API_KEY` and `BEEHIIV_PUBLICATION_ID` set in `.env`, insert one test publication row via the Django shell or a fixture script:
  ```sql
  INSERT INTO drafts (item_id, prompt_version, linkedin_post, newsletter_para, so_what_line, status)
  VALUES (1, 'test-v1', '', 'Full newsletter para text here. Second sentence.', 'Bid teams should watch this closely.', 'approved');
  
  INSERT INTO publications (draft_id, channel, final_content, scheduled_for, status)
  VALUES (1, 'newsletter', '', NOW(), 'scheduled');
  ```

- [ ] **8.2** Trigger the scheduler job manually:
  ```python
  # In a Python shell or test script
  import asyncio
  from bidequity.publish.newsletter_compiler import compile_weekly_newsletter
  from bidequity.publish.beehiiv import BeehiivClient
  from bidequity.common.db import get_session
  from datetime import date
  
  session = next(get_session())
  week_start = date.today() - __import__('datetime').timedelta(days=date.today().weekday())
  html = asyncio.run(compile_weekly_newsletter(session, week_start))
  client = BeehiivClient(api_key="...", publication_id="...")
  post_id = asyncio.run(client.create_post("BidEquity Intelligence — test", html))
  print(f"Created Beehiiv draft post ID: {post_id}")
  ```

- [ ] **8.3** Verify the draft post appears in the Beehiiv dashboard under the publication's Posts > Drafts view.

- [ ] **8.4** Visit `http://localhost:8000/newsletter/YYYY-MM-DD` in the browser. Verify:
  - Preview HTML renders with the test item.
  - "What this means for bid teams:" callout is present.
  - Editor's note textarea is empty; type a note and click Save — page reloads with note persisted.
  - Click "Confirm and send" — Beehiiv post moves to confirmed/scheduled status.

- [ ] **8.5** In Beehiiv dashboard, verify the post status changed from Draft to Scheduled/Confirmed.

---

### Phase 9 — Final checks and commit

- [ ] **9.1** Run the full test suite: `pytest bidequity-newsroom/tests/` — all tests green.

- [ ] **9.2** Run `ruff check bidequity-newsroom/src/bidequity/publish/` and `mypy bidequity-newsroom/src/bidequity/publish/` — no errors.

- [ ] **9.3** Verify both env vars are documented in `README.md` or `docs/env-vars.md` (wherever the project's env var reference lives).

- [ ] **9.4** Commit: `git commit -m "test(publish): newsletter compiler and Beehiiv integration smoke test pass"`

---

## Acceptance Criteria

- [ ] Friday 8am: a test newsletter has been sent to the Beehiiv list with the week's approved newsletter-channel publications correctly ordered (highest relevance first) and formatted with Warm Logic palette.
- [ ] Every item has a visible "What this means for bid teams:" callout block.
- [ ] The deeper cut item (highest relevance score) is rendered with full `newsletter_para` text; other items show a 2-sentence summary.
- [ ] Editor's note block appears in the email when content is present; is hidden (not rendered as an empty block) when empty.
- [ ] Unsubscribe link passes through as `{{unsubscribe_url}}` for Beehiiv to resolve at send time.
- [ ] `pytest tests/test_publish/` passes with no failures.
- [ ] `mypy` and `ruff` pass with no errors on the `publish/` module.

---

## Integration Notes

**Depends on (must exist before this ticket):**
- Ticket 7 (Editorial dashboard) — `publications` table with `channel='newsletter'` rows, `drafts` with `newsletter_para` and `so_what_line` fields, base Jinja2 template (`base.html`), FastAPI app with `Session` dependency injection pattern.
- Ticket 8 (LinkedIn publishing) — `scheduler.py` already exists with APScheduler wired up; this ticket adds a job to it.

**Must exist in `common/config.py` before Phase 6:**
```python
BEEHIIV_API_KEY: str
BEEHIIV_PUBLICATION_ID: str
```

**Publications queried by the compiler** use `status IN ('approved', 'scheduled')` — the newsletter compile job must run *after* the operator has approved items for the week. The Thursday 18:00 UTC trigger assumes Monday and Wednesday morning editorial triage sessions (per the operational runbook) have already completed.

**Beehiiv `scheduled_at` behaviour:** Beehiiv treats `scheduled_at` as the send time. If you want to schedule the newsletter for Friday 8am, pass `scheduled_for=datetime(year, month, day_of_friday, 8, 0, tzinfo=timezone.utc)` to `create_post`. The compiler computes this automatically from `week_start + 4 days` (Friday) at 08:00 UTC. Adjust the `compile_and_draft_newsletter` job in scheduler.py accordingly.
