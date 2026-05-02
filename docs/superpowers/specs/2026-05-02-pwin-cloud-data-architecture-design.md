---
title: PWIN Cloud Data Architecture — Design Specification
date: 2026-05-02
status: draft-for-review
scope: Wave 1 — Competitive Intel + Platform + Plugin Skills + PWIN Qualify
deferred: Wave 2 — Bid Execution, Verdict, Portfolio
---

# PWIN Cloud Data Architecture — Design Specification

## 1. Context and motivation

PWIN currently runs on a SQLite database (`bid_intel.db`, ~1.3 GB) and a collection of JSON files under `~/.pwin/`. The platform is single-user, laptop-bound, and has hit clear limitations in the analytical workloads it needs to support — particularly the cross-table aggregations required for sector intelligence, supplier dossier joins, and longitudinal artefact storage. SQLite is an OLTP engine being asked to do OLAP work; the mismatch is structural, not tunable.

A 31-case end-to-end validation run on 2026-05-02 confirmed both the immediate pain (every supplier profile query timed out on the live API; sector profiles required workaround caps to complete) and the broader architectural ceiling. The platform also blocks several near-term commercial paths: defence engagements require UK sovereign hosting, multi-user access requires server-side state, and the proprietary intelligence layer that PWIN's long-term value depends on cannot compound across pursuits without a proper relational store with versioned artefacts and outcome linkage.

This spec describes the migration to a Google Cloud UK hosted PostgreSQL platform, with the architecture deliberately designed so that:

- The current SQLite + JSON file mess is replaced with a clean, structured data layer
- Defence engagements at OFFICIAL and OFFICIAL-SENSITIVE classifications can be supported without rebuilding
- The longitudinal compounding intelligence layer can be turned on later (year 2) as an additive change, not a rewrite
- Multi-tenant patterns are not implemented but not precluded
- A non-technical operator can run the platform without DevOps support

The scope is deliberately Wave 1 only: the competitive intelligence database, the platform JSON store, the plugin skills supporting the intelligence platform, and PWIN Qualify (both consulting and website variants). Bid Execution, Verdict, and Portfolio are explicitly deferred to Wave 2 and will plug into the same architecture when they migrate.

## 2. Goals and non-goals

### Goals (Wave 1)

- Replace SQLite + JSON file storage with Google Cloud UK PostgreSQL (Cloud SQL)
- Migrate all current data without loss (raw procurement data, canonical layers, dossiers, stakeholder records, framework register, spend transparency)
- Maintain functional equivalence: every current MCP tool and HTTP endpoint continues to work, just against the new data layer
- Bake in capture mechanisms (versioning, provenance, outcome linkage) from day 1, even where their use is deferred
- Build to OFFICIAL classification with strong technical controls, designed so OFFICIAL-SENSITIVE is a process/policy upgrade rather than a re-architect
- Run on managed services exclusively to keep operator burden low (Cloud SQL, Cloud Run, Cloud Storage, Vertex AI, Identity Platform, Cloud Scheduler, Secret Manager)
- Provide reversible cutover with a 14-day rollback window

### Non-goals (Wave 1)

- Multi-tenant data isolation
- Active vector embedding pipeline (the column exists; the pipeline is deferred)
- Cross-pursuit pattern analytics dashboards
- Outcome capture UI (data captured via direct database access for Wave 1)
- ISO 27001 and Cyber Essentials Plus formal certification (separate workstream)
- Bid Execution / Verdict / Portfolio data layer (Wave 2)
- SaaS billing, customer self-service, productisation infrastructure
- Offline-first standalone Qualify with local model (separate decision)

### Out of scope permanently

- Self-hosting any component
- AWS or Microsoft Azure as primary cloud (decided in favour of Google Cloud UK)
- Migration of the Qualify consulting standalone HTML to a different distribution model — it remains an offline-capable file with online platform dependency for AI calls

## 3. Foundational decisions

