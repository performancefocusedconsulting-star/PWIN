# Buyer Intelligence Dossier — Output Schema v3.0

This reference defines the complete JSON output schema, field rules, and
archetype taxonomy. Read this file when constructing the dossier JSON.

## What changed in v3.0 (vs v2.2)

Three new top-level sections, five existing sections enriched, no sections
removed or restructured.

**New sections:**
- `procurementBehaviourSnapshot` — pinned snapshot of the buyer-behaviour-profile
  signals (cancellation rate vs peers, notice-to-award timing, distressed-
  incumbent flag, competition intensity). Self-contains the dossier so consumers
  do not need a live API call to read it.
- `actionRegister` — owned, prioritised list of intelligence gaps with
  recommended next step and downstream-decision impact. Turns the dossier from
  a passive report into a living capture artefact.
- `pursuitImplications` — the seventh intelligence lens. Buyer-derived,
  bidder-neutral implications. What any pursuit against this buyer should do
  or avoid because of who this buyer is.

**Enriched sections:**
- `commissioningContextHypotheses` — adds `spendClassification` (mandatory /
  discretionary / reactive / strategic).
- `decisionUnitAssumptions` — adds `perRoleInterests`, `internalTensions`,
  `dominantDecisionLens`. Names the cast and what each one cares about.
- `cultureAndPreferences` — adds `languageAndFraming`. The terms the buyer uses
  and rejects.
- `commercialAndRiskPosture` — adds `preferredCommercialModels` and
  `paymentTermsNorms`.
- `supplierEcosystem` — adds `vulnerabilitySignals` per incumbent and a
  top-level `barriersToEntry`.

Migration: existing v2.2 dossiers stay readable. New sections show up empty
until the next refresh re-derives them from existing sources or new ones.

---

## Table of Contents

