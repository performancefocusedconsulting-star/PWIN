# Extraction Template — Senior Leadership Announcement

This template is loaded when a source is classified as
`leadership_announcement`.

Senior leadership changes are the highest-value short-form intelligence
in a buyer dossier. A new Permanent Secretary, CEO, CDIO, or Director
General usually rebases the department's priorities, risk appetite, and
supplier preferences within 6–9 months. The template forces capture of
the substance — what is the new arrival's track record, what mandate
have they been given, whose departure caused the vacancy — not the
surface fact that "the department has a new permanent secretary".

---

## When to apply this template

Apply when the source is any of:

- A Cabinet Office press release announcing a permanent or interim
  appointment
- A Written Ministerial Statement on a senior appointment
- A department's own news item announcing a new senior leader
- A board appointment / non-executive director announcement
- A senior departure announcement (resignation, retirement, internal move)
- A reorganisation announcement that creates or abolishes senior roles

Do not apply to lower-grade promotions (Deputy Director and below in
central government, Band 7 and below in NHS) unless the role is
explicitly named in the dossier's `decisionUnitAssumptions`.

---

## Extraction depth requirement

Announcements are short (typically 1–3 pages). Full-read is always
expected. The depth requirement is on synthesis: connecting the
announcement to known programme priorities, fiscal context, and
predecessor history.

---

## Template schema

```json
{
  "extractionType": "leadership_announcement",
  "extractionAppliedAt": "ISO 8601",
  "appliedToSourceId": "SRC-nnn",

  "documentMeta": {
    "title": "string — exact document title",
    "buyerName": "string",
    "publisher": "Cabinet Office | department | NHS body | other",
    "publicationDate": "ISO 8601",
    "announcementType": "appointment | departure | role-restructure | acting-arrangement",
    "extractionDepth": "full-read | targeted-sections | summary-only"
  },

  "appointment": {
    "name": "string",
    "role": "string — exact role title",
    "isInterim": "boolean",
    "startDate": "ISO 8601 or null",
    "endDate": "ISO 8601 or null — for fixed-term or interim",
    "appointingAuthority": "string — Prime Minister, Secretary of State, Civil Service Commission, board, NHS England, etc.",
    "reportingLine": "string or null — to whom",
    "predecessor": {
      "name": "string or null",
      "departureReason": "retirement | resignation | internal-move | term-end | dismissal | unstated",
      "departureDate": "ISO 8601 or null",
      "tenureLength": "string or null — e.g. '4 years'"
    }
  },

  "incomingLeader": {
    "previousRole": "string or null — most recent prior role",
    "careerSummary": "string — concise career arc focused on relevant prior posts",
    "subjectMatterExpertise": ["string — substantive areas of expertise"],
    "knownPrioritiesOrPositions": ["string — what they're known for from prior roles"],
    "internalOrExternal": "internal-promotion | internal-lateral | other-civil-service | nhs-internal | private-sector | political | academic",
    "previousSupplierRelationships": ["string or null — known dealings with named suppliers"],
    "publicProfile": "string — high | medium | low (how visible they are in trade press / Hansard)"
  },

  "statedMandate": {
    "headlineFraming": "string — how the appointing authority framed the mandate",
    "namedPriorities": ["string — explicit priorities cited in the announcement"],
    "explicitProgrammes": ["string — programmes the new leader is expected to drive"],
    "structuralChanges": ["string — reorganisation, team-building, cultural change asks"],
    "reformLanguage": ["string — distinctive language about pace, ambition, transformation"]
  },

  "publicStatements": [
    {
      "statement": "string — direct quote",
      "speaker": "string — minister, predecessor, the new appointee themselves",
      "speakerRole": "string",
      "topic": "string"
    }
  ],

  "structuralImplications": {
    "rolesCreated": ["string"],
    "rolesAbolished": ["string"],
    "reportingChanges": "string or null",
    "coAppointments": ["string — other senior appointments announced at the same time"]
  },

  "decisionUnitImpact": {
    "isLikelyDecisionMaker": "boolean — true if the role appears in or near a buyer decision unit relevant to pursuit",
    "decisionLensInfluence": "commercial | operational | political | technical | financial | mixed | unknown",
    "ownsBudgetEnvelope": "string or null — what budget this role controls"
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
    "predecessorIdentified": "boolean — true if predecessor named or absence justified",
    "careerSummaryProvided": "boolean",
    "mandateLanguageCaptured": "boolean — true if at least one named priority extracted",
    "decisionUnitImpactAssessed": "boolean",
    "unextractedSections": ["string"]
  }
}
```

