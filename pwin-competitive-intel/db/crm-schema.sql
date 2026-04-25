-- BidEquity CRM Schema v2
-- DB location: ~/.pwin/crm.db
-- Separate from bid_intel.db (FTS intelligence data, bulk-replaced on reimport)
-- This DB is operational — never overwritten by ingest
--
-- v2 changes (2026-04-24):
--   opportunities.status — aligned with Obsidian YAML state machine
--   contacts.linkedin_id — stable dedup key for Evaboot CSV imports
--   organisations/contacts PKs remain INTEGER (no UUID needed at this scale)

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ── Organisations ────────────────────────────────────────────────────────────
-- Buyers, competitors, and consortium partners we have a relationship with.
-- Soft-linked to bid_intel.db via fts_buyer_id / fts_supplier_id (no FK
-- constraint across DBs — join manually when needed).

CREATE TABLE IF NOT EXISTS organisations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL,
    type             TEXT    NOT NULL CHECK(type IN ('buyer','supplier','both')),
    relationship     TEXT    NOT NULL DEFAULT 'prospect'
                             CHECK(relationship IN ('prospect','active','lapsed','competitor','partner')),
    fts_buyer_id     INTEGER,   -- soft link → bid_intel.db buyers.id
    fts_supplier_id  INTEGER,   -- soft link → bid_intel.db suppliers.id
    website          TEXT,
    notes            TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ── Contacts ─────────────────────────────────────────────────────────────────
-- People at buyer and supplier organisations.

CREATE TABLE IF NOT EXISTS contacts (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    name                  TEXT    NOT NULL,
    org_id                INTEGER REFERENCES organisations(id),
    role                  TEXT,
    email                 TEXT,
    linkedin              TEXT,
    linkedin_id           TEXT    UNIQUE,   -- stable dedup key for Evaboot CSV imports
    strength              TEXT    DEFAULT 'cold'
                                  CHECK(strength IN ('cold','warm','known','advocate')),
    first_met             TEXT,   -- ISO date
    first_met_context     TEXT,   -- e.g. "7 May Police.AI market engagement session"
    notes                 TEXT,
    last_interaction_date TEXT,   -- ISO date — updated when interaction logged
    created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ── Opportunities ─────────────────────────────────────────────────────────────
-- One row per procurement notice flagged by the daily scan or added manually.
-- Primary key is the notice ref (e.g. BLC0329) — natural key, stable.
--
-- Status lifecycle (mirrors Obsidian YAML frontmatter state machine):
--
--   new              → just ingested, unread
--   watching         → noted, passive monitor, no action taken
--   action_required  → Paul has set an action_type in Obsidian; watcher will fire
--   researched       → watcher generated a research brief in the pursuit file
--   registered_pending → Gmail registration draft created; waiting to send/confirm
--   attending        → registered and attending / attended market engagement session
--   active           → tender live, bid in progress
--   draft_sent       → outreach or campaign draft sent
--   no_bid           → decided not to bid (reason in decision_reason)
--   won
--   lost
--   withdrawn        → buyer withdrew or cancelled the procurement (soft delete)
--   superseded       → replaced by a subsequent notice (ref in decision_reason)

CREATE TABLE IF NOT EXISTS opportunities (
    id                    TEXT    PRIMARY KEY,  -- notice ref, e.g. BLC0329
    title                 TEXT    NOT NULL,
    buyer_org_id          INTEGER REFERENCES organisations(id),
    value                 REAL,
    notice_type           TEXT,   -- UK1 / UK2 / UK4 / UK5
    priority              TEXT    NOT NULL DEFAULT 'medium'
                                  CHECK(priority IN ('high','medium','low')),
    status                TEXT    NOT NULL DEFAULT 'new'
                                  CHECK(status IN (
                                      'new',
                                      'watching',
                                      'action_required',
                                      'researched',
                                      'registered_pending',
                                      'attending',
                                      'active',
                                      'draft_sent',
                                      'no_bid',
                                      'won',
                                      'lost',
                                      'withdrawn',
                                      'superseded'
                                  )),
    action_type           TEXT    CHECK(action_type IN (
                                      'research',
                                      'register',
                                      'reach_out',
                                      'campaign',
                                      'no_action',
                                      NULL
                                  )),
    decision_reason       TEXT,   -- why no_bid / lost / withdrawn / superseded
    published_date        TEXT,   -- ISO date
    registration_deadline TEXT,   -- ISO datetime
    session_date          TEXT,   -- ISO datetime
    tender_expected       TEXT,   -- ISO date
    submission_deadline   TEXT,   -- ISO datetime
    contract_start        TEXT,   -- ISO date
    contract_end          TEXT,   -- ISO date
    notice_url            TEXT,
    pursuit_file          TEXT,   -- path to Obsidian markdown brief
    content_angle         TEXT,   -- article/post idea if relevant
    processed_at          TEXT,   -- ISO datetime, set by watcher after actioning
    created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ── Interactions ──────────────────────────────────────────────────────────────
-- Immutable audit log. Everything that happens, timestamped.
-- opportunity_id, contact_id, org_id are all optional.

CREATE TABLE IF NOT EXISTS interactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL,   -- ISO datetime
    type            TEXT    NOT NULL
                            CHECK(type IN (
                                'email',
                                'call',
                                'meeting',
                                'event',
                                'article_published',
                                'registered',
                                'no_bid',
                                'watcher_action',   -- automated action by file watcher
                                'note'
                            )),
    opportunity_id  TEXT    REFERENCES opportunities(id),
    contact_id      INTEGER REFERENCES contacts(id),
    org_id          INTEGER REFERENCES organisations(id),
    summary         TEXT    NOT NULL,
    outcome         TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ── Actions ───────────────────────────────────────────────────────────────────
-- Task list. Pending actions drive the weekly review report.

CREATE TABLE IF NOT EXISTS actions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    type            TEXT    NOT NULL
                            CHECK(type IN (
                                'register',
                                'attend',
                                'reach_out',
                                'write_content',
                                'monitor',
                                'bid_decision',
                                'follow_up'
                            )),
    opportunity_id  TEXT    REFERENCES opportunities(id),
    contact_id      INTEGER REFERENCES contacts(id),
    due_date        TEXT    NOT NULL,   -- ISO date
    status          TEXT    NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','done','overdue','cancelled')),
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    completed_at    TEXT    -- ISO datetime, set when status → done
);

-- ── Indexes ───────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_opp_status      ON opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opp_priority    ON opportunities(priority);
CREATE INDEX IF NOT EXISTS idx_opp_updated     ON opportunities(updated_at);
CREATE INDEX IF NOT EXISTS idx_opp_buyer       ON opportunities(buyer_org_id);
CREATE INDEX IF NOT EXISTS idx_actions_due     ON actions(due_date, status);
CREATE INDEX IF NOT EXISTS idx_actions_opp     ON actions(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_interactions_opp     ON interactions(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_contacts_org    ON contacts(org_id);
CREATE INDEX IF NOT EXISTS idx_contacts_strength    ON contacts(strength);
CREATE INDEX IF NOT EXISTS idx_contacts_linkedin    ON contacts(linkedin_id);
