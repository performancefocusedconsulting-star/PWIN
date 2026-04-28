# Source Inventory — Named Must-Check Documents by Organisation Type

This reference tells the skill **which specific named documents to go and find**
before synthesis in build and refresh modes. It is a checklist, not a
description of what to do with those documents. Once found, classify each
source against `source-classification.md` and apply the appropriate extraction
template if one exists.

**This is the companion to the classification matrix.** The classification
matrix answers "what do I do WITH this document?" This inventory answers
"which documents must I check before I start writing?"

Hard Rule 18 requires this inventory to be consulted at the start of every
BUILD and REFRESH run. Record which checks were attempted and which were
skipped (and why) in `meta.sourceInventoryTrace`.

---

## How to use this inventory

1. Identify the buyer's **organisation type** from the table below.
2. Work through the **Tier 1–4 checklist** for that type.
3. For each named document or source, attempt to locate it.
4. If found: add to source register, classify, apply template if available.
5. If not found or inaccessible: record in `sourceRegister.gaps` with the
   specific document name and why it was not retrieved.
6. Record the full traversal in `meta.sourceInventoryTrace` (see schema in
   `output-schema.md`).

A document need not be fully read to be registered — a confirmed "not
available" is a legitimate finding. Gaps should name the document, not
say "search yielded nothing."

---

## Organisation type index

