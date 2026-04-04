/**
 * Seed ESN Lot 2 Test Data
 *
 * Loads realistic bid execution data that skills cannot extract from documents:
 * - 84-activity schedule with dates, owners, dependencies, critical path
 * - Team / resource data
 * - Win themes
 * - Governance gates
 * - Stakeholders
 * - Response items (assigned to sections)
 *
 * This data represents a mid-bid state: ITT received, strategy locked,
 * solution in progress, some production started. Deliberately includes
 * issues for the AI to find (overdue activities, resource conflicts,
 * missing assignments, unaddressed compliance gaps).
 *
 * Run: node test/skill-tests/seed-esn-data.js <pursuitId>
 *
 * Or import and call: seedESNData(pursuitId)
 */

import { apiGet, apiPut, setProductData, getProductData } from './test-helpers.js';

// Submission deadline: 31 Oct 2014 (from ITT)
// Assume ITT received: 8 Aug 2014 (publication date)
// Bid duration: ~12 weeks
const BID_START = '2014-08-11';
const SUBMISSION = '2014-10-31';

function d(offset) {
  // Days from bid start
  const date = new Date('2014-08-11');
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

async function seedESNData(pursuitId) {
  console.log(`\n  Seeding ESN Lot 2 test data for pursuit ${pursuitId}...\n`);

  const existing = await getProductData(pursuitId, 'bid-execution');

  // Keep extracted sections, framework, context — add everything else
  const bidData = { ...existing };

  // ═══════════════════════════════════════════════════════════════
  // ACTIVITY SCHEDULE — realistic 84-activity subset
  // Includes deliberate issues: overdue activities, missing dates,
  // resource conflicts, critical path pressure
  // ═══════════════════════════════════════════════════════════════

  bidData.activities = [
    // SAL — Sales & Capture (weeks 1-3)
    { activityCode: 'SAL-01', workstreamCode: 'SAL', description: 'Customer engagement & intelligence gathering', owner: 'Sarah Chen', status: 'completed', plannedStart: d(0), plannedEnd: d(10), actualStart: d(0), actualEnd: d(9), criticalPath: true, dependencies: [] },
    { activityCode: 'SAL-02', workstreamCode: 'SAL', description: 'Incumbent performance review (Airwave)', owner: 'Sarah Chen', status: 'completed', plannedStart: d(0), plannedEnd: d(7), actualStart: d(0), actualEnd: d(8), criticalPath: false, dependencies: [] },
    { activityCode: 'SAL-03', workstreamCode: 'SAL', description: 'Competitor analysis & positioning', owner: 'Mike Torres', status: 'completed', plannedStart: d(5), plannedEnd: d(15), actualStart: d(5), actualEnd: d(16), criticalPath: true, dependencies: ['SAL-01'] },
    { activityCode: 'SAL-04', workstreamCode: 'SAL', description: 'Win theme development & refinement', owner: 'Mike Torres', status: 'completed', plannedStart: d(10), plannedEnd: d(18), actualStart: d(11), actualEnd: d(19), criticalPath: true, dependencies: ['SAL-01', 'SAL-03'] },
    { activityCode: 'SAL-05', workstreamCode: 'SAL', description: 'Evaluation criteria mapping & scoring strategy', owner: 'Rachel Wong', status: 'completed', plannedStart: d(5), plannedEnd: d(12), actualStart: d(5), actualEnd: d(12), criticalPath: false, dependencies: ['SAL-04'] },
    { activityCode: 'SAL-06', workstreamCode: 'SAL', description: 'Capture plan finalisation & win strategy lock', owner: 'Sarah Chen', status: 'completed', plannedStart: d(15), plannedEnd: d(20), actualStart: d(16), actualEnd: d(21), criticalPath: true, dependencies: ['SAL-04', 'SAL-05', 'SAL-10'] },
    { activityCode: 'SAL-07', workstreamCode: 'SAL', description: 'Pre-submission clarification strategy', owner: 'Rachel Wong', status: 'in_progress', plannedStart: d(20), plannedEnd: d(35), criticalPath: false, dependencies: ['SAL-04'] },
    { activityCode: 'SAL-10', workstreamCode: 'SAL', description: 'Stakeholder relationship mapping & engagement', owner: 'Sarah Chen', status: 'completed', plannedStart: d(0), plannedEnd: d(15), actualStart: d(0), actualEnd: d(14), criticalPath: false, dependencies: ['SAL-01'] },

    // SOL — Solution Design (weeks 3-8) — DELIBERATELY BEHIND SCHEDULE
    { activityCode: 'SOL-01', workstreamCode: 'SOL', description: 'Requirements analysis & interpretation', owner: 'James Park', status: 'completed', plannedStart: d(14), plannedEnd: d(21), actualStart: d(16), actualEnd: d(24), criticalPath: true, dependencies: ['SAL-06'] },
    { activityCode: 'SOL-02', workstreamCode: 'SOL', description: 'Current operating model assessment (Airwave)', owner: 'James Park', status: 'completed', plannedStart: d(7), plannedEnd: d(14), actualStart: d(7), actualEnd: d(14), criticalPath: false, dependencies: [] },
    { activityCode: 'SOL-03', workstreamCode: 'SOL', description: 'Target operating model design', owner: 'James Park', status: 'in_progress', plannedStart: d(21), plannedEnd: d(42), criticalPath: true, dependencies: ['SOL-01', 'SOL-02'] },
    { activityCode: 'SOL-04', workstreamCode: 'SOL', description: 'Service delivery model design', owner: 'Lisa Chen', status: 'not_started', plannedStart: d(35), plannedEnd: d(49), criticalPath: true, dependencies: ['SOL-03'] },
    { activityCode: 'SOL-05', workstreamCode: 'SOL', description: 'Technology & digital approach', owner: 'David Kumar', status: 'in_progress', plannedStart: d(21), plannedEnd: d(42), criticalPath: false, dependencies: ['SOL-03'] },
    { activityCode: 'SOL-06', workstreamCode: 'SOL', description: 'Staffing model & TUPE analysis', owner: 'Lisa Chen', status: 'not_started', plannedStart: d(42), plannedEnd: d(52), criticalPath: false, dependencies: ['SOL-04'] },
    { activityCode: 'SOL-07', workstreamCode: 'SOL', description: 'Transition & mobilisation approach', owner: 'James Park', status: 'not_started', plannedStart: d(42), plannedEnd: d(56), criticalPath: true, dependencies: ['SOL-04', 'SOL-05', 'SOL-06'] },
    { activityCode: 'SOL-08', workstreamCode: 'SOL', description: 'Innovation & continuous improvement', owner: 'David Kumar', status: 'not_started', plannedStart: d(35), plannedEnd: d(45), criticalPath: false, dependencies: ['SOL-03'] },
    { activityCode: 'SOL-09', workstreamCode: 'SOL', description: 'Social value proposition', owner: 'Rachel Wong', status: 'not_started', plannedStart: d(35), plannedEnd: d(45), criticalPath: false, dependencies: ['SOL-04'] },
    { activityCode: 'SOL-10', workstreamCode: 'SOL', description: 'Evidence strategy & case study identification', owner: 'Rachel Wong', status: 'in_progress', plannedStart: d(14), plannedEnd: d(28), criticalPath: false, dependencies: ['SOL-04', 'SAL-05'] },
    { activityCode: 'SOL-11', workstreamCode: 'SOL', description: 'Solution design lock', owner: 'James Park', status: 'not_started', plannedStart: d(52), plannedEnd: d(56), criticalPath: true, dependencies: ['SOL-03', 'SOL-04', 'SOL-05', 'SOL-06', 'SOL-07', 'SOL-08', 'SOL-09', 'SOL-10'] },
    { activityCode: 'SOL-12', workstreamCode: 'SOL', description: 'Solution risk identification & analysis', owner: 'James Park', status: 'not_started', plannedStart: d(42), plannedEnd: d(49), criticalPath: false, dependencies: ['SOL-03', 'SOL-04'] },

    // COM — Commercial (weeks 5-10)
    { activityCode: 'COM-01', workstreamCode: 'COM', description: 'Should-cost model development', owner: 'Tom Richards', status: 'not_started', plannedStart: d(35), plannedEnd: d(49), criticalPath: true, dependencies: ['SOL-04', 'SOL-06'] },
    { activityCode: 'COM-02', workstreamCode: 'COM', description: 'Price-to-win analysis', owner: 'Tom Richards', status: 'not_started', plannedStart: d(42), plannedEnd: d(49), criticalPath: false, dependencies: ['SAL-03', 'COM-01'] },
    { activityCode: 'COM-04', workstreamCode: 'COM', description: 'Commercial model & payment mechanisms', owner: 'Tom Richards', status: 'not_started', plannedStart: d(42), plannedEnd: d(52), criticalPath: false, dependencies: ['SOL-04'] },
    { activityCode: 'COM-05', workstreamCode: 'COM', description: 'Margin structure & sensitivity analysis', owner: 'Tom Richards', status: 'not_started', plannedStart: d(49), plannedEnd: d(56), criticalPath: false, dependencies: ['COM-01'] },
    { activityCode: 'COM-06', workstreamCode: 'COM', description: 'Pricing model finalisation', owner: 'Tom Richards', status: 'not_started', plannedStart: d(56), plannedEnd: d(63), criticalPath: true, dependencies: ['COM-01', 'COM-02', 'COM-04', 'COM-05'] },
    { activityCode: 'COM-07', workstreamCode: 'COM', description: 'Commercial risk identification', owner: 'Tom Richards', status: 'not_started', plannedStart: d(49), plannedEnd: d(56), criticalPath: false, dependencies: ['COM-01', 'COM-04'] },

    // BM — Bid Management (continuous)
    { activityCode: 'BM-01', workstreamCode: 'BM', description: 'Kickoff planning & execution', owner: 'Rachel Wong', status: 'completed', plannedStart: d(0), plannedEnd: d(3), actualStart: d(0), actualEnd: d(3), criticalPath: false, dependencies: [] },
    { activityCode: 'BM-02', workstreamCode: 'BM', description: 'Bid management plan production', owner: 'Rachel Wong', status: 'completed', plannedStart: d(3), plannedEnd: d(7), actualStart: d(3), actualEnd: d(8), criticalPath: false, dependencies: ['BM-01'] },
    { activityCode: 'BM-07', workstreamCode: 'BM', description: 'Quality management approach', owner: 'Rachel Wong', status: 'completed', plannedStart: d(5), plannedEnd: d(10), actualStart: d(5), actualEnd: d(10), criticalPath: false, dependencies: ['SAL-05', 'BM-01'] },
    // DELIBERATELY OVERDUE — storyboard not started despite strategy being locked
    { activityCode: 'BM-10', workstreamCode: 'BM', description: 'Storyboard development & sign-off', owner: 'Rachel Wong', status: 'not_started', plannedStart: d(21), plannedEnd: d(35), criticalPath: true, dependencies: ['SAL-06', 'SAL-05', 'SOL-11'] },
    { activityCode: 'BM-13', workstreamCode: 'BM', description: 'Bid risk & assumptions register', owner: 'Rachel Wong', status: 'in_progress', plannedStart: d(0), plannedEnd: d(77), criticalPath: false, dependencies: [] },
    { activityCode: 'BM-16', workstreamCode: 'BM', description: 'Win strategy refresh (post-ITT)', owner: 'Sarah Chen', status: 'not_started', plannedStart: d(14), plannedEnd: d(21), criticalPath: false, dependencies: ['BM-01', 'SOL-01'] },

    // GOV — Governance Gates
    { activityCode: 'GOV-01', workstreamCode: 'GOV', description: 'Pursuit approval', owner: 'Director', status: 'completed', plannedStart: d(18), plannedEnd: d(21), actualStart: d(19), actualEnd: d(22), criticalPath: false, dependencies: ['SAL-06'] },
    { activityCode: 'GOV-02', workstreamCode: 'GOV', description: 'Solution & strategy review', owner: 'Director', status: 'not_started', plannedStart: d(52), plannedEnd: d(56), criticalPath: true, dependencies: ['SAL-06', 'SOL-03'] },
    { activityCode: 'GOV-03', workstreamCode: 'GOV', description: 'Pricing & risk review', owner: 'CFO', status: 'not_started', plannedStart: d(63), plannedEnd: d(66), criticalPath: true, dependencies: ['COM-06'] },
    { activityCode: 'GOV-04', workstreamCode: 'GOV', description: 'Executive approval', owner: 'CEO', status: 'not_started', plannedStart: d(70), plannedEnd: d(73), criticalPath: true, dependencies: ['GOV-03'] },
    { activityCode: 'GOV-05', workstreamCode: 'GOV', description: 'Final submission authority', owner: 'CEO', status: 'not_started', plannedStart: d(77), plannedEnd: d(78), criticalPath: true, dependencies: ['GOV-04'] },

    // PRD — Production (weeks 6-11) — BLOCKED by BM-10 storyboard
    { activityCode: 'PRD-01', workstreamCode: 'PRD', description: 'Compliance matrix & requirements mapping', owner: 'Rachel Wong', status: 'in_progress', plannedStart: d(14), plannedEnd: d(28), criticalPath: false, dependencies: ['SOL-01'] },
    { activityCode: 'PRD-02', workstreamCode: 'PRD', description: 'Section drafting & content assembly', owner: 'Multiple', status: 'not_started', plannedStart: d(42), plannedEnd: d(70), criticalPath: true, dependencies: ['BM-10', 'SOL-11'] },
    { activityCode: 'PRD-03', workstreamCode: 'PRD', description: 'Evidence, case studies & CV assembly', owner: 'Rachel Wong', status: 'not_started', plannedStart: d(35), plannedEnd: d(56), criticalPath: false, dependencies: ['SOL-10'] },
    { activityCode: 'PRD-04', workstreamCode: 'PRD', description: 'Pricing schedules & commercial response', owner: 'Tom Richards', status: 'not_started', plannedStart: d(63), plannedEnd: d(70), criticalPath: true, dependencies: ['COM-06'] },
    { activityCode: 'PRD-05', workstreamCode: 'PRD', description: 'Pink review (storyboard/outline)', owner: 'Reviewers', status: 'not_started', plannedStart: d(38), plannedEnd: d(42), criticalPath: true, dependencies: ['BM-10'] },
    { activityCode: 'PRD-06', workstreamCode: 'PRD', description: 'Red review (full draft)', owner: 'Reviewers', status: 'not_started', plannedStart: d(63), plannedEnd: d(66), criticalPath: true, dependencies: ['PRD-02', 'PRD-03', 'PRD-04'] },
    { activityCode: 'PRD-07', workstreamCode: 'PRD', description: 'Gold review (final/executive)', owner: 'Director', status: 'not_started', plannedStart: d(70), plannedEnd: d(73), criticalPath: true, dependencies: ['PRD-06', 'COM-06'] },
    { activityCode: 'PRD-08', workstreamCode: 'PRD', description: 'Final QA & formatting', owner: 'Rachel Wong', status: 'not_started', plannedStart: d(73), plannedEnd: d(77), criticalPath: true, dependencies: ['PRD-07'] },
    { activityCode: 'PRD-09', workstreamCode: 'PRD', description: 'Submission packaging & upload', owner: 'Rachel Wong', status: 'not_started', plannedStart: d(77), plannedEnd: d(79), criticalPath: true, dependencies: ['PRD-08', 'GOV-05'] },

    // DEL — Delivery Planning
    { activityCode: 'DEL-01', workstreamCode: 'DEL', description: 'Delivery risk & assumptions register', owner: 'James Park', status: 'in_progress', plannedStart: d(21), plannedEnd: d(63), criticalPath: false, dependencies: ['SOL-03', 'SOL-04'] },

    // LEG — Legal
    { activityCode: 'LEG-01', workstreamCode: 'LEG', description: 'Contract review & markup', owner: 'Legal', status: 'in_progress', plannedStart: d(7), plannedEnd: d(35), criticalPath: false, dependencies: [] },
    { activityCode: 'LEG-04', workstreamCode: 'LEG', description: 'TUPE obligations assessment', owner: 'Legal', status: 'not_started', plannedStart: d(35), plannedEnd: d(49), criticalPath: false, dependencies: ['SOL-06'] },
    { activityCode: 'LEG-05', workstreamCode: 'LEG', description: 'Data protection & security review', owner: 'Legal', status: 'not_started', plannedStart: d(28), plannedEnd: d(42), criticalPath: false, dependencies: ['SOL-05'] },
  ];

  // ═══════════════════════════════════════════════════════════════
  // TEAM
  // ═══════════════════════════════════════════════════════════════

  bidData.team = [
    { name: 'Sarah Chen', role: 'Capture Lead / Bid Director', allocation: 80 },
    { name: 'Rachel Wong', role: 'Bid Manager', allocation: 100 },
    { name: 'James Park', role: 'Solution Architect', allocation: 100 },
    { name: 'Lisa Chen', role: 'Service Design Lead', allocation: 60 },
    { name: 'David Kumar', role: 'Technology Architect', allocation: 60 },
    { name: 'Mike Torres', role: 'Strategy & Competitive Lead', allocation: 40 },
    { name: 'Tom Richards', role: 'Commercial Lead', allocation: 60 },
  ];

  // ═══════════════════════════════════════════════════════════════
  // WIN THEMES
  // ═══════════════════════════════════════════════════════════════

  bidData.winThemes = [
    { id: 'WT-01', statement: 'Proven emergency services digital transformation at national scale', rationale: 'Only bidder with live 4G public safety deployment in UK policing', status: 'confirmed', evidenceStatus: 'substantiated' },
    { id: 'WT-02', statement: 'Zero-disruption transition from Airwave with dual-running assurance', rationale: 'Airwave replacement is highest risk — client needs confidence in continuity', status: 'confirmed', evidenceStatus: 'partial' },
    { id: 'WT-03', statement: 'Service management excellence with 99.999% availability track record', rationale: 'Public safety demands highest availability — incumbent Airwave standard', status: 'draft', evidenceStatus: 'unsubstantiated' },
    { id: 'WT-04', statement: 'Innovation roadmap: leveraging LTE for next-gen operational applications', rationale: 'ESN is not just voice replacement — it enables data-driven policing', status: 'draft', evidenceStatus: 'unsubstantiated' },
  ];

  // ═══════════════════════════════════════════════════════════════
  // GOVERNANCE GATES
  // ═══════════════════════════════════════════════════════════════

  bidData.gates = [
    { id: 'G1', name: 'Pursuit Approval', plannedDate: d(21), status: 'passed', decision: 'approved' },
    { id: 'G2', name: 'Solution & Strategy Review', plannedDate: d(56), status: 'scheduled', decision: null },
    { id: 'G3', name: 'Pricing & Risk Review', plannedDate: d(66), status: 'scheduled', decision: null },
    { id: 'G4', name: 'Executive Approval', plannedDate: d(73), status: 'not_scheduled', decision: null },
    { id: 'G5', name: 'Final Submission Authority', plannedDate: d(78), status: 'not_scheduled', decision: null },
  ];

  // ═══════════════════════════════════════════════════════════════
  // STAKEHOLDERS
  // ═══════════════════════════════════════════════════════════════

  bidData.stakeholders = [
    { name: 'Stephen Webb', role: 'SRO — ESMCP Programme', influenceLevel: 'decision_maker', disposition: 'neutral', bipRelationshipOwner: 'Sarah Chen', lastContactDate: '2014-07-15', confidence: 'M' },
    { name: 'Commercial Director', role: 'Head of Commercial — Home Office', influenceLevel: 'decision_maker', disposition: 'unknown', bipRelationshipOwner: null, lastContactDate: null, confidence: 'U' },
    { name: 'PICT Representative', role: 'Police ICT Company Board', influenceLevel: 'influencer', disposition: 'supportive', bipRelationshipOwner: 'Sarah Chen', lastContactDate: '2014-08-01', confidence: 'H' },
    { name: 'Technical Evaluation Lead', role: 'Authority Technical Evaluator', influenceLevel: 'evaluator', disposition: 'unknown', bipRelationshipOwner: null, lastContactDate: null, confidence: 'U' },
    { name: 'Fire & Rescue Representative', role: 'CFOA / FRS User Representative', influenceLevel: 'influencer', disposition: 'neutral', bipRelationshipOwner: 'Mike Torres', lastContactDate: '2014-06-20', confidence: 'L' },
  ];

  // ═══════════════════════════════════════════════════════════════
  // RESPONSE ITEMS (assign owners to extracted sections)
  // Leave some deliberately unassigned to test coverage gaps
  // ═══════════════════════════════════════════════════════════════

  const sections = bidData.responseSections || [];
  bidData.responseItems = [];

  // Assign owners to the top scored sections only — leave lower-weight ones unassigned
  const assignments = {
    'Public Safety': { owner: 'David Kumar', status: 'not_started' },
    'Service Management': { owner: 'James Park', status: 'not_started' },
    'System Integration': { owner: 'David Kumar', status: 'not_started' },
    'Network and IT': { owner: 'David Kumar', status: 'not_started' },
    'User Device': { owner: 'James Park', status: 'not_started' },
    'Implementation': { owner: 'James Park', status: 'not_started' },
    'Schedule 7.1': { owner: 'Tom Richards', status: 'not_started' },
  };

  for (const section of sections) {
    const ref = section.reference || '';
    let assigned = null;
    for (const [key, val] of Object.entries(assignments)) {
      if (ref.includes(key)) { assigned = val; break; }
    }

    if (assigned) {
      bidData.responseItems.push({
        id: `ri-${section.id}`,
        reference: ref,
        linkedResponseSectionId: section.id,
        owner: assigned.owner,
        status: assigned.status,
        dueDate: null,
      });
    }
    // Deliberately leave Customer Support, Security, Quality Plan, Testing,
    // Exit, BCDR, Collaboration, Personnel, Termination UNASSIGNED
  }

  // Save
  await setProductData(pursuitId, 'bid-execution', bidData);

  const stats = {
    activities: bidData.activities.length,
    team: bidData.team.length,
    winThemes: bidData.winThemes.length,
    gates: bidData.gates.length,
    stakeholders: bidData.stakeholders.length,
    responseItems: bidData.responseItems.length,
    unassignedSections: sections.length - bidData.responseItems.length,
  };

  console.log(`  Seeded:`);
  console.log(`    Activities: ${stats.activities} (${bidData.activities.filter(a => a.status === 'completed').length} completed, ${bidData.activities.filter(a => a.status === 'in_progress').length} in progress, ${bidData.activities.filter(a => a.status === 'not_started').length} not started)`);
  console.log(`    Team: ${stats.team} members`);
  console.log(`    Win themes: ${stats.winThemes} (${bidData.winThemes.filter(t => t.status === 'confirmed').length} confirmed, ${bidData.winThemes.filter(t => t.status === 'draft').length} draft)`);
  console.log(`    Gates: ${stats.gates} (${bidData.gates.filter(g => g.status === 'passed').length} passed, ${bidData.gates.filter(g => g.status === 'scheduled').length} scheduled)`);
  console.log(`    Stakeholders: ${stats.stakeholders}`);
  console.log(`    Response items: ${stats.responseItems} assigned / ${stats.unassignedSections} unassigned`);
  console.log(`    Deliberate issues: overdue BM-10 storyboard, resource conflict James Park (SOL-03 + SOL-11), unassigned low-weight sections`);

  return stats;
}

// CLI usage
if (process.argv[2]) {
  seedESNData(process.argv[2]).then(() => console.log('\n  Done.\n'));
}

export { seedESNData };
