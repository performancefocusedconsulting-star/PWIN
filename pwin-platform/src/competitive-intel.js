/**
 * PWIN Platform — Competitive Intelligence Module
 *
 * Read-only queries against the pwin-competitive-intel SQLite database.
 * Built on the UK Find a Tender Service OCDS data.
 * Uses Node.js built-in node:sqlite (Node 22+).
 */

import { DatabaseSync } from 'node:sqlite';
import { join } from 'node:path';
import { existsSync, readFileSync, writeFileSync, statSync } from 'node:fs';

// Database path — sibling product folder
const DB_PATH = join(import.meta.dirname, '..', '..', 'pwin-competitive-intel', 'db', 'bid_intel.db');
const CPV_P95_CACHE = join(import.meta.dirname, '..', '..', 'pwin-competitive-intel', 'db', '_cpv_p95_cache.json');

function getDb() {
  if (!existsSync(DB_PATH)) return null;
  return new DatabaseSync(DB_PATH, { readOnly: true });
}

// ── Summary ──────────────────────────────────────────────────────────────

function dbSummary() {
  const db = getDb();
  if (!db) return { error: 'Database not found. Run pwin-competitive-intel/agent/ingest.py first.' };
  try {
    const tables = ['buyers', 'suppliers', 'notices', 'lots', 'awards', 'award_suppliers', 'cpv_codes', 'planning_notices'];
    const counts = {};
    for (const t of tables) {
      counts[t] = db.prepare(`SELECT COUNT(*) as cnt FROM ${t}`).get().cnt;
    }
    const cursor = db.prepare("SELECT value FROM ingest_state WHERE key='last_cursor'").get();
    const val = db.prepare("SELECT SUM(value_amount_gross) as total, AVG(value_amount_gross) as avg, MAX(value_amount_gross) as max FROM awards WHERE value_amount_gross IS NOT NULL").get();
    return {
      tables: counts,
      lastCursor: cursor?.value || null,
      totalValue: val.total,
      avgValue: val.avg,
      maxValue: val.max,
    };
  } finally {
    db.close();
  }
}

// ── Buyer Profile ────────────────────────────────────────────────────────

function buyerProfile(nameQuery, limit = 20) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const resolved = _resolveBuyerCanonical(db, nameQuery);

    if (!resolved) {
      return { buyers: [], message: `No buyers matching '${nameQuery}'` };
    }

    if (resolved.ambiguous) {
      return {
        buyers: [],
        ambiguous: true,
        candidates: resolved.candidates,
        message: `Multiple canonical matches for '${nameQuery}' — please be more specific`,
      };
    }

    if (resolved.fragmented) {
      // No canonical match — fall back to raw rows the resolver already pulled.
      // Surface the gap so coverage problems are visible.
      console.warn(`[buyerProfile] No canonical match for '${nameQuery}' — falling back to raw LIKE (fragmented)`);
      return _buildRawProfile(db, resolved.rawBuyerIds, limit);
    }

    // Resolved cleanly — return one consolidated profile aggregated across all
    // raw buyer rows that map to this canonical entity. Use buyers.canonical_id
    // as the source of truth (catches rows matched via normalised/prefix rules
    // in addition to exact-alias rows).
    const memberIds = db.prepare(
      'SELECT id, name, org_type, region_code FROM buyers WHERE canonical_id = ?'
    ).all(resolved.canonicalId);

    if (!memberIds.length) {
      // Canonical exists but no raw rows back-ref it. Use whatever the
      // resolver's alias-join produced as a last resort.
      if (!resolved.rawBuyerIds.length) {
        return { buyers: [], message: `Canonical buyer '${resolved.canonicalName}' has no raw rows in the database` };
      }
      return _buildConsolidatedProfile(db, resolved, resolved.rawBuyerIds, [], limit);
    }

    const ids = memberIds.map(m => m.id);
    return _buildConsolidatedProfile(db, resolved, ids, memberIds, limit);
  } finally {
    db.close();
  }
}

function _placeholders(n) {
  return new Array(n).fill('?').join(',');
}

function _buildConsolidatedProfile(db, resolved, ids, memberRows, limit) {
  const ph = _placeholders(ids.length);

  const stats = db.prepare(`
    SELECT
      COUNT(DISTINCT a.id) AS total_awards,
      COUNT(DISTINCT n.ocid) AS total_notices,
      SUM(a.value_amount_gross) AS total_spend,
      AVG(a.value_amount_gross) AS avg_value,
      MAX(a.value_amount_gross) AS max_value,
      AVG(n.total_bids) AS avg_bids
    FROM awards a
    JOIN notices n ON a.ocid = n.ocid
    WHERE n.buyer_id IN (${ph}) AND a.status IN ('active', 'pending')
  `).get(...ids);

  const methods = db.prepare(`
    SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
    FROM awards a JOIN notices n ON a.ocid = n.ocid
    WHERE n.buyer_id IN (${ph}) AND a.status IN ('active', 'pending')
    GROUP BY n.procurement_method ORDER BY cnt DESC
  `).all(...ids);

  const topSuppliers = db.prepare(`
    SELECT canonical_name AS name,
           COUNT(DISTINCT award_id) AS wins,
           SUM(value_amount_gross)  AS total_value
    FROM v_canonical_supplier_wins
    WHERE buyer_id IN (${ph}) AND value_quality IS NULL
    GROUP BY canonical_id
    ORDER BY wins DESC, total_value DESC LIMIT 15
  `).all(...ids);

  const recentAwards = db.prepare(`
    SELECT n.title, a.value_amount_gross, n.procurement_method,
           GROUP_CONCAT(DISTINCT s.name) AS suppliers,
           a.contract_end_date, a.award_date
    FROM awards a
    JOIN notices n ON a.ocid = n.ocid
    LEFT JOIN award_suppliers asup ON a.id = asup.award_id
    LEFT JOIN suppliers s ON asup.supplier_id = s.id
    WHERE n.buyer_id IN (${ph}) AND a.status IN ('active', 'pending')
    GROUP BY a.id
    ORDER BY a.award_date DESC NULLS LAST LIMIT ?
  `).all(...ids, limit);

  const memberNames = memberRows.map(m => m.name).filter(Boolean);

  const spendSignal = _buildSpendSignal(db, resolved.canonicalId);

  return {
    buyers: [{
      id: resolved.canonicalId,
      name: resolved.canonicalName,
      org_type: resolved.canonicalType,
      region_code: null,
      canonical: {
        canonicalId: resolved.canonicalId,
        canonicalName: resolved.canonicalName,
        canonicalType: resolved.canonicalType,
        memberCount: ids.length,
        memberNames: memberNames.slice(0, 25),
      },
      stats: {
        totalAwards: stats.total_awards,
        totalNotices: stats.total_notices,
        totalSpend: stats.total_spend,
        avgValue: stats.avg_value,
        maxValue: stats.max_value,
        avgBidsPerTender: stats.avg_bids,
      },
      procurementMethods: methods.map(m => ({ method: m.procurement_method, count: m.cnt })),
      topSuppliers: topSuppliers.map(s => ({ name: s.name, wins: s.wins, totalValue: s.total_value })),
      recentAwards: recentAwards.map(r => ({
        title: r.title,
        value: r.value_amount_gross,
        method: r.procurement_method,
        suppliers: r.suppliers,
        contractEndDate: r.contract_end_date,
        awardDate: r.award_date,
      })),
      spendSignal,
    }],
  };
}

function _buildSpendSignal(db, canonicalId) {
  try {
    const tables = db.prepare(
      "SELECT name FROM sqlite_master WHERE type='table' AND name='spend_transactions'"
    ).get();
    if (!tables) return null;

    const summary = db.prepare(`
      SELECT
        COUNT(*) AS row_count,
        SUM(amount) AS total_amount,
        MIN(payment_date) AS earliest,
        MAX(payment_date) AS latest,
        COUNT(DISTINCT raw_entity) AS entity_variants
      FROM spend_transactions
      WHERE canonical_sub_org_id = ?
    `).get(canonicalId);

    if (!summary || !summary.row_count) return null;

    const topSuppliers = db.prepare(`
      SELECT raw_supplier_name, canonical_supplier_id,
             COUNT(*) AS transactions, SUM(amount) AS total
      FROM spend_transactions
      WHERE canonical_sub_org_id = ?
      GROUP BY COALESCE(canonical_supplier_id, raw_supplier_name)
      ORDER BY total DESC LIMIT 10
    `).all(canonicalId);

    return {
      rowCount: summary.row_count,
      totalAmount: summary.total_amount,
      dateRange: { from: summary.earliest, to: summary.latest },
      entityVariants: summary.entity_variants,
      topSuppliers: topSuppliers.map(s => ({
        name: s.raw_supplier_name,
        canonicalId: s.canonical_supplier_id,
        transactions: s.transactions,
        total: s.total,
      })),
    };
  } catch (err) {
    return null;
  }
}

