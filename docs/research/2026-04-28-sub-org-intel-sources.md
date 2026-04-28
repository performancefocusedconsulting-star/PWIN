# Sub-organisation intelligence sources for UK central government

**Author:** Research workstream
**Date:** 2026-04-28
**Scope:** Identify and evaluate every plausible source of UK central-government sub-organisation procurement and operational intelligence to overlay on the existing PWIN procurement database, with specific reference to two test cases that the contract notice feeds cover poorly: **UK Visas and Immigration (UKVI)** inside the Home Office, and **Defence Digital** inside the Ministry of Defence.

---

## 1. Executive summary

The contract notice feeds (Find a Tender, Contracts Finder) are the **only** source that gives us notice-level structured data — every other source either trades off granularity, structure, or freshness. The realistic strategy is to **layer five complementary sources** on top of the notice data we already have:

| Rank | Source | What it adds | UKVI coverage | Defence Digital coverage |
|---|---|---|---|---|
| 1 | **Departmental spend over £25k transparency CSVs** (monthly, gov.uk) | Transactional supplier-by-supplier spend with an "Entity" column that breaks out sub-organisations. The single biggest unlock for UKVI. | **Strong** — Home Office CSVs carry an Entity column that names UKVI, Border Force, HMPO, Immigration Enforcement separately. | **Partial** — MOD CSVs use Top Level Budget (TLB) holders as the entity, so Strategic Command appears but Defence Digital itself often does not as a distinct line. Still useful for narrowing. |
| 2 | **Government Major Projects Portfolio (GMPP) annual data, now NISTA** | Project-level whole-life costs, delivery confidence ratings, sponsor department, and (for MOD) the owning command. Names the actual programmes — Atlas, FBIS, Skynet 6, Morpheus. | **Strong** — surfaces FBIS (£3.8bn), IPT, Atlas as named programmes with cost envelopes. | **Strong** — Skynet 6 is explicitly recorded as Defence Digital-owned in GMPP returns. |
| 3 | **NAO and Public Accounts Committee reports** | Forensic narrative about supplier performance, programme overruns, contract structure, and named incumbents. | **Strong** — repeated coverage of asylum accommodation contracts (Serco, Mears, Clearsprings), Skilled Worker visa system, Atlas data quality, Immigration Enforcement value-for-money. | **Strong** — Defence Digital Strategy was the subject of a dedicated PAC report; MOD departmental overviews surface IT and digital cost trends. |
| 4 | **Departmental Annual Reports and Accounts (and agency annual reports)** | Top supplier lists, programme expenditure, headcount, organisational structure. HMPPS, Dstl and similar agencies publish their own ARAs even when they don't publish their own contract notices. | **Strong** — Home Office ARA 2024-25 names the suppliers behind the £15.3bn asylum contracts and gives commentary on FBIS spend. | **Partial-to-strong** — MOD ARA names the top-10 suppliers MOD-wide; Dstl and DE&S publish their own ARAs; Defence Digital is normally referenced inside Strategic Command's ARA section rather than its own. |
| 5 | **Trade press archive (Computer Weekly, The Register, PublicTechnology, UKAuthority)** | Named contract awards with values, supplier names, and dates — often *months before* the formal notice appears, and often filling in the gaps where notices were never published. | **Very strong** — the £85m architecture deal, the £120m FBIS systems integration deal, the Capgemini £37m UK border deal were all reported in trade press first. | **Strong** — Defence Digital's £2.7bn IT envelope, individual command-and-control programme awards, supplier rotations all surface here. |

**The single highest-value action is to ingest the monthly £25k spend CSVs for Home Office and MOD, parse the "Entity" column as a sub-organisation key, and join it back to canonical suppliers.** This alone closes most of the visible gap on UKVI, because the Home Office uses the Entity column properly. For the MOD it is a partial win because the entity column is at TLB level, not below.

For **Defence Digital specifically**, the best signal stack is: GMPP project records (Skynet 6, Morpheus etc. are explicitly tagged) → MOD top-supplier disclosures in the ARA and the MOD Trade, Industry and Contracts annual statistics → SSRO single-source contract reports (DefCARS) for the non-competitive segment → trade press for everything else.

For **UKVI specifically**: spend over £25k Entity-tagged → FBIS / Atlas project data in NAO and PAC reports → ICIBI (Independent Chief Inspector) inspection reports → Home Office migration transparency data for operational context → trade press.

---

## 2. Source-by-source catalogue

### Tier A: Official open data — high structure, high reuse value

#### A1. Departmental spend over £25,000 transparency CSVs

- **URL (Home Office):** https://www.data.gov.uk/dataset/ecc70eba-dbf2-4bba-9f04-415cbe845118/spend-over-25-000-in-the-home-office (links to monthly CSVs on gov.uk publication pages)
- **URL (MOD):** https://www.gov.uk/government/publications/mod-spending-over-25000-january-to-december-2025 (and equivalent annual landing pages 2016 → 2026)
- **Cabinet Office collection page (template):** https://www.gov.uk/government/collections/cabinet-office-spend-data
- **What it publishes:** Every transaction the department settled above £25k. Columns are Department, **Entity** (the sub-organisation), Date, Expense Type, Expense Area, Supplier, Transaction number, Amount.
- **Sub-org granularity:** This is the headline finding. The Entity column **is** the sub-organisation breakout. For Home Office it names UKVI, Border Force, HM Passport Office, Immigration Enforcement, Disclosure and Barring Service distinctly. For MOD it names the TLB holders (Army, Navy, RAF, Strategic Command, Head Office, DE&S, Defence Infrastructure Organisation, Defence Nuclear Organisation) — Defence Digital sits inside Strategic Command and is not consistently broken out as its own entity, though the Expense Area column sometimes names it.
- **Cadence:** Monthly, with one-to-three months' lag.
- **Access:** Free, machine-readable CSV. No login. No API per-se — a regular pattern of monthly publication URLs.
- **Format:** CSV (all departments), with column-name and date-format inconsistencies between months and between departments. Some legacy months are PDF.
- **Quality issues:** Naming of suppliers is freeform — same supplier reappears under multiple spellings; needs the same name-clean / Splink approach as the FTS supplier layer. Entity values are also freeform across months. Some months are missing or republished.
- **UKVI evaluation:** **Yes — direct hit.** Entity field is consistently populated with "UK Visas and Immigration" (or close variants). Combined with Supplier and Amount this gives a transactional view of UKVI's external spend. This is the single best source for the test case.
- **Defence Digital evaluation:** **Partial.** Entity field rolls up to TLB. Defence Digital spend is buried in Strategic Command. The Expense Area / cost-centre fields sometimes name Defence Digital or its predecessor units — useful as a heuristic but not a clean primary key.

