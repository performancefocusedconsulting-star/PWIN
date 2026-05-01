# Sub-organisation contract registers for UK central government

**Author:** Research workstream
**Date:** 2026-04-28
**Companion to:** `2026-04-28-sub-org-intel-sources.md`
**Scope:** Find every published source of UK central-government **contract-level** data at **sub-organisation** level for the priority sub-orgs in the Ministry of Justice, Home Office, and Ministry of Defence families.

---

## 0. Why this report exists

The earlier research pass said: ingest the monthly £25,000 spend transparency CSVs and you fix the sub-organisation gap. We have now done that and confirmed the data works — but the data is a **spend view** (payment-by-payment), not a **contract view** (contract title, supplier, total value, start, expiry, procurement method, lots, bidders). Senior consultants making bid pursuit decisions need the contract view. They are asking "who holds the £100m HMPPS prison facilities contract that expires next year, and how was it bought?" — not "how much did HMPPS pay G4S in March 2025?".

This report establishes how much of that contract view is actually publicly available at sub-organisation level.

---

## 1. Executive summary

| Department family | Best contract-level sources at sub-org level | Realistic completeness | Comment |
|---|---|---|---|
| **Ministry of Justice** (HMPPS, HMCTS, LAA, OPG, Probation Service) | Find a Tender + Contracts Finder (FTS+CF) buyer field, MoJ annual report and accounts (ARA), HMPPS / HMCTS / LAA separate ARAs, `data.justice.gov.uk/contracts` for major outsourced services, NAO reports | **Medium-to-high.** MoJ is the cleanest of the three families. HMPPS and HMCTS sometimes appear in their own right as the FTS buyer; major outsourced contracts (private prisons, electronic monitoring, prisoner escort, asylum interpreting, legal aid) have rich coverage in NAO and parliamentary papers. | LAA contracts (legal aid panels) are mostly bulk panel awards rather than individual procurements — different shape of data. |
| **Home Office** (UKVI, Border Force, HMPO, Immigration Enforcement, DBS, UKVIP) | FTS+CF with parent buyer "Home Office", monthly £25k spend with Entity column, Home Office ARA, NAO asylum and FBIS reports, ICIBI inspection reports, trade press | **Low-to-medium.** Home Office is the worst of the three for sub-org contract attribution. The £25k spend is the only structured source that names UKVI / Border Force / HMPO / Immigration Enforcement separately. The contract notices themselves overwhelmingly say "Home Office" with sub-org buried in the title or specification. | DBS publishes some commercial information separately as a non-departmental public body. |
| **Ministry of Defence** (Defence Digital, DE&S, Dstl, DIO, Strategic Command, single services, SDA) | DE&S, Dstl, DIO and SDA each publish their own annual report and accounts; DE&S and SDA are major buyers in their own right on FTS; SSRO publishes single-source defence contract aggregate statistics; MOD Trade, Industry and Contracts annual statistics name top suppliers; NISTA (former GMPP) names the major programme owner; trade press is strong | **Medium.** DE&S, Dstl, DIO and SDA do appear as named FTS buyers (good), so contract-level data at this level is real. Defence Digital sits inside Strategic Command and rarely gets its own buyer attribution — a known gap. SSRO single-source register is **not public at contract level** — only aggregates. | The pure-defence contracts are the most useful target because DE&S is named as buyer in its own right. Defence Digital is the residual gap. |

**The headline conclusion:** there is no public, structured, downloadable contract register at sub-organisation level for any of the three families. The contract view has to be **assembled** from FTS+CF (where the sub-org is sometimes the named buyer) plus narrative sources (annual reports, NAO, parliamentary, trade press) plus the £25k spend layer to confirm operational ownership and rough start/end dates. The Procurement Act 2023 transparency regime is the most likely future unlock — see section 4 — but its current granularity is no improvement on the predecessor regime for sub-org attribution.

**Single biggest practical win available now:** rebuild our existing Find a Tender + Contracts Finder buyer canonical layer to recognise that DE&S, Dstl, DIO, SDA, HMPPS, HMCTS, LAA, OPG, and DBS **already publish notices in their own name** as buyer. We are losing this signal because the buyer canonical layer maps them all to the parent. Re-keying the canonical layer to keep the sub-org as the buying entity (and the parent as a separate "department family" relationship) is a code change, not a new data source. This is the cheapest, biggest single fix.

---

## 2. Source-by-source catalogue

Each source is documented with explicit yes/no on the contract-view fields.

### 2.1 Find a Tender Service (FTS) + Contracts Finder (CF) — the core feed we already ingest

- **URL (FTS):** https://www.find-tender.service.gov.uk/
- **URL (CF):** https://www.contractsfinder.service.gov.uk/
- **API documentation:** https://www.find-tender.service.gov.uk/Developer/Documentation
- **What it publishes:** Notices in OCDS format (release packages and record packages). Notice fields cover contract title, supplier, value, start date, end date, procurement method, lots, CPV codes, buyer.
- **Contract title:** Yes
- **Supplier:** Yes (post-award notices)
- **Total value:** Yes
- **Start date:** Yes (when published)
- **End date / expiry:** Yes (when published)
- **Procurement method:** Yes
- **Lot structure:** Yes
- **Bidder count:** Sometimes (not on every notice, more reliable since the Procurement Act 2023 came into force 24 February 2025)
- **Sub-org attribution:** **Partial and inconsistent.** Some sub-organisations publish in their own right — HMPPS, HMCTS, LAA, OPG, DBS, DE&S, Dstl, DIO, SDA all appear as the named buyer on at least some notices. Others (UKVI, Border Force, HMPO, Immigration Enforcement, Defence Digital) overwhelmingly publish under the parent department name with the sub-org only mentioned in the contract title or specification. The buyer field is freeform text and the same body appears under many spellings.
- **Cadence:** Real-time / hourly
- **Access:** Free, OCDS API, also available as the Open Contracting Partnership weekly bulk file (which we already use)
- **Coverage scope:** All contracts above £10,000 (central government) and £25,000 (wider public sector) — but compliance is patchy, especially below the higher EU-thresholds and for the call-offs from frameworks
- **Quality issues:** Buyer name is freeform text, supplier names are freeform, framework values are notional ceilings not realised draw-down, sub-org attribution drift inside the buyer field