| Type label | Applies to |
|---|---|
| [MoD family](#mod-family) | Ministry of Defence, Defence Digital, DE&S, DIO, Dstl, UKSC, DSSC, SDA, service commands |
| [Central government department](#central-government-department) | Cabinet-level departments and their arm's-length bodies (except MoD) |
| [Home Office family](#home-office-family) | Home Office, UKVI, Border Force, Immigration Enforcement, DBS, Serious Fraud Office |
| [MoJ family](#moj-family) | Ministry of Justice, HMPPS, HMCTS, Legal Aid Agency, OPG |
| [HMRC / DWP](#hmrc--dwp) | HMRC, DWP, their agencies |
| [NHS / health](#nhs--health) | NHS England, ICBs, NHS trusts, NHSX-era programmes |
| [Local government](#local-government) | County, district, metropolitan, unitary, London borough councils and combined authorities |
| [Devolved government](#devolved-government) | Scottish Government, Welsh Government, NI Executive and their agencies |

When a buyer spans multiple types (e.g. NHS England is both a national
body and a major digital commissioner), apply both type checklists and
de-duplicate.

---

## MoD family

Applies to: Ministry of Defence (parent), Defence Digital, DE&S, DIO,
Dstl, UK Strategic Command (UKSC), Defence and Security Accelerator (DASA),
Service Command HQs (Navy, Army, Air).

> For Defence Digital and the service sub-organisations, always run the
> parent MoD Tier 1 checks PLUS the sub-org-specific checks below.
> Defence Digital does not publish its own Annual Report.

### Tier 1 — MoD's own material

| Document | Where to find it | Dossier sections | Lenses | Template |
|---|---|---|---|---|
| MoD Annual Report and Accounts (latest financial year) | search: `site:gov.uk "ministry of defence" "annual report and accounts"` | organisationContext, strategicPriorities, commercialAndRiskPosture, risksAndSensitivities | money, pressure, risk-posture | `annual-report.md` |
| Strategic Defence Review 2025 / Defence White Paper | search: `"strategic defence review" 2025 site:gov.uk` | strategicPriorities, commissioningContextHypotheses | mandate, pressure | `departmental-plan.md` |
| Defence Industrial Strategy (2021 or successor) | search: `"defence industrial strategy" site:gov.uk` | strategicPriorities, procurementBehaviour, supplierEcosystem | mandate, buying-behaviour, supplier-landscape | `commercial-strategy.md` |
| MOD Acquisition Pipeline (Excel file on "Doing Business with Defence") | search: `"acquisition pipeline" site:gov.uk/guidance/doing-business-with-defence` — download the Excel | commissioningContextHypotheses, strategicPriorities, supplierEcosystem | pressure, buying-behaviour | `acquisition-pipeline.md` |
| Defence Sourcing Portal (DSP) pipeline publications | browse: `find-tender.service.gov.uk` filter buyer=Ministry of Defence; also check `find-tender.service.gov.uk/notices/planning` | commissioningContextHypotheses, procurementBehaviour | buying-behaviour, pressure | — |
| Defence Digital Strategy (most recent) | search: `"defence digital strategy" site:gov.uk` | strategicPriorities, cultureAndPreferences | pressure, mandate | `digital-strategy.md` |
| Defence AI Strategy | search: `"defence artificial intelligence strategy" site:gov.uk` | strategicPriorities, cultureAndPreferences | pressure, risk-posture | `digital-strategy.md` |
| Cyber Security Strategy (Defence-specific) | search: `"ministry of defence" "cyber security strategy" site:gov.uk` | commercialAndRiskPosture, strategicPriorities | risk-posture | `cyber-strategy.md` |
| MoD Organogram (most recent, March or September snapshot) | search: `site:gov.uk/government/publications "ministry of defence" "organogram"` | organisationContext, decisionUnitAssumptions | mandate | — |
| "Doing Business with Defence" procurement page | `gov.uk/guidance/doing-business-with-defence` | procurementBehaviour | buying-behaviour | — |
| JSP 936 (Defence Procurement Manual) — if publicly accessible | search: `JSP 936 site:gov.uk` | procurementBehaviour, commercialAndRiskPosture | buying-behaviour, risk-posture | — |

**Defence Digital-specific additions (always check when buyer is Defence Digital):**

| Document | Where to find it | Sections | Lenses |
|---|---|---|---|
| Defence Digital annual priorities / programme updates | search: `"defence digital" site:gov.uk` (blog posts, press releases) | strategicPriorities, commissioningContextHypotheses | pressure, mandate |
| Skynet (SK6 WSS) programme status | search: `"Skynet 6" OR "SK6 WSS" site:gov.uk` + NISTA report | strategicPriorities, commissioningContextHypotheses | pressure |
| MODNET / NGCN programme references | search: `MODNET OR NGCN site:gov.uk` + parliamentary answers | commissioningContextHypotheses | pressure |
| Future C4I / F-IUS programme references | search: `"Future C4I" OR "F-IUS" site:gov.uk` + parliamentary answers | commissioningContextHypotheses | pressure |
| Defence Digital organogram (separate from parent MoD) | search: `"defence digital" "organogram" site:gov.uk` | organisationContext, decisionUnitAssumptions | mandate |

### Tier 2 — Centre-of-government sources

| Document | Where to find it | Sections | Lenses | Template |
|---|---|---|---|---|
| NISTA Annual Report (formerly GMPP / IPA GMPP — renamed April 2025) | search: `"NISTA" OR "government major projects portfolio" site:gov.uk` | strategicPriorities, risksAndSensitivities, supplierEcosystem | pressure, risk-posture, supplier-landscape | `gmpp-entry.md` |
| Spending Review — MoD settlement tables | search: `"spending review" "ministry of defence" site:gov.uk` + HMT supporting documents | commercialAndRiskPosture, commissioningContextHypotheses | money, pressure | `spending-review-settlement.md` |
| Main Supply Estimates — Defence (annual) | search: `"defence estimates" site:gov.uk` | commercialAndRiskPosture, organisationContext | money | — |
| Single Source Regulations Office (SSRO) annual report | search: `"SSRO" "annual report" site:gov.uk` | procurementBehaviour, commercialAndRiskPosture | buying-behaviour, risk-posture | — |

### Tier 3 — External scrutiny

| Document | Where to find it | Sections | Lenses | Template |
|---|---|---|---|---|
| Defence Committee inquiry reports (current Parliament) | `committees.parliament.uk/committee/24/defence-committee/publications/` | risksAndSensitivities, strategicPriorities | pressure, risk-posture | `nao-pac-report.md` |
| PAC reports on MoD programmes | `committees.parliament.uk/committee/127/public-accounts-committee/publications/` filter "defence" | risksAndSensitivities, commercialAndRiskPosture, supplierEcosystem | risk-posture, pressure | `nao-pac-report.md` |
| NAO VfM reports on MoD and Defence Digital | search: `site:nao.org.uk "ministry of defence" OR "defence digital"` | risksAndSensitivities, commercialAndRiskPosture, supplierEcosystem | risk-posture, pressure | `nao-pac-report.md` |
| Hansard written answers — defence topics | search: `hansard.parliament.uk` filter written answers, keyword = programme name or "Defence Digital" | strategicPriorities, commissioningContextHypotheses, decisionUnitAssumptions | pressure, mandate | `parliamentary-answers.md` |
| techUK Defence / DASA / ADS published proceedings | search: `techuk.org "defence" OR `adsgroup.org.uk` | cultureAndPreferences, procurementBehaviour | buying-behaviour, supplier-landscape | `industry-engagement-deck.md` |
| RUSI reports on defence programmes and procurement | search: `rusi.org "defence digital" OR "defence procurement"` | strategicPriorities, risksAndSensitivities | pressure, risk-posture | — |

### Tier 4 — Market and procurement data

| Source | How to query it | Sections | Lenses |
|---|---|---|---|
| FTS notices — parent MoD | find-tender: buyer = "Ministry of Defence" — last 3 years | procurementBehaviour, supplierEcosystem | buying-behaviour, supplier-landscape |
| FTS notices — Defence Digital sub-org | find-tender: buyer = "Defence Digital" — last 3 years | procurementBehaviour, supplierEcosystem | buying-behaviour |
| FTS notices — DE&S | find-tender: buyer = "Defence Equipment and Support" | procurementBehaviour, supplierEcosystem | buying-behaviour |
| FTS notices — Strategic Command | find-tender: buyer = "United Kingdom Strategic Command" | procurementBehaviour, supplierEcosystem | buying-behaviour |
| CCS Framework call-offs — TEPAS 2 (RM6098) | FTS: framework reference "RM6098", buyer = MoD family | procurementBehaviour, supplierEcosystem | buying-behaviour, supplier-landscape |
| CCS Framework call-offs — Tech Services 3 (RM6100) | FTS: framework reference "RM6100", buyer = MoD family | procurementBehaviour, supplierEcosystem | buying-behaviour |
| CCS Framework call-offs — Network Services 3 (RM6116) | FTS: framework reference "RM6116", buyer = MoD family | procurementBehaviour, supplierEcosystem | buying-behaviour |
| CCS Framework call-offs — MVDS (RM6261) | FTS: framework reference "RM6261", buyer = MoD family | procurementBehaviour, supplierEcosystem | buying-behaviour |
| DIPS (Digital and IT Professional Services) call-offs | FTS: framework reference "DIPS", buyer = MoD family | procurementBehaviour, supplierEcosystem | buying-behaviour |
| MCF 4 (Management Consultancy Framework 4) call-offs | FTS: framework reference "RM6187", buyer = MoD family | procurementBehaviour, supplierEcosystem | buying-behaviour |
| Spend transparency CSVs — MoD £25k+ | search: `site:gov.uk "ministry of defence" "transparency" "spend"` | procurementBehaviour, supplierEcosystem | buying-behaviour, supplier-landscape |

---

## Central government department

Applies to: any Cabinet-level ministerial department not covered by a
more specific type above (e.g. DHSC, DfT, DESNZ, FCDO, DSIT, DfE, MHCLG,
Defra, DCMS, CO, HMT). Also applies to major arm's-length bodies (Ofsted,
Environment Agency, DVLA, DVSA, Companies House, UKSA, etc.).

### Tier 1

| Document | Where to find it | Sections | Template |
|---|---|---|---|
| Annual Report and Accounts | search: `site:gov.uk "[department name]" "annual report and accounts"` | organisationContext, strategicPriorities, money, risk | `annual-report.md` |
| Outcome Delivery Plan / Single Departmental Plan | search: `site:gov.uk "[department name]" "outcome delivery plan" OR "single departmental plan"` | strategicPriorities, commissioningContextHypotheses | `departmental-plan.md` |
| Digital / Data strategy | search: `site:gov.uk "[department name]" "digital strategy" OR "data strategy"` | strategicPriorities, cultureAndPreferences | `digital-strategy.md` |
| Commercial strategy (if published) | search: `site:gov.uk "[department name]" "commercial strategy" OR "procurement strategy"` | procurementBehaviour, commercialAndRiskPosture | `commercial-strategy.md` |
| Workforce / People plan | search: `site:gov.uk "[department name]" "workforce strategy" OR "people plan"` | commissioningContextHypotheses, cultureAndPreferences | `workforce-strategy.md` |
| Cyber strategy (if published separately) | search: `site:gov.uk "[department name]" "cyber security strategy"` | commercialAndRiskPosture | `cyber-strategy.md` |
| Organogram (twice-yearly) | search: `site:gov.uk/government/publications "[department name]" "organogram"` | organisationContext, decisionUnitAssumptions | — |
| Procurement / "working with us" page | search: `site:gov.uk "[department name]" "working with us" OR "procurement"` | procurementBehaviour | — |

### Tier 2

| Document | Where to find it | Template |
|---|---|---|
| Spending Review settlement | search: `"spending review" "[department name]" site:gov.uk` | `spending-review-settlement.md` |
| NISTA Major Projects entry (if department has major programmes) | search: `"NISTA" OR "government major projects portfolio" site:gov.uk` | `gmpp-entry.md` |
| Main Estimates | search: `"[department name] estimates" site:parliament.uk` | — |

### Tier 3

| Document | Where to find it | Template |
|---|---|---|
| Relevant select committee reports | `committees.parliament.uk` — filter by relevant committee and department | `nao-pac-report.md` |
| PAC reports | `committees.parliament.uk/committee/127` | `nao-pac-report.md` |
| NAO VfM reports | `nao.org.uk` — search department name | `nao-pac-report.md` |
| Hansard written answers | `hansard.parliament.uk` — keyword = programme names or department | `parliamentary-answers.md` |

### Tier 4

| Source | How to query |
|---|---|
| FTS notices — parent department | buyer = "[department canonical name]" |
| FTS notices — agency sub-orgs | buyer = "[agency name]" (run for each known sub-org) |
| Contracts Finder | same search, catches below-threshold awards |
| CCS framework call-offs | FTS framework references relevant to the department's main spend categories |
| Spend transparency CSVs | search: `site:gov.uk "[department name]" "spend" "transparency"` |

---

## Home Office family

Applies to: Home Office (parent), UK Visas and Immigration (UKVI), Border
Force, Immigration Enforcement, Disclosure and Barring Service (DBS),
Serious Fraud Office.

> Home Office, UKVI, Border Force, and Immigration Enforcement publish
> contracts under the parent Home Office name. The £25k spend transparency
> CSV (available monthly) is the primary route to sub-org spend visibility
> because it breaks out by expense area.

### Tier 1

All central-government-department Tier 1 checks, PLUS:

| Document | Where to find it | Note |
|---|---|---|
| FBIS (Futures Border and Immigration System) programme publications | search: `"FBIS" site:gov.uk` | Links UKVI's major digital programme |
| Home Office Biometrics programme documents | search: `"Home Office Biometrics" site:gov.uk` | Key incumbent landscape signal |
| ICIBI inspection reports (Independent Chief Inspector of Borders and Immigration) | `gov.uk/government/organisations/independent-chief-inspector-of-borders-and-immigration` | Tier 3 signal, listed here because often missed |
| Home Office £25k spend CSV — current financial year | search: `site:gov.uk "home office" "transparency" "spend data" csv` | Best sub-org route for UKVI / Border Force |

### Tier 3 additions

| Document | Where |
|---|---|
| ICIBI thematic inspection reports | `gov.uk/government/organisations/independent-chief-inspector-of-borders-and-immigration/publications` |
| Prisons and Probation Ombudsman (cross-reference for immigration detention) | `ppo.gov.uk` |

---

## MoJ family

Applies to: Ministry of Justice (parent), HMPPS (His Majesty's Prison and
Probation Service), HMCTS (His Majesty's Courts and Tribunals Service),
Legal Aid Agency, Official Solicitor, Office of the Public Guardian.

> MoJ, HMPPS, and HMCTS publish contracts under the parent MoJ name.
> HMCTS does publish some standalone tender and award notices.
> Three separate spend transparency channels: MoJ HQ, HMCTS standalone,
> and eleven arm's-length-body files.

### Tier 1

All central-government Tier 1 checks, PLUS:

| Document | Note |
|---|---|
| HMPPS annual report | Published separately: search `site:gov.uk "HMPPS" "annual report"` |
| HMCTS reform programme publications | Search `site:gov.uk "HMCTS reform"` — names the key digital contracts |
| MoJ Prisons Strategy White Paper (or current successor) | `site:gov.uk "prisons strategy"` |
| MoJ £25k spend — all three channels | MoJ HQ, HMCTS, and each arm's-length body separately |

### Tier 3 additions

| Document | Where |
|---|---|
| Prisons and Probation Ombudsman reports | `ppo.gov.uk` |
| HM Inspectorate of Prisons | `justiceinspectorates.gov.uk/hmiprisons` |
| HM Inspectorate of Courts and Tribunals | `justiceinspectorates.gov.uk/hmicfrs` (cross-check) |

---

## HMRC / DWP

Applies to: HMRC (and Valuation Office Agency, VOA), DWP (and The
Pensions Regulator, Child Maintenance Service, Health and Safety Executive).

> Both are high-volume digital commissioners. HMRC runs Making Tax
> Digital; DWP runs Universal Credit infrastructure. Both are
> frequent users of G-Cloud and Digital Outcomes frameworks.

### Tier 1 additions (over standard)

| Document | Note |
|---|---|
| Making Tax Digital programme updates (HMRC) | `site:gov.uk "making tax digital" progress` |
| Universal Credit programme status (DWP) | `site:gov.uk "universal credit" "programme" site:gov.uk` |
| DWP Digital strategy | Published separately from DWP corporate plan |
| DWP / HMRC £25k spend CSVs | Published monthly |

---

## NHS / health

Applies to: NHS England, Integrated Care Boards (ICBs), NHS trusts,
NHSE-sponsored programmes (NHSX-era, Frontline Digitisation, etc.).

> NHS procurement routes include NHS SBS (Shared Business Services)
> and NHSE-specific frameworks as well as CCS. Local authority public
> health commissioning (post-2022 transfer) often passes through the
> council, not the ICB.

### Tier 1

| Document | Where | Template |
|---|---|---|
| NHS England Annual Report | `england.nhs.uk` — publications | `annual-report.md` |
| NHS Long Term Plan / NHS Strategy (most recent) | `longtermplan.nhs.uk` | `departmental-plan.md` |
| ICB Joint Forward Plan (for ICB buyers) | `nhse` ICB publication page | `departmental-plan.md` |
| Integrated Care Strategy (for ICB buyers) | Local authority and ICB sites | `departmental-plan.md` |
| NHS Digital / NHSX digital transformation publications | `digital.nhs.uk` | `digital-strategy.md` |
| NHS commercial framework strategy | search: `NHS England "commercial strategy"` | `commercial-strategy.md` |
| NHS Procurement Transformation Programme publications | `england.nhs.uk/procurement` | — |
| Trust board papers (for trust-level buyers) | Individual trust websites — "board papers" section | — |

### Tier 3 additions

| Document | Where |
|---|---|
| CQC inspection reports (for trust buyers) | `cqc.org.uk` — search trust name |
| PAC reports on NHS digital programmes | `committees.parliament.uk/committee/127` |
| NAO reports on NHS digital / NHS Test and Trace / NHS PFI | `nao.org.uk` |
| Health and Social Care Committee | `committees.parliament.uk` |

### Tier 4 additions

| Source | Note |
|---|---|
| NHS SBS framework call-offs | NHS Shared Business Services portal |
| NHSE procurement framework call-offs | `england.nhs.uk` procurement pages |

---

## Local government

Applies to: county, district, metropolitan, unitary, London borough
councils, and combined authorities.

> Local authorities publish their own contract registers (often above £500
> or £5k, not just £25k). These are more granular than FTS and often
> the best route to named supplier and spend data.

### Tier 1

| Document | Where | Template |
|---|---|---|
| Corporate Plan / Council Plan | Council website — "About the council" or "policies" | `departmental-plan.md` |
| Annual Report (where published) | Council website | `annual-report.md` |
| Digital strategy | search: `"[council name]" "digital strategy"` | `digital-strategy.md` |
| Commercial / procurement strategy | search: `"[council name]" "procurement strategy"` | `commercial-strategy.md` |
| Contract register (£500+ or £5k+) | Council website — "transparency" or "spending" — often CSV | — |
| Cabinet / Executive papers (major contract decisions) | Council committee management system | — |

### Tier 2

| Document | Note |
|---|---|
| Local Government Finance Settlement | MHCLG annual settlement — sets the funding envelope |
| UKSPF / Levelling-Up Fund allocations | Where relevant to programme scope |

### Tier 3

| Document | Note |
|---|---|
| Ofsted / CQC inspection (children's services, adult social care) | Where service transformation is the buy |
| Local Government Ombudsman reports | `lgo.org.uk` — signals risk culture |

---

## Devolved government

Applies to: Scottish Government and its agencies (Transport Scotland, Social
Security Scotland, etc.), Welsh Government and its agencies, NI Executive.

> Devolved governments have separate procurement regimes and framework
> agreements. Scottish Government uses Public Contracts Scotland (PCS)
> and the Procurement Reform (Scotland) Act 2014. Wales uses Sell2Wales.
> NI uses eSourcing NI.

### Key additions over standard central-government checklist

| Document | Where |
|---|---|
| Scottish Government / Welsh Government / NI Executive budget (equivalent of UK Spending Review) | Scottish Budget, Welsh Budget, NI Budget — published by respective governments |
| Programme for Government (Scotland / Wales) — equivalent of ODP | Scottish Government website / Welsh Government website |
| Scottish Procurement framework call-offs | Public Contracts Scotland (PCS) — `publiccontractsscotland.gov.uk` |
| Wales Procurement Policy framework notices | Sell2Wales — `sell2wales.gov.wales` |
| Auditor General / Audit Scotland / Wales Audit Office reports | `audit.scot` / `audit.wales` |

---

## Notes

- **Document not found** is a valid finding. Always record attempted
  checks and confirmed gaps by document name in
  `sourceRegister.gaps`. "Search yielded nothing" without naming the
  document being searched for is not acceptable.
- **Freshness.** Annual reports more than 18 months old should be flagged
  stale. Spending Review settlements are superseded by the next review.
  Organograms are refreshed twice yearly — use only the most recent.
- **Sub-organisation lookups.** For publish-at-parent departments (MoD,
  Home Office, MoJ, DfE), always run FTS searches for BOTH the parent
  AND the known sub-organisation names. The parent search alone will miss
  the sub-org picture.
- **Injection of documents not in this inventory.** Documents the user
  injects via INJECT mode are classified against `source-classification.md`
  regardless of whether they appear in this inventory. This inventory
  governs the skill's own proactive search behaviour, not what it does
  with documents it is given.
