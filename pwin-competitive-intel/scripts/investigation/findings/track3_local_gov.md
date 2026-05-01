# Track 3 — Local government reality check

**Date:** 2026-04-30

---

## LGA canonical officer list

**Not found.**

The Local Government Association (LGA) does not maintain a cross-council database of senior officers. The LGA Transparency Code (2015, revised 2025) mandates that individual councils publish their own senior officer data, but this obligation sits with each council separately — there is no central aggregation or API.

The LGA publishes transparency data about its own organisation (staff salaries, structure) but does not aggregate officer data from the ~350+ English councils it represents. The LG Inform dataset platform (lginform.local.gov.uk) contains financial and performance statistics but no named officer data.

**Conclusion:** No central feed exists for local government senior officers. Any build would require scraping each council website individually, with no standardised format to rely on.

---

## Council website sample

### Birmingham City Council

- **URL visited:** https://www.birmingham.gov.uk/council
- **Senior officers named:** No. The main council landing page links to governance, committees, and democracy pages but does not surface a senior officers listing. Birmingham is under government intervention (Commissioners appointed 2023) and its standard governance pages appear reorganised.
- **Detail level:** N/A — no officers listed on the pages reached
- **Last updated shown:** N/A
- **Note:** Birmingham CC had no organogram on data.gov.uk (confirmed in Task 2). Its website also does not surface a clear senior officer page. As a large council under intervention, the governance structure is atypical.

### Manchester City Council

- **URL visited:** https://www.manchester.gov.uk (senior structure URL 404d)
- **Senior officers named:** Partially. Web search confirms a senior structure directory exists and Tom Stannard is listed as Chief Executive, but the directory URL structure has changed and the page was not directly accessible. Council does publish senior officer data.
- **Detail level:** Chief Executive confirmed; wider team available via directory page when accessible
- **Last updated shown:** Unknown — not retrieved
- **Note:** Manchester's senior structure is published under the Transparency Code, but URL stability is poor — the directory path changed and the old URLs 404. Scraping would require regular URL discovery.

### Oxfordshire County Council

- **URL found:** https://www.oxfordshire.gov.uk/council/about-your-council/managers-and-salaries/senior-managers
- **Senior officers named:** Yes — 10 named directors confirmed via web search:
  - Martin Reeves — Chief Executive
  - Lorna Baxter — Executive Director of Resources and Section 151 Officer
  - Ansaf Azhar — Director of Public Health and Communities
  - Karen Fuller — Director of Adult Social Care
  - Lisa Lyons — Director of Children's Services
  - Rob MacDougall — Chief Fire Officer and Director of Community Safety
  - Paul Fermer — Director of Environment and Highways
  - Robin Rogers — Director of Economy and Place
  - Anita Bradley — Director of Law and Governance and Monitoring Officer
  - Cherie Cuthbertson — Director of HR and Cultural Change
- **Detail level:** Role + name + contact. Salary bands published on a separate page. No grade equivalent to central government SCS bands.
- **Last updated shown:** Not confirmed — page found via web search without direct visit
- **Note:** Oxfordshire is a good example of what the Transparency Code produces when well-implemented: named directors with titles and contact details. Coverage is chief officer tier only — no assistant directors or commercial leads listed.

### London Borough of Hackney

- **URL:** Not successfully retrieved (URL from plan 404d, no web search performed)
- **Senior officers named:** Unknown
- **Detail level:** Unknown
- **Last updated shown:** Unknown
- **Note:** London boroughs typically publish senior officer registers under the Transparency Code. Hackney is a well-run council with good transparency record, but the specific page was not confirmed in this investigation.

### South Cambridgeshire District Council

- **URL found:** https://www.scambs.gov.uk/your-council-and-democracy/access-to-information/our-leadership-team-structure/
- **Senior officers named:** Yes — Liz Watts confirmed as Chief Executive via web search. Leadership team structure page exists.
- **Detail level:** Chief Executive and leadership team published under transparency obligations. Smaller district council — likely 4–6 named senior officers total.
- **Last updated shown:** Not confirmed
- **Note:** Smaller district councils typically have fewer named officers (Chief Executive, S151 Officer, Monitoring Officer, and 2–3 service directors). Procurement leads are generally not listed.

---

## Local government recommendation

**Defer local government coverage from v1.** There is no canonical cross-council officer list, council websites use inconsistent formats and unstable URL structures, coverage only reaches Chief Officer tier (not procurement leads or commercial staff), and the data quality issues that affect central government organograms (75-80% redaction rate) do not apply here — instead the problem is inconsistent publication and no bulk access mechanism. If local government buyer stakeholders are needed, the recommended approach is per-pursuit manual research rather than a maintained canonical layer.
