# Output Schema — Supplier Dossier JSON

This schema conforms to the BidEquity Universal Skill Spec. The `meta`,
`changeSummary`, and `sourceRegister` blocks are universal; the `D1`–`D9`
domains and `strategicScores` are supplier-skill-specific.

```json
{
  "meta": {
    "slug": "string — kebab-case supplier identifier",
    "supplierName": "string — full legal name",
    "skillName": "supplier-intelligence",
    "version": "string — semver e.g. 1.0.0 or 3.1.2",
    "mode": "build | refresh | inject | amend",
    "builtDate": "YYYY-MM-DD",
    "lastModifiedDate": "YYYY-MM-DD",
    "refreshDue": "YYYY-MM-DD",
    "depthMode": "snapshot | standard | deep",
    "degradedMode": "boolean",
    "degradedModeReason": "string or null",
    "sourceCount": "integer",
    "internalSourceCount": "integer",
    "prerequisitesPresentAt": {
      "version": "string — version this snapshot was taken at",
      "date": "YYYY-MM-DD",
      "required": {
        "supplierName": "boolean"
      },
      "preferred": {
        "ftsData": "boolean",
        "companiesHouseData": "boolean"
      }
    },
    "versionLog": [
      {
        "version": "string",
        "date": "YYYY-MM-DD",
        "mode": "build | refresh | inject | amend",
        "summary": "string — one-line description of what this operation did"
      }
    ]
  },

  "claims": [
    {
      "claimId": "string — CLM-NNN format",
      "claimText": "string — assertion text, self-contained",
      "claimDate": "ISO 8601 date",
      "source": "string — SRC-nnn or URL or upstream dossier reference",
      "sourceDate": "ISO 8601 date or null",
      "sourceTier": "integer — 1, 2, 3, or 4"
    }
  ],

  "changeSummary": [
    {
      "section": "string — top-level section affected, e.g. D6",
      "field": "string — dotted field path",
      "before": "string — previous value summary",
      "after": "string — new value summary",
      "reason": "string — why the change happened"
    }
  ],

  "deltaSummary": "string — one-line summary of changes since previous version (refresh mode only)",

  "D1": {
    "legalName": "evidence_wrapper",
    "companiesHouseNo": "evidence_wrapper",
    "parentCompany": "evidence_wrapper",
    "subsidiaries": ["evidence_wrapper"],
    "sicCodes": ["evidence_wrapper"],
    "incorporationDate": "evidence_wrapper",
    "groupStructureNotes": "evidence_wrapper"
  },

  "D2": {
    "totalUkPublicSectorRevenueGbpm": "evidence_wrapper",
    "pctOfGroupRevenue": "evidence_wrapper",
    "sectorBreakdown": {
      "centralGovernment": "evidence_wrapper",
      "localAuthority": "evidence_wrapper",
      "nhs": "evidence_wrapper",
      "defence": "evidence_wrapper",
      "justice": "evidence_wrapper",
      "transport": "evidence_wrapper"
    },
    "geographicSpread": "evidence_wrapper"
  },

  "D3": {
    "frameworkPositions": [
      {
        "framework": "string",
        "lot": "string",
        "expiry": "YYYY-MM-DD",
        "valueCeilingGbpm": "number or null"
      }
    ],
    "topContracts": [
      {
        "buyer": "string",
        "title": "string",
        "valueGbpm": "number",
        "expiry": "YYYY-MM-DD",
        "cpv": "string"
      }
    ]
  },

  "D4": {
    "contractsExpiring24m": [
      {
        "buyer": "string",
        "title": "string",
        "valueGbpm": "number",
        "expiry": "YYYY-MM-DD",
        "rebidVulnerability": "high | medium | low",
        "vulnerabilityRationale": "string"
      }
    ],
    "knownPipelinePursuits": ["evidence_wrapper"]
  },

  "D5": {
    "coreCapabilities": ["evidence_wrapper"],
    "technologyStack": ["evidence_wrapper"],
    "accreditations": ["evidence_wrapper"],
    "partnershipEcosystem": ["evidence_wrapper"]
  },

  "D6": {
    "ceo": "evidence_wrapper",
    "cfo": "evidence_wrapper",
    "publicSectorMd": "evidence_wrapper",
    "bdDirector": "evidence_wrapper",
    "recentLeadershipChanges": ["evidence_wrapper"],
    "keyBuyerRelationships": ["evidence_wrapper"]
  },

  "D7": {
    "ftsWinRateSignal": "evidence_wrapper",
    "keyCompetitorsBySector": {"sector": ["competitorName"]},
    "differentiationNarrative": "evidence_wrapper",
    "knownWeaknesses": ["evidence_wrapper"],
    "pricingPosture": "evidence_wrapper"
  },

  "D8": {
    "recentWins": ["evidence_wrapper"],
    "recentLosses": ["evidence_wrapper"],
    "pressSignals90d": ["evidence_wrapper"],
    "regulatoryReputationalEvents": ["evidence_wrapper"],
    "investorAnalystCommentary": ["evidence_wrapper"]
  },

  "D9": {
    "revenueTrend3yrGbpm": ["number"],
    "ebitdaMarginPct": "evidence_wrapper",
    "netDebtGbpm": "evidence_wrapper",
    "publicSectorRevenuePct": "evidence_wrapper",
    "contractRiskProvisions": "evidence_wrapper",
    "creditRiskSummary": "evidence_wrapper"
  },

  "strategicScores": {
    "sectorStrength": {
      "score": "number 0-10",
      "factors": {
        "frameworkCoverage": "number 0-3",
        "contractTenure": "number 0-3",
        "buyerRelationshipDepth": "number 0-2",
        "capabilityBreadth": "number 0-2"
      },
      "rationale": "string 2 sentences"
    },
    "competitorThreat": {
      "score": "number 0-10",
      "factors": {
        "incumbencyRelevance": "number 0-3",
        "bidCapacity": "number 0-3",
        "priceAggressionSignals": "number 0-2",
        "differentiationStrength": "number 0-2"
      },
      "rationale": "string 2 sentences"
    },
    "vulnerability": {
      "score": "number 0-10",
      "factors": {
        "contractExpiryConcentration": "number 0-3",
        "financialStressSignals": "number 0-3",
        "reputationalRisk": "number 0-2",
        "leadershipInstability": "number 0-2"
      },
      "rationale": "string 2 sentences"
    }
  },

  "vulnerabilityMap": [
    {
      "contract": "string",
      "buyer": "string",
      "expiry": "YYYY-MM-DD",
      "vulnerability": "high | medium | low",
      "displacementRoute": "string"
    }
  ],

  "signalWatchList": [
    {
      "signal": "string",
      "trigger": "string",
      "action": "string"
    }
  ],

  "amendments": [
    {
      "sourceId": "SRC-INT-001",
      "date": "YYYY-MM-DD",
      "type": "debrief | crmNote | accountTeam | partnerIntel",
      "author": "string",
      "content": "string",
      "domainsAffected": ["D7"],
      "confidence": "high | medium | low"
    }
  ],

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
        "sectionsSupported": ["D1"],
        "evidenceAge": "string e.g. '13 months'",
        "notes": "string"
      }
    ],
    "internalSources": [
      {
        "sourceId": "SRC-INT-001",
        "tier": 4,
        "sourceType": "internal",
        "sourceName": "string",
        "accessDate": "YYYY-MM-DD",
        "sectionsSupported": ["D7"]
      }
    ],
    "gaps": ["string — what is missing and what would close it"],
    "staleFields": ["string — fields where evidence is >24 months old"],
    "lowConfidenceInferences": ["string — fields needing corroboration"]
  }
}
```