#### A2. Find a Tender Service (FTS) and Contracts Finder

- **URLs:** https://www.find-tender.service.gov.uk/, https://www.contractsfinder.service.gov.uk/
- **Status:** Already ingested by PWIN.
- **Sub-org gap:** This is the gap that triggered the whole research task. UKVI, Border Force, HMPPS, HM Passport Office, Defence Digital appear as buyers on essentially zero notices.
- **Note:** The Contracts Finder API does publish a buyer register where each buyer organisation has a unique identifier — useful for confirming that the sub-orgs *do not* have separate buyer IDs in the notice system, which is consistent with the gap.

#### A3. Government Major Projects Portfolio (GMPP) — now operated by NISTA

- **URL (collection):** https://www.gov.uk/government/collections/government-major-projects-portfolio-data (each department publishes its own)
- **MOD-specific URL:** https://www.gov.uk/government/publications/mod-government-major-projects-portfolio-data-2024 (same pattern annually)
- **What it publishes:** Per project: project name, sponsoring department, sponsoring agency / TLB, whole life cost (WLC), benefits, snapshot date, and the IPA's traffic-light Delivery Confidence Assessment (Red/Amber/Green/Exempt).
- **Sub-org granularity:** **Strong for both test cases.** GMPP records explicitly tag projects to their owning command or executive agency. MOD's GMPP file shows Skynet 6 as a Defence Digital project, Morpheus as a Strategic Command / Defence Digital project. Home Office's GMPP file shows FBIS (£3.8bn) under UKVI / Migration and Borders Technology Portfolio.
- **Cadence:** Annual snapshot at 31 March, published in late spring/early summer.
- **Access:** Free, machine-readable. Latest releases include CSV; older years are PDF + Excel.
- **Format:** CSV / XLSX / PDF.
- **Quality issues:** Annual snapshot only — no in-year tracking. WLC numbers are aggregated, not transactional. Supplier names are NOT published in GMPP (this is the big disappointment — programme yes, suppliers no). Confidence ratings are sometimes redacted as "Exempt".
- **UKVI evaluation:** **Strong.** Identifies the major programmes (FBIS, IPT, Atlas if it appears) by name with cost envelopes and confidence ratings. Doesn't tell you the supplier — pair with NAO / trade press for that.
- **Defence Digital evaluation:** **Strong.** Skynet 6, Morpheus, and equivalent programmes are tagged to Defence Digital. Whole life cost gives a credible upper bound for spend tracking.

#### A4. Companies House (already ingested) — supplier annual filings

- **URL:** https://find-and-update.company-information.service.gov.uk/
- **Status:** Already ingested for company status, directors, SIC, parent.
- **Adds for the sub-org problem:** The annual report and accounts of major suppliers (Capita, Capgemini, Atos, DXC, Fujitsu, Sopra Steria, Babcock, BAE, Leidos, Serco, Mears) routinely **name their public sector clients in narrative form** — especially in segmental disclosures and risk factors. Capita's annual report for example breaks out its government work by named contract; Serco's names its asylum accommodation work. This is unstructured but rich.
- **Action:** Pull the full PDF / iXBRL filings for the strategic supplier list and run targeted text extraction looking for sub-org mentions ("UKVI", "Border Force", "HMPPS", "Defence Digital", "Strategic Command").

#### A5. Departmental organograms (Civil Service organisation charts)

- **URL (Home Office):** https://www.data.gov.uk/dataset/ — search "organogram Home Office" (and equivalent for MOD)
- **What it publishes:** Names, job titles, salary bands and reporting lines for all senior civil servants and directors. Released as CSV under Open Government Licence.
- **Sub-org granularity:** **Strong.** Each role is tagged to its parent unit, so the chart names UKVI, Border Force, HMPO, Immigration Enforcement directly. For MOD it names Defence Digital and its directorates (Cyber, Networks, Service Operations).
- **Cadence:** Twice a year — 31 March snapshot published by 6 June, 30 September snapshot published by 6 December.
- **Access:** Free, CSV.
- **Format:** CSV (junior staff aggregated; senior named).
- **Quality issues:** The data is patchy — IfG has noted that some departments publish on gov.uk, some on data.gov.uk, format changes between years.
- **Use in PWIN:** This is a **stakeholder-mapping** asset, not a contract asset. Feeds Win Strategy's stakeholder map directly. A consistent canonical layer of UKVI / Defence Digital senior staff with role and grade.

#### A6. MOD Trade, Industry and Contracts annual statistics

- **URL:** https://www.gov.uk/government/statistics/mod-trade-industry-and-contracts-2025/mod-trade-industry-and-contracts-2025 (and prior years)
- **Collection:** https://www.gov.uk/government/collections/defence-trade-and-industry-index
- **What it publishes:** Aggregate analysis of MOD spending by type, by supplier, by geography, by industry sector. Names the **top 10 MOD suppliers** by expenditure each year. PFI contract details. Direct payments to industry totals.
- **Sub-org granularity:** **Limited.** The publication is MOD-wide. Some breakdowns by Front Line Command but Defence Digital is not consistently a published cut.
- **Cadence:** Annual, published mid-year (covers FY end-March).
- **Access:** Free, ODS / Excel + HTML narrative.
- **Quality issues:** Top-10 only — no long-tail supplier list. Reconciliation against actual spend has known gaps (NAO has called this out).
- **MOD top-suppliers FY24/25 from this dataset:** Babcock, KBR, Leidos, BAE Systems, Thales (Defence Strategic Suppliers grouping). Total MOD core-department supplier spend FY24/25: £40.6bn.
- **UKVI evaluation:** N/A (MOD only).
- **Defence Digital evaluation:** **Indirect.** The MOD-wide IT spend pattern lets us infer Defence Digital share, but it does not break it out.