### 2.2 Departmental £25k spend transparency CSVs (monthly)

- **URL pattern:** `https://www.gov.uk/government/collections/<department>-spend-data` (each department has its own collection page)
- **What it publishes:** Every transaction settled above £25k. Columns include Department, **Entity** (the sub-org), Date, Expense Type, Expense Area, Supplier, Transaction number, Amount.
- **Contract title:** No (only a free-text "Expense Type" / "Expense Area" classification)
- **Supplier:** Yes
- **Total value:** No (only a single payment)
- **Start date:** No (only the payment date — first payment is a weak proxy for contract start)
- **End date:** No (absence of further payments is a weak proxy for end)
- **Procurement method:** No
- **Lot structure:** No
- **Bidder count:** No
- **Sub-org attribution:** **Yes — this is its strongest feature.** Home Office uses the Entity column properly (UKVI, Border Force, HMPO, Immigration Enforcement, DBS appear distinctly). MoJ uses Entity to break out HMPPS, HMCTS, LAA, OPG. MOD uses Top Level Budget holders (Army, Navy, RAF, Strategic Command, DE&S, Defence Infrastructure Organisation, Defence Nuclear Organisation) — Defence Digital is buried inside Strategic Command.
- **Cadence:** Monthly, 1–3 month lag
- **Access:** Free CSV
- **Coverage scope:** All transactions above £25k that the department settled. Misses contracts that exist on paper but haven't been drawn down yet, and misses payment splits made at sub-£25k granularity
- **Quality issues:** Supplier names freeform across spellings, Entity values vary across months, format inconsistencies

### 2.3 `data.justice.gov.uk/contracts` — Justice Data contracts pages

- **URL:** https://data.justice.gov.uk/contracts (and per-service pages e.g. `/contracts/electronic-monitoring`, `/contracts/bass`)
- **What it publishes:** Curated narrative dashboards on a small set of major outsourced MoJ services — the Community Accommodation Service (CAS-1, CAS-2, CAS-3), Electronic Monitoring, Prisoner Escort and Custody Services, Approved Premises. Each page describes the service, names the current providers, gives the current contract dates, and links to the underlying notices.
- **Contract title:** Yes (named services)
- **Supplier:** Yes
- **Total value:** Sometimes (not consistently published — narrative figures, not structured)
- **Start date:** Yes (narrative)
- **End date:** Yes (narrative)
- **Procurement method:** No
- **Lot structure:** Sometimes (the regional split for asylum / accommodation contracts)
- **Bidder count:** No
- **Sub-org attribution:** Yes — pages are explicitly tagged HMPPS or HMCTS
- **Cadence:** Updated when contracts change (ad-hoc, not a regular release)
- **Access:** Free HTML page, no structured download, no API
- **Coverage scope:** **Very narrow.** Only the headline-grabbing outsourced services. Not a comprehensive contract register. Useful as a cross-check that confirms incumbents and dates for those few services, not as a primary data feed.
- **Quality issues:** Hand-curated, scope creep limited, no structured field definitions

### 2.4 SSRO Single Source Defence Contract data (DefCARS)