## `claims` (array, required)

Top-level array of structured claim objects. Every material assertion in
the dossier narrative must appear here with a stable `claimId`. The
narrative cites claims inline using `[CLM-id]` markers.

```json
{
  "claims": [
    {
      "claimId": "CLM-001",
      "claimText": "Serco holds the Electronic Monitoring contract with the Ministry of Justice, valued at approximately £300m over 8 years.",
      "claimDate": "2026-04-30",
      "source": "SRC-003",
      "sourceDate": "2023-11-15",
      "sourceTier": 1
    }
  ]
}
```

The six fields are mandatory on every claim. Schema and validation rules
live in `pwin-platform/skills/agent2-market-competitive/master/CLAIMS-BLOCK-SCHEMA.md`
(canonical) and §13 of the Universal Skill Spec.

"Material" means any claim that bears on a downstream decision — competitive
positioning, win theme, displacement strategy, or incumbent threat assessment.
Background colour ("Serco is a UK-listed public services company") does not
need a citation.

---

## Evidence wrapper structure

Every interpretive data point uses this shape:

```json
{
  "value": "the fact or estimate",
  "type": "fact | estimate | signal | inference",
  "confidence": "high | medium | low",
  "rationale": "why this confidence level",
  "sourceRefs": ["SRC-001", "SRC-002"]
}
```
