# Extraction Template — Cyber Security Strategy

This template is loaded when a source is classified as
`cyber_security_strategy`.

A cyber strategy carries the highest concentration of risk-posture
intelligence in a buyer dossier. It tells the bidder what control
frameworks they must align to, what clearance levels are non-
negotiable, what data residency rules apply, what the buyer thinks
about supply-chain security, and how mature their internal security
function is. Slogans like "they have a cyber strategy" are useless;
the template forces capture of accreditations, clearance bands, named
frameworks, and supplier obligations.

---

## When to apply this template

Apply when the source is any of:

- A published cyber security strategy
- A security governance framework
- A departmental cyber operating model
- An NCSC alignment statement specific to this buyer
- A data security and protection toolkit (NHS DSPT) submission summary
- A defence security policy framework / JSP-aligned document
- An information security policy with substantive control content
  (not a one-page restatement of legal obligations)

Do not apply to generic privacy notices, ICO registration documents,
or one-page "we take security seriously" statements. If the source is
a digital strategy with a security chapter, use the digital-strategy
template (its `technologyDirection.cyberPosture` block already
captures the substance).

---

## Extraction depth requirement

Cyber strategies are typically 15–60 pages. Deep mode requires capture
of every named accreditation framework, clearance band, sovereignty
position, and supplier obligation. Skip reproductions of NCSC guidance
that the document only references — capture the references, not the
guidance content itself.

---

## Template schema

