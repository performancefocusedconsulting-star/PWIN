# BidEquity Agentic Content Intelligence Platform

## End-to-End Design Specification

**Prepared for:** Paul Scott
**Intended handoff:** Claude Code (implementation)
**Version:** 1.1 — April 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [Data Model](#4-data-model)
5. [Ingestion Pipeline (Stages 1-2)](#5-ingestion-pipeline-stages-1-2)
6. [Classification Stage (Stage 3)](#6-classification-stage-stage-3)
7. [Draft Generation Stage (Stage 4)](#7-draft-generation-stage-stage-4)
8. [Topic Intelligence Layer (Stage 3A) — new in v1.1](#8-topic-intelligence-layer-stage-3a)
9. [Editorial Dashboard (Stage 5)](#9-editorial-dashboard-stage-5)
10. [Publishing and Measurement (Stages 6-8)](#10-publishing-and-measurement-stages-6-8)
11. [Cost Model](#11-cost-model)
12. [Implementation Roadmap](#12-implementation-roadmap)
13. [Appendices](#13-appendices)

### Changes in v1.1

Version 1.1 introduces the Topic Intelligence Layer (new section 8). This is a new capability sitting between classification and generation that provides: topic tracking, stance detection on live debates, momentum signals, and theme decomposition. It unlocks three new content types (topic radars, stance maps, theme-led analysis) and is intentionally deferred to months 3-6 of implementation so that sufficient historical data has accumulated for the analytics to produce signal rather than noise. Sections 4 (data model), 10 (cost model), and 12 (roadmap) have been extended to cover it. Earlier sections are unchanged.

---

## 1. Executive Summary

This specification defines an agentic content intelligence platform for BidEquity, designed to continuously scan UK public-sector sources, identify content-worthy and pursuit-relevant items, generate draft editorial output with a pursuit-lens angle, and publish to LinkedIn and a Beehiiv newsletter on cadence. The system is intended to require three to five hours per week of human editorial time once operational.

The platform is built from composable components. It is cost-optimised for early-stage operation (target under £25 per month operating cost) with a clear upgrade path as subscriber growth, content volume, and client demand ramp. All implementation choices prioritise: (a) low maintenance burden on a non-technical sole operator, (b) full control and portability (no vendor lock-in where avoidable), and (c) the ability to hand incremental build phases to Claude Code with a clear, testable specification.

The specification is structured in eleven sections. Sections 2 through 4 cover architecture and technology selections with rationale and alternatives. Sections 5 through 9 cover each functional stage of the pipeline with data models, prompt designs, and operational detail. Section 10 covers the cost model across three growth phases. Section 11 provides the implementation roadmap organised as tickets suitable for Claude Code execution.

### 1.1 Scope in this version

- UK public sector source scanning across seven sectors (Defence, Justice, Health & Social Care, Local Gov & Devolved, Central Gov & Cabinet Office, Transport, Emergency Services)
- Automated ingest, deduplication, classification, and draft generation
- Human-in-the-loop editorial review via web dashboard
- Automated publishing to BidEquity LinkedIn company page and Beehiiv newsletter
- Performance metric ingest and feedback loop to classifier
- Cost phasing across three growth stages (Seed, Build, Scale)

### 1.2 Out of scope

- BIP bid intelligence platform features (client-facing briefings, pursuit scoring). Treated as a potential future module sharing the same data substrate.
- Commercial data integrations (Tussell, Stotles). Called out as Phase 3 enhancements.
- Fine-tuning of bespoke models. Premature at projected volumes.
- Multi-user access controls. Single-operator model assumed.

### 1.3 Success criteria

| Metric | Target | How measured |
|---|---|---|
| Editorial time/week | ≤ 5 hours | Time logged in dashboard editorial sessions |
| Items published/week | 2–4 LinkedIn + 1 newsletter | Publishing scheduler output |
| Classifier agreement rate | ≥ 80% with human labels | Weekly sample of 20 items manually re-scored |
| Operating cost (Phase 1) | ≤ £25/month | Actual spend logged against subscription & API billing |
| System uptime | ≥ 99% ingest success | Healthchecks.io reports |
| Content quality (proxy) | LinkedIn engagement rate ≥ 3% | Impressions-to-engagement ratio |

---

## 2. Architecture Overview

### 2.1 Design principles

**Boring technology, interesting prompts.** The architecture uses well-understood components (PostgreSQL, Python, cron) with the intelligence concentrated in prompt design and the classifier/generator layer. This keeps maintenance burden minimal and debugging fast.

**Single process, single machine, until forced otherwise.** A monolithic FastAPI application handles ingestion (via scheduled jobs), classification, generation, dashboard serving, and publishing. Horizontal scaling is unnecessary at projected volumes (~200 items/day ingested, ~10 published/week). This avoids the complexity cost of microservices, queues, and distributed state.

**Idempotent everything.** Every operation (fetch, classify, generate, publish) is safe to re-run. Unique constraints on content hashes prevent duplicate work. Failed runs resume rather than restart.

**Human-in-the-loop at one stage, not many.** The editorial dashboard is the only place the operator intervenes in normal operation. Everything before it is automatic; everything after it is automatic. Cognitive load on the operator is a first-class concern.

**Cost proportional to value.** Cheap models for high-volume low-judgement tasks (classification), expensive models for low-volume high-judgement tasks (generation). Caching, batching, and pre-filtering are applied wherever they reduce cost without degrading quality.

**Data locality.** All content, classifications, drafts, and metrics are stored in one PostgreSQL database. Single source of truth. No data synchronisation problems between services.

### 2.2 Logical architecture

The system is composed of eight functional stages organised into three layers: an ingestion layer (stages 1–2), an intelligence layer (stages 3–4), and a production layer (stages 5–8). A feedback loop connects the production layer back to the intelligence layer to improve classification and generation over time.

| # | Stage | Function | Human/Auto |
|---|---|---|---|
| 1 | Ingest | Poll RSS, APIs, and scrape pages on cadence | Automated |
| 2 | Dedupe + store | Hash, embed, persist items to database | Automated |
| 3 | Classify | Score relevance, extract entities, tag sectors | Automated (Haiku) |
| 4 | Angle generator | Produce LinkedIn + newsletter drafts with pursuit lens | Automated (Sonnet) |
| 5 | Editorial review | Operator approves, edits, rejects candidates | Human (3–5 hrs/wk) |
| 6 | Format | Transform approved items into final post/email | Automated |
| 7 | Schedule | Queue to LinkedIn + Beehiiv | Automated |
| 8 | Publish + measure | Post, then pull engagement metrics back | Automated |

### 2.3 Physical architecture

Single virtual private server running a Python monolith against a local PostgreSQL database. External services are called via HTTPS for model inference (Anthropic API), publishing (LinkedIn API, Beehiiv API), and monitoring (Healthchecks.io).

All application code, configuration, prompts, and database are version-controlled and backed up nightly to an S3-compatible object store (Backblaze B2 or Hetzner Storage Box).

### 2.4 Key architectural decisions

#### ADR-001: Single database

| Aspect | Detail |
|---|---|
| Decision | Use a single PostgreSQL database for items, embeddings, classifications, drafts, and metrics |
| Rationale | Simpler operational model. pgvector extension handles embeddings. Single backup target. Transactional consistency across stages. |
| Alternatives considered | Separate vector DB (Qdrant, Pinecone); separate data lake. Rejected: unnecessary complexity at projected volumes. |
| Revisit when | Item corpus exceeds 1M rows or vector search latency exceeds 500ms |

#### ADR-002: Monolithic application

| Aspect | Detail |
|---|---|
| Decision | Use monolithic FastAPI application with APScheduler for orchestration |
| Rationale | Zero infrastructure beyond a VPS. No broker. No worker pool. Python ecosystem has everything needed. APScheduler runs jobs in-process. |
| Alternatives considered | Celery + Redis; Prefect; Temporal; n8n. Rejected for early phase: operational overhead outweighs benefit. |
| Revisit when | Jobs exceed 10 minutes of runtime or require distributed execution |

#### ADR-003: Model selection

| Aspect | Detail |
|---|---|
| Decision | Use Claude Haiku 4.5 for classification, Claude Sonnet 4.6 for generation |
| Rationale | Haiku is 3x cheaper and sufficient for structured classification. Sonnet quality on generation is the direct leverage point on operator editorial time. |
| Alternatives considered | All-Haiku (rejected: draft quality degrades, costing human time); all-Sonnet (rejected: 3x classifier cost unnecessary); open models via Ollama (rejected: GPU hosting more expensive than API). |
| Revisit when | Anthropic releases a new model tier or usage patterns shift materially |

#### ADR-004: Dashboard stack

| Aspect | Detail |
|---|---|
| Decision | Server-rendered HTML with HTMX for the editorial dashboard |
| Rationale | One-operator internal tool. No SPA benefits justified. FastAPI + Jinja2 + HTMX gives full interactivity with half the code of React. Faster to build, easier to modify. |
| Alternatives considered | React/Next.js; Streamlit; Retool. Rejected: React is overkill; Streamlit is ugly for production use; Retool has subscription cost. |
| Revisit when | Multi-user access needed or mobile-native experience becomes important |

---

## 3. Technology Stack

Each component is chosen with rationale and listed alternatives. The default is the recommended choice; alternatives are noted for cases where preferences or circumstances differ.

### 3.1 Core application stack

| Component | Choice | Why |
|---|---|---|
| Language runtime | Python 3.12 | Rich ecosystem for scraping, data work, and Anthropic SDK. Stable and well-supported. |
| Package manager | `uv` | Fastest pip-compatible manager. Handles virtualenvs and lockfile natively. Consistent with Paul's existing Claude Code workflow. |
| Web framework | FastAPI 0.115+ | Type-safe, async-first, OpenAPI docs automatic, excellent for both API and server-rendered routes. |
| Template engine | Jinja2 + HTMX | Server-rendered HTML with progressive enhancement. Minimal JavaScript. Pair with Pico.css for zero-config styling. |
| Scheduler | APScheduler 3.10+ | In-process cron. No external broker. Persists job state to Postgres. Sufficient for 200 items/day. |
| ORM | SQLModel | Pydantic + SQLAlchemy. Type safety from schema to response. Reduces class duplication. |
| Database | PostgreSQL 16 + pgvector | Relational data, full-text search, and vector similarity in one system. pgvector is production-ready. |
| HTTP client | httpx | Async-native. Better than `requests` for this workload. |
| Scraper runtime (JS) | Playwright | Handles JavaScript-rendered pages. Only when needed — most UK gov sources are static. |
| RSS parser | feedparser | Battle-tested. Handles malformed feeds gracefully. |
| HTML parser | selectolax | 10x faster than BeautifulSoup. C-backed. Used for static scraping. |
| Testing | pytest + pytest-asyncio | Standard. |
| Code quality | ruff + mypy | Single-binary linter/formatter. Static typing on prompts and data models. |

**Alternatives considered**

- Node.js/TypeScript runtime — rejected for weaker scraping ecosystem and Paul's Python familiarity.
- Go — rejected for slower AI SDK maturity and longer iteration loop on prompts.
- Django — rejected as heavy for this problem; FastAPI + HTMX produces less code.
- SQLite — rejected because pgvector support is not native, and Postgres gives headroom with negligible ops cost.
- Celery/Redis — rejected as over-engineered for single-machine workload.

### 3.2 AI and intelligence layer

| Component | Choice | Why |
|---|---|---|
| Classification model | `claude-haiku-4-5` | £0.80/M input, £4/M output. 3x cheaper than Sonnet. Sufficient for structured JSON classification. |
| Generation model | `claude-sonnet-4-6` | £2.40/M input, £12/M output. Quality on narrative generation directly offsets editorial time. |
| Embedding model | voyage-3-lite (via Voyage API) or OpenAI text-embedding-3-small | Embeddings used only for semantic dedupe and retrieval. Cheap models suffice. |
| Prompt caching | Anthropic prompt caching (1h cache TTL) | Classifier and generator system prompts cached. 90% cost reduction on cached tokens. |
| Batch processing | Anthropic Message Batches API | Classification batched every 6 hours. 50% cost reduction on batch-eligible workloads. |
| Prompt versioning | Git + prompt files in `/prompts` directory | Every prompt change tracked. Regression testing via golden dataset. |

**Alternatives considered**

- OpenAI GPT-4o mini for classification — comparable price to Haiku but more variable JSON adherence. Rejected for marginal gain.
- Self-hosted Llama 3.3 70B via Ollama — rejected: GPU hosting (~£150-400/month) exceeds API cost; instruction-following degrades; no prompt caching.
- Groq for inference — fast but limited model selection and less stable pricing. Use case for future speed-sensitive features only.

### 3.3 Infrastructure and hosting

| Component | Choice | Why |
|---|---|---|
| Compute | Hetzner Cloud CX22 (Phase 1) | €4.50/month. 2 vCPU, 4GB RAM, 40GB NVMe. Plenty for monolithic app + Postgres. |
| Storage backups | Backblaze B2 | $6/TB/month. S3-compatible. Nightly `pg_dump` + code backup. |
| DNS + email forwarding | Cloudflare | Free tier covers DNS and transactional email forwarding for bidequity.co.uk. |
| TLS certificates | Let's Encrypt via Caddy | Automatic. Caddy acts as reverse proxy and handles certs transparently. |
| Reverse proxy | Caddy 2.x | Zero-config HTTPS. Simpler than Nginx for a single-site deployment. |
| Monitoring | Healthchecks.io (free tier) | Dead-man's switch for scheduled jobs. Alerts to email/SMS if a cron misses. |
| Error tracking | Sentry (free tier — 5k events/month) | Exception capture and alerting. Free tier is generous for this scale. |
| Uptime monitoring | UptimeRobot (free tier) | 50 monitors, 5-min interval. Dashboard uptime. |
| Secrets management | Environment variables via Doppler (free tier) or Hetzner's env injection | Doppler for secret rotation and audit. Free tier sufficient. |

**Alternatives considered**

- DigitalOcean — twice the price of Hetzner for equivalent spec. Rejected on cost.
- AWS EC2 — operational overhead (IAM, security groups, CloudWatch) unjustified for personal brand infrastructure.
- Fly.io — good alternative; main issue is cold-start pricing model less predictable than Hetzner flat rate.
- Railway/Render — acceptable alternatives at ~3x Hetzner cost; preference if Paul wants zero VPS administration.
- Nginx instead of Caddy — more complex config for no gain at this scale.

### 3.4 Publishing and distribution

| Component | Choice | Why |
|---|---|---|
| LinkedIn publishing | LinkedIn Marketing Developer Platform API (direct) | No intermediary. One OAuth flow for BidEquity company page. Saves Buffer's £12/month. Full control. |
| Newsletter platform | Beehiiv (Launch tier — free to 2,500 subscribers) | API-first. Free tier generous. Better deliverability than Substack at scale. Clean design. |
| Email transactional | Cloudflare Email Routing | Free. For contact forms and system alerts. |
| Content scheduling | In-application (cron-driven) | No third-party scheduler. Cheaper and keeps editorial state in one place. |
| Image generation (optional) | Anthropic Claude + canvas (SVG) or Unsplash API for stock | BidEquity 'Warm Logic' aesthetic can be produced as SVG inline. Stock photos via Unsplash (free tier). |

**Alternatives considered**

- Buffer/Publer/Hootsuite — £10-30/month. Rejected: dashboard already exists; direct LinkedIn API posting is a half-day of work.
- Substack — rejected for less granular API, Substack-branded sending, and lower growth ceiling.
- Ghost — self-hosted; meaningful time sink to run vs Beehiiv's free tier.
- ConvertKit/Mailchimp — over-specified for a simple weekly digest.

### 3.5 Development and deployment

| Component | Choice | Why |
|---|---|---|
| Version control | GitHub (private repo) | Standard. Free for private. GitHub Actions for CI. |
| CI/CD | GitHub Actions | Runs tests on PR. Deploys on merge to `main` via SSH + systemd restart. |
| Deployment style | Rsync + systemd (single binary) | No containers. Copy code, run migrations, restart service. Fast, debuggable. |
| Database migrations | Alembic | Standard SQLAlchemy migration tool. |
| Local development | Docker Compose (Postgres only) + uv-managed venv | Runs local Postgres with pgvector in container; Python locally for fast iteration. |
| Environment config | `.env` files via python-dotenv; production via Doppler | Simple locally, audited in production. |

**Alternatives considered**

- Docker for production — adds operational complexity (image registry, compose, volumes) for no benefit on a single-machine deployment. Revisit if moving to multi-service.
- GitLab CI — functionally equivalent; GitHub chosen for ecosystem and Claude Code integration.
- Fly.io deployment — possible; Fly's deploy model is more complex than rsync+systemd for this scale.

---

## 4. Data Model

All data lives in one PostgreSQL database. The schema is designed for append-mostly workload with immutable audit history. Rows are never hard-deleted in the core content tables; deprecated items are flagged and retained for learning.

### 4.1 Entity relationships

- `sources` (1) → `items` (many): each item originates from a source
- `items` (1) → `classifications` (many): each classification is a versioned assessment of an item
- `items` (1) → `drafts` (many): each draft is a generated piece for editorial review
- `drafts` (1) → `publications` (0..1): an approved draft becomes a publication
- `publications` (1) → `metrics` (many): post-hoc engagement data
- `editorial_actions` (many): append-only log of operator decisions, used for learning

### 4.2 Table: `sources`

Seeded from the BidEquity UK Public Sector Source Map spreadsheet. Managed through the dashboard once live.

```sql
CREATE TABLE sources (
  id              BIGSERIAL PRIMARY KEY,
  name            TEXT NOT NULL,
  owner           TEXT,                        -- e.g. 'Ministry of Defence'
  category        TEXT NOT NULL,               -- e.g. 'Official Blogs'
  sector          TEXT NOT NULL,               -- e.g. 'Defence'
  url             TEXT UNIQUE NOT NULL,
  feed_url        TEXT,                        -- RSS/Atom if available
  feed_type       TEXT NOT NULL,               -- 'rss' | 'api' | 'scrape_static' | 'scrape_js'
  cadence         TEXT NOT NULL,               -- 'daily' | 'weekly' | 'monthly'
  signal_strength TEXT NOT NULL,               -- 'high' | 'medium' | 'low'
  priority_score  SMALLINT NOT NULL,
  active          BOOLEAN NOT NULL DEFAULT true,
  last_polled_at  TIMESTAMPTZ,
  last_success_at TIMESTAMPTZ,
  consecutive_failures INT NOT NULL DEFAULT 0,
  notes           TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 4.3 Table: `items`

One row per unique piece of content ingested. Dedupe by `content_hash` (MD5 of normalised body text) and semantic similarity (via embeddings).

```sql
CREATE TABLE items (
  id              BIGSERIAL PRIMARY KEY,
  source_id       BIGINT NOT NULL REFERENCES sources(id),
  external_id     TEXT,                        -- source's own ID if available
  url             TEXT NOT NULL,
  title           TEXT NOT NULL,
  author          TEXT,
  body_text       TEXT NOT NULL,               -- full extracted body
  body_preview    TEXT,                        -- first 500 chars for fast browsing
  content_hash    CHAR(32) NOT NULL,           -- MD5 of normalised body
  embedding       VECTOR(1024),                -- voyage-3-lite or equivalent
  published_at    TIMESTAMPTZ,                 -- source's stated publication time
  ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  language        TEXT NOT NULL DEFAULT 'en',
  raw_metadata    JSONB,                       -- feed metadata, headers, etc.
  UNIQUE (content_hash)
);

CREATE INDEX idx_items_embedding ON items USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_items_published_at ON items(published_at DESC);
CREATE INDEX idx_items_source_id ON items(source_id);
```

### 4.4 Table: `classifications`

Claude's assessment of each item. Versioned to allow prompt iteration without losing history.

```sql
CREATE TABLE classifications (
  id                  BIGSERIAL PRIMARY KEY,
  item_id             BIGINT NOT NULL REFERENCES items(id),
  prompt_version      TEXT NOT NULL,           -- e.g. 'classifier-v3.2'
  relevance_score     SMALLINT NOT NULL,       -- 0–10
  signal_strength     TEXT NOT NULL,           -- 'high' | 'medium' | 'low'
  signal_type         TEXT NOT NULL,           -- 'procurement' | 'policy' | 'oversight' | 'financial' | 'leadership' | 'other'
  sectors             TEXT[] NOT NULL,         -- e.g. ['Defence', 'Justice']
  buyers_mentioned    TEXT[],
  suppliers_mentioned TEXT[],
  programmes_mentioned TEXT[],
  summary             TEXT NOT NULL,
  pursuit_implication TEXT,
  content_angle_hook  TEXT,
  cost_usd            NUMERIC(10,6),
  latency_ms          INT,
  classified_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_class_item_id ON classifications(item_id);
CREATE INDEX idx_class_relevance ON classifications(relevance_score DESC);
```

### 4.5 Table: `drafts`

Generated content ready for editorial review. One item can produce multiple drafts if regenerated.

```sql
CREATE TABLE drafts (
  id               BIGSERIAL PRIMARY KEY,
  item_id          BIGINT NOT NULL REFERENCES items(id),
  cluster_id       BIGINT REFERENCES clusters(id),  -- if grouped with related items
  prompt_version   TEXT NOT NULL,
  linkedin_post    TEXT NOT NULL,
  newsletter_para  TEXT NOT NULL,
  so_what_line     TEXT NOT NULL,
  supporting_points JSONB,                     -- array of strings
  cost_usd         NUMERIC(10,6),
  generated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  status           TEXT NOT NULL DEFAULT 'pending'  -- 'pending' | 'approved' | 'edited' | 'rejected' | 'saved'
);
```

### 4.6 Table: `clusters`

Groups of related items covering the same story or programme. Reduces redundant drafts.

```sql
CREATE TABLE clusters (
  id              BIGSERIAL PRIMARY KEY,
  theme           TEXT NOT NULL,                -- short label
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  item_ids        BIGINT[] NOT NULL
);
```

### 4.7 Table: `publications`

Approved drafts that have been or will be published.

```sql
CREATE TABLE publications (
  id              BIGSERIAL PRIMARY KEY,
  draft_id        BIGINT NOT NULL REFERENCES drafts(id),
  channel         TEXT NOT NULL,               -- 'linkedin' | 'newsletter'
  final_content   TEXT NOT NULL,               -- post-edit final text
  scheduled_for   TIMESTAMPTZ NOT NULL,
  published_at    TIMESTAMPTZ,
  external_id     TEXT,                        -- LinkedIn URN or Beehiiv post ID
  external_url    TEXT,
  status          TEXT NOT NULL DEFAULT 'scheduled'  -- 'scheduled' | 'published' | 'failed'
);
```

### 4.8 Table: `metrics`

Engagement data pulled post-publication at 24h, 72h, and 7d intervals.

```sql
CREATE TABLE metrics (
  id              BIGSERIAL PRIMARY KEY,
  publication_id  BIGINT NOT NULL REFERENCES publications(id),
  measured_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  checkpoint      TEXT NOT NULL,               -- '24h' | '72h' | '7d'
  impressions     INT,
  reactions       INT,
  comments        INT,
  shares          INT,
  clicks          INT,                         -- for newsletter
  opens           INT,                         -- for newsletter
  raw_response    JSONB
);
```

### 4.9 Table: `editorial_actions`

Append-only log of every editorial decision. Feeds back into classifier tuning and prompt improvement.

```sql
CREATE TABLE editorial_actions (
  id              BIGSERIAL PRIMARY KEY,
  draft_id        BIGINT NOT NULL REFERENCES drafts(id),
  action          TEXT NOT NULL,               -- 'approve' | 'edit' | 'reject' | 'save'
  original_text   TEXT,
  edited_text     TEXT,
  reason          TEXT,                        -- optional operator reason
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 4.10 Topic intelligence tables (v1.1)

Four additional tables support the Topic Intelligence Layer. These are added in Ticket 11 (see section 12) after the core pipeline is running.

### 4.11 Table: `topics`

Broad themes the classifier tags against. Seeded from `config/topics_seed.csv` (see topic_taxonomy_starter.xlsx starter file).

```sql
CREATE TABLE topics (
  id              BIGSERIAL PRIMARY KEY,
  slug            TEXT UNIQUE NOT NULL,        -- 'ai-public-sector'
  name            TEXT NOT NULL,               -- 'AI in UK public sector'
  description     TEXT,
  sectors         TEXT[] NOT NULL,             -- primary + cross-cutting sectors
  keywords        TEXT[] NOT NULL,             -- phrase triggers for matching
  bid_equity_relevance TEXT,                   -- why this topic matters
  active          BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 4.12 Table: `debates`

Live questions on which sources take positions. Seeded from specs in `/prompts/debates/`.

```sql
CREATE TABLE debates (
  id              BIGSERIAL PRIMARY KEY,
  slug            TEXT UNIQUE NOT NULL,        -- 'ai-procurement-centralisation'
  topic_id        BIGINT NOT NULL REFERENCES topics(id),
  question        TEXT NOT NULL,
  pole_a_label    TEXT NOT NULL,               -- e.g. 'centralisation'
  pole_b_label    TEXT NOT NULL,               -- e.g. 'federation'
  spec_path       TEXT NOT NULL,               -- path to full markdown spec
  active          BOOLEAN NOT NULL DEFAULT true,
  opened_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  retired_at      TIMESTAMPTZ
);
```

### 4.13 Table: `item_topics`

Many-to-many between items and topics. Populated by the classifier as part of its normal pass.

```sql
CREATE TABLE item_topics (
  item_id         BIGINT NOT NULL REFERENCES items(id),
  topic_id        BIGINT NOT NULL REFERENCES topics(id),
  confidence      NUMERIC(3,2) NOT NULL,       -- 0.00 to 1.00
  sub_theme       TEXT,                        -- populated by theme decomposition
  matched_keywords TEXT[],                     -- audit: which keywords drove the match
  classified_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (item_id, topic_id)
);
CREATE INDEX idx_item_topics_topic ON item_topics(topic_id);
CREATE INDEX idx_item_topics_sub_theme ON item_topics(topic_id, sub_theme);
```

### 4.14 Table: `item_stances`

Stance scores for items that are relevant to a live debate. Most items have zero stance entries.

```sql
CREATE TABLE item_stances (
  item_id         BIGINT NOT NULL REFERENCES items(id),
  debate_id       BIGINT NOT NULL REFERENCES debates(id),
  stance          SMALLINT NOT NULL,           -- -2 strongly critiques, -1 critiques, 0 neutral, 1 supports, 2 strongly supports
  confidence      NUMERIC(3,2) NOT NULL,
  excerpt         TEXT,                        -- max 200 chars
  classified_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (item_id, debate_id)
);
CREATE INDEX idx_item_stances_debate ON item_stances(debate_id);
```

### 4.15 Materialised view: `topic_state`

Refreshed nightly. Carries the momentum math for each active topic.

```sql
CREATE MATERIALIZED VIEW topic_state AS
SELECT
  t.id AS topic_id,
  t.slug,
  t.name,
  COUNT(DISTINCT it.item_id) FILTER (WHERE i.ingested_at > now() - interval '7 days')  AS items_7d,
  COUNT(DISTINCT it.item_id) FILTER (WHERE i.ingested_at > now() - interval '30 days') AS items_30d,
  COUNT(DISTINCT it.item_id) FILTER (WHERE i.ingested_at > now() - interval '90 days') AS items_90d,
  COUNT(DISTINCT i.source_id) FILTER (WHERE i.ingested_at > now() - interval '30 days') AS source_diversity_30d,
  -- velocity = delta between this week and last week
  COUNT(DISTINCT it.item_id) FILTER (WHERE i.ingested_at > now() - interval '7 days')
    - COUNT(DISTINCT it.item_id) FILTER (
        WHERE i.ingested_at > now() - interval '14 days'
          AND i.ingested_at <= now() - interval '7 days'
      ) AS velocity_wow,
  now() AS refreshed_at
FROM topics t
LEFT JOIN item_topics it ON it.topic_id = t.id
LEFT JOIN items i ON i.id = it.item_id
WHERE t.active
GROUP BY t.id, t.slug, t.name;

CREATE UNIQUE INDEX idx_topic_state_topic ON topic_state(topic_id);
```

Derived fields `topic_state_label` (emerging / accelerating / established / decaying) are computed in application code from these raw counts; see section 8.4.

---

## 5. Ingestion Pipeline (Stages 1-2)

### 5.1 Goals

- Poll ~76 tier-1 sources on their appropriate cadence
- Extract clean body text and metadata
- Detect and skip duplicates at both exact (content_hash) and semantic (embedding similarity) levels
- Persist to the `items` table with full provenance
- Fail gracefully — individual source failures must not break the pipeline

### 5.2 Scheduling strategy

| Job | Schedule | Sources or action |
|---|---|---|
| Tier 1 daily sources | Every 4 hours | Find a Tender, Contracts Finder, NAO, PublicTechnology, HSJ |
| Tier 1 weekly sources | Every 24 hours at 06:00 UTC | Most think tanks, most committees, weekly trade press |
| Tier 1 monthly sources | Every Monday at 07:00 UTC | Monthly blogs, quarterly reports |
| Semantic dedupe + embedding | Every 30 minutes | Runs after each ingest batch completes |
| Dead-source check | Daily at 09:00 UTC | Flags any source with zero new items in 14 days |
| Backup + `pg_dump` | Daily at 02:00 UTC | Upload to Backblaze B2 |

### 5.3 Source-type handlers

The ingest worker dispatches to one of four handlers based on `feed_type`:

**`rss` handler**
Uses feedparser. Per feed, fetch entries; for each entry not yet seen (by URL or GUID), fetch full article HTML if present, extract body text using readability-lxml or trafilatura, persist.

**`api` handler**
For sources with structured APIs (Find a Tender OCDS, Contracts Finder, Parliament committees). Handler-specific Python modules in `/ingest/handlers/` named `api_find_a_tender.py` etc. Each handler exports `fetch(since: datetime) → List[Item]`.

**`scrape_static` handler**
For HTML pages without feeds. httpx + selectolax. CSS selectors configured per source in `sources.notes` JSONB. Output identical to RSS handler.

**`scrape_js` handler**
Playwright. Only used where JavaScript is required (dynamic filters, SPAs). Adds ~500MB dependency and longer runtime; minimise use.

### 5.4 Dedupe logic

1. Compute `content_hash` as MD5 of normalised body (lowercased, whitespace-collapsed, first 2,000 chars).
2. Attempt insert; if UNIQUE constraint on `content_hash` fails, skip the item and log.
3. After insert, compute embedding via batch embedding job.
4. Every 30 minutes, for items ingested in the last 24h, run k-nearest-neighbours search (k=3) over earlier items. If cosine similarity > 0.94 with an earlier item from the same story cluster, mark as `semantic_duplicate`.
5. Semantic duplicates are retained in the database but excluded from classification (reduces API cost).

### 5.5 Pre-filter layer (cost saving)

Before classification, a cheap regex pre-filter drops items that mention none of: target sectors, named buyers, known programmes, or keyword triggers ('procurement', 'framework', 'tender', 'strategy', 'inspection', 'report', 'announced', 'launched').

Empirical target: 40–60% drop rate. Items dropped here are not classified by Claude, saving API cost with negligible quality cost (the discarded items are almost always irrelevant).

Filter rules live in `/config/prefilter.yaml` and are version-controlled.

### 5.6 Error handling and retries

- Transient failures (HTTP 5xx, network): exponential backoff, 3 retries over 15 minutes.
- Permanent failures (HTTP 404, 410): increment `consecutive_failures` on source. After 5 consecutive failures, set `active=false` and alert.
- Parse failures: log and skip. Don't kill the batch.
- Observability: every batch logs item count, failure count, duration, and Claude API cost to a `runs` table.

---

## 6. Classification Stage (Stage 3)

### 6.1 Purpose

The classifier assesses every candidate item (post pre-filter) against the BidEquity editorial and pursuit-intelligence remit. Its output determines which items flow to draft generation. Its quality directly governs editorial time and content relevance.

### 6.2 Model and economics

- Model: `claude-haiku-4-5`
- Volume assumption: ~120 items/day post pre-filter → ~3,600 items/month
- Average input: ~1,200 tokens (title + first 300 words of body + metadata)
- Average output: ~350 tokens (structured JSON)
- System prompt: ~2,000 tokens (cached)
- Estimated monthly cost before optimisations: ~£32
- After prompt caching (90% cache hit on system prompt) + batching (50% discount): ~£8-10/month

### 6.3 Prompt design

The classifier prompt has four parts: role, taxonomy, rubric, and output contract. Each is versioned and stored as a separate file to allow hot-swapping without code change.

**Role (`role.md`)**
Defines the persona: a senior public-sector bid intelligence analyst with expertise in UK procurement, specifically assessing content for potential commentary by a strategic pursuit consultancy (BidEquity).

**Taxonomy (`taxonomy.yaml`)**
Structured reference data passed into the system prompt: sector definitions; the 120-source register (name → category → sector mapping); known UK public-sector buyers and suppliers; active programmes (ESN, Common Platform, FDP, SKYNET 6, etc); BidEquity's content angles and topic areas.

**Rubric (`rubric.md`)**
Explicit scoring criteria for the 0–10 relevance scale with worked examples. Key distinctions:

- **10**: Direct, named, immediate pursuit signal (e.g. new framework ITT published in a target sector).
- **8–9**: Strong leading indicator (e.g. NAO report on an active programme; SRO appointment; policy paper).
- **6–7**: Contextual — relevant trend or theme supporting a point of view.
- **4–5**: Ambient — background knowledge but not immediately actionable.
- **0–3**: Irrelevant or off-topic.

**Output contract (`output_schema.json`)**
JSON Schema that defines the exact shape of the classifier response. Haiku called with `response_format: json_object` and validated on return. Malformed responses are retried once then logged.

Example response:

```json
{
  "relevance_score": 8,
  "signal_strength": "high",
  "signal_type": "procurement",
  "sectors": ["Defence"],
  "buyers_mentioned": ["MOD", "DE&S"],
  "suppliers_mentioned": [],
  "programmes_mentioned": ["SKYNET 6"],
  "summary": "MOD has released the final Invitation to Negotiate for the SKYNET 6 Wideband Satellite System, marking a major step in UK military satcom procurement.",
  "pursuit_implication": "Primes with satcom capability should now be resourcing full bid teams; sub-prime opportunities for specialist subsystems will follow within 8-12 weeks.",
  "content_angle_hook": "What SKYNET 6's ITN release signals about the pace of MOD's new procurement cadence under Defence Reform."
}
```

### 6.4 Few-shot examples

The system prompt includes 8 curated examples covering edge cases: a high-signal procurement, a high-signal policy piece, a medium-signal blog post, a low-signal news item, a news item about a different sector (should score low), an NAO report, a council announcement, and an industry body press release.

Examples are stored in `/prompts/examples/classifier/` and appended to the system prompt dynamically.

### 6.5 Quality gate

Before each prompt version is promoted from staging to production, it must score ≥ 80% agreement on a golden set of 50 hand-labelled items. The eval harness lives in `/evals/classifier_eval.py`.

Prompt versions are named semantically (`classifier-v3.2.md`). Rollback is instant by changing the active version file.

### 6.6 Batching and caching

- Items are queued on arrival; batch worker runs every 6 hours.
- Each batch submits up to 500 items to the Message Batches API.
- System prompt is cached with 1-hour TTL. Cache hit rate ~95% within a batch.
- Batch results return asynchronously (typically within 30 minutes).
- For items with score ≥ 7 where immediate processing matters (rare), a real-time fast-path exists bypassing the batch queue.

---

## 7. Draft Generation Stage (Stage 4)

### 7.1 Purpose

The generator takes items with classification score ≥ 7 and produces editorial-ready drafts in BidEquity's voice: a LinkedIn post, a newsletter paragraph, and supporting material. This is where the pursuit lens is applied.

### 7.2 Model and economics

- Model: `claude-sonnet-4-6`
- Volume assumption: ~20 items/week post-classification → ~80/month
- Average input: ~5,000 tokens (item body + brand voice context + examples)
- Average output: ~800 tokens
- Estimated monthly cost with prompt caching: ~£5-7/month

### 7.3 Input context

The generator receives:

1. The item body and classification metadata
2. Any clustered related items (up to 3)
3. BidEquity brand voice spec (`brand_voice.md`)
4. Paul's how-I-work preferences (`how_i_work.md`)
5. The current week's already-published content (to avoid repetition)
6. Three recent high-performing posts as style anchors

### 7.4 Prompt design

The generator prompt is structured as:

**System prompt (cached)**
- Role: BidEquity editorial voice — strategic pursuit consultancy
- Brand voice rules (Warm Logic aesthetic, tone, length constraints)
- Structural template for LinkedIn (hook, development, pursuit-lens insight, soft CTA)
- Template for newsletter paragraph (one sentence per idea, signposted)
- Hard constraints: never name a specific active bid; never make investment recommendations; always cite sources; never fabricate quotes

**User prompt (per item)**
- Item body text
- Classifier output
- Any cluster context

**Output contract**
Structured response with sections: `linkedin_post`, `newsletter_paragraph`, `so_what_line`, `supporting_points` (array of 3), `suggested_image_prompt` (optional).

### 7.5 The 'pursuit lens' — the defining prompt element

The single sentence that differentiates BidEquity content from generic commentary is the 'pursuit implication'. The prompt is explicit:

> "For every piece, the insight must answer: what does this mean for someone deciding whether to pursue a bid? Not 'this is interesting news' — 'here's the move'."

Worked examples are embedded in the prompt showing the contrast between generic trade-press framing and pursuit-lens framing on the same underlying item.

### 7.6 Clustering and consolidation

Before generation, a clustering pass groups items with cosine similarity > 0.85 within a 7-day window. Each cluster produces ONE draft, not N drafts. This prevents publishing three LinkedIn posts about the same MOD announcement in different wrappings.

### 7.7 Integration with topic intelligence (v1.1)

When the Topic Intelligence Layer is live (from month 4-5 of implementation), the generator receives additional context per item:

- The topics the item is tagged to, and each topic's current momentum state
- Any debate stances the item expresses, with pole labels
- The sub-theme within the topic, if assigned

This context enables the generator to produce drafts that frame individual items against broader trends. For example, an item tagged to `ai-public-sector` with a rising momentum score and a strongly-critiques stance on `ai-procurement-centralisation` would be drafted differently from the same item with no topic or debate tags. The pursuit lens becomes sharper when the item is positioned against a trend rather than in isolation.

---

## 8. Topic Intelligence Layer (Stage 3A)

### 8.1 Purpose

The Topic Intelligence Layer sits between classification (stage 3) and draft generation (stage 4). It enriches the per-item classifier output with three cross-item intelligences: which topics an item belongs to, where it sits on active debates, and how its parent topic is trending over time. The result is that draft generation, the dashboard, and the weekly digest can answer not just "what happened" but "what does this mean against what's happening".

This layer is new in v1.1 and is intentionally deferred to month 3-6 of implementation. It depends on sufficient historical classification data; running the momentum math or theme decomposition over a handful of items produces noise.

### 8.2 The four components

The layer has four components, built in sequence across tickets 11-13.

**Topic tagging.** Each item is matched against the active topic list at classification time. Matches are stored in `item_topics` with a confidence score. Items may match zero, one, or several topics.

**Stance detection.** For each live debate, items genuinely relevant to the debate are scored on a five-point stance scale from strongly critiques (-2) to strongly supports (+2), with a neutral/descriptive option (0) and an excerpt capturing the evidence.

**Momentum signals.** Pure analytics over the tagging data. For each active topic, the system computes volume, velocity, source diversity, and buyer diversity over rolling windows. These are combined into a topic state label: emerging, accelerating, established, or decaying.

**Theme decomposition.** A weekly Sonnet pass clusters the items tagged to each topic and proposes sub-theme labels. The operator approves, renames, or merges sub-themes in the dashboard; the system then back-tags historical items with the confirmed sub-theme.

### 8.3 Implementation pattern — topic tagging

Topic tagging is folded into the existing classifier prompt rather than running as a separate pass. The classifier receives the active topic list in its system prompt and returns a `topics` array as part of its normal JSON output:

```json
{
  ...normal classification fields...,
  "topics": [
    {
      "slug": "ai-public-sector",
      "confidence": 0.92,
      "matched_keywords": ["AI Playbook", "cross-government AI framework"]
    },
    {
      "slug": "procurement-act-implementation",
      "confidence": 0.68,
      "matched_keywords": ["Procurement Act"]
    }
  ]
}
```

Design notes:

- The topic list is passed as a compact YAML block (not the full descriptions) to minimise tokens. The classifier uses the slug + keywords for matching; the fuller description is only loaded when detailed disambiguation is required.
- Topic matching is permissive — when confidence is between 0.5 and 0.7, the match is recorded but flagged for operator review.
- Topics are re-loaded into the system prompt on each batch run, so adding a topic is a zero-downtime change.

Cost: ~200 additional tokens in the system prompt (cached) and ~50 tokens in each response. At 3,600 classifications/month, approximately £1/month added.

### 8.4 Implementation pattern — stance detection

Stance detection runs as a second, conditional pass. After classification completes, a router determines whether any active debates are plausibly relevant to the item (based on topic match and keyword overlap). Only if yes does the stance pass run.

The stance pass sends to the classifier: the full item text, the classifier's topic tags, and the full debate spec(s) for the relevant debate(s). It returns stance scores and excerpts for each relevant debate:

```json
{
  "item_stances": [
    {
      "debate_id": "ai-procurement-centralisation",
      "relevant": true,
      "stance": -1,
      "confidence": 0.75,
      "excerpt": "The proposed framework addresses a real assurance gap. However..."
    }
  ]
}
```

Design notes:

- The router keeps stance pass volume low — typically 10-15% of items trigger it.
- Each debate spec is loaded as a separate cached system-prompt block; adding a debate adds cache entries, not per-call cost.
- Stance entries where `confidence < 0.6` are recorded but not used in downstream aggregations without operator confirmation.

Cost: an additional ~400 tokens per stance call, at 15% of 3,600 items = 540 stance calls/month. Approximately £2-3/month.

### 8.5 Implementation pattern — momentum signals

Momentum is pure SQL over the `item_topics` table, materialised nightly into the `topic_state` view. No AI cost.

The derived `topic_state_label` is computed in application code from the raw counts using simple rules:

| Condition | Label |
|---|---|
| `items_30d < 5` and `velocity_wow >= 0` | emerging |
| `items_30d >= 5` and `velocity_wow > 2` | accelerating |
| `items_30d >= 5` and `abs(velocity_wow) <= 2` | established |
| `items_30d >= 5` and `velocity_wow < -2` | decaying |

These thresholds are initial guesses. They should be tuned after three months of live data based on what feels like a genuine acceleration in your specific domain.

### 8.6 Implementation pattern — theme decomposition

Runs weekly. For each active topic with at least 15 items in the last 90 days, a Sonnet call receives:

- The topic definition and expected sub-themes (from the seed taxonomy, if any)
- A sample of up to 60 items tagged to the topic in the last 90 days (title, source, summary)
- The existing sub-theme labels for this topic (if any)

Returns: proposed sub-theme labels with assignments of the sample items. The operator reviews in the dashboard. Confirmed sub-themes are written back to `item_topics.sub_theme`; rejected ones are discarded.

Design notes:

- Each topic gets at most one decomposition call per week.
- Sub-themes that remain unconfirmed for 14 days are auto-archived.
- Sub-theme distributions over time become a secondary signal surface in the dashboard.

Cost: one Sonnet call per active topic per week. At 10 active topics × ~3,000 tokens each, approximately £1/month.

### 8.7 Content outputs enabled

Three new content types become possible once the layer is running for 60+ days.

**Topic radars.** Periodic (monthly) visuals showing which topics are emerging, accelerating, established, or decaying — filtered by sector or by all. Published as a standalone LinkedIn asset and as a recurring newsletter section. Differentiated from trade-press content because it's quantified: "AI in courts went from 3 items/month to 19 items/month this quarter".

**Stance maps.** When a debate is live and has sufficient data, a visual showing who is saying what. X-axis is stance, Y-axis is source type (government, think tank, industry, press). Each dot is a publication with a hover-over excerpt. This content cannot be produced by trade press at all — it requires the structured data the layer produces.

**Theme-led analysis pieces.** Rather than reacting to individual items, publish when a sub-theme crosses a momentum threshold. "AI procurement governance has accelerated to an average of 8 items/week, with Cabinet Office driving 40% of signal. Here's what's about to happen in procurement frameworks." This is pursuit analysis applied to trends, not events.

### 8.8 Dashboard surfaces

The editorial dashboard (section 9) gains three new views in v1.1:

**Topic Radar.** A visual dashboard of all active topics with current state, velocity, and source composition. Clickable through to the items backing each topic.

**Debate Board.** Per active debate, the stance distribution across sources over time. Highlights shifts in position — for example, when techUK moves from neutral to mildly critical over a quarter.

**Sub-theme Review.** Weekly queue of proposed sub-themes for operator approval, rejection, or merge.

---

## 9. Editorial Dashboard (Stage 5)

### 8.1 Purpose

The operator's single interface with the system. It must be mobile-friendly (triage during the week), fast, and minimise cognitive load. Every interaction should feel like a forward step, not a reopened decision.

### 8.2 Core views

**Inbox**
The default view. Drafts ranked by `relevance_score` descending. Each row shows: title, source, classification summary, `so_what_line`, and inline action buttons (Approve / Edit / Reject / Save).

One-click approve sends the draft to the formatter. Edit opens a modal with the LinkedIn post and newsletter paragraph in editable text areas.

**Scheduled**
Approved items queued for publication. Shows scheduled time, channel, and lets the operator reorder, reschedule, or pull back.

**Published**
Historical view with performance metrics. Filter by channel, date range, sector, signal type. Top-performing items flagged.

**Sources**
The 120-source register. Health indicators (last success, consecutive failures). Toggle active. Add new source.

**Insights**
Derived analytics: what topics perform; which sources produce the most approved content; classifier agreement rate; operating cost this month.

### 8.3 Interaction design principles

- Keyboard shortcuts: `A` (approve), `R` (reject), `E` (edit), `S` (save), `J`/`K` (navigate). Reduces mouse dependence for power-user triage.
- Optimistic UI: actions apply immediately; server confirms asynchronously.
- Mobile-responsive: approve/reject usable on phone; full editing assumed to happen on desktop.
- No alerts for individual items: a digest email arrives every Sunday evening with the week's candidate list.
- No streaks, gamification, or engagement hooks aimed at the operator. It is a tool, not a product.

### 8.4 Authentication

Single-user. Basic auth via Caddy with a bcrypt-hashed password in environment variable. No OAuth complexity needed. A second admin account (Paul's business partner if desired) can be added later.

### 8.5 Technology detail

- FastAPI routes rendering Jinja2 templates.
- HTMX for interactivity (inline edits, infinite scroll, optimistic updates).
- Pico.css for base styling, with custom BidEquity palette overrides.
- AlpineJS for small client-side state (keyboard shortcut handler, modal state).
- No build step. No bundler. No npm dependencies in production.

---

## 10. Publishing and Measurement (Stages 6-8)

### 9.1 Formatting

Approved drafts go through a formatter that transforms the raw text into channel-specific final output.

**LinkedIn**
- Max 3,000 chars; optimal 1,200–1,500.
- Double-line breaks between paragraphs (LinkedIn collapses single breaks).
- Hashtag strategy: 3–5 relevant tags at the end (controlled by generator output and editable in dashboard).
- First line is the hook — rendered as the preview text.
- No em-dashes (LinkedIn renders them as hyphens).
- Optional: one inline image generated via SVG-to-PNG pipeline matching Warm Logic palette.

**Newsletter**
- Compiled weekly every Thursday evening from the week's approved items.
- Template: brief editor's note (manually written or generated + edited), 3–5 item summaries, and a 'deeper cut' (one item expanded).
- Beehiiv's HTML templates used for delivery.

### 9.2 Scheduling

A scheduler job runs every 15 minutes and checks for publications with `scheduled_for <= now() AND status = 'scheduled'`. Matching publications are published via their channel's API.

**LinkedIn API**
- OAuth 2.0 flow completed once during setup.
- `POST /v2/ugcPosts` with author URN of BidEquity company page.
- Token refresh handled by background job 24h before expiry.
- Rate limits: 150 posts/day per page — far above our volume.

**Beehiiv API**
- API key in env var.
- `POST /publications/{id}/posts` with final HTML.
- Status 'draft' initially; promoted to 'confirmed' on successful create.
- Scheduled send via Beehiiv's native scheduling (not re-implemented locally).

### 9.3 Measurement

Three measurement checkpoints: 24h, 72h, and 7d after publication. A worker queries the respective API and writes to `metrics` table.

Fields captured: impressions, reactions, comments, shares (LinkedIn); opens, clicks (Beehiiv).

The Insights dashboard view aggregates these and feeds them back into the system:

- Classifier weekly retraining: high-engagement items' characteristics reinforce the rubric's high-relevance patterns.
- Generator style feedback: top 3 posts over the last 30 days are dynamically inserted into the generator's system prompt as style anchors.
- Source scoring: sources producing high-engagement content see their `priority_score` nudged upward.

---

## 11. Cost Model

### 10.1 Three growth phases

#### Phase 1 — Seed (Months 1–6)

Goal: launch the platform, establish cadence, learn what works. Low content volume, no commercial data, single operator. Topic Intelligence Layer added from month 3-4.

| Component | Monthly £ | Notes |
|---|---|---|
| Hetzner CX22 VPS | £4 | Base infrastructure |
| Claude API — classifier + generator (post-optimisation) | £12 | Optimised with caching + batching + pre-filter |
| Claude API — topic intelligence layer | £4 | +£1 topic tagging, +£2-3 stance detection, +£1 theme decomposition. Added from month 3-4. |
| Backblaze B2 backups | £1 | ~10GB storage |
| Sentry / Healthchecks / UptimeRobot / Cloudflare | £0 | All free tier |
| Beehiiv Launch | £0 | Free up to 2,500 subscribers |
| Doppler secrets | £0 | Free tier |
| Voyage embedding API | £1 | Very low volume |
| Domain (bidequity.co.uk) | £1 | Annualised |
| **Total monthly (months 1-3)** | **£19** | Pre-topic-intelligence |
| **Total monthly (months 4-6)** | **£23** | Target still < £25 |

#### Phase 2 — Build (Months 6–18)

Goal: the newsletter has crossed 1,000 subscribers, LinkedIn following is building, BidEquity services are generating client inquiries. Volume increases; some commercial data is added.

| Component | Monthly £ | Notes |
|---|---|---|
| Hetzner CX32 VPS (upgrade) | £8 | 4 vCPU, 8GB RAM for more concurrent embedding/generation |
| Claude API (higher volume) | £25 | ~5,000 classifications + 150 generations/month |
| Backblaze B2 | £2 | Growing corpus |
| Beehiiv Scale tier (>2,500 subs) | £36 | If subscriber count crosses threshold |
| Tussell subscription (light tier) | £150-250 | Commercial procurement intelligence; tax-deductible business expense |
| Sentry paid tier (if noisy) | £20 | Optional; free tier may still suffice |
| **Total monthly (without Tussell)** | **£91** | Still within personal-brand infra budget |
| **Total monthly (with Tussell)** | **£241** | Justified once BIP/BidEquity revenue references this data |

#### Phase 3 — Scale (18 months+)

Goal: BidEquity is a meaningful brand. Newsletter at 5,000+ subs. LinkedIn generating qualified inbound. The platform begins to support BIP pursuit work directly.

| Component | Monthly £ | Notes |
|---|---|---|
| Hetzner CCX33 dedicated VPS | £30 | 8 vCPU, 32GB RAM; dedicated CPU for consistent latency |
| Claude API (higher volume + more generators) | £60 | Additional generators for client briefings |
| Backblaze B2 | £5 | Larger corpus |
| Beehiiv Scale tier | £79 | 10,000 subscribers |
| Tussell full tier or Stotles | £600 | Full commercial data |
| LinkedIn Sales Navigator (optional) | £65 | For audience research |
| Observability stack paid tiers | £30 | Sentry + advanced uptime |
| Staff / VA (part-time editorial) | £400-800 | 5-10 hours/week editorial support |
| **Total monthly (without staff)** | **£869** | Supported by client revenue |

### 10.2 Cost optimisation principles (carry across all phases)

- Prompt caching on every repeated system prompt. Do not skip this.
- Batch processing for classification. Real-time only when necessary.
- Pre-filter before the LLM sees anything. Regex is free.
- Haiku for structured tasks, Sonnet for creative tasks. Never invert.
- Truncate input aggressively. First 300 words almost always suffice for classification.
- Free tiers are genuine alternatives for monitoring and secrets. Use them.
- Avoid vendor lock-in where switching cost is non-trivial. Portable choices today protect future optionality.

### 10.3 What to spend more on, not less

**Generator model quality.** Sonnet → Opus when Opus is released in a form with better quality-to-latency. Editorial time is the real scarce resource, and better drafts reduce editing time more than better classifier reduces API time.

**Prompt engineering effort.** Invest in the golden eval set, few-shot examples, and version testing. This is where the real leverage sits.

**Monitoring.** A scraper silently failing for two weeks costs more than any line-item in the cost table.

---

## 12. Implementation Roadmap

### 12.1 Structure

Work is structured as ten tickets, each scoped for 1–3 sessions of Claude Code execution. Every ticket has an acceptance test and a rollback path. The sequence builds the least-valuable-first layers that unblock later tickets.

### 12.2 Ticket 1: Project scaffolding and deployment

**Deliverables**
- GitHub repo with Python project managed by `uv`
- FastAPI app with `/healthz` endpoint and Caddy reverse proxy
- Hetzner CX22 provisioned; Debian 12; systemd service; Caddyfile; GitHub Actions deploy pipeline
- Postgres 16 with pgvector extension installed
- Alembic migrations set up
- Environment config via `.env` + python-dotenv locally; systemd `EnvironmentFile` in production
- Sentry, Healthchecks, UptimeRobot accounts wired up
- Backblaze B2 nightly `pg_dump` script

**Acceptance**
Pushing to `main` deploys automatically; `/healthz` returns 200; database migrations apply cleanly; nightly backup appears in B2.

### 12.3 Ticket 2: Data model and seed data

**Deliverables**
- SQLModel definitions for all tables in section 4
- Alembic migration generating the full schema
- Seed script loading the 120 sources from the BidEquity source map spreadsheet
- Admin CLI for CRUD on sources

**Acceptance**
Database contains 120 sources with correct tier classifications; sources list view in dashboard renders them.

### 12.4 Ticket 3: Ingest layer (RSS + API handlers)

**Deliverables**
- RSS handler, implemented with feedparser + trafilatura
- Find a Tender API handler
- Contracts Finder API handler
- APScheduler configuration for the four-hour tier-1 cadence
- Runs table and logging of every ingestion batch
- Pre-filter regex engine reading from `/config/prefilter.yaml`

**Acceptance**
After 24 hours of operation, at least 100 items ingested from at least 20 distinct sources; duplicate detection demonstrably preventing re-insertion; pre-filter dropping 40%+ of items.

### 12.5 Ticket 4: Ingest layer (scrapers + dead source monitoring)

**Deliverables**
- Static scraper with configurable CSS selectors
- Playwright-based JS scraper for the small number of sources that need it
- Daily dead-source check that flags sources with no new items in 14 days
- Embedding worker populating `items.embedding` via Voyage API
- Semantic dedupe job flagging `semantic_duplicate` items

**Acceptance**
All 120 tier-1 sources successfully ingest at least once; embeddings populated; semantic duplicates correctly identified (test with two known-duplicate items).

### 12.6 Ticket 5: Classifier stage

**Deliverables**
- Prompt files in `/prompts/classifier/` (role, taxonomy, rubric, examples, schema)
- Classifier worker using Anthropic Python SDK with prompt caching
- Message Batches integration for 6-hour batching
- Golden eval set (50 hand-labelled items) in `/evals/classifier_golden.json`
- Eval harness producing agreement rate against golden set
- Cost logging per classification in `classifications.cost_usd`

**Acceptance**
Classifier-v1 achieves ≥ 70% agreement on golden set; cost per classification logged; prompt versioning works (can switch versions via config change).

### 12.7 Ticket 6: Generator stage

**Deliverables**
- Prompt files in `/prompts/generator/` including `brand_voice.md` and `how_i_work.md`
- Clustering job that groups similar items within 7-day windows
- Generator worker using Sonnet with prompt caching
- Draft persistence
- Golden set of 10 items with human-written reference drafts for manual quality comparison

**Acceptance**
For the 10 golden items, generator output is judged 'publishable with light edits' by Paul in manual review; clustering demonstrably reduces redundant drafts.

### 12.8 Ticket 7: Editorial dashboard

**Deliverables**
- Inbox, Scheduled, Published, Sources, and Insights views
- HTMX-powered inline actions (approve/edit/reject/save)
- Keyboard shortcuts
- Editorial actions log
- Basic auth via Caddy
- Sunday evening digest email

**Acceptance**
Paul can triage 20 items in < 10 minutes; editing updates persist; mobile view works; keyboard shortcuts functional.

### 12.9 Ticket 8: LinkedIn publishing

**Deliverables**
- LinkedIn OAuth setup flow
- Token refresh job
- LinkedIn formatter transforming drafts to final posts
- Publishing worker picking up scheduled publications
- Error handling (retry, fallback, operator alert)

**Acceptance**
A test draft approved in dashboard publishes to BidEquity company page on schedule; failure case surfaces in dashboard.

### 12.10 Ticket 9: Newsletter publishing

**Deliverables**
- Beehiiv API integration
- Weekly newsletter compiler (Thursday evening cron)
- HTML templating matching Warm Logic aesthetic
- Editor's-note editable block before send

**Acceptance**
Friday 8am a test newsletter sends to the Beehiiv list with the week's approved items correctly ordered and formatted.

### 12.11 Ticket 10: Measurement and feedback loop

**Deliverables**
- LinkedIn metrics worker (24h, 72h, 7d checkpoints)
- Beehiiv metrics worker
- Insights dashboard view with topic performance, cost tracking, and classifier agreement trend
- Monthly auto-generated cost report
- Top-3-posts dynamic injection into generator's system prompt

**Acceptance**
30 days after launch, insights dashboard shows engagement data for all published posts; monthly cost report reconciles with Anthropic billing; generator prompt auto-updates with top posts.

### 12.12 Ticket 11: Topic tagging (v1.1 addition)

**Deliverables**
- `topics` and `item_topics` tables migrated
- Topic taxonomy loaded from `config/topics_seed.csv` (from topic_taxonomy_starter.xlsx)
- Classifier prompt extended with compact topic taxonomy block (cached)
- Classifier response schema extended to include `topics[]` array
- Writer that persists topic matches to `item_topics` with matched keywords
- Dashboard view showing topic tagging volume per topic per week (basic, non-visual)

**Acceptance**
After 14 days of live operation, every active topic has at least one confident match (confidence ≥ 0.7); zero crashes on topic prompt injection; dashboard view shows volume per topic.

### 12.13 Ticket 12: Stance detection (v1.1 addition)

**Deliverables**
- `debates` and `item_stances` tables migrated
- Debate spec loader reading from `/prompts/debates/*.md`
- Three starter debates loaded (from debate_specs.md):
  - `ai-procurement-centralisation`
  - `nhs-digital-incumbency`
  - `govt-inhouse-vs-managed`
- Router that decides whether stance pass runs for each item (topic + keyword overlap)
- Stance pass worker invoking classifier with debate spec(s)
- Quality gate harness: for each new debate spec, Paul scores 5 items manually and compares to classifier output; spec only activates when 80% agreement met
- Dashboard `Debate Board` view showing stance distribution per debate per source type

**Acceptance**
For each starter debate, at least 10 items accumulate stance entries within 30 days; 80% manual-to-classifier agreement demonstrated; false positive rate (items incorrectly flagged as debate-relevant) below 5%.

### 12.14 Ticket 13: Momentum and theme decomposition (v1.1 addition)

**Deliverables**
- `topic_state` materialised view created
- Nightly refresh job for `topic_state`
- Topic state labelling rules implemented in application code (emerging / accelerating / established / decaying)
- Theme decomposition weekly worker (Sonnet, one call per topic with ≥15 items in 90 days)
- Dashboard `Topic Radar` view with visual state indicators
- Dashboard `Sub-theme Review` queue for operator approval
- Generator prompt extended to receive topic context (momentum state, sub-theme) for each item

**Acceptance**
By month 5 (60+ days of data), at least 5 topics have computed state labels that align with operator intuition; sub-theme proposals produced for at least 3 topics and at least 60% of proposals approved by operator; generator draft quality on topic-contextualised items rated higher than baseline by operator in blind review.

### 12.15 Non-ticket ongoing work

- **Weekly**: 30 minutes reviewing classifier disagreements, refining rubric
- **Monthly**: prompt version review; promote winners; rollback losers
- **Quarterly**: source register review; prune dead sources; add new ones based on sector priorities
- **Annually**: full architecture review; consider Phase 2/3 upgrades

---

## 13. Appendices

### 13.1 Environment variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/bidequity

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
CLASSIFIER_MODEL=claude-haiku-4-5
GENERATOR_MODEL=claude-sonnet-4-6

# Voyage
VOYAGE_API_KEY=...

# LinkedIn
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
LINKEDIN_ORG_URN=urn:li:organization:...

# Beehiiv
BEEHIIV_API_KEY=...
BEEHIIV_PUBLICATION_ID=...

# Monitoring
SENTRY_DSN=...
HEALTHCHECKS_BASE_URL=https://hc-ping.com/...

# Dashboard auth
DASHBOARD_USERNAME=paul
DASHBOARD_PASSWORD_HASH=$2b$12$...
```

### 13.2 Directory structure

```
bidequity-platform/
├── pyproject.toml
├── uv.lock
├── Caddyfile
├── .github/workflows/
├── alembic/
├── config/
│   ├── prefilter.yaml
│   ├── sources_seed.csv
│   └── topics_seed.csv              # v1.1 — from topic_taxonomy_starter.xlsx
├── prompts/
│   ├── classifier/
│   │   ├── role.md
│   │   ├── taxonomy.yaml
│   │   ├── rubric.md
│   │   ├── output_schema.json
│   │   └── examples/
│   ├── generator/
│   │   ├── brand_voice.md
│   │   ├── how_i_work.md
│   │   └── templates/
│   └── debates/                      # v1.1
│       ├── ai-procurement-centralisation.md
│       ├── nhs-digital-incumbency.md
│       └── govt-inhouse-vs-managed.md
├── evals/
│   ├── classifier_golden.json
│   ├── classifier_eval.py
│   └── generator_golden.json
├── src/
│   ├── bidequity/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app
│   │   ├── models/                  # SQLModel definitions
│   │   ├── ingest/
│   │   │   ├── handlers/
│   │   │   │   ├── rss.py
│   │   │   │   ├── api_find_a_tender.py
│   │   │   │   ├── api_contracts_finder.py
│   │   │   │   ├── scrape_static.py
│   │   │   │   └── scrape_js.py
│   │   │   ├── prefilter.py
│   │   │   ├── dedupe.py
│   │   │   └── scheduler.py
│   │   ├── intelligence/
│   │   │   ├── classifier.py
│   │   │   ├── generator.py
│   │   │   ├── clusterer.py
│   │   │   ├── topic_tagger.py        # v1.1
│   │   │   ├── stance_detector.py     # v1.1
│   │   │   ├── theme_decomposer.py    # v1.1
│   │   │   ├── momentum.py            # v1.1
│   │   │   └── prompt_loader.py
│   │   ├── dashboard/
│   │   │   ├── routes.py
│   │   │   ├── templates/
│   │   │   └── static/
│   │   ├── publish/
│   │   │   ├── linkedin.py
│   │   │   ├── beehiiv.py
│   │   │   └── formatter.py
│   │   ├── metrics/
│   │   │   ├── collectors.py
│   │   │   └── insights.py
│   │   └── common/
│   │       ├── db.py
│   │       ├── config.py
│   │       └── observability.py
├── tests/
└── scripts/
    ├── backup.sh
    └── seed_sources.py
```

### 13.3 Operational runbook

**Daily (automated, no human action)**
- Ingest runs four times
- Classifier batches twice
- Generator runs once (after morning classifier batch)
- Backup runs at 02:00 UTC
- Dead-source check runs at 09:00 UTC

**Weekly (operator)**
- Sunday evening: receive digest email, plan the week's content
- Monday + Wednesday mornings: 30–45 min editorial triage
- Thursday afternoon: write editor's note for newsletter
- Friday morning: review published newsletter

**Monthly (operator)**
- Review classifier agreement rate; adjust rubric if drift detected
- Review published-post performance; note style anchors
- Review cost report; optimise any overages
- Promote/rollback prompt versions

**Quarterly (operator)**
- Source register audit; prune, add, reclassify
- Architecture health check
- Consider Phase upgrades

### 13.4 Key risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| LinkedIn API deprecation or policy change | Direct publishing stops working; manual posting becomes necessary | Maintain Buffer as fallback (£0 free tier); keep dashboard's 'copy to clipboard' view |
| Anthropic pricing changes | Monthly cost line item moves | Architecture supports model swap; fallback to Haiku-only operation possible |
| Source URL rot from gov reorgs | Silent failure of scrapers | Dead-source monitoring; weekly report on failing sources |
| Prompt drift / quality regression | Draft quality degrades; editorial time increases | Golden eval set; prompt versioning; rollback instant |
| Operator capacity shock (illness, leave) | Content gap | Scheduled queue can carry 2-3 weeks of pre-approved content; VA onboarding plan ready |
| Data breach / unauthorised access | Reputational risk; not much sensitive data, but still | Basic auth, TLS everywhere, rate limiting on dashboard, no PII beyond Paul's credentials |
| Classifier over-filters | Relevant content missed | Weekly 'reject pile' sample review; adjustable relevance threshold per source category |
| Classifier under-filters | Too many candidates, editorial overwhelm | Tighten rubric; pre-filter regex expansion |

### 13.5 Handoff checklist for Claude Code

- This specification document is the source of truth.
- Work ticket-by-ticket in the order defined in section 12.
- Each ticket's acceptance criteria must pass before moving on.
- Keep prompt files under version control from day one — they are production code.
- Every Claude API call logs cost. Spend is observable.
- Use Paul's existing Cowork context files (`about_me.md`, `brand_voice.md`, `how_i_work.md`) to seed the generator prompts.
- Build tests as you go, not at the end. The classifier eval harness is table stakes, not a nice-to-have.
- Bias toward shipping thin slices. Ticket 3's output should already appear in a minimal dashboard before Ticket 4 starts.
- Ask Paul for an editorial sample approval before promoting any prompt version to production.
- **v1.1 inputs** — the Topic Intelligence Layer tickets (11-13) depend on three hand-produced files: `topic_taxonomy_starter.xlsx` (14 active topics for the `topics` table), `debate_specs.md` (three starter debates for `/prompts/debates/`), and the classifier few-shot examples already produced. Load these as seed data in the respective tickets.
- **Sequencing reminder** — Tickets 11-13 must NOT start before the core pipeline (Tickets 1-10) has accumulated at least 30 days of classified items. Running momentum math or theme decomposition on sparse data produces noise, not signal.

### 13.6 Glossary

| Term | Definition |
|---|---|
| ADR | Architecture Decision Record — captures a choice, rationale, and alternatives |
| APScheduler | Python in-process scheduling library |
| Caddy | Web server with automatic HTTPS |
| DXA | Document XML attributes — Word's internal unit (1/1440 inch) |
| Find a Tender | UK's public-sector tender portal, post-Brexit successor to TED |
| Golden set | Hand-labelled benchmark dataset for evaluating prompt quality |
| HTMX | JavaScript library enabling server-driven interactivity without SPA overhead |
| OCDS | Open Contracting Data Standard — JSON schema used by Find a Tender |
| pgvector | PostgreSQL extension for vector similarity search |
| Prompt caching | Anthropic feature that reduces cost on repeated prompt prefixes |
| SRO | Senior Responsible Owner — accountable officer on a UK government programme |
| `uv` | Python package manager from Astral; faster than pip/poetry |

---

*BidEquity Content Platform — Design Specification v1.1*