| Decision | Choice | Rationale |
|---|---|---|
| Cloud provider | Google Cloud (UK region `europe-west2`) | UK sovereign capability including the November 2025 MOD SECRET-tier sovereign cloud; native first-class Anthropic Claude hosting on Vertex AI; Google embedding models on the same platform |
| Database technology | PostgreSQL via Cloud SQL Flexible Server | Industry-standard relational engine; strong analytical query support; pgvector extension for future semantic search; portable across hosting tiers if needed later |
| AI runtime (real-time) | Vertex AI Claude (Sonnet 4.6 / Opus 4.7) | Sovereign UK hosting; same compliance envelope as data; first-class Anthropic partnership |
| AI runtime (heavy generation) | Anthropic Claude.ai subscription | Flat-cost, high-volume; appropriate for batch dossier generation; outputs land in Cloud Storage and ingest into database |
| Embedding model | Google `text-embedding` (Vertex AI) | Same cloud, same compliance envelope; Anthropic does not produce embedding models |
| Compute pattern | Cloud Run for stateless services | Pay-per-request; auto-scales from zero; no server management; UK region |
| Identity | Google Workspace SSO via Identity Platform | Aligned with how UK government uses Microsoft / Google Workspace identity; simple federation path when client identity integration becomes needed |
| Architecture pattern | Existing MCP server + HTTP API both moved to Cloud Run, pointed at PostgreSQL | Preserves accumulated tool logic; no integration rewrite needed; both APIs are industry-aligned (MCP becoming standard, HTTP universal) |
| Classification posture | OFFICIAL with OFFICIAL-SENSITIVE upgrade designed in | Defence engagements likely 6-12 months out; technical foundations ready; upgrade is paperwork plus three configuration changes |
| Tenancy | Single tenant for now, multi-tenant patterns possible | No multi-tenant requirements in Wave 1; design choices do not preclude future multi-tenant addition |
| Approach | "Approach B with capture baked in" | Considered rebuild with the future-proofing tax included — versioning, provenance, outcome linkage on artefacts from day 1 |

### Cost expectations

- Cloud SQL (Small instance, HA): ~£100-150/month fixed
- Cloud Run usage: ~£5-20/month at expected volumes
- Cloud Storage: ~£1-5/month
- Vertex AI Claude API (real-time): ~£20-60/month at expected volumes
- Vertex AI embeddings: trivial when active
- Claude.ai subscription (heavy generation): ~£200/month flat
- **Total all-in: ~£300-450/month**

Costs scale predictably; the fixed Cloud SQL component does not vary with usage volume within reason. The Claude.ai subscription absorbs heavy generation cost regardless of dossier volume.

## 4. Architecture overview

PWIN's runtime will live in a single Google Cloud project in `europe-west2` (London). Inside the project, eight Google Cloud services do the work:

| Service | Job | Cost shape |
|---|---|---|
| Cloud SQL for PostgreSQL | The single database holding all structured data | Fixed (~£100-150/month with HA) |
| Cloud Run (4 services) | Stateless application code: MCP server, HTTP API, ingest pipelines, artefact uploader | Pay-per-request (~£5-20/month) |
| Cloud Storage | Files: dossier staging, intermediate ingest files, archives | Pay per GB (~£1-5/month) |
| Cloud Scheduler | Triggers ingest pipelines on schedules | Free tier sufficient |
| Vertex AI | Claude API + Google embedding models | Pay-per-token (~£20-60/month) |
| Identity Platform | User authentication via Google Workspace federation | Free tier sufficient |
| Secret Manager | API keys, credentials, third-party tokens | Pennies/month |
| Cloud Logging / Monitoring | Audit trail and operational visibility | Free tier sufficient |

The four Cloud Run services:

1. **`mcp-server`** — the existing Node.js MCP server, containerised, pointed at PostgreSQL. Same ~94 typed tools.
2. **`http-api`** — the existing Node.js HTTP API, containerised, pointed at PostgreSQL. Adds a public-tier endpoint for the Qualify website with rate limiting and reduced intelligence injection.
3. **`ingest-pipelines`** — Python services for the FTS daily fetch, Companies House enrichment, OCP weekly refresh, daily pipeline scan, spend transparency monthly fetch. Triggered by Cloud Scheduler.
4. **`artefact-uploader`** — small Python service triggered by Cloud Storage events. Watches the dossier staging bucket; when a file lands, validates, computes provenance, upserts to `intel.artefacts`.

