-- ============================================================
-- PWIN Competitive Intelligence — Database Schema
-- Source: Find a Tender Service OCDS API (Cabinet Office)
-- ============================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ============================================================
-- BUYERS (contracting authorities)
-- ============================================================
CREATE TABLE IF NOT EXISTS buyers (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    org_type            TEXT,
    devolved_region     TEXT,
    street_address      TEXT,
    locality            TEXT,
    postal_code         TEXT,
    region_code         TEXT,
    contact_name        TEXT,
    contact_email       TEXT,
    contact_telephone   TEXT,
    website             TEXT,
    first_seen          TEXT NOT NULL DEFAULT (datetime('now')),
    last_updated        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_buyers_name ON buyers(name);
CREATE INDEX IF NOT EXISTS idx_buyers_region ON buyers(region_code);
CREATE INDEX IF NOT EXISTS idx_buyers_type ON buyers(org_type);

-- ============================================================
-- SUPPLIERS (winning / shortlisted companies)
-- ============================================================
CREATE TABLE IF NOT EXISTS suppliers (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    companies_house_no  TEXT,
    scale               TEXT,
    is_vcse             INTEGER DEFAULT 0,
    is_sheltered        INTEGER DEFAULT 0,
    is_public_mission   INTEGER DEFAULT 0,
    street_address      TEXT,
    locality            TEXT,
    postal_code         TEXT,
    region_code         TEXT,
    contact_email       TEXT,
    website             TEXT,
    -- Companies House enrichment
    ch_company_name     TEXT,
    ch_status           TEXT,              -- active | dissolved | liquidation | etc.
    ch_type             TEXT,              -- ltd | plc | llp | etc.
    ch_incorporated     TEXT,              -- date
    ch_sic_codes        TEXT,              -- JSON array of SIC codes
    ch_address          TEXT,              -- registered office one-liner
    ch_turnover         REAL,              -- from latest accounts (if filed)
    ch_net_assets       REAL,
    ch_employees        INTEGER,
    ch_accounts_date    TEXT,              -- date of latest accounts
    ch_directors        TEXT,              -- JSON array of current director names
    ch_parent           TEXT,              -- immediate parent company name (if group)
    ch_enriched_at      TEXT,              -- when we last pulled from CH
    first_seen          TEXT NOT NULL DEFAULT (datetime('now')),
    last_updated        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name);
CREATE INDEX IF NOT EXISTS idx_suppliers_scale ON suppliers(scale);
CREATE INDEX IF NOT EXISTS idx_suppliers_coh ON suppliers(companies_house_no);

-- ============================================================
-- NOTICES (one row per OCID — the contracting process)
-- ============================================================
CREATE TABLE IF NOT EXISTS notices (
    ocid                    TEXT PRIMARY KEY,
    buyer_id                TEXT REFERENCES buyers(id),
    latest_release_id       TEXT,

    -- Tender fields
    title                   TEXT,
    description             TEXT,
    procurement_method      TEXT,
    procurement_method_detail TEXT,
    main_category           TEXT,
    legal_basis             TEXT,
    above_threshold         INTEGER DEFAULT 0,

    -- Overall value (tender-level estimate or sum)
    value_amount            REAL,
    value_amount_gross      REAL,
    currency                TEXT DEFAULT 'GBP',

    -- Dates
    tender_end_date         TEXT,
    published_date          TEXT,

    -- Status
    tender_status           TEXT,

    -- Bid intelligence (from bids.statistics)
    total_bids              INTEGER,
    final_stage_bids        INTEGER,
    sme_bids                INTEGER,
    vcse_bids               INTEGER,

    -- Renewal
    has_renewal             INTEGER DEFAULT 0,
    renewal_description     TEXT,

    -- Notice metadata
    notice_type             TEXT,
    notice_url              TEXT,

    -- Latest release tag seen
    latest_tag              TEXT,

    -- Framework fields (added 2026-04-12 for Decision C06)
    is_framework            INTEGER DEFAULT 0,          -- TRUE if this notice establishes a framework agreement
    framework_method        TEXT,                        -- e.g. withReopeningCompetition, withAndWithoutReopeningCompetition
    framework_type          TEXT,                        -- e.g. closed, open
    parent_framework_ocid   TEXT,                        -- OCID of the parent framework (for call-offs)
    parent_framework_title  TEXT,                        -- Name of the parent framework (for call-offs)

    ingested_at             TEXT NOT NULL DEFAULT (datetime('now')),
    last_updated            TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_notices_buyer ON notices(buyer_id);
CREATE INDEX IF NOT EXISTS idx_notices_status ON notices(tender_status);
CREATE INDEX IF NOT EXISTS idx_notices_published ON notices(published_date);
CREATE INDEX IF NOT EXISTS idx_notices_framework ON notices(is_framework);
CREATE INDEX IF NOT EXISTS idx_notices_parent_fw ON notices(parent_framework_ocid);

-- ============================================================
-- LOTS (one row per lot within a notice)
-- ============================================================
CREATE TABLE IF NOT EXISTS lots (
    id                      TEXT PRIMARY KEY,   -- ocid + '-lot-' + lot_id
    ocid                    TEXT NOT NULL REFERENCES notices(ocid),
    lot_number              TEXT NOT NULL,
    title                   TEXT,
    description             TEXT,
    status                  TEXT,
    has_options             INTEGER DEFAULT 0,
    ingested_at             TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_lots_ocid ON lots(ocid);

-- ============================================================
-- AWARDS (one row per award — links to lot and has suppliers)
-- ============================================================
CREATE TABLE IF NOT EXISTS awards (
    id                      TEXT PRIMARY KEY,   -- release award id e.g. 031223-2026-1
    ocid                    TEXT NOT NULL REFERENCES notices(ocid),
    lot_id                  TEXT REFERENCES lots(id),
    title                   TEXT,
    status                  TEXT,
    award_date              TEXT,

    -- Value for this specific award
    value_amount            REAL,
    value_amount_gross      REAL,
    currency                TEXT DEFAULT 'GBP',

    -- Contract period (from award.contractPeriod or linked contract)
    contract_start_date     TEXT,
    contract_end_date       TEXT,
    contract_max_extend     TEXT,
    date_signed             TEXT,
    contract_status         TEXT,

    -- Award criteria (JSON)
    award_criteria          TEXT,

    -- Value-quality flag. NULL = plausible. 'suspect_outlier' = value_amount_gross
    -- at or above a plausibility threshold (currently £10bn) — almost always a
    -- data error (unit confusion, framework-ceiling-as-award) and should be
    -- excluded from spend aggregations by default. See CANONICAL-LAYER-PLAYBOOK
    -- §16 for the threshold rationale.
    value_quality           TEXT,

    ingested_at             TEXT NOT NULL DEFAULT (datetime('now')),
    last_updated            TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_awards_ocid ON awards(ocid);
CREATE INDEX IF NOT EXISTS idx_awards_lot ON awards(lot_id);
CREATE INDEX IF NOT EXISTS idx_awards_end_date ON awards(contract_end_date);
CREATE INDEX IF NOT EXISTS idx_awards_status ON awards(status);
CREATE INDEX IF NOT EXISTS idx_awards_value ON awards(value_amount_gross);
CREATE INDEX IF NOT EXISTS idx_awards_value_quality ON awards(value_quality);

-- ============================================================
-- AWARD_SUPPLIERS (many-to-many: awards can have multiple suppliers)
-- ============================================================
CREATE TABLE IF NOT EXISTS award_suppliers (
    award_id    TEXT NOT NULL REFERENCES awards(id),
    supplier_id TEXT NOT NULL REFERENCES suppliers(id),
    PRIMARY KEY (award_id, supplier_id)
);

CREATE INDEX IF NOT EXISTS idx_as_supplier ON award_suppliers(supplier_id);
CREATE INDEX IF NOT EXISTS idx_as_award ON award_suppliers(award_id);

-- ============================================================
-- CPV_CODES (normalised — one row per code per notice)
-- ============================================================
CREATE TABLE IF NOT EXISTS cpv_codes (
    ocid        TEXT NOT NULL REFERENCES notices(ocid),
    code        TEXT NOT NULL,
    description TEXT,
    PRIMARY KEY (ocid, code)
);

CREATE INDEX IF NOT EXISTS idx_cpv_code ON cpv_codes(code);

-- ============================================================
-- PLANNING NOTICES (market engagement / future tenders)
-- ============================================================
CREATE TABLE IF NOT EXISTS planning_notices (
    ocid                TEXT PRIMARY KEY,
    buyer_id            TEXT REFERENCES buyers(id),
    title               TEXT,
    description         TEXT,
    engagement_deadline TEXT,
    future_notice_date  TEXT,
    estimated_value     REAL,
    notice_url          TEXT,
    notice_type         TEXT,
    published_date      TEXT,
    ingested_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_planning_buyer ON planning_notices(buyer_id);
CREATE INDEX IF NOT EXISTS idx_planning_future ON planning_notices(future_notice_date);

-- ============================================================
-- PLANNING CPV CODES
-- ============================================================
CREATE TABLE IF NOT EXISTS planning_cpv_codes (
    ocid        TEXT NOT NULL REFERENCES planning_notices(ocid),
    code        TEXT NOT NULL,
    description TEXT,
    PRIMARY KEY (ocid, code)
);

CREATE INDEX IF NOT EXISTS idx_planning_cpv_code ON planning_cpv_codes(code);

-- ============================================================
-- INGEST STATE
-- ============================================================
CREATE TABLE IF NOT EXISTS ingest_state (
    key     TEXT PRIMARY KEY,
    value   TEXT,
    updated TEXT DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO ingest_state (key, value)
VALUES ('last_cursor', '');

-- ============================================================
-- VIEWS
-- ============================================================

-- Contracts expiring in the next 365 days
CREATE VIEW IF NOT EXISTS v_expiring_contracts AS
SELECT
    a.id                            AS award_id,
    n.ocid,
    b.name                          AS buyer_name,
    b.org_type                      AS buyer_type,
    b.region_code,
    GROUP_CONCAT(DISTINCT s.name)   AS supplier_names,
    n.title,
    n.main_category,
    a.value_amount_gross,
    a.contract_start_date,
    a.contract_end_date,
    a.contract_max_extend,
    n.has_renewal,
    n.renewal_description,
    n.procurement_method,
    n.notice_url,
    CAST(julianday(a.contract_end_date) - julianday('now') AS INTEGER) AS days_to_expiry
FROM awards a
JOIN notices n ON a.ocid = n.ocid
JOIN buyers b ON n.buyer_id = b.id
LEFT JOIN award_suppliers asup ON a.id = asup.award_id
LEFT JOIN suppliers s ON asup.supplier_id = s.id
WHERE a.contract_end_date IS NOT NULL
  AND a.contract_end_date > datetime('now')
  AND a.status IN ('active', 'pending')
GROUP BY a.id
ORDER BY a.contract_end_date ASC;

-- Supplier win history (one row per supplier per award)
CREATE VIEW IF NOT EXISTS v_supplier_wins AS
SELECT
    s.id                            AS supplier_id,
    s.name                          AS supplier_name,
    s.scale,
    s.is_vcse,
    b.name                          AS buyer_name,
    b.org_type                      AS buyer_type,
    a.id                            AS award_id,
    n.title,
    n.main_category,
    a.value_amount_gross,
    a.contract_start_date,
    a.contract_end_date,
    n.procurement_method,
    n.total_bids,
    a.award_date
FROM award_suppliers asup
JOIN suppliers s ON asup.supplier_id = s.id
JOIN awards a ON asup.award_id = a.id
JOIN notices n ON a.ocid = n.ocid
JOIN buyers b ON n.buyer_id = b.id
ORDER BY a.award_date DESC;

-- Buyer procurement history
CREATE VIEW IF NOT EXISTS v_buyer_history AS
SELECT
    b.id                            AS buyer_id,
    b.name                          AS buyer_name,
    b.org_type,
    b.region_code,
    GROUP_CONCAT(DISTINCT s.name)   AS supplier_names,
    a.id                            AS award_id,
    n.title,
    n.main_category,
    a.value_amount_gross,
    n.procurement_method,
    n.total_bids,
    a.contract_start_date,
    a.contract_end_date,
    a.award_date
FROM awards a
JOIN notices n ON a.ocid = n.ocid
JOIN buyers b ON n.buyer_id = b.id
LEFT JOIN award_suppliers asup ON a.id = asup.award_id
LEFT JOIN suppliers s ON asup.supplier_id = s.id
GROUP BY a.id
ORDER BY a.award_date DESC;

-- PWIN signals: competition level per buyer + category
CREATE VIEW IF NOT EXISTS v_pwin_signals AS
SELECT
    b.name                                          AS buyer_name,
    b.org_type,
    n.main_category,
    COUNT(DISTINCT a.id)                            AS awards_count,
    AVG(n.total_bids)                               AS avg_bids_per_tender,
    AVG(a.value_amount_gross)                       AS avg_award_value,
    SUM(a.value_amount_gross)                       AS total_value,
    SUM(CASE WHEN n.procurement_method = 'direct' THEN 1 ELSE 0 END) AS direct_awards,
    SUM(CASE WHEN n.procurement_method = 'open'   THEN 1 ELSE 0 END) AS open_awards,
    SUM(CASE WHEN n.procurement_method = 'limited' THEN 1 ELSE 0 END) AS limited_awards,
    SUM(CASE WHEN n.procurement_method = 'selective' THEN 1 ELSE 0 END) AS selective_awards,
    ROUND(100.0 * SUM(CASE WHEN n.procurement_method = 'open' THEN 1 ELSE 0 END) / COUNT(DISTINCT a.id), 1) AS pct_open
FROM awards a
JOIN notices n ON a.ocid = n.ocid
JOIN buyers b ON n.buyer_id = b.id
WHERE a.status IN ('active', 'pending')
GROUP BY b.id, n.main_category
HAVING awards_count >= 1
ORDER BY awards_count DESC;

-- ============================================================
-- CANONICAL ADJUDICATOR STAGING — ADJUDICATION QUEUE
-- Authoritative definition is in emit_adjudication_queue.py.
-- Duplicated here so schema.sql initialises a fresh DB fully.
-- ============================================================
CREATE TABLE IF NOT EXISTS adjudication_queue (
    queue_id               TEXT PRIMARY KEY,
    decision_type          TEXT NOT NULL,
    left_canonical_id      TEXT NOT NULL,
    right_canonical_id     TEXT NOT NULL,
    left_name              TEXT,
    right_name             TEXT,
    left_member_count      INTEGER,
    right_member_count     INTEGER,
    left_ch_numbers        TEXT,
    right_ch_numbers       TEXT,
    left_postcodes         TEXT,
    right_postcodes        TEXT,
    left_localities        TEXT,
    right_localities       TEXT,
    left_name_variants     TEXT,
    right_name_variants    TEXT,
    left_id_kind           TEXT,
    right_id_kind          TEXT,
    structural_flag        TEXT,
    max_match_probability  REAL NOT NULL,
    supporting_pair_count  INTEGER NOT NULL,
    status                 TEXT NOT NULL DEFAULT 'pending',
    decision_json          TEXT,
    reviewed_at            TEXT,
    created_at             TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_adj_queue_status ON adjudication_queue(status);
CREATE INDEX IF NOT EXISTS idx_adj_queue_prob   ON adjudication_queue(max_match_probability DESC);

-- ============================================================
-- CANONICAL ADJUDICATOR STAGING — ESCALATIONS
-- Written by the stage_escalation MCP tool for every
-- recommendation=escalate decision. Operator resolves by
-- setting operator_outcome = human_approved | human_rejected.
-- ============================================================
CREATE TABLE IF NOT EXISTS adjudicator_escalations (
    escalation_id     TEXT PRIMARY KEY,
    decision_type     TEXT NOT NULL,
    queue_id          TEXT,
    confidence        REAL NOT NULL,
    canonical_target  TEXT,
    raw_ids           TEXT NOT NULL,
    evidence          TEXT NOT NULL,
    playbook_rule     TEXT,
    uncertainty_notes TEXT,
    operator_outcome  TEXT NOT NULL DEFAULT 'pending',
    logged_at         TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at       TEXT
);

CREATE INDEX IF NOT EXISTS idx_escalations_outcome ON adjudicator_escalations(operator_outcome);
CREATE INDEX IF NOT EXISTS idx_escalations_type    ON adjudicator_escalations(decision_type);

-- ============================================================
-- Canonical supplier wins — one row per (canonical_supplier × award).
-- Left-joins the canonical map so suppliers that have not been clustered
-- yet (or were never seen by Splink) still appear under a synthetic
-- RAW-<id> canonical_id rather than vanishing from downstream aggregations.
-- This is the primary read path for any consumer that needs supplier-level
-- rollup (queries.py supplier_profile, MCP get_supplier_profile, etc.).
CREATE VIEW IF NOT EXISTS v_canonical_supplier_wins AS
SELECT
    COALESCE(s2c.canonical_id, 'RAW-' || s.id)       AS canonical_id,
    COALESCE(cs.canonical_name, s.name)              AS canonical_name,
    cs.ch_numbers                                    AS canonical_ch_numbers,
    cs.distinct_ch_count                             AS canonical_distinct_ch_count,
    cs.member_count                                  AS canonical_member_count,
    s.id                                             AS raw_supplier_id,
    s.name                                           AS raw_supplier_name,
    s.companies_house_no                             AS raw_ch_no,
    s.scale,
    s.is_vcse,
    b.id                                             AS buyer_id,
    b.name                                           AS buyer_name,
    b.org_type                                       AS buyer_type,
    a.id                                             AS award_id,
    n.ocid,
    n.title,
    n.main_category,
    n.procurement_method,
    n.total_bids,
    a.value_amount_gross,
    a.value_quality,
    a.contract_start_date,
    a.contract_end_date,
    a.contract_max_extend,
    a.award_date,
    a.status                                         AS award_status
FROM award_suppliers asup
JOIN suppliers s            ON asup.supplier_id = s.id
LEFT JOIN supplier_to_canonical s2c ON s.id = s2c.supplier_id
LEFT JOIN canonical_suppliers cs    ON s2c.canonical_id = cs.canonical_id
JOIN awards a               ON asup.award_id = a.id
JOIN notices n              ON a.ocid = n.ocid
JOIN buyers b               ON n.buyer_id = b.id;