function _buildRawProfile(db, rawBuyerIds, limit) {
  if (!rawBuyerIds || !rawBuyerIds.length) {
    return { buyers: [], message: 'No matching raw buyers' };
  }
  const ids = rawBuyerIds.slice(0, 10);
  const buyers = db.prepare(
    `SELECT id, name, org_type, region_code FROM buyers WHERE id IN (${_placeholders(ids.length)}) ORDER BY name`
  ).all(...ids);

  return {
    buyers: buyers.map(buyer => {
      const stats = db.prepare(`
        SELECT
          COUNT(DISTINCT a.id) AS total_awards,
          COUNT(DISTINCT n.ocid) AS total_notices,
          SUM(a.value_amount_gross) AS total_spend,
          AVG(a.value_amount_gross) AS avg_value,
          MAX(a.value_amount_gross) AS max_value,
          AVG(n.total_bids) AS avg_bids
        FROM awards a
        JOIN notices n ON a.ocid = n.ocid
        WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
      `).get(buyer.id);

      const methods = db.prepare(`
        SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
        FROM awards a JOIN notices n ON a.ocid = n.ocid
        WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
        GROUP BY n.procurement_method ORDER BY cnt DESC
      `).all(buyer.id);

      const topSuppliers = db.prepare(`
        SELECT canonical_name AS name,
               COUNT(DISTINCT award_id) AS wins,
               SUM(value_amount_gross)  AS total_value
        FROM v_canonical_supplier_wins
        WHERE buyer_id = ? AND value_quality IS NULL
        GROUP BY canonical_id
        ORDER BY wins DESC, total_value DESC LIMIT 15
      `).all(buyer.id);

      const recentAwards = db.prepare(`
        SELECT n.title, a.value_amount_gross, n.procurement_method,
               GROUP_CONCAT(DISTINCT s.name) AS suppliers,
               a.contract_end_date, a.award_date
        FROM awards a
        JOIN notices n ON a.ocid = n.ocid
        LEFT JOIN award_suppliers asup ON a.id = asup.award_id
        LEFT JOIN suppliers s ON asup.supplier_id = s.id
        WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
        GROUP BY a.id
        ORDER BY a.award_date DESC NULLS LAST LIMIT ?
      `).all(buyer.id, limit);

      return {
        ...buyer,
        canonical: null,
        stats: {
          totalAwards: stats.total_awards,
          totalNotices: stats.total_notices,
          totalSpend: stats.total_spend,
          avgValue: stats.avg_value,
          maxValue: stats.max_value,
          avgBidsPerTender: stats.avg_bids,
        },
        procurementMethods: methods.map(m => ({ method: m.procurement_method, count: m.cnt })),
        topSuppliers: topSuppliers.map(s => ({ name: s.name, wins: s.wins, totalValue: s.total_value })),
        recentAwards: recentAwards.map(r => ({
          title: r.title,
          value: r.value_amount_gross,
          method: r.procurement_method,
          suppliers: r.suppliers,
          contractEndDate: r.contract_end_date,
          awardDate: r.award_date,
        })),
      };
    }),
    fragmented: true,
    message: 'Buyer name did not resolve to canonical — results are raw rows only',
  };
}

// ── Supplier Profile ─────────────────────────────────────────────────────

function supplierProfile(nameQuery, limit = 20) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    // Search canonical entities by canonical_name OR any raw member name.
    // Returns one row per canonical supplier — all raw variants rolled up.
    const canonicals = db.prepare(`
      SELECT DISTINCT canonical_id, canonical_name, canonical_ch_numbers,
                      canonical_distinct_ch_count, canonical_member_count
      FROM v_canonical_supplier_wins
      WHERE LOWER(canonical_name) LIKE LOWER(?)
         OR LOWER(raw_supplier_name) LIKE LOWER(?)
      ORDER BY canonical_member_count DESC NULLS LAST, canonical_name
      LIMIT 10
    `).all(`%${nameQuery}%`, `%${nameQuery}%`);

    if (!canonicals.length) return { suppliers: [], message: `No suppliers matching '${nameQuery}'` };

    return {
      suppliers: canonicals.map(sup => {
        const stats = db.prepare(`
          SELECT
            COUNT(DISTINCT award_id)     AS total_wins,
            SUM(value_amount_gross)      AS total_value,
            AVG(value_amount_gross)      AS avg_value,
            MAX(value_amount_gross)      AS max_value,
            MIN(award_date)              AS first_win,
            MAX(award_date)              AS last_win
          FROM v_canonical_supplier_wins
          WHERE canonical_id = ? AND value_quality IS NULL
        `).get(sup.canonical_id);

        const buyerRelationships = db.prepare(`
          SELECT buyer_name AS name, COUNT(DISTINCT award_id) AS awards,
                 SUM(value_amount_gross) AS total_value,
                 MAX(contract_end_date)  AS latest_expiry
          FROM v_canonical_supplier_wins
          WHERE canonical_id = ? AND value_quality IS NULL
          GROUP BY buyer_id
          ORDER BY awards DESC LIMIT 15
        `).all(sup.canonical_id);

        // GROUP BY award_id collapses the N-rows-per-award that result
        // when a canonical rolls up multiple raw suppliers on one award.
        const activeContracts = db.prepare(`
          SELECT title, buyer_name AS buyer, value_amount_gross,
                 contract_end_date, contract_max_extend
          FROM v_canonical_supplier_wins
          WHERE canonical_id = ?
            AND contract_end_date > datetime('now')
          GROUP BY award_id
          ORDER BY contract_end_date ASC LIMIT 20
        `).all(sup.canonical_id);

        return {
          canonicalId: sup.canonical_id,
          name: sup.canonical_name,
          chNumbers: sup.canonical_ch_numbers,
          distinctChCount: sup.canonical_distinct_ch_count,
          memberCount: sup.canonical_member_count,
          stats: {
            totalWins: stats.total_wins,
            totalValue: stats.total_value,
            avgValue: stats.avg_value,
            maxValue: stats.max_value,
            firstWin: stats.first_win,
            lastWin: stats.last_win,
          },
          buyerRelationships: buyerRelationships.map(r => ({
            buyer: r.name,
            awards: r.awards,
            totalValue: r.total_value,
            latestExpiry: r.latest_expiry,
          })),
          activeContracts: activeContracts.map(c => ({
            title: c.title,
            buyer: c.buyer,
            value: c.value_amount_gross,
            expires: c.contract_end_date,
            maxExtend: c.contract_max_extend,
          })),
        };
      }),
    };
  } finally {
    db.close();
  }
}

// ── Expiring Contracts ───────────────────────────────────────────────────

function expiringContracts({ days = 365, minValue = null, buyer = null, category = null } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    let sql = "SELECT * FROM v_expiring_contracts WHERE days_to_expiry <= ?";
    const params = [days];

    if (minValue) { sql += " AND value_amount_gross >= ?"; params.push(minValue); }
    if (buyer) { sql += " AND LOWER(buyer_name) LIKE LOWER(?)"; params.push(`%${buyer}%`); }
    if (category) { sql += " AND LOWER(main_category) LIKE LOWER(?)"; params.push(`%${category}%`); }
    sql += " ORDER BY days_to_expiry ASC LIMIT 100";

    const rows = db.prepare(sql).all(...params);
    return {
      count: rows.length,
      filters: { days, minValue, buyer, category },
      contracts: rows.map(r => ({
        awardId: r.award_id,
        buyer: r.buyer_name,
        buyerType: r.buyer_type,
        suppliers: r.supplier_names,
        title: r.title,
        category: r.main_category,
        value: r.value_amount_gross,
        contractEndDate: r.contract_end_date,
        maxExtend: r.contract_max_extend,
        daysToExpiry: r.days_to_expiry,
        method: r.procurement_method,
        hasRenewal: !!r.has_renewal,
      })),
    };
  } finally {
    db.close();
  }
}

// ── Forward Pipeline ─────────────────────────────────────────────────────

function forwardPipeline({ buyer = null } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    let sql = `
      SELECT p.*, b.name AS buyer_name, b.org_type
      FROM planning_notices p
      JOIN buyers b ON p.buyer_id = b.id
      WHERE 1=1
    `;
    const params = [];
    if (buyer) { sql += " AND LOWER(b.name) LIKE LOWER(?)"; params.push(`%${buyer}%`); }
    sql += ` ORDER BY CASE WHEN p.future_notice_date IS NOT NULL
             THEN p.future_notice_date ELSE p.engagement_deadline END ASC LIMIT 100`;

    const rows = db.prepare(sql).all(...params);
    return {
      count: rows.length,
      notices: rows.map(r => ({
        ocid: r.ocid,
        buyer: r.buyer_name,
        buyerType: r.org_type,
        title: r.title,
        description: r.description,
        estimatedValue: r.estimated_value,
        engagementDeadline: r.engagement_deadline,
        futureNoticeDate: r.future_notice_date,
        noticeUrl: r.notice_url,
      })),
    };
  } finally {
    db.close();
  }
}