External consumers:
- **Operator's laptop** — Claude Code calls the MCP server in Cloud Run; development continues locally with code pointed at the cloud database.
- **PWIN Qualify (consulting variant)** — single HTML, calls the HTTP API in Cloud Run; retains offline capability for Qualify content but requires the platform online for AI calls.
- **PWIN Qualify (website variant)** — public lead-gen, calls the HTTP API public-tier endpoint; restricted intelligence injection by design.
- **Claude.ai subscription** — operates outside the platform; outputs JSON files that are uploaded to Cloud Storage to enter the artefact ingest pipeline.

## 5. Schema design

The database is divided into four logical schemas with clear responsibilities.

### 5.1 `raw` schema — published facts ingested from external sources

| Table | Description |
|---|---|
| `buyers` | Raw FTS publisher records, one row per buyer-name-as-published |
| `suppliers` | Raw FTS supplier records plus Companies House enrichment columns |
| `notices` | Every procurement notice — tender, award, planning, contract performance (UK7), performance scores (UK9), contract change, cancellation. Distinguished by `notice_type` |
| `lots` | Lot breakdowns within notices |
| `awards` | Individual contract awards with values and contract periods |
| `award_suppliers` | Many-to-many link between awards and supplier records |
| `cpv_codes` | CPV procurement category codes per notice |
| `planning_notices` | Forward pipeline — opportunities being planned, not yet advertised |
| `planning_cpv_codes` | CPV codes per planning notice |
| `spend_transactions` | £25k transparency spend data — sub-organisation level |
| `spend_files_state` | Operational tracking for spend file ingestion |

11 tables, structurally migrated from `bid_intel.db`. Read-heavy, refreshed by overnight pipelines, never edited by hand. Performance notices (UK7/UK9) are stored in `notices` with notice-type filter; an optional `intel.performance_signals` view surfaces them for downstream products.

### 5.2 `intel` schema — derived proprietary layer

**Canonical entity layer:**

| Table | Description |
|---|---|
| `canonical_buyers` | Deduplicated UK public buyer master list (~4,155 entities) |
| `canonical_buyer_aliases` | Alias glossary mapping any raw buyer name variant to its canonical entity |
| `canonical_suppliers` | Splink-derived deduplicated supplier master list (~82,637 entities) |
| `supplier_to_canonical` | Link between raw `suppliers` rows and `canonical_suppliers` |

**Frameworks layer:**

| Table | Description |
|---|---|
| `frameworks` | Canonical UK public procurement framework register |
| `framework_lots` | Lots within each framework |
| `framework_suppliers` | Supplier appointments to frameworks/lots |
| `framework_call_offs` | Call-off contracts under frameworks, matched from FTS notices |

**Stakeholder layer:**

| Table | Description |
|---|---|
| `stakeholders` | Senior civil servants from organogram CSVs (Director tier and above), linked to `canonical_buyer_id` |
| `stakeholder_history` | Versioning of stakeholder records over time |
| `pac_witnesses` | Public Accounts Committee witness records (Director-level SROs) |

**Adjudication staging:**

| Table | Description |
|---|---|
| `adjudication_queue` | Canonical-layer decisions awaiting human review |
| `adjudicator_escalations` | Decisions flagged for escalation |

**Central capture mechanism:**

| Table | Description |
|---|---|
| `artefacts` | Every AI-generated output — buyer/supplier/sector dossiers, incumbency assessments, Qualify reviews, win strategy outputs, and future Wave 2 outputs. Versioned, never overwritten, full provenance metadata, JSONB content, vector embedding column (initially NULL), outcome linkage hooks |

14 tables in `intel` (4 canonical entity + 4 frameworks + 3 stakeholders + 2 adjudication + 1 `artefacts`). The `artefacts` table is the new central addition.

### 5.3 `pursuits` schema — Wave 2 placeholder