- **URL:** https://www.ssro.gov.uk/
- **What it publishes:** The SSRO holds detailed contract reports through DefCARS (Defence Contract Analysis and Reporting System), but **the contract-level data is not public**. The SSRO publishes only aggregate annual statistics (number of qualifying single-source defence contracts, total value, contracted vs target profit etc.).
- **Contract title:** No (public)
- **Supplier:** No (public — only aggregate)
- **Total value:** Aggregate only
- **Start date:** No (public)
- **End date:** No (public)
- **Procurement method:** Single-source by definition (since it's the SSRO regime)
- **Lot structure:** No
- **Bidder count:** N/A (single-source)
- **Sub-org attribution:** No public attribution. SSRO holds the buying body internally but does not publish it at contract level.
- **Cadence:** Annual aggregate publication
- **Access:** Aggregate stats are free; contract-level data is not available except through FOI (and FOIs are routinely refused on commercial sensitivity grounds)
- **Coverage scope:** Only Qualifying Defence Contracts (single-source, value above £5m) and Qualifying Sub-Contracts (above £25m). Includes most of MOD's heavy single-source spend — submarines, complex weapons, ISTAR — but is not relevant to competed defence work
- **Quality issues:** Public face is aggregate-only. The detail exists but is not part of the open data ecosystem.

**Implication:** Single-source defence contracts (which include most submarine, complex weapons, and AWE work — much of the long-tail Strategic Command and DE&S spend) have **no public contract-level register at all**. The only paths to that data are FTS post-award notices (which sometimes exist for SSRO contracts) and trade press / NAO / parliamentary reports.

### 2.5 MOD Trade, Industry and Contracts annual statistics

- **URL pattern:** https://www.gov.uk/government/statistics/mod-trade-industry-and-contracts-2024 (and similar for each year), index at https://www.gov.uk/government/collections/defence-trade-and-industry-index
- **What it publishes:** MOD's annual accredited statistical bulletin on its industry spend. Covers total core MOD spend, competitive vs non-competitive split, payments to top suppliers (named), counts and values of new contracts placed, PFI spend, major equipment projects.
- **Contract title:** No (only programme-level for major equipment)
- **Supplier:** Yes (named top suppliers)
- **Total value:** Aggregate per supplier, per year
- **Start date / end date:** Sometimes for major equipment projects
- **Procurement method:** Aggregate competitive vs single-source split only
- **Lot structure:** No
- **Bidder count:** No
- **Sub-org attribution:** Partial — major equipment projects are named (e.g. Type 26 frigate, Skynet 6, Morpheus) and you can infer the owning command. Top supplier table is at MOD-wide level, not broken down by buying command.
- **Cadence:** Annual (revised in March of the following year)
- **Access:** Free PDF and ODS data tables
- **Coverage scope:** All MOD spend
- **Quality issues:** Aggregated; useful for narrative context and trend, not for contract-level reconstruction

### 2.6 NISTA (formerly GMPP) Major Projects data

- **URL:** https://www.gov.uk/government/collections/major-projects-data and the latest NISTA Annual Report at https://www.gov.uk/government/publications/nista-annual-report-2024-2025
- **What it publishes:** Project-level data for the 213 major projects in the GMPP at March 2025 (reducing to ~80 from April 2026). Whole-life cost, sponsor department, delivery confidence rating, schedule. From the 2024-25 report onwards data is downloadable from a single dashboard spreadsheet.
- **Contract title:** No (project title only)
- **Supplier:** No (not in the public data; named in the underlying programme reports)
- **Total value:** Whole-life cost (not contract value)
- **Start date / end date:** Project schedule, not contract schedule
- **Procurement method:** No
- **Sub-org attribution:** **Yes** — sponsor department and (for MOD) owning command. Skynet 6 is tagged Defence Digital; FBIS is tagged Home Office Migration and Borders Technology Portfolio; Atlas is tagged Home Office.
- **Cadence:** Annual snapshot (March), published mid-year
- **Access:** Free PDF and downloadable spreadsheet
- **Coverage scope:** Top ~200 major projects only (reducing to ~80). Misses most of the long tail.
- **Quality issues:** Project view, not contract view. Useful for "who runs the £3.8bn programme" but not for "what is the start and end date of each underlying contract".

### 2.7 Departmental Annual Reports and Accounts (ARAs)

Multiple URLs, indexed under each department's organisation page on gov.uk. Key ones for our test cases:

- MoJ ARA 2024-25 — names top suppliers and major outsourced contracts
- HMPPS ARA 2024-25 — separate from MoJ, covers private prisons, electronic monitoring, education, healthcare commissioning
- HMCTS ARA 2024-25 — separate from MoJ, covers court estate, court IT, HMCTS Reform programme suppliers
- Home Office ARA 2024-25 — names asylum accommodation suppliers (Serco, Mears, Clearsprings), Migrant Help, key tech suppliers (Accenture, Mastek, PA Consulting)
- DE&S ARA 2024-25 — DE&S is a bespoke trading entity, publishes its own ARA; names major equipment programme spend (£12.171bn in 2024-25)
- Dstl ARA — Dstl is an on-vote defence agency, publishes its own
- DIO ARA — Defence Infrastructure Organisation publishes its own
- SDA ARA — Submarine Delivery Agency publishes its own

- **Contract title:** Sometimes (narrative, not structured)
- **Supplier:** Yes (named in narrative and supplier tables)
- **Total value:** Sometimes (programme spend, not contract value)
- **Start date / end date:** Sometimes (narrative)
- **Procurement method:** No
- **Sub-org attribution:** Yes — each ARA covers a specific body
- **Cadence:** Annual (typically July of the following year)
- **Access:** Free HTML and PDF
- **Coverage scope:** Narrative around the headline programmes, not a comprehensive register
- **Quality issues:** Unstructured narrative, no consistent supplier table format. Useful as a cross-reference, not a primary feed.

### 2.8 Cabinet Office Strategic Suppliers list

- **URL:** https://www.gov.uk/government/publications/strategic-suppliers
- **What it publishes:** A list of the ~39 strategic suppliers (companies that earn over £100m per year from government contracts) and the Crown Representatives assigned to manage them. **It does not publish contract-level information.**
- **Contract title / supplier / value / dates / method / sub-org:** No on all
- **What's actually here:** Just a list of supplier names paired with their assigned Crown Representative
- **Cadence:** Updated when memberships change
- **Coverage scope:** Top suppliers only
- **Quality issues:** Often perceived as a contract register but isn't one. The Memoranda of Understanding between government and each strategic supplier require the supplier to provide contract data to government, but that data is not published.

### 2.9 Crown Commercial Service framework call-off data (G-Cloud, DOS, Tech Services)

- **URL:** https://www.gca.gov.uk/agreements (formerly crowncommercial.gov.uk/agreements). G-Cloud spend dashboard is published monthly.
- **What it publishes:** Spend per framework, per supplier. G-Cloud spend reached almost £3bn in FY2024-25.
- **Contract title:** Sometimes (call-off label only)
- **Supplier:** Yes
- **Total value:** Yes (call-off value)
- **Start date / end date:** Yes (call-off term, typically 36+12 months)
- **Procurement method:** Yes (framework call-off, with the parent framework named)
- **Lot structure:** Limited
- **Bidder count:** No
- **Sub-org attribution:** **Yes — the buying body is named.** This is the best single source for sub-org attribution on technology and digital call-offs. UKVI, Border Force, HMPO, Defence Digital, HMPPS, HMCTS all appear as named buyers on G-Cloud and DOS call-offs.
- **Cadence:** Monthly
- **Access:** Free dashboard, downloadable
- **Coverage scope:** Only the framework call-offs (cloud, digital outcomes, technology services). Misses everything off-framework.
- **Quality issues:** Buyer name is freeform; G-Cloud call-offs often understate scope (a £100k call-off can be the start of a much larger engagement that grows through extensions)

### 2.10 Ministry of Justice procurement pipeline (UK1 pipeline notices) and Sourcing Portal

- **URL:** https://www.gov.uk/government/organisations/ministry-of-justice/about/procurement
- **Sourcing portal:** https://ministryofjusticecommercial.ukp.app.jaggaer.com/
- **What it publishes:** UK1 pipeline notices for contracts over £2m planned over the next 18 months. The sourcing portal is where actual procurements run.
- **Contract title:** Yes (planned)
- **Supplier:** No (not yet awarded)
- **Total value:** Yes (estimated)
- **Start date:** Yes (planned)
- **End date:** Sometimes (planned)
- **Procurement method:** Yes (planned)
- **Sub-org attribution:** Sometimes — UK1 notices include a "lead organisation" field that varies by department's discipline. Better than the predecessor regime but not yet consistent.
- **Cadence:** UK1 published quarterly under the Procurement Act
- **Access:** Free, FTS / CDP
- **Coverage scope:** Forward pipeline of >£2m contracts only
- **Quality issues:** Pipelines are forward-looking statements of intent and slip badly

### 2.11 NAO and Public Accounts Committee reports

- **URLs:** https://www.nao.org.uk/, https://committees.parliament.uk/
- **What it publishes:** Forensic narrative reports on supplier performance, programme overruns, contract structure, named incumbents.
- **Contract title:** Yes (narrative)
- **Supplier:** Yes (named)
- **Total value:** Yes (cited)
- **Start date / end date:** Yes (cited)
- **Procurement method:** Yes (narrative)
- **Sub-org attribution:** Yes (always names the actual buying body)
- **Cadence:** Ad hoc, typically 5–15 reports per year per major department
- **Access:** Free PDF
- **Coverage scope:** Programmes and contracts that NAO or PAC choose to investigate. Strong on big-ticket and politically salient items (asylum accommodation, FBIS, Atlas, prison places, major defence equipment); weak on routine contracting.
- **Quality issues:** Narrative not structured. Excellent ground truth for the contracts NAO covers.

### 2.12 Trade press archive

- **Sources:** Computer Weekly, The Register, PublicTechnology, UKAuthority, Civil Service World, Defence Contracts International, Defence Advancement, Inside Time
- **What it publishes:** Named contract awards with values, suppliers, dates — often before the formal notice is published, often filling gaps where notices are missing.
- **Sub-org attribution:** Yes (journalists name the actual buying body)
- **Cadence:** Continuous
- **Access:** Free or paywalled
- **Coverage scope:** Whatever the journalists pick up. Strong on tech and defence, sparse on routine commodities.
- **Quality issues:** Unstructured, requires NLP / extraction

### 2.13 WhatDoTheyKnow FOI corpus

- **URL:** https://www.whatdotheyknow.com/
- **What it publishes:** FOI requests and responses by public body
- **For "contract register" requests:** The pattern is consistent across MoJ / HMPPS / Home Office / MOD: contract registers ARE released under FOI but typically with values, lot structure, and sometimes dates redacted. Useful for finding the **list of contract titles** even when the values are blanked.
- **Sub-org attribution:** Yes (when the body itself is the FOI subject)
- **Cadence:** Whenever someone asks
- **Access:** Free
- **Coverage scope:** Patchy, depends on requests
- **Quality issues:** Heavy redaction is the norm. Format varies (PDF, Excel, narrative). Often one-shot snapshots rather than ongoing feeds.

### 2.14 Commercial platforms (Tussell, Stotles, Spend Network, BIP / Tracker, TechMarketView)

- **URLs:** https://www.tussell.com/, https://www.stotles.com/, https://www.spendnetwork.com/, https://www.tracker-rkb.com/, https://techmarketview.com/
- **What they publish:** Aggregated, normalised, deduplicated views over the same underlying open data (FTS, CF, £25k spend, framework call-off, OJEU/TED archive), plus FOI-derived contract registers, plus their own NLP layer.
- **Sub-org attribution:** Yes — Tussell explicitly consolidates buyers on a "parent + arms-length-bodies" basis using the government's own classification system, but exposes the underlying sub-org name on each record. Stotles likewise normalises.
- **Cadence:** Daily refresh
- **Access:** Subscription (Tussell prices typically £20k–£60k per year; Stotles similar)
- **Coverage scope:** Comprehensive over UK public sector
- **Quality issues:** Same underlying source quality issues, but their canonical layers and supplier deduplication are mature. **The single biggest commercial advantage they have is that they have already done what we are still building** — a reliable buyer canonical layer with parent-and-child relationships.

**Honest assessment:** Tussell or Stotles **already give a strong contract view at sub-org level for our priority sub-orgs**, sourced from the same open data we have, normalised to a higher standard than our canonical layer currently achieves. If the residual sub-org gap matters more than the budget, buying one of them as the back-stop is rational.

### 2.15 Other niche sources

| Source | What it adds | Sub-org? | Value |
|---|---|---|---|
| **HMPPS Custodial Contracts Group evidence to Justice Committee** | Periodic written evidence detailing private prison contracts, expiry dates and operators | Yes (HMPPS) | High for the prison estate |
| **DBS commercial publications** | DBS is a non-departmental public body and publishes its own ARA and procurement pages | Yes (DBS) | Medium |
| **Defence Sourcing Portal (DSP)** | MOD's e-tendering portal — opportunities and awards | Yes for some sub-orgs | Most useful awards already mirror to FTS |
| **Independent Chief Inspector of Borders and Immigration (ICIBI) reports** | Inspections of UKVI, Border Force, HMPO, Immigration Enforcement that name the systems and sometimes the suppliers | Yes (Home Office sub-orgs) | High for narrative context |
| **Migration Transparency Data** | Quarterly operational performance data for Border Force, UKVI, Immigration Enforcement, HMPO | Yes (Home Office sub-orgs) | High for operational context, no contract data |
| **Inside HMCTS / blog.gov.uk channels** | Officials writing about specific programmes (e.g. PECS contract management) | Yes | Useful colour |
| **HMPPS reference data (GitHub)** | CSV/JSON reference data for HMPPS systems | N/A | Not a contract feed |
| **Parliamentary Written Answers** | Ministers answering specific questions about contracts, values, suppliers | Yes | Strong source for specific gaps if a question has been asked |

---

## 3. Per-sub-org coverage matrix

Coverage rated Strong / Partial / Sparse / None against each priority sub-org.

| Sub-org | FTS+CF buyer field | £25k spend Entity | data.justice.gov.uk | Own ARA | NAO/PAC | NISTA | CCS framework | Trade press | Tussell/Stotles |
|---|---|---|---|---|---|---|---|---|---|
| **HMPPS** | Strong (HMPPS does publish in own name) | Strong (Entity column) | Partial (only outsourced services) | Strong (own ARA) | Strong | Partial (some prison build projects) | Partial | Strong | Strong |
| **HMCTS** | Strong (HMCTS publishes in own name) | Strong | Partial (PECS, intermediaries) | Strong (own ARA) | Strong | Strong (HMCTS Reform programme) | Strong (digital call-offs) | Strong | Strong |
| **Legal Aid Agency (LAA)** | Strong (LAA does publish) | Strong | Sparse | Strong (own ARA) | Strong | None | Sparse | Sparse | Strong |
| **Office of the Public Guardian (OPG)** | Partial (sometimes named) | Partial | None | Yes (own ARA) | Sparse | None | Sparse | Sparse | Partial |
| **Probation Service** (within HMPPS) | Sparse (rolls into HMPPS) | Partial | Strong (CAS-1, CAS-2, CAS-3 pages) | Inside HMPPS ARA | Strong | None | Sparse | Strong | Partial |
| **UK Visas and Immigration (UKVI)** | Sparse (publishes as Home Office) | **Strong** (Entity column nails it) | None | Inside Home Office ARA | Strong (FBIS, Atlas, asylum) | Strong (FBIS programme) | Strong (digital call-offs) | Strong | Partial |
| **Border Force** | Sparse | **Strong** (Entity column) | None | Inside Home Office ARA | Strong | Partial | Strong | Strong | Partial |
| **HM Passport Office (HMPO)** | Sparse | **Strong** (Entity column) | None | Inside Home Office ARA | Partial | None | Partial | Partial | Partial |
| **Immigration Enforcement** | Sparse | **Strong** (Entity column) | None | Inside Home Office ARA | Strong | None | Partial | Partial | Partial |
| **Disclosure and Barring Service (DBS)** | Partial (DBS does publish in own name as NDPB) | Strong | None | Strong (own ARA) | Partial | None | Partial | Sparse | Partial |
| **UKVIP (combined)** | Same as UKVI/HMPO | Same | None | Inside Home Office ARA | Sparse | None | Same | Same | Same |
| **Defence Digital** | Sparse (publishes as MOD or Strategic Command) | Sparse (rolls into Strategic Command) | None | Inside Strategic Command section of MOD ARA | Strong (PAC report on Defence Digital Strategy) | Strong (Skynet 6, Morpheus tagged Defence Digital) | Strong (digital call-offs) | Strong | Partial |
| **DE&S** | Strong (DE&S publishes in own name) | Strong (TLB-level Entity) | None | Strong (own ARA) | Strong | Strong | Partial | Strong | Strong |
| **Dstl** | Strong (Dstl publishes in own name) | Partial | None | Strong (own ARA) | Partial | Partial | Partial | Partial | Strong |
| **DIO** | Strong (DIO publishes in own name) | Strong (TLB-level) | None | Strong (own ARA) | Partial | Partial | Partial | Partial | Strong |
| **UK Strategic Command** | Partial | Strong (TLB-level) | None | Inside MOD ARA | Partial | Partial | Partial | Partial | Partial |
| **British Army / Royal Navy / Royal Air Force** | Partial | Strong (TLB-level) | None | Inside MOD ARA | Strong | Strong | Partial | Strong | Strong |
| **Submarine Delivery Agency (SDA)** | Strong (SDA publishes in own name) | Sparse | None | Strong (own ARA) | Strong | Strong | None | Strong | Strong |

**Reading of the matrix:**

- The **MoJ family** is the most contract-view-complete: HMPPS, HMCTS, LAA all behave well as named buyers on FTS+CF, and they each have rich ARA + NAO coverage. The £25k spend Entity column adds the supplier confirmation.
- The **Home Office family** has the structural pattern that the £25k spend Entity column is the **only** structured source that names UKVI / Border Force / HMPO / Immigration Enforcement separately. Contract notices almost always say "Home Office". This is exactly the gap Wave 1 was meant to close.
- The **MOD family** is mixed: DE&S, Dstl, DIO, and SDA all publish in their own name (we should be using this), but Defence Digital is the residual gap. NISTA is the only structured source that explicitly tags Defence Digital programmes.

---

## 4. Procurement Act 2023 transparency regime

The Procurement Act 2023 came into force on **24 February 2025** alongside the Procurement Regulations 2024. The enhanced Find a Tender service is the central digital platform. The Act introduced a richer notice taxonomy — UK1 to UK7 plus several supplementary notices — that, in principle, gives a fuller end-to-end view of every contract.

### Notice taxonomy

| Code | Notice | When | Contains |
|---|---|---|---|
| **UK1** | Pipeline notice | If the body expects to spend over £100m in the year, must publish a forward pipeline of contracts over £2m | Planned contracts, estimated values |
| **UK2** | Preliminary market engagement notice | Before formal procurement, if the body is talking to the market | Engagement scope |
| **UK3** | Planned procurement notice | Optional, signals intent to procure | Planned contract |
| **UK4** | Tender notice | Invites tenders | Full ITT-style data |
| **UK5** | Transparency notice | Required where the body intends to direct-award | Justification for non-competitive |
| **UK6** | Contract award notice | After award, before contract signature | Winner, value |
| **UK7** | Contract details notice | Within 30 days of contract signature (120 for light touch) — REQUIRED for all in-scope contracts | Title, supplier, value, start, end, procurement method, lots, contract document for ≥£5m |
| Supplementary | Contract performance notice | At least every 12 months for contracts ≥£5m, reporting against KPIs | Performance against three most-material KPIs |
| Supplementary | Contract change notice | When a contract is varied | Change details |
| Supplementary | Contract termination notice | When a contract is terminated | Termination details |
| Supplementary | Payment compliance notice | Twice yearly for any body with above-threshold contracts | Late payment data |
| Supplementary | Supplier debarment notice | When a supplier is excluded | Exclusion reason |

### What's actually new and useful for sub-org work

1. **UK7 is mandatory and rich.** Every contract entered into by an in-scope body must produce a UK7 within 30 days. The fields cover everything we need at contract level: title, supplier, total value, start, end, procurement method, lots. For contracts ≥£5m the contract itself must be published within 90 days (with redactions). This is genuinely new and is the single biggest unlock for the contract view.

2. **Contract performance notices** for ≥£5m contracts are also new and surface during-life KPI data — directly useful for our future paid Qualify tier and for Bid Execution incumbent intelligence.

3. **Contract change and termination notices** are new — they let us track contract drift through life rather than relying on the original award. Major win for tracking actual end dates vs original end dates.

### What is NOT new — the sub-org gap survives

The Act and the Regulations 2024 govern **what** must be published but they do not redefine **who the buyer is** in a way that fixes the sub-org problem. The "contracting authority" field on a UK7 notice is still freeform-ish, still inherits the publisher's existing practice. There is no mandated parent / child relationship in the OCDS schema (the OCDS for eForms profile has discussed this — open-contracting/standard issue 368 — but it's not yet a UK requirement).

