# BidEquity Newsroom — Ticket 5: Classifier Stage

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully tested, prompt-versioned classifier that scores ingested items 0–10 for BidEquity pursuit-intelligence relevance, runs in real-time and batch modes, logs cost per classification, and achieves ≥ 70% agreement on the golden eval set.

**Architecture:** Every ingested item (post pre-filter) is scored by `claude-haiku-4-5` via a structured JSON call; items scoring ≥ 7 enter a real-time fast-path, while the remainder batch every 6 hours through the Anthropic Message Batches API. The system prompt (role + taxonomy + rubric + examples, ~2,000 tokens) is cached with Anthropic prompt caching for a ~90% cache-hit cost reduction, giving a blended cost of ~£8–10/month at 3,600 items/month.

**Tech Stack:** Anthropic SDK (claude-haiku-4-5), prompt caching, Message Batches API, pytest

---

## File Map

| File | Description |
|---|---|
| `bidequity-newsroom/prompts/classifier/role.md` | Classifier persona: senior UK public-sector bid intelligence analyst at BidEquity |
| `bidequity-newsroom/prompts/classifier/rubric.md` | 0–10 relevance scoring scale with worked examples per band |
| `bidequity-newsroom/prompts/classifier/output_schema.json` | JSON Schema for the classifier's required response shape |
| `bidequity-newsroom/prompts/classifier/taxonomy.yaml` | Sector definitions, known buyers, known programmes, BidEquity content angles |
| `bidequity-newsroom/prompts/classifier/examples/01_high_signal_procurement.json` | Few-shot: direct ITT published in target sector (score 10) |
| `bidequity-newsroom/prompts/classifier/examples/02_high_signal_policy.json` | Few-shot: NAO report on active programme (score 8) |
| `bidequity-newsroom/prompts/classifier/examples/03_medium_signal_blog.json` | Few-shot: relevant think-tank perspective (score 6) |
| `bidequity-newsroom/prompts/classifier/examples/04_low_signal_item.json` | Few-shot: tangentially related sector news (score 4) |
| `bidequity-newsroom/prompts/classifier/examples/05_wrong_sector.json` | Few-shot: unrelated sector item that should score low (score 2) |
| `bidequity-newsroom/prompts/classifier/examples/06_nao_report.json` | Few-shot: NAO value-for-money study on a live programme (score 9) |
| `bidequity-newsroom/prompts/classifier/examples/07_council_announcement.json` | Few-shot: local council digital transformation announcement (score 5) |
| `bidequity-newsroom/prompts/classifier/examples/08_industry_body_press_release.json` | Few-shot: techUK press release on procurement reform (score 6) |
| `bidequity-newsroom/src/bidequity/intelligence/prompt_loader.py` | Loads and assembles classifier system prompt from prompt files; lists available versions |
| `bidequity-newsroom/src/bidequity/intelligence/classifier.py` | `ClassifierResult` model; `classify_item` (real-time); `classify_batch` (Message Batches) |
| `bidequity-newsroom/evals/classifier_eval.py` | Runs golden set against classifier; prints agreement rate; writes timestamped results |
| `bidequity-newsroom/evals/classifier_golden.json` | 10-item seed golden set (expandable to 50); each item has expected score and signal type |
| `bidequity-newsroom/tests/test_intelligence/test_classifier.py` | Unit tests: parse valid response; log cost; retry on malformed; raise after second failure |

---

## Tasks

### Task 1 — Write the classifier prompt files

- [ ] **1.1** Create `bidequity-newsroom/prompts/classifier/role.md` with the following content:

  ```markdown
  # Classifier Role

  You are a senior UK public-sector bid intelligence analyst working for BidEquity,
  a strategic pursuit consultancy. BidEquity helps bid teams decide whether to pursue
  public-sector contracts, and publishes commentary that keeps those teams informed
  about procurement trends, policy shifts, and programme developments across seven
  sectors: Defence, Justice, Health & Social Care, Local Government & Devolved,
  Central Government & Cabinet Office, Transport, and Emergency Services.

  Your task is to assess a piece of content — typically a government announcement,
  think-tank report, trade press article, NAO publication, or committee output — and
  judge how useful it is to a pursuit team or a BidEquity editorial decision.

  You have deep knowledge of:
  - UK public procurement law and practice (PCR 2015, Procurement Act 2023)
  - The major UK government frameworks (Crown Commercial Service, NHSE, DSIT, MOD)
  - Active programmes: ESN, Common Platform, FDP, SKYNET 6, NHS Federated Data Platform,
    HMCTS Reform, Adult Social Care digital programmes, UK Shared Prosperity Fund
  - The bid lifecycle from gate review through ITT to contract award
  - Supplier landscape: major primes (Serco, G4S, Capita, Sopra Steria, Atos, Leidos,
    BAE Systems, Fujitsu, CGI, IBM UK, DXC, NTT DATA) and specialist SMEs
  - Government spending review cycles and how they create pipeline surges

  You are precise, commercially minded, and do not overstate relevance. You score
  content against the rubric honestly. You are not impressed by big names unless
  the signal is real. A press release from a supplier claiming success is scored
  lower than an official procurement notice or independent oversight report.

  Always return your assessment as a single valid JSON object matching the output
  schema exactly. Do not include any text outside the JSON object.
  ```

- [ ] **1.2** Create `bidequity-newsroom/prompts/classifier/rubric.md` with the full scoring scale:

  ```markdown
  # Relevance Scoring Rubric

  Score every item on a 0–10 integer scale. Apply the scale strictly.
  When in doubt between two bands, choose the lower one — do not round up.

  ---

  ## 10 — Direct pursuit signal (act now)

  The item announces or describes something that directly opens or changes a named
  procurement opportunity in a BidEquity target sector. A bid team should be alerted
  immediately.

  **Qualifying signals:**
  - A named ITT, PQQ, or PIN published on Find a Tender or Contracts Finder in a
    target sector
  - Contract award or re-let announcement creating a follow-on opportunity
  - An incumbent's contract confirmed as ending, with a re-competition date

  **Example:** "Ministry of Defence publishes Invitation to Tender for Emergency
  Services Network Phase 2 — responses due in 90 days."

  ---

  ## 8–9 — Strong leading indicator (watch and prepare)

  The item strongly foreshadows a procurement, changes a programme's trajectory, or
  signals a buyer intent that is likely to result in market engagement within 6–12 months.

  **Score 9:** Named programme, named buyer, clear forward signal.
  **Score 8:** Named programme or strong sector signal, but timing or buyer less certain.

  **Qualifying signals:**
  - NAO or PAC report critical of a programme in delivery, suggesting re-competition
  - SRO appointment or departure on a major programme
  - Spending review settlement published for a target department
  - Policy paper committing to a new digital or outsourced service
  - Framework expiry confirmed with re-competition notice expected
  - Major supplier profit warning or exit from a sector

  **Example (9):** "NAO finds HMCTS Common Platform three years behind schedule and
  £200m over budget — recommends options appraisal of continued development vs. replatform."

  **Example (8):** "Cabinet Office publishes new cloud-first policy mandating public cloud
  migration for all central government departments by 2027."

  ---

  ## 6–7 — Contextual signal (adds to picture)

  The item is relevant to BidEquity's sectors and adds useful context for a pursuit
  team or an editorial point of view, but does not indicate an imminent procurement.

  **Score 7:** Clear sector relevance; develops a named programme or named buyer.
  **Score 6:** Sector relevance; thematic or trend-level.

  **Qualifying signals:**
  - Think-tank analysis of a target sector's performance or challenges
  - Government response to a Select Committee report on a relevant programme
  - Industry body position paper on procurement reform
  - Regulatory change affecting how public services are procured or delivered

  **Example (7):** "DSIT publishes AI Playbook for public sector — sets expectations for AI
  procurement across government."

  **Example (6):** "techUK calls for multi-year contracts to enable more SME participation
  in government digital procurement."

  ---

  ## 4–5 — Ambient signal (background awareness)

  The item is broadly about public sector or adjacent areas and may inform general
  awareness, but has no clear editorial angle or pursuit implication for BidEquity.

  **Score 5:** Sector adjacent; could be filed as background.
  **Score 4:** Weakly connected; would only be relevant in a very specific context.

  **Qualifying signals:**
  - Generic government productivity or workforce stories
  - Local council budget commentary with no specific procurement dimension
  - Overseas procurement case studies without clear UK application

  ---

  ## 0–3 — Irrelevant (discard)

  The item has no meaningful connection to BidEquity's sectors, editorial remit, or
  pursuit intelligence function.

  **Score 3:** Could be argued as background but is not worth classifying.
  **Score 1–2:** Clearly a different sector or country.
  **Score 0:** Spam, duplicate, or entirely off-topic.

  ---

  ## Calibration rules

  1. **Source authority matters.** An official procurement notice outweighs a supplier
     press release for the same programme by at least two score points.
  2. **Named beats unnamed.** "MOD re-competes SKYNET 6" scores higher than "defence
     satellite procurement is expected to increase."
  3. **Recency matters at the top.** A score of 10 requires the opportunity to be live
     or newly announced, not historical.
  4. **Do not award 8+ for opinion pieces** unless they cite primary source evidence
     that would independently score 8+.
  5. **UK-specific.** Score foreign procurement news as 0–3 unless it has a direct
     UK programme implication.
  ```