| Table | Description |
|---|---|
| `pursuits` | One row per consulting engagement, created at engagement start |
| `outcomes` | Empty for Wave 1; populated when pursuits complete (won/lost/walked/no-bid) with reasons |
| `score_history` | Trajectory of Qualify scores across re-runs per pursuit; links to `artefacts` row |

When Wave 2 products migrate, they add their own tables here (response sections, governance gates, verdict assessments, etc.).

### 5.4 `_meta` schema — operational housekeeping

| Table | Description |
|---|---|
| `ingest_state` | Cursors and checkpoints for ingest pipelines |
| `audit_log` | Security audit trail — every read/write touching sensitive data |

### 5.5 Database views

The existing SQLite views (`v_expiring_contracts`, `v_supplier_wins`, `v_buyer_history`, `v_pwin_signals`, `v_canonical_supplier_wins`) are rebuilt as PostgreSQL views or materialised views depending on refresh requirements. New views may be added (e.g. `intel.performance_signals` to surface UK7/UK9 notices).

### 5.6 Configuration kept outside the database

The following remain as version-controlled JSON files in the code repository, not database tables:

- `sector_knowledge.json`
- `opportunity_types.json`
- `sector_opp_matrix.json`
- `output_schemas.json`
- `reasoning_rules.json`
- `confidence_model.json`
- Few-shot example sets per skill

These benefit from git versioning and are loaded into platform memory at startup.

## 6. Capture model

This is the future-proofing decision that matters most. Once an artefact is overwritten without versioning, that historical state is gone forever. Wave 1 captures everything needed for the year-2 compounding intelligence layer to work, even where the use of that data is deferred.

### 6.1 Three things every artefact carries

Every row in `intel.artefacts` carries metadata in three categories beyond the content itself:

**Identity and subject:**
- Unique UUID
- `artefact_type` from a controlled vocabulary (`buyer_dossier`, `supplier_dossier`, `sector_brief`, `incumbency_assessment`, `qualify_review`, `win_theme`, `solution_spine`, `verdict_assessment`, etc.)
- Foreign keys to canonical entities the artefact concerns: `canonical_buyer_id`, `canonical_supplier_id`, `sector_key`, `pursuit_id`

**Versioning (never overwrite):**
- `version` — incrementing integer
- `supersedes_id` — points to previous version
- `superseded_by_id` — populated on the previous version when a new one arrives
- `status` — `current`, `superseded`, `archived`, `stale`

**Provenance (full audit trail):**
- `generated_at` — exact timestamp
- `generated_by` — user identity
- `generated_via` — channel (`claude.ai-subscription`, `vertex-ai-api`, `manual-upload`)
- `model_name` and `model_version`
- `skill_name` and `skill_version`
- `input_summary` — JSONB summary of inputs
- `input_data_hash` — hash of underlying raw data at generation time, for staleness detection
- `classification` — `OFFICIAL` or `OFFICIAL-SENSITIVE`
- `refresh_due` and `stale_reason`
- `outcome_id` — populated later when outcome data exists
- `embedding` — pgvector column, NULL until embedding pipeline is enabled

### 6.2 Pursuits and outcomes

`pursuits.pursuits` holds engagement records: `name`, `canonical_buyer_id`, `sector_key`, `opportunity_type`, `estimated_value`, `state`, timestamps.

`pursuits.outcomes` holds the result when an engagement closes:
- `outcome` — `won`, `lost`, `walked`, `no-bid`
- `outcome_reason` — controlled vocabulary
- `outcome_notes` — free text
- `final_score` — final PWIN at gate decision
- `contract_value` — if won
- `competitor_winner` — if lost

`pursuits.score_history` holds the Qualify score trajectory across re-runs, linking each score point to the specific `artefacts` row containing the full review.

### 6.3 What's automatic vs manual

| Action | Automatic | Manual |
|---|---|---|
| Generate dossier via Claude.ai | — | Operator action |
| Upload dossier to `artefacts` | ✅ | — |
| Create `artefacts` rows for Qualify reviews | ✅ | — |
| Create a pursuit | ✅ on first artefact, with optional manual creation | Optional |
| Initial pursuit metadata | — | One-time entry per pursuit (~30 seconds) |
| Track score trajectory | ✅ | — |
| Flag stale dossiers | ✅ via `refresh_due` | — |
| Record outcome | — | One-time per pursuit when complete (~1 minute) |
| Embedding generation | ✅ when enabled | — |

