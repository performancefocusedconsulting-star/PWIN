# Extraction Template — Major Projects Portfolio (GMPP) Entry

This template is loaded when a source is classified as `gmpp_entry` —
typically the per-project page or row in the IPA Annual Report on Major
Projects, the underlying GMPP transparency dataset, or a department's
own GMPP commentary.

GMPP entries carry the highest concentration of forensic supplier-
relevant intelligence in the public domain: a Delivery Confidence
Assessment (DCA) RAG rating from the IPA, whole-life cost and variance
against baseline, and the IPA's stated reasons for any rating
deterioration. A red or amber-red rating is a load-bearing signal for
incumbent vulnerability and for evidence-burden on bidders. The
template forces full capture of these signals.

---

## When to apply this template

Apply when the source is any of:

- An IPA Annual Report on Major Projects (per-project entry for this
  buyer)
- The GMPP transparency dataset (per-project rows)
- A department's response to a GMPP rating (formal IPA reply,
  parliamentary answer, NAO commentary on the project)
- A project's own annual transparency report referencing its DCA

For programmes that are not on the GMPP, do not use this template —
use the digital-strategy or departmental-plan template depending on
the source. For NAO/PAC reports about a GMPP project, use the NAO/PAC
template (which can extend a prior GMPP extraction).

---

## Extraction depth requirement

GMPP entries are typically half a page to two pages per project. Full-
read is always required. Where the source is the dataset, capture all
columns. Where the source is the report narrative, also capture the
IPA's qualitative commentary verbatim.

---

## Template schema

```json
{
  "extractionType": "gmpp_entry",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact title",
    "buyerName": "string — sponsoring department or arm's-length body",
    "publisher": "Infrastructure and Projects Authority | department | NAO | other",
    "reportingDate": "ISO 8601 — usually 30 September of reporting year",
    "publicationDate": "ISO 8601",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "project": {
    "projectName": "string — exact name as published",
    "sponsoringDepartment": "string",
    "projectId": "string or null — IPA reference if given",
    "projectType": "ICT | infrastructure | military-capability | transformation | government-transformation | service-delivery | property | scientific | other",
    "yearEnteredGmpp": "string or null",
    "expectedYearOfDelivery": "string or null",
    "projectStage": "concept | feasibility | development | implementation | live-service | closure"
  },

  "deliveryConfidenceAssessment": {
    "currentRating": "green | amber-green | amber | amber-red | red | exempt | unknown",
    "ratingDate": "ISO 8601",
    "ratingTrend": "improved | stable | deteriorated | new-entry",
    "priorRating": "string or null — most recent prior DCA",
    "ipaCommentary": "string — IPA's stated reason for the rating, verbatim where possible",
    "ratingHistory": [
      { "year": "string", "rating": "string" }
    ]
  },

  "cost": {
    "wholeLifeCost": "string — current estimate, e.g. '£3.4bn'",
    "wholeLifeCostAtBaseline": "string or null",
    "varianceFromBaseline": "string or null — e.g. '+£820m (+24%)'",
    "varianceCause": "string or null — IPA-stated cause if given",
    "annualSpendInReportingYear": "string or null",
    "fundingSource": "string or null — capital DEL, RDel, ring-fenced, mixed"
  },

  "schedule": {
    "currentEndDate": "string or null",
    "baselineEndDate": "string or null",
    "scheduleVariance": "string or null — e.g. '+18 months'",
    "varianceCause": "string or null"
  },

  "leadership": {
    "sro": "string or null — name and role",
    "sroTenure": "string or null",
    "sroChangeFlag": "boolean — true if SRO changed in the reporting period",
    "programmeDirector": "string or null"
  },

  "issuesAndRisks": [
    {
      "issue": "string — IPA-stated issue or risk",
      "severity": "high | medium | low | unstated",
      "category": "delivery | technical | commercial | supplier | resource | dependency | scope | benefit-realisation | other",
      "mitigationStated": "string or null"
    }
  ],

  "supplierContext": {
    "namedSuppliers": [
      {
        "supplierName": "string",
        "scope": "string — what they deliver on this project",
        "contractStatus": "active | terminated | renegotiated | unknown",
        "performanceContext": "string or null — IPA or NAO commentary on this supplier's role"
      }
    ],
    "deliveryModel": "in-house | outsourced | hybrid | systems-integrator-led | platform-led | partnership | unstated",
    "knownContractValues": ["string"],
    "vulnerabilitySignals": ["string — supplier-specific concerns surfaced (cost overrun blamed, performance issues cited, contract restructured, etc.)"]
  },

  "scopeChanges": [
    {
      "changeDescription": "string",
      "rationale": "string or null",
      "costImpact": "string or null",
      "scheduleImpact": "string or null"
    }
  ],

  "benefitsRealisation": {
    "stated": "string or null — what benefits the project is meant to deliver",
    "realisedToDate": "string or null",
    "concernsFlagged": ["string"]
  },

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
    "currentRatingCaptured": "boolean",
    "ipaCommentaryCaptured": "boolean — true if IPA's reason text captured verbatim or paraphrased",
    "wholeLifeCostCaptured": "boolean",
    "namedSuppliersCaptured": "number",
    "issuesAndRisksCaptured": "number",
    "unextractedSections": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `project.projectName + projectStage + cost + schedule` | `strategicPriorities.majorProgrammes[]` | pressure, money | extend or upgrade (GMPP is the most authoritative source on programme status) |
| `deliveryConfidenceAssessment.currentRating + ipaCommentary` | `strategicPriorities.majorProgrammes[].status` (synthesised RAG) | pressure | upgrade |
| `deliveryConfidenceAssessment` (where amber/amber-red/red) | `risksAndSensitivities.programmeFailures` | risk-posture | extend |
| `deliveryConfidenceAssessment` (where deteriorated trend) | `commissioningContextHypotheses.timelineRisks` | risk-posture, pressure | extend |
| `cost.varianceFromBaseline` (where positive) | `risksAndSensitivities.programmeFailures` and `commercialAndRiskPosture.affordabilitySensitivity` | money, risk-posture | extend |
| `schedule.scheduleVariance` (where slipped) | `commissioningContextHypotheses.timelineRisks` | pressure | extend |
| `leadership.sro + sroChangeFlag` | `organisationContext.seniorLeadership[]` and `organisationContext.recentChanges` (if changed) | mandate | extend |
| `issuesAndRisks[]` | `risksAndSensitivities.programmeFailures` and `commercialAndRiskPosture.mobilisationSensitivity` (where delivery/resource related) | risk-posture | extend |
| `supplierContext.namedSuppliers[]` | `supplierEcosystem.incumbents[]` | supplier-landscape | extend |
| `supplierContext.vulnerabilitySignals[]` | `supplierEcosystem.incumbents[].vulnerabilitySignals` | supplier-landscape | extend or upgrade |
| `supplierContext.deliveryModel` | `procurementBehaviour.innovationVsProven` and `supplierEcosystem.summaryNarrative` | buying-behaviour | extend |
| `scopeChanges[]` | `procurementBehaviour.renewalPatterns` (signal of mid-flight rebaselining) | buying-behaviour | extend |
| `benefitsRealisation.concernsFlagged` | `commercialAndRiskPosture.affordabilitySensitivity` | money, risk-posture | extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `currentRating` is `unknown` AND IPA report contains a rating —
   the rating is the central data point and must be captured.
2. `ipaCommentary` is empty when `currentRating` is amber-red, red,
   or deteriorating — the IPA always explains negative ratings, and
   that commentary is the highest-value qualitative signal.
3. `cost.wholeLifeCost` is null AND the entry is from the IPA Annual
   Report — cost is mandatory in IPA reporting.
4. `supplierContext.namedSuppliers[]` is empty when narrative names
   suppliers — the suppliers were mentioned but not extracted.
5. `pursuitImplications[]` is empty — every GMPP entry carries
   implications. At minimum: any non-green rating → "expect aggressive
   delivery-confidence scrutiny on adjacent bids"; any cost variance
   → "over-evidence cost control"; any SRO change → "engage incoming
   SRO on commercial direction"; any supplier vulnerability signal →
   "displacement opportunity if recompete window opens".
6. `dossierMappings` does not include the `pursuitImplications`
   mapping.

---

## Worked example (illustrative)

For a hypothetical "MoD — Future Combat Air System (FCAS)" GMPP entry:

```
project:
  projectName: "Future Combat Air System (Tempest / GCAP)"
  sponsoringDepartment: "Ministry of Defence"
  projectType: "military-capability"
  yearEnteredGmpp: "2018"
  expectedYearOfDelivery: "2035"
  projectStage: "development"
