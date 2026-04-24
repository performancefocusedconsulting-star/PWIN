-- BidEquity CRM Schema v1
-- DB location: ~/.pwin/crm.db
-- Separate from bid_intel.db (FTS intelligence data, bulk-replaced on reimport)
-- This DB is operational — never overwritten by ingest

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
-- One row per procurement notice that has been flagged by the daily scan or
-- added manually. Primary key is the notice ref (e.g. BLC0329).

CREATE TABLE IF NOT EXISTS opportunities (
    id                    TEXT    PRIMARY KEY,  -- notice ref, e.g. BLC0329
    title                 TEXT    NOT NULL,
    buyer_org_id          INTEGER REFERENCES organisations(id),
    value                 REAL,
    notice_type           TEXT,   -- UK1 / UK2 / UK4 / UK5
    status                TEXT    NOT NULL DEFAULT 'new'
                                  CHECK(status IN (
                                      'new',        -- just ingested, no decision yet
                                      'watching',   -- noted, monitoring
                                      'registered', -- registered for market engagement
                                      'attending',  -- attending / attended session
                                      'active',     -- tender live, bid in progress
                                      'no_bid',     -- decided not to bid
                                      'ignored',    -- dismissed (reason logged)
                                      'won',
                                      'lost'
                                  )),
    decision_reason       TEXT,   -- why ignored / no_bid / lost
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
    created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ── Interactions ──────────────────────────────────────────────────────────────
-- Immutable audit log. Everything that happens, timestamped.
-- opportunity_id, contact_id, org_id are all optional — an interaction can be
-- linked to any combination of them.

CREATE TABLE IF NOT EXISTS interactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL,   -- ISO datetime
    type            TEXT    NOT NULL
                            CHECK(type IN (
                                'email',
                                'call',
                                'meeting',
                                'event',            -- attended a session/event
                                'article_published',
                                'registered',       -- registered for market engagement
                                'no_bid',           -- formal no-bid decision logged
                                'note'              -- general note
                            )),
    opportunity_id  TEXT    REFERENCES opportunities(id),
    contact_id      INTEGER REFERENCES contacts(id),
    org_id          INTEGER REFERENCES organisations(id),
    summary         TEXT    NOT NULL,
    outcome         TEXT,   -- what this interaction led to
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ── Actions ───────────────────────────────────────────────────────────────────
-- Task list. Pending actions drive the weekly review report.

CREATE TABLE IF NOT EXISTS actions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    type            TEXT    NOT NULL
                            CHECK(type IN (
                                'register',      -- register for market engagement
                                'attend',        -- attend a session/event
                                'reach_out',     -- contact someone
                                'write_content', -- write article/post
                                'monitor',       -- watch for tender to drop
                                'bid_decision',  -- make go/no-bid call
                                'follow_up'      -- follow up after interaction
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
CREATE INDEX IF NOT EXISTS idx_opp_updated     ON opportunities(updated_at);
CREATE INDEX IF NOT EXISTS idx_opp_buyer       ON opportunities(buyer_org_id);
CREATE INDEX IF NOT EXISTS idx_actions_due     ON actions(due_date, status);
CREATE INDEX IF NOT EXISTS idx_actions_opp     ON actions(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_interactions_opp     ON interactions(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_contacts_org    ON contacts(org_id);
CREATE INDEX IF NOT EXISTS idx_contacts_strength    ON contacts(strength);