Operator burden: ~90 seconds per pursuit lifecycle for capture metadata. Everything else is automatic.

### 6.4 What's deferred to year 2

The data structure supports these from day 1; their active use is deferred:

- Embedding pipeline running on every artefact write
- Pattern-analytics views and dashboards
- Outcome capture UI (Wave 1 uses direct database insert)
- Cross-pursuit similarity search

None require schema changes when activated. Each is an additive feature on already-captured data.

## 7. Services and data flow

### 7.1 Five main data flows

**Flow 1 — Daily FTS ingest (overnight, automated):**
Cloud Scheduler triggers `ingest-pipelines` at 02:00 UTC. The job calls UK FTS OCDS API, paginates, parses notices/awards/lots/suppliers, writes to `raw` schema, updates `_meta.ingest_state` cursor.

**Flow 2 — Dossier generation (manual, semi-automated upload):**
Operator runs buyer-intelligence skill via Claude.ai subscription. ~40 minutes of generation produces structured JSON. Operator drops file in Cloud Storage staging bucket. Storage event triggers `artefact-uploader` Cloud Run service, which validates, computes provenance, upserts to `intel.artefacts` with versioning, marks previous version superseded, archives source file.

**Flow 3 — Real-time Qualify review:**
Consultant clicks "Review my answer" in PWIN Qualify. Browser POSTs to `http-api` Cloud Run service. Service validates session, identifies pursuit/buyer, reads relevant dossier from `intel.artefacts` (latest current version), assembles prompt, calls Claude on Vertex AI (UK region), receives response, writes new `artefacts` row with full provenance, returns response to browser. Total latency budget: under 10 seconds.

**Flow 4 — Operator using Claude Code with MCP server:**
Operator asks Claude something. Claude calls `get_supplier_profile('Serco')` via MCP. Claude Code MCP request to `mcp-server` Cloud Run. Service queries Cloud SQL `intel.artefacts` for current Serco dossier, returns JSON. Claude weaves into response.

**Flow 5 — PWIN Qualify website (public lead-gen):**
Visitor on public URL, HTML loaded from CDN. Browser POSTs to `http-api` public endpoint with rate limiting and reduced intelligence injection. Public-tier prompt sent to Claude on Vertex AI. Response returned. Lead capture writes to a separate `leads` table, not `pursuits`.

### 7.2 Schedule

| Pipeline | Schedule | Trigger |
|---|---|---|
| FTS daily ingest | 02:00 UTC | Cloud Scheduler |
| Companies House enrichment | 03:00 UTC | Cloud Scheduler |
| Canonical layer maintenance | 04:00 UTC | Cloud Scheduler |
| Daily pipeline scan | 06:00 UTC | Cloud Scheduler |
| Spend transparency monthly fetch | 1st of month, 05:00 UTC | Cloud Scheduler |
| OCP weekly refresh | Sundays, 01:00 UTC | Cloud Scheduler |
| Dossier upload | On file landing in staging | Cloud Storage event |
| Real-time API requests | On every request | Cloud Run autoscaling |

## 8. Security posture

### 8.1 OFFICIAL baseline — always on

1. **Encryption at rest** — Google-managed keys for Cloud SQL, Cloud Storage, Cloud Logging by default
2. **Encryption in transit** — TLS 1.3 on every connection; SSL on database connections; no unencrypted paths
3. **UK data residency** — all services configured to `europe-west2` only; replication, backups, compute all UK
4. **Identity** — Google Workspace SSO via Identity Platform; Workload Identity Federation for machine-to-machine
5. **Network security** — Cloud SQL has no public IP; only Cloud Run services in the same project can connect
6. **Audit logging** — every read/write to sensitive tables logged with user, timestamp, operation, source IP, endpoint; 30-day retention default
7. **Secrets management** — credentials in Secret Manager only; never in code, environment variables, or files
8. **Backups and DR** — automatic daily backups, 7-day retention; point-in-time recovery; cross-zone HA replication for failover

