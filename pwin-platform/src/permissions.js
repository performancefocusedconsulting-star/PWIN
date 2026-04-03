/**
 * PWIN Platform — Field-Level Permission Enforcement
 *
 * Claude never writes to bid manager-owned fields.
 * Enforced at the MCP server layer, not as a prompt convention.
 */

const OWNERSHIP = {
  // Activity entity
  'Activity.owner':           'bid_manager',
  'Activity.status':          'bid_manager',
  'Activity.plannedStart':    'bid_manager',
  'Activity.plannedEnd':      'bid_manager',
  'Activity.actualStart':     'bid_manager',
  'Activity.actualEnd':       'bid_manager',
  'Activity.notes':           'bid_manager',
  'Activity.dependencies':    'bid_manager',
  'Activity.outputAssurance': 'bid_manager',
  'Activity.forecastEnd':     'ai',

  // ActivityAIInsight — entirely AI-owned
  'ActivityAIInsight.*':      'ai',

  // ResponseItem entity
  'ResponseItem.status':                     'bid_manager',
  'ResponseItem.qualityAnswersQuestion':     'bid_manager',
  'ResponseItem.qualityFollowsStructure':    'bid_manager',
  'ResponseItem.qualityScoreSelfAssessment': 'bid_manager',
  'ResponseItem.qualityScoreRationale':      'bid_manager',
  'ResponseItem.qualityScoreGap':            'bid_manager',
  'ResponseItem.qualityCredentials':         'bid_manager',
  'ResponseItem.qualityCredentialsRefs':     'bid_manager',
  'ResponseItem.qualityWinThemeAssessments': 'bid_manager',
  'ResponseItem.qualityComplianceMapping':   'bid_manager',
  'ResponseItem.owner':                      'bid_manager',
  'ResponseItem.dueDate':                    'bid_manager',
  'ResponseItem.notes':                      'bid_manager',
  'ResponseItem.effortAllocationEfficiency': 'ai',

  // ResponseItemAIInsight — entirely AI-owned
  'ResponseItemAIInsight.*': 'ai',

  // ResponseSection entity
  'ResponseSection.questionText':          'bid_manager',
  'ResponseSection.evaluationCriteria':    'bid_manager',
  'ResponseSection.evaluationMaxScore':    'bid_manager',
  'ResponseSection.hurdleScore':           'bid_manager',
  'ResponseSection.wordLimit':             'bid_manager',
  'ResponseSection.winThemeCoverageScore': 'ai',
  'ResponseSection.lastAmended':           'ai',

  // Ingested entities — AI creates, bid manager can edit after
  'ResponseSection.createdBy':   'system',
  'EvaluationFramework.*':       'ai_ingestion',
  'ITTDocument.*':               'ai_ingestion',

  // GovernanceGate entity
  'GovernanceGate.decision':      'bid_manager',
  'GovernanceGate.conditions':    'bid_manager',
  'GovernanceGate.riskPremiumPct':'bid_manager',
  'GateReadinessAIInsight.*':     'ai',

  // WinTheme entity
  'WinTheme.statement':                  'bid_manager',
  'WinTheme.rationale':                  'bid_manager',
  'WinTheme.status':                     'bid_manager',
  'WinTheme.portfolioSaturationRating':  'ai',

  // StandupAction entity
  'StandupAction.owner':                  'bid_manager',
  'StandupAction.dueDate':                'bid_manager',
  'StandupAction.status':                 'bid_manager',
  'StandupAction.deferred_count':         'ai',
  'StandupAction.escalation_recommended': 'ai',
  'StandupAction.recommended_decision':   'ai',

  // ComplianceRequirement entity
  'ComplianceRequirement.complianceStatus':       'bid_manager',
  'ComplianceRequirement.complianceExplanation':   'bid_manager',
  'ComplianceRequirement.solutionAlignment':       'bid_manager',
  'ComplianceRequirement.impactedByClarification': 'ai',

  // Engagement, TeamMember — entirely bid manager
  'Engagement.*':  'bid_manager',
  'TeamMember.*':  'bid_manager',

  // AI insight entities — entirely AI-owned
  'BidAIInsight.*':                 'ai',
  'ComplianceCoverageAIInsight.*':  'ai',
  'EffortAllocationAIInsight.*':    'ai',
  'TeamMemberAIInsight.*':          'ai',
};

/**
 * Validate that an AI write does not touch bid manager-owned fields.
 * Throws with a clear error message if permission is denied.
 */
function validateAIWrite(entity, fields) {
  const violations = [];
  for (const field of Object.keys(fields)) {
    const key = `${entity}.${field}`;
    const wildcardKey = `${entity}.*`;
    const owner = OWNERSHIP[key] || OWNERSHIP[wildcardKey];
    if (owner === 'bid_manager') {
      violations.push(key);
    }
  }
  if (violations.length > 0) {
    const err = new Error(
      `PERMISSION_DENIED: AI cannot write to bid_manager-owned fields: ${violations.join(', ')}`
    );
    err.code = 'PERMISSION_DENIED';
    err.fields = violations;
    throw err;
  }
}

export { OWNERSHIP, validateAIWrite };