#### A7. MOD Departmental Resources statistics

- **URL:** https://www.gov.uk/government/statistics/defence-departmental-resources-2025/mod-departmental-resources-2025
- **What it publishes:** MOD spending by TLB holder, by category (Resource DEL, Capital DEL, Operations), with multi-year trend data.
- **Sub-org granularity:** **TLB level** — Strategic Command gets a line, Defence Digital does not.
- **Cadence:** Annual.
- **Use:** Establishes the Strategic Command spend envelope inside which Defence Digital sits.

#### A8. Single Source Regulations Office (SSRO) compliance bulletins and DefCARS data

- **URL:** https://www.ssro.gov.uk/
- **What it publishes:** Aggregate reporting on non-competitive defence contracts (single-source). Annual compliance bulletin covers ~£20bn+ of contract value. The underlying DefCARS data is contractor-by-contractor and contract-by-contract, but is **not public** at item level — only aggregate figures and named compliance summaries.
- **Sub-org granularity:** Aggregate. Reports do name large single-source contracts and contractors but not always the MOD sub-organisation.
- **Cadence:** Annual compliance bulletin; ad hoc analysis publications.
- **Access:** Free.
- **Quality issues:** ~39% of MOD contracts are non-competitive and therefore *not* on FTS — DefCARS is the only structured visibility we get into that segment. But only at aggregate. Item-level DefCARS data sits with SSRO and would require negotiation or FOI to access.
- **UKVI evaluation:** N/A.
- **Defence Digital evaluation:** **Partial.** Single-source IT contracts (rare but they exist — sustainment of legacy systems, sole-source comms infrastructure) sit here. Worth ingesting the bulletin narrative for named contracts.

#### A9. Defence Sourcing Portal (DSP)

- **URL:** https://www.contracts.mod.uk/
- **What it publishes:** Live MOD tender opportunities. Account-free read access for opportunity browsing; bidding requires registration.
- **Sub-org granularity:** Notices typically name the requesting unit (DE&S, Defence Digital, Strategic Command). **More granular than FTS for MOD specifically.**
- **Cadence:** Continuous.
- **Access:** Free read; registration required for full document download. **No bulk export, no documented public API** — would require scraping, and MOD T&Cs may restrict that.
- **Format:** HTML, with PDF / DOCX attachments per opportunity.
- **Quality issues:** Coverage overlaps significantly with FTS (most >£10k are dual-published) but some defence-specific opportunities appear here only.
- **Defence Digital evaluation:** **Strong** — DSP is where Defence Digital itself publishes tenders and is named as the buying authority on the notice.

#### A10. Crown Commercial Service (CCS) framework data

- **URL:** https://www.crowncommercial.gov.uk/, https://www.gov.uk/government/publications/crown-commercial-service-annual-report-and-accounts-2024-to-2025
- **What it publishes:** CCS annual report (which names the largest frameworks and customer departments), framework agreement documents, and call-off reporting.
- **What CCS does NOT publish openly:** A full call-off ledger by sub-organisation. Some call-offs surface as FTS contract award notices but many sub-£threshold call-offs are invisible.
- **Sub-org granularity:** Limited. CCS reports use department-family level; only occasionally name sub-orgs.
- **Cadence:** Annual report; framework agreements as awarded.
- **Use:** Establishes which frameworks UKVI / Defence Digital are likely calling off through (Technology Services 3, G-Cloud, DOS) — useful for inferring competitive context.

### Tier B: Official disclosure-style sources — narrative-rich, structurally weak

#### B1. National Audit Office reports

- **URL:** https://www.nao.org.uk/reports/
- **What it publishes:** Forensic value-for-money studies and departmental annual audit overviews. Names suppliers, contract values, programme costs, and structural failures.
- **UKVI / Home Office hot reports (recent):**
  - "An analysis of the asylum system" (Dec 2025) — detailed Atlas case management commentary, asylum accommodation contract analysis.
  - "Home Office's asylum accommodation contracts" (May 2025) — the £15.3bn over-ten-years figure for Serco, Mears, Clearsprings.
  - "Immigration: Skilled Worker visas" (March 2025).
  - "Immigration enforcement" (June 2020) — the foundation VFM report.
  - Annual Home Office overview (latest: October 2025, FY24-25).
- **Defence Digital / MOD hot reports (recent):**
  - "Ministry of Defence Accounts 2024-25" (Dec 2025) — overview narrative.
  - PAC's "The Defence digital strategy" report (cmpubacc/727) — explicitly evaluates Defence Digital's performance.
  - Various annual MOD departmental overviews.
- **Sub-org granularity:** **Strong** — NAO routinely names sub-organisations and individual programmes / contracts.
- **Cadence:** Continuous (one or two reports per department per year, plus annual audit overviews).
- **Access:** Free, PDF.
- **Quality issues:** Narrative. Numbers in PDF tables, not always re-released as CSV. Requires text extraction.
- **Action for PWIN:** Build a small NAO ingest that pulls the report PDFs for the priority departments, runs entity extraction over them, and surfaces named-supplier and named-programme mentions tagged to sub-organisation.

#### B2. Public Accounts Committee (PAC) and other Select Committee reports

- **URL:** https://committees.parliament.uk/committee/127/public-accounts-committee/publications/ (PAC), plus Defence Committee and Home Affairs Committee
- **What it publishes:** Hearings, evidence sessions, and reports — often shadowing NAO reports and adding direct supplier-level questioning.
- **Sub-org granularity:** **Strong.** PAC has reported specifically on the Defence digital strategy and the Home Office asylum transformation programme.
- **Cadence:** Continuous.
- **Access:** Free, HTML + PDF + transcribed evidence.
- **Quality issues:** Narrative. Witness statements include named suppliers and contract figures.
- **Action:** Combine with NAO ingest above.

#### B3. Hansard — written and oral parliamentary questions