### 8.2 Data classification metadata

Every `artefacts` row carries a `classification` field (`OFFICIAL` or `OFFICIAL-SENSITIVE`). For Wave 1, all artefacts default to `OFFICIAL`. The field exists so the upgrade path is "set the right value when ingesting" rather than schema rebuild.

### 8.3 OFFICIAL-SENSITIVE upgrade path

Process and policy changes (most of the upgrade):
- Document an Information Asset Register
- Document data handling rules (RBAC, exports, retention)
- Cyber Essentials Plus certification (~£500-1,500/year)
- ISO 27001 audit if required (~£5-10k first year, ~£2-3k ongoing)
- Train associate consultants

Technical changes (small, non-disruptive):
- Extend audit log retention from 30 days to 14+ months
- Enable customer-managed encryption keys (CMEK)
- Tighten access controls with role-based granularity
- Enable VPC Service Controls
- Stricter session and re-authentication policies

What does NOT change: schema, application code, data structures, basic operational model.

### 8.4 ISO 27001 and Cyber Essentials Plus alignment

Architecture is designed to satisfy both certifications without rework. Technical controls (boundary firewalls, secure configuration, access control, malware protection, patch management) are inherited from Google Cloud's managed services. ISO 27001 controls (asset management, access control, cryptography, operations security, communications security, business continuity, compliance) are addressed by the design as documented. Certification readiness is structural; the audit work itself is a separate workstream.

## 9. Migration approach

Six phases, parallel-run-then-cutover, fully reversible until 14 days post-cutover.

### Phase 0 — Foundation (Week 1)
Provision empty Google Cloud project, Cloud SQL instance, Cloud Storage buckets, Identity Platform, Secret Manager, Cloud Logging, Cloud Scheduler. Configure VPC with private IP for Cloud SQL.

### Phase 1 — Schema (Week 1-2)
Create all four schemas with PostgreSQL-native types. Apply indexes informed by today's performance work. Install pgvector. Create audit triggers. Build database views. Verify with sample inserts.

### Phase 2 — Data migration (Week 2-3)
Export SQLite tables, bulk-load into PostgreSQL with `COPY`. Verify row counts match. Spot-check key entities. Migrate canonical layers, frameworks, stakeholders. Ingest existing dossier JSON files into `intel.artefacts` with proper versioning and provenance.

### Phase 3 — Application services (Week 3-4)
Containerise MCP server (replace `node:sqlite` with `pg`). Containerise HTTP API. Containerise ingest pipelines. Build artefact uploader. Deploy all four to Cloud Run. Add authentication middleware and audit logging.

### Phase 4 — Verification (Week 4-5)
Run the 31-case validation battery. Run full Qualify review end-to-end. Generate fresh dossier through full lifecycle. Verify audit logs, backups, restore. Run FTS daily ingest on new system. Side-by-side comparison with old system.

### Phase 5 — Cutover (Week 5)
Final incremental data migration. Update Qualify HTML apps' API endpoint. Update Claude Code MCP connection. Update Claude.ai dossier output script to write to Cloud Storage. Stop laptop services. SQLite file frozen as backup.

### Phase 6 — Stabilisation (Week 5-6)
Monitor for 14 days. Re-run validation battery. Watch costs. After 14 clean days, archive SQLite to Cloud Storage permanently, decommission laptop services. Document operational runbook.

### 9.1 Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Data conversion bug | Medium | Medium | Verification queries at every step; spot-check 20 entities by hand; SQLite backup retained 30 days |
| Performance regression on PostgreSQL | Medium | Low-Medium | Benchmark all production queries during Phase 4 |
| Cost surprise | Low | Low | Start Small instance; scale up only on metrics |
| Cutover-day issue | Medium | Medium | Comprehensive Phase 4 testing; don't cutover with known issues |
| Dossier upload pipeline misses files | Low | Low | Idempotent uploader; one-off catch-up script |

### 9.2 Rollback strategy

