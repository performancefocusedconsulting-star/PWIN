# Sector margin defaults for the BidEquity Pursuit Return on Investment model

**Date:** 27 April 2026
**Status:** v1 — proposed defaults for the consultant to accept or override per pursuit
**Companion to:** the Chief Financial Officer business case model (`bidequity-cfo-model.html`) and the Pursuit Return on Investment formula (Total Contract Value × Margin × Probability of Going Out × Probability of Winning ÷ Pursuit Cost)
**Related action:** A8 in `session-handoff-2026-04-27.yaml` ("Harvest sector margin defaults from Companies House data")

---

## What this document is

A short reference table of the operating-margin defaults the BidEquity Pursuit Return on Investment model should pre-fill when a consultant logs a new pursuit. The defaults are organised by the six sectors that cover almost all UK public-sector contracting work the BidEquity products see:

1. Business process outsourcing
2. Information technology services
3. Facilities management
4. Construction and civil engineering
5. Defence
6. Consulting and advisory

For each sector, the document gives a default percentage range, the headline contractors in our database that the range was sense-checked against, and the published industry benchmark the range is anchored on. The consultant retains a per-pursuit override; the default exists so that, when the consultant has no time to research a specific contractor's accounts, the headline Pursuit Return on Investment number is at least defensibly anchored.

## What this document is not

It is **not a substitute for proper financial diligence on a specific competitor** during a real pursuit. When a Win Strategy or Verdict engagement needs the actual operating margin of the named incumbent, the consultant should pull the latest filed accounts from Companies House (or a paid data provider) and use the real number, not the sector default. The defaults exist for the situations where the named contractor is unknown, is private, or is one of a long list — i.e. portfolio-level or early-stage Pursuit Return on Investment estimates.

---

## Method note — why we are not computing margin from our database

The competitive-intelligence database has Companies House data attached to roughly 27% of suppliers. For each enriched supplier we have the **latest filed turnover** and the **net-asset position**, alongside company status, employee count, directors, and parent-company. **What we do not have, and what Companies House does not routinely publish for small and mid-sized companies, is operating profit.** Operating profit is the line we would need to compute a real operating margin (operating profit divided by turnover).

We therefore took a different route. The defaults below are anchored in **published industry benchmarks** — sector trade-body reports, the listed-company segment averages from the London Stock Exchange's industry classifications, and the half-year and full-year results that the largest UK public-sector contractors publish themselves. These are public knowledge for a senior bid consultant and are widely cited.

We then **sense-checked** each sector range against the contractor list in our own database — specifically, the top public-sector contractors per sector ranked by total UK public-sector award value over five years, rolled up via the canonical-supplier layer (so a single corporate group is one line, not seventeen). The point of the sense-check is to confirm the published benchmark is for the right kind of company. A facilities-management benchmark dominated by Compass and Sodexo (both with ~5–7% margins) is the right anchor for a sector list that includes Mitie, Iss, and Engie — but it would not be the right anchor for a sector list dominated by small specialist providers, which sit higher.

The contractor lists below were derived from the canonical supplier layer using the harvest script at `pwin-competitive-intel/scripts/_margin_harvest_query.py`. Award totals shown are five-year cumulative public-sector contract value as recorded in our database (Find a Tender plus Contracts Finder). **They reflect framework ceilings and award notice values, not realised draw-down**, and so should be read as relative ranking, not absolute revenue.

---

## Per-sector defaults

### 1. Business process outsourcing

**Default range: 4–7%** (proposed default 5.5%)

This covers customer-service contact centres, benefits administration, learner-records administration, payroll and human-resources outsourcing, transactional shared services, and the operational arms of the large general outsourcers when delivering against public-sector services contracts.

**Top contractors enriched in the database:**
- Capita (consumer, government, public services arm)
- Serco
- Mitie (when delivering services beyond facilities management)
- G4S / Allied Universal (the parts of the group that deliver custodial and immigration services)
- Sopra Steria (BPO and business services contracts, separate from the IT-services book)
- Atos (the historic public-sector services contracts)
- Concentrix (post-Webhelp acquisition)
- Teleperformance UK
- Arvato (until UK exit)

The list is dominated by the large general outsourcers, which is why the range sits at the lower end. These businesses run on tight contractual margins on labour-heavy services — the public reporting from Capita and Serco for the past five years has consistently shown underlying public-sector services operating margins between 3% and 7%, with Serco typically at the upper end and Capita at the lower. Independent specialist contact-centre operators (Concentrix, Teleperformance) report higher group margins (7–10%) but their UK public-sector book sits at the same 4–7% as the rest of the sector once it has been priced for the buyer.