// ── PWIN Signals ─────────────────────────────────────────────────────────

function pwinSignals({ buyer = null, category = null } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    let sql = "SELECT * FROM v_pwin_signals WHERE 1=1";
    const params = [];
    if (buyer) { sql += " AND LOWER(buyer_name) LIKE LOWER(?)"; params.push(`%${buyer}%`); }
    if (category) { sql += " AND LOWER(main_category) LIKE LOWER(?)"; params.push(`%${category}%`); }
    sql += " LIMIT 50";

    const rows = db.prepare(sql).all(...params);
    return {
      count: rows.length,
      signals: rows.map(r => ({
        buyer: r.buyer_name,
        buyerType: r.org_type,
        category: r.main_category,
        awardsCount: r.awards_count,
        avgBidsPerTender: r.avg_bids_per_tender,
        avgAwardValue: r.avg_award_value,
        totalValue: r.total_value,
        openAwards: r.open_awards,
        limitedAwards: r.limited_awards,
        directAwards: r.direct_awards,
        selectiveAwards: r.selective_awards,
        pctOpen: r.pct_open,
      })),
    };
  } finally {
    db.close();
  }
}

// ── CPV Search ───────────────────────────────────────────────────────────

function cpvSearch(codePrefix) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const rows = db.prepare(`
      SELECT c.code, c.description, n.title, b.name AS buyer,
             n.procurement_method, n.tender_status,
             (SELECT SUM(a.value_amount_gross) FROM awards a WHERE a.ocid = n.ocid) AS total_value
      FROM cpv_codes c
      JOIN notices n ON c.ocid = n.ocid
      JOIN buyers b ON n.buyer_id = b.id
      WHERE c.code LIKE ?
      ORDER BY n.published_date DESC LIMIT 50
    `).all(`${codePrefix}%`);

    return {
      count: rows.length,
      codePrefix,
      notices: rows.map(r => ({
        cpvCode: r.code,
        cpvDescription: r.description,
        title: r.title,
        buyer: r.buyer,
        method: r.procurement_method,
        status: r.tender_status,
        totalValue: r.total_value,
      })),
    };
  } finally {
    db.close();
  }
}

// ── Sector Profile ───────────────────────────────────────────────────────

// Maps sector names to buyer org_type values in the DB.
// Falls back to LIKE search on buyer name if no org_type match.
const SECTOR_ORG_TYPES = {
  'local government': ['local_authority'],
  'local authority': ['local_authority'],
  'health': ['nhs_trust', 'nhs_icb'],
  'nhs': ['nhs_trust', 'nhs_icb'],
  'central government': ['department', 'agency', 'ndpb'],
  'government': ['department', 'agency', 'ndpb'],
  'defence': ['mod'],
  'defense': ['mod'],
};

function sectorProfile(sectorName, limit = 15) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };

  try {
    const key = Object.keys(SECTOR_ORG_TYPES).find(k =>
      sectorName.toLowerCase().includes(k) || k.includes(sectorName.toLowerCase())
    );

    let buyerWhere, buyerParams;
    if (key) {
      const types = SECTOR_ORG_TYPES[key];
      const placeholders = types.map(() => '?').join(', ');
      buyerWhere = `b.org_type IN (${placeholders})`;
      buyerParams = types;
    } else {
      buyerWhere = 'LOWER(b.name) LIKE ?';
      buyerParams = [`%${sectorName.toLowerCase()}%`];
    }

    const summary = db.prepare(`
      SELECT COUNT(DISTINCT b.id) AS buyer_count,
             COUNT(DISTINCT a.id) AS award_count,
             SUM(a.value_amount_gross) AS total_spend,
             AVG(a.value_amount_gross) AS avg_award_value,
             AVG(n.total_bids) AS avg_bids_per_tender
      FROM buyers b
      JOIN notices n ON n.buyer_id = b.id
      JOIN awards a ON a.ocid = n.ocid
      WHERE ${buyerWhere} AND a.status IN ('active', 'pending')
    `).get(...buyerParams);

    const topBuyers = db.prepare(`
      SELECT b.name, b.org_type,
             COUNT(DISTINCT a.id) AS award_count,
             SUM(a.value_amount_gross) AS total_spend,
             AVG(a.value_amount_gross) AS avg_value
      FROM buyers b
      JOIN notices n ON n.buyer_id = b.id
      JOIN awards a ON a.ocid = n.ocid
      WHERE ${buyerWhere} AND a.status IN ('active', 'pending')
      GROUP BY b.id ORDER BY total_spend DESC NULLS LAST LIMIT ?
    `).all(...buyerParams, limit);

    const topSuppliers = db.prepare(`
      SELECT v.canonical_name AS name,
             COUNT(DISTINCT v.award_id) AS wins,
             SUM(v.value_amount_gross) AS total_value
      FROM v_canonical_supplier_wins v
      JOIN buyers b ON v.buyer_id = b.id
      WHERE ${buyerWhere} AND v.value_quality IS NULL
      GROUP BY v.canonical_id
      ORDER BY wins DESC, total_value DESC LIMIT ?
    `).all(...buyerParams, limit);

    const methods = db.prepare(`
      SELECT n.procurement_method,
             COUNT(DISTINCT a.id) AS cnt,
             SUM(a.value_amount_gross) AS total_value
      FROM awards a
      JOIN notices n ON a.ocid = n.ocid
      JOIN buyers b ON n.buyer_id = b.id
      WHERE ${buyerWhere} AND a.status IN ('active', 'pending')
      GROUP BY n.procurement_method ORDER BY cnt DESC
    `).all(...buyerParams);

    const pipeline = db.prepare(`
      SELECT p.title, b.name AS buyer, b.org_type,
             p.estimated_value, p.future_notice_date, p.engagement_deadline
      FROM planning_notices p
      JOIN buyers b ON p.buyer_id = b.id
      WHERE ${buyerWhere}
      ORDER BY p.future_notice_date ASC NULLS LAST LIMIT 20
    `).all(...buyerParams);

    return {
      sector: sectorName,
      summary: {
        buyerCount: summary.buyer_count,
        awardCount: summary.award_count,
        totalSpend: summary.total_spend,
        avgAwardValue: summary.avg_award_value,
        avgBidsPerTender: summary.avg_bids_per_tender,
      },
      topBuyers: topBuyers.map(b => ({
        name: b.name, orgType: b.org_type,
        awards: b.award_count, totalSpend: b.total_spend, avgValue: b.avg_value,
      })),
      topSuppliers: topSuppliers.map(s => ({
        name: s.name, wins: s.wins, totalValue: s.total_value,
      })),
      procurementMethods: methods.map(m => ({
        method: m.procurement_method, count: m.cnt, totalValue: m.total_value,
      })),
      forwardPipeline: pipeline.map(p => ({
        title: p.title, buyer: p.buyer, buyerType: p.org_type,
        estimatedValue: p.estimated_value,
        futureNoticeDate: p.future_notice_date,
        engagementDeadline: p.engagement_deadline,
      })),
    };
  } finally {
    db.close();
  }
}

// ── Daily pipeline scan support ──────────────────────────────────────────
// Returns notices + planning notices published in the last N hours, with
// the buyer joined in. Used by the daily-pipeline-scan skill (Agent 2)
// to triage new procurement activity. Results are intentionally rich so
// the LLM can score on value/scope/buyer without further DB lookups.