- [ ] **1.3** Create `bidequity-newsroom/prompts/classifier/output_schema.json`:

  ```json
  {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ClassifierOutput",
    "description": "Structured output from the BidEquity classifier. Every field is required unless marked nullable.",
    "type": "object",
    "required": [
      "relevance_score",
      "signal_strength",
      "signal_type",
      "sectors",
      "buyers_mentioned",
      "suppliers_mentioned",
      "programmes_mentioned",
      "summary",
      "pursuit_implication",
      "content_angle_hook"
    ],
    "additionalProperties": false,
    "properties": {
      "relevance_score": {
        "type": "integer",
        "minimum": 0,
        "maximum": 10,
        "description": "Integer 0-10 relevance score per rubric. 10=direct ITT, 8-9=strong leading indicator, 6-7=contextual, 4-5=ambient, 0-3=irrelevant."
      },
      "signal_strength": {
        "type": "string",
        "enum": ["high", "medium", "low"],
        "description": "high = score 7-10, medium = score 4-6, low = score 0-3"
      },
      "signal_type": {
        "type": "string",
        "enum": ["procurement", "policy", "oversight", "financial", "leadership", "other"],
        "description": "Primary signal type. procurement=tender/contract/framework. policy=government policy/legislation. oversight=NAO/PAC/inspectorate. financial=spending review/budget/VFM. leadership=SRO/CEO/minister appointment. other=none of the above."
      },
      "sectors": {
        "type": "array",
        "items": { "type": "string" },
        "description": "One or more of: Defence, Justice, Health & Social Care, Local Government & Devolved, Central Government & Cabinet Office, Transport, Emergency Services. Empty array if none apply."
      },
      "buyers_mentioned": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Named UK public-sector buyers referenced in the content. Use short canonical forms: MOD, HMCTS, NHSE, Home Office, DSIT, Cabinet Office, etc. Empty array if none."
      },
      "suppliers_mentioned": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Named suppliers or market participants referenced. Empty array if none."
      },
      "programmes_mentioned": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Named programmes, frameworks, or projects referenced. Empty array if none."
      },
      "summary": {
        "type": "string",
        "maxLength": 300,
        "description": "One to three sentences summarising the item's content and why it scored as it did. Factual, no speculation."
      },
      "pursuit_implication": {
        "type": ["string", "null"],
        "maxLength": 300,
        "description": "What this means for a bid team deciding whether and how to pursue. Null if relevance_score < 6. Must answer: what is the move?"
      },
      "content_angle_hook": {
        "type": ["string", "null"],
        "maxLength": 200,
        "description": "One sentence framing a LinkedIn or newsletter commentary angle for BidEquity. Null if relevance_score < 6. Should be opinionated, not descriptive."
      }
    }
  }
  ```

- [ ] **1.4** Create `bidequity-newsroom/prompts/classifier/taxonomy.yaml`:

  ```yaml
  # BidEquity Classifier Taxonomy
  # Passed into the classifier system prompt as a reference block.
  # Keep entries concise — this is cached, but token count still matters.

  sectors:
    - slug: defence
      name: Defence
      description: MOD, DE&S, DSTL, single-service commands, defence primes, national security
    - slug: justice
      name: Justice
      description: HMCTS, MoJ, HMPPS, probation, legal aid, Common Platform, court reform
    - slug: health_social_care
      name: Health & Social Care
      description: NHSE, ICBs, NHS trusts, DHSC, CQC, adult social care, FDP, NHS digital
    - slug: local_gov_devolved
      name: Local Government & Devolved
      description: English councils, Welsh Government, Scottish Government, combined authorities
    - slug: central_gov_co
      name: Central Government & Cabinet Office
      description: Cabinet Office, DSIT, HMRC, DWP, cross-government digital, GDS, CCS frameworks
    - slug: transport
      name: Transport
      description: DfT, National Highways, Network Rail, HS2, DVLA, regional transport authorities
    - slug: emergency_services
      name: Emergency Services
      description: Home Office, police forces, fire services, ambulance services, ESN, NPAS

  programmes:
    # Active or recently completed programmes of significance
    - name: Emergency Services Network (ESN)
      buyer: Home Office
      sector: Emergency Services
    - name: Common Platform
      buyer: HMCTS
      sector: Justice
    - name: Federated Data Platform (FDP)
      buyer: NHSE
      sector: Health & Social Care
    - name: SKYNET 6
      buyer: MOD / UK Space Command
      sector: Defence
    - name: HMCTS Reform Programme
      buyer: HMCTS
      sector: Justice
    - name: Adult Social Care Connect
      buyer: DHSC
      sector: Health & Social Care
    - name: DSTL Future Combat Air
      buyer: DSTL / MOD
      sector: Defence
    - name: National Law Enforcement Data Programme (NLEDP)
      buyer: Home Office
      sector: Justice / Emergency Services
    - name: Shared Services Connected (SSCL)
      buyer: Cabinet Office
      sector: Central Government & Cabinet Office
    - name: UK Border Control Post Programme
      buyer: HMRC / Home Office
      sector: Central Government & Cabinet Office

  buyers:
    # Canonical short names for known UK public-sector buyers
    - MOD
    - DE&S
    - DSTL
    - HMCTS
    - MoJ
    - HMPPS
    - NHSE
    - DHSC
    - NHS England
    - Home Office
    - Cabinet Office
    - DSIT
    - GDS
    - HMRC
    - DWP
    - DfT
    - National Highways
    - Network Rail
    - HS2 Ltd
    - DVLA
    - CQC
    - NHS BSA
    - NHS Shared Business Services

  suppliers:
    # Major primes and known suppliers active in BidEquity target sectors
    - Serco
    - G4S
    - Capita
    - Sopra Steria
    - Atos
    - Leidos
    - BAE Systems
    - Fujitsu
    - CGI
    - IBM UK
    - DXC Technology
    - NTT DATA
    - Unison (as a labour intelligence signal, not a supplier)
    - Accenture
    - Deloitte
    - KPMG
    - PwC

  frameworks:
    # Major CCS and sector-specific frameworks
    - name: G-Cloud
      owner: CCS
    - name: Digital Outcomes and Specialists (DOS / DIOS)
      owner: CCS
    - name: Technology Products and Associated Services (TPAS)
      owner: CCS
    - name: Management Consultancy Framework (MCF2)
      owner: CCS
    - name: National Outsourcing Framework (NOF)
      owner: CCS
    - name: NHS Workforce Alliance frameworks
      owner: NHSE / NHS BSA
    - name: Defence and Security Accelerator (DASA)
      owner: MOD

  content_angles:
    # BidEquity's standing editorial lenses — used to generate the content_angle_hook
    - The pursuit implication (what does this mean for a bid team right now?)
    - The incumbent's position (does this strengthen or weaken the defender?)
    - The buyer's intent signal (what is the customer telling the market?)
    - The programme trajectory (is this accelerating, stalling, or resetting?)
    - The procurement reform angle (how does the Procurement Act 2023 apply here?)
    - The SME/prime dynamic (does this open or close the door for smaller suppliers?)
    - The value-for-money narrative (what does this say about public spending discipline?)
    - The 'what happens next' frame (what should a bid team do in the next 30 days?)
  ```