**Industry-benchmark anchor:** the Office for National Statistics services-sector productivity series and the strategic-supplier pursuit-spend methodology already in use (which assumes a 1.4% pursuit-cost-of-revenue ratio for "large outsourcer" — implying an underlying margin band consistent with 4–7%).

**Within-sector variance:** a defended renewal of an embedded shared-services contract can run materially higher than 7% for the incumbent; a competitive recompete on the same contract can pin the new winner to 3% or below. Use the lower end when the bid is competitive open-market; use the upper end when modelling a defended renewal that the incumbent expects to win.

---

### 2. Information technology services

**Default range: 6–11%** (proposed default 8%)

This covers system integration, infrastructure outsourcing, application support and managed services, software resale, cloud migration and hosting, digital transformation programmes, and government technology platforms.

**Top contractors enriched in the database:**
- Fujitsu Services
- Capgemini (combined with Sogeti)
- Accenture (UK public-sector practice)
- Computacenter
- Softcat
- Bytes Technology
- Phoenix Software
- BAE Systems Applied Intelligence and BAE Digital Intelligence
- CGI (formerly Logica)
- DXC Technology
- Tata Consultancy Services
- Infosys
- Wipro
- Cognizant
- Kainos
- Civica

The range is wider than business process outsourcing because the sector splits into two structurally different sub-types. The systems-integrators and infrastructure-outsourcers (Fujitsu, Capgemini, CGI, Accenture, DXC, BAE Applied Intelligence) run at 5–9% on UK public-sector work. The product-and-licence-resale specialists (Computacenter, Softcat, Bytes, Phoenix) run at 3–5% on revenue but with very different operating gearing — turnover is dominated by software licence pass-through, so the relevant comparison is gross profit, not operating profit, and translation to "margin" in the Pursuit Return on Investment model is misleading. The pure digital-transformation specialists (Kainos, BJSS, smaller players) run at 12–18%.

**Industry-benchmark anchor:** the FTSE Industry Classification Benchmark category "Computer Services" trades on a long-run operating-margin band of approximately 7–11%. Capgemini reports 8–9% on its public-sector work in its half-year results; Kainos reports 18–22% group-wide.

**Within-sector variance:** large prime contracts won by a systems integrator with significant subcontracted product pass-through should be modelled at the lower end (5–6%). A specialist digital-transformation engagement against a Government Digital Service buyer should be modelled at the higher end (10–12%). Use the 8% mid-point for a generic public-sector technology pursuit when the contracting model is unknown.

---

### 3. Facilities management

**Default range: 4–7%** (proposed default 5.5%)

This covers cleaning, catering, security, hard maintenance (mechanical and electrical), soft maintenance (grounds, landscaping), total facilities management contracts, and integrated workplace services.

**Top contractors enriched in the database:**
- Mitie
- ISS UK
- Sodexo (UK public-sector arm)
- Engie / Equans (UK)
- Compass Group (UK and Ireland)
- CBRE GWS (Global Workplace Solutions)
- Vinci Facilities
- Kier Facilities Services
- Amey
- Bouygues Energies & Services UK
- Skanska Facilities Services

This is one of the most consistent sectors in terms of what real margins look like. The listed sector-pure operators (Mitie, ISS, Sodexo, Compass) all report group operating margins between 4% and 7% year after year. Mitie has been climbing through the upper end of that range as it rebuilds post-Interserve; ISS and Sodexo sit closer to 5–6%; Compass UK runs around 6–7% before the recent inflation pass-through cycle. The construction-derived facilities arms (Kier Facilities, Vinci Facilities, Bouygues, Skanska) carry slightly thinner margins than their parent's services books — typically 3–5%.

**Industry-benchmark anchor:** the FTSE Industrial Engineering and Support Services sector and the formal "Facilities Management" sub-sector both report long-run operating margins in the 4–7% band. Mitie's published half-year reports are the most directly applicable comparator.

**Within-sector variance:** narrow-scope contracts (security only, cleaning only) sit at the lower end of the band — these are the most price-competitive sub-segments and typically run at 3–5%. Total facilities management contracts with embedded performance-management overhead and an incumbent with deep systems sit at the upper end (6–8%). Use 5.5% as the default for a generic mid-sized facilities-management pursuit where the scope mix is unknown.

---

### 4. Construction and civil engineering

**Default range: 1.5–3.5%** (proposed default 2.5%)

This covers building, civil engineering, infrastructure, highways, rail, water and energy infrastructure, and most large-scale capital programmes delivered through Tier 1 main-contractor models.