function pipelineRecentNotices({
  hoursLookback = 24,
  valueFloor = 1_000_000,     // include notices >= this OR with NULL value
  rowLimit = 150,             // hard cap per table to keep prompt tractable
  descTruncateChars = 2000,   // long descriptions cost tokens; keep enough for triage
} = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const cutoff = `datetime('now', '-${Math.max(1, parseInt(hoursLookback))} hours')`;
    const floor = Number(valueFloor) || 0;
    const limit = Math.max(1, parseInt(rowLimit));

    const noticesSql = `
      SELECT n.ocid, n.buyer_id, n.title, n.description, n.value_amount,
             n.value_amount_gross, n.currency, n.notice_type, n.latest_tag,
             n.published_date, n.tender_end_date, n.notice_url,
             n.is_framework, n.framework_type, n.suitable_for_sme,
             n.main_category, n.cpv_category, n.procurement_method,
             n.procurement_method_detail, n.tender_status,
             n.data_source,
             b.name AS buyer_name, b.org_type AS buyer_org_type,
             b.region_code AS buyer_region
      FROM notices n
      LEFT JOIN buyers b ON n.buyer_id = b.id
      WHERE n.published_date >= ${cutoff}
        AND (
          n.value_amount IS NULL
          OR n.value_amount >= ?
          OR n.value_amount_gross >= ?
        )
      ORDER BY COALESCE(n.value_amount, n.value_amount_gross, 0) DESC,
               n.published_date DESC
      LIMIT ?
    `;
    const truncate = s => (s && s.length > descTruncateChars
      ? s.slice(0, descTruncateChars) + ` … [truncated, ${s.length - descTruncateChars} more chars]`
      : s);
    const notices = db.prepare(noticesSql).all(floor, floor, limit).map(r => ({
      ocid: r.ocid,
      buyerId: r.buyer_id,
      buyerName: r.buyer_name,
      buyerOrgType: r.buyer_org_type,
      buyerRegion: r.buyer_region,
      title: r.title,
      description: truncate(r.description),
      value: r.value_amount,
      valueGross: r.value_amount_gross,
      currency: r.currency,
      noticeType: r.notice_type,
      latestTag: r.latest_tag,
      publishedDate: r.published_date,
      tenderEndDate: r.tender_end_date,
      noticeUrl: r.notice_url,
      isFramework: !!r.is_framework,
      frameworkType: r.framework_type,
      suitableForSme: !!r.suitable_for_sme,
      mainCategory: r.main_category,
      cpvCategory: r.cpv_category,
      procurementMethod: r.procurement_method,
      procurementMethodDetail: r.procurement_method_detail,
      tenderStatus: r.tender_status,
      dataSource: r.data_source,
    }));

    const planningSql = `
      SELECT p.ocid, p.buyer_id, p.title, p.description, p.estimated_value,
             p.engagement_deadline, p.future_notice_date, p.notice_url,
             p.notice_type, p.published_date,
             b.name AS buyer_name, b.org_type AS buyer_org_type,
             b.region_code AS buyer_region
      FROM planning_notices p
      LEFT JOIN buyers b ON p.buyer_id = b.id
      WHERE p.published_date >= ${cutoff}
        AND (p.estimated_value IS NULL OR p.estimated_value >= ?)
      ORDER BY COALESCE(p.estimated_value, 0) DESC, p.published_date DESC
      LIMIT ?
    `;
    const planningNotices = db.prepare(planningSql).all(floor, limit).map(r => ({
      ocid: r.ocid,
      buyerId: r.buyer_id,
      buyerName: r.buyer_name,
      buyerOrgType: r.buyer_org_type,
      buyerRegion: r.buyer_region,
      title: r.title,
      description: truncate(r.description),
      estimatedValue: r.estimated_value,
      engagementDeadline: r.engagement_deadline,
      futureNoticeDate: r.future_notice_date,
      noticeUrl: r.notice_url,
      noticeType: r.notice_type,
      publishedDate: r.published_date,
    }));

    return {
      hoursLookback: parseInt(hoursLookback),
      cutoff: db.prepare(`SELECT ${cutoff} AS c`).get().c,
      noticeCount: notices.length,
      planningCount: planningNotices.length,
      notices,
      planningNotices,
    };
  } finally {
    db.close();
  }
}

// Recent awards for a set of buyers — used as the competitive-field
// reference block when the daily-pipeline-scan skill triages a batch.
// Default: last 730 days, value floor £1m, max 200 rows total.
function pipelineRecentAwardsForBuyers({
  buyerIds = [],
  daysLookback = 730,
  valueFloor = 1_000_000,
  rowLimit = 200,
} = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  if (!Array.isArray(buyerIds) || buyerIds.length === 0) {
    db.close();
    return { count: 0, awards: [], note: 'No buyer IDs supplied' };
  }
  try {
    const placeholders = buyerIds.map(() => '?').join(',');
    const sql = `
      SELECT a.id AS award_id, a.ocid, a.title AS award_title, a.value_amount,
             a.value_amount_gross, a.award_date, a.contract_start_date,
             a.contract_end_date,
             n.procurement_method,
             n.title AS notice_title, n.main_category, n.cpv_category,
             b.id AS buyer_id, b.name AS buyer_name,
             (SELECT GROUP_CONCAT(s.name, ' | ')
                FROM award_suppliers asup
                JOIN suppliers s ON asup.supplier_id = s.id
                WHERE asup.award_id = a.id) AS suppliers
      FROM awards a
      JOIN notices n ON a.ocid = n.ocid
      JOIN buyers b ON n.buyer_id = b.id
      WHERE n.buyer_id IN (${placeholders})
        AND a.award_date >= date('now', '-${parseInt(daysLookback)} days')
        AND COALESCE(a.value_amount, a.value_amount_gross, 0) >= ?
      ORDER BY a.award_date DESC, COALESCE(a.value_amount, a.value_amount_gross, 0) DESC
      LIMIT ?
    `;
    const params = [...buyerIds, valueFloor, rowLimit];
    const rows = db.prepare(sql).all(...params).map(r => ({
      awardId: r.award_id,
      ocid: r.ocid,
      buyerId: r.buyer_id,
      buyerName: r.buyer_name,
      noticeTitle: r.notice_title,
      awardTitle: r.award_title,
      mainCategory: r.main_category,
      cpvCategory: r.cpv_category,
      value: r.value_amount,
      valueGross: r.value_amount_gross,
      awardDate: r.award_date,
      contractStart: r.contract_start_date,
      contractEnd: r.contract_end_date,
      procurementMethod: r.procurement_method,
      suppliers: r.suppliers ? r.suppliers.split(' | ').map(s => s.trim()).filter(Boolean) : [],
    }));
    return {
      buyerIdCount: buyerIds.length,
      daysLookback: parseInt(daysLookback),
      valueFloor,
      count: rows.length,
      awards: rows,
    };
  } finally {
    db.close();
  }
}

// ── Buyer Behaviour Analytics (v1) ───────────────────────────────────────
// JSON-returning equivalent of the CLI in pwin-competitive-intel/queries/
// queries.py:buyer_behaviour. Powers the empirical Probability of Going
// Out (PGO) figure for Win Strategy, Verdict, and the future paid Qualify
// tier.
//
// Caveats baked in (same as the CLI version):
//   - Contracts Finder rows have no cancellation marker → cancellation
//     analysis is FTS-only, with the FTS share disclosed.
//   - Procurement-method fields are essentially FTS-only.
//   - Amendment behaviour deferred to Phase 2 (data not in current schema).
//   - Distress flag fires on ch_status='dissolved' only.
//   - Peer-buyer comparison uses canonical_buyers.type only.

const CPV_DIVISION_LABELS = {
  '03': 'Agriculture / forestry',  '09': 'Petroleum / fuels',
  '14': 'Mining / minerals',       '15': 'Food / beverages',
  '16': 'Agricultural machinery',  '18': 'Clothing / footwear',
  '19': 'Leather / textiles',      '22': 'Printed matter',
  '24': 'Chemicals',               '30': 'Office / IT equipment',
  '31': 'Electrical / electronic', '32': 'Radio / TV / comms equipment',
  '33': 'Medical / pharma equipment','34': 'Transport equipment',
  '35': 'Security / defence equipment','37': 'Sports / musical / arts goods',
  '38': 'Laboratory / measuring',  '39': 'Furniture',
  '41': 'Water utility',           '42': 'Industrial machinery',
  '43': 'Mining / quarrying machinery','44': 'Construction materials',
  '45': 'Construction works',      '48': 'Software packages',
  '50': 'Repair / maintenance',    '51': 'Installation services',
  '55': 'Hotel / catering',        '60': 'Transport services',
  '63': 'Supporting transport / travel','64': 'Postal / telecoms services',
  '65': 'Public utilities',        '66': 'Financial / insurance services',
  '70': 'Real estate services',    '71': 'Architectural / engineering',
  '72': 'IT services',             '73': 'Research / development',
  '75': 'Public administration',   '76': 'Oil / gas services',
  '77': 'Agricultural services',   '79': 'Business / consultancy services',
  '80': 'Education / training',    '85': 'Health / social care',
  '90': 'Sewage / waste / cleaning','92': 'Recreational / cultural / sport',
  '98': 'Other community / social services',
};

function _cpvDivisionLabel(div) {
  if (!div) return 'Uncategorised';
  return CPV_DIVISION_LABELS[div] || `CPV ${div}`;
}

function _safePct(num, denom, places = 1) {
  if (!denom) return null;
  return Number(((num * 100.0) / denom).toFixed(places));
}

