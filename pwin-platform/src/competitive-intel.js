/**
 * PWIN Platform — Competitive Intelligence Module
 *
 * Read-only queries against the pwin-competitive-intel SQLite database.
 * Built on the UK Find a Tender Service OCDS data.
 * Uses Node.js built-in node:sqlite (Node 22+).
 */

import { DatabaseSync } from 'node:sqlite';
import { join } from 'node:path';
import { existsSync } from 'node:fs';

// Database path — sibling product folder
const DB_PATH = join(import.meta.dirname, '..', '..', 'pwin-competitive-intel', 'db', 'bid_intel.db');

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
    const buyers = db.prepare(`
      SELECT id, name, org_type, region_code FROM buyers
      WHERE LOWER(name) LIKE LOWER(?)
      ORDER BY name LIMIT 10
    `).all(`%${nameQuery}%`);

    if (!buyers.length) return { buyers: [], message: `No buyers matching '${nameQuery}'` };

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
          SELECT s.name, COUNT(DISTINCT a.id) AS wins,
                 SUM(a.value_amount_gross) AS total_value
          FROM award_suppliers asup
          JOIN suppliers s ON asup.supplier_id = s.id
          JOIN awards a ON asup.award_id = a.id
          JOIN notices n ON a.ocid = n.ocid
          WHERE n.buyer_id = ?
          GROUP BY s.id ORDER BY wins DESC, total_value DESC LIMIT 15
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
    };
  } finally {
    db.close();
  }
}

// ── Supplier Profile ─────────────────────────────────────────────────────

function supplierProfile(nameQuery, limit = 20) {
  const db = getDb();
  if (!db) return { error: 'Database not found' };
  try {
    const suppliers = db.prepare(`
      SELECT id, name, scale, is_vcse, companies_house_no FROM suppliers
      WHERE LOWER(name) LIKE LOWER(?)
      ORDER BY name LIMIT 10
    `).all(`%${nameQuery}%`);

    if (!suppliers.length) return { suppliers: [], message: `No suppliers matching '${nameQuery}'` };

    return {
      suppliers: suppliers.map(sup => {
        const stats = db.prepare(`
          SELECT
            COUNT(DISTINCT a.id) AS total_wins,
            SUM(a.value_amount_gross) AS total_value,
            AVG(a.value_amount_gross) AS avg_value,
            MAX(a.value_amount_gross) AS max_value,
            MIN(a.award_date) AS first_win,
            MAX(a.award_date) AS last_win
          FROM award_suppliers asup
          JOIN awards a ON asup.award_id = a.id
          WHERE asup.supplier_id = ?
        `).get(sup.id);

        const buyerRelationships = db.prepare(`
          SELECT b.name, COUNT(DISTINCT a.id) AS awards,
                 SUM(a.value_amount_gross) AS total_value,
                 MAX(a.contract_end_date) AS latest_expiry
          FROM award_suppliers asup
          JOIN awards a ON asup.award_id = a.id
          JOIN notices n ON a.ocid = n.ocid
          JOIN buyers b ON n.buyer_id = b.id
          WHERE asup.supplier_id = ?
          GROUP BY b.id ORDER BY awards DESC LIMIT 15
        `).all(sup.id);

        const activeContracts = db.prepare(`
          SELECT n.title, b.name AS buyer, a.value_amount_gross,
                 a.contract_end_date, a.contract_max_extend
          FROM award_suppliers asup
          JOIN awards a ON asup.award_id = a.id
          JOIN notices n ON a.ocid = n.ocid
          JOIN buyers b ON n.buyer_id = b.id
          WHERE asup.supplier_id = ?
            AND a.contract_end_date > datetime('now')
          ORDER BY a.contract_end_date ASC LIMIT 20
        `).all(sup.id);

        return {
          ...sup,
          isVcse: !!sup.is_vcse,
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

export {
  dbSummary,
  buyerProfile,
  supplierProfile,
  expiringContracts,
  forwardPipeline,
  pwinSignals,
  cpvSearch,
};