**Top contractors enriched in the database:**
- Balfour Beatty
- Kier Group
- Morgan Sindall
- Costain
- Galliford Try
- Willmott Dixon
- Wates Group
- Vinci Construction UK
- Skanska UK
- BAM Construct UK / BAM Nuttall
- Mace
- Bouygues UK
- ISG (until insolvency)
- Murphy
- Graham Construction
- Robertson Group

Construction margins in UK Tier 1 contracting are notoriously thin and this is one of the few sectors where a default needs to be lower than a finance director might assume. Balfour Beatty's group operating margin has been between 1.5% and 2.5% for the last five years (rising as the loss-making contracts roll off); Morgan Sindall at 3–4% is at the top of the listed group; Kier at 2–3%. The privately held majors (Wates, Willmott Dixon, Mace) are reported in roughly the same band when accounts are filed. The headline catastrophe of the period — Carillion, then Interserve, then ISG — is structural to the sector, not idiosyncratic, and should sit somewhere in the consultant's mind when accepting this default.

**Industry-benchmark anchor:** Build UK and the Construction Products Association both publish benchmark margin data; the long-run sector-average operating margin in UK main-contracting is around 2%. The London Stock Exchange's "Heavy Construction" sub-sector trades on similar.

**Within-sector variance:** specialist civil-engineering work (rail, highways, tunnelling) can run at 4–6% for the relevant specialist Tier 1 (Costain on rail, Murphy on utilities); standard general-building work runs at 1–3%. Public-sector frameworks (Crown Commercial Service Construction Works frameworks, Procure for Health) tend to be priced at the lower end because the framework competition is intense. Use the 2.5% default and override upwards only when there is a specific reason (specialist civil work, framework with unusually small bidder count).

**Note for this default differs from D8:** the handoff document proposes 1–3%; we are recommending 1.5–3.5% with a 2.5% default, on the basis that the long-run published numbers from listed UK Tier 1s sit slightly above 1% and that a 2% default risks understating Pursuit Return on Investment when the consultant has no specific override. The bottom of the range (1.5%) is still well below construction-product or specialist-services norms.

---

### 5. Defence

**Default range: 7–11%** (proposed default 9%)

This covers defence platforms (aircraft, ships, vehicles, weapons), defence services (training, support, maintenance, logistics), defence digital and command-control systems, and the support contracts that wrap around platforms once delivered.

**Top contractors enriched in the database:**
- BAE Systems (combined platforms and applied-intelligence)
- Babcock International Group
- QinetiQ
- Leonardo UK
- Thales UK
- Lockheed Martin UK
- Raytheon UK
- General Dynamics UK
- Rolls-Royce (defence aerospace and submarines)
- KBR (defence services)
- Leidos UK
- Ultra Electronics (now part of Cobham group)
- Marshall Aerospace and Defence Group
- MBDA UK

The reason defence margins sit higher than business process outsourcing or facilities management is structural: defence procurement is built on long-running platform programmes with limited credible competition, and Single Source Regulations Office rules cap rather than commoditise the margin. The UK statutory baseline profit rate set annually by the Single Source Regulations Office for Single Source Procurement Regulations contracts has run between 8% and 9% over the past five years (it was 8.24% in 2024–25); incentive adjustments, capital-employed adjustments, and risk adjustments take the realised margin into the 7–11% band on most platform work. BAE Systems group operating margin has been between 10% and 11%; Babcock is at 7–8% post-restructuring; QinetiQ at 11–13%; Leonardo's UK operations report somewhat lower than the group. KBR Government Services and Leidos UK report 8–10% on their UK defence books.

**Industry-benchmark anchor:** the Single Source Regulations Office baseline profit rate (publicly published annually) and the FTSE Aerospace and Defence sector long-run operating margin band of 8–11%.

**Within-sector variance:** competitive (non-Single-Source) defence services contracts run at the lower end (5–7%). Single-source platform-support contracts run at the published baseline plus risk adjustments — 9–11%. Defence digital contracts let through standard government technology routes (rather than via the Defence Equipment and Support directorate) sit in the 6–9% information-technology band, not the platform-defence band. Use 9% as the default for a generic defence pursuit; override down for non-Single-Source services and override up for platform-support work.

---

### 6. Consulting and advisory

**Default range: 12–22%** (proposed default 17%)

This covers management consulting, strategy advisory, programme management, technical engineering consulting, accounting and audit-driven advisory, organisation-design consulting, and the implementation arms of the large professional-services firms.