- **URL (PQs):** https://questions-statements.parliament.uk/, https://hansard.parliament.uk/search/WrittenAnswers
- **TheyWorkForYou mirror:** https://www.theyworkforyou.com/written-answers-and-statements/
- **What it publishes:** Every PQ asked of every department, plus the minister's answer. PQs *frequently* extract sub-organisation level data that does not appear elsewhere — "How much has UKVI spent with Capgemini in each of the last three years?" is a typical question and the answer comes out as a written response.
- **Sub-org granularity:** **Variable but often very strong** — depends entirely on what was asked.
- **Cadence:** Continuous (Parliament sitting days).
- **Access:** Free, with full-text search. TheyWorkForYou has a stable URL pattern and a usable scraping target.
- **Quality issues:** Coverage is opportunistic — only what MPs ask gets answered.
- **Action:** Build a topic-watch on the priority sub-orgs ("UKVI", "Border Force", "Defence Digital", "Skynet", "FBIS", "Atlas") and pull the resulting Q&A pairs into an unstructured intel store.

#### B4. Independent Chief Inspector of Borders and Immigration (ICIBI)

- **URL:** https://www.gov.uk/government/organisations/independent-chief-inspector-of-borders-and-immigration
- **Inspection reports collection:** https://www.gov.uk/government/collections/inspection-reports-by-the-independent-chief-inspector-of-borders-and-immigration
- **What it publishes:** Programme inspections of UKVI, Border Force, Immigration Enforcement and HMPO. Topics include FBIS, sponsorship, eVisas, asylum casework, EU Settlement Scheme.
- **Sub-org granularity:** **Strong** — every report is by definition scoped to a sub-organisation function.
- **Cadence:** Multiple inspections per year + annual report.
- **Access:** Free, PDF.
- **UKVI evaluation:** **Very strong** — ICIBI has announced an inspection of FBIS programme benefits and has previously inspected Atlas-related casework.
- **Defence Digital evaluation:** N/A.

#### B5. Departmental Annual Reports and Accounts (and agency ARAs)

- **URLs:**
  - Home Office ARA 2024-25: https://www.gov.uk/government/publications/home-office-annual-report-and-accounts-2024-to-2025
  - MOD ARA 2024-25: https://www.gov.uk/government/publications/ministry-of-defence-annual-report-and-accounts-2024-to-2025
  - HMPPS ARA: https://www.gov.uk/government/publications/hmpps-annual-report-and-accounts-2024-to-2025 (and equivalent for Dstl, DE&S etc.)
- **What it publishes:** Performance narrative, financial statements, top-supplier disclosures (departments with strategic suppliers list them), major programme commentary, headcount, organisational structure.
- **Sub-org granularity:** **Variable** — some sub-orgs publish their own ARA (HMPPS, Dstl, DE&S, DBS), others appear only as sections inside the parent department's ARA.
- **Cadence:** Annual, normally laid in Parliament October–November for prior FY.
- **Access:** Free, PDF (HMRC and a few others publish HTML).
- **UKVI evaluation:** Home Office ARA names FBIS, Atlas, asylum accommodation suppliers, with budget commentary. UKVI itself does not publish an own-name ARA.
- **Defence Digital evaluation:** MOD ARA names top suppliers MOD-wide; Defence Digital appears in narrative under Strategic Command. Dstl and DE&S publish their own ARAs (useful adjacents).

#### B6. Migration transparency data

- **URL:** https://www.gov.uk/government/statistical-data-sets/migration-transparency-data
- **What it publishes:** Quarterly performance data on UKVI, Border Force, Immigration Enforcement, HMPO — application volumes, processing times, customer service metrics, sponsorship data.
- **Sub-org granularity:** **Excellent for operations, irrelevant for procurement.**
- **Use in PWIN:** Provides the operational context that flows into Win Strategy buyer-need hypotheses (volumes, backlog, performance trajectory). Not a procurement source per se.
- **UKVI evaluation:** **Strong (operational context).**
- **Defence Digital evaluation:** N/A.

#### B7. Government commercial pipeline publications