- **Pre-cutover:** old system authoritative; just stop, fix, resume
- **Within 14 days post-cutover:** revert endpoint URLs to laptop; restart local services; SQLite backup still authoritative
- **After 14 days:** rolling back accepts loss of any data only on new system (acceptable risk after stabilisation period)

### 9.3 Realistic timeline

- Optimistic: 4 weeks
- Realistic: 5-6 weeks
- Conservative: 7-8 weeks

Operator time investment: ~10-15 hours configuration/decisions + ~10-15 hours testing/verification across the 5-6 week window. Day-to-day product work continues in parallel.

### 9.4 Parallel feature work during migration

Most current feature work (Qualify v0.2 content, win strategy skills, orchestration layer, prompts, HTML apps, knowledge files) is decoupled from the migration and continues uninterrupted. Three rules govern coordination:

1. Schema changes require coordination — added to both old and new system, or to new only after Phase 2
2. No deep MCP server / HTTP API refactors during weeks 3-4 (the same code is being containerised)
3. The cutover window (~24 hours) is a code freeze for new deployments

## 10. Open questions and decisions to revisit

Items deliberately deferred or marked for later decision:

- **Embedding model selection** — Google's `text-embedding` family chosen by default; revisit when activating semantic search
- **Outcome vocabulary** — controlled list for `outcome_reason` to be defined when first pursuits complete on the platform
- **Embedding refresh cadence** — daily? on every artefact change? deferred until pipeline activation
- **Public Qualify website rate limits** — specific thresholds to be tuned based on traffic
- **Multi-tenant identity model** — how client teams gain restricted access, deferred until first such engagement
- **Local-model offline standalone Qualify variant** — separate decision; Llama 3.1 8B or similar on a stripped intelligence subset for client-meeting demos
- **Bid Execution data model** — Wave 2 design effort, plugs into reserved `pursuits` schema
- **Cyber Essentials Plus / ISO 27001 timing** — separate workstream, kicked off when first defence engagement enters serious conversation

## 11. Appendix: decision log

Brief record of key decisions made during the brainstorming session of 2026-05-02:

- **Cloud choice (Google over Azure/AWS):** UK MOD sovereign accreditation (Nov 2025), native first-class Anthropic Claude on Vertex AI, same-cloud Google embeddings; Azure was the alternative considered, AWS deprioritised after MOD contract loss
- **Cost vs migration risk (start direct on Google rather than Supabase Pro):** the £100-200/month delta over 6-12 months (~£1,200-2,400) is trivial relative to the cost of mid-engagement migration; Day-one defence credibility worth it
- **Approach B over C (capture without active compounding features):** the gap between B+ and C is ~1-2 weeks of build effort plus active embedding compute; capture decisions are irreversible (must do now), use decisions are deferrable; outcome capture model better designed after first pursuits run on platform
- **Generic `artefacts` table over per-type tables:** simpler cross-cutting queries, no schema migrations for new artefact types, uniform compounding intelligence operations later
- **Two-tier AI cost model (Claude.ai for heavy, Vertex AI for real-time):** large dossier generation runs flat-rate via subscription; per-call real-time uses pay-per-token API; fundamentally different economics handled by different paths
- **Configuration files (sector knowledge etc.) stay in repo, not database:** version control via git, edit-by-hand workflow, loaded at startup
- **OFFICIAL classification baseline with OFFICIAL-SENSITIVE upgrade path designed in:** technical foundations included by default at near-zero cost; formal compliance work deferred until client trigger; classification metadata on every artefact enables granular handling later
- **Single-tenant Wave 1, multi-tenant patterns possible:** no current multi-tenant requirement; design choices preserve future option

---

## Sign-off

This spec was developed through structured brainstorming on 2026-05-02. The operator (Patrick Fenton) approved each section in turn:

- Section 1 (high-level architecture): approved
- Section 2 (schema design): approved with comprehensive sweep added
- Section 3 (capture model): approved
- Section 4 (services and data flow): approved
- Section 5 (security posture): approved
- Section 6 (migration approach): approved
- Parallel feature work during migration: approved

Next step: implementation plan via the writing-plans skill.
