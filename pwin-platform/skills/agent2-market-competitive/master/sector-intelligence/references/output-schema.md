# Output Schema — Sector Brief JSON

This schema conforms to the BidEquity Universal Skill Spec. The `meta`,
`changeSummary`, and `sourceRegister` blocks are universal; the `S1`–`S6`
sections and `sectorSummary` are sector-skill-specific.

```json
{
  "meta": {
    "slug": "string — kebab-case sector identifier",
    "sectorName": "string — display name",
    "skillName": "sector-intelligence",
    "version": "string — semver e.g. 1.0.0",
    "mode": "build | refresh | inject",
    "builtDate": "YYYY-MM-DD",
    "lastModifiedDate": "YYYY-MM-DD",
    "refreshDue": "YYYY-MM-DD",
    "depthMode": "snapshot | standard | deep",
    "degradedMode": "boolean",
    "degradedModeReason": "string or null",
    "sourceCount": "integer",
    "internalSourceCount": "integer (always 0 for sector — Tier 4 not applicable)",
    "prerequisitesPresentAt": {
      "version": "string",
      "date": "YYYY-MM-DD",
      "required": {
        "sectorName": "boolean"
      },
      "preferred": {
        "ftsSpendData": "boolean",
        "platformSectorKnowledge": "boolean"
      }
    },
    "versionLog": [
      {
        "version": "string",
        "date": "YYYY-MM-DD",
        "mode": "build | refresh | inject",
        "summary": "string"
      }
    ]
  },

  "changeSummary": [
    {
      "section": "string — top-level section affected, e.g. S1",
      "field": "string — dotted field path",
      "before": "string",
      "after": "string",
      "reason": "string"
    }
  ],

  "deltaSummary": "string — one-line summary of changes since previous version (refresh mode only)",

  "sectorSummary": {
    "addressableSpendGbpbn": "evidence_wrapper",
    "spendTrajectory": "growing | stable | declining",
    "topFrameworks": ["string"],
    "avgContractValueGbpm": "evidence_wrapper",
    "socialValueWeightTypicalPct": "evidence_wrapper",
    "qualityPriceSplitTypical": "evidence_wrapper",
    "keyBuyerOrganisations": ["string"],
    "majorRecompetes24m": ["string"],
    "sectorRiskLevel": "high | medium | low",
    "riskRationale": "string 2 sentences"
  },

  "S1": {
    "policyDirectionSummary": "evidence_wrapper",
    "keyLegislationActive": ["evidence_wrapper"],
    "keyLegislationPending": ["evidence_wrapper"],
    "scrutinyAndOversight": ["evidence_wrapper"],
    "policyRisks": ["evidence_wrapper"],
    "keyPolicyDocuments12m": ["evidence_wrapper"]
  },

  "S2": {
    "totalAddressableSpendGbpbn": "evidence_wrapper",
    "budgetTrajectory": "evidence_wrapper",
    "srCommitments": ["evidence_wrapper"],
    "procurementChannelMix": {
      "directAwardPct": "evidence_wrapper",
      "frameworkPct": "evidence_wrapper",
      "openCompetitionPct": "evidence_wrapper"
    },
    "topFrameworksByValue": ["evidence_wrapper"],
    "ftsSpendData": {
      "contractCount": "integer",
      "totalValueGbpm": "number",
      "avgContractValueGbpm": "number",
      "topCpvCodes": ["string"]
    }
  },

  "S3": {
    "demandDrivers": ["evidence_wrapper"],
    "serviceDeliveryModelShifts": ["evidence_wrapper"],
    "technologyAdoption": ["evidence_wrapper"],
    "workforceContext": ["evidence_wrapper"],
    "esgSocialValueRequirements": ["evidence_wrapper"],
    "majorRecompetes24m": [
      {
        "buyer": "string",
        "contract": "string",
        "estimatedValueGbpm": "number",
        "expiry": "YYYY-MM-DD",
        "notes": "string"
      }
    ]
  },

  "S4": {
    "keyPublications": ["string"],
    "commentaryThemes90d": ["evidence_wrapper"],
    "tradeBodyPositions": ["evidence_wrapper"],
    "analystViews": ["evidence_wrapper"],
    "parliamentaryActivity90d": ["evidence_wrapper"]
  },

  "S5": {
    "internationalComparisons": ["evidence_wrapper"],
    "performanceBenchmarks": ["evidence_wrapper"],
    "deliveryInnovationCases": ["evidence_wrapper"],
    "deliveryFailureCases": ["evidence_wrapper"],
    "devolvedComparisons": ["evidence_wrapper"]
  },

  "S6": {
    "buyerPrioritiesForSolutionDesign": ["evidence_wrapper"],
    "evaluationCriteriaPatterns": ["evidence_wrapper"],
    "differentiationAngles": ["evidence_wrapper"],
    "qualificationRiskFlags": ["evidence_wrapper"],
    "signalWatchList": [
      {
        "signal": "string",
        "trigger": "string",
        "action": "string"
      }
    ]
  },

  "sourceRegister": {
    "sources": [
      {
        "sourceId": "SRC-001",
        "tier": "integer 1-3",
        "sourceType": "string",
        "title": "string",
        "publicationDate": "YYYY-MM-DD or null",
        "accessDate": "YYYY-MM-DD",
        "url": "string or null",
        "sectionsSupported": ["S1"],
        "evidenceAge": "string",
        "notes": "string"
      }
    ],
    "internalSources": [],
    "gaps": ["string"],
    "staleFields": ["string"],
    "lowConfidenceInferences": ["string"]
  }
}
```

## Evidence wrapper structure

Every interpretive data point uses this shape:

```json
{
  "value": "the fact or estimate",
  "type": "fact | estimate | signal | inference",
  "confidence": "high | medium | low",
  "rationale": "why this confidence level",
  "sourceRefs": ["SRC-001"]
}
```