function _resolveBuyerCanonical(db, nameQuery) {
  const q = (nameQuery || '').trim();
  const qLow = q.toLowerCase();
  let canonicalId = null;

  // Path 1 — exact alias
  let row = db.prepare(
    'SELECT canonical_id FROM canonical_buyer_aliases WHERE alias_lower = ?'
  ).get(qLow);
  if (row) canonicalId = row.canonical_id;

  // Path 2 — abbreviation
  if (!canonicalId) {
    row = db.prepare(
      'SELECT canonical_id FROM canonical_buyers ' +
      'WHERE LOWER(abbreviation) = ? LIMIT 1'
    ).get(qLow);
    if (row) canonicalId = row.canonical_id;
  }

  // Path 3 — canonical name LIKE (only resolve if exactly one match)
  if (!canonicalId) {
    const rows = db.prepare(
      'SELECT canonical_id, canonical_name FROM canonical_buyers ' +
      'WHERE LOWER(canonical_name) LIKE ? ' +
      'ORDER BY LENGTH(canonical_name) ASC LIMIT 5'
    ).all(`%${qLow}%`);
    if (rows.length === 1) canonicalId = rows[0].canonical_id;
    else if (rows.length > 1) {
      return {
        ambiguous: true,
        candidates: rows.map(r => r.canonical_name),
      };
    }
  }

  if (canonicalId) {
    const canon = db.prepare(
      'SELECT canonical_id, canonical_name, type FROM canonical_buyers WHERE canonical_id = ?'
    ).get(canonicalId);
    const ids = db.prepare(`
      SELECT DISTINCT id FROM buyers WHERE canonical_id = ?
    `).all(canonicalId).map(r => r.id);
    return {
      canonicalId: canon.canonical_id,
      canonicalName: canon.canonical_name,
      canonicalType: canon.type,
      rawBuyerIds: ids,
      fragmented: false,
    };
  }

  // Path 4 — fragmented fallback
  const rawRows = db.prepare(
    'SELECT id, name FROM buyers WHERE LOWER(name) LIKE ? ORDER BY name LIMIT 200'
  ).all(`%${qLow}%`);
  if (!rawRows.length) return null;
  return {
    canonicalId: null,
    canonicalName: q,
    canonicalType: null,
    rawBuyerIds: rawRows.map(r => r.id),
    fragmented: true,
  };
}

function _stageBuyerIdTempTable(db, ids) {
  db.exec('DROP TABLE IF EXISTS _bb_ids');
  db.exec('CREATE TEMP TABLE _bb_ids (id TEXT PRIMARY KEY)');
  const ins = db.prepare('INSERT OR IGNORE INTO _bb_ids (id) VALUES (?)');
  for (const id of ids) ins.run(id);
}

function _loadCpvP95Cache() {
  // The Python CLI populates this cache; we read it if it's <24h old.
  // Falls back to an empty object (consumers use 'overall' default).
  try {
    if (!existsSync(CPV_P95_CACHE)) return null;
    const ageMs = Date.now() - statSync(CPV_P95_CACHE).mtimeMs;
    if (ageMs > 24 * 3600 * 1000) return null;
    return JSON.parse(readFileSync(CPV_P95_CACHE, 'utf-8'));
  } catch {
    return null;
  }
}

function _computeCpvP95(db, minSample = 50) {
  const cached = _loadCpvP95Cache();
  if (cached) return cached;

  const rows = db.prepare(`
    WITH first_award AS (
      SELECT n.ocid, n.published_date,
             MIN(COALESCE(a.award_date, a.date_signed,
                          a.contract_start_date)) AS first_aw
      FROM notices n JOIN awards a ON a.ocid = n.ocid
      WHERE a.status IN ('active','pending') AND n.published_date IS NOT NULL
      GROUP BY n.ocid
    )
    SELECT SUBSTR(c.code, 1, 2)  AS div,
           CAST(julianday(fa.first_aw) - julianday(fa.published_date) AS INTEGER) AS days
    FROM first_award fa
    JOIN cpv_codes c ON c.ocid = fa.ocid
    WHERE fa.first_aw IS NOT NULL AND fa.first_aw > fa.published_date
  `).all();

  const buckets = {};
  const overall = [];
  for (const r of rows) {
    if (r.days == null || r.days < 0 || r.days > 2000) continue;
    (buckets[r.div] ||= []).push(r.days);
    overall.push(r.days);
  }
  const p95 = vals => {
    if (!vals.length) return null;
    const s = [...vals].sort((a, b) => a - b);
    return s[Math.floor(0.95 * (s.length - 1))];
  };
  const overallP95 = p95(overall) || 365;
  const out = { _overall: overallP95 };
  for (const [div, vals] of Object.entries(buckets)) {
    out[div] = vals.length >= minSample ? p95(vals) : overallP95;
  }
  try { writeFileSync(CPV_P95_CACHE, JSON.stringify(out)); } catch {}
  return out;
}

function _classifyOutcomes(db, years, catP95) {
  const rows = db.prepare(`
    WITH buyer_notices AS (
      SELECT n.ocid, n.published_date, n.tender_status, n.latest_tag,
             COALESCE(n.data_source, 'fts') AS src,
             CAST(julianday('now') - julianday(n.published_date) AS INTEGER) AS age_days
      FROM notices n
      JOIN _bb_ids b ON n.buyer_id = b.id
      WHERE n.published_date >= datetime('now', '-${years} years')
        AND n.published_date IS NOT NULL
    ),
    award_agg AS (
      SELECT a.ocid,
             SUM(CASE WHEN a.status IN ('active','pending') THEN 1 ELSE 0 END) AS awarded_n,
             SUM(CASE WHEN a.status = 'unsuccessful' THEN 1 ELSE 0 END) AS unsucc_n,
             COUNT(*) AS total_aw
      FROM awards a WHERE a.ocid IN (SELECT ocid FROM buyer_notices)
      GROUP BY a.ocid
    ),
    cpv_first AS (
      SELECT c.ocid, MIN(SUBSTR(c.code, 1, 2)) AS cpv_div
      FROM cpv_codes c WHERE c.ocid IN (SELECT ocid FROM buyer_notices)
      GROUP BY c.ocid
    )
    SELECT bn.ocid, bn.src, bn.published_date, bn.tender_status, bn.latest_tag,
           bn.age_days, cf.cpv_div,
           COALESCE(aa.awarded_n, 0) AS awarded_n,
           COALESCE(aa.unsucc_n, 0)  AS unsucc_n,
           COALESCE(aa.total_aw, 0)  AS total_aw
    FROM buyer_notices bn
    LEFT JOIN award_agg aa ON aa.ocid = bn.ocid
    LEFT JOIN cpv_first cf ON cf.ocid = bn.ocid
  `).all();

  const overall = catP95?._overall || 365;
  const out = [];
  for (const r of rows) {
    let bucket;
    if (r.awarded_n > 0) {
      bucket = 'awarded';
    } else if (r.src === 'fts' && (
      r.tender_status === 'cancelled' ||
      r.tender_status === 'withdrawn' ||
      r.latest_tag === 'tenderCancellation'
    )) {
      bucket = 'cancelled';
    } else if (r.tender_status === 'unsuccessful' ||
               (r.total_aw > 0 && r.unsucc_n === r.total_aw)) {
      bucket = 'noCompliantBid';
    } else {
      const threshold = (catP95?.[r.cpv_div] ?? overall) + 90;
      bucket = (r.age_days != null && r.age_days > threshold) ? 'dormant' : 'inFlight';
    }
    out.push({ ocid: r.ocid, src: r.src, bucket, cpvDiv: r.cpv_div, ageDays: r.age_days });
  }
  return out;
}

function _sectionVolume(db, years) {
  const rows = db.prepare(`
    SELECT CAST(STRFTIME('%Y', n.published_date) AS INTEGER) AS yr,
           COALESCE(n.data_source, 'fts')                    AS src,
           COUNT(*)                                          AS notices
    FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
    WHERE n.published_date >= datetime('now', '-${years} years')
    GROUP BY yr, src ORDER BY yr ASC, src ASC
  `).all();
  const awardRows = db.prepare(`
    SELECT CAST(STRFTIME('%Y', a.award_date) AS INTEGER) AS yr,
           COUNT(DISTINCT a.id) AS awards
    FROM awards a
    JOIN notices n ON a.ocid = n.ocid
    JOIN _bb_ids b ON n.buyer_id = b.id
    WHERE a.award_date >= datetime('now', '-${years} years')
      AND a.status IN ('active','pending')
    GROUP BY yr ORDER BY yr ASC
  `).all();
  const awardsByYr = {};
  for (const r of awardRows) if (r.yr) awardsByYr[r.yr] = r.awards;
  const byYrSrc = {}, byYr = {};
  for (const r of rows) {
    if (!r.yr) continue;
    byYr[r.yr] = (byYr[r.yr] || 0) + r.notices;
    byYrSrc[`${r.yr}|${r.src}`] = r.notices;
  }
  const yrs = Object.keys(byYr).map(Number).sort((a, b) => a - b);
  let totalNotices = 0, ftsTotal = 0, cfTotal = 0, awTotal = 0;
  const byYear = yrs.map(y => {
    const fts = byYrSrc[`${y}|fts`] || 0;
    const cf  = byYrSrc[`${y}|cf`]  || 0;
    const aw  = awardsByYr[y] || 0;
    totalNotices += byYr[y]; ftsTotal += fts; cfTotal += cf; awTotal += aw;
    return { year: y, notices: byYr[y], fts, cf, awards: aw };
  });
  let trendDirection = null, trendDeltaPct = null;
  if (yrs.length >= 3) {
    const recent = byYr[yrs[yrs.length - 2]];
    const prior  = byYr[yrs[yrs.length - 3]];
    if (prior) {
      const d = ((recent - prior) * 100.0) / prior;
      trendDeltaPct = Number(d.toFixed(0));
      trendDirection = d > 10 ? 'growing' : d < -10 ? 'shrinking' : 'steady';
    }
  }
  return {
    totalNotices, ftsNotices: ftsTotal, cfNotices: cfTotal,
    totalAwards: awTotal, byYear, trendDirection, trendDeltaPct,
  };
}

