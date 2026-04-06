/**
 * PWIN Competitive Intelligence — Cloudflare Worker
 *
 * Serves procurement intelligence from D1 (serverless SQLite).
 * Called by Qualify app for AI assurance context enrichment.
 *
 * Deploy:  cd workers && npx wrangler deploy
 * D1 setup: npx wrangler d1 create pwin-competitive-intel
 *           npx wrangler d1 execute pwin-competitive-intel --file=../db/schema.sql
 */

function cors(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Cache-Control': 'public, max-age=300',
    },
  });
}

// ── Route handlers ────────────────────────────────────────────

async function summary(db) {
  const tables = ['buyers', 'suppliers', 'notices', 'lots', 'awards', 'award_suppliers', 'cpv_codes', 'planning_notices'];
  const counts = {};
  for (const t of tables) {
    const r = await db.prepare(`SELECT COUNT(*) as cnt FROM ${t}`).first();
    counts[t] = r.cnt;
  }

  const cursor = await db.prepare("SELECT value FROM ingest_state WHERE key='last_cursor'").first();
  const val = await db.prepare("SELECT SUM(value_amount_gross) as total, AVG(value_amount_gross) as avg, MAX(value_amount_gross) as mx FROM awards WHERE value_amount_gross IS NOT NULL").first();

  const topCpv = (await db.prepare("SELECT code, description, COUNT(*) AS cnt FROM cpv_codes GROUP BY code ORDER BY cnt DESC LIMIT 15").all()).results;
  const methods = (await db.prepare(`
    SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
    FROM awards a JOIN notices n ON a.ocid = n.ocid
    WHERE a.status IN ('active', 'pending')
    GROUP BY n.procurement_method ORDER BY cnt DESC
  `).all()).results;

  const methodMap = { open: 0, limited: 0, direct: 0, selective: 0 };
  for (const m of methods) {
    if (m.procurement_method in methodMap) methodMap[m.procurement_method] = m.cnt;
  }

  return cors({
    buyers: counts.buyers, suppliers: counts.suppliers,
    notices: counts.notices, awards: counts.awards,
    total_value: val.total, avg_value: val.avg, max_value: val.mx,
    last_ingest: cursor?.value || null,
    top_cpv: topCpv.map(r => ({ code: r.code, description: r.description, awards: r.cnt })),
    methods: methodMap,
  });
}

async function buyerProfile(db, name, limit = 20) {
  if (!name) return cors({ error: 'name parameter required' }, 400);

  const buyers = (await db.prepare(`
    SELECT id, name, org_type, region_code FROM buyers
    WHERE LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 10
  `).bind(`%${name}%`).all()).results;

  if (!buyers.length) return cors({ buyers: [], message: `No buyers matching '${name}'` });

  const results = [];
  for (const buyer of buyers) {
    const stats = await db.prepare(`
      SELECT COUNT(DISTINCT a.id) AS total_awards,
             SUM(a.value_amount_gross) AS total_spend,
             AVG(a.value_amount_gross) AS avg_value,
             MAX(a.value_amount_gross) AS max_value,
             AVG(n.total_bids) AS avg_bids
      FROM awards a JOIN notices n ON a.ocid = n.ocid
      WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
    `).bind(buyer.id).first();

    const methodRows = (await db.prepare(`
      SELECT n.procurement_method, COUNT(DISTINCT a.id) AS cnt
      FROM awards a JOIN notices n ON a.ocid = n.ocid
      WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
      GROUP BY n.procurement_method ORDER BY cnt DESC
    `).bind(buyer.id).all()).results;

    const methodMap = { open: 0, limited: 0, direct: 0, selective: 0 };
    for (const m of methodRows) {
      if (m.procurement_method in methodMap) methodMap[m.procurement_method] = m.cnt;
    }

    const topSuppliers = (await db.prepare(`
      SELECT s.name, COUNT(DISTINCT a.id) AS wins, SUM(a.value_amount_gross) AS total_value
      FROM award_suppliers asup
      JOIN suppliers s ON asup.supplier_id = s.id
      JOIN awards a ON asup.award_id = a.id
      JOIN notices n ON a.ocid = n.ocid
      WHERE n.buyer_id = ?
      GROUP BY s.id ORDER BY wins DESC, total_value DESC LIMIT 15
    `).bind(buyer.id).all()).results;

    const recentAwards = (await db.prepare(`
      SELECT n.title, a.value_amount_gross, n.procurement_method,
             a.contract_end_date, a.award_date
      FROM awards a
      JOIN notices n ON a.ocid = n.ocid
      WHERE n.buyer_id = ? AND a.status IN ('active', 'pending')
      ORDER BY a.award_date DESC NULLS LAST LIMIT ?
    `).bind(buyer.id, limit).all()).results;

    results.push({
      name: buyer.name, org_type: buyer.org_type, region_code: buyer.region_code,
      awards: stats.total_awards, total_spend: stats.total_spend,
      avg_value: stats.avg_value, max_value: stats.max_value, avg_bids: stats.avg_bids,
      methods: methodMap,
      top_suppliers: topSuppliers.map(s => ({ name: s.name, awards: s.wins, value: s.total_value })),
      recent_awards: recentAwards.map(a => ({
        title: a.title, value: a.value_amount_gross, method: a.procurement_method,
        date: a.award_date, end_date: a.contract_end_date,
      })),
    });
  }

  return cors({ buyers: results });
}