In practical terms: a UK7 notice published by the Home Office is still published by the Home Office. There is nothing in the Act that compels the Home Office to publish UKVI / Border Force / HMPO / Immigration Enforcement as separate buyers. A few departments may choose to do so voluntarily, but most publish at parent level for consistency with governance and signing authority.

### Adoption rate

The Act came into force February 2025. Adoption has been ramping through 2025 and into 2026. Notice volume on the central digital platform has grown but compliance with the full notice set (especially performance notices, change notices, termination notices) is uneven across departments. The NAP6 commitment specifically tracks this; the December 2025 update reported "encouraging" early uptake with significant gaps in the long tail of contracting authorities.

### Conclusion on Procurement Act 2023

It is the biggest contract-data upgrade in UK public procurement history, but it does **not** by itself solve the sub-org attribution problem we have. The buyer field is still freeform. The unlock is in the richness per notice (especially UK7 + contract document publication for ≥£5m) and in the through-life tracking (performance, change, termination notices). For our priority sub-orgs the Procurement Act:

- Helps DE&S, Dstl, DIO, SDA, HMPPS, HMCTS, LAA, OPG, DBS — they were already publishing as themselves and now publish more per notice
- Does not help UKVI, Border Force, HMPO, Immigration Enforcement, Defence Digital — they were not publishing as themselves before and the Act does not require them to start