function _sectionMethodMix(db, years) {
  const rows = db.prepare(`
    SELECT n.procurement_method AS method,
           n.procurement_method_detail AS detail,
           COUNT(*) AS n
    FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
    WHERE COALESCE(n.data_source, 'fts') = 'fts'
      AND n.published_date >= datetime('now', '-${years} years')
    GROUP BY method, detail
  `).all();
  const ftsTotal = rows.reduce((s, r) => s + r.n, 0);
  const byMethod = {};
  let frameworkCalloff = 0;
  for (const r of rows) {
    const d = (r.detail || '').toLowerCase();
    if (d.includes('framework') || d.includes('call-off') || d.includes('call off')) {
      frameworkCalloff += r.n;
    } else {
      const m = r.method || 'unknown';
      byMethod[m] = (byMethod[m] || 0) + r.n;
    }
  }
  if (frameworkCalloff) byMethod['framework_call_off'] = frameworkCalloff;

  const methods = Object.entries(byMethod)
    .map(([method, count]) => ({ method, count, sharePct: _safePct(count, ftsTotal) }))
    .sort((a, b) => b.count - a.count);

  const cfNoMethod = db.prepare(`
    SELECT COUNT(*) AS n FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
    WHERE n.data_source = 'cf'
      AND n.published_date >= datetime('now', '-${years} years')
  `).get().n;

  return { ftsTotal, cfNoMethodCount: cfNoMethod, methods };
}

function _sectionCompetition(db, years) {
  const overall = db.prepare(`
    SELECT AVG(n.total_bids) AS avg_bids, COUNT(n.total_bids) AS n
    FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
    WHERE n.published_date >= datetime('now', '-${years} years')
      AND n.total_bids IS NOT NULL AND n.total_bids > 0
  `).get();
  if (!overall.n) return { avgBidders: null, bidRecordedN: 0, byYear: [] };

  const yearly = db.prepare(`
    SELECT CAST(STRFTIME('%Y', n.published_date) AS INTEGER) AS yr,
           AVG(n.total_bids) AS avg_bids, COUNT(*) AS n
    FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
    WHERE n.published_date >= datetime('now', '-${years} years')
      AND n.total_bids > 0
    GROUP BY yr ORDER BY yr ASC
  `).all().filter(r => r.yr);

  const lowComp = db.prepare(`
    SELECT COUNT(*) AS n FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
    WHERE n.published_date >= datetime('now', '-${years} years')
      AND n.total_bids IS NOT NULL AND n.total_bids < 3 AND n.total_bids > 0
  `).get().n;

  let trendDirection = null;
  if (yearly.length >= 3) {
    const first = yearly[0].avg_bids, last = yearly[yearly.length - 1].avg_bids;
    if (first) {
      const d = (last - first) / first;
      trendDirection = d > 0.15 ? 'rising' : d < -0.15 ? 'falling' : 'flat';
    }
  }

  return {
    avgBidders: Number(overall.avg_bids.toFixed(2)),
    bidRecordedN: overall.n,
    byYear: yearly.map(r => ({
      year: r.yr,
      avgBidders: Number(r.avg_bids.toFixed(2)),
      noticesWithBidCount: r.n,
    })),
    lowCompetitionCount: lowComp,
    lowCompetitionSharePct: _safePct(lowComp, overall.n),
    trendDirection,
  };
}

function _sectionOutcomeMix(classified) {
  const total = classified.length;
  const ftsTotal = classified.filter(c => c.src === 'fts').length;
  const counts = { awarded: 0, cancelled: 0, noCompliantBid: 0, dormant: 0, inFlight: 0 };
  for (const c of classified) counts[c.bucket]++;

  let sampleQuality;
  if (total < 10) sampleQuality = 'too_small';
  else if (total < 25) sampleQuality = 'indicative';
  else sampleQuality = 'reliable';

  const closed = counts.awarded + counts.cancelled + counts.noCompliantBid + counts.dormant;

  return {
    sampleSize: total, sampleQuality, ftsTotal,
    buckets: counts,
    sharesPct: {
      awarded:        _safePct(counts.awarded, total),
      cancelled:      _safePct(counts.cancelled, ftsTotal),
      noCompliantBid: _safePct(counts.noCompliantBid, total),
      dormant:        _safePct(counts.dormant, total),
      inFlight:       _safePct(counts.inFlight, total),
    },
    closedTotal: closed,
    awardedOfClosedPct: _safePct(counts.awarded, closed),
  };
}

function _sectionTimeline(db, years) {
  const rows = db.prepare(`
    WITH first_aw AS (
      SELECT n.ocid, n.published_date,
             MIN(COALESCE(a.award_date, a.date_signed, a.contract_start_date)) AS first_aw_date
      FROM notices n JOIN _bb_ids b ON n.buyer_id = b.id
      JOIN awards a ON a.ocid = n.ocid
      WHERE n.published_date >= datetime('now', '-${years} years')
        AND a.status IN ('active','pending')
      GROUP BY n.ocid
    )
    SELECT CAST(julianday(first_aw_date) - julianday(published_date) AS INTEGER) AS days
    FROM first_aw
    WHERE first_aw_date IS NOT NULL AND first_aw_date > published_date
  `).all();
  const days = rows.map(r => r.days)
    .filter(d => d != null && d >= 0 && d < 1500)
    .sort((a, b) => a - b);
  const n = days.length;
  if (n < 25) {
    return {
      pairedN: n,
      suppressedReason: n === 0
        ? 'No paired publication and award dates in window.'
        : `Only ${n} notices have paired dates — too few for percentile analysis.`,
    };
  }
  const pct = p => days[Math.max(0, Math.min(n - 1, Math.floor(p * (n - 1))))];
  return {
    pairedN: n,
    medianDays: pct(0.5),
    p25Days: pct(0.25),
    p75Days: pct(0.75),
    p90Days: pct(0.9),
    p95Days: pct(0.95),
  };
}

function _sectionCategoryFootprint(classified) {
  const byDiv = {};
  for (const c of classified) {
    const d = c.cpvDiv || '??';
    (byDiv[d] ||= { total: 0, awarded: 0, cancelled: 0, ncb: 0, dormant: 0, inFlight: 0 });
    byDiv[d].total++;
    const k = c.bucket === 'noCompliantBid' ? 'ncb'
            : c.bucket === 'inFlight' ? 'inFlight'
            : c.bucket;
    byDiv[d][k]++;
  }
  return Object.entries(byDiv)
    .filter(([, v]) => v.total >= 5)
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, 10)
    .map(([div, v]) => ({
      cpvDivision: div === '??' ? null : div,
      label: _cpvDivisionLabel(div === '??' ? null : div),
      total: v.total,
      awardedPct:    _safePct(v.awarded, v.total),
      cancelledPct:  _safePct(v.cancelled, v.total),
      ncbPct:        _safePct(v.ncb, v.total),
      dormantPct:    _safePct(v.dormant, v.total),
      inFlightPct:   _safePct(v.inFlight, v.total),
    }));
}