async function supplierProfile(db, name) {
  if (!name) return cors({ error: 'name parameter required' }, 400);

  const suppliers = (await db.prepare(`
    SELECT id, name, scale, is_vcse, companies_house_no FROM suppliers
    WHERE LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 10
  `).bind(`%${name}%`).all()).results;

  if (!suppliers.length) return cors({ suppliers: [], message: `No suppliers matching '${name}'` });

  const results = [];
  for (const sup of suppliers) {
    const stats = await db.prepare(`
      SELECT COUNT(DISTINCT a.id) AS total_wins, SUM(a.value_amount_gross) AS total_value,
             AVG(a.value_amount_gross) AS avg_value,
             MIN(a.award_date) AS first_win, MAX(a.award_date) AS last_win
      FROM award_suppliers asup JOIN awards a ON asup.award_id = a.id
      WHERE asup.supplier_id = ?
    `).bind(sup.id).first();

    const buyerRels = (await db.prepare(`
      SELECT b.name, COUNT(DISTINCT a.id) AS awards, SUM(a.value_amount_gross) AS total_value
      FROM award_suppliers asup
      JOIN awards a ON asup.award_id = a.id
      JOIN notices n ON a.ocid = n.ocid
      JOIN buyers b ON n.buyer_id = b.id
      WHERE asup.supplier_id = ?
      GROUP BY b.id ORDER BY awards DESC LIMIT 15
    `).bind(sup.id).all()).results;

    const active = (await db.prepare(`
      SELECT n.title, b.name AS buyer, a.value_amount_gross,
             a.contract_end_date, a.contract_max_extend
      FROM award_suppliers asup
      JOIN awards a ON asup.award_id = a.id
      JOIN notices n ON a.ocid = n.ocid
      JOIN buyers b ON n.buyer_id = b.id
      WHERE asup.supplier_id = ? AND a.contract_end_date > datetime('now')
      ORDER BY a.contract_end_date ASC LIMIT 20
    `).bind(sup.id).all()).results;

    results.push({
      name: sup.name, scale: sup.scale, is_vcse: !!sup.is_vcse,
      companies_house_no: sup.companies_house_no,
      wins: stats.total_wins, total_value: stats.total_value,
      avg_value: stats.avg_value, first_win: stats.first_win, last_win: stats.last_win,
      buyers: buyerRels.map(b => ({ name: b.name, awards: b.awards, value: b.total_value })),
      active_contracts: active.map(c => ({
        title: c.title, buyer: c.buyer, value: c.value_amount_gross,
        end_date: c.contract_end_date, max_extend: c.contract_max_extend,
      })),
    });
  }

  return cors({ suppliers: results });
}