1. [The seven intelligence lenses](#the-seven-intelligence-lenses)
2. [Full schema structure](#full-schema-structure)
3. [Organisational archetype taxonomy](#organisational-archetype-taxonomy)
4. [Schema rules](#schema-rules)
5. [Organisation type enum](#organisation-type-enum)
6. [Buying readiness enum](#buying-readiness-enum)
7. [Spend classification enum](#spend-classification-enum)
8. [Dominant decision lens enum](#dominant-decision-lens-enum)
9. [Change maturity sub-fields](#change-maturity-sub-fields)
10. [Action register field reference](#action-register-field-reference)
11. [Pursuit implications field reference](#pursuit-implications-field-reference)
12. [Linked assets structure](#linked-assets-structure)

---

## The seven intelligence lenses

The dossier organises buyer intelligence around seven lenses. Every extracted
fact contributes to at least one. Most dossier sections map to a single
primary lens; some span two.

| Lens | What it captures | Primary dossier sections |
|---|---|---|
| **Mandate** | What the buyer exists to deliver — statutory role, services, missions | `buyerSnapshot`, `organisationContext` |
| **Pressure** | What is forcing action now — fiscal, political, regulatory, audit, leadership | `strategicPriorities`, `commissioningContextHypotheses` (drivers, pressures), `risksAndSensitivities` |
| **Money** | What is funded, constrained, or exposed — budget envelope, conditions, savings targets | `commercialAndRiskPosture` (affordability), `commissioningContextHypotheses` (spendClassification, approvalsPending), `procurementBehaviour` (totalValue) |
| **Buying behaviour** | How they actually procure — routes, frameworks, weighting, retention vs switching | `procurementBehaviour`, `procurementBehaviourSnapshot`, `decisionUnitAssumptions` |
| **Risk posture** | What they are trying to avoid — audit-driven concerns, public sensitivities, contractual cautions | `cultureAndPreferences` (riskTolerance), `commercialAndRiskPosture`, `risksAndSensitivities` |
| **Supplier landscape** | Who is embedded, who is vulnerable | `supplierEcosystem`, `relationshipHistory` (Tier 4) |
| **Pursuit implications** | What any pursuit against this buyer should do or avoid because of who this buyer is | `pursuitImplications` (the seventh lens — buyer-derived, bidder-neutral) |

Lenses are not stored as a parallel structure in the dossier — they are the
*organising principle*. Extraction templates declare which lens(es) each
extracted fact contributes to, and that determines where the fact lands in
the dossier.

---

## Full schema structure

Produce a single JSON object with these top-level keys:

```json
{
  "meta": {
    "buyerName": "string",
    "slug": "string — kebab-case identifier",
    "sector": "string",
    "generatedAt": "ISO 8601 datetime",
    "generatedBy": "Agent 2 Skill 2 v3.0",
    "version": "3.0 on first build; increment on refresh",
    "depthMode": "snapshot | standard | deep | snapshot-data-insufficient | <mode>-partial",
    "taxonomyVersion": "2.0",
    "sourcesSummary": "string — e.g. '12 sources, 6 web searches, 3 extraction templates applied'",
    "refreshDue": "ISO 8601 date — 6 months from today or next reporting milestone",
    "refreshTriggers": [
      "new procurement in category",
      "leadership change",
      "annual report publication",
      "strategy refresh",
      "major controversy or audit event",
      "pursuit launched against this buyer"
    ],
    "versionLog": [{ "version": "string", "date": "ISO 8601", "mode": "build | refresh | inject | amend", "summary": "string" }],
    "prerequisitesPresentAt": {
      "version": "string — version this snapshot was taken at",
      "date": "ISO 8601 date",
      "required": {
        "buyerName": "boolean"
      },
      "preferred": {
        "ftsData": "boolean",
        "behaviourProfile": "boolean",
        "sectorBrief": "boolean"
      }
    },
    "extractionTemplatesApplied": [
      {
        "documentType": "string — e.g. 'digital_strategy', 'annual_report', 'nao_pac_report'",
        "sourceId": "string — SRC-nnn the template was applied to",
        "appliedAt": "ISO 8601",
        "lensesContributed": ["mandate | pressure | money | buying-behaviour | risk-posture | supplier-landscape | pursuit-implications"]
      }
    ],
    "degradedReason": "string or null — only set in degraded/partial mode"
  },

  "buyerSnapshot": {
    "legalName": "string",
    "parentBody": "string or null",
    "organisationType": "enum — see Organisation type enum below",
    "sector": "string",
    "subSector": "string or null",
    "geographicRemit": "string",
    "headcount": "number or null",
    "annualBudget": "string or null",
    "organisationalArchetype": {
      "value": "enum — see Archetype taxonomy below",
      "type": "inference",
      "confidence": "high | medium | low",
      "rationale": "string — explain the evidence chain",
      "sourceRefs": ["SRC-001"]
    },
    "executiveSummary": {
      "headline": "string — one-sentence decision-grade summary",
      "narrative": "string — 2-3 paragraph overview"
    },
    "keyRisks": ["string — top 3-5 risks for any pursuit against this buyer"]
  },

  "organisationContext": {
    "sectionConfidence": "high | medium | low | none",
    "mandate": "evidenced field",
    "operatingModel": "evidenced field",
    "organisationStructure": "evidenced field",
    "keyBusinessUnits": ["string or evidenced field"],
    "seniorLeadership": [{ "name": "string", "role": "string", "since": "string or null", "background": "string or null" }],
    "fundingModel": "evidenced field",
    "recentChanges": "evidenced field — include predecessor/successor bodies, MoG changes"
  },

  "strategicPriorities": {
    "sectionConfidence": "high | medium | low | none",
    "summaryNarrative": "string",
    "publishedStrategyThemes": ["evidenced field"],
    "majorProgrammes": [
      {
        "name": "string",
        "status": "string",
        "value": "string or null",
        "sro": "string or null",
        "timeline": "string or null",
        "quantifiedTargets": [
          {
            "metric": "string — fiscal-savings | fte-displacement | productivity | transaction-time | customer-satisfaction | error-rate | digital-adoption | other",
            "value": "string — exact figure as stated",
            "baseline": "string or null",
            "byWhen": "string or null",
            "stretchOrCommitted": "committed | stretch | aspirational | unclear"
          }
        ],
        "dependencies": ["string"],
        "sourceRefs": ["SRC-nnn"]
      }
    ],
    "regulatoryPressures": ["evidenced field"],
    "politicalPressures": ["evidenced field"],
    "fiscalPressures": ["evidenced field"],
    "servicePerformancePressures": ["evidenced field"],
    "publicStatementsOfIntent": ["evidenced field"]
  },

  "commissioningContextHypotheses": {
    "sectionConfidence": "high | medium | low | none",
    "sectionCaveat": "These are hypotheses derived from available evidence. They require validation by the pursuit team.",
    "driversOfExternalBuying": ["evidenced field — type must be inference"],
    "pressuresShapingSpend": ["evidenced field — type must be inference"],
    "operationalPainPoints": ["evidenced field — type must be inference"],
    "outcomesSought": ["evidenced field — type must be inference"],
    "consequencesOfInaction": ["evidenced field — type must be inference"],
    "commissioningCycleStage": "evidenced field — type must be inference",
    "approvalsPending": "evidenced field — type must be inference",
    "marketEngagementLikelihood": "evidenced field — type must be inference",
    "buyingReadiness": "evidenced field — enum value, type must be inference",
    "spendClassification": "evidenced field — enum value (mandatory | discretionary | reactive | strategic | mixed | unknown), type must be inference",
    "timelineRisks": ["evidenced field — type must be inference"]
  },

  "procurementBehaviour": {
    "sectionConfidence": "high | medium | low | none",
    "summaryNarrative": "string",
    "totalAwards": "number",
    "totalValue": "string — e.g. '£142m'",
    "dataWindow": "string — e.g. '2020-2026'",
    "preferredRoutes": ["string — e.g. 'CCS framework call-off', 'open procedure'"],
    "frameworkUsage": ["string — framework names and lot references"],
    "sharedServiceArrangements": "string or null — e.g. 'Procures IT through NHS SBS; professional services direct'",
    "typicalContractLength": "string — e.g. '3+1+1 years'",
    "typicalContractValue": "string — e.g. '£2m-£10m'",
    "categoryConcentration": "evidenced field",
    "innovationVsProven": "evidenced field",
    "priceVsQualityBias": "evidenced field",
    "renewalPatterns": "evidenced field"
  },

  "procurementBehaviourSnapshot": {
    "snapshotTakenAt": "ISO 8601",
    "snapshotSourcedFrom": "get_buyer_behaviour_profile MCP tool | manual | unavailable",
    "yearsCovered": "number — typically 5",
    "volumeTrend": "growing | stable | shrinking | unknown",
    "outcomeMix": {
      "awarded": "number or null",
      "cancelled": "number or null",
      "nonCompliant": "number or null",
      "dormant": "number or null",
      "live": "number or null"
    },
    "cancellationRateVsPeers": "above-peer-average | at-peer-average | below-peer-average | unknown",
    "cancellationRatePercentage": "number or null",
    "noticeToAwardDays": {
      "median": "number or null",
      "p25": "number or null",
      "p75": "number or null"
    },
    "competitionIntensity": "high | medium | low | unknown",
    "averageBidsPerTender": "number or null",
    "distressedIncumbentFlag": "boolean",
    "distressedIncumbentEvidence": "string or null",
    "topCategoriesByOutcome": [
      {
        "category": "string",
        "awarded": "number",
        "cancelled": "number"
      }
    ],
    "consultantSummarySentence": "string — one-line takeaway a capture lead can lift directly, e.g. 'HMRC cancels at 1.7x the central-government median and takes 28% longer than peers from notice to award — plan for slip and verify funding state before bid commit.'"
  },

  "decisionUnitAssumptions": {
    "sectionConfidence": "high | medium | low | none",
    "sectionCaveat": "Inferred from published structures and procurement patterns. Requires pursuit-team validation.",
    "businessOwnerRoles": ["evidenced field — type must be inference"],
    "commercialRoles": ["evidenced field — type must be inference"],
    "technicalStakeholders": ["evidenced field — type must be inference"],
    "financeAssuranceRoles": ["evidenced field — type must be inference"],
    "evaluatorGroups": ["evidenced field — type must be inference"],
    "perRoleInterests": {
      "businessOwner": {
        "primaryInterest": "string — what this role optimises for",
        "secondaryInterest": "string or null",
        "evidenceBasis": "string — what published signal supports this",
        "type": "inference",
        "confidence": "high | medium | low",
        "rationale": "string",
        "sourceRefs": ["SRC-nnn"]
      },
      "commercial": {
        "primaryInterest": "string",
        "secondaryInterest": "string or null",
        "evidenceBasis": "string",
        "type": "inference",
        "confidence": "high | medium | low",
        "rationale": "string",
        "sourceRefs": ["SRC-nnn"]
      },
      "technical": {
        "primaryInterest": "string",
        "secondaryInterest": "string or null",
        "evidenceBasis": "string",
        "type": "inference",
        "confidence": "high | medium | low",
        "rationale": "string",
        "sourceRefs": ["SRC-nnn"]
      },
      "finance": {
        "primaryInterest": "string",
        "secondaryInterest": "string or null",
        "evidenceBasis": "string",
        "type": "inference",
        "confidence": "high | medium | low",
        "rationale": "string",
        "sourceRefs": ["SRC-nnn"]
      },
      "evaluators": {
        "primaryInterest": "string",
        "secondaryInterest": "string or null",
        "evidenceBasis": "string",
        "type": "inference",
        "confidence": "high | medium | low",
        "rationale": "string",
        "sourceRefs": ["SRC-nnn"]
      }
    },
    "internalTensions": [
      {
        "tension": "string — e.g. 'commercial wants framework speed; technical wants bespoke fit'",
        "between": ["business-owner | commercial | technical | finance | evaluators"],
        "evidenceBasis": "string",
        "type": "inference",
        "confidence": "high | medium | low",
        "rationale": "string",
        "sourceRefs": ["SRC-nnn"]
      }
    ],
    "dominantDecisionLens": {
      "value": "commercial | operational | political | technical | financial | mixed | unknown",
      "type": "inference",
      "confidence": "high | medium | low",
      "rationale": "string — name the signals (e.g. last 5 procurements were lowest-price-compliant → commercial lens)",
      "sourceRefs": ["SRC-nnn"]
    },
    "intelligenceGaps": ["string"]
  },

  "cultureAndPreferences": {
    "sectionConfidence": "high | medium | low | none",
    "decisionMakingFormality": "evidenced field",
    "governanceIntensity": "evidenced field",
    "riskTolerance": "evidenced field",
    "evidencePreferences": "evidenced field",
    "supplierInteractionStyle": "evidenced field",
    "presentationStyle": "evidenced field",
    "socialValueAndESG": "evidenced field — PPN 06/20 approach, net zero commitments, SME spend targets, community benefit expectations",
    "changeMaturity": "object — see Change maturity sub-fields below",
    "languageAndFraming": {
      "preferredTerminology": ["string — terms the buyer uses repeatedly"],
      "policyFrames": ["string — policy framings the buyer leans on, e.g. 'value for money', 'levelling up', 'AI-enabled', 'mission-led'"],
      "avoidLanguage": ["string — terms or framings the buyer rejects, ignores, or has been criticised for"],
      "evidenceBasis": "string — strategy doc, ministerial statement, procurement language, etc.",
      "type": "fact | inference",
      "confidence": "high | medium | low",
      "rationale": "string",
      "sourceRefs": ["SRC-nnn"]
    }
  },

  "commercialAndRiskPosture": {
    "sectionConfidence": "high | medium | low | none",
    "affordabilitySensitivity": "evidenced field",
    "riskTransferPosture": "evidenced field",
    "contractualCaution": "evidenced field",
    "cyberDataSensitivity": "evidenced field",
    "mobilisationSensitivity": "evidenced field",
    "auditFoiExposure": "evidenced field",
    "securityClearanceRequirements": "evidenced field — SC/DV/BPSS obligations, relevant for Defence, Justice, and intelligence-community buyers",
    "preferredCommercialModels": {
      "value": ["string — e.g. 'fixed price', 'time-and-materials', 'outcome-based', 'capped T&M', 'gainshare', 'milestone-based'"],
      "type": "fact | inference",
      "confidence": "high | medium | low",
      "rationale": "string — name the awards/contracts that show this",
      "sourceRefs": ["SRC-nnn"]
    },
    "paymentTermsNorms": {
      "value": "string — e.g. '30-day payment, milestone-based, retentions on 5% pending acceptance'",
      "type": "fact | inference",
      "confidence": "high | medium | low",
      "rationale": "string",
      "sourceRefs": ["SRC-nnn"]
    }
  },

  "supplierEcosystem": {
    "sectionConfidence": "high | medium | low | none",
    "summaryNarrative": "string",
    "incumbents": [
      {
        "supplierName": "string",
        "serviceLines": ["string — from 13-category taxonomy"],
        "contractCount": "number",
        "totalValue": "string",
        "longestRelationship": "string — e.g. 'since 2018'",
        "strategicImportance": "critical | major | moderate | minor",
        "recentActivity": "growing | stable | thinning",
        "entrenchmentIndicators": {
          "systems": "string or null",
          "tupeWorkforce": "string or null",
          "data": "string or null",
          "relationships": "string or null",
          "scopeCreepHistory": "string or null",
          "ipHeld": "string or null"
        },
        "vulnerabilitySignals": {
          "cancelledContracts": ["string — name + date"],
          "auditFindings": ["string — what NAO/PAC said about this supplier on this buyer"],
          "performanceIssues": ["string — public reporting of missed SLAs, complaints, etc."],
          "publicComplaints": ["string — service-user or media reporting"],
          "earlyTerminations": ["string"],
          "leadershipDeparturesAtSupplier": ["string — relevant if account-team continuity is at risk"],
          "overallVulnerability": "high | medium | low | none",
          "rationale": "string",
          "sourceRefs": ["SRC-nnn"]
        },
        "dossierRef": "string or null — asset ID of supplier dossier if one exists"
      }
    ],
    "adjacentSuppliers": ["string"],
    "supplierConcentration": "evidenced field",
    "switchingEvidence": "evidenced field",
    "marketRefreshAreas": ["string"],
    "barriersToEntry": {
      "value": ["string — frameworks not accessible, accreditations required, security clearance levels, named domain expertise, prior-experience thresholds"],
      "type": "fact | inference",
      "confidence": "high | medium | low",
      "rationale": "string",
      "sourceRefs": ["SRC-nnn"]
    }
  },

  "relationshipHistory": {
    "sectionConfidence": "high | medium | low | none",
    "tierNote": "string — e.g. 'No Tier 4 data provided...'",
    "priorContracts": [
      { "contractName": "string", "value": "string", "period": "string", "status": "active | closed" }
    ],
    "activeProgrammes": ["string"],
    "pastBids": [
      { "opportunityName": "string", "date": "string", "outcome": "win | loss | no-bid", "feedbackReceived": "string or null" }
    ],
    "executiveRelationships": ["string"],
    "knownAdvocates": ["string"],
    "knownBlockers": ["string"],
    "intelGaps": ["string"]
  },

  "risksAndSensitivities": {
    "sectionConfidence": "high | medium | low | none",
    "summaryNarrative": "string — decision-grade summary of risk landscape",
    "procurementControversies": ["evidenced field"],
    "programmeFailures": ["evidenced field"],
    "auditFindings": ["evidenced field"],
    "mediaScrutiny": ["evidenced field"],
    "publicSensitivities": ["evidenced field"],
    "positioningSensitivities": ["evidenced field"]
  },

  "pursuitImplications": {
    "sectionConfidence": "high | medium | low | none",
    "sectionCaveat": "These are buyer-derived, bidder-neutral implications. They describe what any pursuit against this buyer should do or avoid because of who this buyer is. They do not factor in the bidder's specific positioning — that is downstream Win Strategy work.",
    "summaryNarrative": "string — one paragraph headline of buyer-specific pursuit implications",
    "implications": [
      {
        "implication": "string — what any bidder against this buyer should do or avoid",
        "category": "stance | language | evidence | commercial | engagement | risk-management | timing | structural",
        "rationale": "string — why the buyer's profile drives this",
        "type": "inference",
        "confidence": "high | medium | low",
        "sourceRefs": ["SRC-nnn"],
        "linkedFrameworkQuestions": ["string — e.g. 'A1: change-driver', 'B6: switching anxiety'"],
        "derivedFromLenses": ["mandate | pressure | money | buying-behaviour | risk-posture | supplier-landscape"]
      }
    ]
  },

  "sourceRegister": {
    "sources": [
      {
        "sourceId": "SRC-001",
        "sourceName": "string — e.g. 'HMRC Annual Report 2024-25'",
        "sourceType": "annual_report | strategy_document | board_paper | procurement_notice | audit_report | media | parliamentary | framework_data | internal | other",
        "publicationDate": "ISO 8601 or null",
        "accessDate": "ISO 8601",
        "reliability": "Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5",
        "sectionsSupported": ["string — section names this source informs"],
        "lensesContributed": ["mandate | pressure | money | buying-behaviour | risk-posture | supplier-landscape | pursuit-implications"],
        "extractionTemplateApplied": "string or null — e.g. 'digital_strategy', 'annual_report'",
        "url": "string or null"
      }
    ],
    "gaps": ["string — areas where no source was found"],
    "staleFields": ["string — fields relying on sources older than 3 years"],
    "lowConfidenceInferences": ["string — inferences with low confidence that need validation"]
  },

  "actionRegister": {
    "summary": "string — one-line state, e.g. '7 open (2 critical, 3 high), 3 closed since last refresh'",
    "openCriticalCount": "number",
    "openHighCount": "number",
    "openMediumCount": "number",
    "openLowCount": "number",
    "actions": [
      {
        "actionId": "ACT-001",
        "createdAt": "ISO 8601",
        "createdInVersion": "string — e.g. '3.0'",
        "status": "open | in-progress | closed | superseded",
        "type": "research | document-acquisition | interview | tier4-amend | refresh | triangulation",
        "gap": {
          "description": "string — plain-English statement of what is unknown or uncertain",
          "section": "string — dossier section this gap sits in",
          "fields": ["string — specific dotted paths affected"],
          "frameworkQuestionsBlocked": ["string — e.g. 'A4: cancellation likelihood', 'B6: switching anxiety'"],
          "currentState": "unknown | low-confidence | stale | inference-needs-validation"
        },
        "recommendedNextStep": {
          "method": "find-document | inject-document | web-research | account-team-amend | tier4-debrief | desk-triangulation",
          "specificTarget": "string — e.g. 'HMRC Tax Administration 2030 strategy, full document'",
          "expectedSourceLocation": "string — e.g. 'gov.uk/hmrc-publications, NAO archive'",
          "estimatedEffort": "small | medium | large",
          "estimatedConfidenceUplift": "high | medium | low"
        },
        "owner": {
          "role": "capture-lead | account-director | bid-manager | analyst | sro-engagement | unassigned",
          "namedPerson": "string or null"
        },
        "priority": "critical | high | medium | low",
        "priorityRationale": "string — why this priority, naming the downstream decision affected",
        "blocksDownstreamDecision": ["qualify-pursue-no-pursue | win-strategy-themes | capture-plan-engagement | competitive-positioning | commercial-posture | bid-execution | incumbency-displacement"],
        "closure": {
          "closedAt": "ISO 8601 or null",
          "closedInVersion": "string or null",
          "closedBy": "build | refresh | inject | amend | superseded | null",
          "closingSourceId": "string or null — SRC-nnn or SRC-INT-nnn that closed it",
          "closureNote": "string or null"
        }
      }
    ]
  },

  "computedScores": {
    "buyerRiskAversionScore": null,
    "changeMaturityScore": null,
    "innovationAppetiteScore": null,
    "incumbencyStrengthScore": null,
    "commercialSensitivityScore": null,
    "relationshipStrengthScore": null,
    "winDifficultyScore": null
  },

  "linkedAssets": {
    "supplierDossiers": [{ "assetId": "string", "assetType": "supplier-dossier", "assetName": "string", "generatedAt": "ISO 8601" }],
    "sectorBriefs": [{ "assetId": "string", "assetType": "sector-brief", "assetName": "string", "generatedAt": "ISO 8601" }],
    "pipelineScans": [{ "assetId": "string", "assetType": "pipeline-scan", "assetName": "string", "generatedAt": "ISO 8601" }]
  },

  "changeSummary": [
    {
      "section": "string — section name",
      "field": "string — field name",
      "previousValue": "string — summary of old value",
      "newValue": "string — summary of new value",
      "changeReason": "string — why this changed"
    }
  ]
}
```

**Note:** `changeSummary` is populated ONLY on refresh, inject, and amend runs.
Set to null on first-build runs.

---

## Organisational archetype taxonomy

The `buyerSnapshot.organisationalArchetype` field uses the per-field evidence
wrapper. The value must be one of the following. This describes the
**organisation's dominant buying behaviour** — not a specific opportunity.

| Archetype | Meaning | Pursuit implication |
|---|---|---|
| `strategic_central_commissioner` | Mature commercial centre, strong governance, expects sophisticated outcome-led propositions | High bar for quality; needs strategic narrative |
| `framework_first_operator` | Buys through accessible routes; speed and compliant fit matter more than visionary repositioning | Match framework requirements precisely; don't oversell |
| `devolved_capacity_constrained` | Limited commercial bandwidth; clarity, low-friction compliance, and implementation confidence matter most | Make it easy to buy; reduce burden on buyer team |
| `programme_led_transformer` | Driven by transformation agenda; open to flexible procedure, dialogue, and solution shaping | Co-creation opportunity; invest in pre-market engagement |
| `incumbent_locked_risk_averse` | Market formally open but practically difficult to unseat due to operational, data, security, or TUPE lock-in | Understand lock-in mechanism; find the lever |
| `politically_sensitive_high_scrutiny` | Procurement shaped by controversy, citizen impact, ministerial attention, or audit exposure | Risk-proof the proposition; anticipate scrutiny |
| `compliance_procurement_machine` | Highly process-led, evaluation-led, defensible; less interested in narrative, more in audit-proof quality | Score maximisation; follow the evaluation criteria exactly |

---

## Schema rules

- `meta.generatedBy`: `"Agent 2 Skill 2 v3.0"`
- `meta.taxonomyVersion`: `"2.0"`
- `meta.version`: `"3.0"` on first build under v3.0; increment on refresh
- All `computedScores` values: `null` — the renderer derives scores from
  evidence fields
- Use ISO 8601 dates throughout
- Use `null` for unknown/unavailable fields, not empty strings
- Source register IDs: sequential — SRC-001, SRC-002, etc.
- Action register IDs: sequential — ACT-001, ACT-002, etc.
- `meta.refreshDue`: set to 6 months from today, or the buyer's next known
  reporting milestone if earlier. Do not leave null on first build.
- **Lens tagging is mandatory.** Every source registered in `sourceRegister.sources`
  must carry a `lensesContributed` array naming at least one of the seven lenses.
- **Action register must be populated.** Build mode produces actions for every
  gap, stale field, and low-confidence inference identified during research. An
  empty `actionRegister.actions` array is only valid if the dossier has zero
  gaps, zero stale fields, and zero low-confidence inferences — which is
  effectively never.

---

## Organisation type enum

`organisationType` must be one of:

| Value | Covers |
|---|---|
| `department` | Central government departments (e.g., HMRC, Home Office) |
| `agency` | Executive agencies (e.g., DVLA, Companies House) |
| `ndpb` | Non-departmental public bodies |
| `nhs_trust` | NHS trusts (acute, mental health, community, ambulance) |
| `nhs_icb` | Integrated care boards |
| `local_authority` | County, district, unitary, metropolitan, London borough councils |
| `devolved` | Welsh Government, Scottish Government, NI Executive and their bodies |
| `mod` | Ministry of Defence and defence agencies (DE&S, Dstl, etc.) |
| `regulator` | Regulators (Ofcom, Ofgem, CQC, etc.) |
| `other` | Anything not covered above |

---

## Buying readiness enum

`buyingReadiness` must be one of:

- `pre-pipeline` — no evidence of procurement intent
- `pipeline-identified` — procurement appears in published pipeline
- `pre-market-engagement` — signals of upcoming market engagement
- `post-market-engagement` — market engagement completed, procurement expected
- `procurement-live` — active procurement in progress
- `awarded` — contract recently awarded

---

## Spend classification enum

`spendClassification` must be one of:

| Value | Meaning |
|---|---|
| `mandatory` | Legal, regulatory, or contractual obligation to procure — cannot defer or descope |
| `discretionary` | Optional spend — could be deferred, descoped, or cancelled if pressure rises |
| `reactive` | Triggered by a specific event (audit finding, programme failure, incident, ministerial direction) |
| `strategic` | Tied to a strategic agenda (transformation, modernisation, savings programme) — political commitment |
| `mixed` | Components of multiple classifications (e.g. mandatory floor + discretionary stretch) |
| `unknown` | Insufficient evidence to classify — flag as gap |

The spend classification directly shapes pursuit confidence: mandatory and
strategic spend rarely cancels; discretionary spend cancels first under
pressure; reactive spend can pivot fast.

---

## Dominant decision lens enum

`decisionUnitAssumptions.dominantDecisionLens.value` must be one of:

| Value | Meaning |
|---|---|
| `commercial` | Driven by procurement / commercial team — process discipline, lowest-price-compliant, framework adherence |
| `operational` | Driven by service delivery — continuity, mobilisation safety, operational risk minimisation |
| `political` | Driven by ministerial or board attention — reputation, optics, alignment to public commitments |
| `technical` | Driven by technical authority / SRO — solution fit, architecture compatibility, capability depth |
| `financial` | Driven by finance / HMT controls — affordability, value-for-money, budget envelope adherence |
| `mixed` | Two or more lenses with comparable weight |
| `unknown` | Insufficient evidence to identify a dominant lens |

---

## Change maturity sub-fields

The `cultureAndPreferences.changeMaturity` object contains six sub-fields.
Each uses the per-field evidence wrapper. Each value must be one of: `high`,
`medium`, `low`, `unknown`.

| Sub-field | Assess from |
|---|---|
| `deliveryMaturity` | Programme delivery record, audit findings on delivery |
| `digitalMaturity` | Transformation investment, published digital roadmaps |
| `governanceMaturity` | Audit findings, assurance structure, governance framework |
| `supplierManagementMaturity` | Contract management patterns, renegotiation behaviour |
| `coCreationTolerance` | Market engagement style, dialogue procedure usage |
| `phaseOrAgileCapability` | Evidence of phased or iterative delivery in prior contracts |

---

## Action register field reference

### Action types

| Type | When to use |
|---|---|
| `research` | The gap can be closed by web research alone — no document retrieval needed |
| `document-acquisition` | A specific document needs to be retrieved (often paywalled, internal, or unindexed) |
| `inject-document` | A document is known to exist and is available — should be injected to deepen extraction |
| `interview` | Account team or stakeholder interview required |
| `tier4-amend` | Needs internal Tier 4 / Tier 5 intelligence amend |
| `refresh` | Field is stale and needs a refresh against current sources |
| `triangulation` | Conflict between sources — needs additional source to resolve |

### Priority logic

| Priority | When to use |
|---|---|
| `critical` | Blocks a pursue / no-pursue decision in Qualify (Section A questions). Without closing this, pursuit confidence is structurally weak. |
| `high` | Blocks a Win Strategy or Capture Plan output (Section B and C questions). Pursuit can run, but win architecture is missing a key input. |
| `medium` | Deepens an existing field; pursuit not blocked, but answer quality improves with closure. |
| `low` | Completeness only; nice-to-have. |

### Owner roles

| Role | Typical responsibility |
|---|---|
| `capture-lead` | Strategic intelligence gaps, change-driver, switching anxiety |
| `account-director` | Tier 4 relationship intelligence, advocates, blockers |
| `bid-manager` | Procurement-mechanic gaps, framework access, evaluation criteria |
| `analyst` | Desk research, document acquisition, triangulation |
| `sro-engagement` | Stakeholder access, decision-unit interest validation |
| `unassigned` | Not yet allocated — should be assigned at next pursuit review |

---

## Pursuit implications field reference

### Implication categories

| Category | Example |
|---|---|
| `stance` | "Lead with delivery confidence over transformation ambition — three programmes in last 24 months were NAO-flagged for unrealistic delivery confidence" |
| `language` | "Use 'value-for-money' framing; avoid 'transformation' as a headline term — Permanent Secretary publicly criticised it as 'consultant-speak' in March 2026" |
| `evidence` | "Over-evidence financial controls — internal audit qualification two years running on financial reconciliation" |
| `commercial` | "Expect aggressive redlines on liability cap — commercial team has rejected supplier-favourable caps in last three procurements" |
| `engagement` | "Engage commercial team before SRO — they gatekeep pre-market engagement, and SRO defers to them on commercial fit" |
| `risk-management` | "Neutralise SRO career risk — predecessor was forced out after programme failure; new SRO needs continuity narrative" |
| `timing` | "Engage before April budget cycle close — all approvals freeze for 4 weeks around year-end" |
| `structural` | "Pursue as joint bid with TUPE-compliant partner — incumbent's 1,200 staff sit in scope and buyer has rejected sole-prime bids without TUPE plan" |

Each implication must be backed by specific evidence (sourceRefs) and tagged
to at least one of the framework questions it informs and one of the lenses
it derives from.

---

## Linked assets structure

Each array in `linkedAssets` contains asset pointer objects:

```json
{
  "assetId": "string — platform asset identifier",
  "assetType": "supplier-dossier | sector-brief | pipeline-scan",
  "assetName": "string — human-readable name",
  "generatedAt": "ISO 8601 datetime"
}
```

Use empty arrays `[]` if no linked assets exist. Do not use `null` for these
arrays.