- [ ] **1.5** Create the 8 few-shot example files in `bidequity-newsroom/prompts/classifier/examples/`:

  **`01_high_signal_procurement.json`** (score 10):
  ```json
  {
    "item": {
      "title": "Find a Tender: Invitation to Tender — Emergency Services Network Phase 2 Core Network Infrastructure",
      "source_name": "Find a Tender Service",
      "source_category": "Procurement Notices",
      "sector": "Emergency Services",
      "body_preview": "The Home Office is seeking a prime contractor to design, build, and operate the Phase 2 core network infrastructure for the Emergency Services Network. The contract is valued at approximately £1.2 billion over 10 years. Responses are due by 17:00 on 30 June 2026. This follows the completion of the Phase 1 coverage build-out delivered under the current EE/BT contract."
    },
    "expected_output": {
      "relevance_score": 10,
      "signal_strength": "high",
      "signal_type": "procurement",
      "sectors": ["Emergency Services"],
      "buyers_mentioned": ["Home Office"],
      "suppliers_mentioned": [],
      "programmes_mentioned": ["Emergency Services Network (ESN)"],
      "summary": "Home Office has published a live ITT for the ESN Phase 2 core network, valued at ~£1.2bn over 10 years. Responses due 30 June 2026. This is the primary re-competition following Phase 1 delivery.",
      "pursuit_implication": "Any supplier with mission-critical network, critical national infrastructure, or managed services capability should be qualifying immediately. The 90-day window requires a Go/No-Go decision within two weeks to allow proper bid resourcing.",
      "content_angle_hook": "ESN Phase 2 is live: what the ITT terms signal about the Home Office's procurement maturity since the Phase 1 delivery struggles."
    }
  }
  ```

  **`02_high_signal_policy.json`** (score 8):
  ```json
  {
    "item": {
      "title": "AI Playbook for the UK Public Sector — DSIT",
      "source_name": "DSIT",
      "source_category": "Official Guidance",
      "sector": "Central Government & Cabinet Office",
      "body_preview": "The Department for Science, Innovation and Technology has published the AI Playbook for UK public sector organisations. The guidance mandates that all central government departments must publish AI procurement strategies by Q3 2026 and sets minimum standards for AI supplier assurance, explainability requirements, and contract transparency. Departments that do not comply risk losing access to the AI Fund settlement."
    },
    "expected_output": {
      "relevance_score": 8,
      "signal_strength": "high",
      "signal_type": "policy",
      "sectors": ["Central Government & Cabinet Office"],
      "buyers_mentioned": ["DSIT", "Cabinet Office"],
      "suppliers_mentioned": [],
      "programmes_mentioned": [],
      "summary": "DSIT's AI Playbook mandates AI procurement strategies across central government by Q3 2026 and sets supplier assurance standards. Non-compliance risks AI Fund access. This creates a visible procurement activity surge across departments.",
      "pursuit_implication": "Suppliers with AI capability should expect a wave of AI framework call-offs and direct procurements in H2 2026 as departments race to comply. The assurance and explainability requirements will narrow the field to suppliers who can demonstrate governance maturity, not just technical delivery.",
      "content_angle_hook": "DSIT's AI Playbook is a procurement accelerant in disguise: why the Q3 compliance deadline creates a predictable buyer surge that prepared suppliers should already be positioning for."
    }
  }
  ```

  **`03_medium_signal_blog.json`** (score 6):
  ```json
  {
    "item": {
      "title": "Making outsourcing work: lessons from a decade of public sector contracts",
      "source_name": "Institute for Government",
      "source_category": "Think Tank Reports",
      "sector": "Central Government & Cabinet Office",
      "body_preview": "This briefing paper from the Institute for Government examines ten years of public sector outsourcing contracts, drawing on 47 case studies. It identifies five structural weaknesses: inadequate contract management capability, misaligned payment mechanisms, poor mobilisation planning, insufficient commercial intelligence at procurement stage, and weak supplier relationship management. The paper recommends reforms to the Outsourcing Playbook and calls for a dedicated Commercial Academy within the civil service."
    },
    "expected_output": {
      "relevance_score": 6,
      "signal_strength": "medium",
      "signal_type": "policy",
      "sectors": ["Central Government & Cabinet Office"],
      "buyers_mentioned": ["Cabinet Office"],
      "suppliers_mentioned": [],
      "programmes_mentioned": [],
      "summary": "IfG's ten-year outsourcing retrospective identifies five structural weaknesses in UK public sector contracts and recommends Outsourcing Playbook reforms. Relevant background for any supplier engaging on contract design or mobilisation in a bid.",
      "pursuit_implication": "Bid teams responding to outsourcing procurements should anticipate buyers using this research to demand stronger mobilisation plans, commercial intelligence evidence, and relationship management frameworks in their responses.",
      "content_angle_hook": "The IfG's outsourcing report reads like a bid writer's checklist: the five weaknesses buyers most fear are exactly what your bid should pre-emptively address."
    }
  }
  ```

  **`04_low_signal_item.json`** (score 4):
  ```json
  {
    "item": {
      "title": "Councils warn of growing pressure on children's services budgets",
      "source_name": "Local Government Chronicle",
      "source_category": "Trade Press",
      "sector": "Local Government & Devolved",
      "body_preview": "The Local Government Association has warned that children's services budgets are under severe strain, with a collective overspend of £2.1bn projected across English councils for 2025-26. LGA chair Shaun Davies said the situation was 'not sustainable' and called for emergency funding from central government. Several councils have confirmed they are considering Section 114 notices if emergency support is not forthcoming by the autumn spending review."
    },
    "expected_output": {
      "relevance_score": 4,
      "signal_strength": "medium",
      "signal_type": "financial",
      "sectors": ["Local Government & Devolved"],
      "buyers_mentioned": [],
      "suppliers_mentioned": [],
      "programmes_mentioned": [],
      "summary": "LGA warns of £2.1bn children's services overspend across English councils, with Section 114 notices being considered. Background signal on local government fiscal stress but no specific procurement trigger.",
      "pursuit_implication": null,
      "content_angle_hook": null
    }
  }
  ```

  **`05_wrong_sector.json`** (score 2):
  ```json
  {
    "item": {
      "title": "Ofgem publishes new price cap methodology for 2026",
      "source_name": "Ofgem",
      "source_category": "Regulatory Announcements",
      "sector": "Energy",
      "body_preview": "Ofgem has published its revised methodology for calculating the domestic energy price cap from Q1 2026. The new approach incorporates a quarterly reset mechanism and a revised wholesale cost passthrough formula. The announcement follows a consultation that received responses from 23 energy suppliers and three consumer groups."
    },
    "expected_output": {
      "relevance_score": 2,
      "signal_strength": "low",
      "signal_type": "policy",
      "sectors": [],
      "buyers_mentioned": [],
      "suppliers_mentioned": [],
      "programmes_mentioned": [],
      "summary": "Ofgem energy price cap methodology update. Entirely outside BidEquity's target sectors — no pursuit or editorial relevance.",
      "pursuit_implication": null,
      "content_angle_hook": null
    }
  }
  ```

  **`06_nao_report.json`** (score 9):
  ```json
  {
    "item": {
      "title": "Investigation into the delivery of the Common Platform programme — National Audit Office",
      "source_name": "National Audit Office",
      "source_category": "Oversight & Scrutiny",
      "sector": "Justice",
      "body_preview": "The NAO has published an investigation into the HMCTS Common Platform programme following a referral from the Public Accounts Committee. The report finds the programme is now £312m over its original business case budget and has missed its completion date by at least three years. The NAO recommends that HMCTS conduct a full options appraisal — including consideration of partial replatforming — before committing additional funding. The programme's SRO has changed three times since 2021."
    },
    "expected_output": {
      "relevance_score": 9,
      "signal_strength": "high",
      "signal_type": "oversight",
      "sectors": ["Justice"],
      "buyers_mentioned": ["HMCTS", "MoJ"],
      "suppliers_mentioned": [],
      "programmes_mentioned": ["Common Platform"],
      "summary": "NAO investigation finds Common Platform £312m over budget and three years late, recommending an options appraisal including replatforming. Three SRO changes since 2021. PAC referral indicates parliamentary scrutiny is escalating.",
      "pursuit_implication": "An NAO-recommended options appraisal almost always precedes a significant re-competition or supplementary contract. Suppliers with court technology, case management, or digital transformation capability in justice should be monitoring the options appraisal output as a bid signal within 12–18 months.",
      "content_angle_hook": "The NAO's Common Platform report is a textbook pre-competition signal: when the auditor recommends an options appraisal, the clock starts on the next ITT."
    }
  }
  ```

  **`07_council_announcement.json`** (score 5):
  ```json
  {
    "item": {
      "title": "Leeds City Council launches Digital Inclusion Strategy 2026–2030",
      "source_name": "Leeds City Council",
      "source_category": "Council News",
      "sector": "Local Government & Devolved",
      "body_preview": "Leeds City Council has published its Digital Inclusion Strategy 2026–2030, committing to providing affordable broadband access to 50,000 households currently offline, digital skills training for 15,000 residents, and deployment of 200 digital access hubs across the city by 2028. The strategy commits £18m of council funding and will seek match funding from UKSPF and DSIT's digital infrastructure programme. A procurement exercise for delivery partners will commence in Q3 2026."
    },
    "expected_output": {
      "relevance_score": 5,
      "signal_strength": "medium",
      "signal_type": "procurement",
      "sectors": ["Local Government & Devolved"],
      "buyers_mentioned": [],
      "suppliers_mentioned": [],
      "programmes_mentioned": ["UK Shared Prosperity Fund"],
      "summary": "Leeds City Council publishes £18m digital inclusion strategy with a delivery partner procurement starting Q3 2026. Relevant for suppliers in digital skills, connectivity, or community digital transformation, but a single-council opportunity.",
      "pursuit_implication": null,
      "content_angle_hook": null
    }
  }
  ```

  **`08_industry_body_press_release.json`** (score 6):
  ```json
  {
    "item": {
      "title": "techUK: Procurement Act 2023 implementation creates opportunity to fix SME access barriers",
      "source_name": "techUK",
      "source_category": "Industry Body",
      "sector": "Central Government & Cabinet Office",
      "body_preview": "techUK has published a position paper calling on the Cabinet Office to use the Procurement Act 2023 implementation regulations to mandate disaggregated contract structures, reduce payment terms to 30 days for tier-2 suppliers, and require all central government buyers to publish forward pipelines 18 months in advance. The paper cites data showing SME participation in central government contracts has fallen from 28% to 19% in the last five years despite successive policy commitments to increase it."
    },
    "expected_output": {
      "relevance_score": 6,
      "signal_strength": "medium",
      "signal_type": "policy",
      "sectors": ["Central Government & Cabinet Office"],
      "buyers_mentioned": ["Cabinet Office"],
      "suppliers_mentioned": [],
      "programmes_mentioned": [],
      "summary": "techUK position paper calls for Procurement Act implementation regulations to mandate forward pipelines, disaggregated structures, and 30-day tier-2 payment terms. Flags SME participation in central government at a 5-year low of 19%.",
      "pursuit_implication": "Suppliers preparing bids for central government frameworks should include strong SME supply chain commitments and disaggregation plans — buyers are under increasing scrutiny on this dimension and evaluators will reward it.",
      "content_angle_hook": "The Procurement Act's SME access provisions are only as good as the regulations that implement them — techUK's data on the 28% to 19% collapse is the number buyers should be embarrassed to defend."
    }
  }
  ```