---

## 5. Pattern inference from spend

The question: can we derive contract structure (title, total value, start, end, supplier) from the £25k payment-by-payment data alone?

### What's known publicly

There is **no published, peer-reviewed, government-blessed methodology** for inferring contracts from spend in the UK public sector. The Open Contracting Partnership has published several blog posts (notably "We tried to connect contracts, spending and beneficial ownership in the UK. It was tough and that needs to change", May 2018) explicitly stating that linking spend to contracts is hard and that the UK's data does not yet support clean joins. The OGP / OCP commitments under NAP6 are pushing for this connection but it is not yet there.

### Commercial state of the art

**Spend Network** (https://www.spendnetwork.com/) is the most explicit publisher about its methodology and is the closest to "contract inference from spend" as a discipline:

- They harvest tender notices, contract notices, **and** spend data from public sector bodies globally
- They explicitly say coverage of joining the three is "patchy and only very small amounts of this data links together"
- They use machine learning to categorise transactions when category data is missing, combining keywords and known supplier-to-category mappings
- They describe the goal of matching suppliers to tenders as a vector-similarity problem — Alan Turing Institute Data Study Group documented this

**Tussell** does the same kind of joining commercially and exposes spend + contract on the same supplier record, but they do not publish their methodology in detail.

### Achievable accuracy from spend data alone

For the £25k spend feed, plausible heuristics with rough accuracy expectations are:

- **Supplier identity (canonical):** ~85–95% achievable with good name-matching + Companies House anchoring (we already do this for FTS suppliers)
- **Approximate contract start date** — first material payment to a supplier in a given Entity, with new supplier or step-change in payment scale: ~70% accuracy as a directional signal, but the lag from contract signature to first payment is unpredictable (often months, sometimes a year for build-up)
- **Approximate contract end date** — last material payment plus a "no-payment-for-N-months" rule: ~50–60% accurate, frequently fooled by quiet quarters and by transitional double-payments at handover
- **Total contract value** — running total of all payments: a **lower bound** only, never an upper bound. Misses what wasn't drawn, misses VAT treatment differences, misses contracts that grew via change notice
- **Procurement method** — not derivable from spend at all
- **Contract title** — derivable only as a free-text guess from the Expense Type / Expense Area columns. Often actually useful for narrative tagging (e.g. "Asylum accommodation - Serco North West"), but not the same as the formal contract title
- **Bidder count** — not derivable

### Open-source tooling

There is no widely-adopted, ready-to-use open-source library for "infer contracts from spend on UK public sector data". The Open Contracting Partnership's tooling is centred on the data standard, not on inference. The OCDS Kit (https://github.com/open-contracting/ocdskit) has utilities for OCDS data manipulation but no spend-to-contract inference. Spend Network's pipeline is closed source. There are academic papers on procurement spend mining but none specifically on UK central government with reproducible code.

### Bottom line

Spend-to-contract inference is **a complementary signal, not a primary fix**. It tells us "X supplier was paid Y by sub-organisation Z over period P", which helps us:

1. Confirm the operational owner of a contract we already know about
2. Spot incumbents we don't have a notice for at all (the contract was awarded before our notice history starts, or the notice was never published)
3. Estimate end date as a sanity check
4. Build the supplier-to-sub-org concentration view (which sub-org spends most with this supplier)

It cannot give us:
- Contract title (only a hint)
- Total value (only a lower bound)
- Procurement method
- Lot structure
- Bidder count

These remain notice-only fields.

---

## 6. Recommended Wave 1 redirect

Given the above, here is a revised Wave 1 ingestion and use plan that prioritises contract data over spend data while still using the spend data for what it's actually good at.

### 6.1 First-priority code change (cheap, high yield)

**Rebuild the buyer canonical layer to keep sub-organisations as first-class buyers.** Today, our canonical layer collapses HMPPS, HMCTS, LAA, OPG, DBS, DE&S, Dstl, DIO, SDA into their parent department. They publish notices in their own name. Keeping them as the buying entity, with a separate "department family" relationship to the parent, is a code change against the existing canonical layer rather than a new data source. This single fix:

- Recovers a large part of the MoJ contract view (HMPPS, HMCTS, LAA already publish in their own name)
- Recovers the entire DE&S, Dstl, DIO, SDA contract view for MOD
- Recovers DBS for Home Office
- Costs nothing in terms of new data — it's a model fix on data we already have

This is the highest-leverage action in the whole plan. **Do it first.**

### 6.2 Second-priority new feed (Procurement Act UK7s)

**Make sure the FTS ingest fully captures the UK7 contract details notice and the new supplementary notice types** — performance, change, termination. We already pull FTS via OCDS but need to confirm we are correctly parsing the new Procurement Act 2023 fields (especially the contract document attachment for ≥£5m contracts, and the through-life notices).

### 6.3 Third-priority new feed (£25k spend, scoped)

**Ingest the £25k spend data as a complementary signal**, not the primary contract feed. Use it for:

1. UKVI / Border Force / HMPO / Immigration Enforcement attribution (the Entity column is the **only** structured source)
2. DE&S / DIO / Strategic Command / single services TLB-level attribution for MOD
3. HMPPS / HMCTS / LAA / OPG attribution confirmation for MoJ
4. Supplier-to-sub-org concentration view (incumbent map)
5. End-date sanity-check for known contracts
6. Detection of suppliers who appear in spend but not in our notice history (likely missing notices or pre-history contracts)

Do **not** use it as the primary structure for contract title / value / start / end — those stay notice-derived.

### 6.4 Fourth-priority new feed (NISTA)

**Pull the NISTA major projects spreadsheet as an annual snapshot**, indexed by sponsor department and (for MOD) owning command. This is the only structured source that explicitly tags Defence Digital programmes. Low ingest cost, narrow but high-value coverage.

### 6.5 Fifth-priority new feed (CCS framework call-off data)

**Ingest the G-Cloud / DOS / Tech Services framework call-off published spend** monthly. Buyer field on call-offs is consistently named at sub-org level, value and dates are structured, framework method is known by definition. Strongest source for digital and technology contract attribution at sub-org level.

### 6.6 Narrative cross-check sources (no ingest, on-demand only)

Treat the following as on-demand cross-check sources that the dossier-generation skill consults during dossier construction, not as bulk-ingested feeds:

- Departmental ARAs (HMPPS, HMCTS, LAA, OPG, Home Office, MOD, DE&S, Dstl, DIO, SDA)
- NAO / PAC reports
- ICIBI inspection reports (Home Office sub-orgs)
- Trade press archives
- Parliamentary written answers
- WhatDoTheyKnow FOI corpus (specifically searching for "contract register" responses)
- `data.justice.gov.uk/contracts` major-services pages (small, narrow, but precise on the few services covered)

The Agent 2 intelligence skills running from Claude.ai already have web-fetch capability and can pull these on demand to enrich a dossier when the structured layer is thin.

### 6.7 What we cannot fix from open data

Two structural gaps remain after all of the above:

1. **Defence Digital does not publish in its own name and is not broken out in £25k spend.** The only structured signal is NISTA tagging and CCS digital call-offs. Strong narrative signal (NAO, trade press, PAC) can supplement but Defence Digital will always be the weakest dossier in the MOD family.

2. **Single-source defence contracts (SSRO regime) are not public at contract level.** SSRO publishes only aggregates. This affects most of the heavy single-source spend in the submarine, complex weapons, and AWE areas. NAO / PAC / trade press partly fill this but it is a real gap.

For both of these, the practical residual answer is **either**:
- A Tussell or Stotles subscription (they do not magically have data we can't get, but their canonical layer is more mature than ours and they pre-process the messy buyer-name field), **or**
- Accept the gap and flag it explicitly in dossier output ("Defence Digital coverage is limited because the body does not publish notices in its own name; downstream confidence on incumbents is medium.")

### 6.8 Sub-orgs we can give a strong contract-view dossier for after Wave 1 redirect

Following the redirect:

- **Strong** dossier achievable: HMPPS, HMCTS, LAA, OPG, DBS, DE&S, Dstl, DIO, SDA, the single-service commands (Army / Navy / RAF) above the TLB level
- **Medium** dossier achievable: UKVI, Border Force, HMPO, Immigration Enforcement (because £25k Entity column gives reliable supplier-to-body mapping; we then back-fit notice data using supplier+sector+date heuristics)
- **Sparse** dossier even after redirect: Defence Digital, individual Strategic Command sub-units below TLB
- **Not from open data alone:** Single-source defence contracts in detail (SSRO universe)

---

## 7. Bottom-line answer to the acid test

> The acid test for any source is "would this tell a senior consultant who the incumbent is on a £100m contract that's expiring next year, and how it was structured?"

Today, with our existing FTS+CF feed and current canonical layer:
- **MoJ family:** Yes for HMPPS, HMCTS, LAA. Partial for OPG and Probation.
- **Home Office family:** Partial for the family overall, weak for any specific sub-org.
- **MOD family:** Yes for DE&S, Dstl, DIO, SDA. Weak for Defence Digital.

After the Wave 1 redirect proposed in section 6:
- **MoJ family:** Yes for all priority sub-orgs.
- **Home Office family:** Yes for UKVI, Border Force, HMPO, Immigration Enforcement, DBS at supplier-attribution and rough-dates level. Contract structure (lots, method, bidder count) still inherited from the parent-named notice.
- **MOD family:** Yes for DE&S, Dstl, DIO, SDA, single services. Defence Digital remains the residual gap addressable only by NISTA + narrative + (optionally) Tussell.

**The single biggest insight in this report:** the existing canonical layer is collapsing buyers we already have at sub-org level. The "spend data is the answer" framing of the prior research was right for UKVI / Border Force / HMPO / Immigration Enforcement / Defence Digital (the bodies that don't publish in their own name). It was overstated for HMPPS / HMCTS / LAA / DE&S / Dstl / DIO / SDA — for those, the answer was already in the notice data and we were throwing it away in canonicalisation. Fix that first.

---

## Sources

- [Find a Tender service](https://www.find-tender.service.gov.uk/)
- [Find a Tender API documentation](https://www.find-tender.service.gov.uk/Developer/Documentation)
- [Find a Tender notice types and sequences](https://www.find-tender.service.gov.uk/Home/NoticeTypes)
- [Contracts Finder](https://www.contractsfinder.service.gov.uk/)
- [Justice Data — Contracted services](https://data.justice.gov.uk/contracts)
- [Justice Data — Electronic monitoring](https://data.justice.gov.uk/contracts/electronic-monitoring)
- [Justice Data — Community Accommodation Service](https://data.justice.gov.uk/contracts/bass)
- [Procurement at MOJ](https://www.gov.uk/government/organisations/ministry-of-justice/about/procurement)
- [MoJ Sourcing Portal](https://ministryofjusticecommercial.ukp.app.jaggaer.com/)
- [HMPPS Annual Report and Accounts 2024-25](https://www.gov.uk/government/publications/hmpps-annual-report-and-accounts-2024-to-2025)
- [HMCTS management information](https://www.gov.uk/government/statistical-data-sets/hmcts-management-information-march-2025)
- [Ministry of Justice ARA 2024-25](https://www.gov.uk/government/publications/ministry-of-justice-annual-report-and-accounts-2024-to-2025)
- [NAO MoJ Overview 2024-25](https://www.nao.org.uk/wp-content/uploads/2025/12/Ministry-of-Justice-Overview-24-25.pdf)
- [Tussell — Procurement Profile: Ministry of Justice](https://www.tussell.com/insights/procurement-profile-ministry-of-justice)
- [Tussell — Procurement Profile: Home Office](https://www.tussell.com/insights/procurement-profile-home-office)
- [NAO Home Office Overview 2024-25](https://www.nao.org.uk/wp-content/uploads/2025/10/home-office-overview-2024-25.pdf)
- [NAO Home Office's asylum accommodation contracts](https://www.nao.org.uk/wp-content/uploads/2025/05/home-offices-asylum-accommodation-contracts.pdf)
- [Home Office migration transparency data](https://www.gov.uk/government/statistical-data-sets/migration-transparency-data)
- [Home Office spending over £25,000 (collection)](https://www.gov.uk/government/publications/transparency-spend-over-25-000)
- [Asylum Accommodation and Support Contracts (AASC) Guide](https://asylummatters.org/app/uploads/2019/11/The-Asylum-Accommodation-and-Support-Contracts-A-Guide.pdf)
- [openDemocracy: Home Office fails to monitor asylum accommodation providers](https://www.opendemocracy.net/en/home-office-not-monitoring-asylum-seekers-accommodation-providers-billion-pound-contracts-clearsprings-serco-mears/)
- [The Register: Home Office still relies on 25-year-old asylum case database](https://www.theregister.com/2025/12/12/uk_asylum_atlas/)
- [MOD Trade, Industry and Contracts: 2024](https://www.gov.uk/government/statistics/mod-trade-industry-and-contracts-2024/mod-trade-industry-and-contracts-2024)
- [MOD Trade, Industry and Contracts: 2025](https://www.gov.uk/government/statistics/mod-trade-industry-and-contracts-2025/mod-trade-industry-and-contracts-2025)
- [Defence Trade and Industry index](https://www.gov.uk/government/collections/defence-trade-and-industry-index)
- [Defence Equipment & Support ARA 2024-25](https://www.gov.uk/government/publications/defence-equipment-support-annual-report-and-accounts-2024-to-2025)
- [DE&S 2024-25 Annual Report announcement](https://des.mod.uk/des-2024-25-annual-report-and-accounts-shows-strong-delivery-during-challenging-times/)
- [Defence Sourcing Portal](https://www.digital.mod.uk/sme-dosbg/find-an-opportunity)
- [SKYNET 6 guidance](https://www.gov.uk/guidance/skynet-6)
- [Single Source Regulations Office](https://www.ssro.gov.uk/)
- [SSRO regulatory framework guidance](https://www.gov.uk/guidance/i-would-like-to-find-out-about-the-ssro-and-the-regulatory-framework)
- [Defence procurement: The single source contract regulations (CBP-9645)](https://researchbriefings.files.parliament.uk/documents/CBP-9645/CBP-9645.pdf)
- [Cabinet Office Crown Representatives and strategic suppliers](https://www.gov.uk/government/publications/strategic-suppliers)
- [Tussell 2025 Analysis of UK Government Strategic Suppliers](https://www.tussell.com/insights/uk-government-strategic-suppliers)
- [Major projects data (collection)](https://www.gov.uk/government/collections/major-projects-data)
- [NISTA Annual Report 2024-25](https://www.gov.uk/government/publications/nista-annual-report-2024-2025/nista-annual-report-2024-25)
- [Procurement Act 2023 — Central Digital Platform factsheet](https://www.gov.uk/government/publications/procurement-act-2023-short-guides/central-digital-platform-factsheet-html)
- [Procurement Act 2023 — Contract Details Notices guidance](https://www.gov.uk/government/publications/procurement-act-2023-guidance-documents-procure-phase/guidance-contract-details-notices-html)
- [Procurement Act 2023 — New legislative requirements](https://www.gov.uk/government/publications/procurement-act-2023-short-guides/new-legislative-requirements-under-the-procurement-act-2023-html)
- [Procurement Act 2023 (legislation.gov.uk)](https://www.legislation.gov.uk/ukpga/2023/54)
- [DLA Piper — Transparency requirements in the Procurement Act 2023](https://www.dlapiper.com/en/insights/publications/2025/02/transparency-requirements-in-the-procurement-act-2023)
- [Procurement and contracting transparency requirements: guidance](https://www.gov.uk/government/publications/procurement-and-contracting-transparency-requirements-guidance)
- [How to publish central government transparency data (collection)](https://www.gov.uk/government/collections/how-to-publish-central-government-transparency-data)
- [Crown Commercial Service — G-Cloud agreements](https://www.gca.gov.uk/agreements/RM1557.14)
- [G-Cloud 15 framework feature (Computer Weekly)](https://www.computerweekly.com/feature/UK-governments-G-Cloud-15-framework-Everything-you-need-to-know)
- [HMPPS Custodial Contracts evidence to Justice Committee](https://www.parliament.uk/globalassets/documents/commons-committees/Justice/correspondence/Prison-governance-evidence-HMPPS-NHS-England.pdf)
- [PECS contract management blog (Inside HMCTS)](https://insidehmcts.blog.gov.uk/2025/10/13/inside-pecs-managing-one-of-governments-most-complex-contracts/)
- [WhatDoTheyKnow](https://www.whatdotheyknow.com/)
- [Open Contracting Partnership — UK linkages blog (2018)](https://www.open-contracting.org/2018/05/09/tried-connect-contracts-spending-beneficial-ownership-uk-tough-needs-change/)
- [OCDS for eForms profile](https://standard.open-contracting.org/profiles/eforms/latest/en/)
- [OCP — UK Find a Tender data registry](https://data.open-contracting.org/en/publication/41)
- [Spend Network](https://www.spendnetwork.com/)
- [Alan Turing Institute Data Study Group — Spend Network report](https://www.turing.ac.uk/sites/default/files/2019-11/the_alan_turing_institute_data_study_group_final_report_-_spend_network.pdf)
- [Tussell](https://www.tussell.com/)
- [Stotles](https://www.stotles.com/)
- [BCC-Tussell SME Procurement Tracker (methodology)](https://www.britishchambers.org.uk/wp-content/uploads/2024/08/BCC-Tussell-SME-Procurement-Tracker.pdf)
- [Open Government Partnership — Open Contracting through the Procurement Act (UK0107)](https://www.opengovpartnership.org/members/united-kingdom/commitments/UK0107/)
- [UK NAP6 Final status update on open contracting](https://www.gov.uk/government/publications/uk-national-action-plan-for-open-government-2024-to-2025-final-commitment-updates/uk-nap6-final-status-update-commitment-1-open-contracting-html)