- **Cabinet Office guidance:** https://www.gov.uk/government/publications/commercial-operating-standards-for-government/commercial-pipeline-guidance-v7-html
- **Examples:** HMRC pipeline (https://www.gov.uk/government/publications/hmrcs-commercial-pipeline), HSE pipeline.
- **What it publishes:** Forward look (~18 months) of intended procurements >£2m. Procurement Act 2023 mandates pipeline notices on Find a Tender for procurements over £2m, but several departments publish a richer narrative pipeline alongside.
- **Sub-org granularity:** Variable — most pipelines are department-level; some name the requesting unit.
- **Cadence:** 6-monthly review.
- **Access:** Free, CSV / Excel.
- **Use in PWIN:** Feeds the existing forward pipeline view; richer than FTS UK1 notices alone.

### Tier C: Commercial intelligence platforms

#### C1. Tussell

- **URL:** https://www.tussell.com/
- **Methodology (verified):** Combines invoice spend data (the £25k transparency CSVs and £500 local government equivalents) with notice data (FTS, Contracts Finder), matched against Companies House. Buyers are "consolidated" — i.e. each parent department is shown together with its arms-length bodies. **Match rate is reported at 94% for central government invoices by both volume and value.**
- **Sub-org granularity:** **Strong** — Tussell's buyer hierarchy explicitly carries parent + sub-org rollups.
- **Pricing:** Subscription. Not free.
- **What we'd buy:** A pre-resolved sub-org-tagged invoice + notice dataset that we could otherwise build ourselves but at material engineering cost.
- **Public artefacts (free):** Tussell publishes free reports including the Strategic Suppliers analysis (which gives FY24/25 spend = 10% of the £249bn public procurement total going to the 39 strategic suppliers) and the Procurement Profile series for major buyers.
- **UKVI evaluation:** Strong — accessible only through subscription.
- **Defence Digital evaluation:** Tussell's Defence Procurement Tracker covers MOD; sub-org tagging quality for Defence Digital specifically is unverified without access.

#### C2. Stotles

- **URL:** https://www.stotles.com/
- **Methodology:** Similar pattern (invoice + notice + supplier registry match). Tools.stotles.com has a publicly browsable spend file index. Stotles markets a "competitor and partner mapping" capability.
- **Sub-org granularity:** Their docs reference buyer hierarchy mapping; quality unverified without trial access.
- **Pricing:** Subscription with a freemium / lite tier.

#### C3. Spend Network / Open Opportunities (now part of GovShop)

- **URLs:** https://www.spendnetwork.com/, https://openopps.com/
- **What it publishes:** Aggregates 700+ procurement feeds globally, including UK FTS / Contracts Finder, in OCDS format. OpenOpps offers an aggregated tender alerts product across 800+ sources.
- **Sub-org granularity:** Buyer organisation as published by source — no special sub-org enrichment beyond what the source carries. Probably *not* an uplift over what we already have.
- **Pricing:** Subscription. Open Opportunities has a free tier for browsing.

#### C4. BIP Solutions Tracker / DCI (Defence Contracts International)

- **URL:** https://www.dcicontracts.com/
- **What it publishes:** Defence-specialist tender alert and intelligence product. DCI provides commentary on MOD pipelines, Strategic Defence Review impact, and frameworks.
- **Sub-org granularity:** Defence-specific; tags opportunities to MOD command.
- **Pricing:** Subscription. Not free.
- **Defence Digital evaluation:** Defence-specific, so coverage is plausibly stronger than horizontal trackers; quality unverified without access.

#### C5. TechMarketView

- **URL:** https://www.techmarketview.com/
- **What it publishes:** UK-specific tech and digital market analyst service. Publishes a UK Public Sector Software & IT Services (UK PS-SITS) tracker that breaks down supplier revenue by buyer department and named programme.
- **Sub-org granularity:** **Strong for tech specifically.** Names Atlas, FBIS, Skynet 6, Morpheus and the suppliers behind them.
- **Pricing:** High-end analyst subscription.
- **UKVI evaluation:** Strong (tech-only view of FBIS, Atlas).
- **Defence Digital evaluation:** Strong (tech-only view).
- **Caveat:** Analyst opinion product — proprietary research, not raw data. Useful as a sanity check / triangulation source.

### Tier D: Trade press archives

#### D1. ComputerWeekly UK government beat

- **URL:** https://www.computerweekly.com/topic/UK-government
- **Specifically valuable for:** Long-form supplier-and-contract reporting, FOI-derived spending tables, post-mortems of major IT contracts (Aspire, Horizon, etc.).
- **Sub-org granularity:** Strong — articles name UKVI, Border Force, Defence Digital, individual programmes.

#### D2. The Register (Public Sector / UK Gov)

- **URL:** https://www.theregister.com/
- **Specifically valuable for:** Contract award reporting that often surfaces *before* the formal Contracts Finder notice, with full value and supplier name. Tracks Strategic Supplier dependency stories (Capita, Fujitsu, Capgemini).
- **Examples:** £85m FBIS architecture deal coverage, £37m Capgemini border contract, MOD's £2.1bn IT spend disclosures.

#### D3. PublicTechnology.net

- **URL:** https://www.publictechnology.net/
- **Specifically valuable for:** UK-government-only digital and IT news. Heavy coverage of named programmes.

#### D4. UKAuthority

- **URL:** https://www.ukauthority.com/
- **Specifically valuable for:** Mid-market UK government IT contract announcements that don't make the national tech press.

#### D5. UK Defence Journal

- **URL:** https://ukdefencejournal.org.uk/
- **Specifically valuable for:** MOD contract reporting, including Defence Digital named programmes and supplier rotation news.

#### D6. Civil Service World, Government Computing, ComputerWeekly UK Public Sector

- **URLs:** https://www.civilserviceworld.com/, https://www.governmentcomputing.com/
- **Use:** Cross-cutting policy and contract narrative.

### Tier E: Supplier-side disclosures

#### E1. Strategic supplier annual reports and investor communications

- **URLs (Companies House landing for each):** Capita, Capgemini, Atos, DXC, Fujitsu, IBM, Sopra Steria, Babcock, BAE Systems, Leidos, KBR, Thales, Serco, Mears, Clearsprings.
- **What it publishes:** Annual report and accounts (full PDF/iXBRL) + investor presentations + earnings call transcripts. Strategic suppliers frequently disclose named contract wins, named departments, and named programmes — sometimes well before the formal contract notice.
- **Sub-org granularity:** Mixed but often strong for headline contracts. "We were awarded a five-year extension by UKVI for…"
- **Action:** Targeted PDF/iXBRL pull for the 13 tech strategic suppliers + the asylum accommodation primes + the defence top-5.

#### E2. Supplier press releases, case studies, blog posts

- **What it publishes:** Self-promotional case studies that frequently name the buyer at sub-organisation level (case studies are *more* granular than press releases — naming the actual unit and use case).
- **Sub-org granularity:** Strong but cherry-picked.
- **Use:** Triangulation.

#### E3. LinkedIn — supplier deal announcements + senior staff role transitions

- **What it publishes:** Public posts from supplier business development leads announcing wins, plus the LinkedIn job-history of the senior civil servants in the target sub-orgs (this is how the SRO of FBIS gets confirmed publicly).
- **Sub-org granularity:** Variable, not systematic.

#### E4. Trade body publications — techUK, ADS, SBS, CompTIA

- **techUK:** https://www.techuk.org/ — publishes a Strategic Suppliers reference (the 39-supplier list with the 13 tech firms identified), Cabinet Office market engagement event reports, and quarterly central government programme briefings.
- **ADS:** https://www.adsgroup.org.uk/ — defence and aerospace trade body. Publishes Defence Sourcing Portal guidance and supplier engagement material.
- **Sub-org granularity:** Cabinet Office and MOD oriented; rarely names UKVI or Defence Digital specifically.

### Tier F: FOI portals and request infrastructure

#### F1. WhatDoTheyKnow

- **URL:** https://www.whatdotheyknow.com/
- **What it publishes:** Public archive of FOI requests and responses across all UK public bodies. Operated by mySociety.
- **Sub-org granularity:** As-asked. Many requests target specific sub-orgs ("FOI request to UKVI…").
- **Cadence:** Continuous.
- **Access:** Free public web. **API available** at https://data.mysociety.org/datasets/whatdotheyknow-api/ for programmatic access. RSS / JSON feeds documented.
- **Quality issues:** Highly variable. Some responses are PDFs of tabulated supplier spend (gold), others are refusals citing exemption (useless).
- **Action:** Build a search-watch on the priority sub-orgs and ingest hits.

#### F2. Direct FOI to Home Office and MOD

- **Use case:** Where a public-record gap is consistent (e.g. UKVI supplier ledger), submit an FOI request asking for the ledger directly. Departments routinely fulfil supplier-spend FOI for transparency reasons.
- **Cost:** Time to draft + 20-day statutory wait + risk of refusal or partial release.

### Tier G: Sources actively considered and rejected as low value for sub-org intelligence

| Source | Why not |
|---|---|
| **Migration transparency data (operational only)** | Operational metrics, not procurement. Already noted in B6 as context-only. |
| **Frost & Sullivan / Holon IQ UK government** | Generic global-vendor analyst content; not UK-public-sector-granular. |
| **PublicSpend Forum** | US-government focused. |
| **GovShop / OpenOpps free tier** | Adds nothing over our existing FTS / Contracts Finder ingest at sub-org level. |

---

## 3. Sub-organisation findings

### 3.1 What we can know about UKVI from the public record

**Strong / structured:**
- **Transactional supplier spend** above £25k from the Home Office spend dataset, where UKVI is a named Entity. With monthly cadence and a 1–3 month lag.
- **Major programme cost envelopes** for FBIS (£3.8bn), IPT, Atlas — surfaced in GMPP records, ARA narrative, and NAO reports.
- **Senior staff and organisational structure** from Home Office organograms — twice-yearly snapshots with named directors.
- **Operational performance** (volumes, processing times, casework metrics) from quarterly migration transparency data. Sets the buyer-need context.

**Strong / narrative:**
- **Named contract awards** for the headline tech programmes — the £85m FBIS architecture deal, the £120m FBIS systems integration deal, the Capgemini £37m border DevOps deal, the £25m border transformation contract — surfaced in trade press and (after the fact) in Find a Tender.
- **Asylum accommodation** — Serco, Mears Group, Clearsprings Ready Homes plus Migrant Help on the helpline. Original 10-year envelope £4.5bn revised to £15.3bn through 257 contract modifications. Dense NAO and PAC coverage.
- **Skilled Worker visa system** weaknesses (no exit checks 2020-2024) — PAC coverage.
- **Programme leadership** — Simon Bond appointed as SRO of FBIS in April 2026. LinkedIn confirms this.

**Weak or missing:**
- **Long-tail supplier list** — anyone below the top 20 isn't reliably visible without the £25k spend ingest.
- **Sub-£25k spend** — invisible to transparency reporting. UKVI almost certainly runs hundreds of small consultancy and digital service contracts under threshold.
- **In-flight contract values vs paid-to-date** — transparency data is paid invoices; we don't see the contract envelope without the FTS notice or a separate reference.
- **Internal contract management performance** — never publicly disclosed beyond NAO commentary.
- **UKVI's own ARA** — UKVI does not publish its own annual report; sits inside Home Office ARA. So no top-supplier list scoped specifically to UKVI from official sources.

### 3.2 What we can know about Defence Digital from the public record

**Strong / structured:**
- **Major programme cost envelopes and delivery confidence ratings** for Skynet 6 (>£5bn over 10 years), Morpheus, and others — directly tagged to Defence Digital in GMPP returns.
- **Tendered opportunities and recent awards** via the Defence Sourcing Portal — Defence Digital is named as the requesting authority on many notices not duplicated to FTS.
- **Defence Digital headline budget** — £2.7bn IT envelope confirmed in PAC report and trade press; total digital spend across MOD ~£4.4bn.
- **Headcount** — ~2,400 staff (military, civil servants, contractors) confirmed in PAC report.
- **Senior structure** — CIO sits on Executive Committee, reports to Strategic Command commander and second permanent secretary. Defence Digital now sits inside the National Armaments Directorate Group (NADG) alongside DE&S, Dstl, DIO, SDA.
- **Engagement with industry** — Defence Digital ran 40+ strategic market engagements in 2025, onboarded ~200 new suppliers, SMEs make up 45% of digital supplier base.

**Strong / narrative:**
- **Strategic Suppliers' MOD engagement** — top-10 published annually in MOD Trade, Industry and Contracts. Defence Strategic Suppliers (Babcock, KBR, Leidos, BAE, Thales) saw spend roughly flat in real terms FY19/20 → FY24/25.
- **Top-5 supplier concentration** — over 29% of MOD procurement spend goes to 5 firms; 10 frameworks awarded over £6bn in FY24/25.
- **Non-competitive contracts** — 39% of MOD contracts awarded without competition in 2022-23 (SSRO data) — important context for any Defence Digital incumbency story.

**Weak or missing:**
- **Defence Digital own-name supplier ledger** — does not exist openly. Spend data CSVs roll up to TLB (Strategic Command), not below.
- **Programme-supplier mapping at line-item level** — Skynet 6 → Babcock / Airbus / Viasat is partly known from press but not from a structured source.
- **In-year tracking** — GMPP is annual snapshots only.
- **Single-source contract item-level data** — held by SSRO in DefCARS but not publicly released at item level. Significant blind spot for ~39% of MOD spend.
- **Defence Digital's own ARA** — does not exist; absorbed into MOD ARA narrative.

### 3.3 Biggest known unknowns

For **UKVI**:
1. The total annual supplier ledger at line-item level beyond what the £25k transparency feed publishes — sub-£25k spend is genuinely invisible.
2. Which supplier holds which slice of the FBIS / Atlas / IPT / NPI portfolio at any given moment — pieced together from trade press, never from a single canonical source.
3. The unpublished commercial pipeline (procurements <£2m) that doesn't trigger a Find a Tender pipeline notice.

For **Defence Digital**:
1. The Defence-Digital-specific spend envelope below TLB level — has to be inferred from PAC numbers + spend Expense Area heuristics + DSP notice activity.
2. Single-source contracts to Defence Digital (the ~39% non-competitive segment) — DefCARS has it, the public doesn't.
3. The line-item composition of Skynet 6, Morpheus, Defence Cyber and similar programmes — multiple primes and dozens of subcontractors per programme; surfaced in fragments.

---

## 4. Ingestion roadmap

### Wave 1 — Highest leverage, lowest engineering effort (next 2–4 weeks)

**1.1 Departmental £25k spend ingest, with Entity column as sub-org primary key**
- Targets: Home Office (UKVI, Border Force, HMPO, Immigration Enforcement, DBS), MOD (Strategic Command, Army, Navy, RAF, DE&S, DIO, DNO, Head Office), MoJ (HMPPS, HMCTS, LAA, OPG — even though MoJ doesn't break these out in FTS, they often do in spend), Cabinet Office.
- Build a monthly poller against the gov.uk publication URLs.
- Parse the CSVs (handle the column-name and date-format inconsistencies that vary month to month).
- Run the supplier names through the existing Splink canonical layer.
- **Schema add:** new `transparency_spend` table joined to `canonical_suppliers` and a new `sub_org_entity` dimension. Sub-org entity is freeform but joinable to canonical buyer where possible.

**1.2 GMPP annual ingest**
- Pull the latest annual GMPP CSV per priority department.
- New `gmpp_projects` table with sponsoring department, sponsoring agency / sub-org, project name, WLC, snapshot date, delivery confidence rating.
- Annual refresh job.

**1.3 Departmental organogram ingest**
- Twice-yearly poll for Home Office, MOD, MoJ, HMPPS, Dstl, DE&S organogram CSVs.
- New `senior_civil_servants` table tagged to sub-org.
- Feeds the Win Strategy stakeholder map directly.

### Wave 2 — Narrative and PDF sources (4–8 weeks)

**2.1 NAO + PAC reports archive**
- Pull all reports from priority departments.
- Run named-entity extraction over PDFs to find supplier names, programme names, and amounts, tagged to the report's scope.
- New `narrative_evidence` store keyed by source, date, sub-org, and entities mentioned.

**2.2 Hansard PQ topic-watch**
- Use TheyWorkForYou's stable URL pattern.
- Watch terms: UKVI, Border Force, FBIS, Atlas, Defence Digital, Skynet, Morpheus, plus the strategic-supplier names.
- New `pq_responses` store.

**2.3 ICIBI inspection reports archive**
- Pull all inspection reports.
- Tag to UKVI / Border Force / Immigration Enforcement / HMPO.
- Add to narrative_evidence store.

**2.4 Departmental and agency ARAs**
- Pull the latest ARA per priority department + per priority agency (HMPPS, Dstl, DE&S).
- Extract top-supplier disclosures and major programme commentary.
- Refresh annually.

### Wave 3 — Trade press and supplier-side (8–12 weeks)

**3.1 Trade press feed ingest**
- ComputerWeekly, The Register, PublicTechnology, UKAuthority, UK Defence Journal, Civil Service World.
- RSS / Atom where available, deterministic scrape where not.
- Run NER over headlines and body to capture (supplier, sub-org, amount, date).

**3.2 Strategic supplier annual report extraction**
- The 13 tech strategic suppliers + the 5 defence strategic suppliers + the 4 asylum accommodation primes.
- Pull iXBRL where available, PDF where not, from Companies House.
- Annual cadence.

### Wave 4 — Commercial intelligence (decision required)

**4.1 Tussell or TechMarketView trial**
- Buy short-term access to one of these and benchmark against the open-source stack we've built. Specifically test: do they have a Defence-Digital-specific spend rollup, and a UKVI-specific spend rollup, that beats what Wave 1 + Wave 2 give us?
- Make a buy / build decision based on the gap.

### Wave 5 — Targeted FOI (continuous, low cost)

**5.1 FOI watch + targeted requests**
- WhatDoTheyKnow API watch on priority sub-orgs.
- Quarterly drafting of own FOIs to fill the worst gaps (e.g. "UKVI total spend with each of the strategic suppliers FY22 → FY25").

### Connecting to the existing canonical buyer layer

The existing canonical buyer layer is at parent-department level for the three problem departments. The sub-org overlay should be modelled as a **child** dimension that hangs off the canonical buyer rather than replacing it. Concretely:

- Keep `canonical_buyers` as-is (parent-department canonical entities — already 70.3% award-weighted coverage).
- Add `canonical_sub_orgs` table: id, parent canonical buyer id, sub-org name (canonical), aliases array.
- Each Wave 1+ source ingest produces `(canonical_buyer_id, canonical_sub_org_id, supplier_id, amount, date, source_type)` tuples written to a new `sub_org_evidence` table.
- Existing `get_buyer_profile` MCP tool gains an optional `sub_org` argument; when supplied, it joins evidence from the new tables in addition to the FTS / Contracts Finder award data.
- For the three problem departments, the sub-org dossier is the *primary* artefact; for departments where FTS already breaks out the agencies, sub-org evidence is a supplementary signal.

---

## 5. Notable findings flagged for visibility

- **The £25k spend transparency CSV's Entity column is the single most underused source we're not yet reading.** It is the only structured, machine-readable, monthly-cadence feed that names UKVI, Border Force, HMPO and similar Home Office sub-orgs as discrete entities. Tussell's whole match advantage on these departments rests on it. Ingesting it ourselves removes a substantial part of Tussell's commercial moat for our use case.
- **GMPP records explicitly tag MOD projects to Defence Digital.** Skynet 6 is named as Defence Digital-owned on the public GMPP file, which is more granular than anything in FTS or the £25k feed. The supplier names are absent from GMPP (frustrating) but the programme list itself is the spine on which to hang trade-press-derived supplier evidence.
- **SSRO / DefCARS is the structural blind spot.** ~39% of MOD contracts are non-competitive and DefCARS is where they go. The public release is aggregate only; item-level is held back. This is the single biggest gap in our Defence Digital coverage and no amount of clever ingest from open sources closes it.
- **NISTA replaced IPA on 1 April 2025.** The annual project portfolio publication is now a NISTA product. The 2024-25 NISTA Annual Report covers 213 projects, total whole-life cost £996bn, monetised benefits £742bn. Update product copy and any references in code/docs to use NISTA terminology where speaking about post-2025 reports.
- **The 39 strategic suppliers' share of public procurement fell to a five-year low of 10% in FY24/25 (£249bn total).** £41.7bn of strategic supplier contracts expire this Parliament, £12.8bn in 2026 alone — this is highly relevant pipeline context for the Win Strategy product and worth surfacing prominently to consultants.
- **HMPPS publishes its own ARA** (HMPPS Annual Report and Accounts 2024-25) even though it does not publish its own contract notices. Ingesting agency-level ARAs is a partial workaround for the MoJ sub-org publishing gap, with the same logic applicable to Dstl, DE&S, DBS, OPG, LAA inside their parents.

---

## Sources

- [Home Office spend over £25,000 dataset (data.gov.uk)](https://www.data.gov.uk/dataset/ecc70eba-dbf2-4bba-9f04-415cbe845118/spend-over-25-000-in-the-home-office)
- [MOD spending over £25,000 — 2025](https://www.gov.uk/government/publications/mod-spending-over-25000-january-to-december-2025)
- [MOD finance transparency dataset collection](https://www.gov.uk/government/collections/mod-finance-transparency-dataset)
- [MOD Government Major Projects Portfolio data, 2024](https://www.gov.uk/government/publications/mod-government-major-projects-portfolio-data-2024)
- [NISTA Annual Report 2024-25](https://www.gov.uk/government/publications/nista-annual-report-2024-2025)
- [MOD trade, industry and contracts: 2025](https://www.gov.uk/government/statistics/mod-trade-industry-and-contracts-2025/mod-trade-industry-and-contracts-2025)
- [MOD departmental resources: 2025](https://www.gov.uk/government/statistics/defence-departmental-resources-2025/mod-departmental-resources-2025)
- [Single Source Regulations Office](https://www.ssro.gov.uk/)
- [Defence Sourcing Portal](https://www.contracts.mod.uk/)
- [Crown Commercial Service annual report 2024-25](https://www.gov.uk/government/publications/crown-commercial-service-annual-report-and-accounts-2024-to-2025)
- [Home Office annual report and accounts 2024-25](https://www.gov.uk/government/publications/home-office-annual-report-and-accounts-2024-to-2025)
- [Ministry of Defence annual report and accounts 2024-25](https://www.gov.uk/government/publications/ministry-of-defence-annual-report-and-accounts-2024-to-2025)
- [HMPPS annual report and accounts 2024-25](https://www.gov.uk/government/publications/hmpps-annual-report-and-accounts-2024-to-2025)
- [NAO — An analysis of the asylum system (Dec 2025)](https://www.nao.org.uk/reports/an-analysis-of-the-asylum-system/)
- [NAO — Home Office's asylum accommodation contracts (May 2025)](https://www.nao.org.uk/wp-content/uploads/2025/05/home-offices-asylum-accommodation-contracts.pdf)
- [NAO — Home Office 2024-25 overview (Oct 2025)](https://www.nao.org.uk/overviews/home-office-2024-25/)
- [NAO — Ministry of Defence Accounts 2024-25](https://www.nao.org.uk/reports/ministry-of-defence-accounts-2024-25/)
- [PAC — The Defence digital strategy](https://publications.parliament.uk/pa/cm5803/cmselect/cmpubacc/727/report.html)
- [Independent Chief Inspector of Borders and Immigration — inspection reports](https://www.gov.uk/government/collections/inspection-reports-by-the-independent-chief-inspector-of-borders-and-immigration)
- [Migration transparency data](https://www.gov.uk/government/statistical-data-sets/migration-transparency-data)
- [Hansard — written answers search](https://hansard.parliament.uk/search/WrittenAnswers)
- [TheyWorkForYou written answers](https://www.theyworkforyou.com/written-answers-and-statements/)
- [WhatDoTheyKnow API](https://data.mysociety.org/datasets/whatdotheyknow-api/)
- [techUK — Strategic Suppliers analysis](https://www.techuk.org/resource/the-uk-government-s-strategic-suppliers-what-tech-firms-need-to-know.html)
- [Tussell — 2025 Analysis of UK Government Strategic Suppliers](https://www.tussell.com/insights/uk-government-strategic-suppliers)
- [Tussell — UK Public Sector Defence Procurement Tracker](https://www.tussell.com/insights/defence-procurement-tracker)
- [Tussell — Procurement Profile: Ministry of Justice](https://www.tussell.com/insights/procurement-profile-ministry-of-justice)
- [Stotles spend data documentation](https://help.stotles.com/spend-data)
- [Spend Network](https://www.spendnetwork.com/)
- [Open Opportunities](https://openopps.com)
- [Defence Contracts International](https://www.dcicontracts.com/)
- [JOSCAR / Hellios](https://hellios.com/joscar)
- [The Register — UK Home Office border contract coverage](https://www.theregister.com/2024/10/29/home_office_seeks_border_crossing_tech_help/)
- [PublicTechnology — £85m Home Office digital deal](https://www.publictechnology.net/2025/03/20/international-relations/home-office-signs-85m-digital-deal-to-support-consistent-repeatable-architecture-for-border-it-systems/)
- [Defence Digital blog — MoD Digital Commercial end-of-year message 2025](https://defencedigital.blog.gov.uk/2025/12/19/mod-digital-commercial-end-of-year-message-to-industry-delivering-digital-advantage-together/)
- [Civil Service organisation charts (organograms) — Cabinet Office example](https://www.data.gov.uk/dataset/ff76be1f-4f37-4bef-beb7-32b259413be1/organogram-cabinet-office)
- [Commercial pipeline guidance (Cabinet Office)](https://www.gov.uk/government/publications/commercial-operating-standards-for-government/commercial-pipeline-guidance-v7-html)
- [Contracts Finder API documentation](https://www.contractsfinder.service.gov.uk/apidocumentation)
- [SKYNET 6 — gov.uk guidance](https://www.gov.uk/guidance/skynet-6)