```json
{
  "extractionType": "cyber_security_strategy",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact title",
    "buyerName": "string",
    "publicationDate": "ISO 8601",
    "periodCovered": "string or null",
    "approvingAuthority": "string — CISO, board, Permanent Secretary",
    "supersedes": "string or null",
    "totalPages": "number",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "threatModel": {
    "namedThreatActors": ["string — nation-state, organised crime, hacktivist, insider, supply-chain"],
    "namedRisks": ["string — risks the strategy explicitly acknowledges"],
    "criticalAssetsIdentified": ["string — systems, data, services treated as crown jewels"],
    "regulatedDataTypes": ["string — OFFICIAL-SENSITIVE, SECRET, special-category personal data, healthcare, child protection, etc."]
  },

  "controlFrameworks": {
    "namedAccreditations": ["string — NCSC CAF, ISO 27001, Cyber Essentials Plus, NIS2, FedRAMP, SOC2 Type II"],
    "alignmentStatements": ["string — explicit alignment to NCSC, NIST, NHS DSPT, JSP 440"],
    "internallyOwnedStandards": ["string — buyer's own standards expected of suppliers"],
    "auditCadence": "string or null — how often controls are independently audited"
  },

  "clearanceAndAccess": {
    "personnelClearanceBands": [
      {
        "level": "BPSS | CTC | SC | eSC | DV | eDV | NPPV-3 | other",
        "appliesTo": "string — which roles or services require this level",
        "isMandatory": "boolean"
      }
    ],
    "supplierVettingRules": "string — what suppliers must do to staff contracts",
    "accessControlPosture": "string or null — least-privilege, JIT access, zero-trust statements"
  },

  "dataAndSovereignty": {
    "dataResidencyPosture": "uk-only | uk-and-eu | sovereign-cloud | mixed | unstated",
    "cloudPosture": "string — preferred cloud arrangements (UK Crown Hosting, government-assured cloud, hyperscalers, sovereign cloud, etc.)",
    "encryptionRequirements": "string or null — at-rest, in-transit, FIPS 140-2/3, named ciphers",
    "dataLossPreventionPosture": "string or null",
    "crossBorderRules": "string or null"
  },

  "supplyChainSecurity": {
    "supplierObligations": ["string — what suppliers must demonstrate (e.g. Cyber Essentials Plus before contract award)"],
    "subContractorControls": ["string — flow-down requirements"],
    "softwareSupplyChainPosture": "string or null — SBOM, secure-by-design, code-signing requirements",
    "auditAndAssuranceOfSuppliers": "string or null",
    "knownBarrierToEntry": ["string — accreditations or clearance levels that gate market participation"]
  },

  "incidentAndResilience": {
    "namedIncidentResponseTeam": "string or null — internal team, SOC arrangement, NCSC partnership",
    "incidentReportingObligations": ["string — internal escalation and external regulator notifications"],
    "businessContinuityPosture": "string or null",
    "namedRecentIncidents": ["string — incidents the strategy references as drivers"]
  },

  "investmentAndCapability": {
    "fundedProgrammes": [
      {
        "programmeName": "string",
        "scopeSummary": "string",
        "budget": "string or null",
        "byWhen": "string or null"
      }
    ],
    "internalCapabilityChanges": ["string — CISO appointment, SOC build-out, security workforce growth"],
    "outsourcedSecurityServices": ["string — managed SOC, MDR, vCISO, external pen-testing partners named"],
    "buildVsBuyPosture": "build-internal | buy-managed | hybrid | unstated"
  },

  "complianceLandscape": {
    "namedRegulators": ["string — ICO, NCSC, NIS Competent Authority, MoD DipCC, NHS England DSPT"],
    "namedLegalObligations": ["string — UK GDPR, NIS Regulations, OSA, sector-specific"],
    "publishedTransparencyArtefacts": ["string — annual security report, DSPT submission, IT health check publication"]
  },

  "languageAndFraming": {
    "preferredTerminology": ["string — distinctive terms used repeatedly"],
    "policyFrames": ["string — secure-by-design, defend-as-one, cyber resilient, etc."],
    "prohibitedOrAvoidedLanguage": ["string — terms the document explicitly rejects"]
  },

  "namedStakeholders": [
    {
      "name": "string",
      "role": "string — CISO, SIRO, Director of Security, etc.",
      "responsibilityInStrategy": "string",
      "isDecisionMaker": "boolean"
    }
  ],

  "publicCommitments": [
    {
      "statement": "string — direct quote",
      "speaker": "string",
      "topic": "string"
    }
  ],

  "pursuitImplications": [
    {
      "implication": "string — buyer-derived, bidder-neutral",
      "category": "stance | language | evidence | commercial | engagement | risk-management | timing | structural",
      "rationale": "string"
    }
  ],

  "dossierMappings": [
    {
      "extractedPath": "string",
      "mapsToDossierField": "string",
      "operation": "extend | replace | upgrade",
      "lens": "mandate | pressure | money | buying-behaviour | risk-posture | supplier-landscape | pursuit-implications",
      "answersFrameworkQuestions": ["string"],
      "closesActionIds": ["string or null"]
    }
  ],

  "extractionQualityCheck": {
    "fullRead": "boolean",
    "namedAccreditationsCaptured": "number",
    "clearanceBandsCaptured": "number",
    "supplierObligationsCaptured": "number",
    "fundedProgrammesCaptured": "number",
    "unextractedSections": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `controlFrameworks.namedAccreditations[]` | `commercialAndRiskPosture.cyberDataSensitivity` | risk-posture | upgrade (inference → fact) |
| `controlFrameworks.alignmentStatements[]` | `commercialAndRiskPosture.cyberDataSensitivity` | risk-posture | extend |
| `clearanceAndAccess.personnelClearanceBands[]` | `commercialAndRiskPosture.securityClearanceRequirements` | risk-posture | replace (this is the most authoritative source) |
| `clearanceAndAccess.supplierVettingRules` | `supplierEcosystem.barriersToEntry` | supplier-landscape, risk-posture | extend |
| `dataAndSovereignty.dataResidencyPosture` + `cloudPosture` | `commercialAndRiskPosture.cyberDataSensitivity` | risk-posture | extend |
| `supplyChainSecurity.supplierObligations[]` | `supplierEcosystem.barriersToEntry` | supplier-landscape, risk-posture | extend |
| `supplyChainSecurity.knownBarrierToEntry[]` | `supplierEcosystem.barriersToEntry` | supplier-landscape | extend |
| `incidentAndResilience.namedRecentIncidents[]` | `risksAndSensitivities.publicSensitivities` | risk-posture | extend |
| `investmentAndCapability.fundedProgrammes[]` | `strategicPriorities.majorProgrammes[]` | pressure, money | extend |
| `investmentAndCapability.outsourcedSecurityServices[]` | `supplierEcosystem.incumbents[]` (where named) | supplier-landscape | extend |
| `investmentAndCapability.buildVsBuyPosture` | `cultureAndPreferences.changeMaturity.digitalMaturity` | risk-posture | extend |
| `complianceLandscape.namedRegulators[]` | `commercialAndRiskPosture.auditFoiExposure` | risk-posture | extend |
| `languageAndFraming` | `cultureAndPreferences.languageAndFraming` | risk-posture | extend |
| `namedStakeholders[]` (decisionMakers) | `decisionUnitAssumptions.technicalStakeholders` (CISO etc.) | buying-behaviour | extend |
| `publicCommitments[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `fullRead: false` in deep mode for a strategy >15 pages.
2. `controlFrameworks.namedAccreditations` empty AND
   `controlFrameworks.alignmentStatements` empty — every cyber
   strategy names at least one external standard or alignment.
3. `clearanceAndAccess.personnelClearanceBands` empty when the buyer
   handles classified or special-category data — a contemporary UK
   public-sector cyber strategy always specifies clearance bands for
   sensitive roles.
4. `supplyChainSecurity.supplierObligations` empty — every cyber
   strategy worth the name imposes obligations on suppliers; an empty
   array indicates the model didn't read the supplier-facing chapter.
5. `pursuitImplications[]` empty — every cyber strategy carries
   bidder-relevant implications. At minimum: clearance bands gate
   pursuit eligibility; supply-chain obligations gate bid response
   structure; sovereignty posture gates platform choice.
6. `dossierMappings` does not include the `pursuitImplications` mapping.

---

## Worked example (illustrative)

For a hypothetical "Department for Work and Pensions Cyber Security
Strategy 2026-2029" extraction:

```
controlFrameworks:
  namedAccreditations: ["NCSC CAF", "ISO 27001:2022", "Cyber Essentials Plus (mandatory for all suppliers)"]
  alignmentStatements: ["Aligned to GovAssure (NCSC + Cabinet Office)", "Adheres to UK GDPR Article 32"]
clearanceAndAccess:
  personnelClearanceBands:
    - { level: "BPSS", appliesTo: "All staff and supplier personnel with system access", isMandatory: true }
    - { level: "SC", appliesTo: "Personnel with bulk access to fraud and error case data", isMandatory: true }
    - { level: "eSC", appliesTo: "Personnel handling Universal Credit transactional data at scale", isMandatory: false }
  supplierVettingRules: "All supplier personnel must hold cleared status before contract commencement; vetting cost borne by supplier; no in-flight clearance permitted on operational service contracts."
dataAndSovereignty:
  dataResidencyPosture: "uk-only"
  cloudPosture: "Approved hyperscaler regions (AWS UK, Azure UK South); sovereign-cloud preference for highly sensitive workloads"
supplyChainSecurity:
  supplierObligations:
    - "Cyber Essentials Plus mandatory at contract award and annually thereafter"
    - "SBOM provided for all delivered software"
    - "Annual independent penetration test, results shared with DWP CISO"
  knownBarrierToEntry: ["Cyber Essentials Plus", "SC clearance for delivery team"]
investmentAndCapability:
  fundedProgrammes[0]:
    programmeName: "DWP Security Operations Centre uplift"
    scopeSummary: "Move from outsourced 8x5 SOC to in-house 24x7 SOC with named MDR partner for tier-3 escalation"
    budget: "£42m capital + £18m/year run"
    byWhen: "FY27-28"
  buildVsBuyPosture: "hybrid"
languageAndFraming:
  preferredTerminology: ["secure-by-design", "defend-as-one", "fraud-and-error resilient", "least-privilege"]
pursuitImplications[0]:
  implication: "SC clearance for entire delivery team is a precondition; bidders without cleared headcount in
    place at award face mobilisation risk that DWP explicitly rejects."
  category: "engagement"
  rationale: "Strategy explicitly disallows in-flight clearance on operational service contracts."
pursuitImplications[1]:
  implication: "Sovereign-cloud / UK-only data residency is non-negotiable on sensitive workloads — public-cloud-first bid responses will fail risk gating."
  category: "structural"
  rationale: "dataResidencyPosture: uk-only with sovereign-cloud preference for sensitive workloads."
```

That level of substance satisfies the template. "DWP has a cyber
strategy" does not.