---

### Task 2 — Write the tests first (TDD)

- [ ] **2.1** Create `bidequity-newsroom/tests/test_intelligence/__init__.py` (empty)

- [ ] **2.2** Create `bidequity-newsroom/tests/test_intelligence/test_classifier.py`:

  ```python
  """
  Tests for the BidEquity classifier worker.
  All tests mock the Anthropic client — no real API calls.
  """
  import json
  import pytest
  import pytest_asyncio
  from unittest.mock import AsyncMock, MagicMock, patch
  from decimal import Decimal

  from bidequity.intelligence.classifier import (
      ClassifierResult,
      classify_item,
  )
  from bidequity.models.item import Item


  # ---------------------------------------------------------------------------
  # Fixtures
  # ---------------------------------------------------------------------------

  VALID_RESPONSE_JSON = {
      "relevance_score": 8,
      "signal_strength": "high",
      "signal_type": "procurement",
      "sectors": ["Defence"],
      "buyers_mentioned": ["MOD", "DE&S"],
      "suppliers_mentioned": [],
      "programmes_mentioned": ["SKYNET 6"],
      "summary": "MOD has released the ITN for SKYNET 6 Wideband Satellite System.",
      "pursuit_implication": "Primes with satcom capability should resource bid teams now.",
      "content_angle_hook": "What SKYNET 6's ITN signals about MOD's new procurement cadence.",
  }

  MALFORMED_RESPONSE_JSON = "this is not valid json {"


  def make_mock_item() -> Item:
      return Item(
          id=1,
          source_id=1,
          url="https://www.find-tender.service.gov.uk/Notice/123",
          title="MOD publishes ITN for SKYNET 6 Wideband Satellite System",
          body_text="Full body text of the SKYNET 6 ITN announcement here.",
          body_preview="Full body text of the SKYNET 6 ITN announcement here.",
          content_hash="abc123",
      )


  def make_mock_message(content: str, input_tokens: int = 1200, output_tokens: int = 350):
      """Returns a mock Anthropic Message object."""
      msg = MagicMock()
      msg.content = [MagicMock(text=content)]
      msg.usage = MagicMock(input_tokens=input_tokens, output_tokens=output_tokens)
      return msg


  def make_mock_client(response_content: str) -> AsyncMock:
      client = AsyncMock()
      client.messages.create = AsyncMock(
          return_value=make_mock_message(response_content)
      )
      return client


  # ---------------------------------------------------------------------------
  # Test: ClassifierResult parses correctly from valid response
  # ---------------------------------------------------------------------------

  @pytest.mark.asyncio
  async def test_classify_item_parses_valid_response(tmp_path, monkeypatch):
      """ClassifierResult is returned correctly when the API response is valid JSON."""
      item = make_mock_item()
      client = make_mock_client(json.dumps(VALID_RESPONSE_JSON))

      # Stub the prompt loader so tests don't depend on file system
      monkeypatch.setattr(
          "bidequity.intelligence.classifier.load_classifier_system_prompt",
          lambda version: "stub system prompt",
      )

      result = await classify_item(item, client, prompt_version="classifier-v1")

      assert isinstance(result, ClassifierResult)
      assert result.relevance_score == 8
      assert result.signal_strength == "high"
      assert result.signal_type == "procurement"
      assert "Defence" in result.sectors
      assert "MOD" in result.buyers_mentioned
      assert "SKYNET 6" in result.programmes_mentioned
      assert result.pursuit_implication is not None
      assert result.content_angle_hook is not None


  # ---------------------------------------------------------------------------
  # Test: Cost is logged to the database
  # ---------------------------------------------------------------------------

  @pytest.mark.asyncio
  async def test_classify_item_logs_cost(tmp_path, monkeypatch):
      """
      Cost is computed from token usage and recorded in the returned result.
      Haiku pricing: £0.80/M input, £4/M output.
      For 1200 input + 350 output: expected cost ~ 0.00096 + 0.0014 = ~0.00236 USD.
      """
      item = make_mock_item()
      client = make_mock_client(json.dumps(VALID_RESPONSE_JSON))

      monkeypatch.setattr(
          "bidequity.intelligence.classifier.load_classifier_system_prompt",
          lambda version: "stub system prompt",
      )

      result = await classify_item(item, client, prompt_version="classifier-v1")

      assert result.cost_usd is not None
      assert float(result.cost_usd) > 0
      # Rough sanity check: should be in pence range, not pounds
      assert float(result.cost_usd) < 0.01


  # ---------------------------------------------------------------------------
  # Test: Malformed response is retried once and then raises
  # ---------------------------------------------------------------------------

  @pytest.mark.asyncio
  async def test_classify_item_retries_once_on_malformed_response(monkeypatch):
      """
      If the API returns non-JSON, classify_item retries once.
      If the second attempt also fails, ClassificationError is raised.
      """
      from bidequity.intelligence.classifier import ClassificationError

      item = make_mock_item()

      # Both calls return malformed JSON
      client = AsyncMock()
      client.messages.create = AsyncMock(
          return_value=make_mock_message(MALFORMED_RESPONSE_JSON)
      )

      monkeypatch.setattr(
          "bidequity.intelligence.classifier.load_classifier_system_prompt",
          lambda version: "stub system prompt",
      )

      with pytest.raises(ClassificationError, match="malformed"):
          await classify_item(item, client, prompt_version="classifier-v1")

      # Should have been called twice (original + one retry)
      assert client.messages.create.call_count == 2


  # ---------------------------------------------------------------------------
  # Test: First attempt malformed, second attempt succeeds
  # ---------------------------------------------------------------------------

  @pytest.mark.asyncio
  async def test_classify_item_succeeds_on_second_attempt(monkeypatch):
      """If the first response is malformed but the second is valid, returns result."""
      item = make_mock_item()

      client = AsyncMock()
      client.messages.create = AsyncMock(
          side_effect=[
              make_mock_message(MALFORMED_RESPONSE_JSON),
              make_mock_message(json.dumps(VALID_RESPONSE_JSON)),
          ]
      )

      monkeypatch.setattr(
          "bidequity.intelligence.classifier.load_classifier_system_prompt",
          lambda version: "stub system prompt",
      )

      result = await classify_item(item, client, prompt_version="classifier-v1")
      assert result.relevance_score == 8
      assert client.messages.create.call_count == 2
  ```