function _sectionCancellation(db, years, classified, canonicalType) {
  const fts = classified.filter(c => c.src === 'fts');
  if (!fts.length) {
    return { ftsTotal: 0, cancelledN: 0, suppressed: 'No FTS notices in window.' };
  }
  const cancelled = fts.filter(c => c.bucket === 'cancelled');
  const thisBuyerPct = _safePct(cancelled.length, fts.length);

  let peer = null;
  if (canonicalType) {
    const peerRows = db.prepare(`
      SELECT cb.canonical_id,
             COUNT(*) AS fts_n,
             SUM(CASE WHEN n.tender_status IN ('cancelled','withdrawn')
                        OR n.latest_tag = 'tenderCancellation'
                      THEN 1 ELSE 0 END) AS cancelled_n
      FROM canonical_buyers cb
      JOIN canonical_buyer_aliases a ON a.canonical_id = cb.canonical_id
      JOIN buyers br ON LOWER(TRIM(br.name)) = a.alias_lower
      JOIN notices n ON n.buyer_id = br.id
      WHERE cb.type = ?
        AND COALESCE(n.data_source, 'fts') = 'fts'
        AND n.published_date >= datetime('now', '-${years} years')
      GROUP BY cb.canonical_id
      HAVING fts_n >= 25
    `).all(canonicalType);
    if (peerRows.length) {
      const rates = peerRows.map(r => (r.cancelled_n * 100) / r.fts_n).sort((a, b) => a - b);
      const median = rates[Math.floor(rates.length / 2)];
      const p75 = rates[Math.floor(0.75 * (rates.length - 1))];
      let positionLabel = 'within peer range';
      if (thisBuyerPct > p75) positionLabel = 'above peer P75 — high canceller';
      else if (thisBuyerPct < median) positionLabel = 'below peer median — low canceller';
      peer = {
        peerType: canonicalType,
        peerCount: peerRows.length,
        peerMedianPct: Number(median.toFixed(1)),
        peerP75Pct: Number(p75.toFixed(1)),
        positionLabel,
      };
    } else {
      peer = { peerType: canonicalType, peerCount: 0,
               note: `No peer set with ≥25 FTS notices for type '${canonicalType}'.` };
    }
  }

  // Top cancelled categories
  const byDiv = {};
  for (const c of cancelled) {
    const d = c.cpvDiv || '??';
    byDiv[d] = (byDiv[d] || 0) + 1;
  }
  const topCancelled = Object.entries(byDiv)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([div, n]) => ({
      cpvDivision: div === '??' ? null : div,
      label: _cpvDivisionLabel(div === '??' ? null : div),
      n,
    }));

  // Time-to-cancellation proxy
  let timeToCancel = null;
  if (cancelled.length) {
    const placeholders = cancelled.map(() => '?').join(',');
    const rows = db.prepare(`
      SELECT CAST(julianday(last_updated) - julianday(published_date) AS INTEGER) AS d
      FROM notices WHERE ocid IN (${placeholders})
        AND last_updated > published_date
    `).all(...cancelled.map(c => c.ocid));
    const ttd = rows.map(r => r.d).filter(d => d != null && d >= 0).sort((a, b) => a - b);
    if (ttd.length) {
      const pct = p => ttd[Math.max(0, Math.min(ttd.length - 1, Math.floor(p * (ttd.length - 1))))];
      timeToCancel = { n: ttd.length, medianDays: pct(0.5),
                       p75Days: pct(0.75), p90Days: pct(0.9) };
    }
  }

  return {
    ftsTotal: fts.length,
    cancelledN: cancelled.length,
    thisBuyerPct,
    peer,
    topCancelledCategories: topCancelled,
    timeToCancel,
  };
}

function _sectionDistress(db) {
  const rows = db.prepare(`
    SELECT n.title, b.name AS buyer_name,
           s.name AS supplier_name, s.ch_status,
           a.value_amount_gross, a.contract_end_date
    FROM awards a
    JOIN notices n        ON n.ocid = a.ocid
    JOIN _bb_ids bb       ON bb.id = n.buyer_id
    JOIN buyers b         ON b.id = n.buyer_id
    JOIN award_suppliers asup ON asup.award_id = a.id
    JOIN suppliers s      ON s.id = asup.supplier_id
    WHERE a.status IN ('active', 'pending')
      AND a.contract_end_date > datetime('now')
      AND s.ch_status IN ('dissolved', 'liquidation', 'administration',
                          'receivership', 'in-administration',
                          'voluntary-arrangement', 'compulsory-strike-off',
                          'cessation', 'closed')
    ORDER BY a.contract_end_date ASC LIMIT 20
  `).all();
  return {
    count: rows.length,
    coverageNote: 'Only ~27% of suppliers carry a Companies House number; this flag fires only on enriched suppliers. ch_status \'dissolved\' is currently the only distress value populated in the data.',
    contracts: rows.map(r => ({
      title: r.title,
      supplierName: r.supplier_name,
      chStatus: r.ch_status,
      contractValue: r.value_amount_gross,
      contractEndDate: r.contract_end_date,
    })),
  };
}

function _composeSummary(buyerName, years, outcomeMix, timeline, distress) {
  if (!outcomeMix || !outcomeMix.closedTotal || outcomeMix.closedTotal < 25) {
    return null;
  }
  const closed = outcomeMix.closedTotal;
  const c = outcomeMix.buckets;
  const award = (c.awarded * 100 / closed).toFixed(0);
  const cancel = (c.cancelled * 100 / closed).toFixed(0);
  const ncb = (c.noCompliantBid * 100 / closed).toFixed(0);
  const dorm = (c.dormant * 100 / closed).toFixed(0);
  let timelineClause = '';
  if (timeline?.medianDays != null) {
    timelineClause = ` Median time from publication to award was ${timeline.medianDays} days, with the slowest 10% taking over ${timeline.p90Days} days.`;
  }
  let distressClause = '';
  if (distress?.count) {
    distressClause = ` ${distress.count} live contract${distress.count !== 1 ? 's' : ''} in this buyer's portfolio currently has an incumbent in financial distress.`;
  }
  return `Over the last ${years} years, ${buyerName} published ${outcomeMix.sampleSize.toLocaleString()} tenders (${closed.toLocaleString()} now closed). ${award}% reached award, ${cancel}% were cancelled (FTS-tracked), ${ncb}% received no compliant bid, ${dorm}% went dormant.${timelineClause}${distressClause} PGO benchmark for tenders from this buyer: ${award}% historical award rate.`;
}

function buyerBehaviourProfile(nameQuery, { years = 5 } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found. Run pwin-competitive-intel/agent/ingest.py first.' };
  try {
    const resolved = _resolveBuyerCanonical(db, nameQuery);
    if (!resolved) return { error: `No buyer found matching '${nameQuery}'.` };
    if (resolved.ambiguous) {
      return {
        error: 'Ambiguous buyer name — please be more specific.',
        candidates: resolved.candidates,
      };
    }
    if (!resolved.rawBuyerIds.length) {
      return { error: `Buyer '${resolved.canonicalName}' has no rows in the database.` };
    }

    _stageBuyerIdTempTable(db, resolved.rawBuyerIds);
    const catP95 = _computeCpvP95(db);

    const volume       = _sectionVolume(db, years);
    const methodMix    = _sectionMethodMix(db, years);
    const competition  = _sectionCompetition(db, years);
    const classified   = _classifyOutcomes(db, years, catP95);
    const outcomeMix   = _sectionOutcomeMix(classified);
    const timeline     = _sectionTimeline(db, years);
    const categoryFootprint = _sectionCategoryFootprint(classified);
    const cancellation = _sectionCancellation(db, years, classified, resolved.canonicalType);
    const distress     = _sectionDistress(db);
    const summary      = _composeSummary(resolved.canonicalName, years,
                                         outcomeMix, timeline, distress);

    return {
      meta: {
        canonicalId:      resolved.canonicalId,
        canonicalName:    resolved.canonicalName,
        canonicalType:    resolved.canonicalType,
        rawBuyerIdCount:  resolved.rawBuyerIds.length,
        fragmented:       resolved.fragmented,
        yearsWindow:      years,
        generatedAt:      new Date().toISOString(),
      },
      volume,
      methodMix,
      competition,
      outcomeMix,
      timeline,
      categoryFootprint,
      cancellation,
      distress,
      summary,
      caveats: [
        'Cancellation analysis is FTS-only — Contracts Finder rows have no cancellation marker.',
        'Procurement-method mix is FTS-only — both method columns are unpopulated for Contracts Finder rows.',
        'Amendment behaviour deferred to Phase 2 (no usable amendment trail in current schema).',
        'Distress flag fires only on enriched suppliers (~27% coverage) and only on ch_status=\'dissolved\'.',
        'Peer comparison uses canonical_buyers.type only (region is unpopulated for Contracts Finder).',
      ],
    };
  } finally {
    db.close();
  }
}

// ── Frameworks ────────────────────────────────────────────────────────────