deliveryConfidenceAssessment:
  currentRating: "amber"
  ratingDate: "2025-09-30"
  ratingTrend: "deteriorated"
  priorRating: "amber-green"
  ipaCommentary: "International partnership complexity and supply-chain
    constraints have introduced delivery risk. Trilateral governance
    arrangements with Italy and Japan still maturing. Industrial-base
    capacity assumptions require revalidation."
  ratingHistory:
    - { year: "2024", rating: "amber-green" }
    - { year: "2023", rating: "amber-green" }
    - { year: "2022", rating: "amber" }
cost:
  wholeLifeCost: "£12.0bn"
  wholeLifeCostAtBaseline: "£10.4bn"
  varianceFromBaseline: "+£1.6bn (+15%)"
  varianceCause: "Inflation pressures on long-lead components; partnership cost-share renegotiation"
leadership:
  sro: "Air Vice-Marshal X, Director Future Combat Air System"
  sroChangeFlag: false
issuesAndRisks[0]:
  issue: "Tri-national governance complexity slowing key design decisions"
  severity: "high"
  category: "delivery"
  mitigationStated: "Joint board strengthened; quarterly principal-level reviews"
supplierContext:
  namedSuppliers:
    - { supplierName: "BAE Systems", scope: "Lead UK industrial partner — airframe and integration", contractStatus: "active" }
    - { supplierName: "Rolls-Royce", scope: "Powerplant", contractStatus: "active" }
    - { supplierName: "Leonardo UK", scope: "Sensors and electronics", contractStatus: "active" }
  vulnerabilitySignals:
    - "IPA flagged supply-chain capacity assumptions as requiring revalidation — implies supplier-base review may follow"
pursuitImplications[0]:
  implication: "Expect heightened evidence requirements for delivery-confidence claims on adjacent MoD digital and electronics tenders during FCAS rebaselining window."
  category: "evidence"
  rationale: "FCAS DCA deteriorated from amber-green to amber; departmental scrutiny of major-programme commercial controls typically intensifies after such moves."
```