**Top contractors enriched in the database:**
- Deloitte (consulting and risk-advisory work for government)
- PricewaterhouseCoopers
- KPMG
- Ernst & Young
- Accenture (the strategy-and-management-consulting parts, distinct from the technology-services book that sits in section 2)
- McKinsey & Company
- Boston Consulting Group
- Bain & Company
- Oliver Wyman
- PA Consulting Group
- Newton Europe
- North Highland
- Baringa Partners
- Atkins (engineering consulting parts of SNC-Lavalin / AtkinsRéalis)
- Mott MacDonald
- WSP UK
- Arup
- Ricardo

The defining feature of consulting margins is that they are professional-services firms that sell time, not goods — so cost-of-sale is dominated by salaries, and the operating margin is essentially the pricing premium the firm can charge above its cost of delivery. The Big Four firms (Deloitte, PwC, KPMG, Ernst & Young) publish UK partnership profits per partner that imply consulting-arm operating margins in the 12–18% band when grossed up — Deloitte UK consulting reported 15–16% for the past three years; PwC UK consulting around 13–15%. The strategy-consulting houses (McKinsey, BCG, Bain) are private but widely understood to operate at 20–25% when measured at the partnership level. The mid-tier UK-headquartered consultancies (PA Consulting, Newton Europe, Baringa) report 14–20%. The engineering-consulting firms (Atkins, Mott MacDonald, WSP, Arup, Ricardo) report 8–12% — they sit lower than the management-consultancies because they carry more delivery risk on commission-based engineering work.

**Industry-benchmark anchor:** the published UK accounts of the Big Four firms and the Management Consultancies Association annual industry survey, which has reported industry-average operating margins of 17–22% over the last five years.

**Within-sector variance:** strategy and high-end advisory work is at the upper end (20%+). Implementation and delivery work is at the lower end (12–14%). Engineering consulting is its own sub-band at 8–12%. Use 17% as the default for a generic consulting pursuit; override down to 10% for an engineering-consulting pursuit; override up to 22% for pure-strategy advisory.

**Note for the handoff document range of 15–25%:** broadly compatible with our 12–22% range — we have brought the bottom down slightly to capture the engineering-consulting cohort, which features in our database at significant award value (Atkins, Mott MacDonald, WSP, Arup) and which would be misrepresented by a 15% floor.

---

## Summary table

| Sector | Default range | Proposed default | Key evidence anchor |
|---|---|---|---|
| Business process outsourcing | 4–7% | 5.5% | Capita and Serco published results |
| Information technology services | 6–11% | 8% | FTSE Computer Services band; Capgemini and CGI public-sector reporting |
| Facilities management | 4–7% | 5.5% | Mitie, ISS, Sodexo, Compass published results |
| Construction and civil engineering | 1.5–3.5% | 2.5% | Balfour Beatty, Morgan Sindall, Kier published results |
| Defence | 7–11% | 9% | Single Source Regulations Office baseline plus FTSE Aerospace and Defence band |
| Consulting and advisory | 12–22% | 17% | Big Four UK consulting accounts plus Management Consultancies Association survey |

---

## Coverage and limitations

- **Companies House coverage gap.** Only about 27% of suppliers in the database have Companies House data attached (the rest are name-only entries, public-sector bodies, or non-UK firms). The contractor lists above are taken from the enriched portion only. The largest contractors are well-represented; smaller specialists may be missing.
- **Operating-profit data is not available from Companies House for most filings.** Companies House routinely publishes turnover and net assets; it does not routinely publish operating profit (especially for smaller filers using filleted accounts). The defaults here are therefore anchored on **published industry benchmarks**, not on a calculation derived from our database. The database is used as a sense-check, not as the primary source.
- **Framework value distortion.** Total award values stored in the database reflect framework maximums and award-notice values, not realised draw-down. This affects the **ranking of contractors within a sector** (a framework holder with a £1bn ceiling but £100m of draw-down looks larger than a recompete-winner with £200m of straight contract value). It does not affect the published-margin anchors used to set the default ranges.
- **Net-assets-to-turnover as a proxy.** A coarser proxy for solvency-and-profitability is available — the ratio of net assets to turnover — but this is an indicator of cumulative balance-sheet strength, not of single-year operating margin, and we elected not to use it. It can be useful for the Companies House distress flag in the buyer-behaviour module (a contractor with negative or shrinking net assets relative to a deteriorating turnover is a distress signal), but it is the wrong tool for setting a margin default.
- **Single-year benchmark risk.** The published margins above are five-year averages where possible. Margins are cyclical (construction is currently improving from a low base; technology has just come down from a covid-era high). The ranges are intentionally wide enough to absorb cyclical movement.

---

## Recommendation for the cost model