async function pwinSignals(db, buyer, category) {
  let sql = `
    SELECT buyer_name, main_category, awards_count, avg_bids_per_tender,
           avg_award_value, open_awards, limited_awards, direct_awards, selective_awards
    FROM v_pwin_signals WHERE 1=1
  `;
  const binds = [];
  if (buyer) { sql += " AND LOWER(buyer_name) LIKE LOWER(?)"; binds.push(`%${buyer}%`); }
  if (category) { sql += " AND LOWER(main_category) LIKE LOWER(?)"; binds.push(`%${category}%`); }
  sql += " LIMIT 100";

  const stmt = binds.length ? db.prepare(sql).bind(...binds) : db.prepare(sql);
  const rows = (await stmt.all()).results;

  return cors({
    count: rows.length,
    signals: rows.map(r => ({
      buyer: r.buyer_name, category: r.main_category,
      awards: r.awards_count, avg_bids: r.avg_bids_per_tender, avg_value: r.avg_award_value,
      methods: {
        open: r.open_awards || 0, limited: r.limited_awards || 0,
        direct: r.direct_awards || 0, selective: r.selective_awards || 0,
      },
    })),
  });
}

async function expiringContracts(db, { days = 365, minValue, buyer, category }) {
  let sql = "SELECT * FROM v_expiring_contracts WHERE days_to_expiry <= ?";
  const binds = [days];
  if (minValue > 0) { sql += " AND value_amount_gross >= ?"; binds.push(minValue); }
  if (buyer) { sql += " AND LOWER(buyer_name) LIKE LOWER(?)"; binds.push(`%${buyer}%`); }
  if (category) { sql += " AND LOWER(main_category) LIKE LOWER(?)"; binds.push(`%${category}%`); }
  sql += " ORDER BY days_to_expiry ASC LIMIT 200";

  const rows = (await db.prepare(sql).bind(...binds).all()).results;
  return cors({
    count: rows.length,
    contracts: rows.map(r => ({
      buyer: r.buyer_name, supplier: r.supplier_names, title: r.title,
      value: r.value_amount_gross, days_to_expiry: r.days_to_expiry,
      method: r.procurement_method, end_date: r.contract_end_date,
    })),
  });
}

async function forwardPipeline(db, buyer) {
  let sql = `
    SELECT p.title, p.description, p.engagement_deadline, p.future_notice_date,
           p.estimated_value, p.notice_url, b.name AS buyer_name
    FROM planning_notices p JOIN buyers b ON p.buyer_id = b.id WHERE 1=1
  `;
  const binds = [];
  if (buyer) { sql += " AND LOWER(b.name) LIKE LOWER(?)"; binds.push(`%${buyer}%`); }
  sql += ` ORDER BY CASE WHEN p.future_notice_date IS NOT NULL
           THEN p.future_notice_date ELSE p.engagement_deadline END ASC LIMIT 200`;

  const stmt = binds.length ? db.prepare(sql).bind(...binds) : db.prepare(sql);
  const rows = (await stmt.all()).results;

  return cors({
    count: rows.length,
    notices: rows.map(r => ({
      buyer: r.buyer_name, title: r.title, estimated_value: r.estimated_value,
      engagement_deadline: r.engagement_deadline, future_notice_date: r.future_notice_date,
      notice_url: r.notice_url, description: r.description,
    })),
  });
}

// ── Router ────────────────────────────────────────────────────

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    if (request.method !== 'GET') {
      return cors({ error: 'Method not allowed' }, 405);
    }

    const url = new URL(request.url);
    const path = url.pathname;
    const db = env.DB;

    try {
      if (path === '/api/intel/summary') return await summary(db);
      if (path === '/api/intel/buyer') return await buyerProfile(db, url.searchParams.get('name'), parseInt(url.searchParams.get('limit') || '20'));
      if (path === '/api/intel/supplier') return await supplierProfile(db, url.searchParams.get('name'));
      if (path === '/api/intel/pwin') return await pwinSignals(db, url.searchParams.get('buyer'), url.searchParams.get('category'));
      if (path === '/api/intel/expiring') return await expiringContracts(db, {
        days: parseInt(url.searchParams.get('days') || '365'),
        minValue: parseFloat(url.searchParams.get('minValue') || '0'),
        buyer: url.searchParams.get('buyer'),
        category: url.searchParams.get('category'),
      });
      if (path === '/api/intel/pipeline') return await forwardPipeline(db, url.searchParams.get('buyer'));

      // Health check
      if (path === '/') return cors({ status: 'ok', service: 'pwin-competitive-intel' });

      return cors({ error: 'Not found' }, 404);
    } catch (err) {
      return cors({ error: err.message }, 500);
    }
  },
};