function frameworkProfile(query) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    // Try exact reference_no first, then partial name match
    let fw = db.prepare(
      "SELECT * FROM frameworks WHERE upper(reference_no)=upper(?)"
    ).get(query);
    if (!fw) {
      fw = db.prepare(
        "SELECT * FROM frameworks WHERE instr(lower(name), lower(?)) > 0 ORDER BY call_off_value_total DESC LIMIT 1"
      ).get(query);
    }
    if (!fw) return { error: `No framework found matching '${query}'` };

    const lots = db.prepare(
      "SELECT * FROM framework_lots WHERE framework_id=? ORDER BY lot_number"
    ).all(fw.id);

    const topSuppliers = db.prepare(`
      SELECT supplier_name_raw, supplier_canonical_id,
             call_off_count, call_off_value
      FROM framework_suppliers WHERE framework_id=?
      ORDER BY call_off_value DESC LIMIT 10
    `).all(fw.id);

    return {
      id: fw.id,
      name: fw.name,
      referenceNo: fw.reference_no,
      owner: fw.owner,
      ownerType: fw.owner_type,
      category: fw.category,
      description: fw.description,
      status: fw.status,
      expiryDate: fw.expiry_date,
      routeType: fw.route_type,
      maxValue: fw.max_value,
      callOffCount: fw.call_off_count,
      callOffValueTotal: fw.call_off_value_total,
      source: fw.source,
      lots: lots.map(l => ({
        lotNumber: l.lot_number,
        lotName: l.lot_name,
        scope: l.scope,
        supplierCount: l.supplier_count,
      })),
      topSuppliers: topSuppliers.map(s => ({
        name: s.supplier_name_raw,
        canonicalId: s.supplier_canonical_id,
        callOffCount: s.call_off_count,
        callOffValue: s.call_off_value,
      })),
    };
  } finally {
    db.close();
  }
}

function searchFrameworks(query, { ownerType, category, status, expiringWithinMonths } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const conditions = [];
    const params = [];

    if (query) {
      conditions.push("(instr(lower(name), lower(?)) > 0 OR upper(reference_no) = upper(?))");
      params.push(query, query);
    }
    if (ownerType) {
      conditions.push("owner_type = ?");
      params.push(ownerType);
    }
    if (category) {
      conditions.push("instr(lower(category), lower(?)) > 0");
      params.push(category);
    }
    if (status) {
      conditions.push("status = ?");
      params.push(status);
    }
    if (expiringWithinMonths) {
      conditions.push("expiry_date IS NOT NULL AND expiry_date <= date('now', '+' || ? || ' months')");
      params.push(expiringWithinMonths);
    }

    const where = conditions.length ? "WHERE " + conditions.join(" AND ") : "";
    const rows = db.prepare(`
      SELECT id, name, reference_no, owner, owner_type, category, status,
             expiry_date, call_off_count, call_off_value_total, source
      FROM frameworks ${where}
      ORDER BY call_off_value_total DESC NULLS LAST
      LIMIT 50
    `).all(...params);

    return {
      count: rows.length,
      frameworks: rows.map(r => ({
        id: r.id,
        name: r.name,
        referenceNo: r.reference_no,
        owner: r.owner,
        ownerType: r.owner_type,
        category: r.category,
        status: r.status,
        expiryDate: r.expiry_date,
        callOffCount: r.call_off_count,
        callOffValueTotal: r.call_off_value_total,
        source: r.source,
      })),
    };
  } finally {
    db.close();
  }
}

function buyerFrameworkUsage(buyerQuery) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const resolved = _resolveBuyerCanonical(db, buyerQuery);
    if (!resolved) return { error: `No buyer found matching '${buyerQuery}'` };
    if (resolved.ambiguous) return { error: 'Ambiguous buyer name', candidates: resolved.candidates };

    if (!resolved.canonicalId) {
      // framework_call_offs stores canonical IDs; a raw ID fallback would silently
      // return zero rows. Surface the gap so callers know why results are empty.
      return {
        buyer: resolved.canonicalName || buyerQuery,
        frameworkCount: 0,
        frameworks: [],
        warning: 'Buyer not fully canonicalised — framework usage data may be incomplete.',
      };
    }
    const canonicalId = resolved.canonicalId;

    const usage = db.prepare(`
      SELECT f.id, f.name, f.reference_no, f.owner, f.category, f.status, f.expiry_date,
             COUNT(co.id) AS call_off_count,
             SUM(co.value) AS total_value,
             MIN(co.awarded_date) AS first_date,
             MAX(co.awarded_date) AS last_date
      FROM framework_call_offs co
      JOIN frameworks f ON co.framework_id = f.id
      WHERE co.buyer_canonical_id = ?
      GROUP BY f.id
      ORDER BY total_value DESC NULLS LAST
    `).all(canonicalId);

    return {
      buyer: resolved.canonicalName || buyerQuery,
      frameworkCount: usage.length,
      frameworks: usage.map(r => ({
        id: r.id,
        name: r.name,
        referenceNo: r.reference_no,
        owner: r.owner,
        category: r.category,
        status: r.status,
        expiryDate: r.expiry_date,
        callOffCount: r.call_off_count,
        totalValue: r.total_value,
        firstDate: r.first_date,
        lastDate: r.last_date,
      })),
    };
  } finally {
    db.close();
  }
}

function supplierFrameworkPosition(supplierQuery) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    // Resolve to canonical supplier id via name search
    const sup = db.prepare(`
      SELECT COALESCE(s2c.canonical_id, 'RAW-' || s.id) AS canonical_id,
             COALESCE(cs.canonical_name, s.name) AS canonical_name
      FROM suppliers s
      LEFT JOIN supplier_to_canonical s2c ON s.id = s2c.supplier_id
      LEFT JOIN canonical_suppliers cs ON s2c.canonical_id = cs.canonical_id
      WHERE instr(lower(s.name), lower(?)) > 0
      LIMIT 1
    `).get(supplierQuery);

    if (!sup) return { error: `No supplier found matching '${supplierQuery}'` };

    const positions = db.prepare(`
      SELECT f.id, f.name, f.reference_no, f.owner, f.category, f.status, f.expiry_date,
             fl.lot_number, fl.lot_name,
             fs.status AS position_status, fs.awarded_date,
             fs.call_off_count, fs.call_off_value
      FROM framework_suppliers fs
      JOIN frameworks f ON fs.framework_id = f.id
      LEFT JOIN framework_lots fl ON fs.lot_id = fl.id
      WHERE fs.supplier_canonical_id = ?
      ORDER BY fs.call_off_value DESC NULLS LAST
    `).all(sup.canonical_id);

    return {
      supplier: sup.canonical_name,
      canonicalId: sup.canonical_id,
      positionCount: positions.length,
      positions: positions.map(r => ({
        frameworkId: r.id,
        frameworkName: r.name,
        referenceNo: r.reference_no,
        owner: r.owner,
        category: r.category,
        frameworkStatus: r.status,
        expiryDate: r.expiry_date,
        lotNumber: r.lot_number,
        lotName: r.lot_name,
        positionStatus: r.position_status,
        awardedDate: r.awarded_date,
        callOffCount: r.call_off_count,
        callOffValue: r.call_off_value,
      })),
    };
  } finally {
    db.close();
  }
}

function frameworkCallOffs(frameworkQuery, { buyer, supplier, since, limit = 20 } = {}) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    // Resolve framework
    let fw = db.prepare(
      "SELECT id, name FROM frameworks WHERE upper(reference_no)=upper(?)"
    ).get(frameworkQuery);
    if (!fw) {
      fw = db.prepare(
        "SELECT id, name FROM frameworks WHERE instr(lower(name), lower(?)) > 0 ORDER BY call_off_value_total DESC LIMIT 1"
      ).get(frameworkQuery);
    }
    if (!fw) return { error: `No framework found matching '${frameworkQuery}'` };

    const conditions = ["co.framework_id = ?"];
    const params = [fw.id];

    if (buyer) { conditions.push("instr(lower(co.buyer_canonical_id), lower(?)) > 0"); params.push(buyer); }
    if (supplier) { conditions.push("instr(lower(co.supplier_canonical_id), lower(?)) > 0"); params.push(supplier); }
    if (since) { conditions.push("co.awarded_date >= ?"); params.push(since); }
    params.push(limit);

    const callOffs = db.prepare(`
      SELECT co.notice_ocid, co.buyer_canonical_id, co.supplier_canonical_id,
             co.value, co.awarded_date, co.contract_title,
             co.match_method, co.match_confidence
      FROM framework_call_offs co
      WHERE ${conditions.join(" AND ")}
      ORDER BY co.awarded_date DESC NULLS LAST
      LIMIT ?
    `).all(...params);

    return {
      framework: fw.name,
      frameworkId: fw.id,
      callOffCount: callOffs.length,
      callOffs: callOffs.map(r => ({
        noticeOcid: r.notice_ocid,
        buyer: r.buyer_canonical_id,
        supplier: r.supplier_canonical_id,
        value: r.value,
        awardedDate: r.awarded_date,
        title: r.contract_title,
        matchMethod: r.match_method,
        matchConfidence: r.match_confidence,
      })),
    };
  } finally {
    db.close();
  }
}

export {
  dbSummary,
  buyerProfile,
  supplierProfile,
  sectorProfile,
  expiringContracts,
  forwardPipeline,
  pwinSignals,
  cpvSearch,
  pipelineRecentNotices,
  pipelineRecentAwardsForBuyers,
  buyerBehaviourProfile,
  frameworkProfile,
  searchFrameworks,
  buyerFrameworkUsage,
  supplierFrameworkPosition,
  frameworkCallOffs,
};