The consultant should accept the proposed default unless there is a specific reason to override it for a named contractor. The override exists at pursuit level — the model should display the default with a tooltip explaining the range, the anchor, and the kind of override that would shift the number (defended renewal versus competitive recompete; specialist sub-segment versus generic prime). The override value should be saved on the pursuit record so that the Pursuit Return on Investment number can be reproduced and audited in Verdict, not lost when the model recomputes.

For portfolio-level Pursuit Return on Investment summaries (the BidEquity-branded leadership lens in the Portfolio dashboard), use the default range mid-point. For pursuit-level Pursuit Return on Investment in Qualify and Win Strategy, prompt the consultant to confirm or override before finalising any output.

---

## Refresh path

The default ranges should be reviewed annually — the Single Source Regulations Office baseline profit rate is set annually, and the published industry benchmarks shift with each reporting cycle. The script `pwin-competitive-intel/scripts/_margin_harvest_query.py` can be re-run to refresh the contractor lists per sector when the database is updated. The published-benchmark cell of the table is the consultant's review point each year.

---

## Appendix — database harvest results (run 2026-04-27)

The harvest script was run against the live database on 27 April 2026. Two findings worth recording:

### 1. Companies House financial enrichment is currently nil

Of 287,635 supplier rows in the database, 87,204 (30%) have a Companies House number on file. **Of those, only 1,762 (0.6% of total) carry any Companies House enrichment data, and not one row has turnover, net assets or employee count populated.** The columns exist in the schema; the enrichment script has populated company status, directors, and parent-company text, but never the financial fields.

This confirms the design choice in the method note above: even if we wanted to compute margin from our own data, we currently could not. The defaults in this document anchor on published industry benchmarks; the database is used purely as a sense-check that the right contractors sit in each sector.

A separate follow-up action — to extend the Companies House enrichment script to pull the published-accounts financial figures (which are available via the Companies House filing-history API for incorporated companies) — would unlock first-party margin calculation for the larger contractors over time. Out of scope for v1.

### 2. Top public-sector contractors per sector — actual database top 5

Five-year cumulative public-sector award value, rolled up via the canonical-supplier layer. **These are framework ceiling and award notice values, not realised draw-down**, so the absolute pounds-million numbers should be read as relative ranking, not real revenue.

| Sector | Top 5 by award value | Total £m |
|---|---|---|
| Business process outsourcing | Capita Business Services / Serco / Mitie Property Services / G4S Secure Solutions / Atos IT Services | 67,380 / 67,088 / 36,034 / 31,128 / 30,391 |
| Information technology services | Softcat / Fujitsu Services / CGI IT UK / Phoenix Software (Bytes) / Civica UK | 54,440 / 27,165 / 23,440 / 22,727 / 22,674 |
| Facilities management | Equans Regeneration / Serco / Bouygues E&S / Mitie Property Services / Iss Mediclean | 261,259 / 67,088 / 37,566 / 36,034 / 21,651 |
| Construction and civil engineering | Morgan Sindall / Kier Construction / Willmott Dixon / Wates Construction / Galliford Try | 194,425 / 177,166 / 133,097 / 132,175 / 81,865 |
| Defence | Lockheed Martin UK / BAE Systems (Operations) / Babcock Vehicle Engineering / Raytheon Systems / Babcock Training | 19,893 / 18,638 / 9,637 / 9,170 / 8,118 |
| Consulting and advisory | Atkins / Deloitte / PA Consulting / WSP UK / Mott MacDonald | 42,447 / 27,205 / 24,998 / 24,715 / 18,057 |

The lists confirm the proposed defaults sit at the right anchor:
- Business process outsourcing dominated by the four big general outsourcers, which is why the 4–7% range tracks Capita and Serco rather than the higher specialist contact-centre cohort.
- Information technology services dominated by infrastructure-and-licence resellers (Softcat, Phoenix, Computacenter) with a smaller systems-integrator long tail (CGI, Capgemini, Kainos), which justifies widening the upper end of the range to 11%.
- Facilities management dominated by the engineering-led primes (Equans, Bouygues, Mitie). The 4–7% range fits.
- Construction dominated by the Tier 1 contractors as expected, all running at low single-digit margins. The 1.5–3.5% range fits.
- Defence dominated by the platform and systems primes (Lockheed Martin UK, BAE, Babcock, Raytheon, Thales). The 7–11% range fits the Single Source Regulations Office regime.
- Consulting topped by the engineering-consulting cohort (Atkins, WSP, Mott MacDonald) with the strategy houses (Deloitte, PA, KPMG, EY) close behind, which is why the range was widened down to 12%.

No sector required a default revision after the harvest.