---

## Required dossier mappings

| Extracted content | Maps to dossier field | Lens | Operation |
|---|---|---|---|
| `appointment.name + role + startDate` | `organisationContext.seniorLeadership[]` | mandate | extend or replace (if predecessor previously listed) |
| `appointment.predecessor + this appointment together` | `organisationContext.recentChanges` | mandate, pressure | extend |
| `incomingLeader.knownPrioritiesOrPositions` | `decisionUnitAssumptions.perRoleInterests` (matched to role) | buying-behaviour | extend |
| `incomingLeader.previousSupplierRelationships[]` | `supplierEcosystem.summaryNarrative` (forward direction signal) | supplier-landscape | extend |
| `statedMandate.namedPriorities` | `strategicPriorities.summaryNarrative` (signals re-prioritisation) | pressure, mandate | extend |
| `statedMandate.explicitProgrammes` | `strategicPriorities.majorProgrammes[]` (status note) | pressure | extend |
| `statedMandate.reformLanguage` | `cultureAndPreferences.languageAndFraming` | risk-posture | extend |
| `publicStatements[]` | `strategicPriorities.publicStatementsOfIntent` | pressure | extend |
| `structuralImplications` (if material) | `organisationContext.recentChanges` | mandate | extend |
| `decisionUnitImpact` (where decisionMaker) | `decisionUnitAssumptions.perRoleInterests` or `dominantDecisionLens` | buying-behaviour | upgrade or extend |
| `pursuitImplications[]` | `pursuitImplications.implications[]` | pursuit-implications | extend |

---

## Quality check rules

The extraction is rejected if:

1. `appointment.name` or `appointment.role` is null — the announcement
   always names the appointee and role.
2. `appointment.predecessor.name` is null AND `appointment.predecessor.
   departureReason` is `unstated` — at least one must be captured, or
   absence must be flagged in `unextractedSections` with reason.
3. `incomingLeader.careerSummary` is empty — every leadership
   announcement provides at least one prior role.
4. `pursuitImplications[]` is empty — every senior change carries at
   least one. Common ones: new SRO career-risk window (over-evidence
   delivery confidence in their first 6 months); incoming priority
   shift (re-test the buyer-need hypothesis); predecessor's pet
   programme at risk of descoping; new private-sector entrant likely
   to bring known supplier preferences.
5. `dossierMappings` does not include the `pursuitImplications`
   mapping.

---

## Worked example (illustrative)

For a hypothetical "Cabinet Office — appointment of new HMRC Permanent
Secretary" announcement:

```
appointment:
  name: "Sir John Smith"
  role: "Permanent Secretary, HM Revenue & Customs"
  isInterim: false
  startDate: "2026-06-01"
  predecessor:
    name: "Dame Jane Doe"
    departureReason: "retirement"
    departureDate: "2026-05-31"
    tenureLength: "5 years"
incomingLeader:
  previousRole: "Director General, Customer Strategy and Tax Design, HMRC"
  careerSummary: "27 years in HMRC, including Customer Strategy DG (2022-26),
    Operational Excellence DG (2018-22), prior tax-policy roles in HMT (2010-14)..."
  subjectMatterExpertise: ["digital tax administration", "customer-experience design", "operational resilience"]
  knownPrioritiesOrPositions: ["Single Customer Account programme champion", "advocate for in-house digital build vs outsourced"]
  internalOrExternal: "internal-promotion"
statedMandate:
  headlineFraming: "Continue the digital transformation of tax administration while delivering productivity savings"
  namedPriorities: ["Single Customer Account rollout", "MTD ITSA delivery", "5% efficiency by FY28"]
  reformLanguage: ["AI-enabled", "customer-centric", "frictionless"]
decisionUnitImpact:
  isLikelyDecisionMaker: true
  decisionLensInfluence: "operational"
  ownsBudgetEnvelope: "HMRC entire DEL (£5.2bn FY26-27)"
pursuitImplications[0]:
  implication: "Expect supplier preference toward in-house build augmentation rather than full outsourced delivery; major-system replacements unlikely to be tendered in first 12 months."
  category: "stance"
  rationale: "Incoming Perm Sec is on record as advocate for in-house digital build during prior DG role"
pursuitImplications[1]:
  implication: "Over-evidence productivity savings from any proposed service line — incoming mandate places explicit 5% efficiency target."
  category: "evidence"
  rationale: "Stated mandate names productivity target as a top-three priority"
```