---

### Task 3 — Implement the prompt loader

- [ ] **3.1** Create `bidequity-newsroom/src/bidequity/intelligence/__init__.py` (empty if not exists)

- [ ] **3.2** Create `bidequity-newsroom/src/bidequity/intelligence/prompt_loader.py`:

  ```python
  """
  Loads and assembles the classifier system prompt from versioned prompt files.

  Directory layout expected:
    prompts/
      classifier/
        role.md
        taxonomy.yaml
        rubric.md
        output_schema.json
        examples/
          01_high_signal_procurement.json
          02_high_signal_policy.json
          ... (any *.json files)

  The assembled system prompt is a single string suitable for use as the
  Anthropic 'system' parameter. It is designed to be prompt-cached: the
  content is deterministic for a given version string.
  """
  from __future__ import annotations

  import json
  import os
  from pathlib import Path


  # Root of the prompts directory relative to the repo root.
  # Override via BIDEQUITY_PROMPTS_DIR environment variable if needed.
  def _prompts_root() -> Path:
      env = os.environ.get("BIDEQUITY_PROMPTS_DIR")
      if env:
          return Path(env)
      # Default: bidequity-newsroom/prompts/ relative to this file's package root
      return Path(__file__).parent.parent.parent.parent / "prompts"


  def load_classifier_system_prompt(version: str = "classifier-v1") -> str:
      """
      Assemble and return the full classifier system prompt for the given version.

      The version string is used to locate a versioned subdirectory if present.
      For 'classifier-v1', looks first in prompts/classifier-v1/, then falls back
      to prompts/classifier/. This allows prompt versioning without copying files
      for minor iterations.

      Args:
          version: Prompt version identifier, e.g. 'classifier-v1', 'classifier-v2'.

      Returns:
          A single string containing the full assembled system prompt.

      Raises:
          FileNotFoundError: If required prompt files are missing.
      """
      root = _prompts_root()

      # Resolve prompt directory: versioned takes priority
      versioned_dir = root / version
      base_dir = root / "classifier"
      prompt_dir = versioned_dir if versioned_dir.is_dir() else base_dir

      if not prompt_dir.is_dir():
          raise FileNotFoundError(
              f"Prompt directory not found: {prompt_dir} (also tried {versioned_dir})"
          )

      # Load required components
      role = _read(prompt_dir / "role.md")
      taxonomy = _read(prompt_dir / "taxonomy.yaml")
      rubric = _read(prompt_dir / "rubric.md")
      schema = _read(prompt_dir / "output_schema.json")

      # Load few-shot examples
      examples_dir = prompt_dir / "examples"
      examples_block = _load_examples(examples_dir) if examples_dir.is_dir() else ""

      # Assemble into a single prompt string
      parts = [
          role.strip(),
          "\n\n---\n\n## Taxonomy Reference\n\n```yaml\n" + taxonomy.strip() + "\n```",
          "\n\n---\n\n" + rubric.strip(),
          "\n\n---\n\n## Output Schema\n\nReturn exactly this JSON shape and no other text:\n\n```json\n"
          + schema.strip()
          + "\n```",
      ]

      if examples_block:
          parts.append("\n\n---\n\n## Scored Examples\n\n" + examples_block)

      return "\n".join(parts)


  def list_prompt_versions(prompt_type: str = "classifier") -> list[str]:
      """
      List available prompt versions for the given prompt type.

      Looks for directories named '{prompt_type}-v*' and the base '{prompt_type}'
      directory in the prompts root.

      Args:
          prompt_type: The type of prompt, e.g. 'classifier', 'generator'.

      Returns:
          Sorted list of version strings, e.g. ['classifier-v1', 'classifier-v2'].
      """
      root = _prompts_root()
      if not root.is_dir():
          return []

      versions = []
      for entry in sorted(root.iterdir()):
          if entry.is_dir() and (
              entry.name == prompt_type
              or entry.name.startswith(f"{prompt_type}-v")
          ):
              versions.append(entry.name)
      return versions


  # ---------------------------------------------------------------------------
  # Internal helpers
  # ---------------------------------------------------------------------------

  def _read(path: Path) -> str:
      if not path.exists():
          raise FileNotFoundError(f"Required prompt file not found: {path}")
      return path.read_text(encoding="utf-8")


  def _load_examples(examples_dir: Path) -> str:
      """
      Load all *.json example files in order and format them as a readable block.
      Each example JSON must have 'item' and 'expected_output' keys.
      """
      files = sorted(examples_dir.glob("*.json"))
      if not files:
          return ""

      blocks = []
      for f in files:
          try:
              data = json.loads(f.read_text(encoding="utf-8"))
          except json.JSONDecodeError as exc:
              raise ValueError(f"Invalid JSON in example file {f}: {exc}") from exc

          item = data.get("item", {})
          expected = data.get("expected_output", {})

          block = (
              f"### Example: {item.get('title', f.stem)}\n\n"
              f"**Source:** {item.get('source_name', 'unknown')} "
              f"({item.get('source_category', '')})\n\n"
              f"**Content preview:**\n{item.get('body_preview', '')}\n\n"
              f"**Expected output:**\n```json\n"
              + json.dumps(expected, indent=2)
              + "\n```"
          )
          blocks.append(block)

      return "\n\n---\n\n".join(blocks)
  ```

---

### Task 4 — Implement the classifier worker

- [ ] **4.1** Create `bidequity-newsroom/src/bidequity/intelligence/classifier.py`:

  ```python
  """
  BidEquity classifier worker.

  Provides two entry points:
  - classify_item(): real-time single classification (fast-path for score >= 7)
  - classify_batch(): submits to Anthropic Message Batches API for 6-hour batching

  Both functions:
  - Use prompt caching on the system prompt (cache_control: ephemeral, 1h TTL)
  - Return ClassifierResult with cost logged in cost_usd
  - Retry once on malformed JSON before raising ClassificationError
  """
  from __future__ import annotations

  import json
  import logging
  import time
  from decimal import Decimal
  from typing import Optional

  from anthropic import AsyncAnthropic
  from pydantic import BaseModel, field_validator

  from bidequity.intelligence.prompt_loader import load_classifier_system_prompt

  logger = logging.getLogger(__name__)

  # ---------------------------------------------------------------------------
  # Pricing constants (USD per token)
  # Haiku 4.5: $0.80/M input, $4.00/M output
  # Cache write: $1.00/M (slightly higher — Anthropic charges a small write premium)
  # Cache read: $0.08/M (90% cheaper than standard input)
  # We use standard input price as the base; the effective blended rate is lower.
  # ---------------------------------------------------------------------------
  HAIKU_INPUT_PRICE_PER_TOKEN = Decimal("0.0000008")   # $0.80/M
  HAIKU_OUTPUT_PRICE_PER_TOKEN = Decimal("0.000004")   # $4.00/M
  HAIKU_CACHE_READ_PRICE_PER_TOKEN = Decimal("0.00000008")  # $0.08/M

  CLASSIFIER_MODEL = "claude-haiku-4-5"


  # ---------------------------------------------------------------------------
  # Result model
  # ---------------------------------------------------------------------------

  class ClassifierResult(BaseModel):
      relevance_score: int
      signal_strength: str
      signal_type: str
      sectors: list[str]
      buyers_mentioned: list[str]
      suppliers_mentioned: list[str]
      programmes_mentioned: list[str]
      summary: str
      pursuit_implication: Optional[str]
      content_angle_hook: Optional[str]
      cost_usd: Optional[Decimal] = None
      latency_ms: Optional[int] = None
      prompt_version: Optional[str] = None

      @field_validator("relevance_score")
      @classmethod
      def score_in_range(cls, v: int) -> int:
          if not 0 <= v <= 10:
              raise ValueError(f"relevance_score must be 0-10, got {v}")
          return v

      @field_validator("signal_strength")
      @classmethod
      def valid_signal_strength(cls, v: str) -> str:
          allowed = {"high", "medium", "low"}
          if v not in allowed:
              raise ValueError(f"signal_strength must be one of {allowed}, got {v!r}")
          return v

      @field_validator("signal_type")
      @classmethod
      def valid_signal_type(cls, v: str) -> str:
          allowed = {"procurement", "policy", "oversight", "financial", "leadership", "other"}
          if v not in allowed:
              raise ValueError(f"signal_type must be one of {allowed}, got {v!r}")
          return v


  # ---------------------------------------------------------------------------
  # Custom exception
  # ---------------------------------------------------------------------------

  class ClassificationError(Exception):
      """Raised when classification fails after retries."""
      pass


  # ---------------------------------------------------------------------------
  # Real-time single classification
  # ---------------------------------------------------------------------------

  async def classify_item(
      item,  # bidequity.models.item.Item — typed loosely to avoid circular import
      client: AsyncAnthropic,
      prompt_version: str = "classifier-v1",
  ) -> ClassifierResult:
      """
      Classify a single item in real time.

      Uses prompt caching on the system prompt. Retries once on malformed JSON.

      Args:
          item: An Item ORM/dataclass with at least title, body_preview, source_id.
          client: An AsyncAnthropic client instance.
          prompt_version: The prompt version to use (matches a prompts/ directory).

      Returns:
          ClassifierResult with all fields populated, including cost_usd.

      Raises:
          ClassificationError: If the API returns malformed JSON on both attempts.
      """
      system_prompt = load_classifier_system_prompt(prompt_version)
      user_content = _build_user_message(item)

      for attempt in range(2):
          t0 = time.monotonic()
          try:
              message = await client.messages.create(
                  model=CLASSIFIER_MODEL,
                  max_tokens=600,
                  system=[
                      {
                          "type": "text",
                          "text": system_prompt,
                          "cache_control": {"type": "ephemeral"},
                      }
                  ],
                  messages=[{"role": "user", "content": user_content}],
              )
          except Exception as exc:
              if attempt == 0:
                  logger.warning("Classifier API error on attempt 1, retrying: %s", exc)
                  continue
              raise ClassificationError(f"Classifier API error: {exc}") from exc

          latency_ms = int((time.monotonic() - t0) * 1000)
          raw_text = message.content[0].text.strip()

          try:
              parsed = json.loads(raw_text)
          except json.JSONDecodeError:
              if attempt == 0:
                  logger.warning(
                      "Classifier returned malformed JSON on attempt 1 for item %s, retrying",
                      getattr(item, "id", "?"),
                  )
                  continue
              raise ClassificationError(
                  f"Classifier returned malformed JSON after retry for item "
                  f"{getattr(item, 'id', '?')}: {raw_text[:200]!r}"
              )

          cost = _compute_cost(message.usage)

          try:
              result = ClassifierResult(
                  **parsed,
                  cost_usd=cost,
                  latency_ms=latency_ms,
                  prompt_version=prompt_version,
              )
          except Exception as exc:
              if attempt == 0:
                  logger.warning(
                      "ClassifierResult validation failed on attempt 1: %s", exc
                  )
                  continue
              raise ClassificationError(
                  f"ClassifierResult validation failed after retry: {exc}"
              ) from exc

          logger.debug(
              "Classified item %s: score=%d cost=$%.5f latency=%dms",
              getattr(item, "id", "?"),
              result.relevance_score,
              float(cost),
              latency_ms,
          )
          return result

      # Should not be reached, but satisfy type checker
      raise ClassificationError("classify_item exhausted retries unexpectedly")


  # ---------------------------------------------------------------------------
  # Batch classification via Message Batches API
  # ---------------------------------------------------------------------------

  async def classify_batch(
      items: list,
      client: AsyncAnthropic,
      prompt_version: str = "classifier-v1",
  ) -> list[ClassifierResult]:
      """
      Submit a list of items to the Anthropic Message Batches API.

      Polls until the batch is complete, then returns results in the same order
      as the input list. Uses prompt caching on the system prompt.

      Cost is approximately 50% of real-time due to the batch discount.

      Args:
          items: List of Item objects. Maximum 500 per batch (Anthropic limit).
          client: An AsyncAnthropic client instance.
          prompt_version: The prompt version to use.

      Returns:
          List of ClassifierResult in the same order as items.
          Items that fail to classify get a fallback result with score 0.

      Raises:
          ClassificationError: If the batch submission itself fails.
      """
      import asyncio

      if not items:
          return []

      if len(items) > 500:
          raise ValueError("Batch size exceeds Anthropic limit of 500 items per batch")

      system_prompt = load_classifier_system_prompt(prompt_version)

      # Build requests list
      requests = []
      for item in items:
          requests.append(
              {
                  "custom_id": str(getattr(item, "id", id(item))),
                  "params": {
                      "model": CLASSIFIER_MODEL,
                      "max_tokens": 600,
                      "system": [
                          {
                              "type": "text",
                              "text": system_prompt,
                              "cache_control": {"type": "ephemeral"},
                          }
                      ],
                      "messages": [
                          {
                              "role": "user",
                              "content": _build_user_message(item),
                          }
                      ],
                  },
              }
          )

      logger.info("Submitting batch of %d items to Message Batches API", len(items))

      try:
          batch = await client.messages.batches.create(requests=requests)
      except Exception as exc:
          raise ClassificationError(f"Batch submission failed: {exc}") from exc

      batch_id = batch.id
      logger.info("Batch %s submitted, polling for completion", batch_id)

      # Poll until complete
      poll_interval = 30  # seconds
      max_polls = 120  # up to 60 minutes
      for poll_num in range(max_polls):
          await asyncio.sleep(poll_interval)
          status = await client.messages.batches.retrieve(batch_id)
          if status.processing_status == "ended":
              break
          logger.debug(
              "Batch %s poll %d: %s",
              batch_id,
              poll_num + 1,
              status.processing_status,
          )
      else:
          raise ClassificationError(
              f"Batch {batch_id} did not complete within {max_polls * poll_interval}s"
          )

      logger.info("Batch %s complete, retrieving results", batch_id)

      # Build a map from custom_id to result
      results_by_id: dict[str, ClassifierResult] = {}
      async for result in await client.messages.batches.results(batch_id):
          custom_id = result.custom_id
          if result.result.type == "succeeded":
              message = result.result.message
              raw_text = message.content[0].text.strip()
              cost = _compute_cost(message.usage)
              try:
                  parsed = json.loads(raw_text)
                  cr = ClassifierResult(
                      **parsed,
                      cost_usd=cost,
                      prompt_version=prompt_version,
                  )
                  results_by_id[custom_id] = cr
              except Exception as exc:
                  logger.warning(
                      "Failed to parse batch result for item %s: %s", custom_id, exc
                  )
                  results_by_id[custom_id] = _fallback_result(prompt_version)
          else:
              logger.warning(
                  "Batch item %s failed: %s", custom_id, result.result
              )
              results_by_id[custom_id] = _fallback_result(prompt_version)

      # Return in input order
      return [
          results_by_id.get(
              str(getattr(item, "id", id(item))),
              _fallback_result(prompt_version),
          )
          for item in items
      ]


  # ---------------------------------------------------------------------------
  # Helpers
  # ---------------------------------------------------------------------------

  def _build_user_message(item) -> str:
      """Build the user-turn content for a single item classification."""
      title = getattr(item, "title", "")
      preview = getattr(item, "body_preview", "") or getattr(item, "body_text", "")[:500]
      source = getattr(item, "source_name", "") or f"source_id={getattr(item, 'source_id', '?')}"
      url = getattr(item, "url", "")

      return (
          f"**Title:** {title}\n\n"
          f"**Source:** {source}\n\n"
          f"**URL:** {url}\n\n"
          f"**Content preview:**\n{preview}\n\n"
          f"Classify this item and return the JSON output."
      )


  def _compute_cost(usage) -> Decimal:
      """
      Compute cost from Anthropic usage object.
      Accounts for cache reads when the cache_read_input_tokens field is present.
      """
      input_tokens = getattr(usage, "input_tokens", 0) or 0
      output_tokens = getattr(usage, "output_tokens", 0) or 0
      cache_read_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0
      cache_creation_tokens = getattr(usage, "cache_creation_input_tokens", 0) or 0

      # Non-cached input tokens = total input - cache reads - cache writes
      standard_input = input_tokens - cache_read_tokens - cache_creation_tokens

      cost = (
          Decimal(max(standard_input, 0)) * HAIKU_INPUT_PRICE_PER_TOKEN
          + Decimal(cache_read_tokens) * HAIKU_CACHE_READ_PRICE_PER_TOKEN
          + Decimal(cache_creation_tokens) * HAIKU_INPUT_PRICE_PER_TOKEN  # write ≈ input price
          + Decimal(output_tokens) * HAIKU_OUTPUT_PRICE_PER_TOKEN
      )
      return cost


  def _fallback_result(prompt_version: str) -> ClassifierResult:
      """Return a zero-score fallback result for items that failed to classify."""
      return ClassifierResult(
          relevance_score=0,
          signal_strength="low",
          signal_type="other",
          sectors=[],
          buyers_mentioned=[],
          suppliers_mentioned=[],
          programmes_mentioned=[],
          summary="Classification failed — item scored 0 by default.",
          pursuit_implication=None,
          content_angle_hook=None,
          cost_usd=Decimal("0"),
          prompt_version=prompt_version,
      )
  ```

---

### Task 5 — Create the eval golden set and harness

- [ ] **5.1** Create `bidequity-newsroom/evals/classifier_golden.json`:

  ```json
  {
    "version": "1.0",
    "description": "Golden eval set for the BidEquity classifier. Expand to 50 items before first production promotion. Seed entries are constructed examples; replace with real BIP cases when available.",
    "items": [
      {
        "id": "golden-001",
        "title": "Find a Tender: ITT — Emergency Services Network Phase 2 Core Network Infrastructure",
        "body_preview": "The Home Office is seeking a prime contractor to design, build, and operate the Phase 2 core network infrastructure for the Emergency Services Network. The contract is valued at approximately £1.2 billion over 10 years. Responses are due by 17:00 on 30 June 2026.",
        "source_name": "Find a Tender Service",
        "source_category": "Procurement Notices",
        "expected_relevance_score": 10,
        "expected_signal_type": "procurement",
        "tolerance": 1,
        "notes": "Direct ITT — should reliably score 10. Constructed example."
      },
      {
        "id": "golden-002",
        "title": "NAO: Investigation into Common Platform delivery",
        "body_preview": "The NAO finds Common Platform is £312m over budget and three years late. Recommends options appraisal including replatforming before further funding is committed. SRO has changed three times since 2021.",
        "source_name": "National Audit Office",
        "source_category": "Oversight & Scrutiny",
        "expected_relevance_score": 9,
        "expected_signal_type": "oversight",
        "tolerance": 1,
        "notes": "Strong oversight signal on a named programme. Constructed example."
      },
      {
        "id": "golden-003",
        "title": "DSIT AI Playbook mandates AI procurement strategies across central government by Q3 2026",
        "body_preview": "DSIT publishes AI Playbook mandating AI procurement strategies for all central government departments by Q3 2026 with minimum assurance standards. Non-compliance risks AI Fund access.",
        "source_name": "DSIT",
        "source_category": "Official Guidance",
        "expected_relevance_score": 8,
        "expected_signal_type": "policy",
        "tolerance": 1,
        "notes": "Strong policy signal with direct procurement implication. Constructed example."
      },
      {
        "id": "golden-004",
        "title": "techUK: Procurement Act 2023 must fix SME access barriers",
        "body_preview": "techUK position paper calls on Cabinet Office to mandate disaggregated structures, 30-day payment terms for tier-2 suppliers, and 18-month forward pipelines. SME participation in central government has fallen from 28% to 19%.",
        "source_name": "techUK",
        "source_category": "Industry Body",
        "expected_relevance_score": 6,
        "expected_signal_type": "policy",
        "tolerance": 1,
        "notes": "Contextual policy signal. Constructed example."
      },
      {
        "id": "golden-005",
        "title": "Institute for Government: Making outsourcing work — lessons from a decade of public sector contracts",
        "body_preview": "IfG paper examines 47 outsourcing case studies and identifies five structural weaknesses: contract management, payment mechanisms, mobilisation, commercial intelligence, and supplier relationship management. Recommends Outsourcing Playbook reform.",
        "source_name": "Institute for Government",
        "source_category": "Think Tank Reports",
        "expected_relevance_score": 6,
        "expected_signal_type": "policy",
        "tolerance": 1,
        "notes": "Relevant background; no direct procurement trigger. Constructed example."
      },
      {
        "id": "golden-006",
        "title": "Leeds City Council launches Digital Inclusion Strategy 2026-2030",
        "body_preview": "Leeds City Council commits £18m to digital inclusion: broadband for 50,000 households, skills training for 15,000 residents, 200 digital access hubs by 2028. Delivery partner procurement commencing Q3 2026.",
        "source_name": "Leeds City Council",
        "source_category": "Council News",
        "expected_relevance_score": 5,
        "expected_signal_type": "procurement",
        "tolerance": 1,
        "notes": "Single council procurement — ambient signal. Constructed example."
      },
      {
        "id": "golden-007",
        "title": "LGA: Councils warn of growing pressure on children's services budgets",
        "body_preview": "LGA warns of £2.1bn children's services overspend projected across English councils for 2025-26. Several councils considering Section 114 notices if emergency funding not forthcoming.",
        "source_name": "Local Government Chronicle",
        "source_category": "Trade Press",
        "expected_relevance_score": 4,
        "expected_signal_type": "financial",
        "tolerance": 1,
        "notes": "Financial stress signal with no procurement trigger. Constructed example."
      },
      {
        "id": "golden-008",
        "title": "Ofgem publishes new price cap methodology for 2026",
        "body_preview": "Ofgem publishes revised domestic energy price cap methodology with quarterly reset and revised wholesale cost passthrough formula following consultation with 23 energy suppliers.",
        "source_name": "Ofgem",
        "source_category": "Regulatory Announcements",
        "expected_relevance_score": 2,
        "expected_signal_type": "policy",
        "tolerance": 1,
        "notes": "Wrong sector — should score very low. Constructed example."
      },
      {
        "id": "golden-009",
        "title": "MoJ spending review settlement: Justice digital transformation receives £450m over three years",
        "body_preview": "The Ministry of Justice has confirmed a £450m spending review settlement for digital transformation over the next three years, including HMCTS Reform continuation, prison digital, and probation case management modernisation.",
        "source_name": "Ministry of Justice",
        "source_category": "Official Announcements",
        "expected_relevance_score": 9,
        "expected_signal_type": "financial",
        "tolerance": 1,
        "notes": "Spending review settlement for named buyer with active programmes. Constructed example."
      },
      {
        "id": "golden-010",
        "title": "Serco announces strategic review of UK public services division",
        "body_preview": "Serco has announced a strategic review of its UK public services division following a profit warning. The review may result in disposals or restructuring of contracts in justice, health, and central government. Full results expected Q2 2026.",
        "source_name": "Financial Times",
        "source_category": "Trade Press",
        "expected_relevance_score": 8,
        "expected_signal_type": "financial",
        "tolerance": 1,
        "notes": "Major prime strategic review signals contract availability. Constructed example."
      }
    ]
  }
  ```

- [ ] **5.2** Create `bidequity-newsroom/evals/classifier_eval.py`:

  ```python
  #!/usr/bin/env python3
  """
  BidEquity classifier eval harness.

  Runs the golden eval set through the classifier and reports agreement rate.
  Agreement = |predicted_score - expected_score| <= tolerance (default 1).

  Usage:
      ANTHROPIC_API_KEY=sk-ant-... python evals/classifier_eval.py
      ANTHROPIC_API_KEY=sk-ant-... python evals/classifier_eval.py --version classifier-v2
      ANTHROPIC_API_KEY=sk-ant-... python evals/classifier_eval.py --golden path/to/custom.json

  Results are written to evals/results/classifier_eval_{timestamp}.json.
  """
  from __future__ import annotations

  import argparse
  import asyncio
  import json
  import os
  import sys
  from datetime import datetime, timezone
  from pathlib import Path
  from typing import Any


  # ---------------------------------------------------------------------------
  # Minimal Item-like object for the eval (no DB dependency)
  # ---------------------------------------------------------------------------

  class EvalItem:
      """Lightweight item struct for eval purposes — no ORM required."""

      def __init__(
          self,
          id: str,
          title: str,
          body_preview: str,
          source_name: str,
          source_category: str,
      ):
          self.id = id
          self.title = title
          self.body_preview = body_preview
          self.source_name = source_name
          self.source_category = source_category
          self.url = ""
          self.source_id = 0


  # ---------------------------------------------------------------------------
  # Main eval runner
  # ---------------------------------------------------------------------------

  async def run_eval(
      golden_path: Path,
      prompt_version: str,
      results_dir: Path,
  ) -> dict[str, Any]:
      """Run the classifier against the golden set and return a results dict."""
      from anthropic import AsyncAnthropic
      from bidequity.intelligence.classifier import classify_item, ClassificationError

      api_key = os.environ.get("ANTHROPIC_API_KEY")
      if not api_key:
          print("ERROR: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
          sys.exit(1)

      # Load golden set
      golden_data = json.loads(golden_path.read_text(encoding="utf-8"))
      golden_items = golden_data["items"]

      print(f"Loaded {len(golden_items)} items from {golden_path}")
      print(f"Prompt version: {prompt_version}")
      print(f"Running classifications...\n")

      client = AsyncAnthropic(api_key=api_key)
      item_results = []
      agreed = 0
      total_cost_usd = 0.0

      for golden in golden_items:
          item = EvalItem(
              id=golden["id"],
              title=golden["title"],
              body_preview=golden["body_preview"],
              source_name=golden["source_name"],
              source_category=golden["source_category"],
          )

          expected_score = golden["expected_relevance_score"]
          tolerance = golden.get("tolerance", 1)

          try:
              result = await classify_item(item, client, prompt_version=prompt_version)
              predicted_score = result.relevance_score
              cost = float(result.cost_usd or 0)
              error = None
          except ClassificationError as exc:
              predicted_score = -1
              cost = 0.0
              error = str(exc)

          diff = abs(predicted_score - expected_score) if predicted_score >= 0 else 999
          is_agreed = diff <= tolerance
          if is_agreed:
              agreed += 1
          total_cost_usd += cost

          item_result = {
              "id": golden["id"],
              "title": golden["title"],
              "expected_score": expected_score,
              "predicted_score": predicted_score,
              "diff": diff,
              "agreed": is_agreed,
              "cost_usd": round(cost, 6),
              "error": error,
              "notes": golden.get("notes", ""),
          }
          item_results.append(item_result)

          status = "OK" if is_agreed else "MISS"
          print(
              f"[{status}] {golden['id']}: expected={expected_score} "
              f"predicted={predicted_score} diff={diff}"
          )

      agreement_rate = agreed / len(golden_items) if golden_items else 0.0

      print(f"\n{'='*60}")
      print(f"Agreement rate: {agreed}/{len(golden_items)} = {agreement_rate:.1%}")
      print(f"Total cost: ${total_cost_usd:.4f} USD")
      print(f"Target: >= 70% (production promotion threshold: >= 80%)")
      if agreement_rate >= 0.80:
          print("PASS: Ready for production promotion.")
      elif agreement_rate >= 0.70:
          print("CONDITIONAL PASS: Meets minimum threshold but below production bar.")
      else:
          print("FAIL: Below minimum threshold. Review rubric and examples.")
      print(f"{'='*60}\n")

      results = {
          "timestamp": datetime.now(timezone.utc).isoformat(),
          "prompt_version": prompt_version,
          "golden_set_version": golden_data.get("version", "unknown"),
          "total_items": len(golden_items),
          "agreed": agreed,
          "agreement_rate": round(agreement_rate, 4),
          "total_cost_usd": round(total_cost_usd, 6),
          "pass": agreement_rate >= 0.70,
          "production_ready": agreement_rate >= 0.80,
          "items": item_results,
      }

      # Write results
      results_dir.mkdir(parents=True, exist_ok=True)
      timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
      results_path = results_dir / f"classifier_eval_{timestamp_str}.json"
      results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
      print(f"Results written to: {results_path}")

      return results


  # ---------------------------------------------------------------------------
  # Entry point
  # ---------------------------------------------------------------------------

  def main():
      parser = argparse.ArgumentParser(description="BidEquity classifier eval harness")
      parser.add_argument(
          "--version",
          default="classifier-v1",
          help="Prompt version to evaluate (default: classifier-v1)",
      )
      parser.add_argument(
          "--golden",
          default=None,
          help="Path to golden set JSON (default: evals/classifier_golden.json)",
      )
      args = parser.parse_args()

      # Resolve paths
      script_dir = Path(__file__).parent
      golden_path = Path(args.golden) if args.golden else script_dir / "classifier_golden.json"
      results_dir = script_dir / "results"

      if not golden_path.exists():
          print(f"ERROR: Golden set not found: {golden_path}", file=sys.stderr)
          sys.exit(1)

      results = asyncio.run(
          run_eval(
              golden_path=golden_path,
              prompt_version=args.version,
              results_dir=results_dir,
          )
      )

      # Exit with non-zero if below minimum threshold
      sys.exit(0 if results["pass"] else 1)


  if __name__ == "__main__":
      main()
  ```

---

### Task 6 — Create the `evals/results/` directory

- [ ] **6.1** Create `bidequity-newsroom/evals/results/.gitkeep` (empty file to track the directory in git; add `evals/results/*.json` to `.gitignore`).

---

### Task 7 — Wire up imports and verify structure

- [ ] **7.1** Ensure `bidequity-newsroom/src/bidequity/__init__.py` and `bidequity-newsroom/src/bidequity/intelligence/__init__.py` exist (empty files).

- [ ] **7.2** Ensure `bidequity-newsroom/tests/__init__.py` and `bidequity-newsroom/tests/test_intelligence/__init__.py` exist (empty files).

- [ ] **7.3** Verify `pyproject.toml` includes `anthropic`, `pydantic`, `pytest`, and `pytest-asyncio` as dependencies. Add if missing:

  ```toml
  [project.optional-dependencies]
  dev = ["pytest", "pytest-asyncio"]

  [tool.pytest.ini_options]
  asyncio_mode = "auto"
  ```

- [ ] **7.4** Run tests to confirm they pass (with mocks — no API key required):
  ```bash
  cd bidequity-newsroom
  uv run pytest tests/test_intelligence/test_classifier.py -v
  ```
  All four tests should pass.

---

### Task 8 — Commit

- [ ] **8.1** Stage all new files:
  ```bash
  git add bidequity-newsroom/prompts/classifier/
  git add bidequity-newsroom/src/bidequity/intelligence/prompt_loader.py
  git add bidequity-newsroom/src/bidequity/intelligence/classifier.py
  git add bidequity-newsroom/evals/classifier_golden.json
  git add bidequity-newsroom/evals/classifier_eval.py
  git add bidequity-newsroom/evals/results/.gitkeep
  git add bidequity-newsroom/tests/test_intelligence/
  ```

- [ ] **8.2** Commit:
  ```
  feat(newsroom): classifier stage — prompt files, worker, eval harness, tests (Ticket 5)
  ```

---

### Task 9 — Manual eval run (requires API key)

- [ ] **9.1** Once an API key is available, run the eval harness against the 10-item seed golden set:
  ```bash
  cd bidequity-newsroom
  ANTHROPIC_API_KEY=sk-ant-... uv run python evals/classifier_eval.py --version classifier-v1
  ```
  Record the agreement rate. If below 70%: tune the rubric bands and/or add more few-shot examples, then re-run. Do not promote to production until >= 70% on the seed set (target >= 80% once expanded to 50 items).

- [ ] **9.2** Expand the golden set to 50 items by adding real BIP cases. Replace `"isConstructed": true` seed items with real items when available.

---

## Cost Notes

| Line | Detail |
|---|---|
| Input per item | ~1,200 tokens (title + first 300 words + metadata) |
| Output per item | ~350 tokens (structured JSON) |
| System prompt | ~2,000 tokens, cached at ~90% hit rate |
| Batch discount | 50% off real-time price |
| Haiku pricing | $0.80/M input, $4.00/M output, $0.08/M cached reads |
| Estimated monthly cost before optimisation | ~£32 at 3,600 items/month |
| After caching + batching | ~£8–10/month |
| Cost logging | Every `ClassifierResult` carries `cost_usd` (Decimal, 6dp) for persistence to `classifications.cost_usd` |

---

## Acceptance Criteria

From spec section 12.6:

- [ ] Classifier-v1 achieves **≥ 70% agreement** on the golden set (10-item seed; target 80% on full 50-item set before production promotion)
- [ ] **Cost per classification is logged** in `ClassifierResult.cost_usd` (Decimal, 6dp)
- [ ] **Prompt versioning works**: changing `prompt_version` parameter routes to a different prompts directory; listing versions via `list_prompt_versions()` reflects the filesystem state
- [ ] **Malformed response handling**: retry once, raise `ClassificationError` on second failure
- [ ] **All four unit tests pass** with no API key required (mocked client)
